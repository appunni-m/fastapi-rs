"""Source-reviewed mappings for the remaining custom-response tutorial tests.

Mappings point to FastAPI 0.141.1 and Starlette 1.6.0 source. The workflows
contain independent ASGI inputs only; generic response bodies and file/stream
transport are Starlette behavior.
"""

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
        "role": "sole generic response-class, file, stream, and TestClient transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned dependency; no Pydantic response-model behavior is exercised by these four modules",
    },
}

__all__ = ["CUSTOM_RESPONSE_TUTORIAL_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


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
    feature_ids: tuple[str, ...],
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
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "stimulus_notes": (
            "Independent input-only workflow reference: "
            + link_notes
            + ". Recipes contain no expected outputs or copied upstream test bodies."
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
            "Source-reviewed partial mapping to independent cases: "
            + "; ".join(
                f"{link['recipe_path']}::{link['case_id']} "
                f"(actions: {', '.join(link['action_ids'])}; "
                f"selectors: {', '.join(link['observation_selectors'])})"
                for link in links
            )
            + ". FastAPI owns response-class selection and direct-response dispatch. "
            "Response encoding, file metadata/transfer, streaming, redirects, and TestClient "
            "transport belong to the pinned Starlette contract."
        ),
        "functions": functions,
    }


_BACKGROUND_RECIPE = "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml"
_RUNTIME_RECIPE = "tests/fixtures/input-recipes/parity/starlette-response-runtime-upstream.yaml"
_OPENAPI_REVIEW_RECIPE = (
    "tests/fixtures/input-recipes/parity/custom-response-tutorial006c-openapi-review.yaml"
)
_STATUS_HEADERS = ("http.status", "http.headers.ordered")
_BODY_BYTES = ("http.body.bytes",)
_OPENAPI = ("http.status", "openapi.document")

_TESTCLIENT = (
    _source("fastapi/testclient.py", 1, 1, "FastAPI re-exports Starlette TestClient"),
    _source(
        "starlette/testclient.py",
        327,
        374,
        "Starlette 1.6.0 TestClient captures the ASGI response status, headers, and body",
    ),
    _source(
        "starlette/testclient.py",
        377,
        420,
        "Starlette 1.6.0 TestClient wraps the app in its ASGI HTTP transport",
    ),
)
_FASTAPI_RESPONSE_DISPATCH = (
    _source(
        "fastapi/routing.py",
        357,
        372,
        "FastAPI applies route and injected Response status values when constructing responses",
    ),
    _source(
        "fastapi/routing.py",
        375,
        400,
        "FastAPI selects the route's actual response class",
    ),
    _source(
        "fastapi/routing.py",
        711,
        750,
        "FastAPI preserves returned Response instances and constructs the configured response class for other values",
    ),
)
_ROUTE_RESPONSE_CLASS = (
    _source(
        "fastapi/routing.py",
        961,
        1009,
        "FastAPI stores response_class on the route",
    ),
    _source(
        "fastapi/routing.py",
        1029,
        1033,
        "FastAPI normalizes and stores the declared route status code",
    ),
)
_OPENAPI_STATUS = (
    _source(
        "fastapi/openapi/utils.py",
        403,
        418,
        "FastAPI documents the route's explicit status code or derives it from the response class",
    ),
)
_REDIRECT_RESPONSE = (
    _source(
        "starlette/responses.py",
        204,
        213,
        "Starlette RedirectResponse encodes Location and applies its status code",
    ),
)
_STREAMING_RESPONSE = (
    _source(
        "starlette/responses.py",
        222,
        255,
        "Starlette StreamingResponse adapts iterables and emits response body chunks",
    ),
    _source(
        "starlette/responses.py",
        257,
        276,
        "Starlette dispatches the streaming response over ASGI",
    ),
)
_FILE_RESPONSE = (
    _source(
        "starlette/responses.py",
        296,
        339,
        "Starlette FileResponse initializes path metadata and file headers",
    ),
    _source(
        "starlette/responses.py",
        341,
        400,
        "Starlette FileResponse validates and transfers the selected file over ASGI",
    ),
)


CUSTOM_RESPONSE_TUTORIAL_TEST_REVIEW_MAPPINGS = {
    "tests/test_tutorial/test_custom_response/test_tutorial006c.py": _module(
        "The module checks an explicit 302 RedirectResponse-class route and snapshots OpenAPI's documented response status.",
        {
            "test_redirect_status_code": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial006c.py",
                9,
                12,
                ("response-serialization",),
                _STATUS_HEADERS,
                "The declared RedirectResponse class receives the route's explicit 302 status and the returned URL as Location.",
                (
                    _link(
                        _BACKGROUND_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial006c.test-redirect-status-code",
                        ("redirect",),
                        _STATUS_HEADERS,
                    ),
                ),
                "The source asserts status and the Location value only. Ordered headers compare additional header bytes and order; the existing workload uses a relative destination instead of the tutorial URL. TestClient redirect following is disabled by the upstream function; the workflow drives ASGI directly.",
                (
                    _source(
                        "docs_src/custom_response/tutorial006c_py310.py",
                        7,
                        9,
                        "Declared RedirectResponse class, explicit status, and returned URL",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_REDIRECT_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial006c.py",
                15,
                32,
                ("openapi-docs", "response-serialization"),
                _OPENAPI,
                "The full source snapshot documents the route response under status 302; a separate case now selects that response pointer and observes the OpenAPI request status.",
                (
                    _link(
                        _OPENAPI_REVIEW_RECIPE,
                        "fastapi.custom-response.tutorial006c.openapi-response-status",
                        ("openapi-route-status",),
                        _OPENAPI,
                    ),
                ),
                "The source compares a complete OpenAPI snapshot. The independent workflow selects only the /pydantic GET 302 response object and HTTP status; other paths, top-level document fields, and exact snapshot values are not claimed.",
                (
                    _source(
                        "docs_src/custom_response/tutorial006c_py310.py",
                        7,
                        9,
                        "Declared redirect route and explicit 302 status",
                    ),
                    *_OPENAPI_STATUS,
                    *_ROUTE_RESPONSE_CLASS,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial008.py": _module(
        "The test creates a temporary file, points the documented synchronous file iterator at it, and compares the collected response content.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial008.py",
                12,
                18,
                ("response-serialization",),
                _BODY_BYTES,
                "The source sends bytes from a temporary file through a synchronous generator returned inside StreamingResponse.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial008.test-get",
                        ("request",),
                        _BODY_BYTES,
                    ),
                ),
                "The source compares only response.content. The existing case observes exact body bytes, but its generator reads the workload source file rather than a temporary file containing the source's fake-video bytes; arbitrary file-path/content variation and ASGI chunk boundaries are not claimed. Generic StreamingResponse behavior belongs to Starlette 1.6.0.",
                (
                    _source(
                        "docs_src/custom_response/tutorial008_py310.py",
                        4,
                        14,
                        "Synchronous file iterator returned through StreamingResponse",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_STREAMING_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial009.py": _module(
        "The test writes bytes to a temporary file, assigns its path to the documented module global, and checks a directly returned FileResponse body.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial009.py",
                12,
                18,
                ("response-serialization",),
                _BODY_BYTES,
                "The endpoint returns a FileResponse object for its configured file path; this is the direct Response-return path in FastAPI.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial009.test-get",
                        ("request",),
                        _BODY_BYTES,
                    ),
                ),
                "The source compares only response.content. The current case observes exact body bytes from a stable workload file, not the source's temporary file contents; status, file headers, ranges, missing-file errors, and path variation are not asserted by this function. FileResponse transfer is Starlette 1.6.0 behavior.",
                (
                    _source(
                        "docs_src/custom_response/tutorial009_py310.py",
                        4,
                        10,
                        "File path global and directly returned FileResponse",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_FILE_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial009b.py": _module(
        "The test writes bytes to a temporary file, assigns its path to the documented module global, and checks a FileResponse class selected by the route decorator.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial009b.py",
                12,
                18,
                ("response-serialization",),
                _BODY_BYTES,
                "The route declares FileResponse and returns a path string, so FastAPI constructs the configured response class from the endpoint value.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial009b.test-get",
                        ("request",),
                        _BODY_BYTES,
                    ),
                ),
                "The source compares only response.content. The current case observes exact body bytes from a stable workload file rather than the temporary file containing the source's fake-video bytes; status, file headers, ranges, missing-file errors, and path variation are not claimed. FastAPI class construction is distinct, while file transfer is Starlette 1.6.0 behavior.",
                (
                    _source(
                        "docs_src/custom_response/tutorial009b_py310.py",
                        4,
                        10,
                        "File path global, declared FileResponse class, and string path return",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_FILE_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
}
