"""Source-reviewed request-parameter mappings for the FastAPI 0.141.1 atlas.

This is a separate review module. It does not run the atlas generator or edit
generated inventories. Recipe links resolve to independently authored,
input-only workflows; they are candidates for live parity, not parity results.
"""

from __future__ import annotations

import ast
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"
RECIPE_ROOT = PROJECT_ROOT / "tests/fixtures/input-recipes/parity"

FASTAPI_IDENTITY = {
    "version": "0.141.1",
    "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
}
STARLETTE_IDENTITY = {
    "version": "1.6.0",
    "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    "role": "sole Starlette oracle and generic-framework contract",
}
PYDANTIC_IDENTITY = {
    "version": "2.13.4",
    "role": "field construction, type coercion, and value validation",
}

_API_WORKFLOW_SCHEMA = "fastapi-rs/python-api-workflow@3"
_API_OBSERVATION_SELECTORS = {
    "python_attribute_value": "python.attribute_value",
    "python_call_outcome": "python.call_outcome",
    "python_import_path": "python.import_path",
    "python_object_identity": "python.object_identity",
    "python_pydantic_model_result": "python.pydantic_model_result",
    "python_return_value": "python.attribute_value",
    "python_signature": "python.signature",
}


TOP_LEVEL_REQUEST_PARAMETER_TESTS = (
    "tests/test_ambiguous_params.py",
    "tests/test_enforce_once_required_parameter.py",
    "tests/test_file_and_form_order_issue_9116.py",
    "tests/test_form_default.py",
    "tests/test_forms_from_non_typing_sequences.py",
    "tests/test_forms_single_model.py",
    "tests/test_forms_single_param.py",
    "tests/test_get_request_body.py",
    "tests/test_infer_param_optionality.py",
    "tests/test_invalid_path_param.py",
    "tests/test_invalid_sequence_param.py",
    "tests/test_list_bytes_file_order_preserved_issue_14811.py",
    "tests/test_multi_body_errors.py",
    "tests/test_multi_query_errors.py",
    "tests/test_openapi_query_parameter_extension.py",
    "tests/test_optional_file_list.py",
    "tests/test_param_class.py",
    "tests/test_param_in_path_and_dependency.py",
    "tests/test_param_include_in_schema.py",
    "tests/test_params_repr.py",
    "tests/test_path.py",
    "tests/test_put_no_body.py",
    "tests/test_query.py",
    "tests/test_query_cookie_header_model_extra_params.py",
    "tests/test_regex_deprecated_body.py",
    "tests/test_regex_deprecated_params.py",
    "tests/test_repeated_parameter_alias.py",
    "tests/test_request_body_parameters_media_type.py",
    "tests/test_request_param_model_by_alias.py",
    "tests/test_union_body.py",
    "tests/test_union_body_discriminator.py",
    "tests/test_union_body_discriminator_annotated.py",
    "tests/test_union_forms.py",
    "tests/test_union_inherited_body.py",
    "tests/test_validation_error_context.py",
)

_REQUEST_PARAM_ROOT = FASTAPI_ROOT / "tests/test_request_params"
REQUEST_PARAM_SOURCE_MODULES = tuple(
    str(path.relative_to(FASTAPI_ROOT)) for path in sorted(_REQUEST_PARAM_ROOT.rglob("*.py"))
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _source_file(path: str, role: str) -> dict[str, Any]:
    return {"path": path, "role": role}


def _test_function_spans(test_path: str) -> list[dict[str, Any]]:
    """Return exact top-level pytest function spans from the pinned source tree."""
    source_path = FASTAPI_ROOT / test_path
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    spans = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
            "test_"
        ):
            spans.append(
                _source(
                    test_path,
                    node.lineno,
                    node.end_lineno or node.lineno,
                    f"upstream FastAPI 0.141.1 test function {node.name}",
                )
            )
    return spans


def _nonempty_line_span(test_path: str) -> dict[str, Any] | None:
    lines = (FASTAPI_ROOT / test_path).read_text(encoding="utf-8").splitlines()
    nonempty = [index for index, line in enumerate(lines, start=1) if line.strip()]
    if not nonempty:
        return None
    return _source(
        test_path,
        nonempty[0],
        nonempty[-1],
        "source-backed exclusion text in the pinned FastAPI test tree",
    )


def _workflow_selectors(case: dict[str, Any]) -> list[str]:
    """Translate actual workflow observations to the parity selector catalog."""
    selected: set[str] = set()
    if "probes" in case:
        for probe in case["probes"]:
            if probe.get("capture_warnings") is True:
                selected.add("python.warnings")
            for observation in probe.get("observations", []):
                kind = observation.get("kind")
                selector = _API_OBSERVATION_SELECTORS.get(kind)
                if selector is None:
                    raise ValueError(
                        f"unknown direct API observation kind in source mapping: {kind}"
                    )
                selected.add(selector)
        return sorted(selected)
    if "construction_observation" in case:
        selected.update(
            f"construction.{selector}"
            for selector in case["construction_observation"].get("selectors", [])
        )
    for action in case.get("actions", []):
        if action.get("kind") == "lifespan":
            selected.update(
                f"asgi.lifespan.{observation['selector']}"
                for observation in action.get("observations", [])
            )
            continue
        path = action.get("scope", {}).get("path", "")
        openapi_endpoint = path == "/openapi.json"
        for observation in action.get("observations", []):
            kind = observation.get("kind")
            if kind == "http_response":
                values = set(observation.get("selectors", []))
                if "status" in values:
                    selected.add("http.status")
                    if openapi_endpoint:
                        selected.add("docs.response.status")
                if "headers" in values:
                    selected.add("http.headers.ordered")
                    if openapi_endpoint:
                        selected.add("docs.response.headers")
                if "body" in values:
                    selected.add("http.body.bytes")
                    if openapi_endpoint:
                        selected.add("docs.response.body.bytes")
            elif kind == "openapi":
                pointers = observation.get("json_pointers", [])
                for pointer in pointers:
                    if (
                        pointer.startswith("/components/securitySchemes/")
                        or pointer.endswith("/security")
                        or "/security/" in pointer
                    ):
                        selected.add("openapi.security")
                    elif pointer.startswith("/paths/"):
                        selected.update(("openapi.document", "openapi.paths"))
                    else:
                        selected.add("openapi.document")
            elif kind == "application_error":
                if observation.get("selector") == "validation_error_class":
                    selected.add("validation.error_class")
                elif observation.get("selector") == "exception":
                    selected.add("asgi.application_error.exception")
    return sorted(selected)


def _recipe_case_index() -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for recipe in sorted(RECIPE_ROOT.glob("*.yaml")):
        data = yaml.safe_load(recipe.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema") not in {
            "fastapi-rs/python-asgi-workflow@2",
            "fastapi-rs/python-asgi-workflow@3",
            _API_WORKFLOW_SCHEMA,
        }:
            continue
        for case in data.get("cases", []):
            case_id = case["case_id"]
            if case_id in cases:
                raise ValueError(f"duplicate input recipe case ID: {case_id}")
            cases[case_id] = {
                "recipe_path": str(recipe.relative_to(PROJECT_ROOT)),
                "case": case,
                "observation_selectors": _workflow_selectors(case),
            }
    return cases


def _source_link_index() -> dict[str, list[dict[str, Any]]]:
    """Index only explicit source_evidence paths in existing YAML input cases."""
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case_id, row in _recipe_case_index().items():
        for evidence in row["case"].get("source_evidence", []) or []:
            test_path = evidence.get("path")
            if not test_path or evidence.get("kind") != "upstream_test":
                continue
            index[test_path].append(
                {
                    "recipe_path": row["recipe_path"],
                    "case_id": case_id,
                    "action_ids": [
                        action.get("action_id")
                        for action in row["case"].get("actions", [])
                        if action.get("action_id")
                    ],
                    "observation_selectors": row["observation_selectors"],
                }
            )
    return index


_FASTAPI_IMPLEMENTATION_SOURCES = [
    _source(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI 0.141.1 inspects endpoint signatures, infers parameter fields, and classifies path/query/header/cookie/body fields.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        381,
        547,
        "FastAPI 0.141.1 resolves Annotated/default parameter metadata, aliases, path restrictions, and query type restrictions.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        734,
        777,
        "FastAPI 0.141.1 adapts extracted values and required/default handling to Pydantic ModelField validation.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        780,
        850,
        "FastAPI 0.141.1 extracts query/header/cookie/path values and aggregates request parameter errors.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        888,
        905,
        "FastAPI 0.141.1 selects whether request-body fields must be embedded into one body object.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        951,
        998,
        "FastAPI 0.141.1 extracts and validates JSON, Form, and File request-body fields.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        1001,
        1048,
        "FastAPI 0.141.1 combines Body fields and carries a common declared media type into the aggregate field.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        1051,
        1053,
        "FastAPI 0.141.1 selects a Pydantic validation alias before the declared field alias.",
    ),
    _source(
        "fastapi/routing.py",
        425,
        465,
        "FastAPI 0.141.1 selects JSON body decoding by Content-Type and translates malformed JSON into request validation errors.",
    ),
    _source(
        "fastapi/openapi/utils.py",
        159,
        218,
        "FastAPI 0.141.1 projects parameter location, validation alias, requiredness, and schema into OpenAPI.",
    ),
    _source(
        "fastapi/openapi/utils.py",
        231,
        263,
        "FastAPI 0.141.1 uses Body.media_type as the requestBody content key.",
    ),
    _source(
        "fastapi/openapi/utils.py",
        311,
        382,
        "FastAPI 0.141.1 builds operation parameter lists and request-body OpenAPI entries.",
    ),
    _source(
        "fastapi/params.py",
        137,
        220,
        "FastAPI Path metadata and constraints.",
    ),
    _source(
        "fastapi/params.py",
        221,
        302,
        "FastAPI Query metadata and constraints.",
    ),
    _source(
        "fastapi/params.py",
        303,
        386,
        "FastAPI Header metadata, aliases, and underscore conversion option.",
    ),
    _source(
        "fastapi/params.py",
        387,
        468,
        "FastAPI Cookie metadata and aliases.",
    ),
    _source(
        "fastapi/params.py",
        469,
        662,
        "FastAPI Body/Form request media-type metadata and validation alias parameters.",
    ),
    _source(
        "fastapi/params.py",
        663,
        740,
        "FastAPI File multipart metadata and validation alias parameters.",
    ),
]

_STARLETTE_CONTRACT_SOURCES = [
    _source(
        "starlette/routing.py",
        197,
        266,
        "Starlette 1.6.0 matches HTTP paths and places converted path parameters in the child scope; this generic routing contract belongs to Starlette-RS.",
    ),
    _source(
        "starlette/requests.py",
        132,
        159,
        "Starlette 1.6.0 exposes request headers, query parameters, path parameters, and parsed cookies; these generic request semantics belong to Starlette-RS.",
    ),
    _source(
        "starlette/requests.py",
        214,
        266,
        "Starlette 1.6.0 consumes the ASGI request stream and exposes cached body and JSON parsing; generic request-body behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/requests.py",
        268,
        328,
        "Starlette 1.6.0 parses URL-encoded and multipart request forms; parser behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/datastructures.py",
        378,
        399,
        "Starlette 1.6.0 converts a raw query string into QueryParams; generic multidict behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/datastructures.py",
        410,
        479,
        "Starlette 1.6.0 UploadFile storage and async read/write/seek/close behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/datastructures.py",
        482,
        498,
        "Starlette 1.6.0 FormData is an immutable multidict and closes contained UploadFile objects; generic form data behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/datastructures.py",
        500,
        555,
        "Starlette 1.6.0 Headers lookup and duplicate-value behavior belongs to Starlette-RS.",
    ),
]

_PYDANTIC_BOUNDARY = "Pydantic 2.13.4 owns its public ModelField/BaseModel field metadata, core type coercion, and validation semantics. FastAPI owns inspecting Python endpoint annotations, constructing its field adapter, choosing request sources/locations, and shaping FastAPI validation errors. This mapping does not claim a Rust reimplementation of Pydantic internals."
_STARLETTE_BOUNDARY = "Starlette 1.6.0 is the sole generic-framework oracle. HTTP route matching, ASGI request-body/form/multipart parsing, query/header/cookie data structures, and UploadFile mechanics are assigned to the separate Starlette-RS contract. FastAPI owns parameter declaration inspection, source selection, body-field composition, and FastAPI/OpenAPI validation projections."
_PARITY_GATE = "Input mapping only: the cited recipe cases contain stimuli and observation selectors, not expected outputs or measurements, and no live parity result is claimed. The cases are selected examples from the pinned test module; full module snapshots, unlisted defaults/aliases/constraints, complete validation error structures, and exact TestClient behavior are not established by these cases. Compare only the listed workflow selectors after the complete FastAPI manifest and the isolated Python/ASGI runner are ready; generic request and parser behavior remains under Starlette 1.6.0's separate contract."
_BODY_MEDIA_TYPE_PARITY_GATE = "Input mapping only: the recipe contains stimuli and observation selectors, not expected outputs or measurements, and no live parity result is claimed. The original upstream test asserts the two-route OpenAPI schema only; explicitly named source-derived cases add independent HTTP probes grounded in pinned implementation branches. Full module snapshots, unlisted defaults/aliases/constraints, and exact TestClient behavior remain outside this mapping. Generic request and parser behavior remains under Starlette 1.6.0's separate contract."


def _mapping_for_test_module(
    test_path: str, case_index: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    spans = _test_function_spans(test_path)
    if not spans:
        raise ValueError(f"expected test functions for candidate module {test_path}")
    workflow_cases = case_index.get(test_path, [])
    if not workflow_cases:
        raise ValueError(f"no source-linked input workflow for candidate module {test_path}")
    selectors = sorted(
        {
            selector
            for workflow_case in workflow_cases
            for selector in workflow_case["observation_selectors"]
        }
    )
    if not selectors:
        raise ValueError(f"workflow cases for {test_path} expose no selectors")
    contract_gate = (
        _BODY_MEDIA_TYPE_PARITY_GATE
        if test_path == "tests/test_request_body_parameters_media_type.py"
        else _PARITY_GATE
    )
    return {
        "mapping_status": "source-reviewed-input-candidate; parity pending",
        "source_test_spans": spans,
        "workflow_cases": workflow_cases,
        "observation_selectors": selectors,
        "fastapi_implementation_sources": list(_FASTAPI_IMPLEMENTATION_SOURCES),
        "pydantic_ownership_boundary": _PYDANTIC_BOUNDARY,
        "starlette_ownership_boundary": _STARLETTE_BOUNDARY,
        "starlette_contract_sources": list(_STARLETTE_CONTRACT_SOURCES),
        "contract_gate": contract_gate,
    }


def _source_exclusion(test_path: str, reason: str) -> dict[str, Any]:
    span = _nonempty_line_span(test_path)
    sources = [span] if span else []
    return {
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": reason,
        "supporting_sources": sources,
        "source_file": _source_file(
            test_path, "pinned FastAPI 0.141.1 test source for the exclusion"
        ),
        "starlette_ownership_boundary": _STARLETTE_BOUNDARY,
        "starlette_contract_sources": list(_STARLETTE_CONTRACT_SOURCES),
    }


_UNSUPPORTED_REQUEST_PARAM_MODULES = {
    "tests/test_request_params/test_cookie/test_list.py": (
        "The pinned source contains only the explicit note that duplicate same-name cookies cannot be passed and comma-delimited cookie lists are unsupported by Starlette. It defines no test function or independent expected behavior. The parsing limitation belongs to Starlette 1.6.0 and its sibling Starlette-RS contract; this is not FastAPI support evidence."
    ),
    "tests/test_request_params/test_cookie/test_optional_list.py": (
        "The pinned source contains only the explicit note that duplicate same-name cookies cannot be passed and comma-delimited cookie lists are unsupported by Starlette. It defines no test function or independent expected behavior. The parsing limitation belongs to Starlette 1.6.0 and its sibling Starlette-RS contract; this is not FastAPI support evidence."
    ),
    "tests/test_request_params/test_path/test_list.py": (
        "The pinned source comment says FastAPI does not support non-scalar Path parameters; the module has no test function. No runtime parity case is inferred from the comment."
    ),
    "tests/test_request_params/test_path/test_optional_list.py": (
        "The pinned source comments say optional Path parameters and non-scalar Path parameters are unsupported; the module has no test function. No runtime parity case is inferred from the comment."
    ),
    "tests/test_request_params/test_path/test_optional_str.py": (
        "The pinned source comments say optional Path parameters and non-scalar Path parameters are unsupported; the module has no test function. No runtime parity case is inferred from the comment."
    ),
}

_REQUEST_PARAM_SUPPORT_EXCLUSIONS = {
    "tests/test_request_params/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_body/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_cookie/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_file/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_form/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_header/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_path/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_query/__init__.py": "Empty package initializer; it declares no test or FastAPI behavior.",
    "tests/test_request_params/test_body/utils.py": "A test helper that reads one model name from an already-built OpenAPI document; it is not an independent test or FastAPI behavior.",
    "tests/test_request_params/test_file/utils.py": "A test helper that reads one model name from an already-built OpenAPI document; it is not an independent test or FastAPI behavior.",
    "tests/test_request_params/test_form/utils.py": "A test helper that reads one model name from an already-built OpenAPI document; it is not an independent test or FastAPI behavior.",
}


_RECIPE_CASE_INDEX = _recipe_case_index()
_SOURCE_LINK_INDEX = _source_link_index()

REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {}
for _test_path in TOP_LEVEL_REQUEST_PARAMETER_TESTS:
    REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = _mapping_for_test_module(
        _test_path, _SOURCE_LINK_INDEX
    )

for _test_path in REQUEST_PARAM_SOURCE_MODULES:
    if _test_path in _UNSUPPORTED_REQUEST_PARAM_MODULES:
        REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = _source_exclusion(
            _test_path, _UNSUPPORTED_REQUEST_PARAM_MODULES[_test_path]
        )
    elif _test_path in _REQUEST_PARAM_SUPPORT_EXCLUSIONS:
        if _test_path.endswith("/__init__.py"):
            if (FASTAPI_ROOT / _test_path).read_text(encoding="utf-8").strip():
                raise ValueError(f"expected empty package initializer at {_test_path}")
            REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = {
                "mapping_status": "source-backed-exclusion",
                "exclusion_reason": _REQUEST_PARAM_SUPPORT_EXCLUSIONS[_test_path],
                "supporting_sources": [],
                "source_file": _source_file(
                    _test_path, "empty initializer verified in pinned FastAPI 0.141.1 source"
                ),
            }
        else:
            helper_span = _nonempty_line_span(_test_path)
            REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = {
                "mapping_status": "source-backed-exclusion",
                "exclusion_reason": _REQUEST_PARAM_SUPPORT_EXCLUSIONS[_test_path],
                "supporting_sources": [helper_span] if helper_span else [],
                "source_file": _source_file(
                    _test_path, "test helper source in pinned FastAPI 0.141.1"
                ),
            }
    else:
        REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = _mapping_for_test_module(
            _test_path, _SOURCE_LINK_INDEX
        )


_TAIL_WAVE_CASE_ID = "fastapi.request-parameter-alias-validation-tail-wave.body-form-file"
_TAIL_WAVE_RECIPE = (
    "tests/fixtures/input-recipes/parity/request-parameter-alias-validation-tail-wave.yaml"
)
_TAIL_WAVE_WORKLOAD = "tests/fixtures/workloads/request_parameter_alias_validation_tail_wave.py"
_OPTIONAL_UPLOAD_ALIAS_CASE_ID = (
    "fastapi.request-optional-upload.alias-validation-alias.source-review"
)
_OPTIONAL_UPLOAD_MISSING_CASE_ID = "fastapi.request-optional-upload.optional-missing-doc-example"
_OPTIONAL_UPLOAD_RECIPE = (
    "tests/fixtures/input-recipes/parity/request-optional-upload-alias-validation-alias-review.yaml"
)
_OPTIONAL_UPLOAD_WORKLOAD = (
    "tests/fixtures/workloads/optional_upload_alias_validation_alias_review.py"
)
_OPTIONAL_LIST_SCHEMA_RECIPE = (
    "tests/fixtures/input-recipes/parity/optional-list-openapi-schema-source-review.yaml"
)
_OPTIONAL_LIST_SCHEMA_WORKLOAD = (
    "tests/fixtures/workloads/optional_list_openapi_schema_source_review.py"
)
_OPTIONAL_LIST_SCHEMA_CASES = {
    "fastapi.request-body.optional-list-openapi.no-alias",
    "fastapi.request-body.optional-list-openapi.alias",
    "fastapi.request-body.optional-list-openapi.validation-alias",
    "fastapi.request-body.optional-list-openapi.both-aliases",
}


def _tail_function_mapping(
    test_path: str,
    function_name: str,
    action_ids: list[str],
    behavior: str,
) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.141.1 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _TAIL_WAVE_RECIPE,
            "case_id": _TAIL_WAVE_CASE_ID,
            "action_ids": list(action_ids),
            "observation_selectors": ["http.body.bytes", "http.status"],
        },
        "rationale": behavior,
        "contract_gate": (
            "This is a representative request-source/alias input. It compares raw HTTP response selectors; it does not establish the entire source test's complete Pydantic error object, field-default matrix, or complete OpenAPI snapshot."
        ),
    }


def _optional_upload_function_mapping(
    test_path: str,
    function_name: str,
    case_id: str,
    action_ids: list[str],
    observation_selectors: list[str],
    behavior: str,
) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.141.1 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _OPTIONAL_UPLOAD_RECIPE,
            "case_id": case_id,
            "action_ids": list(action_ids),
            "observation_selectors": list(observation_selectors),
        },
        "rationale": behavior,
        "contract_gate": (
            "This maps only the UploadFile path in a pinned parametrized test; the sibling bytes path is not claimed. "
            "The alias cases distinguish the Python field name, File alias, and validation_alias, and the schema case "
            "observes the independent workload's request-body projection. Multipart framing and UploadFile parsing "
            "remain Starlette 1.6.0 / Starlette-RS-owned; the workflow does not establish full test-module behavior."
        ),
    }


def _optional_list_schema_function_mapping(
    test_path: str,
    function_name: str,
    case_id: str,
    behavior: str,
) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.141.1 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _OPTIONAL_LIST_SCHEMA_RECIPE,
            "case_id": case_id,
            "action_ids": ["inspect-openapi"],
            "observation_selectors": ["openapi.document"],
        },
        "rationale": behavior,
        "contract_gate": (
            "This maps the pinned schema function's direct Body and Pydantic-model variants to "
            "exact requestBody schema-reference and component properties JSON Pointer projections. "
            "It does not claim request validation, complete OpenAPI output, or the remainder of "
            "the parameterized test's behavior."
        ),
    }


REQUEST_PARAMETER_FUNCTION_MAPPINGS = {
    "tests/test_request_params/test_body/test_required_str.py": {
        "test_required_alias_and_validation_alias_by_alias": _tail_function_mapping(
            "tests/test_request_params/test_body/test_required_str.py",
            "test_required_alias_and_validation_alias_by_alias",
            ["body-declared-alias"],
            "The combined Body alias case sends the declared public alias while the field's validation alias names the accepted wire key.",
        ),
        "test_required_alias_and_validation_alias_by_validation_alias": _tail_function_mapping(
            "tests/test_request_params/test_body/test_required_str.py",
            "test_required_alias_and_validation_alias_by_validation_alias",
            ["body-validation-alias"],
            "The combined Body alias case sends the Pydantic validation alias used by FastAPI request-body extraction.",
        ),
    },
    "tests/test_request_params/test_form/test_required_str.py": {
        "test_required_alias_and_validation_alias_by_alias": _tail_function_mapping(
            "tests/test_request_params/test_form/test_required_str.py",
            "test_required_alias_and_validation_alias_by_alias",
            ["form-declared-alias"],
            "The combined Form alias case distinguishes its declared alias from the accepted validation alias.",
        ),
        "test_required_alias_and_validation_alias_by_validation_alias": _tail_function_mapping(
            "tests/test_request_params/test_form/test_required_str.py",
            "test_required_alias_and_validation_alias_by_validation_alias",
            ["form-validation-alias"],
            "The combined Form alias case sends the validation alias through a URL-encoded form input.",
        ),
    },
    "tests/test_request_params/test_file/test_required.py": {
        "test_required_alias_and_validation_alias_by_alias": _tail_function_mapping(
            "tests/test_request_params/test_file/test_required.py",
            "test_required_alias_and_validation_alias_by_alias",
            ["file-declared-alias"],
            "The combined File alias case distinguishes its declared alias from the accepted multipart field name.",
        ),
        "test_required_alias_and_validation_alias_by_validation_alias": _tail_function_mapping(
            "tests/test_request_params/test_file/test_required.py",
            "test_required_alias_and_validation_alias_by_validation_alias",
            ["file-validation-alias"],
            "The combined File alias case sends the Pydantic validation alias as a multipart part name.",
        ),
    },
    "tests/test_request_params/test_file/test_optional.py": {
        "test_optional_alias_and_validation_alias_schema": _optional_upload_function_mapping(
            "tests/test_request_params/test_file/test_optional.py",
            "test_optional_alias_and_validation_alias_schema",
            _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
            ["optional-upload-openapi-schema"],
            ["openapi.document", "openapi.paths"],
            "The pinned schema function checks both bytes and UploadFile routes; this link covers only the independent optional UploadFile route and observes its validation-alias request schema.",
        ),
        "test_optional_alias_and_validation_alias_missing": _optional_upload_function_mapping(
            "tests/test_request_params/test_file/test_optional.py",
            "test_optional_alias_and_validation_alias_missing",
            _OPTIONAL_UPLOAD_MISSING_CASE_ID,
            ["optional-upload-missing"],
            ["http.body.bytes", "http.status"],
            "The pinned parametrized test checks omission for both bytes and UploadFile; this independent case maps only the UploadFile omission branch.",
        ),
        "test_optional_alias_and_validation_alias_by_name": _optional_upload_function_mapping(
            "tests/test_request_params/test_file/test_optional.py",
            "test_optional_alias_and_validation_alias_by_name",
            _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
            ["optional-upload-python-name"],
            ["http.body.bytes", "http.status"],
            "The pinned parametrized test sends the Python field name; this link exercises that name on the independent optional UploadFile declaration.",
        ),
        "test_optional_alias_and_validation_alias_by_alias": _optional_upload_function_mapping(
            "tests/test_request_params/test_file/test_optional.py",
            "test_optional_alias_and_validation_alias_by_alias",
            _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
            ["optional-upload-declared-alias"],
            ["http.body.bytes", "http.status"],
            "The pinned parametrized test sends File.alias; this link observes the optional UploadFile behavior for a separately named declared alias.",
        ),
        "test_optional_alias_and_validation_alias_by_validation_alias": _optional_upload_function_mapping(
            "tests/test_request_params/test_file/test_optional.py",
            "test_optional_alias_and_validation_alias_by_validation_alias",
            _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
            ["optional-upload-validation-alias"],
            ["http.body.bytes", "http.status"],
            "The pinned parametrized test sends File.validation_alias; this link observes accepted extraction for the optional UploadFile path.",
        ),
    },
    "tests/test_request_params/test_body/test_optional_list.py": {
        "test_optional_list_str_schema": _optional_list_schema_function_mapping(
            "tests/test_request_params/test_body/test_optional_list.py",
            "test_optional_list_str_schema",
            "fastapi.request-body.optional-list-openapi.no-alias",
            "The pinned schema assertion covers direct Body and BaseModel routes without aliases; this case projects both request-body schema references and each component's properties object.",
        ),
        "test_optional_list_str_alias_schema": _optional_list_schema_function_mapping(
            "tests/test_request_params/test_body/test_optional_list.py",
            "test_optional_list_str_alias_schema",
            "fastapi.request-body.optional-list-openapi.alias",
            "The pinned schema assertion covers direct Body and BaseModel routes with a declared alias; this case projects the resulting alias property for each route form.",
        ),
        "test_optional_list_validation_alias_schema": _optional_list_schema_function_mapping(
            "tests/test_request_params/test_body/test_optional_list.py",
            "test_optional_list_validation_alias_schema",
            "fastapi.request-body.optional-list-openapi.validation-alias",
            "The pinned schema assertion covers direct Body and BaseModel routes with a validation alias; this case projects that property for each route form.",
        ),
        "test_optional_list_alias_and_validation_alias_schema": _optional_list_schema_function_mapping(
            "tests/test_request_params/test_body/test_optional_list.py",
            "test_optional_list_alias_and_validation_alias_schema",
            "fastapi.request-body.optional-list-openapi.both-aliases",
            "The pinned schema assertion covers direct Body and BaseModel routes with both aliases; this case projects the validation-alias property selected for each route form.",
        ),
    },
}

for _test_path, _function_rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.items():
    _entry = REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path]
    _entry["function_mappings"] = _function_rows
    _groups: dict[tuple[str, str], dict[str, set[str]]] = {}
    for _row in _function_rows.values():
        _workflow = _row["workflow_case"]
        _key = (_workflow["recipe_path"], _workflow["case_id"])
        _group = _groups.setdefault(_key, {"action_ids": set(), "selectors": set()})
        _group["action_ids"].update(_workflow["action_ids"])
        _group["selectors"].update(_workflow["observation_selectors"])
    for (_recipe_path, _case_id), _group in _groups.items():
        _entry["workflow_cases"].append(
            {
                "recipe_path": _recipe_path,
                "case_id": _case_id,
                "action_ids": sorted(_group["action_ids"]),
                "observation_selectors": sorted(_group["selectors"]),
            }
        )
        _entry["observation_selectors"] = sorted(
            set(_entry["observation_selectors"]) | _group["selectors"]
        )


def validate_request_parameter_mappings() -> list[str]:
    """Run focused static checks for source spans, selectors, and case links."""
    errors: list[str] = []
    fastapi_commit = subprocess.check_output(
        ["git", "-C", str(FASTAPI_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    starlette_commit = subprocess.check_output(
        ["git", "-C", str(STARLETTE_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    if fastapi_commit != FASTAPI_IDENTITY["commit"]:
        errors.append(f"FastAPI source commit differs from pinned identity: {fastapi_commit}")
    if starlette_commit != STARLETTE_IDENTITY["commit"]:
        errors.append(f"Starlette source commit differs from pinned identity: {starlette_commit}")
    backlog = json.loads((PROJECT_ROOT / "tests/fixtures/fixture-backlog.json").read_text())
    authority = backlog.get("authority", {})
    if authority.get("fastapi", {}).get("commit") != FASTAPI_IDENTITY["commit"]:
        errors.append("fixture backlog FastAPI identity differs from the selected oracle")
    if authority.get("starlette", {}).get("commit") != STARLETTE_IDENTITY["commit"]:
        errors.append("fixture backlog Starlette identity differs from the selected oracle")
    if authority.get("pydantic", {}).get("selected_version") != PYDANTIC_IDENTITY["version"]:
        errors.append("fixture backlog Pydantic version differs from the selected identity")

    for span in _FASTAPI_IMPLEMENTATION_SOURCES:
        source_path = FASTAPI_ROOT / span["path"]
        line_count = (
            len(source_path.read_text(encoding="utf-8").splitlines())
            if source_path.is_file()
            else 0
        )
        if not source_path.is_file() or not (
            1 <= span["start_line"] <= span["end_line"] <= line_count
        ):
            errors.append(f"invalid pinned FastAPI implementation span: {span}")
    for span in _STARLETTE_CONTRACT_SOURCES:
        source_path = STARLETTE_ROOT / span["path"]
        line_count = (
            len(source_path.read_text(encoding="utf-8").splitlines())
            if source_path.is_file()
            else 0
        )
        if not source_path.is_file() or not (
            1 <= span["start_line"] <= span["end_line"] <= line_count
        ):
            errors.append(f"invalid pinned Starlette contract span: {span}")

    expected_paths = set(TOP_LEVEL_REQUEST_PARAMETER_TESTS) | set(REQUEST_PARAM_SOURCE_MODULES)
    if set(REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS) != expected_paths:
        errors.append("mapping keys do not exactly match the declared request-parameter scope")

    recipe_index = _recipe_case_index()
    for test_path, mapping in REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS.items():
        source_path = FASTAPI_ROOT / test_path
        if not source_path.is_file():
            errors.append(f"missing pinned source module: {test_path}")
            continue
        source_lines = source_path.read_text(encoding="utf-8").splitlines()
        for span in mapping.get("source_test_spans", []):
            if span["path"] != test_path or not (
                1 <= span["start_line"] <= span["end_line"] <= len(source_lines)
            ):
                errors.append(f"invalid test function span in {test_path}: {span}")
        if mapping.get("source_test_spans") and mapping[
            "source_test_spans"
        ] != _test_function_spans(test_path):
            errors.append(f"test function spans no longer match pinned source AST: {test_path}")
        for span in mapping.get("supporting_sources", []):
            if (
                span
                and span["path"] == test_path
                and not (1 <= span["start_line"] <= span["end_line"] <= max(len(source_lines), 1))
            ):
                errors.append(f"invalid exclusion span in {test_path}: {span}")
        if mapping.get("mapping_status") == "source-backed-exclusion":
            if not mapping.get("exclusion_reason"):
                errors.append(f"exclusion lacks a source-backed reason: {test_path}")
            if not mapping.get("supporting_sources") and source_lines:
                if any(line.strip() for line in source_lines):
                    errors.append(f"nonempty source exclusion lacks source spans: {test_path}")
            continue
        if not mapping.get("workflow_cases"):
            errors.append(f"candidate module lacks input workflow links: {test_path}")
            continue
        actual_selectors: set[str] = set()
        for workflow in mapping["workflow_cases"]:
            case_row = recipe_index.get(workflow.get("case_id"))
            if case_row is None:
                errors.append(f"unknown workflow case for {test_path}: {workflow.get('case_id')}")
                continue
            if workflow.get("recipe_path") != case_row["recipe_path"]:
                errors.append(f"recipe path mismatch for case {workflow['case_id']}")
            case = case_row["case"]
            evidence_paths = {
                evidence.get("path")
                for evidence in case.get("source_evidence", []) or []
                if evidence.get("kind") == "upstream_test"
            }
            if test_path not in evidence_paths:
                # Specific action-level aliases may use a case that names its
                # upstream module at the enclosing module row; require that
                # exact source file linkage here as well.
                errors.append(f"case {workflow['case_id']} does not cite {test_path}")
            action_ids = {action.get("action_id") for action in case.get("actions", [])}
            if not set(workflow.get("action_ids", [])) <= action_ids:
                errors.append(f"unknown action ID in {workflow['case_id']} for {test_path}")
            declared = set(workflow.get("observation_selectors", []))
            actual = set(case_row["observation_selectors"])
            if not declared <= actual:
                errors.append(
                    f"selectors are not produced by {workflow['case_id']}: {sorted(declared - actual)}"
                )
            actual_selectors.update(declared)
        if not set(mapping.get("observation_selectors", [])) <= actual_selectors:
            errors.append(f"module selectors exceed linked workflow observations: {test_path}")

    tail_path = PROJECT_ROOT / _TAIL_WAVE_RECIPE
    tail = yaml.safe_load(tail_path.read_text(encoding="utf-8"))
    tail_cases = tail.get("cases", [])
    if len(tail_cases) != 1 or tail_cases[0].get("case_id") != _TAIL_WAVE_CASE_ID:
        errors.append("tail alias recipe does not contain its one declared case")
    optional_upload_path = PROJECT_ROOT / _OPTIONAL_UPLOAD_RECIPE
    optional_upload = yaml.safe_load(optional_upload_path.read_text(encoding="utf-8"))
    optional_upload_cases = {case.get("case_id"): case for case in optional_upload.get("cases", [])}
    if set(optional_upload_cases) != {
        _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
        _OPTIONAL_UPLOAD_MISSING_CASE_ID,
    }:
        errors.append("optional UploadFile alias recipe does not contain its two reviewed cases")
    optional_list_schema_path = PROJECT_ROOT / _OPTIONAL_LIST_SCHEMA_RECIPE
    optional_list_schema = yaml.safe_load(optional_list_schema_path.read_text(encoding="utf-8"))
    optional_list_schema_cases = {
        case.get("case_id"): case for case in optional_list_schema.get("cases", [])
    }
    if set(optional_list_schema_cases) != _OPTIONAL_LIST_SCHEMA_CASES:
        errors.append("optional-list OpenAPI recipe does not contain its four reviewed cases")
    forbidden = {
        "expected",
        "expected_output",
        "expected_outputs",
        "measurement",
        "measurements",
        "benchmark",
    }

    def scan_input_only(value: Any, location: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if str(key).lower() in forbidden:
                    errors.append(f"non-input recipe field {key!r} at {location}")
                scan_input_only(item, f"{location}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                scan_input_only(item, f"{location}[{index}]")

    scan_input_only(tail, str(tail_path.relative_to(PROJECT_ROOT)))
    scan_input_only(optional_upload, str(optional_upload_path.relative_to(PROJECT_ROOT)))
    scan_input_only(
        optional_list_schema,
        str(optional_list_schema_path.relative_to(PROJECT_ROOT)),
    )
    if not (PROJECT_ROOT / _TAIL_WAVE_WORKLOAD).is_file():
        errors.append("tail recipe workload file is missing")
    if tail.get("workload", {}).get("file") != _TAIL_WAVE_WORKLOAD:
        errors.append("tail recipe references a different workload than the reviewed one")
    if not (PROJECT_ROOT / _OPTIONAL_UPLOAD_WORKLOAD).is_file():
        errors.append("optional UploadFile alias workload file is missing")
    if optional_upload.get("workload", {}).get("file") != _OPTIONAL_UPLOAD_WORKLOAD:
        errors.append(
            "optional UploadFile alias recipe references a different workload than the reviewed one"
        )
    if not (PROJECT_ROOT / _OPTIONAL_LIST_SCHEMA_WORKLOAD).is_file():
        errors.append("optional-list OpenAPI workload file is missing")
    if optional_list_schema.get("workload", {}).get("file") != _OPTIONAL_LIST_SCHEMA_WORKLOAD:
        errors.append("optional-list OpenAPI recipe references a different reviewed workload")
    tail_actions = {
        action.get("action_id") for case in tail_cases for action in case.get("actions", [])
    }
    referenced_tail_actions = {
        action_id
        for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
        for row in rows.values()
        if row["workflow_case"]["case_id"] == _TAIL_WAVE_CASE_ID
        for action_id in row["workflow_case"]["action_ids"]
    }
    if not referenced_tail_actions <= tail_actions:
        errors.append(
            f"tail function mapping references unknown action IDs: {sorted(referenced_tail_actions - tail_actions)}"
        )
    for case_id, case in optional_upload_cases.items():
        declared_actions = {action.get("action_id") for action in case.get("actions", [])}
        referenced_actions = {
            action_id
            for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
            for row in rows.values()
            if row["workflow_case"]["case_id"] == case_id
            for action_id in row["workflow_case"]["action_ids"]
        }
        if not referenced_actions <= declared_actions:
            errors.append(
                f"optional UploadFile mapping references unknown actions for {case_id}: "
                f"{sorted(referenced_actions - declared_actions)}"
            )
    for case_id, case in optional_list_schema_cases.items():
        declared_actions = {action.get("action_id") for action in case.get("actions", [])}
        referenced_actions = {
            action_id
            for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
            for row in rows.values()
            if row["workflow_case"]["case_id"] == case_id
            for action_id in row["workflow_case"]["action_ids"]
        }
        if not referenced_actions <= declared_actions:
            errors.append(
                f"optional-list OpenAPI mapping references unknown actions for {case_id}: "
                f"{sorted(referenced_actions - declared_actions)}"
            )

    tail_spans = {
        (
            row["source_span"]["path"],
            row["source_span"]["start_line"],
            row["source_span"]["end_line"],
        )
        for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
        for row in rows.values()
    }
    for test_path, rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.items():
        source_lines = (FASTAPI_ROOT / test_path).read_text(encoding="utf-8").splitlines()
        for function_name, row in rows.items():
            span = row["source_span"]
            if not (1 <= span["start_line"] <= span["end_line"] <= len(source_lines)):
                errors.append(
                    f"invalid request-parameter function source span: {test_path}:{function_name}"
                )
            workflow = row["workflow_case"]
            if workflow["case_id"] == _TAIL_WAVE_CASE_ID:
                expected_recipe = _TAIL_WAVE_RECIPE
            elif workflow["case_id"] in {
                _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
                _OPTIONAL_UPLOAD_MISSING_CASE_ID,
            }:
                expected_recipe = _OPTIONAL_UPLOAD_RECIPE
            else:
                expected_recipe = _OPTIONAL_LIST_SCHEMA_RECIPE
            valid_case_ids = {
                _TAIL_WAVE_CASE_ID,
                _OPTIONAL_UPLOAD_ALIAS_CASE_ID,
                _OPTIONAL_UPLOAD_MISSING_CASE_ID,
            } | _OPTIONAL_LIST_SCHEMA_CASES
            if workflow["case_id"] not in valid_case_ids:
                errors.append(
                    f"request-parameter function case ID mismatch: {test_path}:{function_name}"
                )
            if workflow["recipe_path"] != expected_recipe:
                errors.append(
                    f"request-parameter function recipe path mismatch: {test_path}:{function_name}"
                )
            case_map = (
                {case["case_id"]: case for case in tail_cases}
                | optional_upload_cases
                | optional_list_schema_cases
            )
            case = case_map.get(workflow["case_id"])
            if case is None:
                errors.append(
                    f"unknown request-parameter function case: {test_path}:{function_name}"
                )
                continue
            declared_action_ids = {action.get("action_id") for action in case.get("actions", [])}
            if not set(workflow["action_ids"]) <= declared_action_ids:
                errors.append(
                    f"request-parameter function action mismatch: {test_path}:{function_name}"
                )
            actual_selectors = set(_workflow_selectors(case))
            if not set(workflow["observation_selectors"]) <= actual_selectors:
                errors.append(
                    f"request-parameter function selectors mismatch: {test_path}:{function_name}"
                )
    if len(tail_spans) != sum(len(rows) for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()):
        errors.append("request-parameter function mappings reuse an ambiguous source span")
    return errors


if __name__ == "__main__":
    validation_errors = validate_request_parameter_mappings()
    if validation_errors:
        raise SystemExit("\n".join(validation_errors))
    print(
        f"validated {len(REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS)} request-parameter modules; "
        f"{sum(len(row.get('workflow_cases', [])) for row in REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS.values())} case links"
    )
