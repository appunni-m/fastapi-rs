//! Rust-owned FastAPI parameter classes backed by Pydantic FieldInfo.

use pyo3::exceptions::{PyAssertionError, PyRuntimeError, PyTypeError};
use std::cell::Cell;

use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyList, PyModule, PyString, PyTuple, PyType};

static PARAM_TYPES: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static PARAM_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static PATH_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static QUERY_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static HEADER_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static COOKIE_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static BODY_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static FORM_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static FILE_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static PARAMETER_UNSET: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

thread_local! {
    static ROOT_FACTORY_ORIGIN: Cell<Option<ParameterClassKind>> = const { Cell::new(None) };
}

const EXAMPLE_WARNING: &str = "`example` has been deprecated, please use `examples` instead";
const REGEX_WARNING: &str = "`regex` has been deprecated, please use `pattern` instead";
const REGEX_DEPRECATION: &str =
    "Deprecated in FastAPI 0.100.0 and Pydantic v2, use `pattern` instead.";
const EXAMPLE_DEPRECATION: &str = "Deprecated in OpenAPI 3.1.0 that now uses JSON Schema 2020-12, although still supported. Use examples instead.";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum ParameterClassKind {
    Param,
    Path,
    Query,
    Header,
    Cookie,
    Body,
    Form,
    File,
}

impl ParameterClassKind {
    fn name(self) -> &'static str {
        match self {
            Self::Param => "Param",
            Self::Path => "Path",
            Self::Query => "Query",
            Self::Header => "Header",
            Self::Cookie => "Cookie",
            Self::Body => "Body",
            Self::Form => "Form",
            Self::File => "File",
        }
    }

    fn class_cell(self) -> &'static PyOnceLock<Py<PyType>> {
        match self {
            Self::Param => &PARAM_CLASS,
            Self::Path => &PATH_CLASS,
            Self::Query => &QUERY_CLASS,
            Self::Header => &HEADER_CLASS,
            Self::Cookie => &COOKIE_CLASS,
            Self::Body => &BODY_CLASS,
            Self::Form => &FORM_CLASS,
            Self::File => &FILE_CLASS,
        }
    }

    fn parent(self) -> Option<Self> {
        match self {
            Self::Path | Self::Query | Self::Header | Self::Cookie => Some(Self::Param),
            Self::Form => Some(Self::Body),
            Self::File => Some(Self::Form),
            Self::Param | Self::Body => None,
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ParameterMethodKind {
    Init,
    Repr,
}

#[pyclass(name = "_ParameterMethod", module = "fastapi_rs._core", dict)]
struct ParameterMethod {
    class: ParameterClassKind,
    method: ParameterMethodKind,
    defaults: Option<Py<PyTuple>>,
    keyword_defaults: Option<Py<PyDict>>,
}

#[pymethods]
impl ParameterMethod {
    fn __get__(
        slf: Py<Self>,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        owner: Option<Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        match instance {
            Some(instance) => py
                .import("types")?
                .getattr("MethodType")?
                .call1((slf, instance))
                .map(Bound::unbind),
            None if owner.is_some() => Ok(slf.into_any()),
            None => Err(PyTypeError::new_err("__get__(None, None) is invalid")),
        }
    }

    #[getter(__defaults__)]
    fn get_defaults(&self, py: Python<'_>) -> Py<PyAny> {
        self.defaults
            .as_ref()
            .map_or_else(|| py.None(), |value| value.clone_ref(py).into_any())
    }

    #[setter(__defaults__)]
    fn set_defaults(&mut self, py: Python<'_>, value: Bound<'_, PyAny>) -> PyResult<()> {
        if value.is_none() {
            self.defaults = None;
            return Ok(());
        }
        let tuple = value
            .cast_into::<PyTuple>()
            .map_err(|_| PyTypeError::new_err("__defaults__ must be set to a tuple object"))?;
        let maximum = match self.method {
            ParameterMethodKind::Init => 2,
            ParameterMethodKind::Repr => 1,
        };
        if tuple.len() > maximum {
            return Err(PyTypeError::new_err(
                "__defaults__ length must be less than or equal to the number of positional arguments",
            ));
        }
        self.defaults = Some(tuple.unbind());
        let _ = py;
        Ok(())
    }

    #[getter(__kwdefaults__)]
    fn get_keyword_defaults(&self, py: Python<'_>) -> Py<PyAny> {
        self.keyword_defaults
            .as_ref()
            .map_or_else(|| py.None(), |value| value.clone_ref(py).into_any())
    }

    #[setter(__kwdefaults__)]
    fn set_keyword_defaults(&mut self, py: Python<'_>, value: Bound<'_, PyAny>) -> PyResult<()> {
        if value.is_none() {
            self.keyword_defaults = None;
            return Ok(());
        }
        let dict = value
            .cast_into::<PyDict>()
            .map_err(|_| PyTypeError::new_err("__kwdefaults__ must be set to a dict object"))?;
        self.keyword_defaults = Some(dict.unbind());
        let _ = py;
        Ok(())
    }

    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        slf: Py<Self>,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let (class, method) = {
            let borrowed = slf.borrow(py);
            (borrowed.class, borrowed.method)
        };
        let values = bind_method_arguments(py, slf.bind(py).as_any(), class, method, args, kwargs)?;
        match method {
            ParameterMethodKind::Init => initialize_parameter(py, class, &values),
            ParameterMethodKind::Repr => parameter_repr(py, &values[0]),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ParameterKind {
    PositionalOrKeyword,
    KeywordOnly,
    VariableKeyword,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum DefaultKind {
    Required,
    Undefined,
    Ellipsis,
    Unset,
    None,
    True,
    JsonMediaType,
    FormMediaType,
    FileMediaType,
}

#[derive(Clone, Copy)]
struct ParameterSpec {
    name: &'static str,
    annotation: &'static str,
    kind: ParameterKind,
    default: DefaultKind,
}

type ParameterSignatureParts<'py> = (
    Bound<'py, PyAny>,
    Bound<'py, PyDict>,
    Bound<'py, PyTuple>,
    Bound<'py, PyDict>,
);

fn parameter_specs(class: ParameterClassKind) -> Vec<ParameterSpec> {
    let default = if class == ParameterClassKind::Path {
        DefaultKind::Ellipsis
    } else {
        DefaultKind::Undefined
    };
    let mut specs = vec![ParameterSpec {
        name: "default",
        annotation: "Any",
        kind: ParameterKind::PositionalOrKeyword,
        default,
    }];
    specs.push(ParameterSpec {
        name: "default_factory",
        annotation: "CallableNone",
        kind: ParameterKind::KeywordOnly,
        default: DefaultKind::Unset,
    });
    specs.push(ParameterSpec {
        name: "annotation",
        annotation: "OptionalAny",
        kind: ParameterKind::KeywordOnly,
        default: DefaultKind::None,
    });
    if matches!(
        class,
        ParameterClassKind::Body | ParameterClassKind::Form | ParameterClassKind::File
    ) {
        if class == ParameterClassKind::Body {
            specs.push(ParameterSpec {
                name: "embed",
                annotation: "OptionalBool",
                kind: ParameterKind::KeywordOnly,
                default: DefaultKind::None,
            });
        }
        specs.push(ParameterSpec {
            name: "media_type",
            annotation: "Str",
            kind: ParameterKind::KeywordOnly,
            default: match class {
                ParameterClassKind::Body => DefaultKind::JsonMediaType,
                ParameterClassKind::Form => DefaultKind::FormMediaType,
                ParameterClassKind::File => DefaultKind::FileMediaType,
                _ => DefaultKind::Required,
            },
        });
    }
    let common = [
        ("alias", "OptionalStr", DefaultKind::None),
        ("alias_priority", "OptionalInt", DefaultKind::Unset),
        ("validation_alias", "ValidationAlias", DefaultKind::None),
        ("serialization_alias", "OptionalStr", DefaultKind::None),
    ];
    for (name, annotation, default) in common {
        specs.push(ParameterSpec {
            name,
            annotation,
            kind: ParameterKind::KeywordOnly,
            default,
        });
    }
    if class == ParameterClassKind::Header {
        specs.push(ParameterSpec {
            name: "convert_underscores",
            annotation: "Bool",
            kind: ParameterKind::KeywordOnly,
            default: DefaultKind::True,
        });
    }
    let metadata = [
        ("title", "OptionalStr", DefaultKind::None),
        ("description", "OptionalStr", DefaultKind::None),
        ("gt", "OptionalFloat", DefaultKind::None),
        ("ge", "OptionalFloat", DefaultKind::None),
        ("lt", "OptionalFloat", DefaultKind::None),
        ("le", "OptionalFloat", DefaultKind::None),
        ("min_length", "OptionalInt", DefaultKind::None),
        ("max_length", "OptionalInt", DefaultKind::None),
        ("pattern", "OptionalStr", DefaultKind::None),
        ("regex", "RegexAnnotated", DefaultKind::None),
        ("discriminator", "OptionalStr", DefaultKind::None),
        ("strict", "OptionalBool", DefaultKind::Unset),
        ("multiple_of", "OptionalFloat", DefaultKind::Unset),
        ("allow_inf_nan", "OptionalBool", DefaultKind::Unset),
        ("max_digits", "OptionalInt", DefaultKind::Unset),
        ("decimal_places", "OptionalInt", DefaultKind::Unset),
        ("examples", "ListAny", DefaultKind::None),
        ("example", "ExampleAnnotated", DefaultKind::Unset),
        ("openapi_examples", "OpenApiExamples", DefaultKind::None),
        ("deprecated", "DeprecatedAnnotation", DefaultKind::None),
        ("include_in_schema", "Bool", DefaultKind::True),
        ("json_schema_extra", "DictAny", DefaultKind::None),
    ];
    for (name, annotation, default) in metadata {
        specs.push(ParameterSpec {
            name,
            annotation,
            kind: ParameterKind::KeywordOnly,
            default,
        });
    }
    specs.push(ParameterSpec {
        name: "extra",
        annotation: "Any",
        kind: ParameterKind::VariableKeyword,
        default: DefaultKind::Required,
    });
    specs
}

fn class_type<'py>(py: Python<'py>, class: ParameterClassKind) -> PyResult<Bound<'py, PyType>> {
    let Some(value) = class.class_cell().get(py) else {
        return Err(PyRuntimeError::new_err(format!(
            "{} parameter class has not been registered",
            class.name()
        )));
    };
    Ok(value.bind(py).clone())
}

fn unset<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
    PARAMETER_UNSET
        .get(py)
        .map(|value| value.bind(py).clone())
        .ok_or_else(|| PyRuntimeError::new_err("parameter _Unset has not been registered"))
}

fn field_undefined<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
    py.import("pydantic_core")?.getattr("PydanticUndefined")
}

fn default_value<'py>(py: Python<'py>, default: DefaultKind) -> PyResult<Bound<'py, PyAny>> {
    match default {
        DefaultKind::Required => Ok(py
            .import("inspect")?
            .getattr("Parameter")?
            .getattr("empty")?),
        DefaultKind::Undefined => field_undefined(py),
        DefaultKind::Ellipsis => Ok(py.Ellipsis().into_bound(py)),
        DefaultKind::Unset => unset(py),
        DefaultKind::None => Ok(py.None().into_bound(py)),
        DefaultKind::True => Ok(true.into_pyobject(py)?.to_owned().into_any()),
        DefaultKind::JsonMediaType => Ok(PyString::new(py, "application/json").into_any()),
        DefaultKind::FormMediaType => {
            Ok(PyString::new(py, "application/x-www-form-urlencoded").into_any())
        }
        DefaultKind::FileMediaType => Ok(PyString::new(py, "multipart/form-data").into_any()),
    }
}

fn generic_item<'py>(
    base: &Bound<'py, PyAny>,
    argument: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    base.get_item(argument)
}

fn optional_annotation<'py>(
    py: Python<'py>,
    annotation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    py.import("operator")?
        .getattr("or_")?
        .call1((annotation, py.None()))
}

fn union_annotation<'py>(
    py: Python<'py>,
    annotations: &[Bound<'py, PyAny>],
) -> PyResult<Bound<'py, PyAny>> {
    let Some(first) = annotations.first() else {
        return Err(PyRuntimeError::new_err("empty annotation union"));
    };
    let or = py.import("operator")?.getattr("or_")?;
    let mut result = first.clone();
    for annotation in &annotations[1..] {
        result = or.call1((result, annotation))?;
    }
    Ok(result)
}

fn annotated_type<'py>(
    py: Python<'py>,
    annotation: &Bound<'py, PyAny>,
    metadata: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    py.import("typing")?
        .getattr("Annotated")?
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(py, [annotation, metadata])?,))
}

fn annotation_value<'py>(
    py: Python<'py>,
    module: &Bound<'py, PyModule>,
    kind: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let typing = py.import("typing")?;
    let builtins = py.import("builtins")?;
    let any = typing.getattr("Any")?;
    let str_type = builtins.getattr("str")?;
    let bool_type = builtins.getattr("bool")?;
    let int_type = builtins.getattr("int")?;
    let float_type = builtins.getattr("float")?;
    let none_type = py.None().bind(py).get_type().as_any().clone();
    match kind {
        "Any" => Ok(any),
        "Str" => Ok(str_type),
        "Bool" => Ok(bool_type),
        "CallableNone" => {
            let callable = py.import("collections.abc")?.getattr("Callable")?;
            let arguments = PyTuple::new(py, [PyList::empty(py).as_any(), any.as_any()])?;
            optional_annotation(py, &generic_item(&callable, &arguments)?)
        }
        "OptionalAny" => optional_annotation(py, &any),
        "OptionalStr" => optional_annotation(py, &str_type),
        "OptionalBool" => optional_annotation(py, &bool_type),
        "OptionalInt" => optional_annotation(py, &int_type),
        "OptionalFloat" => optional_annotation(py, &float_type),
        "ValidationAlias" => {
            let aliases = py.import("pydantic.aliases")?;
            union_annotation(
                py,
                &[
                    str_type,
                    aliases.getattr("AliasPath")?,
                    aliases.getattr("AliasChoices")?,
                    none_type,
                ],
            )
        }
        "RegexAnnotated" => {
            let deprecated_type = py.import("typing_extensions")?.getattr("deprecated")?;
            let deprecated = deprecated_type.call1((REGEX_DEPRECATION,))?;
            let optional = optional_annotation(py, &str_type)?;
            annotated_type(py, &optional, &deprecated)
        }
        "ExampleAnnotated" => {
            let deprecated_type = py.import("typing_extensions")?.getattr("deprecated")?;
            let deprecated = deprecated_type.call1((EXAMPLE_DEPRECATION,))?;
            let optional = optional_annotation(py, &any)?;
            annotated_type(py, &optional, &deprecated)
        }
        "ListAny" => {
            let list = generic_item(&builtins.getattr("list")?, &any)?;
            optional_annotation(py, &list)
        }
        "OpenApiExamples" => {
            let dict = builtins.getattr("dict")?;
            let example_type = module.getattr("Example")?;
            let arguments = PyTuple::new(py, [str_type.as_any(), &example_type])?;
            let examples = generic_item(&dict, &arguments)?;
            optional_annotation(py, &examples)
        }
        "DeprecatedAnnotation" => union_annotation(
            py,
            &[
                py.import("typing_extensions")?.getattr("deprecated")?,
                str_type,
                bool_type,
                none_type,
            ],
        ),
        "DictAny" => {
            let dict = builtins.getattr("dict")?;
            let arguments = PyTuple::new(py, [str_type.as_any(), any.as_any()])?;
            let mapping = generic_item(&dict, &arguments)?;
            optional_annotation(py, &mapping)
        }
        _ => Err(PyRuntimeError::new_err(format!(
            "unsupported parameter annotation {kind}"
        ))),
    }
}

fn build_signature<'py>(
    py: Python<'py>,
    module: &Bound<'py, PyModule>,
    class: ParameterClassKind,
    include_self: bool,
) -> PyResult<ParameterSignatureParts<'py>> {
    let specs = parameter_specs(class);
    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let parameters = PyList::empty(py);
    let annotations = PyDict::new(py);
    let kwargs_defaults = PyDict::new(py);
    let mut positional_defaults = Vec::new();

    if include_self {
        let self_kwargs = PyDict::new(py);
        parameters.append(parameter_type.call(
            ("self", parameter_type.getattr("POSITIONAL_OR_KEYWORD")?),
            Some(&self_kwargs),
        )?)?;
    }
    for spec in &specs {
        let annotation = annotation_value(py, module, spec.annotation)?;
        annotations.set_item(spec.name, &annotation)?;
        let kind = match spec.kind {
            ParameterKind::PositionalOrKeyword => {
                parameter_type.getattr("POSITIONAL_OR_KEYWORD")?
            }
            ParameterKind::KeywordOnly => parameter_type.getattr("KEYWORD_ONLY")?,
            ParameterKind::VariableKeyword => parameter_type.getattr("VAR_KEYWORD")?,
        };
        let parameter_kwargs = PyDict::new(py);
        parameter_kwargs.set_item("annotation", &annotation)?;
        if spec.kind != ParameterKind::VariableKeyword {
            let default = default_value(py, spec.default)?;
            parameter_kwargs.set_item("default", &default)?;
            if spec.kind == ParameterKind::PositionalOrKeyword {
                positional_defaults.push(default.clone());
            } else {
                kwargs_defaults.set_item(spec.name, default)?;
            }
        }
        parameters.append(parameter_type.call((spec.name, kind), Some(&parameter_kwargs))?)?;
    }
    let signature = inspect.getattr("Signature")?.call((parameters,), None)?;
    Ok((
        signature,
        annotations,
        PyTuple::new(py, positional_defaults)?,
        kwargs_defaults,
    ))
}

fn create_param_types(py: Python<'_>) -> PyResult<Py<PyType>> {
    let enum_type = py.import("enum")?.getattr("Enum")?;
    let members = PyDict::new(py);
    for name in ["query", "header", "path", "cookie"] {
        members.set_item(name, name)?;
    }
    let kwargs = PyDict::new(py);
    kwargs.set_item("module", "fastapi.params")?;
    kwargs.set_item("qualname", "ParamTypes")?;
    let class = enum_type
        .call(("ParamTypes", members), Some(&kwargs))?
        .cast_into::<PyType>()?;
    class.setattr("__qualname__", "ParamTypes")?;
    class.setattr("__doc__", py.None())?;
    Ok(class.unbind())
}

fn make_method(
    py: Python<'_>,
    module: &Bound<'_, PyModule>,
    class: ParameterClassKind,
    method: ParameterMethodKind,
) -> PyResult<Py<PyAny>> {
    let (signature, annotations, defaults, keyword_defaults) = match method {
        ParameterMethodKind::Init => build_signature(py, module, class, true)?,
        ParameterMethodKind::Repr => {
            let inspect = py.import("inspect")?;
            let parameter_type = inspect.getattr("Parameter")?;
            let parameter_kwargs = PyDict::new(py);
            let parameters = PyList::empty(py);
            parameters.append(parameter_type.call(
                ("self", parameter_type.getattr("POSITIONAL_OR_KEYWORD")?),
                Some(&parameter_kwargs),
            )?)?;
            let signature_kwargs = PyDict::new(py);
            signature_kwargs.set_item("return_annotation", py.get_type::<PyString>())?;
            let signature = inspect
                .getattr("Signature")?
                .call((parameters,), Some(&signature_kwargs))?;
            let annotations = PyDict::new(py);
            annotations.set_item("return", py.get_type::<PyString>())?;
            (signature, annotations, PyTuple::empty(py), PyDict::new(py))
        }
    };
    let callable = Py::new(
        py,
        ParameterMethod {
            class,
            method,
            defaults: if defaults.is_empty() {
                None
            } else {
                Some(defaults.clone().unbind())
            },
            keyword_defaults: if keyword_defaults.is_empty() {
                None
            } else {
                Some(keyword_defaults.clone().unbind())
            },
        },
    )?;
    let callable = callable.bind(py);
    let method_name = match method {
        ParameterMethodKind::Init => "__init__",
        ParameterMethodKind::Repr => "__repr__",
    };
    callable.setattr("__name__", method_name)?;
    callable.setattr("__qualname__", format!("{}.{method_name}", class.name()))?;
    callable.setattr("__module__", "fastapi.params")?;
    callable.setattr("__doc__", py.None())?;
    callable.setattr("__annotations__", annotations)?;
    callable.setattr("__signature__", signature)?;
    Ok(callable.clone().into_any().unbind())
}

fn create_parameter_class(
    py: Python<'_>,
    module: &Bound<'_, PyModule>,
    param_types: &Bound<'_, PyType>,
    class: ParameterClassKind,
) -> PyResult<Py<PyType>> {
    let namespace = PyDict::new(py);
    namespace.set_item("__module__", "fastapi.params")?;
    namespace.set_item("__qualname__", class.name())?;
    namespace.set_item("__doc__", py.None())?;
    match class {
        ParameterClassKind::Param => {
            let annotations = PyDict::new(py);
            annotations.set_item("in_", param_types)?;
            namespace.set_item("__annotations__", annotations)?;
        }
        ParameterClassKind::Path => {
            namespace.set_item("in_", param_types.getattr("path")?)?;
        }
        ParameterClassKind::Query => {
            namespace.set_item("in_", param_types.getattr("query")?)?;
        }
        ParameterClassKind::Header => {
            namespace.set_item("in_", param_types.getattr("header")?)?;
        }
        ParameterClassKind::Cookie => {
            namespace.set_item("in_", param_types.getattr("cookie")?)?;
        }
        ParameterClassKind::Body | ParameterClassKind::Form | ParameterClassKind::File => {}
    }
    namespace.set_item(
        "__init__",
        make_method(py, module, class, ParameterMethodKind::Init)?,
    )?;
    if matches!(class, ParameterClassKind::Param | ParameterClassKind::Body) {
        namespace.set_item(
            "__repr__",
            make_method(py, module, class, ParameterMethodKind::Repr)?,
        )?;
    }
    let base = match class.parent() {
        Some(parent) => class_type(py, parent)?.as_any().clone(),
        None => py.import("pydantic.fields")?.getattr("FieldInfo")?,
    };
    let bases = PyTuple::new(py, [base])?;
    let class_type = py
        .import("builtins")?
        .getattr("type")?
        .call1((class.name(), bases, namespace))?
        .cast_into::<PyType>()?;
    let (signature, _, _, _) = build_signature(py, module, class, false)?;
    class_type.setattr("__signature__", signature)?;
    Ok(class_type.unbind())
}

/// Register public FastAPI parameter classes after the core exports their signature types.
pub(crate) fn register(
    module: &Bound<'_, PyModule>,
    default_placeholder: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let py = module.py();
    PARAMETER_UNSET.get_or_try_init(py, || {
        Ok::<Py<PyAny>, PyErr>(default_placeholder.clone().unbind())
    })?;
    module.add("_Unset", default_placeholder)?;
    let param_types = PARAM_TYPES.get_or_try_init(py, || create_param_types(py))?;
    for (class, export) in [
        (ParameterClassKind::Param, "ParamsParam"),
        (ParameterClassKind::Path, "ParamsPath"),
        (ParameterClassKind::Query, "ParamsQuery"),
        (ParameterClassKind::Header, "ParamsHeader"),
        (ParameterClassKind::Cookie, "ParamsCookie"),
        (ParameterClassKind::Body, "ParamsBody"),
        (ParameterClassKind::Form, "ParamsForm"),
        (ParameterClassKind::File, "ParamsFile"),
    ] {
        let class_value = class.class_cell().get_or_try_init(py, || {
            create_parameter_class(py, module, param_types.bind(py), class)
        })?;
        module.add(export, class_value.bind(py))?;
    }
    module.add("ParamsParamTypes", param_types.bind(py))?;
    Ok(())
}

/// Construct a class instance for a root factory while retaining its independent public name.
pub(crate) fn factory<'py>(
    py: Python<'py>,
    class: ParameterClassKind,
    args: &Bound<'py, PyTuple>,
    kwargs: Option<&Bound<'py, PyDict>>,
) -> PyResult<Py<PyAny>> {
    let previous = ROOT_FACTORY_ORIGIN.with(|origin| origin.replace(Some(class)));
    let _origin_guard = RootFactoryOriginGuard(previous);
    class_type(py, class)?.call(args, kwargs).map(Bound::unbind)
}

struct RootFactoryOriginGuard(Option<ParameterClassKind>);

impl Drop for RootFactoryOriginGuard {
    fn drop(&mut self) {
        ROOT_FACTORY_ORIGIN.with(|origin| origin.set(self.0));
    }
}

fn bind_method_arguments<'py>(
    py: Python<'py>,
    callable: &Bound<'py, PyAny>,
    class: ParameterClassKind,
    method: ParameterMethodKind,
    args: &Bound<'py, PyTuple>,
    kwargs: Option<&Bound<'py, PyDict>>,
) -> PyResult<Vec<Bound<'py, PyAny>>> {
    let names = match method {
        ParameterMethodKind::Init => {
            let mut names = vec!["self", "default"];
            names.extend(
                parameter_specs(class)
                    .into_iter()
                    .skip(1)
                    .filter_map(|spec| {
                        (spec.kind != ParameterKind::VariableKeyword).then_some(spec.name)
                    }),
            );
            names
        }
        ParameterMethodKind::Repr => vec!["self"],
    };
    let positional_count = match method {
        ParameterMethodKind::Init => 2,
        ParameterMethodKind::Repr => 1,
    };
    let defaults = callable.getattr("__defaults__")?;
    let keyword_defaults = callable.getattr("__kwdefaults__")?;
    let mut values = vec![None; names.len()];
    for (position, value) in args.iter().enumerate().take(positional_count) {
        values[position] = Some(value);
    }
    let extra = PyDict::new(py);
    if let Some(kwargs) = kwargs {
        let parameter_names = names
            .iter()
            .map(|name| PyString::intern(py, name))
            .collect::<Vec<_>>();
        let has_var_keyword = matches!(method, ParameterMethodKind::Init);
        for (keyword, value) in kwargs.iter() {
            if !keyword.is_instance_of::<PyString>() {
                return Err(PyTypeError::new_err("keywords must be strings"));
            }
            let mut position = parameter_names
                .iter()
                .position(|parameter| keyword.is(parameter));
            if position.is_none() {
                for (index, parameter) in parameter_names.iter().enumerate() {
                    if keyword.eq(parameter)? {
                        position = Some(index);
                        break;
                    }
                }
            }
            if let Some(position) = position {
                if values[position].is_some() {
                    return Err(keyword_error(py, class, method, &keyword, true)?);
                }
                values[position] = Some(value);
            } else if has_var_keyword {
                extra.set_item(keyword, value)?;
            } else {
                return Err(keyword_error(py, class, method, &keyword, false)?);
            }
        }
    }
    if args.len() > positional_count {
        let positional_defaults = if defaults.is_none() {
            Vec::new()
        } else {
            defaults.cast_into::<PyTuple>()?.iter().collect::<Vec<_>>()
        };
        let required_count = positional_count.saturating_sub(positional_defaults.len());
        let accepted = if required_count == positional_count {
            format!(
                "{positional_count} positional argument{}",
                if positional_count == 1 { "" } else { "s" }
            )
        } else {
            format!("from {required_count} to {positional_count} positional arguments")
        };
        let verb = if args.len() == 1 { "was" } else { "were" };
        return Err(PyTypeError::new_err(format!(
            "{}() takes {accepted} but {} {verb} given",
            callable_name(class, method),
            args.len()
        )));
    }
    let default_tuple = if defaults.is_none() {
        PyTuple::empty(py)
    } else {
        defaults.cast_into::<PyTuple>()?
    };
    let positional_specs = positional_count;
    let first_default = positional_specs.saturating_sub(default_tuple.len());
    for (offset, default) in default_tuple.iter().enumerate() {
        let index = first_default + offset;
        if index < values.len() && values[index].is_none() {
            values[index] = Some(default);
        }
    }
    if !keyword_defaults.is_none() {
        let keyword_defaults = keyword_defaults.cast_into::<PyDict>()?;
        for (index, name) in names.iter().enumerate().skip(positional_count) {
            if values[index].is_none() {
                if let Some(value) = keyword_defaults.get_item(*name)? {
                    values[index] = Some(value);
                }
            }
        }
    }
    if values.iter().any(Option::is_none) {
        // `self` and default have CPython's normal positional binding behavior;
        // all keyword-only constructor arguments have a source default.
        let missing = values
            .iter()
            .enumerate()
            .filter_map(|(index, value)| value.is_none().then_some(names[index]))
            .collect::<Vec<_>>();
        return Err(missing_arguments(callable_name(class, method), &missing));
    }
    if method == ParameterMethodKind::Init {
        let mut result = values.into_iter().flatten().collect::<Vec<_>>();
        result.push(extra.into_any());
        Ok(result)
    } else {
        Ok(values.into_iter().flatten().collect())
    }
}

fn callable_name(class: ParameterClassKind, method: ParameterMethodKind) -> String {
    let method = match method {
        ParameterMethodKind::Init => "__init__",
        ParameterMethodKind::Repr => "__repr__",
    };
    format!("{}.{method}", class.name())
}

fn keyword_error(
    py: Python<'_>,
    class: ParameterClassKind,
    method: ParameterMethodKind,
    keyword: &Bound<'_, PyAny>,
    duplicate: bool,
) -> PyResult<PyErr> {
    let reason = if duplicate {
        "got multiple values for argument"
    } else {
        "got an unexpected keyword argument"
    };
    let parts = PyTuple::new(
        py,
        [
            PyString::new(
                py,
                &format!("{}() {reason} '", callable_name(class, method)),
            ),
            keyword.str()?,
            PyString::new(py, "'"),
        ],
    )?;
    let message = PyString::new(py, "").call_method1("join", (parts,))?;
    let exception = py.get_type::<PyTypeError>().call1((message,))?;
    Ok(PyErr::from_value(exception))
}

fn missing_arguments(callable_name: String, names: &[&str]) -> PyErr {
    let quoted = names
        .iter()
        .map(|name| format!("'{name}'"))
        .collect::<Vec<_>>();
    let description = match quoted.as_slice() {
        [name] => name.clone(),
        [first, second] => format!("{first} and {second}"),
        _ => {
            let prefix = quoted[..quoted.len() - 1].join(", ");
            format!("{prefix}, and {}", quoted[quoted.len() - 1])
        }
    };
    PyTypeError::new_err(format!(
        "{callable_name}() missing {} required positional argument{}: {description}",
        names.len(),
        if names.len() == 1 { "" } else { "s" }
    ))
}

fn initialize_parameter(
    py: Python<'_>,
    class: ParameterClassKind,
    arguments: &[Bound<'_, PyAny>],
) -> PyResult<Py<PyAny>> {
    let instance = &arguments[0];
    let default = &arguments[1];
    let extras = arguments.last().ok_or_else(|| {
        PyRuntimeError::new_err("parameter constructor binding omitted extra keywords")
    })?;
    let extras = extras.cast::<PyDict>()?;
    let specs = parameter_specs(class);
    let value = |index: usize| -> PyResult<&Bound<'_, PyAny>> {
        arguments
            .get(index)
            .ok_or_else(|| PyRuntimeError::new_err("parameter constructor binding is incomplete"))
    };
    let mut named_values = std::collections::HashMap::new();
    for (argument_offset, spec) in specs
        .iter()
        .skip(1)
        .filter(|spec| spec.kind != ParameterKind::VariableKeyword)
        .enumerate()
    {
        named_values.insert(spec.name, value(argument_offset + 2)?);
    }
    let get = |name: &'static str| -> PyResult<&Bound<'_, PyAny>> {
        named_values.get(name).copied().ok_or_else(|| {
            PyRuntimeError::new_err(format!("parameter constructor has no {name} value"))
        })
    };
    if class == ParameterClassKind::Path {
        if !default.is(py.Ellipsis()) {
            return Err(PyAssertionError::new_err(
                "Path parameters cannot have a default value",
            ));
        }
        instance.setattr("in_", instance.getattr("in_")?)?;
    }
    if class == ParameterClassKind::Header {
        instance.setattr("convert_underscores", get("convert_underscores")?)?;
    }
    if class == ParameterClassKind::Body {
        instance.setattr("embed", get("embed")?)?;
        instance.setattr("media_type", get("media_type")?)?;
    } else if matches!(class, ParameterClassKind::Form | ParameterClassKind::File) {
        instance.setattr("media_type", get("media_type")?)?;
    }
    if matches!(class, ParameterClassKind::Param | ParameterClassKind::Body) {
        if !get("example")?.is(&unset(py)?) {
            warn_deprecation(
                py,
                EXAMPLE_WARNING,
                parameter_class_from_instance(instance, class)?,
            )?;
        }
        instance.setattr("example", get("example")?)?;
        instance.setattr("include_in_schema", get("include_in_schema")?)?;
        instance.setattr("openapi_examples", get("openapi_examples")?)?;
    }
    let forwarded = match class {
        ParameterClassKind::Param | ParameterClassKind::Body => field_info_arguments(
            py,
            default,
            &named_values,
            extras,
            parameter_class_from_instance(instance, class)?,
        )?,
        ParameterClassKind::Path
        | ParameterClassKind::Query
        | ParameterClassKind::Header
        | ParameterClassKind::Cookie
        | ParameterClassKind::Form
        | ParameterClassKind::File => {
            constructor_forwarding_arguments(py, class, default, &named_values, extras)?
        }
    };
    let base = py
        .import("builtins")?
        .getattr("super")?
        .call1((class_type(py, class)?, instance))?;
    base.getattr("__init__")?.call((), Some(&forwarded))?;
    Ok(py.None())
}

fn constructor_forwarding_arguments<'py>(
    py: Python<'py>,
    class: ParameterClassKind,
    default: &Bound<'py, PyAny>,
    values: &std::collections::HashMap<&'static str, &Bound<'py, PyAny>>,
    extras: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    let forwarded = PyDict::new(py);
    forwarded.set_item("default", default)?;
    for spec in parameter_specs(class).iter().skip(1) {
        if spec.kind != ParameterKind::VariableKeyword {
            if spec.name == "convert_underscores" {
                continue;
            }
            if let Some(value) = values.get(spec.name) {
                forwarded.set_item(spec.name, *value)?;
            }
        }
    }
    for (key, value) in extras.iter() {
        forwarded.set_item(key, value)?;
    }
    Ok(forwarded)
}

fn field_info_arguments<'py>(
    py: Python<'py>,
    default: &Bound<'py, PyAny>,
    values: &std::collections::HashMap<&'static str, &Bound<'py, PyAny>>,
    extras: &Bound<'py, PyDict>,
    warning_class: ParameterClassKind,
) -> PyResult<Bound<'py, PyDict>> {
    let kwargs = PyDict::new(py);
    for key in [
        "default",
        "default_factory",
        "alias",
        "title",
        "description",
        "gt",
        "ge",
        "lt",
        "le",
        "min_length",
        "max_length",
        "discriminator",
        "multiple_of",
        "allow_inf_nan",
        "max_digits",
        "decimal_places",
    ] {
        let value = if key == "default" {
            default
        } else {
            values.get(key).copied().ok_or_else(|| {
                PyRuntimeError::new_err(format!("parameter constructor has no {key} value"))
            })?
        };
        kwargs.set_item(key, value)?;
    }
    for (key, value) in extras.iter() {
        kwargs.set_item(key, value)?;
    }
    if let Some(examples) = values.get("examples") {
        if !examples.is_none() {
            kwargs.set_item("examples", *examples)?;
        }
    }
    let deprecated = values
        .get("deprecated")
        .ok_or_else(|| PyRuntimeError::new_err("parameter constructor has no deprecated value"))?;
    kwargs.set_item("deprecated", *deprecated)?;
    let annotation = values
        .get("annotation")
        .copied()
        .ok_or_else(|| PyRuntimeError::new_err("parameter constructor has no annotation value"))?;
    let alias_priority = values.get("alias_priority").copied().ok_or_else(|| {
        PyRuntimeError::new_err("parameter constructor has no alias_priority value")
    })?;
    let validation_alias = values.get("validation_alias").copied().ok_or_else(|| {
        PyRuntimeError::new_err("parameter constructor has no validation_alias value")
    })?;
    let serialization_alias = values.get("serialization_alias").copied().ok_or_else(|| {
        PyRuntimeError::new_err("parameter constructor has no serialization_alias value")
    })?;
    let strict = values
        .get("strict")
        .copied()
        .ok_or_else(|| PyRuntimeError::new_err("parameter constructor has no strict value"))?;
    let json_schema_extra = values.get("json_schema_extra").copied().ok_or_else(|| {
        PyRuntimeError::new_err("parameter constructor has no json_schema_extra value")
    })?;

    let unset = unset(py)?;
    let alias = values
        .get("alias")
        .copied()
        .ok_or_else(|| PyRuntimeError::new_err("parameter constructor has no alias value"))?;
    let in_unset_or_none = PyTuple::new(py, [unset.clone(), py.None().into_bound(py)])?;
    let alias_was_unset = in_unset_or_none.contains(serialization_alias.clone())?;
    let alias_is_string = alias.is_instance_of::<PyString>();
    let effective_serialization_alias = if alias_was_unset && alias_is_string {
        alias
    } else {
        serialization_alias
    };
    let validation_was_unset = in_unset_or_none.contains(validation_alias.clone())?;
    let effective_validation_alias = if validation_was_unset {
        alias
    } else {
        validation_alias
    };

    let json_schema_extra_selected = if json_schema_extra.is_truthy()? {
        json_schema_extra
    } else {
        extras.as_any()
    };
    let pattern = values
        .get("pattern")
        .copied()
        .ok_or_else(|| PyRuntimeError::new_err("parameter constructor has no pattern value"))?;
    let regex = values
        .get("regex")
        .copied()
        .ok_or_else(|| PyRuntimeError::new_err("parameter constructor has no regex value"))?;
    if !regex.is_none() {
        warn_deprecation(py, REGEX_WARNING, warning_class)?;
    }
    let selected_pattern = if pattern.is_truthy()? { pattern } else { regex };

    for (name, value) in [
        ("annotation", annotation),
        ("alias_priority", alias_priority),
        ("validation_alias", effective_validation_alias),
        ("serialization_alias", effective_serialization_alias),
        ("strict", strict),
        ("json_schema_extra", json_schema_extra_selected),
        ("pattern", selected_pattern),
    ] {
        kwargs.set_item(name, value)?;
    }
    let use_kwargs = PyDict::new(py);
    for (key, value) in kwargs.iter() {
        if !value.is(&unset) {
            use_kwargs.set_item(key, value)?;
        }
    }
    Ok(use_kwargs)
}

fn parameter_class_from_instance(
    instance: &Bound<'_, PyAny>,
    fallback: ParameterClassKind,
) -> PyResult<ParameterClassKind> {
    let name = instance
        .getattr("__class__")?
        .getattr("__name__")?
        .extract::<String>()?;
    Ok(match name.as_str() {
        "Param" => ParameterClassKind::Param,
        "Path" => ParameterClassKind::Path,
        "Query" => ParameterClassKind::Query,
        "Header" => ParameterClassKind::Header,
        "Cookie" => ParameterClassKind::Cookie,
        "Body" => ParameterClassKind::Body,
        "Form" => ParameterClassKind::Form,
        "File" => ParameterClassKind::File,
        _ => fallback,
    })
}

fn warn_deprecation(
    py: Python<'_>,
    message: &str,
    warning_class: ParameterClassKind,
) -> PyResult<()> {
    let warning = crate::errors::fastapi_deprecation_warning_type(py);
    let warnings = py.import("warnings")?;
    let root_origin = ROOT_FACTORY_ORIGIN.with(Cell::get);
    if root_origin == Some(ParameterClassKind::File) {
        warnings.getattr("warn_explicit")?.call1((
            message,
            warning,
            "fastapi/param_functions.py",
            2355,
        ))?;
    } else {
        let stacklevel = match (warning_class, root_origin) {
            (
                ParameterClassKind::Path
                | ParameterClassKind::Query
                | ParameterClassKind::Header
                | ParameterClassKind::Cookie
                | ParameterClassKind::Form
                | ParameterClassKind::File,
                Some(_),
            ) => 1,
            (ParameterClassKind::Body, Some(_)) => 2,
            (ParameterClassKind::Param | ParameterClassKind::Body, None) => 3,
            (ParameterClassKind::File, None) => 1,
            _ => 2,
        };
        let kwargs = PyDict::new(py);
        kwargs.set_item("stacklevel", stacklevel)?;
        warnings
            .getattr("warn")?
            .call((message, warning), Some(&kwargs))?;
    }
    Ok(())
}

fn parameter_repr(py: Python<'_>, instance: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    let class_name = instance.getattr("__class__")?.getattr("__name__")?;
    let default = instance.getattr("default")?;
    let formatted = py
        .import("builtins")?
        .getattr("format")?
        .call1((default, ""))?;
    let result = PyString::new(
        py,
        &format!(
            "{}({})",
            class_name.str()?.to_str()?,
            formatted.str()?.to_str()?
        ),
    );
    Ok(result.into_any().unbind())
}
