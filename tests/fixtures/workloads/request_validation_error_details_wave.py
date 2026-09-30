"""Independent request-validation error aggregation and exception stimuli."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    age: float = Field(gt=0)


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()

    if factory_input.get("rethrow_validation_error", False):

        @app.exception_handler(RequestValidationError)
        async def rethrow_validation_error(_request: Request, exc: RequestValidationError) -> None:
            raise exc

    @app.post("/items")
    def save_items(q: Annotated[list[int], Query()], items: list[Item]):
        return {"q": q, "items": items}

    return app
