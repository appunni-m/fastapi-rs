"""Source-reviewed request-parameter mappings for the FastAPI 0.157.0 atlas.

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
from urllib.parse import urlsplit

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"
RECIPE_ROOT = PROJECT_ROOT / "tests/fixtures/input-recipes/parity"

FASTAPI_IDENTITY = {
    "version": "0.157.0",
    "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
}
STARLETTE_IDENTITY = {
    "version": "1.6.0",
    "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    "role": "sole Starlette oracle and generic-framework contract",
}
PYDANTIC_IDENTITY = {
    "version": "2.13.5",
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
                    f"upstream FastAPI 0.157.0 test function {node.name}",
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
                if "body_json" in values:
                    selected.add("http.body.json")
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
            "fastapi-rs/python-asgi-workflow@13",
            "fastapi-rs/python-asgi-workflow@17",
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
        314,
        416,
        "FastAPI 0.157.0 inspects endpoint signatures, infers parameter fields, and classifies path/query/header/cookie/body fields.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        423,
        620,
        "FastAPI 0.157.0 resolves Annotated/default parameter metadata, aliases, path restrictions, and query type restrictions.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        822,
        842,
        "FastAPI 0.157.0 adapts extracted values and required/default handling to Pydantic ModelField validation.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        843,
        991,
        "FastAPI 0.157.0 extracts query/header/cookie/path values and aggregates request parameter errors.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        1054,
        1076,
        "FastAPI 0.157.0 selects whether request-body fields must be embedded into one body object.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        1078,
        1236,
        "FastAPI 0.157.0 extracts and validates JSON, Form, and File request-body fields.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        1237,
        1286,
        "FastAPI 0.157.0 combines Body fields and carries a common declared media type into the aggregate field.",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        1287,
        1320,
        "FastAPI 0.157.0 selects a Pydantic validation alias before the declared field alias.",
    ),
    _source(
        "fastapi/routing.py",
        398,
        491,
        "FastAPI 0.157.0 selects JSON body decoding by Content-Type and translates malformed JSON into request validation errors.",
    ),
    _source(
        "fastapi/openapi/utils.py",
        159,
        215,
        "FastAPI 0.157.0 projects parameter location, validation alias, requiredness, and schema into OpenAPI.",
    ),
    _source(
        "fastapi/openapi/utils.py",
        216,
        249,
        "FastAPI 0.157.0 uses Body.media_type as the requestBody content key.",
    ),
    _source(
        "fastapi/openapi/utils.py",
        296,
        527,
        "FastAPI 0.157.0 builds operation parameter lists and request-body OpenAPI entries.",
    ),
    _source(
        "fastapi/params.py",
        27,
        231,
        "FastAPI 0.157.0 parameter metadata and constraints.",
    ),
    _source(
        "fastapi/params.py",
        232,
        497,
        "FastAPI 0.157.0 Query, Header, and Cookie metadata and constraints.",
    ),
    _source(
        "fastapi/params.py",
        498,
        740,
        "FastAPI 0.157.0 Body, Form, and File metadata and constraints.",
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

_PYDANTIC_BOUNDARY = "Pydantic 2.13.5 owns its public ModelField/BaseModel field metadata, core type coercion, and validation semantics. FastAPI owns inspecting Python endpoint annotations, constructing its field adapter, choosing request sources/locations, and shaping FastAPI validation errors. This mapping does not claim a Rust reimplementation of Pydantic internals."
_STARLETTE_BOUNDARY = "Starlette 1.6.0 is the sole generic-framework oracle. HTTP route matching, ASGI request-body/form/multipart parsing, query/header/cookie data structures, and UploadFile mechanics are assigned to the separate Starlette-RS contract. FastAPI owns parameter declaration inspection, source selection, body-field composition, and FastAPI/OpenAPI validation projections."
_PARITY_GATE = "Input mapping only: the cited recipe cases contain stimuli and observation selectors, not expected outputs or measurements. The cases are selected examples from the pinned test module; no complete module parity result is claimed, and any focused workflow receipt covers only its listed cases. Full module snapshots, unlisted defaults/aliases/constraints, complete validation error structures, and exact TestClient behavior are not established by these cases. Compare only the listed workflow selectors; generic request and parser behavior remains under Starlette 1.6.0's separate contract."
_BODY_MEDIA_TYPE_PARITY_GATE = "Input mapping only: the recipe contains stimuli and observation selectors, not expected outputs or measurements. The original upstream test asserts the two-route OpenAPI schema only; explicitly named source-derived cases add independent HTTP probes grounded in pinned implementation branches. No complete module parity result is claimed; any focused workflow receipt covers only its listed cases. Full module snapshots, unlisted defaults/aliases/constraints, and exact TestClient behavior remain outside this mapping. Generic request and parser behavior remains under Starlette 1.6.0's separate contract."


def _mapping_for_test_module(
    test_path: str, case_index: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    spans = _test_function_spans(test_path)
    if not spans:
        raise ValueError(f"expected test functions for candidate module {test_path}")
    function_exclusions = _TOP_LEVEL_REQUEST_PARAMETER_FUNCTION_EXCLUSIONS.get(test_path, {})
    spans_by_function = {span["role"].rsplit(" ", 1)[-1]: span for span in spans}
    unknown_exclusions = set(function_exclusions) - set(spans_by_function)
    if unknown_exclusions:
        raise ValueError(
            f"test-function exclusions do not match pinned source in {test_path}: "
            f"{sorted(unknown_exclusions)}"
        )
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
    function_case_mappings = _path_test_function_case_mappings(test_path)
    contract_gate = (
        _BODY_MEDIA_TYPE_PARITY_GATE
        if test_path == "tests/test_request_body_parameters_media_type.py"
        else _PARITY_GATE
    )
    return {
        "mapping_status": "source-reviewed-input-candidate; parity pending",
        "source_test_spans": spans,
        "excluded_test_functions": [
            {
                "name": name,
                "reason": reason,
                "source_span": spans_by_function[name],
            }
            for name, reason in sorted(function_exclusions.items())
        ],
        "workflow_cases": workflow_cases,
        **({"function_case_mappings": function_case_mappings} if function_case_mappings else {}),
        "observation_selectors": selectors,
        "fastapi_implementation_sources": list(_FASTAPI_IMPLEMENTATION_SOURCES),
        "pydantic_ownership_boundary": _PYDANTIC_BOUNDARY,
        "starlette_ownership_boundary": _STARLETTE_BOUNDARY,
        "starlette_contract_sources": list(_STARLETTE_CONTRACT_SOURCES),
        "contract_gate": contract_gate,
    }


def _path_test_function_case_mappings(test_path: str) -> list[dict[str, Any]]:
    """Join each pinned path test to its exact independent request stimulus."""
    if test_path != "tests/test_path.py":
        return []

    recipe_paths = {
        "tests/fixtures/input-recipes/parity/path-test-input-review.yaml",
        "tests/fixtures/input-recipes/parity/path-validation-test-path-upstream.yaml",
    }
    cases_by_request: dict[tuple[str, str], dict[str, Any]] = {}
    selected_cases = [
        (case_id, row)
        for case_id, row in _RECIPE_CASE_INDEX.items()
        if row["recipe_path"] in recipe_paths
    ]
    for case_id, row in selected_cases:
        actions = row["case"].get("actions", [])
        requests = [action for action in actions if action.get("kind") == "http_request"]
        if len(requests) != 1:
            raise ValueError(f"expected one request action in {case_id}")
        scope = requests[0].get("scope", {})
        request_key = (scope.get("method"), scope.get("path"))
        if not all(isinstance(value, str) and value for value in request_key):
            raise ValueError(f"expected literal method and path in {case_id}")
        if request_key in cases_by_request:
            raise ValueError(f"duplicate path-test fixture request: {request_key}")
        cases_by_request[request_key] = {"case_id": case_id, **row}

    source_path = FASTAPI_ROOT / test_path
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    function_case_mappings = []
    used_case_ids: set[str] = set()
    for node in tree.body:
        if not isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ) or not node.name.startswith("test_"):
            continue
        calls = [
            call
            for call in ast.walk(node)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "client"
            and call.func.attr in {"get", "post", "put", "patch", "delete", "options", "head"}
        ]
        if len(calls) != 1 or not calls[0].args:
            raise ValueError(f"expected one literal client request in {test_path}::{node.name}")
        path_arg = calls[0].args[0]
        if not isinstance(path_arg, ast.Constant) or not isinstance(path_arg.value, str):
            raise ValueError(f"expected literal request path in {test_path}::{node.name}")
        request_key = (calls[0].func.attr.upper(), path_arg.value)
        case = cases_by_request.get(request_key)
        if case is None:
            raise ValueError(
                f"no independent input matches {test_path}::{node.name} request {request_key}"
            )
        case_id = case["case_id"]
        if case_id in used_case_ids:
            raise ValueError(f"multiple path tests map to fixture case {case_id}")
        used_case_ids.add(case_id)
        action_selectors = _workflow_selectors({"actions": requests})
        has_json_observation = "http.body.json" in action_selectors
        function_case_mappings.append(
            {
                "source_function": node.name,
                "source_evidence": _source(
                    test_path,
                    node.lineno,
                    node.end_lineno or node.lineno,
                    f"pinned FastAPI 0.157.0 test function {node.name}",
                ),
                "request": {"method": request_key[0], "path": request_key[1]},
                "recipe_path": case["recipe_path"],
                "case_id": case_id,
                "mapping_basis": "exact method and literal request path",
                "mapping_scope": (
                    "request_and_parsed_json_response"
                    if has_json_observation
                    else "request_stimulus_only"
                ),
                "observation_selectors": action_selectors,
                "scope_note": (
                    "The exact independent request selects status, raw bytes, and the full parsed "
                    "JSON response observed by the upstream response.json() assertion."
                    if has_json_observation
                    else "This link establishes request-stimulus identity; it does not claim "
                    "that fixture selectors reproduce the upstream function's assertions."
                ),
            }
        )

    if len(used_case_ids) != len(cases_by_request):
        unmatched = sorted(
            set(cases_by_request)
            - {(row["request"]["method"], row["request"]["path"]) for row in function_case_mappings}
        )
        raise ValueError(f"path-test input cases without exact test-function links: {unmatched}")
    return function_case_mappings


def _source_exclusion(test_path: str, reason: str) -> dict[str, Any]:
    span = _nonempty_line_span(test_path)
    sources = [span] if span else []
    return {
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": reason,
        "supporting_sources": sources,
        "source_file": _source_file(
            test_path, "pinned FastAPI 0.157.0 test source for the exclusion"
        ),
        "starlette_ownership_boundary": _STARLETTE_BOUNDARY,
        "starlette_contract_sources": list(_STARLETTE_CONTRACT_SOURCES),
    }


_UNSUPPORTED_REQUEST_PARAM_MODULES = {
    "tests/test_request_params/test_cookie/test_list.py": (
        "The pinned module contains only comments that its repeated-cookie list input cannot be supplied and comma-delimited cookie values are unsupported by Starlette; it defines no test function or independent behavior. This exclusion applies only to that list-form scenario. The separate ASGI input fastapi.request-parameters.extra-model.cookie-duplicate-last-value exercises repeated cookie keys and their last-value handling, so duplicate-cookie behavior is not excluded here. Generic cookie parsing remains owned by Starlette 1.6.0 and Starlette-RS."
    ),
    "tests/test_request_params/test_cookie/test_optional_list.py": (
        "The pinned optional-list module contains only comments that its repeated-cookie list input cannot be supplied and comma-delimited cookie values are unsupported by Starlette; it defines no test function or independent behavior. This exclusion applies only to that optional list-form scenario. The separate ASGI input fastapi.request-parameters.extra-model.cookie-duplicate-last-value exercises repeated cookie keys and their last-value handling, so duplicate-cookie behavior is not excluded here. Generic cookie parsing remains owned by Starlette 1.6.0 and Starlette-RS."
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

_TOP_LEVEL_REQUEST_PARAMETER_EXCLUSIONS = {
    "tests/test_param_class.py": (
        "Both pinned tests directly import and construct fastapi.params.Param. The reviewed "
        "FastAPI 0.157.0 atlas classifies Param as private/internal and its base constructor "
        "as uncertain, so FastAPI-RS does not expose that base through the public facade. "
        "Equivalent missing/provided optional-query behavior is mapped through the supported "
        "Query factory in query-default-wave; this exclusion is limited to direct Param use."
    ),
}

_TOP_LEVEL_REQUEST_PARAMETER_FUNCTION_EXCLUSIONS = {
    "tests/test_params_repr.py": {
        name: (
            "Direct construction and repr of fastapi.params.Param is outside the reviewed "
            "public contract; Param is classified private/internal."
        )
        for name in (
            "test_param_repr_str",
            "test_param_repr_none",
            "test_param_repr_ellipsis",
            "test_param_repr_number",
            "test_param_repr_list",
        )
    },
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
    if _test_path in _TOP_LEVEL_REQUEST_PARAMETER_EXCLUSIONS:
        REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = _source_exclusion(
            _test_path, _TOP_LEVEL_REQUEST_PARAMETER_EXCLUSIONS[_test_path]
        )
    else:
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
                    _test_path, "empty initializer verified in pinned FastAPI 0.157.0 source"
                ),
            }
        else:
            helper_span = _nonempty_line_span(_test_path)
            REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = {
                "mapping_status": "source-backed-exclusion",
                "exclusion_reason": _REQUEST_PARAM_SUPPORT_EXCLUSIONS[_test_path],
                "supporting_sources": [helper_span] if helper_span else [],
                "source_file": _source_file(
                    _test_path, "test helper source in pinned FastAPI 0.157.0"
                ),
            }
    else:
        REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_test_path] = _mapping_for_test_module(
            _test_path, _SOURCE_LINK_INDEX
        )


_TAIL_WAVE_CASE_ID = "fastapi.request-parameter-alias-validation-tail-wave.body-form-file"
_TAIL_WAVE_CASES = {
    _TAIL_WAVE_CASE_ID,
    "fastapi.request-parameter-alias-validation-tail-wave.header-validation-alias",
    "fastapi.request-parameter-alias-validation-tail-wave.header-alias-validation-alias",
    "fastapi.request-parameter-alias-validation-tail-wave.cookie-validation-alias",
    "fastapi.request-parameter-alias-validation-tail-wave.cookie-alias-validation-alias",
}
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
_OPTIONAL_BODY_STR_RECIPE = (
    "tests/fixtures/input-recipes/parity/optional-body-str-alias-review.yaml"
)
_OPTIONAL_LIST_SCHEMA_CASES = {
    "fastapi.request-body.optional-list-openapi.no-alias",
    "fastapi.request-body.optional-list-openapi.alias",
    "fastapi.request-body.optional-list-openapi.validation-alias",
    "fastapi.request-body.optional-list-openapi.both-aliases",
}
_REQUEST_UPLOADS_RECIPE = "tests/fixtures/input-recipes/parity/request-uploads.yaml"
_FILE_LIST_FORM_ORDER_CASE = "fastapi.request-uploads.file-form-order.test-file-list-form-order"
_QUERY_LIST_VALIDATION_ALIAS_RECIPE = (
    "tests/fixtures/input-recipes/parity/query-validation-alias-list-cases.yaml"
)
_QUERY_REQUIRED_LIST_RECIPE = "tests/fixtures/input-recipes/parity/query-required-list-aliases.yaml"
_QUERY_REQUIRED_LIST_WORKLOAD = "tests/fixtures/workloads/query_required_list_aliases.py"
_QUERY_REQUIRED_LIST_CASES = {
    "fastapi.request-parameters.query.required-list.plain",
    "fastapi.request-parameters.query.required-list.declared-alias",
}
_QUERY_REQUIRED_OPTIONAL_INTEGER_RECIPE = (
    "tests/fixtures/input-recipes/parity/query-required-optional-integer-upstream.yaml"
)
_OPTIONAL_QUERY_LIST_ALIAS_RECIPE = (
    "tests/fixtures/input-recipes/parity/optional-query-list-aliases.yaml"
)
_OPTIONAL_QUERY_LIST_ALIAS_WORKLOAD = "tests/fixtures/workloads/optional_query_list_aliases.py"
_OPTIONAL_QUERY_LIST_ALIAS_CASES = {
    "fastapi.request-parameters.query.optional-list.alias.openapi",
    "fastapi.request-parameters.query.optional-list.alias.missing",
    "fastapi.request-parameters.query.optional-list.alias.field-name",
    "fastapi.request-parameters.query.optional-list.alias.accepts-wire-name",
    "fastapi.request-parameters.query.optional-list.validation-alias.openapi",
    "fastapi.request-parameters.query.optional-list.validation-alias.missing",
    "fastapi.request-parameters.query.optional-list.validation-alias.field-name",
    "fastapi.request-parameters.query.optional-list.validation-alias.accepts-wire-name",
    "fastapi.request-parameters.query.optional-list.combined-aliases.openapi",
    "fastapi.request-parameters.query.optional-list.combined-aliases.missing",
    "fastapi.request-parameters.query.optional-list.combined-aliases.field-name",
    "fastapi.request-parameters.query.optional-list.combined-aliases.declared-alias",
    "fastapi.request-parameters.query.optional-list.combined-aliases.validation-alias",
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
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


def _header_cookie_alias_function_mapping(
    test_path: str,
    function_name: str,
    case_id: str,
    action_id: str,
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _TAIL_WAVE_RECIPE,
            "case_id": case_id,
            "action_ids": [action_id],
            "observation_selectors": observation_selectors,
        },
        "rationale": behavior,
        "contract_gate": (
            "This is a partial input mapping for one direct Header or Cookie declaration. "
            "The pinned parametrized test also covers its BaseModel route; that route is not "
            "claimed here. Only the selected status/body or route-specific OpenAPI parameter "
            "projection is compared, with generic cookie/header parsing owned by Starlette."
        ),
    }


def _header_cookie_alias_module_mappings(parameter: str, kind: str) -> dict[str, Any]:
    case_root = "fastapi.request-parameter-alias-validation-tail-wave"
    direct_case = f"{case_root}.{parameter}-validation-alias"
    combined_case = f"{case_root}.{parameter}-alias-validation-alias"
    rows = [
        (
            "test_required_validation_alias_schema",
            direct_case,
            f"openapi-{parameter}-validation-alias",
            ["openapi.document", "openapi.paths"],
            f"The selected OpenAPI pointer isolates the direct {kind} parameter declaration that uses only validation_alias.",
        ),
        (
            "test_required_validation_alias_by_name",
            direct_case,
            f"{parameter}-validation-alias-python-name",
            ["http.body.bytes", "http.status"],
            f"The direct {kind} case submits the Python parameter name while validation_alias supplies the alternate wire name.",
        ),
        (
            "test_required_validation_alias_by_validation_alias",
            direct_case,
            f"{parameter}-validation-alias-wire-name",
            ["http.body.bytes", "http.status"],
            f"The direct {kind} case submits the validation alias as the request name.",
        ),
        (
            "test_required_alias_and_validation_alias_schema",
            combined_case,
            f"openapi-{parameter}-alias-validation-alias",
            ["openapi.document", "openapi.paths"],
            f"The selected OpenAPI pointer isolates the direct {kind} declaration with both alias and validation_alias.",
        ),
        (
            "test_required_alias_and_validation_alias_by_name",
            combined_case,
            f"{parameter}-both-aliases-python-name",
            ["http.body.bytes", "http.status"],
            f"The direct {kind} case submits the Python parameter name while both aliases are declared.",
        ),
        (
            "test_required_alias_and_validation_alias_by_alias",
            combined_case,
            f"{parameter}-both-aliases-declared-name",
            ["http.body.bytes", "http.status"],
            f"The direct {kind} case submits the declared alias while validation_alias names the alternate wire field.",
        ),
        (
            "test_required_alias_and_validation_alias_by_validation_alias",
            combined_case,
            f"{parameter}-both-aliases-validation-name",
            ["http.body.bytes", "http.status"],
            f"The direct {kind} case submits the validation alias when both aliases are declared.",
        ),
    ]
    test_path = f"tests/test_request_params/test_{parameter}/test_required_str.py"
    return {
        function_name: _header_cookie_alias_function_mapping(
            test_path,
            function_name,
            case_id,
            action_id,
            selectors,
            behavior,
        )
        for function_name, case_id, action_id, selectors, behavior in rows
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
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


def _optional_body_str_function_mapping(
    function_name: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
    behavior: str,
) -> dict[str, Any]:
    test_path = "tests/test_request_params/test_body/test_optional_str.py"
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _OPTIONAL_BODY_STR_RECIPE,
            "case_id": case_id,
            "action_ids": list(action_ids),
            "observation_selectors": list(selectors),
        },
        "rationale": behavior,
        "contract_gate": (
            "Input-only partial mapping to independently declared optional string Body and "
            "Pydantic-model routes. It records selected status/body or OpenAPI projections, "
            "not expected outputs or parity; it does not cover every test in the module or "
            "the complete OpenAPI document. FastAPI owns body-field defaults and alias "
            "selection; generic request-body handling remains under Starlette 1.6.0."
        ),
    }


def _request_http_function_mapping(
    test_path: str,
    function_name: str,
    case_id: str,
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _REQUEST_UPLOADS_RECIPE,
            "case_id": case_id,
            "action_ids": list(action_ids),
            "observation_selectors": ["http.body.bytes", "http.status"],
        },
        "rationale": behavior,
        "contract_gate": (
            "Partial: the input case links this one source function to two independently "
            "declared `list[bytes]`/Form routes and observes only HTTP status and response bytes. "
            "It is a source-to-input mapping, not a parity result; multipart parsing remains "
            "under the separate Starlette 1.6.0 contract."
        ),
    }


_FIELD_OPTIONS_TEST_PATH = "tests/test_request_params/test_field_options.py"
_FIELD_OPTIONS_RECIPE = "tests/fixtures/input-recipes/parity/field-options-0157.yaml"
_FIELD_OPTIONS_CASE_ID = "fastapi.request-parameters.field-options.source-review"
_FIELD_OPTIONS_ACTION_IDS = {
    "test_union_mode": [
        f"union-{location}-{mode}"
        for location in ("path", "query", "header", "cookie", "body", "form")
        for mode in ("none", "smart", "left-to-right")
    ],
    "test_fail_fast": [
        f"fail-fast-{location}-{setting}"
        for location in ("query", "header", "body", "form")
        for setting in ("fast", "all")
    ],
    "test_omitted_options_preserve_pydantic_validation_metadata": [
        "omitted-options-valid",
        "omitted-options-invalid",
    ],
    "test_explicit_options_override_pydantic_validation_metadata": [
        "explicit-options-valid",
        "explicit-options-invalid",
    ],
    "test_compiled_pattern": [
        f"pattern-{location}-{value}"
        for location in ("path", "query", "header", "cookie", "body", "form")
        for value in ("abc", "xyz")
    ],
    "test_file_list_fail_fast": [
        "file-fail-fast-fast",
        "file-fail-fast-all",
        "file-fail-fast-valid",
    ],
    "test_query_options": ["query-options"],
    "test_body_options": ["body-options"],
    "test_openapi_schema": ["openapi-options"],
}


def _field_options_function_mapping(
    function_name: str,
    action_ids: list[str],
    selectors: list[str],
    rationale: str,
    feature_ids: list[str] | None = None,
) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / _FIELD_OPTIONS_TEST_PATH).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exact source function {function_name} in {_FIELD_OPTIONS_TEST_PATH}"
        )
    function = matches[0]
    return {
        "source_span": _source(
            _FIELD_OPTIONS_TEST_PATH,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "supporting_sources": [
            _source(
                "fastapi/_compat/v2.py",
                359,
                368,
                "FastAPI 0.157.0 copies FieldInfo and merges its annotation metadata before request-field construction.",
            )
        ],
        "workflow_case": {
            "recipe_path": _FIELD_OPTIONS_RECIPE,
            "case_id": _FIELD_OPTIONS_CASE_ID,
            "action_ids": list(action_ids),
            "observation_selectors": list(selectors),
        },
        "feature_ids": feature_ids or ["request-validation"],
        "rationale": rationale,
        "contract_gate": (
            "Input-only partial mapping to independently declared routes. The linked requests "
            "and selected HTTP/OpenAPI observations exercise only the listed field options and "
            "parameter locations; they do not establish complete test-function parity or the "
            "full OpenAPI snapshot. Pydantic owns its field validation semantics, while "
            "FastAPI owns parameter metadata propagation and request-source projection; "
            "generic request and multipart parsing remains under Starlette 1.6.0."
        ),
    }


_NULLABLE_DEFAULTS_RECIPE = (
    "tests/fixtures/input-recipes/parity/request-nullable-defaults-0157.yaml"
)
_NULLABLE_DEFAULTS_CASE_IDS = {
    "file": "fastapi.request-parameters.nullable-defaults.file",
    "form": "fastapi.request-parameters.nullable-defaults.form",
    "header": "fastapi.request-parameters.nullable-defaults.header",
    "locations": "fastapi.request-parameters.nullable-defaults.locations",
}


def _nullable_defaults_function_mapping(
    test_path: str,
    function_name: str,
    case_name: str,
    action_ids: list[str],
    selectors: list[str],
    rationale: str,
    feature_ids: list[str] | None = None,
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _NULLABLE_DEFAULTS_RECIPE,
            "case_id": _NULLABLE_DEFAULTS_CASE_IDS[case_name],
            "action_ids": list(action_ids),
            "observation_selectors": list(selectors),
        },
        "feature_ids": feature_ids or ["request-validation"],
        "rationale": rationale,
        "contract_gate": (
            "Input-only partial mapping to independent request routes and selected HTTP/OpenAPI "
            "observations. It does not claim complete test-function or module parity, complete "
            "validation-error objects, or a full OpenAPI snapshot. FastAPI owns request-field "
            "construction, defaults, and source projection; Pydantic owns model field state and "
            "validation semantics, while Starlette 1.6.0 owns generic form and multipart parsing."
        ),
    }


def _required_parameter_once_openapi_function_mapping() -> dict[str, Any]:
    """Link the focused OpenAPI parameter projection to its exact source test."""
    test_path = "tests/test_enforce_once_required_parameter.py"
    function_name = "test_openapi_schema"
    case_id = "fastapi.dependencies.required-parameter-once.openapi"
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    case_row = _RECIPE_CASE_INDEX.get(case_id)
    if (
        case_row is None
        or case_row["recipe_path"]
        != "tests/fixtures/input-recipes/parity/dependency-required-parameter-once-upstream.yaml"
    ):
        raise ValueError(f"unknown required-parameter OpenAPI case: {case_id}")
    actions = case_row["case"].get("actions", [])
    if len(actions) != 1 or actions[0].get("action_id") != "single-openapi-query-parameter":
        raise ValueError(f"expected one focused OpenAPI action in {case_id}")
    pointers = [
        pointer
        for observation in actions[0].get("observations", [])
        if observation.get("kind") == "openapi"
        for pointer in observation.get("json_pointers", [])
    ]
    if pointers != ["/paths/~1foo/get/parameters"]:
        raise ValueError(
            f"required-parameter OpenAPI case changed its focused projection: {pointers}"
        )
    selectors = _workflow_selectors(case_row["case"])
    if selectors != [
        "docs.response.status",
        "http.status",
        "openapi.document",
        "openapi.paths",
    ]:
        raise ValueError(f"required-parameter OpenAPI selectors changed: {selectors}")
    if not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "response"
        and node.func.attr == "json"
        for node in ast.walk(function)
    ):
        raise ValueError(f"expected response.json() assertion in {test_path}::{function_name}")
    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": case_row["recipe_path"],
            "case_id": case_id,
            "action_ids": ["single-openapi-query-parameter"],
            "observation_selectors": selectors,
        },
        "feature_ids": ["openapi-docs", "status-codes"],
        "rationale": (
            "The source asserts status 200 and snapshots the full OpenAPI document; this "
            "independent case maps the endpoint status and focuses the /foo GET parameter list, "
            "where the shared required/optional client_id query declaration is represented once."
        ),
        "contract_gate": (
            "Partial input mapping only: the case compares the OpenAPI endpoint status and selected "
            "parameter-list projection, not the source function's full document snapshot. It "
            "contains no expected output and makes no parity claim; Pydantic owns core field "
            "validation, FastAPI owns parameter aggregation and OpenAPI projection, and generic "
            "ASGI behavior remains under the pinned Starlette 1.6.0 contract."
        ),
    }


def _required_parameter_once_http_function_mapping(
    function_name: str,
    case_id: str,
    action_id: str,
    observation_selectors: list[str],
    rationale: str,
    contract_gate: str,
) -> dict[str, Any]:
    """Link required-dependency HTTP tests to their existing input cases."""
    test_path = "tests/test_enforce_once_required_parameter.py"
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    case_row = _RECIPE_CASE_INDEX.get(case_id)
    recipe_path = (
        "tests/fixtures/input-recipes/parity/dependency-required-parameter-once-upstream.yaml"
    )
    if case_row is None or case_row["recipe_path"] != recipe_path:
        raise ValueError(f"unknown required-parameter HTTP case: {case_id}")
    actions = case_row["case"].get("actions", [])
    if len(actions) != 1 or actions[0].get("action_id") != action_id:
        raise ValueError(f"expected one {action_id} action in {case_id}")
    selectors = _workflow_selectors({"actions": actions})
    if selectors != observation_selectors:
        raise ValueError(f"required-parameter HTTP selectors changed for {case_id}: {selectors}")
    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": recipe_path,
            "case_id": case_id,
            "action_ids": [action_id],
            "observation_selectors": selectors,
        },
        "feature_ids": ["request-validation", "dependency-security"],
        "rationale": rationale,
        "contract_gate": contract_gate,
    }


def _path_test_function_mapping(function_name: str, case_id: str, behavior: str) -> dict[str, Any]:
    """Link one exact Path test assertion to its independent ASGI input case."""
    test_path = "tests/test_path.py"
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    case_row = _RECIPE_CASE_INDEX.get(case_id)
    if (
        case_row is None
        or case_row["recipe_path"]
        != "tests/fixtures/input-recipes/parity/path-boundary-parsed-json.yaml"
    ):
        raise ValueError(f"unknown path test recipe case for {function_name}: {case_id}")
    actions = case_row["case"].get("actions", [])
    if len(actions) != 1 or actions[0].get("action_id") != "dispatch":
        raise ValueError(f"expected one dispatch action in {case_id}")
    selectors = _workflow_selectors({"actions": actions})
    if not {"http.status", "http.body.bytes", "http.body.json"} <= set(selectors):
        raise ValueError(f"path test action lacks parsed JSON observations: {case_id}")
    json_assertions = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "response"
        and node.func.attr == "json"
    ]
    if not json_assertions:
        raise ValueError(f"expected response.json() assertion in {test_path}::{function_name}")
    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": case_row["recipe_path"],
            "case_id": case_id,
            "action_ids": ["dispatch"],
            "observation_selectors": selectors,
        },
        "feature_ids": ["request-validation"],
        "rationale": behavior,
        "contract_gate": (
            "Partial input mapping only: the exact independent path input observes the full parsed "
            "JSON response, matching the source function's response.json() assertion, plus status "
            "and raw bytes. This is not a live parity result; path declaration and error projection "
            "remain FastAPI-owned, Pydantic owns core validation, and route dispatch remains under "
            "the pinned Starlette 1.6.0 contract."
        ),
    }


def _query_list_validation_alias_function_mapping(
    function_name: str,
    case_id: str,
    action_ids: list[str],
    observation_selectors: list[str],
    behavior: str,
    feature_ids: list[str] | None = None,
) -> dict[str, Any]:
    test_path = "tests/test_request_params/test_query/test_list.py"
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _QUERY_LIST_VALIDATION_ALIAS_RECIPE,
            "case_id": case_id,
            "action_ids": list(action_ids),
            "observation_selectors": list(observation_selectors),
        },
        "feature_ids": list(feature_ids or ["request-validation"]),
        "rationale": behavior,
        "contract_gate": (
            "Partial input mapping only: independently named direct-list and Query(BaseModel) "
            "routes exercise validation_alias selection, repeated values, rejected alternate "
            "names, and the route-specific OpenAPI parameter projection. The recipe contains "
            "no expected outputs and makes no live parity claim; complete error-detail parsing, "
            "unlisted constraints, and exact TestClient behavior remain outside this mapping. "
            "Generic query-string parsing remains owned by the separate Starlette 1.6.0 contract."
        ),
    }


def _query_required_list_function_mapping(
    function_name: str,
    case_id: str,
    action_ids: list[str],
    observation_selectors: list[str],
    behavior: str,
    feature_ids: list[str] | None = None,
) -> dict[str, Any]:
    test_path = "tests/test_request_params/test_query/test_list.py"
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _QUERY_REQUIRED_LIST_RECIPE,
            "case_id": case_id,
            "action_ids": list(action_ids),
            "observation_selectors": list(observation_selectors),
        },
        "feature_ids": list(feature_ids or ["request-validation"]),
        "rationale": behavior,
        "contract_gate": (
            "Partial input mapping only: independent direct-list and Query(BaseModel) routes "
            "exercise required query-list schemas, missing values, repeated values, and declared "
            "alias selection. The recipe contains no expected outputs and makes no live parity "
            "claim; complete error detail and unlisted cases remain outside this mapping. "
            "Generic query-string parsing remains owned by the separate Starlette 1.6.0 contract."
        ),
    }


def _query_required_optional_integer_function_mapping(
    function_name: str,
    case_id: str,
    action_id: str,
    observation_selectors: list[str],
    rationale: str,
) -> dict[str, Any]:
    """Join one pinned query test to one exact literal GET action."""
    test_path = "tests/test_query.py"
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exact source function {function_name} in {test_path}")
    function = matches[0]
    calls = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "client"
        and node.func.attr == "get"
    ]
    if len(calls) != 1 or not calls[0].args:
        raise ValueError(f"expected one literal client.get request in {test_path}::{function_name}")
    request = calls[0].args[0]
    if not isinstance(request, ast.Constant) or not isinstance(request.value, str):
        raise ValueError(f"expected literal client.get URL in {test_path}::{function_name}")

    case_row = _RECIPE_CASE_INDEX.get(case_id)
    if case_row is None or case_row["recipe_path"] != _QUERY_REQUIRED_OPTIONAL_INTEGER_RECIPE:
        raise ValueError(
            f"unknown query test recipe case for {test_path}::{function_name}: {case_id}"
        )
    actions = [
        action
        for action in case_row["case"].get("actions", [])
        if action.get("action_id") == action_id
    ]
    case_actions = case_row["case"].get("actions", [])
    if len(actions) != 1 or len(case_actions) != 1:
        raise ValueError(
            f"expected exactly one mapped action {action_id} in query test case {case_id}"
        )
    scope = actions[0].get("scope", {})
    parsed_request = urlsplit(request.value)
    expected_query = scope.get("query_string") or ""
    if (
        actions[0].get("kind") != "http_request"
        or scope.get("method") != "GET"
        or parsed_request.path != scope.get("path")
        or parsed_request.query != expected_query
        or parsed_request.fragment
        or parsed_request.scheme
        or parsed_request.netloc
    ):
        raise ValueError(f"source request does not match {case_id}::{action_id}: {request.value!r}")
    action_observation_selectors = _workflow_selectors(
        {**case_row["case"], "actions": [actions[0]]}
    )
    if not set(observation_selectors) <= set(action_observation_selectors):
        raise ValueError(f"query test selectors are absent from action {case_id}::{action_id}")

    return {
        "source_span": _source(
            test_path,
            function.lineno,
            function.end_lineno or function.lineno,
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _QUERY_REQUIRED_OPTIONAL_INTEGER_RECIPE,
            "case_id": case_id,
            "action_ids": [action_id],
            "observation_selectors": list(observation_selectors),
        },
        "feature_ids": ["request-validation", "status-codes"],
        "rationale": rationale,
        "contract_gate": (
            "Partial input mapping only: the exact literal GET request maps to one independent "
            "recipe action by method, path, and query string. The case contains request stimuli "
            "and the selected HTTP status/body observations, not expected outputs or a parity "
            "result. Only this function's selected response assertions are linked; full parameter "
            "contracts and generic query parsing remain under their respective FastAPI and "
            "Starlette 1.6.0 contracts."
        ),
    }


def _optional_query_list_alias_function_mapping(
    function_name: str,
    case_id: str,
    action_ids: list[str],
    observation_selectors: list[str],
    behavior: str,
) -> dict[str, Any]:
    test_path = "tests/test_request_params/test_query/test_optional_list.py"
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
            f"upstream FastAPI 0.157.0 test function {function_name}",
        ),
        "workflow_case": {
            "recipe_path": _OPTIONAL_QUERY_LIST_ALIAS_RECIPE,
            "case_id": case_id,
            "action_ids": list(action_ids),
            "observation_selectors": list(observation_selectors),
        },
        "rationale": behavior,
        "contract_gate": (
            "Partial input mapping only: independently named optional direct-list and "
            "Query(BaseModel) routes exercise missing or ignored names as well as repeated "
            "values under the selected wire name. OpenAPI cases select both route forms. "
            "The input records requests and observation selectors, not expected status or "
            "body values; alias declaration/extraction belongs to FastAPI while generic "
            "query-string decoding remains owned by Starlette 1.6.0 / Starlette-RS."
        ),
    }


_QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS = ["http.body.bytes", "http.status"]
_QUERY_REQUIRED_OPTIONAL_INTEGER_FUNCTION_ROWS = {
    "test_query": (
        "fastapi.query-required-optional-integer.required-missing",
        "required-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required string query is omitted, exercising its missing-value response.",
    ),
    "test_query_query_baz": (
        "fastapi.query-required-optional-integer.required-value",
        "required-value",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required string query receives the literal value baz.",
    ),
    "test_query_not_declared_baz": (
        "fastapi.query-required-optional-integer.required-unknown-only",
        "required-unknown-only",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "Only an undeclared query key is supplied to the required string route.",
    ),
    "test_query_optional": (
        "fastapi.query-required-optional-integer.optional-missing",
        "optional-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The optional string query is omitted.",
    ),
    "test_query_optional_query_baz": (
        "fastapi.query-required-optional-integer.optional-value",
        "optional-value",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The optional string query receives the literal value baz.",
    ),
    "test_query_optional_not_declared_baz": (
        "fastapi.query-required-optional-integer.optional-unknown-only",
        "optional-unknown-only",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "Only an undeclared query key is supplied to the optional string route.",
    ),
    "test_query_int": (
        "fastapi.query-required-optional-integer.required-integer-missing",
        "required-integer-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required integer query is omitted.",
    ),
    "test_query_int_query_42": (
        "fastapi.query-required-optional-integer.required-integer-valid",
        "required-integer-valid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required integer query receives a valid integer string.",
    ),
    "test_query_int_query_42_5": (
        "fastapi.query-required-optional-integer.required-integer-decimal-invalid",
        "required-integer-decimal-invalid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "A decimal-form query value is submitted to the required integer parameter.",
    ),
    "test_query_int_query_baz": (
        "fastapi.query-required-optional-integer.required-integer-text-invalid",
        "required-integer-text-invalid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "A non-numeric string is submitted to the required integer parameter.",
    ),
    "test_query_int_not_declared_baz": (
        "fastapi.query-required-optional-integer.required-integer-unknown-only",
        "required-integer-unknown-only",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "Only an undeclared query key is supplied to the required integer route.",
    ),
    "test_query_int_optional": (
        "fastapi.query-required-optional-integer.optional-integer-missing",
        "optional-integer-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The optional integer query is omitted.",
    ),
    "test_query_int_optional_query_50": (
        "fastapi.query-required-optional-integer.optional-integer-valid",
        "optional-integer-valid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The optional integer query receives a valid integer string.",
    ),
    "test_query_int_optional_query_foo": (
        "fastapi.query-required-optional-integer.optional-integer-invalid",
        "optional-integer-invalid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "A non-numeric string is submitted to the optional integer parameter.",
    ),
    "test_query_int_default": (
        "fastapi.query-required-optional-integer.default-integer-missing",
        "default-integer-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The defaulted integer query is omitted.",
    ),
    "test_query_int_default_query_50": (
        "fastapi.query-required-optional-integer.default-integer-valid",
        "default-integer-valid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The defaulted integer query receives a valid integer string.",
    ),
    "test_query_int_default_query_foo": (
        "fastapi.query-required-optional-integer.default-integer-invalid",
        "default-integer-invalid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "A non-numeric string is submitted to the defaulted integer parameter.",
    ),
    "test_query_param": (
        "fastapi.query-required-optional-integer.test-query-param.missing",
        "param-optional-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The optional query parameter declared with Query is omitted.",
    ),
    "test_query_param_query_50": (
        "fastapi.query-required-optional-integer.test-query-param.value",
        "param-optional-value",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The optional Query-declared integer receives a valid value.",
    ),
    "test_query_param_required": (
        "fastapi.query-required-optional-integer.test-query-param-required.missing",
        "param-required-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required Query-declared string parameter is omitted.",
    ),
    "test_query_param_required_query_50": (
        "fastapi.query-required-optional-integer.test-query-param-required.value",
        "param-required-value",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required Query-declared string parameter receives a value.",
    ),
    "test_query_param_required_int": (
        "fastapi.query-required-optional-integer.test-query-param-required-int.missing",
        "param-required-int-missing",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required Query-declared integer parameter is omitted.",
    ),
    "test_query_param_required_int_query_50": (
        "fastapi.query-required-optional-integer.test-query-param-required-int.valid",
        "param-required-int-valid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The required Query-declared integer receives a valid value.",
    ),
    "test_query_param_required_int_query_foo": (
        "fastapi.query-required-optional-integer.test-query-param-required-int.invalid",
        "param-required-int-invalid",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "A non-numeric string is submitted to the required Query-declared integer.",
    ),
    "test_query_frozenset_query_1_query_1_query_2": (
        "fastapi.query-required-optional-integer.test-query-frozenset-query-1-query-1-query-2",
        "frozenset-repeated",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "Repeated integer query values are submitted to a frozenset field, including a duplicate.",
    ),
    "test_query_list": (
        "fastapi.query-required-optional-integer.test-query-list.repeated",
        "list-repeated",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "Repeated values are submitted to the required list query parameter.",
    ),
    "test_query_list_empty": (
        "fastapi.query-required-optional-integer.test-query-list.empty",
        "list-empty",
        ["http.status"],
        "The required list query is omitted; the source function observes only response status.",
    ),
    "test_query_list_default": (
        "fastapi.query-required-optional-integer.test-query-list-default.repeated",
        "list-default-repeated",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "Repeated values are submitted to a list query parameter with a default.",
    ),
    "test_query_list_default_empty": (
        "fastapi.query-required-optional-integer.test-query-list-default.empty",
        "list-default-empty",
        _QUERY_REQUIRED_OPTIONAL_INTEGER_RESPONSE_SELECTORS,
        "The defaulted list query is omitted.",
    ),
}


_PARAMETER_REPR_TEST_PATH = "tests/test_params_repr.py"
_PARAMETER_REPR_RECIPE = "tests/fixtures/input-recipes/parity/public-model-edge-cases-upstream.yaml"
_PARAMETER_REPR_CASE_ID = "fastapi.params-repr.representative-default-categories"
_PARAMETER_REPR_INPUT_DESCRIPTIONS = {
    "str": "the exact string literal 'teststr'",
    "none": "None",
    "ellipsis": "ellipsis, normalized by FastAPI to PydanticUndefined",
    "number": "the integer 1",
    "list": "an empty list",
}


def _parameter_repr_function_mappings() -> dict[str, dict[str, Any]]:
    case_row = _RECIPE_CASE_INDEX.get(_PARAMETER_REPR_CASE_ID)
    if case_row is None or case_row["recipe_path"] != _PARAMETER_REPR_RECIPE:
        raise ValueError("parameter repr source functions need their reviewed input case")
    case = case_row["case"]
    source_paths = {
        evidence.get("path")
        for evidence in case.get("source_evidence", [])
        if evidence.get("kind") == "upstream_test"
    }
    if _PARAMETER_REPR_TEST_PATH not in source_paths:
        raise ValueError("parameter repr input case does not cite its pinned source test")
    actions = case.get("actions", [])
    if len(actions) != 1 or actions[0].get("action_id") != "parameter-representations":
        raise ValueError("parameter repr input case must select its single reviewed action")

    function_specs = {
        "test_path_repr": (
            "Path",
            "the default and explicit-ellipsis values asserted by this source function",
        )
    }
    for class_name in ("Query", "Header", "Cookie", "Body"):
        prefix = f"test_{class_name.lower()}_repr_"
        for suffix, input_description in _PARAMETER_REPR_INPUT_DESCRIPTIONS.items():
            function_specs[prefix + suffix] = (class_name, input_description)

    spans = {
        span["role"].rsplit(" ", 1)[-1]: span
        for span in _test_function_spans(_PARAMETER_REPR_TEST_PATH)
    }
    excluded = set(_TOP_LEVEL_REQUEST_PARAMETER_FUNCTION_EXCLUSIONS[_PARAMETER_REPR_TEST_PATH])
    if set(spans) - excluded != set(function_specs):
        raise ValueError("parameter repr mappings do not cover exactly the public test functions")

    selectors = _workflow_selectors(case)
    contract_gate = REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS[_PARAMETER_REPR_TEST_PATH][
        "contract_gate"
    ]
    supporting_sources = [
        _source(
            "fastapi/params.py",
            132,
            133,
            "FastAPI 0.157.0 Param.__repr__ implementation inherited by public parameter classes.",
        )
    ]
    return {
        function_name: {
            "source_span": spans[function_name],
            "supporting_sources": supporting_sources,
            "workflow_case": {
                "recipe_path": _PARAMETER_REPR_RECIPE,
                "case_id": _PARAMETER_REPR_CASE_ID,
                "action_ids": ["parameter-representations"],
                "observation_selectors": selectors,
            },
            "feature_ids": ["public-api-errors"],
            "rationale": (
                f"The independent parameter-representations response includes repr() for "
                f"{class_name} with {input_description}, matching this pinned source function; "
                "the action also observes sibling parameter categories."
            ),
            "contract_gate": contract_gate,
        }
        for function_name, (class_name, input_description) in function_specs.items()
    }


REQUEST_PARAMETER_FUNCTION_MAPPINGS = {
    _PARAMETER_REPR_TEST_PATH: _parameter_repr_function_mappings(),
    _FIELD_OPTIONS_TEST_PATH: {
        "test_union_mode": _field_options_function_mapping(
            "test_union_mode",
            _FIELD_OPTIONS_ACTION_IDS["test_union_mode"],
            ["http.body.bytes", "http.status"],
            "Independent requests cover None, smart, and left_to_right union_mode selections across Path, Query, Header, Cookie, Body, and Form; the valid numeric string distinguishes left_to_right coercion from the two smart-mode outcomes.",
        ),
        "test_fail_fast": _field_options_function_mapping(
            "test_fail_fast",
            _FIELD_OPTIONS_ACTION_IDS["test_fail_fast"],
            ["http.body.bytes", "http.status"],
            "Invalid repeated values exercise fail_fast=True and False for Query, Header, Body, and Form, observing whether validation stops at the first item or reports both.",
        ),
        "test_omitted_options_preserve_pydantic_validation_metadata": _field_options_function_mapping(
            "test_omitted_options_preserve_pydantic_validation_metadata",
            _FIELD_OPTIONS_ACTION_IDS["test_omitted_options_preserve_pydantic_validation_metadata"],
            ["http.body.bytes", "http.status"],
            "The independent route leaves Query.union_mode and Body.fail_fast unset while Field metadata supplies left_to_right and fail_fast=True; valid and invalid bodies expose the preserved metadata behavior.",
        ),
        "test_explicit_options_override_pydantic_validation_metadata": _field_options_function_mapping(
            "test_explicit_options_override_pydantic_validation_metadata",
            _FIELD_OPTIONS_ACTION_IDS[
                "test_explicit_options_override_pydantic_validation_metadata"
            ],
            ["http.body.bytes", "http.status"],
            "The independent route combines Field metadata with explicit Query.union_mode='smart' and Body.fail_fast=False, then sends valid and invalid inputs to observe the option overrides.",
        ),
        "test_compiled_pattern": _field_options_function_mapping(
            "test_compiled_pattern",
            _FIELD_OPTIONS_ACTION_IDS["test_compiled_pattern"],
            ["http.body.bytes", "http.status"],
            "Case-insensitive compiled patterns are exercised with one matching and one non-matching value at each Path, Query, Header, Cookie, Body, and Form location.",
        ),
        "test_file_list_fail_fast": _field_options_function_mapping(
            "test_file_list_fail_fast",
            _FIELD_OPTIONS_ACTION_IDS["test_file_list_fail_fast"],
            ["http.body.bytes", "http.status"],
            "Multipart inputs compare invalid list items under File(fail_fast=True/False) and include a valid upload. Multipart framing and UploadFile parsing remain Starlette-owned.",
        ),
        "test_query_options": _field_options_function_mapping(
            "test_query_options",
            _FIELD_OPTIONS_ACTION_IDS["test_query_options"],
            ["http.body.bytes", "http.status"],
            "The independent /query request supplies a union value and repeated list values while defaulted fields exercise validate_default and a compiled pattern.",
        ),
        "test_body_options": _field_options_function_mapping(
            "test_body_options",
            _FIELD_OPTIONS_ACTION_IDS["test_body_options"],
            ["http.body.bytes", "http.status"],
            "The independent /body request supplies a list and union value while the defaulted body field exercises validate_default.",
        ),
        "test_openapi_schema": _field_options_function_mapping(
            "test_openapi_schema",
            _FIELD_OPTIONS_ACTION_IDS["test_openapi_schema"],
            ["docs.response.status", "openapi.document", "openapi.paths"],
            "The OpenAPI action selects the /query parameter list and /body requestBody projection, covering the field options' route-level schema output without claiming the source's full-document snapshot.",
            ["openapi-docs"],
        ),
    },
    "tests/test_request_params/test_file/test_nullable_and_defaults.py": {
        "test_missing_required_nullable_files": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_file/test_nullable_and_defaults.py",
            "test_missing_required_nullable_files",
            "file",
            ["file-required-omitted", "file-required-empty-selection"],
            ["http.body.bytes", "http.status"],
            "The required nullable File declaration is sent once without multipart input and once with empty-filename browser parts, mapping missing-field handling for bytes and bytes-list fields.",
        ),
        "test_named_file_is_supplied_even_when_empty": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_file/test_nullable_and_defaults.py",
            "test_named_file_is_supplied_even_when_empty",
            "file",
            ["file-named-empty"],
            ["http.body.bytes", "http.status"],
            "Named multipart file parts with empty content exercise the source distinction between a selected empty file and a no-selection part.",
        ),
        "test_missing_files_use_bytes_defaults": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_file/test_nullable_and_defaults.py",
            "test_missing_files_use_bytes_defaults",
            "file",
            ["file-defaults-omitted"],
            ["http.body.bytes", "http.status"],
            "The independent missing-body request exercises File parameter defaults and a default factory for a bytes list.",
        ),
        "test_individual_file_alias_choices": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_file/test_nullable_and_defaults.py",
            "test_individual_file_alias_choices",
            "file",
            ["file-alias-choice"],
            ["http.body.bytes", "http.status"],
            "The multipart field name uses the first accepted AliasChoices value while File.alias names a different field.",
        ),
        "test_openapi_schema": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_file/test_nullable_and_defaults.py",
            "test_openapi_schema",
            "file",
            ["file-openapi"],
            ["docs.response.status", "openapi.document", "openapi.paths"],
            "The OpenAPI action selects requestBody declarations for required, optional, and aliased file routes instead of the source's complete schema snapshot.",
            ["openapi-docs"],
        ),
    },
    "tests/test_request_params/test_form/test_nullable_and_defaults.py": {
        "test_empty_integer_uses_default": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_form/test_nullable_and_defaults.py",
            "test_empty_integer_uses_default",
            "form",
            ["form-empty-default"],
            ["http.body.bytes", "http.status"],
            "An empty URL-encoded integer field exercises FastAPI's Form empty-value handling for a parameter with a non-null default.",
        ),
        "test_empty_required_integer_is_missing": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_form/test_nullable_and_defaults.py",
            "test_empty_required_integer_is_missing",
            "form",
            ["form-empty-required"],
            ["http.body.bytes", "http.status"],
            "An empty URL-encoded field is supplied to a required integer Form parameter and observes its validation response.",
        ),
        "test_checkbox_with_true_default": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_form/test_nullable_and_defaults.py",
            "test_checkbox_with_true_default",
            "form",
            ["form-checkbox-default"],
            ["http.body.bytes", "http.status"],
            "The omitted checkbox request exercises a direct Form boolean whose declared default is true.",
        ),
    },
    "tests/test_request_params/test_header/test_nullable_and_defaults.py": {
        "test_nullable_header_uses_hyphenated_name": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_header/test_nullable_and_defaults.py",
            "test_nullable_header_uses_hyphenated_name",
            "header",
            ["header-nullable", "header-openapi"],
            [
                "http.body.bytes",
                "http.status",
                "docs.response.status",
                "openapi.document",
                "openapi.paths",
            ],
            "The value and OpenAPI projections exercise FastAPI's underscore-to-hyphen name for an annotated nullable header parameter.",
        ),
        "test_nullable_header_error_uses_hyphenated_name": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_header/test_nullable_and_defaults.py",
            "test_nullable_header_error_uses_hyphenated_name",
            "header",
            ["header-missing"],
            ["http.body.bytes", "http.status"],
            "The missing nullable Header-model input observes the header-prefixed validation location for the converted wire name.",
        ),
        "test_header_model_list_error_preserves_item_index": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_header/test_nullable_and_defaults.py",
            "test_header_model_list_error_preserves_item_index",
            "header",
            ["header-list-error"],
            ["http.body.bytes", "http.status"],
            "Repeated item-ids headers include one invalid second value, exercising the indexed Header-model validation location.",
        ),
    },
    "tests/test_request_params/test_nullable_and_defaults.py": {
        "test_nullable_required_schema_and_supplied_value": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_nullable_and_defaults.py",
            "test_nullable_required_schema_and_supplied_value",
            "locations",
            [
                "request-query-supplied",
                "request-cookie-supplied",
                "request-header-supplied",
                "request-form-supplied",
                "request-body-supplied",
                "request-openapi",
            ],
            [
                "http.body.bytes",
                "http.status",
                "docs.response.status",
                "openapi.document",
                "openapi.paths",
            ],
            "Independent Query, Cookie, Header, Form, and Body declarations accept a supplied zero and expose their selected OpenAPI parameter/requestBody projections.",
        ),
        "test_nullable_scalar_is_required": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_nullable_and_defaults.py",
            "test_nullable_scalar_is_required",
            "locations",
            [
                "request-query-supplied",
                "request-query-missing",
                "request-cookie-supplied",
                "request-cookie-missing",
                "request-header-supplied",
                "request-header-missing",
                "request-form-supplied",
                "request-form-missing",
                "request-body-supplied",
                "request-body-missing",
            ],
            ["http.body.bytes", "http.status"],
            "Nullable scalar parameters are exercised both with a supplied zero and with the source omitted across Query, Cookie, Header, Form, and embedded Body locations.",
        ),
        "test_missing_value_uses_default": _nullable_defaults_function_mapping(
            "tests/test_request_params/test_nullable_and_defaults.py",
            "test_missing_value_uses_default",
            "locations",
            ["request-query-default-missing", "request-body-default-missing"],
            ["http.body.bytes", "http.status"],
            "Omitted query and embedded-body values exercise direct parameter defaults; the mapping selects representative source locations only.",
        ),
    },
    "tests/test_enforce_once_required_parameter.py": {
        "test_get_invalid": _required_parameter_once_http_function_mapping(
            "test_get_invalid",
            "fastapi.dependencies.required-parameter-once.missing",
            "missing-shared-required-query",
            ["http.status"],
            "Omitting client_id leaves the shared required dependency parameter missing and returns the independently observed 422 status.",
            "Partial input mapping: this case observes the validation status only. It does not compare the source error document or assert exact TestClient URL encoding; generic ASGI behavior remains in the pinned Starlette 1.6.0 contract.",
        ),
        "test_get_valid": _required_parameter_once_http_function_mapping(
            "test_get_valid",
            "fastapi.dependencies.required-parameter-once.valid",
            "one-value-feeds-required-and-optional-dependencies",
            ["http.body.bytes", "http.status"],
            "One query value satisfies the required and optional dependency parameters, and the independent endpoint returns its derived values.",
            "Partial input mapping: the case observes status and raw response bytes for independent route and value literals. It maps the valid shared-dependency path without claiming the source body literals or TestClient encoding.",
        ),
        "test_openapi_schema": _required_parameter_once_openapi_function_mapping(),
    },
    "tests/test_path.py": {
        "test_path_param_le_ge_int_1": _path_test_function_mapping(
            "test_path_param_le_ge_int_1",
            "fastapi.path-boundary.source-json-001",
            "The inclusive lower endpoint of Path(ge=1, le=3) is accepted.",
        ),
        "test_path_param_le_ge_int_3": _path_test_function_mapping(
            "test_path_param_le_ge_int_3",
            "fastapi.path-boundary.source-json-002",
            "The inclusive upper endpoint of Path(ge=1, le=3) is accepted.",
        ),
        "test_path_param_maxlength_foobar": _path_test_function_mapping(
            "test_path_param_maxlength_foobar",
            "fastapi.path-boundary.source-json-003",
            "Path(max_length=3) rejects an overlong path value with its validation response.",
        ),
        "test_path_param_min_maxlength_f": _path_test_function_mapping(
            "test_path_param_min_maxlength_f",
            "fastapi.path-boundary.source-json-004",
            "Combined minimum and maximum string bounds reject a value below the minimum.",
        ),
        "test_path_param_min_maxlength_foo": _path_test_function_mapping(
            "test_path_param_min_maxlength_foo",
            "fastapi.path-boundary.source-json-005",
            "Combined minimum and maximum string bounds accept the value at the maximum.",
        ),
        "test_path_param_min_maxlength_foobar": _path_test_function_mapping(
            "test_path_param_min_maxlength_foobar",
            "fastapi.path-boundary.source-json-006",
            "Combined minimum and maximum string bounds reject an overlong value.",
        ),
        "test_path_param_lt_int_2": _path_test_function_mapping(
            "test_path_param_lt_int_2",
            "fastapi.path-boundary.source-json-007",
            "Path(lt=3) accepts an integer below its exclusive upper bound.",
        ),
        "test_path_param_lt_int_42": _path_test_function_mapping(
            "test_path_param_lt_int_42",
            "fastapi.path-boundary.source-json-008",
            "Path(lt=3) rejects an integer above its exclusive upper bound.",
        ),
        "test_path_param_lt_gt_int_4": _path_test_function_mapping(
            "test_path_param_lt_gt_int_4",
            "fastapi.path-boundary.source-json-009",
            "Path(gt=1, lt=3) rejects a value above the exclusive upper bound.",
        ),
        "test_path_param_lt_gt_int_0": _path_test_function_mapping(
            "test_path_param_lt_gt_int_0",
            "fastapi.path-boundary.source-json-010",
            "Path(gt=1, lt=3) rejects a value below the exclusive lower bound.",
        ),
    },
    "tests/test_request_params/test_header/test_required_str.py": (
        _header_cookie_alias_module_mappings("header", "Header")
    ),
    "tests/test_request_params/test_cookie/test_required_str.py": (
        _header_cookie_alias_module_mappings("cookie", "Cookie")
    ),
    "tests/test_file_and_form_order_issue_9116.py": {
        "test_file_list_form_order": _request_http_function_mapping(
            "tests/test_file_and_form_order_issue_9116.py",
            "test_file_list_form_order",
            _FILE_LIST_FORM_ORDER_CASE,
            ["files-before-label", "label-before-files"],
            (
                "The independent multipart case declares repeated byte-file fields and one scalar "
                "form field in both parameter orders, then submits the same request stimulus to "
                "each route. It samples the source function's status/body observations without "
                "reusing its file contents, form value, or response assertion."
            ),
        ),
    },
    "tests/test_request_params/test_query/test_list.py": {
        "test_required_list_str_schema": _query_required_list_function_mapping(
            "test_required_list_str_schema",
            "fastapi.request-parameters.query.required-list.plain",
            ["inspect-openapi"],
            ["openapi.document", "openapi.paths"],
            "The OpenAPI case projects the required list parameter from independent direct and Query(BaseModel) routes.",
        ),
        "test_required_list_str_missing": _query_required_list_function_mapping(
            "test_required_list_str_missing",
            "fastapi.request-parameters.query.required-list.plain",
            ["plain-direct-missing", "plain-model-missing"],
            ["http.body.bytes", "http.status"],
            "The two missing-value requests exercise required list extraction on direct and Query(BaseModel) routes.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_str": _query_required_list_function_mapping(
            "test_required_list_str",
            "fastapi.request-parameters.query.required-list.plain",
            ["plain-direct-repeated", "plain-model-repeated"],
            ["http.body.bytes", "http.status"],
            "The two requests submit repeated values to independent direct and Query(BaseModel) list routes.",
        ),
        "test_required_list_str_alias_schema": _query_required_list_function_mapping(
            "test_required_list_str_alias_schema",
            "fastapi.request-parameters.query.required-list.declared-alias",
            ["inspect-openapi"],
            ["openapi.document", "openapi.paths"],
            "The OpenAPI case projects a declared query alias from independent direct and Query(BaseModel) routes.",
        ),
        "test_required_list_alias_missing": _query_required_list_function_mapping(
            "test_required_list_alias_missing",
            "fastapi.request-parameters.query.required-list.declared-alias",
            ["alias-direct-missing", "alias-model-missing"],
            ["http.body.bytes", "http.status"],
            "The two requests omit the required declared alias on direct and Query(BaseModel) routes.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_alias_by_name": _query_required_list_function_mapping(
            "test_required_list_alias_by_name",
            "fastapi.request-parameters.query.required-list.declared-alias",
            ["alias-direct-field-name", "alias-model-field-name"],
            ["http.body.bytes", "http.status"],
            "The two requests supply the Python field name while the independent routes declare a different wire alias.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_alias_by_alias": _query_required_list_function_mapping(
            "test_required_list_alias_by_alias",
            "fastapi.request-parameters.query.required-list.declared-alias",
            ["alias-direct-wire-name", "alias-model-wire-name"],
            ["http.body.bytes", "http.status"],
            "The two requests supply repeated values under the declared wire alias on both route forms.",
        ),
        "test_required_list_validation_alias_schema": _query_list_validation_alias_function_mapping(
            "test_required_list_validation_alias_schema",
            "fastapi.request-parameters.query.validation-alias-list.validation-only.openapi",
            ["openapi-validation-only-parameters"],
            ["openapi.document", "openapi.paths"],
            "The OpenAPI case projects validation-alias-selected query parameter schemas for both direct list and Query(BaseModel) routes.",
        ),
        "test_required_list_validation_alias_missing": _query_list_validation_alias_function_mapping(
            "test_required_list_validation_alias_missing",
            "fastapi.request-parameters.query.validation-alias-list.validation-only.missing",
            ["direct-missing", "model-missing"],
            ["http.body.bytes", "http.status"],
            "The input case omits the required validation-alias list from both direct and model-valued routes.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_validation_alias_by_name": _query_list_validation_alias_function_mapping(
            "test_required_list_validation_alias_by_name",
            "fastapi.request-parameters.query.validation-alias-list.validation-only.rejects-field-name",
            ["direct-field-name", "model-field-name"],
            ["http.body.bytes", "http.status"],
            "The input case supplies repeated values under the Python field name instead of the required validation alias.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_validation_alias_by_validation_alias": _query_list_validation_alias_function_mapping(
            "test_required_list_validation_alias_by_validation_alias",
            "fastapi.request-parameters.query.validation-alias-list.validation-only.accepts-wire-name",
            ["direct-wire-name", "model-wire-name"],
            ["http.body.bytes", "http.status"],
            "The input case supplies repeated values under the validation alias for both route forms.",
        ),
        "test_required_list_alias_and_validation_alias_schema": _query_list_validation_alias_function_mapping(
            "test_required_list_alias_and_validation_alias_schema",
            "fastapi.request-parameters.query.validation-alias-list.both-aliases.openapi",
            ["openapi-both-aliases-parameters"],
            ["openapi.document", "openapi.paths"],
            "The OpenAPI case compares validation-alias-selected parameters when a separate declared alias is also present.",
        ),
        "test_required_list_alias_and_validation_alias_missing": _query_list_validation_alias_function_mapping(
            "test_required_list_alias_and_validation_alias_missing",
            "fastapi.request-parameters.query.validation-alias-list.both-aliases.missing",
            ["direct-missing", "model-missing"],
            ["http.body.bytes", "http.status"],
            "The input case omits the required wire value when both declared alias and validation alias are present.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_alias_and_validation_alias_by_name": _query_list_validation_alias_function_mapping(
            "test_required_list_alias_and_validation_alias_by_name",
            "fastapi.request-parameters.query.validation-alias-list.both-aliases.rejects-field-name",
            ["direct-field-name", "model-field-name"],
            ["http.body.bytes", "http.status"],
            "The input case uses the Python field name and distinguishes it from both declared aliases.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_alias_and_validation_alias_by_alias": _query_list_validation_alias_function_mapping(
            "test_required_list_alias_and_validation_alias_by_alias",
            "fastapi.request-parameters.query.validation-alias-list.both-aliases.rejects-declared-alias",
            ["direct-declared-alias", "model-declared-alias"],
            ["http.body.bytes", "http.status"],
            "The input case uses the declared alias, which differs from the accepted validation alias.",
            ["request-validation", "status-codes"],
        ),
        "test_required_list_alias_and_validation_alias_by_validation_alias": _query_list_validation_alias_function_mapping(
            "test_required_list_alias_and_validation_alias_by_validation_alias",
            "fastapi.request-parameters.query.validation-alias-list.both-aliases.accepts-validation-alias",
            ["direct-wire-name", "model-wire-name"],
            ["http.body.bytes", "http.status"],
            "The input case uses repeated validation-alias values while both aliases are declared.",
        ),
    },
    "tests/test_request_params/test_query/test_optional_list.py": {
        "test_optional_list_str_alias_schema": _optional_query_list_alias_function_mapping(
            "test_optional_list_str_alias_schema",
            "fastapi.request-parameters.query.optional-list.alias.openapi",
            ["inspect-openapi"],
            ["openapi.document", "openapi.paths"],
            "The schema source function parametrizes direct and Query(BaseModel) routes; the selected OpenAPI pointers project both alias-only parameter lists.",
        ),
        "test_optional_list_alias_missing": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_missing",
            "fastapi.request-parameters.query.optional-list.alias.missing",
            ["direct-missing", "model-missing"],
            ["http.body.bytes", "http.status"],
            "The optional alias case omits the wire key from both route forms.",
        ),
        "test_optional_list_alias_by_name": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_by_name",
            "fastapi.request-parameters.query.optional-list.alias.field-name",
            ["direct-field-name", "model-field-name"],
            ["http.body.bytes", "http.status"],
            "The optional alias case supplies repeated values under the Python field name on both route forms.",
        ),
        "test_optional_list_alias_by_alias": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_by_alias",
            "fastapi.request-parameters.query.optional-list.alias.accepts-wire-name",
            ["direct-declared-alias", "model-declared-alias"],
            ["http.body.bytes", "http.status"],
            "The optional alias case supplies repeated values under the declared alias on both route forms.",
        ),
        "test_optional_list_validation_alias_schema": _optional_query_list_alias_function_mapping(
            "test_optional_list_validation_alias_schema",
            "fastapi.request-parameters.query.optional-list.validation-alias.openapi",
            ["inspect-openapi"],
            ["openapi.document", "openapi.paths"],
            "The schema source function parametrizes direct and Query(BaseModel) routes; the selected OpenAPI pointers project both validation-alias-only parameter lists.",
        ),
        "test_optional_list_validation_alias_missing": _optional_query_list_alias_function_mapping(
            "test_optional_list_validation_alias_missing",
            "fastapi.request-parameters.query.optional-list.validation-alias.missing",
            ["direct-missing", "model-missing"],
            ["http.body.bytes", "http.status"],
            "The optional validation-alias case omits the selected wire key from both route forms.",
        ),
        "test_optional_list_validation_alias_by_name": _optional_query_list_alias_function_mapping(
            "test_optional_list_validation_alias_by_name",
            "fastapi.request-parameters.query.optional-list.validation-alias.field-name",
            ["direct-field-name", "model-field-name"],
            ["http.body.bytes", "http.status"],
            "The optional validation-alias case supplies repeated values under the Python field name on both route forms.",
        ),
        "test_optional_list_validation_alias_by_validation_alias": _optional_query_list_alias_function_mapping(
            "test_optional_list_validation_alias_by_validation_alias",
            "fastapi.request-parameters.query.optional-list.validation-alias.accepts-wire-name",
            ["direct-validation-alias", "model-validation-alias"],
            ["http.body.bytes", "http.status"],
            "The optional validation-alias case supplies repeated values under the validation alias on both route forms.",
        ),
        "test_optional_list_alias_and_validation_alias_schema": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_and_validation_alias_schema",
            "fastapi.request-parameters.query.optional-list.combined-aliases.openapi",
            ["inspect-openapi"],
            ["openapi.document", "openapi.paths"],
            "The schema source function parametrizes direct and Query(BaseModel) routes; the selected OpenAPI pointers project both parameter lists with both aliases configured.",
        ),
        "test_optional_list_alias_and_validation_alias_missing": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_and_validation_alias_missing",
            "fastapi.request-parameters.query.optional-list.combined-aliases.missing",
            ["direct-missing", "model-missing"],
            ["http.body.bytes", "http.status"],
            "The optional combined-alias case omits the selected wire key from both route forms.",
        ),
        "test_optional_list_alias_and_validation_alias_by_name": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_and_validation_alias_by_name",
            "fastapi.request-parameters.query.optional-list.combined-aliases.field-name",
            ["direct-field-name", "model-field-name"],
            ["http.body.bytes", "http.status"],
            "The optional combined-alias case supplies repeated values under the Python field name on both route forms.",
        ),
        "test_optional_list_alias_and_validation_alias_by_alias": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_and_validation_alias_by_alias",
            "fastapi.request-parameters.query.optional-list.combined-aliases.declared-alias",
            ["direct-declared-alias", "model-declared-alias"],
            ["http.body.bytes", "http.status"],
            "The optional combined-alias case supplies repeated values under alias even though validation_alias selects the other wire key.",
        ),
        "test_optional_list_alias_and_validation_alias_by_validation_alias": _optional_query_list_alias_function_mapping(
            "test_optional_list_alias_and_validation_alias_by_validation_alias",
            "fastapi.request-parameters.query.optional-list.combined-aliases.validation-alias",
            ["direct-validation-alias", "model-validation-alias"],
            ["http.body.bytes", "http.status"],
            "The optional combined-alias case supplies repeated values under validation_alias on both route forms.",
        ),
    },
    "tests/test_query.py": {
        function_name: _query_required_optional_integer_function_mapping(
            function_name, case_id, action_id, selectors, rationale
        )
        for function_name, (case_id, action_id, selectors, rationale) in (
            _QUERY_REQUIRED_OPTIONAL_INTEGER_FUNCTION_ROWS.items()
        )
    },
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
    "tests/test_request_params/test_body/test_optional_str.py": {
        "test_optional_str_schema": _optional_body_str_function_mapping(
            "test_optional_str_schema",
            "fastapi.request-body.optional-str-openapi.no-alias",
            ["inspect-openapi"],
            ["openapi.document"],
            "The pinned schema assertion checks direct optional Body and BaseModel routes without aliases; the selected projections isolate both request-body schema references and component properties.",
        ),
        "test_optional_str_alias_schema": _optional_body_str_function_mapping(
            "test_optional_str_alias_schema",
            "fastapi.request-body.optional-str-openapi.alias",
            ["inspect-openapi"],
            ["openapi.document"],
            "The pinned schema assertion checks the declared alias on both direct Body and BaseModel routes.",
        ),
        "test_optional_alias_missing": _optional_body_str_function_mapping(
            "test_optional_alias_missing",
            "fastapi.request-body.optional-str-runtime.alias",
            ["alias-missing-direct"],
            ["http.status", "http.body.bytes"],
            "The direct optional Body route is sent without a request body while a field alias is configured.",
        ),
        "test_model_optional_alias_missing": _optional_body_str_function_mapping(
            "test_model_optional_alias_missing",
            "fastapi.request-body.optional-str-runtime.alias",
            ["alias-missing-model"],
            ["http.status", "http.body.bytes"],
            "The BaseModel request-body route is sent without a request body while a field alias is configured.",
        ),
        "test_model_optional_alias_missing_empty_dict": _optional_body_str_function_mapping(
            "test_model_optional_alias_missing_empty_dict",
            "fastapi.request-body.optional-str-runtime.alias",
            ["alias-empty-object-direct", "alias-empty-object-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test sends an empty JSON object to both direct Body and BaseModel routes with a field alias.",
        ),
        "test_optional_alias_by_name": _optional_body_str_function_mapping(
            "test_optional_alias_by_name",
            "fastapi.request-body.optional-str-runtime.alias",
            ["alias-by-name-direct", "alias-by-name-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits the Python field name on both routes although the declared alias supplies the wire name.",
        ),
        "test_optional_alias_by_alias": _optional_body_str_function_mapping(
            "test_optional_alias_by_alias",
            "fastapi.request-body.optional-str-runtime.alias",
            ["alias-by-alias-direct", "alias-by-alias-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits the declared alias on both route forms.",
        ),
        "test_optional_validation_alias_schema": _optional_body_str_function_mapping(
            "test_optional_validation_alias_schema",
            "fastapi.request-body.optional-str-openapi.validation-alias",
            ["inspect-openapi"],
            ["openapi.document"],
            "The pinned schema assertion checks validation_alias-only projection on both direct Body and BaseModel routes.",
        ),
        "test_optional_validation_alias_missing": _optional_body_str_function_mapping(
            "test_optional_validation_alias_missing",
            "fastapi.request-body.optional-str-runtime.validation-alias",
            ["validation-alias-missing-direct"],
            ["http.status", "http.body.bytes"],
            "The direct optional Body route is sent without a request body while validation_alias is configured.",
        ),
        "test_model_optional_validation_alias_missing": _optional_body_str_function_mapping(
            "test_model_optional_validation_alias_missing",
            "fastapi.request-body.optional-str-runtime.validation-alias",
            ["validation-alias-missing-model"],
            ["http.status", "http.body.bytes"],
            "The BaseModel request-body route is sent without a request body while validation_alias is configured.",
        ),
        "test_model_optional_validation_alias_missing_empty_dict": _optional_body_str_function_mapping(
            "test_model_optional_validation_alias_missing_empty_dict",
            "fastapi.request-body.optional-str-runtime.validation-alias",
            ["validation-alias-empty-object-direct", "validation-alias-empty-object-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test sends an empty JSON object to both route forms with validation_alias configured.",
        ),
        "test_optional_validation_alias_by_name": _optional_body_str_function_mapping(
            "test_optional_validation_alias_by_name",
            "fastapi.request-body.optional-str-runtime.validation-alias",
            ["validation-alias-by-name-direct", "validation-alias-by-name-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits the Python field name on both routes while validation_alias selects another wire name.",
        ),
        "test_optional_validation_alias_by_validation_alias": _optional_body_str_function_mapping(
            "test_optional_validation_alias_by_validation_alias",
            "fastapi.request-body.optional-str-runtime.validation-alias",
            [
                "validation-alias-by-validation-alias-direct",
                "validation-alias-by-validation-alias-model",
            ],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits the validation alias on both route forms.",
        ),
        "test_optional_alias_and_validation_alias_schema": _optional_body_str_function_mapping(
            "test_optional_alias_and_validation_alias_schema",
            "fastapi.request-body.optional-str-openapi.both-aliases",
            ["inspect-openapi"],
            ["openapi.document"],
            "The pinned schema assertion checks property naming when alias and validation_alias are both declared on both route forms.",
        ),
        "test_optional_alias_and_validation_alias_missing": _optional_body_str_function_mapping(
            "test_optional_alias_and_validation_alias_missing",
            "fastapi.request-body.optional-str-runtime.both-aliases",
            ["both-aliases-missing-direct"],
            ["http.status", "http.body.bytes"],
            "The direct optional Body route is sent without a request body while both aliases are configured.",
        ),
        "test_model_optional_alias_and_validation_alias_missing": _optional_body_str_function_mapping(
            "test_model_optional_alias_and_validation_alias_missing",
            "fastapi.request-body.optional-str-runtime.both-aliases",
            ["both-aliases-missing-model"],
            ["http.status", "http.body.bytes"],
            "The BaseModel request-body route is sent without a request body while both aliases are configured.",
        ),
        "test_model_optional_alias_and_validation_alias_missing_empty_dict": _optional_body_str_function_mapping(
            "test_model_optional_alias_and_validation_alias_missing_empty_dict",
            "fastapi.request-body.optional-str-runtime.both-aliases",
            ["both-aliases-empty-object-direct", "both-aliases-empty-object-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test sends an empty JSON object to both route forms with both aliases configured.",
        ),
        "test_optional_alias_and_validation_alias_by_name": _optional_body_str_function_mapping(
            "test_optional_alias_and_validation_alias_by_name",
            "fastapi.request-body.optional-str-runtime.both-aliases",
            ["both-aliases-by-name-direct", "both-aliases-by-name-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits the Python field name on both routes while both aliases are configured.",
        ),
        "test_optional_alias_and_validation_alias_by_alias": _optional_body_str_function_mapping(
            "test_optional_alias_and_validation_alias_by_alias",
            "fastapi.request-body.optional-str-runtime.both-aliases",
            ["both-aliases-by-alias-direct", "both-aliases-by-alias-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits the declared alias although validation_alias supplies the selected input name.",
        ),
        "test_optional_alias_and_validation_alias_by_validation_alias": _optional_body_str_function_mapping(
            "test_optional_alias_and_validation_alias_by_validation_alias",
            "fastapi.request-body.optional-str-runtime.both-aliases",
            ["both-aliases-by-validation-alias-direct", "both-aliases-by-validation-alias-model"],
            ["http.status", "http.body.bytes"],
            "The pinned parameterized test submits validation_alias on both route forms while both aliases are configured.",
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
        _workflow_case = {
            "recipe_path": _recipe_path,
            "case_id": _case_id,
            "action_ids": sorted(_group["action_ids"]),
            "observation_selectors": sorted(_group["selectors"]),
        }
        if _workflow_case not in _entry["workflow_cases"]:
            _entry["workflow_cases"].append(_workflow_case)
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
        expected_function_exclusions = _TOP_LEVEL_REQUEST_PARAMETER_FUNCTION_EXCLUSIONS.get(
            test_path, {}
        )
        actual_function_exclusions = {
            item.get("name"): item.get("reason")
            for item in mapping.get("excluded_test_functions", [])
        }
        if actual_function_exclusions != expected_function_exclusions:
            errors.append(f"test-function exclusions do not match reviewed reasons: {test_path}")
        source_spans = {
            span["role"].rsplit(" ", 1)[-1]: span for span in _test_function_spans(test_path)
        }
        for item in mapping.get("excluded_test_functions", []):
            if (
                not item.get("name")
                or not item.get("reason")
                or item.get("source_span") != source_spans.get(item.get("name"))
            ):
                errors.append(f"invalid test-function exclusion source in {test_path}: {item}")
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
    tail_case_ids = [case.get("case_id") for case in tail_cases]
    if len(tail_case_ids) != len(_TAIL_WAVE_CASES) or set(tail_case_ids) != _TAIL_WAVE_CASES:
        errors.append("tail alias recipe does not contain its five exact reviewed cases")
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
    optional_query_list_path = PROJECT_ROOT / _OPTIONAL_QUERY_LIST_ALIAS_RECIPE
    optional_query_list = yaml.safe_load(optional_query_list_path.read_text(encoding="utf-8"))
    optional_query_list_cases = {
        case.get("case_id"): case for case in optional_query_list.get("cases", [])
    }
    if set(optional_query_list_cases) != _OPTIONAL_QUERY_LIST_ALIAS_CASES:
        errors.append(
            "optional query-list alias recipe does not contain its thirteen reviewed cases"
        )
    query_required_list_path = PROJECT_ROOT / _QUERY_REQUIRED_LIST_RECIPE
    query_required_list = yaml.safe_load(query_required_list_path.read_text(encoding="utf-8"))
    query_required_list_cases = {
        case.get("case_id"): case for case in query_required_list.get("cases", [])
    }
    if set(query_required_list_cases) != _QUERY_REQUIRED_LIST_CASES:
        errors.append("required query-list recipe does not contain its two reviewed cases")
    all_query_list_cases = {**optional_query_list_cases, **query_required_list_cases}
    expected_openapi_pointers = {
        "fastapi.request-parameters.query.optional-list.alias.openapi": {
            "/paths/~1optional-alias~1direct/get/parameters",
            "/paths/~1optional-alias~1model/get/parameters",
        },
        "fastapi.request-parameters.query.optional-list.validation-alias.openapi": {
            "/paths/~1optional-validation-alias~1direct/get/parameters",
            "/paths/~1optional-validation-alias~1model/get/parameters",
        },
        "fastapi.request-parameters.query.optional-list.combined-aliases.openapi": {
            "/paths/~1optional-combined-alias~1direct/get/parameters",
            "/paths/~1optional-combined-alias~1model/get/parameters",
        },
        "fastapi.request-parameters.query.required-list.plain": {
            "/paths/~1catalog~1direct/get/parameters",
            "/paths/~1catalog~1model/get/parameters",
        },
        "fastapi.request-parameters.query.required-list.declared-alias": {
            "/paths/~1labels~1direct/get/parameters",
            "/paths/~1labels~1model/get/parameters",
        },
    }
    for case_id, expected_pointers in expected_openapi_pointers.items():
        case = all_query_list_cases.get(case_id, {})
        action = next(
            (
                action
                for action in case.get("actions", [])
                if action.get("action_id") == "inspect-openapi"
            ),
            {},
        )
        observations = [
            observation
            for observation in action.get("observations", [])
            if observation.get("kind") == "openapi"
        ]
        pointers = {
            pointer
            for observation in observations
            for pointer in observation.get("json_pointers", [])
        }
        if len(observations) != 1 or pointers != expected_pointers:
            errors.append(
                f"optional query-list OpenAPI selectors do not cover both routes for {case_id}"
            )
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
    scan_input_only(
        optional_query_list,
        str(optional_query_list_path.relative_to(PROJECT_ROOT)),
    )
    scan_input_only(
        query_required_list,
        str(query_required_list_path.relative_to(PROJECT_ROOT)),
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
    if not (PROJECT_ROOT / _OPTIONAL_QUERY_LIST_ALIAS_WORKLOAD).is_file():
        errors.append("optional query-list alias workload file is missing")
    if optional_query_list.get("workload", {}).get("file") != _OPTIONAL_QUERY_LIST_ALIAS_WORKLOAD:
        errors.append("optional query-list alias recipe references a different reviewed workload")
    if not (PROJECT_ROOT / _QUERY_REQUIRED_LIST_WORKLOAD).is_file():
        errors.append("required query-list workload file is missing")
    if query_required_list.get("workload", {}).get("file") != _QUERY_REQUIRED_LIST_WORKLOAD:
        errors.append("required query-list recipe references a different reviewed workload")
    referenced_tail_cases = {
        row["workflow_case"]["case_id"]
        for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
        for row in rows.values()
        if row["workflow_case"]["recipe_path"] == _TAIL_WAVE_RECIPE
    }
    if referenced_tail_cases != _TAIL_WAVE_CASES:
        errors.append(
            "tail alias function mappings do not cover the five reviewed recipe cases: "
            f"missing={sorted(_TAIL_WAVE_CASES - referenced_tail_cases)}, "
            f"unexpected={sorted(referenced_tail_cases - _TAIL_WAVE_CASES)}"
        )
    tail_cases_by_id = {case.get("case_id"): case for case in tail_cases}
    for case_id in _TAIL_WAVE_CASES & tail_cases_by_id.keys():
        declared_actions = {
            action.get("action_id") for action in tail_cases_by_id[case_id].get("actions", [])
        }
        referenced_actions = {
            action_id
            for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
            for row in rows.values()
            if row["workflow_case"]["case_id"] == case_id
            for action_id in row["workflow_case"]["action_ids"]
        }
        if not referenced_actions:
            errors.append(f"tail alias recipe case has no exact source mapping: {case_id}")
        if not referenced_actions <= declared_actions:
            errors.append(
                f"tail function mapping references unknown action IDs for {case_id}: "
                f"{sorted(referenced_actions - declared_actions)}"
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
    for case_id, case in optional_query_list_cases.items():
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
                f"optional query-list alias mapping references unknown actions for {case_id}: "
                f"{sorted(referenced_actions - declared_actions)}"
            )
    referenced_required_list_cases = {
        row["workflow_case"]["case_id"]
        for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
        for row in rows.values()
        if row["workflow_case"]["recipe_path"] == _QUERY_REQUIRED_LIST_RECIPE
    }
    if referenced_required_list_cases != _QUERY_REQUIRED_LIST_CASES:
        errors.append("required query-list function mappings do not cover exactly both cases")
    for case_id, case in query_required_list_cases.items():
        declared_actions = {action.get("action_id") for action in case.get("actions", [])}
        referenced_actions = {
            action_id
            for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
            for row in rows.values()
            if row["workflow_case"]["case_id"] == case_id
            for action_id in row["workflow_case"]["action_ids"]
        }
        if not referenced_actions:
            errors.append(f"required query-list case has no exact source mapping: {case_id}")
        if not referenced_actions <= declared_actions:
            errors.append(
                f"required query-list mapping references unknown actions for {case_id}: "
                f"{sorted(referenced_actions - declared_actions)}"
            )

    query_test_path = "tests/test_query.py"
    query_function_mappings = REQUEST_PARAMETER_FUNCTION_MAPPINGS.get(query_test_path, {})
    expected_query_functions = {
        span["role"].rsplit(" ", 1)[-1] for span in _test_function_spans(query_test_path)
    }
    if set(query_function_mappings) != expected_query_functions:
        errors.append(
            "query required/optional/integer mappings do not cover exactly every pinned "
            "tests/test_query.py function"
        )
    query_case_ids = [row["workflow_case"]["case_id"] for row in query_function_mappings.values()]
    expected_query_case_ids = {
        case_id
        for case_id, row in _RECIPE_CASE_INDEX.items()
        if row["recipe_path"] == _QUERY_REQUIRED_OPTIONAL_INTEGER_RECIPE
    }
    if len(query_case_ids) != len(expected_query_case_ids) or set(query_case_ids) != (
        expected_query_case_ids
    ):
        errors.append(
            "query required/optional/integer function mappings do not cover each recipe case "
            "exactly once"
        )

    parameter_repr_function_mappings = REQUEST_PARAMETER_FUNCTION_MAPPINGS.get(
        _PARAMETER_REPR_TEST_PATH, {}
    )
    parameter_repr_source_names = {
        span["role"].rsplit(" ", 1)[-1] for span in _test_function_spans(_PARAMETER_REPR_TEST_PATH)
    }
    parameter_repr_excluded = set(
        _TOP_LEVEL_REQUEST_PARAMETER_FUNCTION_EXCLUSIONS[_PARAMETER_REPR_TEST_PATH]
    )
    if (
        set(parameter_repr_function_mappings)
        != parameter_repr_source_names - parameter_repr_excluded
    ):
        errors.append(
            "parameter repr direct mappings do not cover exactly the non-excluded public functions"
        )
    parameter_repr_case_ids = {
        row["workflow_case"]["case_id"] for row in parameter_repr_function_mappings.values()
    }
    if parameter_repr_case_ids != {_PARAMETER_REPR_CASE_ID}:
        errors.append("parameter repr functions must link to their reviewed input case")
    try:
        source_tree = ast.parse(
            (FASTAPI_ROOT / _PARAMETER_REPR_TEST_PATH).read_text(encoding="utf-8")
        )
        source_values = next(
            ast.literal_eval(node.value)
            for node in source_tree.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "test_data"
        )
        workload_tree = ast.parse(
            (
                PROJECT_ROOT / "tests/fixtures/workloads/public_model_edge_cases_upstream.py"
            ).read_text(encoding="utf-8")
        )
        workload_values = next(
            ast.literal_eval(node.value)
            for function in ast.walk(workload_tree)
            if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef))
            and function.name == "parameter_representations"
            for node in function.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "values"
        )
        if source_values != workload_values:
            errors.append("parameter repr workload inputs differ from pinned test_data values")
    except (OSError, ValueError, StopIteration) as exc:
        errors.append(f"cannot verify parameter repr source inputs: {exc}")

    function_spans = {
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
        source_tree = ast.parse("\n".join(source_lines))
        for function_name, row in rows.items():
            span = row["source_span"]
            if not (1 <= span["start_line"] <= span["end_line"] <= len(source_lines)):
                errors.append(
                    f"invalid request-parameter function source span: {test_path}:{function_name}"
                )
            source_functions = [
                node
                for node in source_tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == function_name
            ]
            if (
                len(source_functions) != 1
                or span["path"] != test_path
                or span["start_line"] != source_functions[0].lineno
                or span["end_line"]
                != (source_functions[0].end_lineno or source_functions[0].lineno)
            ):
                errors.append(
                    f"request-parameter source span does not identify {test_path}:{function_name}"
                )
            workflow = row["workflow_case"]
            case_row = recipe_index.get(workflow["case_id"])
            if case_row is None:
                errors.append(
                    f"unknown request-parameter function case: {test_path}:{function_name}"
                )
                continue
            if workflow["recipe_path"] != case_row["recipe_path"]:
                errors.append(
                    f"request-parameter function recipe path mismatch: {test_path}:{function_name}"
                )
            case = case_row["case"]
            source_paths = {
                evidence.get("path")
                for evidence in case.get("source_evidence", []) or []
                if evidence.get("kind") == "upstream_test"
            }
            if test_path not in source_paths:
                errors.append(
                    f"request-parameter function case does not cite {test_path}:{function_name}"
                )
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
    if len(function_spans) != sum(
        len(rows) for rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.values()
    ):
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
