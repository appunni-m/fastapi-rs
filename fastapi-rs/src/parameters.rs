//! Rust-owned Python metadata for FastAPI parameters and dependencies.

use pyo3::prelude::*;
use pyo3::types::PyModule;

/// Metadata attached to an endpoint annotation through `typing.Annotated`.
#[pyclass(name = "_ParameterMetadata", module = "fastapi_rs._core")]
pub(crate) struct ParameterMetadata {
    kind: String,
    alias: Option<String>,
    dependency: Option<Py<PyAny>>,
    default: Option<Py<PyAny>>,
    gt: Option<Py<PyAny>>,
}

#[pymethods]
impl ParameterMetadata {
    #[getter]
    fn kind(&self) -> String {
        self.kind.clone()
    }

    #[getter]
    fn alias(&self) -> Option<String> {
        self.alias.clone()
    }

    #[getter]
    fn dependency(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.dependency
            .as_ref()
            .map(|dependency| dependency.clone_ref(py))
    }

    #[getter]
    fn default(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.default.as_ref().map(|default| default.clone_ref(py))
    }

    #[getter]
    fn gt(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.gt.as_ref().map(|gt| gt.clone_ref(py))
    }
}

#[pyfunction(name = "Depends")]
fn depends(py: Python<'_>, dependency: Py<PyAny>) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "depends".to_owned(),
            alias: None,
            dependency: Some(dependency),
            default: None,
            gt: None,
        },
    )
}

#[pyfunction(name = "Header", signature = (*, alias = None, default = None))]
fn header(
    py: Python<'_>,
    alias: Option<String>,
    default: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "header".to_owned(),
            alias,
            dependency: None,
            default,
            gt: None,
        },
    )
}

#[pyfunction(name = "Cookie", signature = (*, alias = None, default = None))]
fn cookie(
    py: Python<'_>,
    alias: Option<String>,
    default: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "cookie".to_owned(),
            alias,
            dependency: None,
            default,
            gt: None,
        },
    )
}

#[pyfunction(name = "Query", signature = (*, alias = None, default = None))]
fn query(
    py: Python<'_>,
    alias: Option<String>,
    default: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "query".to_owned(),
            alias,
            dependency: None,
            default,
            gt: None,
        },
    )
}

#[pyfunction(name = "Body", signature = (*, gt = None))]
fn body(py: Python<'_>, gt: Option<Py<PyAny>>) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "body".to_owned(),
            alias: None,
            dependency: None,
            default: None,
            gt,
        },
    )
}

/// Registers parameter metadata constructors and the HTTP status namespace.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    module.add_class::<ParameterMetadata>()?;
    module.add_function(wrap_pyfunction!(depends, module)?)?;
    module.add_function(wrap_pyfunction!(header, module)?)?;
    module.add_function(wrap_pyfunction!(cookie, module)?)?;
    module.add_function(wrap_pyfunction!(query, module)?)?;
    module.add_function(wrap_pyfunction!(body, module)?)?;

    let status = PyModule::new(py, "status")?;
    status.add("HTTP_200_OK", 200)?;
    status.add("HTTP_201_CREATED", 201)?;
    status.add("HTTP_202_ACCEPTED", 202)?;
    status.add("HTTP_204_NO_CONTENT", 204)?;
    status.add("HTTP_400_BAD_REQUEST", 400)?;
    status.add("HTTP_401_UNAUTHORIZED", 401)?;
    status.add("HTTP_403_FORBIDDEN", 403)?;
    status.add("HTTP_404_NOT_FOUND", 404)?;
    status.add("HTTP_405_METHOD_NOT_ALLOWED", 405)?;
    status.add("HTTP_409_CONFLICT", 409)?;
    status.add("HTTP_422_UNPROCESSABLE_ENTITY", 422)?;
    status.add("HTTP_429_TOO_MANY_REQUESTS", 429)?;
    status.add("HTTP_500_INTERNAL_SERVER_ERROR", 500)?;
    status.add("HTTP_501_NOT_IMPLEMENTED", 501)?;
    status.add("HTTP_502_BAD_GATEWAY", 502)?;
    status.add("HTTP_503_SERVICE_UNAVAILABLE", 503)?;
    status.add("HTTP_504_GATEWAY_TIMEOUT", 504)?;
    module.add_submodule(&status)?;
    Ok(())
}
