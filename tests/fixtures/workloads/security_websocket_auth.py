"""Independent FastAPI workload for required and optional WebSocket auth."""

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import FastAPI, Security, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    if factory_input or event_trace:
        raise ValueError("the security WebSocket workload takes no factory input or setup events")
    app = FastAPI()
    required_bearer = HTTPBearer()
    optional_bearer = HTTPBearer(auto_error=False)

    @app.websocket("/ws-required")
    async def required_credentials(
        websocket: WebSocket,
        credentials: Annotated[HTTPAuthorizationCredentials, Security(required_bearer)],
    ) -> None:
        await websocket.accept()
        await websocket.send_json(jsonable_encoder(credentials))
        await websocket.close()

    @app.websocket("/ws-optional")
    async def optional_credentials(
        websocket: WebSocket,
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Security(optional_bearer),
        ],
    ) -> None:
        await websocket.accept()
        await websocket.send_json(jsonable_encoder(credentials))
        await websocket.close()

    return app
