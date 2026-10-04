"""Independent FastAPI routes for response-model/bodyless status policy."""

from collections.abc import Mapping
from typing import Any

from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel


class Payload(BaseModel):
    value: int


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    def select_not_modified(response: Response) -> None:
        response.status_code = 304

    @app.get("/bodyless/205", status_code=205, response_model=None)
    async def reset_content():
        return {"value": 205}

    @app.get("/bodyless/304", status_code=304, response_model=None)
    async def not_modified():
        return {"value": 304}

    @app.get(
        "/bodyless/304-invalid",
        response_model=Payload,
        dependencies=[Depends(select_not_modified)],
    )
    async def invalid_not_modified():
        return {"value": "not-an-integer"}

    return app
