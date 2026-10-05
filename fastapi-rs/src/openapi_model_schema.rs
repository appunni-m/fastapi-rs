//! Private declaration data for the pinned OpenAPI Schema model.

use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyInt, PyList, PySet, PyString, PyTuple};

#[derive(Clone, Copy)]
enum SchemaAnnotation {
    String,
    Boolean,
    Integer,
    Number,
    Any,
    AnyList,
    StringList,
    Schema,
    SchemaList,
    SchemaMap,
    SchemaType,
    StringSetMap,
    Discriminator,
    Xml,
    ExternalDocumentation,
    DeprecatedExample,
}

#[derive(Clone, Copy)]
enum SchemaConstraint {
    Nonnegative,
    Positive,
    None,
}

type SchemaDescriptor = (
    &'static str,
    Option<&'static str>,
    SchemaAnnotation,
    SchemaConstraint,
);

// Python field names and declaration order match FastAPI 0.141.1. Alias names
// belong to Field metadata; they are not substituted for the Python names.
const SCHEMA_FIELDS: [SchemaDescriptor; 61] = {
    use SchemaAnnotation as A;
    use SchemaConstraint as C;
    [
        ("schema_", Some("$schema"), A::String, C::None),
        ("vocabulary", Some("$vocabulary"), A::String, C::None),
        ("id", Some("$id"), A::String, C::None),
        ("anchor", Some("$anchor"), A::String, C::None),
        ("dynamicAnchor", Some("$dynamicAnchor"), A::String, C::None),
        ("ref", Some("$ref"), A::String, C::None),
        ("dynamicRef", Some("$dynamicRef"), A::String, C::None),
        ("defs", Some("$defs"), A::SchemaMap, C::None),
        ("comment", Some("$comment"), A::String, C::None),
        ("allOf", None, A::SchemaList, C::None),
        ("anyOf", None, A::SchemaList, C::None),
        ("oneOf", None, A::SchemaList, C::None),
        ("not_", Some("not"), A::Schema, C::None),
        ("if_", Some("if"), A::Schema, C::None),
        ("then", None, A::Schema, C::None),
        ("else_", Some("else"), A::Schema, C::None),
        ("dependentSchemas", None, A::SchemaMap, C::None),
        ("prefixItems", None, A::SchemaList, C::None),
        ("items", None, A::Schema, C::None),
        ("contains", None, A::Schema, C::None),
        ("properties", None, A::SchemaMap, C::None),
        ("patternProperties", None, A::SchemaMap, C::None),
        ("additionalProperties", None, A::Schema, C::None),
        ("propertyNames", None, A::Schema, C::None),
        ("unevaluatedItems", None, A::Schema, C::None),
        ("unevaluatedProperties", None, A::Schema, C::None),
        ("type", None, A::SchemaType, C::None),
        ("enum", None, A::AnyList, C::None),
        ("const", None, A::Any, C::None),
        ("multipleOf", None, A::Number, C::Positive),
        ("maximum", None, A::Number, C::None),
        ("exclusiveMaximum", None, A::Number, C::None),
        ("minimum", None, A::Number, C::None),
        ("exclusiveMinimum", None, A::Number, C::None),
        ("maxLength", None, A::Integer, C::Nonnegative),
        ("minLength", None, A::Integer, C::Nonnegative),
        ("pattern", None, A::String, C::None),
        ("maxItems", None, A::Integer, C::Nonnegative),
        ("minItems", None, A::Integer, C::Nonnegative),
        ("uniqueItems", None, A::Boolean, C::None),
        ("maxContains", None, A::Integer, C::Nonnegative),
        ("minContains", None, A::Integer, C::Nonnegative),
        ("maxProperties", None, A::Integer, C::Nonnegative),
        ("minProperties", None, A::Integer, C::Nonnegative),
        ("required", None, A::StringList, C::None),
        ("dependentRequired", None, A::StringSetMap, C::None),
        ("format", None, A::String, C::None),
        ("contentEncoding", None, A::String, C::None),
        ("contentMediaType", None, A::String, C::None),
        ("contentSchema", None, A::Schema, C::None),
        ("title", None, A::String, C::None),
        ("description", None, A::String, C::None),
        ("default", None, A::Any, C::None),
        ("deprecated", None, A::Boolean, C::None),
        ("readOnly", None, A::Boolean, C::None),
        ("writeOnly", None, A::Boolean, C::None),
        ("examples", None, A::AnyList, C::None),
        ("discriminator", None, A::Discriminator, C::None),
        ("xml", None, A::Xml, C::None),
        ("externalDocs", None, A::ExternalDocumentation, C::None),
        ("example", None, A::DeprecatedExample, C::None),
    ]
};

/// Returns ordered keyword field data for the private Schema model.
///
/// The caller supplies its extra-allowing base and rebuilds every model using a
/// complete type namespace. Fixed ForwardRefs express SchemaOrBool recursion
/// and companion classes; no user annotation or Python source is evaluated.
pub(crate) fn schema_fields(py: Python<'_>) -> PyResult<Py<PyDict>> {
    let typing = py.import("typing")?;
    let union = py.import("operator")?.getattr("or_")?;
    let optional = typing.getattr("Optional")?;
    let forward_ref = typing.getattr("ForwardRef")?;
    let any = typing.getattr("Any")?;
    let none_type = py.None().bind(py).get_type().into_any();
    let string_type = py.get_type::<PyString>().into_any();
    let boolean_type = py.get_type::<PyBool>().into_any();
    let integer_type = py.get_type::<PyInt>().into_any();
    let number_type = py.get_type::<PyFloat>().into_any();
    let list_type = py.get_type::<PyList>().into_any();
    let dict_type = py.get_type::<PyDict>().into_any();
    let set_type = py.get_type::<PySet>().into_any();
    let schema = forward_ref.call1(("SchemaOrBool",))?;
    let schema_list = list_type.get_item(&schema)?;
    let schema_map = dict_type.get_item(PyTuple::new(py, [&string_type, &schema])?)?;
    let any_list = list_type.get_item(&any)?;
    let string_list = list_type.get_item(&string_type)?;
    let string_set = set_type.get_item(&string_type)?;
    let string_set_map = dict_type.get_item(PyTuple::new(py, [&string_type, &string_set])?)?;
    let schema_type = typing.getattr("Literal")?.get_item(PyTuple::new(
        py,
        [
            "array", "boolean", "integer", "null", "number", "object", "string",
        ],
    )?)?;
    let schema_type_list = list_type.get_item(&schema_type)?;
    let schema_type_union = union.call1((&schema_type, &schema_type_list))?;
    let discriminator = forward_ref.call1(("Discriminator",))?;
    let xml = forward_ref.call1(("XML",))?;
    let external_docs = forward_ref.call1(("ExternalDocumentation",))?;
    let field = py.import("pydantic")?.getattr("Field")?;
    let fields = PyDict::new(py);

    for (name, alias, kind, constraint) in SCHEMA_FIELDS {
        let base_annotation = match kind {
            SchemaAnnotation::String => &string_type,
            SchemaAnnotation::Boolean => &boolean_type,
            SchemaAnnotation::Integer => &integer_type,
            SchemaAnnotation::Number => &number_type,
            SchemaAnnotation::Any | SchemaAnnotation::DeprecatedExample => &any,
            SchemaAnnotation::AnyList => &any_list,
            SchemaAnnotation::StringList => &string_list,
            SchemaAnnotation::Schema => &schema,
            SchemaAnnotation::SchemaList => &schema_list,
            SchemaAnnotation::SchemaMap => &schema_map,
            SchemaAnnotation::SchemaType => &schema_type_union,
            SchemaAnnotation::StringSetMap => &string_set_map,
            SchemaAnnotation::Discriminator => &discriminator,
            SchemaAnnotation::Xml => &xml,
            SchemaAnnotation::ExternalDocumentation => &external_docs,
        };
        let nullable = if matches!(kind, SchemaAnnotation::Schema) {
            optional.get_item(base_annotation)?
        } else {
            union.call1((base_annotation, &none_type))?
        };
        let annotation = if matches!(kind, SchemaAnnotation::DeprecatedExample) {
            let deprecated = py
                .import("typing_extensions")?
                .getattr("deprecated")?
                .call1((
                    "Deprecated in OpenAPI 3.1.0 that now uses JSON Schema 2020-12, \
                 although still supported. Use examples instead.",
                ))?;
            typing
                .getattr("Annotated")?
                .get_item(PyTuple::new(py, [nullable, deprecated])?)?
        } else {
            nullable
        };
        let default = if alias.is_some() || !matches!(constraint, SchemaConstraint::None) {
            let options = PyDict::new(py);
            options.set_item("default", py.None())?;
            if let Some(alias) = alias {
                options.set_item("alias", alias)?;
            }
            match constraint {
                SchemaConstraint::Nonnegative => options.set_item("ge", 0)?,
                SchemaConstraint::Positive => options.set_item("gt", 0)?,
                SchemaConstraint::None => {}
            }
            field.call((), Some(&options))?
        } else {
            py.None().into_bound(py)
        };
        fields.set_item(name, PyTuple::new(py, [annotation, default])?)?;
    }
    Ok(fields.unbind())
}
