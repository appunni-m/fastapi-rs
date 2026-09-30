//! Rust-owned Server-Sent Events API and wire-format encoding.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

#[pyfunction(signature = (*, data_str = None, event = None, id = None, retry = None, comment = None))]
fn format_sse_event(
    py: Python<'_>,
    data_str: Option<String>,
    event: Option<String>,
    id: Option<String>,
    retry: Option<Py<PyAny>>,
    comment: Option<String>,
) -> PyResult<Py<PyBytes>> {
    let mut lines = Vec::new();
    if let Some(comment) = comment.as_deref() {
        lines.extend(split_sse_lines(comment).map(|line| format!(": {line}")));
    }
    if let Some(event) = event {
        lines.push(format!("event: {event}"));
    }
    if let Some(data_str) = data_str.as_deref() {
        lines.extend(split_sse_lines(data_str).map(|line| format!("data: {line}")));
    }
    if let Some(id) = id {
        lines.push(format!("id: {id}"));
    }
    if let Some(retry) = retry {
        lines.push(format!("retry: {}", retry.bind(py).str()?.to_str()?));
    }
    lines.push(String::new());
    lines.push(String::new());
    Ok(PyBytes::new(py, lines.join("\n").as_bytes()).unbind())
}

fn split_sse_lines(value: &str) -> impl Iterator<Item = &str> {
    let mut lines = Vec::new();
    let mut start = 0;
    let mut chars = value.char_indices().peekable();
    while let Some((index, character)) = chars.next() {
        if character == '\r' || character == '\n' {
            lines.push(&value[start..index]);
            if character == '\r'
                && let Some((newline_index, '\n')) = chars.peek().copied()
            {
                chars.next();
                start = newline_index + 1;
            } else {
                start = index + character.len_utf8();
            }
        }
    }
    lines.push(&value[start..]);
    lines.into_iter()
}

#[pyfunction]
fn validate_event(value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    validate_single_line(value, "event")
}

#[pyfunction]
fn validate_id(value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    if !value.is_none() && value.extract::<String>()?.contains('\0') {
        return Err(PyValueError::new_err(
            "SSE 'id' must not contain null characters",
        ));
    }
    validate_single_line(value, "id")
}

fn validate_single_line(value: &Bound<'_, PyAny>, field_name: &str) -> PyResult<Py<PyAny>> {
    if !value.is_none() {
        let value_str = value.extract::<String>()?;
        if value_str.contains('\r') || value_str.contains('\n') {
            return Err(PyValueError::new_err(format!(
                "SSE '{field_name}' must be a single line"
            )));
        }
    }
    Ok(value.clone().unbind())
}

#[pyfunction]
fn validate_data_exclusivity(value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    let data = value.getattr("data")?;
    let raw_data = value.getattr("raw_data")?;
    if data.is_none() || raw_data.is_none() {
        return Ok(value.clone().unbind());
    }
    Err(PyValueError::new_err(
        "Cannot set both 'data' and 'raw_data' on the same ServerSentEvent. Use 'data' for JSON-serialized payloads or 'raw_data' for pre-formatted strings.",
    ))
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let format_function = wrap_pyfunction!(format_sse_event, module)?;
    format_function.setattr("__module__", "fastapi.sse")?;
    module.add_function(format_function)?;

    let event_validator = wrap_pyfunction!(validate_event, module)?;
    let id_validator = wrap_pyfunction!(validate_id, module)?;
    let exclusivity_validator = wrap_pyfunction!(validate_data_exclusivity, module)?;
    let pydantic = py.import("pydantic")?;
    let typing = py.import("typing")?;
    let optional_str = typing
        .getattr("Optional")?
        .get_item(py.get_type::<pyo3::types::PyString>())?;
    let annotated = typing.getattr("Annotated")?;

    let event_after_validator = pydantic
        .getattr("AfterValidator")?
        .call1((event_validator,))?;
    let event_annotation = annotated.get_item((optional_str.clone(), event_after_validator))?;
    let id_after_validator = pydantic.getattr("AfterValidator")?.call1((id_validator,))?;
    let id_annotation = annotated.get_item((optional_str.clone(), id_after_validator))?;

    let field = pydantic.getattr("Field")?;
    let retry_annotation = typing
        .getattr("Optional")?
        .get_item(py.get_type::<pyo3::types::PyInt>())?;
    let retry_field_kwargs = PyDict::new(py);
    retry_field_kwargs.set_item("default", py.None())?;
    retry_field_kwargs.set_item("ge", 0)?;
    let retry_field = field.call((), Some(&retry_field_kwargs))?;

    let validators = PyDict::new(py);
    let model_validator_kwargs = PyDict::new(py);
    model_validator_kwargs.set_item("mode", "after")?;
    let model_validator = pydantic
        .getattr("model_validator")?
        .call((), Some(&model_validator_kwargs))?
        .call1((exclusivity_validator,))?;
    validators.set_item("validate_data_exclusivity", model_validator)?;

    let fields = PyDict::new(py);
    fields.set_item("data", (typing.getattr("Any")?, py.None()))?;
    fields.set_item("raw_data", (optional_str.clone(), py.None()))?;
    fields.set_item("event", (event_annotation, py.None()))?;
    fields.set_item("id", (id_annotation, py.None()))?;
    fields.set_item("retry", (retry_annotation, retry_field))?;
    fields.set_item("comment", (optional_str, py.None()))?;

    let create_kwargs = PyDict::new(py);
    create_kwargs.set_item("__module__", "fastapi.sse")?;
    create_kwargs.set_item("__validators__", validators)?;
    for (name, value) in fields.iter() {
        create_kwargs.set_item(name, value)?;
    }
    let server_sent_event = pydantic
        .getattr("create_model")?
        .call(("ServerSentEvent",), Some(&create_kwargs))?;
    module.add("ServerSentEvent", server_sent_event)?;

    let streaming_response = py
        .import("starlette.responses")?
        .getattr("StreamingResponse")?;
    let bases = PyTuple::new(py, [streaming_response])?;
    let attributes = PyDict::new(py);
    attributes.set_item("__module__", "fastapi.sse")?;
    attributes.set_item("media_type", "text/event-stream")?;
    let response_class = py.import("builtins")?.getattr("type")?.call1((
        "EventSourceResponse",
        bases,
        attributes,
    ))?;
    module.add("EventSourceResponse", response_class)?;
    Ok(())
}

pub(crate) fn is_event_source_response_class(
    py: Python<'_>,
    candidate: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let response_class = py
        .import("fastapi_rs._core")?
        .getattr("EventSourceResponse")?;
    py.import("builtins")?
        .getattr("issubclass")?
        .call1((candidate, response_class))?
        .extract::<bool>()
}

pub(crate) fn is_server_sent_event(py: Python<'_>, candidate: &Bound<'_, PyAny>) -> PyResult<bool> {
    let event_class = py.import("fastapi_rs._core")?.getattr("ServerSentEvent")?;
    candidate.is_instance(&event_class)
}

pub(crate) fn is_server_sent_event_class(
    py: Python<'_>,
    candidate: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    let event_class = py.import("fastapi_rs._core")?.getattr("ServerSentEvent")?;
    Ok(candidate.is(&event_class))
}

pub(crate) fn format_event(
    py: Python<'_>,
    data_str: Option<&str>,
    event: Option<&Bound<'_, PyAny>>,
    id: Option<&Bound<'_, PyAny>>,
    retry: Option<&Bound<'_, PyAny>>,
    comment: Option<&Bound<'_, PyAny>>,
) -> PyResult<Py<PyBytes>> {
    let formatter = py.import("fastapi_rs._core")?.getattr("format_sse_event")?;
    let kwargs = PyDict::new(py);
    let none = py.None();
    kwargs.set_item("data_str", data_str)?;
    kwargs.set_item("event", event.unwrap_or(none.bind(py)))?;
    kwargs.set_item("id", id.unwrap_or(none.bind(py)))?;
    kwargs.set_item("retry", retry.unwrap_or(none.bind(py)))?;
    kwargs.set_item("comment", comment.unwrap_or(none.bind(py)))?;
    Ok(formatter
        .call((), Some(&kwargs))?
        .cast_into::<PyBytes>()
        .map(Bound::unbind)?)
}
