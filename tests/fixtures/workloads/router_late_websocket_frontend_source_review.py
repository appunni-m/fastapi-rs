"""Independent ASGI stimuli for routes added after router inclusion."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, WebSocket


def _included_marker(calls: list[str]) -> str:
    calls.append("included")
    return "include-dependency"


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one late-route scenario from public FastAPI APIs."""
    del event_trace
    scenario = factory_input["scenario"]
    app = FastAPI()

    if scenario == "late-api-websocket":
        dependency_calls: list[str] = []

        def included_dependency() -> str:
            return _included_marker(dependency_calls)

        router = APIRouter(prefix="/v1")
        app.include_router(
            router,
            prefix="/mount",
            dependencies=[Depends(included_dependency)],
        )

        @router.websocket("/ws-api")
        async def api_websocket(
            websocket: WebSocket,
            channel: str,
        ) -> None:
            await websocket.accept()
            message = await websocket.receive_text()
            route_path = websocket.scope["route"].path
            await websocket.send_text(
                f"api:{channel}:{len(dependency_calls)}:{message}:{route_path}"
            )
            await websocket.close(code=4101, reason="api route complete")

        return app

    if scenario == "late-raw-websocket":
        router = APIRouter()
        app.include_router(router, prefix="/wire")

        async def raw_websocket(websocket: WebSocket) -> None:
            await websocket.accept()
            message = await websocket.receive_text()
            token = websocket.query_params["token"]
            await websocket.send_text(f"raw:{token}:{message}")
            await websocket.close(code=4102, reason="raw route complete")

        router.add_websocket_route("/raw", raw_websocket)
        return app

    if scenario == "late-frontend":
        router = APIRouter(prefix="/v2")
        app.include_router(router, prefix="/panel")

        directory = TemporaryDirectory(prefix="fastapi-late-frontend-")
        app.state.late_frontend_directory = directory
        root = Path(directory.name)
        index = root / "index.html"
        index.write_bytes(b"late frontend shell\n")
        os.utime(index, (1_700_000_000, 1_700_000_000))
        router.frontend("/site", directory=root, fallback="index.html")
        return app

    if scenario == "nested-late-api-websocket":
        parent_router = APIRouter()
        child_router = APIRouter()
        app.include_router(parent_router, prefix="/root")
        parent_router.include_router(child_router, prefix="/child")

        async def nested_websocket(websocket: WebSocket) -> None:
            await websocket.accept()
            message = await websocket.receive_text()
            await websocket.send_text(f"nested:{message}")
            await websocket.close(code=4103, reason="nested route complete")

        child_router.add_api_websocket_route("/nested", nested_websocket)
        return app

    raise ValueError(f"unknown route scenario: {scenario}")
