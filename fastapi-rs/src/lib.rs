//! Rust implementation core for FastAPI-RS.
//!
//! Generic ASGI scope classification is delegated to Starlette-RS. FastAPI
//! owns the routing, dependency, validation, serialization, and OpenAPI
//! integration built on top of that boundary.

mod application_runtime;
mod awaitable;
mod datastructures;
mod dependency_records;
mod deprecated_api;
mod docs;
mod encoding;
mod errors;
#[cfg(feature = "fault-injection")]
mod fault_injection;
mod lifespan;
mod openapi;
mod operation;
mod parameters;
mod response_field;
mod security;
mod sse;

use pyo3::prelude::*;
use pyo3::types::PyModule;

pub use encoding::{JsonableEncoderInput, JsonableEncoderOptions};
pub use operation::{
    FastApiInputLocation, FastApiInputParameter, FastApiInputValue, FastApiOperation,
    FastApiOperationMatch, FastApiOperationRouter, FastApiRequestMatch,
};

/// Arms one allow-listed fault point in builds compiled with `fault-injection`.
#[cfg(feature = "fault-injection")]
#[doc(hidden)]
pub fn arm_fault_injection(point: &str) -> Result<(), &'static str> {
    fault_injection::arm(point)
}

/// Clears any still-armed allow-listed fault point in fault-injection builds.
#[cfg(feature = "fault-injection")]
#[doc(hidden)]
pub fn clear_fault_injection() {
    fault_injection::clear();
}

/// Registers FastAPI's public Python API from the Rust-owned implementation.
pub fn register_python_api(module: &Bound<'_, PyModule>) -> PyResult<()> {
    awaitable::register_coroutine_protocol(module.py())?;
    errors::register(module)?;
    dependency_records::register(module)?;
    parameters::register(module)?;
    datastructures::register(module)?;
    deprecated_api::register(module)?;
    docs::register(module)?;
    security::register(module)?;
    sse::register(module)?;
    application_runtime::register(module)?;
    openapi::register(module)
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
