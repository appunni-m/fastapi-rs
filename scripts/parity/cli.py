"""Command line interface for validating and executing parity inputs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.api_comparator import compare_api_workflow_results
from scripts.parity.api_contract import (
    validate_api_surface_contract,
    validate_api_workflow_public_surface,
)
from scripts.parity.comparator import SHARED_ORACLE_PACKAGES, compare_workflow_results
from scripts.parity.contract import (
    API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
    API_COMPARISON_SCHEMAS_BY_ID,
    API_RESULT_SCHEMA_IDS_BY_WORKFLOW,
    API_RESULT_SCHEMAS_BY_ID,
    API_WORKFLOW_SCHEMA_IDS,
    COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
    COMPARISON_SCHEMAS,
    RESULT_SCHEMAS,
    ROOT,
    WORKFLOW_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V7_ID,
    WORKFLOW_SCHEMA_V8_ID,
    WORKFLOW_SCHEMA_V9_ID,
    ContractError,
    load_workflow,
    read_json,
    read_manifest,
    select_oracle_profile,
    sha256_file,
)
from scripts.parity.coverage import (
    validate_compatibility_artifacts,
    validate_runtime_api_surfaces,
)
from scripts.parity.materialized import validate_materialized_input_index

DEFAULT_INPUT = Path("tests/fixtures/inputs/parity/first-asgi-request.json")
DEFAULT_FASTAPI_SOURCE = (ROOT / "../fastapi").resolve()
DEFAULT_STARLETTE_SOURCE = (ROOT / "../starlette").resolve()
DEFAULT_STARLETTE_RS_SOURCE = (ROOT / "../starlette-rs").resolve()


def _relative_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise ContractError(f"path is outside the repository: {path}") from exc


def _manifest_api_inventory(manifest: dict[str, Any]) -> dict[str, Any]:
    artifact = manifest["source_artifacts"]["api_inventory"]
    return read_json(ROOT / artifact["path"])


def _validate_result(result: dict[str, Any], input_digest: str, *, product: str = "oracle") -> None:
    schema_path = RESULT_SCHEMAS.get(result.get("schema"))
    if schema_path is None:
        raise ContractError(f"unsupported product result schema: {result.get('schema')!r}")
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(result), key=lambda error: error.message)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ContractError(f"{product} result does not match its schema: {details}")
    if result.get("product") != product:
        raise ContractError(f"expected a {product} result")
    if result["input"]["sha256"] != input_digest:
        raise ContractError(f"{product} worker result references a different workflow input")


def _load_result_artifact(path: Path, expected_product: str) -> tuple[dict[str, Any], Path, str]:
    result_path = path if path.is_absolute() else ROOT / path
    result_path = result_path.resolve()
    relative = _relative_path(result_path)
    if not relative.startswith("parity-results/"):
        raise ContractError(
            "product result artifacts must come from the ignored parity-results tree"
        )
    result = read_json(result_path)
    if not isinstance(result, dict):
        raise ContractError("product result artifact must be a JSON object")
    schema_path = RESULT_SCHEMAS.get(result.get("schema"))
    if schema_path is None:
        raise ContractError(f"unsupported product result schema: {result.get('schema')!r}")
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(result), key=lambda error: error.message)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ContractError(f"product result does not match its schema: {details}")
    if result["product"] != expected_product:
        raise ContractError(f"expected a {expected_product} result artifact")
    return result, result_path, sha256_file(result_path)


def _write_immutable_result(result: dict[str, Any], artifact_root: Path) -> Path:
    artifact_root = artifact_root.resolve()
    try:
        artifact_root.relative_to(ROOT / "parity-results")
    except ValueError as exc:
        raise ContractError(
            "result artifacts must be written inside the ignored parity-results tree"
        ) from exc
    artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_root / f"{result['run_id']}.json"
    serialized = json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    try:
        with artifact_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
    except FileExistsError as exc:
        raise ContractError(f"refusing to replace immutable result: {artifact_path}") from exc
    return artifact_path


def validate_command(args: argparse.Namespace) -> dict[str, Any]:
    manifest = read_manifest()
    source_root = args.fastapi_source.resolve()
    atlas_path = ROOT / manifest["source_artifacts"]["compatibility_atlas"]["path"]
    backlog_path = ROOT / manifest["source_artifacts"]["fixture_backlog"]["path"]
    selector_path = ROOT / manifest["source_artifacts"]["observation_selector_catalog"]["path"]
    materialized_path = ROOT / manifest["source_artifacts"]["materialized_input_index"]["path"]
    inventory_path = ROOT / manifest["source_artifacts"]["api_inventory"]["path"]
    runtime_core_path = ROOT / manifest["source_artifacts"]["runtime_api_surface_core"]["path"]
    runtime_standard_path = (
        ROOT / manifest["source_artifacts"]["runtime_api_surface_standard"]["path"]
    )
    runtime_reflection = validate_runtime_api_surfaces(
        read_json(inventory_path),
        read_json(runtime_core_path),
        read_json(runtime_standard_path),
    )
    api_surface_contract = validate_api_surface_contract(
        manifest.get("api_surface_contract"),
        inventory=read_json(inventory_path),
        atlas=read_json(atlas_path),
        backlog=read_json(backlog_path),
        materialized_input_index=read_json(materialized_path),
        runtime_core=read_json(runtime_core_path),
        runtime_standard=read_json(runtime_standard_path),
    )
    coverage = validate_compatibility_artifacts(
        read_json(atlas_path),
        read_json(backlog_path),
        read_json(selector_path),
        fastapi_source=source_root,
        starlette_source=args.starlette_source.resolve(),
    )
    materialized_inputs = validate_materialized_input_index(
        read_json(materialized_path),
        atlas=read_json(atlas_path),
        backlog=read_json(backlog_path),
        selector_catalog=read_json(selector_path),
        fastapi_source=source_root,
    )
    workflow, workflow_path, digest, workload_path = load_workflow(
        args.input,
        source_root=source_root,
    )
    return {
        "status": "valid",
        "input": _relative_path(workflow_path),
        "sha256": digest,
        "manifest_sha256": sha256_file(ROOT / "tests/fixtures/manifest.yaml"),
        "workload": _relative_path(workload_path),
        "workload_sha256": sha256_file(workload_path),
        "cases": [case["case_id"] for case in workflow["cases"]],
        "coverage": coverage,
        "materialized_inputs": materialized_inputs,
        "runtime_api_reflection": runtime_reflection,
        "api_surface_contract": api_surface_contract,
    }


def _validate_indexed_api_workflow(
    manifest: dict[str, Any],
    workflow: dict[str, Any],
    workflow_path: Path,
    input_digest: str,
    *,
    fastapi_source: Path,
    starlette_source: Path,
) -> dict[str, Any]:
    """Require direct API evidence to be a current, source-mapped fixture."""
    source_artifacts = manifest["source_artifacts"]
    atlas = read_json(ROOT / source_artifacts["compatibility_atlas"]["path"])
    backlog = read_json(ROOT / source_artifacts["fixture_backlog"]["path"])
    selector_catalog = read_json(ROOT / source_artifacts["observation_selector_catalog"]["path"])
    index = read_json(ROOT / source_artifacts["materialized_input_index"]["path"])
    validate_compatibility_artifacts(
        atlas,
        backlog,
        selector_catalog,
        fastapi_source=fastapi_source,
        starlette_source=starlette_source,
    )
    summary = validate_materialized_input_index(
        index,
        atlas=atlas,
        backlog=backlog,
        selector_catalog=selector_catalog,
        fastapi_source=fastapi_source,
    )

    relative_input = _relative_path(workflow_path)
    matching = [row for row in index["workflows"] if row["input_path"] == relative_input]
    if len(matching) != 1:
        raise ContractError("direct API workflow is not uniquely indexed as a materialized input")
    indexed = matching[0]
    if (
        indexed["input_sha256"] != input_digest
        or indexed["workload_path"] != workflow["workload"]["file"]
        or indexed["workload_sha256"] != sha256_file(ROOT / workflow["workload"]["file"])
        or set(indexed["case_ids"]) != {case["case_id"] for case in workflow["cases"]}
    ):
        raise ContractError("direct API workflow differs from its materialized input index entry")

    coverage_by_id = {row["id"]: row for row in atlas["coverage_matrix"]}
    mappings = [row for row in index["mappings"] if row["workflow_id"] == indexed["id"]]
    for case in workflow["cases"]:
        evidence = {
            (row["path"], row["kind"])
            for row in case["source_evidence"]
            if row["kind"] != "upstream_api_definition"
        }
        expected_definitions = sorted(
            (
                {
                    "case_id": case["case_id"],
                    "symbol_id": row["symbol_id"],
                    "path": row["path"],
                    "sha256": row["sha256"],
                }
                for row in case["source_evidence"]
                if row["kind"] == "upstream_api_definition"
            ),
            key=lambda row: (row["case_id"], row["symbol_id"], row["path"]),
        )
        indexed_definitions = [
            row for row in indexed.get("api_definitions", []) if row["case_id"] == case["case_id"]
        ]
        if indexed_definitions != expected_definitions:
            raise ContractError(
                f"direct API source definitions differ from indexed evidence: {case['case_id']}"
            )
        case_mappings = [row for row in mappings if case["case_id"] in row["case_ids"]]
        mapped = set()
        for mapping in case_mappings:
            source = coverage_by_id[mapping["source_item_id"]]
            kind = (
                "upstream_documentation"
                if source["kind"] == "documented_feature_page"
                else "upstream_test"
            )
            mapped.add((source["source_path"], kind))
        if (not mapped and not indexed_definitions) or not mapped <= evidence:
            raise ContractError(
                f"direct API workflow case lacks its indexed source evidence: {case['case_id']}"
            )
    return summary


def oracle_command(args: argparse.Namespace) -> dict[str, Any]:
    workflow, workflow_path, input_digest, _ = load_workflow(
        args.input,
        source_root=args.fastapi_source.resolve(),
    )
    # Keep a venv's Python symlink intact: resolving it launches the base
    # interpreter and loses that environment's site-packages.
    python = args.python.absolute()
    if not python.is_file():
        raise ContractError(f"oracle Python interpreter does not exist: {python}")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest = read_manifest()
    oracle_profile = select_oracle_profile(manifest, workflow.get("oracle_profile_extension"))

    command = [
        str(python),
        "-m",
        "scripts.parity.worker",
        "--input",
        str(workflow_path),
        "--fastapi-source",
        str(args.fastapi_source.resolve()),
        "--starlette-source",
        str(args.starlette_source.resolve()),
        "--input-sha256",
        input_digest,
        "--workload-sha256",
        sha256_file(ROOT / workflow["workload"]["file"]),
        "--manifest-sha256",
        sha256_file(manifest_path),
        "--oracle-profile",
        json.dumps(oracle_profile, separators=(",", ":")),
    ]
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ContractError(f"oracle worker exceeded {args.timeout_seconds}s") from exc
    if completed.returncode != 0:
        try:
            worker_error = json.loads(completed.stdout)
        except json.JSONDecodeError:
            worker_error = {"message": completed.stderr.strip() or completed.stdout.strip()}
        raise ContractError(f"oracle worker failed: {worker_error}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("oracle worker emitted malformed JSON") from exc
    if not isinstance(result, dict):
        raise ContractError("oracle worker result must be a JSON object")
    result["command"]["argv"] = command
    _validate_result(result, input_digest)

    expected_ids = [case["case_id"] for case in workflow["cases"]]
    actual_ids = [case["case_id"] for case in result["cases"]]
    if actual_ids != expected_ids:
        raise ContractError("oracle result cases do not match input order and cardinality")
    artifact_path = _write_immutable_result(result, args.output_dir)
    return {
        "status": result["status"],
        "product": result["product"],
        "identity": result["identity"],
        "case_count": len(result["cases"]),
        "product_error_cases": [
            case["case_id"]
            for case in result["cases"]
            if case["status"] == "product_error"
            or any(action["status"] == "product_error" for action in case.get("actions", []))
        ],
        "construction_error_cases": [
            case["case_id"]
            for case in result["cases"]
            if case.get("construction_observation", {}).get("values", {}).get("outcome") == "error"
        ],
        "artifact": _relative_path(artifact_path),
    }


def target_command(args: argparse.Namespace) -> dict[str, Any]:
    workflow, workflow_path, input_digest, workload_path = load_workflow(args.input)
    if workflow["schema"] not in {
        WORKFLOW_SCHEMA_ID,
        WORKFLOW_SCHEMA_V3_ID,
        WORKFLOW_SCHEMA_V4_ID,
        WORKFLOW_SCHEMA_V5_ID,
        WORKFLOW_SCHEMA_V6_ID,
        WORKFLOW_SCHEMA_V7_ID,
        WORKFLOW_SCHEMA_V8_ID,
        WORKFLOW_SCHEMA_V9_ID,
    }:
        raise ContractError("target requires a Python/ASGI v2 through v9 workflow")
    python = args.python.absolute()
    if not python.is_file():
        raise ContractError(
            f"target Python interpreter does not exist: {python}; run make parity-prepare-target"
        )
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest = read_manifest()
    manifest_digest = sha256_file(manifest_path)
    workload_digest = sha256_file(workload_path)
    target_profile = {
        "python": manifest["oracle_profile"]["python"],
        "shared_runtime_packages": {
            name: version
            for name, version in manifest["oracle_profile"]["packages"].items()
            if name in SHARED_ORACLE_PACKAGES
        },
        "target": manifest["target"],
    }
    command = [
        str(python),
        "-m",
        "scripts.parity.target_worker",
        "--input",
        str(workflow_path),
        "--target-source",
        str(args.target_source.resolve()),
        "--starlette-rs-source",
        str(args.starlette_rs_source.resolve()),
        "--target-profile",
        json.dumps(target_profile, separators=(",", ":")),
        "--input-sha256",
        input_digest,
        "--workload-sha256",
        workload_digest,
        "--manifest-sha256",
        manifest_digest,
    ]
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ContractError(f"target worker exceeded {args.timeout_seconds}s") from exc
    if completed.returncode != 0:
        try:
            worker_error = json.loads(completed.stdout)
        except json.JSONDecodeError:
            worker_error = {"message": completed.stderr.strip() or completed.stdout.strip()}
        raise ContractError(f"target worker failed: {worker_error}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("target worker emitted malformed JSON") from exc
    if not isinstance(result, dict):
        raise ContractError("target worker result must be a JSON object")
    if not isinstance(result.get("command"), dict):
        raise ContractError("target worker result has no command record")
    result["command"]["argv"] = command
    _validate_result(result, input_digest, product="target")
    if result["manifest"]["sha256"] != manifest_digest:
        raise ContractError("target result references a different manifest")
    if result["input"]["path"] != workflow_path.relative_to(ROOT).as_posix():
        raise ContractError("target result references a different workflow path")
    if result["input"].get("schema") != workflow["schema"]:
        raise ContractError("target result references a different workflow schema")
    if (
        result["workload"]["path"] != workflow["workload"]["file"]
        or result["workload"]["sha256"] != workload_digest
        or result["workload"]["factory"] != workflow["workload"]["factory"]
    ):
        raise ContractError("target result references a different workload")
    expected_ids = [case["case_id"] for case in workflow["cases"]]
    actual_ids = [case["case_id"] for case in result["cases"]]
    if actual_ids != expected_ids:
        raise ContractError("target result cases do not match input order and cardinality")

    artifact_path = _write_immutable_result(result, args.output_dir)
    return {
        "status": result["status"],
        "product": result["product"],
        "identity": result["identity"],
        "case_count": len(result["cases"]),
        "product_error_cases": [
            case["case_id"]
            for case in result["cases"]
            if case["status"] == "product_error"
            or any(action["status"] == "product_error" for action in case.get("actions", []))
        ],
        "construction_error_cases": [
            case["case_id"]
            for case in result["cases"]
            if case.get("construction_observation", {}).get("values", {}).get("outcome") == "error"
        ],
        "artifact": _relative_path(artifact_path),
    }


def api_validate_command(args: argparse.Namespace) -> dict[str, Any]:
    workflow, workflow_path, digest, workload_path = load_workflow(
        args.input,
        source_root=args.fastapi_source.resolve(),
    )
    if workflow["schema"] not in API_WORKFLOW_SCHEMA_IDS:
        raise ContractError("api-validate requires a supported direct Python API workflow")
    manifest = read_manifest()
    materialized_inputs = _validate_indexed_api_workflow(
        manifest,
        workflow,
        workflow_path,
        digest,
        fastapi_source=args.fastapi_source.resolve(),
        starlette_source=args.starlette_source.resolve(),
    )
    public_symbols = validate_api_workflow_public_surface(
        workflow,
        manifest.get("api_surface_contract", {}),
        _manifest_api_inventory(manifest),
        input_path=_relative_path(workflow_path),
    )
    return {
        "status": "valid",
        "input": _relative_path(workflow_path),
        "sha256": digest,
        "workload": _relative_path(workload_path),
        "workload_sha256": sha256_file(workload_path),
        "cases": [case["case_id"] for case in workflow["cases"]],
        "public_symbols": public_symbols,
        "materialized_inputs": materialized_inputs,
    }


def _validate_api_result(
    result: dict[str, Any], input_digest: str, workflow_schema_id: str
) -> None:
    result_schema_id = API_RESULT_SCHEMA_IDS_BY_WORKFLOW.get(workflow_schema_id)
    if result_schema_id is None or result.get("schema") != result_schema_id:
        raise ContractError("direct API result schema differs from its workflow version")
    schema = read_json(API_RESULT_SCHEMAS_BY_ID[result_schema_id])
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(result), key=lambda error: error.message)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ContractError(f"direct API result does not match its schema: {details}")
    if result["input"]["sha256"] != input_digest:
        raise ContractError("direct API result references a different workflow input")


def _validate_api_result_bindings(workflow: dict[str, Any], result: dict[str, Any]) -> None:
    if len(workflow["cases"]) != len(result["cases"]):
        raise ContractError("direct API result case count differs from input")
    for specification, result_case in zip(workflow["cases"], result["cases"], strict=True):
        if specification["case_id"] != result_case["case_id"]:
            raise ContractError("direct API result case order differs from input")
        expected_probes = specification["probes"]
        actual_probes = result_case["probes"]
        case_id = result_case["case_id"]
        if len(expected_probes) != len(actual_probes):
            raise ContractError(f"direct API result probe count differs from input: {case_id}")
        for expected_probe, actual_probe in zip(expected_probes, actual_probes, strict=True):
            if expected_probe["probe_id"] != actual_probe["probe_id"]:
                raise ContractError(
                    f"direct API result probe order differs: {result_case['case_id']}"
                )
            if actual_probe["status"] == "completed":
                if "error" in actual_probe:
                    raise ContractError(
                        f"completed direct API result probe contains an error: {case_id}"
                    )
                expected_observations = [
                    observation["kind"] for observation in expected_probe["observations"]
                ]
                actual_observations = actual_probe["observations"]
                if [row["kind"] for row in actual_observations] != expected_observations:
                    raise ContractError(f"direct API result observations differ: {case_id}")
                if [row["index"] for row in actual_observations] != list(
                    range(len(expected_observations))
                ):
                    raise ContractError(f"direct API result observation indexes differ: {case_id}")
            else:
                if "error" not in actual_probe or actual_probe["observations"] != []:
                    raise ContractError(
                        f"failed direct API result probe has contradictory fields: {case_id}"
                    )
        probe_errors = [
            probe["error"] for probe in actual_probes if probe["status"] == "product_error"
        ]
        expected_status = "product_error" if probe_errors else "completed"
        if result_case["status"] != expected_status:
            raise ContractError(f"direct API result case status differs from its probes: {case_id}")
        if probe_errors:
            if result_case.get("error") != probe_errors[0]:
                raise ContractError(f"failed direct API result case has the wrong error: {case_id}")
        elif "error" in result_case:
            raise ContractError(f"completed direct API result case contains an error: {case_id}")


def api_oracle_command(args: argparse.Namespace) -> dict[str, Any]:
    workflow, workflow_path, input_digest, _ = load_workflow(
        args.input,
        source_root=args.fastapi_source.resolve(),
    )
    if workflow["schema"] not in API_WORKFLOW_SCHEMA_IDS:
        raise ContractError("api-oracle requires a supported direct Python API workflow")
    python = args.python.absolute()
    if not python.is_file():
        raise ContractError(f"oracle Python interpreter does not exist: {python}")
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest = read_manifest()
    materialized_inputs = _validate_indexed_api_workflow(
        manifest,
        workflow,
        workflow_path,
        input_digest,
        fastapi_source=args.fastapi_source.resolve(),
        starlette_source=args.starlette_source.resolve(),
    )
    validate_api_workflow_public_surface(
        workflow,
        manifest.get("api_surface_contract", {}),
        _manifest_api_inventory(manifest),
        input_path=_relative_path(workflow_path),
    )
    oracle_profile = manifest["oracle_profile"]
    command = [
        str(python),
        "-m",
        "scripts.parity.api_worker",
        "--input",
        str(workflow_path),
        "--fastapi-source",
        str(args.fastapi_source.resolve()),
        "--starlette-source",
        str(args.starlette_source.resolve()),
        "--input-sha256",
        input_digest,
        "--workload-sha256",
        sha256_file(ROOT / workflow["workload"]["file"]),
        "--manifest-sha256",
        sha256_file(manifest_path),
        "--oracle-profile",
        json.dumps(oracle_profile, separators=(",", ":")),
    ]
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ContractError(f"direct API oracle exceeded {args.timeout_seconds}s") from exc
    if completed.returncode != 0:
        try:
            worker_error = json.loads(completed.stdout)
        except json.JSONDecodeError:
            worker_error = {"message": completed.stderr.strip() or completed.stdout.strip()}
        raise ContractError(f"direct API oracle failed: {worker_error}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("direct API oracle emitted malformed JSON") from exc
    if not isinstance(result, dict):
        raise ContractError("direct API oracle result must be a JSON object")
    result["command"]["argv"] = command
    _validate_api_result(result, input_digest, workflow["schema"])
    _validate_api_result_bindings(workflow, result)
    artifact_path = _write_immutable_result(result, args.output_dir)
    return {
        "status": result["status"],
        "product": result["product"],
        "identity": result["identity"],
        "case_count": len(result["cases"]),
        "materialized_inputs": materialized_inputs,
        "product_error_cases": [
            case["case_id"] for case in result["cases"] if case["status"] == "product_error"
        ],
        "artifact": _relative_path(artifact_path),
    }


def api_target_command(args: argparse.Namespace) -> dict[str, Any]:
    workflow, workflow_path, input_digest, workload_path = load_workflow(
        args.input,
        source_root=args.fastapi_source.resolve(),
    )
    if workflow["schema"] not in API_WORKFLOW_SCHEMA_IDS:
        raise ContractError("api-target requires a supported direct Python API workflow")
    python = args.python.absolute()
    if not python.is_file():
        raise ContractError(
            f"target Python interpreter does not exist: {python}; run make parity-prepare-target"
        )
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest = read_manifest()
    manifest_digest = sha256_file(manifest_path)
    workload_digest = sha256_file(workload_path)
    materialized_inputs = _validate_indexed_api_workflow(
        manifest,
        workflow,
        workflow_path,
        input_digest,
        fastapi_source=args.fastapi_source.resolve(),
        starlette_source=args.starlette_source.resolve(),
    )
    validate_api_workflow_public_surface(
        workflow,
        manifest.get("api_surface_contract", {}),
        _manifest_api_inventory(manifest),
        input_path=_relative_path(workflow_path),
    )
    target_profile = {
        "python": manifest["oracle_profile"]["python"],
        "shared_runtime_packages": {
            name: version
            for name, version in manifest["oracle_profile"]["packages"].items()
            if name in SHARED_ORACLE_PACKAGES
        },
        "target": manifest["target"],
    }
    command = [
        str(python),
        "-m",
        "scripts.parity.api_target_worker",
        "--input",
        str(workflow_path),
        "--fastapi-source",
        str(args.fastapi_source.resolve()),
        "--target-source",
        str(args.target_source.resolve()),
        "--starlette-rs-source",
        str(args.starlette_rs_source.resolve()),
        "--target-profile",
        json.dumps(target_profile, separators=(",", ":")),
        "--input-sha256",
        input_digest,
        "--workload-sha256",
        workload_digest,
        "--manifest-sha256",
        manifest_digest,
    ]
    environment = os.environ.copy()
    for variable in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=args.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ContractError(f"direct API target exceeded {args.timeout_seconds}s") from exc
    if completed.returncode != 0:
        try:
            worker_error = json.loads(completed.stdout)
        except json.JSONDecodeError:
            worker_error = {"message": completed.stderr.strip() or completed.stdout.strip()}
        raise ContractError(f"direct API target failed: {worker_error}")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("direct API target emitted malformed JSON") from exc
    if not isinstance(result, dict) or not isinstance(result.get("command"), dict):
        raise ContractError("direct API target result is malformed")
    result["command"]["argv"] = command
    _validate_api_result(result, input_digest, workflow["schema"])
    _validate_api_result_bindings(workflow, result)
    if result["product"] != "target":
        raise ContractError("direct API target worker emitted a non-target result")
    if result["manifest"].get("sha256") != manifest_digest:
        raise ContractError("direct API target references a different manifest")
    if result["input"].get("path") != workflow_path.relative_to(ROOT).as_posix():
        raise ContractError("direct API target references a different workflow path")
    if result["workload"].get("sha256") != workload_digest:
        raise ContractError("direct API target references a different workload")
    artifact_path = _write_immutable_result(result, args.output_dir)
    return {
        "status": result["status"],
        "product": result["product"],
        "identity": result["identity"],
        "case_count": len(result["cases"]),
        "product_error_cases": [
            case["case_id"] for case in result["cases"] if case["status"] == "product_error"
        ],
        "materialized_inputs": materialized_inputs,
        "artifact": _relative_path(artifact_path),
    }


def api_compare_command(args: argparse.Namespace) -> dict[str, Any]:
    source, source_path, source_digest = _load_result_artifact(args.source_result, "oracle")
    target, target_path, target_digest = _load_result_artifact(args.target_result, "target")
    workflow, workflow_path, input_digest, workload_path = load_workflow(
        args.input,
        source_root=args.fastapi_source.resolve(),
    )
    if workflow["schema"] not in API_WORKFLOW_SCHEMA_IDS:
        raise ContractError("api-compare requires a supported direct Python API workflow")
    result_schema_id = API_RESULT_SCHEMA_IDS_BY_WORKFLOW[workflow["schema"]]
    if source.get("schema") != result_schema_id or target.get("schema") != result_schema_id:
        raise ContractError("direct API source and target result schemas differ from the workflow")
    _validate_api_result_bindings(workflow, source)
    _validate_api_result_bindings(workflow, target)
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest = read_manifest()
    manifest_digest = sha256_file(manifest_path)
    command = [
        sys.executable,
        "-m",
        "scripts.parity.cli",
        "api-compare",
        "--input",
        workflow_path.relative_to(ROOT).as_posix(),
        "--source-result",
        source_path.relative_to(ROOT).as_posix(),
        "--target-result",
        target_path.relative_to(ROOT).as_posix(),
    ]
    comparison = compare_api_workflow_results(
        workflow=workflow,
        source=source,
        target=target,
        oracle_profile=manifest["oracle_profile"],
        target_profile=manifest["target"],
        manifest_sha256=manifest_digest,
        input_path=workflow_path.relative_to(ROOT).as_posix(),
        input_sha256=input_digest,
        workload_sha256=sha256_file(workload_path),
        source_result_ref={
            "path": source_path.relative_to(ROOT).as_posix(),
            "sha256": source_digest,
            "run_id": source["run_id"],
            "product": source["product"],
        },
        target_result_ref={
            "path": target_path.relative_to(ROOT).as_posix(),
            "sha256": target_digest,
            "run_id": target["run_id"],
            "product": target["product"],
        },
        command=command,
    )
    comparison_schema_id = API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW[workflow["schema"]]
    if comparison.get("schema") != comparison_schema_id:
        raise ContractError("direct API comparator emitted an unsupported result schema")
    schema = read_json(API_COMPARISON_SCHEMAS_BY_ID[comparison_schema_id])
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(comparison), key=lambda error: error.message)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ContractError(f"direct API comparison does not match its schema: {details}")
    artifact_path = _write_immutable_result(comparison, ROOT / "parity-results/comparisons")
    return {
        "status": comparison["status"],
        "summary": comparison["summary"],
        "artifact": _relative_path(artifact_path),
    }


def compare_command(args: argparse.Namespace) -> dict[str, Any]:
    source, source_path, source_digest = _load_result_artifact(args.source_result, "oracle")
    target, target_path, target_digest = _load_result_artifact(args.target_result, "target")
    workflow, workflow_path, input_digest, _ = load_workflow(
        args.input,
        source_root=args.fastapi_source.resolve(),
    )
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest = read_manifest()
    manifest_digest = sha256_file(manifest_path)
    command = [
        sys.executable,
        "-m",
        "scripts.parity.cli",
        "compare",
        "--input",
        workflow_path.relative_to(ROOT).as_posix(),
        "--source-result",
        source_path.relative_to(ROOT).as_posix(),
        "--target-result",
        target_path.relative_to(ROOT).as_posix(),
    ]
    comparison = compare_workflow_results(
        workflow=workflow,
        source=source,
        target=target,
        oracle_profile=select_oracle_profile(manifest, workflow.get("oracle_profile_extension")),
        target_profile=manifest["target"],
        manifest_sha256=manifest_digest,
        input_path=workflow_path.relative_to(ROOT).as_posix(),
        input_sha256=input_digest,
        workload_sha256=sha256_file(ROOT / workflow["workload"]["file"]),
        source_result_ref={
            "path": source_path.relative_to(ROOT).as_posix(),
            "sha256": source_digest,
            "run_id": source["run_id"],
            "product": source["product"],
        },
        target_result_ref={
            "path": target_path.relative_to(ROOT).as_posix(),
            "sha256": target_digest,
            "run_id": target["run_id"],
            "product": target["product"],
        },
        command=command,
    )
    comparison_schema_id = COMPARISON_SCHEMA_IDS_BY_WORKFLOW.get(workflow["schema"])
    comparison_schema_path = COMPARISON_SCHEMAS.get(comparison_schema_id)
    if comparison_schema_path is None:
        raise ContractError(f"no comparison schema for workflow {workflow['schema']!r}")
    schema = read_json(comparison_schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(comparison), key=lambda error: error.message)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ContractError(f"comparison result does not match its schema: {details}")
    artifact_path = _write_immutable_result(
        comparison,
        ROOT / "parity-results/comparisons",
    )
    return {
        "status": comparison["status"],
        "summary": comparison["summary"],
        "artifact": _relative_path(artifact_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate", help="validate an input-only workflow and its references"
    )
    validate.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    validate.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    validate.add_argument("--starlette-source", type=Path, default=DEFAULT_STARLETTE_SOURCE)
    validate.set_defaults(handler=validate_command)

    oracle = subparsers.add_parser(
        "oracle", help="run an input workflow in isolated FastAPI 0.141.1"
    )
    oracle.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    oracle.add_argument("--python", type=Path, default=ROOT / ".venv-oracle/bin/python")
    oracle.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    oracle.add_argument("--starlette-source", type=Path, default=DEFAULT_STARLETTE_SOURCE)
    oracle.add_argument("--timeout-seconds", type=int, default=180)
    oracle.add_argument("--output-dir", type=Path, default=ROOT / "parity-results/oracle")
    oracle.set_defaults(handler=oracle_command)

    target = subparsers.add_parser(
        "target", help="run an input workflow in the isolated FastAPI-RS target environment"
    )
    target.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    target.add_argument("--python", type=Path, default=ROOT / ".venv-target/bin/python")
    target.add_argument("--target-source", type=Path, default=ROOT)
    target.add_argument("--starlette-rs-source", type=Path, default=DEFAULT_STARLETTE_RS_SOURCE)
    target.add_argument("--timeout-seconds", type=int, default=180)
    target.add_argument("--output-dir", type=Path, default=ROOT / "parity-results/target")
    target.set_defaults(handler=target_command)

    api_validate = subparsers.add_parser(
        "api-validate", help="validate a direct Python public API workflow and source references"
    )
    api_validate.add_argument("--input", required=True, type=Path)
    api_validate.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    api_validate.add_argument("--starlette-source", type=Path, default=DEFAULT_STARLETTE_SOURCE)
    api_validate.set_defaults(handler=api_validate_command)

    api_oracle = subparsers.add_parser(
        "api-oracle", help="run direct public Python API probes in isolated FastAPI 0.141.1"
    )
    api_oracle.add_argument("--input", required=True, type=Path)
    api_oracle.add_argument("--python", type=Path, default=ROOT / ".venv-oracle/bin/python")
    api_oracle.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    api_oracle.add_argument("--starlette-source", type=Path, default=DEFAULT_STARLETTE_SOURCE)
    api_oracle.add_argument("--timeout-seconds", type=int, default=180)
    api_oracle.add_argument(
        "--output-dir", type=Path, default=ROOT / "parity-results/python-api-oracle"
    )
    api_oracle.set_defaults(handler=api_oracle_command)

    api_target = subparsers.add_parser(
        "api-target", help="run direct public Python API probes in the isolated FastAPI-RS target"
    )
    api_target.add_argument("--input", required=True, type=Path)
    api_target.add_argument("--python", type=Path, default=ROOT / ".venv-target/bin/python")
    api_target.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    api_target.add_argument("--starlette-source", type=Path, default=DEFAULT_STARLETTE_SOURCE)
    api_target.add_argument("--target-source", type=Path, default=ROOT)
    api_target.add_argument("--starlette-rs-source", type=Path, default=DEFAULT_STARLETTE_RS_SOURCE)
    api_target.add_argument("--timeout-seconds", type=int, default=180)
    api_target.add_argument(
        "--output-dir", type=Path, default=ROOT / "parity-results/python-api-target"
    )
    api_target.set_defaults(handler=api_target_command)

    api_compare = subparsers.add_parser(
        "api-compare", help="compare direct public Python API observations exactly"
    )
    api_compare.add_argument("--input", required=True, type=Path)
    api_compare.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    api_compare.add_argument("--source-result", required=True, type=Path)
    api_compare.add_argument("--target-result", required=True, type=Path)
    api_compare.set_defaults(handler=api_compare_command)

    compare = subparsers.add_parser(
        "compare", help="compare isolated oracle and FastAPI-RS results"
    )
    compare.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    compare.add_argument("--fastapi-source", type=Path, default=DEFAULT_FASTAPI_SOURCE)
    compare.add_argument("--source-result", required=True, type=Path)
    compare.add_argument("--target-result", required=True, type=Path)
    compare.set_defaults(handler=compare_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = args.handler(args)
    except (ContractError, OSError, ValueError) as exc:
        print(f"parity: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    if args.command in {"compare", "api-compare"} and (
        result["summary"]["failed"] or result["summary"]["not_run"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
