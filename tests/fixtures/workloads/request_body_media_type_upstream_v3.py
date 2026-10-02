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

    del event_trace
    media_type = "application/vnd.api+json"
    app = FastAPI()

    @app.post("/products")
    async def create_product(
        data: Product = Body(media_type=media_type, embed=True),  # noqa: B008
    ):
        return data

    @app.post("/shops")
    async def create_shop(
        data: Shop = Body(media_type=media_type),  # noqa: B008
        included: list[Product] = Body(default=[], media_type=media_type),  # noqa: B008
    ):
        return {"data": data, "included": included}

    if factory_input.get("include_source_review_probes", False):

        @app.post("/mixed")
        async def create_mixed(
            data: Shop = Body(media_type=media_type),  # noqa: B008
            included: list[Product] = Body(default=[], media_type="application/json"),  # noqa: B008
        ):
            return {"data": data, "included": included}

        @app.post("/direct-default")
        async def direct_default(
            value: int = Body(default=3, media_type=media_type),  # noqa: B008
        ):
            return value

        @app.post("/unvalidated-default")
        async def unvalidated_default(
            value: int = Body(default="not-an-integer", media_type=media_type),  # noqa: B008
        ):
            return {"value": value}

    return app
