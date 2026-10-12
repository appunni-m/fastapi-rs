"""Exact, selector-only comparison for isolated FastAPI CLI process results."""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.contract import ROOT, ContractError, read_json
from scripts.parity.process_contract import _process_selectors_for_case
from scripts.parity.process_worker import (
    PROCESS_RESULT_SCHEMA_ID,
    PROCESS_RESULT_SCHEMA_PATH,
    SELECTOR_CATALOG_PATH,
    _canonical_sha256,
    _profile_expectations,
)

PROCESS_COMPARISON_SCHEMA_ID = "fastapi-rs/python-process-comparison@1"
PROCESS_COMPARISON_SCHEMA_PATH = (
    ROOT / "tests/fixtures/schemas/python-process-comparison.schema.json"
)


class ProcessComparisonError(ContractError):
    """Process artifacts are unresolved, incomplete, or not profile-identical."""


def _validate_schema(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: error.message)
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise ProcessComparisonError(f"{label} does not match its schema: {detail}")


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def _validate_result(
    result: dict[str, Any],
    *,
    product: str,
    workflow: dict[str, Any],
    input_path: str,
    input_sha256: str,
    manifest_sha256: str,
) -> None:
    if not isinstance(result, dict):
        raise ProcessComparisonError(f"{product} process result must be an object")
    _validate_schema(result, PROCESS_RESULT_SCHEMA_PATH, f"{product} process result")
    if result.get("schema") != PROCESS_RESULT_SCHEMA_ID:
        raise ProcessComparisonError(f"{product} process result schema is unsupported")
    if result.get("product") != product:
        raise ProcessComparisonError(f"expected a {product} process result")
    if result.get("status") != "completed":
        detail = result.get("unresolved_reason") or result.get("infrastructure_errors")
        raise ProcessComparisonError(
            f"{product} process result is not completed; it cannot be compared: {detail}"
        )
    if result.get("manifest") != {
        "path": "tests/fixtures/manifest.yaml",
        "sha256": manifest_sha256,
    }:
        raise ProcessComparisonError(f"{product} process result uses a different manifest")
    if result.get("input") != {
        "path": input_path,
        "sha256": input_sha256,
        "schema": workflow["schema"],
    }:
        raise ProcessComparisonError(f"{product} process result uses a different workflow input")
    if result.get("infrastructure_errors") != []:
        raise ProcessComparisonError(f"{product} process result contains infrastructure errors")

    profile_id = workflow["profiles"][product]
    profile = result.get("profile")
    if profile != {"id": profile_id, "status": "resolved"}:
        raise ProcessComparisonError(
            f"{product} process result profile is unresolved or mismatched"
        )
    identity = result.get("identity")
    if not isinstance(identity, dict):
        raise ProcessComparisonError(f"{product} process result has no runtime identity")
    expected_identity_fields = {
        "profile_id",
        "profile_sha256",
        "python",
        "packages",
        "repositories",
        "entrypoint",
    }
    if product == "target":
        expected_identity_fields |= {
            "distribution",
            "version",
            "target_revision",
            "source_tree_sha256",
            "target_binary_sha256",
        }
    if set(identity) != expected_identity_fields:
        raise ProcessComparisonError(f"{product} runtime identity fields are not canonical")
    if result.get("command") != {
        "mode": product,
        "entrypoint": identity.get("entrypoint"),
    }:
        raise ProcessComparisonError(f"{product} command identity is inconsistent")
    expectations = _profile_expectations(product, profile_id)
    if identity.get("profile_id") != profile_id:
        raise ProcessComparisonError(f"{product} runtime identity names a different profile")
    if identity.get("profile_sha256") != _canonical_sha256(expectations):
        raise ProcessComparisonError(f"{product} runtime identity profile digest differs")
    if identity.get("packages") != expectations["packages"]:
        raise ProcessComparisonError(f"{product} runtime packages differ from the pinned profile")

    python = identity.get("python")
    if not isinstance(python, dict):
        raise ProcessComparisonError(f"{product} runtime identity has no Python identity")
    if set(python) != {"implementation", "version", "path", "sha256"}:
        raise ProcessComparisonError(f"{product} Python identity fields are not canonical")
    if {key: python.get(key) for key in ("implementation", "version")} != expectations["python"]:
        raise ProcessComparisonError(f"{product} Python runtime differs from the pinned profile")
    if not isinstance(python.get("path"), str) or not python["path"].startswith("/"):
        raise ProcessComparisonError(f"{product} Python executable path is not absolute")
    if not _is_sha256(python.get("sha256")):
        raise ProcessComparisonError(f"{product} Python executable digest is malformed")

    entrypoint = identity.get("entrypoint")
    if not isinstance(entrypoint, dict):
        raise ProcessComparisonError(f"{product} runtime identity has no CLI entrypoint")
    if not isinstance(entrypoint.get("path"), str) or not entrypoint["path"].startswith("/"):
        raise ProcessComparisonError(f"{product} CLI entrypoint path is not absolute")
    if not _is_sha256(entrypoint.get("sha256")):
        raise ProcessComparisonError(f"{product} CLI entrypoint digest is malformed")

    repositories = identity.get("repositories")
    if not isinstance(repositories, dict):
        raise ProcessComparisonError(f"{product} repository identities are missing")
    expected_repository_names = set(expectations["repositories"])
    if product == "target":
        expected_repository_names.add("fastapi_rs")
    if set(repositories) != expected_repository_names:
        raise ProcessComparisonError(f"{product} repository identity fields are not canonical")
    for name, revision in expectations["repositories"].items():
        if repositories.get(name) != revision:
            raise ProcessComparisonError(
                f"{product} repository revision differs from its pinned profile: {name}"
            )
    if product == "target":
        fastapi_rs_revision = repositories.get("fastapi_rs")
        if (
            not isinstance(fastapi_rs_revision, str)
            or re.fullmatch(r"[a-f0-9]{40}", fastapi_rs_revision) is None
        ):
            raise ProcessComparisonError("target FastAPI-RS source revision is missing")
        if identity.get("distribution") != "fastapi-rs":
            raise ProcessComparisonError("target runtime is not the FastAPI-RS distribution")
        if identity.get("version") != expectations["target_version"]:
            raise ProcessComparisonError("target FastAPI-RS version differs from its profile")
        if identity.get("target_revision") != fastapi_rs_revision:
            raise ProcessComparisonError("target source revision identity is inconsistent")
        for digest_name in ("source_tree_sha256", "target_binary_sha256"):
            if not _is_sha256(identity.get(digest_name)):
                raise ProcessComparisonError(f"target {digest_name} is missing or malformed")


def _validate_stream(value: Any, *, case_id: str, selector: str) -> bytes:
    if not isinstance(value, dict) or value.get("encoding") != "base64":
        raise ProcessComparisonError(f"{case_id} {selector} is not a base64 byte record")
    encoded = value.get("data")
    if not isinstance(encoded, str):
        raise ProcessComparisonError(f"{case_id} {selector} has no base64 payload")
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ProcessComparisonError(f"{case_id} {selector} has invalid base64") from exc
    if base64.b64encode(decoded).decode("ascii") != encoded:
        raise ProcessComparisonError(f"{case_id} {selector} base64 is not canonical")
    if value.get("length_bytes") != len(decoded):
        raise ProcessComparisonError(f"{case_id} {selector} byte length is inconsistent")
    if value.get("sha256") != hashlib.sha256(decoded).hexdigest():
        raise ProcessComparisonError(f"{case_id} {selector} digest is inconsistent")
    return decoded


def _observation_map(case: dict[str, Any], case_id: str) -> dict[str, Any]:
    observations = case.get("observations")
    if not isinstance(observations, list):
        raise ProcessComparisonError(f"{case_id} process observations are missing")
    indexed: dict[str, Any] = {}
    for observation in observations:
        if not isinstance(observation, dict):
            raise ProcessComparisonError(f"{case_id} contains a malformed observation")
        selector = observation.get("selector")
        if not isinstance(selector, str) or selector in indexed:
            raise ProcessComparisonError(f"{case_id} contains duplicate or malformed selectors")
        if set(observation) != {"selector", "value"}:
            raise ProcessComparisonError(f"{case_id} observation contains unselected fields")
        indexed[selector] = observation["value"]
    return indexed


def _stream_summary(value: dict[str, Any]) -> dict[str, Any]:
    return {"sha256": value["sha256"], "length_bytes": value["length_bytes"]}


def _selector_catalog() -> dict[str, str]:
    catalog = read_json(SELECTOR_CATALOG_PATH)
    return {
        row["id"]: row.get("workflow_support")
        for row in catalog.get("selectors", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _validate_case_command(
    result_case: dict[str, Any],
    specification: dict[str, Any],
    identity: dict[str, Any],
    product: str,
) -> None:
    case_id = specification["case_id"]
    entrypoint = identity["entrypoint"]["path"]
    expected_command = {
        "argv": [entrypoint, *specification["argv"][1:]],
        "cwd": {"kind": "isolated-empty"},
        "environment": {
            "set": specification["environment"]["set"],
            "unset": specification["environment"]["unset"],
            "inherited": False,
        },
    }
    if result_case.get("command") != expected_command:
        raise ProcessComparisonError(
            f"{product} case command does not match the input specification: {case_id}"
        )
    if result_case.get("timeout_seconds") != specification["timeout_seconds"]:
        raise ProcessComparisonError(f"{product} case timeout differs from input: {case_id}")


def _validate_cases(
    workflow: dict[str, Any], source: dict[str, Any], target: dict[str, Any]
) -> list[dict[str, Any]]:
    source_cases = source.get("cases")
    target_cases = target.get("cases")
    specifications = workflow.get("cases")
    if not isinstance(source_cases, list) or not isinstance(target_cases, list):
        raise ProcessComparisonError("process result case arrays are missing")
    if (
        not isinstance(specifications, list)
        or len(source_cases) != len(specifications)
        or len(target_cases) != len(specifications)
    ):
        raise ProcessComparisonError("process source/target case counts differ from the input")

    selector_support = _selector_catalog()
    source_identity = source["identity"]
    target_identity = target["identity"]
    comparisons: list[dict[str, Any]] = []
    for specification, source_case, target_case in zip(
        specifications, source_cases, target_cases, strict=True
    ):
        case_id = specification["case_id"]
        if source_case.get("case_id") != case_id or target_case.get("case_id") != case_id:
            raise ProcessComparisonError("process source/target case order differs from the input")
        _validate_case_command(source_case, specification, source_identity, "oracle")
        _validate_case_command(target_case, specification, target_identity, "target")
        if source_case.get("status") != "completed" or target_case.get("status") != "completed":
            raise ProcessComparisonError(f"process case is incomplete: {case_id}")
        if (
            type(source_case.get("exit_code")) is not int
            or type(target_case.get("exit_code")) is not int
        ):
            raise ProcessComparisonError(f"process exit code is missing: {case_id}")
        source_observations = _observation_map(source_case, case_id)
        target_observations = _observation_map(target_case, case_id)
        selected = _process_selectors_for_case(specification, selector_support)
        expected_order = [
            selector for selector in specification["observations"] if selector in selected
        ]
        if not expected_order:
            raise ProcessComparisonError(
                f"process case has no comparable selected selectors: {case_id}"
            )
        if (
            list(source_observations) != expected_order
            or list(target_observations) != expected_order
        ):
            raise ProcessComparisonError(
                f"process case observations differ from selected input selectors: {case_id}"
            )
        if "process.exit_code" in selected:
            if source_observations["process.exit_code"] != source_case["exit_code"]:
                raise ProcessComparisonError(
                    f"source exit-code selector is inconsistent: {case_id}"
                )
            if target_observations["process.exit_code"] != target_case["exit_code"]:
                raise ProcessComparisonError(
                    f"target exit-code selector is inconsistent: {case_id}"
                )

        observation_comparisons: list[dict[str, Any]] = []
        for selector in expected_order:
            source_value = source_observations[selector]
            target_value = target_observations[selector]
            if selector == "process.exit_code":
                if type(source_value) is not int or type(target_value) is not int:
                    raise ProcessComparisonError(
                        f"{case_id} exit-code observation is not an integer"
                    )
                source_summary: Any = source_value
                target_summary: Any = target_value
                equal = source_value == target_value
            else:
                source_bytes = _validate_stream(source_value, case_id=case_id, selector=selector)
                target_bytes = _validate_stream(target_value, case_id=case_id, selector=selector)
                source_summary = _stream_summary(source_value)
                target_summary = _stream_summary(target_value)
                equal = source_bytes == target_bytes
            observation_comparisons.append(
                {
                    "selector": selector,
                    "comparison": "exact",
                    "equal": equal,
                    "source": source_summary,
                    "target": target_summary,
                }
            )
        case_equal = all(row["equal"] for row in observation_comparisons)
        comparisons.append(
            {
                "case_id": case_id,
                "status": "matched" if case_equal else "mismatched",
                "observations": observation_comparisons,
            }
        )
    return comparisons


def compare_process_workflow_results(
    *,
    workflow: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    manifest_sha256: str,
    input_path: str,
    input_sha256: str,
    source_result_ref: dict[str, Any],
    target_result_ref: dict[str, Any],
    command: list[str],
) -> dict[str, Any]:
    """Compare only the selector projections requested by the process input."""
    _validate_result(
        source,
        product="oracle",
        workflow=workflow,
        input_path=input_path,
        input_sha256=input_sha256,
        manifest_sha256=manifest_sha256,
    )
    _validate_result(
        target,
        product="target",
        workflow=workflow,
        input_path=input_path,
        input_sha256=input_sha256,
        manifest_sha256=manifest_sha256,
    )
    for label, reference, result, product in (
        ("source", source_result_ref, source, "oracle"),
        ("target", target_result_ref, target, "target"),
    ):
        if not isinstance(reference, dict):
            raise ProcessComparisonError(f"{label} result reference is malformed")
        if (
            reference.get("run_id") != result.get("run_id")
            or reference.get("product") != product
            or not isinstance(reference.get("path"), str)
            or not _is_sha256(reference.get("sha256"))
        ):
            raise ProcessComparisonError(f"{label} result reference does not bind to its artifact")
        result_path = Path(reference["path"])
        if result_path.is_absolute():
            raise ProcessComparisonError(
                f"{label} result reference path must be repository-relative"
            )
        resolved_result_path = (ROOT / result_path).resolve()
        artifact_root = (ROOT / "parity-results").resolve()
        try:
            resolved_result_path.relative_to(artifact_root)
        except ValueError as exc:
            raise ProcessComparisonError(
                f"{label} result reference must point into parity-results/"
            ) from exc
        try:
            artifact_bytes = resolved_result_path.read_bytes()
        except OSError as exc:
            raise ProcessComparisonError(f"{label} result artifact cannot be read") from exc
        if hashlib.sha256(artifact_bytes).hexdigest() != reference["sha256"]:
            raise ProcessComparisonError(f"{label} result digest does not match its artifact")
        try:
            artifact_value = json.loads(artifact_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProcessComparisonError(f"{label} result artifact is not valid JSON") from exc
        if artifact_value != result:
            raise ProcessComparisonError(f"{label} result object differs from its artifact")
    if (
        not isinstance(command, list)
        or not command
        or any(not isinstance(part, str) or not part for part in command)
    ):
        raise ProcessComparisonError("comparison command must be a non-empty argv array")
    source_identity = source["identity"]
    target_identity = target["identity"]
    for key in ("implementation", "version"):
        if source_identity["python"][key] != target_identity["python"][key]:
            raise ProcessComparisonError("source and target process Python runtimes differ")
    shared_names = set(source_identity["packages"]) & set(target_identity["packages"])
    for name in shared_names - {"fastapi", "starlette", "fastapi-rs", "starlette-rs-py"}:
        if source_identity["packages"][name] != target_identity["packages"][name]:
            raise ProcessComparisonError(f"source and target shared package differs: {name}")

    cases = _validate_cases(workflow, source, target)
    matched = sum(case["status"] == "matched" for case in cases)
    mismatched = len(cases) - matched
    comparison = {
        "schema": PROCESS_COMPARISON_SCHEMA_ID,
        "comparison_id": str(uuid.uuid4()),
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "status": "matched" if mismatched == 0 else "mismatched",
        "manifest": {"path": "tests/fixtures/manifest.yaml", "sha256": manifest_sha256},
        "input": {
            "path": input_path,
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "source_result": source_result_ref,
        "target_result": target_result_ref,
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "matched": matched,
            "mismatched": mismatched,
        },
        "command": command,
    }
    _validate_schema(comparison, PROCESS_COMPARISON_SCHEMA_PATH, "process comparison")
    return comparison
