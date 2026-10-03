//! Native FastAPI security primitives.

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};
use base64::Engine;
use base64::engine::general_purpose::{GeneralPurpose, GeneralPurposeConfig};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyType};

static PYTHON_COMPATIBLE_STANDARD_BASE64: GeneralPurpose = GeneralPurpose::new(
    &base64::alphabet::STANDARD,
    GeneralPurposeConfig::new().with_decode_allow_trailing_bits(true),
);

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

#[pyclass(name = "HTTPBasic", module = "fastapi.security.http", subclass, dict)]
struct PyHttpBasic {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
    realm: Py<PyAny>,
    auto_error: bool,
}

#[pymethods]
impl PyHttpBasic {
    #[new]
    #[pyo3(signature = (*, scheme_name=None, realm=None, description=None, auto_error=true))]
    fn new(
        py: Python<'_>,
        scheme_name: Option<Py<PyAny>>,
        realm: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: bool,
    ) -> PyResult<Self> {
        let module = py.import("fastapi_rs._core")?;
        let model_type = module.getattr("_HTTPBasicModel")?;
        let model_arguments = PyDict::new(py);
        model_arguments.set_item("scheme", "basic")?;
        model_arguments.set_item("description", description.unwrap_or_else(|| py.None()))?;
        let model = model_type.call((), Some(&model_arguments))?.unbind();

        Ok(Self {
            model,
            scheme_name: scheme_name.unwrap_or_else(|| py.None()),
            realm: realm.unwrap_or_else(|| py.None()),
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
    fn realm(&self, py: Python<'_>) -> Py<PyAny> {
        self.realm.clone_ref(py)
    }

    #[setter]
    fn set_realm(&mut self, realm: Py<PyAny>) {
        self.realm = realm;
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
        let instance = slf.bind(py);
        let realm = instance.getattr("realm")?;
        let challenge = if realm.is_truthy()? {
            let realm = py.import("builtins")?.getattr("str")?.call1((realm,))?;
            format!("Basic realm=\"{}\"", realm.extract::<String>()?)
        } else {
            "Basic".to_owned()
        };
        let headers = PyDict::new(py);
        headers.set_item("WWW-Authenticate", challenge)?;
        Ok(headers.unbind().into_any())
    }

    fn make_not_authenticated_error(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        make_not_authenticated_error(slf.bind(py).as_any())
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            HttpBasicCall {
                security: slf.into_any(),
                request,
            },
        )
    }
}

#[pyclass(name = "HTTPDigest", module = "fastapi.security.http", subclass, dict)]
struct PyHttpDigest {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
    auto_error: bool,
}

#[pymethods]
impl PyHttpDigest {
    #[new]
    #[pyo3(signature = (*, scheme_name=None, description=None, auto_error=true))]
    fn new(
        py: Python<'_>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: bool,
    ) -> PyResult<Self> {
        let module = py.import("fastapi_rs._core")?;
        let model_type = module.getattr("_HTTPBasicModel")?;
        let model_arguments = PyDict::new(py);
        model_arguments.set_item("scheme", "digest")?;
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
        let scheme = slf.bind(py).getattr("model")?.getattr("scheme")?;
        let challenge = scheme.call_method0("title")?;
        let headers = PyDict::new(py);
        headers.set_item("WWW-Authenticate", challenge)?;
        Ok(headers.unbind().into_any())
    }

    fn make_not_authenticated_error(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        make_not_authenticated_error(slf.bind(py).as_any())
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            HttpDigestCall {
                security: slf.into_any(),
                request,
            },
        )
    }
}

#[pyclass(
    name = "OAuth2PasswordBearer",
    module = "fastapi.security.oauth2",
    subclass,
    dict
)]
struct PyOAuth2PasswordBearer {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
    auto_error: bool,
}

#[pymethods]
impl PyOAuth2PasswordBearer {
    // lint-exception: preserve FastAPI's documented camelCase constructor keywords.
    #[allow(
        non_snake_case,
        reason = "preserve the public camelCase tokenUrl and refreshUrl keywords"
    )]
    #[new]
    #[pyo3(signature = (tokenUrl, scheme_name=None, scopes=None, description=None, auto_error=true, refreshUrl=None))]
    fn new(
        py: Python<'_>,
        tokenUrl: Py<PyAny>,
        scheme_name: Option<Py<PyAny>>,
        scopes: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: bool,
        refreshUrl: Option<Py<PyAny>>,
    ) -> PyResult<Self> {
        let module = py.import("fastapi_rs._core")?;
        let password_flow_type = module.getattr("_OAuth2PasswordFlowModel")?;
        let scopes = match scopes {
            Some(scopes) if scopes.bind(py).is_truthy()? => scopes,
            _ => PyDict::new(py).unbind().into_any(),
        };
        let flow_arguments = PyDict::new(py);
        flow_arguments.set_item("tokenUrl", tokenUrl)?;
        flow_arguments.set_item("refreshUrl", refreshUrl.unwrap_or_else(|| py.None()))?;
        flow_arguments.set_item("scopes", scopes)?;
        let password_flow = password_flow_type.call((), Some(&flow_arguments))?.unbind();

        let flows_type = module.getattr("_OAuth2FlowsModel")?;
        let flows_arguments = PyDict::new(py);
        flows_arguments.set_item("password", password_flow)?;
        let flows = flows_type.call((), Some(&flows_arguments))?.unbind();

        let model_type = module.getattr("_OAuth2PasswordBearerModel")?;
        let model_arguments = PyDict::new(py);
        model_arguments.set_item("flows", flows)?;
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
        let _ = slf;
        let headers = PyDict::new(py);
        headers.set_item("WWW-Authenticate", "Bearer")?;
        Ok(headers.unbind().into_any())
    }

    fn make_not_authenticated_error(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        make_not_authenticated_error(slf.bind(py).as_any())
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            OAuth2PasswordBearerCall {
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

struct HttpBasicCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

impl AwaitableStateMachine for HttpBasicCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "HTTPBasic dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let headers = self.request.bind(py).getattr("headers")?;
        let authorization = headers.call_method1("get", ("Authorization",))?;
        let authorization_is_present = authorization.is_truthy()?;
        let (scheme, param) = authorization_parts(&authorization)?;
        if !authorization_is_present || scheme.to_lowercase() != "basic" {
            if security.getattr("auto_error")?.is_truthy()? {
                let exception = security.call_method0("make_not_authenticated_error")?;
                return Err(PyErr::from_value(exception));
            }
            return Ok(MachineAction::Complete(py.None()));
        }

        let Some(credentials) = decode_basic_credentials(&param) else {
            let exception = security.call_method0("make_not_authenticated_error")?;
            return Err(PyErr::from_value(exception));
        };
        let Some((username, password)) = credentials.split_once(':') else {
            let exception = security.call_method0("make_not_authenticated_error")?;
            return Err(PyErr::from_value(exception));
        };

        let credentials_type = security
            .get_type()
            .getattr("_fastapi_rs_credentials_type")?;
        let arguments = PyDict::new(py);
        arguments.set_item("username", username)?;
        arguments.set_item("password", password)?;
        credentials_type
            .call((), Some(&arguments))
            .map(|credentials| MachineAction::Complete(credentials.unbind()))
    }
}

struct HttpDigestCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

impl AwaitableStateMachine for HttpDigestCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "HTTPDigest dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let headers = self.request.bind(py).getattr("headers")?;
        let authorization = headers.call_method1("get", ("Authorization",))?;
        let authorization_is_present = authorization.is_truthy()?;
        let (scheme, credentials) = authorization_parts(&authorization)?;
        let is_digest = authorization_is_present
            && !scheme.is_empty()
            && !credentials.is_empty()
            && scheme.to_lowercase() == "digest";

        if !is_digest {
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

struct OAuth2PasswordBearerCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

impl AwaitableStateMachine for OAuth2PasswordBearerCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "OAuth2PasswordBearer dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let headers = self.request.bind(py).getattr("headers")?;
        let authorization = headers.call_method1("get", ("Authorization",))?;
        let authorization_is_present = authorization.is_truthy()?;
        let (scheme, token) = authorization_parts(&authorization)?;
        if !authorization_is_present || scheme.to_lowercase() != "bearer" {
            if security.getattr("auto_error")?.is_truthy()? {
                let exception = security.call_method0("make_not_authenticated_error")?;
                return Err(PyErr::from_value(exception));
            }
            return Ok(MachineAction::Complete(py.None()));
        }

        Ok(MachineAction::Complete(
            PyString::new(py, &token).unbind().into_any(),
        ))
    }
}

fn decode_basic_credentials(param: &str) -> Option<String> {
    if !param.is_ascii() {
        return None;
    }
    let filtered: Vec<u8> = param
        .bytes()
        .filter(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'+' | b'/' | b'='))
        .collect();
    let padding_length = filtered
        .iter()
        .rev()
        .take_while(|byte| **byte == b'=')
        .count();
    let symbols_length = filtered.len().checked_sub(padding_length)?;
    if filtered[..symbols_length].contains(&b'=') {
        return None;
    }
    let required_padding = match symbols_length % 4 {
        0 => 0,
        2 => 2,
        3 => 1,
        _ => return None,
    };
    if padding_length < required_padding {
        return None;
    }
    let mut normalized = filtered[..symbols_length].to_vec();
    normalized.extend(std::iter::repeat_n(b'=', required_padding));
    let decoded = PYTHON_COMPATIBLE_STANDARD_BASE64.decode(normalized).ok()?;
    if !decoded.is_ascii() {
        return None;
    }
    String::from_utf8(decoded).ok()
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

fn attach_dependency_introspection(py: Python<'_>, class: &Bound<'_, PyType>) -> PyResult<()> {
    class.setattr(
        "__annotations__",
        Py::new(
            py,
            HttpBearerIntrospectionDescriptor {
                kind: HttpBearerIntrospectionKind::Annotations,
            },
        )?,
    )?;
    class.setattr(
        "__signature__",
        Py::new(
            py,
            HttpBearerIntrospectionDescriptor {
                kind: HttpBearerIntrospectionKind::Signature,
            },
        )?,
    )?;
    Ok(())
}

fn optional_type<'py>(py: Python<'py>, inner: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyAny>> {
    py.import("typing")?
        .getattr("Optional")?
        .getattr("__getitem__")?
        .call1((inner,))
}

fn create_http_basic_credentials_model(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let pydantic = py.import("pydantic")?;
    let typing = py.import("typing")?;
    let string_type = py.get_type::<PyString>();
    let annotated_type = typing.getattr("Annotated")?;
    let subscribe = py.import("operator")?.getattr("getitem")?;
    let doc_type = py.import("annotated_doc")?.getattr("Doc")?;
    let ellipsis = py.import("builtins")?.getattr("Ellipsis")?;
    let username_doc = doc_type.call1(("The HTTP Basic username.",))?;
    let password_doc = doc_type.call1(("The HTTP Basic password.",))?;
    let username_type = subscribe.call1((
        annotated_type.as_any(),
        (string_type.as_any(), username_doc),
    ))?;
    let password_type = subscribe.call1((
        annotated_type.as_any(),
        (string_type.as_any(), password_doc),
    ))?;

    let fields = PyDict::new(py);
    fields.set_item("__module__", "fastapi.security.http")?;
    fields.set_item("username", (username_type, ellipsis.clone()))?;
    fields.set_item("password", (password_type, ellipsis))?;
    pydantic
        .getattr("create_model")?
        .call(("HTTPBasicCredentials",), Some(&fields))
        .map(Bound::unbind)
}

fn create_http_basic_model(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let pydantic = py.import("pydantic")?;
    let string_type = py.get_type::<PyString>();
    let optional_string = optional_type(py, string_type.as_any())?;
    let type_field_arguments = PyDict::new(py);
    type_field_arguments.set_item("default", "http")?;
    type_field_arguments.set_item("alias", "type")?;
    let type_field = pydantic
        .getattr("Field")?
        .call((), Some(&type_field_arguments))?;

    let fields = PyDict::new(py);
    fields.set_item("__module__", "fastapi.openapi.models")?;
    fields.set_item("type_", (string_type.as_any(), type_field))?;
    fields.set_item("description", (optional_string, py.None()))?;
    fields.set_item("scheme", string_type.as_any())?;
    pydantic
        .getattr("create_model")?
        .call(("HTTPBase",), Some(&fields))
        .map(Bound::unbind)
}

fn create_oauth2_password_models(py: Python<'_>) -> PyResult<(Py<PyAny>, Py<PyAny>, Py<PyAny>)> {
    let pydantic = py.import("pydantic")?;
    let typing = py.import("typing")?;
    let string_type = py.get_type::<PyString>();
    let optional_string = optional_type(py, string_type.as_any())?;
    let string_mapping = typing
        .getattr("Dict")?
        .getattr("__getitem__")?
        .call1(((string_type.as_any(), string_type.as_any()),))?;

    let password_flow_fields = PyDict::new(py);
    password_flow_fields.set_item("__module__", "fastapi.openapi.models")?;
    password_flow_fields.set_item("refreshUrl", (optional_string.clone(), py.None()))?;
    password_flow_fields.set_item("scopes", (string_mapping, PyDict::new(py)))?;
    password_flow_fields.set_item("tokenUrl", string_type.as_any())?;
    let password_flow_model = pydantic
        .getattr("create_model")?
        .call(("OAuthFlowPassword",), Some(&password_flow_fields))?;

    let optional_password_flow = optional_type(py, password_flow_model.as_any())?;
    let flows_fields = PyDict::new(py);
    flows_fields.set_item("__module__", "fastapi.openapi.models")?;
    flows_fields.set_item("password", (optional_password_flow, py.None()))?;
    let flows_model = pydantic
        .getattr("create_model")?
        .call(("OAuthFlows",), Some(&flows_fields))?;

    let type_field_arguments = PyDict::new(py);
    type_field_arguments.set_item("default", "oauth2")?;
    type_field_arguments.set_item("alias", "type")?;
    let type_field = pydantic
        .getattr("Field")?
        .call((), Some(&type_field_arguments))?;
    let optional_description = optional_type(py, string_type.as_any())?;
    let oauth2_fields = PyDict::new(py);
    oauth2_fields.set_item("__module__", "fastapi.openapi.models")?;
    oauth2_fields.set_item("type_", (string_type.as_any(), type_field))?;
    oauth2_fields.set_item("description", (optional_description, py.None()))?;
    oauth2_fields.set_item("flows", flows_model.as_any())?;
    let oauth2_model = pydantic
        .getattr("create_model")?
        .call(("OAuth2",), Some(&oauth2_fields))?;

    Ok((
        password_flow_model.unbind(),
        flows_model.unbind(),
        oauth2_model.unbind(),
    ))
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

fn make_not_authenticated_error(instance: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    let exception_type = instance
        .get_type()
        .getattr("_fastapi_rs_http_exception_type")?;
    let headers = instance.call_method0("make_authenticate_headers")?;
    let exception_arguments = PyDict::new(instance.py());
    exception_arguments.set_item("status_code", 401)?;
    exception_arguments.set_item("detail", "Not authenticated")?;
    exception_arguments.set_item("headers", headers)?;
    exception_type
        .call((), Some(&exception_arguments))
        .map(Bound::unbind)
}

/// Register the reviewed native HTTP bearer authentication surface.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let credentials_type = create_credentials_model(py)?;
    module.add("HTTPAuthorizationCredentials", credentials_type.bind(py))?;
    let model_type = create_http_bearer_model(py)?;
    module.add("_HTTPBearerModel", model_type.bind(py))?;
    let basic_credentials_type = create_http_basic_credentials_model(py)?;
    module.add("HTTPBasicCredentials", basic_credentials_type.bind(py))?;
    let basic_model_type = create_http_basic_model(py)?;
    module.add("_HTTPBasicModel", basic_model_type.bind(py))?;
    let (password_flow_model, flows_model, oauth2_model) = create_oauth2_password_models(py)?;
    module.add("_OAuth2PasswordFlowModel", password_flow_model.bind(py))?;
    module.add("_OAuth2FlowsModel", flows_model.bind(py))?;
    module.add("_OAuth2PasswordBearerModel", oauth2_model.bind(py))?;
    let exception_type = module.getattr("HTTPException")?;

    module.add_class::<PyHttpBearer>()?;
    let http_bearer_type = py.get_type::<PyHttpBearer>();
    attach_dependency_introspection(py, &http_bearer_type)?;
    http_bearer_type.setattr("_fastapi_rs_credentials_type", credentials_type.bind(py))?;
    http_bearer_type.setattr("_fastapi_rs_http_exception_type", exception_type.clone())?;

    module.add_class::<PyHttpBasic>()?;
    let http_basic_type = py.get_type::<PyHttpBasic>();
    attach_dependency_introspection(py, &http_basic_type)?;
    http_basic_type.setattr(
        "_fastapi_rs_credentials_type",
        basic_credentials_type.bind(py),
    )?;
    http_basic_type.setattr("_fastapi_rs_http_exception_type", exception_type.clone())?;

    module.add_class::<PyHttpDigest>()?;
    let http_digest_type = py.get_type::<PyHttpDigest>();
    attach_dependency_introspection(py, &http_digest_type)?;
    http_digest_type.setattr("_fastapi_rs_credentials_type", credentials_type.bind(py))?;
    http_digest_type.setattr("_fastapi_rs_http_exception_type", exception_type.clone())?;

    module.add_class::<PyOAuth2PasswordBearer>()?;
    let oauth2_password_bearer_type = py.get_type::<PyOAuth2PasswordBearer>();
    attach_dependency_introspection(py, &oauth2_password_bearer_type)?;
    oauth2_password_bearer_type.setattr("_fastapi_rs_http_exception_type", exception_type)?;
    Ok(())
}

/// Check whether `value` inherits a native FastAPI security call implementation.
pub(crate) fn is_native_async_callable(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    let bearer_namespace = py.get_type::<PyHttpBearer>().getattr("__dict__")?;
    let bearer_call = bearer_namespace.get_item("__call__")?;
    let basic_namespace = py.get_type::<PyHttpBasic>().getattr("__dict__")?;
    let basic_call = basic_namespace.get_item("__call__")?;
    let digest_namespace = py.get_type::<PyHttpDigest>().getattr("__dict__")?;
    let digest_call = digest_namespace.get_item("__call__")?;
    let oauth2_namespace = py
        .get_type::<PyOAuth2PasswordBearer>()
        .getattr("__dict__")?;
    let oauth2_call = oauth2_namespace.get_item("__call__")?;
    let mro = value.get_type().getattr("__mro__")?;
    for owner in mro.try_iter()? {
        let owner = owner?;
        let namespace = owner.getattr("__dict__")?;
        if namespace.contains("__call__")? {
            let call = namespace.get_item("__call__")?;
            return Ok(call.is(&bearer_call)
                || call.is(&basic_call)
                || call.is(&digest_call)
                || call.is(&oauth2_call));
        }
    }
    Ok(false)
}
