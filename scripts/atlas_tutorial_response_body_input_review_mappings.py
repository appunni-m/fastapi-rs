"""Reviewed inputs for response and request-body tutorial test modules.

The linked workflows are independently authored ASGI inputs with no stored
expected responses. FastAPI owns route integration, body-field interpretation,
validation locations, configured status selection, and OpenAPI projection.
Pydantic owns model validation and schema mechanics; Starlette 1.6.0 owns the
generic Request, TestClient, and response transport contracts.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT.parent / "fastapi"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic request, response-class, FileResponse, StreamingResponse, and TestClient contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned request/response model validation and schema dependency",
    },
}

__all__ = [
    "SOURCE_IDENTITIES",
    "TUTORIAL_RESPONSE_BODY_INPUT_REVIEW_MAPPINGS",
]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    return _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test inputs and assertions for {function_name}",
    )


def _link(
    recipe_path: str,
    case_id: str,
    action_ids: tuple[str, ...],
    selectors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _function(
    test_path: str,
    function_name: str,
    feature_ids: tuple[str, ...],
    selectors: tuple[str, ...],
    rationale: str,
    links: tuple[dict[str, Any], ...],
    gate: str,
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    links_note = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} actions "
        f"{', '.join(link['action_ids'])} ({', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "workflow_cases": list(links),
        "stimulus_notes": (
            "Independent input-only workflow links: "
            + links_note
            + ". The recipes contain no expected outputs or copied upstream test bodies."
        ),
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _excluded(test_path: str, function_name: str, reason: str) -> dict[str, Any]:
    return {
        "review_status": "reviewed_excluded",
        "feature_ids": [],
        "observation_selectors": [],
        "exclusion_reason": reason,
        "supporting_sources": [_test_span(test_path, function_name)],
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
    module_sources: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    links_by_key: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    sources_by_key: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in functions.values():
        for link in row.get("workflow_cases", []):
            key = (link["recipe_path"], link["case_id"], tuple(link["action_ids"]))
            links_by_key.setdefault(key, link)
        for source in row.get("supporting_sources", []):
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources_by_key.setdefault(key, source)
    for source in module_sources:
        key = (
            source["path"],
            source.get("start_line", 0),
            source.get("end_line", 0),
            source["role"],
        )
        sources_by_key.setdefault(key, source)
    links = list(links_by_key.values())
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
        "functions": functions,
        "workflow_cases": links,
        "supporting_sources": list(sources_by_key.values()),
        "module_observation_selectors": sorted(
            {selector for row in functions.values() for selector in row["observation_selectors"]}
        ),
        "stimulus_notes": (
            "Source-reviewed partial workflow mapping. FastAPI owns route-level "
            "body/status integration and OpenAPI projection; Pydantic owns model "
            "validation/schema mechanics, and Starlette 1.6.0 owns generic ASGI "
            "request/response and TestClient behavior."
        ),
    }


_ADDITIONAL_INPUT = "tests/fixtures/input-recipes/parity/additional-responses.yaml"
_ADDITIONAL_OPENAPI = "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml"
_ADDITIONAL_FILE = (
    "tests/fixtures/input-recipes/parity/tutorial-additional-responses-file-response-review.yaml"
)
_STATUS_INPUT = "tests/fixtures/input-recipes/parity/additional-status-codes-tutorial-upstream.yaml"
_CUSTOM001 = "tests/fixtures/input-recipes/parity/custom-response-tutorial001-upstream.yaml"
_CUSTOM002 = "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml"
_CUSTOM003 = "tests/fixtures/input-recipes/parity/custom-response-tutorial003-upstream.yaml"
_CUSTOM004 = "tests/fixtures/input-recipes/parity/custom-response-tutorial004-upstream.yaml"
_STARLETTE_RESPONSE = "tests/fixtures/input-recipes/parity/starlette-response-runtime-upstream.yaml"
_RESPONSE_MODEL = "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml"
_RESPONSE_MODEL_ERROR = (
    "tests/fixtures/input-recipes/parity/tutorial-response-model003_04-construction-review.yaml"
)
_RESPONSE_STATUS = (
    "tests/fixtures/input-recipes/parity/tutorial-response-status-code001-source-review.yaml"
)
_BODY001 = "tests/fixtures/input-recipes/parity/tutorial-body001-source-review.yaml"
_BODY_FIELDS001 = "tests/fixtures/input-recipes/parity/tutorial-body-fields001-source-review.yaml"
_BODY002 = "tests/fixtures/input-recipes/parity/pydantic-request-body-wave.yaml"
_BODY003 = "tests/fixtures/input-recipes/parity/body-tutorial003-model-upstream.yaml"
_BODY004 = "tests/fixtures/input-recipes/parity/body-tutorial004-model-upstream.yaml"

_JSON_RESPONSE = ("http.status", "http.body.json")
_BYTE_RESPONSE = ("http.status", "http.body.bytes")
_OPENAPI_RESPONSE = ("http.status", "openapi.document")

_BODY_PARSE = (
    _source(
        "fastapi/routing.py",
        425,
        473,
        "FastAPI reads request-body bytes, decides whether the media type is JSON, parses JSON, and converts parser failures",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        951,
        998,
        "FastAPI validates model/body fields and composes body-location errors",
    ),
    _source(
        "fastapi/routing.py",
        751,
        755,
        "FastAPI raises RequestValidationError for body and dependency validation errors",
    ),
    _source(
        "fastapi/exception_handlers.py",
        20,
        26,
        "FastAPI serializes request-validation errors as 422 JSON responses",
    ),
)
_BODY_REQUEST_CONTRACT = (
    _source(
        "starlette/requests.py",
        234,
        266,
        "Starlette 1.6.0 consumes ASGI request chunks and decodes request.json()",
    ),
    _source(
        "starlette/requests.py",
        268,
        311,
        "Starlette 1.6.0 parses form content types into FormData",
    ),
)
_BODY_OPENAPI = (
    _source(
        "fastapi/openapi/utils.py",
        231,
        263,
        "FastAPI projects a route body field into the OpenAPI requestBody schema and required flag",
    ),
    _source(
        "fastapi/openapi/utils.py",
        331,
        385,
        "FastAPI includes parameters and requestBody fields in OpenAPI operations",
    ),
    _source(
        "fastapi/openapi/utils.py",
        517,
        533,
        "FastAPI adds the default request-validation response when an operation has parameters or a body",
    ),
    _source(
        "fastapi/openapi/utils.py",
        325,
        330,
        "FastAPI selects the route response class and its media type for OpenAPI generation",
    ),
    _source(
        "fastapi/openapi/utils.py",
        456,
        472,
        "FastAPI projects the response field into the selected response media type schema",
    ),
)
_BODY_FIELD_EMBED = (
    _source(
        "fastapi/dependencies/utils.py",
        1001,
        1048,
        "FastAPI builds the body model used to embed body fields and generate its schema",
    ),
    *_BODY_PARSE,
    *_BODY_OPENAPI,
)
_ROUTE_RESPONSE = (
    _source(
        "fastapi/routing.py",
        375,
        400,
        "FastAPI selects the configured response class for a route",
    ),
    _source(
        "fastapi/routing.py",
        711,
        750,
        "FastAPI preserves a returned Response instance or serializes endpoint output through the selected response class",
    ),
)
_ROUTE_STATUS = (
    _source(
        "fastapi/routing.py",
        357,
        372,
        "FastAPI combines configured status with dependency-mutated Response status when constructing a response",
    ),
    _source(
        "fastapi/routing.py",
        1029,
        1034,
        "FastAPI stores the normalized route status code",
    ),
    _source(
        "fastapi/openapi/utils.py",
        403,
        418,
        "FastAPI documents the route's configured status code in OpenAPI",
    ),
)
_OPENAPI_DOCUMENT = (
    _source(
        "fastapi/openapi/utils.py",
        585,
        647,
        "FastAPI generates the OpenAPI document from registered route contexts",
    ),
)
_ADDITIONAL_RESPONSES = (
    _source(
        "fastapi/openapi/utils.py",
        325,
        330,
        "FastAPI selects a route response class and media type for OpenAPI generation",
    ),
    _source(
        "fastapi/openapi/utils.py",
        456,
        472,
        "FastAPI projects default response media types and response fields into OpenAPI",
    ),
    _source(
        "fastapi/openapi/utils.py",
        473,
        516,
        "FastAPI merges additional response definitions and model schemas into an operation",
    ),
    *_OPENAPI_DOCUMENT,
)
_INFERRED_RESPONSE_MODEL = (
    _source(
        "fastapi/routing.py",
        1081,
        1113,
        "FastAPI infers response models from return annotations and constructs response fields unless the annotation is a Response subclass",
    ),
    _source(
        "fastapi/utils.py",
        58,
        77,
        "FastAPI converts unsupported Pydantic schema-generation failures into FastAPIError",
    ),
)
_STARLETTE_RESPONSE_RUNTIME = (
    _source(
        "starlette/responses.py",
        33,
        81,
        "Starlette 1.6.0 renders generic response bodies and initializes content headers",
    ),
    _source(
        "starlette/responses.py",
        163,
        168,
        "Starlette 1.6.0 sends the HTTP response start and body over ASGI",
    ),
)
_FASTAPI_UJSON_RESPONSE = (
    _source(
        "fastapi/responses.py",
        39,
        66,
        "FastAPI UJSONResponse is deprecated and renders JSON through its optional ujson dependency",
    ),
)
_APP_DEFAULT_RESPONSE_CLASS = (
    _source(
        "fastapi/applications.py",
        353,
        372,
        "FastAPI configures JSONResponse as the app-level default response class unless overridden",
    ),
)
_RESPONSE_CLASS_OPENAPI = (
    _source(
        "fastapi/openapi/utils.py",
        325,
        330,
        "FastAPI resolves the route's response class and media type for OpenAPI generation",
    ),
    _source(
        "fastapi/openapi/utils.py",
        456,
        472,
        "FastAPI emits the selected response-class media type and schema",
    ),
)
_STARLETTE_FILE = (
    _source(
        "starlette/responses.py",
        296,
        339,
        "Starlette 1.6.0 FileResponse infers content type and initializes file metadata headers",
    ),
    _source(
        "starlette/responses.py",
        341,
        400,
        "Starlette 1.6.0 FileResponse validates a path and transfers file bytes over ASGI",
    ),
)
_STARLETTE_STREAM = (
    _source(
        "starlette/responses.py",
        222,
        255,
        "Starlette 1.6.0 adapts streaming iterables and emits response chunks",
    ),
    _source(
        "starlette/responses.py",
        257,
        276,
        "Starlette 1.6.0 dispatches a StreamingResponse over ASGI",
    ),
)
_TESTCLIENT = (
    _source(
        "starlette/testclient.py",
        327,
        374,
        "Starlette 1.6.0 TestClient captures ASGI status, headers, and response bytes",
    ),
    _source(
        "starlette/testclient.py",
        377,
        420,
        "Starlette 1.6.0 configures the TestClient transport and redirect policy",
    ),
)


def _one(
    recipe: str,
    case_id: str,
    action_id: str,
    selectors: tuple[str, ...],
) -> dict[str, Any]:
    return _link(recipe, case_id, (action_id,), selectors)


def _body001(action_id: str, selectors: tuple[str, ...] = _JSON_RESPONSE) -> dict[str, Any]:
    return _one(
        _BODY001,
        "fastapi.tutorial-body001.input-and-openapi-matrix",
        action_id,
        selectors,
    )


_TUTORIAL_ROOT = "tests/test_tutorial/"
_ADDITIONAL_ROOT = _TUTORIAL_ROOT + "test_additional_responses/"
_CUSTOM_ROOT = _TUTORIAL_ROOT + "test_custom_response/"
_BODY_ROOT = _TUTORIAL_ROOT + "test_body/"


TUTORIAL_RESPONSE_BODY_INPUT_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    _ADDITIONAL_ROOT + "test_tutorial001.py": _module(
        "The module checks a successful item, an additional 404 response, and the generated response schema.",
        {
            "test_path_operation": _function(
                _ADDITIONAL_ROOT + "test_tutorial001.py",
                "test_path_operation",
                ("response-serialization",),
                _JSON_RESPONSE,
                "A successful request returns a response-model item as JSON.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.found",
                        "get-existing-stock",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The independent input exercises the same successful modeled-response path with another route and item. The source compares decoded JSON; the recipe captures raw ASGI body bytes, so the mapping is partial and does not claim byte-for-byte equality with the source payload.",
                (*_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_path_operation_not_found": _function(
                _ADDITIONAL_ROOT + "test_tutorial001.py",
                "test_path_operation_not_found",
                ("response-serialization",),
                _JSON_RESPONSE,
                "A missing item uses the documented additional 404 response model.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.not-found",
                        "get-missing-stock",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The fixture sends an independent missing-key request and selects status/body; it uses a different route, payload, and model name than the tutorial source.",
                (*_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _ADDITIONAL_ROOT + "test_tutorial001.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot checks the declared 200 model response, additional 404 model response, and validation response.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.openapi",
                        "read-stock-openapi",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The linked input selects response/schema references from a different but equivalent additional-response operation; it does not compare the full source snapshot or its exact names and descriptions.",
                _ADDITIONAL_RESPONSES,
            ),
        },
    ),
    _ADDITIONAL_ROOT + "test_tutorial002.py": _module(
        "The module checks normal item JSON, a conditional PNG FileResponse, and OpenAPI media content for the JSON/image response variants.",
        {
            "test_path_operation": _function(
                _ADDITIONAL_ROOT + "test_tutorial002.py",
                "test_path_operation",
                ("response-serialization",),
                _JSON_RESPONSE,
                "The route's non-image branch returns the modeled item JSON response.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.found",
                        "get-existing-stock",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The independent input uses a different route, item, and model while sampling a successful JSON branch; it does not prove the tutorial's selected item values.",
                (*_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_path_operation_img": _function(
                _ADDITIONAL_ROOT + "test_tutorial002.py",
                "test_path_operation_img",
                ("response-serialization",),
                ("http.status", "http.headers.ordered", "http.body.bytes"),
                "The image query branch returns a PNG FileResponse with a nonempty body.",
                (
                    _one(
                        _ADDITIONAL_FILE,
                        "fastapi.tutorial-additional-responses.file-response",
                        "return-file-response",
                        ("http.status", "http.headers.ordered", "http.body.bytes"),
                    ),
                ),
                "The recipe uses a deterministic independent file payload. It compares all ordered headers and exact bytes, which is stricter than the source's Content-Type lookup and nonempty-body predicate; file metadata, transfer, and TestClient behavior are Starlette 1.6.0 contracts.",
                (*_ROUTE_RESPONSE, *_STARLETTE_FILE, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _ADDITIONAL_ROOT + "test_tutorial002.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot checks JSON plus image/png content for the default response.",
                (
                    _one(
                        _ADDITIONAL_OPENAPI,
                        "fastapi.additional-response-openapi-wave.media-content.test-openapi-schema",
                        "dispatch",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The OpenAPI workflow selects the whole response object for a different route; the source's parameters, operation metadata, component references, and full document snapshot are outside this selector.",
                _ADDITIONAL_RESPONSES,
            ),
        },
    ),
    _ADDITIONAL_ROOT + "test_tutorial003.py": _module(
        "The module checks the modeled additional 404 response and example-bearing OpenAPI response documentation.",
        {
            "test_path_operation": _function(
                _ADDITIONAL_ROOT + "test_tutorial003.py",
                "test_path_operation",
                ("response-serialization",),
                _JSON_RESPONSE,
                "A successful item request returns the response model as JSON.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.found",
                        "get-existing-stock",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The workflow exercises the same success path with independent endpoint and data values; it does not claim source payload equality.",
                (*_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_path_operation_not_found": _function(
                _ADDITIONAL_ROOT + "test_tutorial003.py",
                "test_path_operation_not_found",
                ("response-serialization",),
                _JSON_RESPONSE,
                "An unknown item returns the endpoint's additional not-found response.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.not-found",
                        "get-missing-stock",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The recipe observes an equivalent missing-key JSON response using another path and model name.",
                (*_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _ADDITIONAL_ROOT + "test_tutorial003.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot checks a model-backed 404 response plus a 200 response with an example.",
                (
                    _one(
                        _ADDITIONAL_OPENAPI,
                        "fastapi.additional-response-openapi-wave.modeled-not-found.test-openapi-schema",
                        "dispatch",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The independent operation has the same modeled-404 and response-example shape but different paths, models, example values, and descriptions; only the response object is selected, not the full snapshot.",
                _ADDITIONAL_RESPONSES,
            ),
        },
    ),
    _ADDITIONAL_ROOT + "test_tutorial004.py": _module(
        "The module checks the normal JSON item path, its conditional PNG FileResponse, and multiple additional status responses in OpenAPI.",
        {
            "test_path_operation": _function(
                _ADDITIONAL_ROOT + "test_tutorial004.py",
                "test_path_operation",
                ("response-serialization",),
                _JSON_RESPONSE,
                "The route's ordinary branch returns the item model as JSON.",
                (
                    _one(
                        _ADDITIONAL_INPUT,
                        "fastapi.docs.additional-responses.found",
                        "get-existing-stock",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The workflow covers a successful JSON model response with independent route and item values.",
                (*_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_path_operation_img": _function(
                _ADDITIONAL_ROOT + "test_tutorial004.py",
                "test_path_operation_img",
                ("response-serialization",),
                ("http.status", "http.headers.ordered", "http.body.bytes"),
                "The image query selects a PNG FileResponse and the test checks its media type and nonempty body.",
                (
                    _one(
                        _ADDITIONAL_FILE,
                        "fastapi.tutorial-additional-responses.file-response",
                        "return-file-response",
                        ("http.status", "http.headers.ordered", "http.body.bytes"),
                    ),
                ),
                "The independent fixture fixes file bytes and mtime; its full header and body comparisons are stronger than the source's selected Content-Type and nonempty-body checks. FileResponse and TestClient transport are Starlette 1.6.0 behavior.",
                (*_ROUTE_RESPONSE, *_STARLETTE_FILE, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _ADDITIONAL_ROOT + "test_tutorial004.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot checks documented 404, 302, and 403 responses plus the JSON/image 200 media types.",
                (
                    _one(
                        _ADDITIONAL_OPENAPI,
                        "fastapi.additional-response-openapi-wave.multiple-statuses.test-openapi-schema",
                        "dispatch",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The linked response object represents the same response-code/media-type matrix with different content and descriptions; it is not a full source snapshot comparison.",
                _ADDITIONAL_RESPONSES,
            ),
        },
    ),
    _TUTORIAL_ROOT + "test_additional_status_codes/test_tutorial001.py": _module(
        "The tutorial selects HTTP 200 for an update and HTTP 201 for a newly created item.",
        {
            "test_update": _function(
                _TUTORIAL_ROOT + "test_additional_status_codes/test_tutorial001.py",
                "test_update",
                ("response-serialization",),
                ("http.status",),
                "Updating an existing key returns its record with the default success status.",
                (
                    _one(
                        _STATUS_INPUT,
                        "fastapi.additional-status-codes.tutorial-update-existing",
                        "update-existing-record",
                        ("http.status",),
                    ),
                ),
                "The fixture uses a different record key and supplies a size value; it covers the existing-key branch and 200 status only, not the source's omitted-size default or its asserted JSON object.",
                (*_ROUTE_STATUS, *_ROUTE_RESPONSE, *_STARLETTE_RESPONSE_RUNTIME),
            ),
            "test_create": _function(
                _TUTORIAL_ROOT + "test_additional_status_codes/test_tutorial001.py",
                "test_create",
                ("response-serialization",),
                ("http.status",),
                "An unknown key returns a direct JSONResponse with status 201.",
                (
                    _one(
                        _STATUS_INPUT,
                        "fastapi.additional-status-codes.tutorial-create-new",
                        "create-record",
                        ("http.status",),
                    ),
                ),
                "The fixture supplies a size value whereas the source omits it and asserts size null; it covers the create branch and 201 status only, not the source JSON object. FastAPI preserves the returned Response, while JSON byte rendering and ASGI emission are Starlette 1.6.0 behavior.",
                (*_ROUTE_STATUS, *_ROUTE_RESPONSE, *_STARLETTE_RESPONSE_RUNTIME),
            ),
        },
    ),
    _CUSTOM_ROOT + "test_tutorial001.py": _module(
        "The module checks a configured UJSONResponse route, JSON output, and response-class OpenAPI projection.",
        {
            "test_get_custom_response": _function(
                _CUSTOM_ROOT + "test_tutorial001.py",
                "test_get_custom_response",
                ("response-serialization",),
                _JSON_RESPONSE,
                "The route's UJSONResponse class serializes the returned list, and the assertion compares decoded JSON.",
                (
                    _one(
                        _CUSTOM001,
                        "fastapi.custom-response.tutorial001.items-response",
                        "items",
                        _JSON_RESPONSE,
                    ),
                ),
                "The independent route returns the same JSON object but the recipe captures exact raw bytes; the source's JSON decoder ignores formatting. The upstream warning filter and deprecation warning are not represented as workflow observations.",
                (
                    *_FASTAPI_UJSON_RESPONSE,
                    *_ROUTE_RESPONSE,
                    *_STARLETTE_RESPONSE_RUNTIME,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                _CUSTOM_ROOT + "test_tutorial001.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The exact snapshot checks the response media type and empty response schema for the configured JSON response class.",
                (
                    _one(
                        _CUSTOM001,
                        "fastapi.custom-response.tutorial001.openapi",
                        "openapi",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The workflow selects the independent operation's OpenAPI paths/info sections rather than the entire document; it does not observe deprecation warnings.",
                (*_OPENAPI_DOCUMENT, *_ROUTE_RESPONSE, *_RESPONSE_CLASS_OPENAPI),
            ),
        },
    ),
    _CUSTOM_ROOT + "test_tutorial002_tutorial003_tutorial004.py": _module(
        "The parametrized tests compare HTMLResponse class selection, direct HTMLResponse returns, and response-class OpenAPI media types.",
        {
            "test_get_custom_response": _function(
                _CUSTOM_ROOT + "test_tutorial002_tutorial003_tutorial004.py",
                "test_get_custom_response",
                ("response-serialization",),
                _BYTE_RESPONSE,
                "The test compares the exact HTML text returned across declared-class and direct-response variants.",
                (
                    _one(
                        _CUSTOM002,
                        "fastapi.custom-response.tutorial002.items-response",
                        "items",
                        _BYTE_RESPONSE,
                    ),
                    _one(
                        _CUSTOM003,
                        "fastapi.custom-response.tutorial003.items-response",
                        "items",
                        _BYTE_RESPONSE,
                    ),
                    _one(
                        _CUSTOM004,
                        "fastapi.custom-response.tutorial004.items-response",
                        "items",
                        _BYTE_RESPONSE,
                    ),
                ),
                "All three inputs return the tutorial HTML content through their corresponding route forms. ASGI body bytes are compared; HTML text decoding, response headers, and TestClient behavior belong to Starlette 1.6.0.",
                (*_ROUTE_RESPONSE, *_STARLETTE_RESPONSE_RUNTIME, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _CUSTOM_ROOT + "test_tutorial002_tutorial003_tutorial004.py",
                "test_openapi_schema",
                ("openapi-docs", "response-serialization"),
                _OPENAPI_RESPONSE,
                "The parameterized snapshot distinguishes declared HTMLResponse media type from an undeclared direct Response return.",
                (
                    _one(
                        _CUSTOM002,
                        "fastapi.custom-response.tutorial002.openapi",
                        "openapi",
                        _OPENAPI_RESPONSE,
                    ),
                    _one(
                        _CUSTOM003,
                        "fastapi.custom-response.tutorial003.openapi",
                        "openapi",
                        _OPENAPI_RESPONSE,
                    ),
                    _one(
                        _CUSTOM004,
                        "fastapi.custom-response.tutorial004.openapi",
                        "openapi",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The input recipes separately select all three variants' paths/info sections; their sample OpenAPI results cover the route-class distinction but do not compare the full source snapshot or every parameterized test fixture object.",
                (*_ROUTE_RESPONSE, *_OPENAPI_DOCUMENT, *_RESPONSE_CLASS_OPENAPI),
            ),
        },
    ),
    _CUSTOM_ROOT + "test_tutorial005.py": _module(
        "The test checks a PlainTextResponse body's decoded text and the inferred text/plain OpenAPI response schema.",
        {
            "test_get": _function(
                _CUSTOM_ROOT + "test_tutorial005.py",
                "test_get",
                ("response-serialization",),
                _BYTE_RESPONSE,
                "The declared PlainTextResponse route emits the expected plain-text body.",
                (
                    _one(
                        _STARLETTE_RESPONSE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-get",
                        "request",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The input uses the same plain-text payload at an independent /plain route (the source route is /). It observes raw bytes, stricter than the source's decoded response.text equality; response encoding and TestClient behavior are Starlette 1.6.0 contracts.",
                (*_ROUTE_RESPONSE, *_STARLETTE_RESPONSE_RUNTIME, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _CUSTOM_ROOT + "test_tutorial005.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The exact snapshot checks the plain-text media type and inferred string schema.",
                (
                    _one(
                        _STARLETTE_RESPONSE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-openapi-schema",
                        "request",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The recipe selects the independent /plain operation's OpenAPI response fields but not the full source snapshot; its path differs from the source root route.",
                (*_ROUTE_RESPONSE, *_OPENAPI_DOCUMENT, *_RESPONSE_CLASS_OPENAPI),
            ),
        },
    ),
    _CUSTOM_ROOT + "test_tutorial007.py": _module(
        "The test compares the concatenated response bytes from ten StreamingResponse chunks.",
        {
            "test_get": _function(
                _CUSTOM_ROOT + "test_tutorial007.py",
                "test_get",
                ("response-serialization",),
                ("http.body.bytes",),
                "The function checks that a streamed body consists of ten repetitions of the supplied byte chunk.",
                (
                    _one(
                        _STARLETTE_RESPONSE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial007.test-get",
                        "request",
                        ("http.body.bytes",),
                    ),
                ),
                "The independent workload exercises StreamingResponse and emits ten chunks, but uses a different chunk payload. The workflow captures the concatenated body, not chunk boundaries or sleeps; streaming ASGI semantics and TestClient aggregation are Starlette 1.6.0 behavior.",
                (*_ROUTE_RESPONSE, *_STARLETTE_STREAM, *_TESTCLIENT),
            ),
        },
    ),
    _CUSTOM_ROOT + "test_tutorial010.py": _module(
        "The module checks app-level default HTMLResponse selection, body text, and its OpenAPI text/html media type.",
        {
            "test_get_custom_response": _function(
                _CUSTOM_ROOT + "test_tutorial010.py",
                "test_get_custom_response",
                ("response-serialization",),
                _BYTE_RESPONSE,
                "The app-level default response class renders a route's HTML string.",
                (
                    _one(
                        _STARLETTE_RESPONSE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial010.test-get-custom-response",
                        "request",
                        _BYTE_RESPONSE,
                    ),
                ),
                "The independent input selects the same route and HTML response class but uses different example markup; exact byte equality is stronger than the source's text comparison. FastAPI owns default response-class selection, and Starlette 1.6.0 owns encoding and transport.",
                (
                    *_APP_DEFAULT_RESPONSE_CLASS,
                    *_ROUTE_RESPONSE,
                    *_STARLETTE_RESPONSE_RUNTIME,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                _CUSTOM_ROOT + "test_tutorial010.py",
                "test_openapi_schema",
                ("openapi-docs", "response-serialization"),
                _OPENAPI_RESPONSE,
                "The snapshot checks that the app-level HTML default appears as text/html in the generated response schema.",
                (
                    _one(
                        _STARLETTE_RESPONSE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial010.test-openapi-schema",
                        "request",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The linked observation selects this operation's OpenAPI response fields but not the full source snapshot.",
                (
                    *_APP_DEFAULT_RESPONSE_CLASS,
                    *_ROUTE_RESPONSE,
                    *_OPENAPI_DOCUMENT,
                    *_RESPONSE_CLASS_OPENAPI,
                ),
            ),
        },
    ),
    _TUTORIAL_ROOT + "test_response_model/test_tutorial003_04.py": _module(
        "The test expects FastAPIError while registering a route whose Response | dict return annotation cannot be inferred as a response model.",
        {
            "test_invalid_response_model": _function(
                _TUTORIAL_ROOT + "test_response_model/test_tutorial003_04.py",
                "test_invalid_response_model",
                ("public-api-errors", "response-serialization"),
                ("construction.outcome", "construction.exception_class"),
                "The route-registration failure is observed as a construction exception; the source asserts the exception class FastAPIError.",
                (
                    _link(
                        _RESPONSE_MODEL_ERROR,
                        "fastapi.tutorial-response-model003-04.invalid-union-return-annotation",
                        (),
                        ("construction.outcome", "construction.exception_class"),
                    ),
                ),
                "The isolated factory independently declares Response | dict and records the generated error message as extra evidence; only outcome and exception class correspond to source assertions. Pydantic's schema-generation exception is translated to FastAPIError by FastAPI.",
                _INFERRED_RESPONSE_MODEL,
            ),
        },
    ),
    _TUTORIAL_ROOT + "test_response_status_code/test_tutorial001_tutorial002.py": _module(
        "The tutorial verifies an explicitly configured 201 response and the OpenAPI response/parameter metadata for the created item route.",
        {
            "test_create_item": _function(
                _TUTORIAL_ROOT + "test_response_status_code/test_tutorial001_tutorial002.py",
                "test_create_item",
                ("response-serialization",),
                _JSON_RESPONSE,
                "A POST query parameter is returned as JSON with the route's configured 201 status.",
                (
                    _one(
                        _RESPONSE_STATUS,
                        "fastapi.tutorial-response-status-code001.created-item",
                        "create-item-with-query-name",
                        _JSON_RESPONSE,
                    ),
                ),
                "The independent input uses another name value; it exercises the same query extraction, returned JSON shape, and explicit 201 route status. Exact JSON bytes are represented as decoded JSON at the source selector.",
                (*_ROUTE_STATUS, *_ROUTE_RESPONSE, *_STARLETTE_RESPONSE_RUNTIME, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _TUTORIAL_ROOT + "test_response_status_code/test_tutorial001_tutorial002.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The exact snapshot checks the route query parameter and response code 201 in OpenAPI.",
                (
                    _one(
                        _RESPONSE_STATUS,
                        "fastapi.tutorial-response-status-code001.openapi",
                        "inspect-created-response",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The independently authored recipe selects the response-201 and parameter subtrees rather than comparing the complete OpenAPI snapshot.",
                (*_ROUTE_STATUS, *_OPENAPI_DOCUMENT),
            ),
        },
    ),
    _BODY_ROOT + "test_tutorial001.py": _module(
        "The module covers required/optional model fields, scalar coercion and missing-field errors, malformed/form bodies, strict content-type parsing, and OpenAPI request-body documentation.",
        {
            "test_body_float": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_body_float",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "A JSON object with a numeric price validates as the request model, with optional fields represented by their defaults.",
                (_body001("body-float"),),
                "The recipe uses independent field values and exact raw response bytes; the source asserts decoded JSON values, so formatting differences are not covered.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_post_with_str_float": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_str_float",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "The request model coerces a numeric string to a float and supplies optional field defaults.",
                (_body001("string-float"),),
                "The input uses new values but the same scalar coercion and optional-field shape; raw-byte workflow comparison is stricter than the source's response.json() comparison.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_post_with_str_float_description": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_str_float_description",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "The request accepts a numeric string and an optional description while leaving tax unset.",
                (_body001("string-float-description"),),
                "The input keeps the same field-presence pattern with independent values; the workflow records exact body bytes while the source compares decoded JSON.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_post_with_str_float_description_tax": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_str_float_description_tax",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "The request accepts all model fields, coercing price to float and retaining the supplied tax.",
                (_body001("string-float-description-tax"),),
                "The independent payload preserves the same field and coercion pattern; exact raw response bytes are stricter than the source JSON-value comparison.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_post_with_only_name": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_only_name",
                ("request-validation",),
                _JSON_RESPONSE,
                "Omitting the required price field produces a request-validation response at body.price.",
                (_body001("missing-price"),),
                "The workflow exercises the same missing-field shape with another name value and compares raw bytes instead of decoded JSON.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_post_with_only_name_price": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_only_name_price",
                ("request-validation",),
                _JSON_RESPONSE,
                "An unparseable string for the required float price yields a float-parsing error at body.price.",
                (_body001("unparseable-price"),),
                "The input probes the same invalid scalar type using independent values; response error wording/details depend on the pinned Pydantic contract.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_post_with_no_data": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_no_data",
                ("request-validation",),
                _JSON_RESPONSE,
                "An empty JSON object reports both required model fields as missing.",
                (_body001("empty-object"),),
                "The empty-object input has the same validation shape; precise error details and JSON serialization remain pinned to Pydantic/FastAPI.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_post_with_none": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_with_none",
                ("request-validation",),
                _JSON_RESPONSE,
                "A request without a body reports that the model body itself is required.",
                (_body001("empty-body"),),
                "The ASGI request has an empty body and no content-type, matching the source's None request at the body-presence level; the source compares decoded error JSON.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_post_broken_body": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_broken_body",
                ("request-validation",),
                _JSON_RESPONSE,
                "Malformed application/json is translated into a json_invalid request-validation response.",
                (_body001("malformed-json"),),
                "The fixture uses different malformed JSON text; its byte offset and decoder message are therefore not evidence for the source's exact input-specific error context.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_post_form_for_json": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_post_form_for_json",
                ("request-validation",),
                _JSON_RESPONSE,
                "Form-encoded bytes sent to a JSON model endpoint do not become a JSON object and fail model validation.",
                (_body001("form-body-to-json-model"),),
                "The independent form body carries the same form media type and model endpoint. Generic form parsing is Starlette 1.6.0 behavior; validation and error location are FastAPI/Pydantic behavior.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_explicit_content_type": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_explicit_content_type",
                ("request-validation",),
                ("http.status",),
                "A valid raw JSON body with explicit application/json content type succeeds.",
                (_body001("explicit-json-content-type", ("http.status",)),),
                "The input body is valid JSON and uses application/json; this mapping observes only the asserted status.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_geo_json": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_geo_json",
                ("request-validation",),
                ("http.status",),
                "A +json media subtype is accepted as JSON for a body model.",
                (_body001("json-suffix-content-type", ("http.status",)),),
                "The workflow exercises application/geo+json with an independent valid object and observes only the asserted success status.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_no_content_type_json": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_no_content_type_json",
                ("request-validation",),
                ("http.status",),
                "With the default strict content-type policy, JSON-looking bytes without Content-Type are not decoded as JSON and fail the model field.",
                (_body001("json-without-content-type", ("http.status",)),),
                "The recipe sends a valid JSON-looking body without a content-type header and observes the asserted failure status.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_wrong_headers": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_wrong_headers",
                ("request-validation",),
                _JSON_RESPONSE,
                "Three non-JSON content types leave JSON-looking bytes unparsed, producing model validation errors.",
                (
                    _link(
                        _BODY001,
                        "fastapi.tutorial-body001.input-and-openapi-matrix",
                        (
                            "wrong-text-content-type",
                            "wrong-json-sequence-content-type",
                            "wrong-vendor-content-type",
                        ),
                        _JSON_RESPONSE,
                    ),
                ),
                "Each input uses one of the source's rejected media-type classes with a valid JSON-looking body. Exact error details are Pydantic/FastAPI-specific; the raw body bytes are not normalized to response.json() semantics.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_other_exceptions": _excluded(
                _BODY_ROOT + "test_tutorial001.py",
                "test_other_exceptions",
                "The function patches json.loads to raise an arbitrary Python exception while a request is being parsed. That injected process-local failure is not an input-only HTTP/ASGI stimulus and cannot be represented by a deterministic request recipe without reproducing the test harness monkeypatch.",
            ),
            "test_openapi_schema": _function(
                _BODY_ROOT + "test_tutorial001.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot covers the requestBody model schema, optional fields, validation response, and operation metadata.",
                (_body001("openapi", _OPENAPI_RESPONSE),),
                "The recipe selects the route operation, Item schema, and validation schemas; it does not compare the entire OpenAPI document byte-for-byte.",
                (*_BODY_OPENAPI, *_OPENAPI_DOCUMENT),
            ),
        },
    ),
    _BODY_ROOT + "test_tutorial002.py": _module(
        "The tutorial derives a response field from one Pydantic body model and distinguishes supplied from omitted optional tax.",
        {
            "test_post_with_tax": _function(
                _BODY_ROOT + "test_tutorial002.py",
                "test_post_with_tax",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "A supplied tax value is included in application-computed price_with_tax output.",
                (
                    _one(
                        _BODY002,
                        "fastapi.pydantic-request-body-wave.body-model.test-post-with-tax",
                        "dispatch",
                        _JSON_RESPONSE,
                    ),
                ),
                "The upstream function is parametrized with string and numeric price values; the input recipe samples only the string form. Its body/model and computed-tax behavior match, but data values differ and exact response bytes are stricter than the source JSON comparison.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_post_without_tax": _function(
                _BODY_ROOT + "test_tutorial002.py",
                "test_post_without_tax",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "Omitting optional tax leaves tax null and skips the application's computed price_with_tax field.",
                (
                    _one(
                        _BODY002,
                        "fastapi.pydantic-request-body-wave.body-model.test-post-without-tax",
                        "dispatch",
                        _JSON_RESPONSE,
                    ),
                ),
                "The source runs both string and numeric price variants; this input samples the numeric variant only. The route model and omitted-tax shape match, but the sample values differ.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_post_with_no_data": _function(
                _BODY_ROOT + "test_tutorial002.py",
                "test_post_with_no_data",
                ("request-validation",),
                _JSON_RESPONSE,
                "An empty model object reports missing required request fields.",
                (
                    _one(
                        _BODY002,
                        "fastapi.pydantic-request-body-wave.body-model.test-post-with-no-data",
                        "dispatch",
                        _JSON_RESPONSE,
                    ),
                ),
                "The independent request is an empty JSON object and observes status plus raw body; field-error content is a pinned Pydantic/FastAPI contract.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _BODY_ROOT + "test_tutorial002.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot documents the request body's Product model schema and generated response metadata.",
                (
                    _one(
                        _BODY002,
                        "fastapi.pydantic-request-body-wave.body-model.test-openapi-schema",
                        "dispatch",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The recipe selects the requestBody schema only and uses a different operation/model name; it does not compare the full source snapshot.",
                (*_BODY_OPENAPI, *_OPENAPI_DOCUMENT),
            ),
        },
    ),
    _BODY_ROOT + "test_tutorial003.py": _module(
        "The module checks required and optional request-model fields and the generated operation/model schema for a PUT route.",
        {
            "test_put_all": _function(
                _BODY_ROOT + "test_tutorial003.py",
                "test_put_all",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "A full request model supplies both optional fields and returns the route identifier with model values.",
                (
                    _one(
                        _BODY003,
                        "fastapi.body.tutorial003.complete-model",
                        "tutorial003-replace-complete-record",
                        _JSON_RESPONSE,
                    ),
                ),
                "The input exercises a full model with all optional fields, but uses another route, field names, and values; body bytes are stricter than the source decoded JSON assertion.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_put_only_required": _function(
                _BODY_ROOT + "test_tutorial003.py",
                "test_put_only_required",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "A request with only required fields returns optional fields with their default null values.",
                (
                    _one(
                        _BODY003,
                        "fastapi.body.tutorial003.optional-model-fields-absent",
                        "tutorial003-replace-required-fields-only",
                        _JSON_RESPONSE,
                    ),
                ),
                "The independent model fixture tests required-versus-optional field behavior with another model and endpoint; it does not prove source payload serialization.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_put_with_no_data": _function(
                _BODY_ROOT + "test_tutorial003.py",
                "test_put_with_no_data",
                ("request-validation",),
                _JSON_RESPONSE,
                "An empty model body reports both required fields missing.",
                (
                    _one(
                        _BODY003,
                        "fastapi.body.tutorial003.required-model-fields-missing",
                        "tutorial003-reject-incomplete-record",
                        _JSON_RESPONSE,
                    ),
                ),
                "The recipe sends an empty object and observes the analogous required-field validation shape under a different schema.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _BODY_ROOT + "test_tutorial003.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot includes the PUT requestBody, response, model schema, and validation-error components.",
                (
                    _one(
                        _BODY003,
                        "fastapi.body.tutorial003.openapi-operation-and-model",
                        "tutorial003-inspect-body-operation",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The input selects corresponding operation and model subtrees but uses a different path and model name and does not compare the full source snapshot.",
                (*_BODY_OPENAPI, *_OPENAPI_DOCUMENT),
            ),
        },
    ),
    _BODY_ROOT + "test_tutorial004.py": _module(
        "The module checks a request model combined with a query parameter and optional model-field defaults.",
        {
            "test_put_all": _function(
                _BODY_ROOT + "test_tutorial004.py",
                "test_put_all",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "The full model and query parameter are echoed in the response.",
                (
                    _one(
                        _BODY004,
                        "fastapi.body.tutorial004.complete-model",
                        "tutorial004-replace-complete-record",
                        _JSON_RESPONSE,
                    ),
                ),
                "The workflow includes a nonempty query string and full model while using a different route, values, and query value than the source; raw body comparison is stricter than response.json().",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_put_only_required": _function(
                _BODY_ROOT + "test_tutorial004.py",
                "test_put_only_required",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "A model with only required fields returns the optional fields as null defaults.",
                (
                    _one(
                        _BODY004,
                        "fastapi.body.tutorial004.optional-model-fields-absent",
                        "tutorial004-replace-required-fields-only",
                        _JSON_RESPONSE,
                    ),
                ),
                "The fixture uses a different model and endpoint but exercises absent optional fields; exact source body values are not represented.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_put_with_no_data": _function(
                _BODY_ROOT + "test_tutorial004.py",
                "test_put_with_no_data",
                ("request-validation",),
                _JSON_RESPONSE,
                "An empty body model reports missing required fields.",
                (
                    _one(
                        _BODY004,
                        "fastapi.body.tutorial004.required-model-fields-missing",
                        "tutorial004-reject-incomplete-record",
                        _JSON_RESPONSE,
                    ),
                ),
                "The fixture uses a different schema and path; it samples the same empty-object validation behavior.",
                (*_BODY_PARSE, *_BODY_REQUEST_CONTRACT, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _BODY_ROOT + "test_tutorial004.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The full snapshot checks both path and query parameters alongside requestBody and model schemas.",
                (
                    _one(
                        _BODY004,
                        "fastapi.body.tutorial004.openapi-operation-and-model",
                        "tutorial004-inspect-body-operation",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The linked OpenAPI observation selects a related operation/model projection with its query and body fields but a different endpoint, schema, and values.",
                (*_BODY_OPENAPI, *_OPENAPI_DOCUMENT),
            ),
        },
    ),
    _TUTORIAL_ROOT + "test_body_fields/test_tutorial001.py": _module(
        "The parametrized module checks Body(embed=True) in default and Annotated forms, nested request validation, Field constraints, and generated embedded-body schemas.",
        {
            "test_items_5": _function(
                _TUTORIAL_ROOT + "test_body_fields/test_tutorial001.py",
                "test_items_5",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "Both parameter-declaration forms require the embedded item object and return its optional defaults.",
                (
                    _link(
                        _BODY_FIELDS001,
                        "fastapi.tutorial-body-fields001.embedded-body-and-field-matrix",
                        ("default-items-5", "annotated-items-5"),
                        _JSON_RESPONSE,
                    ),
                ),
                "The workflow includes both independently authored Body(embed=True) and Annotated[Item, Body(embed=True)] routes; its route prefixes and values are independent of the two source fixture modules.",
                (*_BODY_FIELD_EMBED, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_items_6": _function(
                _TUTORIAL_ROOT + "test_body_fields/test_tutorial001.py",
                "test_items_6",
                ("request-validation", "response-serialization"),
                _JSON_RESPONSE,
                "Both embedded body forms coerce the supplied tax string while retaining the other optional fields.",
                (
                    _link(
                        _BODY_FIELDS001,
                        "fastapi.tutorial-body-fields001.embedded-body-and-field-matrix",
                        ("default-items-6", "annotated-items-6"),
                        _JSON_RESPONSE,
                    ),
                ),
                "The input uses independent field values but samples the same embedded object and scalar coercion for both declarations.",
                (*_BODY_FIELD_EMBED, *_ROUTE_RESPONSE, *_TESTCLIENT),
            ),
            "test_invalid_price": _function(
                _TUTORIAL_ROOT + "test_body_fields/test_tutorial001.py",
                "test_invalid_price",
                ("request-validation",),
                _JSON_RESPONSE,
                "A negative embedded item price violates the greater-than-zero Field constraint in both body declarations.",
                (
                    _link(
                        _BODY_FIELDS001,
                        "fastapi.tutorial-body-fields001.embedded-body-and-field-matrix",
                        ("default-invalid-price", "annotated-invalid-price"),
                        _JSON_RESPONSE,
                    ),
                ),
                "The recipe submits the same negative numeric class to two independently authored embedded routes. Error serialization and wording depend on pinned Pydantic/FastAPI behavior.",
                (*_BODY_FIELD_EMBED, *_TESTCLIENT),
            ),
            "test_openapi_schema": _function(
                _TUTORIAL_ROOT + "test_body_fields/test_tutorial001.py",
                "test_openapi_schema",
                ("openapi-docs",),
                _OPENAPI_RESPONSE,
                "The snapshot records the embedded body wrapper, constrained Item properties, route parameter, and validation response.",
                (
                    _one(
                        _BODY_FIELDS001,
                        "fastapi.tutorial-body-fields001.embedded-body-and-field-matrix",
                        "openapi-embedded-body-fields",
                        _OPENAPI_RESPONSE,
                    ),
                ),
                "The workflow selects both independent operation subtrees and component schemas rather than comparing the full snapshot; its route prefixes produce different operation/wrapper names.",
                (*_BODY_FIELD_EMBED, *_OPENAPI_DOCUMENT),
            ),
        },
    ),
}
