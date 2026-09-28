"""OpenAPI operation response declarations for documented alternative responses."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class ItemView(BaseModel):
    id: str
    value: str


class NotFoundMessage(BaseModel):
    message: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/media/{item_id}",
        response_model=ItemView,
        responses={
            200: {
                "description": "Metadata or an alternate image representation.",
                "content": {"image/png": {}},
            }
        },
    )
    async def media_item(item_id: str) -> ItemView:
        return ItemView(id=item_id, value="sample")

    @app.get(
        "/documented/{item_id}",
        response_model=ItemView,
        responses={
            404: {"model": NotFoundMessage, "description": "No matching item."},
            200: {
                "description": "Item requested by key.",
                "content": {"application/json": {"example": {"id": "demo", "value": "sample"}}},
            },
        },
    )
    async def documented_item(item_id: str) -> ItemView:
        return ItemView(id=item_id, value="sample")

    @app.get(
        "/status-codes/{item_id}",
        response_model=ItemView,
        responses={
            404: {"description": "No matching item."},
            302: {"description": "The item moved."},
            403: {"description": "Access is restricted."},
            200: {"content": {"image/png": {}}},
        },
    )
    async def item_with_status_docs(item_id: str) -> ItemView:
        return ItemView(id=item_id, value="sample")

    @app.get("/untyped/{key}")
    async def untyped_path(key):
        return {"key": key}

    return app
