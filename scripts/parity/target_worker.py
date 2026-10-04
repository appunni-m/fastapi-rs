"""Run input-only FastAPI-RS workflows in one isolated target process."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import importlib.machinery
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import tomllib

from scripts.parity.fault_contracts import verification_mode
from scripts.parity.worker import (
    RESULT_SCHEMA_ID,
    RESULT_SCHEMA_V3_ID,
    RESULT_SCHEMA_V4_ID,
    RESULT_SCHEMA_V5_ID,
    RESULT_SCHEMA_V6_ID,
    RESULT_SCHEMA_V7_ID,
    ROOT,
    WORKFLOW_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V7_ID,
    WorkerError,
    _assert_clean_source_tree,
    _git_commit,
    _is_under,
    _load_workload,
    _run_case_v3,
    _run_cases,
    _run_cases_v3,
    _sha256_file,
    _validate_workload_path,
)

TARGET_PACKAGE_ROOT = ROOT / "fastapi-rs-py/python/fastapi"
TARGET_BINDING_ROOT = ROOT / "fastapi-rs-py/python/fastapi_rs"
FAULT_BINDING_ROOT = ROOT / "target/fault-injection/python/fastapi_rs"
STARLETTE_PACKAGE_RELATIVE_PATH = "starlette-rs-py/python/starlette"
STARLETTE_BINDING_RELATIVE_PATH = "starlette-rs-py/python/starlette_rs_py"
SHARED_ORACLE_PACKAGES = {
    "annotated-doc",
    "annotated-types",
    "anyio",
    "idna",
    "pydantic",
    "pydantic-core",
    "typing-extensions",
    "typing-inspection",
}


def _normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise WorkerError(f"workflow contains a duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise WorkerError(f"workflow contains a non-finite JSON number: {value}")


def _read_workflow(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkerError(f"cannot read validated workflow input: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkerError("workflow input must be a JSON object")
    return value


def _distribution(name: str) -> importlib.metadata.Distribution:
    try:
        return importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError as exc:
        raise WorkerError(f"target runtime package is missing: {name}") from exc


def _distribution_packages() -> dict[str, str]:
    packages: dict[str, str] = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        if not name:
            raise WorkerError("target runtime contains a distribution without a name")
        normalized = _normalize_distribution_name(name)
        if normalized in packages:
            raise WorkerError(f"target runtime contains duplicate distributions: {normalized}")
        packages[normalized] = distribution.version
    return packages


def _assert_editable_distribution(
    distribution: importlib.metadata.Distribution,
    expected_source: Path,
    label: str,
) -> None:
    raw_direct_url = distribution.read_text("direct_url.json")
    if raw_direct_url is None:
        raise WorkerError(f"{label} distribution is not linked to a source checkout")
    try:
        direct_url = json.loads(raw_direct_url)
    except json.JSONDecodeError as exc:
        raise WorkerError(f"{label} distribution has malformed direct_url.json") from exc
    if not isinstance(direct_url, dict):
        raise WorkerError(f"{label} distribution has malformed direct_url.json")
    parsed_url = urlsplit(direct_url.get("url", ""))
    if parsed_url.scheme != "file" or parsed_url.netloc not in {"", "localhost"}:
        raise WorkerError(f"{label} distribution does not use a local source checkout")
    actual_source = Path(unquote(parsed_url.path)).resolve()
    if actual_source != expected_source.resolve():
        raise WorkerError(
            f"{label} distribution source mismatch: expected {expected_source}, got {actual_source}"
        )
    if direct_url.get("dir_info", {}).get("editable") is not True:
        raise WorkerError(f"{label} distribution must be installed from its editable source")


def _assert_module_source(module: Any, expected_root: Path, label: str) -> Path:
    module_file = getattr(module, "__file__", None)
    if not isinstance(module_file, str):
        raise WorkerError(f"{label} module has no concrete source path")
    resolved = Path(module_file).resolve()
    if not _is_under(resolved, expected_root):
        raise WorkerError(f"{label} imported outside the selected source checkout: {resolved}")
    return resolved


def _extension_path(module: Any, label: str) -> Path:
    module_file = getattr(module, "__file__", None)
    if not isinstance(module_file, str):
        raise WorkerError(f"{label} native extension has no file identity")
    resolved = Path(module_file).resolve()
    if not resolved.is_file() or not any(
        resolved.name.endswith(suffix) for suffix in importlib.machinery.EXTENSION_SUFFIXES
    ):
        raise WorkerError(f"{label} did not load a compiled Python extension: {resolved}")
    return resolved


def _source_tree_sha256(root: Path, label: str) -> str:
    """Hash tracked and non-ignored source files, including working-tree edits."""
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        check=False,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise WorkerError(f"cannot enumerate {label} source files: {detail}")

    paths = sorted(set(entry for entry in completed.stdout.split(b"\0") if entry))
    digest = hashlib.sha256()
    for relative_bytes in paths:
        relative = os.fsdecode(relative_bytes)
        path = root / relative
        digest.update(relative_bytes)
        digest.update(b"\0")
        if path.is_symlink():
            digest.update(b"symlink\0")
            digest.update(os.fsencode(os.readlink(path)))
        elif path.is_file():
            digest.update(b"file\0")
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            # A deleted tracked file must affect the identity too.
            digest.update(b"missing\0")
        digest.update(b"\0")
    return digest.hexdigest()


def _combine_digests(entries: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(entries.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(value.encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _cargo_starlette_rs_source(target_source: Path, starlette_rs_source: Path) -> Path:
    """Resolve the Starlette-RS crate Cargo actually links into FastAPI-RS."""
    workspace_manifest = target_source / "Cargo.toml"
    try:
        manifest_text = workspace_manifest.read_text(encoding="utf-8")
        manifest_data = tomllib.loads(manifest_text)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise WorkerError(f"cannot read target Cargo workspace manifest: {exc}") from exc
    workspace = manifest_data.get("workspace", {})
    starlette_dependency = workspace.get("dependencies", {}).get("starlette-rs")
    if not isinstance(starlette_dependency, dict) or not starlette_dependency.get("path"):
        raise WorkerError("Cargo.toml must declare starlette-rs as a workspace path dependency")
    declared_path = starlette_dependency["path"]
    old_path = f"path = {json.dumps(declared_path)}"
    if manifest_text.count(old_path) != 1:
        raise WorkerError("Cargo.toml starlette-rs workspace dependency path is ambiguous")
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
        "--offline",
    ]
    with tempfile.TemporaryDirectory(
        prefix=".fastapi-rs-cargo-metadata-", dir=target_source
    ) as tmp:
        overlay_root = Path(tmp)
        (overlay_root / "Cargo.toml").write_text(overlay_text, encoding="utf-8")
        shutil.copy2(target_source / "Cargo.lock", overlay_root / "Cargo.lock")
        for filename in ("README.md", "LICENSE.md", "THIRD_PARTY_NOTICES.md"):
            shutil.copy2(target_source / filename, overlay_root / filename)
        members = workspace.get("members", [])
        if not members:
            raise WorkerError("Cargo.toml does not declare workspace members")
        for member in members:
            member_path = Path(member)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise WorkerError(f"unsupported non-workspace Cargo member path: {member}")
            source_member = target_source / member_path
            if not source_member.exists():
                raise WorkerError(f"Cargo workspace member does not exist: {member}")
            link_path = overlay_root / member_path
            link_path.parent.mkdir(parents=True, exist_ok=True)
            link_path.symlink_to(source_member, target_is_directory=source_member.is_dir())
        completed = subprocess.run(
            command,
            cwd=overlay_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            raise WorkerError(
                "cannot resolve target Cargo dependencies: "
                + (completed.stderr.strip() or "cargo metadata failed")
            )
        try:
            metadata = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise WorkerError(f"Cargo returned malformed dependency metadata: {exc}") from exc

        if Path(metadata.get("workspace_root", "")).resolve() != overlay_root.resolve():
            raise WorkerError(
                "Cargo metadata did not resolve this FastAPI overlay as its workspace"
            )
        packages = {package["id"]: package for package in metadata.get("packages", [])}
        workspace_members = set(metadata.get("workspace_members", []))
        expected_members = {
            "fastapi-rs": target_source / "fastapi-rs/Cargo.toml",
            "fastapi-rs-py": target_source / "fastapi-rs-py/Cargo.toml",
        }
        root_packages: dict[str, dict[str, Any]] = {}
        for name, member_manifest in expected_members.items():
            matches = [
                package
                for package in packages.values()
                if package.get("name") == name
                and Path(package.get("manifest_path", "")).resolve() == member_manifest.resolve()
                and package.get("id") in workspace_members
            ]
            if len(matches) != 1:
                raise WorkerError(
                    "Cargo metadata does not prove the overlay contains FastAPI workspace member "
                    f"{name}"
                )
            root_packages[name] = matches[0]
        root_node = next(
            (
                node
                for node in metadata.get("resolve", {}).get("nodes", [])
                if node["id"] == root_packages["fastapi-rs"]["id"]
            ),
            None,
        )
        if root_node is None:
            raise WorkerError("Cargo metadata omitted the FastAPI-RS dependency node")
        starlette_packages = [
            packages[dependency["pkg"]]
            for dependency in root_node.get("deps", [])
            if packages.get(dependency.get("pkg"), {}).get("name") == "starlette-rs"
        ]
        if len(starlette_packages) != 1:
            raise WorkerError("FastAPI-RS must resolve exactly one Starlette-RS Cargo dependency")
        manifest_path = Path(starlette_packages[0]["manifest_path"]).resolve()
        return manifest_path.parent.parent.resolve()


def _target_identity(
    target_source: Path,
    starlette_rs_source: Path,
    *,
    target_profile: dict[str, Any],
    fault_injection_required: bool | None = None,
) -> dict[str, Any]:
    if set(target_profile) != {"python", "shared_runtime_packages", "target"}:
        raise WorkerError("target profile is malformed")
    python_profile = target_profile["python"]
    shared_runtime_packages = target_profile["shared_runtime_packages"]
    distribution_profile = target_profile["target"]
    if (
        not isinstance(python_profile, dict)
        or not isinstance(shared_runtime_packages, dict)
        or not isinstance(distribution_profile, dict)
    ):
        raise WorkerError("target profile fields must be objects")
    starlette_profile = distribution_profile.get("starlette_rs_distribution")
    if (
        distribution_profile.get("public_surface") != "import fastapi"
        or not isinstance(starlette_profile, dict)
        or starlette_profile.get("starlette_contract") != "1.6.0"
        or not isinstance(starlette_profile.get("commit"), str)
    ):
        raise WorkerError(
            "target profile does not select the pinned public and Starlette contracts"
        )
    target_source = target_source.resolve()
    starlette_rs_source = starlette_rs_source.resolve()
    if target_source != ROOT.resolve():
        raise WorkerError(f"target worker must identify this FastAPI-RS checkout: {ROOT}")
    cargo_starlette_rs_source = _cargo_starlette_rs_source(target_source, starlette_rs_source)
    if cargo_starlette_rs_source != starlette_rs_source:
        raise WorkerError(
            "FastAPI-RS Cargo links a different Starlette-RS source than the target Python "
            f"environment: Cargo={cargo_starlette_rs_source}, Python={starlette_rs_source}"
        )
    _assert_clean_source_tree(
        starlette_rs_source,
        "Starlette-RS",
        allowed_untracked=frozenset({".DS_Store"}),
    )
    starlette_rs_revision = _git_commit(starlette_rs_source, "Starlette-RS")
    expected_starlette_rs_revision = starlette_profile["commit"]
    if starlette_rs_revision != expected_starlette_rs_revision:
        raise WorkerError(
            "Starlette-RS source commit differs from the selected target profile: "
            f"expected {expected_starlette_rs_revision}, got {starlette_rs_revision}"
        )

    if set(shared_runtime_packages) != SHARED_ORACLE_PACKAGES:
        raise WorkerError("target profile has an incomplete shared runtime package set")
    expected_packages = dict(shared_runtime_packages)
    expected_packages.update(
        {
            "fastapi-rs": str(distribution_profile["version"]),
            "starlette-rs-py": str(starlette_profile["version"]),
        }
    )
    actual_packages = _distribution_packages()
    if actual_packages != expected_packages:
        missing = sorted(set(expected_packages) - set(actual_packages))
        unexpected = sorted(set(actual_packages) - set(expected_packages))
        mismatched = sorted(
            name
            for name in set(expected_packages) & set(actual_packages)
            if expected_packages[name] != actual_packages[name]
        )
        raise WorkerError(
            "target runtime package profile mismatch "
            f"(missing={missing}, unexpected={unexpected}, mismatched={mismatched})"
        )
    for forbidden_distribution in ("fastapi", "starlette"):
        try:
            importlib.metadata.distribution(forbidden_distribution)
        except importlib.metadata.PackageNotFoundError:
            continue
        raise WorkerError(f"target environment must not install upstream {forbidden_distribution}")

    python_identity = {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
    }
    if python_identity != python_profile:
        raise WorkerError(
            f"target Python identity differs from the selected profile: {python_identity}"
        )

    fastapi_rs_distribution = _distribution("fastapi-rs")
    starlette_rs_distribution = _distribution("starlette-rs-py")
    _assert_editable_distribution(fastapi_rs_distribution, target_source, "FastAPI-RS")
    _assert_editable_distribution(starlette_rs_distribution, starlette_rs_source, "Starlette-RS")

    try:
        starlette = importlib.import_module("starlette")
        starlette_rs_py = importlib.import_module("starlette_rs_py")
        starlette_native = importlib.import_module("starlette_rs_py._core")
    except ImportError as exc:
        raise WorkerError(f"cannot import the selected Starlette-RS implementation: {exc}") from exc
    _assert_module_source(
        starlette,
        starlette_rs_source / STARLETTE_PACKAGE_RELATIVE_PATH,
        "Starlette-RS public `starlette`",
    )
    _assert_module_source(
        starlette_rs_py,
        starlette_rs_source / STARLETTE_BINDING_RELATIVE_PATH,
        "Starlette-RS private binding",
    )
    starlette_native_path = _extension_path(starlette_native, "Starlette-RS")

    try:
        fastapi = importlib.import_module("fastapi")
    except ImportError as exc:
        raise WorkerError(
            "FastAPI-RS has no importable public `fastapi` package in the selected target"
        ) from exc
    _assert_module_source(fastapi, TARGET_PACKAGE_ROOT, "FastAPI-RS public `fastapi`")
    required_public_exports = {
        "FastAPI": True,
        "Depends": True,
        "Header": True,
        "Query": True,
        "status": False,
    }
    for name, requires_callable in required_public_exports.items():
        export = getattr(fastapi, name, None)
        if export is None or (requires_callable and not callable(export)):
            raise WorkerError(f"FastAPI-RS public `fastapi` facade is missing {name}")

    try:
        fastapi_rs = importlib.import_module("fastapi_rs")
        fastapi_native = importlib.import_module("fastapi_rs._core")
    except ImportError as exc:
        raise WorkerError(f"cannot import the FastAPI-RS compiled extension: {exc}") from exc
    fastapi_native_path = _extension_path(fastapi_native, "FastAPI-RS")
    native_identity = getattr(fastapi_native, "identity", None)
    if not callable(native_identity):
        raise WorkerError("FastAPI-RS compiled extension does not expose its identity function")
    reported_identity = native_identity()
    fault_injection_compiled = (
        reported_identity.get("fault_injection_compiled")
        if isinstance(reported_identity, dict)
        else None
    )
    if reported_identity != {
        "target": "fastapi-rs",
        "version": str(distribution_profile["version"]),
        "binding": "pyo3",
        "fault_injection_compiled": fault_injection_compiled,
    }:
        raise WorkerError(f"FastAPI-RS compiled extension identity mismatch: {reported_identity}")
    if type(fault_injection_compiled) is not bool:
        raise WorkerError("FastAPI-RS extension did not report its fault-injection build identity")
    if fault_injection_required is None and fault_injection_compiled:
        raise WorkerError("fault-injection extension is forbidden for this target workflow")
    if (
        fault_injection_required is not None
        and fault_injection_compiled != fault_injection_required
    ):
        raise WorkerError(
            "fault-injection extension identity does not match the workflow lane: "
            f"required={fault_injection_required}, compiled={fault_injection_compiled}"
        )
    if fault_injection_compiled and not _is_under(
        Path(sys.prefix), ROOT / "target/fault-injection"
    ):
        raise WorkerError("fault-injection target must run from its isolated fault venv")
    binding_root = FAULT_BINDING_ROOT if fault_injection_compiled else TARGET_BINDING_ROOT
    _assert_module_source(fastapi_rs, binding_root, "FastAPI-RS private binding")

    fastapi_rs_revision = _git_commit(target_source, "FastAPI-RS")
    source_tree_sha256 = _combine_digests(
        {
            "fastapi-rs": _source_tree_sha256(target_source, "FastAPI-RS"),
            "starlette-rs": _source_tree_sha256(starlette_rs_source, "Starlette-RS"),
        }
    )
    target_binary_sha256 = _combine_digests(
        {
            "fastapi_rs._core": _sha256_file(fastapi_native_path),
            "starlette_rs_py._core": _sha256_file(starlette_native_path),
        }
    )
    identity = {
        "distribution": "fastapi-rs",
        "version": str(distribution_profile["version"]),
        "python": python_identity,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "repositories": {
            "fastapi_source": None,
            "starlette_source": None,
            "fastapi_rs": fastapi_rs_revision,
            "starlette_rs": starlette_rs_revision,
        },
        "target_revision": fastapi_rs_revision,
        "source_tree_sha256": source_tree_sha256,
        "target_binary_sha256": target_binary_sha256,
        "packages": actual_packages,
    }
    if fault_injection_required is not None:
        identity["fault_injection_compiled"] = fault_injection_compiled
    return identity


async def _run_cases_v7_target(
    workflow: dict[str, Any],
    factory: Any,
    warning_package_roots: list[tuple[str, Path]],
    native: Any,
) -> list[dict[str, Any]]:
    results = []
    for case in workflow["cases"]:
        mode = verification_mode(case)
        if mode == "fault-contract":
            arm = getattr(native, "arm_fault_injection", None)
            clear = getattr(native, "clear_fault_injection", None)
            if not callable(arm) or not callable(clear):
                raise WorkerError("fault-injection extension is missing its private controls")
            arm(case["fault"]["point"])
            try:
                result = await _run_case_v3(case, factory, warning_package_roots)
            finally:
                clear()
        else:
            result = await _run_case_v3(case, factory, warning_package_roots)
        result["verification"] = mode
        results.append(result)
    return results


def run_target(
    input_path: Path,
    target_source: Path,
    starlette_rs_source: Path,
    *,
    target_profile: dict[str, Any],
    input_sha256: str,
    workload_sha256: str,
    manifest_sha256: str,
) -> dict[str, Any]:
    if Path.cwd().resolve() != ROOT:
        raise WorkerError(f"target worker must run from the repository root: {ROOT}")
    workflow_path = input_path if input_path.is_absolute() else ROOT / input_path
    workflow_path = workflow_path.resolve()
    if not _is_under(workflow_path, ROOT):
        raise WorkerError("workflow inputs must live inside the repository")
    if not workflow_path.is_file():
        raise WorkerError(f"workflow input does not exist: {workflow_path}")
    if _sha256_file(workflow_path) != input_sha256:
        raise WorkerError("workflow input digest changed after host-side validation")
    workflow = _read_workflow(workflow_path)
    if workflow["schema"] not in {
        WORKFLOW_SCHEMA_ID,
        WORKFLOW_SCHEMA_V3_ID,
        WORKFLOW_SCHEMA_V4_ID,
        WORKFLOW_SCHEMA_V5_ID,
        WORKFLOW_SCHEMA_V6_ID,
        WORKFLOW_SCHEMA_V7_ID,
    }:
        raise WorkerError("target worker accepts only Python/ASGI v2 through v7 workflows")
    workload_relative_path = workflow["workload"]["file"]
    if not isinstance(workload_relative_path, str):
        raise WorkerError("workflow workload file reference is malformed")
    resolved_workload = _validate_workload_path(ROOT / workload_relative_path)
    if not resolved_workload.is_file():
        raise WorkerError(f"workflow workload does not exist: {resolved_workload}")
    if _sha256_file(resolved_workload) != workload_sha256:
        raise WorkerError("workload digest changed after host-side validation")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    if _sha256_file(manifest_path) != manifest_sha256:
        raise WorkerError("manifest digest changed after host-side validation")

    started = datetime.now(UTC)
    has_fault_contracts = workflow["schema"] == WORKFLOW_SCHEMA_V7_ID and any(
        verification_mode(case) == "fault-contract" for case in workflow["cases"]
    )
    identity = _target_identity(
        target_source,
        starlette_rs_source,
        target_profile=target_profile,
        fault_injection_required=(
            has_fault_contracts if workflow["schema"] == WORKFLOW_SCHEMA_V7_ID else None
        ),
    )
    factory = _load_workload(resolved_workload, input_sha256, workflow["workload"]["factory"])
    if workflow["schema"] in {
        WORKFLOW_SCHEMA_V3_ID,
        WORKFLOW_SCHEMA_V4_ID,
        WORKFLOW_SCHEMA_V5_ID,
        WORKFLOW_SCHEMA_V6_ID,
        WORKFLOW_SCHEMA_V7_ID,
    }:
        warning_package_roots = (
            [
                ("fastapi", TARGET_PACKAGE_ROOT),
                ("starlette", starlette_rs_source / STARLETTE_PACKAGE_RELATIVE_PATH),
            ]
            if workflow["schema"]
            in {
                WORKFLOW_SCHEMA_V4_ID,
                WORKFLOW_SCHEMA_V5_ID,
                WORKFLOW_SCHEMA_V6_ID,
                WORKFLOW_SCHEMA_V7_ID,
            }
            else []
        )
        if workflow["schema"] == WORKFLOW_SCHEMA_V7_ID:
            native = importlib.import_module("fastapi_rs._core")
            cases = asyncio.run(
                _run_cases_v7_target(workflow, factory, warning_package_roots, native)
            )
        else:
            cases = asyncio.run(_run_cases_v3(workflow, factory, warning_package_roots))
        result_schema_id = (
            RESULT_SCHEMA_V7_ID
            if workflow["schema"] == WORKFLOW_SCHEMA_V7_ID
            else RESULT_SCHEMA_V6_ID
            if workflow["schema"] == WORKFLOW_SCHEMA_V6_ID
            else RESULT_SCHEMA_V5_ID
            if workflow["schema"] == WORKFLOW_SCHEMA_V5_ID
            else RESULT_SCHEMA_V4_ID
            if workflow["schema"] == WORKFLOW_SCHEMA_V4_ID
            else RESULT_SCHEMA_V3_ID
        )
    else:
        cases = asyncio.run(_run_cases(workflow, factory))
        result_schema_id = RESULT_SCHEMA_ID
    finished = datetime.now(UTC)
    if _sha256_file(workflow_path) != input_sha256:
        raise WorkerError("workflow input changed during target execution")
    if _sha256_file(resolved_workload) != workload_sha256:
        raise WorkerError("workload changed during target execution")
    if _sha256_file(manifest_path) != manifest_sha256:
        raise WorkerError("manifest changed during target execution")
    result = {
        "schema": result_schema_id,
        "run_id": str(uuid.uuid4()),
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "product": "target",
        "identity": identity,
        "manifest": {
            "path": manifest_path.relative_to(ROOT).as_posix(),
            "sha256": manifest_sha256,
        },
        "input": {
            "path": workflow_path.relative_to(ROOT).as_posix(),
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "workload": {
            "path": resolved_workload.relative_to(ROOT).as_posix(),
            "sha256": workload_sha256,
            "factory": workflow["workload"]["factory"],
        },
        "command": {
            "argv": [sys.executable, "-m", "scripts.parity.target_worker", *sys.argv[1:]],
            "cwd": ".",
        },
        "status": "completed",
        "cases": cases,
        "infrastructure_errors": [],
    }
    expected_case_ids = [case["case_id"] for case in workflow["cases"]]
    actual_case_ids = [case["case_id"] for case in cases]
    if actual_case_ids != expected_case_ids:
        raise WorkerError("target worker case result order or cardinality differs from input")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--target-source", required=True, type=Path)
    parser.add_argument("--starlette-rs-source", required=True, type=Path)
    parser.add_argument("--target-profile", required=True)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--workload-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    try:
        target_profile = json.loads(args.target_profile)
        if not isinstance(target_profile, dict):
            raise WorkerError("target profile must be a JSON object")
        result = run_target(
            args.input,
            args.target_source,
            args.starlette_rs_source,
            target_profile=target_profile,
            input_sha256=args.input_sha256,
            workload_sha256=args.workload_sha256,
            manifest_sha256=args.manifest_sha256,
        )
    except Exception as exc:
        print(json.dumps({"worker_error": type(exc).__name__, "message": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
