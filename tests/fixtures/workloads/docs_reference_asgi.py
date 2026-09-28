from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, UploadFile, WebSocket, WebSocketException
from fastapi.requests import HTTPConnection


async def read_connection_state(connection: HTTPConnection) -> int:
    return connection.app.state.value


def create_app() -> FastAPI:
    app = FastAPI()
    app.state.value = 42

    @app.get("/connection")
    async def read_connection(
        value: Annotated[int, Depends(read_connection_state)],
    ) -> int:
        return value

    @app.websocket("/connection/ws")
    async def websocket_connection(
        websocket: WebSocket,
        value: Annotated[int, Depends(read_connection_state)],
    ) -> None:
        await websocket.accept()
        await websocket.send_json(value)
        await websocket.close()

    @app.get("/errors/missing")
    async def raise_http_error() -> None:
        raise HTTPException(
            status_code=410,
            detail="This record is no longer available",
            headers={"X-Error-Source": "reference-workload"},
        )

    @app.websocket("/errors/policy")
    async def raise_websocket_error(websocket: WebSocket) -> None:
        raise WebSocketException(code=1008, reason="policy")

    @app.websocket("/echo")
    async def websocket_echo(websocket: WebSocket) -> None:
        await websocket.accept()
        message = await websocket.receive_text()
        await websocket.send_text(f"received:{message}")
        await websocket.close()

    @app.post("/uploads")
    async def inspect_upload(upload: UploadFile) -> dict[str, object]:
        contents = await upload.read()
        return {
            "filename": upload.filename,
            "content_type": upload.content_type,
            "size": upload.size,
            "text": contents.decode("utf-8"),
        }

    return app
