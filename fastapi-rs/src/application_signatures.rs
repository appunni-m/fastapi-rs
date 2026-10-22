//! Source-derived public signatures for FastAPI's application and router APIs.

use std::collections::HashMap;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyList, PyModule, PyString, PyTuple};

const CONTRACT: &str = include_str!("route_signature.json");
const CONTRACT_SCHEMA: &str = "fastapi-rs/application-signature-contract@1";
const FASTAPI_SOURCE_REVISION: &str = "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1";

static PARSED_CONTRACT: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

pub(crate) struct ApplicationSignatureBuilder {
    contract: Py<PyAny>,
    core_module: Py<PyModule>,
    type_variables: HashMap<String, Py<PyAny>>,
}

impl ApplicationSignatureBuilder {
    pub(crate) fn new(module: &Bound<'_, PyModule>) -> PyResult<Self> {
        let py = module.py();
        let contract = PARSED_CONTRACT
            .get_or_try_init(py, || {
                py.import("json")?
                    .getattr("loads")?
                    .call1((CONTRACT,))
                    .map(Bound::unbind)
            })?
            .clone_ref(py);
        let contract_value = contract.bind(py);
        let schema: String = contract_value.get_item("schema")?.extract()?;
        let revision: String = contract_value
            .get_item("source")?
            .get_item("revision")?
            .extract()?;
        if schema != CONTRACT_SCHEMA || revision != FASTAPI_SOURCE_REVISION {
            return Err(PyRuntimeError::new_err(
                "application signature contract is not pinned to FastAPI 0.157.0",
            ));
        }
        Ok(Self {
            contract,
            core_module: module.clone().unbind(),
            type_variables: HashMap::new(),
        })
    }

    pub(crate) fn build_signature(&mut self, py: Python<'_>, name: &str) -> PyResult<Py<PyAny>> {
        let contract = self.contract.bind(py);
        let callable = contract
            .get_item("callables")?
            .get_item(name)
            .map_err(|_| {
                PyValueError::new_err(format!("unknown application signature contract: {name}"))
            })?;
        let annotations = contract.get_item("annotations")?;
        let documentation = contract.get_item("documentation")?;
        let parameter_type = py.import("inspect")?.getattr("Parameter")?;
        let parameters = PyList::empty(py);
        for parameter in callable.get_item("parameters")?.try_iter()? {
            let parameter = parameter?;
            let parameter_name: String = parameter.get_item("name")?.extract()?;
            let kind_name: String = parameter.get_item("kind")?.extract()?;
            let kind = parameter_type.getattr(&kind_name)?;
            let annotation_index: usize = parameter.get_item("annotation_ref")?.extract()?;
            let annotation = self.build_annotation(
                py,
                &annotations.get_item(annotation_index)?,
                &documentation,
            )?;
            let kwargs = PyDict::new(py);
            kwargs.set_item("annotation", annotation)?;
            if parameter.get_item("has_default")?.extract::<bool>()? {
                let default = self.build_default(py, &parameter.get_item("default")?)?;
                kwargs.set_item("default", default)?;
            }
            parameters.append(parameter_type.call((&parameter_name, &kind), Some(&kwargs))?)?;
        }
        let return_index: usize = callable.get_item("return_annotation_ref")?.extract()?;
        let return_annotation =
            self.build_annotation(py, &annotations.get_item(return_index)?, &documentation)?;
        let signature_kwargs = PyDict::new(py);
        signature_kwargs.set_item("return_annotation", return_annotation)?;
        py.import("inspect")?
            .getattr("Signature")?
            .call((&parameters,), Some(&signature_kwargs))
            .map(Bound::unbind)
    }

    fn build_default<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        if !descriptor.is_instance_of::<PyDict>() {
            return Ok(descriptor.clone());
        }
        match descriptor.get_item("kind")?.extract::<String>()?.as_str() {
            "fastapi_default_placeholder" => {
                let value = self.build_default(py, &descriptor.get_item("value")?)?;
                crate::application_runtime::default_placeholder(py, value.unbind())
                    .map(|value| value.into_bound(py))
            }
            "class" => {
                let name: String = descriptor.get_item("qualified_name")?.extract()?;
                self.resolve_qualified_name(py, &name)
            }
            "callable" => {
                let name: String = descriptor.get_item("qualified_name")?.extract()?;
                self.resolve_qualified_name(py, &name)
            }
            "python_singleton" => {
                match descriptor.get_item("name")?.extract::<String>()?.as_str() {
                    "Ellipsis" => Ok(py.Ellipsis().into_bound(py)),
                    "PydanticUndefined" => py.import("pydantic_core")?.getattr("PydanticUndefined"),
                    name => Err(PyValueError::new_err(format!(
                        "unsupported application signature singleton: {name}"
                    ))),
                }
            }
            kind => Err(PyValueError::new_err(format!(
                "unsupported application signature default: {kind}"
            ))),
        }
    }

    fn build_annotation<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
        documentation: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let kind: String = descriptor.get_item("kind")?.extract()?;
        match kind.as_str() {
            "type" | "typing_form" => {
                let name: String = descriptor.get_item("qualified_name")?.extract()?;
                self.resolve_qualified_name(py, &name)
            }
            "literal" => descriptor.get_item("value"),
            "empty" => py.import("inspect")?.getattr("Signature")?.getattr("empty"),
            "ellipsis" => Ok(py.Ellipsis().into_bound(py)),
            "forward_ref" => self.build_forward_ref(py, descriptor),
            "type_variable" => self.build_type_variable(py, descriptor, documentation),
            "annotated" => self.build_annotated(py, descriptor, documentation),
            "generic" => self.build_generic(py, descriptor, documentation),
            "annotation_sequence" => self.build_annotation_sequence(py, descriptor, documentation),
            kind => Err(PyValueError::new_err(format!(
                "unsupported application signature annotation: {kind}"
            ))),
        }
    }

    fn build_annotated<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
        documentation: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base = self.build_annotation(py, &descriptor.get_item("base")?, documentation)?;
        let mut arguments = vec![base];
        for item in descriptor.get_item("metadata")?.try_iter()? {
            arguments.push(self.build_metadata(py, &item?, documentation)?);
        }
        py.import("typing")?
            .getattr("Annotated")?
            .getattr("__class_getitem__")?
            .call1((PyTuple::new(py, arguments)?,))
    }

    fn build_generic<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
        documentation: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let origin_name: String = descriptor.get_item("origin")?.extract()?;
        let alias_name = descriptor
            .get_item("alias_name")?
            .extract::<Option<String>>()?;
        let origin = if let Some(alias) = alias_name.as_deref() {
            py.import("typing")?.getattr(alias)?
        } else {
            self.resolve_qualified_name(py, &origin_name)?
        };
        let mut arguments = Vec::new();
        for argument in descriptor.get_item("arguments")?.try_iter()? {
            arguments.push(self.build_annotation(py, &argument?, documentation)?);
        }
        if alias_name.as_deref() == Some("Optional") {
            let Some(optional_value) = arguments.into_iter().next() else {
                return Err(PyValueError::new_err(
                    "a source Optional annotation must contain a value type",
                ));
            };
            return origin.get_item(optional_value);
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
        let item = if arguments.len() == 1 {
            arguments.remove(0)
        } else {
            PyTuple::new(py, arguments)?.into_any()
        };
        origin.get_item(item)
    }

    fn build_annotation_sequence<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
        documentation: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let mut items = Vec::new();
        for item in descriptor.get_item("items")?.try_iter()? {
            items.push(self.build_annotation(py, &item?, documentation)?);
        }
        let sequence_type: String = descriptor.get_item("python_type")?.extract()?;
        match sequence_type.as_str() {
            "builtins.list" => Ok(PyList::new(py, items)?.into_any()),
            "builtins.tuple" => Ok(PyTuple::new(py, items)?.into_any()),
            kind => Err(PyValueError::new_err(format!(
                "unsupported signature annotation sequence: {kind}"
            ))),
        }
    }

    fn build_metadata<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
        documentation: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        match descriptor.get_item("kind")?.extract::<String>()?.as_str() {
            "doc" => {
                let name: String = descriptor.get_item("qualified_name")?.extract()?;
                let doc_type = self.resolve_qualified_name(py, &name)?;
                let index: usize = descriptor.get_item("documentation_ref")?.extract()?;
                doc_type.call1((documentation.get_item(index)?,))
            }
            "deprecated" => {
                let name: String = descriptor.get_item("qualified_name")?.extract()?;
                let deprecated_type = self.resolve_qualified_name(py, &name)?;
                let category =
                    self.build_annotation(py, &descriptor.get_item("category")?, documentation)?;
                let kwargs = PyDict::new(py);
                kwargs.set_item("category", category)?;
                kwargs.set_item("stacklevel", descriptor.get_item("stacklevel")?)?;
                deprecated_type.call((descriptor.get_item("message")?,), Some(&kwargs))
            }
            kind => Err(PyValueError::new_err(format!(
                "unsupported application signature metadata: {kind}"
            ))),
        }
    }

    fn build_forward_ref<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let kwargs = PyDict::new(py);
        kwargs.set_item("module", descriptor.get_item("module")?)?;
        kwargs.set_item("is_argument", descriptor.get_item("is_argument")?)?;
        kwargs.set_item("is_class", descriptor.get_item("is_class")?)?;
        py.import("typing")?
            .getattr("ForwardRef")?
            .call((descriptor.get_item("argument")?,), Some(&kwargs))
    }

    fn build_type_variable<'py>(
        &mut self,
        py: Python<'py>,
        descriptor: &Bound<'py, PyAny>,
        documentation: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let module: String = descriptor.get_item("module")?.extract()?;
        let name: String = descriptor.get_item("name")?.extract()?;
        let key = format!("{module}.{name}");
        if let Some(type_variable) = self.type_variables.get(&key) {
            return Ok(type_variable.bind(py).clone());
        }
        let mut arguments = vec![PyString::new(py, &name).into_any()];
        let mut constraints = Vec::new();
        for constraint in descriptor.get_item("constraints")?.try_iter()? {
            constraints.push(self.build_annotation(py, &constraint?, documentation)?);
        }
        arguments.extend(constraints);
        let bound = self.build_annotation(py, &descriptor.get_item("bound")?, documentation)?;
        let kwargs = PyDict::new(py);
        if !bound.is_none() {
            kwargs.set_item("bound", &bound)?;
        }
        kwargs.set_item("covariant", descriptor.get_item("covariant")?)?;
        kwargs.set_item("contravariant", descriptor.get_item("contravariant")?)?;
        if !descriptor.get_item("infer_variance")?.is_none() {
            kwargs.set_item("infer_variance", descriptor.get_item("infer_variance")?)?;
        }
        let type_variable = py
            .import("typing")?
            .getattr("TypeVar")?
            .call(PyTuple::new(py, arguments)?, Some(&kwargs))?;
        type_variable.setattr("__module__", module)?;
        let type_variable = type_variable.unbind();
        self.type_variables.insert(key, type_variable.clone_ref(py));
        Ok(type_variable.into_bound(py))
    }

    fn resolve_qualified_name<'py>(
        &self,
        py: Python<'py>,
        qualified_name: &str,
    ) -> PyResult<Bound<'py, PyAny>> {
        let module = self.core_module.bind(py);
        if qualified_name == "builtins.NoneType" {
            let none = py.None();
            return Ok(none.bind(py).get_type().into_any());
        }
        let source_package: String = self
            .contract
            .bind(py)
            .get_item("source")?
            .get_item("distribution")?
            .extract()?;
        let source_prefix = format!("{source_package}.");
        if let Some(source_name) = qualified_name.strip_prefix(&source_prefix) {
            return match source_name {
                "applications.FastAPI" => module.getattr("FastAPI"),
                "datastructures.DefaultPlaceholder" => module.getattr("DefaultPlaceholder"),
                "params.Depends" => module.getattr("ParamsDepends"),
                "routing.APIRoute" => module.getattr("APIRoute"),
                "routing.APIRouter" => module.getattr("APIRouter"),
                "utils.generate_unique_id" => module.getattr("_generate_unique_id"),
                _ => Err(PyValueError::new_err(format!(
                    "unmapped source-owned application signature type: {source_name}"
                ))),
            };
        }
        let Some((module_name, attribute_name)) = qualified_name.rsplit_once('.') else {
            return Err(PyValueError::new_err(format!(
                "unqualified application signature type: {qualified_name}"
            )));
        };
        py.import(module_name)?.getattr(attribute_name)
    }
}
