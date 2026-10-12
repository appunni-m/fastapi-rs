"""Strict loading and pinned-identity checks for subprocess parity workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from scripts.parity.contract import (
    PROCESS_WORKFLOW_SCHEMA,
    PROCESS_WORKFLOW_SCHEMA_ID,
    ROOT,
    ContractError,
    _validate_unique_ids,
    read_json,
    sha256_file,
)

ORACLE_PROCESS_PROFILE_ID = "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-standard"
TARGET_PROCESS_PROFILE_ID = "fastapi-rs-python-consumer"


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _process_selectors_for_case(case: dict[str, Any], selector_support: dict[str, str]) -> set[str]:
    """Return only requested process selectors currently implemented by the lane."""
    requested = set(case.get("observations", []))
    unknown = requested - selector_support.keys()
    if unknown:
        raise ContractError(
            "process case references unknown observation selectors: " + ", ".join(sorted(unknown))
        )
    return {
        selector
        for selector in requested
        if selector_support.get(selector) in {"supported", "partial"}
    }


def _verify_source_evidence(case: dict[str, Any], source_root: Path) -> None:
    seen: set[str] = set()
    root = source_root.resolve()
    for evidence in case["source_evidence"]:
        relative = evidence["path"]
        if relative in seen:
            raise ContractError(
                f"process case {case['case_id']} repeats source evidence: {relative}"
            )
        seen.add(relative)
        path = (root / relative).resolve()
        if not _is_under(path, root):
            raise ContractError(
                f"process source evidence resolves outside the pinned source tree: {relative}"
            )
        if not path.is_file():
            raise ContractError(f"process source evidence does not exist: {relative}")
        if sha256_file(path) != evidence["sha256"]:
            raise ContractError(f"process source evidence digest is stale: {relative}")


def _verify_profiles(workflow: dict[str, Any]) -> None:
    profiles = workflow["profiles"]
    if profiles != {
        "oracle": ORACLE_PROCESS_PROFILE_ID,
        "target": TARGET_PROCESS_PROFILE_ID,
    }:
        raise ContractError("process workflow profiles differ from the pinned profile identities")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read process profile authority: {exc}") from exc
    artifacts = manifest.get("source_artifacts", {}) if isinstance(manifest, dict) else {}
    if not isinstance(artifacts, dict):
        raise ContractError("manifest has no source artifact identities for process profiles")
    artifact = artifacts.get("runtime_api_surface_standard")
    if not isinstance(artifact, dict):
        raise ContractError("manifest standard runtime surface reference is malformed")
    surface_path = (ROOT / artifact.get("path", "")).resolve()
    if not _is_under(surface_path, ROOT) or not surface_path.is_file():
        raise ContractError("manifest standard runtime surface path is invalid")
    if sha256_file(surface_path) != artifact.get("sha256"):
        raise ContractError("manifest standard runtime surface digest is stale")
    surface = read_json(surface_path)
    authority = surface.get("authority", {}) if isinstance(surface, dict) else {}
    expected_authority = {
        "fastapi": {"version": "0.141.1", "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"},
        "starlette": {"version": "1.6.0", "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"},
        "python": {"implementation": "CPython", "version": "3.12.13"},
    }
    optional_versions = authority.get("optional_package_versions", {})
    if authority.get("fastapi") != expected_authority["fastapi"]:
        raise ContractError("standard process profile does not identify FastAPI 0.141.1")
    if authority.get("starlette") != expected_authority["starlette"]:
        raise ContractError("standard process profile does not identify Starlette 1.6.0")
    if authority.get("python") != expected_authority["python"]:
        raise ContractError("standard process profile does not identify CPython 3.12.13")
    if optional_versions.get("fastapi-cli") != "0.0.32":
        raise ContractError("standard process profile must pin fastapi-cli 0.0.32")


def load_process_workflow(
    input_path: Path,
    *,
    source_root: Path | None = None,
) -> tuple[dict[str, Any], Path, str]:
    """Load an input-only process workflow and verify its source/profile identities."""
    workflow_path = input_path if input_path.is_absolute() else ROOT / input_path
    workflow_path = workflow_path.resolve()
    input_root = (ROOT / "tests/fixtures/inputs/parity").resolve()
    if not _is_under(workflow_path, input_root):
        raise ContractError("process workflow inputs must live under tests/fixtures/inputs/parity")
    workflow = read_json(workflow_path)
    if not isinstance(workflow, dict):
        raise ContractError("process workflow input must be a JSON object")
    if workflow.get("schema") != PROCESS_WORKFLOW_SCHEMA_ID:
        raise ContractError(f"unsupported process workflow schema: {workflow.get('schema')!r}")
    schema = read_json(PROCESS_WORKFLOW_SCHEMA)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema has multiple schema error types.
        raise ContractError(f"process workflow schema is invalid: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema).iter_errors(workflow),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ContractError(f"process workflow input does not match its schema: {details}")

    _verify_profiles(workflow)
    _validate_unique_ids(workflow["cases"], "case_id", "process workflow cases")
    if source_root is None:
        source_root = (ROOT.parent / "fastapi").resolve()
    if not source_root.is_dir():
        raise ContractError(f"pinned FastAPI source checkout does not exist: {source_root}")
    selector_catalog = read_json(ROOT / "tests/fixtures/observation-selectors.json")
    selector_support = {
        row["id"]: row.get("workflow_support")
        for row in selector_catalog.get("selectors", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    for case in workflow["cases"]:
        environment = case["environment"]
        overlap = set(environment["set"]) & set(environment["unset"])
        if overlap:
            raise ContractError(
                f"process case {case['case_id']} both sets and unsets: "
                + ", ".join(sorted(overlap))
            )
        _process_selectors_for_case(case, selector_support)
        _verify_source_evidence(case, source_root)

    return workflow, workflow_path, sha256_file(workflow_path)
