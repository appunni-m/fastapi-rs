"""Function-level source review for dependency lifecycle and security tests.

The mappings retain the full source-test denominator, reuse existing input
cases wherever their behavior already exists, and add one independent
input-only ASGI recipe for the remaining public workflows. They describe
stimuli and source coverage only; they do not record parity results.
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
        "role": "sole generic ASGI, HTTP/WebSocket response, streaming, Mount, and TestClient contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "owns BaseModel field validation and schema semantics in duplicate-body cases",
    },
}

TEST_MODULES = (
    "tests/test_dependency_after_yield_streaming.py",
    "tests/test_dependency_cache.py",
    "tests/test_dependency_duplicates.py",
    "tests/test_dependency_security_overrides.py",
    "tests/test_dependency_yield_scope.py",
    "tests/test_dependency_yield_scope_websockets.py",
    "tests/test_generic_parameterless_depends.py",
)

NEW_RECIPE = "tests/fixtures/input-recipes/parity/dependency-lifecycle-security-review.yaml"
NEW_WORKLOAD = "tests/fixtures/workloads/dependency_lifecycle_security_review.py"
HTTP = ["http.status", "http.body.bytes"]
HTTP_JSON = ["http.status", "http.body.json"]
HTTP_AND_APP_ERROR = ["http.status", "http.body.bytes", "validation.error_class"]
WEBSOCKET = ["websocket.messages", "websocket.event_order", "websocket.close_code"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_functions(test_path: str) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def _test_function_span(test_path: str, name: str) -> dict[str, Any]:
    matches = [node for node in _test_functions(test_path) if node.name == name]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {name} in {test_path}")
    node = matches[0]
    return _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 source test function {name}",
    )


def _test_setup_span(test_path: str) -> dict[str, Any]:
    tests = _test_functions(test_path)
    first_test_line = min((node.lineno for node in tests), default=1)
    return _source(
        test_path,
        1,
        max(first_test_line - 1, 1),
        "upstream app, dependency, route, and fixture setup exercised by this test module",
    )


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


def _reviewed(
    test_path: str,
    function_name: str,
    *,
    features: list[str],
    selectors: list[str],
    rationale: str,
    links: list[dict[str, Any]],
    gate: str,
    evidence: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(features),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": gate,
        "workflow_cases": list(links),
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            _test_setup_span(test_path),
            *evidence,
        ],
    }


def _excluded(
    test_path: str,
    function_name: str,
    *,
    features: list[str],
    selectors: list[str],
    reason: str,
    evidence: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    return {
        "review_status": "reviewed_excluded",
        "feature_ids": list(features),
        "observation_selectors": list(selectors),
        "rationale": reason,
        "exclusion_reason": reason,
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            _test_setup_span(test_path),
            *evidence,
        ],
    }


_DEPENDENCY_SCOPE_BUILD = _source(
    "fastapi/dependencies/utils.py",
    279,
    320,
    "FastAPI builds dependency nodes, enforces valid yield-scope nesting, and propagates security scopes",
)
_DEPENDENCY_SOLVER = _source(
    "fastapi/dependencies/utils.py",
    586,
    680,
    "FastAPI resolves dependencies, consults the request-local cache, and enters yield dependencies on the function or request exit stack",
)
_SECURITY_CACHE_KEY = _source(
    "fastapi/dependencies/models.py",
    82,
    96,
    "FastAPI includes applicable OAuth scopes and computed cleanup scope in a dependency cache key",
)
_HTTP_EXIT_STACKS = _source(
    "fastapi/routing.py",
    137,
    158,
    "FastAPI closes the function stack before sending the response and the request stack after response dispatch",
)
_WEBSOCKET_EXIT_STACKS = _source(
    "fastapi/routing.py",
    163,
    184,
    "FastAPI wraps WebSocket endpoint dispatch in function and request dependency exit stacks",
)
_WEBSOCKET_DEPENDENCY_SOLVER = _source(
    "fastapi/routing.py",
    775,
    794,
    "FastAPI solves dependencies from a WebSocket connection before calling the endpoint",
)
_OVERRIDE_REBUILD = _source(
    "fastapi/dependencies/utils.py",
    623,
    638,
    "FastAPI substitutes an override callable and rebuilds its dependency signature with inherited security scopes",
)
_STARLETTE_STREAMING = _source(
    "starlette/responses.py",
    222,
    282,
    "Starlette 1.6.0 implements StreamingResponse body iteration, ASGI send, and disconnect handling",
)
_STARLETTE_MOUNT = _source(
    "starlette/routing.py",
    363,
    420,
    "Starlette 1.6.0 owns generic mounted-application path matching and scope changes",
)
_FASTAPI_TESTCLIENT_REEXPORT = _source(
    "fastapi/testclient.py",
    1,
    1,
    "FastAPI re-exports Starlette TestClient directly",
)
_STARLETTE_TESTCLIENT = _source(
    "starlette/testclient.py",
    1,
    48,
    "Starlette 1.6.0 TestClient selects HTTPX 2 when installed and otherwise uses the HTTPX compatibility fallback",
)
_PYTHON_PROFILE = _source(
    "pyproject.toml",
    5,
    12,
    "FastAPI 0.141.1 declares Python >=3.10",
)

_ASGI_CLIENT_GATE = "Partial: the linked input runs the public ASGI application directly, not FastAPI/Starlette TestClient or HTTPX. It compares response events and any surfaced ASGI exception; it does not claim TestClient raise_server_exceptions behavior, buffered stream/session mechanics, or HTTPX transport compatibility. Starlette 1.6.0 owns those generic client and transport semantics."
_PYDANTIC_GATE = "Partial: the independent inputs use fresh names, fields, and values. Pydantic 2.13.4 owns BaseModel validation and generated model schema details; FastAPI owns body-field composition and dependency reuse. Only the linked HTTP observations and selected schema pointers are claimed."
_WEBSOCKET_GATE = "Partial: the workflow sends explicit ASGI WebSocket connect/disconnect events and observes messages, send order, close code, and a follow-up cleanup read. It does not reproduce TestClient.websocket_connect context-manager or HTTPX behavior; those transport semantics belong to Starlette 1.6.0."
_MOUNT_GATE = "Partial: the new app/router scope case reaches independent FastAPI routes under a mounted child app so one input recipe can exercise both app-level and router-level dependencies. Starlette 1.6.0 owns Mount path/scope mechanics. Direct ASGI error capture does not reproduce TestClient raise_server_exceptions=False."

_LIFECYCLE = "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml"
_WAVE = "tests/fixtures/input-recipes/parity/dependency-wave.yaml"
_GRAPH = "tests/fixtures/input-recipes/parity/dependency-wave-graphs.yaml"
_WAVE_LIFECYCLE = "tests/fixtures/input-recipes/parity/dependency-wave-lifecycle.yaml"
_CACHE_SOURCE = "tests/fixtures/input-recipes/parity/dependency-cache-source-wave.yaml"

_FUNCTIONS: dict[str, dict[str, dict[str, Any]]] = {
    "tests/test_dependency_after_yield_streaming.py": {
        "test_regular_no_stream": _reviewed(
            "tests/test_dependency_after_yield_streaming.py",
            "test_regular_no_stream",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="A non-streaming route consumes and serializes values from a yielded session dependency; the existing public dependency-yield input is an independent sample of this basic lifecycle.",
            links=[
                _link(
                    _WAVE,
                    "fastapi.dependency-wave.dependency-yield-resource.test-get-db",
                    ["dispatch"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS),
        ),
        "test_stream_simple": _excluded(
            "tests/test_dependency_after_yield_streaming.py",
            "test_stream_simple",
            features=["response-serialization"],
            selectors=HTTP,
            reason="The response body comes from a static iterator that does not read the yielded session. This function checks buffered StreamingResponse content only; generic streaming and TestClient body aggregation belong to Starlette 1.6.0.",
            evidence=(_STARLETTE_STREAMING, _STARLETTE_TESTCLIENT),
        ),
        "test_stream_session": _reviewed(
            "tests/test_dependency_after_yield_streaming.py",
            "test_stream_session",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="The response iterator reads the dependency-owned session, so the stream proves that FastAPI keeps a yielded resource available through response consumption.",
            links=[
                _link(
                    _WAVE_LIFECYCLE,
                    "fastapi.dependencies.streaming-resource-lifetime",
                    ["stream-resource-open", "stream-resource-cleanup"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS, _STARLETTE_STREAMING),
        ),
        "test_broken_session_data": _reviewed(
            "tests/test_dependency_after_yield_streaming.py",
            "test_broken_session_data",
            features=["dependency-security", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="The dependency yields an already closed session, so endpoint iteration raises before response streaming starts; the new ASGI case records the response and surfaced application error.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.broken-session-data-lifecycle",
                    ["closed-session-access"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS),
        ),
        "test_broken_session_data_no_raise": _reviewed(
            "tests/test_dependency_after_yield_streaming.py",
            "test_broken_session_data_no_raise",
            features=["dependency-security", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="This is the same closed-resource failure observed through a TestClient configured not to re-raise server exceptions; the new direct-ASGI case covers the response/error pair and leaves the client suppression policy as a gate.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.broken-session-data-lifecycle",
                    ["closed-session-access"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _FASTAPI_TESTCLIENT_REEXPORT,
                _STARLETTE_TESTCLIENT,
            ),
        ),
        "test_broken_session_stream_raise": _reviewed(
            "tests/test_dependency_after_yield_streaming.py",
            "test_broken_session_stream_raise",
            features=["dependency-security", "response-serialization", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="Iteration of a dependency-owned resource fails after StreamingResponse begins. The existing closed-resource stream input observes the response/error boundary; the TestClient exception class and re-raise behavior are not claimed.",
            links=[
                _link(
                    _WAVE_LIFECYCLE,
                    "fastapi.dependencies.streaming-closed-resource-error",
                    ["stream-closed-before-iteration"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=(
                _ASGI_CLIENT_GATE
                + " The source comment allows ValueError or ExceptionGroup across Pydantic major versions; this profile is pinned to Pydantic 2.13.4, but the linked independent stream uses a different exception class."
            ),
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS, _STARLETTE_STREAMING),
        ),
        "test_broken_session_stream_no_raise": _reviewed(
            "tests/test_dependency_after_yield_streaming.py",
            "test_broken_session_stream_no_raise",
            features=["dependency-security", "response-serialization", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="The source expects a 200 response with an empty body when stream iteration fails after response start and TestClient suppresses the server exception; the existing direct-ASGI case records the same response/error phase without claiming TestClient suppression.",
            links=[
                _link(
                    _WAVE_LIFECYCLE,
                    "fastapi.dependencies.streaming-closed-resource-error",
                    ["stream-closed-before-iteration"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_STREAMING,
                _STARLETTE_TESTCLIENT,
            ),
        ),
    },
    "tests/test_dependency_cache.py": {
        "test_normal_counter": _reviewed(
            "tests/test_dependency_cache.py",
            "test_normal_counter",
            features=["dependency-security"],
            selectors=HTTP_JSON,
            rationale="A repeated dependency is reused within one request and resolved afresh on the next request; the existing cache-reuse input already links these source assertions to two requests.",
            links=[
                _link(
                    _LIFECYCLE,
                    "fastapi.dependencies.cache-reuse",
                    ["first-request", "next-request"],
                    HTTP_JSON,
                )
            ],
            gate="Partial: the input uses independent callable names and counter values; FastAPI request-local cache behavior is sampled, while ASGI response encoding and transport remain Starlette 1.6.0 behavior.",
            evidence=(_DEPENDENCY_SOLVER, _SECURITY_CACHE_KEY),
        ),
        "test_sub_counter": _reviewed(
            "tests/test_dependency_cache.py",
            "test_sub_counter",
            features=["dependency-security"],
            selectors=HTTP,
            rationale="A common subdependency is resolved once through a parent and once as a direct parameter, then resolved anew for the following request. Both the existing broad cache case and source-focused two-request case are retained.",
            links=[
                _link(
                    _LIFECYCLE,
                    "fastapi.dependencies.cache-reuse",
                    ["first-request", "next-request"],
                    HTTP_JSON,
                ),
                _link(
                    _CACHE_SOURCE,
                    "fastapi.dependencies.cache-shared-subdependency-source-wave",
                    ["first-request", "next-request"],
                    HTTP,
                ),
            ],
            gate="Partial: the source-focused workflow preserves the nested/direct edge shape but changes callable names and values; Starlette 1.6.0 owns generic HTTP transport and Pydantic does not validate these scalar counters.",
            evidence=(_DEPENDENCY_SOLVER, _SECURITY_CACHE_KEY),
        ),
        "test_sub_counter_no_cache": _reviewed(
            "tests/test_dependency_cache.py",
            "test_sub_counter_no_cache",
            features=["dependency-security"],
            selectors=HTTP,
            rationale="A direct use_cache=False dependency edge resolves again after the nested parent has populated the request cache; both existing general and source-focused cases are linked.",
            links=[
                _link(
                    _LIFECYCLE,
                    "fastapi.dependencies.cache-bypass",
                    ["first-request", "next-request"],
                    HTTP_JSON,
                ),
                _link(
                    _CACHE_SOURCE,
                    "fastapi.dependencies.cache-bypass-subdependency-source-wave",
                    ["first-request", "next-request"],
                    HTTP,
                ),
            ],
            gate="Partial: the independent cases use new names and marker values; they sample repeated graph-edge cache bypass but do not assert source counter values or Python callable identities. Starlette 1.6.0 owns generic HTTP transport.",
            evidence=(_DEPENDENCY_SOLVER, _SECURITY_CACHE_KEY),
        ),
        "test_security_cache": _reviewed(
            "tests/test_dependency_cache.py",
            "test_security_cache",
            features=["dependency-security"],
            selectors=HTTP_JSON,
            rationale="The same callable is used through plain Depends and two Security declarations with equal scopes; the new two-request input exposes the scope-sensitive key and request-local cache lifetime.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.security.scope-sensitive-dependency-cache",
                    ["first-scope-counter-request", "next-scope-counter-request"],
                    HTTP_JSON,
                )
            ],
            gate="Partial: the workload uses a new scalar counter and route; it samples FastAPI's callable/scope cache key and per-request reset only. Starlette 1.6.0 owns the generic HTTP transport.",
            evidence=(_DEPENDENCY_SOLVER, _SECURITY_CACHE_KEY),
        ),
    },
    "tests/test_dependency_duplicates.py": {
        "test_no_duplicates_invalid": _reviewed(
            "tests/test_dependency_duplicates.py",
            "test_no_duplicates_invalid",
            features=["dependency-security", "request-validation"],
            selectors=HTTP,
            rationale="Distinct body parameters require distinct embedded fields; the existing missing-second-field input samples the resulting request-validation response.",
            links=[
                _link(
                    _GRAPH,
                    "fastapi.dependencies.separate-body-validation",
                    ["missing-second-body-field"],
                    HTTP,
                )
            ],
            gate=_PYDANTIC_GATE,
            evidence=(_DEPENDENCY_SCOPE_BUILD,),
        ),
        "test_no_duplicates": _reviewed(
            "tests/test_dependency_duplicates.py",
            "test_no_duplicates",
            features=["dependency-security", "request-validation"],
            selectors=HTTP,
            rationale="Different body-bearing callables are combined as separate request-body fields; the existing success input uses the equivalent two-field model shape.",
            links=[
                _link(
                    _GRAPH,
                    "fastapi.dependencies.separate-body-fields",
                    ["two-named-body-inputs"],
                    HTTP,
                )
            ],
            gate=_PYDANTIC_GATE,
            evidence=(_DEPENDENCY_SCOPE_BUILD,),
        ),
        "test_duplicates": _reviewed(
            "tests/test_dependency_duplicates.py",
            "test_duplicates",
            features=["dependency-security", "request-validation"],
            selectors=HTTP,
            rationale="The same body dependency is reached both directly and through the endpoint graph and its resolved model value is reused; the existing duplicate-body input links a one-field payload to that graph shape.",
            links=[
                _link(
                    _GRAPH, "fastapi.dependencies.duplicate-body-dependencies", ["body-reuse"], HTTP
                )
            ],
            gate=_PYDANTIC_GATE,
            evidence=(_DEPENDENCY_SOLVER,),
        ),
        "test_sub_duplicates": _reviewed(
            "tests/test_dependency_duplicates.py",
            "test_sub_duplicates",
            features=["dependency-security", "request-validation"],
            selectors=HTTP,
            rationale="A body dependency is repeated inside a subdependency graph while the endpoint also declares the same model body; the existing nested-body case samples this reuse path.",
            links=[
                _link(
                    _GRAPH,
                    "fastapi.dependencies.duplicate-body-dependencies",
                    ["nested-body-reuse"],
                    HTTP,
                )
            ],
            gate=_PYDANTIC_GATE,
            evidence=(_DEPENDENCY_SOLVER,),
        ),
        "test_openapi_schema": _reviewed(
            "tests/test_dependency_duplicates.py",
            "test_openapi_schema",
            features=["dependency-security", "openapi-docs", "request-validation"],
            selectors=["openapi.request_schema"],
            rationale="The source compares a whole OpenAPI document. Existing input cases select the three request-body schema projections for reused, nested, and separate body dependencies; unrelated OpenAPI fields are not claimed.",
            links=[
                _link(
                    _GRAPH,
                    "fastapi.dependencies.duplicate-body-dependencies",
                    ["body-schema-links"],
                    ["openapi.request_schema"],
                ),
                _link(
                    _GRAPH,
                    "fastapi.dependencies.separate-body-fields",
                    ["separate-body-schema"],
                    ["openapi.request_schema"],
                ),
            ],
            gate="Partial: the source snapshot includes complete paths, operations, responses, and component schemas. The existing cases select only the relevant requestBody schema pointers; Pydantic 2.13.4 owns model schema construction.",
            evidence=(
                _source(
                    "fastapi/openapi/utils.py",
                    290,
                    400,
                    "FastAPI composes route dependency body fields and model references into OpenAPI operations",
                ),
            ),
        ),
    },
    "tests/test_dependency_security_overrides.py": {
        "test_normal": _reviewed(
            "tests/test_dependency_security_overrides.py",
            "test_normal",
            features=["dependency-security"],
            selectors=HTTP,
            rationale="The unmodified Security dependency returns the baseline identity and required scopes; the new scope-preservation input includes that baseline as an explicit action.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.security.security-scopes-dependency-override",
                    ["baseline-security-scopes"],
                    HTTP,
                )
            ],
            gate="Partial: the independent route uses fresh callable names, user labels, and scopes; it samples SecurityScopes injection and response values. Starlette 1.6.0 owns generic HTTP transport.",
            evidence=(_DEPENDENCY_SCOPE_BUILD,),
        ),
        "test_override_data": _reviewed(
            "tests/test_dependency_security_overrides.py",
            "test_override_data",
            features=["dependency-security"],
            selectors=HTTP,
            rationale="FastAPI replaces a plain data dependency while leaving the Security dependency and its scope value unchanged; the existing dependency override case contains an independent data-provider replacement.",
            links=[
                _link(
                    _GRAPH,
                    "fastapi.security.dependency-overrides",
                    ["replacement-data-provider"],
                    HTTP,
                )
            ],
            gate="Partial: the existing input changes endpoint values and dependency names and does not reproduce the exact upstream route or test-time override reset. Generic HTTP transport is Starlette 1.6.0-owned.",
            evidence=(_OVERRIDE_REBUILD, _DEPENDENCY_SOLVER),
        ),
        "test_override_security": _reviewed(
            "tests/test_dependency_security_overrides.py",
            "test_override_security",
            features=["dependency-security"],
            selectors=HTTP,
            rationale="An overridden Security callable receives the route's scopes and returns a replacement identity; the new case records both baseline and override actions, while the existing security-provider case samples override resolution separately.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.security.security-scopes-dependency-override",
                    ["baseline-security-scopes", "overridden-security-scopes"],
                    HTTP,
                ),
                _link(
                    _GRAPH,
                    "fastapi.security.dependency-overrides",
                    ["replacement-security-provider"],
                    HTTP,
                ),
            ],
            gate="Partial: the new workflow preserves scope injection through an override but uses independent functions and route paths; the existing provider case omits SecurityScopes in its replacement. Starlette 1.6.0 owns generic HTTP transport.",
            evidence=(_DEPENDENCY_SCOPE_BUILD, _OVERRIDE_REBUILD, _DEPENDENCY_SOLVER),
        ),
    },
    "tests/test_dependency_yield_scope.py": {
        "test_function_scope": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_function_scope",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="A function-scoped resource is closed before the streamed response body is consumed; the existing scope-cleanup input observes function-scope state through the response path.",
            links=[
                _link(
                    _LIFECYCLE,
                    "fastapi.dependencies.yield-scope-cleanup",
                    ["first-response", "subsequent-response"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS, _STARLETTE_STREAMING),
        ),
        "test_request_scope": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_request_scope",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="A request-scoped resource remains open while the streamed response is consumed and closes after the request; the existing scope-cleanup case samples both response and later request state.",
            links=[
                _link(
                    _LIFECYCLE,
                    "fastapi.dependencies.yield-scope-cleanup",
                    ["first-response", "subsequent-response"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS, _STARLETTE_STREAMING),
        ),
        "test_two_scopes": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_two_scopes",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="The same streamed response reads one function-scoped and one request-scoped resource together; the existing yield-scope input declares both lifetime classes and observes the response/cleanup boundary.",
            links=[
                _link(
                    _LIFECYCLE,
                    "fastapi.dependencies.yield-scope-cleanup",
                    ["first-response", "subsequent-response"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(_DEPENDENCY_SOLVER, _HTTP_EXIT_STACKS, _STARLETTE_STREAMING),
        ),
        "test_sub": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_sub",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="A request-scoped generator depends twice on the same request resource and yields a named resource tuple; the new case observes the shared identity's open state during response streaming and cleanup afterward.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-http",
                    ["nested-request-scope", "http-scope-cleanup"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_STREAMING,
            ),
        ),
        "test_broken_scope": _excluded(
            "tests/test_dependency_yield_scope.py",
            "test_broken_scope",
            features=["dependency-security", "public-api-errors"],
            selectors=[
                "construction.outcome",
                "construction.exception_class",
                "construction.exception_message",
            ],
            reason="The function expects FastAPI to raise DependencyScopeError while registering an invalid route before any ASGI request exists. Workflow v2 has no construction action, so the registration-time exception is retained as an explicit exclusion.",
            evidence=(_DEPENDENCY_SCOPE_BUILD,),
        ),
        "test_named_function_scope": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_named_function_scope",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="A function-scoped yielding parent and child both close before a StreamingResponse consumes the body; the new nested-scope route exposes their post-cleanup states.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-http",
                    ["named-function-scope"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_STREAMING,
            ),
        ),
        "test_regular_function_scope": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_regular_function_scope",
            features=["dependency-security", "response-serialization"],
            selectors=HTTP,
            rationale="A regular parent dependency returns a named object while its nested function-scoped yielded child closes before the streamed body is consumed; the new route makes both states observable.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-http",
                    ["regular-function-scope"],
                    HTTP,
                )
            ],
            gate=_ASGI_CLIENT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_STREAMING,
            ),
        ),
        "test_router_level_dep_scope_function": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_router_level_dep_scope_function",
            features=["dependency-security", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="An APIRouter-level function-scoped yielded dependency raises HTTPException during cleanup before response dispatch; the new case reaches the included router and records response/error state.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.app-router-yield-scopes",
                    ["router-function-scope-cleanup"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_MOUNT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_MOUNT,
            ),
        ),
        "test_router_level_dep_scope_request": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_router_level_dep_scope_request",
            features=["dependency-security", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="An APIRouter-level request-scoped yielded dependency raises after the response has started; the new case records the sent response and surfaced ASGI exception.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.app-router-yield-scopes",
                    ["router-request-scope-cleanup"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_MOUNT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_MOUNT,
            ),
        ),
        "test_app_level_dep_scope_function": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_app_level_dep_scope_function",
            features=["dependency-security", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="An app-level function-scoped yielded dependency raises HTTPException before response dispatch; the new mounted FastAPI child app includes a separate route for this cleanup phase.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.app-router-yield-scopes",
                    ["app-function-scope-cleanup"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_MOUNT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_MOUNT,
            ),
        ),
        "test_app_level_dep_scope_request": _reviewed(
            "tests/test_dependency_yield_scope.py",
            "test_app_level_dep_scope_request",
            features=["dependency-security", "public-api-errors"],
            selectors=HTTP_AND_APP_ERROR,
            rationale="An app-level request-scoped yielded dependency raises after response send; the new case distinguishes its response boundary from the function-scoped path.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.app-router-yield-scopes",
                    ["app-request-scope-cleanup"],
                    HTTP_AND_APP_ERROR,
                )
            ],
            gate=_MOUNT_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _HTTP_EXIT_STACKS,
                _STARLETTE_MOUNT,
            ),
        ),
    },
    "tests/test_dependency_yield_scope_websockets.py": {
        "test_function_scope": _reviewed(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_function_scope",
            features=["dependency-security", "websocket-lifecycle"],
            selectors=WEBSOCKET,
            rationale="The function-scoped resource is open while the WebSocket endpoint sends its message and is finalized when the endpoint function returns; the existing WebSocket function-scope input samples message and cleanup.",
            links=[
                _link(
                    _WAVE_LIFECYCLE,
                    "fastapi.dependencies.websocket-function-scope",
                    ["function-scope-session", "function-scope-cleanup"],
                    WEBSOCKET,
                )
            ],
            gate=_WEBSOCKET_GATE,
            evidence=(_DEPENDENCY_SOLVER, _WEBSOCKET_EXIT_STACKS, _WEBSOCKET_DEPENDENCY_SOLVER),
        ),
        "test_request_scope": _reviewed(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_request_scope",
            features=["dependency-security", "websocket-lifecycle"],
            selectors=WEBSOCKET,
            rationale="The request-scoped resource stays open through the WebSocket handler and is finalized after disconnect; the existing request-scope input links messages and a follow-up cleanup observation.",
            links=[
                _link(
                    _WAVE_LIFECYCLE,
                    "fastapi.dependencies.websocket-request-scope",
                    ["request-scope-session", "request-scope-cleanup"],
                    WEBSOCKET,
                )
            ],
            gate=_WEBSOCKET_GATE,
            evidence=(_DEPENDENCY_SOLVER, _WEBSOCKET_EXIT_STACKS, _WEBSOCKET_DEPENDENCY_SOLVER),
        ),
        "test_two_scopes": _reviewed(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_two_scopes",
            features=["dependency-security", "websocket-lifecycle"],
            selectors=WEBSOCKET,
            rationale="A single WebSocket endpoint reads function- and request-scoped yielded resources together, then observes cleanup after session termination; the new case includes that combined path.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-websocket",
                    ["two-scopes-session", "websocket-scope-cleanup"],
                    WEBSOCKET,
                )
            ],
            gate=_WEBSOCKET_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _WEBSOCKET_EXIT_STACKS,
                _WEBSOCKET_DEPENDENCY_SOLVER,
            ),
        ),
        "test_sub": _reviewed(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_sub",
            features=["dependency-security", "websocket-lifecycle"],
            selectors=WEBSOCKET,
            rationale="Two dependency edges resolve the same request-scoped resource into a yielded parent; the new WebSocket case observes shared open state and cleanup after disconnect.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-websocket",
                    ["nested-request-session", "websocket-scope-cleanup"],
                    WEBSOCKET,
                )
            ],
            gate=_WEBSOCKET_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _WEBSOCKET_EXIT_STACKS,
                _WEBSOCKET_DEPENDENCY_SOLVER,
            ),
        ),
        "test_broken_scope": _excluded(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_broken_scope",
            features=["dependency-security", "public-api-errors", "websocket-lifecycle"],
            selectors=[
                "construction.outcome",
                "construction.exception_class",
                "construction.exception_message",
            ],
            reason="The function expects FastAPI to raise DependencyScopeError while registering an invalid WebSocket route before ASGI connection events exist. Workflow v2 has no construction action, so registration-time scope rejection is recorded as an exclusion.",
            evidence=(_DEPENDENCY_SCOPE_BUILD,),
        ),
        "test_named_function_scope": _reviewed(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_named_function_scope",
            features=["dependency-security", "websocket-lifecycle"],
            selectors=WEBSOCKET,
            rationale="A function-scoped yielded parent and its function-scoped child remain open for the sent WebSocket message and close as the endpoint exits; the new case records both states and cleanup.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-websocket",
                    ["named-function-session", "websocket-scope-cleanup"],
                    WEBSOCKET,
                )
            ],
            gate=_WEBSOCKET_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _WEBSOCKET_EXIT_STACKS,
                _WEBSOCKET_DEPENDENCY_SOLVER,
            ),
        ),
        "test_regular_function_scope": _reviewed(
            "tests/test_dependency_yield_scope_websockets.py",
            "test_regular_function_scope",
            features=["dependency-security", "websocket-lifecycle"],
            selectors=WEBSOCKET,
            rationale="A regular parent returns a named resource while the nested function-scoped generator stays open through the WebSocket message and closes on endpoint return; the new case distinguishes it from a yielding parent.",
            links=[
                _link(
                    NEW_RECIPE,
                    "fastapi.dependencies.nested-yield-scopes-websocket",
                    ["regular-function-session", "websocket-scope-cleanup"],
                    WEBSOCKET,
                )
            ],
            gate=_WEBSOCKET_GATE,
            evidence=(
                _DEPENDENCY_SCOPE_BUILD,
                _DEPENDENCY_SOLVER,
                _WEBSOCKET_EXIT_STACKS,
                _WEBSOCKET_DEPENDENCY_SOLVER,
            ),
        ),
    },
    "tests/test_generic_parameterless_depends.py": {
        "test_generic_parameterless_depends": _reviewed(
            "tests/test_generic_parameterless_depends.py",
            "test_generic_parameterless_depends",
            features=["dependency-security"],
            selectors=HTTP_JSON,
            rationale="A parameterless generic Depends declaration resolves the class bound to the endpoint's type parameter for two HTTP routes; the existing generic dependency input contains both route requests.",
            links=[
                _link(
                    _WAVE,
                    "fastapi.dependency-wave.generic-parameterless.test-generic-parameterless-depends",
                    ["class-a", "class-b"],
                    HTTP_JSON,
                )
            ],
            gate="Partial: the input uses independently declared generic aliases, classes, and routes; it samples FastAPI dependency resolution but does not claim the source OpenAPI snapshot. Starlette 1.6.0 owns generic HTTP transport.",
            evidence=(_DEPENDENCY_SCOPE_BUILD, _DEPENDENCY_SOLVER),
        ),
        "test_openapi_schema": _excluded(
            "tests/test_generic_parameterless_depends.py",
            "test_openapi_schema",
            features=["dependency-security", "openapi-docs"],
            selectors=["openapi.document"],
            reason="This function compares the complete OpenAPI JSON document for both generic routes. The HTTP dependency case does not cover OpenAPI projection; the complete snapshot remains assigned to the OpenAPI/docs review wave.",
            evidence=(
                _source(
                    "fastapi/openapi/utils.py",
                    290,
                    400,
                    "FastAPI composes dependency declarations and route metadata into OpenAPI operations",
                ),
            ),
        ),
    },
}

_MODULE_RATIONALES = {
    "tests/test_dependency_after_yield_streaming.py": "Public yielded-dependency behavior across normal responses, streamed resource consumption, and failures; Starlette 1.6.0 owns generic StreamingResponse and TestClient transport behavior.",
    "tests/test_dependency_cache.py": "FastAPI dependency-cache reuse, use_cache bypass, and security-scope-sensitive cache keys, sampled through public HTTP routes.",
    "tests/test_dependency_duplicates.py": "FastAPI dependency graph body-field composition and duplicate body reuse; Pydantic 2.13.4 owns model validation and schema details.",
    "tests/test_dependency_security_overrides.py": "Security and ordinary dependency overrides, including inherited SecurityScopes on an override callable.",
    "tests/test_dependency_yield_scope.py": "Yield dependencies across function/request scope, nested scope validity, app/router placement, HTTP responses, and streamed bodies.",
    "tests/test_dependency_yield_scope_websockets.py": "Yield dependency scope behavior during WebSocket endpoint execution and after disconnect; Starlette 1.6.0 owns generic WebSocket ASGI/TestClient behavior.",
    "tests/test_generic_parameterless_depends.py": "Generic parameterless Depends resolution over HTTP; its full OpenAPI snapshot is explicitly excluded from this dependency-resolution mapping.",
}

_MODULE_SELECTORS = {
    test_path: sorted(
        {
            selector
            for review in function_reviews.values()
            for selector in review["observation_selectors"]
        }
    )
    for test_path, function_reviews in _FUNCTIONS.items()
}

DEPENDENCY_LIFECYCLE_SECURITY_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    test_path: {
        "rationale": _MODULE_RATIONALES[test_path],
        "module_observation_selectors": _MODULE_SELECTORS[test_path],
        "supporting_sources": [_test_setup_span(test_path)],
        "functions": function_reviews,
    }
    for test_path, function_reviews in _FUNCTIONS.items()
}

# Keep the source-visible denominator tied to the pinned upstream AST, not to
# the subset with runnable or currently expressible observations.
SOURCE_VISIBLE_FUNCTIONS = {
    test_path: [node.name for node in _test_functions(test_path)] for test_path in TEST_MODULES
}
for _test_path, _function_names in SOURCE_VISIBLE_FUNCTIONS.items():
    _reviewed_names = set(DEPENDENCY_LIFECYCLE_SECURITY_REVIEW_MAPPINGS[_test_path]["functions"])
    if _reviewed_names != set(_function_names):
        raise ValueError(
            f"source-test denominator mismatch for {_test_path}: "
            f"missing={sorted(set(_function_names) - _reviewed_names)}, "
            f"extra={sorted(_reviewed_names - set(_function_names))}"
        )

REVIEW_LIMITS = {
    "python": {
        "minimum": "3.10",
        "source": "FastAPI 0.141.1 pyproject.toml requires Python >=3.10",
        "exact_execution_version": "not asserted by this source-only review",
    },
    "testclient": {
        "fastapi_import": "fastapi.testclient.TestClient is a direct Starlette re-export",
        "starlette_contract": "Starlette 1.6.0",
        "httpx2_from_fastapi_uv_lock": "2.5.0",
        "legacy_httpx_from_fastapi_uv_lock": "0.28.1",
        "version_pairing_limit": "FastAPI's uv.lock resolves Starlette 1.3.1, so its HTTPX versions do not establish TestClient compatibility for the separately pinned Starlette 1.6.0 contract",
        "workload_boundary": "new and existing linked workloads are direct ASGI inputs; they do not run TestClient or HTTPX",
    },
    "pydantic": {
        "version": "2.13.4",
        "limit": "the upstream stream test's ValueError/ExceptionGroup compatibility note is not generalized across Pydantic major versions",
    },
    "static_review_only": True,
}

__all__ = [
    "DEPENDENCY_LIFECYCLE_SECURITY_REVIEW_MAPPINGS",
    "REVIEW_LIMITS",
    "SOURCE_IDENTITIES",
    "SOURCE_VISIBLE_FUNCTIONS",
    "TEST_MODULES",
]
