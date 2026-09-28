"""Independent app route for FastAPI's HTTPStatus enum response code."""

from __future__ import annotations

from http import HTTPStatus

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/enum-status-code", status_code=HTTPStatus.CREATED)
    def get_enum_status_code() -> str:
        return "foo bar"

    return app
