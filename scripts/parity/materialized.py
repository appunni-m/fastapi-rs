"""Validate concrete workflow mappings back to the pinned FastAPI backlog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.build_parity_inputs import read_recipe
from scripts.parity.contract import (
    API_WORKFLOW_SCHEMA_V3_ID,
    ROOT,
    WORKFLOW_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID,
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
            if (
                workflow_schema == API_WORKFLOW_SCHEMA_V3_ID
                and probe.get("capture_warnings") is True
            ):
                selectors.add("python.warnings")
            for observation in probe["observations"]:
                if observation["kind"] == "python_return_value":
                    selectors.add("python.attribute_value")
                elif observation["kind"] == "python_attribute_value":
                    selectors.add("python.attribute_value")
                elif observation["kind"] == "python_signature":
                    selectors.add("python.signature")
                elif observation["kind"] == "python_call_outcome":
                    selectors.add("python.call_outcome")
        return selectors

    if workflow_schema in {
        WORKFLOW_SCHEMA_V3_ID,
        WORKFLOW_SCHEMA_V4_ID,
        WORKFLOW_SCHEMA_V5_ID,
        WORKFLOW_SCHEMA_V6_ID,
    }:
        selectors.update(
            f"construction.{selector}" for selector in case["construction_observation"]["selectors"]
        )
    if (
        workflow_schema in {WORKFLOW_SCHEMA_V4_ID, WORKFLOW_SCHEMA_V5_ID, WORKFLOW_SCHEMA_V6_ID}
        and case.get("construction_observation", {}).get("capture_warnings") is True
    ):
        selectors.add("python.warnings")
    for action in case["actions"]:
        if (
            workflow_schema in {WORKFLOW_SCHEMA_V4_ID, WORKFLOW_SCHEMA_V5_ID, WORKFLOW_SCHEMA_V6_ID}
            and action.get("capture_warnings") is True
        ):
            selectors.add("warnings.category_message")
        if action["kind"] == "lifespan":
            selectors.update(
                f"asgi.lifespan.{observation['selector']}" for observation in action["observations"]
            )
            continue
        if action["kind"] == "websocket_conversation":
            for observation in action["observations"]:
                if observation["kind"] == "websocket":
                    selectors.add(f"websocket.{observation['selector']}")
            continue
        path = action["scope"]["path"]
        openapi_endpoint = path == "/openapi.json"
        for observation in action["observations"]:
            if observation["kind"] == "asgi_send":
                selectors.add("asgi.send.message_types")
            elif observation["kind"] == "websocket":
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
            elif observation["kind"] == "application_error":
                if observation["selector"] == "validation_error_class":
                    selectors.add("validation.error_class")
                elif observation["selector"] == "exception":
                    selectors.add("asgi.application_error.exception")
                elif observation["selector"] == "validation_error_details":
                    selectors.add("validation.error_details")
                elif observation["selector"] == "error_public_attributes":
                    selectors.add("error.public_attributes")
            elif observation["kind"] == "asgi_cancellation":
                selectors.add("asgi.cancellation.cancelled_caught")
    return selectors


def _source_selectors_for_case(
    case: dict[str, Any],
    source_selectors: set[str],
    *,
    workflow_schema: str | None = None,
) -> set[str]:
    """Pair feature selectors with generic protocol observations used by this case."""
    selected = _selected_selectors(case, workflow_schema=workflow_schema)
    candidates = set(source_selectors)
    if "asgi.send.message_types" in selected and any(
        action.get("kind") == "http_request" for action in case.get("actions", [])
    ):
        candidates.add("asgi.send.message_types")
    return selected & candidates


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
    api_definition_cases: dict[str, set[str]] = {}
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
        expected_api_definitions: list[dict[str, str]] = []
        defined_cases: set[str] = set()
        for case in workflow["cases"]:
            public_symbol_ids = {
                f"{probe[key]['module']}.{probe[key]['attribute']}"
                for probe in case.get("probes", [])
                for key in ("public_callable", "public_attribute")
                if isinstance(probe.get(key), dict)
            }
            for evidence in case["source_evidence"]:
                if evidence["kind"] != "upstream_api_definition":
                    continue
                symbol_id = evidence["symbol_id"]
                if symbol_id not in public_symbol_ids:
                    _fail(
                        "API definition evidence does not match a probed public symbol: "
                        f"{case['case_id']} -> {symbol_id}"
                    )
                source_path = (fastapi_source / evidence["path"]).resolve()
                try:
                    source_path.relative_to(fastapi_source.resolve())
                except ValueError as exc:
                    raise ContractError(
                        "materialized input index: API definition escapes the pinned FastAPI tree"
                    ) from exc
                if not source_path.is_file() or sha256_file(source_path) != evidence["sha256"]:
                    _fail(f"API definition source digest is stale: {evidence['path']}")
                expected_api_definitions.append(
                    {
                        "case_id": case["case_id"],
                        "symbol_id": symbol_id,
                        "path": evidence["path"],
                        "sha256": evidence["sha256"],
                    }
                )
                defined_cases.add(case["case_id"])
            if any("public_attribute" in probe for probe in case.get("probes", [])) and not any(
                evidence["kind"] == "upstream_api_definition"
                for evidence in case["source_evidence"]
            ):
                _fail(f"public attribute probe lacks API definition evidence: {case['case_id']}")
            if case["case_id"] in defined_cases:
                selected = _selected_selectors(case, workflow_schema=workflow["schema"])
                for selector_id in selected:
                    selector = selector_rows.get(selector_id)
                    if selector is None or selector["workflow_support"] not in {
                        "supported",
                        "partial",
                    }:
                        _fail(f"API definition probe uses an unsupported selector: {selector_id}")
        expected_api_definitions.sort(
            key=lambda row: (row["case_id"], row["symbol_id"], row["path"])
        )
        if workflow_ref.get("api_definitions", []) != expected_api_definitions:
            _fail(f"API source-definition references differ from workflow evidence: {workflow_id}")
        api_definition_cases[workflow_id] = defined_cases
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

        expected_evidence_kind = {
            "upstream_test_module": "upstream_test",
            "documented_feature_page": "upstream_documentation",
            "documented_python_example_source": "upstream_documentation_example",
        }.get(coverage["kind"])
        if expected_evidence_kind is None:
            _fail(f"unsupported materialized source kind: {coverage['kind']}")
        used_selectors: set[str] = set()
        source_selectors: set[str] = set()
        for case_id in case_ids:
            case = cases[case_id]
            if not any(
                evidence["path"] == source_path and evidence["kind"] == expected_evidence_kind
                for evidence in case["source_evidence"]
            ):
                _fail(f"workflow case lacks matching source evidence: {case_id} -> {source_id}")
            workflow_schema = workflow_schemas[workflow_id]
            used_selectors.update(_selected_selectors(case, workflow_schema=workflow_schema))
            source_selectors.update(
                _source_selectors_for_case(
                    case,
                    set(coverage["observation_selectors"]),
                    workflow_schema=workflow_schema,
                )
            )

        declared_selectors = set(mapping["observation_selectors"])
        if not declared_selectors <= used_selectors:
            _fail(f"declared selectors do not map to workflow observations: {source_id}")
        if not declared_selectors <= source_selectors:
            _fail(f"selectors exceed the mapped source candidate: {source_id}")
        for selector_id in declared_selectors:
            selector = selector_rows.get(selector_id)
            if selector is None or selector["workflow_support"] not in {"supported", "partial"}:
                _fail(f"selector is missing or lacks workflow support: {selector_id}")

    for workflow_id, cases in workflow_cases.items():
        covered_cases = mapped_cases[workflow_id] | api_definition_cases[workflow_id]
        if covered_cases != cases.keys():
            _fail(
                f"workflow contains cases without source mappings or API definitions: {workflow_id}"
            )

    expected_mappings_by_source: dict[str, list[dict[str, Any]]] = {}
    for mapping in sorted(
        index["mappings"], key=lambda row: (row["source_item_id"], row["workflow_id"])
    ):
        workflow = workflow_by_id[mapping["workflow_id"]]
        expected_mappings_by_source.setdefault(mapping["source_item_id"], []).append(
            {
                "workflow_id": mapping["workflow_id"],
                "recipe_path": workflow["recipe_path"],
                "case_ids": mapping["case_ids"],
                "observation_selectors": mapping["observation_selectors"],
                "coverage_status": mapping["coverage_status"],
                "coverage_scope": mapping["coverage_scope"],
            }
        )

    for source_id, coverage in coverage_rows.items():
        if coverage.get("kind") not in {
            "upstream_test_module",
            "documented_feature_page",
            "documented_python_example_source",
        }:
            continue
        expected = expected_mappings_by_source.get(source_id, [])
        actual = coverage.get("mapping_evidence", {}).get("independent_workflow_mappings", [])
        if actual != expected:
            _fail(f"coverage workflow crosswalk differs from the materialized index: {source_id}")
        backlog_row = backlog_rows.get(source_id)
        if (
            backlog_row is not None
            and backlog_row.get("independent_workflow_mappings", []) != expected
        ):
            _fail(f"backlog workflow crosswalk differs from the materialized index: {source_id}")

    return {
        "workflows": len(workflow_by_id),
        "cases": sum(len(cases) for cases in workflow_cases.values()),
        "source_mappings": len(index["mappings"]),
        "partial_mappings": sum(
            mapping["coverage_status"] == "partial" for mapping in index["mappings"]
        ),
    }
