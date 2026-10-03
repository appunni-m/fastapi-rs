"""Independent WebSocket request-validation handler stimuli."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, WebSocket
from fastapi.exceptions import WebSocketRequestValidationError


async def required_header_dependency(x_missing: Annotated[str, Header()]) -> None:
    del x_missing


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()

    if factory_input.get("custom_validation_handler", False):

        @app.exception_handler(WebSocketRequestValidationError)
        async def websocket_validation_handler(
            websocket: WebSocket, exception: WebSocketRequestValidationError
        ) -> None:
            del exception
            await websocket.close(code=1002, reason="foo")

    @app.websocket("/depends-validate/")
    async def dependency_validation_endpoint(
        websocket: WebSocket,
        _dependency: None = Depends(required_header_dependency),
    ) -> None:
        del websocket, _dependency

    @app.websocket("/ws/{item_id}")
    async def path_validation_endpoint(websocket: WebSocket, item_id: int) -> None:
        await websocket.accept()
        await websocket.send_text(f"Item: {item_id}")
        await websocket.close()

    return app
