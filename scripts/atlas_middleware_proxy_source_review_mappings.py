"""Source-backed function mappings for middleware, proxy, static-file, and settings tests.

These are review inputs, not parity results. FastAPI owns its application-level
control flow; Python facade modules are direct native re-exports only. The
Starlette 1.6.0 checkout is the sole generic ASGI and middleware oracle, and
Starlette-RS owns the corresponding generic target behavior. Pydantic Settings
owns direct environment loading in the one excluded test.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "behavior source oracle and development-only source; never a target runtime dependency or import",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI, middleware, TestClient, static-file, and response contract",
    },
    "starlette-rs": {
        "version": "0.1.0",
        "role": "Rust owner of the ported Starlette 1.6.0 generic contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model dependency; Pydantic model semantics are not claimed by these workflows",
    },
    "pydantic-settings": {
        "version": "2.14.2",
        "role": "locked optional settings dependency used by the source-only environment-loading test",
    },
}

OWNERSHIP_BOUNDARIES = {
    "fastapi": (
        "FastAPI owns application-level control flow: middleware registration and stack composition, "
        "the middleware decorator, root_path application policy, OpenAPI server projection, "
        "dependency override resolution, and FastAPI route wiring. Rust implements that behavior."
    ),
    "python_facade": (
        "The target Python runtime exposes only direct native re-exports and literal __all__; it has "
        "no helper, branch, fallback, or behavioral control flow."
    ),
    "starlette": (
        "Pinned Starlette 1.6.0 is the sole generic behavior oracle for ASGI transport, middleware "
        "execution, middleware primitives, mounting, static responses, and TestClient scope creation."
    ),
    "starlette_rs": "Starlette-RS owns the generic behavior port under the separate Starlette contract.",
    "pydantic": (
        "Pydantic model parsing/serialization is not independently asserted by the mapped request cases."
    ),
    "pydantic_settings": (
        "The direct environment-to-Settings assertion is Pydantic Settings behavior, outside FastAPI."
    ),
}

__all__ = ["MIDDLEWARE_PROXY_SOURCE_REVIEW_MAPPINGS", "OWNERSHIP_BOUNDARIES", "SOURCE_IDENTITIES"]


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
    action_ids: tuple[str, ...],
    selectors: tuple[str, ...],
    coverage: str,
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
        "coverage": coverage,
    }


def _function(
    test_path: str,
    function_name: str,
    feature_ids: tuple[str, ...],
    rationale: str,
    gate: str,
    workflows: tuple[dict[str, Any], ...],
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    workflow_notes = "; ".join(
        f"{row['recipe_path']}::{row['case_id']} ({', '.join(row['action_ids'])})"
        for row in workflows
    )
    selectors = sorted({selector for row in workflows for selector in row["observation_selectors"]})
    return {
        "mapping_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": f"Partial: {gate}",
        "workflow_cases": list(workflows),
        "stimulus_notes": (
            f"Independent input-only workflow link(s): {workflow_notes}. The recipes contain no "
            "expected output values or copied upstream test bodies."
        ),
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _exclusion(
    test_path: str,
    function_name: str,
    reason: str,
    owner: str,
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    return {
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": reason,
        "owner": owner,
        "workflow_cases": [],
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _module(rationale: str, functions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    workflows: dict[tuple[str, str], dict[str, Any]] = {}
    for function in functions.values():
        for row in function["supporting_sources"]:
            key = (row["path"], row["start_line"], row["end_line"], row["role"])
            sources.setdefault(key, row)
        for row in function["workflow_cases"]:
            workflows.setdefault((row["recipe_path"], row["case_id"]), row)
    return {
        "rationale": rationale,
        "ownership_boundaries": dict(OWNERSHIP_BOUNDARIES),
        "supporting_sources": list(sources.values()),
        "workflow_cases": list(workflows.values()),
        "module_observation_selectors": sorted(
            {
                selector
                for function in functions.values()
                for selector in function.get("observation_selectors", [])
            }
        ),
        "functions": functions,
    }


_ADVANCED_RECIPE = (
    "tests/fixtures/input-recipes/parity/middleware-proxy-advanced-source-review.yaml"
)
_PROXY_RECIPE = "tests/fixtures/input-recipes/parity/middleware-proxy-root-path-source-review.yaml"
_MIXED_RECIPE = (
    "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml"
)
_ADVANCED_WORKLOAD = "tests/fixtures/workloads/middleware_proxy_source_review.py"

_TESTCLIENT_REEXPORT = _source(
    "fastapi/testclient.py", 1, 1, "FastAPI directly re-exports Starlette TestClient"
)
_APP_MIDDLEWARE_STACK = _source(
    "fastapi/applications.py",
    1020,
    1045,
    "FastAPI owns construction of its application middleware stack and inserts its dependency exit-stack middleware",
)
_STARLETTE_MIDDLEWARE_REGISTRATION = _source(
    "starlette/applications.py",
    63,
    83,
    "Starlette 1.6.0 supplies the generic middleware stack order and wrapping behavior",
)
_STARLETTE_ADD_MIDDLEWARE = _source(
    "starlette/applications.py",
    104,
    107,
    "Starlette 1.6.0 stores newly registered middleware in its user middleware list",
)
_HTTPS_REEXPORT = _source(
    "fastapi/middleware/httpsredirect.py",
    1,
    3,
    "FastAPI middleware module directly re-exports the generic Starlette middleware",
)
_HTTPS_IMPLEMENTATION = _source(
    "starlette/middleware/httpsredirect.py",
    6,
    19,
    "Starlette 1.6.0 redirects insecure HTTP and WebSocket scopes to their secure schemes",
)
_TRUSTED_REEXPORT = _source(
    "fastapi/middleware/trustedhost.py",
    1,
    3,
    "FastAPI middleware module directly re-exports the generic Starlette middleware",
)
_TRUSTED_IMPLEMENTATION = _source(
    "starlette/middleware/trustedhost.py",
    12,
    60,
    "Starlette 1.6.0 validates the Host header against exact and wildcard allowed-host patterns",
)
_GZIP_REEXPORT = _source(
    "fastapi/middleware/gzip.py",
    1,
    1,
    "FastAPI middleware module directly re-exports the generic Starlette middleware",
)
_GZIP_IMPLEMENTATION = _source(
    "starlette/middleware/gzip.py",
    44,
    78,
    "Starlette 1.6.0 applies GZipMiddleware for HTTP requests that advertise gzip support",
)
_ROOT_PATH_CONFIG = _source(
    "fastapi/applications.py",
    881,
    885,
    "FastAPI stores root_path_in_servers and its configured server list on the application",
)
_ROOT_PATH_INIT = _source(
    "fastapi/applications.py",
    928,
    950,
    "FastAPI resolves deprecated openapi_prefix and stores the configured root_path",
)
_ROOT_PATH_SCOPE = _source(
    "fastapi/applications.py",
    1160,
    1163,
    "FastAPI applies its configured root_path to request scopes before dispatch",
)
_ROOT_PATH_OPENAPI = _source(
    "fastapi/applications.py",
    1105,
    1118,
    "FastAPI adds a request root_path server to OpenAPI when root_path_in_servers is enabled",
)
_OPENAPI_GENERATION = _source(
    "fastapi/applications.py",
    1070,
    1103,
    "FastAPI generates and caches the OpenAPI document from its route set and configured servers",
)
_STARLETTE_TESTCLIENT_ROOT = _source(
    "starlette/testclient.py",
    208,
    224,
    "Starlette 1.6.0 TestClient transport retains its configured root_path",
)
_STARLETTE_TESTCLIENT_SCOPE = _source(
    "starlette/testclient.py",
    277,
    291,
    "Starlette 1.6.0 TestClient writes root_path and HTTP request data into the ASGI scope",
)
_MIDDLEWARE_DECORATOR = _source(
    "fastapi/applications.py",
    4683,
    4727,
    "FastAPI's middleware decorator registers dispatch through Starlette BaseHTTPMiddleware",
)
_BASE_HTTP_MIDDLEWARE = _source(
    "starlette/middleware/base.py",
    96,
    120,
    "Starlette 1.6.0 implements the generic HTTP middleware request/response dispatch wrapper",
)
_STATIC_REEXPORT = _source(
    "fastapi/staticfiles.py",
    1,
    1,
    "FastAPI directly re-exports Starlette StaticFiles",
)
_STATIC_IMPLEMENTATION = _source(
    "starlette/staticfiles.py",
    39,
    56,
    "Starlette 1.6.0 validates and stores a static directory configuration",
)
_STATIC_DISPATCH = _source(
    "starlette/staticfiles.py",
    87,
    132,
    "Starlette 1.6.0 resolves mounted file paths and builds static-file responses or HTTP errors",
)
_STARLETTE_MOUNT = _source(
    "starlette/applications.py",
    98,
    99,
    "Starlette 1.6.0 delegates application mounting to its generic router",
)
_DEPENDENCY_OVERRIDES = _source(
    "fastapi/applications.py",
    967,
    983,
    "FastAPI initializes the application dependency_overrides mapping",
)
_DEPENDENCY_RESOLUTION = _source(
    "fastapi/dependencies/utils.py",
    600,
    643,
    "FastAPI resolves dependency callables and consults application overrides during request solving",
)
_SETTINGS_CONFIG = _source(
    "docs_src/settings/app02_py310/config.py",
    1,
    7,
    "The tutorial Settings class derives from pydantic_settings.BaseSettings and declares defaults",
)

_ADVANCED_DOCS = _source(
    "docs/en/docs/advanced/middleware.md",
    54,
    86,
    "FastAPI documentation demonstrates HTTPS redirect, trusted-host, and gzip middleware",
)
_PROXY_DOCS = _source(
    "docs/en/docs/advanced/behind-a-proxy.md",
    190,
    227,
    "FastAPI documentation explains reading request root_path and configuring it on the application",
)
_PROXY_OPENAPI_DOCS = _source(
    "docs/en/docs/advanced/behind-a-proxy.md",
    395,
    456,
    "FastAPI documentation explains root_path server insertion and disabling its automatic OpenAPI server",
)
_MIDDLEWARE_DOCS = _source(
    "docs/en/docs/tutorial/middleware.md",
    58,
    66,
    "FastAPI documentation demonstrates an X-Process-Time response header",
)
_STATIC_DOCS = _source(
    "docs/en/docs/tutorial/static-files.md",
    13,
    22,
    "FastAPI documentation instructs importing and mounting a StaticFiles instance",
)
_SETTINGS_ENV_DOCS = _source(
    "docs/en/docs/advanced/settings.md",
    25,
    70,
    "FastAPI documentation attributes environment parsing/defaults to Pydantic Settings",
)
_SETTINGS_OVERRIDE_DOCS = _source(
    "docs/en/docs/advanced/settings.md",
    143,
    184,
    "FastAPI documentation demonstrates Settings through a dependency and a test dependency override",
)
_PYDANTIC_SETTINGS_LOCK = _source(
    "uv.lock",
    3099,
    3108,
    "FastAPI's pinned development lock resolves pydantic-settings 2.14.2 and its pydantic dependency",
)
_PYDANTIC_LOCK = _source(
    "uv.lock",
    2852,
    2857,
    "FastAPI's pinned development lock resolves Pydantic 2.13.4",
)

_HTTP_STATUS = ("http.status",)
_HTTP_HEADERS = ("http.status", "http.headers.ordered")
_HTTP_BODY = ("http.status", "http.body.bytes")
_HTTP_OPENAPI = ("http.status", "openapi.document")


MIDDLEWARE_PROXY_SOURCE_REVIEW_MAPPINGS = {
    "tests/test_tutorial/test_advanced_middleware/test_tutorial001.py": _module(
        "The source checks the HTTPSRedirectMiddleware pass-through for HTTPS and its HTTP 307 redirect target. The case exercises FastAPI registration around Starlette's generic middleware and transport behavior.",
        {
            "test_middleware": _function(
                "tests/test_tutorial/test_advanced_middleware/test_tutorial001.py",
                "test_middleware",
                ("middleware-integrations",),
                "A secure request reaches the route; an insecure request receives a 307 response whose Location targets the same host over HTTPS.",
                "The independent input uses another request host/path fixture; its raw ASGI response headers are compared exactly, while the source checks only status and Location. Starlette's TestClient URL/scope construction is represented by the explicit ASGI scheme and host inputs, not by invoking TestClient.",
                (
                    _workflow(
                        _ADVANCED_RECIPE,
                        "fastapi.middleware-proxy.https-redirect",
                        ("secure-pass-through", "insecure-redirect"),
                        ("http.status", "http.headers.ordered"),
                        "secure pass-through status and HTTP-to-HTTPS redirect status/Location",
                    ),
                ),
                (
                    _ADVANCED_DOCS,
                    _APP_MIDDLEWARE_STACK,
                    _STARLETTE_MIDDLEWARE_REGISTRATION,
                    _STARLETTE_ADD_MIDDLEWARE,
                    _HTTPS_REEXPORT,
                    _HTTPS_IMPLEMENTATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_advanced_middleware/test_tutorial002.py": _module(
        "The source checks exact-host acceptance, wildcard-subdomain acceptance, and an invalid-host 400 status.",
        {
            "test_middleware": _function(
                "tests/test_tutorial/test_advanced_middleware/test_tutorial002.py",
                "test_middleware",
                ("middleware-integrations",),
                "Three independent Host header values cover exact allow-list acceptance, wildcard acceptance, and rejected-host status.",
                "The workload uses the independently declared example.net allow-list and corresponding requests; only status is selected because the source asserts no response body or headers. Host validation mechanics belong to Starlette 1.6.0.",
                (
                    _workflow(
                        _ADVANCED_RECIPE,
                        "fastapi.middleware-proxy.trusted-host",
                        ("accept-exact-host", "accept-subdomain-host", "reject-unlisted-host"),
                        _HTTP_STATUS,
                        "three HTTP statuses for exact, wildcard, and invalid Host inputs",
                    ),
                ),
                (
                    _ADVANCED_DOCS,
                    _APP_MIDDLEWARE_STACK,
                    _STARLETTE_MIDDLEWARE_REGISTRATION,
                    _STARLETTE_ADD_MIDDLEWARE,
                    _TRUSTED_REEXPORT,
                    _TRUSTED_IMPLEMENTATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_advanced_middleware/test_tutorial003.py": _module(
        "The source adds a large text route, requests it with Accept-Encoding: gzip, checks the decoded client text and compression headers, then checks the application root route.",
        {
            "test_middleware": _function(
                "tests/test_tutorial/test_advanced_middleware/test_tutorial003.py",
                "test_middleware",
                ("middleware-integrations",),
                "The input requests a generated large text response with gzip support advertised and then dispatches a second route without compression.",
                "Partial: the raw ASGI workflow observes status and exact response headers, but does not decode gzip into the upstream TestClient's response.text or assert Content-Length is less than the uncompressed size. The independent payload and threshold are stimulus inputs. Starlette owns compression; FastAPI owns app middleware and route wiring.",
                (
                    _workflow(
                        _ADVANCED_RECIPE,
                        "fastapi.middleware-proxy.gzip-response",
                        ("request-compressed-payload", "request-uncompressed-status"),
                        _HTTP_HEADERS,
                        "status and gzip response headers, followed by status on a second route",
                    ),
                ),
                (
                    _ADVANCED_DOCS,
                    _APP_MIDDLEWARE_STACK,
                    _STARLETTE_MIDDLEWARE_REGISTRATION,
                    _STARLETTE_ADD_MIDDLEWARE,
                    _GZIP_REEXPORT,
                    _GZIP_IMPLEMENTATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial001.py": _module(
        "The source gives Starlette TestClient a root_path and separately checks the path response and generated OpenAPI snapshot.",
        {
            "test_main": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial001.py",
                "test_main",
                ("root-path",),
                "An explicit incoming ASGI root_path is reflected by the request endpoint.",
                "The recipe constructs an ASGI scope directly, so FastAPI root_path propagation is covered but Starlette TestClient's conversion from base_url/client options into an ASGI scope is not re-executed. The workload uses independent response fields and compares raw JSON bytes, stricter than the source's decoded JSON comparison.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-client-root-path",
                        ("read-service-root-path",),
                        _HTTP_BODY,
                        "status and exact JSON body carrying the incoming scope root_path",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _ROOT_PATH_SCOPE,
                    _STARLETTE_TESTCLIENT_ROOT,
                    _STARLETTE_TESTCLIENT_SCOPE,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_openapi": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial001.py",
                "test_openapi",
                ("root-path", "openapi-docs"),
                "The generated document contains a root_path-derived server and the service operation.",
                "The source compares a complete snapshot; the recipe selects the server list and service operation pointers. The direct ASGI request uses the same root_path stimulus without TestClient.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-client-root-path",
                        ("read-service-openapi",),
                        _HTTP_OPENAPI,
                        "selected /servers and service-operation OpenAPI subtrees",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _PROXY_OPENAPI_DOCS,
                    _ROOT_PATH_OPENAPI,
                    _OPENAPI_GENERATION,
                    _STARLETTE_TESTCLIENT_ROOT,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial002.py": _module(
        "The source configures FastAPI.root_path and checks the endpoint-visible scope value plus the generated server entry.",
        {
            "test_main": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial002.py",
                "test_main",
                ("root-path",),
                "FastAPI's configured root_path is applied before the independent service route reads its scope.",
                "The recipe uses a distinct path/message and raw JSON-byte observation; Starlette TestClient defaults to an empty configured root_path in the source, while the workflow supplies the HTTP scope directly.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-app-root-path",
                        ("read-configured-root-path",),
                        _HTTP_BODY,
                        "status and JSON body with FastAPI's configured root_path",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _ROOT_PATH_CONFIG,
                    _ROOT_PATH_INIT,
                    _ROOT_PATH_SCOPE,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_openapi": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial002.py",
                "test_openapi",
                ("root-path", "openapi-docs"),
                "OpenAPI includes the configured root_path in servers and retains the independent service operation.",
                "The source compares a complete OpenAPI snapshot; the workflow selects only /servers and the service operation. FastAPI owns the dynamic root_path server projection; the request transport is represented by direct ASGI scope input.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-app-root-path",
                        ("read-configured-openapi",),
                        _HTTP_OPENAPI,
                        "selected /servers and service-operation OpenAPI subtrees",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _PROXY_OPENAPI_DOCS,
                    _ROOT_PATH_CONFIG,
                    _ROOT_PATH_OPENAPI,
                    _OPENAPI_GENERATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial003.py": _module(
        "The source combines configured root_path with two configured absolute servers and checks both the service scope and complete OpenAPI output.",
        {
            "test_main": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial003.py",
                "test_main",
                ("root-path",),
                "The configured root_path reaches the route's request scope while configured server entries remain application inputs.",
                "The input uses independent message, path, and server values; the route's JSON response body and status are observed. The example uses no Pydantic models.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-root-path-with-servers",
                        ("read-service-with-configured-servers",),
                        _HTTP_BODY,
                        "status and service response body under configured root_path",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _ROOT_PATH_CONFIG,
                    _ROOT_PATH_INIT,
                    _ROOT_PATH_SCOPE,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial003.py",
                "test_openapi_schema",
                ("root-path", "openapi-docs"),
                "The selected OpenAPI server list combines the request root_path entry with the two configured server objects.",
                "The source snapshots the complete OpenAPI document. The workflow selects /servers and the independent service operation only; its configured server URLs/descriptions are fresh inputs.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-root-path-with-servers",
                        ("read-configured-server-openapi",),
                        _HTTP_OPENAPI,
                        "selected /servers and service-operation OpenAPI subtrees",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _PROXY_OPENAPI_DOCS,
                    _ROOT_PATH_CONFIG,
                    _ROOT_PATH_OPENAPI,
                    _OPENAPI_GENERATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial004.py": _module(
        "The source sets root_path_in_servers=False while configuring two absolute servers; endpoint scope still exposes root_path and OpenAPI omits its automatic server.",
        {
            "test_main": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial004.py",
                "test_main",
                ("root-path",),
                "The configured root_path is still applied to the service request even when it is excluded from OpenAPI servers.",
                "The request body and status are observed with independent application values. The workflow separately checks the OpenAPI policy through the paired schema action.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-root-path-without-auto-server",
                        ("read-service-with-server-filter",),
                        _HTTP_BODY,
                        "status and service response body with configured root_path",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _ROOT_PATH_CONFIG,
                    _ROOT_PATH_INIT,
                    _ROOT_PATH_SCOPE,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_behind_a_proxy/test_tutorial004.py",
                "test_openapi_schema",
                ("root-path", "openapi-docs"),
                "The selected server list retains both configured URLs and does not add the automatic root_path server.",
                "The source snapshots the full OpenAPI document. The recipe observes /servers and the service operation; FastAPI owns the root_path_in_servers branch, while OpenAPI generation remains FastAPI behavior.",
                (
                    _workflow(
                        _PROXY_RECIPE,
                        "fastapi.middleware-proxy.proxy-root-path-without-auto-server",
                        ("read-filtered-server-openapi",),
                        _HTTP_OPENAPI,
                        "selected /servers and service-operation OpenAPI subtrees",
                    ),
                ),
                (
                    _PROXY_DOCS,
                    _PROXY_OPENAPI_DOCS,
                    _ROOT_PATH_CONFIG,
                    _ROOT_PATH_OPENAPI,
                    _OPENAPI_GENERATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_middleware/test_tutorial001.py": _module(
        "Both source functions issue GET /openapi.json: one checks the response-time header and one checks the complete empty-path OpenAPI snapshot.",
        {
            "test_response_headers": _function(
                "tests/test_tutorial/test_middleware/test_tutorial001.py",
                "test_response_headers",
                ("middleware-integrations",),
                "The independent HTTP middleware adds the documented X-Process-Time header to an OpenAPI response.",
                "The source checks header presence only. The independent workload uses a deterministic header value so full response-header comparison is stable; timing measurement and its numeric value are not claimed.",
                (
                    _workflow(
                        _MIXED_RECIPE,
                        "fastapi.middleware-proxy.decorator-middleware",
                        ("request-openapi-through-middleware",),
                        _HTTP_HEADERS,
                        "status and response headers including X-Process-Time",
                    ),
                ),
                (
                    _MIDDLEWARE_DOCS,
                    _MIDDLEWARE_DECORATOR,
                    _APP_MIDDLEWARE_STACK,
                    _BASE_HTTP_MIDDLEWARE,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_middleware/test_tutorial001.py",
                "test_openapi_schema",
                ("middleware-integrations", "openapi-docs"),
                "The middleware-wrapped application emits an empty-path OpenAPI document with the pinned default title and version.",
                "The source compares the complete document. The independent recipe selects the OpenAPI version, title, version string, and paths object only.",
                (
                    _workflow(
                        _MIXED_RECIPE,
                        "fastapi.middleware-proxy.decorator-middleware",
                        ("request-openapi-through-middleware",),
                        _HTTP_OPENAPI,
                        "selected empty-path OpenAPI metadata pointers",
                    ),
                ),
                (
                    _MIDDLEWARE_DOCS,
                    _MIDDLEWARE_DECORATOR,
                    _APP_MIDDLEWARE_STACK,
                    _OPENAPI_GENERATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_static_files/test_tutorial001.py": _module(
        "The source creates a temporary static directory and file, checks the mounted file response and a missing-file 404, then checks an empty-path OpenAPI snapshot.",
        {
            "test_static_files": _function(
                "tests/test_tutorial/test_static_files/test_tutorial001.py",
                "test_static_files",
                ("static-files", "app-routing"),
                "The independent mount serves an input-created file and exposes its response status and bytes.",
                "The recipe uses a separate temporary directory, URL prefix, filename, and file body. It selects raw body bytes, which is stricter than the source's decoded response.text assertion; file metadata headers are not selected.",
                (
                    _workflow(
                        _MIXED_RECIPE,
                        "fastapi.middleware-proxy.static-files",
                        ("request-mounted-file",),
                        _HTTP_BODY,
                        "status and raw bytes from an input-created mounted file",
                    ),
                ),
                (
                    _STATIC_DOCS,
                    _STATIC_REEXPORT,
                    _STARLETTE_MOUNT,
                    _STATIC_IMPLEMENTATION,
                    _STATIC_DISPATCH,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_static_files_not_found": _function(
                "tests/test_tutorial/test_static_files/test_tutorial001.py",
                "test_static_files_not_found",
                ("static-files", "app-routing"),
                "A missing file under the independent static mount produces the source-asserted 404 status.",
                "The source asserts status only; the recipe selects status only and uses a separately named missing path. Starlette owns static lookup and generic HTTP error dispatch.",
                (
                    _workflow(
                        _MIXED_RECIPE,
                        "fastapi.middleware-proxy.static-files",
                        ("request-missing-mounted-file",),
                        _HTTP_STATUS,
                        "status for a missing mounted file",
                    ),
                ),
                (
                    _STATIC_DOCS,
                    _STATIC_REEXPORT,
                    _STARLETTE_MOUNT,
                    _STATIC_IMPLEMENTATION,
                    _STATIC_DISPATCH,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_static_files/test_tutorial001.py",
                "test_openapi_schema",
                ("static-files", "openapi-docs"),
                "The OpenAPI document has no path-operation entries for the mounted static application.",
                "The source compares the complete OpenAPI document. The recipe selects its version/title metadata and paths object; static-file response details belong to the neighboring HTTP actions.",
                (
                    _workflow(
                        _MIXED_RECIPE,
                        "fastapi.middleware-proxy.static-files",
                        ("request-static-openapi",),
                        _HTTP_OPENAPI,
                        "selected empty-path OpenAPI metadata pointers",
                    ),
                ),
                (
                    _STATIC_DOCS,
                    _STATIC_REEXPORT,
                    _STARLETTE_MOUNT,
                    _OPENAPI_GENERATION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_settings/test_app02.py": _module(
        "The module exercises direct Pydantic Settings environment loading and delegates a second assertion to a documentation test app with a FastAPI dependency override.",
        {
            "test_settings": _exclusion(
                "tests/test_tutorial/test_settings/test_app02.py",
                "test_settings",
                "The function sets ADMIN_EMAIL and calls the tutorial's get_settings() directly, then reads BaseSettings fields. It does not construct FastAPI or issue an HTTP/ASGI request; environment parsing, defaults, and cached Settings construction belong to pydantic-settings, outside the FastAPI contract.",
                "pydantic-settings 2.14.2 optional settings dependency",
                (
                    _SETTINGS_ENV_DOCS,
                    _SETTINGS_CONFIG,
                    _source(
                        "docs_src/settings/app02_py310/main.py",
                        10,
                        13,
                        "The tutorial get_settings callable constructs and caches the Pydantic Settings object",
                    ),
                    _PYDANTIC_SETTINGS_LOCK,
                    _PYDANTIC_LOCK,
                ),
            ),
            "test_override_settings": _function(
                "tests/test_tutorial/test_settings/test_app02.py",
                "test_override_settings",
                ("dependency-overrides",),
                "The delegated documentation test app overrides a dependency and checks the resulting HTTP response; the independent workflow isolates FastAPI override resolution on a renamed route and data shape.",
                "The workflow exercises FastAPI dependency override control flow and selected response bytes. It uses ordinary dictionary values, so it does not claim Pydantic BaseSettings/environment-source behavior or model validation/serialization. The source's nested TestClient request is represented as an explicit ASGI HTTP action.",
                (
                    _workflow(
                        _MIXED_RECIPE,
                        "fastapi.middleware-proxy.settings-dependency-override",
                        ("request-overridden-profile",),
                        _HTTP_BODY,
                        "status and serialized output after a FastAPI dependency override",
                    ),
                ),
                (
                    _SETTINGS_OVERRIDE_DOCS,
                    _SETTINGS_CONFIG,
                    _source(
                        "docs_src/settings/app02_py310/main.py",
                        10,
                        20,
                        "The tutorial resolves Settings through Depends in its /info route",
                    ),
                    _source(
                        "docs_src/settings/app02_py310/test_main.py",
                        9,
                        23,
                        "The documentation test app registers a dependency override and asserts its HTTP JSON output",
                    ),
                    _PYDANTIC_SETTINGS_LOCK,
                    _PYDANTIC_LOCK,
                    _DEPENDENCY_OVERRIDES,
                    _DEPENDENCY_RESOLUTION,
                    _TESTCLIENT_REEXPORT,
                ),
            ),
        },
    ),
}
