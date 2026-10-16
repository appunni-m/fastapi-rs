"""Input-only workload for prefixed APIRouter constructor routes."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket


async def read_items(_request: Request) -> PlainTextResponse:
    return PlainTextResponse("items from constructor route")


async def connect_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_text("socket from constructor route")
    await websocket.close(code=4100, reason="constructor route complete")


def create_app() -> FastAPI:
    leaf_router = APIRouter(
        routes=[
            Route("/items", read_items, methods=["GET"]),
            WebSocketRoute("/socket", connect_socket, name="constructor-socket"),
        ]
    )
    router = APIRouter()
    router.include_router(leaf_router)
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app
