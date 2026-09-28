"""Independent text-echo WebSocket workload for the FastAPI compatibility lane."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()

    @app.websocket("/ws/echo")
    async def echo(websocket: WebSocket) -> None:
        await websocket.accept()
        message = await websocket.receive_text()
        await websocket.send_text(message.upper())
        await websocket.close()

    @app.websocket("/ws/echo-binary")
    async def echo_binary(websocket: WebSocket) -> None:
        await websocket.accept()
        payload = await websocket.receive_bytes()
        await websocket.send_bytes(payload[::-1])
        await websocket.close()

    return app
