"""Source review for pending FastAPI route/application test functions.

This is a separate atlas input. It links upstream functions to independently
authored input-only workflows and records exact per-function exclusions. It
does not claim generic Starlette or Pydantic behavior as FastAPI behavior.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI routing, Response, and HTTP/WebSocket transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned request validation and model serialization dependency",
    },
}

_ROUTING_UPSTREAM = "tests/fixtures/input-recipes/parity/routing-upstream.yaml"
_ROUTING_SURFACE = "tests/fixtures/input-recipes/parity/routing-surface.yaml"
_ENUM_RECIPE = "tests/fixtures/input-recipes/parity/application-enum-status-code-upstream.yaml"
_WS_ROUTE_SCOPE_RECIPE = "tests/fixtures/input-recipes/parity/route-scope-websocket-path.yaml"
_HTTP_BODY_SELECTORS = ["http.status", "http.body.bytes"]
_HTTP_HEADER_SELECTORS = ["http.status", "http.headers.ordered"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(test_path: str, function_name: str) -> dict[str, Any]:
    path = FASTAPI_ROOT / test_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    starts = [node.lineno, *(decorator.lineno for decorator in node.decorator_list)]
    return _source(
        test_path,
        min(starts),
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test function {function_name} and its assertions",
    )


def _workflow(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _mapping(
    test_path: str,
    function_name: str,
    *,
    workflows: list[dict[str, Any]],
    rationale: str,
    contract_gate: str,
    feature_ids: list[str] | None = None,
    supporting_sources: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    selectors = sorted(
        {selector for workflow in workflows for selector in workflow["observation_selectors"]}
    )
    return {
        "mapping_status": "reviewed_partial",
        "feature_ids": list(feature_ids or ["app-routing"]),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": f"Partial: {contract_gate}",
        "workflow_cases": workflows,
        "stimulus_notes": (
            "The linked YAML recipes specify inputs and selected observations only; "
            "their independently authored workloads store no expected outputs."
        ),
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            *supporting_sources,
        ],
    }


def _exclusion(
    test_path: str,
    function_name: str,
    reason: str,
    *,
    supporting_sources: tuple[dict[str, Any], ...] = (),
    related_workflows: tuple[dict[str, Any], ...] = (),
    owner: str,
) -> dict[str, Any]:
    return {
        "source_span": _test_function_span(test_path, function_name),
        "reason": reason,
        "owner": owner,
        "related_workflows": list(related_workflows),
        "supporting_sources": list(supporting_sources),
    }


_CUSTOM_ROUTE_SETUP = _source(
    "tests/test_custom_route_class.py",
    10,
    44,
    "custom APIRoute subclasses, nested routers, route declarations, and include prefixes",
)
_EXTRA_ROUTES_SETUP = _source(
    "tests/test_extra_routes.py",
    10,
    49,
    "Item model and public FastAPI route declarations used by the extra-route tests",
)
_HTTP_ROUTE_SCOPE_SETUP = _source(
    "tests/test_route_scope.py",
    9,
    19,
    "HTTP and WebSocket endpoints read the matched FastAPI route from ASGI scope",
)
_HTTP_ROUTE_SCOPE_IMPLEMENTATION = _source(
    "fastapi/routing.py",
    1251,
    1259,
    "FastAPI APIRoute adds itself as scope['route'] after Starlette path matching",
)
_WEBSOCKET_ROUTE_SCOPE_IMPLEMENTATION = _source(
    "fastapi/routing.py",
    833,
    837,
    "FastAPI APIWebSocketRoute adds itself as scope['route'] after Starlette matching",
)
_STARLETTE_ROUTE_MATCHING = _source(
    "starlette/routing.py",
    242,
    258,
    "Starlette 1.6.0 Route.matches handles generic HTTP path and method matching",
)
_STARLETTE_WEBSOCKET_MATCHING = _source(
    "starlette/routing.py",
    327,
    340,
    "Starlette 1.6.0 WebSocketRoute.matches handles generic WebSocket path matching",
)
_STARLETTE_ROUTER_DISPATCH = _source(
    "starlette/routing.py",
    684,
    720,
    "Starlette 1.6.0 Router dispatches full/partial matches and invokes its default for misses",
)

ROUTE_APPLICATION_TEST_SOURCE_REVIEW = {
    "fastapi_identity": SOURCE_IDENTITIES["fastapi"],
    "starlette_identity": SOURCE_IDENTITIES["starlette"],
    "pydantic_identity": SOURCE_IDENTITIES["pydantic"],
    "mapping_status": "source-reviewed-input-candidate; parity pending",
    "observation_boundary": (
        "FastAPI app/route registration and FastAPI route-specific ASGI scope metadata. "
        "Starlette 1.6.0 owns generic routing, response emission, and TestClient transport. "
        "Pydantic 2.13.4 owns request validation and model conversion; those behaviors are "
        "not claimed by this routing review."
    ),
    "test_modules": {
        "tests/test_custom_route_class.py": {
            "test_mappings": {
                "test_get_path": _mapping(
                    "tests/test_custom_route_class.py",
                    "test_get_path",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-custom-route-class.test-get-path",
                            ["outer", "middle", "inner"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The three independent requests dispatch through the root and two nested "
                        "router prefixes. The workload supplies its own custom route subclass and "
                        "route values; only status and response-body behavior are mapped here."
                    ),
                    contract_gate=(
                        "The source checks status and parsed JSON, while the workflow compares "
                        "raw response bytes. It does not claim APIRoute Python class identity, "
                        "custom response-header behavior, or generic Starlette matching."
                    ),
                    supporting_sources=(_CUSTOM_ROUTE_SETUP,),
                ),
                "test_openapi_schema": _mapping(
                    "tests/test_custom_route_class.py",
                    "test_openapi_schema",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-custom-route-class.test-openapi-schema",
                            ["schema"],
                            ["openapi.paths"],
                        )
                    ],
                    rationale=(
                        "The existing input selects the three nested route path items from the "
                        "OpenAPI document produced by an independently authored nested-router app."
                    ),
                    contract_gate=(
                        "The upstream function compares a complete OpenAPI snapshot; the workflow "
                        "observes only the three selected path items and does not claim top-level "
                        "document metadata or other OpenAPI behavior."
                    ),
                    feature_ids=["openapi-docs"],
                    supporting_sources=(_CUSTOM_ROUTE_SETUP,),
                ),
            },
            "exclusions": {
                "test_route_classes": _exclusion(
                    "tests/test_custom_route_class.py",
                    "test_route_classes",
                    (
                        "The route-context workflow records the built-in APIRoute projection and "
                        "original-route identity, but this function exercises three user-defined "
                        "APIRoute subclasses selected through APIRouter.route_class. Custom-class "
                        "registration, subclass state, and nested subclass preservation remain "
                        "outside the reviewed slice."
                    ),
                    supporting_sources=(_CUSTOM_ROUTE_SETUP,),
                    owner="APIRoute subclass and custom route-class support",
                ),
            },
        },
        "tests/test_extra_routes.py": {
            "test_mappings": {
                "test_get_api_route": _mapping(
                    "tests/test_extra_routes.py",
                    "test_get_api_route",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-get-api-route",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "An independently declared FastAPI api_route with an explicit GET method "
                        "dispatches a path parameter and returns a JSON response."
                    ),
                    contract_gate=(
                        "The source compares parsed JSON; the workflow compares raw response "
                        "bytes. Path matching and response framing remain in the Starlette 1.6.0 "
                        "contract."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_get_api_route_not_decorated": _mapping(
                    "tests/test_extra_routes.py",
                    "test_get_api_route_not_decorated",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-get-api-route-not-decorated",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The workload registers an undecorated endpoint through add_api_route and "
                        "dispatches its path parameter through the public app interface."
                    ),
                    contract_gate=(
                        "The source compares parsed JSON; the workflow compares raw response "
                        "bytes. Generic path matching and Response behavior remain Starlette-owned."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_delete": _mapping(
                    "tests/test_extra_routes.py",
                    "test_delete",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-delete",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The independent workload registers a DELETE path operation with a typed "
                        "body and records its HTTP result."
                    ),
                    contract_gate=(
                        "This routing link does not own Item validation/default handling or model "
                        "serialization; Pydantic 2.13.4 and the request/response waves own those "
                        "behaviors. The source parses JSON while the workflow compares raw bytes."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_head": _mapping(
                    "tests/test_extra_routes.py",
                    "test_head",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-head",
                            ["dispatch"],
                            _HTTP_HEADER_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The public HEAD decorator registers a route that returns a custom response "
                        "header; the independent workload uses a different header name and item value."
                    ),
                    contract_gate=(
                        "The source selects one named response header; the workflow compares the "
                        "whole ordered header list. HEAD body suppression and TestClient semantics "
                        "belong to Starlette 1.6.0."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_options": _mapping(
                    "tests/test_extra_routes.py",
                    "test_options",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-options",
                            ["dispatch"],
                            _HTTP_HEADER_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The public OPTIONS decorator registers and dispatches a route with a "
                        "custom response header."
                    ),
                    contract_gate=(
                        "The source selects one named response header; the workflow compares the "
                        "whole ordered header list. Response construction and emission are owned "
                        "by the Starlette contract."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_patch": _mapping(
                    "tests/test_extra_routes.py",
                    "test_patch",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-patch",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The independent workload registers a PATCH path operation with a typed "
                        "body and records its HTTP result."
                    ),
                    contract_gate=(
                        "This routing link does not own Item validation/default handling or model "
                        "serialization; Pydantic 2.13.4 and the request/response waves own those "
                        "behaviors. The source parses JSON while the workflow compares raw bytes."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_trace": _mapping(
                    "tests/test_extra_routes.py",
                    "test_trace",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-trace",
                            ["dispatch"],
                            _HTTP_HEADER_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The public TRACE decorator registers a route that returns a response "
                        "with the selected message/http media type."
                    ),
                    contract_gate=(
                        "The source inspects status and Content-Type; the workflow compares the "
                        "complete ordered headers. Generic routing and response-class framing are "
                        "Starlette-owned."
                    ),
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
                "test_openapi_schema": _mapping(
                    "tests/test_extra_routes.py",
                    "test_openapi_schema",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-openapi-schema",
                            ["schema"],
                            ["openapi.paths"],
                        )
                    ],
                    rationale=(
                        "The input selects the operation path items for independently authored "
                        "GET, DELETE, HEAD, OPTIONS, PATCH, TRACE, and add_api_route declarations."
                    ),
                    contract_gate=(
                        "The source asserts a complete OpenAPI snapshot; the workflow selects only "
                        "two path-item projections and omits top-level document metadata."
                    ),
                    feature_ids=["openapi-docs"],
                    supporting_sources=(_EXTRA_ROUTES_SETUP,),
                ),
            },
            "exclusions": {},
        },
        "tests/test_route_scope.py": {
            "test_mappings": {
                "test_get": _mapping(
                    "tests/test_route_scope.py",
                    "test_get",
                    workflows=[
                        _workflow(
                            _ROUTING_SURFACE,
                            "fastapi.routing.include-router-prefix",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The independent HTTP workflow reads the matched APIRoute path from the "
                        "Request scope and includes it in the response body."
                    ),
                    contract_gate=(
                        "The source also returns its string path parameter; this link selects only "
                        "status/body behavior and the route path projection. Generic HTTP route "
                        "matching and the integer path conversion in the workflow are owned by "
                        "Starlette and Pydantic, respectively."
                    ),
                    supporting_sources=(
                        _HTTP_ROUTE_SCOPE_SETUP,
                        _HTTP_ROUTE_SCOPE_IMPLEMENTATION,
                    ),
                ),
                "test_websocket": _mapping(
                    "tests/test_route_scope.py",
                    "test_websocket",
                    workflows=[
                        _workflow(
                            _WS_ROUTE_SCOPE_RECIPE,
                            "fastapi.route-scope.websocket-route-path",
                            ["observe-route-scope"],
                            ["websocket.event_order", "websocket.messages"],
                        )
                    ],
                    rationale=(
                        "The independent WebSocket endpoint returns its path parameter together "
                        "with websocket.scope['route'].path, exercising FastAPI's APIWebSocketRoute "
                        "scope metadata through a public session."
                    ),
                    contract_gate=(
                        "The source receives one parsed JSON message; the workflow compares the "
                        "ordered WebSocket messages and event trace. The generic handshake and "
                        "message transport remain Starlette 1.6.0 behavior."
                    ),
                    supporting_sources=(
                        _HTTP_ROUTE_SCOPE_SETUP,
                        _WEBSOCKET_ROUTE_SCOPE_IMPLEMENTATION,
                        _STARLETTE_WEBSOCKET_MATCHING,
                    ),
                ),
            },
            "exclusions": {
                "test_invalid_method_doesnt_match": _exclusion(
                    "tests/test_route_scope.py",
                    "test_invalid_method_doesnt_match",
                    (
                        "The function observes only a 405 after a path match with an unsupported "
                        "method. The existing method-not-allowed case is a cross-reference to the "
                        "Starlette routing contract, not a FastAPI-specific claim."
                    ),
                    supporting_sources=(
                        _STARLETTE_ROUTE_MATCHING,
                        _STARLETTE_ROUTER_DISPATCH,
                    ),
                    related_workflows=(
                        _workflow(
                            _ROUTING_SURFACE,
                            "fastapi.routing.method-not-allowed",
                            ["dispatch"],
                            ["http.status"],
                        ),
                    ),
                    owner="Starlette-RS generic HTTP method matching",
                ),
                "test_invalid_path_doesnt_match": _exclusion(
                    "tests/test_route_scope.py",
                    "test_invalid_path_doesnt_match",
                    (
                        "The function observes only a 404 when no registered path matches. The "
                        "existing not-found case is a cross-reference to the generic Starlette "
                        "router-default contract; this near-match path variant is not a separate "
                        "FastAPI behavior."
                    ),
                    supporting_sources=(_STARLETTE_ROUTER_DISPATCH,),
                    related_workflows=(
                        _workflow(
                            _ROUTING_SURFACE,
                            "fastapi.routing.not-found",
                            ["dispatch"],
                            ["http.status"],
                        ),
                    ),
                    owner="Starlette-RS generic HTTP route-miss behavior",
                ),
                "test_websocket_invalid_path_doesnt_match": _exclusion(
                    "tests/test_route_scope.py",
                    "test_websocket_invalid_path_doesnt_match",
                    (
                        "The function exercises only the generic unmatched-WebSocket route path "
                        "and TestClient handshake failure. FastAPI's APIWebSocketRoute scope "
                        "metadata is exercised by test_websocket; generic no-match and close "
                        "behavior remain in the Starlette contract."
                    ),
                    supporting_sources=(
                        _STARLETTE_WEBSOCKET_MATCHING,
                        _STARLETTE_ROUTER_DISPATCH,
                    ),
                    owner="Starlette-RS generic WebSocket matching and handshake behavior",
                ),
            },
        },
        "tests/test_application.py": {
            "test_mappings": {
                "test_get_path": _mapping(
                    "tests/test_application.py",
                    "test_get_path",
                    workflows=[
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-get-api-route",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        ),
                        _workflow(
                            _ROUTING_UPSTREAM,
                            "fastapi.test.test-extra-routes.test-get-api-route-not-decorated",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        ),
                        _workflow(
                            _ROUTING_SURFACE,
                            "fastapi.routing.not-found",
                            ["dispatch"],
                            _HTTP_BODY_SELECTORS,
                        ),
                    ],
                    rationale=(
                        "The source parametrizes an api_route endpoint, an add_api_route endpoint, "
                        "and an unmatched path. Existing independent workflows cover the two "
                        "registration forms plus the generic route-miss response."
                    ),
                    contract_gate=(
                        "The workflows use distinct path names and endpoint values. This mapping "
                        "does not claim the source's exact parsed JSON values or TestClient behavior; "
                        "the 404 branch is owned by the Starlette router contract."
                    ),
                    supporting_sources=(
                        _source(
                            "tests/main.py",
                            13,
                            22,
                            "api_route and add_api_route endpoints used by the successful cases",
                        ),
                    ),
                ),
                "test_enum_status_code_response": _mapping(
                    "tests/test_application.py",
                    "test_enum_status_code_response",
                    workflows=[
                        _workflow(
                            _ENUM_RECIPE,
                            "fastapi.test.test-application.test-enum-status-code-response",
                            ["get-enum-status-code"],
                            _HTTP_BODY_SELECTORS,
                        )
                    ],
                    rationale=(
                        "The input configures HTTPStatus.CREATED on a GET route and returns a JSON "
                        "string, exercising FastAPI's configured route status through ASGI."
                    ),
                    contract_gate=(
                        "The input workload uses the same path, status enum, and return value as "
                        "the source function but constructs its app independently. The source checks "
                        "parsed JSON; the recipe compares raw response bytes."
                    ),
                    supporting_sources=(
                        _source(
                            "tests/main.py",
                            191,
                            193,
                            "HTTPStatus.CREATED route declaration and endpoint return value",
                        ),
                        _source(
                            "fastapi/routing.py",
                            1161,
                            1223,
                            "FastAPI APIRoute initialization receives and stores the configured status code",
                        ),
                    ),
                ),
            },
            "exclusions": {
                "test_swagger_ui": _exclusion(
                    "tests/test_application.py",
                    "test_swagger_ui",
                    (
                        "The function checks Swagger UI HTML, its media type, and an OAuth redirect "
                        "snippet. Docs HTML/helper behavior belongs to the OpenAPI/docs wave."
                    ),
                    supporting_sources=(
                        _source(
                            "fastapi/applications.py",
                            1105,
                            1158,
                            "FastAPI configures OpenAPI, Swagger UI, OAuth redirect, and ReDoc routes",
                        ),
                    ),
                    owner="OpenAPI/docs wave",
                ),
                "test_swagger_ui_oauth2_redirect": _exclusion(
                    "tests/test_application.py",
                    "test_swagger_ui_oauth2_redirect",
                    (
                        "The function checks the OAuth redirect HTML body and media type; this "
                        "docs-specific behavior belongs to the OpenAPI/docs wave."
                    ),
                    supporting_sources=(
                        _source(
                            "fastapi/applications.py",
                            1105,
                            1158,
                            "FastAPI configures OpenAPI, Swagger UI, OAuth redirect, and ReDoc routes",
                        ),
                    ),
                    owner="OpenAPI/docs wave",
                ),
                "test_redoc": _exclusion(
                    "tests/test_application.py",
                    "test_redoc",
                    (
                        "The function checks ReDoc HTML, its media type, and a versioned frontend "
                        "asset reference; this docs-specific behavior belongs to the OpenAPI/docs wave."
                    ),
                    supporting_sources=(
                        _source(
                            "fastapi/applications.py",
                            1105,
                            1158,
                            "FastAPI configures OpenAPI, Swagger UI, OAuth redirect, and ReDoc routes",
                        ),
                    ),
                    owner="OpenAPI/docs wave",
                ),
                "test_openapi_schema": _exclusion(
                    "tests/test_application.py",
                    "test_openapi_schema",
                    (
                        "The function compares the complete OpenAPI document for the shared main.app "
                        "route set. The smaller existing OpenAPI inputs select different routes; this "
                        "full document belongs to the OpenAPI/docs wave."
                    ),
                    supporting_sources=(
                        _source(
                            "tests/main.py",
                            1,
                            22,
                            "shared application configuration and the first two public routes",
                        ),
                        _source(
                            "fastapi/applications.py",
                            1105,
                            1158,
                            "FastAPI configures its OpenAPI endpoint and documentation routes",
                        ),
                    ),
                    owner="OpenAPI/docs wave",
                ),
            },
        },
    },
}

__all__ = [
    "ROUTE_APPLICATION_TEST_SOURCE_REVIEW",
    "SOURCE_IDENTITIES",
]
