//! Rust implementation core for FastAPI-RS.
//!
//! Generic ASGI scope classification is delegated to Starlette-RS. FastAPI
//! owns the routing, dependency, validation, serialization, and OpenAPI
//! integration built on top of that boundary.

mod application_runtime;
mod awaitable;
mod datastructures;
mod deprecated_api;
mod docs;
mod encoding;
mod errors;
mod lifespan;
mod openapi;
mod operation;
mod parameters;
mod sse;

use pyo3::prelude::*;
use pyo3::types::PyModule;

pub use encoding::{JsonableEncoderInput, JsonableEncoderOptions};
pub use operation::{
    FastApiInputLocation, FastApiInputParameter, FastApiInputValue, FastApiOperation,
    FastApiOperationMatch, FastApiOperationRouter, FastApiRequestMatch,
};

/// Registers FastAPI's public Python API from the Rust-owned implementation.
pub fn register_python_api(module: &Bound<'_, PyModule>) -> PyResult<()> {
    awaitable::register_coroutine_protocol(module.py())?;
    errors::register(module)?;
    parameters::register(module)?;
    datastructures::register(module)?;
    deprecated_api::register(module)?;
    sse::register(module)?;
    application_runtime::register(module)
}

/// Convert a Python value into JSON-compatible data using FastAPI's encoder rules.
pub fn jsonable_encoder<'py>(
    py: Python<'py>,
    obj: &Bound<'py, PyAny>,
    options: &JsonableEncoderOptions,
) -> PyResult<Bound<'py, PyAny>> {
    encoding::jsonable_encoder(py, obj, options)
}

/// ASGI scope helpers supplied by the Starlette-RS dependency.
pub mod asgi {
    pub use starlette_rs::{AsgiScopeKind, classify_scope};
}
