#!/usr/bin/env python3
"""Reflect FastAPI's pinned runtime namespace in an identity-checked oracle.

The source inventory remains the API denominator. This artifact records what
the pinned CPython/Pydantic runtime actually imports and adds dynamically; it
does not declare FastAPI-RS support or contain behavioral oracle outputs.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import hashlib
import importlib
import importlib.metadata
import inspect
import io
import json
import platform
import subprocess
import sys
import types
import typing
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FASTAPI_SOURCE = PROJECT_ROOT.parent / "fastapi"
DEFAULT_STARLETTE_SOURCE = PROJECT_ROOT.parent / "starlette"
DEFAULT_OUTPUT = PROJECT_ROOT / "tests/fixtures/runtime-api-surface.json"
EXPECTED_FASTAPI = ("0.141.1", "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f")
EXPECTED_STARLETTE = ("1.6.0", "4f250d6b814587e20c5365f0a5f0c4d42bcb929f")
EXPECTED_PYDANTIC = ("2.13.4", "2.46.4")
EXPECTED_PYTHON = ("CPython", "3.12.13")
SCHEMA = "fastapi-rs/runtime-api-surface@1"
OPTIONAL_DISTRIBUTIONS = (
    "email-validator",
    "fastapi-cli",
    "fastapi-cloud-cli",
    "fastar",
    "httpx",
    "httpx2",
    "jinja2",
    "pydantic-extra-types",
    "pydantic-settings",
    "python-multipart",
    "uvicorn",
)


class RuntimeInventoryError(RuntimeError):
    """Raised when runtime reflection uses the wrong pinned authority."""


def _git(checkout: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(checkout), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        details = getattr(exc, "stderr", "") or str(exc)
        raise RuntimeInventoryError(f"cannot identify {checkout}: {details.strip()}") from exc
    return result.stdout.strip()


def _verify_checkout(
    path: Path,
    label: str,
    expected: tuple[str, str],
    relevant_paths: tuple[str, ...],
) -> dict[str, str]:
    head = _git(path, "rev-parse", "HEAD")
    tag = _git(path, "describe", "--tags", "--exact-match", "HEAD")
    dirty = _git(path, "status", "--porcelain=v1", "--", *relevant_paths)
    if (tag, head) != expected or dirty:
        raise RuntimeInventoryError(
            f"{label} checkout mismatch: expected {expected[0]}/{expected[1]}, "
            f"observed {tag}/{head}; dirty={bool(dirty)}"
        )
    return {"version": tag, "commit": head}


def _qualified(value: Any) -> str:
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
    if isinstance(module, str) and isinstance(name, str):
        return f"{module}.{name}"
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def _annotation(value: Any) -> Any:
    if value is inspect.Parameter.empty:
        return None
    if isinstance(value, type):
        return _qualified(value)
    if isinstance(value, typing.ForwardRef):
        return {"form": "forward_ref", "expression": value.__forward_arg__}
    if isinstance(value, typing.TypeVar):
        return {
            "form": "typevar",
            "name": value.__name__,
            "bound": _annotation(value.__bound__) if value.__bound__ is not None else None,
            "constraints": [_annotation(item) for item in value.__constraints__],
        }
    origin = typing.get_origin(value)
    arguments = typing.get_args(value)
    if origin is typing.Annotated:
        base, *metadata = arguments
        return {
            "form": "annotated",
            "base": _annotation(base),
            "metadata": [_annotation_metadata(item) for item in metadata],
        }
    if origin is typing.Literal:
        return {"form": "literal", "values": list(arguments)}
    if origin is not None:
        return {
            "form": "generic",
            "origin": _qualified(origin),
            "arguments": [_annotation(argument) for argument in arguments],
        }
    if isinstance(value, str):
        return {"form": "forward_ref", "expression": value}
    return _qualified(value)


def _annotation_metadata(value: Any) -> dict[str, Any]:
    attributes = {}
    for name in ("documentation", "message", "category", "stacklevel"):
        if not hasattr(value, name):
            continue
        attribute = getattr(value, name)
        attributes[name] = (
            _qualified(attribute)
            if isinstance(attribute, type)
            else attribute
            if attribute is None or isinstance(attribute, (bool, int, float, str))
            else _qualified(attribute)
        )
    return {"type": _qualified(value), "attributes": attributes}


def _safe_default(value: Any) -> dict[str, Any]:
    if value is inspect.Parameter.empty:
        return {"kind": "empty"}
    if value is None or isinstance(value, (bool, int, float, str)):
        return {"kind": "literal", "type": type(value).__name__, "value": value}
    if isinstance(value, bytes):
        return {"kind": "bytes", "hex": value.hex()}
    if value is Ellipsis:
        return {"kind": "ellipsis"}
    return {"kind": "object", "type": _qualified(value)}


def _signature(value: Any) -> dict[str, Any] | None:
    if not (inspect.isroutine(value) or inspect.isclass(value)):
        return None
    try:
        signature = inspect.signature(value)
    except (TypeError, ValueError) as exc:
        return {"status": "unavailable", "reason": type(exc).__name__}
    return {
        "status": "available",
        "parameters": [
            {
                "name": parameter.name,
                "kind": parameter.kind.name.lower(),
                "required": parameter.default is inspect.Parameter.empty
                and parameter.kind
                not in {
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                },
                "default": _safe_default(parameter.default),
                "annotation": _annotation(parameter.annotation),
            }
            for parameter in signature.parameters.values()
        ],
        "return_annotation": _qualified(signature.return_annotation)
        if signature.return_annotation is not inspect.Signature.empty
        else None,
    }


def _object_kind(value: Any) -> str:
    if isinstance(value, types.ModuleType):
        return "module"
    if inspect.isclass(value):
        return "class"
    if inspect.isroutine(value):
        return "callable"
    return "value"


def _resolve(module: types.ModuleType, identifier: str, module_id: str) -> Any:
    suffix = identifier.removeprefix(module_id + ".")
    value: Any = module
    for component in suffix.split("."):
        value = getattr(value, component)
    return value


def _model_fields(value: Any) -> list[dict[str, Any]]:
    fields = getattr(value, "model_fields", None)
    if not isinstance(fields, dict):
        return []
    result = []
    for name, field in sorted(fields.items()):
        required = getattr(field, "is_required", None)
        result.append(
            {
                "name": name,
                "alias": getattr(field, "alias", None),
                "validation_alias": _qualified(getattr(field, "validation_alias", None))
                if getattr(field, "validation_alias", None) is not None
                else None,
                "serialization_alias": getattr(field, "serialization_alias", None),
                "annotation": _annotation(getattr(field, "annotation", object)),
                "required": bool(required()) if callable(required) else None,
                "default": _safe_default(getattr(field, "default", inspect.Parameter.empty)),
            }
        )
    return result


def _field_symbol(identifier: str, module_id: str, module: types.ModuleType) -> dict[str, Any]:
    owner_id, _, name = identifier.rpartition(".")
    owner = _resolve(module, owner_id, module_id)
    model_fields = getattr(owner, "model_fields", None)
    if isinstance(model_fields, dict) and name in model_fields:
        field = model_fields[name]
        return {
            "id": identifier,
            "kind": "pydantic_field",
            "annotation": _annotation(getattr(field, "annotation", inspect.Parameter.empty)),
            "alias": getattr(field, "alias", None),
            "required": bool(field.is_required()),
            "default": _safe_default(field.default),
        }
    if dataclasses.is_dataclass(owner):
        for field in dataclasses.fields(owner):
            if field.name == name:
                default = _safe_default(field.default)
                if field.default_factory is not dataclasses.MISSING:
                    default = {
                        "kind": "default_factory",
                        "type": _qualified(field.default_factory),
                    }
                return {
                    "id": identifier,
                    "kind": "dataclass_field",
                    "annotation": _annotation(field.type),
                    "required": field.default is dataclasses.MISSING
                    and field.default_factory is dataclasses.MISSING,
                    "default": default,
                }
    for base in getattr(owner, "__mro__", (owner,)):
        annotation = getattr(base, "__annotations__", {}).get(name)
        if annotation is not None:
            return {
                "id": identifier,
                "kind": "annotated_instance_field",
                "annotation": _annotation(annotation),
                "defined_by": _qualified(base),
            }
    raise AttributeError(name)


def _pydantic_inherited_members(value: Any) -> list[dict[str, str]]:
    if not inspect.isclass(value) or not isinstance(getattr(value, "model_fields", None), dict):
        return []
    members: dict[str, str] = {}
    for base in getattr(value, "__mro__", ())[1:]:
        module = getattr(base, "__module__", "")
        if not (module == "pydantic" or module.startswith("pydantic.")):
            continue
        for name in vars(base):
            if not name.startswith("_"):
                members.setdefault(name, f"{module}.{base.__qualname__}")
    return [{"name": name, "defined_by": owner} for name, owner in sorted(members.items())]


def _module_candidates(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in inventory["modules"]:
        module_id = row["id"]
        for definition in row["definitions"]:
            result[definition["id"]] = {
                "module": module_id,
                "source_ref": definition.get("source_ref"),
                "visibility": definition.get("visibility"),
                "kind": definition.get("kind"),
            }
            for member in definition.get("members", []):
                result[member["id"]] = {
                    "module": module_id,
                    "source_ref": member.get("source_ref"),
                    "visibility": member.get("visibility"),
                    "kind": member.get("kind"),
                }
    for binding in inventory["import_bindings"]:
        result[binding["id"]] = {
            "module": binding["module"],
            "source_ref": binding.get("source_ref"),
            "visibility": "import_binding",
            "kind": "import_binding",
        }
    return result


def _runtime_symbol(
    identifier: str,
    module_id: str,
    module: types.ModuleType,
    candidate: dict[str, Any],
) -> tuple[dict[str, Any], Any | None]:
    if candidate["kind"] == "field":
        try:
            value = _resolve(module, identifier, module_id)
        except AttributeError:
            field = _field_symbol(identifier, module_id, module)
            field["source_visibility"] = candidate["visibility"]
            field["source_kind"] = candidate["kind"]
            return field, None
    else:
        value = _resolve(module, identifier, module_id)
    symbol: dict[str, Any] = {
        "id": identifier,
        "kind": _object_kind(value),
        "object_identity": _qualified(value),
        "deprecated_metadata": getattr(value, "__deprecated__", None),
        "source_visibility": candidate["visibility"],
        "source_kind": candidate["kind"],
    }
    signature = _signature(value)
    if signature is not None:
        symbol["signature"] = signature
    fields = _model_fields(value)
    if fields:
        symbol["pydantic_model_fields"] = fields
        symbol["pydantic_generated_inherited_members"] = _pydantic_inherited_members(value)
    return symbol, value


def build_runtime_surface(
    inventory: dict[str, Any],
    *,
    fastapi_checkout: Path,
    starlette_checkout: Path,
    optional_extras: tuple[str, ...] = (),
) -> dict[str, Any]:
    fastapi_identity = _verify_checkout(
        fastapi_checkout,
        "FastAPI",
        EXPECTED_FASTAPI,
        ("fastapi", "docs/en/docs", "pyproject.toml", "uv.lock"),
    )
    starlette_identity = _verify_checkout(
        starlette_checkout,
        "Starlette",
        EXPECTED_STARLETTE,
        ("starlette", "pyproject.toml"),
    )
    if inventory.get("source_identity", {}).get("commit") != EXPECTED_FASTAPI[1]:
        raise RuntimeInventoryError("source API inventory does not match FastAPI 0.141.1")

    import fastapi
    import pydantic
    import pydantic_core
    import starlette

    if importlib.metadata.version("fastapi") != EXPECTED_FASTAPI[0]:
        raise RuntimeInventoryError("imported FastAPI package version is not 0.141.1")
    if importlib.metadata.version("starlette") != EXPECTED_STARLETTE[0]:
        raise RuntimeInventoryError("imported Starlette package version is not 1.6.0")
    if (pydantic.__version__, pydantic_core.__version__) != EXPECTED_PYDANTIC:
        raise RuntimeInventoryError("imported Pydantic runtime is not 2.13.4/2.46.4")
    python_identity = (platform.python_implementation(), platform.python_version())
    if python_identity != EXPECTED_PYTHON:
        raise RuntimeInventoryError(
            "runtime reflection requires CPython 3.12.13; "
            f"observed {python_identity[0]} {python_identity[1]}"
        )
    for label, module, checkout in (
        ("FastAPI", fastapi, fastapi_checkout / "fastapi"),
        ("Starlette", starlette, starlette_checkout / "starlette"),
    ):
        module_path = Path(module.__file__).resolve()
        try:
            module_path.relative_to(checkout.resolve())
        except ValueError as exc:
            raise RuntimeInventoryError(
                f"imported {label} does not come from the pinned local checkout"
            ) from exc

    candidates = _module_candidates(inventory)
    by_module: dict[str, list[str]] = defaultdict(list)
    for identifier, candidate in candidates.items():
        by_module[candidate["module"]].append(identifier)

    module_rows = []
    symbols = []
    alias_names: dict[int, list[str]] = defaultdict(list)
    identity_values: dict[int, Any] = {}
    runtime_only = []
    warnings_seen = []
    for module_entry in inventory["modules"]:
        module_id = module_entry["id"]
        if module_id == "fastapi.__main__":
            module_rows.append(
                {
                    "id": module_id,
                    "status": "entrypoint_import_skipped",
                    "reason": "Importing this module executes the FastAPI CLI main function.",
                    "source_declared_symbol_count": len(by_module[module_id]),
                    "source_declared_symbol_ids": sorted(by_module[module_id]),
                }
            )
            continue
        captured_stdout = io.StringIO()
        with (
            warnings.catch_warnings(record=True) as captured,
            contextlib.redirect_stdout(captured_stdout),
        ):
            warnings.simplefilter("always")
            try:
                module = importlib.import_module(module_id)
            except Exception as exc:
                detail = str(exc)
                if "fastapi[standard]" in detail or "httpx2" in detail or "jinja2" in detail:
                    status = "optional_feature_unavailable"
                else:
                    status = "import_error"
                module_rows.append(
                    {
                        "id": module_id,
                        "status": status,
                        "error_type": _qualified(type(exc)),
                        "error_message": detail,
                        "stdout": captured_stdout.getvalue(),
                        "source_declared_symbol_count": len(by_module[module_id]),
                        "source_declared_symbol_ids": sorted(by_module[module_id]),
                    }
                )
                continue
        for item in captured:
            warning = {
                "module": module_id,
                "category": _qualified(item.category),
                "message": str(item.message),
            }
            if warning not in warnings_seen:
                warnings_seen.append(warning)

        declared_ids = sorted(by_module[module_id])
        declared_names = {
            identifier.removeprefix(module_id + ".").split(".", 1)[0]
            for identifier in declared_ids
            if identifier.startswith(module_id + ".")
        }
        actual_names = {name for name in vars(module) if not name.startswith("_")}
        public_all = getattr(module, "__all__", None)
        all_names = sorted(
            {name for name in public_all if isinstance(name, str)}
            if isinstance(public_all, (list, tuple, set, frozenset))
            else []
        )
        missing = []
        for identifier in declared_ids:
            try:
                symbol, value = _runtime_symbol(
                    identifier,
                    module_id,
                    module,
                    candidates[identifier],
                )
            except (AttributeError, ImportError, RuntimeError) as exc:
                missing.append({"id": identifier, "reason": type(exc).__name__})
                continue
            symbols.append(symbol)
            if value is not None and _object_kind(value) in {"module", "class", "callable"}:
                identity = id(value)
                alias_names[identity].append(identifier)
                identity_values[identity] = value

        dynamic_names = sorted((actual_names | set(all_names)) - declared_names)
        for name in dynamic_names:
            identifier = f"{module_id}.{name}"
            value = getattr(module, name, None)
            runtime_only.append(
                {
                    "id": identifier,
                    "kind": _object_kind(value),
                    "object_identity": _qualified(value),
                    "included_in___all__": name in all_names,
                }
            )
            if value is not None and _object_kind(value) in {"module", "class", "callable"}:
                identity = id(value)
                alias_names[identity].append(identifier)
                identity_values[identity] = value
        module_rows.append(
            {
                "id": module_id,
                "status": "imported",
                "source_declared_symbol_count": len(declared_ids),
                "source_declared_symbol_ids": declared_ids,
                "source_declared_names_missing_at_runtime": missing,
                "public_runtime_name_count": len(actual_names),
                "all_names": all_names,
                "runtime_only_name_count": len(dynamic_names),
            }
        )

    alias_groups = []
    for identity, names in alias_names.items():
        unique_names = sorted(set(names))
        if len(unique_names) > 1:
            alias_groups.append(
                {
                    "object_identity": _qualified(identity_values[identity]),
                    "names": unique_names,
                }
            )
    module_rows.sort(key=lambda item: item["id"])
    symbols.sort(key=lambda item: item["id"])
    runtime_only.sort(key=lambda item: item["id"])
    alias_groups.sort(key=lambda item: (item["object_identity"], item["names"]))
    warnings_seen.sort(key=lambda item: (item["module"], item["category"], item["message"]))
    return {
        "schema": SCHEMA,
        "purpose": (
            "Identity-checked runtime reflection; not implementation support or "
            "behavioral parity evidence."
        ),
        "authority": {
            "fastapi": fastapi_identity,
            "starlette": starlette_identity,
            "python": {"implementation": python_identity[0], "version": python_identity[1]},
            "pydantic": {
                "version": pydantic.__version__,
                "pydantic_core_version": pydantic_core.__version__,
            },
            "source_inventory_sha256": hashlib.sha256(
                json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "optional_extras": list(optional_extras),
            "optional_package_versions": {
                name: importlib.metadata.version(name)
                for name in OPTIONAL_DISTRIBUTIONS
                if _distribution_available(name)
            },
        },
        "profile_limits": [
            "Only CPython 3.12.13 is reflected.",
            "fastapi.__main__ is excluded because importing it launches the CLI.",
            *(
                ["Optional FastAPI dependencies are not installed in this source-oracle profile."]
                if not optional_extras
                else []
            ),
            "Imported names and Python signatures are observations, not a support claim.",
        ],
        "modules": module_rows,
        "symbols": symbols,
        "runtime_only_names": runtime_only,
        "object_identity_alias_groups": alias_groups,
        "import_warnings": warnings_seen,
        "counts": {
            "source_modules": len(module_rows),
            "imported_modules": sum(row["status"] == "imported" for row in module_rows),
            "import_error_modules": sum(
                row["status"] in {"import_error", "optional_feature_unavailable"}
                for row in module_rows
            ),
            "entrypoint_modules_skipped": sum(
                row["status"] == "entrypoint_import_skipped" for row in module_rows
            ),
            "optional_feature_unavailable_modules": sum(
                row["status"] == "optional_feature_unavailable" for row in module_rows
            ),
            "source_symbols_reflected": len(symbols),
            "runtime_only_names": len(runtime_only),
            "object_identity_alias_groups": len(alias_groups),
            "pydantic_model_classes": sum("pydantic_model_fields" in row for row in symbols),
            "import_warnings": len(warnings_seen),
        },
    }


def _distribution_available(name: str) -> bool:
    try:
        importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    parser.add_argument("--starlette-source", type=Path, default=DEFAULT_STARLETTE_SOURCE)
    parser.add_argument(
        "--inventory",
        type=Path,
        default=PROJECT_ROOT / "tests/fixtures/api-inventory.json",
    )
    parser.add_argument(
        "--optional-extras",
        default="",
        help="Comma-separated extras/groups installed in this oracle profile.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        surface = build_runtime_surface(
            inventory,
            fastapi_checkout=args.fastapi_source.resolve(),
            starlette_checkout=args.starlette_source.resolve(),
            optional_extras=tuple(
                sorted({item.strip() for item in args.optional_extras.split(",") if item.strip()})
            ),
        )
    except (OSError, json.JSONDecodeError, RuntimeInventoryError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(surface, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "counts": surface["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
