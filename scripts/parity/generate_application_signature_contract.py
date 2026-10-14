"""Generate the embedded FastAPI application signature contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILES = (Path("fastapi/applications.py"), Path("fastapi/routing.py"))
CONTRACT_SCHEMA = "fastapi-rs/application-signature-contract@1"
SIGNATURES = (
    ("FastAPI", "fastapi", "FastAPI"),
    ("APIRoute", "fastapi.routing", "APIRoute"),
    ("operation", "fastapi.applications", "FastAPI.get"),
    ("openapi", "fastapi.applications", "FastAPI.openapi"),
    ("websocket", "fastapi.applications", "FastAPI.websocket"),
    ("include_router", "fastapi.applications", "FastAPI.include_router"),
    ("frontend", "fastapi.applications", "FastAPI.frontend"),
    ("on_event", "fastapi.applications", "FastAPI.on_event"),
    ("middleware", "fastapi.applications", "FastAPI.middleware"),
    ("exception_handler", "fastapi.applications", "FastAPI.exception_handler"),
)
EXPECTED_SOURCE_REVISION = "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"


def _source_revision(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def build_contract(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    sys.path.insert(0, str(REPOSITORY_ROOT))
    sys.path.insert(0, str(source_root))
    for module_name in tuple(sys.modules):
        if module_name == "fastapi" or module_name.startswith("fastapi."):
            del sys.modules[module_name]

    fastapi = importlib.import_module("fastapi")
    if fastapi.__version__ != "0.141.1":
        raise SystemExit(f"expected FastAPI 0.141.1 at {source_root}, found {fastapi.__version__}")
    revision = _source_revision(source_root)
    if revision != EXPECTED_SOURCE_REVISION:
        raise SystemExit(f"expected FastAPI source {EXPECTED_SOURCE_REVISION}, found {revision}")

    applications = importlib.import_module("fastapi.applications")
    routing = importlib.import_module("fastapi.routing")
    from scripts.parity.api_worker import _signature_component
    from scripts.parity.signature_annotations import project_annotation

    source_objects = {
        "FastAPI": fastapi.FastAPI,
        "APIRoute": routing.APIRoute,
        "operation": applications.FastAPI.get,
        "openapi": applications.FastAPI.openapi,
        "websocket": applications.FastAPI.websocket,
        "include_router": applications.FastAPI.include_router,
        "frontend": applications.FastAPI.frontend,
        "on_event": applications.FastAPI.on_event,
        "middleware": applications.FastAPI.middleware,
        "exception_handler": applications.FastAPI.exception_handler,
    }
    if inspect.signature(routing.APIRouter.get) != inspect.signature(applications.FastAPI.get):
        raise SystemExit(
            "FastAPI.get and APIRouter.get signatures diverge from the shared contract"
        )

    documentation: list[str] = []
    documentation_indexes: dict[str, int] = {}
    annotations: list[dict[str, Any]] = []
    annotation_indexes: dict[str, int] = {}

    def reference_documentation(value: Any) -> Any:
        if isinstance(value, list):
            return [reference_documentation(item) for item in value]
        if not isinstance(value, dict):
            return value
        if value.get("kind") == "doc":
            text = value["documentation"]
            index = documentation_indexes.get(text)
            if index is None:
                index = len(documentation)
                documentation_indexes[text] = index
                documentation.append(text)
            return {
                "kind": "doc",
                "qualified_name": value["qualified_name"],
                "documentation_ref": index,
            }
        return {key: reference_documentation(item) for key, item in value.items()}

    def register_annotation(value: Any) -> int:
        descriptor = reference_documentation(project_annotation(value, _signature_component))
        key = json.dumps(descriptor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        index = annotation_indexes.get(key)
        if index is None:
            index = len(annotations)
            annotation_indexes[key] = index
            annotations.append(descriptor)
        return index

    callables: dict[str, Any] = {}
    for contract_name, module_name, qualified_name in SIGNATURES:
        function = source_objects[contract_name]
        signature = inspect.signature(function)
        callables[contract_name] = {
            "module": module_name,
            "qualname": qualified_name,
            "parameters": [
                {
                    "name": parameter.name,
                    "kind": parameter.kind.name,
                    "has_default": parameter.default is not inspect.Parameter.empty,
                    "default": (
                        _signature_component(parameter.default)
                        if parameter.default is not inspect.Parameter.empty
                        else None
                    ),
                    "annotation_ref": register_annotation(parameter.annotation),
                }
                for parameter in signature.parameters.values()
            ],
            "return_annotation_ref": register_annotation(signature.return_annotation),
        }

    source_hashes = {
        path.as_posix(): hashlib.sha256((source_root / path).read_bytes()).hexdigest()
        for path in SOURCE_FILES
    }
    return {
        "schema": CONTRACT_SCHEMA,
        "source": {
            "distribution": "fastapi",
            "release": fastapi.__version__,
            "repository": "https://github.com/fastapi/fastapi",
            "revision": revision,
            "files": [
                {"path": path.as_posix(), "sha256": source_hashes[path.as_posix()]}
                for path in SOURCE_FILES
            ],
        },
        "documentation": documentation,
        "annotations": annotations,
        "callables": callables,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastapi-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    contract = build_contract(arguments.fastapi_source)
    arguments.output.write_text(
        json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
