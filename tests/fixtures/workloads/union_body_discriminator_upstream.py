"""Explicit tagged union body discriminator and OpenAPI mapping."""

from typing import Annotated, Any, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field, Tag


class FirstItem(BaseModel):
    value: Literal["first"]
    price: int


class OtherItem(BaseModel):
    value: Literal["other"]
    price: float


Item = Annotated[
    Annotated[FirstItem, Tag("first")] | Annotated[OtherItem, Tag("other")],
    Field(discriminator="value"),
]


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/items/")
    def save_union_body_discriminator(
        item: Item, q: Annotated[str, Field(description="Query string")]
    ) -> dict[str, Any]:
        return {"item": item}

    return app
