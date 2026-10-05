//! Private Pydantic graph used to validate assembled OpenAPI documents.
//!
//! Rust constructs the pinned model definitions through Pydantic's public
//! dynamic-model API. The graph is not a public OpenAPI model implementation:
//! only its root validator is retained on the native module.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule, PyString, PyTuple};

const MODEL_MODULE: &str = "fastapi.openapi.models";
const ROOT_HANDLE: &str = "_FastApiOpenApiModel";

enum Annotation {
    Named(&'static str),
    Forward(&'static str),
    Union(&'static [Self]),
    TypingUnion(&'static [Self]),
    List(&'static Self),
    Dict(&'static Self, &'static Self),
    Literal(&'static [&'static str]),
    MinLength(&'static Self, usize),
}

enum DefaultValue {
    Required,
    None,
    EmptyDict,
    Text(&'static str),
    EnumMember(&'static str, &'static str),
}

struct FieldDefinition {
    name: &'static str,
    annotation: Annotation,
    default: DefaultValue,
    alias: Option<&'static str>,
}

enum GraphDefinition {
    Model {
        name: &'static str,
        base: &'static str,
        fields: &'static [FieldDefinition],
        extra_allow: bool,
    },
    Enum {
        name: &'static str,
        members: &'static [(&'static str, &'static str)],
    },
    Alias {
        name: &'static str,
        annotation: Annotation,
    },
    Schema,
    Example(&'static [FieldDefinition]),
}

/// Builds and publishes the complete private graph before user factories run.
///
/// Model construction, namespace rebuilding, and partial-reference destruction
/// occur without application or cache borrows. Publication follows a successful
/// rebuild of every model, so a failed registration exposes no partial root.
pub(crate) fn register(py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    let pydantic = py.import("pydantic")?;
    let namespace = PyDict::new(py);
    let builtins = py.import("builtins")?;
    for name in ["str", "bool", "int", "float"] {
        namespace.set_item(name, builtins.getattr(name)?)?;
    }
    namespace.set_item("NoneType", py.None().bind(py).get_type())?;
    namespace.set_item("Any", py.import("typing")?.getattr("Any")?)?;
    namespace.set_item("AnyUrl", pydantic.getattr("AnyUrl")?)?;
    namespace.set_item("BaseModel", pydantic.getattr("BaseModel")?)?;
    namespace.set_item("EmailStr", crate::openapi_model_email::email_type(py)?)?;

    let mut models = Vec::new();
    for definition in GRAPH {
        match definition {
            GraphDefinition::Model {
                name,
                base,
                fields,
                extra_allow,
            } => {
                let model = create_model(py, &namespace, name, base, fields, *extra_allow)?;
                namespace.set_item(name, &model)?;
                models.push(model.unbind());
            }
            GraphDefinition::Enum { name, members } => {
                namespace.set_item(name, create_enum(py, name, members)?)?;
            }
            GraphDefinition::Alias { name, annotation } => {
                namespace.set_item(name, annotation.resolve(py, &namespace)?)?;
            }
            GraphDefinition::Schema => {
                let fields = crate::openapi_model_schema::schema_fields(py)?;
                let options = fields.bind(py);
                options.set_item("__module__", MODEL_MODULE)?;
                options.set_item("__base__", named(&namespace, "BaseModelWithConfig")?)?;
                let model = pydantic
                    .getattr("create_model")?
                    .call(("Schema",), Some(options))?;
                namespace.set_item("Schema", &model)?;
                models.push(model.unbind());
            }
            GraphDefinition::Example(fields) => {
                namespace.set_item("Example", create_example(py, &namespace, fields)?)?;
            }
        }
    }

    let options = PyDict::new(py);
    options.set_item("_types_namespace", &namespace)?;
    for model in models {
        model
            .bind(py)
            .call_method("model_rebuild", (), Some(&options))?;
    }
    module.add(ROOT_HANDLE, named(&namespace, "OpenAPI")?)
}

/// Applies the private source-shaped root model to a complete raw document.
///
/// The caller subsequently runs Rust's existing `jsonable_encoder` with the
/// source alias/exclusion options. Pydantic selects all model/Any union branches;
/// no route or dictionary-shape heuristic chooses a serialization path here.
pub(crate) fn finalize_document<'py>(
    py: Python<'py>,
    document: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyAny>> {
    py.import("fastapi_rs._core")?
        .getattr(ROOT_HANDLE)?
        .call((), Some(document))
}

fn named<'py>(namespace: &Bound<'py, PyDict>, name: &str) -> PyResult<Bound<'py, PyAny>> {
    namespace.get_item(name)?.ok_or_else(|| {
        PyRuntimeError::new_err(format!("OpenAPI model namespace is missing {name}"))
    })
}

impl Annotation {
    fn resolve<'py>(
        &self,
        py: Python<'py>,
        namespace: &Bound<'py, PyDict>,
    ) -> PyResult<Bound<'py, PyAny>> {
        match self {
            Self::Named(name) => named(namespace, name),
            Self::Forward(name) => py.import("typing")?.getattr("ForwardRef")?.call1((name,)),
            Self::Union(members) => {
                let mut members = members.iter();
                let first = members.next().ok_or_else(|| {
                    PyRuntimeError::new_err("OpenAPI union definition has no members")
                })?;
                let mut annotation = first.resolve(py, namespace)?;
                let union = py.import("operator")?.getattr("or_")?;
                for member in members {
                    annotation = union.call1((annotation, member.resolve(py, namespace)?))?;
                }
                Ok(annotation)
            }
            Self::TypingUnion(members) => {
                let members = members
                    .iter()
                    .map(|member| member.resolve(py, namespace))
                    .collect::<PyResult<Vec<_>>>()?;
                py.import("typing")?
                    .getattr("Union")?
                    .call_method1("__getitem__", (PyTuple::new(py, members)?,))
            }
            Self::List(item) => py
                .import("builtins")?
                .getattr("list")?
                .call_method1("__class_getitem__", (item.resolve(py, namespace)?,)),
            Self::Dict(key, value) => py.import("builtins")?.getattr("dict")?.call_method1(
                "__class_getitem__",
                ((key.resolve(py, namespace)?, value.resolve(py, namespace)?),),
            ),
            Self::Literal(values) => py
                .import("typing")?
                .getattr("Literal")?
                .call_method1("__getitem__", (PyTuple::new(py, *values)?,)),
            Self::MinLength(annotation, minimum) => {
                let options = PyDict::new(py);
                options.set_item("min_length", minimum)?;
                let metadata = py
                    .import("pydantic")?
                    .getattr("Field")?
                    .call((), Some(&options))?;
                py.import("typing")?.getattr("Annotated")?.call_method1(
                    "__class_getitem__",
                    ((annotation.resolve(py, namespace)?, metadata),),
                )
            }
        }
    }
}

impl DefaultValue {
    fn resolve<'py>(
        &self,
        py: Python<'py>,
        namespace: &Bound<'py, PyDict>,
    ) -> PyResult<Bound<'py, PyAny>> {
        match self {
            Self::Required => py.import("pydantic_core")?.getattr("PydanticUndefined"),
            Self::None => Ok(py.None().into_bound(py)),
            Self::EmptyDict => Ok(PyDict::new(py).into_any()),
            Self::Text(value) => Ok(PyString::new(py, value).into_any()),
            Self::EnumMember(owner, member) => named(namespace, owner)?.getattr(member),
        }
    }
}

fn create_model<'py>(
    py: Python<'py>,
    namespace: &Bound<'py, PyDict>,
    name: &str,
    base: &str,
    fields: &[FieldDefinition],
    extra_allow: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let options = PyDict::new(py);
    options.set_item("__module__", MODEL_MODULE)?;
    if extra_allow {
        let config = PyDict::new(py);
        config.set_item("extra", "allow")?;
        options.set_item("__config__", config)?;
    } else {
        options.set_item("__base__", named(namespace, base)?)?;
    }
    for field in fields {
        let annotation = field.annotation.resolve(py, namespace)?;
        if let Some(alias) = field.alias {
            let field_options = PyDict::new(py);
            field_options.set_item("alias", alias)?;
            if !matches!(field.default, DefaultValue::Required) {
                field_options.set_item("default", field.default.resolve(py, namespace)?)?;
            }
            let value = py
                .import("pydantic")?
                .getattr("Field")?
                .call((), Some(&field_options))?;
            options.set_item(field.name, (annotation, value))?;
        } else if matches!(field.default, DefaultValue::Required) {
            options.set_item(field.name, annotation)?;
        } else {
            options.set_item(
                field.name,
                (annotation, field.default.resolve(py, namespace)?),
            )?;
        }
    }
    py.import("pydantic")?
        .getattr("create_model")?
        .call((name,), Some(&options))
}

fn create_enum<'py>(
    py: Python<'py>,
    name: &str,
    members: &[(&str, &str)],
) -> PyResult<Bound<'py, PyAny>> {
    let values = PyDict::new(py);
    for (name, value) in members {
        values.set_item(name, value)?;
    }
    let options = PyDict::new(py);
    options.set_item("module", MODEL_MODULE)?;
    py.import("enum")?
        .getattr("Enum")?
        .call((name, values), Some(&options))
}

fn create_example<'py>(
    py: Python<'py>,
    namespace: &Bound<'py, PyDict>,
    fields: &[FieldDefinition],
) -> PyResult<Bound<'py, PyAny>> {
    let annotations = PyDict::new(py);
    for field in fields {
        annotations.set_item(field.name, field.annotation.resolve(py, namespace)?)?;
    }
    let options = PyDict::new(py);
    options.set_item("total", false)?;
    let example = py
        .import("typing_extensions")?
        .getattr("TypedDict")?
        .call(("Example", annotations), Some(&options))?;
    example.setattr("__module__", MODEL_MODULE)?;
    let config = PyDict::new(py);
    config.set_item("extra", "allow")?;
    example.setattr("__pydantic_config__", config)?;
    Ok(example)
}

// Pinned fastapi/openapi/models.py annotation data; definition order is retained.
const GRAPH: &[GraphDefinition] = &[
    GraphDefinition::Model {
        name: "BaseModelWithConfig",
        base: "BaseModel",
        extra_allow: true,
        fields: &[],
    },
    GraphDefinition::Model {
        name: "Contact",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "name",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "url",
                annotation: Annotation::Union(&[
                    Annotation::Named("AnyUrl"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "email",
                annotation: Annotation::Union(&[
                    Annotation::Named("EmailStr"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "License",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "name",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "identifier",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "url",
                annotation: Annotation::Union(&[
                    Annotation::Named("AnyUrl"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Info",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "title",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "summary",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "termsOfService",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "contact",
                annotation: Annotation::Union(&[
                    Annotation::Named("Contact"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "license",
                annotation: Annotation::Union(&[
                    Annotation::Named("License"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "version",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "ServerVariable",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "enum",
                annotation: Annotation::MinLength(
                    &Annotation::Union(&[
                        Annotation::List(&Annotation::Named("str")),
                        Annotation::Named("NoneType"),
                    ]),
                    1,
                ),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "default",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Server",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "url",
                annotation: Annotation::Union(&[
                    Annotation::Named("AnyUrl"),
                    Annotation::Named("str"),
                ]),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "variables",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Named("ServerVariable"),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Reference",
        base: "BaseModel",
        extra_allow: false,
        fields: &[FieldDefinition {
            name: "ref",
            annotation: Annotation::Named("str"),
            default: DefaultValue::Required,
            alias: Some("$ref"),
        }],
    },
    GraphDefinition::Model {
        name: "Discriminator",
        base: "BaseModel",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "propertyName",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "mapping",
                annotation: Annotation::Union(&[
                    Annotation::Dict(&Annotation::Named("str"), &Annotation::Named("str")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "XML",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "name",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "namespace",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "prefix",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "attribute",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "wrapped",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "ExternalDocumentation",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "url",
                annotation: Annotation::Named("AnyUrl"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Alias {
        name: "SchemaType",
        annotation: Annotation::Literal(&[
            "array", "boolean", "integer", "null", "number", "object", "string",
        ]),
    },
    GraphDefinition::Schema,
    GraphDefinition::Alias {
        name: "SchemaOrBool",
        annotation: Annotation::Union(&[Annotation::Named("Schema"), Annotation::Named("bool")]),
    },
    GraphDefinition::Example(&[
        FieldDefinition {
            name: "summary",
            annotation: Annotation::Union(&[
                Annotation::Named("str"),
                Annotation::Named("NoneType"),
            ]),
            default: DefaultValue::Required,
            alias: None,
        },
        FieldDefinition {
            name: "description",
            annotation: Annotation::Union(&[
                Annotation::Named("str"),
                Annotation::Named("NoneType"),
            ]),
            default: DefaultValue::Required,
            alias: None,
        },
        FieldDefinition {
            name: "value",
            annotation: Annotation::Union(&[
                Annotation::Named("Any"),
                Annotation::Named("NoneType"),
            ]),
            default: DefaultValue::Required,
            alias: None,
        },
        FieldDefinition {
            name: "externalValue",
            annotation: Annotation::Union(&[
                Annotation::Named("AnyUrl"),
                Annotation::Named("NoneType"),
            ]),
            default: DefaultValue::Required,
            alias: None,
        },
    ]),
    GraphDefinition::Enum {
        name: "ParameterInType",
        members: &[
            ("query", "query"),
            ("header", "header"),
            ("path", "path"),
            ("cookie", "cookie"),
        ],
    },
    GraphDefinition::Model {
        name: "Encoding",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "contentType",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "headers",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::TypingUnion(&[
                            Annotation::Forward("Header"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "style",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "explode",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "allowReserved",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "MediaType",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "schema_",
                annotation: Annotation::Union(&[
                    Annotation::Named("Schema"),
                    Annotation::Named("Reference"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: Some("schema"),
            },
            FieldDefinition {
                name: "example",
                annotation: Annotation::Union(&[
                    Annotation::Named("Any"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "examples",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Example"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "encoding",
                annotation: Annotation::Union(&[
                    Annotation::Dict(&Annotation::Named("str"), &Annotation::Named("Encoding")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "ParameterBase",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "required",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "deprecated",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "style",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "explode",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "allowReserved",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "schema_",
                annotation: Annotation::Union(&[
                    Annotation::Named("Schema"),
                    Annotation::Named("Reference"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: Some("schema"),
            },
            FieldDefinition {
                name: "example",
                annotation: Annotation::Union(&[
                    Annotation::Named("Any"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "examples",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Example"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "content",
                annotation: Annotation::Union(&[
                    Annotation::Dict(&Annotation::Named("str"), &Annotation::Named("MediaType")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Parameter",
        base: "ParameterBase",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "name",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "in_",
                annotation: Annotation::Named("ParameterInType"),
                default: DefaultValue::Required,
                alias: Some("in"),
            },
        ],
    },
    GraphDefinition::Model {
        name: "Header",
        base: "ParameterBase",
        extra_allow: false,
        fields: &[],
    },
    GraphDefinition::Model {
        name: "RequestBody",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "content",
                annotation: Annotation::Dict(
                    &Annotation::Named("str"),
                    &Annotation::Named("MediaType"),
                ),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "required",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Link",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "operationRef",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "operationId",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "parameters",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[Annotation::Named("Any"), Annotation::Named("str")]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "requestBody",
                annotation: Annotation::Union(&[
                    Annotation::Named("Any"),
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "server",
                annotation: Annotation::Union(&[
                    Annotation::Named("Server"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Response",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "description",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "headers",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Header"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "content",
                annotation: Annotation::Union(&[
                    Annotation::Dict(&Annotation::Named("str"), &Annotation::Named("MediaType")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "links",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Link"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Operation",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "tags",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Named("str")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "summary",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "externalDocs",
                annotation: Annotation::Union(&[
                    Annotation::Named("ExternalDocumentation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "operationId",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "parameters",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Union(&[
                        Annotation::Named("Parameter"),
                        Annotation::Named("Reference"),
                    ])),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "requestBody",
                annotation: Annotation::Union(&[
                    Annotation::Named("RequestBody"),
                    Annotation::Named("Reference"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "responses",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Response"),
                            Annotation::Named("Any"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "callbacks",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Dict(
                                &Annotation::Named("str"),
                                &Annotation::Forward("PathItem"),
                            ),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "deprecated",
                annotation: Annotation::Union(&[
                    Annotation::Named("bool"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "security",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::List(&Annotation::Named("str")),
                    )),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "servers",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Named("Server")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "PathItem",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "ref",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: Some("$ref"),
            },
            FieldDefinition {
                name: "summary",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "get",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "put",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "post",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "delete",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "options",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "head",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "patch",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "trace",
                annotation: Annotation::Union(&[
                    Annotation::Named("Operation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "servers",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Named("Server")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "parameters",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Union(&[
                        Annotation::Named("Parameter"),
                        Annotation::Named("Reference"),
                    ])),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Enum {
        name: "SecuritySchemeType",
        members: &[
            ("apiKey", "apiKey"),
            ("http", "http"),
            ("oauth2", "oauth2"),
            ("openIdConnect", "openIdConnect"),
        ],
    },
    GraphDefinition::Model {
        name: "SecurityBase",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "type_",
                annotation: Annotation::Named("SecuritySchemeType"),
                default: DefaultValue::Required,
                alias: Some("type"),
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Enum {
        name: "APIKeyIn",
        members: &[
            ("query", "query"),
            ("header", "header"),
            ("cookie", "cookie"),
        ],
    },
    GraphDefinition::Model {
        name: "APIKey",
        base: "SecurityBase",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "type_",
                annotation: Annotation::Named("SecuritySchemeType"),
                default: DefaultValue::EnumMember("SecuritySchemeType", "apiKey"),
                alias: Some("type"),
            },
            FieldDefinition {
                name: "in_",
                annotation: Annotation::Named("APIKeyIn"),
                default: DefaultValue::Required,
                alias: Some("in"),
            },
            FieldDefinition {
                name: "name",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "HTTPBase",
        base: "SecurityBase",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "type_",
                annotation: Annotation::Named("SecuritySchemeType"),
                default: DefaultValue::EnumMember("SecuritySchemeType", "http"),
                alias: Some("type"),
            },
            FieldDefinition {
                name: "scheme",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "HTTPBearer",
        base: "HTTPBase",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "scheme",
                annotation: Annotation::Literal(&["bearer"]),
                default: DefaultValue::Text("bearer"),
                alias: None,
            },
            FieldDefinition {
                name: "bearerFormat",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "OAuthFlow",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "refreshUrl",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "scopes",
                annotation: Annotation::Dict(&Annotation::Named("str"), &Annotation::Named("str")),
                default: DefaultValue::EmptyDict,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "OAuthFlowImplicit",
        base: "OAuthFlow",
        extra_allow: false,
        fields: &[FieldDefinition {
            name: "authorizationUrl",
            annotation: Annotation::Named("str"),
            default: DefaultValue::Required,
            alias: None,
        }],
    },
    GraphDefinition::Model {
        name: "OAuthFlowPassword",
        base: "OAuthFlow",
        extra_allow: false,
        fields: &[FieldDefinition {
            name: "tokenUrl",
            annotation: Annotation::Named("str"),
            default: DefaultValue::Required,
            alias: None,
        }],
    },
    GraphDefinition::Model {
        name: "OAuthFlowClientCredentials",
        base: "OAuthFlow",
        extra_allow: false,
        fields: &[FieldDefinition {
            name: "tokenUrl",
            annotation: Annotation::Named("str"),
            default: DefaultValue::Required,
            alias: None,
        }],
    },
    GraphDefinition::Model {
        name: "OAuthFlowAuthorizationCode",
        base: "OAuthFlow",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "authorizationUrl",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "tokenUrl",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "OAuthFlows",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "implicit",
                annotation: Annotation::Union(&[
                    Annotation::Named("OAuthFlowImplicit"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "password",
                annotation: Annotation::Union(&[
                    Annotation::Named("OAuthFlowPassword"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "clientCredentials",
                annotation: Annotation::Union(&[
                    Annotation::Named("OAuthFlowClientCredentials"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "authorizationCode",
                annotation: Annotation::Union(&[
                    Annotation::Named("OAuthFlowAuthorizationCode"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "OAuth2",
        base: "SecurityBase",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "type_",
                annotation: Annotation::Named("SecuritySchemeType"),
                default: DefaultValue::EnumMember("SecuritySchemeType", "oauth2"),
                alias: Some("type"),
            },
            FieldDefinition {
                name: "flows",
                annotation: Annotation::Named("OAuthFlows"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "OpenIdConnect",
        base: "SecurityBase",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "type_",
                annotation: Annotation::Named("SecuritySchemeType"),
                default: DefaultValue::EnumMember("SecuritySchemeType", "openIdConnect"),
                alias: Some("type"),
            },
            FieldDefinition {
                name: "openIdConnectUrl",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
        ],
    },
    GraphDefinition::Alias {
        name: "SecurityScheme",
        annotation: Annotation::Union(&[
            Annotation::Named("APIKey"),
            Annotation::Named("HTTPBase"),
            Annotation::Named("OAuth2"),
            Annotation::Named("OpenIdConnect"),
            Annotation::Named("HTTPBearer"),
        ]),
    },
    GraphDefinition::Model {
        name: "Components",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "schemas",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Schema"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "responses",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Response"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "parameters",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Parameter"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "examples",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Example"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "requestBodies",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("RequestBody"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "headers",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Header"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "securitySchemes",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("SecurityScheme"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "links",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("Link"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "callbacks",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Dict(
                                &Annotation::Named("str"),
                                &Annotation::Named("PathItem"),
                            ),
                            Annotation::Named("Reference"),
                            Annotation::Named("Any"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "pathItems",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("PathItem"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "Tag",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "name",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "description",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "externalDocs",
                annotation: Annotation::Union(&[
                    Annotation::Named("ExternalDocumentation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
    GraphDefinition::Model {
        name: "OpenAPI",
        base: "BaseModelWithConfig",
        extra_allow: false,
        fields: &[
            FieldDefinition {
                name: "openapi",
                annotation: Annotation::Named("str"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "info",
                annotation: Annotation::Named("Info"),
                default: DefaultValue::Required,
                alias: None,
            },
            FieldDefinition {
                name: "jsonSchemaDialect",
                annotation: Annotation::Union(&[
                    Annotation::Named("str"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "servers",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Named("Server")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "paths",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("PathItem"),
                            Annotation::Named("Any"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "webhooks",
                annotation: Annotation::Union(&[
                    Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::Union(&[
                            Annotation::Named("PathItem"),
                            Annotation::Named("Reference"),
                        ]),
                    ),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "components",
                annotation: Annotation::Union(&[
                    Annotation::Named("Components"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "security",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Dict(
                        &Annotation::Named("str"),
                        &Annotation::List(&Annotation::Named("str")),
                    )),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "tags",
                annotation: Annotation::Union(&[
                    Annotation::List(&Annotation::Named("Tag")),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
            FieldDefinition {
                name: "externalDocs",
                annotation: Annotation::Union(&[
                    Annotation::Named("ExternalDocumentation"),
                    Annotation::Named("NoneType"),
                ]),
                default: DefaultValue::None,
                alias: None,
            },
        ],
    },
];
