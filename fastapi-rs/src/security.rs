//! Native FastAPI security primitives.

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};

#[pyclass(name = "HTTPBearer", module = "fastapi.security.http", subclass, dict)]
struct PyHttpBearer {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
    auto_error: bool,
}

#[derive(Clone, Copy)]
enum HttpBearerIntrospectionKind {
    Annotations,
    Signature,
}

#[pyclass]
struct HttpBearerIntrospectionDescriptor {
    kind: HttpBearerIntrospectionKind,
}

#[pymethods]
impl HttpBearerIntrospectionDescriptor {
    fn __get__(
        &self,
        py: Python<'_>,
        instance: Option<Bound<'_, PyAny>>,
        _owner: Bound<'_, PyAny>,
    ) -> PyResult<Py<PyAny>> {
        if instance.is_none() {
            return Ok(py.None());
        }
        match self.kind {
            HttpBearerIntrospectionKind::Annotations => dependency_annotations(py),
            HttpBearerIntrospectionKind::Signature => dependency_signature(py),
        }
    }
}

#[pymethods]
impl PyHttpBearer {
    // lint-exception: preserve FastAPI's documented camelCase constructor keyword.
    #[allow(
        non_snake_case,
        reason = "preserve the public camelCase bearerFormat keyword"
    )]
    #[new]
    #[pyo3(signature = (*, bearerFormat=None, scheme_name=None, description=None, auto_error=true))]
    fn new(
        py: Python<'_>,
        bearerFormat: Option<Py<PyAny>>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: bool,
    ) -> PyResult<Self> {
        let module = py.import("fastapi_rs._core")?;
        let model_type = module.getattr("_HTTPBearerModel")?;
        let model_arguments = PyDict::new(py);
        model_arguments.set_item("bearerFormat", bearerFormat.unwrap_or_else(|| py.None()))?;
        model_arguments.set_item("description", description.unwrap_or_else(|| py.None()))?;
        let model = model_type.call((), Some(&model_arguments))?.unbind();

        Ok(Self {
            model,
            scheme_name: scheme_name.unwrap_or_else(|| py.None()),
            auto_error,
        })
    }

    #[getter]
    fn model(&self, py: Python<'_>) -> Py<PyAny> {
        self.model.clone_ref(py)
    }

    #[setter]
    fn set_model(&mut self, model: Py<PyAny>) {
        self.model = model;
    }

    #[getter]
    fn scheme_name(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let instance = slf.bind(py);
        let stored = instance.borrow().scheme_name.clone_ref(py);
        if stored.bind(py).is_truthy()? {
            return Ok(stored);
        }
        let class_name = instance.get_type().name()?.to_string();
        Ok(PyString::new(py, &class_name).unbind().into_any())
    }

    #[setter]
    fn set_scheme_name(&mut self, scheme_name: Py<PyAny>) {
        self.scheme_name = scheme_name;
    }

    #[getter]
    fn auto_error(&self) -> bool {
        self.auto_error
    }

    #[setter]
    fn set_auto_error(&mut self, auto_error: bool) {
        self.auto_error = auto_error;
    }

    fn make_authenticate_headers(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let model = slf.bind(py).getattr("model")?;
        let challenge = model
            .getattr("scheme")?
            .call_method0("title")?
            .extract::<String>()?;
        let headers = PyDict::new(py);
        headers.set_item("WWW-Authenticate", challenge)?;
        Ok(headers.unbind().into_any())
    }

    fn make_not_authenticated_error(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let instance = slf.bind(py);
        let exception_type = instance
            .get_type()
            .getattr("_fastapi_rs_http_exception_type")?;
        let headers = instance.call_method0("make_authenticate_headers")?;
        let exception_arguments = PyDict::new(py);
        exception_arguments.set_item("status_code", 401)?;
        exception_arguments.set_item("detail", "Not authenticated")?;
        exception_arguments.set_item("headers", headers)?;
        exception_type
            .call((), Some(&exception_arguments))
            .map(Bound::unbind)
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            HttpBearerCall {
                security: slf.into_any(),
                request,
            },
        )
    }
}

struct HttpBearerCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

impl AwaitableStateMachine for HttpBearerCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "HTTPBearer dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let headers = self.request.bind(py).getattr("headers")?;
        let authorization = headers.call_method1("get", ("Authorization",))?;
        let authorization_is_present = authorization.is_truthy()?;
        let (scheme, credentials) = authorization_parts(&authorization)?;
        let is_bearer = authorization_is_present
            && !scheme.is_empty()
            && !credentials.is_empty()
            && scheme.to_lowercase() == "bearer";

        if !is_bearer {
            if security.getattr("auto_error")?.is_truthy()? {
                let exception = security.call_method0("make_not_authenticated_error")?;
                return Err(PyErr::from_value(exception));
            }
            return Ok(MachineAction::Complete(py.None()));
        }

        let credentials_type = security
            .get_type()
            .getattr("_fastapi_rs_credentials_type")?;
        let arguments = PyDict::new(py);
        arguments.set_item("scheme", scheme)?;
        arguments.set_item("credentials", credentials)?;
        credentials_type
            .call((), Some(&arguments))
            .map(|credentials| MachineAction::Complete(credentials.unbind()))
    }
}

fn authorization_parts(authorization: &Bound<'_, PyAny>) -> PyResult<(String, String)> {
    if !authorization.is_truthy()? {
        return Ok((String::new(), String::new()));
    }
    let value = authorization.extract::<String>()?;
    match value.split_once(' ') {
        Some((scheme, credentials)) => Ok((scheme.to_owned(), credentials.trim().to_owned())),
        None => Ok((value, String::new())),
    }
}

fn dependency_annotations(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let annotations = PyDict::new(py);
    annotations.set_item(
        "request",
        py.import("starlette.requests")?.getattr("Request")?,
    )?;
    Ok(annotations.unbind().into_any())
}

fn dependency_signature(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let kind = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let parameter_kwargs = PyDict::new(py);
    parameter_kwargs.set_item(
        "annotation",
        py.import("starlette.requests")?.getattr("Request")?,
    )?;
    let request = parameter_type.call(("request", kind), Some(&parameter_kwargs))?;
    let parameters = PyList::new(py, [request])?;
    inspect
        .getattr("Signature")?
        .call1((parameters,))
        .map(Bound::unbind)
}

fn create_credentials_model(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let create_model = py.import("pydantic")?.getattr("create_model")?;
    let fields = PyDict::new(py);
    fields.set_item("__module__", "fastapi.security.http")?;
    fields.set_item("scheme", py.get_type::<PyString>())?;
    fields.set_item("credentials", py.get_type::<PyString>())?;
    create_model
        .call(("HTTPAuthorizationCredentials",), Some(&fields))
        .map(Bound::unbind)
}

fn create_http_bearer_model(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let pydantic = py.import("pydantic")?;
    let typing = py.import("typing")?;
    let string_type = py.get_type::<PyString>();
    let optional_string = typing
        .getattr("Optional")?
        .getattr("__getitem__")?
        .call1((string_type.as_any(),))?;
    let bearer_literal = typing
        .getattr("Literal")?
        .getattr("__getitem__")?
        .call1(("bearer",))?;
    let type_field_kwargs = PyDict::new(py);
    type_field_kwargs.set_item("default", "http")?;
    type_field_kwargs.set_item("alias", "type")?;
    let type_field = pydantic
        .getattr("Field")?
        .call((), Some(&type_field_kwargs))?;

    let fields = PyDict::new(py);
    fields.set_item("__module__", "fastapi.openapi.models")?;
    fields.set_item("type_", (string_type.as_any(), type_field))?;
    fields.set_item("description", (optional_string.clone(), py.None()))?;
    fields.set_item("scheme", (bearer_literal, "bearer"))?;
    fields.set_item("bearerFormat", (optional_string, py.None()))?;
    pydantic
        .getattr("create_model")?
        .call(("HTTPBearer",), Some(&fields))
        .map(Bound::unbind)
}

/// Register the reviewed native HTTP bearer authentication surface.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let credentials_type = create_credentials_model(py)?;
    module.add("HTTPAuthorizationCredentials", credentials_type.bind(py))?;
    let model_type = create_http_bearer_model(py)?;
    module.add("_HTTPBearerModel", model_type.bind(py))?;
    let exception_type = module.getattr("HTTPException")?;

    module.add_class::<PyHttpBearer>()?;
    let http_bearer_type = py.get_type::<PyHttpBearer>();
    http_bearer_type.setattr(
        "__annotations__",
        Py::new(
            py,
            HttpBearerIntrospectionDescriptor {
                kind: HttpBearerIntrospectionKind::Annotations,
            },
        )?,
    )?;
    http_bearer_type.setattr(
        "__signature__",
        Py::new(
            py,
            HttpBearerIntrospectionDescriptor {
                kind: HttpBearerIntrospectionKind::Signature,
            },
        )?,
    )?;
    http_bearer_type.setattr("_fastapi_rs_credentials_type", credentials_type.bind(py))?;
    http_bearer_type.setattr("_fastapi_rs_http_exception_type", exception_type)?;
    Ok(())
}

/// Check whether `value` inherits the native async HTTPBearer call implementation.
pub(crate) fn is_native_async_callable(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    let bearer_type = py.get_type::<PyHttpBearer>();
    let bearer_namespace = bearer_type.getattr("__dict__")?;
    let native_call = bearer_namespace.get_item("__call__")?;
    let mro = value.get_type().getattr("__mro__")?;
    for owner in mro.try_iter()? {
        let owner = owner?;
        let namespace = owner.getattr("__dict__")?;
        if namespace.contains("__call__")? {
            let call = namespace.get_item("__call__")?;
            return Ok(call.is(&native_call));
        }
    }
    Ok(false)
}
