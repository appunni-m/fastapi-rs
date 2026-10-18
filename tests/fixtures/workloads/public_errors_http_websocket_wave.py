"""Independent HTTP and WebSocket exception stimuli for the public error surface."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketException
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
    WebSocketException as StarletteWebSocketException,
)


def _exception_snapshot(exception: Exception) -> dict[str, object]:
    exception_type = type(exception)
    return {
        "class_module": exception_type.__module__,
        "class_qualname": exception_type.__qualname__,
        "mro": [
            f"{class_type.__module__}.{class_type.__qualname__}"
            for class_type in exception_type.__mro__
        ],
        "args": list(exception.args),
        "message": str(exception),
    }


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

    @app.get("/errors/informational")
    async def informational_http_error() -> None:
        raise HTTPException(
            status_code=199,
            detail="Informational responses do not carry a body.",
            headers={"X-Failure-Origin": "informational"},
        )

    @app.get("/errors/reset-content")
    async def reset_content_http_error() -> None:
        raise HTTPException(
            status_code=205,
            detail="Reset-content responses do not carry a body.",
            headers={"X-Failure-Origin": "reset-content"},
        )

    @app.get("/errors/not-modified")
    async def not_modified_http_error() -> None:
        raise HTTPException(
            status_code=304,
            detail="Not-modified responses do not carry a body.",
            headers={"X-Failure-Origin": "not-modified"},
        )

    @app.get("/errors/numeric-string-status")
    async def numeric_string_status_error() -> None:
        raise HTTPException(
            status_code="204",
            detail="Status values are not normalized by the exception constructor.",
        )

    @app.get("/errors/http-constructor-state")
    async def http_exception_constructor_state() -> dict[str, object]:
        exception = HTTPException(
            status_code=422,
            detail={"field": "display_name", "problems": ["empty", "too_short"]},
            headers={"X-Exception-Owner": "fastapi"},
        )
        return {
            **_exception_snapshot(exception),
            "is_starlette_http_exception": isinstance(exception, StarletteHTTPException),
            "status_code": exception.status_code,
            "detail": exception.detail,
            "headers": exception.headers,
        }

    @app.get("/errors/websocket-constructor-state")
    async def websocket_exception_constructor_state() -> dict[str, object]:
        exception = WebSocketException(code=1008, reason="credentials required")
        return {
            **_exception_snapshot(exception),
            "is_starlette_websocket_exception": isinstance(
                exception, StarletteWebSocketException
            ),
            "code": exception.code,
            "reason": exception.reason,
        }

    @app.websocket("/errors/websocket")
    async def websocket_policy_error(websocket: WebSocket) -> None:
        del websocket
        raise WebSocketException(code=1008, reason="credentials required")

    return app
