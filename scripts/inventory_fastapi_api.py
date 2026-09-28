#!/usr/bin/env python3
"""Emit a deterministic, source-only inventory for pinned FastAPI 0.141.1.

This is discovery input for the future migration-parity manifest. It does not
import FastAPI, run an oracle, claim target support, or store parity results.
Only Python's standard library is required.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import re
import subprocess
import sys
import tokenize
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "tests" / "fixtures" / "api-inventory.json"
DEFAULT_SOURCE_CHECKOUT = PROJECT_ROOT.parent / "fastapi"
EXPECTED_VERSION = "0.141.1"
EXPECTED_TAG = "0.141.1"
EXPECTED_COMMIT = "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"
SCHEMA = "fastapi-rs/source-api-inventory@1"
DOC_TARGET = re.compile(r"^\s*:::\s+(fastapi(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*$")
LOCK_PACKAGE = re.compile(
    r"(?ms)^\[\[package\]\]\s*\n(?:(?!^\[\[package\]\]).)*?"
    r'^name = "(?P<name>[^"]+)"\s*\n'
    r'^version = "(?P<version>[^"]+)"\s*$',
)


class InventoryError(RuntimeError):
    """Raised when the source checkout is not the pinned inventory authority."""


@dataclass
class ParsedModule:
    name: str
    path: Path
    relative_path: str
    text: str
    tree: ast.Module
    sha256: str
    package: str


def run_git(checkout: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(checkout), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        details = getattr(exc, "stderr", "") or str(exc)
        raise InventoryError(f"git {' '.join(args)} failed: {details.strip()}") from exc
    return result.stdout.strip()


def validate_checkout(checkout: Path) -> dict[str, Any]:
    checkout = checkout.resolve()
    if not (checkout / ".git").exists() and not run_git(checkout, "rev-parse", "--git-dir"):
        raise InventoryError(f"not a Git checkout: {checkout}")
    head = run_git(checkout, "rev-parse", "HEAD")
    tag = run_git(checkout, "describe", "--tags", "--exact-match", "HEAD")
    tag_commit = run_git(checkout, "rev-parse", f"refs/tags/{EXPECTED_TAG}^{{commit}}")
    if head != EXPECTED_COMMIT or tag != EXPECTED_TAG or tag_commit != EXPECTED_COMMIT:
        raise InventoryError(
            "source identity mismatch: expected exact FastAPI tag/commit "
            f"{EXPECTED_TAG}/{EXPECTED_COMMIT}, observed {tag}/{head} "
            f"(tag commit {tag_commit})"
        )
    dirty = run_git(checkout, "status", "--porcelain=v1", "--", "fastapi", "docs/en/docs")
    if dirty:
        raise InventoryError(
            "FastAPI source/docs paths have local changes; refusing to inventory "
            f"a tree different from the pinned commit:\n{dirty}"
        )
    package_dir = checkout / "fastapi"
    docs_dir = checkout / "docs" / "en" / "docs"
    for required in (package_dir / "__init__.py", docs_dir / "reference"):
        if not required.exists():
            raise InventoryError(f"pinned checkout is missing {required.relative_to(checkout)}")
    try:
        init_tree = ast.parse((package_dir / "__init__.py").read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        raise InventoryError(f"cannot parse fastapi/__init__.py: {exc}") from exc
    version = None
    for node in init_tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(
                isinstance(target, ast.Name) and target.id == "__version__" for target in targets
            ):
                value = node.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    version = value.value
                break
    if version != EXPECTED_VERSION:
        raise InventoryError(
            f"package version mismatch: expected {EXPECTED_VERSION}, got {version!r}"
        )
    lock = (checkout / "uv.lock").read_text(encoding="utf-8")
    dependencies = {
        match.group("name"): match.group("version")
        for match in LOCK_PACKAGE.finditer(lock)
        if match.group("name") in {"starlette", "pydantic", "httpx"}
    }
    # This pins the dependency versions recorded in FastAPI's upstream source
    # lock for inventory provenance. Oracle and target compatibility are pinned
    # independently to Starlette 1.6.0 in the parity contract.
    expected_source_lock_components = {
        "starlette": "1.3.1",
        "pydantic": "2.13.4",
        "httpx": "0.28.1",
    }
    if dependencies != expected_source_lock_components:
        raise InventoryError(
            "FastAPI source-lock API dependency versions differ from the audited baseline: "
            f"expected {expected_source_lock_components}, observed {dependencies}"
        )
    return {
        "repository": "https://github.com/fastapi/fastapi",
        "tag": EXPECTED_TAG,
        "commit": EXPECTED_COMMIT,
        "package_version": version,
        "python_requirement": read_requires_python(checkout / "pyproject.toml"),
        "lockfile": "uv.lock",
        "locked_components": dependencies,
    }


def read_requires_python(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    project_section = re.search(r"(?ms)^\[project\]\s*\n(.*?)(?=^\[|\Z)", text)
    if project_section:
        match = re.search(r'^requires-python\s*=\s*"([^"]+)"', project_section.group(1), re.M)
        if match:
            return match.group(1)
    return None


def module_name(package_dir: Path, path: Path) -> str:
    relative = path.relative_to(package_dir).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(["fastapi", *parts]) if parts else "fastapi"


def package_name(module: str, path: Path) -> str:
    return module if path.name == "__init__.py" else module.rpartition(".")[0]


def load_modules(checkout: Path) -> dict[str, ParsedModule]:
    package_dir = checkout / "fastapi"
    modules: dict[str, ParsedModule] = {}
    for path in sorted(package_dir.rglob("*.py"), key=lambda p: p.as_posix()):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=path.as_posix(), type_comments=True)
        except SyntaxError as exc:
            raise InventoryError(f"cannot parse {path}: {exc}") from exc
        name = module_name(package_dir, path)
        modules[name] = ParsedModule(
            name=name,
            path=path,
            relative_path=path.relative_to(checkout).as_posix(),
            text=text,
            tree=tree,
            sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            package=package_name(name, path),
        )
    return modules


def node_source(module: ParsedModule, node: ast.AST | None) -> str | None:
    if node is None:
        return None
    return ast.get_source_segment(module.text, node)


def node_expr(module: ParsedModule, node: ast.AST | None) -> str | None:
    if node is None:
        return None
    raw = node_source(module, node)
    return raw if raw is not None else ast.unparse(node)


def position(node: ast.AST) -> dict[str, int]:
    result = {"line": getattr(node, "lineno", 1)}
    end_line = getattr(node, "end_lineno", None)
    if end_line is not None:
        result["end_line"] = end_line
    return result


def raw_function_header(module: ParsedModule, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Return the original `def ...:` header, preserving annotations/defaults/comments."""
    start = (node.lineno, node.col_offset)
    body_tokens = tokenize.generate_tokens(io.StringIO(module.text).readline)
    stack: list[str] = []
    parameter_list_closed = False
    colon: tokenize.TokenInfo | None = None
    for token in body_tokens:
        if token.start < start or token.type in {tokenize.ENCODING, tokenize.COMMENT}:
            continue
        if token.type == tokenize.OP:
            if token.string in "([{":
                stack.append(token.string)
            elif token.string in ")]}":
                if stack:
                    stack.pop()
                if token.string == ")" and not stack:
                    parameter_list_closed = True
            elif token.string == ":" and parameter_list_closed and not stack:
                colon = token
                break
    if colon is None:
        raise InventoryError(
            f"could not find signature terminator for {module.name}.{node.name} at {node.lineno}"
        )
    lines = module.text.splitlines(keepends=True)
    start_line, start_column = node.lineno - 1, node.col_offset
    end_line, end_column = colon.end[0] - 1, colon.end[1]
    if start_line == end_line:
        return lines[start_line][start_column:end_column]
    return (
        lines[start_line][start_column:]
        + "".join(lines[start_line + 1 : end_line])
        + lines[end_line][:end_column]
    )


def annotation_parameters(
    module: ParsedModule, node: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool
) -> list[dict[str, Any]]:
    args = node.args
    parameters: list[dict[str, Any]] = []
    positional = list(args.posonlyargs) + list(args.args)
    default_offset = len(positional) - len(args.defaults)
    positional_defaults = {
        default_offset + index: value for index, value in enumerate(args.defaults)
    }
    posonly_count = len(args.posonlyargs)

    def add(arg: ast.arg, style: str, default: ast.AST | None = None, order: int = 0) -> None:
        if (
            is_method
            and order == 0
            and arg.arg in {"self", "cls"}
            and style in {"positional", "positional_or_keyword"}
        ):
            style = "receiver"
        item: dict[str, Any] = {
            "name": arg.arg,
            "style": style,
            "annotation_source": node_source(module, arg.annotation),
            "annotation_expression": ast.unparse(arg.annotation)
            if arg.annotation is not None
            else None,
            "default_source": node_source(module, default),
            "default_expression": ast.unparse(default) if default is not None else None,
            "required": default is None
            and style not in {"variadic_positional", "variadic_keyword"},
        }
        parameters.append(item)

    all_positional = list(args.posonlyargs) + list(args.args)
    for index, arg in enumerate(all_positional):
        style = "positional" if index < posonly_count else "positional_or_keyword"
        add(arg, style, positional_defaults.get(index), index)
    if args.vararg is not None:
        add(args.vararg, "variadic_positional", order=len(parameters))
    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        add(arg, "keyword", default, len(parameters))
    if args.kwarg is not None:
        add(args.kwarg, "variadic_keyword", order=len(parameters))
    return parameters


def qualified_import(
    module: ParsedModule, imported_module: str | None, level: int, imported_name: str | None
) -> str:
    if level:
        package_parts = module.package.split(".") if module.package else []
        trim = level - 1
        if trim:
            package_parts = package_parts[:-trim]
        base_parts = package_parts
        if imported_module:
            base_parts.extend(imported_module.split("."))
        base = ".".join(base_parts)
    else:
        base = imported_module or ""
    if imported_name:
        return f"{base}.{imported_name}" if base else imported_name
    return base


def iter_import_nodes(tree: ast.Module) -> Iterable[ast.Import | ast.ImportFrom]:
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            yield node


def import_bindings(
    modules: dict[str, ParsedModule],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    bindings: list[dict[str, Any]] = []
    maps: dict[str, dict[str, str]] = {}
    for module_name_key, module in modules.items():
        local_map: dict[str, str] = {}
        for node in iter_import_nodes(module.tree):
            if isinstance(node, ast.ImportFrom):
                imported_module = node.module
                for alias in node.names:
                    local_name = alias.asname or alias.name
                    target = qualified_import(module, imported_module, node.level, alias.name)
                    explicit_identity = alias.asname == alias.name
                    root_export = module_name_key == "fastapi"
                    source_comment = module.text.splitlines()[node.lineno - 1]
                    noqa_reexport = "F401" in source_comment and "#" in source_comment
                    is_reexport = explicit_identity or root_export or noqa_reexport
                    starlette = target == "starlette" or target.startswith("starlette.")
                    binding_id = f"{module_name_key}.{local_name}"
                    local_map[local_name] = target
                    bindings.append(
                        {
                            "id": binding_id,
                            "module": module_name_key,
                            "local_name": local_name,
                            "imported_name": alias.name,
                            "imported_module": imported_module,
                            "relative_level": node.level,
                            "target_path": target,
                            "alias_spelling": alias.asname,
                            "identity_alias": explicit_identity,
                            "reexport_candidate": is_reexport,
                            "root_export": root_export,
                            "starlette_delegation": (
                                "direct_reexport"
                                if starlette and is_reexport
                                else "internal_dependency"
                                if starlette
                                else None
                            ),
                            "source_ref": {"path": module.relative_path, **position(node)},
                        }
                    )
            else:
                for alias in node.names:
                    local_name = alias.asname or alias.name.split(".")[0]
                    target = alias.name if alias.asname else alias.name.split(".")[0]
                    # `import starlette.routing as routing` binds the full module; without
                    # `as`, Python binds only the first dotted component.
                    local_map[local_name] = target
                    starlette = target == "starlette" or target.startswith("starlette.")
                    bindings.append(
                        {
                            "id": f"{module_name_key}.{local_name}",
                            "module": module_name_key,
                            "local_name": local_name,
                            "imported_name": alias.name,
                            "imported_module": None,
                            "relative_level": 0,
                            "target_path": target,
                            "alias_spelling": alias.asname,
                            "identity_alias": bool(
                                alias.asname and alias.asname == alias.name.split(".")[-1]
                            ),
                            "reexport_candidate": False,
                            "root_export": False,
                            "starlette_delegation": "internal_dependency" if starlette else None,
                            "source_ref": {"path": module.relative_path, **position(node)},
                        }
                    )
        maps[module_name_key] = local_map
    bindings.sort(key=lambda item: (item["module"], item["source_ref"]["line"], item["local_name"]))
    return bindings, maps


def call_leaf(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def literal_message(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return None
    return value if isinstance(value, str) else None


def deprecation_evidence(module: ParsedModule, node: ast.AST) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    candidates: list[tuple[str, ast.AST]] = []
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        candidates.extend(("decorator", decorator) for decorator in node.decorator_list)
        for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
            if arg.annotation is not None:
                candidates.append((f"parameter_annotation:{arg.arg}", arg.annotation))
        if node.returns is not None:
            candidates.append(("return_annotation", node.returns))
        candidates.extend(("body", child) for child in ast.walk(node))
    elif isinstance(node, ast.ClassDef):
        candidates.extend(("decorator", decorator) for decorator in node.decorator_list)
        candidates.extend(
            ("class", child) for child in node.body if isinstance(child, ast.AnnAssign)
        )
        candidates.extend(
            ("class", child) for child in ast.walk(node) if isinstance(child, ast.Call)
        )
    else:
        candidates.append(("annotation", node))
    for location, candidate in candidates:
        calls = (
            [candidate]
            if isinstance(candidate, ast.Call)
            else [part for part in ast.walk(candidate) if isinstance(part, ast.Call)]
        )
        for call in calls:
            leaf = call_leaf(call.func)
            message = literal_message(call.args[0] if call.args else None)
            category = next(
                (keyword.value for keyword in call.keywords if keyword.arg == "category"), None
            )
            marker = leaf == "deprecated"
            warning = leaf == "warn" and (message is not None and "deprecat" in message.lower())
            logged = leaf == "warning" and message is not None and "deprecat" in message.lower()
            if not (marker or warning or logged):
                continue
            key = (location, call.lineno)
            if key in seen:
                continue
            seen.add(key)
            evidence.append(
                {
                    "kind": "typing_extensions.deprecated"
                    if marker
                    else "warning_call"
                    if warning
                    else "logger_warning",
                    "scope": location,
                    "message": message,
                    "category_expression": node_expr(module, category),
                    "expression_source": node_source(module, call),
                    "source_ref": {"path": module.relative_path, **position(call)},
                }
            )
    evidence.sort(key=lambda item: (item["source_ref"]["line"], item["kind"], item["scope"]))
    return evidence


def decorator_kind(module: ParsedModule, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    decorators = [
        ast.unparse(item).split("(", 1)[0].rsplit(".", 1)[-1] for item in node.decorator_list
    ]
    if "property" in decorators:
        return "property_getter"
    if "setter" in decorators:
        return "property_setter"
    if "deleter" in decorators:
        return "property_deleter"
    if "classmethod" in decorators:
        return "classmethod"
    if "staticmethod" in decorators:
        return "staticmethod"
    if node.name.startswith("__") and node.name.endswith("__"):
        return "protocol_method"
    return "method"


def source_ref(module: ParsedModule, node: ast.AST) -> dict[str, Any]:
    return {"path": module.relative_path, **position(node)}


def function_record(
    module: ParsedModule,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    qualname: str,
    is_method: bool,
    visibility: str,
) -> dict[str, Any]:
    decorators = [
        node_source(module, decorator) or ast.unparse(decorator)
        for decorator in node.decorator_list
    ]
    return {
        "id": qualname,
        "kind": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
        "visibility": visibility,
        "signature_source": raw_function_header(module, node),
        "parameters": annotation_parameters(module, node, is_method),
        "return_annotation_source": node_source(module, node.returns),
        "return_annotation_expression": ast.unparse(node.returns)
        if node.returns is not None
        else None,
        "decorators": decorators,
        "deprecations": deprecation_evidence(module, node),
        "source_ref": source_ref(module, node),
    }


def public_visibility(name: str) -> str:
    if name == "__version__":
        return "public"
    if name.startswith("__") and name.endswith("__"):
        return "public_protocol"
    return "public" if not name.startswith("_") else "private"


def assignment_names(node: ast.Assign | ast.AnnAssign) -> list[str]:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    names: list[str] = []
    for target in targets:
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            names.extend(item.id for item in target.elts if isinstance(item, ast.Name))
    return names


def assignment_record(
    module: ParsedModule, node: ast.Assign | ast.AnnAssign, name: str, qualname: str, scope: str
) -> dict[str, Any]:
    annotation = node.annotation if isinstance(node, ast.AnnAssign) else None
    value = node.value
    return {
        "id": qualname,
        "kind": "field" if scope == "class" else "value",
        "visibility": public_visibility(name),
        "annotation_source": node_source(module, annotation),
        "annotation_expression": ast.unparse(annotation) if annotation is not None else None,
        "value_source": node_source(module, value),
        "value_expression": ast.unparse(value) if value is not None else None,
        "deprecations": deprecation_evidence(module, node),
        "source_ref": source_ref(module, node),
    }


def resolve_base(expr: ast.AST, imports: dict[str, str]) -> str:
    if isinstance(expr, ast.Name):
        return imports.get(expr.id, expr.id)
    if isinstance(expr, ast.Attribute):
        value = resolve_base(expr.value, imports)
        return f"{value}.{expr.attr}"
    return ast.unparse(expr)


def class_record(
    module: ParsedModule, node: ast.ClassDef, imports: dict[str, str]
) -> dict[str, Any]:
    qualname = f"{module.name}.{node.name}"
    members: list[dict[str, Any]] = []
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visibility = public_visibility(child.name)
            method = function_record(
                module,
                child,
                qualname=f"{qualname}.{child.name}",
                is_method=True,
                visibility=visibility,
            )
            method["kind"] = decorator_kind(module, child)
            members.append(method)
        elif isinstance(child, (ast.Assign, ast.AnnAssign)):
            for name in assignment_names(child):
                members.append(
                    assignment_record(module, child, name, f"{qualname}.{name}", "class")
                )
        elif isinstance(child, ast.ClassDef):
            members.append(
                {
                    "id": f"{qualname}.{child.name}",
                    "kind": "nested_class",
                    "visibility": public_visibility(child.name),
                    "source_ref": source_ref(module, child),
                }
            )
    bases = [
        {
            "source_expression": node_source(module, base),
            "resolved_path": resolve_base(base, imports),
        }
        for base in node.bases
    ]
    decorators = [
        node_source(module, decorator) or ast.unparse(decorator)
        for decorator in node.decorator_list
    ]
    class_options = []
    for keyword in node.keywords:
        try:
            literal_value = ast.literal_eval(keyword.value)
            literal = True
        except (ValueError, TypeError, SyntaxError):
            literal_value = None
            literal = False
        class_options.append(
            {
                "name": keyword.arg,
                "expression": node_source(module, keyword.value) or ast.unparse(keyword.value),
                "literal": literal,
                "literal_value": literal_value,
            }
        )
    starlette_bases = [
        base["resolved_path"]
        for base in bases
        if base["resolved_path"] == "starlette" or base["resolved_path"].startswith("starlette.")
    ]
    pydantic_bases = [
        base["resolved_path"]
        for base in bases
        if base["resolved_path"] == "pydantic.BaseModel"
        or base["resolved_path"].startswith("pydantic.")
    ]
    return {
        "id": qualname,
        "kind": "class",
        "visibility": public_visibility(node.name),
        "bases": bases,
        "decorators": decorators,
        "class_options": class_options,
        "members": members,
        "deprecations": deprecation_evidence(module, node),
        "starlette_delegation": {
            "classification": "subclass" if starlette_bases else None,
            "bases": starlette_bases,
            "inherited_members_enumerated": False if starlette_bases else None,
        },
        "pydantic_integration": {
            "direct_pydantic_base": bool(pydantic_bases),
            "bases": pydantic_bases,
            "direct_base_model": "pydantic.BaseModel" in pydantic_bases,
            "runtime_members_enumerated": False if pydantic_bases else None,
        },
        "source_ref": source_ref(module, node),
    }


def module_record(module: ParsedModule, imports: dict[str, str]) -> dict[str, Any]:
    definitions: list[dict[str, Any]] = []
    for node in module.tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definitions.append(
                function_record(
                    module,
                    node,
                    qualname=f"{module.name}.{node.name}",
                    is_method=False,
                    visibility=public_visibility(node.name),
                )
            )
        elif isinstance(node, ast.ClassDef):
            definitions.append(class_record(module, node, imports))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for name in assignment_names(node):
                definitions.append(
                    assignment_record(module, node, name, f"{module.name}.{name}", "module")
                )
    definitions.sort(key=lambda item: (item["source_ref"]["line"], item["id"]))
    return {
        "id": module.name,
        "source_ref": {
            "path": module.relative_path,
            "line": 1,
            "end_line": len(module.text.splitlines()),
        },
        "sha256": module.sha256,
        "definitions": definitions,
    }


def documented_targets(
    checkout: Path,
    modules: dict[str, ParsedModule],
    all_definitions: dict[str, dict[str, Any]],
    bindings_by_module: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    docs_root = checkout / "docs" / "en" / "docs"
    discovered: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(docs_root.rglob("*.md"), key=lambda item: item.as_posix()):
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            match = DOC_TARGET.match(line)
            if match:
                discovered.setdefault(match.group(1), []).append(
                    {
                        "path": path.relative_to(checkout).as_posix(),
                        "line": line_no,
                    }
                )
    module_names = set(modules)
    result: list[dict[str, Any]] = []
    for target in sorted(discovered):
        parts = target.split(".")
        resolved = None
        resolved_as = None
        for split in range(len(parts), 0, -1):
            candidate_module = ".".join(parts[:split])
            suffix = parts[split:]
            if candidate_module not in module_names:
                continue
            if not suffix:
                resolved = candidate_module
                resolved_as = "module"
                break
            local_name = suffix[0]
            symbol_id = f"{candidate_module}.{local_name}"
            if symbol_id in all_definitions:
                resolved = symbol_id
                resolved_as = "source_definition"
                break
            imported_target = bindings_by_module.get(candidate_module, {}).get(local_name)
            if imported_target:
                resolved = imported_target
                resolved_as = "import_binding"
                break
        result.append(
            {
                "id": target,
                "kind": "documented_target",
                "resolved_source_path": resolved,
                "resolution_kind": resolved_as or "unresolved",
                "references": discovered[target],
            }
        )
    return result


def document_deprecation_evidence(checkout: Path, target_name: str) -> list[dict[str, Any]]:
    docs_root = checkout / "docs" / "en" / "docs"
    leaf = target_name.rsplit(".", 1)[-1]
    evidence: list[dict[str, Any]] = []
    for path in sorted(docs_root.rglob("*.md"), key=lambda item: item.as_posix()):
        relative = path.relative_to(docs_root).as_posix()
        if relative in {"release-notes.md", "_llm-test.md"}:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if leaf not in line:
                continue
            start = max(0, index - 3)
            end = min(len(lines), index + 4)
            context = " ".join(lines[start:end])
            if "deprecat" not in context.lower():
                continue
            evidence.append(
                {
                    "kind": "nearby_documentation_mention",
                    "context": context[:360],
                    "source_ref": {
                        "path": (path.relative_to(checkout)).as_posix(),
                        "line": index + 1,
                    },
                }
            )
    unique: dict[tuple[str, int], dict[str, Any]] = {}
    for item in evidence:
        key = (item["source_ref"]["path"], item["source_ref"]["line"])
        unique[key] = item
    return [unique[key] for key in sorted(unique)]


def root_exports(
    modules: dict[str, ParsedModule], import_records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    root = modules["fastapi"]
    exports: list[dict[str, Any]] = []
    for binding in import_records:
        if binding["module"] != "fastapi":
            continue
        exports.append(
            {
                "id": f"fastapi.{binding['local_name']}",
                "name": binding["local_name"],
                "kind": "import_alias",
                "target_path": binding["target_path"],
                "starlette_delegation": binding["starlette_delegation"],
                "source_ref": binding["source_ref"],
            }
        )
    for node in root.tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        for name in assignment_names(node):
            if name.startswith("_") and name != "__version__":
                continue
            exports.append(
                {
                    "id": f"fastapi.{name}",
                    "name": name,
                    "kind": "value",
                    "value_expression": ast.unparse(node.value) if node.value is not None else None,
                    "source_ref": source_ref(root, node),
                }
            )
    exports.sort(key=lambda item: (item["source_ref"]["line"], item["id"]))
    return exports


def propagate_pydantic_models(records: list[dict[str, Any]]) -> list[str]:
    classes = {
        item["id"]: item
        for module in records
        for item in module["definitions"]
        if item["kind"] == "class"
    }
    marked: set[str] = set()
    changed = True
    while changed:
        changed = False
        for class_id, item in classes.items():
            bases = [base["resolved_path"] for base in item["bases"]]
            if class_id in marked:
                continue
            if any(base == "pydantic.BaseModel" or base in marked for base in bases):
                marked.add(class_id)
                item["pydantic_integration"]["transitive_model"] = True
                item["pydantic_integration"]["runtime_members_enumerated"] = False
                changed = True
    for class_id, item in classes.items():
        item["pydantic_integration"].setdefault("transitive_model", class_id in marked)
    return sorted(marked)


def build_inventory(checkout: Path) -> dict[str, Any]:
    checkout = checkout.resolve()
    source = validate_checkout(checkout)
    modules = load_modules(checkout)
    import_records, imports_by_module = import_bindings(modules)
    module_records = [
        module_record(module, imports_by_module[module_name])
        for module_name, module in sorted(modules.items())
    ]
    definitions = {item["id"]: item for module in module_records for item in module["definitions"]}
    targets = documented_targets(checkout, modules, definitions, imports_by_module)
    unresolved = [item["id"] for item in targets if item["resolution_kind"] == "unresolved"]
    if unresolved:
        raise InventoryError(
            f"documented targets did not resolve to source modules/bindings: {unresolved}"
        )
    for target in targets:
        target["deprecation_evidence"] = document_deprecation_evidence(checkout, target["id"])
    exports = root_exports(modules, import_records)
    pydantic_classes = propagate_pydantic_models(module_records)
    pydantic_integrations = [
        item["id"]
        for module in module_records
        for item in module["definitions"]
        if item["kind"] == "class" and item["pydantic_integration"]["direct_pydantic_base"]
    ]
    starlette_reexports = [
        item for item in import_records if item["starlette_delegation"] == "direct_reexport"
    ]
    starlette_internal = [
        item for item in import_records if item["starlette_delegation"] == "internal_dependency"
    ]
    starlette_bases = [
        {"class_id": item["id"], "base": base["resolved_path"], "source_ref": item["source_ref"]}
        for module in module_records
        for item in module["definitions"]
        if item["kind"] == "class"
        for base in item["bases"]
        if base["resolved_path"] == "starlette" or base["resolved_path"].startswith("starlette.")
    ]
    deprecations = [
        {"symbol_id": item["id"], "evidence": item["deprecations"]}
        for module in module_records
        for item in module["definitions"]
        if item.get("deprecations")
    ]
    callable_kinds = {
        "function",
        "async_function",
        "method",
        "classmethod",
        "staticmethod",
        "property_getter",
        "property_setter",
        "property_deleter",
        "protocol_method",
    }
    callables = [
        entry
        for module in module_records
        for definition in module["definitions"]
        for entry in (
            [definition]
            if definition["kind"] in {"function", "async_function"}
            else definition.get("members", [])
            if definition["kind"] == "class"
            else []
        )
        if entry["kind"] in callable_kinds
    ]
    public_classes = sum(
        1
        for module in module_records
        for definition in module["definitions"]
        if definition["kind"] == "class" and definition["visibility"] == "public"
    )
    return {
        "schema": SCHEMA,
        "purpose": "pinned FastAPI source API inventory; not a parity result, support claim, or executable manifest",
        "source_identity": source,
        "counts": {
            "python_source_modules": len(module_records),
            "documented_target_names": len(targets),
            "documented_target_occurrences": sum(len(item["references"]) for item in targets),
            "root_exports": len(exports),
            "import_bindings": len(import_records),
            "module_level_definitions": sum(
                len(module["definitions"]) for module in module_records
            ),
            "source_defined_callables": len(callables),
            "public_or_protocol_callables": sum(
                item["visibility"] in {"public", "public_protocol"} for item in callables
            ),
            "public_classes": public_classes,
            "pydantic_model_classes": len(pydantic_classes),
            "pydantic_integration_classes": len(pydantic_integrations),
            "starlette_reexport_bindings": len(starlette_reexports),
            "starlette_import_dependencies": len(starlette_internal),
            "starlette_subclass_edges": len(starlette_bases),
            "symbols_with_source_deprecation_evidence": len(deprecations),
        },
        "root_exports": exports,
        "documented_targets": targets,
        "modules": module_records,
        "import_bindings": import_records,
        "deprecations": deprecations,
        "delegated_scope": {
            "starlette": {
                "source_lock_version": source["locked_components"]["starlette"],
                "contract_owner": "Starlette-RS's separate public API manifest",
                "direct_reexports": [item["id"] for item in starlette_reexports],
                "base_edges": starlette_bases,
                "internal_imports": [item["id"] for item in starlette_internal],
                "inherited_public_members_enumerated": False,
                "gap": "The full Starlette member/API denominator is intentionally delegated; this source inventory records direct aliases, subclass edges, imported helpers, and integration dependencies only.",
            },
            "pydantic": {
                "source_lock_version": source["locked_components"]["pydantic"],
                "model_classes": pydantic_classes,
                "other_integration_classes": pydantic_integrations,
                "source_declared_members_enumerated": True,
                "runtime_generated_members_enumerated": False,
                "gap": "Pydantic-generated model_fields, validation/serialization methods, JSON-schema hooks and inherited BaseModel members are runtime API owned by pinned Pydantic and are not enumerated as FastAPI source declarations.",
            },
            "dynamic_python_surface": {
                "implicit_package_submodule_attributes_in_root_exports": False,
                "dynamic_getattr_or_runtime_signature_mutations_enumerated": False,
                "gap": "This inventory records explicit import bindings and AST-defined declarations. Runtime-created package attributes, wrappers, and __signature__ mutations require a separate live runtime reflection pass.",
            },
        },
        "inventory_limits": [
            "Importable private implementation names are present only when represented by source definitions/import bindings; they are not classified as supported public API solely because they exist.",
            "The inventory preserves source annotations and default expressions, including Annotated metadata, but does not execute them or infer their runtime type domains.",
            "Documented module targets such as fastapi.status and fastapi.openapi.models are represented as targets/modules; their delegated or generated members are identified in delegated_scope rather than expanded as FastAPI-owned declarations.",
            "Deprecation evidence is extracted from source decorators, annotations, warning calls, and nearby user-facing documentation; lifecycle semantics still require oracle behavior confirmation.",
            "No target implementation, target signatures, compatibility support, parity inputs, timings, or parity outcomes are asserted here.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source_checkout",
        nargs="?",
        type=Path,
        default=DEFAULT_SOURCE_CHECKOUT,
        help="Local FastAPI checkout at exact tag 0.141.1 (default: ../fastapi)",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="Inventory JSON output path"
    )
    args = parser.parse_args(argv)
    try:
        inventory = build_inventory(args.source_checkout)
    except InventoryError as exc:
        parser.error(str(exc))
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    output.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {output}: {inventory['counts']['documented_target_names']} documented targets, "
        f"{inventory['counts']['root_exports']} root exports, "
        f"{inventory['counts']['python_source_modules']} source modules",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
