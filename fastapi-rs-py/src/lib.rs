//! Private Python bindings for FastAPI-RS.

use fastapi_rs::asgi::{AsgiScopeKind, classify_scope};
use fastapi_rs::{
    FastApiInputLocation, FastApiInputParameter, FastApiOperationMatch, FastApiOperationRouter,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList, PyModule};

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
    module.add_class::<PyOperationRouter>()?;
    module.add_function(wrap_pyfunction!(identity, module)?)?;
    module.add_function(wrap_pyfunction!(scope_kind, module)?)?;
    module.add_function(wrap_pyfunction!(require_supported_scope, module)?)?;
    Ok(())
}
