"""Migrate old direct API signature recipes and validate current workflow versions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECIPE_ROOT = ROOT / "tests/fixtures/input-recipes/parity"
OLD_SCHEMA = re.compile(r"^fastapi-rs/python-api-workflow@([1-4])$")
SCHEMA_LINE = re.compile(r"(?m)^schema: fastapi-rs/python-api-workflow@[1-4]\s*$")
NEW_SCHEMA = "fastapi-rs/python-api-workflow@5"
CURRENT_SCHEMA = re.compile(r"^fastapi-rs/python-api-workflow@([5-8])$")


def _contains_signature(value: Any) -> bool:
    if isinstance(value, dict):
        return value.get("kind") == "python_signature" or any(
            _contains_signature(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_signature(item) for item in value)
    return False


def _active_signature_recipes() -> list[Path]:
    recipes: list[Path] = []
    for path in sorted(RECIPE_ROOT.glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or not _contains_signature(document):
            continue
        schema = document.get("schema")
        if isinstance(schema, str) and CURRENT_SCHEMA.fullmatch(schema):
            continue
        if not isinstance(schema, str) or OLD_SCHEMA.fullmatch(schema) is None:
            relative_path = path.relative_to(ROOT)
            raise ValueError(
                f"unsupported signature workflow schema in {relative_path}: {schema!r}"
            )
        recipes.append(path)
    return recipes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="rewrite active signature recipes to workflow v5",
    )
    args = parser.parse_args()
    recipes = _active_signature_recipes()
    if not args.apply:
        if recipes:
            names = ", ".join(path.relative_to(ROOT).as_posix() for path in recipes)
            print(f"signature recipes require workflow v5 migration: {names}", file=sys.stderr)
            return 1
        print("all active signature recipes use supported workflow v5-v8")
        return 0
    for path in recipes:
        source = path.read_text(encoding="utf-8")
        updated, count = SCHEMA_LINE.subn(f"schema: {NEW_SCHEMA}", source, count=1)
        if count != 1:
            relative_path = path.relative_to(ROOT)
            raise ValueError(f"could not migrate top-level workflow schema in {relative_path}")
        path.write_text(updated, encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
