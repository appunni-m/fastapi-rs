"""Reviewed mappings for the FastAPI response-headers documentation page."""

_DIRECT = "tests/fixtures/input-recipes/parity/docs-response-headers-1016.yaml"
_RESPONSE_HEADER_TUTORIAL = "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml"
_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]


def _workflow(heading, start, end, recipe, case, action, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": [case],
        "action_ids": [action],
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


DOC_SECTION_CASE_MAPPINGS_RESPONSE_HEADERS_1016 = {
    ("advanced/response-headers.md", "response-headers"): _workflow(
        "Response Headers { #response-headers }",
        1,
        41,
        _DIRECT,
        "fastapi.docs.response-headers-1016.direct-response",
        "header-response",
        _HTTP,
        (
            "The page-level mapping selects the documented direct JSONResponse with two "
            "headers. The temporary Response parameter and custom-header guidance are "
            "mapped in their child sections."
        ),
        (
            "FastAPI accepts a Starlette Response returned directly from a path operation; "
            "the response class owns header encoding and transport."
        ),
    ),
    ("advanced/response-headers.md", "use-a-response-parameter"): _workflow(
        "Use a `Response` parameter { #use-a-response-parameter }",
        3,
        18,
        _RESPONSE_HEADER_TUTORIAL,
        "fastapi.test.test-tutorial-test-response-headers-test-tutorial002.test-path-operation",
        "response-header",
        _HTTP,
        (
            "This is the pinned tutorial 002 route: it mutates the temporary injected "
            "Response and returns the documented dictionary. The observation selects the "
            "complete HTTP result; dependency-provided headers and response-model filtering "
            "are not added here."
        ),
        (
            "FastAPI injects a temporary Response into the path operation, extracts its "
            "headers, and applies them to the serialized endpoint result."
        ),
    ),
    ("advanced/response-headers.md", "return-a-response-directly"): _workflow(
        "Return a `Response` directly { #return-a-response-directly }",
        19,
        36,
        _DIRECT,
        "fastapi.docs.response-headers-1016.direct-response",
        "header-response",
        _HTTP,
        (
            "The action follows the page's tutorial 001 example and observes the returned "
            "JSONResponse headers, status, and body. Generic JSONResponse construction is "
            "owned by Starlette."
        ),
        (
            "FastAPI passes a path operation's directly returned Response through as the "
            "HTTP result; Starlette defines the JSONResponse representation."
        ),
    ),
    ("advanced/response-headers.md", "custom-headers"): _excluded(
        "Custom Headers { #custom-headers }",
        37,
        41,
        (
            "This section gives HTTP header naming guidance and points browser clients to "
            "Starlette's CORS middleware `expose_headers` setting. Neither rule defines an "
            "independent FastAPI behavior; generic header and CORS behavior belongs to the "
            "pinned Starlette 1.6.0 contract."
        ),
        (
            "The source explicitly refers users to Starlette's CORS documentation for "
            "exposed headers. FastAPI-specific direct and injected Response integration is "
            "covered by the adjacent section mappings."
        ),
    ),
}
