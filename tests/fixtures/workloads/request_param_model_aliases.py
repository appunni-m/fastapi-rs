"""Independent Query/Header/Cookie model-alias workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Query
from pydantic import BaseModel, Field


class Model(BaseModel):
    param: str = Field(alias="param_alias")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query")
    async def query_model(data: Annotated[Model, Query()]) -> dict[str, str]:
        return {"param": data.param}

    @app.get("/header")
    async def header_model(data: Annotated[Model, Header()]) -> dict[str, str]:
        return {"param": data.param}

    @app.get("/cookie")
    async def cookie_model(data: Annotated[Model, Cookie()]) -> dict[str, str]:
        return {"param": data.param}

    return app
