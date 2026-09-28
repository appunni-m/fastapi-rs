//! Rust implementation core for FastAPI-RS.
//!
//! Generic ASGI scope classification is delegated to Starlette-RS. FastAPI
//! owns the routing, dependency, validation, serialization, and OpenAPI
//! integration built on top of that boundary.

mod operation;

pub use operation::{
    FastApiInputLocation, FastApiInputParameter, FastApiInputValue, FastApiOperation,
    FastApiOperationMatch, FastApiOperationRouter, FastApiRequestMatch,
};

/// ASGI scope helpers supplied by the Starlette-RS dependency.
pub mod asgi {
    pub use starlette_rs::{AsgiScopeKind, classify_scope};
}
