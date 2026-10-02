"""Input workload for FastAPI root re-export identity relations."""

from __future__ import annotations

import json

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Security,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    applications,
    background,
    datastructures,
    exceptions,
    param_functions,
    requests,
    responses,
    routing,
    status,
    websockets,
)
from starlette import status as starlette_status
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from starlette.websockets import WebSocket as StarletteWebSocket
from starlette.websockets import WebSocketDisconnect as StarletteWebSocketDisconnect


def _http_identity_relations() -> dict[str, dict[str, bool]]:
    return {
        "root_to_public_module": {
            "FastAPI": FastAPI is applications.FastAPI,
            "BackgroundTasks": BackgroundTasks is background.BackgroundTasks,
            "UploadFile": UploadFile is datastructures.UploadFile,
            "HTTPException": HTTPException is exceptions.HTTPException,
            "WebSocketException": WebSocketException is exceptions.WebSocketException,
            "Body": Body is param_functions.Body,
            "Cookie": Cookie is param_functions.Cookie,
            "Depends": Depends is param_functions.Depends,
            "File": File is param_functions.File,
            "Form": Form is param_functions.Form,
            "Header": Header is param_functions.Header,
            "Path": Path is param_functions.Path,
            "Query": Query is param_functions.Query,
            "Security": Security is param_functions.Security,
            "Request": Request is requests.Request,
            "Response": Response is responses.Response,
            "APIRouter": APIRouter is routing.APIRouter,
        },
        "root_to_starlette_module": {
            "status": status is starlette_status,
            "Request": Request is StarletteRequest,
            "Response": Response is StarletteResponse,
        },
        "public_module_to_starlette": {
            "Request": requests.Request is StarletteRequest,
            "Response": responses.Response is StarletteResponse,
        },
    }


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/identity")
    def read_http_identity_relations() -> dict[str, dict[str, bool]]:
        return _http_identity_relations()

    @app.websocket("/identity")
    async def read_websocket_identity_relations(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.receive_text()
        await websocket.send_text(
            json.dumps(
                {
                    "root_to_public_module": {
                        "WebSocket": WebSocket is websockets.WebSocket,
                        "WebSocketDisconnect": (
                            WebSocketDisconnect is websockets.WebSocketDisconnect
                        ),
                    },
                    "root_to_starlette_module": {
                        "WebSocket": WebSocket is StarletteWebSocket,
                        "WebSocketDisconnect": (
                            WebSocketDisconnect is StarletteWebSocketDisconnect
                        ),
                    },
                    "public_module_to_starlette": {
                        "WebSocket": websockets.WebSocket is StarletteWebSocket,
                        "WebSocketDisconnect": (
                            websockets.WebSocketDisconnect is StarletteWebSocketDisconnect
                        ),
                    },
                },
                sort_keys=True,
            )
        )
        await websocket.close()

    return app
