"""Input workload comparing default and opt-out JSON content-type checking."""

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/")
    async def create_strict_item(item: Item) -> Item:
        return item

    legacy_app = FastAPI(strict_content_type=False)

    @legacy_app.post("/items/")
    async def create_legacy_item(item: Item) -> Item:
        return item

    app.mount("/legacy", legacy_app)
    return app
