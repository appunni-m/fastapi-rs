"""Reviewed section mapping for FastAPI's Global Dependencies page."""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


_PAGE = "tutorial/dependencies/global-dependencies.md"
_RECIPE = "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml"
_CASE = "fastapi.docs.documentation-wave.dependencies-security.global-dependencies"
_SELECTORS = [
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
]


DOC_SECTION_CASE_MAPPINGS_GLOBAL_DEPENDENCIES_20261015 = {
    (_PAGE, "global-dependencies"): _workflow(
        "Global Dependencies { #global-dependencies }",
        1,
        16,
        _RECIPE,
        [_CASE],
        ["dispatch", "openapi"],
        _SELECTORS,
        (
            "The selected dispatch requests one `/reports` operation with the valid tenant "
            "key and observes its status, ordered headers, and body bytes. The OpenAPI "
            "action inspects that operation's parameter pointer. This samples one app-level "
            "dependency and one operation; it does not exercise missing or rejected keys, "
            "another operation, multiple global dependencies, dependency overrides/cache or "
            "scope interactions, or the nested grouped-router section."
        ),
        (
            "The pinned example configures `FastAPI(dependencies=...)` and declares two "
            "operations (`../fastapi/docs_src/dependencies/tutorial012_an_py310.py:15-25`). "
            "FastAPI 0.141.1 forwards the constructor's dependency list to its root "
            "`APIRouter` (`../fastapi/fastapi/applications.py:984-999`); `add_api_route` "
            "copies router dependencies into each `APIRoute` "
            "(`../fastapi/fastapi/routing.py:2927-2945`), whose dependency graph is built "
            "and solved by FastAPI (`../fastapi/fastapi/dependencies/utils.py:271-347,619-680`). "
            "The selected input observes one successful operation and its required header "
            "parameter in OpenAPI, not the example's second global dependency or every "
            "operation's request path."
        ),
    ),
}
