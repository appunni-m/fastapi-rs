"""Independent FastAPI.Security declaration and dependency input."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Security


def get_principal() -> dict[str, str]:
    return {"principal": "demo"}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/scoped")
    def read_scoped(
        principal: Annotated[dict[str, str], Security(get_principal, scopes=["records:read"])],
    ) -> dict[str, str]:
        return principal

    return app
