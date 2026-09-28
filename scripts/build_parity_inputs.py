#!/usr/bin/env python3
"""Materialize ignored JSON workflows from reviewed YAML input recipes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.parity.contract import (
    ROOT,
    WORKFLOW_SCHEMAS,
    ContractError,
    _UniqueKeyLoader,
    read_json,
)

RECIPE_DIR = ROOT / "tests/fixtures/input-recipes/parity"
INPUT_DIR = ROOT / "tests/fixtures/inputs/parity"


def read_recipe(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as stream:
            value = yaml.load(stream, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read parity input recipe {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"parity input recipe must be a YAML object: {path}")
    schema_path = WORKFLOW_SCHEMAS.get(value.get("schema"))
    if schema_path is None:
        raise ContractError(f"unsupported workflow schema in recipe: {path}")
    schema = read_json(schema_path)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ContractError(f"recipe does not match its workflow schema ({path}): {details}")
    return value


def materialize(*, check: bool = False) -> tuple[int, int]:
    recipes = sorted(RECIPE_DIR.glob("*.yaml"))
    if not recipes:
        raise ContractError(f"no parity input recipes found under {RECIPE_DIR}")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected: dict[str, str] = {}
    for recipe in recipes:
        value = read_recipe(recipe)
        output_name = f"{recipe.stem}.json"
        expected[output_name] = json.dumps(value, indent=2, ensure_ascii=False) + "\n"

    stale = sorted(path for path in INPUT_DIR.glob("*.json") if path.name not in expected)
    for path in stale:
        if check:
            raise ContractError(f"stale generated parity input exists: {path.relative_to(ROOT)}")
        path.unlink()

    changed = 0
    for name, content in expected.items():
        output = INPUT_DIR / name
        current = output.read_text(encoding="utf-8") if output.is_file() else None
        if current == content:
            continue
        if check:
            raise ContractError(f"generated parity input is stale: {output.relative_to(ROOT)}")
        output.write_text(content, encoding="utf-8")
        changed += 1
    return len(expected), changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated inputs are current")
    args = parser.parse_args()
    try:
        count, changed = materialize(check=args.check)
    except (ContractError, OSError, ValueError) as exc:
        print(f"parity input materialization failed: {exc}", file=sys.stderr)
        return 1
    action = "checked" if args.check else "materialized"
    print(f"{action} {count} generated parity inputs ({changed} written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
