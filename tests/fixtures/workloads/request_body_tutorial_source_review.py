"""Independent request-body tutorial workloads for source review.

The route prefixes and request values are new. FastAPI owns the Rust request-body
and route integration under review; this fixture uses the public Python facade.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI, Path
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/source-review/body/tutorial001/items/")
    async def body_tutorial001(item: Item):
        return item

    @app.post("/source-review/body/tutorial002/items/")
    async def body_tutorial002(item: Item):
        item_data = item.model_dump()
        if item.tax is not None:
            item_data["price_with_tax"] = item.price + item.tax
        return item_data

    @app.put("/source-review/body/tutorial003/items/{item_id}")
    async def body_tutorial003(item_id: int, item: Item):
        return {"item_id": item_id, **item.model_dump()}

    @app.put("/source-review/body/tutorial004/items/{item_id}")
    async def body_tutorial004(item_id: int, item: Item, q: str | None = None):
        result = {"item_id": item_id, **item.model_dump()}
        if q:
            result["q"] = q
        return result

    @app.put("/source-review/multi/tutorial001/items/{item_id}")
    async def body_multi_tutorial001(
        *,
        item_id: int = Path(title="A bounded item identifier", ge=0, le=1000),
        q: str | None = None,
        item: Item | None = None,
    ):
        result = {"item_id": item_id}
        if q:
            result["q"] = q
        if item:
            result["item"] = item
        return result

    @app.put("/source-review/multi/tutorial002/items/{item_id}")
    async def body_multi_tutorial002(item_id: int, item: Item, user: User):
        return {"item_id": item_id, "item": item, "user": user}

    @app.put("/source-review/multi/tutorial003/default/items/{item_id}")
    async def body_multi_tutorial003_default(
        item_id: int, item: Item, user: User, importance: int = Body()
    ):
        return {
            "item_id": item_id,
            "item": item,
            "user": user,
            "importance": importance,
        }

    @app.put("/source-review/multi/tutorial003/annotated/items/{item_id}")
    async def body_multi_tutorial003_annotated(
        item_id: int,
        item: Item,
        user: User,
        importance: Annotated[int, Body()],
    ):
        return {
            "item_id": item_id,
            "item": item,
            "user": user,
            "importance": importance,
        }

    @app.put("/source-review/multi/tutorial004/default/items/{item_id}")
    async def body_multi_tutorial004_default(
        *,
        item_id: int,
        item: Item,
        user: User,
        importance: int = Body(gt=0),
        q: str | None = None,
    ):
        result = {
            "item_id": item_id,
            "item": item,
            "user": user,
            "importance": importance,
        }
        if q:
            result["q"] = q
        return result

    @app.put("/source-review/multi/tutorial004/annotated/items/{item_id}")
    async def body_multi_tutorial004_annotated(
        *,
        item_id: int,
        item: Item,
        user: User,
        importance: Annotated[int, Body(gt=0)],
        q: str | None = None,
    ):
        result = {
            "item_id": item_id,
            "item": item,
            "user": user,
            "importance": importance,
        }
        if q:
            result["q"] = q
        return result

    @app.put("/source-review/multi/tutorial005/default/items/{item_id}")
    async def body_multi_tutorial005_default(
        item_id: int,
        item: Item = Body(embed=True),  # noqa: B008
    ):
        return {"item_id": item_id, "item": item}

    @app.put("/source-review/multi/tutorial005/annotated/items/{item_id}")
    async def body_multi_tutorial005_annotated(
        item_id: int, item: Annotated[Item, Body(embed=True)]
    ):
        return {"item_id": item_id, "item": item}

    return app
