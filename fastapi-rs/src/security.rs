//! Native FastAPI security primitives.

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};
use base64::Engine;
use base64::engine::general_purpose::{GeneralPurpose, GeneralPurposeConfig};
use pyo3::exceptions::PyRuntimeError;
use pyo3::types::{PyBool, PyDict, PyList, PyString, PyType};
use pyo3::{PyClassInitializer, prelude::*};

static PYTHON_COMPATIBLE_STANDARD_BASE64: GeneralPurpose = GeneralPurpose::new(
    &base64::alphabet::STANDARD,
    GeneralPurposeConfig::new().with_decode_allow_trailing_bits(true),
);

#[pyclass(
    name = "SecurityBase",
    module = "fastapi.security.base",
    subclass,
    dict
)]
struct PySecurityBase;

#[pymethods]
impl PySecurityBase {
    #[new]
    fn new() -> Self {
        Self
    }
}

#[pyclass(
    name = "APIKeyBase",
    module = "fastapi.security.api_key",
    extends = PySecurityBase,
    subclass,
    dict
)]
struct PyApiKeyBase {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
    scheme_name_is_default: bool,
    auto_error: Py<PyAny>,
}

#[derive(Clone, Copy)]
enum ApiKeyInputKind {
    Header,
    Query,
    Cookie,
}

struct ApiKeyModels {
    security_scheme_type: Py<PyAny>,
    api_key_in_type: Py<PyAny>,
    base_model_type: Py<PyAny>,
    security_base_model_type: Py<PyAny>,
    api_key_model_type: Py<PyAny>,
}

#[pyclass(
    name = "APIKeyHeader",
    module = "fastapi.security.api_key",
    extends = PyApiKeyBase,
    subclass,
    dict
)]
struct PyApiKeyHeader;

#[pyclass(
    name = "APIKeyQuery",
    module = "fastapi.security.api_key",
    extends = PyApiKeyBase,
    subclass,
    dict
)]
struct PyApiKeyQuery;

#[pyclass(
    name = "APIKeyCookie",
    module = "fastapi.security.api_key",
    extends = PyApiKeyBase,
    subclass,
    dict
)]
struct PyApiKeyCookie;

#[pymethods]
impl PyApiKeyBase {
    #[new]
    #[pyo3(signature = (location, name, description, scheme_name, auto_error))]
    fn new(
        py: Python<'_>,
        location: Py<PyAny>,
        name: Py<PyAny>,
        description: Py<PyAny>,
        scheme_name: Py<PyAny>,
        auto_error: Py<PyAny>,
    ) -> PyResult<PyClassInitializer<Self>> {
        let model =
            create_api_key_model(py, location.bind(py), name.bind(py), description.bind(py))?;
        let scheme_name_is_default = !scheme_name.bind(py).is_truthy()?;
        Ok(PyClassInitializer::from(PySecurityBase).add_subclass(Self {
            model,
            scheme_name,
            scheme_name_is_default,
            auto_error,
        }))
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
        let (stored, scheme_name_is_default) = {
            let borrowed = instance.borrow();
            (
                borrowed.scheme_name.clone_ref(py),
                borrowed.scheme_name_is_default,
            )
        };
        if !scheme_name_is_default {
            return Ok(stored);
        }
        let class_name = instance.get_type().name()?.to_string();
        Ok(PyString::new(py, &class_name).unbind().into_any())
    }

    #[setter]
    fn set_scheme_name(&mut self, scheme_name: Py<PyAny>) {
        self.scheme_name = scheme_name;
        self.scheme_name_is_default = false;
    }

    #[getter]
    fn auto_error(&self, py: Python<'_>) -> Py<PyAny> {
        self.auto_error.clone_ref(py)
    }

    #[setter]
    fn set_auto_error(&mut self, auto_error: Py<PyAny>) {
        self.auto_error = auto_error;
    }

    fn make_not_authenticated_error(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let instance = slf.bind(py);
        let exception_type = instance
            .get_type()
            .getattr("_fastapi_rs_http_exception_type")?;
        let headers = PyDict::new(py);
        headers.set_item("WWW-Authenticate", "APIKey")?;
        let arguments = PyDict::new(py);
        arguments.set_item("status_code", 401)?;
        arguments.set_item("detail", "Not authenticated")?;
        arguments.set_item("headers", headers)?;
        exception_type.call((), Some(&arguments)).map(Bound::unbind)
    }

    fn check_api_key(slf: Py<Self>, py: Python<'_>, api_key: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let instance = slf.bind(py);
        if !api_key.bind(py).is_truthy()? {
            let auto_error = instance.borrow().auto_error.clone_ref(py);
            if auto_error.bind(py).is_truthy()? {
                let error = instance.call_method0("make_not_authenticated_error")?;
                return Err(PyErr::from_value(error));
            }
            return Ok(py.None());
        }
        Ok(api_key)
    }
}

#[pymethods]
impl PyApiKeyHeader {
    #[new]
    #[pyo3(signature = (*, name, scheme_name=None, description=None, auto_error=api_key_auto_error_default()))]
    fn new(
        py: Python<'_>,
        name: Py<PyAny>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: Py<PyAny>,
    ) -> PyResult<PyClassInitializer<Self>> {
        let base = create_api_key_initializer(
            py,
            ApiKeyInputKind::Header,
            name,
            scheme_name,
            description,
            auto_error,
        )?;
        Ok(base.add_subclass(Self))
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            ApiKeyCall {
                security: slf.into_any(),
                request,
                input_kind: ApiKeyInputKind::Header,
            },
        )
    }
}

#[pymethods]
impl PyApiKeyQuery {
    #[new]
    #[pyo3(signature = (*, name, scheme_name=None, description=None, auto_error=api_key_auto_error_default()))]
    fn new(
        py: Python<'_>,
        name: Py<PyAny>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: Py<PyAny>,
    ) -> PyResult<PyClassInitializer<Self>> {
        let base = create_api_key_initializer(
            py,
            ApiKeyInputKind::Query,
            name,
            scheme_name,
            description,
            auto_error,
        )?;
        Ok(base.add_subclass(Self))
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            ApiKeyCall {
                security: slf.into_any(),
                request,
                input_kind: ApiKeyInputKind::Query,
            },
        )
    }
}

#[pymethods]
impl PyApiKeyCookie {
    #[new]
    #[pyo3(signature = (*, name, scheme_name=None, description=None, auto_error=api_key_auto_error_default()))]
    fn new(
        py: Python<'_>,
        name: Py<PyAny>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: Py<PyAny>,
    ) -> PyResult<PyClassInitializer<Self>> {
        let base = create_api_key_initializer(
            py,
            ApiKeyInputKind::Cookie,
            name,
            scheme_name,
            description,
            auto_error,
        )?;
        Ok(base.add_subclass(Self))
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            ApiKeyCall {
                security: slf.into_any(),
                request,
                input_kind: ApiKeyInputKind::Cookie,
            },
        )
    }
}

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

#[derive(Clone, Copy)]
enum ApiKeyIntrospectionKind {
    Annotations,
    Signature,
}

#[pyclass]
struct ApiKeyIntrospectionDescriptor {
    kind: ApiKeyIntrospectionKind,
}

#[pymethods]
impl ApiKeyIntrospectionDescriptor {
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
            ApiKeyIntrospectionKind::Annotations => api_key_dependency_annotations(py),
            ApiKeyIntrospectionKind::Signature => api_key_dependency_signature(py),
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

#[pyclass(name = "HTTPBase", module = "fastapi.security.http", subclass, dict)]
struct PyHttpBase {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
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

#[pymethods]
impl PyHttpBase {
    #[new]
    #[pyo3(signature = (*, scheme, scheme_name=None, description=None, auto_error=true))]
    fn new(
        py: Python<'_>,
        scheme: Py<PyAny>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: bool,
    ) -> PyResult<Self> {
        let module = py.import("fastapi_rs._core")?;
        let model_type = module.getattr("_HTTPBasicModel")?;
        let model_arguments = PyDict::new(py);
        model_arguments.set_item("scheme", scheme)?;
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
            HttpBaseCall {
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

#[pyclass(name = "OAuth2", module = "fastapi.security.oauth2", subclass, dict)]
struct PyOAuth2 {
    model: Py<PyAny>,
    scheme_name: Py<PyAny>,
    auto_error: bool,
}

#[pymethods]
impl PyOAuth2 {
    #[new]
    #[pyo3(signature = (*, flows=None, scheme_name=None, description=None, auto_error=true))]
    fn new(
        py: Python<'_>,
        flows: Option<Py<PyAny>>,
        scheme_name: Option<Py<PyAny>>,
        description: Option<Py<PyAny>>,
        auto_error: bool,
    ) -> PyResult<Self> {
        let module = py.import("fastapi_rs._core")?;
        let model_type = module.getattr("_OAuth2Model")?;
        let model_arguments = PyDict::new(py);
        model_arguments.set_item(
            "flows",
            flows.unwrap_or_else(|| PyDict::new(py).unbind().into_any()),
        )?;
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

    fn make_not_authenticated_error(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let exception_type = slf
            .bind(py)
            .get_type()
            .getattr("_fastapi_rs_http_exception_type")?;
        let headers = PyDict::new(py);
        headers.set_item("WWW-Authenticate", "Bearer")?;
        let arguments = PyDict::new(py);
        arguments.set_item("status_code", 401)?;
        arguments.set_item("detail", "Not authenticated")?;
        arguments.set_item("headers", headers)?;
        exception_type.call((), Some(&arguments)).map(Bound::unbind)
    }

    fn __call__(slf: Py<Self>, py: Python<'_>, request: Py<PyAny>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            OAuth2Call {
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

        let model_type = module.getattr("_OAuth2Model")?;
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

struct HttpBaseCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

impl AwaitableStateMachine for HttpBaseCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "HTTPBase dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let headers = self.request.bind(py).getattr("headers")?;
        let authorization = headers.call_method1("get", ("Authorization",))?;
        let authorization_is_present = authorization.is_truthy()?;
        let (scheme, credentials) = authorization_parts(&authorization)?;
        if !authorization_is_present || scheme.is_empty() || credentials.is_empty() {
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

struct OAuth2Call {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

impl AwaitableStateMachine for OAuth2Call {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "OAuth2 dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let headers = self.request.bind(py).getattr("headers")?;
        let authorization = headers.call_method1("get", ("Authorization",))?;
        if !authorization.is_truthy()? {
            if security.getattr("auto_error")?.is_truthy()? {
                let exception = security.call_method0("make_not_authenticated_error")?;
                return Err(PyErr::from_value(exception));
            }
            return Ok(MachineAction::Complete(py.None()));
        }

        Ok(MachineAction::Complete(authorization.unbind()))
    }
}

struct OAuth2PasswordBearerCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
}

struct ApiKeyCall {
    security: Py<PyAny>,
    request: Py<PyAny>,
    input_kind: ApiKeyInputKind,
}

impl AwaitableStateMachine for ApiKeyCall {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        if !matches!(input, MachineResume::Start) {
            return Err(PyRuntimeError::new_err(
                "API key dependency resumed more than once",
            ));
        }

        let security = self.security.bind(py);
        let request = self.request.bind(py);
        let model = security.getattr("model")?;
        let name = model.getattr("name")?;
        let source = match self.input_kind {
            ApiKeyInputKind::Header => request.getattr("headers")?,
            ApiKeyInputKind::Query => request.getattr("query_params")?,
            ApiKeyInputKind::Cookie => request.getattr("cookies")?,
        };
        let api_key = source.call_method1("get", (name,))?;
        security
            .call_method1("check_api_key", (api_key,))
            .map(|value| MachineAction::Complete(value.unbind()))
    }
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

fn api_key_dependency_annotations(py: Python<'_>) -> PyResult<Py<PyAny>> {
    let annotations = PyDict::new(py);
    annotations.set_item(
        "request",
        py.import("starlette.requests")?.getattr("Request")?,
    )?;
    annotations.set_item("return", api_key_return_annotation(py)?)?;
    Ok(annotations.unbind().into_any())
}

fn api_key_dependency_signature(py: Python<'_>) -> PyResult<Py<PyAny>> {
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
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", api_key_return_annotation(py)?)?;
    inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))
        .map(Bound::unbind)
}

fn api_key_return_annotation<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
    let string_type = py.get_type::<PyString>();
    let none_type = py.import("types")?.getattr("NoneType")?;
    py.import("operator")?
        .getattr("or_")?
        .call1((string_type.as_any(), none_type))
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

fn attach_api_key_dependency_introspection(
    py: Python<'_>,
    class: &Bound<'_, PyType>,
) -> PyResult<()> {
    class.setattr(
        "__annotations__",
        Py::new(
            py,
            ApiKeyIntrospectionDescriptor {
                kind: ApiKeyIntrospectionKind::Annotations,
            },
        )?,
    )?;
    class.setattr(
        "__signature__",
        Py::new(
            py,
            ApiKeyIntrospectionDescriptor {
                kind: ApiKeyIntrospectionKind::Signature,
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

fn create_string_enum(py: Python<'_>, name: &str, members: &[(&str, &str)]) -> PyResult<Py<PyAny>> {
    let enum_members = PyDict::new(py);
    for (member, value) in members {
        enum_members.set_item(member, value)?;
    }
    let arguments = PyDict::new(py);
    arguments.set_item("module", "fastapi.openapi.models")?;
    py.import("enum")?
        .getattr("Enum")?
        .call((name, enum_members), Some(&arguments))
        .map(Bound::unbind)
}

fn create_api_key_models(py: Python<'_>) -> PyResult<ApiKeyModels> {
    let security_scheme_type = create_string_enum(
        py,
        "SecuritySchemeType",
        &[
            ("apiKey", "apiKey"),
            ("http", "http"),
            ("oauth2", "oauth2"),
            ("openIdConnect", "openIdConnect"),
        ],
    )?;
    let api_key_in = create_string_enum(
        py,
        "APIKeyIn",
        &[
            ("query", "query"),
            ("header", "header"),
            ("cookie", "cookie"),
        ],
    )?;

    let pydantic = py.import("pydantic")?;
    let extra_config = PyDict::new(py);
    extra_config.set_item("extra", "allow")?;
    let base_fields = PyDict::new(py);
    base_fields.set_item("__module__", "fastapi.openapi.models")?;
    base_fields.set_item("__config__", extra_config)?;
    let base_model = pydantic
        .getattr("create_model")?
        .call(("BaseModelWithConfig",), Some(&base_fields))?;

    let string_type = py.get_type::<PyString>();
    let optional_string = optional_type(py, string_type.as_any())?;
    let type_field_arguments = PyDict::new(py);
    type_field_arguments.set_item("alias", "type")?;
    let required_type_field = pydantic
        .getattr("Field")?
        .call((), Some(&type_field_arguments))?;
    let security_base_fields = PyDict::new(py);
    security_base_fields.set_item("__module__", "fastapi.openapi.models")?;
    security_base_fields.set_item("__base__", base_model.as_any())?;
    security_base_fields.set_item(
        "type_",
        (security_scheme_type.bind(py).as_any(), required_type_field),
    )?;
    security_base_fields.set_item("description", (optional_string, py.None()))?;
    let security_base_model = pydantic
        .getattr("create_model")?
        .call(("SecurityBase",), Some(&security_base_fields))?;

    let api_key_type = security_scheme_type.bind(py).getattr("apiKey")?;
    let api_key_type_field_arguments = PyDict::new(py);
    api_key_type_field_arguments.set_item("default", api_key_type)?;
    api_key_type_field_arguments.set_item("alias", "type")?;
    let api_key_type_field = pydantic
        .getattr("Field")?
        .call((), Some(&api_key_type_field_arguments))?;
    let api_key_location_field_arguments = PyDict::new(py);
    api_key_location_field_arguments.set_item("alias", "in")?;
    let api_key_location_field = pydantic
        .getattr("Field")?
        .call((), Some(&api_key_location_field_arguments))?;
    let api_key_fields = PyDict::new(py);
    api_key_fields.set_item("__module__", "fastapi.openapi.models")?;
    api_key_fields.set_item("__base__", security_base_model.as_any())?;
    api_key_fields.set_item(
        "type_",
        (security_scheme_type.bind(py).as_any(), api_key_type_field),
    )?;
    api_key_fields.set_item(
        "in_",
        (api_key_in.bind(py).as_any(), api_key_location_field),
    )?;
    api_key_fields.set_item("name", string_type.as_any())?;
    let api_key_model = pydantic
        .getattr("create_model")?
        .call(("APIKey",), Some(&api_key_fields))?;

    Ok(ApiKeyModels {
        security_scheme_type,
        api_key_in_type: api_key_in,
        base_model_type: base_model.unbind(),
        security_base_model_type: security_base_model.unbind(),
        api_key_model_type: api_key_model.unbind(),
    })
}

fn create_api_key_model(
    py: Python<'_>,
    location: &Bound<'_, PyAny>,
    name: &Bound<'_, PyAny>,
    description: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let model_type = py.import("fastapi_rs._core")?.getattr("_APIKeyModel")?;
    let arguments = PyDict::new(py);
    arguments.set_item("in", location)?;
    arguments.set_item("name", name)?;
    arguments.set_item("description", description)?;
    model_type.call((), Some(&arguments)).map(Bound::unbind)
}

fn api_key_location_name(location: ApiKeyInputKind) -> &'static str {
    match location {
        ApiKeyInputKind::Header => "header",
        ApiKeyInputKind::Query => "query",
        ApiKeyInputKind::Cookie => "cookie",
    }
}

fn create_api_key_initializer(
    py: Python<'_>,
    location: ApiKeyInputKind,
    name: Py<PyAny>,
    scheme_name: Option<Py<PyAny>>,
    description: Option<Py<PyAny>>,
    auto_error: Py<PyAny>,
) -> PyResult<PyClassInitializer<PyApiKeyBase>> {
    let api_key_in = py.import("fastapi_rs._core")?.getattr("_APIKeyIn")?;
    let location = api_key_in.getattr(api_key_location_name(location))?;
    let description = description.unwrap_or_else(|| py.None());
    let model = create_api_key_model(py, &location, name.bind(py), description.bind(py))?;
    let scheme_name = scheme_name.unwrap_or_else(|| py.None());
    let scheme_name_is_default = !scheme_name.bind(py).is_truthy()?;
    Ok(
        PyClassInitializer::from(PySecurityBase).add_subclass(PyApiKeyBase {
            model,
            scheme_name,
            scheme_name_is_default,
            auto_error,
        }),
    )
}

fn api_key_auto_error_default() -> Py<PyAny> {
    Python::attach(|py| PyBool::new(py, true).to_owned().into_any().unbind())
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
    let api_key_models = create_api_key_models(py)?;
    module.add(
        "SecuritySchemeType",
        api_key_models.security_scheme_type.bind(py),
    )?;
    module.add("APIKeyIn", api_key_models.api_key_in_type.bind(py))?;
    module.add("_APIKeyIn", api_key_models.api_key_in_type.bind(py))?;
    module.add(
        "BaseModelWithConfig",
        api_key_models.base_model_type.bind(py),
    )?;
    module.add(
        "OpenAPISecurityBaseModel",
        api_key_models.security_base_model_type.bind(py),
    )?;
    module.add(
        "SecurityBaseModel",
        api_key_models.security_base_model_type.bind(py),
    )?;
    module.add("APIKey", api_key_models.api_key_model_type.bind(py))?;
    module.add("_APIKeyModel", api_key_models.api_key_model_type.bind(py))?;

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
    module.add("_OAuth2Model", oauth2_model.bind(py))?;
    let exception_type = module.getattr("HTTPException")?;
    let starlette_http_exception_type = py
        .import("starlette.exceptions")?
        .getattr("HTTPException")?;

    module.add_class::<PySecurityBase>()?;
    let security_base_type = py.get_type::<PySecurityBase>();
    let security_base_annotations = PyDict::new(py);
    security_base_annotations
        .set_item("model", api_key_models.security_base_model_type.bind(py))?;
    security_base_annotations.set_item("scheme_name", py.get_type::<PyString>())?;
    security_base_type.setattr("__annotations__", security_base_annotations)?;

    module.add_class::<PyApiKeyBase>()?;
    let api_key_base_type = py.get_type::<PyApiKeyBase>();
    let api_key_base_annotations = PyDict::new(py);
    api_key_base_annotations.set_item("model", api_key_models.api_key_model_type.bind(py))?;
    api_key_base_type.setattr("__annotations__", api_key_base_annotations)?;
    api_key_base_type.setattr(
        "_fastapi_rs_http_exception_type",
        starlette_http_exception_type,
    )?;

    module.add_class::<PyApiKeyHeader>()?;
    let api_key_header_type = py.get_type::<PyApiKeyHeader>();
    attach_api_key_dependency_introspection(py, &api_key_header_type)?;

    module.add_class::<PyApiKeyQuery>()?;
    let api_key_query_type = py.get_type::<PyApiKeyQuery>();
    attach_api_key_dependency_introspection(py, &api_key_query_type)?;

    module.add_class::<PyApiKeyCookie>()?;
    let api_key_cookie_type = py.get_type::<PyApiKeyCookie>();
    attach_api_key_dependency_introspection(py, &api_key_cookie_type)?;

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

    module.add_class::<PyHttpBase>()?;
    let http_base_type = py.get_type::<PyHttpBase>();
    attach_dependency_introspection(py, &http_base_type)?;
    http_base_type.setattr("_fastapi_rs_credentials_type", credentials_type.bind(py))?;
    http_base_type.setattr("_fastapi_rs_http_exception_type", exception_type.clone())?;

    module.add_class::<PyHttpDigest>()?;
    let http_digest_type = py.get_type::<PyHttpDigest>();
    attach_dependency_introspection(py, &http_digest_type)?;
    http_digest_type.setattr("_fastapi_rs_credentials_type", credentials_type.bind(py))?;
    http_digest_type.setattr("_fastapi_rs_http_exception_type", exception_type.clone())?;

    module.add_class::<PyOAuth2>()?;
    let oauth2_type = py.get_type::<PyOAuth2>();
    attach_dependency_introspection(py, &oauth2_type)?;
    oauth2_type.setattr("_fastapi_rs_http_exception_type", exception_type.clone())?;

    module.add_class::<PyOAuth2PasswordBearer>()?;
    let oauth2_password_bearer_type = py.get_type::<PyOAuth2PasswordBearer>();
    attach_dependency_introspection(py, &oauth2_password_bearer_type)?;
    oauth2_password_bearer_type.setattr("_fastapi_rs_http_exception_type", exception_type)?;
    Ok(())
}

/// Return the OpenAPI scheme name and model for a native FastAPI security callable.
pub(crate) fn openapi_security_metadata(
    callable: &Bound<'_, PyAny>,
) -> PyResult<Option<(String, Py<PyAny>)>> {
    if !(callable.is_instance_of::<PyHttpBasic>()
        || callable.is_instance_of::<PyHttpBearer>()
        || callable.is_instance_of::<PyHttpBase>()
        || callable.is_instance_of::<PyHttpDigest>()
        || callable.is_instance_of::<PyApiKeyBase>()
        || callable.is_instance_of::<PyOAuth2>()
        || callable.is_instance_of::<PyOAuth2PasswordBearer>()
        || callable.is_instance_of::<PySecurityBase>())
    {
        return Ok(None);
    }
    let scheme_name = callable.getattr("scheme_name")?.extract::<String>()?;
    let model = callable.getattr("model")?.unbind();
    Ok(Some((scheme_name, model)))
}

/// Check whether `value` inherits a native FastAPI security call implementation.
pub(crate) fn is_native_async_callable(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<bool> {
    let bearer_namespace = py.get_type::<PyHttpBearer>().getattr("__dict__")?;
    let bearer_call = bearer_namespace.get_item("__call__")?;
    let basic_namespace = py.get_type::<PyHttpBasic>().getattr("__dict__")?;
    let basic_call = basic_namespace.get_item("__call__")?;
    let base_namespace = py.get_type::<PyHttpBase>().getattr("__dict__")?;
    let base_call = base_namespace.get_item("__call__")?;
    let digest_namespace = py.get_type::<PyHttpDigest>().getattr("__dict__")?;
    let digest_call = digest_namespace.get_item("__call__")?;
    let api_key_header_namespace = py.get_type::<PyApiKeyHeader>().getattr("__dict__")?;
    let api_key_header_call = api_key_header_namespace.get_item("__call__")?;
    let api_key_query_namespace = py.get_type::<PyApiKeyQuery>().getattr("__dict__")?;
    let api_key_query_call = api_key_query_namespace.get_item("__call__")?;
    let api_key_cookie_namespace = py.get_type::<PyApiKeyCookie>().getattr("__dict__")?;
    let api_key_cookie_call = api_key_cookie_namespace.get_item("__call__")?;
    let oauth2_base_namespace = py.get_type::<PyOAuth2>().getattr("__dict__")?;
    let oauth2_base_call = oauth2_base_namespace.get_item("__call__")?;
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
                || call.is(&base_call)
                || call.is(&digest_call)
                || call.is(&api_key_header_call)
                || call.is(&api_key_query_call)
                || call.is(&api_key_cookie_call)
                || call.is(&oauth2_base_call)
                || call.is(&oauth2_call));
        }
    }
    Ok(false)
}
