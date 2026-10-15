"""Reviewed section mappings for FastAPI's advanced middleware page."""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    row = {
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
        row["action_ids"] = actions
    return row


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_MIDDLEWARE = "tests/fixtures/input-recipes/parity/middleware.yaml"
_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_GZIP = "tests/fixtures/input-recipes/parity/gzip-streaming-response-integration-docs.yaml"


DOC_SECTION_CASE_MAPPINGS_ADVANCED_MIDDLEWARE_1016 = {
    ("advanced/middleware.md", "advanced-middleware"): _excluded(
        "Advanced Middleware { #advanced-middleware }",
        1,
        97,
        (
            "The page introduction links back to the custom-middleware and CORS tutorials, then "
            "previews the child sections. "
            "It defines no separate request, response, or public operation; the independently "
            "observable child topics are "
            "mapped below."
        ),
        (
            "This H1 is an overview. Its linked middleware behavior is captured by the tutorial "
            "pages and the child-section "
            "workflows below, so no additional input is needed for the heading itself."
        ),
    ),
    ("advanced/middleware.md", "adding-asgi-middlewares"): _workflow(
        "Adding ASGI middlewares { #adding-asgi-middlewares }",
        9,
        41,
        _MIDDLEWARE,
        [
            "fastapi.middleware.custom-asgi-body-accepted",
            "fastapi.middleware.custom-asgi-body-exceeded",
        ],
        None,
        _HTTP,
        (
            "The two requests exercise a custom ASGI middleware registered on a FastAPI app: one "
            "body stays within the "
            "configured limit and one exceeds it. They observe exact status, ordered headers, and "
            "body bytes; they sample "
            "one custom middleware and do not cover arbitrary third-party classes or every "
            "add_middleware argument."
        ),
        (
            "FastAPI is a Starlette application and exposes inherited middleware registration. The "
            "selected input exercises "
            "that FastAPI integration; middleware dispatch and the ASGI response boundary "
            "belong to Starlette 1.6.0 and Starlette-RS."
        ),
    ),
    ("advanced/middleware.md", "integrated-middlewares"): _excluded(
        "Integrated middlewares { #integrated-middlewares }",
        42,
        53,
        (
            "This short section introduces the middleware examples and explains that most "
            "implementations come from "
            "Starlette. The concrete HTTPS redirect, trusted-host, and GZip sections below carry "
            "the independently "
            "observable behavior."
        ),
        (
            "The introduction identifies package ownership and points to the following "
            "examples; it "
            "specifies no distinct "
            "middleware input or outcome. Each named middleware section is mapped separately."
        ),
    ),
    ("advanced/middleware.md", "httpsredirectmiddleware"): _workflow(
        "`HTTPSRedirectMiddleware` { #httpsredirectmiddleware }",
        54,
        61,
        _MIDDLEWARE,
        ["fastapi.middleware.https-redirect-http"],
        ["redirect-insecure-request"],
        _HTTP,
        (
            "The request uses the documented insecure HTTP scheme and observes the redirect "
            "response status, ordered "
            "headers, and body bytes. It samples HTTP-to-HTTPS redirection only; the documented "
            "WebSocket scheme is not "
            "exercised here."
        ),
        (
            "FastAPI documents and re-exports Starlette's HTTPSRedirectMiddleware; its redirect "
            "behavior is owned by "
            "Starlette 1.6.0 and the corresponding Starlette-RS contract."
        ),
    ),
    ("advanced/middleware.md", "trustedhostmiddleware"): _workflow(
        "`TrustedHostMiddleware` { #trustedhostmiddleware }",
        62,
        74,
        _MIDDLEWARE,
        [
            "fastapi.middleware.trusted-host-wildcard-allowed",
            "fastapi.middleware.trusted-host-rejected",
        ],
        None,
        _HTTP,
        (
            "One request accepts a matching wildcard subdomain; another rejects an unlisted host. "
            "Both observe "
            "exact status, ordered headers, and body bytes. The documented www_redirect behavior "
            "and invalid-host variants "
            "are not sampled."
        ),
        (
            "FastAPI documents and re-exports Starlette's TrustedHostMiddleware; host validation "
            "and its rejection response "
            "are Starlette 1.6.0 behavior covered by Starlette-RS."
        ),
    ),
    ("advanced/middleware.md", "gzipmiddleware"): _workflow(
        "`GZipMiddleware` { #gzipmiddleware }",
        75,
        87,
        _GZIP,
        ["fastapi.middleware.gzip.streaming-response-docs-contract"],
        ["request-streaming-response-with-gzip"],
        ["asgi.send.message_types", "http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The request advertises gzip and selects a multi-yield StreamingResponse; the "
            "observations include exact wire "
            "body bytes, ordered headers, status, and ASGI send-message types. This samples the "
            "documented streaming path. "
            "minimum_size and compresslevel boundaries are not covered, and compressed bytes are "
            "compared without "
            "normalization."
        ),
        (
            "FastAPI documents GZipMiddleware as a convenience re-export from Starlette. "
            "Compression, threshold settings, "
            "and streaming response behavior belong to Starlette 1.6.0 and Starlette-RS."
        ),
    ),
    ("advanced/middleware.md", "other-middlewares"): _excluded(
        "Other middlewares { #other-middlewares }",
        88,
        97,
        (
            "The section only points to separately maintained Uvicorn, MessagePack, Starlette, and "
            "ASGI middleware "
            "catalogs. It defines no FastAPI-owned operation or outcome."
        ),
        (
            "Those middleware implementations and their contracts are owned by their respective "
            "projects, not FastAPI "
            "0.141.1. The generic ASGI protocol is covered by the Starlette-RS contract."
        ),
    ),
}
