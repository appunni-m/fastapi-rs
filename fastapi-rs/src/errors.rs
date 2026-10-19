//! Rust-owned exception identities used by FastAPI behavior.

use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyRuntimeError, PyTypeError, PyUserWarning};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyInt, PyList, PyString, PyTuple};

create_exception!(
    fastapi.exceptions,
    FastAPIError,
    PyRuntimeError,
    "A generic, FastAPI-specific error."
);
create_exception!(
    fastapi.exceptions,
    DependencyScopeError,
    FastAPIError,
    "A dependency declared an invalid scope relationship."
);
create_exception!(
    fastapi.exceptions,
    PydanticV1NotSupportedError,
    FastAPIError,
    "A pydantic.v1 model is used, which is no longer supported."
);
create_exception!(
    fastapi.exceptions,
    FastAPIDeprecationWarning,
    PyUserWarning,
    "A deprecation warning emitted by FastAPI."
);

create_exception!(
    fastapi.exceptions,
    ValidationException,
    PyException,
    "A validation error occurred."
);
create_exception!(
    fastapi.exceptions,
    RequestValidationError,
    ValidationException,
    "The request data failed validation."
);
create_exception!(
    fastapi.exceptions,
    WebSocketRequestValidationError,
    ValidationException,
    "The WebSocket request data failed validation."
);
create_exception!(
    fastapi.exceptions,
    ResponseValidationError,
    ValidationException,
    "The response data failed validation."
);

#[derive(Clone, Copy)]
enum ValidationExceptionMethod {
    Init,
    Errors,
    String,
}

#[pyclass]
struct ValidationExceptionMethodDescriptor {
    method: ValidationExceptionMethod,
}

#[pymethods]
impl ValidationExceptionMethodDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(
                py,
                Self {
                    method: self.method,
                },
            )
            .map(Py::into_any);
        };
        let instance = instance.unbind();
        match self.method {
            ValidationExceptionMethod::Init => {
                Py::new(py, BoundValidationExceptionInit { instance }).map(Py::into_any)
            }
            ValidationExceptionMethod::Errors => {
                Py::new(py, BoundValidationExceptionErrors { instance }).map(Py::into_any)
            }
            ValidationExceptionMethod::String => {
                Py::new(py, BoundValidationExceptionString { instance }).map(Py::into_any)
            }
        }
    }
}

#[pyclass]
struct BoundValidationExceptionInit {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundValidationExceptionInit {
    #[pyo3(signature = (errors, *, endpoint_ctx=None))]
    fn __call__(
        &self,
        py: Python<'_>,
        errors: Bound<'_, PyAny>,
        endpoint_ctx: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        initialize_validation_exception(
            py,
            self.instance.bind(py),
            &errors,
            endpoint_ctx.as_ref(),
        )?;
        self.instance.bind(py).setattr(
            "endpoint_ctx",
            endpoint_ctx.map(Bound::unbind).unwrap_or_else(|| py.None()),
        )?;
        Ok(())
    }
}

#[pyclass]
struct BoundValidationExceptionErrors {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundValidationExceptionErrors {
    fn __call__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.instance.bind(py).getattr("_errors").map(Bound::unbind)
    }
}

#[pyclass]
struct BoundValidationExceptionString {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundValidationExceptionString {
    fn __call__(&self, py: Python<'_>) -> PyResult<String> {
        let instance = self.instance.bind(py);
        let errors = instance.getattr("_errors")?;
        let count = errors.len()?;
        let suffix = if count == 1 { "" } else { "s" };
        let mut message = format!("{count} validation error{suffix}:\n");
        for error in errors.try_iter()? {
            let error = error?;
            message.push_str("  ");
            message.push_str(&error.str()?.to_string_lossy());
            message.push('\n');
        }

        let endpoint_file = instance.getattr("endpoint_file")?;
        let endpoint_line = instance.getattr("endpoint_line")?;
        let endpoint_function = instance.getattr("endpoint_function")?;
        if endpoint_file.is_truthy()?
            && endpoint_line.is_truthy()?
            && endpoint_function.is_truthy()?
        {
            message.push_str(&format!(
                "\n  File \"{}\", line {}, in {}",
                endpoint_file.str()?.to_string_lossy(),
                endpoint_line.str()?.to_string_lossy(),
                endpoint_function.str()?.to_string_lossy(),
            ));
            let endpoint_path = instance.getattr("endpoint_path")?;
            if endpoint_path.is_truthy()? {
                message.push_str(&format!("\n    {}", endpoint_path.str()?.to_string_lossy()));
            }
        } else {
            let endpoint_path = instance.getattr("endpoint_path")?;
            if endpoint_path.is_truthy()? {
                message.push_str(&format!(
                    "\n  Endpoint: {}",
                    endpoint_path.str()?.to_string_lossy()
                ));
            }
        }
        Ok(message.trim_end().to_owned())
    }
}

#[derive(Clone, Copy)]
enum ResponseValidationErrorMethod {
    Init,
}

#[derive(Clone, Copy)]
enum RequestValidationErrorMethod {
    Init,
}

#[pyclass]
struct ResponseValidationErrorMethodDescriptor {
    method: ResponseValidationErrorMethod,
}

#[pyclass]
struct RequestValidationErrorMethodDescriptor {
    method: RequestValidationErrorMethod,
}

#[pymethods]
impl ResponseValidationErrorMethodDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(
                py,
                Self {
                    method: self.method,
                },
            )
            .map(Py::into_any);
        };
        let instance = instance.unbind();
        match self.method {
            ResponseValidationErrorMethod::Init => {
                Py::new(py, BoundResponseValidationErrorInit { instance }).map(Py::into_any)
            }
        }
    }
}

#[pymethods]
impl RequestValidationErrorMethodDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let Some(instance) = instance else {
            return Py::new(
                py,
                Self {
                    method: self.method,
                },
            )
            .map(Py::into_any);
        };
        let instance = instance.unbind();
        match self.method {
            RequestValidationErrorMethod::Init => {
                Py::new(py, BoundRequestValidationErrorInit { instance }).map(Py::into_any)
            }
        }
    }
}

#[pyclass]
struct BoundRequestValidationErrorInit {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundRequestValidationErrorInit {
    #[pyo3(signature = (errors, *, body=None, endpoint_ctx=None))]
    fn __call__(
        &self,
        py: Python<'_>,
        errors: Bound<'_, PyAny>,
        body: Option<Bound<'_, PyAny>>,
        endpoint_ctx: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        initialize_validation_exception(
            py,
            self.instance.bind(py),
            &errors,
            endpoint_ctx.as_ref(),
        )?;
        self.instance
            .bind(py)
            .setattr("body", body.map(Bound::unbind).unwrap_or_else(|| py.None()))?;
        self.instance.bind(py).setattr(
            "endpoint_ctx",
            endpoint_ctx.map(Bound::unbind).unwrap_or_else(|| py.None()),
        )?;
        Ok(())
    }
}

#[pyclass]
struct BoundResponseValidationErrorInit {
    instance: Py<PyAny>,
}

#[pymethods]
impl BoundResponseValidationErrorInit {
    #[pyo3(signature = (errors, *, body=None, endpoint_ctx=None))]
    fn __call__(
        &self,
        py: Python<'_>,
        errors: Bound<'_, PyAny>,
        body: Option<Bound<'_, PyAny>>,
        endpoint_ctx: Option<Bound<'_, PyAny>>,
    ) -> PyResult<()> {
        let instance = self.instance.bind(py);
        initialize_validation_exception(py, instance, &errors, endpoint_ctx.as_ref())?;
        instance.setattr("body", body.map(Bound::unbind).unwrap_or_else(|| py.None()))?;
        instance.setattr(
            "endpoint_ctx",
            endpoint_ctx.map(Bound::unbind).unwrap_or_else(|| py.None()),
        )?;
        Ok(())
    }
}

fn initialize_validation_exception(
    py: Python<'_>,
    instance: &Bound<'_, PyAny>,
    errors: &Bound<'_, PyAny>,
    endpoint_ctx: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    let context = match endpoint_ctx {
        Some(context) if context.is_truthy()? => context.clone(),
        _ => PyDict::new(py).into_any(),
    };
    instance.setattr("_errors", errors)?;
    instance.setattr(
        "endpoint_function",
        context.call_method1("get", ("function",))?,
    )?;
    instance.setattr("endpoint_path", context.call_method1("get", ("path",))?)?;
    instance.setattr("endpoint_file", context.call_method1("get", ("file",))?)?;
    instance.setattr("endpoint_line", context.call_method1("get", ("line",))?)?;
    Ok(())
}

fn validation_exception_endpoint_context_type<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
    let fields = PyDict::new(py);
    let string_type = py.get_type::<PyString>();
    fields.set_item("function", &string_type)?;
    fields.set_item("path", &string_type)?;
    fields.set_item("file", &string_type)?;
    fields.set_item("line", py.get_type::<PyInt>())?;

    let kwargs = PyDict::new(py);
    kwargs.set_item("total", false)?;
    let endpoint_context = py
        .import("typing")?
        .getattr("TypedDict")?
        .call(("EndpointContext", fields), Some(&kwargs))?;
    endpoint_context.setattr("__module__", "fastapi.exceptions")?;
    Ok(endpoint_context)
}

fn signature_parameter<'py>(
    py: Python<'py>,
    parameter_type: &Bound<'py, PyAny>,
    name: &str,
    kind: &Bound<'py, PyAny>,
    annotation: Option<&Bound<'py, PyAny>>,
    default: Option<&Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyAny>> {
    let kwargs = PyDict::new(py);
    if let Some(annotation) = annotation {
        kwargs.set_item("annotation", annotation)?;
    }
    if let Some(default) = default {
        kwargs.set_item("default", default)?;
    }
    parameter_type.call((name, kind), Some(&kwargs))
}

fn set_validation_exception_signature(
    py: Python<'_>,
    exception_type: &Bound<'_, PyAny>,
    endpoint_context_type: &Bound<'_, PyAny>,
    includes_body: bool,
) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let positional_or_keyword = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let keyword_only = parameter_type.getattr("KEYWORD_ONLY")?;
    let sequence_type = py.import("collections.abc")?.getattr("Sequence")?;
    let any_type = py.import("typing")?.getattr("Any")?;
    let errors_annotation = sequence_type.call_method1("__class_getitem__", (any_type.clone(),))?;
    let none_type = py.None().into_bound(py).get_type();
    let endpoint_context_annotation = py
        .import("operator")?
        .getattr("or_")?
        .call1((endpoint_context_type, &none_type))?;
    let none_value = py.None();

    let parameters = PyList::empty(py);
    parameters.append(signature_parameter(
        py,
        &parameter_type,
        "errors",
        &positional_or_keyword,
        Some(&errors_annotation),
        None,
    )?)?;
    if includes_body {
        parameters.append(signature_parameter(
            py,
            &parameter_type,
            "body",
            &keyword_only,
            Some(&any_type),
            Some(none_value.bind(py)),
        )?)?;
    }
    parameters.append(signature_parameter(
        py,
        &parameter_type,
        "endpoint_ctx",
        &keyword_only,
        Some(&endpoint_context_annotation),
        Some(none_value.bind(py)),
    )?)?;

    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", py.None())?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    exception_type.setattr("__signature__", signature)
}

#[pyclass(name = "_HTTPExceptionInit", module = "fastapi_rs._core", dict)]
struct HTTPExceptionInit {
    initializer: Py<PyAny>,
}

#[pymethods]
impl HTTPExceptionInit {
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
        slf: Py<Self>,
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<PyAny>> {
        let initializer = slf.borrow(py).initializer.clone_ref(py);
        initializer.bind(py).call(args, kwargs).map(Bound::unbind)
    }
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let http_exception_base = py
        .import("starlette.exceptions")?
        .getattr("HTTPException")?;
    let http_exception_initializer = http_exception_base.getattr("__init__")?.unbind();
    let http_exception_bases = PyTuple::new(py, [http_exception_base])?;
    let http_exception_namespace = PyDict::new(py);
    http_exception_namespace.set_item("__module__", "fastapi.exceptions")?;
    http_exception_namespace.set_item(
        "__doc__",
        concat!(
            "\n",
            "    An HTTP exception you can raise in your own code to show errors to the client.\n",
            "\n",
            "    This is for client errors, invalid authentication, invalid data, etc. Not for server\n",
            "    errors in your code.\n",
            "\n",
            "    Read more about it in the\n",
            "    [FastAPI docs for Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/).\n",
            "\n",
            "    ## Example\n",
            "\n",
            "    \x60\x60\x60python\n",
            "    from fastapi import FastAPI, HTTPException\n",
            "\n",
            "    app = FastAPI()\n",
            "\n",
            "    items = {\"foo\": \"The Foo Wrestlers\"}\n",
            "\n",
            "\n",
            "    @app.get(\"/items/{item_id}\")\n",
            "    async def read_item(item_id: str):\n",
            "        if item_id not in items:\n",
            "            raise HTTPException(status_code=404, detail=\"Item not found\")\n",
            "        return {\"item\": items[item_id]}\n",
            "    \x60\x60\x60\n",
            "    "
        ),
    )?;
    let http_exception_type = py.import("builtins")?.getattr("type")?.call1((
        "HTTPException",
        http_exception_bases,
        http_exception_namespace,
    ))?;
    set_http_exception_signature(py, &http_exception_type, http_exception_initializer)?;

    let validation_exception_type = py.get_type::<ValidationException>();
    let endpoint_context_type = validation_exception_endpoint_context_type(py)?;
    set_validation_exception_signature(
        py,
        &validation_exception_type,
        &endpoint_context_type,
        false,
    )?;
    validation_exception_type.setattr(
        "__init__",
        Py::new(
            py,
            ValidationExceptionMethodDescriptor {
                method: ValidationExceptionMethod::Init,
            },
        )?,
    )?;
    validation_exception_type.setattr(
        "errors",
        Py::new(
            py,
            ValidationExceptionMethodDescriptor {
                method: ValidationExceptionMethod::Errors,
            },
        )?,
    )?;
    validation_exception_type.setattr(
        "__str__",
        Py::new(
            py,
            ValidationExceptionMethodDescriptor {
                method: ValidationExceptionMethod::String,
            },
        )?,
    )?;

    let request_exception_type = py.get_type::<RequestValidationError>();
    set_validation_exception_signature(py, &request_exception_type, &endpoint_context_type, true)?;
    request_exception_type.setattr(
        "__init__",
        Py::new(
            py,
            RequestValidationErrorMethodDescriptor {
                method: RequestValidationErrorMethod::Init,
            },
        )?,
    )?;

    let exception_type = py.get_type::<ResponseValidationError>();
    set_validation_exception_signature(py, &exception_type, &endpoint_context_type, true)?;
    exception_type.setattr(
        "__init__",
        Py::new(
            py,
            ResponseValidationErrorMethodDescriptor {
                method: ResponseValidationErrorMethod::Init,
            },
        )?,
    )?;
    let websocket_exception_base = py
        .import("starlette.exceptions")?
        .getattr("WebSocketException")?;
    let websocket_exception_initializer = websocket_exception_base.getattr("__init__")?.unbind();
    let websocket_exception_bases = PyTuple::new(py, [websocket_exception_base])?;
    let websocket_exception_namespace = PyDict::new(py);
    websocket_exception_namespace.set_item("__module__", "fastapi.exceptions")?;
    websocket_exception_namespace.set_item(
        "__doc__",
        concat!(
            "\n",
            "    A WebSocket exception you can raise in your own code to show errors to the client.\n",
            "\n",
            "    This is for client errors, invalid authentication, invalid data, etc. Not for server\n",
            "    errors in your code.\n",
            "\n",
            "    Read more about it in the\n",
            "    [FastAPI docs for WebSockets](https://fastapi.tiangolo.com/advanced/websockets/).\n",
            "\n",
            "    ## Example\n",
            "\n",
            "    ```python\n",
            "    from typing import Annotated\n",
            "\n",
            "    from fastapi import (\n",
            "        Cookie,\n",
            "        FastAPI,\n",
            "        WebSocket,\n",
            "        WebSocketException,\n",
            "        status,\n",
            "    )\n",
            "\n",
            "    app = FastAPI()\n",
            "\n",
            "    @app.websocket(\"/items/{item_id}/ws\")\n",
            "    async def websocket_endpoint(\n",
            "        *,\n",
            "        websocket: WebSocket,\n",
            "        session: Annotated[str | None, Cookie()] = None,\n",
            "        item_id: str,\n",
            "    ):\n",
            "        if session is None:\n",
            "            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)\n",
            "        await websocket.accept()\n",
            "        while True:\n",
            "            data = await websocket.receive_text()\n",
            "            await websocket.send_text(f\"Session cookie is: {session}\")\n",
            "            await websocket.send_text(f\"Message text was: {data}, for item ID: {item_id}\")\n",
            "    ```\n",
            "    "
        ),
    )?;
    let websocket_exception_type = py.import("builtins")?.getattr("type")?.call1((
        "WebSocketException",
        websocket_exception_bases,
        websocket_exception_namespace,
    ))?;
    set_websocket_exception_signature(
        py,
        &websocket_exception_type,
        websocket_exception_initializer,
    )?;
    let websocket_request_exception_type = py.get_type::<WebSocketRequestValidationError>();
    set_validation_exception_signature(
        py,
        &websocket_request_exception_type,
        &endpoint_context_type,
        false,
    )?;
    module.add("HTTPException", http_exception_type)?;
    module.add("ValidationException", validation_exception_type)?;
    module.add("RequestValidationError", request_exception_type)?;
    module.add(
        "WebSocketRequestValidationError",
        websocket_request_exception_type,
    )?;
    module.add("ResponseValidationError", exception_type)?;
    module.add("_FastAPIError", py.get_type::<FastAPIError>())?;
    module.add(
        "_FastAPIDeprecationWarning",
        py.get_type::<FastAPIDeprecationWarning>(),
    )?;
    module.add(
        "_DependencyScopeError",
        py.get_type::<DependencyScopeError>(),
    )?;
    module.add("WebSocketException", websocket_exception_type)
}

pub(crate) fn fastapi_deprecation_warning_type<'py>(py: Python<'py>) -> Bound<'py, PyAny> {
    py.get_type::<FastAPIDeprecationWarning>().into_any()
}

pub(crate) fn fastapi_error(message: &str) -> PyErr {
    FastAPIError::new_err(message.to_owned())
}

pub(crate) fn dependency_scope_error(message: &str) -> PyErr {
    DependencyScopeError::new_err(message.to_owned())
}

pub(crate) fn request_validation_error_type<'py>(py: Python<'py>) -> Bound<'py, PyAny> {
    py.get_type::<RequestValidationError>().into_any()
}

pub(crate) fn websocket_request_validation_error(
    py: Python<'_>,
    errors: &Bound<'_, PyAny>,
    endpoint_ctx: Option<&Bound<'_, PyAny>>,
) -> PyResult<PyErr> {
    let kwargs = PyDict::new(py);
    if let Some(endpoint_ctx) = endpoint_ctx {
        kwargs.set_item("endpoint_ctx", endpoint_ctx)?;
    } else {
        kwargs.set_item("endpoint_ctx", py.None())?;
    }
    let exception = py
        .get_type::<WebSocketRequestValidationError>()
        .call((errors,), Some(&kwargs))?;
    Ok(PyErr::from_value(exception))
}

pub(crate) fn websocket_request_validation_error_type<'py>(py: Python<'py>) -> Bound<'py, PyAny> {
    py.get_type::<WebSocketRequestValidationError>().into_any()
}

pub(crate) fn request_validation_error(
    py: Python<'_>,
    errors: &Bound<'_, PyAny>,
    body: Option<&Bound<'_, PyAny>>,
    endpoint_ctx: Option<&Bound<'_, PyAny>>,
) -> PyResult<PyErr> {
    let kwargs = PyDict::new(py);
    if let Some(body) = body {
        kwargs.set_item("body", body)?;
    } else {
        kwargs.set_item("body", py.None())?;
    }
    if let Some(endpoint_ctx) = endpoint_ctx {
        kwargs.set_item("endpoint_ctx", endpoint_ctx)?;
    } else {
        kwargs.set_item("endpoint_ctx", py.None())?;
    }
    let exception = py
        .get_type::<RequestValidationError>()
        .call((errors,), Some(&kwargs))?;
    Ok(PyErr::from_value(exception))
}

fn set_http_exception_signature(
    py: Python<'_>,
    exception_type: &Bound<'_, PyAny>,
    initializer: Py<PyAny>,
) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let annotated = py.import("typing")?.getattr("Annotated")?;
    let status_doc = annotated_doc.call1((
        "\n                HTTP status code to send to the client.\n\n                Read more about it in the\n                [FastAPI docs for Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception)\n                ",
    ))?;
    let detail_doc = annotated_doc.call1((
        "\n                Any data to be sent to the client in the `detail` key of the JSON\n                response.\n\n                Read more about it in the\n                [FastAPI docs for Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception)\n                ",
    ))?;
    let headers_doc = annotated_doc.call1((
        "\n                Any headers to send to the client in the response.\n\n                Read more about it in the\n                [FastAPI docs for Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/#add-custom-headers)\n\n                ",
    ))?;
    let status_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [py.get_type::<PyInt>().as_any(), status_doc.as_any()],
        )?,))?;
    let any = py.import("typing")?.getattr("Any")?;
    let detail_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(py, [any.as_any(), detail_doc.as_any()])?,))?;
    let mapping = py.import("collections.abc")?.getattr("Mapping")?;
    let mapping_arguments = PyTuple::new(
        py,
        [
            py.get_type::<PyString>().as_any(),
            py.get_type::<PyString>().as_any(),
        ],
    )?;
    let mapping = mapping
        .getattr("__class_getitem__")?
        .call1((mapping_arguments,))?;
    let none_type = py.None().bind(py).get_type();
    let optional_mapping = py
        .import("operator")?
        .getattr("or_")?
        .call1((mapping, none_type))?;
    let headers_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_mapping.as_any(), headers_doc.as_any()],
        )?,))?;

    let parameter_type = inspect.getattr("Parameter")?;
    let kind = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let self_parameter = parameter_type.call(("self", &kind), None)?;
    let status_kwargs = PyDict::new(py);
    status_kwargs.set_item("annotation", &status_annotation)?;
    let status = parameter_type.call(("status_code", &kind), Some(&status_kwargs))?;
    let detail_kwargs = PyDict::new(py);
    detail_kwargs.set_item("annotation", &detail_annotation)?;
    detail_kwargs.set_item("default", py.None())?;
    let detail = parameter_type.call(("detail", &kind), Some(&detail_kwargs))?;
    let headers_kwargs = PyDict::new(py);
    headers_kwargs.set_item("annotation", &headers_annotation)?;
    headers_kwargs.set_item("default", py.None())?;
    let headers = parameter_type.call(("headers", &kind), Some(&headers_kwargs))?;
    let initializer_parameters = PyList::new(
        py,
        [
            self_parameter,
            status.clone(),
            detail.clone(),
            headers.clone(),
        ],
    )?;
    let parameters = PyList::new(py, [status, detail, headers])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", py.None())?;
    let signature_type = inspect.getattr("Signature")?;
    let signature = signature_type.call((parameters,), Some(&signature_kwargs))?;
    let initializer_signature =
        signature_type.call((initializer_parameters,), Some(&signature_kwargs))?;
    exception_type.setattr("__signature__", signature)?;

    let descriptor = Py::new(py, HTTPExceptionInit { initializer })?;
    let descriptor = descriptor.bind(py);
    descriptor.setattr("__module__", "fastapi.exceptions")?;
    descriptor.setattr("__name__", "__init__")?;
    descriptor.setattr("__qualname__", "HTTPException.__init__")?;
    descriptor.setattr("__doc__", py.None())?;
    descriptor.setattr("__defaults__", PyTuple::new(py, [py.None(), py.None()])?)?;
    descriptor.setattr("__signature__", initializer_signature)?;

    let annotations = PyDict::new(py);
    annotations.set_item("status_code", status_annotation)?;
    annotations.set_item("detail", detail_annotation)?;
    annotations.set_item("headers", headers_annotation)?;
    annotations.set_item("return", py.None())?;
    descriptor.setattr("__annotations__", annotations)?;
    descriptor.setattr("__type_params__", PyTuple::empty(py))?;
    exception_type.setattr("__init__", descriptor)
}

fn set_websocket_exception_signature(
    py: Python<'_>,
    exception_type: &Bound<'_, PyAny>,
    initializer: Py<PyAny>,
) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let annotated = py.import("typing")?.getattr("Annotated")?;
    let code_doc = annotated_doc.call1((
        "\n                A closing code from the\n                [valid codes defined in the specification](https://datatracker.ietf.org/doc/html/rfc6455#section-7.4.1).\n                ",
    ))?;
    let reason_doc = annotated_doc.call1((
        "\n                The reason to close the WebSocket connection.\n\n                It is UTF-8-encoded data. The interpretation of the reason is up to the\n                application, it is not specified by the WebSocket specification.\n\n                It could contain text that could be human-readable or interpretable\n                by the client code, etc.\n                ",
    ))?;
    let code_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [
                py.get_type::<pyo3::types::PyInt>().as_any(),
                code_doc.as_any(),
            ],
        )?,))?;
    let string_type = py.get_type::<PyString>();
    let none = py.None();
    let none_type = none.bind(py).get_type();
    let optional_string = string_type.call_method1("__or__", (none_type,))?;
    let reason_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_string.as_any(), reason_doc.as_any()],
        )?,))?;

    let parameter_type = inspect.getattr("Parameter")?;
    let kind = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let self_parameter = parameter_type.call(("self", &kind), None)?;
    let code_kwargs = PyDict::new(py);
    code_kwargs.set_item("annotation", &code_annotation)?;
    let code = parameter_type.call(("code", &kind), Some(&code_kwargs))?;
    let reason_kwargs = PyDict::new(py);
    reason_kwargs.set_item("annotation", &reason_annotation)?;
    reason_kwargs.set_item("default", py.None())?;
    let reason = parameter_type.call(("reason", &kind), Some(&reason_kwargs))?;
    let initializer_parameters = PyList::new(py, [self_parameter, code.clone(), reason.clone()])?;
    let parameters = PyList::new(py, [code, reason])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", py.None())?;
    let signature_type = inspect.getattr("Signature")?;
    let signature = signature_type.call((parameters,), Some(&signature_kwargs))?;
    let initializer_signature =
        signature_type.call((initializer_parameters,), Some(&signature_kwargs))?;
    exception_type.setattr("__signature__", signature)?;

    let descriptor = Py::new(py, HTTPExceptionInit { initializer })?;
    let descriptor = descriptor.bind(py);
    descriptor.setattr("__module__", "fastapi.exceptions")?;
    descriptor.setattr("__name__", "__init__")?;
    descriptor.setattr("__qualname__", "WebSocketException.__init__")?;
    descriptor.setattr("__doc__", py.None())?;
    descriptor.setattr("__defaults__", PyTuple::new(py, [py.None()])?)?;
    descriptor.setattr("__signature__", initializer_signature)?;

    let annotations = PyDict::new(py);
    annotations.set_item("code", code_annotation)?;
    annotations.set_item("reason", reason_annotation)?;
    annotations.set_item("return", py.None())?;
    descriptor.setattr("__annotations__", annotations)?;
    descriptor.setattr("__type_params__", PyTuple::empty(py))?;
    exception_type.setattr("__init__", descriptor)
}

pub(crate) fn response_validation_error(
    py: Python<'_>,
    validation_error: &PyErr,
    body: &Bound<'_, PyAny>,
    endpoint_ctx: &Bound<'_, PyAny>,
) -> PyResult<PyErr> {
    let kwargs = PyDict::new(py);
    kwargs.set_item("include_url", false)?;
    let details = validation_error
        .value(py)
        .call_method("errors", (), Some(&kwargs))?
        .cast_into::<PyList>()?;
    let response_details = PyList::empty(py);

    for detail in details.iter() {
        let detail = detail.cast_into::<PyDict>()?;
        let response_detail = PyDict::new(py);
        for (key, value) in detail.iter() {
            let key = key.extract::<String>()?;
            match key.as_str() {
                "url" => {}
                "loc" => {
                    let location = value.cast_into::<PyTuple>()?;
                    let mut prefixed_location = Vec::with_capacity(location.len() + 1);
                    prefixed_location.push(PyString::new(py, "response").into_any().unbind());
                    prefixed_location.extend(location.iter().map(Bound::unbind));
                    response_detail.set_item("loc", PyTuple::new(py, prefixed_location)?)?;
                }
                _ => response_detail.set_item(key, value)?,
            }
        }
        response_details.append(response_detail)?;
    }

    let kwargs = PyDict::new(py);
    kwargs.set_item("body", body)?;
    kwargs.set_item("endpoint_ctx", endpoint_ctx)?;
    let exception = py
        .get_type::<ResponseValidationError>()
        .call((response_details,), Some(&kwargs))?;
    Ok(PyErr::from_value(exception))
}
