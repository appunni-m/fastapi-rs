"""Independent nested request-body, multi-body, and partial-update routes."""

from __future__ import annotations

from fastapi import Body, FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field


class Image(BaseModel):
    url: str
    name: str


class NestedItem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = Field(default_factory=set)
    image: Image | None = None


class BundleItem(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


class BundleUser(BaseModel):
    username: str
    full_name: str | None = None


class EditableItem(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = Field(default_factory=list)


_INITIAL_ITEMS = {
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


def create_app() -> FastAPI:
    app = FastAPI()
    items = {key: value.copy() for key, value in _INITIAL_ITEMS.items()}

    @app.put("/items/{item_id}")
    async def replace_nested_item(item_id: int, item: NestedItem):
        return {"item_id": item_id, "item": item}

    @app.put("/bundles/{item_id}")
    async def accept_body_bundle(
        item_id: int,
        item: BundleItem,
        user: BundleUser,
        importance: int = Body(gt=0),
        q: str | None = None,
    ):
        result = {
            "item_id": item_id,
            "item": item,
            "user": user,
            "importance": importance,
        }
        if q:
            result["q"] = q
        return result

    @app.get("/store/{item_id}", response_model=EditableItem)
    async def read_editable_item(item_id: str):
        return items[item_id]

    @app.patch("/store/{item_id}", response_model=EditableItem)
    async def patch_editable_item(item_id: str, item: EditableItem):
        stored = EditableItem(**items[item_id])
        changes = item.model_dump(exclude_unset=True)
        updated = stored.model_copy(update=changes)
        items[item_id] = jsonable_encoder(updated)
        return updated

    return app
