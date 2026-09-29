"""Cookie parameter extraction, validation, and OpenAPI workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/cookies/required")
    def read_required_cookie(
        session: Annotated[str, Cookie(alias="session-id")],
    ) -> dict[str, str]:
        return {"value": session}

    @app.get("/cookies/optional")
    def read_optional_cookie(
        session: Annotated[str | None, Cookie(alias="session-id")] = None,
    ) -> dict[str, str | None]:
        return {"value": session}

    return app
