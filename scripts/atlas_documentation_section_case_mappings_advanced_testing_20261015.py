"""Reviewed source mappings for pending advanced testing documentation sections.

Source identities: FastAPI 0.141.1 at
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f, Starlette 1.6.0 at
4f250d6b814587e20c5365f0a5f0c4d42bcb929f, and Starlette-RS at
b4c8a65c85e1b0d251ca05874412811eaa3ac7b8.

These mappings select FastAPI route, dependency, lifecycle, and Request behavior
from independently authored ASGI inputs. TestClient, AnyIO, HTTPX, pytest, and
general Python event-loop behavior remain owned by their respective tools.
"""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        mapping["action_ids"] = actions
    return mapping


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_ASYNC_TESTS = "tests/fixtures/input-recipes/parity/async_tests.yaml"
_DEPENDENCY_LIFECYCLE = "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml"
_LIFECYCLE = "tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml"
_WEBSOCKETS = "tests/fixtures/input-recipes/parity/testing_websockets.yaml"
_REQUEST = "tests/fixtures/input-recipes/parity/using_request_directly.yaml"
_REQUEST_INJECTION = "tests/fixtures/input-recipes/parity/request-injection-slice.yaml"

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]
_LIFESPAN_AND_HTTP = [
    "asgi.lifespan.application_errors",
    "asgi.lifespan.event_order",
    "asgi.lifespan.shutdown",
    "asgi.lifespan.startup",
    "asgi.lifespan.workload_trace",
    "http.body.bytes",
    "http.status",
    "warnings.category_message",
]
_WEBSOCKET = ["websocket.close_code", "websocket.event_order", "websocket.messages"]


DOC_SECTION_CASE_MAPPINGS_ADVANCED_TESTING_20261015 = {
    ("advanced/async-tests.md", "async-tests"): _excluded(
        "Async Tests { #async-tests }",
        1,
        99,
        (
            "The H1 is a page-level summary spanning the concrete async route and several test-"
            "harness topics. The route is mapped under Example; pytest/AnyIO/HTTPX guidance and "
            "general async-function advice have their own child dispositions."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/async-tests.md:1-99 introduces "
            "testing async applications, while the independent route sample is isolated at "
            "lines 21-40 and the test-runner/tooling material is isolated at lines 9-19, 41-90, "
            "and 91-98. A second H1 workflow would duplicate the narrower Example mapping and "
            "blur the external test-tool boundaries."
        ),
    ),
    ("advanced/async-tests.md", "example"): _workflow(
        "Example { #example }",
        21,
        40,
        _ASYNC_TESTS,
        ["fastapi.docs.async-tests.async-route"],
        ["async-root"],
        _HTTP,
        (
            "The selected direct ASGI GET / action exercises the included async FastAPI route "
            "and observes its response status, ordered headers, and body bytes. It does not "
            "exercise the example's pytest/AnyIO/HTTPX client setup or test lifecycle."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/async-tests.md:21-40 includes "
            "docs_src/async_tests/app_a_py310/main.py:1-8 and test_main.py:1-14. The independent "
            "recipe selects only async-root (async_tests.yaml:7-52; workload "
            "async_tests.py:6-13). FastAPI 0.141.1 classifies coroutine path operations in "
            "fastapi/routing.py:394 and dispatches them in fastapi/routing.py:344-354; "
            "pytest.mark.anyio, AsyncClient, and "
            "ASGITransport setup in the sample test are outside this response mapping."
        ),
    ),
    ("advanced/async-tests.md", "in-detail"): _excluded(
        "In Detail { #in-detail }",
        55,
        90,
        (
            "This section documents pytest.mark.anyio, HTTPX AsyncClient usage, awaiting client "
            "requests, and lifespan behavior of that test client. Those testing integrations "
            "are not FastAPI route inputs or outputs."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/async-tests.md:55-90 points to "
            "docs_src/async_tests/app_a_py310/test_main.py:1-14 and describes external pytest, "
            "AnyIO, HTTPX, and asgi-lifespan APIs. The direct ASGI route workflow at "
            "async_tests.yaml:7-52 cannot establish those client or lifespan-manager contracts."
        ),
    ),
    ("advanced/async-tests.md", "other-asynchronous-function-calls"): _excluded(
        "Other Asynchronous Function Calls { #other-asynchronous-function-calls }",
        91,
        99,
        (
            "This is general guidance about awaiting arbitrary async functions and managing "
            "objects tied to a Python event loop; it defines no separate FastAPI request "
            "behavior."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/async-tests.md:91-98 discusses "
            "arbitrary test-code calls and MotorClient loop affinity. The startup-callback "
            "example is covered at the FastAPI application lifecycle boundary under "
            "testing-events.md; Python scheduling and third-party client lifetime have no "
            "FastAPI-owned selector in this input set."
        ),
    ),
    (
        "advanced/testing-dependencies.md",
        "testing-dependencies-with-overrides",
    ): _excluded(
        "Testing Dependencies with Overrides { #testing-dependencies-with-overrides }",
        1,
        53,
        (
            "The H1 is a page-level summary. Its concrete override behavior is mapped under "
            "Overriding dependencies during testing, the external-service narrative is "
            "excluded separately, and the app.dependency_overrides API details already have "
            "a reviewed child mapping."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/testing-dependencies.md:1-53 "
            "contains one dependency-override topic with a concrete workflow at lines 3-9 and "
            "23-53, and a hypothetical provider-cost example at lines 11-22. The H1 adds no "
            "independent request operation; mapping the focused child sections avoids "
            "duplicating their input evidence."
        ),
    ),
    (
        "advanced/testing-dependencies.md",
        "overriding-dependencies-during-testing",
    ): _workflow(
        "Overriding dependencies during testing { #overriding-dependencies-during-testing }",
        3,
        53,
        _DEPENDENCY_LIFECYCLE,
        ["fastapi.dependencies.override-resolution"],
        ["replacement-parameter", "original-parameter-absent"],
        _HTTP_BODY_STATUS,
        (
            "The two selected requests exercise one FastAPI override: one supplies the "
            "replacement callable's region parameter and the other supplies only the original "
            "callable's query parameter. The response selectors sample override resolution and "
            "parameter requirements; they do not observe original-call side effects, "
            "subdependency suppression, test setup, or override reset."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/testing-dependencies.md:3-9 and "
            "23-53 describes replacing a dependency callable. The independent recipe selects "
            "case fastapi.dependencies.override-resolution and actions replacement-parameter "
            "and original-parameter-absent (dependency-lifecycle.yaml:149-221; workload "
            "dependency_lifecycle.py:36-48). FastAPI stores the override mapping on the app "
            "(fastapi/applications.py:967-983), looks up and analyzes the replacement callable "
            "in solve_dependencies (fastapi/dependencies/utils.py:619-638), and invokes the "
            "resolved callable at lines 673-680. This does not substantiate the page's broader "
            "claim about side effects in original or subdependency callables."
        ),
    ),
    ("advanced/testing-dependencies.md", "use-cases-external-service"): _excluded(
        "Use cases: external service { #use-cases-external-service }",
        11,
        22,
        (
            "The section is a hypothetical cost and latency narrative about an external "
            "authentication provider; it supplies no provider workload or independently "
            "observable FastAPI contract."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/testing-dependencies.md:11-22 "
            "describes when a user might substitute a mock user but defines no endpoint, "
            "dependency callable, or request/response observation. The selected override "
            "workflow under the parent section samples callable replacement only and does not "
            "claim billing, network latency, or authentication-provider behavior."
        ),
    ),
    (
        "advanced/testing-events.md",
        "testing-events-lifespan-and-startup-shutdown",
    ): _workflow(
        (
            "Testing Events: lifespan and startup - shutdown "
            "{ #testing-events-lifespan-and-startup-shutdown }"
        ),
        1,
        12,
        _LIFECYCLE,
        ["fastapi.lifecycle.router-events-legacy", "fastapi.lifecycle.app-lifespan-state"],
        ["lifespan", "request"],
        _LIFESPAN_AND_HTTP,
        (
            "The selected ASGI actions exercise one legacy on_event application and one "
            "lifespan-context application, followed by a route request; they observe lifecycle "
            "event traces, HTTP response status/body, and the captured warning category/message "
            "for legacy registration. This maps FastAPI's application lifecycle integration "
            "only. It does not map TestClient's context manager, its portal, or its "
            "startup/shutdown bridge."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/testing-events.md:3-12 includes the "
            "modern and deprecated examples at docs_src/app_testing/tutorial004_py310.py:9-43 "
            "and tutorial003_py310.py:9-24. The linked independent ASGI recipe selects "
            "fastapi.lifecycle.router-events-legacy and fastapi.lifecycle.app-lifespan-state, "
            "with lifespan and request actions (router-events-lifespan-upstream.yaml:9-189; "
            "workload router_events_lifespan_upstream.py:139-147); each case cites this page as "
            "upstream documentation. FastAPI passes on_startup, on_shutdown, and lifespan into "
            "APIRouter (fastapi/applications.py:984-992) and routes deprecated on_event calls "
            "to its router (fastapi/applications.py:4654-4681). Starlette 1.6.0 handles ASGI "
            "lifespan messages in starlette/routing.py:639-665. TestClient is a direct "
            "Starlette re-export (fastapi/testclient.py:1); its context entry/exit and "
            "handshake are Starlette-owned (starlette/testclient.py:679-735)."
        ),
    ),
    ("advanced/testing-websockets.md", "testing-websockets"): _workflow(
        "Testing WebSockets { #testing-websockets }",
        1,
        13,
        _WEBSOCKETS,
        ["fastapi.docs.testing-websockets.testclient-example"],
        ["websocket-testclient-example"],
        _WEBSOCKET,
        (
            "The selected ASGI WebSocket session sends connect and client-disconnect events "
            "and observes server messages, event order, and close code. It samples the FastAPI "
            "WebSocket route response; it does not exercise TestClient.websocket_connect or "
            "the session context-manager API. The tutorial's separate HTTP request is outside "
            "this section mapping."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/testing-websockets.md:3-11 points to "
            "docs_src/app_testing/tutorial002_py310.py:13-18. The independent recipe selects "
            "case fastapi.docs.testing-websockets.testclient-example and action "
            "websocket-testclient-example (testing_websockets.yaml:7-52; workload "
            "testing_websockets.py:14-18). FastAPI dispatches WebSocket path operations in "
            "fastapi/routing.py:764-831. TestClient is re-exported directly from Starlette "
            "(fastapi/testclient.py:1), and Starlette 1.6.0 owns websocket_connect and session "
            "context entry/exit (starlette/testclient.py:656-677,115-131)."
        ),
    ),
    ("advanced/using-request-directly.md", "using-the-request-directly"): _workflow(
        "Using the Request Directly { #using-the-request-directly }",
        1,
        56,
        _REQUEST,
        ["fastapi.docs.using-request-directly.client-host"],
        ["read-client-host", "request-openapi"],
        [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected route action reads a client's host through a Request-typed parameter; "
            "the OpenAPI action observes the separately declared path parameter. This samples "
            "one successful request and its documented path parameter, not all Request "
            "properties, invalid path values, direct-body validation rules, or every typed "
            "parameter source described on the page."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/using-request-directly.md:1-56 "
            "includes the Request/client-host example at lines 26-42 and the Starlette "
            "ownership note at lines 46-54. The independent recipe selects read-client-host "
            "and request-openapi (using_request_directly.yaml:7-84; workload "
            "using_request_directly.py:9-12), observing the response and the "
            "/items/{item_id} GET parameter projection. FastAPI classifies and injects a "
            "Request-typed parameter in fastapi/dependencies/utils.py:350-355,473-490,709-712; "
            "Starlette 1.6.0 derives Request.client from the ASGI client tuple in "
            "starlette/requests.py:161-167."
        ),
    ),
    ("advanced/using-request-directly.md", "details-about-the-request-object"): _workflow(
        "Details about the `Request` object { #details-about-the-request-object }",
        16,
        25,
        _REQUEST_INJECTION,
        ["fastapi.request-injection-slice.cached-parsed-body"],
        ["post-parsed-body"],
        _HTTP,
        (
            "The selected valid JSON POST reads the raw request body through Request while "
            "also supplying a normally declared Pydantic body parameter; it observes only "
            "the resulting HTTP response. This samples one successful coexistence case, not "
            "invalid-body errors, the absence of an OpenAPI request body, or all Request "
            "properties and validation boundaries."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/using-request-directly.md:16-25 "
            "states that Request comes from Starlette, direct body access bypasses FastAPI's "
            "validation/conversion/documentation path, and normally declared parameters retain "
            "that path. The independent recipe selects case "
            "fastapi.request-injection-slice.cached-parsed-body and action post-parsed-body "
            "(request-injection-slice.yaml:49-90; workload request_injection_slice.py:29-36). "
            "FastAPI injects Request outside field handling in "
            "fastapi/dependencies/utils.py:350-355,473-490,709-712, while declared body fields "
            "are resolved at lines 700-708. The input is valid JSON and does not establish "
            "failure or OpenAPI behavior."
        ),
    ),
}
