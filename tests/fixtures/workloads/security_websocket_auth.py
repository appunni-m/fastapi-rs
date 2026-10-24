"""Independent FastAPI workload for the WebSocket security factory matrix."""

from collections.abc import Mapping
from functools import partial
from typing import Any

from fastapi import FastAPI, Security, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.security import (
    APIKeyCookie,
    APIKeyHeader,
    APIKeyQuery,
    HTTPBasic,
    HTTPBearer,
    HTTPDigest,
    OAuth2,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
    OpenIdConnect,
)
from fastapi.security.http import HTTPBase


_SECURITY_FACTORIES = {
    "http-base": partial(HTTPBase, scheme="Other"),
    "http-basic": HTTPBasic,
    "http-bearer": HTTPBearer,
    "http-digest": HTTPDigest,
    "api-key-query": partial(APIKeyQuery, name="key"),
    "api-key-header": partial(APIKeyHeader, name="key"),
    "api-key-cookie": partial(APIKeyCookie, name="key"),
    "oauth2": OAuth2,
    "oauth2-password-bearer": partial(OAuth2PasswordBearer, tokenUrl="/token"),
    "oauth2-authorization-code-bearer": partial(
        OAuth2AuthorizationCodeBearer,
        authorizationUrl="/authorize",
        tokenUrl="/token",
    ),
    "openid-connect": partial(OpenIdConnect, openIdConnectUrl="/openid"),
}


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    if event_trace:
        raise ValueError("the security WebSocket workload takes no setup events")
    try:
        security_factory = _SECURITY_FACTORIES[factory_input["security_factory"]]
    except KeyError as error:
        raise ValueError("unknown WebSocket security factory") from error

    security = security_factory(auto_error=factory_input["auto_error"])
    app = FastAPI()

    @app.websocket("/")
    async def security_endpoint(websocket: WebSocket, credentials=Security(security)) -> None:
        await websocket.accept()
        await websocket.send_json(jsonable_encoder(credentials))
        await websocket.close()

    return app
