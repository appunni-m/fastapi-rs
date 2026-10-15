"""Strict workload and result contracts for the TestClient benchmark lane."""

from __future__ import annotations

import argparse
import base64
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.contract import (
    COMPARISON_SCHEMA_V13_ID,
    COMPARISON_SCHEMAS,
    RESULT_SCHEMA_V12_ID,
    RESULT_SCHEMAS,
    ROOT,
    WORKFLOW_SCHEMA_V12_ID,
    ContractError,
    _UniqueKeyLoader,
    load_workflow,
    read_json,
    read_manifest,
    sha256_file,
)

WORKLOAD_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/testclient-benchmark-workload.schema.json"
RESULT_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/testclient-benchmark-result.schema.json"
WORKLOAD_SCHEMA_ID = "fastapi-rs/testclient-benchmark-workload@1"
RESULT_SCHEMA_ID = "fastapi-rs/testclient-benchmark-result@1"
WORKLOAD_ROOT = (ROOT / "benchmarks/workloads/testclient").resolve()
PARITY_INPUT_ROOT = (ROOT / "tests/fixtures/inputs/parity").resolve()
PARITY_RESULT_ROOT = (ROOT / "parity-results").resolve()
BENCHMARK_RESULT_ROOT = (ROOT / "benchmark-results").resolve()

CASE_ID = "fastapi.benchmarks.sync-validated.testclient-request"
ACTION_ID = "sync-validated-post"
_EXPECTED_SUBJECTS = {
    "fastapi": ("fastapi-0.141.1", "oracle"),
    "fastapi-rs": ("fastapi-rs-release", "target"),
}
_EXPECTED_METRICS = {
    "per-request latency nanoseconds: min, median, p95, p99, max, mean",
    "sequential request-loop throughput including per-call setup and response extraction",
}


def _fail(message: str) -> None:
    raise ContractError(f"TestClient benchmark contract: {message}")


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


def _validate_schema_by_id(value: dict[str, Any], schemas: dict[str, Path], label: str) -> None:
    schema_id = value.get("schema")
    schema_path = schemas.get(schema_id)
    if schema_path is None:
        _fail(f"{label} has an unsupported schema: {schema_id!r}")
    _validate_schema(value, schema_path, label)


def _resolve_under(path_value: str, root: Path, label: str) -> Path:
    candidate = (ROOT / path_value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ContractError(
            f"TestClient benchmark {label} escapes {root.relative_to(ROOT)}"
        ) from exc
    if not candidate.is_file():
        _fail(f"{label} does not exist: {path_value}")
    return candidate


def _manifest_profiles(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    oracle = manifest["oracle_profile_extensions"]["testclient"]
    target = manifest["target_profile_extensions"]["testclient"]
    if oracle["added_packages"].get("httpx") != "0.28.1":
        _fail("oracle TestClient profile does not pin HTTPX 0.28.1")
    if target["added_packages"].get("httpx") != "0.28.1":
        _fail("target TestClient profile does not pin HTTPX 0.28.1")
    target_lock = target.get("lock", {})
    return {
        "oracle": {
            "name": "testclient",
            "id": oracle["id"],
            "base_profile": oracle["base_profile"],
            "added_packages": oracle["added_packages"],
        },
        "target": {
            "name": "testclient",
            "id": target["id"],
            "base_profile": target["base_profile"],
            "lock_sha256": target_lock["sha256"],
            "added_packages": target["added_packages"],
        },
    }


def _profile_packages(manifest: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    base = dict(manifest["oracle_profile"]["packages"])
    oracle = dict(base)
    oracle.update(manifest["oracle_profile_extensions"]["testclient"]["added_packages"])
    target = {name: value for name, value in base.items() if name not in {"fastapi", "starlette"}}
    target.update(manifest["target_profile_extensions"]["testclient"]["added_packages"])
    target["fastapi-rs"] = manifest["target"]["version"]
    target["starlette-rs-py"] = manifest["target"]["starlette_rs_distribution"]["version"]
    return oracle, target


def _combine_digests(entries: dict[str, str]) -> str:
    import hashlib

    digest = hashlib.sha256()
    for name, value in sorted(entries.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(value.encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def load_workload(
    path: Path,
    *,
    validate_payload_json: bool = True,
) -> tuple[dict[str, Any], Path, dict[str, Any], Path, dict[str, Any]]:
    """Load the single-case TestClient workload and its selected parity action."""
    workload_path = path if path.is_absolute() else ROOT / path
    workload_path = workload_path.resolve()
    try:
        workload_path.relative_to(WORKLOAD_ROOT)
    except ValueError as exc:
        raise ContractError(
            "TestClient benchmark workload must live under benchmarks/workloads/testclient"
        ) from exc
    if not workload_path.is_file():
        _fail(f"workload does not exist: {workload_path}")
    try:
        with workload_path.open(encoding="utf-8") as stream:
            workload = yaml.load(stream, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(
            f"cannot read TestClient benchmark workload {workload_path}: {exc}"
        ) from exc
    if not isinstance(workload, dict):
        _fail("workload must be a YAML object")
    _validate_schema(workload, WORKLOAD_SCHEMA_PATH, "workload")

    if workload["profiles"] != {"oracle": "testclient", "target": "testclient"}:
        _fail("oracle and target must select the paired testclient runtime profiles")
    manifest = read_manifest()
    if workload["python_identity"] != manifest["oracle_profile"]["python"]:
        _fail("workload Python identity differs from the pinned CPython profile")
    _manifest_profiles(manifest)

    input_path = _resolve_under(workload["input"]["path"], PARITY_INPUT_ROOT, "parity input")
    workflow, _, _, _ = load_workflow(input_path)
    if workflow.get("schema") != WORKFLOW_SCHEMA_V12_ID:
        _fail("TestClient benchmark input must use Python/ASGI workflow schema v12")
    if workflow.get("oracle_profile_extension") != "testclient":
        _fail("selected parity input does not use the TestClient oracle profile")
    cases = [case for case in workflow["cases"] if case["case_id"] == CASE_ID]
    if len(cases) != 1 or workload["input"]["case_id"] != CASE_ID:
        _fail(f"input must contain exactly the pinned TestClient case {CASE_ID}")
    case = cases[0]
    actions = [action for action in case["actions"] if action["action_id"] == ACTION_ID]
    if len(actions) != 1 or workload["input"]["action_id"] != ACTION_ID:
        _fail(f"input must contain exactly the pinned TestClient action {ACTION_ID}")
    action = actions[0]
    if action["kind"] != "testclient_request":
        _fail("selected parity action must execute through TestClient")
    request = action["request"]
    if request["method"] != "POST" or request["url"] != "/sync/validated":
        _fail("selected action differs from the sync-validated POST benchmark")
    if validate_payload_json:
        try:
            body = base64.b64decode(request["content_base64"], validate=True)
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ContractError("selected TestClient request body must be a JSON document") from exc
        if not isinstance(payload, dict):
            _fail("selected TestClient JSON request body must be an object")
    response_observations = [
        observation
        for observation in action["observations"]
        if observation["kind"] == "http_response"
    ]
    if len(response_observations) != 1 or set(response_observations[0]["selectors"]) != {
        "status",
        "body",
    }:
        _fail("selected parity action must compare exactly the HTTP status and response body")
    if response_observations[0]["comparison"] != "exact":
        _fail("selected TestClient response must use exact parity comparison")
    if set(workload["correctness_gate"]["require_equal_untimed_observation"]) != {
        "status",
        "body",
    }:
        _fail("benchmark correctness gate must compare untimed status and body observations")
    if workload["correctness_gate"]["required_comparison"] != "all-selected-cases-pass":
        _fail("benchmark correctness gate must require the selected parity case to pass")

    subject_kinds = [subject["kind"] for subject in workload["subjects"]]
    if len(subject_kinds) != len(set(subject_kinds)) or set(subject_kinds) != set(
        _EXPECTED_SUBJECTS
    ):
        _fail("benchmark subjects must include FastAPI oracle and FastAPI-RS target exactly once")
    for subject in workload["subjects"]:
        expected_id, expected_environment = _EXPECTED_SUBJECTS[subject["kind"]]
        if subject["id"] != expected_id or subject["environment"] != expected_environment:
            _fail(f"subject identity differs from the pinned runner mapping: {subject['kind']}")

    timing = workload["timing"]
    if timing["concurrency"] != 1 or set(timing["metrics"]) != _EXPECTED_METRICS:
        _fail("TestClient timing metrics or sequential concurrency differ from the reviewed lane")
    if timing["raw_samples"] != "retain all per-request latency samples":
        _fail("TestClient worker must retain every measured per-request latency sample")
    if "client.post" not in timing["boundary"] or "response.content" not in timing["boundary"]:
        _fail("timing boundary must include TestClient POST and response-body extraction")
    if not any(
        "TestClient construction" in item and "lifespan" in item for item in timing["excludes"]
    ):
        _fail("timing exclusions must keep client construction and lifespan startup outside timing")
    return workload, workload_path, workflow, input_path, action


def _artifact(path_value: str, expected_product: str, expected_digest: str) -> dict[str, Any]:
    artifact_path = _resolve_under(path_value, PARITY_RESULT_ROOT, "parity result artifact")
    if sha256_file(artifact_path) != expected_digest:
        _fail(f"parity result digest differs from comparison reference: {path_value}")
    result = read_json(artifact_path)
    if not isinstance(result, dict) or result.get("product") != expected_product:
        _fail(f"parity result is not a {expected_product} artifact: {path_value}")
    _validate_schema_by_id(result, RESULT_SCHEMAS, f"{expected_product} parity result")
    if result.get("schema") != RESULT_SCHEMA_V12_ID:
        _fail("TestClient parity result must use result schema v12 for workflow v12")
    return result


def _expected_worker_identities(
    source: dict[str, Any], target: dict[str, Any], manifest: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_identity = source["identity"]
    target_identity = target["identity"]
    oracle_packages, target_packages = _profile_packages(manifest)
    shared_source = {
        key: value for key, value in oracle_packages.items() if key not in {"fastapi", "starlette"}
    }
    shared_target = {
        key: value
        for key, value in target_packages.items()
        if key not in {"fastapi-rs", "starlette-rs-py"}
    }
    oracle_pins = manifest["oracle_profile"]
    target_pins = manifest["target"]
    oracle_repositories = source_identity["repositories"]
    target_repositories = target_identity["repositories"]
    if (
        source_identity["distribution"] != "fastapi"
        or source_identity["version"] != oracle_pins["packages"]["fastapi"]
        or source_identity["python"] != oracle_pins["python"]
        or oracle_repositories["fastapi_source"] != oracle_pins["source_commits"]["fastapi"]
        or oracle_repositories["starlette_source"] != oracle_pins["source_commits"]["starlette"]
        or source_identity["packages"] != oracle_packages
    ):
        _fail("fresh oracle parity identity differs from the pinned TestClient profile")
    starlette_rs_pin = target_pins["starlette_rs_distribution"]
    if (
        target_identity["distribution"] != "fastapi-rs"
        or target_identity["version"] != target_pins["version"]
        or target_identity["python"] != oracle_pins["python"]
        or target_repositories["fastapi_rs"] != target_identity["target_revision"]
        or target_repositories["starlette_rs"] != starlette_rs_pin["commit"]
        or target_identity["packages"] != target_packages
    ):
        _fail("fresh target parity identity differs from the pinned TestClient profile")
    measured_source = {
        "fastapi": source_identity["version"],
        "fastapi_source": oracle_repositories["fastapi_source"],
        "starlette": oracle_packages["starlette"],
        "starlette_source": oracle_repositories["starlette_source"],
        "shared_packages": shared_source,
    }
    measured_target = {
        "fastapi_rs_source": target_repositories["fastapi_rs"],
        "fastapi_rs": target_identity["version"],
        "target_binary_sha256": target_identity["target_binary_sha256"],
        "source_tree_sha256": target_identity["source_tree_sha256"],
        "starlette_rs": starlette_rs_pin["version"],
        "starlette_rs_source": target_repositories["starlette_rs"],
        "shared_packages": shared_target,
    }
    return measured_source, measured_target


def _percentile(samples: list[int], percent: float) -> int:
    ordered = sorted(samples)
    return ordered[round((len(ordered) - 1) * percent / 100)]


def _latency_summary(samples: list[int]) -> dict[str, int | float]:
    import statistics

    return {
        "min": min(samples),
        "median": int(statistics.median(samples)),
        "p95": _percentile(samples, 95),
        "p99": _percentile(samples, 99),
        "max": max(samples),
        "mean": statistics.fmean(samples),
    }


def validate_result(
    result: dict[str, Any],
    *,
    workload: dict[str, Any],
    workload_path: Path,
    input_path: Path,
    action: dict[str, Any],
    comparison_path: Path | None = None,
) -> None:
    """Validate a paired result against workload, parity, and live identities."""
    _validate_schema(result, RESULT_SCHEMA_PATH, "benchmark result")
    workload_path = workload_path.resolve()
    input_path = input_path.resolve()
    expected_workload = {
        "id": workload["id"],
        "path": workload_path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(workload_path),
        "input_path": input_path.relative_to(ROOT).as_posix(),
        "input_sha256": sha256_file(input_path),
        "case_id": workload["input"]["case_id"],
        "action_id": workload["input"]["action_id"],
    }
    if result["workload"] != expected_workload:
        _fail("result workload/input digests or case/action identity differs from its declaration")
    manifest = read_manifest()
    profiles = _manifest_profiles(manifest)
    if result["profiles"] != profiles:
        _fail("result runtime profile identity or target lock digest differs from the manifest")
    if result["python_identity"] != workload["python_identity"]:
        _fail("result Python identity differs from the workload")
    if result["boundary"] != workload["timing"]["boundary"]:
        _fail("result timing boundary differs from the declared workload boundary")
    expected_timing = {
        "warmups": workload["timing"]["warmups"],
        "rounds": workload["timing"]["rounds"],
        "samples_per_round": workload["timing"]["samples_per_round"],
        "concurrency": workload["timing"]["concurrency"],
    }
    if result["timing"] != expected_timing:
        _fail("result counts differ from the declared timing policy")
    expected_count = expected_timing["rounds"] * expected_timing["samples_per_round"]
    observations: set[str] = set()
    for kind in ("fastapi", "fastapi-rs"):
        measurement = result["subjects"][kind]
        profile = profiles["oracle" if kind == "fastapi" else "target"]
        expected_identity = result["source_identity" if kind == "fastapi" else "target_identity"]
        if (
            measurement["subject"] != kind
            or measurement["selected_action_id"] != action["action_id"]
            or measurement["profile_identity"] != profile
            or measurement["identity"] != expected_identity
            or measurement["python_identity"] != workload["python_identity"]
        ):
            _fail(f"{kind} result identity differs from the selected profile or parity identity")
        if (
            measurement["sample_count"] != expected_count
            or len(measurement["raw_latency_ns"]) != expected_count
            or measurement["warmup_count"] != expected_timing["warmups"]
            or measurement["rounds"] != expected_timing["rounds"]
            or measurement["samples_per_round"] != expected_timing["samples_per_round"]
        ):
            _fail(f"{kind} sample counts differ from the declared timing policy")
        samples = measurement["raw_latency_ns"]
        if measurement["latency_ns"] != _latency_summary(samples):
            _fail(f"{kind} latency summary differs from its raw samples")
        if not math.isclose(
            measurement["request_loop_throughput_per_second"],
            expected_count * 1_000_000_000 / measurement["request_loop_elapsed_ns"],
            rel_tol=1e-12,
            abs_tol=0,
        ):
            _fail(f"{kind} loop throughput differs from its elapsed time")
        observations.add(json.dumps(measurement["correctness_observation"], sort_keys=True))
    if len(observations) != 1:
        _fail("untimed live status/body observations differ across benchmark subjects")
    source_latency = result["subjects"]["fastapi"]["latency_ns"]
    target_latency = result["subjects"]["fastapi-rs"]["latency_ns"]
    if source_latency["median"] <= 0 or source_latency["p95"] <= 0:
        _fail("FastAPI latency denominator must be positive")
    expected_ratios = {
        "fastapi_rs_over_fastapi_median": target_latency["median"] / source_latency["median"],
        "fastapi_rs_over_fastapi_p95": target_latency["p95"] / source_latency["p95"],
    }
    for name, expected in expected_ratios.items():
        if not math.isclose(result["ratios"][name], expected, rel_tol=0, abs_tol=0):
            _fail(f"reported ratio differs from raw subject statistics: {name}")

    gate = result["parity_gate"]
    comparison_path = (
        Path(comparison_path) if comparison_path is not None else Path(gate["comparison_artifact"])
    )
    if not comparison_path.is_absolute():
        comparison_path = ROOT / comparison_path
    comparison_path = comparison_path.resolve()
    try:
        comparison_path.relative_to(PARITY_RESULT_ROOT)
    except ValueError as exc:
        raise ContractError(
            "TestClient benchmark comparison must live under parity-results"
        ) from exc
    declared_path = (ROOT / gate["comparison_artifact"]).resolve()
    if declared_path != comparison_path:
        _fail("command-line comparison artifact differs from the result declaration")
    if sha256_file(comparison_path) != gate["comparison_sha256"]:
        _fail("parity comparison artifact digest differs from the result declaration")
    comparison = read_json(comparison_path)
    if not isinstance(comparison, dict):
        _fail("parity comparison artifact must be a JSON object")
    _validate_schema_by_id(comparison, COMPARISON_SCHEMAS, "parity comparison")
    if comparison.get("schema") != COMPARISON_SCHEMA_V13_ID:
        _fail("TestClient parity comparison must use comparison schema v13 for workflow v12")
    expected_input = {
        "path": expected_workload["input_path"],
        "sha256": expected_workload["input_sha256"],
        "schema": WORKFLOW_SCHEMA_V12_ID,
    }
    if comparison.get("input") != expected_input:
        _fail("fresh parity comparison input differs from the benchmark input")
    if comparison.get("manifest") != {
        "path": "tests/fixtures/manifest.yaml",
        "sha256": sha256_file(ROOT / "tests/fixtures/manifest.yaml"),
    }:
        _fail("fresh parity comparison does not use the current manifest digest")
    summary = comparison.get("summary", {})
    parity_summary = summary.get("parity", {})
    selected_cases = comparison.get("cases", [])
    if (
        comparison.get("status") != "completed"
        or summary.get("selected") != 1
        or summary.get("passed") != 1
        or summary.get("failed") != 0
        or summary.get("not_run") != 0
        or parity_summary.get("selected") != 1
        or parity_summary.get("passed") != 1
        or parity_summary.get("failed") != 0
        or len(selected_cases) != 1
        or selected_cases[0].get("case_id") != workload["input"]["case_id"]
        or selected_cases[0].get("outcome") != "pass"
    ):
        _fail("fresh parity comparison must contain exactly one passing selected case")
    if gate["summary"] != {"selected": 1, "passed": 1, "failed": 0, "not_run": 0}:
        _fail("result parity summary must record exactly one passed case")
    source_ref = comparison.get("source_result", {})
    target_ref = comparison.get("target_result", {})
    source = _artifact(source_ref.get("path", ""), "oracle", source_ref.get("sha256", ""))
    target = _artifact(target_ref.get("path", ""), "target", target_ref.get("sha256", ""))
    if (
        source.get("run_id") != source_ref.get("run_id")
        or target.get("run_id") != target_ref.get("run_id")
        or source.get("run_id") == target.get("run_id")
        or source.get("status") != "completed"
        or target.get("status") != "completed"
        or source.get("input") != expected_input
        or target.get("input") != expected_input
        or source.get("manifest") != comparison.get("manifest")
        or target.get("manifest") != comparison.get("manifest")
    ):
        _fail(
            "comparison must reference fresh completed source and target identities for this input"
        )
    source_identity, target_identity = _expected_worker_identities(source, target, manifest)
    measured_target = result["target_identity"]
    target_identity_matches = all(
        measured_target.get(name) == value for name, value in target_identity.items()
    )
    binary_digest = _combine_digests(
        {
            "fastapi_rs._core": measured_target["fastapi_rs_extension_sha256"],
            "starlette_rs_py._core": measured_target["starlette_rs_extension_sha256"],
        }
    )
    if (
        result["source_identity"] != source_identity
        or not target_identity_matches
        or binary_digest != measured_target["target_binary_sha256"]
    ):
        _fail("benchmark source/target identities differ from the fresh parity identity pair")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate one named workload/result")
    parser.add_argument("--workload", type=Path, required=True)
    parser.add_argument("--result", type=Path, help="optional paired benchmark result JSON")
    parser.add_argument("--comparison", type=Path, help="explicit parity comparison artifact")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")
    if args.comparison is not None and args.result is None:
        parser.error("--comparison requires --result")
    try:
        workload, workload_path, _, input_path, action = load_workload(args.workload)
        if args.result is not None:
            result_path = args.result if args.result.is_absolute() else ROOT / args.result
            result_path = result_path.resolve()
            try:
                result_path.relative_to(BENCHMARK_RESULT_ROOT)
            except ValueError as exc:
                raise ContractError("benchmark result must live under benchmark-results") from exc
            result = read_json(result_path)
            if not isinstance(result, dict):
                _fail("benchmark result must be a JSON object")
            validate_result(
                result,
                workload=workload,
                workload_path=workload_path,
                input_path=input_path,
                action=action,
                comparison_path=args.comparison,
            )
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"TestClient benchmark contract check failed: {exc}", file=sys.stderr)
        return 1
    if args.result is None:
        print(f"TestClient benchmark workload valid: {workload['id']}")
    else:
        print(f"TestClient benchmark workload and result valid: {workload['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
