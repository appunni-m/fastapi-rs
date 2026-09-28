"""Independent request-value and content-type workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, FastAPI, Form, Header, Query
from pydantic import BaseModel, Field, Json


class AliasParameters(BaseModel):
    value: str = Field(alias="external_value")


class Product(BaseModel):
    name: str
    price: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/json/form")
    async def json_form(values: Annotated[Json[list[str]], Form()]) -> list[str]:
        return values

    @app.get("/json/query")
    async def json_query(values: Annotated[Json[list[str]], Query()]) -> list[str]:
        return values

    @app.get("/json/header")
    async def json_header(x_items: Annotated[Json[list[str]], Header()]) -> list[str]:
        return x_items

    @app.get("/alias/query")
    async def query_alias(parameters: Annotated[AliasParameters, Query()]) -> dict[str, str]:
        return {"value": parameters.value}

    @app.get("/alias/header")
    async def header_alias(parameters: Annotated[AliasParameters, Header()]) -> dict[str, str]:
        return {"value": parameters.value}

    @app.get("/alias/cookie")
    async def cookie_alias(parameters: Annotated[AliasParameters, Cookie()]) -> dict[str, str]:
        return {"value": parameters.value}

    @app.get("/product")
    async def get_product(product: Product) -> Product:
        return product

    strict_app = FastAPI()
    lax_app = FastAPI(strict_content_type=False)

    @strict_app.post("/items")
    async def strict_item(data: dict[str, str]) -> dict[str, str]:
        return data

    @lax_app.post("/items")
    async def lax_item(data: dict[str, str]) -> dict[str, str]:
        return data

    app.mount("/strict", strict_app)
    app.mount("/lax", lax_app)
    return app
