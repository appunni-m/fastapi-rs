"""Build the source mapping index for independently authored parity workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scripts.atlas_documentation_example_review_mappings import (
    DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS,
)
from scripts.atlas_documentation_page_case_links_fastapi_wave_l import (
    DOC_PAGE_CASE_LINK_COMPLETIONS_WAVE_L,
)
from scripts.atlas_documentation_section_case_mappings_additional_response_model_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_ADDITIONAL_RESPONSE_MODEL_20261015,
)
from scripts.atlas_documentation_section_case_mappings_advanced_testing_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_ADVANCED_TESTING_20261015,
)
from scripts.atlas_documentation_section_case_mappings_async_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_ASYNC_20261015,
)
from scripts.atlas_documentation_section_case_mappings_authentication_error_status_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_AUTHENTICATION_ERROR_STATUS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_background_tasks_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_BACKGROUND_TASKS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_body_wave_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_BODY_WAVE_20261015,
)
from scripts.atlas_documentation_section_case_mappings_cookie_encoder_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_COOKIE_ENCODER_20261015,
)
from scripts.atlas_documentation_section_case_mappings_cookie_params_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_COOKIE_PARAMS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_custom_request_route_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_CUSTOM_REQUEST_ROUTE_20261015,
)
from scripts.atlas_documentation_section_case_mappings_data_conversion_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_DATA_CONVERSION_20261015,
)
from scripts.atlas_documentation_section_case_mappings_dependency_overrides_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_DEPENDENCY_OVERRIDES_20261015,
)
from scripts.atlas_documentation_section_case_mappings_extra_form_fields_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_EXTRA_FORM_FIELDS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_fastapi_cli_entrypoint_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_FASTAPI_CLI_ENTRYPOINT_20261015,
)
from scripts.atlas_documentation_section_case_mappings_first_steps_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_FIRST_STEPS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_form_parameters_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_FORM_PARAMETERS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_frontend_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_FRONTEND_20261015,
)
from scripts.atlas_documentation_section_case_mappings_global_dependencies_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_GLOBAL_DEPENDENCIES_20261015,
)
from scripts.atlas_documentation_section_case_mappings_jsonable_encoder_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_JSONABLE_ENCODER_20261015,
)
from scripts.atlas_documentation_section_case_mappings_openapi_callbacks_webhooks_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_OPENAPI_CALLBACKS_WEBHOOKS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_operation_config_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_OPERATION_CONFIG_20261015,
)
from scripts.atlas_documentation_section_case_mappings_path_params_1016 import (
    DOC_SECTION_CASE_MAPPINGS_PATH_PARAMS_1016,
)
from scripts.atlas_documentation_section_case_mappings_query_header_parameters_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_QUERY_HEADER_PARAMETERS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_reference_api_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_REFERENCE_API_20261015,
)
from scripts.atlas_documentation_section_case_mappings_reference_dependencies_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_REFERENCE_DEPENDENCIES_20261015,
)
from scripts.atlas_documentation_section_case_mappings_request_forms_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_REQUEST_FORMS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_request_middleware_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_REQUEST_MIDDLEWARE_20261015,
)
from scripts.atlas_documentation_section_case_mappings_request_object_directly_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_REQUEST_OBJECT_DIRECTLY_20261015,
)
from scripts.atlas_documentation_section_case_mappings_response_directly_1016 import (
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_DIRECTLY_1016,
)
from scripts.atlas_documentation_section_case_mappings_response_model_defaults_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_MODEL_DEFAULTS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_response_reference_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_REFERENCE_20261015,
)
from scripts.atlas_documentation_section_case_mappings_response_status_review_20261016 import (
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_STATUS_REVIEW_20261016,
)
from scripts.atlas_documentation_section_case_mappings_security_intro_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_SECURITY_INTRO_20261015,
)
from scripts.atlas_documentation_section_case_mappings_security_reference_sections_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_SECURITY_REFERENCE_SECTIONS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_security_scopes_1016 import (
    DOC_SECTION_CASE_MAPPINGS_SECURITY_SCOPES_1016,
)
from scripts.atlas_documentation_section_case_mappings_settings_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_SETTINGS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_streaming_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_STREAMING_20261015,
)
from scripts.atlas_documentation_section_case_mappings_strict_cli_background_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_STRICT_CLI_BACKGROUND_20261015,
)
from scripts.atlas_documentation_section_case_mappings_strict_content_type_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_STRICT_CONTENT_TYPE_20261015,
)
from scripts.atlas_documentation_section_case_mappings_sub_applications_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_SUB_APPLICATIONS_20261015,
)
from scripts.atlas_documentation_section_case_mappings_ui_clients_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_UI_CLIENTS_20261015,
)
from scripts.atlas_events_documentation_section_review_mappings_20261015 import (
    DOC_SECTION_CASE_MAPPINGS_EVENTS_20261015,
)
from scripts.atlas_remaining_docs_wave_mappings import (
    DOC_PAGE_REVIEW_MAPPINGS as REMAINING_DOC_PAGE_REVIEW_MAPPINGS,
)
from scripts.atlas_tutorial_doc_review_mappings import (
    DOC_PAGE_REVIEW_MAPPINGS as TUTORIAL_DOC_PAGE_REVIEW_MAPPINGS,
)
from scripts.parity.contract import (
    API_WORKFLOW_SCHEMA_IDS,
    MATERIALIZED_INPUT_INDEX_SCHEMA_ID,
    ROOT,
    WORKFLOW_SCHEMA_V16_ID,
    WORKFLOW_SCHEMA_V17_ID,
    ContractError,
    load_workflow,
    read_json,
    sha256_file,
)
from scripts.parity.materialized import _api_probe_selectors, _source_selectors_for_case
from scripts.parity.process_contract import (
    PROCESS_WORKFLOW_SCHEMA_IDS,
    load_process_workflow,
)

INDEX_PATH = ROOT / "tests/fixtures/materialized-input-index.json"
INPUT_DIR = ROOT / "tests/fixtures/inputs/parity"
FASTAPI_SOURCE = (ROOT / "../fastapi").resolve()
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
INDEX_SCHEMA = MATERIALIZED_INPUT_INDEX_SCHEMA_ID
INDEX_SCHEMA_PATH = ROOT / "tests/fixtures/schemas/materialized-input-index-v11.schema.json"

_REVIEWED_PAGE_SECTION_MAPPINGS = (
    DOC_SECTION_CASE_MAPPINGS_ASYNC_20261015,
    DOC_SECTION_CASE_MAPPINGS_ADVANCED_TESTING_20261015,
    DOC_SECTION_CASE_MAPPINGS_ADDITIONAL_RESPONSE_MODEL_20261015,
    DOC_SECTION_CASE_MAPPINGS_AUTHENTICATION_ERROR_STATUS_20261015,
    DOC_SECTION_CASE_MAPPINGS_BACKGROUND_TASKS_20261015,
    DOC_SECTION_CASE_MAPPINGS_BODY_WAVE_20261015,
    DOC_SECTION_CASE_MAPPINGS_CUSTOM_REQUEST_ROUTE_20261015,
    DOC_SECTION_CASE_MAPPINGS_COOKIE_PARAMS_20261015,
    DOC_SECTION_CASE_MAPPINGS_COOKIE_ENCODER_20261015,
    DOC_SECTION_CASE_MAPPINGS_DATA_CONVERSION_20261015,
    DOC_SECTION_CASE_MAPPINGS_DEPENDENCY_OVERRIDES_20261015,
    DOC_SECTION_CASE_MAPPINGS_FRONTEND_20261015,
    DOC_SECTION_CASE_MAPPINGS_FORM_PARAMETERS_20261015,
    DOC_SECTION_CASE_MAPPINGS_GLOBAL_DEPENDENCIES_20261015,
    DOC_SECTION_CASE_MAPPINGS_JSONABLE_ENCODER_20261015,
    DOC_SECTION_CASE_MAPPINGS_OPENAPI_CALLBACKS_WEBHOOKS_20261015,
    DOC_SECTION_CASE_MAPPINGS_OPERATION_CONFIG_20261015,
    DOC_SECTION_CASE_MAPPINGS_PATH_PARAMS_1016,
    DOC_SECTION_CASE_MAPPINGS_QUERY_HEADER_PARAMETERS_20261015,
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_STATUS_REVIEW_20261016,
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_DIRECTLY_1016,
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_MODEL_DEFAULTS_20261015,
    DOC_SECTION_CASE_MAPPINGS_REQUEST_OBJECT_DIRECTLY_20261015,
    DOC_SECTION_CASE_MAPPINGS_RESPONSE_REFERENCE_20261015,
    DOC_SECTION_CASE_MAPPINGS_REQUEST_MIDDLEWARE_20261015,
    DOC_SECTION_CASE_MAPPINGS_REFERENCE_DEPENDENCIES_20261015,
    DOC_SECTION_CASE_MAPPINGS_REFERENCE_API_20261015,
    DOC_SECTION_CASE_MAPPINGS_SECURITY_REFERENCE_SECTIONS_20261015,
    DOC_SECTION_CASE_MAPPINGS_SECURITY_SCOPES_1016,
    DOC_SECTION_CASE_MAPPINGS_SECURITY_INTRO_20261015,
    DOC_SECTION_CASE_MAPPINGS_STREAMING_20261015,
    DOC_SECTION_CASE_MAPPINGS_STRICT_CONTENT_TYPE_20261015,
    DOC_SECTION_CASE_MAPPINGS_STRICT_CLI_BACKGROUND_20261015,
    DOC_SECTION_CASE_MAPPINGS_REQUEST_FORMS_20261015,
    DOC_SECTION_CASE_MAPPINGS_SUB_APPLICATIONS_20261015,
    DOC_SECTION_CASE_MAPPINGS_UI_CLIENTS_20261015,
    DOC_SECTION_CASE_MAPPINGS_EVENTS_20261015,
    DOC_SECTION_CASE_MAPPINGS_EXTRA_FORM_FIELDS_20261015,
    DOC_SECTION_CASE_MAPPINGS_FASTAPI_CLI_ENTRYPOINT_20261015,
    DOC_SECTION_CASE_MAPPINGS_FIRST_STEPS_20261015,
    DOC_SECTION_CASE_MAPPINGS_SETTINGS_20261015,
)


def _reviewed_page_case_selectors(source_path: str, recipe_path: str, case_id: str) -> set[str]:
    """Return selectors explicitly reviewed for this docs page and fixture case."""
    page_rel = source_path.removeprefix("docs/en/docs/")
    selectors: set[str] = set()
    for mappings in _REVIEWED_PAGE_SECTION_MAPPINGS:
        for (mapped_page, _), mapping in mappings.items():
            if mapped_page != page_rel or mapping.get("status") == "excluded":
                continue
            if mapping.get("recipe_path") == recipe_path and case_id in mapping.get("case_ids", []):
                selectors.update(mapping["observation_selectors"])
    for page_mappings in (
        REMAINING_DOC_PAGE_REVIEW_MAPPINGS,
        TUTORIAL_DOC_PAGE_REVIEW_MAPPINGS,
    ):
        page_review = page_mappings.get(page_rel)
        if not isinstance(page_review, dict):
            continue
        for mapping in page_review.get("workflow_cases", []):
            if not isinstance(mapping, dict) or mapping.get("recipe_path") != recipe_path:
                continue
            mapped_cases = mapping.get("case_ids")
            if mapped_cases is None and isinstance(mapping.get("case_id"), str):
                mapped_cases = [mapping["case_id"]]
            if (
                isinstance(mapped_cases, list)
                and case_id in mapped_cases
                and isinstance(mapping.get("observation_selectors"), list)
            ):
                selectors.update(mapping["observation_selectors"])
    return selectors


def _source_item_id(
    evidence: dict[str, Any], coverage_by_path: dict[str, list[dict[str, Any]]]
) -> str | None:
    expected_kind = {
        "upstream_test": "upstream_test_module",
        "upstream_documentation": "documented_feature_page",
        "upstream_documentation_example": "documented_python_example_source",
    }.get(evidence["kind"])
    if expected_kind is None:
        return None
    if evidence["kind"] == "upstream_documentation_example":
        source_path = evidence["path"]
        if (
            not source_path.startswith("docs_src/")
            or not source_path.endswith(".py")
            or source_path not in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS
        ):
            raise ContractError(
                "upstream_documentation_example must name a reviewed docs_src Python example: "
                f"{source_path}"
            )
    for row in coverage_by_path.get(evidence["path"], []):
        if row["kind"] == expected_kind:
            return row["id"]
    if evidence["kind"] == "upstream_documentation_example":
        raise ContractError(
            "reviewed documentation example is absent from the compatibility atlas: "
            f"{evidence['path']}"
        )
    return None


def _validate_reviewed_documentation_example_mappings(index: dict[str, Any]) -> None:
    workflows_by_id = {row["id"]: row for row in index["workflows"]}
    mappings_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for mapping in index["mappings"]:
        mappings_by_source[mapping["source_item_id"]].append(mapping)

    for source_path, review in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.items():
        source_id = "documented-example:" + source_path
        expected_by_recipe: dict[str, dict[str, set[str]]] = {}
        for workflow_case in review["workflow_cases"]:
            expected = expected_by_recipe.setdefault(
                workflow_case["recipe_path"], {"case_ids": set(), "selectors": set()}
            )
            expected["case_ids"].update(workflow_case["case_ids"])
            expected["selectors"].update(workflow_case["observation_selectors"])
        expected = sorted(
            (recipe_path, tuple(sorted(values["case_ids"])), tuple(sorted(values["selectors"])))
            for recipe_path, values in expected_by_recipe.items()
        )
        actual = sorted(
            (
                workflows_by_id[mapping["workflow_id"]]["recipe_path"],
                tuple(mapping["case_ids"]),
                tuple(mapping["observation_selectors"]),
            )
            for mapping in mappings_by_source.get(source_id, [])
        )
        if actual != expected:
            raise ContractError(
                "indexed documentation-example cases/selectors differ from reviewed mapping: "
                f"{source_path}; expected {expected!r}, found {actual!r}"
            )


def _scope(case_count: int, selectors: set[str]) -> str:
    selected = ", ".join(sorted(selectors))
    return (
        f"Partial independent sample across {case_count} case(s); observes {selected}. "
        "Unlisted functions, branches, configurations, and edge cases are not claimed."
    )


def _manifest_with_current_index(text: str, index: dict[str, Any]) -> str:
    index_bytes = (json.dumps(index, indent=2) + "\n").encode("utf-8")
    values = {
        "schema": index["schema"],
        "schema_path": INDEX_SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(index_bytes).hexdigest(),
        "schema_sha256": sha256_file(INDEX_SCHEMA_PATH),
        "workflows": len(index["workflows"]),
        "cases": sum(len(row["case_ids"]) for row in index["workflows"]),
        "partial_source_mappings": sum(
            row["coverage_status"] == "partial" for row in index["mappings"]
        ),
    }
    lines = text.splitlines(keepends=True)
    try:
        start = next(i for i, line in enumerate(lines) if line == "  materialized_input_index:\n")
    except StopIteration as exc:
        raise ContractError("manifest has no materialized_input_index artifact block") from exc
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() and not lines[i][0].isspace()),
        len(lines),
    )
    replacements = {
        "schema": re.compile(r"^    schema: .*(\n?)$"),
        "schema_path": re.compile(r"^    schema_path: .*(\n?)$"),
        "sha256": re.compile(r"^    sha256: .*(\n?)$"),
        "schema_sha256": re.compile(r"^    schema_sha256: .*(\n?)$"),
        "workflows": re.compile(r"^      workflows: .*(\n?)$"),
        "cases": re.compile(r"^      cases: .*(\n?)$"),
        "partial_source_mappings": re.compile(r"^      partial_source_mappings: .*(\n?)$"),
    }
    found: set[str] = set()
    for i in range(start + 1, end):
        for key, pattern in replacements.items():
            match = pattern.match(lines[i])
            if match:
                indent = (
                    "    "
                    if key in {"schema", "schema_path", "sha256", "schema_sha256"}
                    else "      "
                )
                lines[i] = f"{indent}{key}: {values[key]}{match[1]}"
                found.add(key)
                break
    if found != set(values):
        missing = ", ".join(sorted(set(values) - found))
        raise ContractError(f"manifest materialized index block is missing fields: {missing}")
    return "".join(lines)


def build_index() -> dict[str, Any]:
    atlas = read_json(ROOT / "tests/fixtures/compatibility-atlas.json")
    backlog = read_json(ROOT / "tests/fixtures/fixture-backlog.json")
    selector_catalog = read_json(ROOT / "tests/fixtures/observation-selectors.json")
    selector_support = {
        row["id"]: row["workflow_support"] for row in selector_catalog["selectors"] if "id" in row
    }
    api_candidates_by_symbol = {row["id"]: row for row in atlas["api_candidates"]}
    supported_api_symbols = {
        symbol_id
        for symbol_id, row in api_candidates_by_symbol.items()
        if row["classification"] == "supported"
    }
    supported_api_symbols.update(
        row["id"]
        for row in atlas.get("reviewed_inherited_api_candidates", [])
        if row["classification"] == "supported"
    )
    coverage_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in atlas["coverage_matrix"]:
        coverage_by_path[row["source_path"]].append(row)
    backlog_by_source = {row["source_item_id"]: row for row in backlog["fixture_designs"]}

    # Derive the active index from disk every time. Carrying rows forward kept
    # stale workflow IDs after input files were renamed and made new source
    # citations invisible for cases that already had an index mapping.
    workflow_rows: dict[str, dict[str, Any]] = {}
    workflow_documents: dict[str, dict[str, Any]] = {}
    mappings: dict[tuple[str, str], dict[str, Any]] = {}

    for input_path in sorted(INPUT_DIR.glob("*.json")):
        # Workflow IDs follow the materialized-index slug schema even when an
        # older input filename uses underscores.
        workflow_id = input_path.stem.replace("_", "-")
        if read_json(input_path).get("schema") in PROCESS_WORKFLOW_SCHEMA_IDS:
            workflow, _, input_digest = load_process_workflow(
                input_path, source_root=FASTAPI_SOURCE
            )
            workload_path = None
            is_process_workflow = True
        else:
            workflow, _, input_digest, workload_path = load_workflow(
                input_path, source_root=FASTAPI_SOURCE
            )
            is_process_workflow = False
        api_definitions = []
        api_probes = []
        for case in workflow["cases"]:
            public_symbol_ids: set[str] = set()
            case_probes = case.get("probes", [])
            for probe in case_probes:
                if "public_module" in probe:
                    module = probe["public_module"]["module"]
                    public_symbol_ids.update(
                        f"{module}.{binding}" for binding in probe["public_module"]["bindings"]
                    )
                    continue
                for key in ("public_callable", "public_attribute"):
                    reference = probe.get(key)
                    if isinstance(reference, dict):
                        public_symbol_ids.add(f"{reference['module']}.{reference['attribute']}")
            if workflow["schema"] in API_WORKFLOW_SCHEMA_IDS:
                for probe in case_probes:
                    if "public_module" in probe:
                        module = probe["public_module"]["module"]
                        references = [
                            (f"{module}.{binding}", "attribute")
                            for binding in probe["public_module"]["bindings"]
                        ]
                    else:
                        reference = probe.get("public_callable", probe.get("public_attribute"))
                        references = [
                            (
                                f"{reference['module']}.{reference['attribute']}",
                                "callable" if "public_callable" in probe else "attribute",
                            )
                        ]
                    for symbol_id, probe_kind in references:
                        if symbol_id not in supported_api_symbols:
                            raise ContractError(
                                "direct API workflow probe is outside the supported source API "
                                f"contract: {case['case_id']} -> {symbol_id}"
                            )
                        api_probes.append(
                            {
                                "case_id": case["case_id"],
                                "probe_id": probe["probe_id"],
                                "symbol_id": symbol_id,
                                "probe_kind": probe_kind,
                                "observation_selectors": _api_probe_selectors(
                                    probe, selector_support
                                ),
                            }
                        )
            for evidence in case["source_evidence"]:
                if evidence["kind"] != "upstream_api_definition":
                    continue
                if evidence["symbol_id"] not in public_symbol_ids:
                    candidate = api_candidates_by_symbol.get(evidence["symbol_id"])
                    candidate_sources = (
                        candidate.get("source_evidence", []) if candidate is not None else []
                    )
                    source_matches_candidate = any(
                        source.get("path") == evidence["path"]
                        and source.get("module_sha256") == evidence["sha256"]
                        for source in candidate_sources
                    )
                    if (
                        workflow["schema"]
                        not in {
                            WORKFLOW_SCHEMA_V16_ID,
                            WORKFLOW_SCHEMA_V17_ID,
                        }
                        or evidence["symbol_id"] not in supported_api_symbols
                        or not source_matches_candidate
                    ):
                        raise ContractError(
                            "ASGI API definition evidence must identify a supported symbol and "
                            "its reviewed source file: "
                            f"{case['case_id']} -> {evidence['symbol_id']}"
                        )
                api_definitions.append(
                    {
                        "case_id": case["case_id"],
                        "symbol_id": evidence["symbol_id"],
                        "path": evidence["path"],
                        "sha256": evidence["sha256"],
                    }
                )
        input_rel_path = input_path.relative_to(ROOT).as_posix()
        if (
            workflow_id in workflow_rows
            and workflow_rows[workflow_id]["input_path"] != input_rel_path
        ):
            raise ContractError(f"workflow ID is shared by different files: {workflow_id}")
        workflow_ref: dict[str, Any] = {
            "id": workflow_id,
            "input_path": input_path.relative_to(ROOT).as_posix(),
            "input_sha256": input_digest,
            "recipe_path": (
                Path("tests/fixtures/input-recipes/parity") / f"{input_path.stem}.yaml"
            ).as_posix(),
            "recipe_sha256": sha256_file(
                ROOT / "tests/fixtures/input-recipes/parity" / f"{input_path.stem}.yaml"
            ),
            "case_ids": [case["case_id"] for case in workflow["cases"]],
        }
        if is_process_workflow:
            workflow_ref["workflow_schema"] = workflow["schema"]
        else:
            assert workload_path is not None
            workflow_ref["workload_path"] = workload_path.relative_to(ROOT).as_posix()
            workflow_ref["workload_sha256"] = sha256_file(workload_path)
        if "oracle_profile_extension" in workflow:
            workflow_ref["oracle_profile_extension"] = workflow["oracle_profile_extension"]
        if api_definitions:
            workflow_ref["api_definitions"] = sorted(
                api_definitions,
                key=lambda row: (row["case_id"], row["symbol_id"], row["path"]),
            )
        if api_probes:
            workflow_ref["api_probes"] = sorted(
                api_probes,
                key=lambda row: (row["case_id"], row["probe_id"], row["symbol_id"]),
            )
        workflow_rows[workflow_id] = workflow_ref
        workflow_documents[workflow_id] = workflow

        new_mapping_cases: dict[str, dict[str, Any]] = {}
        reviewed_doc_required_selectors: dict[str, set[str]] = {}
        reviewed_doc_case_selectors = {
            (source_path, case_id): set(workflow_case["observation_selectors"])
            for source_path, review in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.items()
            for workflow_case in review["workflow_cases"]
            if workflow_case["recipe_path"] == workflow_ref["recipe_path"]
            for case_id in workflow_case["case_ids"]
        }
        for source_path, review in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.items():
            for workflow_case in review["workflow_cases"]:
                if workflow_case["recipe_path"] == workflow_ref["recipe_path"]:
                    reviewed_doc_required_selectors.setdefault(source_path, set()).update(
                        workflow_case["observation_selectors"]
                    )
        reviewed_doc_observed_selectors: dict[str, set[str]] = {}
        for case in workflow["cases"]:
            # Target-only injected failures are valuable fault-contract
            # evidence, but cannot substantiate parity against the pinned
            # FastAPI source. Keep their source citations as context only.
            if case.get("verification", "parity") == "fault-contract":
                continue
            candidates: list[tuple[str, set[str]]] = []
            for evidence in case["source_evidence"]:
                source_id = _source_item_id(evidence, coverage_by_path)
                if source_id is None:
                    continue
                coverage = next(row for row in atlas["coverage_matrix"] if row["id"] == source_id)
                if coverage.get("kind") == "upstream_test_module":
                    source_selectors = set(
                        coverage.get("candidate_observation_selectors")
                        or coverage["observation_selectors"]
                    )
                else:
                    source_selectors = set(coverage["observation_selectors"])
                if evidence["kind"] == "upstream_documentation":
                    reviewed_page_selectors = _reviewed_page_case_selectors(
                        evidence["path"], workflow_ref["recipe_path"], case["case_id"]
                    )
                    if reviewed_page_selectors:
                        # Reviewed section claims break the one-generation atlas/index refresh
                        # cycle while keeping source mappings limited to documented behavior.
                        source_selectors.update(reviewed_page_selectors)
                if evidence["kind"] == "upstream_documentation_example":
                    # Reviewed mappings own the selector contract. Reading this
                    # from the generated atlas creates a refresh cycle when a
                    # newly reviewed case expands the example's observations.
                    source_selectors = {
                        selector
                        for row in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS[evidence["path"]][
                            "workflow_cases"
                        ]
                        for selector in row["observation_selectors"]
                    }
                usable = _source_selectors_for_case(
                    case,
                    source_selectors,
                    workflow_schema=workflow["schema"],
                    selector_support=selector_support,
                )
                usable = {
                    selector
                    for selector in usable
                    if selector_support.get(selector) in {"supported", "partial"}
                }
                if evidence["kind"] == "upstream_documentation_example":
                    reviewed = reviewed_doc_case_selectors.get((evidence["path"], case["case_id"]))
                    if reviewed is None:
                        raise ContractError(
                            "documentation example source evidence has no reviewed case mapping: "
                            f"{evidence['path']} -> {case['case_id']}"
                        )
                    usable &= reviewed
                    reviewed_doc_observed_selectors.setdefault(evidence["path"], set()).update(
                        usable
                    )
                if usable and source_id in backlog_by_source:
                    candidates.append((source_id, usable))
            if not candidates:
                if any(
                    evidence.get("kind") == "upstream_api_definition"
                    for evidence in case["source_evidence"]
                ):
                    continue
                raise ContractError(
                    "workflow case has no source row with a supported observed selector: "
                    f"{case['case_id']}"
                )
            for source_id, usable in candidates:
                mapping = new_mapping_cases.setdefault(
                    source_id,
                    {"case_ids": set(), "observation_selectors": set()},
                )
                mapping["case_ids"].add(case["case_id"])
                mapping["observation_selectors"].update(usable)

        for source_path, required in reviewed_doc_required_selectors.items():
            missing = required - reviewed_doc_observed_selectors.get(source_path, set())
            if missing:
                raise ContractError(
                    "reviewed documentation-example selectors are not observed by the mapped "
                    f"workflow cases: {source_path}: {', '.join(sorted(missing))}"
                )

        for source_id, detail in new_mapping_cases.items():
            old = mappings.get((source_id, workflow_id))
            all_case_ids = set(detail["case_ids"])
            all_selectors = set(detail["observation_selectors"])
            if old:
                all_case_ids.update(old["case_ids"])
                all_selectors.update(old["observation_selectors"])
            mappings[(source_id, workflow_id)] = {
                "source_item_id": source_id,
                "fixture_id": backlog_by_source[source_id]["id"],
                "workflow_id": workflow_id,
                "coverage_status": "partial",
                "coverage_scope": _scope(len(all_case_ids), all_selectors),
                "case_ids": sorted(all_case_ids),
                "observation_selectors": sorted(all_selectors),
            }

    for page_rel, reviewed_rows in DOC_PAGE_CASE_LINK_COMPLETIONS_WAVE_L.items():
        source_id = "documented-page:" + page_rel
        if source_id not in backlog_by_source:
            raise ContractError(
                "reviewed documentation page link is absent from the compatibility atlas: "
                + page_rel
            )
        for row in reviewed_rows:
            recipe_path = row["recipe_path"]
            workflow_id = Path(recipe_path).stem.replace("_", "-")
            workflow_ref = workflow_rows.get(workflow_id)
            workflow = workflow_documents.get(workflow_id)
            if (
                workflow_ref is None
                or workflow is None
                or workflow_ref["recipe_path"] != recipe_path
            ):
                raise ContractError(
                    "reviewed documentation page link references an unknown workflow: "
                    f"{page_rel} -> {recipe_path}"
                )
            cases_by_id = {case["case_id"]: case for case in workflow["cases"]}
            case_ids = row["case_ids"]
            missing_cases = sorted(set(case_ids) - cases_by_id.keys())
            if missing_cases:
                raise ContractError(
                    "reviewed documentation page link references unknown cases: "
                    f"{page_rel} -> {missing_cases}"
                )
            fault_case_ids = sorted(
                case_id
                for case_id in case_ids
                if cases_by_id[case_id].get("verification", "parity") == "fault-contract"
            )
            if fault_case_ids:
                raise ContractError(
                    "reviewed documentation parity mapping contains target-only fault cases: "
                    f"{page_rel} -> {fault_case_ids}"
                )
            declared = set(row["observation_selectors"])
            observed: set[str] = set()
            for case_id in case_ids:
                case = cases_by_id[case_id]
                page_path = "docs/en/docs/" + page_rel
                if not any(
                    evidence.get("path") == page_path
                    and evidence.get("kind") == "upstream_documentation"
                    for evidence in case.get("source_evidence", [])
                ):
                    raise ContractError(
                        "reviewed documentation page link lacks exact input evidence: "
                        f"{page_rel} -> {recipe_path}::{case_id}"
                    )
                if workflow["schema"] in PROCESS_WORKFLOW_SCHEMA_IDS:
                    projected = set(case["observations"])
                else:
                    selected_case = case
                    action_ids = row.get("action_ids")
                    if action_ids is not None:
                        actions = {action["action_id"]: action for action in case["actions"]}
                        missing_actions = sorted(set(action_ids) - actions.keys())
                        if missing_actions:
                            raise ContractError(
                                "reviewed documentation page link references unknown actions: "
                                f"{page_rel} -> {missing_actions}"
                            )
                        selected_case = {
                            **case,
                            "actions": [actions[action_id] for action_id in action_ids],
                        }
                    projected = _source_selectors_for_case(
                        selected_case,
                        set(selector_support),
                        workflow_schema=workflow["schema"],
                        selector_support=selector_support,
                    )
                observed.update(
                    selector
                    for selector in projected
                    if selector_support.get(selector) in {"supported", "partial"}
                )
            if observed != declared:
                raise ContractError(
                    "reviewed documentation page selectors differ from linked cases: "
                    f"{page_rel} / {recipe_path}; expected {sorted(declared)}, "
                    f"observed {sorted(observed)}"
                )
            old = mappings.get((source_id, workflow_id))
            all_case_ids = set(case_ids)
            all_selectors = set(declared)
            if old:
                all_case_ids.update(old["case_ids"])
                all_selectors.update(old["observation_selectors"])
            mappings[(source_id, workflow_id)] = {
                "source_item_id": source_id,
                "fixture_id": backlog_by_source[source_id]["id"],
                "workflow_id": workflow_id,
                "coverage_status": "partial",
                "coverage_scope": _scope(len(all_case_ids), all_selectors),
                "case_ids": sorted(all_case_ids),
                "observation_selectors": sorted(all_selectors),
            }

    requirements_by_case: dict[tuple[str, str], set[str]] = defaultdict(set)
    for mapping in mappings.values():
        for case_id in mapping["case_ids"]:
            requirements_by_case[(mapping["workflow_id"], case_id)].add(
                f"source:{mapping['source_item_id']}"
            )
    for workflow_id, workflow_ref in workflow_rows.items():
        for case in workflow_documents[workflow_id]["cases"]:
            if case.get("verification", "parity") == "fault-contract":
                fault = case["fault"]
                requirements_by_case[(workflow_id, case["case_id"])].add(
                    f"fault-contract:{fault['point']}#{fault['contract']}"
                )
        for definition in workflow_ref.get("api_definitions", []):
            requirements_by_case[(workflow_id, definition["case_id"])].add(
                f"api:{definition['symbol_id']}"
            )
        for probe in workflow_ref.get("api_probes", []):
            requirements_by_case[(workflow_id, probe["case_id"])].add(f"api:{probe['symbol_id']}")
        case_contracts = []
        for case in workflow_documents[workflow_id]["cases"]:
            requirement_refs = sorted(requirements_by_case[(workflow_id, case["case_id"])])
            if not requirement_refs:
                raise ContractError(
                    f"workflow case has no indexed requirement reference: {case['case_id']}"
                )
            contract = {
                "case_id": case["case_id"],
                "verification": case.get("verification", "parity"),
                "requirement_refs": requirement_refs,
            }
            if contract["verification"] == "fault-contract":
                contract["fault"] = dict(case["fault"])
            case_contracts.append(contract)
        workflow_ref["case_contracts"] = case_contracts

    generated = {
        "schema": INDEX_SCHEMA,
        "authority": {
            "fastapi": atlas["authorities"]["fastapi"]["version"],
            "starlette": atlas["authorities"]["starlette"]["version"],
        },
        "workflows": sorted(workflow_rows.values(), key=lambda row: row["id"]),
        "mappings": sorted(
            mappings.values(), key=lambda row: (row["workflow_id"], row["source_item_id"])
        ),
    }
    _validate_reviewed_documentation_example_mappings(generated)
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the index does not already match the current workflow inputs",
    )
    args = parser.parse_args()
    current = read_json(INDEX_PATH)
    generated = build_index()
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    expected_manifest = _manifest_with_current_index(manifest_text, generated)
    if args.check:
        if generated != current:
            raise ContractError("materialized input index is stale; rebuild without --check")
        if expected_manifest != manifest_text:
            raise ContractError("manifest materialized index digest or counts are stale")
        print(
            f"materialized input index is current: {len(generated['workflows'])} workflows, "
            f"{sum(len(row['case_ids']) for row in generated['workflows'])} cases, "
            f"{len(generated['mappings'])} source mappings"
        )
        return 0
    INDEX_PATH.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(
        _manifest_with_current_index(MANIFEST_PATH.read_text(encoding="utf-8"), generated),
        encoding="utf-8",
    )
    print(
        f"wrote {INDEX_PATH.relative_to(ROOT)}: {len(generated['workflows'])} workflows, "
        f"{sum(len(row['case_ids']) for row in generated['workflows'])} cases, "
        f"{len(generated['mappings'])} source mappings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
