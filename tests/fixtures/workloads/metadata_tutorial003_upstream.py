"""App for the metadata tutorial's custom Swagger UI and disabled ReDoc case."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(docs_url="/documentation", redoc_url=None)

    @app.get("/items/")
    async def read_items() -> list[dict[str, str]]:
        return [{"name": "Foo"}]

    return app
