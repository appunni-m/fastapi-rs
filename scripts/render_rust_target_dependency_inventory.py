#!/usr/bin/env python3
"""Render the locked Rust workspace dependency and license inventory."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "RUST_TARGET_DEPENDENCIES.md"
ROLE_ORDER = (
    "runtime",
    "optional runtime",
    "build",
    "optional build",
    "dev",
    "optional dev",
)


def cargo_metadata(*, offline: bool) -> dict[str, Any]:
    command = [
        "cargo",
        "metadata",
        "--locked",
        "--format-version",
        "1",
        "--features",
        "pyo3/extension-module",
    ]
    if offline:
        command.append("--offline")
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "cargo metadata failed")
    return json.loads(result.stdout)


def validate_starlette_rs_revision(source_root: Path) -> str:
    """Require the local path dependency to match the reviewed source pin."""
    authority = yaml.safe_load((ROOT / "metadata.yaml").read_text(encoding="utf-8"))
    expected_revision = authority["starlette_rs"]["commit"]
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise RuntimeError(f"Starlette-RS source checkout does not exist: {source_root}")
    revision = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if revision != expected_revision:
        raise RuntimeError(
            "Starlette-RS source revision mismatch: "
            f"metadata pins {expected_revision}, local checkout is {revision}"
        )

    source_paths = (
        "Cargo.toml",
        "starlette-rs/Cargo.toml",
        "starlette-rs/src",
        "starlette-rs-py/Cargo.toml",
        "starlette-rs-py/src",
        "starlette-rs-py/python",
        "starlette-rs-py/pyproject.toml",
    )
    changes = subprocess.run(
        [
            "git",
            "-C",
            str(source_root),
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            *source_paths,
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if changes:
        raise RuntimeError(
            "Starlette-RS implementation sources are dirty; dependency inventory requires "
            f"the clean pinned revision {expected_revision}\n{changes}"
        )
    return expected_revision


def validate_cargo_source(metadata: dict[str, Any], source_root: Path) -> None:
    """Ensure Cargo resolved the Starlette-RS path passed to this inventory run."""
    expected_manifest = (source_root.resolve() / "starlette-rs" / "Cargo.toml").resolve()
    manifests = {
        Path(package["manifest_path"]).resolve()
        for package in metadata.get("packages", [])
        if package.get("name") == "starlette-rs"
    }
    if manifests != {expected_manifest}:
        raise RuntimeError(
            "Cargo metadata does not resolve the pinned Starlette-RS source argument: "
            f"expected={expected_manifest}, resolved={sorted(map(str, manifests))}"
        )


def markdown_cell(value: object) -> str:
    return " ".join(str(value or "—").split()).replace("|", "\\|")


def dependency_kinds(dependency: dict[str, Any]) -> set[str]:
    return {dep_kind["kind"] or "normal" for dep_kind in dependency.get("dep_kinds", [])}


def cargo_crate_name(value: str) -> str:
    """Normalize hyphen/underscore spelling differences in Cargo metadata names."""
    return value.replace("-", "_").lower()


def optional_dependency(
    package: dict[str, Any], dependency: dict[str, Any], target_package: dict[str, Any]
) -> bool:
    """Return whether this active metadata edge is declared optional."""
    active_kinds = {
        (dep_kind["kind"] or "normal", dep_kind.get("target"))
        for dep_kind in dependency.get("dep_kinds", [])
    }
    edge_name = dependency["name"]
    for declared in package.get("dependencies", []):
        if cargo_crate_name(declared["name"]) != cargo_crate_name(target_package["name"]):
            continue
        if cargo_crate_name(declared.get("rename") or declared["name"]) != cargo_crate_name(
            edge_name
        ):
            continue
        declared_kind = declared.get("kind") or "normal"
        if (declared_kind, declared.get("target")) not in active_kinds:
            continue
        if declared.get("optional", False):
            return True
    return False


def package_roles(metadata: dict[str, Any]) -> dict[str, set[str]]:
    """Propagate active Cargo dependency roles from the workspace product roots."""
    packages = {package["id"]: package for package in metadata["packages"]}
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    roles: dict[str, set[str]] = {}
    visited: set[tuple[str, str, bool]] = set()

    def visit(package_id: str, role: str, optional: bool) -> None:
        state = (package_id, role, optional)
        if state in visited:
            return
        visited.add(state)
        roles.setdefault(package_id, set()).add(f"optional {role}" if optional else role)
        node = nodes.get(package_id)
        package = packages.get(package_id)
        if node is None or package is None:
            return
        for dependency in node["deps"]:
            target_id = dependency["pkg"]
            target_package = packages[target_id]
            is_optional = optional or optional_dependency(package, dependency, target_package)
            for kind in dependency_kinds(dependency):
                next_role = role
                if kind == "build":
                    next_role = "build"
                elif kind == "dev":
                    next_role = "dev"
                visit(target_id, next_role, is_optional)

    workspace_members = metadata.get("workspace_members", [])
    if not workspace_members:
        raise RuntimeError("Cargo metadata does not identify workspace dependency roots")
    for package_id in workspace_members:
        visit(package_id, "runtime", False)
    return roles


def target_description(package: dict[str, Any]) -> str:
    """Describe Rust language and the declared Cargo target kinds."""
    kinds = sorted({kind for target in package.get("targets", []) for kind in target["kind"]})
    if not kinds:
        return "Rust (target kind unavailable)"
    language = "Rust proc macro" if "proc-macro" in kinds else "Rust"
    labels = {
        "bin": "binary",
        "cdylib": "C-compatible dynamic library",
        "custom-build": "build script",
        "dylib": "dynamic library",
        "example": "example",
        "lib": "library",
        "rlib": "Rust library",
        "staticlib": "static library",
        "test": "test target",
    }
    rendered_kinds = ", ".join(labels.get(kind, kind) for kind in kinds)
    return f"{language}; Cargo targets: {rendered_kinds}"


def foreign_boundary(
    package: dict[str, Any], annotations: dict[str, dict[str, str]]
) -> str:
    signals: list[str] = []
    links = package.get("links")
    if links:
        signals.append(f"Cargo links = {links}")
    annotation = annotations.get(package["name"])
    if annotation is not None:
        if package["version"] != annotation["version"]:
            raise RuntimeError(
                f"reviewed Cargo boundary annotation for {package['name']} "
                f"expects version {annotation['version']}, found {package['version']}"
            )
        if " ".join((package.get("description") or "").split()) != " ".join(
            annotation["source_description"].split()
        ):
            raise RuntimeError(
                f"reviewed Cargo boundary annotation for {package['name']} "
                "no longer matches its Cargo package description"
            )
        signals.append(f"Reviewed metadata annotation: {annotation['signal']}")
    return "; ".join(signals) or "No Cargo links declaration or reviewed boundary annotation"


def reviewed_boundary_annotations() -> dict[str, dict[str, str]]:
    authority = yaml.safe_load((ROOT / "metadata.yaml").read_text(encoding="utf-8"))
    inventory = authority.get("cargo_dependency_inventory", {})
    if inventory.get("schema") != "fastapi-rs/cargo-dependency-inventory-annotations@1":
        raise RuntimeError("metadata.yaml does not declare the reviewed Cargo inventory schema")
    annotations = inventory.get("foreign_boundary_annotations")
    if not isinstance(annotations, dict):
        raise RuntimeError("metadata.yaml Cargo foreign-boundary annotations must be a mapping")
    for name, annotation in annotations.items():
        if not isinstance(annotation, dict) or set(annotation) != {
            "version",
            "signal",
            "source_description",
        } or not all(
            isinstance(annotation[field], str) and annotation[field]
            for field in ("version", "signal", "source_description")
        ):
            raise RuntimeError(f"malformed reviewed Cargo boundary annotation: {name}")
    return annotations


def render(metadata: dict[str, Any], starlette_rs_revision: str) -> str:
    packages = {package["id"]: package for package in metadata["packages"]}
    nodes = {node["id"]: node for node in metadata["resolve"]["nodes"]}
    roles_by_package = package_roles(metadata)
    annotations = reviewed_boundary_annotations()
    active_packages_by_name: dict[str, list[dict[str, Any]]] = {}
    for package_id, package in packages.items():
        if package_id in nodes:
            active_packages_by_name.setdefault(package["name"], []).append(package)
    for name, annotation in annotations.items():
        matching = active_packages_by_name.get(name, [])
        if len(matching) != 1 or matching[0]["version"] != annotation["version"]:
            raise RuntimeError(
                f"reviewed Cargo boundary annotation for {name} does not identify exactly "
                "one active package at its pinned version"
            )
    rows: list[str] = []

    for package_id, package in sorted(
        packages.items(), key=lambda pair: (pair[1]["name"], pair[1]["version"])
    ):
        node = nodes.get(package_id)
        if node is None:
            continue
        package_id_label = f"{package['name']} {package['version']}"
        features = ", ".join(sorted(node["features"])) or "—"
        roles = sorted(roles_by_package.get(package_id, set()), key=ROLE_ORDER.index)
        if not roles:
            raise RuntimeError(f"active Cargo package has no workspace role: {package_id_label}")
        source = "registry"
        if package["source"] is None:
            source = "workspace/path"
        license_value = package.get("license")
        if not license_value and package.get("license_file"):
            license_value = f"file: {package['license_file']}"
        edges: list[str] = []
        for dependency in sorted(node["deps"], key=lambda item: item["name"]):
            target = packages[dependency["pkg"]]
            edge_name = f"{target['name']} {target['version']}"
            kinds = sorted({dep_kind["kind"] or "normal" for dep_kind in dependency["dep_kinds"]})
            if kinds != ["normal"]:
                edge_name += f" ({', '.join(kinds)})"
            edges.append(edge_name)
        rows.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    package_id_label,
                    license_value or "UNSPECIFIED",
                    target_description(package),
                    ", ".join(roles),
                    foreign_boundary(package, annotations),
                    source,
                    features,
                    package.get("description") or "No Cargo package description",
                    ", ".join(edges) or "—",
                )
            )
            + " |"
        )

    return f"""# FastAPI-RS Rust dependency inventory

This report is generated by `scripts/render_rust_target_dependency_inventory.py`
from `cargo metadata --locked --format-version 1 --features
pyo3/extension-module`. It describes the current Cargo.lock graph, including the
local Starlette-RS path dependency at reviewed commit
`{starlette_rs_revision}` and the extension-module feature used by Maturin.
Regenerate after changing a Cargo manifest, the lockfile, or the reviewed
Starlette-RS revision. The lock snapshot is [`Cargo.lock`](../Cargo.lock); a
clean checkout of the pinned Starlette-RS revision is required to resolve the
path dependency.

## Direct use in the project

| Dependency | Declared by | Current purpose and source evidence |
| --- | --- | --- |
| `starlette-rs` 0.1.0 | `fastapi-rs` normal dependency | Rust routing and request-input primitives used by `fastapi-rs/src/operation.rs` (`RouteTable`, `DetailedRouteMatch`, `QueryParams`, `RequestHeaders`, and `RouteError`). FastAPI-RS owns ASGI orchestration, dependency execution, validation, response shaping, and OpenAPI integration in `fastapi-rs/src/application_runtime.rs`. |
| `pyo3` 0.29.2 | `fastapi-rs` and `fastapi-rs-py` normal dependencies | Python/Rust binding API used by the Rust-owned FastAPI runtime in `fastapi-rs/src/application_runtime.rs` and `fastapi-rs/src/parameters.rs`, and by extension registration and existing bindings in `fastapi-rs-py/src/lib.rs`. `abi3-py310` sets the stable Python ABI minimum; Maturin enables `pyo3/extension-module` from `pyproject.toml`. |
| `pyo3-build-config` 0.29.2 | `fastapi-rs-py` build dependency | PyO3 linker configuration invoked by `fastapi-rs-py/build.rs` so the Rust cdylib is linked as a Python extension. |
| `flate2` 1.1.10 | Starlette-RS normal dependency | Starlette-RS gzip middleware in `starlette-rs/src/gzip.rs`; enables `zlib` with default features disabled, selecting `libz-sys` and its native zlib backend. |
| `getrandom` 0.4.3 | Starlette-RS normal dependency | Creates unpredictable multipart boundaries for multi-range file responses in `starlette-rs/src/file_response.rs`. |
| `httpdate` 1.0.3 | Starlette-RS normal dependency | Formats the `Last-Modified` header for file responses in `starlette-rs/src/file_response.rs`. |
| `md-5` 0.11.0 | Starlette-RS normal dependency | Computes the ETag for file responses in `starlette-rs/src/file_response.rs`. |
| `mime_guess` 2.0.5 | Starlette-RS normal dependency | Infers file-response media types from paths in `starlette-rs/src/file_response.rs`. |
| `serde_json` 1.0.151 | Starlette-RS normal dependency | JSON protocol parsing and output in `starlette-rs/src/bin/starlette-rs-parity-adapter.rs`. |
| `sha2` 0.10.9 | Starlette-RS normal dependency | SHA-256 dependency-lock identity check in the same parity adapter. |

The four file-response dependencies are used by the Starlette-RS library.
`serde_json` and `sha2` are used by its parity-adapter binary but are currently
declared as normal dependencies, so they remain in the package's Cargo graph.
The adapter uses Rust; the zlib path additionally links the platform C zlib
library. The `cc`, `pkg-config`, and `vcpkg` crates support native zlib
discovery/building. Transitive crates below PyO3 provide Python C-API bindings,
procedural macros, Rust syntax/token processing, and their helper routines;
each exact edge is listed below.

## Complete locked package graph

Cargo metadata reports every active workspace/registry package, selected
feature, package license expression, Cargo target kind, declared `links`
value, declared target kinds, description, and immediate dependency edges.
Listed target kinds are package declarations, not claims that every test,
example, or benchmark target is built in this profile. Roles propagate from
the workspace product roots: normal edges preserve the current role, while
build and dev edges classify their dependency subgraphs as build or dev.
Optional labels mark packages reached through an active optional dependency
edge. The foreign-boundary column reports Cargo `links` declarations and
reviewed package-description annotations in `metadata.yaml`; an absent signal
means no such declaration is present in this inventory. Cargo license
expressions are preserved verbatim; `OR` means the distributor may satisfy
either license, while `AND` requires both.

| Package | Cargo license expression/file | Language and declared Cargo targets | Role(s) | Native/foreign boundary signal | Source | Enabled features | Package purpose | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Python package dependencies

The Python distribution declares `pydantic==2.13.4` and
`starlette-rs-py==0.1.0` in `pyproject.toml`; the selected oracle profile uses
Pydantic 2.13.4. Pydantic's Python package builds schemas and exposes model
behavior, while `pydantic-core` supplies its Rust validation/serialization
engine. `starlette-rs-py` is a separate Rust/Python package and declares AnyIO
`>=3.6.2,<5` in its own manifest. Maturin 1.14.1 is the Python build-system
dependency. The target pins its direct Python runtime packages but does not yet
have a lockfile for their full resolved closure; the FastAPI 0.141.1 oracle
closure is separately locked and documented in
[`DEPENDENCY_GRAPH.md`](DEPENDENCY_GRAPH.md).

Pydantic's public model/schema API and user-supplied endpoints or validators
remain Python objects. Rust owns FastAPI-specific orchestration and framework
control flow, invoking those user/Pydantic callables through PyO3 where needed;
`pydantic-core` supplies Pydantic's Rust validation/serialization engine. The
public `fastapi` package is restricted to direct native re-exports and literal
`__all__`. The current consumer-facing runtime is a first ASGI slice with Rust
owning route registration, dependency execution, request validation, response
model filtering, and OpenAPI assembly; Pydantic models and user callables remain
Python objects invoked through PyO3.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT.parent / "starlette-rs")
    args = parser.parse_args()
    try:
        revision = validate_starlette_rs_revision(args.starlette_rs_source)
        metadata = cargo_metadata(offline=args.offline)
        validate_cargo_source(metadata, args.starlette_rs_source)
        output = render(metadata, revision)
    except (RuntimeError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"dependency inventory failed: {error}", file=sys.stderr)
        return 1
    if args.check:
        try:
            current = OUTPUT.read_text(encoding="utf-8")
        except OSError as error:
            print(f"dependency inventory is missing: {OUTPUT}: {error}", file=sys.stderr)
            return 1
        if current != output:
            print(f"dependency inventory is stale: regenerate {OUTPUT}", file=sys.stderr)
            return 1
        print(f"dependency inventory current for Starlette-RS {revision}")
        return 0
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
