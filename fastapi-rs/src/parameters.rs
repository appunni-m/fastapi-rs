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
    media_type: Option<String>,
    title: Option<String>,
    description: Option<String>,
    pattern: Option<String>,
    deprecated: Option<Py<PyAny>>,
    include_in_schema: bool,
    gt: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    min_length: Option<Py<PyAny>>,
    max_length: Option<Py<PyAny>>,
    convert_underscores: bool,
    use_cache: bool,
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
    fn media_type(&self) -> Option<String> {
        self.media_type.clone()
    }

    #[getter]
    fn title(&self) -> Option<String> {
        self.title.clone()
    }

    #[getter]
    fn description(&self) -> Option<String> {
        self.description.clone()
    }

    #[getter]
    fn pattern(&self) -> Option<String> {
        self.pattern.clone()
    }

    #[getter]
    fn deprecated(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.deprecated
            .as_ref()
            .map(|deprecated| deprecated.clone_ref(py))
    }

    #[getter]
    fn include_in_schema(&self) -> bool {
        self.include_in_schema
    }

    #[getter]
    fn default_is_set(&self) -> bool {
        self.default.is_some()
    }

    #[getter]
    fn gt(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.gt.as_ref().map(|gt| gt.clone_ref(py))
    }

    #[getter]
    fn lt(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.lt.as_ref().map(|lt| lt.clone_ref(py))
    }

    #[getter]
    fn min_length(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.min_length
            .as_ref()
            .map(|min_length| min_length.clone_ref(py))
    }

    #[getter]
    fn max_length(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.max_length
            .as_ref()
            .map(|max_length| max_length.clone_ref(py))
    }

    #[getter]
    fn convert_underscores(&self) -> bool {
        self.convert_underscores
    }

    #[getter]
    fn use_cache(&self) -> bool {
        self.use_cache
    }
}

#[pyfunction(name = "Depends", signature = (dependency, *, use_cache = true))]
fn depends(
    py: Python<'_>,
    dependency: Py<PyAny>,
    use_cache: bool,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "depends".to_owned(),
            alias: None,
            dependency: Some(dependency),
            default: None,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache,
        },
    )
}

#[pyfunction(
    name = "Header",
    signature = (*, alias = None, default = None, convert_underscores = true)
)]
fn header(
    py: Python<'_>,
    alias: Option<String>,
    default: Option<Py<PyAny>>,
    convert_underscores: bool,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "header".to_owned(),
            alias,
            dependency: None,
            default,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores,
            use_cache: true,
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
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

fn query_ellipsis_default() -> Py<PyAny> {
    Python::attach(|py| py.Ellipsis())
}

#[pyfunction(
    name = "Query",
    signature = (
        default = query_ellipsis_default(),
        *,
        alias = None,
        title = None,
        description = None,
        gt = None,
        lt = None,
        min_length = None,
        max_length = None,
        pattern = None,
        deprecated = None,
        include_in_schema = true
    )
)]
// lint-exception: PyO3 needs one Rust argument per FastAPI-compatible Query keyword.
#[allow(
    clippy::too_many_arguments,
    reason = "preserve FastAPI Query's positional default and named option signature"
)]
fn query(
    py: Python<'_>,
    default: Py<PyAny>,
    alias: Option<String>,
    title: Option<String>,
    description: Option<String>,
    gt: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    min_length: Option<Py<PyAny>>,
    max_length: Option<Py<PyAny>>,
    pattern: Option<String>,
    deprecated: Option<Py<PyAny>>,
    include_in_schema: bool,
) -> PyResult<Py<ParameterMetadata>> {
    let ellipsis = py.Ellipsis();
    let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
    let default = if default.bind(py).is(ellipsis.bind(py)) || default.bind(py).is(&undefined) {
        None
    } else {
        Some(default)
    };
    Py::new(
        py,
        ParameterMetadata {
            kind: "query".to_owned(),
            alias,
            dependency: None,
            default,
            media_type: None,
            title,
            description,
            pattern,
            deprecated,
            include_in_schema,
            gt,
            lt,
            min_length,
            max_length,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

#[pyfunction(name = "Path", signature = (*, gt = None))]
fn path(py: Python<'_>, gt: Option<Py<PyAny>>) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "path".to_owned(),
            alias: None,
            dependency: None,
            default: None,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
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
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

// lint-exception: Preserve PydanticUndefined as the exact required-default sentinel.
#[expect(
    clippy::expect_used,
    reason = "pydantic-core is a required target runtime dependency"
)]
fn form_file_undefined_default() -> Py<PyAny> {
    Python::attach(|py| {
        py.import("pydantic_core")
            .and_then(|module| module.getattr("PydanticUndefined"))
            .expect("pydantic-core is required for FastAPI parameter defaults")
            .unbind()
    })
}

fn normalize_undefined_default(py: Python<'_>, default: Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
    let ellipsis = py.Ellipsis();
    let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
    if default.bind(py).is(ellipsis.bind(py)) || default.bind(py).is(&undefined) {
        Ok(None)
    } else {
        Ok(Some(default))
    }
}

#[pyfunction(
    name = "Form",
    signature = (
        default = form_file_undefined_default(),
        *,
        media_type = "application/x-www-form-urlencoded",
        alias = None,
        description = None
    )
)]
fn form(
    py: Python<'_>,
    default: Py<PyAny>,
    media_type: &str,
    alias: Option<String>,
    description: Option<String>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "form".to_owned(),
            alias,
            dependency: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

#[pyfunction(
    name = "File",
    signature = (
        default = form_file_undefined_default(),
        *,
        media_type = "multipart/form-data",
        alias = None,
        description = None
    )
)]
fn file(
    py: Python<'_>,
    default: Py<PyAny>,
    media_type: &str,
    alias: Option<String>,
    description: Option<String>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "file".to_owned(),
            alias,
            dependency: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            lt: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
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
    module.add_function(wrap_pyfunction!(path, module)?)?;
    module.add_function(wrap_pyfunction!(body, module)?)?;
    module.add_function(wrap_pyfunction!(form, module)?)?;
    module.add_function(wrap_pyfunction!(file, module)?)?;

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
