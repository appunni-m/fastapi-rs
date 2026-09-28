"""Input-only ASGI workload for the WebSocket app-testing tutorial."""

from fastapi import FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/")
    async def read_main():
        return {"msg": "Hello World"}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json({"msg": "Hello WebSocket"})
        await websocket.close()

    return app
