"""Independent optional-body schema workload for alias projection parity."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field


class PlainPayload(BaseModel):
    p: list[str] | None = None


class AliasPayload(BaseModel):
    p: list[str] | None = Field(None, alias="p_alias")


class ValidationAliasPayload(BaseModel):
    p: list[str] | None = Field(None, validation_alias="p_val_alias")


class BothAliasesPayload(BaseModel):
    p: list[str] | None = Field(None, alias="p_alias", validation_alias="p_val_alias")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/schema/plain/direct", operation_id="schema_optional_list_plain_direct")
    async def plain_direct(
        p: Annotated[list[str] | None, Body(embed=True)] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post("/schema/plain/model", operation_id="schema_optional_list_plain_model")
    async def plain_model(payload: PlainPayload) -> dict[str, list[str] | None]:
        return {"p": payload.p}

    @app.post("/schema/alias/direct", operation_id="schema_optional_list_alias_direct")
    async def alias_direct(
        p: Annotated[list[str] | None, Body(embed=True, alias="p_alias")] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post("/schema/alias/model", operation_id="schema_optional_list_alias_model")
    async def alias_model(payload: AliasPayload) -> dict[str, list[str] | None]:
        return {"p": payload.p}

    @app.post(
        "/schema/validation-alias/direct",
        operation_id="schema_optional_list_validation_alias_direct",
    )
    async def validation_alias_direct(
        p: Annotated[list[str] | None, Body(embed=True, validation_alias="p_val_alias")] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post(
        "/schema/validation-alias/model",
        operation_id="schema_optional_list_validation_alias_model",
    )
    async def validation_alias_model(
        payload: ValidationAliasPayload,
    ) -> dict[str, list[str] | None]:
        return {"p": payload.p}

    @app.post(
        "/schema/both-aliases/direct",
        operation_id="schema_optional_list_both_aliases_direct",
    )
    async def both_aliases_direct(
        p: Annotated[
            list[str] | None,
            Body(embed=True, alias="p_alias", validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post(
        "/schema/both-aliases/model",
        operation_id="schema_optional_list_both_aliases_model",
    )
    async def both_aliases_model(payload: BothAliasesPayload) -> dict[str, list[str] | None]:
        return {"p": payload.p}

    return app
