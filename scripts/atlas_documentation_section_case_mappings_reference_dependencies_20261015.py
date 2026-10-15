"""Reviewed section mappings for the FastAPI dependency API reference."""


_TUTORIAL_RECIPE = (
    "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml"
)
_SECURITY_SCOPES_RECIPE = "tests/fixtures/input-recipes/parity/docs-security-scopes-1016.yaml"
_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_OPENAPI_SECURITY = ["openapi.document", "openapi.paths", "openapi.security"]


DOC_SECTION_CASE_MAPPINGS_REFERENCE_DEPENDENCIES_20261015 = {
    ("reference/dependencies.md", "@line:1"): {
        "status": "excluded",
        "heading": "Dependencies - `Depends()` and `Security()`",
        "start_line": 1,
        "end_line": 29,
        "exclusion_reason": (
            "The H1 introduces the two API sections below and adds no independent behavior."
        ),
        "rationale": (
            "Callable dependency resolution and OAuth2 scope declaration are mapped in the "
            "child sections; the page title is a navigation summary."
        ),
    },
    ("reference/dependencies.md", "@line:3"): {
        "heading": "`Depends()`",
        "start_line": 3,
        "end_line": 16,
        "recipe_path": _TUTORIAL_RECIPE,
        "case_ids": [
            "fastapi.dependencies.tutorial-review.basic-defaults",
            "fastapi.dependencies.tutorial-review.basic-partial-query",
        ],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "Each selected case contains one request action: `omit-query-values` sends no "
            "query values, while `set-query-and-use-numeric-defaults` supplies `q=birch`; "
            "both exercise a callable dependency and observe its response. This samples "
            "dependency use only; it does not claim the complete Depends signature, "
            "caching/scope options, or every dependency parameter source."
        ),
        "rationale": (
            "FastAPI 0.141.1 at 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f defines Depends "
            "as a frozen record carrying a callable, cache "
            "flag, and scope (`../fastapi/fastapi/params.py:746-751`), then analyzes and "
            "resolves callable dependencies in `get_dependant` and `solve_dependencies` "
            "(`../fastapi/fastapi/dependencies/utils.py:302-347,619-690`). The selected "
            "workflows are independent requests with different routes and values; Starlette "
            "1.6.0 owns generic ASGI request and response transport."
        ),
    },
    ("reference/dependencies.md", "@line:17"): {
        "heading": "`Security()`",
        "start_line": 17,
        "end_line": 29,
        "recipe_path": _SECURITY_SCOPES_RECIPE,
        "case_ids": ["fastapi.docs.security-scopes-1016.oauth2-surface"],
        "action_ids": ["inspect-decorator-openapi", "read-security-decorator"],
        "observation_selectors": _HTTP + _OPENAPI_SECURITY,
        "scope_note": (
            "The selected actions sample one Security-decorated route's HTTP response and "
            "its declared OpenAPI security projection. They do not claim JWT signing, password "
            "hashing, application authorization policy, or all OAuth2 scope combinations."
        ),
        "rationale": (
            "FastAPI 0.141.1 at 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f defines Security "
            "as a Depends subtype with an OAuth2 scopes "
            "field (`../fastapi/fastapi/params.py:753-757`); dependency analysis attaches "
            "those scopes to the dependant and OpenAPI generation emits the security "
            "requirement (`../fastapi/fastapi/dependencies/utils.py:302-347`; "
            "`../fastapi/fastapi/openapi/utils.py:99-154`). The recipe selects only the "
            "decorator route's OpenAPI action and one request action."
        ),
    },
}
