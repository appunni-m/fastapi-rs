"""Independent ASGI workload for the Header-based application-testing example."""

from typing import Annotated, Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


class Item(BaseModel):
    id: str
    title: str
    description: str | None = None


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Create one fresh item store with the selected Header declaration style."""
    del event_trace
    fake_secret_token = "coneofsilence"
    fake_db: dict[str, dict[str, str | None]] = {
        "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
        "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
    }
    app = FastAPI()

    def read_item(item_id: str, x_token: str) -> dict[str, str | None]:
        if x_token != fake_secret_token:
            raise HTTPException(status_code=400, detail="Invalid X-Token header")
        if item_id not in fake_db:
            raise HTTPException(status_code=404, detail="Item not found")
        return fake_db[item_id]

    def insert_item(item: Item, x_token: str) -> Item:
        if x_token != fake_secret_token:
            raise HTTPException(status_code=400, detail="Invalid X-Token header")
        if item.id in fake_db:
            raise HTTPException(status_code=409, detail="Item already exists")
        fake_db[item.id] = item.model_dump()
        return item

    header_style = factory_input["header_style"]
    if header_style == "default":

        @app.get("/items/{item_id}", response_model=Item)
        async def read_main(item_id: str, x_token: str = Header()):
            return read_item(item_id, x_token)

        @app.post("/items/")
        async def create_item(item: Item, x_token: str = Header()) -> Item:
            return insert_item(item, x_token)

    elif header_style == "annotated":

        @app.get("/items/{item_id}", response_model=Item)
        async def read_main(item_id: str, x_token: Annotated[str, Header()]):
            return read_item(item_id, x_token)

        @app.post("/items/")
        async def create_item(item: Item, x_token: Annotated[str, Header()]) -> Item:
            return insert_item(item, x_token)

    else:
        raise ValueError("unsupported Header declaration style in workload input")

    return app
