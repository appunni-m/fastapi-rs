//! Private Python bindings for FastAPI-RS.

use fastapi_rs::asgi::{AsgiScopeKind, classify_scope};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};

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
    module.add_function(wrap_pyfunction!(identity, module)?)?;
    module.add_function(wrap_pyfunction!(scope_kind, module)?)?;
    module.add_function(wrap_pyfunction!(require_supported_scope, module)?)?;
    Ok(())
}
