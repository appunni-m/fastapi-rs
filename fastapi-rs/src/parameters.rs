//! Rust-owned Python metadata for FastAPI parameters and dependencies.

use pyo3::exceptions::PyAssertionError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyList, PyModule, PyString, PyTuple};

static EXAMPLE_UNSET: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
const EXAMPLE_DEPRECATION_WARNING: &str =
    "`example` has been deprecated, please use `examples` instead";
const REGEX_DEPRECATION_WARNING: &str = "`regex` has been deprecated, please use `pattern` instead";
const FASTAPI_FILE_REGEX_WARNING_PATH: &str = "fastapi/param_functions.py";
const FASTAPI_FILE_REGEX_WARNING_LINE: u32 = 2249;

#[pyclass(name = "_ParameterUnset", module = "fastapi_rs._core")]
struct ParameterUnset;

#[pymethods]
impl ParameterUnset {
    fn __repr__(&self) -> &'static str {
        "_Unset"
    }
}

/// Metadata attached to an endpoint annotation through `typing.Annotated`.
#[pyclass(name = "_ParameterMetadata", module = "fastapi_rs._core")]
pub(crate) struct ParameterMetadata {
    kind: String,
    alias: Option<String>,
    validation_alias: Option<Py<PyAny>>,
    embed: Option<bool>,
    dependency: Option<Py<PyAny>>,
    scope: Option<String>,
    scopes: Option<Py<PyAny>>,
    default: Option<Py<PyAny>>,
    media_type: Option<String>,
    title: Option<String>,
    description: Option<String>,
    pattern: Option<String>,
    example: Option<Py<PyAny>>,
    examples: Option<Py<PyAny>>,
    deprecated: Option<Py<PyAny>>,
    include_in_schema: bool,
    gt: Option<Py<PyAny>>,
    ge: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    le: Option<Py<PyAny>>,
    allow_inf_nan: Option<Py<PyAny>>,
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
    fn scope(&self) -> Option<String> {
        self.scope.clone()
    }

    #[getter]
    fn scopes(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.scopes.as_ref().map(|scopes| scopes.clone_ref(py))
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
    fn example(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.example.as_ref().map(|example| example.clone_ref(py))
    }

    #[getter]
    fn examples(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.examples
            .as_ref()
            .map(|examples| examples.clone_ref(py))
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
    fn allow_inf_nan(&self, py: Python<'_>) -> Option<Py<PyAny>> {
        self.allow_inf_nan
            .as_ref()
            .map(|allow_inf_nan| allow_inf_nan.clone_ref(py))
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

// lint-exception: this sentinel is initialized before any constructor defaults are created.
#[expect(
    clippy::expect_used,
    reason = "constructor signatures are registered after the sentinel is initialized"
)]
fn example_unset_default() -> Py<PyAny> {
    Python::attach(|py| {
        EXAMPLE_UNSET
            .get(py)
            .expect("parameter example sentinel must be initialized before registration")
            .clone_ref(py)
    })
}

fn warn_parameter_deprecation(py: Python<'_>, message: &str) -> PyResult<()> {
    warn_parameter_deprecation_at_level(py, message, 1)
}

fn warn_body_parameter_deprecation(py: Python<'_>, message: &str) -> PyResult<()> {
    warn_parameter_deprecation_at_level(py, message, 2)
}

fn warn_parameter_deprecation_at_level(
    py: Python<'_>,
    message: &str,
    stacklevel: usize,
) -> PyResult<()> {
    let warnings = py.import("warnings")?;
    let category = crate::errors::fastapi_deprecation_warning_type(py);
    let kwargs = PyDict::new(py);
    kwargs.set_item("stacklevel", stacklevel)?;
    warnings
        .getattr("warn")?
        .call((message, category), Some(&kwargs))?;
    Ok(())
}

fn warn_fastapi_file_regex_deprecation(py: Python<'_>) -> PyResult<()> {
    let warnings = py.import("warnings")?;
    let category = crate::errors::fastapi_deprecation_warning_type(py);
    warnings.getattr("warn_explicit")?.call1((
        REGEX_DEPRECATION_WARNING,
        category,
        FASTAPI_FILE_REGEX_WARNING_PATH,
        FASTAPI_FILE_REGEX_WARNING_LINE,
    ))?;
    Ok(())
}

fn normalize_pattern(pattern: Option<String>, regex: Option<String>) -> Option<String> {
    pattern.filter(|value| !value.is_empty()).or(regex)
}

// lint-exception: every exposed constructor is registered after the sentinel initialization.
#[expect(
    clippy::expect_used,
    reason = "parameter calls cannot run before constructor registration completes"
)]
fn is_example_unset(py: Python<'_>, example: &Py<PyAny>) -> bool {
    let unset = EXAMPLE_UNSET
        .get(py)
        .expect("parameter example sentinel must be initialized before use");
    example.bind(py).is(unset.bind(py))
}

fn normalized_example(example: Py<PyAny>, py: Python<'_>) -> Option<Py<PyAny>> {
    if is_example_unset(py, &example) {
        None
    } else {
        Some(example)
    }
}

#[pyfunction(name = "Depends", signature = (*args, **kwargs))]
fn depends(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    crate::dependency_records::depends_factory(py, args, kwargs)
}

#[pyfunction(name = "Security", signature = (*args, **kwargs))]
fn security(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    crate::dependency_records::security_factory(py, args, kwargs)
}

#[pyfunction(
    name = "Header",
    signature = (
        default = query_ellipsis_default(),
        *,
        alias = None,
        convert_underscores = true,
        pattern = None,
        regex = None,
        example = example_unset_default(),
        examples = None
    )
)]
// lint-exception: PyO3 needs one Rust argument per FastAPI-compatible Header keyword.
#[allow(
    clippy::too_many_arguments,
    reason = "preserve FastAPI Header's public keyword signature"
)]
fn header(
    py: Python<'_>,
    default: Py<PyAny>,
    alias: Option<String>,
    convert_underscores: bool,
    pattern: Option<String>,
    regex: Option<String>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    let default = optional_parameter_default(py, default)?;
    if !is_example_unset(py, &example) {
        warn_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        warn_parameter_deprecation(py, REGEX_DEPRECATION_WARNING)?;
    }
    Py::new(
        py,
        ParameterMetadata {
            kind: "header".to_owned(),
            alias,
            validation_alias: None,
            embed: None,
            dependency: None,
            scope: None,
            scopes: None,
            default,
            media_type: None,
            title: None,
            description: None,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
            allow_inf_nan: None,
            min_length: None,
            max_length: None,
            convert_underscores,
            use_cache: true,
        },
    )
}

#[pyfunction(
    name = "Cookie",
    signature = (
        default = query_ellipsis_default(),
        *,
        alias = None,
        pattern = None,
        regex = None,
        example = example_unset_default(),
        examples = None
    )
)]
fn cookie(
    py: Python<'_>,
    default: Py<PyAny>,
    alias: Option<String>,
    pattern: Option<String>,
    regex: Option<String>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    let default = optional_parameter_default(py, default)?;
    if !is_example_unset(py, &example) {
        warn_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        warn_parameter_deprecation(py, REGEX_DEPRECATION_WARNING)?;
    }
    Py::new(
        py,
        ParameterMetadata {
            kind: "cookie".to_owned(),
            alias,
            validation_alias: None,
            embed: None,
            dependency: None,
            scope: None,
            scopes: None,
            default,
            media_type: None,
            title: None,
            description: None,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
            allow_inf_nan: None,
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
        ge = None,
        lt = None,
        le = None,
        min_length = None,
        max_length = None,
        pattern = None,
        deprecated = None,
        include_in_schema = true,
        regex = None,
        example = example_unset_default(),
        examples = None
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
    ge: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    le: Option<Py<PyAny>>,
    min_length: Option<Py<PyAny>>,
    max_length: Option<Py<PyAny>>,
    pattern: Option<String>,
    deprecated: Option<Py<PyAny>>,
    include_in_schema: bool,
    regex: Option<String>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    if !is_example_unset(py, &example) {
        warn_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        warn_parameter_deprecation(py, REGEX_DEPRECATION_WARNING)?;
    }
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
            scope: None,
            scopes: None,
            default,
            media_type: None,
            title,
            description,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated,
            include_in_schema,
            gt,
            ge,
            lt,
            le,
            allow_inf_nan: None,
            min_length,
            max_length,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

#[pyfunction(
    name = "Path",
    signature = (
        default = query_ellipsis_default(),
        *,
        alias = None,
        gt = None,
        ge = None,
        lt = None,
        le = None,
        pattern = None,
        regex = None,
        example = example_unset_default(),
        examples = None
    )
)]
// lint-exception: PyO3 needs one Rust argument per FastAPI-compatible Path keyword.
#[allow(
    clippy::too_many_arguments,
    reason = "preserve FastAPI Path's public keyword signature"
)]
fn path(
    py: Python<'_>,
    default: Py<PyAny>,
    alias: Option<String>,
    gt: Option<Py<PyAny>>,
    ge: Option<Py<PyAny>>,
    lt: Option<Py<PyAny>>,
    le: Option<Py<PyAny>>,
    pattern: Option<String>,
    regex: Option<String>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    if !default.bind(py).is(py.Ellipsis().bind(py)) {
        return Err(PyAssertionError::new_err(
            "Path parameters cannot have a default value",
        ));
    }
    if !is_example_unset(py, &example) {
        warn_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        warn_parameter_deprecation(py, REGEX_DEPRECATION_WARNING)?;
    }
    Py::new(
        py,
        ParameterMetadata {
            kind: "path".to_owned(),
            alias,
            validation_alias: None,
            embed: None,
            dependency: None,
            scope: None,
            scopes: None,
            default: None,
            media_type: None,
            title: None,
            description: None,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated: None,
            include_in_schema: true,
            gt,
            ge,
            lt,
            le,
            allow_inf_nan: None,
            min_length: None,
            max_length: None,
            convert_underscores: true,
            use_cache: true,
        },
    )
}

#[pyfunction(
    name = "Body",
    signature = (
        default = form_file_undefined_default(),
        *,
        embed = None,
        media_type = "application/json",
        alias = None,
        validation_alias = None,
        gt = None,
        pattern = None,
        regex = None,
        allow_inf_nan = None,
        example = example_unset_default(),
        examples = None
    )
)]
// lint-exception: retain the directly callable FastAPI Body option names.
#[allow(
    clippy::too_many_arguments,
    reason = "preserve FastAPI Body keyword compatibility"
)]
fn body(
    py: Python<'_>,
    default: Py<PyAny>,
    embed: Option<bool>,
    media_type: &str,
    alias: Option<String>,
    validation_alias: Option<Py<PyAny>>,
    gt: Option<Py<PyAny>>,
    pattern: Option<String>,
    regex: Option<String>,
    allow_inf_nan: Option<Py<PyAny>>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    if !is_example_unset(py, &example) {
        warn_body_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        warn_body_parameter_deprecation(py, REGEX_DEPRECATION_WARNING)?;
    }
    Py::new(
        py,
        ParameterMetadata {
            kind: "body".to_owned(),
            alias,
            validation_alias,
            embed,
            dependency: None,
            scope: None,
            scopes: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description: None,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated: None,
            include_in_schema: true,
            gt,
            ge: None,
            lt: None,
            le: None,
            allow_inf_nan,
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
        validation_alias = None,
        description = None,
        pattern = None,
        regex = None,
        example = example_unset_default(),
        examples = None
    )
)]
// lint-exception: retain FastAPI Form's directly callable compatibility options.
#[allow(
    clippy::too_many_arguments,
    reason = "preserve FastAPI Form keyword compatibility"
)]
fn form(
    py: Python<'_>,
    default: Py<PyAny>,
    media_type: &str,
    alias: Option<String>,
    validation_alias: Option<Py<PyAny>>,
    description: Option<String>,
    pattern: Option<String>,
    regex: Option<String>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    if !is_example_unset(py, &example) {
        warn_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        warn_parameter_deprecation(py, REGEX_DEPRECATION_WARNING)?;
    }
    Py::new(
        py,
        ParameterMetadata {
            kind: "form".to_owned(),
            alias,
            validation_alias,
            embed: None,
            dependency: None,
            scope: None,
            scopes: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
            allow_inf_nan: None,
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
        validation_alias = None,
        description = None,
        pattern = None,
        regex = None,
        example = example_unset_default(),
        examples = None
    )
)]
// lint-exception: retain FastAPI File's directly callable compatibility options.
#[allow(
    clippy::too_many_arguments,
    reason = "preserve FastAPI File keyword compatibility"
)]
fn file(
    py: Python<'_>,
    default: Py<PyAny>,
    media_type: &str,
    alias: Option<String>,
    validation_alias: Option<Py<PyAny>>,
    description: Option<String>,
    pattern: Option<String>,
    regex: Option<String>,
    example: Py<PyAny>,
    examples: Option<Py<PyAny>>,
) -> PyResult<Py<ParameterMetadata>> {
    if !is_example_unset(py, &example) {
        warn_parameter_deprecation(py, EXAMPLE_DEPRECATION_WARNING)?;
    }
    if regex.is_some() {
        // Match FastAPI 0.141.1's public File wrapper, which emits this warning
        // from its params.File call at param_functions.py:2249.
        warn_fastapi_file_regex_deprecation(py)?;
    }
    Py::new(
        py,
        ParameterMetadata {
            kind: "file".to_owned(),
            alias,
            validation_alias,
            embed: None,
            dependency: None,
            scope: None,
            scopes: None,
            default: normalize_undefined_default(py, default)?,
            media_type: Some(media_type.to_owned()),
            title: None,
            description,
            pattern: normalize_pattern(pattern, regex),
            example: normalized_example(example, py),
            examples,
            deprecated: None,
            include_in_schema: true,
            gt: None,
            ge: None,
            lt: None,
            le: None,
            allow_inf_nan: None,
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
    module.add_class::<ParameterUnset>()?;
    EXAMPLE_UNSET.get_or_try_init(py, || Py::new(py, ParameterUnset).map(Py::into_any))?;
    module.add_class::<ParameterMetadata>()?;
    let depends_function = wrap_pyfunction!(depends, module)?;
    let depends = py
        .import("functools")?
        .getattr("partial")?
        .call1((depends_function,))?;
    set_depends_signature(py, &depends)?;
    let security_function = wrap_pyfunction!(security, module)?;
    let security = py
        .import("functools")?
        .getattr("partial")?
        .call1((security_function,))?;
    set_security_signature(py, &security, &depends)?;
    module.add("Depends", depends)?;
    module.add("Security", security)?;
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

fn set_depends_signature(py: Python<'_>, function: &Bound<'_, PyAny>) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let typing = py.import("typing")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let annotated = typing.getattr("Annotated")?;
    let dependency_doc = annotated_doc.call1((r#"
            A "dependable" callable (like a function).

            Don't call it directly, FastAPI will call it for you, just pass the object
            directly.

            Read more about it in the
            [FastAPI docs for Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
            "#,))?;
    let cache_doc = annotated_doc.call1((
        r#"
            By default, after a dependency is called the first time in a request, if
            the dependency is declared again for the rest of the request (for example
            if the dependency is needed by several dependencies), the value will be
            re-used for the rest of the request.

            Set `use_cache` to `False` to disable this behavior and ensure the
            dependency is called again (if declared more than once) in the same request.

            Read more about it in the
            [FastAPI docs about sub-dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/#using-the-same-dependency-multiple-times)
            "#,
    ))?;
    let scope_doc = annotated_doc.call1((
        r#"
            Mainly for dependencies with `yield`, define when the dependency function
            should start (the code before `yield`) and when it should end (the code
            after `yield`).

            * `"function"`: start the dependency before the *path operation function*
                that handles the request, end the dependency after the *path operation
                function* ends, but **before** the response is sent back to the client.
                So, the dependency function will be executed **around** the *path operation
                **function***.
            * `"request"`: start the dependency before the *path operation function*
                that handles the request (similar to when using `"function"`), but end
                **after** the response is sent back to the client. So, the dependency
                function will be executed **around** the **request** and response cycle.

            Read more about it in the
            [FastAPI docs for FastAPI Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#early-exit-and-scope)
            "#,
    ))?;

    let any_type = typing.getattr("Any")?;
    let callable_type = py.import("collections.abc")?.getattr("Callable")?;
    let ellipsis = py.Ellipsis().into_bound(py);
    let callable_args = PyTuple::new(py, [ellipsis, any_type.clone()])?;
    let callable_type = callable_type.get_item(callable_args)?;
    let none_type = py.None().bind(py).get_type();
    let optional_callable = py
        .import("operator")?
        .getattr("or_")?
        .call1((callable_type, none_type.clone()))?;
    let dependency_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_callable.as_any(), dependency_doc.as_any()],
        )?,))?;
    let cache_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [
                py.get_type::<pyo3::types::PyBool>().as_any(),
                cache_doc.as_any(),
            ],
        )?,))?;

    let literal_values = PyTuple::new(
        py,
        [
            PyString::new(py, "function").as_any(),
            PyString::new(py, "request").as_any(),
        ],
    )?;
    let literal_scope = typing
        .getattr("Literal")?
        .getattr("__getitem__")?
        .call1((literal_values,))?;
    let optional_scope = literal_scope.call_method1("__or__", (none_type,))?;
    let scope_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_scope.as_any(), scope_doc.as_any()],
        )?,))?;

    let parameter_type = inspect.getattr("Parameter")?;
    let positional_or_keyword = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let keyword_only = parameter_type.getattr("KEYWORD_ONLY")?;
    let dependency_kwargs = PyDict::new(py);
    dependency_kwargs.set_item("annotation", dependency_annotation.clone())?;
    dependency_kwargs.set_item("default", py.None())?;
    let dependency = parameter_type.call(
        ("dependency", positional_or_keyword),
        Some(&dependency_kwargs),
    )?;
    let cache_kwargs = PyDict::new(py);
    cache_kwargs.set_item("annotation", cache_annotation.clone())?;
    cache_kwargs.set_item("default", true)?;
    let use_cache =
        parameter_type.call(("use_cache", keyword_only.clone()), Some(&cache_kwargs))?;
    let scope_kwargs = PyDict::new(py);
    scope_kwargs.set_item("annotation", scope_annotation.clone())?;
    scope_kwargs.set_item("default", py.None())?;
    let scope = parameter_type.call(("scope", keyword_only), Some(&scope_kwargs))?;
    let parameters = PyList::new(py, [dependency, use_cache, scope])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", any_type.clone())?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    let annotations = PyDict::new(py);
    annotations.set_item("dependency", dependency_annotation)?;
    annotations.set_item("use_cache", cache_annotation)?;
    annotations.set_item("scope", scope_annotation)?;
    annotations.set_item("return", any_type)?;
    function.setattr("__signature__", signature)?;
    function.setattr("__annotations__", annotations)?;
    function.setattr("__module__", "fastapi.param_functions")?;
    function.setattr("__name__", "Depends")?;
    function.setattr("__qualname__", "Depends")?;
    function.setattr(
        "__doc__",
        r#"
    Declare a FastAPI dependency.

    It takes a single "dependable" callable (like a function).

    Don't call it directly, FastAPI will call it for you.

    Read more about it in the
    [FastAPI docs for Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/).

    **Example**

    ```python
    from typing import Annotated

    from fastapi import Depends, FastAPI

    app = FastAPI()


    async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
        return {"q": q, "skip": skip, "limit": limit}


    @app.get("/items/")
    async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
        return commons
    ```
    "#,
    )?;
    Ok(())
}

fn set_security_signature(
    py: Python<'_>,
    function: &Bound<'_, PyAny>,
    depends_function: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let typing = py.import("typing")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let annotated = typing.getattr("Annotated")?;
    let dependency_parameters = inspect
        .getattr("signature")?
        .call1((depends_function,))?
        .getattr("parameters")?;
    let dependency = dependency_parameters.get_item("dependency")?;
    let use_cache = dependency_parameters.get_item("use_cache")?;
    let dependency_annotation = dependency.getattr("annotation")?;
    let cache_annotation = use_cache.getattr("annotation")?;

    let scopes_doc = annotated_doc.call1((r#"
            OAuth2 scopes required for the *path operation* that uses this Security
            dependency.

            The term "scope" comes from the OAuth2 specification, it seems to be
            intentionally vague and interpretable. It normally refers to permissions,
            in cases to roles.

            These scopes are integrated with OpenAPI (and the API docs at `/docs`).
            So they are visible in the OpenAPI specification.

            Read more about it in the
            [FastAPI docs about OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
            "#,
    ))?;
    let sequence_type = py.import("collections.abc")?.getattr("Sequence")?;
    let string_type = py.import("builtins")?.getattr("str")?;
    let sequence_string = sequence_type.get_item(string_type)?;
    let none_type = py.None().bind(py).get_type();
    let optional_scopes = py
        .import("operator")?
        .getattr("or_")?
        .call1((sequence_string, none_type))?;
    let scopes_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_scopes.as_any(), scopes_doc.as_any()],
        )?,))?;

    let parameter_type = inspect.getattr("Parameter")?;
    let keyword_only = parameter_type.getattr("KEYWORD_ONLY")?;
    let scopes_kwargs = PyDict::new(py);
    scopes_kwargs.set_item("annotation", scopes_annotation.clone())?;
    scopes_kwargs.set_item("default", py.None())?;
    let scopes = parameter_type.call(("scopes", keyword_only.clone()), Some(&scopes_kwargs))?;
    let parameters = PyList::new(py, [dependency, scopes, use_cache])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", typing.getattr("Any")?)?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    let annotations = PyDict::new(py);
    annotations.set_item("dependency", dependency_annotation)?;
    annotations.set_item("scopes", scopes_annotation)?;
    annotations.set_item("use_cache", cache_annotation)?;
    annotations.set_item("return", typing.getattr("Any")?)?;
    function.setattr("__signature__", signature)?;
    function.setattr("__annotations__", annotations)?;
    function.setattr("__module__", "fastapi.param_functions")?;
    function.setattr("__name__", "Security")?;
    function.setattr("__qualname__", "Security")?;
    function.setattr("__doc__", "Declare a FastAPI Security dependency.")?;
    Ok(())
}
