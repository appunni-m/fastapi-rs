"""Independent workload for inherited models in a union request body."""

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str | None = None


class ExtendedItem(Item):
    age: int


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/")
    def save_union_different_body(item: ExtendedItem | Item):
        return {"item": item}

    return app
