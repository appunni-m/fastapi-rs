"""Independent WebSocket request-validation handler stimuli."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, Query, WebSocket
from fastapi.exceptions import WebSocketRequestValidationError


async def required_header_dependency(x_missing: Annotated[str, Header()]) -> None:
    del x_missing


async def required_query_dependency(required_query: Annotated[str, Query()]) -> None:
    del required_query


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    constructor_handler = None
    exception_handlers = None
    if factory_input.get("constructor_validation_handler", False):

        async def constructor_validation_handler(
            websocket: WebSocket, exception: WebSocketRequestValidationError
        ) -> None:
            del exception
            await websocket.close(code=1003, reason="constructor")

        constructor_handler = constructor_validation_handler
        exception_handlers = {WebSocketRequestValidationError: constructor_validation_handler}
    app = FastAPI(exception_handlers=exception_handlers)
    registered_handler = app.exception_handlers.get(WebSocketRequestValidationError)
    event_trace.append(
        "default-websocket-validation-handler-present"
        if registered_handler is not None
        else "default-websocket-validation-handler-missing"
    )
    if constructor_handler is not None:
        event_trace.append(
            "constructor-websocket-validation-handler-registered"
            if registered_handler is constructor_handler
            else "constructor-websocket-validation-handler-not-registered"
        )

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

        event_trace.append(
            "custom-websocket-validation-handler-registered"
            if app.exception_handlers.get(WebSocketRequestValidationError)
            is websocket_validation_handler
            else "custom-websocket-validation-handler-not-registered"
        )

    @app.websocket("/depends-validate/")
    async def dependency_validation_endpoint(
        websocket: WebSocket,
        _dependency: None = Depends(required_header_dependency),
        _lease: None = Depends(websocket_validation_lease),
    ) -> None:
        del websocket, _dependency, _lease

    @app.websocket("/depends-query-validate/")
    async def query_dependency_validation_endpoint(
        websocket: WebSocket,
        _dependency: None = Depends(required_query_dependency),
        _lease: None = Depends(websocket_validation_lease),
    ) -> None:
        del websocket, _dependency, _lease

    @app.websocket("/ws/{item_id}")
    async def path_validation_endpoint(websocket: WebSocket, item_id: int) -> None:
        await websocket.accept()
        await websocket.send_text(f"Item: {item_id}")
        await websocket.close()

    return app
