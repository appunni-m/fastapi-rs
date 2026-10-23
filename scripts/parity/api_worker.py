"""Run direct public Python API probes in an identity-checked oracle process."""

from __future__ import annotations

import argparse
import asyncio
import base64
import datetime as dt
import importlib
import inspect
import json
import math
import re
import sys
import typing
import uuid
import warnings
from collections.abc import Mapping
from decimal import Decimal
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic_core import PydanticUndefined

from scripts.parity.schema_ids import MATERIALIZED_INPUT_INDEX_SCHEMA_ID
from scripts.parity.signature_annotations import (
    SignatureAnnotationError,
    project_annotation,
)
from scripts.parity.worker import (
    ORACLE_PROFILE_ID,
    ORACLE_PROFILE_PACKAGE_EXTENSIONS,
    ROOT,
    WorkerError,
    _is_under,
    _load_workload,
    _oracle_identity,
    _sha256_file,
    _validate_workload_path,
)

WORKFLOW_SCHEMA_ID = "fastapi-rs/python-api-workflow@1"
WORKFLOW_SCHEMA_V2_ID = "fastapi-rs/python-api-workflow@2"
WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow@3"
WORKFLOW_SCHEMA_V4_ID = "fastapi-rs/python-api-workflow@4"
WORKFLOW_SCHEMA_V5_ID = "fastapi-rs/python-api-workflow@5"
WORKFLOW_SCHEMA_V6_ID = "fastapi-rs/python-api-workflow@6"
WORKFLOW_SCHEMA_V7_ID = "fastapi-rs/python-api-workflow@7"
WORKFLOW_SCHEMA_V8_ID = "fastapi-rs/python-api-workflow@8"
WORKFLOW_SCHEMA_V9_ID = "fastapi-rs/python-api-workflow@9"
WORKFLOW_SCHEMA_V10_ID = "fastapi-rs/python-api-workflow@10"
WORKFLOW_SCHEMA_V11_ID = "fastapi-rs/python-api-workflow@11"
WORKFLOW_SCHEMA_V12_ID = "fastapi-rs/python-api-workflow@12"
WORKFLOW_SCHEMA_V13_ID = "fastapi-rs/python-api-workflow@13"
WORKFLOW_SCHEMA_V14_ID = "fastapi-rs/python-api-workflow@14"
WORKFLOW_SCHEMA_V15_ID = "fastapi-rs/python-api-workflow@15"
WORKFLOW_SCHEMA_IDS = frozenset(
    {
        WORKFLOW_SCHEMA_ID,
        WORKFLOW_SCHEMA_V2_ID,
        WORKFLOW_SCHEMA_V3_ID,
        WORKFLOW_SCHEMA_V4_ID,
        WORKFLOW_SCHEMA_V5_ID,
        WORKFLOW_SCHEMA_V6_ID,
        WORKFLOW_SCHEMA_V7_ID,
        WORKFLOW_SCHEMA_V8_ID,
        WORKFLOW_SCHEMA_V9_ID,
        WORKFLOW_SCHEMA_V10_ID,
        WORKFLOW_SCHEMA_V11_ID,
        WORKFLOW_SCHEMA_V12_ID,
        WORKFLOW_SCHEMA_V13_ID,
        WORKFLOW_SCHEMA_V14_ID,
        WORKFLOW_SCHEMA_V15_ID,
    }
)
RESULT_SCHEMA_ID = "fastapi-rs/python-api-workflow-result@2"
RESULT_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow-result@3"
RESULT_SCHEMA_V4_ID = "fastapi-rs/python-api-workflow-result@4"
RESULT_SCHEMA_V5_ID = "fastapi-rs/python-api-workflow-result@5"
RESULT_SCHEMA_V6_ID = "fastapi-rs/python-api-workflow-result@6"
RESULT_SCHEMA_V7_ID = "fastapi-rs/python-api-workflow-result@7"
RESULT_SCHEMA_V8_ID = "fastapi-rs/python-api-workflow-result@8"
RESULT_SCHEMA_V9_ID = "fastapi-rs/python-api-workflow-result@9"
RESULT_SCHEMA_V10_ID = "fastapi-rs/python-api-workflow-result@10"
RESULT_SCHEMA_V11_ID = "fastapi-rs/python-api-workflow-result@11"
RESULT_SCHEMA_V12_ID = "fastapi-rs/python-api-workflow-result@12"
RESULT_SCHEMA_V13_ID = "fastapi-rs/python-api-workflow-result@13"
RESULT_SCHEMA_V14_ID = "fastapi-rs/python-api-workflow-result@14"
RESULT_SCHEMA_V15_ID = "fastapi-rs/python-api-workflow-result@15"
RESULT_SCHEMA_V16_ID = "fastapi-rs/python-api-workflow-result@16"
RESULT_SCHEMA_V17_ID = "fastapi-rs/python-api-workflow-result@17"
RESULT_SCHEMA_V18_ID = "fastapi-rs/python-api-workflow-result@18"
RESULT_SCHEMA_IDS_BY_WORKFLOW = {
    WORKFLOW_SCHEMA_ID: RESULT_SCHEMA_ID,
    WORKFLOW_SCHEMA_V2_ID: RESULT_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V3_ID: RESULT_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V4_ID: RESULT_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V5_ID: RESULT_SCHEMA_V7_ID,
    WORKFLOW_SCHEMA_V6_ID: RESULT_SCHEMA_V8_ID,
    WORKFLOW_SCHEMA_V7_ID: RESULT_SCHEMA_V9_ID,
    WORKFLOW_SCHEMA_V8_ID: RESULT_SCHEMA_V10_ID,
    WORKFLOW_SCHEMA_V9_ID: RESULT_SCHEMA_V11_ID,
    WORKFLOW_SCHEMA_V10_ID: RESULT_SCHEMA_V12_ID,
    WORKFLOW_SCHEMA_V11_ID: RESULT_SCHEMA_V13_ID,
    WORKFLOW_SCHEMA_V12_ID: RESULT_SCHEMA_V14_ID,
    WORKFLOW_SCHEMA_V13_ID: RESULT_SCHEMA_V15_ID,
    WORKFLOW_SCHEMA_V14_ID: RESULT_SCHEMA_V17_ID,
    WORKFLOW_SCHEMA_V15_ID: RESULT_SCHEMA_V18_ID,
}
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
ATLAS_SCHEMA_ID = "fastapi-rs/compatibility-atlas@11"
INDEX_SCHEMA_ID = MATERIALIZED_INPUT_INDEX_SCHEMA_ID
_MODULE_PATH = re.compile(r"fastapi(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
_STARLETTE_MODULE_PATH = re.compile(r"starlette(?:\.[A-Za-z_][A-Za-z0-9_]*)+\Z")
_ATTRIBUTE_PATH = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
PINNED_AUTHORITIES = {
    "fastapi": {
        "version": "0.157.0",
        "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    },
}
_PARAMETER_VALUE_MISSING = object()
_PARAMETER_VALUE_ATTRIBUTES = (
    "annotation",
    "default",
    "default_factory",
    "alias",
    "alias_priority",
    "validation_alias",
    "serialization_alias",
    "title",
    "description",
    "examples",
    "example",
    "openapi_examples",
    "deprecated",
    "include_in_schema",
    "json_schema_extra",
    "discriminator",
    "in_",
    "convert_underscores",
    "embed",
    "media_type",
)
_PARAMETER_CONSTRAINT_ATTRIBUTES = (
    "gt",
    "ge",
    "lt",
    "le",
    "multiple_of",
    "min_length",
    "max_length",
    "max_digits",
    "decimal_places",
    "pattern",
    "allow_inf_nan",
    "strict",
)


def _error_record(error: Exception) -> dict[str, str]:
    error_type = type(error)
    return {
        "class": f"{error_type.__module__}.{error_type.__qualname__}",
        "message": str(error),
    }


def _warning_filename(
    filename: str,
    fastapi_root: Path,
    starlette_package_root: Path | None = None,
) -> str:
    """Normalize warning paths to stable repository or package-relative names."""
    warning_path = Path(filename)
    resolved_path = warning_path.resolve()
    package_root = (fastapi_root / "fastapi").resolve()
    try:
        package_relative = resolved_path.relative_to(package_root)
    except ValueError:
        pass
    else:
        return PurePosixPath("fastapi", *package_relative.parts).as_posix()

    if starlette_package_root is not None:
        try:
            package_relative = resolved_path.relative_to(starlette_package_root.resolve())
        except ValueError:
            pass
        else:
            return PurePosixPath("starlette", *package_relative.parts).as_posix()

    try:
        repository_relative = resolved_path.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        return PurePosixPath(*repository_relative.parts).as_posix()

    if not warning_path.is_absolute():
        return PurePosixPath(*warning_path.parts).as_posix()
    parts = resolved_path.parts
    for marker in ("site-packages", "dist-packages"):
        if marker in parts:
            return PurePosixPath(*parts[parts.index(marker) + 1 :]).as_posix()
    for index, part in enumerate(parts):
        if re.fullmatch(r"python\d+\.\d+", part):
            return PurePosixPath("python", *parts[index + 1 :]).as_posix()
    return resolved_path.name


def _warning_record(
    warning: warnings.WarningMessage,
    fastapi_root: Path,
    starlette_package_root: Path | None = None,
) -> dict[str, Any]:
    category = warning.category
    return {
        "category": f"{category.__module__}.{category.__qualname__}",
        "message": str(warning.message),
        "filename": _warning_filename(warning.filename, fastapi_root, starlette_package_root),
        "lineno": warning.lineno,
    }


async def _invoke_public_callable(
    function: Any,
    args: list[Any] | tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    capture_warnings: bool,
    captured_warnings: list[dict[str, Any]],
    fastapi_root: Path,
) -> Any:
    if not capture_warnings:
        result = function(*args, **kwargs)
        return await result if inspect.isawaitable(result) else result

    with warnings.catch_warnings(record=True) as emitted:
        warnings.simplefilter("always")
        try:
            result = function(*args, **kwargs)
            return await result if inspect.isawaitable(result) else result
        finally:
            captured_warnings.extend(_warning_record(warning, fastapi_root) for warning in emitted)


def _json_safe(value: Any) -> Any:
    """Project a Python result into strict JSON data, rejecting non-JSON values."""
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        return json.loads(encoded, parse_constant=_reject_constant)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError(
            f"public callable returned a value that is not strict JSON: {exc}"
        ) from exc


class _NonFiniteFloat:
    """Temporary marker used only while projecting non-finite JSON numbers."""

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value


def _json_safe_with_nonfinite(value: Any) -> tuple[Any, list[dict[str, str]]]:
    """Project JSON data while retaining non-finite float paths as sidecar metadata."""
    labels = {
        "NaN": "nan",
        "Infinity": "positive_infinity",
        "-Infinity": "negative_infinity",
    }
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=True,
            separators=(",", ":"),
        )
        decoded = json.loads(
            encoded,
            parse_constant=lambda token: _NonFiniteFloat(labels[token]),
        )
        sidecar: list[dict[str, str]] = []

        def replace_nonfinite(item: Any, path: str) -> Any:
            if isinstance(item, _NonFiniteFloat):
                sidecar.append({"path": path, "value": item.value})
                return None
            if isinstance(item, list):
                return [
                    replace_nonfinite(child, f"{path}/{index}") for index, child in enumerate(item)
                ]
            if isinstance(item, dict):
                return {
                    key: replace_nonfinite(
                        child, f"{path}/{key.replace('~', '~0').replace('/', '~1')}"
                    )
                    for key, child in item.items()
                }
            return item

        projected = replace_nonfinite(decoded, "")
        sidecar.sort(key=lambda record: record["path"])
        return projected, sidecar
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError(
            f"public callable returned a value that is not JSON-compatible: {exc}"
        ) from exc


def _pydantic_model_projection(value: Any) -> tuple[Any, list[dict[str, str]]]:
    """Project one returned Pydantic model with the fixed v4 model_dump contract."""
    from pydantic import BaseModel

    if not isinstance(value, BaseModel):
        raise TypeError("public callable result is not a pydantic.BaseModel instance")
    try:
        dumped = value.model_dump(
            mode="json",
            by_alias=True,
            exclude_unset=False,
            exclude_defaults=False,
            exclude_none=False,
            round_trip=False,
            warnings="error",
        )
        return _json_safe_with_nonfinite(dumped)
    except WorkerError as exc:
        raise ValueError(f"Pydantic model_dump projection failed: {exc}") from exc


def _signature_object_identity(value: Any, kind: str) -> dict[str, str] | None:
    module = getattr(value, "__module__", None)
    qualified_name = getattr(value, "__qualname__", None)
    if not isinstance(module, str) or not isinstance(qualified_name, str):
        return None
    return {"kind": kind, "qualified_name": f"{module}.{qualified_name}"}


def _is_strict_json_value(value: Any, *, depth: int = 0) -> bool:
    """Accept only values whose JSON projection preserves their Python types."""
    if value is None or type(value) in {bool, int, str}:
        return True
    if type(value) is float:
        return math.isfinite(value)
    if depth >= 64:
        return False
    if type(value) is list:
        return all(_is_strict_json_value(item, depth=depth + 1) for item in value)
    if type(value) is dict:
        return all(
            type(key) is str and _is_strict_json_value(item, depth=depth + 1)
            for key, item in value.items()
        )
    return False


def _signature_component(
    value: Any, *, depth: int = 0, allow_pydantic_model_defaults: bool = False
) -> Any:
    """Keep JSON defaults exact and encode non-JSON signature values without loss."""
    if value is inspect.Signature.empty:
        return None
    if depth > 8:
        raise WorkerError("signature default projection exceeded its nesting limit")
    if value is Ellipsis:
        return {"kind": "python_singleton", "name": "Ellipsis"}
    if value is PydanticUndefined:
        return {
            "kind": "python_singleton",
            "name": "PydanticUndefined",
            "qualified_name": "pydantic_core._pydantic_core.PydanticUndefinedType",
        }
    if isinstance(value, Enum):
        enum_type = type(value)
        return {
            "kind": "python_enum",
            "qualified_name": f"{enum_type.__module__}.{enum_type.__qualname__}",
            "member_name": value.name,
            "value": _signature_component(
                value.value,
                depth=depth + 1,
                allow_pydantic_model_defaults=allow_pydantic_model_defaults,
            ),
        }
    if _is_strict_json_value(value):
        return _json_safe(value)
    value_type = type(value)
    qualified_type = f"{value_type.__module__}.{value_type.__qualname__}"

    if value_type is tuple:
        return {
            "kind": "python_tuple",
            "items": [
                _signature_component(
                    item,
                    depth=depth + 1,
                    allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                )
                for item in value
            ],
        }

    if qualified_type == "fastapi.datastructures.DefaultPlaceholder":
        return {
            "kind": "fastapi_default_placeholder",
            "value": _signature_component(
                value.value,
                depth=depth + 1,
                allow_pydantic_model_defaults=allow_pydantic_model_defaults,
            ),
        }
    if allow_pydantic_model_defaults and any(
        base.__module__ == "pydantic.main" and base.__name__ == "BaseModel"
        for base in value_type.__mro__
    ):
        dumped, nonfinite_floats = _pydantic_model_projection(value)
        projection: dict[str, Any] = {
            "kind": "pydantic_model_default",
            "qualified_name": qualified_type,
            "value": dumped,
        }
        if nonfinite_floats:
            projection["nonfinite_floats"] = nonfinite_floats
        return projection
    if inspect.isclass(value):
        identity = _signature_object_identity(value, "class")
        if identity is not None:
            return identity
    elif inspect.isroutine(value):
        identity = _signature_object_identity(value, "callable")
        if identity is not None:
            return identity

    raise WorkerError(
        f"signature default cannot be represented as strict JSON without loss: {qualified_type}"
    ) from None


def _parameter_value(value: Any, *, depth: int = 0) -> Any:
    """Encode selected public parameter values without traversing object layouts."""
    if value is _PARAMETER_VALUE_MISSING:
        return {"kind": "not_present"}
    if depth > 8:
        value_type = type(value)
        return {
            "kind": "python_object",
            "python_type": f"{value_type.__module__}.{value_type.__qualname__}",
        }

    from pydantic.aliases import AliasChoices, AliasPath

    if isinstance(value, AliasPath):
        return {
            "kind": "pydantic_alias_path",
            "path": [_parameter_value(part, depth=depth + 1) for part in value.path],
        }
    if isinstance(value, AliasChoices):
        return {
            "kind": "pydantic_alias_choices",
            "choices": [_parameter_value(choice, depth=depth + 1) for choice in value.choices],
        }
    if isinstance(value, Enum):
        encoded_value = _parameter_value(value.value, depth=depth + 1)
        if isinstance(encoded_value, dict):
            value_type = type(value)
            return {
                "kind": "python_object",
                "python_type": f"{value_type.__module__}.{value_type.__qualname__}",
            }
        return {
            "kind": "python_enum",
            "qualified_name": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": encoded_value,
        }
    if isinstance(value, Decimal):
        return {"kind": "python_decimal", "value": str(value)}
    if type(value) is float and not math.isfinite(value):
        if math.isnan(value):
            label = "nan"
        else:
            label = "positive_infinity" if value > 0 else "negative_infinity"
        return {"kind": "python_nonfinite_float", "value": label}

    try:
        return _signature_component(value)
    except WorkerError:
        value_type = type(value)
        return {
            "kind": "python_object",
            "python_type": f"{value_type.__module__}.{value_type.__qualname__}",
        }


def _parameter_annotation(value: Any) -> Any:
    try:
        return project_annotation(value, _parameter_value)
    except SignatureAnnotationError:
        return _parameter_value(value)


def _parameter_attribute(value: Any, name: str) -> Any:
    try:
        return getattr(value, name)
    except AttributeError:
        return _PARAMETER_VALUE_MISSING


def _parameter_metadata_projection(value: Any) -> dict[str, Any]:
    """Project public parameter semantics, never FieldInfo or marker internals."""
    value_type = type(value)
    required_method = _parameter_attribute(value, "is_required")
    if callable(required_method):
        required: Any = required_method()
    else:
        required = _PARAMETER_VALUE_MISSING

    raw_constraints: dict[str, Any] = {}
    for name in _PARAMETER_CONSTRAINT_ATTRIBUTES:
        direct_value = _parameter_attribute(value, name)
        if direct_value is not _PARAMETER_VALUE_MISSING and direct_value is not None:
            raw_constraints[name] = direct_value
    metadata = _parameter_attribute(value, "metadata")
    if isinstance(metadata, (list, tuple)):
        for item in metadata:
            for name in _PARAMETER_CONSTRAINT_ATTRIBUTES:
                if name in raw_constraints:
                    continue
                metadata_value = _parameter_attribute(item, name)
                if metadata_value is not _PARAMETER_VALUE_MISSING and metadata_value is not None:
                    raw_constraints[name] = metadata_value

    attributes = {
        name: (
            _parameter_annotation(_parameter_attribute(value, name))
            if name == "annotation"
            else _parameter_value(_parameter_attribute(value, name))
        )
        for name in _PARAMETER_VALUE_ATTRIBUTES
    }
    return {
        "type": {"module": value_type.__module__, "name": value_type.__name__},
        "required": _parameter_value(required),
        "attributes": attributes,
        "constraints": {
            name: _parameter_value(raw_constraints[name])
            for name in _PARAMETER_CONSTRAINT_ATTRIBUTES
            if name in raw_constraints
        },
    }


def _signature_value(
    function: Any,
    *,
    allow_pydantic_model_defaults: bool = False,
    structural_signatures: bool = False,
) -> dict[str, Any]:
    signature = inspect.signature(function)
    if structural_signatures:
        try:

            def project(value: Any) -> dict[str, Any]:
                return project_annotation(
                    value,
                    lambda component: _signature_component(
                        component,
                        allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                    ),
                )

            return {
                "parameters": [
                    {
                        "name": parameter.name,
                        "kind": parameter.kind.name,
                        "has_default": parameter.default is not inspect.Parameter.empty,
                        "default": _signature_component(
                            parameter.default,
                            allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                        ),
                        "annotation": project(parameter.annotation),
                    }
                    for parameter in signature.parameters.values()
                ],
                "return_annotation": project(signature.return_annotation),
            }
        except SignatureAnnotationError as exc:
            raise WorkerError(f"signature annotation is outside reviewed domain: {exc}") from None
    return {
        "parameters": [
            {
                "name": parameter.name,
                "kind": parameter.kind.name,
                "has_default": parameter.default is not inspect.Parameter.empty,
                "default": _signature_component(
                    parameter.default,
                    allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                ),
                "annotation": (
                    None
                    if parameter.annotation is inspect.Parameter.empty
                    else str(parameter.annotation)
                ),
            }
            for parameter in signature.parameters.values()
        ],
        "return_annotation": (
            None
            if signature.return_annotation is inspect.Signature.empty
            else str(signature.return_annotation)
        ),
    }


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite number is not strict JSON: {value}")


def _resolve_public_callable(
    spec: dict[str, str], fastapi_root: Path, supported_symbols: frozenset[str]
) -> Any:
    _require_supported_callable(spec, supported_symbols)
    value = _resolve_public_attribute_value(spec, fastapi_root)
    if not callable(value):
        raise TypeError(f"public attribute is not callable: {spec['module']}.{spec['attribute']}")
    return value


def _resolve_public_attribute(
    spec: dict[str, str],
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    *,
    allow_literal_type_alias: bool = False,
) -> Any:
    _require_supported_attribute(spec, supported_symbols)
    value = _resolve_public_attribute_value(spec, fastapi_root)
    if callable(value) and not (
        allow_literal_type_alias and typing.get_origin(value) is typing.Literal
    ):
        raise TypeError(f"public attribute is callable: {spec['module']}.{spec['attribute']}")
    return value


def _resolve_public_attribute_value(spec: dict[str, str], fastapi_root: Path) -> Any:
    module_name = spec["module"]
    module = importlib.import_module(module_name)
    module_file = getattr(module, "__file__", None)
    if module_file is None or not _is_under(Path(module_file), fastapi_root / "fastapi"):
        raise WorkerError(f"public module is outside the pinned FastAPI source: {module_name}")
    value: Any = module
    for segment in spec["attribute"].split("."):
        value = getattr(value, segment)
    return value


def _public_module_observations(
    probe: dict[str, Any],
    fastapi_root: Path,
    starlette_package_root: Path | None = None,
    *,
    captured_warnings: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Project module import metadata and reviewed same-process identity relations."""
    specification = probe["public_module"]
    module_name = specification["module"]
    if captured_warnings is None:
        module = importlib.import_module(module_name)
    else:
        try:
            with warnings.catch_warnings(record=True) as emitted:
                warnings.simplefilter("always")
                module = importlib.import_module(module_name)
        finally:
            captured_warnings.extend(
                _warning_record(warning, fastapi_root, starlette_package_root)
                for warning in emitted
            )
    module_file = getattr(module, "__file__", None)
    if module_file is None or not _is_under(Path(module_file), fastapi_root / "fastapi"):
        raise WorkerError(f"public module is outside the selected FastAPI package: {module_name}")
    module_spec = getattr(module, "__spec__", None)
    if module_spec is None:
        raise WorkerError(f"public module has no import specification: {module_name}")
    parent_name, _, attribute_name = module_name.rpartition(".")
    parent = importlib.import_module(parent_name) if parent_name else None
    repeated = importlib.import_module(module_name)
    import_path = {
        "module_name": getattr(module, "__name__", ""),
        "package": getattr(module, "__package__", None),
        "spec_name": getattr(module_spec, "name", ""),
        "spec_parent": getattr(module_spec, "parent", ""),
        "is_package": module_spec.submodule_search_locations is not None,
    }
    bindings: list[dict[str, Any]] = []
    for name in specification["bindings"]:
        if name not in vars(module):
            bindings.append({"name": name, "exists": False})
            continue
        value = vars(module)[name]
        value_type = type(value)
        value_type_name = f"{value_type.__module__}.{value_type.__qualname__}"
        bindings.append(
            {
                "name": name,
                "exists": True,
                "binding_kind": (
                    "type" if inspect.isclass(value) else "callable" if callable(value) else "value"
                ),
                "module": getattr(value, "__module__", None),
                "qualname": getattr(value, "__qualname__", None),
                "python_type": value_type_name,
                "same_on_reimport": vars(repeated).get(name) is value,
            }
        )
    object_identity = {
        "module_is_sys_modules": sys.modules.get(module_name) is module,
        "module_is_parent_binding": (
            parent is not None and vars(parent).get(attribute_name) is module
        ),
        "module_is_reimport": repeated is module,
        "bindings": bindings,
    }
    observations: list[dict[str, Any]] = []
    for index, observation in enumerate(probe["observations"]):
        if observation["kind"] == "python_import_path":
            values = import_path
        elif observation["kind"] == "python_object_identity":
            values = object_identity
        else:
            raise WorkerError(f"unsupported module identity observation: {observation['kind']}")
        observations.append({"index": index, "kind": observation["kind"], "values": values})
    return observations


def _binding_identity_values(
    probe: dict[str, Any],
    public_value: Any,
    starlette_package_root: Path | None,
) -> dict[str, Any]:
    """Observe whether a FastAPI binding is the selected Starlette object itself."""
    if starlette_package_root is None:
        raise WorkerError("binding identity probe requires a selected Starlette package root")
    public_reference = probe["public_callable"]
    canonical_reference = probe["binding_identity"]
    canonical_module = importlib.import_module(canonical_reference["module"])
    canonical_module_file = getattr(canonical_module, "__file__", None)
    if canonical_module_file is None or not _is_under(
        Path(canonical_module_file), starlette_package_root
    ):
        raise WorkerError(
            "canonical binding module is outside the selected Starlette package: "
            f"{canonical_reference['module']}"
        )
    canonical_value = canonical_module
    for segment in canonical_reference["attribute"].split("."):
        canonical_value = getattr(canonical_value, segment)
    return {
        "public_symbol": f"{public_reference['module']}.{public_reference['attribute']}",
        "canonical_symbol": f"{canonical_reference['module']}.{canonical_reference['attribute']}",
        "same_object": public_value is canonical_value,
    }


def _enum_primitive_value(value: Any) -> dict[str, Any]:
    """Preserve only exact built-in primitive enum values without coercion."""
    if value is None:
        return {"type": "null", "value": None}
    if type(value) is bool:
        return {"type": "bool", "value": value}
    if type(value) is int:
        return {"type": "int", "value": value}
    if type(value) is float and math.isfinite(value):
        return {"type": "float", "value": value}
    if type(value) is str:
        return {"type": "str", "value": value}
    raise WorkerError(
        "enum values must use a supported strict primitive type "
        "(null, bool, int, finite float, or str); "
        f"got {type(value).__module__}.{type(value).__qualname__}"
    )


def _enum_class_name(enum_class: type[Enum]) -> str:
    module = enum_class.__module__
    qualname = enum_class.__qualname__
    if type(module) is not str or type(qualname) is not str:
        raise WorkerError("Enum class has malformed module or qualified name")
    return f"{module}.{qualname}"


def _enum_member_projection(
    enum_class: type[Enum], binding_name: str, member: Enum
) -> dict[str, Any]:
    """Project one selected Enum binding, including same-process identity relations."""
    member_bindings = enum_class.__members__
    if binding_name not in member_bindings or member_bindings[binding_name] is not member:
        raise WorkerError(f"selected Enum binding is not a class member: {binding_name}")
    canonical_name = member.name
    if type(canonical_name) is not str or not canonical_name:
        raise WorkerError("Enum member has a malformed canonical name")
    binding_names = [
        name for name, bound_member in member_bindings.items() if bound_member is member
    ]
    if not binding_names:
        raise WorkerError(f"Enum member has no class binding: {canonical_name}")
    value = member.value
    canonical_attribute = getattr(enum_class, canonical_name)
    name_lookup = enum_class[canonical_name]
    value_lookup = enum_class(value)
    return {
        "binding_name": binding_name,
        "binding_names": binding_names,
        "canonical_name": canonical_name,
        "is_alias": binding_name != canonical_name,
        "value": _enum_primitive_value(value),
        "repr": repr(member),
        "str": str(member),
        "identity": {
            "same_as_binding_attribute": getattr(enum_class, binding_name) is member,
            "same_as_binding_entry": member_bindings[binding_name] is member,
            "same_as_canonical_attribute": canonical_attribute is member,
            "same_as_name_lookup": name_lookup is member,
            "same_as_value_lookup": value_lookup is member,
        },
    }


def _enum_lookup_error(error: Exception) -> dict[str, Any]:
    error_type = type(error)
    return {
        "class": f"{error_type.__module__}.{error_type.__qualname__}",
        "args": _json_safe(list(error.args)),
        "message": str(error),
    }


def _enum_behavior_projection(
    probe: dict[str, Any],
    observation: dict[str, Any],
    bundles: Mapping[str, Any],
    public_value: Any,
) -> dict[str, Any]:
    """Observe an input-selected Enum operation without invoking unrelated call paths."""
    operation = observation["operation"]
    if "public_callable" in probe:
        enum_class = public_value
        if not inspect.isclass(enum_class) or not issubclass(enum_class, Enum):
            raise WorkerError("Enum class operation requires a public Enum class")
        if operation == "class_members":
            args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
            if args or kwargs:
                raise WorkerError("Enum class_members operation requires an empty argument bundle")
            return {
                "operation": operation,
                "enum_class": _enum_class_name(enum_class),
                "members": [
                    _enum_member_projection(enum_class, name, member)
                    for name, member in enum_class.__members__.items()
                ],
                "iteration_order": [member.name for member in enum_class],
            }

        args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
        if kwargs or len(args) != 1:
            raise WorkerError(
                f"Enum {operation} operation requires exactly one positional argument"
            )
        if operation == "lookup_by_name":
            name = args[0]
            if type(name) is not str:
                raise WorkerError("Enum lookup_by_name argument must be a string")
            try:
                member = enum_class[name]
            except Exception as exc:
                return {
                    "operation": operation,
                    "enum_class": _enum_class_name(enum_class),
                    "outcome": "error",
                    "error": _enum_lookup_error(exc),
                }
            binding_name = name
        elif operation == "lookup_by_value":
            value = args[0]
            _enum_primitive_value(value)
            try:
                member = enum_class(value)
            except Exception as exc:
                return {
                    "operation": operation,
                    "enum_class": _enum_class_name(enum_class),
                    "outcome": "error",
                    "error": _enum_lookup_error(exc),
                }
            binding_name = member.name if isinstance(member, Enum) else ""
        else:
            raise WorkerError(f"unsupported Enum class operation: {operation}")

        if not isinstance(member, enum_class):
            raise WorkerError("Enum lookup did not return a member of the selected class")
        return {
            "operation": operation,
            "enum_class": _enum_class_name(enum_class),
            "outcome": "member",
            "member": _enum_member_projection(enum_class, binding_name, member),
        }

    if operation != "member" or "public_attribute" not in probe:
        raise WorkerError("Enum member operation requires a public Enum member attribute")
    member = public_value
    if not isinstance(member, Enum):
        raise WorkerError("Enum member operation requires a public Enum member")
    enum_class = type(member)
    binding_name = probe["public_attribute"]["attribute"].rsplit(".", 1)[-1]
    return {
        "operation": operation,
        "enum_class": _enum_class_name(enum_class),
        "outcome": "member",
        "member": _enum_member_projection(enum_class, binding_name, member),
    }


def _require_supported_callable(spec: dict[str, str], supported_symbols: frozenset[str]) -> str:
    return _require_supported_symbol(spec, supported_symbols, label="callable")


def _require_supported_attribute(spec: dict[str, str], supported_symbols: frozenset[str]) -> str:
    return _require_supported_symbol(spec, supported_symbols, label="attribute")


def _require_supported_symbol(
    spec: dict[str, str], supported_symbols: frozenset[str], *, label: str
) -> str:
    if not isinstance(spec, dict):
        raise WorkerError(f"direct Python API {label} reference is malformed")
    module_name = spec.get("module")
    attribute = spec.get("attribute")
    if (
        not isinstance(module_name, str)
        or not isinstance(attribute, str)
        or _MODULE_PATH.fullmatch(module_name) is None
        or _ATTRIBUTE_PATH.fullmatch(attribute) is None
    ):
        raise WorkerError(f"direct Python API {label} reference is malformed")
    symbol_id = f"{module_name}.{attribute}"
    if symbol_id not in supported_symbols:
        raise WorkerError(
            "direct Python API workflow references a symbol outside the supported "
            f"pinned API atlas: {symbol_id}"
        )
    return symbol_id


def _validate_workflow_callables(
    workflow: dict[str, Any], supported_symbols: frozenset[str]
) -> None:
    cases = workflow.get("cases")
    if not isinstance(cases, list) or not cases:
        raise WorkerError("direct Python API workflow has no valid case list")
    selected: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("probes"), list):
            raise WorkerError("direct Python API workflow case has no valid probe list")
        for probe in case["probes"]:
            if not isinstance(probe, dict):
                raise WorkerError("direct Python API workflow probe is malformed")
            observations = probe.get("observations")
            if not isinstance(observations, list):
                raise WorkerError("direct Python API probe observations are malformed")
            binding_identity_selected = any(
                isinstance(observation, dict)
                and observation.get("kind")
                in {
                    "python_binding_identity",
                    "python_binding_distinct",
                }
                for observation in observations
            )
            class_docstring_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_class_docstring"
                for observation in observations
            )
            literal_type_alias_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_literal_type_alias"
                for observation in observations
            )
            exception_instance_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_exception_instance"
                for observation in observations
            )
            enum_behavior_observations = [
                observation
                for observation in observations
                if isinstance(observation, dict)
                and observation.get("kind") == "python_enum_behavior"
            ]
            bytes_return_value_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_bytes_return_value"
                for observation in observations
            )
            if bytes_return_value_selected and (
                workflow.get("schema") != WORKFLOW_SCHEMA_V15_ID
                or len(observations) != 1
                or "public_callable" not in probe
                or "argument_bundle" not in probe
                or "public_attribute" in probe
                or "public_module" in probe
                or "capture_warnings" in probe
            ):
                raise WorkerError(
                    "bytes return-value observation requires one v15 public-callable invocation"
                )
            if enum_behavior_observations:
                enum_operation = enum_behavior_observations[0].get("operation")
                if (
                    workflow.get("schema") not in {WORKFLOW_SCHEMA_V14_ID, WORKFLOW_SCHEMA_V15_ID}
                    or len(observations) != 1
                    or len(enum_behavior_observations) != 1
                    or "public_module" in probe
                    or "capture_warnings" in probe
                    or enum_operation
                    not in {"class_members", "member", "lookup_by_name", "lookup_by_value"}
                ):
                    raise WorkerError(
                        "Enum behavior requires one supported v14 public Enum operation"
                    )
                if enum_operation == "member":
                    if (
                        "public_attribute" not in probe
                        or "public_callable" in probe
                        or "argument_bundle" in probe
                    ):
                        raise WorkerError(
                            "Enum member observation requires one public Enum member attribute"
                        )
                elif (
                    "public_callable" not in probe
                    or "argument_bundle" not in probe
                    or "public_attribute" in probe
                ):
                    raise WorkerError(
                        "Enum class operation requires a public Enum class and argument bundle"
                    )
            if literal_type_alias_selected and (
                workflow.get("schema")
                not in {
                    WORKFLOW_SCHEMA_V12_ID,
                    WORKFLOW_SCHEMA_V13_ID,
                    WORKFLOW_SCHEMA_V14_ID,
                    WORKFLOW_SCHEMA_V15_ID,
                }
                or len(observations) != 1
                or "public_attribute" not in probe
                or "public_callable" in probe
                or "public_module" in probe
                or "argument_bundle" in probe
            ):
                raise WorkerError(
                    "Literal type alias observation requires one v12 through v14 "
                    "public-attribute probe"
                )
            if exception_instance_selected and (
                workflow.get("schema")
                not in {
                    WORKFLOW_SCHEMA_V13_ID,
                    WORKFLOW_SCHEMA_V14_ID,
                    WORKFLOW_SCHEMA_V15_ID,
                }
                or len(observations) != 1
                or "public_callable" not in probe
                or "argument_bundle" not in probe
                or "public_attribute" in probe
                or "public_module" in probe
            ):
                raise WorkerError(
                    "exception instance observation requires one v13 or v14 public-callable probe"
                )
            if class_docstring_selected and (
                workflow.get("schema")
                not in {
                    WORKFLOW_SCHEMA_V10_ID,
                    WORKFLOW_SCHEMA_V11_ID,
                    WORKFLOW_SCHEMA_V12_ID,
                    WORKFLOW_SCHEMA_V13_ID,
                    WORKFLOW_SCHEMA_V14_ID,
                    WORKFLOW_SCHEMA_V15_ID,
                }
                or len(observations) != 1
                or "public_callable" not in probe
                or "argument_bundle" not in probe
                or "public_attribute" in probe
            ):
                raise WorkerError(
                    "class docstring observation requires one v10 through v14 public-callable probe"
                )
            if "binding_identity" in probe or binding_identity_selected:
                binding_identity = probe.get("binding_identity")
                if (
                    workflow.get("schema")
                    not in {
                        WORKFLOW_SCHEMA_V8_ID,
                        WORKFLOW_SCHEMA_V9_ID,
                        WORKFLOW_SCHEMA_V10_ID,
                        WORKFLOW_SCHEMA_V11_ID,
                        WORKFLOW_SCHEMA_V12_ID,
                        WORKFLOW_SCHEMA_V13_ID,
                        WORKFLOW_SCHEMA_V14_ID,
                        WORKFLOW_SCHEMA_V15_ID,
                    }
                    or not binding_identity_selected
                    or len(observations) != 1
                    or "public_callable" not in probe
                    or "argument_bundle" not in probe
                    or "public_attribute" in probe
                    or "public_module" in probe
                    or not isinstance(binding_identity, dict)
                    or not isinstance(binding_identity.get("module"), str)
                    or _STARLETTE_MODULE_PATH.fullmatch(binding_identity["module"]) is None
                    or not isinstance(binding_identity.get("attribute"), str)
                    or _ATTRIBUTE_PATH.fullmatch(binding_identity["attribute"]) is None
                ):
                    raise WorkerError(
                        "cross-module binding identity requires one v8 through v14 callable probe"
                    )
            background_task_queue_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_background_task_queue"
                for observation in observations
            )
            if background_task_queue_selected:
                public_callable = probe.get("public_callable")
                invocation_selected = any(
                    isinstance(observation, dict)
                    and observation.get("kind") in {"python_return_value", "python_call_outcome"}
                    for observation in observations
                )
                if (
                    workflow.get("schema")
                    not in {
                        WORKFLOW_SCHEMA_V9_ID,
                        WORKFLOW_SCHEMA_V10_ID,
                        WORKFLOW_SCHEMA_V11_ID,
                        WORKFLOW_SCHEMA_V12_ID,
                        WORKFLOW_SCHEMA_V13_ID,
                        WORKFLOW_SCHEMA_V14_ID,
                        WORKFLOW_SCHEMA_V15_ID,
                    }
                    or not isinstance(public_callable, dict)
                    or public_callable.get("module") != "fastapi.background"
                    or public_callable.get("attribute") != "BackgroundTasks.add_task"
                    or "argument_bundle" not in probe
                    or len(observations) != 2
                    or not invocation_selected
                ):
                    raise WorkerError(
                        "BackgroundTasks queue observation requires v9 through v14, "
                        "one add_task call "
                        "and a return or call-outcome observation"
                    )
            if "public_module" in probe:
                if (
                    workflow.get("schema")
                    not in {
                        WORKFLOW_SCHEMA_V7_ID,
                        WORKFLOW_SCHEMA_V8_ID,
                        WORKFLOW_SCHEMA_V9_ID,
                        WORKFLOW_SCHEMA_V10_ID,
                        WORKFLOW_SCHEMA_V11_ID,
                        WORKFLOW_SCHEMA_V12_ID,
                        WORKFLOW_SCHEMA_V13_ID,
                        WORKFLOW_SCHEMA_V14_ID,
                        WORKFLOW_SCHEMA_V15_ID,
                    }
                    or any(
                        key in probe
                        for key in (
                            "public_callable",
                            "public_attribute",
                            "argument_bundle",
                        )
                    )
                    or (
                        "capture_warnings" in probe
                        and workflow.get("schema")
                        not in {
                            WORKFLOW_SCHEMA_V11_ID,
                            WORKFLOW_SCHEMA_V12_ID,
                            WORKFLOW_SCHEMA_V13_ID,
                            WORKFLOW_SCHEMA_V14_ID,
                            WORKFLOW_SCHEMA_V15_ID,
                        }
                    )
                    or len(observations) != 2
                    or {row.get("kind") for row in observations if isinstance(row, dict)}
                    != {"python_import_path", "python_object_identity"}
                ):
                    raise WorkerError(
                        "module identity requires one v7 through v14 module probe with both "
                        "identity "
                        "observations"
                    )
                module_spec = probe["public_module"]
                module_name = module_spec.get("module") if isinstance(module_spec, dict) else None
                bindings = module_spec.get("bindings") if isinstance(module_spec, dict) else None
                if (
                    not isinstance(module_name, str)
                    or _MODULE_PATH.fullmatch(module_name) is None
                    or not isinstance(bindings, list)
                    or not bindings
                    or any(not isinstance(name, str) for name in bindings)
                    or len(set(bindings)) != len(bindings)
                ):
                    raise WorkerError("direct Python API module reference is malformed")
                for binding in bindings:
                    if (
                        _ATTRIBUTE_PATH.fullmatch(binding) is None
                        or f"{module_name}.{binding}" not in supported_symbols
                    ):
                        raise WorkerError(
                            "direct Python API module binding is outside the supported pinned "
                            "API atlas: "
                            f"{module_name}.{binding}"
                        )
                    selected.add(f"{module_name}.{binding}")
                continue
            if any(
                isinstance(observation, dict)
                and observation.get("kind") in {"python_import_path", "python_object_identity"}
                for observation in observations
            ):
                raise WorkerError("module identity observations require a public_module probe")
            model_result_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_pydantic_model_result"
                for observation in observations
            )
            if model_result_selected and (
                workflow.get("schema")
                not in {
                    WORKFLOW_SCHEMA_V4_ID,
                    WORKFLOW_SCHEMA_V5_ID,
                    WORKFLOW_SCHEMA_V7_ID,
                    WORKFLOW_SCHEMA_V12_ID,
                    WORKFLOW_SCHEMA_V13_ID,
                    WORKFLOW_SCHEMA_V14_ID,
                    WORKFLOW_SCHEMA_V15_ID,
                }
                or len(observations) != 1
                or "public_callable" not in probe
                or "argument_bundle" not in probe
            ):
                raise WorkerError(
                    "Pydantic model result requires one supported public-callable observation"
                )
            parameter_metadata_selected = any(
                isinstance(observation, dict)
                and observation.get("kind") == "python_parameter_metadata"
                for observation in observations
            )
            if parameter_metadata_selected and (
                workflow.get("schema")
                not in {
                    WORKFLOW_SCHEMA_V6_ID,
                    WORKFLOW_SCHEMA_V7_ID,
                    WORKFLOW_SCHEMA_V12_ID,
                    WORKFLOW_SCHEMA_V13_ID,
                    WORKFLOW_SCHEMA_V14_ID,
                    WORKFLOW_SCHEMA_V15_ID,
                }
                or len(observations) != 1
                or "public_callable" not in probe
                or "argument_bundle" not in probe
            ):
                raise WorkerError(
                    "parameter metadata requires one supported public-callable observation"
                )
            if "public_callable" in probe:
                if any(
                    isinstance(observation, dict)
                    and observation.get("kind") == "python_attribute_value"
                    for observation in observations
                ):
                    raise WorkerError("python_attribute_value requires a public_attribute probe")
                selected.add(
                    _require_supported_callable(probe["public_callable"], supported_symbols)
                )
            elif "public_attribute" in probe:
                selected.add(
                    _require_supported_attribute(probe["public_attribute"], supported_symbols)
                )
            else:
                raise WorkerError("direct Python API probe has no public symbol reference")
    if not selected:
        raise WorkerError("direct Python API workflow contains no supported public symbols")


def _validate_argument_bundles(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise WorkerError("workload factory must return a non-empty mapping of argument bundles")
    if any(not isinstance(name, str) for name in value):
        raise WorkerError("argument bundle names must be strings")
    return value


def _get_arguments(
    bundles: Mapping[str, Any], name: str
) -> tuple[list[Any] | tuple[Any, ...], dict[str, Any]]:
    if name not in bundles:
        raise WorkerError(f"workload does not provide argument bundle: {name}")
    bundle = bundles[name]
    if not isinstance(bundle, Mapping) or set(bundle) != {"args", "kwargs"}:
        raise WorkerError(f"argument bundle must contain exactly args and kwargs: {name}")
    args = bundle["args"]
    kwargs = bundle["kwargs"]
    if not isinstance(args, (list, tuple)):
        raise WorkerError(f"argument bundle args must be a list or tuple: {name}")
    if not isinstance(kwargs, Mapping) or any(not isinstance(key, str) for key in kwargs):
        raise WorkerError(f"argument bundle kwargs must be a mapping with string keys: {name}")
    return args, dict(kwargs)


async def _make_bundles(factory: Any) -> Mapping[str, Any]:
    bundles = factory()
    if inspect.isawaitable(bundles):
        bundles = await bundles
    return _validate_argument_bundles(bundles)


def _background_task_queue_projection(receiver: Any) -> list[dict[str, Any]]:
    """Project the public BackgroundTasks queue without executing its callbacks."""
    try:
        tasks = receiver.tasks
    except Exception as exc:
        raise WorkerError("BackgroundTasks receiver has no readable public task queue") from exc
    if not isinstance(tasks, list):
        raise WorkerError("BackgroundTasks.tasks must be a list for this selector")

    projected_tasks: list[dict[str, Any]] = []
    for task in tasks:
        try:
            function = task.func
            args = task.args
            kwargs = task.kwargs
            is_async = task.is_async
            module = function.__module__
            qualname = function.__qualname__
        except Exception as exc:
            raise WorkerError(
                "queued BackgroundTask does not expose the declared public fields"
            ) from exc
        if (
            not callable(function)
            or not isinstance(module, str)
            or not module
            or not isinstance(qualname, str)
            or not qualname
            or not isinstance(args, (list, tuple))
            or not isinstance(kwargs, Mapping)
            or any(not isinstance(key, str) for key in kwargs)
            or type(is_async) is not bool
        ):
            raise WorkerError("queued BackgroundTask fields do not match the selector contract")
        try:
            projected_args = _json_safe(args)
            projected_kwargs = [
                {"name": key, "value": _json_safe(value)} for key, value in kwargs.items()
            ]
        except (TypeError, ValueError) as exc:
            raise WorkerError("queued BackgroundTask arguments must be strict JSON values") from exc
        projected_tasks.append(
            {
                "callable": {"module": module, "qualname": qualname},
                "args": projected_args,
                "kwargs": projected_kwargs,
                "is_async": is_async,
            }
        )
    return projected_tasks


async def _run_probe(
    probe: dict[str, Any],
    bundles: Mapping[str, Any],
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    starlette_package_root: Path | None = None,
    *,
    allow_nonfinite_floats: bool = False,
    allow_pydantic_model_defaults: bool = False,
    structural_signatures: bool = False,
) -> dict[str, Any]:
    if "public_module" in probe:
        capture_import_warnings = probe.get("capture_warnings") is True
        captured_warnings: list[dict[str, Any]] = []
        try:
            probe_result = {
                "probe_id": probe["probe_id"],
                "status": "completed",
                "observations": _public_module_observations(
                    probe,
                    fastapi_root,
                    starlette_package_root,
                    captured_warnings=(captured_warnings if capture_import_warnings else None),
                ),
            }
            if capture_import_warnings:
                probe_result["warnings"] = captured_warnings
            return probe_result
        except WorkerError:
            raise
        except Exception as exc:
            probe_result = {
                "probe_id": probe["probe_id"],
                "status": "product_error",
                "error": _error_record(exc),
                "observations": [],
            }
            if capture_import_warnings:
                probe_result["warnings"] = captured_warnings
            return probe_result
    capture_warnings = probe.get("capture_warnings") is True
    captured_warnings: list[dict[str, Any]] = []
    try:
        attribute_value = None
        if "public_attribute" in probe:
            literal_type_alias_observation = any(
                observation["kind"] == "python_literal_type_alias"
                for observation in probe["observations"]
            )
            attribute_value = _resolve_public_attribute(
                probe["public_attribute"],
                fastapi_root,
                supported_symbols,
                allow_literal_type_alias=literal_type_alias_observation,
            )
            function = None
        else:
            function = _resolve_public_callable(
                probe["public_callable"], fastapi_root, supported_symbols
            )
        has_attribute_value_observation = any(
            observation["kind"] == "python_attribute_value" for observation in probe["observations"]
        )
        has_class_docstring_observation = any(
            observation["kind"] == "python_class_docstring" for observation in probe["observations"]
        )
        has_signature_observation = any(
            observation["kind"] == "python_signature" for observation in probe["observations"]
        )
        has_return_value_observation = any(
            observation["kind"] == "python_return_value" for observation in probe["observations"]
        )
        has_bytes_return_value_observation = any(
            observation["kind"] == "python_bytes_return_value"
            for observation in probe["observations"]
        )
        has_pydantic_model_result_observation = any(
            observation["kind"] == "python_pydantic_model_result"
            for observation in probe["observations"]
        )
        has_exception_instance_observation = any(
            observation["kind"] == "python_exception_instance"
            for observation in probe["observations"]
        )
        has_parameter_metadata_observation = any(
            observation["kind"] == "python_parameter_metadata"
            for observation in probe["observations"]
        )
        has_call_outcome_observation = any(
            observation["kind"] == "python_call_outcome" for observation in probe["observations"]
        )
        signature = (
            _signature_value(
                function,
                allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                structural_signatures=structural_signatures,
            )
            if has_signature_observation
            else None
        )
        result = None
        call_outcome = None
        if (
            has_return_value_observation
            or has_bytes_return_value_observation
            or has_pydantic_model_result_observation
            or has_parameter_metadata_observation
            or has_exception_instance_observation
        ):
            args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
            result = await _invoke_public_callable(
                function,
                args,
                kwargs,
                capture_warnings=capture_warnings,
                captured_warnings=captured_warnings,
                fastapi_root=fastapi_root,
            )
        elif has_call_outcome_observation:
            args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
            try:
                result = await _invoke_public_callable(
                    function,
                    args,
                    kwargs,
                    capture_warnings=capture_warnings,
                    captured_warnings=captured_warnings,
                    fastapi_root=fastapi_root,
                )
            except Exception as exc:
                call_outcome = {"status": "raised", "error": _error_record(exc)}
            else:
                call_outcome = {"status": "returned"}
        elif capture_warnings:
            args, kwargs = _get_arguments(bundles, probe["argument_bundle"])
            result = await _invoke_public_callable(
                function,
                args,
                kwargs,
                capture_warnings=True,
                captured_warnings=captured_warnings,
                fastapi_root=fastapi_root,
            )

        observations = []
        for index, observation in enumerate(probe["observations"]):
            if observation["kind"] == "python_signature":
                values = {"signature": signature}
            elif observation["kind"] == "python_literal_type_alias":
                if (
                    typing.get_origin(attribute_value) is not typing.Literal
                    or "public_attribute" not in probe
                ):
                    raise WorkerError(
                        "Literal type alias observation requires a typing.Literal public attribute"
                    )
                arguments = typing.get_args(attribute_value)
                if not arguments or not all(_is_strict_json_value(value) for value in arguments):
                    raise WorkerError("Literal type alias arguments must be strict JSON values")
                values = {
                    "origin": "typing.Literal",
                    "arguments": _json_safe(list(arguments)),
                }
            elif observation["kind"] == "python_attribute_value":
                if not has_attribute_value_observation:
                    raise WorkerError("attribute value observation is missing its public attribute")
                if not _is_strict_json_value(attribute_value):
                    raise ValueError("public attribute value is not strict JSON")
                values = {"value": _json_safe(attribute_value)}
            elif observation["kind"] == "python_class_docstring":
                if not has_class_docstring_observation or not inspect.isclass(function):
                    raise WorkerError("class docstring observation requires a public Python class")
                values = {"value": _json_safe(function.__doc__)}
            elif observation["kind"] in {
                "python_binding_identity",
                "python_binding_distinct",
            }:
                public_value = function if "public_callable" in probe else attribute_value
                if public_value is None:
                    raise WorkerError("binding identity observation has no public object")
                values = _binding_identity_values(probe, public_value, starlette_package_root)
            elif observation["kind"] == "python_return_value":
                if allow_nonfinite_floats:
                    projected, nonfinite_floats = _json_safe_with_nonfinite(result)
                    values = {"value": projected}
                    if nonfinite_floats:
                        values["nonfinite_floats"] = nonfinite_floats
                else:
                    values = {"value": _json_safe(result)}
            elif observation["kind"] == "python_bytes_return_value":
                if type(result) is not bytes:
                    raise TypeError(
                        "bytes return-value observation requires an exact builtins.bytes result"
                    )
                values = {
                    "encoding": "base64",
                    "byte_length": len(result),
                    "value_base64": base64.b64encode(result).decode("ascii"),
                }
            elif observation["kind"] == "python_pydantic_model_result":
                projected, nonfinite_floats = _pydantic_model_projection(result)
                values = {"value": projected}
                if nonfinite_floats:
                    values["nonfinite_floats"] = nonfinite_floats
            elif observation["kind"] == "python_exception_instance":
                if not isinstance(result, BaseException):
                    raise WorkerError(
                        "exception instance observation requires a returned exception"
                    )
                public_attributes = {}
                for name in observation["attributes"]:
                    try:
                        attribute_value = getattr(result, name)
                    except AttributeError:
                        raise WorkerError(
                            f"selected public exception attribute is missing: {name}"
                        ) from None
                    public_attributes[name] = _json_safe(attribute_value)
                error_type = type(result)
                values = {
                    "class": f"{error_type.__module__}.{error_type.__qualname__}",
                    "args": _json_safe(result.args),
                    "message": str(result),
                    "representation": repr(result),
                    "attributes": public_attributes,
                }
            elif observation["kind"] == "python_enum_behavior":
                public_value = function if "public_callable" in probe else attribute_value
                values = _enum_behavior_projection(probe, observation, bundles, public_value)
            elif observation["kind"] == "python_parameter_metadata":
                values = {"parameter_metadata": _parameter_metadata_projection(result)}
            elif observation["kind"] == "python_call_outcome":
                values = {"outcome": call_outcome}
            elif observation["kind"] == "python_background_task_queue":
                args, _ = _get_arguments(bundles, probe["argument_bundle"])
                if not args:
                    raise WorkerError("BackgroundTasks queue observation has no receiver argument")
                values = {"tasks": _background_task_queue_projection(args[0])}
            else:
                raise WorkerError(f"unsupported direct API observation: {observation['kind']}")
            observations.append({"index": index, "kind": observation["kind"], "values": values})
        probe_result = {
            "probe_id": probe["probe_id"],
            "status": "completed",
            "observations": observations,
        }
        if capture_warnings:
            probe_result["warnings"] = captured_warnings
        return probe_result
    except WorkerError:
        raise
    except Exception as exc:
        probe_result = {
            "probe_id": probe["probe_id"],
            "status": "product_error",
            "error": _error_record(exc),
            "observations": [],
        }
        if capture_warnings:
            probe_result["warnings"] = captured_warnings
        return probe_result


async def _run_case(
    case: dict[str, Any],
    factory: Any,
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    starlette_package_root: Path | None = None,
    *,
    allow_nonfinite_floats: bool = False,
    allow_pydantic_model_defaults: bool = False,
    structural_signatures: bool = False,
) -> dict[str, Any]:
    bundles = (
        await _make_bundles(factory)
        if any("public_callable" in probe for probe in case["probes"])
        else {}
    )
    probes = []
    for probe in case["probes"]:
        probes.append(
            await _run_probe(
                probe,
                bundles,
                fastapi_root,
                supported_symbols,
                starlette_package_root,
                allow_nonfinite_floats=allow_nonfinite_floats,
                allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                structural_signatures=structural_signatures,
            )
        )
    errors = [probe["error"] for probe in probes if probe["status"] == "product_error"]
    result: dict[str, Any] = {
        "case_id": case["case_id"],
        "status": "product_error" if errors else "completed",
        "probes": probes,
    }
    if errors:
        result["error"] = errors[0]
    return result


async def _run_cases(
    workflow: dict[str, Any],
    factory: Any,
    fastapi_root: Path,
    supported_symbols: frozenset[str],
    starlette_package_root: Path | None = None,
    *,
    allow_nonfinite_floats: bool = False,
    allow_pydantic_model_defaults: bool = False,
    structural_signatures: bool = False,
) -> list[dict[str, Any]]:
    cases = []
    for case in workflow["cases"]:
        cases.append(
            await _run_case(
                case,
                factory,
                fastapi_root,
                supported_symbols,
                starlette_package_root,
                allow_nonfinite_floats=allow_nonfinite_floats,
                allow_pydantic_model_defaults=allow_pydantic_model_defaults,
                structural_signatures=structural_signatures,
            )
        )
    return cases


def _strict_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise WorkerError(f"duplicate object key in pinned API atlas: {key}")
        result[key] = value
    return result


def _manifest_artifact_ref(
    manifest_text: str, artifact_name: str, schema_id: str
) -> tuple[str, str]:
    """Read one narrow, fixed YAML artifact reference without oracle-only packages."""
    lines = manifest_text.splitlines()
    section_headers = [index for index, line in enumerate(lines) if line == "source_artifacts:"]
    if len(section_headers) != 1:
        raise WorkerError("manifest must contain exactly one source_artifacts mapping")
    section_start = section_headers[0] + 1
    section_end = next(
        (
            index
            for index in range(section_start, len(lines))
            if lines[index] and not lines[index][0].isspace()
        ),
        len(lines),
    )
    artifact_headers = [
        index
        for index in range(section_start, section_end)
        if lines[index] == f"  {artifact_name}:"
    ]
    if len(artifact_headers) != 1:
        raise WorkerError(f"manifest must contain exactly one {artifact_name} reference")
    artifact_start = artifact_headers[0] + 1
    atlas_end = next(
        (
            index
            for index in range(artifact_start, section_end)
            if lines[index] and not lines[index].startswith("    ")
        ),
        section_end,
    )
    fields: dict[str, str] = {}
    for line in lines[artifact_start:atlas_end]:
        match = re.fullmatch(r"    (path|schema|sha256): ([^\s#]+)", line)
        if match:
            key, value = match.groups()
            if key in fields:
                raise WorkerError(f"duplicate {artifact_name} field: {key}")
            fields[key] = value
    if (
        not fields.get("path")
        or fields.get("schema") != schema_id
        or re.fullmatch(r"[a-f0-9]{64}", fields.get("sha256", "")) is None
    ):
        raise WorkerError(f"manifest {artifact_name} reference is missing or unsupported")
    return fields["path"], fields["sha256"]


def _read_pinned_artifact(manifest_text: str, artifact_name: str, schema_id: str) -> dict[str, Any]:
    artifact_relative_path, artifact_digest = _manifest_artifact_ref(
        manifest_text, artifact_name, schema_id
    )
    artifact_path = (ROOT / artifact_relative_path).resolve()
    if not _is_under(artifact_path, ROOT) or _sha256_file(artifact_path) != artifact_digest:
        raise WorkerError(f"{artifact_name} digest differs from its manifest pin")
    try:
        artifact = json.loads(
            artifact_path.read_text(encoding="utf-8"), object_pairs_hook=_strict_json_pairs
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkerError(f"cannot read pinned {artifact_name}: {exc}") from exc
    if not isinstance(artifact, dict) or artifact.get("schema") != schema_id:
        raise WorkerError(f"{artifact_name} schema identity is unsupported")
    return artifact


def _trusted_supported_symbols(manifest_sha256: str) -> frozenset[str]:
    """Load the allowlist only from the manifest-digested, pinned FastAPI atlas."""
    if re.fullmatch(r"[a-f0-9]{64}", manifest_sha256) is None:
        raise WorkerError("manifest digest is malformed")
    if _sha256_file(MANIFEST_PATH) != manifest_sha256:
        raise WorkerError("manifest changed after host-side API workflow validation")
    try:
        manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkerError(f"cannot read pinned contract manifest: {exc}") from exc
    atlas = _read_pinned_artifact(manifest_text, "compatibility_atlas", ATLAS_SCHEMA_ID)
    authorities = atlas.get("authorities")
    if not isinstance(authorities, dict):
        raise WorkerError("compatibility atlas has no source authorities")
    for name, expected in PINNED_AUTHORITIES.items():
        authority = authorities.get(name)
        if not isinstance(authority, dict) or any(
            authority.get(key) != value for key, value in expected.items()
        ):
            raise WorkerError(
                f"compatibility atlas does not select pinned {name} {expected['version']}"
            )
    candidates = atlas.get("api_candidates")
    if not isinstance(candidates, list):
        raise WorkerError("compatibility atlas API candidates are malformed")
    supported = {
        candidate["id"]
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("classification") == "supported"
        and isinstance(candidate.get("id"), str)
    }
    inherited_candidates = atlas.get("reviewed_inherited_api_candidates", [])
    if not isinstance(inherited_candidates, list):
        raise WorkerError("compatibility atlas inherited API candidates are malformed")
    supported.update(
        candidate["id"]
        for candidate in inherited_candidates
        if isinstance(candidate, dict)
        and candidate.get("classification") == "supported"
        and isinstance(candidate.get("id"), str)
    )
    if not supported:
        raise WorkerError("compatibility atlas has no supported API candidates")
    return frozenset(supported)


def _validate_indexed_workflow(
    manifest_sha256: str,
    workflow: dict[str, Any],
    workflow_path: Path,
    input_sha256: str,
    workload_sha256: str,
    fastapi_root: Path,
) -> None:
    """Require the worker input, callable evidence, and workload to be indexed."""
    if _sha256_file(MANIFEST_PATH) != manifest_sha256:
        raise WorkerError("manifest changed after host-side API workflow validation")
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    index = _read_pinned_artifact(manifest_text, "materialized_input_index", INDEX_SCHEMA_ID)
    if index.get("authority") != {"fastapi": "0.157.0", "starlette": "1.6.0"}:
        raise WorkerError("materialized input index does not select the pinned source contract")
    relative_input = workflow_path.relative_to(ROOT).as_posix()
    matching = [
        row for row in index.get("workflows", []) if row.get("input_path") == relative_input
    ]
    if len(matching) != 1:
        raise WorkerError("direct API workflow is not uniquely indexed as a materialized input")
    indexed = matching[0]
    workload_path = workflow["workload"]["file"]
    if (
        indexed.get("input_sha256") != input_sha256
        or indexed.get("workload_path") != workload_path
        or indexed.get("workload_sha256") != workload_sha256
        or set(indexed.get("case_ids", [])) != {case.get("case_id") for case in workflow["cases"]}
    ):
        raise WorkerError("direct API workflow differs from its materialized input index entry")

    atlas = _read_pinned_artifact(manifest_text, "compatibility_atlas", ATLAS_SCHEMA_ID)
    coverage_by_id = {
        row.get("id"): row for row in atlas.get("coverage_matrix", []) if isinstance(row, dict)
    }
    mappings = [
        row for row in index.get("mappings", []) if row.get("workflow_id") == indexed.get("id")
    ]
    for case in workflow["cases"]:
        evidence = {
            (row.get("path"), row.get("kind"))
            for row in case["source_evidence"]
            if row.get("kind") != "upstream_api_definition"
        }
        expected_definitions = sorted(
            (
                {
                    "case_id": case["case_id"],
                    "symbol_id": row["symbol_id"],
                    "path": row["path"],
                    "sha256": row["sha256"],
                }
                for row in case["source_evidence"]
                if row.get("kind") == "upstream_api_definition"
            ),
            key=lambda row: (row["case_id"], row["symbol_id"], row["path"]),
        )
        indexed_definitions = [
            row
            for row in indexed.get("api_definitions", [])
            if row.get("case_id") == case["case_id"]
        ]
        if indexed_definitions != expected_definitions:
            raise WorkerError(
                f"direct API source definitions differ from indexed evidence: {case['case_id']}"
            )
        probed_symbols = {
            f"{reference['module']}.{reference['attribute']}"
            for probe in case["probes"]
            for key in ("public_callable", "public_attribute")
            if isinstance((reference := probe.get(key)), dict)
        }
        probed_symbols.update(
            f"{probe['public_module']['module']}.{binding}"
            for probe in case["probes"]
            if isinstance(probe.get("public_module"), dict)
            for binding in probe["public_module"].get("bindings", [])
        )
        if any(
            definition["symbol_id"] not in probed_symbols for definition in expected_definitions
        ):
            raise WorkerError(
                f"direct API source definition is not bound to a public probe: {case['case_id']}"
            )
        if any("public_attribute" in probe for probe in case["probes"]) and not any(
            definition["symbol_id"] in probed_symbols for definition in expected_definitions
        ):
            raise WorkerError(
                f"public attribute probe lacks API definition evidence: {case['case_id']}"
            )
        for source_evidence in case["source_evidence"]:
            source_path = (fastapi_root / source_evidence["path"]).resolve()
            if (
                not _is_under(source_path, fastapi_root)
                or not source_path.is_file()
                or _sha256_file(source_path) != source_evidence["sha256"]
            ):
                raise WorkerError(
                    f"direct API source evidence digest is stale: {source_evidence['path']}"
                )
        mapped: set[tuple[str, str]] = set()
        for mapping in mappings:
            if case["case_id"] not in mapping.get("case_ids", []):
                continue
            source = coverage_by_id.get(mapping.get("source_item_id"))
            if not isinstance(source, dict):
                raise WorkerError("materialized API mapping references missing source evidence")
            kind = (
                "upstream_documentation"
                if source.get("kind") == "documented_feature_page"
                else "upstream_test"
            )
            mapped.add((source.get("source_path"), kind))
        if (not mapped and not expected_definitions) or not mapped <= evidence:
            raise WorkerError(
                "direct API workflow case lacks indexed source evidence or an API definition: "
                f"{case['case_id']}"
            )


def _validate_result_consistency(cases: list[dict[str, Any]]) -> None:
    """Ensure status, error, and observation fields agree before emitting results."""
    for case in cases:
        probe_errors = [
            probe.get("error") for probe in case["probes"] if probe.get("status") == "product_error"
        ]
        for probe in case["probes"]:
            status = probe.get("status")
            error_present = "error" in probe
            observations = probe.get("observations")
            if status == "completed" and (error_present or not isinstance(observations, list)):
                raise WorkerError("completed API probe has contradictory error status fields")
            if status == "product_error" and (not error_present or observations != []):
                raise WorkerError("failed API probe must have an error and no observations")
        expected_status = "product_error" if probe_errors else "completed"
        if case.get("status") != expected_status:
            raise WorkerError("API case status does not match its probe statuses")
        if probe_errors:
            if case.get("error") != probe_errors[0]:
                raise WorkerError("failed API case must expose its first probe error")
        elif "error" in case:
            raise WorkerError("completed API case must not expose an error")


def _select_workflow_cases(
    workflow: dict[str, Any], requested_case_ids: list[str]
) -> dict[str, Any]:
    cases = workflow["cases"]
    available = [case["case_id"] for case in cases]
    if not requested_case_ids:
        return workflow
    if len(requested_case_ids) != len(set(requested_case_ids)):
        raise WorkerError("case selection repeats a case ID")
    requested = set(requested_case_ids)
    unknown = requested - set(available)
    if unknown:
        raise WorkerError(
            "case selection contains IDs outside the indexed workflow: "
            + ", ".join(sorted(unknown))
        )
    selected = [case for case in cases if case["case_id"] in requested]
    if not selected:
        raise WorkerError("case selection must contain at least one indexed case")
    return {**workflow, "cases": selected}


def run_oracle(
    input_path: Path,
    fastapi_root: Path,
    starlette_root: Path,
    *,
    input_sha256: str,
    workload_sha256: str,
    manifest_sha256: str,
    profile: dict[str, Any],
    case_ids: list[str],
) -> dict[str, Any]:
    if Path.cwd().resolve() != ROOT:
        raise WorkerError(f"worker must run from the repository root: {ROOT}")
    workflow_path = input_path.resolve()
    try:
        workflow_path.relative_to(ROOT)
    except ValueError as exc:
        raise WorkerError("workflow input must live inside the repository") from exc
    if _sha256_file(workflow_path) != input_sha256:
        raise WorkerError("workflow input changed after host-side validation")
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    if not isinstance(workflow, dict) or workflow.get("schema") not in WORKFLOW_SCHEMA_IDS:
        raise WorkerError("workflow schema identity changed after host-side validation")

    fastapi_root = fastapi_root.resolve()
    starlette_root = starlette_root.resolve()
    workload_path = _validate_workload_path(ROOT / workflow["workload"]["file"])
    try:
        workload_path.relative_to(ROOT)
    except ValueError as exc:
        raise WorkerError("validated workload file resolves outside the repository") from exc
    if _sha256_file(workload_path) != workload_sha256:
        raise WorkerError("workload file changed after host-side validation")

    started = dt.datetime.now(dt.UTC)
    supported_symbols = _trusted_supported_symbols(manifest_sha256)
    _validate_workflow_callables(workflow, supported_symbols)
    _validate_indexed_workflow(
        manifest_sha256,
        workflow,
        workflow_path,
        input_sha256,
        workload_sha256,
        fastapi_root,
    )
    workflow = _select_workflow_cases(workflow, case_ids)
    identity = _oracle_identity(fastapi_root, starlette_root, profile)
    factory = _load_workload(workload_path, input_sha256, workflow["workload"]["factory"])
    cases = asyncio.run(
        _run_cases(
            workflow,
            factory,
            fastapi_root,
            supported_symbols,
            starlette_root / "starlette",
            allow_nonfinite_floats=workflow["schema"]
            in {
                WORKFLOW_SCHEMA_V2_ID,
                WORKFLOW_SCHEMA_V3_ID,
                WORKFLOW_SCHEMA_V4_ID,
                WORKFLOW_SCHEMA_V5_ID,
            },
            allow_pydantic_model_defaults=workflow["schema"]
            in {WORKFLOW_SCHEMA_V4_ID, WORKFLOW_SCHEMA_V5_ID},
            structural_signatures=workflow["schema"]
            in {
                WORKFLOW_SCHEMA_V5_ID,
                WORKFLOW_SCHEMA_V6_ID,
                WORKFLOW_SCHEMA_V7_ID,
                WORKFLOW_SCHEMA_V8_ID,
                WORKFLOW_SCHEMA_V9_ID,
                WORKFLOW_SCHEMA_V10_ID,
                WORKFLOW_SCHEMA_V11_ID,
                WORKFLOW_SCHEMA_V12_ID,
                WORKFLOW_SCHEMA_V13_ID,
                WORKFLOW_SCHEMA_V14_ID,
                WORKFLOW_SCHEMA_V15_ID,
            },
        )
    )
    _validate_result_consistency(cases)
    finished = dt.datetime.now(dt.UTC)
    manifest_path = MANIFEST_PATH
    result = {
        "schema": RESULT_SCHEMA_IDS_BY_WORKFLOW[workflow["schema"]],
        "run_id": str(uuid.uuid4()),
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "product": "oracle",
        "identity": identity,
        "manifest": {"path": manifest_path.relative_to(ROOT).as_posix(), "sha256": manifest_sha256},
        "input": {
            "path": workflow_path.relative_to(ROOT).as_posix(),
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "workload": {
            "path": workload_path.relative_to(ROOT).as_posix(),
            "sha256": workload_sha256,
            "factory": workflow["workload"]["factory"],
        },
        "command": {
            "argv": [sys.executable, "-m", "scripts.parity.api_worker", *sys.argv[1:]],
            "cwd": ".",
        },
        "status": "completed",
        "cases": cases,
        "infrastructure_errors": [],
    }
    expected_cases = [case["case_id"] for case in workflow["cases"]]
    actual_cases = [case["case_id"] for case in cases]
    if actual_cases != expected_cases:
        raise WorkerError("worker case result order or cardinality differs from input")
    for specification, result_case in zip(workflow["cases"], cases, strict=True):
        expected_probes = [probe["probe_id"] for probe in specification["probes"]]
        actual_probes = [probe["probe_id"] for probe in result_case["probes"]]
        if actual_probes != expected_probes:
            raise WorkerError(
                f"worker probe result order or cardinality differs: {result_case['case_id']}"
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--fastapi-source", required=True, type=Path)
    parser.add_argument("--starlette-source", required=True, type=Path)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--workload-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--oracle-profile", required=True)
    parser.add_argument("--case-id", action="append", default=[])
    args = parser.parse_args()
    try:
        profile = json.loads(args.oracle_profile)
        if not isinstance(profile, dict) or profile.get("id") not in {
            ORACLE_PROFILE_ID,
            *ORACLE_PROFILE_PACKAGE_EXTENSIONS,
        }:
            raise WorkerError("worker received an unsupported oracle profile")
        result = run_oracle(
            args.input,
            args.fastapi_source,
            args.starlette_source,
            input_sha256=args.input_sha256,
            workload_sha256=args.workload_sha256,
            manifest_sha256=args.manifest_sha256,
            profile=profile,
            case_ids=args.case_id,
        )
    except (WorkerError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
