"""Build a deterministic ledger for declared, indexed parity requirements."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from scripts.parity.api_comparator import compare_api_workflow_results
from scripts.parity.comparator import SHARED_ORACLE_PACKAGES, compare_workflow_results
from scripts.parity.contract import (
    API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
    API_COMPARISON_SCHEMAS_BY_ID,
    API_WORKFLOW_SCHEMA_IDS,
    COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
    COMPARISON_SCHEMAS,
    PROCESS_WORKFLOW_SCHEMA_IDS,
    RECIPE_WORKFLOW_SCHEMAS,
    RESULT_SCHEMA_IDS_BY_WORKFLOW,
    RESULT_SCHEMAS,
    ROOT,
    ContractError,
    read_json,
    read_manifest,
    select_oracle_profile,
    select_target_profile,
    sha256_file,
)
from scripts.parity.fault_contracts import verification_mode
from scripts.parity.process_comparator import (
    PROCESS_COMPARISON_SCHEMAS,
    PROCESS_RESULT_SCHEMAS,
    compare_process_workflow_results,
)
from scripts.parity.process_comparator import (
    _validate_schema as _validate_process_schema,
)
from scripts.parity.source_identity import (
    SourceIdentityError,
    fastapi_rs_source_tree_sha256,
)

REPORT_SCHEMA_ID = "fastapi-rs/parity-campaign-report@1"
REPORT_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/parity-campaign-report-v1.schema.json"
PARITY_RESULTS_ROOT = (ROOT / "parity-results").resolve()
SUPPORTED_PARITY_WORKFLOW_SCHEMAS = frozenset(
    schema_id
    for schema_id in RECIPE_WORKFLOW_SCHEMAS
    if schema_id not in PROCESS_WORKFLOW_SCHEMA_IDS
)


class CampaignError(ContractError):
    """The declared campaign input or comparison evidence is invalid."""


def _schema_errors(value: Any, schema_path: Path, label: str) -> None:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: error.message)
    if errors:
        details = "; ".join(error.message for error in errors)
        raise CampaignError(f"{label} does not match its schema: {details}")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _repo_path(value: Any, label: str) -> tuple[Path, str]:
    if not isinstance(value, str) or not value:
        raise CampaignError(f"{label} must be a non-empty repository-relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise CampaignError(f"{label} must be repository-relative")
    resolved = (ROOT / relative).resolve()
    if not _inside(resolved, ROOT.resolve()):
        raise CampaignError(f"{label} resolves outside the repository")
    return resolved, resolved.relative_to(ROOT.resolve()).as_posix()


def _artifact_path(value: Any, label: str) -> tuple[Path, str]:
    resolved, relative = _repo_path(value, label)
    if not _inside(resolved, PARITY_RESULTS_ROOT):
        raise CampaignError(f"{label} must point inside parity-results/")
    return resolved, relative


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = read_json(path)
    except (OSError, ValueError) as exc:
        raise CampaignError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise CampaignError(f"{label} must be a JSON object")
    return value


def _current_target_revision() -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[a-f0-9]{40}", revision) is None:
        return None
    return revision


def _git_revision(path: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or re.fullmatch(r"[a-f0-9]{40}", revision) is None:
        return None
    return revision


def _git_worktree_clean(path: Path) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ],
        check=False,
        capture_output=True,
        timeout=30,
    )
    return completed.returncode == 0 and not completed.stdout


def _current_target_source_identity(
    manifest: dict[str, Any],
) -> dict[str, Any]:
    # metadata.yaml is YAML; keep its Starlette-RS checkout selection aligned
    # with the target workers' STARLETTE_RS_SOURCE override.
    try:
        metadata = yaml.safe_load((ROOT / "metadata.yaml").read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CampaignError(f"cannot read pinned Starlette-RS source identity: {exc}") from exc
    starlette_rs = metadata.get("starlette_rs") if isinstance(metadata, dict) else None
    if not isinstance(starlette_rs, dict) or not isinstance(starlette_rs.get("owner"), str):
        raise CampaignError("metadata.yaml has no pinned Starlette-RS source checkout")
    override = os.environ.get("STARLETTE_RS_SOURCE")
    starlette_rs_source = (
        Path(override).resolve() if override else (ROOT / starlette_rs["owner"]).resolve()
    )
    target_revision = _current_target_revision()
    starlette_rs_revision = _git_revision(starlette_rs_source)
    try:
        source_tree_sha256 = fastapi_rs_source_tree_sha256(ROOT, starlette_rs_source)
    except (OSError, SourceIdentityError) as exc:
        raise CampaignError(f"cannot compute current target source identity: {exc}") from exc
    expected_starlette_rs = manifest.get("target", {}).get("starlette_rs_distribution", {})
    metadata_revision = starlette_rs.get("commit")
    clean = _git_worktree_clean(ROOT) and _git_worktree_clean(starlette_rs_source)
    return {
        "revision": target_revision,
        "source_tree_sha256": source_tree_sha256,
        "clean": clean,
        "starlette_rs_revision": starlette_rs_revision,
        "starlette_rs_profile_matches": (
            starlette_rs_revision == metadata_revision
            and starlette_rs_revision == expected_starlette_rs.get("commit")
        ),
    }


def _validate_index_and_workflows(
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    artifact = manifest.get("source_artifacts", {}).get("materialized_input_index")
    if not isinstance(artifact, dict):
        raise CampaignError("manifest does not declare a materialized input index")
    index_path, index_relative = _repo_path(artifact.get("path"), "materialized index path")
    index = _read_json_object(index_path, "materialized input index")
    index_digest = sha256_file(index_path)
    if index_digest != artifact.get("sha256"):
        raise CampaignError("manifest materialized input index digest is stale")
    if index.get("schema") != artifact.get("schema"):
        raise CampaignError("manifest materialized input index schema differs from the index")
    schema_path, _ = _repo_path(artifact.get("schema_path"), "materialized index schema path")
    if sha256_file(schema_path) != artifact.get("schema_sha256"):
        raise CampaignError("manifest materialized input index schema digest is stale")
    _schema_errors(index, schema_path, "materialized input index")

    workflows = index.get("workflows")
    if not isinstance(workflows, list) or not workflows:
        raise CampaignError("materialized input index has no workflow rows")
    expected_counts = artifact.get("counts", {})
    actual_counts = {
        "workflows": len(workflows),
        "cases": sum(len(row.get("case_ids", [])) for row in workflows),
        "partial_source_mappings": len(index.get("mappings", [])),
    }
    if expected_counts != actual_counts:
        raise CampaignError("manifest materialized input index counts differ from the index")

    ids: set[str] = set()
    inputs: set[str] = set()
    loaded: list[dict[str, Any]] = []
    for row in workflows:
        workflow_id = row.get("id")
        if not isinstance(workflow_id, str) or workflow_id in ids:
            raise CampaignError("materialized input index has a duplicate or malformed workflow id")
        ids.add(workflow_id)
        input_path, input_relative = _repo_path(row.get("input_path"), "indexed input path")
        if input_relative in inputs:
            raise CampaignError("materialized input index has a duplicate input path")
        inputs.add(input_relative)
        if not input_relative.startswith("tests/fixtures/inputs/parity/"):
            raise CampaignError(
                f"indexed input is outside the active parity inputs: {input_relative}"
            )
        if sha256_file(input_path) != row.get("input_sha256"):
            raise CampaignError(f"indexed workflow input digest is stale: {workflow_id}")
        workflow = _read_json_object(input_path, f"indexed workflow {workflow_id}")
        workflow_schema = workflow.get("schema")
        schema_path = RECIPE_WORKFLOW_SCHEMAS.get(workflow_schema)
        if schema_path is None:
            raise CampaignError(f"indexed workflow has an unsupported schema: {workflow_schema!r}")
        _schema_errors(workflow, schema_path, f"indexed workflow {workflow_id}")
        if row.get("workflow_schema") is not None and row.get("workflow_schema") != workflow_schema:
            raise CampaignError(f"indexed workflow schema differs from its input: {workflow_id}")
        if workflow_schema not in PROCESS_WORKFLOW_SCHEMA_IDS:
            workload = workflow.get("workload")
            workload_path, workload_relative = _repo_path(
                row.get("workload_path"), f"indexed workload path for {workflow_id}"
            )
            if (
                not isinstance(workload, dict)
                or workload.get("file") != workload_relative
                or workload.get("factory") is None
                or sha256_file(workload_path) != row.get("workload_sha256")
            ):
                raise CampaignError(f"indexed workflow workload is stale: {workflow_id}")
        case_ids = row.get("case_ids")
        case_contracts = row.get("case_contracts")
        if not isinstance(case_ids, list) or not isinstance(case_contracts, list):
            raise CampaignError(f"workflow is missing case ids or case contracts: {workflow_id}")
        case_ids_from_workflow = [case.get("case_id") for case in workflow.get("cases", [])]
        contract_ids = [contract.get("case_id") for contract in case_contracts]
        if (
            len(set(case_ids)) != len(case_ids)
            or len(set(contract_ids)) != len(contract_ids)
            or set(case_ids) != set(contract_ids)
            or case_ids != case_ids_from_workflow
        ):
            raise CampaignError(
                "case_ids and case_contracts are not a bijection with the workflow cases: "
                f"{workflow_id}"
            )
        contracts_by_id = {contract["case_id"]: contract for contract in case_contracts}
        cases_by_id = {case["case_id"]: case for case in workflow["cases"]}
        for case_id, contract in contracts_by_id.items():
            try:
                lane = verification_mode(cases_by_id[case_id])
            except (ValueError, KeyError) as exc:
                raise CampaignError(
                    f"invalid verification lane for {workflow_id}/{case_id}: {exc}"
                ) from exc
            if contract.get("verification") != lane:
                raise CampaignError(
                    f"case contract lane differs from workflow: {workflow_id}/{case_id}"
                )
            refs = contract.get("requirement_refs")
            if (
                not isinstance(refs, list)
                or not refs
                or any(not isinstance(ref, str) or not ref for ref in refs)
                or len(set(refs)) != len(refs)
            ):
                raise CampaignError(
                    f"case contract requirement refs are malformed: {workflow_id}/{case_id}"
                )
        extension = row.get("oracle_profile_extension")
        workflow_extension = workflow.get("oracle_profile_extension")
        if workflow_extension is not None and workflow_extension != extension:
            raise CampaignError(f"indexed profile extension differs from workflow: {workflow_id}")
        loaded.append(
            {
                "row": row,
                "workflow": workflow,
                "workflow_schema": workflow_schema,
                "input_path": input_path,
                "input_relative": input_relative,
                "contracts_by_id": contracts_by_id,
                "cases_by_id": cases_by_id,
                "index_path": index_path,
                "index_relative": index_relative,
            }
        )
    return index, loaded, index_digest


def _option(argv: list[str], option: str) -> str:
    positions = [index for index, value in enumerate(argv) if value == option]
    if len(positions) != 1 or positions[0] + 1 >= len(argv):
        raise CampaignError(f"runner argv must contain exactly one {option} value")
    return argv[positions[0] + 1]


def _same_repo_path(value: str, expected: str) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        expected_path, _ = _repo_path(expected, "expected input path")
    except CampaignError:
        return False
    actual_candidate = Path(value)
    actual = (
        actual_candidate if actual_candidate.is_absolute() else ROOT / actual_candidate
    ).resolve()
    if not _inside(actual, ROOT.resolve()):
        return False
    return actual == expected_path


def _module_identity(argv: Any, module: str, label: str) -> None:
    if (
        not isinstance(argv, list)
        or len(argv) < 3
        or not isinstance(argv[0], str)
        or not Path(argv[0]).is_absolute()
        or argv[1:3] != ["-m", module]
    ):
        raise CampaignError(f"{label} runner identity is not {module}")


def _json_option(argv: list[str], option: str, expected: dict[str, Any], label: str) -> None:
    try:
        value = json.loads(_option(argv, option))
    except (json.JSONDecodeError, CampaignError) as exc:
        raise CampaignError(f"{label} profile argument is malformed") from exc
    if value != expected:
        raise CampaignError(f"{label} profile argument differs from the current manifest")


def _validate_runner_identity(
    *,
    workflow: dict[str, Any],
    row: dict[str, Any],
    comparison: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    manifest: dict[str, Any],
    workflow_path: str,
    workflow_schema: str,
    workload_sha256: str | None,
    source_path: str,
    target_path: str,
) -> dict[str, Any]:
    is_api = workflow_schema in API_WORKFLOW_SCHEMA_IDS
    source_module = "scripts.parity.api_worker" if is_api else "scripts.parity.worker"
    target_module = "scripts.parity.api_target_worker" if is_api else "scripts.parity.target_worker"
    compare_command = "api-compare" if is_api else "compare"
    source_command = source.get("command")
    target_command = target.get("command")
    source_argv = source_command.get("argv") if isinstance(source_command, dict) else None
    target_argv = target_command.get("argv") if isinstance(target_command, dict) else None
    comparison_command = comparison.get("command")
    if not isinstance(comparison_command, dict) or comparison_command.get("cwd") != ".":
        raise CampaignError("comparison runner command record is malformed")
    comparison_argv = comparison_command.get("argv")
    _module_identity(source_argv, source_module, "oracle")
    _module_identity(target_argv, target_module, "target")
    _module_identity(comparison_argv, "scripts.parity.cli", "comparison")
    if comparison_argv[3:4] != [compare_command]:
        raise CampaignError(f"comparison runner is not the {compare_command} command")
    for label, argv in (("oracle", source_argv), ("target", target_argv)):
        if not isinstance(argv, list) or not _same_repo_path(
            _option(argv, "--input"), workflow_path
        ):
            raise CampaignError(f"{label} runner input path differs from the indexed input")
        if _option(argv, "--manifest-sha256") != comparison["manifest"]["sha256"]:
            raise CampaignError(f"{label} runner manifest digest differs from the comparison")
        if _option(argv, "--input-sha256") != comparison["input"]["sha256"]:
            raise CampaignError(f"{label} runner input digest differs from the comparison")
    if not _same_repo_path(_option(comparison_argv, "--input"), workflow_path):
        raise CampaignError("comparison runner input path differs from the indexed input")
    if not _same_repo_path(_option(comparison_argv, "--source-result"), source_path):
        raise CampaignError("comparison runner source result path differs from its artifact ref")
    if not _same_repo_path(_option(comparison_argv, "--target-result"), target_path):
        raise CampaignError("comparison runner target result path differs from its artifact ref")

    extension = row.get("oracle_profile_extension")
    if is_api:
        if extension:
            for label, argv in (
                ("oracle", source_argv),
                ("target", target_argv),
                ("comparison", comparison_argv),
            ):
                if _option(argv, "--profile-extension") != extension:
                    raise CampaignError(f"{label} runner profile extension differs from the index")
        else:
            for label, argv in (
                ("oracle", source_argv),
                ("target", target_argv),
                ("comparison", comparison_argv),
            ):
                if "--profile-extension" in argv:
                    raise CampaignError(f"{label} runner selected an unindexed profile extension")
    oracle_profile = select_oracle_profile(manifest, extension)
    target_profile = select_target_profile(manifest, extension)
    if is_api:
        _json_option(source_argv, "--oracle-profile", oracle_profile, "oracle")
        target_command_profile = {
            "python": manifest["oracle_profile"]["python"],
            "shared_runtime_packages": {
                name: version
                for name, version in manifest["oracle_profile"]["packages"].items()
                if name in SHARED_ORACLE_PACKAGES
            },
            "target": target_profile,
        }
        _json_option(target_argv, "--target-profile", target_command_profile, "target")
        workload = workflow["workload"]
        expected_result_scope = "direct-python-api"
    else:
        _json_option(source_argv, "--oracle-profile", oracle_profile, "oracle")
        target_command_profile = {
            "python": manifest["oracle_profile"]["python"],
            "shared_runtime_packages": {
                name: version
                for name, version in manifest["oracle_profile"]["packages"].items()
                if name in SHARED_ORACLE_PACKAGES
            },
            "target": target_profile,
        }
        _json_option(target_argv, "--target-profile", target_command_profile, "target")
        workload = workflow["workload"]
        expected_result_scope = "input-defined-slice"
    if workload_sha256 is None:
        raise CampaignError("non-process workflow is missing its workload digest")
    for label, argv in (("oracle", source_argv), ("target", target_argv)):
        if _option(argv, "--workload-sha256") != workload_sha256:
            raise CampaignError(f"{label} runner workload digest differs from the index")
    if comparison.get("scope") != expected_result_scope:
        raise CampaignError("comparison scope differs from its workflow kind")
    if not _same_repo_path(workload.get("file"), row["workload_path"]):
        raise CampaignError("workflow workload path differs from the materialized index")
    if source.get("workload") != {
        "path": workload["file"],
        "sha256": workload_sha256,
        "factory": workload["factory"],
    } or target.get("workload") != source.get("workload"):
        raise CampaignError("product workload identities differ from the indexed workload")
    return {
        "oracle": {"id": oracle_profile["id"], "packages": oracle_profile["packages"]},
        "target": {
            "id": target_profile["id"],
            "version": target_profile["version"],
            "starlette_rs_distribution": target_profile["starlette_rs_distribution"],
            "optional_runtime_packages": target_profile.get("optional_runtime_packages", {}),
        },
        "runners": {
            "oracle": source_module,
            "target": target_module,
            "comparison": f"scripts.parity.cli {compare_command}",
        },
    }


def _validate_target_revision(target: dict[str, Any], current_identity: dict[str, Any]) -> None:
    identity = target.get("identity")
    repositories = identity.get("repositories") if isinstance(identity, dict) else None
    current_revision = current_identity.get("revision")
    if current_revision is None:
        raise CampaignError("cannot verify current FastAPI-RS target revision")
    if not isinstance(identity, dict) or not isinstance(repositories, dict):
        raise CampaignError("target result has no target identity")
    if identity.get("target_revision") != current_revision:
        raise CampaignError("target result revision differs from the current FastAPI-RS checkout")
    if repositories.get("fastapi_rs") != current_revision:
        raise CampaignError("target repository revision differs from its runtime identity")
    if not current_identity.get("clean"):
        raise CampaignError("current FastAPI-RS or Starlette-RS target source checkout is dirty")
    if not current_identity.get("starlette_rs_profile_matches"):
        raise CampaignError("current Starlette-RS checkout differs from the pinned profile")
    current_source_tree_sha256 = current_identity.get("source_tree_sha256")
    if (
        not isinstance(current_source_tree_sha256, str)
        or identity.get("source_tree_sha256") != current_source_tree_sha256
    ):
        raise CampaignError(
            "target result source-tree digest differs from the current target source"
        )


def _load_result_reference(
    reference: Any,
    *,
    product: str,
    process: bool,
    workflow_schema: str,
) -> tuple[dict[str, Any], str, str]:
    if not isinstance(reference, dict) or reference.get("product") != product:
        raise CampaignError(f"comparison {product} result reference is malformed")
    result_path, relative = _artifact_path(reference.get("path"), f"{product} result path")
    result = _read_json_object(result_path, f"{product} result artifact")
    digest = sha256_file(result_path)
    if digest != reference.get("sha256"):
        raise CampaignError(f"{product} result digest differs from its comparison reference")
    if result.get("run_id") != reference.get("run_id") or result.get("product") != product:
        raise CampaignError(f"{product} result identity differs from its comparison reference")
    if process:
        expected = PROCESS_RESULT_SCHEMAS.get(workflow_schema)
        if expected is None:
            raise CampaignError("process result schema is not supported")
        schema_id, schema_path = expected
        _validate_process_schema(result, schema_path, f"{product} process result")
    else:
        schema_id = RESULT_SCHEMA_IDS_BY_WORKFLOW.get(workflow_schema)
        schema_path = RESULT_SCHEMAS.get(schema_id)
        if schema_id is None or schema_path is None:
            raise CampaignError(f"workflow result schema is unsupported: {workflow_schema}")
        _schema_errors(result, schema_path, f"{product} result")
    if result.get("schema") != schema_id:
        raise CampaignError(f"{product} result schema differs from the indexed workflow")
    return result, relative, digest


def _validate_process_comparison(
    *,
    candidate: dict[str, Any],
    entry: dict[str, Any],
    manifest: dict[str, Any],
    manifest_sha256: str,
    current_target_identity: dict[str, Any],
) -> dict[str, Any]:
    workflow = entry["workflow"]
    row = entry["row"]
    workflow_schema = entry["workflow_schema"]
    comparison = candidate["value"]
    comparison_schema = PROCESS_COMPARISON_SCHEMAS.get(workflow_schema)
    if comparison_schema is None:
        raise CampaignError(f"process comparison schema is unsupported: {workflow_schema}")
    comparison_schema_id, comparison_schema_path = comparison_schema
    _validate_process_schema(comparison, comparison_schema_path, "process comparison")
    if comparison.get("schema") != comparison_schema_id:
        raise CampaignError("process comparison schema differs from its workflow")
    if comparison.get("manifest") != {
        "path": "tests/fixtures/manifest.yaml",
        "sha256": manifest_sha256,
    }:
        raise CampaignError("process comparison manifest differs from the current manifest")
    if comparison.get("input") != {
        "path": entry["input_relative"],
        "sha256": row["input_sha256"],
        "schema": workflow_schema,
    }:
        raise CampaignError("process comparison input differs from the current indexed input")

    source, source_path, source_digest = _load_result_reference(
        comparison.get("source_result"),
        product="oracle",
        process=True,
        workflow_schema=workflow_schema,
    )
    target, target_path, target_digest = _load_result_reference(
        comparison.get("target_result"),
        product="target",
        process=True,
        workflow_schema=workflow_schema,
    )
    _validate_target_revision(target, current_target_identity)
    target_identity = target["identity"]
    starlette_rs = manifest["target"]["starlette_rs_distribution"]
    if target_identity.get("repositories", {}).get("starlette_rs") != starlette_rs["commit"]:
        raise CampaignError("process target Starlette-RS revision differs from the current profile")

    argv = comparison.get("command")
    if (
        not isinstance(argv, list)
        or len(argv) != 10
        or not Path(argv[0]).is_absolute()
        or argv[1:4] != ["-m", "scripts.parity.process_worker", "compare"]
        or argv[4] != "--input"
        or not _same_repo_path(argv[5], entry["input_relative"])
        or argv[6] != "--source-result"
        or argv[7] != source_path
        or argv[8] != "--target-result"
        or argv[9] != target_path
    ):
        raise CampaignError("process comparison runner identity or artifact paths are invalid")

    expected = compare_process_workflow_results(
        workflow=workflow,
        source=source,
        target=target,
        manifest_sha256=manifest_sha256,
        input_path=entry["input_relative"],
        input_sha256=row["input_sha256"],
        source_result_ref=comparison["source_result"],
        target_result_ref=comparison["target_result"],
        command=argv,
    )
    stable_fields = (
        "schema",
        "status",
        "manifest",
        "input",
        "source_result",
        "target_result",
        "cases",
        "summary",
        "command",
    )
    if any(comparison.get(field) != expected.get(field) for field in stable_fields):
        raise CampaignError("process comparison does not match a fresh identity-checked comparison")
    return _comparison_evidence(
        candidate,
        comparison,
        source,
        target,
        source_path,
        source_digest,
        target_path,
        target_digest,
        profiles={
            "oracle": {
                "id": source["profile"]["id"],
                "sha256": source["identity"]["profile_sha256"],
            },
            "target": {
                "id": target["profile"]["id"],
                "sha256": target["identity"]["profile_sha256"],
            },
        },
        runners={
            "oracle": "FastAPI CLI entrypoint identity",
            "target": "FastAPI-RS CLI entrypoint identity",
            "comparison": "scripts.parity.process_worker compare",
        },
    )


def _validate_api_asgi_comparison(
    *,
    candidate: dict[str, Any],
    entry: dict[str, Any],
    manifest: dict[str, Any],
    manifest_sha256: str,
    current_target_identity: dict[str, Any],
) -> dict[str, Any]:
    workflow = entry["workflow"]
    row = entry["row"]
    workflow_schema = entry["workflow_schema"]
    comparison = candidate["value"]
    is_api = workflow_schema in API_WORKFLOW_SCHEMA_IDS
    if is_api:
        comparison_schema_id = API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW.get(workflow_schema)
        comparison_schema_path = API_COMPARISON_SCHEMAS_BY_ID.get(comparison_schema_id)
    else:
        comparison_schema_id = COMPARISON_SCHEMA_IDS_BY_WORKFLOW.get(workflow_schema)
        comparison_schema_path = COMPARISON_SCHEMAS.get(comparison_schema_id)
    if comparison_schema_id is None or comparison_schema_path is None:
        raise CampaignError(f"comparison schema is unsupported for workflow {workflow_schema}")
    if comparison.get("schema") != comparison_schema_id:
        raise CampaignError("comparison schema differs from the indexed workflow")
    _schema_errors(comparison, comparison_schema_path, "comparison result")
    expected_scope = "direct-python-api" if is_api else "input-defined-slice"
    if comparison.get("scope") != expected_scope:
        raise CampaignError("comparison scope differs from the indexed workflow")
    if comparison.get("status") != "completed":
        raise CampaignError("comparison status is not completed")
    if comparison.get("manifest") != {
        "path": "tests/fixtures/manifest.yaml",
        "sha256": manifest_sha256,
    }:
        raise CampaignError("comparison manifest differs from the current manifest")
    expected_input = {
        "path": entry["input_relative"],
        "sha256": row["input_sha256"],
        "schema": workflow_schema,
    }
    if comparison.get("input") != expected_input:
        raise CampaignError("comparison input differs from the current indexed input")

    source, source_path, source_digest = _load_result_reference(
        comparison.get("source_result"),
        product="oracle",
        process=False,
        workflow_schema=workflow_schema,
    )
    target, target_path, target_digest = _load_result_reference(
        comparison.get("target_result"),
        product="target",
        process=False,
        workflow_schema=workflow_schema,
    )
    _validate_target_revision(target, current_target_identity)
    target_identity = target.get("identity", {})
    starlette_rs = manifest["target"]["starlette_rs_distribution"]
    if target_identity.get("repositories", {}).get("starlette_rs") != starlette_rs["commit"]:
        raise CampaignError("target Starlette-RS revision differs from the current profile")
    if target_identity.get("packages", {}).get("starlette-rs-py") != starlette_rs["version"]:
        raise CampaignError("target Starlette-RS version differs from the current profile")

    workload = workflow.get("workload")
    workload_sha256 = row.get("workload_sha256")
    if not isinstance(workload, dict) or not isinstance(workload_sha256, str):
        raise CampaignError("indexed workflow workload identity is missing")
    profiles = _validate_runner_identity(
        workflow=workflow,
        row=row,
        comparison=comparison,
        source=source,
        target=target,
        manifest=manifest,
        workflow_path=entry["input_relative"],
        workflow_schema=workflow_schema,
        workload_sha256=workload_sha256,
        source_path=source_path,
        target_path=target_path,
    )
    oracle_profile = select_oracle_profile(manifest, row.get("oracle_profile_extension"))
    target_profile = select_target_profile(manifest, row.get("oracle_profile_extension"))
    source_reference = comparison["source_result"]
    target_reference = comparison["target_result"]
    command_argv = comparison["command"]["argv"]
    if is_api:
        expected = compare_api_workflow_results(
            workflow=workflow,
            source=source,
            target=target,
            oracle_profile=oracle_profile,
            target_profile=target_profile,
            manifest_sha256=manifest_sha256,
            input_path=entry["input_relative"],
            input_sha256=row["input_sha256"],
            workload_sha256=workload_sha256,
            source_result_ref=source_reference,
            target_result_ref=target_reference,
            command=command_argv,
        )
    else:
        expected = compare_workflow_results(
            workflow=workflow,
            source=source,
            target=target,
            oracle_profile=oracle_profile,
            target_profile=target_profile,
            manifest_sha256=manifest_sha256,
            input_path=entry["input_relative"],
            input_sha256=row["input_sha256"],
            workload_sha256=workload_sha256,
            source_result_ref=source_reference,
            target_result_ref=target_reference,
            command=command_argv,
        )
    stable_fields = (
        "schema",
        "scope",
        "manifest",
        "input",
        "source_result",
        "target_result",
        "command",
        "status",
        "summary",
        "cases",
        "infrastructure_errors",
    )
    if any(comparison.get(field) != expected.get(field) for field in stable_fields):
        raise CampaignError("comparison does not match a fresh identity-checked comparison")
    return _comparison_evidence(
        candidate,
        comparison,
        source,
        target,
        source_path,
        source_digest,
        target_path,
        target_digest,
        profiles={"oracle": profiles["oracle"], "target": profiles["target"]},
        runners=profiles["runners"],
    )


def _comparison_evidence(
    candidate: dict[str, Any],
    comparison: dict[str, Any],
    source: dict[str, Any],
    target: dict[str, Any],
    source_path: str,
    source_digest: str,
    target_path: str,
    target_digest: str,
    *,
    profiles: dict[str, Any],
    runners: dict[str, str],
) -> dict[str, Any]:
    source_identity = source.get("identity", {})
    target_identity = target.get("identity", {})
    source_repositories = source_identity.get("repositories", {})
    target_repositories = target_identity.get("repositories", {})
    oracle_identity = {
        "fastapi_commit": source_repositories.get("fastapi_source"),
        "starlette_commit": source_repositories.get("starlette_source"),
        "python": source_identity.get("python"),
        "entrypoint": source_identity.get("entrypoint"),
        "profile_sha256": source_identity.get("profile_sha256"),
    }
    for field in ("distribution", "version"):
        if field in source_identity:
            oracle_identity[field] = source_identity[field]
    return {
        "comparison": {
            "path": candidate["relative_path"],
            "sha256": candidate["sha256"],
            "schema": comparison["schema"],
            "id": comparison.get("run_id", comparison.get("comparison_id")),
        },
        "source_result": {
            "path": source_path,
            "sha256": source_digest,
            "run_id": source["run_id"],
        },
        "target_result": {
            "path": target_path,
            "sha256": target_digest,
            "run_id": target["run_id"],
        },
        "profiles": profiles,
        "runners": runners,
        "identities": {
            "oracle": oracle_identity,
            "target": {
                "distribution": target_identity.get("distribution"),
                "version": target_identity.get("version"),
                "target_revision": target_identity.get("target_revision"),
                "fastapi_rs_commit": target_repositories.get("fastapi_rs"),
                "starlette_rs_commit": target_repositories.get("starlette_rs"),
                "starlette_rs_version": target_identity.get("packages", {}).get("starlette-rs-py"),
                "source_tree_sha256": target_identity.get("source_tree_sha256"),
                "target_binary_sha256": target_identity.get("target_binary_sha256"),
                "entrypoint": target_identity.get("entrypoint"),
                "profile_sha256": target_identity.get("profile_sha256"),
            },
        },
    }


def _candidate_header(path_value: str) -> dict[str, Any]:
    resolved, relative = _artifact_path(path_value, "comparison path")
    value = _read_json_object(resolved, "comparison artifact")
    input_value = value.get("input")
    input_path = input_value.get("path") if isinstance(input_value, dict) else None
    return {
        "path": resolved,
        "relative_path": relative,
        "sha256": sha256_file(resolved),
        "value": value,
        "input_path": input_path,
        "case_ids": [
            case.get("case_id")
            for case in value.get("cases", [])
            if isinstance(case, dict) and isinstance(case.get("case_id"), str)
        ]
        if isinstance(value.get("cases"), list)
        else [],
    }


def _case_outcomes(
    comparison: dict[str, Any],
    *,
    process: bool,
) -> dict[str, dict[str, Any]]:
    rows = comparison.get("cases")
    if not isinstance(rows, list):
        raise CampaignError("comparison cases are missing")
    outcomes: dict[str, dict[str, Any]] = {}
    for case in rows:
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
            raise CampaignError("comparison case record is malformed")
        case_id = case["case_id"]
        if case_id in outcomes:
            raise CampaignError(f"comparison repeats a case id: {case_id}")
        if process:
            outcome = case.get("status")
            if outcome == "matched":
                outcome = "pass"
            elif outcome == "mismatched":
                outcome = "fail"
            verification = "parity"
        else:
            outcome = case.get("outcome")
            verification = case.get("verification", "parity")
        if outcome not in {"pass", "fail", "not_run"}:
            raise CampaignError(f"comparison has an unsupported case outcome: {case_id}")
        if verification not in {"parity", "fault-contract"}:
            raise CampaignError(f"comparison has an unsupported verification lane: {case_id}")
        outcomes[case_id] = {
            "outcome": outcome,
            "verification": verification,
            "reason": case.get("reason"),
            "contract_id": case.get("contract_id"),
        }
    return outcomes


def _new_row(
    entry: dict[str, Any], case_id: str, requirement_ref: str, lane: str
) -> dict[str, Any]:
    row = entry["row"]
    result = {
        "workflow_id": row["id"],
        "workflow_schema": entry["workflow_schema"],
        "input_path": entry["input_relative"],
        "input_sha256": row["input_sha256"],
        "case_id": case_id,
        "requirement_ref": requirement_ref,
        "status": "not_run",
        "reason": "no compatible comparison evidence was selected",
        "evidence": None,
    }
    if lane == "fault-contract":
        result["fault"] = entry["contracts_by_id"][case_id]["fault"]
    return result


def _invalid_record(
    candidate: dict[str, Any], reason: str, affected_cases: list[str]
) -> dict[str, Any]:
    return {
        "path": candidate["relative_path"],
        "sha256": candidate["sha256"],
        "status": "invalid",
        "reason": reason,
        "affected_case_ids": sorted(set(affected_cases)),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(row["status"] for row in rows)
    return {
        "requirement_count": len(rows),
        "passed": counts["pass"],
        "failed": counts["fail"],
        "not_run": counts["not_run"],
    }


def build_campaign_report(comparison_paths: list[str]) -> dict[str, Any]:
    manifest = read_manifest()
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    manifest_sha256 = sha256_file(manifest_path)
    index, entries, index_sha256 = _validate_index_and_workflows(manifest)
    current_target_identity = _current_target_source_identity(manifest)
    by_input = {entry["input_relative"]: entry for entry in entries}
    by_workflow = {entry["row"]["id"]: entry for entry in entries}
    by_case_id: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for entry in entries:
        workflow_id = entry["row"]["id"]
        for case_id, contract in entry["contracts_by_id"].items():
            by_case_id[case_id].append((workflow_id, contract["verification"]))

    parity_rows: list[dict[str, Any]] = []
    fault_rows: list[dict[str, Any]] = []
    for entry in entries:
        for case_id, contract in entry["contracts_by_id"].items():
            destination = (
                fault_rows if contract["verification"] == "fault-contract" else parity_rows
            )
            for requirement_ref in contract["requirement_refs"]:
                row = _new_row(entry, case_id, requirement_ref, contract["verification"])
                destination.append(row)
    for rows in (parity_rows, fault_rows):
        rows.sort(key=lambda row: (row["workflow_id"], row["case_id"], row["requirement_ref"]))

    candidates_by_workflow: dict[str, list[dict[str, Any]]] = defaultdict(list)
    invalid_evidence: list[dict[str, Any]] = []
    invalid_for_case: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    seen_paths: set[str] = set()
    for raw_path in comparison_paths:
        try:
            candidate = _candidate_header(raw_path)
        except (CampaignError, OSError, ValueError) as exc:
            invalid_evidence.append(
                {
                    "path": raw_path,
                    "sha256": None,
                    "status": "invalid",
                    "reason": str(exc),
                    "affected_case_ids": [],
                }
            )
            continue
        if candidate["relative_path"] in seen_paths:
            continue
        seen_paths.add(candidate["relative_path"])
        input_path = candidate["input_path"]
        entry = by_input.get(input_path) if isinstance(input_path, str) else None
        if entry is None:
            reason = (
                "comparison input path must be a string"
                if input_path is not None and not isinstance(input_path, str)
                else "comparison input path is not in the current index"
            )
            invalid_evidence.append(_invalid_record(candidate, reason, candidate["case_ids"]))
            for case_id in set(candidate["case_ids"]):
                for workflow_id, lane in by_case_id.get(case_id, []):
                    invalid_for_case[(workflow_id, case_id, lane)].append(
                        f"{candidate['relative_path']}: {reason}"
                    )
            continue
        candidate["workflow_id"] = entry["row"]["id"]
        candidates_by_workflow[entry["row"]["id"]].append(candidate)

    accepted_comparisons: list[dict[str, Any]] = []
    evidence_for_case: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for workflow_id in sorted(candidates_by_workflow):
        entry = by_workflow[workflow_id]
        candidates = sorted(
            candidates_by_workflow[workflow_id], key=lambda item: item["relative_path"]
        )
        parsed: list[tuple[dict[str, Any], dict[str, Any] | None, str | None]] = []
        for candidate in candidates:
            try:
                workflow_schema = entry["workflow_schema"]
                if workflow_schema in PROCESS_WORKFLOW_SCHEMA_IDS:
                    evidence = _validate_process_comparison(
                        candidate=candidate,
                        entry=entry,
                        manifest=manifest,
                        manifest_sha256=manifest_sha256,
                        current_target_identity=current_target_identity,
                    )
                elif workflow_schema in SUPPORTED_PARITY_WORKFLOW_SCHEMAS:
                    evidence = _validate_api_asgi_comparison(
                        candidate=candidate,
                        entry=entry,
                        manifest=manifest,
                        manifest_sha256=manifest_sha256,
                        current_target_identity=current_target_identity,
                    )
                else:
                    raise CampaignError(
                        f"workflow schema is not in the parity campaign: {workflow_schema}"
                    )
                parsed.append((candidate, evidence, None))
            except (CampaignError, OSError, ValueError, KeyError, TypeError) as exc:
                parsed.append((candidate, None, str(exc)))
                invalid_evidence.append(_invalid_record(candidate, str(exc), candidate["case_ids"]))

        valid_candidates: list[
            tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]
        ] = []
        expected_case_ids = set(entry["contracts_by_id"])
        for candidate, evidence, error in parsed:
            if evidence is None:
                for case_id, contract in entry["contracts_by_id"].items():
                    invalid_for_case[(workflow_id, case_id, contract["verification"])].append(
                        f"{candidate['relative_path']}: {error}"
                    )
                continue
            try:
                outcomes = _case_outcomes(
                    candidate["value"],
                    process=entry["workflow_schema"] in PROCESS_WORKFLOW_SCHEMA_IDS,
                )
            except CampaignError as exc:
                reason = str(exc)
                invalid_evidence.append(_invalid_record(candidate, reason, candidate["case_ids"]))
                for case_id, contract in entry["contracts_by_id"].items():
                    invalid_for_case[(workflow_id, case_id, contract["verification"])].append(
                        f"{candidate['relative_path']}: {reason}"
                    )
                continue
            reasons: list[str] = []
            if set(outcomes) != expected_case_ids:
                reasons.append("comparison case set differs from the indexed workflow")
            if any(
                case_id not in entry["contracts_by_id"]
                or entry["contracts_by_id"][case_id]["verification"] != outcome["verification"]
                for case_id, outcome in outcomes.items()
            ):
                reasons.append(
                    "comparison case verification lane differs from the indexed contract"
                )
            if reasons:
                reason = "; ".join(reasons)
                affected = sorted(expected_case_ids | set(candidate["case_ids"]) | set(outcomes))
                invalid_evidence.append(_invalid_record(candidate, reason, affected))
                for case_id in affected:
                    contract = entry["contracts_by_id"].get(case_id)
                    if contract is not None:
                        invalid_for_case[(workflow_id, case_id, contract["verification"])].append(
                            f"{candidate['relative_path']}: {reason}"
                        )
                continue
            valid_candidates.append((candidate, evidence, outcomes))

        owners: dict[tuple[str, str], list[str]] = defaultdict(list)
        for candidate, _evidence, outcomes in valid_candidates:
            for case_id, outcome in outcomes.items():
                owners[(case_id, outcome["verification"])].append(candidate["relative_path"])
        conflicts_by_path: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for key, paths in owners.items():
            if len(paths) < 2:
                continue
            for path in set(paths):
                conflicts_by_path[path].add(key)

        for candidate, evidence, outcomes in valid_candidates:
            candidate_path = candidate["relative_path"]
            conflicts = conflicts_by_path.get(candidate_path, set())
            if conflicts:
                conflict_cases = sorted(case_id for case_id, _lane in conflicts)
                reason = (
                    "compatible comparison overlaps another selected artifact at: "
                    + ", ".join(conflict_cases)
                )
                affected = sorted(outcomes)
                invalid_evidence.append(_invalid_record(candidate, reason, affected))
                for case_id, outcome in outcomes.items():
                    invalid_for_case[(workflow_id, case_id, outcome["verification"])].append(
                        f"{candidate_path}: {reason}"
                    )
                continue
            accepted_comparisons.append(evidence)
            for case_id, outcome in outcomes.items():
                lane = outcome["verification"]
                evidence_for_case[(workflow_id, case_id, lane)].append(
                    {
                        "comparison": evidence["comparison"],
                        "outcome": outcome["outcome"],
                        "reason": outcome["reason"],
                        "profiles": evidence["profiles"],
                        "runners": evidence["runners"],
                    }
                )

    for rows in (parity_rows, fault_rows):
        for row in rows:
            key = (
                row["workflow_id"],
                row["case_id"],
                "fault-contract" if "fault" in row else "parity",
            )
            valid_evidence = evidence_for_case.get(key, [])
            invalid_reasons = sorted(set(invalid_for_case.get(key, [])))
            if len(valid_evidence) > 1:
                row["reason"] = (
                    "no compatible comparison evidence was selected; conflicting artifacts"
                )
                continue
            if valid_evidence:
                evidence = valid_evidence[0]
                row["status"] = evidence["outcome"]
                row["reason"] = evidence["reason"] or (
                    "comparison marked this case not_run"
                    if evidence["outcome"] == "not_run"
                    else ""
                )
                row["evidence"] = {
                    "comparison": evidence["comparison"],
                    "case_outcome": evidence["outcome"],
                    "profiles": evidence["profiles"],
                    "runners": evidence["runners"],
                }
            elif invalid_reasons:
                row["reason"] = "no compatible comparison evidence was selected; " + "; ".join(
                    invalid_reasons
                )

    invalid_evidence.sort(key=lambda item: (str(item.get("path")), str(item.get("reason"))))
    accepted_comparisons.sort(key=lambda item: item["comparison"]["path"])
    api_contract = manifest.get("api_surface_contract", {})
    contract = manifest.get("contract", {})
    target = manifest.get("target", {})
    oracle = manifest.get("oracle_profile", {})
    starlette_rs = target.get("starlette_rs_distribution", {})
    report = {
        "schema": REPORT_SCHEMA_ID,
        "denominator": "declared-indexed-fixtures",
        "foundation": {
            "contract_status": contract.get("status"),
            "api_surface_contract_status": api_contract.get("status"),
            "api_scope_counts": api_contract.get("counts", {}),
        },
        "identity": {
            "fastapi": {
                "version": oracle.get("packages", {}).get("fastapi"),
                "commit": oracle.get("source_commits", {}).get("fastapi"),
            },
            "starlette": {
                "version": oracle.get("packages", {}).get("starlette"),
                "commit": oracle.get("source_commits", {}).get("starlette"),
            },
            "starlette_rs": {
                "name": starlette_rs.get("name"),
                "version": starlette_rs.get("version"),
                "contract": starlette_rs.get("starlette_contract"),
                "commit": starlette_rs.get("commit"),
            },
            "target": {
                "distribution": "fastapi-rs",
                "version": target.get("version"),
                "current_revision": current_target_identity["revision"],
                "source_tree_sha256": current_target_identity["source_tree_sha256"],
                "source_clean": current_target_identity["clean"],
                "starlette_rs_revision": current_target_identity["starlette_rs_revision"],
                "starlette_rs_profile_matches": current_target_identity[
                    "starlette_rs_profile_matches"
                ],
            },
            "manifest": {"path": "tests/fixtures/manifest.yaml", "sha256": manifest_sha256},
            "materialized_index": {
                "path": manifest["source_artifacts"]["materialized_input_index"]["path"],
                "sha256": index_sha256,
            },
        },
        "scope": {
            "workflow_count": len(entries),
            "case_count": sum(len(entry["row"]["case_ids"]) for entry in entries),
            "parity_requirement_count": len(parity_rows),
            "fault_contract_requirement_count": len(fault_rows),
            "complete_fastapi_behavior_denominator": False,
            "supports_100_percent_compatibility_claim": False,
        },
        "summary": {
            "parity": _summary(parity_rows),
            "fault_contract": _summary(fault_rows),
        },
        "parity_cases": parity_rows,
        "fault_contract_cases": fault_rows,
        "accepted_comparisons": accepted_comparisons,
        "invalid_evidence": invalid_evidence,
    }
    _schema_errors(report, REPORT_SCHEMA_PATH, "parity campaign report")
    return report


def _write_report(report: dict[str, Any], output_dir: Path) -> tuple[Path, str]:
    output_dir = output_dir if output_dir.is_absolute() else ROOT / output_dir
    output_dir = output_dir.resolve()
    if not _inside(output_dir, PARITY_RESULTS_ROOT):
        raise CampaignError("campaign reports must be written inside parity-results/")
    serialized = (
        json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"declared-indexed-fixtures-{digest}.json"
    try:
        with output_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
    except FileExistsError:
        if output_path.read_text(encoding="utf-8") != serialized:
            raise CampaignError(
                f"refusing to replace a different immutable report: {output_path}"
            ) from None
    return output_path, digest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--comparison",
        action="append",
        default=[],
        help="explicit identity-checked comparison artifact (repeatable)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "parity-results/campaign",
        help="ignored parity-results directory for the content-addressed report",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        report = build_campaign_report(args.comparison)
        artifact, digest = _write_report(report, args.output_dir)
    except (
        CampaignError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"parity campaign: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "written",
                "artifact": artifact.relative_to(ROOT).as_posix(),
                "sha256": digest,
                "summary": report["summary"],
                "scope": report["scope"],
            },
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
