//! Rust implementation core for FastAPI-RS.
//!
//! Generic ASGI scope classification is delegated to Starlette-RS. FastAPI
//! owns the routing, dependency, validation, serialization, and OpenAPI
//! integration built on top of that boundary.

#[cfg(feature = "python")]
mod application_runtime;
#[cfg(feature = "python")]
mod awaitable;
#[cfg(feature = "python")]
mod datastructures;
#[cfg(feature = "python")]
mod dependency_records;
#[cfg(feature = "python")]
mod deprecated_api;
#[cfg(feature = "python")]
mod docs;
#[cfg(feature = "python")]
mod encoding;
#[cfg(feature = "python")]
mod errors;
#[cfg(feature = "fault-injection")]
mod fault_injection;
#[cfg(feature = "python")]
mod lifespan;
#[cfg(feature = "python")]
mod openapi;
#[cfg(feature = "python")]
mod openapi_model_email;
#[cfg(feature = "python")]
mod openapi_model_schema;
#[cfg(feature = "python")]
mod openapi_models;
mod operation;
#[cfg(feature = "python")]
mod parameters;
#[cfg(feature = "python")]
mod response_field;
#[cfg(feature = "python")]
mod security;
#[cfg(feature = "python")]
mod sse;

#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::types::PyModule;

#[cfg(feature = "python")]
pub use encoding::{JsonableEncoderInput, JsonableEncoderOptions};
pub use operation::{
    FastApiInputLocation, FastApiInputParameter, FastApiInputValue, FastApiOperation,
    FastApiOperationMatch, FastApiOperationRouter, FastApiRequestMatch,
};

/// Rust-native FastAPI service APIs, composed on Starlette-RS routing and bodies.
pub mod native;

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
#[cfg(feature = "python")]
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
    openapi_models::register(module.py(), module)?;
    application_runtime::register(module)?;
    openapi::register(module)
}

/// Convert a Python value into JSON-compatible data using FastAPI's encoder rules.
#[cfg(feature = "python")]
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
