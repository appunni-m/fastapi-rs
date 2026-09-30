"""Independent router dependency workflow derived from FastAPI's router contract."""

from __future__ import annotations

from collections.abc import Mapping

from fastapi import APIRouter, Depends, FastAPI, WebSocket


async def socket_value() -> str:
    return "Socket Dependency"


async def socket_value_override() -> str:
    return "Override"


def create_app(factory_input: Mapping[str, object], event_trace: list[str]) -> FastAPI:
    """Build a router with one WebSocket dependency and optional override."""
    del event_trace
    app = FastAPI()
    router = APIRouter()

    @router.websocket("/router-ws-depends/")
    async def dependency_socket(
        websocket: WebSocket,
        value: str = Depends(socket_value),
    ) -> None:
        await websocket.accept()
        await websocket.send_text(value)
        await websocket.close()

    if factory_input["dependency_override"]:
        app.dependency_overrides[socket_value] = socket_value_override
    app.include_router(router)
    return app
