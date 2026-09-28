"""Input workload for the documented WebSocket TestClient example."""

from fastapi import FastAPI
from fastapi.websockets import WebSocket


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def read_main() -> dict[str, str]:
        return {"msg": "Hello World"}

    @app.websocket("/ws")
    async def websocket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json({"msg": "Hello WebSocket"})
        await websocket.close()

    return app
