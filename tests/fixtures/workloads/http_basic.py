"""Small, independently authored HTTP Basic authentication workload."""

from __future__ import annotations

from fastapi import FastAPI, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials


def create_app() -> FastAPI:
    app = FastAPI()
    security = HTTPBasic(realm="simple")

    @app.get("/users/me")
    def read_current_user(
        credentials: HTTPBasicCredentials = Security(security),  # noqa: B008
    ) -> dict[str, str]:
        return {"username": credentials.username, "password": credentials.password}

    return app
