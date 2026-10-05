//! OpenAPI document assembly owned by the FastAPI compatibility layer.

use std::collections::BTreeMap;

use crate::encoding::{JsonableEncoderInput, JsonableEncoderOptions, jsonable_encoder};
use pyo3::exceptions::{PyKeyError, PyNotImplementedError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyList, PyModule, PyString, PyTuple};

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
    pub(crate) security_schemes: Vec<(String, Py<PyAny>)>,
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
    pub(crate) response_schema_title: Option<String>,
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
    pub(crate) openapi_version: &'a str,
    pub(crate) tags: Option<&'a Py<PyAny>>,
    pub(crate) title: &'a str,
    pub(crate) summary: Option<&'a str>,
    pub(crate) description: &'a str,
    pub(crate) terms_of_service: Option<&'a str>,
    pub(crate) contact: Option<&'a Py<PyAny>>,
    pub(crate) license_info: Option<&'a Py<PyAny>>,
    pub(crate) openapi_external_docs: Option<&'a Py<PyAny>>,
    pub(crate) servers: Option<&'a Py<PyAny>>,
    pub(crate) version: &'a str,
}

fn deduplicate_operation_parameters<'py>(
    parameters: &Bound<'py, PyList>,
) -> PyResult<Bound<'py, PyList>> {
    let py = parameters.py();
    let parameter_key = |parameter: &Bound<'py, PyDict>| -> PyResult<Bound<'py, PyTuple>> {
        PyTuple::new(
            py,
            [
                parameter
                    .get_item("in")?
                    .ok_or_else(|| PyKeyError::new_err("in"))?,
                parameter
                    .get_item("name")?
                    .ok_or_else(|| PyKeyError::new_err("name"))?,
            ],
        )
    };
    let all_parameters = PyDict::new(py);
    for parameter in parameters.iter() {
        let parameter = parameter.cast::<PyDict>()?;
        all_parameters.set_item(parameter_key(parameter)?, parameter)?;
    }
    let required_parameters = PyDict::new(py);
    for parameter in parameters.iter() {
        let parameter = parameter.cast::<PyDict>()?;
        let Some(required) = parameter.get_item("required")? else {
            continue;
        };
        if required.is_truthy()? {
            required_parameters.set_item(parameter_key(parameter)?, parameter)?;
        }
    }
    // Replacing values preserves the first (in, name) position while the last
    // required definition takes precedence over the last overall definition.
    for (key, parameter) in required_parameters.iter() {
        all_parameters.set_item(key, parameter)?;
    }
    PyList::new(py, all_parameters.iter().map(|(_, parameter)| parameter))
}

/// Assemble the first-slice FastAPI OpenAPI 3.1 document from Rust-owned
/// operation metadata and Pydantic JSON Schema values.
pub(crate) fn openapi_document(
    py: Python<'_>,
    app_info: OpenApiInfo<'_>,
    operations: &[OpenApiOperation],
    root_path: Option<&str>,
    shared_definitions: Option<&Py<PyDict>>,
) -> PyResult<Py<PyAny>> {
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
    let mut schemas = BTreeMap::<String, Py<PyAny>>::new();
    if let Some(definitions) = shared_definitions {
        for (name, schema) in definitions.bind(py).iter() {
            schemas.insert(
                name.extract::<String>()?,
                normalize_schema(py, &schema, true)?.unbind(),
            );
        }
    }
    let mut security_schemes = Vec::new();
    for operation in operations {
        for (name, scheme) in &operation.security_schemes {
            // Source encodes each operation's scheme before insertion/dedup.
            // The private graph receives the ordinary definition dictionary.
            let definition = jsonable_encoder(py, scheme.bind(py), &encoder_options)?;
            register_security_scheme(&mut security_schemes, name.clone(), definition.unbind());
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
                let mut schema = normalize_schema(py, parameter.schema.bind(py), false)?;
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
            operation_document
                .set_item("parameters", deduplicate_operation_parameters(&parameters)?)?;
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
                (None, Some(schema)) => normalize_schema(py, schema.bind(py), true)?,
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
                    (None, Some(schema)) => normalize_schema(py, schema.bind(py), true)?,
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
                            normalize_schema(py, schema.bind(py), true)?,
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
                                let schema = normalize_schema(py, schema.bind(py), true)?;
                                if let Ok(schema_dict) = schema.cast::<PyDict>() {
                                    if let Some(title) = operation.response_schema_title.as_deref()
                                    {
                                        if schema_dict.get_item("$ref")?.is_none() {
                                            schema_dict.set_item("title", title)?;
                                        }
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
                    None => normalize_schema(py, schema.bind(py), true)?,
                };
                media.set_item("schema", schema)?;
            }
        }

        operation_document.set_item("responses", responses)?;
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
        path_item.set_item(operation.method.to_ascii_lowercase(), operation_document)?;
    }

    let document = PyDict::new(py);
    document.set_item("openapi", app_info.openapi_version)?;
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
    let configured_servers = match app_info.servers.map(|servers| servers.bind(py)) {
        Some(servers) if servers.is_truthy()? => Some(servers),
        _ => None,
    };
    if let Some(root_path) = root_path.filter(|path| !path.is_empty()) {
        let server = PyDict::new(py);
        server.set_item("url", root_path)?;
        let servers = PyList::empty(py);
        servers.append(server)?;
        if let Some(configured_servers) = configured_servers.as_ref() {
            for configured_server in configured_servers.try_iter()? {
                servers.append(configured_server?)?;
            }
        }
        document.set_item("servers", servers)?;
    } else if let Some(servers) = configured_servers {
        document.set_item("servers", servers)?;
    }
    document.set_item("paths", paths)?;
    if let Some(tags) = app_info.tags {
        let tags = tags.bind(py);
        if tags.is_truthy()? {
            document.set_item("tags", tags)?;
        }
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

    // FastAPI finalizes the complete graph through OpenAPI(**output). Let
    // Pydantic choose model/Any union branches before the existing encoder.
    let document = crate::openapi_models::finalize_document(py, &document)?;
    jsonable_encoder(py, &document, &encoder_options).map(Bound::unbind)
}

#[pyclass(name = "_GetOpenApiCallable", module = "fastapi.openapi.utils", dict)]
struct GetOpenApiCallable;

#[pymethods]
impl GetOpenApiCallable {
    #[new]
    fn new() -> Self {
        Self
    }

    #[pyo3(signature = (*, title, version, openapi_version="3.1.0", summary=None, description=None, routes, webhooks=None, tags=None, servers=None, terms_of_service=None, contact=None, license_info=None, separate_input_output_schemas=true, external_docs=None))]
    // lint-exception: The public FastAPI signature has fourteen ordered keyword-only parameters.
    #[allow(
        clippy::too_many_arguments,
        reason = "Preserve FastAPI's reviewed 14-parameter public get_openapi signature"
    )]
    fn __call__(
        &self,
        py: Python<'_>,
        title: &str,
        version: &str,
        openapi_version: &str,
        summary: Option<&str>,
        description: Option<&str>,
        routes: &Bound<'_, PyAny>,
        webhooks: Option<Bound<'_, PyAny>>,
        tags: Option<Bound<'_, PyAny>>,
        servers: Option<Bound<'_, PyAny>>,
        terms_of_service: Option<&str>,
        contact: Option<Bound<'_, PyAny>>,
        license_info: Option<Bound<'_, PyAny>>,
        separate_input_output_schemas: bool,
        external_docs: Option<Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let _ = separate_input_output_schemas;
        let route_count = routes.len()?;
        if route_count > 1
            || webhooks
                .as_ref()
                .map(|items| items.len())
                .transpose()?
                .is_some_and(|length| length != 0)
        {
            return Err(PyNotImplementedError::new_err(
                "FastAPI-RS get_openapi supports empty routes or one native simple GET APIRoute; webhooks are unsupported",
            ));
        }
        let operations = if route_count == 1 {
            vec![crate::application_runtime::direct_route_openapi_operation(
                &routes.get_item(0)?,
            )?]
        } else {
            Vec::new()
        };

        let contact = contact.map(Bound::unbind);
        let license_info = license_info.map(Bound::unbind);
        let servers = servers.map(Bound::unbind);
        let external_docs = external_docs.map(Bound::unbind);
        let tags = tags.map(Bound::unbind);
        openapi_document(
            py,
            OpenApiInfo {
                openapi_version,
                tags: tags.as_ref(),
                title,
                summary,
                description: description.unwrap_or_default(),
                terms_of_service,
                contact: contact.as_ref(),
                license_info: license_info.as_ref(),
                openapi_external_docs: external_docs.as_ref(),
                servers: servers.as_ref(),
                version,
            },
            &operations,
            None,
            None,
        )
    }
}

fn install_get_openapi_annotations(
    py: Python<'_>,
    module: &Bound<'_, PyModule>,
    callable: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let annotations = PyDict::new(py);
    let string_type = py.get_type::<PyString>().into_any();
    let bool_type = py.get_type::<PyBool>().into_any();
    let none_type = py.None().bind(py).get_type().into_any();
    let any_type = py.import("typing")?.getattr("Any")?;
    let builtins = py.import("builtins")?;
    let dict_type = builtins.getattr("dict")?;
    let list_type = builtins.getattr("list")?;
    let operator = py.import("operator")?;
    let union = operator.getattr("or_")?;
    let optional_string = union.call1((string_type.as_any(), none_type.as_any()))?;
    let string_any = union.call1((string_type.as_any(), any_type.as_any()))?;
    let string_any_dict =
        dict_type.get_item(PyTuple::new(py, [string_type.as_any(), any_type.as_any()])?)?;
    let string_or_any_dict = dict_type.get_item(PyTuple::new(
        py,
        [string_type.as_any(), string_any.as_any()],
    )?)?;
    let optional_string_or_any_dict =
        union.call1((string_or_any_dict.as_any(), none_type.as_any()))?;
    let tags = list_type.get_item(string_any_dict.clone())?;
    let optional_tags = union.call1((tags, none_type.as_any()))?;
    let servers = list_type.get_item(string_or_any_dict)?;
    let optional_servers = union.call1((servers, none_type.as_any()))?;
    let routes_type = py.import("collections.abc")?.getattr("Sequence")?;
    let base_route = py.import("starlette.routing")?.getattr("BaseRoute")?;
    let route_context = module.getattr("RouteContext")?;
    let route_type = union.call1((base_route, route_context))?;
    let routes = routes_type.get_item(route_type)?;
    let optional_routes = union.call1((routes.clone(), none_type.as_any()))?;
    let optional_external_docs = union.call1((string_any_dict, none_type.as_any()))?;
    annotations.set_item("title", string_type.clone())?;
    annotations.set_item("version", string_type.clone())?;
    annotations.set_item("openapi_version", string_type)?;
    annotations.set_item("summary", optional_string.clone())?;
    annotations.set_item("description", optional_string.clone())?;
    annotations.set_item("routes", routes)?;
    annotations.set_item("webhooks", optional_routes)?;
    annotations.set_item("tags", optional_tags)?;
    annotations.set_item("servers", optional_servers)?;
    annotations.set_item("terms_of_service", optional_string)?;
    annotations.set_item("contact", optional_string_or_any_dict.clone())?;
    annotations.set_item("license_info", optional_string_or_any_dict)?;
    annotations.set_item("separate_input_output_schemas", bool_type)?;
    annotations.set_item("external_docs", optional_external_docs)?;
    annotations.set_item(
        "return",
        dict_type.get_item(PyTuple::new(
            py,
            [py.get_type::<PyString>().as_any(), any_type.as_any()],
        )?)?,
    )?;
    callable.setattr("__annotations__", &annotations)?;
    callable.setattr("__module__", "fastapi.openapi.utils")?;
    callable.setattr("__name__", "get_openapi")?;
    callable.setattr("__qualname__", "get_openapi")?;

    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let keyword_only = parameter_type.getattr("KEYWORD_ONLY")?;
    let empty = parameter_type.getattr("empty")?;
    enum DefaultValue {
        Required,
        None,
        String(&'static str),
        True,
    }
    let parameters = PyList::empty(py);
    for (name, default) in [
        ("title", DefaultValue::Required),
        ("version", DefaultValue::Required),
        ("openapi_version", DefaultValue::String("3.1.0")),
        ("summary", DefaultValue::None),
        ("description", DefaultValue::None),
        ("routes", DefaultValue::Required),
        ("webhooks", DefaultValue::None),
        ("tags", DefaultValue::None),
        ("servers", DefaultValue::None),
        ("terms_of_service", DefaultValue::None),
        ("contact", DefaultValue::None),
        ("license_info", DefaultValue::None),
        ("separate_input_output_schemas", DefaultValue::True),
        ("external_docs", DefaultValue::None),
    ] {
        let parameter_kwargs = PyDict::new(py);
        parameter_kwargs.set_item("kind", &keyword_only)?;
        parameter_kwargs.set_item("annotation", annotation(&annotations, name)?)?;
        match default {
            DefaultValue::Required => parameter_kwargs.set_item("default", &empty)?,
            DefaultValue::None => parameter_kwargs.set_item("default", py.None())?,
            DefaultValue::String(default) => parameter_kwargs.set_item("default", default)?,
            DefaultValue::True => parameter_kwargs.set_item("default", true)?,
        }
        parameters.append(parameter_type.call((name,), Some(&parameter_kwargs))?)?;
    }
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", annotation(&annotations, "return")?)?;
    callable.setattr(
        "__signature__",
        inspect
            .getattr("Signature")?
            .call((parameters,), Some(&signature_kwargs))?,
    )?;
    Ok(())
}

fn annotation<'py>(annotations: &Bound<'py, PyDict>, name: &str) -> PyResult<Bound<'py, PyAny>> {
    annotations
        .get_item(name)?
        .ok_or_else(|| PyValueError::new_err(format!("missing get_openapi annotation {name}")))
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<GetOpenApiCallable>()?;
    let callable = module.getattr("_GetOpenApiCallable")?.call0()?;
    install_get_openapi_annotations(module.py(), module, &callable)?;
    module.add("get_openapi", callable)?;
    Ok(())
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

    let normalized = normalize_schema(py, schema.bind(py), preserve_defaults)?;
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
                    let normalized = normalize_schema(py, &definition_schema, preserve_defaults)?;
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
        entries.sort_by_key(|(key, _)| schema_key_rank(key));

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
                result.set_item(name, normalize_schema(py, &schema, preserve_defaults)?)?;
            }
            return Ok(result.into_any());
        }
    }

    if matches!(key, "anyOf" | "allOf" | "oneOf" | "prefixItems") {
        if let Ok(source) = value.cast::<PyList>() {
            let result = PyList::empty(py);
            for schema in source.iter() {
                result.append(normalize_schema(py, &schema, preserve_defaults)?)?;
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
            return normalize_schema(py, value, preserve_defaults);
        }
        if key == "items" {
            if let Ok(source) = value.cast::<PyList>() {
                let result = PyList::empty(py);
                for schema in source.iter() {
                    result.append(normalize_schema(py, &schema, preserve_defaults)?)?;
                }
                return Ok(result.into_any());
            }
        }
    }

    Ok(value.clone())
}

const SCHEMA_WIRE_FIELD_ORDER: &[&str] = &[
    "$schema",
    "$vocabulary",
    "$id",
    "$anchor",
    "$dynamicAnchor",
    "$ref",
    "$dynamicRef",
    "$defs",
    "$comment",
    "allOf",
    "anyOf",
    "oneOf",
    "not",
    "if",
    "then",
    "else",
    "dependentSchemas",
    "prefixItems",
    "items",
    "contains",
    "properties",
    "patternProperties",
    "additionalProperties",
    "propertyNames",
    "unevaluatedItems",
    "unevaluatedProperties",
    "type",
    "enum",
    "const",
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "maxLength",
    "minLength",
    "pattern",
    "maxItems",
    "minItems",
    "uniqueItems",
    "maxContains",
    "minContains",
    "maxProperties",
    "minProperties",
    "required",
    "dependentRequired",
    "format",
    "contentEncoding",
    "contentMediaType",
    "contentSchema",
    "title",
    "description",
    "default",
    "deprecated",
    "readOnly",
    "writeOnly",
    "examples",
    "discriminator",
    "xml",
    "externalDocs",
    "example",
];

fn schema_key_rank(key: &str) -> (usize, usize) {
    // FastAPI 0.141.1 serializes every Schema through its declared field order.
    // Unknown extension keys retain their input order after the known fields.
    SCHEMA_WIRE_FIELD_ORDER
        .iter()
        .position(|candidate| *candidate == key)
        .map_or((1, 0), |index| (0, index))
}

pub(crate) fn register_security_scheme(
    schemes: &mut Vec<(String, Py<PyAny>)>,
    name: String,
    model: Py<PyAny>,
) {
    if let Some((_, existing)) = schemes.iter_mut().find(|(candidate, _)| candidate == &name) {
        *existing = model;
    } else {
        schemes.push((name, model));
    }
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
