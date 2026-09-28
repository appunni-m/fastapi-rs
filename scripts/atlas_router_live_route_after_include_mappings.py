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
        "test_live_route_addition_uses_include_metadata_for_runtime_and_openapi": _LIVE_ROUTE_MAPPING
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
        "test_url_path_for_uses_effective_context_for_live_included_route": {
            "source_span": {"path": _TEST, "start_line": 310, "end_line": 320},
            "reason": "URL path generation is a Python API observation, not the selected public ASGI/OpenAPI workflow.",
        },
    },
    "observation_boundary": (
        "Public FastAPI ASGI request and the selected OpenAPI operation tags/responses pointers. "
        "The entire OpenAPI document, schema generation internals, TestClient behavior, and generic Starlette "
        "route matching are not claimed."
    ),
}

__all__ = [
    "ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW",
    "SOURCE_IDENTITIES",
]
