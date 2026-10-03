//! Rust-owned FastAPI application registration and ASGI request flow.

use std::cell::RefCell;
use std::collections::{BTreeMap, BTreeSet, HashMap, VecDeque};
use std::path::Path;
use std::rc::Rc;
use std::sync::Mutex;
use std::sync::atomic::{AtomicU64, Ordering};

use pyo3::exceptions::{
    PyAssertionError, PyAttributeError, PyException, PyKeyError, PyNameError,
    PyNotImplementedError, PyRuntimeError, PyStopAsyncIteration, PyTypeError, PyValueError,
};
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{
    PyBool, PyBytes, PyDict, PyInt, PyIterator, PyList, PyModule, PySet, PyString, PyTuple, PyType,
};
use starlette_rs::{DetailedRouteMatch, NamedRouteError, NamedRouteTable, QueryParams, RouteTable};

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};
use crate::docs;
use crate::encoding::jsonable_encoder_default;
use crate::errors::fastapi_error;
use crate::lifespan::{FastApiLifespan, warn_on_event};
use crate::openapi::{
    OpenApiAdditionalResponse, OpenApiInfo, OpenApiOperation, OpenApiParameter, openapi_document,
};
use crate::sse;
use crate::{
    FastApiInputLocation, FastApiInputParameter, FastApiOperationMatch, FastApiOperationRouter,
};

const DEFAULT_RESPONSE_DESCRIPTION: &str = "Successful Response";

#[pyclass(name = "_PydanticBytesSchemaDescriptor")]
struct PydanticBytesSchemaDescriptor;

#[pyclass(name = "_PydanticBytesSchema")]
struct PydanticBytesSchema {
    generator: Py<PyAny>,
}

#[pymethods]
impl PydanticBytesSchemaDescriptor {
    #[new]
    fn new() -> Self {
        Self
    }

    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Option<Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(py, Self).map(Py::into_any);
        };
        Py::new(
            py,
            PydanticBytesSchema {
                generator: instance.unbind(),
            },
        )
        .map(Py::into_any)
    }
}

#[pymethods]
impl PydanticBytesSchema {
    fn __call__(&self, py: Python<'_>, core_schema: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        let generator = self.generator.bind(py);
        let schema = PyDict::new(py);
        schema.set_item("type", "string")?;
        schema.set_item("contentMediaType", "application/octet-stream")?;
        let mode = generator.getattr("mode")?.extract::<String>()?;
        let config = generator.getattr("_config")?;
        let bytes_mode = config
            .getattr(if mode == "serialization" {
                "ser_json_bytes"
            } else {
                "val_json_bytes"
            })?
            .extract::<String>()?;
        if bytes_mode == "base64" {
            schema.set_item("contentEncoding", "base64")?;
        }
        let validations = generator.getattr("ValidationsMapping")?.getattr("bytes")?;
        generator.call_method1(
            "update_with_validations",
            (schema.clone(), core_schema, validations),
        )?;
        Ok(schema.into_any().unbind())
    }
}

fn register_pydantic_schema_generator(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    module.add_class::<PydanticBytesSchemaDescriptor>()?;
    module.add_class::<PydanticBytesSchema>()?;
    let descriptor = module.getattr("_PydanticBytesSchemaDescriptor")?.call0()?;
    let attributes = PyDict::new(py);
    attributes.set_item("bytes_schema", descriptor)?;
    attributes.set_item("__module__", "fastapi_rs._core")?;
    let base = py
        .import("pydantic.json_schema")?
        .getattr("GenerateJsonSchema")?;
    let bases = PyTuple::new(py, [base])?;
    let generator = py.import("builtins")?.getattr("type")?.call1((
        "FastApiGenerateJsonSchema",
        bases,
        attributes,
    ))?;
    module.add("_FastApiGenerateJsonSchema", generator)
}

#[pyfunction(name = "_frontend_dependency_endpoint")]
fn frontend_dependency_endpoint() {}

fn omitted_response_model() -> Py<PyAny> {
    Python::attach(|py| py.NotImplemented())
}

fn middleware_cached_request_type(py: Python<'_>) -> PyResult<Py<PyAny>> {
    static CACHED_REQUEST_TYPE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
    CACHED_REQUEST_TYPE
        .get_or_try_init(py, || {
            let request_type = py.import("starlette.requests")?.getattr("Request")?;
            let descriptor = Py::new(py, PyFastApiCachedReceiveDescriptor)?.into_any();
            let namespace = PyDict::new(py);
            namespace.set_item("__module__", "starlette.middleware.base")?;
            namespace.set_item("wrapped_receive", descriptor)?;
            let bases = PyTuple::new(py, [request_type])?;
            py.import("builtins")?
                .getattr("type")?
                .call1(("_CachedRequest", bases, namespace))
                .map(Bound::unbind)
        })
        .map(|request_type| request_type.clone_ref(py))
}

fn default_frontend_auto() -> Py<PyAny> {
    Python::attach(|py| PyString::new(py, "auto").unbind().into_any())
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum InputSource {
    Path,
    Query,
    Header,
    Cookie,
    Body,
    Form,
    File,
}

impl InputSource {
    const fn location(self) -> FastApiInputLocation {
        match self {
            Self::Path => FastApiInputLocation::Path,
            Self::Query => FastApiInputLocation::Query,
            Self::Header => FastApiInputLocation::Header,
            Self::Cookie => FastApiInputLocation::Cookie,
            Self::Body => FastApiInputLocation::Body,
            Self::Form | Self::File => FastApiInputLocation::Body,
        }
    }

    const fn as_str(self) -> &'static str {
        match self {
            Self::Path => "path",
            Self::Query => "query",
            Self::Header => "header",
            Self::Cookie => "cookie",
            Self::Body | Self::Form | Self::File => "body",
        }
    }
}

enum ParameterSource {
    Input {
        source: InputSource,
        alias: String,
    },
    WebSocket,
    Request,
    HttpConnection,
    Response,
    BackgroundTasks,
    Dependency {
        plan: Box<CallablePlan>,
        use_cache: bool,
        scope: Option<String>,
        security_scopes: Vec<String>,
        bind_value: bool,
    },
}

type DependencyCacheKey = (usize, Option<String>);
type OpenApiSecurityVisitKey = (usize, Option<String>, Vec<String>);

struct CallableParameter {
    name: String,
    annotation: Py<PyAny>,
    default: Option<Py<PyAny>>,
    is_sequence: bool,
    parameter_model_fields: Option<Vec<ParameterModelField>>,
    parameter_model_config: Option<Py<PyAny>>,
    model_convert_underscores: Option<bool>,
    media_type: Option<String>,
    title: Option<String>,
    description: Option<String>,
    deprecated: bool,
    include_in_schema: bool,
    body_embed: bool,
    source: ParameterSource,
}

struct ParameterModelField {
    name: String,
    alias: String,
    field_info: Py<PyAny>,
    is_sequence: bool,
    is_json: bool,
    convert_underscores: Option<bool>,
}

struct CallablePlan {
    callable: Py<PyAny>,
    parameters: Vec<CallableParameter>,
    path_parameters: Vec<String>,
    return_annotation: Option<Py<PyAny>>,
    computed_scope: Option<String>,
}

impl ParameterSource {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        match self {
            Self::Input { source, alias } => Self::Input {
                source: *source,
                alias: alias.clone(),
            },
            Self::WebSocket => Self::WebSocket,
            Self::Request => Self::Request,
            Self::HttpConnection => Self::HttpConnection,
            Self::Response => Self::Response,
            Self::BackgroundTasks => Self::BackgroundTasks,
            Self::Dependency {
                plan,
                use_cache,
                scope,
                security_scopes,
                bind_value,
            } => Self::Dependency {
                plan: Box::new(plan.clone_ref(py)),
                use_cache: *use_cache,
                scope: scope.clone(),
                security_scopes: security_scopes.clone(),
                bind_value: *bind_value,
            },
        }
    }
}

impl CallableParameter {
    fn body_alias(&self) -> &str {
        match &self.source {
            ParameterSource::Input { alias, .. } => alias,
            _ => &self.name,
        }
    }

    fn clone_ref(&self, py: Python<'_>) -> Self {
        Self {
            name: self.name.clone(),
            annotation: self.annotation.clone_ref(py),
            default: self.default.as_ref().map(|value| value.clone_ref(py)),
            is_sequence: self.is_sequence,
            parameter_model_fields: self.parameter_model_fields.as_ref().map(|fields| {
                fields
                    .iter()
                    .map(|field| ParameterModelField {
                        name: field.name.clone(),
                        alias: field.alias.clone(),
                        field_info: field.field_info.clone_ref(py),
                        is_sequence: field.is_sequence,
                        is_json: field.is_json,
                        convert_underscores: field.convert_underscores,
                    })
                    .collect()
            }),
            parameter_model_config: self
                .parameter_model_config
                .as_ref()
                .map(|value| value.clone_ref(py)),
            model_convert_underscores: self.model_convert_underscores,
            media_type: self.media_type.clone(),
            title: self.title.clone(),
            description: self.description.clone(),
            deprecated: self.deprecated,
            include_in_schema: self.include_in_schema,
            body_embed: self.body_embed,
            source: self.source.clone_ref(py),
        }
    }
}

impl CallablePlan {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        Self {
            callable: self.callable.clone_ref(py),
            parameters: self
                .parameters
                .iter()
                .map(|parameter| parameter.clone_ref(py))
                .collect(),
            path_parameters: self.path_parameters.clone(),
            return_annotation: self
                .return_annotation
                .as_ref()
                .map(|annotation| annotation.clone_ref(py)),
            computed_scope: self.computed_scope.clone(),
        }
    }
}

impl DependencyExecutionNode {
    fn build(
        original_plan: &CallablePlan,
        use_cache: bool,
        scope: Option<String>,
        binding_index: usize,
        context: &InvocationContext<'_, '_>,
    ) -> PyResult<Self> {
        let original_callable = original_plan.callable.bind(context.py);
        let replacement = context.dependency_overrides.get_item(original_callable)?;
        let plan = match replacement {
            Some(replacement) if !replacement.is(original_callable) => CallablePlan::build(
                context.py,
                replacement.unbind(),
                &original_plan.path_parameters,
                scope,
            )?,
            _ => original_plan.clone_ref(context.py),
        };
        let callable_kind =
            dependency_override_callable(context.py, plan.callable.bind(context.py))?;
        if callable_kind == DependencyOverrideCallable::AsyncCallableInstance {
            return Err(PyNotImplementedError::new_err(
                "async dependency graphs do not support callable-instance dependencies",
            ));
        }
        let generator_kind =
            dependency_callable_generator_kind(context.py, plan.callable.bind(context.py))?;
        let cache_key = (
            original_plan.callable.as_ptr() as usize,
            original_plan.computed_scope.clone(),
        );
        let mut children = Vec::new();
        let mut dependency_edge_index = 0;
        for parameter in &plan.parameters {
            let ParameterSource::Dependency {
                plan: child_plan,
                use_cache: child_use_cache,
                scope: child_scope,
                ..
            } = &parameter.source
            else {
                continue;
            };
            children.push(Self::build(
                child_plan,
                *child_use_cache,
                child_scope.clone(),
                dependency_edge_index,
                context,
            )?);
            dependency_edge_index += 1;
        }
        Ok(Self {
            plan,
            cache_key,
            use_cache,
            binding_index,
            callable_kind,
            generator_kind,
            children,
            result: None,
            awaiting: false,
            failed: false,
        })
    }

    fn has_nested_generator(&self) -> bool {
        self.children
            .iter()
            .any(|child| child.generator_kind.is_some() || child.has_nested_generator())
    }

    fn advance(
        &mut self,
        context: &mut InvocationContext<'_, '_>,
        path: &mut Vec<usize>,
    ) -> PyResult<DependencyGraphStep> {
        if self.failed {
            return Ok(DependencyGraphStep::Invalid);
        }
        if let Some(result) = self.result.as_ref() {
            return Ok(DependencyGraphStep::Ready(result.clone_ref(context.py)));
        }
        if self.use_cache {
            if let Some(result) = context.dependency_cache.get(&self.cache_key) {
                self.result = Some(result.clone_ref(context.py));
                return Ok(DependencyGraphStep::Ready(result.clone_ref(context.py)));
            }
        }

        let mut child_failed = false;
        for (index, child) in self.children.iter_mut().enumerate() {
            path.push(index);
            let step = child.advance(context, path);
            path.pop();
            match step? {
                DependencyGraphStep::Ready(_) => {}
                DependencyGraphStep::Invalid => child_failed = true,
                DependencyGraphStep::Await { awaitable, path } => {
                    return Ok(DependencyGraphStep::Await { awaitable, path });
                }
            }
        }
        if child_failed {
            self.failed = true;
            return Ok(DependencyGraphStep::Invalid);
        }

        let mut prepared_dependencies = HashMap::with_capacity(self.children.len());
        for child in &self.children {
            let value = child.result.as_ref().ok_or_else(|| {
                PyRuntimeError::new_err("resolved dependency graph omitted a child value")
            })?;
            prepared_dependencies.insert(child.binding_index, value.clone_ref(context.py));
        }
        let invoke_plan = if let Some(generator_kind) = self.generator_kind {
            let decorator = context
                .py
                .import("contextlib")?
                .getattr(match generator_kind {
                    DependencyGeneratorKind::Sync => "contextmanager",
                    DependencyGeneratorKind::Async => "asynccontextmanager",
                })?;
            let mut plan = self.plan.clone_ref(context.py);
            plan.callable = decorator
                .call1((self.plan.callable.bind(context.py),))?
                .unbind();
            plan
        } else {
            self.plan.clone_ref(context.py)
        };
        let use_threadpool =
            self.generator_kind.is_none() && self.callable_kind == DependencyOverrideCallable::Sync;
        let Some(value) = invoke_plan.invoke_with_threadpool(
            context,
            None,
            None,
            use_threadpool,
            Some(&prepared_dependencies),
        )?
        else {
            self.failed = true;
            return Ok(DependencyGraphStep::Invalid);
        };

        let awaitable = if let Some(generator_kind) = self.generator_kind {
            let context_manager = match generator_kind {
                DependencyGeneratorKind::Async => value,
                DependencyGeneratorKind::Sync => Py::new(
                    context.py,
                    ThreadpoolDependencyContextManager {
                        context_manager: value,
                    },
                )?
                .into_any(),
            };
            let exit_stack = if self.plan.computed_scope.as_deref() == Some("function") {
                context.function_dependency_exit_stack
            } else {
                context.dependency_exit_stack
            };
            Some(
                exit_stack
                    .call_method1("enter_async_context", (context_manager.bind(context.py),))?
                    .unbind(),
            )
        } else if is_awaitable(context.py, value.bind(context.py))? {
            Some(value)
        } else {
            self.store_result(context, value.clone_ref(context.py));
            return Ok(DependencyGraphStep::Ready(value));
        };

        let awaitable = awaitable.ok_or_else(|| {
            PyRuntimeError::new_err("dependency graph entered a context without an awaitable")
        })?;
        self.awaiting = true;
        Ok(DependencyGraphStep::Await {
            awaitable,
            path: path.clone(),
        })
    }

    fn store_result(&mut self, context: &mut InvocationContext<'_, '_>, value: Py<PyAny>) {
        let py = context.py;
        context
            .dependency_cache
            .entry(self.cache_key.clone())
            .or_insert_with(|| value.clone_ref(py));
        self.result = Some(value);
    }

    fn store_result_at_path(
        &mut self,
        path: &[usize],
        context: &mut InvocationContext<'_, '_>,
        value: Py<PyAny>,
    ) -> PyResult<()> {
        let Some((index, remaining)) = path.split_first() else {
            if !self.awaiting {
                return Err(PyRuntimeError::new_err(
                    "dependency graph resumed without a pending node",
                ));
            }
            self.awaiting = false;
            self.store_result(context, value);
            return Ok(());
        };
        let child = self.children.get_mut(*index).ok_or_else(|| {
            PyRuntimeError::new_err("dependency graph resume path does not identify a child")
        })?;
        child.store_result_at_path(remaining, context, value)
    }
}

impl DependencyExecutionGraph {
    fn build(plan: &CallablePlan, context: &InvocationContext<'_, '_>) -> PyResult<Self> {
        let mut roots = Vec::new();
        let mut dependency_edge_index = 0;
        for parameter in &plan.parameters {
            let ParameterSource::Dependency {
                plan: dependency_plan,
                use_cache,
                scope,
                ..
            } = &parameter.source
            else {
                continue;
            };
            roots.push(DependencyExecutionNode::build(
                dependency_plan,
                *use_cache,
                scope.clone(),
                dependency_edge_index,
                context,
            )?);
            dependency_edge_index += 1;
        }
        Ok(Self {
            roots,
            next_root: 0,
            in_progress_root: None,
            pending_path: None,
        })
    }

    fn has_nested_generator(&self) -> bool {
        self.roots
            .iter()
            .any(DependencyExecutionNode::has_nested_generator)
    }

    fn advance(
        &mut self,
        context: &mut InvocationContext<'_, '_>,
    ) -> PyResult<DependencyGraphAdvance> {
        while self.next_root < self.roots.len() {
            let root_index = self.next_root;
            let edge_index = self.roots[root_index].binding_index;
            if edge_index < *context.dependency_override_cursor
                && self.in_progress_root != Some(root_index)
            {
                self.next_root += 1;
                continue;
            }
            self.in_progress_root = Some(root_index);
            *context.dependency_override_cursor = edge_index + 1;
            let step = self.roots[root_index].advance(context, &mut vec![root_index]);
            match step? {
                DependencyGraphStep::Ready(value) => {
                    context.prepared_dependency_values.insert(edge_index, value);
                    self.next_root += 1;
                    self.in_progress_root = None;
                }
                DependencyGraphStep::Invalid => {
                    self.next_root += 1;
                    self.in_progress_root = None;
                }
                DependencyGraphStep::Await { awaitable, path } => {
                    self.pending_path = Some(path);
                    return Ok(DependencyGraphAdvance::Await(awaitable));
                }
            }
        }
        if context.failures.is_empty() {
            Ok(DependencyGraphAdvance::Ready)
        } else {
            Ok(DependencyGraphAdvance::Invalid)
        }
    }

    fn resume(
        &mut self,
        context: &mut InvocationContext<'_, '_>,
        value: Py<PyAny>,
    ) -> PyResult<DependencyGraphAdvance> {
        let path = self.pending_path.take().ok_or_else(|| {
            PyRuntimeError::new_err("dependency graph resumed without a pending awaitable")
        })?;
        let Some((root_index, remaining)) = path.split_first() else {
            return Err(PyRuntimeError::new_err(
                "dependency graph resume path omitted its root",
            ));
        };
        let root = self.roots.get_mut(*root_index).ok_or_else(|| {
            PyRuntimeError::new_err("dependency graph resume path does not identify a root")
        })?;
        root.store_result_at_path(remaining, context, value)?;
        self.advance(context)
    }
}

struct InvocationContext<'context, 'py> {
    py: Python<'py>,
    inputs: &'context Bound<'py, PyDict>,
    request: Option<&'context Bound<'py, PyAny>>,
    websocket: Option<&'context Bound<'py, PyAny>>,
    response: Option<&'context Bound<'py, PyAny>>,
    query_params: &'context QueryParams,
    body_fields_embedded: bool,
    form_body_embedded: bool,
    failures: &'context mut Vec<ValidationIssue>,
    dependency_overrides: &'context Bound<'py, PyDict>,
    dependency_cache: &'context mut HashMap<DependencyCacheKey, Py<PyAny>>,
    prepared_dependency_values: &'context mut HashMap<usize, Py<PyAny>>,
    dependency_override_cursor: &'context mut usize,
    dependency_exit_stack: &'context Bound<'py, PyAny>,
    function_dependency_exit_stack: &'context Bound<'py, PyAny>,
    background_tasks: &'context mut Option<Py<PyAny>>,
}

struct RequestInvocation {
    inputs: Py<PyDict>,
    query_params: QueryParams,
    request_body: Option<Py<PyAny>>,
    form_body_embedded: bool,
    failures: Vec<ValidationIssue>,
    dependency_cache: HashMap<DependencyCacheKey, Py<PyAny>>,
    prepared_dependency_values: HashMap<usize, Py<PyAny>>,
    dependency_override_cursor: usize,
    dependency_exit_stack: Py<PyAny>,
    dependency_exit_stack_closed: bool,
    function_dependency_exit_stack: Py<PyAny>,
    function_dependency_exit_stack_closed: bool,
    background_tasks: Option<Py<PyAny>>,
}

struct FormFileReadPlan {
    name: String,
    annotation: Py<PyAny>,
    sequence: bool,
    awaitables: VecDeque<Py<PyAny>>,
    values: Vec<Py<PyAny>>,
}

enum RouteInvocation {
    Ready(Option<Py<PyAny>>),
    AwaitDependencyGraph {
        awaitable: Py<PyAny>,
        graph: Box<DependencyExecutionGraph>,
    },
    AwaitDependency {
        awaitable: Py<PyAny>,
        cache_key: DependencyCacheKey,
        edge_index: usize,
    },
    AwaitOverrideSubdependency {
        awaitable: Py<PyAny>,
        parent_plan: Box<CallablePlan>,
        cache_key: DependencyCacheKey,
        edge_index: usize,
    },
}

enum OverridePreparation {
    Ready,
    Invalid,
    AwaitDependencyGraph {
        awaitable: Py<PyAny>,
        graph: Box<DependencyExecutionGraph>,
    },
    Await {
        awaitable: Py<PyAny>,
        cache_key: DependencyCacheKey,
        edge_index: usize,
    },
    AwaitSubdependency {
        awaitable: Py<PyAny>,
        parent_plan: Box<CallablePlan>,
        cache_key: DependencyCacheKey,
        edge_index: usize,
    },
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum DependencyOverrideCallable {
    Sync,
    CoroutineFunction,
    AsyncCallableInstance,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum DependencyGeneratorKind {
    Sync,
    Async,
}

struct DependencyExecutionNode {
    plan: CallablePlan,
    cache_key: DependencyCacheKey,
    use_cache: bool,
    binding_index: usize,
    callable_kind: DependencyOverrideCallable,
    generator_kind: Option<DependencyGeneratorKind>,
    children: Vec<Self>,
    result: Option<Py<PyAny>>,
    awaiting: bool,
    failed: bool,
}

struct DependencyExecutionGraph {
    roots: Vec<DependencyExecutionNode>,
    next_root: usize,
    in_progress_root: Option<usize>,
    pending_path: Option<Vec<usize>>,
}

enum DependencyGraphStep {
    Ready(Py<PyAny>),
    Invalid,
    Await {
        awaitable: Py<PyAny>,
        path: Vec<usize>,
    },
}

enum DependencyGraphAdvance {
    Ready,
    Invalid,
    Await(Py<PyAny>),
}

#[pyclass]
struct ThreadpoolDependencyContextManager {
    context_manager: Py<PyAny>,
}

#[pymethods]
impl ThreadpoolDependencyContextManager {
    fn __aenter__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let enter = self.context_manager.bind(py).getattr("__enter__")?;
        py.import("starlette.concurrency")?
            .getattr("run_in_threadpool")?
            .call1((enter,))
            .map(Bound::unbind)
    }

    fn __aexit__(
        &self,
        py: Python<'_>,
        exception_type: &Bound<'_, PyAny>,
        exception: &Bound<'_, PyAny>,
        traceback: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let exit = self.context_manager.bind(py).getattr("__exit__")?;
        py.import("starlette.concurrency")?
            .getattr("run_in_threadpool")?
            .call1((exit, exception_type, exception, traceback))
            .map(Bound::unbind)
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum FastApiGeneratorKind {
    None,
    Sync,
    Async,
}

impl FastApiGeneratorKind {
    const fn is_generator(self) -> bool {
        !matches!(self, Self::None)
    }
}

struct FastApiRoute {
    path: String,
    path_format: String,
    method: String,
    name: String,
    route_scope: Py<PyAny>,
    param_convertors: Py<PyDict>,
    summary: Option<String>,
    response_description: String,
    additional_responses: Vec<OpenApiAdditionalResponse>,
    operation_id: Option<String>,
    deprecated: Option<bool>,
    tags: Option<Vec<String>>,
    status_code: Option<u16>,
    include_in_schema: bool,
    response_class: Option<Py<PyAny>>,
    strict_content_type: Option<bool>,
    sse_stream: bool,
    generator_kind: FastApiGeneratorKind,
    stream_item_type: Option<Py<PyAny>>,
    endpoint: Py<PyAny>,
    original_route: Py<PyAny>,
    public_route: Py<PyAny>,
    effective_route_context: Option<Py<PyAny>>,
    response_model: Option<Py<PyAny>>,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    router_dependencies: Vec<Py<PyAny>>,
    plan: CallablePlan,
}

#[pyclass(name = "APIRoute", module = "fastapi.routing")]
struct PyApiRoute {
    path: String,
    path_format: String,
    name: String,
    methods: Vec<String>,
    tags: Vec<String>,
    endpoint: Py<PyAny>,
}

#[pyclass(name = "RouteContext", module = "fastapi.routing")]
struct PyRouteContext {
    original_route: Py<PyAny>,
    effective_route: Py<PyAny>,
}

#[pyclass(module = "fastapi.routing")]
struct PyRouteContextIterator {
    routes: Py<PyAny>,
    iterator: Option<Py<PyIterator>>,
    finished: bool,
}

#[pymethods]
impl PyApiRoute {
    #[getter]
    fn path(&self) -> &str {
        &self.path
    }

    #[getter]
    fn path_format(&self) -> &str {
        &self.path_format
    }

    #[getter]
    fn name(&self) -> &str {
        &self.name
    }

    #[getter]
    fn methods(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        PySet::new(py, self.methods.iter().map(String::as_str))
            .map(|methods| methods.into_any().unbind())
    }

    #[getter]
    fn tags(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let tags = PyList::empty(py);
        for tag in &self.tags {
            tags.append(tag)?;
        }
        Ok(tags.into_any().unbind())
    }

    #[getter]
    fn endpoint(&self, py: Python<'_>) -> Py<PyAny> {
        self.endpoint.clone_ref(py)
    }
}

#[pymethods]
impl PyRouteContext {
    #[getter]
    fn original_route(&self, py: Python<'_>) -> Py<PyAny> {
        self.original_route.clone_ref(py)
    }

    fn __getattr__(&self, py: Python<'_>, attribute: &str) -> PyResult<Py<PyAny>> {
        self.effective_route
            .bind(py)
            .getattr(attribute)
            .map(Bound::unbind)
    }
}

#[pymethods]
impl PyRouteContextIterator {
    fn __iter__(self_: Py<Self>) -> Py<Self> {
        self_
    }

    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        if self.finished {
            return Ok(None);
        }
        if self.iterator.is_none() {
            self.iterator = match self.routes.bind(py).try_iter() {
                Ok(iterator) => Some(iterator.unbind()),
                Err(error) => {
                    self.finished = true;
                    return Err(error);
                }
            };
        }
        let Some(iterator) = self.iterator.as_ref() else {
            self.finished = true;
            return Ok(None);
        };
        let mut iterator = iterator.clone_ref(py).into_bound(py);
        let route = match iterator.next() {
            Some(Ok(route)) => route,
            Some(Err(error)) => {
                self.finished = true;
                return Err(error);
            }
            None => {
                self.finished = true;
                return Ok(None);
            }
        };
        if route.is_instance_of::<PyRouteContext>() {
            return Ok(Some(route.unbind()));
        }
        let route = route.unbind();
        match new_route_context(py, route.clone_ref(py), route) {
            Ok(context) => Ok(Some(context)),
            Err(error) => {
                self.finished = true;
                Err(error)
            }
        }
    }
}

fn new_api_route_view(
    py: Python<'_>,
    path: &str,
    path_format: &str,
    method: &str,
    name: &str,
    tags: &[String],
    endpoint: Py<PyAny>,
) -> PyResult<Py<PyAny>> {
    Py::new(
        py,
        PyApiRoute {
            path: path.to_owned(),
            path_format: path_format.to_owned(),
            name: name.to_owned(),
            methods: vec![method.to_owned()],
            tags: tags.to_vec(),
            endpoint,
        },
    )
    .map(Py::into_any)
}

fn new_route_context(
    py: Python<'_>,
    original_route: Py<PyAny>,
    effective_route: Py<PyAny>,
) -> PyResult<Py<PyAny>> {
    Py::new(
        py,
        PyRouteContext {
            original_route,
            effective_route,
        },
    )
    .map(Py::into_any)
}

fn route_views(py: Python<'_>, routes: &[FastApiRoute]) -> PyResult<Py<PyList>> {
    let views = PyList::empty(py);
    for route in routes {
        views.append(route.public_route.bind(py))?;
    }
    Ok(views.unbind())
}

#[pyfunction(name = "iter_route_contexts")]
fn py_iter_route_contexts(py: Python<'_>, routes: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    Py::new(
        py,
        PyRouteContextIterator {
            routes: routes.clone().unbind(),
            iterator: None,
            finished: false,
        },
    )
    .map(Py::into_any)
}

struct FastApiRouterInclude {
    route_position: usize,
    router: Py<PyAny>,
    prefix: String,
}

#[derive(Clone, Copy)]
enum FastApiDocsRoute {
    SwaggerUi,
    OAuth2Redirect,
    ReDoc,
}

struct FastApiWebSocketRoute {
    path: String,
    name: String,
    route_scope: Py<PyAny>,
    param_convertors: Py<PyDict>,
    route_dependencies: Vec<Py<PyAny>>,
    endpoint: Py<PyAny>,
    plan: Option<CallablePlan>,
    raw: bool,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum FastApiFrontendFallback {
    Auto,
    IndexHtml,
    NotFoundHtml,
    None,
}

struct FastApiFrontendRoute {
    path: String,
    static_files: Py<PyAny>,
    fallback: FastApiFrontendFallback,
    dependency_plan: CallablePlan,
}

struct ResponseModelOptions {
    include: Option<Py<PyAny>>,
    exclude: Option<Py<PyAny>>,
    by_alias: bool,
    exclude_unset: bool,
    exclude_defaults: bool,
    exclude_none: bool,
    include_in_schema: bool,
    response_description: Option<String>,
    responses: Option<Py<PyAny>>,
    summary: Option<String>,
    operation_id: Option<String>,
    deprecated: Option<bool>,
    tags: Option<Vec<String>>,
    dependencies: Vec<Py<PyAny>>,
    response_class: Option<Py<PyAny>>,
    name: Option<String>,
}

struct ParameterOpenApiPlan {
    name: String,
    location: String,
    required: bool,
    annotation: Py<PyAny>,
    schema_config: Option<Py<PyAny>>,
    default: Option<Py<PyAny>>,
    title: Option<String>,
    description: Option<String>,
    deprecated: bool,
}

#[pyclass(name = "FastAPI", module = "fastapi_rs._core")]
pub(crate) struct PyFastApi {
    state: Py<PyAny>,
    route_scope_prefix: String,
    title: String,
    summary: Option<String>,
    description: String,
    version: String,
    openapi_url: String,
    swagger_ui_init_oauth: Option<Py<PyAny>>,
    terms_of_service: Option<String>,
    contact: Option<Py<PyAny>>,
    license_info: Option<Py<PyAny>>,
    openapi_external_docs: Option<Py<PyAny>>,
    dependencies: Vec<Py<PyAny>>,
    default_response_class: Option<Py<PyAny>>,
    redirect_slashes: bool,
    strict_content_type: Option<bool>,
    exception_handlers: Py<PyAny>,
    lifespan: FastApiLifespan,
    dependency_overrides: Py<PyDict>,
    router: FastApiOperationRouter,
    websocket_router: FastApiOperationRouter,
    docs_router: RouteTable,
    docs_routes: Vec<FastApiDocsRoute>,
    named_routes: NamedRouteTable,
    routes: Vec<FastApiRoute>,
    router_includes: Vec<FastApiRouterInclude>,
    routes_version: AtomicU64,
    openapi_cache: Mutex<OpenApiCache>,
    mounted_routes: Vec<Py<PyAny>>,
    frontend_routes: Vec<FastApiFrontendRoute>,
    websocket_routes: Vec<FastApiWebSocketRoute>,
    user_middleware: Vec<Py<PyAny>>,
    middleware_stack: Option<Py<PyAny>>,
}

struct OpenApiCache {
    schema: Py<PyAny>,
    routes_version: Option<u64>,
}

#[pyclass(name = "_FastAPIAsgiApp", module = "fastapi_rs._core")]
struct PyFastApiAsgiApp {
    app: Py<PyFastApi>,
}

#[pyclass(name = "_MiddlewareDecorator", module = "fastapi_rs._core")]
struct PyMiddlewareDecorator {
    app: Py<PyFastApi>,
}

#[pyclass(
    name = "_FastAPIHTTPMiddleware",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiHttpMiddleware {
    app: Py<PyAny>,
    dispatch: Py<PyAny>,
}

#[pyclass(
    name = "_FastAPIMessageCapture",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiMessageCapture {
    messages: Py<PyList>,
}

#[pyclass(
    name = "_FastAPICachedReceiveDescriptor",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiCachedReceiveDescriptor;

#[pyclass(unsendable)]
struct PyFastApiCachedReceive {
    request: Py<PyAny>,
}

#[pyclass(name = "_FastAPIHTTPExceptionHandler", module = "fastapi_rs._core")]
struct PyFastApiHttpExceptionHandler;

#[pyclass(
    name = "_FastAPIRequestValidationExceptionHandler",
    module = "fastapi_rs._core"
)]
struct PyFastApiRequestValidationExceptionHandler;

#[pyclass(name = "_ExceptionHandlerDecorator", module = "fastapi_rs._core")]
struct PyExceptionHandlerDecorator {
    app: Py<PyFastApi>,
    exception_key: Py<PyAny>,
}

#[pyclass(name = "_FastAPICallNext", module = "fastapi_rs._core", unsendable)]
struct PyFastApiCallNext {
    app: Py<PyAny>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    post_response_error: Rc<RefCell<Option<PyErr>>>,
}

#[pymethods]
impl PyFastApiAsgiApp {
    fn __call__(
        &self,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        fastapi_core_call(py, self.app.clone_ref(py), scope, receive, send)
    }
}

#[pymethods]
impl PyMiddlewareDecorator {
    fn __call__(&self, py: Python<'_>, dispatch: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let middleware_class = py.get_type::<PyFastApiHttpMiddleware>();
        let kwargs = PyDict::new(py);
        kwargs.set_item("dispatch", dispatch.bind(py))?;
        self.app
            .bind(py)
            .call_method("add_middleware", (middleware_class,), Some(&kwargs))?;
        Ok(dispatch)
    }
}

#[pyclass(name = "_WebSocketDecorator", module = "fastapi_rs._core")]
struct PyWebSocketDecorator {
    app: Py<PyFastApi>,
    path: String,
    name: Option<String>,
    dependencies: Vec<Py<PyAny>>,
}

#[pyclass(name = "_RawWebSocketDecorator", module = "fastapi_rs._core")]
struct PyRawWebSocketDecorator {
    app: Py<PyFastApi>,
    path: String,
    name: Option<String>,
}

#[pyclass(name = "APIRouter", module = "fastapi_rs._core", unsendable)]
pub(crate) struct PyApiRouter {
    inner: Py<PyFastApi>,
    prefix: String,
    tags: Vec<String>,
    deprecated: Option<bool>,
    include_in_schema: bool,
    dependencies: Vec<Py<PyAny>>,
    strict_content_type: Option<bool>,
}

struct RouterIncludePolicy<'policy> {
    prefix: &'policy str,
    tags: &'policy [String],
    dependencies: &'policy [Py<PyAny>],
    deprecated: Option<bool>,
    include_in_schema: bool,
    strict_content_type: Option<bool>,
}

#[pymethods]
impl PyFastApi {
    #[new]
    #[pyo3(signature = (*, title = "FastAPI", summary = None, description = "", version = "0.1.0", openapi_url = "/openapi.json", docs_url = "/docs", redoc_url = "/redoc", swagger_ui_init_oauth = None, terms_of_service = None, contact = None, license_info = None, openapi_external_docs = None, dependencies = None, default_response_class = None, redirect_slashes = true, middleware = None, exception_handlers = None, on_startup = None, on_shutdown = None, lifespan = None, strict_content_type = true))]
    // lint-exception: PyO3 needs one Rust argument per Python constructor keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python FastAPI constructor keyword signature"
    )]
    fn new(
        py: Python<'_>,
        title: &str,
        summary: Option<String>,
        description: &str,
        version: &str,
        openapi_url: &str,
        docs_url: Option<&str>,
        redoc_url: Option<&str>,
        swagger_ui_init_oauth: Option<Py<PyAny>>,
        terms_of_service: Option<String>,
        contact: Option<Py<PyAny>>,
        license_info: Option<Py<PyAny>>,
        openapi_external_docs: Option<Py<PyAny>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        default_response_class: Option<Py<PyAny>>,
        redirect_slashes: bool,
        middleware: Option<Py<PyAny>>,
        exception_handlers: Option<Py<PyAny>>,
        on_startup: Option<Py<PyAny>>,
        on_shutdown: Option<Py<PyAny>>,
        lifespan: Option<Py<PyAny>>,
        strict_content_type: bool,
    ) -> PyResult<Self> {
        let user_middleware = match middleware {
            Some(middleware) => py
                .import("builtins")?
                .getattr("list")?
                .call1((middleware,))?
                .extract()?,
            None => Vec::new(),
        };
        let state = py
            .import("starlette.datastructures")?
            .getattr("State")?
            .call0()?
            .unbind();
        let exception_handlers = match exception_handlers {
            Some(handlers) => py
                .import("builtins")?
                .getattr("dict")?
                .call1((handlers,))?
                .cast_into::<PyDict>()?,
            None => PyDict::new(py),
        };
        let http_exception_type = py
            .import("starlette.exceptions")?
            .getattr("HTTPException")?;
        if !exception_handlers.contains(&http_exception_type)? {
            exception_handlers.set_item(
                http_exception_type,
                Py::new(py, PyFastApiHttpExceptionHandler)?.into_any(),
            )?;
        }
        let request_validation_exception_type = crate::errors::request_validation_error_type(py);
        if !exception_handlers.contains(&request_validation_exception_type)? {
            exception_handlers.set_item(
                request_validation_exception_type,
                Py::new(py, PyFastApiRequestValidationExceptionHandler)?.into_any(),
            )?;
        }
        let mut docs_router = RouteTable::new();
        let mut docs_routes = Vec::new();
        if !openapi_url.is_empty() {
            if let Some(path) = docs_url {
                docs_router
                    .add_route(path, ["GET"])
                    .map_err(|error| PyValueError::new_err(error.to_string()))?;
                docs_routes.push(FastApiDocsRoute::SwaggerUi);
                docs_router
                    .add_route("/docs/oauth2-redirect", ["GET"])
                    .map_err(|error| PyValueError::new_err(error.to_string()))?;
                docs_routes.push(FastApiDocsRoute::OAuth2Redirect);
            }
            if let Some(path) = redoc_url {
                docs_router
                    .add_route(path, ["GET"])
                    .map_err(|error| PyValueError::new_err(error.to_string()))?;
                docs_routes.push(FastApiDocsRoute::ReDoc);
            }
        }
        let lifespan = FastApiLifespan::new(py, on_startup, on_shutdown, lifespan)?;
        Ok(Self {
            state,
            route_scope_prefix: String::new(),
            title: title.to_owned(),
            summary,
            description: description.to_owned(),
            version: version.to_owned(),
            openapi_url: openapi_url.to_owned(),
            swagger_ui_init_oauth,
            terms_of_service,
            contact,
            license_info,
            openapi_external_docs,
            dependencies: dependencies.unwrap_or_default(),
            default_response_class,
            redirect_slashes,
            strict_content_type: Some(strict_content_type),
            exception_handlers: exception_handlers.unbind().into_any(),
            lifespan,
            dependency_overrides: PyDict::new(py).unbind(),
            router: FastApiOperationRouter::new(),
            websocket_router: FastApiOperationRouter::new(),
            docs_router,
            docs_routes,
            named_routes: NamedRouteTable::new(),
            routes: Vec::new(),
            router_includes: Vec::new(),
            routes_version: AtomicU64::new(0),
            openapi_cache: Mutex::new(OpenApiCache {
                schema: py.None(),
                routes_version: None,
            }),
            mounted_routes: Vec::new(),
            frontend_routes: Vec::new(),
            websocket_routes: Vec::new(),
            user_middleware,
            middleware_stack: None,
        })
    }

    #[getter]
    fn state(&self, py: Python<'_>) -> Py<PyAny> {
        self.state.clone_ref(py)
    }

    #[getter]
    fn routes(&self, py: Python<'_>) -> PyResult<Py<PyList>> {
        route_views(py, &self.routes)
    }

    #[getter]
    fn strict_content_type(&self) -> bool {
        self.strict_content_type.unwrap_or(true)
    }

    #[setter]
    fn set_strict_content_type(&mut self, strict_content_type: bool) {
        self.strict_content_type = Some(strict_content_type);
    }

    #[setter]
    fn set_state(&mut self, state: Py<PyAny>) {
        self.state = state;
    }

    #[getter]
    fn openapi_schema(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.openapi_cache
            .lock()
            .map(|cache| cache.schema.clone_ref(py))
            .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))
    }

    #[setter]
    fn set_openapi_schema(&self, schema: Py<PyAny>) -> PyResult<()> {
        self.openapi_cache
            .lock()
            .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?
            .schema = schema;
        Ok(())
    }

    #[getter]
    fn dependency_overrides(&self, py: Python<'_>) -> Py<PyDict> {
        self.dependency_overrides.clone_ref(py)
    }

    #[setter]
    fn set_dependency_overrides(&mut self, dependency_overrides: Py<PyDict>) {
        self.dependency_overrides = dependency_overrides;
    }

    #[getter]
    fn exception_handlers(&self, py: Python<'_>) -> Py<PyAny> {
        self.exception_handlers.clone_ref(py)
    }

    #[setter]
    fn set_exception_handlers(&mut self, exception_handlers: Py<PyAny>) {
        self.exception_handlers = exception_handlers;
    }

    fn on_event(&self, py: Python<'_>, event_type: &str) -> PyResult<Py<PyAny>> {
        warn_on_event(py, true)?;
        self.lifespan.decorator(py, event_type)
    }

    fn add_exception_handler(
        &self,
        py: Python<'_>,
        exc_class_or_status_code: Py<PyAny>,
        handler: Py<PyAny>,
    ) -> PyResult<()> {
        self.exception_handlers
            .bind(py)
            .set_item(exc_class_or_status_code.bind(py), handler.bind(py))
    }

    fn exception_handler(
        slf: Py<Self>,
        py: Python<'_>,
        exc_class_or_status_code: Py<PyAny>,
    ) -> PyResult<Py<PyExceptionHandlerDecorator>> {
        Py::new(
            py,
            PyExceptionHandlerDecorator {
                app: slf,
                exception_key: exc_class_or_status_code,
            },
        )
    }

    #[pyo3(signature = (middleware_class, *args, **kwargs))]
    fn add_middleware(
        &mut self,
        py: Python<'_>,
        middleware_class: Py<PyAny>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        if self.middleware_stack.is_some() {
            return Err(PyRuntimeError::new_err(
                "Cannot add middleware after an application has started",
            ));
        }
        let middleware_type = py.import("starlette.middleware")?.getattr("Middleware")?;
        let mut argument_values = Vec::with_capacity(args.len() + 1);
        argument_values.push(middleware_class.bind(py).clone());
        argument_values.extend(args.iter());
        let arguments = PyTuple::new(py, argument_values)?;
        let registration = middleware_type.call(&arguments, kwargs)?;
        self.user_middleware.insert(0, registration.unbind());
        Ok(())
    }

    fn middleware(
        slf: Py<Self>,
        py: Python<'_>,
        _middleware_type: &str,
    ) -> PyResult<Py<PyMiddlewareDecorator>> {
        Py::new(py, PyMiddlewareDecorator { app: slf })
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    // Distinguish omission (infer from the endpoint return annotation) from explicit None (opt out).
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn post(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "POST",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn get(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "GET",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn put(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "PUT",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn delete(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "DELETE",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn patch(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "PATCH",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn head(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "HEAD",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn options(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "OPTIONS",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, response_class = None, name = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, response_class=None, name=None)"
    )]
    fn trace(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        response_class: Option<Py<PyAny>>,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "TRACE",
            response_model,
            status_code,
            ResponseModelOptions {
                include: response_model_include,
                exclude: response_model_exclude,
                by_alias: response_model_by_alias,
                exclude_unset: response_model_exclude_unset,
                exclude_defaults: response_model_exclude_defaults,
                exclude_none: response_model_exclude_none,
                include_in_schema,
                response_class,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                name,
            },
        )
    }

    #[pyo3(
        signature = (path, *, dependencies = None, include_in_schema = true, name = None),
        text_signature = "($self, path, *, dependencies=None, include_in_schema=True, name=None)"
    )]
    fn api_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        dependencies: Option<Vec<Py<PyAny>>>,
        include_in_schema: bool,
        name: Option<String>,
    ) -> PyResult<Py<PyOperationDecorator>> {
        operation_decorator(
            slf,
            py,
            path,
            "GET",
            Some(py.NotImplemented()),
            None,
            ResponseModelOptions {
                include: None,
                exclude: None,
                by_alias: true,
                exclude_unset: false,
                exclude_defaults: false,
                exclude_none: false,
                include_in_schema,
                response_description: None,
                responses: None,
                summary: None,
                operation_id: None,
                deprecated: None,
                tags: None,
                dependencies: dependencies.unwrap_or_default(),
                response_class: None,
                name,
            },
        )
    }

    #[pyo3(
        signature = (path, endpoint, *, dependencies = None, include_in_schema = true, name = None),
        text_signature = "($self, path, endpoint, *, dependencies=None, include_in_schema=True, name=None)"
    )]
    fn add_api_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        endpoint: Py<PyAny>,
        dependencies: Option<Vec<Py<PyAny>>>,
        include_in_schema: bool,
        name: Option<String>,
    ) -> PyResult<()> {
        let decorator = Self::api_route(slf, py, path, dependencies, include_in_schema, name)?;
        decorator.bind(py).call1((endpoint,))?;
        Ok(())
    }

    #[pyo3(signature = (path, app, name=None))]
    fn mount(
        &mut self,
        py: Python<'_>,
        path: &str,
        app: Py<PyAny>,
        name: Option<String>,
    ) -> PyResult<()> {
        let mount_type = py.import("starlette.routing")?.getattr("Mount")?;
        let kwargs = PyDict::new(py);
        if let Some(name) = name {
            kwargs.set_item("name", name)?;
        }
        let mount = mount_type.call((path, app.bind(py)), Some(&kwargs))?;
        self.mounted_routes.push(mount.unbind());
        Ok(())
    }

    #[pyo3(signature = (path, route, methods=None, name=None, include_in_schema=true))]
    fn add_route(
        &mut self,
        py: Python<'_>,
        path: &str,
        route: Py<PyAny>,
        methods: Option<Py<PyAny>>,
        name: Option<String>,
        include_in_schema: bool,
    ) -> PyResult<()> {
        let route_type = py.import("starlette.routing")?.getattr("Route")?;
        let kwargs = PyDict::new(py);
        if let Some(methods) = methods {
            kwargs.set_item("methods", methods.bind(py))?;
        }
        if let Some(name) = name {
            kwargs.set_item("name", name)?;
        }
        kwargs.set_item("include_in_schema", include_in_schema)?;
        let route_object = route_type.call((path, route.bind(py)), Some(&kwargs))?;
        self.mounted_routes.push(route_object.unbind());
        Ok(())
    }

    #[pyo3(signature = (host, app, name=None))]
    fn host(
        &mut self,
        py: Python<'_>,
        host: &str,
        app: Py<PyAny>,
        name: Option<String>,
    ) -> PyResult<()> {
        let host_type = py.import("starlette.routing")?.getattr("Host")?;
        let kwargs = PyDict::new(py);
        if let Some(name) = name {
            kwargs.set_item("name", name)?;
        }
        let route = host_type.call((host, app.bind(py)), Some(&kwargs))?;
        self.mounted_routes.push(route.unbind());
        Ok(())
    }

    #[pyo3(signature = (path, *, directory, fallback=default_frontend_auto(), check_dir=default_frontend_auto()))]
    fn frontend(
        &mut self,
        py: Python<'_>,
        path: &str,
        directory: Py<PyAny>,
        fallback: Py<PyAny>,
        check_dir: Py<PyAny>,
    ) -> PyResult<()> {
        let dependencies = self
            .dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        add_frontend_route(
            self,
            py,
            path,
            directory,
            fallback,
            check_dir,
            &dependencies,
        )
    }

    #[pyo3(signature = (path, name = None, *, dependencies = None))]
    fn websocket(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        name: Option<String>,
        dependencies: Option<Vec<Py<PyAny>>>,
    ) -> PyResult<Py<PyWebSocketDecorator>> {
        Py::new(
            py,
            PyWebSocketDecorator {
                app: slf,
                path: path.to_owned(),
                name,
                dependencies: dependencies.unwrap_or_default(),
            },
        )
    }

    #[pyo3(signature = (path, name = None))]
    fn websocket_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        name: Option<String>,
    ) -> PyResult<Py<PyRawWebSocketDecorator>> {
        Py::new(
            py,
            PyRawWebSocketDecorator {
                app: slf,
                path: path.to_owned(),
                name,
            },
        )
    }

    #[pyo3(signature = (path, endpoint, name = None))]
    fn add_websocket_route(
        &mut self,
        py: Python<'_>,
        path: &str,
        endpoint: Py<PyAny>,
        name: Option<String>,
    ) -> PyResult<()> {
        add_raw_websocket_route(self, py, path, endpoint.bind(py), name.as_deref())
    }

    #[pyo3(signature = (path, endpoint, name = None, *, dependencies = None))]
    fn add_api_websocket_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        endpoint: Py<PyAny>,
        name: Option<String>,
        dependencies: Option<Vec<Py<PyAny>>>,
    ) -> PyResult<()> {
        let decorator = Self::websocket(slf, py, path, name, dependencies)?;
        decorator.bind(py).call1((endpoint,))?;
        Ok(())
    }

    #[pyo3(signature = (router, *, prefix = "", tags = None, dependencies = None, deprecated = None, include_in_schema = true))]
    // lint-exception: preserve FastAPI's include_router keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible include_router signature"
    )]
    fn include_router(
        &mut self,
        py: Python<'_>,
        router: Py<PyApiRouter>,
        prefix: &str,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        deprecated: Option<bool>,
        include_in_schema: bool,
    ) -> PyResult<()> {
        let router_object = router.clone_ref(py).into_any();
        let include_prefix = prefix.to_owned();
        let router = router.bind(py).borrow();
        let prefix = combined_router_prefix(prefix, &router.prefix)?;
        let tags = combined_router_tags(tags.as_deref(), &router.tags);
        let mut inherited_dependencies = self
            .dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        inherited_dependencies.extend(dependencies.unwrap_or_default());
        inherited_dependencies.extend(
            router
                .dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py)),
        );
        let deprecated = combined_deprecated(deprecated, router.deprecated);
        let include_in_schema = include_in_schema && router.include_in_schema;
        let source = router.inner.bind(py).borrow();
        let route_position = self.routes.len();
        merge_router_routes(
            py,
            self,
            &source,
            RouterIncludePolicy {
                prefix: &prefix,
                tags: &tags,
                dependencies: &inherited_dependencies,
                deprecated,
                include_in_schema,
                strict_content_type: self.strict_content_type,
            },
        )?;
        self.router_includes.push(FastApiRouterInclude {
            route_position,
            router: router_object,
            prefix: include_prefix,
        });
        self.lifespan.include_router(py, &source.lifespan)?;
        self.bump_routes_version();
        Ok(())
    }

    fn openapi(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let routes_version = self.routes_version.load(Ordering::Relaxed);
        let (cached_schema, cached_routes_version) = self
            .openapi_cache
            .lock()
            .map(|cache| (cache.schema.clone_ref(py), cache.routes_version))
            .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
        if cached_routes_version == Some(routes_version) && cached_schema.bind(py).is_truthy()? {
            return Ok(cached_schema);
        }

        let schema = self.openapi_document(py, None)?;
        let mut cache = self
            .openapi_cache
            .lock()
            .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
        cache.schema = schema.clone_ref(py);
        cache.routes_version = Some(routes_version);
        Ok(schema)
    }

    #[pyo3(
        signature = (name, /, **path_params),
        text_signature = "($self, name, /, **path_params)"
    )]
    fn url_path_for(
        &self,
        py: Python<'_>,
        name: &str,
        path_params: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let empty_path_params = PyDict::new(py);
        let path_params = path_params.unwrap_or(&empty_path_params);
        let mut supplied_names = path_params.keys().extract::<Vec<String>>()?;
        supplied_names.sort();

        let mut matching_route = None;
        let no_match_type = py.import("starlette.routing")?.getattr("NoMatchFound")?;
        for route_position in 0..=self.routes.len() {
            for include in &self.router_includes {
                if include.route_position != route_position {
                    continue;
                }
                if let Some(url_path) = try_included_router_url_path_for(
                    py,
                    &include.router,
                    &include.prefix,
                    name,
                    path_params,
                    &no_match_type,
                )? {
                    return Ok(url_path);
                }
            }

            let Some(route) = self.routes.get(route_position) else {
                continue;
            };
            if route.name == name {
                let mut expected_names = route
                    .param_convertors
                    .bind(py)
                    .keys()
                    .extract::<Vec<String>>()?;
                expected_names.sort();
                if expected_names == supplied_names {
                    matching_route = Some(route);
                    break;
                }
            }
        }

        for route in &self.websocket_routes {
            if route.name != name {
                continue;
            }
            let url_path =
                route
                    .route_scope
                    .bind(py)
                    .call_method("url_path_for", (name,), Some(path_params));
            let url_path = match url_path {
                Ok(url_path) => url_path,
                Err(error) if error.is_instance(py, &no_match_type) => continue,
                Err(error) => return Err(error),
            };
            if self.route_scope_prefix.is_empty() {
                return Ok(url_path.unbind());
            }
            let url_path_string = url_path.str()?;
            let path = url_path_string
                .to_str()?
                .strip_prefix(&self.route_scope_prefix);
            let Some(path) = path else {
                return Ok(url_path.unbind());
            };
            return py
                .import("starlette.datastructures")?
                .getattr("URLPath")?
                .call1((
                    path,
                    url_path.getattr("protocol")?,
                    url_path.getattr("host")?,
                ))
                .map(Bound::unbind);
        }

        let Some(route) = matching_route else {
            let exception = no_match_type.call1((name, path_params))?;
            return Err(PyErr::from_value(exception));
        };

        let convertors = route.param_convertors.bind(py);
        let mut formatted_path_params = Vec::with_capacity(path_params.len());
        for (parameter_name, value) in path_params.iter() {
            let parameter_name = parameter_name.extract::<String>()?;
            let convertor = convertors.get_item(&parameter_name)?.ok_or_else(|| {
                PyRuntimeError::new_err("matched route is missing a path parameter convertor")
            })?;
            let formatted_value = convertor
                .call_method1("to_string", (value,))?
                .extract::<String>()?;
            formatted_path_params.push((parameter_name, formatted_value));
        }

        let route_path = match self.named_routes.url_path_for(name, &formatted_path_params) {
            Ok(path) => path,
            Err(NamedRouteError::NoMatchFound { .. }) => {
                let no_match_type = py.import("starlette.routing")?.getattr("NoMatchFound")?;
                let exception = no_match_type.call1((name, path_params))?;
                return Err(PyErr::from_value(exception));
            }
            Err(NamedRouteError::RouteFormatting(error)) => {
                return Err(PyValueError::new_err(error.to_string()));
            }
        };
        py.import("starlette.datastructures")?
            .getattr("URLPath")?
            .call1((route_path.path, route_path.protocol, route_path.host))
            .map(Bound::unbind)
    }

    fn __call__(
        slf: Py<Self>,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        scope.bind(py).set_item("app", slf.clone_ref(py))?;
        Self::middleware_stack_for(slf, py)?
            .bind(py)
            .call1((scope, receive, send))
            .map(Bound::unbind)
    }
}

#[pymethods]
impl PyFastApiHttpMiddleware {
    #[new]
    #[pyo3(signature = (app, *, dispatch))]
    fn new(app: Py<PyAny>, dispatch: Py<PyAny>) -> Self {
        Self { app, dispatch }
    }

    fn __call__(
        &self,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        if scope.bind(py).get_item("type")?.extract::<String>()? != "http" {
            return self
                .app
                .bind(py)
                .call1((scope, receive, send))
                .map(Bound::unbind);
        }
        into_python_awaitable(
            py,
            FastApiHttpMiddlewareCall {
                app: self.app.clone_ref(py),
                dispatch: self.dispatch.clone_ref(py),
                scope,
                receive,
                send,
                pending: None,
                post_response_error: Rc::new(RefCell::new(None)),
            },
        )
    }
}

#[pymethods]
impl PyFastApiMessageCapture {
    fn __call__(&self, py: Python<'_>, message: Py<PyAny>) -> PyResult<Py<PyAny>> {
        self.messages.bind(py).append(message)?;
        into_python_awaitable(py, FastApiImmediateAwaitable { result: py.None() })
    }
}

#[pymethods]
impl PyFastApiCachedReceiveDescriptor {
    fn __get__(
        slf: Py<Self>,
        py: Python<'_>,
        request: Option<Bound<'_, PyAny>>,
        _owner: Option<Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let Some(request) = request else {
            return Ok(slf.into_any());
        };
        Py::new(
            py,
            PyFastApiCachedReceive {
                request: request.unbind(),
            },
        )
        .map(Into::into)
    }
}

#[pymethods]
impl PyFastApiCachedReceive {
    fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            FastApiCachedReceiveMachine {
                request: self.request.clone_ref(py),
                pending: None,
            },
        )
    }
}

type FastApiMiddlewareBodyReceiveState = (Option<Py<PyAny>>, bool, bool, bool, bool);

enum FastApiCachedReceivePending {
    StreamChunk,
    ConsumedReceive,
}

struct FastApiCachedReceiveMachine {
    request: Py<PyAny>,
    pending: Option<FastApiCachedReceivePending>,
}

impl AwaitableStateMachine for FastApiCachedReceiveMachine {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.start(py),
            MachineResume::Value(value) => match self.pending.take() {
                Some(FastApiCachedReceivePending::StreamChunk) => self.stream_chunk(py, value),
                Some(FastApiCachedReceivePending::ConsumedReceive) => {
                    self.consumed_receive(py, value)
                }
                None => Err(PyRuntimeError::new_err(
                    "cached request resumed without a pending receive",
                )),
            },
            MachineResume::Error(error) => self.receive_error(py, error),
        }
    }
}

impl FastApiCachedReceiveMachine {
    fn start(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let request = self.request.bind(py);
        let (body, stream_consumed, request_disconnected, disconnected, consumed) =
            fastapi_middleware_body_receive_state(request)?;
        if disconnected {
            return fastapi_cached_disconnect_message(py);
        }
        if consumed {
            if request_disconnected {
                set_fastapi_cached_receive_flags(request, Some(true), None)?;
                return fastapi_cached_disconnect_message(py);
            }
            return self.await_original_receive(py);
        }
        if let Some(body) = body {
            set_fastapi_cached_receive_flags(request, None, Some(true))?;
            return fastapi_cached_request_message(py, body, false);
        }
        if stream_consumed {
            set_fastapi_cached_receive_flags(request, None, Some(true))?;
            return fastapi_cached_request_message(
                py,
                PyBytes::new(py, b"").into_any().unbind(),
                false,
            );
        }

        let stream = request.call_method0("stream")?;
        let awaitable = stream.call_method0("__anext__")?;
        self.pending = Some(FastApiCachedReceivePending::StreamChunk);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn await_original_receive(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let receive = self
            .request
            .bind(py)
            .getattr("_body_state")?
            .getattr("receive")?
            .call_method0("__call__")?;
        self.pending = Some(FastApiCachedReceivePending::ConsumedReceive);
        Ok(MachineAction::Await(receive.unbind()))
    }

    fn stream_chunk(&mut self, py: Python<'_>, chunk: Py<PyAny>) -> PyResult<MachineAction> {
        let request = self.request.bind(py);
        let (_, stream_consumed, _, _, _) = fastapi_middleware_body_receive_state(request)?;
        set_fastapi_cached_receive_flags(request, None, Some(stream_consumed))?;
        fastapi_cached_request_message(py, chunk, !stream_consumed)
    }

    fn consumed_receive(&mut self, py: Python<'_>, message: Py<PyAny>) -> PyResult<MachineAction> {
        let message_bound = message.bind(py).cast::<PyDict>()?;
        let message_type = message_bound
            .get_item("type")?
            .ok_or_else(|| PyKeyError::new_err("type"))?
            .extract::<String>()?;
        if message_type != "http.disconnect" {
            return Err(PyRuntimeError::new_err(format!(
                "Unexpected message received: {message_type}"
            )));
        }
        set_fastapi_cached_receive_flags(self.request.bind(py), Some(true), None)?;
        Ok(MachineAction::Complete(message))
    }

    fn receive_error(&mut self, py: Python<'_>, error: PyErr) -> PyResult<MachineAction> {
        match self.pending.take() {
            Some(FastApiCachedReceivePending::StreamChunk) => {
                let client_disconnect = py
                    .import("starlette.requests")?
                    .getattr("ClientDisconnect")?;
                if error.value(py).is_instance(&client_disconnect)? {
                    set_fastapi_cached_receive_flags(self.request.bind(py), Some(true), None)?;
                    return fastapi_cached_disconnect_message(py);
                }
                Err(error)
            }
            Some(FastApiCachedReceivePending::ConsumedReceive) | None => Err(error),
        }
    }
}

fn fastapi_middleware_body_receive_state(
    request: &Bound<'_, PyAny>,
) -> PyResult<FastApiMiddlewareBodyReceiveState> {
    request
        .getattr("_body_state")?
        .call_method0("_base_http_wrapped_receive_state")?
        .extract()
}

fn set_fastapi_cached_receive_flags(
    request: &Bound<'_, PyAny>,
    disconnected: Option<bool>,
    consumed: Option<bool>,
) -> PyResult<()> {
    if let Some(disconnected) = disconnected {
        request.setattr("_wrapped_rcv_disconnected", disconnected)?;
    }
    if let Some(consumed) = consumed {
        request.setattr("_wrapped_rcv_consumed", consumed)?;
    }
    request.getattr("_body_state")?.call_method1(
        "_base_http_set_wrapped_receive_flags",
        (disconnected, consumed),
    )?;
    Ok(())
}

fn fastapi_cached_disconnect_message(py: Python<'_>) -> PyResult<MachineAction> {
    let message = PyDict::new(py);
    message.set_item("type", "http.disconnect")?;
    Ok(MachineAction::Complete(message.into_any().unbind()))
}

fn fastapi_cached_request_message(
    py: Python<'_>,
    body: Py<PyAny>,
    more_body: bool,
) -> PyResult<MachineAction> {
    let message = PyDict::new(py);
    message.set_item("type", "http.request")?;
    message.set_item("body", body)?;
    message.set_item("more_body", more_body)?;
    Ok(MachineAction::Complete(message.into_any().unbind()))
}

#[pymethods]
impl PyFastApiHttpExceptionHandler {
    fn __call__(
        &self,
        py: Python<'_>,
        _request: Py<PyAny>,
        exception: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let exception = exception.bind(py);
        let status_code = exception.getattr("status_code")?.extract::<u16>()?;
        let response_module = py.import("starlette.responses")?;
        let has_body = status_code >= 200 && !matches!(status_code, 204 | 205 | 304);
        let response_type = if has_body {
            response_module.getattr("JSONResponse")?
        } else {
            response_module.getattr("Response")?
        };
        let kwargs = PyDict::new(py);
        kwargs.set_item("status_code", status_code)?;
        let headers = exception.getattr("headers")?;
        if !headers.is_none() {
            kwargs.set_item("headers", headers)?;
        }
        if has_body {
            let content = PyDict::new(py);
            content.set_item("detail", exception.getattr("detail")?)?;
            response_type
                .call((content,), Some(&kwargs))
                .map(Bound::unbind)
        } else {
            response_type.call((), Some(&kwargs)).map(Bound::unbind)
        }
    }
}

#[pymethods]
impl PyFastApiRequestValidationExceptionHandler {
    fn __call__(
        &self,
        py: Python<'_>,
        _request: Py<PyAny>,
        exception: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let encoded_errors =
            jsonable_encoder_default(py, &exception.bind(py).call_method0("errors")?)?;
        let content = PyDict::new(py);
        content.set_item("detail", encoded_errors)?;
        let kwargs = PyDict::new(py);
        kwargs.set_item("status_code", 422)?;
        py.import("starlette.responses")?
            .getattr("JSONResponse")?
            .call((content,), Some(&kwargs))
            .map(Bound::unbind)
    }
}

#[pymethods]
impl PyExceptionHandlerDecorator {
    fn __call__(&self, py: Python<'_>, handler: Py<PyAny>) -> PyResult<Py<PyAny>> {
        self.app.bind(py).call_method1(
            "add_exception_handler",
            (self.exception_key.bind(py), handler.bind(py)),
        )?;
        Ok(handler)
    }
}

#[pymethods]
impl PyFastApiCallNext {
    fn __call__(&self, py: Python<'_>, _request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let messages = PyList::empty(py).unbind();
        into_python_awaitable(
            py,
            FastApiCallNextMachine {
                app: self.app.clone_ref(py),
                scope: self.scope.clone_ref(py),
                receive: self.receive.clone_ref(py),
                messages,
                pending: false,
                post_response_error: self.post_response_error.clone(),
            },
        )
    }
}

enum FastApiHttpMiddlewarePending {
    Dispatch,
    Response,
}

struct FastApiHttpMiddlewareCall {
    app: Py<PyAny>,
    dispatch: Py<PyAny>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
    pending: Option<FastApiHttpMiddlewarePending>,
    post_response_error: Rc<RefCell<Option<PyErr>>>,
}

impl AwaitableStateMachine for FastApiHttpMiddlewareCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start if self.pending.is_none() => {
                let request_type = middleware_cached_request_type(py)?;
                let request = request_type
                    .bind(py)
                    .call1((self.scope.bind(py), self.receive.bind(py)))?;
                request.setattr("_wrapped_rcv_disconnected", false)?;
                request.setattr("_wrapped_rcv_consumed", false)?;
                self.receive = request.getattr("wrapped_receive")?.unbind();
                let call_next = Py::new(
                    py,
                    PyFastApiCallNext {
                        app: self.app.clone_ref(py),
                        scope: self.scope.clone_ref(py),
                        receive: self.receive.clone_ref(py),
                        post_response_error: self.post_response_error.clone(),
                    },
                )?
                .into_any();
                let response = self.dispatch.bind(py).call1((request, call_next))?.unbind();
                self.pending = Some(FastApiHttpMiddlewarePending::Dispatch);
                Ok(MachineAction::Await(response))
            }
            MachineResume::Value(response) => match self.pending.take() {
                Some(FastApiHttpMiddlewarePending::Dispatch) => {
                    let awaitable = response.bind(py).call1((
                        self.scope.bind(py),
                        self.receive.bind(py),
                        self.send.bind(py),
                    ))?;
                    self.pending = Some(FastApiHttpMiddlewarePending::Response);
                    Ok(MachineAction::Await(awaitable.unbind()))
                }
                Some(FastApiHttpMiddlewarePending::Response) => {
                    match self.post_response_error.borrow_mut().take() {
                        Some(error) => Err(error),
                        None => Ok(MachineAction::Complete(py.None())),
                    }
                }
                None => Err(PyRuntimeError::new_err(
                    "HTTP middleware resumed without a pending operation",
                )),
            },
            MachineResume::Error(error) => {
                self.pending = None;
                Err(error)
            }
            MachineResume::Start => Err(PyRuntimeError::new_err(
                "HTTP middleware received a duplicate start signal",
            )),
        }
    }
}

struct FastApiImmediateAwaitable {
    result: Py<PyAny>,
}

impl AwaitableStateMachine for FastApiImmediateAwaitable {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => Ok(MachineAction::Complete(self.result.clone_ref(py))),
            MachineResume::Value(_) | MachineResume::Error(_) => Err(PyRuntimeError::new_err(
                "immediate awaitable resumed more than once",
            )),
        }
    }
}

struct FastApiCallNextMachine {
    app: Py<PyAny>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    messages: Py<PyList>,
    pending: bool,
    post_response_error: Rc<RefCell<Option<PyErr>>>,
}

impl AwaitableStateMachine for FastApiCallNextMachine {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start if !self.pending => {
                let send = Py::new(
                    py,
                    PyFastApiMessageCapture {
                        messages: self.messages.clone_ref(py),
                    },
                )?
                .into_any();
                let awaitable =
                    self.app
                        .bind(py)
                        .call1((self.scope.bind(py), self.receive.bind(py), send))?;
                self.pending = true;
                Ok(MachineAction::Await(awaitable.unbind()))
            }
            MachineResume::Value(_) if self.pending => {
                self.pending = false;
                let response = response_from_captured_messages(py, self.messages.bind(py))?;
                Ok(MachineAction::Complete(response))
            }
            MachineResume::Error(error) if self.pending => {
                self.pending = false;
                if captured_response_started(self.messages.bind(py))? {
                    let response = response_from_captured_messages(py, self.messages.bind(py))?;
                    *self.post_response_error.borrow_mut() = Some(error);
                    Ok(MachineAction::Complete(response))
                } else {
                    Err(error)
                }
            }
            MachineResume::Value(_) | MachineResume::Error(_) | MachineResume::Start => Err(
                PyRuntimeError::new_err("call_next resumed without a pending application call"),
            ),
        }
    }
}

fn captured_response_started(messages: &Bound<'_, PyList>) -> PyResult<bool> {
    for message in messages.iter() {
        let message = message.cast::<PyDict>()?;
        let message_type = message
            .get_item("type")?
            .ok_or_else(|| PyValueError::new_err("ASGI response message has no type"))?
            .extract::<String>()?;
        if message_type == "http.response.start" {
            return Ok(true);
        }
    }
    Ok(false)
}

fn response_from_captured_messages(
    py: Python<'_>,
    messages: &Bound<'_, PyList>,
) -> PyResult<Py<PyAny>> {
    let mut status_code = None;
    let headers = PyDict::new(py);
    let mut body = Vec::new();

    for message in messages.iter() {
        let message = message.cast::<PyDict>()?;
        match message
            .get_item("type")?
            .ok_or_else(|| PyValueError::new_err("ASGI response message has no type"))?
            .extract::<String>()?
            .as_str()
        {
            "http.response.start" => {
                status_code = Some(
                    message
                        .get_item("status")?
                        .ok_or_else(|| PyValueError::new_err("ASGI response start has no status"))?
                        .extract::<u16>()?,
                );
                if let Some(raw_headers) = message.get_item("headers")? {
                    for header in raw_headers.try_iter()? {
                        let header = header?.cast_into::<PyTuple>()?;
                        let name = header.get_item(0)?.call_method1("decode", ("latin-1",))?;
                        let value = header.get_item(1)?.call_method1("decode", ("latin-1",))?;
                        headers.set_item(name, value)?;
                    }
                }
            }
            "http.response.body" => {
                if let Some(chunk) = message.get_item("body")? {
                    body.extend(chunk.extract::<Vec<u8>>()?);
                }
            }
            "http.response.debug" => {}
            other => {
                return Err(PyValueError::new_err(format!(
                    "unsupported ASGI message in HTTP middleware response: {other}"
                )));
            }
        }
    }

    let status_code = status_code
        .ok_or_else(|| PyRuntimeError::new_err("downstream ASGI app returned no response"))?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("status_code", status_code)?;
    kwargs.set_item("headers", headers)?;
    py.import("starlette.responses")?
        .getattr("Response")?
        .call((PyBytes::new(py, &body),), Some(&kwargs))
        .map(Bound::unbind)
}

fn openapi_document_for_root_path(
    py: Python<'_>,
    schema: Py<PyAny>,
    root_path: &str,
) -> PyResult<Py<PyAny>> {
    if root_path.is_empty() {
        return Ok(schema);
    }

    let schema = schema.bind(py);
    let existing_servers = schema.call_method1("get", ("servers", PyList::empty(py)))?;
    for server in existing_servers.try_iter()? {
        let server = server?;
        let server_url = server.call_method1("get", ("url",))?;
        if server_url
            .extract::<String>()
            .is_ok_and(|server_url| server_url == root_path)
        {
            return Ok(schema.clone().unbind());
        }
    }

    let schema_copy = py.import("builtins")?.getattr("dict")?.call1((schema,))?;
    let root_server = PyDict::new(py);
    root_server.set_item("url", root_path)?;
    let servers = PyList::empty(py);
    servers.append(root_server)?;
    for server in existing_servers.try_iter()? {
        servers.append(server?)?;
    }
    schema_copy.set_item("servers", servers)?;
    Ok(schema_copy.unbind())
}

impl PyFastApi {
    fn bump_routes_version(&self) {
        self.routes_version.fetch_add(1, Ordering::Relaxed);
    }

    fn middleware_stack_for(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let (cached, registrations, exception_handlers) = {
            let app = slf.bind(py).borrow();
            (
                app.middleware_stack
                    .as_ref()
                    .map(|stack| stack.clone_ref(py)),
                app.user_middleware
                    .iter()
                    .map(|registration| registration.clone_ref(py))
                    .collect::<Vec<_>>(),
                app.exception_handlers.clone_ref(py),
            )
        };
        if let Some(cached) = cached {
            return Ok(cached);
        }

        let mut stack = Py::new(
            py,
            PyFastApiAsgiApp {
                app: slf.clone_ref(py),
            },
        )?
        .into_any();
        let exception_middleware = py
            .import("starlette.middleware.exceptions")?
            .getattr("ExceptionMiddleware")?;
        let handlers = PyDict::new(py);
        let mut server_error_handler = None;
        let exception_type = py.get_type::<PyException>();
        for entry in exception_handlers
            .bind(py)
            .call_method0("items")?
            .try_iter()?
        {
            let pair = entry?.cast_into::<PyTuple>()?;
            let key = pair.get_item(0)?;
            let handler = pair.get_item(1)?;
            if key.eq(500)? || key.is(&exception_type) {
                server_error_handler = Some(handler.unbind());
            } else {
                handlers.set_item(key, handler)?;
            }
        }
        let exception_kwargs = PyDict::new(py);
        exception_kwargs.set_item("handlers", handlers)?;
        stack = exception_middleware
            .call((stack.bind(py),), Some(&exception_kwargs))?
            .unbind();
        for registration in registrations.iter().rev() {
            let registration = registration.bind(py);
            let middleware_class = registration.getattr("cls")?;
            let arguments = registration.getattr("args")?.cast_into::<PyTuple>()?;
            let keywords = registration.getattr("kwargs")?.cast_into::<PyDict>()?;
            let mut argument_values = Vec::with_capacity(arguments.len() + 1);
            argument_values.push(stack.bind(py).clone());
            argument_values.extend(arguments.iter());
            let arguments = PyTuple::new(py, argument_values)?;
            stack = middleware_class.call(&arguments, Some(&keywords))?.unbind();
        }
        let server_error_middleware = py
            .import("starlette.middleware.errors")?
            .getattr("ServerErrorMiddleware")?;
        let server_error_kwargs = PyDict::new(py);
        server_error_kwargs.set_item("handler", server_error_handler)?;
        server_error_kwargs.set_item("debug", false)?;
        stack = server_error_middleware
            .call((stack.bind(py),), Some(&server_error_kwargs))?
            .unbind();

        let mut app = slf.bind(py).borrow_mut();
        if app.middleware_stack.is_none() {
            app.middleware_stack = Some(stack.clone_ref(py));
        }
        Ok(stack)
    }

    fn openapi_document(&self, py: Python<'_>, root_path: Option<&str>) -> PyResult<Py<PyAny>> {
        let operations = self
            .routes
            .iter()
            .filter(|route| route.include_in_schema)
            .map(|route| self.openapi_operation(py, route))
            .collect::<PyResult<Vec<_>>>()?;
        openapi_document(
            py,
            OpenApiInfo {
                title: &self.title,
                summary: self.summary.as_deref(),
                description: &self.description,
                terms_of_service: self.terms_of_service.as_deref(),
                contact: self.contact.as_ref(),
                license_info: self.license_info.as_ref(),
                openapi_external_docs: self.openapi_external_docs.as_ref(),
                version: &self.version,
            },
            &operations,
            root_path,
        )
    }

    fn openapi_operation(
        &self,
        py: Python<'_>,
        route: &FastApiRoute,
    ) -> PyResult<OpenApiOperation> {
        let name = route
            .endpoint
            .bind(py)
            .getattr("__name__")?
            .extract::<String>()?;
        let summary = route
            .summary
            .as_ref()
            .filter(|summary| !summary.is_empty())
            .cloned()
            .unwrap_or_else(|| {
                name.split('_')
                    .filter(|part| !part.is_empty())
                    .map(title_case)
                    .collect::<Vec<_>>()
                    .join(" ")
            });
        let operation_id = route
            .operation_id
            .as_ref()
            .filter(|operation_id| !operation_id.is_empty())
            .cloned()
            .unwrap_or_else(|| operation_id(&name, &route.path_format, &route.method));
        let parameters = route
            .plan
            .openapi_parameters(py)?
            .into_iter()
            .map(|parameter| {
                let title = if parameter.location == "header" {
                    title_case(&parameter.name).replace('_', " ")
                } else {
                    title_case(&parameter.name.replace('_', " "))
                };
                let schema = pydantic_schema_with_config(
                    py,
                    parameter.annotation.bind(py),
                    "validation",
                    parameter.title.as_deref().or(Some(&title)),
                    parameter
                        .schema_config
                        .as_ref()
                        .map(|config| config.bind(py)),
                )?;
                Ok(OpenApiParameter {
                    name: parameter.name,
                    location: parameter.location,
                    required: parameter.required,
                    description: parameter.description,
                    deprecated: parameter.deprecated,
                    default: parameter.default,
                    schema,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        let validation_parameters_present = route.plan.has_openapi_parameter_inputs();
        let mut security_schemes = BTreeMap::new();
        let mut security_requirements = Vec::new();
        route.plan.collect_openapi_security(
            py,
            &mut security_schemes,
            &mut security_requirements,
            &[],
            &mut Vec::new(),
        )?;

        let has_form_body = route.plan.has_form_inputs();
        let (request_model_name, request_schema, request_required, request_media_type) =
            if has_form_body {
                let body_parameters = route.plan.all_body_parameters();
                let aggregate_body = form_body_should_embed(py, &body_parameters)?;
                if aggregate_body {
                    let aggregate_name = format!("Body_{operation_id}");
                    let aggregate_model =
                        aggregate_body_model(py, &aggregate_name, &body_parameters)?;
                    let request_schema =
                        pydantic_schema(py, aggregate_model.bind(py), "validation", None)?;
                    let request_required = body_parameters
                        .iter()
                        .any(|parameter| parameter.default.is_none());
                    let media_type = aggregate_body_media_type(&body_parameters);
                    (None, Some(request_schema), request_required, media_type)
                } else {
                    match body_parameters.first().copied() {
                        Some(parameter) => (
                            None,
                            Some(body_parameter_schema(
                                py,
                                parameter,
                                Some(&title_case(&parameter.body_alias().replace('_', " "))),
                            )?),
                            parameter.default.is_none(),
                            parameter
                                .media_type
                                .as_deref()
                                .unwrap_or("application/json")
                                .to_owned(),
                        ),
                        None => (None, None, false, "application/json".to_owned()),
                    }
                }
            } else {
                let direct_body_parameters = route.plan.all_body_parameters();
                let aggregate_body = body_fields_embedded(&direct_body_parameters);
                if aggregate_body {
                    let aggregate_name = format!("Body_{operation_id}");
                    let aggregate_model =
                        aggregate_body_model(py, &aggregate_name, &direct_body_parameters)?;
                    let request_schema =
                        pydantic_schema(py, aggregate_model.bind(py), "validation", None)?;
                    let request_required = direct_body_parameters
                        .iter()
                        .any(|parameter| parameter.default.is_none());
                    (
                        None,
                        Some(request_schema),
                        request_required,
                        aggregate_body_media_type(&direct_body_parameters),
                    )
                } else {
                    match route.plan.body_parameter() {
                        Some(parameter) => (
                            None,
                            Some(body_parameter_schema(
                                py,
                                parameter,
                                Some(&title_case(&parameter.body_alias().replace('_', " "))),
                            )?),
                            parameter.default.is_none(),
                            parameter
                                .media_type
                                .as_deref()
                                .unwrap_or("application/json")
                                .to_owned(),
                        ),
                        None => (None, None, false, "application/json".to_owned()),
                    }
                }
            };
        let (response_model_name, response_schema) = match route.response_model.as_ref() {
            Some(model) => {
                let schema = pydantic_schema(py, model.bind(py), "serialization", None)?;
                let model_name = match schema_definition_name(schema.bind(py))? {
                    Some(name) => Some(name),
                    None => {
                        if is_pydantic_model(py, model.bind(py))? {
                            model_name(py, model.bind(py))?
                        } else {
                            None
                        }
                    }
                };
                (model_name, Some(schema))
            }
            None => (None, None),
        };
        let (response_media_type, response_class_is_json) =
            if let Some(response_class) = route.response_class.as_ref() {
                let response_class = response_class.bind(py);
                let media_type = response_class.getattr("media_type")?;
                let media_type = if media_type.is_none() {
                    // Starlette-RS exposes PlainTextResponse's constructor default
                    // ("text/plain") without the class attribute that upstream
                    // Starlette exposes. FastAPI's OpenAPI builder reads the class
                    // attribute, so recover that inherited default for this class
                    // family while preserving an explicit subclass override to None.
                    let responses = py.import("starlette.responses")?;
                    let plain_text_response = responses.getattr("PlainTextResponse")?;
                    let is_plain_text_response =
                        annotation_is_subclass(py, response_class, &plain_text_response)?;
                    let defines_media_type = response_class
                        .getattr("__dict__")?
                        .call_method1("__contains__", ("media_type",))?
                        .extract::<bool>()?;
                    if is_plain_text_response && !defines_media_type {
                        Some("text/plain".to_owned())
                    } else {
                        None
                    }
                } else {
                    Some(media_type.extract::<String>()?)
                };
                let json_response = py.import("starlette.responses")?.getattr("JSONResponse")?;
                (
                    media_type,
                    annotation_is_subclass(py, response_class, &json_response)?,
                )
            } else {
                // FastAPI's implicit response class is JSONResponse.
                (Some("application/json".to_owned()), true)
            };
        let sse_stream = route.sse_stream;
        let jsonl_stream =
            route.generator_kind.is_generator() && route.response_class.is_none() && !sse_stream;
        let (stream_item_model_name, stream_item_schema) = if jsonl_stream || sse_stream {
            match route.stream_item_type.as_ref() {
                Some(stream_item_type) => {
                    let schema =
                        pydantic_schema(py, stream_item_type.bind(py), "serialization", None)?;
                    let model_name = match schema_definition_name(schema.bind(py))? {
                        Some(name) => Some(name),
                        None => {
                            if is_pydantic_model(py, stream_item_type.bind(py))? {
                                model_name(py, stream_item_type.bind(py))?
                            } else {
                                None
                            }
                        }
                    };
                    (model_name, Some(schema))
                }
                None => (None, None),
            }
        } else {
            (None, None)
        };
        let request_body_present = request_schema.is_some();

        Ok(OpenApiOperation {
            path: route.path_format.clone(),
            method: route.method.to_ascii_lowercase(),
            summary,
            response_description: route.response_description.clone(),
            additional_responses: clone_additional_responses(py, &route.additional_responses),
            operation_id,
            status: route.status_code,
            response_status_key: openapi_response_status_key(
                py,
                route.status_code,
                route
                    .response_class
                    .as_ref()
                    .map(|response_class| response_class.bind(py)),
            )?,
            parameters,
            security_schemes,
            security_requirements,
            validation_parameters_present,
            request_model_name,
            request_schema,
            request_required,
            request_body_present,
            request_body_content_before_required: has_form_body,
            request_media_type,
            response_model_name,
            response_schema,
            response_schema_title: response_field_schema_title(
                &name,
                &route.path_format,
                &route.method,
            ),
            response_media_type,
            response_class_is_json,
            jsonl_stream,
            sse_stream,
            stream_item_model_name,
            stream_item_schema,
            deprecated: route.deprecated,
            tags: route.tags.clone(),
        })
    }
}

#[pymethods]
impl PyApiRouter {
    #[new]
    #[pyo3(signature = (*, prefix = "", tags = None, dependencies = None, default_response_class = None, on_startup = None, on_shutdown = None, lifespan = None, deprecated = None, include_in_schema = true, strict_content_type = None))]
    // lint-exception: preserve the FastAPI-compatible APIRouter constructor keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible APIRouter constructor keywords"
    )]
    fn new(
        py: Python<'_>,
        prefix: &str,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        default_response_class: Option<Py<PyAny>>,
        on_startup: Option<Py<PyAny>>,
        on_shutdown: Option<Py<PyAny>>,
        lifespan: Option<Py<PyAny>>,
        deprecated: Option<bool>,
        include_in_schema: bool,
        strict_content_type: Option<bool>,
    ) -> PyResult<Self> {
        validate_router_prefix(prefix)?;
        let inner = Py::new(
            py,
            PyFastApi::new(
                py,
                "FastAPI",
                None,
                "",
                "0.1.0",
                "/openapi.json",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                default_response_class,
                true,
                None,
                None,
                on_startup,
                on_shutdown,
                lifespan,
                strict_content_type.unwrap_or(true),
            )?,
        )?;
        {
            let mut inner = inner.bind(py).borrow_mut();
            inner.route_scope_prefix = prefix.to_owned();
            inner.strict_content_type = strict_content_type;
        }
        Ok(Self {
            inner,
            prefix: prefix.to_owned(),
            tags: tags.unwrap_or_default(),
            deprecated,
            include_in_schema,
            dependencies: dependencies.unwrap_or_default(),
            strict_content_type,
        })
    }

    #[getter]
    fn prefix(&self) -> &str {
        &self.prefix
    }

    #[getter]
    fn routes(&self, py: Python<'_>) -> PyResult<Py<PyList>> {
        route_views(py, &self.inner.bind(py).borrow().routes)
    }

    #[getter]
    fn strict_content_type(&self) -> bool {
        self.strict_content_type.unwrap_or(true)
    }

    #[setter]
    fn set_strict_content_type(&mut self, py: Python<'_>, strict_content_type: bool) {
        self.strict_content_type = Some(strict_content_type);
        self.inner.bind(py).borrow_mut().strict_content_type = Some(strict_content_type);
    }

    fn add_event_handler(
        &self,
        py: Python<'_>,
        event_type: &str,
        handler: Py<PyAny>,
    ) -> PyResult<()> {
        self.inner
            .bind(py)
            .borrow()
            .lifespan
            .add_event_handler(py, event_type, handler)
    }

    fn on_event(&self, py: Python<'_>, event_type: &str) -> PyResult<Py<PyAny>> {
        warn_on_event(py, false)?;
        self.inner
            .bind(py)
            .borrow()
            .lifespan
            .decorator(py, event_type)
    }

    #[pyo3(signature = (path, *, directory, fallback=default_frontend_auto(), check_dir=default_frontend_auto()))]
    fn frontend(
        &self,
        py: Python<'_>,
        path: &str,
        directory: Py<PyAny>,
        fallback: Py<PyAny>,
        check_dir: Py<PyAny>,
    ) -> PyResult<()> {
        let mut inner = self.inner.bind(py).borrow_mut();
        add_frontend_route(&mut inner, py, path, directory, fallback, check_dir, &[])
    }

    #[pyo3(signature = (router, *, prefix = "", tags = None, dependencies = None, deprecated = None, include_in_schema = true))]
    // lint-exception: preserve FastAPI's include_router keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible include_router signature"
    )]
    fn include_router(
        &self,
        py: Python<'_>,
        router: Py<PyApiRouter>,
        prefix: &str,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        deprecated: Option<bool>,
        include_in_schema: bool,
    ) -> PyResult<()> {
        let router_object = router.clone_ref(py).into_any();
        let include_prefix = prefix.to_owned();
        let router = router.bind(py).borrow();
        if self.inner.as_ptr() == router.inner.as_ptr() {
            return Err(PyAssertionError::new_err(
                "Cannot include the same APIRouter instance into itself. Did you mean to include a different router?",
            ));
        }
        let prefix = combined_router_prefix(prefix, &router.prefix)?;
        let tags = combined_router_tags(tags.as_deref(), &router.tags);
        let mut dependencies = dependencies.unwrap_or_default();
        dependencies.extend(
            router
                .dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py)),
        );
        let deprecated = combined_deprecated(deprecated, router.deprecated);
        let include_in_schema = include_in_schema && router.include_in_schema;
        let source = router.inner.bind(py).borrow();
        let mut destination = self.inner.bind(py).borrow_mut();
        if source.lifespan.is_included_by(py, &destination.lifespan)? {
            return Err(PyAssertionError::new_err(
                "Cannot include an APIRouter instance that already includes this router. Did you mean to include a different router?",
            ));
        }
        let inherited_strict_content_type = destination.strict_content_type;
        let route_position = destination.routes.len();
        merge_router_routes(
            py,
            &mut destination,
            &source,
            RouterIncludePolicy {
                prefix: &prefix,
                tags: &tags,
                dependencies: &dependencies,
                deprecated,
                include_in_schema,
                strict_content_type: inherited_strict_content_type,
            },
        )?;
        destination.router_includes.push(FastApiRouterInclude {
            route_position,
            router: router_object,
            prefix: include_prefix,
        });
        destination.lifespan.include_router(py, &source.lifespan)
    }

    #[pyo3(
        signature = (name, /, **path_params),
        text_signature = "($self, name, /, **path_params)"
    )]
    fn url_path_for(
        &self,
        py: Python<'_>,
        name: &str,
        path_params: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let url_path = self
            .inner
            .bind(py)
            .call_method("url_path_for", (name,), path_params)?;
        prefix_url_path(py, url_path, &self.prefix)
    }

    fn __getattr__(&self, py: Python<'_>, name: &str) -> PyResult<Py<PyAny>> {
        if !matches!(
            name,
            "get"
                | "post"
                | "put"
                | "delete"
                | "patch"
                | "head"
                | "options"
                | "trace"
                | "api_route"
                | "add_api_route"
                | "websocket"
                | "websocket_route"
                | "add_websocket_route"
                | "add_api_websocket_route"
        ) {
            return Err(PyAttributeError::new_err(format!(
                "'APIRouter' object has no attribute '{name}'"
            )));
        }
        Ok(self.inner.bind(py).getattr(name)?.unbind())
    }
}

fn validate_router_prefix(prefix: &str) -> PyResult<()> {
    if prefix.is_empty() {
        return Ok(());
    }
    if !prefix.starts_with('/') {
        return Err(PyAssertionError::new_err(
            "A path prefix must start with '/'",
        ));
    }
    if prefix.ends_with('/') {
        return Err(PyAssertionError::new_err(
            "A path prefix must not end with '/', as the routes will start with '/'",
        ));
    }
    Ok(())
}

fn combined_router_prefix(include_prefix: &str, router_prefix: &str) -> PyResult<String> {
    validate_router_prefix(include_prefix)?;
    validate_router_prefix(router_prefix)?;
    Ok(format!("{include_prefix}{router_prefix}"))
}

fn try_included_router_url_path_for(
    py: Python<'_>,
    router: &Py<PyAny>,
    prefix: &str,
    name: &str,
    path_params: &Bound<'_, PyDict>,
    no_match_type: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    match router
        .bind(py)
        .call_method("url_path_for", (name,), Some(path_params))
    {
        Ok(url_path) => prefix_url_path(py, url_path, prefix).map(Some),
        Err(error) if error.is_instance(py, no_match_type) => Ok(None),
        Err(error) => Err(error),
    }
}

fn prefix_url_path(
    py: Python<'_>,
    url_path: Bound<'_, PyAny>,
    prefix: &str,
) -> PyResult<Py<PyAny>> {
    if prefix.is_empty() {
        return Ok(url_path.unbind());
    }
    let path = format!("{prefix}{}", url_path.str()?.to_str()?);
    py.import("starlette.datastructures")?
        .getattr("URLPath")?
        .call1((
            path,
            url_path.getattr("protocol")?,
            url_path.getattr("host")?,
        ))
        .map(Bound::unbind)
}

fn combined_router_tags(include_tags: Option<&[String]>, router_tags: &[String]) -> Vec<String> {
    let mut tags = include_tags.unwrap_or_default().to_vec();
    tags.extend_from_slice(router_tags);
    tags
}

fn combined_route_tags(
    inherited_tags: &[String],
    route_tags: Option<&[String]>,
) -> Option<Vec<String>> {
    if inherited_tags.is_empty() && route_tags.is_none() {
        return None;
    }
    let mut tags = inherited_tags.to_vec();
    if let Some(route_tags) = route_tags {
        tags.extend_from_slice(route_tags);
    }
    Some(tags)
}

fn combined_deprecated(inherited: Option<bool>, router: Option<bool>) -> Option<bool> {
    if inherited.unwrap_or(false) || router.unwrap_or(false) {
        Some(true)
    } else {
        None
    }
}

fn normalize_frontend_path(path: &str) -> PyResult<String> {
    if path.is_empty() {
        return Err(PyAssertionError::new_err("A frontend path cannot be empty"));
    }
    if !path.starts_with('/') {
        return Err(PyAssertionError::new_err(
            "A frontend path must start with '/'",
        ));
    }
    if path == "/" {
        return Ok(path.to_owned());
    }
    Ok(path.trim_end_matches('/').to_owned())
}

fn join_frontend_paths(prefix: &str, path: &str) -> String {
    if prefix.is_empty() {
        path.to_owned()
    } else if path == "/" {
        prefix.to_owned()
    } else {
        format!("{prefix}{path}")
    }
}

fn frontend_path_for(route_path: &str, frontend_path: &str) -> Option<String> {
    if frontend_path == "/" {
        return Some(route_path.trim_start_matches('/').to_owned());
    }
    if route_path == frontend_path {
        return Some(String::new());
    }
    route_path
        .strip_prefix(frontend_path)
        .and_then(|remainder| remainder.strip_prefix('/'))
        .map(str::to_owned)
}

fn frontend_path_specificity(path: &str) -> usize {
    if path == "/" { 0 } else { path.chars().count() }
}

fn normalize_frontend_relative_path(path: &str) -> String {
    let mut normalized = std::path::PathBuf::new();
    for component in Path::new(path).components() {
        match component {
            std::path::Component::CurDir => {}
            std::path::Component::ParentDir => {
                if !normalized.pop() {
                    normalized.push("..");
                }
            }
            std::path::Component::Normal(value) => normalized.push(value),
            std::path::Component::RootDir | std::path::Component::Prefix(_) => {
                normalized.push(component.as_os_str());
            }
        }
    }
    if normalized.as_os_str().is_empty() {
        ".".to_owned()
    } else {
        normalized.to_string_lossy().into_owned()
    }
}

fn frontend_file_is_regular(
    py: Python<'_>,
    static_files: &Bound<'_, PyAny>,
    path: &str,
) -> PyResult<bool> {
    let lookup = static_files.call_method1("lookup_path", (path,))?;
    let stat_result = lookup.get_item(1)?;
    if stat_result.is_none() {
        return Ok(false);
    }
    py.import("stat")?
        .getattr("S_ISREG")?
        .call1((stat_result.getattr("st_mode")?,))?
        .extract()
}

fn frontend_static_resource_exists(
    py: Python<'_>,
    static_files: &Bound<'_, PyAny>,
    path: &str,
) -> PyResult<bool> {
    let lookup = static_files.call_method1("lookup_path", (path,))?;
    let stat_result = lookup.get_item(1)?;
    if stat_result.is_none() {
        return Ok(false);
    }
    let mode = stat_result.getattr("st_mode")?;
    let stat_module = py.import("stat")?;
    if stat_module
        .getattr("S_ISREG")?
        .call1((&mode,))?
        .extract::<bool>()?
    {
        return Ok(true);
    }
    if !stat_module
        .getattr("S_ISDIR")?
        .call1((mode,))?
        .extract::<bool>()?
    {
        return Ok(false);
    }
    let index_path = if path == "." {
        "index.html".to_owned()
    } else {
        format!("{path}/index.html")
    };
    frontend_file_is_regular(py, static_files, &index_path)
}

fn python_path_string(py: Python<'_>, path: &Bound<'_, PyAny>) -> PyResult<String> {
    py.import("os")?
        .getattr("fsdecode")?
        .call1((py.import("os")?.getattr("fspath")?.call1((path,))?,))?
        .extract()
}

fn python_path_display(py: Python<'_>, path: &Bound<'_, PyAny>) -> PyResult<String> {
    py.import("builtins")?
        .getattr("str")?
        .call1((path,))?
        .extract()
}

fn resolved_absolute_path(py: Python<'_>, path: &str) -> PyResult<String> {
    py.import("os.path")?
        .getattr("realpath")?
        .call1((path,))?
        .extract()
}

fn parse_frontend_fallback(fallback: &Bound<'_, PyAny>) -> PyResult<FastApiFrontendFallback> {
    if fallback.is_none() {
        return Ok(FastApiFrontendFallback::None);
    }
    if fallback.eq("auto")? {
        return Ok(FastApiFrontendFallback::Auto);
    }
    if fallback.eq("index.html")? {
        return Ok(FastApiFrontendFallback::IndexHtml);
    }
    if fallback.eq("404.html")? {
        return Ok(FastApiFrontendFallback::NotFoundHtml);
    }
    Err(PyAssertionError::new_err(
        "fallback must be 'auto', 'index.html', '404.html', or None",
    ))
}

fn frontend_fallback_file_error(
    py: Python<'_>,
    fallback: &str,
    directory: &Bound<'_, PyAny>,
    directory_path: &str,
) -> PyResult<PyErr> {
    let display = python_path_display(py, directory)?;
    let resolved = resolved_absolute_path(py, directory_path)?;
    Ok(PyRuntimeError::new_err(format!(
        "Frontend fallback file '{fallback}' does not exist in directory '{display}'. Resolved absolute directory: '{resolved}'"
    )))
}

fn frontend_http_error(py: Python<'_>, status_code: u16) -> PyResult<PyErr> {
    let exception = py
        .import("starlette.exceptions")?
        .getattr("HTTPException")?
        .call1((status_code,))?;
    Ok(PyErr::from_value(exception))
}

fn frontend_is_navigation_request(py: Python<'_>, request: &Bound<'_, PyAny>) -> PyResult<bool> {
    let accept = request
        .getattr("headers")?
        .call_method1("get", ("accept", ""))?
        .extract::<String>()?;
    let email_message = py.import("email.message")?.getattr("Message")?;
    let builtins = py.import("builtins")?;
    for raw_value in accept.split(',') {
        let message = email_message.call0()?;
        message.set_item("content-type", raw_value.trim())?;
        let media_type = format!(
            "{}/{}",
            message
                .call_method0("get_content_maintype")?
                .extract::<String>()?,
            message
                .call_method0("get_content_subtype")?
                .extract::<String>()?
        );
        if !matches!(media_type.as_str(), "text/html" | "application/xhtml+xml") {
            continue;
        }
        let quality = message.call_method1("get_param", ("q",))?;
        let quality = if quality.is_none() {
            1.0
        } else {
            match builtins.getattr("float")?.call1((quality,)) {
                Ok(value) => value.extract::<f64>()?,
                Err(error) if error.is_instance_of::<PyValueError>(py) => 1.0,
                Err(error) => return Err(error),
            }
        };
        if quality != 0.0 {
            return Ok(true);
        }
    }
    Ok(false)
}

fn add_frontend_route(
    app: &mut PyFastApi,
    py: Python<'_>,
    path: &str,
    directory: Py<PyAny>,
    fallback: Py<PyAny>,
    check_dir: Py<PyAny>,
    dependencies: &[Py<PyAny>],
) -> PyResult<()> {
    let path = normalize_frontend_path(path)?;
    let fallback = parse_frontend_fallback(fallback.bind(py))?;
    let directory_path = python_path_string(py, directory.bind(py))?;
    let directory_exists = Path::new(&directory_path).is_dir();
    let is_automatic = check_dir.bind(py).eq("auto")?;
    let is_development =
        std::env::var("FASTAPI_ENV").is_ok_and(|environment| environment == "development");
    let check_now = if is_automatic {
        !is_development
    } else {
        check_dir.bind(py).is_truthy()?
    };
    let display = python_path_display(py, directory.bind(py))?;
    let resolved = resolved_absolute_path(py, &directory_path)?;
    if check_now && !directory_exists {
        return Err(PyRuntimeError::new_err(format!(
            "Frontend directory '{display}' does not exist. Resolved absolute path: '{resolved}'"
        )));
    }
    if is_automatic && is_development && !directory_exists {
        let warning = format!(
            "Frontend directory '{display}' does not exist. Resolved absolute path: '{resolved}'"
        );
        let warning_kwargs = PyDict::new(py);
        warning_kwargs.set_item("stacklevel", 3)?;
        py.import("warnings")?.call_method(
            "warn",
            (warning, py.import("builtins")?.getattr("UserWarning")?),
            Some(&warning_kwargs),
        )?;
    }

    let static_files_type = py.import("starlette.staticfiles")?.getattr("StaticFiles")?;
    let static_files_kwargs = PyDict::new(py);
    static_files_kwargs.set_item("directory", directory.bind(py))?;
    static_files_kwargs.set_item("html", true)?;
    // FastAPI has already applied its own constructor-time directory policy.
    // Starlette-RS performs the deferred configuration check on first use.
    static_files_kwargs.set_item("check_dir", false)?;
    static_files_kwargs.set_item("follow_symlink", false)?;
    let static_files = static_files_type
        .call((), Some(&static_files_kwargs))?
        .unbind();

    if check_now {
        let required_fallback = match fallback {
            FastApiFrontendFallback::IndexHtml => Some("index.html"),
            FastApiFrontendFallback::NotFoundHtml => Some("404.html"),
            FastApiFrontendFallback::Auto | FastApiFrontendFallback::None => None,
        };
        if let Some(required_fallback) = required_fallback
            && !frontend_file_is_regular(py, static_files.bind(py), required_fallback)?
        {
            return Err(frontend_fallback_file_error(
                py,
                required_fallback,
                directory.bind(py),
                &directory_path,
            )?);
        }
    }

    let endpoint = py
        .import("fastapi_rs._core")?
        .getattr("_frontend_dependency_endpoint")?
        .unbind();
    let mut dependency_plan = CallablePlan::build(py, endpoint, &[], None)?;
    dependency_plan.prepend_dependencies(py, dependencies)?;
    app.frontend_routes.push(FastApiFrontendRoute {
        path,
        static_files,
        fallback,
        dependency_plan,
    });
    app.bump_routes_version();
    Ok(())
}

fn merge_router_routes(
    py: Python<'_>,
    app: &mut PyFastApi,
    source: &PyFastApi,
    policy: RouterIncludePolicy<'_>,
) -> PyResult<()> {
    let RouterIncludePolicy {
        prefix,
        tags: inherited_tags,
        dependencies: inherited_dependencies,
        deprecated: inherited_deprecated,
        include_in_schema: inherited_include_in_schema,
        strict_content_type: inherited_strict_content_type,
    } = policy;
    for source_route in &source.routes {
        let path = format!("{prefix}{}", source_route.path);
        let mut route_dependencies = inherited_dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        route_dependencies.extend(
            source_route
                .router_dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py)),
        );
        let mut plan = CallablePlan::build(
            py,
            source_route.endpoint.clone_ref(py),
            &path_parameter_names(&path),
            None,
        )?;
        plan.prepend_dependencies(py, &route_dependencies)?;
        let param_convertors = route_param_convertors(py, &path)?;
        let response_class = source_route
            .response_class
            .as_ref()
            .map(|value| value.clone_ref(py))
            .or_else(|| {
                app.default_response_class
                    .as_ref()
                    .map(|value| value.clone_ref(py))
            });
        let route_scope = source_route.route_scope.clone_ref(py);
        let path_format = route_path_format(py, &path)?;
        let tags = combined_route_tags(inherited_tags, source_route.tags.as_deref());
        let original_route = source_route.original_route.clone_ref(py);
        let effective_route = new_api_route_view(
            py,
            &path,
            &path_format,
            &source_route.method,
            &source_route.name,
            tags.as_deref().unwrap_or_default(),
            source_route.endpoint.clone_ref(py),
        )?;
        let effective_route_context =
            new_route_context(py, original_route.clone_ref(py), effective_route)?;
        let sse_stream = source_route.generator_kind.is_generator()
            && match response_class.as_ref() {
                Some(class) => sse::is_event_source_response_class(py, class.bind(py))?,
                None => false,
            };
        let index = app
            .router
            .add_operation(&path, &source_route.method, source_route.status_code)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.named_routes
            .add_route(&path, &source_route.name)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.router
            .set_parameters(index, plan.input_parameters())
            .ok_or_else(|| PyRuntimeError::new_err("included FastAPI operation was lost"))?;
        app.routes.push(FastApiRoute {
            path,
            path_format,
            method: source_route.method.clone(),
            name: source_route.name.clone(),
            route_scope,
            param_convertors,
            summary: source_route.summary.clone(),
            response_description: source_route.response_description.clone(),
            additional_responses: clone_additional_responses(
                py,
                &source_route.additional_responses,
            ),
            operation_id: source_route.operation_id.clone(),
            deprecated: combined_deprecated(inherited_deprecated, source_route.deprecated),
            tags,
            status_code: source_route.status_code,
            include_in_schema: inherited_include_in_schema && source_route.include_in_schema,
            response_class,
            strict_content_type: source_route
                .strict_content_type
                .or(source.strict_content_type)
                .or(inherited_strict_content_type),
            sse_stream,
            generator_kind: source_route.generator_kind,
            stream_item_type: source_route
                .stream_item_type
                .as_ref()
                .map(|value| value.clone_ref(py)),
            endpoint: source_route.endpoint.clone_ref(py),
            original_route,
            public_route: effective_route_context.clone_ref(py),
            effective_route_context: Some(effective_route_context),
            response_model: source_route
                .response_model
                .as_ref()
                .map(|model| model.clone_ref(py)),
            response_model_include: source_route
                .response_model_include
                .as_ref()
                .map(|value| value.clone_ref(py)),
            response_model_exclude: source_route
                .response_model_exclude
                .as_ref()
                .map(|value| value.clone_ref(py)),
            response_model_by_alias: source_route.response_model_by_alias,
            response_model_exclude_unset: source_route.response_model_exclude_unset,
            response_model_exclude_defaults: source_route.response_model_exclude_defaults,
            response_model_exclude_none: source_route.response_model_exclude_none,
            router_dependencies: route_dependencies,
            plan,
        });
        app.bump_routes_version();
    }
    for source_route in &source.websocket_routes {
        let path = format!("{prefix}{}", source_route.path);
        if source_route.raw {
            let route_scope = websocket_route_scope(
                py,
                &path,
                source_route.endpoint.bind(py),
                Some(&source_route.name),
            )?;
            let param_convertors = route_param_convertors(py, &path)?;
            let index = app
                .websocket_router
                .add_operation(&path, "GET", Some(200))
                .map_err(|error| PyValueError::new_err(error.to_string()))?;
            app.websocket_router
                .set_parameters(index, Vec::new())
                .ok_or_else(|| PyRuntimeError::new_err("included raw WebSocket route was lost"))?;
            app.websocket_routes.push(FastApiWebSocketRoute {
                path,
                name: source_route.name.clone(),
                route_scope,
                param_convertors,
                route_dependencies: Vec::new(),
                endpoint: source_route.endpoint.clone_ref(py),
                plan: None,
                raw: true,
            });
            app.bump_routes_version();
            continue;
        }
        let mut route_dependencies = inherited_dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        route_dependencies.extend(
            source_route
                .route_dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py)),
        );
        let mut plan = CallablePlan::build(
            py,
            source_route.endpoint.clone_ref(py),
            &path_parameter_names(&path),
            None,
        )?;
        plan.prepend_dependencies(py, &route_dependencies)?;
        let param_convertors = route_param_convertors(py, &path)?;
        let route_scope = source_route.route_scope.clone_ref(py);
        let index = app
            .websocket_router
            .add_operation(&path, "GET", Some(200))
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.websocket_router
            .set_parameters(index, plan.input_parameters())
            .ok_or_else(|| PyRuntimeError::new_err("included FastAPI WebSocket route was lost"))?;
        app.websocket_routes.push(FastApiWebSocketRoute {
            path,
            name: source_route.name.clone(),
            route_scope,
            param_convertors,
            route_dependencies,
            endpoint: source_route.endpoint.clone_ref(py),
            plan: Some(plan),
            raw: false,
        });
        app.bump_routes_version();
    }
    for source_frontend in &source.frontend_routes {
        let mut dependency_plan = source_frontend.dependency_plan.clone_ref(py);
        dependency_plan.prepend_dependencies(py, inherited_dependencies)?;
        app.frontend_routes.push(FastApiFrontendRoute {
            path: join_frontend_paths(prefix, &source_frontend.path),
            static_files: source_frontend.static_files.clone_ref(py),
            fallback: source_frontend.fallback,
            dependency_plan,
        });
        app.bump_routes_version();
    }
    Ok(())
}

#[pyclass(name = "_OperationDecorator", module = "fastapi_rs._core", unsendable)]
struct PyOperationDecorator {
    app: Py<PyFastApi>,
    path: String,
    method: String,
    summary: Option<String>,
    response_description: String,
    additional_responses: Vec<OpenApiAdditionalResponse>,
    operation_id: Option<String>,
    deprecated: Option<bool>,
    tags: Option<Vec<String>>,
    dependencies: Vec<Py<PyAny>>,
    response_model: Option<Py<PyAny>>,
    status_code: Option<u16>,
    include_in_schema: bool,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    response_class: Option<Py<PyAny>>,
    name: Option<String>,
}

fn inspect_generator_kind(
    inspect: &Bound<'_, PyAny>,
    callable: &Bound<'_, PyAny>,
) -> PyResult<FastApiGeneratorKind> {
    let unwrapped = inspect.getattr("unwrap")?.call1((callable,))?;
    for candidate in [callable, &unwrapped] {
        if inspect
            .getattr("isasyncgenfunction")?
            .call1((candidate,))?
            .extract::<bool>()?
        {
            return Ok(FastApiGeneratorKind::Async);
        }
        if inspect
            .getattr("isgeneratorfunction")?
            .call1((candidate,))?
            .extract::<bool>()?
        {
            return Ok(FastApiGeneratorKind::Sync);
        }
    }

    if inspect
        .getattr("isclass")?
        .call1((&unwrapped,))?
        .extract::<bool>()?
    {
        return Ok(FastApiGeneratorKind::None);
    }

    if let Ok(dunder_call) = callable.getattr("__call__") {
        let unwrapped_dunder_call = inspect.getattr("unwrap")?.call1((&dunder_call,))?;
        for candidate in [&dunder_call, &unwrapped_dunder_call] {
            if inspect
                .getattr("isasyncgenfunction")?
                .call1((candidate,))?
                .extract::<bool>()?
            {
                return Ok(FastApiGeneratorKind::Async);
            }
            if inspect
                .getattr("isgeneratorfunction")?
                .call1((candidate,))?
                .extract::<bool>()?
            {
                return Ok(FastApiGeneratorKind::Sync);
            }
        }
    }

    Ok(FastApiGeneratorKind::None)
}

fn generator_kind(py: Python<'_>, callable: &Bound<'_, PyAny>) -> PyResult<FastApiGeneratorKind> {
    let inspect = py.import("inspect")?;
    let kind = inspect_generator_kind(&inspect, callable)?;
    if kind.is_generator() {
        return Ok(kind);
    }
    let unwrapped = inspect.getattr("unwrap")?.call1((callable,))?;
    if inspect
        .getattr("isclass")?
        .call1((&unwrapped,))?
        .extract::<bool>()?
    {
        return Ok(FastApiGeneratorKind::None);
    }
    match callable.getattr("__call__") {
        Ok(dunder_call) => inspect_generator_kind(&inspect, &dunder_call),
        Err(error) if error.is_instance_of::<PyAttributeError>(py) => {
            Ok(FastApiGeneratorKind::None)
        }
        Err(error) => Err(error),
    }
}

fn stream_item_type(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<Option<Py<PyAny>>> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    if origin.is_none() {
        return Ok(None);
    }
    let collections_abc = py.import("collections.abc")?;
    let is_stream_origin = [
        "AsyncIterable",
        "AsyncIterator",
        "AsyncGenerator",
        "Iterable",
        "Iterator",
        "Generator",
    ]
    .into_iter()
    .try_fold(false, |matches, name| {
        Ok::<_, PyErr>(matches || origin.is(&collections_abc.getattr(name)?))
    })?;
    if !is_stream_origin {
        return Ok(None);
    }
    let arguments = typing
        .getattr("get_args")?
        .call1((annotation,))?
        .cast_into::<PyTuple>()?;
    if arguments.is_empty() {
        Ok(Some(typing.getattr("Any")?.unbind()))
    } else {
        Ok(Some(arguments.get_item(0)?.unbind()))
    }
}

fn additional_response_descriptions(
    py: Python<'_>,
    responses: Option<&Py<PyAny>>,
) -> PyResult<Vec<OpenApiAdditionalResponse>> {
    let Some(responses) = responses else {
        return Ok(Vec::new());
    };
    let responses = responses.bind(py).cast::<PyDict>()?;
    let mut additional_responses = Vec::with_capacity(responses.len());
    for (status, response) in responses.iter() {
        if !status.is_instance_of::<PyInt>() || status.is_instance_of::<PyBool>() {
            return Err(PyNotImplementedError::new_err(
                "route-level responses currently support integer status keys only",
            ));
        }
        let status = status.str()?.to_str()?.to_owned();
        let response = response.cast::<PyDict>()?;
        for (key, _) in response.iter() {
            let key = key.extract::<String>()?;
            if !matches!(key.as_str(), "description" | "model") {
                return Err(PyNotImplementedError::new_err(
                    "route-level responses currently support description and model entries only",
                ));
            }
        }
        if response.len() > 2 {
            return Err(PyNotImplementedError::new_err(
                "route-level responses currently support description and model entries only",
            ));
        }
        let description = response
            .get_item("description")?
            .ok_or_else(|| {
                PyNotImplementedError::new_err(
                    "route-level responses require an explicit description",
                )
            })?
            .extract::<String>()?;
        if description.is_empty() {
            return Err(PyNotImplementedError::new_err(
                "route-level response descriptions must be non-empty",
            ));
        }
        let (response_model_name, response_schema) = match response.get_item("model")? {
            Some(response_model) if !response_model.is_none() => {
                let schema = pydantic_schema(py, &response_model, "serialization", None)?;
                let model_name = match schema_definition_name(schema.bind(py))? {
                    Some(name) => Some(name),
                    None if is_pydantic_model(py, &response_model)? => {
                        model_name(py, &response_model)?
                    }
                    None => None,
                };
                (model_name, Some(schema))
            }
            _ => (None, None),
        };
        additional_responses.push(OpenApiAdditionalResponse {
            status,
            description,
            response_model_name,
            response_schema,
        });
    }
    Ok(additional_responses)
}

fn clone_additional_responses(
    py: Python<'_>,
    responses: &[OpenApiAdditionalResponse],
) -> Vec<OpenApiAdditionalResponse> {
    responses
        .iter()
        .map(|response| OpenApiAdditionalResponse {
            status: response.status.clone(),
            description: response.description.clone(),
            response_model_name: response.response_model_name.clone(),
            response_schema: response
                .response_schema
                .as_ref()
                .map(|schema| schema.clone_ref(py)),
        })
        .collect()
}

fn operation_decorator(
    app: Py<PyFastApi>,
    py: Python<'_>,
    path: &str,
    method: &str,
    response_model: Option<Py<PyAny>>,
    status_code: Option<u16>,
    response_model_options: ResponseModelOptions,
) -> PyResult<Py<PyOperationDecorator>> {
    let additional_responses =
        additional_response_descriptions(py, response_model_options.responses.as_ref())?;
    Py::new(
        py,
        PyOperationDecorator {
            app,
            path: path.to_owned(),
            method: method.to_owned(),
            summary: response_model_options.summary,
            response_description: response_model_options
                .response_description
                .unwrap_or_else(|| DEFAULT_RESPONSE_DESCRIPTION.to_owned()),
            additional_responses,
            operation_id: response_model_options.operation_id,
            deprecated: response_model_options.deprecated,
            tags: response_model_options.tags,
            dependencies: response_model_options.dependencies,
            response_model,
            status_code,
            include_in_schema: response_model_options.include_in_schema,
            response_model_include: response_model_options.include,
            response_model_exclude: response_model_options.exclude,
            response_model_by_alias: response_model_options.by_alias,
            response_model_exclude_unset: response_model_options.exclude_unset,
            response_model_exclude_defaults: response_model_options.exclude_defaults,
            response_model_exclude_none: response_model_options.exclude_none,
            response_class: response_model_options.response_class,
            name: response_model_options.name,
        },
    )
}

#[pymethods]
impl PyOperationDecorator {
    fn __call__(&self, py: Python<'_>, endpoint: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let path_parameters = path_parameter_names(&self.path);
        let app_dependencies = self
            .app
            .bind(py)
            .borrow()
            .dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        let mut route_dependencies = app_dependencies;
        route_dependencies.extend(
            self.dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py)),
        );
        let mut plan = CallablePlan::build(py, endpoint.clone_ref(py), &path_parameters, None)?;
        plan.prepend_dependencies(py, &route_dependencies)?;
        let generator_kind = generator_kind(py, endpoint.bind(py))?;
        let (inferred_name, param_convertors) =
            route_reverse_metadata(py, &self.path, endpoint.bind(py))?;
        let name = self.name.clone().unwrap_or(inferred_name);
        let scope_path = {
            let app = self.app.bind(py).borrow();
            format!("{}{}", app.route_scope_prefix, self.path)
        };
        let (route_scope, path_format) =
            http_route_scope(py, &scope_path, endpoint.bind(py), &self.method, &name)?;
        let public_route = new_api_route_view(
            py,
            &scope_path,
            &path_format,
            &self.method,
            &name,
            self.tags.as_deref().unwrap_or_default(),
            endpoint.clone_ref(py),
        )?;
        let inferred_stream_item_type = match (
            generator_kind.is_generator(),
            plan.return_annotation.as_ref(),
        ) {
            (true, Some(annotation)) => stream_item_type(py, annotation.bind(py))?,
            _ => None,
        };
        let default_response_class = self
            .app
            .bind(py)
            .borrow()
            .default_response_class
            .as_ref()
            .map(|value| value.clone_ref(py));
        let response_class = self
            .response_class
            .as_ref()
            .map(|value| value.clone_ref(py))
            .or(default_response_class);
        let sse_stream = generator_kind.is_generator()
            && match response_class.as_ref() {
                Some(class) => sse::is_event_source_response_class(py, class.bind(py))?,
                None => false,
            };
        let stream_item_type = if self.response_class.is_none() || sse_stream {
            match inferred_stream_item_type.as_ref() {
                Some(item_type)
                    if sse_stream && sse::is_server_sent_event_class(py, item_type.bind(py))? =>
                {
                    None
                }
                Some(item_type) => Some(item_type.clone_ref(py)),
                None => None,
            }
        } else {
            None
        };
        let default_response_model = py.NotImplemented();
        let response_model = match self.response_model.as_ref() {
            Some(response_model) if response_model.bind(py).is(default_response_model.bind(py)) => {
                match plan.return_annotation.as_ref() {
                    Some(annotation) if is_response_annotation(py, annotation.bind(py))? => None,
                    Some(_) if inferred_stream_item_type.is_some() => None,
                    Some(annotation) => Some(annotation.clone_ref(py)),
                    None => None,
                }
            }
            Some(response_model) => Some(response_model.clone_ref(py)),
            None => None,
        };
        let inputs = plan.input_parameters();
        let mut app = self.app.bind(py).borrow_mut();
        let index = app
            .router
            .add_operation(&self.path, &self.method, self.status_code)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.named_routes
            .add_route(&self.path, &name)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.router
            .set_parameters(index, inputs)
            .ok_or_else(|| PyRuntimeError::new_err("registered FastAPI operation was lost"))?;
        let strict_content_type = app.strict_content_type;
        app.routes.push(FastApiRoute {
            path: self.path.clone(),
            path_format,
            method: self.method.clone(),
            name,
            route_scope,
            param_convertors,
            summary: self.summary.clone(),
            response_description: self.response_description.clone(),
            additional_responses: clone_additional_responses(py, &self.additional_responses),
            operation_id: self.operation_id.clone(),
            deprecated: self.deprecated,
            tags: self.tags.clone(),
            status_code: self.status_code,
            include_in_schema: self.include_in_schema,
            response_class,
            strict_content_type,
            sse_stream,
            generator_kind,
            stream_item_type,
            endpoint: endpoint.clone_ref(py),
            original_route: public_route.clone_ref(py),
            public_route,
            effective_route_context: None,
            response_model,
            response_model_include: self
                .response_model_include
                .as_ref()
                .map(|value| value.clone_ref(py)),
            response_model_exclude: self
                .response_model_exclude
                .as_ref()
                .map(|value| value.clone_ref(py)),
            response_model_by_alias: self.response_model_by_alias,
            response_model_exclude_unset: self.response_model_exclude_unset,
            response_model_exclude_defaults: self.response_model_exclude_defaults,
            response_model_exclude_none: self.response_model_exclude_none,
            router_dependencies: route_dependencies,
            plan,
        });
        app.bump_routes_version();
        Ok(endpoint)
    }
}

#[pymethods]
impl PyWebSocketDecorator {
    fn __call__(&self, py: Python<'_>, endpoint: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let path_parameters = path_parameter_names(&self.path);
        let mut route_dependencies = self
            .app
            .bind(py)
            .borrow()
            .dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        route_dependencies.extend(
            self.dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py)),
        );
        let mut plan = CallablePlan::build(py, endpoint.clone_ref(py), &path_parameters, None)?;
        plan.prepend_dependencies(py, &route_dependencies)?;
        let param_convertors = route_param_convertors(py, &self.path)?;
        let inputs = plan.input_parameters();
        let scope_path = {
            let app = self.app.bind(py).borrow();
            format!("{}{}", app.route_scope_prefix, self.path)
        };
        let route_scope =
            websocket_route_scope(py, &scope_path, endpoint.bind(py), self.name.as_deref())?;
        let name = route_scope.bind(py).getattr("name")?.extract::<String>()?;
        let mut app = self.app.bind(py).borrow_mut();
        let index = app
            .websocket_router
            .add_operation(&self.path, "GET", Some(200))
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.websocket_router
            .set_parameters(index, inputs)
            .ok_or_else(|| {
                PyRuntimeError::new_err("registered FastAPI WebSocket route was lost")
            })?;
        app.websocket_routes.push(FastApiWebSocketRoute {
            path: self.path.clone(),
            name,
            route_scope,
            param_convertors,
            route_dependencies,
            endpoint: endpoint.clone_ref(py),
            plan: Some(plan),
            raw: false,
        });
        app.bump_routes_version();
        Ok(endpoint)
    }
}

#[pymethods]
impl PyRawWebSocketDecorator {
    fn __call__(&self, py: Python<'_>, endpoint: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let mut app = self.app.bind(py).borrow_mut();
        add_raw_websocket_route(
            &mut app,
            py,
            &self.path,
            endpoint.bind(py),
            self.name.as_deref(),
        )?;
        Ok(endpoint)
    }
}

impl CallablePlan {
    fn has_only_synchronous_dependencies(
        &self,
        context: &InvocationContext<'_, '_>,
    ) -> PyResult<bool> {
        for parameter in &self.parameters {
            let ParameterSource::Dependency { plan, .. } = &parameter.source else {
                continue;
            };
            let original_callable = plan.callable.bind(context.py);
            let replacement = context.dependency_overrides.get_item(original_callable)?;
            let callable = match replacement {
                Some(replacement) if !replacement.is(original_callable) => replacement.unbind(),
                _ => plan.callable.clone_ref(context.py),
            };
            if dependency_override_callable(context.py, callable.bind(context.py))?
                != DependencyOverrideCallable::Sync
                || dependency_callable_is_generator(context.py, callable.bind(context.py))?
            {
                return Ok(false);
            }
            let dependency_plan = CallablePlan::build(
                context.py,
                callable,
                &plan.path_parameters,
                plan.computed_scope.clone(),
            )?;
            if !dependency_plan.has_only_synchronous_dependencies(context)? {
                return Ok(false);
            }
        }
        Ok(true)
    }

    fn build(
        py: Python<'_>,
        callable: Py<PyAny>,
        path_parameters: &[String],
        declared_scope: Option<String>,
    ) -> PyResult<Self> {
        let computed_scope = match declared_scope.as_deref() {
            Some(scope) if !scope.is_empty() => Some(scope.to_owned()),
            _ if dependency_callable_is_generator(py, callable.bind(py))? => {
                Some("request".to_owned())
            }
            _ => None,
        };
        let inspect = py.import("inspect")?;
        let typing = py.import("typing")?;
        let signature = inspect.getattr("signature")?.call1((callable.bind(py),))?;
        let hints_kwargs = PyDict::new(py);
        hints_kwargs.set_item("include_extras", true)?;
        let get_type_hints = typing.getattr("get_type_hints")?;
        let hints = match get_type_hints.call((callable.bind(py),), Some(&hints_kwargs)) {
            Ok(hints) => hints,
            Err(error) if error.is_instance_of::<PyTypeError>(py) => {
                let call_method = callable.bind(py).getattr("__call__")?;
                get_type_hints.call((call_method,), Some(&hints_kwargs))?
            }
            Err(error) => return Err(error),
        };
        let empty = inspect.getattr("_empty")?;
        let raw_return_annotation = signature.getattr("return_annotation")?;
        let return_annotation =
            typed_return_annotation(py, callable.bind(py), &raw_return_annotation, &empty)?;
        let parameters = signature
            .getattr("parameters")?
            .call_method0("values")?
            .try_iter()?
            .map(|item| {
                let item = item?;
                let name = item.getattr("name")?.extract::<String>()?;
                let raw_annotation = item.getattr("annotation")?;
                let annotation = if raw_annotation.is(&empty) {
                    typing.getattr("Any")?.unbind()
                } else {
                    hints
                        .call_method1("get", (&name, &raw_annotation))?
                        .unbind()
                };
                let raw_default = item.getattr("default")?;
                let (annotation, mut metadata) = annotation_parts(py, annotation)?;
                let raw_default_marker_kind =
                    if !raw_default.is(&empty) && raw_default.hasattr("kind")? {
                        Some(raw_default.getattr("kind")?.extract::<String>()?)
                    } else {
                        None
                    };
                let default_is_parameter_marker = matches!(
                    raw_default_marker_kind.as_deref(),
                    Some("body" | "depends" | "query" | "header" | "cookie" | "form" | "file")
                );
                if default_is_parameter_marker {
                    metadata.push(raw_default.clone().unbind());
                }
                let default = if raw_default.is(&empty) || default_is_parameter_marker {
                    marker_default(py, &metadata)?
                } else {
                    Some(raw_default.unbind())
                };
                let validated_annotation = constrained_parameter_annotation(
                    py,
                    annotation.bind(py),
                    &metadata,
                    default.as_ref().map(|value| value.bind(py)),
                )?;
                let is_sequence = field_annotation_is_sequence(py, validated_annotation.bind(py))?;
                let source =
                    parameter_source(py, &name, annotation.bind(py), &metadata, path_parameters)?;
                let (parameter_model_fields, parameter_model_config, model_convert_underscores) =
                    match &source {
                        ParameterSource::Input {
                            source:
                                model_source @ (InputSource::Query
                                | InputSource::Header
                                | InputSource::Cookie),
                            ..
                        } if is_pydantic_model(py, annotation.bind(py))? => {
                            let model_fields = parameter_model_fields(py, annotation.bind(py))?;
                            let model_config =
                                annotation.bind(py).getattr("model_config")?.unbind();
                            let convert_underscores = if *model_source == InputSource::Header {
                                Some(header_model_convert_underscores(py, &metadata)?)
                            } else {
                                None
                            };
                            (Some(model_fields), Some(model_config), convert_underscores)
                        }
                        _ => (None, None, None),
                    };
                Ok(CallableParameter {
                    name,
                    annotation: validated_annotation,
                    default,
                    is_sequence,
                    parameter_model_fields,
                    parameter_model_config,
                    model_convert_underscores,
                    media_type: parameter_media_type(py, &source, &metadata)?,
                    title: parameter_title(py, &source, &metadata)?,
                    description: parameter_description(py, &source, &metadata)?,
                    deprecated: parameter_deprecated(py, &source, &metadata)?,
                    include_in_schema: parameter_include_in_schema(py, &source, &metadata)?,
                    body_embed: parameter_body_embed(py, &source, &metadata)?,
                    source,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        if dependency_callable_is_generator(py, callable.bind(py))?
            && computed_scope.as_deref() == Some("request")
        {
            for parameter in &parameters {
                let ParameterSource::Dependency {
                    scope: Some(child_scope),
                    ..
                } = &parameter.source
                else {
                    continue;
                };
                if child_scope == "function" {
                    let callable_name = py
                        .import("builtins")?
                        .getattr("getattr")?
                        .call1((callable.bind(py), "__name__", "<unnamed_callable>"))?
                        .str()?
                        .to_string_lossy()
                        .into_owned();
                    return Err(crate::errors::dependency_scope_error(&format!(
                        "The dependency \"{callable_name}\" has a scope of \"request\", it cannot depend on dependencies with scope \"function\"."
                    )));
                }
            }
        }
        Ok(Self {
            callable,
            parameters,
            path_parameters: path_parameters.to_vec(),
            return_annotation,
            computed_scope,
        })
    }

    fn prepend_dependencies(&mut self, py: Python<'_>, dependencies: &[Py<PyAny>]) -> PyResult<()> {
        let mut parameters = Vec::with_capacity(dependencies.len() + self.parameters.len());
        for dependency in dependencies {
            let annotation = py.None();
            let source = parameter_source(
                py,
                "",
                annotation.bind(py),
                std::slice::from_ref(dependency),
                &self.path_parameters,
            )?;
            let ParameterSource::Dependency {
                plan,
                use_cache,
                scope,
                security_scopes,
                ..
            } = source
            else {
                return Err(PyValueError::new_err(
                    "router dependencies must be Depends declarations",
                ));
            };
            parameters.push(CallableParameter {
                name: String::new(),
                annotation,
                default: None,
                is_sequence: false,
                parameter_model_fields: None,
                parameter_model_config: None,
                model_convert_underscores: None,
                media_type: None,
                title: None,
                description: None,
                deprecated: false,
                include_in_schema: true,
                body_embed: false,
                source: ParameterSource::Dependency {
                    plan,
                    use_cache,
                    scope,
                    security_scopes,
                    bind_value: false,
                },
            });
        }
        parameters.append(&mut self.parameters);
        self.parameters = parameters;
        Ok(())
    }

    fn input_parameters(&self) -> Vec<FastApiInputParameter> {
        self.parameters
            .iter()
            .flat_map(CallableParameter::input_parameters)
            .collect()
    }

    fn single_model_parameter_index(&self, source: InputSource) -> Option<usize> {
        let mut model_parameter_index = None;
        for (index, parameter) in self.parameters.iter().enumerate() {
            if !matches!(
                &parameter.source,
                ParameterSource::Input {
                    source: parameter_source,
                    ..
                } if *parameter_source == source
            ) {
                continue;
            }
            if model_parameter_index.replace(index).is_some() {
                return None;
            }
        }
        model_parameter_index
            .filter(|index| self.parameters[*index].parameter_model_fields.is_some())
    }

    fn parameter_count(&self, source: InputSource) -> usize {
        self.parameter_count_with_visited(source, &mut Vec::new())
    }

    fn parameter_count_with_visited(
        &self,
        source: InputSource,
        visited: &mut Vec<DependencyCacheKey>,
    ) -> usize {
        let mut count = self
            .parameters
            .iter()
            .filter(|parameter| {
                matches!(
                    &parameter.source,
                    ParameterSource::Input {
                        source: parameter_source,
                        ..
                    } if *parameter_source == source
                )
            })
            .count();
        for parameter in &self.parameters {
            let ParameterSource::Dependency { plan, .. } = &parameter.source else {
                continue;
            };
            let key = (plan.callable.as_ptr() as usize, plan.computed_scope.clone());
            if visited.contains(&key) {
                continue;
            }
            visited.push(key);
            count += plan.parameter_count_with_visited(source, visited);
        }
        count
    }

    fn body_parameter(&self) -> Option<&CallableParameter> {
        self.parameters
            .iter()
            .find_map(|parameter| match parameter.source {
                ParameterSource::Input {
                    source: InputSource::Body,
                    ..
                } => Some(parameter),
                ParameterSource::Dependency { ref plan, .. } => plan.body_parameter(),
                _ => None,
            })
    }

    fn all_body_parameters(&self) -> Vec<&CallableParameter> {
        let mut parameters = Vec::new();
        self.collect_body_parameters(&mut parameters);
        parameters
    }

    fn has_openapi_parameter_inputs(&self) -> bool {
        self.parameters
            .iter()
            .any(|parameter| match &parameter.source {
                ParameterSource::Input { source, .. } => !matches!(
                    source,
                    InputSource::Body | InputSource::Form | InputSource::File
                ),
                ParameterSource::WebSocket => false,
                ParameterSource::Request => false,
                ParameterSource::HttpConnection => false,
                ParameterSource::Response => false,
                ParameterSource::BackgroundTasks => false,
                ParameterSource::Dependency { plan, .. } => plan.has_openapi_parameter_inputs(),
            })
    }

    fn collect_body_parameters<'a>(&'a self, parameters: &mut Vec<&'a CallableParameter>) {
        for parameter in &self.parameters {
            match &parameter.source {
                ParameterSource::Input {
                    source: InputSource::Body | InputSource::Form | InputSource::File,
                    ..
                } => parameters.push(parameter),
                ParameterSource::Input { .. }
                | ParameterSource::WebSocket
                | ParameterSource::Request
                | ParameterSource::HttpConnection
                | ParameterSource::Response
                | ParameterSource::BackgroundTasks
                | ParameterSource::Dependency { .. } => {}
            }
        }
        // FastAPI flattens a dependant's body fields before visiting its child
        // dependants, retaining dependency declaration order.
        for parameter in &self.parameters {
            if let ParameterSource::Dependency { plan, .. } = &parameter.source {
                plan.collect_body_parameters(parameters);
            }
        }
    }

    fn has_form_inputs(&self) -> bool {
        self.parameters
            .iter()
            .any(|parameter| match &parameter.source {
                ParameterSource::Input {
                    source: InputSource::Form | InputSource::File,
                    ..
                } => true,
                ParameterSource::Input { .. } => false,
                ParameterSource::WebSocket => false,
                ParameterSource::Request => false,
                ParameterSource::HttpConnection => false,
                ParameterSource::Response => false,
                ParameterSource::BackgroundTasks => false,
                ParameterSource::Dependency { plan, .. } => plan.has_form_inputs(),
            })
    }

    fn populate_form_inputs(
        &self,
        py: Python<'_>,
        form: &Bound<'_, PyAny>,
        inputs: &Bound<'_, PyDict>,
        form_body_embedded: bool,
        file_reads: &mut VecDeque<FormFileReadPlan>,
    ) -> PyResult<()> {
        for parameter in &self.parameters {
            if matches!(
                parameter.source,
                ParameterSource::Input {
                    source: InputSource::Form | InputSource::File,
                    ..
                }
            ) {
                parameter.populate_form_value(py, form, inputs, form_body_embedded, file_reads)?;
            }
        }
        for parameter in &self.parameters {
            if let ParameterSource::Dependency { plan, .. } = &parameter.source {
                plan.populate_form_inputs(py, form, inputs, form_body_embedded, file_reads)?;
            }
        }
        Ok(())
    }

    fn collect_openapi_security(
        &self,
        py: Python<'_>,
        security_schemes: &mut BTreeMap<String, Py<PyAny>>,
        security_requirements: &mut Vec<(String, Vec<String>)>,
        inherited_scopes: &[String],
        visited: &mut Vec<OpenApiSecurityVisitKey>,
    ) -> PyResult<()> {
        for parameter in &self.parameters {
            let ParameterSource::Dependency {
                plan,
                security_scopes,
                ..
            } = &parameter.source
            else {
                continue;
            };

            let mut effective_scopes = inherited_scopes.to_vec();
            for scope in security_scopes {
                if !effective_scopes.contains(scope) {
                    effective_scopes.push(scope.clone());
                }
            }
            let cache_key = (
                plan.callable.as_ptr() as usize,
                plan.computed_scope.clone(),
                effective_scopes.clone(),
            );
            if visited.contains(&cache_key) {
                continue;
            }
            visited.push(cache_key);

            let callable = plan.callable.bind(py);
            if let Some((scheme_name, model)) =
                crate::security::openapi_security_metadata(callable)?
            {
                security_schemes.insert(scheme_name.clone(), model);
                if let Some((_, required_scopes)) = security_requirements
                    .iter_mut()
                    .find(|(name, _)| name == &scheme_name)
                {
                    for scope in &effective_scopes {
                        if !required_scopes.contains(scope) {
                            required_scopes.push(scope.clone());
                        }
                    }
                } else {
                    security_requirements.push((scheme_name, effective_scopes.clone()));
                }
            }
            plan.collect_openapi_security(
                py,
                security_schemes,
                security_requirements,
                &effective_scopes,
                visited,
            )?;
        }
        Ok(())
    }

    fn openapi_parameters(&self, py: Python<'_>) -> PyResult<Vec<ParameterOpenApiPlan>> {
        let flatten_model_sources = [InputSource::Query, InputSource::Header, InputSource::Cookie]
            .into_iter()
            .filter(|source| self.parameter_count(*source) == 1)
            .collect::<Vec<_>>();
        self.openapi_parameters_with_model_fields(py, &flatten_model_sources)
    }

    fn openapi_parameters_with_model_fields(
        &self,
        py: Python<'_>,
        flatten_model_sources: &[InputSource],
    ) -> PyResult<Vec<ParameterOpenApiPlan>> {
        let mut parameters = Vec::new();
        for parameter in &self.parameters {
            match &parameter.source {
                ParameterSource::Input { source, alias }
                    if !matches!(
                        source,
                        InputSource::Body | InputSource::Form | InputSource::File
                    ) =>
                {
                    if flatten_model_sources.contains(source)
                        && parameter.parameter_model_fields.is_some()
                    {
                        if let Some(fields) = parameter.parameter_model_fields.as_ref() {
                            for field in fields {
                                if let Some(field_plan) = parameter_model_field_openapi_plan(
                                    py,
                                    field,
                                    *source,
                                    parameter.parameter_model_config.as_ref(),
                                    parameter.model_convert_underscores,
                                )? {
                                    parameters.push(field_plan);
                                }
                            }
                            continue;
                        }
                    }
                    if parameter.include_in_schema {
                        parameters.push(ParameterOpenApiPlan {
                            name: alias.clone(),
                            location: source.as_str().to_owned(),
                            required: parameter.default.is_none(),
                            annotation: parameter.annotation.clone_ref(py),
                            schema_config: None,
                            default: parameter
                                .default
                                .as_ref()
                                .filter(|value| !value.bind(py).is_none())
                                .map(|value| value.clone_ref(py)),
                            title: parameter.title.clone(),
                            description: parameter.description.clone(),
                            deprecated: parameter.deprecated,
                        });
                    }
                }
                ParameterSource::Dependency { plan, .. } => {
                    parameters.extend(
                        plan.openapi_parameters_with_model_fields(py, flatten_model_sources)?,
                    );
                }
                ParameterSource::Input { .. }
                | ParameterSource::WebSocket
                | ParameterSource::Request
                | ParameterSource::HttpConnection
                | ParameterSource::Response
                | ParameterSource::BackgroundTasks => {}
            }
        }
        parameters.sort_by_key(|parameter| match parameter.location.as_str() {
            "path" => 0,
            "query" => 1,
            "header" => 2,
            "cookie" => 3,
            _ => 4,
        });
        Ok(parameters)
    }

    fn prepare_direct_dependency_overrides(
        &self,
        context: &mut InvocationContext<'_, '_>,
    ) -> PyResult<OverridePreparation> {
        let mut has_direct_dependency = false;
        let mut has_async_dependency = false;
        let mut direct_dependencies = Vec::new();
        let mut dependency_edge_index = 0;

        for parameter in &self.parameters {
            let ParameterSource::Dependency {
                plan,
                use_cache,
                scope,
                ..
            } = &parameter.source
            else {
                continue;
            };
            let edge_index = dependency_edge_index;
            dependency_edge_index += 1;
            has_direct_dependency = true;

            let cache_key = (plan.callable.as_ptr() as usize, plan.computed_scope.clone());
            let original_callable = plan.callable.bind(context.py);
            let replacement = context.dependency_overrides.get_item(original_callable)?;
            let (callable, callable_kind) = match replacement {
                Some(replacement) if !replacement.is(original_callable) => {
                    let callable_kind = dependency_override_callable(context.py, &replacement)?;
                    match callable_kind {
                        DependencyOverrideCallable::AsyncCallableInstance => {
                            return Err(PyNotImplementedError::new_err(
                                "async callable-instance dependency overrides are not supported",
                            ));
                        }
                        DependencyOverrideCallable::CoroutineFunction => {
                            has_async_dependency = true;
                        }
                        DependencyOverrideCallable::Sync => {}
                    }
                    (replacement.unbind(), callable_kind)
                }
                _ => {
                    let callable = plan.callable.clone_ref(context.py);
                    let callable_kind =
                        dependency_override_callable(context.py, callable.bind(context.py))?;
                    has_async_dependency |=
                        callable_kind == DependencyOverrideCallable::CoroutineFunction;
                    (callable, callable_kind)
                }
            };
            let generator_kind =
                dependency_callable_generator_kind(context.py, callable.bind(context.py))?;
            has_async_dependency |= generator_kind.is_some();
            direct_dependencies.push((
                edge_index,
                cache_key,
                *use_cache,
                scope.clone(),
                callable,
                callable_kind,
                generator_kind,
                plan.path_parameters.clone(),
            ));
        }

        if !has_async_dependency {
            return Ok(OverridePreparation::Ready);
        }

        if !has_direct_dependency
            || matches!(
                dependency_override_callable(context.py, self.callable.bind(context.py))?,
                DependencyOverrideCallable::AsyncCallableInstance
            )
        {
            return Err(PyNotImplementedError::new_err(
                "async dependencies require flat direct dependencies; async callable-instance endpoints are not supported",
            ));
        }

        let mut dependency_graph = DependencyExecutionGraph::build(self, context)?;
        if dependency_graph.has_nested_generator() {
            return match dependency_graph.advance(context)? {
                DependencyGraphAdvance::Ready => Ok(OverridePreparation::Ready),
                DependencyGraphAdvance::Invalid => Ok(OverridePreparation::Invalid),
                DependencyGraphAdvance::Await(awaitable) => {
                    Ok(OverridePreparation::AwaitDependencyGraph {
                        awaitable,
                        graph: Box::new(dependency_graph),
                    })
                }
            };
        }

        // Validate every effective edge before invoking any dependency. The
        // scheduler below then preserves declaration order across synchronous
        // and coroutine callables without passing coroutine objects to the
        // endpoint or performing work before an unsupported graph is rejected.
        let direct_dependency_count = direct_dependencies.len();
        let mut dependency_plans = Vec::with_capacity(direct_dependencies.len());
        let mut nested_override = None;
        for (
            edge_index,
            cache_key,
            use_cache,
            scope,
            callable,
            callable_kind,
            generator_kind,
            path_parameters,
        ) in direct_dependencies
        {
            if callable_kind == DependencyOverrideCallable::AsyncCallableInstance {
                return Err(PyNotImplementedError::new_err(
                    "async dependency graphs do not support callable-instance dependencies",
                ));
            }
            let mut dependency_plan = CallablePlan::build(
                context.py,
                callable.clone_ref(context.py),
                &path_parameters,
                scope.clone(),
            )?;
            let nested_dependencies = dependency_plan
                .parameters
                .iter()
                .filter_map(|parameter| match &parameter.source {
                    ParameterSource::Dependency { plan, .. } => Some(plan.as_ref()),
                    ParameterSource::Input { .. }
                    | ParameterSource::WebSocket
                    | ParameterSource::Request
                    | ParameterSource::HttpConnection
                    | ParameterSource::Response
                    | ParameterSource::BackgroundTasks => None,
                })
                .collect::<Vec<_>>();
            if let Some(generator_kind) = generator_kind {
                if !nested_dependencies.is_empty()
                    && !dependency_plan.has_only_synchronous_dependencies(context)?
                {
                    return Err(PyNotImplementedError::new_err(
                        "yield dependencies with nested dependencies require a synchronous child graph",
                    ));
                }
                let contextlib = context.py.import("contextlib")?;
                let decorator = contextlib.getattr(match generator_kind {
                    DependencyGeneratorKind::Sync => "contextmanager",
                    DependencyGeneratorKind::Async => "asynccontextmanager",
                })?;
                dependency_plan.callable = decorator.call1((callable.bind(context.py),))?.unbind();
                dependency_plans.push((
                    edge_index,
                    cache_key,
                    use_cache,
                    callable_kind,
                    Some(generator_kind),
                    dependency_plan,
                ));
                continue;
            }
            if nested_dependencies.is_empty() {
                dependency_plans.push((
                    edge_index,
                    cache_key,
                    use_cache,
                    callable_kind,
                    None,
                    dependency_plan,
                ));
                continue;
            }

            if callable_kind == DependencyOverrideCallable::Sync
                && dependency_plan.has_only_synchronous_dependencies(context)?
            {
                dependency_plans.push((
                    edge_index,
                    cache_key,
                    use_cache,
                    callable_kind,
                    None,
                    dependency_plan,
                ));
                continue;
            }

            if direct_dependency_count != 1
                || nested_override.is_some()
                || nested_dependencies.len() != 1
                || callable_kind != DependencyOverrideCallable::CoroutineFunction
            {
                return Err(PyNotImplementedError::new_err(
                    "async nested dependency support is limited to one coroutine dependency with one coroutine query dependency",
                ));
            }
            let nested_plan = nested_dependencies[0];
            let nested_original = nested_plan.callable.bind(context.py);
            let nested_replacement = context.dependency_overrides.get_item(nested_original)?;
            let (nested_callable, nested_kind) = match nested_replacement {
                Some(replacement) if !replacement.is(nested_original) => {
                    let kind = dependency_override_callable(context.py, &replacement)?;
                    (replacement.unbind(), kind)
                }
                _ => (
                    nested_plan.callable.clone_ref(context.py),
                    dependency_override_callable(context.py, nested_original)?,
                ),
            };
            if nested_kind != DependencyOverrideCallable::CoroutineFunction
                || dependency_callable_is_generator(context.py, nested_callable.bind(context.py))?
            {
                return Err(PyNotImplementedError::new_err(
                    "async nested dependency support requires a coroutine query dependency",
                ));
            }
            let subdependency_plan = CallablePlan::build(
                context.py,
                nested_callable,
                &nested_plan.path_parameters,
                nested_plan.computed_scope.clone(),
            )?;
            let mut supported_query_parameters = true;
            for parameter in &subdependency_plan.parameters {
                // QueryParams::get supplies one scalar value. Sequence
                // annotations need FastAPI's getlist behavior and stay out of
                // this nested-override slice.
                let query_name_matches = match &parameter.source {
                    ParameterSource::Input {
                        source: InputSource::Query,
                        ..
                    } => true,
                    ParameterSource::Input { .. }
                    | ParameterSource::WebSocket
                    | ParameterSource::Request
                    | ParameterSource::HttpConnection
                    | ParameterSource::Response
                    | ParameterSource::BackgroundTasks
                    | ParameterSource::Dependency { .. } => false,
                };
                if parameter.default.is_some()
                    || !query_name_matches
                    || !is_builtin_scalar_query_annotation(
                        context.py,
                        parameter.annotation.bind(context.py),
                    )?
                {
                    supported_query_parameters = false;
                    break;
                }
            }
            if !supported_query_parameters {
                return Err(PyNotImplementedError::new_err(
                    "async nested dependency parameters must be required scalar query parameters",
                ));
            }
            nested_override = Some((
                edge_index,
                cache_key,
                use_cache,
                Box::new(dependency_plan),
                Box::new(subdependency_plan),
            ));
        }

        if let Some((edge_index, cache_key, use_cache, parent_plan, subdependency_plan)) =
            nested_override
        {
            if edge_index < *context.dependency_override_cursor {
                return if context.failures.is_empty() {
                    Ok(OverridePreparation::Ready)
                } else {
                    Ok(OverridePreparation::Invalid)
                };
            }
            *context.dependency_override_cursor = edge_index + 1;
            if use_cache {
                if let Some(value) = context.dependency_cache.get(&cache_key) {
                    context
                        .prepared_dependency_values
                        .insert(edge_index, value.clone_ref(context.py));
                    return Ok(OverridePreparation::Ready);
                }
            }
            let initial_failure_count = context.failures.len();
            let value = subdependency_plan.invoke(context, None, None)?;
            let Some(awaitable) = value else {
                if context.failures.len() != initial_failure_count {
                    return Ok(OverridePreparation::Invalid);
                }
                return Err(PyRuntimeError::new_err(
                    "nested coroutine dependency completed without a value or validation failure",
                ));
            };
            return Ok(OverridePreparation::AwaitSubdependency {
                awaitable,
                parent_plan,
                cache_key,
                edge_index,
            });
        }

        let mut has_validation_errors = !context.failures.is_empty();
        for (edge_index, cache_key, use_cache, callable_kind, generator_kind, dependency_plan) in
            dependency_plans
        {
            if edge_index < *context.dependency_override_cursor {
                continue;
            }
            *context.dependency_override_cursor = edge_index + 1;
            if use_cache {
                if let Some(value) = context.dependency_cache.get(&cache_key) {
                    context
                        .prepared_dependency_values
                        .insert(edge_index, value.clone_ref(context.py));
                    continue;
                }
            }
            let initial_failure_count = context.failures.len();
            let value = if let Some(generator_kind) = generator_kind {
                let Some(context_manager) = dependency_plan.invoke(context, None, None)? else {
                    if context.failures.len() != initial_failure_count {
                        has_validation_errors = true;
                        continue;
                    }
                    return Err(PyRuntimeError::new_err(
                        "yield dependency completed without a context manager or validation failure",
                    ));
                };
                let context_manager = match generator_kind {
                    DependencyGeneratorKind::Async => context_manager,
                    DependencyGeneratorKind::Sync => Py::new(
                        context.py,
                        ThreadpoolDependencyContextManager { context_manager },
                    )?
                    .into_any(),
                };
                let exit_stack = if dependency_plan.computed_scope.as_deref() == Some("function") {
                    context.function_dependency_exit_stack
                } else {
                    context.dependency_exit_stack
                };
                Some(
                    exit_stack
                        .call_method1("enter_async_context", (context_manager.bind(context.py),))?
                        .unbind(),
                )
            } else {
                match callable_kind {
                    DependencyOverrideCallable::CoroutineFunction => {
                        dependency_plan.invoke(context, None, None)?
                    }
                    DependencyOverrideCallable::Sync => {
                        dependency_plan.invoke_in_threadpool(context, None, None)?
                    }
                    DependencyOverrideCallable::AsyncCallableInstance => {
                        return Err(PyNotImplementedError::new_err(
                            "async callable-instance dependency overrides are not supported",
                        ));
                    }
                }
            };
            let Some(value) = value else {
                if context.failures.len() != initial_failure_count {
                    has_validation_errors = true;
                }
                continue;
            };
            return Ok(OverridePreparation::Await {
                awaitable: value,
                cache_key,
                edge_index,
            });
        }
        if has_validation_errors {
            Ok(OverridePreparation::Invalid)
        } else {
            Ok(OverridePreparation::Ready)
        }
    }

    fn invoke(
        &self,
        context: &mut InvocationContext<'_, '_>,
        cache_result: Option<bool>,
        cache_key_override: Option<DependencyCacheKey>,
    ) -> PyResult<Option<Py<PyAny>>> {
        self.invoke_with_threadpool(context, cache_result, cache_key_override, false, None)
    }

    fn invoke_with_prepared_dependencies(
        &self,
        context: &mut InvocationContext<'_, '_>,
        prepared_dependencies: &HashMap<usize, Py<PyAny>>,
    ) -> PyResult<Option<Py<PyAny>>> {
        self.invoke_with_threadpool(context, None, None, false, Some(prepared_dependencies))
    }

    fn invoke_in_threadpool(
        &self,
        context: &mut InvocationContext<'_, '_>,
        cache_result: Option<bool>,
        cache_key_override: Option<DependencyCacheKey>,
    ) -> PyResult<Option<Py<PyAny>>> {
        self.invoke_with_threadpool(context, cache_result, cache_key_override, true, None)
    }

    fn invoke_with_threadpool(
        &self,
        context: &mut InvocationContext<'_, '_>,
        cache_result: Option<bool>,
        cache_key_override: Option<DependencyCacheKey>,
        use_threadpool: bool,
        prepared_dependencies: Option<&HashMap<usize, Py<PyAny>>>,
    ) -> PyResult<Option<Py<PyAny>>> {
        let initial_failure_count = context.failures.len();
        let kwargs = PyDict::new(context.py);
        let aggregate_body = context.body_fields_embedded;
        for parameter in &self.parameters {
            match &parameter.source {
                ParameterSource::WebSocket => {
                    let websocket = context.websocket.ok_or_else(|| {
                        PyRuntimeError::new_err("WebSocket parameter requires a WebSocket scope")
                    })?;
                    kwargs.set_item(&parameter.name, websocket)?;
                }
                ParameterSource::Request => {
                    if let Some(request) = context.request {
                        kwargs.set_item(&parameter.name, request)?;
                    }
                }
                ParameterSource::HttpConnection => {
                    if let Some(connection) = context.request.or(context.websocket) {
                        kwargs.set_item(&parameter.name, connection)?;
                    }
                }
                ParameterSource::Response => {
                    let response = context.response.ok_or_else(|| {
                        PyRuntimeError::new_err(
                            "Response parameter requires a request response context",
                        )
                    })?;
                    kwargs.set_item(&parameter.name, response)?;
                }
                ParameterSource::BackgroundTasks => {
                    let tasks = if let Some(tasks) = context.background_tasks.as_ref() {
                        tasks.clone_ref(context.py)
                    } else {
                        let tasks = context
                            .py
                            .import("fastapi_rs._core")?
                            .getattr("BackgroundTasks")?
                            .call0()?
                            .unbind();
                        *context.background_tasks = Some(tasks.clone_ref(context.py));
                        tasks
                    };
                    kwargs.set_item(&parameter.name, tasks.bind(context.py))?;
                }
                ParameterSource::Input { .. } | ParameterSource::Dependency { .. } => {}
            }
        }
        let mut dependency_edge_index = 0;
        for parameter in &self.parameters {
            if let ParameterSource::Dependency {
                plan,
                use_cache,
                scope,
                bind_value,
                ..
            } = &parameter.source
            {
                let edge_index = dependency_edge_index;
                dependency_edge_index += 1;
                let prepared_value = prepared_dependencies
                    .and_then(|values| values.get(&edge_index))
                    .or_else(|| context.prepared_dependency_values.get(&edge_index));
                if let Some(value) = prepared_value {
                    if *bind_value {
                        kwargs.set_item(&parameter.name, value.bind(context.py))?;
                    }
                    continue;
                }
                let original_cache_key =
                    (plan.callable.as_ptr() as usize, plan.computed_scope.clone());
                let original_callable = plan.callable.bind(context.py);
                let replacement = context.dependency_overrides.get_item(original_callable)?;
                let value = match replacement {
                    Some(replacement) if !replacement.is(original_callable) => {
                        let replacement_plan = CallablePlan::build(
                            context.py,
                            replacement.unbind(),
                            &plan.path_parameters,
                            scope.clone(),
                        )?;
                        replacement_plan.invoke(
                            context,
                            Some(*use_cache),
                            Some(original_cache_key.clone()),
                        )?
                    }
                    _ => plan.invoke(context, Some(*use_cache), Some(original_cache_key))?,
                };
                if let Some(value) = value {
                    if *bind_value {
                        kwargs.set_item(&parameter.name, value.bind(context.py))?;
                    }
                }
            }
        }
        let mut ordered_input_parameters = Vec::with_capacity(self.parameters.len());
        for source in [
            InputSource::Path,
            InputSource::Query,
            InputSource::Header,
            InputSource::Cookie,
        ] {
            let model_parameter_index = self.single_model_parameter_index(source);
            for (index, parameter) in self.parameters.iter().enumerate() {
                if matches!(
                    &parameter.source,
                    ParameterSource::Input {
                        source: parameter_source,
                        ..
                    } if *parameter_source == source
                ) {
                    ordered_input_parameters.push((
                        parameter,
                        source,
                        model_parameter_index == Some(index),
                    ));
                }
            }
        }
        for parameter in &self.parameters {
            if let ParameterSource::Input {
                source: source @ (InputSource::Body | InputSource::Form | InputSource::File),
                ..
            } = &parameter.source
            {
                ordered_input_parameters.push((parameter, *source, false));
            }
        }
        for (parameter, source, is_model_parameter) in ordered_input_parameters {
            let ParameterSource::Input { alias, .. } = &parameter.source else {
                continue;
            };
            let body_field = match source {
                InputSource::Body => aggregate_body,
                InputSource::Form | InputSource::File => !form_parameter_is_unembedded_model(
                    context.py,
                    parameter.annotation.bind(context.py),
                    context.form_body_embedded,
                )?,
                _ => false,
            };
            let value = if is_model_parameter {
                let fields = parameter.parameter_model_fields.as_ref().ok_or_else(|| {
                    PyRuntimeError::new_err("parameter model field plan was not retained")
                })?;
                let values = if source == InputSource::Query {
                    query_model_values(context.py, fields, context.query_params)?
                } else {
                    let connection = context.request.or(context.websocket).ok_or_else(|| {
                        PyRuntimeError::new_err(
                            "request parameter model requires an HTTP or WebSocket connection",
                        )
                    })?;
                    let received_params = connection.getattr(match source {
                        InputSource::Header => "headers",
                        InputSource::Cookie => "cookies",
                        _ => {
                            return Err(PyRuntimeError::new_err(
                                "unsupported parameter model source",
                            ));
                        }
                    })?;
                    parameter_model_values(
                        context.py,
                        fields,
                        &received_params,
                        source,
                        parameter.model_convert_underscores.unwrap_or(true),
                    )?
                };
                Some(values.into_any())
            } else if source == InputSource::Query {
                if parameter.is_sequence {
                    let query_values = context.query_params.get_list(alias);
                    if query_values.is_empty() {
                        None
                    } else {
                        let values = PyList::empty(context.py);
                        for value in query_values {
                            values.append(PyString::new(context.py, value))?;
                        }
                        Some(values.into_any())
                    }
                } else {
                    context
                        .query_params
                        .get(alias)
                        .map(|value| PyString::new(context.py, value).into_any())
                }
            } else {
                context.inputs.get_item(&parameter.name)?
            };
            if source == InputSource::Body
                && aggregate_body
                && value.as_ref().is_some_and(|body| {
                    !body.is_none()
                        && !body.is_instance_of::<PyDict>()
                        && !body.is_instance_of::<PyBytes>()
                })
            {
                context.failures.push(ValidationIssue::Missing {
                    location: source.as_str().to_owned(),
                    alias: alias.clone(),
                    body_field,
                });
                continue;
            }
            let value = if source == InputSource::Body && aggregate_body {
                match value {
                    Some(body) if body.is_instance_of::<PyDict>() => {
                        body.cast::<PyDict>()?.get_item(alias)?
                    }
                    Some(body) if body.is_none() || body.is_instance_of::<PyBytes>() => None,
                    value => value,
                }
            } else {
                value
            };
            let Some(value) = value else {
                if let Some(default) = parameter.default.as_ref() {
                    let default = context
                        .py
                        .import("copy")?
                        .call_method1("deepcopy", (default.bind(context.py),))?;
                    if default.is_none() || source == InputSource::Body {
                        kwargs.set_item(&parameter.name, default)?;
                    } else {
                        match validate_python_value(
                            context.py,
                            parameter.annotation.bind(context.py),
                            &default,
                        ) {
                            Ok(value) => kwargs.set_item(&parameter.name, value)?,
                            Err(error) if is_pydantic_validation_error(context.py, &error) => {
                                context.failures.push(ValidationIssue::Input(Box::new(
                                    InputValidationFailure {
                                        error,
                                        location: source.as_str().to_owned(),
                                        alias: alias.clone(),
                                        include_parameter_alias: !is_model_parameter,
                                        body_field,
                                    },
                                )));
                            }
                            Err(error) => return Err(error),
                        }
                    }
                } else {
                    context.failures.push(ValidationIssue::Missing {
                        location: source.as_str().to_owned(),
                        alias: alias.clone(),
                        body_field,
                    });
                }
                continue;
            };
            match validate_python_value(context.py, parameter.annotation.bind(context.py), &value) {
                Ok(value) => kwargs.set_item(&parameter.name, value)?,
                Err(error) if is_pydantic_validation_error(context.py, &error) => {
                    context.failures.push(ValidationIssue::Input(Box::new(
                        InputValidationFailure {
                            error,
                            location: source.as_str().to_owned(),
                            alias: alias.clone(),
                            include_parameter_alias: !is_model_parameter,
                            body_field,
                        },
                    )));
                }
                Err(error) => return Err(error),
            }
        }
        if context.failures.len() != initial_failure_count {
            return Ok(None);
        }
        let cache_key = cache_key_override
            .unwrap_or_else(|| (self.callable.as_ptr() as usize, self.computed_scope.clone()));
        if cache_result == Some(true) {
            if let Some(value) = context.dependency_cache.get(&cache_key) {
                return Ok(Some(value.clone_ref(context.py)));
            }
        }
        let result = if use_threadpool {
            context
                .py
                .import("starlette.concurrency")?
                .getattr("run_in_threadpool")?
                .call((self.callable.bind(context.py),), Some(&kwargs))?
        } else {
            self.callable.bind(context.py).call((), Some(&kwargs))?
        }
        .unbind();
        if cache_result.is_some() && !context.dependency_cache.contains_key(&cache_key) {
            context
                .dependency_cache
                .insert(cache_key, result.clone_ref(context.py));
        }
        Ok(Some(result))
    }
}

fn is_awaitable(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    py.import("inspect")?
        .getattr("isawaitable")?
        .call1((value,))?
        .extract()
}

fn new_dependency_exit_stack(py: Python<'_>) -> PyResult<Py<PyAny>> {
    py.import("contextlib")?
        .getattr("AsyncExitStack")?
        .call0()
        .map(Bound::unbind)
}

fn dependency_exit_with_error(
    py: Python<'_>,
    exit_stack: &Py<PyAny>,
    error: &PyErr,
) -> PyResult<Py<PyAny>> {
    let exception_type = error.get_type(py).unbind();
    let exception_value = error.value(py).clone().unbind().into_any();
    let traceback = error
        .traceback(py)
        .map(|traceback| traceback.unbind().into_any())
        .unwrap_or_else(|| py.None());
    exit_stack
        .bind(py)
        .call_method1("__aexit__", (exception_type, exception_value, traceback))
        .map(Bound::unbind)
}

fn dependency_override_callable(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
) -> PyResult<DependencyOverrideCallable> {
    let inspect = py.import("inspect")?;
    if inspect
        .getattr("isclass")?
        .call1((value,))?
        .extract::<bool>()?
    {
        return Ok(DependencyOverrideCallable::Sync);
    }
    if inspect
        .getattr("iscoroutinefunction")?
        .call1((value,))?
        .extract::<bool>()?
    {
        return Ok(DependencyOverrideCallable::CoroutineFunction);
    }
    let call_method = value.getattr("__call__")?;
    if inspect
        .getattr("iscoroutinefunction")?
        .call1((call_method,))?
        .extract::<bool>()?
    {
        return Ok(DependencyOverrideCallable::AsyncCallableInstance);
    }
    if crate::security::is_native_async_callable(py, value)? {
        return Ok(DependencyOverrideCallable::CoroutineFunction);
    }
    Ok(DependencyOverrideCallable::Sync)
}

fn dependency_callable_is_generator(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    Ok(dependency_callable_generator_kind(py, value)?.is_some())
}

fn dependency_callable_generator_kind(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
) -> PyResult<Option<DependencyGeneratorKind>> {
    let inspect = py.import("inspect")?;
    let is_class = inspect
        .getattr("isclass")?
        .call1((value,))?
        .extract::<bool>()?;
    if is_class {
        return Ok(None);
    }
    let kind_for = |callable: &Bound<'_, PyAny>| -> PyResult<Option<DependencyGeneratorKind>> {
        if inspect
            .getattr("isasyncgenfunction")?
            .call1((callable,))?
            .extract::<bool>()?
        {
            return Ok(Some(DependencyGeneratorKind::Async));
        }
        if inspect
            .getattr("isgeneratorfunction")?
            .call1((callable,))?
            .extract::<bool>()?
        {
            return Ok(Some(DependencyGeneratorKind::Sync));
        }
        Ok(None)
    };
    if let Some(kind) = kind_for(value)? {
        return Ok(Some(kind));
    }
    kind_for(&value.getattr("__call__")?)
}

fn marker_default(py: Python<'_>, metadata: &[Py<PyAny>]) -> PyResult<Option<Py<PyAny>>> {
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? {
            continue;
        }
        let kind = marker.getattr("kind")?.extract::<String>()?;
        if kind == "header"
            || kind == "query"
            || kind == "cookie"
            || kind == "body"
            || kind == "form"
            || kind == "file"
        {
            let default = marker.getattr("default")?;
            let has_default = if matches!(
                kind.as_str(),
                "header" | "query" | "cookie" | "body" | "form" | "file"
            ) && marker.hasattr("default_is_set")?
            {
                marker.getattr("default_is_set")?.extract::<bool>()?
            } else {
                !default.is_none()
            };
            if has_default {
                return Ok(Some(default.unbind()));
            }
        }
    }
    Ok(None)
}

impl CallableParameter {
    fn populate_form_value(
        &self,
        py: Python<'_>,
        form: &Bound<'_, PyAny>,
        inputs: &Bound<'_, PyDict>,
        form_body_embedded: bool,
        file_reads: &mut VecDeque<FormFileReadPlan>,
    ) -> PyResult<()> {
        let ParameterSource::Input { source, alias } = &self.source else {
            return Ok(());
        };
        if !form_body_embedded && matches!(source, InputSource::Form | InputSource::File) {
            if is_pydantic_model_annotation(py, self.annotation.bind(py))? {
                let model_values = form_model_values(py, self.annotation.bind(py), form)?;
                inputs.set_item(&self.name, model_values)?;
                return Ok(());
            }
            if is_union_of_base_models(py, self.annotation.bind(py))? {
                let model_values =
                    form_union_values(py, form, alias, self.default.as_ref(), self.is_sequence)?;
                inputs.set_item(&self.name, model_values)?;
                return Ok(());
            }
        }
        let value = if self.is_sequence {
            let values = form.call_method1("getlist", (alias,))?;
            if values.len()? == 0 {
                None
            } else {
                Some(values)
            }
        } else {
            let value = form.call_method1("get", (alias,))?;
            (!value.is_none()).then_some(value)
        };
        if let Some(value) = value {
            if !self.is_sequence
                && value.is_instance_of::<PyString>()
                && value.extract::<String>()?.is_empty()
            {
                return Ok(());
            }
            if *source == InputSource::File
                && self.is_sequence
                && is_bytes_sequence_annotation(py, self.annotation.bind(py))?
            {
                let awaitables = value
                    .try_iter()?
                    .map(|item| item?.call_method0("read").map(Bound::unbind))
                    .collect::<PyResult<VecDeque<_>>>()?;
                file_reads.push_back(FormFileReadPlan {
                    name: self.name.clone(),
                    annotation: self.annotation.clone_ref(py),
                    sequence: true,
                    awaitables,
                    values: Vec::new(),
                });
            } else if *source == InputSource::File
                && is_bytes_annotation(py, self.annotation.bind(py))?
            {
                let upload_file_type = py
                    .import("starlette.datastructures")?
                    .getattr("UploadFile")?;
                if value.is_instance(&upload_file_type)? {
                    file_reads.push_back(FormFileReadPlan {
                        name: self.name.clone(),
                        annotation: self.annotation.clone_ref(py),
                        sequence: false,
                        awaitables: VecDeque::from([value.call_method0("read")?.unbind()]),
                        values: Vec::new(),
                    });
                } else {
                    inputs.set_item(&self.name, value)?;
                }
            } else {
                inputs.set_item(&self.name, value)?;
            }
        }
        Ok(())
    }

    fn input_parameters(&self) -> Vec<FastApiInputParameter> {
        match &self.source {
            ParameterSource::Input { source, alias } => vec![FastApiInputParameter {
                name: self.name.clone(),
                alias: alias.clone(),
                location: source.location(),
                required: self.default.is_none(),
            }],
            ParameterSource::Dependency { plan, .. } => plan.input_parameters(),
            ParameterSource::WebSocket
            | ParameterSource::Request
            | ParameterSource::HttpConnection
            | ParameterSource::Response
            | ParameterSource::BackgroundTasks => Vec::new(),
        }
    }
}

enum ValidationIssue {
    Input(Box<InputValidationFailure>),
    Missing {
        location: String,
        alias: String,
        body_field: bool,
    },
}

struct InputValidationFailure {
    error: PyErr,
    location: String,
    alias: String,
    include_parameter_alias: bool,
    body_field: bool,
}

fn annotation_parts(
    py: Python<'_>,
    annotation: Py<PyAny>,
) -> PyResult<(Py<PyAny>, Vec<Py<PyAny>>)> {
    let typing = py.import("typing")?;
    let origin = typing
        .getattr("get_origin")?
        .call1((annotation.bind(py),))?;
    let annotated = typing.getattr("Annotated")?;
    if !origin.is(&annotated) {
        return Ok((annotation, Vec::new()));
    }
    let arguments = typing
        .getattr("get_args")?
        .call1((annotation.bind(py),))?
        .cast_into::<PyTuple>()?;
    let base = arguments.get_item(0)?.unbind();
    let metadata = arguments.iter().skip(1).map(Bound::unbind).collect();
    Ok((base, metadata))
}

fn parameter_source(
    py: Python<'_>,
    name: &str,
    annotation: &Bound<'_, PyAny>,
    metadata: &[Py<PyAny>],
    path_parameters: &[String],
) -> PyResult<ParameterSource> {
    // Explicit Depends takes precedence over framework-managed parameter injection.
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? || marker.getattr("kind")?.extract::<String>()? != "depends" {
            continue;
        }
        let dependency = marker.getattr("dependency")?;
        let dependency = if dependency.is_none() {
            annotation.clone().unbind()
        } else {
            dependency.unbind()
        };
        let use_cache = marker.getattr("use_cache")?.extract::<bool>()?;
        let scope = marker.getattr("scope")?.extract::<Option<String>>()?;
        let marker_scopes = marker.getattr("scopes")?;
        let security_scopes = if marker_scopes.is_none() {
            Vec::new()
        } else {
            marker_scopes
                .try_iter()?
                .map(|scope| scope?.extract::<String>())
                .collect::<PyResult<Vec<_>>>()?
        };
        let path_names = path_parameters.to_vec();
        return CallablePlan::build(py, dependency, &path_names, scope.clone()).map(|plan| {
            ParameterSource::Dependency {
                plan: Box::new(plan),
                use_cache,
                scope,
                security_scopes,
                bind_value: true,
            }
        });
    }
    let request_type = py.import("starlette.requests")?.getattr("Request")?;
    if annotation_is_subclass(py, annotation, &request_type)? {
        return Ok(ParameterSource::Request);
    }
    let websocket_type = py.import("starlette.websockets")?.getattr("WebSocket")?;
    if annotation.is(&websocket_type) {
        return Ok(ParameterSource::WebSocket);
    }
    let connection_type = py.import("starlette.requests")?.getattr("HTTPConnection")?;
    if annotation_is_subclass(py, annotation, &connection_type)? {
        return Ok(ParameterSource::HttpConnection);
    }
    let response_type = py.import("starlette.responses")?.getattr("Response")?;
    if annotation_is_subclass(py, annotation, &response_type)? {
        return Ok(ParameterSource::Response);
    }
    let background_tasks_type = py
        .import("starlette.background")?
        .getattr("BackgroundTasks")?;
    if annotation_is_subclass(py, annotation, &background_tasks_type)? {
        return Ok(ParameterSource::BackgroundTasks);
    }
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? {
            continue;
        }
        let kind = marker.getattr("kind")?.extract::<String>()?;
        if kind == "body" {
            let declared_alias = marker.getattr("alias")?.extract::<Option<String>>()?;
            let validation_alias = marker.getattr("validation_alias")?;
            let validation_alias =
                if validation_alias.is_truthy()? && validation_alias.is_instance_of::<PyString>() {
                    Some(validation_alias.extract::<String>()?)
                } else {
                    None
                };
            return Ok(ParameterSource::Input {
                source: InputSource::Body,
                alias: validation_alias
                    .or(declared_alias)
                    .unwrap_or_else(|| name.to_owned()),
            });
        }
        if kind == "form" || kind == "file" {
            let declared_alias = marker.getattr("alias")?.extract::<Option<String>>()?;
            let validation_alias = marker.getattr("validation_alias")?;
            let validation_alias =
                if validation_alias.is_truthy()? && validation_alias.is_instance_of::<PyString>() {
                    Some(validation_alias.extract::<String>()?)
                } else {
                    None
                };
            let alias = validation_alias
                .or(declared_alias)
                .unwrap_or_else(|| name.to_owned());
            return Ok(ParameterSource::Input {
                source: if kind == "form" {
                    InputSource::Form
                } else {
                    InputSource::File
                },
                alias,
            });
        }
        if kind == "path" {
            return Ok(ParameterSource::Input {
                source: InputSource::Path,
                alias: name.to_owned(),
            });
        }
        if kind == "header" || kind == "query" || kind == "cookie" {
            let declared_alias = marker.getattr("alias")?.extract::<Option<String>>()?;
            let validation_alias = if kind == "query" {
                let validation_alias = marker.getattr("validation_alias")?;
                if validation_alias.is_instance_of::<PyString>() {
                    let validation_alias = validation_alias.extract::<String>()?;
                    (!validation_alias.is_empty()).then_some(validation_alias)
                } else {
                    None
                }
            } else {
                None
            };
            let alias = match validation_alias.or(declared_alias) {
                Some(alias) => alias,
                None if kind == "header"
                    && marker.getattr("convert_underscores")?.extract::<bool>()? =>
                {
                    name.replace('_', "-")
                }
                None => name.to_owned(),
            };
            return Ok(ParameterSource::Input {
                source: if kind == "header" {
                    InputSource::Header
                } else if kind == "cookie" {
                    InputSource::Cookie
                } else {
                    InputSource::Query
                },
                alias,
            });
        }
    }

    if path_parameters.iter().any(|path_name| path_name == name) {
        return Ok(ParameterSource::Input {
            source: InputSource::Path,
            alias: name.to_owned(),
        });
    }
    if is_uploadfile_annotation(py, annotation)?
        || is_uploadfile_sequence_annotation(py, annotation)?
    {
        return Ok(ParameterSource::Input {
            source: InputSource::File,
            alias: name.to_owned(),
        });
    }
    if field_annotation_is_complex(py, annotation)? {
        return Ok(ParameterSource::Input {
            source: InputSource::Body,
            alias: name.to_owned(),
        });
    }
    Ok(ParameterSource::Input {
        source: InputSource::Query,
        alias: name.to_owned(),
    })
}

/// Mirrors FastAPI's ``field_annotation_is_complex`` default-source rule.
fn field_annotation_is_complex(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let annotated = typing.getattr("Annotated")?;
    if origin.is(&annotated) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        return field_annotation_is_complex(py, &arguments.get_item(0)?);
    }

    let union = typing.getattr("Union")?;
    let union_type = py.import("types")?.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        for argument in arguments.iter() {
            if field_annotation_is_complex(py, &argument)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }

    if annotation_is_complex_type(py, annotation)?
        || (!origin.is_none() && annotation_is_complex_type(py, &origin)?)
    {
        return Ok(true);
    }

    if origin.is_none() {
        return Ok(false);
    }
    Ok(origin.hasattr("__pydantic_core_schema__")?
        || origin.hasattr("__get_pydantic_core_schema__")?)
}

fn annotation_is_complex_type(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let base_model = py.import("pydantic")?.getattr("BaseModel")?;
    if annotation_is_subclass(py, annotation, &base_model)? {
        return Ok(true);
    }
    let mapping = py.import("collections.abc")?.getattr("Mapping")?;
    if annotation_is_subclass(py, annotation, &mapping)? {
        return Ok(true);
    }
    let upload_file = py
        .import("starlette.datastructures")?
        .getattr("UploadFile")?;
    if annotation_is_subclass(py, annotation, &upload_file)? || is_sequence_class(py, annotation)? {
        return Ok(true);
    }
    py.import("dataclasses")?
        .getattr("is_dataclass")?
        .call1((annotation,))?
        .extract()
}

fn annotation_is_subclass(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    parent: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let inspect = py.import("inspect")?;
    if !inspect
        .getattr("isclass")?
        .call1((annotation,))?
        .extract::<bool>()?
    {
        return Ok(false);
    }
    py.import("builtins")?
        .getattr("issubclass")?
        .call1((annotation, parent))?
        .extract()
}

fn parameter_media_type(
    py: Python<'_>,
    source: &ParameterSource,
    metadata: &[Py<PyAny>],
) -> PyResult<Option<String>> {
    let expected_kind = match source {
        ParameterSource::Input {
            source: InputSource::Body,
            ..
        } => "body",
        ParameterSource::Input {
            source: InputSource::Form,
            ..
        } => "form",
        ParameterSource::Input {
            source: InputSource::File,
            ..
        } => "file",
        _ => return Ok(None),
    };
    for marker in metadata {
        let marker = marker.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == expected_kind
        {
            if let Some(media_type) = marker.getattr("media_type")?.extract::<Option<String>>()? {
                return Ok(Some(media_type));
            }
        }
    }
    let default_media_type = match expected_kind {
        "body" => "application/json",
        "form" => "application/x-www-form-urlencoded",
        "file" => "multipart/form-data",
        _ => return Ok(None),
    };
    Ok(Some(default_media_type.to_owned()))
}

fn parameter_description(
    py: Python<'_>,
    source: &ParameterSource,
    metadata: &[Py<PyAny>],
) -> PyResult<Option<String>> {
    let expected_kind = match source {
        ParameterSource::Input {
            source: InputSource::Query,
            ..
        } => "query",
        ParameterSource::Input {
            source: InputSource::Form,
            ..
        } => "form",
        ParameterSource::Input {
            source: InputSource::File,
            ..
        } => "file",
        _ => return Ok(None),
    };
    for marker in metadata {
        let marker = marker.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == expected_kind
        {
            return marker.getattr("description")?.extract::<Option<String>>();
        }
    }
    Ok(None)
}

fn parameter_title(
    py: Python<'_>,
    source: &ParameterSource,
    metadata: &[Py<PyAny>],
) -> PyResult<Option<String>> {
    if !matches!(
        source,
        ParameterSource::Input {
            source: InputSource::Query,
            ..
        }
    ) {
        return Ok(None);
    }
    for marker in metadata {
        let marker = marker.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == "query" {
            return marker.getattr("title")?.extract::<Option<String>>();
        }
    }
    Ok(None)
}

fn parameter_deprecated(
    py: Python<'_>,
    source: &ParameterSource,
    metadata: &[Py<PyAny>],
) -> PyResult<bool> {
    if !matches!(
        source,
        ParameterSource::Input {
            source: InputSource::Query,
            ..
        }
    ) {
        return Ok(false);
    }
    for marker in metadata {
        let marker = marker.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == "query" {
            let deprecated = marker.getattr("deprecated")?;
            return Ok(!deprecated.is_none() && deprecated.is_truthy()?);
        }
    }
    Ok(false)
}

fn parameter_include_in_schema(
    py: Python<'_>,
    source: &ParameterSource,
    metadata: &[Py<PyAny>],
) -> PyResult<bool> {
    if !matches!(
        source,
        ParameterSource::Input {
            source: InputSource::Query,
            ..
        }
    ) {
        return Ok(true);
    }
    for marker in metadata {
        let marker = marker.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == "query" {
            return marker.getattr("include_in_schema")?.extract::<bool>();
        }
    }
    Ok(true)
}

fn parameter_body_embed(
    py: Python<'_>,
    source: &ParameterSource,
    metadata: &[Py<PyAny>],
) -> PyResult<bool> {
    if !matches!(
        source,
        ParameterSource::Input {
            source: InputSource::Body,
            ..
        }
    ) {
        return Ok(false);
    }
    for marker in metadata {
        let marker = marker.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == "body" {
            let embed = marker.getattr("embed")?;
            return Ok(!embed.is_none() && embed.is_truthy()?);
        }
    }
    Ok(false)
}

fn is_pydantic_model_annotation(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    if origin.is(&typing.getattr("Annotated")?) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        return is_pydantic_model_annotation(py, &arguments.get_item(0)?);
    }
    let union = typing.getattr("Union")?;
    let union_type = py.import("types")?.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        if arguments.len() == 2 {
            let none = py.None();
            let none_type = none.bind(py).get_type();
            for argument in arguments.iter() {
                if argument.is(&none_type) {
                    let model = if arguments.get_item(0)?.is(&none_type) {
                        arguments.get_item(1)?
                    } else {
                        arguments.get_item(0)?
                    };
                    return is_pydantic_model_annotation(py, &model);
                }
            }
        }
        return Ok(false);
    }
    is_pydantic_model(py, annotation)
}

fn is_union_of_base_models(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let union = typing.getattr("Union")?;
    let union_type = py.import("types")?.getattr("UnionType")?;
    if !origin.is(&union) && !origin.is(&union_type) {
        return Ok(false);
    }
    let arguments = typing
        .getattr("get_args")?
        .call1((annotation,))?
        .cast_into::<PyTuple>()?;
    if arguments.is_empty() {
        return Ok(false);
    }
    for argument in arguments.iter() {
        if !is_pydantic_model_annotation(py, &argument)? {
            return Ok(false);
        }
    }
    Ok(true)
}

fn form_body_should_embed(
    py: Python<'_>,
    body_parameters: &[&CallableParameter],
) -> PyResult<bool> {
    if body_parameters.is_empty() {
        return Ok(false);
    }
    if body_fields_embedded(body_parameters) {
        return Ok(true);
    }
    let unique_names = body_parameters
        .iter()
        .map(|parameter| parameter.name.as_str())
        .collect::<BTreeSet<_>>();
    if unique_names.len() > 1 {
        return Ok(true);
    }

    let first = body_parameters[0];
    let is_form_field = matches!(
        first.source,
        ParameterSource::Input {
            source: InputSource::Form | InputSource::File,
            ..
        }
    );
    if is_form_field
        && !is_pydantic_model_annotation(py, first.annotation.bind(py))?
        && !is_union_of_base_models(py, first.annotation.bind(py))?
    {
        return Ok(true);
    }
    Ok(false)
}

fn body_fields_embedded(body_parameters: &[&CallableParameter]) -> bool {
    let unique_names = body_parameters
        .iter()
        .map(|parameter| parameter.name.as_str())
        .collect::<BTreeSet<_>>();
    unique_names.len() > 1
        || body_parameters
            .first()
            .is_some_and(|parameter| parameter.body_embed)
}

fn form_parameter_is_unembedded_model(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    form_body_embedded: bool,
) -> PyResult<bool> {
    if form_body_embedded {
        return Ok(false);
    }
    Ok(is_pydantic_model_annotation(py, annotation)? || is_union_of_base_models(py, annotation)?)
}

fn aggregate_body_media_type(body_parameters: &[&CallableParameter]) -> String {
    if body_parameters.iter().any(|parameter| {
        matches!(
            parameter.source,
            ParameterSource::Input {
                source: InputSource::File,
                ..
            }
        )
    }) {
        // FastAPI constructs an aggregate File field with File's default media type.
        "multipart/form-data".to_owned()
    } else if body_parameters.iter().any(|parameter| {
        matches!(
            parameter.source,
            ParameterSource::Input {
                source: InputSource::Form,
                ..
            }
        )
    }) {
        // FastAPI constructs an aggregate Form field with Form's default media type.
        "application/x-www-form-urlencoded".to_owned()
    } else {
        let media_types = body_parameters
            .iter()
            .filter(|parameter| {
                matches!(
                    &parameter.source,
                    ParameterSource::Input {
                        source: InputSource::Body,
                        ..
                    }
                )
            })
            .map(|parameter| parameter.media_type.as_deref())
            .collect::<BTreeSet<_>>();
        if media_types.len() == 1 {
            if let Some(Some(media_type)) = media_types.first().copied() {
                return media_type.to_owned();
            }
        }
        "application/json".to_owned()
    }
}

fn is_uploadfile_annotation(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        for argument in arguments.iter() {
            if is_uploadfile_annotation(py, &argument)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }
    let builtins = py.import("builtins")?;
    let is_type = builtins
        .getattr("isinstance")?
        .call1((annotation, builtins.getattr("type")?))?
        .extract::<bool>()?;
    if !is_type {
        return Ok(false);
    }
    let upload_file_type = py
        .import("starlette.datastructures")?
        .getattr("UploadFile")?;
    builtins
        .getattr("issubclass")?
        .call1((annotation, upload_file_type))?
        .extract()
}

fn is_uploadfile_sequence_annotation(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        for argument in arguments.iter() {
            if is_uploadfile_sequence_annotation(py, &argument)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }
    if !field_annotation_is_sequence(py, annotation)? {
        return Ok(false);
    }
    let arguments = typing
        .getattr("get_args")?
        .call1((annotation,))?
        .cast_into::<PyTuple>()?;
    for argument in arguments.iter() {
        if !is_uploadfile_annotation(py, &argument)? {
            return Ok(false);
        }
    }
    Ok(true)
}

fn constrained_parameter_annotation(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    metadata: &[Py<PyAny>],
    default: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let mut annotated_arguments = vec![annotation.clone().unbind()];
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? {
            annotated_arguments.push(marker.clone().unbind());
            continue;
        }
        let kind = marker.getattr("kind")?.extract::<String>()?;
        if kind != "body" && kind != "query" && kind != "path" {
            continue;
        }
        let kwargs = PyDict::new(py);
        let mut has_field_metadata = false;
        for name in ["gt", "ge", "lt", "le", "min_length", "max_length"] {
            if kind != "query" && !matches!(name, "gt" | "ge" | "lt" | "le") {
                continue;
            }
            let value = marker.getattr(name)?;
            if !value.is_none() {
                kwargs.set_item(name, value)?;
                has_field_metadata = true;
            }
        }
        if kind == "query" {
            for name in ["title", "description", "pattern", "deprecated"] {
                let value = marker.getattr(name)?;
                if value.is_none() || (name == "pattern" && value.extract::<String>()?.is_empty()) {
                    continue;
                }
                kwargs.set_item(name, value)?;
                has_field_metadata = true;
            }
            if let Some(default) = default {
                kwargs.set_item("default", default)?;
                has_field_metadata = true;
            }
        }
        if has_field_metadata {
            let field = py
                .import("pydantic")?
                .getattr("Field")?
                .call((), Some(&kwargs))?;
            annotated_arguments.push(field.unbind());
        }
    }
    if annotated_arguments.len() == 1 {
        return Ok(annotated_arguments.remove(0));
    }
    let arguments = PyTuple::new(py, annotated_arguments)?;
    py.import("typing")?
        .getattr("Annotated")?
        .get_item(arguments)
        .map(Bound::unbind)
}

fn is_pydantic_model(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let Ok(annotation_type) = annotation.cast::<PyType>() else {
        return Ok(false);
    };
    let issubclass = py.import("builtins")?.getattr("issubclass")?;
    let base_model = py.import("pydantic")?.getattr("BaseModel")?;
    issubclass
        .call1((annotation_type, base_model))?
        .extract::<bool>()
}

fn is_response_annotation(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let Ok(annotation_type) = annotation.cast::<PyType>() else {
        return Ok(false);
    };
    let response_type = py.import("starlette.responses")?.getattr("Response")?;
    py.import("builtins")?
        .getattr("issubclass")?
        .call1((annotation_type, response_type))?
        .extract::<bool>()
}

fn typed_return_annotation(
    py: Python<'_>,
    callable: &Bound<'_, PyAny>,
    annotation: &Bound<'_, PyAny>,
    empty: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    if annotation.is(empty) || annotation.is_none() {
        return Ok(None);
    }
    let Ok(annotation_string) = annotation.cast::<PyString>() else {
        return Ok(Some(annotation.clone().unbind()));
    };

    let inspect = py.import("inspect")?;
    let unwrapped = inspect.getattr("unwrap")?.call1((callable,))?;
    let globalns = match unwrapped.getattr("__globals__") {
        Ok(globalns) => globalns,
        Err(error) if error.is_instance_of::<PyAttributeError>(py) => PyDict::new(py).into_any(),
        Err(error) => return Err(error),
    };
    let evaluated =
        py.import("builtins")?
            .getattr("eval")?
            .call1((annotation_string, &globalns, &globalns));
    let evaluated = match evaluated {
        Ok(evaluated) => evaluated,
        Err(error) if error.is_instance_of::<PyNameError>(py) => {
            return py
                .import("typing")?
                .getattr("ForwardRef")?
                .call1((annotation_string,))
                .map(|forward_ref| Some(forward_ref.unbind()));
        }
        Err(error) => return Err(error),
    };
    if evaluated.is_none() {
        Ok(None)
    } else {
        Ok(Some(evaluated.unbind()))
    }
}

fn route_reverse_metadata(
    py: Python<'_>,
    path: &str,
    endpoint: &Bound<'_, PyAny>,
) -> PyResult<(String, Py<PyDict>)> {
    let routing = py.import("starlette.routing")?;
    let name = routing
        .getattr("_get_name")?
        .call1((endpoint,))?
        .extract::<String>()?;
    let param_convertors = route_param_convertors(py, path)?;
    Ok((name, param_convertors))
}

fn http_route_scope(
    py: Python<'_>,
    path: &str,
    endpoint: &Bound<'_, PyAny>,
    method: &str,
    name: &str,
) -> PyResult<(Py<PyAny>, String)> {
    let route_type = py.import("starlette.routing")?.getattr("Route")?;
    let methods = PyList::new(py, [method])?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("methods", methods)?;
    kwargs.set_item("name", name)?;
    let route = route_type.call((path, endpoint), Some(&kwargs))?;
    let path_format = route.getattr("path_format")?.extract::<String>()?;
    Ok((route.unbind(), path_format))
}

fn websocket_route_scope(
    py: Python<'_>,
    path: &str,
    endpoint: &Bound<'_, PyAny>,
    name: Option<&str>,
) -> PyResult<Py<PyAny>> {
    let kwargs = PyDict::new(py);
    if let Some(name) = name {
        kwargs.set_item("name", name)?;
    }
    py.import("starlette.routing")?
        .getattr("WebSocketRoute")?
        .call((path, endpoint), Some(&kwargs))
        .map(Bound::unbind)
}

fn add_raw_websocket_route(
    app: &mut PyFastApi,
    py: Python<'_>,
    path: &str,
    endpoint: &Bound<'_, PyAny>,
    name: Option<&str>,
) -> PyResult<()> {
    let scope_path = format!("{}{}", app.route_scope_prefix, path);
    let route_scope = websocket_route_scope(py, &scope_path, endpoint, name)?;
    let route_name = route_scope.bind(py).getattr("name")?.extract::<String>()?;
    let param_convertors = route_param_convertors(py, path)?;
    let index = app
        .websocket_router
        .add_operation(path, "GET", Some(200))
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    app.websocket_router
        .set_parameters(index, Vec::new())
        .ok_or_else(|| PyRuntimeError::new_err("registered raw WebSocket route was lost"))?;
    app.websocket_routes.push(FastApiWebSocketRoute {
        path: path.to_owned(),
        name: route_name,
        route_scope,
        param_convertors,
        route_dependencies: Vec::new(),
        endpoint: endpoint.clone().unbind(),
        plan: None,
        raw: true,
    });
    app.bump_routes_version();
    Ok(())
}

fn route_param_convertors(py: Python<'_>, path: &str) -> PyResult<Py<PyDict>> {
    let compiled_path = py
        .import("starlette.routing")?
        .getattr("compile_path")?
        .call1((path,))?;
    Ok(compiled_path
        .get_item(2)?
        .cast::<PyDict>()?
        .clone()
        .unbind())
}

fn route_path_format(py: Python<'_>, path: &str) -> PyResult<String> {
    py.import("starlette.routing")?
        .getattr("compile_path")?
        .call1((path,))?
        .get_item(1)?
        .extract()
}

fn path_parameter_names(path: &str) -> Vec<String> {
    let mut names = Vec::new();
    let mut remainder = path;
    while let Some(open) = remainder.find('{') {
        remainder = &remainder[open + 1..];
        let Some(close) = remainder.find('}') else {
            break;
        };
        let name = remainder[..close]
            .split_once(':')
            .map_or(&remainder[..close], |(name, _)| name);
        names.push(name.to_owned());
        remainder = &remainder[close + 1..];
    }
    names
}

fn operation_id(name: &str, path: &str, method: &str) -> String {
    let mut operation_id = String::with_capacity(name.len() + path.len() + method.len() + 1);
    for character in name.chars().chain(path.chars()) {
        if character.is_alphanumeric() || character == '_' {
            operation_id.push(character);
        } else {
            operation_id.push('_');
        }
    }
    operation_id.push('_');
    operation_id.push_str(&method.to_ascii_lowercase());
    operation_id
}

fn title_case(value: &str) -> String {
    let mut titled = String::with_capacity(value.len());
    let mut capitalize_next = true;
    for character in value.chars() {
        if character.is_alphanumeric() {
            if capitalize_next {
                titled.extend(character.to_uppercase());
            } else {
                titled.extend(character.to_lowercase());
            }
            capitalize_next = false;
        } else {
            titled.push(character);
            capitalize_next = true;
        }
    }
    titled
}

fn model_name(_py: Python<'_>, model: &Bound<'_, PyAny>) -> PyResult<Option<String>> {
    model
        .getattr("__name__")
        .and_then(|name| name.extract::<String>())
        .map(Some)
        .or_else(|_| Ok(None))
}

fn schema_definition_name(schema: &Bound<'_, PyAny>) -> PyResult<Option<String>> {
    let Ok(schema) = schema.cast::<PyDict>() else {
        return Ok(None);
    };
    let Some(reference) = schema.get_item("$ref")? else {
        return Ok(None);
    };
    let Ok(reference) = reference.extract::<String>() else {
        return Ok(None);
    };
    let Some(name) = reference
        .strip_prefix("#/$defs/")
        .or_else(|| reference.strip_prefix("#/components/schemas/"))
    else {
        return Ok(None);
    };
    Ok(Some(name.replace("~1", "/").replace("~0", "~")))
}

fn response_field_schema_title(name: &str, path: &str, method: &str) -> String {
    let mut unique_id = format!("{name}{path}")
        .chars()
        .map(|character| {
            if character.is_alphanumeric() || character == '_' {
                character
            } else {
                '_'
            }
        })
        .collect::<String>();
    unique_id.push('_');
    unique_id.push_str(&method.to_ascii_lowercase());
    title_case(&format!("Response_{unique_id}").replace('_', " "))
}

fn openapi_response_status_key(
    py: Python<'_>,
    route_status_code: Option<u16>,
    response_class: Option<&Bound<'_, PyAny>>,
) -> PyResult<Option<String>> {
    if let Some(status_code) = route_status_code {
        return Ok(Some(status_code.to_string()));
    }

    let response_class = match response_class {
        Some(response_class) => response_class.clone(),
        None => py.import("starlette.responses")?.getattr("JSONResponse")?,
    };
    let response_signature = py
        .import("inspect")?
        .getattr("signature")?
        .call1((response_class.getattr("__init__")?,))?;
    let parameters = response_signature.getattr("parameters")?;
    let status_code_parameter = parameters.call_method1("get", ("status_code",))?;
    if status_code_parameter.is_none() {
        return Ok(None);
    }
    let default = status_code_parameter.getattr("default")?;
    if !default.is_instance(&py.import("builtins")?.getattr("int")?)? {
        return Ok(None);
    }
    py.import("builtins")?
        .getattr("str")?
        .call1((default,))?
        .extract()
        .map(Some)
}

fn aggregate_body_model(
    py: Python<'_>,
    model_name: &str,
    body_parameters: &[&CallableParameter],
) -> PyResult<Py<PyAny>> {
    let fields = PyDict::new(py);
    let required = py.import("builtins")?.getattr("Ellipsis")?;
    for parameter in body_parameters {
        let default = parameter
            .default
            .as_ref()
            .map_or_else(|| required.clone(), |value| value.bind(py).clone());
        let field = match &parameter.source {
            ParameterSource::Input {
                source: InputSource::Body | InputSource::Form | InputSource::File,
                alias,
            } => {
                let kwargs = PyDict::new(py);
                kwargs.set_item("alias", alias)?;
                if let Some(description) = parameter.description.as_deref() {
                    kwargs.set_item("description", description)?;
                }
                py.import("pydantic")?
                    .getattr("Field")?
                    .call((default,), Some(&kwargs))?
            }
            _ => default,
        };
        fields.set_item(&parameter.name, (parameter.annotation.bind(py), field))?;
    }
    py.import("pydantic")?
        .getattr("create_model")?
        .call((model_name,), Some(&fields))
        .map(Bound::unbind)
}

fn pydantic_schema(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    mode: &str,
    title: Option<&str>,
) -> PyResult<Py<PyAny>> {
    pydantic_schema_with_config(py, annotation, mode, title, None)
}

fn body_parameter_schema(
    py: Python<'_>,
    parameter: &CallableParameter,
    title: Option<&str>,
) -> PyResult<Py<PyAny>> {
    let is_body = matches!(
        &parameter.source,
        ParameterSource::Input {
            source: InputSource::Body,
            ..
        }
    );
    let Some(default) = parameter.default.as_ref().filter(|_| is_body) else {
        return pydantic_schema(py, parameter.annotation.bind(py), "validation", title);
    };
    let field = py
        .import("pydantic")?
        .getattr("Field")?
        .call1((default.bind(py),))?;
    let annotation = PyTuple::new(py, [parameter.annotation.clone_ref(py), field.unbind()])?;
    let annotation = py
        .import("typing")?
        .getattr("Annotated")?
        .get_item(annotation)?;
    pydantic_schema(py, &annotation, "validation", title)
}

fn pydantic_schema_with_config(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    mode: &str,
    title: Option<&str>,
    config: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let adapter_kwargs = PyDict::new(py);
    if let Some(config) = config {
        adapter_kwargs.set_item("config", config)?;
    }
    let adapter = py
        .import("pydantic")?
        .getattr("TypeAdapter")?
        .call((annotation,), Some(&adapter_kwargs))?;
    let core_schema = adapter.getattr("core_schema")?;
    let generator_kwargs = PyDict::new(py);
    generator_kwargs.set_item("ref_template", "#/components/schemas/{model}")?;
    let generator = py
        .import("fastapi_rs._core")?
        .getattr("_FastApiGenerateJsonSchema")?
        .call((), Some(&generator_kwargs))?;
    let inputs = PyList::empty(py);
    let input = PyTuple::new(
        py,
        [
            PyString::new(py, "fastapi-rs-schema").into_any(),
            PyString::new(py, mode).into_any(),
            core_schema.clone(),
        ],
    )?;
    inputs.append(input)?;
    let generated = generator
        .call_method1("generate_definitions", (inputs,))?
        .cast_into::<PyTuple>()?;
    let field_schemas = generated.get_item(0)?.cast_into::<PyDict>()?;
    let definitions = generated.get_item(1)?.cast_into::<PyDict>()?;
    let field_key = PyTuple::new(
        py,
        [
            PyString::new(py, "fastapi-rs-schema").into_any(),
            PyString::new(py, mode).into_any(),
        ],
    )?;
    let field_schema = field_schemas.get_item(&field_key)?.ok_or_else(|| {
        PyValueError::new_err("Pydantic did not generate the requested JSON Schema mode")
    })?;
    let field_schema = field_schema.cast_into::<PyDict>()?;
    let schema = PyDict::new(py);
    for (key, value) in field_schema.iter() {
        schema.set_item(key, value)?;
    }
    if !definitions.is_empty() {
        schema.set_item("$defs", definitions)?;
    }
    if schema.get_item("title")?.is_none() && schema.get_item("$ref")?.is_none() {
        if let Some(title) = title {
            schema.set_item("title", title)?;
        }
    }
    Ok(schema.into_any().unbind())
}

fn validate_python_value(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    value: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let adapter = py
        .import("pydantic")?
        .getattr("TypeAdapter")?
        .call1((annotation,))?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("from_attributes", true)?;
    adapter
        .call_method("validate_python", (value,), Some(&kwargs))
        .map(Bound::unbind)
}

fn is_builtin_scalar_query_annotation(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let builtins = py.import("builtins")?;
    for name in ["str", "int", "float", "bool", "bytes"] {
        if annotation.is(&builtins.getattr(name)?) {
            return Ok(true);
        }
    }
    Ok(false)
}

fn is_pydantic_validation_error(py: Python<'_>, error: &PyErr) -> bool {
    py.import("pydantic")
        .and_then(|pydantic| pydantic.getattr("ValidationError"))
        .is_ok_and(|validation_error| {
            error
                .matches(py, &validation_error)
                .is_ok_and(|value| value)
        })
}

/// Mirrors FastAPI's public sequence-annotation classification for request extraction.
fn field_annotation_is_sequence(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let annotated = typing.getattr("Annotated")?;
    if origin.is(&annotated) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        return field_annotation_is_sequence(py, &arguments.get_item(0)?);
    }

    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        for argument in arguments.iter() {
            if field_annotation_is_sequence(py, &argument)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }

    if is_sequence_class(py, annotation)? {
        return Ok(true);
    }
    if origin.is_none() {
        Ok(false)
    } else {
        is_sequence_class(py, &origin)
    }
}

fn is_sequence_class(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let builtins = py.import("builtins")?;
    if !builtins
        .getattr("isinstance")?
        .call1((annotation, builtins.getattr("type")?))?
        .extract::<bool>()?
    {
        return Ok(false);
    }

    let str_type = builtins.getattr("str")?;
    let bytes_type = builtins.getattr("bytes")?;
    let excluded = PyTuple::new(py, [str_type, bytes_type])?;
    if builtins
        .getattr("issubclass")?
        .call1((annotation, excluded))?
        .extract::<bool>()?
    {
        return Ok(false);
    }

    let collections_abc = py.import("collections.abc")?;
    let collections = py.import("collections")?;
    let sequence_types = PyTuple::new(
        py,
        [
            collections_abc.getattr("Sequence")?,
            builtins.getattr("list")?,
            builtins.getattr("tuple")?,
            builtins.getattr("set")?,
            builtins.getattr("frozenset")?,
            collections.getattr("deque")?,
        ],
    )?;
    builtins
        .getattr("issubclass")?
        .call1((annotation, sequence_types))?
        .extract()
}

fn is_bytes_annotation(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        for argument in arguments.iter() {
            if is_bytes_annotation(py, &argument)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }
    let builtins = py.import("builtins")?;
    let is_type = builtins
        .getattr("isinstance")?
        .call1((annotation, builtins.getattr("type")?))?
        .extract::<bool>()?;
    if is_type {
        return builtins
            .getattr("issubclass")?
            .call1((annotation, builtins.getattr("bytes")?))?
            .extract();
    }
    Ok(false)
}

fn is_bytes_sequence_annotation(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        for argument in arguments.iter() {
            if is_bytes_sequence_annotation(py, &argument)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }
    if !field_annotation_is_sequence(py, annotation)? {
        return Ok(false);
    }
    let arguments = typing
        .getattr("get_args")?
        .call1((annotation,))?
        .cast_into::<PyTuple>()?;
    for argument in arguments.iter() {
        if !is_bytes_annotation(py, &argument)? {
            return Ok(false);
        }
    }
    Ok(true)
}

fn sequence_value_for_annotation<'py>(
    py: Python<'py>,
    annotation: &Bound<'py, PyAny>,
    values: &Bound<'py, PyList>,
) -> PyResult<Bound<'py, PyAny>> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    let sequence_annotation = if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        let mut found = None;
        for argument in arguments.iter() {
            if field_annotation_is_sequence(py, &argument)? {
                found = Some(argument);
                break;
            }
        }
        found.ok_or_else(|| {
            PyValueError::new_err("bytes sequence annotation has no sequence type")
        })?
    } else {
        annotation.clone()
    };
    let sequence_origin = typing
        .getattr("get_origin")?
        .call1((&sequence_annotation,))?;
    let sequence_type = if sequence_origin.is_none() {
        &sequence_annotation
    } else {
        &sequence_origin
    };
    let sequence_abc = py.import("collections.abc")?.getattr("Sequence")?;
    let typing_sequence = typing.getattr("Sequence")?;
    let constructor = if sequence_type.is(&sequence_abc) || sequence_type.is(&typing_sequence) {
        py.import("builtins")?.getattr("list")?
    } else {
        sequence_type.clone()
    };
    constructor.call1((values,))
}

fn pydantic_field_validation_alias(
    field_name: &Bound<'_, PyAny>,
    field_info: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let validation_alias = field_info.getattr("validation_alias")?;
    if let Ok(validation_alias) = validation_alias.extract::<String>() {
        if !validation_alias.is_empty() {
            return Ok(PyString::new(field_name.py(), &validation_alias)
                .unbind()
                .into_any());
        }
    }
    let alias = field_info.getattr("alias")?;
    if let Ok(alias) = alias.extract::<String>() {
        if !alias.is_empty() {
            return Ok(PyString::new(field_name.py(), &alias).unbind().into_any());
        }
    }
    Ok(field_name.clone().unbind())
}

fn copied_pydantic_field_default<'py>(
    py: Python<'py>,
    field_info: &Bound<'py, PyAny>,
) -> PyResult<Option<Bound<'py, PyAny>>> {
    if field_info.call_method0("is_required")?.extract::<bool>()? {
        return Ok(None);
    }
    let kwargs = PyDict::new(py);
    kwargs.set_item("call_default_factory", true)?;
    let default = field_info.call_method("get_default", (), Some(&kwargs))?;
    py.import("copy")?
        .call_method1("deepcopy", (default,))
        .map(Some)
}

fn header_model_convert_underscores(py: Python<'_>, metadata: &[Py<PyAny>]) -> PyResult<bool> {
    for item in metadata {
        let marker = item.bind(py);
        if marker.hasattr("kind")? && marker.getattr("kind")?.extract::<String>()? == "header" {
            return marker.getattr("convert_underscores")?.extract::<bool>();
        }
    }
    Ok(true)
}

fn parameter_model_fields(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
) -> PyResult<Vec<ParameterModelField>> {
    let model_fields = annotation.getattr("model_fields")?.cast_into::<PyDict>()?;
    let json_type = py.import("pydantic.types")?.getattr("Json")?;
    let mut fields = Vec::with_capacity(model_fields.len());
    for (field_name, field_info) in model_fields.iter() {
        let name = field_name.extract::<String>()?;
        let alias = pydantic_field_validation_alias(&field_name, &field_info)?;
        let alias = alias.extract::<String>(py)?;
        let field_annotation = field_info.getattr("annotation")?;
        let is_sequence = field_annotation_is_sequence(py, &field_annotation)?;
        let metadata = field_info.getattr("metadata")?;
        let mut is_json = false;
        for item in metadata.try_iter()? {
            if item?.get_type().is(&json_type) {
                is_json = true;
                break;
            }
        }
        let convert_underscores = if field_info.hasattr("convert_underscores")? {
            Some(
                field_info
                    .getattr("convert_underscores")?
                    .extract::<bool>()?,
            )
        } else {
            None
        };
        fields.push(ParameterModelField {
            name,
            alias,
            field_info: field_info.unbind(),
            is_sequence,
            is_json,
            convert_underscores,
        });
    }
    Ok(fields)
}

fn pydantic_field_schema_annotation(
    py: Python<'_>,
    field_info: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let field_data = field_info.call_method0("asdict")?.cast_into::<PyDict>()?;
    let annotation = field_data
        .get_item("annotation")?
        .ok_or_else(|| PyValueError::new_err("Pydantic field is missing its annotation"))?;
    let metadata = field_data
        .get_item("metadata")?
        .ok_or_else(|| PyValueError::new_err("Pydantic field is missing its metadata"))?;
    let attributes = field_data
        .get_item("attributes")?
        .ok_or_else(|| PyValueError::new_err("Pydantic field is missing its attributes"))?
        .cast_into::<PyDict>()?;
    let field = py
        .import("pydantic")?
        .getattr("Field")?
        .call((), Some(&attributes))?;
    let arguments = PyList::empty(py);
    arguments.append(annotation)?;
    for metadata_item in metadata.try_iter()? {
        arguments.append(metadata_item?)?;
    }
    arguments.append(field)?;
    let arguments = py
        .import("builtins")?
        .getattr("tuple")?
        .call1((arguments,))?;
    py.import("typing")?
        .getattr("Annotated")?
        .get_item(arguments)
        .map(Bound::unbind)
}

fn parameter_model_field_openapi_plan(
    py: Python<'_>,
    field: &ParameterModelField,
    source: InputSource,
    model_config: Option<&Py<PyAny>>,
    model_convert_underscores: Option<bool>,
) -> PyResult<Option<ParameterOpenApiPlan>> {
    let field_info = field.field_info.bind(py);
    if field_info.hasattr("include_in_schema")?
        && !field_info.getattr("include_in_schema")?.is_truthy()?
    {
        return Ok(None);
    }
    let required = field_info.call_method0("is_required")?.extract::<bool>()?;
    let field_title = field_info.getattr("title")?.extract::<Option<String>>()?;
    let title = field_title.unwrap_or_else(|| title_case(&field.alias.replace('_', " ")));
    let description = field_info
        .getattr("description")?
        .extract::<Option<String>>()?;
    let deprecated = field_info.getattr("deprecated")?.is_truthy()?;
    let default = query_model_field_openapi_default(py, field_info)?;
    let annotation = pydantic_field_schema_annotation(py, field_info)?;
    let name = if source == InputSource::Header
        && field
            .convert_underscores
            .unwrap_or(model_convert_underscores.unwrap_or(true))
        && field.alias == field.name
    {
        field.name.replace('_', "-")
    } else {
        field.alias.clone()
    };
    Ok(Some(ParameterOpenApiPlan {
        name,
        location: source.as_str().to_owned(),
        required,
        annotation,
        schema_config: model_config.map(|value| value.clone_ref(py)),
        default,
        title: Some(title),
        description,
        deprecated,
    }))
}

fn query_model_field_openapi_default(
    py: Python<'_>,
    field_info: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    if field_info.call_method0("is_required")?.extract::<bool>()?
        || !field_info.getattr("default_factory")?.is_none()
    {
        return Ok(None);
    }
    let default = field_info.getattr("default")?;
    let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
    if default.is_none() || default.is(&undefined) {
        return Ok(None);
    }
    Ok(Some(default.unbind()))
}

fn copy_unmatched_form_values(
    form: &Bound<'_, PyAny>,
    values: &Bound<'_, PyDict>,
    processed_aliases: &[String],
) -> PyResult<()> {
    for key in form.call_method0("keys")?.try_iter()? {
        let key = key?;
        let key_name = key.extract::<String>().ok();
        if key_name
            .as_deref()
            .is_some_and(|name| processed_aliases.iter().any(|alias| alias == name))
        {
            continue;
        }
        let field_values = form.call_method1("getlist", (&key,))?;
        let value = if field_values.len()? == 1 {
            field_values.get_item(0)?
        } else {
            field_values
        };
        values.set_item(&key, value)?;
    }
    Ok(())
}

fn form_model_values<'py>(
    py: Python<'py>,
    annotation: &Bound<'py, PyAny>,
    form: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    let model_fields = annotation.getattr("model_fields")?.cast_into::<PyDict>()?;
    let values = PyDict::new(py);
    let mut processed_aliases = Vec::with_capacity(model_fields.len());
    for (field_name, field_info) in model_fields.iter() {
        let alias = pydantic_field_validation_alias(&field_name, &field_info)?;
        if let Ok(alias_name) = alias.bind(py).extract::<String>() {
            processed_aliases.push(alias_name);
        }
        let field_annotation = field_info.getattr("annotation")?;
        let mut value = if field_annotation_is_sequence(py, &field_annotation)? {
            let field_values = form.call_method1("getlist", (alias.bind(py),))?;
            if field_values.len()? == 0 {
                None
            } else {
                Some(field_values)
            }
        } else {
            let field_value = form.call_method1("get", (alias.bind(py),))?;
            if field_value.is_none() {
                None
            } else {
                Some(field_value)
            }
        };
        if value.is_none() {
            value = copied_pydantic_field_default(py, &field_info)?;
        }
        if let Some(value) = value.filter(|value| !value.is_none()) {
            values.set_item(alias.bind(py), value)?;
        }
    }
    copy_unmatched_form_values(form, &values, &processed_aliases)?;
    Ok(values)
}

fn query_model_values<'py>(
    py: Python<'py>,
    fields: &[ParameterModelField],
    query_params: &QueryParams,
) -> PyResult<Bound<'py, PyDict>> {
    let values = PyDict::new(py);
    let mut processed_aliases = Vec::with_capacity(fields.len());
    for field in fields {
        processed_aliases.push(field.alias.as_str());
        let mut value = if field.is_sequence && !field.is_json {
            let field_values = query_params.get_list(&field.alias);
            if field_values.is_empty() {
                None
            } else {
                let values = PyList::empty(py);
                for field_value in field_values {
                    values.append(PyString::new(py, field_value))?;
                }
                Some(values.into_any())
            }
        } else {
            query_params
                .get(&field.alias)
                .map(|value| PyString::new(py, value).into_any())
        };
        if value.is_none() {
            value = copied_pydantic_field_default(py, field.field_info.bind(py))?;
        }
        if let Some(value) = value.filter(|value| !value.is_none()) {
            values.set_item(&field.alias, value)?;
        }
    }

    for key in query_params.keys() {
        if processed_aliases.contains(&key) {
            continue;
        }
        let field_values = query_params.get_list(key);
        let value = if field_values.len() == 1 {
            PyString::new(py, field_values[0]).into_any()
        } else {
            let values = PyList::empty(py);
            for field_value in field_values {
                values.append(PyString::new(py, field_value))?;
            }
            values.into_any()
        };
        values.set_item(key, value)?;
    }
    Ok(values)
}

fn parameter_model_values<'py>(
    py: Python<'py>,
    fields: &[ParameterModelField],
    received_params: &Bound<'py, PyAny>,
    source: InputSource,
    model_convert_underscores: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let values = PyDict::new(py);
    let mut processed_aliases = Vec::with_capacity(fields.len() * 2);
    for field in fields {
        let request_alias = if source == InputSource::Header
            && field
                .convert_underscores
                .unwrap_or(model_convert_underscores)
            && field.alias == field.name
        {
            field.name.replace('_', "-")
        } else {
            field.alias.clone()
        };
        processed_aliases.push(request_alias.clone());
        processed_aliases.push(field.alias.clone());
        let mut value = if source == InputSource::Header && field.is_sequence && !field.is_json {
            let field_values = received_params.call_method1("getlist", (&request_alias,))?;
            if field_values.len()? == 0 {
                None
            } else {
                Some(field_values)
            }
        } else {
            let field_value = received_params.call_method1("get", (&request_alias,))?;
            if field_value.is_none() {
                None
            } else {
                Some(field_value)
            }
        };
        if value.is_none() {
            value = copied_pydantic_field_default(py, field.field_info.bind(py))?;
        }
        if let Some(value) = value.filter(|value| !value.is_none()) {
            values.set_item(&field.alias, value)?;
        }
    }

    for key in received_params.call_method0("keys")?.try_iter()? {
        let key = key?;
        let key_name = key.extract::<String>().ok();
        if key_name.as_deref().is_some_and(|name| {
            processed_aliases
                .iter()
                .any(|processed_alias| processed_alias == name)
        }) {
            continue;
        }
        let value = if source == InputSource::Header {
            let field_values = received_params.call_method1("getlist", (&key,))?;
            if field_values.len()? == 1 {
                field_values.get_item(0)?
            } else {
                field_values
            }
        } else {
            received_params.call_method1("get", (&key,))?
        };
        values.set_item(&key, value)?;
    }
    Ok(values)
}

fn form_union_values<'py>(
    py: Python<'py>,
    form: &Bound<'py, PyAny>,
    alias: &str,
    default: Option<&Py<PyAny>>,
    sequence: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let values = PyDict::new(py);
    let processed_aliases = [alias.to_owned()];
    let mut value = if sequence {
        let field_values = form.call_method1("getlist", (alias,))?;
        if field_values.len()? == 0 {
            None
        } else {
            Some(field_values.into_any())
        }
    } else {
        let field_value = form.call_method1("get", (alias,))?;
        if field_value.is_none() {
            None
        } else {
            Some(field_value)
        }
    };
    if value.as_ref().is_some_and(|value| {
        value.is_instance_of::<PyString>()
            && value
                .extract::<String>()
                .is_ok_and(|value| value.is_empty())
    }) || value.is_none()
    {
        value = match default {
            Some(default) => Some(
                py.import("copy")?
                    .call_method1("deepcopy", (default.bind(py),))?,
            ),
            None => None,
        };
    }
    if let Some(value) = value.filter(|value| !value.is_none()) {
        values.set_item(alias, value)?;
    }
    copy_unmatched_form_values(form, &values, &processed_aliases)?;
    Ok(values)
}

fn is_json_decode_error(py: Python<'_>, error: &PyErr) -> bool {
    py.import("json")
        .and_then(|json| json.getattr("JSONDecodeError"))
        .is_ok_and(|decode_error| error.matches(py, &decode_error).is_ok_and(|value| value))
}

fn validation_error_details<'py>(
    py: Python<'py>,
    failures: &[ValidationIssue],
) -> PyResult<Bound<'py, PyList>> {
    let details = PyList::empty(py);
    for failure in failures {
        match failure {
            ValidationIssue::Input(failure) => {
                append_input_validation_details(py, &details, failure)?;
            }
            ValidationIssue::Missing {
                location,
                alias,
                body_field,
            } => {
                append_missing_validation_detail(py, &details, location, alias, *body_field)?;
            }
        }
    }
    Ok(details)
}

fn validation_response_body_from_details(
    py: Python<'_>,
    details: &Bound<'_, PyList>,
) -> PyResult<Py<PyAny>> {
    let result = PyDict::new(py);
    result.set_item("detail", details)?;
    Ok(jsonable_encoder_default(py, &result)?.unbind())
}

fn validation_location_tuple(py: Python<'_>, location: &Bound<'_, PyList>) -> PyResult<Py<PyAny>> {
    py.import("builtins")?
        .getattr("tuple")?
        .call1((location,))
        .map(Bound::unbind)
}

fn append_input_validation_details(
    py: Python<'_>,
    details: &Bound<'_, PyList>,
    failure: &InputValidationFailure,
) -> PyResult<()> {
    let error_value = failure.error.value(py);
    let kwargs = PyDict::new(py);
    kwargs.set_item("include_url", false)?;
    let errors = error_value
        .call_method("errors", (), Some(&kwargs))?
        .cast_into::<PyList>()?;
    for entry in errors.iter() {
        let entry = entry.cast_into::<PyDict>()?;
        let detail = PyDict::new(py);
        detail.set_item("type", entry.get_item("type")?)?;
        let loc = PyList::empty(py);
        loc.append(failure.location.as_str())?;
        if failure.location == "body" {
            if failure.body_field {
                loc.append(failure.alias.as_str())?;
            }
            let field_loc = entry.get_item("loc")?.ok_or_else(|| {
                PyValueError::new_err("Pydantic validation error is missing its location")
            })?;
            for part in field_loc.try_iter()? {
                loc.append(part?)?;
            }
        } else {
            if failure.include_parameter_alias {
                loc.append(failure.alias.as_str())?;
            }
            let field_loc = entry.get_item("loc")?.ok_or_else(|| {
                PyValueError::new_err("Pydantic validation error is missing its location")
            })?;
            for part in field_loc.try_iter()? {
                loc.append(part?)?;
            }
        }
        detail.set_item("loc", validation_location_tuple(py, &loc)?)?;
        detail.set_item("msg", entry.get_item("msg")?)?;
        if let Some(input) = entry.get_item("input")? {
            let input = if input.is_instance_of::<PyBytes>() {
                input.call_method0("decode")?
            } else {
                input
            };
            detail.set_item("input", input)?;
        }
        if let Some(context) = entry.get_item("ctx")? {
            detail.set_item("ctx", context)?;
        }
        details.append(detail)?;
    }
    Ok(())
}

fn append_missing_validation_detail(
    py: Python<'_>,
    details: &Bound<'_, PyList>,
    location: &str,
    alias: &str,
    body_field: bool,
) -> PyResult<()> {
    let detail = PyDict::new(py);
    detail.set_item("type", "missing")?;
    let loc = PyList::empty(py);
    loc.append(location)?;
    if location != "body" || body_field {
        loc.append(alias)?;
    }
    detail.set_item("loc", validation_location_tuple(py, &loc)?)?;
    detail.set_item("msg", "Field required")?;
    detail.set_item("input", py.None())?;
    details.append(detail)?;
    Ok(())
}

fn json_decode_validation_response_body(py: Python<'_>, error: &PyErr) -> PyResult<Py<PyAny>> {
    let error_value = error.value(py);
    let detail = PyDict::new(py);
    detail.set_item("type", "json_invalid")?;
    let location = PyList::empty(py);
    location.append("body")?;
    location.append(error_value.getattr("pos")?)?;
    detail.set_item("loc", validation_location_tuple(py, &location)?)?;
    detail.set_item("msg", "JSON decode error")?;
    detail.set_item("input", PyDict::new(py))?;
    let context = PyDict::new(py);
    context.set_item("error", error_value.getattr("msg")?)?;
    detail.set_item("ctx", context)?;
    let details = PyList::empty(py);
    details.append(detail)?;
    let result = PyDict::new(py);
    result.set_item("detail", details)?;
    Ok(result.into_any().unbind())
}

fn bad_request_body_response_body(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let result = PyDict::new(py);
    result.set_item("detail", "There was an error parsing the body")?;
    Ok(result.into_any().unbind())
}

fn json_bytes(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<Vec<u8>> {
    let kwargs = PyDict::new(py);
    kwargs.set_item("ensure_ascii", false)?;
    kwargs.set_item("allow_nan", false)?;
    kwargs.set_item("separators", (",", ":"))?;
    py.import("json")?
        .getattr("dumps")?
        .call((value,), Some(&kwargs))?
        .extract::<String>()
        .map(String::into_bytes)
}

enum InputDecodeError {
    JsonValidation(PyErr),
    BodyParse(PyErr),
    Other(PyErr),
}

fn should_parse_json_body(headers: &[(Vec<u8>, Vec<u8>)], strict_content_type: bool) -> bool {
    let Some((_, value)) = headers
        .iter()
        .find(|(name, _)| name.eq_ignore_ascii_case(b"content-type"))
    else {
        return !strict_content_type;
    };
    if value.is_empty() {
        return !strict_content_type;
    }
    let media_type = value.split(|byte| *byte == b';').next().unwrap_or_default();
    let Ok(media_type) = std::str::from_utf8(media_type) else {
        return false;
    };
    let media_type = media_type.trim();
    let Some((media_type, subtype)) = media_type.split_once('/') else {
        return false;
    };
    let subtype = subtype.trim().to_ascii_lowercase();
    media_type.trim().eq_ignore_ascii_case("application")
        && (subtype == "json" || subtype.ends_with("+json"))
}

fn decode_input_values(
    py: Python<'_>,
    request: crate::FastApiRequestMatch,
    parse_json_body: bool,
) -> Result<Py<PyDict>, InputDecodeError> {
    let values = PyDict::new(py);
    for input in request.inputs {
        let Some(value) = input.value else {
            continue;
        };
        if input.location == FastApiInputLocation::Body && value.is_empty() {
            continue;
        }
        let value = match input.location {
            FastApiInputLocation::Body if parse_json_body => {
                let json = py.import("json").map_err(InputDecodeError::Other)?;
                let loads = json.getattr("loads").map_err(InputDecodeError::Other)?;
                match loads.call1((PyBytes::new(py, &value),)) {
                    Ok(value) => value,
                    Err(error) if is_json_decode_error(py, &error) => {
                        return Err(InputDecodeError::JsonValidation(error));
                    }
                    Err(error) => return Err(InputDecodeError::BodyParse(error)),
                }
            }
            FastApiInputLocation::Body => PyBytes::new(py, &value).into_any(),
            FastApiInputLocation::Header => PyBytes::new(py, &value)
                .call_method1("decode", ("latin-1",))
                .map_err(InputDecodeError::Other)?,
            FastApiInputLocation::Path
            | FastApiInputLocation::Query
            | FastApiInputLocation::Cookie => PyBytes::new(py, &value)
                .call_method1("decode", ("utf-8",))
                .map_err(InputDecodeError::Other)?,
        };
        values
            .set_item(input.name, value)
            .map_err(InputDecodeError::Other)?;
    }
    Ok(values.unbind())
}

fn response_start(
    py: Python<'_>,
    send: &Bound<'_, PyAny>,
    status: u16,
    body: &[u8],
    extra_headers: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let headers = PyList::empty(py);
    if status != 204 {
        headers.append((
            PyBytes::new(py, b"content-length"),
            PyBytes::new(py, body.len().to_string().as_bytes()),
        ))?;
    }
    headers.append((
        PyBytes::new(py, b"content-type"),
        PyBytes::new(py, b"application/json"),
    ))?;
    if let Some(extra_headers) = extra_headers {
        for header in extra_headers.try_iter()? {
            headers.append(header?)?;
        }
    }
    let message = PyDict::new(py);
    message.set_item("type", "http.response.start")?;
    message.set_item("status", status)?;
    message.set_item("headers", headers)?;
    send.call1((message,)).map(Bound::unbind)
}

fn fastapi_response_state(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let response = py
        .import("starlette.responses")?
        .getattr("Response")?
        .call0()?;
    response
        .getattr("headers")?
        .call_method1("__delitem__", ("content-length",))?;
    response.setattr("status_code", py.None())?;
    Ok(response.unbind())
}

fn injected_response_status(response: Option<&Bound<'_, PyAny>>) -> PyResult<Option<Py<PyAny>>> {
    let Some(response) = response else {
        return Ok(None);
    };
    let status_code = response.getattr("status_code")?;
    if status_code.is_none() || !status_code.is_truthy()? {
        return Ok(None);
    }
    Ok(Some(status_code.unbind()))
}

fn merge_injected_response_state(
    py: Python<'_>,
    response: &Bound<'_, PyAny>,
    injected_response: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    let Some(injected_response) = injected_response else {
        return Ok(());
    };
    if let Some(status_code) = injected_response_status(Some(injected_response))? {
        response.setattr("status_code", status_code.bind(py))?;
    }
    let response_headers = response.getattr("headers")?.getattr("raw")?;
    let injected_headers = injected_response.getattr("headers")?.getattr("raw")?;
    response_headers.call_method1("extend", (injected_headers,))?;
    Ok(())
}

fn attach_response_background_if_missing(
    response: &Bound<'_, PyAny>,
    background_tasks: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    if response.getattr("background")?.is_none()
        && let Some(background_tasks) = background_tasks
    {
        response.setattr("background", background_tasks)?;
    }
    Ok(())
}

fn response_body(py: Python<'_>, send: &Bound<'_, PyAny>, body: &[u8]) -> PyResult<Py<PyAny>> {
    let message = PyDict::new(py);
    message.set_item("type", "http.response.body")?;
    message.set_item("body", PyBytes::new(py, body))?;
    message.set_item("more_body", false)?;
    send.call1((message,)).map(Bound::unbind)
}

fn parse_scope_string(scope: &Bound<'_, PyAny>, key: &str, default: &str) -> PyResult<String> {
    scope
        .call_method1("get", (key, default))?
        .extract::<String>()
}

fn response_endpoint_context<'py>(
    py: Python<'py>,
    endpoint: &Bound<'py, PyAny>,
    method: &str,
    path: &str,
    root_path: &str,
) -> PyResult<Bound<'py, PyDict>> {
    let context = PyDict::new(py);
    let inspect = py.import("inspect")?;
    let endpoint_details = (|| -> PyResult<()> {
        let source_file = inspect.getattr("getsourcefile")?.call1((endpoint,))?;
        if !source_file.is_none() {
            context.set_item("file", source_file)?;
        }
        let source_lines = inspect.getattr("getsourcelines")?.call1((endpoint,))?;
        let line = source_lines.get_item(1)?;
        if !line.is_none() {
            context.set_item("line", line)?;
        }
        let function =
            py.import("builtins")?
                .getattr("getattr")?
                .call1((endpoint, "__name__", py.None()))?;
        if !function.is_none() {
            context.set_item("function", function)?;
        }
        Ok(())
    })();
    if endpoint_details.is_err() {
        context.clear();
    }
    context.set_item(
        "path",
        format!("{method} {}{path}", root_path.trim_end_matches('/')),
    )?;
    Ok(context)
}

enum PendingAction {
    RequestBody,
    FormParse,
    FormFileRead,
    LifespanCompletion,
    WebSocketEndpoint,
    WebSocketClose,
    MountedApp,
    FrontendConfig,
    FrontendResponse,
    FrontendAsgiResponse,
    RouteInvocation,
    Endpoint,
    Dependency {
        cache_key: DependencyCacheKey,
        edge_index: usize,
    },
    DependencyGraph(Box<DependencyExecutionGraph>),
    OverrideSubdependency {
        parent_plan: Box<CallablePlan>,
        cache_key: DependencyCacheKey,
        edge_index: usize,
    },
    ReturnedResponse,
    FunctionDependencyCloseBeforeResponse,
    FunctionDependencyCloseAfterResponse,
    FunctionDependencyCloseAfterError(PyErr),
    DependencyCloseAfterResponse,
    DependencyCloseAfterError(PyErr),
    FormCloseAfterResponse,
    FormCloseAfterError(PyErr),
    SendStart,
    SendBody,
    BackgroundTasks,
}

enum FunctionCloseContinuation {
    ReturnedResponse(Py<PyAny>),
    SendStart(Option<Py<PyAny>>),
}

#[derive(Clone, Copy)]
enum FastApiStreamEncoding {
    Raw,
    JsonLines,
    ServerSentEvents,
}

struct StreamItemSerializer {
    adapter: Py<PyAny>,
    validation_kwargs: Py<PyDict>,
    serialization_kwargs: Py<PyDict>,
    endpoint_context: Py<PyAny>,
}

impl StreamItemSerializer {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        Self {
            adapter: self.adapter.clone_ref(py),
            validation_kwargs: self.validation_kwargs.clone_ref(py),
            serialization_kwargs: self.serialization_kwargs.clone_ref(py),
            endpoint_context: self.endpoint_context.clone_ref(py),
        }
    }
}

fn encode_sse_stream_item(
    py: Python<'_>,
    item: &Bound<'_, PyAny>,
    serializer: Option<&StreamItemSerializer>,
) -> PyResult<Py<PyBytes>> {
    if sse::is_server_sent_event(py, item)? {
        let raw_data = item.getattr("raw_data")?;
        let data = item.getattr("data")?;
        let data_str = if !raw_data.is_none() {
            Some(raw_data.extract::<String>()?)
        } else if data.is_none() {
            None
        } else if data.hasattr("model_dump_json")? {
            Some(data.call_method0("model_dump_json")?.extract::<String>()?)
        } else {
            let encoded = jsonable_encoder_default(py, &data)?;
            Some(
                py.import("json")?
                    .getattr("dumps")?
                    .call1((encoded,))?
                    .extract::<String>()?,
            )
        };
        let event = item.getattr("event")?;
        let id = item.getattr("id")?;
        let retry = item.getattr("retry")?;
        let comment = item.getattr("comment")?;
        return sse::format_event(
            py,
            data_str.as_deref(),
            Some(&event),
            Some(&id),
            Some(&retry),
            Some(&comment),
        );
    }

    let data_str = if let Some(serializer) = serializer {
        let validated = match serializer.adapter.bind(py).call_method(
            "validate_python",
            (item,),
            Some(serializer.validation_kwargs.bind(py)),
        ) {
            Ok(validated) => validated,
            Err(error) if is_pydantic_validation_error(py, &error) => {
                return Err(crate::errors::response_validation_error(
                    py,
                    &error,
                    item,
                    serializer.endpoint_context.bind(py),
                )?);
            }
            Err(error) => return Err(error),
        };
        let bytes = serializer
            .adapter
            .bind(py)
            .call_method(
                "dump_json",
                (validated,),
                Some(serializer.serialization_kwargs.bind(py)),
            )?
            .extract::<Vec<u8>>()?;
        String::from_utf8(bytes).map_err(|error| PyValueError::new_err(error.to_string()))?
    } else {
        let encoded = jsonable_encoder_default(py, item)?;
        py.import("json")?
            .getattr("dumps")?
            .call1((encoded,))?
            .extract::<String>()?
    };
    sse::format_event(py, Some(&data_str), None, None, None, None)
}

#[pyclass(name = "_FastApiAsyncStream", module = "fastapi_rs._core", unsendable)]
struct PyFastApiAsyncStream {
    iterator: Py<PyAny>,
    synchronous: bool,
    sentinel: Py<PyAny>,
    encoding: FastApiStreamEncoding,
    serializer: Option<StreamItemSerializer>,
    checkpoint_next: bool,
}

#[pymethods]
impl PyFastApiAsyncStream {
    #[new]
    fn new(py: Python<'_>, content: Py<PyAny>, json_lines: bool) -> PyResult<Self> {
        Self::from_content(py, content, false, json_lines, false, None)
    }

    fn __aiter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    fn __anext__(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let (next, sentinel) = if self.synchronous {
            let next = py.import("builtins")?.getattr("next")?;
            let run_sync = py
                .import("anyio")?
                .getattr("to_thread")?
                .getattr("run_sync")?;
            (
                run_sync
                    .call1((next, self.iterator.bind(py), self.sentinel.bind(py)))?
                    .unbind(),
                Some(self.sentinel.clone_ref(py)),
            )
        } else {
            let next = self.iterator.bind(py).call_method0("__anext__")?.unbind();
            (next, None)
        };
        let checkpoint = if self.synchronous {
            None
        } else if self.checkpoint_next {
            Some(py.import("anyio")?.getattr("sleep")?.call1((0,))?.unbind())
        } else {
            None
        };
        self.checkpoint_next = true;
        let serializer = self.serializer.as_ref().map(|value| value.clone_ref(py));
        into_python_awaitable(
            py,
            FastApiStreamNext {
                next,
                sentinel,
                checkpoint,
                stage: StreamNextStage::Next,
                encoding: self.encoding,
                serializer,
            },
        )
    }
}

impl PyFastApiAsyncStream {
    fn from_content(
        py: Python<'_>,
        content: Py<PyAny>,
        synchronous: bool,
        json_lines: bool,
        sse_stream: bool,
        serializer: Option<StreamItemSerializer>,
    ) -> PyResult<Self> {
        let iterator = if synchronous {
            content.bind(py).call_method0("__iter__")?
        } else {
            content.bind(py).call_method0("__aiter__")?
        }
        .unbind();
        let sentinel = py.import("builtins")?.getattr("object")?.call0()?.unbind();
        Ok(Self {
            iterator,
            synchronous,
            sentinel,
            encoding: if sse_stream {
                FastApiStreamEncoding::ServerSentEvents
            } else if json_lines {
                FastApiStreamEncoding::JsonLines
            } else {
                FastApiStreamEncoding::Raw
            },
            serializer,
            checkpoint_next: false,
        })
    }
}

#[derive(Clone, Copy)]
enum StreamNextStage {
    Checkpoint,
    Next,
}

struct FastApiStreamNext {
    next: Py<PyAny>,
    sentinel: Option<Py<PyAny>>,
    checkpoint: Option<Py<PyAny>>,
    stage: StreamNextStage,
    encoding: FastApiStreamEncoding,
    serializer: Option<StreamItemSerializer>,
}

impl AwaitableStateMachine for FastApiStreamNext {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => match self.checkpoint.as_ref() {
                Some(checkpoint) => {
                    self.stage = StreamNextStage::Checkpoint;
                    Ok(MachineAction::Await(checkpoint.clone_ref(py)))
                }
                None => {
                    self.stage = StreamNextStage::Next;
                    Ok(MachineAction::Await(self.next.clone_ref(py)))
                }
            },
            MachineResume::Value(value) => match self.stage {
                StreamNextStage::Checkpoint => {
                    self.stage = StreamNextStage::Next;
                    Ok(MachineAction::Await(self.next.clone_ref(py)))
                }
                StreamNextStage::Next => {
                    if self
                        .sentinel
                        .as_ref()
                        .is_some_and(|sentinel| value.bind(py).is(sentinel.bind(py)))
                    {
                        return Err(PyStopAsyncIteration::new_err(""));
                    }
                    match self.encoding {
                        FastApiStreamEncoding::Raw => Ok(MachineAction::Complete(value)),
                        FastApiStreamEncoding::ServerSentEvents => {
                            encode_sse_stream_item(py, value.bind(py), self.serializer.as_ref())
                                .map(|encoded| MachineAction::Complete(encoded.into_any()))
                        }
                        FastApiStreamEncoding::JsonLines => {
                            let mut line = if let Some(serializer) = self.serializer.as_ref() {
                                let validated = match serializer.adapter.bind(py).call_method(
                                    "validate_python",
                                    (value.bind(py),),
                                    Some(serializer.validation_kwargs.bind(py)),
                                ) {
                                    Ok(validated) => validated,
                                    Err(error) if is_pydantic_validation_error(py, &error) => {
                                        return Err(crate::errors::response_validation_error(
                                            py,
                                            &error,
                                            value.bind(py),
                                            serializer.endpoint_context.bind(py),
                                        )?);
                                    }
                                    Err(error) => return Err(error),
                                };
                                serializer
                                    .adapter
                                    .bind(py)
                                    .call_method(
                                        "dump_json",
                                        (validated,),
                                        Some(serializer.serialization_kwargs.bind(py)),
                                    )?
                                    .extract::<Vec<u8>>()?
                            } else {
                                let encoded = jsonable_encoder_default(py, value.bind(py))?;
                                py.import("json")?
                                    .getattr("dumps")?
                                    .call1((encoded,))?
                                    .extract::<String>()?
                                    .into_bytes()
                            };
                            line.push(b'\n');
                            Ok(MachineAction::Complete(
                                PyBytes::new(py, &line).into_any().unbind(),
                            ))
                        }
                    }
                }
            },
            MachineResume::Error(error) => Err(error),
        }
    }
}

fn fastapi_core_call(
    py: Python<'_>,
    app: Py<PyFastApi>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
) -> PyResult<Py<PyAny>> {
    into_python_awaitable(
        py,
        FastApiCall {
            app,
            scope,
            receive,
            send,
            route_index: None,
            frontend_route_index: None,
            frontend_path: None,
            frontend_response_status_override: None,
            websocket_route_index: None,
            request: None,
            websocket: None,
            injected_response: None,
            path_params: Vec::new(),
            pending: None,
            response_status: 200,
            response_body: Vec::new(),
            invocation: None,
            form_request: None,
            form_body: None,
            form_close_started: false,
            form_body_embedded: false,
            form_inputs: None,
            form_query_params: None,
            form_file_reads: VecDeque::new(),
            active_form_file_read: None,
            function_close_continuation: None,
        },
    )
}

struct FastApiCall {
    app: Py<PyFastApi>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
    route_index: Option<usize>,
    frontend_route_index: Option<usize>,
    frontend_path: Option<String>,
    frontend_response_status_override: Option<u16>,
    websocket_route_index: Option<usize>,
    request: Option<Py<PyAny>>,
    websocket: Option<Py<PyAny>>,
    injected_response: Option<Py<PyAny>>,
    path_params: Vec<(String, String)>,
    pending: Option<PendingAction>,
    response_status: u16,
    response_body: Vec<u8>,
    invocation: Option<RequestInvocation>,
    form_request: Option<Py<PyAny>>,
    form_body: Option<Py<PyAny>>,
    form_close_started: bool,
    form_body_embedded: bool,
    form_inputs: Option<Py<PyDict>>,
    form_query_params: Option<QueryParams>,
    form_file_reads: VecDeque<FormFileReadPlan>,
    active_form_file_read: Option<FormFileReadPlan>,
    function_close_continuation: Option<FunctionCloseContinuation>,
}

impl FastApiCall {
    fn request_background_tasks(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.invocation
            .as_ref()
            .and_then(|invocation| invocation.background_tasks.as_ref())
            .map(|tasks| tasks.clone_ref(py))
    }

    fn request_validation_endpoint_context<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let (endpoint, method, path) = {
            let app = self.app.bind(py).borrow();
            if let Some(frontend_index) = self.frontend_route_index {
                let frontend = app
                    .frontend_routes
                    .get(frontend_index)
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?;
                (
                    frontend.dependency_plan.callable.clone_ref(py),
                    "GET".to_owned(),
                    frontend.path.clone(),
                )
            } else {
                let route = app
                    .routes
                    .get(self.route_index.unwrap_or_default())
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
                (
                    route.endpoint.clone_ref(py),
                    route.method.clone(),
                    route.path.clone(),
                )
            }
        };
        let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
        response_endpoint_context(py, endpoint.bind(py), &method, &path, &root_path)
    }

    fn start_returned_response(
        &mut self,
        py: Python<'_>,
        response: &Bound<'_, PyAny>,
    ) -> PyResult<MachineAction> {
        self.close_function_dependency_stack_before_response(
            py,
            FunctionCloseContinuation::ReturnedResponse(response.clone().unbind()),
        )
    }

    fn start_returned_response_after_function_close(
        &mut self,
        py: Python<'_>,
        response: &Bound<'_, PyAny>,
    ) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::ReturnedResponse);
        let awaitable = response.call1((
            self.scope.bind(py),
            self.receive.bind(py),
            self.send.bind(py),
        ))?;
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn close_function_dependency_stack_before_response(
        &mut self,
        py: Python<'_>,
        continuation: FunctionCloseContinuation,
    ) -> PyResult<MachineAction> {
        let exit_stack = self.invocation.as_mut().and_then(|invocation| {
            if invocation.function_dependency_exit_stack_closed {
                None
            } else {
                invocation.function_dependency_exit_stack_closed = true;
                Some(invocation.function_dependency_exit_stack.clone_ref(py))
            }
        });
        let Some(exit_stack) = exit_stack else {
            return self.resume_function_close_continuation(py, continuation);
        };
        self.function_close_continuation = Some(continuation);
        self.pending = Some(PendingAction::FunctionDependencyCloseBeforeResponse);
        exit_stack
            .bind(py)
            .call_method0("aclose")
            .map(Bound::unbind)
            .map(MachineAction::Await)
    }

    fn resume_function_close_continuation(
        &mut self,
        py: Python<'_>,
        continuation: FunctionCloseContinuation,
    ) -> PyResult<MachineAction> {
        match continuation {
            FunctionCloseContinuation::ReturnedResponse(response) => {
                self.start_returned_response_after_function_close(py, response.bind(py))
            }
            FunctionCloseContinuation::SendStart(extra_headers) => {
                self.send_start_after_function_close(py, extra_headers)
            }
        }
    }

    fn dispatch_mounted_app(&mut self, py: Python<'_>) -> PyResult<Option<MachineAction>> {
        let mounted_routes = self
            .app
            .bind(py)
            .borrow()
            .mounted_routes
            .iter()
            .map(|route| route.clone_ref(py))
            .collect::<Vec<_>>();
        let scope = self.scope.bind(py);
        let full_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("FULL")?;
        let partial_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("PARTIAL")?;
        let mut partial_route = None;

        for route in mounted_routes {
            let match_result = route.bind(py).call_method1("matches", (scope,))?;
            let route_match = match_result.get_item(0)?;
            if route_match.is(&partial_match) && partial_route.is_none() {
                partial_route = Some((route.clone_ref(py), match_result.get_item(1)?.unbind()));
            }
            if !route_match.is(&full_match) {
                continue;
            }

            let child_scope = match_result.get_item(1)?;
            scope.call_method1("update", (child_scope,))?;
            let awaitable = route
                .bind(py)
                .call_method1("handle", (scope, self.receive.bind(py), self.send.bind(py)))?;
            self.pending = Some(PendingAction::MountedApp);
            return Ok(Some(MachineAction::Await(awaitable.unbind())));
        }

        if let Some((route, child_scope)) = partial_route {
            scope.call_method1("update", (child_scope.bind(py),))?;
            let awaitable = route
                .bind(py)
                .call_method1("handle", (scope, self.receive.bind(py), self.send.bind(py)))?;
            self.pending = Some(PendingAction::MountedApp);
            return Ok(Some(MachineAction::Await(awaitable.unbind())));
        }

        Ok(None)
    }

    fn dispatch_frontend_route(
        &mut self,
        py: Python<'_>,
        route_path: &str,
        method: &str,
    ) -> PyResult<Option<MachineAction>> {
        let selected = {
            let app = self.app.bind(py).borrow();
            let mut selected: Option<(usize, String, usize)> = None;
            for (index, route) in app.frontend_routes.iter().enumerate() {
                let Some(frontend_path) = frontend_path_for(route_path, &route.path) else {
                    continue;
                };
                let specificity = frontend_path_specificity(&route.path);
                if selected
                    .as_ref()
                    .is_none_or(|(_, _, selected_specificity)| specificity > *selected_specificity)
                {
                    selected = Some((index, frontend_path, specificity));
                }
            }
            selected.map(|(index, path, _)| (index, path))
        };
        let Some((route_index, frontend_path)) = selected else {
            return Ok(None);
        };
        let frontend_path = normalize_frontend_relative_path(&frontend_path);
        let static_files = self
            .app
            .bind(py)
            .borrow()
            .frontend_routes
            .get(route_index)
            .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
            .static_files
            .clone_ref(py);

        if !matches!(method, "GET" | "HEAD") {
            let status_code =
                if frontend_static_resource_exists(py, static_files.bind(py), &frontend_path)? {
                    405
                } else {
                    404
                };
            return Err(frontend_http_error(py, status_code)?);
        }

        self.frontend_route_index = Some(route_index);
        self.frontend_path = Some(frontend_path);
        self.frontend_response_status_override = None;
        self.injected_response = Some(fastapi_response_state(py)?);
        let scope = self.scope.bind(py);
        let fastapi_scope_key = concat!("fast", "api");
        let fastapi_scope =
            scope.call_method1("setdefault", (fastapi_scope_key, PyDict::new(py)))?;
        fastapi_scope.set_item(
            "frontend_path",
            self.frontend_path.as_deref().unwrap_or_default(),
        )?;
        let path_specificity = {
            let app = self.app.bind(py).borrow();
            let frontend = app
                .frontend_routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?;
            frontend_path_specificity(&frontend.path)
        };
        fastapi_scope.set_item("frontend_specificity", path_specificity)?;
        scope.set_item("path_params", PyDict::new(py))?;
        let request_type = py.import("starlette.requests")?.getattr("Request")?;
        let request = request_type.call1((scope, self.receive.bind(py), self.send.bind(py)))?;
        scope.set_item("starlette._exception_request", &request)?;
        self.request = Some(request.unbind());
        let query: Vec<u8> = scope
            .call_method1("get", ("query_string", PyBytes::new(py, b"")))?
            .extract()?;
        self.invocation = Some(RequestInvocation {
            inputs: PyDict::new(py).unbind(),
            query_params: QueryParams::parse(&query),
            request_body: None,
            form_body_embedded: false,
            failures: Vec::new(),
            dependency_cache: HashMap::new(),
            prepared_dependency_values: HashMap::new(),
            dependency_override_cursor: 0,
            dependency_exit_stack: new_dependency_exit_stack(py)?,
            dependency_exit_stack_closed: false,
            function_dependency_exit_stack: new_dependency_exit_stack(py)?,
            function_dependency_exit_stack_closed: false,
            background_tasks: None,
        });
        self.invoke_route(py).map(Some)
    }

    fn start_frontend_response(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let route_index = self
            .frontend_route_index
            .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected frontend"))?;
        let static_files = self
            .app
            .bind(py)
            .borrow()
            .frontend_routes
            .get(route_index)
            .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
            .static_files
            .clone_ref(py);
        if static_files
            .bind(py)
            .getattr("config_checked")?
            .extract::<bool>()?
        {
            return self.get_frontend_response(py, None);
        }
        let awaitable = static_files.bind(py).call_method0("check_config")?;
        self.pending = Some(PendingAction::FrontendConfig);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn get_frontend_response(
        &mut self,
        py: Python<'_>,
        fallback_status_code: Option<u16>,
    ) -> PyResult<MachineAction> {
        let route_index = self
            .frontend_route_index
            .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected frontend"))?;
        let (static_files, path) = {
            let app = self.app.bind(py).borrow();
            let frontend = app
                .frontend_routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?;
            (
                frontend.static_files.clone_ref(py),
                self.frontend_path
                    .clone()
                    .ok_or_else(|| PyRuntimeError::new_err("frontend request path was lost"))?,
            )
        };
        self.frontend_response_status_override = fallback_status_code;
        let awaitable = static_files
            .bind(py)
            .call_method1("get_response", (path, self.scope.bind(py)))?;
        self.pending = Some(PendingAction::FrontendResponse);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn get_frontend_fallback_response(
        &mut self,
        py: Python<'_>,
        fallback: &str,
        status_code: Option<u16>,
    ) -> PyResult<MachineAction> {
        let route_index = self
            .frontend_route_index
            .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected frontend"))?;
        let static_files = self
            .app
            .bind(py)
            .borrow()
            .frontend_routes
            .get(route_index)
            .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
            .static_files
            .clone_ref(py);
        if !frontend_file_is_regular(py, static_files.bind(py), fallback)? {
            let directory = static_files.bind(py).getattr("directory")?;
            let directory_path = python_path_string(py, &directory)?;
            return Err(frontend_fallback_file_error(
                py,
                fallback,
                &directory,
                &directory_path,
            )?);
        }
        let awaitable = static_files
            .bind(py)
            .call_method1("get_response", (fallback, self.scope.bind(py)))?;
        self.frontend_response_status_override = status_code;
        self.pending = Some(PendingAction::FrontendResponse);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn finish_frontend_response(
        &mut self,
        py: Python<'_>,
        response: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let status_override = self.frontend_response_status_override.take();
        let response = response.bind(py);
        if let Some(status_code) = status_override {
            response.setattr("status_code", status_code)?;
        } else if response.getattr("status_code")?.extract::<u16>()? == 404 {
            let fallback = {
                let app = self.app.bind(py).borrow();
                app.frontend_routes
                    .get(self.frontend_route_index.ok_or_else(|| {
                        PyRuntimeError::new_err("ASGI dispatch has no selected frontend")
                    })?)
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
                    .fallback
            };
            match fallback {
                FastApiFrontendFallback::Auto | FastApiFrontendFallback::NotFoundHtml => {}
                FastApiFrontendFallback::IndexHtml => {
                    let request = self
                        .request
                        .as_ref()
                        .ok_or_else(|| PyRuntimeError::new_err("frontend request was lost"))?;
                    if frontend_is_navigation_request(py, request.bind(py))? {
                        return self.get_frontend_fallback_response(py, "index.html", None);
                    }
                    return Err(frontend_http_error(py, 404)?);
                }
                FastApiFrontendFallback::None => return Err(frontend_http_error(py, 404)?),
            }
        }
        let background_tasks = self.request_background_tasks(py);
        attach_response_background_if_missing(
            response,
            background_tasks.as_ref().map(|tasks| tasks.bind(py)),
        )?;
        if let Some(injected_response) = self.injected_response.as_ref() {
            let response_headers = response.getattr("headers")?.getattr("raw")?;
            let injected_headers = injected_response
                .bind(py)
                .getattr("headers")?
                .getattr("raw")?;
            response_headers.call_method1("extend", (injected_headers,))?;
        }
        let awaitable = response.call1((
            self.scope.bind(py),
            self.receive.bind(py),
            self.send.bind(py),
        ))?;
        self.pending = Some(PendingAction::FrontendAsgiResponse);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn frontend_response_failed(
        &mut self,
        py: Python<'_>,
        error: PyErr,
    ) -> PyResult<MachineAction> {
        let value = error.value(py);
        let http_exception = py
            .import("starlette.exceptions")?
            .getattr("HTTPException")?;
        if !value.is_instance(&http_exception)?
            || value.getattr("status_code")?.extract::<u16>()? != 404
        {
            return self.route_exception(py, error);
        }
        let fallback = {
            let app = self.app.bind(py).borrow();
            app.frontend_routes
                .get(self.frontend_route_index.ok_or_else(|| {
                    PyRuntimeError::new_err("ASGI dispatch has no selected frontend")
                })?)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
                .fallback
        };
        match fallback {
            FastApiFrontendFallback::Auto => {
                if frontend_file_is_regular(
                    py,
                    self.frontend_static_files(py)?.bind(py),
                    "404.html",
                )? {
                    return self.get_frontend_fallback_response(py, "404.html", Some(404));
                }
                let request = self
                    .request
                    .as_ref()
                    .ok_or_else(|| PyRuntimeError::new_err("frontend request was lost"))?;
                if frontend_is_navigation_request(py, request.bind(py))?
                    && frontend_file_is_regular(
                        py,
                        self.frontend_static_files(py)?.bind(py),
                        "index.html",
                    )?
                {
                    return self.get_frontend_fallback_response(py, "index.html", None);
                }
                Err(error)
            }
            FastApiFrontendFallback::IndexHtml => {
                let request = self
                    .request
                    .as_ref()
                    .ok_or_else(|| PyRuntimeError::new_err("frontend request was lost"))?;
                if frontend_is_navigation_request(py, request.bind(py))? {
                    self.get_frontend_fallback_response(py, "index.html", None)
                } else {
                    Err(error)
                }
            }
            FastApiFrontendFallback::NotFoundHtml => {
                self.get_frontend_fallback_response(py, "404.html", Some(404))
            }
            FastApiFrontendFallback::None => Err(error),
        }
    }

    fn frontend_static_files(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let route_index = self
            .frontend_route_index
            .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected frontend"))?;
        self.app
            .bind(py)
            .borrow()
            .frontend_routes
            .get(route_index)
            .map(|frontend| frontend.static_files.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))
    }

    fn redirect_http_slash(
        &mut self,
        py: Python<'_>,
        path: &str,
        root_path: &str,
        method: &str,
    ) -> PyResult<Option<MachineAction>> {
        let redirect_path = {
            let app = self.app.bind(py).borrow();
            if !app.redirect_slashes {
                return Ok(None);
            }
            app.docs_router
                .find_slash_redirect_path(path, root_path, method)
                .or_else(|| app.router.find_slash_redirect_path(path, root_path, method))
        };
        let Some(redirect_path) = redirect_path else {
            return Ok(None);
        };

        let redirect_scope = PyDict::new(py);
        redirect_scope.call_method1("update", (self.scope.bind(py),))?;
        redirect_scope.set_item("path", redirect_path)?;
        let url_kwargs = PyDict::new(py);
        url_kwargs.set_item("scope", redirect_scope)?;
        let redirect_url = py
            .import("starlette.datastructures")?
            .getattr("URL")?
            .call((), Some(&url_kwargs))?;
        let response = py
            .import("starlette.responses")?
            .getattr("RedirectResponse")?
            .call1((redirect_url,))?;
        self.start_returned_response(py, &response).map(Some)
    }

    fn begin(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let scope_type = parse_scope_string(scope, "type", "http")?;
        if scope_type == "lifespan" {
            return self.receive_lifespan(py);
        }
        if scope_type == "websocket" {
            return self.begin_websocket(py);
        }
        if scope_type != "http" {
            return Err(PyValueError::new_err(format!(
                "FastAPI-RS currently supports HTTP and lifespan ASGI scopes, not {scope_type:?}"
            )));
        }
        let path = parse_scope_string(scope, "path", "/")?;
        let method = parse_scope_string(scope, "method", "GET")?;
        let route_path = py
            .import("starlette.routing")?
            .getattr("_get_route_path")?
            .call1((scope,))?
            .extract::<String>()?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let (openapi_url, title, init_oauth) = {
            let app = self.app.bind(py).borrow();
            (
                app.openapi_url.clone(),
                app.title.clone(),
                app.swagger_ui_init_oauth
                    .as_ref()
                    .map(|configuration| configuration.clone_ref(py)),
            )
        };
        if !openapi_url.is_empty() && route_path == openapi_url && method == "GET" {
            let root_path = root_path.trim_end_matches('/');
            let document = {
                let app = self.app.bind(py).borrow();
                openapi_document_for_root_path(py, app.openapi(py)?, root_path)?
            };
            self.response_status = 200;
            self.response_body = json_bytes(py, document.bind(py))?;
            return self.send_start(py);
        }
        if !openapi_url.is_empty() {
            let docs_match = self
                .app
                .bind(py)
                .borrow()
                .docs_router
                .matches_detailed_with_root_path(&path, &root_path, &method);
            match docs_match {
                DetailedRouteMatch::Matched { route_index, .. } => {
                    let docs_route = self
                        .app
                        .bind(py)
                        .borrow()
                        .docs_routes
                        .get(route_index)
                        .copied()
                        .ok_or_else(|| {
                            PyRuntimeError::new_err("matched FastAPI docs route was lost")
                        })?;
                    let docs_root_path = root_path.trim_end_matches('/');
                    let init_oauth_bound = init_oauth.as_ref().map(|value| value.bind(py));
                    let html = match docs_route {
                        FastApiDocsRoute::SwaggerUi => docs::swagger_ui_html_with_init_oauth(
                            py,
                            &format!("{docs_root_path}{openapi_url}"),
                            &format!("{docs_root_path}/docs/oauth2-redirect"),
                            &format!("{title} - Swagger UI"),
                            init_oauth_bound,
                        )?,
                        FastApiDocsRoute::OAuth2Redirect => docs::oauth2_redirect_html().to_owned(),
                        FastApiDocsRoute::ReDoc => docs::redoc_html(
                            &format!("{docs_root_path}{openapi_url}"),
                            &format!("{title} - ReDoc"),
                        ),
                    };
                    let response = py
                        .import("starlette.responses")?
                        .getattr("HTMLResponse")?
                        .call1((html,))?;
                    return self.start_returned_response(py, &response);
                }
                DetailedRouteMatch::MethodNotAllowed {
                    allowed_methods, ..
                } => {
                    let headers = PyDict::new(py);
                    headers.set_item("Allow", allowed_methods.join(", "))?;
                    let content = PyDict::new(py);
                    content.set_item("detail", "Method Not Allowed")?;
                    let kwargs = PyDict::new(py);
                    kwargs.set_item("status_code", 405)?;
                    kwargs.set_item("headers", headers)?;
                    let response = py
                        .import("starlette.responses")?
                        .getattr("JSONResponse")?
                        .call((content,), Some(&kwargs))?;
                    return self.start_returned_response(py, &response);
                }
                DetailedRouteMatch::NotFound => {}
            }
        }

        let match_result = self
            .app
            .bind(py)
            .borrow()
            .router
            .matches(&path, &root_path, &method);
        match match_result {
            FastApiOperationMatch::Matched {
                operation_index,
                path_params,
            } => {
                self.route_index = Some(operation_index);
                self.path_params = path_params;
                self.injected_response = Some(fastapi_response_state(py)?);
                let (route_scope, effective_route_context) = {
                    let app = self.app.bind(py).borrow();
                    let route = app.routes.get(operation_index).ok_or_else(|| {
                        PyRuntimeError::new_err("selected FastAPI route was lost")
                    })?;
                    (
                        route.route_scope.clone_ref(py),
                        route
                            .effective_route_context
                            .as_ref()
                            .map(|context| context.clone_ref(py)),
                    )
                };
                scope.set_item("route", route_scope)?;
                if let Some(effective_route_context) = effective_route_context {
                    let fastapi_scope = scope
                        .call_method1("setdefault", (concat!("fast", "api"), PyDict::new(py)))?;
                    fastapi_scope.set_item("effective_route_context", effective_route_context)?;
                }
                let converted_path_params = PyDict::new(py);
                {
                    let app = self.app.bind(py).borrow();
                    let route = app.routes.get(operation_index).ok_or_else(|| {
                        PyRuntimeError::new_err("selected FastAPI route was lost")
                    })?;
                    let convertors = route.param_convertors.bind(py);
                    for (name, value) in &self.path_params {
                        let convertor = convertors.get_item(name)?.ok_or_else(|| {
                            PyRuntimeError::new_err(
                                "matched FastAPI route is missing a path convertor",
                            )
                        })?;
                        converted_path_params
                            .set_item(name, convertor.call_method1("convert", (value,))?)?;
                    }
                }
                scope.set_item("path_params", converted_path_params)?;
                let request_type = py.import("starlette.requests")?.getattr("Request")?;
                let request =
                    request_type.call1((scope, self.receive.bind(py), self.send.bind(py)))?;
                scope.set_item("starlette._exception_request", &request)?;
                self.request = Some(request.unbind());
                let (has_form_inputs, has_body_inputs) = {
                    let app = self.app.bind(py).borrow();
                    let route = app.routes.get(operation_index).ok_or_else(|| {
                        PyRuntimeError::new_err("selected FastAPI route was lost")
                    })?;
                    (
                        route.plan.has_form_inputs(),
                        !route.plan.all_body_parameters().is_empty(),
                    )
                };
                if has_form_inputs {
                    self.receive_form(py)
                } else if has_body_inputs {
                    self.receive_http_body(py)
                } else {
                    self.invoke_http_route(py, &[], false)
                }
            }
            FastApiOperationMatch::MethodNotAllowed {
                allowed_methods, ..
            } => {
                let headers = PyDict::new(py);
                headers.set_item("Allow", allowed_methods.join(", "))?;
                let content = PyDict::new(py);
                content.set_item("detail", "Method Not Allowed")?;
                let kwargs = PyDict::new(py);
                kwargs.set_item("status_code", 405)?;
                kwargs.set_item("headers", headers)?;
                let response = py
                    .import("starlette.responses")?
                    .getattr("JSONResponse")?
                    .call((content,), Some(&kwargs))?;
                self.start_returned_response(py, &response)
            }
            FastApiOperationMatch::NotFound => {
                if let Some(action) = self.dispatch_mounted_app(py)? {
                    return Ok(action);
                }
                if let Some(action) = self.redirect_http_slash(py, &path, &root_path, &method)? {
                    return Ok(action);
                }
                if let Some(action) = self.dispatch_frontend_route(py, &route_path, &method)? {
                    return Ok(action);
                }
                let exception = py
                    .import("starlette.exceptions")?
                    .getattr("HTTPException")?
                    .call1((404,))?;
                Err(PyErr::from_value(exception))
            }
        }
    }

    fn begin_websocket(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let path = parse_scope_string(scope, "path", "/")?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let match_result = self
            .app
            .bind(py)
            .borrow()
            .websocket_router
            .matches(&path, &root_path, "GET");
        let FastApiOperationMatch::Matched {
            operation_index,
            path_params,
        } = match_result
        else {
            return self.close_unmatched_websocket(py);
        };
        let (raw_route, route_scope) = {
            let app = self.app.bind(py).borrow();
            let route = app.websocket_routes.get(operation_index).ok_or_else(|| {
                PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
            })?;
            (route.raw, route.route_scope.clone_ref(py))
        };
        if raw_route {
            let full_match = py
                .import("starlette.routing")?
                .getattr("Match")?
                .getattr("FULL")?;
            let match_result = route_scope.bind(py).call_method1("matches", (scope,))?;
            if !match_result.get_item(0)?.is(&full_match) {
                return self.close_unmatched_websocket(py);
            }
            scope.call_method1("update", (match_result.get_item(1)?,))?;
            let awaitable = route_scope
                .bind(py)
                .call_method1("handle", (scope, self.receive.bind(py), self.send.bind(py)))?;
            self.pending = Some(PendingAction::MountedApp);
            return Ok(MachineAction::Await(awaitable.unbind()));
        }
        self.websocket_route_index = Some(operation_index);
        self.injected_response = Some(fastapi_response_state(py)?);
        self.path_params = path_params.clone();
        let route_scope = {
            let app = self.app.bind(py).borrow();
            app.websocket_routes
                .get(operation_index)
                .ok_or_else(|| {
                    PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
                })?
                .route_scope
                .clone_ref(py)
        };
        scope.set_item("route", route_scope)?;

        let query: Vec<u8> = scope
            .call_method1("get", ("query_string", PyBytes::new(py, b"")))?
            .extract()?;
        let headers: Vec<(Vec<u8>, Vec<u8>)> = scope
            .call_method1("get", ("headers", PyList::empty(py)))?
            .extract()?;
        let inputs = {
            let app = self.app.bind(py).borrow();
            let route = app.websocket_routes.get(operation_index).ok_or_else(|| {
                PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
            })?;
            let convertors = route.param_convertors.bind(py);
            let native_path_params = PyDict::new(py);
            for (name, value) in &path_params {
                let convertor = convertors.get_item(name)?.ok_or_else(|| {
                    PyRuntimeError::new_err("matched WebSocket route is missing a path convertor")
                })?;
                let converted = convertor.call_method1("convert", (value.as_str(),))?;
                native_path_params.set_item(name, converted)?;
            }
            scope.set_item("path_params", native_path_params)?;
            app.websocket_router
                .resolve_inputs(&path, &root_path, "GET", &query, headers, &[])
        };
        let websocket_type = py.import("starlette.websockets")?.getattr("WebSocket")?;
        self.websocket = Some(
            websocket_type
                .call1((scope, self.receive.bind(py), self.send.bind(py)))?
                .unbind(),
        );
        let values = match decode_input_values(py, inputs, false) {
            Ok(values) => values,
            Err(InputDecodeError::Other(error)) => return Err(error),
            Err(InputDecodeError::JsonValidation(error) | InputDecodeError::BodyParse(error)) => {
                return Err(error);
            }
        };
        self.invocation = Some(RequestInvocation {
            inputs: values,
            query_params: QueryParams::parse(&query),
            request_body: None,
            form_body_embedded: false,
            failures: Vec::new(),
            dependency_cache: HashMap::new(),
            prepared_dependency_values: HashMap::new(),
            dependency_override_cursor: 0,
            dependency_exit_stack: new_dependency_exit_stack(py)?,
            dependency_exit_stack_closed: false,
            function_dependency_exit_stack: new_dependency_exit_stack(py)?,
            function_dependency_exit_stack_closed: false,
            background_tasks: None,
        });
        self.invoke_route(py)
    }

    fn close_unmatched_websocket(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let close_type = py
            .import("starlette.websockets")?
            .getattr("WebSocketClose")?;
        let close = close_type.call0()?;
        let awaitable = close.call1((
            self.scope.bind(py),
            self.receive.bind(py),
            self.send.bind(py),
        ))?;
        self.pending = Some(PendingAction::WebSocketClose);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn close_websocket_exception(
        &mut self,
        py: Python<'_>,
        error: PyErr,
    ) -> PyResult<MachineAction> {
        let value = error.value(py);
        let exception_type = py
            .import("starlette.exceptions")?
            .getattr("WebSocketException")?;
        if !value.is_instance(&exception_type)? {
            return Err(error);
        }
        let websocket = self
            .websocket
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("FastAPI WebSocket was not initialized"))?;
        let awaitable = websocket
            .bind(py)
            .call_method1("close", (value.getattr("code")?, value.getattr("reason")?))?;
        if !is_awaitable(py, &awaitable)? {
            return Err(PyTypeError::new_err(
                "Starlette WebSocket.close must return an awaitable",
            ));
        }
        self.pending = Some(PendingAction::WebSocketClose);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn receive_http_body(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let request = self
            .request
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("HTTP request was not initialized"))?;
        self.pending = Some(PendingAction::RequestBody);
        request
            .bind(py)
            .call_method0("body")
            .map(Bound::unbind)
            .map(MachineAction::Await)
    }

    fn receive_form(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let request = self
            .request
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("HTTP request was not initialized"))?
            .bind(py);
        let form_awaitable = request.call_method0("form")?;
        self.form_request = Some(request.clone().unbind());
        self.pending = Some(PendingAction::FormParse);
        Ok(MachineAction::Await(form_awaitable.unbind()))
    }

    fn receive_lifespan(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let context = self.app.bind(py).borrow().lifespan.context(py);
        let awaitable = py
            .import("starlette_rs_py._core")?
            .getattr("router_lifespan")?
            .call1((
                context,
                self.scope.bind(py),
                self.receive.bind(py),
                self.send.bind(py),
            ))?;
        self.pending = Some(PendingAction::LifespanCompletion);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn receive_request_body(&mut self, py: Python<'_>, body: Py<PyAny>) -> PyResult<MachineAction> {
        let body = body.bind(py).extract::<Vec<u8>>()?;
        let scope = self.scope.bind(py);
        let headers: Vec<(Vec<u8>, Vec<u8>)> = scope
            .call_method1("get", ("headers", PyList::empty(py)))?
            .extract()?;
        let strict_content_type = self
            .route_index
            .and_then(|index| {
                self.app
                    .bind(py)
                    .borrow()
                    .routes
                    .get(index)
                    .and_then(|route| route.strict_content_type)
            })
            .unwrap_or(true);
        self.invoke_http_route(
            py,
            &body,
            should_parse_json_body(&headers, strict_content_type),
        )
    }

    fn invoke_http_route(
        &mut self,
        py: Python<'_>,
        body: &[u8],
        parse_json_body: bool,
    ) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let path = parse_scope_string(scope, "path", "/")?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let method = parse_scope_string(scope, "method", "GET")?;
        let query: Vec<u8> = scope
            .call_method1("get", ("query_string", PyBytes::new(py, b"")))?
            .extract()?;
        let query_params = QueryParams::parse(&query);
        let headers: Vec<(Vec<u8>, Vec<u8>)> = scope
            .call_method1("get", ("headers", PyList::empty(py)))?
            .extract()?;
        let inputs = self
            .app
            .bind(py)
            .borrow()
            .router
            .resolve_inputs(&path, &root_path, &method, &query, headers, body);
        let request_has_body = inputs
            .inputs
            .iter()
            .any(|input| input.location == FastApiInputLocation::Body);
        let values = match decode_input_values(py, inputs, parse_json_body) {
            Ok(values) => values,
            Err(InputDecodeError::JsonValidation(error)) => {
                let response_body = json_decode_validation_response_body(py, &error)?;
                let details = response_body.bind(py).get_item("detail")?;
                let body = error.value(py).getattr("doc")?;
                let endpoint_ctx = self.request_validation_endpoint_context(py)?;
                let validation_error = crate::errors::request_validation_error(
                    py,
                    &details,
                    Some(&body),
                    Some(&endpoint_ctx),
                )?;
                if self.has_registered_exception_handler(py, &validation_error)? {
                    return self.route_exception(py, validation_error);
                }
                self.response_status = 422;
                self.response_body = json_bytes(py, response_body.bind(py))?;
                return self.send_start(py);
            }
            Err(InputDecodeError::BodyParse(_error)) => {
                self.response_status = 400;
                self.response_body = json_bytes(py, bad_request_body_response_body(py)?.bind(py))?;
                return self.send_start(py);
            }
            Err(InputDecodeError::Other(error)) => return Err(error),
        };
        let request_body = if request_has_body && !body.is_empty() {
            let body = PyBytes::new(py, body);
            let body = if parse_json_body {
                py.import("json")?.getattr("loads")?.call1((body,))?
            } else {
                body.into_any()
            };
            Some(body.unbind())
        } else {
            None
        };
        self.invocation = Some(RequestInvocation {
            inputs: values,
            query_params,
            request_body,
            form_body_embedded: false,
            failures: Vec::new(),
            dependency_cache: HashMap::new(),
            prepared_dependency_values: HashMap::new(),
            dependency_override_cursor: 0,
            dependency_exit_stack: new_dependency_exit_stack(py)?,
            dependency_exit_stack_closed: false,
            function_dependency_exit_stack: new_dependency_exit_stack(py)?,
            function_dependency_exit_stack_closed: false,
            background_tasks: None,
        });
        self.invoke_route(py)
    }

    fn receive_form_data(&mut self, py: Python<'_>, form: Py<PyAny>) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let path = parse_scope_string(scope, "path", "/")?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let method = parse_scope_string(scope, "method", "GET")?;
        let query: Vec<u8> = scope
            .call_method1("get", ("query_string", PyBytes::new(py, b"")))?
            .extract()?;
        let query_params = QueryParams::parse(&query);
        let headers: Vec<(Vec<u8>, Vec<u8>)> = scope
            .call_method1("get", ("headers", PyList::empty(py)))?
            .extract()?;
        let inputs = self.app.bind(py).borrow().router.resolve_inputs(
            &path,
            &root_path,
            &method,
            &query,
            headers,
            &[],
        );
        let values = match decode_input_values(py, inputs, false) {
            Ok(values) => values,
            Err(InputDecodeError::Other(error)) => return Err(error),
            Err(InputDecodeError::JsonValidation(error) | InputDecodeError::BodyParse(error)) => {
                return Err(error);
            }
        };
        let route_index = self
            .route_index
            .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected route"))?;
        {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            self.form_body_embedded =
                form_body_should_embed(py, &route.plan.all_body_parameters())?;
            route.plan.populate_form_inputs(
                py,
                form.bind(py),
                values.bind(py),
                self.form_body_embedded,
                &mut self.form_file_reads,
            )?;
        }
        self.form_inputs = Some(values);
        self.form_query_params = Some(query_params);
        self.form_body = Some(form.clone_ref(py));
        self.advance_form_file_reads(py)
    }

    fn advance_form_file_reads(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        loop {
            if self.active_form_file_read.is_none() {
                self.active_form_file_read = self.form_file_reads.pop_front();
            }
            let next_awaitable = self
                .active_form_file_read
                .as_mut()
                .and_then(|plan| plan.awaitables.pop_front());
            if let Some(awaitable) = next_awaitable {
                self.pending = Some(PendingAction::FormFileRead);
                return Ok(MachineAction::Await(awaitable));
            }
            if let Some(plan) = self.active_form_file_read.take() {
                let values = PyList::new(py, plan.values.iter().map(|value| value.bind(py)))?;
                let value = if plan.sequence {
                    sequence_value_for_annotation(py, plan.annotation.bind(py), &values)?
                } else {
                    values.get_item(0)?
                };
                self.form_inputs
                    .as_ref()
                    .ok_or_else(|| PyRuntimeError::new_err("form inputs were not retained"))?
                    .bind(py)
                    .set_item(&plan.name, value)?;
                continue;
            }
            let inputs = self
                .form_inputs
                .take()
                .ok_or_else(|| PyRuntimeError::new_err("form inputs were not retained"))?;
            let query_params = self.form_query_params.take().ok_or_else(|| {
                PyRuntimeError::new_err("form query parameters were not retained")
            })?;
            self.invocation = Some(RequestInvocation {
                inputs,
                query_params,
                request_body: self.form_body.take(),
                form_body_embedded: self.form_body_embedded,
                failures: Vec::new(),
                dependency_cache: HashMap::new(),
                prepared_dependency_values: HashMap::new(),
                dependency_override_cursor: 0,
                dependency_exit_stack: new_dependency_exit_stack(py)?,
                dependency_exit_stack_closed: false,
                function_dependency_exit_stack: new_dependency_exit_stack(py)?,
                function_dependency_exit_stack_closed: false,
                background_tasks: None,
            });
            return self.invoke_route(py);
        }
    }

    fn selected_body_fields_embedded(&self, py: Python<'_>) -> PyResult<bool> {
        let app = self.app.bind(py).borrow();
        let plan = if let Some(route_index) = self.frontend_route_index {
            &app.frontend_routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
                .dependency_plan
        } else if let Some(route_index) = self.websocket_route_index {
            app.websocket_routes
                .get(route_index)
                .ok_or_else(|| {
                    PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
                })?
                .plan
                .as_ref()
                .ok_or_else(|| PyRuntimeError::new_err("raw WebSocket route entered FastAPI"))?
        } else {
            let route_index = self
                .route_index
                .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected route"))?;
            &app.routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?
                .plan
        };
        Ok(body_fields_embedded(&plan.all_body_parameters()))
    }

    fn invoke_route(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        if self.websocket_route_index.is_none()
            && self.frontend_route_index.is_none()
            && self.route_index.is_none()
        {
            return Err(PyRuntimeError::new_err(
                "ASGI dispatch has no selected route",
            ));
        }
        let route_body_fields_embedded = self.selected_body_fields_embedded(py)?;
        self.pending = Some(PendingAction::RouteInvocation);
        let websocket = self.websocket.as_ref().map(|socket| socket.bind(py));
        let request = self.request.as_ref().map(|request| request.bind(py));
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.bind(py));
        let invocation = self
            .invocation
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("request invocation state was lost"))?;
        let (plan, dependency_overrides) = {
            let app = self.app.bind(py).borrow();
            let plan = if let Some(route_index) = self.frontend_route_index {
                &app.frontend_routes
                    .get(route_index)
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
                    .dependency_plan
            } else if let Some(route_index) = self.websocket_route_index {
                app.websocket_routes
                    .get(route_index)
                    .ok_or_else(|| {
                        PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
                    })?
                    .plan
                    .as_ref()
                    .ok_or_else(|| PyRuntimeError::new_err("raw WebSocket route entered FastAPI"))?
            } else {
                let route_index = self.route_index.ok_or_else(|| {
                    PyRuntimeError::new_err("ASGI dispatch has no selected HTTP route")
                })?;
                &app.routes
                    .get(route_index)
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?
                    .plan
            };
            (plan.clone_ref(py), app.dependency_overrides.clone_ref(py))
        };
        let route_invocation = {
            let mut context = InvocationContext {
                py,
                inputs: invocation.inputs.bind(py),
                request,
                websocket,
                response: injected_response,
                query_params: &invocation.query_params,
                body_fields_embedded: invocation.form_body_embedded || route_body_fields_embedded,
                form_body_embedded: invocation.form_body_embedded,
                failures: &mut invocation.failures,
                dependency_overrides: dependency_overrides.bind(py),
                dependency_cache: &mut invocation.dependency_cache,
                prepared_dependency_values: &mut invocation.prepared_dependency_values,
                dependency_override_cursor: &mut invocation.dependency_override_cursor,
                dependency_exit_stack: invocation.dependency_exit_stack.bind(py),
                function_dependency_exit_stack: invocation.function_dependency_exit_stack.bind(py),
                background_tasks: &mut invocation.background_tasks,
            };
            match plan.prepare_direct_dependency_overrides(&mut context)? {
                OverridePreparation::AwaitDependencyGraph { awaitable, graph } => {
                    RouteInvocation::AwaitDependencyGraph { awaitable, graph }
                }
                OverridePreparation::Await {
                    awaitable,
                    cache_key,
                    edge_index,
                } => RouteInvocation::AwaitDependency {
                    awaitable,
                    cache_key,
                    edge_index,
                },
                OverridePreparation::AwaitSubdependency {
                    awaitable,
                    parent_plan,
                    cache_key,
                    edge_index,
                } => RouteInvocation::AwaitOverrideSubdependency {
                    awaitable,
                    parent_plan,
                    cache_key,
                    edge_index,
                },
                OverridePreparation::Invalid => RouteInvocation::Ready(None),
                OverridePreparation::Ready => {
                    RouteInvocation::Ready(plan.invoke(&mut context, None, None)?)
                }
            }
        };
        match route_invocation {
            RouteInvocation::AwaitDependencyGraph { awaitable, graph } => {
                self.pending = Some(PendingAction::DependencyGraph(graph));
                Ok(MachineAction::Await(awaitable))
            }
            RouteInvocation::AwaitDependency {
                awaitable,
                cache_key,
                edge_index,
            } => {
                self.pending = Some(PendingAction::Dependency {
                    cache_key,
                    edge_index,
                });
                Ok(MachineAction::Await(awaitable))
            }
            RouteInvocation::AwaitOverrideSubdependency {
                awaitable,
                parent_plan,
                cache_key,
                edge_index,
            } => {
                self.pending = Some(PendingAction::OverrideSubdependency {
                    parent_plan,
                    cache_key,
                    edge_index,
                });
                Ok(MachineAction::Await(awaitable))
            }
            RouteInvocation::Ready(Some(endpoint_result)) => {
                if self.websocket_route_index.is_some() {
                    if is_awaitable(py, endpoint_result.bind(py))? {
                        self.pending = Some(PendingAction::WebSocketEndpoint);
                        Ok(MachineAction::Await(endpoint_result))
                    } else {
                        Err(PyTypeError::new_err(
                            "FastAPI WebSocket endpoints must return an awaitable",
                        ))
                    }
                } else {
                    self.pending = Some(PendingAction::Endpoint);
                    if is_awaitable(py, endpoint_result.bind(py))? {
                        Ok(MachineAction::Await(endpoint_result))
                    } else {
                        self.finish_endpoint(py, endpoint_result)
                    }
                }
            }
            RouteInvocation::Ready(None) => {
                let (has_failures, failures) = {
                    let invocation = self.invocation.as_ref().ok_or_else(|| {
                        PyRuntimeError::new_err("request invocation state was lost")
                    })?;
                    (
                        !invocation.failures.is_empty(),
                        validation_error_details(py, &invocation.failures)?,
                    )
                };
                if has_failures {
                    if self.websocket_route_index.is_some() {
                        let reason = jsonable_encoder_default(py, &failures)?;
                        let websocket = self.websocket.as_ref().ok_or_else(|| {
                            PyRuntimeError::new_err("FastAPI WebSocket was not initialized")
                        })?;
                        let kwargs = PyDict::new(py);
                        kwargs.set_item("code", 1008)?;
                        kwargs.set_item("reason", reason)?;
                        let close = websocket.bind(py).call_method("close", (), Some(&kwargs))?;
                        if !is_awaitable(py, &close)? {
                            return Err(PyTypeError::new_err(
                                "Starlette WebSocket.close must return an awaitable",
                            ));
                        }
                        self.pending = Some(PendingAction::WebSocketClose);
                        return Ok(MachineAction::Await(close.unbind()));
                    }

                    let request_body = self
                        .invocation
                        .as_ref()
                        .and_then(|invocation| invocation.request_body.as_ref())
                        .map(|body| body.bind(py));
                    let endpoint_ctx = self.request_validation_endpoint_context(py)?;
                    let error = crate::errors::request_validation_error(
                        py,
                        &failures,
                        request_body,
                        Some(&endpoint_ctx),
                    )?;
                    if self.has_registered_exception_handler(py, &error)? {
                        return self.route_exception(py, error);
                    }

                    self.response_status = 422;
                    self.response_body = json_bytes(
                        py,
                        validation_response_body_from_details(py, &failures)?.bind(py),
                    )?;
                    self.send_start(py)
                } else {
                    Err(PyRuntimeError::new_err(
                        "request invocation completed without a callable result or validation failure",
                    ))
                }
            }
        }
    }

    fn dependency_resumed(
        &mut self,
        py: Python<'_>,
        cache_key: DependencyCacheKey,
        edge_index: usize,
        value: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let invocation = self
            .invocation
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("request invocation state was lost"))?;
        invocation
            .dependency_cache
            .entry(cache_key)
            .or_insert_with(|| value.clone_ref(py));
        invocation
            .prepared_dependency_values
            .insert(edge_index, value);
        self.invoke_route(py)
    }

    fn dependency_graph_resumed(
        &mut self,
        py: Python<'_>,
        mut graph: DependencyExecutionGraph,
        value: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let request = self.request.as_ref().map(|request| request.bind(py));
        let websocket = self.websocket.as_ref().map(|socket| socket.bind(py));
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.bind(py));
        let route_body_fields_embedded = self.selected_body_fields_embedded(py)?;
        let advance = {
            let invocation = self
                .invocation
                .as_mut()
                .ok_or_else(|| PyRuntimeError::new_err("request invocation state was lost"))?;
            let app = self.app.bind(py).borrow();
            let mut context = InvocationContext {
                py,
                inputs: invocation.inputs.bind(py),
                request,
                websocket,
                response: injected_response,
                query_params: &invocation.query_params,
                body_fields_embedded: invocation.form_body_embedded || route_body_fields_embedded,
                form_body_embedded: invocation.form_body_embedded,
                failures: &mut invocation.failures,
                dependency_overrides: app.dependency_overrides.bind(py),
                dependency_cache: &mut invocation.dependency_cache,
                prepared_dependency_values: &mut invocation.prepared_dependency_values,
                dependency_override_cursor: &mut invocation.dependency_override_cursor,
                dependency_exit_stack: invocation.dependency_exit_stack.bind(py),
                function_dependency_exit_stack: invocation.function_dependency_exit_stack.bind(py),
                background_tasks: &mut invocation.background_tasks,
            };
            graph.resume(&mut context, value)?
        };
        match advance {
            DependencyGraphAdvance::Await(awaitable) => {
                self.pending = Some(PendingAction::DependencyGraph(Box::new(graph)));
                Ok(MachineAction::Await(awaitable))
            }
            DependencyGraphAdvance::Ready | DependencyGraphAdvance::Invalid => {
                self.invoke_route(py)
            }
        }
    }

    fn override_subdependency_resumed(
        &mut self,
        py: Python<'_>,
        parent_plan: CallablePlan,
        cache_key: DependencyCacheKey,
        edge_index: usize,
        subdependency_value: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::RouteInvocation);
        let mut prepared_dependencies = HashMap::new();
        prepared_dependencies.insert(0, subdependency_value);
        let request = self.request.as_ref().map(|request| request.bind(py));
        let websocket = self.websocket.as_ref().map(|socket| socket.bind(py));
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.bind(py));
        let route_body_fields_embedded = self.selected_body_fields_embedded(py)?;
        let parent_result = {
            let invocation = self
                .invocation
                .as_mut()
                .ok_or_else(|| PyRuntimeError::new_err("request invocation state was lost"))?;
            let app = self.app.bind(py).borrow();
            let mut context = InvocationContext {
                py,
                inputs: invocation.inputs.bind(py),
                request,
                websocket,
                response: injected_response,
                query_params: &invocation.query_params,
                body_fields_embedded: invocation.form_body_embedded || route_body_fields_embedded,
                form_body_embedded: invocation.form_body_embedded,
                failures: &mut invocation.failures,
                dependency_overrides: app.dependency_overrides.bind(py),
                dependency_cache: &mut invocation.dependency_cache,
                prepared_dependency_values: &mut invocation.prepared_dependency_values,
                dependency_override_cursor: &mut invocation.dependency_override_cursor,
                dependency_exit_stack: invocation.dependency_exit_stack.bind(py),
                function_dependency_exit_stack: invocation.function_dependency_exit_stack.bind(py),
                background_tasks: &mut invocation.background_tasks,
            };
            parent_plan.invoke_with_prepared_dependencies(&mut context, &prepared_dependencies)?
        };
        let Some(parent_result) = parent_result else {
            return self.invoke_route(py);
        };
        if is_awaitable(py, parent_result.bind(py))? {
            self.pending = Some(PendingAction::Dependency {
                cache_key,
                edge_index,
            });
            Ok(MachineAction::Await(parent_result))
        } else {
            self.dependency_resumed(py, cache_key, edge_index, parent_result)
        }
    }

    fn finish_endpoint(&mut self, py: Python<'_>, result: Py<PyAny>) -> PyResult<MachineAction> {
        if self.frontend_route_index.is_some() {
            return self.start_frontend_response(py);
        }
        let response_type = py.import("starlette.responses")?.getattr("Response")?;
        if result.bind(py).is_instance(&response_type)? {
            // Starlette responses own their status, headers, body, and ASGI send path.
            let background_tasks = self.request_background_tasks(py);
            attach_response_background_if_missing(
                result.bind(py),
                background_tasks.as_ref().map(|tasks| tasks.bind(py)),
            )?;
            return self.start_returned_response(py, result.bind(py));
        }

        let (generator_kind, response_class, sse_stream, status_code, stream_serializer) = {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(self.route_index.unwrap_or_default())
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            let stream_serializer = if let Some(stream_item_type) = route.stream_item_type.as_ref()
            {
                let adapter = py
                    .import("pydantic")?
                    .getattr("TypeAdapter")?
                    .call1((stream_item_type.bind(py),))?
                    .unbind();
                let validation_kwargs = PyDict::new(py);
                validation_kwargs.set_item("from_attributes", true)?;
                let serialization_kwargs = PyDict::new(py);
                serialization_kwargs.set_item("by_alias", route.response_model_by_alias)?;
                serialization_kwargs
                    .set_item("exclude_unset", route.response_model_exclude_unset)?;
                serialization_kwargs
                    .set_item("exclude_defaults", route.response_model_exclude_defaults)?;
                serialization_kwargs.set_item("exclude_none", route.response_model_exclude_none)?;
                if let Some(include) = route.response_model_include.as_ref() {
                    serialization_kwargs.set_item("include", include.bind(py))?;
                } else {
                    serialization_kwargs.set_item("include", py.None())?;
                }
                if let Some(exclude) = route.response_model_exclude.as_ref() {
                    serialization_kwargs.set_item("exclude", exclude.bind(py))?;
                } else {
                    serialization_kwargs.set_item("exclude", py.None())?;
                }
                let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
                let endpoint_context = response_endpoint_context(
                    py,
                    route.endpoint.bind(py),
                    &route.method,
                    &route.path,
                    &root_path,
                )?
                .unbind();
                Some(StreamItemSerializer {
                    adapter,
                    validation_kwargs: validation_kwargs.unbind(),
                    serialization_kwargs: serialization_kwargs.unbind(),
                    endpoint_context: endpoint_context.into(),
                })
            } else {
                None
            };
            (
                route.generator_kind,
                route
                    .response_class
                    .as_ref()
                    .map(|response_class| response_class.clone_ref(py)),
                route.sse_stream,
                route.status_code,
                stream_serializer,
            )
        };
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.clone_ref(py));
        let injected_response_bound = injected_response.as_ref().map(|response| response.bind(py));
        let status_code = injected_response_status(injected_response_bound)
            .and_then(|status_code| {
                status_code
                    .map(|status_code| status_code.bind(py).extract::<u16>())
                    .transpose()
            })?
            .or(status_code);
        if generator_kind.is_generator() {
            let json_lines = response_class.is_none() && !sse_stream;
            let synchronous = generator_kind == FastApiGeneratorKind::Sync;
            let stream = Py::new(
                py,
                PyFastApiAsyncStream::from_content(
                    py,
                    result,
                    synchronous,
                    json_lines,
                    sse_stream,
                    stream_serializer,
                )?,
            )?;
            let response_class = if sse_stream {
                py.import("starlette.responses")?
                    .getattr("StreamingResponse")?
                    .unbind()
            } else {
                match response_class {
                    Some(response_class) => response_class,
                    None => py
                        .import("starlette.responses")?
                        .getattr("StreamingResponse")?
                        .unbind(),
                }
            };
            let kwargs = PyDict::new(py);
            kwargs.set_item("content", stream.bind(py))?;
            if let Some(status_code) = status_code {
                kwargs.set_item("status_code", status_code)?;
            }
            let background_tasks = self.request_background_tasks(py);
            if let Some(background_tasks) = background_tasks.as_ref() {
                kwargs.set_item("background", background_tasks.bind(py))?;
            } else {
                kwargs.set_item("background", py.None())?;
            }
            if json_lines {
                kwargs.set_item("media_type", "application/jsonl")?;
            } else if sse_stream {
                kwargs.set_item("media_type", "text/event-stream")?;
            } else {
                let streaming_response = py
                    .import("starlette.responses")?
                    .getattr("StreamingResponse")?;
                let is_streaming_response = py
                    .import("builtins")?
                    .getattr("issubclass")?
                    .call1((response_class.bind(py), streaming_response))?
                    .extract::<bool>()?;
                if is_streaming_response {
                    kwargs
                        .set_item("media_type", response_class.bind(py).getattr("media_type")?)?;
                }
            }
            let response = response_class.bind(py).call((), Some(&kwargs))?;
            if sse_stream {
                let headers = response.getattr("headers")?;
                headers.set_item("Cache-Control", "no-cache")?;
                headers.set_item("X-Accel-Buffering", "no")?;
            }
            merge_injected_response_state(py, &response, injected_response_bound)?;
            return self.start_returned_response(py, &response);
        }

        let app = self.app.bind(py).borrow();
        let route = app
            .routes
            .get(self.route_index.unwrap_or_default())
            .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
        let response_value = if let Some(response_model) = route.response_model.as_ref() {
            let adapter = py
                .import("pydantic")?
                .getattr("TypeAdapter")?
                .call1((response_model.bind(py),))?;
            let validation_kwargs = PyDict::new(py);
            validation_kwargs.set_item("from_attributes", true)?;
            let validated = match adapter.call_method(
                "validate_python",
                (result.bind(py),),
                Some(&validation_kwargs),
            ) {
                Ok(validated) => validated,
                Err(error) if is_pydantic_validation_error(py, &error) => {
                    let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
                    let endpoint_ctx = response_endpoint_context(
                        py,
                        route.endpoint.bind(py),
                        &route.method,
                        &route.path,
                        &root_path,
                    )?;
                    return Err(crate::errors::response_validation_error(
                        py,
                        &error,
                        result.bind(py),
                        &endpoint_ctx,
                    )?);
                }
                Err(error) => return Err(error),
            };
            let kwargs = PyDict::new(py);
            kwargs.set_item("mode", "json")?;
            kwargs.set_item("by_alias", route.response_model_by_alias)?;
            kwargs.set_item("exclude_unset", route.response_model_exclude_unset)?;
            kwargs.set_item("exclude_defaults", route.response_model_exclude_defaults)?;
            kwargs.set_item("exclude_none", route.response_model_exclude_none)?;
            if let Some(include) = route.response_model_include.as_ref() {
                kwargs.set_item("include", include.bind(py))?;
            } else {
                kwargs.set_item("include", py.None())?;
            }
            if let Some(exclude) = route.response_model_exclude.as_ref() {
                kwargs.set_item("exclude", exclude.bind(py))?;
            } else {
                kwargs.set_item("exclude", py.None())?;
            }
            adapter.call_method("dump_python", (validated,), Some(&kwargs))?
        } else {
            jsonable_encoder_default(py, result.bind(py))?
        };
        let response_class = route
            .response_class
            .as_ref()
            .map(|response_class| response_class.clone_ref(py));
        drop(app);
        if let Some(response_class) = response_class {
            let kwargs = PyDict::new(py);
            if let Some(status_code) = status_code {
                kwargs.set_item("status_code", status_code)?;
            }
            let background_tasks = self.request_background_tasks(py);
            if let Some(background_tasks) = background_tasks.as_ref() {
                kwargs.set_item("background", background_tasks.bind(py))?;
            } else {
                kwargs.set_item("background", py.None())?;
            }
            let response = response_class
                .bind(py)
                .call((response_value,), Some(&kwargs))?;
            merge_injected_response_state(py, &response, injected_response_bound)?;
            let response_status_code = response.getattr("status_code")?.extract::<i64>()?;
            if response_status_code < 200 || matches!(response_status_code, 204 | 205 | 304) {
                response.setattr("body", PyBytes::new(py, b""))?;
            }
            return self.start_returned_response(py, &response);
        }
        self.response_status = status_code.unwrap_or(200);
        self.response_body = if status_code == Some(204) {
            Vec::new()
        } else {
            json_bytes(py, &response_value)?
        };
        self.send_start_with_injected_response_headers(py)
    }

    fn send_start(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.send_start_with_extra_headers(py, None)
    }

    fn send_start_with_injected_response_headers(
        &mut self,
        py: Python<'_>,
    ) -> PyResult<MachineAction> {
        let extra_headers = self
            .injected_response
            .as_ref()
            .map(|response| {
                response
                    .bind(py)
                    .getattr("headers")?
                    .getattr("raw")
                    .map(Bound::unbind)
            })
            .transpose()?;
        self.send_start_with_extra_headers(py, extra_headers)
    }

    fn send_start_with_extra_headers(
        &mut self,
        py: Python<'_>,
        extra_headers: Option<Py<PyAny>>,
    ) -> PyResult<MachineAction> {
        self.close_function_dependency_stack_before_response(
            py,
            FunctionCloseContinuation::SendStart(extra_headers),
        )
    }

    fn send_start_after_function_close(
        &mut self,
        py: Python<'_>,
        extra_headers: Option<Py<PyAny>>,
    ) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::SendStart);
        response_start(
            py,
            self.send.bind(py),
            self.response_status,
            &self.response_body,
            extra_headers.as_ref().map(|headers| headers.bind(py)),
        )
        .map(MachineAction::Await)
    }

    fn send_body(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::SendBody);
        response_body(py, self.send.bind(py), &self.response_body).map(MachineAction::Await)
    }

    fn run_background_tasks_after_send(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let Some(background_tasks) = self.request_background_tasks(py) else {
            return self.close_form_after_response(py);
        };
        let awaitable = background_tasks.bind(py).call0()?;
        self.pending = Some(PendingAction::BackgroundTasks);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn form_parse_failed(&mut self, py: Python<'_>, error: PyErr) -> PyResult<MachineAction> {
        let value = error.value(py);
        let http_exception = py
            .import("starlette.exceptions")?
            .getattr("HTTPException")?;
        if error.matches(py, &http_exception)? {
            return Err(error);
        }
        let multipart_exception = py
            .import("starlette.formparsers")?
            .getattr("MultiPartException")?;
        if !error.matches(py, &multipart_exception)? {
            return Err(error);
        }
        self.response_status = 400;
        let detail = value.getattr("message")?;
        let body = PyDict::new(py);
        body.set_item("detail", detail)?;
        self.response_body = json_bytes(py, &body)?;
        self.send_start(py)
    }

    fn dependency_stacks_open(&self) -> bool {
        self.invocation.as_ref().is_some_and(|invocation| {
            !invocation.function_dependency_exit_stack_closed
                || !invocation.dependency_exit_stack_closed
        })
    }

    fn route_exception(&mut self, py: Python<'_>, error: PyErr) -> PyResult<MachineAction> {
        let function_exit_stack = self.invocation.as_mut().and_then(|invocation| {
            if invocation.function_dependency_exit_stack_closed {
                None
            } else {
                invocation.function_dependency_exit_stack_closed = true;
                Some(invocation.function_dependency_exit_stack.clone_ref(py))
            }
        });
        if let Some(exit_stack) = function_exit_stack {
            let awaitable = dependency_exit_with_error(py, &exit_stack, &error)?;
            self.pending = Some(PendingAction::FunctionDependencyCloseAfterError(error));
            return Ok(MachineAction::Await(awaitable));
        }
        self.close_request_dependency_stack_after_error(py, error)
    }

    fn close_request_dependency_stack_after_error(
        &mut self,
        py: Python<'_>,
        error: PyErr,
    ) -> PyResult<MachineAction> {
        let exit = self.invocation.as_mut().and_then(|invocation| {
            if invocation.dependency_exit_stack_closed {
                None
            } else {
                invocation.dependency_exit_stack_closed = true;
                Some(invocation.dependency_exit_stack.clone_ref(py))
            }
        });
        if let Some(exit_stack) = exit {
            let awaitable = dependency_exit_with_error(py, &exit_stack, &error)?;
            self.pending = Some(PendingAction::DependencyCloseAfterError(error));
            return Ok(MachineAction::Await(awaitable));
        }
        self.route_exception_after_dependency_cleanup(py, error)
    }

    fn route_exception_after_dependency_cleanup(
        &mut self,
        py: Python<'_>,
        error: PyErr,
    ) -> PyResult<MachineAction> {
        if self.websocket_route_index.is_some() {
            if self.has_registered_exception_handler(py, &error)? {
                return Err(error);
            }
            return self.close_websocket_exception(py, error);
        }
        Err(error)
    }

    fn has_registered_exception_handler(&self, py: Python<'_>, error: &PyErr) -> PyResult<bool> {
        let exception_type = error.get_type(py);
        let server_error_type = py.get_type::<PyException>();
        let integer_type = py.get_type::<PyInt>();
        let issubclass = py.import("builtins")?.getattr("issubclass")?;
        let exception_handlers = self.app.bind(py).borrow().exception_handlers.clone_ref(py);

        for entry in exception_handlers
            .bind(py)
            .call_method0("items")?
            .try_iter()?
        {
            let pair = entry?.cast_into::<PyTuple>()?;
            let key = pair.get_item(0)?;
            if key.is_instance(&integer_type)? || key.is(&server_error_type) {
                continue;
            }
            if issubclass
                .call1((exception_type.clone(), key))?
                .extract::<bool>()?
            {
                return Ok(true);
            }
        }
        Ok(false)
    }

    fn close_form_after_response(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let function_exit_stack = self.invocation.as_mut().and_then(|invocation| {
            if invocation.function_dependency_exit_stack_closed {
                None
            } else {
                invocation.function_dependency_exit_stack_closed = true;
                Some(invocation.function_dependency_exit_stack.clone_ref(py))
            }
        });
        if let Some(exit_stack) = function_exit_stack {
            self.pending = Some(PendingAction::FunctionDependencyCloseAfterResponse);
            return exit_stack
                .bind(py)
                .call_method0("aclose")
                .map(Bound::unbind)
                .map(MachineAction::Await);
        }
        self.close_request_dependency_stack_after_response(py)
    }

    fn close_request_dependency_stack_after_response(
        &mut self,
        py: Python<'_>,
    ) -> PyResult<MachineAction> {
        let exit_stack = self.invocation.as_mut().and_then(|invocation| {
            if invocation.dependency_exit_stack_closed {
                None
            } else {
                invocation.dependency_exit_stack_closed = true;
                Some(invocation.dependency_exit_stack.clone_ref(py))
            }
        });
        if let Some(exit_stack) = exit_stack {
            self.pending = Some(PendingAction::DependencyCloseAfterResponse);
            return exit_stack
                .bind(py)
                .call_method0("aclose")
                .map(Bound::unbind)
                .map(MachineAction::Await);
        }
        self.close_form_request_after_response(py)
    }

    fn close_form_request_after_response(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let Some(request) = self.form_request.as_ref() else {
            return Ok(MachineAction::Complete(py.None()));
        };
        if self.form_close_started {
            return Ok(MachineAction::Complete(py.None()));
        }
        self.form_close_started = true;
        self.pending = Some(PendingAction::FormCloseAfterResponse);
        request
            .bind(py)
            .call_method0("close")
            .map(Bound::unbind)
            .map(MachineAction::Await)
    }

    fn resume_inner(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.begin(py),
            MachineResume::Value(value) => match self.pending.take() {
                Some(PendingAction::RequestBody) => self.receive_request_body(py, value),
                Some(PendingAction::FormParse) => self.receive_form_data(py, value),
                Some(PendingAction::FormFileRead) => {
                    let active = self.active_form_file_read.as_mut().ok_or_else(|| {
                        PyRuntimeError::new_err("form file read completed without an active field")
                    })?;
                    active.values.push(value);
                    self.advance_form_file_reads(py)
                }
                Some(PendingAction::LifespanCompletion) => Ok(MachineAction::Complete(py.None())),
                Some(PendingAction::WebSocketEndpoint | PendingAction::WebSocketClose) => {
                    self.close_form_after_response(py)
                }
                Some(PendingAction::MountedApp) => Ok(MachineAction::Complete(py.None())),
                Some(PendingAction::FrontendConfig) => self.get_frontend_response(py, None),
                Some(PendingAction::FrontendResponse) => self.finish_frontend_response(py, value),
                Some(PendingAction::FrontendAsgiResponse) => self.close_form_after_response(py),
                Some(PendingAction::Endpoint) => self.finish_endpoint(py, value),
                Some(PendingAction::Dependency {
                    cache_key,
                    edge_index,
                }) => self.dependency_resumed(py, cache_key, edge_index, value),
                Some(PendingAction::DependencyGraph(graph)) => {
                    self.dependency_graph_resumed(py, *graph, value)
                }
                Some(PendingAction::OverrideSubdependency {
                    parent_plan,
                    cache_key,
                    edge_index,
                }) => self.override_subdependency_resumed(
                    py,
                    *parent_plan,
                    cache_key,
                    edge_index,
                    value,
                ),
                Some(PendingAction::ReturnedResponse) => self.close_form_after_response(py),
                Some(PendingAction::FunctionDependencyCloseBeforeResponse) => {
                    let continuation =
                        self.function_close_continuation.take().ok_or_else(|| {
                            PyRuntimeError::new_err(
                                "function dependency cleanup resumed without a response",
                            )
                        })?;
                    self.resume_function_close_continuation(py, continuation)
                }
                Some(PendingAction::FunctionDependencyCloseAfterResponse) => {
                    if let Some(continuation) = self.function_close_continuation.take() {
                        self.resume_function_close_continuation(py, continuation)
                    } else {
                        self.close_request_dependency_stack_after_response(py)
                    }
                }
                Some(PendingAction::FunctionDependencyCloseAfterError(error)) => {
                    if value.bind(py).is_truthy()? {
                        Err(fastapi_error(concat!(
                            "Response not awaited. There's a high chance that the ",
                            "application code is raising an exception and a dependency with yield ",
                            "has a block with a bare except, or a block with except Exception, ",
                            "and is not raising the exception again. Read more about it in the ",
                            "docs: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#dependencies-with-yield-and-except"
                        )))
                    } else {
                        self.close_request_dependency_stack_after_error(py, error)
                    }
                }
                Some(PendingAction::DependencyCloseAfterResponse) => {
                    self.close_form_request_after_response(py)
                }
                Some(PendingAction::DependencyCloseAfterError(error)) => {
                    if value.bind(py).is_truthy()? {
                        Err(fastapi_error(concat!(
                            "Response not awaited. There's a high chance that the ",
                            "application code is raising an exception and a dependency with yield ",
                            "has a block with a bare except, or a block with except Exception, ",
                            "and is not raising the exception again. Read more about it in the ",
                            "docs: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#dependencies-with-yield-and-except"
                        )))
                    } else {
                        self.route_exception_after_dependency_cleanup(py, error)
                    }
                }
                Some(PendingAction::FormCloseAfterResponse) => {
                    Ok(MachineAction::Complete(py.None()))
                }
                Some(PendingAction::FormCloseAfterError(error)) => Err(error),
                Some(PendingAction::SendStart) => self.send_body(py),
                Some(PendingAction::SendBody) => self.run_background_tasks_after_send(py),
                Some(PendingAction::BackgroundTasks) => self.close_form_after_response(py),
                Some(PendingAction::RouteInvocation) => Err(PyRuntimeError::new_err(
                    "FastAPI route invocation resumed without a pending awaitable",
                )),
                None => Err(PyRuntimeError::new_err(
                    "ASGI call resumed without a pending action",
                )),
            },
            MachineResume::Error(error) => match self.pending.take() {
                Some(PendingAction::FormParse) => self.form_parse_failed(py, error),
                Some(
                    PendingAction::WebSocketEndpoint
                    | PendingAction::WebSocketClose
                    | PendingAction::RouteInvocation
                    | PendingAction::Endpoint
                    | PendingAction::ReturnedResponse
                    | PendingAction::FrontendConfig
                    | PendingAction::FrontendAsgiResponse
                    | PendingAction::FunctionDependencyCloseBeforeResponse
                    | PendingAction::FunctionDependencyCloseAfterResponse
                    | PendingAction::SendStart
                    | PendingAction::SendBody
                    | PendingAction::BackgroundTasks
                    | PendingAction::Dependency { .. }
                    | PendingAction::DependencyGraph(_)
                    | PendingAction::OverrideSubdependency { .. },
                ) => self.route_exception(py, error),
                Some(PendingAction::FrontendResponse) => self.frontend_response_failed(py, error),
                Some(PendingAction::FunctionDependencyCloseAfterError(_)) => {
                    self.route_exception(py, error)
                }
                Some(PendingAction::DependencyCloseAfterError(_)) => {
                    self.route_exception_after_dependency_cleanup(py, error)
                }
                Some(PendingAction::DependencyCloseAfterResponse)
                | Some(PendingAction::FormCloseAfterError(_))
                | Some(PendingAction::FormCloseAfterResponse) => Err(error),
                _ => Err(error),
            },
        }
    }
}

impl AwaitableStateMachine for FastApiCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match self.resume_inner(py, input) {
            Err(error) if self.dependency_stacks_open() => self.route_exception(py, error),
            Err(error) if matches!(self.pending, Some(PendingAction::RouteInvocation)) => {
                match self.route_exception(py, error) {
                    Ok(action) => Ok(action),
                    Err(error) => {
                        if self.form_request.is_some() && !self.form_close_started {
                            let request = self
                                .form_request
                                .as_ref()
                                .ok_or_else(|| PyRuntimeError::new_err("form request was lost"))?;
                            match request.bind(py).call_method0("close") {
                                Ok(awaitable) => {
                                    self.form_close_started = true;
                                    self.pending = Some(PendingAction::FormCloseAfterError(error));
                                    Ok(MachineAction::Await(awaitable.unbind()))
                                }
                                Err(_) => Err(error),
                            }
                        } else {
                            Err(error)
                        }
                    }
                }
            }
            Err(error) if self.form_request.is_some() && !self.form_close_started => {
                let request = self
                    .form_request
                    .as_ref()
                    .ok_or_else(|| PyRuntimeError::new_err("form request was lost"))?;
                match request.bind(py).call_method0("close") {
                    Ok(awaitable) => {
                        self.form_close_started = true;
                        self.pending = Some(PendingAction::FormCloseAfterError(error));
                        Ok(MachineAction::Await(awaitable.unbind()))
                    }
                    Err(_) => Err(error),
                }
            }
            result => result,
        }
    }
}

/// Registers FastAPI's Rust-owned application type and request markers.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    crate::lifespan::register(module)?;
    register_pydantic_schema_generator(module)?;
    module.add_function(wrap_pyfunction!(frontend_dependency_endpoint, module)?)?;
    module.add_class::<PyFastApi>()?;
    module.add_class::<PyFastApiAsgiApp>()?;
    module.add_class::<PyMiddlewareDecorator>()?;
    module.add_class::<PyFastApiHttpMiddleware>()?;
    module.add_class::<PyFastApiCachedReceiveDescriptor>()?;
    module.add_class::<PyFastApiCachedReceive>()?;
    module.add_class::<PyFastApiMessageCapture>()?;
    module.add_class::<PyFastApiHttpExceptionHandler>()?;
    module.add_class::<PyFastApiRequestValidationExceptionHandler>()?;
    module.add_class::<PyExceptionHandlerDecorator>()?;
    module.add_class::<PyFastApiCallNext>()?;
    module.add_class::<PyApiRouter>()?;
    module.add_class::<PyApiRoute>()?;
    module.add_class::<PyRouteContext>()?;
    module.add_class::<PyRouteContextIterator>()?;
    module.add_class::<PyOperationDecorator>()?;
    module.add_class::<PyWebSocketDecorator>()?;
    module.add_class::<PyRawWebSocketDecorator>()?;
    module.add_class::<PyFastApiAsyncStream>()?;
    module.add_function(wrap_pyfunction!(py_iter_route_contexts, module)?)?;
    let response = module
        .py()
        .import("starlette.responses")?
        .getattr("Response")?;
    module.add("Response", &response)?;
    let request = module
        .py()
        .import("starlette.requests")?
        .getattr("Request")?;
    module.add("Request", &request)?;
    let http_connection = module
        .py()
        .import("starlette.requests")?
        .getattr("HTTPConnection")?;
    module.add("HTTPConnection", &http_connection)?;
    let responses = module.py().import("starlette.responses")?;
    for name in [
        "FileResponse",
        "HTMLResponse",
        "JSONResponse",
        "PlainTextResponse",
        "RedirectResponse",
        "StreamingResponse",
    ] {
        module.add(name, responses.getattr(name)?)?;
    }
    let static_files = module
        .py()
        .import("starlette.staticfiles")?
        .getattr("StaticFiles")?;
    module.add("StaticFiles", static_files)?;
    let websockets = module.py().import("starlette.websockets")?;
    for name in ["WebSocket", "WebSocketDisconnect", "WebSocketState"] {
        module.add(name, websockets.getattr(name)?)?;
    }
    for (name, module_path) in [
        ("Middleware", "starlette.middleware"),
        ("CORSMiddleware", "starlette.middleware.cors"),
        ("GZipMiddleware", "starlette.middleware.gzip"),
        (
            "HTTPSRedirectMiddleware",
            "starlette.middleware.httpsredirect",
        ),
        ("TrustedHostMiddleware", "starlette.middleware.trustedhost"),
        ("WSGIMiddleware", "starlette.middleware.wsgi"),
    ] {
        module.add(name, module.py().import(module_path)?.getattr(name)?)?;
    }
    Ok(())
}
