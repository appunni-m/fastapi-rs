from typing import Annotated

from pydantic import AliasChoices

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/required-alias-and-validation-alias")
    def read_direct(p: Annotated[str, Query(alias="p_alias", validation_alias="p_val_alias")]):
        return {"p": p}

    @app.get("/required-alias-choices")
    def read_alias_choices(
        p: Annotated[
            str,
            Query(
                alias="external-id",
                validation_alias=AliasChoices("legacy-id", "external-id"),
            ),
        ],
    ):
        return {"p": p}

    return app
