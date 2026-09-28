"""Source-reviewed case links for FastAPI's handling-errors tutorial tests.

The rows are atlas inputs only. They point to existing independently authored
ASGI workflows and make no parity or output claim. Generic TestClient and
exception dispatch behavior remains under the pinned Starlette 1.6.0 contract.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT.parent / "fastapi"

SOURCE_IDENTITY = {
    "fastapi_version": "0.141.1",
    "fastapi_commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "starlette_version": "1.6.0",
    "starlette_commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}

_HTTP_SELECTORS = ["http.body.bytes", "http.headers.ordered", "http.status"]
_OPENAPI_SELECTORS = ["http.headers.ordered", "http.status", "openapi.document"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
    source_path = FASTAPI_ROOT / test_path
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
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
        f"pinned FastAPI 0.141.1 test stimulus and assertions for {function_name}",
    )


def _case_link(recipe_path: str, case_id: str, selectors: list[str]) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "workflow_selectors": list(selectors),
    }


def _review(
    test_path: str,
    function_name: str,
    feature_ids: list[str],
    selectors: list[str],
    rationale: str,
    recipe_path: str,
    case_id: str,
    contract_gate: str,
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    link = _case_link(recipe_path, case_id, selectors)
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + contract_gate,
        "workflow_cases": [link],
        "stimulus_notes": (
            f"Existing input-only case {recipe_path}::{case_id}; selectors: "
            f"{', '.join(selectors)}. The case contains no expected output."
        ),
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    links_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    source_rows: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for review in functions.values():
        for link in review["workflow_cases"]:
            key = (link["recipe_path"], link["case_id"])
            links_by_key.setdefault(key, link)
        for row in review["supporting_sources"]:
            key = (row["path"], row.get("start_line", 0), row.get("end_line", 0), row["role"])
            source_rows.setdefault(key, row)
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
        "functions": functions,
        "workflow_cases": list(links_by_key.values()),
        "supporting_sources": list(source_rows.values()),
        "module_observation_selectors": sorted(
            {
                selector
                for review in functions.values()
                for selector in review["observation_selectors"]
            }
        ),
    }


_HTTP_HANDLER = _source(
    "fastapi/exception_handlers.py",
    11,
    17,
    "FastAPI's default HTTP exception handler emits detail, status, and exception headers",
)
_VALIDATION_HANDLER = _source(
    "fastapi/exception_handlers.py",
    20,
    26,
    "FastAPI's default request-validation handler encodes errors into a 422 JSON response",
)
_DEFAULT_HANDLER_REGISTRATION = _source(
    "fastapi/applications.py",
    1000,
    1012,
    "FastAPI installs default HTTP, request-validation, and WebSocket validation handlers",
)
_HANDLER_DECORATOR = _source(
    "fastapi/applications.py",
    4729,
    4774,
    "FastAPI's exception_handler decorator registers the supplied handler",
)
_HTTP_EXCEPTION_CLASS = _source(
    "fastapi/exceptions.py",
    17,
    43,
    "FastAPI HTTPException subclasses Starlette HTTPException and documents detail behavior",
)
_REQUEST_VALIDATION_CREATION = _source(
    "fastapi/routing.py",
    751,
    755,
    "FastAPI wraps dependency and field errors in RequestValidationError",
)
_BODY_VALIDATION_FLOW = _source(
    "fastapi/routing.py",
    425,
    465,
    "FastAPI reads and decodes request bodies and reports malformed JSON as RequestValidationError",
)
_OPENAPI_PATH_FIELDS = _source(
    "fastapi/openapi/utils.py",
    311,
    385,
    "FastAPI builds OpenAPI path operations and their parameter and request-body schemas",
)
_OPENAPI_RESPONSE_FIELDS = _source(
    "fastapi/openapi/utils.py",
    403,
    472,
    "FastAPI constructs the documented response status and validation response schema",
)
_STARLETTE_HANDLER_DISPATCH = _source(
    "starlette/_exception_handler.py",
    16,
    63,
    "Starlette 1.6.0 looks up handlers through exception MRO and dispatches the selected handler",
)

_HANDLING = "tests/fixtures/input-recipes/parity/handling-errors.yaml"
_OVERRIDES = "tests/fixtures/input-recipes/parity/exception-overrides.yaml"
_BODY_VALIDATION = "tests/fixtures/input-recipes/parity/request-validation-body.yaml"

ERROR_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_tutorial/test_handling_errors/test_tutorial001.py": _module(
        "The module tests a successful route, a default HTTPException response, and an OpenAPI snapshot. The linked workflows sample those behavior families with separate routes and selected OpenAPI pointers.",
        {
            "test_get_item": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial001.py",
                "test_get_item",
                ["response-serialization"],
                _HTTP_SELECTORS,
                "A successful path operation returns an app-owned item value through FastAPI's route response path.",
                _HANDLING,
                "fastapi.docs.handling-errors.success",
                "The case uses /products/kettle and a different item value; it does not replay /items/foo or assert the source's parsed JSON structure. Generic HTTP framing and TestClient.json() behavior remain Starlette/client contract details.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial001_py310.py",
                        8,
                        12,
                        "documented item route and success branch",
                    ),
                    _source(
                        "fastapi/routing.py",
                        706,
                        759,
                        "FastAPI executes the endpoint and selects the response path",
                    ),
                ),
            ),
            "test_get_item_not_found": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial001.py",
                "test_get_item_not_found",
                ["public-api-errors"],
                _HTTP_SELECTORS,
                "A missing item raises FastAPI HTTPException and produces the default HTTP error response.",
                _HANDLING,
                "fastapi.docs.handling-errors.http-exception-detail",
                "The case uses a different route and structured detail value. The source only asserts that x-error is absent, while the workflow compares ordered headers and the current observation schema has no header-absence predicate; no complete-header-set equivalence is claimed.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial001_py310.py",
                        8,
                        12,
                        "documented missing-item HTTPException branch",
                    ),
                    _HTTP_EXCEPTION_CLASS,
                    _HTTP_HANDLER,
                    _DEFAULT_HANDLER_REGISTRATION,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial001.py",
                "test_openapi_schema",
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source compares generated path, parameter, response, and validation-schema OpenAPI content.",
                _HANDLING,
                "fastapi.docs.handling-errors.openapi",
                "The workflow checks selected pointers for its independent /products and /quantities routes. It does not compare the exact /items/{item_id} snapshot, generated names, all component fields, or the full source JSON document; the OpenAPI assertion is only partially represented.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial001_py310.py",
                        1,
                        12,
                        "documented FastAPI app and path operation included in OpenAPI",
                    ),
                    _OPENAPI_PATH_FIELDS,
                    _OPENAPI_RESPONSE_FIELDS,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_handling_errors/test_tutorial002.py": _module(
        "The module tests successful output, an HTTPException with a custom header, and an OpenAPI snapshot. The existing workflows sample response emission and path schema on separately authored routes.",
        {
            "test_get_item_header": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial002.py",
                "test_get_item_header",
                ["response-serialization"],
                _HTTP_SELECTORS,
                "The successful route returns the app-owned item value as JSON.",
                _HANDLING,
                "fastapi.docs.handling-errors.success",
                "The workflow uses a different route and success value and compares raw bytes plus ordered headers; the source checks status and decoded JSON for its own route.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial002_py310.py",
                        8,
                        16,
                        "documented header tutorial route and success branch",
                    ),
                    _source(
                        "fastapi/routing.py",
                        706,
                        759,
                        "FastAPI executes the endpoint and selects the response path",
                    ),
                ),
            ),
            "test_get_item_not_found_header": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial002.py",
                "test_get_item_not_found_header",
                ["public-api-errors"],
                _HTTP_SELECTORS,
                "FastAPI carries the HTTPException's custom headers onto its default error response.",
                _HANDLING,
                "fastapi.docs.handling-errors.http-exception-detail",
                "The case exercises HTTPException header forwarding with a different detail and X-Catalog-Error name/value. It does not assert the source's exact X-Error value or parsed JSON detail, and ordered-header equality is beyond the source assertions.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial002_py310.py",
                        8,
                        16,
                        "documented HTTPException headers and route branch",
                    ),
                    _HTTP_EXCEPTION_CLASS,
                    _HTTP_HANDLER,
                    _DEFAULT_HANDLER_REGISTRATION,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial002.py",
                "test_openapi_schema",
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source compares the generated OpenAPI document for the header tutorial route and default validation schema.",
                _HANDLING,
                "fastapi.docs.handling-errors.openapi",
                "Only selected parameter and 422-schema pointers are observed for independent routes. The exact /items-header/{item_id} operation ID and entire source snapshot remain gated.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial002_py310.py",
                        1,
                        16,
                        "documented app route represented in the source OpenAPI snapshot",
                    ),
                    _OPENAPI_PATH_FIELDS,
                    _OPENAPI_RESPONSE_FIELDS,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_handling_errors/test_tutorial003.py": _module(
        "The module exercises a successful route, a registered handler for an app-defined exception, and an OpenAPI snapshot. Existing cases sample success, a separately defined handled exception, and selected OpenAPI paths.",
        {
            "test_get": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial003.py",
                "test_get",
                ["response-serialization"],
                _HTTP_SELECTORS,
                "The successful endpoint returns an app-owned unicorn value through the FastAPI response path.",
                _HANDLING,
                "fastapi.docs.handling-errors.success",
                "The case uses a different route and value, and its byte/header observations exceed the source's status and parsed JSON assertions.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial003_py310.py",
                        21,
                        25,
                        "documented unicorn route and successful branch",
                    ),
                    _source(
                        "fastapi/routing.py",
                        706,
                        759,
                        "FastAPI executes the endpoint and selects the response path",
                    ),
                ),
            ),
            "test_get_exception": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial003.py",
                "test_get_exception",
                ["public-api-errors"],
                _HTTP_SELECTORS,
                "An exception_handler-registered app handler returns an HTTP status and JSON body for an app-defined exception.",
                _HANDLING,
                "fastapi.docs.handling-errors.custom-exception",
                "The workflow uses CatalogIssue and a different response body/status payload than UnicornException. It samples handler registration/dispatch and HTTP output shape only; exact exception class, name interpolation, and parsed JSON are not matched.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial003_py310.py",
                        5,
                        18,
                        "documented exception type and registered JSON response handler",
                    ),
                    _HANDLER_DECORATOR,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial003.py",
                "test_openapi_schema",
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source compares the generated OpenAPI path, response, path parameter, and shared validation component.",
                _HANDLING,
                "fastapi.docs.handling-errors.openapi",
                "The case observes selected pointers for separate routes and does not compare the exact /unicorns/{name} operation or full snapshot.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial003_py310.py",
                        1,
                        25,
                        "documented exception-handler app and route included in OpenAPI",
                    ),
                    _OPENAPI_PATH_FIELDS,
                    _OPENAPI_RESPONSE_FIELDS,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_handling_errors/test_tutorial004.py": _module(
        "The module tests custom HTTP and validation handlers, a successful typed path parameter, and an OpenAPI snapshot. Existing exception-overrides cases independently exercise those handler categories and the selected path schema.",
        {
            "test_get_validation_error": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial004.py",
                "test_get_validation_error",
                ["request-validation", "public-api-errors"],
                _HTTP_SELECTORS,
                "A RequestValidationError handler replaces the default validation response with plain text and status 400.",
                _OVERRIDES,
                "fastapi.docs.handling-errors.overridden-validation-error",
                "The case uses an independently named integer order route and returns a different plain-text message. It samples override dispatch, status, headers, and response bytes; the source's exact path error location and substring assertions are not exercised.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial004_py310.py",
                        14,
                        19,
                        "custom RequestValidationError handler",
                    ),
                    _source(
                        "docs_src/handling_errors/tutorial004_py310.py",
                        22,
                        26,
                        "typed path route producing the validation error",
                    ),
                    _REQUEST_VALIDATION_CREATION,
                    _HANDLER_DECORATOR,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_get_http_error": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial004.py",
                "test_get_http_error",
                ["public-api-errors"],
                _HTTP_SELECTORS,
                "A custom StarletteHTTPException handler returns plain text while preserving the selected error status.",
                _OVERRIDES,
                "fastapi.docs.handling-errors.overridden-http-error",
                "The case uses a different route, exception detail, and response text. It samples handler dispatch and response emission but does not replay the exact status/body assertion; ordered response headers are not asserted in the source.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial004_py310.py",
                        9,
                        11,
                        "custom StarletteHTTPException handler",
                    ),
                    _source(
                        "docs_src/handling_errors/tutorial004_py310.py",
                        22,
                        26,
                        "route raises FastAPI HTTPException",
                    ),
                    _HTTP_EXCEPTION_CLASS,
                    _HANDLER_DECORATOR,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_get": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial004.py",
                "test_get",
                ["request-validation", "response-serialization"],
                _HTTP_SELECTORS,
                "A valid integer path parameter reaches the route and returns its app-owned value.",
                _OVERRIDES,
                "fastapi.docs.handling-errors.override-success",
                "The workflow uses /orders/2 and a different response model/value. It samples a successful typed route with handler registrations present; source JSON parsing and exact /items/2 result are not claimed.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial004_py310.py",
                        22,
                        26,
                        "typed integer path parameter and successful route branch",
                    ),
                    _source(
                        "fastapi/routing.py",
                        475,
                        490,
                        "FastAPI resolves the route's validated dependency values",
                    ),
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial004.py",
                "test_openapi_schema",
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source compares the exact generated integer path and default validation response schema while custom handlers are registered.",
                _OVERRIDES,
                "fastapi.docs.handling-errors.overrides-openapi",
                "The case observes selected pointers for an independent /orders/{order_id} path. It does not compare the full /items/{item_id} snapshot or establish that registering error handlers changes the generated schema.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial004_py310.py",
                        1,
                        26,
                        "documented handlers and route included in OpenAPI",
                    ),
                    _OPENAPI_PATH_FIELDS,
                    _OPENAPI_RESPONSE_FIELDS,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_handling_errors/test_tutorial005.py": _module(
        "The module tests a custom RequestValidationError response that includes the decoded body, a valid Pydantic body route, and an OpenAPI snapshot. The existing body-validation workflow samples invalid/valid bodies and selected schema pointers on a separately authored model.",
        {
            "test_post_validation_error": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial005.py",
                "test_post_validation_error",
                ["request-validation", "public-api-errors"],
                _HTTP_SELECTORS,
                "The custom handler returns validation errors together with the parsed request body in its JSON response.",
                _BODY_VALIDATION,
                "fastapi.docs.handling-errors.body-echo.invalid-input",
                "The source handler emits {detail, body} for Item(title, size); the workflow uses PackageInput(label, units) and emits {issues, payload}. It samples invalid JSON-body validation and body access only. Exact Pydantic errors, fields, values, JSON key names, and decoded-object semantics are not claimed.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial005_py310.py",
                        10,
                        15,
                        "custom validation handler encodes validation errors and request body",
                    ),
                    _source(
                        "docs_src/handling_errors/tutorial005_py310.py",
                        18,
                        25,
                        "Item request model and POST route",
                    ),
                    _BODY_VALIDATION_FLOW,
                    _REQUEST_VALIDATION_CREATION,
                    _HANDLER_DECORATOR,
                ),
            ),
            "test_post": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial005.py",
                "test_post",
                ["request-validation", "response-serialization"],
                _HTTP_SELECTORS,
                "A valid JSON request body is parsed into a Pydantic model and the endpoint returns that model.",
                _BODY_VALIDATION,
                "fastapi.docs.handling-errors.body-echo.valid-input",
                "The workflow uses a different model, route, and field values. It samples successful body parsing and route output with raw response bytes; Pydantic owns model construction and JSON value semantics under the pinned identity.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial005_py310.py",
                        18,
                        25,
                        "Item input model and POST route",
                    ),
                    _BODY_VALIDATION_FLOW,
                    _source(
                        "fastapi/routing.py",
                        706,
                        759,
                        "FastAPI resolves the endpoint result and constructs its response",
                    ),
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial005.py",
                "test_openapi_schema",
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source compares the request-body, response, and Item component schema in its exact OpenAPI document.",
                _BODY_VALIDATION,
                "fastapi.docs.handling-errors.body-echo.openapi",
                "The workflow observes selected pointers for /packages and PackageInput only. It does not compare the complete source /items/ OpenAPI snapshot or Item schema.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial005_py310.py",
                        18,
                        25,
                        "documented request model and POST route represented in OpenAPI",
                    ),
                    _OPENAPI_PATH_FIELDS,
                    _OPENAPI_RESPONSE_FIELDS,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_handling_errors/test_tutorial006.py": _module(
        "The module tests custom handlers that delegate to FastAPI's default handlers, typed path validation and success, and an OpenAPI snapshot. Existing cases sample default error responses, successful routing, and selected schema pointers but do not run the tutorial's delegating wrappers.",
        {
            "test_get_validation_error": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial006.py",
                "test_get_validation_error",
                ["request-validation", "public-api-errors"],
                _HTTP_SELECTORS,
                "The custom RequestValidationError handler delegates to FastAPI's default handler, producing a 422 error response for an invalid integer path value.",
                _HANDLING,
                "fastapi.docs.handling-errors.validation-error",
                "The workload exercises FastAPI's default validation response for a different typed path route; it does not register or invoke the tutorial's delegating handler and does not check its stdout. The source's exact item_id error object is also not represented by the quantity case.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial006_py310.py",
                        18,
                        21,
                        "custom validation handler delegates to FastAPI's default handler",
                    ),
                    _source(
                        "docs_src/handling_errors/tutorial006_py310.py",
                        24,
                        28,
                        "typed integer path route",
                    ),
                    _REQUEST_VALIDATION_CREATION,
                    _VALIDATION_HANDLER,
                    _HANDLER_DECORATOR,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_get_http_error": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial006.py",
                "test_get_http_error",
                ["public-api-errors"],
                _HTTP_SELECTORS,
                "The custom HTTP handler delegates to FastAPI's default HTTPException response handler.",
                _HANDLING,
                "fastapi.docs.handling-errors.http-exception-status",
                "The workload raises HTTPException without the tutorial's custom logging/delegating handler and uses a different detail and route. It samples the ordinary status/error response path only; stdout, delegation, and the exact source JSON detail are not observed.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial006_py310.py",
                        12,
                        15,
                        "custom HTTP handler logs then delegates to FastAPI's default",
                    ),
                    _source(
                        "docs_src/handling_errors/tutorial006_py310.py",
                        24,
                        28,
                        "typed route's HTTPException branch",
                    ),
                    _HTTP_HANDLER,
                    _HANDLER_DECORATOR,
                    _STARLETTE_HANDLER_DISPATCH,
                ),
            ),
            "test_get": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial006.py",
                "test_get",
                ["request-validation", "response-serialization"],
                _HTTP_SELECTORS,
                "A valid integer path value reaches the endpoint and returns its app-owned result.",
                _HANDLING,
                "fastapi.docs.handling-errors.success",
                "The case uses a string product parameter and a different response model/value, so it does not exercise integer conversion or replay the exact source response. Its raw bytes and ordered-header comparisons exceed the source's parsed-JSON assertion.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial006_py310.py",
                        24,
                        28,
                        "typed integer route and success branch",
                    ),
                    _source(
                        "fastapi/routing.py",
                        475,
                        490,
                        "FastAPI resolves validated path values for the endpoint",
                    ),
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_handling_errors/test_tutorial006.py",
                "test_openapi_schema",
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source compares the integer path schema, default validation response, and complete OpenAPI snapshot while custom handlers are registered.",
                _HANDLING,
                "fastapi.docs.handling-errors.openapi",
                "The workflow checks selected pointers for independent routes and does not compare the exact /items/{item_id} path or full snapshot. It does not prove whether registering delegating error handlers changes the document.",
                (
                    _source(
                        "docs_src/handling_errors/tutorial006_py310.py",
                        1,
                        28,
                        "documented delegating handlers and path operation included in OpenAPI",
                    ),
                    _OPENAPI_PATH_FIELDS,
                    _OPENAPI_RESPONSE_FIELDS,
                ),
            ),
        },
    ),
}

# This package marker is outside the atlas's tests/test_*.py executable test
# denominator. It has no test functions or runtime behavior to map.
ERROR_TUTORIAL_TEST_MODULE_EXCLUSIONS = {
    "tests/test_tutorial/test_handling_errors/__init__.py": {
        "mapping_status": "source-backed-exclusion",
        "reason": "The package marker contains no executable test function and is not a tests/test_*.py atlas module.",
        "supporting_sources": [
            {
                "path": "tests/test_tutorial/test_handling_errors/__init__.py",
                "role": "pinned FastAPI 0.141.1 package marker; no test functions",
            }
        ],
    }
}
