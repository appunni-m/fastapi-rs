"""Independent inputs for uncovered HTTP authentication behavior."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Security
from fastapi.security import HTTPDigest, OAuth2
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBase


def create_app() -> FastAPI:
    app = FastAPI()

    base = HTTPBase(scheme="Other")
    digest = HTTPDigest()
    optional_digest = HTTPDigest(auto_error=False)
    oauth2 = OAuth2(
        flows={
            "password": {
                "tokenUrl": "token",
                "scopes": {"read:users": "Read the users", "write:users": "Create users"},
            }
        }
    )
    optional_oauth2 = OAuth2(
        flows={
            "password": {
                "tokenUrl": "token",
                "scopes": {"read:users": "Read the users", "write:users": "Create users"},
            }
        },
        auto_error=False,
    )

    @app.get("/users/me")
    def read_base(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(base)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    @app.get("/digest")
    def read_digest(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(digest)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    @app.get("/digest-optional")
    def read_optional_digest(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Security(optional_digest)],
    ) -> dict[str, str | None]:
        if credentials is None:
            return {"msg": "Create an account first"}
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    @app.get("/oauth2")
    def read_oauth2(authorization: Annotated[str, Security(oauth2)]) -> dict[str, str]:
        return {"username": authorization}

    @app.get("/oauth2-optional")
    def read_optional_oauth2(
        authorization: Annotated[str | None, Security(optional_oauth2)],
    ) -> dict[str, str | None]:
        if authorization is None:
            return {"msg": "Create an account first"}
        return {"username": authorization}

    return app


def create_described_base_app() -> FastAPI:
    app = FastAPI()
    described_base = HTTPBase(scheme="Other", description="Other Security Scheme")

    @app.get("/users/me")
    def read_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Security(described_base)],
    ) -> dict[str, str]:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}

    return app
