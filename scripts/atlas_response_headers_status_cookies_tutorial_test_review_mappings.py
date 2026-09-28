"""Function-level source review for response header, status, and cookie tutorials."""

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
        "role": "sole generic response and TestClient/ASGI transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned dependency; the selected response tutorials do not exercise model behavior",
    },
}

__all__ = ["RESPONSE_HEADERS_STATUS_COOKIES_TUTORIAL_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


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
        "feature_ids": ["app-routing", "response-serialization"],
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
            "Source-reviewed partial mapping to independent ASGI cases: "
            + "; ".join(f"{link['recipe_path']}::{link['case_id']}" for link in links)
            + ". FastAPI routes and propagates temporary Response values; generic response "
            "rendering, Set-Cookie construction, and TestClient transport are governed by "
            "the pinned Starlette 1.6.0 contract."
        ),
        "functions": functions,
    }


_RESPONSE_SURFACE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_RESPONSES_BACKGROUND = "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml"
_STATUS_TUTORIAL = "tests/fixtures/input-recipes/parity/response-change-status-tutorial-review.yaml"
_HTTP_SELECTORS = ("http.status", "http.headers.ordered", "http.body.bytes")
_STATUS_BODY_SELECTORS = ("http.status", "http.body.bytes")

_TESTCLIENT = (
    _source("fastapi/testclient.py", 1, 1, "FastAPI re-exports Starlette TestClient"),
    _source(
        "starlette/testclient.py",
        327,
        374,
        "Starlette 1.6.0 TestClient captures ASGI response status, headers, and body",
    ),
    _source(
        "starlette/testclient.py",
        377,
        420,
        "Starlette 1.6.0 TestClient wraps its transport with the HTTP client",
    ),
)
_FASTAPI_INJECTED_RESPONSE = (
    _source(
        "fastapi/dependencies/utils.py",
        611,
        615,
        "FastAPI creates the temporary Response injected into path operations",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        719,
        730,
        "FastAPI injects and returns the temporary Response in SolvedDependency",
    ),
    _source(
        "fastapi/routing.py",
        357,
        372,
        "FastAPI selects the temporary Response status override when building response arguments",
    ),
    _source(
        "fastapi/routing.py",
        716,
        750,
        "FastAPI constructs the route response and copies injected raw headers to it",
    ),
)
_STARLETTE_RESPONSE = (
    _source(
        "starlette/responses.py",
        33,
        87,
        "Starlette Response applies status/content headers and exposes mutable headers",
    ),
    _source(
        "starlette/responses.py",
        89,
        132,
        "Starlette Response serializes Set-Cookie into a raw response header",
    ),
)


RESPONSE_HEADERS_STATUS_COOKIES_TUTORIAL_REVIEW_MAPPINGS = {
    "tests/test_tutorial/test_response_headers/test_tutorial001.py": _module(
        "The test checks a directly returned JSONResponse, its decoded JSON body, and two named response headers.",
        {
            "test_path_operation": _function(
                "tests/test_tutorial/test_response_headers/test_tutorial001.py",
                8,
                13,
                _HTTP_SELECTORS,
                "A route returns an explicit JSONResponse containing content and custom headers.",
                (
                    _link(
                        _RESPONSE_SURFACE,
                        "fastapi.response.direct-json",
                        ("dispatch",),
                        _HTTP_SELECTORS,
                    ),
                ),
                "The existing case is a direct JSONResponse with an explicit header, but its route, header, body, and status differ from the tutorial. It observes the complete ordered header list and exact body bytes, which are stricter than the source's two named-header and parsed-JSON assertions; there is no semantic JSON or selected-header-value selector. The FastAPI direct-Response branch is sampled, not the exact tutorial output.",
                (
                    _source(
                        "docs_src/response_headers/tutorial001_py310.py",
                        7,
                        11,
                        "Documented route constructs a JSONResponse with explicit content and headers",
                    ),
                    _source(
                        "fastapi/routing.py",
                        711,
                        714,
                        "FastAPI preserves an endpoint-returned Response instance",
                    ),
                    _source(
                        "starlette/responses.py",
                        33,
                        81,
                        "Starlette Response applies the status, body, and supplied header mapping",
                    ),
                    _source(
                        "starlette/responses.py",
                        181,
                        201,
                        "Starlette JSONResponse renders JSON and accepts explicit status and headers",
                    ),
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_headers/test_tutorial002.py": _module(
        "The test mutates the injected temporary Response header and returns a JSON object.",
        {
            "test_path_operation": _function(
                "tests/test_tutorial/test_response_headers/test_tutorial002.py",
                8,
                12,
                _HTTP_SELECTORS,
                "FastAPI copies headers set on an injected Response to the final response while serializing the returned object.",
                (
                    _link(
                        _RESPONSES_BACKGROUND,
                        "fastapi.test.test-tutorial-test-response-headers-test-tutorial002.test-path-operation",
                        ("response-header",),
                        _HTTP_SELECTORS,
                    ),
                ),
                "The existing input uses the same /headers-and-object/ route shape and injected-header mechanism, but sets X-Probe and returns a different JSON object. The selectors compare the full ordered raw headers and exact body bytes, stricter than the source's one named-header and parsed-JSON checks. No selected-header or semantic-JSON selector exists.",
                (
                    _source(
                        "docs_src/response_headers/tutorial002_py310.py",
                        6,
                        9,
                        "Documented route mutates the injected Response and returns JSON data",
                    ),
                    *_FASTAPI_INJECTED_RESPONSE,
                    *_STARLETTE_RESPONSE[:1],
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_change_status_code/test_tutorial001.py": _module(
        "The test sends sequential updates for one existing and one missing key and checks their effective status and decoded JSON string.",
        {
            "test_path_operation": _function(
                "tests/test_tutorial/test_response_change_status_code/test_tutorial001.py",
                8,
                15,
                _STATUS_BODY_SELECTORS,
                "The route defaults to status 200 and mutates the injected Response to 201 only when the requested record does not exist.",
                (
                    _link(
                        _STATUS_TUTORIAL,
                        "fastapi.response.change-status-code.tutorial-existing-and-created",
                        ("update-existing-record", "create-new-record"),
                        _STATUS_BODY_SELECTORS,
                    ),
                ),
                "The new input sends two requests to the same independently authored stateful route, covering default 200 followed by an injected 201 override. It uses different route names and values from the source. The source compares parsed JSON strings while the workflow compares exact body bytes; no stdout observation is made for the test's debug print of response.content.",
                (
                    _source(
                        "docs_src/response_change_status_code/tutorial001_py310.py",
                        8,
                        13,
                        "Documented route returns an existing value or mutates the injected status for a newly created value",
                    ),
                    *_FASTAPI_INJECTED_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_cookies/test_tutorial002.py": _module(
        "The test sets a cookie on the injected temporary Response and reads it back from the TestClient response cookie jar.",
        {
            "test_path_operation": _function(
                "tests/test_tutorial/test_response_cookies/test_tutorial002.py",
                8,
                12,
                _HTTP_SELECTORS,
                "FastAPI propagates a cookie added to the injected Response and serializes the returned JSON object.",
                (
                    _link(
                        _RESPONSES_BACKGROUND,
                        "fastapi.test.test-tutorial-test-response-cookies-test-tutorial002.test-path-operation",
                        ("response-cookie",),
                        _HTTP_SELECTORS,
                    ),
                ),
                "The existing case uses the same /cookie-and-object/ route shape and injected set_cookie call, but independent cookie and body values. The workflow observes raw Set-Cookie bytes, full ordered headers, and exact body bytes. It does not observe HTTPX TestClient's response.cookies jar lookup or semantic JSON equality; cookie-jar extraction remains outside this ASGI workflow.",
                (
                    _source(
                        "docs_src/response_cookies/tutorial002_py310.py",
                        6,
                        9,
                        "Documented route sets a cookie on injected Response and returns JSON data",
                    ),
                    *_FASTAPI_INJECTED_RESPONSE,
                    *_STARLETTE_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
}
