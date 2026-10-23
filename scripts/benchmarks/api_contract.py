"""Validate input-only direct Python API benchmark workloads."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.contract import (
    API_WORKFLOW_SCHEMA_IDS,
    ROOT,
    ContractError,
    _UniqueKeyLoader,
    load_workflow,
    read_json,
    read_manifest,
    sha256_file,
)

DEFAULT_FASTAPI_SOURCE = (ROOT / "../fastapi").resolve()
WORKLOAD_ROOT = (ROOT / "benchmarks/workloads/api").resolve()
INPUT_ROOT = (ROOT / "tests/fixtures/inputs/parity").resolve()
WORKLOAD_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/api-benchmark-workload.schema.json"
RESULT_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/api-benchmark-result.schema.json"
WORKLOAD_SCHEMA_ID = "fastapi-rs/python-api-benchmark-workload@1"
RESULT_SCHEMA_ID = "fastapi-rs/python-api-benchmark-result@1"


class ApiBenchmarkContractError(ContractError):
    """A direct API benchmark declaration or result is invalid."""


def _validate_schema(value: Any, schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    Draft202012Validator.check_schema(schema)
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
        raise ApiBenchmarkContractError(f"{label} does not match its schema: {details}")


def load_workload(
    path: Path,
    *,
    fastapi_source: Path = DEFAULT_FASTAPI_SOURCE,
) -> tuple[dict[str, Any], Path, dict[str, Any], Path, Path, dict[str, Any], dict[str, Any]]:
    """Load one strict benchmark declaration and its indexed API case/probe."""
    workload_path = path if path.is_absolute() else ROOT / path
    workload_path = workload_path.resolve()
    try:
        workload_path.relative_to(WORKLOAD_ROOT)
    except ValueError as exc:
        raise ApiBenchmarkContractError(
            "API benchmark workload must live under benchmarks/workloads/api"
        ) from exc
    try:
        with workload_path.open(encoding="utf-8") as stream:
            workload = yaml.load(stream, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ApiBenchmarkContractError(f"cannot read API benchmark workload: {exc}") from exc
    if not isinstance(workload, dict):
        raise ApiBenchmarkContractError("API benchmark workload must be a YAML object")
    _validate_schema(workload, WORKLOAD_SCHEMA_PATH, "API benchmark workload")

    input_path = (ROOT / workload["input"]["path"]).resolve()
    try:
        input_path.relative_to(INPUT_ROOT)
    except ValueError as exc:
        raise ApiBenchmarkContractError("API benchmark parity input escapes its lane") from exc
    workflow, resolved_input, input_digest, parity_workload_path = load_workflow(
        input_path,
        source_root=fastapi_source.resolve(),
    )
    if resolved_input != input_path or workflow.get("schema") not in API_WORKFLOW_SCHEMA_IDS:
        raise ApiBenchmarkContractError("API benchmark must reference a direct API parity input")

    selected_cases = [
        case for case in workflow["cases"] if case["case_id"] == workload["input"]["case_id"]
    ]
    if len(selected_cases) != 1:
        raise ApiBenchmarkContractError("API benchmark case is missing or ambiguous")
    selected_probes = [
        probe
        for probe in selected_cases[0]["probes"]
        if probe["probe_id"] == workload["input"]["probe_id"]
    ]
    if len(selected_probes) != 1:
        raise ApiBenchmarkContractError("API benchmark probe is missing or ambiguous")
    probe = selected_probes[0]
    if (
        probe.get("public_callable") != workload["invoke"]["public_callable"]
        or probe.get("argument_bundle") != workload["input"]["argument_bundle"]
    ):
        raise ApiBenchmarkContractError(
            "benchmark callable or arguments differ from the indexed parity probe"
        )
    manifest = read_manifest()
    if workload["python_identity"] != manifest["oracle_profile"]["python"]:
        raise ApiBenchmarkContractError("benchmark Python identity differs from the pinned profile")
    if [subject["kind"] for subject in workload["subjects"]] != ["fastapi", "fastapi-rs"]:
        raise ApiBenchmarkContractError("API benchmark subjects must be oracle then target")
    if workload["correctness_gate"]["required_comparison"] != "all-selected-cases-pass":
        raise ApiBenchmarkContractError("API benchmark requires a passing parity comparison")

    return (
        workload,
        workload_path,
        workflow,
        input_path,
        parity_workload_path,
        selected_cases[0],
        probe,
    )


def validate_result(
    result: dict[str, Any],
    *,
    workload: dict[str, Any],
    workload_path: Path,
    input_path: Path,
    comparison_path: Path,
    comparison_sha256: str,
) -> None:
    """Validate generated measurement identity, counts, and reported ratios."""
    _validate_schema(result, RESULT_SCHEMA_PATH, "API benchmark result")
    relative_workload = workload_path.relative_to(ROOT).as_posix()
    relative_input = input_path.relative_to(ROOT).as_posix()
    expected_workload = {
        "id": workload["id"],
        "path": relative_workload,
        "sha256": sha256_file(workload_path),
        "input_path": relative_input,
        "input_sha256": sha256_file(input_path),
        "case_id": workload["input"]["case_id"],
        "probe_id": workload["input"]["probe_id"],
        "argument_bundle": workload["input"]["argument_bundle"],
    }
    if result["workload"] != expected_workload:
        raise ApiBenchmarkContractError("result workload identity differs from its declaration")
    gate = result["parity_gate"]
    if gate["comparison_artifact"] != comparison_path.relative_to(ROOT).as_posix():
        raise ApiBenchmarkContractError("result parity comparison path differs")
    if gate["comparison_sha256"] != comparison_sha256:
        raise ApiBenchmarkContractError("result parity comparison digest differs")
    timing = workload["timing"]
    expected_count = timing["rounds"] * timing["samples_per_round"]
    for subject in ("fastapi", "fastapi-rs"):
        measurement = result["subjects"][subject]
        if (
            measurement["sample_count"] != expected_count
            or len(measurement["raw_latency_ns"]) != expected_count
            or measurement["warmup_count"] != timing["warmups"]
            or measurement["rounds"] != timing["rounds"]
            or measurement["samples_per_round"] != timing["samples_per_round"]
        ):
            raise ApiBenchmarkContractError(f"measurement counts differ from policy: {subject}")
    source = result["subjects"]["fastapi"]["latency_ns"]
    target = result["subjects"]["fastapi-rs"]["latency_ns"]
    expected_ratios = {
        "fastapi_rs_over_fastapi_median": target["median"] / source["median"],
        "fastapi_rs_over_fastapi_p95": target["p95"] / source["p95"],
    }
    if result["ratios"] != expected_ratios:
        raise ApiBenchmarkContractError("benchmark ratios differ from recorded measurements")


def check_workloads(
    paths: list[Path] | None = None,
    *,
    fastapi_source: Path = DEFAULT_FASTAPI_SOURCE,
) -> int:
    selected = paths if paths else sorted(WORKLOAD_ROOT.rglob("*.yaml"))
    if not selected:
        raise ApiBenchmarkContractError(f"no API workloads found under {WORKLOAD_ROOT}")
    Draft202012Validator.check_schema(read_json(WORKLOAD_SCHEMA_PATH))
    Draft202012Validator.check_schema(read_json(RESULT_SCHEMA_PATH))
    ids: set[str] = set()
    for path in selected:
        workload, *_ = load_workload(path, fastapi_source=fastapi_source)
        if workload["id"] in ids:
            raise ApiBenchmarkContractError(
                f"duplicate API benchmark workload ID: {workload['id']}"
            )
        ids.add(workload["id"])
    return len(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--workload", action="append", type=Path)
    parser.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    args = parser.parse_args()
    if not args.check and not args.workload:
        parser.error("choose --check or provide at least one --workload")
    try:
        count = check_workloads(args.workload, fastapi_source=args.fastapi_source)
    except (ApiBenchmarkContractError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"API benchmark contract check failed: {exc}", file=sys.stderr)
        return 1
    print(f"API benchmark contracts valid: {count} workloads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
