"""Query endpoints for exercising optional list wire-name selection."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field


class DeclaredAliasQuery(BaseModel):
    p: list[str] | None = Field(default=None, alias="p_alias")


class ValidationAliasQuery(BaseModel):
    p: list[str] | None = Field(default=None, validation_alias="p_val_alias")


class CombinedAliasQuery(BaseModel):
    p: list[str] | None = Field(
        default=None,
        alias="p_alias",
        validation_alias="p_val_alias",
    )


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/optional-alias/direct")
    async def declared_alias_direct(
        p: Annotated[list[str] | None, Query(alias="p_alias")] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.get("/optional-alias/model")
    async def declared_alias_model(
        query: Annotated[DeclaredAliasQuery, Query()],
    ) -> dict[str, list[str] | None]:
        return {"p": query.p}

    @app.get("/optional-validation-alias/direct")
    async def validation_alias_direct(
        p: Annotated[list[str] | None, Query(validation_alias="p_val_alias")] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.get("/optional-validation-alias/model")
    async def validation_alias_model(
        query: Annotated[ValidationAliasQuery, Query()],
    ) -> dict[str, list[str] | None]:
        return {"p": query.p}

    @app.get("/optional-combined-alias/direct")
    async def combined_alias_direct(
        p: Annotated[
            list[str] | None,
            Query(alias="p_alias", validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.get("/optional-combined-alias/model")
    async def combined_alias_model(
        query: Annotated[CombinedAliasQuery, Query()],
    ) -> dict[str, list[str] | None]:
        return {"p": query.p}

    return app
