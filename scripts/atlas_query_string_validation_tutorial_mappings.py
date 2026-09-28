"""Source-reviewed mappings for the FastAPI query-string tutorial tests.

The mappings are candidate evidence only. They link exact upstream test-function
spans to existing or input-only ASGI cases; they do not encode expected output
or claim live source/target parity.
"""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"
RECIPE_ROOT = PROJECT_ROOT / "tests/fixtures/input-recipes/parity"
TEST_ROOT = FASTAPI_ROOT / "tests/test_tutorial/test_query_params_str_validations"
DOC_ROOT = FASTAPI_ROOT / "docs_src/query_params_str_validations"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI, query-string parsing, response, and TestClient contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned field validation, string constraints, custom AfterValidator, and schema generation dependency",
    },
}

_FASTAPI_SOURCES = (
    {
        "path": "fastapi/params.py",
        "start_line": 26,
        "end_line": 60,
        "role": "FastAPI Param declaration stores query field metadata, aliases, length bounds, and pattern constraints.",
    },
    {
        "path": "fastapi/params.py",
        "start_line": 221,
        "end_line": 300,
        "role": "FastAPI Query selects query location and forwards defaults, aliases, descriptions, deprecation, and constraints to FieldInfo.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 381,
        "end_line": 547,
        "role": "FastAPI analyzes endpoint annotations/defaults, copies Annotated FieldInfo, infers Query, applies aliases, and creates the request field.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 550,
        "end_line": 560,
        "role": "FastAPI classifies a created field into the dependant's query-parameter collection.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 681,
        "end_line": 697,
        "role": "FastAPI supplies Starlette Request.query_params to query-field extraction and collects resulting values/errors.",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 734,
        "end_line": 866,
        "role": "FastAPI handles missing/default values, reads aliases and repeated values, invokes the field validator, and attaches query locations to errors.",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 751,
        "end_line": 755,
        "role": "FastAPI turns dependency-solving errors into RequestValidationError.",
    },
    {
        "path": "fastapi/exception_handlers.py",
        "start_line": 20,
        "end_line": 26,
        "role": "FastAPI encodes request validation errors as a 422 JSON response.",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 159,
        "end_line": 228,
        "role": "FastAPI builds OpenAPI parameter names, query location, required flags, schemas, descriptions, and deprecation metadata.",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 672,
        "end_line": 679,
        "role": "FastAPI validates and encodes the assembled OpenAPI document through its OpenAPI model.",
    },
)

_STARLETTE_SOURCES = (
    {
        "path": "starlette/requests.py",
        "start_line": 138,
        "end_line": 142,
        "role": "Starlette Request lazily constructs QueryParams from the ASGI query_string bytes.",
    },
    {
        "path": "starlette/datastructures.py",
        "start_line": 253,
        "end_line": 319,
        "role": "Starlette ImmutableMultiDict stores repeated query pairs and exposes getlist/multi_items semantics.",
    },
    {
        "path": "starlette/datastructures.py",
        "start_line": 378,
        "end_line": 399,
        "role": "Starlette QueryParams parses blank query values and normalizes keys/values to strings.",
    },
    {
        "path": "fastapi/testclient.py",
        "start_line": 1,
        "end_line": 1,
        "role": "FastAPI TestClient is a direct Starlette TestClient re-export.",
    },
    {
        "path": "starlette/testclient.py",
        "start_line": 327,
        "end_line": 365,
        "role": "Starlette TestClient transports ASGI response start/body messages into the observed response.",
    },
)

_GLOBAL_GATES = (
    "Atlas mapping is candidate evidence only: the manifest remains foundation-only and no identity-checked source/target run is represented.",
    "Where an upstream fixture parameterizes both direct Query and Annotated declarations, each independent workload represents one declaration form, so the other variant remains gated.",
    "Pydantic 2.13.4 owns value/type validation, string length and pattern enforcement, custom AfterValidator execution, and field schema generation. FastAPI owns parameter classification, extraction, error locations/422 handling, and OpenAPI parameter assembly.",
    "Generic ASGI request/response transport, query-string decoding, blank-value preservation, multidict behavior, and FastAPI TestClient behavior belong to the pinned Starlette 1.6.0 / Starlette-RS contract.",
)


def _src(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_spans(test_path: str) -> dict[str, dict[str, Any]]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    spans: dict[str, dict[str, Any]] = {}
    for node in tree.body:
        if not isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ) or not node.name.startswith("test_"):
            continue
        start_line = min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)])
        spans[node.name] = _src(
            test_path,
            start_line,
            node.end_lineno or node.lineno,
            f"FastAPI 0.141.1 upstream test function {node.name}",
        )
    return spans


def _fixture_source(test_path: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_client":
            start_line = min(
                [node.lineno, *(decorator.lineno for decorator in node.decorator_list)]
            )
            return _src(
                test_path,
                start_line,
                node.end_lineno or node.lineno,
                "Upstream fixture selects the docs_src direct/Annotated variants used by this tutorial test module.",
            )
    raise ValueError(f"get_client fixture was not found in {test_path}")


def _doc_variant_names(test_path: str) -> tuple[str, ...]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    names = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and re.fullmatch(r"tutorial\d{3}c?(?:_an)?_py310", node.value)
    }
    return tuple(sorted(names))


def _doc_endpoint_sources(test_path: str) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for variant in _doc_variant_names(test_path):
        path = f"docs_src/query_params_str_validations/{variant}.py"
        tree = ast.parse((FASTAPI_ROOT / path).read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name != "read_items":
                continue
            if not any(
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "get"
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
                and decorator.args[0].value == "/items/"
                for decorator in node.decorator_list
            ):
                continue
            sources.append(
                _src(
                    path,
                    node.lineno,
                    node.end_lineno or node.lineno,
                    f"FastAPI documentation endpoint fixture {variant} used by the upstream test fixture",
                )
            )
            break
    return sources


def _action_selectors(action: dict[str, Any]) -> list[str]:
    selected: set[str] = set()
    openapi_endpoint = action.get("scope", {}).get("path") == "/openapi.json"
    for observation in action.get("observations", []):
        if observation.get("kind") == "http_response":
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
        elif observation.get("kind") == "openapi":
            for pointer in observation.get("json_pointers", []):
                if pointer.startswith("/paths/"):
                    selected.update(("openapi.document", "openapi.paths"))
                else:
                    selected.add("openapi.document")
    return sorted(selected)


def _recipe_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in sorted(RECIPE_ROOT.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema") not in {
            "fastapi-rs/python-asgi-workflow@2",
            "fastapi-rs/python-asgi-workflow@3",
        }:
            continue
        for case in data.get("cases", []):
            case_id = case["case_id"]
            if case_id in index:
                raise ValueError(f"duplicate recipe case ID {case_id}")
            index[case_id] = {
                "recipe_path": str(path.relative_to(PROJECT_ROOT)),
                "case": case,
                "actions": {action["action_id"]: action for action in case.get("actions", [])},
            }
    return index


_P = "tests/fixtures/input-recipes/parity/"
_BRANCH_RECIPE = _P + "query-string-validation-tutorial-branches.yaml"
_T002_RECIPE = _P + "query-string-validation-tutorial002-branches.yaml"
_T006_RECIPE = _P + "query-string-validation-tutorial006-required.yaml"
_TEN_MODULE_RECIPE = _P + "query-string-validation-ten-modules-upstream.yaml"
_REQUEST_VALIDATION_RECIPE = _P + "request-validation-wave.yaml"
_REQUEST_PARAMETER_RECIPE = _P + "request-parameter-openapi-wave.yaml"
_EDGE_RECIPE = _P + "request-parameter-edges-wave.yaml"
_TAIL_RECIPE = _P + "request-parameter-tail-wave.yaml"

_WORKLOAD_DECLARATION_FORMS = {
    "test_tutorial001.py": "plain optional query parameter (no Query metadata)",
    "test_tutorial002.py": "Annotated[str | None, Query(max_length=50)]",
    "test_tutorial006.py": "Annotated[str, Query(min_length=3)]",
    "test_tutorial015.py": "Annotated[str | None, AfterValidator(...)]",
}


def _ref(recipe: str, case_id: str, action_id: str) -> tuple[str, str, str]:
    return recipe, case_id, action_id


_PLANS: dict[str, dict[str, Any]] = {
    "test_tutorial001.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial001-omitted-empty-openapi",
            "omitted-query",
        ),
        "test_query_params_str_validations_q_empty_str": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial001-omitted-empty-openapi",
            "empty-query",
        ),
        "test_query_params_str_validations_q_query": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial001-basic-query",
            "optional-query-value",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial001-omitted-empty-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial002.py": {
        "test_query_params_str_validations_no_query": _ref(
            _T002_RECIPE,
            "fastapi.query-validation.tutorial002-optional-query-values",
            "omitted-query",
        ),
        "test_query_params_str_validations_q_empty_str": _ref(
            _T002_RECIPE,
            "fastapi.query-validation.tutorial002-optional-query-values",
            "empty-query",
        ),
        "test_query_params_str_validations_q_query": _ref(
            _T002_RECIPE,
            "fastapi.query-validation.tutorial002-optional-query-values",
            "valid-query",
        ),
        "test_query_params_str_validations_q_too_long": _ref(
            _REQUEST_VALIDATION_RECIPE,
            "fastapi.request-validation-wave.query-string-validation.test-query-params-str-validations-q-too-long",
            "dispatch",
        ),
        "test_openapi_schema": _ref(
            _T002_RECIPE,
            "fastapi.query-validation.tutorial002-openapi-max-length",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial003.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial003-omitted-valid-max-openapi",
            "omitted-query",
        ),
        "test_query_params_str_validations_q_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial003-omitted-valid-max-openapi",
            "valid-query",
        ),
        "test_query_params_str_validations_q_too_short": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial003-length-bounds",
            "below-minimum-length",
        ),
        "test_query_params_str_validations_q_too_long": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial003-omitted-valid-max-openapi",
            "above-maximum-query-length",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial003-omitted-valid-max-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial004.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial004-omitted-valid-openapi",
            "omitted-query",
        ),
        "test_query_params_str_validations_q_fixedquery": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial004-omitted-valid-openapi",
            "accepted-pattern-query",
        ),
        "test_query_params_str_validations_q_nonregexquery": _ref(
            _TEN_MODULE_RECIPE, "fastapi.query-validation.tutorial004-pattern", "pattern-mismatch"
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial004-omitted-valid-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial005.py": {
        "test_query_params_str_validations_no_query": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial005-default-value",
            "omitted-query-uses-default",
        ),
        "test_query_params_str_validations_q_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial005-valid-short-openapi",
            "valid-query",
        ),
        "test_query_params_str_validations_q_short": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial005-valid-short-openapi",
            "below-minimum-query-length",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial005-valid-short-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial006.py": {
        "test_query_params_str_validations_no_query": _ref(
            _T006_RECIPE,
            "fastapi.query-validation.tutorial006-required-query-missing",
            "missing-required-query",
        ),
        "test_query_params_str_validations_q_fixedquery": _ref(
            _REQUEST_PARAMETER_RECIPE,
            "fastapi.request-parameter-openapi-wave.query-length.test-query-params-str-validations-q-fixedquery",
            "dispatch",
        ),
        "test_query_params_str_validations_q_fixedquery_too_short": _ref(
            _REQUEST_PARAMETER_RECIPE,
            "fastapi.request-parameter-openapi-wave.query-length.test-query-params-str-validations-q-fixedquery-too-short",
            "dispatch",
        ),
        "test_openapi_schema": _ref(
            _REQUEST_PARAMETER_RECIPE,
            "fastapi.request-parameter-openapi-wave.query-length.test-openapi-schema",
            "dispatch",
        ),
    },
    "test_tutorial006c.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial006c-omitted-empty-valid-openapi",
            "omitted-query-xfail",
        ),
        "test_query_params_str_validations_empty_str": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial006c-omitted-empty-valid-openapi",
            "empty-query-xfail",
        ),
        "test_query_params_str_validations_q_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial006c-omitted-empty-valid-openapi",
            "valid-query",
        ),
        "test_query_params_str_validations_q_short": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial006c-required-minimum",
            "too-short-query",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial006c-omitted-empty-valid-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial007.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial007-omitted-valid-openapi",
            "omitted-query",
        ),
        "test_query_params_str_validations_q_fixedquery": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial007-omitted-valid-openapi",
            "valid-query",
        ),
        "test_query_params_str_validations_q_fixedquery_too_short": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial007-title-and-minimum",
            "too-short-titled-query",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial007-omitted-valid-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial008.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial008-omitted-valid-openapi",
            "omitted-query",
        ),
        "test_query_params_str_validations_q_fixedquery": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial008-omitted-valid-openapi",
            "valid-query",
        ),
        "test_query_params_str_validations_q_fixedquery_too_short": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial008-description-and-minimum",
            "too-short-described-query",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial008-omitted-valid-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial009.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE, "fastapi.query-validation.tutorial009-omitted-openapi", "omitted-query"
        ),
        "test_query_params_str_validations_item_query_fixedquery": _ref(
            _TEN_MODULE_RECIPE, "fastapi.query-validation.tutorial009-alias", "public-alias-value"
        ),
        "test_query_params_str_validations_q_fixedquery": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial009-alias",
            "python-name-is-not-public-alias",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial009-omitted-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial010.py": {
        "test_query_params_str_validations_no_query": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial010-omitted-wrong-name-openapi",
            "omitted-query",
        ),
        "test_query_params_str_validations_item_query_fixedquery": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial010-deprecated-pattern-alias",
            "valid-public-alias",
        ),
        "test_query_params_str_validations_q_fixedquery": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial010-omitted-wrong-name-openapi",
            "python-name-is-not-alias",
        ),
        "test_query_params_str_validations_item_query_nonregexquery": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial010-deprecated-pattern-alias",
            "alias-value-fails-pattern",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial010-omitted-wrong-name-openapi",
            "openapi-query-parameter",
        ),
    },
    "test_tutorial011.py": {
        "test_multi_query_values": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.multi-query-values.test-multi-query-values",
            "dispatch",
        ),
        "test_query_no_values": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.multi-query-values.test-query-no-values",
            "dispatch",
        ),
        "test_openapi_schema": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.multi-query-values.test-openapi-schema",
            "dispatch",
        ),
    },
    "test_tutorial012.py": {
        "test_default_query_values": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.default-query-values.test-default-query-values",
            "dispatch",
        ),
        "test_multi_query_values": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.default-query-values.test-multi-query-values",
            "dispatch",
        ),
        "test_openapi_schema": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.default-query-values.test-openapi-schema",
            "dispatch",
        ),
    },
    "test_tutorial013.py": {
        "test_multi_query_values": _ref(
            _TAIL_RECIPE,
            "fastapi.request-parameter-tail-wave.repeated-query.test-multi-query-values",
            "dispatch",
        ),
        "test_query_no_values": _ref(
            _TAIL_RECIPE,
            "fastapi.request-parameter-tail-wave.repeated-query.test-query-no-values",
            "dispatch",
        ),
        "test_openapi_schema": _ref(
            _TAIL_RECIPE,
            "fastapi.request-parameter-tail-wave.repeated-query.test-openapi-schema",
            "dispatch",
        ),
    },
    "test_tutorial014.py": {
        "test_hidden_query": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.hidden-query.test-hidden-query",
            "dispatch",
        ),
        "test_no_hidden_query": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.hidden-query.test-no-hidden-query",
            "dispatch",
        ),
        "test_openapi_schema": _ref(
            _EDGE_RECIPE,
            "fastapi.request-parameter-edges-wave.hidden-query.test-openapi-schema",
            "dispatch",
        ),
    },
    "test_tutorial015.py": {
        "test_get_random_item": {
            "mapping_status": "source-backed-exclusion",
            "reason": "The test omits the query parameter and asserts random.choice-driven application data; it does not exercise a query-value validation branch, and no stable expected response can be compared.",
        },
        "test_get_item": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial015-valid-unknown-openapi",
            "recognized-id",
        ),
        "test_get_item_does_not_exist": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial015-valid-unknown-openapi",
            "valid-format-unknown-id",
        ),
        "test_get_invalid_item": _ref(
            _TEN_MODULE_RECIPE,
            "fastapi.query-validation.tutorial015-custom-after-validator",
            "invalid-custom-id",
        ),
        "test_openapi_schema": _ref(
            _BRANCH_RECIPE,
            "fastapi.query-validation.tutorial015-valid-unknown-openapi",
            "openapi-query-parameter",
        ),
    },
}

_SPECIAL_GATES = {
    ("test_tutorial002.py", "test_query_params_str_validations_no_query"): (
        "The mapped /search input uses the same optional Query(max_length=50) field, but its response body differs from the tutorial's /items/ application; the case gates query default/validation behavior only.",
    ),
    ("test_tutorial002.py", "test_query_params_str_validations_q_empty_str"): (
        "The mapped /search input uses the same optional Query(max_length=50) field, but its response body differs from the tutorial's /items/ application; the case gates blank-value handling only.",
    ),
    ("test_tutorial002.py", "test_query_params_str_validations_q_query"): (
        "The mapped /search input uses the same optional Query(max_length=50) field, but its response body differs from the tutorial's /items/ application; the case gates query extraction only.",
    ),
    ("test_tutorial002.py", "test_query_params_str_validations_q_too_long"): (
        "The existing /search case exercises max_length=50 with the same 51-character input. It uses an independently authored endpoint and response body, so this is a query-validation-only mapping.",
    ),
    ("test_tutorial002.py", "test_openapi_schema"): (
        "The independent /search workflow selects the query parameter node, not the upstream full OpenAPI snapshot or /items/ path/operation metadata.",
    ),
    ("test_tutorial006.py", "test_query_params_str_validations_no_query"): (
        "The required-query workflow uses the same Query(min_length=3) constraint on /search; the route and response body differ from the source /items/ app.",
    ),
    ("test_tutorial006.py", "test_query_params_str_validations_q_fixedquery"): (
        "The existing /search workflow uses the same required Query(min_length=3) field, but returns a different response body than the tutorial app.",
    ),
    ("test_tutorial006.py", "test_query_params_str_validations_q_fixedquery_too_short"): (
        "The existing /search workflow uses the same required Query(min_length=3) field and fa input, but returns a different response body than the tutorial app.",
    ),
    ("test_tutorial006.py", "test_openapi_schema"): (
        "The existing /search workflow selects only its query parameter schema; the upstream test asserts the full /items/ OpenAPI document.",
    ),
    ("test_tutorial006c.py", "test_query_params_str_validations_no_query"): (
        "The upstream test is marked xfail because the example's omitted nullable query is invalid; the workflow records the request and actual response without treating the asserted 200 as a compatibility oracle.",
    ),
    ("test_tutorial006c.py", "test_query_params_str_validations_empty_str"): (
        "The upstream test is marked xfail because the example's empty constrained query is invalid; the workflow records the request and actual response without treating the asserted 200 as a compatibility oracle.",
    ),
    ("test_tutorial006c.py", "test_openapi_schema"): (
        "The selected OpenAPI parameter node is a focused schema sample, not the upstream full OpenAPI snapshot.",
    ),
    ("test_tutorial015.py", "test_get_item"): (
        "The workload uses a prefixed route with a trailing slash, while the upstream client requests /items without a slash; redirect behavior is outside this query-value mapping.",
    ),
    ("test_tutorial015.py", "test_get_item_does_not_exist"): (
        "The workload exercises the valid-prefix/unknown-ID lookup result, but its route is prefixed and slash-terminated; application lookup output is not a validation contract.",
    ),
    ("test_tutorial015.py", "test_get_invalid_item"): (
        "The independent workload recreates the custom prefix validator; the exact exception context comes from Pydantic 2.13.4 and remains a live-parity gate.",
    ),
    ("test_tutorial015.py", "test_openapi_schema"): (
        "The selected OpenAPI parameter node is a focused schema sample, not the upstream full OpenAPI snapshot.",
    ),
}


def _build_mappings() -> dict[str, dict[str, Any]]:
    recipe_index = _recipe_index()
    mappings: dict[str, dict[str, Any]] = {}
    for filename, plan in _PLANS.items():
        test_path = f"tests/test_tutorial/test_query_params_str_validations/{filename}"
        test_spans = _test_spans(test_path)
        if set(plan) != set(test_spans):
            raise ValueError(
                f"function plan differs from source test functions in {test_path}: "
                f"missing={sorted(set(test_spans) - set(plan))}; "
                f"extra={sorted(set(plan) - set(test_spans))}"
            )
        function_rows: dict[str, dict[str, Any]] = {}
        for function_name, assignment in plan.items():
            source_span = test_spans[function_name]
            if isinstance(assignment, dict):
                function_rows[function_name] = {
                    "mapping_status": "source-backed-exclusion",
                    "feature_ids": ["request-validation"],
                    "observation_selectors": [],
                    "source_span": source_span,
                    "supporting_sources": [
                        _fixture_source(test_path),
                        *(_doc_endpoint_sources(test_path)),
                        _src(
                            "docs_src/query_params_str_validations/tutorial015_an_py310.py",
                            26,
                            30,
                            "The omitted-id application branch calls random.choice over the local data mapping.",
                        ),
                    ],
                    "workflow_cases": [],
                    "exclusion_reason": assignment["reason"],
                    "contract_gates": list(_GLOBAL_GATES),
                }
                continue

            recipe_path, case_id, action_id = assignment
            case_row = recipe_index.get(case_id)
            if case_row is None or case_row["recipe_path"] != recipe_path:
                raise ValueError(f"case link is missing or has the wrong recipe: {case_id}")
            action = case_row["actions"].get(action_id)
            if action is None:
                raise ValueError(f"action {action_id} is missing from {case_id}")
            case_source_paths = {
                evidence.get("path")
                for evidence in case_row["case"].get("source_evidence", []) or []
                if evidence.get("kind") == "upstream_test"
            }
            if test_path not in case_source_paths:
                raise ValueError(f"case {case_id} does not cite {test_path}")
            selectors = _action_selectors(action)
            if not selectors:
                raise ValueError(f"case action has no observable selectors: {case_id}:{action_id}")
            is_openapi = function_name == "test_openapi_schema"
            features = (
                ["request-validation", "openapi-docs"] if is_openapi else ["request-validation"]
            )
            specific_gates = list(_SPECIAL_GATES.get((filename, function_name), ()))
            if filename in {
                "test_tutorial011.py",
                "test_tutorial012.py",
                "test_tutorial013.py",
            }:
                specific_gates.append(
                    "The request uses an independently named route in the workload while preserving the repeated/default query input; route naming and unrelated OpenAPI metadata are not source-test equivalence claims."
                )
            if filename == "test_tutorial014.py":
                specific_gates.append(
                    "The upstream HTTP tests request /items without a trailing slash and the workflow uses a prefixed /items/ route; Starlette redirect behavior and full path metadata remain gated."
                )
            if filename == "test_tutorial006c.py" and function_name not in {
                "test_openapi_schema",
            }:
                specific_gates.append(
                    "This input selects one direct Query declaration; the upstream test also parameterizes an Annotated form."
                )
            workflow_case = {
                "recipe_path": recipe_path,
                "case_id": case_id,
                "action_ids": [action_id],
                "observation_selectors": selectors,
                "mapping_scope": "query-input-and-selected-observations",
            }
            function_rows[function_name] = {
                "mapping_status": "mapped-partial",
                "feature_ids": features,
                "observation_selectors": selectors,
                "source_span": source_span,
                "supporting_sources": [
                    _fixture_source(test_path),
                    *_doc_endpoint_sources(test_path),
                    *_FASTAPI_SOURCES,
                    *_STARLETTE_SOURCES,
                ],
                "workflow_cases": [workflow_case],
                "rationale": (
                    "Maps this test's specific query input and selected HTTP or OpenAPI observation to an independently authored workflow action."
                ),
                "contract_gates": [*_GLOBAL_GATES, *specific_gates],
            }

        feature_ids = sorted(
            {feature for row in function_rows.values() for feature in row.get("feature_ids", [])}
        )
        selectors = sorted(
            {
                selector
                for row in function_rows.values()
                for selector in row.get("observation_selectors", [])
            }
        )
        mappings[test_path] = {
            "mapping_status": "mapped-partial",
            "feature_ids": feature_ids,
            "observation_selectors": selectors,
            "source_test_functions": list(test_spans),
            "source_doc_variants": list(_doc_variant_names(test_path)),
            "fixture_source_span": _fixture_source(test_path),
            "workflow_declaration_form": _WORKLOAD_DECLARATION_FORMS.get(
                filename, "direct Query declaration"
            ),
            "unrepresented_doc_variants": [
                variant
                for variant in _doc_variant_names(test_path)
                if ("_an_" in variant)
                != ("Annotated" in _WORKLOAD_DECLARATION_FORMS.get(filename, "direct Query"))
            ],
            "supporting_sources": [*_FASTAPI_SOURCES, *_STARLETTE_SOURCES],
            "function_mappings": function_rows,
            "ownership_boundaries": {
                "fastapi": "Query construction/inference, query-field grouping/extraction, validation location/error assembly, 422 response handling, and OpenAPI parameter assembly.",
                "pydantic": "Pinned 2.13.4 field validation, string constraints, AfterValidator, and schema generation.",
                "starlette": "Pinned 1.6.0 ASGI Request.query_params, URL query parsing/blank preservation, multidict behavior, response transport, and TestClient; the replacement's generic contract is Starlette-RS.",
            },
            "contract_gates": list(_GLOBAL_GATES),
        }
    return mappings


QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS = _build_mappings()


def _builder_review_mappings() -> dict[str, dict[str, Any]]:
    """Normalize source-backed rows to build_fastapi_compatibility_atlas.py's input shape."""
    normalized: dict[str, dict[str, Any]] = {}
    for test_path, module in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.items():
        functions: dict[str, dict[str, Any]] = {}
        for function_name, function in module["function_mappings"].items():
            if function["mapping_status"] == "source-backed-exclusion":
                continue
            links = function["workflow_cases"]
            notes = [
                f"{link['recipe_path']}::{link['case_id']} actions "
                f"{', '.join(link['action_ids'])}; observed selectors: "
                f"{', '.join(link['observation_selectors'])}"
                for link in links
            ]
            functions[function_name] = {
                "feature_ids": function["feature_ids"],
                "observation_selectors": function["observation_selectors"],
                "rationale": function["rationale"],
                "replace_features": True,
                "supporting_sources": [
                    function["source_span"],
                    *function["supporting_sources"],
                ],
                "stimulus_notes": "Input-only workflow links: " + "; ".join(notes) + ".",
                "contract_gate": "; ".join(function["contract_gates"]),
            }
        normalized[test_path] = {
            "feature_ids": module["feature_ids"],
            "module_observation_selectors": module["observation_selectors"],
            "rationale": "Source-reviewed query-string tutorial test module with function-level input-only workflow links.",
            "supporting_sources": module["supporting_sources"],
            "functions": functions,
        }
    return normalized


QUERY_STRING_VALIDATION_TUTORIAL_BUILDER_REVIEW_MAPPINGS = _builder_review_mappings()

QUERY_STRING_VALIDATION_TUTORIAL_FUNCTION_EXCLUSIONS = {
    test_path: {
        function_name: function["exclusion_reason"]
        for function_name, function in module["function_mappings"].items()
        if function["mapping_status"] == "source-backed-exclusion"
    }
    for test_path, module in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.items()
    if any(
        function["mapping_status"] == "source-backed-exclusion"
        for function in module["function_mappings"].values()
    )
}

QUERY_STRING_VALIDATION_TUTORIAL_FUNCTION_EXCLUSION_EVIDENCE = {
    test_path: {
        function_name: function["supporting_sources"]
        for function_name, function in module["function_mappings"].items()
        if function["mapping_status"] == "source-backed-exclusion"
    }
    for test_path, module in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.items()
    if any(
        function["mapping_status"] == "source-backed-exclusion"
        for function in module["function_mappings"].values()
    )
}

PACKAGE_INITIALIZER_EXCLUSION = {
    "path": "tests/test_tutorial/test_query_params_str_validations/__init__.py",
    "mapping_status": "source-backed-exclusion",
    "source_line_count": 0,
    "reason": "The pinned tutorial package initializer is an empty file and contains no test function or executable request-parameter behavior.",
}


def validate_query_string_validation_tutorial_mappings() -> list[str]:
    errors: list[str] = []
    manifest_path = PROJECT_ROOT / "tests/fixtures/manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    for name, repo_root, manifest_name in (
        ("fastapi", FASTAPI_ROOT, "fastapi"),
        ("starlette", STARLETTE_ROOT, "starlette"),
    ):
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        actual_commit = result.stdout.strip()
        expected_commit = SOURCE_IDENTITIES[name]["commit"]
        selected = manifest["selected_contracts"][manifest_name]
        if actual_commit != expected_commit or selected.get("commit") != expected_commit:
            errors.append(f"pinned source identity mismatch for {name}")
        if selected.get("version") != SOURCE_IDENTITIES[name]["version"]:
            errors.append(f"manifest version mismatch for {name}")
    if (
        manifest.get("selected_contracts", {}).get("pydantic", {}).get("version")
        != SOURCE_IDENTITIES["pydantic"]["version"]
    ):
        errors.append("manifest Pydantic version differs from the reviewed identity")
    expected_modules = {
        str(path.relative_to(FASTAPI_ROOT)) for path in TEST_ROOT.glob("test_tutorial*.py")
    }
    if set(QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS) != expected_modules:
        errors.append("module mapping does not cover exactly the 16 tutorial test modules")
    recipe_index = _recipe_index()
    function_count = 0
    case_link_count = 0
    for test_path, mapping in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.items():
        expected_spans = _test_spans(test_path)
        function_rows = mapping["function_mappings"]
        if set(function_rows) != set(expected_spans):
            errors.append(f"function denominator mismatch for {test_path}")
        for function_name, row in function_rows.items():
            function_count += 1
            source_span = row["source_span"]
            if source_span != expected_spans.get(function_name):
                errors.append(f"source span mismatch for {test_path}:{function_name}")
            source_lines = (FASTAPI_ROOT / test_path).read_text(encoding="utf-8").splitlines()
            if not (1 <= source_span["start_line"] <= source_span["end_line"] <= len(source_lines)):
                errors.append(f"source span is out of range for {test_path}:{function_name}")
            for source in row.get("supporting_sources", []):
                if source["path"].startswith("fastapi/"):
                    source_path = FASTAPI_ROOT / source["path"]
                elif source["path"].startswith("docs_src/"):
                    source_path = FASTAPI_ROOT / source["path"]
                elif source["path"].startswith("starlette/"):
                    source_path = STARLETTE_ROOT / source["path"]
                elif source["path"].startswith("tests/"):
                    source_path = FASTAPI_ROOT / source["path"]
                else:
                    errors.append(f"unknown source root in evidence {source['path']}")
                    continue
                if not source_path.is_file():
                    errors.append(f"missing evidence source {source_path}")
                    continue
                line_count = len(source_path.read_text(encoding="utf-8").splitlines())
                if not (1 <= source["start_line"] <= source["end_line"] <= line_count):
                    errors.append(f"invalid source evidence span {source}")
            if row["mapping_status"] == "source-backed-exclusion":
                if row.get("workflow_cases") or not row.get("exclusion_reason"):
                    errors.append(f"invalid exclusion mapping {test_path}:{function_name}")
                continue
            if row["mapping_status"] != "mapped-partial":
                errors.append(f"unexpected function mapping status {test_path}:{function_name}")
            if not row.get("workflow_cases"):
                errors.append(f"mapped function has no workflow case {test_path}:{function_name}")
                continue
            for workflow in row["workflow_cases"]:
                case_row = recipe_index.get(workflow["case_id"])
                if case_row is None:
                    errors.append(f"unknown workflow case {workflow['case_id']}")
                    continue
                if workflow["recipe_path"] != case_row["recipe_path"]:
                    errors.append(f"workflow recipe mismatch for {workflow['case_id']}")
                case_sources = {
                    evidence.get("path")
                    for evidence in case_row["case"].get("source_evidence", []) or []
                    if evidence.get("kind") == "upstream_test"
                }
                if test_path not in case_sources:
                    errors.append(
                        f"workflow case {workflow['case_id']} omits {test_path} source evidence"
                    )
                for action_id in workflow["action_ids"]:
                    case_link_count += 1
                    action = case_row["actions"].get(action_id)
                    if action is None:
                        errors.append(f"missing action {action_id} in {workflow['case_id']}")
                        continue
                    actual = set(_action_selectors(action))
                    declared = set(workflow["observation_selectors"])
                    if not declared <= actual:
                        errors.append(
                            f"selectors not observed by {workflow['case_id']}:{action_id}: {sorted(declared - actual)}"
                        )
        if mapping["mapping_status"] != "mapped-partial":
            errors.append(f"unexpected module mapping status {test_path}")
        builder_functions = QUERY_STRING_VALIDATION_TUTORIAL_BUILDER_REVIEW_MAPPINGS[test_path][
            "functions"
        ]
        expected_builder_functions = set(function_rows) - {
            name
            for name, row in function_rows.items()
            if row["mapping_status"] == "source-backed-exclusion"
        }
        if set(builder_functions) != expected_builder_functions:
            errors.append(f"builder adapter function denominator mismatch for {test_path}")
    if function_count != 65:
        errors.append(f"expected 65 test functions, found {function_count}")
    if case_link_count != 64:
        errors.append(f"expected 64 function-to-case links, found {case_link_count}")

    for recipe_name in (
        "query-string-validation-tutorial-branches.yaml",
        "query-string-validation-tutorial002-branches.yaml",
        "query-string-validation-tutorial006-required.yaml",
    ):
        path = RECIPE_ROOT / recipe_name
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("schema") != "fastapi-rs/python-asgi-workflow@2":
            errors.append(f"unsupported input-only recipe schema: {recipe_name}")
        forbidden = {
            "expected",
            "expected_output",
            "expected_outputs",
            "measurement",
            "measurements",
            "benchmark",
        }

        def scan(value: Any, location: str, forbidden_fields: set[str]) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if str(key).lower() in forbidden_fields:
                        errors.append(f"non-input field {key!r} in {location}")
                    scan(item, f"{location}.{key}", forbidden_fields)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    scan(item, f"{location}[{index}]", forbidden_fields)

        scan(data, recipe_name, forbidden)
        workload_path = data.get("workload", {}).get("file", "")
        if not (PROJECT_ROOT / workload_path).is_file():
            errors.append(f"missing recipe workload {workload_path}")
        for case in data.get("cases", []):
            for action in case.get("actions", []):
                scope = action.get("scope", {})
                if scope.get("type") != "http" or scope.get("method") not in {"GET", "HEAD"}:
                    errors.append(
                        f"unexpected request kind in {recipe_name}:{action.get('action_id')}"
                    )
                if not isinstance(scope.get("query_string"), str):
                    errors.append(
                        f"missing query-string input in {recipe_name}:{action.get('action_id')}"
                    )
                if (
                    len(scope.get("client", [])) != 2
                    or scope.get("client", [None])[0] != "127.0.0.1"
                ):
                    errors.append(
                        f"invalid ASGI client input in {recipe_name}:{action.get('action_id')}"
                    )
    initializer = FASTAPI_ROOT / PACKAGE_INITIALIZER_EXCLUSION["path"]
    if not initializer.is_file() or initializer.stat().st_size != 0:
        errors.append("package initializer is no longer an empty source-backed exclusion")
    return errors


if __name__ == "__main__":
    errors = validate_query_string_validation_tutorial_mappings()
    if errors:
        raise SystemExit("\n".join(errors))
    functions = sum(
        len(row["function_mappings"])
        for row in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.values()
    )
    links = sum(
        len(function["workflow_cases"])
        for module in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.values()
        for function in module["function_mappings"].values()
    )
    exclusions = sum(
        function["mapping_status"] == "source-backed-exclusion"
        for module in QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS.values()
        for function in module["function_mappings"].values()
    )
    print(
        f"validated {len(QUERY_STRING_VALIDATION_TUTORIAL_TEST_REVIEW_MAPPINGS)} modules, "
        f"{functions} test functions, {links} workflow links, {exclusions} function exclusion"
    )
