//! Private Python bindings for FastAPI-RS.

use fastapi_rs::asgi::{AsgiScopeKind, classify_scope};
use fastapi_rs::{
    FastApiInputLocation, FastApiInputParameter, FastApiOperationMatch, FastApiOperationRouter,
    JsonableEncoderInput, JsonableEncoderOptions,
};
use pyo3::IntoPyObjectExt;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList, PyModule};

#[pyclass(name = "jsonable_encoder", module = "fastapi.encoders", dict)]
struct PyJsonableEncoder;

fn extract_truthy(value: &Bound<'_, PyAny>) -> PyResult<bool> {
    value.is_truthy()
}

#[pymethods]
impl PyJsonableEncoder {
    #[pyo3(signature = (obj, include=None, exclude=None, by_alias=true, exclude_unset=false, exclude_defaults=false, exclude_none=false, custom_encoder=None, sqlalchemy_safe=true))]
    // lint-exception: Preserve every ordered FastAPI parameter at the native call boundary.
    #[allow(
        clippy::too_many_arguments,
        reason = "the reviewed public Python signature has nine named parameters"
    )]
    fn __call__<'py>(
        &self,
        py: Python<'py>,
        obj: Bound<'py, PyAny>,
        include: Option<Bound<'py, PyAny>>,
        exclude: Option<Bound<'py, PyAny>>,
        #[pyo3(from_py_with = extract_truthy)] by_alias: bool,
        #[pyo3(from_py_with = extract_truthy)] exclude_unset: bool,
        #[pyo3(from_py_with = extract_truthy)] exclude_defaults: bool,
        #[pyo3(from_py_with = extract_truthy)] exclude_none: bool,
        custom_encoder: Option<Bound<'py, PyAny>>,
        #[pyo3(from_py_with = extract_truthy)] sqlalchemy_safe: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let options = JsonableEncoderOptions::new(JsonableEncoderInput {
            include,
            exclude,
            by_alias,
            exclude_unset,
            exclude_defaults,
            exclude_none,
            custom_encoder,
            sqlalchemy_safe,
        });
        fastapi_rs::jsonable_encoder(py, &obj, &options)
    }
}

fn install_encoder_signature(py: Python<'_>, callable: &Bound<'_, PyAny>) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let kind = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let parameters = PyList::empty(py);
    let parameter_specs = [
        (
            "obj",
            None,
            "typing.Annotated[typing.Any, Doc('\\n            The input object to convert to JSON.\\n            ')]",
        ),
        (
            "include",
            Some(None),
            "typing.Annotated[typing.Union[set[int], set[str], collections.abc.Mapping[int, typing.Union[ForwardRef('IncEx'), bool]], collections.abc.Mapping[str, typing.Union[ForwardRef('IncEx'), bool]], NoneType], Doc(\"\\n            Pydantic's `include` parameter, passed to Pydantic models to set the\\n            fields to include.\\n            \")]",
        ),
        (
            "exclude",
            Some(None),
            "typing.Annotated[typing.Union[set[int], set[str], collections.abc.Mapping[int, typing.Union[ForwardRef('IncEx'), bool]], collections.abc.Mapping[str, typing.Union[ForwardRef('IncEx'), bool]], NoneType], Doc(\"\\n            Pydantic's `exclude` parameter, passed to Pydantic models to set the\\n            fields to exclude.\\n            \")]",
        ),
        (
            "by_alias",
            Some(Some(true)),
            "typing.Annotated[bool, Doc(\"\\n            Pydantic's `by_alias` parameter, passed to Pydantic models to define if\\n            the output should use the alias names (when provided) or the Python\\n            attribute names. In an API, if you set an alias, it's probably because you\\n            want to use it in the result, so you probably want to leave this set to\\n            `True`.\\n            \")]",
        ),
        (
            "exclude_unset",
            Some(Some(false)),
            "typing.Annotated[bool, Doc(\"\\n            Pydantic's `exclude_unset` parameter, passed to Pydantic models to define\\n            if it should exclude from the output the fields that were not explicitly\\n            set (and that only had their default values).\\n            \")]",
        ),
        (
            "exclude_defaults",
            Some(Some(false)),
            "typing.Annotated[bool, Doc(\"\\n            Pydantic's `exclude_defaults` parameter, passed to Pydantic models to define\\n            if it should exclude from the output the fields that had the same default\\n            value, even when they were explicitly set.\\n            \")]",
        ),
        (
            "exclude_none",
            Some(Some(false)),
            "typing.Annotated[bool, Doc(\"\\n            Pydantic's `exclude_none` parameter, passed to Pydantic models to define\\n            if it should exclude from the output any fields that have a `None` value.\\n            \")]",
        ),
        (
            "custom_encoder",
            Some(None),
            "typing.Annotated[dict[typing.Any, collections.abc.Callable[[typing.Any], typing.Any]] | None, Doc(\"\\n            Pydantic's `custom_encoder` parameter, passed to Pydantic models to define\\n            a custom encoder.\\n            \")]",
        ),
        (
            "sqlalchemy_safe",
            Some(Some(true)),
            "typing.Annotated[bool, Doc(\"\\n            Exclude from the output any fields that start with the name `_sa`.\\n\\n            This is mainly a hack for compatibility with SQLAlchemy objects, they\\n            store internal SQLAlchemy-specific state in attributes named with `_sa`,\\n            and those objects can't (and shouldn't be) serialized to JSON.\\n            \")]",
        ),
    ];

    for (name, default, annotation) in parameter_specs {
        let kwargs = PyDict::new(py);
        if let Some(default) = default {
            let value = match default {
                None => py.None().into_bound(py),
                Some(value) => value.into_bound_py_any(py)?,
            };
            kwargs.set_item("default", value)?;
        }
        kwargs.set_item("annotation", annotation)?;
        parameters.append(parameter_type.call((name, &kind), Some(&kwargs))?)?;
    }

    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", "typing.Any")?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    callable.setattr("__signature__", signature)
}

#[pyclass(name = "_OperationRouter")]
struct PyOperationRouter {
    inner: FastApiOperationRouter,
}

#[pymethods]
impl PyOperationRouter {
    #[new]
    fn new() -> Self {
        Self {
            inner: FastApiOperationRouter::new(),
        }
    }

    fn add_operation(&mut self, path: &str, method: &str, status_code: u16) -> PyResult<usize> {
        self.inner
            .add_operation(path, method, status_code)
            .map_err(|error| PyValueError::new_err(error.to_string()))
    }

    fn set_parameters(
        &mut self,
        operation_index: usize,
        parameters: Vec<(String, String, String, bool)>,
    ) -> PyResult<()> {
        let parameters = parameters
            .into_iter()
            .map(|(name, alias, location, required)| {
                let location = match location.as_str() {
                    "path" => FastApiInputLocation::Path,
                    "query" => FastApiInputLocation::Query,
                    "header" => FastApiInputLocation::Header,
                    "cookie" => FastApiInputLocation::Cookie,
                    "body" => FastApiInputLocation::Body,
                    _ => return Err(PyValueError::new_err("unknown FastAPI input location")),
                };
                Ok(FastApiInputParameter {
                    name,
                    alias,
                    location,
                    required,
                })
            })
            .collect::<PyResult<Vec<_>>>()?;
        self.inner
            .set_parameters(operation_index, parameters)
            .ok_or_else(|| PyValueError::new_err("unknown operation index"))
    }

    fn matches<'py>(
        &self,
        py: Python<'py>,
        path: &str,
        root_path: &str,
        method: &str,
    ) -> PyResult<Bound<'py, PyDict>> {
        let result = PyDict::new(py);
        match self.inner.matches(path, root_path, method) {
            FastApiOperationMatch::Matched {
                operation_index,
                path_params,
            } => {
                result.set_item("outcome", "matched")?;
                result.set_item("operation_index", operation_index)?;
                result.set_item("path_params", path_params)?;
                if let Some(operation) = self.inner.operation(operation_index) {
                    result.set_item("status_code", operation.status_code)?;
                }
            }
            FastApiOperationMatch::MethodNotAllowed {
                operation_index,
                allowed_methods,
                path_params,
            } => {
                result.set_item("outcome", "method_not_allowed")?;
                result.set_item("operation_index", operation_index)?;
                result.set_item("allowed_methods", allowed_methods)?;
                result.set_item("path_params", path_params)?;
            }
            FastApiOperationMatch::NotFound => {
                result.set_item("outcome", "not_found")?;
            }
        }
        Ok(result)
    }

    fn resolve_inputs<'py>(
        &self,
        py: Python<'py>,
        scope: &Bound<'py, PyDict>,
        body: &[u8],
    ) -> PyResult<Bound<'py, PyDict>> {
        let path: String = scope
            .get_item("path")?
            .ok_or_else(|| PyValueError::new_err("ASGI scope is missing path"))?
            .extract()?;
        let root_path: String = scope
            .get_item("root_path")?
            .map_or(Ok(String::new()), |value| value.extract())?;
        let method: String = scope
            .get_item("method")?
            .ok_or_else(|| PyValueError::new_err("ASGI scope is missing method"))?
            .extract()?;
        let raw_query: Vec<u8> = scope
            .get_item("query_string")?
            .ok_or_else(|| PyValueError::new_err("ASGI scope is missing query_string"))?
            .extract()?;
        let headers: Vec<(Vec<u8>, Vec<u8>)> = scope
            .get_item("headers")?
            .ok_or_else(|| PyValueError::new_err("ASGI scope is missing headers"))?
            .extract()?;
        let request = self
            .inner
            .resolve_inputs(&path, &root_path, &method, &raw_query, headers, body);
        let result = PyDict::new(py);
        match request.route {
            FastApiOperationMatch::Matched {
                operation_index,
                path_params,
            } => {
                result.set_item("outcome", "matched")?;
                result.set_item("operation_index", operation_index)?;
                result.set_item("path_params", path_params)?;
                if let Some(operation) = self.inner.operation(operation_index) {
                    result.set_item("status_code", operation.status_code)?;
                }
            }
            FastApiOperationMatch::MethodNotAllowed {
                operation_index,
                allowed_methods,
                path_params,
            } => {
                result.set_item("outcome", "method_not_allowed")?;
                result.set_item("operation_index", operation_index)?;
                result.set_item("allowed_methods", allowed_methods)?;
                result.set_item("path_params", path_params)?;
            }
            FastApiOperationMatch::NotFound => result.set_item("outcome", "not_found")?,
        }
        let inputs = PyList::empty(py);
        for input in request.inputs {
            let item = PyDict::new(py);
            item.set_item("name", input.name)?;
            item.set_item("location", input.location.as_str())?;
            if let Some(value) = input.value {
                item.set_item("value", PyBytes::new(py, &value))?;
            } else {
                item.set_item("value", py.None())?;
            }
            inputs.append(item)?;
        }
        result.set_item("inputs", inputs)?;
        Ok(result)
    }

    fn len(&self) -> usize {
        self.inner.len()
    }

    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
}

#[pyfunction]
fn scope_kind(scope_type: &str) -> &'static str {
    match classify_scope(scope_type) {
        AsgiScopeKind::Http => "http",
        AsgiScopeKind::WebSocket => "websocket",
        AsgiScopeKind::Lifespan => "lifespan",
        AsgiScopeKind::Other => "other",
    }
}

#[pyfunction]
fn identity<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
    let identity = PyDict::new(py);
    identity.set_item("target", "fastapi-rs")?;
    identity.set_item("version", env!("CARGO_PKG_VERSION"))?;
    identity.set_item("binding", "pyo3")?;
    Ok(identity)
}

#[pyfunction]
fn require_supported_scope(scope_type: &str) -> PyResult<&'static str> {
    match scope_kind(scope_type) {
        "http" | "websocket" | "lifespan" => Ok(scope_kind(scope_type)),
        _ => Err(PyValueError::new_err("unsupported ASGI scope type")),
    }
}

#[pymodule]
fn _core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    fastapi_rs::register_python_api(module)?;
    module.add_class::<PyOperationRouter>()?;
    module.add_function(wrap_pyfunction!(identity, module)?)?;
    module.add_function(wrap_pyfunction!(scope_kind, module)?)?;
    module.add_function(wrap_pyfunction!(require_supported_scope, module)?)?;
    module.add_class::<PyJsonableEncoder>()?;
    let encoder = Py::new(module.py(), PyJsonableEncoder)?;
    install_encoder_signature(module.py(), encoder.bind(module.py()))?;
    module.add("jsonable_encoder", encoder)?;
    Ok(())
}
