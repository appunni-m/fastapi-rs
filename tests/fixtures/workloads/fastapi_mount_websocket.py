"""Input-only workload for FastAPI-mounted WebSocket applications."""

from fastapi import FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()
    mounted = FastAPI()

    @mounted.websocket("/socket")
    async def mounted_socket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.receive_text()
        await websocket.send_text("mounted")
        await websocket.close(code=1000)

    @mounted.get("/http")
    def mounted_http() -> dict[str, str]:
        return {"owner": "mounted"}

    app.mount("/mounted-first", mounted)

    @app.websocket("/{rest:path}")
    async def native_socket(websocket: WebSocket, rest: str) -> None:
        await websocket.accept()
        await websocket.receive_text()
        await websocket.send_text("native")
        await websocket.close(code=1000)

    @app.get("/{rest:path}")
    def native_http(rest: str) -> dict[str, str]:
        return {"owner": "native"}

    app.mount("/native-first", mounted)
    return app
