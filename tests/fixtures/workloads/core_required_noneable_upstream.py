"""Input-only routes for required, nullable query and embedded body fields."""

from __future__ import annotations

from fastapi import Body, FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query")
    def required_query(value: str | None) -> str | None:
        return value

    @app.get("/explicit-query")
    def explicit_required_query(value: str | None = Query()) -> str | None:
        return value

    @app.post("/body-embed")
    def required_embedded_body(value: str | None = Body(embed=True)) -> str | None:
        return value

    return app
