//! Rust-owned exception identities used by FastAPI behavior.

use pyo3::create_exception;

use pyo3::exceptions::PyRuntimeError;

create_exception!(
    fastapi.exceptions,
    FastAPIError,
    PyRuntimeError,
    "A generic, FastAPI-specific error."
);
create_exception!(
    fastapi.exceptions,
    PydanticV1NotSupportedError,
    FastAPIError,
    "A pydantic.v1 model is used, which is no longer supported."
);
