from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post(
        "/items/",
        summary="Create an item",
        description=(
            "Create an item with all the information, name, description, price, tax "
            "and a set of unique tags"
        ),
    )
    async def create_item(item: Item) -> Item:
        return item

    return app
