//! Rust-owned Server-Sent Events API and wire-format encoding.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple, PyType};

const EVENT_SOURCE_RESPONSE_DOC: &str = r#"Streaming response with `text/event-stream` media type.

    Use as `response_class=EventSourceResponse` on a *path operation* that uses `yield`
    to enable Server Sent Events (SSE) responses.

    Works with **any HTTP method** (`GET`, `POST`, etc.), which makes it compatible
    with protocols like MCP that stream SSE over `POST`.

    The actual encoding logic lives in the FastAPI routing layer. This class
    serves mainly as a marker and sets the correct `Content-Type`.
    "#;

const SERVER_SENT_EVENT_DOC: &str = r#"Represents a single Server-Sent Event.

    When `yield`ed from a *path operation function* that uses
    `response_class=EventSourceResponse`, each `ServerSentEvent` is encoded
    into the [SSE wire format](https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream)
    (`text/event-stream`).

    If you yield a plain object (dict, Pydantic model, etc.) instead, it is
    automatically JSON-encoded and sent as the `data:` field.

    All `data` values **including plain strings** are JSON-serialized.

    For example, `data="hello"` produces `data: "hello"` on the wire (with
    quotes).
    "#;

const SSE_DATA_DOC: &str = r#"
            The event payload.

            Can be any JSON-serializable value: a Pydantic model, dict, list,
            string, number, etc. It is **always** serialized to JSON: strings
            are quoted (`"hello"` becomes `data: "hello"` on the wire).

            Mutually exclusive with `raw_data`.
            "#;

const SSE_RAW_DATA_DOC: &str = r#"
            Raw string to send as the `data:` field **without** JSON encoding.

            Use this when you need to send pre-formatted text, HTML fragments,
            CSV lines, or any non-JSON payload. The string is placed directly
            into the `data:` field as-is.

            Mutually exclusive with `data`.
            "#;

const SSE_EVENT_DOC: &str = r#"
            Optional event type name.

            Maps to `addEventListener(event, ...)` on the browser. When omitted,
            the browser dispatches on the generic `message` event. Must be a
            single line.
            "#;

const SSE_ID_DOC: &str = r#"
            Optional event ID.

            The browser sends this value back as the `Last-Event-ID` header on
            automatic reconnection. **Must be a single line** and must not contain
            null (`\0`) characters.
            "#;

const SSE_RETRY_DOC: &str = r#"
            Optional reconnection time in **milliseconds**.

            Tells the browser how long to wait before reconnecting after the
            connection is lost. Must be a non-negative integer.
            "#;

const SSE_COMMENT_DOC: &str = r#"
            Optional comment line(s).

            Comment lines start with `:` in the SSE wire format and are ignored by
            `EventSource` clients. Useful for keep-alive pings to prevent
            proxy/load-balancer timeouts.
            "#;

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
fn _check_event_single_line(value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    validate_single_line(value, "event")
}

#[pyfunction]
fn _check_id_valid(value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
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

    let event_validator = wrap_pyfunction!(_check_event_single_line, module)?;
    event_validator.setattr("__module__", "fastapi.sse")?;
    let id_validator = wrap_pyfunction!(_check_id_valid, module)?;
    id_validator.setattr("__module__", "fastapi.sse")?;
    let exclusivity_validator = wrap_pyfunction!(validate_data_exclusivity, module)?;
    let pydantic = py.import("pydantic")?;
    let typing = py.import("typing")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let none_type = py.import("types")?.getattr("NoneType")?;
    let type_type = py.get_type::<PyType>();
    let optional_str = type_type.call_method1(
        "__or__",
        (py.get_type::<pyo3::types::PyString>(), none_type.clone()),
    )?;
    let annotated = typing.getattr("Annotated")?;

    let event_after_validator = pydantic
        .getattr("AfterValidator")?
        .call1((event_validator,))?;
    let event_annotation = annotated.get_item((
        optional_str.clone(),
        event_after_validator,
        annotated_doc.call1((SSE_EVENT_DOC,))?,
    ))?;
    let id_after_validator = pydantic.getattr("AfterValidator")?.call1((id_validator,))?;
    let id_annotation = annotated.get_item((
        optional_str.clone(),
        id_after_validator,
        annotated_doc.call1((SSE_ID_DOC,))?,
    ))?;
    let data_annotation = annotated.get_item((
        typing.getattr("Any")?,
        annotated_doc.call1((SSE_DATA_DOC,))?,
    ))?;
    let raw_data_annotation = annotated.get_item((
        optional_str.clone(),
        annotated_doc.call1((SSE_RAW_DATA_DOC,))?,
    ))?;
    let comment_annotation = annotated.get_item((
        optional_str.clone(),
        annotated_doc.call1((SSE_COMMENT_DOC,))?,
    ))?;

    let field = pydantic.getattr("Field")?;
    let retry_base_annotation =
        type_type.call_method1("__or__", (py.get_type::<pyo3::types::PyInt>(), none_type))?;
    let retry_field_kwargs = PyDict::new(py);
    retry_field_kwargs.set_item("ge", 0)?;
    let retry_field = field.call((), Some(&retry_field_kwargs))?;
    let retry_annotation = annotated.get_item((
        retry_base_annotation,
        retry_field,
        annotated_doc.call1((SSE_RETRY_DOC,))?,
    ))?;

    let validators = PyDict::new(py);
    let model_validator_kwargs = PyDict::new(py);
    model_validator_kwargs.set_item("mode", "after")?;
    let model_validator = pydantic
        .getattr("model_validator")?
        .call((), Some(&model_validator_kwargs))?
        .call1((exclusivity_validator,))?;
    validators.set_item("validate_data_exclusivity", model_validator)?;

    let fields = PyDict::new(py);
    fields.set_item("data", (data_annotation, py.None()))?;
    fields.set_item("raw_data", (raw_data_annotation, py.None()))?;
    fields.set_item("event", (event_annotation, py.None()))?;
    fields.set_item("id", (id_annotation, py.None()))?;
    fields.set_item("retry", (retry_annotation, py.None()))?;
    fields.set_item("comment", (comment_annotation, py.None()))?;

    let create_kwargs = PyDict::new(py);
    create_kwargs.set_item("__module__", "fastapi.sse")?;
    create_kwargs.set_item("__doc__", SERVER_SENT_EVENT_DOC)?;
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
    attributes.set_item("__doc__", EVENT_SOURCE_RESPONSE_DOC)?;
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
