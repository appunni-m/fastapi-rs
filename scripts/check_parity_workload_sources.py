#!/usr/bin/env python3
"""Statically screen executable parity workloads for test and output leakage."""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_parity_inputs import RECIPE_DIR, read_recipe
from scripts.parity.contract import ROOT, ContractError
from scripts.parity.process_contract import PROCESS_WORKFLOW_SCHEMA_IDS

WORKLOAD_ROOT = (ROOT / "tests/fixtures/workloads").resolve()
DEFAULT_FASTAPI_SOURCE = (ROOT / "../fastapi").resolve()
TEST_FRAMEWORKS = frozenset({"doctest", "hypothesis", "nose", "pytest", "unittest"})
OUTPUT_WORDS = frozenset(
    {
        "body",
        "bytes",
        "content",
        "error",
        "errors",
        "exception",
        "exceptions",
        "event",
        "events",
        "document",
        "file",
        "headers",
        "html",
        "image",
        "json",
        "messages",
        "metric",
        "metrics",
        "openapi",
        "output",
        "outputs",
        "response",
        "responses",
        "result",
        "results",
        "schema",
        "stderr",
        "stdout",
        "status",
        "statuscode",
        "text",
        "trace",
        "value",
        "values",
        "warning",
        "warnings",
    }
)
OUTPUT_SOURCE_MARKERS = frozenset({"expected", "golden", "oracle", "reference"})


class _LiteralNormalizer(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        if node.value is None:
            kind = "null"
        elif isinstance(node.value, bool):
            kind = "boolean"
        elif isinstance(node.value, str):
            kind = "string"
        elif isinstance(node.value, bytes):
            kind = "bytes"
        elif isinstance(node.value, (int, float, complex)):
            kind = "number"
        else:
            kind = type(node.value).__name__
        return ast.copy_location(ast.Constant(value=f"<{kind}>"), node)


def _body_fingerprint(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    body = list(node.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body.pop(0)
    normalized = _LiteralNormalizer().visit(ast.Module(body=body, type_ignores=[]))
    normalized_body = ast.dump(normalized, include_attributes=False)
    return hashlib.sha256(normalized_body.encode("utf-8")).hexdigest()


def _load_upstream_test_bodies(
    source_test_paths: set[Path], source_root: Path
) -> dict[str, list[str]]:
    fingerprints: dict[str, list[str]] = {}
    for source_path in sorted(source_test_paths):
        relative_path = source_path.relative_to(source_root).as_posix()
        try:
            source = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ContractError(f"cannot read upstream test source {relative_path}: {exc}") from exc
        try:
            tree = ast.parse(source, filename=relative_path)
        except SyntaxError as exc:
            raise ContractError(
                f"cannot parse upstream test source {relative_path}:{exc.lineno or 1}: {exc.msg}"
            ) from exc
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue
            location = f"{relative_path}:{node.lineno} ({node.name})"
            fingerprints.setdefault(_body_fingerprint(node), []).append(location)
    return fingerprints


def _parity_workload_paths(
    source_root: Path,
) -> tuple[int, list[Path], set[Path], set[Path]]:
    recipes = sorted(RECIPE_DIR.glob("*.yaml"))
    if not recipes:
        raise ContractError(f"no active parity recipes found under {RECIPE_DIR}")

    workload_paths: set[Path] = set()
    test_module_paths: set[Path] = set()
    source_scan_paths: set[Path] = set()
    resolved_source_root = source_root.resolve()
    upstream_tests_root = resolved_source_root / "tests"
    if not upstream_tests_root.is_dir():
        raise ContractError(
            f"pinned FastAPI test source tree does not exist: {upstream_tests_root}"
        )

    for source_path in upstream_tests_root.rglob("test*.py"):
        if not source_path.is_file():
            continue
        resolved_source_path = source_path.resolve()
        try:
            resolved_source_path.relative_to(resolved_source_root)
        except ValueError as exc:
            raise ContractError(
                "upstream test module resolves outside the pinned FastAPI source tree: "
                f"{source_path}"
            ) from exc
        test_module_paths.add(resolved_source_path)
        source_scan_paths.add(resolved_source_path)

    for recipe_path in recipes:
        recipe = read_recipe(recipe_path)
        if recipe.get("schema") not in PROCESS_WORKFLOW_SCHEMA_IDS:
            workload = recipe.get("workload")
            if not isinstance(workload, dict) or not isinstance(workload.get("file"), str):
                raise ContractError(
                    f"active parity recipe has no workload file reference: "
                    f"{recipe_path.relative_to(ROOT)}"
                )
            workload_path = (ROOT / workload["file"]).resolve()
            try:
                workload_path.relative_to(WORKLOAD_ROOT)
            except ValueError as exc:
                raise ContractError(
                    f"active workload resolves outside tests/fixtures/workloads: {workload['file']}"
                ) from exc
            if not workload_path.is_file():
                raise ContractError(f"active workload does not exist: {workload['file']}")
            workload_paths.add(workload_path)

        for case in recipe.get("cases", []):
            for evidence in case.get("source_evidence", []):
                if evidence.get("kind") != "upstream_test":
                    continue
                source_path = (resolved_source_root / evidence["path"]).resolve()
                try:
                    source_path.relative_to(resolved_source_root)
                except ValueError as exc:
                    raise ContractError(
                        "upstream test evidence resolves outside the pinned FastAPI source tree: "
                        f"{evidence['path']}"
                    ) from exc
                if not source_path.is_file():
                    raise ContractError(
                        f"upstream test evidence does not exist: {evidence['path']}"
                    )
                source_scan_paths.add(source_path)

    for workload_path in WORKLOAD_ROOT.rglob("*.py"):
        if not workload_path.is_file():
            continue
        resolved_workload_path = workload_path.resolve()
        try:
            resolved_workload_path.relative_to(WORKLOAD_ROOT)
        except ValueError as exc:
            raise ContractError(
                f"workload module resolves outside tests/fixtures/workloads: {workload_path}"
            ) from exc
        workload_paths.add(resolved_workload_path)

    return len(recipes), sorted(workload_paths), test_module_paths, source_scan_paths


class _WorkloadSourceVisitor(ast.NodeVisitor):
    def __init__(
        self,
        *,
        source_test_bodies: dict[str, list[str]],
    ) -> None:
        self.function_stack: list[str] = []
        self.findings: list[tuple[int, str]] = []
        self.source_test_bodies = source_test_bodies
        self.assertion_aliases: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_output_name(node.name, node.lineno)
        self.generic_visit(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if node.name.startswith("test_"):
            self.findings.append((node.lineno, f"test-named function: {node.name}"))
        self._check_output_name(node.name, node.lineno)
        for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            self._check_output_name(argument.arg, argument.lineno)
        copied_from = self.source_test_bodies.get(_body_fingerprint(node))
        if copied_from:
            self.findings.append(
                (
                    node.lineno,
                    "function body matches upstream test code after literal normalization from "
                    + ", ".join(copied_from[:3]),
                )
            )
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_Assert(self, node: ast.Assert) -> None:
        self.findings.append(
            (
                node.lineno,
                "assert statement in parity workload",
            )
        )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._check_import(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None:
            self._check_import(node.module, node.lineno)
        for alias in node.names:
            if _is_assertion_method(alias.name):
                local_name = alias.asname or alias.name
                self.assertion_aliases.add(local_name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        else:
            name = None
        if name is not None and (_is_assertion_method(name) or name in self.assertion_aliases):
            self.findings.append((node.lineno, f"assertion helper call: {name}"))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        self._check_output_name(node.id, node.lineno)
        if node.id.casefold() == "testclient":
            self.findings.append((node.lineno, "TestClient use in parity workload"))
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self._check_output_name(node.attr, node.lineno)
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg is not None:
            self._check_output_name(node.arg, node.value.lineno)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if any(
            isinstance(target, ast.Name) and target.id.casefold() == "expected"
            for target in node.targets
        ):
            self.findings.append((node.lineno, "stored value named expected"))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and node.target.id.casefold() == "expected":
            self.findings.append((node.lineno, "stored value named expected"))
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if key.value.casefold() == "expected" or _is_expected_output_name(key.value):
                    self.findings.append((key.lineno, f"expected-output mapping key: {key.value}"))
        self.generic_visit(node)

    def _check_import(self, module: str, lineno: int) -> None:
        parts = module.split(".")
        if parts[0] in TEST_FRAMEWORKS:
            self.findings.append((lineno, f"test framework import: {module}"))
        if any(part.casefold() == "testclient" for part in parts):
            self.findings.append((lineno, f"TestClient import: {module}"))
        if any(part == "tests" or part.startswith("test_") for part in parts):
            self.findings.append((lineno, f"test-module import: {module}"))

    def _check_output_name(self, name: str, lineno: int) -> None:
        if _is_expected_output_name(name):
            self.findings.append((lineno, f"expected-output name: {name}"))


def _is_assertion_method(name: str) -> bool:
    return name.startswith("assert_") or (
        name.startswith("assert") and len(name) > len("assert") and name[len("assert")].isupper()
    )


def _is_expected_output_name(name: str) -> bool:
    normalized = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).casefold()
    parts = {part for part in re.split(r"[^a-z0-9]+", normalized) if part}
    return bool(parts & OUTPUT_SOURCE_MARKERS) and bool(parts & OUTPUT_WORDS)


def check_active_workloads(source_root: Path) -> tuple[int, int, int, int, list[str]]:
    recipe_count, workload_paths, test_module_paths, source_scan_paths = _parity_workload_paths(
        source_root
    )
    source_test_bodies = _load_upstream_test_bodies(source_scan_paths, source_root.resolve())
    failures: list[str] = []
    for workload_path in workload_paths:
        relative_path = workload_path.relative_to(ROOT).as_posix()
        try:
            source = workload_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(f"{relative_path}: cannot read workload source: {exc}")
            continue
        try:
            tree = ast.parse(source, filename=relative_path)
        except SyntaxError as exc:
            failures.append(f"{relative_path}:{exc.lineno or 1}: invalid Python syntax: {exc.msg}")
            continue

        visitor = _WorkloadSourceVisitor(source_test_bodies=source_test_bodies)
        visitor.visit(tree)
        failures.extend(f"{relative_path}:{line}: {message}" for line, message in visitor.findings)
    return (
        recipe_count,
        len(workload_paths),
        len(test_module_paths),
        len(source_scan_paths - test_module_paths),
        sorted(failures),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fastapi-source",
        type=Path,
        default=DEFAULT_FASTAPI_SOURCE,
        help="pinned FastAPI source checkout used by upstream-test evidence",
    )
    args = parser.parse_args()
    try:
        (
            recipe_count,
            workload_count,
            test_module_count,
            additional_source_count,
            failures,
        ) = check_active_workloads(args.fastapi_source)
    except (ContractError, OSError, ValueError) as exc:
        print(f"parity workload source check failed: {exc}", file=sys.stderr)
        return 1
    additional_source_label = "source" if additional_source_count == 1 else "sources"

    if failures:
        for failure in failures:
            print(f"parity workload source check failed: {failure}", file=sys.stderr)
        print(
            f"checked {workload_count} workload sources against {test_module_count} "
            f"upstream test modules and {additional_source_count} additional evidence "
            f"{additional_source_label} "
            f"from {recipe_count} recipes; found {len(failures)} issue(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"checked {workload_count} workload sources against {test_module_count} upstream "
        f"test modules and {additional_source_count} additional evidence "
        f"{additional_source_label} from "
        f"{recipe_count} recipes; "
        "no expected-output or copied-test-code patterns found"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
