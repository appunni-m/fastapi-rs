from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class IngredientsValidationOnly(BaseModel):
    ingredients: list[str] = Field(validation_alias="wire_ingredients")


class IngredientsAliasAndValidationAlias(BaseModel):
    ingredients: list[str] = Field(
        alias="declared_ingredients",
        validation_alias="wire_ingredients",
    )


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/matrix-validation-only-direct")
    def direct_validation_only(
        ingredients: Annotated[list[str], Query(validation_alias="wire_ingredients")],
    ):
        return {"ingredients": ingredients}

    @app.get("/matrix-validation-only-model")
    def model_validation_only(
        query: Annotated[IngredientsValidationOnly, Query()],
    ):
        return {"ingredients": query.ingredients}

    @app.get("/matrix-both-aliases-direct")
    def direct_both_aliases(
        ingredients: Annotated[
            list[str],
            Query(alias="declared_ingredients", validation_alias="wire_ingredients"),
        ],
    ):
        return {"ingredients": ingredients}

    @app.get("/matrix-both-aliases-model")
    def model_both_aliases(
        query: Annotated[IngredientsAliasAndValidationAlias, Query()],
    ):
        return {"ingredients": query.ingredients}

    return app
