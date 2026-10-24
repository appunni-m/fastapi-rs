#!/usr/bin/env python3
"""Run exactly one source-mapped workflow selected by materialized-index ID."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from scripts.build_parity_inputs import read_recipe
from scripts.parity.comparator import SHARED_ORACLE_PACKAGES
from scripts.parity.contract import (
    API_WORKFLOW_SCHEMA_IDS,
    ROOT,
    ContractError,
    load_workflow,
    read_json,
    read_manifest,
    select_oracle_profile,
    select_target_profile,
    sha256_file,
)
from scripts.parity.fault_contracts import verification_mode
from scripts.parity.materialized import validate_materialized_input_index
from scripts.parity.process_contract import (
    ORACLE_PROCESS_CORE_PROFILE_ID,
    ORACLE_PROCESS_PROFILE_ID,
    PROCESS_WORKFLOW_SCHEMA_IDS,
    TARGET_PROCESS_PROFILE_ID,
    load_process_workflow,
)
from scripts.parity.source_identity import (
    fastapi_rs_runtime_source_scope_sha256,
    fastapi_rs_source_tree_sha256,
    indexed_parity_harness_source_scope_sha256,
)

MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
INDEXED_INDEX_SCHEMA = "fastapi-rs/materialized-input-index@12"
PROCESS_RESULT_DIR = ROOT / "parity-results/indexed"
PROFILE_RECEIPT_DIR = ROOT / "parity-results/indexed-profiles"
CASE_RECEIPT_DIR = ROOT / "parity-results/indexed-receipts"
PROFILE_RECEIPT_SCHEMA = "fastapi-rs/indexed-profile-receipt@2"
CASE_RECEIPT_SCHEMA = "fastapi-rs/indexed-parity-reuse-receipt@2"
PARITY_RESULTS_ROOT = (ROOT / "parity-results").resolve()

PROFILE_PATHS: dict[str | None, tuple[str, str]] = {
    None: (".venv-oracle/bin/python", ".venv-target/bin/python"),
    "standard-multipart": (
        ".venv-oracle-standard/bin/python",
        "target/standard-multipart/venv/bin/python",
    ),
    "testclient": (
        ".venv-oracle-testclient/bin/python",
        "target/testclient/venv/bin/python",
    ),
    "email-validation": (
        ".venv-oracle-email-validation/bin/python",
        "target/email-validation/venv/bin/python",
    ),
    "pydantic-extra-types": (
        ".venv-oracle-pydantic-extra-types/bin/python",
        "target/pydantic-extra-types/venv/bin/python",
    ),
    "templates": (
        ".venv-oracle-templates/bin/python",
        "target/templates/venv/bin/python",
    ),
    "telemetry": (
        ".venv-oracle-telemetry/bin/python",
        "target/telemetry/venv/bin/python",
    ),
    "json-serializers": (
        ".venv-oracle-json-serializers/bin/python",
        "target/json-serializers/venv/bin/python",
    ),
}
ORACLE_PREP_TARGETS = {
    None: "parity-prepare-oracle",
    "standard-multipart": "parity-prepare-oracle-standard",
    "testclient": "parity-prepare-oracle-testclient",
    "email-validation": "parity-prepare-oracle-email-validation",
    "pydantic-extra-types": "parity-prepare-oracle-pydantic-extra-types",
    "templates": "parity-prepare-oracle-templates",
    "telemetry": "parity-prepare-oracle-telemetry",
    "json-serializers": "parity-prepare-oracle-json-serializers",
}
TARGET_PREP_TARGETS = {
    None: "parity-prepare-target",
    "standard-multipart": "parity-prepare-target-standard-multipart",
    "testclient": "parity-prepare-target-testclient",
    "email-validation": "parity-prepare-target-email-validation",
    "pydantic-extra-types": "parity-prepare-target-pydantic-extra-types",
    "templates": "parity-prepare-target-templates",
    "telemetry": "parity-prepare-target-telemetry",
    "json-serializers": "parity-prepare-target-json-serializers",
}


def _git_revision(source: Path, label: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[a-f0-9]{40}", revision) is None:
        detail = completed.stderr.strip()
        raise ContractError(f"cannot identify {label} source revision: {detail}")
    return revision


def _run_json(step: str, arguments: list[str], *, timeout: int = 1800) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise ContractError(
            f"{step} failed with exit code {completed.returncode}:\n"
            f"{completed.stdout}{completed.stderr}"
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError(f"{step} returned invalid JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise ContractError(f"{step} returned a non-object result")
    return result


def _canonical_sha256(value: Any) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _profile_identity(
    *,
    python: Path,
    lane: str,
    profile: dict[str, Any],
    fastapi_source: Path,
    starlette_source: Path,
    target_source: Path,
    starlette_rs_source: Path,
    fault_injection_required: bool | None = None,
) -> dict[str, Any]:
    command = [
        str(python),
        "-m",
        "scripts.parity.profile_identity",
        lane,
        "--profile-json",
        json.dumps(profile, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
    ]
    if lane == "oracle":
        command.extend(
            ["--fastapi-source", str(fastapi_source), "--starlette-source", str(starlette_source)]
        )
    else:
        command.extend(
            [
                "--target-source",
                str(target_source),
                "--starlette-rs-source",
                str(starlette_rs_source),
            ]
        )
        if fault_injection_required is not None:
            command.extend(
                [
                    "--fault-injection-required",
                    "true" if fault_injection_required else "false",
                ]
            )
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["RUSTC_WRAPPER"] = ""
    environment["CARGO_BUILD_RUSTC_WRAPPER"] = ""
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise ContractError(
            f"{lane} profile identity probe failed with exit code {completed.returncode}:\n"
            f"{completed.stdout}{completed.stderr}"
        )
    try:
        identity = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError(f"{lane} profile identity probe returned invalid JSON: {exc}") from exc
    if not isinstance(identity, dict) or "identity_error" in identity:
        raise ContractError(
            f"{lane} profile identity probe returned an invalid identity: {identity}"
        )
    return identity


def _probe_profile_pair(
    *,
    oracle_python: Path,
    target_python: Path,
    oracle_profile: dict[str, Any],
    target_profile: dict[str, Any],
    fastapi_source: Path,
    starlette_source: Path,
    target_source: Path,
    starlette_rs_source: Path,
    fault_injection_required: bool | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    oracle_identity = _profile_identity(
        python=oracle_python,
        lane="oracle",
        profile=oracle_profile,
        fastapi_source=fastapi_source,
        starlette_source=starlette_source,
        target_source=target_source,
        starlette_rs_source=starlette_rs_source,
    )
    target_identity = _profile_identity(
        python=target_python,
        lane="target",
        profile=target_profile,
        fastapi_source=fastapi_source,
        starlette_source=starlette_source,
        target_source=target_source,
        starlette_rs_source=starlette_rs_source,
        fault_injection_required=fault_injection_required,
    )
    return oracle_identity, target_identity


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
            + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_artifact_ref(reference: Any, *, product: str) -> tuple[dict[str, Any], str] | None:
    if not isinstance(reference, dict):
        return None
    expected_keys = (
        {"path", "sha256", "run_id", "product"}
        if product != "comparison"
        else {
            "path",
            "sha256",
            "run_id",
        }
    )
    if set(reference) != expected_keys:
        return None
    relative_path = reference.get("path")
    if not isinstance(relative_path, str):
        return None
    artifact_path = (ROOT / relative_path).resolve()
    try:
        artifact_path.relative_to(PARITY_RESULTS_ROOT)
    except ValueError:
        return None
    if not artifact_path.is_file() or sha256_file(artifact_path) != reference.get("sha256"):
        return None
    try:
        artifact = read_json(artifact_path)
    except (OSError, ValueError, ContractError):
        return None
    if not isinstance(artifact, dict) or artifact.get("run_id") != reference.get("run_id"):
        return None
    if product != "comparison" and artifact.get("product") != product:
        return None
    return artifact, relative_path


def _target_execution_identity(
    identity: Any, *, runtime_source_scope_sha256: str
) -> dict[str, Any] | None:
    """Project a target identity onto the runtime sources and artifacts in scope."""
    if not isinstance(identity, dict):
        return None
    repositories = identity.get("repositories")
    packages = identity.get("packages")
    python = identity.get("python")
    platform = identity.get("platform")
    target_binary_sha256 = identity.get("target_binary_sha256")
    starlette_rs_revision = (
        repositories.get("starlette_rs") if isinstance(repositories, dict) else None
    )
    if (
        not isinstance(identity.get("distribution"), str)
        or not isinstance(identity.get("version"), str)
        or not isinstance(python, dict)
        or not isinstance(platform, dict)
        or not isinstance(packages, dict)
        or not all(
            isinstance(name, str) and isinstance(version, str) for name, version in packages.items()
        )
        or not isinstance(starlette_rs_revision, str)
        or not isinstance(runtime_source_scope_sha256, str)
        or re.fullmatch(r"[a-f0-9]{64}", runtime_source_scope_sha256) is None
        or not isinstance(target_binary_sha256, str)
        or re.fullmatch(r"[a-f0-9]{64}", target_binary_sha256) is None
    ):
        return None
    result = {
        "distribution": identity["distribution"],
        "version": identity["version"],
        "python": python,
        "platform": platform,
        "packages": packages,
        "starlette_rs_revision": starlette_rs_revision,
        "runtime_source_scope_sha256": runtime_source_scope_sha256,
        "target_binary_sha256": target_binary_sha256,
    }
    if "fault_injection_compiled" in identity:
        fault_injection_compiled = identity["fault_injection_compiled"]
        if type(fault_injection_compiled) is not bool:
            return None
        result["fault_injection_compiled"] = fault_injection_compiled
    return result


def _oracle_result_identity(identity: Any, workflow_schema: str) -> Any:
    """Add the result-schema-only null fault flag absent from oracle profile probes."""
    prefix = "fastapi-rs/python-asgi-workflow@"
    if isinstance(identity, dict) and workflow_schema.startswith(prefix):
        version = workflow_schema.removeprefix(prefix)
        if version.isdecimal() and int(version) >= 7:
            return {**identity, "fault_injection_compiled": None}
    return identity


def _case_result_matches(result: dict[str, Any], *, product: str, context: dict[str, Any]) -> bool:
    result_identity = result.get("identity")
    expected_identity = (
        context.get("target_execution_identity")
        if product == "target"
        else context.get("oracle_identity")
    )
    actual_identity = (
        _target_execution_identity(
            result_identity,
            runtime_source_scope_sha256=context.get("runtime_source_scope_sha256"),
        )
        if product == "target"
        else result_identity
    )
    if (
        result.get("product") != product
        or result.get("status") != "completed"
        or not isinstance(result.get("schema"), str)
    ):
        return False
    if actual_identity != expected_identity:
        return False
    input_identity = result.get("input")
    manifest_identity = result.get("manifest")
    if (
        not isinstance(input_identity, dict)
        or input_identity.get("sha256") != context["input_sha256"]
        or input_identity.get("schema") != context["workflow_schema"]
    ):
        return False
    if (
        not isinstance(manifest_identity, dict)
        or manifest_identity.get("path") != "tests/fixtures/manifest.yaml"
        or manifest_identity.get("sha256") != context["manifest_sha256"]
    ):
        return False
    workload = result.get("workload")
    if (
        not isinstance(workload, dict)
        or workload.get("path") != context["workload_path"]
        or workload.get("sha256") != context["workload_sha256"]
        or workload.get("factory") != context["workload_factory"]
    ):
        return False
    if result.get("infrastructure_errors"):
        return False
    cases = result.get("cases")
    return (
        isinstance(cases, list)
        and all(isinstance(case, dict) and isinstance(case.get("case_id"), str) for case in cases)
        and [case["case_id"] for case in cases] == context["selected_case_ids"]
    )


def _load_cached_case(
    receipt_path: Path,
    *,
    context: dict[str, Any],
    profile_context_sha256: str,
) -> dict[str, Any] | None:
    if not receipt_path.is_file():
        return None
    try:
        receipt = read_json(receipt_path)
    except (OSError, ValueError, ContractError):
        return None
    context_sha256 = _canonical_sha256(context)
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema") != CASE_RECEIPT_SCHEMA
        or receipt.get("status") != "passed"
        or receipt.get("context") != context
        or receipt.get("context_sha256") != context_sha256
        or receipt.get("profile_context_sha256") != profile_context_sha256
    ):
        return None

    oracle_ref = receipt.get("oracle_result")
    target_ref = receipt.get("target_result")
    comparison_ref = receipt.get("comparison_result")
    oracle_entry = _read_artifact_ref(oracle_ref, product="oracle")
    target_entry = _read_artifact_ref(target_ref, product="target")
    comparison_entry = _read_artifact_ref(comparison_ref, product="comparison")
    if oracle_entry is None or target_entry is None or comparison_entry is None:
        return None
    oracle_result, _ = oracle_entry
    target_result, _ = target_entry
    comparison_result, comparison_relative_path = comparison_entry
    if not _case_result_matches(oracle_result, product="oracle", context=context):
        return None
    if not _case_result_matches(target_result, product="target", context=context):
        return None
    if oracle_result.get("schema") != target_result.get("schema"):
        return None
    comparison_input = comparison_result.get("input")
    comparison_manifest = comparison_result.get("manifest")
    if (
        comparison_result.get("status") != "completed"
        or not isinstance(comparison_input, dict)
        or comparison_input.get("sha256") != context["input_sha256"]
        or comparison_input.get("schema") != context["workflow_schema"]
        or not isinstance(comparison_manifest, dict)
        or comparison_manifest.get("path") != "tests/fixtures/manifest.yaml"
        or comparison_manifest.get("sha256") != context["manifest_sha256"]
        or comparison_result.get("infrastructure_errors")
        or comparison_result.get("source_result") != oracle_ref
        or comparison_result.get("target_result") != target_ref
        or not _comparison_passed(comparison_result, len(context["selected_case_ids"]))
    ):
        return None
    comparison_cases = comparison_result.get("cases")
    if (
        not isinstance(comparison_cases, list)
        or not all(isinstance(case, dict) for case in comparison_cases)
        or [case["case_id"] for case in comparison_cases] != context["selected_case_ids"]
        or any(case.get("outcome") != "pass" for case in comparison_cases)
    ):
        return None
    return {
        "oracle_result": oracle_ref,
        "target_result": target_ref,
        "comparison_result": comparison_relative_path,
        "summary": comparison_result["summary"],
        "target_identity": target_result["identity"],
    }


def _run_prepare(
    *,
    oracle_target: str,
    target_target: str,
    fastapi_source: Path,
    starlette_source: Path,
    starlette_rs_source: Path,
) -> None:
    command = [
        "make",
        f"FASTAPI_SOURCE={fastapi_source}",
        f"STARLETTE_SOURCE={starlette_source}",
        f"STARLETTE_RS_SOURCE={starlette_rs_source}",
        oracle_target,
        target_target,
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False, timeout=3600)
    if completed.returncode != 0:
        raise ContractError(f"selected profile preparation failed: {' '.join(command)}")


def _select_workflow(
    workflow_id: str, *, fastapi_source: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = read_manifest()
    source_artifacts = manifest["source_artifacts"]
    index_ref = source_artifacts["materialized_input_index"]
    index = read_json(ROOT / index_ref["path"])
    if not isinstance(index, dict) or index.get("schema") != INDEXED_INDEX_SCHEMA:
        raise ContractError("manifest materialized input index uses an unsupported schema")
    rows = [row for row in index.get("workflows", []) if row.get("id") == workflow_id]
    if len(rows) != 1:
        raise ContractError(f"workflow ID must select exactly one indexed row: {workflow_id}")
    row = rows[0]
    input_path = (ROOT / row["input_path"]).resolve()
    recipe_path = (ROOT / row["recipe_path"]).resolve()
    if input_path.parent != (ROOT / "tests/fixtures/inputs/parity").resolve():
        raise ContractError("selected workflow input is outside the active parity input directory")
    if input_path.stem.replace("_", "-") != workflow_id:
        raise ContractError("workflow ID does not match its canonical input filename")
    if (
        recipe_path
        != (ROOT / "tests/fixtures/input-recipes/parity" / f"{input_path.stem}.yaml").resolve()
    ):
        raise ContractError("selected workflow recipe path is not paired with its input")

    atlas = read_json(ROOT / source_artifacts["compatibility_atlas"]["path"])
    backlog = read_json(ROOT / source_artifacts["fixture_backlog"]["path"])
    selector_catalog = read_json(ROOT / source_artifacts["observation_selector_catalog"]["path"])
    validate_materialized_input_index(
        index,
        atlas=atlas,
        backlog=backlog,
        selector_catalog=selector_catalog,
        fastapi_source=fastapi_source,
        workflow_ids={workflow_id},
    )

    recipe = read_recipe(recipe_path)
    canonical_json = json.dumps(recipe, indent=2, ensure_ascii=False) + "\n"
    if input_path.read_text(encoding="utf-8") != canonical_json:
        raise ContractError(
            "selected generated JSON is not the canonical serialization of its recipe"
        )
    if sha256_file(input_path) != row["input_sha256"]:
        raise ContractError("selected workflow input digest differs from the materialized index")
    if sha256_file(recipe_path) != row["recipe_sha256"]:
        raise ContractError("selected workflow recipe digest differs from the materialized index")

    if row.get("workflow_schema") in PROCESS_WORKFLOW_SCHEMA_IDS:
        workflow, loaded_path, _ = load_process_workflow(input_path, source_root=fastapi_source)
        if loaded_path != input_path or row["workflow_schema"] != workflow["schema"]:
            raise ContractError(
                "selected process workflow schema or path differs from its index row"
            )
    else:
        workflow, loaded_path, _, workload = load_workflow(input_path, source_root=fastapi_source)
        if (
            loaded_path != input_path
            or workload.relative_to(ROOT).as_posix() != row["workload_path"]
        ):
            raise ContractError("selected workflow workload binding differs from its index row")
        if sha256_file(workload) != row["workload_sha256"]:
            raise ContractError("selected workflow workload digest differs from its index row")
    if [case["case_id"] for case in workflow["cases"]] != row["case_ids"]:
        raise ContractError("selected workflow case order differs from its materialized index")
    return manifest, {"row": row, "workflow": workflow, "input": input_path}


def _profile_extension(
    workflow: dict[str, Any], row: dict[str, Any], requested: str | None
) -> str | None:
    if workflow["schema"] in PROCESS_WORKFLOW_SCHEMA_IDS:
        if requested is not None:
            raise ContractError("process workflow profiles are declared by the process input")
        return None
    if workflow["schema"] not in API_WORKFLOW_SCHEMA_IDS:
        embedded = workflow.get("oracle_profile_extension")
        if embedded != row.get("oracle_profile_extension"):
            raise ContractError("selected workflow profile extension differs from its index")
        if requested is not None and requested != embedded:
            raise ContractError("requested profile extension differs from the ASGI workflow input")
        return embedded
    return requested


def _select_cases(
    workflow: dict[str, Any], requested_case_ids: list[str]
) -> tuple[list[dict[str, Any]], list[str]]:
    cases = workflow["cases"]
    available_case_ids = [case["case_id"] for case in cases]
    if not requested_case_ids:
        return cases, available_case_ids
    if len(requested_case_ids) != len(set(requested_case_ids)):
        raise ContractError("case selection repeats a case ID")
    requested = set(requested_case_ids)
    unknown_case_ids = requested - set(available_case_ids)
    if unknown_case_ids:
        raise ContractError(
            "case selection contains IDs outside the indexed workflow: "
            + ", ".join(sorted(unknown_case_ids))
        )
    selected_cases = [case for case in cases if case["case_id"] in requested]
    return selected_cases, [case["case_id"] for case in selected_cases]


def _materialize_case_selection(
    *,
    workflow_id: str,
    indexed_input_path: Path,
    selected_case_ids: list[str],
    is_process: bool,
) -> Path:
    input_data = read_json(indexed_input_path)
    if not isinstance(input_data, dict) or not isinstance(input_data.get("cases"), list):
        raise ContractError("indexed workflow input has no case list")
    selected_case_id_set = set(selected_case_ids)
    input_data["cases"] = [
        case for case in input_data["cases"] if case.get("case_id") in selected_case_id_set
    ]
    if [case.get("case_id") for case in input_data["cases"]] != selected_case_ids:
        raise ContractError("selected input cases differ from the validated indexed workflow")

    run_id = uuid.uuid4().hex
    if is_process:
        selected_input_path = (
            ROOT / "tests/fixtures/inputs/parity" / f"case-selection-{run_id}.json"
        )
    else:
        selected_input_path = PROCESS_RESULT_DIR / workflow_id / run_id / "input.json"
        selected_input_path.parent.mkdir(parents=True, exist_ok=False)
    serialized = json.dumps(input_data, indent=2, ensure_ascii=False) + "\n"
    try:
        with selected_input_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
    except OSError as exc:
        raise ContractError(f"cannot materialize selected workflow input: {exc}") from exc
    return selected_input_path


def _check_target_identity(
    result: dict[str, Any],
    *,
    fastapi_revision: str,
    source_digest: str,
    starlette_rs_revision: str,
    runtime_source_scope_sha256: str,
) -> dict[str, str]:
    identity = result.get("identity")
    repositories = identity.get("repositories") if isinstance(identity, dict) else None
    if not isinstance(identity, dict) or not isinstance(repositories, dict):
        raise ContractError("target result did not report runtime and repository identities")
    if identity.get("target_revision") != fastapi_revision:
        raise ContractError("target result FastAPI-RS revision differs from the current checkout")
    if repositories.get("fastapi_rs") != fastapi_revision:
        raise ContractError("target result has inconsistent FastAPI-RS revision fields")
    if repositories.get("starlette_rs") != starlette_rs_revision:
        raise ContractError("target result Starlette-RS revision differs from its source checkout")
    if identity.get("source_tree_sha256") != source_digest:
        raise ContractError("target result source-tree digest differs from current source trees")
    binary_digest = identity.get("target_binary_sha256")
    if not isinstance(binary_digest, str) or re.fullmatch(r"[a-f0-9]{64}", binary_digest) is None:
        raise ContractError("target result compiled-extension digest is missing or malformed")
    return {
        "target_revision": fastapi_revision,
        "starlette_rs_revision": starlette_rs_revision,
        "source_tree_sha256": source_digest,
        "runtime_source_scope_sha256": runtime_source_scope_sha256,
        "target_binary_sha256": binary_digest,
    }


def _artifact(result: dict[str, Any], step: str) -> str:
    value = result.get("artifact")
    if not isinstance(value, str):
        raise ContractError(f"{step} did not report an immutable result artifact")
    return value


def _comparison_passed(result: dict[str, Any], count: int) -> bool:
    summary = result.get("summary")
    return (
        result.get("status") == "completed"
        and isinstance(summary, dict)
        and summary.get("selected") == count
        and summary.get("passed") == count
        and summary.get("failed") == 0
        and summary.get("not_run") == 0
    )


def _profile_context(
    *,
    profile_extension: str | None,
    starlette_rs_revision: str,
    runtime_source_scope_sha256: str,
    oracle_profile: dict[str, Any],
    target_profile: dict[str, Any],
    oracle_identity: dict[str, Any],
    target_identity: dict[str, Any],
) -> dict[str, Any]:
    target_execution_identity = _target_execution_identity(
        target_identity, runtime_source_scope_sha256=runtime_source_scope_sha256
    )
    if target_execution_identity is None:
        raise ContractError("target profile has no valid scoped execution identity")
    return {
        "profile_extension": profile_extension,
        "starlette_rs_revision": starlette_rs_revision,
        "runtime_source_scope_sha256": runtime_source_scope_sha256,
        "oracle_profile": oracle_profile,
        "target_profile": target_profile,
        "oracle_identity": oracle_identity,
        "target_execution_identity": target_execution_identity,
    }


def _profile_receipt_matches(path: Path, context: dict[str, Any]) -> bool:
    if not path.is_file():
        return False
    try:
        receipt = read_json(path)
    except (OSError, ValueError, ContractError):
        return False
    context_sha256 = _canonical_sha256(context)
    return (
        isinstance(receipt, dict)
        and receipt.get("schema") == PROFILE_RECEIPT_SCHEMA
        and receipt.get("status") == "prepared"
        and receipt.get("context") == context
        and receipt.get("context_sha256") == context_sha256
    )


def _write_profile_receipt(path: Path, context: dict[str, Any]) -> None:
    _write_receipt(
        path,
        {
            "schema": PROFILE_RECEIPT_SCHEMA,
            "status": "prepared",
            "context": context,
            "context_sha256": _canonical_sha256(context),
        },
    )


def _artifact_reference(path: str, *, product: str | None) -> dict[str, str]:
    artifact_path = (ROOT / path).resolve()
    try:
        artifact_path.relative_to(PARITY_RESULTS_ROOT)
        relative_path = artifact_path.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise ContractError("parity artifact reference is outside parity-results/") from exc
    artifact = read_json(artifact_path)
    if not isinstance(artifact, dict):
        raise ContractError("parity artifact must contain a JSON object")
    run_id = artifact.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ContractError("parity artifact has no immutable run ID")
    reference = {
        "path": relative_path,
        "sha256": sha256_file(artifact_path),
        "run_id": run_id,
    }
    if product is not None:
        if artifact.get("product") != product:
            raise ContractError(f"parity artifact is not a {product} result")
        reference["product"] = product
    return reference


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--id", required=True, help="exact workflow ID from materialized-input-index"
    )
    parser.add_argument("--fastapi-source", type=Path, default=ROOT.parent / "fastapi")
    parser.add_argument("--starlette-source", type=Path, default=ROOT.parent / "starlette")
    parser.add_argument("--starlette-rs-source", type=Path, default=ROOT.parent / "starlette-rs")
    parser.add_argument("--target-source", type=Path, default=ROOT)
    parser.add_argument(
        "--profile-extension",
        choices=tuple(PROFILE_PATHS.keys())[1:],
        help="required when a direct API workflow uses a non-core package profile",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="run one indexed case; repeat to select a small case subset",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="validate one indexed workflow without running it"
    )
    prepare = parser.add_mutually_exclusive_group()
    prepare.add_argument(
        "--prepare",
        action="store_true",
        help="force preparation of this workflow's oracle and target profiles",
    )
    prepare.add_argument(
        "--prepare-if-needed",
        action="store_true",
        help="reuse a profile receipt when the scoped runtime and oracle identities match",
    )
    parser.add_argument(
        "--no-reuse", action="store_true", help="execute selected cases even when receipts match"
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    fastapi_source = args.fastapi_source.resolve()
    starlette_source = args.starlette_source.resolve()
    starlette_rs_source = args.starlette_rs_source.resolve()
    target_source = args.target_source.resolve()
    manifest, selected = _select_workflow(args.id, fastapi_source=fastapi_source)
    workflow = selected["workflow"]
    row = selected["row"]
    indexed_workflow_path = selected["input"]
    indexed_case_ids = [case["case_id"] for case in workflow["cases"]]
    selected_cases, selected_case_ids = _select_cases(workflow, args.case_id)
    case_filter_applied = len(selected_case_ids) != len(indexed_case_ids)
    if case_filter_applied:
        workflow = {**workflow, "cases": selected_cases}
    workflow_path = indexed_workflow_path
    schema = workflow["schema"]
    is_process = schema in PROCESS_WORKFLOW_SCHEMA_IDS
    is_api = schema in API_WORKFLOW_SCHEMA_IDS
    extension = _profile_extension(workflow, row, args.profile_extension)
    if extension not in PROFILE_PATHS:
        raise ContractError(f"workflow selects an unsupported package profile: {extension}")
    if args.check_only:
        print(
            json.dumps(
                {
                    "status": "valid",
                    "workflow_id": args.id,
                    "schema": schema,
                    "indexed_case_count": len(indexed_case_ids),
                    "case_count": len(selected_case_ids),
                    "selected_case_ids": selected_case_ids,
                    "profile_extension": extension,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    oracle_extension = extension
    target_extension = extension
    if is_process:
        oracle_profile = workflow["profiles"]["oracle"]
        if oracle_profile == ORACLE_PROCESS_CORE_PROFILE_ID:
            oracle_extension = None
        elif oracle_profile == ORACLE_PROCESS_PROFILE_ID:
            oracle_extension = "standard-multipart"
        else:
            raise ContractError(f"unsupported process oracle profile: {oracle_profile}")
        if workflow["profiles"]["target"] != TARGET_PROCESS_PROFILE_ID:
            raise ContractError("process workflow target profile differs from the pinned target")
        target_extension = None

    oracle_python = ROOT / PROFILE_PATHS[oracle_extension][0]
    target_python = ROOT / PROFILE_PATHS[target_extension][1]
    if case_filter_applied and not is_api:
        workflow_path = _materialize_case_selection(
            workflow_id=args.id,
            indexed_input_path=indexed_workflow_path,
            selected_case_ids=selected_case_ids,
            is_process=is_process,
        )
    fault_selected = not is_process and any(
        verification_mode(case) == "fault-contract" for case in workflow["cases"]
    )
    target_prepare = (
        "fault-injection-build" if fault_selected else TARGET_PREP_TARGETS[target_extension]
    )
    if fault_selected:
        target_python = ROOT / "target/fault-injection/venv/bin/python"
    profiles_present = oracle_python.is_file() and target_python.is_file()
    profiles_prepared_this_run = False
    if args.prepare or (args.prepare_if_needed and not profiles_present):
        _run_prepare(
            oracle_target=ORACLE_PREP_TARGETS[oracle_extension],
            target_target=target_prepare,
            fastapi_source=fastapi_source,
            starlette_source=starlette_source,
            starlette_rs_source=starlette_rs_source,
        )
        profiles_prepared_this_run = True
    for label, python in (("oracle", oracle_python), ("target", target_python)):
        if not python.is_file():
            prepare = ORACLE_PREP_TARGETS[oracle_extension] if label == "oracle" else target_prepare
            raise ContractError(f"{label} profile is not prepared; run make {prepare}")

    target_revision = _git_revision(target_source, "FastAPI-RS")
    starlette_rs_revision = _git_revision(starlette_rs_source, "Starlette-RS")
    target_source_digest = fastapi_rs_source_tree_sha256(target_source, starlette_rs_source)
    runtime_source_scope_sha256 = fastapi_rs_runtime_source_scope_sha256(
        target_source, starlette_rs_source
    )
    harness_source_scope_sha256 = indexed_parity_harness_source_scope_sha256(ROOT)
    indexed_input_sha256 = sha256_file(indexed_workflow_path)
    input_sha256 = sha256_file(workflow_path)
    recipe_path = ROOT / row["recipe_path"]
    recipe_sha256 = sha256_file(recipe_path)
    manifest_sha256 = sha256_file(MANIFEST_PATH)
    index_path = ROOT / manifest["source_artifacts"]["materialized_input_index"]["path"]
    index_sha256 = sha256_file(index_path)
    workload_path = None if is_process else ROOT / row["workload_path"]
    workload_sha256 = None if workload_path is None else sha256_file(workload_path)

    profile_context = None
    profile_context_sha256 = None
    profile_receipt_path = None
    case_context = None
    case_receipt_path = None
    oracle_profile_identity = None
    target_profile_identity = None
    profile_receipt_trusted = False
    if not is_process:
        oracle_profile = select_oracle_profile(manifest, oracle_extension)
        target_profile = {
            "python": manifest["oracle_profile"]["python"],
            "shared_runtime_packages": {
                name: version
                for name, version in manifest["oracle_profile"]["packages"].items()
                if name in SHARED_ORACLE_PACKAGES
            },
            "target": select_target_profile(manifest, target_extension),
        }
        fault_identity_required = None
        if schema.startswith("fastapi-rs/python-asgi-workflow@"):
            schema_version = int(schema.rsplit("@", 1)[1])
            if schema_version >= 7:
                fault_identity_required = fault_selected

        def probe_pair() -> tuple[dict[str, Any], dict[str, Any]]:
            return _probe_profile_pair(
                oracle_python=oracle_python,
                target_python=target_python,
                oracle_profile=oracle_profile,
                target_profile=target_profile,
                fastapi_source=fastapi_source,
                starlette_source=starlette_source,
                target_source=target_source,
                starlette_rs_source=starlette_rs_source,
                fault_injection_required=fault_identity_required,
            )

        try:
            oracle_profile_identity, target_profile_identity = probe_pair()
        except ContractError:
            if not args.prepare_if_needed or profiles_prepared_this_run:
                raise
            _run_prepare(
                oracle_target=ORACLE_PREP_TARGETS[oracle_extension],
                target_target=target_prepare,
                fastapi_source=fastapi_source,
                starlette_source=starlette_source,
                starlette_rs_source=starlette_rs_source,
            )
            profiles_prepared_this_run = True
            oracle_profile_identity, target_profile_identity = probe_pair()

        target_repositories = target_profile_identity.get("repositories")
        if (
            target_profile_identity.get("target_revision") != target_revision
            or target_profile_identity.get("source_tree_sha256") != target_source_digest
            or not isinstance(target_repositories, dict)
            or target_repositories.get("starlette_rs") != starlette_rs_revision
        ):
            raise ContractError("profile identity probe differs from the current source identities")

        profile_context = _profile_context(
            profile_extension=extension,
            starlette_rs_revision=starlette_rs_revision,
            runtime_source_scope_sha256=runtime_source_scope_sha256,
            oracle_profile=oracle_profile,
            target_profile=target_profile,
            oracle_identity=oracle_profile_identity,
            target_identity=target_profile_identity,
        )
        profile_context_sha256 = _canonical_sha256(profile_context)
        profile_receipt_path = PROFILE_RECEIPT_DIR / f"{profile_context_sha256}.json"
        if args.prepare_if_needed and not profiles_prepared_this_run:
            if not _profile_receipt_matches(profile_receipt_path, profile_context):
                _run_prepare(
                    oracle_target=ORACLE_PREP_TARGETS[oracle_extension],
                    target_target=target_prepare,
                    fastapi_source=fastapi_source,
                    starlette_source=starlette_source,
                    starlette_rs_source=starlette_rs_source,
                )
                profiles_prepared_this_run = True
                oracle_profile_identity, target_profile_identity = probe_pair()
                target_repositories = target_profile_identity.get("repositories")
                if (
                    target_profile_identity.get("target_revision") != target_revision
                    or target_profile_identity.get("source_tree_sha256") != target_source_digest
                    or not isinstance(target_repositories, dict)
                    or target_repositories.get("starlette_rs") != starlette_rs_revision
                ):
                    raise ContractError(
                        "prepared profile identity differs from current source identities"
                    )
                profile_context = _profile_context(
                    profile_extension=extension,
                    starlette_rs_revision=starlette_rs_revision,
                    runtime_source_scope_sha256=runtime_source_scope_sha256,
                    oracle_profile=oracle_profile,
                    target_profile=target_profile,
                    oracle_identity=oracle_profile_identity,
                    target_identity=target_profile_identity,
                )
                profile_context_sha256 = _canonical_sha256(profile_context)
                profile_receipt_path = PROFILE_RECEIPT_DIR / f"{profile_context_sha256}.json"

        profile_receipt_trusted = _profile_receipt_matches(profile_receipt_path, profile_context)
        if profiles_prepared_this_run:
            _write_profile_receipt(profile_receipt_path, profile_context)

        case_context = {
            "workflow_id": args.id,
            "workflow_schema": schema,
            "selected_case_ids": selected_case_ids,
            "profile_extension": extension,
            "profile_context_sha256": profile_context_sha256,
            "starlette_rs_revision": starlette_rs_revision,
            "runtime_source_scope_sha256": runtime_source_scope_sha256,
            "harness_source_scope_sha256": harness_source_scope_sha256,
            "manifest_sha256": manifest_sha256,
            "index_sha256": index_sha256,
            "indexed_input_sha256": indexed_input_sha256,
            "input_sha256": input_sha256,
            "recipe_sha256": recipe_sha256,
            "workload_sha256": workload_sha256,
            "oracle_identity": _oracle_result_identity(oracle_profile_identity, schema),
            "target_execution_identity": _target_execution_identity(
                target_profile_identity, runtime_source_scope_sha256=runtime_source_scope_sha256
            ),
            "workload_path": row["workload_path"],
            "workload_factory": workflow["workload"]["factory"],
        }
        if case_context["target_execution_identity"] is None:
            raise ContractError("target profile has no valid scoped execution identity")
        case_context_sha256 = _canonical_sha256(case_context)
        case_receipt_path = CASE_RECEIPT_DIR / f"{case_context_sha256}.json"

        if not args.no_reuse and not args.prepare and profile_receipt_trusted:
            cached_case = _load_cached_case(
                case_receipt_path,
                context=case_context,
                profile_context_sha256=profile_context_sha256,
            )
            if cached_case is not None:
                cached_freshness_checks = [
                    (MANIFEST_PATH, manifest_sha256, "manifest"),
                    (index_path, index_sha256, "materialized index"),
                    (indexed_workflow_path, indexed_input_sha256, "indexed workflow input"),
                    (recipe_path, recipe_sha256, "workflow recipe"),
                ]
                if case_filter_applied and not is_api:
                    cached_freshness_checks.append(
                        (workflow_path, input_sha256, "selected workflow input")
                    )
                if workload_path is not None and workload_sha256 is not None:
                    cached_freshness_checks.append(
                        (workload_path, workload_sha256, "workflow workload")
                    )
                for path, digest, label in cached_freshness_checks:
                    if sha256_file(path) != digest:
                        raise ContractError(f"{label} changed while checking cached parity")
                if (
                    _git_revision(target_source, "FastAPI-RS") != target_revision
                    or _git_revision(starlette_rs_source, "Starlette-RS") != starlette_rs_revision
                    or fastapi_rs_source_tree_sha256(target_source, starlette_rs_source)
                    != target_source_digest
                ):
                    raise ContractError("source identity changed while checking cached parity")
                print(
                    json.dumps(
                        {
                            "status": "matched",
                            "workflow_id": args.id,
                            "schema": schema,
                            "profile_extension": extension,
                            "indexed_case_count": len(indexed_case_ids),
                            "case_count": len(selected_case_ids),
                            "selected_case_ids": selected_case_ids,
                            "summary": cached_case["summary"],
                            "oracle_result": cached_case["oracle_result"]["path"],
                            "target_result": cached_case["target_result"]["path"],
                            "comparison_result": cached_case["comparison_result"],
                            "target_identity": {
                                "target_revision": target_revision,
                                "starlette_rs_revision": starlette_rs_revision,
                                "source_tree_sha256": target_source_digest,
                                "runtime_source_scope_sha256": runtime_source_scope_sha256,
                                "target_binary_sha256": target_profile_identity[
                                    "target_binary_sha256"
                                ],
                            },
                            "receipt_target_identity": cached_case["target_identity"],
                            "manifest_sha256": manifest_sha256,
                            "input_sha256": input_sha256,
                            "indexed_input_sha256": indexed_input_sha256,
                            "selected_input": workflow_path.relative_to(ROOT).as_posix(),
                            "reused": True,
                            "reuse_receipt": case_receipt_path.relative_to(ROOT).as_posix(),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
                return 0

        _write_receipt(
            case_receipt_path,
            {
                "schema": CASE_RECEIPT_SCHEMA,
                "status": "running",
                "context": case_context,
                "context_sha256": case_context_sha256,
                "profile_context_sha256": profile_context_sha256,
            },
        )

    if is_process:
        run_id = uuid.uuid4().hex
        base = PROCESS_RESULT_DIR / args.id / run_id
        oracle_path = base / "oracle.json"
        target_path = base / "target.json"
        comparison_path = base / "comparison.json"
        source_run = _run_json(
            "process oracle",
            [
                "-m",
                "scripts.parity.process_worker",
                "oracle",
                "--input",
                str(workflow_path),
                "--profile",
                workflow["profiles"]["oracle"],
                "--python",
                str(oracle_python),
                "--fastapi-source",
                str(fastapi_source),
                "--starlette-source",
                str(starlette_source),
                "--output",
                str(oracle_path),
            ],
        )
        target_run = _run_json(
            "process target",
            [
                "-m",
                "scripts.parity.process_worker",
                "target",
                "--input",
                str(workflow_path),
                "--profile",
                workflow["profiles"]["target"],
                "--python",
                str(target_python),
                "--target-source",
                str(target_source),
                "--starlette-rs-source",
                str(starlette_rs_source),
                "--output",
                str(target_path),
            ],
        )
        oracle_artifact = _artifact(source_run, "process oracle")
        target_artifact = _artifact(target_run, "process target")
        target_result = read_json(ROOT / target_artifact)
        if not isinstance(target_result, dict):
            raise ContractError("process target artifact is malformed")
        target_identity = _check_target_identity(
            target_result,
            fastapi_revision=target_revision,
            source_digest=target_source_digest,
            starlette_rs_revision=starlette_rs_revision,
            runtime_source_scope_sha256=runtime_source_scope_sha256,
        )
        comparison = _run_json(
            "process comparison",
            [
                "-m",
                "scripts.parity.process_worker",
                "compare",
                "--input",
                str(workflow_path),
                "--source-result",
                oracle_artifact,
                "--target-result",
                target_artifact,
                "--fastapi-source",
                str(fastapi_source),
                "--output",
                str(comparison_path),
            ],
        )
        comparison_artifact = _artifact(comparison, "process comparison")
        comparison_result = read_json(ROOT / comparison_artifact)
        summary = comparison_result.get("summary") if isinstance(comparison_result, dict) else None
        passed = (
            comparison_result.get("status") == "matched"
            and isinstance(summary, dict)
            and summary.get("case_count") == len(workflow["cases"])
            and summary.get("matched") == len(workflow["cases"])
            and summary.get("mismatched") == 0
        )
        oracle_reference = None
        target_reference = None
        comparison_reference = None
    else:
        oracle_command = "api-oracle" if is_api else "oracle"
        target_command = "api-target" if is_api else "target"
        compare_command = "api-compare" if is_api else "compare"
        source_args = [
            "-m",
            "scripts.parity.cli",
            oracle_command,
            "--input",
            str(workflow_path),
            "--python",
            str(oracle_python),
            "--fastapi-source",
            str(fastapi_source),
            "--starlette-source",
            str(starlette_source),
        ]
        target_args = [
            "-m",
            "scripts.parity.cli",
            target_command,
            "--input",
            str(workflow_path),
            "--python",
            str(target_python),
            "--target-source",
            str(target_source),
            "--starlette-rs-source",
            str(starlette_rs_source),
        ]
        compare_args = [
            "-m",
            "scripts.parity.cli",
            compare_command,
            "--input",
            str(workflow_path),
            "--fastapi-source",
            str(fastapi_source),
        ]
        if is_api and extension:
            for command in (source_args, target_args, compare_args):
                command.extend(["--profile-extension", extension])
        if is_api:
            target_args.extend(
                [
                    "--fastapi-source",
                    str(fastapi_source),
                    "--starlette-source",
                    str(starlette_source),
                ]
            )
            for command in (source_args, target_args, compare_args):
                for case_id in args.case_id:
                    command.extend(["--case-id", case_id])
        source_run = _run_json("oracle run", source_args)
        target_run = _run_json("target run", target_args)
        target_identity = _check_target_identity(
            target_run,
            fastapi_revision=target_revision,
            source_digest=target_source_digest,
            starlette_rs_revision=starlette_rs_revision,
            runtime_source_scope_sha256=runtime_source_scope_sha256,
        )
        compare_args.extend(
            [
                "--source-result",
                _artifact(source_run, "oracle run"),
                "--target-result",
                _artifact(target_run, "target run"),
            ]
        )
        comparison = _run_json("comparison", compare_args)
        comparison_artifact = _artifact(comparison, "comparison")
        summary = comparison.get("summary")
        passed = _comparison_passed(comparison, len(workflow["cases"]))
        oracle_artifact = _artifact(source_run, "oracle run")
        target_artifact = _artifact(target_run, "target run")
        oracle_reference = _artifact_reference(oracle_artifact, product="oracle")
        target_reference = _artifact_reference(target_artifact, product="target")
        comparison_reference = _artifact_reference(comparison_artifact, product=None)
        oracle_result = read_json(ROOT / oracle_artifact)
        target_result = read_json(ROOT / target_artifact)
        if not isinstance(oracle_result, dict) or oracle_result.get(
            "identity"
        ) != _oracle_result_identity(oracle_profile_identity, schema):
            raise ContractError("oracle result identity changed after profile probing")
        if (
            not isinstance(target_result, dict)
            or target_result.get("identity") != target_profile_identity
        ):
            raise ContractError("target result identity changed after profile probing")
        comparison_result = read_json(ROOT / comparison_artifact)
        if (
            not isinstance(comparison_result, dict)
            or comparison_result.get("source_result") != oracle_reference
            or comparison_result.get("target_result") != target_reference
        ):
            raise ContractError("comparison result does not bind to the selected lane artifacts")

    if (
        _git_revision(target_source, "FastAPI-RS") != target_revision
        or _git_revision(starlette_rs_source, "Starlette-RS") != starlette_rs_revision
        or fastapi_rs_source_tree_sha256(target_source, starlette_rs_source) != target_source_digest
    ):
        raise ContractError(
            "FastAPI-RS or Starlette-RS source changed during the selected parity run"
        )
    freshness_checks = [
        (MANIFEST_PATH, manifest_sha256, "manifest"),
        (index_path, index_sha256, "materialized index"),
        (indexed_workflow_path, indexed_input_sha256, "indexed workflow input"),
        (recipe_path, recipe_sha256, "workflow recipe"),
    ]
    if case_filter_applied and not is_api:
        freshness_checks.append((workflow_path, input_sha256, "selected workflow input"))
    if workload_path is not None and workload_sha256 is not None:
        freshness_checks.append((workload_path, workload_sha256, "workflow workload"))
    for path, digest, label in freshness_checks:
        if sha256_file(path) != digest:
            raise ContractError(f"{label} changed during the selected parity run")

    if not is_process:
        assert case_receipt_path is not None
        assert case_context is not None
        assert profile_context_sha256 is not None
        assert oracle_reference is not None
        assert target_reference is not None
        assert comparison_reference is not None
        _write_receipt(
            case_receipt_path,
            {
                "schema": CASE_RECEIPT_SCHEMA,
                "status": "passed" if passed else "not_passed",
                "context": case_context,
                "context_sha256": _canonical_sha256(case_context),
                "profile_context_sha256": profile_context_sha256,
                "oracle_result": oracle_reference,
                "target_result": target_reference,
                "comparison_result": comparison_reference,
            },
        )

    if not passed:
        raise ContractError(f"selected workflow parity did not pass every case: {summary}")
    print(
        json.dumps(
            {
                "status": "matched",
                "workflow_id": args.id,
                "schema": schema,
                "profile_extension": extension if not is_process else None,
                "indexed_case_count": len(indexed_case_ids),
                "case_count": len(selected_case_ids),
                "selected_case_ids": selected_case_ids,
                "summary": summary,
                "oracle_result": _artifact(source_run, "oracle run"),
                "target_result": _artifact(target_run, "target run"),
                "comparison_result": comparison_artifact,
                "target_identity": target_identity,
                "manifest_sha256": manifest_sha256,
                "input_sha256": input_sha256,
                "indexed_input_sha256": indexed_input_sha256,
                "selected_input": workflow_path.relative_to(ROOT).as_posix(),
                "reused": False,
                "reuse_receipt": (
                    case_receipt_path.relative_to(ROOT).as_posix()
                    if case_receipt_path is not None
                    else None
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        print(f"parity indexed workflow: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
