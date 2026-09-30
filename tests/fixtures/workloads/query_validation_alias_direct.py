from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/required-alias-and-validation-alias")
    def read_direct(p: Annotated[str, Query(alias="p_alias", validation_alias="p_val_alias")]):
        return {"p": p}

    return app
