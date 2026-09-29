//! Rust-owned exception identities used by FastAPI behavior.

use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyRuntimeError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};

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

create_exception!(
    fastapi.exceptions,
    ValidationException,
    PyException,
    "A validation error occurred."
);
create_exception!(
    fastapi.exceptions,
    RequestValidationError,
    ValidationException,
    "The request data failed validation."
);
create_exception!(
    fastapi.exceptions,
    ResponseValidationError,
    ValidationException,
    "The response data failed validation."
);

#[derive(Clone, Copy)]
enum ValidationExceptionMethod {
    Init,
    Errors,
    String,
}

#[pyclass]
struct ValidationExceptionMethodDescriptor {
    method: ValidationExceptionMethod,
}

#[pymethods]
impl ValidationExceptionMethodDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(
                py,
                Self {
                    method: self.method,
                },
            )
            .map(Py::into_any);
        };
        let instance = instance.unbind();
        match self.method {
            ValidationExceptionMethod::Init => {
                Py::new(py, BoundValidationExceptionInit { instance }).map(Py::into_any)
            }
            ValidationExceptionMethod::Errors => {
                Py::new(py, BoundValidationExceptionErrors { instance }).map(Py::into_any)
            }
            ValidationExceptionMethod::String => {
                Py::new(py, BoundValidationExceptionString { instance }).map(Py::into_any)
            }
        }
    }
}

#[pyclass]
struct BoundValidationExceptionInit {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundValidationExceptionInit {
    #[pyo3(signature = (errors, *, endpoint_ctx=None))]
    fn __call__(
        &self,
        py: Python<'_>,
        errors: Bound<'_, PyAny>,
        endpoint_ctx: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        initialize_validation_exception(
            py,
            self.instance.bind(py),
            &errors,
            endpoint_ctx.as_ref(),
        )?;
        self.instance.bind(py).setattr(
            "endpoint_ctx",
            endpoint_ctx.map(Bound::unbind).unwrap_or_else(|| py.None()),
        )?;
        Ok(())
    }
}

#[pyclass]
struct BoundValidationExceptionErrors {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundValidationExceptionErrors {
    fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.instance.bind(py).getattr("_errors").map(Bound::unbind)
    }
}

#[pyclass]
struct BoundValidationExceptionString {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundValidationExceptionString {
    fn __call__(&self, py: Python<'_>) -> PyResult<String> {
        let instance = self.instance.bind(py);
        let errors = instance.getattr("_errors")?;
        let count = errors.len()?;
        let suffix = if count == 1 { "" } else { "s" };
        let mut message = format!("{count} validation error{suffix}:\n");
        for error in errors.try_iter()? {
            let error = error?;
            message.push_str("  ");
            message.push_str(&error.str()?.to_string_lossy());
            message.push('\n');
        }

        let endpoint_file = instance.getattr("endpoint_file")?;
        let endpoint_line = instance.getattr("endpoint_line")?;
        let endpoint_function = instance.getattr("endpoint_function")?;
        if endpoint_file.is_truthy()?
            && endpoint_line.is_truthy()?
            && endpoint_function.is_truthy()?
        {
            message.push_str(&format!(
                "\n  File \"{}\", line {}, in {}",
                endpoint_file.str()?.to_string_lossy(),
                endpoint_line.str()?.to_string_lossy(),
                endpoint_function.str()?.to_string_lossy(),
            ));
            let endpoint_path = instance.getattr("endpoint_path")?;
            if endpoint_path.is_truthy()? {
                message.push_str(&format!("\n    {}", endpoint_path.str()?.to_string_lossy()));
            }
        } else {
            let endpoint_path = instance.getattr("endpoint_path")?;
            if endpoint_path.is_truthy()? {
                message.push_str(&format!(
                    "\n  Endpoint: {}",
                    endpoint_path.str()?.to_string_lossy()
                ));
            }
        }
        Ok(message.trim_end().to_owned())
    }
}

#[derive(Clone, Copy)]
enum ResponseValidationErrorMethod {
    Init,
}

#[derive(Clone, Copy)]
enum RequestValidationErrorMethod {
    Init,
}

#[pyclass]
struct ResponseValidationErrorMethodDescriptor {
    method: ResponseValidationErrorMethod,
}

#[pyclass]
struct RequestValidationErrorMethodDescriptor {
    method: RequestValidationErrorMethod,
}

#[pymethods]
impl ResponseValidationErrorMethodDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(
                py,
                Self {
                    method: self.method,
                },
            )
            .map(Py::into_any);
        };
        let instance = instance.unbind();
        match self.method {
            ResponseValidationErrorMethod::Init => {
                Py::new(py, BoundResponseValidationErrorInit { instance }).map(Py::into_any)
            }
        }
    }
}

#[pymethods]
impl RequestValidationErrorMethodDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(
                py,
                Self {
                    method: self.method,
                },
            )
            .map(Py::into_any);
        };
        let instance = instance.unbind();
        match self.method {
            RequestValidationErrorMethod::Init => {
                Py::new(py, BoundRequestValidationErrorInit { instance }).map(Py::into_any)
            }
        }
    }
}

#[pyclass]
struct BoundRequestValidationErrorInit {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundRequestValidationErrorInit {
    #[pyo3(signature = (errors, *, body=None, endpoint_ctx=None))]
    fn __call__(
        &self,
        py: Python<'_>,
        errors: Bound<'_, PyAny>,
        body: Option<Bound<'_, PyAny>>,
        endpoint_ctx: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        initialize_validation_exception(
            py,
            self.instance.bind(py),
            &errors,
            endpoint_ctx.as_ref(),
        )?;
        self.instance
            .bind(py)
            .setattr("body", body.map(Bound::unbind).unwrap_or_else(|| py.None()))?;
        self.instance.bind(py).setattr(
            "endpoint_ctx",
            endpoint_ctx.map(Bound::unbind).unwrap_or_else(|| py.None()),
        )?;
        Ok(())
    }
}

#[pyclass]
struct BoundResponseValidationErrorInit {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundResponseValidationErrorInit {
    #[pyo3(signature = (errors, *, body=None, endpoint_ctx=None))]
    fn __call__(
        &self,
        py: Python<'_>,
        errors: Bound<'_, PyAny>,
        body: Option<Bound<'_, PyAny>>,
        endpoint_ctx: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let instance = self.instance.bind(py);
        initialize_validation_exception(py, instance, &errors, endpoint_ctx.as_ref())?;
        instance.setattr("body", body.map(Bound::unbind).unwrap_or_else(|| py.None()))?;
        instance.setattr(
            "endpoint_ctx",
            endpoint_ctx.map(Bound::unbind).unwrap_or_else(|| py.None()),
        )?;
        Ok(())
    }
}

fn initialize_validation_exception(
    py: Python<'_>,
    instance: &Bound<'_, PyAny>,
    errors: &Bound<'_, PyAny>,
    endpoint_ctx: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    let context = match endpoint_ctx {
        Some(context) if context.is_truthy()? => context.clone(),
        _ => PyDict::new(py).into_any(),
    };
    instance.setattr("_errors", errors)?;
    instance.setattr(
        "endpoint_function",
        context.call_method1("get", ("function",))?,
    )?;
    instance.setattr("endpoint_path", context.call_method1("get", ("path",))?)?;
    instance.setattr("endpoint_file", context.call_method1("get", ("file",))?)?;
    instance.setattr("endpoint_line", context.call_method1("get", ("line",))?)?;
    Ok(())
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let validation_exception_type = py.get_type::<ValidationException>();
    validation_exception_type.setattr(
        "__init__",
        Py::new(
            py,
            ValidationExceptionMethodDescriptor {
                method: ValidationExceptionMethod::Init,
            },
        )?,
    )?;
    validation_exception_type.setattr(
        "errors",
        Py::new(
            py,
            ValidationExceptionMethodDescriptor {
                method: ValidationExceptionMethod::Errors,
            },
        )?,
    )?;
    validation_exception_type.setattr(
        "__str__",
        Py::new(
            py,
            ValidationExceptionMethodDescriptor {
                method: ValidationExceptionMethod::String,
            },
        )?,
    )?;

    let request_exception_type = py.get_type::<RequestValidationError>();
    request_exception_type.setattr(
        "__init__",
        Py::new(
            py,
            RequestValidationErrorMethodDescriptor {
                method: RequestValidationErrorMethod::Init,
            },
        )?,
    )?;

    let exception_type = py.get_type::<ResponseValidationError>();
    exception_type.setattr(
        "__init__",
        Py::new(
            py,
            ResponseValidationErrorMethodDescriptor {
                method: ResponseValidationErrorMethod::Init,
            },
        )?,
    )?;
    module.add("ValidationException", validation_exception_type)?;
    module.add("RequestValidationError", request_exception_type)?;
    module.add("ResponseValidationError", exception_type)
}

pub(crate) fn response_validation_error(
    py: Python<'_>,
    validation_error: &PyErr,
    body: &Bound<'_, PyAny>,
    endpoint_ctx: &Bound<'_, PyAny>,
) -> PyResult<PyErr> {
    let kwargs = PyDict::new(py);
    kwargs.set_item("include_url", false)?;
    let details = validation_error
        .value(py)
        .call_method("errors", (), Some(&kwargs))?
        .cast_into::<PyList>()?;
    let response_details = PyList::empty(py);

    for detail in details.iter() {
        let detail = detail.cast_into::<PyDict>()?;
        let response_detail = PyDict::new(py);
        for (key, value) in detail.iter() {
            let key = key.extract::<String>()?;
            match key.as_str() {
                "url" => {}
                "loc" => {
                    let location = value.cast_into::<PyTuple>()?;
                    let mut prefixed_location = Vec::with_capacity(location.len() + 1);
                    prefixed_location.push(PyString::new(py, "response").into_any().unbind());
                    prefixed_location.extend(location.iter().map(Bound::unbind));
                    response_detail.set_item("loc", PyTuple::new(py, prefixed_location)?)?;
                }
                _ => response_detail.set_item(key, value)?,
            }
        }
        response_details.append(response_detail)?;
    }

    let kwargs = PyDict::new(py);
    kwargs.set_item("body", body)?;
    kwargs.set_item("endpoint_ctx", endpoint_ctx)?;
    let exception = py
        .get_type::<ResponseValidationError>()
        .call((response_details,), Some(&kwargs))?;
    Ok(PyErr::from_value(exception))
}
