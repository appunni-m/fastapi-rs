#!/usr/bin/env python3
"""Derive and check FastAPI's locked Python dependency graph."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
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
    "Purpose in selected path": "purpose",
    "Implementation / native parts": "language/native components",
    "License (release/sdist metadata)": "license metadata",
    "FastAPI imports": "source-import evidence",
}
ROW_SEPARATOR = r"\|\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*){6}\|"
SURFACE_SUMMARY = re.compile(r"^- `([^`]+)`: ([0-9]+) locked distributions reachable\.$")


class DependencyGraphError(ValueError):
    """Raised when the dependency graph and its pinned lock disagree."""


@dataclass(frozen=True)
class DependencyRow:
    """One reviewed table row and its source line."""

    line_number: int
    name: str
    version: str
    cells: tuple[str, ...]


@dataclass(frozen=True)
class DerivedGraph:
    """Lock-derived reachability and incoming edges across project profiles."""

    versions: dict[str, str]
    surfaces: dict[str, set[str]]
    incoming_edges: dict[str, set[str]]
    surface_counts: dict[str, int]


def _read_metadata() -> dict[str, Any]:
    try:
        metadata: Any = yaml.safe_load(METADATA_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise DependencyGraphError(f"cannot read metadata.yaml: {exc}") from exc
    if not isinstance(metadata, dict):
        raise DependencyGraphError("metadata.yaml must contain a mapping")
    return metadata


def _git_bytes(source_root: Path, *arguments: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source_root), *arguments], stderr=subprocess.PIPE
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = (
            exc.stderr.decode("utf-8", errors="replace").strip()
            if isinstance(exc, subprocess.CalledProcessError)
            else str(exc)
        )
        raise DependencyGraphError(f"cannot inspect pinned FastAPI source: {detail}") from exc


def load_authority() -> tuple[Path, Path, str]:
    metadata = _read_metadata()
    authority = metadata.get("authority")
    if not isinstance(authority, dict):
        raise DependencyGraphError("metadata.yaml is missing the authority mapping")
    checkout = authority.get("checkout")
    source_commit = authority.get("commit")
    source_lock = authority.get("upstream_source_lock")
    if (
        not isinstance(checkout, str)
        or not isinstance(source_commit, str)
        or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None
        or not isinstance(source_lock, dict)
    ):
        raise DependencyGraphError("metadata.yaml is missing the pinned FastAPI source identity")

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
    project_path = source_root / "pyproject.toml"
    for path in (lock_path, project_path):
        try:
            path.relative_to(source_root)
        except ValueError as exc:
            raise DependencyGraphError(
                "FastAPI source paths must remain inside its checkout"
            ) from exc
        if not path.is_file():
            raise DependencyGraphError(f"pinned FastAPI source file is missing: {path}")

    actual_commit = _git_bytes(source_root, "rev-parse", "HEAD").decode().strip()
    if actual_commit != source_commit:
        raise DependencyGraphError(
            f"FastAPI checkout commit mismatch: metadata={source_commit}, actual={actual_commit}"
        )
    for relative in (lock_relative_path, "pyproject.toml"):
        pinned = _git_bytes(source_root, "show", f"{source_commit}:{relative}")
        local = (source_root / relative).read_bytes()
        if local != pinned:
            raise DependencyGraphError(
                f"FastAPI source file differs from pinned commit {source_commit}: {relative}"
            )

    actual_digest = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    if actual_digest != expected_digest:
        raise DependencyGraphError(
            "pinned FastAPI lock SHA-256 mismatch: "
            f"metadata={expected_digest}, actual={actual_digest}"
        )
    return lock_path, project_path, expected_digest


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


def read_dependency_rows() -> tuple[dict[str, DependencyRow], list[str]]:
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
    if start + 1 >= len(lines) or not re.fullmatch(ROW_SEPARATOR, lines[start + 1]):
        raise DependencyGraphError("dependency graph table is missing its seven-column separator")

    rows: dict[str, DependencyRow] = {}
    for line_index in range(start + 2, len(lines)):
        line = lines[line_index]
        if not line.startswith("|"):
            break
        cells = split_markdown_row(line)
        line_number = line_index + 1
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
        rows[normalized] = DependencyRow(line_number, name, version, tuple(cells))
    return rows, lines


def _records(value: Any, owner: str, key: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise DependencyGraphError(f"{owner}.{key} must be a dependency list")
    records: list[dict[str, Any]] = []
    for index, record in enumerate(value):
        if not isinstance(record, dict) or not isinstance(record.get("name"), str):
            raise DependencyGraphError(f"{owner}.{key}[{index}] is malformed")
        extras = record.get("extra", [])
        marker = record.get("marker")
        if not isinstance(extras, list) or any(not isinstance(item, str) for item in extras):
            raise DependencyGraphError(f"{owner}.{key}[{index}].extra must be a string list")
        if marker is not None and (not isinstance(marker, str) or not marker):
            raise DependencyGraphError(f"{owner}.{key}[{index}].marker must be a nonempty string")
        records.append(record)
    return records


def _source_groups(project: dict[str, Any], root: dict[str, Any]) -> dict[str, list[str]]:
    project_table = project.get("project")
    extras = project_table.get("optional-dependencies") if isinstance(project_table, dict) else None
    lock_extras = root.get("optional-dependencies", {})
    if not isinstance(extras, dict) or not isinstance(lock_extras, dict):
        raise DependencyGraphError(
            "FastAPI project extras are missing from pyproject.toml or uv.lock"
        )
    if set(extras) != set(lock_extras):
        raise DependencyGraphError("FastAPI pyproject extras differ from uv.lock extras")

    groups = project.get("dependency-groups")
    lock_groups = root.get("dev-dependencies", {})
    if not isinstance(groups, dict) or not isinstance(lock_groups, dict):
        raise DependencyGraphError(
            "FastAPI dependency groups are missing from pyproject.toml or uv.lock"
        )
    if set(groups) != set(lock_groups):
        raise DependencyGraphError("FastAPI pyproject dependency groups differ from uv.lock groups")

    def expand(group: str, visiting: tuple[str, ...] = ()) -> list[str]:
        if group not in groups:
            raise DependencyGraphError(f"FastAPI dependency group includes unknown group {group!r}")
        if group in visiting:
            cycle = " -> ".join((*visiting, group))
            raise DependencyGraphError(
                f"FastAPI dependency groups contain an include cycle: {cycle}"
            )
        included = [group]
        entries = groups[group]
        if not isinstance(entries, list):
            raise DependencyGraphError(f"FastAPI dependency group {group!r} must be a list")
        for entry in entries:
            if isinstance(entry, dict) and "include-group" in entry:
                child = entry.get("include-group")
                if not isinstance(child, str):
                    raise DependencyGraphError(
                        f"FastAPI dependency group {group!r} has a malformed include-group"
                    )
                included.extend(expand(child, (*visiting, group)))
        return list(dict.fromkeys(included))

    return {group: expand(group) for group in groups}


def _target_label(record: dict[str, Any]) -> str:
    name = canonical_name(record["name"])
    extras = sorted(set(record.get("extra", [])))
    if extras:
        name += " [extra=" + ",".join(extras) + "]"
    marker = record.get("marker")
    if marker:
        name += " [marker=" + marker + "]"
    return name.replace("|", r"\|")


def _edge(parent: str, context: tuple[str, ...], record: dict[str, Any]) -> str:
    label = parent
    if context:
        label += "[" + ",".join(context) + "]"
    return f"{label} -> {_target_label(record)}"


def _add_context(
    name: str,
    extras: tuple[str, ...],
    packages: dict[str, dict[str, Any]],
    contexts: dict[str, set[tuple[str, ...]]],
    active_extras: dict[str, set[str]],
    reached: set[str],
    queue: deque[str],
) -> None:
    if name not in packages:
        raise DependencyGraphError(f"uv.lock edge points to missing package {name!r}")
    if extras not in contexts[name]:
        contexts[name].add(extras)
        active_extras[name].update(extras)
        reached.add(name)
        queue.append(name)


def derive_graph(lock_path: Path, project_path: Path) -> DerivedGraph:
    try:
        lock: Any = tomllib.loads(lock_path.read_text(encoding="utf-8"))
        project: Any = tomllib.loads(project_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise DependencyGraphError(f"cannot parse FastAPI lock or pyproject.toml: {exc}") from exc
    package_records = lock.get("package") if isinstance(lock, dict) else None
    if not isinstance(package_records, list):
        raise DependencyGraphError("pinned FastAPI uv.lock is missing its package array")

    packages: dict[str, dict[str, Any]] = {}
    versions: dict[str, str] = {}
    root: dict[str, Any] | None = None
    for package in package_records:
        if not isinstance(package, dict) or not isinstance(package.get("name"), str):
            raise DependencyGraphError("pinned FastAPI uv.lock contains a malformed package record")
        name = canonical_name(package["name"])
        version = package.get("version")
        if version is None:
            source = package.get("source")
            if (
                name != "fastapi"
                or not isinstance(source, dict)
                or not isinstance(source.get("editable"), str)
            ):
                raise DependencyGraphError(
                    "versionless FastAPI lock root must be its editable source package"
                )
            if root is not None:
                raise DependencyGraphError("pinned FastAPI uv.lock has duplicate editable roots")
            root = package
            continue
        if not isinstance(version, str) or name in packages:
            raise DependencyGraphError(
                f"pinned FastAPI uv.lock has an invalid or duplicate {name!r}"
            )
        packages[name] = package
        versions[name] = version
    if root is None:
        raise DependencyGraphError("pinned FastAPI uv.lock is missing its editable FastAPI root")

    group_members = _source_groups(project, root)
    profiles: dict[str, list[tuple[str, list[dict[str, Any]]]]] = {
        "runtime": [
            ("fastapi (root)", _records(root.get("dependencies"), "fastapi", "dependencies"))
        ]
    }
    for extra, records in root.get("optional-dependencies", {}).items():
        profiles[f"extra:{extra}"] = [
            (
                f"fastapi[{extra}] (base root)",
                _records(root.get("dependencies"), "fastapi", "dependencies"),
            ),
            (f"fastapi[{extra}] (root)", _records(records, "fastapi", f"extra {extra}")),
        ]
    lock_groups = root.get("dev-dependencies", {})
    for group, members in group_members.items():
        root_refs: list[dict[str, Any]] = []
        for member in members:
            root_refs.extend(
                _records(lock_groups[member], f"fastapi group {member}", "dependencies")
            )
        profiles[f"group:{group}"] = [(f"group:{group} (root)", root_refs)]

    surfaces: dict[str, set[str]] = defaultdict(set)
    incoming_edges: dict[str, set[str]] = defaultdict(set)
    for surface, root_groups in profiles.items():
        reached: set[str] = set()
        contexts: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        active_extras: dict[str, set[str]] = defaultdict(set)
        queue: deque[str] = deque()
        root_edges: dict[str, set[str]] = defaultdict(set)
        processed_base: set[str] = set()
        processed_extras: dict[str, set[str]] = defaultdict(set)

        for root_label, requirements in root_groups:
            for requirement in requirements:
                name = canonical_name(requirement["name"])
                extras = tuple(sorted(set(requirement.get("extra", []))))
                _add_context(name, extras, packages, contexts, active_extras, reached, queue)
                root_edges[name].add(f"{root_label} -> {_target_label(requirement)}")

        while queue:
            parent = queue.popleft()
            package = packages[parent]
            if parent not in processed_base:
                processed_base.add(parent)
                for requirement in _records(
                    package.get("dependencies", []), parent, "dependencies"
                ):
                    name = canonical_name(requirement["name"])
                    extras = tuple(sorted(set(requirement.get("extra", []))))
                    _add_context(name, extras, packages, contexts, active_extras, reached, queue)
            for extra in sorted(active_extras[parent] - processed_extras[parent]):
                processed_extras[parent].add(extra)
                optional = package.get("optional-dependencies", {}).get(extra, [])
                for requirement in _records(optional, parent, f"extra {extra}"):
                    name = canonical_name(requirement["name"])
                    extras = tuple(sorted(set(requirement.get("extra", []))))
                    _add_context(name, extras, packages, contexts, active_extras, reached, queue)

        for child, edges in root_edges.items():
            incoming_edges[child].update(edges)
        for parent in reached:
            package = packages[parent]
            for requirement in _records(package.get("dependencies", []), parent, "dependencies"):
                child = canonical_name(requirement["name"])
                for context in contexts[parent]:
                    incoming_edges[child].add(_edge(parent, context, requirement))
            optional_dependencies = package.get("optional-dependencies", {})
            for extra in active_extras[parent]:
                for requirement in _records(
                    optional_dependencies.get(extra, []), parent, f"extra {extra}"
                ):
                    child = canonical_name(requirement["name"])
                    incoming_edges[child].add(_edge(parent, (extra,), requirement))
        for name in reached:
            surfaces[name].add(surface)

    unreachable = sorted(set(packages) - set(surfaces))
    unknown = sorted(set(surfaces) - set(packages))
    if unreachable or unknown:
        details = []
        if unreachable:
            details.append(
                "locked packages unreachable from all declared profiles: " + ", ".join(unreachable)
            )
        if unknown:
            details.append("profiles reach packages absent from the lock: " + ", ".join(unknown))
        raise DependencyGraphError("dependency graph closure failed: " + "; ".join(details))

    counts = {
        profile: sum(profile in package_surfaces for package_surfaces in surfaces.values())
        for profile in profiles
    }
    return DerivedGraph(versions, dict(surfaces), dict(incoming_edges), counts)


def _read_surface_summary(lines: list[str]) -> tuple[dict[str, int], int, int]:
    heading = [index for index, line in enumerate(lines) if line.strip() == "## Graph summary"]
    if len(heading) != 1:
        raise DependencyGraphError("dependency graph must have exactly one 'Graph summary' section")
    start = heading[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    summary: dict[str, int] = {}
    matching_lines: list[int] = []
    for index in range(start, end):
        match = SURFACE_SUMMARY.fullmatch(lines[index])
        if match is None:
            if matching_lines and lines[index].strip():
                break
            continue
        surface, count = match.groups()
        if surface in summary:
            raise DependencyGraphError(f"duplicate reachability summary for {surface!r}")
        summary[surface] = int(count)
        matching_lines.append(index)
    if not matching_lines:
        raise DependencyGraphError("dependency graph has no lock-derived reachability summary")
    return summary, matching_lines[0], matching_lines[-1]


def _render_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def update_document(rows: dict[str, DependencyRow], lines: list[str], graph: DerivedGraph) -> None:
    for name, row in rows.items():
        cells = list(row.cells)
        cells[1] = ", ".join(sorted(graph.surfaces[name]))
        cells[2] = "; ".join(sorted(graph.incoming_edges[name]))
        lines[row.line_number - 1] = _render_row(cells)

    _, first_summary_line, last_summary_line = _read_surface_summary(lines)
    rendered_summary = [
        f"- `{surface}`: {count} locked distributions reachable."
        for surface, count in sorted(graph.surface_counts.items())
    ]
    lines[first_summary_line : last_summary_line + 1] = rendered_summary
    GRAPH_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _check_row_sets(locked: dict[str, str], rows: dict[str, DependencyRow]) -> list[str]:
    missing = sorted(set(locked) - set(rows))
    extra = sorted(set(rows) - set(locked))
    mismatched = sorted(
        (name, locked[name], rows[name].version)
        for name in set(locked) & set(rows)
        if locked[name] != rows[name].version
    )
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
    return details


def check(*, update: bool = False) -> int:
    lock_path, project_path, digest = load_authority()
    graph = derive_graph(lock_path, project_path)
    rows, lines = read_dependency_rows()
    row_drift = _check_row_sets(graph.versions, rows)
    if row_drift:
        raise DependencyGraphError("dependency graph drift: " + "; ".join(row_drift))

    if update:
        update_document(rows, lines, graph)
        rows, lines = read_dependency_rows()

    for name, row in rows.items():
        expected_surfaces = ", ".join(sorted(graph.surfaces[name]))
        expected_edges = "; ".join(sorted(graph.incoming_edges[name]))
        if row.cells[1] != expected_surfaces:
            raise DependencyGraphError(
                f"{GRAPH_PATH.relative_to(ROOT)}:{row.line_number}: {name} surface drift; "
                f"expected {expected_surfaces!r}, found {row.cells[1]!r}"
            )
        if row.cells[2] != expected_edges:
            raise DependencyGraphError(
                f"{GRAPH_PATH.relative_to(ROOT)}:{row.line_number}: {name} edge drift; "
                f"expected {expected_edges!r}, found {row.cells[2]!r}"
            )

    summary, _, _ = _read_surface_summary(lines)
    if summary != graph.surface_counts:
        raise DependencyGraphError(
            "dependency graph reachability summary drift: "
            f"expected {graph.surface_counts!r}, found {summary!r}"
        )

    print(
        "FastAPI dependency graph check passed: "
        f"{len(graph.versions)} locked distributions and {len(graph.surface_counts)} "
        f"profiles match lock-derived edges, extras, groups, markers, and reachability; "
        f"reviewed purpose/language/license/import annotations are present; lock sha256={digest}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update",
        action="store_true",
        help="rewrite lock-derived surface, edge, and reachability fields before checking",
    )
    args = parser.parse_args()
    try:
        return check(update=args.update)
    except (DependencyGraphError, OSError) as exc:
        print(f"FastAPI dependency graph check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
