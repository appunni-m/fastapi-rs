"""Source-reviewed FastAPI frontend workflow mappings and exclusions.

The fixture is an input candidate for FastAPI 0.141.1. It records ASGI
stimuli and existing observation selectors only; it contains no expected
responses or parity results. Generic static-file emission and TestClient
behavior remain assigned to the pinned Starlette 1.6.0 / Starlette-RS
contract.
"""

from __future__ import annotations

from typing import Any

_TEST = "tests/test_frontend.py"
_DOC = "docs/en/docs/tutorial/frontend.md"
_RECIPE = "tests/fixtures/input-recipes/parity/frontend-fallback-routing-source-review.yaml"
_SURFACE_CASE = "fastapi.frontend.fallback-routing-surface"
_CONFIG_AUTO_CASE = "fastapi.frontend.configuration.auto-check-directory-production"
_CONFIG_FALLBACK_CASE = "fastapi.frontend.configuration.explicit-fallback-file-required"
_CONFIG_INVALID_CASE = "fastapi.frontend.configuration.invalid-fallback-value"
_CONFIG_DEFERRED_CASE = "fastapi.frontend.configuration.check-dir-false-defers-check"
_ROOT_PATH_CASE = "fastapi.test.test-frontend.test-frontend-respects-root-path"


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _candidate(
    *,
    start: int,
    end: int,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
    rationale: str,
    sources: list[dict[str, Any]],
    feature_ids: list[str] | None = None,
    gate: str | None = None,
) -> dict[str, Any]:
    test_source = _source(_TEST, start, end, "exact upstream FastAPI 0.141.1 test function span")
    workflow_link = {
        "recipe_path": _RECIPE,
        "case_id": case_id,
        "action_ids": action_ids,
        "observation_selectors": selectors,
    }
    row: dict[str, Any] = {
        "feature_ids": feature_ids or ["app-routing"],
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "supporting_sources": [test_source, *sources],
        "stimulus_notes": (
            f"Use {_RECIPE}, case {case_id}, actions {', '.join(action_ids) or '(construction only)'}. "
            "The recipe supplies only independently authored inputs and observation selectors."
        ),
        "workflow_cases": [workflow_link],
    }
    if gate:
        row["contract_gate"] = gate
    return row


_FALLBACK_IMPL = _source(
    "fastapi/routing.py",
    1899,
    2044,
    "FastAPI frontend static adapter selects fallback files, applies GET/HEAD and Accept gating, and assigns fallback response status",
)
_FRONTEND_REGISTRATION = _source(
    "fastapi/routing.py",
    2630,
    2717,
    "APIRouter.frontend resolves configuration, normalizes paths, adds low-priority frontend routes, and records route changes",
)
_APP_FRONTEND = _source(
    "fastapi/applications.py",
    1222,
    1299,
    "FastAPI.frontend public signature and delegation to the application router",
)
_LOW_PRIORITY_DISPATCH = _source(
    "fastapi/routing.py",
    2728,
    2781,
    "FastAPI Router dispatches ordinary routes before its low-priority route collection",
)
_FRONTEND_WEBSOCKET_FILTER = _source(
    "fastapi/routing.py",
    2069,
    2083,
    "FastAPI frontend route matching excludes WebSocket scopes, allowing an explicit WebSocket route at the same path to win",
)
_FRONTEND_MATCH_ROOT_PATH = _source(
    "fastapi/routing.py",
    2068,
    2078,
    "FastAPI frontend route matching uses Starlette get_route_path for the ASGI scope, so a configured root_path is considered during path matching",
)
_STARLETTE_ROUTE_PATH = _source(
    "starlette/_utils.py",
    96,
    110,
    "Starlette get_route_path strips a matching ASGI root_path prefix and otherwise preserves the path",
)
_FRONTEND_GROUP = _source(
    "fastapi/routing.py",
    2103,
    2169,
    "FastAPI frontend route group applies included prefixes and selects the most-specific frontend path",
)
_FRONTEND_DEPENDENCIES = _source(
    "fastapi/routing.py",
    2110,
    2121,
    "FastAPI frontend route group builds its parameterless dependency graph from app/router dependencies",
)
_FRONTEND_DEPENDENCY_DISPATCH = _source(
    "fastapi/routing.py",
    2191,
    2207,
    "FastAPI resolves frontend route dependencies before invoking the selected static frontend route",
)
_FRONTEND_CHECK_DIR = _source(
    "fastapi/routing.py",
    1881,
    1929,
    "FastAPI resolves check_dir from FASTAPI_ENV and eagerly validates frontend directories and explicit fallback files",
)
_DOC_FALLBACK = _source(
    _DOC,
    45,
    105,
    "documented SPA navigation gates, auto fallback precedence, and disabled fallback",
)
_DOC_DIRECTORY = _source(
    _DOC,
    107,
    131,
    "documented check_dir behavior and APIRouter prefix integration",
)

_ASGI_GATE = (
    "Input mapping only. It samples the listed FastAPI-owned fallback, route-priority, and "
    "configuration paths; it does not claim a complete frontend API contract. File lookup, "
    "headers, MIME types, validators, directory redirects, and static response emission are "
    "Starlette 1.6.0 behavior under the sibling Starlette-RS contract. The recipe uses direct "
    "ASGI observations, not TestClient parity."
)


FRONTEND_TEST_REVIEW_MAPPINGS = {
    _TEST: {
        "feature_ids": ["app-routing", "public-api-errors"],
        "module_observation_selectors": [
            "http.status",
            "http.body.bytes",
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
            "asgi.application_error.exception",
        ],
        "workflow_cases": [
            {
                "recipe_path": _RECIPE,
                "case_ids": [_SURFACE_CASE],
                "observation_selectors": [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                    "http.status",
                    "http.body.bytes",
                ],
            },
            {
                "recipe_path": _RECIPE,
                "case_ids": [_CONFIG_AUTO_CASE],
                "observation_selectors": [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
            },
            {
                "recipe_path": _RECIPE,
                "case_ids": [_CONFIG_FALLBACK_CASE],
                "observation_selectors": [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
            },
            {
                "recipe_path": _RECIPE,
                "case_ids": [_CONFIG_INVALID_CASE],
                "observation_selectors": [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
            },
            {
                "recipe_path": _RECIPE,
                "case_ids": [_CONFIG_DEFERRED_CASE],
                "observation_selectors": [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                    "asgi.application_error.exception",
                ],
            },
            {
                "recipe_path": _RECIPE,
                "case_ids": [_ROOT_PATH_CASE],
                "observation_selectors": ["http.status", "http.body.bytes"],
            },
        ],
        "rationale": (
            "FastAPI 0.141.1 adds fallback policy and low-priority frontend routing on top of "
            "Starlette static files. This independent wave samples fallback policy, API and "
            "included-router precedence, and construction/deferred directory configuration."
        ),
        "supporting_sources": [
            _FALLBACK_IMPL,
            _FRONTEND_REGISTRATION,
            _APP_FRONTEND,
            _DOC_FALLBACK,
            _DOC_DIRECTORY,
        ],
        "stimulus_notes": (
            "The source-reviewed recipe uses fresh per-case apps, deterministic temporary static "
            "directories, and direct ASGI requests. The fixed missing-directory input is used "
            "only for deferred check_dir error capture."
        ),
        "functions": {
            "test_404_fallback_handles_missing_assets": _candidate(
                start=756,
                end=765,
                case_id=_SURFACE_CASE,
                action_ids=["auto-404-serves-missing-asset"],
                selectors=["http.status", "http.body.bytes"],
                rationale="A configured 404 fallback serves a missing asset path while retaining the not-found status.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_auto_fallback_prefers_404_over_index": _candidate(
                start=768,
                end=778,
                case_id=_SURFACE_CASE,
                action_ids=["auto-prefers-404-for-navigation"],
                selectors=["http.status", "http.body.bytes"],
                rationale="The default auto policy chooses the 404 file when both it and index.html exist for an HTML navigation path.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_auto_fallback_uses_index_when_404_is_missing": _candidate(
                start=781,
                end=790,
                case_id=_SURFACE_CASE,
                action_ids=["auto-uses-index-for-xhtml-navigation"],
                selectors=["http.status", "http.body.bytes"],
                rationale="The default auto policy uses index.html for an XHTML navigation request when 404.html is absent.",
                sources=[_FALLBACK_IMPL, _FRONTEND_GROUP, _DOC_FALLBACK],
                gate=_ASGI_GATE,
            ),
            "test_auto_fallback_returns_normal_404_without_fallback_files": _candidate(
                start=793,
                end=802,
                case_id=_SURFACE_CASE,
                action_ids=["auto-no-fallback-files"],
                selectors=["http.status", "http.body.bytes"],
                rationale="The default auto policy produces the normal missing-route response when neither fallback file exists.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_index_fallback_for_navigation_request": _candidate(
                start=660,
                end=669,
                case_id=_SURFACE_CASE,
                action_ids=["explicit-index-html-navigation"],
                selectors=["http.status", "http.body.bytes"],
                rationale="The explicit index fallback serves a missing client-side route for a request that accepts HTML.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                gate=_ASGI_GATE,
            ),
            "test_head_fallback_request_works": _candidate(
                start=1019,
                end=1031,
                case_id=_SURFACE_CASE,
                action_ids=["explicit-index-head-navigation"],
                selectors=["http.status", "http.body.bytes"],
                rationale="HEAD is accepted for an HTML-navigation index fallback; body suppression and file headers remain Starlette response behavior.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                gate=_ASGI_GATE,
            ),
            "test_index_fallback_requires_explicit_html_acceptance": _candidate(
                start=742,
                end=753,
                case_id=_SURFACE_CASE,
                action_ids=["explicit-index-missing-asset"],
                selectors=["http.status", "http.body.bytes"],
                rationale="A missing JavaScript asset with only wildcard acceptance does not select the index fallback.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_unsupported_methods_to_fallback_only_routes_return_404": _candidate(
                start=1046,
                end=1058,
                case_id=_SURFACE_CASE,
                action_ids=["explicit-index-post-fallback-path"],
                selectors=["http.status", "http.body.bytes"],
                rationale="POST to a client-side path that exists only through the index fallback remains a not-found response.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_index_fallback_respects_explicit_html_rejection_with_wildcard": _candidate(
                start=700,
                end=713,
                case_id=_SURFACE_CASE,
                action_ids=["explicit-html-rejected-with-wildcard"],
                selectors=["http.status", "http.body.bytes"],
                rationale="An explicit q=0 rejection for HTML is retained even when a wildcard media range is accepted.",
                sources=[_FALLBACK_IMPL],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_no_fallback_returns_normal_404": _candidate(
                start=805,
                end=814,
                case_id=_SURFACE_CASE,
                action_ids=["disabled-fallback"],
                selectors=["http.status", "http.body.bytes"],
                rationale="fallback=None disables the SPA fallback for a missing HTML-navigation path.",
                sources=[_FALLBACK_IMPL, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_existing_api_route_wins_over_frontend": _candidate(
                start=618,
                end=632,
                case_id=_SURFACE_CASE,
                action_ids=["api-route-before-static-file"],
                selectors=["http.status", "http.body.bytes"],
                rationale="An ordinary included API route wins at a path that also names a static file below the frontend root.",
                sources=[_LOW_PRIORITY_DISPATCH, _DOC_FALLBACK],
                gate=_ASGI_GATE,
            ),
            "test_websocket_route_wins_over_frontend": _candidate(
                start=987,
                end=1003,
                case_id="fastapi.test.test-frontend.test-websocket-route-wins-over-frontend",
                action_ids=["colliding-websocket-path"],
                selectors=[
                    "websocket.event_order",
                    "websocket.messages",
                    "websocket.close_code",
                ],
                rationale="An explicitly registered FastAPI WebSocket route handles a path that also names a static frontend file.",
                sources=[_LOW_PRIORITY_DISPATCH, _FRONTEND_WEBSOCKET_FILTER],
                feature_ids=["app-routing", "websocket-lifecycle"],
                gate=(
                    "FastAPI route matching and frontend WebSocket exclusion are sampled here. "
                    "WebSocket handshake, message framing, and close protocol remain assigned "
                    "to the Starlette 1.6.0 / Starlette-RS contract."
                ),
            ),
            "test_api_route_404_is_not_replaced_by_frontend_fallback": _candidate(
                start=635,
                end=649,
                case_id=_SURFACE_CASE,
                action_ids=["api-404-before-static-fallback"],
                selectors=["http.status", "http.body.bytes"],
                rationale="A matched API route's FastAPI HTTPException response is preserved instead of falling through to the index file.",
                sources=[_LOW_PRIORITY_DISPATCH, _DOC_FALLBACK],
                feature_ids=["app-routing", "public-api-errors"],
                gate=_ASGI_GATE,
            ),
            "test_global_priority_across_included_routers": _candidate(
                start=890,
                end=908,
                case_id=_SURFACE_CASE,
                action_ids=["api-route-before-static-file"],
                selectors=["http.status", "http.body.bytes"],
                rationale="An API route included from a separate APIRouter has priority over a frontend fallback.",
                sources=[_LOW_PRIORITY_DISPATCH, _DOC_FALLBACK],
                gate=_ASGI_GATE,
            ),
            "test_frontend_path_matching_uses_segment_boundaries": _candidate(
                start=850,
                end=858,
                case_id=_SURFACE_CASE,
                action_ids=["auto-uses-index-for-xhtml-navigation"],
                selectors=["http.status", "http.body.bytes"],
                rationale="The /auto-index frontend path must be matched at a path-segment boundary instead of being captured by /auto.",
                sources=[_FRONTEND_GROUP, _FRONTEND_REGISTRATION],
                gate=_ASGI_GATE,
            ),
            "test_multiple_frontends_use_longest_matching_prefix": _candidate(
                start=861,
                end=873,
                case_id=_SURFACE_CASE,
                action_ids=["auto-uses-index-for-xhtml-navigation"],
                selectors=["http.status", "http.body.bytes"],
                rationale="When multiple frontend paths match, the more-specific registered path supplies the frontend fallback.",
                sources=[_FRONTEND_GROUP, _FRONTEND_REGISTRATION],
                gate=_ASGI_GATE,
            ),
            "test_apirouter_frontend_with_router_prefix_and_frontend_subpath": _candidate(
                start=49,
                end=60,
                case_id=_SURFACE_CASE,
                action_ids=["included-router-prefix-and-subpath"],
                selectors=["http.status", "http.body.bytes"],
                rationale="Frontend static paths compose the APIRouter's own prefix, its frontend subpath, and include_router's prefix.",
                sources=[_FRONTEND_REGISTRATION, _FRONTEND_GROUP, _DOC_DIRECTORY],
                gate=_ASGI_GATE,
            ),
            "test_frontend_respects_root_path": _candidate(
                start=975,
                end=985,
                case_id=_ROOT_PATH_CASE,
                action_ids=["nonempty-root-path-static-asset"],
                selectors=["http.status", "http.body.bytes"],
                rationale="A frontend mounted at /app continues to serve its asset when the ASGI scope carries a nonempty /proxy root_path.",
                sources=[_FRONTEND_MATCH_ROOT_PATH, _STARLETTE_ROUTE_PATH],
                feature_ids=["app-routing"],
                gate=(
                    _ASGI_GATE
                    + " This direct ASGI input represents the TestClient root_path scope from the source test; generic root_path normalization is defined by Starlette's get_route_path utility."
                ),
            ),
            "test_apirouter_frontend_dependencies_protect_prefixed_frontend": _candidate(
                start=313,
                end=343,
                case_id=_SURFACE_CASE,
                action_ids=[
                    "included-router-missing-session",
                    "included-router-authenticated-session",
                ],
                selectors=["http.status", "http.body.bytes"],
                rationale="An APIRouter dependency rejects the included frontend request without a session cookie and permits the same request after the cookie is supplied.",
                sources=[
                    _FRONTEND_DEPENDENCIES,
                    _FRONTEND_DEPENDENCY_DISPATCH,
                    _DOC_DIRECTORY,
                    _source(
                        _DOC,
                        133,
                        139,
                        "documented app/router/include_router dependency and middleware behavior for frontend responses",
                    ),
                ],
                feature_ids=["app-routing", "dependency-security", "public-api-errors"],
                gate=(
                    _ASGI_GATE
                    + " The two cookie requests sample FastAPI dependency enforcement; file lookup and response emission remain Starlette-owned."
                ),
            ),
            "test_check_dir_auto_fails_outside_development": _candidate(
                start=1247,
                end=1252,
                case_id=_CONFIG_AUTO_CASE,
                action_ids=[],
                selectors=[
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                rationale="With FASTAPI_ENV set to production, check_dir='auto' checks the missing directory during route registration.",
                sources=[
                    _APP_FRONTEND,
                    _FRONTEND_REGISTRATION,
                    _FRONTEND_CHECK_DIR,
                    _DOC_DIRECTORY,
                ],
                gate=_ASGI_GATE,
            ),
            "test_explicit_fallback_files_fail_clearly_when_missing": _candidate(
                start=1263,
                end=1284,
                case_id=_CONFIG_FALLBACK_CASE,
                action_ids=[],
                selectors=[
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                rationale="With an existing frontend directory, selecting a missing explicit index.html fallback fails during construction.",
                sources=[_APP_FRONTEND, _FRONTEND_REGISTRATION, _FRONTEND_CHECK_DIR, _DOC_FALLBACK],
                gate=_ASGI_GATE,
            ),
            "test_frontend_fallback_rejects_invalid_fallback": _candidate(
                start=63,
                end=69,
                case_id=_CONFIG_INVALID_CASE,
                action_ids=[],
                selectors=[
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                rationale="An unsupported fallback value is rejected as FastAPI registers the frontend route.",
                sources=[_APP_FRONTEND, _FRONTEND_REGISTRATION, _FALLBACK_IMPL],
                gate=_ASGI_GATE,
            ),
            "test_check_dir_false_allows_missing_directory_and_fails_on_request": _candidate(
                start=1255,
                end=1260,
                case_id=_CONFIG_DEFERRED_CASE,
                action_ids=["dispatch-to-missing-front-end-directory"],
                selectors=[
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                    "asgi.application_error.exception",
                ],
                rationale="check_dir=False permits construction and defers the missing-directory error until the ASGI request is dispatched.",
                sources=[
                    _APP_FRONTEND,
                    _FRONTEND_REGISTRATION,
                    _source(
                        "fastapi/routing.py",
                        1940,
                        1944,
                        "FastAPI frontend static adapter checks deferred configuration before the file lookup",
                    ),
                    _source(
                        "starlette/staticfiles.py",
                        189,
                        203,
                        "Starlette 1.6.0 checks StaticFiles configuration on the first request; generic failure behavior belongs to the separate Starlette-RS contract",
                    ),
                    _DOC_DIRECTORY,
                ],
                feature_ids=["app-routing", "public-api-errors"],
                gate=(
                    _ASGI_GATE
                    + " The deferred exception is selected at the integration boundary; its generic StaticFiles check_config implementation is Starlette-owned."
                ),
            ),
        },
    }
}


FRONTEND_TEST_FUNCTION_EXCLUSIONS = {
    _TEST: {
        "test_frontend_static_files_lookup_errors": (
            "This test monkeypatches the private FastAPI frontend StaticFiles lookup_path and injects operating-system exceptions. The current wave samples public ASGI fallback and routing behavior; direct internal monkeypatch behavior and generic filesystem error injection are outside its input contract."
        ),
        "test_frontend_route_group_helpers": (
            "This test calls private _frontend_routes.matches/handle/url_path_for directly and asserts Starlette Match and NoMatchFound internals. The current workflow samples the public app/router ASGI path and has no observation for private route-object internals."
        ),
        "test_included_low_priority_routes_cache_is_reused": (
            "This test asserts object identity of the private effective_low_priority_routes cache. Cache identity is an implementation detail and is not an observable ASGI compatibility selector."
        ),
        "test_low_priority_api_route_handles_with_context": (
            "This test inserts a route directly into the private _low_priority_routes list. The public API-route priority case uses include_router and ordinary route registration instead."
        ),
        "test_included_low_priority_api_route_handles_with_context": (
            "This test inserts a route directly into the private _low_priority_routes list and exercises internal route context plumbing, outside the selected public frontend contract."
        ),
        "test_normal_route_partial_match_returns_before_frontend": (
            "This test supplies a synthetic Starlette BaseRoute with Match.PARTIAL to inspect low-level routing order. It does not use a regular FastAPI path operation and generic Starlette matching belongs to the separate contract."
        ),
        "test_normal_route_partial_match_wins_before_frontend": (
            "This test depends on a synthetic Starlette partial route; the selected route-priority cases use regular FastAPI operations through public ASGI dispatch."
        ),
        "test_basic_file_serving": (
            "This test checks static-file ETag and Last-Modified headers. File response construction and validators are generic Starlette static-file behavior under the sibling contract."
        ),
        "test_directory_index_and_redirect": (
            "This test checks directory index lookup and slash redirect behavior supplied by generic Starlette StaticFiles. It is not a FastAPI fallback-policy claim."
        ),
        "test_check_dir_auto_warns_in_development": (
            "The v3 workflow schema has no construction-warning observation selector, so it cannot express the source's UserWarning category/message or warning source filename."
        ),
        "test_check_dir_auto_router_warning_points_to_user_code": (
            "The v3 workflow schema has no construction-warning observation selector, so it cannot express the UserWarning source filename asserted by this APIRouter test."
        ),
        "test_docs_frontend_examples": (
            "This parameterized test executes documentation example files with runpy and TestClient. The new workload independently authors ASGI stimuli; it does not import source examples or claim docs-test-runner parity."
        ),
        "test_path_traversal_cannot_escape_directory": (
            "Traversal containment and path normalization are generic static-file lookup guarantees assigned to the Starlette 1.6.0 / Starlette-RS contract."
        ),
        "test_symlink_outside_directory_is_not_served": (
            "Symlink containment and platform-dependent symlink availability are generic static-file lookup behavior assigned to Starlette-RS, not FastAPI fallback policy."
        ),
    }
}


FRONTEND_TEST_FUNCTION_EXCLUSION_EVIDENCE = {
    _TEST: {
        "test_frontend_static_files_lookup_errors": [
            _source(
                _TEST,
                86,
                121,
                "private lookup_path monkeypatch and injected filesystem error assertions",
            )
        ],
        "test_frontend_route_group_helpers": [
            _source(
                _TEST,
                124,
                161,
                "direct assertions against private frontend route-group and Starlette route methods",
            )
        ],
        "test_included_low_priority_routes_cache_is_reused": [
            _source(
                _TEST,
                164,
                185,
                "private included-router effective_low_priority_routes cache identity",
            )
        ],
        "test_low_priority_api_route_handles_with_context": [
            _source(
                _TEST, 188, 201, "direct private low-priority route insertion and context assertion"
            )
        ],
        "test_included_low_priority_api_route_handles_with_context": [
            _source(
                _TEST,
                204,
                219,
                "direct private APIRouter low-priority route insertion and context assertion",
            )
        ],
        "test_normal_route_partial_match_returns_before_frontend": [
            _source(_TEST, 222, 240, "synthetic Starlette BaseRoute partial-match stimulus")
        ],
        "test_normal_route_partial_match_wins_before_frontend": [
            _source(_TEST, 243, 261, "synthetic Starlette route-partial precedence stimulus")
        ],
        "test_basic_file_serving": [
            _source(_TEST, 264, 275, "generic static-file body, ETag, and Last-Modified assertions")
        ],
        "test_directory_index_and_redirect": [
            _source(
                _TEST, 817, 830, "generic static-file directory index and slash redirect assertions"
            )
        ],
        "test_check_dir_auto_warns_in_development": [
            _source(
                _TEST, 1218, 1226, "development-mode UserWarning and source-filename assertions"
            )
        ],
        "test_check_dir_auto_router_warning_points_to_user_code": [
            _source(
                _TEST, 1229, 1236, "router development-mode UserWarning source-filename assertion"
            )
        ],
        "test_docs_frontend_examples": [
            _source(
                _TEST, 1354, 1376, "parameterized docs-example loader and TestClient assertions"
            )
        ],
        "test_path_traversal_cannot_escape_directory": [
            _source(_TEST, 1174, 1184, "generic static-file traversal containment assertions")
        ],
        "test_symlink_outside_directory_is_not_served": [
            _source(_TEST, 1187, 1203, "generic static-file symlink containment and platform skip")
        ],
    }
}


FRONTEND_TEST_SCOPE_NOTES = {
    _TEST: {
        "test_frontend_routes_are_not_in_openapi": {
            "source": _source(
                _TEST,
                1287,
                1304,
                "OpenAPI exclusion behavior already represented by frontend-openapi-metadata-wave.yaml",
            ),
            "existing_workflow": "tests/fixtures/input-recipes/parity/frontend-openapi-metadata-wave.yaml",
            "note": (
                "Retain the existing OpenAPI workflow mapping; do not add this test to the "
                "global TEST_FUNCTION_EXCLUSIONS set because exclusions take precedence."
            ),
        }
    }
}


FRONTEND_WAVE_SOURCE_REVIEW = {
    "fastapi_identity": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette_identity": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic-framework oracle and separate Starlette-RS contract",
    },
    "mapping_status": "source-reviewed-input-candidate; parity pending",
    "recipe_path": _RECIPE,
    "workload_path": "tests/fixtures/workloads/frontend_fallback_routing_source_review.py",
    "test_module": _TEST,
    "documentation_page": _DOC,
    "test_mappings": FRONTEND_TEST_REVIEW_MAPPINGS[_TEST]["functions"],
    "exclusions": FRONTEND_TEST_FUNCTION_EXCLUSIONS[_TEST],
    "exclusion_evidence": FRONTEND_TEST_FUNCTION_EXCLUSION_EVIDENCE[_TEST],
    "scope_notes": FRONTEND_TEST_SCOPE_NOTES[_TEST],
    "observation_boundary": _ASGI_GATE,
}
