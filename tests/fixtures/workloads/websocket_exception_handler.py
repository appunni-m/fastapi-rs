"""Independent custom WebSocketException handler stimulus."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketException


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    app = FastAPI()
    endpoint_websockets: list[WebSocket] = []

    @app.exception_handler(WebSocketException)
    async def websocket_exception_handler(
        websocket: WebSocket, exception: WebSocketException
    ) -> None:
        endpoint_websocket = endpoint_websockets[0]
        event_trace.append(f"same-endpoint-websocket:{websocket is endpoint_websocket}")
        event_trace.append(
            f"handler-state:{websocket.client_state.name}:{websocket.application_state.name}"
        )
        event_trace.append(f"exception:{exception.code}:{exception.reason}")
        await websocket.close(
            code=factory_input["handler_close_code"],
            reason=factory_input["handler_close_reason"],
        )
        event_trace.append(
            "endpoint-state-after-handler:"
            f"{endpoint_websocket.client_state.name}:"
            f"{endpoint_websocket.application_state.name}"
        )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        endpoint_websockets.append(websocket)
        await websocket.accept()
        event_trace.append(
            f"endpoint-state-after-accept:{websocket.client_state.name}:"
            f"{websocket.application_state.name}"
        )
        raise WebSocketException(
            code=factory_input["endpoint_code"],
            reason=factory_input["endpoint_reason"],
        )

    return app
