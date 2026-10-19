//! FastAPI-owned data structure integrations with Starlette-RS values.

use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyModule, PyTuple, PyType};

const BACKGROUND_TASKS_CLASS_DOC: &str = r#"
    A collection of background tasks that will be called after a response has been
    sent to the client.

    Read more about it in the
    [FastAPI docs for Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).

    ## Example

    ```python
    from fastapi import BackgroundTasks, FastAPI

    app = FastAPI()


    def write_notification(email: str, message=""):
        with open("log.txt", mode="w") as email_file:
            content = f"notification for {email}: {message}"
            email_file.write(content)


    @app.post("/send-notification/{email}")
    async def send_notification(email: str, background_tasks: BackgroundTasks):
        background_tasks.add_task(write_notification, email, message="some notification")
        return {"message": "Notification sent in the background"}
    ```
    "#;
const BACKGROUND_TASKS_ADD_TASK_DOC: &str = r#"
        Add a function to be called in the background after the response is sent.

        Read more about it in the
        [FastAPI docs for Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).
        "#;

const UPLOAD_FILE_WRITE_DOC: &str = r#"
        Write some bytes to the file.

        You normally wouldn't use this from a file you read in a request.

        To be awaitable, compatible with async, this is run in threadpool.
        "#;
const UPLOAD_FILE_READ_DOC: &str = r#"
        Read some bytes from the file.

        To be awaitable, compatible with async, this is run in threadpool.
        "#;
const UPLOAD_FILE_SEEK_DOC: &str = r#"
        Move to a position in the file.

        Any next read or write will be done from that position.

        To be awaitable, compatible with async, this is run in threadpool.
        "#;
const UPLOAD_FILE_CLOSE_DOC: &str = r#"
        Close the file.

        To be awaitable, compatible with async, this is run in threadpool.
        "#;
const UPLOAD_FILE_CLASS_DOC: &str = r#"
    A file uploaded in a request.

    Define it as a *path operation function* (or dependency) parameter.

    If you are using a regular `def` function, you can use the `upload_file.file`
    attribute to access the raw standard Python file (blocking, not async), useful and
    needed for non-async code.

    Read more about it in the
    [FastAPI docs for Request Files](https://fastapi.tiangolo.com/tutorial/request-files/).

    ## Example

    ```python
    from typing import Annotated

    from fastapi import FastAPI, File, UploadFile

    app = FastAPI()


    @app.post("/files/")
    async def create_file(file: Annotated[bytes, File()]):
        return {"file_size": len(file)}


    @app.post("/uploadfile/")
    async def create_upload_file(file: UploadFile):
        return {"filename": file.filename}
    ```
    "#;

fn upload_file_annotated_type<'py>(
    py: Python<'py>,
    base: &Bound<'py, PyAny>,
    documentation: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let doc = py
        .import("annotated_doc")?
        .getattr("Doc")?
        .call1((documentation,))?;
    let metadata = PyTuple::new(py, [base, &doc])?;
    py.import("typing")?
        .getattr("Annotated")?
        .get_item(metadata)
}

fn copy_upload_file_method<'py>(
    py: Python<'py>,
    starlette_upload_file: &Bound<'py, PyAny>,
    method_name: &str,
    documentation: &str,
    annotations: &Bound<'py, PyDict>,
) -> PyResult<Bound<'py, PyAny>> {
    let source = starlette_upload_file.getattr(method_name)?;
    let function_type = py.import("types")?.getattr("FunctionType")?;
    let method = function_type.call1((
        source.getattr("__code__")?,
        source.getattr("__globals__")?,
        method_name,
        source.getattr("__defaults__")?,
        source.getattr("__closure__")?,
    ))?;
    method.setattr("__kwdefaults__", source.getattr("__kwdefaults__")?)?;
    method.setattr("__annotations__", annotations)?;
    method.setattr("__module__", "fastapi.datastructures")?;
    method.setattr("__qualname__", format!("UploadFile.{method_name}"))?;
    method.setattr("__doc__", documentation)?;
    Ok(method)
}

fn upload_file_method<'py>(
    py: Python<'py>,
    starlette_upload_file: &Bound<'py, PyAny>,
    method_name: &str,
    documentation: &str,
    parameter: Option<(&str, Bound<'py, PyAny>)>,
    return_annotation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let annotations = PyDict::new(py);
    if let Some((name, annotation)) = parameter {
        annotations.set_item(name, annotation)?;
    }
    annotations.set_item("return", return_annotation)?;
    copy_upload_file_method(
        py,
        starlette_upload_file,
        method_name,
        documentation,
        &annotations,
    )
}

fn upload_file_class_annotations<'py>(
    py: Python<'py>,
    starlette_datastructures: &Bound<'py, PyAny>,
    string_type: &Bound<'py, PyAny>,
    integer_type: &Bound<'py, PyAny>,
    none_type: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    let typing = py.import("typing")?;
    let union = py.import("operator")?.getattr("or_")?;
    let optional_string = union.call1((string_type, none_type))?;
    let optional_integer = union.call1((integer_type, none_type))?;
    let annotations = PyDict::new(py);
    annotations.set_item(
        "file",
        upload_file_annotated_type(
            py,
            &typing.getattr("BinaryIO")?,
            "The standard Python file object (non-async).",
        )?,
    )?;
    annotations.set_item(
        "filename",
        upload_file_annotated_type(py, &optional_string, "The original file name.")?,
    )?;
    annotations.set_item(
        "size",
        upload_file_annotated_type(py, &optional_integer, "The size of the file in bytes.")?,
    )?;
    annotations.set_item(
        "headers",
        upload_file_annotated_type(
            py,
            &starlette_datastructures.getattr("Headers")?,
            "The headers of the request.",
        )?,
    )?;
    annotations.set_item(
        "content_type",
        upload_file_annotated_type(
            py,
            &optional_string,
            "The content type of the request, from the headers.",
        )?,
    )?;
    Ok(annotations)
}

#[pyclass(name = "_BackgroundTasksAddTask", module = "fastapi_rs._core", dict)]
struct BackgroundTasksAddTask;

fn background_task_keyword_present(
    kwargs: Option<&Bound<'_, PyDict>>,
    name: &str,
) -> PyResult<bool> {
    kwargs
        .map(|kwargs| kwargs.contains(name))
        .transpose()
        .map(|present| present.unwrap_or(false))
}

fn normalize_background_task_binding_error(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
    error: PyErr,
) -> PyResult<PyErr> {
    if !error.is_instance_of::<PyTypeError>(py) {
        return Ok(error);
    }

    let message = error.value(py).str()?.to_string_lossy().into_owned();
    if message.starts_with("multiple values for argument ") {
        return Ok(PyTypeError::new_err(format!(
            "BackgroundTasks.add_task() got {message}"
        )));
    }

    if message.starts_with("missing a required argument: ") {
        let mut missing = Vec::new();
        if args.is_empty() && !background_task_keyword_present(kwargs, "self")? {
            missing.push("self");
        }
        if args.len() < 2 && !background_task_keyword_present(kwargs, "func")? {
            missing.push("func");
        }
        let message = match missing.as_slice() {
            [name] => format!(
                "BackgroundTasks.add_task() missing 1 required positional argument: '{name}'"
            ),
            [first, second] => format!(
                "BackgroundTasks.add_task() missing 2 required positional arguments: '{first}' and '{second}'"
            ),
            _ => return Ok(error),
        };
        return Ok(PyTypeError::new_err(message));
    }

    Ok(error)
}

#[pymethods]
impl BackgroundTasksAddTask {
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
        let bound_arguments = match slf
            .bind(py)
            .getattr("__signature__")?
            .call_method("bind", args, kwargs)
        {
            Ok(bound_arguments) => bound_arguments,
            Err(error) => {
                return Err(normalize_background_task_binding_error(
                    py, args, kwargs, error,
                )?);
            }
        };
        let bound_args = bound_arguments.getattr("args")?.cast_into::<PyTuple>()?;
        let bound_kwargs = bound_arguments.getattr("kwargs")?.cast_into::<PyDict>()?;
        let instance = bound_args.get_item(0)?;
        let owner = slf.bind(py).getattr("__fastapi_owner__")?;
        let super_object = py
            .import("builtins")?
            .getattr("super")?
            .call1((owner, instance))?;
        let parent_method = super_object.getattr("add_task")?;
        let forwarded_args = PyTuple::new(py, bound_args.iter().skip(1))?;
        parent_method
            .call(&forwarded_args, Some(&bound_kwargs))
            .map(Bound::unbind)
    }
}

fn background_tasks_add_task_signature<'py>(
    py: Python<'py>,
) -> PyResult<(Bound<'py, PyAny>, Bound<'py, PyDict>)> {
    let typing = py.import("typing")?;
    let parameter_spec = py
        .import("typing_extensions")?
        .getattr("ParamSpec")?
        .call1(("P",))?;
    parameter_spec.setattr("__module__", "fastapi.background")?;
    let callable = py.import("collections.abc")?.getattr("Callable")?;
    let callable_arguments = PyTuple::new(py, [parameter_spec.clone(), typing.getattr("Any")?])?;
    let callable_annotation = callable.get_item(callable_arguments)?;
    let documentation = py
        .import("annotated_doc")?
        .getattr("Doc")?
        .call1(("\n                The function to call after the response is sent.\n\n                It can be a regular `def` function or an `async def` function.\n                ",))?;
    let annotated_arguments = PyTuple::new(py, [callable_annotation, documentation])?;
    let function_annotation = typing.getattr("Annotated")?.get_item(annotated_arguments)?;
    let args_annotation = parameter_spec.getattr("args")?;
    let kwargs_annotation = parameter_spec.getattr("kwargs")?;

    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let positional_or_keyword = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let parameters = PyList::empty(py);
    parameters.append(parameter_type.call1(("self", &positional_or_keyword))?)?;

    let function_kwargs = PyDict::new(py);
    function_kwargs.set_item("annotation", &function_annotation)?;
    parameters
        .append(parameter_type.call(("func", &positional_or_keyword), Some(&function_kwargs))?)?;

    let variable_positional = parameter_type.getattr("VAR_POSITIONAL")?;
    let args_kwargs = PyDict::new(py);
    args_kwargs.set_item("annotation", &args_annotation)?;
    parameters.append(parameter_type.call(("args", variable_positional), Some(&args_kwargs))?)?;

    let variable_keyword = parameter_type.getattr("VAR_KEYWORD")?;
    let kwargs_kwargs = PyDict::new(py);
    kwargs_kwargs.set_item("annotation", &kwargs_annotation)?;
    parameters.append(parameter_type.call(("kwargs", variable_keyword), Some(&kwargs_kwargs))?)?;

    let annotations = PyDict::new(py);
    annotations.set_item("func", &function_annotation)?;
    annotations.set_item("args", &args_annotation)?;
    annotations.set_item("kwargs", &kwargs_annotation)?;
    annotations.set_item("return", py.None())?;

    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", py.None())?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    Ok((signature, annotations))
}

/// FastAPI's Pydantic validator accepts any Starlette UploadFile and preserves
/// the exact object produced by the request parser.
#[pyfunction]
fn upload_file_validate(
    py: Python<'_>,
    _cls: &Bound<'_, PyType>,
    input_value: &Bound<'_, PyAny>,
    _info: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let starlette_upload_file = py
        .import("starlette.datastructures")?
        .getattr("UploadFile")?;
    let is_upload_file = py
        .import("builtins")?
        .getattr("isinstance")?
        .call1((input_value, starlette_upload_file))?
        .extract::<bool>()?;
    if !is_upload_file {
        let received_type = py
            .import("builtins")?
            .getattr("type")?
            .call1((input_value,))?
            .repr()?
            .to_str()?
            .to_owned();
        return Err(PyValueError::new_err(format!(
            "Expected UploadFile, received: {received_type}"
        )));
    }
    Ok(input_value.clone().unbind())
}

/// Build the same info-aware plain-validator schema used by FastAPI 0.141.1.
#[pyfunction]
fn upload_file_core_schema(
    py: Python<'_>,
    cls: &Bound<'_, PyType>,
    _source: &Bound<'_, PyAny>,
    _handler: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let validator = cls.getattr("_validate")?;
    py.import("pydantic_core.core_schema")?
        .getattr("with_info_plain_validator_function")?
        .call1((validator,))
        .map(Bound::unbind)
}

/// Return FastAPI UploadFile's fixed Pydantic JSON schema.
#[pyfunction]
fn upload_file_json_schema(
    py: Python<'_>,
    _cls: &Bound<'_, PyType>,
    _core_schema: &Bound<'_, PyAny>,
    _handler: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let schema = PyDict::new(py);
    schema.set_item("type", "string")?;
    schema.set_item("contentMediaType", "application/octet-stream")?;
    Ok(schema.into_any().unbind())
}

/// Register FastAPI's annotation class over the Starlette-RS UploadFile type.
///
/// A runtime-created subclass keeps the FastAPI class identity while inheriting
/// Starlette-RS construction and file behavior. The Pydantic protocol callbacks
/// are native PyO3 functions installed as class methods on the generated type.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let classmethod = py.import("builtins")?.getattr("classmethod")?;
    let validate = wrap_pyfunction!(upload_file_validate, module)?;
    let core_schema = wrap_pyfunction!(upload_file_core_schema, module)?;
    let json_schema = wrap_pyfunction!(upload_file_json_schema, module)?;

    let starlette_datastructures = py.import("starlette.datastructures")?;
    let starlette_upload_file = starlette_datastructures.getattr("UploadFile")?;
    let builtins = py.import("builtins")?;
    let bytes_type = builtins.getattr("bytes")?;
    let integer_type = builtins.getattr("int")?;
    let string_type = builtins.getattr("str")?;
    let none_value = py.None();
    let none_type = builtins.getattr("type")?.call1((none_value.bind(py),))?;
    let class_annotations = upload_file_class_annotations(
        py,
        &starlette_datastructures,
        &string_type,
        &integer_type,
        &none_type,
    )?;

    let write_annotation = upload_file_annotated_type(
        py,
        &bytes_type,
        "\n                The bytes to write to the file.\n                ",
    )?;
    let read_annotation = upload_file_annotated_type(
        py,
        &integer_type,
        "\n                The number of bytes to read from the file.\n                ",
    )?;
    let seek_annotation = upload_file_annotated_type(
        py,
        &integer_type,
        "\n                The position in bytes to seek to in the file.\n                ",
    )?;
    let write = upload_file_method(
        py,
        &starlette_upload_file,
        "write",
        UPLOAD_FILE_WRITE_DOC,
        Some(("data", write_annotation)),
        none_value.bind(py),
    )?;
    let read = upload_file_method(
        py,
        &starlette_upload_file,
        "read",
        UPLOAD_FILE_READ_DOC,
        Some(("size", read_annotation)),
        &bytes_type,
    )?;
    let seek = upload_file_method(
        py,
        &starlette_upload_file,
        "seek",
        UPLOAD_FILE_SEEK_DOC,
        Some(("offset", seek_annotation)),
        none_value.bind(py),
    )?;
    let close = upload_file_method(
        py,
        &starlette_upload_file,
        "close",
        UPLOAD_FILE_CLOSE_DOC,
        None,
        none_value.bind(py),
    )?;

    let attributes = PyDict::new(py);
    attributes.set_item("__module__", "fastapi.datastructures")?;
    attributes.set_item("__doc__", UPLOAD_FILE_CLASS_DOC)?;
    attributes.set_item("__annotations__", class_annotations)?;
    attributes.set_item("write", write)?;
    attributes.set_item("read", read)?;
    attributes.set_item("seek", seek)?;
    attributes.set_item("close", close)?;
    attributes.set_item("_validate", classmethod.call1((validate,))?)?;
    attributes.set_item(
        "__get_pydantic_core_schema__",
        classmethod.call1((core_schema,))?,
    )?;
    attributes.set_item(
        "__get_pydantic_json_schema__",
        classmethod.call1((json_schema,))?,
    )?;

    let bases = PyTuple::new(py, [starlette_upload_file])?;
    let upload_file =
        py.import("builtins")?
            .getattr("type")?
            .call1(("UploadFile", bases, attributes))?;
    module.add("UploadFile", upload_file)?;
    register_background_tasks(module)?;

    for name in [
        "URL",
        "Address",
        "FormData",
        "Headers",
        "QueryParams",
        "State",
    ] {
        module.add(name, starlette_datastructures.getattr(name)?)?;
    }
    Ok(())
}

/// Register FastAPI's public subclass over Starlette-RS background task support.
fn register_background_tasks(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let attributes = PyDict::new(py);
    attributes.set_item("__module__", "fastapi.background")?;
    attributes.set_item("__doc__", BACKGROUND_TASKS_CLASS_DOC)?;

    let (signature, annotations) = background_tasks_add_task_signature(py)?;
    let add_task = Py::new(py, BackgroundTasksAddTask)?;
    let add_task_bound = add_task.bind(py);
    add_task_bound.setattr("__name__", "add_task")?;
    add_task_bound.setattr("__qualname__", "BackgroundTasks.add_task")?;
    add_task_bound.setattr("__module__", "fastapi.background")?;
    add_task_bound.setattr("__doc__", BACKGROUND_TASKS_ADD_TASK_DOC)?;
    add_task_bound.setattr("__annotations__", annotations)?;
    add_task_bound.setattr("__signature__", signature)?;
    attributes.set_item("add_task", add_task_bound)?;

    let starlette_background_tasks = py
        .import("starlette.background")?
        .getattr("BackgroundTasks")?;
    let bases = PyTuple::new(py, [starlette_background_tasks])?;
    let background_tasks =
        py.import("builtins")?
            .getattr("type")?
            .call1(("BackgroundTasks", bases, attributes))?;
    add_task_bound.setattr("__fastapi_owner__", &background_tasks)?;
    module.add("BackgroundTasks", background_tasks)
}
