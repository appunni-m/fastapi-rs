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
    check_python_facade_control_flow()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="check Python facade control flow without checking an installed target environment",
    )
    args = parser.parse_args()
    if args.source_only:
        print(
            "Python facade static boundary valid: no branches, loops, handlers, "
            "or imports from original FastAPI"
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
        "Python facade has no branches or loops"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
