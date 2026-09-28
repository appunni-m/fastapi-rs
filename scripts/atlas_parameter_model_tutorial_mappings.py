"""Source-reviewed atlas mappings for grouped query, header, and cookie models.

The linked recipes are input-only candidates. Their selectors are read from
the actual workflow actions so this sidecar cannot claim an unobserved result.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"
RECIPE_ROOT = PROJECT_ROOT / "tests/fixtures/input-recipes/parity"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI request, multidict, cookie parsing, response, and TestClient contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "BaseModel field defaults, coercion, constraints, Literal checks, extra policy, and model schema generation",
    },
}

_QUERY_TUTORIALS = (
    "tests/test_tutorial/test_query_param_models/test_tutorial001.py",
    "tests/test_tutorial/test_query_param_models/test_tutorial002.py",
)
_HEADER_TUTORIALS = (
    "tests/test_tutorial/test_header_param_models/test_tutorial001.py",
    "tests/test_tutorial/test_header_param_models/test_tutorial002.py",
    "tests/test_tutorial/test_header_param_models/test_tutorial003.py",
)
_COOKIE_TUTORIALS = (
    "tests/test_tutorial/test_cookie_param_models/test_tutorial001.py",
    "tests/test_tutorial/test_cookie_param_models/test_tutorial002.py",
)
TUTORIAL_TEST_MODULES = (*_QUERY_TUTORIALS, *_HEADER_TUTORIALS, *_COOKIE_TUTORIALS)

_FASTAPI_SOURCES = (
    {
        "path": "fastapi/params.py",
        "start_line": 26,
        "end_line": 134,
        "role": "FastAPI Param stores request location and parameter FieldInfo metadata used when grouped Pydantic models are declared.",
    },
    {
        "path": "fastapi/params.py",
        "start_line": 221,
        "end_line": 300,
        "role": "FastAPI Query declaration selects query parameters and forwards aliases, defaults, and validation metadata.",
    },
    {
        "path": "fastapi/params.py",
        "start_line": 303,
        "end_line": 384,
        "role": "FastAPI Header declaration selects header parameters and stores convert_underscores behavior.",
    },
    {
        "path": "fastapi/params.py",
        "start_line": 387,
        "end_line": 466,
        "role": "FastAPI Cookie declaration selects cookie parameters and forwards field metadata.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 381,
        "end_line": 547,
        "role": "FastAPI analyzes endpoint annotations/defaults, recognizes a single request-parameter BaseModel, and builds its request field.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 550,
        "end_line": 563,
        "role": "FastAPI assigns constructed request fields to the path, query, header, or cookie dependant collection.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 681,
        "end_line": 697,
        "role": "FastAPI supplies Starlette Request query parameters, headers, and cookies to request-field extraction.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 749,
        "end_line": 866,
        "role": "FastAPI reads defaults and repeated values, applies header underscore conversion, validates grouped model input, and attaches request-location errors.",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 751,
        "end_line": 755,
        "role": "FastAPI raises RequestValidationError when dependency solving returns request parameter errors.",
    },
    {
        "path": "fastapi/exception_handlers.py",
        "start_line": 20,
        "end_line": 26,
        "role": "FastAPI serializes request validation errors as a 422 JSON response.",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 159,
        "end_line": 228,
        "role": "FastAPI expands grouped request models into OpenAPI parameter names, locations, required flags, and field schemas, including header underscore names.",
    },
)

_STARLETTE_SOURCES = (
    {
        "path": "starlette/requests.py",
        "start_line": 133,
        "end_line": 159,
        "role": "Starlette Request exposes case-insensitive headers, parsed query parameters, and parsed cookies from the ASGI scope.",
    },
    {
        "path": "starlette/requests.py",
        "start_line": 46,
        "end_line": 70,
        "role": "Starlette parses cookie header pairs into a cookie mapping.",
    },
    {
        "path": "starlette/datastructures.py",
        "start_line": 253,
        "end_line": 319,
        "role": "Starlette ImmutableMultiDict retains repeated values and provides getlist/multi_items behavior for query parameters.",
    },
    {
        "path": "starlette/datastructures.py",
        "start_line": 378,
        "end_line": 407,
        "role": "Starlette QueryParams parses query strings while retaining blank values and repeated entries.",
    },
    {
        "path": "starlette/datastructures.py",
        "start_line": 500,
        "end_line": 574,
        "role": "Starlette Headers provides case-insensitive multi-value header lookup used for model field extraction.",
    },
    {
        "path": "starlette/testclient.py",
        "start_line": 327,
        "end_line": 375,
        "role": "Starlette TestClient transports ASGI response status, headers, and body into the observable response.",
    },
)

_OWNERSHIP_BOUNDARIES = {
    "fastapi": (
        "FastAPI owns Query/Header/Cookie declarations, endpoint parameter analysis, grouping a single BaseModel into a request location, extraction aliases/defaults, validation error location and 422 handling, and OpenAPI parameter assembly."
    ),
    "pydantic": (
        "Pinned Pydantic 2.13.4 owns BaseModel field parsing/coercion, defaults, Literal and numeric constraints, model extra-ignore/extra-forbid policy, and generated field schemas. These checks are not attributed to FastAPI."
    ),
    "starlette": (
        "Pinned Starlette 1.6.0 owns ASGI Request construction, query/header/cookie parsing, multidict repeated-value behavior, response transport, and TestClient defaults. Generic behavior is tracked by the separate Starlette-RS contract."
    ),
}

_MODULE_GATES = (
    "The source fixtures parameterize both direct parameter-default and Annotated declarations. Each linked independent workload instantiates one declaration form, so equivalence across both source fixture variants remains gated.",
    "Most source tests compare response.json() values; workflows observe exact response body bytes, which is a stricter wire comparison. These mappings remain atlas candidates and do not claim a live source/target parity result.",
    "OpenAPI tutorial tests snapshot the full document; workflows select only the request parameter list for one path. Full-document equivalence remains unproven.",
)

_HEADER_T3_GATE = "The source header tutorial includes TestClient-generated request headers in validation error input, including an Accept-Encoding value accepted from a set. The workflow selects status only for its failure actions, so structured error input/details remain gated."


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_spans(test_path: str) -> dict[str, dict[str, Any]]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    spans: dict[str, dict[str, Any]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
            "test_"
        ):
            spans[node.name] = _source(
                test_path,
                node.lineno,
                node.end_lineno or node.lineno,
                f"FastAPI 0.141.1 upstream test function {node.name}",
            )
    return spans


def _fixture_and_document_sources(test_path: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    test_tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    fixture = next(
        node
        for node in test_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_client"
    )
    fixture_span = _source(
        test_path,
        min([fixture.lineno, *(decorator.lineno for decorator in fixture.decorator_list)]),
        fixture.end_lineno or fixture.lineno,
        "Upstream fixture selects direct and Annotated docs_src variants for the tutorial test module.",
    )
    variants = sorted(
        {
            node.value
            for node in ast.walk(test_tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and re.fullmatch(r"tutorial\d{3}(?:_an)?_py310", node.value)
        }
    )
    docs_group = (
        "query_param_models"
        if "query_param_models" in test_path
        else (
            "header_param_models" if "header_param_models" in test_path else "cookie_param_models"
        )
    )
    doc_sources: list[dict[str, Any]] = []
    for variant in variants:
        doc_path = f"docs_src/{docs_group}/{variant}.py"
        tree = ast.parse((FASTAPI_ROOT / doc_path).read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                doc_sources.append(
                    _source(
                        doc_path,
                        node.lineno,
                        node.end_lineno or node.lineno,
                        f"FastAPI tutorial docs model declaration {node.name} ({variant}) used by the source test fixture.",
                    )
                )
            elif (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == "read_items"
            ):
                doc_sources.append(
                    _source(
                        doc_path,
                        node.lineno,
                        node.end_lineno or node.lineno,
                        f"FastAPI tutorial docs endpoint declaration read_items ({variant}) used by the source test fixture.",
                    )
                )
    return fixture_span, doc_sources


def _action_selectors(action: dict[str, Any]) -> list[str]:
    selected: set[str] = set()
    for observation in action.get("observations", []):
        if observation.get("kind") == "http_response":
            selectors = set(observation.get("selectors", []))
            if "status" in selectors:
                selected.add("http.status")
            if "headers" in selectors:
                selected.add("http.headers.ordered")
            if "body" in selectors:
                selected.add("http.body.bytes")
        elif observation.get("kind") == "openapi":
            for pointer in observation.get("json_pointers", []):
                selected.add("openapi.document")
                if pointer.startswith("/paths/"):
                    selected.add("openapi.paths")
    return sorted(selected)


def _recipe_index() -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for recipe in sorted(RECIPE_ROOT.glob("*.yaml")):
        data = yaml.safe_load(recipe.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema") not in {
            "fastapi-rs/python-asgi-workflow@2",
            "fastapi-rs/python-asgi-workflow@3",
        }:
            continue
        for case in data.get("cases", []):
            case_id = case["case_id"]
            if case_id in cases:
                raise ValueError(f"duplicate input recipe case ID: {case_id}")
            cases[case_id] = {
                "recipe_path": str(recipe.relative_to(PROJECT_ROOT)),
                "case": case,
                "actions": {action["action_id"]: action for action in case.get("actions", [])},
            }
    return cases


def _link(recipe_path: str, case_id: str, action_id: str, selectors: list[str]) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": [action_id],
        "observation_selectors": sorted(selectors),
    }


_Q1 = "tests/fixtures/input-recipes/parity/query-param-models.yaml"
_Q1_EDGES = "tests/fixtures/input-recipes/parity/query-param-model-tutorial-edges.yaml"
_REQUEST_MODELS = "tests/fixtures/input-recipes/parity/request-models.yaml"
_MODEL_EDGES = "tests/fixtures/input-recipes/parity/request-parameter-model-tutorial-edges.yaml"
_IGNORE_EDGES = (
    "tests/fixtures/input-recipes/parity/request-parameter-model-tutorial-ignore-edges.yaml"
)
_HEADER3 = "tests/fixtures/input-recipes/parity/header-param-model-tutorial003.yaml"
_OPENAPI_WAVE = "tests/fixtures/input-recipes/parity/request-parameter-openapi-wave.yaml"

_STATUS_BODY = ["http.body.bytes", "http.status"]
_STATUS_ONLY = ["http.status"]
_OPENAPI = ["openapi.document", "openapi.paths"]
_STATUS_OPENAPI = ["http.status", "openapi.document", "openapi.paths"]


def _fn(
    test_path: str,
    function_name: str,
    links: list[dict[str, Any]],
    feature_ids: list[str],
    rationale: str,
    gates: list[str] | None = None,
) -> dict[str, Any]:
    span = _test_spans(test_path)[function_name]
    selectors = sorted({selector for link in links for selector in link["observation_selectors"]})
    return {
        "mapping_status": "mapped-partial",
        "source_span": span,
        "feature_ids": feature_ids,
        "observation_selectors": selectors,
        "rationale": rationale,
        "workflow_cases": links,
        "supporting_sources": [*_FASTAPI_SOURCES, *_STARLETTE_SOURCES],
        "contract_gates": [*_MODULE_GATES, *(gates or [])],
    }


def _module(test_path: str, function_mappings: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fixture_span, docs_sources = _fixture_and_document_sources(test_path)
    module_sources = [fixture_span, *docs_sources, *_FASTAPI_SOURCES, *_STARLETTE_SOURCES]
    links_by_id: dict[tuple[str, str], dict[str, Any]] = {}
    for row in function_mappings.values():
        for link in row["workflow_cases"]:
            links_by_id.setdefault((link["recipe_path"], link["case_id"]), link)
    return {
        "mapping_status": "mapped-partial",
        "feature_ids": sorted(
            {feature for row in function_mappings.values() for feature in row["feature_ids"]}
        ),
        "observation_selectors": sorted(
            {
                selector
                for row in function_mappings.values()
                for selector in row["observation_selectors"]
            }
        ),
        "source_test_spans": list(_test_spans(test_path).values()),
        "fixture_source_span": fixture_span,
        "documentation_sources": docs_sources,
        "supporting_sources": module_sources,
        "workflow_cases": list(links_by_id.values()),
        "ownership_boundaries": dict(_OWNERSHIP_BOUNDARIES),
        "contract_gates": list(_MODULE_GATES),
        "function_mappings": function_mappings,
    }


_QUERY_T1_PATH = _QUERY_TUTORIALS[0]
_QUERY_T2_PATH = _QUERY_TUTORIALS[1]
_HEADER_T1_PATH = _HEADER_TUTORIALS[0]
_HEADER_T2_PATH = _HEADER_TUTORIALS[1]
_HEADER_T3_PATH = _HEADER_TUTORIALS[2]
_COOKIE_T1_PATH = _COOKIE_TUTORIALS[0]
_COOKIE_T2_PATH = _COOKIE_TUTORIALS[1]


PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    _QUERY_T1_PATH: _module(
        _QUERY_T1_PATH,
        {
            "test_query_param_model": _fn(
                _QUERY_T1_PATH,
                "test_query_param_model",
                [
                    _link(
                        _Q1,
                        "fastapi.query-param-models.grouped-repeated-list",
                        "get-items-with-repeated-tags",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies the grouped query model with scalar fields and two repeated tag values.",
            ),
            "test_query_param_model_defaults": _fn(
                _QUERY_T1_PATH,
                "test_query_param_model_defaults",
                [
                    _link(
                        _Q1,
                        "fastapi.query-param-models.grouped-defaults",
                        "get-items-with-default-filters",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies the Pydantic defaults for all grouped query model fields.",
            ),
            "test_query_param_model_invalid": _fn(
                _QUERY_T1_PATH,
                "test_query_param_model_invalid",
                [
                    _link(
                        _Q1,
                        "fastapi.query-param-models.grouped-validation-invalid",
                        "get-items-with-invalid-filters",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks upper/lower numeric bounds and Literal rejection on grouped query fields.",
            ),
            "test_query_param_model_extra": _fn(
                _QUERY_T1_PATH,
                "test_query_param_model_extra",
                [
                    _link(
                        _Q1_EDGES,
                        "fastapi.request-parameter-model-tutorial.query-001-extra-ignore",
                        "query-extra-ignored",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source checks that an undeclared query key is ignored by the default Pydantic model extra policy.",
            ),
            "test_openapi_schema": _fn(
                _QUERY_T1_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _Q1,
                        "fastapi.query-param-models.openapi-query-parameters",
                        "get-openapi-query-parameters",
                        _STATUS_OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects the /items/ query-parameter array and response status.",
            ),
        },
    ),
    _QUERY_T2_PATH: _module(
        _QUERY_T2_PATH,
        {
            "test_query_param_model": _fn(
                _QUERY_T2_PATH,
                "test_query_param_model",
                [
                    _link(
                        _REQUEST_MODELS,
                        "fastapi.request-models.query-model-002.test-query-param-model",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies successful parsing of grouped query fields with the model's extra-forbid configuration.",
            ),
            "test_query_param_model_defaults": _fn(
                _QUERY_T2_PATH,
                "test_query_param_model_defaults",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.query-002",
                        "query-defaults",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies model defaults when all optional grouped query fields are omitted.",
            ),
            "test_query_param_model_invalid": _fn(
                _QUERY_T2_PATH,
                "test_query_param_model_invalid",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.query-002",
                        "query-validation-invalid",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks numeric bounds and Literal validation errors for grouped query fields.",
            ),
            "test_query_param_model_extra": _fn(
                _QUERY_T2_PATH,
                "test_query_param_model_extra",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.query-002",
                        "query-extra-forbidden",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks that ConfigDict(extra='forbid') rejects an undeclared query key.",
            ),
            "test_openapi_schema": _fn(
                _QUERY_T2_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.query-002",
                        "query-openapi-parameters",
                        _STATUS_OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects only the grouped query parameter list and response status.",
            ),
        },
    ),
    _HEADER_T1_PATH: _module(
        _HEADER_T1_PATH,
        {
            "test_header_param_model": _fn(
                _HEADER_T1_PATH,
                "test_header_param_model",
                [
                    _link(
                        _OPENAPI_WAVE,
                        "fastapi.request-parameter-openapi-wave.header-model.test-header-param-model",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies normal hyphenated headers, default underscore-to-hyphen conversion, boolean parsing, and repeated x-tag values.",
            ),
            "test_header_param_model_defaults": _fn(
                _HEADER_T1_PATH,
                "test_header_param_model_defaults",
                [
                    _link(
                        _OPENAPI_WAVE,
                        "fastapi.request-parameter-openapi-wave.header-model.test-header-param-model-defaults",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies optional header defaults and an empty repeated-header list.",
            ),
            "test_header_param_model_invalid": _fn(
                _HEADER_T1_PATH,
                "test_header_param_model_invalid",
                [
                    _link(
                        _IGNORE_EDGES,
                        "fastapi.request-parameter-model-tutorial.header-001-ignore-edges",
                        "header-required-missing",
                        _STATUS_ONLY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks a missing required header; this workflow selects the 422 status because the upstream TestClient contributes additional transport headers to error input.",
            ),
            "test_header_param_model_extra": _fn(
                _HEADER_T1_PATH,
                "test_header_param_model_extra",
                [
                    _link(
                        _IGNORE_EDGES,
                        "fastapi.request-parameter-model-tutorial.header-001-ignore-edges",
                        "header-extra-ignored",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source checks that an undeclared header is ignored under the default Pydantic model extra policy.",
            ),
            "test_openapi_schema": _fn(
                _HEADER_T1_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _OPENAPI_WAVE,
                        "fastapi.request-parameter-openapi-wave.header-model.test-openapi-schema",
                        "dispatch",
                        _OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects the /headers parameter array only.",
            ),
        },
    ),
    _HEADER_T2_PATH: _module(
        _HEADER_T2_PATH,
        {
            "test_header_param_model": _fn(
                _HEADER_T2_PATH,
                "test_header_param_model",
                [
                    _link(
                        _REQUEST_MODELS,
                        "fastapi.request-models.header-model-002.test-header-param-model",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies hyphenated header extraction, boolean coercion, and repeated list-valued headers under extra-forbid model configuration.",
            ),
            "test_header_param_model_defaults": _fn(
                _HEADER_T2_PATH,
                "test_header_param_model_defaults",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.header-002",
                        "header-defaults",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies optional header defaults and an empty repeated-header list.",
            ),
            "test_header_param_model_invalid": _fn(
                _HEADER_T2_PATH,
                "test_header_param_model_invalid",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.header-002",
                        "header-required-missing",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks the missing required save-data header and its header-location validation error.",
            ),
            "test_header_param_model_extra": _fn(
                _HEADER_T2_PATH,
                "test_header_param_model_extra",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.header-002",
                        "header-extra-forbidden",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks that ConfigDict(extra='forbid') rejects an undeclared header.",
            ),
            "test_openapi_schema": _fn(
                _HEADER_T2_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.header-002",
                        "header-openapi-parameters",
                        _STATUS_OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects only the /trace header parameter array and response status.",
            ),
        },
    ),
    _HEADER_T3_PATH: _module(
        _HEADER_T3_PATH,
        {
            "test_header_param_model": _fn(
                _HEADER_T3_PATH,
                "test_header_param_model",
                [
                    _link(
                        _HEADER3,
                        "fastapi.request-parameter-model-tutorial.header-003-underscore-disabled",
                        "header-underscore-valid",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies that literal underscore header names populate the grouped model when convert_underscores is disabled.",
            ),
            "test_header_param_model_no_underscore": _fn(
                _HEADER_T3_PATH,
                "test_header_param_model_no_underscore",
                [
                    _link(
                        _HEADER3,
                        "fastapi.request-parameter-model-tutorial.header-003-underscore-disabled",
                        "header-hyphenated-name-missing",
                        _STATUS_ONLY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks that hyphenated names do not satisfy literal underscore aliases and return 422.",
                [_HEADER_T3_GATE],
            ),
            "test_header_param_model_defaults": _fn(
                _HEADER_T3_PATH,
                "test_header_param_model_defaults",
                [
                    _link(
                        _HEADER3,
                        "fastapi.request-parameter-model-tutorial.header-003-underscore-disabled",
                        "header-underscore-defaults",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies optional defaults with a literal save_data header.",
            ),
            "test_header_param_model_invalid": _fn(
                _HEADER_T3_PATH,
                "test_header_param_model_invalid",
                [
                    _link(
                        _HEADER3,
                        "fastapi.request-parameter-model-tutorial.header-003-underscore-disabled",
                        "header-underscore-required-missing",
                        _STATUS_ONLY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks the missing required literal save_data header.",
                [_HEADER_T3_GATE],
            ),
            "test_header_param_model_extra": _fn(
                _HEADER_T3_PATH,
                "test_header_param_model_extra",
                [
                    _link(
                        _HEADER3,
                        "fastapi.request-parameter-model-tutorial.header-003-underscore-disabled",
                        "header-extra-ignored",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source checks that a tool header is ignored while convert_underscores is disabled and the model uses the default extra-ignore policy.",
            ),
            "test_openapi_schema": _fn(
                _HEADER_T3_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _HEADER3,
                        "fastapi.request-parameter-model-tutorial.header-003-underscore-disabled",
                        "header-underscore-openapi",
                        _OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects only the /items/ header parameter array, whose literal names retain underscores.",
            ),
        },
    ),
    _COOKIE_T1_PATH: _module(
        _COOKIE_T1_PATH,
        {
            "test_cookie_param_model": _fn(
                _COOKIE_T1_PATH,
                "test_cookie_param_model",
                [
                    _link(
                        _OPENAPI_WAVE,
                        "fastapi.request-parameter-openapi-wave.cookie-model.test-cookie-param-model",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies required and optional cookie fields from a grouped cookie model.",
            ),
            "test_cookie_param_model_defaults": _fn(
                _COOKIE_T1_PATH,
                "test_cookie_param_model_defaults",
                [
                    _link(
                        _OPENAPI_WAVE,
                        "fastapi.request-parameter-openapi-wave.cookie-model.test-cookie-param-model-defaults",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies optional cookie defaults when only the required session_id cookie is present.",
            ),
            "test_cookie_param_model_invalid": _fn(
                _COOKIE_T1_PATH,
                "test_cookie_param_model_invalid",
                [
                    _link(
                        _IGNORE_EDGES,
                        "fastapi.request-parameter-model-tutorial.cookie-001-ignore-edges",
                        "cookie-required-missing",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks a missing required session_id cookie.",
            ),
            "test_cookie_param_model_extra": _fn(
                _COOKIE_T1_PATH,
                "test_cookie_param_model_extra",
                [
                    _link(
                        _IGNORE_EDGES,
                        "fastapi.request-parameter-model-tutorial.cookie-001-ignore-edges",
                        "cookie-extra-ignored",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source checks that an undeclared cookie is ignored by the default Pydantic model extra policy.",
            ),
            "test_openapi_schema": _fn(
                _COOKIE_T1_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _OPENAPI_WAVE,
                        "fastapi.request-parameter-openapi-wave.cookie-model.test-openapi-schema",
                        "dispatch",
                        _OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects only the /cookies parameter array.",
            ),
        },
    ),
    _COOKIE_T2_PATH: _module(
        _COOKIE_T2_PATH,
        {
            "test_cookie_param_model": _fn(
                _COOKIE_T2_PATH,
                "test_cookie_param_model",
                [
                    _link(
                        _REQUEST_MODELS,
                        "fastapi.request-models.cookie-model-002.test-cookie-param-model",
                        "dispatch",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies all grouped cookie values with the model's extra-forbid configuration.",
            ),
            "test_cookie_param_model_defaults": _fn(
                _COOKIE_T2_PATH,
                "test_cookie_param_model_defaults",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.cookie-002",
                        "cookie-defaults",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "response-serialization"],
                "The source verifies optional cookie defaults with the required session_id cookie present.",
            ),
            "test_cookie_param_model_invalid": _fn(
                _COOKIE_T2_PATH,
                "test_cookie_param_model_invalid",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.cookie-002",
                        "cookie-required-missing",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks the missing required session_id cookie and cookie-location error.",
            ),
            "test_cookie_param_model_extra": _fn(
                _COOKIE_T2_PATH,
                "test_cookie_param_model_extra",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.cookie-002",
                        "cookie-extra-forbidden",
                        _STATUS_BODY,
                    )
                ],
                ["request-validation", "public-api-errors"],
                "The source checks that ConfigDict(extra='forbid') rejects an undeclared cookie.",
            ),
            "test_openapi_schema": _fn(
                _COOKIE_T2_PATH,
                "test_openapi_schema",
                [
                    _link(
                        _MODEL_EDGES,
                        "fastapi.request-parameter-model-tutorial.cookie-002",
                        "cookie-openapi-parameters",
                        _STATUS_OPENAPI,
                    )
                ],
                ["openapi-docs"],
                "The source snapshots the complete OpenAPI document; the workflow selects only the /session cookie parameter array and response status.",
            ),
        },
    ),
}


def _builder_review_mappings() -> dict[str, dict[str, Any]]:
    """Normalize reviewed source links to the main atlas builder's mapping shape."""
    normalized: dict[str, dict[str, Any]] = {}
    for test_path, module in PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS.items():
        functions: dict[str, dict[str, Any]] = {}
        for function_name, function in module["function_mappings"].items():
            notes = [
                f"{link['recipe_path']}::{link['case_id']} action {', '.join(link['action_ids'])}; selectors: {', '.join(link['observation_selectors'])}"
                for link in function["workflow_cases"]
            ]
            functions[function_name] = {
                "feature_ids": function["feature_ids"],
                "observation_selectors": function["observation_selectors"],
                "rationale": function["rationale"],
                "replace_features": True,
                "supporting_sources": [function["source_span"], *function["supporting_sources"]],
                "stimulus_notes": "Input-only workflow links: " + "; ".join(notes) + ".",
                "contract_gate": "; ".join(function["contract_gates"]),
            }
        normalized[test_path] = {
            "feature_ids": module["feature_ids"],
            "module_observation_selectors": module["observation_selectors"],
            "rationale": "Source-reviewed grouped query/header/cookie tutorial module with exact function-level input-only workflow links.",
            "supporting_sources": module["supporting_sources"],
            "functions": functions,
        }
    return normalized


PARAMETER_MODEL_TUTORIAL_BUILDER_REVIEW_MAPPINGS = _builder_review_mappings()


def validate_parameter_model_tutorial_mappings() -> list[str]:
    errors: list[str] = []
    for name, root, expected in (
        ("fastapi", FASTAPI_ROOT, SOURCE_IDENTITIES["fastapi"]["commit"]),
        ("starlette", STARLETTE_ROOT, SOURCE_IDENTITIES["starlette"]["commit"]),
    ):
        actual = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != expected:
            errors.append(f"{name} source commit differs from pinned identity: {actual}")

    backlog = json.loads((PROJECT_ROOT / "tests/fixtures/fixture-backlog.json").read_text())
    authority = backlog.get("authority", {})
    if authority.get("fastapi", {}).get("commit") != SOURCE_IDENTITIES["fastapi"]["commit"]:
        errors.append("fixture backlog FastAPI identity differs from the reviewed identity")
    if authority.get("starlette", {}).get("commit") != SOURCE_IDENTITIES["starlette"]["commit"]:
        errors.append("fixture backlog Starlette identity differs from the reviewed identity")
    if (
        authority.get("pydantic", {}).get("selected_version")
        != SOURCE_IDENTITIES["pydantic"]["version"]
    ):
        errors.append("fixture backlog Pydantic version differs from the reviewed identity")

    recipe_index = _recipe_index()
    source_roots = {
        "fastapi/": FASTAPI_ROOT,
        "starlette/": STARLETTE_ROOT,
        "docs_src/": FASTAPI_ROOT,
        "tests/": FASTAPI_ROOT,
    }
    test_function_total = 0
    case_action_link_total = 0
    for test_path, module in PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS.items():
        if test_path not in TUTORIAL_TEST_MODULES:
            errors.append(f"unexpected module mapping: {test_path}")
        actual_spans = _test_spans(test_path)
        functions = module["function_mappings"]
        if set(functions) != set(actual_spans):
            errors.append(f"test function denominator mismatch for {test_path}")
        if module["source_test_spans"] != list(actual_spans.values()):
            errors.append(f"module test spans differ from the pinned source AST: {test_path}")
        test_function_total += len(functions)
        for source in module["supporting_sources"]:
            root = next(
                (
                    candidate
                    for prefix, candidate in source_roots.items()
                    if source["path"].startswith(prefix)
                ),
                None,
            )
            if root is None:
                errors.append(f"unknown evidence source root: {source['path']}")
                continue
            source_file = root / source["path"]
            if not source_file.is_file():
                errors.append(f"missing evidence source: {source_file}")
                continue
            lines = source_file.read_text(encoding="utf-8").splitlines()
            if not (1 <= source["start_line"] <= source["end_line"] <= len(lines)):
                errors.append(f"invalid evidence source span: {source}")
        for function_name, function in functions.items():
            if function["source_span"] != actual_spans.get(function_name):
                errors.append(f"source span mismatch for {test_path}:{function_name}")
            if function["mapping_status"] != "mapped-partial" or not function["workflow_cases"]:
                errors.append(
                    f"function is not mapped to an input workflow: {test_path}:{function_name}"
                )
            for link in function["workflow_cases"]:
                case_action_link_total += len(link["action_ids"])
                case_row = recipe_index.get(link["case_id"])
                if case_row is None:
                    errors.append(f"unknown workflow case {link['case_id']}")
                    continue
                if case_row["recipe_path"] != link["recipe_path"]:
                    errors.append(f"recipe path mismatch for {link['case_id']}")
                evidence_paths = {
                    evidence.get("path")
                    for evidence in case_row["case"].get("source_evidence", []) or []
                    if evidence.get("kind") == "upstream_test"
                }
                if test_path not in evidence_paths:
                    errors.append(
                        f"workflow case {link['case_id']} omits source evidence for {test_path}"
                    )
                for action_id in link["action_ids"]:
                    action = case_row["actions"].get(action_id)
                    if action is None:
                        errors.append(f"missing action {action_id} in {link['case_id']}")
                        continue
                    actual_selectors = _action_selectors(action)
                    if sorted(link["observation_selectors"]) != actual_selectors:
                        errors.append(
                            f"selector mismatch for {link['case_id']}:{action_id}: declared {link['observation_selectors']}, actual {actual_selectors}"
                        )
        normalized = PARAMETER_MODEL_TUTORIAL_BUILDER_REVIEW_MAPPINGS.get(test_path, {})
        if set(normalized.get("functions", {})) != set(functions):
            errors.append(f"builder adapter function mismatch for {test_path}")

    if set(PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS) != set(TUTORIAL_TEST_MODULES):
        errors.append("mapping module set does not exactly cover the assigned seven files")
    if test_function_total != 36:
        errors.append(f"expected 36 test functions, found {test_function_total}")

    for source in [*_FASTAPI_SOURCES, *_STARLETTE_SOURCES]:
        if source["path"].startswith("fastapi/"):
            root = FASTAPI_ROOT
        else:
            root = STARLETTE_ROOT
        source_file = root / source["path"]
        line_count = len(source_file.read_text(encoding="utf-8").splitlines())
        if not (1 <= source["start_line"] <= source["end_line"] <= line_count):
            errors.append(
                f"invalid pinned implementation span {source['path']}:{source['start_line']}-{source['end_line']}"
            )

    expected_recipes = (
        "query-param-model-tutorial-edges.yaml",
        "request-parameter-model-tutorial-edges.yaml",
        "request-parameter-model-tutorial-ignore-edges.yaml",
        "header-param-model-tutorial003.yaml",
    )
    forbidden_fields = {
        "expected",
        "expected_output",
        "expected_outputs",
        "measurement",
        "measurements",
        "benchmark",
    }
    for recipe_name in expected_recipes:
        recipe_path = RECIPE_ROOT / recipe_name
        data = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
        if data.get("schema") != "fastapi-rs/python-asgi-workflow@2":
            errors.append(f"unexpected workflow schema in {recipe_name}")

        def reject_outputs(value: Any, where: str) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    if str(key).lower() in forbidden_fields:
                        errors.append(
                            f"forbidden expected-output/measurement field {key!r} at {where}"
                        )
                    reject_outputs(child, f"{where}.{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    reject_outputs(child, f"{where}[{index}]")

        reject_outputs(data, recipe_name)
        workload = data.get("workload", {}).get("file", "")
        if not (PROJECT_ROOT / workload).is_file():
            errors.append(f"missing recipe workload {workload}")
        for case in data.get("cases", []):
            for action in case.get("actions", []):
                if (
                    action.get("kind") != "http_request"
                    or action.get("scope", {}).get("type") != "http"
                ):
                    errors.append(
                        f"unexpected non-HTTP stimulus in {recipe_name}:{action.get('action_id')}"
                    )
                if action.get("scope", {}).get("method") != "GET":
                    errors.append(
                        f"unexpected request method in {recipe_name}:{action.get('action_id')}"
                    )
    new_workload = PROJECT_ROOT / "tests/fixtures/workloads/header_param_models_tutorial003.py"
    if not new_workload.is_file():
        errors.append(f"missing dedicated underscore-disabled header workload: {new_workload}")
    return errors


if __name__ == "__main__":
    failures = validate_parameter_model_tutorial_mappings()
    if failures:
        raise SystemExit("\n".join(failures))
    modules = len(PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS)
    functions = sum(
        len(row["function_mappings"])
        for row in PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS.values()
    )
    links = sum(
        len(function["workflow_cases"])
        for module in PARAMETER_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS.values()
        for function in module["function_mappings"].values()
    )
    print(
        f"validated {modules} modules, {functions} test functions, {links} function-to-case links"
    )
