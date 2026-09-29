"""Focused Annotated integer path-bound workflow from FastAPI's tutorial."""

from typing import Annotated

from fastapi import FastAPI, Path


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: Annotated[int, Path(gt=0)], q: str):
        result = {"item_id": item_id}
        if q:
            result["q"] = q
        return result

    return app
