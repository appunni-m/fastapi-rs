"""Independent path, query, header, cookie, and body validation workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


class Coordinate(BaseModel):
    x: float
    y: float


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/float")
    async def read_float(value: Annotated[float, Body(allow_inf_nan=False)]) -> float:
        return value

    @app.post("/nullable")
    async def read_nullable(value: Annotated[str | None, Body(embed=True)]) -> str | None:
        return value

    @app.post("/coordinates")
    async def read_coordinate_pair(
        points: tuple[Coordinate, Coordinate],
    ) -> tuple[Coordinate, Coordinate]:
        return points

    @app.post("/products")
    async def create_product(product: Product) -> Product:
        return product

    @app.get("/items")
    async def read_items(user_id: str | None = None) -> dict[str, str | None]:
        return {"user_id": user_id}

    @app.get("/items/{item_id}")
    async def read_item(item_id: str, user_id: str | None = None) -> dict[str, str | None]:
        return {"item_id": item_id, "user_id": user_id}

    @app.get("/catalog/{item_id}")
    async def read_numeric_item(
        item_id: Annotated[int, Path(ge=1)], q: str
    ) -> dict[str, int | str]:
        return {"item_id": item_id, "q": q}

    @app.get("/search")
    async def search_items(
        q: Annotated[str | None, Query(max_length=50)] = None,
    ) -> dict[str, str | None]:
        return {"q": q}

    @app.get("/cookies")
    async def read_cookie(ads_id: Annotated[str | None, Cookie()] = None) -> dict[str, str | None]:
        return {"ads_id": ads_id}

    @app.get("/headers")
    async def read_user_agent(
        user_agent: Annotated[str | None, Header()] = None,
    ) -> dict[str, str | None]:
        return {"user_agent": user_agent}

    nested_app = FastAPI(strict_content_type=False)
    outer = APIRouter(prefix="/outer")
    default_router = APIRouter(prefix="/default")

    @default_router.post("/items")
    async def read_untyped_json(data: dict[str, str]) -> dict[str, str]:
        return data

    outer.include_router(default_router)
    nested_app.include_router(outer)
    app.mount("/nested-content-type", nested_app)
    return app
