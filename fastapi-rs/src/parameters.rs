//! Rust-owned parameter class factories and dependency constructors.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyModule, PyString, PyTuple};

use crate::parameter_classes::{self, ParameterClassKind};

#[pyfunction(name = "Depends", signature = (*args, **kwargs))]
fn depends(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    crate::dependency_records::depends_factory(py, args, kwargs)
}

#[pyfunction(name = "Security", signature = (*args, **kwargs))]
fn security(
    py: Python<'_>,
    args: &Bound<'_, PyTuple>,
    kwargs: Option<&Bound<'_, PyDict>>,
) -> PyResult<Py<PyAny>> {
    crate::dependency_records::security_factory(py, args, kwargs)
}

macro_rules! parameter_factory {
    ($rust_name:ident, $public_name:literal, $kind:ident) => {
        #[pyfunction(name = $public_name, signature = (*args, **kwargs))]
        fn $rust_name(
            py: Python<'_>,
            args: &Bound<'_, PyTuple>,
            kwargs: Option<&Bound<'_, PyDict>>,
        ) -> PyResult<Py<PyAny>> {
            parameter_classes::factory(py, ParameterClassKind::$kind, args, kwargs)
        }
    };
}

parameter_factory!(header, "Header", Header);
parameter_factory!(cookie, "Cookie", Cookie);
parameter_factory!(query, "Query", Query);
parameter_factory!(path, "Path", Path);
parameter_factory!(body, "Body", Body);
parameter_factory!(form, "Form", Form);
parameter_factory!(file, "File", File);

/// Register public parameter factories and dependency constructors.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    let depends_function = wrap_pyfunction!(depends, module)?;
    let depends = py
        .import("functools")?
        .getattr("partial")?
        .call1((depends_function,))?;
    set_depends_signature(py, &depends)?;
    let security_function = wrap_pyfunction!(security, module)?;
    let security = py
        .import("functools")?
        .getattr("partial")?
        .call1((security_function,))?;
    set_security_signature(py, &security, &depends)?;
    module.add("Depends", depends)?;
    module.add("Security", security)?;
    module.add_function(wrap_pyfunction!(header, module)?)?;
    module.add_function(wrap_pyfunction!(cookie, module)?)?;
    module.add_function(wrap_pyfunction!(query, module)?)?;
    module.add_function(wrap_pyfunction!(path, module)?)?;
    module.add_function(wrap_pyfunction!(body, module)?)?;
    module.add_function(wrap_pyfunction!(form, module)?)?;
    module.add_function(wrap_pyfunction!(file, module)?)?;

    let status = py.import("starlette.status")?;
    module.add_submodule(&status)?;
    Ok(())
}

/// Register parameter class types after application runtime adds signature types.
pub(crate) fn register_classes(
    module: &Bound<'_, PyModule>,
    default_placeholder: &Bound<'_, PyAny>,
) -> PyResult<()> {
    parameter_classes::register(module, default_placeholder)
}

fn set_depends_signature(py: Python<'_>, function: &Bound<'_, PyAny>) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let typing = py.import("typing")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let annotated = typing.getattr("Annotated")?;
    let dependency_doc = annotated_doc.call1((r#"
            A "dependable" callable (like a function).

            Don't call it directly, FastAPI will call it for you, just pass the object
            directly.

            Read more about it in the
            [FastAPI docs for Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
            "#,))?;
    let cache_doc = annotated_doc.call1((
        r#"
            By default, after a dependency is called the first time in a request, if
            the dependency is declared again for the rest of the request (for example
            if the dependency is needed by several dependencies), the value will be
            re-used for the rest of the request.

            Set `use_cache` to `False` to disable this behavior and ensure the
            dependency is called again (if declared more than once) in the same request.

            Read more about it in the
            [FastAPI docs about sub-dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/#using-the-same-dependency-multiple-times)
            "#,
    ))?;
    let scope_doc = annotated_doc.call1((
        r#"
            Mainly for dependencies with `yield`, define when the dependency function
            should start (the code before `yield`) and when it should end (the code
            after `yield`).

            * `"function"`: start the dependency before the *path operation function*
                that handles the request, end the dependency after the *path operation
                function* ends, but **before** the response is sent back to the client.
                So, the dependency function will be executed **around** the *path operation
                **function***.
            * `"request"`: start the dependency before the *path operation function*
                that handles the request (similar to when using `"function"`), but end
                **after** the response is sent back to the client. So, the dependency
                function will be executed **around** the **request** and response cycle.

            Read more about it in the
            [FastAPI docs for FastAPI Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#early-exit-and-scope)
            "#,
    ))?;

    let any_type = typing.getattr("Any")?;
    let callable_type = py.import("collections.abc")?.getattr("Callable")?;
    let ellipsis = py.Ellipsis().into_bound(py);
    let callable_args = PyTuple::new(py, [ellipsis, any_type.clone()])?;
    let callable_type = callable_type.get_item(callable_args)?;
    let none_type = py.None().bind(py).get_type();
    let optional_callable = py
        .import("operator")?
        .getattr("or_")?
        .call1((callable_type, none_type.clone()))?;
    let dependency_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_callable.as_any(), dependency_doc.as_any()],
        )?,))?;
    let cache_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [
                py.get_type::<pyo3::types::PyBool>().as_any(),
                cache_doc.as_any(),
            ],
        )?,))?;

    let literal_values = PyTuple::new(
        py,
        [
            PyString::new(py, "function").as_any(),
            PyString::new(py, "request").as_any(),
        ],
    )?;
    let literal_scope = typing
        .getattr("Literal")?
        .getattr("__getitem__")?
        .call1((literal_values,))?;
    let optional_scope = literal_scope.call_method1("__or__", (none_type,))?;
    let scope_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_scope.as_any(), scope_doc.as_any()],
        )?,))?;

    let parameter_type = inspect.getattr("Parameter")?;
    let positional_or_keyword = parameter_type.getattr("POSITIONAL_OR_KEYWORD")?;
    let keyword_only = parameter_type.getattr("KEYWORD_ONLY")?;
    let dependency_kwargs = PyDict::new(py);
    dependency_kwargs.set_item("annotation", dependency_annotation.clone())?;
    dependency_kwargs.set_item("default", py.None())?;
    let dependency = parameter_type.call(
        ("dependency", positional_or_keyword),
        Some(&dependency_kwargs),
    )?;
    let cache_kwargs = PyDict::new(py);
    cache_kwargs.set_item("annotation", cache_annotation.clone())?;
    cache_kwargs.set_item("default", true)?;
    let use_cache =
        parameter_type.call(("use_cache", keyword_only.clone()), Some(&cache_kwargs))?;
    let scope_kwargs = PyDict::new(py);
    scope_kwargs.set_item("annotation", scope_annotation.clone())?;
    scope_kwargs.set_item("default", py.None())?;
    let scope = parameter_type.call(("scope", keyword_only), Some(&scope_kwargs))?;
    let parameters = PyList::new(py, [dependency, use_cache, scope])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", any_type.clone())?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    let annotations = PyDict::new(py);
    annotations.set_item("dependency", dependency_annotation)?;
    annotations.set_item("use_cache", cache_annotation)?;
    annotations.set_item("scope", scope_annotation)?;
    annotations.set_item("return", any_type)?;
    function.setattr("__signature__", signature)?;
    function.setattr("__annotations__", annotations)?;
    function.setattr("__module__", "fastapi.param_functions")?;
    function.setattr("__name__", "Depends")?;
    function.setattr("__qualname__", "Depends")?;
    function.setattr(
        "__doc__",
        r#"
    Declare a FastAPI dependency.

    It takes a single "dependable" callable (like a function).

    Don't call it directly, FastAPI will call it for you.

    Read more about it in the
    [FastAPI docs for Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/).

    **Example**

    ```python
    from typing import Annotated

    from fastapi import Depends, FastAPI

    app = FastAPI()


    async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
        return {"q": q, "skip": skip, "limit": limit}


    @app.get("/items/")
    async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
        return commons
    ```
    "#,
    )?;
    Ok(())
}

fn set_security_signature(
    py: Python<'_>,
    function: &Bound<'_, PyAny>,
    depends_function: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let inspect = py.import("inspect")?;
    let typing = py.import("typing")?;
    let annotated_doc = py.import("annotated_doc")?.getattr("Doc")?;
    let annotated = typing.getattr("Annotated")?;
    let dependency_parameters = inspect
        .getattr("signature")?
        .call1((depends_function,))?
        .getattr("parameters")?;
    let dependency = dependency_parameters.get_item("dependency")?;
    let use_cache = dependency_parameters.get_item("use_cache")?;
    let dependency_annotation = dependency.getattr("annotation")?;
    let cache_annotation = use_cache.getattr("annotation")?;

    let scopes_doc = annotated_doc.call1((r#"
            OAuth2 scopes required for the *path operation* that uses this Security
            dependency.

            The term "scope" comes from the OAuth2 specification, it seems to be
            intentionally vague and interpretable. It normally refers to permissions,
            in cases to roles.

            These scopes are integrated with OpenAPI (and the API docs at `/docs`).
            So they are visible in the OpenAPI specification.

            Read more about it in the
            [FastAPI docs about OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
            "#,
    ))?;
    let sequence_type = py.import("collections.abc")?.getattr("Sequence")?;
    let string_type = py.import("builtins")?.getattr("str")?;
    let sequence_string = sequence_type.get_item(string_type)?;
    let none_type = py.None().bind(py).get_type();
    let optional_scopes = py
        .import("operator")?
        .getattr("or_")?
        .call1((sequence_string, none_type))?;
    let scopes_annotation = annotated
        .getattr("__class_getitem__")?
        .call1((PyTuple::new(
            py,
            [optional_scopes.as_any(), scopes_doc.as_any()],
        )?,))?;

    let parameter_type = inspect.getattr("Parameter")?;
    let keyword_only = parameter_type.getattr("KEYWORD_ONLY")?;
    let scopes_kwargs = PyDict::new(py);
    scopes_kwargs.set_item("annotation", scopes_annotation.clone())?;
    scopes_kwargs.set_item("default", py.None())?;
    let scopes = parameter_type.call(("scopes", keyword_only.clone()), Some(&scopes_kwargs))?;
    let parameters = PyList::new(py, [dependency, scopes, use_cache])?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", typing.getattr("Any")?)?;
    let signature = inspect
        .getattr("Signature")?
        .call((parameters,), Some(&signature_kwargs))?;
    let annotations = PyDict::new(py);
    annotations.set_item("dependency", dependency_annotation)?;
    annotations.set_item("scopes", scopes_annotation)?;
    annotations.set_item("use_cache", cache_annotation)?;
    annotations.set_item("return", typing.getattr("Any")?)?;
    function.setattr("__signature__", signature)?;
    function.setattr("__annotations__", annotations)?;
    function.setattr("__module__", "fastapi.param_functions")?;
    function.setattr("__name__", "Security")?;
    function.setattr("__qualname__", "Security")?;
    function.setattr("__doc__", "Declare a FastAPI Security dependency.")?;
    Ok(())
}
