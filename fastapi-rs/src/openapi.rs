//! OpenAPI document assembly owned by the FastAPI compatibility layer.

use std::collections::BTreeMap;

use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyList};

/// One OpenAPI parameter extracted from a FastAPI operation.
pub(crate) struct OpenApiParameter {
    pub(crate) name: String,
    pub(crate) location: String,
    pub(crate) required: bool,
    pub(crate) schema: Py<PyAny>,
}

/// The OpenAPI-facing contract for one registered FastAPI operation.
pub(crate) struct OpenApiOperation {
    pub(crate) path: String,
    pub(crate) method: String,
    pub(crate) summary: String,
    pub(crate) operation_id: String,
    pub(crate) status: u16,
    pub(crate) parameters: Vec<OpenApiParameter>,
    pub(crate) request_model_name: Option<String>,
    pub(crate) request_schema: Option<Py<PyAny>>,
    pub(crate) request_required: bool,
    pub(crate) response_model_name: Option<String>,
    pub(crate) response_schema: Option<Py<PyAny>>,
    pub(crate) response_schema_title: String,
}

/// Assemble the first-slice FastAPI OpenAPI 3.1 document from Rust-owned
/// operation metadata and Pydantic JSON Schema values.
pub(crate) fn openapi_document(
    py: Python<'_>,
    title: &str,
    version: &str,
    operations: &[OpenApiOperation],
) -> PyResult<Py<PyAny>> {
    let mut schemas = BTreeMap::<String, Py<PyAny>>::new();
    for operation in operations {
        if let (Some(name), Some(schema)) = (
            operation.request_model_name.as_deref(),
            operation.request_schema.as_ref(),
        ) {
            collect_model_schema(py, &mut schemas, name, schema)?;
        }
        if let Some(schema) = operation.response_schema.as_ref() {
            if let Some(name) = operation.response_model_name.as_deref() {
                collect_model_schema(py, &mut schemas, name, schema)?;
            } else {
                collect_schema_definitions(py, &mut schemas, schema)?;
            }
        }
    }

    let paths = PyDict::new(py);
    for operation in operations {
        let path_item = match paths.get_item(&operation.path)? {
            Some(value) => value.cast_into::<PyDict>().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "OpenAPI path item must be a dictionary",
                )
            })?,
            None => {
                let value = PyDict::new(py);
                paths.set_item(&operation.path, &value)?;
                value
            }
        };

        let operation_document = PyDict::new(py);
        operation_document.set_item("summary", &operation.summary)?;
        operation_document.set_item("operationId", &operation.operation_id)?;

        if !operation.parameters.is_empty() {
            let parameters = PyList::empty(py);
            for parameter in &operation.parameters {
                let parameter_document = PyDict::new(py);
                parameter_document.set_item("name", &parameter.name)?;
                parameter_document.set_item("in", &parameter.location)?;
                parameter_document.set_item("required", parameter.required)?;
                let schema = normalize_schema(py, parameter.schema.bind(py), false)?;
                parameter_document.set_item("schema", schema)?;
                parameters.append(parameter_document)?;
            }
            operation_document.set_item("parameters", parameters)?;
        }

        if let Some(model_name) = operation.request_model_name.as_deref() {
            let request_body = PyDict::new(py);
            request_body.set_item("required", operation.request_required)?;
            let content = PyDict::new(py);
            let media_type = PyDict::new(py);
            let schema = reference_schema(py, model_name)?;
            media_type.set_item("schema", schema)?;
            content.set_item("application/json", media_type)?;
            request_body.set_item("content", content)?;
            operation_document.set_item("requestBody", request_body)?;
        }

        let responses = PyDict::new(py);
        let success_response = PyDict::new(py);
        success_response.set_item("description", "Successful Response")?;
        if body_allowed_for_status_code(operation.status) {
            let response_schema = match (
                operation.response_model_name.as_deref(),
                operation.response_schema.as_ref(),
            ) {
                (Some(model_name), Some(_)) => reference_schema(py, model_name)?.into_any(),
                (None, Some(schema)) => {
                    let schema = normalize_schema(py, schema.bind(py), false)?;
                    if let Ok(schema_dict) = schema.cast::<PyDict>() {
                        if schema_dict.get_item("$ref")?.is_none() {
                            schema_dict.set_item("title", &operation.response_schema_title)?;
                        }
                    }
                    schema
                }
                _ => PyDict::new(py).into_any(),
            };
            let content = PyDict::new(py);
            let media_type = PyDict::new(py);
            media_type.set_item("schema", response_schema)?;
            content.set_item("application/json", media_type)?;
            success_response.set_item("content", content)?;
        }
        let status_key = operation.status.to_string();
        responses.set_item(status_key, success_response)?;

        let needs_validation_response =
            !operation.parameters.is_empty() || operation.request_model_name.is_some();
        if needs_validation_response && operation.status != 422 {
            responses.set_item("422", validation_response(py)?)?;
            schemas
                .entry("HTTPValidationError".to_owned())
                .or_insert(http_validation_error_schema(py)?.unbind().into_any());
            schemas
                .entry("ValidationError".to_owned())
                .or_insert(validation_error_schema(py)?.unbind().into_any());
        }

        operation_document.set_item("responses", responses)?;
        path_item.set_item(operation.method.to_ascii_lowercase(), operation_document)?;
    }

    let document = PyDict::new(py);
    document.set_item("openapi", "3.1.0")?;
    let info = PyDict::new(py);
    info.set_item("title", title)?;
    info.set_item("version", version)?;
    document.set_item("info", info)?;
    document.set_item("paths", paths)?;

    let components = PyDict::new(py);
    let component_schemas = PyDict::new(py);
    for (name, schema) in schemas {
        component_schemas.set_item(name, schema.bind(py))?;
    }
    components.set_item("schemas", component_schemas)?;
    document.set_item("components", components)?;

    Ok(document.into_any().unbind())
}

const fn body_allowed_for_status_code(status_code: u16) -> bool {
    status_code >= 200 && !matches!(status_code, 204 | 205 | 304)
}

fn collect_model_schema(
    py: Python<'_>,
    schemas: &mut BTreeMap<String, Py<PyAny>>,
    name: &str,
    schema: &Py<PyAny>,
) -> PyResult<()> {
    collect_schema_definitions(py, schemas, schema)?;

    let normalized = normalize_schema(py, schema.bind(py), true)?;
    schemas
        .entry(name.to_owned())
        .or_insert(normalized.unbind().into_any());
    Ok(())
}

fn collect_schema_definitions(
    py: Python<'_>,
    schemas: &mut BTreeMap<String, Py<PyAny>>,
    schema: &Py<PyAny>,
) -> PyResult<()> {
    let schema = schema.bind(py);
    if let Ok(schema_dict) = schema.cast::<PyDict>() {
        if let Some(definitions) = schema_dict.get_item("$defs")? {
            if let Ok(definitions) = definitions.cast::<PyDict>() {
                for (definition_name, definition_schema) in definitions.iter() {
                    let definition_name: String = definition_name.extract()?;
                    let normalized = normalize_schema(py, &definition_schema, true)?;
                    schemas
                        .entry(definition_name)
                        .or_insert(normalized.unbind().into_any());
                }
            }
        }
    }
    Ok(())
}

fn normalize_schema<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
    top_level_model: bool,
) -> PyResult<Bound<'py, PyAny>> {
    if let Ok(source) = value.cast::<PyDict>() {
        let mut entries = Vec::<(String, Bound<'py, PyAny>)>::new();
        for (key, item) in source.iter() {
            let key: String = key.extract()?;
            // Pydantic's field defaults are excluded from FastAPI's OpenAPI schemas.
            if key == "default" || key == "$defs" {
                continue;
            }
            entries.push((key, item));
        }
        entries.sort_by_key(|(key, _)| schema_key_rank(key, top_level_model));

        let result = PyDict::new(py);
        for (key, item) in entries {
            if key == "$ref" {
                if let Ok(reference) = item.extract::<String>() {
                    let reference = reference.replace("#/$defs/", "#/components/schemas/");
                    result.set_item(key, reference)?;
                    continue;
                }
            }
            if key == "exclusiveMinimum" && !item.is_instance_of::<PyBool>() {
                if let Ok(number) = item.extract::<f64>() {
                    result.set_item(key, PyFloat::new(py, number))?;
                    continue;
                }
            }
            let item = normalize_schema_value(py, &key, &item)?;
            result.set_item(key, item)?;
        }
        return Ok(result.into_any());
    }

    Ok(value.clone())
}

fn normalize_schema_value<'py>(
    py: Python<'py>,
    key: &str,
    value: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    if matches!(key, "properties" | "patternProperties" | "dependentSchemas") {
        if let Ok(source) = value.cast::<PyDict>() {
            let result = PyDict::new(py);
            for (name, schema) in source.iter() {
                result.set_item(name, normalize_schema(py, &schema, false)?)?;
            }
            return Ok(result.into_any());
        }
    }

    if matches!(key, "anyOf" | "allOf" | "oneOf" | "prefixItems") {
        if let Ok(source) = value.cast::<PyList>() {
            let result = PyList::empty(py);
            for schema in source.iter() {
                result.append(normalize_schema(py, &schema, false)?)?;
            }
            return Ok(result.into_any());
        }
    }

    if matches!(
        key,
        "items"
            | "additionalProperties"
            | "not"
            | "contains"
            | "if"
            | "then"
            | "else"
            | "propertyNames"
            | "unevaluatedProperties"
            | "contentSchema"
    ) {
        if value.cast::<PyDict>().is_ok() {
            return normalize_schema(py, value, false);
        }
        if key == "items" {
            if let Ok(source) = value.cast::<PyList>() {
                let result = PyList::empty(py);
                for schema in source.iter() {
                    result.append(normalize_schema(py, &schema, false)?)?;
                }
                return Ok(result.into_any());
            }
        }
    }

    Ok(value.clone())
}

fn schema_key_rank(key: &str, top_level_model: bool) -> (usize, usize) {
    let model_order = ["$ref", "properties", "type", "required", "title"];
    let field_order = [
        "$ref",
        "anyOf",
        "oneOf",
        "allOf",
        "type",
        "format",
        "const",
        "enum",
        "minimum",
        "exclusiveMinimum",
        "maximum",
        "exclusiveMaximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "items",
        "properties",
        "additionalProperties",
        "required",
        "title",
        "description",
    ];
    let order = if top_level_model {
        &model_order[..]
    } else {
        &field_order[..]
    };
    order
        .iter()
        .position(|candidate| *candidate == key)
        .map_or((1, 0), |index| (0, index))
}

fn reference_schema<'py>(py: Python<'py>, model_name: &str) -> PyResult<Bound<'py, PyDict>> {
    let schema = PyDict::new(py);
    schema.set_item("$ref", format!("#/components/schemas/{model_name}"))?;
    Ok(schema)
}

fn validation_response(py: Python<'_>) -> PyResult<Bound<'_, PyDict>> {
    let response = PyDict::new(py);
    response.set_item("description", "Validation Error")?;
    let content = PyDict::new(py);
    let media_type = PyDict::new(py);
    media_type.set_item("schema", reference_schema(py, "HTTPValidationError")?)?;
    content.set_item("application/json", media_type)?;
    response.set_item("content", content)?;
    Ok(response)
}

fn http_validation_error_schema(py: Python<'_>) -> PyResult<Bound<'_, PyDict>> {
    let detail = PyDict::new(py);
    let item = PyDict::new(py);
    item.set_item("$ref", "#/components/schemas/ValidationError")?;
    detail.set_item("items", item)?;
    detail.set_item("type", "array")?;
    detail.set_item("title", "Detail")?;

    let properties = PyDict::new(py);
    properties.set_item("detail", detail)?;
    let schema = PyDict::new(py);
    schema.set_item("properties", properties)?;
    schema.set_item("type", "object")?;
    schema.set_item("title", "HTTPValidationError")?;
    Ok(schema)
}

fn validation_error_schema(py: Python<'_>) -> PyResult<Bound<'_, PyDict>> {
    let loc_union = PyList::empty(py);
    for kind in ["string", "integer"] {
        let variant = PyDict::new(py);
        variant.set_item("type", kind)?;
        loc_union.append(variant)?;
    }
    let loc_items = PyDict::new(py);
    loc_items.set_item("anyOf", loc_union)?;
    let loc = PyDict::new(py);
    loc.set_item("items", loc_items)?;
    loc.set_item("type", "array")?;
    loc.set_item("title", "Location")?;

    let msg = string_schema(py, "Message")?;
    let error_type = string_schema(py, "Error Type")?;
    let input = PyDict::new(py);
    input.set_item("title", "Input")?;
    let context = PyDict::new(py);
    context.set_item("type", "object")?;
    context.set_item("title", "Context")?;

    let properties = PyDict::new(py);
    properties.set_item("loc", loc)?;
    properties.set_item("msg", msg)?;
    properties.set_item("type", error_type)?;
    properties.set_item("input", input)?;
    properties.set_item("ctx", context)?;

    let required = PyList::empty(py);
    for field in ["loc", "msg", "type"] {
        required.append(field)?;
    }
    let schema = PyDict::new(py);
    schema.set_item("properties", properties)?;
    schema.set_item("type", "object")?;
    schema.set_item("required", required)?;
    schema.set_item("title", "ValidationError")?;
    Ok(schema)
}

fn string_schema<'py>(py: Python<'py>, title: &str) -> PyResult<Bound<'py, PyDict>> {
    let schema = PyDict::new(py);
    schema.set_item("type", "string")?;
    schema.set_item("title", title)?;
    Ok(schema)
}
