"""Independent Pydantic and dataclass request-body workloads."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@dataclass
class InventoryItem:
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/products/")
    async def create_product(item: Product) -> dict[str, object]:
        result = item.model_dump()
        if item.tax is not None:
            result["price_with_tax"] = item.price + item.tax
        return result

    @app.post("/inventory/")
    async def create_inventory_item(item: InventoryItem) -> InventoryItem:
        return item

    return app
