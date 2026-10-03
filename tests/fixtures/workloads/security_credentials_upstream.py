"""Independently authored credentials workload for upstream security behavior."""

from typing import Annotated

from fastapi import FastAPI, Request, Security
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.responses import JSONResponse
from fastapi.security import (
    APIKeyCookie,
    APIKeyHeader,
    APIKeyQuery,
    HTTPBasic,
    HTTPBearer,
)
from fastapi.security.base import SecurityBase
from fastapi.security.http import (
    HTTPAuthorizationCredentials,
    HTTPBase,
    HTTPBasicCredentials,
)


class CustomHeaderSecurity(SecurityBase):
    def __init__(self) -> None:
        self.model = APIKey(**{"in": APIKeyIn.header}, name="x-custom-security-key")
        self.scheme_name = "CustomHeaderSecurity"

    async def __call__(self, request: Request) -> str | None:
        return request.headers.get("x-custom-security-key")


def _optional_user(value: str | None) -> dict[str, str]:
    if value is None:
        return {"msg": "Create an account first"}
    return {"username": value}


def create_app() -> FastAPI:
    app = FastAPI()

    cookie_required = APIKeyCookie(name="key")
    cookie_optional = APIKeyCookie(name="key", auto_error=False, scheme_name="OptionalCookieKey")
    cookie_described = APIKeyCookie(
        name="key",
        description="Cookie API key",
        scheme_name="DescribedCookieKey",
    )

    @app.get("/api-key/cookie")
    async def read_cookie_key(
        key: Annotated[str, Security(cookie_required)],
    ) -> dict[str, str]:
        return {"username": key}

    @app.get("/api-key/cookie-optional")
    async def read_optional_cookie_key(
        key: Annotated[str | None, Security(cookie_optional)],
    ) -> dict[str, str]:
        return _optional_user(key)

    @app.get("/api-key/cookie-described")
    async def read_described_cookie_key(
        key: Annotated[str, Security(cookie_described)],
    ) -> dict[str, str]:
        return {"username": key}

    query_required = APIKeyQuery(name="key")
    query_optional = APIKeyQuery(name="key", auto_error=False, scheme_name="OptionalQueryKey")
    query_described = APIKeyQuery(
        name="key",
        description="Query API key",
        scheme_name="DescribedQueryKey",
    )

    @app.get("/api-key/query")
    async def read_query_key(
        key: Annotated[str, Security(query_required)],
    ) -> dict[str, str]:
        return {"username": key}

    @app.get("/api-key/query-optional")
    async def read_optional_query_key(
        key: Annotated[str | None, Security(query_optional)],
    ) -> dict[str, str]:
        return _optional_user(key)

    @app.get("/api-key/query-described")
    async def read_described_query_key(
        key: Annotated[str, Security(query_described)],
    ) -> dict[str, str]:
        return {"username": key}

    header_described = APIKeyHeader(
        name="key",
        description="An API Key Header",
    )

    @app.get("/api-key/header-described")
    async def read_described_header_key(
        key: Annotated[str, Security(header_described)],
    ) -> dict[str, str]:
        return {"username": key}

    custom_security = CustomHeaderSecurity()

    @app.get("/api-key/custom-security-base")
    async def read_custom_security_key(
        key: Annotated[str | None, Security(custom_security)],
    ) -> dict[str, str | None]:
        return {"username": key}

    basic_optional = HTTPBasic(auto_error=False, scheme_name="OptionalHTTPBasic")

    @app.get("/http/basic-optional")
    async def read_optional_basic(
        credentials: Annotated[HTTPBasicCredentials | None, Security(basic_optional)],
    ) -> dict[str, str]:
        if credentials is None:
            return _optional_user(None)
        return {"username": credentials.username, "password": credentials.password}

    basic_realm = HTTPBasic(realm="simple", description="HTTPBasic scheme")

    @app.get("/http/basic-realm-description")
    async def read_basic_realm(
        credentials: Annotated[HTTPBasicCredentials, Security(basic_realm)],
    ) -> dict[str, str]:
        return {"username": credentials.username, "password": credentials.password}

    bearer_required = HTTPBearer()

    @app.get("/http/bearer")
    async def read_bearer(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer_required)],
    ) -> dict[str, str]:
        return {
            "scheme": credentials.scheme,
            "credentials": credentials.credentials,
        }

    bearer_optional = HTTPBearer(auto_error=False, scheme_name="OptionalHTTPBearer")

    @app.get("/http/bearer-optional")
    async def read_optional_bearer(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_optional)],
    ) -> dict[str, str]:
        if credentials is None:
            return _optional_user(None)
        return {
            "scheme": credentials.scheme,
            "credentials": credentials.credentials,
        }

    bearer_described = HTTPBearer(
        description="HTTP Bearer token scheme",
        scheme_name="DescribedHTTPBearer",
    )

    @app.get("/http/bearer-described")
    async def read_described_bearer(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer_described)],
    ) -> dict[str, str]:
        return {
            "scheme": credentials.scheme,
            "credentials": credentials.credentials,
        }

    http_base_optional = HTTPBase(scheme="Other", auto_error=False, scheme_name="OptionalHTTPBase")

    @app.get("/http/base-optional")
    async def read_optional_http_base(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Security(http_base_optional)],
    ) -> dict[str, str]:
        if credentials is None:
            return _optional_user(None)
        return {
            "scheme": credentials.scheme,
            "credentials": credentials.credentials,
        }

    return app


def create_exception_boundary_app() -> FastAPI:
    app = FastAPI()

    @app.exception_handler(FastAPIHTTPException)
    async def handle_fastapi_http_exception(
        request: Request, exc: FastAPIHTTPException
    ) -> JSONResponse:
        return JSONResponse({"handler": "fastapi-http-exception"}, status_code=418)

    exception_boundary_key = APIKeyHeader(
        name="exception-key",
        scheme_name="ExceptionBoundaryKey",
    )

    @app.get("/api-key/exception-boundary")
    async def read_exception_boundary_key(
        key: Annotated[str, Security(exception_boundary_key)],
    ) -> dict[str, str]:
        return {"username": key}

    return app
