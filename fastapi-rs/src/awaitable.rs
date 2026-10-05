//! Drive Python awaitables from a Rust-owned continuation.
//!
//! [`AwaitableStateMachine`] keeps framework decisions and sequencing in Rust. When
//! it returns [`MachineAction::Await`], [`into_python_awaitable`] obtains the
//! object's await iterator and forwards each yielded Future unchanged. The
//! task and event loop which awaited the returned object remain responsible for
//! scheduling those Futures; this module creates no executor or event loop.
//!
//! Values and exceptions sent back by the task resume the active Python iterator.
//! A delegated iterator's `StopIteration.value` resumes the Rust state machine as
//! [`MachineResume::Value`]. Other exceptions, including task cancellation, arrive
//! as [`MachineResume::Error`]. Closing the returned iterator forwards
//! `GeneratorExit` through the active await and into the state machine.

use pyo3::exceptions::{
    PyBaseException, PyGeneratorExit, PyRuntimeError, PyStopIteration, PyTypeError,
};
use pyo3::prelude::*;
use pyo3::types::{PyIterator, PyTraceback, PyType};

/// Input delivered when a Rust continuation starts or an awaited object resumes.
pub(crate) enum MachineResume {
    /// Start the continuation before any delegated awaitable has run.
    Start,
    /// An awaited Python object completed with this value.
    Value(Py<PyAny>),
    /// An awaited Python object raised this exception, or the task threw it in.
    Error(PyErr),
}

/// The next action requested by a Rust continuation.
pub(crate) enum MachineAction {
    /// Await this Python awaitable, yielding its Futures to the caller's event loop.
    Await(Py<PyAny>),
    /// Deliver this exception back to the active state machine as an await failure.
    #[cfg(feature = "fault-injection")]
    Raise(PyErr),
    /// Finish the outer awaitable with this value.
    Complete(Py<PyAny>),
}

/// A Rust-owned continuation whose asynchronous boundary is driven by Python.
///
/// Implementations must advance their own state in `resume` and return the next
/// operation. For an awaited Python object, normal completion is reported as
/// [`MachineResume::Value`], while a raised exception is reported as
/// [`MachineResume::Error`]. Returning an error from `resume` terminates the outer
/// awaitable and propagates that error to its caller.
pub(crate) trait AwaitableStateMachine: 'static {
    /// Advance after startup or the completion/failure of a delegated await.
    fn resume(&mut self, py: Python<'_>, input: MachineResume) -> PyResult<MachineAction>;
}

/// Wrap a Rust continuation in a Python awaitable.
///
/// The returned object implements the `__await__` iterator protocol. Every Future
/// yielded by a delegated Python awaitable is returned directly to the active
/// Python task, so scheduling, wakeups, and cancellation stay with its event loop.
/// The wrapper is single-use, matching coroutine reuse behavior.
pub(crate) fn into_python_awaitable<M>(py: Python<'_>, machine: M) -> PyResult<Py<PyAny>>
where
    M: AwaitableStateMachine,
{
    Py::new(py, NativeAwaitable::new(machine)).map(|value| value.into_any())
}

/// Register the native continuation as a coroutine for task-group integrations.
///
/// The object already implements `send`, `throw`, `close`, and `__await__`; the
/// virtual registration lets asyncio and AnyIO recognize it as a coroutine.
pub(crate) fn register_coroutine_protocol(py: Python<'_>) -> PyResult<()> {
    py.import("collections.abc")?
        .getattr("Coroutine")?
        .call_method1("register", (py.get_type::<NativeAwaitable>(),))?;
    Ok(())
}

#[pyclass(unsendable)]
struct NativeAwaitable {
    machine: Option<Box<dyn AwaitableStateMachine>>,
    delegated_iterator: Option<DelegatedIterator>,
    started: bool,
    finished: bool,
}

impl NativeAwaitable {
    fn new<M>(machine: M) -> Self
    where
        M: AwaitableStateMachine,
    {
        Self {
            machine: Some(Box::new(machine)),
            delegated_iterator: None,
            started: false,
            finished: false,
        }
    }

    fn send_from_python(&mut self, py: Python<'_>, value: Py<PyAny>) -> PyResult<Py<PyAny>> {
        if self.finished {
            return Err(reused_coroutine_error());
        }
        if !self.started {
            if !value.bind(py).is_none() {
                return Err(PyTypeError::new_err(
                    "can't send non-None value to a just-started coroutine",
                ));
            }
            self.started = true;
            self.drive(py, DriveInput::Start)
        } else {
            self.drive(py, DriveInput::Send(value))
        }
    }

    fn throw_from_python(
        &mut self,
        py: Python<'_>,
        exception_type: Py<PyAny>,
        value: Option<Py<PyAny>>,
        traceback: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        if self.finished {
            return Err(reused_coroutine_error());
        }
        let error = normalize_throw(py, exception_type, value, traceback)?;
        if !self.started {
            self.finish();
            return Err(error);
        }
        self.drive(py, DriveInput::Throw(error))
    }

    fn close_from_python(&mut self, py: Python<'_>) -> PyResult<()> {
        if self.finished {
            return Ok(());
        }
        if !self.started {
            self.finish();
            return Ok(());
        }

        match self.drive(py, DriveInput::Close) {
            Ok(_) => {
                let close_result = self.close_delegated_iterator(py);
                self.finish();
                close_result?;
                Err(PyRuntimeError::new_err("coroutine ignored GeneratorExit"))
            }
            Err(error)
                if error.is_instance_of::<PyGeneratorExit>(py)
                    || error.is_instance_of::<PyStopIteration>(py) =>
            {
                let close_result = self.close_delegated_iterator(py);
                self.finish();
                close_result
            }
            Err(error) => {
                let close_result = self.close_delegated_iterator(py);
                self.finish();
                close_result.and(Err(error))
            }
        }
    }

    fn drive(&mut self, py: Python<'_>, mut input: DriveInput) -> PyResult<Py<PyAny>> {
        loop {
            if self.finished {
                return Err(reused_coroutine_error());
            }

            if self.delegated_iterator.is_some() {
                match self.resume_delegated_iterator(py, &input) {
                    Ok(yielded) => return Ok(yielded),
                    Err(error) if error.is_instance_of::<PyStopIteration>(py) => {
                        let value = error.value(py).getattr("value")?.unbind();
                        self.delegated_iterator = None;
                        input = DriveInput::Machine(MachineResume::Value(value));
                    }
                    Err(error) => {
                        self.delegated_iterator = None;
                        input = DriveInput::Machine(MachineResume::Error(error));
                    }
                }
                continue;
            }

            let resume = match input {
                DriveInput::Start => MachineResume::Start,
                DriveInput::Send(value) => MachineResume::Value(value),
                DriveInput::Throw(error) => MachineResume::Error(error),
                DriveInput::Close => MachineResume::Error(PyGeneratorExit::new_err(())),
                DriveInput::Machine(resume) => resume,
            };

            let action = match self.machine.as_mut() {
                Some(machine) => machine.resume(py, resume),
                None => return Err(reused_coroutine_error()),
            };
            let action = match action {
                Ok(action) => action,
                Err(error) => {
                    self.finish();
                    return Err(coroutine_boundary_error(py, error));
                }
            };

            match action {
                MachineAction::Await(awaitable) => match await_iterator(py, awaitable) {
                    Ok(iterator) => {
                        self.delegated_iterator = Some(iterator);
                        input = DriveInput::Send(py.None());
                    }
                    Err(error) => input = DriveInput::Machine(MachineResume::Error(error)),
                },
                #[cfg(feature = "fault-injection")]
                MachineAction::Raise(error) => {
                    input = DriveInput::Machine(MachineResume::Error(error));
                }
                MachineAction::Complete(value) => {
                    self.finish();
                    return Err(PyStopIteration::new_err((value,)));
                }
            }
        }
    }

    fn resume_delegated_iterator(&self, py: Python<'_>, input: &DriveInput) -> PyResult<Py<PyAny>> {
        let delegated = self
            .delegated_iterator
            .as_ref()
            .ok_or_else(|| PyRuntimeError::new_err("await delegation is not active"))?;
        let iterator = delegated.iterator.bind(py);

        match input {
            DriveInput::Start => send_value(iterator, py.None().bind(py)),
            DriveInput::Send(value) => send_value(iterator, value.bind(py)),
            DriveInput::Throw(error) => throw_into_iterator(
                iterator,
                py,
                error.clone_ref(py),
                delegated.single_exception_throw,
            ),
            DriveInput::Close => {
                close_iterator(iterator)?;
                Err(PyGeneratorExit::new_err(()))
            }
            DriveInput::Machine(_) => Err(PyRuntimeError::new_err(
                "state-machine input cannot resume an active Python awaitable",
            )),
        }
    }

    fn close_delegated_iterator(&mut self, py: Python<'_>) -> PyResult<()> {
        let Some(iterator) = self.delegated_iterator.take() else {
            return Ok(());
        };
        close_iterator(iterator.iterator.bind(py))
    }

    fn finish(&mut self) {
        self.finished = true;
        self.delegated_iterator = None;
        self.machine = None;
    }
}

enum DriveInput {
    Start,
    Send(Py<PyAny>),
    Throw(PyErr),
    Close,
    Machine(MachineResume),
}

#[pymethods]
impl NativeAwaitable {
    fn __await__(self_: Py<Self>) -> Py<Self> {
        self_
    }

    fn __iter__(self_: Py<Self>) -> Py<Self> {
        self_
    }

    fn __next__(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        self.send_from_python(py, py.None())
    }

    fn send(&mut self, py: Python<'_>, value: Py<PyAny>) -> PyResult<Py<PyAny>> {
        self.send_from_python(py, value)
    }

    #[pyo3(signature = (exception_type, value=None, traceback=None))]
    fn throw(
        &mut self,
        py: Python<'_>,
        exception_type: Py<PyAny>,
        value: Option<Py<PyAny>>,
        traceback: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        self.throw_from_python(py, exception_type, value, traceback)
    }

    fn close(&mut self, py: Python<'_>) -> PyResult<()> {
        self.close_from_python(py)
    }
}

struct DelegatedIterator {
    iterator: Py<PyAny>,
    // Exact native generators/coroutines use single-instance throw. The
    // existing generic three-argument branch remains an unproven arity gap.
    single_exception_throw: bool,
}

fn await_iterator(py: Python<'_>, awaitable: Py<PyAny>) -> PyResult<DelegatedIterator> {
    let awaitable = awaitable.bind(py);
    let types = py.import("types")?;
    let coroutine_type = types.getattr("CoroutineType")?;
    let generator_type = types.getattr("GeneratorType")?;
    if awaitable.get_type().is(&coroutine_type)
        || is_iterable_coroutine_generator(awaitable, &generator_type)?
    {
        return Ok(DelegatedIterator {
            iterator: awaitable.clone().unbind(),
            single_exception_throw: true,
        });
    }

    let is_awaitable = py
        .import("inspect")?
        .getattr("isawaitable")?
        .call1((awaitable,))?
        .extract::<bool>()?;
    if !is_awaitable {
        return Err(PyTypeError::new_err(format!(
            "object {} can't be used in 'await' expression",
            type_name(awaitable)?
        )));
    }

    let iterator = awaitable.call_method0("__await__")?;
    if iterator.get_type().is(&coroutine_type)
        || is_iterable_coroutine_generator(&iterator, &generator_type)?
    {
        return Err(PyTypeError::new_err("__await__() returned a coroutine"));
    }
    if !iterator.is_instance_of::<PyIterator>() {
        return Err(PyTypeError::new_err(format!(
            "__await__() returned non-iterator of type '{}'",
            type_name(&iterator)?
        )));
    }
    let single_exception_throw = iterator.get_type().is(&generator_type);
    Ok(DelegatedIterator {
        iterator: iterator.unbind(),
        single_exception_throw,
    })
}

fn is_iterable_coroutine_generator(
    value: &Bound<'_, PyAny>,
    generator_type: &Bound<'_, PyAny>,
) -> PyResult<bool> {
    // CO_ITERABLE_COROUTINE in the pinned CPython 3.12 code-object protocol.
    const CO_ITERABLE_COROUTINE: u32 = 0x100;
    if !value.get_type().is(generator_type) {
        return Ok(false);
    }
    // This public property emits an audit event; audit-hook fidelity is unproven.
    let flags = value
        .getattr("gi_code")?
        .getattr("co_flags")?
        .extract::<u32>()?;
    Ok(flags & CO_ITERABLE_COROUTINE != 0)
}

fn type_name(value: &Bound<'_, PyAny>) -> PyResult<String> {
    value.get_type().getattr("__name__")?.extract()
}

fn send_value(iterator: &Bound<'_, PyAny>, value: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
    if value.is_none() && !iterator.hasattr("send")? {
        return iterator.call_method0("__next__").map(Bound::unbind);
    }
    iterator.call_method1("send", (value,)).map(Bound::unbind)
}

fn throw_into_iterator(
    iterator: &Bound<'_, PyAny>,
    py: Python<'_>,
    error: PyErr,
    single_exception_throw: bool,
) -> PyResult<Py<PyAny>> {
    if !iterator.hasattr("throw")? {
        return Err(error);
    }

    if single_exception_throw {
        let exception_value = error.into_value(py).into_any();
        return iterator
            .call_method1("throw", (exception_value,))
            .map(Bound::unbind);
    }

    let exception_type = error.get_type(py).unbind();
    let traceback = error
        .traceback(py)
        .map(|traceback| traceback.unbind().into_any())
        .unwrap_or_else(|| py.None());
    let exception_value = error.into_value(py).into_any();
    iterator
        .call_method1("throw", (exception_type, exception_value, traceback))
        .map(Bound::unbind)
}

fn close_iterator(iterator: &Bound<'_, PyAny>) -> PyResult<()> {
    if iterator.hasattr("close")? {
        iterator.call_method0("close")?;
    }
    Ok(())
}

fn normalize_throw(
    py: Python<'_>,
    exception_type: Py<PyAny>,
    value: Option<Py<PyAny>>,
    traceback: Option<Py<PyAny>>,
) -> PyResult<PyErr> {
    let exception_type = exception_type.bind(py);
    let exception = if exception_type.is_instance_of::<PyBaseException>() {
        if value
            .as_ref()
            .is_some_and(|value| !value.bind(py).is_none())
        {
            return Err(PyTypeError::new_err(
                "instance exception may not have a separate value",
            ));
        }
        exception_type.clone().unbind()
    } else {
        let exception_class = exception_type.cast::<PyType>()?;
        let constructed = match value {
            Some(value) if value.bind(py).is_instance_of::<PyBaseException>() => value,
            Some(value) if !value.bind(py).is_none() => {
                exception_class.call1((value.bind(py),))?.unbind()
            }
            _ => exception_class.call0()?.unbind(),
        };
        if !constructed.bind(py).is_instance_of::<PyBaseException>() {
            return Err(PyTypeError::new_err(
                "exceptions must derive from BaseException",
            ));
        }
        constructed
    };

    let error = PyErr::from_value(exception.into_bound(py));
    if let Some(traceback) = traceback.filter(|traceback| !traceback.bind(py).is_none()) {
        let traceback = traceback.bind(py).cast::<PyTraceback>()?.clone();
        error.set_traceback(py, Some(traceback));
    }
    Ok(error)
}

fn coroutine_boundary_error(py: Python<'_>, error: PyErr) -> PyErr {
    if error.is_instance_of::<PyStopIteration>(py) {
        let replacement = PyRuntimeError::new_err("coroutine raised StopIteration");
        replacement.set_cause(py, Some(error));
        replacement
    } else {
        error
    }
}

fn reused_coroutine_error() -> PyErr {
    PyRuntimeError::new_err("cannot reuse already awaited coroutine")
}
