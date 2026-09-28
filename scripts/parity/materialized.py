"""Validate concrete workflow mappings back to the pinned FastAPI backlog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.build_parity_inputs import read_recipe
from scripts.parity.contract import (
    ROOT,
    WORKFLOW_SCHEMA_V3_ID,
    ContractError,
    load_workflow,
    read_json,
    sha256_file,
)

INDEX_SCHEMA = ROOT / "tests/fixtures/schemas/materialized-input-index.schema.json"
INDEX_SCHEMA_ID = "fastapi-rs/materialized-input-index@1"


def _fail(message: str) -> None:
    raise ContractError(f"materialized input index: {message}")


def _selected_selectors(case: dict[str, Any], *, workflow_schema: str | None = None) -> set[str]:
    selectors: set[str] = set()
    if "probes" in case:
        for probe in case["probes"]:
            for observation in probe["observations"]:
                if observation["kind"] == "python_return_value":
                    selectors.add("python.attribute_value")
                elif observation["kind"] == "python_signature":
                    selectors.add("python.signature")
        return selectors

    if workflow_schema == WORKFLOW_SCHEMA_V3_ID:
        selectors.update(
            f"construction.{selector}" for selector in case["construction_observation"]["selectors"]
        )
    for action in case["actions"]:
        if action["kind"] == "lifespan":
            selectors.update(
                f"asgi.lifespan.{observation['selector']}" for observation in action["observations"]
            )
            continue
        path = action["scope"]["path"]
        openapi_endpoint = path == "/openapi.json"
        for observation in action["observations"]:
            if observation["kind"] == "websocket":
                selectors.add(f"websocket.{observation['selector']}")
            elif observation["kind"] == "http_response":
                if "status" in observation["selectors"]:
                    selectors.add("http.status")
                    if openapi_endpoint:
                        selectors.add("docs.response.status")
                if "headers" in observation["selectors"]:
                    selectors.add("http.headers.ordered")
                    if openapi_endpoint:
                        selectors.add("docs.response.headers")
                if "body" in observation["selectors"]:
                    selectors.add("http.body.bytes")
                    if openapi_endpoint:
                        selectors.add("docs.response.body.bytes")
            elif observation["kind"] == "openapi":
                pointers = observation["json_pointers"]
                for pointer in pointers:
                    if (
                        pointer.startswith("/components/securitySchemes/")
                        or pointer.endswith("/security")
                        or "/security/" in pointer
                    ):
                        selectors.add("openapi.security")
                    elif pointer.startswith("/paths/"):
                        selectors.add("openapi.document")
                        selectors.add("openapi.paths")
                    else:
                        selectors.add("openapi.document")
            elif (
                observation["kind"] == "application_error"
                and observation["selector"] == "validation_error_class"
            ):
                selectors.add("validation.error_class")
    return selectors


def validate_materialized_input_index(
    index: dict[str, Any],
    *,
    atlas: dict[str, Any],
    backlog: dict[str, Any],
    selector_catalog: dict[str, Any],
    fastapi_source: Path,
) -> dict[str, Any]:
    """Validate workflow digests, concrete source mapping, and observed selectors."""
    schema = read_json(INDEX_SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(index),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        _fail(f"input does not match its schema: {details}")
    if index["schema"] != INDEX_SCHEMA_ID:
        _fail(f"unsupported schema: {index['schema']!r}")
    if index["authority"] != {"fastapi": "0.141.1", "starlette": "1.6.0"}:
        _fail("index authority differs from the selected FastAPI/Starlette contract")

    workflow_by_id = {row["id"]: row for row in index["workflows"]}
    if len(workflow_by_id) != len(index["workflows"]):
        _fail("workflow IDs must be unique")
    mapping_keys = [(row["source_item_id"], row["workflow_id"]) for row in index["mappings"]]
    if len(set(mapping_keys)) != len(index["mappings"]):
        _fail("source item/workflow mappings must be unique")

    coverage_rows = {row["id"]: row for row in atlas["coverage_matrix"]}
    backlog_rows = {row["source_item_id"]: row for row in backlog["fixture_designs"]}
    selector_rows = {row["id"]: row for row in selector_catalog["selectors"] if "id" in row}
    workflow_cases: dict[str, dict[str, dict[str, Any]]] = {}
    workflow_schemas: dict[str, str] = {}
    for workflow_id, workflow_ref in workflow_by_id.items():
        for path_key, digest_key, label in (
            ("input_path", "input_sha256", "workflow input"),
            ("recipe_path", "recipe_sha256", "workflow recipe"),
            ("workload_path", "workload_sha256", "workload"),
        ):
            path = (ROOT / workflow_ref[path_key]).resolve()
            try:
                path.relative_to(ROOT)
            except ValueError as exc:
                raise ContractError(
                    f"materialized input index: {label} escapes the repository"
                ) from exc
            if not path.is_file() or sha256_file(path) != workflow_ref[digest_key]:
                _fail(f"{label} path/digest is missing or stale: {workflow_ref[path_key]}")

        workflow, _, input_digest, workload_path = load_workflow(
            ROOT / workflow_ref["input_path"], source_root=fastapi_source
        )
        if read_recipe(ROOT / workflow_ref["recipe_path"]) != workflow:
            _fail(f"generated workflow differs from its YAML recipe: {workflow_id}")
        if workflow_ref.get("oracle_profile_extension") != workflow.get("oracle_profile_extension"):
            _fail(f"workflow oracle profile extension differs from index: {workflow_id}")
        if input_digest != workflow_ref["input_sha256"]:
            _fail(f"workflow input digest differs from loaded input: {workflow_id}")
        if workload_path.relative_to(ROOT).as_posix() != workflow_ref["workload_path"]:
            _fail(f"workload binding differs from index: {workflow_id}")
        if sha256_file(workload_path) != workflow_ref["workload_sha256"]:
            _fail(f"workload digest differs from loaded workflow: {workflow_id}")
        actual_cases = {case["case_id"]: case for case in workflow["cases"]}
        if set(actual_cases) != set(workflow_ref["case_ids"]):
            _fail(f"workflow case IDs differ from index: {workflow_id}")
        workflow_cases[workflow_id] = actual_cases
        workflow_schemas[workflow_id] = workflow["schema"]

    mapped_cases: dict[str, set[str]] = {workflow_id: set() for workflow_id in workflow_by_id}
    for mapping in index["mappings"]:
        source_id = mapping["source_item_id"]
        coverage = coverage_rows.get(source_id)
        backlog_row = backlog_rows.get(source_id)
        if coverage is None or backlog_row is None:
            _fail(f"source item is absent from the coverage matrix or fixture backlog: {source_id}")
        if (
            coverage["fixture_id"] != mapping["fixture_id"]
            or backlog_row["id"] != mapping["fixture_id"]
        ):
            _fail(f"fixture identity differs from source inventory: {source_id}")

        source_path = coverage["source_path"]
        source_file = (fastapi_source / source_path).resolve()
        try:
            source_file.relative_to(fastapi_source.resolve())
        except ValueError as exc:
            raise ContractError(
                f"materialized input index: source escapes the pinned FastAPI tree: {source_path}"
            ) from exc
        source_digest = coverage["source_sha256"]
        backlog_evidence = backlog_row["source_evidence"]
        if isinstance(backlog_evidence, dict):
            evidence_rows = [backlog_evidence]
        else:
            evidence_rows = backlog_evidence
        source_evidence = next(
            (row for row in evidence_rows if row.get("path") == source_path),
            None,
        )
        if (
            source_evidence is None
            or source_evidence.get("sha256") != source_digest
            or not source_file.is_file()
            or sha256_file(source_file) != source_digest
        ):
            _fail(f"source evidence is stale or inconsistent: {source_id}")

        workflow_id = mapping["workflow_id"]
        cases = workflow_cases.get(workflow_id)
        if cases is None:
            _fail(f"mapping references unknown workflow: {workflow_id}")
        case_ids = set(mapping["case_ids"])
        if not case_ids <= cases.keys():
            _fail(f"mapping references unknown workflow cases: {source_id}")
        mapped_cases[workflow_id].update(case_ids)

        expected_evidence_kind = (
            "upstream_documentation"
            if coverage["kind"] == "documented_feature_page"
            else "upstream_test"
        )
        used_selectors: set[str] = set()
        for case_id in case_ids:
            case = cases[case_id]
            if not any(
                evidence["path"] == source_path and evidence["kind"] == expected_evidence_kind
                for evidence in case["source_evidence"]
            ):
                _fail(f"workflow case lacks matching source evidence: {case_id} -> {source_id}")
            used_selectors.update(
                _selected_selectors(case, workflow_schema=workflow_schemas[workflow_id])
            )

        declared_selectors = set(mapping["observation_selectors"])
        if not declared_selectors <= used_selectors:
            _fail(f"declared selectors do not map to workflow observations: {source_id}")
        if not declared_selectors <= set(coverage["observation_selectors"]):
            _fail(f"selectors exceed the mapped source candidate: {source_id}")
        for selector_id in declared_selectors:
            selector = selector_rows.get(selector_id)
            if selector is None or selector["workflow_support"] not in {"supported", "partial"}:
                _fail(f"selector is missing or lacks workflow support: {selector_id}")

    for workflow_id, cases in workflow_cases.items():
        if mapped_cases[workflow_id] != cases.keys():
            _fail(f"workflow contains cases without source mappings: {workflow_id}")

    return {
        "workflows": len(workflow_by_id),
        "cases": sum(len(cases) for cases in workflow_cases.values()),
        "source_mappings": len(index["mappings"]),
        "partial_mappings": sum(
            mapping["coverage_status"] == "partial" for mapping in index["mappings"]
        ),
    }
