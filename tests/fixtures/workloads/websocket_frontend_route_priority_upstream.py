"""Independent input for FastAPI WebSocket-over-frontend route priority."""

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, WebSocket


def create_app() -> FastAPI:
    frontend_directory = TemporaryDirectory(prefix="fastapi-rs-ws-frontend-")
    (Path(frontend_directory.name) / "ws").write_text("frontend", encoding="utf-8")

    app = FastAPI()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("websocket")
        await websocket.close()

    app.frontend("/", directory=frontend_directory.name)
    app.state.frontend_directory = frontend_directory
    return app
