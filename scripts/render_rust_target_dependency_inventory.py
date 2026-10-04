#!/usr/bin/env python3
"""Render the locked Rust workspace dependency and license inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "RUST_TARGET_DEPENDENCIES.md"
BUILD_TOOLS_INPUT = ROOT / "requirements" / "build-tools-cpython-3.12.13.in"
BUILD_TOOLS_LOCK = ROOT / "requirements" / "build-tools-cpython-3.12.13.lock"
ROLE_ORDER = (
    "runtime",
    "optional runtime",
    "build",
    "optional build",
    "dev",
    "optional dev",
)
BUILD_TOOL_REVIEW = {
    "maturin": {
        "version": "1.14.1",
        "purpose": (
            "Pinned PEP 517 backend that invokes Cargo and packages the Rust extension as a "
            "Python wheel."
        ),
        "implementation": (
            "Python backend shim plus a Rust native CLI shipped in platform-specific "
            "py3-none wheels"
        ),
        "license": "MIT OR Apache-2.0",
    }
}
LOCKED_PACKAGE_LINE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s\\]+)(?:\s+\\)?$")
SHA256_HASH = re.compile(r"^--hash=sha256:([0-9a-f]{64})$")


def cargo_metadata(*, offline: bool, starlette_rs_source: Path) -> dict[str, Any]:
    """Read Cargo's resolved graph with the reviewed Starlette-RS source path.

    The checkout's normal workspace manifest points at the sibling development
    checkout. Build a short-lived manifest overlay so inventory checks can use
    the pinned clean source without editing Cargo.toml or touching that sibling.
    """
    workspace_manifest = ROOT / "Cargo.toml"
    manifest_text = workspace_manifest.read_text(encoding="utf-8")
    manifest_data = tomllib.loads(manifest_text)
    workspace = manifest_data.get("workspace", {})
    starlette_dependency = workspace.get("dependencies", {}).get("starlette-rs")
    if not isinstance(starlette_dependency, dict) or not starlette_dependency.get("path"):
        raise RuntimeError("Cargo.toml must declare starlette-rs as a workspace path dependency")
    declared_path = starlette_dependency["path"]
    old_path = f"path = {json.dumps(declared_path)}"
    if manifest_text.count(old_path) != 1:
        raise RuntimeError("Cargo.toml starlette-rs workspace dependency path is ambiguous")
    pinned_path = starlette_rs_source.resolve() / "starlette-rs"
    overlay_text = manifest_text.replace(old_path, f"path = {json.dumps(str(pinned_path))}", 1)

    command = [
        "cargo",
        "metadata",
        "--manifest-path",
        "Cargo.toml",
        "--locked",
        "--format-version",
        "1",
        "--features",
        "pyo3/extension-module",
    ]
    if offline:
        command.append("--offline")
    with tempfile.TemporaryDirectory(prefix=".fastapi-rs-cargo-metadata-", dir=ROOT) as tmp:
        overlay_root = Path(tmp)
        (overlay_root / "Cargo.toml").write_text(overlay_text, encoding="utf-8")
        shutil.copy2(ROOT / "Cargo.lock", overlay_root / "Cargo.lock")
        members = workspace.get("members", [])
        if not members:
            raise RuntimeError("Cargo.toml does not declare workspace members")
        for member in members:
            member_path = Path(member)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise RuntimeError(f"unsupported non-workspace Cargo member path: {member}")
            source_member = ROOT / member_path
            if not source_member.exists():
                raise RuntimeError(f"Cargo workspace member does not exist: {member}")
            link_path = overlay_root / member_path
            link_path.parent.mkdir(parents=True, exist_ok=True)
            link_path.symlink_to(source_member, target_is_directory=source_member.is_dir())
        result = subprocess.run(
            command,
            cwd=overlay_root,
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


def canonical_distribution_name(name: str) -> str:
    """Normalize a Python distribution name according to PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


def exact_python_pins(requirements: list[str], *, source: str) -> dict[str, tuple[str, str]]:
    """Read a deliberately small list of exact, marker-free Python pins."""
    pins: dict[str, tuple[str, str]] = {}
    for requirement in requirements:
        match = re.fullmatch(
            r"\s*([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)\s*",
            requirement,
        )
        if match is None:
            raise RuntimeError(f"{source} must contain only exact Python pins: {requirement!r}")
        name, version = match.groups()
        normalized = canonical_distribution_name(name)
        if normalized in pins:
            raise RuntimeError(f"{source} contains duplicate normalized package {name!r}")
        pins[normalized] = (name, version)
    return pins


def read_hashed_python_lock(path: Path) -> dict[str, tuple[str, int]]:
    """Read package versions and SHA-256 counts from a uv pip compile requirements lock."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"cannot read Python build-tool lock {path}: {exc}") from exc

    packages: dict[str, tuple[str, int]] = {}
    current_name: str | None = None
    current_version: str | None = None
    current_hashes: set[str] = set()

    def finish_package() -> None:
        nonlocal current_name, current_version, current_hashes
        if current_name is None or current_version is None:
            return
        normalized = canonical_distribution_name(current_name)
        if normalized in packages:
            raise RuntimeError(f"build-tool lock repeats package {current_name!r}")
        if not current_hashes:
            raise RuntimeError(f"build-tool lock has no SHA-256 hashes for {current_name}")
        packages[normalized] = (current_version, len(current_hashes))
        current_name = None
        current_version = None
        current_hashes = set()

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        entry = LOCKED_PACKAGE_LINE.fullmatch(stripped)
        if entry is not None:
            finish_package()
            current_name, current_version = entry.groups()
            continue
        hash_text = stripped.removesuffix("\\").rstrip()
        hash_entry = SHA256_HASH.fullmatch(hash_text)
        if hash_entry is not None and current_name is not None:
            current_hashes.add(hash_entry.group(1))
            continue
        raise RuntimeError(f"{path}:{line_number}: unsupported build-tool lock line {stripped!r}")
    finish_package()
    if not packages:
        raise RuntimeError(f"build-tool lock contains no package entries: {path}")
    return packages


def render_python_build_tool_inventory() -> str:
    """Validate and describe the separately locked CPython build-tool closure."""
    try:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        input_lines = BUILD_TOOLS_INPUT.read_text(encoding="utf-8").splitlines()
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"cannot read build-tool requirements: {exc}") from exc

    input_requirements = [
        line.strip() for line in input_lines if line.strip() and not line.lstrip().startswith("#")
    ]
    input_pins = exact_python_pins(
        input_requirements, source=str(BUILD_TOOLS_INPUT.relative_to(ROOT))
    )
    project_requires = pyproject.get("build-system", {}).get("requires", [])
    if not isinstance(project_requires, list) or any(
        not isinstance(requirement, str) for requirement in project_requires
    ):
        raise RuntimeError("pyproject.toml build-system.requires must be a string list")
    project_pins = exact_python_pins(
        project_requires, source="pyproject.toml build-system.requires"
    )
    if project_pins != input_pins:
        raise RuntimeError(
            "build-tool requirements input must match pyproject.toml build-system.requires: "
            f"project={project_pins!r}, input={input_pins!r}"
        )

    locked_packages = read_hashed_python_lock(BUILD_TOOLS_LOCK)
    reviewed_packages = set(BUILD_TOOL_REVIEW)
    if set(locked_packages) != reviewed_packages:
        raise RuntimeError(
            "build-tool lock package set differs from reviewed inventory metadata: "
            f"locked={sorted(locked_packages)}, reviewed={sorted(reviewed_packages)}"
        )
    for name, (locked_version, _) in locked_packages.items():
        reviewed_version = BUILD_TOOL_REVIEW[name].get("version")
        if locked_version != reviewed_version:
            raise RuntimeError(
                f"build-tool lock/review do not agree on {name}: "
                f"lock={locked_version}, review={reviewed_version}"
            )
    for name, (_, required_version) in input_pins.items():
        lock_record = locked_packages.get(name)
        if lock_record is None or lock_record[0] != required_version:
            raise RuntimeError(
                f"build-tool lock does not resolve {name} to required version {required_version}"
            )

    rows: list[str] = []
    for name in sorted(locked_packages):
        version, hash_count = locked_packages[name]
        review = BUILD_TOOL_REVIEW[name]
        display_name = input_pins.get(name, (name, version))[0]
        rows.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in (
                    f"{display_name} {version}",
                    "build",
                    review["purpose"],
                    review["implementation"],
                    review["license"],
                    f"{hash_count} SHA-256 artifact hashes",
                )
            )
            + " |"
        )

    lock_digest = hashlib.sha256(BUILD_TOOLS_LOCK.read_bytes()).hexdigest()
    distribution_word = "distribution" if len(locked_packages) == 1 else "distributions"
    source_links = ", ".join(
        f"[{label}]({url})"
        for label, url in (
            (
                "Maturin 1.14.1 backend documentation",
                "https://github.com/PyO3/maturin/blob/v1.14.1/README.md",
            ),
            (
                "Maturin 1.14.1 package license metadata",
                "https://github.com/PyO3/maturin/blob/v1.14.1/Cargo.toml",
            ),
            (
                "Maturin 1.14.1 PyPI requirements metadata",
                "https://pypi.org/pypi/maturin/1.14.1/json",
            ),
        )
    )
    return f"""### Isolated Python build-tool closure

`requirements/build-tools-cpython-3.12.13.in` and its hash-locked output
[`requirements/build-tools-cpython-3.12.13.lock`](../requirements/build-tools-cpython-3.12.13.lock)
define a CPython 3.12.13 build-tool environment, separate from the target
runtime lock. Its lock SHA-256 is
`{lock_digest}`. The lock resolves the full Python distribution closure. Each
listed artifact has a recorded SHA-256, and `make build-tools-prepare` installs
it with `uv pip sync --require-hashes`.

| Distribution | Role | Purpose | Implementation / native parts | Release license | Artifact hashes |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

The locked closure contains {len(locked_packages)} Python {distribution_word}; the
CPython 3.12.13 profile selects no additional Python distributions. Maturin
1.14.1's metadata adds `tomli` only below Python 3.11; its optional `patchelf`
and `ziglang` extras are not selected. Maturin is the project's PEP 517 backend
and runs Cargo to build the extension.
{source_links}.
"""


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


def foreign_boundary(package: dict[str, Any], annotations: dict[str, dict[str, str]]) -> str:
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
        if (
            not isinstance(annotation, dict)
            or set(annotation)
            != {
                "version",
                "signal",
                "source_description",
            }
            or not all(
                isinstance(annotation[field], str) and annotation[field]
                for field in ("version", "signal", "source_description")
            )
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
            edge_kinds = {
                (dep_kind.get("kind") or "normal", dep_kind.get("target"))
                for dep_kind in dependency.get("dep_kinds", [])
            }
            labels = sorted(
                f"{kind} if {target_predicate}" if target_predicate else kind
                for kind, target_predicate in edge_kinds
            ) or ["normal"]
            if labels != ["normal"]:
                edge_name += f" ({'; '.join(labels)})"
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

    build_tool_inventory = render_python_build_tool_inventory()
    return f"""# FastAPI-RS Rust dependency inventory

This report is generated by `scripts/render_rust_target_dependency_inventory.py`
from `cargo metadata --locked --format-version 1 --features
pyo3/extension-module`. It describes the current Cargo.lock graph, including the
local Starlette-RS path dependency at reviewed commit
`{starlette_rs_revision}` and the extension-module feature used by Maturin.
Dependency edges retain Cargo kind and target predicates; a conditional edge
applies only to targets matching its predicate. Package roles summarize the
resolved graph and do not make every conditional edge active on every platform.
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
| `sha2` 0.11.0 | Starlette-RS normal dependency | SHA-256 dependency-lock identity check in the same parity adapter. |

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

### Native C zlib backend

The pinned Starlette-RS workspace enables `flate2` 1.1.10's `zlib` feature
with default features disabled. That selects `libz-sys` 1.1.29, whose license
expression is MIT OR Apache-2.0 and whose native interface is C. Its build
script can link a host-provided zlib (discovered with `pkg-config` or vcpkg)
or compile the bundled stock zlib C source, version 1.3.2, as a fallback. The
bundled zlib source has its own zlib license, separate from `libz-sys`'s Cargo
license expression. Cargo.lock pins `libz-sys`, not the host library selected
for each platform build; record the actual linked backend and preserve its
applicable notices for every release artifact. `cc`, `pkg-config`, and `vcpkg`
are build-time support for this discovery/fallback path.

## Python package dependencies

The Python distribution directly pins `annotated-doc==0.0.4`,
`pydantic==2.13.4`,
`pydantic-core==2.46.4`, and `starlette-rs-py==0.1.0` in `pyproject.toml`.
FastAPI-RS Rust code imports `annotated_doc.Doc` through PyO3 while registering
public Python signatures, dependency/security parameters, and exceptions; it
constructs the `Annotated` documentation metadata consumed by introspection.
Pydantic's Python package builds schemas and exposes model behavior, while the
separately installed `pydantic-core` wheel supplies its Rust
validation/serialization engine. `starlette-rs-py` is a separate Rust/Python
package and declares AnyIO `>=3.6.2,<5` plus typing-extensions `>=4.12.0` in
its own manifest. Maturin 1.14.1 is
the Python build-system dependency. The external target runtime closure is
hash-locked for CPython 3.12.13 in
[`requirements/target-runtime-cpython-3.12.13.lock`](../requirements/target-runtime-cpython-3.12.13.lock);
the local Starlette-RS source install is separately pinned. The FastAPI
0.141.1 oracle closure is separately locked and documented in
[`DEPENDENCY_GRAPH.md`](DEPENDENCY_GRAPH.md).

{build_tool_inventory}

### Narrow Pydantic Core encoder bridge

FastAPI 0.141.1's public `jsonable_encoder` imports
`PydanticUndefinedType` from `pydantic_core` and encodes its instances as
`None` (`fastapi/encoders.py:27,279–280`). It registers `Url` and `AnyUrl` as
string encoders (`fastapi/encoders.py:103–111`); `AnyUrl` comes from
`pydantic.networks`, while the FastAPI compatibility layer imports `Url` from
Pydantic Core (`fastapi/_compat/v2.py:32–34`). The Rust target does not import
these classes at module load: its encoder performs runtime instance checks for
`PydanticUndefinedType` and resolves the URL classes dynamically
(`fastapi-rs/src/encoding.rs:223–225,407–415`).

Pinned implementation evidence is FastAPI 0.141.1 commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`: `fastapi/encoders.py`
SHA-256 `4cc09230eca6435892f6bc25a2185e214dbedfe994d5103feb63ad269137caad`
and `fastapi/_compat/v2.py` SHA-256
`b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9`.
The input-only encoder review is
`tests/fixtures/input-recipes/parity/pydantic-core-encoder-compatibility.yaml`.

These runtime checks are an internal compatibility bridge, not a FastAPI-RS
public API. The `pydantic-core` wheel is a direct target Python runtime
dependency and its Rust implementation remains Pydantic-owned, outside this
workspace's Cargo graph. The explicit `2.46.4` pin matches the selected
manifest identity. The public Pydantic `AnyUrl` type does not replace the raw
Core `Url` check, and Pydantic does not export the undefined sentinel type as
a public API. Keep the behavior tied to these encoder classifications and
revisit it when the Pydantic pin changes.

Pydantic's public model/schema API and user-supplied endpoints or validators
remain Python objects. Rust owns FastAPI-specific orchestration and framework
control flow, invoking those user/Pydantic callables through PyO3 where needed;
`pydantic-core` supplies Pydantic's Rust validation/serialization engine. The
public `fastapi` package is restricted to direct native re-exports and literal
`__all__`. The current consumer-facing runtime is a first ASGI slice with Rust
owning route registration, dependency execution, request validation, response
model filtering, and OpenAPI assembly; Pydantic models and user callables remain
Python objects invoked through PyO3.

Do not add the pinned `pydantic-core` crate directly to this workspace without
an explicit toolchain and boundary review. Its [2.46.4 Cargo manifest] sets
`rust-version = 1.88` and depends on PyO3 0.28, while this workspace declares
Rust 1.85 and PyO3 0.29.2. Pydantic's [architecture contract] also treats model
definition and core-schema generation as Python package work, with validation
and serialization delegated to the Rust core. Keep FastAPI-specific control
flow in `fastapi-rs`, and call Pydantic's public model/schema APIs through the
existing PyO3 boundary.

[2.46.4 Cargo manifest]: https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/Cargo.toml
[architecture contract]: https://pydantic.dev/docs/validation/dev/internals/architecture/
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT.parent / "starlette-rs")
    args = parser.parse_args()
    try:
        revision = validate_starlette_rs_revision(args.starlette_rs_source)
        metadata = cargo_metadata(
            offline=args.offline, starlette_rs_source=args.starlette_rs_source
        )
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
