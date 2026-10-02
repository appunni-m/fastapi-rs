"""Source review for FastAPI routes added after APIRouter inclusion."""

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
        "role": "sole generic ASGI routing and HTTP transport contract",
    },
    "pydantic": {"version": "2.13.4", "role": "pinned validation dependency"},
}

_TEST = "tests/test_router_include_context.py"
_RECIPE = "tests/fixtures/input-recipes/parity/router-live-route-after-include-source-review.yaml"
_WORKLOAD = "tests/fixtures/workloads/router_live_route_after_include_source_review.py"
_CASE = "fastapi.router.include-context.live-route-after-include"
_RUNTIME_ACTION = "dispatch-late-route"
_OPENAPI_ACTION = "project-openapi-late-route"
_SELECTORS = ["http.status", "http.body.bytes", "openapi.document"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


_WORKFLOW = {
    "recipe_path": _RECIPE,
    "case_id": _CASE,
    "action_ids": [_RUNTIME_ACTION, _OPENAPI_ACTION],
    "observation_selectors": list(_SELECTORS),
}

_APP_URL_PATH_FOR_WORKFLOW = {
    "recipe_path": "tests/fixtures/input-recipes/parity/inherited-app-url-path-for.yaml",
    "case_id": "fastapi.applications.url-path-for.included-router-context",
    "action_ids": ["reverse-included-route"],
    "observation_selectors": ["http.status", "http.headers.ordered", "http.body.bytes"],
}

_APIRouter_URL_PATH_FOR_WORKFLOW = {
    "recipe_path": "tests/fixtures/input-recipes/parity/inherited-apirouter-url-path-for.yaml",
    "case_id": "fastapi.apirouter.url-path-for.repeated-inclusion-context",
    "action_ids": ["reverse-parent-router-route"],
    "observation_selectors": ["http.status", "http.headers.ordered", "http.body.bytes"],
}

_APP_URL_PATH_FOR_MAPPING = {
    "review_status": "reviewed_partial",
    "feature_ids": ["app-routing"],
    "observation_selectors": list(_APP_URL_PATH_FOR_WORKFLOW["observation_selectors"]),
    "rationale": (
        "A FastAPI application reverses a route added to an APIRouter after the router was included, then "
        "returns the URLPath string through an independent HTTP endpoint. The route prefix and value are input-only."
    ),
    "replace_features": True,
    "contract_gate": (
        "Partial: this case observes the path string for one explicitly named route added after router inclusion. "
        "It does not claim URLPath host/protocol metadata, missing names, or other converter values."
    ),
    "workflow_cases": [_APP_URL_PATH_FOR_WORKFLOW],
    "stimulus_notes": (
        "The recipe includes an empty router before adding its named route, then requests a separate probe "
        "endpoint that returns the lookup result as response text; no expected path is embedded in the input."
    ),
    "supporting_sources": [
        _source(
            _TEST,
            310,
            320,
            "pinned FastAPI test_url_path_for_uses_effective_context_for_live_included_route and its public app.url_path_for assertion",
        )
    ],
}

_APIRouter_URL_PATH_FOR_MAPPING = {
    "review_status": "reviewed_partial",
    "feature_ids": ["app-routing"],
    "observation_selectors": list(_APIRouter_URL_PATH_FOR_WORKFLOW["observation_selectors"]),
    "rationale": (
        "A parent APIRouter reverses a route from a child router included under two prefixes. The workflow "
        "selects the public parent.url_path_for result through an independent HTTP endpoint."
    ),
    "replace_features": True,
    "contract_gate": (
        "Partial: the workflow observes the public parent router's first matching URLPath string. The "
        "source test's direct routes[1].url_path_for assertion concerns the mutable route collection and "
        "is not claimed by this public API case. URLPath metadata and other inclusion shapes remain open."
    ),
    "workflow_cases": [_APIRouter_URL_PATH_FOR_WORKFLOW],
    "stimulus_notes": (
        "The independent routers use distinct prefixes and an entry identifier. The expected path is not "
        "stored in the YAML input."
    ),
    "supporting_sources": [
        _source(
            _TEST,
            322,
            335,
            "pinned FastAPI test_url_path_for_uses_distinct_repeated_inclusion_contexts and its public parent_router.url_path_for assertion",
        )
    ],
}

_LIVE_ROUTE_MAPPING = {
    "review_status": "reviewed_partial",
    "feature_ids": ["app-routing"],
    "observation_selectors": list(_SELECTORS),
    "rationale": (
        "A route is added to an APIRouter after FastAPI has included that router. The public ASGI request "
        "checks that the new prefixed route dispatches and receives the include-level dependency; a focused "
        "OpenAPI projection checks that the include-level tag and response declaration apply to the late route."
    ),
    "replace_features": True,
    "contract_gate": (
        "Partial: one direct included-router mutation, dependency, tag, response declaration, and selected "
        "OpenAPI values are covered. The workflow does not assert the pre-mutation OpenAPI document or other "
        "router mutation shapes. Raw body-byte comparison also observes JSON response encoding beyond the "
        "source's parsed-value assertion. Generic ASGI routing and HTTP emission remain Starlette 1.6.0 behavior."
    ),
    "workflow_cases": [_WORKFLOW],
    "stimulus_notes": (
        f"Use {_RECIPE}::{_CASE}. It uses a new prefix, route, dependency marker, tag, response code, "
        "and response description. The recipe specifies only inputs and selected observations."
    ),
    "supporting_sources": [
        _source(
            _TEST,
            218,
            247,
            "pinned FastAPI 0.141.1 test_live_route_addition_uses_include_metadata_for_runtime_and_openapi and its assertions",
        ),
        _source(
            "fastapi/routing.py",
            2889,
            2971,
            "APIRouter.add_api_route combines router-level metadata, appends the route, and marks the route collection changed",
        ),
        _source(
            "fastapi/routing.py",
            2570,
            2584,
            "APIRouter tracks route changes and recursively derives versions for included routers",
        ),
        _source(
            "fastapi/routing.py",
            1601,
            1623,
            "_IncludedRouter rebuilds effective route candidates when the included router changes",
        ),
        _source(
            "fastapi/routing.py",
            3296,
            3312,
            "APIRouter.include_router records the include context and registers the included router",
        ),
        _source(
            "fastapi/applications.py",
            1070,
            1103,
            "FastAPI.openapi refreshes the cached schema when the router route version changes",
        ),
    ],
}

ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW = {
    "fastapi_identity": SOURCE_IDENTITIES["fastapi"],
    "mapping_status": "source-reviewed-input-candidate; parity pending",
    "recipe_path": _RECIPE,
    "workload_path": _WORKLOAD,
    "test_module": _TEST,
    "test_mappings": {
        "test_live_route_addition_uses_include_metadata_for_runtime_and_openapi": _LIVE_ROUTE_MAPPING,
        "test_url_path_for_uses_effective_context_for_live_included_route": _APP_URL_PATH_FOR_MAPPING,
        "test_url_path_for_uses_distinct_repeated_inclusion_contexts": _APIRouter_URL_PATH_FOR_MAPPING,
    },
    "exclusions": {
        "test_openapi_cache_updates_after_live_route_addition": {
            "source_span": {"path": _TEST, "start_line": 249, "end_line": 264},
            "reason": (
                "That test asserts that the first schema omits the route and a later schema includes it. "
                "This workflow observes only the post-addition projection and does not claim the separate "
                "pre-mutation cache invalidation sequence."
            ),
        },
        "test_nested_router_added_after_parent_inclusion_is_live": {
            "source_span": {"path": _TEST, "start_line": 266, "end_line": 284},
            "reason": (
                "This wave adds a direct route to an already included APIRouter; it does not add a child router "
                "to an already included parent."
            ),
        },
        "test_repeated_deep_inclusions_handle_all_concrete_paths": {
            "source_span": {"path": _TEST, "start_line": 286, "end_line": 308},
            "reason": "Repeated nested inclusion prefixes and several concrete paths are outside this focused case.",
        },
    },
    "observation_boundary": (
        "Public FastAPI ASGI responses for late-route dispatch, selected OpenAPI operation tags/responses "
        "pointers, and inherited url_path_for path strings returned through probe endpoints. The entire "
        "OpenAPI document, URLPath host/protocol metadata, TestClient behavior, and generic Starlette route "
        "matching and reversal internals are not claimed."
    ),
}

__all__ = [
    "ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW",
    "SOURCE_IDENTITIES",
]
