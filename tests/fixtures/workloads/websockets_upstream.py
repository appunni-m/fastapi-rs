"""Independent ASGI stimuli for WebSocket dependencies and sessions."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect


def dependency_list() -> list[str]:
    return []


DependencyList = Annotated[list[str], Depends(dependency_list)]


def append_dependency(name: str):
    def add_name(dependencies: DependencyList):
        dependencies.append(name)
        return dependencies

    return Depends(add_name)


def create_app() -> FastAPI:
    app = FastAPI(dependencies=[append_dependency("app")])

    @app.get("/")
    async def home():
        return HTMLResponse("<!DOCTYPE html><html><body>socket workflow</body></html>")

    @app.websocket("/", dependencies=[append_dependency("index")])
    async def dependency_index(websocket: WebSocket, dependencies: DependencyList):
        await websocket.accept()
        await websocket.send_text(json.dumps(dependencies))
        await websocket.close()

    router = APIRouter(dependencies=[append_dependency("router")])
    prefix_router = APIRouter(dependencies=[append_dependency("prefix-router")])

    @router.websocket("/router", dependencies=[append_dependency("router-index")])
    async def router_index(websocket: WebSocket, dependencies: DependencyList):
        await websocket.accept()
        await websocket.send_text(json.dumps(dependencies))
        await websocket.close()

    @prefix_router.websocket("/", dependencies=[append_dependency("prefix-index")])
    async def prefix_index(websocket: WebSocket, dependencies: DependencyList):
        await websocket.accept()
        await websocket.send_text(json.dumps(dependencies))
        await websocket.close()

    app.include_router(router, dependencies=[append_dependency("router-include")])
    app.include_router(
        prefix_router,
        prefix="/prefix",
        dependencies=[append_dependency("prefix-include")],
    )

    @app.websocket("/ws")
    async def echo_socket(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_text()
                await websocket.send_text(f"Message text was: {message}")
        except WebSocketDisconnect:
            return

    async def cookie_or_token(
        session: str | None = Cookie(default=None),
        token: str | None = Query(default=None),
    ):
        if session is None and token is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        return session or token

    @app.websocket("/items/{item_id}/ws")
    async def item_socket(
        websocket: WebSocket,
        item_id: str,
        q: int | None = None,
        credential: str = Depends(cookie_or_token),
    ):
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_text()
                await websocket.send_text(f"Credential: {credential}")
                if q is not None:
                    await websocket.send_text(f"Query q: {q}")
                await websocket.send_text(f"Message: {message}, item: {item_id}")
        except WebSocketDisconnect:
            return

    return app
