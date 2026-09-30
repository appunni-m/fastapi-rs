"""Compare direct public Python API probes from isolated product processes."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from scripts.parity.comparator import _validate_identity_pair
from scripts.parity.contract import (
    API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
    API_RESULT_SCHEMA_IDS_BY_WORKFLOW,
    API_WORKFLOW_SCHEMA_IDS,
    ContractError,
)

WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow@3"


def _diff(probe_id: str, path: str, source: Any, target: Any) -> dict[str, Any]:
    return {
        "probe_id": probe_id,
        "path": path,
        "comparison": "exact",
        "source": source,
        "target": target,
    }


def _json_exact_equal(source: Any, target: Any) -> bool:
    """Compare JSON values without Python's bool/int/float equality coercions."""
    if type(source) is not type(target):
        return False
    if type(source) is dict:
        if source.keys() != target.keys():
            return False
        return all(_json_exact_equal(source[key], target[key]) for key in source)
    if type(source) is list:
        return len(source) == len(target) and all(
            _json_exact_equal(left, right) for left, right in zip(source, target, strict=True)
        )
    return source == target


def compare_api_workflow_results(
    *,
    workflow: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    oracle_profile: dict[str, Any],
    target_profile: dict[str, Any],
    manifest_sha256: str,
    input_path: str,
    input_sha256: str,
    workload_sha256: str,
    source_result_ref: dict[str, Any],
    target_result_ref: dict[str, Any],
    command: list[str],
) -> dict[str, Any]:
    """Compare same-index API observations and retain exact source/target values."""
    workflow_schema_id = workflow.get("schema")
    if workflow_schema_id not in API_WORKFLOW_SCHEMA_IDS:
        raise ContractError("direct API comparison requires a supported API workflow")
    expected_result_schema = API_RESULT_SCHEMA_IDS_BY_WORKFLOW[workflow_schema_id]
    if source.get("schema") != expected_result_schema:
        raise ContractError("direct API source result schema differs from its workflow version")
    if target.get("schema") != expected_result_schema:
        raise ContractError("direct API target result schema differs from its workflow version")
    if source.get("product") != "oracle" or target.get("product") != "target":
        raise ContractError("direct API comparison needs oracle and target results")
    for label, result in (("oracle", source), ("target", target)):
        if result.get("status") != "completed" or result.get("infrastructure_errors") != []:
            raise ContractError(
                f"direct API {label} run is incomplete or has infrastructure errors"
            )
        if result.get("manifest") != {
            "path": "tests/fixtures/manifest.yaml",
            "sha256": manifest_sha256,
        }:
            raise ContractError(f"direct API {label} result uses a different manifest")
        if result.get("input") != {
            "path": input_path,
            "sha256": input_sha256,
            "schema": workflow["schema"],
        }:
            raise ContractError(f"direct API {label} result uses a different workflow input")
        expected_workload = {
            "path": workflow["workload"]["file"],
            "sha256": workload_sha256,
            "factory": workflow["workload"]["factory"],
        }
        if result.get("workload") != expected_workload:
            raise ContractError(f"direct API {label} result uses a different workload")

    _validate_identity_pair(source, target, oracle_profile, target_profile)
    source_cases = source.get("cases")
    target_cases = target.get("cases")
    specifications = workflow.get("cases")
    if not isinstance(source_cases, list) or not isinstance(target_cases, list):
        raise ContractError("direct API product results must contain case arrays")
    if (
        not isinstance(specifications, list)
        or len(source_cases) != len(specifications)
        or len(target_cases) != len(specifications)
    ):
        raise ContractError("direct API source/target case counts differ from the workflow")

    cases: list[dict[str, Any]] = []
    for specification, source_case, target_case in zip(
        specifications, source_cases, target_cases, strict=True
    ):
        case_id = specification["case_id"]
        if source_case.get("case_id") != case_id or target_case.get("case_id") != case_id:
            raise ContractError("direct API source/target case order differs from the workflow")
        expected_probes = specification.get("probes")
        source_probes = source_case.get("probes")
        target_probes = target_case.get("probes")
        if (
            not isinstance(expected_probes, list)
            or not isinstance(source_probes, list)
            or not isinstance(target_probes, list)
        ):
            raise ContractError(f"direct API probe arrays are missing: {case_id}")
        if len(source_probes) != len(expected_probes) or len(target_probes) != len(expected_probes):
            raise ContractError(f"direct API probe counts differ from the workflow: {case_id}")

        diffs: list[dict[str, Any]] = []

        if source_case.get("status") != target_case.get("status"):
            diffs.append(
                _diff("case", "/status", source_case.get("status"), target_case.get("status"))
            )
        if (
            source_case.get("status") == "product_error"
            and target_case.get("status") == "product_error"
        ):
            if source_case.get("error") != target_case.get("error"):
                diffs.append(
                    _diff("case", "/error", source_case.get("error"), target_case.get("error"))
                )

        for probe_spec, source_probe, target_probe in zip(
            expected_probes, source_probes, target_probes, strict=True
        ):
            probe_id = probe_spec["probe_id"]
            if source_probe.get("probe_id") != probe_id or target_probe.get("probe_id") != probe_id:
                raise ContractError(f"direct API probe order differs from the workflow: {case_id}")
            source_status = source_probe.get("status")
            target_status = target_probe.get("status")
            base = f"/probes/{probe_id}"
            if source_status != target_status:
                diffs.append(_diff(probe_id, f"{base}/status", source_status, target_status))
            if workflow_schema_id == WORKFLOW_SCHEMA_V3_ID:
                if probe_spec.get("capture_warnings") is True:
                    source_warnings = source_probe.get("warnings")
                    target_warnings = target_probe.get("warnings")
                    if not isinstance(source_warnings, list) or not isinstance(
                        target_warnings, list
                    ):
                        raise ContractError(
                            f"direct API warning sidecars are missing: {case_id}/{probe_id}"
                        )
                    if not _json_exact_equal(source_warnings, target_warnings):
                        diffs.append(
                            _diff(
                                probe_id,
                                f"{base}/warnings",
                                source_warnings,
                                target_warnings,
                            )
                        )
                elif "warnings" in source_probe or "warnings" in target_probe:
                    raise ContractError(
                        f"direct API warning sidecar was not selected: {case_id}/{probe_id}"
                    )
            if source_status == "product_error" and target_status == "product_error":
                if source_probe.get("error") != target_probe.get("error"):
                    diffs.append(
                        _diff(
                            probe_id,
                            f"{base}/error",
                            source_probe.get("error"),
                            target_probe.get("error"),
                        )
                    )
                continue
            if source_status != "completed" or target_status != "completed":
                continue
            source_observations = source_probe.get("observations")
            target_observations = target_probe.get("observations")
            expected_kinds = [row["kind"] for row in probe_spec["observations"]]
            if not isinstance(source_observations, list) or not isinstance(
                target_observations, list
            ):
                raise ContractError(f"direct API observations are missing: {case_id}/{probe_id}")
            if len(source_observations) != len(expected_kinds) or len(target_observations) != len(
                expected_kinds
            ):
                raise ContractError(
                    f"direct API observation counts differ from input: {case_id}/{probe_id}"
                )
            for index, (kind, source_observation, target_observation) in enumerate(
                zip(expected_kinds, source_observations, target_observations, strict=True)
            ):
                if (
                    source_observation.get("index") != index
                    or target_observation.get("index") != index
                    or source_observation.get("kind") != kind
                    or target_observation.get("kind") != kind
                ):
                    raise ContractError(
                        f"direct API observation ordering differs: {case_id}/{probe_id}"
                    )
                if not _json_exact_equal(
                    source_observation.get("values"), target_observation.get("values")
                ):
                    diffs.append(
                        _diff(
                            probe_id,
                            f"{base}/observations/{index}/values",
                            source_observation.get("values"),
                            target_observation.get("values"),
                        )
                    )

        cases.append({"case_id": case_id, "outcome": "fail" if diffs else "pass", "diffs": diffs})

    failed = sum(case["outcome"] == "fail" for case in cases)
    return {
        "schema": API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW[workflow_schema_id],
        "run_id": str(uuid.uuid4()),
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "scope": "direct-python-api",
        "manifest": {"path": "tests/fixtures/manifest.yaml", "sha256": manifest_sha256},
        "input": {"path": input_path, "sha256": input_sha256, "schema": workflow["schema"]},
        "source_result": source_result_ref,
        "target_result": target_result_ref,
        "command": {"argv": command, "cwd": "."},
        "status": "completed",
        "summary": {
            "selected": len(cases),
            "passed": len(cases) - failed,
            "failed": failed,
            "not_run": 0,
        },
        "cases": cases,
        "infrastructure_errors": [],
    }
