"""Independent optional string-body schema and alias workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field


class PlainPayload(BaseModel):
    p: str | None = None


class AliasPayload(BaseModel):
    p: str | None = Field(None, alias="p_alias")


class ValidationAliasPayload(BaseModel):
    p: str | None = Field(None, validation_alias="p_val_alias")


class BothAliasesPayload(BaseModel):
    p: str | None = Field(None, alias="p_alias", validation_alias="p_val_alias")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/schema/plain/direct", operation_id="optional_body_str_plain_direct")
    async def plain_direct(
        p: Annotated[str | None, Body(embed=True)] = None,
    ) -> dict[str, str | None]:
        return {"p": p}

    @app.post("/schema/plain/model", operation_id="optional_body_str_plain_model")
    async def plain_model(payload: PlainPayload) -> dict[str, str | None]:
        return {"p": payload.p}

    @app.post("/schema/alias/direct", operation_id="optional_body_str_alias_direct")
    async def alias_direct(
        p: Annotated[str | None, Body(embed=True, alias="p_alias")] = None,
    ) -> dict[str, str | None]:
        return {"p": p}

    @app.post("/schema/alias/model", operation_id="optional_body_str_alias_model")
    async def alias_model(payload: AliasPayload) -> dict[str, str | None]:
        return {"p": payload.p}

    @app.post(
        "/schema/validation-alias/direct",
        operation_id="optional_body_str_validation_alias_direct",
    )
    async def validation_alias_direct(
        p: Annotated[str | None, Body(embed=True, validation_alias="p_val_alias")] = None,
    ) -> dict[str, str | None]:
        return {"p": p}

    @app.post(
        "/schema/validation-alias/model",
        operation_id="optional_body_str_validation_alias_model",
    )
    async def validation_alias_model(
        payload: ValidationAliasPayload,
    ) -> dict[str, str | None]:
        return {"p": payload.p}

    @app.post(
        "/schema/both-aliases/direct",
        operation_id="optional_body_str_both_aliases_direct",
    )
    async def both_aliases_direct(
        p: Annotated[
            str | None,
            Body(embed=True, alias="p_alias", validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, str | None]:
        return {"p": p}

    @app.post(
        "/schema/both-aliases/model",
        operation_id="optional_body_str_both_aliases_model",
    )
    async def both_aliases_model(payload: BothAliasesPayload) -> dict[str, str | None]:
        return {"p": payload.p}

    return app
