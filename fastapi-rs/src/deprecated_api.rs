//! Deprecated FastAPI APIs retained for source-compatible imports.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule, PyString};

const OPERATION_ID_FOR_PATH_WARNING: &str = "fastapi.utils.generate_operation_id_for_path() was deprecated, it is not used internally, and will be removed soon";
const OPERATION_ID_WARNING: &str = "fastapi.openapi.utils.generate_operation_id() was deprecated, it is not used internally, and will be removed soon";

#[pyfunction]
#[pyo3(signature = (*, name, path, method))]
fn generate_operation_id_for_path(
    py: Python<'_>,
    name: &Bound<'_, PyAny>,
    path: &Bound<'_, PyAny>,
    method: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    emit_warning(py, OPERATION_ID_FOR_PATH_WARNING, 1)?;
    let operation_id = operation_id(
        name.str()?.to_str()?,
        path.str()?.to_str()?,
        method.str()?.to_str()?,
    );
    Ok(PyString::new(py, &operation_id).into_any().unbind())
}

#[pyfunction]
#[pyo3(signature = (*, route, method))]
fn generate_operation_id(
    py: Python<'_>,
    route: &Bound<'_, PyAny>,
    method: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    emit_warning(py, OPERATION_ID_WARNING, 1)?;
    let route_operation_id = route.getattr("operation_id")?;
    if route_operation_id.is_truthy()? {
        return Ok(route_operation_id.unbind());
    }

    emit_warning_explicit(py)?;
    let name = route.getattr("name")?;
    let path = route.getattr("path_format")?;
    let operation_id = operation_id(
        name.str()?.to_str()?,
        path.str()?.to_str()?,
        method.str()?.to_str()?,
    );
    Ok(PyString::new(py, &operation_id).into_any().unbind())
}

fn operation_id(name: &str, path: &str, method: &str) -> String {
    let operation_name = format!("{name}{path}");
    let mut normalized = String::with_capacity(operation_name.len() + method.len() + 1);
    normalized.extend(operation_name.chars().map(|character| {
        if character == '_' || character.is_alphanumeric() {
            character
        } else {
            '_'
        }
    }));
    normalized.push('_');
    normalized.push_str(&method.to_lowercase());
    normalized
}

fn emit_warning(py: Python<'_>, message: &str, stacklevel: usize) -> PyResult<()> {
    let warnings = py.import("warnings")?;
    let category = crate::errors::fastapi_deprecation_warning_type(py);
    let kwargs = PyDict::new(py);
    kwargs.set_item("stacklevel", stacklevel)?;
    warnings
        .getattr("warn")?
        .call((message, category), Some(&kwargs))?;
    Ok(())
}

fn emit_warning_explicit(py: Python<'_>) -> PyResult<()> {
    let warnings = py.import("warnings")?;
    let category = crate::errors::fastapi_deprecation_warning_type(py);
    warnings.getattr("warn_explicit")?.call1((
        OPERATION_ID_FOR_PATH_WARNING,
        category,
        "fastapi/openapi/utils.py",
        278,
    ))?;
    Ok(())
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let operation_id_for_path = wrap_pyfunction!(generate_operation_id_for_path, module)?;
    operation_id_for_path.setattr("__module__", "fastapi.utils")?;
    module.add("generate_operation_id_for_path", operation_id_for_path)?;

    let operation_id = wrap_pyfunction!(generate_operation_id, module)?;
    operation_id.setattr("__module__", "fastapi.openapi.utils")?;
    module.add("generate_operation_id", operation_id)?;
    Ok(())
}
