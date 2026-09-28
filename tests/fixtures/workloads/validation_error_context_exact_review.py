"""Endpoint-context validation errors exposed at the ASGI exception boundary."""

from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import (
    RequestValidationError,
    ResponseValidationError,
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


def create_app() -> FastAPI:
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

    return app
