"""Independent app exercising the public Query default as a query parameter."""

from __future__ import annotations

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    def read_items(q: str | None = Query(default=None)) -> dict[str, str | None]:
        return {"q": q}

    return app
