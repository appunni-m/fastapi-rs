"""Enforce the FastAPI-RS Python pass-through and runtime dependency boundary."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from importlib import metadata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_PACKAGE_ROOT = PROJECT_ROOT / "fastapi-rs-py" / "python"
FORBIDDEN_PYTHON_CONTROL_FLOW = (
    ast.AsyncFor,
    ast.AsyncWith,
    ast.BoolOp,
    ast.DictComp,
    ast.For,
    ast.If,
    ast.IfExp,
    ast.ListComp,
    ast.Match,
    ast.SetComp,
    ast.Try,
    getattr(ast, "TryStar", ast.Try),
    ast.While,
    ast.With,
    ast.comprehension,
    ast.GeneratorExp,
)
PROJECT_DEPENDENCY_SECTION = "project"
PROJECT_OPTIONAL_DEPENDENCY_SECTION = "project.optional-dependencies"


def _toml_array_is_complete(value: str) -> bool:
    quote = None
    escaped = False
    for character in value:
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif character in {"'", '"'}:
            quote = character
        elif character == "]":
            return True
    return False


def _toml_strings(value: str) -> list[str]:
    return [
        match.group(1) if match.group(1) is not None else match.group(2)
        for match in re.finditer(
            r"\"([^\"\\]*(?:\\.[^\"\\]*)*)\"|'([^'\\]*(?:\\.[^'\\]*)*)'", value
        )
    ]


def check_declared_runtime_dependency_boundary() -> None:
    """Reject upstream FastAPI in PEP 621 runtime or optional dependencies."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = None
    array_value = None
    array_label = None
    dependency_requirements = []

    for line_number, line in enumerate(pyproject.splitlines(), start=1):
        section_match = re.fullmatch(r"\s*\[([^]]+)\]\s*", line)
        if section_match:
            section = section_match.group(1)
            array_value = None
            array_label = None
            continue

        if array_value is not None:
            array_value += "\n" + line
            if _toml_array_is_complete(array_value):
                dependency_requirements.extend(
                    (requirement, array_label, line_number)
                    for requirement in _toml_strings(array_value)
                )
                array_value = None
                array_label = None
            continue

        dependency_key = re.match(r"\s*([A-Za-z0-9_-]+)\s*=\s*(\[.*)$", line)
        if not dependency_key:
            continue
        key = dependency_key.group(1)
        is_runtime_dependency_list = (
            section == PROJECT_DEPENDENCY_SECTION and key == "dependencies"
        ) or section == PROJECT_OPTIONAL_DEPENDENCY_SECTION
        if not is_runtime_dependency_list:
            continue

        array_value = dependency_key.group(2)
        array_label = (
            "project.dependencies"
            if section == PROJECT_DEPENDENCY_SECTION
            else f"project.optional-dependencies.{key}"
        )
        if _toml_array_is_complete(array_value):
            dependency_requirements.extend(
                (requirement, array_label, line_number)
                for requirement in _toml_strings(array_value)
            )
            array_value = None
            array_label = None

    forbidden = []
    for requirement, dependency_group, line_number in dependency_requirements:
        match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
        if match and re.sub(r"[-_.]+", "-", match.group(1)).lower() == "fastapi":
            forbidden.append(
                f"pyproject.toml:{line_number}: original FastAPI is declared in "
                f"{dependency_group}: {requirement}"
            )
    if forbidden:
        raise SystemExit("\n".join(forbidden))


def check_python_facade_control_flow() -> None:
    python_files = sorted(PYTHON_PACKAGE_ROOT.rglob("*.py"))
    if not python_files:
        raise SystemExit(f"no Python facade sources found under {PYTHON_PACKAGE_ROOT}")

    violations = []
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, FORBIDDEN_PYTHON_CONTROL_FLOW):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                    f"{type(node).__name__} is forbidden in the Python pass-through layer"
                )
            if isinstance(node, ast.Import) and any(
                alias.name == "fastapi" or alias.name.startswith("fastapi.") for alias in node.names
            ):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                    "the original FastAPI package cannot be imported by the target facade"
                )
            if isinstance(node, ast.ImportFrom) and (
                node.module == "fastapi" or (node.module or "").startswith("fastapi.")
            ):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                    "the original FastAPI package cannot be imported by the target facade"
                )
    if violations:
        raise SystemExit("\n".join(violations))


def main() -> int:
    check_declared_runtime_dependency_boundary()
    check_python_facade_control_flow()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="check source boundaries without checking an installed target environment",
    )
    args = parser.parse_args()
    if args.source_only:
        print(
            "Static target boundary valid: no original FastAPI runtime dependency or import, "
            "and no Python facade branches, loops, or handlers"
        )
        return 0

    try:
        metadata.distribution("fastapi")
    except metadata.PackageNotFoundError:
        pass
    else:
        raise SystemExit(
            "target environment contains the original FastAPI distribution; "
            "FastAPI is source-oracle-only"
        )

    try:
        target = metadata.distribution("fastapi-rs")
    except metadata.PackageNotFoundError as exc:
        raise SystemExit("target environment is missing the fastapi-rs distribution") from exc

    declared = target.requires or []
    original_fastapi_requirement = next(
        (
            requirement
            for requirement in declared
            if (match := re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement))
            and match.group(1).lower().replace("_", "-") == "fastapi"
        ),
        None,
    )
    if original_fastapi_requirement is not None:
        raise SystemExit(
            "fastapi-rs declares the original FastAPI runtime dependency: "
            + original_fastapi_requirement
        )

    print(
        "target runtime boundary valid: fastapi-rs installed; upstream fastapi absent; "
        "Python facade has no branches or loops; runtime metadata has no upstream dependency"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
