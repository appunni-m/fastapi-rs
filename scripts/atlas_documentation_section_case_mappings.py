"""Reviewed section-level links from FastAPI documentation to input cases."""

DOC_SECTION_CASE_MAPPINGS = {
    ("tutorial/cors.md", "cors-preflight-requests"): {
        "heading": "CORS preflight requests { #cors-preflight-requests }",
        "start_line": 69,
        "end_line": 74,
        "recipe_path": "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml",
        "case_ids": [
            "fastapi.docs.cors-tutorial.allowed-preflight",
            "fastapi.docs.cors-tutorial.disallowed-preflight-method",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The section defines preflight requests as OPTIONS with Origin and "
            "Access-Control-Request-Method; these independent allowed and rejected "
            "inputs observe the response body, headers, and status."
        ),
        "rationale": (
            "This section's request shape and allowed/rejected outcomes are isolated from "
            "the neighboring simple-request section. FastAPI re-exports CORSMiddleware; "
            "Starlette owns the middleware behavior."
        ),
    },
    ("tutorial/cors.md", "simple-requests"): {
        "heading": "Simple requests { #simple-requests }",
        "start_line": 75,
        "end_line": 78,
        "recipe_path": "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml",
        "case_ids": [
            "fastapi.docs.cors-tutorial.allowed-simple-request",
            "fastapi.docs.cors-tutorial.unlisted-simple-request",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The section describes passing requests with Origin through the application "
            "while adding CORS headers; these independent allowed and unlisted origins "
            "observe response body, headers, and status."
        ),
        "rationale": (
            "This section's normal-request behavior is sampled separately from preflight. "
            "FastAPI re-exports CORSMiddleware; Starlette owns the middleware behavior."
        ),
    },
}
