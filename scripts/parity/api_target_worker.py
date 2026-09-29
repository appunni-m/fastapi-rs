"""Run direct public Python API probes in an identity-checked target process."""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import sys
import uuid
from pathlib import Path
from typing import Any

from scripts.parity import api_worker
from scripts.parity.target_worker import (
    TARGET_PACKAGE_ROOT,
    _read_workflow,
    _target_identity,
)
from scripts.parity.worker import (
    PINNED_SOURCE_COMMITS,
    ROOT,
    WorkerError,
    _assert_clean_source_tree,
    _git_commit,
    _is_under,
    _load_workload,
    _sha256_file,
    _validate_workload_path,
)

WORKFLOW_SCHEMA_ID = api_worker.WORKFLOW_SCHEMA_ID
RESULT_SCHEMA_ID = "fastapi-rs/python-api-workflow-result@2"
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
TARGET_IMPORT_ROOT = TARGET_PACKAGE_ROOT.parent


def _validate_fastapi_source(fastapi_source: Path) -> Path:
    """Verify source evidence against the exact, clean FastAPI oracle checkout."""
    fastapi_source = fastapi_source.resolve()
    if not fastapi_source.is_dir():
        raise WorkerError(f"pinned FastAPI source checkout does not exist: {fastapi_source}")
    _assert_clean_source_tree(fastapi_source, "FastAPI")
    revision = _git_commit(fastapi_source, "FastAPI")
    expected_revision = PINNED_SOURCE_COMMITS["fastapi"]
    if revision != expected_revision:
        raise WorkerError(
            f"FastAPI source commit mismatch: expected {expected_revision}, got {revision}"
        )
    return fastapi_source


def _verify_case_probe_order(workflow: dict[str, Any], cases: list[dict[str, Any]]) -> None:
    expected_cases = [case["case_id"] for case in workflow["cases"]]
    actual_cases = [case["case_id"] for case in cases]
    if actual_cases != expected_cases:
        raise WorkerError("target API case result order or cardinality differs from input")
    for specification, result_case in zip(workflow["cases"], cases, strict=True):
        expected_probes = [probe["probe_id"] for probe in specification["probes"]]
        actual_probes = [probe["probe_id"] for probe in result_case["probes"]]
        if actual_probes != expected_probes:
            raise WorkerError(
                f"target API probe result order or cardinality differs: {result_case['case_id']}"
            )


def run_target(
    input_path: Path,
    fastapi_source: Path,
    target_source: Path,
    starlette_rs_source: Path,
    *,
    target_profile: dict[str, Any],
    input_sha256: str,
    workload_sha256: str,
    manifest_sha256: str,
) -> dict[str, Any]:
    """Execute the indexed direct-API workflow using only the installed target facade."""
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
    if workflow.get("schema") != WORKFLOW_SCHEMA_ID:
        raise WorkerError(f"target API worker accepts only {WORKFLOW_SCHEMA_ID} workflows")

    workload_reference = workflow.get("workload")
    if not isinstance(workload_reference, dict) or not isinstance(
        workload_reference.get("file"), str
    ):
        raise WorkerError("direct API workload reference is malformed")
    factory_name = workload_reference.get("factory")
    if not isinstance(factory_name, str):
        raise WorkerError("direct API workload factory reference is malformed")
    workload_path = _validate_workload_path(ROOT / workload_reference["file"])
    if not workload_path.is_file():
        raise WorkerError(f"workflow workload does not exist: {workload_path}")
    if _sha256_file(workload_path) != workload_sha256:
        raise WorkerError("workload digest changed after host-side validation")
    if _sha256_file(MANIFEST_PATH) != manifest_sha256:
        raise WorkerError("manifest digest changed after host-side validation")

    fastapi_source = _validate_fastapi_source(fastapi_source)
    identity = _target_identity(
        target_source,
        starlette_rs_source,
        target_profile=target_profile,
    )

    supported_symbols = api_worker._trusted_supported_symbols(manifest_sha256)
    api_worker._validate_workflow_callables(workflow, supported_symbols)
    api_worker._validate_indexed_workflow(
        manifest_sha256,
        workflow,
        workflow_path,
        input_sha256,
        workload_sha256,
        fastapi_source,
    )

    started = dt.datetime.now(dt.UTC)
    factory = _load_workload(workload_path, input_sha256, factory_name)
    # The worker's source allowlist remains anchored to FastAPI, while callable
    # imports are constrained to the target's public `fastapi` package root.
    cases = asyncio.run(
        api_worker._run_cases(workflow, factory, TARGET_IMPORT_ROOT, supported_symbols)
    )
    api_worker._validate_result_consistency(cases)
    _verify_case_probe_order(workflow, cases)

    if _sha256_file(workflow_path) != input_sha256:
        raise WorkerError("workflow input changed during target execution")
    if _sha256_file(workload_path) != workload_sha256:
        raise WorkerError("workload changed during target execution")
    if _sha256_file(MANIFEST_PATH) != manifest_sha256:
        raise WorkerError("manifest changed during target execution")

    finished = dt.datetime.now(dt.UTC)
    return {
        "schema": RESULT_SCHEMA_ID,
        "run_id": str(uuid.uuid4()),
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "product": "target",
        "identity": identity,
        "manifest": {
            "path": MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "sha256": manifest_sha256,
        },
        "input": {
            "path": workflow_path.relative_to(ROOT).as_posix(),
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "workload": {
            "path": workload_path.relative_to(ROOT).as_posix(),
            "sha256": workload_sha256,
            "factory": factory_name,
        },
        "command": {
            "argv": [sys.executable, "-m", "scripts.parity.api_target_worker", *sys.argv[1:]],
            "cwd": ".",
        },
        "status": "completed",
        "cases": cases,
        "infrastructure_errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--fastapi-source", required=True, type=Path)
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
            args.fastapi_source,
            args.target_source,
            args.starlette_rs_source,
            target_profile=target_profile,
            input_sha256=args.input_sha256,
            workload_sha256=args.workload_sha256,
            manifest_sha256=args.manifest_sha256,
        )
    except Exception as exc:
        print(
            json.dumps(
                {"worker_error": type(exc).__name__, "message": str(exc)},
                ensure_ascii=False,
                allow_nan=False,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
