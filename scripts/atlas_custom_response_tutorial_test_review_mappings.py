"""Source-reviewed mappings for the remaining custom-response tutorial tests.

Mappings point to FastAPI 0.157.0 and Starlette 1.6.0 source. The workflows
contain independent ASGI inputs only; generic response bodies and file/stream
transport are Starlette behavior.
"""

from __future__ import annotations

from typing import Any

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.157.0",
        "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic response-class, file, stream, and TestClient transport contract",
    },
    "pydantic": {
        "version": "2.13.5",
        "role": "pinned dependency; no Pydantic response-model behavior is exercised by these custom-response mappings",
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
    *,
    direct_workflow_case: dict[str, Any] | None = None,
) -> dict[str, Any]:
    link_notes = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} "
        f"(actions: {', '.join(link['action_ids'])}; "
        f"selectors: {', '.join(link['observation_selectors'])})"
        for link in links
    )
    mapping = {
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
                "pinned FastAPI 0.157.0 test function and asserted observations",
            ),
            *sources,
        ],
    }
    if direct_workflow_case is not None:
        mapping["workflow_case"] = direct_workflow_case
    return mapping


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
_HTTP_RESPONSE = ("http.status", "http.headers.ordered", "http.body.bytes")
_OPENAPI = ("http.status", "openapi.document")
_OPENAPI_ACTION = (
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
)


def _direct_case(
    workflow_id: str,
    recipe_path: str,
    case_id: str,
    action_ids: tuple[str, ...],
    selectors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _runtime_direct_case(case_id: str, selectors: tuple[str, ...]) -> dict[str, Any]:
    return _direct_case(
        "starlette-response-runtime-upstream",
        _RUNTIME_RECIPE,
        case_id,
        ("request",),
        selectors,
    )


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
        380,
        395,
        "FastAPI applies route and injected Response status values when constructing responses",
    ),
    _source(
        "fastapi/routing.py",
        398,
        423,
        "FastAPI selects the route's actual response class",
    ),
    _source(
        "fastapi/routing.py",
        751,
        791,
        "FastAPI preserves returned Response instances and constructs the configured response class for other values",
    ),
)
_ROUTE_RESPONSE_CLASS = (
    _source(
        "fastapi/routing.py",
        1016,
        1064,
        "FastAPI stores response_class on the route",
    ),
    _source(
        "fastapi/routing.py",
        1084,
        1088,
        "FastAPI normalizes and stores the declared route status code",
    ),
)
_OPENAPI_STATUS = (
    _source(
        "fastapi/openapi/utils.py",
        388,
        403,
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
    "tests/test_tutorial/test_custom_response/test_tutorial002_tutorial003_tutorial004.py": _module(
        "The three independent HTML response workflows reproduce the shared tutorial body and each response class's OpenAPI projection.",
        {
            "test_get_custom_response": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial002_tutorial003_tutorial004.py",
                38,
                41,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The source shares one exact HTML body across tutorials 002, 003, and 004; each independently authored workflow uses that body and /items/ route.",
                (
                    _link(
                        "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml",
                        "fastapi.custom-response.tutorial002.items-response",
                        ("items",),
                        _HTTP_RESPONSE,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/custom-response-tutorial003-upstream.yaml",
                        "fastapi.custom-response.tutorial003.items-response",
                        ("items",),
                        ("http.status", "http.body.bytes"),
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/custom-response-tutorial004-upstream.yaml",
                        "fastapi.custom-response.tutorial004.items-response",
                        ("items",),
                        _HTTP_RESPONSE,
                    ),
                ),
                "The test is parameterized over all three tutorials. The direct function link selects tutorial002; the other two independent inputs are also linked above. Status and body are asserted by the source; ordered headers are additional observations for tutorials 002 and 004. Response encoding is Starlette 1.6.0 behavior.",
                (
                    _source(
                        "docs_src/custom_response/tutorial002_py310.py",
                        1,
                        18,
                        "Tutorial002's explicit HTMLResponse route and source HTML body",
                    ),
                    _source(
                        "docs_src/custom_response/tutorial003_py310.py",
                        1,
                        19,
                        "Tutorial003's direct HTMLResponse return and source HTML body",
                    ),
                    _source(
                        "docs_src/custom_response/tutorial004_py310.py",
                        1,
                        23,
                        "Tutorial004's response helper, route class, and source HTML body",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_direct_case(
                    "custom-response-tutorial002-upstream",
                    "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml",
                    "fastapi.custom-response.tutorial002.items-response",
                    ("items",),
                    _HTTP_RESPONSE,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial002_tutorial003_tutorial004.py",
                44,
                71,
                ("openapi-docs", "response-serialization"),
                _OPENAPI,
                "The source compares the /items/ OpenAPI operation for all three tutorial variants; each independent workflow selects the matching OpenAPI paths and response content.",
                (
                    _link(
                        "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml",
                        "fastapi.custom-response.tutorial002.openapi",
                        ("openapi",),
                        _OPENAPI_ACTION,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/custom-response-tutorial003-upstream.yaml",
                        "fastapi.custom-response.tutorial003.openapi",
                        ("openapi",),
                        _OPENAPI_ACTION,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/custom-response-tutorial004-upstream.yaml",
                        "fastapi.custom-response.tutorial004.openapi",
                        ("openapi",),
                        _OPENAPI_ACTION,
                    ),
                ),
                "The function is parameterized across tutorials 002, 003, and 004; the direct link uses tutorial002's text/html projection while the other two projections remain independently mapped. Each action selects the OpenAPI identity, info, paths, operation response, and HTTP status; the test's response_content branch remains reflected in the three distinct inputs.",
                (
                    _source(
                        "docs_src/custom_response/tutorial002_py310.py",
                        1,
                        18,
                        "Tutorial002's declared HTMLResponse OpenAPI behavior",
                    ),
                    _source(
                        "docs_src/custom_response/tutorial003_py310.py",
                        1,
                        19,
                        "Tutorial003's default response class with a returned HTMLResponse",
                    ),
                    _source(
                        "docs_src/custom_response/tutorial004_py310.py",
                        1,
                        23,
                        "Tutorial004's route response class and returned response instance",
                    ),
                    *_ROUTE_RESPONSE_CLASS,
                    *_OPENAPI_STATUS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_direct_case(
                    "custom-response-tutorial002-upstream",
                    "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml",
                    "fastapi.custom-response.tutorial002.openapi",
                    ("openapi",),
                    _OPENAPI_ACTION,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial005.py": _module(
        "The independent PlainTextResponse inputs reproduce the tutorial's root route, body, response class, and selected OpenAPI operation.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial005.py",
                9,
                12,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The input reproduces the root GET route and exact Hello World body with the tutorial's explicit PlainTextResponse class.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-get",
                        ("request",),
                        _HTTP_RESPONSE,
                    ),
                ),
                "The source asserts status and decoded text; the input uses the same path, route name, response class, and body, and additionally compares ordered headers and raw bytes. Generic PlainTextResponse encoding belongs to Starlette 1.6.0.",
                (
                    _source(
                        "docs_src/custom_response/tutorial005_py310.py",
                        4,
                        9,
                        "Root route, explicit PlainTextResponse class, and exact response text",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-get",
                    _HTTP_RESPONSE,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial005.py",
                15,
                39,
                ("openapi-docs", "response-serialization"),
                _OPENAPI,
                "The independent OpenAPI input selects the same root GET operation, including its PlainTextResponse-derived text/plain schema.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-openapi-schema",
                        ("request",),
                        _OPENAPI_ACTION,
                    ),
                ),
                "The source compares a complete OpenAPI snapshot. The input selects only the matching root GET operation and HTTP status; top-level document fields and unrelated paths are not claimed.",
                (
                    _source(
                        "docs_src/custom_response/tutorial005_py310.py",
                        4,
                        9,
                        "Root route and explicit PlainTextResponse response-class declaration",
                    ),
                    *_ROUTE_RESPONSE_CLASS,
                    *_OPENAPI_STATUS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-openapi-schema",
                    _OPENAPI_ACTION,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial006.py": _module(
        "The independent redirect inputs reproduce the tutorial's /typer route and destination and select its corresponding OpenAPI operation.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial006.py",
                9,
                12,
                ("response-serialization",),
                _STATUS_HEADERS,
                "The input sends GET /typer and returns the tutorial's exact 307 Location target.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial006.test-get",
                        ("request",),
                        _HTTP_RESPONSE,
                    ),
                ),
                "The source disables TestClient redirect following and asserts status plus Location. The direct ASGI input compares the matching response and does not exercise a redirect-following client policy; the shared workload sets JSONResponse explicitly because tutorial010 requires an app-wide HTMLResponse default, so default-class inheritance is not claimed. Generic RedirectResponse encoding belongs to Starlette 1.6.0.",
                (
                    _source(
                        "docs_src/custom_response/tutorial006_py310.py",
                        4,
                        9,
                        "GET /typer route and exact RedirectResponse destination",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_REDIRECT_RESPONSE,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial006.test-get",
                    _HTTP_RESPONSE,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial006.py",
                15,
                37,
                ("openapi-docs", "response-serialization"),
                _OPENAPI,
                "The independent OpenAPI input selects the same /typer GET operation and generated operation identifier.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial006.test-openapi-schema",
                        ("request",),
                        _OPENAPI_ACTION,
                    ),
                ),
                "The source compares a complete OpenAPI snapshot. The input selects only the matching /typer GET operation and HTTP status; top-level document fields and unrelated paths are not claimed. The shared workload selects JSONResponse on this route to reproduce the source operation while retaining tutorial010's app-wide HTMLResponse default.",
                (
                    _source(
                        "docs_src/custom_response/tutorial006_py310.py",
                        4,
                        9,
                        "GET /typer route and RedirectResponse endpoint name",
                    ),
                    *_ROUTE_RESPONSE_CLASS,
                    *_OPENAPI_STATUS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial006.test-openapi-schema",
                    _OPENAPI_ACTION,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial006b.py": _module(
        "The independent redirect inputs reproduce the tutorial's /fastapi route, destination, RedirectResponse selection, and response documentation.",
        {
            "test_redirect_response_class": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial006b.py",
                9,
                12,
                ("response-serialization",),
                _STATUS_HEADERS,
                "The input sends GET /fastapi and observes the source's 307 status and exact FastAPI documentation URL in Location.",
                (
                    _link(
                        _BACKGROUND_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial006b.test-redirect-response-class",
                        ("redirect",),
                        _STATUS_HEADERS,
                    ),
                ),
                "The source disables TestClient redirect following and asserts status plus Location. The direct ASGI action observes those exact response selectors; client redirect-following policy and generic RedirectResponse encoding are Starlette 1.6.0 behavior.",
                (
                    _source(
                        "docs_src/custom_response/tutorial006b_py310.py",
                        1,
                        9,
                        "GET /fastapi with RedirectResponse class and exact return URL",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_REDIRECT_RESPONSE,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_direct_case(
                    "responses-background-upstream",
                    _BACKGROUND_RECIPE,
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial006b.test-redirect-response-class",
                    ("redirect",),
                    _STATUS_HEADERS,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial006b.py",
                15,
                32,
                ("openapi-docs", "response-serialization"),
                _OPENAPI,
                "The independent OpenAPI input selects the /fastapi GET response status and route operation documented by the tutorial.",
                (
                    _link(
                        _BACKGROUND_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial006b.test-openapi-schema",
                        ("openapi-schema",),
                        _OPENAPI_ACTION,
                    ),
                ),
                "The source compares the full OpenAPI snapshot. The input selects the /fastapi response object and HTTP status; top-level fields and route operation identifiers are not asserted by this link.",
                (
                    _source(
                        "docs_src/custom_response/tutorial006b_py310.py",
                        1,
                        9,
                        "GET /fastapi route, response class, and operation name",
                    ),
                    *_ROUTE_RESPONSE_CLASS,
                    *_OPENAPI_STATUS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_direct_case(
                    "responses-background-upstream",
                    _BACKGROUND_RECIPE,
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial006b.test-openapi-schema",
                    ("openapi-schema",),
                    _OPENAPI_ACTION,
                ),
            ),
        },
    ),
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
                direct_workflow_case=_direct_case(
                    "responses-background-upstream",
                    _BACKGROUND_RECIPE,
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial006c.test-redirect-status-code",
                    ("redirect",),
                    _STATUS_HEADERS,
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
                direct_workflow_case=_direct_case(
                    "custom-response-tutorial006c-openapi-review",
                    _OPENAPI_REVIEW_RECIPE,
                    "fastapi.custom-response.tutorial006c.openapi-response-status",
                    ("openapi-route-status",),
                    _OPENAPI_ACTION,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial007.py": _module(
        "The independent StreamingResponse case reproduces the documented ten-chunk fake-video body; its exact body bytes cover the upstream assertion, while chunk framing remains outside that assertion.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial007.py",
                8,
                11,
                ("response-serialization",),
                _BODY_BYTES,
                "The input stream yields the documented fake-video bytes ten times and compares the complete body.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial007.test-get",
                        ("request",),
                        _BODY_BYTES,
                    ),
                ),
                "The source asserts the exact aggregated body. The independent ASGI case uses the same ten payload chunks; the source does not assert chunk boundaries. StreamingResponse transport is owned by Starlette 1.6.0.",
                (
                    _source(
                        "docs_src/custom_response/tutorial007_py310.py",
                        8,
                        16,
                        "documented ten-chunk fake-video StreamingResponse",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_STREAMING_RESPONSE,
                    *_TESTCLIENT,
                ),
                direct_workflow_case={
                    "workflow_id": "starlette-response-runtime-upstream",
                    "recipe_path": _RUNTIME_RECIPE,
                    "case_id": "fastapi.test.test-tutorial-test-custom-response-test-tutorial007.test-get",
                    "action_ids": ["request"],
                    "observation_selectors": [
                        "http.status",
                        "http.headers.ordered",
                        "http.body.bytes",
                        "asgi.send.message_types",
                    ],
                },
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial008.py": _module(
        "The input reproduces the documented synchronous file iterator over the same fake-video bytes and compares the collected response content.",
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
                "The source compares only response.content. The input streams the same fake-video bytes from an independently created temporary file; dynamic file-path variation and ASGI chunk boundaries are not claimed. Generic StreamingResponse behavior belongs to Starlette 1.6.0.",
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
                direct_workflow_case={
                    "workflow_id": "starlette-response-runtime-upstream",
                    "recipe_path": _RUNTIME_RECIPE,
                    "case_id": "fastapi.test.test-tutorial-test-custom-response-test-tutorial008.test-get",
                    "action_ids": ["request"],
                    "observation_selectors": [
                        "http.status",
                        "http.headers.ordered",
                        "http.body.bytes",
                        "asgi.send.message_types",
                    ],
                },
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial009.py": _module(
        "The test writes fake-video bytes to a temporary file and checks the body from a directly returned FileResponse.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial009.py",
                12,
                18,
                ("response-serialization",),
                _BODY_BYTES,
                "The independent route returns FileResponse for an independently created .mp4 file containing the source's exact fake-video bytes.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial009.test-get",
                        ("request",),
                        _HTTP_RESPONSE,
                    ),
                ),
                "The source compares only response.content. The independent input uses an independently created temporary .mp4 with the exact Fake video bytes; the temporary filename and fixed metadata differ, and this source function does not assert status or file headers. FileResponse transfer is Starlette 1.6.0 behavior.",
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
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial009.test-get",
                    _HTTP_RESPONSE,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial009b.py": _module(
        "The input reproduces a route-selected FileResponse returning a path to an independently created temporary file with the source's fake-video bytes.",
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
                "The source compares only response.content. The input uses the same fake-video bytes and route-selected FileResponse class from an independently created temporary file; status, file headers, ranges, missing-file errors, and dynamic path variation are not asserted by this function. FastAPI class construction is distinct, while file transfer is Starlette 1.6.0 behavior.",
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
                direct_workflow_case={
                    "workflow_id": "starlette-response-runtime-upstream",
                    "recipe_path": _RUNTIME_RECIPE,
                    "case_id": "fastapi.test.test-tutorial-test-custom-response-test-tutorial009b.test-get",
                    "action_ids": ["request"],
                    "observation_selectors": [
                        "http.status",
                        "http.headers.ordered",
                        "http.body.bytes",
                    ],
                },
            ),
        },
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial010.py": _module(
        "The independent HTMLResponse inputs reproduce the tutorial's /items/ route, exact HTML body, default response class, and selected OpenAPI operation.",
        {
            "test_get_custom_response": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial010.py",
                20,
                23,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The input reproduces the exact /items/ body and the app-level HTMLResponse default documented by the tutorial.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial010.test-get-custom-response",
                        ("request",),
                        _HTTP_RESPONSE,
                    ),
                ),
                "The source asserts status and decoded text; the input uses the exact path and body, and additionally compares ordered headers and raw bytes. Generic HTMLResponse encoding belongs to Starlette 1.6.0.",
                (
                    _source(
                        "docs_src/custom_response/tutorial010_py310.py",
                        4,
                        9,
                        "App-level HTMLResponse default and exact /items/ response body",
                    ),
                    *_FASTAPI_RESPONSE_DISPATCH,
                    *_ROUTE_RESPONSE_CLASS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial010.test-get-custom-response",
                    _HTTP_RESPONSE,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_custom_response/test_tutorial010.py",
                26,
                50,
                ("openapi-docs", "response-serialization"),
                _OPENAPI,
                "The independent OpenAPI input selects the same /items/ GET operation, HTML response schema, and operation identifier.",
                (
                    _link(
                        _RUNTIME_RECIPE,
                        "fastapi.test.test-tutorial-test-custom-response-test-tutorial010.test-openapi-schema",
                        ("request",),
                        _OPENAPI_ACTION,
                    ),
                ),
                "The source compares a complete OpenAPI snapshot. The input selects only the matching /items/ GET operation and HTTP status; top-level document fields and unrelated paths are not claimed.",
                (
                    _source(
                        "docs_src/custom_response/tutorial010_py310.py",
                        4,
                        9,
                        "App-level HTMLResponse default and /items/ route",
                    ),
                    *_ROUTE_RESPONSE_CLASS,
                    *_OPENAPI_STATUS,
                    *_TESTCLIENT,
                ),
                direct_workflow_case=_runtime_direct_case(
                    "fastapi.test.test-tutorial-test-custom-response-test-tutorial010.test-openapi-schema",
                    _OPENAPI_ACTION,
                ),
            ),
        },
    ),
}
