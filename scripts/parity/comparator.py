"""Exact, input-driven comparison for isolated oracle and target results."""

from __future__ import annotations

import datetime as dt
import re
import uuid
from typing import Any

from scripts.parity.contract import (
    COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
    RESULT_SCHEMA_IDS_BY_WORKFLOW,
    WORKFLOW_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V5_ID,
    ContractError,
)

WORKFLOW_SCHEMA_V4_ID = "fastapi-rs/python-asgi-workflow@4"

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
PRODUCT_PACKAGES = {"fastapi", "starlette", "fastapi-rs", "starlette-rs-py"}


class ComparisonError(ContractError):
    """Run artifacts cannot be compared under the selected fixed profile."""


def _validate_identity_pair(
    source: dict[str, Any],
    target: dict[str, Any],
    oracle_profile: dict[str, Any],
    target_profile: dict[str, Any],
) -> None:
    if source.get("product") != "oracle" or target.get("product") != "target":
        raise ComparisonError("comparison requires one oracle result and one target result")
    source_identity = source["identity"]
    target_identity = target["identity"]
    expected_packages = oracle_profile["packages"]
    expected_commits = oracle_profile["source_commits"]

    if source_identity["distribution"] != "fastapi":
        raise ComparisonError("source result is not the FastAPI distribution")
    if source_identity["version"] != expected_packages["fastapi"]:
        raise ComparisonError("source FastAPI version differs from the pinned oracle profile")
    if source_identity["python"] != oracle_profile["python"]:
        raise ComparisonError("source Python identity differs from the pinned oracle profile")
    if source_identity["repositories"]["fastapi_source"] != expected_commits["fastapi"]:
        raise ComparisonError("source FastAPI commit differs from the pinned oracle profile")
    if source_identity["repositories"]["starlette_source"] != expected_commits["starlette"]:
        raise ComparisonError("source Starlette commit differs from the sole 1.6.0 profile")
    if source_identity["packages"] != expected_packages:
        raise ComparisonError("source runtime packages differ from the pinned oracle profile")

    if target_identity["distribution"] != "fastapi-rs":
        raise ComparisonError("target result is not the FastAPI-RS distribution")
    if target_identity["version"] != target_profile["version"]:
        raise ComparisonError("target FastAPI-RS version differs from the selected target profile")
    if not target_identity["target_revision"]:
        raise ComparisonError("target source revision is missing")
    tree_digest = target_identity["source_tree_sha256"]
    if not isinstance(tree_digest, str) or re.fullmatch(r"[a-f0-9]{64}", tree_digest) is None:
        raise ComparisonError("target source-tree identity is missing or malformed")
    binary_digest = target_identity["target_binary_sha256"]
    if not isinstance(binary_digest, str) or re.fullmatch(r"[a-f0-9]{64}", binary_digest) is None:
        raise ComparisonError("target compiled-extension identity is missing or malformed")
    repositories = target_identity["repositories"]
    if not repositories["fastapi_rs"] or not repositories["starlette_rs"]:
        raise ComparisonError("FastAPI-RS and Starlette-RS source identities are both required")
    if repositories["fastapi_source"] is not None or repositories["starlette_source"] is not None:
        raise ComparisonError(
            "target process must not import the FastAPI or Starlette oracle checkouts"
        )
    if "starlette" in target_identity["packages"]:
        raise ComparisonError(
            "target process installed upstream Starlette alongside its replacement"
        )
    if target_identity["packages"].get("fastapi-rs") != target_identity["version"]:
        raise ComparisonError("target distribution metadata and worker identity version differ")
    if "starlette-rs-py" not in target_identity["packages"]:
        raise ComparisonError("target process did not identify its Starlette-RS distribution")
    starlette_rs = target_profile["starlette_rs_distribution"]
    if target_identity["packages"]["starlette-rs-py"] != starlette_rs["version"]:
        raise ComparisonError(
            "target Starlette-RS version differs from the selected target profile"
        )
    if target_identity["repositories"]["starlette_rs"] != starlette_rs["commit"]:
        raise ComparisonError("target Starlette-RS commit differs from the selected target profile")
    expected_target_packages = SHARED_ORACLE_PACKAGES | {"fastapi-rs", "starlette-rs-py"}
    if set(target_identity["packages"]) != expected_target_packages:
        raise ComparisonError("target runtime package set differs from its declared fixed profile")
    if target_identity["python"] != source_identity["python"]:
        raise ComparisonError("source and target Python runtimes differ")
    if target_identity["platform"] != source_identity["platform"]:
        raise ComparisonError("source and target platforms differ")
    for package in SHARED_ORACLE_PACKAGES:
        if target_identity["packages"].get(package) != expected_packages[package]:
            raise ComparisonError(f"source and target {package} versions differ or are missing")
    unexpected_shared = (
        set(source_identity["packages"]) & set(target_identity["packages"])
    ) - PRODUCT_PACKAGES
    for package in unexpected_shared:
        if source_identity["packages"][package] != target_identity["packages"][package]:
            raise ComparisonError(f"source and target shared dependency differs: {package}")


def _compare_error(source: Any, target: Any, path: str, action_id: str) -> list[dict[str, Any]]:
    if source == target:
        return []
    return [
        {
            "action_id": action_id,
            "path": path,
            "comparison": "exact",
            "source": source,
            "target": target,
        }
    ]


def _observation_index(action_result: dict[str, Any]) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}
    for observation in action_result["observations"]:
        index = observation["index"]
        if index in indexed:
            raise ComparisonError(f"duplicate observed selector index: {index}")
        indexed[index] = observation
    return indexed


def _compare_action(
    action_spec: dict[str, Any],
    source_action: dict[str, Any] | None,
    target_action: dict[str, Any] | None,
    *,
    require_selector_match: bool = False,
) -> list[dict[str, Any]]:
    action_id = action_spec["action_id"]
    if source_action is None or target_action is None:
        return [
            {
                "action_id": action_id,
                "path": "action_presence",
                "comparison": "exact",
                "source": source_action is not None,
                "target": target_action is not None,
            }
        ]
    if source_action["status"] == "not_run" or target_action["status"] == "not_run":
        if source_action["status"] != target_action["status"]:
            return _compare_error(
                source_action["status"], target_action["status"], "action_status", action_id
            )
        return _compare_error(
            source_action.get("reason"), target_action.get("reason"), "action_not_run", action_id
        )
    if source_action["status"] == "product_error" or target_action["status"] == "product_error":
        if source_action["status"] != target_action["status"]:
            return _compare_error(
                source_action["status"], target_action["status"], "action_status", action_id
            )
        return _compare_error(
            source_action.get("error"),
            target_action.get("error"),
            "action_error",
            action_id,
        )

    source_observations = _observation_index(source_action)
    target_observations = _observation_index(target_action)
    diffs = []
    for index, observation_spec in enumerate(action_spec["observations"]):
        source_observation = source_observations.get(index)
        target_observation = target_observations.get(index)
        expected_kind = observation_spec["kind"]
        path = f"observations[{index}]"
        if source_observation is None or target_observation is None:
            diffs.append(
                {
                    "action_id": action_id,
                    "path": f"{path}.presence",
                    "comparison": "exact",
                    "source": source_observation is not None,
                    "target": target_observation is not None,
                }
            )
            continue
        if (
            source_observation["kind"] != expected_kind
            or target_observation["kind"] != expected_kind
        ):
            diffs.append(
                {
                    "action_id": action_id,
                    "path": f"{path}.kind",
                    "comparison": "exact",
                    "source": source_observation["kind"],
                    "target": target_observation["kind"],
                }
            )
            continue
        expected_selector = observation_spec.get("selector")
        # ASGI send observations have a single schema-fixed selector; result
        # artifacts carry only the resulting message_types value.
        if (
            require_selector_match
            and expected_selector is not None
            and expected_kind != "asgi_send"
            and (
                source_observation.get("selector") != expected_selector
                or target_observation.get("selector") != expected_selector
            )
        ):
            diffs.append(
                {
                    "action_id": action_id,
                    "path": f"{path}.selector",
                    "comparison": "exact",
                    "source": source_observation.get("selector"),
                    "target": target_observation.get("selector"),
                }
            )
            continue
        comparison = observation_spec["comparison"]
        if source_observation["values"] != target_observation["values"]:
            diffs.append(
                {
                    "action_id": action_id,
                    "path": f"{path}.values",
                    "comparison": comparison,
                    "source": source_observation["values"],
                    "target": target_observation["values"],
                }
            )

    expected_indices = set(range(len(action_spec["observations"])))
    for side, observations in (("source", source_observations), ("target", target_observations)):
        for extra_index in sorted(set(observations) - expected_indices):
            diffs.append(
                {
                    "action_id": action_id,
                    "path": f"observations[{extra_index}].unexpected_{side}",
                    "comparison": "exact",
                    "source": extra_index in source_observations,
                    "target": extra_index in target_observations,
                }
            )
    return diffs


def _compare_case(
    case_spec: dict[str, Any],
    source_case: dict[str, Any] | None,
    target_case: dict[str, Any] | None,
) -> dict[str, Any]:
    case_id = case_spec["case_id"]
    if source_case is None or target_case is None:
        return {
            "case_id": case_id,
            "outcome": "not_run",
            "reason": "a product result is missing this input case",
            "diffs": [],
        }
    if "unsupported" in {source_case["status"], target_case["status"]}:
        return {
            "case_id": case_id,
            "outcome": "not_run",
            "reason": "a product reported this case as unsupported",
            "diffs": [],
        }
    if source_case["status"] == "product_error" or target_case["status"] == "product_error":
        diffs = _compare_error(
            source_case.get("error"),
            target_case.get("error"),
            "case_error",
            "<case>",
        )
        return {"case_id": case_id, "outcome": "fail" if diffs else "pass", "diffs": diffs}

    source_actions = {action["action_id"]: action for action in source_case["actions"]}
    target_actions = {action["action_id"]: action for action in target_case["actions"]}
    expected_action_ids = [action["action_id"] for action in case_spec["actions"]]
    if len(source_actions) != len(source_case["actions"]) or len(target_actions) != len(
        target_case["actions"]
    ):
        raise ComparisonError(f"duplicate action result id in case {case_id}")
    diffs = []
    for action_spec in case_spec["actions"]:
        diffs.extend(
            _compare_action(
                action_spec,
                source_actions.get(action_spec["action_id"]),
                target_actions.get(action_spec["action_id"]),
            )
        )
    unexpected_source = set(source_actions) - set(expected_action_ids)
    unexpected_target = set(target_actions) - set(expected_action_ids)
    for action_id in sorted(unexpected_source | unexpected_target):
        diffs.append(
            {
                "action_id": action_id,
                "path": "unexpected_action",
                "comparison": "exact",
                "source": action_id in source_actions,
                "target": action_id in target_actions,
            }
        )
    return {"case_id": case_id, "outcome": "fail" if diffs else "pass", "diffs": diffs}


def _compare_case_v3(
    case_spec: dict[str, Any],
    source_case: dict[str, Any] | None,
    target_case: dict[str, Any] | None,
) -> dict[str, Any]:
    case_id = case_spec["case_id"]
    if source_case is None or target_case is None:
        return {
            "case_id": case_id,
            "outcome": "not_run",
            "reason": "a product result is missing this input case",
            "diffs": [],
        }

    diffs = _compare_error(
        source_case["construction_observation"],
        target_case["construction_observation"],
        "construction_observation",
        "<construction>",
    )
    source_actions = {action["action_id"]: action for action in source_case["actions"]}
    target_actions = {action["action_id"]: action for action in target_case["actions"]}
    expected_action_ids = [action["action_id"] for action in case_spec["actions"]]
    if len(source_actions) != len(source_case["actions"]) or len(target_actions) != len(
        target_case["actions"]
    ):
        raise ComparisonError(f"duplicate action result id in case {case_id}")
    for action_spec in case_spec["actions"]:
        diffs.extend(
            _compare_action(
                action_spec,
                source_actions.get(action_spec["action_id"]),
                target_actions.get(action_spec["action_id"]),
                require_selector_match=True,
            )
        )
    unexpected_source = set(source_actions) - set(expected_action_ids)
    unexpected_target = set(target_actions) - set(expected_action_ids)
    for action_id in sorted(unexpected_source | unexpected_target):
        diffs.append(
            {
                "action_id": action_id,
                "path": "unexpected_action",
                "comparison": "exact",
                "source": action_id in source_actions,
                "target": action_id in target_actions,
            }
        )
    return {"case_id": case_id, "outcome": "fail" if diffs else "pass", "diffs": diffs}


def _compare_warning_sidecar(
    phase_spec: dict[str, Any],
    source_phase: dict[str, Any] | None,
    target_phase: dict[str, Any] | None,
    *,
    phase_id: str,
) -> list[dict[str, Any]]:
    if source_phase is None or target_phase is None:
        return []

    selected = phase_spec.get("capture_warnings") is True
    source_has_warnings = "warnings" in source_phase
    target_has_warnings = "warnings" in target_phase
    if not selected:
        if source_has_warnings or target_has_warnings:
            raise ComparisonError("warning sidecar was emitted for a phase that did not select it")
        return []

    source_warnings = source_phase.get("warnings")
    target_warnings = target_phase.get("warnings")
    if not isinstance(source_warnings, list) or not isinstance(target_warnings, list):
        raise ComparisonError("selected warning sidecar is missing from a source or target phase")
    if source_warnings == target_warnings:
        return []
    return [
        {
            "action_id": phase_id,
            "path": "warnings",
            "comparison": "ordered",
            "source": source_warnings,
            "target": target_warnings,
        }
    ]


def _compare_case_v4(
    case_spec: dict[str, Any],
    source_case: dict[str, Any] | None,
    target_case: dict[str, Any] | None,
) -> dict[str, Any]:
    case_id = case_spec["case_id"]
    if source_case is None or target_case is None:
        return {
            "case_id": case_id,
            "outcome": "not_run",
            "reason": "a product result is missing this input case",
            "diffs": [],
        }

    source_construction = {
        key: value
        for key, value in source_case["construction_observation"].items()
        if key != "warnings"
    }
    target_construction = {
        key: value
        for key, value in target_case["construction_observation"].items()
        if key != "warnings"
    }
    diffs = _compare_error(
        source_construction,
        target_construction,
        "construction_observation",
        "<construction>",
    )
    diffs.extend(
        _compare_warning_sidecar(
            case_spec["construction_observation"],
            source_case["construction_observation"],
            target_case["construction_observation"],
            phase_id="<construction>",
        )
    )

    source_actions = {action["action_id"]: action for action in source_case["actions"]}
    target_actions = {action["action_id"]: action for action in target_case["actions"]}
    expected_action_ids = [action["action_id"] for action in case_spec["actions"]]
    if len(source_actions) != len(source_case["actions"]) or len(target_actions) != len(
        target_case["actions"]
    ):
        raise ComparisonError(f"duplicate action result id in case {case_id}")
    for action_spec in case_spec["actions"]:
        action_id = action_spec["action_id"]
        source_action = source_actions.get(action_id)
        target_action = target_actions.get(action_id)
        diffs.extend(
            _compare_warning_sidecar(
                action_spec,
                source_action,
                target_action,
                phase_id=action_id,
            )
        )
        diffs.extend(
            _compare_action(
                action_spec,
                source_action,
                target_action,
                require_selector_match=True,
            )
        )
    unexpected_source = set(source_actions) - set(expected_action_ids)
    unexpected_target = set(target_actions) - set(expected_action_ids)
    for action_id in sorted(unexpected_source | unexpected_target):
        diffs.append(
            {
                "action_id": action_id,
                "path": "unexpected_action",
                "comparison": "exact",
                "source": action_id in source_actions,
                "target": action_id in target_actions,
            }
        )
    return {"case_id": case_id, "outcome": "fail" if diffs else "pass", "diffs": diffs}


def compare_workflow_results(
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
    source_result_ref: dict[str, str],
    target_result_ref: dict[str, str],
    command: list[str],
) -> dict[str, Any]:
    expected_result_schema = RESULT_SCHEMA_IDS_BY_WORKFLOW.get(workflow.get("schema"))
    comparison_schema = COMPARISON_SCHEMA_IDS_BY_WORKFLOW.get(workflow.get("schema"))
    if expected_result_schema is None or comparison_schema is None:
        raise ComparisonError(f"unsupported workflow schema: {workflow.get('schema')!r}")
    for result in (source, target):
        if result.get("schema") != expected_result_schema:
            raise ComparisonError("source or target result uses a different workflow result schema")
    _validate_identity_pair(source, target, oracle_profile, target_profile)
    workload_ref = {
        "path": workflow["workload"]["file"],
        "sha256": workload_sha256,
    }
    if source["status"] != "completed" or target["status"] != "completed":
        raise ComparisonError("source and target runs must both complete before comparison")
    if source["infrastructure_errors"] or target["infrastructure_errors"]:
        raise ComparisonError("source or target result contains infrastructure errors")
    if (
        source["manifest"]["sha256"] != manifest_sha256
        or target["manifest"]["sha256"] != manifest_sha256
    ):
        raise ComparisonError("source and target results must use the current manifest digest")
    for result in (source, target):
        if result["input"]["path"] != input_path or result["input"]["sha256"] != input_sha256:
            raise ComparisonError("source and target results must use the same current input")
        if result["input"].get("schema") != workflow["schema"]:
            raise ComparisonError("source or target result uses a different workflow schema")
        if result["workload"]["path"] != workload_ref["path"]:
            raise ComparisonError("source and target results must use the same workload file")
        if result["workload"]["sha256"] != workload_ref["sha256"]:
            raise ComparisonError("source and target results must use the same workload digest")
        if result["workload"]["factory"] != workflow["workload"]["factory"]:
            raise ComparisonError("source or target result uses a different workload factory")

    source_cases = {case["case_id"]: case for case in source["cases"]}
    target_cases = {case["case_id"]: case for case in target["cases"]}
    if len(source_cases) != len(source["cases"]) or len(target_cases) != len(target["cases"]):
        raise ComparisonError("duplicate case result id")
    expected_case_ids = {case["case_id"] for case in workflow["cases"]}
    if set(source_cases) - expected_case_ids or set(target_cases) - expected_case_ids:
        raise ComparisonError("a result artifact contains a case absent from the input workflow")
    if workflow["schema"] in {WORKFLOW_SCHEMA_V4_ID, WORKFLOW_SCHEMA_V5_ID}:
        compare_case = _compare_case_v4
    elif workflow["schema"] == WORKFLOW_SCHEMA_V3_ID:
        compare_case = _compare_case_v3
    else:
        compare_case = _compare_case
    case_results = [
        compare_case(case, source_cases.get(case["case_id"]), target_cases.get(case["case_id"]))
        for case in workflow["cases"]
    ]
    outcomes = [case["outcome"] for case in case_results]
    return {
        "schema": comparison_schema,
        "run_id": str(uuid.uuid4()),
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "scope": "input-defined-slice",
        "manifest": {"path": "tests/fixtures/manifest.yaml", "sha256": manifest_sha256},
        "input": {
            "path": input_path,
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "source_result": source_result_ref,
        "target_result": target_result_ref,
        "command": {"argv": command, "cwd": "."},
        "status": "completed",
        "summary": {
            "selected": len(case_results),
            "passed": outcomes.count("pass"),
            "failed": outcomes.count("fail"),
            "not_run": outcomes.count("not_run"),
        },
        "cases": case_results,
        "infrastructure_errors": [],
    }
