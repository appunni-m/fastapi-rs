from fastapi import FastAPI, status
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/", status_code=status.HTTP_201_CREATED)
    async def create_item(item: Item) -> Item:
        return item

    return app
