//! FastAPI-specific lifespan composition over Starlette-RS's ASGI runner.

use pyo3::exceptions::{PyAssertionError, PyRuntimeError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};
use std::collections::HashSet;

use crate::awaitable::{
    AwaitableStateMachine, MachineAction, MachineResume, into_python_awaitable,
};

/// Lifecycle configuration attached to a FastAPI application or APIRouter.
pub(crate) struct FastApiLifespan {
    factory: Py<PyFastApiLifespanFactory>,
}

impl FastApiLifespan {
    /// Creates FastAPI's default legacy lifecycle or stores a custom lifespan.
    pub(crate) fn new(
        py: Python<'_>,
        on_startup: Option<Py<PyAny>>,
        on_shutdown: Option<Py<PyAny>>,
        lifespan: Option<Py<PyAny>>,
    ) -> PyResult<Self> {
        let on_startup = callback_list(py, on_startup)?;
        let on_shutdown = callback_list(py, on_shutdown)?;
        let lifespan = lifespan
            .filter(|context| !context.bind(py).is_none())
            .map(|context| normalize_lifespan(py, context))
            .transpose()?;
        let factory = Py::new(
            py,
            PyFastApiLifespanFactory {
                lifespan,
                on_startup,
                on_shutdown,
                children: Vec::new(),
            },
        )?;
        Ok(Self { factory })
    }

    /// Adds an included router's handlers and nested lifespan to this router.
    pub(crate) fn include_router(&mut self, py: Python<'_>, router: &Self) -> PyResult<()> {
        let (on_startup, on_shutdown) = {
            let child = router.factory.bind(py).borrow();
            (
                child
                    .on_startup
                    .iter()
                    .map(|handler| handler.clone_ref(py))
                    .collect::<Vec<_>>(),
                child
                    .on_shutdown
                    .iter()
                    .map(|handler| handler.clone_ref(py))
                    .collect::<Vec<_>>(),
            )
        };
        let mut parent = self.factory.bind(py).borrow_mut();
        parent.on_startup.extend(on_startup);
        parent.on_shutdown.extend(on_shutdown);
        parent.children.push(router.factory.clone_ref(py));
        Ok(())
    }

    /// Checks whether an included router already contains this router.
    pub(crate) fn is_included_by(&self, py: Python<'_>, router: &Self) -> PyResult<bool> {
        let mut visited = HashSet::new();
        contains_factory(py, &self.factory, router.factory.as_ptr(), &mut visited)
    }

    /// Registers a callback for a legacy startup or shutdown event.
    pub(crate) fn add_event_handler(
        &self,
        py: Python<'_>,
        event_type: &str,
        handler: Py<PyAny>,
    ) -> PyResult<()> {
        let mut factory = self.factory.bind(py).borrow_mut();
        match event_type {
            "startup" => factory.on_startup.push(handler),
            "shutdown" => factory.on_shutdown.push(handler),
            _ => return Err(PyAssertionError::new_err("")),
        }
        Ok(())
    }

    /// Returns the decorator used by FastAPI's deprecated on_event API.
    pub(crate) fn decorator(&self, py: Python<'_>, event_type: &str) -> PyResult<Py<PyAny>> {
        Py::new(
            py,
            PyFastApiOnEventDecorator {
                factory: self.factory.clone_ref(py),
                event_type: event_type.to_owned(),
            },
        )
        .map(|decorator| decorator.into_any())
    }

    /// Returns the lifecycle factory passed to the Starlette-RS ASGI runner.
    pub(crate) fn context(&self, py: Python<'_>) -> Py<PyAny> {
        self.factory.clone_ref(py).into_any()
    }
}

#[pyclass(
    name = "_FastAPILifespanFactory",
    module = "fastapi_rs._core",
    unsendable
)]
pub(crate) struct PyFastApiLifespanFactory {
    lifespan: Option<Py<PyAny>>,
    on_startup: Vec<Py<PyAny>>,
    on_shutdown: Vec<Py<PyAny>>,
    children: Vec<Py<PyFastApiLifespanFactory>>,
}

#[pymethods]
impl PyFastApiLifespanFactory {
    fn __call__(slf: Py<Self>, py: Python<'_>, app: Py<PyAny>) -> PyResult<Py<PyAny>> {
        Py::new(
            py,
            PyFastApiLifespanContextManager {
                factory: slf,
                app,
                stack: None,
            },
        )
        .map(|manager| manager.into_any())
    }
}

#[pyclass(
    name = "_FastAPILifespanContextManager",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiLifespanContextManager {
    factory: Py<PyFastApiLifespanFactory>,
    app: Py<PyAny>,
    stack: Option<Py<PyAny>>,
}

#[pymethods]
impl PyFastApiLifespanContextManager {
    fn __aenter__(slf: Py<Self>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            FastApiLifespanEnter {
                manager: slf,
                stack: None,
                state: None,
                child_index: 0,
                pending: None,
            },
        )
    }

    fn __aexit__(
        &self,
        py: Python<'_>,
        exception_type: Py<PyAny>,
        exception: Py<PyAny>,
        traceback: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        let stack = self.stack.as_ref().ok_or_else(|| {
            PyRuntimeError::new_err("FastAPI lifespan context manager was not entered")
        })?;
        stack
            .bind(py)
            .call_method1(
                "__aexit__",
                (
                    exception_type.bind(py),
                    exception.bind(py),
                    traceback.bind(py),
                ),
            )
            .map(Bound::unbind)
    }
}

enum LifespanEnterPending {
    StackEnter,
    OwnContextEnter,
    ChildContextEnter,
    Cleanup { original: PyErr },
}

struct FastApiLifespanEnter {
    manager: Py<PyFastApiLifespanContextManager>,
    stack: Option<Py<PyAny>>,
    state: Option<Py<PyAny>>,
    child_index: usize,
    pending: Option<LifespanEnterPending>,
}

impl AwaitableStateMachine for FastApiLifespanEnter {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Error(error) => self.fail(py, error),
            input => self
                .advance(py, input)
                .or_else(|error| self.fail(py, error)),
        }
    }
}

impl FastApiLifespanEnter {
    fn advance(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => {
                let stack = py
                    .import("contextlib")?
                    .getattr("AsyncExitStack")?
                    .call0()?;
                let entered = stack.call_method0("__aenter__")?;
                self.stack = Some(stack.unbind());
                self.pending = Some(LifespanEnterPending::StackEnter);
                Ok(MachineAction::Await(entered.unbind()))
            }
            MachineResume::Value(value) => match self.pending.take() {
                Some(LifespanEnterPending::StackEnter) => self.enter_own_context(py),
                Some(LifespanEnterPending::OwnContextEnter) => {
                    self.merge_state(py, value)?;
                    self.enter_child_context(py)
                }
                Some(LifespanEnterPending::ChildContextEnter) => {
                    self.merge_state(py, value)?;
                    self.child_index += 1;
                    self.enter_child_context(py)
                }
                Some(LifespanEnterPending::Cleanup { original }) => Err(original),
                None => Err(PyRuntimeError::new_err(
                    "FastAPI lifespan context resumed without a pending operation",
                )),
            },
            MachineResume::Error(error) => Err(error),
        }
    }

    fn enter_own_context(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let (lifespan, on_startup, on_shutdown) = {
            let manager = self.manager.bind(py).borrow();
            let factory = manager.factory.bind(py).borrow();
            (
                factory
                    .lifespan
                    .as_ref()
                    .map(|context| context.clone_ref(py)),
                factory
                    .on_startup
                    .iter()
                    .map(|handler| handler.clone_ref(py))
                    .collect::<Vec<_>>(),
                factory
                    .on_shutdown
                    .iter()
                    .map(|handler| handler.clone_ref(py))
                    .collect::<Vec<_>>(),
            )
        };
        let context = match lifespan {
            Some(lifespan) => lifespan
                .bind(py)
                .call1((self.manager.bind(py).borrow().app.bind(py),))?
                .unbind(),
            None => Py::new(
                py,
                PyFastApiLegacyLifespanContextManager {
                    on_startup,
                    on_shutdown,
                },
            )?
            .into_any(),
        };
        let stack = self.stack.as_ref().ok_or_else(|| {
            PyRuntimeError::new_err("FastAPI lifespan exit stack was not initialized")
        })?;
        let entered = stack
            .bind(py)
            .call_method1("enter_async_context", (context.bind(py),))?;
        self.pending = Some(LifespanEnterPending::OwnContextEnter);
        Ok(MachineAction::Await(entered.unbind()))
    }

    fn enter_child_context(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        let child = {
            let manager = self.manager.bind(py).borrow();
            let factory = manager.factory.bind(py).borrow();
            factory
                .children
                .get(self.child_index)
                .map(|child| child.clone_ref(py))
        };
        let Some(child) = child else {
            self.manager.bind(py).borrow_mut().stack =
                self.stack.as_ref().map(|stack| stack.clone_ref(py));
            return Ok(MachineAction::Complete(
                self.state
                    .as_ref()
                    .map(|state| state.clone_ref(py))
                    .unwrap_or_else(|| py.None()),
            ));
        };
        let app = self.manager.bind(py).borrow().app.clone_ref(py);
        let context = child.bind(py).call1((app,))?;
        let stack = self.stack.as_ref().ok_or_else(|| {
            PyRuntimeError::new_err("FastAPI lifespan exit stack was not initialized")
        })?;
        let entered = stack
            .bind(py)
            .call_method1("enter_async_context", (context,))?;
        self.pending = Some(LifespanEnterPending::ChildContextEnter);
        Ok(MachineAction::Await(entered.unbind()))
    }

    fn merge_state(&mut self, py: Python<'_>, nested: Py<PyAny>) -> PyResult<()> {
        let original = self.state.take();
        if original
            .as_ref()
            .is_none_or(|state| state.bind(py).is_none())
            && nested.bind(py).is_none()
        {
            self.state = original;
            return Ok(());
        }
        let merged = PyDict::new(py);
        if !nested.bind(py).is_none() {
            merged.call_method1("update", (nested.bind(py),))?;
        }
        if let Some(original) = original.filter(|state| !state.bind(py).is_none()) {
            merged.call_method1("update", (original.bind(py),))?;
        }
        self.state = Some(merged.into_any().unbind());
        Ok(())
    }

    fn fail(&mut self, py: Python<'_>, original: PyErr) -> PyResult<MachineAction> {
        if matches!(&self.pending, Some(LifespanEnterPending::Cleanup { .. })) {
            return Err(original);
        }
        let Some(stack) = self.stack.as_ref() else {
            return Err(original);
        };
        let exception = original.value(py);
        let exception_type = exception.getattr("__class__")?;
        let traceback = exception.getattr("__traceback__")?;
        let cleanup = stack
            .bind(py)
            .call_method1("__aexit__", (exception_type, exception, traceback))?;
        self.pending = Some(LifespanEnterPending::Cleanup { original });
        Ok(MachineAction::Await(cleanup.unbind()))
    }
}

#[pyclass(
    name = "_FastAPILegacyLifespanContextManager",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiLegacyLifespanContextManager {
    on_startup: Vec<Py<PyAny>>,
    on_shutdown: Vec<Py<PyAny>>,
}

#[pymethods]
impl PyFastApiLegacyLifespanContextManager {
    fn __aenter__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            LifecycleHandlers {
                handlers: self
                    .on_startup
                    .iter()
                    .map(|handler| handler.clone_ref(py))
                    .collect(),
                index: 0,
            },
        )
    }

    fn __aexit__(
        &self,
        py: Python<'_>,
        _exception_type: Py<PyAny>,
        _exception: Py<PyAny>,
        _traceback: Py<PyAny>,
    ) -> PyResult<Py<PyAny>> {
        into_python_awaitable(
            py,
            LifecycleHandlers {
                handlers: self
                    .on_shutdown
                    .iter()
                    .map(|handler| handler.clone_ref(py))
                    .collect(),
                index: 0,
            },
        )
    }
}

struct LifecycleHandlers {
    handlers: Vec<Py<PyAny>>,
    index: usize,
}

impl AwaitableStateMachine for LifecycleHandlers {
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction> {
        match input {
            MachineResume::Start => self.advance(py),
            MachineResume::Value(_) => {
                self.index += 1;
                self.advance(py)
            }
            MachineResume::Error(error) => Err(error),
        }
    }
}

impl LifecycleHandlers {
    fn advance(&mut self, py: Python<'_>) -> PyResult<MachineAction> {
        while let Some(handler) = self.handlers.get(self.index) {
            let handler = handler.bind(py);
            let async_callable = is_async_callable(py, handler)?;
            let result = handler.call0()?;
            if async_callable {
                return Ok(MachineAction::Await(result.unbind()));
            }
            self.index += 1;
        }
        Ok(MachineAction::Complete(py.None()))
    }
}

fn is_async_callable(py: Python<'_>, handler: &Bound<'_, PyAny>) -> PyResult<bool> {
    let inspect = py.import("inspect")?;
    let is_coroutine_function = inspect.getattr("iscoroutinefunction")?;
    if is_coroutine_function.call1((handler,))?.extract::<bool>()? {
        return Ok(true);
    }
    let call_method =
        py.import("builtins")?
            .getattr("getattr")?
            .call1((handler, "__call__", py.None()))?;
    if call_method.is_none() {
        return Ok(false);
    }
    is_coroutine_function
        .call1((call_method,))?
        .extract::<bool>()
}

fn contains_factory(
    py: Python<'_>,
    factory: &Py<PyFastApiLifespanFactory>,
    target: *mut pyo3::ffi::PyObject,
    visited: &mut HashSet<*mut pyo3::ffi::PyObject>,
) -> PyResult<bool> {
    let identity = factory.as_ptr();
    if identity == target {
        return Ok(true);
    }
    if !visited.insert(identity) {
        return Ok(false);
    }
    let children = factory
        .bind(py)
        .borrow()
        .children
        .iter()
        .map(|child| child.clone_ref(py))
        .collect::<Vec<_>>();
    for child in children {
        if contains_factory(py, &child, target, visited)? {
            return Ok(true);
        }
    }
    Ok(false)
}

#[pyclass(
    name = "_FastAPIOnEventDecorator",
    module = "fastapi_rs._core",
    unsendable
)]
struct PyFastApiOnEventDecorator {
    factory: Py<PyFastApiLifespanFactory>,
    event_type: String,
}

#[pymethods]
impl PyFastApiOnEventDecorator {
    fn __call__(&self, py: Python<'_>, handler: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let mut factory = self.factory.bind(py).borrow_mut();
        match self.event_type.as_str() {
            "startup" => factory.on_startup.push(handler.clone_ref(py)),
            "shutdown" => factory.on_shutdown.push(handler.clone_ref(py)),
            _ => return Err(PyAssertionError::new_err("")),
        }
        Ok(handler)
    }
}

/// Emits the FastAPI deprecation notice used by FastAPI.on_event.
pub(crate) fn warn_on_event(py: Python<'_>, application: bool) -> PyResult<()> {
    const MESSAGE: &str = "\n        on_event is deprecated, use lifespan event handlers instead.\n\n        Read more about it in the\n        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).\n        ";
    let warnings = py.import("warnings")?;
    let category = py.get_type::<pyo3::exceptions::PyDeprecationWarning>();
    let kwargs = PyDict::new(py);
    kwargs.set_item("stacklevel", 1)?;
    warnings
        .getattr("warn")?
        .call((MESSAGE, category.clone()), Some(&kwargs))?;
    if application {
        warnings.getattr("warn_explicit")?.call1((
            MESSAGE,
            category,
            "fastapi/applications.py",
            4681,
        ))?;
    }
    Ok(())
}

/// Registers FastAPI's native lifespan adapters.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyFastApiLifespanFactory>()?;
    module.add_class::<PyFastApiLifespanContextManager>()?;
    module.add_class::<PyFastApiLegacyLifespanContextManager>()?;
    module.add_class::<PyFastApiOnEventDecorator>()?;
    Ok(())
}

fn callback_list(py: Python<'_>, callbacks: Option<Py<PyAny>>) -> PyResult<Vec<Py<PyAny>>> {
    let Some(callbacks) = callbacks.filter(|callbacks| !callbacks.bind(py).is_none()) else {
        return Ok(Vec::new());
    };
    py.import("builtins")?
        .getattr("list")?
        .call1((callbacks,))?
        .extract()
}

fn normalize_lifespan(py: Python<'_>, lifespan: Py<PyAny>) -> PyResult<Py<PyAny>> {
    let inspect = py.import("inspect")?;
    let async_generator = inspect
        .getattr("isasyncgenfunction")?
        .call1((lifespan.bind(py),))?
        .extract::<bool>()?;
    let generator = if async_generator {
        false
    } else {
        inspect
            .getattr("isgeneratorfunction")?
            .call1((lifespan.bind(py),))?
            .extract::<bool>()?
    };
    if !async_generator && !generator {
        return Ok(lifespan);
    }

    let warning_message = if async_generator {
        "async generator function lifespans are deprecated, use an @contextlib.asynccontextmanager function instead"
    } else {
        "generator function lifespans are deprecated, use an @contextlib.asynccontextmanager function instead"
    };
    let warnings = py.import("warnings")?;
    let warning_category = py
        .import("starlette.exceptions")?
        .getattr("StarletteDeprecationWarning")?;
    let warning_context = warnings.getattr("catch_warnings")?.call0()?;
    warning_context.call_method0("__enter__")?;
    let wrapped = (|| {
        let filter_options = PyDict::new(py);
        filter_options.set_item("message", warning_message)?;
        filter_options.set_item("category", warning_category)?;
        warnings
            .getattr("filterwarnings")?
            .call(("ignore",), Some(&filter_options))?;
        let router_options = PyDict::new(py);
        router_options.set_item("lifespan", lifespan.bind(py))?;
        let router = py
            .import("starlette.routing")?
            .getattr("Router")?
            .call((), Some(&router_options))?;
        router.getattr("lifespan_context").map(Bound::unbind)
    })();
    let restored = warning_context.call_method1("__exit__", (py.None(), py.None(), py.None()));
    match wrapped {
        Ok(context) => {
            restored?;
            Ok(context)
        }
        Err(error) => {
            let _ = restored;
            Err(error)
        }
    }
}
