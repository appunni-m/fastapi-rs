"""Independent ASGI workload for FastAPI 0.157 alias-choice integration."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Body, Cookie, FastAPI, Header, Path, Query, Security, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.sse import EventSourceResponse
from pydantic import AliasChoices

bearer = HTTPBearer()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query")
    def read_query(
        value: Annotated[int, Query(validation_alias=AliasChoices("first", "second"))],
    ) -> int:
        return value

    @app.post("/body")
    def read_body(
        value: Annotated[int, Body(embed=True, validation_alias=AliasChoices("first", "second"))],
    ) -> int:
        return value

    @app.get("/header")
    def read_header(
        value: Annotated[
            int,
            Header(alias="ignored", validation_alias=AliasChoices("X-First", "X-Second")),
        ],
    ) -> int:
        return value

    @app.get("/cookie")
    def read_cookie(
        value: Annotated[
            int,
            Cookie(validation_alias=AliasChoices("session", "legacy_session")),
        ],
    ) -> int:
        return value

    @app.get("/path/{item_id}")
    def read_path(
        item_id: Annotated[int, Path(validation_alias=AliasChoices("item_id", "legacy_id"))],
    ) -> int:
        return item_id

    @app.websocket("/ws")
    async def read_websocket(
        websocket: WebSocket,
        credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer)],
    ) -> None:
        await websocket.accept()
        await websocket.send_json(
            {"scheme": credentials.scheme, "credentials": credentials.credentials}
        )
        await websocket.close()

    @app.get("/stream", response_class=EventSourceResponse)
    async def stream_non_finite_values() -> AsyncIterator[float]:
        for value in (float("nan"), float("inf"), float("-inf")):
            yield value

    return app
