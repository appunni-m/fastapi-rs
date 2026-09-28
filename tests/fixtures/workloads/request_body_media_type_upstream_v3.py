"""Independent OpenAPI workload for custom request-body media types."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import Body, FastAPI
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float


class Shop(BaseModel):
    name: str


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    """Create request-body declarations matching the pinned source scenario."""

    del factory_input, event_trace
    media_type = "application/vnd.api+json"
    app = FastAPI()

    @app.post("/products")
    async def create_product(
        data: Product = Body(media_type=media_type, embed=True),  # noqa: B008
    ):
        pass

    @app.post("/shops")
    async def create_shop(
        data: Shop = Body(media_type=media_type),  # noqa: B008
        included: list[Product] = Body(default=[], media_type=media_type),  # noqa: B008
    ):
        pass

    return app
