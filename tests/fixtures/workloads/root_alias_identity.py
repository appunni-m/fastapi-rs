"""Input workload for FastAPI root re-export identity relations."""

from __future__ import annotations

import json

import fastapi.middleware.cors as fastapi_cors
import fastapi.middleware.gzip as fastapi_gzip
import fastapi.middleware.httpsredirect as fastapi_httpsredirect
import fastapi.middleware.trustedhost as fastapi_trustedhost
import fastapi.middleware.wsgi as fastapi_wsgi
import fastapi.staticfiles as fastapi_staticfiles
import starlette.datastructures as starlette_datastructures
import starlette.middleware.cors as starlette_cors
import starlette.middleware.gzip as starlette_gzip
import starlette.middleware.httpsredirect as starlette_httpsredirect
import starlette.middleware.trustedhost as starlette_trustedhost
import starlette.middleware.wsgi as starlette_wsgi
import starlette.requests as starlette_requests
import starlette.responses as starlette_responses
import starlette.staticfiles as starlette_staticfiles
import starlette.websockets as starlette_websockets
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
            "Request": Request is starlette_requests.Request,
            "Response": Response is starlette_responses.Response,
        },
        "public_module_to_starlette": {
            "Address": datastructures.Address is starlette_datastructures.Address,
            "CORSMiddleware": (fastapi_cors.CORSMiddleware is starlette_cors.CORSMiddleware),
            "FileResponse": responses.FileResponse is starlette_responses.FileResponse,
            "FormData": datastructures.FormData is starlette_datastructures.FormData,
            "GZipMiddleware": fastapi_gzip.GZipMiddleware is starlette_gzip.GZipMiddleware,
            "HTMLResponse": responses.HTMLResponse is starlette_responses.HTMLResponse,
            "Headers": datastructures.Headers is starlette_datastructures.Headers,
            "HTTPConnection": (requests.HTTPConnection is starlette_requests.HTTPConnection),
            "HTTPSRedirectMiddleware": (
                fastapi_httpsredirect.HTTPSRedirectMiddleware
                is starlette_httpsredirect.HTTPSRedirectMiddleware
            ),
            "JSONResponse": responses.JSONResponse is starlette_responses.JSONResponse,
            "PlainTextResponse": (
                responses.PlainTextResponse is starlette_responses.PlainTextResponse
            ),
            "QueryParams": datastructures.QueryParams is starlette_datastructures.QueryParams,
            "RedirectResponse": (
                responses.RedirectResponse is starlette_responses.RedirectResponse
            ),
            "Request": requests.Request is starlette_requests.Request,
            "Response": responses.Response is starlette_responses.Response,
            "State": datastructures.State is starlette_datastructures.State,
            "StaticFiles": (fastapi_staticfiles.StaticFiles is starlette_staticfiles.StaticFiles),
            "StreamingResponse": (
                responses.StreamingResponse is starlette_responses.StreamingResponse
            ),
            "TrustedHostMiddleware": (
                fastapi_trustedhost.TrustedHostMiddleware
                is starlette_trustedhost.TrustedHostMiddleware
            ),
            "URL": datastructures.URL is starlette_datastructures.URL,
            "WSGIMiddleware": fastapi_wsgi.WSGIMiddleware is starlette_wsgi.WSGIMiddleware,
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
                        "WebSocket": WebSocket is starlette_websockets.WebSocket,
                        "WebSocketDisconnect": (
                            WebSocketDisconnect is starlette_websockets.WebSocketDisconnect
                        ),
                    },
                    "public_module_to_starlette": {
                        "WebSocket": (websockets.WebSocket is starlette_websockets.WebSocket),
                        "WebSocketDisconnect": (
                            websockets.WebSocketDisconnect
                            is starlette_websockets.WebSocketDisconnect
                        ),
                        "WebSocketState": (
                            websockets.WebSocketState is starlette_websockets.WebSocketState
                        ),
                    },
                },
                sort_keys=True,
            )
        )
        await websocket.close()

    return app
