"""Independent app for the pinned body-updates tutorial test inputs."""

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


def create_app() -> FastAPI:
    app = FastAPI()
    items = {
        "foo": {"name": "Foo", "price": 50.2},
        "bar": {
            "name": "Bar",
            "description": "The bartenders",
            "price": 62,
            "tax": 20.2,
        },
        "baz": {
            "name": "Baz",
            "description": None,
            "price": 50.2,
            "tax": 10.5,
            "tags": [],
        },
    }

    @app.get("/items/{item_id}", response_model=Item)
    async def read_item(item_id: str):
        return items[item_id]

    @app.put("/items/{item_id}", response_model=Item)
    async def update_item(item_id: str, item: Item):
        update_item_encoded = jsonable_encoder(item)
        items[item_id] = update_item_encoded
        return update_item_encoded

    return app
