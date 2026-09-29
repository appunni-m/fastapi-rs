"""Source-reviewed app, routing, dependency, lifecycle, and WebSocket case links.

This module is an atlas input only. Workflow cases are independently authored
stimuli, not copied tests or expected outputs. Every positive link is deliberately
partial until the full FastAPI manifest and runner contract are complete.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT.parent / "fastapi"
TEST_ROOT = FASTAPI_ROOT / "tests"

SOURCE_IDENTITY = {
    "fastapi_version": "0.141.1",
    "fastapi_commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "starlette_version": "1.6.0",
    "starlette_commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}


def _source(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(test_path: str, function_name: str) -> dict[str, object]:
    path = TEST_ROOT / Path(test_path).name
    tree = ast.parse(path.read_text(encoding="utf-8"))
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
        "pinned FastAPI test stimulus and asserted behavior for this exact function",
    )


def _all_test_function_spans(test_path: str) -> list[dict[str, object]]:
    path = TEST_ROOT / Path(test_path).name
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        _source(
            test_path,
            node.lineno,
            node.end_lineno or node.lineno,
            "pinned FastAPI test function reviewed for this wave exclusion",
        )
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def _case_link(
    recipe_path: str,
    case_id: str,
    selectors: list[str],
) -> dict[str, object]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "workflow_selectors": list(selectors),
    }


def _review(
    test_path: str,
    function_name: str,
    feature_ids: list[str],
    observation_selectors: list[str],
    rationale: str,
    links: list[dict[str, object]],
    contract_gate: str,
    implementation_sources: tuple[dict[str, object], ...] = (),
) -> dict[str, object]:
    link_text = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} ({', '.join(link['workflow_selectors'])})"
        for link in links
    )
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(observation_selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": contract_gate
        if contract_gate.startswith("Partial:")
        else f"Partial: {contract_gate}",
        "stimulus_notes": (
            "Input-only workflow case link(s): "
            + link_text
            + ". Case IDs and observation selectors are references to the reviewed recipes; "
            "they contain no expected outputs."
        ),
        "workflow_cases": list(links),
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            *implementation_sources,
        ],
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, object]],
) -> dict[str, object]:
    return {"rationale": rationale, "functions": functions}


_ROUTER_INCLUDE = _source(
    "fastapi/routing.py",
    3268,
    3319,
    "FastAPI rejects cyclic router inclusion, validates empty prefixes, and merges included routes/lifespans",
)
_DEPENDENCY_SOLVER = _source(
    "fastapi/dependencies/utils.py",
    566,
    680,
    "FastAPI enters generator dependencies, applies overrides, caches dependency results, and resolves dependency values",
)
_LIFESPAN_MERGE = _source(
    "fastapi/routing.py",
    233,
    254,
    "FastAPI merges app and router lifespan contexts and combines yielded state",
)
_WEBSOCKET_ROUTE = _source(
    "fastapi/routing.py",
    801,
    837,
    "FastAPI constructs APIWebSocketRoute dependency graphs and installs the matched FastAPI route in scope",
)
_WEBSOCKET_RESOLUTION = _source(
    "fastapi/routing.py",
    764,
    797,
    "FastAPI resolves WebSocket dependencies and applies its WebSocket validation handler",
)
_HTTP_EXCEPTION = _source(
    "fastapi/exception_handlers.py",
    11,
    34,
    "FastAPI maps HTTP and request-validation exceptions to HTTP responses and closes invalid WebSockets",
)
_APP_HANDLER_REGISTRATION = _source(
    "fastapi/applications.py",
    1000,
    1012,
    "FastAPI installs default HTTP/WebSocket handlers and retains user-supplied handlers",
)
_STARLETTE_EXCEPTION_DISPATCH = _source(
    "starlette/middleware/exceptions.py",
    36,
    63,
    "Starlette 1.6.0 registers exception classes and dispatches HTTP/WebSocket exceptions through ExceptionMiddleware",
)

_HTTP_BODY_STATUS = ["http_response.status", "http_response.body"]
_HTTP_FULL = ["http_response.status", "http_response.headers", "http_response.body"]
_HTTP_ROUTING = [*_HTTP_FULL]
_HTTP_ROUTING_SEND = [*_HTTP_FULL, "asgi.send.message_types"]
_CONSTRUCTION = [
    "construction.outcome",
    "construction.exception_class",
    "construction.exception_message",
]
_LIFESPAN = [
    "asgi_lifespan.event_order",
    "asgi_lifespan.startup",
    "asgi_lifespan.shutdown",
    "asgi_lifespan.application_errors",
    "asgi_lifespan.workload_trace",
    "http_response.status",
    "http_response.body",
    *_CONSTRUCTION,
]
_WS_FULL = [
    "websocket.close_code",
    "websocket.close_reason",
    "websocket.event_order",
    "websocket.messages",
    *_CONSTRUCTION,
]
_WS_DEPENDENCY = [
    "websocket.close_code",
    "websocket.event_order",
    "websocket.messages",
    *_CONSTRUCTION,
]


APP_DEPENDENCY_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_application.py": _module(
        "The app module contains route dispatch, configured status codes, docs UI, and a full OpenAPI snapshot; only the route/status behaviors linked below belong to this wave.",
        {
            "test_get_path": _review(
                "tests/test_application.py",
                "test_get_path",
                ["app-routing"],
                [
                    "http.status",
                    "http.headers.ordered",
                    "http.body.bytes",
                    "asgi.send.message_types",
                ],
                "The source parametrizes an api_route endpoint, an add_api_route endpoint, and an unmatched path; the independent cases cover both successful registration forms and the existing 404 branch.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/application-route-registration-upstream.yaml",
                        "fastapi.application.api-route-dispatch",
                        _HTTP_ROUTING_SEND,
                    ),
                    _case_link(
                        "tests/fixtures/input-recipes/parity/application-route-registration-upstream.yaml",
                        "fastapi.application.add-api-route-dispatch",
                        _HTTP_ROUTING_SEND,
                    ),
                    _case_link(
                        "tests/fixtures/input-recipes/parity/routing-surface.yaml",
                        "fastapi.routing.not-found",
                        _HTTP_ROUTING,
                    ),
                ],
                "Partial: all three path branches now have input coverage, with exact status, ordered headers, body bytes, and ASGI send order for the two successful registration forms. The workflow uses independently authored endpoints and does not claim TestClient behavior or broader route registration semantics; generic Starlette 1.6.0 routing remains in Starlette-RS.",
                (
                    _source(
                        "tests/main.py",
                        13,
                        22,
                        "Pinned app fixture registers the tested endpoint once with api_route and once with add_api_route",
                    ),
                ),
            ),
            "test_enum_status_code_response": _review(
                "tests/test_application.py",
                "test_enum_status_code_response",
                ["app-routing"],
                ["http.status", "http.body.json"],
                "A configured HTTPStatus enum is converted into the route response status while the endpoint value remains the response body.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/application-enum-status-code-upstream.yaml",
                        "fastapi.test.test-application.test-enum-status-code-response",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the case uses an independently named route and enum value. It samples configured status propagation and response emission, not the source's exact endpoint/body value or TestClient response parsing.",
                (
                    _source(
                        "fastapi/applications.py",
                        1176,
                        1217,
                        "FastAPI path-operation decorator accepts and stores the configured status code",
                    ),
                ),
            ),
        },
    ),
    "tests/test_callable_endpoint.py": _module(
        "The partial endpoint case covers callable endpoint signature inspection and route invocation through FastAPI's public decorator.",
        {
            "test_partial": _review(
                "tests/test_callable_endpoint.py",
                "test_partial",
                ["app-routing", "dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI registers a functools.partial endpoint and supplies its remaining query argument.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/callable-endpoint-partial-upstream.yaml",
                        "fastapi.test.test-callable-endpoint.test-partial",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the workflow uses a fresh endpoint and query value; it covers partial-call binding and public route dispatch, not the source's exact function or TestClient convenience.",
                (
                    _source(
                        "fastapi/dependencies/utils.py",
                        271,
                        347,
                        "FastAPI inspects callable endpoint signatures while building dependency nodes",
                    ),
                ),
            )
        },
    ),
    "tests/test_custom_route_class.py": _module(
        "The route-class workflow covers nested APIRouter inclusion and request dispatch through custom APIRoute subclasses; direct Python class-introspection and OpenAPI snapshots are excluded below.",
        {
            "test_get_path": _review(
                "tests/test_custom_route_class.py",
                "test_get_path",
                ["app-routing"],
                ["http.status", "http.body.json"],
                "Three nested routers preserve their route declarations and dispatch to the endpoint registered at each prefix depth.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/routing-upstream.yaml",
                        "fastapi.test.test-custom-route-class.test-get-path",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the workflow recreates nested route-class dispatch with independent route names and values. It does not establish public APIRoute object identity or full OpenAPI behavior; generic path matching belongs to Starlette-RS.",
                (_ROUTER_INCLUDE,),
            )
        },
    ),
    "tests/test_empty_router.py": _module(
        "The source distinguishes dispatch through an included router whose endpoint path is empty from FastAPI's rejection of an empty path with no include prefix.",
        {
            "test_use_empty": _review(
                "tests/test_empty_router.py",
                "test_use_empty",
                ["app-routing"],
                ["http.status", "http.body.json"],
                "An included router with a route path of the empty string serves both the prefix and its slash form.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/routing-upstream.yaml",
                        "fastapi.test.test-empty-router.test-use-empty",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the case uses an independently named route and response. It samples empty-route inclusion and slash forms; generic redirect and route-matching semantics remain Starlette-RS behavior.",
                (_ROUTER_INCLUDE,),
            ),
            "test_include_empty": _review(
                "tests/test_empty_router.py",
                "test_include_empty",
                ["app-routing", "public-api-errors"],
                _CONSTRUCTION,
                "Including an empty APIRouter without a prefix raises FastAPIError during application construction.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/empty-router-include-construction-upstream.yaml",
                        "fastapi.routing.empty-router-include-construction",
                        _CONSTRUCTION,
                    )
                ],
                "The independent workload performs the same public include_router operation with an empty router and no prefix; parity remains gated by the complete public manifest and identity-checked runner.",
                (
                    _source(
                        "fastapi/routing.py",
                        3281,
                        3295,
                        "FastAPI rejects a route whose path and router include prefix are both empty",
                    ),
                ),
            ),
        },
    ),
    "tests/test_include_route.py": _module(
        "The route inclusion case exercises the public APIRouter.route decorator and FastAPI app inclusion; Request injection and Starlette response handling are not its parity claim.",
        {
            "test_sub_router": _review(
                "tests/test_include_route.py",
                "test_sub_router",
                ["app-routing"],
                ["http.status", "http.body.json"],
                "FastAPI includes an independently defined router route and dispatches an HTTP request through the composed app.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/routing-surface.yaml",
                        "fastapi.routing.include-router-prefix",
                        _HTTP_ROUTING,
                    )
                ],
                "Partial: the workflow uses a new route path, prefix, and response. It samples APIRouter inclusion and dispatch only; the source's Request injection, JSONResponse rendering, and TestClient parsing are not claimed.",
                (_ROUTER_INCLUDE,),
            )
        },
    ),
    "tests/test_router_circular_import.py": _module(
        "FastAPI rejects a public APIRouter self-inclusion during construction.",
        {
            "test_router_circular_import": _review(
                "tests/test_router_circular_import.py",
                "test_router_circular_import",
                ["app-routing", "public-api-errors"],
                _CONSTRUCTION,
                "Including the same APIRouter instance into itself raises the source-asserted construction exception.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/router-circular-self-include-upstream.yaml",
                        "fastapi.routing.router-self-include-construction",
                        _CONSTRUCTION,
                    )
                ],
                "The workflow repeats the public self-include operation and captures construction outcome/class/message; the full public manifest is still required before an executable parity claim.",
                (_ROUTER_INCLUDE,),
            )
        },
    ),
    "tests/test_router_events.py": _module(
        "The existing lifespan recipe covers the module's router/app startup, shutdown, state merging, and generator-lifespan behaviors. The deprecated on_event warning and TestClient.app_state are explicit gaps.",
        {
            name: _review(
                "tests/test_router_events.py",
                name,
                ["websocket-lifecycle"],
                [
                    "asgi.lifespan.event_order",
                    "asgi.lifespan.startup",
                    "asgi.lifespan.shutdown",
                    "asgi.lifespan.application_errors",
                    "asgi.lifespan.workload_trace",
                    "http.status",
                    "http.body.bytes",
                ],
                description,
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml",
                        case_id,
                        _LIFESPAN,
                    )
                ],
                "Partial: direct ASGI lifespan events and request observations do not capture the source's TestClient.app_state or exact DeprecationWarning for on_event. Generic lifespan protocol mechanics remain the Starlette 1.6.0 contract.",
                (_LIFESPAN_MERGE,),
            )
            for name, case_id, description in [
                (
                    "test_router_events",
                    "fastapi.lifecycle.router-events-legacy",
                    "App and nested-router deprecated startup/shutdown handlers run in registration order.",
                ),
                (
                    "test_app_lifespan_state",
                    "fastapi.lifecycle.app-lifespan-state",
                    "The app lifespan opens with state and the route observes the merged lifespan value.",
                ),
                (
                    "test_router_nested_lifespan_state",
                    "fastapi.lifecycle.nested-lifespan-state",
                    "Nested router lifespan contexts merge state across the app/router tree.",
                ),
                (
                    "test_router_nested_lifespan_state_overriding_by_parent",
                    "fastapi.lifecycle.parent-lifespan-state-override",
                    "Parent lifespan state wins when app and nested-router keys overlap.",
                ),
                (
                    "test_merged_no_return_lifespans_return_none",
                    "fastapi.lifecycle.empty-merged-lifespan-state",
                    "Merged lifespans preserve the no-state case when contexts yield no mapping.",
                ),
                (
                    "test_merged_mixed_state_lifespans",
                    "fastapi.lifecycle.mixed-merged-lifespan-state",
                    "Merged lifespans combine a state-yielding context with a no-state context.",
                ),
                (
                    "test_router_async_shutdown_handler",
                    "fastapi.lifecycle.async-shutdown-handler",
                    "An async router shutdown handler runs after the app shutdown phase.",
                ),
                (
                    "test_router_sync_generator_lifespan",
                    "fastapi.lifecycle.sync-generator-lifespan",
                    "A sync generator lifespan enters and exits around the app request.",
                ),
                (
                    "test_router_async_generator_lifespan",
                    "fastapi.lifecycle.async-generator-lifespan",
                    "An async generator lifespan enters and exits around the app request.",
                ),
                (
                    "test_startup_shutdown_handlers_as_parameters",
                    "fastapi.lifecycle.parameter-event-handlers",
                    "App and router event handlers accept the documented startup/shutdown registration shape.",
                ),
            ]
        },
    ),
    "tests/test_dependency_after_yield_raise.py": _module(
        "Existing yield-lifecycle cases sample exception handling and cleanup after a yielded dependency; TestClient exception policy and every sync/async exception combination remain partial.",
        {
            "test_catching": _review(
                "tests/test_dependency_after_yield_raise.py",
                "test_catching",
                ["dependency-security", "public-api-errors"],
                ["http.status", "http.body.json"],
                "A yielded dependency catches an endpoint exception and raises FastAPI HTTPException during cleanup.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.yield-caught-error",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workflow uses a new dependency and exception value. It samples caught-error propagation through yield cleanup; the source's exact 418 detail and TestClient behavior are not claimed.",
                (_DEPENDENCY_SOLVER, _HTTP_EXCEPTION),
            ),
            "test_broken_raise": _review(
                "tests/test_dependency_after_yield_raise.py",
                "test_broken_raise",
                ["dependency-security", "asgi-error-propagation"],
                ["http.status", "http.body.bytes", "asgi.application_error.exception"],
                "A generator dependency raises after its endpoint has returned, and FastAPI unwinds it after the response body is produced.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.after-yield-cleanup-error",
                        [
                            "http_response.status",
                            "http_response.body",
                            "application_error.validation_error_class",
                        ],
                    )
                ],
                "Partial: the case observes response-before-cleanup-error ordering with a distinct cleanup error class; TestClient's re-raise policy and exact ValueError message remain Starlette/Python-profile gaps.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_broken_no_raise": _review(
                "tests/test_dependency_after_yield_raise.py",
                "test_broken_no_raise",
                ["dependency-security", "asgi-error-propagation"],
                ["http.status", "http.body.bytes", "asgi.application_error.exception"],
                "The same post-response cleanup failure is observed when the client suppresses server exceptions.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.after-yield-cleanup-error",
                        [
                            "http_response.status",
                            "http_response.body",
                            "application_error.validation_error_class",
                        ],
                    )
                ],
                "Partial: direct ASGI error capture differs from TestClient(raise_server_exceptions=False), and the independent workflow uses a different cleanup exception. Only response-before-cleanup-error sequencing is sampled.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_broken_return_finishes": _review(
                "tests/test_dependency_after_yield_raise.py",
                "test_broken_return_finishes",
                ["dependency-security", "asgi-error-propagation"],
                ["http.status", "http.body.json"],
                "The cleanup-failing dependency still leaves a completed response observable when the client suppresses server exceptions.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.after-yield-cleanup-error",
                        [
                            "http_response.status",
                            "http_response.body",
                            "application_error.validation_error_class",
                        ],
                    )
                ],
                "Partial: this function repeats the same route and 200 response assertion as test_broken_no_raise with client construction outside a context manager; the direct ASGI case samples only response-before-cleanup-error order.",
                (_DEPENDENCY_SOLVER,),
            ),
        },
    ),
    "tests/test_dependency_after_yield_websockets.py": _module(
        "Existing cases exercise successful and failing yielded WebSocket dependencies, including cleanup errors across the WebSocket lifecycle.",
        {
            "test_websocket_dependency_after_yield": _review(
                "tests/test_dependency_after_yield_websockets.py",
                "test_websocket_dependency_after_yield",
                ["dependency-security", "websocket-lifecycle"],
                ["websocket.messages", "websocket.event_order", "websocket.close_code"],
                "A yielded dependency remains active through the WebSocket endpoint and is cleaned up after disconnect.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.websocket-yield-cleanup",
                        [
                            "websocket.messages",
                            "websocket.event_order",
                            "websocket.close_code",
                            "http_response.status",
                            "http_response.body",
                        ],
                    )
                ],
                "Partial: the workflow uses an independent route/session trace and closes through a direct ASGI peer event, not Starlette TestClient's WebSocketSession API.",
                (_WEBSOCKET_ROUTE, _DEPENDENCY_SOLVER),
            ),
            "test_websocket_dependency_after_yield_broken": _review(
                "tests/test_dependency_after_yield_websockets.py",
                "test_websocket_dependency_after_yield_broken",
                ["asgi-error-propagation", "websocket-lifecycle"],
                ["websocket.messages", "websocket.event_order", "asgi.application_error.exception"],
                "A yielded WebSocket dependency raises during cleanup; the case records both ASGI WebSocket events and the surfaced exception.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-after-yield-websocket-broken-upstream.yaml",
                        "fastapi.test.test-dependency-after-yield-websockets.test-websocket-dependency-after-yield-broken",
                        [
                            "application_error.exception",
                            "websocket.event_order",
                            "websocket.messages",
                        ],
                    )
                ],
                "Partial: the workflow uses an independently authored cleanup exception and a direct disconnect event; it checks propagation shape, not the source's exact endpoint/helper objects or TestClient session mechanics.",
                (_WEBSOCKET_ROUTE, _DEPENDENCY_SOLVER),
            ),
        },
    ),
    "tests/test_dependency_cache.py": _module(
        "The two HTTP dependency cases cover FastAPI per-request cache reuse and explicit cache bypass; the security-scope cache test belongs to the security wave.",
        {
            "test_normal_counter": _review(
                "tests/test_dependency_cache.py",
                "test_normal_counter",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A repeated dependency in one request reuses the cached result.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                        "fastapi.dependencies.cache-reuse",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the case uses a new dependency graph and HTTP body; it samples request-local cache reuse but not the exact source counter values or callable identities.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_sub_counter": _review(
                "tests/test_dependency_cache.py",
                "test_sub_counter",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A common sub-dependency resolves once when reached through multiple parents in one request.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                        "fastapi.dependencies.cache-reuse",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the independent graph samples same-request sub-dependency reuse with different names and values; generic request dispatch is Starlette-RS behavior.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_sub_counter_no_cache": _review(
                "tests/test_dependency_cache.py",
                "test_sub_counter_no_cache",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A dependency declared with use_cache=False is re-evaluated through repeated graph edges.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                        "fastapi.dependencies.cache-bypass",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the independent graph uses new dependency functions and returned markers. It covers explicit cache bypass only.",
                (_DEPENDENCY_SOLVER,),
            ),
        },
    ),
    "tests/test_dependency_class.py": _module(
        "Callable class dependencies are invoked through FastAPI's dependency solver.",
        {
            "test_class_dependency": _review(
                "tests/test_dependency_class.py",
                "test_class_dependency",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI inspects and invokes a class-based callable dependency through an HTTP route.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-callables.yaml",
                        "fastapi.dependencies.callable-instances-and-methods",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workflow uses new callable instances and route payloads; callable classification and invocation are sampled, not every class-instance variant.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_dependency_partial.py": _module(
        "The callable recipe covers functools.partial signature inspection in a Depends declaration.",
        {
            "test_dependency_types_with_partial": _review(
                "tests/test_dependency_partial.py",
                "test_dependency_types_with_partial",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI resolves a partial callable's remaining declared dependency parameters.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-callables.yaml",
                        "fastapi.dependencies.partial-callable-signatures",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the independent callable and values differ from the source; only public Depends signature resolution is sampled.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_dependency_wrapped.py": _module(
        "The callable recipe covers a wrapped class dependency through the public Depends/route path.",
        {
            "test_class_dependency": _review(
                "tests/test_dependency_wrapped.py",
                "test_class_dependency",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI unwraps and inspects the decorated callable used as a dependency.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-callables.yaml",
                        "fastapi.dependencies.wrapped-callable-signatures",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the case uses an independently wrapped callable and fresh values; it does not assert source decorator identity.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_dependency_pep695.py": _module(
        "The existing callable workflow samples a PEP 695 dependency type alias under the pinned Python profile.",
        {
            "test_pep695_type_dependencies": _review(
                "tests/test_dependency_pep695.py",
                "test_pep695_type_dependencies",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI resolves a dependency whose annotation uses a PEP 695 type alias.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-callables.yaml",
                        "fastapi.dependencies.pep695-type-alias",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the independently authored alias and endpoint values differ; the input samples alias resolution only under its declared Python version gate.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_stringified_annotation_dependency.py": _module(
        "The HTTP dependency case is in scope; the module's generated OpenAPI snapshot is assigned to the OpenAPI wave.",
        {
            "test_get": _review(
                "tests/test_stringified_annotation_dependency.py",
                "test_get",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI resolves a dependency from a stringified endpoint annotation and invokes it for a request.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-callables.yaml",
                        "fastapi.dependencies.stringified-annotation",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the case uses independent annotations, callables, and values. Its OpenAPI pointers are deliberately not claimed by this routing/dependency row.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_generic_parameterless_depends.py": _module(
        "The generic parameterless Depends HTTP case is in scope; its OpenAPI snapshot is not.",
        {
            "test_generic_parameterless_depends": _review(
                "tests/test_generic_parameterless_depends.py",
                "test_generic_parameterless_depends",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI resolves parameterless Depends declarations for an HTTP endpoint.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave.yaml",
                        "fastapi.dependency-wave.generic-parameterless.test-generic-parameterless-depends",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workflow uses independently declared generic dependencies and routes; it does not cover the module's OpenAPI projection.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_depends_hashable.py": _module(
        "A public HTTP dependency workflow exercises the observable effects of equivalent Depends instances and their cache keys.",
        {
            "test_depends_hashable": _review(
                "tests/test_depends_hashable.py",
                "test_depends_hashable",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "Equivalent dependency declarations are resolved through a public route so their shared cache behavior is observable.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/public-model-edge-cases-upstream.yaml",
                        "fastapi.depends-hashability.equivalent-dependencies",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workload exercises an independent dependency graph and output values; it does not assert the Python hash/equality value directly.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_dependency_overrides.py": _module(
        "The existing lifecycle case samples replacement dependency resolution. Request-parameter-heavy subdependency variants are explicitly outside this wave.",
        {
            "test_override_simple": _review(
                "tests/test_dependency_overrides.py",
                "test_override_simple",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "FastAPI's dependency_overrides mapping substitutes a callable through the public app route path.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                        "fastapi.dependencies.override-resolution",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the source parametrizes multiple app/router dependency configurations and query inputs; the independent case covers one replacement dependency. Other parameter extraction and validation assertions remain assigned to that wave.",
                (_DEPENDENCY_SOLVER,),
            )
        },
    ),
    "tests/test_dependency_contextvars.py": _module(
        "The existing case observes a dependency-set ContextVar across FastAPI's user-middleware stack.",
        {
            "test_dependency_contextvars": _review(
                "tests/test_dependency_contextvars.py",
                "test_dependency_contextvars",
                ["dependency-security", "middleware-integrations"],
                ["http.status", "http.headers.ordered", "http.body.json"],
                "The dependency value remains visible to middleware and the endpoint under the FastAPI async exit-stack placement.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.contextvars-through-middleware",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the workflow uses a new ContextVar, middleware, and route. Generic middleware ordering and ASGI dispatch remain Starlette-RS behavior.",
                (
                    _DEPENDENCY_SOLVER,
                    _source(
                        "fastapi/applications.py",
                        1020,
                        1062,
                        "FastAPI positions AsyncExitStackMiddleware inside user middleware to preserve ContextVar state",
                    ),
                ),
            )
        },
    ),
    "tests/test_dependency_yield_except_httpexception.py": _module(
        "A yielded dependency observes an endpoint HTTPException, skips its normal post-yield commit, and still finalizes; a separate success case commits the yielded value.",
        {
            "test_dependency_gets_exception": _review(
                "tests/test_dependency_yield_except_httpexception.py",
                "test_dependency_gets_exception",
                ["dependency-security", "public-api-errors"],
                ["http.status", "http.body.json"],
                "The dependency catches and re-raises the endpoint HTTPException; the transaction copy is not committed and the finalizer runs.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-yield-transaction-upstream.yaml",
                        "fastapi.dependencies.yield-http-exception-rollback",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the input observes HTTPException response mapping and a follow-up state read; it uses an independently authored state store and omits the source's PUT path/body parsing.",
                (_DEPENDENCY_SOLVER, _HTTP_EXCEPTION),
            ),
            "test_dependency_no_exception": _review(
                "tests/test_dependency_yield_except_httpexception.py",
                "test_dependency_no_exception",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A normal endpoint return lets the yielded dependency commit its copied state and run its finalizer.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-yield-transaction-upstream.yaml",
                        "fastapi.dependencies.yield-success-commit",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the input uses a separate route and in-memory state shape; it observes response and committed state but omits source PUT/body parsing and fixture reset mechanics.",
                (_DEPENDENCY_SOLVER,),
            ),
        },
    ),
    "tests/test_dependency_yield_scope.py": _module(
        "The dependency lifecycle input covers function/request scope cleanup; additional app/router scope combinations and invalid-scope errors remain unrepresented.",
        {
            "test_function_scope": _review(
                "tests/test_dependency_yield_scope.py",
                "test_function_scope",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A function-scoped yielded dependency is finalized before the request finishes its response lifecycle.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                        "fastapi.dependencies.yield-scope-cleanup",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workflow independently authors its resource and event trace; it does not cover every nested/app/router-level scope combination in the source module.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_request_scope": _review(
                "tests/test_dependency_yield_scope.py",
                "test_request_scope",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A request-scoped yielded dependency remains active through response processing and is finalized with the request.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                        "fastapi.dependencies.yield-scope-cleanup",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workflow samples request cleanup through its own lifecycle trace and route; it does not establish every source scope combination.",
                (_DEPENDENCY_SOLVER,),
            ),
        },
    ),
    "tests/test_dependency_yield_scope_websockets.py": _module(
        "The existing WebSocket lifecycle cases distinguish function-scope and request-scope dependency cleanup around one session.",
        {
            "test_function_scope": _review(
                "tests/test_dependency_yield_scope_websockets.py",
                "test_function_scope",
                ["dependency-security", "websocket-lifecycle"],
                ["websocket.messages", "websocket.close_code"],
                "A function-scoped yielded dependency is finalized at the end of the WebSocket endpoint function.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.websocket-function-scope",
                        [
                            "websocket.messages",
                            "websocket.close_code",
                            "http_response.status",
                            "http_response.body",
                        ],
                    )
                ],
                "Partial: the input uses a fresh WebSocket route and resource trace; it does not recreate the source endpoint's resource objects or TestClient session.",
                (_WEBSOCKET_ROUTE, _DEPENDENCY_SOLVER),
            ),
            "test_request_scope": _review(
                "tests/test_dependency_yield_scope_websockets.py",
                "test_request_scope",
                ["dependency-security", "websocket-lifecycle"],
                ["websocket.messages", "websocket.close_code"],
                "A request-scoped yielded dependency remains live through the WebSocket session and is finalized after disconnect.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.websocket-request-scope",
                        [
                            "websocket.messages",
                            "websocket.close_code",
                            "http_response.status",
                            "http_response.body",
                        ],
                    )
                ],
                "Partial: the input uses a fresh WebSocket route and resource trace; it samples disconnect cleanup but not all nested and named scope variants.",
                (_WEBSOCKET_ROUTE, _DEPENDENCY_SOLVER),
            ),
        },
    ),
    "tests/test_dependency_contextmanager.py": _module(
        "The existing lifecycle recipe provides nested generator-dependency and post-response cleanup samples. The full sync/async exception matrix and background-task ordering are not claimed.",
        {
            "test_context_b": _review(
                "tests/test_dependency_contextmanager.py",
                "test_context_b",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "Nested yield dependencies enter in dependency order and clean up in reverse order around a successful route.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.context-manager-nesting",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the case uses an independent pair of context-managed dependencies and response state. It does not establish the module's complete sync/async exception matrix.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_async_state": _review(
                "tests/test_dependency_contextmanager.py",
                "test_async_state",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "An async generator dependency exposes its pre-cleanup value and completes cleanup after the route.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.context-manager-nesting",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the existing nested async context case samples lifecycle order with independent values; it does not reproduce this module's full middleware headers/state matrix.",
                (_DEPENDENCY_SOLVER,),
            ),
            "test_sync_state": _review(
                "tests/test_dependency_contextmanager.py",
                "test_sync_state",
                ["dependency-security"],
                ["http.status", "http.body.json"],
                "A sync generator dependency enters before route execution and finishes after the response is formed.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml",
                        "fastapi.dependencies.context-manager-nesting",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the independent nested workflow uses two sync generator dependencies under contextlib context managers; it samples sync enter/exit behavior but not this function's global-state assertion or response value.",
                (_DEPENDENCY_SOLVER,),
            ),
        },
    ),
    "tests/test_exception_handlers.py": _module(
        "FastAPI-specific HTTPException and RequestValidationError handler registration is linked to existing cases. ServerErrorMiddleware and TestClient server-exception policy are Starlette-owned and excluded.",
        {
            "test_override_http_exception": _review(
                "tests/test_exception_handlers.py",
                "test_override_http_exception",
                ["public-api-errors"],
                ["http.status", "http.body.json"],
                "A user-provided FastAPI HTTPException handler replaces the default detail response.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml",
                        "fastapi.test.test-exception-handlers.test-override-http-exception",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the workflow uses an independently named route, status, and JSON body. It samples the handler override path; generic exception dispatch and TestClient behavior are Starlette-RS responsibilities.",
                (_APP_HANDLER_REGISTRATION, _HTTP_EXCEPTION),
            ),
            "test_override_request_validation_exception": _review(
                "tests/test_exception_handlers.py",
                "test_override_request_validation_exception",
                ["public-api-errors"],
                ["http.status", "http.body.json"],
                "A user-provided RequestValidationError handler replaces FastAPI's default validation response.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml",
                        "fastapi.test.test-exception-handlers.test-override-request-validation-exception",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the independent workflow triggers validation on a different route and observes the override body/status, not the source's request or Pydantic error details. Request validation itself belongs to the validation wave.",
                (_APP_HANDLER_REGISTRATION, _HTTP_EXCEPTION),
            ),
        },
    ),
    "tests/test_starlette_exception.py": _module(
        "Only FastAPI's HTTPException compatibility/handler paths are linked here; generic Starlette HTTPException and no-body response semantics remain with Starlette-RS.",
        {
            "test_get_item_not_found": _review(
                "tests/test_starlette_exception.py",
                "test_get_item_not_found",
                ["public-api-errors"],
                ["http.status", "http.body.json"],
                "A FastAPI HTTPException raised by the source route is converted to the declared HTTP error response.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml",
                        "fastapi.test.test-starlette-exception.test-get-item-not-found",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the input changes the route/value and samples status/body mapping; Starlette exception dispatch and TestClient parsing are tracked separately.",
                (_HTTP_EXCEPTION,),
            ),
            "test_get_starlette_item_not_found": _review(
                "tests/test_starlette_exception.py",
                "test_get_starlette_item_not_found",
                ["public-api-errors"],
                ["http.status", "http.body.json"],
                "FastAPI's registered HTTPException handler also handles a Starlette HTTPException raised by an endpoint.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml",
                        "fastapi.test.test-starlette-exception.test-get-starlette-item-not-found",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the case uses a new route/value; class compatibility is a FastAPI-to-Starlette integration edge and generic exception dispatch remains Starlette-RS behavior.",
                (_APP_HANDLER_REGISTRATION, _HTTP_EXCEPTION),
            ),
            "test_no_body_status_code_exception_handlers": _review(
                "tests/test_starlette_exception.py",
                "test_no_body_status_code_exception_handlers",
                ["public-api-errors"],
                ["http.status", "http.body.bytes"],
                "The default FastAPI HTTPException handler suppresses a body for status codes that disallow one.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml",
                        "fastapi.test.test-starlette-exception.test-no-body-status-code-exception-handlers",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the independent case checks a selected no-body status only. Generic response framing and status-code body policy also belong to the pinned Starlette contract.",
                (_HTTP_EXCEPTION,),
            ),
            "test_no_body_status_code_with_detail_exception_handlers": _review(
                "tests/test_starlette_exception.py",
                "test_no_body_status_code_with_detail_exception_handlers",
                ["public-api-errors"],
                ["http.status", "http.body.bytes"],
                "The default FastAPI HTTPException handler suppresses a supplied detail body for a bodyless status.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml",
                        "fastapi.test.test-starlette-exception.test-no-body-status-code-with-detail-exception-handlers",
                        _HTTP_FULL,
                    )
                ],
                "Partial: the workflow uses one independent status/detail pair and exact bytes; generic Response emission belongs to Starlette-RS.",
                (_HTTP_EXCEPTION,),
            ),
        },
    ),
    "tests/test_router_include_context.py": _module(
        "Two public inclusion/context workflows are mapped. Direct private helpers, request-parameter/OpenAPI assertions, and generic Starlette mount/host/match behavior are excluded below.",
        {
            "test_router_include_context_matches_flattened_include_metadata": _review(
                "tests/test_router_include_context.py",
                "test_router_include_context_matches_flattened_include_metadata",
                ["app-routing"],
                ["http.status", "http.body.json"],
                "Nested FastAPI router inclusion preserves the effective route metadata used by runtime dispatch.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/router-context-metadata-upstream.yaml",
                        "fastapi.test.test-router-include-context.test-router-include-context-matches-flattened-include-metadata",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the workflow uses a fresh router tree and one HTTP observation; it does not compare every source metadata field or the OpenAPI projection.",
                (_ROUTER_INCLUDE,),
            ),
            "test_effective_route_context_is_available_in_scope_during_request": _review(
                "tests/test_router_include_context.py",
                "test_effective_route_context_is_available_in_scope_during_request",
                ["app-routing"],
                ["http.status", "http.body.json"],
                "The included route receives its effective FastAPI route context during request handling.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/router-effective-scope-context-upstream.yaml",
                        "fastapi.test.test-router-include-context.test-effective-route-context-is-available-in-scope-during-request",
                        _HTTP_BODY_STATUS,
                    )
                ],
                "Partial: the input independently builds one included route and exposes selected context in a response; the rest of the route-context test matrix remains open.",
                (_ROUTER_INCLUDE,),
            ),
        },
    ),
    "tests/test_ws_router.py": _module(
        "Existing cases cover root/router/prefix WebSocket dispatch, router dependency overrides, and a custom WebSocket exception handler. Parameter extraction, unmatched-route behavior, and user middleware are assigned to request/Starlette-RS contracts.",
        {
            name: _review(
                "tests/test_ws_router.py",
                name,
                ["app-routing", "websocket-lifecycle"],
                ["websocket.messages", "websocket.event_order", "websocket.close_code"],
                rationale,
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/websocket-router-routes-errors-upstream.yaml",
                        case_id,
                        _WS_FULL,
                    )
                ],
                "Partial: the input independently names route paths/messages and runs direct ASGI WebSocket sessions. Generic handshake/session behavior belongs to Starlette-RS.",
                (_WEBSOCKET_ROUTE,),
            )
            for name, case_id, rationale in [
                (
                    "test_app",
                    "fastapi.test.test-ws-router.test-app",
                    "FastAPI registers and dispatches a root WebSocket endpoint.",
                ),
                (
                    "test_router",
                    "fastapi.test.test-ws-router.test-router",
                    "FastAPI includes an APIRouter WebSocket endpoint.",
                ),
                (
                    "test_prefix_router",
                    "fastapi.test.test-ws-router.test-prefix-router",
                    "FastAPI applies an include_router prefix to a WebSocket route.",
                ),
                (
                    "test_native_prefix_router",
                    "fastapi.test.test-ws-router.test-native-prefix-router",
                    "FastAPI dispatches a WebSocket route from a router with its own prefix.",
                ),
                (
                    "test_router2",
                    "fastapi.test.test-ws-router.test-router2",
                    "A second WebSocket decorator form is registered through an APIRouter.",
                ),
            ]
        }
        | {
            name: _review(
                "tests/test_ws_router.py",
                name,
                ["dependency-security", "websocket-lifecycle"],
                ["websocket.messages", "websocket.event_order", "websocket.close_code"],
                rationale,
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/websocket-router-dependencies-upstream.yaml",
                        case_id,
                        _WS_DEPENDENCY,
                    )
                ],
                "Partial: the independent workflow samples router dependency resolution and app-level override through a direct ASGI WebSocket session; generic handshake/session behavior remains Starlette-RS-owned.",
                (_WEBSOCKET_ROUTE, _WEBSOCKET_RESOLUTION, _DEPENDENCY_SOLVER),
            )
            for name, case_id, rationale in [
                (
                    "test_router_ws_depends",
                    "fastapi.test.test-ws-router.test-router-ws-depends",
                    "An included APIRouter WebSocket route resolves its declared dependency.",
                ),
                (
                    "test_router_ws_depends_with_override",
                    "fastapi.test.test-ws-router.test-router-ws-depends-with-override",
                    "The app dependency_overrides mapping substitutes a dependency for an included WebSocket route.",
                ),
            ]
        }
        | {
            "test_depend_err_handler": _review(
                "tests/test_ws_router.py",
                "test_depend_err_handler",
                ["public-api-errors", "websocket-lifecycle"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "A registered exception handler catches a custom endpoint exception and closes a WebSocket with its configured code and reason.",
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/websocket-router-routes-errors-upstream.yaml",
                        "fastapi.test.test-ws-router.test-depend-err-handler",
                        _WS_FULL,
                    )
                ],
                "Partial: the input uses an independently defined exception and direct ASGI WebSocket session; FastAPI handler registration is paired with Starlette 1.6.0 exception dispatch.",
                (_APP_HANDLER_REGISTRATION, _STARLETTE_EXCEPTION_DISPATCH),
            )
        },
    ),
    "tests/test_ws_dependencies.py": _module(
        "Existing cases observe dependency call order and values accumulated at app, router, include, and endpoint scope for WebSocket routes.",
        {
            name: _review(
                "tests/test_ws_dependencies.py",
                name,
                ["dependency-security", "websocket-lifecycle"],
                ["websocket.messages", "websocket.event_order"],
                rationale,
                [
                    _case_link(
                        "tests/fixtures/input-recipes/parity/websockets-upstream.yaml",
                        case_id,
                        ["websocket.event_order", "websocket.messages"],
                    )
                ],
                "Partial: the cases use independent dependency functions/values and direct ASGI sessions. They sample FastAPI dependency ordering only; generic WebSocket session mechanics remain Starlette-RS behavior.",
                (_WEBSOCKET_ROUTE, _WEBSOCKET_RESOLUTION, _DEPENDENCY_SOLVER),
            )
            for name, case_id, rationale in [
                (
                    "test_index",
                    "fastapi.test.test-ws-dependencies.test-index",
                    "Application and endpoint dependencies resolve in declared order for the root WebSocket.",
                ),
                (
                    "test_routerindex",
                    "fastapi.test.test-ws-dependencies.test-routerindex",
                    "Application, include-level, router, and endpoint dependencies resolve in order.",
                ),
                (
                    "test_routerprefixindex",
                    "fastapi.test.test-ws-dependencies.test-routerprefixindex",
                    "The prefixed included router retains dependency ordering across all inclusion levels.",
                ),
            ]
        },
    ),
}


def _function_exclusion(
    test_path: str,
    function_name: str,
    reason: str,
    additional_sources: tuple[dict[str, object], ...] = (),
) -> dict[str, object]:
    return {
        "reason": reason,
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            *additional_sources,
        ],
    }


APP_DEPENDENCY_TEST_FUNCTION_EXCLUSIONS: dict[str, dict[str, dict[str, object]]] = {
    "tests/test_application.py": {
        name: _function_exclusion(
            "tests/test_application.py",
            name,
            "The function asserts FastAPI docs UI HTML or the full OpenAPI document; those behaviors are assigned to the OpenAPI/docs wave.",
            (
                _source(
                    "fastapi/applications.py",
                    1105,
                    1158,
                    "FastAPI configures its OpenAPI, Swagger UI, OAuth redirect, and ReDoc routes",
                ),
            ),
        )
        for name in (
            "test_swagger_ui",
            "test_swagger_ui_oauth2_redirect",
            "test_redoc",
            "test_openapi_schema",
        )
    },
    "tests/test_custom_route_class.py": {
        "test_route_classes": _function_exclusion(
            "tests/test_custom_route_class.py",
            "test_route_classes",
            "The function directly inspects APIRouter.routes Python objects with isinstance; the current Python-ASGI workflow schema does not observe Python object class identity.",
            (
                _source(
                    "fastapi/routing.py",
                    1126,
                    1159,
                    "APIRoute is the FastAPI route class extended by the test's custom classes",
                ),
            ),
        ),
        "test_openapi_schema": _function_exclusion(
            "tests/test_custom_route_class.py",
            "test_openapi_schema",
            "The function compares a complete OpenAPI snapshot and is assigned to the OpenAPI/docs wave.",
            (
                _source(
                    "fastapi/openapi/utils.py",
                    290,
                    400,
                    "FastAPI composes route metadata into OpenAPI operations",
                ),
            ),
        ),
    },
    "tests/test_dependency_cache.py": {
        "test_security_cache": _function_exclusion(
            "tests/test_dependency_cache.py",
            "test_security_cache",
            "This function tests scope-sensitive Security cache keys and belongs to the security wave.",
            (
                _source(
                    "fastapi/dependencies/utils.py",
                    656,
                    680,
                    "FastAPI caches dependencies under keys that include security scopes",
                ),
            ),
        )
    },
    "tests/test_stringified_annotation_dependency.py": {
        "test_openapi_schema": _function_exclusion(
            "tests/test_stringified_annotation_dependency.py",
            "test_openapi_schema",
            "The function compares a complete generated OpenAPI snapshot and is assigned to the OpenAPI/docs wave.",
        )
    },
    "tests/test_generic_parameterless_depends.py": {
        "test_openapi_schema": _function_exclusion(
            "tests/test_generic_parameterless_depends.py",
            "test_openapi_schema",
            "The function compares an OpenAPI document rather than dependency resolution at the HTTP boundary.",
        )
    },
    "tests/test_dependency_overrides.py": {
        name: _function_exclusion(
            "tests/test_dependency_overrides.py",
            name,
            "This function's asserted behavior depends on query-parameter extraction, validation, or nested parameter overrides; those are assigned to the request-parameter wave. Only test_override_simple is linked to the existing dependency override case.",
            (_DEPENDENCY_SOLVER,),
        )
        for name in (
            "test_main_depends",
            "test_main_depends_q_foo",
            "test_main_depends_q_foo_skip_100_limit_200",
            "test_decorator_depends",
            "test_decorator_depends_q_foo",
            "test_decorator_depends_q_foo_skip_100_limit_200",
            "test_router_depends",
            "test_router_depends_q_foo",
            "test_router_depends_q_foo_skip_100_limit_200",
            "test_router_decorator_depends",
            "test_router_decorator_depends_q_foo",
            "test_router_decorator_depends_q_foo_skip_100_limit_200",
            "test_override_with_sub_main_depends",
            "test_override_with_sub__main_depends_q_foo",
            "test_override_with_sub_main_depends_k_bar",
            "test_override_with_sub_decorator_depends",
            "test_override_with_sub_decorator_depends_q_foo",
            "test_override_with_sub_decorator_depends_k_bar",
            "test_override_with_sub_router_depends",
            "test_override_with_sub_router_depends_q_foo",
            "test_override_with_sub_router_depends_k_bar",
            "test_override_with_sub_router_decorator_depends",
            "test_override_with_sub_router_decorator_depends_q_foo",
            "test_override_with_sub_router_decorator_depends_k_bar",
        )
    },
    "tests/test_dependency_contextmanager.py": {
        name: _function_exclusion(
            "tests/test_dependency_contextmanager.py",
            name,
            reason,
            (_DEPENDENCY_SOLVER,),
        )
        for name, reason in {
            "test_background_tasks": "The source asserts background-task execution after nested yield cleanup; generic background response ordering belongs to Starlette-RS.",
            "test_sync_background_tasks": "The source asserts background-task execution after nested yield cleanup; generic background response ordering belongs to Starlette-RS.",
            "test_async_raise_server_error": "The source asserts ServerErrorMiddleware/TestClient behavior after dependency cleanup; this is assigned to the Starlette 1.6.0 exception contract.",
            "test_sync_raise_server_error": "The source asserts ServerErrorMiddleware/TestClient behavior after dependency cleanup; this is assigned to the Starlette 1.6.0 exception contract.",
            "test_async_raise_raises": "The assertion is specifically TestClient re-raising a server exception after ASGI dispatch; TestClient behavior is Starlette-RS-owned.",
            "test_sync_raise_raises": "The assertion is specifically TestClient re-raising a server exception after ASGI dispatch; TestClient behavior is Starlette-RS-owned.",
            "test_async_raise_other": "This is an additional exception-class variant of the yield-cleanup matrix; the selected independent case does not reproduce its class/message.",
            "test_sync_raise_other": "This is an additional exception-class variant of the yield-cleanup matrix; the selected independent case does not reproduce its class/message.",
            "test_context_b_raise": "The function asserts propagation of an application exception through nested context managers, which is not selected by the linked successful nesting case.",
            "test_sync_async_state": "The function adds a sync endpoint with async cleanup to the sync/async matrix; no distinct case is linked in this bounded wave.",
            "test_sync_sync_state": "The function adds a sync endpoint with sync cleanup to the sync/async matrix; no distinct case is linked in this bounded wave.",
            "test_sync_async_raise_other": "The function adds a sync endpoint/async cleanup error combination; no distinct case is linked in this bounded wave.",
            "test_sync_sync_raise_other": "The function adds a sync endpoint/sync cleanup error combination; no distinct case is linked in this bounded wave.",
            "test_sync_async_raise_raises": "The assertion is specifically TestClient re-raising a server exception after ASGI dispatch; TestClient behavior is Starlette-RS-owned.",
            "test_sync_sync_raise_raises": "The assertion is specifically TestClient re-raising a server exception after ASGI dispatch; TestClient behavior is Starlette-RS-owned.",
            "test_sync_async_raise_server_error": "The source asserts ServerErrorMiddleware/TestClient behavior after dependency cleanup; this is assigned to the Starlette 1.6.0 exception contract.",
            "test_sync_sync_raise_server_error": "The source asserts ServerErrorMiddleware/TestClient behavior after dependency cleanup; this is assigned to the Starlette 1.6.0 exception contract.",
            "test_sync_context_b": "The independent nested case uses async context managers; this sync nested variant is not separately represented.",
            "test_sync_context_b_raise": "The function combines sync nested cleanup with an application exception; no equivalent case is linked in this bounded wave.",
        }.items()
    },
    "tests/test_dependency_yield_scope.py": {
        name: _function_exclusion(
            "tests/test_dependency_yield_scope.py",
            name,
            "This function covers an additional dependency scope nesting, invalid-scope error, or compatibility spelling not selected by the current cleanup case.",
            (_DEPENDENCY_SOLVER,),
        )
        for name in (
            "test_two_scopes",
            "test_sub",
            "test_broken_scope",
            "test_named_function_scope",
            "test_regular_function_scope",
            "test_router_level_dep_scope_function",
            "test_router_level_dep_scope_request",
            "test_app_level_dep_scope_function",
            "test_app_level_dep_scope_request",
        )
    },
    "tests/test_dependency_yield_scope_websockets.py": {
        name: _function_exclusion(
            "tests/test_dependency_yield_scope_websockets.py",
            name,
            "This function covers combined/nested/invalid or compatibility scope variants not represented by the two selected WebSocket lifecycle cases.",
            (_WEBSOCKET_ROUTE, _DEPENDENCY_SOLVER),
        )
        for name in (
            "test_two_scopes",
            "test_sub",
            "test_broken_scope",
            "test_named_function_scope",
            "test_regular_function_scope",
        )
    },
    "tests/test_ws_router.py": {
        "test_router_with_params": _function_exclusion(
            "tests/test_ws_router.py",
            "test_router_with_params",
            "The assertions are path/query parameter extraction and are assigned to the request-parameter wave.",
            (_WEBSOCKET_ROUTE,),
        ),
        "test_wrong_uri": _function_exclusion(
            "tests/test_ws_router.py",
            "test_wrong_uri",
            "This asserts generic unmatched WebSocket routing and close code behavior provided by Starlette 1.6.0.",
            (
                _source(
                    "starlette/routing.py",
                    616,
                    629,
                    "Starlette Router.not_found emits the unmatched-WebSocket close",
                ),
            ),
        ),
        "test_depend_validation": _function_exclusion(
            "tests/test_ws_router.py",
            "test_depend_validation",
            "The behavior is missing Header dependency validation and its WebSocket close mapping; request-parameter validation is assigned to another wave.",
            (_WEBSOCKET_RESOLUTION, _HTTP_EXCEPTION),
        ),
        "test_depend_err_middleware": _function_exclusion(
            "tests/test_ws_router.py",
            "test_depend_err_middleware",
            "This asserts a user ASGI WebSocket middleware's exception interception and close behavior, which belongs to the Starlette middleware contract.",
            (
                _source(
                    "starlette/websockets.py",
                    180,
                    181,
                    "Starlette WebSocket.close emits the generic websocket.close ASGI message",
                ),
            ),
        ),
    },
    "tests/test_exception_handlers.py": {
        "test_override_server_error_exception_raises": _function_exclusion(
            "tests/test_exception_handlers.py",
            "test_override_server_error_exception_raises",
            "The assertion is Starlette TestClient's default re-raise policy for an unhandled server error.",
            (
                _source(
                    "starlette/testclient.py",
                    348,
                    357,
                    "Starlette TestClient re-raises application exceptions by default",
                ),
            ),
        ),
        "test_override_server_error_exception_response": _function_exclusion(
            "tests/test_exception_handlers.py",
            "test_override_server_error_exception_response",
            "This asserts the generic ServerErrorMiddleware Exception handler response and TestClient suppression; both are covered by the separate Starlette 1.6.0 contract.",
            (
                _source(
                    "starlette/middleware/errors.py",
                    149,
                    182,
                    "Starlette ServerErrorMiddleware invokes the configured generic server-error handler and emits its response",
                ),
            ),
        ),
        "test_traceback_for_dependency_with_yield": _function_exclusion(
            "tests/test_exception_handlers.py",
            "test_traceback_for_dependency_with_yield",
            "The test asserts a Python traceback frame path and source line through Starlette TestClient; this is runtime/test-client behavior, not a FastAPI HTTP observation.",
            (
                _source(
                    "starlette/testclient.py",
                    348,
                    357,
                    "Starlette TestClient propagates the original application exception",
                ),
            ),
        ),
    },
    "tests/test_starlette_exception.py": {
        "test_get_item": _function_exclusion(
            "tests/test_starlette_exception.py",
            "test_get_item",
            "The function asserts a successful response body and has no exception-handler behavior; response serialization is assigned to another wave.",
        ),
        "test_get_starlette_item": _function_exclusion(
            "tests/test_starlette_exception.py",
            "test_get_starlette_item",
            "The function asserts a successful response body and has no exception-handler behavior; response serialization is assigned to another wave.",
        ),
        "test_openapi_schema": _function_exclusion(
            "tests/test_starlette_exception.py",
            "test_openapi_schema",
            "The function compares a full OpenAPI snapshot and is assigned to the OpenAPI/docs wave.",
        ),
    },
    "tests/test_router_include_context.py": {
        name: _function_exclusion(
            "tests/test_router_include_context.py",
            name,
            reason,
            (_ROUTER_INCLUDE,),
        )
        for name, reason in {
            "test_iter_route_contexts_returns_direct_route_context": "Directly calls the internal route-context iterator rather than the FastAPI public app interface.",
            "test_iter_route_contexts_supports_nested_conflict_detection": "Directly calls the internal route-context iterator and inspects its conflict result.",
            "test_get_openapi_accepts_filtered_route_contexts_with_effective_paths": "Exercises OpenAPI generation directly; assigned to the OpenAPI/docs wave.",
            "test_get_openapi_accepts_webhook_route_contexts": "Exercises OpenAPI/webhook projection directly; assigned to the OpenAPI/docs wave.",
            "test_live_route_addition_uses_include_metadata_for_runtime_and_openapi": "Assigned to the separate source-reviewed public ASGI/OpenAPI live-route-after-include workflow.",
            "test_openapi_cache_updates_after_live_route_addition": "Asserts OpenAPI cache invalidation and document output; assigned to the OpenAPI/docs wave.",
            "test_nested_router_added_after_parent_inclusion_is_live": "Live nested-router mutation is not represented by an existing input case.",
            "test_repeated_deep_inclusions_handle_all_concrete_paths": "Exercises multiple concrete paths and path matching beyond the linked single-route context cases.",
            "test_url_path_for_uses_effective_context_for_live_included_route": "Asserts URL generation from a live route context; no existing Python-object/URL observation is linked.",
            "test_url_path_for_uses_distinct_repeated_inclusion_contexts": "Asserts URL generation and route object context identity; no existing workflow selector represents it.",
            "test_indirect_router_inclusion_cycles_are_rejected": "Distinct indirect-cycle construction error has no existing case in this wave.",
            "test_original_api_route_subclass_instance_is_called_after_inclusion": "Directly inspects/calls a custom route instance and its method identity.",
            "test_original_api_route_get_route_handler_is_called_after_inclusion": "Directly inspects/calls get_route_handler on a Python route object.",
            "test_original_api_route_matches_is_called_after_inclusion": "Directly calls APIRoute.matches and inspects method calls rather than public ASGI output.",
            "test_original_api_router_matches_is_called_after_inclusion": "Directly calls APIRouter.matches and inspects Python call identity.",
            "test_original_nested_api_router_subclasses_are_called_after_inclusion": "Directly inspects custom APIRouter subclass call identity.",
            "test_router_and_include_prefix_path_params_reach_endpoint_and_openapi": "Combines path-parameter injection and OpenAPI assertions; assigned to request-parameter/OpenAPI waves.",
            "test_effective_body_fields_from_app_router_include_and_route_match_openapi": "Combines request-body field composition with OpenAPI; assigned to request-validation/OpenAPI waves.",
            "test_later_full_match_wins_over_earlier_included_partial_match": "Generic partial/full route matching is Starlette 1.6.0 routing behavior.",
            "test_included_partial_match_returns_405_when_no_later_full_match_exists": "Generic method partial-match/405 behavior is Starlette 1.6.0 routing behavior.",
            "test_included_slash_redirect_does_not_block_later_exact_match": "Generic slash-redirect route matching is Starlette 1.6.0 routing behavior.",
            "test_failed_included_match_does_not_leak_effective_context_to_later_route": "Combines generic route matching with internal context state; not represented by the selected public workflow.",
            "test_included_starlette_mount_keeps_prefix_runtime_and_url_path_for": "Generic Starlette Mount and URLPath behavior belongs to Starlette-RS.",
            "test_included_starlette_host_keeps_prefix_runtime_and_url_path_for": "Generic Starlette Host and URLPath behavior belongs to Starlette-RS.",
            "test_included_api_route_without_app_scope_returns_405_response": "Directly invokes a route app without the public FastAPI application scope.",
            "test_effective_api_route_context_does_not_match_websocket_scope": "Directly tests internal route-context matching across ASGI scope types.",
            "test_effective_api_route_context_url_path_for_no_match": "Tests internal URL generation failure, not the public ASGI contract.",
            "test_included_starlette_host_without_prefix_keeps_original_app": "Generic Starlette Host scope behavior belongs to Starlette-RS.",
            "test_included_unknown_route_is_ignored_and_can_return_default_404": "Generic route filtering plus default 404 behavior belongs to Starlette-RS.",
            "test_included_router_candidate_cache_is_thread_safe": "Internal concurrent router-candidate cache invariant, not an independently observable public workflow.",
            "test_included_router_low_priority_cache_rechecks_version_after_lock": "Internal cache locking/version invariant, not an independently observable public workflow.",
            "test_no_prefix_include_validation_sees_effective_starlette_route_candidates": "Directly inspects private inclusion validation against Starlette route candidates.",
            "test_no_prefix_include_validation_sees_effective_api_route_path": "Directly inspects private inclusion validation rather than ASGI output.",
            "test_no_prefix_include_validation_sees_effective_starlette_route_path": "Directly inspects private inclusion validation with Starlette routes.",
            "test_no_prefix_include_validation_rejects_empty_effective_api_route_path": "The focused empty-path public construction behavior is represented by test_empty_router.test_include_empty; this direct internal context variant is not a separate public case.",
            "test_apirouter_matches_fallback_without_include_context": "Directly invokes APIRouter.matches without the public app dispatch path.",
            "test_apirouter_handle_fallback_without_include_context": "Directly invokes APIRouter.handle without the public app dispatch path.",
            "test_restore_fastapi_scope_key_ignores_non_dict_fastapi_scope": "Calls private fastapi.routing._restore_fastapi_scope_key directly; no public route observation is made.",
        }.items()
    },
}


def _module_exclusion(test_path: str, reason: str) -> dict[str, object]:
    return {
        "reason": reason,
        "supporting_sources": _all_test_function_spans(test_path),
    }


APP_DEPENDENCY_TEST_MODULE_EXCLUSIONS: dict[str, dict[str, object]] = {
    "tests/test_additional_responses_router.py": _module_exclusion(
        "tests/test_additional_responses_router.py",
        "The module exercises response model and additional response metadata inherited through routers; response serialization and OpenAPI projection are assigned to their dedicated waves.",
    ),
    "tests/test_extra_routes.py": _module_exclusion(
        "tests/test_extra_routes.py",
        "These typed body and response assertions are already reviewed by the core wave; their remaining request parsing and response behavior belongs to the request-parameter and response waves.",
    ),
    "tests/test_http_connection_injection.py": _module_exclusion(
        "tests/test_http_connection_injection.py",
        "HTTPConnection injection over HTTP and WebSocket is already mapped by the core review wave to dedicated workflow cases; this app/dependency wave does not duplicate those links.",
    ),
    "tests/test_param_in_path_and_dependency.py": _module_exclusion(
        "tests/test_param_in_path_and_dependency.py",
        "The module couples path parameter extraction and validation to dependency resolution; request-parameter and validation behavior are assigned to their dedicated waves.",
    ),
    "tests/test_path.py": _module_exclusion(
        "tests/test_path.py",
        "The module focuses on path parameter declaration, extraction, and validation, which are assigned to the request-parameter wave.",
    ),
    "tests/test_dependencies_utils.py": _module_exclusion(
        "tests/test_dependencies_utils.py",
        "This module directly tests get_typed_annotation from FastAPI's dependency utility internals and does not exercise a public application or ASGI interface.",
    ),
    "tests/test_dependency_models.py": _module_exclusion(
        "tests/test_dependency_models.py",
        "This module inspects Dependant internals and private callable-classification/cache helpers; public dependency behavior is represented by separate route workflows.",
    ),
    "tests/test_dependency_duplicates.py": _module_exclusion(
        "tests/test_dependency_duplicates.py",
        "The functions combine request-body field composition, validation detail, duplicate parameter extraction, or OpenAPI snapshots; these are assigned to request-validation/OpenAPI waves.",
    ),
    "tests/test_dependency_paramless.py": _module_exclusion(
        "tests/test_dependency_paramless.py",
        "The module exercises SecurityScopes and OAuth scope composition, assigned to the security wave; its direct helper call is already source-excluded from public parity.",
    ),
    "tests/test_dependency_security_overrides.py": _module_exclusion(
        "tests/test_dependency_security_overrides.py",
        "The module's route overrides are security-object and credential behaviors, assigned to the security wave.",
    ),
    "tests/test_dependency_after_yield_streaming.py": _module_exclusion(
        "tests/test_dependency_after_yield_streaming.py",
        "The module couples yield-dependency cleanup to StreamingResponse consumption and client stream behavior; response/streaming and Starlette ASGI lifecycle are owned by other waves.",
    ),
    "tests/test_repeated_dependency_schema.py": _module_exclusion(
        "tests/test_repeated_dependency_schema.py",
        "The module asserts dependency-derived OpenAPI parameter reuse and request parameter behavior, assigned to OpenAPI/request-validation waves.",
    ),
    "tests/test_response_dependency.py": _module_exclusion(
        "tests/test_response_dependency.py",
        "The module covers injected Response state, returned response precedence, background tasks, and request parsing; response/Starlette behavior is assigned to other waves.",
    ),
    "tests/test_default_response_class_router.py": _module_exclusion(
        "tests/test_default_response_class_router.py",
        "The module's router-tree matrix is specifically about response-class inheritance/override and response headers, assigned to the response wave.",
    ),
    "tests/test_include_router_defaults_overrides.py": _module_exclusion(
        "tests/test_include_router_defaults_overrides.py",
        "The mapped functions assert response-class defaults, response headers, and a large OpenAPI snapshot; response and OpenAPI behavior are assigned to other waves.",
    ),
    "tests/test_route_scope.py": _module_exclusion(
        "tests/test_route_scope.py",
        "The HTTP functions rely on path parameter extraction and generic Starlette Route.matches scope construction; the WebSocket function relies on Starlette WebSocketRoute.matches and path parameters. These belong to request-parameter and Starlette-RS contracts.",
    ),
    "tests/test_router_prefix_with_template.py": _module_exclusion(
        "tests/test_router_prefix_with_template.py",
        "The module checks Starlette path-converter and path-parameter behavior under a router prefix; those behaviors are assigned to the request-parameter/Starlette-RS routing contracts.",
    ),
    "tests/test_router_redirect_slashes.py": _module_exclusion(
        "tests/test_router_redirect_slashes.py",
        "The module asserts generic slash redirects from the Starlette Router; FastAPI adds no distinct behavior in these assertions, so the pinned Starlette 1.6.0 contract is authoritative.",
    ),
    "tests/test_strict_content_type_router_level.py": _module_exclusion(
        "tests/test_strict_content_type_router_level.py",
        "The module checks request Content-Type parsing/validation and router-level inheritance, assigned to the request-validation wave.",
    ),
    "tests/test_security_scopes_sub_dependency.py": _module_exclusion(
        "tests/test_security_scopes_sub_dependency.py",
        "The module checks scope-sensitive security dependency caching and OpenAPI security projection, assigned to the security wave.",
    ),
    "tests/test_stringified_annotation_dependency_py314.py": _module_exclusion(
        "tests/test_stringified_annotation_dependency_py314.py",
        "The module is gated by needs_py314 and exercises native Python 3.14 forward-reference evaluation; the pinned oracle profile is CPython 3.12.13, while the adjacent supported-version stringified-annotation case is mapped separately.",
    ),
    "tests/test_custom_middleware_exception.py": _module_exclusion(
        "tests/test_custom_middleware_exception.py",
        "The custom receive-wrapper upload-limit behavior is already mapped by the core review wave; multipart parsing and generic ExceptionMiddleware are Starlette-RS responsibilities, so it is not duplicated here.",
    ),
}


APP_DEPENDENCY_WAVE_GAPS = {
    "full_fastapi_manifest": "Every linked case remains a source candidate until the full FastAPI public API manifest is complete and identity-checked.",
    "python_object_observations": "The current ASGI workflow does not express Python object identity/isinstance observations such as APIRoute subclass identity.",
    "dependency_matrix": "The current links do not exhaust all dependency cache keys, sync/async generator forms, nested scopes, app/router overrides, or exception matrices.",
    "lifespan_warning_capture": "The current workflow does not capture exact DeprecationWarning category/message or TestClient.app_state assertions from test_router_events.py.",
    "websocket_request_validation": "WebSocket Header/path/query dependency failures remain with request-validation/security waves; generic handshakes, middleware, and unmatched-route close behavior remain Starlette-RS-owned.",
    "starlette_contract_identity": "Starlette behavior is assigned to the pinned 1.6.0 / 4f250d6b814587e20c5365f0a5f0c4d42bcb929f contract; no sibling Starlette-RS files are modified by this mapping wave.",
}
