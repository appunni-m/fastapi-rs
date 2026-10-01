//! Rust-owned Python metadata for FastAPI parameters and dependencies.

use pyo3::prelude::*;
use pyo3::types::PyModule;

/// Metadata attached to an endpoint annotation through `typing.Annotated`.
#[pyclass(name = "_ParameterMetadata", module = "fastapi_rs._core")]
pub(crate) struct ParameterMetadata {
    kind: String,
    alias: Option<String>,
    validation_alias: Option<Py<PyAny>>,
    embed: Option<bool>,
    dependency: Option<Py<PyAny>>,
    default: Option<Py<PyAny>>,
    media_type: Option<String>,
    title: Option<String>,
    description: Option<String>,
    pattern: Option<String>,
    deprecated: Option<Py<PyAny>>,
    include_in_schema: bool,
    gt: Option<Py<PyAny>>,
    ge: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    le: Option<Py<PyAny>>,
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
    fn validation_alias(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.validation_alias
            .as_ref()
            .map(|validation_alias| validation_alias.clone_ref(py))
    }

    #[getter]
    fn embed(&self) -> Option<bool> {
        self.embed
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
    fn ge(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.ge.as_ref().map(|ge| ge.clone_ref(py))
    }

    #[getter]
    fn lt(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.lt.as_ref().map(|lt| lt.clone_ref(py))
    }

    #[getter]
    fn le(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.le.as_ref().map(|le| le.clone_ref(py))
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
            validation_alias: None,
            embed: None,
            dependency: Some(dependency),
            default: None,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache,
        },
    )
}

#[pyfunction(
    name = "Header",
    signature = (default = query_ellipsis_default(), *, alias = None, convert_underscores = true)
)]
fn header(
    py: Python<'_>,
    default: Py<PyAny>,
    alias: Option<String>,
    convert_underscores: bool,
) -> PyResult<Py<ParameterMetadata>> {
    let default = optional_parameter_default(py, default)?;
    Py::new(
        py,
        ParameterMetadata {
            kind: "header".to_owned(),
            alias,
            validation_alias: None,
            embed: None,
            dependency: None,
            default,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
            min_length: None,
            max_length: None,
            convert_underscores,
            use_cache: true,
        },
    )
}

#[pyfunction(name = "Cookie", signature = (default = query_ellipsis_default(), *, alias = None))]
fn cookie(
    py: Python<'_>,
    default: Py<PyAny>,
    alias: Option<String>,
) -> PyResult<Py<ParameterMetadata>> {
    let default = optional_parameter_default(py, default)?;
    Py::new(
        py,
        ParameterMetadata {
            kind: "cookie".to_owned(),
            alias,
            validation_alias: None,
            embed: None,
            dependency: None,
            default,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
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

fn optional_parameter_default(py: Python<'_>, default: Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
    let default = default.bind(py);
    let ellipsis = py.Ellipsis();
    let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
    if default.is(ellipsis.bind(py)) || default.is(&undefined) {
        Ok(None)
    } else {
        Ok(Some(default.clone().unbind()))
    }
}

#[pyfunction(
    name = "Query",
    signature = (
        default = query_ellipsis_default(),
        *,
        alias = None,
        validation_alias = None,
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
    validation_alias: Option<Py<PyAny>>,
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
            validation_alias,
            embed: None,
            dependency: None,
            default,
            media_type: None,
            title,
            description,
            pattern,
            deprecated,
            include_in_schema,
            gt,
            ge: None,
            lt,
            le: None,
            min_length,
            max_length,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

#[pyfunction(name = "Path", signature = (*, gt = None, ge = None, lt = None, le = None))]
fn path(
    py: Python<'_>,
    gt: Option<Py<PyAny>>,
    ge: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    le: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "path".to_owned(),
            alias: None,
            validation_alias: None,
            embed: None,
            dependency: None,
            default: None,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt,
            ge,
            lt,
            le,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

#[pyfunction(
    name = "Body",
    signature = (*, embed = None, alias = None, validation_alias = None, gt = None)
)]
fn body(
    py: Python<'_>,
    embed: Option<bool>,
    alias: Option<String>,
    validation_alias: Option<Py<PyAny>>,
    gt: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    Py::new(
        py,
        ParameterMetadata {
            kind: "body".to_owned(),
            alias,
            validation_alias,
            embed,
            dependency: None,
            default: None,
            media_type: None,
            title: None,
            description: None,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt,
            ge: None,
            lt: None,
            le: None,
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
            validation_alias: None,
            embed: None,
            dependency: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
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
            validation_alias: None,
            embed: None,
            dependency: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description,
            pattern: None,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
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

    let status = py.import("starlette.status")?;
    module.add_submodule(&status)?;
    Ok(())
}
