from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class QueryModelRequiredAliasAndValidationAlias(BaseModel):
    p: str = Field(alias="p_alias", validation_alias="p_val_alias")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/model-required-alias-and-validation-alias")
    def read_model(p: Annotated[QueryModelRequiredAliasAndValidationAlias, Query()]):
        return {"p": p.p}

    return app
