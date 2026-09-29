"""Focused HEAD dispatch cases without router or dependency features."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def get_item(item_id: str):
        return {"selected": "get", "item_id": item_id}

    @app.head("/items/{item_id}")
    async def head_item(item_id: str):
        return {"selected": "head", "item_id": item_id}

    @app.get("/headless/{item_id}")
    async def get_only_item(item_id: str):
        return {"selected": "get-only", "item_id": item_id}

    return app
