"""Strict workload and result contracts for direct-ASGI benchmarks."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.contract import (
    ROOT,
    WORKFLOW_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID,
    ContractError,
    _UniqueKeyLoader,
    load_workflow,
    read_json,
    read_manifest,
    sha256_file,
)

WORKLOAD_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/benchmark-workload.schema.json"
RESULT_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/benchmark-result.schema.json"
WORKLOAD_SCHEMA_ID = "fastapi-rs/benchmark-workload@1"
RESULT_SCHEMA_ID = "fastapi-rs/benchmark-result@1"
WORKLOAD_ROOT = (ROOT / "benchmarks/workloads").resolve()
PARITY_INPUT_ROOT = (ROOT / "tests/fixtures/inputs/parity").resolve()
RESULT_ROOT = (ROOT / "parity-results").resolve()

_EXPECTED_EXCLUSIONS = {
    "interpreter and module startup",
    "app construction and route registration",
    "ASGI scope and receive/send callback construction from per-request latency",
    "response signature extraction and correctness checks from per-request latency",
    "sequential loop bookkeeping from per-request latency",
    "network and HTTP client",
}
_EXPECTED_METRICS = {
    "per-request latency nanoseconds: min, median, p95, p99, max, mean",
    (
        "sequential request-loop throughput including per-call setup, response "
        "observation, correctness checks, and loop bookkeeping"
    ),
}
_EXPECTED_KINDS = {"fastapi", "fastapi-rs"}
_SUBJECT_IDS = {
    "fastapi": "fastapi-0.141.1",
    "fastapi-rs": "fastapi-rs-release",
    "starlette-control": "starlette-1.6.0-control",
}


def _fail(message: str) -> None:
    raise ContractError(f"benchmark contract: {message}")


def _validate_schema(value: Any, schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        raise ContractError(f"{label} schema is invalid: {exc}") from exc
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(value),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        _fail(f"{label} does not match its schema: {details}")


def _check_schema(schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        raise ContractError(f"{label} schema is invalid: {exc}") from exc


def _resolve_under(path_value: str, root: Path, label: str) -> Path:
    candidate = (ROOT / path_value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ContractError(f"benchmark {label} escapes {root.relative_to(ROOT)}") from exc
    if not candidate.is_file():
        _fail(f"{label} does not exist: {path_value}")
    return candidate


def load_workload(path: Path) -> tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]:
    """Load a strict benchmark declaration and its uniquely selected ASGI action."""
    workload_path = path if path.is_absolute() else ROOT / path
    workload_path = workload_path.resolve()
    try:
        workload_path.relative_to(WORKLOAD_ROOT)
    except ValueError as exc:
        raise ContractError("benchmark workload must live under benchmarks/workloads") from exc
    if not workload_path.is_file():
        _fail(f"workload does not exist: {workload_path}")
    try:
        with workload_path.open(encoding="utf-8") as stream:
            workload = yaml.load(stream, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read benchmark workload {workload_path}: {exc}") from exc
    if not isinstance(workload, dict):
        _fail(f"workload must be a YAML object: {workload_path}")
    _validate_schema(workload, WORKLOAD_SCHEMA_PATH, "workload")

    input_path = _resolve_under(workload["input"]["path"], PARITY_INPUT_ROOT, "parity input")
    workflow, _, _, _ = load_workflow(input_path)
    if workflow.get("schema") not in {WORKFLOW_SCHEMA_ID, WORKFLOW_SCHEMA_V3_ID}:
        _fail("benchmark input must be a Python/ASGI workflow")
    selected_cases = [
        case for case in workflow["cases"] if case["case_id"] == workload["input"]["case_id"]
    ]
    if len(selected_cases) != 1:
        _fail(f"input case is missing or ambiguous: {workload['input']['case_id']}")
    case = selected_cases[0]
    if workload["correctness_gate"]["parity_case_id"] != case["case_id"]:
        _fail("correctness gate case ID must match the selected benchmark input case")
    actions = [action for action in case["actions"] if action["kind"] == "http_request"]
    action_id = workload["input"].get("action_id")
    if action_id is not None:
        actions = [action for action in actions if action["action_id"] == action_id]
    if len(actions) != 1:
        _fail("benchmark input must select exactly one HTTP request action")
    action = actions[0]

    manifest = read_manifest()
    if workload["python_identity"] != manifest["oracle_profile"]["python"]:
        _fail("workload Python identity differs from the pinned oracle/target profile")
    if workload["correctness_gate"]["required_comparison"] != "all-selected-cases-pass":
        _fail("runner gates the full selected workflow and requires every case to pass")
    if not set(workload["correctness_gate"]["require_equal_untimed_observation"]) <= {
        "status",
        "headers",
        "body",
    }:
        _fail("untimed correctness selectors exceed the response signature emitted by the runner")
    selected_observations = {
        selector
        for observation in action["observations"]
        if observation["kind"] == "http_response"
        for selector in observation["selectors"]
    }
    requested_observations = set(workload["correctness_gate"]["require_equal_untimed_observation"])
    if not requested_observations <= selected_observations:
        _fail("untimed correctness selectors are not selected by the parity action")

    subject_kinds = [subject["kind"] for subject in workload["subjects"]]
    subject_ids = [subject["id"] for subject in workload["subjects"]]
    if len(subject_kinds) != len(set(subject_kinds)) or len(subject_ids) != len(set(subject_ids)):
        _fail("subject kinds and IDs must be unique")
    if not _EXPECTED_KINDS <= set(subject_kinds):
        _fail("every benchmark must include FastAPI oracle and FastAPI-RS target subjects")
    if set(subject_kinds) - (_EXPECTED_KINDS | {"starlette-control"}):
        _fail("workload selects a subject kind the runner does not execute")
    for subject in workload["subjects"]:
        if subject["id"] != _SUBJECT_IDS[subject["kind"]]:
            _fail(f"subject ID differs from the runner identity for {subject['kind']}")
        expected_environment = "target" if subject["kind"] == "fastapi-rs" else "oracle"
        if subject["environment"] != expected_environment:
            _fail(f"subject environment differs from the runner for {subject['kind']}")
    has_control = "starlette-control" in subject_kinds
    control_policy = workload["reporting"].get("starlette_control")
    if (
        has_control
        and control_policy != "contextual baseline; do not subtract from FastAPI timings"
    ):
        _fail("Starlette control must be declared as contextual and must not be subtracted")
    if not has_control and control_policy not in {
        None,
        "omitted because standalone Starlette has no FastAPI dependency injection semantics",
    }:
        _fail("Starlette control reporting is inconsistent with the selected subjects")

    timing = workload["timing"]
    if "direct asgi" not in timing["boundary"].lower():
        _fail("runner measures one direct ASGI application invocation")
    if not _EXPECTED_EXCLUSIONS <= set(timing["excludes"]):
        _fail("timing exclusions must state the runner's startup, setup, and network boundaries")
    if set(timing["metrics"]) != _EXPECTED_METRICS:
        _fail("timing metrics differ from the statistics emitted by the runner")
    if timing["raw_samples"] != "retain all per-request latency samples":
        _fail("runner retains every measured per-request latency sample")
    if timing["concurrency"] != 1:
        _fail("runner executes samples sequentially with concurrency one")

    return workload, workload_path, workflow, input_path, action


def _read_result_artifact(
    path_value: str, expected_product: str, expected_sha256: str
) -> dict[str, Any]:
    artifact_path = (ROOT / path_value).resolve()
    try:
        artifact_path.relative_to(RESULT_ROOT)
    except ValueError as exc:
        raise ContractError("benchmark parity evidence must live under parity-results") from exc
    if not artifact_path.is_file():
        _fail(f"parity evidence artifact is missing: {path_value}")
    if sha256_file(artifact_path) != expected_sha256:
        _fail(f"parity evidence digest differs from its comparison reference: {path_value}")
    result = read_json(artifact_path)
    if not isinstance(result, dict) or result.get("product") != expected_product:
        _fail(f"parity evidence is not a {expected_product} result: {path_value}")
    return result


def _validate_identity_links(result: dict[str, Any], comparison_path: Path) -> None:
    comparison = read_json(comparison_path)
    if comparison.get("status") != result["parity_gate"]["status"]:
        _fail("benchmark parity-gate status differs from its comparison artifact")
    if comparison.get("summary") != result["parity_gate"]["summary"]:
        _fail("benchmark parity-gate summary differs from its comparison artifact")
    input_identity = result["workload"]
    if (
        comparison.get("input", {}).get("path") != input_identity["input_path"]
        or comparison.get("input", {}).get("sha256") != input_identity["input_sha256"]
    ):
        _fail("parity comparison input differs from the benchmark workload input")
    input_document = read_json(ROOT / input_identity["input_path"])
    if comparison.get("input", {}).get("schema") != input_document.get("schema"):
        _fail("parity comparison uses a different input schema")
    parity_cases = comparison.get("cases", [])
    selected_case = [
        case for case in parity_cases if case.get("case_id") == input_identity["case_id"]
    ]
    if len(selected_case) != 1 or selected_case[0].get("outcome") != "pass":
        _fail("the selected benchmark case did not pass in its fresh parity comparison")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    if comparison.get("manifest", {}).get("sha256") != sha256_file(manifest_path):
        _fail("parity comparison does not reference the current manifest")
    source_ref = comparison.get("source_result", {})
    target_ref = comparison.get("target_result", {})
    source_path = source_ref.get("path")
    target_path = target_ref.get("path")
    if not isinstance(source_path, str) or not isinstance(target_path, str):
        _fail("comparison artifact must identify its source and target result artifacts")
    source = _read_result_artifact(source_path, "oracle", source_ref.get("sha256", ""))
    target = _read_result_artifact(target_path, "target", target_ref.get("sha256", ""))
    if source.get("run_id") != source_ref.get("run_id") or target.get("run_id") != target_ref.get(
        "run_id"
    ):
        _fail("comparison artifact run IDs do not match the referenced parity artifacts")
    oracle_identity = source["identity"]
    target_identity = target["identity"]
    measurements = result["subjects"]

    fastapi_identity = measurements["fastapi"]["identity"]
    if (
        fastapi_identity["fastapi"] != oracle_identity["version"]
        or fastapi_identity["fastapi_source"] != oracle_identity["repositories"]["fastapi_source"]
        or fastapi_identity["starlette"] != oracle_identity["packages"]["starlette"]
        or fastapi_identity["starlette_source"]
        != oracle_identity["repositories"]["starlette_source"]
    ):
        _fail("timed FastAPI identity differs from the live parity oracle identity")
    oracle_shared = {
        name: version
        for name, version in oracle_identity["packages"].items()
        if name not in {"fastapi", "starlette"}
    }
    if fastapi_identity["shared_packages"] != oracle_shared:
        _fail("timed FastAPI shared packages differ from the live parity oracle identity")

    target_measurement_identity = measurements["fastapi-rs"]["identity"]
    if (
        target_measurement_identity["fastapi_rs_source"]
        != target_identity["repositories"]["fastapi_rs"]
        or target_measurement_identity["fastapi_rs"] != target_identity["version"]
        or target_measurement_identity["starlette_rs_source"]
        != target_identity["repositories"]["starlette_rs"]
        or target_measurement_identity["starlette_rs"]
        != target_identity["packages"]["starlette-rs-py"]
        or target_measurement_identity["target_binary_sha256"]
        != target_identity["target_binary_sha256"]
    ):
        _fail("timed FastAPI-RS identity differs from the live parity target identity")
    target_shared = {
        name: version
        for name, version in target_identity["packages"].items()
        if name not in {"fastapi-rs", "starlette-rs-py"}
    }
    if target_measurement_identity["shared_packages"] != target_shared:
        _fail("timed FastAPI-RS shared packages differ from the live parity target identity")

    expected_code = {
        "fastapi_source": oracle_identity["repositories"]["fastapi_source"],
        "starlette_source": oracle_identity["repositories"]["starlette_source"],
        "fastapi_rs_source": target_identity["repositories"]["fastapi_rs"],
        "starlette_rs_source": target_identity["repositories"]["starlette_rs"],
    }
    if result["code"] != expected_code:
        _fail("benchmark source revisions differ from the live parity identity pair")

    if "starlette-control" in measurements:
        control_identity = measurements["starlette-control"]["identity"]
        if (
            control_identity["starlette"] != oracle_identity["packages"]["starlette"]
            or control_identity["starlette_source"]
            != oracle_identity["repositories"]["starlette_source"]
            or control_identity["shared_packages"] != oracle_shared
        ):
            _fail("timed Starlette control identity differs from the live parity oracle profile")


def validate_result(
    result: dict[str, Any],
    *,
    workload: dict[str, Any],
    workload_path: Path,
    input_path: Path,
    action: dict[str, Any],
) -> None:
    """Validate generated benchmark evidence against schema and selected inputs."""
    _validate_schema(result, RESULT_SCHEMA_PATH, "benchmark result")
    input_relative = input_path.relative_to(ROOT).as_posix()
    workload_relative = workload_path.relative_to(ROOT).as_posix()
    if result["workload"] != {
        "id": workload["id"],
        "path": workload_relative,
        "sha256": sha256_file(workload_path),
        "input_path": input_relative,
        "input_sha256": sha256_file(input_path),
        "case_id": workload["input"]["case_id"],
        "action_id": workload["input"].get("action_id"),
    }:
        _fail("result workload identity differs from the validated declaration")
    if result["parity_gate"]["summary"]["passed"] != result["parity_gate"]["summary"]["selected"]:
        _fail("benchmark parity gate did not pass every selected case")
    expected_kinds = {subject["kind"] for subject in workload["subjects"]}
    if set(result["subjects"]) != expected_kinds:
        _fail("result subject set differs from the benchmark declaration")

    timing = workload["timing"]
    expected_sample_count = timing["rounds"] * timing["samples_per_round"]
    observations: set[str] = set()
    hosts: set[str] = set()
    for kind, measurement in result["subjects"].items():
        if measurement["subject"] != kind:
            _fail(f"result subject identity differs from its map key: {kind}")
        if measurement["selected_action_id"] != action["action_id"]:
            _fail(f"measured action differs from the selected input action: {kind}")
        if measurement["python"] != workload["python_identity"]:
            _fail(f"measured Python identity differs from the workload: {kind}")
        hosts.add(
            json.dumps(
                {
                    "platform": measurement["host"]["platform"],
                    "machine": measurement["host"]["machine"],
                },
                sort_keys=True,
            )
        )
        if (
            measurement["sample_count"] != expected_sample_count
            or len(measurement["raw_latency_ns"]) != expected_sample_count
            or measurement["warmup_count"] != timing["warmups"]
            or measurement["rounds"] != timing["rounds"]
            or measurement["samples_per_round"] != timing["samples_per_round"]
        ):
            _fail(f"measurement counts differ from the declared policy: {kind}")
        observations.add(json.dumps(measurement["correctness_observation"], sort_keys=True))
    if len(observations) != 1:
        _fail("untimed correctness observations differ across measured subjects")
    if len(hosts) != 1 or next(iter(hosts)) != json.dumps(result["host"], sort_keys=True):
        _fail("measured subjects do not share the recorded host platform and machine")

    fastapi_latency = result["subjects"]["fastapi"]["latency_ns"]
    target_latency = result["subjects"]["fastapi-rs"]["latency_ns"]
    expected_ratios = {
        "fastapi_rs_over_fastapi_median": target_latency["median"] / fastapi_latency["median"],
        "fastapi_rs_over_fastapi_p95": target_latency["p95"] / fastapi_latency["p95"],
    }
    for name, expected in expected_ratios.items():
        if not math.isclose(result["ratios"][name], expected, rel_tol=0, abs_tol=0):
            _fail(f"reported ratio differs from raw subject statistics: {name}")

    comparison_path = (ROOT / result["parity_gate"]["comparison_artifact"]).resolve()
    try:
        comparison_path.relative_to(RESULT_ROOT)
    except ValueError as exc:
        raise ContractError("benchmark parity comparison must live under parity-results") from exc
    if not comparison_path.is_file():
        _fail("benchmark parity comparison artifact is missing")
    if sha256_file(comparison_path) != result["parity_gate"]["comparison_sha256"]:
        _fail("benchmark parity comparison artifact digest differs")
    _validate_identity_links(result, comparison_path)


def check_workloads(paths: list[Path] | None = None) -> tuple[int, int]:
    """Validate every checked-in benchmark declaration without executing products."""
    selected = paths if paths else sorted(WORKLOAD_ROOT.glob("*.yaml"))
    if not selected:
        _fail(f"no benchmark workloads found under {WORKLOAD_ROOT}")
    _check_schema(WORKLOAD_SCHEMA_PATH, "workload")
    _check_schema(RESULT_SCHEMA_PATH, "result")
    seen_ids: set[str] = set()
    for path in selected:
        workload, _, _, _, _ = load_workload(path)
        if workload["id"] in seen_ids:
            _fail(f"duplicate benchmark workload ID: {workload['id']}")
        seen_ids.add(workload["id"])
    return len(selected), len(seen_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="validate all declared benchmark workloads"
    )
    parser.add_argument("--workload", action="append", type=Path)
    args = parser.parse_args()
    if not args.check and not args.workload:
        parser.error("choose --check or provide at least one --workload")
    try:
        count, identities = check_workloads(args.workload)
    except (ContractError, OSError, ValueError) as exc:
        print(f"benchmark contract check failed: {exc}", file=sys.stderr)
        return 1
    print(f"benchmark contracts valid: {count} workloads, {identities} unique IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
