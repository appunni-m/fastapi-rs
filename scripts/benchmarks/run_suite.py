#!/usr/bin/env python3
"""Run the complete, identity-compatible direct-ASGI benchmark workload set."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.benchmarks import contract

ROOT = contract.ROOT
RESULT_ROOT = ROOT / "benchmark-results"
RUNNER = ROOT / "scripts/benchmarks/run_first_slice.py"
SUITE_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/benchmark-suite-result.schema.json"
SUITE_SCHEMA_V2_PATH = ROOT / "tests/fixtures/schemas/benchmark-suite-result-v2.schema.json"
SUITE_SCHEMA_V1_ID = "fastapi-rs/benchmark-suite-result@1"
SUITE_SCHEMA_V2_ID = "fastapi-rs/benchmark-suite-result@2"

EXPECTED_WORKLOADS_V1 = (
    (
        "async-nested-distinct-query-aliases-asgi.yaml",
        "fastapi.async-nested-distinct-query-aliases.asgi",
    ),
    ("async-nested-two-query-asgi.yaml", "fastapi.async-nested-two-query.asgi"),
    ("first-slice-chunked-asgi.yaml", "fastapi.first-slice.chunked-body-asgi"),
    ("first-slice-invalid-asgi.yaml", "fastapi.first-slice.invalid-asgi"),
    ("first-slice-valid-asgi.yaml", "fastapi.first-slice.valid-asgi"),
    ("repeated-sequence-query-asgi.yaml", "fastapi.request.repeated-sequence-query.asgi"),
)

# This versioned list is the reviewed suite denominator. Adding or removing a
# declaration requires an explicit suite schema revision.
EXPECTED_WORKLOADS = (
    *EXPECTED_WORKLOADS_V1[:-1],
    ("large-response-model-asgi.yaml", "fastapi.large-response-model.asgi"),
    EXPECTED_WORKLOADS_V1[-1],
)
SUITE_CONTRACTS = {
    SUITE_SCHEMA_V1_ID: (SUITE_SCHEMA_PATH, EXPECTED_WORKLOADS_V1),
    SUITE_SCHEMA_V2_ID: (SUITE_SCHEMA_V2_PATH, EXPECTED_WORKLOADS),
}


class SuiteError(RuntimeError):
    """A workload-set, source-identity, benchmark, or suite-consistency failure."""


class WorkloadFailureError(SuiteError):
    """A workload failed after producing a possibly useful identity record."""

    def __init__(self, message: str, identity: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.identity = identity


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(128 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(root: Path, *arguments: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if process.returncode:
        raise SuiteError(
            f"git identity lookup failed for {root}: {process.stderr.strip() or process.returncode}"
        )
    return process.stdout.strip()


def _assert_source(
    root: Path,
    expected_revision: str,
    label: str,
    *,
    clean: bool,
    ignore_ds_store: bool = False,
) -> None:
    source = root.resolve()
    if not source.is_dir():
        raise SuiteError(f"{label} source checkout does not exist: {source}")
    actual_revision = _git(source, "rev-parse", "HEAD")
    if actual_revision != expected_revision:
        raise SuiteError(
            f"{label} source revision differs from the expected revision: "
            f"expected {expected_revision}, got {actual_revision}"
        )
    if clean:
        changes = _git(source, "status", "--porcelain", "--untracked-files=all")
        if ignore_ds_store:
            changes = "\n".join(
                line for line in changes.splitlines() if not line.endswith(".DS_Store")
            )
        if changes:
            revision_policy = (
                f"clean working tree at current HEAD ({expected_revision})"
                if label == "FastAPI-RS target"
                else f"clean pinned checkout at {expected_revision}"
            )
            raise SuiteError(
                f"{label} source checkout is dirty; use a {revision_policy}:\n{changes}"
            )


def _load_expected_workloads() -> list[
    tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]
]:
    expected_ids = [workload_id for _, workload_id in EXPECTED_WORKLOADS]
    if len(expected_ids) != len(set(expected_ids)):
        raise SuiteError("reviewed benchmark suite contains duplicate workload IDs")
    declared_paths = sorted(path.name for path in contract.WORKLOAD_ROOT.glob("*.yaml"))
    expected_paths = sorted(name for name, _ in EXPECTED_WORKLOADS)
    if declared_paths != expected_paths:
        missing = sorted(set(expected_paths) - set(declared_paths))
        extra = sorted(set(declared_paths) - set(expected_paths))
        raise SuiteError(
            "reviewed benchmark suite workload set differs from declarations: "
            f"missing={missing}, extra={extra}"
        )

    loaded = []
    for filename, expected_id in EXPECTED_WORKLOADS:
        workload, workload_path, workflow, input_path, action = contract.load_workload(
            contract.WORKLOAD_ROOT / filename
        )
        if workload["id"] != expected_id:
            raise SuiteError(
                f"{filename} workload ID differs from the reviewed suite: "
                f"expected {expected_id!r}, got {workload['id']!r}"
            )
        loaded.append((workload, workload_path, workflow, input_path, action))
    return loaded


def _preflight(
    *,
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
    loaded: list[tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]],
) -> list[tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]]:
    manifest = contract.read_manifest()
    oracle = manifest["oracle_profile"]
    target = manifest["target"]
    _assert_source(
        fastapi_source,
        oracle["source_commits"]["fastapi"],
        "FastAPI oracle",
        clean=True,
        ignore_ds_store=True,
    )
    _assert_source(
        starlette_source,
        oracle["source_commits"]["starlette"],
        "Starlette oracle",
        clean=True,
        ignore_ds_store=True,
    )
    _assert_source(
        starlette_rs_source,
        target["starlette_rs_distribution"]["commit"],
        "Starlette-RS",
        clean=True,
    )
    _assert_source(ROOT, _git(ROOT, "rev-parse", "HEAD"), "FastAPI-RS target", clean=True)
    return loaded


def _result_path(value: str) -> Path:
    path = Path(value)
    artifact = (path if path.is_absolute() else ROOT / path).resolve()
    try:
        artifact.relative_to(RESULT_ROOT.resolve())
    except ValueError as exc:
        raise SuiteError("benchmark result artifact must live under benchmark-results/") from exc
    if not artifact.is_file():
        raise SuiteError(f"benchmark result artifact is missing: {artifact}")
    return artifact


def _runner_result(
    *,
    workload_entry: tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]],
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
    oracle_python: Path,
    target_python: Path,
) -> tuple[dict[str, Any], Path]:
    workload, workload_path, _, input_path, action = workload_entry
    command = [
        sys.executable,
        str(RUNNER),
        "--workload",
        str(workload_path),
        "--fastapi-source",
        str(fastapi_source.resolve()),
        "--starlette-source",
        str(starlette_source.resolve()),
        "--starlette-rs-source",
        str(starlette_rs_source.resolve()),
        "--oracle-python",
        str(oracle_python.absolute()),
        "--target-python",
        str(target_python.absolute()),
    ]
    before = set(RESULT_ROOT.glob("*.json"))
    process = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=3600,
    )
    if process.returncode:
        raise SuiteError(
            f"benchmark {workload['id']} failed ({process.returncode}):\n"
            f"{process.stdout}{process.stderr}"
        )
    try:
        output = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise SuiteError(
            f"benchmark {workload['id']} did not return a JSON completion record: "
            f"{exc}\n{process.stdout}"
        ) from exc
    if not isinstance(output, dict) or output.get("status") != "completed":
        raise SuiteError(f"benchmark {workload['id']} did not report completion")

    artifact_value = output.get("artifact")
    if not isinstance(artifact_value, str):
        raise SuiteError(f"benchmark {workload['id']} omitted its result artifact path")
    artifact = _result_path(artifact_value)
    if artifact in before:
        raise SuiteError(f"benchmark {workload['id']} returned a pre-existing result artifact")
    result = contract.read_json(artifact)
    try:
        contract.validate_result(
            result,
            workload=workload,
            workload_path=workload_path,
            input_path=input_path,
            action=action,
        )
    except (contract.ContractError, OSError, ValueError) as exc:
        identity = None
        try:
            contract._validate_schema(result, contract.RESULT_SCHEMA_PATH, "benchmark result")
            identity = _result_identity(result)
        except (contract.ContractError, KeyError, TypeError):
            pass
        raise WorkloadFailureError(
            f"benchmark {workload['id']} result validation failed: {exc}", identity
        ) from exc
    return result, artifact


def _assert_compatible_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    first = results[0]
    common_fields = ("code", "host", "target_build")
    for field in common_fields:
        expected = first[field]
        if any(result[field] != expected for result in results[1:]):
            raise SuiteError(f"benchmark results do not share one current {field} identity")

    first_subjects = first["subjects"]
    identities = {
        "python": first_subjects["fastapi"]["python"],
        "fastapi": first_subjects["fastapi"]["identity"],
        "fastapi_rs": first_subjects["fastapi-rs"]["identity"],
        "subject_hosts": {
            "fastapi": first_subjects["fastapi"]["host"],
            "fastapi_rs": first_subjects["fastapi-rs"]["host"],
        },
    }
    first_control = first_subjects.get("starlette-control")
    if first_control is not None:
        identities["starlette_control"] = first_control["identity"]
        identities["subject_hosts"]["starlette_control"] = first_control["host"]
    for result in results[1:]:
        subjects = result["subjects"]
        if subjects["fastapi"]["python"] != identities["python"]:
            raise SuiteError("benchmark results do not share one Python identity")
        if subjects["fastapi"]["identity"] != identities["fastapi"]:
            raise SuiteError("FastAPI oracle identities differ across benchmark workloads")
        if subjects["fastapi-rs"]["identity"] != identities["fastapi_rs"]:
            raise SuiteError("FastAPI-RS target identities differ across benchmark workloads")
        for kind, identity_key in (("fastapi", "fastapi"), ("fastapi-rs", "fastapi_rs")):
            if subjects[kind]["host"] != identities["subject_hosts"][identity_key]:
                raise SuiteError(f"{kind} measurement hosts differ across benchmark workloads")
        control = subjects.get("starlette-control")
        if control is not None and control["identity"] != identities.get("starlette_control"):
            if "starlette_control" not in identities:
                identities["starlette_control"] = control["identity"]
                identities["subject_hosts"]["starlette_control"] = control["host"]
            else:
                raise SuiteError("Starlette control identities differ across workloads")
        elif (
            control is not None
            and control["host"] != identities["subject_hosts"]["starlette_control"]
        ):
            raise SuiteError("Starlette control measurement hosts differ across workloads")
    return identities


def _result_identity(result: dict[str, Any]) -> dict[str, Any]:
    subjects = result["subjects"]
    return {
        "code": result["code"],
        "host": result["host"],
        "target_build": result["target_build"],
        "python": subjects["fastapi"]["python"],
        "subjects": {
            name: {
                "identity": subject["identity"],
                "python": subject["python"],
                "host": subject["host"],
            }
            for name, subject in subjects.items()
        },
    }


def _source_revisions() -> dict[str, str]:
    manifest = contract.read_manifest()
    return {
        "fastapi_source": manifest["oracle_profile"]["source_commits"]["fastapi"],
        "starlette_source": manifest["oracle_profile"]["source_commits"]["starlette"],
        "starlette_rs_source": manifest["target"]["starlette_rs_distribution"]["commit"],
        # FastAPI-RS is identified by the clean HEAD used for this run, not a manifest pin.
        "fastapi_rs_source": _git(ROOT, "rev-parse", "HEAD"),
    }


def _pending_outcome(workload_id: str) -> dict[str, Any]:
    return {
        "id": workload_id,
        "status": "not_run",
        "artifact": None,
        "artifact_sha256": None,
        "run_id": None,
        "parity_gate": None,
        "identity": None,
        "error": None,
    }


def _completed_outcome(result: dict[str, Any], artifact: Path) -> dict[str, Any]:
    return {
        "id": result["workload"]["id"],
        "status": "completed",
        "artifact": artifact.relative_to(ROOT).as_posix(),
        "artifact_sha256": _sha256(artifact),
        "run_id": result["run_id"],
        "parity_gate": result["parity_gate"]["summary"],
        "identity": _result_identity(result),
        "error": None,
    }


def _failed_outcome(workload_id: str, error: BaseException) -> dict[str, Any]:
    message = str(error).strip() or error.__class__.__name__
    message = message[-2000:]
    outcome = _pending_outcome(workload_id)
    outcome.update(status="failed", error=message, identity=getattr(error, "identity", None))
    return outcome


def _check_suite_document(
    suite: dict[str, Any],
    loaded_by_id: dict[str, tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]],
) -> None:
    try:
        schema_path, expected_workloads = SUITE_CONTRACTS[suite["schema"]]
    except KeyError as exc:
        raise SuiteError(f"unsupported benchmark suite schema: {suite.get('schema')!r}") from exc
    contract._validate_schema(suite, schema_path, "benchmark suite result")
    expected_ids = [workload_id for _, workload_id in expected_workloads]
    if suite["required_workloads"] != expected_ids:
        raise SuiteError("suite result denominator differs from the reviewed workload set")
    outcomes = suite["workloads"]
    if [outcome["id"] for outcome in outcomes] != expected_ids:
        raise SuiteError("suite result outcomes do not match the exact reviewed workload order")

    results = []
    for outcome in outcomes:
        if outcome["status"] != "completed":
            continue
        artifact = _result_path(outcome["artifact"])
        if _sha256(artifact) != outcome["artifact_sha256"]:
            raise SuiteError(f"suite result digest differs for {outcome['id']}")
        result = contract.read_json(artifact)
        contract._validate_schema(
            result, contract.RESULT_SCHEMA_PATH, "referenced benchmark result"
        )
        if result["run_id"] != outcome["run_id"]:
            raise SuiteError(f"suite result run ID differs for {outcome['id']}")
        if result["workload"]["id"] != outcome["id"]:
            raise SuiteError(f"suite result workload ID differs for {outcome['id']}")
        if result["parity_gate"]["summary"] != outcome["parity_gate"]:
            raise SuiteError(f"suite result parity summary differs for {outcome['id']}")
        if _result_identity(result) != outcome["identity"]:
            raise SuiteError(f"suite result identity differs for {outcome['id']}")
        if suite["status"] == "completed" and result["code"] != suite["source_revisions"]:
            raise SuiteError(f"suite result source revisions differ for {outcome['id']}")
        try:
            workload, workload_path, _, input_path, action = loaded_by_id[outcome["id"]]
        except KeyError as exc:
            raise SuiteError(f"suite result names an undeclared workload: {outcome['id']}") from exc
        contract.validate_result(
            result,
            workload=workload,
            workload_path=workload_path,
            input_path=input_path,
            action=action,
        )
        results.append(result)

    failure = suite["failure"]
    if suite["status"] == "completed":
        if len(results) != len(expected_ids):
            raise SuiteError(
                f"completed suite does not reference {len(expected_ids)} completed workloads"
            )
        identities = _assert_compatible_results(results)
        if suite["identity"] != identities:
            raise SuiteError("completed suite identity differs from its workload results")
        return

    if suite["identity"] is not None or failure is None:
        raise SuiteError("incomplete suite must retain its failure and omit common identity")
    statuses = [outcome["status"] for outcome in outcomes]
    if failure["stage"] == "preflight" and any(status != "not_run" for status in statuses):
        raise SuiteError("preflight failure cannot include attempted workload results")
    if failure["stage"] == "workload":
        failed = [outcome for outcome in outcomes if outcome["status"] == "failed"]
        if len(failed) != 1 or failed[0]["id"] != failure["workload_id"]:
            raise SuiteError("workload failure does not identify its failed workload outcome")
        failed_index = outcomes.index(failed[0])
        if any(outcome["status"] != "completed" for outcome in outcomes[:failed_index]):
            raise SuiteError("workload outcomes before the failure must be completed")
        if any(outcome["status"] != "not_run" for outcome in outcomes[failed_index + 1 :]):
            raise SuiteError("workload outcomes after the failure must be not_run")
    if failure["stage"] == "aggregation" and len(results) != len(expected_ids):
        raise SuiteError(
            f"aggregation failure must retain all {len(expected_ids)} completed workloads"
        )


def _validate_saved_suite_artifacts(
    loaded: list[tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]],
) -> int:
    if not RESULT_ROOT.exists():
        return 0
    loaded_by_id = {entry[0]["id"]: entry for entry in loaded}
    paths = sorted(RESULT_ROOT.glob("suite-*.json"))
    for path in paths:
        try:
            path.resolve().relative_to(RESULT_ROOT.resolve())
        except ValueError as exc:
            raise SuiteError(f"suite artifact escapes benchmark-results/: {path}") from exc
        _check_suite_document(contract.read_json(path), loaded_by_id)
    return len(paths)


def _write_suite_artifact(
    suite: dict[str, Any],
    loaded: list[tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]],
) -> Path:
    _check_suite_document(suite, {entry[0]["id"]: entry for entry in loaded})
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = suite["run_id"]
    suite_path = RESULT_ROOT / f"suite-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{run_id}.json"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=RESULT_ROOT,
            prefix=".suite-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(suite, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary_path, suite_path)
    except BaseException:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return suite_path


def _suite_document(
    *,
    status: str,
    source_revisions: dict[str, str],
    outcomes: list[dict[str, Any]],
    identity: dict[str, Any] | None,
    failure: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema": SUITE_SCHEMA_V2_ID,
        "run_id": str(uuid.uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "status": status,
        "required_workloads": [workload_id for _, workload_id in EXPECTED_WORKLOADS],
        "source_revisions": source_revisions,
        "identity": identity,
        "failure": failure,
        "workloads": outcomes,
    }


def _failure_record(stage: str, workload_id: str | None, error: BaseException) -> dict[str, Any]:
    message = str(error).strip() or error.__class__.__name__
    return {"stage": stage, "workload_id": workload_id, "message": message[-2000:]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastapi-source", type=Path, default=ROOT / "../fastapi")
    parser.add_argument("--starlette-source", type=Path, default=ROOT / "../starlette")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT / "../starlette-rs")
    parser.add_argument("--oracle-python", type=Path, default=ROOT / ".venv-oracle/bin/python")
    parser.add_argument("--target-python", type=Path, default=ROOT / ".venv-target/bin/python")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="check the exact reviewed workload set")
    mode.add_argument(
        "--preflight-only",
        action="store_true",
        help="validate the exact workload set, pinned oracles, and clean target checkout",
    )
    args = parser.parse_args()

    try:
        if args.check:
            loaded = _load_expected_workloads()
            contract._check_schema(SUITE_SCHEMA_PATH, "benchmark suite v1 result")
            contract._check_schema(SUITE_SCHEMA_V2_PATH, "benchmark suite v2 result")
            artifact_count = _validate_saved_suite_artifacts(loaded)
            print(
                f"benchmark suite contract valid: {len(loaded)} required workloads, "
                f"{artifact_count} suite artifacts and result references"
            )
            return 0

        source_revisions = _source_revisions()
        workload_ids = [workload_id for _, workload_id in EXPECTED_WORKLOADS]
        outcomes = [_pending_outcome(workload_id) for workload_id in workload_ids]
        try:
            loaded = _load_expected_workloads()
        except (SuiteError, contract.ContractError, OSError, ValueError) as exc:
            failure = _failure_record("preflight", None, exc)
            suite_artifact = _write_suite_artifact(
                _suite_document(
                    status="incomplete",
                    source_revisions=source_revisions,
                    outcomes=outcomes,
                    identity=None,
                    failure=failure,
                ),
                loaded=[],
            )
            print(
                f"benchmark suite failed: {exc}\nsuite artifact: {suite_artifact}",
                file=sys.stderr,
            )
            return 1
        try:
            _preflight(
                fastapi_source=args.fastapi_source,
                starlette_source=args.starlette_source,
                starlette_rs_source=args.starlette_rs_source,
                loaded=loaded,
            )
        except (
            SuiteError,
            contract.ContractError,
            OSError,
            ValueError,
            subprocess.TimeoutExpired,
        ) as exc:
            failure = _failure_record("preflight", None, exc)
            suite_artifact = _write_suite_artifact(
                _suite_document(
                    status="incomplete",
                    source_revisions=source_revisions,
                    outcomes=outcomes,
                    identity=None,
                    failure=failure,
                ),
                loaded=loaded,
            )
            print(
                f"benchmark suite failed: {exc}\nsuite artifact: {suite_artifact}", file=sys.stderr
            )
            return 1
        if args.preflight_only:
            print(
                f"benchmark suite preflight valid: {len(loaded)} workloads "
                "and clean source checkouts"
            )
            return 0

        results = []
        failed_workload: str | None = None
        workload_error: BaseException | None = None
        for index, entry in enumerate(loaded):
            workload_id = entry[0]["id"]
            try:
                result, artifact = _runner_result(
                    workload_entry=entry,
                    fastapi_source=args.fastapi_source,
                    starlette_source=args.starlette_source,
                    starlette_rs_source=args.starlette_rs_source,
                    oracle_python=args.oracle_python,
                    target_python=args.target_python,
                )
            except (
                SuiteError,
                contract.ContractError,
                OSError,
                ValueError,
                subprocess.TimeoutExpired,
            ) as exc:
                outcomes[index] = _failed_outcome(workload_id, exc)
                failed_workload = workload_id
                workload_error = exc
                break
            results.append(result)
            outcomes[index] = _completed_outcome(result, artifact)

        if workload_error is not None:
            failure = _failure_record("workload", failed_workload, workload_error)
            suite_artifact = _write_suite_artifact(
                _suite_document(
                    status="incomplete",
                    source_revisions=source_revisions,
                    outcomes=outcomes,
                    identity=None,
                    failure=failure,
                ),
                loaded=loaded,
            )
            print(
                f"benchmark suite failed: {workload_error}\nsuite artifact: {suite_artifact}",
                file=sys.stderr,
            )
            return 1

        try:
            identities = _assert_compatible_results(results)
        except SuiteError as exc:
            failure = _failure_record("aggregation", None, exc)
            suite_artifact = _write_suite_artifact(
                _suite_document(
                    status="incomplete",
                    source_revisions=source_revisions,
                    outcomes=outcomes,
                    identity=None,
                    failure=failure,
                ),
                loaded=loaded,
            )
            print(
                f"benchmark suite failed: {exc}\nsuite artifact: {suite_artifact}", file=sys.stderr
            )
            return 1

        suite_artifact = _write_suite_artifact(
            _suite_document(
                status="completed",
                source_revisions=source_revisions,
                outcomes=outcomes,
                identity=identities,
                failure=None,
            ),
            loaded=loaded,
        )
    except (
        SuiteError,
        contract.ContractError,
        OSError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"benchmark suite failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "completed",
                "workloads": len(results),
                "artifact": suite_artifact.relative_to(ROOT).as_posix(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
