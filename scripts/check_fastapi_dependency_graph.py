#!/usr/bin/env python3
"""Check the reviewed FastAPI Python dependency table against its pinned lock."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "metadata.yaml"
GRAPH_PATH = ROOT / "docs" / "DEPENDENCY_GRAPH.md"
TABLE_HEADER = (
    "Distribution @ locked version",
    "Surfaces",
    "Incoming edges / direct roots (extra; marker)",
    "Purpose in selected path",
    "Implementation / native parts",
    "License (release/sdist metadata)",
    "FastAPI imports",
)
REQUIRED_FIELDS = {
    "Surfaces": "runtime/extra/group role",
    "Incoming edges / direct roots (extra; marker)": "dependency path/marker",
    "Purpose in selected path": "purpose",
    "Implementation / native parts": "language/native components",
    "License (release/sdist metadata)": "license metadata",
}


class DependencyGraphError(ValueError):
    """Raised when the dependency graph and its pinned lock disagree."""


def load_authority() -> tuple[Path, str]:
    try:
        metadata: Any = yaml.safe_load(METADATA_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise DependencyGraphError(f"cannot read metadata.yaml: {exc}") from exc
    if not isinstance(metadata, dict):
        raise DependencyGraphError("metadata.yaml must contain a mapping")

    authority = metadata.get("authority")
    if not isinstance(authority, dict):
        raise DependencyGraphError("metadata.yaml is missing the authority mapping")
    checkout = authority.get("checkout")
    source_lock = authority.get("upstream_source_lock")
    if not isinstance(checkout, str) or not isinstance(source_lock, dict):
        raise DependencyGraphError("metadata.yaml is missing the FastAPI source-lock identity")
    lock_relative_path = source_lock.get("file")
    expected_digest = source_lock.get("sha256")
    if not isinstance(lock_relative_path, str) or not lock_relative_path:
        raise DependencyGraphError("authority.upstream_source_lock.file must be a path")
    if not isinstance(expected_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        raise DependencyGraphError(
            "authority.upstream_source_lock.sha256 must be a lowercase SHA-256 digest"
        )

    source_root = (ROOT / checkout).resolve()
    lock_path = (source_root / lock_relative_path).resolve()
    try:
        lock_path.relative_to(source_root)
    except ValueError as exc:
        raise DependencyGraphError(
            "FastAPI source lock path must remain inside its checkout"
        ) from exc
    if not lock_path.is_file():
        raise DependencyGraphError(f"pinned FastAPI lock is missing: {lock_path}")

    actual_digest = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    if actual_digest != expected_digest:
        raise DependencyGraphError(
            "pinned FastAPI lock SHA-256 mismatch: "
            f"metadata={expected_digest}, actual={actual_digest}"
        )
    return lock_path, expected_digest


def canonical_name(name: str) -> str:
    """Normalize a Python distribution name according to PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


def split_markdown_row(line: str) -> list[str]:
    """Split a Markdown table row on unescaped pipes."""
    value = line.strip()
    if not value.startswith("|") or not value.endswith("|"):
        raise DependencyGraphError(f"malformed dependency table row: {line!r}")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in value[1:-1]:
        if character == "|" and not escaped:
            cells.append("".join(current).strip())
            current.clear()
        else:
            current.append(character)
        if character == "\\" and not escaped:
            escaped = True
        else:
            escaped = False
    cells.append("".join(current).strip())
    return cells


def read_dependency_rows() -> dict[str, tuple[str, dict[str, str]]]:
    try:
        lines = GRAPH_PATH.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DependencyGraphError(f"cannot read {GRAPH_PATH.relative_to(ROOT)}: {exc}") from exc

    header_text = "| " + " | ".join(TABLE_HEADER) + " |"
    matches = [index for index, line in enumerate(lines) if line.strip() == header_text]
    if len(matches) != 1:
        raise DependencyGraphError(
            f"expected exactly one dependency table with the required columns, found {len(matches)}"
        )
    start = matches[0]
    separator_pattern = r"\|\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*){6}\|"
    if start + 1 >= len(lines) or not re.fullmatch(separator_pattern, lines[start + 1]):
        raise DependencyGraphError("dependency graph table is missing its seven-column separator")

    rows: dict[str, tuple[str, dict[str, str]]] = {}
    for line_number, line in enumerate(lines[start + 2 :], start=start + 3):
        if not line.startswith("|"):
            break
        cells = split_markdown_row(line)
        if len(cells) != len(TABLE_HEADER):
            raise DependencyGraphError(
                f"{GRAPH_PATH.relative_to(ROOT)}:{line_number}: expected 7 cells, "
                f"found {len(cells)}"
            )
        identity = re.fullmatch(r"`([^`]+)` `([^`]+)`", cells[0])
        if identity is None:
            raise DependencyGraphError(
                f"{GRAPH_PATH.relative_to(ROOT)}:{line_number}: expected `name` `version`"
            )
        name, version = identity.groups()
        normalized = canonical_name(name)
        if normalized in rows:
            raise DependencyGraphError(
                f"{GRAPH_PATH.relative_to(ROOT)}:{line_number}: duplicate package row {name!r}"
            )

        fields = dict(zip(TABLE_HEADER[1:], cells[1:], strict=True))
        missing_fields = [
            field_name
            for field_name in REQUIRED_FIELDS
            if not fields[field_name] or fields[field_name] == "—"
        ]
        if missing_fields:
            missing = ", ".join(REQUIRED_FIELDS[field_name] for field_name in missing_fields)
            raise DependencyGraphError(
                f"{GRAPH_PATH.relative_to(ROOT)}:{line_number}: {name} is missing {missing}"
            )
        rows[normalized] = (version, fields)
    return rows


def read_locked_packages(lock_path: Path) -> dict[str, str]:
    try:
        with lock_path.open("rb") as stream:
            lock: Any = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise DependencyGraphError(f"cannot parse pinned FastAPI lock {lock_path}: {exc}") from exc
    package_records = lock.get("package") if isinstance(lock, dict) else None
    if not isinstance(package_records, list):
        raise DependencyGraphError("pinned FastAPI uv.lock is missing its package array")

    packages: dict[str, str] = {}
    for package in package_records:
        if not isinstance(package, dict):
            raise DependencyGraphError("pinned FastAPI uv.lock contains a malformed package record")
        name = package.get("name")
        version = package.get("version")
        if version is None:
            # FastAPI itself is an editable source root without a resolved distribution version.
            if not isinstance(name, str) or canonical_name(name) != "fastapi":
                raise DependencyGraphError(
                    "pinned FastAPI uv.lock contains a versionless package other than its "
                    f"FastAPI editable root: {name!r}"
                )
            source = package.get("source")
            if not isinstance(source, dict) or not isinstance(source.get("editable"), str):
                raise DependencyGraphError(
                    "versionless FastAPI lock root must be an editable source package"
                )
            if canonical_name(name) in packages:
                raise DependencyGraphError("pinned FastAPI uv.lock has duplicate package 'fastapi'")
            continue
        if not isinstance(name, str) or not isinstance(version, str):
            raise DependencyGraphError("pinned FastAPI uv.lock has an invalid versioned package")
        normalized = canonical_name(name)
        if normalized in packages:
            raise DependencyGraphError(f"pinned FastAPI uv.lock has duplicate package {name!r}")
        packages[normalized] = version
    return packages


def check() -> int:
    lock_path, digest = load_authority()
    locked = read_locked_packages(lock_path)
    rows = read_dependency_rows()

    missing = sorted(set(locked) - set(rows))
    extra = sorted(set(rows) - set(locked))
    mismatched = sorted(
        (name, locked[name], rows[name][0])
        for name in set(locked) & set(rows)
        if locked[name] != rows[name][0]
    )
    if missing or extra or mismatched:
        details: list[str] = []
        if missing:
            details.append("missing rows: " + ", ".join(missing))
        if extra:
            details.append("rows absent from lock: " + ", ".join(extra))
        if mismatched:
            versions = ", ".join(
                f"{name} lock={expected} docs={actual}" for name, expected, actual in mismatched
            )
            details.append("version mismatches: " + versions)
        raise DependencyGraphError("dependency graph drift: " + "; ".join(details))

    print(
        "FastAPI dependency graph check passed: "
        f"{len(locked)} locked distributions match exactly; "
        f"required role/path/purpose/language/license fields are present; lock sha256={digest}"
    )
    return 0


def main() -> int:
    try:
        return check()
    except DependencyGraphError as exc:
        print(f"FastAPI dependency graph check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
