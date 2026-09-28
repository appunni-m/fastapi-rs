"""Independent ASGI observations for validation exception context formatting."""

from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import (
    RequestValidationError,
    ResponseValidationError,
    WebSocketRequestValidationError,
)
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel


class Summary(BaseModel):
    identifier: int
    caption: str


def _register_handlers(app: FastAPI) -> None:
    async def request_error(_request: Request, exc: RequestValidationError) -> Response:
        return PlainTextResponse(str(exc), status_code=422)

    async def response_error(_request: Request, exc: ResponseValidationError) -> Response:
        return PlainTextResponse(str(exc), status_code=500)

    async def websocket_error(_: WebSocket, exc: WebSocketRequestValidationError) -> None:
        raise exc

    app.exception_handler(RequestValidationError)(request_error)
    app.exception_handler(ResponseValidationError)(response_error)
    app.exception_handler(WebSocketRequestValidationError)(websocket_error)


def create_app() -> FastAPI:
    app = FastAPI()
    sub_app = FastAPI()
    _register_handlers(app)
    _register_handlers(sub_app)
    app.mount("/mounted", sub_app)

    @app.get("/members/{member_id}")
    async def read_member(member_id: int) -> dict[str, int]:
        return {"member_id": member_id}

    @app.get("/summary", response_model=Summary)
    async def read_summary() -> dict[str, object]:
        return {"identifier": 12}

    @sub_app.get("/members/{member_id}")
    async def read_mounted_member(member_id: int) -> dict[str, int]:
        return {"member_id": member_id}

    @app.websocket("/socket/{socket_id}")
    async def read_socket(websocket: WebSocket, socket_id: int) -> None:
        await websocket.accept()

    @sub_app.websocket("/socket/{socket_id}")
    async def read_mounted_socket(websocket: WebSocket, socket_id: int) -> None:
        await websocket.accept()

    @app.get("/diagnostics/path-only")
    async def render_path_context() -> PlainTextResponse:
        error = RequestValidationError(
            [{"type": "missing", "loc": ("payload", "title"), "msg": "Field required"}],
            endpoint_ctx={"path": "POST /diagnostics/constructed"},
        )
        return PlainTextResponse(str(error))

    @app.get("/diagnostics/empty-context")
    async def render_empty_context() -> PlainTextResponse:
        error = RequestValidationError(
            [{"type": "missing", "loc": ("payload", "title"), "msg": "Field required"}],
            endpoint_ctx={},
        )
        return PlainTextResponse(str(error))

    return app
