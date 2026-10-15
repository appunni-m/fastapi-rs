"""Reviewed section-to-workflow links for FastAPI's frontend tutorial."""

_PAGE = "tutorial/frontend.md"
_FALLBACK_RECIPE = (
    "tests/fixtures/input-recipes/parity/frontend-fallback-routing-source-review.yaml"
)
_DEPENDENCY_RECIPE = "tests/fixtures/input-recipes/parity/frontend-dependency-source-wave.yaml"
_FRONTEND_SECTIONS_RECIPE = (
    "tests/fixtures/input-recipes/parity/frontend-documentation-sections-20261015.yaml"
)

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_BODY = ["http.body.bytes", "http.status"]
_CONSTRUCTION = [
    "construction.outcome",
    "construction.exception_class",
    "construction.exception_message",
]


def _workflow(
    *,
    heading: str,
    start: int,
    end: int,
    recipe: str,
    cases: list[str],
    actions: list[str] | None,
    selectors: list[str],
    note: str,
    rationale: str,
) -> dict[str, object]:
    row: dict[str, object] = {
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


_ROUTING_RATIONALE = (
    "FastAPI 0.141.1 registers frontend routes in the low-priority route collection and "
    "dispatches ordinary path operations first (fastapi/routing.py:2630-2717, 2728-2781). "
    "The linked input is direct ASGI; generic file lookup and response emission remain "
    "Starlette 1.6.0 behavior."
)

_FALLBACK_RATIONALE = (
    "FastAPI 0.141.1's frontend adapter applies the GET/HEAD, Accept, and fallback-file "
    "selection policy in fastapi/routing.py:1899-2044. The input records only response "
    "status and body; generic static-file headers, MIME types, and HEAD body suppression "
    "remain Starlette 1.6.0 behavior."
)

DOC_SECTION_CASE_MAPPINGS_FRONTEND_20261015 = {
    (_PAGE, "frontend"): _workflow(
        heading="Frontend { #frontend }",
        start=1,
        end=145,
        recipe="tests/fixtures/input-recipes/parity/docs-types-frontend.yaml",
        cases=["fastapi.docs.reference-wave.frontend.api-route-priority"],
        actions=["dispatch", "serve-existing-build-asset"],
        selectors=_HTTP,
        note=(
            "The API-path request observes path-operation priority; a separate request serves "
            "an existing file from the build directory. Frontend-framework build commands and "
            "project structure are illustrative user tooling and outside these cases."
        ),
        rationale=_ROUTING_RATIONALE,
    ),
    (_PAGE, "serve-a-frontend"): _workflow(
        heading="Serve a Frontend { #serve-a-frontend }",
        start=19,
        end=44,
        recipe=_FRONTEND_SECTIONS_RECIPE,
        cases=["fastapi.docs.frontend-section.static-app-asset"],
        actions=["serve-built-asset"],
        selectors=_HTTP,
        note=(
            "One GET retrieves an existing asset from a generated-files directory registered "
            "with app.frontend(). The input samples ordinary app-level file delivery only; "
            "build-tool execution and API-route priority are mapped separately."
        ),
        rationale=(
            "FastAPI 0.141.1 registers the configured frontend path and delegates file lookup "
            "to its Starlette StaticFiles adapter (fastapi/routing.py:2630-2717, 1899-2044). "
            "The selected response confirms the integrated route outcome; generic file "
            "lookup, MIME handling, and response emission remain Starlette 1.6.0 behavior."
        ),
    ),
    (_PAGE, "client-side-routing"): _workflow(
        heading="Client-Side Routing { #client-side-routing }",
        start=45,
        end=66,
        recipe=_FALLBACK_RECIPE,
        cases=["fastapi.frontend.fallback-routing-surface"],
        actions=[
            "explicit-index-html-navigation",
            "explicit-index-head-navigation",
            "explicit-index-missing-asset",
            "explicit-index-post-fallback-path",
            "explicit-html-rejected-with-wildcard",
        ],
        selectors=_HTTP_BODY,
        note=(
            "The selected inputs cover GET and HEAD navigation fallback, a missing asset, a "
            "non-GET client-side path, and explicit HTML rejection despite wildcard acceptance. "
            "They do not claim all methods, media ranges, or response-header behavior."
        ),
        rationale=_FALLBACK_RATIONALE,
    ),
    (_PAGE, "custom-404-page"): _workflow(
        heading="Custom 404 Page { #custom-404-page }",
        start=67,
        end=86,
        recipe=_FRONTEND_SECTIONS_RECIPE,
        cases=["fastapi.docs.frontend-section.explicit-custom-404"],
        actions=["missing-asset-uses-explicit-404-file"],
        selectors=_HTTP_BODY,
        note=(
            "A missing asset request uses the explicitly configured 404.html file and selects "
            "its response status and body. The separate automatic fallback precedence is "
            "covered by the Fallback Auto section mapping."
        ),
        rationale=_FALLBACK_RATIONALE,
    ),
    (_PAGE, "fallback-auto"): _workflow(
        heading="Fallback Auto { #fallback-auto }",
        start=87,
        end=98,
        recipe=_FALLBACK_RECIPE,
        cases=["fastapi.frontend.fallback-routing-surface"],
        actions=[
            "auto-prefers-404-for-navigation",
            "auto-uses-index-for-xhtml-navigation",
            "auto-no-fallback-files",
        ],
        selectors=_HTTP_BODY,
        note=(
            "The actions independently supply both fallback files, index.html without 404.html, "
            "and neither file. They select response status and body only; static response "
            "details remain Starlette-owned."
        ),
        rationale=_FALLBACK_RATIONALE,
    ),
    (_PAGE, "disable-fallback"): _workflow(
        heading="Disable Fallback { #disable-fallback }",
        start=99,
        end=106,
        recipe=_FALLBACK_RECIPE,
        cases=["fastapi.frontend.fallback-routing-surface"],
        actions=["disabled-fallback"],
        selectors=_HTTP_BODY,
        note=(
            "The input configures fallback=None and requests a missing HTML-navigation path; "
            "only the resulting HTTP status and body are selected."
        ),
        rationale=_FALLBACK_RATIONALE,
    ),
    (_PAGE, "check-directory"): _workflow(
        heading="Check Directory { #check-directory }",
        start=107,
        end=122,
        recipe=_FRONTEND_SECTIONS_RECIPE,
        cases=[
            "fastapi.docs.frontend-section.auto-directory-production-error",
            "fastapi.docs.frontend-section.auto-directory-development-warning",
            "fastapi.docs.frontend-section.explicit-check-dir-true",
            "fastapi.docs.frontend-section.check-dir-false-defers-error",
        ],
        actions=None,
        selectors=[*_CONSTRUCTION, "asgi.application_error.exception", "python.warnings"],
        note=(
            "Fresh cases cover auto mode in production and development, explicit check_dir=True, "
            "and check_dir=False followed by a request. The mapping selects construction "
            "outcome/error details, the construction warning, and the deferred ASGI application "
            "error. FASTAPI_ENV setup by the separate fastapi dev command is outside this "
            "page case."
        ),
        rationale=(
            "FastAPI 0.141.1 resolves check_dir='auto' from FASTAPI_ENV, warns for a missing "
            "development directory, validates other environments during construction, and "
            "defers validation when check_dir=False (fastapi/routing.py:1881-1929). The warning "
            "and errors are FastAPI-owned; request protocol behavior remains Starlette-owned."
        ),
    ),
    (_PAGE, "use-it-with-apirouter"): _workflow(
        heading="Use it with `APIRouter` { #use-it-with-apirouter }",
        start=123,
        end=132,
        recipe=_FALLBACK_RECIPE,
        cases=["fastapi.frontend.fallback-routing-surface"],
        actions=["included-router-prefix-and-subpath"],
        selectors=_HTTP_BODY,
        note=(
            "The selected static asset request composes an APIRouter prefix, frontend subpath, "
            "and include_router prefix. Ordinary API-route priority is covered by the page's "
            "intro mapping; this action observes the asset response only."
        ),
        rationale=(
            "FastAPI 0.141.1 composes router and include_router prefixes when it registers a "
            "frontend route (fastapi/routing.py:2630-2717). The fixture observes one direct "
            "ASGI asset request; generic static-file behavior remains Starlette 1.6.0-owned."
        ),
    ),
    (_PAGE, "dependencies-and-middleware"): _workflow(
        heading="Dependencies and Middleware { #dependencies-and-middleware }",
        start=133,
        end=140,
        recipe=_DEPENDENCY_RECIPE,
        cases=["fastapi.frontend.dependencies-nested-inclusion-order"],
        actions=["nested-frontend-dependency-order"],
        selectors=_HTTP,
        note=(
            "The nested app/include/router dependencies run for a frontend request and expose "
            "their order through response headers. This partial input does not sample middleware "
            "registration or background-task execution; generic middleware and response "
            "transport behavior remain assigned to Starlette-RS."
        ),
        rationale=(
            "FastAPI 0.141.1 builds the frontend's parameterless dependency graph from app and "
            "router dependencies, then resolves it before invoking the selected frontend route "
            "(fastapi/routing.py:2103-2169, 2191-2207). The independent case observes HTTP "
            "status, ordered headers, and body."
        ),
    ),
    (_PAGE, "static-build-output-only"): {
        "status": "excluded",
        "heading": "Static Build Output Only { #static-build-output-only }",
        "start_line": 141,
        "end_line": 145,
        "exclusion_reason": (
            "The section's server-side-rendering distinction describes frontend-framework "
            "architecture and the application's build/deployment choice. Serving an existing "
            "file is already sampled under Serve a Frontend; server-side rendering is not a "
            "FastAPI frontend-route input contract, and generic static-file service is "
            "Starlette-owned."
        ),
        "rationale": (
            "FastAPI 0.141.1 frontend registration selects a directory-backed Starlette "
            "StaticFiles adapter (fastapi/routing.py:1899-2044, 2630-2717). The pinned page's "
            "framework rendering boundary does not describe additional FastAPI control flow."
        ),
    },
}
