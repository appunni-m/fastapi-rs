"""Source-reviewed inputs for FastAPI testing, WebSocket, and mount tutorials.

This sidecar contains reviewed source mappings only. Its linked YAML recipes are
input-only; parity workers and upstream tests are never run by this module.
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
        "role": "pinned source oracle only; the target runtime is FastAPI-RS",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI, TestClient, WebSocket, and mount contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "pydantic_core_version": "2.46.4",
        "role": "FastAPI's field validation and parameter conversion backend",
    },
    "python": {
        "implementation": "CPython",
        "version": "3.12.13",
        "role": "pinned source-oracle interpreter profile",
    },
    "starlette_rs": {
        "version": "0.1.0",
        "commit": "8d63ce729a789ae2d6c9fab9d37ae4b1e7b2ac89",
        "contract_id": "starlette-1.6.0-asgi-http-config-session-slice",
        "role": "generic Starlette contract implementation",
    },
}

# The task named this path, but it does not exist at the pinned FastAPI commit.
# The tutorial module below is the extant WebSocket TestClient source reviewed.
SOURCE_REVIEW_SCOPE_NOTE = (
    "tests/test_websockets.py is absent from the pinned FastAPI 0.141.1 source tree "
    "at 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f; it has no top-level functions "
    "to map and is intentionally omitted from module mappings and exclusion counts. "
    "The extant WebSocket tutorial TestClient module in this review is "
    "tests/test_tutorial/test_websockets/test_tutorial002.py."
)

HTTP = ["http.body.bytes", "http.status"]
OPENAPI = ["http.status", "openapi.document", "openapi.paths"]
WEBSOCKET = ["websocket.close_code", "websocket.event_order", "websocket.messages"]

TESTING_HTTP_RECIPE = "tests/fixtures/input-recipes/parity/atlas-testing-websocket-app-testing.yaml"
TESTING_WS_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-app-testing-ws.yaml"
)
DEPENDENCY_OVERRIDE_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-dependency-overrides.yaml"
)
DEPENDENCY_DEFAULT_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-dependency-defaults.yaml"
)
WEBSOCKET_TUTORIAL_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-websockets-tutorial002.yaml"
)
SUB_APPLICATION_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-sub-applications.yaml"
)
FIRST_STEPS_ASYNC_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-first-steps-async.yaml"
)
FIRST_STEPS_SYNC_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-testing-websocket-first-steps-sync.yaml"
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _function_source(test_path: str, function_name: str) -> dict[str, Any]:
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
    return _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 top-level function {function_name}",
    )


def _documented_function(path: str, function_name: str, role: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one documented {function_name} in {path}")
    node = matches[0]
    return _source(path, node.lineno, node.end_lineno or node.lineno, role)


def _link(
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


def _review(
    test_path: str,
    function_name: str,
    feature_ids: list[str],
    rationale: str,
    contract_gate: str,
    links: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    selectors = sorted({selector for link in links for selector in link["observation_selectors"]})
    notes = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} actions "
        f"{', '.join(link['action_ids'])} observe "
        f"{', '.join(link['observation_selectors'])}"
        for link in links
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + contract_gate,
        "workflow_cases": links,
        "stimulus_notes": (
            "Input-only case links: " + notes + ". YAML inputs contain no expected outputs."
        ),
        "supporting_sources": [_function_source(test_path, function_name), *sources],
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    workflows: dict[tuple[str, str], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for review in functions.values():
        for link in review["workflow_cases"]:
            key = (link["recipe_path"], link["case_id"])
            entry = workflows.setdefault(
                key,
                {
                    "recipe_path": link["recipe_path"],
                    "case_ids": [link["case_id"]],
                    "observation_selectors": set(),
                },
            )
            entry["observation_selectors"].update(link["observation_selectors"])
        for source in review["supporting_sources"]:
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources.setdefault(key, source)
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
        "module_observation_selectors": sorted(
            {
                selector
                for review in functions.values()
                for selector in review["observation_selectors"]
            }
        ),
        "supporting_sources": list(sources.values()),
        "workflow_cases": [
            {**link, "observation_selectors": sorted(link["observation_selectors"])}
            for link in workflows.values()
        ],
        "functions": functions,
        "stimulus_notes": (
            "Every top-level function in this extant upstream module has a source span "
            "and at least one input-only recipe action link. The ASGI recipes model the "
            "application protocol; TestClient wrapper methods remain Starlette-RS-owned "
            "and are not exercised as Python TestClient calls here."
        ),
    }


_FASTAPI_HTTP_ROUTES = _source(
    "fastapi/applications.py",
    1646,
    1815,
    "FastAPI registers HTTP path operations and their response metadata",
)
_FASTAPI_DEPENDENCIES = _source(
    "fastapi/dependencies/utils.py",
    619,
    698,
    "FastAPI resolves dependencies and query/path/header/cookie parameters; ModelField validation uses the pinned Pydantic layer",
)
_FASTAPI_HTTP_EXECUTION = _source(
    "fastapi/routing.py",
    475,
    489,
    "FastAPI solves endpoint dependencies before invoking the endpoint",
)
_FASTAPI_RESPONSE = _source(
    "fastapi/routing.py",
    706,
    759,
    "FastAPI turns returned values into configured responses and raises request validation errors",
)
_FASTAPI_OPENAPI = _source(
    "fastapi/applications.py",
    1070,
    1120,
    "FastAPI generates the OpenAPI document and serves it at the configured path",
)
_FASTAPI_WS_ROUTE = _source(
    "fastapi/applications.py",
    1361,
    1438,
    "FastAPI's websocket decorator registers an APIWebSocketRoute",
)
_FASTAPI_WS_RESOLUTION = _source(
    "fastapi/routing.py",
    764,
    837,
    "FastAPI resolves WebSocket dependencies and raises WebSocketRequestValidationError for invalid parameters",
)
_FASTAPI_WS_VALIDATION_CLOSE = _source(
    "fastapi/exception_handlers.py",
    29,
    34,
    "FastAPI maps WebSocket request validation failures to the policy-violation close code",
)
_FASTAPI_PYDANTIC_ADAPTER = _source(
    "fastapi/_compat/v2.py",
    114,
    178,
    "FastAPI creates a Pydantic TypeAdapter for field validation and input conversion",
)
_FASTAPI_TESTCLIENT_REEXPORT = _source(
    "fastapi/testclient.py",
    1,
    1,
    "FastAPI directly re-exports Starlette's TestClient",
)
_FASTAPI_WEBSOCKET_REEXPORT = _source(
    "fastapi/websockets.py",
    1,
    3,
    "FastAPI directly re-exports Starlette WebSocket types",
)
_STARLETTE_TESTCLIENT_HTTP = _source(
    "starlette/testclient.py",
    211,
    290,
    "Starlette 1.6.0 TestClient builds HTTP and WebSocket ASGI scopes",
)
_STARLETTE_TESTCLIENT_SESSION = _source(
    "starlette/testclient.py",
    102,
    178,
    "Starlette 1.6.0 WebSocketTestSession enters, sends, and receives protocol events",
)
_STARLETTE_TESTCLIENT_WS_CONNECT = _source(
    "starlette/testclient.py",
    656,
    677,
    "Starlette 1.6.0 TestClient.websocket_connect handles the WebSocket upgrade boundary",
)
_STARLETTE_MOUNT = _source(
    "starlette/routing.py",
    363,
    425,
    "Starlette 1.6.0 Mount matches HTTP/WebSocket paths and extends child root_path",
)
_STARLETTE_ROUTER = _source(
    "starlette/routing.py",
    616,
    720,
    "Starlette 1.6.0 Router selects matching routes and its unmatched-path handler returns 404",
)
_STARLETTE_WS = _source(
    "starlette/websockets.py",
    165,
    182,
    "Starlette 1.6.0 WebSocket sends text and JSON messages and closes sessions",
)


def _doc(path: str, name: str, role: str) -> dict[str, Any]:
    return _documented_function(path, name, role)


_TESTING_A_MAIN = _doc(
    "docs_src/app_testing/app_a_py310/main.py",
    "read_main",
    "documented FastAPI route returning the app-testing message",
)
_TESTING_TUTORIAL001_MAIN = _doc(
    "docs_src/app_testing/tutorial001_py310.py",
    "read_main",
    "documented FastAPI route returning the app-testing message",
)
_TESTING_TUTORIAL002_MAIN = _doc(
    "docs_src/app_testing/tutorial002_py310.py",
    "read_main",
    "documented HTTP route from the HTTP and WebSocket testing tutorial",
)
_TESTING_TUTORIAL002_WS = _doc(
    "docs_src/app_testing/tutorial002_py310.py",
    "websocket",
    "documented WebSocket endpoint sends one JSON message then closes",
)
_TESTING_A_TEST = _doc(
    "docs_src/app_testing/app_a_py310/test_main.py",
    "test_read_main",
    "documented TestClient request and response assertions for app A",
)
_TESTING_TUTORIAL001_TEST = _doc(
    "docs_src/app_testing/tutorial001_py310.py",
    "test_read_main",
    "documented TestClient request and response assertions for tutorial001",
)
_TESTING_TUTORIAL002_HTTP_TEST = _doc(
    "docs_src/app_testing/tutorial002_py310.py",
    "test_read_main",
    "documented HTTP TestClient assertion in the HTTP and WebSocket tutorial",
)
_TESTING_TUTORIAL002_WS_TEST = _doc(
    "docs_src/app_testing/tutorial002_py310.py",
    "test_websocket",
    "documented TestClient WebSocket session and JSON receive assertion",
)
_DEP_PLAIN = [
    _doc(
        "docs_src/dependency_testing/tutorial001_py310.py",
        "common_parameters",
        "documented query dependency and defaults",
    ),
    _doc(
        "docs_src/dependency_testing/tutorial001_py310.py",
        "override_dependency",
        "documented testing dependency override",
    ),
    _doc(
        "docs_src/dependency_testing/tutorial001_py310.py",
        "read_items",
        "documented items route using Depends",
    ),
    _doc(
        "docs_src/dependency_testing/tutorial001_py310.py",
        "read_users",
        "documented users route using Depends",
    ),
]
_DEP_ANNOTATED = [
    _doc(
        "docs_src/dependency_testing/tutorial001_an_py310.py",
        "common_parameters",
        "documented query dependency and defaults",
    ),
    _doc(
        "docs_src/dependency_testing/tutorial001_an_py310.py",
        "override_dependency",
        "documented testing dependency override",
    ),
    _doc(
        "docs_src/dependency_testing/tutorial001_an_py310.py",
        "read_items",
        "documented items route using Annotated Depends",
    ),
    _doc(
        "docs_src/dependency_testing/tutorial001_an_py310.py",
        "read_users",
        "documented users route using Annotated Depends",
    ),
]
_DEP_ITEMS_TESTS = {
    name: [
        _doc(
            "docs_src/dependency_testing/tutorial001_py310.py",
            name,
            "documented dependency-override TestClient assertion",
        ),
        _doc(
            "docs_src/dependency_testing/tutorial001_an_py310.py",
            name,
            "documented Annotated dependency-override TestClient assertion",
        ),
    ]
    for name in (
        "test_override_in_items",
        "test_override_in_items_with_q",
        "test_override_in_items_with_params",
    )
}
_WS_DOCS = [
    _doc(
        "docs_src/websockets_/tutorial002_py310.py",
        "get_cookie_or_token",
        "documented cookie/query WebSocket dependency and its missing-credential policy",
    ),
    _doc(
        "docs_src/websockets_/tutorial002_py310.py",
        "websocket_endpoint",
        "documented WebSocket endpoint reads messages, formats replies, and validates q as an integer",
    ),
    _doc(
        "docs_src/websockets_/tutorial002_an_py310.py",
        "get_cookie_or_token",
        "documented Annotated cookie/query WebSocket dependency",
    ),
    _doc(
        "docs_src/websockets_/tutorial002_an_py310.py",
        "websocket_endpoint",
        "documented Annotated WebSocket endpoint",
    ),
]
_SUBAPP_DOCS = [
    _doc(
        "docs_src/sub_applications/tutorial001_py310.py",
        "read_main",
        "documented main FastAPI route",
    ),
    _doc(
        "docs_src/sub_applications/tutorial001_py310.py",
        "read_sub",
        "documented mounted FastAPI route",
    ),
    _source(
        "docs_src/sub_applications/tutorial001_py310.py",
        1,
        19,
        "documented parent app mounts a second FastAPI application at /subapi",
    ),
]
_FIRST_ASYNC = _doc(
    "docs_src/first_steps/tutorial001_py310.py", "root", "documented asynchronous first-steps route"
)
_FIRST_SYNC = _doc(
    "docs_src/first_steps/tutorial003_py310.py", "root", "documented synchronous first-steps route"
)


TESTING_WEBSOCKET_TUTORIAL_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_tutorial/test_testing/test_main_a.py": _module(
        "The source delegates its HTTP assertion to the app-testing docs module and asserts the generated OpenAPI snapshot. FastAPI owns route/OpenAPI behavior; Starlette 1.6.0 owns the TestClient transport and JSON response surface, implemented by Starlette-RS.",
        {
            "test_main": _review(
                "tests/test_tutorial/test_testing/test_main_a.py",
                "test_main",
                ["app-routing", "response-serialization"],
                "The documented asynchronous root route returns its JSON message through the ASGI HTTP path.",
                "The recipe records ASGI response status and bytes rather than invoking Starlette TestClient.get or decoding Response.json; the test itself only asserts status and decoded JSON.",
                [_link(TESTING_HTTP_RECIPE, "fastapi.atlas-testing.main-a", ["read-main"], HTTP)],
                [
                    _TESTING_A_MAIN,
                    _TESTING_A_TEST,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_HTTP_EXECUTION,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_testing/test_main_a.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The test compares the full OpenAPI response document for the documented root route.",
                "The input selects the full JSON document and HTTP status; it does not call TestClient or reproduce the snapshot assertion as an expected recipe output.",
                [
                    _link(
                        TESTING_HTTP_RECIPE,
                        "fastapi.atlas-testing.main-a",
                        ["openapi-document"],
                        OPENAPI,
                    )
                ],
                [
                    _TESTING_A_MAIN,
                    _FASTAPI_OPENAPI,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
        },
    ),
    "tests/test_tutorial/test_testing/test_tutorial001.py": _module(
        "This module mirrors the app-testing example: one delegated root request and one complete OpenAPI snapshot. FastAPI owns the registered route and schema; Starlette 1.6.0 owns generic TestClient transport behavior.",
        {
            "test_main": _review(
                "tests/test_tutorial/test_testing/test_tutorial001.py",
                "test_main",
                ["app-routing", "response-serialization"],
                "The documented root route returns its message in an HTTP JSON response.",
                "The input observes ASGI status and bytes; TestClient.get and Response.json are not invoked by the workflow.",
                [
                    _link(
                        TESTING_HTTP_RECIPE,
                        "fastapi.atlas-testing.tutorial001",
                        ["read-main"],
                        HTTP,
                    )
                ],
                [
                    _TESTING_TUTORIAL001_MAIN,
                    _TESTING_TUTORIAL001_TEST,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_HTTP_EXECUTION,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_testing/test_tutorial001.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The test snapshots the full OpenAPI document generated from the tutorial root route.",
                "The ASGI input selects the complete parsed OpenAPI value and status, but the expected snapshot and TestClient.json conversion are intentionally not copied into recipe data.",
                [
                    _link(
                        TESTING_HTTP_RECIPE,
                        "fastapi.atlas-testing.tutorial001",
                        ["openapi-document"],
                        OPENAPI,
                    )
                ],
                [
                    _TESTING_TUTORIAL001_MAIN,
                    _FASTAPI_OPENAPI,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
        },
    ),
    "tests/test_tutorial/test_testing/test_tutorial002.py": _module(
        "The source checks one HTTP route and one WebSocket message from a documented app. FastAPI owns route registration and endpoint dispatch; Starlette 1.6.0 owns the generic ASGI WebSocket and TestClient session contract.",
        {
            "test_main": _review(
                "tests/test_tutorial/test_testing/test_tutorial002.py",
                "test_main",
                ["app-routing", "response-serialization"],
                "The HTTP action reaches the documented root route and observes its response.",
                "The raw ASGI action does not exercise TestClient.get or Response.json, which belong to the Starlette-RS compatibility surface.",
                [
                    _link(
                        TESTING_WS_RECIPE, "fastapi.atlas-testing.tutorial002", ["read-main"], HTTP
                    )
                ],
                [
                    _TESTING_TUTORIAL002_MAIN,
                    _TESTING_TUTORIAL002_HTTP_TEST,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_ws": _review(
                "tests/test_tutorial/test_testing/test_tutorial002.py",
                "test_ws",
                ["websocket-lifecycle"],
                "The WebSocket action sends a connect event, observes the endpoint's JSON text message, and records the server close.",
                "The source uses TestClient.websocket_connect and receive_json; this workflow records ordered ASGI WebSocket messages and close metadata, not TestClient context-manager or JSON-decoding behavior.",
                [
                    _link(
                        TESTING_WS_RECIPE,
                        "fastapi.atlas-testing.tutorial002",
                        ["websocket"],
                        WEBSOCKET,
                    )
                ],
                [
                    _TESTING_TUTORIAL002_WS,
                    _TESTING_TUTORIAL002_WS_TEST,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_WEBSOCKET_REEXPORT,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_TESTCLIENT_WS_CONNECT,
                    _STARLETTE_WS,
                ],
            ),
        },
    ),
    "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py": _module(
        "The fixture selects both plain and Annotated dependency syntax. FastAPI owns override lookup, dependency resolution, parameter conversion and endpoint values; Pydantic 2.13.4 supplies typed query validation. Starlette-RS owns only generic ASGI/TestClient transport and response delivery.",
        {
            "get_test_module": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "get_test_module",
                ["dependency-security", "request-validation"],
                "The fixture chooses the plain or Annotated tutorial app. The linked inputs represent both declaration forms across the overridden and unoverridden workflow apps.",
                "The independent workload uses equivalent local route names for the additional Annotated path variant; it does not execute pytest fixture parametrization or import either upstream docs module.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        [
                            "items-default-plain",
                            "items-default-annotated",
                            "items-query-plain",
                            "items-query-annotated",
                            "items-params-plain",
                            "items-params-annotated",
                            "users-default-plain",
                            "users-default-annotated",
                            "users-query-plain",
                            "users-query-annotated",
                            "users-params-plain",
                            "users-params-annotated",
                        ],
                        HTTP,
                    ),
                    _link(
                        DEPENDENCY_DEFAULT_RECIPE,
                        "fastapi.atlas-testing-dependency.defaults",
                        ["normal-items"],
                        HTTP,
                    ),
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    *_DEP_ITEMS_TESTS["test_override_in_items"],
                    *_DEP_ITEMS_TESTS["test_override_in_items_with_q"],
                    *_DEP_ITEMS_TESTS["test_override_in_items_with_params"],
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_HTTP_EXECUTION,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_override_in_items_run": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_override_in_items_run",
                ["dependency-security", "response-serialization"],
                "The default query and explicitly supplied q/skip/limit inputs exercise the dependency override on /items/ in both declaration forms.",
                "The input covers the three source request shapes and both Depends syntaxes; it observes raw ASGI results rather than TestClient response decoding.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        [
                            "items-default-plain",
                            "items-default-annotated",
                            "items-query-plain",
                            "items-query-annotated",
                            "items-params-plain",
                            "items-params-annotated",
                        ],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    *_DEP_ITEMS_TESTS["test_override_in_items"],
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_HTTP_EXECUTION,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_override_in_items_with_q_run": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_override_in_items_with_q_run",
                ["dependency-security", "request-validation", "response-serialization"],
                "A string query value reaches the override while skip and limit stay at the override's constants.",
                "The action samples q conversion and override output but does not reproduce TestClient or pytest's fixture lifecycle.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        ["items-query-plain", "items-query-annotated"],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    *_DEP_ITEMS_TESTS["test_override_in_items_with_q"],
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_override_in_items_with_params_run": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_override_in_items_with_params_run",
                ["dependency-security", "request-validation", "response-serialization"],
                "The request provides all three query values; the override signature accepts q and supplies fixed skip and limit values.",
                "The workflow models the request and response values, but TestClient's HTTP interface is not part of the ASGI action.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        ["items-params-plain", "items-params-annotated"],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    *_DEP_ITEMS_TESTS["test_override_in_items_with_params"],
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_override_in_users": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_override_in_users",
                ["dependency-security", "response-serialization"],
                "The user route shares the overridden dependency and is observed with default, q-only, and all-query request shapes.",
                "All three assertion inputs are represented in both plain and Annotated route forms; the workflow does not run the upstream assertions.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        [
                            "users-default-plain",
                            "users-default-annotated",
                            "users-query-plain",
                            "users-query-annotated",
                            "users-params-plain",
                            "users-params-annotated",
                        ],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_override_in_users_with_q": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_override_in_users_with_q",
                ["dependency-security", "request-validation", "response-serialization"],
                "The user route receives q=foo through the replacement dependency in both declaration styles.",
                "The case captures status and body bytes; it does not call TestClient.get or Response.json.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        ["users-query-plain", "users-query-annotated"],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_override_in_users_with_params": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_override_in_users_with_params",
                ["dependency-security", "request-validation", "response-serialization"],
                "The user route receives q, skip, and limit while the override returns its fixed pagination values.",
                "The action reproduces the source query shape for both declaration styles but leaves TestClient and pytest fixture behavior to Starlette-RS and the Python test runner.",
                [
                    _link(
                        DEPENDENCY_OVERRIDE_RECIPE,
                        "fastapi.atlas-testing-dependency.overrides",
                        ["users-params-plain", "users-params-annotated"],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    *_DEP_ANNOTATED,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_normal_app": _review(
                "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py",
                "test_normal_app",
                ["dependency-security", "request-validation", "response-serialization"],
                "After the test clears dependency_overrides, the original common dependency receives q, skip, and limit.",
                "The separate no-override workload preserves the source /items/ path and query but creates a fresh app instead of mutating the prior test module's dependency_overrides dictionary.",
                [
                    _link(
                        DEPENDENCY_DEFAULT_RECIPE,
                        "fastapi.atlas-testing-dependency.defaults",
                        ["normal-items"],
                        HTTP,
                    )
                ],
                [
                    *_DEP_PLAIN,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
        },
    ),
    "tests/test_tutorial/test_websockets/test_tutorial002.py": _module(
        "This parametrized source covers plain and Annotated WebSocket dependencies, cookie/query credentials, q conversion, and pre-accept closes. FastAPI owns WebSocket route/dependency validation; Pydantic 2.13.4 validates q. Starlette-RS owns generic WebSocket event/session semantics.",
        {
            "get_app": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "get_app",
                ["websocket-lifecycle", "dependency-security", "request-validation"],
                "The fixture selects both tutorial implementations. The workload carries their corresponding plain and Annotated declarations on separate path prefixes so each can be driven as independent input.",
                "The recipe models ASGI sessions directly; it does not invoke pytest parametrization or Starlette TestClient.websocket_connect.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        [
                            "read-main",
                            "cookie-plain",
                            "cookie-annotated",
                            "query-token-plain",
                            "query-token-annotated",
                            "query-token-q-plain",
                            "query-token-q-annotated",
                            "no-credentials-plain",
                            "no-credentials-annotated",
                            "invalid-query-plain",
                            "invalid-query-annotated",
                        ],
                        sorted(set(HTTP + WEBSOCKET)),
                    )
                ],
                [
                    *_WS_DOCS,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_WS_VALIDATION_CLOSE,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _FASTAPI_WEBSOCKET_REEXPORT,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_TESTCLIENT_WS_CONNECT,
                    _STARLETTE_WS,
                ],
            ),
            "test_main": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "test_main",
                ["app-routing", "response-serialization"],
                "The test requests the documented HTML landing page and checks for its doctype.",
                "The independent workload preserves the required doctype but uses a minimal page; its raw body comparison does not assert the source's substring-only check or invoke TestClient.get.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        ["read-main"],
                        HTTP,
                    )
                ],
                [
                    _WS_DOCS[0],
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
            "test_websocket_with_cookie": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "test_websocket_with_cookie",
                ["websocket-lifecycle", "dependency-security"],
                "The session cookie supplies credentials and each of two client messages elicits token and item-specific text replies.",
                "The workflow records ASGI messages and the close; it does not assert that TestClient raises WebSocketDisconnect from its context-manager exit.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        ["cookie-plain", "cookie-annotated"],
                        WEBSOCKET,
                    )
                ],
                [
                    *_WS_DOCS,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_WEBSOCKET_REEXPORT,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_TESTCLIENT_WS_CONNECT,
                    _STARLETTE_WS,
                ],
            ),
            "test_websocket_with_header": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "test_websocket_with_header",
                ["websocket-lifecycle", "dependency-security"],
                "Despite the test name, the source puts the token in the query string; the input drives two text messages and checks token/item-specific replies.",
                "This ASGI recipe records event/message values and close metadata, not WebSocketTestSession context-manager or receive_text exceptions.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        ["query-token-plain", "query-token-annotated"],
                        WEBSOCKET,
                    )
                ],
                [
                    *_WS_DOCS,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_DEPENDENCIES,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_TESTCLIENT_WS_CONNECT,
                    _STARLETTE_WS,
                ],
            ),
            "test_websocket_with_header_and_query": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "test_websocket_with_header_and_query",
                ["websocket-lifecycle", "dependency-security", "request-validation"],
                "The source supplies a query token and integer q, then checks both dependency output and the item-specific response for two messages.",
                "Pydantic-backed q conversion and FastAPI dependency resolution are observable in ASGI messages; the recipe does not test TestClient cookie/header merging or decoded session calls.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        ["query-token-q-plain", "query-token-q-annotated"],
                        WEBSOCKET,
                    )
                ],
                [
                    *_WS_DOCS,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_WS,
                ],
            ),
            "test_websocket_no_credentials": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "test_websocket_no_credentials",
                ["websocket-lifecycle", "dependency-security"],
                "The missing-credential dependency raises a FastAPI WebSocketException before accepting a client session.",
                "The input records the ASGI close code and event order; it does not assert the TestClient-specific WebSocketDisconnect raised on context entry.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        ["no-credentials-plain", "no-credentials-annotated"],
                        WEBSOCKET,
                    )
                ],
                [
                    *_WS_DOCS,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_WEBSOCKET_REEXPORT,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_WS,
                ],
            ),
            "test_websocket_invalid_data": _review(
                "tests/test_tutorial/test_websockets/test_tutorial002.py",
                "test_websocket_invalid_data",
                ["websocket-lifecycle", "request-validation"],
                "A non-integer q value fails FastAPI WebSocket dependency validation before endpoint execution and produces a policy-violation close.",
                "The source asserts the TestClient context raises WebSocketDisconnect; the workflow observes the close code and does not compare validation details or TestClient exceptions.",
                [
                    _link(
                        WEBSOCKET_TUTORIAL_RECIPE,
                        "fastapi.atlas-testing.websocket-tutorial002",
                        ["invalid-query-plain", "invalid-query-annotated"],
                        WEBSOCKET,
                    )
                ],
                [
                    *_WS_DOCS,
                    _FASTAPI_WS_ROUTE,
                    _FASTAPI_WS_RESOLUTION,
                    _FASTAPI_WS_VALIDATION_CLOSE,
                    _FASTAPI_DEPENDENCIES,
                    _FASTAPI_PYDANTIC_ADAPTER,
                    _STARLETTE_TESTCLIENT_SESSION,
                    _STARLETTE_WS,
                ],
            ),
        },
    ),
    "tests/test_tutorial/test_sub_applications/test_tutorial001.py": _module(
        "The source distinguishes parent and mounted FastAPI routes and snapshots both OpenAPI documents. FastAPI owns each app's routes and schemas; Starlette 1.6.0 Mount owns prefix matching and child root_path construction, which is the Starlette-RS contract.",
        {
            "test_main": _review(
                "tests/test_tutorial/test_sub_applications/test_tutorial001.py",
                "test_main",
                ["app-routing", "response-serialization"],
                "The parent app serves its own /app operation independently of the mounted child.",
                "The ASGI path exercises mounted application composition but does not call the source TestClient.get or Response.json APIs.",
                [
                    _link(
                        SUB_APPLICATION_RECIPE,
                        "fastapi.atlas-testing.sub-applications",
                        ["main-http"],
                        HTTP,
                    )
                ],
                [
                    *_SUBAPP_DOCS,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                    _STARLETTE_MOUNT,
                ],
            ),
            "test_sub": _review(
                "tests/test_tutorial/test_sub_applications/test_tutorial001.py",
                "test_sub",
                ["app-routing", "response-serialization"],
                "A request under /subapi reaches the child FastAPI route after Starlette mount-prefix matching.",
                "The recipe observes raw ASGI output, not TestClient response decoding or the child route's Python app boundary directly.",
                [
                    _link(
                        SUB_APPLICATION_RECIPE,
                        "fastapi.atlas-testing.sub-applications",
                        ["sub-http"],
                        HTTP,
                    )
                ],
                [
                    *_SUBAPP_DOCS,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                    _STARLETTE_MOUNT,
                ],
            ),
            "test_openapi_schema_main": _review(
                "tests/test_tutorial/test_sub_applications/test_tutorial001.py",
                "test_openapi_schema_main",
                ["openapi-docs"],
                "The parent app's OpenAPI document describes /app and is observed separately from its mounted child.",
                "The case selects the full OpenAPI JSON value; it does not embed the source snapshot as a fixture expectation or invoke TestClient.json.",
                [
                    _link(
                        SUB_APPLICATION_RECIPE,
                        "fastapi.atlas-testing.sub-applications",
                        ["main-openapi"],
                        OPENAPI,
                    )
                ],
                [
                    *_SUBAPP_DOCS,
                    _FASTAPI_OPENAPI,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                    _STARLETTE_MOUNT,
                ],
            ),
            "test_openapi_schema_sub": _review(
                "tests/test_tutorial/test_sub_applications/test_tutorial001.py",
                "test_openapi_schema_sub",
                ["openapi-docs", "app-routing"],
                "The mounted child exposes a distinct OpenAPI document whose server prefix reflects /subapi.",
                "The recipe selects the whole child document at the mounted path; Starlette Mount prefix/root_path and FastAPI OpenAPI server construction are both needed for this observation.",
                [
                    _link(
                        SUB_APPLICATION_RECIPE,
                        "fastapi.atlas-testing.sub-applications",
                        ["sub-openapi"],
                        OPENAPI,
                    )
                ],
                [
                    *_SUBAPP_DOCS,
                    _FASTAPI_OPENAPI,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                    _STARLETTE_MOUNT,
                ],
            ),
        },
    ),
    "tests/test_tutorial/test_first_steps/test_tutorial001_tutorial002_tutorial003.py": _module(
        "The fixture selects asynchronous tutorial001 and synchronous tutorial003 applications. FastAPI owns the declared route and OpenAPI behavior; Starlette 1.6.0 owns route matching, the unmatched-path 404, and generic TestClient transport. Pydantic is not used by the declared path or response models in these examples.",
        {
            "get_client": _review(
                "tests/test_tutorial/test_first_steps/test_tutorial001_tutorial002_tutorial003.py",
                "get_client",
                ["app-routing", "openapi-docs"],
                "The fixture builds the async and sync app variants. Separate input workflows preserve the same / route and its documented operation for each app style.",
                "The ASGI inputs do not instantiate Starlette TestClient; they represent both route call styles at the app boundary.",
                [
                    _link(
                        FIRST_STEPS_ASYNC_RECIPE,
                        "fastapi.atlas-testing.first-steps-async",
                        ["get-root", "get-notfound", "openapi-document"],
                        sorted(set(HTTP + OPENAPI)),
                    ),
                    _link(
                        FIRST_STEPS_SYNC_RECIPE,
                        "fastapi.atlas-testing.first-steps-sync",
                        ["get-root", "get-notfound", "openapi-document"],
                        sorted(set(HTTP + OPENAPI)),
                    ),
                ],
                [
                    _FIRST_ASYNC,
                    _FIRST_SYNC,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_RESPONSE,
                    _FASTAPI_OPENAPI,
                    _FASTAPI_TESTCLIENT_REEXPORT,
                    _STARLETTE_TESTCLIENT_HTTP,
                    _STARLETTE_ROUTER,
                ],
            ),
            "test_get_path": _review(
                "tests/test_tutorial/test_first_steps/test_tutorial001_tutorial002_tutorial003.py",
                "test_get_path",
                ["app-routing", "response-serialization"],
                "The parametrized source sends GET / and GET /nonexistent through both asynchronous and synchronous tutorial apps.",
                "The recipe covers both input paths for each endpoint style and records ASGI responses; it does not call TestClient.get or json-decode the body.",
                [
                    _link(
                        FIRST_STEPS_ASYNC_RECIPE,
                        "fastapi.atlas-testing.first-steps-async",
                        ["get-root", "get-notfound"],
                        HTTP,
                    ),
                    _link(
                        FIRST_STEPS_SYNC_RECIPE,
                        "fastapi.atlas-testing.first-steps-sync",
                        ["get-root", "get-notfound"],
                        HTTP,
                    ),
                ],
                [
                    _FIRST_ASYNC,
                    _FIRST_SYNC,
                    _FASTAPI_HTTP_ROUTES,
                    _FASTAPI_RESPONSE,
                    _STARLETTE_TESTCLIENT_HTTP,
                    _STARLETTE_ROUTER,
                ],
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_first_steps/test_tutorial001_tutorial002_tutorial003.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The test checks the root operation's full OpenAPI document for each async/sync fixture app.",
                "The recipes select the complete parsed document for each route implementation without copying snapshot values into input data.",
                [
                    _link(
                        FIRST_STEPS_ASYNC_RECIPE,
                        "fastapi.atlas-testing.first-steps-async",
                        ["openapi-document"],
                        OPENAPI,
                    ),
                    _link(
                        FIRST_STEPS_SYNC_RECIPE,
                        "fastapi.atlas-testing.first-steps-sync",
                        ["openapi-document"],
                        OPENAPI,
                    ),
                ],
                [
                    _FIRST_ASYNC,
                    _FIRST_SYNC,
                    _FASTAPI_OPENAPI,
                    _FASTAPI_HTTP_ROUTES,
                    _STARLETTE_TESTCLIENT_HTTP,
                ],
            ),
        },
    ),
}


SOURCE_REVIEW_SUMMARY = {
    "requested_paths": 8,
    "existing_upstream_modules_reviewed": 7,
    "top_level_functions_reviewed": 28,
    "functions_with_case_and_selectors": 28,
    "functions_with_source_backed_exclusion": 0,
    "absent_upstream_paths": ["tests/test_websockets.py"],
    "absent_path_note": SOURCE_REVIEW_SCOPE_NOTE,
}


def validate_source_function_coverage() -> None:
    """Check that every top-level function in the seven extant modules is linked."""
    for test_path, module in TESTING_WEBSOCKET_TUTORIAL_REVIEW_MAPPINGS.items():
        tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
        actual = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        mapped = set(module["functions"])
        if actual != mapped:
            raise ValueError(
                f"source review mismatch in {test_path}: "
                f"unmapped={sorted(actual - mapped)}, stale={sorted(mapped - actual)}"
            )
        for name, review in module["functions"].items():
            if not review.get("workflow_cases"):
                raise ValueError(f"top-level function has no case link: {test_path}::{name}")
            if not review.get("observation_selectors"):
                raise ValueError(f"top-level function has no selectors: {test_path}::{name}")


validate_source_function_coverage()

__all__ = [
    "SOURCE_IDENTITIES",
    "SOURCE_REVIEW_SCOPE_NOTE",
    "SOURCE_REVIEW_SUMMARY",
    "TESTING_WEBSOCKET_TUTORIAL_REVIEW_MAPPINGS",
    "validate_source_function_coverage",
]
