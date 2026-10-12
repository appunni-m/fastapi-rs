"""Run input-only FastAPI CLI cases as isolated operating-system processes."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.contract import ROOT, ContractError, read_json, read_manifest, sha256_file
from scripts.parity.process_contract import (
    ORACLE_PROCESS_PROFILE_ID,
    TARGET_PROCESS_PROFILE_ID,
    _process_selectors_for_case,
    load_process_workflow,
)

PROCESS_RESULT_SCHEMA_ID = "fastapi-rs/python-process-workflow-result@1"
PROCESS_RESULT_SCHEMA_PATH = (
    ROOT / "tests/fixtures/schemas/python-process-workflow-result.schema.json"
)
PROCESS_COMPARISON_SCHEMA_PATH = (
    ROOT / "tests/fixtures/schemas/python-process-comparison.schema.json"
)
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
STANDARD_SURFACE_PATH = ROOT / "tests/fixtures/runtime-api-surface-standard.json"
SELECTOR_CATALOG_PATH = ROOT / "tests/fixtures/observation-selectors.json"
ORACLE_PYTHON_PACKAGES = {
    "annotated-doc",
    "annotated-types",
    "anyio",
    "email-validator",
    "fastapi",
    "fastapi-cli",
    "fastapi-cloud-cli",
    "fastar",
    "httpx",
    "httpx2",
    "idna",
    "jinja2",
    "pydantic",
    "pydantic-core",
    "pydantic-extra-types",
    "pydantic-settings",
    "python-multipart",
    "starlette",
    "typing-extensions",
    "typing-inspection",
    "uvicorn",
}
TARGET_SHARED_PACKAGES = {
    "annotated-doc",
    "annotated-types",
    "anyio",
    "idna",
    "pydantic",
    "pydantic-core",
    "typing-extensions",
    "typing-inspection",
}


class ProcessError(ContractError):
    """A process run cannot be tied to the selected pinned profile."""


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _git_revision(path: Path, label: str) -> str:
    git = shutil.which("git")
    if git is None:
        raise ProcessError("git is required to identify the selected source revision")
    completed = subprocess.run(
        [git, "-C", str(path.resolve()), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        timeout=10,
        env={},
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProcessError(f"cannot identify {label} source revision: {detail}")
    try:
        revision = completed.stdout.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise ProcessError(f"{label} source revision is not ASCII") from exc
    if len(revision) != 40 or any(char not in "0123456789abcdef" for char in revision):
        raise ProcessError(f"{label} source revision is malformed: {revision!r}")
    return revision


def _assert_clean_source(path: Path, label: str, *, allow_ds_store: bool = False) -> None:
    git = shutil.which("git")
    if git is None:
        raise ProcessError("git is required to identify the selected source revision")
    completed = subprocess.run(
        [
            git,
            "-C",
            str(path.resolve()),
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ],
        check=False,
        capture_output=True,
        timeout=10,
        env={},
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProcessError(f"cannot inspect {label} source checkout: {detail}")
    dirty: list[str] = []
    for record in completed.stdout.split(b"\0"):
        if not record:
            continue
        source_path = record[3:].decode("utf-8", errors="replace")
        if allow_ds_store and record.startswith(b"?? ") and source_path == ".DS_Store":
            continue
        dirty.append(source_path)
    if dirty:
        raise ProcessError(f"{label} source checkout is dirty: {', '.join(sorted(dirty))}")


def _profile_expectations(mode: Literal["oracle", "target"], profile_id: str) -> dict[str, Any]:
    """Resolve the expected runtime facts from the checked-in pinned profiles."""
    manifest = read_manifest()
    if mode == "oracle":
        if profile_id != ORACLE_PROCESS_PROFILE_ID:
            raise ProcessError("oracle process runner received a non-pinned profile")
        standard = read_json(STANDARD_SURFACE_PATH)
        authority = standard.get("authority", {})
        if not isinstance(authority, dict):
            raise ProcessError("standard oracle runtime identity is malformed")
        python = authority.get("python")
        fastapi = authority.get("fastapi")
        starlette = authority.get("starlette")
        optional_packages = authority.get("optional_package_versions")
        if (
            not isinstance(python, dict)
            or not isinstance(fastapi, dict)
            or not isinstance(starlette, dict)
            or not isinstance(optional_packages, dict)
        ):
            raise ProcessError("standard oracle runtime identity is incomplete")
        base_profile = manifest["oracle_profile"]
        packages = {**base_profile["packages"], **optional_packages}
        if set(packages) != ORACLE_PYTHON_PACKAGES:
            raise ProcessError("standard oracle package identity differs from the reviewed profile")
        expected = {
            "id": profile_id,
            "python": python,
            "packages": packages,
            "repositories": {
                "fastapi_source": fastapi.get("commit"),
                "starlette_source": starlette.get("commit"),
            },
        }
        if (
            fastapi.get("version") != packages.get("fastapi")
            or starlette.get("version") != packages.get("starlette")
            or expected["repositories"]["fastapi_source"] is None
            or expected["repositories"]["starlette_source"] is None
        ):
            raise ProcessError("standard oracle package and repository identities disagree")
        return expected

    if profile_id != TARGET_PROCESS_PROFILE_ID:
        raise ProcessError("target process runner received a non-pinned profile")
    target = manifest["target"]
    starlette_rs = target["starlette_rs_distribution"]
    oracle_packages = manifest["oracle_profile"]["packages"]
    expected_packages = {name: oracle_packages[name] for name in sorted(TARGET_SHARED_PACKAGES)}
    expected_packages.update(
        {
            "fastapi-rs": str(target["version"]),
            "starlette-rs-py": str(starlette_rs["version"]),
        }
    )
    return {
        "id": profile_id,
        "python": manifest["oracle_profile"]["python"],
        "packages": expected_packages,
        "repositories": {"starlette_rs": starlette_rs["commit"]},
        "target_version": str(target["version"]),
        "target": target,
        "shared_runtime_packages": {
            name: expected_packages[name] for name in sorted(TARGET_SHARED_PACKAGES)
        },
    }


_IDENTITY_PROBE = r"""
import importlib.metadata
import importlib.util
import json
import platform
import sys

names = json.loads(sys.argv[1])
packages = {}
for name in names:
    try:
        packages[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        packages[name] = None
modules = {}
for name in ("fastapi", "starlette"):
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        spec = None
    modules[name] = None if spec is None else spec.origin
print(json.dumps({
    "python": {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
    },
    "packages": packages,
    "modules": modules,
}, ensure_ascii=True, allow_nan=False, separators=(",", ":")))
"""


def _runtime_facts(python: Path, expectations: dict[str, Any]) -> dict[str, Any]:
    package_names = set(expectations["packages"])
    if "target_version" in expectations:
        package_names.update({"fastapi", "starlette"})
    package_names = sorted(package_names)
    try:
        with tempfile.TemporaryDirectory(prefix="fastapi-rs-process-identity-") as cwd:
            completed = subprocess.run(
                [
                    str(python),
                    "-I",
                    "-c",
                    _IDENTITY_PROBE,
                    json.dumps(package_names, separators=(",", ":")),
                ],
                cwd=cwd,
                env={},
                check=False,
                capture_output=True,
                timeout=15,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProcessError(f"cannot inspect selected Python runtime: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProcessError(f"selected Python runtime identity probe failed: {detail}")
    try:
        observed = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProcessError("selected Python runtime identity probe emitted invalid JSON") from exc
    if not isinstance(observed, dict):
        raise ProcessError("selected Python runtime identity probe result is malformed")

    actual_python = observed.get("python")
    if actual_python != expectations["python"]:
        raise ProcessError(
            "selected Python implementation/version differs from the pinned profile: "
            f"expected {expectations['python']}, observed {actual_python}"
        )
    actual_packages = observed.get("packages")
    if not isinstance(actual_packages, dict):
        raise ProcessError("selected Python runtime package identity is malformed")
    expected_packages = expectations["packages"]
    missing = sorted(
        name for name, version in expected_packages.items() if actual_packages.get(name) is None
    )
    mismatched = sorted(
        name
        for name, version in expected_packages.items()
        if actual_packages.get(name) is not None and actual_packages[name] != str(version)
    )
    if missing or mismatched:
        raise ProcessError(
            f"selected Python package profile mismatch (missing={missing}, mismatched={mismatched})"
        )
    if "target_version" in expectations:
        forbidden = sorted(
            name for name in ("fastapi", "starlette") if actual_packages.get(name) is not None
        )
        if forbidden:
            raise ProcessError(
                "target runtime must not install upstream distributions: " + ", ".join(forbidden)
            )
    return observed


_TARGET_IDENTITY_PROBE = r"""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
target_profile = json.loads(sys.argv[2])
target_source = Path(sys.argv[3])
starlette_source = Path(sys.argv[4])
from scripts.parity.target_worker import _target_identity

try:
    identity = _target_identity(
        target_source,
        starlette_source,
        target_profile=target_profile,
    )
except Exception as exc:
    print(json.dumps({"identity_error": type(exc).__name__, "message": str(exc)}))
    raise SystemExit(2)
print(json.dumps(identity, ensure_ascii=True, allow_nan=False, separators=(",", ":")))
"""


def _target_runtime_identity(
    python: Path,
    expectations: dict[str, Any],
    target_source: Path,
    starlette_rs_source: Path,
) -> dict[str, Any]:
    target_profile = {
        "python": expectations["python"],
        "shared_runtime_packages": expectations["shared_runtime_packages"],
        "target": expectations["target"],
    }
    try:
        with tempfile.TemporaryDirectory(prefix="fastapi-rs-target-identity-") as cwd:
            completed = subprocess.run(
                [
                    str(python),
                    "-B",
                    "-c",
                    _TARGET_IDENTITY_PROBE,
                    str(ROOT.resolve()),
                    json.dumps(target_profile, separators=(",", ":")),
                    str(target_source.resolve()),
                    str(starlette_rs_source.resolve()),
                ],
                cwd=cwd,
                env={},
                check=False,
                capture_output=True,
                timeout=45,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProcessError(f"cannot inspect selected FastAPI-RS runtime: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stdout.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProcessError(f"selected FastAPI-RS runtime identity probe failed: {detail}")
    try:
        identity = json.loads(completed.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProcessError("FastAPI-RS identity probe emitted invalid JSON") from exc
    if not isinstance(identity, dict):
        raise ProcessError("FastAPI-RS identity probe result is malformed")
    return identity


def _resolve_file_path(path: Path | None, label: str) -> Path | None:
    if path is None:
        return None
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    if not resolved.is_file():
        return None
    return resolved


def _resolve_python_path(path: Path | None) -> Path | None:
    """Keep a virtualenv interpreter symlink's directory for sibling-script lookup."""
    if path is None:
        return None
    candidate = path if path.is_absolute() else ROOT / path
    candidate = Path(os.path.abspath(candidate))
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        return None
    return candidate


def _find_entrypoint(python: Path | None, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return _resolve_file_path(explicit, "FastAPI CLI entrypoint")
    if python is None:
        return None
    suffix = ".exe" if os.name == "nt" else ""
    candidate = python.parent / f"fastapi{suffix}"
    return _resolve_file_path(candidate, "FastAPI CLI entrypoint")


def _verify_script_interpreter(entrypoint: Path, python: Path) -> None:
    """Require console scripts to bind to the explicitly selected interpreter."""
    try:
        with entrypoint.open("rb") as stream:
            first_line = stream.readline(4096).rstrip(b"\r\n")
    except OSError as exc:
        raise ProcessError(f"cannot read selected CLI entrypoint: {exc}") from exc
    if os.name == "nt" and entrypoint.suffix.lower() == ".exe":
        return
    if not first_line.startswith(b"#!"):
        raise ProcessError("selected FastAPI CLI entrypoint has no direct interpreter shebang")
    try:
        interpreter_text = first_line[2:].decode("utf-8").strip().split()[0]
    except (UnicodeDecodeError, IndexError) as exc:
        raise ProcessError("selected FastAPI CLI entrypoint has a malformed shebang") from exc
    if interpreter_text == "/usr/bin/env":
        raise ProcessError("selected CLI entrypoint uses PATH lookup and cannot be isolated safely")
    interpreter = Path(interpreter_text).resolve()
    if interpreter != python.resolve():
        raise ProcessError(
            "selected FastAPI CLI entrypoint is bound to a different Python interpreter: "
            f"{interpreter}"
        )


def _identity(
    *,
    mode: Literal["oracle", "target"],
    profile_id: str,
    expectations: dict[str, Any],
    python: Path,
    entrypoint: Path,
    runtime: dict[str, Any],
    source_root: Path | None,
    starlette_source: Path | None,
    target_source: Path | None,
    starlette_rs_source: Path | None,
) -> dict[str, Any]:
    if mode == "oracle":
        if source_root is None or starlette_source is None:
            raise ProcessError("oracle identity requires pinned FastAPI and Starlette source roots")
        _assert_clean_source(source_root, "FastAPI")
        _assert_clean_source(starlette_source, "Starlette", allow_ds_store=True)
        fastapi_revision = _git_revision(source_root, "FastAPI")
        starlette_revision = _git_revision(starlette_source, "Starlette")
        expected_repositories = expectations["repositories"]
        if fastapi_revision != expected_repositories["fastapi_source"]:
            raise ProcessError("FastAPI source revision differs from the selected oracle profile")
        if starlette_revision != expected_repositories["starlette_source"]:
            raise ProcessError("Starlette source revision differs from the selected oracle profile")
        modules = runtime.get("modules", {})
        fastapi_module = modules.get("fastapi")
        starlette_module = modules.get("starlette")
        if not isinstance(fastapi_module, str) or not _is_under(
            Path(fastapi_module), source_root / "fastapi"
        ):
            raise ProcessError("oracle Python imports FastAPI outside the pinned source checkout")
        if not isinstance(starlette_module, str) or not _is_under(
            Path(starlette_module), starlette_source / "starlette"
        ):
            raise ProcessError("oracle Python imports Starlette outside the pinned source checkout")
        repositories = {
            "fastapi_source": fastapi_revision,
            "starlette_source": starlette_revision,
        }
    else:
        if target_source is None or starlette_rs_source is None:
            raise ProcessError("target identity requires FastAPI-RS and Starlette-RS source roots")
        fastapi_rs_revision = runtime.get("target_revision")
        repositories_runtime = runtime.get("repositories")
        if not isinstance(repositories_runtime, dict):
            raise ProcessError("target runtime repository identity is missing")
        starlette_rs_revision = repositories_runtime.get("starlette_rs")
        if (
            not isinstance(fastapi_rs_revision, str)
            or re.fullmatch(r"[a-f0-9]{40}", fastapi_rs_revision) is None
        ):
            raise ProcessError("target FastAPI-RS source revision is missing")
        if starlette_rs_revision != expectations["repositories"]["starlette_rs"]:
            raise ProcessError("Starlette-RS source revision differs from the target profile")
        if runtime.get("python") != expectations["python"]:
            raise ProcessError("target runtime Python identity differs from its profile")
        if runtime.get("packages") != expectations["packages"]:
            raise ProcessError("target runtime package set differs from its profile")
        if runtime.get("version") != expectations["target_version"]:
            raise ProcessError("FastAPI-RS distribution version differs from the target profile")
        for digest_name in ("source_tree_sha256", "target_binary_sha256"):
            if (
                not isinstance(runtime.get(digest_name), str)
                or re.fullmatch(r"[a-f0-9]{64}", runtime[digest_name]) is None
            ):
                raise ProcessError(f"target runtime identity has no valid {digest_name}")
        repositories = {
            "fastapi_rs": fastapi_rs_revision,
            "starlette_rs": starlette_rs_revision,
        }

    python_resolved = python.resolve()
    entrypoint_resolved = entrypoint.resolve()
    result = {
        "profile_id": profile_id,
        "profile_sha256": _canonical_sha256(expectations),
        "python": {
            **runtime["python"],
            "path": str(python_resolved),
            "sha256": sha256_file(python_resolved),
        },
        "packages": expectations["packages"],
        "repositories": repositories,
        "entrypoint": {
            "path": str(entrypoint_resolved),
            "sha256": sha256_file(entrypoint_resolved),
        },
    }
    if mode == "target":
        result.update(
            {
                "distribution": "fastapi-rs",
                "version": runtime["version"],
                "target_revision": runtime["target_revision"],
                "source_tree_sha256": runtime["source_tree_sha256"],
                "target_binary_sha256": runtime["target_binary_sha256"],
            }
        )
    return result


def _stream_record(value: bytes) -> dict[str, Any]:
    return {
        "encoding": "base64",
        "data": base64.b64encode(value).decode("ascii"),
        "sha256": hashlib.sha256(value).hexdigest(),
        "length_bytes": len(value),
    }


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass


def _execute_case(case: dict[str, Any], entrypoint: Path) -> tuple[dict[str, Any], bool]:
    argv = [str(entrypoint), *case["argv"][1:]]
    declared_environment = case["environment"]
    environment = {name: value for name, value in declared_environment["set"].items()}
    timeout_seconds = case["timeout_seconds"]
    started = time.monotonic()
    observations: list[dict[str, Any]] = []
    try:
        with tempfile.TemporaryDirectory(
            prefix=f"fastapi-rs-{case['case_id'].rsplit('.', 1)[-1]}-"
        ) as cwd_text:
            cwd = Path(cwd_text)
            if any(cwd.iterdir()):
                raise ProcessError("isolated process working directory was not empty")
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                start_new_session=(os.name == "posix"),
            )
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                status = "completed"
            except subprocess.TimeoutExpired:
                _kill_process_tree(process)
                stdout, stderr = process.communicate()
                status = "timeout"
                selected = set(case["observations"])
                if "process.stdout" in selected:
                    observations.append(
                        {"selector": "process.stdout", "value": _stream_record(stdout)}
                    )
                if "process.stderr" in selected:
                    observations.append(
                        {"selector": "process.stderr", "value": _stream_record(stderr)}
                    )
                elapsed = max(0.0, time.monotonic() - started)
                return (
                    {
                        "case_id": case["case_id"],
                        "status": status,
                        "exit_code": None,
                        "observations": observations,
                        "command": {
                            "argv": argv,
                            "cwd": {"kind": "isolated-empty"},
                            "environment": {
                                "set": declared_environment["set"],
                                "unset": declared_environment["unset"],
                                "inherited": False,
                            },
                        },
                        "timeout_seconds": timeout_seconds,
                        "duration_seconds": elapsed,
                    },
                    False,
                )
            exit_code = process.returncode
    except OSError as exc:
        elapsed = max(0.0, time.monotonic() - started)
        return (
            {
                "case_id": case["case_id"],
                "status": "spawn_error",
                "exit_code": None,
                "observations": [],
                "command": {
                    "argv": argv,
                    "cwd": {"kind": "isolated-empty"},
                    "environment": {
                        "set": declared_environment["set"],
                        "unset": declared_environment["unset"],
                        "inherited": False,
                    },
                },
                "timeout_seconds": timeout_seconds,
                "duration_seconds": elapsed,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            },
            False,
        )

    for selector in case["observations"]:
        if selector == "process.exit_code":
            observations.append({"selector": selector, "value": exit_code})
        elif selector == "process.stdout":
            observations.append({"selector": selector, "value": _stream_record(stdout)})
        elif selector == "process.stderr":
            observations.append({"selector": selector, "value": _stream_record(stderr)})
    elapsed = max(0.0, time.monotonic() - started)
    return (
        {
            "case_id": case["case_id"],
            "status": "completed",
            "exit_code": exit_code,
            "observations": observations,
            "command": {
                "argv": argv,
                "cwd": {"kind": "isolated-empty"},
                "environment": {
                    "set": declared_environment["set"],
                    "unset": declared_environment["unset"],
                    "inherited": False,
                },
            },
            "timeout_seconds": timeout_seconds,
            "duration_seconds": elapsed,
        },
        True,
    )


def _relative_input_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise ProcessError("process workflow input must be inside the repository") from exc


def _validate_schema(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: error.message)
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise ProcessError(f"{label} does not match its schema: {detail}")


def write_process_artifact(value: dict[str, Any], output_path: Path, *, group: str) -> Path:
    """Write a new immutable process artifact below ignored parity-results/."""
    if group not in {"oracle", "target", "comparisons"}:
        raise ProcessError(f"unsupported process artifact group: {group}")
    resolved = output_path if output_path.is_absolute() else ROOT / output_path
    resolved = resolved.resolve()
    artifact_root = (ROOT / "parity-results").resolve()
    try:
        resolved.relative_to(artifact_root)
    except ValueError as exc:
        raise ProcessError("process artifacts must be written under parity-results/") from exc
    _validate_schema(
        value,
        PROCESS_COMPARISON_SCHEMA_PATH if group == "comparisons" else PROCESS_RESULT_SCHEMA_PATH,
        "process comparison" if group == "comparisons" else "process result",
    )
    resolved.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    try:
        with resolved.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
    except FileExistsError as exc:
        raise ProcessError(f"refusing to replace immutable process artifact: {resolved}") from exc
    return resolved


def run_process_workflow(
    input_path: Path,
    *,
    mode: Literal["oracle", "target"],
    profile: str,
    python: Path | None,
    executable: Path | None = None,
    source_root: Path | None = None,
    starlette_source: Path | None = None,
    target_source: Path | None = None,
    starlette_rs_source: Path | None = None,
) -> dict[str, Any]:
    """Execute every selected case in the explicitly selected oracle or target profile.

    A missing target entrypoint yields an explicit unresolved receipt.  The
    comparator rejects that receipt, so it cannot be represented as parity.
    """
    if mode not in {"oracle", "target"}:
        raise ProcessError("process mode must be exactly 'oracle' or 'target'")
    if mode == "target" and executable is not None:
        raise ProcessError(
            "target CLI entrypoint must be provided by the selected profile next to --python"
        )
    expected_profile_id = (
        ORACLE_PROCESS_PROFILE_ID if mode == "oracle" else TARGET_PROCESS_PROFILE_ID
    )
    if profile != expected_profile_id:
        raise ProcessError(f"{mode} process runner requires profile {expected_profile_id}")
    if source_root is None:
        source_root = (ROOT.parent / "fastapi").resolve()
    if starlette_source is None:
        starlette_source = (ROOT.parent / "starlette").resolve()
    if target_source is None:
        target_source = ROOT
    if starlette_rs_source is None:
        starlette_rs_source = (ROOT.parent / "starlette-rs").resolve()
    workflow, workflow_path, input_digest = load_process_workflow(
        input_path,
        source_root=source_root,
    )
    if workflow["profiles"][mode] != profile:
        raise ProcessError(f"workflow does not select the requested {mode} profile")
    expectations = _profile_expectations(mode, profile)
    manifest_digest = sha256_file(MANIFEST_PATH)
    started_at = dt.datetime.now(dt.UTC)
    resolved_python = _resolve_python_path(python)
    resolved_entrypoint = (
        None
        if resolved_python is None
        else _find_entrypoint(resolved_python, executable if mode == "oracle" else None)
    )
    relative_input = _relative_input_path(workflow_path)
    common: dict[str, Any] = {
        "schema": PROCESS_RESULT_SCHEMA_ID,
        "run_id": str(uuid.uuid4()),
        "started_at": started_at.isoformat(),
        "finished_at": dt.datetime.now(dt.UTC).isoformat(),
        "product": mode,
        "profile": {"id": profile, "status": "resolved"},
        "identity": None,
        "manifest": {"path": "tests/fixtures/manifest.yaml", "sha256": manifest_digest},
        "input": {
            "path": relative_input,
            "sha256": input_digest,
            "schema": workflow["schema"],
        },
        "command": {"mode": mode, "entrypoint": None},
        "status": "incomplete",
        "cases": [],
        "infrastructure_errors": [],
    }
    if resolved_entrypoint is None:
        reason = (
            "selected Python interpreter is unavailable"
            if resolved_python is None
            else f"selected {mode} profile has no fastapi console entrypoint"
        )
        if mode == "oracle":
            raise ProcessError(reason)
        common.update(
            {
                "finished_at": dt.datetime.now(dt.UTC).isoformat(),
                "status": "unresolved",
                "profile": {"id": profile, "status": "unresolved", "reason": reason},
                "unresolved_reason": reason,
            }
        )
        _validate_schema(common, PROCESS_RESULT_SCHEMA_PATH, "process result")
        return common
    _verify_script_interpreter(resolved_entrypoint, resolved_python)
    runtime = (
        _runtime_facts(resolved_python, expectations)
        if mode == "oracle"
        else _target_runtime_identity(
            resolved_python,
            expectations,
            target_source,
            starlette_rs_source,
        )
    )
    identity = _identity(
        mode=mode,
        profile_id=profile,
        expectations=expectations,
        python=resolved_python,
        entrypoint=resolved_entrypoint,
        runtime=runtime,
        source_root=source_root,
        starlette_source=starlette_source,
        target_source=target_source,
        starlette_rs_source=starlette_rs_source,
    )
    common["identity"] = identity
    common["command"] = {
        "mode": mode,
        "entrypoint": identity["entrypoint"],
    }

    selector_catalog = read_json(SELECTOR_CATALOG_PATH)
    selector_support = {
        row["id"]: row.get("workflow_support")
        for row in selector_catalog.get("selectors", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    all_cases_completed = True
    for case in workflow["cases"]:
        selected = _process_selectors_for_case(case, selector_support)
        selected_case = {
            **case,
            "observations": [selector for selector in case["observations"] if selector in selected],
        }
        result_case, completed = _execute_case(selected_case, resolved_entrypoint)
        common["cases"].append(result_case)
        if not completed:
            all_cases_completed = False
            common["infrastructure_errors"].append(
                {
                    "case_id": case["case_id"],
                    "kind": result_case["status"],
                    "message": result_case.get("error", {}).get(
                        "message", "process case exceeded its declared timeout"
                    ),
                }
            )
    common["finished_at"] = dt.datetime.now(dt.UTC).isoformat()
    common["status"] = "completed" if all_cases_completed else "incomplete"
    _validate_schema(common, PROCESS_RESULT_SCHEMA_PATH, "process result")
    return common


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser(
        "validate", help="validate a process workflow and its pinned source references"
    )
    validate.add_argument("--input", required=True, type=Path)
    validate.add_argument("--fastapi-source", type=Path, default=ROOT.parent / "fastapi")
    for mode in ("oracle", "target"):
        run = subparsers.add_parser(mode, help=f"run the selected {mode} process profile")
        run.add_argument("--input", required=True, type=Path)
        run.add_argument("--profile", required=True)
        default_python = (
            ROOT / ".venv-oracle-standard/bin/python"
            if mode == "oracle"
            else ROOT / ".venv-target/bin/python"
        )
        run.add_argument("--python", type=Path, default=default_python)
        if mode == "oracle":
            run.add_argument("--executable", type=Path)
        run.add_argument("--fastapi-source", type=Path, default=ROOT.parent / "fastapi")
        run.add_argument("--starlette-source", type=Path, default=ROOT.parent / "starlette")
        run.add_argument("--target-source", type=Path, default=ROOT)
        run.add_argument("--starlette-rs-source", type=Path, default=ROOT.parent / "starlette-rs")
        run.add_argument("--output", type=Path)
    compare = subparsers.add_parser("compare", help="compare two completed process results")
    compare.add_argument("--input", required=True, type=Path)
    compare.add_argument("--source-result", required=True, type=Path)
    compare.add_argument("--target-result", required=True, type=Path)
    compare.add_argument("--fastapi-source", type=Path, default=ROOT.parent / "fastapi")
    compare.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate":
            workflow, workflow_path, input_digest = load_process_workflow(
                args.input, source_root=args.fastapi_source
            )
            result = {
                "status": "valid",
                "input": workflow_path.relative_to(ROOT).as_posix(),
                "sha256": input_digest,
                "schema": workflow["schema"],
                "profiles": workflow["profiles"],
                "cases": [case["case_id"] for case in workflow["cases"]],
            }
        elif args.command in {"oracle", "target"}:
            result = run_process_workflow(
                args.input,
                mode=args.command,
                profile=args.profile,
                python=args.python,
                executable=getattr(args, "executable", None),
                source_root=args.fastapi_source,
                starlette_source=args.starlette_source,
                target_source=args.target_source,
                starlette_rs_source=args.starlette_rs_source,
            )
        else:
            from scripts.parity.process_comparator import compare_process_workflow_results

            workflow, workflow_path, input_digest = load_process_workflow(
                args.input, source_root=args.fastapi_source
            )
            source_path = args.source_result.resolve()
            target_path = args.target_result.resolve()
            source = read_json(source_path)
            target = read_json(target_path)
            result = compare_process_workflow_results(
                workflow=workflow,
                source=source,
                target=target,
                manifest_sha256=sha256_file(MANIFEST_PATH),
                input_path=_relative_input_path(workflow_path),
                input_sha256=input_digest,
                source_result_ref={
                    "path": _relative_input_path(source_path),
                    "sha256": sha256_file(source_path),
                    "run_id": source["run_id"],
                    "product": source["product"],
                },
                target_result_ref={
                    "path": _relative_input_path(target_path),
                    "sha256": sha256_file(target_path),
                    "run_id": target["run_id"],
                    "product": target["product"],
                },
                command=[
                    sys.executable,
                    "-m",
                    "scripts.parity.process_worker",
                    "compare",
                    "--input",
                    workflow_path.relative_to(ROOT).as_posix(),
                    "--source-result",
                    source_path.relative_to(ROOT).as_posix(),
                    "--target-result",
                    target_path.relative_to(ROOT).as_posix(),
                ],
            )
    except (ContractError, OSError, ValueError, KeyError) as exc:
        print(f"process parity: {exc}", file=sys.stderr)
        return 2
    if args.command != "validate" and args.output is not None:
        group = "comparisons" if args.command == "compare" else args.command
        try:
            artifact_path = write_process_artifact(result, args.output, group=group)
        except (ContractError, OSError, ValueError) as exc:
            print(f"process parity: {exc}", file=sys.stderr)
            return 2
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "product": result.get("product"),
                    "summary": result.get("summary"),
                    "artifact": artifact_path.relative_to(ROOT).as_posix(),
                },
                ensure_ascii=False,
                allow_nan=False,
                indent=2,
            )
        )
        if args.command == "compare" and result["summary"]["mismatched"]:
            return 1
        if result.get("status") == "unresolved":
            return 3
        return 0
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    if args.command == "compare" and result["summary"]["mismatched"]:
        return 1
    if result.get("status") == "unresolved":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
