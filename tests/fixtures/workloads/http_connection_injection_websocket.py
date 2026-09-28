from typing import Annotated

from fastapi import Depends, FastAPI, WebSocket
from fastapi.requests import HTTPConnection


async def read_connection_marker(connection: HTTPConnection) -> int:
    return connection.app.state.marker


def create_app() -> FastAPI:
    app = FastAPI()
    app.state.marker = 91

    @app.websocket("/state-stream")
    async def send_connection_marker(
        websocket: WebSocket,
        marker: Annotated[int, Depends(read_connection_marker)],
    ) -> None:
        await websocket.accept()
        await websocket.send_json(marker)
        await websocket.close()

    return app
