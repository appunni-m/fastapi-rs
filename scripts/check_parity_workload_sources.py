#!/usr/bin/env python3
"""Statically screen active parity workload sources for obvious test code."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_parity_inputs import RECIPE_DIR, read_recipe
from scripts.parity.contract import ROOT, ContractError

WORKLOAD_ROOT = (ROOT / "tests/fixtures/workloads").resolve()
TEST_FRAMEWORKS = frozenset({"pytest", "unittest"})


class _WorkloadSourceVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.function_stack: list[str] = []
        self.findings: list[tuple[int, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_Assert(self, node: ast.Assert) -> None:
        if not self.function_stack or any(name.startswith("test_") for name in self.function_stack):
            self.findings.append(
                (
                    node.lineno,
                    "assert statement in module scope or a test-named function",
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
        self.generic_visit(node)

    def _check_import(self, module: str, lineno: int) -> None:
        parts = module.split(".")
        if parts[0] in TEST_FRAMEWORKS:
            self.findings.append((lineno, f"test framework import: {module}"))
        if any(part == "tests" or part.startswith("test_") for part in parts):
            self.findings.append((lineno, f"test-module import: {module}"))


def _active_workload_paths() -> tuple[int, list[Path]]:
    recipes = sorted(RECIPE_DIR.glob("*.yaml"))
    if not recipes:
        raise ContractError(f"no active parity recipes found under {RECIPE_DIR}")

    paths: set[Path] = set()
    for recipe_path in recipes:
        recipe = read_recipe(recipe_path)
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
        paths.add(workload_path)
    return len(recipes), sorted(paths)


def check_active_workloads() -> tuple[int, int, list[str]]:
    recipe_count, workload_paths = _active_workload_paths()
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

        visitor = _WorkloadSourceVisitor()
        visitor.visit(tree)
        failures.extend(f"{relative_path}:{line}: {message}" for line, message in visitor.findings)
    return recipe_count, len(workload_paths), sorted(failures)


def main() -> int:
    try:
        recipe_count, workload_count, failures = check_active_workloads()
    except (ContractError, OSError, ValueError) as exc:
        print(f"parity workload source check failed: {exc}", file=sys.stderr)
        return 1

    if failures:
        for failure in failures:
            print(f"parity workload source check failed: {failure}", file=sys.stderr)
        print(
            f"checked {workload_count} active workload sources from "
            f"{recipe_count} recipes; found {len(failures)} issue(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"checked {workload_count} active workload sources from "
        f"{recipe_count} parity recipes; no obvious test-code patterns found"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
