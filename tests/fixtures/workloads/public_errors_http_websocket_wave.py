"""Independent HTTP and WebSocket exception stimuli for the public error surface."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketException
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/errors/fastapi")
    async def fastapi_http_error() -> None:
        raise HTTPException(
            status_code=418,
            detail={
                "kind": "invalid_request",
                "field": "display_name",
                "problems": ["empty", "too_short"],
            },
            headers={"X-Failure-Origin": "fastapi"},
        )

    @app.get("/errors/starlette")
    async def starlette_http_error() -> None:
        raise StarletteHTTPException(
            status_code=451,
            detail="This resource is restricted.",
            headers={"X-Failure-Origin": "starlette"},
        )

    @app.get("/errors/bodyless")
    async def bodyless_http_error() -> None:
        raise HTTPException(
            status_code=204,
            detail="This detail should not produce a body.",
            headers={"X-Failure-Origin": "bodyless"},
        )

    @app.websocket("/errors/websocket")
    async def websocket_policy_error(websocket: WebSocket) -> None:
        del websocket
        raise WebSocketException(code=1008, reason="credentials required")

    return app
