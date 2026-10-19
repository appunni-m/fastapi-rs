from __future__ import annotations

import argparse
import inspect
import json
import subprocess
import sys
import typing
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "fastapi-rs" / "src" / "route_signature.json"
FASTAPI_VERSION = "0.141.1"
FASTAPI_REVISION = "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"
STARLETTE_VERSION = "1.6.0"
STARLETTE_REVISION = "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"
CALLABLES = {
    "FastAPI.__init__": ("FastAPI", "__init__"),
    "FastAPI.__call__": ("FastAPI", "__call__"),
}


class SignatureContractError(ValueError):
    pass


def _qualified_name(value: Any) -> str:
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
    if not isinstance(module, str) or not isinstance(name, str):
        raise SignatureContractError(f"cannot qualify signature component {value!r}")
    return f"{module}.{name}"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


class SignatureContractCapture:
    def __init__(self, contract: dict[str, Any], default_placeholder_type: type[Any]) -> None:
        self.documentation = contract["documentation"]
        self.annotations = contract["annotations"]
        self._documentation_indices = {
            value: index for index, value in enumerate(self.documentation)
        }
        self._annotation_indices = {
            _canonical(value): index for index, value in enumerate(self.annotations)
        }
        self.default_placeholder_type = default_placeholder_type

    def _intern_documentation(self, value: str) -> int:
        index = self._documentation_indices.get(value)
        if index is None:
            index = len(self.documentation)
            self.documentation.append(value)
            self._documentation_indices[value] = index
        return index

    def _intern_annotation(self, descriptor: dict[str, Any]) -> int:
        canonical = _canonical(descriptor)
        index = self._annotation_indices.get(canonical)
        if index is None:
            index = len(self.annotations)
            self.annotations.append(descriptor)
            self._annotation_indices[canonical] = index
        return index

    def _metadata(self, value: Any) -> dict[str, Any]:
        metadata_type = type(value)
        qualified_name = _qualified_name(metadata_type)
        if qualified_name == "annotated_doc.main.Doc":
            documentation = getattr(value, "documentation", None)
            if not isinstance(documentation, str):
                raise SignatureContractError("Doc metadata has no string documentation")
            return {
                "documentation_ref": self._intern_documentation(documentation),
                "kind": "doc",
                "qualified_name": qualified_name,
            }
        if qualified_name == "typing_extensions.deprecated":
            category = getattr(value, "category", DeprecationWarning)
            return {
                "category": self._annotation(category),
                "kind": "deprecated",
                "message": value.message,
                "qualified_name": qualified_name,
                "stacklevel": value.stacklevel,
            }
        raise SignatureContractError(f"unsupported Annotated metadata: {qualified_name}")

    def _annotation_sequence(self, values: list[Any] | tuple[Any, ...]) -> dict[str, Any]:
        return {
            "items": [self._annotation(value) for value in values],
            "kind": "annotation_sequence",
            "python_type": _qualified_name(type(values)),
        }

    def _annotation(self, value: Any) -> dict[str, Any]:
        if value is inspect.Signature.empty:
            return {"kind": "empty"}
        if value is None:
            return {"kind": "literal", "python_type": "builtins.NoneType", "value": None}
        if value is Ellipsis:
            return {"kind": "ellipsis"}
        if isinstance(value, typing.ForwardRef):
            return {
                "argument": value.__forward_arg__,
                "is_argument": value.__forward_is_argument__,
                "is_class": value.__forward_is_class__,
                "kind": "forward_ref",
                "module": value.__forward_module__,
                "python_type": "typing.ForwardRef",
            }
        if type(value).__name__ == "TypeVar" and type(value).__module__ == "typing":
            return {
                "bound": self._annotation(value.__bound__),
                "constraints": [self._annotation(item) for item in value.__constraints__],
                "contravariant": value.__contravariant__,
                "covariant": value.__covariant__,
                "infer_variance": getattr(value, "__infer_variance__", None),
                "kind": "type_variable",
                "module": value.__module__,
                "name": value.__name__,
                "python_type": "typing.TypeVar",
            }
        origin = typing.get_origin(value)
        if origin is typing.Annotated:
            arguments = typing.get_args(value)
            return {
                "alias_name": "Annotated",
                "base": self._annotation(arguments[0]),
                "kind": "annotated",
                "metadata": [self._metadata(item) for item in arguments[1:]],
                "python_type": _qualified_name(type(value)),
            }
        if origin is not None:
            arguments = typing.get_args(value)
            return {
                "alias_name": None,
                "arguments": [
                    self._annotation_sequence(item)
                    if isinstance(item, (list, tuple))
                    else self._annotation(item)
                    for item in arguments
                ],
                "kind": "generic",
                "origin": _qualified_name(origin),
                "python_type": _qualified_name(type(value)),
            }
        if isinstance(value, (str, int, float, bool)):
            return {
                "kind": "literal",
                "python_type": _qualified_name(type(value)),
                "value": value,
            }
        if isinstance(value, type):
            return {
                "kind": "type",
                "python_type": "builtins.type",
                "qualified_name": _qualified_name(value),
            }
        if _qualified_name(value) == "typing.Any":
            return {
                "kind": "typing_form",
                "python_type": _qualified_name(type(value)),
                "qualified_name": "typing.Any",
            }
        raise SignatureContractError(f"unsupported signature annotation: {value!r}")

    def _default(self, value: Any) -> Any:
        if isinstance(value, self.default_placeholder_type):
            return {
                "kind": "fastapi_default_placeholder",
                "value": self._default(value.value),
            }
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if value is Ellipsis:
            return {"kind": "python_singleton", "name": "Ellipsis"}
        if inspect.isclass(value):
            return {"kind": "class", "qualified_name": _qualified_name(value)}
        if callable(value):
            return {"kind": "callable", "qualified_name": _qualified_name(value)}
        raise SignatureContractError(f"unsupported signature default: {value!r}")

    def capture(self, function: Any) -> dict[str, Any]:
        signature = inspect.signature(function)
        parameters = []
        for parameter in signature.parameters.values():
            item = {
                "annotation_ref": self._intern_annotation(self._annotation(parameter.annotation)),
                "has_default": parameter.default is not inspect.Parameter.empty,
                "kind": parameter.kind.name,
                "name": parameter.name,
            }
            if item["has_default"]:
                item["default"] = self._default(parameter.default)
            parameters.append(item)
        return {
            "parameters": parameters,
            "return_annotation_ref": self._intern_annotation(
                self._annotation(signature.return_annotation)
            ),
        }


def _git_revision(source: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture pinned FastAPI application signatures into the Rust contract."
    )
    parser.add_argument("--fastapi-source", type=Path, default=ROOT.parent / "fastapi")
    parser.add_argument("--starlette-source", type=Path, default=ROOT.parent / "starlette")
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    fastapi_source = args.fastapi_source.resolve()
    starlette_source = args.starlette_source.resolve()
    sys.path.insert(0, str(starlette_source))
    sys.path.insert(0, str(fastapi_source))

    import fastapi
    import starlette
    from fastapi.applications import FastAPI
    from fastapi.datastructures import DefaultPlaceholder

    if fastapi.__version__ != FASTAPI_VERSION or _git_revision(fastapi_source) != FASTAPI_REVISION:
        raise SignatureContractError("FastAPI source identity does not match the pinned contract")
    if (
        starlette.__version__ != STARLETTE_VERSION
        or _git_revision(starlette_source) != STARLETTE_REVISION
    ):
        raise SignatureContractError("Starlette source identity does not match the pinned contract")
    if not Path(fastapi.__file__).resolve().is_relative_to(fastapi_source / "fastapi"):
        raise SignatureContractError("FastAPI import did not resolve inside the pinned source")
    if not Path(starlette.__file__).resolve().is_relative_to(starlette_source / "starlette"):
        raise SignatureContractError("Starlette import did not resolve inside the pinned source")

    contract_path = args.contract.resolve()
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["source"]["revision"] != FASTAPI_REVISION:
        raise SignatureContractError("signature contract source revision is not FastAPI 0.141.1")
    capture = SignatureContractCapture(contract, DefaultPlaceholder)
    for contract_name, (owner_name, member_name) in CALLABLES.items():
        owner = {"FastAPI": FastAPI}[owner_name]
        contract["callables"][contract_name] = capture.capture(getattr(owner, member_name))

    output = json.dumps(contract, ensure_ascii=False, indent=2) + "\n"
    current = contract_path.read_text(encoding="utf-8")
    if args.check:
        if current != output:
            print("application signature contract is stale")
            return 1
        print(f"application signature contract current: {len(CALLABLES)} FastAPI callables")
        return 0
    contract_path.write_text(output, encoding="utf-8")
    print(f"updated {contract_path.relative_to(ROOT)} with {len(CALLABLES)} FastAPI callables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
