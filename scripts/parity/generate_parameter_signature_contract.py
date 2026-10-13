"""Generate the embedded public factory signature contract from pinned FastAPI."""

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


FACTORY_NAMES = ("Path", "Query", "Header", "Cookie", "Body", "Form", "File")
SOURCE_FILE = Path("fastapi/param_functions.py")
OPENAPI_MODEL_SOURCE_FILE = Path("fastapi/openapi/models.py")
CONTRACT_SCHEMA = "fastapi-rs/parameter-factory-signature-contract@1"


def _source_revision(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def build_contract(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    if str(REPOSITORY_ROOT) not in sys.path:
        sys.path.insert(0, str(REPOSITORY_ROOT))
    sys.path.insert(0, str(source_root))
    for module_name in tuple(sys.modules):
        if module_name == "fastapi" or module_name.startswith("fastapi."):
            del sys.modules[module_name]

    fastapi = importlib.import_module("fastapi")
    if fastapi.__version__ != "0.141.1":
        raise SystemExit(f"expected FastAPI 0.141.1 at {source_root}, found {fastapi.__version__}")
    factories = importlib.import_module("fastapi.param_functions")
    openapi_models = importlib.import_module("fastapi.openapi.models")
    from scripts.parity.api_worker import _signature_component
    from scripts.parity.signature_annotations import project_annotation

    source_files = (SOURCE_FILE, OPENAPI_MODEL_SOURCE_FILE)
    source_file_hashes = {
        path.as_posix(): hashlib.sha256((source_root / path).read_bytes()).hexdigest()
        for path in source_files
    }

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

    def register_annotation(value: dict[str, Any]) -> int:
        descriptor = reference_documentation(value)
        key = json.dumps(descriptor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        index = annotation_indexes.get(key)
        if index is None:
            index = len(annotations)
            annotation_indexes[key] = index
            annotations.append(descriptor)
        return index

    factory_contracts = {}
    for name in FACTORY_NAMES:
        function = getattr(factories, name)
        signature = inspect.signature(function)
        factory_contracts[name] = {
            "module": function.__module__,
            "name": function.__name__,
            "qualname": function.__qualname__,
            "doc": function.__doc__,
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
                    "annotation_ref": register_annotation(
                        project_annotation(parameter.annotation, _signature_component)
                    ),
                }
                for parameter in signature.parameters.values()
            ],
            "return_annotation_ref": register_annotation(
                project_annotation(signature.return_annotation, _signature_component)
            ),
        }

    example_type = openapi_models.Example
    private_types = {
        "fastapi.openapi.models.Example": {
            "kind": "typed_dict",
            "name": example_type.__qualname__,
            "module": example_type.__module__,
            "total": example_type.__total__,
            "pydantic_config": example_type.__pydantic_config__,
            "fields": [
                {
                    "name": name,
                    "annotation_ref": register_annotation(
                        project_annotation(annotation, _signature_component)
                    ),
                }
                for name, annotation in example_type.__annotations__.items()
            ],
        }
    }

    return {
        "schema": CONTRACT_SCHEMA,
        "source": {
            "release": fastapi.__version__,
            "package": fastapi.__name__,
            "repository": "https://github.com/fastapi/fastapi",
            "revision": _source_revision(source_root),
            "files": [
                {"path": path.as_posix(), "sha256": source_file_hashes[path.as_posix()]}
                for path in source_files
            ],
        },
        "documentation": documentation,
        "annotations": annotations,
        "private_types": private_types,
        "factories": factory_contracts,
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
