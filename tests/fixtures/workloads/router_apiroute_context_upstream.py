"""Input workload for direct and nested APIRoute context observations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, Request


def _snapshot_route(route: Any, context: Any) -> dict[str, object]:
    return {
        "route": {
            "type": type(route).__name__,
            "path": route.path,
            "path_format": route.path_format,
            "name": route.name,
            "methods": sorted(route.methods),
            "tags": list(route.tags),
            "endpoint": route.endpoint.__name__,
        },
        "context": {
            "type": type(context).__name__,
            "original_route_matches": context.original_route is route,
            "path": context.path,
            "path_format": context.path_format,
            "name": context.name,
            "methods": sorted(context.methods),
            "tags": list(context.tags),
            "endpoint": context.endpoint.__name__,
        },
    }


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/direct/{item_id}", name="read_direct", tags=["direct"])
    def read_direct(item_id: str) -> dict[str, object]:
        from fastapi.routing import APIRoute, iter_route_contexts

        route = next(
            route
            for route in app.routes
            if isinstance(route, APIRoute) and route.name == "read_direct"
        )
        context = next(
            context
            for context in iter_route_contexts(app.routes)
            if context.original_route is route
        )
        snapshot = _snapshot_route(route, context)
        snapshot["item_id"] = item_id
        return snapshot

    leaf_router = APIRouter()

    @leaf_router.get("/items/{item_id}", name="read_nested", tags=["route"])
    def read_nested(item_id: str, request: Request) -> dict[str, object]:
        from fastapi.routing import iter_route_contexts

        original_route = leaf_router.routes[0]
        context = next(
            context
            for context in iter_route_contexts(app.routes)
            if context.original_route is original_route
        )
        snapshot = _snapshot_route(original_route, context)
        snapshot["scope_context_path"] = request.scope["fastapi"]["effective_route_context"].path
        snapshot["item_id"] = item_id
        return snapshot

    parent_router = APIRouter()
    parent_router.include_router(leaf_router, prefix="/v1", tags=["parent"])
    app.include_router(parent_router, prefix="/api", tags=["app"])
    return app
