#!/usr/bin/env python3
"""Run exactly one source-mapped workflow selected by materialized-index ID."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from scripts.build_parity_inputs import read_recipe
from scripts.parity.contract import (
    API_WORKFLOW_SCHEMA_IDS,
    ROOT,
    ContractError,
    load_workflow,
    read_json,
    read_manifest,
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
from scripts.parity.source_identity import fastapi_rs_source_tree_sha256

MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
INDEXED_INDEX_SCHEMA = "fastapi-rs/materialized-input-index@12"
PROCESS_RESULT_DIR = ROOT / "parity-results/indexed"

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
    "templates": "parity-prepare-oracle-templates",
    "telemetry": "parity-prepare-oracle-telemetry",
    "json-serializers": "parity-prepare-oracle-json-serializers",
}
TARGET_PREP_TARGETS = {
    None: "parity-prepare-target",
    "standard-multipart": "parity-prepare-target-standard-multipart",
    "testclient": "parity-prepare-target-testclient",
    "email-validation": "parity-prepare-target-email-validation",
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
    parser.add_argument(
        "--prepare", action="store_true", help="prepare only this workflow's oracle/target profiles"
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
    if args.prepare:
        _run_prepare(
            oracle_target=ORACLE_PREP_TARGETS[oracle_extension],
            target_target=target_prepare,
            fastapi_source=fastapi_source,
            starlette_source=starlette_source,
            starlette_rs_source=starlette_rs_source,
        )
    for label, python in (("oracle", oracle_python), ("target", target_python)):
        if not python.is_file():
            prepare = ORACLE_PREP_TARGETS[oracle_extension] if label == "oracle" else target_prepare
            raise ContractError(f"{label} profile is not prepared; run make {prepare}")

    target_revision = _git_revision(target_source, "FastAPI-RS")
    starlette_rs_revision = _git_revision(starlette_rs_source, "Starlette-RS")
    target_source_digest = fastapi_rs_source_tree_sha256(target_source, starlette_rs_source)
    indexed_input_sha256 = sha256_file(indexed_workflow_path)
    input_sha256 = sha256_file(workflow_path)
    recipe_path = ROOT / row["recipe_path"]
    recipe_sha256 = sha256_file(recipe_path)
    manifest_sha256 = sha256_file(MANIFEST_PATH)
    index_path = ROOT / manifest["source_artifacts"]["materialized_input_index"]["path"]
    index_sha256 = sha256_file(index_path)
    workload_path = None if is_process else ROOT / row["workload_path"]
    workload_sha256 = None if workload_path is None else sha256_file(workload_path)

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
