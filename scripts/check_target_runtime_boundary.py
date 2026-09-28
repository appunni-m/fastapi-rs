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
PROJECT_DEPENDENCY_SECTION = "project"
PROJECT_OPTIONAL_DEPENDENCY_SECTION = "project.optional-dependencies"


def _configured_native_module() -> str:
    """Read the extension module configured for the published wheel."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = None
    for line in pyproject.splitlines():
        section_match = re.fullmatch(r"\s*\[([^]]+)\]\s*", line)
        if section_match:
            section = section_match.group(1)
            continue
        if section != "tool.maturin":
            continue
        module_match = re.fullmatch(
            r'\s*module-name\s*=\s*["\']([A-Za-z_][A-Za-z0-9_.]*)["\']\s*', line
        )
        if module_match:
            return module_match.group(1)
    raise SystemExit("pyproject.toml must configure tool.maturin.module-name")


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


def _is_static_all_assignment(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "__all__"
        and isinstance(node.value, (ast.List, ast.Tuple))
        and all(
            isinstance(item, ast.Constant) and isinstance(item.value, str)
            for item in node.value.elts
        )
    )


def _is_native_extension_import(path: Path, node: ast.stmt, module_name: str) -> bool:
    """Accept an absolute or package-relative import from the configured extension."""
    if not isinstance(node, ast.ImportFrom):
        return False
    if node.level == 0:
        return node.module == module_name
    if node.level != 1 or node.module is None:
        return False

    native_package = module_name.rpartition(".")[0]
    source_package = ".".join(path.relative_to(PYTHON_PACKAGE_ROOT).parent.parts)
    imported_module = f"{source_package}.{node.module}"
    return imported_module == module_name and source_package == native_package


def check_python_facade_pass_through() -> None:
    """Allow only native-extension re-exports and a matching literal ``__all__``."""
    python_files = sorted(PYTHON_PACKAGE_ROOT.rglob("*.py"))
    if not python_files:
        raise SystemExit(f"no Python facade sources found under {PYTHON_PACKAGE_ROOT}")

    native_module = _configured_native_module()
    violations = []
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_names = []
        all_assignments = []
        for index, node in enumerate(tree.body):
            is_docstring = (
                index == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
            if is_docstring:
                continue
            if _is_static_all_assignment(node):
                all_assignments.append(node)
                continue
            if isinstance(node, ast.ImportFrom):
                if not _is_native_extension_import(path, node, native_module):
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: imports must be "
                        f"direct re-exports from the configured native module {native_module!r}"
                    )
                    continue
                if any(alias.name == "*" for alias in node.names):
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: wildcard native "
                        "re-exports are not allowed"
                    )
                    continue
                imported_names.extend(alias.asname or alias.name for alias in node.names)
                continue
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                f"{type(node).__name__} is not a native re-export; Python runtime modules "
                "may contain only native imports and a literal __all__"
            )

        if len(all_assignments) != 1:
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}: Python runtime modules must define "
                "exactly one literal __all__"
            )
        elif all_assignments[0].value.elts:
            exported_names = [item.value for item in all_assignments[0].value.elts]
            if len(exported_names) != len(set(exported_names)):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{all_assignments[0].lineno}: "
                    "__all__ contains duplicate names"
                )
            if imported_names != exported_names:
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{all_assignments[0].lineno}: "
                    f"__all__ must exactly match native re-exports; imports={imported_names!r}, "
                    f"__all__={exported_names!r}"
                )
        elif imported_names:
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}: native imports must be listed in "
                "literal __all__"
            )

        for node in ast.walk(tree):
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
    check_python_facade_pass_through()
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
            "and Python runtime modules re-export only configured native symbols via "
            "literal __all__"
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
        "Python facade contains only configured native re-exports; runtime metadata has no "
        "upstream dependency"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
