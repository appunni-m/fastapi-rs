"""Independent request-body and body-schema workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI, Path
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI-RS request-body workload")

    @app.post("/labels")
    async def echo_label(label: Annotated[str, Body(embed=True, alias="label")]) -> dict[str, str]:
        return {"label": label}

    @app.post("/swatches")
    async def echo_swatches(
        swatches: Annotated[list[str], Body(embed=True)],
    ) -> dict[str, list[str]]:
        return {"swatches": swatches}

    @app.post("/bundles")
    async def create_bundle(
        product: Product,
        priority: Annotated[int, Body(gt=0)],
    ) -> dict[str, Product | int]:
        return {"product": product, "priority": priority}

    @app.put("/products/{product_id}")
    async def replace_product(
        product_id: Annotated[int, Path(ge=0, le=1000)],
        product: Product | None = None,
        q: str | None = None,
    ) -> dict[str, int | str | Product]:
        result: dict[str, int | str | Product] = {"product_id": product_id}
        if product is not None:
            result["product"] = product
        if q is not None:
            result["query"] = q
        return result

    return app
