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

    @app.post("/items/", tags=["items"])
    async def create_item(item: Item) -> Item:
        return item

    @app.get("/items/", tags=["items"])
    async def read_items():
        return [{"name": "Foo", "price": 42}]

    @app.get("/users/", tags=["users"])
    async def read_users():
        return [{"username": "johndoe"}]

    return app
