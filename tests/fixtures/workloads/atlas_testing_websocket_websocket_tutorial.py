"""Input-only ASGI workload for WebSocket auth, query, and validation cases."""

from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.responses import HTMLResponse


async def get_cookie_or_token_plain(
    websocket: WebSocket,
    session: str | None = Cookie(default=None),
    token: str | None = Query(default=None),
) -> str:
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


async def get_cookie_or_token_annotated(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
) -> str:
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


def create_app() -> FastAPI:
    app = FastAPI()
    page = "<!DOCTYPE html><html><body>WebSocket Chat</body></html>"

    @app.get("/")
    async def get_page():
        return HTMLResponse(page)

    @app.websocket("/items/{item_id}/ws")
    async def websocket_plain(
        websocket: WebSocket,
        item_id: str,
        q: int | None = None,
        cookie_or_token: str = Depends(get_cookie_or_token_plain),
    ) -> None:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Session cookie or query token value is: {cookie_or_token}")
            if q is not None:
                await websocket.send_text(f"Query parameter q is: {q}")
            await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

    @app.websocket("/annotated/items/{item_id}/ws")
    async def websocket_annotated(
        *,
        websocket: WebSocket,
        item_id: str,
        q: int | None = None,
        cookie_or_token: Annotated[str, Depends(get_cookie_or_token_annotated)],
    ) -> None:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Session cookie or query token value is: {cookie_or_token}")
            if q is not None:
                await websocket.send_text(f"Query parameter q is: {q}")
            await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

    return app
