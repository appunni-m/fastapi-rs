//! Native methods for FastAPI's frozen dependency dataclasses.
//!
//! The records are ordinary heap types with instance dictionaries. Their
//! methods execute in Rust, while stdlib Field and signature values expose the
//! dataclass protocol without asking dataclasses to generate Python methods.

use std::collections::HashSet;
use std::sync::Mutex;
use std::thread::{self, ThreadId};

use pyo3::basic::CompareOp;
use pyo3::exceptions::{PyRuntimeError, PyTypeError};
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyBool, PyDict, PyList, PyModule, PySet, PyString, PyTuple, PyType};

static DEPENDS_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();
static SECURITY_CLASS: PyOnceLock<Py<PyType>> = PyOnceLock::new();

#[derive(Clone, Copy)]
enum RecordKind {
    Depends,
    Security,
}

impl RecordKind {
    fn name(self) -> &'static str {
        match self {
            Self::Depends => "Depends",
            Self::Security => "Security",
        }
    }

    fn fields(self) -> &'static [&'static str] {
        match self {
            Self::Depends => &["dependency", "use_cache", "scope"],
            Self::Security => &["dependency", "use_cache", "scope", "scopes"],
        }
    }
}

#[derive(Clone, Copy)]
enum MethodKind {
    Init,
    Repr,
    Equal,
    Hash,
    SetAttribute,
    DeleteAttribute,
}

impl MethodKind {
    fn name(self) -> &'static str {
        match self {
            Self::Init => "__init__",
            Self::Repr => "__repr__",
            Self::Equal => "__eq__",
            Self::Hash => "__hash__",
            Self::SetAttribute => "__setattr__",
            Self::DeleteAttribute => "__delattr__",
        }
    }

    fn parameters(self, record: RecordKind) -> &'static [ParameterBinding] {
        match self {
            Self::Init => match record {
                RecordKind::Depends => DEPENDS_INIT_PARAMETERS,
                RecordKind::Security => SECURITY_INIT_PARAMETERS,
            },
            Self::Repr | Self::Hash => SELF_PARAMETER,
            Self::Equal => EQUALITY_PARAMETERS,
            Self::SetAttribute => SET_ATTRIBUTE_PARAMETERS,
            Self::DeleteAttribute => DELETE_ATTRIBUTE_PARAMETERS,
        }
    }
}

#[derive(Clone, Copy)]
enum ParameterDefault {
    None,
    True,
}

impl ParameterDefault {
    fn value(self, py: Python<'_>) -> Bound<'_, PyAny> {
        match self {
            Self::None => py.None().into_bound(py),
            Self::True => PyBool::new(py, true).to_owned().into_any(),
        }
    }
}

#[derive(Clone, Copy)]
struct ParameterBinding {
    name: &'static str,
    default: Option<ParameterDefault>,
    keyword_only: bool,
}

impl ParameterBinding {
    const fn required(name: &'static str) -> Self {
        Self {
            name,
            default: None,
            keyword_only: false,
        }
    }

    const fn optional(name: &'static str, default: ParameterDefault) -> Self {
        Self {
            name,
            default: Some(default),
            keyword_only: false,
        }
    }

    const fn keyword(name: &'static str, default: ParameterDefault) -> Self {
        Self {
            name,
            default: Some(default),
            keyword_only: true,
        }
    }
}

const SELF_PARAMETER: &[ParameterBinding] = &[ParameterBinding::required("self")];
const EQUALITY_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::required("self"),
    ParameterBinding::required("other"),
];
const SET_ATTRIBUTE_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::required("self"),
    ParameterBinding::required("name"),
    ParameterBinding::required("value"),
];
const DELETE_ATTRIBUTE_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::required("self"),
    ParameterBinding::required("name"),
];
const DEPENDS_INIT_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::required("self"),
    ParameterBinding::optional("dependency", ParameterDefault::None),
    ParameterBinding::optional("use_cache", ParameterDefault::True),
    ParameterBinding::optional("scope", ParameterDefault::None),
];
const SECURITY_INIT_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::required("self"),
    ParameterBinding::optional("dependency", ParameterDefault::None),
    ParameterBinding::optional("use_cache", ParameterDefault::True),
    ParameterBinding::optional("scope", ParameterDefault::None),
    ParameterBinding::optional("scopes", ParameterDefault::None),
];
const DEPENDS_FACTORY_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::optional("dependency", ParameterDefault::None),
    ParameterBinding::keyword("use_cache", ParameterDefault::True),
    ParameterBinding::keyword("scope", ParameterDefault::None),
];
const SECURITY_FACTORY_PARAMETERS: &[ParameterBinding] = &[
    ParameterBinding::optional("dependency", ParameterDefault::None),
    ParameterBinding::keyword("scopes", ParameterDefault::None),
    ParameterBinding::keyword("use_cache", ParameterDefault::True),
];

#[pyclass(name = "_DependencyRecordMethod", module = "fastapi_rs._core", dict)]
struct RecordMethod {
    record: RecordKind,
    method: MethodKind,
    repr_running: Mutex<HashSet<(usize, ThreadId)>>,
}

#[pymethods]
impl RecordMethod {
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

    #[pyo3(signature = (*args, **kwargs))]
    fn __call__(
        &self,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let name = format!("{}.{}", self.record.name(), self.method.name());
        let arguments =
            bind_arguments(py, &name, self.method.parameters(self.record), args, kwargs)?;
        let instance = &arguments[0];
        match self.method {
            MethodKind::Init => {
                let object_setattr = py
                    .import("builtins")?
                    .getattr("object")?
                    .getattr("__setattr__")?;
                for (field, value) in self.record.fields().iter().zip(&arguments[1..]) {
                    object_setattr.call1((instance, *field, value))?;
                }
                Ok(py.None())
            }
            MethodKind::Repr => self.record_repr(py, instance),
            MethodKind::Equal => {
                let other_class = arguments[1].getattr("__class__")?;
                let instance_class = instance.getattr("__class__")?;
                if !other_class.is(&instance_class) {
                    return Ok(py.NotImplemented());
                }
                let left = record_tuple(py, self.record, instance)?;
                let right = record_tuple(py, self.record, &arguments[1])?;
                left.rich_compare(&right, CompareOp::Eq).map(Bound::unbind)
            }
            MethodKind::Hash => {
                let hash = record_tuple(py, self.record, instance)?.hash()?;
                Ok(hash.into_pyobject(py)?.into_any().unbind())
            }
            MethodKind::SetAttribute => {
                frozen_attribute(
                    py,
                    self.record,
                    instance,
                    &arguments[1],
                    Some(&arguments[2]),
                )?;
                Ok(py.None())
            }
            MethodKind::DeleteAttribute => {
                frozen_attribute(py, self.record, instance, &arguments[1], None)?;
                Ok(py.None())
            }
        }
    }
}

impl RecordMethod {
    fn record_repr(&self, py: Python<'_>, instance: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        let key = (instance.as_ptr() as usize, thread::current().id());
        let inserted = self
            .repr_running
            .lock()
            .map_err(|_| PyRuntimeError::new_err("dependency repr recursion guard is unavailable"))?
            .insert(key);
        if !inserted {
            return Ok(PyString::new(py, "...").into_any().unbind());
        }
        let result = render_record_repr(py, self.record, instance);
        self.repr_running
            .lock()
            .map_err(|_| PyRuntimeError::new_err("dependency repr recursion guard is unavailable"))?
            .remove(&key);
        result
    }
}

fn record_tuple<'py>(
    py: Python<'py>,
    record: RecordKind,
    instance: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let values = record
        .fields()
        .iter()
        .map(|field| instance.getattr(*field))
        .collect::<PyResult<Vec<_>>>()?;
    PyTuple::new(py, values)
}

fn render_record_repr(
    py: Python<'_>,
    record: RecordKind,
    instance: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let qualname = instance.getattr("__class__")?.getattr("__qualname__")?;
    let mut fields = Vec::with_capacity(record.fields().len());
    for field in record.fields() {
        let value = instance.getattr(*field)?.repr()?;
        fields.push(format!("{field}={}", value.to_str()?));
    }
    let suffix = PyString::new(py, &format!("({})", fields.join(", ")));
    // Python string addition retains the generated dataclass method's behavior
    // if a subclass supplies a custom __class__ attribute.
    py.import("operator")?
        .getattr("add")?
        .call1((qualname, suffix))
        .map(Bound::unbind)
}

fn frozen_attribute(
    py: Python<'_>,
    record: RecordKind,
    instance: &Bound<'_, PyAny>,
    name: &Bound<'_, PyAny>,
    value: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    let class = record_class(py, record)?;
    let exact_class = instance.get_type().is(class);
    let frozen_field = if exact_class {
        true
    } else {
        PySet::new(py, record.fields().iter().copied())?
            .as_any()
            .contains(name)?
    };
    if frozen_field {
        let operation = if value.is_some() {
            "assign to"
        } else {
            "delete"
        };
        let message = format!("cannot {operation} field {}", name.repr()?.to_str()?);
        let exception = py
            .import("dataclasses")?
            .getattr("FrozenInstanceError")?
            .call1((message,))?;
        return Err(PyErr::from_value(exception));
    }
    let base = py
        .import("builtins")?
        .getattr("super")?
        .call1((class, instance))?;
    if let Some(value) = value {
        base.call_method1("__setattr__", (name, value))?;
    } else {
        base.call_method1("__delattr__", (name,))?;
    }
    Ok(())
}

fn bind_arguments<'py>(
    py: Python<'py>,
    callable_name: &str,
    parameters: &[ParameterBinding],
    args: &Bound<'py, PyTuple>,
    kwargs: Option<&Bound<'py, PyDict>>,
) -> PyResult<Vec<Bound<'py, PyAny>>> {
    let positional_count = parameters
        .iter()
        .take_while(|parameter| !parameter.keyword_only)
        .count();
    let mut values = vec![None; parameters.len()];
    for (position, value) in args.iter().take(positional_count).enumerate() {
        values[position] = Some(value);
    }
    if let Some(kwargs) = kwargs {
        let parameter_names = parameters
            .iter()
            .map(|parameter| PyString::intern(py, parameter.name))
            .collect::<Vec<_>>();
        for (keyword, value) in kwargs.iter() {
            if !keyword.is_instance_of::<PyString>() {
                return Err(PyTypeError::new_err("keywords must be strings"));
            }
            // CPython searches every parameter by identity before invoking
            // keyword equality in parameter order. Keep the keyword object so
            // str subclasses can participate in that second search.
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
            let Some(position) = position else {
                return Err(keyword_binding_error(py, callable_name, &keyword, false)?);
            };
            if values[position].is_some() {
                return Err(keyword_binding_error(py, callable_name, &keyword, true)?);
            }
            values[position] = Some(value);
        }
    }
    if args.len() > positional_count {
        let required_count = parameters[..positional_count]
            .iter()
            .filter(|parameter| parameter.default.is_none())
            .count();
        let accepted = if required_count == positional_count {
            format!(
                "{positional_count} positional argument{}",
                if positional_count == 1 { "" } else { "s" }
            )
        } else {
            format!("from {required_count} to {positional_count} positional arguments")
        };
        let supplied_keyword_only = values[positional_count..]
            .iter()
            .filter(|value| value.is_some())
            .count();
        let supplied = if supplied_keyword_only == 0 {
            args.len().to_string()
        } else {
            format!(
                "{} positional argument{} (and {supplied_keyword_only} keyword-only argument{})",
                args.len(),
                if args.len() == 1 { "" } else { "s" },
                if supplied_keyword_only == 1 { "" } else { "s" }
            )
        };
        let verb = if args.len() == 1 && supplied_keyword_only == 0 {
            "was"
        } else {
            "were"
        };
        return Err(PyTypeError::new_err(format!(
            "{callable_name}() takes {accepted} but {supplied} {verb} given"
        )));
    }
    let missing = parameters
        .iter()
        .zip(&values)
        .filter_map(|(parameter, value)| {
            (parameter.default.is_none() && value.is_none()).then_some(parameter.name)
        })
        .collect::<Vec<_>>();
    if !missing.is_empty() {
        return Err(missing_arguments(callable_name, &missing));
    }
    values
        .into_iter()
        .zip(parameters)
        .map(|(value, parameter)| {
            value.map_or_else(
                || {
                    parameter
                        .default
                        .map(|default| default.value(py))
                        .ok_or_else(|| {
                            PyRuntimeError::new_err("dependency argument binding is incomplete")
                        })
                },
                Ok,
            )
        })
        .collect()
}

fn keyword_binding_error(
    py: Python<'_>,
    callable_name: &str,
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
            PyString::new(py, &format!("{callable_name}() {reason} '")),
            keyword.str()?,
            PyString::new(py, "'"),
        ],
    )?;
    // PyErr_Format's %S conversion calls str(keyword), then copies Unicode
    // contents. Join preserves that conversion, including lone surrogates,
    // without running subclass formatting or addition hooks.
    let message = PyString::new(py, "").call_method1("join", (parts,))?;
    let exception = py.get_type::<PyTypeError>().call1((message,))?;
    Ok(PyErr::from_value(exception))
}

fn missing_arguments(callable_name: &str, names: &[&str]) -> PyErr {
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

fn record_class<'py>(py: Python<'py>, record: RecordKind) -> PyResult<&'py Bound<'py, PyType>> {
    let class = match record {
        RecordKind::Depends => DEPENDS_CLASS.get(py),
        RecordKind::Security => SECURITY_CLASS.get(py),
    };
    class
        .map(|class| class.bind(py))
        .ok_or_else(|| PyRuntimeError::new_err("dependency record classes are not registered"))
}

/// Recognize the actual dependency class hierarchy without synthetic markers.
pub(crate) fn is_dependency_record(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    value.is_instance(record_class(py, RecordKind::Depends)?.as_any())
}

/// Only Security records carry the source's scopes field.
pub(crate) fn is_security_record(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    value.is_instance(record_class(py, RecordKind::Security)?.as_any())
}

/// Apply the public Depends factory binding and preserve every supplied value.
pub(crate) fn depends_factory(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    dependency_factory(
        py,
        RecordKind::Depends,
        DEPENDS_FACTORY_PARAMETERS,
        args,
        kwargs,
    )
}

/// Apply the public Security factory binding and preserve every supplied value.
pub(crate) fn security_factory(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    dependency_factory(
        py,
        RecordKind::Security,
        SECURITY_FACTORY_PARAMETERS,
        args,
        kwargs,
    )
}

fn dependency_factory(
    py: Python<'_>,
    record: RecordKind,
    parameters: &[ParameterBinding],
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    let arguments = bind_arguments(py, record.name(), parameters, args, kwargs)?;
    let record_kwargs = PyDict::new(py);
    for (parameter, value) in parameters.iter().zip(arguments) {
        record_kwargs.set_item(parameter.name, value)?;
    }
    record_class(py, record)?
        .call((), Some(&record_kwargs))
        .map(Bound::unbind)
}

fn record_annotations(py: Python<'_>) -> PyResult<Bound<'_, PyDict>> {
    let typing = py.import("typing")?;
    let abc = py.import("collections.abc")?;
    let operator = py.import("operator")?;
    let none_type = py.None().bind(py).get_type();
    let callable_arguments =
        PyTuple::new(py, [py.Ellipsis().into_bound(py), typing.getattr("Any")?])?;
    let callable = abc.getattr("Callable")?.get_item(callable_arguments)?;
    let literal = typing
        .getattr("Literal")?
        .get_item(PyTuple::new(py, ["function", "request"])?)?;
    let sequence = abc
        .getattr("Sequence")?
        .get_item(py.get_type::<PyString>())?;
    let annotations = PyDict::new(py);
    annotations.set_item(
        "dependency",
        operator.getattr("or_")?.call1((callable, &none_type))?,
    )?;
    annotations.set_item("use_cache", py.get_type::<PyBool>())?;
    annotations.set_item(
        "scope",
        operator.getattr("or_")?.call1((literal, &none_type))?,
    )?;
    annotations.set_item(
        "scopes",
        operator.getattr("or_")?.call1((sequence, none_type))?,
    )?;
    Ok(annotations)
}

fn method_signature<'py>(
    py: Python<'py>,
    record: RecordKind,
    method: MethodKind,
    annotations: &Bound<'py, PyDict>,
    include_self: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let positional_kind = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let parameters = PyList::empty(py);
    for parameter in method.parameters(record) {
        if parameter.name == "self" && !include_self {
            continue;
        }
        let arguments = PyDict::new(py);
        if let Some(annotation) = annotations.get_item(parameter.name)? {
            arguments.set_item("annotation", annotation)?;
        }
        if let Some(default) = parameter.default {
            arguments.set_item("default", default.value(py))?;
        }
        parameters
            .append(parameter_type.call((parameter.name, &positional_kind), Some(&arguments))?)?;
    }
    let arguments = PyDict::new(py);
    if matches!(method, MethodKind::Init) {
        arguments.set_item("return_annotation", py.None())?;
    }
    inspect
        .getattr("Signature")?
        .call((parameters,), Some(&arguments))
}

fn install_record_methods(
    py: Python<'_>,
    class: &Bound<'_, PyType>,
    record: RecordKind,
    field_annotations: &Bound<'_, PyDict>,
) -> PyResult<()> {
    for method in [
        MethodKind::Init,
        MethodKind::Repr,
        MethodKind::Equal,
        MethodKind::SetAttribute,
        MethodKind::DeleteAttribute,
        MethodKind::Hash,
    ] {
        let annotations = PyDict::new(py);
        if matches!(method, MethodKind::Init) {
            for field in record.fields() {
                if let Some(annotation) = field_annotations.get_item(*field)? {
                    annotations.set_item(*field, annotation)?;
                }
            }
            annotations.set_item("return", py.None())?;
        }
        let signature = method_signature(py, record, method, &annotations, true)?;
        let callable = Py::new(
            py,
            RecordMethod {
                record,
                method,
                repr_running: Mutex::new(HashSet::new()),
            },
        )?;
        let callable = callable.bind(py);
        callable.setattr("__name__", method.name())?;
        callable.setattr(
            "__qualname__",
            format!("{}.{}", record.name(), method.name()),
        )?;
        callable.setattr("__module__", "fastapi.params")?;
        callable.setattr("__doc__", py.None())?;
        callable.setattr("__annotations__", annotations)?;
        callable.setattr("__signature__", signature)?;
        let defaults = method
            .parameters(record)
            .iter()
            .filter_map(|parameter| parameter.default)
            .map(|default| default.value(py))
            .collect::<Vec<_>>();
        if defaults.is_empty() {
            callable.setattr("__defaults__", py.None())?;
        } else {
            callable.setattr("__defaults__", PyTuple::new(py, defaults)?)?;
        }
        callable.setattr("__kwdefaults__", py.None())?;
        class.setattr(method.name(), callable)?;
    }
    Ok(())
}

fn record_dataclass_fields<'py>(
    py: Python<'py>,
    record: RecordKind,
    annotations: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyDict>> {
    let dataclasses = py.import("dataclasses")?;
    let fields = PyDict::new(py);
    if matches!(record, RecordKind::Security) {
        let inherited = record_class(py, RecordKind::Depends)?
            .getattr("__dataclass_fields__")?
            .cast_into::<PyDict>()?;
        fields.update(inherited.as_mapping())?;
    }
    let own_fields = match record {
        RecordKind::Depends => RecordKind::Depends.fields(),
        RecordKind::Security => &["scopes"],
    };
    for name in own_fields {
        let field_arguments = PyDict::new(py);
        let default = if *name == "use_cache" {
            ParameterDefault::True
        } else {
            ParameterDefault::None
        };
        field_arguments.set_item("default", default.value(py))?;
        field_arguments.set_item("kw_only", false)?;
        let field = dataclasses
            .getattr("field")?
            .call((), Some(&field_arguments))?;
        field.setattr("name", *name)?;
        if let Some(annotation) = annotations.get_item(*name)? {
            field.setattr("type", annotation)?;
        }
        field.setattr("_field_type", dataclasses.getattr("_FIELD")?)?;
        fields.set_item(*name, field)?;
    }
    Ok(fields)
}

fn create_record_class(py: Python<'_>, record: RecordKind) -> PyResult<Py<PyType>> {
    let annotations = record_annotations(py)?;
    if matches!(record, RecordKind::Security) {
        let inherited_fields =
            record_class(py, RecordKind::Depends)?.getattr("__dataclass_fields__")?;
        for name in RecordKind::Depends.fields() {
            annotations.set_item(*name, inherited_fields.get_item(*name)?.getattr("type")?)?;
        }
    }
    let own_annotations = PyDict::new(py);
    let own_fields = match record {
        RecordKind::Depends => RecordKind::Depends.fields(),
        RecordKind::Security => &["scopes"],
    };
    let namespace = PyDict::new(py);
    namespace.set_item("__module__", "fastapi.params")?;
    namespace.set_item("__qualname__", record.name())?;
    namespace.set_item("__annotations__", &own_annotations)?;
    for name in own_fields {
        if let Some(annotation) = annotations.get_item(*name)? {
            own_annotations.set_item(*name, annotation)?;
        }
        let default = if *name == "use_cache" {
            ParameterDefault::True
        } else {
            ParameterDefault::None
        };
        namespace.set_item(*name, default.value(py))?;
    }
    let base = match record {
        RecordKind::Depends => py.import("builtins")?.getattr("object")?,
        RecordKind::Security => record_class(py, RecordKind::Depends)?.as_any().clone(),
    };
    let class = py
        .import("builtins")?
        .getattr("type")?
        .call1((record.name(), PyTuple::new(py, [base])?, namespace))?
        .cast_into::<PyType>()?;
    let dataclass_parameters = PyTuple::new(
        py,
        [
            true, true, true, false, false, true, true, false, false, false,
        ],
    )?;
    class.setattr(
        "__dataclass_params__",
        py.import("dataclasses")?
            .getattr("_DataclassParams")?
            .call1(dataclass_parameters)?,
    )?;
    class.setattr(
        "__dataclass_fields__",
        record_dataclass_fields(py, record, &annotations)?,
    )?;
    install_record_methods(py, &class, record, &annotations)?;
    let class_signature = method_signature(py, record, MethodKind::Init, &annotations, false)?;
    let signature_text = class_signature.str()?.to_str()?.replace(" -> None", "");
    class.setattr("__doc__", format!("{}{signature_text}", record.name()))?;
    class.setattr(
        "__match_args__",
        PyTuple::new(py, record.fields().iter().copied())?,
    )?;
    Ok(class.unbind())
}

/// Register the class exports independently of the root dependency factories.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let depends =
        DEPENDS_CLASS.get_or_try_init(py, || create_record_class(py, RecordKind::Depends))?;
    let security =
        SECURITY_CLASS.get_or_try_init(py, || create_record_class(py, RecordKind::Security))?;
    module.add("ParamsDepends", depends.bind(py))?;
    module.add("ParamsSecurity", security.bind(py))?;
    Ok(())
}
