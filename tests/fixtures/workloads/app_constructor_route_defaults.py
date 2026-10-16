"""Observe FastAPI constructor defaults inherited by path operations."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _event_trace: list[str]) -> FastAPI:
    app = FastAPI(
        deprecated=factory_input["deprecated"],
        include_in_schema=factory_input["include_in_schema"],
        **factory_input["extra"],
    )

    @app.get("/default")
    async def default_route() -> dict[str, str]:
        return {"route": "default"}

    @app.get("/_observe/route-defaults", include_in_schema=False)
    async def observe_defaults() -> dict[str, object]:
        route = next(route for route in app.routes if route.path == "/default")
        return {
            "router": {
                "deprecated": app.router.deprecated,
                "include_in_schema": app.router.include_in_schema,
            },
            "route": {
                "path": route.path,
                "deprecated": route.deprecated,
                "include_in_schema": route.include_in_schema,
            },
            "extra": app.extra,
        }

    return app
