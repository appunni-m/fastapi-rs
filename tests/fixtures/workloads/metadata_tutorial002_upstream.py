"""App for the metadata tutorial's top-level OpenAPI URL case."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(openapi_url="/api/v1/openapi.json")

    @app.get("/items/")
    async def read_items() -> list[dict[str, str]]:
        return [{"name": "Foo"}]

    return app
