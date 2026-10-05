#!/usr/bin/env python3
"""Render the pinned Pydantic Core Rust dependency and license inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Any

import tomllib
import yaml
from render_rust_target_dependency_inventory import (
    dependency_kinds,
    optional_dependency,
    package_roles,
    target_description,
)

ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "metadata.yaml"
TARGET_PROJECT_PATH = ROOT / "pyproject.toml"


class InventoryError(ValueError):
    """Raised when the pinned Pydantic Core source and inventory disagree."""


def read_metadata() -> dict[str, Any]:
    try:
        metadata: Any = yaml.safe_load(METADATA_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise InventoryError(f"cannot read {METADATA_PATH}: {exc}") from exc
    if not isinstance(metadata, dict):
        raise InventoryError("metadata.yaml must contain a mapping")
    return metadata


def git_text(source_root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source_root), *args], stderr=subprocess.PIPE, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise InventoryError(f"cannot inspect pinned Pydantic source: {detail}") from exc


def canonical_repository(value: str) -> str:
    value = value.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    elif value.startswith("ssh://git@github.com/"):
        value = "https://github.com/" + value.removeprefix("ssh://git@github.com/")
    elif "//" not in value and value.count("/") == 1:
        value = "https://github.com/" + value
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/")


def read_pins(metadata: dict[str, Any]) -> tuple[dict[str, Any], Path, Path, str]:
    authority = metadata.get("authority")
    source = authority.get("pydantic_core_source")
    inventory = metadata.get("pydantic_core_dependency_inventory")
    if not isinstance(authority, dict) or not isinstance(source, dict):
        raise InventoryError("metadata.yaml is missing the Pydantic Core source identity")
    if not isinstance(inventory, dict):
        raise InventoryError("metadata.yaml is missing the Pydantic Core inventory policy")
    if inventory.get("schema") != "fastapi-rs/pydantic-core-cargo-inventory@1":
        raise InventoryError("metadata.yaml declares an unsupported Pydantic Core inventory schema")
    if inventory.get("generator") != Path(__file__).relative_to(ROOT).as_posix():
        raise InventoryError("metadata.yaml Pydantic Core inventory generator path is stale")
    if inventory.get("artifact") != "docs/PYDANTIC_CORE_DEPENDENCIES.md":
        raise InventoryError("metadata.yaml Pydantic Core inventory artifact path is stale")

    pydantic = authority.get("pydantic")
    if not isinstance(pydantic, dict):
        raise InventoryError("metadata.yaml is missing the selected Pydantic versions")
    expected_version = pydantic.get("pydantic_core_version")
    if source.get("version") != expected_version:
        raise InventoryError(
            "Pydantic Core source version differs from the selected package identity: "
            f"source={source.get('version')!r}, selected={expected_version!r}"
        )

    checkout = source.get("checkout")
    manifest = source.get("cargo_manifest")
    lockfile = source.get("cargo_lock")
    if not all(isinstance(value, str) and value for value in (checkout, manifest, lockfile)):
        raise InventoryError("Pydantic Core source paths must be nonempty strings")
    return source, (ROOT / checkout).resolve(), Path(manifest), str(expected_version)


def validate_source(source: dict[str, Any], source_root: Path, manifest_relative: Path) -> Path:
    if not source_root.is_dir():
        raise InventoryError(f"pinned Pydantic source checkout does not exist: {source_root}")
    expected_repository = source.get("repository")
    expected_commit = source.get("commit")
    tag = source.get("tag")
    if not all(
        isinstance(value, str) and value for value in (expected_repository, expected_commit, tag)
    ):
        raise InventoryError("Pydantic source identity requires repository, tag, and commit")

    actual_repository = canonical_repository(git_text(source_root, "remote", "get-url", "origin"))
    if actual_repository != canonical_repository(expected_repository):
        raise InventoryError(
            "Pydantic source repository mismatch: "
            f"metadata={expected_repository}, actual={actual_repository}"
        )
    actual_commit = git_text(source_root, "rev-parse", "HEAD")
    if actual_commit != expected_commit:
        raise InventoryError(
            f"Pydantic source commit mismatch: metadata={expected_commit}, actual={actual_commit}"
        )
    tagged_commit = git_text(source_root, "rev-parse", f"refs/tags/{tag}^{{}}")
    if tagged_commit != expected_commit:
        raise InventoryError(
            f"Pydantic tag {tag} no longer resolves to its reviewed commit {expected_commit}"
        )

    manifest_path = (source_root / manifest_relative).resolve()
    lock_relative = Path(str(source.get("cargo_lock", "")))
    lock_path = (source_root / lock_relative).resolve()
    for path in (manifest_path, lock_path):
        try:
            path.relative_to(source_root)
        except ValueError as exc:
            raise InventoryError("Pydantic source paths must remain inside the checkout") from exc
        if not path.is_file():
            raise InventoryError(f"pinned Pydantic source file is missing: {path}")

    for path, relative, digest_key in (
        (manifest_path, manifest_relative, "cargo_manifest_sha256"),
        (lock_path, lock_relative, "cargo_lock_sha256"),
    ):
        pinned = subprocess.run(
            ["git", "-C", str(source_root), "show", f"{expected_commit}:{relative.as_posix()}"],
            capture_output=True,
            check=False,
        )
        if pinned.returncode:
            raise InventoryError(f"pinned Pydantic source omits {relative.as_posix()}")
        local_bytes = path.read_bytes()
        if local_bytes != pinned.stdout:
            raise InventoryError(
                f"Pydantic source file differs from pinned commit {expected_commit}: {relative}"
            )
        actual_digest = hashlib.sha256(local_bytes).hexdigest()
        expected_digest = source.get(digest_key)
        if actual_digest != expected_digest:
            raise InventoryError(
                f"{relative.as_posix()} SHA-256 mismatch: "
                f"metadata={expected_digest}, actual={actual_digest}"
            )

    return manifest_path


def validate_package_identity(
    manifest_path: Path, expected_version: str, target_project_path: Path
) -> None:
    try:
        cargo_manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        target_project = tomllib.loads(target_project_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise InventoryError(f"cannot read a pinned package manifest: {exc}") from exc
    package = cargo_manifest.get("package", {})
    if package.get("name") != "pydantic-core" or package.get("version") != expected_version:
        raise InventoryError(
            "Pydantic Core Cargo identity mismatch: "
            f"expected=pydantic-core {expected_version}, "
            f"found={package.get('name')} {package.get('version')}"
        )
    if package.get("rust-version") != "1.88":
        raise InventoryError(
            "Pydantic Core Rust version changed; review target toolchain boundary: "
            f"found {package.get('rust-version')!r}"
        )

    requirements = target_project.get("project", {}).get("dependencies", [])
    target_core = [
        requirement
        for requirement in requirements
        if isinstance(requirement, str)
        and re.match(r"^pydantic[-_]core\s*==", requirement, flags=re.IGNORECASE)
    ]
    if target_core != [f"pydantic-core=={expected_version}"]:
        raise InventoryError(
            "target pyproject.toml must keep the separately installed Pydantic Core pin: "
            f"found={target_core!r}"
        )


def cargo_metadata(manifest_path: Path, *, offline: bool) -> dict[str, Any]:
    command = [
        "cargo",
        "metadata",
        "--manifest-path",
        str(manifest_path),
        "--locked",
        "--format-version",
        "1",
    ]
    if offline:
        command.append("--offline")
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode:
        raise InventoryError(result.stderr.strip() or "cargo metadata failed")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise InventoryError("cargo metadata returned invalid JSON") from exc


def package_label(package: dict[str, Any]) -> str:
    return f"{package['name']} {package['version']}"


def canonical_crate_name(value: str) -> str:
    return value.replace("-", "_").lower()


def edge_declarations(
    parent: dict[str, Any], dependency: dict[str, Any], target: dict[str, Any]
) -> list[dict[str, Any]]:
    """Find every manifest declaration represented by a resolved Cargo edge."""
    edge_name = canonical_crate_name(dependency["name"])
    target_name = canonical_crate_name(target["name"])
    active_kinds = {
        (dep_kind.get("kind") or "normal", dep_kind.get("target"))
        for dep_kind in dependency.get("dep_kinds", [])
    }
    declarations = []
    for declared in parent.get("dependencies", []):
        declared_target = canonical_crate_name(declared.get("package") or declared["name"])
        declared_edge = canonical_crate_name(declared.get("rename") or declared["name"])
        declared_kind = declared.get("kind") or "normal"
        if declared_target != target_name or declared_edge != edge_name:
            continue
        if (declared_kind, declared.get("target")) not in active_kinds:
            continue
        declarations.append(declared)
    return declarations


def resolved_edge_labels(
    parent: dict[str, Any], dependency: dict[str, Any], target: dict[str, Any]
) -> str:
    declarations = edge_declarations(parent, dependency, target)
    kinds = []
    active_kinds = sorted(
        {
            (dep_kind.get("kind") or "normal", dep_kind.get("target"))
            for dep_kind in dependency.get("dep_kinds", [])
        }
    )
    for kind, predicate in active_kinds:
        label = kind
        if predicate:
            label += f" if {predicate}"
        kinds.append(label)
    labels = list(kinds)
    for declared in declarations:
        context = declared.get("kind") or "normal"
        if declared.get("target"):
            context += f" if {declared['target']}"
        details = []
        if declared.get("optional"):
            details.append("optional")
        requested = declared.get("features", [])
        if requested:
            details.append("requests features " + ", ".join(sorted(requested)))
        if not declared.get("uses_default_features", True):
            details.append("default features disabled")
        if details:
            labels.append(f"{context}: " + ", ".join(details))
    return "; ".join(labels) or "normal"


def dependency_paths(
    metadata: dict[str, Any],
) -> dict[str, dict[tuple[str, bool], tuple[str, ...]]]:
    """Find one shortest root path for every package role/optional path."""
    packages = {package["id"]: package for package in metadata["packages"]}
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    roots = metadata.get("workspace_members", [])
    if len(roots) != 1:
        raise InventoryError(f"expected one Pydantic Core Cargo root, found {len(roots)}")

    paths: dict[str, dict[tuple[str, bool], tuple[str, ...]]] = {}
    queue: deque[tuple[str, str, bool, tuple[str, ...]]] = deque(
        [(roots[0], "runtime", False, (package_label(packages[roots[0]]),))]
    )
    visited: set[tuple[str, str, bool]] = set()
    while queue:
        parent_id, role, optional, path = queue.popleft()
        state = (parent_id, role, optional)
        if state in visited:
            continue
        visited.add(state)
        paths.setdefault(parent_id, {})[(role, optional)] = path
        parent = packages[parent_id]
        node = nodes.get(parent_id)
        if node is None:
            continue
        for dependency in sorted(node["deps"], key=lambda item: item["name"]):
            child_id = dependency["pkg"]
            child = packages[child_id]
            optional_edge = optional or bool(optional_dependency(parent, dependency, child))
            for kind in sorted(dependency_kinds(dependency)):
                if kind == "build":
                    child_role = "build"
                elif kind == "dev":
                    child_role = "dev"
                else:
                    child_role = role
                queue.append((child_id, child_role, optional_edge, (*path, package_label(child))))
    return paths


def markdown_cell(value: object) -> str:
    return " ".join(str(value or "—").split()).replace("|", "\\|")


def package_license(package: dict[str, Any]) -> str:
    license_value = package.get("license")
    if license_value:
        return str(license_value)
    if package.get("license_file"):
        return f"file: {package['license_file']}"
    return "UNSPECIFIED"


def package_source(package: dict[str, Any], root_id: str) -> str:
    if package["id"] == root_id:
        return "Pinned Pydantic source"
    source = package.get("source")
    if source == "registry+https://github.com/rust-lang/crates.io-index":
        return "crates.io"
    return str(source or "UNSPECIFIED")


def package_native_boundary(package: dict[str, Any], root_id: str) -> str:
    signals = []
    kinds = {kind for target in package.get("targets", []) for kind in target.get("kind", [])}
    if package["id"] == root_id:
        signals.append("Python extension built as Rust cdylib via PyO3")
    elif package["name"] == "pyo3":
        signals.append("Rust bindings to the Python C API")
    elif package["name"] == "pyo3-ffi":
        signals.append("Python C-API FFI bindings")
    links = package.get("links")
    if links:
        signals.append(f"Cargo links = {links}")
    if "proc-macro" in kinds:
        signals.append("Rust procedural macro")
    if not signals:
        return "No Cargo links declaration"
    return "; ".join(signals)


def render_inventory(metadata: dict[str, Any], source: dict[str, Any], version: str) -> str:
    packages = {package["id"]: package for package in metadata["packages"]}
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    roots = metadata.get("workspace_members", [])
    if len(roots) != 1:
        raise InventoryError(f"expected one Pydantic Core Cargo root, found {len(roots)}")
    root_id = roots[0]
    root = packages[root_id]
    if root["name"] != "pydantic-core" or root["version"] != version:
        raise InventoryError(
            f"Cargo root identity mismatch: expected pydantic-core {version}, found {root_id}"
        )

    all_lock_packages = {package_id for package_id in nodes}
    locked_count = sum(
        1
        for line in (Path(root["manifest_path"]).parent / "Cargo.lock").read_text().splitlines()
        if line == "[[package]]"
    )
    if len(all_lock_packages) != locked_count:
        raise InventoryError(
            "Cargo metadata resolution and Cargo.lock package counts differ: "
            f"resolved={len(all_lock_packages)}, locked={locked_count}"
        )

    roles = package_roles(metadata)
    paths = dependency_paths(metadata)
    role_order = ("runtime", "optional runtime", "build", "optional build", "dev", "optional dev")
    role_counts: dict[str, int] = {role: 0 for role in role_order}
    for package_id in nodes:
        for role in roles.get(package_id, set()):
            if role in role_counts:
                role_counts[role] += 1

    rows: list[str] = []
    for package_id in sorted(
        nodes, key=lambda item: (packages[item]["name"], packages[item]["version"])
    ):
        package = packages[package_id]
        node = nodes[package_id]
        feature_list = sorted(node.get("features", []))
        features = ", ".join(feature_list) or "—"
        role_labels = sorted(roles.get(package_id, set()), key=role_order.index)
        package_paths = paths.get(package_id, {})
        representative_paths = [
            f"{'optional ' if optional else ''}{role}: {' → '.join(path)}"
            for (role, optional), path in sorted(
                package_paths.items(),
                key=lambda item: (
                    role_order.index(f"optional {item[0][0]}")
                    if item[0][1]
                    else role_order.index(item[0][0]),
                    item[1],
                ),
            )
            if role in {"runtime", "build", "dev"}
        ]
        direct_dependencies = []
        for dependency in sorted(node["deps"], key=lambda item: item["name"]):
            target = packages[dependency["pkg"]]
            labels = resolved_edge_labels(package, dependency, target)
            direct_dependencies.append(f"{package_label(target)} ({labels})")

        purpose = package.get("description")
        if package_id == root_id:
            purpose = "Core functionality for Pydantic validation and serialization"
        rows.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    package_label(package),
                    package_license(package),
                    package_source(package, root_id),
                    target_description(package),
                    ", ".join(role_labels),
                    package_native_boundary(package, root_id),
                    features,
                    purpose or "No package description in Cargo metadata",
                    "; ".join(representative_paths),
                    ", ".join(direct_dependencies),
                )
            )
            + " |"
        )

    lock_digest = source["cargo_lock_sha256"]
    manifest_digest = source["cargo_manifest_sha256"]
    count = len(nodes)
    role_summary = ", ".join(
        f"{role}: {role_counts[role]}" for role in role_order if role_counts[role]
    )
    table_header = (
        "| Crate | Source | License | Cargo targets | Role | Native part | Features | "
        "Purpose | Root path | Dependencies |"
    )
    return f"""# Pydantic Core {version} Rust dependency inventory

This is a separate inventory of Pydantic Core's pinned Rust extension crate and
the recursive Cargo graph resolved by its own `Cargo.lock`. Pydantic Core is a
separately installed Python runtime wheel used through PyO3. This graph is
Pydantic-owned; it is not added to FastAPI-RS's Cargo workspace or runtime
dependencies.

## Pinned source and package boundary

- Pydantic source tag `{source["tag"]}` resolves to commit `{source["commit"]}`
  in [{source["repository"]}](https://github.com/pydantic/pydantic/tree/{source["commit"]}).
- `pydantic-core/Cargo.toml` declares version `{version}`, MIT, Rust
  `{source["rust_version"]}`, and a `cdylib`/`rlib` library. It builds the
  Python extension through PyO3 0.28.3. The selected FastAPI-RS workspace uses
  Rust 1.85 and PyO3 0.29.2, so this source inventory must remain outside that
  Cargo graph.
- Cargo manifest SHA-256: `{manifest_digest}`.
- Pydantic Core Cargo lock SHA-256: `{lock_digest}`.
- The directly selected FastAPI-RS Python runtime pin is
  `pydantic-core=={version}`. Its Python package requires `typing-extensions`;
  this Rust table expands the native crate graph inside that distribution.

## Reading this graph

- Cargo resolves {count} package records from the pinned lockfile, including
  the root package. Exact versions, Cargo license expressions/files, package
  descriptions, target kinds, and active edge kinds/target predicates come from
  `cargo metadata --locked` for the pinned source.
- Cargo package features are the resolver's enabled-feature union across the
  lock graph, including default features when enabled and contexts that use
  optional features. The role column distinguishes runtime, build, and dev
  paths; feature lists are not a claim that every listed feature ships in each
  platform wheel. A listed `default` feature is enabled; Cargo enables default
  features for dependency declarations unless an edge says `default features
  disabled`. Optional dependency edges are labeled, and requested feature sets
  are kept separate when the same crate has normal, build, or dev declarations.
- A representative path starts at `pydantic-core`; immediate dependency lists
  retain normal/build/dev edge kind, target predicates, optional edges,
  explicitly requested features, and default-feature disabling. Package
  descriptions document each crate's purpose; the paths show why it is present.
- Language and target kinds come from Cargo package metadata. `Cargo links`
  records declared native link boundaries. `No Cargo links declaration`
  means metadata declares no linked foreign library; it does not prove that
  every published wheel contains no platform runtime references.
- Cargo license expressions are copied as declared; this report is not a
  source-file license audit of every registry package or a release-artifact
  notice bundle.

Role reachability counts (role sets may overlap): {role_summary}.

## Complete Cargo package graph

{table_header}
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Sources

- [Pinned Pydantic Core Cargo manifest](https://github.com/pydantic/pydantic/blob/{source["commit"]}/pydantic-core/Cargo.toml)
- [Pinned Pydantic Core Cargo lock](https://github.com/pydantic/pydantic/blob/{source["commit"]}/pydantic-core/Cargo.lock)
- [Pinned Pydantic Core package metadata](https://github.com/pydantic/pydantic/blob/{source["commit"]}/pydantic-core/pyproject.toml)
"""


def run(*, source_override: Path | None, offline: bool, check: bool) -> int:
    metadata = read_metadata()
    source, default_source_root, manifest_relative, version = read_pins(metadata)
    source_root = source_override.resolve() if source_override else default_source_root
    manifest_path = validate_source(source, source_root, manifest_relative)
    validate_package_identity(manifest_path, version, TARGET_PROJECT_PATH)
    cargo = cargo_metadata(manifest_path, offline=offline)
    document = render_inventory(cargo, source, version)
    output = ROOT / str(metadata["pydantic_core_dependency_inventory"]["artifact"])
    if check:
        try:
            current = output.read_text(encoding="utf-8")
        except OSError as exc:
            raise InventoryError(f"dependency inventory is missing: {output}: {exc}") from exc
        if current != document:
            raise InventoryError(f"dependency inventory is stale: regenerate {output}")
        print(
            f"Pydantic Core dependency inventory current: {version}, "
            f"{len(cargo['resolve']['nodes'])} resolved packages, source {source['commit']}"
        )
        return 0
    output.write_text(document, encoding="utf-8")
    print(f"wrote {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pydantic-source",
        type=Path,
        help="use a clean Pydantic source checkout containing pydantic-core/Cargo.lock",
    )
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        return run(source_override=args.pydantic_source, offline=args.offline, check=args.check)
    except (InventoryError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"Pydantic Core dependency inventory failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
