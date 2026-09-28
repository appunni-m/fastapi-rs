"""Independent workload for the union request-body tutorial tests."""

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str | None = None


class OtherItem(BaseModel):
    price: int


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/")
    def save_union_body(item: OtherItem | Item):
        return {"item": item}

    return app
