"""Input-only workload for mount ordering around an included WebSocket router."""

from fastapi import APIRouter, FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()
    mounted = FastAPI()
    router = APIRouter()

    @mounted.websocket("/socket")
    async def mounted_socket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.receive_text()
        await websocket.send_text("mounted")
        await websocket.close(code=1000)

    @mounted.get("/http")
    def mounted_http() -> dict[str, str]:
        return {"owner": "mounted"}

    @router.websocket("/{rest:path}")
    async def included_socket(websocket: WebSocket, rest: str) -> None:
        await websocket.accept()
        await websocket.receive_text()
        await websocket.send_text("included")
        await websocket.close(code=1000)

    app.mount("/mounted-first", mounted)
    app.include_router(router)
    app.mount("/native-first", mounted)
    return app
