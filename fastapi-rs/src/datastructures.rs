//! FastAPI-owned data structure integrations with Starlette-RS values.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule, PyTuple, PyType};

/// FastAPI's Pydantic validator accepts any Starlette UploadFile and preserves
/// the exact object produced by the request parser.
#[pyfunction]
fn upload_file_validate(
    py: Python<'_>,
    _cls: &Bound<'_, PyType>,
    input_value: &Bound<'_, PyAny>,
    _info: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let starlette_upload_file = py
        .import("starlette.datastructures")?
        .getattr("UploadFile")?;
    let is_upload_file = py
        .import("builtins")?
        .getattr("isinstance")?
        .call1((input_value, starlette_upload_file))?
        .extract::<bool>()?;
    if !is_upload_file {
        let received_type = py
            .import("builtins")?
            .getattr("type")?
            .call1((input_value,))?
            .repr()?
            .to_str()?
            .to_owned();
        return Err(PyValueError::new_err(format!(
            "Expected UploadFile, received: {received_type}"
        )));
    }
    Ok(input_value.clone().unbind())
}

/// Build the same info-aware plain-validator schema used by FastAPI 0.141.1.
#[pyfunction]
fn upload_file_core_schema(
    py: Python<'_>,
    cls: &Bound<'_, PyType>,
    _source: &Bound<'_, PyAny>,
    _handler: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let validator = cls.getattr("_validate")?;
    py.import("pydantic_core.core_schema")?
        .getattr("with_info_plain_validator_function")?
        .call1((validator,))
        .map(Bound::unbind)
}

/// Return FastAPI UploadFile's fixed Pydantic JSON schema.
#[pyfunction]
fn upload_file_json_schema(
    py: Python<'_>,
    _cls: &Bound<'_, PyType>,
    _core_schema: &Bound<'_, PyAny>,
    _handler: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let schema = PyDict::new(py);
    schema.set_item("type", "string")?;
    schema.set_item("contentMediaType", "application/octet-stream")?;
    Ok(schema.into_any().unbind())
}

/// Register FastAPI's annotation class over the Starlette-RS UploadFile type.
///
/// A runtime-created subclass keeps the FastAPI class identity while inheriting
/// Starlette-RS construction and file behavior. The Pydantic protocol callbacks
/// are native PyO3 functions installed as class methods on the generated type.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let classmethod = py.import("builtins")?.getattr("classmethod")?;
    let validate = wrap_pyfunction!(upload_file_validate, module)?;
    let core_schema = wrap_pyfunction!(upload_file_core_schema, module)?;
    let json_schema = wrap_pyfunction!(upload_file_json_schema, module)?;

    let attributes = PyDict::new(py);
    attributes.set_item("__module__", "fastapi.datastructures")?;
    attributes.set_item(
        "__doc__",
        "A file uploaded in a request, validated as a Starlette UploadFile.",
    )?;
    attributes.set_item("_validate", classmethod.call1((validate,))?)?;
    attributes.set_item(
        "__get_pydantic_core_schema__",
        classmethod.call1((core_schema,))?,
    )?;
    attributes.set_item(
        "__get_pydantic_json_schema__",
        classmethod.call1((json_schema,))?,
    )?;

    let starlette_upload_file = py
        .import("starlette.datastructures")?
        .getattr("UploadFile")?;
    let bases = PyTuple::new(py, [starlette_upload_file])?;
    let upload_file =
        py.import("builtins")?
            .getattr("type")?
            .call1(("UploadFile", bases, attributes))?;
    module.add("UploadFile", upload_file)?;
    register_background_tasks(module)
}

/// Register FastAPI's public subclass over Starlette-RS background task support.
fn register_background_tasks(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let attributes = PyDict::new(py);
    attributes.set_item("__module__", "fastapi.background")?;
    attributes.set_item(
        "__doc__",
        "A collection of background tasks that will be called after a response has been sent to the client.",
    )?;

    let starlette_background_tasks = py
        .import("starlette.background")?
        .getattr("BackgroundTasks")?;
    let bases = PyTuple::new(py, [starlette_background_tasks])?;
    let background_tasks =
        py.import("builtins")?
            .getattr("type")?
            .call1(("BackgroundTasks", bases, attributes))?;
    module.add("BackgroundTasks", background_tasks)
}
