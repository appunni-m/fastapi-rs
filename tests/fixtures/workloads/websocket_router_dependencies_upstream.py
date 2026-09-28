"""Partial FastAPI-owned APIRouter WebSocket dependency workload.

This covers dependency resolution and app overrides for router WebSocket
endpoints. Generic ASGI handshake behavior belongs to Starlette-RS; other
``test_ws_router.py`` route, validation, middleware, and exception cases are
outside this partial slice.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, FastAPI, WebSocket


async def websocket_dependency() -> str:
    return "Socket Dependency"


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build a router app with the selected dependency override state."""
    del event_trace
    app = FastAPI()
    router = APIRouter()

    if factory_input["dependency_override"]:
        app.dependency_overrides[websocket_dependency] = lambda: "Override"

    @router.websocket("/router-ws-depends/")
    async def router_websocket(
        websocket: WebSocket,
        data: str = Depends(websocket_dependency),
    ) -> None:
        await websocket.accept()
        await websocket.send_text(data)
        await websocket.close()

    app.include_router(router)
    return app
