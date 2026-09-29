//! Rust-owned FastAPI application registration and ASGI request flow.

use std::collections::BTreeSet;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList, PyModule, PyTuple};

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};
use crate::encoding::jsonable_encoder_default;
use crate::openapi::{OpenApiOperation, OpenApiParameter, openapi_document};
use crate::{
    FastApiInputLocation, FastApiInputParameter, FastApiOperationMatch, FastApiOperationRouter,
};

#[derive(Clone, Copy, PartialEq, Eq)]
enum InputSource {
    Path,
    Query,
    Header,
    Cookie,
    Body,
}

impl InputSource {
    const fn location(self) -> FastApiInputLocation {
        match self {
            Self::Path => FastApiInputLocation::Path,
            Self::Query => FastApiInputLocation::Query,
            Self::Header => FastApiInputLocation::Header,
            Self::Cookie => FastApiInputLocation::Cookie,
            Self::Body => FastApiInputLocation::Body,
        }
    }

    const fn as_str(self) -> &'static str {
        self.location().as_str()
    }
}

enum ParameterSource {
    Input { source: InputSource, alias: String },
    Dependency(Box<CallablePlan>),
}

struct CallableParameter {
    name: String,
    annotation: Py<PyAny>,
    default: Option<Py<PyAny>>,
    source: ParameterSource,
}

struct CallablePlan {
    callable: Py<PyAny>,
    parameters: Vec<CallableParameter>,
}

struct FastApiRoute {
    path: String,
    method: String,
    status_code: u16,
    endpoint: Py<PyAny>,
    response_model: Option<Py<PyAny>>,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
    plan: CallablePlan,
}

struct ResponseModelOptions {
    include: Option<Py<PyAny>>,
    exclude: Option<Py<PyAny>>,
    by_alias: bool,
    exclude_unset: bool,
    exclude_defaults: bool,
    exclude_none: bool,
}

struct ParameterOpenApiPlan {
    name: String,
    location: String,
    required: bool,
    annotation: Py<PyAny>,
}

#[pyclass(name = "FastAPI", module = "fastapi_rs._core")]
pub(crate) struct PyFastApi {
    title: String,
    version: String,
    openapi_url: String,
    router: FastApiOperationRouter,
    routes: Vec<FastApiRoute>,
}

#[pymethods]
impl PyFastApi {
    #[new]
    #[pyo3(signature = (*, title = "FastAPI", version = "0.1.0", openapi_url = "/openapi.json"))]
    fn new(title: &str, version: &str, openapi_url: &str) -> Self {
        Self {
            title: title.to_owned(),
            version: version.to_owned(),
            openapi_url: openapi_url.to_owned(),
            router: FastApiOperationRouter::new(),
            routes: Vec::new(),
        }
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(signature = (path, *, response_model = None, status_code = 200, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false))]
    fn post(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: u16,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
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
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(signature = (path, *, response_model = None, status_code = 200, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false))]
    fn get(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: u16,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
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
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(signature = (path, *, response_model = None, status_code = 200, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false))]
    fn put(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: u16,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
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
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(signature = (path, *, response_model = None, status_code = 200, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false))]
    fn delete(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: u16,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
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
            },
        )
    }

    // lint-exception: PyO3 needs one Rust argument per FastAPI-compatible keyword.
    #[allow(
        clippy::too_many_arguments,
        reason = "preserve the Python route decorator keyword signature"
    )]
    #[pyo3(signature = (path, *, response_model = None, status_code = 200, response_model_include = None, response_model_exclude = None, response_model_by_alias = true, response_model_exclude_unset = false, response_model_exclude_defaults = false, response_model_exclude_none = false))]
    fn patch(
        slf: Py<Self>,
        py: Python<'_>,
        path: &str,
        response_model: Option<Py<PyAny>>,
        status_code: u16,
        response_model_include: Option<Py<PyAny>>,
        response_model_exclude: Option<Py<PyAny>>,
        response_model_by_alias: bool,
        response_model_exclude_unset: bool,
        response_model_exclude_defaults: bool,
        response_model_exclude_none: bool,
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
            },
        )
    }

    fn openapi(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.openapi_document(py)
    }

    fn __call__(
        slf: Py<Self>,
        py: Python<'_>,
        scope: Py<PyAny>,
        receive: Py<PyAny>,
        send: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            FastApiCall {
                app: slf,
                scope,
                receive,
                send,
                route_index: None,
                path_params: Vec::new(),
                pending: None,
                body: Vec::new(),
                response_status: 200,
                response_body: Vec::new(),
            },
        )
    }
}

impl PyFastApi {
    fn openapi_document(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let operations = self
            .routes
            .iter()
            .map(|route| self.openapi_operation(py, route))
            .collect::<PyResult<Vec<_>>>()?;
        openapi_document(py, &self.title, &self.version, &operations)
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
        let summary = name
            .split('_')
            .filter(|part| !part.is_empty())
            .map(title_case)
            .collect::<Vec<_>>()
            .join(" ");
        let operation_id = operation_id(&name, &route.path, &route.method);
        let parameters = route
            .plan
            .openapi_parameters(py)?
            .into_iter()
            .map(|parameter| {
                let title = if parameter.location == "header" {
                    parameter.name.clone()
                } else {
                    title_case(&parameter.name.replace('_', " "))
                };
                let schema = pydantic_schema(
                    py,
                    parameter.annotation.bind(py),
                    "validation",
                    Some(&title),
                )?;
                Ok(OpenApiParameter {
                    name: parameter.name,
                    location: parameter.location,
                    required: parameter.required,
                    schema,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;

        let direct_body_parameters = route.plan.direct_body_parameters();
        let unique_body_names = direct_body_parameters
            .iter()
            .map(|parameter| parameter.name.as_str())
            .collect::<BTreeSet<_>>();
        let aggregate_body = unique_body_names.len() > 1;
        let (request_model_name, request_schema, request_required) = if aggregate_body {
            let aggregate_name = format!("Body_{operation_id}");
            let aggregate_model =
                aggregate_body_model(py, &aggregate_name, &direct_body_parameters)?;
            let request_schema = pydantic_schema(py, aggregate_model.bind(py), "validation", None)?;
            let request_required = direct_body_parameters
                .iter()
                .any(|parameter| parameter.default.is_none());
            (Some(aggregate_name), Some(request_schema), request_required)
        } else {
            match route.plan.body_parameter() {
                Some(parameter) => (
                    model_name(py, parameter.annotation.bind(py))?,
                    Some(pydantic_schema(
                        py,
                        parameter.annotation.bind(py),
                        "validation",
                        None,
                    )?),
                    parameter.default.is_none(),
                ),
                None => (None, None, false),
            }
        };
        let (response_model_name, response_schema) = match route.response_model.as_ref() {
            Some(model) => (
                model_name(py, model.bind(py))?,
                Some(pydantic_schema(py, model.bind(py), "serialization", None)?),
            ),
            None => (None, None),
        };

        Ok(OpenApiOperation {
            path: route.path.clone(),
            method: route.method.to_ascii_lowercase(),
            summary,
            operation_id,
            status: route.status_code,
            parameters,
            request_model_name,
            request_schema,
            request_required,
            response_model_name,
            response_schema,
        })
    }
}

#[pyclass(name = "_OperationDecorator", module = "fastapi_rs._core", unsendable)]
struct PyOperationDecorator {
    app: Py<PyFastApi>,
    path: String,
    method: String,
    response_model: Option<Py<PyAny>>,
    status_code: u16,
    response_model_include: Option<Py<PyAny>>,
    response_model_exclude: Option<Py<PyAny>>,
    response_model_by_alias: bool,
    response_model_exclude_unset: bool,
    response_model_exclude_defaults: bool,
    response_model_exclude_none: bool,
}

fn operation_decorator(
    app: Py<PyFastApi>,
    py: Python<'_>,
    path: &str,
    method: &str,
    response_model: Option<Py<PyAny>>,
    status_code: u16,
    response_model_options: ResponseModelOptions,
) -> PyResult<Py<PyOperationDecorator>> {
    Py::new(
        py,
        PyOperationDecorator {
            app,
            path: path.to_owned(),
            method: method.to_owned(),
            response_model,
            status_code,
            response_model_include: response_model_options.include,
            response_model_exclude: response_model_options.exclude,
            response_model_by_alias: response_model_options.by_alias,
            response_model_exclude_unset: response_model_options.exclude_unset,
            response_model_exclude_defaults: response_model_options.exclude_defaults,
            response_model_exclude_none: response_model_options.exclude_none,
        },
    )
}

#[pymethods]
impl PyOperationDecorator {
    fn __call__(&self, py: Python<'_>, endpoint: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let path_parameters = path_parameter_names(&self.path);
        let plan = CallablePlan::build(py, endpoint.clone_ref(py), &path_parameters)?;
        let inputs = plan.input_parameters();
        let mut app = self.app.bind(py).borrow_mut();
        let index = app
            .router
            .add_operation(&self.path, &self.method, self.status_code)
            .map_err(|error| PyValueError::new_err(error.to_string()))?;
        app.router
            .set_parameters(index, inputs)
            .ok_or_else(|| PyRuntimeError::new_err("registered FastAPI operation was lost"))?;
        app.routes.push(FastApiRoute {
            path: self.path.clone(),
            method: self.method.clone(),
            status_code: self.status_code,
            endpoint: endpoint.clone_ref(py),
            response_model: self
                .response_model
                .as_ref()
                .map(|model| model.clone_ref(py)),
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
            plan,
        });
        Ok(endpoint)
    }
}

impl CallablePlan {
    fn build(py: Python<'_>, callable: Py<PyAny>, path_parameters: &[String]) -> PyResult<Self> {
        let inspect = py.import("inspect")?;
        let typing = py.import("typing")?;
        let signature = inspect.getattr("signature")?.call1((callable.bind(py),))?;
        let hints_kwargs = PyDict::new(py);
        hints_kwargs.set_item("include_extras", true)?;
        let hints = typing
            .getattr("get_type_hints")?
            .call((callable.bind(py),), Some(&hints_kwargs))?;
        let empty = inspect.getattr("_empty")?;
        let parameters = signature
            .getattr("parameters")?
            .call_method0("values")?
            .try_iter()?
            .map(|item| {
                let item = item?;
                let name = item.getattr("name")?.extract::<String>()?;
                let raw_annotation = item.getattr("annotation")?;
                let annotation = hints
                    .call_method1("get", (&name, &raw_annotation))?
                    .unbind();
                let raw_default = item.getattr("default")?;
                let (annotation, mut metadata) = annotation_parts(py, annotation)?;
                let default_is_body_marker = !raw_default.is(&empty)
                    && raw_default.hasattr("kind")?
                    && raw_default.getattr("kind")?.extract::<String>()? == "body";
                if default_is_body_marker {
                    metadata.push(raw_default.clone().unbind());
                }
                let default = if raw_default.is(&empty) || default_is_body_marker {
                    marker_default(py, &metadata)?
                } else {
                    Some(raw_default.unbind())
                };
                let validated_annotation =
                    constrained_parameter_annotation(py, annotation.bind(py), &metadata)?;
                let source =
                    parameter_source(py, &name, annotation.bind(py), &metadata, path_parameters)?;
                Ok(CallableParameter {
                    name,
                    annotation: validated_annotation,
                    default,
                    source,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        Ok(Self {
            callable,
            parameters,
        })
    }

    fn input_parameters(&self) -> Vec<FastApiInputParameter> {
        self.parameters
            .iter()
            .flat_map(CallableParameter::input_parameters)
            .collect()
    }

    fn body_parameter(&self) -> Option<&CallableParameter> {
        self.parameters
            .iter()
            .find_map(|parameter| match parameter.source {
                ParameterSource::Input {
                    source: InputSource::Body,
                    ..
                } => Some(parameter),
                ParameterSource::Dependency(ref dependency) => dependency.body_parameter(),
                _ => None,
            })
    }

    fn direct_body_parameters(&self) -> Vec<&CallableParameter> {
        self.parameters
            .iter()
            .filter(|parameter| {
                matches!(
                    parameter.source,
                    ParameterSource::Input {
                        source: InputSource::Body,
                        ..
                    }
                )
            })
            .collect()
    }

    fn openapi_parameters(&self, py: Python<'_>) -> PyResult<Vec<ParameterOpenApiPlan>> {
        let mut parameters = Vec::new();
        for parameter in &self.parameters {
            match &parameter.source {
                ParameterSource::Input { source, alias }
                    if !matches!(source, InputSource::Body) =>
                {
                    parameters.push(ParameterOpenApiPlan {
                        name: alias.clone(),
                        location: source.as_str().to_owned(),
                        required: parameter.default.is_none(),
                        annotation: parameter.annotation.clone_ref(py),
                    });
                }
                ParameterSource::Dependency(dependency) => {
                    parameters.extend(dependency.openapi_parameters(py)?);
                }
                ParameterSource::Input { .. } => {}
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

    fn invoke(
        &self,
        py: Python<'_>,
        inputs: &Bound<'_, PyDict>,
        failures: &mut Vec<ValidationIssue>,
    ) -> PyResult<Option<Py<PyAny>>> {
        let initial_failure_count = failures.len();
        let kwargs = PyDict::new(py);
        let aggregate_body = self
            .input_parameters()
            .iter()
            .filter(|parameter| parameter.location == FastApiInputLocation::Body)
            .count()
            > 1;
        for parameter in &self.parameters {
            if let ParameterSource::Dependency(dependency) = &parameter.source {
                if let Some(value) = dependency.invoke(py, inputs, failures)? {
                    kwargs.set_item(&parameter.name, value.bind(py))?;
                }
            }
        }
        for source in [
            InputSource::Path,
            InputSource::Query,
            InputSource::Header,
            InputSource::Cookie,
            InputSource::Body,
        ] {
            for parameter in &self.parameters {
                let ParameterSource::Input {
                    source: parameter_source,
                    alias,
                } = &parameter.source
                else {
                    continue;
                };
                if *parameter_source != source {
                    continue;
                }
                let value = inputs.get_item(&parameter.name)?;
                let value = if *parameter_source == InputSource::Body && aggregate_body {
                    match value {
                        Some(body) if body.is_instance_of::<PyDict>() => {
                            body.cast::<PyDict>()?.get_item(alias)?
                        }
                        value => value,
                    }
                } else {
                    value
                };
                let Some(value) = value else {
                    if let Some(default) = parameter.default.as_ref() {
                        kwargs.set_item(&parameter.name, default.bind(py))?;
                    } else {
                        failures.push(ValidationIssue::Missing {
                            location: source.as_str().to_owned(),
                            alias: alias.clone(),
                            body_field: *parameter_source == InputSource::Body && aggregate_body,
                        });
                    }
                    continue;
                };
                match validate_python_value(py, parameter.annotation.bind(py), &value) {
                    Ok(value) => kwargs.set_item(&parameter.name, value)?,
                    Err(error) if is_pydantic_validation_error(py, &error) => {
                        failures.push(ValidationIssue::Input(Box::new(InputValidationFailure {
                            error,
                            location: source.as_str().to_owned(),
                            alias: alias.clone(),
                            body_field: *parameter_source == InputSource::Body && aggregate_body,
                        })));
                    }
                    Err(error) => return Err(error),
                }
            }
        }
        if failures.len() != initial_failure_count {
            return Ok(None);
        }
        self.callable
            .bind(py)
            .call((), Some(&kwargs))
            .map(Bound::unbind)
            .map(Some)
    }
}

fn marker_default(py: Python<'_>, metadata: &[Py<PyAny>]) -> PyResult<Option<Py<PyAny>>> {
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? {
            continue;
        }
        let kind = marker.getattr("kind")?.extract::<String>()?;
        if kind == "header" || kind == "query" || kind == "cookie" || kind == "body" {
            let default = marker.getattr("default")?;
            if !default.is_none() {
                return Ok(Some(default.unbind()));
            }
        }
    }
    Ok(None)
}

impl CallableParameter {
    fn input_parameters(&self) -> Vec<FastApiInputParameter> {
        match &self.source {
            ParameterSource::Input { source, alias } => vec![FastApiInputParameter {
                name: self.name.clone(),
                alias: alias.clone(),
                location: source.location(),
                required: self.default.is_none(),
            }],
            ParameterSource::Dependency(dependency) => dependency.input_parameters(),
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
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? {
            continue;
        }
        let kind = marker.getattr("kind")?.extract::<String>()?;
        if kind == "depends" {
            let dependency = marker.getattr("dependency")?.unbind();
            let path_names = path_parameters.to_vec();
            return CallablePlan::build(py, dependency, &path_names)
                .map(Box::new)
                .map(ParameterSource::Dependency);
        }
        if kind == "body" {
            return Ok(ParameterSource::Input {
                source: InputSource::Body,
                alias: name.to_owned(),
            });
        }
        if kind == "header" || kind == "query" || kind == "cookie" {
            let alias = marker
                .getattr("alias")?
                .extract::<Option<String>>()?
                .unwrap_or_else(|| {
                    if kind == "header" {
                        name.replace('_', "-")
                    } else {
                        name.to_owned()
                    }
                });
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
    if is_pydantic_model(py, annotation) {
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

fn constrained_parameter_annotation(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    metadata: &[Py<PyAny>],
) -> PyResult<Py<PyAny>> {
    for marker in metadata {
        let marker = marker.bind(py);
        if !marker.hasattr("kind")? {
            continue;
        }
        let kind = marker.getattr("kind")?.extract::<String>()?;
        if kind != "body" && kind != "query" {
            continue;
        }
        let gt = marker.getattr("gt")?;
        if gt.is_none() {
            continue;
        }
        let kwargs = PyDict::new(py);
        kwargs.set_item("gt", gt)?;
        let field = py
            .import("pydantic")?
            .getattr("Field")?
            .call((), Some(&kwargs))?;
        return py
            .import("typing")?
            .getattr("Annotated")?
            .get_item((annotation, field))
            .map(Bound::unbind);
    }
    Ok(annotation.clone().unbind())
}

fn is_pydantic_model(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> bool {
    let result = py
        .import("builtins")
        .and_then(|builtins| builtins.getattr("issubclass"))
        .and_then(|issubclass| {
            let base_model = py.import("pydantic")?.getattr("BaseModel")?;
            issubclass.call1((annotation, base_model))
        })
        .and_then(|result| result.extract::<bool>());
    result.unwrap_or(false)
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
    let path = path.trim_matches('/').replace(['/', '{', '}'], "_");
    format!("{name}_{path}_{}", method.to_ascii_lowercase())
}

fn title_case(value: &str) -> String {
    let mut titled = String::with_capacity(value.len());
    let mut capitalize_next = true;
    for character in value.chars() {
        if capitalize_next {
            titled.extend(character.to_uppercase());
            capitalize_next = false;
        } else if character.is_alphanumeric() {
            titled.extend(character.to_lowercase());
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
        fields.set_item(&parameter.name, (parameter.annotation.bind(py), default))?;
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
    let adapter = py
        .import("pydantic")?
        .getattr("TypeAdapter")?
        .call1((annotation,))?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("mode", mode)?;
    let schema = adapter
        .call_method("json_schema", (), Some(&kwargs))?
        .cast_into::<PyDict>()?;
    if let Some(title) = title {
        schema.set_item("title", title)?;
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

fn is_pydantic_validation_error(py: Python<'_>, error: &PyErr) -> bool {
    py.import("pydantic")
        .and_then(|pydantic| pydantic.getattr("ValidationError"))
        .is_ok_and(|validation_error| {
            error
                .matches(py, &validation_error)
                .is_ok_and(|value| value)
        })
}

fn is_json_decode_error(py: Python<'_>, error: &PyErr) -> bool {
    py.import("json")
        .and_then(|json| json.getattr("JSONDecodeError"))
        .is_ok_and(|decode_error| error.matches(py, &decode_error).is_ok_and(|value| value))
}

fn validation_response_body(py: Python<'_>, failures: &[ValidationIssue]) -> PyResult<Py<PyAny>> {
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
    let result = PyDict::new(py);
    result.set_item("detail", details)?;
    Ok(result.into_any().unbind())
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
            loc.append(failure.alias.as_str())?;
            let field_loc = entry.get_item("loc")?.ok_or_else(|| {
                PyValueError::new_err("Pydantic validation error is missing its location")
            })?;
            for part in field_loc.try_iter()? {
                loc.append(part?)?;
            }
        }
        detail.set_item("loc", loc)?;
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
    detail.set_item("loc", loc)?;
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
    detail.set_item("loc", location)?;
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

fn should_parse_json_body(headers: &[(Vec<u8>, Vec<u8>)]) -> bool {
    let Some((_, value)) = headers
        .iter()
        .find(|(name, _)| name.eq_ignore_ascii_case(b"content-type"))
    else {
        return false;
    };
    let Ok(value) = std::str::from_utf8(value) else {
        return false;
    };
    let media_type = value.split(';').next().unwrap_or_default().trim();
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
) -> PyResult<Py<PyAny>> {
    let headers = PyList::empty(py);
    headers.append((
        PyBytes::new(py, b"content-length"),
        PyBytes::new(py, body.len().to_string().as_bytes()),
    ))?;
    headers.append((
        PyBytes::new(py, b"content-type"),
        PyBytes::new(py, b"application/json"),
    ))?;
    let message = PyDict::new(py);
    message.set_item("type", "http.response.start")?;
    message.set_item("status", status)?;
    message.set_item("headers", headers)?;
    send.call1((message,)).map(Bound::unbind)
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
    Receive,
    LifespanReceive,
    LifespanStartupSend,
    LifespanShutdownSend,
    Endpoint,
    SendStart,
    SendBody,
}

struct FastApiCall {
    app: Py<PyFastApi>,
    scope: Py<PyAny>,
    receive: Py<PyAny>,
    send: Py<PyAny>,
    route_index: Option<usize>,
    path_params: Vec<(String, String)>,
    pending: Option<PendingAction>,
    body: Vec<u8>,
    response_status: u16,
    response_body: Vec<u8>,
}

impl FastApiCall {
    fn begin(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let scope = self.scope.bind(py);
        let scope_type = parse_scope_string(scope, "type", "http")?;
        if scope_type == "lifespan" {
            return self.receive_lifespan(py);
        }
        if scope_type != "http" {
            return Err(PyValueError::new_err(format!(
                "FastAPI-RS currently supports HTTP and lifespan ASGI scopes, not {scope_type:?}"
            )));
        }
        let path = parse_scope_string(scope, "path", "/")?;
        let method = parse_scope_string(scope, "method", "GET")?;
        if path == self.app.bind(py).borrow().openapi_url && method == "GET" {
            let document = self.app.bind(py).borrow().openapi_document(py)?;
            self.response_status = 200;
            self.response_body = json_bytes(py, document.bind(py))?;
            return self.send_start(py);
        }

        let root_path = parse_scope_string(scope, "root_path", "")?;
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
                self.receive_http_body(py)
            }
            FastApiOperationMatch::MethodNotAllowed { .. } => {
                self.response_status = 405;
                self.response_body = br#"{"detail":"Method Not Allowed"}"#.to_vec();
                self.send_start(py)
            }
            FastApiOperationMatch::NotFound => {
                self.response_status = 404;
                self.response_body = br#"{"detail":"Not Found"}"#.to_vec();
                self.send_start(py)
            }
        }
    }

    fn receive_http_body(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::Receive);
        self.receive
            .bind(py)
            .call0()
            .map(Bound::unbind)
            .map(MachineAction::Await)
    }

    fn receive_lifespan(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::LifespanReceive);
        self.receive
            .bind(py)
            .call0()
            .map(Bound::unbind)
            .map(MachineAction::Await)
    }

    fn lifespan_message(&mut self, py: Python<'_>, message: Py<PyAny>) -> PyResult<MachineAction> {
        let event = message
            .bind(py)
            .call_method1("get", ("type", ""))?
            .extract::<String>()?;
        let (response_type, pending) = match event.as_str() {
            "lifespan.startup" => (
                "lifespan.startup.complete",
                PendingAction::LifespanStartupSend,
            ),
            "lifespan.shutdown" => (
                "lifespan.shutdown.complete",
                PendingAction::LifespanShutdownSend,
            ),
            _ => {
                return Err(PyValueError::new_err(format!(
                    "unsupported ASGI lifespan event {event:?}"
                )));
            }
        };
        let response = PyDict::new(py);
        response.set_item("type", response_type)?;
        self.pending = Some(pending);
        self.send
            .bind(py)
            .call1((response,))
            .map(Bound::unbind)
            .map(MachineAction::Await)
    }

    fn receive_body(&mut self, py: Python<'_>, message: Py<PyAny>) -> PyResult<MachineAction> {
        let message = message.bind(py);
        let event_type = message
            .call_method1("get", ("type", ""))?
            .extract::<String>()?;
        if event_type == "http.disconnect" {
            return Err(PyRuntimeError::new_err(
                "client disconnected during request body",
            ));
        }
        if event_type != "http.request" {
            return Err(PyValueError::new_err(format!(
                "unsupported ASGI HTTP request event {event_type:?}"
            )));
        }
        let chunk: Vec<u8> = message
            .call_method1("get", ("body", PyBytes::new(py, b"")))?
            .extract()?;
        self.body.extend(chunk);
        let more_body = message
            .call_method1("get", ("more_body", false))?
            .extract::<bool>()?;
        if more_body {
            self.pending = Some(PendingAction::Receive);
            return self
                .receive
                .bind(py)
                .call0()
                .map(Bound::unbind)
                .map(MachineAction::Await);
        }
        let scope = self.scope.bind(py);
        let path = parse_scope_string(scope, "path", "/")?;
        let root_path = parse_scope_string(scope, "root_path", "")?;
        let method = parse_scope_string(scope, "method", "GET")?;
        let query: Vec<u8> = scope
            .call_method1("get", ("query_string", PyBytes::new(py, b"")))?
            .extract()?;
        let headers: Vec<(Vec<u8>, Vec<u8>)> = scope
            .call_method1("get", ("headers", PyList::empty(py)))?
            .extract()?;
        let parse_json_body = should_parse_json_body(&headers);
        let inputs = self
            .app
            .bind(py)
            .borrow()
            .router
            .resolve_inputs(&path, &root_path, &method, &query, headers, &self.body);
        let values = match decode_input_values(py, inputs, parse_json_body) {
            Ok(values) => values,
            Err(InputDecodeError::JsonValidation(error)) => {
                self.response_status = 422;
                self.response_body = json_bytes(
                    py,
                    json_decode_validation_response_body(py, &error)?.bind(py),
                )?;
                return self.send_start(py);
            }
            Err(InputDecodeError::BodyParse(_error)) => {
                self.response_status = 400;
                self.response_body = json_bytes(py, bad_request_body_response_body(py)?.bind(py))?;
                return self.send_start(py);
            }
            Err(InputDecodeError::Other(error)) => return Err(error),
        };
        let route_index = self
            .route_index
            .ok_or_else(|| PyRuntimeError::new_err("ASGI dispatch has no selected route"))?;
        let mut validation_issues = Vec::new();
        let invocation = {
            let app = self.app.bind(py).borrow();
            let route = app
                .routes
                .get(route_index)
                .ok_or_else(|| PyRuntimeError::new_err("selected FastAPI route was lost"))?;
            route
                .plan
                .invoke(py, values.bind(py), &mut validation_issues)
        };
        match invocation {
            Ok(Some(endpoint_result)) => {
                self.pending = Some(PendingAction::Endpoint);
                if py
                    .import("inspect")?
                    .getattr("isawaitable")?
                    .call1((endpoint_result.bind(py),))?
                    .extract::<bool>()?
                {
                    Ok(MachineAction::Await(endpoint_result))
                } else {
                    self.finish_endpoint(py, endpoint_result)
                }
            }
            Ok(None) if !validation_issues.is_empty() => {
                self.response_status = 422;
                self.response_body = json_bytes(
                    py,
                    validation_response_body(py, &validation_issues)?.bind(py),
                )?;
                self.send_start(py)
            }
            Ok(None) => Err(PyRuntimeError::new_err(
                "request invocation completed without a callable result or validation failure",
            )),
            Err(error) => Err(error),
        }
    }

    fn finish_endpoint(&mut self, py: Python<'_>, result: Py<PyAny>) -> PyResult<MachineAction> {
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
        self.response_status = route.status_code;
        self.response_body = json_bytes(py, &response_value)?;
        drop(app);
        self.send_start(py)
    }

    fn send_start(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::SendStart);
        response_start(
            py,
            self.send.bind(py),
            self.response_status,
            &self.response_body,
        )
        .map(MachineAction::Await)
    }

    fn send_body(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        self.pending = Some(PendingAction::SendBody);
        response_body(py, self.send.bind(py), &self.response_body).map(MachineAction::Await)
    }
}

impl AwaitableStateMachine for FastApiCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.begin(py),
            MachineResume::Value(value) => match self.pending.take() {
                Some(PendingAction::Receive) => self.receive_body(py, value),
                Some(PendingAction::LifespanReceive) => self.lifespan_message(py, value),
                Some(PendingAction::LifespanStartupSend) => self.receive_lifespan(py),
                Some(PendingAction::LifespanShutdownSend) => Ok(MachineAction::Complete(py.None())),
                Some(PendingAction::Endpoint) => self.finish_endpoint(py, value),
                Some(PendingAction::SendStart) => self.send_body(py),
                Some(PendingAction::SendBody) => Ok(MachineAction::Complete(py.None())),
                None => Err(PyRuntimeError::new_err(
                    "ASGI call resumed without a pending action",
                )),
            },
            MachineResume::Error(error) => Err(error),
        }
    }
}

/// Registers FastAPI's Rust-owned application type and request markers.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyFastApi>()?;
    module.add_class::<PyOperationDecorator>()?;
    Ok(())
}
