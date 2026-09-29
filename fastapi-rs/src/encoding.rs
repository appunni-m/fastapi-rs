//! Rust-owned JSON-compatible conversion for FastAPI values.

use pyo3::PyTypeInfo;
use pyo3::exceptions::{PyAssertionError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PySet, PyType};

/// Runtime options for FastAPI's JSON-compatible value encoder.
pub struct JsonableEncoderOptions {
    include: Option<Py<PyAny>>,
    exclude: Option<Py<PyAny>>,
    by_alias: bool,
    exclude_unset: bool,
    exclude_defaults: bool,
    exclude_none: bool,
    custom_encoder: Option<Py<PyAny>>,
    sqlalchemy_safe: bool,
}

/// Python arguments converted by the PyO3 boundary for one encoder invocation.
pub struct JsonableEncoderInput<'py> {
    /// Keys or fields to include.
    pub include: Option<Bound<'py, PyAny>>,
    /// Keys or fields to exclude.
    pub exclude: Option<Bound<'py, PyAny>>,
    /// Whether Pydantic model aliases should be used.
    pub by_alias: bool,
    /// Whether Pydantic unset fields should be excluded.
    pub exclude_unset: bool,
    /// Whether Pydantic default-valued fields should be excluded.
    pub exclude_defaults: bool,
    /// Whether `None` values should be excluded.
    pub exclude_none: bool,
    /// User-supplied exact-type or class-based encoders.
    pub custom_encoder: Option<Bound<'py, PyAny>>,
    /// Whether `_sa`-prefixed mapping keys should be excluded.
    pub sqlalchemy_safe: bool,
}

impl JsonableEncoderOptions {
    /// Normalize direct-call options once before recursive conversion.
    pub fn new<'py>(input: JsonableEncoderInput<'py>) -> Self {
        Self {
            include: input.include.map(Bound::unbind),
            exclude: input.exclude.map(Bound::unbind),
            by_alias: input.by_alias,
            exclude_unset: input.exclude_unset,
            exclude_defaults: input.exclude_defaults,
            exclude_none: input.exclude_none,
            custom_encoder: input.custom_encoder.map(Bound::unbind),
            sqlalchemy_safe: input.sqlalchemy_safe,
        }
    }

    fn without_filters(&self, py: Python<'_>, keep_custom_encoder: bool) -> Self {
        Self {
            include: None,
            exclude: None,
            by_alias: self.by_alias,
            exclude_unset: self.exclude_unset,
            exclude_defaults: self.exclude_defaults,
            exclude_none: self.exclude_none,
            custom_encoder: if keep_custom_encoder {
                self.custom_encoder
                    .as_ref()
                    .map(|value| value.clone_ref(py))
            } else {
                None
            },
            sqlalchemy_safe: self.sqlalchemy_safe,
        }
    }
}

/// Convert one value according to the selected FastAPI 0.141.1 encoder rules.
pub(crate) fn jsonable_encoder<'py>(
    py: Python<'py>,
    obj: &Bound<'py, PyAny>,
    options: &JsonableEncoderOptions,
) -> PyResult<Bound<'py, PyAny>> {
    encode_value(py, obj, options)
}

fn normalize_filter<'py>(
    py: Python<'py>,
    filter: Option<&Bound<'py, PyAny>>,
) -> PyResult<Option<Bound<'py, PyAny>>> {
    let Some(filter) = filter.filter(|value| !value.is_none()) else {
        return Ok(None);
    };
    let set_type = py.import("builtins")?.getattr("set")?;
    if filter.cast::<PySet>().is_ok() || filter.cast::<PyDict>().is_ok() {
        return Ok(Some(filter.clone()));
    }
    Ok(Some(set_type.call1((filter,))?))
}

fn encode_value<'py>(
    py: Python<'py>,
    obj: &Bound<'py, PyAny>,
    options: &JsonableEncoderOptions,
) -> PyResult<Bound<'py, PyAny>> {
    let custom_encoder = options.custom_encoder.as_ref().map(|value| value.bind(py));
    if let Some(custom_encoder) = custom_encoder {
        if custom_encoder.is_truthy()? {
            let object_type = obj.get_type();
            if custom_encoder.contains(&object_type)? {
                let encoder = custom_encoder.get_item(object_type)?;
                return encoder.call1((obj,));
            }
            for item in custom_encoder.call_method0("items")?.try_iter()? {
                let item = item?;
                let encoder_type = item.get_item(0)?;
                if obj.is_instance(&encoder_type)? {
                    return item.get_item(1)?.call1((obj,));
                }
            }
        }
    }

    let include = normalize_filter(py, options.include.as_ref().map(|value| value.bind(py)))?;
    let exclude = normalize_filter(py, options.exclude.as_ref().map(|value| value.bind(py)))?;

    if is_instance(py, obj, "pydantic", "BaseModel")? {
        let kwargs = PyDict::new(py);
        kwargs.set_item("mode", "json")?;
        if let Some(include) = include.as_ref() {
            kwargs.set_item("include", include)?;
        }
        if let Some(exclude) = exclude.as_ref() {
            kwargs.set_item("exclude", exclude)?;
        }
        kwargs.set_item("by_alias", options.by_alias)?;
        kwargs.set_item("exclude_unset", options.exclude_unset)?;
        kwargs.set_item("exclude_none", options.exclude_none)?;
        kwargs.set_item("exclude_defaults", options.exclude_defaults)?;
        let data = obj.call_method("model_dump", (), Some(&kwargs))?;
        let nested_options = JsonableEncoderOptions {
            include: None,
            exclude: None,
            by_alias: true,
            exclude_unset: false,
            exclude_defaults: options.exclude_defaults,
            exclude_none: options.exclude_none,
            custom_encoder: None,
            sqlalchemy_safe: options.sqlalchemy_safe,
        };
        return encode_value(py, &data, &nested_options);
    }

    if py
        .import("dataclasses")?
        .getattr("is_dataclass")?
        .call1((obj,))?
        .extract::<bool>()?
    {
        if obj.is_instance(&py.get_type::<PyType>())? {
            return Err(PyAssertionError::new_err(()));
        }
        let data = py.import("dataclasses")?.getattr("asdict")?.call1((obj,))?;
        return encode_value(py, &data, options);
    }

    encode_builtin_and_container_value(py, obj, options, include.as_ref(), exclude.as_ref())
}

fn encode_builtin_and_container_value<'py>(
    py: Python<'py>,
    obj: &Bound<'py, PyAny>,
    options: &JsonableEncoderOptions,
    include: Option<&Bound<'py, PyAny>>,
    exclude: Option<&Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyAny>> {
    if is_instance(py, obj, "enum", "Enum")? {
        return obj.getattr("value");
    }
    if is_instance(py, obj, "pathlib", "PurePath")? {
        return obj.str().map(Bound::into_any);
    }
    if obj.is_none()
        || is_instance(py, obj, "builtins", "str")?
        || is_instance(py, obj, "builtins", "int")?
        || is_instance(py, obj, "builtins", "float")?
    {
        return Ok(obj.clone());
    }
    if is_instance(py, obj, "pydantic_core", "PydanticUndefinedType")? {
        return Ok(py.None().into_bound(py));
    }

    if let Ok(dictionary) = obj.cast::<PyDict>() {
        let key_set = py
            .import("builtins")?
            .getattr("set")?
            .call1((dictionary.call_method0("keys")?,))?;
        if let Some(include) = include.as_ref() {
            key_set.call_method1("intersection_update", (include,))?;
        }
        if let Some(exclude) = exclude.as_ref() {
            key_set.call_method1("difference_update", (exclude,))?;
        }

        let encoded = PyDict::new(py);
        let nested_options = options.without_filters(py, true);
        for (key, value) in dictionary.iter() {
            if options.sqlalchemy_safe && is_string_with_prefix(&key, "_sa")? {
                continue;
            }
            if options.exclude_none && value.is_none() {
                continue;
            }
            if !key_set
                .call_method1("__contains__", (&key,))?
                .extract::<bool>()?
            {
                continue;
            }
            let encoded_key = encode_value(py, &key, &nested_options)?;
            let encoded_value = encode_value(py, &value, &nested_options)?;
            encoded.set_item(encoded_key, encoded_value)?;
        }
        return Ok(encoded.into_any());
    }

    if is_iterable_encoder_value(py, obj)? {
        let encoded = PyList::empty(py);
        for item in obj.try_iter()? {
            let item = item?;
            encoded.append(encode_value(py, &item, options)?)?;
        }
        return Ok(encoded.into_any());
    }

    if is_instance(py, obj, "datetime", "datetime")?
        || is_instance(py, obj, "datetime", "date")?
        || is_instance(py, obj, "datetime", "time")?
    {
        return obj.call_method0("isoformat");
    }
    if is_instance(py, obj, "datetime", "timedelta")? {
        return obj.call_method0("total_seconds");
    }
    if is_instance(py, obj, "decimal", "Decimal")? {
        let exponent = obj.call_method0("as_tuple")?.getattr("exponent")?;
        if is_instance(py, &exponent, "builtins", "int")? && exponent.extract::<i64>()? >= 0 {
            return py.import("builtins")?.getattr("int")?.call1((obj,));
        }
        return py.import("builtins")?.getattr("float")?.call1((obj,));
    }
    if is_instance(py, obj, "builtins", "bytes")? {
        return obj.call_method0("decode");
    }
    if is_instance(py, obj, "re", "Pattern")? {
        return obj.getattr("pattern");
    }
    if let Some(encoded) = encode_pydantic_builtin(py, obj)? {
        return Ok(encoded);
    }

    let dict_constructor = py.import("builtins")?.getattr("dict")?;
    match dict_constructor.call1((obj,)) {
        Ok(data) => encode_value(py, &data, options),
        Err(dict_error) => {
            let vars = py.import("builtins")?.getattr("vars")?;
            match vars.call1((obj,)) {
                Ok(data) => encode_value(py, &data, options),
                Err(vars_error) => {
                    let errors = PyList::empty(py);
                    errors.append(dict_error.value(py))?;
                    errors.append(vars_error.value(py))?;
                    let exception = PyValueError::type_object(py).call1((errors,))?;
                    exception.setattr("__cause__", vars_error.value(py))?;
                    exception.setattr("__suppress_context__", true)?;
                    Err(PyErr::from_value(exception))
                }
            }
        }
    }
}

fn is_instance(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
    module: &str,
    class: &str,
) -> PyResult<bool> {
    let class = py.import(module)?.getattr(class)?;
    value.is_instance(&class)
}

fn is_string_with_prefix(value: &Bound<'_, PyAny>, prefix: &str) -> PyResult<bool> {
    if !value.is_instance_of::<pyo3::types::PyString>() {
        return Ok(false);
    }
    value
        .call_method1("startswith", (prefix,))?
        .extract::<bool>()
}

fn is_iterable_encoder_value(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    for (module, class) in [
        ("builtins", "list"),
        ("builtins", "set"),
        ("builtins", "frozenset"),
        ("builtins", "tuple"),
        ("collections", "deque"),
        ("types", "GeneratorType"),
    ] {
        if is_instance(py, value, module, class)? {
            return Ok(true);
        }
    }
    Ok(false)
}

fn encode_pydantic_builtin<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
) -> PyResult<Option<Bound<'py, PyAny>>> {
    for (module, class) in [
        ("uuid", "UUID"),
        ("ipaddress", "IPv4Address"),
        ("ipaddress", "IPv4Interface"),
        ("ipaddress", "IPv4Network"),
        ("ipaddress", "IPv6Address"),
        ("ipaddress", "IPv6Interface"),
        ("ipaddress", "IPv6Network"),
        ("pydantic.networks", "NameEmail"),
        ("pydantic.networks", "AnyUrl"),
        ("pydantic_core", "Url"),
        ("pydantic.types", "SecretBytes"),
        ("pydantic.types", "SecretStr"),
        ("pydantic.color", "Color"),
        ("pydantic_extra_types.color", "Color"),
    ] {
        if is_instance_if_available(py, value, module, class)? {
            return value.str().map(Bound::into_any).map(Some);
        }
    }
    Ok(None)
}

fn is_instance_if_available(
    py: Python<'_>,
    value: &Bound<'_, PyAny>,
    module: &str,
    class: &str,
) -> PyResult<bool> {
    match py.import(module) {
        Ok(imported_module) => value.is_instance(&imported_module.getattr(class)?),
        Err(error) if error.is_instance_of::<pyo3::exceptions::PyImportError>(py) => Ok(false),
        Err(error) => Err(error),
    }
}
