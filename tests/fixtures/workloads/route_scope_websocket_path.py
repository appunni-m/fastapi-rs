"""Independent input for FastAPI's WebSocket route-scope metadata."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()

    @app.websocket("/streams/{stream_id}")
    async def observe_route_scope(stream_id: str, websocket: WebSocket) -> None:
        route = websocket.scope["route"]
        await websocket.accept()
        await websocket.send_json({"stream_id": stream_id, "route_path": route.path})
        await websocket.close()

    return app
