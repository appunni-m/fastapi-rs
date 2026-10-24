//! Rust-owned FastAPI application registration and ASGI request flow.

use std::cell::RefCell;
use std::collections::{BTreeSet, HashMap, HashSet, VecDeque};
use std::path::Path;
use std::rc::Rc;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, Weak};

use pyo3::exceptions::{
    PyAssertionError, PyAttributeError, PyException, PyKeyError, PyModuleNotFoundError,
    PyNameError, PyNotImplementedError, PyRuntimeError, PyStopAsyncIteration, PyTimeoutError,
    PyTypeError, PyValueError,
};
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{
    PyBool, PyBytes, PyDict, PyFrozenSet, PyInt, PyIterator, PyList, PyMapping, PyModule, PySet,
    PyString, PyTuple, PyType, PyWeakrefMethods, PyWeakrefReference,
};
use starlette_rs::{DetailedRouteMatch, NamedRouteTable, QueryParams, RouteTable};

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};
use crate::dependency_records::{is_dependency_record, is_security_record};
use crate::docs;
use crate::encoding::jsonable_encoder_default;
use crate::errors::fastapi_error;
use crate::lifespan::{FastApiLifespan, warn_on_event};
use crate::openapi::{
    OpenApiAdditionalResponse, OpenApiInfo, OpenApiOperation, OpenApiParameter, openapi_document,
};
use crate::response_field::{ResponseField, ResponseFieldSchemaBatch};
use crate::sse;
use crate::{
    FastApiInputLocation, FastApiInputParameter, FastApiOperationMatch, FastApiOperationRouter,
};

const DEFAULT_RESPONSE_DESCRIPTION: &str = "Successful Response";
const UJSON_RESPONSE_DEPRECATION_MESSAGE: &str = concat!(
    "UJSONResponse is deprecated, FastAPI now serializes data directly to JSON ",
    "bytes via Pydantic when a return type or response model is set, which is ",
    "faster and doesn't need a custom response class. Read more in the FastAPI ",
    "docs: https://fastapi.tiangolo.com/advanced/custom-response/#orjson-or-response-model ",
    "and https://fastapi.tiangolo.com/tutorial/response-model/",
);
const UJSON_RESPONSE_DOC: &str = concat!(
    "JSON response using the ujson library to serialize data to JSON.\n\n",
    "    **Deprecated**: `UJSONResponse` is deprecated. FastAPI now serializes data\n",
    "    directly to JSON bytes via Pydantic when a return type or response model is\n",
    "    set, which is faster and doesn't need a custom response class.\n\n",
    "    Read more in the\n",
    "    [FastAPI docs for Custom Response](https://fastapi.tiangolo.com/advanced/custom-response/#orjson-or-response-model)\n",
    "    and the\n",
    "    [FastAPI docs for Response Model](https://fastapi.tiangolo.com/tutorial/response-model/).\n\n",
    "    **Note**: `ujson` is not included with FastAPI and must be installed\n",
    "    separately, e.g. `pip install ujson`.\n",
    "    "
);
const UJSON_RESPONSE_MISSING_ASSERTION: &str = "ujson must be installed to use UJSONResponse";
const ORJSON_RESPONSE_DEPRECATION_MESSAGE: &str = concat!(
    "ORJSONResponse is deprecated, FastAPI now serializes data directly to JSON ",
    "bytes via Pydantic when a return type or response model is set, which is ",
    "faster and doesn't need a custom response class. Read more in the FastAPI ",
    "docs: https://fastapi.tiangolo.com/advanced/custom-response/#orjson-or-response-model ",
    "and https://fastapi.tiangolo.com/tutorial/response-model/",
);
const ORJSON_RESPONSE_DOC: &str = concat!(
    "JSON response using the orjson library to serialize data to JSON.\n\n",
    "    **Deprecated**: `ORJSONResponse` is deprecated. FastAPI now serializes data\n",
    "    directly to JSON bytes via Pydantic when a return type or response model is\n",
    "    set, which is faster and doesn't need a custom response class.\n\n",
    "    Read more in the\n",
    "    [FastAPI docs for Custom Response](https://fastapi.tiangolo.com/advanced/custom-response/#orjson-or-response-model)\n",
    "    and the\n",
    "    [FastAPI docs for Response Model](https://fastapi.tiangolo.com/tutorial/response-model/).\n\n",
    "    **Note**: `orjson` is not included with FastAPI and must be installed\n",
    "    separately, e.g. `pip install orjson`.\n",
    "    "
);
const FASTAPI_INNER_ASTACK_SCOPE_KEY: &str = "fastapi_inner_astack";
const FASTAPI_FUNCTION_ASTACK_SCOPE_KEY: &str = "fastapi_function_astack";
const SSE_KEEPALIVE_INTERVAL_SECONDS: f64 = 15.0;
const SSE_KEEPALIVE_COMMENT: &[u8] = b": ping\n\n";
const FASTAPI_TELEMETRY_VERSION: &str = "0.157.0";
const FASTAPI_TELEMETRY_SCHEMA_URL: &str = "https://opentelemetry.io/schemas/1.44.0";

fn native_task_coroutine(py: Python<'_>, awaitable: Py<PyAny>) -> PyResult<Py<PyAny>> {
    py.import("fastapi_rs._core")?
        .getattr("_run_native_task")?
        .call1((awaitable,))
        .map(Bound::unbind)
}

thread_local! {
    static EFFECTIVE_ROUTE_CONTEXT: RefCell<Option<Py<PyAny>>> = const { RefCell::new(None) };
}
const ORJSON_RESPONSE_MISSING_ASSERTION: &str = "orjson must be installed to use ORJSONResponse";

#[derive(Clone, Copy)]
enum DeprecatedJsonResponseKind {
    Ujson,
    Orjson,
}

impl DeprecatedJsonResponseKind {
    fn class_name(self) -> &'static str {
        match self {
            Self::Ujson => "UJSONResponse",
            Self::Orjson => "ORJSONResponse",
        }
    }

    fn module_name(self) -> &'static str {
        match self {
            Self::Ujson => "ujson",
            Self::Orjson => "orjson",
        }
    }

    fn deprecation_message(self) -> &'static str {
        match self {
            Self::Ujson => UJSON_RESPONSE_DEPRECATION_MESSAGE,
            Self::Orjson => ORJSON_RESPONSE_DEPRECATION_MESSAGE,
        }
    }

    fn documentation(self) -> &'static str {
        match self {
            Self::Ujson => UJSON_RESPONSE_DOC,
            Self::Orjson => ORJSON_RESPONSE_DOC,
        }
    }

    fn missing_assertion(self) -> &'static str {
        match self {
            Self::Ujson => UJSON_RESPONSE_MISSING_ASSERTION,
            Self::Orjson => ORJSON_RESPONSE_MISSING_ASSERTION,
        }
    }
}

#[pyclass(name = "_DeprecatedJsonResponseRenderDescriptor")]
struct DeprecatedJsonResponseRenderDescriptor {
    serializer_module: Option<Py<PyAny>>,
    kind: DeprecatedJsonResponseKind,
    class_signature: Py<PyAny>,
    instance_signature: Py<PyAny>,
    annotations: Py<PyAny>,
}

#[pymethods]
impl DeprecatedJsonResponseRenderDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Option<Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let signature = if instance.is_some() {
            self.instance_signature.bind(py)
        } else {
            self.class_signature.bind(py)
        };
        let method = Py::new(
            py,
            DeprecatedJsonResponseRenderMethod {
                serializer_module: self
                    .serializer_module
                    .as_ref()
                    .map(|module| module.clone_ref(py)),
                kind: self.kind,
                signature: signature.clone().unbind(),
            },
        )?;
        let method_bound = method.bind(py);
        method_bound.setattr("__name__", "render")?;
        method_bound.setattr("__doc__", py.None())?;
        method_bound.setattr("__module__", "fastapi.responses")?;
        method_bound.setattr("__qualname__", format!("{}.render", self.kind.class_name()))?;
        method_bound.setattr("__annotations__", self.annotations.bind(py))?;
        method_bound.setattr("__signature__", signature)?;
        Ok(method.into_any())
    }
}

#[pyclass(name = "_DeprecatedJsonResponseRenderMethod", dict)]
struct DeprecatedJsonResponseRenderMethod {
    serializer_module: Option<Py<PyAny>>,
    kind: DeprecatedJsonResponseKind,
    signature: Py<PyAny>,
}

#[pymethods]
impl DeprecatedJsonResponseRenderMethod {
    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let bound_arguments = self.signature.bind(py).call_method("bind", args, kwargs)?;
        let arguments = bound_arguments.getattr("arguments")?;
        let arguments = arguments.cast::<PyDict>()?;
        let content = arguments
            .get_item("content")?
            .ok_or_else(|| PyTypeError::new_err("missing required argument: 'content'"))?;
        let Some(serializer_module) = self.serializer_module.as_ref() else {
            return Err(PyAssertionError::new_err(self.kind.missing_assertion()));
        };
        match self.kind {
            DeprecatedJsonResponseKind::Ujson => {
                let kwargs = PyDict::new(py);
                kwargs.set_item("ensure_ascii", false)?;
                let json =
                    serializer_module
                        .bind(py)
                        .call_method("dumps", (content,), Some(&kwargs))?;
                json.call_method1("encode", ("utf-8",)).map(Bound::unbind)
            }
            DeprecatedJsonResponseKind::Orjson => {
                let module = serializer_module.bind(py);
                let non_str_keys = module.getattr("OPT_NON_STR_KEYS")?;
                let serialize_numpy = module.getattr("OPT_SERIALIZE_NUMPY")?;
                let options = py
                    .import("operator")?
                    .getattr("or_")?
                    .call1((non_str_keys, serialize_numpy))?;
                module
                    .getattr("dumps")?
                    .call((content, py.None(), options), None)
                    .map(Bound::unbind)
            }
        }
    }
}

fn deprecated_json_response_render_signature(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let inspect = py.import("inspect")?;
    let parameter = inspect.getattr("Parameter")?;
    let kind = parameter.getattr("POSITIONAL_OR_KEYWORD")?;
    let self_parameter = parameter.call1(("self", kind.clone()))?;
    let content_kwargs = PyDict::new(py);
    content_kwargs.set_item("annotation", py.import("typing")?.getattr("Any")?)?;
    let content_parameter = parameter.call(("content", kind), Some(&content_kwargs))?;
    let parameters = PyTuple::new(py, [self_parameter, content_parameter])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", py.get_type::<PyBytes>())?;
    inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))
        .map(Bound::unbind)
}

#[pyclass(name = "_DeprecatedJsonResponseNew", dict)]
struct DeprecatedJsonResponseNew {
    response_class: Py<PyAny>,
    kind: DeprecatedJsonResponseKind,
}

#[pymethods]
impl DeprecatedJsonResponseNew {
    #[pyo3(signature = (cls, *args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        cls: Bound<'_, PyAny>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let _ = (args, kwargs);
        if cls.is(self.response_class.bind(py)) {
            emit_deprecated_json_response_warning(py, self.kind)?;
        }
        py.import("builtins")?
            .getattr("object")?
            .getattr("__new__")?
            .call1((cls,))
            .map(Bound::unbind)
    }
}

#[pyclass(name = "_DeprecatedJsonResponseInitSubclass", dict)]
struct DeprecatedJsonResponseInitSubclass {
    response_class: Py<PyAny>,
    kind: DeprecatedJsonResponseKind,
}

#[pymethods]
impl DeprecatedJsonResponseInitSubclass {
    #[pyo3(signature = (cls, *args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        cls: Bound<'_, PyAny>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        emit_deprecated_json_response_warning(py, self.kind)?;
        let parent_init_subclass = py
            .import("builtins")?
            .getattr("super")?
            .call1((self.response_class.bind(py), cls))?
            .getattr("__init_subclass__")?;
        parent_init_subclass.call(args, kwargs)?;
        Ok(())
    }
}

fn emit_deprecated_json_response_warning(
    py: Python<'_>,
    kind: DeprecatedJsonResponseKind,
) -> PyResult<()> {
    let kwargs = PyDict::new(py);
    // The source class adds one Python wrapper around construction. This native
    // replacement has no corresponding frame, so step over one fewer frame.
    kwargs.set_item("stacklevel", 2)?;
    py.import("warnings")?.getattr("warn")?.call(
        (
            kind.deprecation_message(),
            crate::errors::fastapi_deprecation_warning_type(py),
        ),
        Some(&kwargs),
    )?;
    Ok(())
}

fn register_deprecated_json_response_helpers(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<DeprecatedJsonResponseRenderDescriptor>()?;
    module.add_class::<DeprecatedJsonResponseRenderMethod>()?;
    module.add_class::<DeprecatedJsonResponseNew>()?;
    module.add_class::<DeprecatedJsonResponseInitSubclass>()?;
    Ok(())
}

fn register_deprecated_json_response(
    module: &Bound<'_, PyModule>,
    kind: DeprecatedJsonResponseKind,
) -> PyResult<()> {
    let py = module.py();
    let class_signature = deprecated_json_response_render_signature(py)?;
    let instance_signature = bound_operation_signature(py, class_signature.bind(py))?;
    let annotations = PyDict::new(py);
    annotations.set_item("content", py.import("typing")?.getattr("Any")?)?;
    annotations.set_item("return", py.get_type::<PyBytes>())?;
    let serializer_module = match py.import(kind.module_name()) {
        Ok(module) => Some(module.into_any().unbind()),
        Err(error) if error.is_instance_of::<PyModuleNotFoundError>(py) => None,
        Err(error) => return Err(error),
    };
    let json_response = py.import("starlette.responses")?.getattr("JSONResponse")?;
    let bases = PyTuple::new(py, [json_response.clone()])?;
    let namespace = PyDict::new(py);
    namespace.set_item("__module__", "fastapi.responses")?;
    namespace.set_item("__doc__", kind.documentation())?;
    namespace.set_item("__deprecated__", kind.deprecation_message())?;
    namespace.set_item(
        "render",
        Py::new(
            py,
            DeprecatedJsonResponseRenderDescriptor {
                serializer_module,
                kind,
                class_signature,
                instance_signature,
                annotations: annotations.into_any().unbind(),
            },
        )?,
    )?;
    let response_class =
        py.import("builtins")?
            .getattr("type")?
            .call1((kind.class_name(), bases, namespace))?;

    let new_method = Py::new(
        py,
        DeprecatedJsonResponseNew {
            response_class: response_class.clone().unbind(),
            kind,
        },
    )?;
    new_method.setattr(py, "__deprecated__", kind.deprecation_message())?;
    let staticmethod = py
        .import("builtins")?
        .getattr("staticmethod")?
        .call1((new_method,))?;
    response_class.setattr("__new__", staticmethod)?;

    let init_subclass = Py::new(
        py,
        DeprecatedJsonResponseInitSubclass {
            response_class: response_class.clone().unbind(),
            kind,
        },
    )?;
    init_subclass.setattr(py, "__deprecated__", kind.deprecation_message())?;
    let classmethod = py
        .import("builtins")?
        .getattr("classmethod")?
        .call1((init_subclass,))?;
    response_class.setattr("__init_subclass__", classmethod)?;

    module.add(kind.class_name(), response_class)
}

fn register_ujson_response(module: &Bound<'_, PyModule>) -> PyResult<()> {
    register_deprecated_json_response(module, DeprecatedJsonResponseKind::Ujson)
}

fn register_orjson_response(module: &Bound<'_, PyModule>) -> PyResult<()> {
    register_deprecated_json_response(module, DeprecatedJsonResponseKind::Orjson)
}

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
    SecurityScopes,
    Dependency {
        plan: Arc<CallablePlan>,
        use_cache: Py<PyAny>,
        scope: Option<String>,
        security_scopes: Vec<String>,
        bind_value: bool,
    },
}

type DependencyCacheKey = (usize, Vec<String>, String);
type OpenApiSecurityVisitKey = (usize, Option<String>, Vec<String>);

#[derive(Clone, Copy)]
enum ParameterDefaultDelivery {
    External,
    InAnnotation,
}

struct CallableParameter {
    name: String,
    annotation: Py<PyAny>,
    validation_adapter: Option<Py<PyAny>>,
    field_info: Option<Py<PyAny>>,
    required: bool,
    default: Option<Py<PyAny>>,
    default_delivery: ParameterDefaultDelivery,
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
    example: Option<Py<PyAny>>,
    openapi_examples: Option<Py<PyAny>>,
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
    own_oauth_scopes: Vec<String>,
    oauth_scopes: Vec<String>,
    is_security_scheme: bool,
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
            Self::SecurityScopes => Self::SecurityScopes,
            Self::Dependency {
                plan,
                use_cache,
                scope,
                security_scopes,
                bind_value,
            } => Self::Dependency {
                plan: Arc::clone(plan),
                use_cache: use_cache.clone_ref(py),
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
            validation_adapter: self
                .validation_adapter
                .as_ref()
                .map(|adapter| adapter.clone_ref(py)),
            field_info: self
                .field_info
                .as_ref()
                .map(|field_info| field_info.clone_ref(py)),
            required: self.required,
            default: self.default.as_ref().map(|value| value.clone_ref(py)),
            default_delivery: self.default_delivery,
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
            example: self.example.as_ref().map(|value| value.clone_ref(py)),
            openapi_examples: self
                .openapi_examples
                .as_ref()
                .map(|value| value.clone_ref(py)),
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
            own_oauth_scopes: self.own_oauth_scopes.clone(),
            oauth_scopes: self.oauth_scopes.clone(),
            is_security_scheme: self.is_security_scheme,
        }
    }

    fn inherit_oauth_scopes(
        &mut self,
        parent_scopes: &[String],
        own_scopes: &[String],
    ) -> PyResult<()> {
        self.own_oauth_scopes = own_scopes.to_vec();
        self.oauth_scopes = parent_scopes.to_vec();
        for scope in own_scopes {
            if !self.oauth_scopes.contains(scope) {
                self.oauth_scopes.push(scope.clone());
            }
        }
        for parameter in &mut self.parameters {
            if let ParameterSource::Dependency {
                plan,
                security_scopes,
                ..
            } = &mut parameter.source
            {
                Arc::get_mut(plan)
                    .ok_or_else(|| {
                        PyRuntimeError::new_err(
                            "dependency plan is shared during scope inheritance",
                        )
                    })?
                    .inherit_oauth_scopes(&self.oauth_scopes, security_scopes)?;
            }
        }
        Ok(())
    }

    fn uses_oauth_scopes(&self) -> bool {
        !self.own_oauth_scopes.is_empty()
            || self.is_security_scheme
            || self.parameters.iter().any(|parameter| {
                matches!(&parameter.source, ParameterSource::SecurityScopes)
                    || matches!(
                        &parameter.source,
                        ParameterSource::Dependency { plan, .. } if plan.uses_oauth_scopes()
                    )
            })
    }

    fn dependency_cache_key(&self) -> DependencyCacheKey {
        let scopes = if self.uses_oauth_scopes() {
            self.oauth_scopes
                .iter()
                .cloned()
                .collect::<BTreeSet<_>>()
                .into_iter()
                .collect()
        } else {
            Vec::new()
        };
        (
            self.callable.as_ptr() as usize,
            scopes,
            self.computed_scope.clone().unwrap_or_default(),
        )
    }

    fn reanalyze_dependency(
        &self,
        context: &InvocationContext<'_, '_>,
        declared_scope: Option<&str>,
    ) -> PyResult<Option<Self>> {
        // Each reached edge reads the current provider dictionary before
        // lookup, signature analysis, or any Python hooks.
        let provider = context.dependency_overrides_provider.bind(context.py);
        if !provider.is_truthy()? {
            return Ok(None);
        }
        let dependency_overrides = provider.getattr("dependency_overrides")?;
        if !dependency_overrides.is_truthy()? {
            return Ok(None);
        }
        // FastAPI rebuilds every edge for a nonempty override map, including
        // unchanged callables. The caller retains the original edge's cache
        // identity and raw use_cache policy while solving the rebuilt signature.
        let callable = dependency_overrides
            .call_method1(
                "get",
                (
                    self.callable.bind(context.py),
                    self.callable.bind(context.py),
                ),
            )?
            .unbind();
        let mut plan = Self::build(
            context.py,
            callable,
            &self.path_parameters,
            declared_scope.map(str::to_owned),
        )?;
        // The replacement receives the original edge's effective scopes as
        // inherited scopes; its outer cache identity still belongs to that edge.
        plan.inherit_oauth_scopes(&self.oauth_scopes, &[])?;
        Ok(Some(plan))
    }
}

impl DependencyExecutionNode {
    fn new(
        original_plan: &CallablePlan,
        use_cache: &Py<PyAny>,
        scope: Option<String>,
        binding_index: usize,
        py: Python<'_>,
    ) -> Self {
        Self {
            original_plan: original_plan.clone_ref(py),
            plan: None,
            cache_key: original_plan.dependency_cache_key(),
            use_cache: use_cache.clone_ref(py),
            scope,
            binding_index,
            children: Vec::new(),
            result: None,
            awaiting: false,
            failed: false,
        }
    }

    fn initialize(&mut self, context: &InvocationContext<'_, '_>) -> PyResult<()> {
        if self.plan.is_some() {
            return Ok(());
        }
        // Source selects this edge once before solving children. Building the
        // chosen parent captures its full child declarations; their own override
        // selection waits until traversal reaches each child.
        let plan = self
            .original_plan
            .reanalyze_dependency(context, self.scope.as_deref())?
            .unwrap_or_else(|| self.original_plan.clone_ref(context.py));
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
            children.push(Self::new(
                child_plan,
                child_use_cache,
                child_scope.clone(),
                dependency_edge_index,
                context.py,
            ));
            dependency_edge_index += 1;
        }
        self.plan = Some(plan);
        self.children = children;
        Ok(())
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
        self.initialize(context)?;
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
        let mut prepared_dependencies = HashMap::with_capacity(self.children.len());
        for child in &self.children {
            if let Some(value) = child.result.as_ref() {
                prepared_dependencies.insert(child.binding_index, value.clone_ref(context.py));
            } else if !child.failed {
                return Err(PyRuntimeError::new_err(
                    "resolved dependency graph omitted a child value",
                ));
            }
        }
        // The source resolves children and validates the parent's own inputs
        // before its caller consults the parent cache, even when a child failed.
        let plan = self.plan.as_ref().ok_or_else(|| {
            PyRuntimeError::new_err("initialized dependency graph omitted its selected plan")
        })?;
        let arguments = plan.prepare_arguments(context, Some(&prepared_dependencies))?;
        if child_failed || arguments.is_none() {
            self.failed = true;
            return Ok(DependencyGraphStep::Invalid);
        }
        if self.use_cache.bind(context.py).is_truthy()? {
            if let Some(result) = context.dependency_cache.get(&self.cache_key) {
                self.result = Some(result.clone_ref(context.py));
                return Ok(DependencyGraphStep::Ready(result.clone_ref(context.py)));
            }
        }
        let arguments = arguments.ok_or_else(|| {
            PyRuntimeError::new_err("validated dependency graph omitted callable arguments")
        })?;
        let generator_kind =
            dependency_callable_generator_kind(context.py, plan.callable.bind(context.py))?;
        // Source generator wrapping occurs only after successful solving and a
        // cache miss, so invalid or cached edges do not invoke wrapper hooks.
        let invoke_plan = if let Some(generator_kind) = generator_kind {
            let decorator = context
                .py
                .import("contextlib")?
                .getattr(match generator_kind {
                    DependencyGeneratorKind::Sync => "contextmanager",
                    DependencyGeneratorKind::Async => "asynccontextmanager",
                })?;
            let mut invoke_plan = plan.clone_ref(context.py);
            invoke_plan.callable = decorator.call1((plan.callable.bind(context.py),))?.unbind();
            invoke_plan
        } else {
            plan.clone_ref(context.py)
        };
        let use_threadpool = generator_kind.is_none()
            && dependency_override_callable(context.py, plan.callable.bind(context.py))?
                == DependencyOverrideCallable::Sync;
        let value =
            invoke_plan.call_with_arguments(context, arguments.bind(context.py), use_threadpool)?;

        let awaitable = if let Some(generator_kind) = generator_kind {
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
            let exit_stack = if self.scope.as_deref() == Some("function") {
                context.function_dependency_exit_stack
            } else {
                context.dependency_exit_stack
            };
            exit_stack
                .call_method1("enter_async_context", (context_manager.bind(context.py),))?
                .unbind()
        } else {
            // Source awaits the classified coroutine's result or the sync
            // worker once. A worker's returned value is stored on resume.
            value
        };

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
    fn new(plan: &CallablePlan, py: Python<'_>) -> Self {
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
            roots.push(DependencyExecutionNode::new(
                dependency_plan,
                use_cache,
                scope.clone(),
                dependency_edge_index,
                py,
            ));
            dependency_edge_index += 1;
        }
        Self {
            roots,
            next_root: 0,
            in_progress_root: None,
            pending_path: None,
        }
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
    dependency_overrides_provider: &'context Py<PyAny>,
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
}

enum DependencyPreparation {
    Ready,
    Invalid,
    AwaitDependencyGraph {
        awaitable: Py<PyAny>,
        graph: Box<DependencyExecutionGraph>,
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
    original_plan: CallablePlan,
    plan: Option<CallablePlan>,
    cache_key: DependencyCacheKey,
    use_cache: Py<PyAny>,
    scope: Option<String>,
    binding_index: usize,
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

struct FastApiTag(String);

impl FromPyObject<'_, '_> for FastApiTag {
    type Error = PyErr;

    fn extract(value: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        if value.is_instance_of::<PyString>() {
            return value.extract::<String>().map(Self);
        }

        let py = value.py();
        let enum_type = py.import("enum")?.getattr("Enum")?;
        if value.is_instance(&enum_type)? {
            return value.getattr("value")?.extract::<String>().map(Self);
        }

        value.extract::<String>().map(Self)
    }
}

impl FastApiGeneratorKind {
    const fn is_generator(self) -> bool {
        !matches!(self, Self::None)
    }
}

fn default_response_class(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let value = py
        .import("starlette.responses")?
        .getattr("JSONResponse")?
        .unbind();
    Py::new(py, PyFastApiDefaultPlaceholder { value }).map(Py::into_any)
}

fn strict_content_type_python_value(py: Python<'_>, value: Option<bool>) -> PyResult<Py<PyAny>> {
    match value {
        Some(value) => Ok(PyBool::new(py, value).to_owned().unbind().into_any()),
        None => {
            let value = PyBool::new(py, true).to_owned().unbind().into_any();
            Py::new(py, PyFastApiDefaultPlaceholder { value }).map(Py::into_any)
        }
    }
}

// Argument presence is captured before Python None could be conflated with an
// omitted keyword. Default creation may fail normally and occurs in the method.
enum ResponseClassArgument {
    Omitted,
    Provided(Py<PyAny>),
}

impl FromPyObject<'_, '_> for ResponseClassArgument {
    type Error = PyErr;

    fn extract(value: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        Ok(Self::Provided(value.to_owned().unbind()))
    }
}

impl ResponseClassArgument {
    fn into_choice(self, py: Python<'_>) -> PyResult<ResponseClassChoice> {
        match self {
            Self::Omitted => default_response_class(py).map(ResponseClassChoice::Default),
            Self::Provided(value) => Ok(ResponseClassChoice::from_python(py, value)),
        }
    }
}

enum RouteClassArgument {
    Omitted,
    Provided(Py<PyAny>),
}

impl FromPyObject<'_, '_> for RouteClassArgument {
    type Error = PyErr;

    fn extract(value: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        Ok(Self::Provided(value.to_owned().unbind()))
    }
}

impl RouteClassArgument {
    fn into_class(self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        match self {
            Self::Omitted => Ok(api_route_type(py)?.unbind()),
            Self::Provided(route_class) => Ok(route_class),
        }
    }
}

enum StrictContentTypeArgument {
    Omitted,
    Provided(Py<PyAny>),
}

impl FromPyObject<'_, '_> for StrictContentTypeArgument {
    type Error = PyErr;

    fn extract(value: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        Ok(Self::Provided(value.to_owned().unbind()))
    }
}

impl StrictContentTypeArgument {
    fn resolve(
        &self,
        py: Python<'_>,
        inherited: Option<bool>,
    ) -> PyResult<(Py<PyAny>, Option<bool>)> {
        match self {
            Self::Omitted => Ok((strict_content_type_python_value(py, inherited)?, inherited)),
            Self::Provided(value) => {
                let is_default = value
                    .bind(py)
                    .is_instance_of::<PyFastApiDefaultPlaceholder>();
                if is_default {
                    if let Some(inherited) = inherited {
                        return Ok((
                            strict_content_type_python_value(py, Some(inherited))?,
                            Some(inherited),
                        ));
                    }
                    let default_value = value.bind(py).getattr("value")?;
                    let strict = default_value.is_truthy()?;
                    return Ok((value.clone_ref(py), Some(strict)));
                }
                let strict = value.bind(py).is_truthy()?;
                Ok((value.clone_ref(py), Some(strict)))
            }
        }
    }
}

enum ResponseClassChoice {
    Default(Py<PyAny>),
    Explicit(Py<PyAny>),
}

impl ResponseClassChoice {
    fn from_python(py: Python<'_>, value: Py<PyAny>) -> Self {
        if value
            .bind(py)
            .is_instance_of::<PyFastApiDefaultPlaceholder>()
        {
            Self::Default(value)
        } else {
            Self::Explicit(value)
        }
    }

    const fn is_default(&self) -> bool {
        matches!(self, Self::Default(_))
    }

    fn clone_ref(&self, py: Python<'_>) -> Self {
        match self {
            Self::Default(value) => Self::Default(value.clone_ref(py)),
            Self::Explicit(value) => Self::Explicit(value.clone_ref(py)),
        }
    }

    fn python_value(&self, py: Python<'_>) -> Py<PyAny> {
        match self {
            Self::Default(value) | Self::Explicit(value) => value.clone_ref(py),
        }
    }

    fn actual(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        match self {
            Self::Default(value) => Ok(value
                .bind(py)
                .extract::<PyRef<'_, PyFastApiDefaultPlaceholder>>()?
                .value
                .clone_ref(py)),
            Self::Explicit(value) => Ok(value.clone_ref(py)),
        }
    }

    fn first_explicit(py: Python<'_>, values: &[&Self]) -> Self {
        values
            .iter()
            .find(|value| !value.is_default())
            .unwrap_or(&values[0])
            .clone_ref(py)
    }
}

enum GenerateUniqueIdArgument {
    Omitted,
    Provided(Py<PyAny>),
}

impl FromPyObject<'_, '_> for GenerateUniqueIdArgument {
    type Error = PyErr;

    fn extract(value: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
        Ok(Self::Provided(value.to_owned().unbind()))
    }
}

impl GenerateUniqueIdArgument {
    fn into_choice(self, py: Python<'_>) -> PyResult<GenerateUniqueIdChoice> {
        match self {
            Self::Omitted => default_generate_unique_id_function(py),
            Self::Provided(value) => Ok(GenerateUniqueIdChoice::from_python(py, value)),
        }
    }
}

enum GenerateUniqueIdChoice {
    Default(Py<PyAny>),
    Explicit(Py<PyAny>),
}

impl GenerateUniqueIdChoice {
    fn from_python(py: Python<'_>, value: Py<PyAny>) -> Self {
        if value
            .bind(py)
            .is_instance_of::<PyFastApiDefaultPlaceholder>()
        {
            Self::Default(value)
        } else {
            Self::Explicit(value)
        }
    }

    const fn is_default(&self) -> bool {
        matches!(self, Self::Default(_))
    }

    fn clone_ref(&self, py: Python<'_>) -> Self {
        match self {
            Self::Default(value) => Self::Default(value.clone_ref(py)),
            Self::Explicit(value) => Self::Explicit(value.clone_ref(py)),
        }
    }

    fn first_explicit(py: Python<'_>, values: &[&Self]) -> Self {
        values
            .iter()
            .find(|value| !value.is_default())
            .unwrap_or(&values[0])
            .clone_ref(py)
    }

    fn actual(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        match self {
            Self::Default(value) => Ok(value
                .bind(py)
                .extract::<PyRef<'_, PyFastApiDefaultPlaceholder>>()?
                .value
                .clone_ref(py)),
            Self::Explicit(value) => Ok(value.clone_ref(py)),
        }
    }

    fn python_value(&self, py: Python<'_>) -> Py<PyAny> {
        match self {
            Self::Default(value) | Self::Explicit(value) => value.clone_ref(py),
        }
    }
}

fn default_generate_unique_id_function(py: Python<'_>) -> PyResult<GenerateUniqueIdChoice> {
    let value = py
        .import("fastapi_rs._core")?
        .getattr("_generate_unique_id")?
        .unbind();
    Py::new(py, PyFastApiDefaultPlaceholder { value })
        .map(|placeholder| GenerateUniqueIdChoice::Default(placeholder.into_any()))
}

struct AdditionalResponseField {
    status: Py<PyAny>,
    response: Py<PyDict>,
    field: Option<ResponseField>,
}

impl AdditionalResponseField {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        Self {
            status: self.status.clone_ref(py),
            response: self.response.clone_ref(py),
            field: self.field.as_ref().map(|field| field.clone_ref(py)),
        }
    }
}

struct RouteResponseFields {
    primary: Option<ResponseField>,
    additional: Vec<AdditionalResponseField>,
}

enum ResponseFieldState {
    Deferred,
    Ready(RouteResponseFields),
}

impl ResponseFieldState {
    fn field(&self, py: Python<'_>) -> PyResult<Option<ResponseField>> {
        match self {
            Self::Ready(fields) => Ok(fields.primary.as_ref().map(|field| field.clone_ref(py))),
            Self::Deferred => Err(PyRuntimeError::new_err(
                "included response field was not materialized",
            )),
        }
    }

    fn additional_fields(&self, py: Python<'_>) -> PyResult<Vec<AdditionalResponseField>> {
        match self {
            Self::Ready(fields) => Ok(fields
                .additional
                .iter()
                .map(|field| field.clone_ref(py))
                .collect()),
            Self::Deferred => Err(PyRuntimeError::new_err(
                "included response field was not materialized",
            )),
        }
    }
}

struct FastApiRoute {
    operation_index: Option<usize>,
    route_matcher: Option<FastApiOperationRouter>,
    path: String,
    path_format: String,
    url_path_format: String,
    methods: Vec<String>,
    name: String,
    route_scope: Option<Py<PyAny>>,
    param_convertors: Py<PyDict>,
    summary: Option<String>,
    description: String,
    response_description: String,
    responses: Py<PyDict>,
    inherited_responses: Py<PyDict>,
    original_responses_snapshot: Py<PyDict>,
    openapi_extra: Option<Py<PyAny>>,
    operation_id: Option<String>,
    unique_id: String,
    unique_id_value: Py<PyAny>,
    generate_unique_id_function: GenerateUniqueIdChoice,
    deprecated: Option<bool>,
    tags: Option<Vec<String>>,
    status_code: Option<u16>,
    include_in_schema: bool,
    response_class: ResponseClassChoice,
    response_class_resolution: Option<ResponseClassResolution>,
    strict_content_type: Option<bool>,
    sse_stream: bool,
    generator_kind: FastApiGeneratorKind,
    stream_item_type: Option<Py<PyAny>>,
    endpoint: Py<PyAny>,
    endpoint_is_coroutine: bool,
    original_route: Py<PyAny>,
    public_route: Py<PyAny>,
    request_handler: Option<Py<PyAny>>,
    effective_route_context: Option<Py<PyAny>>,
    response_model: Option<Py<PyAny>>,
    response_field: ResponseFieldState,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    router_dependencies: Vec<Py<PyAny>>,
    plan: CallablePlan,
}

enum ResponseClassResolutionCandidate {
    Static(ResponseClassChoice),
    RouterDefault(Py<PyFastApi>),
}

impl ResponseClassResolutionCandidate {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        match self {
            Self::Static(value) => Self::Static(value.clone_ref(py)),
            Self::RouterDefault(router) => Self::RouterDefault(router.clone_ref(py)),
        }
    }

    fn current_choice(&self, py: Python<'_>) -> ResponseClassChoice {
        match self {
            Self::Static(value) => value.clone_ref(py),
            Self::RouterDefault(router) => router
                .bind(py)
                .borrow()
                .default_response_class
                .clone_ref(py),
        }
    }
}

struct ResponseClassResolutionState {
    candidates: Vec<ResponseClassResolutionCandidate>,
    resolved: Mutex<Option<ResponseClassChoice>>,
}

impl ResponseClassResolutionState {
    fn choose(&self, py: Python<'_>) -> ResponseClassChoice {
        let choices = self
            .candidates
            .iter()
            .map(|candidate| candidate.current_choice(py))
            .collect::<Vec<_>>();
        let references = choices.iter().collect::<Vec<_>>();
        ResponseClassChoice::first_explicit(py, &references)
    }

    fn cached_choice(&self, py: Python<'_>) -> Option<ResponseClassChoice> {
        self.resolved
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
            .as_ref()
            .map(|choice| choice.clone_ref(py))
    }

    fn resolve(&self, py: Python<'_>) -> ResponseClassChoice {
        if let Some(resolved) = self.cached_choice(py) {
            return resolved;
        }
        let choice = self.choose(py);
        let mut resolved = self
            .resolved
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        if let Some(resolved) = resolved.as_ref() {
            return resolved.clone_ref(py);
        }
        *resolved = Some(choice.clone_ref(py));
        choice
    }
}

struct ResponseClassResolutionGroup {
    members: Mutex<Vec<Weak<ResponseClassResolutionState>>>,
}

impl ResponseClassResolutionGroup {
    fn new() -> Arc<Self> {
        Arc::new(Self {
            members: Mutex::new(Vec::new()),
        })
    }

    fn register(&self, state: &Arc<ResponseClassResolutionState>) {
        self.members
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
            .push(Arc::downgrade(state));
    }

    fn resolve_all(&self, py: Python<'_>) {
        let members = self
            .members
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
            .iter()
            .filter_map(Weak::upgrade)
            .collect::<Vec<_>>();
        for state in members {
            state.resolve(py);
        }
    }
}

struct ResponseClassResolution {
    state: Arc<ResponseClassResolutionState>,
    group: Arc<ResponseClassResolutionGroup>,
}

impl ResponseClassResolution {
    fn for_included_route(
        py: Python<'_>,
        route: &FastApiRoute,
        source_router: &Py<PyFastApi>,
        inherited: &ResponseClassChoice,
        group: &Arc<ResponseClassResolutionGroup>,
    ) -> Self {
        let mut candidates = match route.response_class_resolution.as_ref() {
            Some(resolution) => resolution
                .state
                .candidates
                .iter()
                .map(|candidate| candidate.clone_ref(py))
                .collect(),
            None => vec![
                ResponseClassResolutionCandidate::Static(route.response_class.clone_ref(py)),
                ResponseClassResolutionCandidate::RouterDefault(source_router.clone_ref(py)),
            ],
        };
        candidates.push(ResponseClassResolutionCandidate::Static(
            inherited.clone_ref(py),
        ));
        let state = Arc::new(ResponseClassResolutionState {
            candidates,
            resolved: Mutex::new(None),
        });
        group.register(&state);
        Self {
            state,
            group: Arc::clone(group),
        }
    }

    fn provisional_choice(&self, py: Python<'_>) -> ResponseClassChoice {
        self.state.choose(py)
    }

    fn resolve(&self, py: Python<'_>) -> ResponseClassChoice {
        self.group.resolve_all(py);
        self.state.resolve(py)
    }

    fn clone_ref(&self) -> Self {
        Self {
            state: Arc::clone(&self.state),
            group: Arc::clone(&self.group),
        }
    }
}

struct ResponseModelConfig {
    field: ResponseField,
    include: Option<Py<PyAny>>,
    exclude: Option<Py<PyAny>>,
    by_alias: bool,
    exclude_unset: bool,
    exclude_defaults: bool,
    exclude_none: bool,
    endpoint_is_coroutine: bool,
    endpoint: Py<PyAny>,
    method: String,
    path: String,
}

struct StreamItemConfig {
    annotation: Py<PyAny>,
    include: Option<Py<PyAny>>,
    exclude: Option<Py<PyAny>>,
    by_alias: bool,
    exclude_unset: bool,
    exclude_defaults: bool,
    exclude_none: bool,
    endpoint: Py<PyAny>,
    method: String,
    path: String,
}

struct ResponseValidationState {
    adapter: Py<PyAny>,
    original_content: Py<PyAny>,
    serialization_kwargs: Py<PyDict>,
    response_class: ResponseClassChoice,
    status_code: Option<u16>,
    endpoint: Py<PyAny>,
    method: String,
    path: String,
}

#[pyclass]
struct ResponseModelValidator {
    adapter: Py<PyAny>,
}

impl ResponseModelValidator {
    fn validate(
        &self,
        py: Python<'_>,
        content: &Bound<'_, PyAny>,
    ) -> PyResult<(Py<PyAny>, Py<PyList>)> {
        let kwargs = PyDict::new(py);
        kwargs.set_item("from_attributes", true)?;
        match self
            .adapter
            .bind(py)
            .call_method("validate_python", (content,), Some(&kwargs))
        {
            Ok(value) => Ok((value.unbind(), PyList::empty(py).unbind())),
            Err(error) if is_pydantic_validation_error(py, &error) => {
                // This entire ModelField.validate stage runs in the same
                // context as the validator, including extracting error details.
                let kwargs = PyDict::new(py);
                kwargs.set_item("include_url", false)?;
                let details = error.value(py).call_method("errors", (), Some(&kwargs))?;
                let response_details = PyList::empty(py);
                let prefix = PyTuple::new(py, ["response"])?;
                let add = py.import("operator")?.getattr("add")?;
                for detail in details.try_iter()? {
                    let detail = detail?;
                    let updated = PyDict::new(py);
                    updated.update(detail.cast::<PyMapping>()?)?;
                    let location = detail.call_method1("get", ("loc", PyTuple::empty(py)))?;
                    updated.set_item("loc", add.call1((&prefix, location))?)?;
                    response_details.append(updated)?;
                }
                Ok((py.None(), response_details.unbind()))
            }
            Err(error) => Err(error),
        }
    }
}

#[pymethods]
impl ResponseModelValidator {
    fn __call__(
        &self,
        py: Python<'_>,
        content: &Bound<'_, PyAny>,
    ) -> PyResult<(Py<PyAny>, Py<PyList>)> {
        self.validate(py, content)
    }
}

#[pyclass(name = "_APIRouteState", module = "fastapi_rs._core")]
struct PyApiRouteState {
    path: String,
    path_format: String,
    path_regex: Py<PyAny>,
    param_convertors: Py<PyDict>,
    name: String,
    methods: Py<PySet>,
    tags: Py<PyList>,
    summary: Option<String>,
    description: String,
    description_initialized: bool,
    response_description: String,
    responses: Py<PyDict>,
    deprecated: Option<bool>,
    include_in_schema: bool,
    operation_id: Option<String>,
    openapi_extra: Option<Py<PyAny>>,
    endpoint: Py<PyAny>,
    unique_id: Option<Py<PyAny>>,
    generate_unique_id_function: Py<PyAny>,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    response_class: Py<PyAny>,
    response_class_resolution: Option<ResponseClassResolution>,
    dependency_overrides_provider: Option<Py<PyAny>>,
    callbacks: Py<PyAny>,
    strict_content_type: Py<PyAny>,
    stream_item_type: Option<Py<PyAny>>,
    response_field: Option<ResponseField>,
    openapi_snapshots: Vec<OpenApiRouteSnapshot>,
    standalone_owner: Option<Py<PyFastApi>>,
    standalone_route_index: Option<usize>,
    cached_app: Option<Py<PyAny>>,
}

const API_ROUTE_STATE_ATTRIBUTE: &str = "_fastapi_rs_state";

#[derive(Clone, Copy)]
enum ApiRouteProxyMember {
    Init,
    GetAttr,
    SetAttr,
    Matches,
    GetRouteHandler,
    App,
}

#[pyclass(name = "_APIRouteProxyDescriptor", module = "fastapi_rs._core")]
struct PyApiRouteProxyDescriptor {
    member: ApiRouteProxyMember,
}

#[pyclass(name = "_BoundAPIRouteProxyMember", module = "fastapi_rs._core")]
struct PyBoundApiRouteProxyMember {
    instance: Py<PyAny>,
    member: ApiRouteProxyMember,
}

fn api_route_type<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
    py.import("fastapi_rs._core")?.getattr("APIRoute")
}

fn api_route_state<'py>(route: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
    route.getattr(API_ROUTE_STATE_ATTRIBUTE)
}

fn api_route_state_ref<'py>(route: &Bound<'py, PyAny>) -> PyResult<PyRef<'py, PyApiRouteState>> {
    api_route_state(route)?.extract().map_err(Into::into)
}

fn api_route_state_mut<'py>(route: &Bound<'py, PyAny>) -> PyResult<PyRefMut<'py, PyApiRouteState>> {
    api_route_state(route)?.extract().map_err(Into::into)
}

fn is_fastapi_api_route(py: Python<'_>, route: &Bound<'_, PyAny>) -> PyResult<bool> {
    py.import("builtins")?
        .getattr("isinstance")?
        .call1((route, api_route_type(py)?))?
        .is_truthy()
}

fn set_api_route_proxy_state(
    py: Python<'_>,
    route: &Bound<'_, PyAny>,
    state: &Bound<'_, PyAny>,
) -> PyResult<()> {
    py.import("builtins")?
        .getattr("object")?
        .getattr("__setattr__")?
        .call1((route, API_ROUTE_STATE_ATTRIBUTE, state))?;
    Ok(())
}

fn new_api_route_proxy(py: Python<'_>, state: Py<PyAny>) -> PyResult<Py<PyAny>> {
    let route_type = api_route_type(py)?;
    let route = py
        .import("builtins")?
        .getattr("object")?
        .getattr("__new__")?
        .call1((&route_type, &route_type))?;
    set_api_route_proxy_state(py, &route, state.bind(py))?;
    Ok(route.unbind())
}

fn api_route_proxy_descriptor(py: Python<'_>, member: ApiRouteProxyMember) -> PyResult<Py<PyAny>> {
    Py::new(py, PyApiRouteProxyDescriptor { member }).map(Py::into_any)
}

fn install_api_route_proxy(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    let route_type = py.import("starlette.routing")?.getattr("Route")?;
    let bases = PyTuple::new(py, [route_type])?;
    let namespace = PyDict::new(py);
    namespace.set_item("__module__", "fastapi.routing")?;
    namespace.set_item("__qualname__", "APIRoute")?;
    for (name, member) in [
        ("__init__", ApiRouteProxyMember::Init),
        ("__getattr__", ApiRouteProxyMember::GetAttr),
        ("__setattr__", ApiRouteProxyMember::SetAttr),
        ("matches", ApiRouteProxyMember::Matches),
        ("get_route_handler", ApiRouteProxyMember::GetRouteHandler),
        ("app", ApiRouteProxyMember::App),
    ] {
        namespace.set_item(name, api_route_proxy_descriptor(py, member)?)?;
    }
    let route_type = py
        .import("builtins")?
        .getattr("type")?
        .call1(("APIRoute", bases, namespace))?;
    module.add("APIRoute", route_type)?;
    Ok(())
}

const FASTAPI_PROXY_STATE_ATTRIBUTE: &str = "_fastapi_rs_state";

#[pyclass(name = "_FastAPIProxyDescriptor", module = "fastapi_rs._core")]
struct PyFastApiProxyDescriptor {
    member: String,
    signature: Option<Py<PyAny>>,
}

#[pyclass(name = "_FastAPIProxyPropertyDescriptor", module = "fastapi_rs._core")]
struct PyFastApiProxyPropertyDescriptor {
    member: String,
}

#[pyclass(name = "_BoundFastAPIProxyMember", module = "fastapi_rs._core")]
struct PyBoundFastApiProxyMember {
    instance: Py<PyAny>,
    member: String,
}

fn fastapi_proxy_state<'py>(instance: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
    instance
        .py()
        .import("builtins")?
        .getattr("object")?
        .getattr("__getattribute__")?
        .call1((instance, FASTAPI_PROXY_STATE_ATTRIBUTE))
}

fn fastapi_state_from_object(instance: &Bound<'_, PyAny>) -> PyResult<Py<PyFastApi>> {
    if let Ok(state) = instance.extract::<Py<PyFastApi>>() {
        return Ok(state);
    }
    fastapi_proxy_state(instance)?
        .extract::<Py<PyFastApi>>()
        .map_err(Into::into)
}

fn fastapi_public_instance(py: Python<'_>, app: &Py<PyFastApi>) -> PyResult<Py<PyAny>> {
    let public_instance = app
        .bind(py)
        .borrow()
        .public_instance
        .as_ref()
        .map(|reference| reference.clone_ref(py));
    if let Some(reference) = public_instance {
        let instance = reference.bind(py).call0()?;
        if !instance.is_none() {
            return Ok(instance.unbind());
        }
    }
    Ok(app.clone_ref(py).into_any())
}

fn fastapi_proxy_descriptor_signature(
    py: Python<'_>,
    descriptor: &Bound<'_, PyAny>,
    owner: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    if !descriptor.is_instance_of::<PyOperationRouteDescriptor>() {
        return Ok(None);
    }
    let unbound_callable = descriptor.call_method1("__get__", (py.None(), owner))?;
    unbound_callable
        .getattr("__signature__")
        .map(|signature| Some(signature.unbind()))
}

fn starlette_application_method_signature(py: Python<'_>, member: &str) -> PyResult<Py<PyAny>> {
    let starlette_type = py.import("starlette.applications")?.getattr("Starlette")?;
    let method = starlette_type.getattr(member)?;
    py.import("inspect")?
        .getattr("signature")?
        .call1((method,))
        .map(Bound::unbind)
}

fn fastapi_proxy_descriptor(
    py: Python<'_>,
    member: &str,
    signature: Option<Py<PyAny>>,
) -> PyResult<Py<PyAny>> {
    Py::new(
        py,
        PyFastApiProxyDescriptor {
            member: member.to_owned(),
            signature,
        },
    )
    .map(Py::into_any)
}

fn fastapi_proxy_property_descriptor(py: Python<'_>, member: &str) -> PyResult<Py<PyAny>> {
    Py::new(
        py,
        PyFastApiProxyPropertyDescriptor {
            member: member.to_owned(),
        },
    )
    .map(Py::into_any)
}

fn install_fastapi_proxy(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyFastApiProxyDescriptor>()?;
    module.add_class::<PyFastApiProxyPropertyDescriptor>()?;
    module.add_class::<PyBoundFastApiProxyMember>()?;

    let mut signatures = crate::application_signatures::ApplicationSignatureBuilder::new(module)?;
    let init_signature = signatures.build_signature(py, "FastAPI.__init__")?;
    let call_signature = signatures.build_signature(py, "FastAPI.__call__")?;

    let native_type = py.get_type::<PyFastApi>();
    let native_members = native_type.getattr("__dict__")?;
    let property_type = py.import("builtins")?.getattr("property")?;
    let namespace = PyDict::new(py);
    namespace.set_item("__module__", "fastapi.applications")?;
    namespace.set_item("__qualname__", "FastAPI")?;
    if let Ok(doc) = native_type.getattr("__doc__") {
        if !doc.is_none() {
            namespace.set_item("__doc__", doc)?;
        }
    }
    namespace.set_item(
        "__init__",
        fastapi_proxy_descriptor(py, "__init__", Some(init_signature))?,
    )?;
    namespace.set_item(
        "__getattr__",
        fastapi_proxy_descriptor(py, "__getattr__", None)?,
    )?;

    for item in native_members.call_method0("items")?.try_iter()? {
        let item = item?.cast_into::<PyTuple>()?;
        let key = item.get_item(0)?;
        let value = item.get_item(1)?;
        let Ok(member) = key.extract::<String>() else {
            continue;
        };
        if member == "add_websocket_route" {
            continue;
        }
        if matches!(
            member.as_str(),
            "__new__"
                | "__init__"
                | "__module__"
                | "__qualname__"
                | "__doc__"
                | "__dict__"
                | "__weakref__"
                | "__signature__"
                | "__annotations__"
        ) {
            continue;
        }
        if member.starts_with("__") && member != "__call__" {
            continue;
        }
        let descriptor = if value.is_instance(&property_type)? || value.hasattr("__set__")? {
            fastapi_proxy_property_descriptor(py, &member)?
        } else {
            let signature = match member.as_str() {
                "__call__" => Some(call_signature.clone_ref(py)),
                "add_exception_handler"
                | "add_middleware"
                | "add_route"
                | "host"
                | "mount"
                | "url_path_for" => Some(starlette_application_method_signature(py, &member)?),
                _ => fastapi_proxy_descriptor_signature(py, &value, &native_type)?,
            };
            fastapi_proxy_descriptor(py, &member, signature)?
        };
        namespace.set_item(member, descriptor)?;
    }

    let starlette = py.import("starlette.applications")?.getattr("Starlette")?;
    let bases = PyTuple::new(py, [starlette])?;
    let proxy_type = py
        .import("builtins")?
        .getattr("type")?
        .call1(("FastAPI", bases, namespace))?;
    if let Ok(signature) = native_type.getattr("__signature__") {
        proxy_type.setattr("__signature__", signature)?;
    }
    if let Ok(annotations) = native_type.getattr("__annotations__") {
        if !annotations.is_none() {
            proxy_type.setattr("__annotations__", annotations)?;
        }
    }
    module.add("FastAPI", proxy_type)?;
    Ok(())
}

#[pymethods]
impl PyFastApiProxyDescriptor {
    #[getter]
    fn __signature__(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.signature
            .as_ref()
            .map(|signature| signature.clone_ref(py))
    }

    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let keyword_instance = kwargs
            .map(|kwargs| kwargs.get_item("self"))
            .transpose()?
            .flatten();
        if !args.is_empty() && keyword_instance.is_some() {
            return Err(PyTypeError::new_err(format!(
                "FastAPI.{}() got multiple values for argument 'self'",
                self.member
            )));
        }
        let instance = if args.is_empty() {
            keyword_instance
        } else {
            Some(args.get_item(0)?)
        }
        .ok_or_else(|| {
            PyTypeError::new_err(format!(
                "FastAPI.{}() missing 1 required positional argument: 'self'",
                self.member
            ))
        })?;
        let forwarded_args = PyTuple::new(py, args.iter().skip(usize::from(!args.is_empty())))?;
        let forwarded_kwargs = PyDict::new(py);
        if let Some(kwargs) = kwargs {
            for (key, value) in kwargs.iter() {
                if key.extract::<String>()? != "self" {
                    forwarded_kwargs.set_item(key, value)?;
                }
            }
        }

        if matches!(self.member.as_str(), "__init__" | "__getattr__") {
            let bound_member = Py::new(
                py,
                PyBoundFastApiProxyMember {
                    instance: instance.unbind(),
                    member: self.member.clone(),
                },
            )?;
            return bound_member
                .bind(py)
                .call(&forwarded_args, Some(&forwarded_kwargs))
                .map(Bound::unbind);
        }

        fastapi_proxy_state(&instance)?
            .getattr(self.member.as_str())?
            .call(&forwarded_args, Some(&forwarded_kwargs))
            .map(Bound::unbind)
    }

    fn __get__(
        slf: Py<Self>,
        py: Python<'_>,
        instance: &Bound<'_, PyAny>,
        _owner: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        if instance.is_none() {
            return Ok(slf.into_any());
        }
        let member = slf.bind(py).borrow().member.clone();
        if matches!(member.as_str(), "__init__" | "__getattr__") {
            return Py::new(
                py,
                PyBoundFastApiProxyMember {
                    instance: instance.clone().unbind(),
                    member,
                },
            )
            .map(Py::into_any);
        }
        fastapi_proxy_state(instance)?
            .getattr(member)
            .map(Bound::unbind)
    }
}

#[pymethods]
impl PyFastApiProxyPropertyDescriptor {
    fn __get__(
        slf: Py<Self>,
        py: Python<'_>,
        instance: &Bound<'_, PyAny>,
        _owner: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        if instance.is_none() {
            return Ok(slf.into_any());
        }
        let member = slf.bind(py).borrow().member.clone();
        fastapi_proxy_state(instance)?
            .getattr(member)
            .map(Bound::unbind)
    }

    fn __set__(&self, instance: &Bound<'_, PyAny>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        let member = self.member.as_str();
        fastapi_proxy_state(instance)?.setattr(member, value)?;
        Ok(())
    }

    fn __delete__(&self, instance: &Bound<'_, PyAny>) -> PyResult<()> {
        let state = fastapi_proxy_state(instance)?;
        if self.member == "contact" {
            let mut state = state.extract::<PyRefMut<'_, PyFastApi>>()?;
            if !state.contact_is_set {
                return Err(PyAttributeError::new_err(
                    "'FastAPI' object has no attribute 'contact'",
                ));
            }
            state.contact = None;
            state.contact_is_set = false;
            return Ok(());
        }
        if self.member == "version" {
            let mut state = state.extract::<PyRefMut<'_, PyFastApi>>()?;
            if !state.version_is_set {
                return Err(PyAttributeError::new_err(
                    "'FastAPI' object has no attribute 'version'",
                ));
            }
            state.version_is_set = false;
            return Ok(());
        }
        if self.member == "openapi_schema" {
            let state = state.extract::<PyRefMut<'_, PyFastApi>>()?;
            let retired = {
                let mut cache = state
                    .openapi_cache
                    .lock()
                    .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
                if !cache.schema_is_set {
                    return Err(PyAttributeError::new_err(
                        "'FastAPI' object has no attribute 'openapi_schema'",
                    ));
                }
                cache.schema_is_set = false;
                std::mem::replace(&mut cache.schema, instance.py().None())
            };
            drop(retired);
            return Ok(());
        }
        if self.member == "openapi_tags" {
            let mut state = state.extract::<PyRefMut<'_, PyFastApi>>()?;
            if !state.openapi_tags_is_set {
                return Err(PyAttributeError::new_err(
                    "'FastAPI' object has no attribute 'openapi_tags'",
                ));
            }
            state.openapi_tags_is_set = false;
            return Ok(());
        }
        state.delattr(self.member.as_str())?;
        Ok(())
    }
}

#[pymethods]
impl PyBoundFastApiProxyMember {
    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let instance = self.instance.bind(py);
        match self.member.as_str() {
            "__init__" => {
                let state = py.get_type::<PyFastApi>().call(args, kwargs)?;
                let weakref = PyWeakrefReference::new(instance)?;
                object_setattr(py, instance, FASTAPI_PROXY_STATE_ATTRIBUTE, &state)?;
                state.extract::<PyRefMut<'_, PyFastApi>>()?.public_instance =
                    Some(weakref.unbind());
                Ok(py.None())
            }
            "__getattr__" => {
                require_proxy_arguments(args, kwargs, 1, "FastAPI.__getattr__")?;
                let name = args.get_item(0)?.extract::<String>()?;
                fastapi_proxy_state(instance)?
                    .getattr(name)
                    .map(Bound::unbind)
            }
            _ => Err(PyTypeError::new_err("invalid FastAPI proxy member")),
        }
    }
}

#[pymethods]
impl PyApiRouteProxyDescriptor {
    fn __get__(
        slf: Py<Self>,
        py: Python<'_>,
        instance: &Bound<'_, PyAny>,
        _owner: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        if instance.is_none() {
            return Ok(slf.into_any());
        }
        let member = slf.bind(py).borrow().member;
        if matches!(member, ApiRouteProxyMember::App) {
            let bound = Py::new(
                py,
                PyBoundApiRouteProxyMember {
                    instance: instance.clone().unbind(),
                    member,
                },
            )?;
            return bound.bind(py).call0().map(Bound::unbind);
        }
        Py::new(
            py,
            PyBoundApiRouteProxyMember {
                instance: instance.clone().unbind(),
                member,
            },
        )
        .map(Py::into_any)
    }
}

fn require_proxy_arguments(
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
    expected: usize,
    method: &str,
) -> PyResult<()> {
    if args.len() == expected && kwargs.is_none_or(|kwargs| kwargs.len() == 0) {
        return Ok(());
    }
    Err(PyTypeError::new_err(format!(
        "{method} expected {expected} argument(s)"
    )))
}

fn object_setattr(
    py: Python<'_>,
    instance: &Bound<'_, PyAny>,
    name: &str,
    value: &Bound<'_, PyAny>,
) -> PyResult<()> {
    py.import("builtins")?
        .getattr("object")?
        .getattr("__setattr__")?
        .call1((instance, name, value))?;
    Ok(())
}

#[pymethods]
impl PyBoundApiRouteProxyMember {
    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let instance = self.instance.bind(py);
        match self.member {
            ApiRouteProxyMember::Init => {
                let state = py.get_type::<PyApiRouteState>().call(args, kwargs)?;
                set_api_route_proxy_state(py, instance, &state)?;
                Ok(py.None())
            }
            ApiRouteProxyMember::GetAttr => {
                require_proxy_arguments(args, kwargs, 1, "APIRoute.__getattr__")?;
                let name = args.get_item(0)?.extract::<String>()?;
                api_route_state(instance)?
                    .getattr(name.as_str())
                    .map(Bound::unbind)
            }
            ApiRouteProxyMember::SetAttr => {
                require_proxy_arguments(args, kwargs, 2, "APIRoute.__setattr__")?;
                let name = args.get_item(0)?.extract::<String>()?;
                let value = args.get_item(1)?;
                if name == API_ROUTE_STATE_ATTRIBUTE {
                    object_setattr(py, instance, &name, &value)?;
                } else {
                    let state = api_route_state(instance)?;
                    if matches!(name.as_str(), "summary" | "methods" | "response_class") {
                        state.setattr(name.as_str(), &value)?;
                    } else {
                        object_setattr(py, instance, &name, &value)?;
                    }
                }
                Ok(py.None())
            }
            ApiRouteProxyMember::Matches => {
                require_proxy_arguments(args, kwargs, 1, "APIRoute.matches")?;
                let scope = args.get_item(0)?;
                let result = py
                    .import("starlette.routing")?
                    .getattr("Route")?
                    .getattr("matches")?
                    .call1((instance, &scope))?;
                let match_kind = result.get_item(0)?;
                let child_scope = result.get_item(1)?;
                let no_match = py
                    .import("starlette.routing")?
                    .getattr("Match")?
                    .getattr("NONE")?;
                if !match_kind.is(&no_match) {
                    child_scope.set_item("route", instance)?;
                }
                Ok(result.unbind())
            }
            ApiRouteProxyMember::GetRouteHandler => {
                require_proxy_arguments(args, kwargs, 0, "APIRoute.get_route_handler")?;
                let route = route_for_current_effective_context(py, self.instance.clone_ref(py))?;
                let response_class = route.bind(py).getattr("response_class")?.unbind();
                Py::new(
                    py,
                    PyFastApiRouteHandler {
                        route,
                        response_class,
                    },
                )
                .map(Py::into_any)
            }
            ApiRouteProxyMember::App => {
                require_proxy_arguments(args, kwargs, 0, "APIRoute.app")?;
                let mut route = api_route_state_mut(instance)?;
                if let Some(app) = route.cached_app.as_ref() {
                    return Ok(app.clone_ref(py));
                }
                let (owner, route_index) = api_route_dispatch_owner(py, instance, &route)?;
                let dependency_overrides_provider = route
                    .dependency_overrides_provider
                    .as_ref()
                    .map(|provider| provider.clone_ref(py));
                let app = Py::new(
                    py,
                    PyApiRouteAsgiApp {
                        owner,
                        route_index,
                        dependency_overrides_provider,
                    },
                )?
                .into_any();
                route.cached_app = Some(app.clone_ref(py));
                Ok(app)
            }
        }
    }
}

#[pyclass(name = "RouteContext", module = "fastapi.routing")]
struct PyRouteContext {
    original_route: Py<PyAny>,
    effective_route: Py<PyAny>,
}

#[pyclass(name = "_IncludedRouter", module = "fastapi.routing")]
struct PyFastApiIncludedRouter {
    original_router: Py<PyAny>,
    effective_route_contexts: Py<PyList>,
}

#[pyclass(module = "fastapi.routing")]
struct PyRouteContextIterator {
    routes: Py<PyAny>,
    iterator: Option<Py<PyIterator>>,
    included_iterator: Option<Py<PyIterator>>,
    finished: bool,
}

#[pymethods]
impl PyApiRouteState {
    fn get_route_handler(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let route = route_for_current_effective_context(py, slf.into_any())?;
        let response_class = route.bind(py).getattr("response_class")?.unbind();
        Py::new(
            py,
            PyFastApiRouteHandler {
                route,
                response_class,
            },
        )
        .map(|handler| handler.into_any())
    }

    #[new]
    #[pyo3(signature = (path, endpoint, *, response_model = omitted_response_model(), status_code = None, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, deprecated = None, name = None, methods = None, operation_id = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, include_in_schema = true, response_class = ResponseClassArgument::Omitted, dependency_overrides_provider = None, callbacks = None, openapi_extra = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, strict_content_type = StrictContentTypeArgument::Omitted))]
    // lint-exception: PyO3 needs one Rust argument per APIRoute-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the pinned APIRoute constructor keywords"
    )]
    fn new(
        py: Python<'_>,
        path: &str,
        endpoint: Py<PyAny>,
        response_model: Py<PyAny>,
        status_code: Option<u16>,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        deprecated: Option<bool>,
        name: Option<String>,
        methods: Option<Py<PyAny>>,
        operation_id: Option<String>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        include_in_schema: bool,
        response_class: ResponseClassArgument,
        dependency_overrides_provider: Option<Py<PyAny>>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        strict_content_type: StrictContentTypeArgument,
    ) -> PyResult<Self> {
        let response_class = response_class.into_choice(py)?;

        // Build through the Rust-owned route pipeline so OpenAPI receives a
        // complete operation snapshot. The scratch router is not retained.
        let scratch_router = Py::new(
            py,
            PyApiRouter::new(
                py,
                "",
                None,
                None,
                ResponseClassArgument::Omitted,
                None,
                None,
                None,
                true,
                None,
                None,
                RouteClassArgument::Omitted,
                None,
                None,
                None,
                None,
                true,
                GenerateUniqueIdArgument::Omitted,
                None,
            )?,
        )?;
        let inner = scratch_router.bind(py).borrow().inner_app(py)?;
        let response_model = if response_model.bind(py).is_none() {
            None
        } else if response_model
            .bind(py)
            .is_instance_of::<PyFastApiDefaultPlaceholder>()
        {
            let value = response_model
                .bind(py)
                .extract::<PyRef<'_, PyFastApiDefaultPlaceholder>>()?
                .value
                .clone_ref(py);
            if value.bind(py).is_none() {
                Some(py.NotImplemented())
            } else {
                Some(value)
            }
        } else {
            Some(response_model)
        };
        let decorator = operation_decorator(
            inner.clone_ref(py),
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
                strict_content_type,
                response_description: Some(response_description.to_owned()),
                description,
                responses,
                callbacks,
                openapi_extra,
                summary,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                response_class,
                name,
            },
        )?;
        decorator
            .bind(py)
            .borrow_mut()
            .dependency_overrides_provider = dependency_overrides_provider;
        let normalized_methods = PySet::empty(py)?;
        if let Some(methods) = methods {
            for method in methods.bind(py).try_iter()? {
                normalized_methods.add(method?.call_method0("upper")?)?;
            }
        } else {
            normalized_methods.add("GET")?;
        }
        let callback_methods = normalized_methods
            .iter()
            .map(|method| method.extract::<String>())
            .collect::<PyResult<Vec<_>>>()?;
        register_multi_method_api_route(
            py,
            decorator,
            endpoint,
            callback_methods,
            None,
            None,
            true,
        )?;
        let route = {
            let app = inner.bind(py).borrow();
            app.routes
                .first()
                .map(|route| route.public_route.clone_ref(py))
                .ok_or_else(|| PyRuntimeError::new_err("APIRoute construction produced no route"))?
        };
        let mut route = clone_api_route(py, &route)?;
        route.standalone_owner = Some(inner);
        route.standalone_route_index = Some(0);
        Ok(route)
    }

    #[getter]
    fn app(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let mut route = slf.bind(py).borrow_mut();
        if let Some(app) = route.cached_app.as_ref() {
            return Ok(app.clone_ref(py));
        }
        let (owner, route_index) = api_route_dispatch_owner(py, slf.bind(py), &route)?;
        let dependency_overrides_provider = route
            .dependency_overrides_provider
            .as_ref()
            .map(|provider| provider.clone_ref(py));
        let app = Py::new(
            py,
            PyApiRouteAsgiApp {
                owner,
                route_index,
                dependency_overrides_provider,
            },
        )?
        .into_any();
        route.cached_app = Some(app.clone_ref(py));
        Ok(app)
    }

    fn __call__(
        slf: Py<Self>,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        py.import("starlette.routing")?
            .getattr("BaseRoute")?
            .getattr("__call__")?
            .call1((slf.bind(py), scope, receive, send))
            .map(Bound::unbind)
    }

    fn matches(slf: Py<Self>, py: Python<'_>, scope: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let result = py
            .import("starlette.routing")?
            .getattr("Route")?
            .getattr("matches")?
            .call1((slf.bind(py), scope.bind(py)))?;
        let match_kind = result.get_item(0)?;
        let child_scope = result.get_item(1)?;
        let no_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("NONE")?;
        if !match_kind.is(&no_match) {
            child_scope.set_item("route", slf.bind(py))?;
        }
        Ok(result.unbind())
    }

    fn handle(
        slf: Py<Self>,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        py.import("starlette.routing")?
            .getattr("Route")?
            .getattr("handle")?
            .call1((slf.bind(py), scope, receive, send))
            .map(Bound::unbind)
    }

    #[pyo3(signature = (name, /, **path_params))]
    fn url_path_for(
        slf: Py<Self>,
        py: Python<'_>,
        name: &str,
        path_params: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        py.import("starlette.routing")?
            .getattr("Route")?
            .getattr("url_path_for")?
            .call((slf.bind(py), name), path_params)
            .map(Bound::unbind)
    }

    #[getter]
    fn path(&self) -> &str {
        &self.path
    }

    #[getter]
    fn path_format(&self) -> &str {
        &self.path_format
    }

    #[getter]
    fn path_regex(&self, py: Python<'_>) -> Py<PyAny> {
        self.path_regex.clone_ref(py)
    }

    #[getter]
    fn param_convertors(&self, py: Python<'_>) -> Py<PyDict> {
        self.param_convertors.clone_ref(py)
    }

    #[getter]
    fn name(&self) -> &str {
        &self.name
    }

    #[getter]
    fn summary(&self) -> Option<&str> {
        self.summary.as_deref()
    }

    #[getter]
    fn description(&self) -> PyResult<&str> {
        if !self.description_initialized {
            return Err(PyAttributeError::new_err(
                "'APIRoute' object has no attribute 'description'",
            ));
        }
        Ok(&self.description)
    }

    #[setter]
    fn set_summary(&mut self, summary: Option<String>) {
        self.summary = summary;
    }

    #[getter]
    fn response_description(&self) -> &str {
        &self.response_description
    }

    #[getter]
    fn responses(&self, py: Python<'_>) -> Py<PyDict> {
        self.responses.clone_ref(py)
    }

    #[getter]
    fn deprecated(&self) -> Option<bool> {
        self.deprecated
    }

    #[getter]
    fn include_in_schema(&self) -> bool {
        self.include_in_schema
    }

    #[getter]
    fn operation_id(&self) -> Option<&str> {
        self.operation_id.as_deref()
    }

    #[getter]
    fn openapi_extra(&self, py: Python<'_>) -> Py<PyAny> {
        self.openapi_extra
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[getter]
    fn unique_id(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.unique_id
            .as_ref()
            .map(|unique_id| unique_id.clone_ref(py))
            .ok_or_else(|| {
                PyAttributeError::new_err("'APIRoute' object has no attribute 'unique_id'")
            })
    }

    #[getter]
    fn generate_unique_id_function(&self, py: Python<'_>) -> Py<PyAny> {
        self.generate_unique_id_function.clone_ref(py)
    }

    #[getter]
    fn methods(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self.methods.clone_ref(py).into_any())
    }

    #[setter]
    fn set_methods(&mut self, py: Python<'_>, methods: &Bound<'_, PyAny>) -> PyResult<()> {
        self.methods = py
            .import("builtins")?
            .getattr("set")?
            .call1((methods,))?
            .cast::<PySet>()?
            .clone()
            .unbind();
        Ok(())
    }

    #[getter]
    fn tags(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self.tags.clone_ref(py).into_any())
    }

    #[getter]
    fn endpoint(&self, py: Python<'_>) -> Py<PyAny> {
        self.endpoint.clone_ref(py)
    }

    #[getter]
    fn response_model_include(&self, py: Python<'_>) -> Py<PyAny> {
        self.response_model_include
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[getter]
    fn response_model_exclude(&self, py: Python<'_>) -> Py<PyAny> {
        self.response_model_exclude
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[getter]
    fn response_model_by_alias(&self) -> bool {
        self.response_model_by_alias
    }

    #[getter]
    fn response_model_exclude_unset(&self) -> bool {
        self.response_model_exclude_unset
    }

    #[getter]
    fn response_model_exclude_defaults(&self) -> bool {
        self.response_model_exclude_defaults
    }

    #[getter]
    fn response_model_exclude_none(&self) -> bool {
        self.response_model_exclude_none
    }

    #[getter]
    fn response_class(&self, py: Python<'_>) -> Py<PyAny> {
        self.response_class_resolution
            .as_ref()
            .map(|resolution| resolution.resolve(py).python_value(py))
            .unwrap_or_else(|| self.response_class.clone_ref(py))
    }

    #[setter]
    fn set_response_class(&mut self, response_class: Py<PyAny>) {
        self.response_class = response_class;
        self.response_class_resolution = None;
    }

    #[getter]
    fn dependency_overrides_provider(&self, py: Python<'_>) -> Py<PyAny> {
        self.dependency_overrides_provider
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[getter]
    fn callbacks(&self, py: Python<'_>) -> Py<PyAny> {
        self.callbacks.clone_ref(py)
    }

    #[getter]
    fn strict_content_type(&self, py: Python<'_>) -> Py<PyAny> {
        self.strict_content_type.clone_ref(py)
    }

    #[getter]
    fn stream_item_type(&self, py: Python<'_>) -> Py<PyAny> {
        self.stream_item_type
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }
}

fn clone_api_route(py: Python<'_>, route: &Py<PyAny>) -> PyResult<PyApiRouteState> {
    let route = api_route_state_ref(route.bind(py))?;
    Ok(PyApiRouteState {
        path: route.path.clone(),
        path_format: route.path_format.clone(),
        path_regex: route.path_regex.clone_ref(py),
        param_convertors: route.param_convertors.clone_ref(py),
        name: route.name.clone(),
        methods: route.methods.clone_ref(py),
        tags: route.tags.clone_ref(py),
        summary: route.summary.clone(),
        description: route.description.clone(),
        description_initialized: route.description_initialized,
        response_description: route.response_description.clone(),
        responses: route.responses.clone_ref(py),
        deprecated: route.deprecated,
        include_in_schema: route.include_in_schema,
        operation_id: route.operation_id.clone(),
        openapi_extra: route
            .openapi_extra
            .as_ref()
            .map(|value| value.clone_ref(py)),
        endpoint: route.endpoint.clone_ref(py),
        unique_id: route.unique_id.as_ref().map(|value| value.clone_ref(py)),
        generate_unique_id_function: route.generate_unique_id_function.clone_ref(py),
        response_model_include: route
            .response_model_include
            .as_ref()
            .map(|value| value.clone_ref(py)),
        response_model_exclude: route
            .response_model_exclude
            .as_ref()
            .map(|value| value.clone_ref(py)),
        response_model_by_alias: route.response_model_by_alias,
        response_model_exclude_unset: route.response_model_exclude_unset,
        response_model_exclude_defaults: route.response_model_exclude_defaults,
        response_model_exclude_none: route.response_model_exclude_none,
        response_class: route.response_class.clone_ref(py),
        response_class_resolution: route
            .response_class_resolution
            .as_ref()
            .map(ResponseClassResolution::clone_ref),
        dependency_overrides_provider: route
            .dependency_overrides_provider
            .as_ref()
            .map(|value| value.clone_ref(py)),
        callbacks: route.callbacks.clone_ref(py),
        strict_content_type: route.strict_content_type.clone_ref(py),
        stream_item_type: route
            .stream_item_type
            .as_ref()
            .map(|value| value.clone_ref(py)),
        response_field: route
            .response_field
            .as_ref()
            .map(|field| field.clone_ref(py)),
        openapi_snapshots: route
            .openapi_snapshots
            .iter()
            .map(|snapshot| snapshot.clone_ref(py))
            .collect(),
        standalone_owner: route
            .standalone_owner
            .as_ref()
            .map(|owner| owner.clone_ref(py)),
        standalone_route_index: route.standalone_route_index,
        cached_app: route.cached_app.as_ref().map(|app| app.clone_ref(py)),
    })
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
impl PyFastApiIncludedRouter {
    #[getter]
    fn original_router(&self, py: Python<'_>) -> Py<PyAny> {
        self.original_router.clone_ref(py)
    }
}

fn materialize_api_route_response_class(py: Python<'_>, route: &Py<PyAny>) -> PyResult<()> {
    if !is_fastapi_api_route(py, route.bind(py))? {
        return Ok(());
    }
    let resolution = {
        let route = api_route_state_ref(route.bind(py))?;
        route
            .response_class_resolution
            .as_ref()
            .map(ResponseClassResolution::clone_ref)
    };
    let Some(resolution) = resolution else {
        return Ok(());
    };
    let response_class = resolution.resolve(py).python_value(py);
    let retired = {
        let mut route = api_route_state_mut(route.bind(py))?;
        if route.response_class_resolution.is_some() {
            Some((
                std::mem::replace(&mut route.response_class, response_class),
                route.response_class_resolution.take(),
            ))
        } else {
            None
        }
    };
    drop(retired);
    Ok(())
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
        loop {
            let from_included = self.included_iterator.is_some();
            let next = if let Some(iterator) = self.included_iterator.as_ref() {
                iterator.clone_ref(py).into_bound(py).next()
            } else {
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
                iterator.clone_ref(py).into_bound(py).next()
            };
            let route = match next {
                Some(Ok(route)) => route,
                Some(Err(error)) => {
                    self.finished = true;
                    return Err(error);
                }
                None if from_included => {
                    self.included_iterator = None;
                    continue;
                }
                None => {
                    self.finished = true;
                    return Ok(None);
                }
            };
            if route.is_instance_of::<PyFastApiIncludedRouter>() {
                let included = route.extract::<PyRef<'_, PyFastApiIncludedRouter>>()?;
                self.included_iterator = Some(
                    included
                        .effective_route_contexts
                        .bind(py)
                        .try_iter()?
                        .unbind(),
                );
                continue;
            }
            if route.is_instance_of::<PyRouteContext>() {
                let context = route.unbind();
                let effective_route = context
                    .bind(py)
                    .extract::<PyRef<'_, PyRouteContext>>()?
                    .effective_route
                    .clone_ref(py);
                materialize_api_route_response_class(py, &effective_route)?;
                return Ok(Some(context));
            }
            let route = route.unbind();
            materialize_api_route_response_class(py, &route)?;
            return match new_route_context(py, route.clone_ref(py), route) {
                Ok(context) => Ok(Some(context)),
                Err(error) => {
                    self.finished = true;
                    Err(error)
                }
            };
        }
    }
}

struct ApiRouteViewConfig<'a> {
    route_class: Option<&'a Py<PyAny>>,
    path: &'a str,
    path_format: &'a str,
    path_regex: &'a Py<PyAny>,
    param_convertors: &'a Py<PyDict>,
    methods: &'a [String],
    name: &'a str,
    tags: &'a [String],
    summary: Option<&'a str>,
    description: &'a str,
    response_description: &'a str,
    responses: &'a Py<PyDict>,
    deprecated: Option<bool>,
    include_in_schema: bool,
    operation_id: Option<&'a str>,
    openapi_extra: Option<&'a Py<PyAny>>,
    generate_unique_id_function: &'a GenerateUniqueIdChoice,
    response_model_include: Option<&'a Py<PyAny>>,
    response_model_exclude: Option<&'a Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    response_class: &'a ResponseClassChoice,
    response_class_resolution: Option<&'a ResponseClassResolution>,
    dependency_overrides_provider: Option<&'a Py<PyAny>>,
    callbacks: Option<&'a Py<PyAny>>,
    strict_content_type: &'a Py<PyAny>,
    stream_item_type: Option<&'a Py<PyAny>>,
    response_model: Option<&'a Py<PyAny>>,
    status_code: Option<u16>,
    dependencies: &'a [Py<PyAny>],
}

fn new_api_route_view(
    py: Python<'_>,
    config: ApiRouteViewConfig<'_>,
    endpoint: Py<PyAny>,
) -> PyResult<Py<PyAny>> {
    if let Some(route_class) = config.route_class {
        let is_route_subclass = py
            .import("builtins")?
            .getattr("issubclass")?
            .call1((route_class.bind(py), api_route_type(py)?))?
            .is_truthy()?;
        if !is_route_subclass {
            return Err(PyTypeError::new_err(
                "route_class must be a subclass of APIRoute",
            ));
        }
        let kwargs = PyDict::new(py);
        kwargs.set_item("endpoint", endpoint.bind(py))?;
        match config.response_model {
            Some(response_model) if response_model.bind(py).is(py.NotImplemented()) => {
                let default_response_model = default_placeholder(py, py.None())?;
                kwargs.set_item("response_model", default_response_model.bind(py))?;
            }
            Some(response_model) => kwargs.set_item("response_model", response_model.bind(py))?,
            None => kwargs.set_item("response_model", py.None())?,
        }
        kwargs.set_item("status_code", config.status_code)?;
        kwargs.set_item("tags", PyList::new(py, config.tags)?)?;
        kwargs.set_item(
            "dependencies",
            PyList::new(py, config.dependencies.iter().map(|value| value.bind(py)))?,
        )?;
        kwargs.set_item("summary", config.summary)?;
        kwargs.set_item("description", config.description)?;
        kwargs.set_item("response_description", config.response_description)?;
        kwargs.set_item("responses", config.responses.bind(py))?;
        kwargs.set_item("deprecated", config.deprecated)?;
        kwargs.set_item("name", config.name)?;
        kwargs.set_item(
            "methods",
            PySet::new(py, config.methods.iter().map(String::as_str))?,
        )?;
        kwargs.set_item("operation_id", config.operation_id)?;
        for (name, value) in [
            ("response_model_include", config.response_model_include),
            ("response_model_exclude", config.response_model_exclude),
            ("openapi_extra", config.openapi_extra),
            (
                "dependency_overrides_provider",
                config.dependency_overrides_provider,
            ),
            ("callbacks", config.callbacks),
        ] {
            match value {
                Some(value) => kwargs.set_item(name, value.bind(py))?,
                None => kwargs.set_item(name, py.None())?,
            }
        }
        kwargs.set_item("response_model_by_alias", config.response_model_by_alias)?;
        kwargs.set_item(
            "response_model_exclude_unset",
            config.response_model_exclude_unset,
        )?;
        kwargs.set_item(
            "response_model_exclude_defaults",
            config.response_model_exclude_defaults,
        )?;
        kwargs.set_item(
            "response_model_exclude_none",
            config.response_model_exclude_none,
        )?;
        kwargs.set_item("include_in_schema", config.include_in_schema)?;
        kwargs.set_item("response_class", config.response_class.python_value(py))?;
        kwargs.set_item(
            "generate_unique_id_function",
            config.generate_unique_id_function.python_value(py),
        )?;
        kwargs.set_item("strict_content_type", config.strict_content_type.bind(py))?;
        let route = route_class.bind(py).call((config.path,), Some(&kwargs))?;
        let mut route_state = api_route_state_mut(&route)?;
        route_state.response_class_resolution = config
            .response_class_resolution
            .map(ResponseClassResolution::clone_ref);
        route_state.stream_item_type = config.stream_item_type.map(|value| value.clone_ref(py));
        route_state.response_field = None;
        route_state.openapi_snapshots.clear();
        route_state.standalone_owner = None;
        route_state.standalone_route_index = None;
        route_state.cached_app = None;
        drop(route_state);
        return Ok(route.unbind());
    }

    let tags = PyList::empty(py);
    for tag in config.tags {
        tags.append(tag)?;
    }
    let route_state = Py::new(
        py,
        PyApiRouteState {
            path: config.path.to_owned(),
            path_format: config.path_format.to_owned(),
            path_regex: config.path_regex.clone_ref(py),
            param_convertors: config.param_convertors.clone_ref(py),
            name: config.name.to_owned(),
            methods: PySet::new(py, config.methods.iter().map(String::as_str))?.unbind(),
            tags: tags.unbind(),
            summary: config.summary.map(str::to_owned),
            description: config.description.to_owned(),
            description_initialized: false,
            response_description: config.response_description.to_owned(),
            responses: config.responses.clone_ref(py),
            deprecated: config.deprecated,
            include_in_schema: config.include_in_schema,
            operation_id: config.operation_id.map(str::to_owned),
            openapi_extra: config.openapi_extra.map(|value| value.clone_ref(py)),
            endpoint,
            unique_id: None,
            generate_unique_id_function: config.generate_unique_id_function.python_value(py),
            response_model_include: config
                .response_model_include
                .map(|value| value.clone_ref(py)),
            response_model_exclude: config
                .response_model_exclude
                .map(|value| value.clone_ref(py)),
            response_model_by_alias: config.response_model_by_alias,
            response_model_exclude_unset: config.response_model_exclude_unset,
            response_model_exclude_defaults: config.response_model_exclude_defaults,
            response_model_exclude_none: config.response_model_exclude_none,
            response_class: config.response_class.python_value(py),
            response_class_resolution: config
                .response_class_resolution
                .map(ResponseClassResolution::clone_ref),
            dependency_overrides_provider: config
                .dependency_overrides_provider
                .map(|value| value.clone_ref(py)),
            callbacks: config
                .callbacks
                .map(|value| value.clone_ref(py))
                .unwrap_or_else(|| PyList::empty(py).unbind().into_any()),
            strict_content_type: config.strict_content_type.clone_ref(py),
            stream_item_type: config.stream_item_type.map(|value| value.clone_ref(py)),
            response_field: None,
            openapi_snapshots: Vec::new(),
            standalone_owner: None,
            standalone_route_index: None,
            cached_app: None,
        },
    )?
    .into_any();
    new_api_route_proxy(py, route_state)
}

fn python_string_set_items(set: &Bound<'_, PySet>) -> PyResult<Vec<String>> {
    set.iter().map(|value| value.extract::<String>()).collect()
}

fn api_route_methods(route: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    let methods = route.getattr("methods")?;
    python_string_set_items(methods.cast::<PySet>()?)
}

fn generated_unique_id(
    py: Python<'_>,
    generate_unique_id_function: &GenerateUniqueIdChoice,
    route: &Py<PyAny>,
    operation_id: Option<&str>,
) -> PyResult<Py<PyAny>> {
    if let Some(operation_id) = operation_id.filter(|value| !value.is_empty()) {
        return Ok(PyString::new(py, operation_id).into_any().unbind());
    }
    generate_unique_id_function
        .actual(py)?
        .bind(py)
        .call1((route.bind(py),))
        .map(Bound::unbind)
}

type ApiRouteViewRegistration = (Py<PyAny>, Py<PyAny>, Option<Py<PyAny>>);

fn api_route_view_and_unique_id(
    py: Python<'_>,
    config: ApiRouteViewConfig<'_>,
    endpoint: Py<PyAny>,
    generate_unique_id_function: &GenerateUniqueIdChoice,
    operation_id: Option<&str>,
    cache: Option<&Rc<RefCell<OperationRouteRegistrationCache>>>,
) -> PyResult<ApiRouteViewRegistration> {
    if let Some(cache) = cache {
        let cached = {
            let cache = cache.borrow();
            cache
                .public_route
                .as_ref()
                .zip(cache.unique_id.as_ref())
                .map(|(route, unique_id)| {
                    (
                        route.clone_ref(py),
                        unique_id.clone_ref(py),
                        cache
                            .request_handler
                            .as_ref()
                            .map(|handler| handler.clone_ref(py)),
                    )
                })
        };
        if let Some(cached) = cached {
            return Ok(cached);
        }
    }

    let public_route = new_api_route_view(py, config, endpoint)?;
    let request_handler = custom_api_route_handler(py, public_route.bind(py))?;
    let unique_id =
        generated_unique_id(py, generate_unique_id_function, &public_route, operation_id)?;
    set_api_route_unique_id(py, &public_route, unique_id.bind(py))?;
    set_api_route_description_initialized(py, &public_route)?;
    if let Some(cache) = cache {
        let mut cache = cache.borrow_mut();
        cache.public_route = Some(public_route.clone_ref(py));
        cache.unique_id = Some(unique_id.clone_ref(py));
        cache.request_handler = request_handler
            .as_ref()
            .map(|handler| handler.clone_ref(py));
    }
    Ok((public_route, unique_id, request_handler))
}

fn api_route_callback_summary_tags(
    route: &Bound<'_, PyAny>,
    original_summary: Option<&str>,
    original_tags: Option<&[String]>,
) -> PyResult<(Option<String>, Option<Vec<String>>)> {
    let summary = route.getattr("summary")?.extract::<Option<String>>()?;
    let tags = route.getattr("tags")?.extract::<Vec<String>>()?;
    let tags = if tags.as_slice() == original_tags.unwrap_or_default() {
        original_tags.map(<[String]>::to_vec)
    } else {
        Some(tags)
    };
    let summary = if summary.as_deref() == original_summary {
        original_summary.map(str::to_owned)
    } else {
        summary
    };
    Ok((summary, tags))
}

fn set_api_route_unique_id(
    py: Python<'_>,
    route: &Py<PyAny>,
    unique_id: &Bound<'_, PyAny>,
) -> PyResult<()> {
    api_route_state_mut(route.bind(py))?.unique_id = Some(unique_id.clone().unbind());
    Ok(())
}

fn set_api_route_description_initialized(py: Python<'_>, route: &Py<PyAny>) -> PyResult<()> {
    api_route_state_mut(route.bind(py))?.description_initialized = true;
    Ok(())
}

fn set_api_route_response_field(
    py: Python<'_>,
    route: &Py<PyAny>,
    field: Option<&ResponseField>,
) -> PyResult<()> {
    api_route_state_mut(route.bind(py))?.response_field = field.map(|field| field.clone_ref(py));
    Ok(())
}

fn set_api_route_openapi_snapshots(
    py: Python<'_>,
    route: &Py<PyAny>,
    snapshots: Vec<OpenApiRouteSnapshot>,
) -> PyResult<()> {
    api_route_state_mut(route.bind(py))?.openapi_snapshots = snapshots;
    Ok(())
}

fn python_string_value(value: &Bound<'_, PyAny>) -> PyResult<String> {
    Ok(value.str()?.to_string_lossy().into_owned())
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

fn new_public_starlette_route(
    py: Python<'_>,
    path: &str,
    endpoint: &Bound<'_, PyAny>,
    name: &str,
    include_in_schema: bool,
) -> PyResult<Py<PyAny>> {
    let route_type = py.import("starlette.routing")?.getattr("Route")?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("methods", PyList::new(py, ["GET"])?)?;
    kwargs.set_item("name", name)?;
    kwargs.set_item("include_in_schema", include_in_schema)?;
    route_type
        .call((path, endpoint), Some(&kwargs))
        .map(Bound::unbind)
}

fn replace_python_list(py: Python<'_>, target: &Py<PyList>, values: &[Py<PyAny>]) -> PyResult<()> {
    let target = target.bind(py);
    target.call_method0("clear")?;
    for value in values {
        target.append(value.bind(py))?;
    }
    Ok(())
}

fn openapi_warning_identity(
    py: Python<'_>,
    endpoint: &Bound<'_, PyAny>,
) -> PyResult<(String, Option<String>)> {
    let getattr = py.import("builtins")?.getattr("getattr")?;
    let endpoint_name = getattr
        .call1((endpoint, "__name__", "<unnamed_endpoint>"))?
        .str()?
        .to_string_lossy()
        .into_owned();
    let empty_globals = PyDict::new(py);
    let globals = getattr.call1((endpoint, "__globals__", &empty_globals))?;
    let file_name = globals.call_method1("get", ("__file__",))?;
    let endpoint_file = if file_name.is_truthy()? {
        Some(file_name.str()?.to_string_lossy().into_owned())
    } else {
        None
    };
    Ok((endpoint_name, endpoint_file))
}

struct DirectOpenApiRoute {
    effective_route: Py<PyAny>,
    owner: Option<Py<PyFastApi>>,
    owner_route_index: Option<usize>,
    include_in_schema: bool,
    is_webhook: bool,
}

fn direct_openapi_route_index(
    owner: &Py<PyFastApi>,
    context: &Bound<'_, PyAny>,
    effective_route: &Bound<'_, PyAny>,
) -> Option<usize> {
    let context_pointer = context.as_ptr() as usize;
    let effective_pointer = effective_route.as_ptr() as usize;
    owner
        .bind(context.py())
        .borrow()
        .routes
        .iter()
        .position(|route| {
            let public_pointer = route.public_route.as_ptr() as usize;
            public_pointer == context_pointer
                || public_pointer == effective_pointer
                || route
                    .effective_route_context
                    .as_ref()
                    .is_some_and(|route_context| {
                        let pointer = route_context.as_ptr() as usize;
                        pointer == context_pointer
                            || pointer == effective_pointer
                            || route_context
                                .bind(context.py())
                                .extract::<PyRef<'_, PyRouteContext>>()
                                .is_ok_and(|route_context| {
                                    route_context.effective_route.as_ptr() as usize
                                        == effective_pointer
                                })
                    })
        })
}

fn response_map_with_live_route_changes(
    py: Python<'_>,
    inherited: &Py<PyDict>,
    previous_original: &Py<PyDict>,
    current_original: &Py<PyDict>,
    effective: &Py<PyDict>,
) -> PyResult<(Py<PyDict>, bool)> {
    let updated = PyDict::new(py);
    for (status, response) in effective.bind(py).iter() {
        updated.set_item(status, response)?;
    }
    let mut changed = false;
    for (status, previous) in previous_original.bind(py).iter() {
        let current = current_original.bind(py).get_item(&status)?;
        let source_unchanged = match current.as_ref() {
            Some(current) => current.eq(&previous)?,
            None => false,
        };
        if source_unchanged {
            continue;
        }
        let effective_value = updated.get_item(&status)?;
        let effective_matches_previous = match effective_value.as_ref() {
            Some(value) => value.eq(&previous)?,
            None => false,
        };
        if !effective_matches_previous {
            continue;
        }
        match current {
            Some(current) => updated.set_item(&status, current)?,
            None => match inherited.bind(py).get_item(&status)? {
                Some(inherited_value) => updated.set_item(&status, inherited_value)?,
                None => updated.del_item(&status)?,
            },
        }
        changed = true;
    }
    for (status, current) in current_original.bind(py).iter() {
        if previous_original.bind(py).contains(&status)? {
            continue;
        }
        let effective_value = updated.get_item(&status)?;
        let inherited_value = inherited.bind(py).get_item(&status)?;
        let matches_inherited = match (effective_value.as_ref(), inherited_value.as_ref()) {
            (None, None) => true,
            (Some(effective), Some(inherited)) => effective.eq(inherited)?,
            _ => false,
        };
        if matches_inherited {
            updated.set_item(&status, current)?;
            changed = true;
        }
    }
    Ok((updated.unbind(), changed))
}

fn refresh_deferred_openapi_route_responses(
    py: Python<'_>,
    owner: &Py<PyFastApi>,
    route_index: usize,
    original_route: &Py<PyAny>,
    effective_route: &Py<PyAny>,
) -> PyResult<()> {
    let (is_deferred, inherited, previous_original, effective) = {
        let app = owner.bind(py).borrow();
        let route = app
            .routes
            .get(route_index)
            .ok_or_else(|| PyRuntimeError::new_err("selected OpenAPI route was lost"))?;
        (
            matches!(&route.response_field, ResponseFieldState::Deferred),
            route.inherited_responses.clone_ref(py),
            route.original_responses_snapshot.clone_ref(py),
            route.responses.clone_ref(py),
        )
    };
    if !is_deferred {
        return Ok(());
    }

    let source_responses = api_route_state_ref(original_route.bind(py))?
        .responses
        .clone_ref(py);
    let current_original = clone_response_map(py, &source_responses)?;
    let (updated, changed) = response_map_with_live_route_changes(
        py,
        &inherited,
        &previous_original,
        &current_original,
        &effective,
    )?;
    if changed {
        api_route_state_mut(effective_route.bind(py))?.responses = updated.clone_ref(py);
    }
    let mut app = owner.bind(py).borrow_mut();
    let route = app
        .routes
        .get_mut(route_index)
        .ok_or_else(|| PyRuntimeError::new_err("selected OpenAPI route was lost"))?;
    route.original_responses_snapshot = current_original;
    if changed {
        route.responses = updated;
    }
    Ok(())
}

fn api_route_dispatch_owner(
    py: Python<'_>,
    facade: &Bound<'_, PyAny>,
    route: &PyApiRouteState,
) -> PyResult<(Py<PyFastApi>, usize)> {
    if let (Some(owner), Some(route_index)) = (
        route.standalone_owner.as_ref(),
        route.standalone_route_index,
    ) {
        return Ok((owner.clone_ref(py), route_index));
    }

    let provider = route
        .dependency_overrides_provider
        .as_ref()
        .ok_or_else(|| PyAttributeError::new_err("'APIRoute' has no dispatch owner"))?;
    let owner = if provider.bind(py).is_instance_of::<PyApiRouter>() {
        provider
            .bind(py)
            .extract::<PyRef<'_, PyApiRouter>>()?
            .inner_app(py)?
    } else {
        fastapi_state_from_object(provider.bind(py))
            .map_err(|_| PyAttributeError::new_err("'APIRoute' has no dispatch owner"))?
    };
    let route_index = direct_openapi_route_index(&owner, facade, facade).ok_or_else(|| {
        PyAttributeError::new_err("'APIRoute' is not registered with its dispatch owner")
    })?;
    Ok((owner, route_index))
}

fn custom_api_route_handler(
    py: Python<'_>,
    route: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    if route.get_type().is(&api_route_type(py)?) {
        return Ok(None);
    }
    route
        .call_method0("get_route_handler")
        .map(Bound::unbind)
        .map(Some)
}

struct EffectiveRouteContextGuard {
    previous: Option<Py<PyAny>>,
}

impl EffectiveRouteContextGuard {
    fn enter(context: &Bound<'_, PyAny>) -> Self {
        let context = Some(context.clone().unbind());
        let previous = EFFECTIVE_ROUTE_CONTEXT
            .with(|current| std::mem::replace(&mut *current.borrow_mut(), context));
        Self { previous }
    }
}

impl Drop for EffectiveRouteContextGuard {
    fn drop(&mut self) {
        EFFECTIVE_ROUTE_CONTEXT.with(|current| {
            *current.borrow_mut() = self.previous.take();
        });
    }
}

fn route_for_current_effective_context(py: Python<'_>, route: Py<PyAny>) -> PyResult<Py<PyAny>> {
    let context = EFFECTIVE_ROUTE_CONTEXT.with(|current| {
        current
            .borrow()
            .as_ref()
            .map(|context| context.clone_ref(py))
    });
    let Some(context) = context else {
        return Ok(route);
    };
    let Ok(context) = context.bind(py).extract::<PyRef<'_, PyRouteContext>>() else {
        return Ok(route);
    };
    if context.original_route.as_ptr() == route.as_ptr() {
        Ok(context.effective_route.clone_ref(py))
    } else {
        Ok(route)
    }
}

fn custom_api_route_handler_in_effective_context(
    py: Python<'_>,
    original_route: &Bound<'_, PyAny>,
    effective_context: &Bound<'_, PyAny>,
) -> PyResult<Option<Py<PyAny>>> {
    if original_route.get_type().is(&api_route_type(py)?) {
        return Ok(None);
    }
    let context_guard = EffectiveRouteContextGuard::enter(effective_context);
    let result = original_route.call_method0("get_route_handler");
    drop(context_guard);
    result.map(Bound::unbind).map(Some)
}

fn direct_openapi_contexts(
    py: Python<'_>,
    routes: &Bound<'_, PyAny>,
    is_webhook: bool,
) -> PyResult<Vec<DirectOpenApiRoute>> {
    let iterator = py_iter_route_contexts(py, routes)?;
    let iterator = iterator.bind(py).try_iter()?;
    let mut contexts = Vec::new();
    for context in iterator {
        let context = context?;
        let context = context.unbind();
        let (original_route, effective_route) = {
            let context_ref = context.bind(py).extract::<PyRef<'_, PyRouteContext>>()?;
            (
                context_ref.original_route.clone_ref(py),
                context_ref.effective_route.clone_ref(py),
            )
        };
        if !is_fastapi_api_route(py, original_route.bind(py))?
            || !is_fastapi_api_route(py, effective_route.bind(py))?
        {
            continue;
        }
        let (include_in_schema, provider) = {
            let route = api_route_state_ref(effective_route.bind(py))?;
            (
                route.include_in_schema,
                route
                    .dependency_overrides_provider
                    .as_ref()
                    .map(|provider| provider.clone_ref(py)),
            )
        };
        let owner = provider
            .as_ref()
            .and_then(|provider| fastapi_state_from_object(provider.bind(py)).ok());
        let owner_route_index = owner.as_ref().and_then(|owner| {
            direct_openapi_route_index(owner, context.bind(py), effective_route.bind(py))
        });
        if let (Some(owner), Some(route_index)) = (owner.as_ref(), owner_route_index) {
            refresh_deferred_openapi_route_responses(
                py,
                owner,
                route_index,
                &original_route,
                &effective_route,
            )?;
        }
        contexts.push(DirectOpenApiRoute {
            effective_route,
            owner,
            owner_route_index,
            include_in_schema,
            is_webhook,
        });
    }
    Ok(contexts)
}

fn apply_openapi_route_view(
    py: Python<'_>,
    snapshot: &mut OpenApiRouteSnapshot,
    route: &PyApiRouteState,
    is_webhook: bool,
) -> PyResult<()> {
    snapshot.path_format.clone_from(&route.path_format);
    snapshot.is_webhook = is_webhook;
    snapshot.name.clone_from(&route.name);
    snapshot.summary.clone_from(&route.summary);
    snapshot.description.clone_from(&route.description);
    snapshot
        .response_description
        .clone_from(&route.response_description);
    snapshot.callbacks = route.callbacks.clone_ref(py);
    snapshot.openapi_extra = route
        .openapi_extra
        .as_ref()
        .map(|value| value.clone_ref(py));
    snapshot.operation_id.clone_from(&route.operation_id);
    snapshot.deprecated = route.deprecated;
    let tags = route.tags.bind(py).extract::<Vec<String>>()?;
    snapshot.tags = (!tags.is_empty()).then_some(tags);
    if let Some(unique_id) = route.unique_id.as_ref() {
        snapshot.unique_id_value = unique_id.clone_ref(py);
        snapshot.unique_id = python_string_value(unique_id.bind(py))?;
    }
    let mut additional_fields = Vec::with_capacity(route.responses.bind(py).len());
    for (status, response) in route.responses.bind(py).iter() {
        let mut field = None;
        for existing in &snapshot.additional_fields {
            if existing.status.bind(py).eq(&status)? {
                field = existing.field.as_ref().map(|field| field.clone_ref(py));
                break;
            }
        }
        let response = response
            .cast::<PyDict>()
            .map_err(|_| PyAssertionError::new_err("An additional response must be a dict"))?
            .clone()
            .unbind();
        additional_fields.push(AdditionalResponseField {
            status: status.unbind(),
            response,
            field,
        });
    }
    snapshot.additional_fields = additional_fields;
    Ok(())
}

pub(crate) fn direct_openapi_operations<'py>(
    py: Python<'py>,
    routes: &Bound<'py, PyAny>,
    webhooks: Option<&Bound<'py, PyAny>>,
    separate_input_output_schemas: bool,
) -> PyResult<(Vec<OpenApiOperation>, Py<PyDict>)> {
    let mut direct_routes = direct_openapi_contexts(py, routes, false)?;
    if let Some(webhooks) = webhooks {
        direct_routes.extend(direct_openapi_contexts(py, webhooks, true)?);
    }

    let mut owners = Vec::<(Py<PyFastApi>, HashSet<usize>)>::new();
    let mut owner_positions = HashMap::<usize, usize>::new();
    for route in &direct_routes {
        let (Some(owner), Some(index)) = (route.owner.as_ref(), route.owner_route_index) else {
            continue;
        };
        let pointer = owner.as_ptr() as usize;
        let position = *owner_positions.entry(pointer).or_insert_with(|| {
            owners.push((owner.clone_ref(py), HashSet::new()));
            owners.len() - 1
        });
        owners[position].1.insert(index);
    }
    for (owner, indexes) in &owners {
        materialize_included_response_fields(py, owner, None, Some(indexes))?;
    }

    let mut snapshots = Vec::new();
    for input in direct_routes {
        if !input.include_in_schema {
            continue;
        }
        let methods = {
            let route = api_route_state_ref(input.effective_route.bind(py))?;
            python_string_set_items(route.methods.bind(py))?
        };
        if let (Some(owner), Some(index)) = (input.owner.as_ref(), input.owner_route_index) {
            let owner = owner.bind(py).borrow();
            let route = owner
                .routes
                .get(index)
                .ok_or_else(|| PyRuntimeError::new_err("selected OpenAPI route was lost"))?;
            for method in &methods {
                let mut snapshot =
                    OpenApiRouteSnapshot::from_route(py, route, method, input.is_webhook)?;
                let route_view = api_route_state_ref(input.effective_route.bind(py))?;
                apply_openapi_route_view(py, &mut snapshot, &route_view, input.is_webhook)?;
                snapshots.push(snapshot);
            }
        } else {
            let route = api_route_state_ref(input.effective_route.bind(py))?;
            let template = route.openapi_snapshots.first();
            if template.is_none() && !methods.is_empty() {
                return Err(PyNotImplementedError::new_err(
                    "FastAPI-RS get_openapi could not resolve the APIRoute's operation state",
                ));
            }
            for method in &methods {
                let stored = route
                    .openapi_snapshots
                    .iter()
                    .find(|stored| stored.method == *method)
                    .or(template)
                    .ok_or_else(|| PyRuntimeError::new_err("APIRoute OpenAPI snapshot was lost"))?;
                let mut snapshot = stored.clone_ref(py);
                snapshot.method.clone_from(method);
                apply_openapi_route_view(py, &mut snapshot, &route, input.is_webhook)?;
                snapshots.push(snapshot);
            }
        }
    }

    openapi_operations_from_snapshots(py, &mut snapshots, separate_input_output_schemas)
}

fn endpoint_openapi_description(
    py: Python<'_>,
    endpoint: &Bound<'_, PyAny>,
) -> PyResult<Option<String>> {
    let docstring = endpoint.getattr("__doc__")?;
    if docstring.is_none() || !docstring.is_truthy()? {
        return Ok(None);
    }
    let description = py
        .import("inspect")?
        .getattr("cleandoc")?
        .call1((docstring,))?
        .extract::<String>()?;
    let description = description
        .split('\u{c}')
        .next()
        .unwrap_or_default()
        .trim()
        .to_owned();
    Ok((!description.is_empty()).then_some(description))
}

fn normalized_route_description(
    py: Python<'_>,
    explicit_description: Option<&str>,
    endpoint: &Bound<'_, PyAny>,
) -> PyResult<String> {
    if let Some(description) = explicit_description.filter(|value| !value.is_empty()) {
        return Ok(description
            .split('\u{c}')
            .next()
            .unwrap_or_default()
            .trim()
            .to_owned());
    }
    Ok(endpoint_openapi_description(py, endpoint)?.unwrap_or_default())
}

#[pyfunction(name = "iter_route_contexts")]
fn py_iter_route_contexts(py: Python<'_>, routes: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    Py::new(
        py,
        PyRouteContextIterator {
            routes: routes.clone().unbind(),
            iterator: None,
            included_iterator: None,
            finished: false,
        },
    )
    .map(Py::into_any)
}

struct FastApiRouterInclude {
    route_position: usize,
    websocket_route_position: usize,
    frontend_route_position: usize,
    router: Py<PyAny>,
    merge_prefix: String,
    frontend_merge_prefix: String,
    responses: Py<PyDict>,
    response_class: ResponseClassChoice,
    generate_unique_id_function: GenerateUniqueIdChoice,
    tags: Vec<String>,
    dependencies: Vec<Py<PyAny>>,
    callbacks: Vec<Py<PyAny>>,
    deprecated: Option<bool>,
    include_in_schema: bool,
    strict_content_type: Option<bool>,
    public_route: Py<PyAny>,
    source_route_cursor: usize,
    source_route_indexes: Vec<usize>,
    source_websocket_route_cursor: usize,
    source_websocket_route_indexes: Vec<usize>,
    source_frontend_route_cursor: usize,
    source_frontend_route_indexes: Vec<usize>,
    fields: IncludedFieldBranch,
}

#[derive(Clone, Copy)]
enum RouteDispatchEntry {
    ApiRoute(usize),
    ApiWebSocketRoute(usize),
    MountedRoute(usize),
    RouterInclude(usize),
}

enum HttpDispatchCandidate {
    ApiRoute(usize),
    StarletteRoute(Py<PyAny>),
}

enum WebSocketDispatchCandidate {
    ApiWebSocketRoute(usize),
    StarletteRoute(Py<PyAny>),
}

#[derive(Clone)]
struct IncludedFieldBranch {
    direct_indexes: Vec<usize>,
    children: Vec<Self>,
    ready: bool,
}

impl IncludedFieldBranch {
    fn from_router_indexes(source: &PyFastApi, route_indexes: &[usize]) -> Self {
        let direct_indexes = (0..source.routes.len())
            .filter(|index| {
                !source
                    .router_includes
                    .iter()
                    .any(|include| include.fields.contains_route_index(*index))
            })
            .filter_map(|index| route_indexes.get(index).copied())
            .collect();
        Self {
            direct_indexes,
            children: source
                .router_includes
                .iter()
                .map(|include| include.fields.remap_routes(route_indexes))
                .collect(),
            ready: false,
        }
    }

    fn remap_routes(&self, route_indexes: &[usize]) -> Self {
        Self {
            direct_indexes: self
                .direct_indexes
                .iter()
                .filter_map(|index| route_indexes.get(*index).copied())
                .collect(),
            children: self
                .children
                .iter()
                .map(|child| child.remap_routes(route_indexes))
                .collect(),
            ready: false,
        }
    }

    fn contains_route_index(&self, index: usize) -> bool {
        self.direct_indexes.contains(&index)
            || self
                .children
                .iter()
                .any(|child| child.contains_route_index(index))
    }

    fn preserve_ready_state(&mut self, previous: &Self) {
        self.ready = self.direct_indexes == previous.direct_indexes && previous.ready;
        for (current, previous) in self.children.iter_mut().zip(&previous.children) {
            current.preserve_ready_state(previous);
        }
    }

    fn collect_visits(
        &self,
        full_match_position: Option<usize>,
        route_positions: &[usize],
        path: &mut Vec<usize>,
        visits: &mut Vec<(Vec<usize>, Vec<usize>)>,
    ) {
        let first_route_position = self
            .direct_indexes
            .iter()
            .filter_map(|index| route_positions.get(*index).copied())
            .chain(
                self.children
                    .iter()
                    .filter_map(|child| child.first_route_position(route_positions)),
            )
            .min();
        if full_match_position
            .is_some_and(|position| first_route_position.is_none_or(|first| first > position))
        {
            return;
        }
        if !self.ready {
            visits.push((path.clone(), self.direct_indexes.clone()));
        }
        for (index, child) in self.children.iter().enumerate() {
            path.push(index);
            child.collect_visits(full_match_position, route_positions, path, visits);
            path.pop();
        }
    }

    fn first_route_position(&self, route_positions: &[usize]) -> Option<usize> {
        self.direct_indexes
            .iter()
            .filter_map(|index| route_positions.get(*index).copied())
            .chain(
                self.children
                    .iter()
                    .filter_map(|child| child.first_route_position(route_positions)),
            )
            .min()
    }

    fn collect_selected_visits(
        &self,
        selected_indexes: &HashSet<usize>,
        path: &mut Vec<usize>,
        visits: &mut Vec<(Vec<usize>, Vec<usize>)>,
    ) {
        if !self.ready {
            let selected = self
                .direct_indexes
                .iter()
                .copied()
                .filter(|index| selected_indexes.contains(index))
                .collect::<Vec<_>>();
            if !selected.is_empty() {
                visits.push((path.clone(), selected));
            }
        }
        for (index, child) in self.children.iter().enumerate() {
            path.push(index);
            child.collect_selected_visits(selected_indexes, path, visits);
            path.pop();
        }
    }

    fn descendant_mut(&mut self, path: &[usize]) -> Option<&mut Self> {
        match path.split_first() {
            Some((index, remaining)) => self.children.get_mut(*index)?.descendant_mut(remaining),
            None => Some(self),
        }
    }

    fn descendant(&self, path: &[usize]) -> Option<&Self> {
        match path.split_first() {
            Some((index, remaining)) => self.children.get(*index)?.descendant(remaining),
            None => Some(self),
        }
    }
}

fn build_response_field(
    py: Python<'_>,
    unique_id: &str,
    model: Option<&Py<PyAny>>,
) -> PyResult<Option<ResponseField>> {
    let Some(model) = model else { return Ok(None) };
    if !model.bind(py).is_truthy()? {
        return Ok(None);
    }
    ResponseField::new(py, &format!("Response_{unique_id}"), model.bind(py)).map(Some)
}

struct ResponseFieldInput {
    index: usize,
    unique_id: String,
    model: Option<Py<PyAny>>,
    responses: Py<PyDict>,
    response_class_resolution: Option<ResponseClassResolution>,
    generator_kind: FastApiGeneratorKind,
    effective_route_context: Option<Py<PyAny>>,
}

struct IncludedResponseClassUpdate {
    response_class: ResponseClassChoice,
    sse_stream: bool,
    effective_route: Py<PyAny>,
    python_value: Py<PyAny>,
}

struct PreparedIncludedRoute {
    index: usize,
    response_field: ResponseFieldState,
    response_class: Option<IncludedResponseClassUpdate>,
}

fn included_route_sse_stream(
    py: Python<'_>,
    generator_kind: FastApiGeneratorKind,
    response_class: &ResponseClassChoice,
) -> PyResult<bool> {
    if !generator_kind.is_generator() {
        return Ok(false);
    }
    let actual_response_class = response_class.actual(py)?;
    if !actual_response_class.bind(py).is_instance_of::<PyType>() {
        return Ok(false);
    }
    sse::is_event_source_response_class(py, actual_response_class.bind(py))
}

fn included_effective_api_route(py: Python<'_>, route_context: &Py<PyAny>) -> PyResult<Py<PyAny>> {
    let context = route_context
        .bind(py)
        .extract::<PyRef<'_, PyRouteContext>>()?;
    let route = context.effective_route.clone_ref(py);
    api_route_state_ref(route.bind(py))?;
    Ok(route)
}

fn materialize_included_response_fields(
    py: Python<'_>,
    app: &Py<PyFastApi>,
    full_match: Option<usize>,
    selected_indexes: Option<&HashSet<usize>>,
) -> PyResult<()> {
    // Flat native indexes are retained for immutable route declarations. The
    // companion branch tree preserves source traversal and whole-branch fields.
    // Dynamic route/version refresh remains a separate compatibility boundary.
    let route_order = {
        let app = app.bind(py).borrow();
        effective_route_order(py, &app, IncludedRouteCategory::Http)?
    };
    let mut route_positions = vec![usize::MAX; route_order.len()];
    for (position, route_index) in route_order.into_iter().enumerate() {
        if let Some(route_position) = route_positions.get_mut(route_index) {
            *route_position = position;
        }
    }
    let full_match_position = full_match
        .and_then(|route_index| route_positions.get(route_index).copied())
        .filter(|position| *position != usize::MAX);
    let mut visits = Vec::new();
    {
        let app = app.bind(py).borrow();
        for (index, include) in app.router_includes.iter().enumerate() {
            if let Some(selected_indexes) = selected_indexes {
                include.fields.collect_selected_visits(
                    selected_indexes,
                    &mut vec![index],
                    &mut visits,
                );
            } else {
                include.fields.collect_visits(
                    full_match_position,
                    &route_positions,
                    &mut vec![index],
                    &mut visits,
                );
            }
        }
    }
    for (branch_path, indexes) in visits {
        let inputs = {
            let app = app.bind(py).borrow();
            indexes
                .iter()
                .map(|index| {
                    let route = app.routes.get(*index).ok_or_else(|| {
                        PyRuntimeError::new_err("included route field input was lost")
                    })?;
                    if matches!(&route.response_field, ResponseFieldState::Ready(_)) {
                        return Ok(None);
                    }
                    Ok(Some(ResponseFieldInput {
                        index: *index,
                        unique_id: route.unique_id.clone(),
                        model: route
                            .response_model
                            .as_ref()
                            .map(|model| model.clone_ref(py)),
                        responses: route.responses.clone_ref(py),
                        response_class_resolution: route
                            .response_class_resolution
                            .as_ref()
                            .map(ResponseClassResolution::clone_ref),
                        generator_kind: route.generator_kind,
                        effective_route_context: route
                            .effective_route_context
                            .as_ref()
                            .map(|context| context.clone_ref(py)),
                    }))
                })
                .collect::<PyResult<Vec<_>>>()?
                .into_iter()
                .flatten()
                .collect::<Vec<_>>()
        };
        // Schema hooks, truth testing and destruction on failure are outside
        // the app borrow. No successful partial branch is published on error.
        let mut prepared = Vec::with_capacity(inputs.len());
        for input in inputs {
            let additional =
                build_additional_response_fields(py, input.responses.bind(py), &input.unique_id)?;
            let field = build_response_field(py, &input.unique_id, input.model.as_ref())?;
            let response_class = input
                .response_class_resolution
                .as_ref()
                .map(|resolution| -> PyResult<IncludedResponseClassUpdate> {
                    let response_class = resolution.resolve(py);
                    let route_context =
                        input.effective_route_context.as_ref().ok_or_else(|| {
                            PyRuntimeError::new_err(
                                "included route response class has no effective route context",
                            )
                        })?;
                    Ok(IncludedResponseClassUpdate {
                        sse_stream: included_route_sse_stream(
                            py,
                            input.generator_kind,
                            &response_class,
                        )?,
                        effective_route: included_effective_api_route(py, route_context)?,
                        python_value: response_class.python_value(py),
                        response_class,
                    })
                })
                .transpose()?;
            prepared.push(PreparedIncludedRoute {
                index: input.index,
                response_field: ResponseFieldState::Ready(RouteResponseFields {
                    primary: field,
                    additional,
                }),
                response_class,
            });
        }
        let mut public_response_class_updates = Vec::new();
        let retired = {
            let mut app = app.bind(py).borrow_mut();
            if prepared.iter().any(|route| route.index >= app.routes.len()) {
                return Err(PyRuntimeError::new_err(
                    "included route field destination was lost",
                ));
            }
            let (include_index, descendant) = branch_path
                .split_first()
                .ok_or_else(|| PyRuntimeError::new_err("included field branch was lost"))?;
            let mut retired = Vec::with_capacity(prepared.len());
            for update in prepared {
                let route = app.routes.get_mut(update.index).ok_or_else(|| {
                    PyRuntimeError::new_err("included route field destination was lost")
                })?;
                let old_field = std::mem::replace(&mut route.response_field, update.response_field);
                let old_response_class = match update.response_class {
                    Some(class_update) => {
                        route.sse_stream = class_update.sse_stream;
                        public_response_class_updates
                            .push((class_update.effective_route, class_update.python_value));
                        Some(std::mem::replace(
                            &mut route.response_class,
                            class_update.response_class,
                        ))
                    }
                    None => None,
                };
                retired.push((old_field, old_response_class));
            }
            let branch_ready = app
                .router_includes
                .get(*include_index)
                .and_then(|include| include.fields.descendant(descendant))
                .ok_or_else(|| PyRuntimeError::new_err("included field branch was lost"))?
                .direct_indexes
                .iter()
                .all(|index| {
                    app.routes.get(*index).is_some_and(|route| {
                        matches!(&route.response_field, ResponseFieldState::Ready(_))
                    })
                });
            if let Some(branch) = app
                .router_includes
                .get_mut(*include_index)
                .and_then(|include| include.fields.descendant_mut(descendant))
            {
                branch.ready = branch_ready;
            }
            retired
        };
        for (effective_route, response_class) in public_response_class_updates {
            let retired = {
                let mut route = api_route_state_mut(effective_route.bind(py))?;
                (
                    std::mem::replace(&mut route.response_class, response_class),
                    route.response_class_resolution.take(),
                )
            };
            drop(retired);
        }
        // Finalizers can call user code, so drop replaced Python references only
        // after releasing the mutable app borrow.
        drop(retired);
    }
    Ok(())
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
    strict_content_type: StrictContentTypeArgument,
    response_description: Option<String>,
    description: Option<String>,
    responses: Option<Py<PyAny>>,
    callbacks: Option<Py<PyAny>>,
    openapi_extra: Option<Py<PyAny>>,
    summary: Option<String>,
    operation_id: Option<String>,
    generate_unique_id_function: GenerateUniqueIdChoice,
    deprecated: Option<bool>,
    tags: Option<Vec<String>>,
    dependencies: Vec<Py<PyAny>>,
    response_class: ResponseClassChoice,
    name: Option<String>,
}

type ParameterOpenApiExamples = (Option<Py<PyAny>>, Option<Py<PyAny>>);

struct ParameterOpenApiPlan {
    name: String,
    location: String,
    required: bool,
    annotation: Py<PyAny>,
    schema_config: Option<Py<PyAny>>,
    default: Option<Py<PyAny>>,
    default_delivery: ParameterDefaultDelivery,
    title: Option<String>,
    description: Option<String>,
    deprecated: bool,
    example: Option<Py<PyAny>>,
    openapi_examples: Option<Py<PyAny>>,
}

#[pyclass(name = "FastAPI", module = "fastapi.applications", dict, weakref)]
pub(crate) struct PyFastApi {
    public_instance: Option<Py<PyWeakrefReference>>,
    state: Py<PyAny>,
    extra: Py<PyAny>,
    debug: bool,
    route_scope_prefix: String,
    is_router_inner: bool,
    router_tags: Py<PyAny>,
    router_dependencies: Vec<Py<PyAny>>,
    router_callbacks: Py<PyAny>,
    router_route_class: Option<Py<PyAny>>,
    router_deprecated: Option<bool>,
    router_include_in_schema: bool,
    title: String,
    summary: Option<String>,
    description: String,
    version: Py<PyAny>,
    version_is_set: bool,
    openapi_version: String,
    openapi_url: Option<String>,
    openapi_tags: Py<PyAny>,
    openapi_tags_is_set: bool,
    servers: Py<PyAny>,
    root_path: String,
    root_path_in_servers: bool,
    docs_url: Option<String>,
    redoc_url: Option<String>,
    swagger_ui_oauth2_redirect_url: Option<String>,
    swagger_ui_init_oauth: Option<Py<PyAny>>,
    swagger_ui_parameters: Option<Py<PyAny>>,
    generate_unique_id_function: GenerateUniqueIdChoice,
    separate_input_output_schemas: bool,
    terms_of_service: Option<String>,
    contact: Option<Py<PyAny>>,
    contact_is_set: bool,
    license_info: Option<Py<PyAny>>,
    openapi_external_docs: Option<Py<PyAny>>,
    webhooks: Py<PyAny>,
    dependencies: Vec<Py<PyAny>>,
    responses: Py<PyAny>,
    default_response_class: ResponseClassChoice,
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
    constructor_routes: Vec<Py<PyAny>>,
    route_surface: Py<PyList>,
    routes: Vec<FastApiRoute>,
    route_dispatch_order: Vec<RouteDispatchEntry>,
    router_includes: Vec<FastApiRouterInclude>,
    routes_version: AtomicU64,
    openapi_cache: Mutex<OpenApiCache>,
    mounted_routes: Vec<Py<PyAny>>,
    frontend_routes: Vec<FastApiFrontendRoute>,
    websocket_routes: Vec<FastApiWebSocketRoute>,
    user_middleware: Py<PyList>,
    middleware_stack: Option<Py<PyAny>>,
    router_view: Option<Py<PyAny>>,
    telemetry_tracing: bool,
    telemetry_tracer_provider: Option<Py<PyAny>>,
}

struct OpenApiRouteSnapshot {
    path_format: String,
    is_webhook: bool,
    method: String,
    name: String,
    endpoint: Py<PyAny>,
    summary: Option<String>,
    description: String,
    response_description: String,
    callbacks: Py<PyAny>,
    openapi_extra: Option<Py<PyAny>>,
    operation_id: Option<String>,
    unique_id: String,
    unique_id_value: Py<PyAny>,
    deprecated: Option<bool>,
    tags: Option<Vec<String>>,
    status_code: Option<u16>,
    response_class: ResponseClassChoice,
    sse_stream: bool,
    generator_kind: FastApiGeneratorKind,
    stream_item_type: Option<Py<PyAny>>,
    response_model: Option<Py<PyAny>>,
    primary_field: Option<ResponseField>,
    additional_fields: Vec<AdditionalResponseField>,
    request_schema_key: Option<usize>,
    plan: CallablePlan,
}

impl OpenApiRouteSnapshot {
    fn from_route(
        py: Python<'_>,
        route: &FastApiRoute,
        method: &str,
        is_webhook: bool,
    ) -> PyResult<Self> {
        Ok(Self {
            path_format: route.path_format.clone(),
            is_webhook,
            method: method.to_owned(),
            name: route.name.clone(),
            endpoint: route.endpoint.clone_ref(py),
            summary: route.summary.clone(),
            description: route.description.clone(),
            response_description: route.response_description.clone(),
            callbacks: route.public_route.bind(py).getattr("callbacks")?.unbind(),
            openapi_extra: route
                .openapi_extra
                .as_ref()
                .map(|value| value.clone_ref(py)),
            operation_id: route.operation_id.clone(),
            unique_id: route.unique_id.clone(),
            unique_id_value: route.unique_id_value.clone_ref(py),
            deprecated: route.deprecated,
            tags: route.tags.clone(),
            status_code: route.status_code,
            response_class: route.response_class.clone_ref(py),
            sse_stream: route.sse_stream,
            generator_kind: route.generator_kind,
            stream_item_type: route
                .stream_item_type
                .as_ref()
                .map(|value| value.clone_ref(py)),
            response_model: route
                .response_model
                .as_ref()
                .map(|value| value.clone_ref(py)),
            primary_field: route.response_field.field(py)?,
            additional_fields: route.response_field.additional_fields(py)?,
            request_schema_key: None,
            plan: route.plan.clone_ref(py),
        })
    }

    fn clone_ref(&self, py: Python<'_>) -> Self {
        Self {
            path_format: self.path_format.clone(),
            is_webhook: self.is_webhook,
            method: self.method.clone(),
            name: self.name.clone(),
            endpoint: self.endpoint.clone_ref(py),
            summary: self.summary.clone(),
            description: self.description.clone(),
            response_description: self.response_description.clone(),
            callbacks: self.callbacks.clone_ref(py),
            openapi_extra: self.openapi_extra.as_ref().map(|value| value.clone_ref(py)),
            operation_id: self.operation_id.clone(),
            unique_id: self.unique_id.clone(),
            unique_id_value: self.unique_id_value.clone_ref(py),
            deprecated: self.deprecated,
            tags: self.tags.clone(),
            status_code: self.status_code,
            response_class: self.response_class.clone_ref(py),
            sse_stream: self.sse_stream,
            generator_kind: self.generator_kind,
            stream_item_type: self
                .stream_item_type
                .as_ref()
                .map(|value| value.clone_ref(py)),
            response_model: self
                .response_model
                .as_ref()
                .map(|value| value.clone_ref(py)),
            primary_field: self.primary_field.as_ref().map(|field| field.clone_ref(py)),
            additional_fields: self
                .additional_fields
                .iter()
                .map(|field| field.clone_ref(py))
                .collect(),
            request_schema_key: self.request_schema_key,
            plan: self.plan.clone_ref(py),
        }
    }
}

struct OpenApiAppSnapshot {
    title: String,
    summary: Option<String>,
    description: String,
    openapi_version: String,
    openapi_tags: Py<PyAny>,
    terms_of_service: Option<String>,
    contact: Option<Py<PyAny>>,
    license_info: Option<Py<PyAny>>,
    openapi_external_docs: Option<Py<PyAny>>,
    servers: Py<PyAny>,
    version: Py<PyAny>,
    separate_input_output_schemas: bool,
    operations: Vec<OpenApiRouteSnapshot>,
}

fn fastapi_version_value(app: &PyFastApi) -> PyResult<&Py<PyAny>> {
    if !app.version_is_set {
        return Err(PyAttributeError::new_err(
            "'FastAPI' object has no attribute 'version'",
        ));
    }
    Ok(&app.version)
}

fn fastapi_contact_value(py: Python<'_>, app: &PyFastApi) -> PyResult<Option<Py<PyAny>>> {
    if !app.contact_is_set {
        return Err(PyAttributeError::new_err(
            "'FastAPI' object has no attribute 'contact'",
        ));
    }
    Ok(app.contact.as_ref().map(|value| value.clone_ref(py)))
}

impl OpenApiAppSnapshot {
    fn from_app(py: Python<'_>, app: &PyFastApi) -> PyResult<Self> {
        let route_order = effective_route_order(py, app, IncludedRouteCategory::Http)?;
        let mut operations = route_order
            .iter()
            .filter_map(|route_index| app.routes.get(*route_index))
            .filter(|route| route.include_in_schema)
            .flat_map(|route| route.methods.iter().map(move |method| (route, method)))
            .map(|(route, method)| OpenApiRouteSnapshot::from_route(py, route, method, false))
            .collect::<PyResult<Vec<_>>>()?;
        let webhook_router = app.webhooks.bind(py).extract::<PyRef<'_, PyApiRouter>>()?;
        let webhook_inner = webhook_router.inner_app(py)?;
        let webhook_app = webhook_inner.bind(py).borrow();
        let webhook_route_order =
            effective_route_order(py, &webhook_app, IncludedRouteCategory::Http)?;
        operations.extend(
            webhook_route_order
                .iter()
                .filter_map(|route_index| webhook_app.routes.get(*route_index))
                .filter(|route| webhook_router.include_in_schema && route.include_in_schema)
                .flat_map(|route| route.methods.iter().map(move |method| (route, method)))
                .map(|(route, method)| OpenApiRouteSnapshot::from_route(py, route, method, true))
                .collect::<PyResult<Vec<_>>>()?,
        );
        Ok(Self {
            title: app.title.clone(),
            summary: app.summary.clone(),
            description: app.description.clone(),
            openapi_version: app.openapi_version.clone(),
            openapi_tags: if app.openapi_tags_is_set {
                app.openapi_tags.clone_ref(py)
            } else {
                return Err(PyAttributeError::new_err(
                    "'FastAPI' object has no attribute 'openapi_tags'",
                ));
            },
            terms_of_service: app.terms_of_service.clone(),
            contact: fastapi_contact_value(py, app)?,
            license_info: app.license_info.as_ref().map(|value| value.clone_ref(py)),
            openapi_external_docs: app
                .openapi_external_docs
                .as_ref()
                .map(|value| value.clone_ref(py)),
            servers: app.servers.clone_ref(py),
            version: fastapi_version_value(app)?.clone_ref(py),
            separate_input_output_schemas: app.separate_input_output_schemas,
            operations,
        })
    }
}

fn openapi_request_schema_annotation(
    py: Python<'_>,
    route: &OpenApiRouteSnapshot,
) -> PyResult<Option<Py<PyAny>>> {
    let body_parameters = route.plan.all_body_parameters();
    let aggregate_body = if route.plan.has_form_inputs() {
        form_body_should_embed(py, &body_parameters)?
    } else {
        body_fields_embedded(&body_parameters)
    };
    if aggregate_body {
        let operation_id = route
            .operation_id
            .as_deref()
            .filter(|value| !value.is_empty())
            .unwrap_or(&route.unique_id);
        return aggregate_body_model(py, &format!("Body_{operation_id}"), &body_parameters)
            .map(Some);
    }

    let parameter = if route.plan.has_form_inputs() {
        body_parameters.first().copied()
    } else {
        route.plan.body_parameter()
    };
    Ok(parameter.map(|parameter| parameter.annotation.clone_ref(py)))
}

struct OpenApiCache {
    schema: Py<PyAny>,
    schema_is_set: bool,
    routes_version: Option<u64>,
}

#[pyclass(name = "_FastAPIAsgiApp", module = "fastapi_rs._core")]
struct PyFastApiAsgiApp {
    router: Py<PyAny>,
}

#[pyclass(name = "_APIRouteAsgiApp", module = "fastapi_rs._core")]
struct PyApiRouteAsgiApp {
    owner: Py<PyFastApi>,
    route_index: usize,
    dependency_overrides_provider: Option<Py<PyAny>>,
}

#[pyclass(name = "_APIRouteAsgiCore", module = "fastapi_rs._core")]
struct PyApiRouteAsgiCore {
    owner: Py<PyFastApi>,
    route_index: usize,
    dependency_overrides_provider: Option<Py<PyAny>>,
}

#[pyclass(name = "_FastAPIRouteHandler", module = "fastapi_rs._core")]
struct PyFastApiRouteHandler {
    route: Py<PyAny>,
    response_class: Py<PyAny>,
}

#[pyclass(
    name = "_FastAPIRequestCleanup",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiRequestCleanup {
    records: RefCell<Vec<RouteHandlerCleanupRecord>>,
    previous_scope_value: Option<Py<PyAny>>,
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

#[pyclass(
    name = "_FastAPIHTTPExceptionHandler",
    module = "fastapi_rs._core",
    dict
)]
struct PyFastApiHttpExceptionHandler;

#[pyclass(
    name = "_FastAPIRequestValidationExceptionHandler",
    module = "fastapi_rs._core",
    dict
)]
struct PyFastApiRequestValidationExceptionHandler;

#[pyclass(
    name = "_FastAPIWebSocketRequestValidationExceptionHandler",
    module = "fastapi_rs._core"
)]
struct PyFastApiWebSocketRequestValidationExceptionHandler;

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

#[pyclass(
    name = "_FastAPITelemetrySend",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiTelemetrySend {
    send: Py<PyAny>,
    span_state: Rc<RefCell<FastApiTelemetrySpanState>>,
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
        self.router
            .bind(py)
            .call1((scope, receive, send))
            .map(Bound::unbind)
    }
}

#[pymethods]
impl PyApiRouteAsgiApp {
    fn __call__(
        slf: Py<Self>,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let (owner, route_index, dependency_overrides_provider) = {
            let app = slf.bind(py).borrow();
            (
                app.owner.clone_ref(py),
                app.route_index,
                app.dependency_overrides_provider
                    .as_ref()
                    .map(|provider| provider.clone_ref(py)),
            )
        };
        let has_exception_handlers = scope
            .bind(py)
            .call_method1("__contains__", ("starlette.exception_handlers",))?
            .extract::<bool>()?;
        if !has_exception_handlers {
            return fastapi_route_core_call(
                py,
                owner,
                route_index,
                scope,
                receive,
                send,
                dependency_overrides_provider,
            );
        }

        let exception_handler_context = scope.bind(py).get_item("starlette.exception_handlers")?;
        let exception_handler_context = exception_handler_context.cast::<PyTuple>()?;
        let handlers = PyDict::new(py);
        handlers.call_method1("update", (exception_handler_context.get_item(0)?,))?;
        handlers.call_method1("update", (exception_handler_context.get_item(1)?,))?;
        if handlers.len() == 0 {
            return fastapi_route_core_call(
                py,
                owner,
                route_index,
                scope,
                receive,
                send,
                dependency_overrides_provider,
            );
        }

        let core = Py::new(
            py,
            PyApiRouteAsgiCore {
                owner,
                route_index,
                dependency_overrides_provider,
            },
        )?;
        let kwargs = PyDict::new(py);
        kwargs.set_item("handlers", &handlers)?;
        let middleware = py
            .import("starlette.middleware.exceptions")?
            .getattr("ExceptionMiddleware")?
            .call((core,), Some(&kwargs))?;
        middleware.call1((scope, receive, send)).map(Bound::unbind)
    }
}

#[pymethods]
impl PyApiRouteAsgiCore {
    fn __call__(
        &self,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        fastapi_route_core_call(
            py,
            self.owner.clone_ref(py),
            self.route_index,
            scope,
            receive,
            send,
            self.dependency_overrides_provider
                .as_ref()
                .map(|provider| provider.clone_ref(py)),
        )
    }
}

#[pymethods]
impl PyFastApiRouteHandler {
    fn __call__(&self, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let route = self.route.bind(py);
        let route_state = api_route_state_ref(route)?;
        let (owner, route_index) = api_route_dispatch_owner(py, route, &route_state)?;
        let dependency_overrides_provider = route_state
            .dependency_overrides_provider
            .as_ref()
            .map(|provider| provider.clone_ref(py));
        drop(route_state);
        let request = request.bind(py);
        let scope = request.getattr("scope")?.unbind();
        let receive = request.getattr("_receive")?.unbind();
        into_python_awaitable(
            py,
            FastApiCall::new(
                owner,
                scope,
                receive,
                py.None(),
                FastApiCallOptions {
                    forced_route_index: Some(route_index),
                    route_dependency_overrides_provider: dependency_overrides_provider,
                    router_default: None,
                    provided_request: Some(request.clone().unbind()),
                    response_class_override: Some(self.response_class.clone_ref(py)),
                },
            ),
        )
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

#[pyclass(name = "APIRouter", module = "fastapi.routing")]
pub(crate) struct PyApiRouter {
    inner: ApiRouterInner,
    prefix: String,
    default: Option<Py<PyAny>>,
    dependency_overrides_provider: Option<Py<PyAny>>,
    route_class: Py<PyAny>,
    tag_values: Py<PyAny>,
    deprecated: Option<bool>,
    include_in_schema: bool,
    dependencies: Vec<Py<PyAny>>,
    strict_content_type: Option<bool>,
}

enum ApiRouterInner {
    Owned(Py<PyFastApi>),
    FastApiWeak(Py<PyWeakrefReference>),
}

impl ApiRouterInner {
    fn app(&self, py: Python<'_>) -> PyResult<Py<PyFastApi>> {
        match self {
            Self::Owned(app) => Ok(app.clone_ref(py)),
            Self::FastApiWeak(reference) => reference
                .bind(py)
                .upgrade_as::<PyFastApi>()?
                .map(Bound::unbind)
                .ok_or_else(|| PyRuntimeError::new_err("FastAPI app no longer exists")),
        }
    }
}

struct RouterIncludePolicy<'policy> {
    prefix: &'policy str,
    frontend_prefix: &'policy str,
    responses: &'policy Py<PyDict>,
    response_class: &'policy ResponseClassChoice,
    generate_unique_id_function: &'policy GenerateUniqueIdChoice,
    tags: &'policy [String],
    dependencies: &'policy [Py<PyAny>],
    callbacks: &'policy [Py<PyAny>],
    deprecated: Option<bool>,
    include_in_schema: bool,
    strict_content_type: Option<bool>,
}

#[derive(Clone, Copy)]
struct RouterMergeStarts {
    routes: usize,
    websocket_routes: usize,
    frontend_routes: usize,
}

#[pyclass(name = "DefaultPlaceholder", module = "fastapi.datastructures")]
struct PyFastApiDefaultPlaceholder {
    value: Py<PyAny>,
}

#[pymethods]
impl PyFastApiDefaultPlaceholder {
    #[getter]
    fn value(&self, py: Python<'_>) -> Py<PyAny> {
        self.value.clone_ref(py)
    }

    #[setter]
    fn set_value(&mut self, value: Py<PyAny>) {
        self.value = value;
    }
}

/// Construct FastAPI's default-placeholder sentinel for Rust-owned signatures.
pub(crate) fn default_placeholder(py: Python<'_>, value: Py<PyAny>) -> PyResult<Py<PyAny>> {
    Py::new(py, PyFastApiDefaultPlaceholder { value }).map(Py::into_any)
}

#[pyclass(name = "_OperationRouteDescriptor", module = "fastapi_rs._core")]
struct PyOperationRouteDescriptor {
    method: Py<PyAny>,
    is_router: bool,
    signature: Py<PyAny>,
}

#[pymethods]
impl PyOperationRouteDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Py<PyAny>>,
        _owner: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let signature = match instance {
            Some(_) => bound_operation_signature(py, self.signature.bind(py))?,
            None => self.signature.clone_ref(py),
        };
        let callable = Py::new(
            py,
            PyOperationRouteCallable {
                method: self.method.clone_ref(py),
                instance,
                is_router: self.is_router,
            },
        )?;
        callable
            .bind(py)
            .setattr("__signature__", signature.bind(py))?;
        Ok(callable.into_any())
    }
}

#[pyclass(name = "_OperationRouteCallable", module = "fastapi_rs._core", dict)]
struct PyOperationRouteCallable {
    method: Py<PyAny>,
    instance: Option<Py<PyAny>>,
    is_router: bool,
}

#[pymethods]
impl PyOperationRouteCallable {
    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let mut keyword_receiver_kwargs = None;
        let (instance, first_argument) = match &self.instance {
            Some(instance) => (instance.bind(py).clone(), 0),
            None if !args.is_empty() => (args.get_item(0)?, 1),
            None => {
                let Some(kwargs) = kwargs else {
                    return Err(PyTypeError::new_err(
                        "missing required positional argument: 'self'",
                    ));
                };
                let instance = kwargs.get_item("self")?.ok_or_else(|| {
                    PyTypeError::new_err("missing required positional argument: 'self'")
                })?;
                let copied_kwargs = PyDict::new(py);
                for (key, value) in kwargs.iter() {
                    if key.extract::<String>()? != "self" {
                        copied_kwargs.set_item(key, value)?;
                    }
                }
                keyword_receiver_kwargs = Some(copied_kwargs.unbind());
                (instance, 0)
            }
        };
        let forwarded_kwargs = keyword_receiver_kwargs
            .as_ref()
            .map(|kwargs| kwargs.bind(py))
            .or(kwargs);
        let mut router_kwargs = None;
        let mut dependency_overrides_provider = None;
        let method_instance = if self.is_router {
            let router = instance.extract::<PyRef<'_, PyApiRouter>>()?;
            dependency_overrides_provider = router.route_dependency_overrides_provider(py)?;
            let effective_kwargs = PyDict::new(py);
            if let Some(kwargs) = forwarded_kwargs {
                for (key, value) in kwargs.iter() {
                    effective_kwargs.set_item(key, value)?;
                }
            }
            let route_deprecated = effective_kwargs
                .get_item("deprecated")?
                .map(|value| value.extract::<Option<bool>>())
                .transpose()?
                .flatten();
            effective_kwargs.set_item(
                "deprecated",
                combined_deprecated(route_deprecated, router.deprecated),
            )?;
            let route_include_in_schema = effective_kwargs
                .get_item("include_in_schema")?
                .map(|value| value.extract::<bool>())
                .transpose()?
                .unwrap_or(true);
            effective_kwargs.set_item(
                "include_in_schema",
                route_include_in_schema && router.include_in_schema,
            )?;
            router_kwargs = Some(effective_kwargs.unbind());
            router.inner_app(py)?.into_bound(py).into_any()
        } else {
            instance
        };
        let forwarded_kwargs = router_kwargs
            .as_ref()
            .map(|kwargs| kwargs.bind(py))
            .or(forwarded_kwargs);
        let mut forwarded_arguments = Vec::with_capacity(args.len() + 1);
        forwarded_arguments.push(method_instance);
        forwarded_arguments.extend(args.iter().skip(first_argument));
        let forwarded_arguments = PyTuple::new(py, forwarded_arguments)?;
        let result = self
            .method
            .bind(py)
            .call(&forwarded_arguments, forwarded_kwargs)?;
        if self.is_router {
            let mut decorator = result.extract::<PyRefMut<'_, PyOperationDecorator>>()?;
            decorator.deprecated_precombined = true;
            decorator.dependency_overrides_provider = dependency_overrides_provider;
        }
        Ok(result.unbind())
    }
}

fn bound_operation_signature<'py>(
    py: Python<'py>,
    signature: &Bound<'py, PyAny>,
) -> PyResult<Py<PyAny>> {
    let parameters = signature.getattr("parameters")?.call_method0("values")?;
    let parameter_values = parameters
        .try_iter()?
        .map(|parameter| parameter.map(Bound::unbind))
        .collect::<PyResult<Vec<_>>>()?;
    let bound_parameters = PyList::new(py, parameter_values.into_iter().skip(1))?;
    let replace_kwargs = PyDict::new(py);
    replace_kwargs.set_item("parameters", bound_parameters)?;
    signature
        .call_method("replace", (), Some(&replace_kwargs))
        .map(Bound::unbind)
}

fn install_route_operation_descriptors(
    py: Python<'_>,
    module: &Bound<'_, PyModule>,
) -> PyResult<()> {
    let mut signatures = crate::application_signatures::ApplicationSignatureBuilder::new(module)?;
    let signature = signatures.build_signature(py, "operation")?;
    let fast_api_type = py.get_type::<PyFastApi>();
    let api_router_type = py.get_type::<PyApiRouter>();
    api_route_type(py)?.setattr("__signature__", signatures.build_signature(py, "APIRoute")?)?;
    api_router_type.setattr(
        "__signature__",
        signatures.build_signature(py, "APIRouter")?,
    )?;
    for name in [
        "get", "put", "post", "delete", "options", "head", "patch", "trace",
    ] {
        let method = fast_api_type.getattr(name)?.unbind();
        let fast_api_descriptor = Py::new(
            py,
            PyOperationRouteDescriptor {
                method: method.clone_ref(py),
                is_router: false,
                signature: signature.clone_ref(py),
            },
        )?;
        fast_api_type.setattr(name, fast_api_descriptor)?;
        let router_descriptor = Py::new(
            py,
            PyOperationRouteDescriptor {
                method,
                is_router: true,
                signature: signature.clone_ref(py),
            },
        )?;
        api_router_type.setattr(name, router_descriptor)?;
    }

    for (name, contract_name) in [
        ("openapi", "openapi"),
        ("websocket", "websocket"),
        ("include_router", "include_router"),
        ("frontend", "frontend"),
        ("on_event", "on_event"),
        ("middleware", "middleware"),
        ("exception_handler", "exception_handler"),
    ] {
        let method = fast_api_type.getattr(name)?.unbind();
        let signature = signatures.build_signature(py, contract_name)?;
        let descriptor = Py::new(
            py,
            PyOperationRouteDescriptor {
                method,
                is_router: false,
                signature,
            },
        )?;
        fast_api_type.setattr(name, descriptor)?;
    }
    fast_api_type.setattr("__signature__", signatures.build_signature(py, "FastAPI")?)?;
    Ok(())
}

#[pyfunction]
fn generate_unique_id(route: &Bound<'_, PyAny>) -> PyResult<String> {
    let name = route.getattr("name")?.extract::<String>()?;
    let path = route.getattr("path_format")?.extract::<String>()?;
    let mut methods = route.getattr("methods")?.try_iter()?;
    let method = methods
        .next()
        .ok_or_else(|| PyValueError::new_err("route has no methods"))??
        .extract::<String>()?;
    Ok(operation_id(&name, &path, &method))
}

fn default_fastapi_version() -> Py<PyAny> {
    Python::attach(|py| PyString::new(py, "0.1.0").into_any().unbind())
}

#[pymethods]
impl PyFastApi {
    // Native ASGI calls return Python awaitables, but their PyO3 call slot is
    // synchronous. Expose the standard coroutine markers so Starlette's
    // TestClient recognizes FastAPI instances as ASGI3 applications.
    #[getter(_is_coroutine)]
    fn asyncio_coroutine_marker(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        py.import("asyncio")?
            .getattr("coroutines")?
            .getattr("_is_coroutine")
            .map(Bound::unbind)
    }

    #[getter(_is_coroutine_marker)]
    fn inspect_coroutine_marker(&self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        inspect_coroutine_marker(py)
    }

    #[new]
    #[pyo3(signature = (*, telemetry = None, debug = false, routes = None, title = "FastAPI", summary = None, description = "", version = default_fastapi_version(), openapi_url = "/openapi.json", openapi_tags = None, servers = None, docs_url = "/docs", redoc_url = "/redoc", swagger_ui_oauth2_redirect_url = "/docs/oauth2-redirect", swagger_ui_init_oauth = None, swagger_ui_parameters = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, separate_input_output_schemas = true, terms_of_service = None, contact = None, license_info = None, openapi_prefix = "", root_path = "", root_path_in_servers = true, responses = None, callbacks = None, openapi_external_docs = None, webhooks = None, dependencies = None, default_response_class = ResponseClassArgument::Omitted, redirect_slashes = true, middleware = None, exception_handlers = None, on_startup = None, on_shutdown = None, lifespan = None, strict_content_type = true, deprecated = None, include_in_schema = true, **extra))]
    // lint-exception: PyO3 needs one Rust argument per Python constructor keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python FastAPI constructor keyword signature"
    )]
    fn new(
        py: Python<'_>,
        telemetry: Option<Py<PyAny>>,
        debug: bool,
        routes: Option<Py<PyAny>>,
        title: &str,
        summary: Option<String>,
        description: &str,
        version: Py<PyAny>,
        openapi_url: Option<&str>,
        openapi_tags: Option<Py<PyAny>>,
        servers: Option<Py<PyAny>>,
        docs_url: Option<&str>,
        redoc_url: Option<&str>,
        swagger_ui_oauth2_redirect_url: Option<&str>,
        swagger_ui_init_oauth: Option<Py<PyAny>>,
        swagger_ui_parameters: Option<Py<PyAny>>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        separate_input_output_schemas: bool,
        terms_of_service: Option<String>,
        contact: Option<Py<PyAny>>,
        license_info: Option<Py<PyAny>>,
        openapi_prefix: &str,
        root_path: &str,
        root_path_in_servers: bool,
        responses: Option<Py<PyAny>>,
        callbacks: Option<Py<PyAny>>,
        openapi_external_docs: Option<Py<PyAny>>,
        webhooks: Option<Py<PyAny>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        default_response_class: ResponseClassArgument,
        redirect_slashes: bool,
        middleware: Option<Py<PyAny>>,
        exception_handlers: Option<Py<PyAny>>,
        on_startup: Option<Py<PyAny>>,
        on_shutdown: Option<Py<PyAny>>,
        lifespan: Option<Py<PyAny>>,
        strict_content_type: bool,
        deprecated: Option<bool>,
        include_in_schema: bool,
        extra: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        let (telemetry_tracing, telemetry_tracer_provider) = match telemetry {
            Some(telemetry) => {
                let telemetry = telemetry.bind(py);
                let tracing = telemetry
                    .call_method1("get", ("tracing", true))?
                    .extract::<bool>()?;
                let provider = telemetry.call_method1("get", ("tracer_provider", py.None()))?;
                (tracing, (!provider.is_none()).then(|| provider.unbind()))
            }
            None => (true, None),
        };
        if openapi_url.is_some_and(|url| !url.is_empty()) && title.is_empty() {
            return Err(PyAssertionError::new_err(
                "A title must be provided for OpenAPI, e.g.: 'My API'",
            ));
        }
        if openapi_url.is_some_and(|url| !url.is_empty()) && !version.bind(py).is_truthy()? {
            return Err(PyAssertionError::new_err(
                "A version must be provided for OpenAPI, e.g.: '2.1.0'",
            ));
        }
        let responses = response_map_or_empty(py, responses)?;
        let router_callbacks = match callbacks {
            Some(callbacks) if callbacks.bind(py).is_truthy()? => callbacks,
            _ => PyList::empty(py).into_any().unbind(),
        };
        let user_middleware = match middleware {
            Some(middleware) => py
                .import("builtins")?
                .getattr("list")?
                .call1((middleware,))?
                .cast_into::<PyList>()?
                .unbind(),
            None => PyList::empty(py).unbind(),
        };
        let state = py
            .import("starlette.datastructures")?
            .getattr("State")?
            .call0()?
            .unbind();
        let extra = extra
            .map(|extra| extra.clone().into_any().unbind())
            .unwrap_or_else(|| PyDict::new(py).into_any().unbind());
        let servers = match servers {
            Some(servers) if servers.bind(py).is_truthy()? => servers,
            _ => PyList::empty(py).into_any().unbind(),
        };
        let openapi_tags = openapi_tags.unwrap_or_else(|| py.None());
        let constructor_routes = match routes {
            Some(routes) => py
                .import("builtins")?
                .getattr("list")?
                .call1((routes,))?
                .extract::<Vec<Py<PyAny>>>()?,
            None => Vec::new(),
        };
        if !openapi_prefix.is_empty() {
            py.import("logging")?
                .getattr("getLogger")?
                .call1(("fastapi",))?
                .call_method1(
                    "warning",
                    (concat!(
                        "\"openapi_prefix\" has been deprecated in favor of \"root_path\", which ",
                        "follows more closely the ASGI standard, is simpler, and more ",
                        "automatic. Check the docs at ",
                        "https://fastapi.tiangolo.com/advanced/sub-applications/"
                    ),),
                )?;
        }
        let root_path = if root_path.is_empty() {
            openapi_prefix.to_owned()
        } else {
            root_path.to_owned()
        };
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
            let handler = py
                .import("fastapi_rs._core")?
                .getattr("http_exception_handler")?;
            exception_handlers.set_item(http_exception_type, handler)?;
        }
        let request_validation_exception_type = crate::errors::request_validation_error_type(py);
        if !exception_handlers.contains(&request_validation_exception_type)? {
            let handler = py
                .import("fastapi_rs._core")?
                .getattr("request_validation_exception_handler")?;
            exception_handlers.set_item(request_validation_exception_type, handler)?;
        }
        let websocket_validation_exception_type =
            crate::errors::websocket_request_validation_error_type(py);
        if !exception_handlers.contains(&websocket_validation_exception_type)? {
            exception_handlers.set_item(
                websocket_validation_exception_type,
                Py::new(py, PyFastApiWebSocketRequestValidationExceptionHandler)?.into_any(),
            )?;
        }
        let mut docs_router = RouteTable::new();
        let mut docs_routes = Vec::new();
        if openapi_url.is_some_and(|url| !url.is_empty()) {
            if let Some(path) = docs_url.filter(|path| !path.is_empty()) {
                docs_router
                    .add_route(path, ["GET"])
                    .map_err(|error| PyValueError::new_err(error.to_string()))?;
                docs_routes.push(FastApiDocsRoute::SwaggerUi);
                if let Some(redirect_path) =
                    swagger_ui_oauth2_redirect_url.filter(|path| !path.is_empty())
                {
                    docs_router
                        .add_route(redirect_path, ["GET"])
                        .map_err(|error| PyValueError::new_err(error.to_string()))?;
                    docs_routes.push(FastApiDocsRoute::OAuth2Redirect);
                }
            }
            if let Some(path) = redoc_url.filter(|path| !path.is_empty()) {
                docs_router
                    .add_route(path, ["GET"])
                    .map_err(|error| PyValueError::new_err(error.to_string()))?;
                docs_routes.push(FastApiDocsRoute::ReDoc);
            }
        }
        let route_surface = PyList::empty(py);
        for route in &constructor_routes {
            route_surface.append(route.bind(py))?;
        }
        if let Some(path) = openapi_url.filter(|path| !path.is_empty()) {
            let response_endpoint = py.import("starlette.responses")?.getattr("Response")?;
            route_surface.append(
                new_public_starlette_route(py, path, &response_endpoint, "openapi", false)?
                    .bind(py),
            )?;
            if let Some(path) = docs_url.filter(|path| !path.is_empty()) {
                route_surface.append(
                    new_public_starlette_route(
                        py,
                        path,
                        &response_endpoint,
                        "swagger_ui_html",
                        false,
                    )?
                    .bind(py),
                )?;
                if let Some(path) = swagger_ui_oauth2_redirect_url.filter(|path| !path.is_empty()) {
                    route_surface.append(
                        new_public_starlette_route(
                            py,
                            path,
                            &response_endpoint,
                            "swagger_ui_redirect",
                            false,
                        )?
                        .bind(py),
                    )?;
                }
            }
            if let Some(path) = redoc_url.filter(|path| !path.is_empty()) {
                route_surface.append(
                    new_public_starlette_route(py, path, &response_endpoint, "redoc_html", false)?
                        .bind(py),
                )?;
            }
        }
        let lifespan = FastApiLifespan::new(py, on_startup, on_shutdown, lifespan)?;
        let webhooks = match webhooks {
            Some(webhooks) if webhooks.bind(py).is_none() => webhooks,
            Some(webhooks) if webhooks.bind(py).is_truthy()? => webhooks,
            _ => Py::new(
                py,
                PyApiRouter::new(
                    py,
                    "",
                    None,
                    None,
                    ResponseClassArgument::Omitted,
                    None,
                    None,
                    None,
                    true,
                    None,
                    None,
                    RouteClassArgument::Omitted,
                    None,
                    None,
                    None,
                    None,
                    true,
                    GenerateUniqueIdArgument::Omitted,
                    None,
                )?,
            )?
            .into_any(),
        };
        let mut app = Self {
            public_instance: None,
            state,
            extra,
            debug,
            route_scope_prefix: String::new(),
            is_router_inner: false,
            router_tags: PyList::empty(py).into_any().unbind(),
            router_dependencies: Vec::new(),
            router_callbacks,
            router_route_class: None,
            router_deprecated: deprecated,
            router_include_in_schema: include_in_schema,
            title: title.to_owned(),
            summary,
            description: description.to_owned(),
            version,
            version_is_set: true,
            openapi_version: "3.1.0".to_owned(),
            openapi_url: openapi_url.map(str::to_owned),
            openapi_tags,
            openapi_tags_is_set: true,
            servers,
            root_path,
            root_path_in_servers,
            docs_url: docs_url.map(str::to_owned),
            redoc_url: redoc_url.map(str::to_owned),
            swagger_ui_oauth2_redirect_url: swagger_ui_oauth2_redirect_url.map(str::to_owned),
            swagger_ui_init_oauth,
            swagger_ui_parameters,
            generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
            separate_input_output_schemas,
            terms_of_service,
            contact,
            contact_is_set: true,
            license_info,
            openapi_external_docs,
            webhooks,
            dependencies: dependencies.unwrap_or_default(),
            responses,
            default_response_class: default_response_class.into_choice(py)?,
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
            constructor_routes,
            route_surface: route_surface.unbind(),
            routes: Vec::new(),
            route_dispatch_order: Vec::new(),
            router_includes: Vec::new(),
            routes_version: AtomicU64::new(0),
            openapi_cache: Mutex::new(OpenApiCache {
                schema: py.None(),
                schema_is_set: true,
                routes_version: None,
            }),
            mounted_routes: Vec::new(),
            frontend_routes: Vec::new(),
            websocket_routes: Vec::new(),
            user_middleware,
            middleware_stack: None,
            router_view: None,
            telemetry_tracing,
            telemetry_tracer_provider,
        };
        register_constructor_websocket_routes(&mut app, py)?;
        Ok(app)
    }

    #[getter]
    fn router(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        if let Some(router) = slf.bind(py).borrow().router_view.as_ref() {
            return Ok(router.clone_ref(py));
        }
        let router = Py::new(py, PyApiRouter::from_fastapi_app(slf.bind(py))?)?.into_any();
        slf.bind(py).borrow_mut().router_view = Some(router.clone_ref(py));
        Ok(router)
    }

    #[setter]
    fn set_router(&mut self, router: Py<PyAny>) {
        self.router_view = Some(router);
    }

    #[getter]
    fn state(&self, py: Python<'_>) -> Py<PyAny> {
        self.state.clone_ref(py)
    }

    #[getter]
    fn extra(&self, py: Python<'_>) -> Py<PyAny> {
        self.extra.clone_ref(py)
    }

    #[setter]
    fn set_extra(&mut self, extra: Py<PyAny>) {
        self.extra = extra;
    }

    #[getter]
    fn debug(&self) -> bool {
        self.debug
    }

    #[setter]
    fn set_debug(&mut self, debug: bool) {
        self.debug = debug;
    }

    #[getter]
    fn title(&self) -> &str {
        &self.title
    }

    #[setter]
    fn set_title(&mut self, title: String) {
        self.title = title;
    }

    #[getter]
    fn summary(&self) -> Option<&str> {
        self.summary.as_deref()
    }

    #[setter]
    fn set_summary(&mut self, summary: Option<String>) {
        self.summary = summary;
    }

    #[getter]
    fn description(&self) -> &str {
        &self.description
    }

    #[setter]
    fn set_description(&mut self, description: String) {
        self.description = description;
    }

    #[getter]
    fn version(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(fastapi_version_value(self)?.clone_ref(py))
    }

    #[setter]
    fn set_version(&mut self, version: Py<PyAny>) {
        self.version = version;
        self.version_is_set = true;
    }

    #[getter]
    fn terms_of_service(&self) -> Option<&str> {
        self.terms_of_service.as_deref()
    }

    #[setter]
    fn set_terms_of_service(&mut self, terms_of_service: Option<String>) {
        self.terms_of_service = terms_of_service;
    }

    #[getter]
    fn contact(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(fastapi_contact_value(py, self)?.unwrap_or_else(|| py.None()))
    }

    #[setter]
    fn set_contact(&mut self, contact: Option<Py<PyAny>>) {
        self.contact = contact;
        self.contact_is_set = true;
    }

    #[getter]
    fn license_info(&self, py: Python<'_>) -> Py<PyAny> {
        self.license_info
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[setter]
    fn set_license_info(&mut self, license_info: Option<Py<PyAny>>) {
        self.license_info = license_info;
    }

    #[getter]
    fn openapi_version(&self) -> &str {
        &self.openapi_version
    }

    #[setter]
    fn set_openapi_version(&mut self, openapi_version: String) {
        self.openapi_version = openapi_version;
    }

    #[getter]
    fn separate_input_output_schemas(&self) -> bool {
        self.separate_input_output_schemas
    }

    #[setter]
    fn set_separate_input_output_schemas(&mut self, value: bool) {
        self.separate_input_output_schemas = value;
    }

    #[getter]
    fn openapi_url(&self, py: Python<'_>) -> Py<PyAny> {
        self.openapi_url
            .as_deref()
            .map(|url| PyString::new(py, url).into_any().unbind())
            .unwrap_or_else(|| py.None())
    }

    #[setter]
    fn set_openapi_url(&mut self, openapi_url: Option<String>) {
        self.openapi_url = openapi_url;
    }

    #[getter]
    fn servers(&self, py: Python<'_>) -> Py<PyAny> {
        self.servers.clone_ref(py)
    }

    #[setter]
    fn set_servers(&mut self, servers: Py<PyAny>) {
        self.servers = servers;
    }

    #[getter]
    fn swagger_ui_oauth2_redirect_url(&self, py: Python<'_>) -> Py<PyAny> {
        self.swagger_ui_oauth2_redirect_url
            .as_deref()
            .map(|url| PyString::new(py, url).into_any().unbind())
            .unwrap_or_else(|| py.None())
    }

    #[setter]
    fn set_swagger_ui_oauth2_redirect_url(
        &mut self,
        swagger_ui_oauth2_redirect_url: Option<String>,
    ) {
        self.swagger_ui_oauth2_redirect_url = swagger_ui_oauth2_redirect_url;
    }

    #[getter]
    fn swagger_ui_parameters(&self, py: Python<'_>) -> Py<PyAny> {
        self.swagger_ui_parameters
            .as_ref()
            .map(|value| value.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[setter]
    fn set_swagger_ui_parameters(&mut self, swagger_ui_parameters: Option<Py<PyAny>>) {
        self.swagger_ui_parameters = swagger_ui_parameters;
    }

    #[getter]
    fn docs_url(&self) -> Option<&str> {
        self.docs_url.as_deref()
    }

    #[setter]
    fn set_docs_url(&mut self, docs_url: Option<String>) {
        self.docs_url = docs_url;
    }

    #[getter]
    fn redoc_url(&self) -> Option<&str> {
        self.redoc_url.as_deref()
    }

    #[setter]
    fn set_redoc_url(&mut self, redoc_url: Option<String>) {
        self.redoc_url = redoc_url;
    }

    #[getter]
    fn root_path(&self) -> &str {
        &self.root_path
    }

    #[setter]
    fn set_root_path(&mut self, root_path: String) {
        self.root_path = root_path;
    }

    #[getter]
    fn root_path_in_servers(&self) -> bool {
        self.root_path_in_servers
    }

    #[setter]
    fn set_root_path_in_servers(&mut self, root_path_in_servers: bool) {
        self.root_path_in_servers = root_path_in_servers;
    }

    #[getter]
    fn openapi_tags(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        if !self.openapi_tags_is_set {
            return Err(PyAttributeError::new_err(
                "'FastAPI' object has no attribute 'openapi_tags'",
            ));
        }
        Ok(self.openapi_tags.clone_ref(py))
    }

    #[setter]
    fn set_openapi_tags(&mut self, openapi_tags: Py<PyAny>) {
        self.openapi_tags = openapi_tags;
        self.openapi_tags_is_set = true;
    }

    #[getter]
    fn webhooks(&self, py: Python<'_>) -> Py<PyAny> {
        self.webhooks.clone_ref(py)
    }

    #[setter]
    fn set_webhooks(&mut self, webhooks: Py<PyAny>) {
        self.webhooks = webhooks;
    }

    #[getter]
    fn routes(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyList>> {
        refresh_included_router_routes(py, &slf)?;
        Ok(slf.bind(py).borrow().route_surface.clone_ref(py))
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
        let cache = self
            .openapi_cache
            .lock()
            .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
        if !cache.schema_is_set {
            return Err(PyAttributeError::new_err(
                "'FastAPI' object has no attribute 'openapi_schema'",
            ));
        }
        Ok(cache.schema.clone_ref(py))
    }

    #[setter]
    fn set_openapi_schema(&self, schema: Py<PyAny>) -> PyResult<()> {
        let mut cache = self
            .openapi_cache
            .lock()
            .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
        cache.schema = schema;
        cache.schema_is_set = true;
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
        self.user_middleware
            .bind(py)
            .call_method1("insert", (0, registration))?;
        Ok(())
    }

    fn middleware(
        slf: Py<Self>,
        py: Python<'_>,
        middleware_type: &str,
    ) -> PyResult<Py<PyMiddlewareDecorator>> {
        let _ = middleware_type;
        Py::new(py, PyMiddlewareDecorator { app: slf })
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    // Distinguish omission (infer from the endpoint return annotation) from explicit None (opt out).
    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
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
        signature = (path, *, response_model = omitted_response_model(), status_code = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, include_in_schema = true, deprecated = None, operation_id = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, response_class = ResponseClassArgument::Omitted, name = None, callbacks = None, openapi_extra = None),
        text_signature = "($self, path, *, response_model=None, status_code=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, tags=None, dependencies=None, summary=None, description=None, response_description=\"Successful Response\", responses=None, include_in_schema=True, deprecated=None, operation_id=None, generate_unique_id_function=None, response_class=None, name=None, callbacks=None, openapi_extra=None)"
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
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        include_in_schema: bool,
        deprecated: Option<bool>,
        operation_id: Option<String>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        response_class: ResponseClassArgument,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks,
                openapi_extra,
                name,
            },
        )
    }

    #[pyo3(
        signature = (path, *, response_model = omitted_response_model(), status_code = None, tags = None, dependencies = None, summary = None, description = None, response_description = "Successful Response", responses = None, deprecated = None, methods = None, operation_id = None, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false, include_in_schema = true, response_class = ResponseClassArgument::Omitted, name = None, openapi_extra = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted),
        text_signature = "($self, path, *, response_model=None, status_code=None, tags=None, dependencies=None, summary=None, description=None, response_description='Successful Response', responses=None, deprecated=None, methods=None, operation_id=None, response_model_include=None, response_model_exclude=None, response_model_by_alias=True, response_model_exclude_unset=False, response_model_exclude_defaults=False, response_model_exclude_none=False, include_in_schema=True, response_class=None, name=None, openapi_extra=None, generate_unique_id_function=None)"
    )]
    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve FastAPI.api_route's reviewed keyword signature"
    )]
    fn api_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: Option<u16>,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        summary: Option<String>,
        description: Option<String>,
        response_description: &str,
        responses: Option<Py<PyAny>>,
        deprecated: Option<bool>,
        methods: Option<Py<PyAny>>,
        operation_id: Option<String>,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
        include_in_schema: bool,
        response_class: ResponseClassArgument,
        name: Option<String>,
        openapi_extra: Option<Py<PyAny>>,
        generate_unique_id_function: GenerateUniqueIdArgument,
    ) -> PyResult<Py<PyOperationDecorator>> {
        let normalized_methods = PySet::empty(py)?;
        if let Some(methods) = methods {
            for method in methods.bind(py).try_iter()? {
                normalized_methods.add(method?.call_method0("upper")?)?;
            }
        } else {
            normalized_methods.add("GET")?;
        }
        let callback_methods = normalized_methods
            .iter()
            .map(|method| method.extract::<String>())
            .collect::<PyResult<Vec<_>>>()?;
        let method = callback_methods.first().cloned().unwrap_or_default();
        let decorator = operation_decorator(
            slf,
            py,
            path,
            &method,
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
                strict_content_type: StrictContentTypeArgument::Omitted,
                response_class: response_class.into_choice(py)?,
                response_description: Some(response_description.to_owned()),
                responses,
                summary,
                description,
                operation_id,
                deprecated,
                tags,
                dependencies: dependencies.unwrap_or_default(),
                callbacks: None,
                openapi_extra,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                name,
            },
        )?;
        {
            let mut decorator = decorator.bind(py).borrow_mut();
            decorator.method = method;
            decorator.callback_methods = callback_methods;
        }
        Ok(decorator)
    }

    #[pyo3(
        signature = (path, endpoint, *, dependencies = None, description = None, methods = None, include_in_schema = true, name = None, callbacks = None, openapi_extra = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, deprecated = None, tags = None),
        text_signature = "($self, path, endpoint, *, dependencies=None, description=None, methods=None, include_in_schema=True, name=None, callbacks=None, openapi_extra=None, generate_unique_id_function=None, deprecated=None, tags=None)"
    )]
    // lint-exception: preserve the supported FastAPI.add_api_route keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the supported FastAPI.add_api_route keyword signature"
    )]
    fn add_api_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        endpoint: Py<PyAny>,
        dependencies: Option<Vec<Py<PyAny>>>,
        description: Option<String>,
        methods: Option<Py<PyAny>>,
        include_in_schema: bool,
        name: Option<String>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        deprecated: Option<bool>,
        tags: Option<Vec<String>>,
    ) -> PyResult<()> {
        let normalized_methods = PySet::empty(py)?;
        if let Some(methods) = methods {
            for method in methods.bind(py).try_iter()? {
                normalized_methods.add(method?.call_method0("upper")?)?;
            }
        } else {
            normalized_methods.add("GET")?;
        }
        let callback_methods = normalized_methods
            .iter()
            .map(|method| method.extract::<String>())
            .collect::<PyResult<Vec<_>>>()?;
        let decorator = Self::api_route(
            slf,
            py,
            path,
            Some(py.NotImplemented()),
            None,
            None,
            dependencies,
            None,
            description,
            "Successful Response",
            None,
            None,
            None,
            None,
            None,
            None,
            true,
            false,
            false,
            false,
            include_in_schema,
            ResponseClassArgument::Omitted,
            name,
            openapi_extra,
            generate_unique_id_function,
        )?;
        decorator.bind(py).borrow_mut().callbacks = callbacks;
        register_multi_method_api_route(
            py,
            decorator,
            endpoint,
            callback_methods,
            tags,
            deprecated,
            false,
        )
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
        let route_index = self.mounted_routes.len();
        self.route_surface.bind(py).append(&mount)?;
        self.mounted_routes.push(mount.unbind());
        self.route_dispatch_order
            .push(RouteDispatchEntry::MountedRoute(route_index));
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
        let route_index = self.mounted_routes.len();
        self.route_surface.bind(py).append(&route_object)?;
        self.mounted_routes.push(route_object.unbind());
        self.route_dispatch_order
            .push(RouteDispatchEntry::MountedRoute(route_index));
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
        let route_index = self.mounted_routes.len();
        self.route_surface.bind(py).append(&route)?;
        self.mounted_routes.push(route.unbind());
        self.route_dispatch_order
            .push(RouteDispatchEntry::MountedRoute(route_index));
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
        add_raw_websocket_route(self, py, path, endpoint.bind(py), name.as_deref())?;
        let route_index = self.websocket_routes.len() - 1;
        self.route_dispatch_order
            .push(RouteDispatchEntry::ApiWebSocketRoute(route_index));
        Ok(())
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

    #[pyo3(signature = (router, *, prefix = "", tags = None, dependencies = None, responses = None, deprecated = None, include_in_schema = true, default_response_class = ResponseClassArgument::Omitted, callbacks = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted))]
    // lint-exception: preserve FastAPI's include_router keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible include_router signature"
    )]
    fn include_router(
        slf: Py<Self>,
        py: Python<'_>,
        router: Py<PyApiRouter>,
        prefix: &str,
        tags: Option<Vec<FastApiTag>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        responses: Option<Py<PyAny>>,
        deprecated: Option<bool>,
        include_in_schema: bool,
        default_response_class: ResponseClassArgument,
        callbacks: Option<Py<PyAny>>,
        generate_unique_id_function: GenerateUniqueIdArgument,
    ) -> PyResult<()> {
        let tags: Option<Vec<String>> =
            tags.map(|tags| tags.into_iter().map(|tag| tag.0).collect());
        let include_responses = response_map_or_empty(py, responses)?;
        let include_response_class = default_response_class.into_choice(py)?;
        let include_generate_unique_id_function = generate_unique_id_function.into_choice(py)?;
        let router_callbacks = {
            let destination = slf.bind(py).borrow();
            callback_values(destination.router_callbacks.bind(py))?
        };
        let include_callbacks =
            inherited_callback_values(py, &router_callbacks, callbacks.as_ref())?;
        let source_inner = { router.bind(py).borrow().inner_app(py)? };
        refresh_included_router_routes(py, &source_inner)?;
        {
            let source = source_inner.bind(py).borrow();
            validate_empty_path_router_include(&source.routes, prefix)?;
        }
        let dependency_overrides_provider = fastapi_public_instance(py, &slf)?;
        let mut destination_guard = slf.bind(py).borrow_mut();
        let destination = &mut *destination_guard;
        let parent_responses = route_response_declarations(py, Some(&destination.responses))?;
        let include_responses = route_response_declarations(py, Some(&include_responses))?;
        let inherited_responses =
            merge_response_maps(py, parent_responses.bind(py), include_responses.bind(py))?;
        let inherited_response_class = ResponseClassChoice::first_explicit(
            py,
            &[&include_response_class, &destination.default_response_class],
        );
        let inherited_generate_unique_id_function = GenerateUniqueIdChoice::first_explicit(
            py,
            &[
                &include_generate_unique_id_function,
                &destination.generate_unique_id_function,
            ],
        );
        let router_object = router.clone_ref(py).into_any();
        let include_prefix = prefix.to_owned();
        let frontend_merge_prefix = include_prefix.clone();
        let router = router.bind(py).borrow();
        let prefix = combined_router_prefix(prefix, &router.prefix)?;
        let tags = tags.unwrap_or_default();
        let mut inherited_dependencies = destination
            .dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        inherited_dependencies.extend(dependencies.unwrap_or_default());
        let source = source_inner.bind(py).borrow();
        let route_position = destination.routes.len();
        let websocket_route_position = destination.websocket_routes.len();
        let frontend_route_position = destination.frontend_routes.len();
        let source_route_indexes =
            (route_position..route_position + source.routes.len()).collect::<Vec<_>>();
        let source_websocket_route_indexes = (websocket_route_position
            ..websocket_route_position + source.websocket_routes.len())
            .collect::<Vec<_>>();
        let source_frontend_route_indexes = (frontend_route_position
            ..frontend_route_position + source.frontend_routes.len())
            .collect::<Vec<_>>();
        let strict_content_type = destination.strict_content_type;
        merge_router_routes(
            py,
            destination,
            &source_inner,
            &source,
            Some(&dependency_overrides_provider),
            RouterIncludePolicy {
                prefix: &prefix,
                frontend_prefix: &frontend_merge_prefix,
                responses: &inherited_responses,
                response_class: &inherited_response_class,
                generate_unique_id_function: &inherited_generate_unique_id_function,
                tags: &tags,
                dependencies: &inherited_dependencies,
                callbacks: &include_callbacks,
                deprecated,
                include_in_schema,
                strict_content_type,
            },
        )?;
        let effective_route_contexts = PyList::empty(py);
        for route_index in &source_route_indexes {
            let route = destination
                .routes
                .get(*route_index)
                .ok_or_else(|| PyRuntimeError::new_err("included public route context was lost"))?;
            effective_route_contexts.append(route.public_route.bind(py))?;
        }
        let public_route = Py::new(
            py,
            PyFastApiIncludedRouter {
                original_router: router_object.clone_ref(py),
                effective_route_contexts: effective_route_contexts.clone().unbind(),
            },
        )?
        .into_any();
        destination
            .route_surface
            .bind(py)
            .append(public_route.bind(py))?;
        destination.router_includes.push(FastApiRouterInclude {
            route_position,
            websocket_route_position,
            frontend_route_position,
            router: router_object,
            merge_prefix: prefix,
            frontend_merge_prefix,
            responses: inherited_responses.clone_ref(py),
            response_class: inherited_response_class.clone_ref(py),
            generate_unique_id_function: inherited_generate_unique_id_function.clone_ref(py),
            tags: tags.clone(),
            dependencies: inherited_dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py))
                .collect(),
            callbacks: include_callbacks
                .iter()
                .map(|callback| callback.clone_ref(py))
                .collect(),
            deprecated,
            include_in_schema,
            strict_content_type,
            public_route,
            source_route_cursor: source.routes.len(),
            source_route_indexes: source_route_indexes.clone(),
            source_websocket_route_cursor: source.websocket_routes.len(),
            source_websocket_route_indexes,
            source_frontend_route_cursor: source.frontend_routes.len(),
            source_frontend_route_indexes,
            fields: IncludedFieldBranch::from_router_indexes(&source, &source_route_indexes),
        });
        let include_index = destination.router_includes.len() - 1;
        destination
            .route_dispatch_order
            .push(RouteDispatchEntry::RouterInclude(include_index));
        destination.lifespan.include_router(py, &source.lifespan)?;
        destination.bump_routes_version();
        drop(source);
        drop(router);
        drop(destination_guard);
        synchronize_included_route_orders(py, &slf)?;
        Ok(())
    }

    fn openapi(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        refresh_included_router_routes(py, &slf)?;
        let (routes_version, cached_schema, cached_routes_version) = {
            let app = slf.bind(py).borrow();
            let cache = app
                .openapi_cache
                .lock()
                .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
            if !cache.schema_is_set {
                return Err(PyAttributeError::new_err(
                    "'FastAPI' object has no attribute 'openapi_schema'",
                ));
            }
            (
                app.routes_version.load(Ordering::Relaxed),
                cache.schema.clone_ref(py),
                cache.routes_version,
            )
        };
        if cached_routes_version == Some(routes_version) && cached_schema.bind(py).is_truthy()? {
            return Ok(cached_schema);
        }

        let schema = Self::openapi_document(&slf, py, None)?;
        #[cfg(feature = "fault-injection")]
        if crate::fault_injection::take_openapi_cache_publish_before() {
            return Err(PyRuntimeError::new_err(
                "Fault injected at openapi.cache.publish.before",
            ));
        }
        let retired = {
            let app = slf.bind(py).borrow();
            let mut cache = app
                .openapi_cache
                .lock()
                .map_err(|_| PyRuntimeError::new_err("OpenAPI schema cache is unavailable"))?;
            let retired = std::mem::replace(&mut cache.schema, schema.clone_ref(py));
            cache.schema_is_set = true;
            cache.routes_version = Some(routes_version);
            retired
        };
        drop(retired);
        Ok(schema)
    }

    #[pyo3(
        signature = (name, /, **path_params),
        text_signature = "($self, name, /, **path_params)"
    )]
    fn url_path_for(
        slf: Py<Self>,
        py: Python<'_>,
        name: &str,
        path_params: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        refresh_included_router_routes(py, &slf)?;
        let empty_path_params = PyDict::new(py);
        let path_params = path_params.unwrap_or(&empty_path_params);
        let mut supplied_names = path_params.keys().extract::<Vec<String>>()?;
        supplied_names.sort();

        let (http_order, websocket_order) = {
            let app = slf.bind(py).borrow();
            (
                effective_route_order(py, &app, IncludedRouteCategory::Http)?,
                effective_route_order(py, &app, IncludedRouteCategory::WebSocket)?,
            )
        };

        let matching_route = {
            let app = slf.bind(py).borrow();
            let mut matching_route = None;
            for route_index in http_order {
                let route = app.routes.get(route_index).ok_or_else(|| {
                    PyRuntimeError::new_err("effective named route order was lost")
                })?;
                if route.name != name {
                    continue;
                }
                let mut expected_names = route
                    .param_convertors
                    .bind(py)
                    .keys()
                    .extract::<Vec<String>>()?;
                expected_names.sort();
                if expected_names == supplied_names {
                    matching_route = Some(route_index);
                    break;
                }
            }
            matching_route
        };

        if let Some(route_index) = matching_route {
            let (url_path_format, param_convertors) = {
                let app = slf.bind(py).borrow();
                let route = app.routes.get(route_index).ok_or_else(|| {
                    PyRuntimeError::new_err("matched named FastAPI route was lost")
                })?;
                (
                    route.url_path_format.clone(),
                    route.param_convertors.clone_ref(py),
                )
            };
            let path = format_route_url_path(py, &url_path_format, &param_convertors, path_params)?;
            return py
                .import("starlette.datastructures")?
                .getattr("URLPath")?
                .call1((path, "http"))
                .map(Bound::unbind);
        }

        let no_match_type = py.import("starlette.routing")?.getattr("NoMatchFound")?;
        let websocket_routes = {
            let app = slf.bind(py).borrow();
            let mut matches = Vec::new();
            for route_index in websocket_order {
                let route = app.websocket_routes.get(route_index).ok_or_else(|| {
                    PyRuntimeError::new_err("effective WebSocket route order was lost")
                })?;
                if route.name != name {
                    continue;
                }
                let mut expected_names = route
                    .param_convertors
                    .bind(py)
                    .keys()
                    .extract::<Vec<String>>()?;
                expected_names.sort();
                if expected_names == supplied_names {
                    matches.push((route.path.clone(), route.param_convertors.clone_ref(py)));
                }
            }
            matches
        };
        for (path, param_convertors) in websocket_routes {
            let path_format = route_path_format(py, &path)?;
            let path = match format_route_url_path(py, &path_format, &param_convertors, path_params)
            {
                Ok(path) => path,
                Err(error) if error.is_instance(py, &no_match_type) => continue,
                Err(error) => return Err(error),
            };
            return py
                .import("starlette.datastructures")?
                .getattr("URLPath")?
                .call1((path, "websocket"))
                .map(Bound::unbind);
        }

        let starlette_routes =
            collect_http_dispatch_candidates(py, &slf, true, "", &mut HashSet::new())?;
        for candidate in starlette_routes {
            let HttpDispatchCandidate::StarletteRoute(route) = candidate else {
                continue;
            };
            match route
                .bind(py)
                .call_method("url_path_for", (name,), Some(path_params))
            {
                Ok(url_path) => return Ok(url_path.unbind()),
                Err(error) if error.is_instance(py, &no_match_type) => {}
                Err(error) => return Err(error),
            }
        }

        let exception = no_match_type.call1((name, path_params))?;
        Err(PyErr::from_value(exception))
    }

    fn __call__(
        slf: Py<Self>,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let root_path = slf.bind(py).borrow().root_path.clone();
        if !root_path.is_empty() {
            scope.bind(py).set_item("root_path", root_path)?;
        }
        scope
            .bind(py)
            .set_item("app", fastapi_public_instance(py, &slf)?)?;
        let (telemetry_tracing, configured_tracer_provider) = {
            let app = slf.bind(py).borrow();
            (
                app.telemetry_tracing,
                app.telemetry_tracer_provider
                    .as_ref()
                    .map(|provider| provider.clone_ref(py)),
            )
        };
        let stack = Self::middleware_stack_for(slf, py)?;
        if scope.bind(py).get_item("type")?.extract::<String>()? == "http" && telemetry_tracing {
            if let Some(tracer_provider) =
                fastapi_telemetry_tracer_provider(py, configured_tracer_provider)?
            {
                return into_python_awaitable(
                    py,
                    FastApiTelemetryCall {
                        app: stack,
                        tracer_provider,
                        scope,
                        receive,
                        send,
                        span_state: None,
                        pending: false,
                    },
                );
            }
        }
        stack
            .bind(py)
            .call1((scope, receive, send))
            .map(Bound::unbind)
    }
}

fn fastapi_telemetry_tracer_provider(
    py: Python<'_>,
    configured: Option<Py<PyAny>>,
) -> PyResult<Option<Py<PyAny>>> {
    let trace = py.import("opentelemetry.trace")?;
    let configured_is_none = configured.is_none();
    let provider = match configured {
        Some(provider) if provider.bind(py).is_truthy()? => provider,
        Some(_) | None => trace.call_method0("get_tracer_provider")?.unbind(),
    };
    let provider_bound = provider.bind(py);
    if provider_bound.is_instance(&trace.getattr("NoOpTracerProvider")?)? {
        return Ok(None);
    }
    if configured_is_none {
        let provider_type = provider_bound.get_type();
        let provider_module = provider_type.getattr("__module__")?.extract::<String>()?;
        let provider_name = provider_type.getattr("__name__")?.extract::<String>()?;
        if provider_module == "opentelemetry.trace" && provider_name == "ProxyTracerProvider" {
            return Ok(None);
        }
    }
    Ok(Some(provider))
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

#[derive(Clone, Copy)]
enum FastApiDefaultExceptionHandlerKind {
    Http,
    RequestValidation,
}

struct FastApiDefaultExceptionHandlerCall {
    kind: FastApiDefaultExceptionHandlerKind,
    exception: Py<PyAny>,
}

impl AwaitableStateMachine for FastApiDefaultExceptionHandlerCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        let response = match input {
            MachineResume::Start => {
                let exception = self.exception.bind(py);
                match self.kind {
                    FastApiDefaultExceptionHandlerKind::Http => {
                        default_http_exception_response(py, exception)?
                    }
                    FastApiDefaultExceptionHandlerKind::RequestValidation => {
                        default_request_validation_exception_response(py, exception)?
                    }
                }
            }
            MachineResume::Error(error) => return Err(error),
            MachineResume::Value(_) => {
                return Err(PyRuntimeError::new_err(
                    "FastAPI exception handler resumed without an awaited operation",
                ));
            }
        };
        Ok(MachineAction::Complete(response))
    }
}

fn default_http_exception_response(
    py: Python<'_>,
    exception: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let status_code = exception.getattr("status_code")?;
    let has_body = is_body_allowed_for_status_code(py, &status_code)?;
    let response_module = py.import("starlette.responses")?;
    let response_type = if has_body {
        response_module.getattr("JSONResponse")?
    } else {
        response_module.getattr("Response")?
    };
    let kwargs = PyDict::new(py);
    kwargs.set_item("status_code", &status_code)?;
    let headers =
        py.import("builtins")?
            .getattr("getattr")?
            .call1((exception, "headers", py.None()))?;
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

fn default_request_validation_exception_response(
    py: Python<'_>,
    exception: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let encoded_errors = jsonable_encoder_default(py, &exception.call_method0("errors")?)?;
    let content = PyDict::new(py);
    content.set_item("detail", encoded_errors)?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("status_code", 422)?;
    py.import("starlette.responses")?
        .getattr("JSONResponse")?
        .call((content,), Some(&kwargs))
        .map(Bound::unbind)
}

#[pymethods]
impl PyFastApiHttpExceptionHandler {
    #[getter(_is_coroutine)]
    fn asyncio_coroutine_marker(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        py.import("asyncio")?
            .getattr("coroutines")?
            .getattr("_is_coroutine")
            .map(Bound::unbind)
    }

    #[getter(_is_coroutine_marker)]
    fn inspect_coroutine_marker(&self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        inspect_coroutine_marker(py)
    }

    #[pyo3(signature = (request, exc))]
    fn __call__(&self, py: Python<'_>, request: Py<PyAny>, exc: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let _ = request;
        into_python_awaitable(
            py,
            FastApiDefaultExceptionHandlerCall {
                kind: FastApiDefaultExceptionHandlerKind::Http,
                exception: exc,
            },
        )
    }
}

#[pymethods]
impl PyFastApiRequestValidationExceptionHandler {
    #[getter(_is_coroutine)]
    fn asyncio_coroutine_marker(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        py.import("asyncio")?
            .getattr("coroutines")?
            .getattr("_is_coroutine")
            .map(Bound::unbind)
    }

    #[getter(_is_coroutine_marker)]
    fn inspect_coroutine_marker(&self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        inspect_coroutine_marker(py)
    }

    #[pyo3(signature = (request, exc))]
    fn __call__(&self, py: Python<'_>, request: Py<PyAny>, exc: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let _ = request;
        into_python_awaitable(
            py,
            FastApiDefaultExceptionHandlerCall {
                kind: FastApiDefaultExceptionHandlerKind::RequestValidation,
                exception: exc,
            },
        )
    }
}

fn inspect_coroutine_marker(py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
    let version = py.import("sys")?.getattr("version_info")?;
    let major = version.get_item(0)?.extract::<u8>()?;
    let minor = version.get_item(1)?.extract::<u8>()?;
    if major > 3 || (major == 3 && minor >= 13) {
        return py
            .import("inspect")?
            .getattr("_is_coroutine_marker")
            .map(Bound::unbind)
            .map(Some);
    }
    Ok(None)
}

#[pymethods]
impl PyFastApiWebSocketRequestValidationExceptionHandler {
    fn __call__(
        &self,
        py: Python<'_>,
        websocket: Py<PyAny>,
        exception: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let errors = exception.bind(py).call_method0("errors")?;
        let reason = jsonable_encoder_default(py, &errors)?;
        let kwargs = PyDict::new(py);
        kwargs.set_item("code", 1008_u16)?;
        kwargs.set_item("reason", reason)?;
        websocket
            .bind(py)
            .call_method("close", (), Some(&kwargs))
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

struct FastApiTelemetrySpanState {
    context_manager: Option<Py<PyAny>>,
    span: Option<Py<PyAny>>,
    scope: Py<PyAny>,
    response_status: Option<u16>,
    expects_trailers: bool,
    response_terminal: bool,
    ended: bool,
}

impl FastApiTelemetrySpanState {
    fn start(
        py: Python<'_>,
        tracer_provider: &Bound<'_, PyAny>,
        scope: Py<PyAny>,
    ) -> PyResult<Self> {
        let scope_bound = scope.bind(py);
        let method = parse_scope_string(scope_bound, "method", "GET")?;
        let path = parse_scope_string(scope_bound, "path", "/")?;
        let attributes = PyDict::new(py);
        attributes.set_item("http.request.method", &method)?;
        attributes.set_item(
            "network.protocol.version",
            parse_scope_string(scope_bound, "http_version", "1.1")?,
        )?;
        attributes.set_item("url.path", &path)?;
        attributes.set_item(
            "url.scheme",
            parse_scope_string(scope_bound, "scheme", "http")?,
        )?;

        let server = scope_bound.call_method1("get", ("server", py.None()))?;
        if let Ok(server) = server.cast::<PyTuple>() {
            if !server.is_empty() {
                if let Ok(address) = server.get_item(0)?.extract::<String>() {
                    attributes.set_item("server.address", address)?;
                }
            }
            if server.len() > 1 {
                if let Ok(port) = server.get_item(1)?.extract::<i64>() {
                    attributes.set_item("server.port", port)?;
                }
            }
        }

        let trace = py.import("opentelemetry.trace")?;
        let tracer_kwargs = PyDict::new(py);
        tracer_kwargs.set_item("schema_url", FASTAPI_TELEMETRY_SCHEMA_URL)?;
        let tracer = tracer_provider.call_method(
            "get_tracer",
            (concat!("fast", "api"), FASTAPI_TELEMETRY_VERSION),
            Some(&tracer_kwargs),
        )?;
        let headers_type = py.import("starlette.datastructures")?.getattr("Headers")?;
        let headers_kwargs = PyDict::new(py);
        headers_kwargs.set_item("scope", scope_bound)?;
        let headers = headers_type.call((), Some(&headers_kwargs))?;
        let parent_context = py
            .import("opentelemetry.propagate")?
            .call_method1("extract", (headers,))?;
        let kwargs = PyDict::new(py);
        kwargs.set_item("context", parent_context)?;
        kwargs.set_item("kind", trace.getattr("SpanKind")?.getattr("SERVER")?)?;
        kwargs.set_item("attributes", attributes)?;
        kwargs.set_item("record_exception", false)?;
        kwargs.set_item("set_status_on_exception", false)?;
        kwargs.set_item("end_on_exit", true)?;
        let context_manager = tracer
            .call_method("start_as_current_span", (method,), Some(&kwargs))?
            .unbind();
        let span = context_manager.bind(py).call_method0("__enter__")?.unbind();

        Ok(Self {
            context_manager: Some(context_manager),
            span: Some(span),
            scope,
            response_status: None,
            expects_trailers: false,
            response_terminal: false,
            ended: false,
        })
    }

    fn finish(&mut self, py: Python<'_>, error: Option<&PyErr>, incomplete: bool) -> PyResult<()> {
        if self.ended {
            return Ok(());
        }
        self.ended = true;
        let Some(context_manager) = self.context_manager.take() else {
            return Ok(());
        };
        let Some(span) = self.span.take() else {
            return context_manager
                .bind(py)
                .call_method1("__exit__", (py.None(), py.None(), py.None()))
                .map(|_| ());
        };

        let update_result: PyResult<()> = (|| {
            if let Some(status) = self.response_status {
                span.bind(py)
                    .call_method1("set_attribute", ("http.response.status_code", status))?;
            }
            let route = self
                .scope
                .bind(py)
                .call_method1("get", ("route", py.None()))?;
            if !route.is_none() {
                let route_path = if route.hasattr("path_format")? {
                    route.getattr("path_format")?.extract::<String>().ok()
                } else if route.hasattr("path")? {
                    route.getattr("path")?.extract::<String>().ok()
                } else {
                    None
                };
                if let Some(route_path) = route_path {
                    span.bind(py)
                        .call_method1("set_attribute", ("http.route", &route_path))?;
                    let method = parse_scope_string(self.scope.bind(py), "method", "GET")?;
                    span.bind(py)
                        .call_method1("update_name", (format!("{method} {route_path}"),))?;
                }
            }
            let failed = error.is_some()
                || incomplete
                || self.response_status.is_none_or(|status| status >= 500);
            if failed {
                let error_type = match error {
                    Some(error) => Some(fastapi_telemetry_exception_type(py, error)?),
                    None => Some(
                        self.response_status
                            .map(|status| status.to_string())
                            .unwrap_or_else(|| {
                                if incomplete {
                                    "RuntimeError".to_owned()
                                } else {
                                    "incomplete_response".to_owned()
                                }
                            }),
                    ),
                };
                if let Some(error_type) = error_type {
                    span.bind(py)
                        .call_method1("set_attribute", ("error.type", error_type))?;
                }
                let trace = py.import("opentelemetry.trace")?;
                let status = trace
                    .getattr("Status")?
                    .call1((trace.getattr("StatusCode")?.getattr("ERROR")?,))?;
                span.bind(py).call_method1("set_status", (status,))?;
            }
            Ok(())
        })();

        let exit_result = if let Some(error) = error {
            let exception_type = error.get_type(py).unbind().into_any();
            let exception_value = error.value(py).clone().unbind().into_any();
            let traceback = error
                .traceback(py)
                .map(|traceback| traceback.unbind().into_any())
                .unwrap_or_else(|| py.None());
            context_manager
                .bind(py)
                .call_method1("__exit__", (exception_type, exception_value, traceback))
                .map(|_| ())
        } else {
            context_manager
                .bind(py)
                .call_method1("__exit__", (py.None(), py.None(), py.None()))
                .map(|_| ())
        };

        update_result.and(exit_result)
    }
}

fn fastapi_telemetry_exception_type(py: Python<'_>, error: &PyErr) -> PyResult<String> {
    let exception_type = error.get_type(py);
    let module = exception_type.getattr("__module__")?.extract::<String>()?;
    let qualified_name = exception_type
        .getattr("__qualname__")?
        .extract::<String>()?;
    if module == "builtins" {
        Ok(qualified_name)
    } else {
        Ok(format!("{module}.{qualified_name}"))
    }
}

enum FastApiTelemetryMessage {
    ResponseStart { status: u16, trailers: bool },
    ResponseBody { more: bool },
    ResponseTrailers { more: bool },
    PathSend,
    Other,
}

impl FastApiTelemetryMessage {
    fn parse(message: &Bound<'_, PyAny>) -> PyResult<Self> {
        let message = message.cast::<PyDict>()?;
        let message_type = message
            .get_item("type")?
            .ok_or_else(|| PyValueError::new_err("ASGI response message has no type"))?
            .extract::<String>()?;
        match message_type.as_str() {
            "http.response.start" => Ok(Self::ResponseStart {
                status: message
                    .get_item("status")?
                    .ok_or_else(|| PyValueError::new_err("ASGI response start has no status"))?
                    .extract::<u16>()?,
                trailers: message
                    .call_method1("get", ("trailers", false))?
                    .extract::<bool>()?,
            }),
            "http.response.body" => Ok(Self::ResponseBody {
                more: message
                    .call_method1("get", ("more_body", false))?
                    .extract::<bool>()?,
            }),
            "http.response.trailers" => Ok(Self::ResponseTrailers {
                more: message
                    .call_method1("get", ("more_trailers", false))?
                    .extract::<bool>()?,
            }),
            "http.response.pathsend" => Ok(Self::PathSend),
            _ => Ok(Self::Other),
        }
    }

    fn observe(&self, state: &mut FastApiTelemetrySpanState) {
        match self {
            Self::ResponseStart { status, trailers } => {
                state.response_status = Some(*status);
                state.expects_trailers = *trailers;
            }
            Self::ResponseBody { more } => {
                let terminal = !more && !state.expects_trailers;
                state.response_terminal |= terminal;
            }
            Self::ResponseTrailers { more } => {
                let terminal = !more;
                state.response_terminal |= terminal;
            }
            Self::PathSend => {
                state.response_terminal = true;
            }
            Self::Other => {}
        }
    }
}

#[pymethods]
impl PyFastApiTelemetrySend {
    fn __call__(&self, py: Python<'_>, message: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            FastApiTelemetrySendCall {
                send: self.send.clone_ref(py),
                span_state: Rc::clone(&self.span_state),
                message,
                message_kind: None,
                pending: false,
            },
        )
    }
}

struct FastApiTelemetrySendCall {
    send: Py<PyAny>,
    span_state: Rc<RefCell<FastApiTelemetrySpanState>>,
    message: Py<PyAny>,
    message_kind: Option<FastApiTelemetryMessage>,
    pending: bool,
}

impl AwaitableStateMachine for FastApiTelemetrySendCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start if !self.pending => {
                self.message_kind = Some(FastApiTelemetryMessage::parse(self.message.bind(py))?);
                let awaitable = self.send.bind(py).call1((self.message.bind(py),))?.unbind();
                self.pending = true;
                Ok(MachineAction::Await(awaitable))
            }
            MachineResume::Value(value) if self.pending => {
                self.pending = false;
                let terminal = {
                    let mut span_state = self.span_state.borrow_mut();
                    self.message_kind
                        .take()
                        .ok_or_else(|| PyRuntimeError::new_err("telemetry send message was lost"))?
                        .observe(&mut span_state);
                    span_state.response_terminal
                };
                if terminal {
                    self.span_state.borrow_mut().finish(py, None, false)?;
                }
                Ok(MachineAction::Complete(value))
            }
            MachineResume::Error(error) if self.pending => {
                self.pending = false;
                Err(error)
            }
            MachineResume::Start | MachineResume::Value(_) | MachineResume::Error(_) => Err(
                PyRuntimeError::new_err("telemetry send resumed without a pending ASGI send"),
            ),
        }
    }
}

struct FastApiTelemetryCall {
    app: Py<PyAny>,
    tracer_provider: Py<PyAny>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
    span_state: Option<Rc<RefCell<FastApiTelemetrySpanState>>>,
    pending: bool,
}

impl FastApiTelemetryCall {
    fn fail(&mut self, py: Python<'_>, error: PyErr) -> PyResult<MachineAction> {
        self.pending = false;
        if let Some(span_state) = self.span_state.take() {
            let _ = span_state.borrow_mut().finish(py, Some(&error), false);
        }
        Err(error)
    }
}

impl AwaitableStateMachine for FastApiTelemetryCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start if !self.pending => {
                let span_state = Rc::new(RefCell::new(FastApiTelemetrySpanState::start(
                    py,
                    self.tracer_provider.bind(py),
                    self.scope.clone_ref(py),
                )?));
                self.span_state = Some(Rc::clone(&span_state));
                let send = match Py::new(
                    py,
                    PyFastApiTelemetrySend {
                        send: self.send.clone_ref(py),
                        span_state,
                    },
                ) {
                    Ok(send) => send.into_any(),
                    Err(error) => return self.fail(py, error),
                };
                let awaitable = match self.app.bind(py).call1((
                    self.scope.bind(py),
                    self.receive.bind(py),
                    send,
                )) {
                    Ok(awaitable) => awaitable.unbind(),
                    Err(error) => return self.fail(py, error),
                };
                self.pending = true;
                Ok(MachineAction::Await(awaitable))
            }
            MachineResume::Value(value) if self.pending => {
                self.pending = false;
                if let Some(span_state) = self.span_state.take() {
                    let incomplete = !span_state.borrow().response_terminal;
                    span_state.borrow_mut().finish(py, None, incomplete)?;
                }
                Ok(MachineAction::Complete(value))
            }
            MachineResume::Error(error) if self.pending => self.fail(py, error),
            MachineResume::Start | MachineResume::Value(_) | MachineResume::Error(_) => Err(
                PyRuntimeError::new_err("telemetry request resumed without a pending app call"),
            ),
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

fn openapi_operations_from_snapshots(
    py: Python<'_>,
    routes: &mut [OpenApiRouteSnapshot],
    separate_input_output_schemas: bool,
) -> PyResult<(Vec<OpenApiOperation>, Py<PyDict>)> {
    let response_field_count = routes
        .iter()
        .flat_map(|route| {
            route.primary_field.iter().chain(
                route
                    .additional_fields
                    .iter()
                    .filter_map(|response| response.field.as_ref()),
            )
        })
        .count();
    let mut request_annotations = Vec::new();
    for route in routes.iter_mut() {
        if let Some(annotation) = openapi_request_schema_annotation(py, route)? {
            route.request_schema_key = Some(response_field_count + request_annotations.len());
            request_annotations.push(annotation);
        }
    }
    let response_fields = routes
        .iter()
        .flat_map(|route| {
            route.primary_field.iter().chain(
                route
                    .additional_fields
                    .iter()
                    .filter_map(|response| response.field.as_ref()),
            )
        })
        .collect::<Vec<_>>();
    // Source collects primary then extras before the shared two-pass JSON
    // generator. Snapshots retain owners across callbacks and errors.
    let response_schemas = ResponseFieldSchemaBatch::new(
        py,
        &response_fields,
        &request_annotations,
        separate_input_output_schemas,
    )?;
    let mut next_field_key = 0;
    let operations = routes
        .iter()
        .map(|route| {
            PyFastApi::openapi_operation(
                py,
                route,
                &response_schemas,
                separate_input_output_schemas,
                &mut next_field_key,
            )
        })
        .collect::<PyResult<Vec<_>>>()?;
    Ok((operations, response_schemas.definitions.clone_ref(py)))
}

fn openapi_document_for_root_path(
    py: Python<'_>,
    schema: Py<PyAny>,
    root_path: &str,
    root_path_in_servers: bool,
) -> PyResult<Py<PyAny>> {
    if root_path.is_empty() || !root_path_in_servers {
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
        let (cached, registrations, exception_handlers, debug) = {
            let app = slf.bind(py).borrow();
            (
                app.middleware_stack
                    .as_ref()
                    .map(|stack| stack.clone_ref(py)),
                app.user_middleware
                    .bind(py)
                    .iter()
                    .map(Bound::unbind)
                    .collect::<Vec<_>>(),
                app.exception_handlers.clone_ref(py),
                app.debug,
            )
        };
        if let Some(cached) = cached {
            return Ok(cached);
        }

        let router = Self::router(slf.clone_ref(py), py)?;
        let mut stack = Py::new(py, PyFastApiAsgiApp { router })?.into_any();
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
        exception_kwargs.set_item("debug", debug)?;
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
        server_error_kwargs.set_item("debug", debug)?;
        stack = server_error_middleware
            .call((stack.bind(py),), Some(&server_error_kwargs))?
            .unbind();

        let mut app = slf.bind(py).borrow_mut();
        if app.middleware_stack.is_none() {
            app.middleware_stack = Some(stack.clone_ref(py));
        }
        Ok(stack)
    }

    fn openapi_document(
        app: &Py<Self>,
        py: Python<'_>,
        root_path: Option<&str>,
    ) -> PyResult<Py<PyAny>> {
        materialize_included_response_fields(py, app, None, None)?;
        let webhook_app = {
            let app = app.bind(py).borrow();
            let webhooks = app.webhooks.bind(py);
            let _routes = webhooks.getattr("routes")?;
            webhooks
                .extract::<PyRef<'_, PyApiRouter>>()?
                .inner_app(py)?
        };
        refresh_included_router_routes(py, &webhook_app)?;
        materialize_included_response_fields(py, &webhook_app, None, None)?;
        let mut snapshot = {
            let app = app.bind(py).borrow();
            OpenApiAppSnapshot::from_app(py, &app)?
        };
        let (operations, response_definitions) = openapi_operations_from_snapshots(
            py,
            &mut snapshot.operations,
            snapshot.separate_input_output_schemas,
        )?;
        openapi_document(
            py,
            OpenApiInfo {
                title: &snapshot.title,
                openapi_version: &snapshot.openapi_version,
                tags: Some(&snapshot.openapi_tags),
                summary: snapshot.summary.as_deref(),
                description: &snapshot.description,
                terms_of_service: snapshot.terms_of_service.as_deref(),
                contact: snapshot.contact.as_ref(),
                license_info: snapshot.license_info.as_ref(),
                openapi_external_docs: snapshot.openapi_external_docs.as_ref(),
                servers: Some(&snapshot.servers),
                version: &snapshot.version,
            },
            &operations,
            root_path,
            Some(&response_definitions),
            true,
        )
    }

    fn openapi_operation(
        py: Python<'_>,
        route: &OpenApiRouteSnapshot,
        response_schemas: &ResponseFieldSchemaBatch,
        separate_input_output_schemas: bool,
        next_field_key: &mut usize,
    ) -> PyResult<OpenApiOperation> {
        let name = route.name.as_str();
        let summary = match route.summary.as_ref().filter(|summary| !summary.is_empty()) {
            Some(summary) => summary.clone(),
            None => PyString::new(py, name)
                .call_method1("replace", ("_", " "))?
                .call_method0("title")?
                .extract::<String>()?,
        };
        let explicit_operation_id = route
            .operation_id
            .as_ref()
            .filter(|operation_id| !operation_id.is_empty())
            .cloned();
        let operation_id = match explicit_operation_id {
            Some(operation_id) => PyString::new(py, &operation_id).into_any().unbind(),
            None => route.unique_id_value.clone_ref(py),
        };
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
                let schema = pydantic_parameter_schema(py, &parameter, &title)?;
                Ok(OpenApiParameter {
                    name: parameter.name,
                    location: parameter.location,
                    required: parameter.required,
                    description: parameter.description,
                    deprecated: parameter.deprecated,
                    example: parameter.example,
                    openapi_examples: parameter.openapi_examples,
                    schema,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        let validation_parameters_present = route.plan.has_openapi_parameter_inputs();
        let mut security_schemes = Vec::new();
        let mut security_requirements = Vec::new();
        route.plan.collect_openapi_security(
            py,
            &mut security_schemes,
            &mut security_requirements,
            &[],
            &mut Vec::new(),
        )?;

        let has_form_body = route.plan.has_form_inputs();
        let (
            request_model_name,
            request_schema,
            request_required,
            request_media_type,
            request_example,
            request_examples,
        ) = if has_form_body {
            let body_parameters = route.plan.all_body_parameters();
            let aggregate_body = form_body_should_embed(py, &body_parameters)?;
            if aggregate_body {
                let request_schema = request_schema_from_batch(py, route, response_schemas, None)?;
                let request_required = body_parameters.iter().any(|parameter| parameter.required);
                let media_type = aggregate_body_media_type(&body_parameters);
                (
                    None,
                    Some(request_schema),
                    request_required,
                    media_type,
                    None,
                    None,
                )
            } else {
                match body_parameters.first().copied() {
                    Some(parameter) => (
                        None,
                        Some(request_schema_from_batch(
                            py,
                            route,
                            response_schemas,
                            Some(&title_case(&parameter.body_alias().replace('_', " "))),
                        )?),
                        parameter.required,
                        parameter
                            .media_type
                            .as_deref()
                            .unwrap_or("application/json")
                            .to_owned(),
                        parameter.example.as_ref().map(|value| value.clone_ref(py)),
                        parameter
                            .openapi_examples
                            .as_ref()
                            .map(|value| value.clone_ref(py)),
                    ),
                    None => (None, None, false, "application/json".to_owned(), None, None),
                }
            }
        } else {
            let direct_body_parameters = route.plan.all_body_parameters();
            let aggregate_body = body_fields_embedded(&direct_body_parameters);
            if aggregate_body {
                let request_schema = request_schema_from_batch(py, route, response_schemas, None)?;
                let request_required = direct_body_parameters
                    .iter()
                    .any(|parameter| parameter.required);
                (
                    None,
                    Some(request_schema),
                    request_required,
                    aggregate_body_media_type(&direct_body_parameters),
                    None,
                    None,
                )
            } else {
                match route.plan.body_parameter() {
                    Some(parameter) => (
                        None,
                        Some(request_schema_from_batch(
                            py,
                            route,
                            response_schemas,
                            Some(&title_case(&parameter.body_alias().replace('_', " "))),
                        )?),
                        parameter.required,
                        parameter
                            .media_type
                            .as_deref()
                            .unwrap_or("application/json")
                            .to_owned(),
                        parameter.example.as_ref().map(|value| value.clone_ref(py)),
                        parameter
                            .openapi_examples
                            .as_ref()
                            .map(|value| value.clone_ref(py)),
                    ),
                    None => (None, None, false, "application/json".to_owned(), None, None),
                }
            }
        };
        let (response_model_name, response_schema) = match route.primary_field.as_ref() {
            Some(field) => {
                let schema = response_schemas.schema(py, *next_field_key, field)?;
                *next_field_key += 1;
                // Preserve generated reference siblings and the retained owner
                // title; assembly must not reconstruct a model-name-only ref.
                (None, Some(schema))
            }
            None => match route.response_model.as_ref() {
                // Stream paths do not yet retain a primary response field.
                // Their existing standalone schema behavior remains separate.
                Some(model) => {
                    let schema = pydantic_response_schema(
                        py,
                        model.bind(py),
                        separate_input_output_schemas,
                        None,
                    )?;
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
            },
        };
        let (response_media_type, response_class_is_json) = if !route.response_class.is_default() {
            let actual_response_class = route.response_class.actual(py)?;
            let response_class = actual_response_class.bind(py);
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
            route.generator_kind.is_generator() && route.response_class.is_default() && !sse_stream;
        let (stream_item_model_name, stream_item_schema) = if jsonl_stream || sse_stream {
            match route.stream_item_type.as_ref() {
                Some(stream_item_type) => {
                    let stream_item_title =
                        title_case(&format!("StreamItem_{}", route.unique_id).replace('_', " "));
                    let schema = pydantic_response_schema(
                        py,
                        stream_item_type.bind(py),
                        separate_input_output_schemas,
                        Some(&stream_item_title),
                    )?;
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
        let (endpoint_name, endpoint_file) = openapi_warning_identity(py, route.endpoint.bind(py))?;
        let OpenApiCallbackData {
            callbacks,
            definitions: callback_definitions,
        } = openapi_callbacks(py, &route.callbacks, separate_input_output_schemas)?;

        Ok(OpenApiOperation {
            path: route.path_format.clone(),
            is_webhook: route.is_webhook,
            method: route.method.to_ascii_lowercase(),
            summary,
            description: (!route.description.is_empty()).then(|| route.description.clone()),
            response_description: route.response_description.clone(),
            openapi_extra: route
                .openapi_extra
                .as_ref()
                .map(|value| value.clone_ref(py)),
            additional_responses: route
                .additional_fields
                .iter()
                .map(|response| {
                    additional_response_openapi(py, response, response_schemas, next_field_key)
                })
                .collect::<PyResult<Vec<_>>>()?,
            operation_id,
            endpoint_name,
            endpoint_file,
            status: route.status_code,
            response_status_key: openapi_response_status_key(
                py,
                route.status_code,
                Some(route.response_class.actual(py)?.bind(py)),
            )?,
            parameters,
            security_schemes,
            callbacks,
            callback_definitions,
            security_requirements,
            validation_parameters_present,
            request_model_name,
            request_schema,
            request_example,
            request_examples,
            request_required,
            request_body_present,
            request_body_content_before_required: has_form_body,
            request_media_type,
            response_model_name,
            response_schema,
            response_schema_title: if route.primary_field.is_some() {
                None
            } else {
                Some(response_field_schema_title(
                    name,
                    &route.path_format,
                    &route.method,
                ))
            },
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

struct OpenApiCallbackData {
    callbacks: Option<Py<PyAny>>,
    definitions: Vec<Py<PyDict>>,
}

fn openapi_callbacks(
    py: Python<'_>,
    callback_routes: &Py<PyAny>,
    separate_input_output_schemas: bool,
) -> PyResult<OpenApiCallbackData> {
    if !callback_routes.bind(py).is_truthy()? {
        return Ok(OpenApiCallbackData {
            callbacks: None,
            definitions: Vec::new(),
        });
    }

    let callbacks = PyDict::new(py);
    let mut definitions = Vec::new();
    for callback in callback_routes.bind(py).try_iter()? {
        let callback = callback?;
        if !is_fastapi_api_route(py, &callback)? {
            continue;
        }
        let callback_route = api_route_state_ref(&callback)?;
        let callback_name = callback_route.name.clone();
        let callback_path = callback_route.path.clone();
        let callback_path_format = callback_route.path_format.clone();
        if !callback_route.include_in_schema {
            let path_item = PyDict::new(py);
            let path_item_map = PyDict::new(py);
            path_item_map.set_item(&callback_path, path_item)?;
            callbacks.set_item(&callback_name, path_item_map)?;
            continue;
        }
        let methods = python_string_set_items(callback_route.methods.bind(py))?;
        let template = callback_route.openapi_snapshots.first();
        if template.is_none() && !methods.is_empty() {
            return Err(PyNotImplementedError::new_err(
                "FastAPI-RS could not resolve the callback APIRoute's OpenAPI state",
            ));
        }

        let mut snapshots = Vec::with_capacity(methods.len());
        for method in &methods {
            let stored = callback_route
                .openapi_snapshots
                .iter()
                .find(|stored| stored.method == *method)
                .or(template)
                .ok_or_else(|| PyRuntimeError::new_err("callback OpenAPI snapshot was lost"))?;
            let mut snapshot = stored.clone_ref(py);
            snapshot.method.clone_from(method);
            apply_openapi_route_view(py, &mut snapshot, &callback_route, false)?;
            snapshots.push(snapshot);
        }
        let (operations, callback_definitions) =
            openapi_operations_from_snapshots(py, &mut snapshots, separate_input_output_schemas)?;
        let callback_version = PyString::new(py, "0.1.0").into_any().unbind();
        let callback_document = openapi_document(
            py,
            OpenApiInfo {
                openapi_version: "3.1.0",
                tags: None,
                title: "FastAPI",
                summary: None,
                description: "",
                terms_of_service: None,
                contact: None,
                license_info: None,
                openapi_external_docs: None,
                servers: None,
                version: &callback_version,
            },
            &operations,
            None,
            Some(&callback_definitions),
            // FastAPI keeps callback-local automatic validation definitions out
            // of the parent document while retaining the callback's 422 ref.
            false,
        )?;
        let callback_document = callback_document.bind(py).cast::<PyDict>()?;
        let paths = callback_document
            .get_item("paths")?
            .ok_or_else(|| PyRuntimeError::new_err("callback OpenAPI document has no paths"))?;
        let path_items = paths.cast::<PyDict>()?;
        let path_item = path_items
            .get_item(&callback_path_format)?
            .or(path_items.get_item(&callback_path)?)
            .ok_or_else(|| {
                PyRuntimeError::new_err("callback OpenAPI document has no matching path item")
            })?;
        let path_item_map = PyDict::new(py);
        path_item_map.set_item(&callback_path, path_item)?;
        callbacks.set_item(&callback_name, path_item_map)?;

        if let Some(components) = callback_document.get_item("components")? {
            let components = components.cast::<PyDict>()?;
            if let Some(schemas) = components.get_item("schemas")? {
                definitions.push(schemas.cast::<PyDict>()?.clone().unbind());
            }
        }
    }

    Ok(OpenApiCallbackData {
        callbacks: Some(callbacks.into_any().unbind()),
        definitions,
    })
}

impl PyApiRouter {
    fn from_fastapi_app(app: &Bound<'_, PyFastApi>) -> PyResult<Self> {
        let py = app.py();
        let inner = ApiRouterInner::FastApiWeak(PyWeakrefReference::new(app.as_any())?.unbind());
        let app_state = app.borrow();
        let route_class = match app_state.router_route_class.as_ref() {
            Some(route_class) => route_class.clone_ref(py),
            None => api_route_type(py)?.unbind(),
        };
        let tag_values = app_state.router_tags.clone_ref(py);
        Ok(Self {
            inner,
            prefix: String::new(),
            default: None,
            dependency_overrides_provider: None,
            route_class,
            tag_values,
            deprecated: app_state.router_deprecated,
            include_in_schema: app_state.router_include_in_schema,
            dependencies: app_state
                .dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py))
                .collect(),
            strict_content_type: app_state.strict_content_type,
        })
    }

    fn inner_app(&self, py: Python<'_>) -> PyResult<Py<PyFastApi>> {
        self.inner.app(py)
    }

    fn route_dependency_overrides_provider(&self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        if let Some(provider) = self.dependency_overrides_provider.as_ref() {
            return Ok(Some(provider.clone_ref(py)));
        }
        match &self.inner {
            ApiRouterInner::Owned(_) => Ok(None),
            ApiRouterInner::FastApiWeak(_) => {
                let app = self.inner_app(py)?;
                fastapi_public_instance(py, &app).map(Some)
            }
        }
    }
}

#[pymethods]
impl PyApiRouter {
    #[new]
    #[pyo3(signature = (*, prefix = "", tags = None, dependencies = None, default_response_class = ResponseClassArgument::Omitted, responses = None, callbacks = None, routes = None, redirect_slashes = true, default = None, dependency_overrides_provider = None, route_class = RouteClassArgument::Omitted, on_startup = None, on_shutdown = None, lifespan = None, deprecated = None, include_in_schema = true, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, strict_content_type = None))]
    // lint-exception: preserve the FastAPI-compatible APIRouter constructor keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible APIRouter constructor keywords"
    )]
    fn new(
        py: Python<'_>,
        prefix: &str,
        tags: Option<Py<PyAny>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        default_response_class: ResponseClassArgument,
        responses: Option<Py<PyAny>>,
        callbacks: Option<Py<PyAny>>,
        routes: Option<Py<PyAny>>,
        redirect_slashes: bool,
        default: Option<Py<PyAny>>,
        dependency_overrides_provider: Option<Py<PyAny>>,
        route_class: RouteClassArgument,
        on_startup: Option<Py<PyAny>>,
        on_shutdown: Option<Py<PyAny>>,
        lifespan: Option<Py<PyAny>>,
        deprecated: Option<bool>,
        include_in_schema: bool,
        generate_unique_id_function: GenerateUniqueIdArgument,
        strict_content_type: Option<bool>,
    ) -> PyResult<Self> {
        validate_router_prefix(prefix)?;
        let route_class = route_class.into_class(py)?;
        let default_route_class = api_route_type(py)?;
        let selected_route_class =
            (!route_class.bind(py).is(&default_route_class)).then(|| route_class.clone_ref(py));
        let tag_values = match tags {
            Some(tags) if tags.bind(py).is_truthy()? => tags,
            _ => PyList::empty(py).into_any().unbind(),
        };
        let router_dependencies = dependencies.unwrap_or_default();
        let router_callbacks = match callbacks {
            Some(callbacks) if callbacks.bind(py).is_truthy()? => callbacks,
            _ => PyList::empty(py).into_any().unbind(),
        };
        let inner = Py::new(
            py,
            PyFastApi::new(
                py,
                None,
                false,
                routes,
                "FastAPI",
                None,
                "",
                PyString::new(py, "0.1.0").into_any().unbind(),
                Some("/openapi.json"),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                generate_unique_id_function,
                true,
                None,
                None,
                None,
                "",
                "",
                true,
                responses.map(|responses| responses.clone_ref(py)),
                Some(router_callbacks.clone_ref(py)),
                None,
                Some(py.None()),
                None,
                default_response_class,
                redirect_slashes,
                None,
                None,
                on_startup,
                on_shutdown,
                lifespan,
                strict_content_type.unwrap_or(true),
                deprecated,
                include_in_schema,
                None,
            )?,
        )?;
        {
            let mut inner = inner.bind(py).borrow_mut();
            let route_surface = PyList::empty(py);
            for route in &inner.constructor_routes {
                route_surface.append(route.bind(py))?;
            }
            inner.route_surface = route_surface.unbind();
            inner.route_scope_prefix = prefix.to_owned();
            inner.is_router_inner = true;
            inner.router_tags = tag_values.clone_ref(py);
            inner.router_dependencies = router_dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py))
                .collect();
            inner.router_callbacks = router_callbacks.clone_ref(py);
            inner.router_route_class = selected_route_class;
            inner.router_deprecated = deprecated;
            inner.router_include_in_schema = include_in_schema;
            inner.strict_content_type = strict_content_type;
        }
        Ok(Self {
            inner: ApiRouterInner::Owned(inner),
            prefix: prefix.to_owned(),
            default,
            dependency_overrides_provider,
            route_class,
            tag_values,
            deprecated,
            include_in_schema,
            dependencies: router_dependencies,
            strict_content_type,
        })
    }

    fn __call__(
        &self,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let default = self.default.as_ref().map(|default| default.clone_ref(py));
        let dependency_overrides_provider = self.route_dependency_overrides_provider(py)?;
        fastapi_core_call(
            py,
            self.inner_app(py)?,
            scope,
            receive,
            send,
            default,
            dependency_overrides_provider,
        )
    }

    #[getter]
    fn prefix(&self) -> &str {
        &self.prefix
    }

    #[getter]
    fn tags(&self, py: Python<'_>) -> Py<PyAny> {
        self.tag_values.clone_ref(py)
    }

    #[setter]
    fn set_tags(&mut self, py: Python<'_>, tags: Py<PyAny>) -> PyResult<()> {
        self.inner_app(py)?.bind(py).borrow_mut().router_tags = tags.clone_ref(py);
        self.tag_values = tags;
        Ok(())
    }

    #[getter]
    fn default(&self, py: Python<'_>) -> Py<PyAny> {
        self.default
            .as_ref()
            .map(|default| default.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[setter]
    fn set_default(&mut self, default: Option<Py<PyAny>>) {
        self.default = default;
    }

    #[getter]
    fn dependency_overrides_provider(&self, py: Python<'_>) -> Py<PyAny> {
        self.dependency_overrides_provider
            .as_ref()
            .map(|provider| provider.clone_ref(py))
            .unwrap_or_else(|| py.None())
    }

    #[setter]
    fn set_dependency_overrides_provider(&mut self, provider: Option<Py<PyAny>>) {
        self.dependency_overrides_provider = provider;
    }

    #[getter]
    fn route_class(&self, py: Python<'_>) -> Py<PyAny> {
        self.route_class.clone_ref(py)
    }

    #[setter]
    fn set_route_class(&mut self, py: Python<'_>, route_class: Py<PyAny>) -> PyResult<()> {
        let default_route_class = api_route_type(py)?;
        let selected_route_class =
            (!route_class.bind(py).is(&default_route_class)).then(|| route_class.clone_ref(py));
        self.inner_app(py)?.bind(py).borrow_mut().router_route_class = selected_route_class;
        self.route_class = route_class;
        Ok(())
    }

    #[getter]
    fn callbacks(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self
            .inner_app(py)?
            .bind(py)
            .borrow()
            .router_callbacks
            .clone_ref(py))
    }

    #[setter]
    fn set_callbacks(&mut self, py: Python<'_>, callbacks: Py<PyAny>) -> PyResult<()> {
        self.inner_app(py)?.bind(py).borrow_mut().router_callbacks = callbacks;
        Ok(())
    }

    #[getter]
    fn default_response_class(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self
            .inner_app(py)?
            .bind(py)
            .borrow()
            .default_response_class
            .python_value(py))
    }

    #[setter]
    fn set_default_response_class(&mut self, py: Python<'_>, value: Py<PyAny>) -> PyResult<()> {
        self.inner_app(py)?
            .bind(py)
            .borrow_mut()
            .default_response_class = ResponseClassChoice::from_python(py, value);
        Ok(())
    }

    #[getter]
    fn routes(&self, py: Python<'_>) -> PyResult<Py<PyList>> {
        let inner = self.inner_app(py)?;
        refresh_included_router_routes(py, &inner)?;
        let inner = inner.bind(py).borrow();
        Ok(inner.route_surface.clone_ref(py))
    }

    #[getter]
    fn redirect_slashes(&self, py: Python<'_>) -> PyResult<bool> {
        Ok(self.inner_app(py)?.bind(py).borrow().redirect_slashes)
    }

    #[setter]
    fn set_redirect_slashes(&mut self, py: Python<'_>, redirect_slashes: bool) -> PyResult<()> {
        self.inner_app(py)?.bind(py).borrow_mut().redirect_slashes = redirect_slashes;
        Ok(())
    }

    #[getter]
    fn dependencies(&self, py: Python<'_>) -> PyResult<Py<PyList>> {
        PyList::new(
            py,
            self.dependencies
                .iter()
                .map(|dependency| dependency.bind(py)),
        )
        .map(Bound::unbind)
    }

    #[getter]
    fn deprecated(&self) -> Option<bool> {
        self.deprecated
    }

    #[getter]
    fn include_in_schema(&self) -> bool {
        self.include_in_schema
    }

    #[getter]
    fn strict_content_type(&self) -> bool {
        self.strict_content_type.unwrap_or(true)
    }

    #[setter]
    fn set_strict_content_type(
        &mut self,
        py: Python<'_>,
        strict_content_type: bool,
    ) -> PyResult<()> {
        self.strict_content_type = Some(strict_content_type);
        self.inner_app(py)?
            .bind(py)
            .borrow_mut()
            .strict_content_type = Some(strict_content_type);
        Ok(())
    }

    #[pyo3(
        signature = (path, endpoint, *, dependencies = None, description = None, methods = None, include_in_schema = true, name = None, route_class_override = None, callbacks = None, openapi_extra = None, generate_unique_id_function = GenerateUniqueIdArgument::Omitted, deprecated = None, tags = None, strict_content_type = StrictContentTypeArgument::Omitted),
        text_signature = "($self, path, endpoint, *, dependencies=None, description=None, methods=None, include_in_schema=True, name=None, route_class_override=None, callbacks=None, openapi_extra=None, generate_unique_id_function=None, deprecated=None, tags=None, strict_content_type=None)"
    )]
    // lint-exception: preserve the selected FastAPI.add_api_route keyword interface.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible add_api_route keyword signature"
    )]
    fn add_api_route(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        endpoint: Py<PyAny>,
        dependencies: Option<Vec<Py<PyAny>>>,
        description: Option<String>,
        methods: Option<Py<PyAny>>,
        include_in_schema: bool,
        name: Option<String>,
        route_class_override: Option<Py<PyAny>>,
        callbacks: Option<Py<PyAny>>,
        openapi_extra: Option<Py<PyAny>>,
        generate_unique_id_function: GenerateUniqueIdArgument,
        deprecated: Option<bool>,
        tags: Option<Vec<String>>,
        strict_content_type: StrictContentTypeArgument,
    ) -> PyResult<()> {
        let normalized_methods = PySet::empty(py)?;
        if let Some(methods) = methods {
            for method in methods.bind(py).try_iter()? {
                normalized_methods.add(method?.call_method0("upper")?)?;
            }
        } else {
            normalized_methods.add("GET")?;
        }
        let callback_methods = normalized_methods
            .iter()
            .map(|method| method.extract::<String>())
            .collect::<PyResult<Vec<_>>>()?;
        let (inner, dependency_overrides_provider, configured_route_class) = {
            let router = slf.bind(py).borrow();
            (
                router.inner_app(py)?,
                router.route_dependency_overrides_provider(py)?,
                router.route_class.clone_ref(py),
            )
        };
        let route_class_selection = match route_class_override {
            Some(route_class_override) if route_class_override.bind(py).is_truthy()? => {
                route_class_override
            }
            _ => configured_route_class,
        };
        let decorator = operation_decorator(
            inner.clone_ref(py),
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
                strict_content_type,
                response_description: None,
                description,
                responses: None,
                callbacks,
                summary: None,
                operation_id: None,
                generate_unique_id_function: generate_unique_id_function.into_choice(py)?,
                deprecated: None,
                tags: None,
                dependencies: dependencies.unwrap_or_default(),
                response_class: ResponseClassChoice::from_python(py, default_response_class(py)?),
                openapi_extra,
                name,
            },
        )?;
        decorator.bind(py).borrow_mut().route_class_selection = Some(route_class_selection);
        decorator
            .bind(py)
            .borrow_mut()
            .dependency_overrides_provider = dependency_overrides_provider;
        register_multi_method_api_route(
            py,
            decorator,
            endpoint,
            callback_methods,
            tags,
            deprecated,
            true,
        )
    }

    fn add_event_handler(
        &self,
        py: Python<'_>,
        event_type: &str,
        handler: Py<PyAny>,
    ) -> PyResult<()> {
        self.inner_app(py)?
            .bind(py)
            .borrow()
            .lifespan
            .add_event_handler(py, event_type, handler)
    }

    fn on_event(&self, py: Python<'_>, event_type: &str) -> PyResult<Py<PyAny>> {
        warn_on_event(py, false)?;
        self.inner_app(py)?
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
        let dependencies = self
            .dependencies
            .iter()
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        let path = normalize_frontend_path(path)?;
        let path = join_frontend_paths(&self.prefix, &path);
        let inner_app = self.inner_app(py)?;
        let mut inner = inner_app.bind(py).borrow_mut();
        add_frontend_route(
            &mut inner,
            py,
            &path,
            directory,
            fallback,
            check_dir,
            &dependencies,
        )
    }

    #[pyo3(signature = (router, *, prefix = "", tags = None, dependencies = None, default_response_class = ResponseClassArgument::Omitted, responses = None, callbacks = None, deprecated = None, include_in_schema = true, generate_unique_id_function = GenerateUniqueIdArgument::Omitted))]
    // lint-exception: preserve FastAPI's include_router keyword signature.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the FastAPI-compatible include_router signature"
    )]
    fn include_router(
        slf: Py<Self>,
        py: Python<'_>,
        router: Py<PyApiRouter>,
        prefix: &str,
        tags: Option<Vec<String>>,
        dependencies: Option<Vec<Py<PyAny>>>,
        default_response_class: ResponseClassArgument,
        responses: Option<Py<PyAny>>,
        callbacks: Option<Py<PyAny>>,
        deprecated: Option<bool>,
        include_in_schema: bool,
        generate_unique_id_function: GenerateUniqueIdArgument,
    ) -> PyResult<()> {
        let include_responses = response_map_or_empty(py, responses)?;
        let source_inner = { router.bind(py).borrow().inner_app(py)? };
        refresh_included_router_routes(py, &source_inner)?;
        let (
            inner,
            parent_prefix,
            parent_tags,
            parent_dependencies,
            parent_callbacks,
            parent_deprecated,
            parent_include_in_schema,
        ) = {
            let parent = slf.bind(py).borrow();
            let inner = parent.inner_app(py)?;
            let parent_callbacks = {
                let inner = inner.bind(py).borrow();
                callback_values(inner.router_callbacks.bind(py))?
            };
            (
                inner,
                parent.prefix.clone(),
                fastapi_router_tags(parent.tag_values.bind(py))?,
                parent
                    .dependencies
                    .iter()
                    .map(|dependency| dependency.clone_ref(py))
                    .collect::<Vec<_>>(),
                parent_callbacks,
                parent.deprecated,
                parent.include_in_schema,
            )
        };
        let include_callbacks =
            inherited_callback_values(py, &parent_callbacks, callbacks.as_ref())?;
        let include_response_class = default_response_class.into_choice(py)?;
        let include_generate_unique_id_function = generate_unique_id_function.into_choice(py)?;
        let parent_responses = {
            let destination = inner.bind(py).borrow();
            route_response_declarations(py, Some(&destination.responses))?
        };
        let include_responses = route_response_declarations(py, Some(&include_responses))?;
        let inherited_responses =
            merge_response_maps(py, parent_responses.bind(py), include_responses.bind(py))?;
        let inherited_response_class = {
            let destination = inner.bind(py).borrow();
            ResponseClassChoice::first_explicit(
                py,
                &[&include_response_class, &destination.default_response_class],
            )
        };
        let inherited_generate_unique_id_function = {
            let destination = inner.bind(py).borrow();
            GenerateUniqueIdChoice::first_explicit(
                py,
                &[
                    &include_generate_unique_id_function,
                    &destination.generate_unique_id_function,
                ],
            )
        };
        let router_object = router.clone_ref(py).into_any();
        let include_prefix = prefix.to_owned();
        let frontend_merge_prefix = format!("{parent_prefix}{include_prefix}");
        let router = router.bind(py).borrow();
        let router_inner = router.inner_app(py)?;
        if inner.as_ptr() == router_inner.as_ptr() {
            return Err(PyAssertionError::new_err(
                "Cannot include the same APIRouter instance into itself. Did you mean to include a different router?",
            ));
        }
        {
            let source = router_inner.bind(py).borrow();
            validate_empty_path_router_include(&source.routes, prefix)?;
        }
        let prefix = combined_router_prefix(prefix, &router.prefix)?;
        let mut inherited_tags = parent_tags;
        inherited_tags.extend(tags.unwrap_or_default());
        let mut inherited_dependencies = parent_dependencies;
        inherited_dependencies.extend(dependencies.unwrap_or_default());
        let deprecated = combined_deprecated(deprecated, parent_deprecated);
        let include_in_schema = include_in_schema && parent_include_in_schema;
        let dependency_overrides_provider = slf
            .bind(py)
            .borrow()
            .route_dependency_overrides_provider(py)?;
        let source = router_inner.bind(py).borrow();
        let mut destination = inner.bind(py).borrow_mut();
        if source.lifespan.is_included_by(py, &destination.lifespan)? {
            return Err(PyAssertionError::new_err(
                "Cannot include an APIRouter instance that already includes this router. Did you mean to include a different router?",
            ));
        }
        let inherited_strict_content_type = destination.strict_content_type;
        let route_position = destination.routes.len();
        let websocket_route_position = destination.websocket_routes.len();
        let frontend_route_position = destination.frontend_routes.len();
        let source_route_indexes =
            (route_position..route_position + source.routes.len()).collect::<Vec<_>>();
        let source_websocket_route_indexes = (websocket_route_position
            ..websocket_route_position + source.websocket_routes.len())
            .collect::<Vec<_>>();
        let source_frontend_route_indexes = (frontend_route_position
            ..frontend_route_position + source.frontend_routes.len())
            .collect::<Vec<_>>();
        merge_router_routes(
            py,
            &mut destination,
            &router_inner,
            &source,
            dependency_overrides_provider.as_ref(),
            RouterIncludePolicy {
                prefix: &prefix,
                frontend_prefix: &frontend_merge_prefix,
                responses: &inherited_responses,
                response_class: &inherited_response_class,
                generate_unique_id_function: &inherited_generate_unique_id_function,
                tags: &inherited_tags,
                dependencies: &inherited_dependencies,
                callbacks: &include_callbacks,
                deprecated,
                include_in_schema,
                strict_content_type: inherited_strict_content_type,
            },
        )?;
        let effective_route_contexts = PyList::empty(py);
        for route_index in &source_route_indexes {
            let route = destination
                .routes
                .get(*route_index)
                .ok_or_else(|| PyRuntimeError::new_err("included public route context was lost"))?;
            effective_route_contexts.append(route.public_route.bind(py))?;
        }
        let public_route = Py::new(
            py,
            PyFastApiIncludedRouter {
                original_router: router_object.clone_ref(py),
                effective_route_contexts: effective_route_contexts.clone().unbind(),
            },
        )?
        .into_any();
        destination
            .route_surface
            .bind(py)
            .append(public_route.bind(py))?;
        destination.router_includes.push(FastApiRouterInclude {
            route_position,
            websocket_route_position,
            frontend_route_position,
            router: router_object,
            merge_prefix: prefix,
            frontend_merge_prefix,
            responses: inherited_responses.clone_ref(py),
            response_class: inherited_response_class.clone_ref(py),
            generate_unique_id_function: inherited_generate_unique_id_function.clone_ref(py),
            tags: inherited_tags.clone(),
            dependencies: inherited_dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py))
                .collect(),
            callbacks: include_callbacks
                .iter()
                .map(|callback| callback.clone_ref(py))
                .collect(),
            deprecated,
            include_in_schema,
            strict_content_type: inherited_strict_content_type,
            public_route,
            source_route_cursor: source.routes.len(),
            source_route_indexes: source_route_indexes.clone(),
            source_websocket_route_cursor: source.websocket_routes.len(),
            source_websocket_route_indexes,
            source_frontend_route_cursor: source.frontend_routes.len(),
            source_frontend_route_indexes,
            fields: IncludedFieldBranch::from_router_indexes(&source, &source_route_indexes),
        });
        let include_index = destination.router_includes.len() - 1;
        destination
            .route_dispatch_order
            .push(RouteDispatchEntry::RouterInclude(include_index));
        destination.lifespan.include_router(py, &source.lifespan)?;
        drop(source);
        drop(router);
        drop(destination);
        synchronize_included_route_orders(py, &inner)?;
        Ok(())
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
        let inner = self.inner_app(py)?;
        let url_path = inner
            .bind(py)
            .call_method("url_path_for", (name,), path_params)?;
        prefix_url_path(py, url_path, &self.prefix)
    }

    fn __getattr__(&self, py: Python<'_>, name: &str) -> PyResult<Py<PyAny>> {
        if name == "generate_unique_id_function" {
            let inner = self.inner_app(py)?;
            return Ok(inner
                .bind(py)
                .borrow()
                .generate_unique_id_function
                .python_value(py));
        }
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
        Ok(self.inner_app(py)?.bind(py).getattr(name)?.unbind())
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

fn validate_empty_path_router_include(routes: &[FastApiRoute], prefix: &str) -> PyResult<()> {
    if prefix.is_empty() {
        if let Some(route) = routes.iter().find(|route| route.path.is_empty()) {
            return Err(fastapi_error(&format!(
                "Prefix and path cannot be both empty (path operation: {})",
                route.name
            )));
        }
    }
    Ok(())
}

fn combined_router_prefix(include_prefix: &str, router_prefix: &str) -> PyResult<String> {
    validate_router_prefix(include_prefix)?;
    validate_router_prefix(router_prefix)?;
    Ok(format!("{include_prefix}{router_prefix}"))
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

fn format_route_url_path(
    py: Python<'_>,
    path_format: &str,
    param_convertors: &Py<PyDict>,
    path_params: &Bound<'_, PyDict>,
) -> PyResult<String> {
    let mut formatted_path_params = Vec::with_capacity(path_params.len());
    for (parameter_name, value) in path_params.iter() {
        let parameter_name = parameter_name.extract::<String>()?;
        let convertor = param_convertors
            .bind(py)
            .get_item(&parameter_name)?
            .ok_or_else(|| {
                PyRuntimeError::new_err("matched route is missing a path parameter convertor")
            })?;
        let formatted_value = convertor
            .call_method1("to_string", (value,))?
            .extract::<String>()?;
        formatted_path_params.push((parameter_name, formatted_value));
    }
    Ok(formatted_path_params
        .iter()
        .fold(path_format.to_owned(), |path, (name, value)| {
            path.replace(&format!("{{{name}}}"), value)
        }))
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

fn fastapi_router_tags(tags: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    Ok(tags
        .extract::<Vec<FastApiTag>>()?
        .into_iter()
        .map(|tag| tag.0)
        .collect())
}

fn callback_values(callbacks: &Bound<'_, PyAny>) -> PyResult<Vec<Py<PyAny>>> {
    callbacks
        .try_iter()?
        .map(|callback| callback.map(Bound::unbind))
        .collect()
}

fn inherited_callback_values(
    py: Python<'_>,
    inherited: &[Py<PyAny>],
    callbacks: Option<&Py<PyAny>>,
) -> PyResult<Vec<Py<PyAny>>> {
    let mut values = inherited
        .iter()
        .map(|callback| callback.clone_ref(py))
        .collect::<Vec<_>>();
    if let Some(callbacks) = callbacks {
        let callbacks = callbacks.bind(py);
        if callbacks.is_truthy()? {
            values.extend(callback_values(callbacks)?);
        }
    }
    Ok(values)
}

fn router_route_callbacks(
    py: Python<'_>,
    router_callbacks: &Py<PyAny>,
    route_callbacks: Option<&Py<PyAny>>,
) -> PyResult<Py<PyAny>> {
    let callbacks = router_callbacks.bind(py).call_method0("copy")?;
    if let Some(route_callbacks) = route_callbacks {
        let route_callbacks = route_callbacks.bind(py);
        if route_callbacks.is_truthy()? {
            callbacks.call_method1("extend", (route_callbacks,))?;
        }
    }
    Ok(callbacks.unbind())
}

fn effective_route_callbacks(
    py: Python<'_>,
    inherited: &[Py<PyAny>],
    route_callbacks: &Py<PyAny>,
) -> PyResult<Py<PyAny>> {
    let mut values = inherited
        .iter()
        .map(|callback| callback.clone_ref(py))
        .collect::<Vec<_>>();
    if route_callbacks.bind(py).is_truthy()? {
        values.extend(callback_values(route_callbacks.bind(py))?);
    }
    PyList::new(py, values.iter().map(|callback| callback.bind(py)))
        .map(|callbacks| callbacks.into_any().unbind())
}

fn combined_deprecated(route: Option<bool>, inherited: Option<bool>) -> Option<bool> {
    if route.unwrap_or(false) {
        route
    } else {
        inherited
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

#[cfg(feature = "fault-injection")]
fn frontend_lookup_fault_error(py: Python<'_>) -> PyResult<Option<PyErr>> {
    use crate::fault_injection::FrontendLookupFault;

    let Some(fault) = crate::fault_injection::take_http_frontend_lookup_fault() else {
        return Ok(None);
    };
    let builtins = py.import("builtins")?;
    let error = match fault {
        FrontendLookupFault::PermissionError => builtins.getattr("PermissionError")?.call0()?,
        FrontendLookupFault::ValueError => builtins.getattr("ValueError")?.call0()?,
        FrontendLookupFault::NameTooLong => {
            let error_number = py.import("errno")?.getattr("ENAMETOOLONG")?;
            builtins
                .getattr("OSError")?
                .call1((error_number, "name too long"))?
        }
        FrontendLookupFault::OsError => {
            let error_number = py.import("errno")?.getattr("EIO")?;
            builtins
                .getattr("OSError")?
                .call1((error_number, "other"))?
        }
    };
    Ok(Some(PyErr::from_value(error)))
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
    source_router: &Py<PyFastApi>,
    source: &PyFastApi,
    dependency_overrides_provider: Option<&Py<PyAny>>,
    policy: RouterIncludePolicy<'_>,
) -> PyResult<()> {
    merge_router_routes_from(
        py,
        app,
        source_router,
        source,
        dependency_overrides_provider,
        policy,
        RouterMergeStarts {
            routes: 0,
            websocket_routes: 0,
            frontend_routes: 0,
        },
    )
}

fn prefix_starlette_route(
    py: Python<'_>,
    route: &Bound<'_, PyAny>,
    prefix: &str,
) -> PyResult<Option<Py<PyAny>>> {
    let routing = py.import("starlette.routing")?;
    let route_type = routing.getattr("Route")?;
    let is_route = py
        .import("builtins")?
        .getattr("isinstance")?
        .call1((route, &route_type))?
        .is_truthy()?;
    if is_route {
        let path = format!("{prefix}{}", route.getattr("path")?.extract::<String>()?);
        let kwargs = PyDict::new(py);
        kwargs.set_item("methods", route.getattr("methods")?)?;
        kwargs.set_item("name", route.getattr("name")?)?;
        kwargs.set_item("include_in_schema", route.getattr("include_in_schema")?)?;
        return route_type
            .call((path, route.getattr("endpoint")?), Some(&kwargs))
            .map(|route| Some(route.unbind()));
    }

    let is_instance = py.import("builtins")?.getattr("isinstance")?;
    let websocket_route_type = routing.getattr("WebSocketRoute")?;
    if is_instance
        .call1((route, &websocket_route_type))?
        .is_truthy()?
    {
        let path = format!("{prefix}{}", route.getattr("path")?.extract::<String>()?);
        let kwargs = PyDict::new(py);
        kwargs.set_item("name", route.getattr("name")?)?;
        let rebuilt =
            websocket_route_type.call((path, route.getattr("endpoint")?), Some(&kwargs))?;
        let copied = py.import("copy")?.call_method1("copy", (route,))?;
        for attribute in ["path", "path_regex", "path_format", "param_convertors"] {
            copied.setattr(attribute, rebuilt.getattr(attribute)?)?;
        }
        return Ok(Some(copied.unbind()));
    }

    let mount_type = routing.getattr("Mount")?;
    if is_instance.call1((route, &mount_type))?.is_truthy()? {
        let path = format!("{prefix}{}", route.getattr("path")?.extract::<String>()?);
        let kwargs = PyDict::new(py);
        kwargs.set_item("name", route.getattr("name")?)?;
        let rebuilt = mount_type.call((path, route.getattr("app")?), Some(&kwargs))?;
        let copied = py.import("copy")?.call_method1("copy", (route,))?;
        for attribute in [
            "path",
            "path_regex",
            "path_format",
            "param_convertors",
            "_route_table",
            "_uses_compatibility_matcher",
        ] {
            if rebuilt.hasattr(attribute)? {
                copied.setattr(attribute, rebuilt.getattr(attribute)?)?;
            }
        }
        return Ok(Some(copied.unbind()));
    }

    let host_type = routing.getattr("Host")?;
    if is_instance.call1((route, &host_type))?.is_truthy()? {
        let app = route.getattr("app")?;
        let app = if prefix.is_empty() {
            app
        } else {
            let mount_kwargs = PyDict::new(py);
            let mount = mount_type.call((prefix, &app), Some(&mount_kwargs))?;
            let routes = PyList::empty(py);
            routes.append(mount)?;
            let router_kwargs = PyDict::new(py);
            router_kwargs.set_item("routes", routes)?;
            routing.getattr("Router")?.call((), Some(&router_kwargs))?
        };
        let kwargs = PyDict::new(py);
        kwargs.set_item("name", route.getattr("name")?)?;
        return host_type
            .call((route.getattr("host")?, app), Some(&kwargs))
            .map(|route| Some(route.unbind()));
    }

    Ok(None)
}

fn collect_http_dispatch_candidates(
    py: Python<'_>,
    app: &Py<PyFastApi>,
    include_constructor_routes: bool,
    prefix: &str,
    visiting: &mut HashSet<usize>,
) -> PyResult<Vec<HttpDispatchCandidate>> {
    let app_identity = app.as_ptr() as usize;
    if !visiting.insert(app_identity) {
        return Err(PyRuntimeError::new_err(
            "recursive APIRouter inclusion encountered during HTTP dispatch",
        ));
    }

    let (constructor_routes, mounted_routes, dispatch_order, includes) = {
        let app = app.bind(py).borrow();
        let includes = app
            .router_includes
            .iter()
            .map(|include| {
                (
                    include.router.clone_ref(py),
                    include.merge_prefix.clone(),
                    include.source_route_indexes.clone(),
                )
            })
            .collect::<Vec<_>>();
        (
            app.constructor_routes
                .iter()
                .map(|route| route.clone_ref(py))
                .collect::<Vec<_>>(),
            app.mounted_routes
                .iter()
                .map(|route| route.clone_ref(py))
                .collect::<Vec<_>>(),
            app.route_dispatch_order.clone(),
            includes,
        )
    };

    let mut candidates = Vec::new();
    if include_constructor_routes {
        for route in constructor_routes {
            if let Some(route) = prefix_starlette_route(py, route.bind(py), prefix)? {
                candidates.push(HttpDispatchCandidate::StarletteRoute(route));
            }
        }
    }

    for entry in dispatch_order {
        match entry {
            RouteDispatchEntry::ApiRoute(route_index) => {
                if route_index >= app.bind(py).borrow().routes.len() {
                    return Err(PyRuntimeError::new_err(
                        "HTTP dispatch references a missing FastAPI route",
                    ));
                }
                candidates.push(HttpDispatchCandidate::ApiRoute(route_index));
            }
            RouteDispatchEntry::ApiWebSocketRoute(_) => {}
            RouteDispatchEntry::MountedRoute(route_index) => {
                let route = mounted_routes.get(route_index).ok_or_else(|| {
                    PyRuntimeError::new_err("HTTP dispatch references a missing Starlette route")
                })?;
                if prefix.is_empty() {
                    candidates.push(HttpDispatchCandidate::StarletteRoute(route.clone_ref(py)));
                } else if let Some(route) = prefix_starlette_route(py, route.bind(py), prefix)? {
                    candidates.push(HttpDispatchCandidate::StarletteRoute(route));
                }
            }
            RouteDispatchEntry::RouterInclude(include_index) => {
                let (router, include_prefix, source_route_indexes) =
                    includes.get(include_index).ok_or_else(|| {
                        PyRuntimeError::new_err("HTTP dispatch references a missing router include")
                    })?;
                let source_app = router
                    .bind(py)
                    .extract::<PyRef<'_, PyApiRouter>>()?
                    .inner_app(py)?;
                let nested_prefix = format!("{prefix}{include_prefix}");
                let nested = collect_http_dispatch_candidates(
                    py,
                    &source_app,
                    true,
                    &nested_prefix,
                    visiting,
                )?;
                for candidate in nested {
                    match candidate {
                        HttpDispatchCandidate::ApiRoute(source_index) => {
                            let destination_index = source_route_indexes
                                .get(source_index)
                                .copied()
                                .ok_or_else(|| {
                                    PyRuntimeError::new_err("included HTTP route mapping was lost")
                                })?;
                            candidates.push(HttpDispatchCandidate::ApiRoute(destination_index));
                        }
                        HttpDispatchCandidate::StarletteRoute(route) => {
                            candidates.push(HttpDispatchCandidate::StarletteRoute(route));
                        }
                    }
                }
            }
        }
    }

    visiting.remove(&app_identity);
    Ok(candidates)
}

fn collect_websocket_dispatch_candidates(
    py: Python<'_>,
    app: &Py<PyFastApi>,
    include_constructor_routes: bool,
    prefix: &str,
    visiting: &mut HashSet<usize>,
) -> PyResult<Vec<WebSocketDispatchCandidate>> {
    let app_identity = app.as_ptr() as usize;
    if !visiting.insert(app_identity) {
        return Err(PyRuntimeError::new_err(
            "recursive APIRouter inclusion encountered during WebSocket dispatch",
        ));
    }

    let (constructor_routes, mounted_routes, dispatch_order, includes) = {
        let app = app.bind(py).borrow();
        let includes = app
            .router_includes
            .iter()
            .map(|include| {
                (
                    include.router.clone_ref(py),
                    include.merge_prefix.clone(),
                    include.source_websocket_route_indexes.clone(),
                )
            })
            .collect::<Vec<_>>();
        (
            app.constructor_routes
                .iter()
                .map(|route| route.clone_ref(py))
                .collect::<Vec<_>>(),
            app.mounted_routes
                .iter()
                .map(|route| route.clone_ref(py))
                .collect::<Vec<_>>(),
            app.route_dispatch_order.clone(),
            includes,
        )
    };

    let mut candidates = Vec::new();
    if include_constructor_routes {
        for route in constructor_routes {
            if let Some(route) = prefix_starlette_route(py, route.bind(py), prefix)? {
                candidates.push(WebSocketDispatchCandidate::StarletteRoute(route));
            }
        }
    }

    for entry in dispatch_order {
        match entry {
            RouteDispatchEntry::ApiRoute(_) => {}
            RouteDispatchEntry::ApiWebSocketRoute(route_index) => {
                if route_index >= app.bind(py).borrow().websocket_routes.len() {
                    return Err(PyRuntimeError::new_err(
                        "WebSocket dispatch references a missing FastAPI route",
                    ));
                }
                candidates.push(WebSocketDispatchCandidate::ApiWebSocketRoute(route_index));
            }
            RouteDispatchEntry::MountedRoute(route_index) => {
                let route = mounted_routes.get(route_index).ok_or_else(|| {
                    PyRuntimeError::new_err(
                        "WebSocket dispatch references a missing Starlette route",
                    )
                })?;
                if prefix.is_empty() {
                    candidates.push(WebSocketDispatchCandidate::StarletteRoute(
                        route.clone_ref(py),
                    ));
                } else if let Some(route) = prefix_starlette_route(py, route.bind(py), prefix)? {
                    candidates.push(WebSocketDispatchCandidate::StarletteRoute(route));
                }
            }
            RouteDispatchEntry::RouterInclude(include_index) => {
                let (router, include_prefix, source_websocket_route_indexes) =
                    includes.get(include_index).ok_or_else(|| {
                        PyRuntimeError::new_err(
                            "WebSocket dispatch references a missing router include",
                        )
                    })?;
                let source_app = router
                    .bind(py)
                    .extract::<PyRef<'_, PyApiRouter>>()?
                    .inner_app(py)?;
                let nested_prefix = format!("{prefix}{include_prefix}");
                let nested = collect_websocket_dispatch_candidates(
                    py,
                    &source_app,
                    true,
                    &nested_prefix,
                    visiting,
                )?;
                for candidate in nested {
                    match candidate {
                        WebSocketDispatchCandidate::ApiWebSocketRoute(source_index) => {
                            let destination_index = source_websocket_route_indexes
                                .get(source_index)
                                .copied()
                                .ok_or_else(|| {
                                    PyRuntimeError::new_err(
                                        "included WebSocket route mapping was lost",
                                    )
                                })?;
                            candidates.push(WebSocketDispatchCandidate::ApiWebSocketRoute(
                                destination_index,
                            ));
                        }
                        WebSocketDispatchCandidate::StarletteRoute(route) => {
                            candidates.push(WebSocketDispatchCandidate::StarletteRoute(route));
                        }
                    }
                }
            }
        }
    }

    visiting.remove(&app_identity);
    Ok(candidates)
}

fn single_api_route_matcher(
    path: &str,
    methods: &[String],
    status_code: Option<u16>,
) -> PyResult<FastApiOperationRouter> {
    let mut matcher = FastApiOperationRouter::new();
    matcher
        .add_operation_with_methods(path, methods.iter().map(String::as_str), status_code)
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    Ok(matcher)
}

fn http_method_not_allowed_response(
    py: Python<'_>,
    allowed_methods: &[String],
) -> PyResult<Py<PyAny>> {
    let headers = PyDict::new(py);
    headers.set_item("Allow", allowed_methods.join(", "))?;
    let content = PyDict::new(py);
    content.set_item("detail", "Method Not Allowed")?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("status_code", 405)?;
    kwargs.set_item("headers", headers)?;
    py.import("starlette.responses")?
        .getattr("JSONResponse")?
        .call((content,), Some(&kwargs))
        .map(Bound::unbind)
}

fn merge_router_routes_from(
    py: Python<'_>,
    app: &mut PyFastApi,
    source_router: &Py<PyFastApi>,
    source: &PyFastApi,
    dependency_overrides_provider: Option<&Py<PyAny>>,
    policy: RouterIncludePolicy<'_>,
    starts: RouterMergeStarts,
) -> PyResult<()> {
    let RouterIncludePolicy {
        prefix,
        frontend_prefix,
        responses: inherited_responses,
        response_class: inherited_response_class,
        generate_unique_id_function: inherited_generate_unique_id_function,
        tags: inherited_tags,
        dependencies: inherited_dependencies,
        callbacks: inherited_callbacks,
        deprecated: inherited_deprecated,
        include_in_schema: inherited_include_in_schema,
        strict_content_type: inherited_strict_content_type,
    } = policy;
    let direct_route_group = ResponseClassResolutionGroup::new();
    let mut included_route_groups: Vec<(
        Arc<ResponseClassResolutionGroup>,
        Arc<ResponseClassResolutionGroup>,
    )> = Vec::new();
    for source_route in source.routes.iter().skip(starts.routes) {
        let path = format!("{prefix}{}", source_route.path);
        let route_inherited_responses = merge_response_maps(
            py,
            inherited_responses.bind(py),
            source_route.inherited_responses.bind(py),
        )?;
        let original_responses = api_route_state_ref(source_route.original_route.bind(py))?
            .responses
            .clone_ref(py);
        let original_responses_snapshot = clone_response_map(py, &original_responses)?;
        let responses = merge_response_maps(
            py,
            route_inherited_responses.bind(py),
            original_responses.bind(py),
        )?;
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
        let path_regex = route_path_regex(py, &path)?;
        let response_class_resolution_group = match source_route.response_class_resolution.as_ref()
        {
            Some(resolution) => {
                if let Some((_, group)) = included_route_groups
                    .iter()
                    .find(|(source_group, _)| Arc::ptr_eq(source_group, &resolution.group))
                {
                    Arc::clone(group)
                } else {
                    let group = ResponseClassResolutionGroup::new();
                    included_route_groups.push((Arc::clone(&resolution.group), Arc::clone(&group)));
                    group
                }
            }
            None => Arc::clone(&direct_route_group),
        };
        let response_class_resolution = ResponseClassResolution::for_included_route(
            py,
            source_route,
            source_router,
            inherited_response_class,
            &response_class_resolution_group,
        );
        let response_class = response_class_resolution.provisional_choice(py);
        let path_format = route_path_format(py, &path)?;
        let tags = combined_route_tags(inherited_tags, source_route.tags.as_deref());
        let source_callbacks = source_route
            .public_route
            .bind(py)
            .getattr("callbacks")?
            .unbind();
        let callbacks = effective_route_callbacks(py, inherited_callbacks, &source_callbacks)?;
        let generate_unique_id_function = GenerateUniqueIdChoice::first_explicit(
            py,
            &[
                &source_route.generate_unique_id_function,
                &source.generate_unique_id_function,
                inherited_generate_unique_id_function,
            ],
        );
        let strict_content_type = strict_content_type_python_value(
            py,
            source_route
                .strict_content_type
                .or(source.strict_content_type)
                .or(inherited_strict_content_type),
        )?;
        let original_route = source_route.original_route.clone_ref(py);
        let source_route_class = original_route.bind(py).get_type().unbind().into_any();
        let public_route_type = api_route_type(py)?;
        let route_class =
            (!source_route_class.bind(py).is(&public_route_type)).then_some(&source_route_class);
        let effective_route = new_api_route_view(
            py,
            ApiRouteViewConfig {
                route_class,
                path: &path,
                path_format: &path_format,
                path_regex: &path_regex,
                param_convertors: &param_convertors,
                methods: &source_route.methods,
                name: &source_route.name,
                tags: tags.as_deref().unwrap_or_default(),
                summary: source_route.summary.as_deref(),
                description: &source_route.description,
                response_description: &source_route.response_description,
                responses: &responses,
                deprecated: combined_deprecated(source_route.deprecated, inherited_deprecated),
                include_in_schema: inherited_include_in_schema && source_route.include_in_schema,
                operation_id: source_route.operation_id.as_deref(),
                openapi_extra: source_route.openapi_extra.as_ref(),
                generate_unique_id_function: &generate_unique_id_function,
                response_model_include: source_route.response_model_include.as_ref(),
                response_model_exclude: source_route.response_model_exclude.as_ref(),
                response_model_by_alias: source_route.response_model_by_alias,
                response_model_exclude_unset: source_route.response_model_exclude_unset,
                response_model_exclude_defaults: source_route.response_model_exclude_defaults,
                response_model_exclude_none: source_route.response_model_exclude_none,
                response_class: &response_class,
                response_class_resolution: Some(&response_class_resolution),
                dependency_overrides_provider,
                callbacks: Some(&callbacks),
                strict_content_type: &strict_content_type,
                stream_item_type: source_route.stream_item_type.as_ref(),
                response_model: source_route.response_model.as_ref(),
                status_code: source_route.status_code,
                dependencies: &source_route.router_dependencies,
            },
            source_route.endpoint.clone_ref(py),
        )?;
        let effective_route_context = new_route_context(
            py,
            original_route.clone_ref(py),
            effective_route.clone_ref(py),
        )?;
        let unique_id_value = generated_unique_id(
            py,
            &generate_unique_id_function,
            &effective_route_context,
            source_route.operation_id.as_deref(),
        )?;
        set_api_route_unique_id(py, &effective_route, unique_id_value.bind(py))?;
        set_api_route_description_initialized(py, &effective_route)?;
        let unique_id = python_string_value(unique_id_value.bind(py))?;
        let methods = api_route_methods(effective_route_context.bind(py))?;
        let route_scope = if path.starts_with('/') {
            Some(
                http_route_scope(
                    py,
                    &path,
                    source_route.endpoint.bind(py),
                    &methods,
                    &source_route.name,
                )?
                .0,
            )
        } else {
            None
        };
        let route_matcher = if route_scope.is_some() {
            Some(single_api_route_matcher(
                &path,
                &methods,
                source_route.status_code,
            )?)
        } else {
            None
        };
        // Included routes are lazy in FastAPI. Resolve class-dependent stream
        // behavior alongside response fields at first dispatch/OpenAPI access.
        let sse_stream = false;
        let mut operation_index = None;
        if route_scope.is_some() {
            let index = app
                .router
                .add_operation_with_methods(&path, &methods, source_route.status_code)
                .map_err(|error| PyValueError::new_err(error.to_string()))?;
            app.named_routes
                .add_route(&path, &source_route.name)
                .map_err(|error| PyValueError::new_err(error.to_string()))?;
            app.router
                .set_parameters(index, plan.input_parameters())
                .ok_or_else(|| PyRuntimeError::new_err("included FastAPI operation was lost"))?;
            operation_index = Some(index);
        }
        app.routes.push(FastApiRoute {
            operation_index,
            route_matcher,
            path,
            url_path_format: path_format.clone(),
            path_format,
            methods,
            name: source_route.name.clone(),
            route_scope,
            param_convertors,
            summary: source_route.summary.clone(),
            description: source_route.description.clone(),
            response_description: source_route.response_description.clone(),
            responses: responses.clone_ref(py),
            inherited_responses: route_inherited_responses,
            original_responses_snapshot,
            openapi_extra: source_route
                .openapi_extra
                .as_ref()
                .map(|value| value.clone_ref(py)),
            operation_id: source_route.operation_id.clone(),
            unique_id,
            unique_id_value,
            generate_unique_id_function,
            deprecated: combined_deprecated(source_route.deprecated, inherited_deprecated),
            tags,
            status_code: source_route.status_code,
            include_in_schema: inherited_include_in_schema && source_route.include_in_schema,
            response_class,
            response_class_resolution: Some(response_class_resolution),
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
            endpoint_is_coroutine: source_route.endpoint_is_coroutine,
            original_route,
            public_route: effective_route_context.clone_ref(py),
            request_handler: None,
            effective_route_context: Some(effective_route_context),
            response_model: source_route
                .response_model
                .as_ref()
                .map(|model| model.clone_ref(py)),
            response_field: ResponseFieldState::Deferred,
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
    for source_route in source.websocket_routes.iter().skip(starts.websocket_routes) {
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
        let route_scope = websocket_route_scope(
            py,
            &path,
            source_route.endpoint.bind(py),
            Some(&source_route.name),
        )?;
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
    for source_frontend in source.frontend_routes.iter().skip(starts.frontend_routes) {
        let mut dependency_plan = source_frontend.dependency_plan.clone_ref(py);
        dependency_plan.prepend_dependencies(py, inherited_dependencies)?;
        app.frontend_routes.push(FastApiFrontendRoute {
            path: join_frontend_paths(frontend_prefix, &source_frontend.path),
            static_files: source_frontend.static_files.clone_ref(py),
            fallback: source_frontend.fallback,
            dependency_plan,
        });
        app.bump_routes_version();
    }
    Ok(())
}

#[derive(Clone, Copy)]
enum IncludedRouteCategory {
    Http,
    WebSocket,
    Frontend,
}

impl IncludedRouteCategory {
    fn route_count(self, app: &PyFastApi) -> usize {
        match self {
            Self::Http => app.routes.len(),
            Self::WebSocket => app.websocket_routes.len(),
            Self::Frontend => app.frontend_routes.len(),
        }
    }

    fn include_position(self, include: &FastApiRouterInclude) -> usize {
        match self {
            Self::Http => include.route_position,
            Self::WebSocket => include.websocket_route_position,
            Self::Frontend => include.frontend_route_position,
        }
    }

    fn include_indexes(self, include: &FastApiRouterInclude) -> &[usize] {
        match self {
            Self::Http => &include.source_route_indexes,
            Self::WebSocket => &include.source_websocket_route_indexes,
            Self::Frontend => &include.source_frontend_route_indexes,
        }
    }
}

fn effective_route_order(
    py: Python<'_>,
    app: &PyFastApi,
    category: IncludedRouteCategory,
) -> PyResult<Vec<usize>> {
    let route_count = category.route_count(app);
    let mut included_indexes = HashSet::new();
    for include in &app.router_includes {
        if category.include_position(include) > route_count {
            return Err(PyRuntimeError::new_err(
                "included route order position is outside its route collection",
            ));
        }
        for &route_index in category.include_indexes(include) {
            if route_index >= route_count || !included_indexes.insert(route_index) {
                return Err(PyRuntimeError::new_err(
                    "included route order mapping is invalid",
                ));
            }
        }
    }

    let mut route_order = Vec::with_capacity(route_count);
    for position in 0..=route_count {
        for include in &app.router_includes {
            if category.include_position(include) != position {
                continue;
            }
            let source_router = include
                .router
                .bind(py)
                .extract::<PyRef<'_, PyApiRouter>>()?
                .inner_app(py)?;
            let source = source_router.bind(py).borrow();
            for source_index in effective_route_order(py, &source, category)? {
                let destination_index = category
                    .include_indexes(include)
                    .get(source_index)
                    .copied()
                    .ok_or_else(|| {
                        PyRuntimeError::new_err("included route order mapping was lost")
                    })?;
                route_order.push(destination_index);
            }
        }
        if position < route_count && !included_indexes.contains(&position) {
            route_order.push(position);
        }
    }

    if route_order.len() != route_count
        || route_order.iter().copied().collect::<HashSet<_>>().len() != route_count
    {
        return Err(PyRuntimeError::new_err(
            "effective route order does not cover its route collection",
        ));
    }
    Ok(route_order)
}

fn synchronize_included_route_orders(py: Python<'_>, app: &Py<PyFastApi>) -> PyResult<()> {
    let (http_order, websocket_order) = {
        let app = app.bind(py).borrow();
        let http_route_order = effective_route_order(py, &app, IncludedRouteCategory::Http)?;
        let http_order = http_route_order
            .iter()
            .filter_map(|route_index| {
                app.routes
                    .get(*route_index)
                    .and_then(|route| route.operation_index)
            })
            .collect::<Vec<_>>();
        let websocket_order = effective_route_order(py, &app, IncludedRouteCategory::WebSocket)?;
        (http_order, websocket_order)
    };

    let mut app = app.bind(py).borrow_mut();
    if !app.router.set_route_order(&http_order) {
        return Err(PyRuntimeError::new_err(
            "effective HTTP route order is incompatible with its operation table",
        ));
    }
    if !app.websocket_router.set_route_order(&websocket_order) {
        return Err(PyRuntimeError::new_err(
            "effective WebSocket route order is incompatible with its operation table",
        ));
    }
    Ok(())
}

struct IncludedRouterRefresh {
    index: usize,
    router: Py<PyAny>,
    public_route: Py<PyAny>,
    merge_prefix: String,
    frontend_merge_prefix: String,
    responses: Py<PyDict>,
    response_class: ResponseClassChoice,
    generate_unique_id_function: GenerateUniqueIdChoice,
    tags: Vec<String>,
    dependencies: Vec<Py<PyAny>>,
    callbacks: Vec<Py<PyAny>>,
    deprecated: Option<bool>,
    include_in_schema: bool,
    strict_content_type: Option<bool>,
    source_route_cursor: usize,
    source_route_indexes: Vec<usize>,
    source_websocket_route_cursor: usize,
    source_websocket_route_indexes: Vec<usize>,
    source_frontend_route_cursor: usize,
    source_frontend_route_indexes: Vec<usize>,
}

fn refresh_included_router_routes(py: Python<'_>, app: &Py<PyFastApi>) -> PyResult<()> {
    refresh_included_router_routes_inner(py, app, &mut HashSet::new())
}

fn refresh_included_router_routes_inner(
    py: Python<'_>,
    app: &Py<PyFastApi>,
    visited: &mut HashSet<usize>,
) -> PyResult<()> {
    if !visited.insert(app.as_ptr() as usize) {
        return Ok(());
    }

    let includes = {
        let app = app.bind(py).borrow();
        app.router_includes
            .iter()
            .enumerate()
            .map(|(index, include)| IncludedRouterRefresh {
                index,
                router: include.router.clone_ref(py),
                public_route: include.public_route.clone_ref(py),
                merge_prefix: include.merge_prefix.clone(),
                frontend_merge_prefix: include.frontend_merge_prefix.clone(),
                responses: include.responses.clone_ref(py),
                response_class: include.response_class.clone_ref(py),
                generate_unique_id_function: include.generate_unique_id_function.clone_ref(py),
                tags: include.tags.clone(),
                dependencies: include
                    .dependencies
                    .iter()
                    .map(|dependency| dependency.clone_ref(py))
                    .collect(),
                callbacks: include
                    .callbacks
                    .iter()
                    .map(|callback| callback.clone_ref(py))
                    .collect(),
                deprecated: include.deprecated,
                include_in_schema: include.include_in_schema,
                strict_content_type: include.strict_content_type,
                source_route_cursor: include.source_route_cursor,
                source_route_indexes: include.source_route_indexes.clone(),
                source_websocket_route_cursor: include.source_websocket_route_cursor,
                source_websocket_route_indexes: include.source_websocket_route_indexes.clone(),
                source_frontend_route_cursor: include.source_frontend_route_cursor,
                source_frontend_route_indexes: include.source_frontend_route_indexes.clone(),
            })
            .collect::<Vec<_>>()
    };

    for include in includes {
        let source_router = include
            .router
            .bind(py)
            .extract::<PyRef<'_, PyApiRouter>>()?
            .inner_app(py)?;
        refresh_included_router_routes_inner(py, &source_router, visited)?;

        let source = source_router.bind(py).borrow();
        if source.routes.len() <= include.source_route_cursor
            && source.websocket_routes.len() <= include.source_websocket_route_cursor
            && source.frontend_routes.len() <= include.source_frontend_route_cursor
        {
            continue;
        }

        let dependency_overrides_provider = fastapi_public_instance(py, app)?;
        let (
            destination_route_start,
            destination_websocket_route_start,
            destination_frontend_route_start,
            mut destination,
        ) = {
            let destination = app.bind(py).borrow_mut();
            (
                destination.routes.len(),
                destination.websocket_routes.len(),
                destination.frontend_routes.len(),
                destination,
            )
        };
        // Route vectors keep stable append-only ids. A separate order
        // projection places late registrations back at this include slot.
        merge_router_routes_from(
            py,
            &mut destination,
            &source_router,
            &source,
            Some(&dependency_overrides_provider),
            RouterIncludePolicy {
                prefix: &include.merge_prefix,
                frontend_prefix: &include.frontend_merge_prefix,
                responses: &include.responses,
                response_class: &include.response_class,
                generate_unique_id_function: &include.generate_unique_id_function,
                tags: &include.tags,
                dependencies: &include.dependencies,
                callbacks: &include.callbacks,
                deprecated: include.deprecated,
                include_in_schema: include.include_in_schema,
                strict_content_type: include.strict_content_type,
            },
            RouterMergeStarts {
                routes: include.source_route_cursor,
                websocket_routes: include.source_websocket_route_cursor,
                frontend_routes: include.source_frontend_route_cursor,
            },
        )?;

        let mut source_route_indexes = include.source_route_indexes;
        source_route_indexes.extend(destination_route_start..destination.routes.len());
        let mut source_websocket_route_indexes = include.source_websocket_route_indexes;
        source_websocket_route_indexes
            .extend(destination_websocket_route_start..destination.websocket_routes.len());
        let mut source_frontend_route_indexes = include.source_frontend_route_indexes;
        source_frontend_route_indexes
            .extend(destination_frontend_route_start..destination.frontend_routes.len());
        let effective_route_contexts = source_route_indexes
            .iter()
            .map(|route_index| {
                destination
                    .routes
                    .get(*route_index)
                    .map(|route| route.public_route.clone_ref(py))
                    .ok_or_else(|| {
                        PyRuntimeError::new_err("included public route context was lost")
                    })
            })
            .collect::<PyResult<Vec<_>>>()?;
        let mut fields = IncludedFieldBranch::from_router_indexes(&source, &source_route_indexes);
        let router_include = destination
            .router_includes
            .get_mut(include.index)
            .ok_or_else(|| PyRuntimeError::new_err("included router state was lost"))?;
        fields.preserve_ready_state(&router_include.fields);
        router_include.source_route_cursor = source.routes.len();
        router_include.source_route_indexes = source_route_indexes;
        router_include.source_websocket_route_cursor = source.websocket_routes.len();
        router_include.source_websocket_route_indexes = source_websocket_route_indexes;
        router_include.source_frontend_route_cursor = source.frontend_routes.len();
        router_include.source_frontend_route_indexes = source_frontend_route_indexes;
        router_include.fields = fields;
        drop(destination);
        let included_route = include
            .public_route
            .bind(py)
            .extract::<PyRef<'_, PyFastApiIncludedRouter>>()?;
        replace_python_list(
            py,
            &included_route.effective_route_contexts,
            &effective_route_contexts,
        )?;
    }
    synchronize_included_route_orders(py, app)
}

#[pyclass(name = "_OperationDecorator", module = "fastapi_rs._core", unsendable)]
struct PyOperationDecorator {
    app: Py<PyFastApi>,
    dependency_overrides_provider: Option<Py<PyAny>>,
    route_class_selection: Option<Py<PyAny>>,
    path: String,
    method: String,
    callback_methods: Vec<String>,
    registration_cache: Option<Rc<RefCell<OperationRouteRegistrationCache>>>,
    summary: Option<String>,
    description: Option<String>,
    response_description: String,
    responses: Option<Py<PyAny>>,
    callbacks: Option<Py<PyAny>>,
    openapi_extra: Option<Py<PyAny>>,
    operation_id: Option<String>,
    generate_unique_id_function: GenerateUniqueIdChoice,
    deprecated: Option<bool>,
    deprecated_precombined: bool,
    tags: Option<Vec<String>>,
    dependencies: Vec<Py<PyAny>>,
    response_model: Option<Py<PyAny>>,
    status_code: Option<u16>,
    include_in_schema: bool,
    strict_content_type: StrictContentTypeArgument,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    response_class: ResponseClassChoice,
    name: Option<String>,
}

#[derive(Default)]
struct OperationRouteRegistrationCache {
    public_route: Option<Py<PyAny>>,
    unique_id: Option<Py<PyAny>>,
    request_handler: Option<Py<PyAny>>,
}

fn register_multi_method_api_route(
    py: Python<'_>,
    decorator: Py<PyOperationDecorator>,
    endpoint: Py<PyAny>,
    callback_methods: Vec<String>,
    tags: Option<Vec<String>>,
    deprecated: Option<bool>,
    deprecated_precombined: bool,
) -> PyResult<()> {
    let (inherited_tags, inherited_deprecated) = {
        let decorator = decorator.bind(py).borrow();
        (decorator.tags.clone(), decorator.deprecated)
    };
    let tags = combined_route_tags(
        inherited_tags.as_deref().unwrap_or_default(),
        tags.as_deref(),
    );
    let deprecated = combined_deprecated(deprecated, inherited_deprecated);
    {
        let mut decorator = decorator.bind(py).borrow_mut();
        decorator.callback_methods = callback_methods.clone();
        decorator.registration_cache = Some(Rc::new(RefCell::new(
            OperationRouteRegistrationCache::default(),
        )));
        decorator.tags = tags;
        decorator.deprecated = deprecated;
        decorator.deprecated_precombined = deprecated_precombined;
    }
    decorator.bind(py).borrow_mut().method = callback_methods.first().cloned().unwrap_or_default();
    decorator.bind(py).call1((endpoint.bind(py),))?;
    Ok(())
}

fn inspect_generator_kind(
    py: Python<'_>,
    inspect: &Bound<'_, PyAny>,
    callable: &Bound<'_, PyAny>,
) -> PyResult<FastApiGeneratorKind> {
    let without_partials = dependency_callable_without_partials(py, callable)?;
    let unwrapped = inspect.getattr("unwrap")?.call1((&without_partials,))?;
    for candidate in [&without_partials, &unwrapped] {
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

    for call_source in [&without_partials, &unwrapped] {
        if let Ok(dunder_call) = call_source.getattr("__call__") {
            let dunder_without_partials = dependency_callable_without_partials(py, &dunder_call)?;
            let unwrapped_dunder_call = inspect
                .getattr("unwrap")?
                .call1((&dunder_without_partials,))?;
            for candidate in [&dunder_without_partials, &unwrapped_dunder_call] {
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
    }

    Ok(FastApiGeneratorKind::None)
}

fn generator_kind(py: Python<'_>, callable: &Bound<'_, PyAny>) -> PyResult<FastApiGeneratorKind> {
    let inspect = py.import("inspect")?;
    let kind = inspect_generator_kind(py, &inspect, callable)?;
    if kind.is_generator() {
        return Ok(kind);
    }
    let without_partials = dependency_callable_without_partials(py, callable)?;
    let unwrapped = inspect.getattr("unwrap")?.call1((&without_partials,))?;
    if inspect
        .getattr("isclass")?
        .call1((&unwrapped,))?
        .extract::<bool>()?
    {
        return Ok(FastApiGeneratorKind::None);
    }
    match without_partials.getattr("__call__") {
        Ok(dunder_call) => inspect_generator_kind(py, &inspect, &dunder_call),
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

fn route_response_declarations(
    py: Python<'_>,
    responses: Option<&Py<PyAny>>,
) -> PyResult<Py<PyDict>> {
    let declarations = PyDict::new(py);
    if let Some(responses) = responses {
        // Source's saved decorator captures the object and shallow-merges it at
        // attachment. Nested records/annotations retain their original owners.
        if responses.bind(py).is_truthy()? {
            for (status, response) in responses.bind(py).cast::<PyDict>()?.iter() {
                declarations.set_item(status, response)?;
            }
        }
    }
    Ok(declarations.unbind())
}

fn response_map_or_empty(py: Python<'_>, responses: Option<Py<PyAny>>) -> PyResult<Py<PyAny>> {
    match responses {
        Some(responses) if responses.bind(py).is_truthy()? => Ok(responses),
        _ => Ok(PyDict::new(py).into_any().unbind()),
    }
}

fn merge_response_maps(
    py: Python<'_>,
    inherited: &Bound<'_, PyDict>,
    route: &Bound<'_, PyDict>,
) -> PyResult<Py<PyDict>> {
    let merged = PyDict::new(py);
    for declarations in [inherited, route] {
        for (status, response) in declarations.iter() {
            merged.set_item(status, response)?;
        }
    }
    Ok(merged.unbind())
}

fn clone_response_map(py: Python<'_>, responses: &Py<PyDict>) -> PyResult<Py<PyDict>> {
    let empty = PyDict::new(py);
    merge_response_maps(py, &empty, responses.bind(py))
}

fn is_body_allowed_for_status_code(py: Python<'_>, status: &Bound<'_, PyAny>) -> PyResult<bool> {
    if status.is_none() {
        return Ok(true);
    }
    // Source's literal membership test precedes int conversion and is case-sensitive.
    if PyFrozenSet::new(py, ["default", "1XX", "2XX", "3XX", "4XX", "5XX"])?.contains(status)? {
        return Ok(true);
    }
    let code = py.import("builtins")?.getattr("int")?.call1((status,))?;
    Ok(!(code.lt(200)? || code.eq(204)? || code.eq(205)? || code.eq(304)?))
}

fn build_additional_response_fields(
    py: Python<'_>,
    responses: &Bound<'_, PyDict>,
    unique_id: &str,
) -> PyResult<Vec<AdditionalResponseField>> {
    let mut fields = Vec::with_capacity(responses.len());
    for (status, response) in responses.iter() {
        let response = response
            .cast::<PyDict>()
            .map_err(|_| PyAssertionError::new_err("An additional response must be a dict"))?;
        let model = response.get_item("model")?;
        let field = match model {
            Some(model) if model.is_truthy()? => {
                if !is_body_allowed_for_status_code(py, &status)? {
                    let options = PyDict::new(py);
                    options.set_item("status", &status)?;
                    let message =
                        PyString::new(py, "Status code {status} must not have a response body")
                            .call_method("format", (), Some(&options))?
                            .extract::<String>()?;
                    return Err(PyAssertionError::new_err(message));
                }
                let options = PyDict::new(py);
                options.set_item("status", &status)?;
                options.set_item("unique_id", unique_id)?;
                let name = PyString::new(py, "Response_{status}_{unique_id}")
                    .call_method("format", (), Some(&options))?
                    .extract::<String>()?;
                Some(ResponseField::new(py, &name, &model)?)
            }
            _ => None,
        };
        fields.push(AdditionalResponseField {
            status: status.unbind(),
            response: response.clone().unbind(),
            field,
        });
    }
    Ok(fields)
}

fn additional_response_openapi(
    py: Python<'_>,
    response: &AdditionalResponseField,
    response_schemas: &ResponseFieldSchemaBatch,
    next_field_key: &mut usize,
) -> PyResult<OpenApiAdditionalResponse> {
    // Keep the raw declaration key until the OpenAPI stage. Source canonicalizes
    // it before reading the corresponding field schema.
    let status = response.status.bind(py).str()?.call_method0("upper")?;
    let status = if status.eq("DEFAULT")? {
        PyString::new(py, "default").into_any()
    } else {
        status
    };
    let response_schema = match response.field.as_ref() {
        Some(field) => {
            let schema = response_schemas.schema(py, *next_field_key, field)?;
            *next_field_key += 1;
            Some(schema)
        }
        None => None,
    };
    let response_document = py
        .import("copy")?
        .getattr("deepcopy")?
        .call1((response.response.bind(py),))?
        .cast_into::<PyDict>()?;
    response_document.call_method1("pop", ("model", py.None()))?;
    Ok(OpenApiAdditionalResponse {
        status: status.unbind(),
        status_code: response.status.clone_ref(py),
        response: response_document.unbind(),
        response_schema,
    })
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
    let (
        generate_unique_id_function,
        router_tags,
        router_dependencies,
        router_deprecated,
        router_include_in_schema,
    ) = {
        let app = app.bind(py).borrow();
        (
            GenerateUniqueIdChoice::first_explicit(
                py,
                &[
                    &response_model_options.generate_unique_id_function,
                    &app.generate_unique_id_function,
                ],
            ),
            app.router_tags.clone_ref(py),
            app.router_dependencies
                .iter()
                .map(|dependency| dependency.clone_ref(py))
                .collect::<Vec<_>>(),
            app.router_deprecated,
            app.router_include_in_schema,
        )
    };
    let router_tags = fastapi_router_tags(router_tags.bind(py))?;
    let tags = combined_route_tags(&router_tags, response_model_options.tags.as_deref());
    let mut dependencies = router_dependencies;
    dependencies.extend(response_model_options.dependencies);
    Py::new(
        py,
        PyOperationDecorator {
            dependency_overrides_provider: Some(fastapi_public_instance(py, &app)?),
            route_class_selection: None,
            app,
            path: path.to_owned(),
            method: method.to_owned(),
            callback_methods: vec![method.to_owned()],
            registration_cache: None,
            summary: response_model_options.summary,
            description: response_model_options.description,
            response_description: response_model_options
                .response_description
                .unwrap_or_else(|| DEFAULT_RESPONSE_DESCRIPTION.to_owned()),
            responses: response_model_options.responses,
            callbacks: response_model_options.callbacks,
            openapi_extra: response_model_options.openapi_extra,
            operation_id: response_model_options.operation_id,
            generate_unique_id_function,
            deprecated: combined_deprecated(response_model_options.deprecated, router_deprecated),
            deprecated_precombined: false,
            tags,
            dependencies,
            response_model,
            status_code,
            include_in_schema: response_model_options.include_in_schema && router_include_in_schema,
            strict_content_type: response_model_options.strict_content_type,
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
        let router_callbacks = { self.app.bind(py).borrow().router_callbacks.clone_ref(py) };
        let callbacks = router_route_callbacks(py, &router_callbacks, self.callbacks.as_ref())?;
        let (inferred_name, param_convertors) =
            route_reverse_metadata(py, &self.path, endpoint.bind(py))?;
        let name = self.name.clone().unwrap_or(inferred_name);
        let description =
            normalized_route_description(py, self.description.as_deref(), endpoint.bind(py))?;
        let (scope_path, event_only) = {
            let app = self.app.bind(py).borrow();
            let scope_path = format!("{}{}", app.route_scope_prefix, self.path);
            let event_only = app.is_router_inner && !self.path.starts_with('/');
            (scope_path, event_only)
        };
        let deprecated = if self.deprecated_precombined {
            self.deprecated
        } else {
            combined_deprecated(self.deprecated, None)
        };
        let path_format = if event_only {
            route_path_format(py, &scope_path)?
        } else {
            http_route_scope(
                py,
                &scope_path,
                endpoint.bind(py),
                &self.callback_methods,
                &name,
            )?
            .1
        };
        let url_path_format = route_path_format(py, &self.path)?;
        let callback_param_convertors = route_param_convertors(py, &scope_path)?;
        let path_regex = route_path_regex(py, &scope_path)?;
        let declared_responses = route_response_declarations(py, self.responses.as_ref())?;
        let response_defaults = self.app.bind(py).borrow().responses.clone_ref(py);
        let response_defaults = route_response_declarations(py, Some(&response_defaults))?;
        let responses =
            merge_response_maps(py, response_defaults.bind(py), declared_responses.bind(py))?;
        if !endpoint.bind(py).is_callable() {
            return Err(PyAssertionError::new_err("An endpoint must be a callable"));
        }
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
        // Source captures this once when building the request handler, then
        // uses it for endpoint dispatch and response model validation.
        let endpoint_is_coroutine = dependency_override_callable(py, endpoint.bind(py))?
            != DependencyOverrideCallable::Sync;
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
            .clone_ref(py);
        let response_class = ResponseClassChoice::first_explicit(
            py,
            &[&self.response_class, &default_response_class],
        );
        let actual_response_class = response_class.actual(py)?;
        let sse_stream = generator_kind.is_generator()
            && actual_response_class.bind(py).is_instance_of::<PyType>()
            && sse::is_event_source_response_class(py, actual_response_class.bind(py))?;
        let stream_item_type = if response_class.is_default() || sse_stream {
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
        let inherited_strict_content_type = self.app.bind(py).borrow().strict_content_type;
        let (strict_content_type_value, strict_content_type) = self
            .strict_content_type
            .resolve(py, inherited_strict_content_type)?;
        let public_route_type = api_route_type(py)?;
        let route_class = match self.route_class_selection.as_ref() {
            Some(route_class) if route_class.bind(py).is(&public_route_type) => None,
            Some(route_class) => Some(route_class.clone_ref(py)),
            None => self
                .app
                .bind(py)
                .borrow()
                .router_route_class
                .as_ref()
                .map(|route_class| route_class.clone_ref(py)),
        };
        let (public_route, unique_id, request_handler) = api_route_view_and_unique_id(
            py,
            ApiRouteViewConfig {
                route_class: route_class.as_ref(),
                path: &scope_path,
                path_format: &path_format,
                path_regex: &path_regex,
                param_convertors: &callback_param_convertors,
                methods: &self.callback_methods,
                name: &name,
                tags: self.tags.as_deref().unwrap_or_default(),
                summary: self.summary.as_deref(),
                description: &description,
                response_description: &self.response_description,
                responses: &responses,
                deprecated,
                include_in_schema: self.include_in_schema,
                operation_id: self.operation_id.as_deref(),
                openapi_extra: self.openapi_extra.as_ref(),
                generate_unique_id_function: &self.generate_unique_id_function,
                response_model_include: self.response_model_include.as_ref(),
                response_model_exclude: self.response_model_exclude.as_ref(),
                response_model_by_alias: self.response_model_by_alias,
                response_model_exclude_unset: self.response_model_exclude_unset,
                response_model_exclude_defaults: self.response_model_exclude_defaults,
                response_model_exclude_none: self.response_model_exclude_none,
                response_class: &response_class,
                response_class_resolution: None,
                dependency_overrides_provider: self.dependency_overrides_provider.as_ref(),
                callbacks: Some(&callbacks),
                strict_content_type: &strict_content_type_value,
                stream_item_type: None,
                response_model: self.response_model.as_ref(),
                status_code: self.status_code,
                dependencies: &route_dependencies,
            },
            endpoint.clone_ref(py),
            &self.generate_unique_id_function,
            self.operation_id.as_deref(),
            self.registration_cache.as_ref(),
        )?;
        let methods = api_route_methods(public_route.bind(py))?;
        let route_scope = if event_only {
            None
        } else {
            Some(http_route_scope(py, &scope_path, endpoint.bind(py), &methods, &name)?.0)
        };
        let route_matcher = if route_scope.is_some() {
            Some(single_api_route_matcher(
                &scope_path,
                &methods,
                self.status_code,
            )?)
        } else {
            None
        };
        let (summary, tags) = api_route_callback_summary_tags(
            public_route.bind(py),
            self.summary.as_deref(),
            self.tags.as_deref(),
        )?;
        let unique_id_text = python_string_value(unique_id.bind(py))?;
        let additional = build_additional_response_fields(py, responses.bind(py), &unique_id_text)?;
        let response_field = build_response_field(py, &unique_id_text, response_model.as_ref())?;
        set_api_route_response_field(py, &public_route, response_field.as_ref())?;
        let original_responses = api_route_state_ref(public_route.bind(py))?
            .responses
            .clone_ref(py);
        let original_responses_snapshot = clone_response_map(py, &original_responses)?;
        let inherited_responses = PyDict::new(py).unbind();
        let inputs = plan.input_parameters();
        let mut app = self.app.bind(py).borrow_mut();
        let mut operation_index = None;
        if self.path.starts_with('/') || !app.is_router_inner {
            let index = app
                .router
                .add_operation_with_methods(&self.path, &methods, self.status_code)
                .map_err(|error| PyValueError::new_err(error.to_string()))?;
            app.named_routes
                .add_route(&self.path, &name)
                .map_err(|error| PyValueError::new_err(error.to_string()))?;
            app.router
                .set_parameters(index, inputs)
                .ok_or_else(|| PyRuntimeError::new_err("registered FastAPI operation was lost"))?;
            operation_index = Some(index);
        }
        let route = FastApiRoute {
            operation_index,
            route_matcher,
            path: self.path.clone(),
            path_format,
            url_path_format,
            methods,
            name,
            route_scope,
            param_convertors,
            summary,
            description,
            response_description: self.response_description.clone(),
            responses,
            inherited_responses,
            original_responses_snapshot,
            openapi_extra: self.openapi_extra.as_ref().map(|value| value.clone_ref(py)),
            operation_id: self.operation_id.clone(),
            unique_id: unique_id_text,
            unique_id_value: unique_id,
            generate_unique_id_function: self.generate_unique_id_function.clone_ref(py),
            deprecated,
            tags,
            status_code: self.status_code,
            include_in_schema: self.include_in_schema,
            response_class,
            response_class_resolution: None,
            strict_content_type,
            sse_stream,
            generator_kind,
            stream_item_type,
            endpoint: endpoint.clone_ref(py),
            endpoint_is_coroutine,
            original_route: public_route.clone_ref(py),
            public_route,
            request_handler,
            effective_route_context: None,
            response_model,
            response_field: ResponseFieldState::Ready(RouteResponseFields {
                primary: response_field,
                additional,
            }),
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
        };
        let openapi_snapshots = route
            .methods
            .iter()
            .map(|method| OpenApiRouteSnapshot::from_route(py, &route, method, false))
            .collect::<PyResult<Vec<_>>>()?;
        set_api_route_openapi_snapshots(py, &route.public_route, openapi_snapshots)?;
        app.route_surface
            .bind(py)
            .append(route.public_route.bind(py))?;
        app.routes.push(route);
        let route_index = app.routes.len() - 1;
        app.route_dispatch_order
            .push(RouteDispatchEntry::ApiRoute(route_index));
        app.bump_routes_version();
        Ok(endpoint)
    }
}

#[pymethods]
impl PyWebSocketDecorator {
    fn __call__(&self, py: Python<'_>, endpoint: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let path_parameters = path_parameter_names(&self.path);
        let app = self.app.bind(py).borrow();
        let mut route_dependencies = app
            .dependencies
            .iter()
            .chain(&app.router_dependencies)
            .map(|dependency| dependency.clone_ref(py))
            .collect::<Vec<_>>();
        drop(app);
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
        app.route_surface.bind(py).append(route_scope.bind(py))?;
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
        let route_index = app.websocket_routes.len() - 1;
        app.route_dispatch_order
            .push(RouteDispatchEntry::ApiWebSocketRoute(route_index));
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
        let route_index = app.websocket_routes.len() - 1;
        app.route_dispatch_order
            .push(RouteDispatchEntry::ApiWebSocketRoute(route_index));
        Ok(endpoint)
    }
}

impl CallablePlan {
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
        let signature_kwargs = PyDict::new(py);
        signature_kwargs.set_item("eval_str", true)?;
        let signature = match inspect
            .getattr("signature")?
            .call((callable.bind(py),), Some(&signature_kwargs))
        {
            Ok(signature) => signature,
            Err(error) if error.is_instance_of::<PyNameError>(py) => {
                inspect.getattr("signature")?.call1((callable.bind(py),))?
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
                    typed_parameter_annotation(py, callable.bind(py), &raw_annotation)?
                };
                let raw_default = item.getattr("default")?;
                let (annotation, mut metadata) = annotation_parts(py, annotation)?;
                let full_annotation =
                    compose_parameter_annotation(py, annotation.bind(py), &metadata)?;
                let annotated_marker = annotated_parameter_marker(py, &metadata)?;
                let annotated_dependency_index = match annotated_marker {
                    Some(AnnotatedParameterMarker::Dependency(index)) => Some(index),
                    _ => None,
                };
                let has_annotated_field_marker =
                    matches!(annotated_marker, Some(AnnotatedParameterMarker::Field(_)));
                let annotated_field_marker = match annotated_marker {
                    Some(AnnotatedParameterMarker::Field(index)) => Some(
                        metadata
                            .get(index)
                            .ok_or_else(|| {
                                PyRuntimeError::new_err(
                                    "selected FastAPI field marker is missing",
                                )
                            })?
                            .clone_ref(py),
                    ),
                    _ => None,
                };
                if let Some(AnnotatedParameterMarker::Field(index)) = annotated_marker {
                    let field_marker = &metadata[index];
                    let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
                    if !field_marker.bind(py).getattr("default")?.is(&undefined) {
                        let field_name = match parameter_marker_kind(py, field_marker.bind(py))?
                            .as_deref()
                        {
                            Some("body") => "Body",
                            Some("path") => "Path",
                            Some("query") => "Query",
                            Some("header") => "Header",
                            Some("cookie") => "Cookie",
                            Some("form") => "Form",
                            Some("file") => "File",
                            _ => {
                                return Err(PyRuntimeError::new_err(
                                    "selected FastAPI field marker has no field kind",
                                ));
                            }
                        };
                        let parameter_name = PyString::new(py, &name).repr()?;
                        return Err(PyAssertionError::new_err(format!(
                            "`{field_name}` default value cannot be set in `Annotated` for {}. Set the default value with `=` instead.",
                            parameter_name.to_string_lossy()
                        )));
                    }
                    if !raw_default.is(&empty) && path_parameters.contains(&name) {
                        return Err(PyAssertionError::new_err(
                            "Path parameters cannot have default values",
                        ));
                    }
                }
                let default_is_dependency_record =
                    !raw_default.is(&empty) && is_dependency_record(py, &raw_default)?;
                let default_is_field_info =
                    !raw_default.is(&empty) && is_pydantic_field_info(py, &raw_default)?;
                let conflict = if default_is_dependency_record {
                    if annotated_dependency_index.is_some() {
                        Some(
                            "Cannot specify `Depends` in `Annotated` and default value together for",
                        )
                    } else if has_annotated_field_marker {
                        Some(
                            "Cannot specify a FastAPI annotation in `Annotated` and `Depends` as a default value together for",
                        )
                    } else {
                        None
                    }
                } else if default_is_field_info && has_annotated_field_marker {
                    Some(
                        "Cannot specify FastAPI annotations in `Annotated` and default value together for",
                    )
                } else {
                    None
                };
                if let Some(conflict) = conflict {
                    let parameter_name = PyString::new(py, &name).repr()?;
                    return Err(PyAssertionError::new_err(format!(
                        "{conflict} {}",
                        parameter_name.to_string_lossy()
                    )));
                }
                let mut selected_metadata = Vec::with_capacity(metadata.len() + 1);
                for (index, marker) in metadata.into_iter().enumerate() {
                    if !is_dependency_record(py, marker.bind(py))?
                        || Some(index) == annotated_dependency_index
                    {
                        selected_metadata.push(marker);
                    }
                }
                metadata = selected_metadata;
                if default_is_dependency_record {
                    metadata.push(raw_default.clone().unbind());
                }
                let mut field_info = match annotated_marker {
                    Some(AnnotatedParameterMarker::Field(_)) => Some(
                        copy_annotated_field_info(
                            py,
                            annotated_field_marker
                                .as_ref()
                                .ok_or_else(|| {
                                    PyRuntimeError::new_err(
                                        "selected FastAPI field marker was not retained",
                                    )
                                })?
                                .bind(py),
                            full_annotation.bind(py),
                            (!raw_default.is(&empty)).then_some(&raw_default),
                        )?,
                    ),
                    _ if default_is_field_info => {
                        let field_info = raw_default.clone();
                        field_info.setattr("annotation", annotation.bind(py))?;
                        Some(field_info.unbind())
                    }
                    _ => None,
                };
                let mut source = parameter_source(
                    py,
                    &name,
                    annotation.bind(py),
                    &metadata,
                    path_parameters,
                    true,
                    field_info.as_ref().map(|value| value.bind(py)),
                )?;
                if field_info.is_none()
                    && matches!(source, ParameterSource::Input { .. })
                {
                    field_info = Some(inferred_parameter_field_info(
                        py,
                        full_annotation.bind(py),
                        &raw_default,
                        &empty,
                        path_parameters.contains(&name),
                    )?);
                    source = parameter_source(
                        py,
                        &name,
                        annotation.bind(py),
                        &metadata,
                        path_parameters,
                        true,
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?;
                }
                if field_info.is_some() {
                    crate::response_field::validate_pydantic_v1_annotation(
                        py,
                        full_annotation.bind(py),
                    )?;
                }
                let (required, default) = match field_info.as_ref() {
                    Some(field_info) => parameter_field_info_defaults(py, field_info.bind(py))?,
                    None => (false, None),
                };
                let (validated_annotation, default_delivery) = match field_info.as_ref() {
                    Some(field_info) => (
                        pydantic_field_schema_annotation(py, field_info.bind(py))?,
                        ParameterDefaultDelivery::InAnnotation,
                    ),
                    None => (
                        annotation.clone_ref(py),
                        ParameterDefaultDelivery::External,
                    ),
                };
                let is_sequence = field_annotation_is_sequence(py, validated_annotation.bind(py))?;
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
                                Some(header_model_convert_underscores(
                                    field_info.as_ref().map(|value| value.bind(py)),
                                )?)
                            } else {
                                None
                            };
                            (Some(model_fields), Some(model_config), convert_underscores)
                        }
                        _ => (None, None, None),
                    };
                let validation_adapter = if matches!(&source, ParameterSource::Input { .. }) {
                    Some(build_python_value_adapter(
                        py,
                        validated_annotation.bind(py),
                    )?)
                } else {
                    None
                };
                if let Some(field_info) = field_info.as_ref() {
                    validate_parameter_field_shape(
                        py,
                        &name,
                        field_info.bind(py),
                        path_parameters,
                    )?;
                }
                let (example, openapi_examples) = parameter_openapi_examples(
                    py,
                    field_info.as_ref().map(|value| value.bind(py)),
                )?;
                Ok(CallableParameter {
                    name,
                    annotation: validated_annotation,
                    validation_adapter,
                    field_info: field_info
                        .as_ref()
                        .map(|value| value.clone_ref(py)),
                    required,
                    default,
                    default_delivery,
                    is_sequence,
                    parameter_model_fields,
                    parameter_model_config,
                    model_convert_underscores,
                    media_type: parameter_media_type(
                        &source,
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?,
                    title: parameter_title(
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?,
                    description: parameter_description(
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?,
                    deprecated: parameter_deprecated(
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?,
                    include_in_schema: parameter_include_in_schema(
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?,
                    body_embed: parameter_body_embed(
                        &source,
                        field_info.as_ref().map(|value| value.bind(py)),
                    )?,
                    example,
                    openapi_examples,
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
        let is_security_scheme = dependency_is_security_scheme(py, callable.bind(py))?;
        let mut plan = Self {
            callable,
            parameters,
            path_parameters: path_parameters.to_vec(),
            return_annotation,
            computed_scope,
            own_oauth_scopes: Vec::new(),
            oauth_scopes: Vec::new(),
            is_security_scheme,
        };
        plan.inherit_oauth_scopes(&[], &[])?;
        Ok(plan)
    }

    fn prepend_dependencies(&mut self, py: Python<'_>, dependencies: &[Py<PyAny>]) -> PyResult<()> {
        let mut parameters = Vec::with_capacity(dependencies.len() + self.parameters.len());
        for dependency in dependencies {
            let marker = dependency.bind(py);
            if is_dependency_record(py, marker)? && !marker.getattr("dependency")?.is_callable() {
                return Err(PyAssertionError::new_err(
                    "A parameter-less dependency must have a callable dependency",
                ));
            }
            let annotation = py.None();
            let source = parameter_source(
                py,
                "",
                annotation.bind(py),
                std::slice::from_ref(dependency),
                &self.path_parameters,
                false,
                None,
            )?;
            let ParameterSource::Dependency {
                mut plan,
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
            Arc::get_mut(&mut plan)
                .ok_or_else(|| {
                    PyRuntimeError::new_err(
                        "new dependency plan is shared during scope inheritance",
                    )
                })?
                .inherit_oauth_scopes(&self.oauth_scopes, &security_scopes)?;
            parameters.push(CallableParameter {
                name: String::new(),
                annotation,
                validation_adapter: None,
                field_info: None,
                required: false,
                default: None,
                default_delivery: ParameterDefaultDelivery::External,
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
                example: None,
                openapi_examples: None,
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
            let key = plan.dependency_cache_key();
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
                ParameterSource::SecurityScopes => false,
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
                | ParameterSource::SecurityScopes
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
                ParameterSource::SecurityScopes => false,
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
        security_schemes: &mut Vec<(String, Py<PyAny>)>,
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
                crate::openapi::register_security_scheme(
                    security_schemes,
                    scheme_name.clone(),
                    model,
                );
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
                            required: parameter.required,
                            annotation: parameter.annotation.clone_ref(py),
                            schema_config: None,
                            default: parameter.default.as_ref().map(|value| value.clone_ref(py)),
                            default_delivery: parameter.default_delivery,
                            title: parameter.title.clone(),
                            description: parameter.description.clone(),
                            deprecated: parameter.deprecated,
                            example: parameter.example.as_ref().map(|value| value.clone_ref(py)),
                            openapi_examples: parameter
                                .openapi_examples
                                .as_ref()
                                .map(|value| value.clone_ref(py)),
                        });
                    }
                }
                ParameterSource::Dependency { .. } => {}
                ParameterSource::Input { .. }
                | ParameterSource::WebSocket
                | ParameterSource::Request
                | ParameterSource::HttpConnection
                | ParameterSource::Response
                | ParameterSource::BackgroundTasks
                | ParameterSource::SecurityScopes => {}
            }
        }
        // FastAPI flattens each dependant's own parameter fields before
        // visiting its child dependencies. OpenAPI later resolves duplicate
        // (location, name) pairs with the last field taking precedence.
        for parameter in &self.parameters {
            if let ParameterSource::Dependency { plan, .. } = &parameter.source {
                parameters
                    .extend(plan.openapi_parameters_with_model_fields(py, flatten_model_sources)?);
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

    fn prepare_dependencies(
        &self,
        context: &mut InvocationContext<'_, '_>,
    ) -> PyResult<DependencyPreparation> {
        let dependency_count = self
            .parameters
            .iter()
            .filter(|parameter| matches!(&parameter.source, ParameterSource::Dependency { .. }))
            .count();
        // A completed graph already resolved every edge. Returning to endpoint
        // invocation must not reanalyze or truth-test those policies on resume.
        if dependency_count <= *context.dependency_override_cursor {
            return if context.failures.is_empty() {
                Ok(DependencyPreparation::Ready)
            } else {
                Ok(DependencyPreparation::Invalid)
            };
        }
        let mut graph = DependencyExecutionGraph::new(self, context.py);
        match graph.advance(context)? {
            DependencyGraphAdvance::Ready => Ok(DependencyPreparation::Ready),
            DependencyGraphAdvance::Invalid => Ok(DependencyPreparation::Invalid),
            DependencyGraphAdvance::Await(awaitable) => {
                Ok(DependencyPreparation::AwaitDependencyGraph {
                    awaitable,
                    graph: Box::new(graph),
                })
            }
        }
    }

    fn invoke(
        &self,
        context: &mut InvocationContext<'_, '_>,
        cache_policy: Option<&Py<PyAny>>,
        cache_key_override: Option<DependencyCacheKey>,
    ) -> PyResult<Option<Py<PyAny>>> {
        let Some(arguments) = self.prepare_arguments(context, None)? else {
            return Ok(None);
        };
        let cache_key = cache_key_override.unwrap_or_else(|| self.dependency_cache_key());
        // The source reads the policy once after successful recursive solving,
        // including when the request cache has no entry for this edge.
        if let Some(cache_policy) = cache_policy {
            if cache_policy.bind(context.py).is_truthy()? {
                if let Some(value) = context.dependency_cache.get(&cache_key) {
                    return Ok(Some(value.clone_ref(context.py)));
                }
            }
        }
        let result = self.call_with_arguments(context, arguments.bind(context.py), false)?;
        if cache_policy.is_some() && !context.dependency_cache.contains_key(&cache_key) {
            context
                .dependency_cache
                .insert(cache_key, result.clone_ref(context.py));
        }
        Ok(Some(result))
    }

    fn call_with_arguments(
        &self,
        context: &InvocationContext<'_, '_>,
        arguments: &Bound<'_, PyDict>,
        use_threadpool: bool,
    ) -> PyResult<Py<PyAny>> {
        if use_threadpool {
            context
                .py
                .import("starlette.concurrency")?
                .getattr("run_in_threadpool")?
                .call((self.callable.bind(context.py),), Some(arguments))
        } else {
            self.callable.bind(context.py).call((), Some(arguments))
        }
        .map(Bound::unbind)
    }

    fn prepare_arguments(
        &self,
        context: &mut InvocationContext<'_, '_>,
        prepared_dependencies: Option<&HashMap<usize, Py<PyAny>>>,
    ) -> PyResult<Option<Py<PyDict>>> {
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
                ParameterSource::SecurityScopes => {
                    let module = context.py.import("fastapi_rs._core")?;
                    let scopes = PyList::new(context.py, &self.oauth_scopes)?;
                    let arguments = PyDict::new(context.py);
                    arguments.set_item("scopes", scopes)?;
                    let value = module
                        .getattr("SecurityScopes")?
                        .call((), Some(&arguments))?;
                    kwargs.set_item(&parameter.name, value)?;
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
                let prepared_value = match prepared_dependencies {
                    Some(values) => values.get(&edge_index),
                    None => context.prepared_dependency_values.get(&edge_index),
                };
                if let Some(value) = prepared_value {
                    if *bind_value {
                        kwargs.set_item(&parameter.name, value.bind(context.py))?;
                    }
                    continue;
                }
                // An explicit map belongs to an already advanced graph. A
                // missing child failed validation and must not be reinvoked or
                // replaced by an unrelated endpoint-level prepared value.
                if prepared_dependencies.is_some() {
                    continue;
                }
                let original_cache_key = plan.dependency_cache_key();
                let reanalyzed_plan = plan.reanalyze_dependency(context, scope.as_deref())?;
                let dependency_plan = reanalyzed_plan.as_ref().unwrap_or(plan.as_ref());
                let value =
                    dependency_plan.invoke(context, Some(use_cache), Some(original_cache_key))?;
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
            let validation_adapter = parameter.validation_adapter.as_ref().ok_or_else(|| {
                PyRuntimeError::new_err("input validation adapter was not retained")
            })?;
            let validation_adapter = validation_adapter.bind(context.py);
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
            } else if source == InputSource::Header && parameter.is_sequence {
                let connection = context.request.or(context.websocket).ok_or_else(|| {
                    PyRuntimeError::new_err(
                        "header parameter requires an HTTP or WebSocket connection",
                    )
                })?;
                let header_values = connection
                    .getattr("headers")?
                    .call_method1("getlist", (alias,))?;
                if header_values.len()? == 0 {
                    None
                } else {
                    Some(header_values)
                }
            } else if source == InputSource::Header {
                let connection = context.request.or(context.websocket).ok_or_else(|| {
                    PyRuntimeError::new_err(
                        "header parameter requires an HTTP or WebSocket connection",
                    )
                })?;
                let header_value = connection
                    .getattr("headers")?
                    .call_method1("get", (alias,))?;
                if header_value.is_none() {
                    None
                } else {
                    Some(header_value)
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
            let value = value.filter(|value| !value.is_none());
            let Some(value) = value else {
                let mut default_from_validation = matches!(
                    source,
                    InputSource::Body | InputSource::Form | InputSource::File
                );
                let default = if parameter.required {
                    None
                } else {
                    let mut default = parameter_default_for_request(
                        context.py,
                        parameter.field_info.as_ref(),
                        parameter.default.as_ref(),
                        parameter.required,
                    )?;
                    if matches!(
                        source,
                        InputSource::Path
                            | InputSource::Query
                            | InputSource::Header
                            | InputSource::Cookie
                    ) {
                        // FastAPI reads field.default once while collecting the multi-dict,
                        // then reads it again while validating the collected value.
                        default = parameter_default_for_request(
                            context.py,
                            parameter.field_info.as_ref(),
                            parameter.default.as_ref(),
                            parameter.required,
                        )?;
                        if default
                            .as_ref()
                            .is_some_and(|value| value.bind(context.py).is_none())
                        {
                            // A missing None value is read once more by
                            // _validate_value_with_model_field.
                            default_from_validation = true;
                            default = parameter_default_for_request(
                                context.py,
                                parameter.field_info.as_ref(),
                                parameter.default.as_ref(),
                                parameter.required,
                            )?;
                        }
                    }
                    default
                };
                if let Some(default) = default {
                    if default_from_validation || default.bind(context.py).is_none() {
                        kwargs.set_item(&parameter.name, default.bind(context.py))?;
                    } else {
                        match validate_python_value(
                            context.py,
                            validation_adapter,
                            default.bind(context.py),
                        ) {
                            Ok(value) => kwargs.set_item(&parameter.name, value)?,
                            Err(error) if is_pydantic_validation_error(context.py, &error) => {
                                context.failures.push(ValidationIssue::Input(Box::new(
                                    InputValidationFailure {
                                        error,
                                        location: source.as_str().to_owned(),
                                        alias: alias.clone(),
                                        header_aliases: parameter_model_header_error_aliases(
                                            context.py,
                                            parameter,
                                            source,
                                            is_model_parameter,
                                        )?,
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
            match validate_python_value(context.py, validation_adapter, &value) {
                Ok(value) => kwargs.set_item(&parameter.name, value)?,
                Err(error) if is_pydantic_validation_error(context.py, &error) => {
                    context.failures.push(ValidationIssue::Input(Box::new(
                        InputValidationFailure {
                            error,
                            location: source.as_str().to_owned(),
                            alias: alias.clone(),
                            header_aliases: parameter_model_header_error_aliases(
                                context.py,
                                parameter,
                                source,
                                is_model_parameter,
                            )?,
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
        Ok(Some(kwargs.unbind()))
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

fn route_handler_exit_stack(
    py: Python<'_>,
    scope: &Bound<'_, PyAny>,
    key: &str,
) -> PyResult<Py<PyAny>> {
    if scope
        .call_method1("__contains__", (key,))?
        .extract::<bool>()?
    {
        return scope.get_item(key).map(Bound::unbind);
    }
    let stack = new_dependency_exit_stack(py)?;
    scope.set_item(key, stack.bind(py))?;
    Ok(stack)
}

fn route_handler_exit_stacks(
    py: Python<'_>,
    scope: &Bound<'_, PyAny>,
) -> PyResult<(Py<PyAny>, Py<PyAny>)> {
    let request_stack = route_handler_exit_stack(py, scope, FASTAPI_INNER_ASTACK_SCOPE_KEY)?;
    let function_stack = route_handler_exit_stack(py, scope, FASTAPI_FUNCTION_ASTACK_SCOPE_KEY)?;
    Ok((request_stack, function_stack))
}

fn reset_route_handler_exit_stacks(
    py: Python<'_>,
    scope: &Bound<'_, PyAny>,
) -> PyResult<(Py<PyAny>, Py<PyAny>)> {
    let request_stack = new_dependency_exit_stack(py)?;
    let function_stack = new_dependency_exit_stack(py)?;
    scope.set_item(FASTAPI_INNER_ASTACK_SCOPE_KEY, request_stack.bind(py))?;
    scope.set_item(FASTAPI_FUNCTION_ASTACK_SCOPE_KEY, function_stack.bind(py))?;
    Ok((request_stack, function_stack))
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

fn dependency_is_security_scheme(py: Python<'_>, callable: &Bound<'_, PyAny>) -> PyResult<bool> {
    let partial_type = py.import("functools")?.getattr("partial")?;
    let mut callable = callable.clone();
    while callable.is_instance(&partial_type)? {
        callable = callable.getattr("func")?;
    }
    let callable = py
        .import("inspect")?
        .getattr("unwrap")?
        .call1((callable,))?;
    let core = py.import("fastapi_rs._core")?;
    // Several native security classes have independent PyO3 bases. Their
    // exported identities still represent the source's SecurityBase hierarchy.
    for name in [
        "SecurityBase",
        "HTTPBase",
        "HTTPBasic",
        "HTTPBearer",
        "HTTPDigest",
        "OAuth2",
        "OAuth2PasswordBearer",
    ] {
        if callable.is_instance(&core.getattr(name)?)? {
            return Ok(true);
        }
    }
    Ok(false)
}

fn dependency_callable_without_partials<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let partial = py.import("functools")?.getattr("partial")?;
    let mut value = value.clone();
    while value.is_instance(&partial)? {
        value = value.getattr("func")?;
    }
    Ok(value)
}

fn dependency_callable_unwrapped<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    py.import("inspect")?
        .getattr("unwrap")?
        .call1((dependency_callable_without_partials(py, value)?,))
}

fn dependency_callable_call_method<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
) -> PyResult<Option<Bound<'py, PyAny>>> {
    match value.getattr("__call__") {
        Ok(method) if method.is_none() => Ok(None),
        Ok(method) => Ok(Some(method)),
        Err(error) if error.is_instance_of::<PyAttributeError>(py) => Ok(None),
        Err(error) => Err(error),
    }
}

fn dependency_override_callable(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
) -> PyResult<DependencyOverrideCallable> {
    let inspect = py.import("inspect")?;
    // FastAPI uses asyncio's predicate on pinned CPython 3.12, including its
    // legacy marker. Classification does not change the callable we invoke.
    let coroutine_predicate = py.import("asyncio")?.getattr("iscoroutinefunction")?;
    let is_coroutine = |callable: &Bound<'_, PyAny>| -> PyResult<bool> {
        coroutine_predicate.call1((callable,))?.extract()
    };
    let is_routine = |callable: &Bound<'_, PyAny>| -> PyResult<bool> {
        inspect.getattr("isroutine")?.call1((callable,))?.extract()
    };
    if is_routine(&dependency_callable_without_partials(py, value)?)?
        && is_coroutine(&dependency_callable_without_partials(py, value)?)?
    {
        return Ok(DependencyOverrideCallable::CoroutineFunction);
    }
    if is_routine(&dependency_callable_unwrapped(py, value)?)?
        && is_coroutine(&dependency_callable_unwrapped(py, value)?)?
    {
        return Ok(DependencyOverrideCallable::CoroutineFunction);
    }
    if inspect
        .getattr("isclass")?
        .call1((dependency_callable_unwrapped(py, value)?,))?
        .extract::<bool>()?
    {
        return Ok(DependencyOverrideCallable::Sync);
    }
    let impartial = dependency_callable_without_partials(py, value)?;
    let Some(call_method) = dependency_callable_call_method(py, &impartial)? else {
        return Ok(DependencyOverrideCallable::Sync);
    };
    if is_coroutine(&dependency_callable_without_partials(py, &call_method)?)?
        || is_coroutine(&dependency_callable_unwrapped(py, &call_method)?)?
        // Native async descriptors do not carry Python coroutine flags. Retain
        // the owned native bridge at this instance's method-classification step.
        || crate::security::is_native_async_callable(py, &impartial)?
    {
        return Ok(DependencyOverrideCallable::AsyncCallableInstance);
    }
    let unwrapped = dependency_callable_unwrapped(py, value)?;
    let Some(call_method) = dependency_callable_call_method(py, &unwrapped)? else {
        return Ok(DependencyOverrideCallable::Sync);
    };
    if is_coroutine(&dependency_callable_without_partials(py, &call_method)?)?
        || is_coroutine(&dependency_callable_unwrapped(py, &call_method)?)?
        || crate::security::is_native_async_callable(py, &unwrapped)?
    {
        return Ok(DependencyOverrideCallable::AsyncCallableInstance);
    }
    Ok(DependencyOverrideCallable::Sync)
}

fn dependency_callable_matches_generator_predicate(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
    predicate_name: &str,
) -> PyResult<bool> {
    let inspect = py.import("inspect")?;
    let predicate = inspect.getattr(predicate_name)?;
    let matches =
        |callable: &Bound<'_, PyAny>| -> PyResult<bool> { predicate.call1((callable,))?.extract() };
    if matches(&dependency_callable_without_partials(py, value)?)?
        || matches(&dependency_callable_unwrapped(py, value)?)?
    {
        return Ok(true);
    }
    if inspect
        .getattr("isclass")?
        .call1((dependency_callable_unwrapped(py, value)?,))?
        .extract::<bool>()?
    {
        return Ok(false);
    }
    let impartial = dependency_callable_without_partials(py, value)?;
    let Some(call_method) = dependency_callable_call_method(py, &impartial)? else {
        return Ok(false);
    };
    if matches(&dependency_callable_without_partials(py, &call_method)?)?
        || matches(&dependency_callable_unwrapped(py, &call_method)?)?
    {
        return Ok(true);
    }
    let unwrapped = dependency_callable_unwrapped(py, value)?;
    let Some(call_method) = dependency_callable_call_method(py, &unwrapped)? else {
        return Ok(false);
    };
    Ok(
        matches(&dependency_callable_without_partials(py, &call_method)?)?
            || matches(&dependency_callable_unwrapped(py, &call_method)?)?,
    )
}

fn dependency_callable_is_generator(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    // Source scope analysis and the miss branch test sync before async.
    Ok(
        dependency_callable_matches_generator_predicate(py, value, "isgeneratorfunction")?
            || dependency_callable_matches_generator_predicate(py, value, "isasyncgenfunction")?,
    )
}

fn dependency_callable_generator_kind(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
) -> PyResult<Option<DependencyGeneratorKind>> {
    if !dependency_callable_is_generator(py, value)? {
        return Ok(None);
    }
    // Once source enters _solve_generator, an async generator wins even when
    // unwrapping also identifies an underlying sync generator.
    if dependency_callable_matches_generator_predicate(py, value, "isasyncgenfunction")? {
        return Ok(Some(DependencyGeneratorKind::Async));
    }
    if dependency_callable_matches_generator_predicate(py, value, "isgeneratorfunction")? {
        return Ok(Some(DependencyGeneratorKind::Sync));
    }
    Ok(None)
}

fn parameter_marker_kind(py: Python<'_>, marker: &Bound<'_, PyAny>) -> PyResult<Option<String>> {
    if is_dependency_record(py, marker)? {
        return Ok(None);
    }
    let core = py.import("fastapi_rs._core")?;
    for (class_name, kind) in [
        ("ParamsFile", "file"),
        ("ParamsForm", "form"),
        ("ParamsBody", "body"),
    ] {
        let class = core.getattr(class_name)?;
        if marker.is_instance(&class)? {
            return Ok(Some(kind.to_owned()));
        }
    }
    let parameter = core.getattr("ParamsParam")?;
    if !marker.is_instance(&parameter)? {
        return Ok(None);
    }
    if !marker.hasattr("in_")? {
        return Ok(Some("query".to_owned()));
    }
    let location = marker.getattr("in_")?;
    if location.is_none() {
        return Ok(Some("query".to_owned()));
    }
    location.getattr("value")?.extract().map(Some)
}

fn is_pydantic_field_info(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    value.is_instance(&py.import("pydantic.fields")?.getattr("FieldInfo")?)
}

fn copy_annotated_field_info(
    py: Python<'_>,
    marker: &Bound<'_, PyAny>,
    full_annotation: &Bound<'_, PyAny>,
    signature_default: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let merged = marker
        .get_type()
        .call_method1("from_annotation", (full_annotation,))?;
    let copied = py.import("copy")?.call_method1("copy", (marker,))?;
    copied.setattr("metadata", merged.getattr("metadata")?)?;
    copied.setattr("annotation", merged.getattr("annotation")?)?;
    let default = match signature_default {
        Some(default) => default.clone(),
        None => py.import("pydantic_core")?.getattr("PydanticUndefined")?,
    };
    copied.setattr("default", default)?;
    Ok(copied.unbind())
}

fn compose_parameter_annotation(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    metadata: &[Py<PyAny>],
) -> PyResult<Py<PyAny>> {
    if metadata.is_empty() {
        return Ok(annotation.clone().unbind());
    }
    let arguments = PyList::empty(py);
    arguments.append(annotation)?;
    for item in metadata {
        arguments.append(item.bind(py))?;
    }
    let tuple = py
        .import("builtins")?
        .getattr("tuple")?
        .call1((arguments,))?;
    py.import("typing")?
        .getattr("Annotated")?
        .get_item(tuple)
        .map(Bound::unbind)
}

fn inferred_parameter_field_info(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    raw_default: &Bound<'_, PyAny>,
    empty: &Bound<'_, PyAny>,
    is_path_parameter: bool,
) -> PyResult<Py<PyAny>> {
    let (class_name, default) = if is_path_parameter {
        ("ParamsPath", py.import("builtins")?.getattr("Ellipsis")?)
    } else if is_uploadfile_annotation(py, annotation)?
        || is_uploadfile_sequence_annotation(py, annotation)?
    {
        (
            "ParamsFile",
            if raw_default.is(empty) {
                py.import("pydantic_core")?.getattr("PydanticUndefined")?
            } else {
                raw_default.clone()
            },
        )
    } else if field_annotation_is_complex(py, annotation)? {
        (
            "ParamsBody",
            if raw_default.is(empty) {
                py.import("pydantic_core")?.getattr("PydanticUndefined")?
            } else {
                raw_default.clone()
            },
        )
    } else {
        (
            "ParamsQuery",
            if raw_default.is(empty) {
                py.import("pydantic_core")?.getattr("PydanticUndefined")?
            } else {
                raw_default.clone()
            },
        )
    };
    let class = py.import("fastapi_rs._core")?.getattr(class_name)?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("annotation", annotation)?;
    kwargs.set_item("default", default)?;
    class.call((), Some(&kwargs)).map(Bound::unbind)
}

fn parameter_field_info_defaults(
    py: Python<'_>,
    field_info: &Bound<'_, PyAny>,
) -> PyResult<(bool, Option<Py<PyAny>>)> {
    let required = field_info.call_method0("is_required")?.extract::<bool>()?;
    if required {
        return Ok((true, None));
    }
    let default = field_info.getattr("default")?;
    let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
    let default = if default.is(&undefined) {
        None
    } else {
        Some(default.unbind())
    };
    Ok((false, default))
}

fn validate_parameter_field_shape(
    py: Python<'_>,
    name: &str,
    field_info: &Bound<'_, PyAny>,
    path_parameters: &[String],
) -> PyResult<()> {
    let annotation = field_info.getattr("annotation")?;
    if path_parameters.iter().any(|path_name| path_name == name) {
        let body_type = py.import("fastapi_rs._core")?.getattr("ParamsBody")?;
        if field_info.is_instance(&body_type)? || !field_annotation_is_scalar(py, &annotation)? {
            return Err(PyAssertionError::new_err(
                "Path params must be of one of the supported types",
            ));
        }
    }

    let query_type = py.import("fastapi_rs._core")?.getattr("ParamsQuery")?;
    if field_info.is_instance(&query_type)?
        && !field_annotation_is_scalar(py, &annotation)?
        && !field_annotation_is_scalar_sequence(py, &annotation)?
        && !is_pydantic_model(py, &annotation)?
    {
        let parameter_name = PyString::new(py, name).repr()?;
        return Err(PyAssertionError::new_err(format!(
            "Query parameter {} must be one of the supported types",
            parameter_name.to_string_lossy()
        )));
    }
    Ok(())
}

fn parameter_default_for_request(
    py: Python<'_>,
    field_info: Option<&Py<PyAny>>,
    default: Option<&Py<PyAny>>,
    required: bool,
) -> PyResult<Option<Py<PyAny>>> {
    if required {
        return Ok(None);
    }
    let value = if let Some(field_info) = field_info {
        let kwargs = PyDict::new(py);
        kwargs.set_item("call_default_factory", true)?;
        field_info
            .bind(py)
            .call_method("get_default", (), Some(&kwargs))?
            .unbind()
    } else if let Some(default) = default {
        default.clone_ref(py)
    } else {
        return Ok(None);
    };
    py.import("copy")?
        .call_method1("deepcopy", (value.bind(py),))
        .map(Bound::unbind)
        .map(Some)
}

#[derive(Clone, Copy)]
enum AnnotatedParameterMarker {
    Dependency(usize),
    Field(usize),
}

fn annotated_parameter_marker(
    py: Python<'_>,
    metadata: &[Py<PyAny>],
) -> PyResult<Option<AnnotatedParameterMarker>> {
    for (index, marker) in metadata.iter().enumerate().rev() {
        let marker = marker.bind(py);
        if is_dependency_record(py, marker)? {
            return Ok(Some(AnnotatedParameterMarker::Dependency(index)));
        }
        if matches!(
            parameter_marker_kind(py, marker)?.as_deref(),
            Some("body" | "path" | "query" | "header" | "cookie" | "form" | "file")
        ) {
            return Ok(Some(AnnotatedParameterMarker::Field(index)));
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
                let model_values = form_union_values(
                    py,
                    form,
                    alias,
                    self.field_info.as_ref(),
                    self.default.as_ref(),
                    self.required,
                    self.is_sequence,
                )?;
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
        let value = match value {
            Some(value)
                if !self.is_sequence
                    && value.is_instance_of::<PyString>()
                    && value.extract::<String>()?.is_empty() =>
            {
                None
            }
            value => value,
        };
        if let Some(value) = value {
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
        } else if !self.required {
            if let Some(default) = parameter_default_for_request(
                py,
                self.field_info.as_ref(),
                self.default.as_ref(),
                self.required,
            )? {
                if !default.bind(py).is_none() {
                    inputs.set_item(&self.name, default.bind(py))?;
                }
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
                required: self.required,
            }],
            ParameterSource::Dependency { plan, .. } => plan.input_parameters(),
            ParameterSource::WebSocket
            | ParameterSource::Request
            | ParameterSource::HttpConnection
            | ParameterSource::Response
            | ParameterSource::BackgroundTasks
            | ParameterSource::SecurityScopes => Vec::new(),
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
    header_aliases: Vec<(String, String)>,
    include_parameter_alias: bool,
    body_field: bool,
}

fn annotation_parts(
    py: Python<'_>,
    annotation: Py<PyAny>,
) -> PyResult<(Py<PyAny>, Vec<Py<PyAny>>)> {
    let typing = py.import("typing")?;
    let is_type_alias = annotation
        .bind(py)
        .is_instance(&typing.getattr("TypeAliasType")?)?
        || annotation
            .bind(py)
            .is_instance(&py.import("typing_extensions")?.getattr("TypeAliasType")?)?;
    // Source parameter analysis unpacks one alias before selecting Annotated metadata.
    let annotation = if is_type_alias {
        annotation.bind(py).getattr("__value__")?.unbind()
    } else {
        annotation
    };
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
    bind_value: bool,
    field_info: Option<&Bound<'_, PyAny>>,
) -> PyResult<ParameterSource> {
    // Explicit Depends takes precedence over framework-managed parameter injection.
    for marker in metadata {
        let marker = marker.bind(py);
        if !is_dependency_record(py, marker)? {
            continue;
        }
        let dependency = marker.getattr("dependency")?;
        let dependency = if dependency.is_none() {
            // Inference belongs to the analyzed plan; the frozen source record can be reused.
            annotation.clone().unbind()
        } else {
            dependency.unbind()
        };
        if bind_value && !dependency.bind(py).is_truthy()? {
            return Err(PyAssertionError::new_err(""));
        }
        let use_cache = if bind_value {
            marker.getattr("use_cache")?.unbind()
        } else {
            PyBool::new(py, true).to_owned().unbind().into_any()
        };
        let scope = marker.getattr("scope")?.extract::<Option<String>>()?;
        let mut security_scopes = Vec::new();
        if is_security_record(py, marker)? {
            let marker_scopes = marker.getattr("scopes")?;
            if marker_scopes.is_truthy()? {
                security_scopes = marker_scopes
                    .try_iter()?
                    .map(|scope| scope?.extract::<String>())
                    .collect::<PyResult<Vec<_>>>()?;
            }
        }
        let path_names = path_parameters.to_vec();
        return CallablePlan::build(py, dependency, &path_names, scope.clone()).map(|plan| {
            ParameterSource::Dependency {
                plan: Arc::new(plan),
                use_cache,
                scope,
                security_scopes,
                bind_value,
            }
        });
    }
    let request_type = py.import("starlette.requests")?.getattr("Request")?;
    let websocket_type = py.import("starlette.websockets")?.getattr("WebSocket")?;
    let connection_type = py.import("starlette.requests")?.getattr("HTTPConnection")?;
    let response_type = py.import("starlette.responses")?.getattr("Response")?;
    let background_tasks_type = py
        .import("starlette.background")?
        .getattr("BackgroundTasks")?;
    let security_scopes_type = py.import("fastapi_rs._core")?.getattr("SecurityScopes")?;
    let injected_source = if annotation_is_subclass(py, annotation, &request_type)? {
        Some(ParameterSource::Request)
    } else if annotation_is_subclass(py, annotation, &websocket_type)? {
        Some(ParameterSource::WebSocket)
    } else if annotation_is_subclass(py, annotation, &connection_type)? {
        Some(ParameterSource::HttpConnection)
    } else if annotation_is_subclass(py, annotation, &response_type)? {
        Some(ParameterSource::Response)
    } else if annotation_is_subclass(py, annotation, &background_tasks_type)? {
        Some(ParameterSource::BackgroundTasks)
    } else if annotation_is_subclass(py, annotation, &security_scopes_type)? {
        Some(ParameterSource::SecurityScopes)
    } else {
        None
    };
    if let Some(source) = injected_source {
        if field_info.is_some() {
            let annotation = annotation.repr()?.to_string_lossy().into_owned();
            return Err(PyAssertionError::new_err(format!(
                "Cannot specify FastAPI annotation for type {annotation}"
            )));
        }
        return Ok(source);
    }
    if let Some(field_info) = field_info {
        let core = py.import("fastapi_rs._core")?;
        if path_parameters.iter().any(|path_name| path_name == name)
            && !field_info.is_instance(&core.getattr("ParamsPath")?)?
        {
            let class_name = field_info
                .get_type()
                .getattr("__name__")?
                .extract::<String>()?;
            let parameter_name = PyString::new(py, name).repr()?;
            return Err(PyAssertionError::new_err(format!(
                "Cannot use `{class_name}` for path param {}",
                parameter_name.to_string_lossy()
            )));
        }
        let mut kind = parameter_marker_kind(py, field_info)?;
        if kind.is_none() {
            return Err(PyAssertionError::new_err(format!(
                "non-body parameters must be in path, query, header or cookie: {name}"
            )));
        }
        if matches!(
            kind.as_deref(),
            Some("query" | "header" | "path" | "cookie")
        ) && (!field_info.hasattr("in_")? || field_info.getattr("in_")?.is_none())
        {
            let query_location = core.getattr("ParamsParamTypes")?.getattr("query")?;
            field_info.setattr("in_", query_location)?;
            kind = Some("query".to_owned());
        }
        let Some(kind) = kind else {
            return Err(PyAssertionError::new_err(format!(
                "non-body parameters must be in path, query, header or cookie: {name}"
            )));
        };
        let declared_alias = field_info.getattr("alias")?;
        let alias_is_truthy = declared_alias.is_truthy()?;
        let convert_underscores = if field_info.hasattr("convert_underscores")? {
            field_info.getattr("convert_underscores")?.is_truthy()?
        } else {
            false
        };
        let alias = if alias_is_truthy {
            declared_alias
        } else if kind == "header" && convert_underscores {
            PyString::new(py, &name.replace('_', "-")).into_any()
        } else {
            PyString::new(py, name).into_any()
        };
        field_info.setattr("alias", &alias)?;
        let validation_alias = field_info.getattr("validation_alias")?;
        let alias = if validation_alias.is_instance_of::<PyString>()
            && !validation_alias.extract::<String>()?.is_empty()
        {
            validation_alias.extract::<String>()?
        } else {
            alias.extract::<String>()?
        };
        if kind == "body" {
            return Ok(ParameterSource::Input {
                source: InputSource::Body,
                alias,
            });
        }
        if kind == "form" || kind == "file" {
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
                alias,
            });
        }
        if kind == "header" || kind == "query" || kind == "cookie" {
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

/// Mirrors FastAPI's `field_annotation_is_scalar` classification.
fn field_annotation_is_scalar(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    if annotation.is(&py.import("builtins")?.getattr("Ellipsis")?) {
        return Ok(true);
    }
    Ok(!field_annotation_is_complex(py, annotation)?)
}

/// Mirrors FastAPI's `field_annotation_is_scalar_sequence` query-field rule.
fn field_annotation_is_scalar_sequence(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    if origin.is(&typing.getattr("Annotated")?) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        return field_annotation_is_scalar_sequence(py, &arguments.get_item(0)?);
    }

    let types = py.import("types")?;
    let union = typing.getattr("Union")?;
    let union_type = types.getattr("UnionType")?;
    if origin.is(&union) || origin.is(&union_type) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        let mut found_scalar_sequence = false;
        for argument in arguments.iter() {
            if field_annotation_is_scalar_sequence(py, &argument)? {
                found_scalar_sequence = true;
            } else if !field_annotation_is_scalar(py, &argument)? {
                return Ok(false);
            }
        }
        return Ok(found_scalar_sequence);
    }

    if !field_annotation_is_sequence(py, annotation)? {
        return Ok(false);
    }
    for argument in typing
        .getattr("get_args")?
        .call1((annotation,))?
        .try_iter()?
    {
        if !field_annotation_is_scalar(py, &argument?)? {
            return Ok(false);
        }
    }
    Ok(true)
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
    source: &ParameterSource,
    field_info: Option<&Bound<'_, PyAny>>,
) -> PyResult<Option<String>> {
    match source {
        ParameterSource::Input {
            source: InputSource::Body | InputSource::Form | InputSource::File,
            ..
        } => field_info
            .map(|field_info| {
                field_info
                    .getattr("media_type")?
                    .extract::<Option<String>>()
            })
            .transpose()
            .map(Option::flatten),
        _ => Ok(None),
    }
}

fn parameter_description(field_info: Option<&Bound<'_, PyAny>>) -> PyResult<Option<String>> {
    field_info
        .map(|field_info| {
            field_info
                .getattr("description")?
                .extract::<Option<String>>()
        })
        .transpose()
        .map(Option::flatten)
}

fn parameter_title(field_info: Option<&Bound<'_, PyAny>>) -> PyResult<Option<String>> {
    field_info
        .map(|field_info| field_info.getattr("title")?.extract::<Option<String>>())
        .transpose()
        .map(Option::flatten)
}

fn parameter_deprecated(field_info: Option<&Bound<'_, PyAny>>) -> PyResult<bool> {
    match field_info {
        Some(field_info) if field_info.hasattr("deprecated")? => {
            field_info.getattr("deprecated")?.is_truthy()
        }
        _ => Ok(false),
    }
}

fn parameter_include_in_schema(field_info: Option<&Bound<'_, PyAny>>) -> PyResult<bool> {
    match field_info {
        Some(field_info) if field_info.hasattr("include_in_schema")? => {
            field_info.getattr("include_in_schema")?.extract::<bool>()
        }
        _ => Ok(true),
    }
}

fn parameter_body_embed(
    source: &ParameterSource,
    field_info: Option<&Bound<'_, PyAny>>,
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
    if let Some(field_info) = field_info {
        if field_info.hasattr("embed")? {
            return field_info.getattr("embed")?.is_truthy();
        }
    }
    Ok(false)
}

fn parameter_openapi_examples(
    py: Python<'_>,
    field_info: Option<&Bound<'_, PyAny>>,
) -> PyResult<ParameterOpenApiExamples> {
    let Some(field_info) = field_info else {
        return Ok((None, None));
    };
    let openapi_examples = if field_info.hasattr("openapi_examples")? {
        let examples = field_info.getattr("openapi_examples")?;
        (!examples.is_none()).then(|| examples.unbind())
    } else {
        None
    };
    let example = if field_info.hasattr("example")? {
        let example = field_info.getattr("example")?;
        let unset = py.import("fastapi_rs._core")?.getattr("_Unset")?;
        (!example.is(&unset)).then(|| example.unbind())
    } else {
        None
    };
    Ok((example, openapi_examples))
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

fn typed_parameter_annotation(
    py: Python<'_>,
    callable: &Bound<'_, PyAny>,
    annotation: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let Ok(annotation_string) = annotation.cast::<PyString>() else {
        return Ok(annotation.clone().unbind());
    };
    // Resolve the signature's expression itself. Looking up this parameter in
    // __annotations__ can replace a changed __signature__ with stale types.
    let unwrapped = py
        .import("inspect")?
        .getattr("unwrap")?
        .call1((callable,))?;
    let globalns = match unwrapped.getattr("__globals__") {
        Ok(globalns) => globalns,
        Err(error) if error.is_instance_of::<PyAttributeError>(py) => PyDict::new(py).into_any(),
        Err(error) => return Err(error),
    };
    let forward_ref = py
        .import("typing")?
        .getattr("ForwardRef")?
        .call1((annotation_string,))?;
    let evaluated = py
        .import("pydantic._internal._typing_extra")?
        .getattr("try_eval_type")?
        .call1((forward_ref, &globalns, &globalns))?
        .get_item(0)?;
    let none = py.None();
    if evaluated.is(none.bind(py).get_type()) {
        Ok(none)
    } else {
        Ok(evaluated.unbind())
    }
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
    methods: &[String],
    name: &str,
) -> PyResult<(Py<PyAny>, String)> {
    let route_type = py.import("starlette.routing")?.getattr("Route")?;
    let method_names = PyList::new(py, methods.iter().map(String::as_str))?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("methods", method_names)?;
    kwargs.set_item("name", name)?;
    let route = route_type.call((path, endpoint), Some(&kwargs))?;
    let path_format = route.getattr("path_format")?.extract::<String>()?;
    route.setattr(
        "methods",
        PySet::new(py, methods.iter().map(String::as_str))?,
    )?;
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
    app.route_surface.bind(py).append(route_scope.bind(py))?;
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

fn register_constructor_websocket_routes(app: &mut PyFastApi, py: Python<'_>) -> PyResult<()> {
    let route_type = py.import("starlette.routing")?.getattr("WebSocketRoute")?;
    let is_instance = py.import("builtins")?.getattr("isinstance")?;
    let constructor_routes = app
        .constructor_routes
        .iter()
        .map(|route| route.clone_ref(py))
        .collect::<Vec<_>>();
    for route in constructor_routes {
        if !is_instance
            .call1((route.bind(py), &route_type))?
            .is_truthy()?
        {
            continue;
        }
        let route = route.bind(py);
        let path = route.getattr("path")?.extract::<String>()?;
        let endpoint = route.getattr("endpoint")?;
        let name = route.getattr("name")?.extract::<String>()?;
        add_raw_websocket_route(app, py, &path, &endpoint, Some(&name))?;
    }
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

fn route_path_regex(py: Python<'_>, path: &str) -> PyResult<Py<PyAny>> {
    py.import("starlette.routing")?
        .getattr("compile_path")?
        .call1((path,))?
        .get_item(0)
        .map(Bound::unbind)
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
    for parameter in body_parameters {
        let field_info = parameter
            .field_info
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("body parameter lost its FieldInfo"))?
            .bind(py);
        let annotation = field_info.getattr("annotation")?;
        fields.set_item(&parameter.name, (annotation, field_info))?;
    }
    py.import("pydantic")?
        .getattr("create_model")?
        .call((model_name,), Some(&fields))
        .map(Bound::unbind)
}

fn request_schema_from_batch(
    py: Python<'_>,
    route: &OpenApiRouteSnapshot,
    response_schemas: &ResponseFieldSchemaBatch,
    title: Option<&str>,
) -> PyResult<Py<PyAny>> {
    let key = route
        .request_schema_key
        .ok_or_else(|| PyRuntimeError::new_err("OpenAPI request schema field was not collected"))?;
    response_schemas.validation_schema(py, key, title)
}

fn pydantic_parameter_schema(
    py: Python<'_>,
    parameter: &ParameterOpenApiPlan,
    fallback_title: &str,
) -> PyResult<Py<PyAny>> {
    let annotation = match parameter.default_delivery {
        ParameterDefaultDelivery::External => {
            if let Some(default) = parameter.default.as_ref() {
                // Source's outer Field clears an inherited factory while delivering
                // the static default, including an actual Python None.
                let kwargs = PyDict::new(py);
                kwargs.set_item("default", default.bind(py))?;
                kwargs.set_item("default_factory", py.None())?;
                let field = py
                    .import("pydantic")?
                    .getattr("Field")?
                    .call((), Some(&kwargs))?;
                let arguments = PyTuple::new(py, [parameter.annotation.bind(py).clone(), field])?;
                py.import("typing")?
                    .getattr("Annotated")?
                    .call_method1("__class_getitem__", (arguments,))?
                    .unbind()
            } else {
                parameter.annotation.clone_ref(py)
            }
        }
        ParameterDefaultDelivery::InAnnotation => parameter.annotation.clone_ref(py),
    };
    let schema = pydantic_schema_with_config(
        py,
        annotation.bind(py),
        "validation",
        None,
        parameter
            .schema_config
            .as_ref()
            .map(|config| config.bind(py)),
    )?;
    let schema_dictionary = schema.bind(py).cast::<PyDict>()?;
    if schema_dictionary.get_item("$ref")?.is_none() {
        // Source assigns the outer title after Pydantic encodes the default.
        let title = parameter
            .title
            .as_deref()
            .filter(|title| !title.is_empty())
            .unwrap_or(fallback_title);
        schema_dictionary.set_item("title", title)?;
    }
    Ok(schema)
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
    pydantic_schema_from_adapter(py, &adapter, mode, title)
}

fn pydantic_response_schema(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    separate_input_output_schemas: bool,
    title: Option<&str>,
) -> PyResult<Py<PyAny>> {
    let adapter = py
        .import("pydantic")?
        .getattr("TypeAdapter")?
        .call1((annotation,))?;
    let core_schema = adapter.getattr("core_schema")?;
    let mut has_computed_fields = false;
    if let Ok(core_schema) = core_schema.cast::<PyDict>() {
        if let Some(schema) = core_schema.get_item("schema")? {
            if let Ok(schema) = schema.cast::<PyDict>() {
                if let Some(fields) = schema.get_item("computed_fields")? {
                    has_computed_fields = fields.len()? > 0;
                }
            }
        }
    }
    let mode = if separate_input_output_schemas || has_computed_fields {
        "serialization"
    } else {
        "validation"
    };
    pydantic_schema_from_adapter(py, &adapter, mode, title)
}

fn pydantic_schema_from_adapter(
    py: Python<'_>,
    adapter: &Bound<'_, PyAny>,
    mode: &str,
    title: Option<&str>,
) -> PyResult<Py<PyAny>> {
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

fn build_python_value_adapter(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let warnings = py.import("warnings")?;
    let warning_context = warnings.call_method0("catch_warnings")?;
    warning_context.call_method0("__enter__")?;
    let result = (|| {
        let unsupported_field_attribute = py
            .import("pydantic.warnings")?
            .getattr("UnsupportedFieldAttributeWarning")?;
        warnings.call_method1("simplefilter", ("ignore", unsupported_field_attribute))?;
        py.import("pydantic")?
            .getattr("TypeAdapter")?
            .call1((annotation,))
            .map(Bound::unbind)
    })();
    let context_exit = warning_context.call_method1("__exit__", (py.None(), py.None(), py.None()));
    match (result, context_exit) {
        (Ok(adapter), Ok(_)) => Ok(adapter),
        (Err(error), _) => Err(error),
        (_, Err(error)) => Err(error),
    }
}

fn validate_python_value(
    py: Python<'_>,
    adapter: &Bound<'_, PyAny>,
    value: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let kwargs = PyDict::new(py);
    kwargs.set_item("from_attributes", true)?;
    adapter
        .call_method("validate_python", (value,), Some(&kwargs))
        .map(Bound::unbind)
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
    let annotated = typing.getattr("Annotated")?;
    if origin.is(&annotated) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        return is_bytes_annotation(py, &arguments.get_item(0)?);
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
    let annotated = typing.getattr("Annotated")?;
    if origin.is(&annotated) {
        let arguments = typing
            .getattr("get_args")?
            .call1((annotation,))?
            .cast_into::<PyTuple>()?;
        return is_bytes_sequence_annotation(py, &arguments.get_item(0)?);
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
    let mut normalized_annotation = annotation.clone().unbind();
    loop {
        let (base, metadata) = annotation_parts(py, normalized_annotation)?;
        normalized_annotation = base;
        if metadata.is_empty() {
            break;
        }
    }
    let annotation = normalized_annotation.bind(py);
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

fn header_model_convert_underscores(field_info: Option<&Bound<'_, PyAny>>) -> PyResult<bool> {
    match field_info {
        Some(field_info) if field_info.hasattr("convert_underscores")? => {
            field_info.getattr("convert_underscores")?.extract::<bool>()
        }
        _ => Ok(true),
    }
}

fn parameter_model_header_error_aliases(
    py: Python<'_>,
    parameter: &CallableParameter,
    source: InputSource,
    is_model_parameter: bool,
) -> PyResult<Vec<(String, String)>> {
    if source != InputSource::Header || !is_model_parameter {
        return Ok(Vec::new());
    }

    let loc_by_alias = if let Some(config) = parameter.parameter_model_config.as_ref() {
        config
            .bind(py)
            .cast::<PyDict>()?
            .get_item("loc_by_alias")?
            .map(|value| value.extract::<bool>())
            .transpose()?
            .unwrap_or(true)
    } else {
        true
    };
    if !loc_by_alias {
        return Ok(Vec::new());
    }

    let model_convert_underscores = parameter.model_convert_underscores.unwrap_or(true);
    let Some(fields) = parameter.parameter_model_fields.as_ref() else {
        return Ok(Vec::new());
    };
    Ok(fields
        .iter()
        .filter_map(|field| {
            let convert_underscores = field
                .convert_underscores
                .unwrap_or(model_convert_underscores);
            if convert_underscores && field.alias == field.name {
                let request_alias = field.alias.replace('_', "-");
                (request_alias != field.alias).then(|| (field.alias.clone(), request_alias))
            } else {
                None
            }
        })
        .collect())
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
    let annotation = pydantic_field_schema_annotation(py, field_info)?;
    let (example, openapi_examples) = parameter_openapi_examples(py, Some(field_info))?;
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
        default: None,
        default_delivery: ParameterDefaultDelivery::InAnnotation,
        title: Some(title),
        description,
        deprecated,
        example,
        openapi_examples,
    }))
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
    field_info: Option<&Py<PyAny>>,
    default: Option<&Py<PyAny>>,
    required: bool,
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
        value = parameter_default_for_request(py, field_info, default, required)?
            .map(|default| default.bind(py).clone());
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
            let mut first_field_path = true;
            for part in field_loc.try_iter()? {
                let part = part?;
                if first_field_path {
                    first_field_path = false;
                    if let Ok(field_alias) = part.extract::<String>() {
                        if let Some((_, request_alias)) = failure
                            .header_aliases
                            .iter()
                            .find(|(alias, _)| alias == &field_alias)
                        {
                            loc.append(request_alias.as_str())?;
                            continue;
                        }
                    }
                }
                loc.append(part)?;
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

struct DecodedInputValues {
    values: Py<PyDict>,
    request_body: Option<Py<PyAny>>,
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
) -> Result<DecodedInputValues, InputDecodeError> {
    let values = PyDict::new(py);
    let mut request_body = None;
    for input in request.inputs {
        let Some(value) = input.value else {
            continue;
        };
        if input.location == FastApiInputLocation::Body && value.is_empty() {
            continue;
        }
        let value = match input.location {
            FastApiInputLocation::Body if parse_json_body => {
                #[cfg(feature = "fault-injection")]
                if crate::fault_injection::take_http_request_json_decode_before() {
                    return Err(InputDecodeError::BodyParse(PyRuntimeError::new_err(
                        "Fault injected at http.request.json_decode.before",
                    )));
                }
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
        let value = value.unbind();
        if input.location == FastApiInputLocation::Body && request_body.is_none() {
            request_body = Some(value.clone_ref(py));
        }
        values
            .set_item(input.name, value.bind(py))
            .map_err(InputDecodeError::Other)?;
    }
    Ok(DecodedInputValues {
        values: values.unbind(),
        request_body,
    })
}

fn response_start(
    py: Python<'_>,
    send: &Bound<'_, PyAny>,
    status: u16,
    body: &[u8],
    extra_headers: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let headers = PyList::empty(py);
    // FastAPI clears 205's body after response construction, so its original
    // serialized length remains. Starlette omits this header for 204 and 304.
    if status >= 200 && !matches!(status, 204 | 304) {
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

fn response_status_override(status_code: Option<u16>) -> Option<u16> {
    status_code.filter(|status_code| *status_code != 0)
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
            context.set_item("file", &source_file)?;
        }
        let line = match plain_function_source_line(py, endpoint, &source_file)? {
            Some(line) => line,
            None => inspect
                .getattr("getsourcelines")?
                .call1((endpoint,))?
                .get_item(1)?,
        };
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

fn plain_function_source_line<'py>(
    py: Python<'py>,
    endpoint: &Bound<'py, PyAny>,
    source_file: &Bound<'py, PyAny>,
) -> PyResult<Option<Bound<'py, PyAny>>> {
    if source_file.is_none() {
        return Ok(None);
    }

    let function_type = py.import("types")?.getattr("FunctionType")?;
    if !endpoint.is_instance(&function_type)? {
        return Ok(None);
    }
    let function_namespace = endpoint.getattr("__dict__")?.cast_into::<PyDict>()?;
    if function_namespace.contains("__wrapped__")? {
        return Ok(None);
    }

    let Ok(source_filename) = source_file.extract::<String>() else {
        return Ok(None);
    };
    if !Path::new(&source_filename).is_file() {
        return Ok(None);
    }

    let code = endpoint.getattr("__code__")?;
    let code_filename = code.getattr("co_filename")?.extract::<String>()?;
    if code_filename != source_filename {
        return Ok(None);
    }

    code.getattr("co_firstlineno").map(Some)
}

enum PendingAction {
    RequestBody,
    FormParse,
    FormFileRead,
    LifespanCompletion,
    WebSocketEndpoint,
    WebSocketClose,
    WebSocketExceptionHandler,
    WebSocketExceptionResponse,
    MountedApp,
    FrontendConfig,
    FrontendResponse,
    FrontendAsgiResponse,
    RouteInvocation,
    Endpoint,
    SseStreamSetup,
    CustomRouteHandler,
    RouteHandlerFunctionCleanupBeforeResponse,
    RouteHandlerRequestCleanupAfterResponse,
    RouteHandlerCleanupAfterError(PyErr),
    ResponseValidation(Box<ResponseValidationState>),
    DependencyGraph(Box<DependencyExecutionGraph>),
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

enum HttpRouteFallback {
    StarletteRoute {
        route: Py<PyAny>,
        child_scope: Py<PyAny>,
    },
    Response(Py<PyAny>),
}

struct StarletteRouteMatch {
    route: Py<PyAny>,
    child_scope: Py<PyAny>,
}

struct ConstructorRouteMatches {
    full: Option<StarletteRouteMatch>,
    partial: Option<StarletteRouteMatch>,
}

enum FunctionCloseContinuation {
    ReturnedResponse(Py<PyAny>),
    SendStart(Option<Py<PyAny>>),
}

#[derive(Clone, Copy)]
enum RouteHandlerCleanupBoundary {
    Function,
    Request,
    Form,
}

struct RouteHandlerCleanupRecord {
    function_exit_stack: Py<PyAny>,
    request_exit_stack: Py<PyAny>,
    form_request: Option<Py<PyAny>>,
    function_closed: bool,
    request_closed: bool,
    form_closed: bool,
}

enum RouteHandlerCleanupMode {
    FunctionSuccess,
    RequestSuccess,
    Error(PyErr),
}

#[derive(Clone, Copy)]
enum RouteHandlerCleanupPending {
    FunctionExit,
    RequestExit,
    FormClose,
}

struct RouteHandlerCleanupCall {
    cleanup: Py<PyFastApiRequestCleanup>,
    mode: RouteHandlerCleanupMode,
    pending: Option<RouteHandlerCleanupPending>,
    current_error: Option<PyErr>,
    phase: RouteHandlerCleanupBoundary,
    index: usize,
    active_record_index: Option<usize>,
}

const ROUTE_HANDLER_CLEANUPS_SCOPE_KEY: &str = "_fastapi_rs_route_handler_cleanups";

impl RouteHandlerCleanupCall {
    fn new(
        cleanup: Py<PyFastApiRequestCleanup>,
        mode: RouteHandlerCleanupMode,
        py: Python<'_>,
    ) -> Self {
        let record_count = cleanup.bind(py).borrow().records.borrow().len();
        let current_error = match &mode {
            RouteHandlerCleanupMode::Error(error) => Some(error.clone_ref(py)),
            RouteHandlerCleanupMode::FunctionSuccess | RouteHandlerCleanupMode::RequestSuccess => {
                None
            }
        };
        let phase = match &mode {
            RouteHandlerCleanupMode::RequestSuccess => RouteHandlerCleanupBoundary::Request,
            RouteHandlerCleanupMode::FunctionSuccess | RouteHandlerCleanupMode::Error(_) => {
                RouteHandlerCleanupBoundary::Function
            }
        };
        Self {
            cleanup,
            mode,
            pending: None,
            current_error,
            phase,
            index: record_count,
            active_record_index: None,
        }
    }

    fn advance(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        loop {
            let (record_count, next_action) = {
                let cleanup = self.cleanup.bind(py).borrow();
                let mut records = cleanup.records.borrow_mut();
                let record_count = records.len();
                let mut next_action = None;
                while self.index > 0 {
                    self.index -= 1;
                    let record = &mut records[self.index];
                    let action = match self.phase {
                        RouteHandlerCleanupBoundary::Function if !record.function_closed => {
                            record.function_closed = true;
                            Some((
                                RouteHandlerCleanupPending::FunctionExit,
                                record.function_exit_stack.clone_ref(py),
                            ))
                        }
                        RouteHandlerCleanupBoundary::Request if !record.request_closed => {
                            record.request_closed = true;
                            Some((
                                RouteHandlerCleanupPending::RequestExit,
                                record.request_exit_stack.clone_ref(py),
                            ))
                        }
                        _ => None,
                    };
                    if action.is_some() {
                        self.active_record_index = Some(self.index);
                        next_action = action;
                        break;
                    }
                }
                (record_count, next_action)
            };

            if let Some((pending, exit_stack)) = next_action {
                self.pending = Some(pending);
                let awaitable = match self.current_error.as_ref() {
                    Some(error) => dependency_exit_with_error(py, &exit_stack, error)?,
                    None => exit_stack.bind(py).call_method0("aclose")?.unbind(),
                };
                return Ok(MachineAction::Await(awaitable));
            }

            match self.phase {
                RouteHandlerCleanupBoundary::Function => {
                    if matches!(&self.mode, RouteHandlerCleanupMode::FunctionSuccess) {
                        return Ok(MachineAction::Complete(py.None()));
                    }
                    self.phase = RouteHandlerCleanupBoundary::Request;
                    self.index = record_count;
                }
                RouteHandlerCleanupBoundary::Request => {
                    self.phase = RouteHandlerCleanupBoundary::Form;
                    self.index = record_count;
                }
                RouteHandlerCleanupBoundary::Form => {
                    let form_request = {
                        let cleanup = self.cleanup.bind(py).borrow();
                        let mut records = cleanup.records.borrow_mut();
                        let mut request = None;
                        while self.index > 0 {
                            self.index -= 1;
                            let record = &mut records[self.index];
                            if !record.form_closed {
                                record.form_closed = true;
                                if let Some(form_request) = record.form_request.as_ref() {
                                    self.active_record_index = Some(self.index);
                                    request = Some(form_request.clone_ref(py));
                                    break;
                                }
                            }
                        }
                        request
                    };
                    if let Some(form_request) = form_request {
                        self.pending = Some(RouteHandlerCleanupPending::FormClose);
                        return form_request
                            .bind(py)
                            .call_method0("close")
                            .map(Bound::unbind)
                            .map(MachineAction::Await);
                    }
                    if let Some(error) = self.current_error.take() {
                        return Err(error);
                    }
                    return Ok(MachineAction::Complete(py.None()));
                }
            }
        }
    }

    fn exit_stack_resumed(
        &mut self,
        py: Python<'_>,
        result: &Bound<'_, PyAny>,
        boundary: RouteHandlerCleanupPending,
    ) -> PyResult<MachineAction> {
        if self.current_error.is_some() && result.is_truthy()? {
            self.current_error = Some(match boundary {
                RouteHandlerCleanupPending::FunctionExit => {
                    PyTypeError::new_err("'NoneType' object is not callable")
                }
                RouteHandlerCleanupPending::RequestExit => fastapi_error(concat!(
                    "Response not awaited. There's a high chance that the ",
                    "application code is raising an exception and a dependency with yield ",
                    "has a block with a bare except, or a block with except Exception, ",
                    "and is not raising the exception again. Read more about it in the ",
                    "docs: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#dependencies-with-yield-and-except"
                )),
                RouteHandlerCleanupPending::FormClose => {
                    return Err(PyRuntimeError::new_err(
                        "form cleanup cannot suppress a route handler exception",
                    ));
                }
            });
        }
        self.advance(py)
    }

    fn retry_active_cleanup(&mut self, py: Python<'_>, pending: RouteHandlerCleanupPending) {
        let Some(record_index) = self.active_record_index.take() else {
            return;
        };
        let cleanup = self.cleanup.bind(py).borrow();
        let mut records = cleanup.records.borrow_mut();
        if let Some(record) = records.get_mut(record_index) {
            match pending {
                RouteHandlerCleanupPending::FunctionExit => record.function_closed = false,
                RouteHandlerCleanupPending::RequestExit => record.request_closed = false,
                RouteHandlerCleanupPending::FormClose => record.form_closed = false,
            }
        }
        self.index = record_index + 1;
    }
}

impl AwaitableStateMachine for RouteHandlerCleanupCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.advance(py),
            MachineResume::Value(value) => match self.pending.take() {
                Some(
                    pending @ (RouteHandlerCleanupPending::FunctionExit
                    | RouteHandlerCleanupPending::RequestExit),
                ) => {
                    self.active_record_index = None;
                    self.exit_stack_resumed(py, value.bind(py), pending)
                }
                Some(RouteHandlerCleanupPending::FormClose) => {
                    self.active_record_index = None;
                    self.advance(py)
                }
                None => Err(PyRuntimeError::new_err(
                    "route handler cleanup resumed without a pending operation",
                )),
            },
            MachineResume::Error(error) => {
                self.current_error = Some(error.clone_ref(py));
                match self.pending.take() {
                    Some(pending @ RouteHandlerCleanupPending::FunctionExit)
                        if matches!(self.mode, RouteHandlerCleanupMode::FunctionSuccess) =>
                    {
                        self.retry_active_cleanup(py, pending);
                        Err(error)
                    }
                    Some(
                        pending @ (RouteHandlerCleanupPending::FunctionExit
                        | RouteHandlerCleanupPending::RequestExit
                        | RouteHandlerCleanupPending::FormClose),
                    ) => {
                        self.retry_active_cleanup(py, pending);
                        self.advance(py)
                    }
                    None => Err(error),
                }
            }
        }
    }
}

fn append_route_handler_cleanup(
    py: Python<'_>,
    scope: &Bound<'_, PyAny>,
    record: RouteHandlerCleanupRecord,
) -> PyResult<()> {
    let has_cleanup_key = scope
        .call_method1("__contains__", (ROUTE_HANDLER_CLEANUPS_SCOPE_KEY,))?
        .extract::<bool>()?;
    let cleanup = match has_cleanup_key {
        true => {
            let existing = scope.get_item(ROUTE_HANDLER_CLEANUPS_SCOPE_KEY)?;
            match existing.extract::<Py<PyFastApiRequestCleanup>>() {
                Ok(cleanup) => cleanup,
                Err(_) => {
                    let cleanup = Py::new(
                        py,
                        PyFastApiRequestCleanup {
                            records: RefCell::new(Vec::new()),
                            previous_scope_value: Some(existing.unbind()),
                        },
                    )?;
                    scope.set_item(ROUTE_HANDLER_CLEANUPS_SCOPE_KEY, &cleanup)?;
                    cleanup
                }
            }
        }
        false => {
            let cleanup = Py::new(
                py,
                PyFastApiRequestCleanup {
                    records: RefCell::new(Vec::new()),
                    previous_scope_value: None,
                },
            )?;
            scope.set_item(ROUTE_HANDLER_CLEANUPS_SCOPE_KEY, &cleanup)?;
            cleanup
        }
    };
    cleanup.bind(py).borrow().records.borrow_mut().push(record);
    Ok(())
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
    router_default: Option<Py<PyAny>>,
    route_dependency_overrides_provider: Option<Py<PyAny>>,
) -> PyResult<Py<PyAny>> {
    into_python_awaitable(
        py,
        FastApiCall::new(
            app,
            scope,
            receive,
            send,
            FastApiCallOptions {
                route_dependency_overrides_provider,
                router_default,
                ..FastApiCallOptions::default()
            },
        ),
    )
}

fn fastapi_route_core_call(
    py: Python<'_>,
    app: Py<PyFastApi>,
    route_index: usize,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
    dependency_overrides_provider: Option<Py<PyAny>>,
) -> PyResult<Py<PyAny>> {
    into_python_awaitable(
        py,
        FastApiCall::new(
            app,
            scope,
            receive,
            send,
            FastApiCallOptions {
                forced_route_index: Some(route_index),
                route_dependency_overrides_provider: dependency_overrides_provider,
                ..FastApiCallOptions::default()
            },
        ),
    )
}

fn is_async_custom_route_handler(py: Python<'_>, handler: &Bound<'_, PyAny>) -> PyResult<bool> {
    let partial_type = py.import("functools")?.getattr("partial")?;
    let mut callable = handler.clone();
    while callable.is_instance(&partial_type)? {
        callable = callable.getattr("func")?;
    }

    let version = py.import("sys")?.getattr("version_info")?;
    let major = version.get_item(0)?.extract::<u8>()?;
    let minor = version.get_item(1)?.extract::<u8>()?;
    let inspector = if major > 3 || (major == 3 && minor >= 13) {
        py.import("inspect")?
    } else {
        py.import("asyncio")?
    };
    let iscoroutinefunction = inspector.getattr("iscoroutinefunction")?;
    if iscoroutinefunction.call1((&callable,))?.extract::<bool>()? {
        return Ok(true);
    }

    if !py
        .import("builtins")?
        .getattr("callable")?
        .call1((&callable,))?
        .extract::<bool>()?
    {
        return Ok(false);
    }
    iscoroutinefunction
        .call1((callable.getattr("__call__")?,))?
        .extract::<bool>()
}

#[pyclass(
    name = "_FastApiSseProducerFactory",
    module = "fastapi_rs._core",
    unsendable
)]
struct FastApiSseProducerFactory {
    iterator: Py<PyAny>,
    sender: Py<PyAny>,
}

#[pymethods]
impl FastApiSseProducerFactory {
    fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let awaitable = into_python_awaitable(
            py,
            FastApiSseProducer {
                iterator: self.iterator.clone_ref(py),
                sender: self.sender.clone_ref(py),
                pending_error: None,
                stage: FastApiSseProducerStage::Next,
            },
        )?;
        native_task_coroutine(py, awaitable)
    }
}

#[derive(Clone, Copy)]
enum FastApiSseProducerStage {
    Next,
    Send,
    Close,
}

struct FastApiSseProducer {
    iterator: Py<PyAny>,
    sender: Py<PyAny>,
    pending_error: Option<PyErr>,
    stage: FastApiSseProducerStage,
}

impl FastApiSseProducer {
    fn next(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.stage = FastApiSseProducerStage::Next;
        self.iterator
            .bind(py)
            .call_method0("__anext__")
            .map(|awaitable| MachineAction::Await(awaitable.unbind()))
    }
}

impl AwaitableStateMachine for FastApiSseProducer {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.next(py),
            MachineResume::Value(value) => match self.stage {
                FastApiSseProducerStage::Next => {
                    self.stage = FastApiSseProducerStage::Send;
                    self.sender
                        .bind(py)
                        .call_method1("send", (value,))
                        .map(|awaitable| MachineAction::Await(awaitable.unbind()))
                }
                FastApiSseProducerStage::Send => self.next(py),
                FastApiSseProducerStage::Close => match self.pending_error.take() {
                    Some(error) => Err(error),
                    None => Ok(MachineAction::Complete(py.None())),
                },
            },
            MachineResume::Error(error)
                if matches!(self.stage, FastApiSseProducerStage::Next)
                    && error.is_instance_of::<PyStopAsyncIteration>(py) =>
            {
                self.stage = FastApiSseProducerStage::Close;
                self.sender
                    .bind(py)
                    .call_method0("aclose")
                    .map(|awaitable| MachineAction::Await(awaitable.unbind()))
            }
            MachineResume::Error(error) if matches!(self.stage, FastApiSseProducerStage::Close) => {
                Err(self.pending_error.take().unwrap_or(error))
            }
            MachineResume::Error(error) => {
                self.pending_error = Some(error);
                self.stage = FastApiSseProducerStage::Close;
                self.sender
                    .bind(py)
                    .call_method0("aclose")
                    .map(|awaitable| MachineAction::Await(awaitable.unbind()))
            }
        }
    }
}

#[pyclass(
    name = "_FastApiSseKeepaliveFactory",
    module = "fastapi_rs._core",
    unsendable
)]
struct FastApiSseKeepaliveFactory {
    receiver: Py<PyAny>,
    sender: Py<PyAny>,
}

#[pymethods]
impl FastApiSseKeepaliveFactory {
    fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let awaitable = into_python_awaitable(
            py,
            FastApiSseKeepaliveInserter {
                receiver: self.receiver.clone_ref(py),
                sender: self.sender.clone_ref(py),
                timeout_scope: None,
                pending_error: None,
                stage: FastApiSseKeepaliveInserterStage::Receive,
            },
        )?;
        native_task_coroutine(py, awaitable)
    }
}

#[derive(Clone, Copy)]
enum FastApiSseKeepaliveInserterStage {
    Receive,
    SendData,
    SendPing,
    CloseReceiver,
    CloseSender,
}

struct FastApiSseKeepaliveInserter {
    receiver: Py<PyAny>,
    sender: Py<PyAny>,
    timeout_scope: Option<Py<PyAny>>,
    pending_error: Option<PyErr>,
    stage: FastApiSseKeepaliveInserterStage,
}

impl FastApiSseKeepaliveInserter {
    fn receive(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let timeout_scope = py
            .import("anyio")?
            .getattr("fail_after")?
            .call1((SSE_KEEPALIVE_INTERVAL_SECONDS,))?
            .unbind();
        timeout_scope.bind(py).call_method0("__enter__")?;
        let receive = self.receiver.bind(py).call_method0("receive")?.unbind();
        self.timeout_scope = Some(timeout_scope);
        self.stage = FastApiSseKeepaliveInserterStage::Receive;
        Ok(MachineAction::Await(receive))
    }

    fn exit_timeout_scope(&mut self, py: Python<'_>, error: Option<&PyErr>) -> PyResult<bool> {
        let Some(timeout_scope) = self.timeout_scope.take() else {
            return Ok(false);
        };
        let result = if let Some(error) = error {
            let exception_type = error.get_type(py).unbind().into_any();
            let exception_value = error.value(py).clone().unbind().into_any();
            let traceback = error
                .traceback(py)
                .map(|traceback| traceback.unbind().into_any())
                .unwrap_or_else(|| py.None());
            timeout_scope
                .bind(py)
                .call_method1("__exit__", (exception_type, exception_value, traceback))
        } else {
            timeout_scope
                .bind(py)
                .call_method1("__exit__", (py.None(), py.None(), py.None()))
        };
        match result {
            Ok(_) => Ok(false),
            Err(error) if error.is_instance_of::<PyTimeoutError>(py) => Ok(true),
            Err(error) => Err(error),
        }
    }

    fn close(&mut self, py: Python<'_>, error: Option<PyErr>) -> PyResult<MachineAction> {
        self.pending_error = error;
        self.stage = FastApiSseKeepaliveInserterStage::CloseReceiver;
        self.receiver
            .bind(py)
            .call_method0("aclose")
            .map(|awaitable| MachineAction::Await(awaitable.unbind()))
    }

    fn close_sender(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.stage = FastApiSseKeepaliveInserterStage::CloseSender;
        self.sender
            .bind(py)
            .call_method0("aclose")
            .map(|awaitable| MachineAction::Await(awaitable.unbind()))
    }

    fn finish(&mut self, py: Python<'_>, value: Option<Py<PyAny>>) -> PyResult<MachineAction> {
        match self.pending_error.take() {
            Some(error) => Err(error),
            None => Ok(MachineAction::Complete(value.unwrap_or_else(|| py.None()))),
        }
    }

    fn is_end_of_stream(py: Python<'_>, error: &PyErr) -> PyResult<bool> {
        error
            .value(py)
            .is_instance(&py.import("anyio")?.getattr("EndOfStream")?)
    }
}

impl AwaitableStateMachine for FastApiSseKeepaliveInserter {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.receive(py),
            MachineResume::Value(value) => match self.stage {
                FastApiSseKeepaliveInserterStage::Receive => {
                    match self.exit_timeout_scope(py, None) {
                        Ok(true) => {
                            self.stage = FastApiSseKeepaliveInserterStage::SendPing;
                            self.sender
                                .bind(py)
                                .call_method1("send", (PyBytes::new(py, SSE_KEEPALIVE_COMMENT),))
                                .map(|awaitable| MachineAction::Await(awaitable.unbind()))
                        }
                        Ok(false) => {
                            self.stage = FastApiSseKeepaliveInserterStage::SendData;
                            self.sender
                                .bind(py)
                                .call_method1("send", (value,))
                                .map(|awaitable| MachineAction::Await(awaitable.unbind()))
                        }
                        Err(error) => self.close(py, Some(error)),
                    }
                }
                FastApiSseKeepaliveInserterStage::SendData
                | FastApiSseKeepaliveInserterStage::SendPing => self.receive(py),
                FastApiSseKeepaliveInserterStage::CloseReceiver => self.close_sender(py),
                FastApiSseKeepaliveInserterStage::CloseSender => self.finish(py, Some(value)),
            },
            MachineResume::Error(error) => match self.stage {
                FastApiSseKeepaliveInserterStage::Receive => {
                    match self.exit_timeout_scope(py, Some(&error)) {
                        Ok(true) => {
                            self.stage = FastApiSseKeepaliveInserterStage::SendPing;
                            self.sender
                                .bind(py)
                                .call_method1("send", (PyBytes::new(py, SSE_KEEPALIVE_COMMENT),))
                                .map(|awaitable| MachineAction::Await(awaitable.unbind()))
                        }
                        Ok(false) if Self::is_end_of_stream(py, &error)? => self.close(py, None),
                        Ok(false) => self.close(py, Some(error)),
                        Err(scope_error) => self.close(py, Some(scope_error)),
                    }
                }
                FastApiSseKeepaliveInserterStage::SendData
                | FastApiSseKeepaliveInserterStage::SendPing => self.close(py, Some(error)),
                FastApiSseKeepaliveInserterStage::CloseReceiver => {
                    self.pending_error.get_or_insert(error);
                    self.close_sender(py)
                }
                FastApiSseKeepaliveInserterStage::CloseSender => self.finish(py, None),
            },
        }
    }
}

#[derive(Default)]
struct FastApiSseKeepaliveSession {
    task_group: Option<Py<PyAny>>,
    receive_stream: Option<Py<PyAny>>,
    finished: bool,
}

#[pyclass(
    name = "_FastApiSseKeepaliveStream",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiSseKeepaliveStream {
    producer_iterator: Py<PyAny>,
    session: Rc<RefCell<FastApiSseKeepaliveSession>>,
    checkpoint_next: bool,
}

#[pymethods]
impl PyFastApiSseKeepaliveStream {
    #[new]
    fn new(producer_iterator: Py<PyAny>) -> Self {
        Self {
            producer_iterator,
            session: Rc::new(RefCell::new(FastApiSseKeepaliveSession::default())),
            checkpoint_next: false,
        }
    }

    fn __aiter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    fn start(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            FastApiSseKeepaliveSetup {
                producer_iterator: self.producer_iterator.clone_ref(py),
                session: Rc::clone(&self.session),
                task_group: None,
                producer_sender: None,
                producer_receiver: None,
                keepalive_sender: None,
                keepalive_receiver: None,
                stage: FastApiSseKeepaliveSetupStage::Start,
            },
        )
    }

    fn __anext__(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let checkpoint = if self.checkpoint_next {
            Some(py.import("anyio")?.getattr("sleep")?.call1((0,))?.unbind())
        } else {
            None
        };
        self.checkpoint_next = true;
        into_python_awaitable(
            py,
            FastApiSseKeepaliveNext {
                session: Rc::clone(&self.session),
                checkpoint,
                stage: FastApiSseKeepaliveNextStage::Start,
            },
        )
    }

    fn aclose(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            FastApiSseKeepaliveClose {
                session: Rc::clone(&self.session),
                pending_error: None,
                stage: FastApiSseKeepaliveCloseStage::Start,
            },
        )
    }
}

#[derive(Clone, Copy)]
enum FastApiSseKeepaliveSetupStage {
    Start,
    EnterTaskGroup,
}

struct FastApiSseKeepaliveSetup {
    producer_iterator: Py<PyAny>,
    session: Rc<RefCell<FastApiSseKeepaliveSession>>,
    task_group: Option<Py<PyAny>>,
    producer_sender: Option<Py<PyAny>>,
    producer_receiver: Option<Py<PyAny>>,
    keepalive_sender: Option<Py<PyAny>>,
    keepalive_receiver: Option<Py<PyAny>>,
    stage: FastApiSseKeepaliveSetupStage,
}

impl FastApiSseKeepaliveSetup {
    fn start(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let anyio = py.import("anyio")?;
        let producer_streams = anyio
            .getattr("create_memory_object_stream")?
            .call1((1,))?
            .cast_into::<PyTuple>()?;
        let producer_sender = producer_streams.get_item(0)?.unbind();
        let producer_receiver = producer_streams.get_item(1)?.unbind();
        let keepalive_streams = anyio
            .getattr("create_memory_object_stream")?
            .call1((1,))?
            .cast_into::<PyTuple>()?;
        let keepalive_sender = keepalive_streams.get_item(0)?.unbind();
        let keepalive_receiver = keepalive_streams.get_item(1)?.unbind();
        let task_group = anyio.getattr("create_task_group")?.call0()?.unbind();
        let enter = task_group.bind(py).call_method0("__aenter__")?.unbind();
        self.task_group = Some(task_group);
        self.producer_sender = Some(producer_sender);
        self.producer_receiver = Some(producer_receiver);
        self.keepalive_sender = Some(keepalive_sender);
        self.keepalive_receiver = Some(keepalive_receiver);
        self.stage = FastApiSseKeepaliveSetupStage::EnterTaskGroup;
        Ok(MachineAction::Await(enter))
    }

    fn start_tasks(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let task_group = self
            .task_group
            .as_ref()
            .map(|task_group| task_group.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("SSE task group was not initialized"))?;
        let producer_sender = self
            .producer_sender
            .as_ref()
            .map(|stream| stream.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("SSE producer stream was not initialized"))?;
        let producer_receiver = self
            .producer_receiver
            .as_ref()
            .map(|stream| stream.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("SSE producer stream was not initialized"))?;
        let keepalive_sender = self
            .keepalive_sender
            .as_ref()
            .map(|stream| stream.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("SSE keepalive stream was not initialized"))?;
        let keepalive_receiver = self
            .keepalive_receiver
            .as_ref()
            .map(|stream| stream.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("SSE keepalive stream was not initialized"))?;
        {
            let mut session = self.session.borrow_mut();
            session.task_group = Some(task_group.clone_ref(py));
            session.receive_stream = Some(keepalive_receiver);
            session.finished = false;
        }
        let producer = Py::new(
            py,
            FastApiSseProducerFactory {
                iterator: self.producer_iterator.clone_ref(py),
                sender: producer_sender,
            },
        )?;
        let inserter = Py::new(
            py,
            FastApiSseKeepaliveFactory {
                receiver: producer_receiver,
                sender: keepalive_sender,
            },
        )?;
        let producer_factory = producer.bind(py).getattr("__call__")?;
        let keepalive_factory = inserter.bind(py).getattr("__call__")?;
        task_group
            .bind(py)
            .call_method1("start_soon", (producer_factory,))?;
        task_group
            .bind(py)
            .call_method1("start_soon", (keepalive_factory,))?;
        Ok(MachineAction::Complete(py.None()))
    }
}

impl AwaitableStateMachine for FastApiSseKeepaliveSetup {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.start(py),
            MachineResume::Value(_) => match self.stage {
                FastApiSseKeepaliveSetupStage::Start => self.start(py),
                FastApiSseKeepaliveSetupStage::EnterTaskGroup => self.start_tasks(py),
            },
            MachineResume::Error(error) => Err(error),
        }
    }
}

#[derive(Clone, Copy)]
enum FastApiSseKeepaliveCloseStage {
    Start,
    TaskGroup,
    ReceiveStream,
}

struct FastApiSseKeepaliveClose {
    session: Rc<RefCell<FastApiSseKeepaliveSession>>,
    pending_error: Option<PyErr>,
    stage: FastApiSseKeepaliveCloseStage,
}

impl FastApiSseKeepaliveClose {
    fn finish(&mut self) {
        let mut session = self.session.borrow_mut();
        session.finished = true;
        session.task_group = None;
        session.receive_stream = None;
    }

    fn close_receive_stream(
        &mut self,
        py: Python<'_>,
        error: Option<PyErr>,
    ) -> PyResult<MachineAction> {
        self.pending_error = error;
        let receiver = self
            .session
            .borrow()
            .receive_stream
            .as_ref()
            .map(|stream| stream.clone_ref(py));
        let Some(receiver) = receiver else {
            self.finish();
            return match self.pending_error.take() {
                Some(error) => Err(error),
                None => Ok(MachineAction::Complete(py.None())),
            };
        };
        let close = receiver.bind(py).call_method0("aclose")?.unbind();
        self.stage = FastApiSseKeepaliveCloseStage::ReceiveStream;
        Ok(MachineAction::Await(close))
    }

    fn exit_task_group(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let task_group = self
            .session
            .borrow()
            .task_group
            .as_ref()
            .map(|task_group| task_group.clone_ref(py));
        let Some(task_group) = task_group else {
            return self.close_receive_stream(py, None);
        };
        task_group
            .bind(py)
            .getattr("cancel_scope")?
            .call_method0("cancel")?;
        let exit = task_group
            .bind(py)
            .call_method1("__aexit__", (py.None(), py.None(), py.None()))?
            .unbind();
        self.stage = FastApiSseKeepaliveCloseStage::TaskGroup;
        Ok(MachineAction::Await(exit))
    }
}

impl AwaitableStateMachine for FastApiSseKeepaliveClose {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.exit_task_group(py),
            MachineResume::Value(value) => match self.stage {
                FastApiSseKeepaliveCloseStage::Start => Ok(MachineAction::Complete(value)),
                FastApiSseKeepaliveCloseStage::TaskGroup => {
                    self.session.borrow_mut().task_group = None;
                    self.close_receive_stream(py, None)
                }
                FastApiSseKeepaliveCloseStage::ReceiveStream => {
                    self.finish();
                    match self.pending_error.take() {
                        Some(error) => Err(error),
                        None => Ok(MachineAction::Complete(value)),
                    }
                }
            },
            MachineResume::Error(error) => match self.stage {
                FastApiSseKeepaliveCloseStage::TaskGroup => {
                    self.session.borrow_mut().task_group = None;
                    self.close_receive_stream(py, Some(error))
                }
                FastApiSseKeepaliveCloseStage::ReceiveStream => {
                    self.finish();
                    Err(self.pending_error.take().unwrap_or(error))
                }
                FastApiSseKeepaliveCloseStage::Start => {
                    self.finish();
                    Err(error)
                }
            },
        }
    }
}

#[derive(Clone, Copy)]
enum FastApiSseKeepaliveNextStage {
    Start,
    Checkpoint,
    Receive,
}

struct FastApiSseKeepaliveNext {
    session: Rc<RefCell<FastApiSseKeepaliveSession>>,
    checkpoint: Option<Py<PyAny>>,
    stage: FastApiSseKeepaliveNextStage,
}

impl FastApiSseKeepaliveNext {
    fn start(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        if self.session.borrow().finished {
            return Err(PyStopAsyncIteration::new_err(""));
        }
        if let Some(checkpoint) = self.checkpoint.take() {
            self.stage = FastApiSseKeepaliveNextStage::Checkpoint;
            return Ok(MachineAction::Await(checkpoint));
        }
        self.start_receive(py)
    }

    fn start_receive(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let receiver = self
            .session
            .borrow()
            .receive_stream
            .as_ref()
            .map(|stream| stream.clone_ref(py))
            .ok_or_else(|| PyRuntimeError::new_err("SSE keepalive stream was not initialized"))?;
        self.stage = FastApiSseKeepaliveNextStage::Receive;
        receiver
            .bind(py)
            .call_method0("receive")
            .map(|awaitable| MachineAction::Await(awaitable.unbind()))
    }

    fn is_end_of_stream(py: Python<'_>, error: &PyErr) -> PyResult<bool> {
        error
            .value(py)
            .is_instance(&py.import("anyio")?.getattr("EndOfStream")?)
    }
}

impl AwaitableStateMachine for FastApiSseKeepaliveNext {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.start(py),
            MachineResume::Value(value) => match self.stage {
                FastApiSseKeepaliveNextStage::Start => self.start(py),
                FastApiSseKeepaliveNextStage::Checkpoint => self.start_receive(py),
                FastApiSseKeepaliveNextStage::Receive => Ok(MachineAction::Complete(value)),
            },
            MachineResume::Error(error) => match self.stage {
                FastApiSseKeepaliveNextStage::Receive if Self::is_end_of_stream(py, &error)? => {
                    self.session.borrow_mut().finished = true;
                    Err(PyStopAsyncIteration::new_err(""))
                }
                FastApiSseKeepaliveNextStage::Start
                | FastApiSseKeepaliveNextStage::Checkpoint
                | FastApiSseKeepaliveNextStage::Receive => Err(error),
            },
        }
    }
}

#[derive(Default)]
struct FastApiCallOptions {
    forced_route_index: Option<usize>,
    route_dependency_overrides_provider: Option<Py<PyAny>>,
    router_default: Option<Py<PyAny>>,
    provided_request: Option<Py<PyAny>>,
    response_class_override: Option<Py<PyAny>>,
}

struct FastApiCall {
    app: Py<PyFastApi>,
    route_dependency_overrides_provider: Option<Py<PyAny>>,
    router_default: Option<Py<PyAny>>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
    route_index: Option<usize>,
    forced_route_index: Option<usize>,
    route_handler_response: bool,
    provided_request: Option<Py<PyAny>>,
    response_class_override: Option<Py<PyAny>>,
    route_handler_cleanup: Option<Py<PyFastApiRequestCleanup>>,
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
    sse_setup_response: Option<Py<PyAny>>,
}

impl FastApiCall {
    fn new(
        app: Py<PyFastApi>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
        options: FastApiCallOptions,
    ) -> Self {
        let FastApiCallOptions {
            forced_route_index,
            route_dependency_overrides_provider,
            router_default,
            provided_request,
            response_class_override,
        } = options;
        let route_handler_response = provided_request.is_some();
        Self {
            app,
            route_dependency_overrides_provider,
            router_default,
            scope,
            receive,
            send,
            route_index: None,
            forced_route_index,
            route_handler_response,
            provided_request,
            response_class_override,
            route_handler_cleanup: None,
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
            sse_setup_response: None,
        }
    }

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
        let request_method = parse_scope_string(self.scope.bind(py), "method", "GET")?;
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
                    request_method,
                    route.path.clone(),
                )
            }
        };
        let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
        response_endpoint_context(py, endpoint.bind(py), &method, &path, &root_path)
    }

    fn websocket_validation_endpoint_context<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyDict>> {
        let route_index = self
            .websocket_route_index
            .ok_or_else(|| PyRuntimeError::new_err("WebSocket validation has no selected route"))?;
        let (endpoint, path) = {
            let app = self.app.bind(py).borrow();
            let route = app.websocket_routes.get(route_index).ok_or_else(|| {
                PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
            })?;
            (route.endpoint.clone_ref(py), route.path.clone())
        };
        let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
        response_endpoint_context(py, endpoint.bind(py), "WS", &path, &root_path)
    }

    fn start_returned_response(
        &mut self,
        py: Python<'_>,
        response: &Bound<'_, PyAny>,
    ) -> PyResult<MachineAction> {
        if self.route_handler_response {
            self.defer_route_handler_cleanup(py)?;
            return Ok(MachineAction::Complete(response.clone().unbind()));
        }
        self.close_function_dependency_stack_before_response(
            py,
            FunctionCloseContinuation::ReturnedResponse(response.clone().unbind()),
        )
    }

    fn defer_route_handler_cleanup(&mut self, py: Python<'_>) -> PyResult<()> {
        let (function_exit_stack, request_exit_stack) =
            if let Some(invocation) = self.invocation.as_mut() {
                invocation.function_dependency_exit_stack_closed = true;
                invocation.dependency_exit_stack_closed = true;
                (
                    invocation.function_dependency_exit_stack.clone_ref(py),
                    invocation.dependency_exit_stack.clone_ref(py),
                )
            } else {
                let (request_stack, function_stack) =
                    route_handler_exit_stacks(py, self.scope.bind(py))?;
                (function_stack, request_stack)
            };
        append_route_handler_cleanup(
            py,
            self.scope.bind(py),
            RouteHandlerCleanupRecord {
                function_exit_stack,
                request_exit_stack,
                form_request: self
                    .form_request
                    .as_ref()
                    .map(|request| request.clone_ref(py)),
                function_closed: false,
                request_closed: false,
                form_closed: false,
            },
        )
    }

    fn take_route_handler_cleanup(
        &mut self,
        py: Python<'_>,
    ) -> PyResult<Option<Py<PyFastApiRequestCleanup>>> {
        if self.route_handler_cleanup.is_some() {
            return Ok(self.route_handler_cleanup.take());
        }
        let scope = self.scope.bind(py);
        if !scope
            .call_method1("__contains__", (ROUTE_HANDLER_CLEANUPS_SCOPE_KEY,))?
            .extract::<bool>()?
        {
            return Ok(None);
        }
        let cleanup = scope.get_item(ROUTE_HANDLER_CLEANUPS_SCOPE_KEY)?;
        let cleanup = cleanup.extract::<Py<PyFastApiRequestCleanup>>()?;
        let previous_scope_value = cleanup
            .bind(py)
            .borrow()
            .previous_scope_value
            .as_ref()
            .map(|value| value.clone_ref(py));
        if let Some(previous_scope_value) = previous_scope_value {
            scope.set_item(ROUTE_HANDLER_CLEANUPS_SCOPE_KEY, previous_scope_value)?;
        } else {
            scope.del_item(ROUTE_HANDLER_CLEANUPS_SCOPE_KEY)?;
        }
        Ok(Some(cleanup))
    }

    fn begin_custom_route_response(
        &mut self,
        py: Python<'_>,
        response: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let cleanup = match self.take_route_handler_cleanup(py)? {
            Some(cleanup) => cleanup,
            None => {
                self.defer_route_handler_cleanup(py)?;
                self.take_route_handler_cleanup(py)?.ok_or_else(|| {
                    PyRuntimeError::new_err("route handler response cleanup was lost")
                })?
            }
        };
        self.route_handler_cleanup = Some(cleanup.clone_ref(py));
        self.function_close_continuation =
            Some(FunctionCloseContinuation::ReturnedResponse(response));
        self.pending = Some(PendingAction::RouteHandlerFunctionCleanupBeforeResponse);
        let awaitable = into_python_awaitable(
            py,
            RouteHandlerCleanupCall::new(cleanup, RouteHandlerCleanupMode::FunctionSuccess, py),
        )?;
        Ok(MachineAction::Await(awaitable))
    }

    fn begin_route_handler_cleanup_error(
        &mut self,
        py: Python<'_>,
        error: PyErr,
        ensure_scope_cleanup: bool,
    ) -> PyResult<MachineAction> {
        let cleanup = match self.take_route_handler_cleanup(py)? {
            Some(cleanup) => cleanup,
            None if ensure_scope_cleanup => {
                self.defer_route_handler_cleanup(py)?;
                self.take_route_handler_cleanup(py)?.ok_or_else(|| {
                    PyRuntimeError::new_err("route handler error cleanup was lost")
                })?
            }
            None => return self.route_exception(py, error),
        };
        let original_error = error.clone_ref(py);
        self.pending = Some(PendingAction::RouteHandlerCleanupAfterError(original_error));
        let awaitable = into_python_awaitable(
            py,
            RouteHandlerCleanupCall::new(cleanup, RouteHandlerCleanupMode::Error(error), py),
        )?;
        Ok(MachineAction::Await(awaitable))
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

    fn match_constructor_route(
        &self,
        py: Python<'_>,
        scope: &Bound<'_, PyAny>,
    ) -> PyResult<ConstructorRouteMatches> {
        let routes = self
            .app
            .bind(py)
            .borrow()
            .constructor_routes
            .iter()
            .map(|route| route.clone_ref(py))
            .collect::<Vec<_>>();
        let full_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("FULL")?;
        let partial_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("PARTIAL")?;
        let mut partial_route = None;

        for route in routes {
            let match_result = route.bind(py).call_method1("matches", (scope,))?;
            let route_match = match_result.get_item(0)?;
            let child_scope = match_result.get_item(1)?.unbind();
            if route_match.is(&partial_match) && partial_route.is_none() {
                partial_route = Some(StarletteRouteMatch {
                    route: route.clone_ref(py),
                    child_scope: child_scope.clone_ref(py),
                });
            }
            if route_match.is(&full_match) {
                return Ok(ConstructorRouteMatches {
                    full: Some(StarletteRouteMatch { route, child_scope }),
                    partial: partial_route,
                });
            }
        }

        Ok(ConstructorRouteMatches {
            full: None,
            partial: partial_route,
        })
    }

    fn handle_constructor_route(
        &mut self,
        py: Python<'_>,
        route: Py<PyAny>,
        child_scope: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        scope.call_method1("update", (child_scope.bind(py),))?;
        let awaitable = route
            .bind(py)
            .call_method1("handle", (scope, self.receive.bind(py), self.send.bind(py)))?;
        self.pending = Some(PendingAction::MountedApp);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn dispatch_http_fallback(
        &mut self,
        py: Python<'_>,
        fallback: HttpRouteFallback,
    ) -> PyResult<MachineAction> {
        match fallback {
            HttpRouteFallback::StarletteRoute { route, child_scope } => {
                self.handle_constructor_route(py, route, child_scope)
            }
            HttpRouteFallback::Response(response) => {
                self.start_returned_response(py, response.bind(py))
            }
        }
    }

    fn dispatch_frontend_route(
        &mut self,
        py: Python<'_>,
        route_path: &str,
        method: &str,
    ) -> PyResult<Option<MachineAction>> {
        let selected = {
            let app = self.app.bind(py).borrow();
            let route_order = effective_route_order(py, &app, IncludedRouteCategory::Frontend)?;
            let mut selected: Option<(usize, String, usize)> = None;
            for index in route_order {
                let route = app.frontend_routes.get(index).ok_or_else(|| {
                    PyRuntimeError::new_err("effective frontend route order was lost")
                })?;
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
        #[cfg(feature = "fault-injection")]
        if let Some(error) = frontend_lookup_fault_error(py)? {
            return self.frontend_response_failed(py, error);
        }
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
        let builtins = py.import("builtins")?;
        if value.is_instance(&builtins.getattr("PermissionError")?)? {
            return self.route_exception(py, frontend_http_error(py, 401)?);
        }
        if value.is_instance(&builtins.getattr("ValueError")?)? {
            return self.route_exception(py, frontend_http_error(py, 404)?);
        }
        if value.is_instance(&builtins.getattr("OSError")?)? {
            let error_number = value.getattr("errno")?;
            let name_too_long = py.import("errno")?.getattr("ENAMETOOLONG")?;
            if error_number
                .rich_compare(&name_too_long, pyo3::basic::CompareOp::Eq)?
                .is_truthy()?
            {
                return self.route_exception(py, frontend_http_error(py, 404)?);
            }
        }
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
        let (redirect_path, constructor_routes) = {
            let app = self.app.bind(py).borrow();
            if !app.redirect_slashes {
                return Ok(None);
            }
            (
                app.docs_router
                    .find_slash_redirect_path(path, root_path, method)
                    .or_else(|| app.router.find_slash_redirect_path(path, root_path, method)),
                app.constructor_routes
                    .iter()
                    .map(|route| route.clone_ref(py))
                    .collect::<Vec<_>>(),
            )
        };
        let redirect_path = match redirect_path {
            Some(redirect_path) => redirect_path,
            None => {
                let route_path = py
                    .import("starlette.routing")?
                    .getattr("_get_route_path")?
                    .call1((self.scope.bind(py),))?
                    .extract::<String>()?;
                if route_path == "/" {
                    return Ok(None);
                }
                let redirect_path = if route_path.ends_with('/') {
                    path.trim_end_matches('/').to_owned()
                } else {
                    format!("{path}/")
                };
                let redirect_scope = PyDict::new(py);
                redirect_scope.call_method1("update", (self.scope.bind(py),))?;
                redirect_scope.set_item("path", &redirect_path)?;
                let none_match = py
                    .import("starlette.routing")?
                    .getattr("Match")?
                    .getattr("NONE")?;
                let mut has_redirect_match = false;
                for route in constructor_routes {
                    let match_result =
                        route.bind(py).call_method1("matches", (&redirect_scope,))?;
                    if !match_result.get_item(0)?.is(&none_match) {
                        has_redirect_match = true;
                        break;
                    }
                }
                if !has_redirect_match {
                    return Ok(None);
                }
                redirect_path
            }
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

    fn begin_direct_route(
        &mut self,
        py: Python<'_>,
        route_index: usize,
    ) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let scope_type = parse_scope_string(scope, "type", "http")?;
        if scope_type != "http" {
            return Err(PyValueError::new_err(format!(
                "FastAPI APIRoute supports HTTP ASGI scopes, not {scope_type:?}"
            )));
        }
        let (has_form_inputs, has_body_inputs) = {
            let app = self.app.bind(py).borrow();
            let route = app.routes.get(route_index).ok_or_else(|| {
                PyRuntimeError::new_err("selected standalone FastAPI route was lost")
            })?;
            (
                route.plan.has_form_inputs(),
                !route.plan.all_body_parameters().is_empty(),
            )
        };
        self.route_index = Some(route_index);
        self.injected_response = Some(fastapi_response_state(py)?);
        let _exit_stacks = if self.provided_request.is_some() {
            route_handler_exit_stacks(py, scope)?
        } else {
            reset_route_handler_exit_stacks(py, scope)?
        };
        let request = match self.provided_request.as_ref() {
            Some(request) => request.bind(py).clone(),
            None => py
                .import("starlette.requests")?
                .getattr("Request")?
                .call1((scope, self.receive.bind(py), self.send.bind(py)))?,
        };
        scope.set_item("starlette._exception_request", &request)?;
        self.request = Some(request.unbind());

        if has_form_inputs {
            self.receive_form(py)
        } else if has_body_inputs {
            self.receive_http_body(py)
        } else {
            self.invoke_http_route(py, &[], false)
        }
    }

    fn begin_api_route(
        &mut self,
        py: Python<'_>,
        route_index: usize,
        path_params: Vec<(String, String)>,
    ) -> PyResult<MachineAction> {
        self.route_index = Some(route_index);
        self.path_params = path_params;
        self.injected_response = Some(fastapi_response_state(py)?);
        let (route_scope, effective_route_context, original_route, request_handler) = {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            (
                route
                    .route_scope
                    .as_ref()
                    .ok_or_else(|| {
                        PyRuntimeError::new_err("selected FastAPI route has no dispatch scope")
                    })?
                    .clone_ref(py),
                route
                    .effective_route_context
                    .as_ref()
                    .map(|context| context.clone_ref(py)),
                route.original_route.clone_ref(py),
                route
                    .request_handler
                    .as_ref()
                    .map(|handler| handler.clone_ref(py)),
            )
        };
        let request_handler = match effective_route_context.as_ref() {
            Some(context) => custom_api_route_handler_in_effective_context(
                py,
                original_route.bind(py),
                context.bind(py),
            )?,
            None => request_handler,
        };
        let scope = self.scope.bind(py);
        scope.set_item("route", route_scope)?;
        if let Some(effective_route_context) = effective_route_context {
            let fastapi_scope =
                scope.call_method1("setdefault", (concat!("fast", "api"), PyDict::new(py)))?;
            fastapi_scope.set_item("effective_route_context", effective_route_context)?;
        }
        let converted_path_params = PyDict::new(py);
        {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            let convertors = route.param_convertors.bind(py);
            for (name, value) in &self.path_params {
                let convertor = convertors.get_item(name)?.ok_or_else(|| {
                    PyRuntimeError::new_err("matched FastAPI route is missing a path convertor")
                })?;
                converted_path_params
                    .set_item(name, convertor.call_method1("convert", (value,))?)?;
            }
        }
        scope.set_item("path_params", converted_path_params)?;
        let _exit_stacks = reset_route_handler_exit_stacks(py, scope)?;
        let request_type = py.import("starlette.requests")?.getattr("Request")?;
        let request = request_type.call1((scope, self.receive.bind(py), self.send.bind(py)))?;
        scope.set_item("starlette._exception_request", &request)?;
        self.request = Some(request.clone().unbind());
        if let Some(request_handler) = request_handler {
            self.pending = Some(PendingAction::CustomRouteHandler);
            let is_async_callable = is_async_custom_route_handler(py, request_handler.bind(py))?;
            let awaitable = if is_async_callable {
                request_handler.bind(py).call1((&request,))?
            } else {
                py.import("starlette.concurrency")?
                    .getattr("run_in_threadpool")?
                    .call1((request_handler.bind(py), &request))?
            };
            return Ok(MachineAction::Await(awaitable.unbind()));
        }
        let (has_form_inputs, has_body_inputs) = {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
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

    fn dispatch_registered_http_routes(
        &mut self,
        py: Python<'_>,
        path: &str,
        root_path: &str,
        method: &str,
        mut earlier_fallback: Option<HttpRouteFallback>,
    ) -> PyResult<Option<MachineAction>> {
        let candidates =
            collect_http_dispatch_candidates(py, &self.app, false, "", &mut HashSet::new())?;
        let scope = self.scope.bind(py);
        let full_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("FULL")?;
        let partial_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("PARTIAL")?;

        for candidate in candidates {
            match candidate {
                HttpDispatchCandidate::ApiRoute(route_index) => {
                    let match_result = {
                        let app = self.app.bind(py).borrow();
                        let route = app.routes.get(route_index).ok_or_else(|| {
                            PyRuntimeError::new_err("selected FastAPI route was lost")
                        })?;
                        route
                            .route_matcher
                            .as_ref()
                            .map(|matcher| matcher.matches(path, root_path, method))
                    };
                    match match_result {
                        Some(FastApiOperationMatch::Matched { path_params, .. }) => {
                            materialize_included_response_fields(
                                py,
                                &self.app,
                                Some(route_index),
                                None,
                            )?;
                            return self.begin_api_route(py, route_index, path_params).map(Some);
                        }
                        Some(FastApiOperationMatch::MethodNotAllowed {
                            allowed_methods, ..
                        }) => {
                            if earlier_fallback.is_none() {
                                let response =
                                    http_method_not_allowed_response(py, &allowed_methods)?;
                                earlier_fallback = Some(HttpRouteFallback::Response(response));
                            }
                        }
                        Some(FastApiOperationMatch::NotFound) | None => {}
                    }
                }
                HttpDispatchCandidate::StarletteRoute(route) => {
                    let match_result = route.bind(py).call_method1("matches", (scope,))?;
                    let route_match = match_result.get_item(0)?;
                    let child_scope = match_result.get_item(1)?.unbind();
                    if route_match.is(&partial_match) && earlier_fallback.is_none() {
                        earlier_fallback = Some(HttpRouteFallback::StarletteRoute {
                            route: route.clone_ref(py),
                            child_scope: child_scope.clone_ref(py),
                        });
                    }
                    if route_match.is(&full_match) {
                        materialize_included_response_fields(py, &self.app, None, None)?;
                        return self
                            .handle_constructor_route(py, route, child_scope)
                            .map(Some);
                    }
                }
            }
        }

        if let Some(fallback) = earlier_fallback {
            materialize_included_response_fields(py, &self.app, None, None)?;
            return self.dispatch_http_fallback(py, fallback).map(Some);
        }

        // FastAPI constructs included response fields while scanning, including
        // on a full miss. This completes before slash-redirect probing.
        materialize_included_response_fields(py, &self.app, None, None)?;
        Ok(None)
    }

    fn begin(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        if let Some(route_index) = self.forced_route_index {
            return self.begin_direct_route(py, route_index);
        }
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
        refresh_included_router_routes(py, &self.app)?;
        let path = parse_scope_string(scope, "path", "/")?;
        let method = parse_scope_string(scope, "method", "GET")?;
        let route_path = py
            .import("starlette.routing")?
            .getattr("_get_route_path")?
            .call1((scope,))?
            .extract::<String>()?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let constructor_matches = self.match_constructor_route(py, scope)?;
        let mut earlier_fallback =
            constructor_matches
                .partial
                .map(|matched| HttpRouteFallback::StarletteRoute {
                    route: matched.route,
                    child_scope: matched.child_scope,
                });
        if let Some(matched) = constructor_matches.full {
            return self.handle_constructor_route(py, matched.route, matched.child_scope);
        }
        let (
            openapi_url,
            title,
            redirect_url,
            init_oauth,
            swagger_ui_parameters,
            root_path_in_servers,
        ) = {
            let app = self.app.bind(py).borrow();
            (
                app.openapi_url.clone(),
                app.title.clone(),
                app.swagger_ui_oauth2_redirect_url.clone(),
                app.swagger_ui_init_oauth
                    .as_ref()
                    .map(|configuration| configuration.clone_ref(py)),
                app.swagger_ui_parameters
                    .as_ref()
                    .map(|parameters| parameters.clone_ref(py)),
                app.root_path_in_servers,
            )
        };
        if let Some(openapi_url) = openapi_url.as_deref().filter(|url| !url.is_empty()) {
            if route_path == openapi_url && method == "GET" {
                let root_path = root_path.trim_end_matches('/');
                let public_app = fastapi_public_instance(py, &self.app)?;
                let schema = public_app.bind(py).getattr("openapi")?.call0()?.unbind();
                let document =
                    openapi_document_for_root_path(py, schema, root_path, root_path_in_servers)?;
                self.response_status = 200;
                self.response_body = json_bytes(py, document.bind(py))?;
                return self.send_start(py);
            }
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
                    let response = match docs_route {
                        FastApiDocsRoute::SwaggerUi => {
                            let docs_openapi_url = format!("{docs_root_path}{openapi_url}");
                            let docs_title = format!("{title} - Swagger UI");
                            let oauth2_redirect_url = redirect_url
                                .as_deref()
                                .filter(|path| !path.is_empty())
                                .map(|path| format!("{docs_root_path}{path}"));
                            docs::get_swagger_ui_html(
                                py,
                                PyString::new(py, &docs_openapi_url).into_any(),
                                PyString::new(py, &docs_title).into_any(),
                                PyString::new(py, docs::DEFAULT_SWAGGER_JS_URL).into_any(),
                                PyString::new(py, docs::DEFAULT_SWAGGER_CSS_URL).into_any(),
                                PyString::new(py, docs::DEFAULT_SWAGGER_FAVICON_URL).into_any(),
                                oauth2_redirect_url
                                    .as_deref()
                                    .map(|url| PyString::new(py, url).into_any()),
                                init_oauth.as_ref().map(|value| value.bind(py).clone()),
                                swagger_ui_parameters
                                    .as_ref()
                                    .map(|parameters| parameters.bind(py).clone()),
                            )?
                        }
                        FastApiDocsRoute::OAuth2Redirect => py
                            .import("starlette.responses")?
                            .getattr("HTMLResponse")?
                            .call1((docs::oauth2_redirect_html(),))?,
                        FastApiDocsRoute::ReDoc => {
                            let html = docs::redoc_html(
                                &format!("{docs_root_path}{openapi_url}"),
                                &format!("{title} - ReDoc"),
                            );
                            py.import("starlette.responses")?
                                .getattr("HTMLResponse")?
                                .call1((html,))?
                        }
                    };
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
                    if earlier_fallback.is_none() {
                        earlier_fallback = Some(HttpRouteFallback::Response(response.unbind()));
                    }
                }
                DetailedRouteMatch::NotFound => {}
            }
        }

        if let Some(action) =
            self.dispatch_registered_http_routes(py, &path, &root_path, &method, earlier_fallback)?
        {
            return Ok(action);
        }
        if let Some(action) = self.redirect_http_slash(py, &path, &root_path, &method)? {
            return Ok(action);
        }
        if let Some(action) = self.dispatch_frontend_route(py, &route_path, &method)? {
            return Ok(action);
        }
        if let Some(default) = self
            .router_default
            .as_ref()
            .map(|default| default.clone_ref(py))
        {
            return self.dispatch_router_default(py, default);
        }
        let exception = py
            .import("starlette.exceptions")?
            .getattr("HTTPException")?
            .call1((404,))?;
        Err(PyErr::from_value(exception))
    }

    fn begin_websocket(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        refresh_included_router_routes(py, &self.app)?;
        let scope = self.scope.bind(py);
        let path = parse_scope_string(scope, "path", "/")?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let constructor_matches = self.match_constructor_route(py, scope)?;
        if let Some(matched) = constructor_matches.full {
            return self.handle_constructor_route(py, matched.route, matched.child_scope);
        }
        let selected_api_route = match self
            .app
            .bind(py)
            .borrow()
            .websocket_router
            .matches(&path, &root_path, "GET")
        {
            FastApiOperationMatch::Matched {
                operation_index,
                path_params,
            } => Some((operation_index, path_params)),
            FastApiOperationMatch::MethodNotAllowed { .. } | FastApiOperationMatch::NotFound => {
                None
            }
        };
        let candidates =
            collect_websocket_dispatch_candidates(py, &self.app, false, "", &mut HashSet::new())?;
        let full_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("FULL")?;
        let partial_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("PARTIAL")?;
        let mut earlier_fallback = constructor_matches
            .partial
            .map(|matched| (matched.route, matched.child_scope));

        for candidate in candidates {
            match candidate {
                WebSocketDispatchCandidate::ApiWebSocketRoute(route_index) => {
                    if let Some((selected_index, path_params)) = &selected_api_route {
                        if *selected_index == route_index {
                            return self.begin_fastapi_websocket_route(
                                py,
                                route_index,
                                &path,
                                &root_path,
                                path_params.clone(),
                            );
                        }
                    }
                }
                WebSocketDispatchCandidate::StarletteRoute(route) => {
                    let match_result = route.bind(py).call_method1("matches", (scope,))?;
                    let route_match = match_result.get_item(0)?;
                    let child_scope = match_result.get_item(1)?.unbind();
                    if route_match.is(&partial_match) && earlier_fallback.is_none() {
                        earlier_fallback = Some((route.clone_ref(py), child_scope.clone_ref(py)));
                    }
                    if route_match.is(&full_match) {
                        return self.handle_constructor_route(py, route, child_scope);
                    }
                }
            }
        }

        if let Some((route, child_scope)) = earlier_fallback {
            return self.handle_constructor_route(py, route, child_scope);
        }
        if selected_api_route.is_some() {
            return Err(PyRuntimeError::new_err(
                "selected FastAPI WebSocket route is missing from dispatch order",
            ));
        }
        match self
            .router_default
            .as_ref()
            .map(|default| default.clone_ref(py))
        {
            Some(default) => self.dispatch_router_default(py, default),
            None => self.close_unmatched_websocket(py),
        }
    }

    fn begin_fastapi_websocket_route(
        &mut self,
        py: Python<'_>,
        operation_index: usize,
        path: &str,
        root_path: &str,
        path_params: Vec<(String, String)>,
    ) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let full_match = py
            .import("starlette.routing")?
            .getattr("Match")?
            .getattr("FULL")?;
        let (raw_route, route_scope) = {
            let app = self.app.bind(py).borrow();
            let route = app.websocket_routes.get(operation_index).ok_or_else(|| {
                PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
            })?;
            (route.raw, route.route_scope.clone_ref(py))
        };
        if raw_route {
            let match_result = route_scope.bind(py).call_method1("matches", (scope,))?;
            if !match_result.get_item(0)?.is(&full_match) {
                return self.close_unmatched_websocket(py);
            }
            return self.handle_constructor_route(
                py,
                route_scope,
                match_result.get_item(1)?.unbind(),
            );
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
                .resolve_inputs(path, root_path, "GET", &query, headers, &[])
        };
        let websocket_type = py.import("starlette.websockets")?.getattr("WebSocket")?;
        self.websocket = Some(
            websocket_type
                .call1((scope, self.receive.bind(py), self.send.bind(py)))?
                .unbind(),
        );
        let values = match decode_input_values(py, inputs, false) {
            Ok(values) => values.values,
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

    fn dispatch_router_default(
        &mut self,
        py: Python<'_>,
        default: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let awaitable = default.bind(py).call1((
            self.scope.bind(py),
            self.receive.bind(py),
            self.send.bind(py),
        ))?;
        self.pending = Some(PendingAction::MountedApp);
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
            let validation_exception_type =
                crate::errors::websocket_request_validation_error_type(py);
            if !value.is_instance(&validation_exception_type)? {
                return Err(error);
            }
        }
        let websocket = self
            .websocket
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("FastAPI WebSocket was not initialized"))?;
        let awaitable = if value.is_instance(&exception_type)? {
            websocket
                .bind(py)
                .call_method1("close", (value.getattr("code")?, value.getattr("reason")?))?
        } else {
            let errors = value.call_method0("errors")?;
            let reason = jsonable_encoder_default(py, &errors)?;
            websocket
                .bind(py)
                .call_method1("close", (1008_u16, reason))?
        };
        if !is_awaitable(py, &awaitable)? {
            return Err(PyTypeError::new_err(
                "Starlette WebSocket.close must return an awaitable",
            ));
        }
        self.pending = Some(PendingAction::WebSocketClose);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn registered_websocket_exception_handler(
        &self,
        py: Python<'_>,
        error: &PyErr,
    ) -> PyResult<Option<Py<PyAny>>> {
        let handlers = self.app.bind(py).borrow().exception_handlers.clone_ref(py);
        let handlers = handlers.bind(py).cast::<PyDict>()?;
        let value = error.value(py);
        let http_exception_type = py
            .import("starlette.exceptions")?
            .getattr("HTTPException")?;
        if value.is_instance(&http_exception_type)? {
            let status_code = value.getattr("status_code")?;
            if let Some(handler) = handlers.get_item(status_code)? {
                return Ok(Some(handler.unbind()));
            }
        }

        let exception_type = error.get_type(py);
        let exception_mro = exception_type.getattr("__mro__")?.cast_into::<PyTuple>()?;
        let server_error_type = py.get_type::<PyException>();
        for class in exception_mro.iter() {
            if class.is(&server_error_type) {
                break;
            }
            if let Some(handler) = handlers.get_item(class)? {
                return Ok(Some(handler.unbind()));
            }
        }
        Ok(None)
    }

    fn invoke_websocket_exception_handler(
        &mut self,
        py: Python<'_>,
        handler: Py<PyAny>,
        error: &PyErr,
    ) -> PyResult<MachineAction> {
        let websocket = self
            .websocket
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("FastAPI WebSocket was not initialized"))?;
        let handler = handler.bind(py);
        let websocket = websocket.bind(py);
        let exception = error.value(py);
        let inspect = py.import("inspect")?;
        let iscoroutinefunction = inspect.getattr("iscoroutinefunction")?;
        let is_async = iscoroutinefunction.call1((handler,))?.extract::<bool>()?
            || (py
                .import("builtins")?
                .getattr("callable")?
                .call1((handler,))?
                .extract::<bool>()?
                && iscoroutinefunction
                    .call1((handler.getattr("__call__")?,))?
                    .extract::<bool>()?);
        let native_websocket_validation_handler = handler
            .is_instance(&py.get_type::<PyFastApiWebSocketRequestValidationExceptionHandler>())?;
        let awaitable = if is_async || native_websocket_validation_handler {
            handler.call1((websocket, exception))?
        } else {
            py.import("starlette.concurrency")?
                .getattr("run_in_threadpool")?
                .call1((handler, websocket, exception))?
        };
        self.pending = Some(PendingAction::WebSocketExceptionHandler);
        Ok(MachineAction::Await(awaitable.unbind()))
    }

    fn websocket_exception_handler_resumed(
        &mut self,
        py: Python<'_>,
        response: Py<PyAny>,
    ) -> PyResult<MachineAction> {
        let response = response.bind(py);
        if response.is_none() {
            return self.close_form_after_response(py);
        }
        let awaitable = response.call1((
            self.scope.bind(py),
            self.receive.bind(py),
            self.send.bind(py),
        ))?;
        self.pending = Some(PendingAction::WebSocketExceptionResponse);
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
        self.form_request = Some(request.clone().unbind());
        self.pending = Some(PendingAction::FormParse);
        #[cfg(feature = "fault-injection")]
        if crate::fault_injection::take_http_request_form_parse_before() {
            return Ok(MachineAction::Raise(PyRuntimeError::new_err(
                "Fault injected at http.request.form_parse.before",
            )));
        }
        let form_awaitable = request.call_method0("form")?;
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
        let decoded = match decode_input_values(py, inputs, parse_json_body) {
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
                if self.forced_route_index.is_some() {
                    return Err(validation_error);
                }
                if self.has_registered_exception_handler(py, &validation_error)? {
                    return self.route_exception(py, validation_error);
                }
                self.response_status = 422;
                self.response_body = json_bytes(py, response_body.bind(py))?;
                return self.send_start(py);
            }
            Err(InputDecodeError::BodyParse(_error)) => {
                if self.forced_route_index.is_some() {
                    let kwargs = PyDict::new(py);
                    kwargs.set_item("status_code", 400)?;
                    kwargs.set_item("detail", "There was an error parsing the body")?;
                    let exception = py
                        .import("starlette.exceptions")?
                        .getattr("HTTPException")?
                        .call((), Some(&kwargs))?;
                    return Err(PyErr::from_value(exception));
                }
                self.response_status = 400;
                self.response_body = json_bytes(py, bad_request_body_response_body(py)?.bind(py))?;
                return self.send_start(py);
            }
            Err(InputDecodeError::Other(error)) => return Err(error),
        };
        let (dependency_exit_stack, function_dependency_exit_stack) =
            route_handler_exit_stacks(py, scope)?;
        self.invocation = Some(RequestInvocation {
            inputs: decoded.values,
            query_params,
            request_body: decoded.request_body,
            form_body_embedded: false,
            failures: Vec::new(),
            dependency_cache: HashMap::new(),
            prepared_dependency_values: HashMap::new(),
            dependency_override_cursor: 0,
            dependency_exit_stack,
            dependency_exit_stack_closed: false,
            function_dependency_exit_stack,
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
            Ok(values) => values.values,
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
            let (dependency_exit_stack, function_dependency_exit_stack) =
                route_handler_exit_stacks(py, self.scope.bind(py))?;
            self.invocation = Some(RequestInvocation {
                inputs,
                query_params,
                request_body: self.form_body.take(),
                form_body_embedded: self.form_body_embedded,
                failures: Vec::new(),
                dependency_cache: HashMap::new(),
                prepared_dependency_values: HashMap::new(),
                dependency_override_cursor: 0,
                dependency_exit_stack,
                dependency_exit_stack_closed: false,
                function_dependency_exit_stack,
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

    fn dependency_overrides_provider(&self, py: Python<'_>) -> Py<PyAny> {
        self.route_dependency_overrides_provider
            .as_ref()
            .map(|provider| provider.clone_ref(py))
            .unwrap_or_else(|| self.app.clone_ref(py).into_any())
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
        #[cfg(feature = "fault-injection")]
        if self.route_index.is_some()
            && self.websocket_route_index.is_none()
            && self.frontend_route_index.is_none()
            && crate::fault_injection::take_http_route_invoke_before()
        {
            return Err(PyRuntimeError::new_err(
                "Fault injected at http.route.invoke.before",
            ));
        }
        let websocket = self.websocket.as_ref().map(|socket| socket.bind(py));
        let request = self.request.as_ref().map(|request| request.bind(py));
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.bind(py));
        let dependency_overrides_provider = self.dependency_overrides_provider(py);
        let invocation = self
            .invocation
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("request invocation state was lost"))?;
        let (plan, ordinary_http_endpoint, use_endpoint_threadpool) = {
            let app = self.app.bind(py).borrow();
            if let Some(route_index) = self.frontend_route_index {
                let plan = &app
                    .frontend_routes
                    .get(route_index)
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI frontend was lost"))?
                    .dependency_plan;
                (plan.clone_ref(py), false, false)
            } else if let Some(route_index) = self.websocket_route_index {
                let plan = app
                    .websocket_routes
                    .get(route_index)
                    .ok_or_else(|| {
                        PyRuntimeError::new_err("selected FastAPI WebSocket route was lost")
                    })?
                    .plan
                    .as_ref()
                    .ok_or_else(|| {
                        PyRuntimeError::new_err("raw WebSocket route entered FastAPI")
                    })?;
                (plan.clone_ref(py), false, false)
            } else {
                let route_index = self.route_index.ok_or_else(|| {
                    PyRuntimeError::new_err("ASGI dispatch has no selected HTTP route")
                })?;
                let route = app
                    .routes
                    .get(route_index)
                    .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
                let ordinary = !route.generator_kind.is_generator();
                (
                    route.plan.clone_ref(py),
                    ordinary,
                    ordinary && !route.endpoint_is_coroutine,
                )
            }
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
                dependency_overrides_provider: &dependency_overrides_provider,
                dependency_cache: &mut invocation.dependency_cache,
                prepared_dependency_values: &mut invocation.prepared_dependency_values,
                dependency_override_cursor: &mut invocation.dependency_override_cursor,
                dependency_exit_stack: invocation.dependency_exit_stack.bind(py),
                function_dependency_exit_stack: invocation.function_dependency_exit_stack.bind(py),
                background_tasks: &mut invocation.background_tasks,
            };
            match plan.prepare_dependencies(&mut context)? {
                DependencyPreparation::AwaitDependencyGraph { awaitable, graph } => {
                    RouteInvocation::AwaitDependencyGraph { awaitable, graph }
                }
                DependencyPreparation::Invalid => {
                    // Recursive dependency errors do not prevent the source
                    // solver from collecting the endpoint's own input errors.
                    // The empty explicit map prevents failed child reinvocation.
                    plan.prepare_arguments(&mut context, Some(&HashMap::new()))?;
                    RouteInvocation::Ready(None)
                }
                DependencyPreparation::Ready => {
                    #[cfg(feature = "fault-injection")]
                    if self.route_index.is_some()
                        && self.websocket_route_index.is_none()
                        && self.frontend_route_index.is_none()
                        && crate::fault_injection::take_http_route_invoke_after_dependencies_before(
                        )
                    {
                        return Err(PyRuntimeError::new_err(
                            "Fault injected at http.route.invoke.after_dependencies.before",
                        ));
                    }
                    let result = if ordinary_http_endpoint {
                        // Argument validation remains on the caller loop. Only
                        // the prepared ordinary sync callable enters a worker.
                        match plan.prepare_arguments(&mut context, None)? {
                            Some(arguments) => Some(plan.call_with_arguments(
                                &context,
                                arguments.bind(py),
                                use_endpoint_threadpool,
                            )?),
                            None => None,
                        }
                    } else {
                        plan.invoke(&mut context, None, None)?
                    };
                    RouteInvocation::Ready(result)
                }
            }
        };
        match route_invocation {
            RouteInvocation::AwaitDependencyGraph { awaitable, graph } => {
                self.pending = Some(PendingAction::DependencyGraph(graph));
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
                    if ordinary_http_endpoint || is_awaitable(py, endpoint_result.bind(py))? {
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
                        let endpoint_ctx = self.websocket_validation_endpoint_context(py)?;
                        let error = crate::errors::websocket_request_validation_error(
                            py,
                            &failures,
                            Some(&endpoint_ctx),
                        )?;
                        return self.route_exception(py, error);
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
                    if self.forced_route_index.is_some() {
                        return self.route_exception(py, error);
                    }
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
        let dependency_overrides_provider = self.dependency_overrides_provider(py);
        let route_body_fields_embedded = self.selected_body_fields_embedded(py)?;
        let advance = {
            let invocation = self
                .invocation
                .as_mut()
                .ok_or_else(|| PyRuntimeError::new_err("request invocation state was lost"))?;
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
                dependency_overrides_provider: &dependency_overrides_provider,
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

        let request_method = parse_scope_string(self.scope.bind(py), "method", "GET")?;
        let (generator_kind, response_class, sse_stream, status_code, stream_item_config) = {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(self.route_index.unwrap_or_default())
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            let config = route
                .stream_item_type
                .as_ref()
                .map(|annotation| StreamItemConfig {
                    annotation: annotation.clone_ref(py),
                    include: route
                        .response_model_include
                        .as_ref()
                        .map(|value| value.clone_ref(py)),
                    exclude: route
                        .response_model_exclude
                        .as_ref()
                        .map(|value| value.clone_ref(py)),
                    by_alias: route.response_model_by_alias,
                    exclude_unset: route.response_model_exclude_unset,
                    exclude_defaults: route.response_model_exclude_defaults,
                    exclude_none: route.response_model_exclude_none,
                    endpoint: route.endpoint.clone_ref(py),
                    method: request_method.clone(),
                    path: route.path.clone(),
                });
            let response_class = self
                .response_class_override
                .as_ref()
                .map(|value| ResponseClassChoice::from_python(py, value.clone_ref(py)))
                .unwrap_or_else(|| route.response_class.clone_ref(py));
            let sse_stream = if self.response_class_override.is_some() {
                included_route_sse_stream(py, route.generator_kind, &response_class)?
            } else {
                route.sse_stream
            };
            (
                route.generator_kind,
                response_class,
                sse_stream,
                route.status_code,
                config,
            )
        };
        // Stream lifetime remains a separate slice, but its schema callbacks
        // also execute outside application borrows.
        let stream_serializer = if let Some(stream_item) = stream_item_config {
            let adapter = py
                .import("pydantic")?
                .getattr("TypeAdapter")?
                .call1((stream_item.annotation.bind(py),))?
                .unbind();
            let validation_kwargs = PyDict::new(py);
            validation_kwargs.set_item("from_attributes", true)?;
            let serialization_kwargs = PyDict::new(py);
            serialization_kwargs.set_item("by_alias", stream_item.by_alias)?;
            serialization_kwargs.set_item("exclude_unset", stream_item.exclude_unset)?;
            serialization_kwargs.set_item("exclude_defaults", stream_item.exclude_defaults)?;
            serialization_kwargs.set_item("exclude_none", stream_item.exclude_none)?;
            if let Some(include) = stream_item.include.as_ref() {
                serialization_kwargs.set_item("include", include.bind(py))?;
            } else {
                serialization_kwargs.set_item("include", py.None())?;
            }
            if let Some(exclude) = stream_item.exclude.as_ref() {
                serialization_kwargs.set_item("exclude", exclude.bind(py))?;
            } else {
                serialization_kwargs.set_item("exclude", py.None())?;
            }
            let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
            let endpoint_context = response_endpoint_context(
                py,
                stream_item.endpoint.bind(py),
                &stream_item.method,
                &stream_item.path,
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
            let json_lines = response_class.is_default() && !sse_stream;
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
            let mut sse_stream_for_setup = None;
            let stream = if sse_stream {
                let stream = Py::new(py, PyFastApiSseKeepaliveStream::new(stream.into_any()))?;
                let request_exit_stack = if let Some(invocation) = self.invocation.as_ref() {
                    invocation.dependency_exit_stack.clone_ref(py)
                } else {
                    route_handler_exit_stacks(py, self.scope.bind(py))?.0
                };
                let close = stream.bind(py).getattr("aclose")?;
                request_exit_stack
                    .bind(py)
                    .call_method1("push_async_callback", (close,))?;
                sse_stream_for_setup = Some(stream.clone_ref(py));
                stream.into_any()
            } else {
                stream.into_any()
            };
            let response_class = if sse_stream {
                py.import("starlette.responses")?
                    .getattr("StreamingResponse")?
                    .unbind()
            } else {
                if response_class.is_default() {
                    py.import("starlette.responses")?
                        .getattr("StreamingResponse")?
                        .unbind()
                } else {
                    response_class.actual(py)?
                }
            };
            let kwargs = PyDict::new(py);
            kwargs.set_item("content", stream.bind(py))?;
            if let Some(status_code) = response_status_override(status_code) {
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
                let is_streaming_response = response_class.bind(py).is_instance_of::<PyType>()
                    && py
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
            if let Some(stream) = sse_stream_for_setup {
                self.sse_setup_response = Some(response.clone().unbind());
                self.pending = Some(PendingAction::SseStreamSetup);
                let setup = stream.bind(py).call_method0("start")?.unbind();
                return Ok(MachineAction::Await(setup));
            }
            return self.start_returned_response(py, &response);
        }

        let response_model = {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(self.route_index.unwrap_or_default())
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            route
                .response_field
                .field(py)?
                .map(|field| ResponseModelConfig {
                    field,
                    include: route
                        .response_model_include
                        .as_ref()
                        .map(|value| value.clone_ref(py)),
                    exclude: route
                        .response_model_exclude
                        .as_ref()
                        .map(|value| value.clone_ref(py)),
                    by_alias: route.response_model_by_alias,
                    exclude_unset: route.response_model_exclude_unset,
                    exclude_defaults: route.response_model_exclude_defaults,
                    exclude_none: route.response_model_exclude_none,
                    endpoint_is_coroutine: route.endpoint_is_coroutine,
                    endpoint: route.endpoint.clone_ref(py),
                    method: request_method,
                    path: route.path.clone(),
                })
        };
        let Some(response_model) = response_model else {
            let response_value = jsonable_encoder_default(py, result.bind(py))?.unbind();
            return self.finish_serialized_response(
                py,
                response_value,
                response_class,
                status_code,
            );
        };
        // The route owns one retained adapter. No app borrow survives user
        // validation or serialization; original endpoint scheduling is preserved.
        let adapter = response_model.field.adapter.clone_ref(py);
        let kwargs = PyDict::new(py);
        kwargs.set_item("by_alias", response_model.by_alias)?;
        kwargs.set_item("exclude_unset", response_model.exclude_unset)?;
        kwargs.set_item("exclude_defaults", response_model.exclude_defaults)?;
        kwargs.set_item("exclude_none", response_model.exclude_none)?;
        kwargs.set_item(
            "include",
            response_model.include.as_ref().map(|value| value.bind(py)),
        )?;
        kwargs.set_item(
            "exclude",
            response_model.exclude.as_ref().map(|value| value.bind(py)),
        )?;
        let state = ResponseValidationState {
            adapter,
            original_content: result,
            serialization_kwargs: kwargs.unbind(),
            response_class,
            status_code,
            endpoint: response_model.endpoint,
            method: response_model.method,
            path: response_model.path,
        };
        let validator = ResponseModelValidator {
            adapter: state.adapter.clone_ref(py),
        };
        if response_model.endpoint_is_coroutine {
            let (validated, errors) = validator.validate(py, state.original_content.bind(py))?;
            return self.finish_response_validation(py, state, validated, errors);
        }
        let validator = Py::new(py, validator)?;
        let awaitable = py
            .import("starlette.concurrency")?
            .getattr("run_in_threadpool")?
            .call1((validator, state.original_content.bind(py)))?
            .unbind();
        self.pending = Some(PendingAction::ResponseValidation(Box::new(state)));
        Ok(MachineAction::Await(awaitable))
    }

    fn finish_response_validation(
        &mut self,
        py: Python<'_>,
        state: ResponseValidationState,
        validated: Py<PyAny>,
        errors: Py<PyList>,
    ) -> PyResult<MachineAction> {
        if !errors.bind(py).is_empty() {
            let root_path = parse_scope_string(self.scope.bind(py), "root_path", "")?;
            let endpoint_ctx = response_endpoint_context(
                py,
                state.endpoint.bind(py),
                &state.method,
                &state.path,
                &root_path,
            )?;
            let kwargs = PyDict::new(py);
            kwargs.set_item("body", state.original_content.bind(py))?;
            kwargs.set_item("endpoint_ctx", endpoint_ctx)?;
            let exception = py
                .get_type::<crate::errors::ResponseValidationError>()
                .call((errors.bind(py),), Some(&kwargs))?;
            return Err(PyErr::from_value(exception));
        }
        // Only retained placeholder provenance permits direct byte serialization.
        if state.response_class.is_default() {
            let body = state
                .adapter
                .bind(py)
                .call_method(
                    "dump_json",
                    (validated.bind(py),),
                    Some(state.serialization_kwargs.bind(py)),
                )?
                .extract::<Vec<u8>>()?;
            self.response_status = response_status_override(state.status_code).unwrap_or(200);
            self.response_body = if state.status_code == Some(204) {
                Vec::new()
            } else {
                body
            };
            if self.route_handler_response {
                return self.finish_serialized_body_response(
                    py,
                    &self.response_body.clone(),
                    state.status_code,
                );
            }
            return self.send_start_with_injected_response_headers(py);
        }
        state
            .serialization_kwargs
            .bind(py)
            .set_item("mode", "json")?;
        let response_value = state
            .adapter
            .bind(py)
            .call_method(
                "dump_python",
                (validated.bind(py),),
                Some(state.serialization_kwargs.bind(py)),
            )?
            .unbind();
        self.finish_serialized_response(py, response_value, state.response_class, state.status_code)
    }

    fn finish_serialized_body_response(
        &mut self,
        py: Python<'_>,
        body: &[u8],
        status_code: Option<u16>,
    ) -> PyResult<MachineAction> {
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.bind(py));
        let kwargs = PyDict::new(py);
        if let Some(status_code) = response_status_override(status_code) {
            kwargs.set_item("status_code", status_code)?;
        }
        kwargs.set_item("media_type", "application/json")?;
        let background_tasks = self.request_background_tasks(py);
        kwargs.set_item(
            "background",
            background_tasks.as_ref().map(|tasks| tasks.bind(py)),
        )?;
        let response = py
            .import("starlette.responses")?
            .getattr("Response")?
            .call((PyBytes::new(py, body),), Some(&kwargs))?;
        let response_status_code = response.getattr("status_code")?.extract::<i64>()?;
        if response_status_code < 200 || matches!(response_status_code, 204 | 205 | 304) {
            response.setattr("body", PyBytes::new(py, b""))?;
        }
        merge_injected_response_state(py, &response, injected_response)?;
        self.start_returned_response(py, &response)
    }

    fn finish_serialized_response(
        &mut self,
        py: Python<'_>,
        response_value: Py<PyAny>,
        response_class: ResponseClassChoice,
        status_code: Option<u16>,
    ) -> PyResult<MachineAction> {
        let injected_response = self
            .injected_response
            .as_ref()
            .map(|response| response.bind(py));
        // Without eligible field bytes, source calls the actual selected value,
        // including explicit None. Placeholder provenance does not skip that call.
        let response_class = response_class.actual(py)?;
        let kwargs = PyDict::new(py);
        if let Some(status_code) = response_status_override(status_code) {
            kwargs.set_item("status_code", status_code)?;
        }
        let background_tasks = self.request_background_tasks(py);
        kwargs.set_item(
            "background",
            background_tasks.as_ref().map(|tasks| tasks.bind(py)),
        )?;
        let response = response_class
            .bind(py)
            .call((response_value.bind(py),), Some(&kwargs))?;
        merge_injected_response_state(py, &response, injected_response)?;
        let response_status_code = response.getattr("status_code")?.extract::<i64>()?;
        if response_status_code < 200 || matches!(response_status_code, 204 | 205 | 304) {
            response.setattr("body", PyBytes::new(py, b""))?;
        }
        self.start_returned_response(py, &response)
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
        let body: &[u8] =
            if self.response_status < 200 || matches!(self.response_status, 204 | 205 | 304) {
                &[]
            } else {
                &self.response_body
            };
        response_body(py, self.send.bind(py), body).map(MachineAction::Await)
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
        let body = PyDict::new(py);
        if error.matches(py, &multipart_exception)? {
            body.set_item("detail", value.getattr("message")?)?;
        } else {
            let exception = py.import("builtins")?.getattr("Exception")?;
            if !error.matches(py, &exception)? {
                return Err(error);
            }
            body.set_item("detail", "There was an error parsing the body")?;
        }
        self.response_status = 400;
        if self.route_handler_response {
            let kwargs = PyDict::new(py);
            kwargs.set_item("status_code", 400)?;
            let response = py
                .import("starlette.responses")?
                .getattr("JSONResponse")?
                .call((body,), Some(&kwargs))?;
            return self.start_returned_response(py, &response);
        }
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
        if self.route_handler_response {
            return Err(error);
        }
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
            if let Some(handler) = self.registered_websocket_exception_handler(py, &error)? {
                return self.invoke_websocket_exception_handler(py, handler, &error);
            }
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
        if let Some(cleanup) = self.route_handler_cleanup.as_ref() {
            let cleanup = cleanup.clone_ref(py);
            self.pending = Some(PendingAction::RouteHandlerRequestCleanupAfterResponse);
            let awaitable = into_python_awaitable(
                py,
                RouteHandlerCleanupCall::new(cleanup, RouteHandlerCleanupMode::RequestSuccess, py),
            )?;
            return Ok(MachineAction::Await(awaitable));
        }
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
                Some(PendingAction::WebSocketExceptionHandler) => {
                    self.websocket_exception_handler_resumed(py, value)
                }
                Some(PendingAction::WebSocketExceptionResponse) => {
                    self.close_form_after_response(py)
                }
                Some(PendingAction::MountedApp) => Ok(MachineAction::Complete(py.None())),
                Some(PendingAction::FrontendConfig) => self.get_frontend_response(py, None),
                Some(PendingAction::FrontendResponse) => self.finish_frontend_response(py, value),
                Some(PendingAction::FrontendAsgiResponse) => self.close_form_after_response(py),
                Some(PendingAction::Endpoint) => self.finish_endpoint(py, value),
                Some(PendingAction::SseStreamSetup) => {
                    let response = self.sse_setup_response.take().ok_or_else(|| {
                        PyRuntimeError::new_err("SSE response setup resumed without a response")
                    })?;
                    self.start_returned_response(py, response.bind(py))
                }
                Some(PendingAction::CustomRouteHandler) => {
                    self.begin_custom_route_response(py, value)
                }
                Some(PendingAction::RouteHandlerFunctionCleanupBeforeResponse) => {
                    let continuation =
                        self.function_close_continuation.take().ok_or_else(|| {
                            PyRuntimeError::new_err(
                                "route handler function cleanup resumed without a response",
                            )
                        })?;
                    self.resume_function_close_continuation(py, continuation)
                }
                Some(PendingAction::RouteHandlerRequestCleanupAfterResponse) => {
                    self.route_handler_cleanup = None;
                    Ok(MachineAction::Complete(py.None()))
                }
                Some(PendingAction::RouteHandlerCleanupAfterError(error)) => Err(error),
                Some(PendingAction::ResponseValidation(state)) => {
                    let outcome = value.bind(py).cast::<PyTuple>()?;
                    let validated = outcome.get_item(0)?.unbind();
                    let errors = outcome.get_item(1)?.cast_into::<PyList>()?.unbind();
                    self.finish_response_validation(py, *state, validated, errors)
                }
                Some(PendingAction::DependencyGraph(graph)) => {
                    self.dependency_graph_resumed(py, *graph, value)
                }
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
                    PendingAction::WebSocketExceptionHandler
                    | PendingAction::WebSocketExceptionResponse,
                ) => Err(error),
                Some(
                    PendingAction::WebSocketEndpoint
                    | PendingAction::WebSocketClose
                    | PendingAction::RouteInvocation
                    | PendingAction::Endpoint
                    | PendingAction::ResponseValidation(_)
                    | PendingAction::FrontendConfig
                    | PendingAction::FrontendAsgiResponse
                    | PendingAction::FunctionDependencyCloseBeforeResponse
                    | PendingAction::FunctionDependencyCloseAfterResponse
                    | PendingAction::SendStart
                    | PendingAction::SendBody
                    | PendingAction::BackgroundTasks
                    | PendingAction::DependencyGraph(_),
                ) => self.route_exception(py, error),
                Some(PendingAction::ReturnedResponse) => {
                    self.begin_route_handler_cleanup_error(py, error, false)
                }
                Some(PendingAction::CustomRouteHandler) => {
                    self.begin_route_handler_cleanup_error(py, error, true)
                }
                Some(
                    PendingAction::RouteHandlerFunctionCleanupBeforeResponse
                    | PendingAction::RouteHandlerRequestCleanupAfterResponse,
                ) => self.begin_route_handler_cleanup_error(py, error, false),
                Some(PendingAction::RouteHandlerCleanupAfterError(_)) => Err(error),
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
            Err(error) if self.route_handler_response => {
                self.defer_route_handler_cleanup(py)?;
                Err(error)
            }
            Err(error) if self.route_handler_cleanup.is_some() => {
                self.begin_route_handler_cleanup_error(py, error, false)
            }
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
    let native_task_adapter = PyModule::from_code(
        module.py(),
        c"async def _run_native_task(awaitable):\n    return await awaitable\n",
        c"<fastapi-rs-native-task-adapter>",
        c"_fastapi_rs_native_task_adapter",
    )?;
    module.add(
        "_run_native_task",
        native_task_adapter.getattr("_run_native_task")?,
    )?;
    crate::lifespan::register(module)?;
    register_pydantic_schema_generator(module)?;
    let generate_unique_id = wrap_pyfunction!(generate_unique_id, module)?.into_any();
    generate_unique_id.setattr("__module__", "fastapi.utils")?;
    module.add("_generate_unique_id", &generate_unique_id)?;
    module.add_function(wrap_pyfunction!(frontend_dependency_endpoint, module)?)?;
    module.add_class::<PyFastApiDefaultPlaceholder>()?;
    module.add_class::<PyOperationRouteDescriptor>()?;
    module.add_class::<PyOperationRouteCallable>()?;
    module.add_class::<PyFastApi>()?;
    module.add_class::<PyFastApiAsgiApp>()?;
    module.add_class::<PyApiRouteAsgiApp>()?;
    module.add_class::<PyApiRouteAsgiCore>()?;
    module.add_class::<PyFastApiRouteHandler>()?;
    module.add_class::<PyFastApiRequestCleanup>()?;
    module.add_class::<PyMiddlewareDecorator>()?;
    module.add_class::<PyFastApiHttpMiddleware>()?;
    module.add_class::<PyFastApiCachedReceiveDescriptor>()?;
    module.add_class::<PyFastApiCachedReceive>()?;
    module.add_class::<PyFastApiMessageCapture>()?;
    module.add_class::<PyFastApiTelemetrySend>()?;
    module.add_class::<PyFastApiHttpExceptionHandler>()?;
    module.add_class::<PyFastApiRequestValidationExceptionHandler>()?;
    let py = module.py();
    let http_exception_handler = Py::new(py, PyFastApiHttpExceptionHandler)?.into_any();
    let request_type = py.import("starlette.requests")?.getattr("Request")?;
    let http_exception_type = py
        .import("starlette.exceptions")?
        .getattr("HTTPException")?;
    let response_type = py.import("starlette.responses")?.getattr("Response")?;
    install_exception_handler_metadata(
        py,
        http_exception_handler.bind(py),
        "http_exception_handler",
        [("request", &request_type), ("exc", &http_exception_type)],
        &response_type,
    )?;
    module.add("http_exception_handler", http_exception_handler)?;

    let request_validation_exception_handler =
        Py::new(py, PyFastApiRequestValidationExceptionHandler)?.into_any();
    let request_validation_exception_type = crate::errors::request_validation_error_type(py);
    let json_response_type = py.import("starlette.responses")?.getattr("JSONResponse")?;
    install_exception_handler_metadata(
        py,
        request_validation_exception_handler.bind(py),
        "request_validation_exception_handler",
        [
            ("request", &request_type),
            ("exc", &request_validation_exception_type),
        ],
        &json_response_type,
    )?;
    module.add(
        "request_validation_exception_handler",
        request_validation_exception_handler,
    )?;
    module.add_class::<PyExceptionHandlerDecorator>()?;
    module.add_class::<PyFastApiCallNext>()?;
    module.add_class::<PyApiRouter>()?;
    module.add_class::<PyApiRouteState>()?;
    module.add_class::<PyApiRouteProxyDescriptor>()?;
    module.add_class::<PyBoundApiRouteProxyMember>()?;
    install_api_route_proxy(module.py(), module)?;
    module.add_class::<PyRouteContext>()?;
    module.add_class::<PyFastApiIncludedRouter>()?;
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
    let inc_ex = module.py().import("pydantic.main")?.getattr("IncEx")?;
    module.add("IncEx", &inc_ex)?;
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
    register_deprecated_json_response_helpers(module)?;
    register_ujson_response(module)?;
    register_orjson_response(module)?;
    Ok(())
}

fn install_exception_handler_metadata(
    py: Python<'_>,
    callable: &Bound<'_, PyAny>,
    name: &str,
    parameter_specs: [(&str, &Bound<'_, PyAny>); 2],
    return_type: &Bound<'_, PyAny>,
) -> PyResult<()> {
    callable.setattr("__module__", "fastapi.exception_handlers")?;
    callable.setattr("__name__", name)?;
    callable.setattr("__qualname__", name)?;
    // Python 3.12 needs function-like code flags; calls still enter native __call__.
    let async_code = py
        .import("asyncio")?
        .getattr("sleep")?
        .getattr("__code__")?;
    callable.setattr("__code__", async_code)?;
    callable.setattr("__defaults__", py.None())?;
    callable.setattr("__kwdefaults__", py.None())?;
    let annotations = PyDict::new(py);
    for (parameter_name, annotation) in parameter_specs {
        annotations.set_item(parameter_name, annotation)?;
    }
    annotations.set_item("return", return_type)?;
    callable.setattr("__annotations__", annotations)?;

    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let parameter_kind = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let python_parameters = PyList::empty(py);
    for (parameter_name, annotation) in parameter_specs {
        let kwargs = PyDict::new(py);
        kwargs.set_item("annotation", annotation)?;
        python_parameters
            .append(parameter_type.call((parameter_name, &parameter_kind), Some(&kwargs))?)?;
    }
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", return_type)?;
    let signature = inspect
        .getattr("Signature")?
        .call((python_parameters,), Some(&signature_kwargs))?;
    callable.setattr("__signature__", signature)
}

/// Install source-derived Python introspection signatures after native API types register.
pub(crate) fn register_signatures(module: &Bound<'_, PyModule>) -> PyResult<()> {
    install_route_operation_descriptors(module.py(), module)?;
    install_fastapi_proxy(module.py(), module)
}
