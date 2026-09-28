"""OpenAPI-only event tutorial routes; lifecycle callbacks are not invoked."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: str):
        return {"name": item_id}

    @app.get("/items/")
    async def read_items():
        return [{"name": "Sample"}]

    @app.get("/predict")
    async def predict(x: float):
        return {"result": x * 2}

    return app
