"""Independent direct WebSocket scope inputs for FastAPI dependency cleanup."""

from typing import Annotated

from fastapi import Depends, FastAPI, WebSocket


def create_app() -> FastAPI:
    app = FastAPI()
    events: list[str] = []

    def scoped_resource():
        resource = {"open": True}
        try:
            yield resource
        finally:
            resource["open"] = False
            events.append("close:scoped-websocket")

    @app.websocket("/ws/function-scope")
    async def function_scope_socket(
        websocket: WebSocket,
        resource: Annotated[dict[str, bool], Depends(scoped_resource, scope="function")],
    ) -> None:
        await websocket.accept()
        await websocket.send_json({"open_during_handler": resource["open"]})
        await websocket.close()

    @app.websocket("/ws/request-scope")
    async def request_scope_socket(
        websocket: WebSocket,
        resource: Annotated[dict[str, bool], Depends(scoped_resource, scope="request")],
    ) -> None:
        await websocket.accept()
        await websocket.send_json({"open_during_handler": resource["open"]})
        await websocket.close()

    @app.get("/events")
    def read_events() -> dict[str, list[str]]:
        return {"events": list(events)}

    return app
