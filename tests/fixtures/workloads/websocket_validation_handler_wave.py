"""Independent WebSocket request-validation handler stimuli."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, WebSocket
from fastapi.exceptions import WebSocketRequestValidationError


async def required_header_dependency(x_missing: Annotated[str, Header()]) -> None:
    del x_missing


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    async def websocket_validation_lease() -> AsyncIterator[None]:
        event_trace.append("validation-lease-enter")
        try:
            yield None
        finally:
            event_trace.append("validation-lease-exit")

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
        _lease: None = Depends(websocket_validation_lease),
    ) -> None:
        del websocket, _dependency, _lease

    @app.websocket("/ws/{item_id}")
    async def path_validation_endpoint(websocket: WebSocket, item_id: int) -> None:
        await websocket.accept()
        await websocket.send_text(f"Item: {item_id}")
        await websocket.close()

    return app
