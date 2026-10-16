"""Independent workload for list Header alias selection."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Header


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/headers/list-alias")
    async def read_list_alias(
        values: Annotated[list[str], Header(alias="p_alias")],
    ) -> dict[str, list[str]]:
        return {"values": values}

    @app.get("/headers/list-validation-alias")
    async def read_list_validation_alias(
        values: Annotated[list[str], Header(validation_alias="p_val_alias")],
    ) -> dict[str, list[str]]:
        return {"values": values}

    @app.get("/headers/list-alias-and-validation-alias")
    async def read_list_alias_and_validation_alias(
        values: Annotated[list[str], Header(alias="p_alias", validation_alias="p_val_alias")],
    ) -> dict[str, list[str]]:
        return {"values": values}

    return app
