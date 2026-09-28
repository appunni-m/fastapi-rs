"""Independent text-exchange workload from the FastAPI WebSocket tutorial."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()

    @app.websocket("/ws")
    async def echo(websocket: WebSocket) -> None:
        await websocket.accept()
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {message}")

    return app
