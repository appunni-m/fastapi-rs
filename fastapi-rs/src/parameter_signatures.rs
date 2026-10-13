//! Source-derived `inspect.Signature` metadata for FastAPI parameter factories.
//!
//! The embedded contract is generated from the pinned FastAPI source during
//! development. This module rebuilds its Python typing objects in Rust without
//! importing FastAPI at runtime. Call [`decorate_factories`] after registering
//! `DefaultPlaceholder` and the OpenAPI models, before Python facade imports.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyList, PyModule, PyTuple};

const SIGNATURE_CONTRACT: &str = include_str!("parameter_signature_contract.json");
const FACTORY_NAMES: [&str; 7] = ["Path", "Query", "Header", "Cookie", "Body", "Form", "File"];

static PARSED_SIGNATURE_CONTRACT: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static SIGNATURE_EXAMPLE_TYPE: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

/// Decorate each registered native factory exactly once, replacing its core
/// module binding with the shared callable all Python facade aliases re-export.
///
/// `default_placeholder` must be the target's `DefaultPlaceholder(None)`
/// instance, created by Rust after its PyO3 class is registered.
pub(crate) fn decorate_factories(
    module: &Bound<'_, PyModule>,
    default_placeholder: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let py = module.py();
    let contract = parsed_contract(py)?;
    signature_example_type(py, &contract)?;
    for name in FACTORY_NAMES {
        let native = module.getattr(name)?;
        let decorated = decorate_factory(py, &native, name, default_placeholder, &contract)?;
        module.setattr(name, decorated)?;
    }
    Ok(())
}

fn parsed_contract<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
    PARSED_SIGNATURE_CONTRACT
        .get_or_try_init(py, || {
            py.import("json")?
                .getattr("loads")?
                .call1((SIGNATURE_CONTRACT,))
                .map(Bound::unbind)
        })
        .map(|contract| contract.bind(py).clone())
}

fn signature_example_type<'py>(
    py: Python<'py>,
    contract: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    SIGNATURE_EXAMPLE_TYPE
        .get_or_try_init(py, || {
            let private_types = contract.get_item("private_types")?;
            let mut keys = private_types.try_iter()?;
            let key = keys
                .next()
                .transpose()?
                .ok_or_else(|| PyValueError::new_err("signature contract has no private types"))?;
            if keys.next().is_some() {
                return Err(PyValueError::new_err(
                    "signature contract has unsupported private type count",
                ));
            }
            let descriptor = private_types.get_item(key)?;
            build_example_type(py, &descriptor, contract).map(Bound::unbind)
        })
        .map(|value| value.bind(py).clone())
}

fn build_example_type<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    contract: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let kind: String = descriptor.get_item("kind")?.extract()?;
    if kind != "typed_dict" {
        return Err(PyValueError::new_err(format!(
            "unsupported private annotation type descriptor: {kind}"
        )));
    }
    let annotations = contract.get_item("annotations")?;
    let documentation = contract.get_item("documentation")?;
    let fields = PyDict::new(py);
    for field in descriptor.get_item("fields")?.try_iter()? {
        let field = field?;
        let name: String = field.get_item("name")?.extract()?;
        let annotation_index: usize = field.get_item("annotation_ref")?.extract()?;
        let annotation =
            build_annotation(py, &annotations.get_item(annotation_index)?, &documentation)?;
        fields.set_item(name, annotation)?;
    }
    let name = descriptor.get_item("name")?;
    let total = descriptor.get_item("total")?;
    let kwargs = PyDict::new(py);
    kwargs.set_item("total", total)?;
    let typed_dict = py
        .import("typing_extensions")?
        .getattr("TypedDict")?
        .call((name, fields), Some(&kwargs))?;
    typed_dict.setattr("__module__", descriptor.get_item("module")?)?;
    typed_dict.setattr(
        "__pydantic_config__",
        descriptor.get_item("pydantic_config")?,
    )?;
    Ok(typed_dict)
}

fn decorate_factory<'py>(
    py: Python<'py>,
    native: &Bound<'py, PyAny>,
    name: &str,
    default_placeholder: &Bound<'py, PyAny>,
    contract: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let factory = contract.get_item("factories")?.get_item(name)?;
    let source_name: String = factory.get_item("name")?.extract()?;
    if source_name != name {
        return Err(PyValueError::new_err(format!(
            "signature contract names {source_name}, requested {name}"
        )));
    }

    let annotations = contract.get_item("annotations")?;
    let documentation = contract.get_item("documentation")?;
    let inspect = py.import("inspect")?;
    let parameter_type = inspect.getattr("Parameter")?;
    let parameters = PyList::empty(py);
    let annotations_map = PyDict::new(py);

    for parameter in factory.get_item("parameters")?.try_iter()? {
        let parameter = parameter?;
        let parameter_name: String = parameter.get_item("name")?.extract()?;
        let kind_name: String = parameter.get_item("kind")?.extract()?;
        let kind = parameter_type.getattr(&kind_name)?;
        let annotation_index: usize = parameter.get_item("annotation_ref")?.extract()?;
        let annotation_spec = annotations.get_item(annotation_index)?;
        let annotation = build_annotation(py, &annotation_spec, &documentation)?;
        annotations_map.set_item(&parameter_name, &annotation)?;

        let kwargs = PyDict::new(py);
        kwargs.set_item("annotation", &annotation)?;
        let has_default: bool = parameter.get_item("has_default")?.extract()?;
        if has_default {
            let default_spec = parameter.get_item("default")?;
            let default = build_default(py, &default_spec, default_placeholder)?;
            kwargs.set_item("default", default)?;
        } else {
            kwargs.set_item("default", parameter_type.getattr("empty")?)?;
        }
        parameters.append(parameter_type.call((&parameter_name, &kind), Some(&kwargs))?)?;
    }

    let return_index: usize = factory.get_item("return_annotation_ref")?.extract()?;
    let return_spec = annotations.get_item(return_index)?;
    let return_annotation = build_annotation(py, &return_spec, &documentation)?;
    annotations_map.set_item("return", &return_annotation)?;
    let signature_kwargs = PyDict::new(py);
    signature_kwargs.set_item("return_annotation", &return_annotation)?;
    let signature = inspect
        .getattr("Signature")?
        .call((&parameters,), Some(&signature_kwargs))?;

    let decorated = py
        .import("functools")?
        .getattr("partial")?
        .call1((native,))?;
    decorated.setattr("__signature__", signature)?;
    decorated.setattr("__annotations__", annotations_map)?;
    decorated.setattr("__module__", factory.get_item("module")?)?;
    decorated.setattr("__name__", factory.get_item("name")?)?;
    decorated.setattr("__qualname__", factory.get_item("qualname")?)?;
    decorated.setattr("__doc__", factory.get_item("doc")?)?;
    Ok(decorated)
}

fn build_default<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    default_placeholder: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    if !descriptor.is_instance_of::<PyDict>() {
        return Ok(descriptor.clone());
    }
    match descriptor.get_item("kind")?.extract::<String>()?.as_str() {
        "python_singleton" => match descriptor.get_item("name")?.extract::<String>()?.as_str() {
            "Ellipsis" => Ok(py.Ellipsis().into_bound(py)),
            "PydanticUndefined" => py.import("pydantic_core")?.getattr("PydanticUndefined"),
            name => Err(PyValueError::new_err(format!(
                "unsupported parameter default singleton: {name}"
            ))),
        },
        "fastapi_default_placeholder" => {
            let source_value = descriptor.get_item("value")?;
            if !source_value.is_none() {
                return Err(PyValueError::new_err(
                    "source parameter placeholder value is outside the reviewed contract",
                ));
            }
            Ok(default_placeholder.clone())
        }
        kind => Err(PyValueError::new_err(format!(
            "unsupported parameter default descriptor: {kind}"
        ))),
    }
}

fn build_annotation<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    documentation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let kind: String = descriptor.get_item("kind")?.extract()?;
    match kind.as_str() {
        "type" | "typing_form" => {
            let name: String = descriptor.get_item("qualified_name")?.extract()?;
            resolve_qualified_name(py, &name)
        }
        "annotated" => build_annotated(py, descriptor, documentation),
        "generic" => build_generic(py, descriptor, documentation),
        "annotation_sequence" => build_annotation_sequence(py, descriptor, documentation),
        "empty" => Ok(py
            .import("inspect")?
            .getattr("Signature")?
            .getattr("empty")?),
        "ellipsis" => Ok(py.Ellipsis().into_bound(py)),
        kind => Err(PyValueError::new_err(format!(
            "unsupported parameter annotation descriptor: {kind}"
        ))),
    }
}

fn build_annotated<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    documentation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let alias_name: String = descriptor.get_item("alias_name")?.extract()?;
    if alias_name != "Annotated" {
        return Err(PyValueError::new_err(format!(
            "unsupported Annotated alias name: {alias_name}"
        )));
    }
    let base = build_annotation(py, &descriptor.get_item("base")?, documentation)?;
    let mut arguments = vec![base];
    for metadata in descriptor.get_item("metadata")?.try_iter()? {
        arguments.push(build_metadata(py, &metadata?, documentation)?);
    }
    let tuple = PyTuple::new(py, arguments)?;
    py.import("typing")?
        .getattr("Annotated")?
        .getattr("__class_getitem__")?
        .call1((tuple,))
}

fn build_generic<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    documentation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    if !descriptor.get_item("alias_name")?.is_none() {
        return Err(PyValueError::new_err(
            "named generic aliases are outside the reviewed signature contract",
        ));
    }
    let origin_name: String = descriptor.get_item("origin")?.extract()?;
    let mut arguments = Vec::new();
    for argument in descriptor.get_item("arguments")?.try_iter()? {
        arguments.push(build_annotation(py, &argument?, documentation)?);
    }
    if origin_name == "types.UnionType" {
        let mut values = arguments.into_iter();
        let Some(mut union) = values.next() else {
            return Err(PyValueError::new_err(
                "a source union annotation must contain at least one member",
            ));
        };
        let operator = py.import("operator")?.getattr("or_")?;
        for value in values {
            union = operator.call1((union, value))?;
        }
        return Ok(union);
    }
    let origin = resolve_qualified_name(py, &origin_name)?;
    let item = if arguments.len() == 1 {
        arguments.remove(0)
    } else {
        PyTuple::new(py, arguments)?.into_any()
    };
    origin.getattr("__class_getitem__")?.call1((item,))
}

fn build_annotation_sequence<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    documentation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let mut items = Vec::new();
    for item in descriptor.get_item("items")?.try_iter()? {
        items.push(build_annotation(py, &item?, documentation)?);
    }
    let sequence_type: String = descriptor.get_item("python_type")?.extract()?;
    match sequence_type.as_str() {
        "builtins.list" => Ok(PyList::new(py, items)?.into_any()),
        "builtins.tuple" => Ok(PyTuple::new(py, items)?.into_any()),
        kind => Err(PyValueError::new_err(format!(
            "unsupported annotation sequence type: {kind}"
        ))),
    }
}

fn build_metadata<'py>(
    py: Python<'py>,
    descriptor: &Bound<'py, PyAny>,
    documentation: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    match descriptor.get_item("kind")?.extract::<String>()?.as_str() {
        "doc" => {
            let doc_name: String = descriptor.get_item("qualified_name")?.extract()?;
            let doc_type = resolve_qualified_name(py, &doc_name)?;
            let index: usize = descriptor.get_item("documentation_ref")?.extract()?;
            doc_type.call1((documentation.get_item(index)?,))
        }
        "deprecated" => {
            let deprecated_name: String = descriptor.get_item("qualified_name")?.extract()?;
            let deprecated_type = resolve_qualified_name(py, &deprecated_name)?;
            let message = descriptor.get_item("message")?;
            let category = build_annotation(py, &descriptor.get_item("category")?, documentation)?;
            let stacklevel = descriptor.get_item("stacklevel")?;
            let kwargs = PyDict::new(py);
            kwargs.set_item("category", category)?;
            kwargs.set_item("stacklevel", stacklevel)?;
            deprecated_type.call((message,), Some(&kwargs))
        }
        kind => Err(PyValueError::new_err(format!(
            "unsupported parameter annotation metadata: {kind}"
        ))),
    }
}

fn resolve_qualified_name<'py>(
    py: Python<'py>,
    qualified_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let contract = parsed_contract(py)?;
    if contract
        .get_item("private_types")?
        .contains(qualified_name)?
    {
        return SIGNATURE_EXAMPLE_TYPE
            .get(py)
            .map(|value| value.bind(py).clone())
            .ok_or_else(|| {
                PyValueError::new_err("private Example annotation type was not initialized")
            });
    }
    let Some((module_name, attribute_name)) = qualified_name.rsplit_once('.') else {
        return Err(PyValueError::new_err(format!(
            "unqualified annotation symbol: {qualified_name}"
        )));
    };
    if module_name == "builtins" && attribute_name == "NoneType" {
        let none = py.None();
        return Ok(none.bind(py).get_type().into_any());
    }
    let source_package: String = contract
        .get_item("source")?
        .get_item("package")?
        .extract()?;
    if module_name == source_package
        || module_name
            .strip_prefix(&source_package)
            .is_some_and(|suffix| suffix.starts_with('.'))
    {
        return Err(PyValueError::new_err(
            "source-owned annotation type is missing from the private type contract",
        ));
    }
    py.import(module_name)?.getattr(attribute_name)
}
