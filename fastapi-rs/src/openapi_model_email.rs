//! Native optional EmailStr behavior for the private OpenAPI model graph.

use pyo3::exceptions::{PyAssertionError, PyImportError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString, PyTuple};

const EMAIL_WARNING: &str = concat!(
    "email-validator not installed, email fields will be treated as str.\n",
    "To install, run: pip install email-validator",
);

/// Selects the source optional profile without importing original FastAPI.
///
/// Source catches ImportError from the optional import/EmailStr selection, but
/// preserves every other exception. The fallback retains the ordinary logger
/// object and implements schema/validation callbacks in native Rust.
pub(crate) fn email_type(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let logger = py
        .import("logging")?
        .getattr("getLogger")?
        .call1(("fastapi",))?;
    let selected = (|| {
        let validator = py.import("email_validator")?;
        if !validator.is_truthy()? {
            return Err(PyAssertionError::new_err(()));
        }
        py.import("pydantic")?
            .getattr("EmailStr")
            .map(Bound::unbind)
    })();
    match selected {
        Ok(email_type) => Ok(email_type),
        Err(error) if error.is_instance_of::<PyImportError>(py) => fallback_email_type(py, logger),
        Err(error) => Err(error),
    }
}

fn fallback_email_type(py: Python<'_>, logger: Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    let classmethod = py.import("builtins")?.getattr("classmethod")?;
    let attributes = PyDict::new(py);
    attributes.set_item("__module__", "fastapi.openapi.models")?;
    attributes.set_item(
        "validate",
        classmethod.call1((Py::new(
            py,
            EmailValidate {
                logger: logger.clone().unbind(),
            },
        )?,))?,
    )?;
    attributes.set_item(
        "_validate",
        classmethod.call1((Py::new(
            py,
            EmailValidateWithInfo {
                logger: logger.unbind(),
            },
        )?,))?,
    )?;
    attributes.set_item(
        "__get_validators__",
        classmethod.call1((Py::new(py, EmailGetValidators)?,))?,
    )?;
    attributes.set_item(
        "__get_pydantic_core_schema__",
        classmethod.call1((Py::new(py, EmailCoreSchema)?,))?,
    )?;
    attributes.set_item(
        "__get_pydantic_json_schema__",
        classmethod.call1((Py::new(py, EmailJsonSchema)?,))?,
    )?;
    py.import("builtins")?
        .getattr("type")?
        .call1((
            "EmailStr",
            PyTuple::new(py, [py.get_type::<PyString>()])?,
            attributes,
        ))
        .map(Bound::unbind)
}

fn warn_and_stringify(logger: &Bound<'_, PyAny>, value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    logger.call_method1("warning", (EMAIL_WARNING,))?;
    value.str().map(|value| value.into_any().unbind())
}

#[pyclass(name = "_OpenApiEmailValidate", module = "fastapi_rs._core")]
struct EmailValidate {
    logger: Py<PyAny>,
}

#[pymethods]
impl EmailValidate {
    fn __call__(
        &self,
        py: Python<'_>,
        _class: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        warn_and_stringify(self.logger.bind(py), value)
    }
}

#[pyclass(name = "_OpenApiEmailValidateWithInfo", module = "fastapi_rs._core")]
struct EmailValidateWithInfo {
    logger: Py<PyAny>,
}

#[pymethods]
impl EmailValidateWithInfo {
    fn __call__(
        &self,
        py: Python<'_>,
        _class: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
        _info: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        warn_and_stringify(self.logger.bind(py), value)
    }
}

#[pyclass(name = "_OpenApiEmailCoreSchema", module = "fastapi_rs._core")]
struct EmailCoreSchema;

#[pymethods]
impl EmailCoreSchema {
    fn __call__(
        &self,
        py: Python<'_>,
        class: &Bound<'_, PyAny>,
        _source: &Bound<'_, PyAny>,
        _handler: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        py.import("pydantic_core.core_schema")?
            .getattr("with_info_plain_validator_function")?
            .call1((class.getattr("_validate")?,))
            .map(Bound::unbind)
    }
}

#[pyclass(name = "_OpenApiEmailJsonSchema", module = "fastapi_rs._core")]
struct EmailJsonSchema;

#[pymethods]
impl EmailJsonSchema {
    fn __call__(
        &self,
        py: Python<'_>,
        _class: &Bound<'_, PyAny>,
        _schema: &Bound<'_, PyAny>,
        _handler: &Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let schema = PyDict::new(py);
        schema.set_item("type", "string")?;
        schema.set_item("format", "email")?;
        Ok(schema.into_any().unbind())
    }
}

#[pyclass(name = "_OpenApiEmailGetValidators", module = "fastapi_rs._core")]
struct EmailGetValidators;

#[pymethods]
impl EmailGetValidators {
    fn __call__(&self, py: Python<'_>, class: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        Py::new(
            py,
            EmailValidatorsIterator {
                class: class.clone().unbind(),
                finished: false,
            },
        )
        .map(Py::into_any)
    }
}

#[pyclass(name = "_OpenApiEmailValidatorsIterator", module = "fastapi_rs._core")]
struct EmailValidatorsIterator {
    class: Py<PyAny>,
    finished: bool,
}

#[pymethods]
impl EmailValidatorsIterator {
    fn __iter__(slf: Py<Self>) -> Py<Self> {
        slf
    }

    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        if self.finished {
            return Ok(None);
        }
        self.finished = true;
        self.class
            .bind(py)
            .getattr("validate")
            .map(|value| Some(value.unbind()))
    }
}
