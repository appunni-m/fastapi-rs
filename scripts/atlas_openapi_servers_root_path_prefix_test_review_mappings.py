"""Function-level review for OpenAPI servers, root paths, and deprecated prefix tests."""

from __future__ import annotations

from typing import Any

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole TestClient and generic ASGI transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned dependency; these functions do not exercise Pydantic model behavior",
    },
}

__all__ = ["OPENAPI_SERVERS_ROOT_PATH_PREFIX_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


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
    start: int,
    end: int,
    features: tuple[str, ...],
    selectors: tuple[str, ...],
    rationale: str,
    links: tuple[dict[str, Any], ...],
    gate: str,
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    link_notes = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} "
        f"(actions: {', '.join(link['action_ids'])}; "
        f"selectors: {', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "feature_ids": list(features),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "stimulus_notes": (
            "Independent input-only workflow reference: "
            + link_notes
            + ". Recipes contain no expected output snapshots or copied upstream test bodies."
        ),
        "workflow_cases": list(links),
        "supporting_sources": [
            _source(
                test_path,
                start,
                end,
                "pinned FastAPI 0.141.1 test function and asserted observations",
            ),
            *sources,
        ],
    }


def _module(rationale: str, functions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    workflow_links: dict[tuple[str, str], dict[str, Any]] = {}
    evidence: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in functions.values():
        for link in row["workflow_cases"]:
            workflow_links.setdefault((link["recipe_path"], link["case_id"]), link)
        for source in row["supporting_sources"]:
            key = (source["path"], source["start_line"], source["end_line"], source["role"])
            evidence.setdefault(key, source)
    links = list(workflow_links.values())
    return {
        "rationale": rationale,
        "supporting_sources": list(evidence.values()),
        "workflow_cases": links,
        "module_observation_selectors": sorted(
            {selector for row in functions.values() for selector in row["observation_selectors"]}
        ),
        "stimulus_notes": (
            "Source-reviewed partial mappings to independent request sequences: "
            + "; ".join(f"{link['recipe_path']}::{link['case_id']}" for link in links)
            + ". FastAPI owns the OpenAPI cache and root-path server projection; Starlette 1.6.0 "
            "owns TestClient construction of the ASGI root_path scope."
        ),
        "functions": functions,
    }


_OPENAPI_DOCS_RECIPE = "tests/fixtures/input-recipes/parity/openapi-docs.yaml"
_OPENAPI_OPERATIONS_RECIPE = "tests/fixtures/input-recipes/parity/openapi-operations.yaml"
_SERVERS_ROUTE_RECIPE = "tests/fixtures/input-recipes/parity/openapi-servers-route-review.yaml"
_ROOT_SEQUENCE_RECIPE = (
    "tests/fixtures/input-recipes/parity/openapi-cache-root-path-clean-review.yaml"
)
_SERVERS_REFERENCE_RECIPE = (
    "tests/fixtures/input-recipes/parity/openapi-configured-servers-reference-review.yaml"
)
_PREFIX_REVIEW_RECIPE = (
    "tests/fixtures/input-recipes/parity/deprecated-openapi-prefix-tutorial-review.yaml"
)
_STATUS = ("http.status",)
_OPENAPI = ("http.status", "openapi.document")
_ROOT_DOCUMENT = ("openapi.document",)
_BODY = ("http.status", "http.body.bytes")

_OPENAPI_SERVER_SOURCES = (
    _source(
        "fastapi/applications.py",
        881,
        890,
        "FastAPI stores OpenAPI settings and the configured servers list",
    ),
    _source(
        "fastapi/applications.py",
        1070,
        1103,
        "FastAPI caches the generated schema and passes configured servers to get_openapi",
    ),
    _source(
        "fastapi/openapi/utils.py",
        595,
        615,
        "OpenAPI generation adds the configured servers to the output document",
    ),
    _source("fastapi/testclient.py", 1, 1, "FastAPI re-exports Starlette TestClient"),
)

_ROOT_PATH_SOURCES = (
    _source(
        "fastapi/applications.py",
        1070,
        1103,
        "FastAPI caches OpenAPI generation on the application instance",
    ),
    _source(
        "fastapi/applications.py",
        1105,
        1120,
        "FastAPI reads each request root_path and constructs a response-specific servers list",
    ),
    _source(
        "fastapi/applications.py",
        1160,
        1163,
        "FastAPI applies its configured root_path to incoming ASGI scopes",
    ),
    _source(
        "starlette/testclient.py",
        207,
        224,
        "Starlette TestClient transport stores its configured root_path",
    ),
    _source(
        "starlette/testclient.py",
        277,
        291,
        "Starlette TestClient places root_path into the HTTP ASGI scope",
    ),
)

_CONFIGURED_SERVER_COPY_SOURCES = (
    _source(
        "fastapi/applications.py",
        881,
        890,
        "FastAPI stores the supplied server list on the application",
    ),
    _source(
        "fastapi/applications.py",
        1105,
        1118,
        "FastAPI shallow-copies the OpenAPI document before adding a request root_path server",
    ),
    _source(
        "fastapi/openapi/utils.py",
        595,
        615,
        "OpenAPI generation incorporates configured server entries",
    ),
)

_DEPRECATED_PREFIX_SOURCES = (
    _source(
        "fastapi/applications.py",
        625,
        639,
        "The FastAPI constructor declares openapi_prefix and marks it deprecated in favor of root_path",
    ),
    _source(
        "fastapi/applications.py",
        929,
        949,
        "FastAPI warns for openapi_prefix and falls back to it when assigning root_path",
    ),
    _source(
        "fastapi/applications.py",
        1105,
        1118,
        "The OpenAPI route adds the effective request root_path to generated servers",
    ),
    _source(
        "fastapi/applications.py",
        1160,
        1163,
        "FastAPI writes its effective root_path into the ASGI request scope",
    ),
)


OPENAPI_SERVERS_ROOT_PATH_PREFIX_TEST_REVIEW_MAPPINGS = {
    "tests/test_openapi_servers.py": _module(
        "The module checks a regular route response and a complete OpenAPI snapshot with three configured server entries.",
        {
            "test_app": _function(
                "tests/test_openapi_servers.py",
                25,
                27,
                ("app-routing",),
                _STATUS,
                "The configured-server app's ordinary route returns status 200.",
                (
                    _link(
                        _SERVERS_ROUTE_RECIPE,
                        "fastapi.openapi.openapi-servers.route-status-review",
                        ("route-status",),
                        _STATUS,
                    ),
                ),
                "The independent app also has a configured servers list, but requests /health rather than /foo. The source function asserts only status 200, and the workflow selects only that same observable status.",
                (
                    _source(
                        "tests/test_openapi_servers.py",
                        5,
                        19,
                        "The source app configures servers and registers GET /foo",
                    ),
                    *_OPENAPI_SERVER_SOURCES,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_openapi_servers.py",
                30,
                60,
                ("openapi-docs", "app-routing"),
                _OPENAPI,
                "The source snapshots the full OpenAPI document, including its configured servers and /foo operation.",
                (
                    _link(
                        _OPENAPI_DOCS_RECIPE,
                        "fastapi.openapi.openapi-servers.openapi-schema",
                        ("openapi",),
                        _OPENAPI,
                    ),
                ),
                "The existing input selects /servers and /paths, but the workload has a single different server and /health route. It does not assert the source snapshot's relative URL, three-entry ordering, descriptions, info object, or exact /foo operation; only the selected pointers and HTTP status are represented.",
                (
                    _source(
                        "tests/test_openapi_servers.py",
                        5,
                        19,
                        "The source app configures three servers and registers GET /foo",
                    ),
                    *_OPENAPI_SERVER_SOURCES,
                ),
            ),
        },
    ),
    "tests/test_openapi_cache_root_path.py": _module(
        "The module checks that dynamic root_path servers appear for the active request but do not leak through cached OpenAPI state or mutate caller configuration.",
        {
            "test_root_path_does_not_persist_across_requests": _function(
                "tests/test_openapi_cache_root_path.py",
                5,
                23,
                ("openapi-docs",),
                _ROOT_DOCUMENT,
                "A request carrying one root_path contributes that server, while a later request without root_path must not retain it.",
                (
                    _link(
                        _OPENAPI_DOCS_RECIPE,
                        "fastapi.openapi.openapi-cache-root-path.root-path-does-not-persist-across-requests",
                        ("request-1", "request-2"),
                        _ROOT_DOCUMENT,
                    ),
                ),
                "The existing two-request sequence has the same prefix-then-clean shape, with /tenant-one instead of /evil-api and a configured base server in its workload. It selects the complete /servers list rather than the source's membership predicates. The ASGI recipe supplies root_path directly and does not exercise TestClient construction.",
                _ROOT_PATH_SOURCES,
            ),
            "test_multiple_different_root_paths_do_not_accumulate": _function(
                "tests/test_openapi_cache_root_path.py",
                26,
                45,
                ("openapi-docs",),
                _ROOT_DOCUMENT,
                "Three distinct root_path requests are followed by a clean request whose OpenAPI result must not retain any earlier prefix.",
                (
                    _link(
                        _ROOT_SEQUENCE_RECIPE,
                        "fastapi.openapi.openapi-cache-root-path.several-prefixes-then-clean-review",
                        (
                            "request-prefix-a",
                            "request-prefix-b",
                            "request-prefix-c",
                            "request-clean-path",
                        ),
                        _ROOT_DOCUMENT,
                    ),
                ),
                "The new sequence preserves one app instance across three distinct prefixes and a final empty root_path. It selects the complete OpenAPI document on every request, a stronger observation than the source's final absence checks; prefixes and the root route data are independently authored. The workflow drives ASGI scopes directly rather than constructing Starlette TestClient objects.",
                _ROOT_PATH_SOURCES,
            ),
            "test_legitimate_root_path_still_appears": _function(
                "tests/test_openapi_cache_root_path.py",
                48,
                59,
                ("openapi-docs",),
                _ROOT_DOCUMENT,
                "A request with a configured client root_path includes that root_path in the OpenAPI servers list.",
                (
                    _link(
                        _OPENAPI_DOCS_RECIPE,
                        "fastapi.openapi.openapi-cache-root-path.legitimate-root-path-still-appears",
                        ("openapi",),
                        _ROOT_DOCUMENT,
                    ),
                ),
                "The existing case uses /tenant-legitimate instead of /api/v1 and a workload with a configured base server. It selects the whole /servers list rather than checking membership of one URL; the TestClient wrapper is replaced by an equivalent direct ASGI root_path input.",
                _ROOT_PATH_SOURCES,
            ),
            "test_configured_servers_not_mutated": _function(
                "tests/test_openapi_cache_root_path.py",
                62,
                75,
                ("openapi-docs",),
                ("http.body.bytes",),
                "After requesting OpenAPI under a root_path, the original caller-supplied servers list remains equal to its initial contents.",
                (
                    _link(
                        _SERVERS_REFERENCE_RECIPE,
                        "fastapi.openapi.openapi-cache-root-path.caller-servers-remain-unchanged-review",
                        ("openapi-with-root-path", "inspect-original-server-list"),
                        ("http.body.bytes",),
                    ),
                ),
                "The workload exposes its caller-owned server list through an independent diagnostic route after the OpenAPI request, so the workflow observes value mutation through response bytes. Its configured URL and prefix differ from the source. The route does not test Python object identity, and exact bytes are stricter than the source list equality assertion.",
                (
                    _source(
                        "tests/test_openapi_cache_root_path.py",
                        62,
                        75,
                        "The test passes a caller-owned servers list, requests OpenAPI under root_path, then compares the original list",
                    ),
                    *_CONFIGURED_SERVER_COPY_SOURCES,
                    *_ROOT_PATH_SOURCES,
                ),
            ),
        },
    ),
    "tests/test_deprecated_openapi_prefix.py": _module(
        "The module checks the deprecated openapi_prefix alias in request scope and in generated OpenAPI servers.",
        {
            "test_main": _function(
                "tests/test_deprecated_openapi_prefix.py",
                16,
                19,
                ("app-routing", "openapi-docs"),
                _BODY,
                "The deprecated constructor prefix becomes request.scope.root_path and appears in the ordinary route response.",
                (
                    _link(
                        _PREFIX_REVIEW_RECIPE,
                        "fastapi.openapi.deprecated-openapi-prefix.route-and-openapi-review",
                        ("request-prefix-aware-route",),
                        _BODY,
                    ),
                ),
                "The workflow uses the deprecated constructor argument and observes the resulting root_path through an independently authored route. Its prefix, path, and body fields differ from the source; exact body bytes are stricter than response.json() equality. The source's HTTP status assertion is also observed. FastAPI's deprecation warning is not asserted by the test function and is not captured by this ASGI workflow.",
                (
                    _source(
                        "tests/test_deprecated_openapi_prefix.py",
                        5,
                        10,
                        "The source configures openapi_prefix and returns request.scope.root_path",
                    ),
                    *_DEPRECATED_PREFIX_SOURCES,
                ),
            ),
            "test_openapi": _function(
                "tests/test_deprecated_openapi_prefix.py",
                22,
                45,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the generated OpenAPI paths and server URL after configuring openapi_prefix.",
                (
                    _link(
                        _PREFIX_REVIEW_RECIPE,
                        "fastapi.openapi.deprecated-openapi-prefix.route-and-openapi-review",
                        ("request-openapi",),
                        _OPENAPI,
                    ),
                    _link(
                        _OPENAPI_OPERATIONS_RECIPE,
                        "fastapi.openapi.deprecated-openapi-prefix.openapi",
                        ("openapi",),
                        _OPENAPI,
                    ),
                ),
                "The new case selects /servers and /paths for a route on an app configured directly with openapi_prefix; the existing case independently covers the same deprecated argument with different prefix/path values. Neither compares the complete source snapshot, including info, operationId, response description, or exact route; the selected JSON pointers and status remain the claimed observations. The constructor's deprecation warning is neither asserted by the test nor captured by the workflow.",
                (
                    _source(
                        "tests/test_deprecated_openapi_prefix.py",
                        5,
                        10,
                        "The source configures openapi_prefix and registers GET /app",
                    ),
                    *_DEPRECATED_PREFIX_SOURCES,
                ),
            ),
        },
    ),
}
