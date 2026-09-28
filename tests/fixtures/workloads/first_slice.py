"""Small, independently authored request-to-response workload.

The oracle and target workers must import this module in separate processes so
that ``fastapi`` resolves to exactly one product in each environment.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Header, Query, status
from pydantic import BaseModel, Field


class CreateItem(BaseModel):
    name: str
    quantity: int = Field(gt=0)


class PublicItem(BaseModel):
    item_id: int
    name: str
    quantity: int
    actor: str
    color: str | None = None


def current_actor(x_actor: Annotated[str, Header(alias="X-Actor")]) -> str:
    return x_actor


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI-RS parity slice")

    @app.post("/items/{item_id}", response_model=PublicItem, status_code=status.HTTP_201_CREATED)
    async def create_item(
        item_id: int,
        payload: CreateItem,
        actor: Annotated[str, Depends(current_actor)],
        color: Annotated[str | None, Query()] = None,
    ) -> dict[str, object]:
        return {
            "item_id": item_id,
            "name": payload.name,
            "quantity": payload.quantity,
            "actor": actor,
            "color": color,
            "internal_debug": "filtered by response_model",
        }

    return app
