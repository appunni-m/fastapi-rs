"""Endpoint-context validation errors exposed at the ASGI exception boundary."""

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, Query, Request, WebSocket
from fastapi.exceptions import (
    RequestValidationError,
    ResponseValidationError,
    ValidationException,
    WebSocketRequestValidationError,
)
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str


def _register_handlers(app: FastAPI) -> None:
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> None:
        raise exc

    async def response_validation_handler(request: Request, exc: ResponseValidationError) -> None:
        raise exc

    async def websocket_validation_handler(
        websocket: WebSocket, exc: WebSocketRequestValidationError
    ) -> None:
        raise exc

    app.exception_handler(RequestValidationError)(request_validation_handler)
    app.exception_handler(ResponseValidationError)(response_validation_handler)
    app.exception_handler(WebSocketRequestValidationError)(websocket_validation_handler)


async def _websocket_context_dependency(
    limit: Annotated[int, Query(gt=0)],
    x_count: Annotated[int, Header(gt=0)],
) -> None:
    del limit, x_count


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    request_constructor = factory_input.get("request_constructor")
    websocket_constructor = factory_input.get("websocket_constructor")
    app = FastAPI()
    sub_app = FastAPI()
    _register_handlers(app)
    _register_handlers(sub_app)
    app.mount(path="/sub", app=sub_app)

    @app.get("/users/{user_id}")
    def get_user(user_id: int):
        return {"user_id": user_id}

    @app.get("/items/", response_model=Item)
    def get_item():
        return {"name": "Widget"}

    @sub_app.get("/items/", response_model=Item)
    def get_sub_item():
        return {"name": "Widget"}

    @app.websocket("/ws/{item_id}")
    async def websocket_endpoint(websocket: WebSocket, item_id: int):
        await websocket.accept()
        await websocket.send_text(f"Item: {item_id}")
        await websocket.close()

    @app.websocket("/ws/context/{item_id}")
    async def websocket_context_endpoint(
        websocket: WebSocket,
        item_id: int,
        _dependency: None = Depends(_websocket_context_dependency),
    ) -> None:
        del websocket, item_id, _dependency

    @sub_app.websocket("/ws/{item_id}")
    async def subapp_websocket_endpoint(websocket: WebSocket, item_id: int):
        await websocket.accept()
        await websocket.send_text(f"Item: {item_id}")
        await websocket.close()

    @app.get("/diagnostics/path-only")
    async def render_path_context() -> PlainTextResponse:
        error = RequestValidationError(
            [{"type": "missing", "loc": ("body", "name"), "msg": "Field required"}],
            endpoint_ctx={"path": "GET /api/test"},
        )
        return PlainTextResponse(str(error))

    @app.get("/diagnostics/empty-context")
    async def render_empty_context() -> PlainTextResponse:
        error = RequestValidationError(
            [{"type": "missing", "loc": ("body", "name"), "msg": "Field required"}],
            endpoint_ctx={},
        )
        return PlainTextResponse(str(error))

    if isinstance(request_constructor, Mapping):

        @app.get("/diagnostics/direct-request-error")
        async def direct_request_error() -> None:
            raise RequestValidationError(
                request_constructor["errors"],
                body=request_constructor["body"],
                endpoint_ctx=request_constructor["endpoint_ctx"],
            )

    if isinstance(websocket_constructor, Mapping):

        @app.websocket("/ws/diagnostics/direct-validation-error")
        async def direct_websocket_error(websocket: WebSocket) -> None:
            del websocket
            raise WebSocketRequestValidationError(
                websocket_constructor["errors"],
                endpoint_ctx=websocket_constructor["endpoint_ctx"],
            )

    base_validation_exception = factory_input.get("base_validation_exception")
    if isinstance(base_validation_exception, Mapping):
        errors = base_validation_exception["errors"]
        if base_validation_exception["sequence_type"] == "tuple":
            errors = tuple(errors)

        @app.get("/diagnostics/base-validation-exception-errors")
        def render_base_validation_exception_errors():
            error = ValidationException(errors)
            returned_errors = error.errors()
            return {
                "errors": returned_errors,
                "same_object": returned_errors is errors,
                "sequence_type": type(returned_errors).__name__,
            }

    return app
