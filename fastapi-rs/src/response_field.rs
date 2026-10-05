//! Construction and ownership of a primary FastAPI response field.

use pyo3::exceptions::{PyImportError, PyTypeError, PyUserWarning};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyModule, PyString, PyTuple, PyType};

// FastAPI 0.141.1's compatibility decomposition deliberately omits Undefined
// values. Pydantic's FieldInfo.asdict() retains them on the pinned version.
const FIELD_ATTRIBUTES: [&str; 21] = [
    "default",
    "default_factory",
    "alias",
    "alias_priority",
    "validation_alias",
    "serialization_alias",
    "title",
    "field_title_generator",
    "description",
    "examples",
    "exclude",
    "exclude_if",
    "discriminator",
    "deprecated",
    "json_schema_extra",
    "frozen",
    "validate_default",
    "repr",
    "init",
    "init_var",
    "kw_only",
];

const INVALID_ARGS_MESSAGE: &str = concat!(
    "Invalid args for response field! Hint: ",
    "check that {type_} is a valid Pydantic field type. ",
    "If you are using a return type annotation that is not a valid Pydantic ",
    "field (e.g. Union[Response, dict, None]) you can disable generating the ",
    "response model from the type annotation with the path operation decorator ",
    "parameter response_model=None. Read more: ",
    "https://fastapi.tiangolo.com/tutorial/response-model/",
);

/// An owned field and the adapter constructed for its route context.
///
/// Construction can invoke user schema hooks. Callers must release application,
/// router and cache borrows or locks before calling `new` or dropping a field.
pub(crate) struct ResponseField {
    pub(crate) name: Py<PyString>,
    pub(crate) annotation: Py<PyAny>,
    pub(crate) field_info: Py<PyAny>,
    pub(crate) field_annotation: Py<PyAny>,
    pub(crate) metadata: Py<PyAny>,
    pub(crate) attributes: Py<PyDict>,
    pub(crate) reconstructed_field: Py<PyAny>,
    pub(crate) schema_annotation: Py<PyAny>,
    pub(crate) adapter: Py<PyAny>,
    pub(crate) mode: &'static str,
    pub(crate) config: Py<PyAny>,
}

impl ResponseField {
    /// Constructs the primary field used in response serialization.
    ///
    /// This follows FastAPI's `create_model_field` and v2 `ModelField` setup for
    /// an Undefined default, no alias, serialization mode and no adapter config.
    pub(crate) fn new(py: Python<'_>, name: &str, annotation: &Bound<'_, PyAny>) -> PyResult<Self> {
        if annotation_is_pydantic_v1(py, annotation)? {
            let representation = annotation.repr()?.extract::<String>()?;
            return Err(crate::errors::PydanticV1NotSupportedError::new_err(
                format!(
                    "pydantic.v1 models are no longer supported by FastAPI. Please update the response model {representation}."
                ),
            ));
        }

        let undefined = py.import("pydantic_core")?.getattr("PydanticUndefined")?;
        let options = PyDict::new(py);
        options.set_item("annotation", annotation)?;
        options.set_item("default", &undefined)?;
        options.set_item("alias", py.None())?;
        // FieldInfo construction precedes the source's schema-error catch.
        let field_info = py
            .import("pydantic.fields")?
            .getattr("FieldInfo")?
            .call((), Some(&options))?;
        let pydantic = py.import("pydantic")?;
        let schema_generation_error = pydantic.getattr("PydanticSchemaGenerationError")?;

        let constructed = with_warnings_context(py, |warnings| {
            // The pinned Pydantic 2.13.4 selects FastAPI's >= 2.12 branch.
            let category = py
                .import("pydantic.warnings")?
                .getattr("UnsupportedFieldAttributeWarning")?;
            let filter_options = PyDict::new(py);
            filter_options.set_item("category", category)?;
            warnings
                .getattr("simplefilter")?
                .call(("ignore",), Some(&filter_options))?;

            let attributes = PyDict::new(py);
            for attribute in FIELD_ATTRIBUTES {
                if let Some(value) = field_info.getattr_opt(attribute)? {
                    if !value.is(&undefined) {
                        attributes.set_item(attribute, value)?;
                    }
                }
            }
            let field_annotation = field_info.getattr("annotation")?;
            let metadata = field_info.getattr("metadata")?;
            // Source evaluates/unpacks metadata before invoking fresh Field.
            let mut annotated_arguments = vec![field_annotation.clone().unbind()];
            for item in metadata.try_iter()? {
                annotated_arguments.push(item?.unbind());
            }
            let reconstructed_field = pydantic.getattr("Field")?.call((), Some(&attributes))?;
            annotated_arguments.push(reconstructed_field.clone().unbind());
            let schema_annotation = py
                .import("typing")?
                .getattr("Annotated")?
                .get_item(PyTuple::new(py, annotated_arguments)?)?;
            let config = py.None();
            let adapter_options = PyDict::new(py);
            adapter_options.set_item("config", config.bind(py))?;
            let adapter = pydantic
                .getattr("TypeAdapter")?
                .call((&schema_annotation,), Some(&adapter_options))?;

            Ok(Self {
                name: PyString::new(py, name).unbind(),
                annotation: annotation.clone().unbind(),
                field_info: field_info.clone().unbind(),
                field_annotation: field_annotation.unbind(),
                metadata: metadata.unbind(),
                attributes: attributes.unbind(),
                reconstructed_field: reconstructed_field.unbind(),
                schema_annotation: schema_annotation.unbind(),
                adapter: adapter.unbind(),
                mode: "serialization",
                config,
            })
        });

        match constructed {
            Err(error) if error.is_instance(py, &schema_generation_error) => {
                let options = PyDict::new(py);
                options.set_item("type_", annotation)?;
                let message = match PyString::new(py, INVALID_ARGS_MESSAGE).call_method(
                    "format",
                    (),
                    Some(&options),
                ) {
                    Ok(message) => message.extract::<String>()?,
                    Err(format_error) => {
                        format_error.set_context(py, Some(error));
                        return Err(format_error);
                    }
                };
                let translated = crate::errors::fastapi_error(&message);
                translated.set_context(py, Some(error));
                translated.set_cause(py, None);
                Err(translated)
            }
            result => result,
        }
    }

    /// Copies owned references without constructing another adapter or field.
    pub(crate) fn clone_ref(&self, py: Python<'_>) -> Self {
        Self {
            name: self.name.clone_ref(py),
            annotation: self.annotation.clone_ref(py),
            field_info: self.field_info.clone_ref(py),
            field_annotation: self.field_annotation.clone_ref(py),
            metadata: self.metadata.clone_ref(py),
            attributes: self.attributes.clone_ref(py),
            reconstructed_field: self.reconstructed_field.clone_ref(py),
            schema_annotation: self.schema_annotation.clone_ref(py),
            adapter: self.adapter.clone_ref(py),
            mode: self.mode,
            config: self.config.clone_ref(py),
        }
    }
}

fn with_warnings_context<T>(
    py: Python<'_>,
    operation: impl FnOnce(&Bound<'_, PyModule>) -> PyResult<T>,
) -> PyResult<T> {
    let warnings = py.import("warnings")?;
    let context = warnings.getattr("catch_warnings")?.call0()?;
    let enter = context.getattr("__enter__")?;
    let exit = context.getattr("__exit__")?;
    enter.call0()?;
    match operation(&warnings) {
        Ok(value) => {
            exit.call1((py.None(), py.None(), py.None()))?;
            Ok(value)
        }
        Err(error) => {
            let value = error.clone_ref(py).into_value(py);
            let traceback = error
                .traceback(py)
                .map(|traceback| traceback.into_any().unbind())
                .unwrap_or_else(|| py.None());
            // Pinned catch_warnings restores its state and returns None. Pass
            // the real triple, and preserve a restoration error if it raises.
            if let Err(exit_error) = exit.call1((error.get_type(py), value, traceback)) {
                exit_error.set_context(py, Some(error));
                return Err(exit_error);
            }
            Err(error)
        }
    }
}

fn is_pydantic_v1_model_class(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    // FastAPI confines this broader UserWarning filter to its legacy import.
    let legacy_pydantic = match with_warnings_context(py, |warnings| {
        warnings
            .getattr("simplefilter")?
            .call1(("ignore", py.get_type::<PyUserWarning>()))?;
        py.import("pydantic.v1").map(Bound::unbind)
    }) {
        Ok(module) => module,
        Err(error) if error.is_instance_of::<PyImportError>(py) => return Ok(false),
        Err(error) => return Err(error),
    };
    lenient_issubclass(
        py,
        annotation,
        &legacy_pydantic.bind(py).getattr("BaseModel")?,
    )
}

fn annotation_is_pydantic_v1(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    if is_pydantic_v1_model_class(py, annotation)? {
        return Ok(true);
    }
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    if is_union_origin(py, &origin)? {
        let arguments = typing.getattr("get_args")?.call1((annotation,))?;
        for argument in arguments.try_iter()? {
            if is_pydantic_v1_model_class(py, &argument?)? {
                return Ok(true);
            }
        }
    }
    if field_annotation_is_sequence(py, annotation)? {
        let arguments = typing.getattr("get_args")?.call1((annotation,))?;
        for argument in arguments.try_iter()? {
            if annotation_is_pydantic_v1(py, &argument?)? {
                return Ok(true);
            }
        }
    }
    Ok(false)
}

fn field_annotation_is_sequence(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let typing = py.import("typing")?;
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    if origin.is(&typing.getattr("Annotated")?) {
        let arguments = typing.getattr("get_args")?.call1((annotation,))?;
        return field_annotation_is_sequence(py, &arguments.get_item(0)?);
    }
    if is_union_origin(py, &origin)? {
        let arguments = typing.getattr("get_args")?.call1((annotation,))?;
        for argument in arguments.try_iter()? {
            if field_annotation_is_sequence(py, &argument?)? {
                return Ok(true);
            }
        }
        return Ok(false);
    }
    if annotation_is_sequence(py, annotation)? {
        return Ok(true);
    }
    let origin = typing.getattr("get_origin")?.call1((annotation,))?;
    annotation_is_sequence(py, &origin)
}

fn is_union_origin(py: Python<'_>, origin: &Bound<'_, PyAny>) -> PyResult<bool> {
    Ok(origin.is(&py.import("typing")?.getattr("Union")?)
        || origin.is(&py.import("types")?.getattr("UnionType")?))
}

fn annotation_is_sequence(py: Python<'_>, annotation: &Bound<'_, PyAny>) -> PyResult<bool> {
    let string_types = PyTuple::new(
        py,
        [
            py.get_type::<PyString>().into_any(),
            py.get_type::<PyBytes>().into_any(),
        ],
    )?;
    if lenient_issubclass(py, annotation, string_types.as_any())? {
        return Ok(false);
    }
    let builtins = py.import("builtins")?;
    let sequence_types = PyTuple::new(
        py,
        [
            py.import("collections.abc")?.getattr("Sequence")?,
            builtins.getattr("list")?,
            builtins.getattr("tuple")?,
            builtins.getattr("set")?,
            builtins.getattr("frozenset")?,
            py.import("collections")?.getattr("deque")?,
        ],
    )?;
    lenient_issubclass(py, annotation, sequence_types.as_any())
}

fn lenient_issubclass(
    py: Python<'_>,
    annotation: &Bound<'_, PyAny>,
    classes: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let checked = (|| {
        if !annotation.is_instance(&py.get_type::<PyType>())? {
            return Ok(false);
        }
        py.import("builtins")?
            .getattr("issubclass")?
            .call1((annotation, classes))?
            .is_truthy()
    })();
    match checked {
        Err(error) if error.is_instance_of::<PyTypeError>(py) => {
            let types = py.import("types")?;
            let with_arguments = PyTuple::new(
                py,
                [
                    py.import("typing")?.getattr("_GenericAlias")?,
                    types.getattr("GenericAlias")?,
                    types.getattr("UnionType")?,
                ],
            )?;
            if annotation.is_instance(with_arguments.as_any())? {
                Ok(false)
            } else {
                Err(error)
            }
        }
        result => result,
    }
}
