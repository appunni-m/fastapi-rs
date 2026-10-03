//! OpenAPI document assembly owned by the FastAPI compatibility layer.

use std::collections::BTreeMap;

use crate::encoding::{JsonableEncoderInput, JsonableEncoderOptions, jsonable_encoder};
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyList, PyString};

/// One OpenAPI parameter extracted from a FastAPI operation.
pub(crate) struct OpenApiParameter {
    pub(crate) name: String,
    pub(crate) location: String,
    pub(crate) required: bool,
    pub(crate) description: Option<String>,
    pub(crate) deprecated: bool,
    pub(crate) default: Option<Py<PyAny>>,
    pub(crate) schema: Py<PyAny>,
}

pub(crate) struct OpenApiAdditionalResponse {
    pub(crate) status: String,
    pub(crate) description: String,
    pub(crate) response_model_name: Option<String>,
    pub(crate) response_schema: Option<Py<PyAny>>,
}

/// The OpenAPI-facing contract for one registered FastAPI operation.
pub(crate) struct OpenApiOperation {
    pub(crate) path: String,
    pub(crate) method: String,
    pub(crate) summary: String,
    pub(crate) response_description: String,
    pub(crate) operation_id: String,
    pub(crate) deprecated: Option<bool>,
    pub(crate) tags: Option<Vec<String>>,
    /// The route's explicit status, kept separate from its response-class default.
    pub(crate) status: Option<u16>,
    /// The OpenAPI response key derived from an explicit status or response-class default.
    pub(crate) response_status_key: Option<String>,
    pub(crate) parameters: Vec<OpenApiParameter>,
    pub(crate) security_schemes: BTreeMap<String, Py<PyAny>>,
    pub(crate) security_requirements: Vec<(String, Vec<String>)>,
    pub(crate) validation_parameters_present: bool,
    pub(crate) request_model_name: Option<String>,
    pub(crate) request_schema: Option<Py<PyAny>>,
    pub(crate) request_required: bool,
    pub(crate) request_body_present: bool,
    pub(crate) request_body_content_before_required: bool,
    pub(crate) request_media_type: String,
    pub(crate) response_model_name: Option<String>,
    pub(crate) response_schema: Option<Py<PyAny>>,
    pub(crate) response_schema_title: String,
    pub(crate) response_media_type: Option<String>,
    pub(crate) response_class_is_json: bool,
    pub(crate) jsonl_stream: bool,
    pub(crate) sse_stream: bool,
    pub(crate) stream_item_model_name: Option<String>,
    pub(crate) stream_item_schema: Option<Py<PyAny>>,
    pub(crate) additional_responses: Vec<OpenApiAdditionalResponse>,
}

/// OpenAPI info supplied by the FastAPI application constructor.
pub(crate) struct OpenApiInfo<'a> {
    pub(crate) title: &'a str,
    pub(crate) summary: Option<&'a str>,
    pub(crate) description: &'a str,
    pub(crate) terms_of_service: Option<&'a str>,
    pub(crate) contact: Option<&'a Py<PyAny>>,
    pub(crate) license_info: Option<&'a Py<PyAny>>,
    pub(crate) openapi_external_docs: Option<&'a Py<PyAny>>,
    pub(crate) version: &'a str,
}

/// Assemble the first-slice FastAPI OpenAPI 3.1 document from Rust-owned
/// operation metadata and Pydantic JSON Schema values.
pub(crate) fn openapi_document(
    py: Python<'_>,
    app_info: OpenApiInfo<'_>,
    operations: &[OpenApiOperation],
    root_path: Option<&str>,
) -> PyResult<Py<PyAny>> {
    let mut schemas = BTreeMap::<String, Py<PyAny>>::new();
    let mut security_schemes = BTreeMap::<String, Py<PyAny>>::new();
    for operation in operations {
        for (name, scheme) in &operation.security_schemes {
            security_schemes.insert(name.clone(), scheme.clone_ref(py));
        }
        for parameter in &operation.parameters {
            collect_schema_definitions(py, &mut schemas, &parameter.schema, false)?;
        }
        if operation.request_body_present {
            if let Some(schema) = operation.request_schema.as_ref() {
                if let Some(name) = operation.request_model_name.as_deref() {
                    collect_model_schema(py, &mut schemas, name, schema, true)?;
                } else {
                    collect_schema_definitions(py, &mut schemas, schema, true)?;
                }
            }
        }
        if let Some(schema) = operation.response_schema.as_ref() {
            if let Some(name) = operation.response_model_name.as_deref() {
                collect_model_schema(py, &mut schemas, name, schema, true)?;
            } else {
                collect_schema_definitions(py, &mut schemas, schema, true)?;
            }
        }
        for response in &operation.additional_responses {
            if let Some(schema) = response.response_schema.as_ref() {
                if let Some(name) = response.response_model_name.as_deref() {
                    collect_model_schema(py, &mut schemas, name, schema, true)?;
                } else {
                    collect_schema_definitions(py, &mut schemas, schema, true)?;
                }
            }
        }
        if let Some(schema) = operation.stream_item_schema.as_ref() {
            if let Some(name) = operation.stream_item_model_name.as_deref() {
                collect_model_schema(py, &mut schemas, name, schema, true)?;
            } else {
                collect_schema_definitions(py, &mut schemas, schema, true)?;
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
        if let Some(tags) = operation.tags.as_ref().filter(|tags| !tags.is_empty()) {
            let tag_values = PyList::empty(py);
            for tag in tags {
                tag_values.append(tag)?;
            }
            operation_document.set_item("tags", tag_values)?;
        }
        operation_document.set_item("summary", &operation.summary)?;
        operation_document.set_item("operationId", &operation.operation_id)?;
        if operation.deprecated == Some(true) {
            operation_document.set_item("deprecated", true)?;
        }

        if !operation.parameters.is_empty() {
            let parameters = PyList::empty(py);
            for parameter in &operation.parameters {
                let parameter_document = PyDict::new(py);
                parameter_document.set_item("name", &parameter.name)?;
                parameter_document.set_item("in", &parameter.location)?;
                parameter_document.set_item("required", parameter.required)?;
                if let Some(description) = parameter.description.as_deref() {
                    parameter_document.set_item("description", description)?;
                }
                if parameter.deprecated {
                    parameter_document.set_item("deprecated", true)?;
                }
                let mut schema = normalize_schema(py, parameter.schema.bind(py), false, false)?;
                if let Some(default) = parameter.default.as_ref() {
                    if let Ok(schema) = schema.cast::<PyDict>() {
                        schema.set_item("default", default.bind(py))?;
                    } else {
                        let wrapped_schema = PyDict::new(py);
                        let all_of = PyList::empty(py);
                        all_of.append(&schema)?;
                        wrapped_schema.set_item("allOf", all_of)?;
                        wrapped_schema.set_item("default", default.bind(py))?;
                        schema = wrapped_schema.into_any();
                    }
                }
                parameter_document.set_item("schema", schema)?;
                parameters.append(parameter_document)?;
            }
            operation_document.set_item("parameters", parameters)?;
        }
        if !operation.security_requirements.is_empty() {
            let security = PyList::empty(py);
            for (scheme_name, scopes) in &operation.security_requirements {
                let requirement = PyDict::new(py);
                let required_scopes = PyList::empty(py);
                for scope in scopes {
                    required_scopes.append(scope)?;
                }
                requirement.set_item(scheme_name, required_scopes)?;
                security.append(requirement)?;
            }
            operation_document.set_item("security", security)?;
        }

        if operation.request_body_present {
            let request_body = PyDict::new(py);
            if operation.request_required && !operation.request_body_content_before_required {
                request_body.set_item("required", true)?;
            }
            let content = PyDict::new(py);
            let media_type = PyDict::new(py);
            let schema = match (
                operation.request_model_name.as_deref(),
                operation.request_schema.as_ref(),
            ) {
                (Some(model_name), Some(_)) => reference_schema(py, model_name)?.into_any(),
                (None, Some(schema)) => normalize_schema(py, schema.bind(py), false, true)?,
                _ => PyDict::new(py).into_any(),
            };
            media_type.set_item("schema", schema)?;
            content.set_item(&operation.request_media_type, media_type)?;
            request_body.set_item("content", content)?;
            if operation.request_required && operation.request_body_content_before_required {
                request_body.set_item("required", true)?;
            }
            operation_document.set_item("requestBody", request_body)?;
        }

        let responses = PyDict::new(py);
        let success_response = PyDict::new(py);
        success_response.set_item("description", &operation.response_description)?;
        if body_allowed_for_status_code(operation.status) {
            if operation.jsonl_stream {
                let item_schema = match (
                    operation.stream_item_model_name.as_deref(),
                    operation.stream_item_schema.as_ref(),
                ) {
                    (Some(model_name), Some(_)) => reference_schema(py, model_name)?.into_any(),
                    (None, Some(schema)) => normalize_schema(py, schema.bind(py), false, true)?,
                    _ => PyDict::new(py).into_any(),
                };
                let media_type = PyDict::new(py);
                media_type.set_item("itemSchema", item_schema)?;
                let content = PyDict::new(py);
                content.set_item("application/jsonl", media_type)?;
                success_response.set_item("content", content)?;
            } else if operation.sse_stream {
                let properties = PyDict::new(py);
                let data_schema = PyDict::new(py);
                data_schema.set_item("type", "string")?;
                properties.set_item("data", &data_schema)?;
                let event_schema = PyDict::new(py);
                event_schema.set_item("type", "string")?;
                properties.set_item("event", event_schema)?;
                let id_schema = PyDict::new(py);
                id_schema.set_item("type", "string")?;
                properties.set_item("id", id_schema)?;
                let retry_schema = PyDict::new(py);
                retry_schema.set_item("type", "integer")?;
                retry_schema.set_item("minimum", 0)?;
                properties.set_item("retry", retry_schema)?;

                let item_schema = PyDict::new(py);
                item_schema.set_item("type", "object")?;
                item_schema.set_item("properties", &properties)?;
                if let Some(schema) = operation.stream_item_schema.as_ref() {
                    data_schema.set_item("contentMediaType", "application/json")?;
                    if let Some(model_name) = operation.stream_item_model_name.as_deref() {
                        data_schema.set_item("contentSchema", reference_schema(py, model_name)?)?;
                    } else {
                        data_schema.set_item(
                            "contentSchema",
                            normalize_schema(py, schema.bind(py), false, true)?,
                        )?;
                    }
                    let required = PyList::empty(py);
                    required.append("data")?;
                    item_schema.set_item("required", required)?;
                }
                let media_type = PyDict::new(py);
                media_type.set_item("itemSchema", item_schema)?;
                let content = PyDict::new(py);
                content.set_item("text/event-stream", media_type)?;
                success_response.set_item("content", content)?;
            } else {
                if let Some(response_media_type) = operation.response_media_type.as_deref() {
                    let response_schema = if operation.response_class_is_json {
                        match (
                            operation.response_model_name.as_deref(),
                            operation.response_schema.as_ref(),
                        ) {
                            (Some(model_name), Some(_)) => {
                                reference_schema(py, model_name)?.into_any()
                            }
                            (None, Some(schema)) => {
                                let schema = normalize_schema(py, schema.bind(py), false, true)?;
                                if let Ok(schema_dict) = schema.cast::<PyDict>() {
                                    if schema_dict.get_item("$ref")?.is_none() {
                                        schema_dict
                                            .set_item("title", &operation.response_schema_title)?;
                                    }
                                }
                                schema
                            }
                            _ => PyDict::new(py).into_any(),
                        }
                    } else {
                        let schema = PyDict::new(py);
                        schema.set_item("type", "string")?;
                        schema.into_any()
                    };
                    let content = PyDict::new(py);
                    let media_type = PyDict::new(py);
                    media_type.set_item("schema", response_schema)?;
                    content.set_item(response_media_type, media_type)?;
                    success_response.set_item("content", content)?;
                }
            }
        }
        if let Some(status_key) = operation.response_status_key.as_deref() {
            responses.set_item(status_key, success_response)?;
        } else {
            responses.set_item(py.None(), success_response)?;
        }

        let needs_validation_response =
            operation.validation_parameters_present || operation.request_body_present;
        if needs_validation_response && operation.status != Some(422) {
            responses.set_item("422", validation_response(py)?)?;
            schemas
                .entry("HTTPValidationError".to_owned())
                .or_insert(http_validation_error_schema(py)?.unbind().into_any());
            schemas
                .entry("ValidationError".to_owned())
                .or_insert(validation_error_schema(py)?.unbind().into_any());
        }

        for additional_response in &operation.additional_responses {
            let response = match responses.get_item(&additional_response.status)? {
                Some(existing) => existing.cast_into::<PyDict>().map_err(|_| {
                    PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                        "OpenAPI response must be a dictionary",
                    )
                })?,
                None => {
                    let response = PyDict::new(py);
                    responses.set_item(&additional_response.status, &response)?;
                    response
                }
            };
            response.set_item("description", &additional_response.description)?;
            if let Some(schema) = additional_response.response_schema.as_ref() {
                let content = match response.get_item("content")? {
                    Some(content) => content.cast_into::<PyDict>().map_err(|_| {
                        PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                            "OpenAPI response content must be a dictionary",
                        )
                    })?,
                    None => {
                        let content = PyDict::new(py);
                        response.set_item("content", &content)?;
                        content
                    }
                };
                let media_type = operation
                    .response_media_type
                    .as_deref()
                    .unwrap_or("application/json");
                let media = match content.get_item(media_type)? {
                    Some(media) => media.cast_into::<PyDict>().map_err(|_| {
                        PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                            "OpenAPI media type entry must be a dictionary",
                        )
                    })?,
                    None => {
                        let media = PyDict::new(py);
                        content.set_item(media_type, &media)?;
                        media
                    }
                };
                let schema = match additional_response.response_model_name.as_deref() {
                    Some(model_name) => reference_schema(py, model_name)?.into_any(),
                    None => normalize_schema(py, schema.bind(py), false, true)?,
                };
                if additional_response.response_model_name.is_none() {
                    if let Ok(schema_dict) = schema.cast::<PyDict>() {
                        if schema_dict.get_item("$ref")?.is_none() {
                            let alias = format!(
                                "Response_{}_{}",
                                additional_response.status, operation.operation_id
                            );
                            let title = PyString::new(py, &alias)
                                .call_method0("title")?
                                .extract::<String>()?;
                            schema_dict.set_item("title", title.replace('_', " "))?;
                        }
                    }
                }
                media.set_item("schema", schema)?;
            }
        }

        operation_document.set_item("responses", responses)?;
        path_item.set_item(operation.method.to_ascii_lowercase(), operation_document)?;
    }

    let document = PyDict::new(py);
    document.set_item("openapi", "3.1.0")?;
    let info = PyDict::new(py);
    info.set_item("title", app_info.title)?;
    if let Some(summary) = app_info.summary.filter(|summary| !summary.is_empty()) {
        info.set_item("summary", summary)?;
    }
    if !app_info.description.is_empty() {
        info.set_item("description", app_info.description)?;
    }
    if let Some(terms_of_service) = app_info.terms_of_service.filter(|value| !value.is_empty()) {
        info.set_item("termsOfService", terms_of_service)?;
    }
    if let Some(contact) = app_info.contact {
        let contact = contact.bind(py);
        if contact.is_truthy()? {
            info.set_item("contact", contact)?;
        }
    }
    if let Some(license_info) = app_info.license_info {
        let license_info = license_info.bind(py);
        if license_info.is_truthy()? {
            info.set_item("license", license_info)?;
        }
    }
    info.set_item("version", app_info.version)?;
    document.set_item("info", info)?;
    document.set_item("paths", paths)?;
    if let Some(root_path) = root_path.filter(|path| !path.is_empty()) {
        let server = PyDict::new(py);
        server.set_item("url", root_path)?;
        let servers = PyList::empty(py);
        servers.append(server)?;
        document.set_item("servers", servers)?;
    }
    if let Some(external_docs) = app_info.openapi_external_docs {
        let external_docs = external_docs.bind(py);
        if external_docs.is_truthy()? {
            document.set_item("externalDocs", external_docs)?;
        }
    }

    if !schemas.is_empty() || !security_schemes.is_empty() {
        let components = PyDict::new(py);
        if !schemas.is_empty() {
            let component_schemas = PyDict::new(py);
            for (name, schema) in schemas {
                component_schemas.set_item(name, schema.bind(py))?;
            }
            components.set_item("schemas", component_schemas)?;
        }
        if !security_schemes.is_empty() {
            let definitions = PyDict::new(py);
            for (name, scheme) in security_schemes {
                definitions.set_item(name, scheme.bind(py))?;
            }
            components.set_item("securitySchemes", definitions)?;
        }
        document.set_item("components", components)?;
    }

    let document = document.into_any();
    let encoder_options = JsonableEncoderOptions::new(JsonableEncoderInput {
        include: None,
        exclude: None,
        by_alias: true,
        exclude_unset: false,
        exclude_defaults: false,
        exclude_none: true,
        custom_encoder: None,
        sqlalchemy_safe: true,
    });
    jsonable_encoder(py, &document, &encoder_options).map(Bound::unbind)
}

const fn body_allowed_for_status_code(status_code: Option<u16>) -> bool {
    match status_code {
        None => true,
        Some(status_code) => status_code >= 200 && !matches!(status_code, 204 | 205 | 304),
    }
}

fn collect_model_schema(
    py: Python<'_>,
    schemas: &mut BTreeMap<String, Py<PyAny>>,
    name: &str,
    schema: &Py<PyAny>,
    preserve_defaults: bool,
) -> PyResult<()> {
    collect_schema_definitions(py, schemas, schema, preserve_defaults)?;

    if let Ok(schema) = schema.bind(py).cast::<PyDict>() {
        if let Some(reference) = schema.get_item("$ref")? {
            let reference = reference.extract::<String>()?;
            if reference == format!("#/components/schemas/{name}") {
                return Ok(());
            }
        }
    }

    let normalized = normalize_schema(py, schema.bind(py), true, preserve_defaults)?;
    schemas
        .entry(name.to_owned())
        .or_insert(normalized.unbind().into_any());
    Ok(())
}

fn collect_schema_definitions(
    py: Python<'_>,
    schemas: &mut BTreeMap<String, Py<PyAny>>,
    schema: &Py<PyAny>,
    preserve_defaults: bool,
) -> PyResult<()> {
    let schema = schema.bind(py);
    if let Ok(schema_dict) = schema.cast::<PyDict>() {
        if let Some(definitions) = schema_dict.get_item("$defs")? {
            if let Ok(definitions) = definitions.cast::<PyDict>() {
                for (definition_name, definition_schema) in definitions.iter() {
                    let definition_name: String = definition_name.extract()?;
                    let normalized =
                        normalize_schema(py, &definition_schema, true, preserve_defaults)?;
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
    preserve_defaults: bool,
) -> PyResult<Bound<'py, PyAny>> {
    if let Ok(source) = value.cast::<PyDict>() {
        let schema_type = source
            .get_item("type")?
            .and_then(|item| item.extract::<String>().ok());
        let schema_format = source
            .get_item("format")?
            .and_then(|item| item.extract::<String>().ok());
        let fastapi_binary_bytes_schema = schema_type.as_deref() == Some("string")
            && schema_format.as_deref() == Some("binary")
            && source.get_item("contentMediaType")?.is_none();
        let mut entries = Vec::<(String, Bound<'py, PyAny>)>::new();
        for (key, item) in source.iter() {
            let key: String = key.extract()?;
            if key == "$defs"
                || (!preserve_defaults && key == "default")
                || (fastapi_binary_bytes_schema && key == "format")
            {
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
            let item = normalize_schema_value(py, &key, &item, preserve_defaults)?;
            result.set_item(&key, item)?;
            if key == "type" && fastapi_binary_bytes_schema {
                result.set_item("contentMediaType", "application/octet-stream")?;
            }
        }
        return Ok(result.into_any());
    }

    Ok(value.clone())
}

fn normalize_schema_value<'py>(
    py: Python<'py>,
    key: &str,
    value: &Bound<'py, PyAny>,
    preserve_defaults: bool,
) -> PyResult<Bound<'py, PyAny>> {
    if matches!(key, "properties" | "patternProperties" | "dependentSchemas") {
        if let Ok(source) = value.cast::<PyDict>() {
            let result = PyDict::new(py);
            for (name, schema) in source.iter() {
                result.set_item(
                    name,
                    normalize_schema(py, &schema, false, preserve_defaults)?,
                )?;
            }
            return Ok(result.into_any());
        }
    }

    if matches!(key, "anyOf" | "allOf" | "oneOf" | "prefixItems") {
        if let Ok(source) = value.cast::<PyList>() {
            let result = PyList::empty(py);
            for schema in source.iter() {
                result.append(normalize_schema(py, &schema, false, preserve_defaults)?)?;
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
            return normalize_schema(py, value, false, preserve_defaults);
        }
        if key == "items" {
            if let Ok(source) = value.cast::<PyList>() {
                let result = PyList::empty(py);
                for schema in source.iter() {
                    result.append(normalize_schema(py, &schema, false, preserve_defaults)?)?;
                }
                return Ok(result.into_any());
            }
        }
    }

    Ok(value.clone())
}

fn schema_key_rank(key: &str, top_level_model: bool) -> (usize, usize) {
    let model_order = [
        "$ref",
        "properties",
        "additionalProperties",
        "type",
        "contentMediaType",
        "required",
        "title",
    ];
    let field_order = [
        "$ref",
        "anyOf",
        "oneOf",
        "allOf",
        "items",
        "type",
        "additionalProperties",
        "contentMediaType",
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
