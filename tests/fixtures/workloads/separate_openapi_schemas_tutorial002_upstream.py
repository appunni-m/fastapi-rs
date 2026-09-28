"""ASGI workload for the shared input/output schema tutorial example."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(separate_input_output_schemas=False)

    @app.post("/items/")
    def create_item(item: Item) -> Item:
        return item

    @app.get("/items/")
    def read_items() -> list[Item]:
        return [
            Item(
                name="Portal Gun",
                description="Device to travel through the multi-rick-verse",
            ),
            Item(name="Plumbus"),
        ]

    return app
