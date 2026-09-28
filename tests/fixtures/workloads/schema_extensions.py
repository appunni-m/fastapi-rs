"""Independent schema, validation, and response-filtering workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, WithJsonSchema


class MapPayload(BaseModel):
    values: dict[str, int]


class StrictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Gadget(BaseModel):
    code: str
    description: Annotated[
        str | None,
        WithJsonSchema({"type": ["string", "null"]}),
    ] = None

    model_config = ConfigDict(json_schema_extra={"x-inventory": {"tier": 4}})


class Profile(BaseModel):
    display_name: str
    internal_code: str


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI-RS schema extensions workload")

    @app.post("/maps")
    async def accept_map(payload: MapPayload) -> dict[str, int]:
        return payload.values

    @app.post("/strict")
    async def accept_strict(payload: StrictPayload | None = None) -> StrictPayload | None:
        return payload

    @app.get("/gadgets/primary", response_model=Gadget)
    async def get_gadget() -> dict[str, str]:
        return {"code": "g-8"}

    @app.get(
        "/profiles/primary",
        response_model=Profile,
        response_model_include={"display_name"},
    )
    async def get_profile() -> dict[str, str]:
        return {"display_name": "Mira", "internal_code": "private-13"}

    return app
