"""Independent APIRouter WebSocket routing, dependency, and error workload."""

from __future__ import annotations

import functools
from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, Header, WebSocket
from fastapi.middleware import Middleware


class CustomError(Exception):
    """Application exception handled by a WebSocket close handler."""


async def websocket_dependency() -> str:
    return "Socket Dependency"


async def websocket_dependency_override() -> str:
    return "Override"


async def websocket_error_dependency() -> None:
    raise NotImplementedError()


async def websocket_validation_dependency(x_missing: Annotated[str, Header()]) -> None:
    del x_missing


def websocket_middleware(middleware_func: Any) -> Any:
    """Wrap an ASGI app with the Starlette-style WebSocket middleware protocol."""

    def middleware_constructor(app: Any) -> Any:
        @functools.wraps(app)
        async def wrapped_app(scope: Any, receive: Any, send: Any) -> Any:
            if scope["type"] != "websocket":
                return await app(scope, receive, send)

            async def call_next() -> Any:
                return await app(scope, receive, send)

            websocket = WebSocket(scope, receive=receive, send=send)
            return await middleware_func(websocket, call_next)

        return wrapped_app

    return middleware_constructor


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    """Create the route matrix and selected dependency/error configuration."""

    middleware = []
    middleware_mode = factory_input.get("middleware_mode")
    if middleware_mode == "catch_validation_error":

        async def validation_catcher(websocket: WebSocket, call_next: Any) -> None:
            del websocket
            try:
                await call_next()
            except Exception:
                event_trace.append("validation-error-caught")
                raise

        middleware = [Middleware(websocket_middleware(validation_catcher))]
    elif middleware_mode == "catch_dependency_error":

        async def error_handler(websocket: WebSocket, call_next: Any) -> None:
            try:
                await call_next()
            except Exception as exc:
                await websocket.close(code=1006, reason=repr(exc))

        middleware = [Middleware(websocket_middleware(error_handler))]

    exception_handlers = {}
    if factory_input.get("custom_error_handler"):

        async def custom_error_handler(websocket: WebSocket, exc: CustomError) -> None:
            del exc
            await websocket.close(1002, "foo")

        exception_handlers[CustomError] = custom_error_handler

    app = FastAPI(
        middleware=middleware,
        exception_handlers=exception_handlers,
    )
    if factory_input.get("dependency_override"):
        app.dependency_overrides[websocket_dependency] = websocket_dependency_override
    router = APIRouter()
    prefix_router = APIRouter()
    native_prefix_router = APIRouter(prefix="/native")

    @app.websocket_route("/")
    async def index(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("Hello, world!")
        await websocket.close()

    @router.websocket_route("/router")
    async def router_index(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("Hello, router!")
        await websocket.close()

    @prefix_router.websocket_route("/")
    async def router_prefix_index(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("Hello, router with prefix!")
        await websocket.close()

    @router.websocket("/router2")
    async def router_index_decorator(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("Hello, router!")
        await websocket.close()

    @router.websocket("/router/{pathparam:path}")
    async def router_index_params(websocket: WebSocket, pathparam: str, queryparam: str) -> None:
        await websocket.accept()
        await websocket.send_text(pathparam)
        await websocket.send_text(queryparam)
        await websocket.close()

    @router.websocket("/router-ws-depends/")
    async def router_websocket_dependency(
        websocket: WebSocket,
        data: str = Depends(websocket_dependency),
    ) -> None:
        await websocket.accept()
        await websocket.send_text(data)
        await websocket.close()

    @native_prefix_router.websocket("/")
    async def native_prefix_websocket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("Hello, router with native prefix!")
        await websocket.close()

    @router.websocket("/depends-err/")
    async def websocket_dependency_error(
        websocket: WebSocket,
        data: None = Depends(websocket_error_dependency),
    ) -> None:
        del websocket, data

    @router.websocket("/depends-validate/")
    async def websocket_dependency_validation(
        websocket: WebSocket,
        data: None = Depends(websocket_validation_dependency),
    ) -> None:
        del websocket, data

    @router.websocket("/custom_error/")
    async def websocket_custom_error(websocket: WebSocket) -> None:
        del websocket
        raise CustomError()

    app.include_router(router)
    app.include_router(prefix_router, prefix="/prefix")
    app.include_router(native_prefix_router)
    return app
