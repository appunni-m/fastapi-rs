"""Exercise a configured APIRouter ASGI default on unmatched protocols."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter


async def _default_handler(scope: dict[str, Any], _receive: Any, send: Any) -> None:
    if scope["type"] == "http":
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [
                    (b"content-type", b"text/plain; charset=utf-8"),
                    (b"x-router-default", b"hit"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"router miss",
                "more_body": False,
            }
        )
        return

    if scope["type"] == "websocket":
        await send(
            {
                "type": "websocket.close",
                "code": 4404,
                "reason": "router miss",
            }
        )
        return

    raise ValueError(f"unsupported scope type: {scope['type']}")


def create_app(_factory_input: dict[str, Any], _event_trace: list[str]) -> APIRouter:
    router = APIRouter(default=_default_handler)
    return router
