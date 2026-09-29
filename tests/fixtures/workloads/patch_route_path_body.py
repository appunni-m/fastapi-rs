"""Focused PATCH workload for path dispatch and Pydantic body parsing."""

from fastapi import FastAPI
from pydantic import BaseModel


class ItemPatch(BaseModel):
    name: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.patch("/items/{item_id}")
    def patch_item(item_id: str, item: ItemPatch):
        return {"item_id": item_id, "item": item}

    return app
