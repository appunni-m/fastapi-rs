from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class PlainListQuery(BaseModel):
    item_names: list[str]


class AliasedListQuery(BaseModel):
    item_names: list[str] = Field(alias="public_names")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/catalog/direct")
    def direct_plain(item_names: Annotated[list[str], Query()]):
        return {"item_names": item_names}

    @app.get("/catalog/model")
    def model_plain(query: Annotated[PlainListQuery, Query()]):
        return {"item_names": query.item_names}

    @app.get("/labels/direct")
    def direct_alias(item_names: Annotated[list[str], Query(alias="public_names")]):
        return {"item_names": item_names}

    @app.get("/labels/model")
    def model_alias(query: Annotated[AliasedListQuery, Query()]):
        return {"item_names": query.item_names}

    return app
