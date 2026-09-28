"""Independent response-model serialization and validation workload."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field


class Owner(BaseModel):
    name: str
    credential: str


class Record(BaseModel):
    label: str
    owner: Owner
    internal_note: str


class Preferences(BaseModel):
    owner: str
    theme: str = "light"
    accent: str | None = None
    retries: int = 3


class AliasedItem(BaseModel):
    item_name: str = Field(alias="displayName")


class RequiredOutput(BaseModel):
    name: str
    total: int


def create_app() -> FastAPI:
    app = FastAPI(title="Response Model Serialization", version="1.0.0")

    @app.get(
        "/include",
        response_model=Record,
        response_model_include={"label": ..., "owner": {"name"}},
    )
    async def include_nested_fields() -> dict[str, object]:
        return {
            "label": "draft",
            "owner": {"name": "Ari", "credential": "opaque-token"},
            "internal_note": "staff-only",
        }

    @app.get(
        "/exclude",
        response_model=Record,
        response_model_exclude={"owner": {"credential"}},
    )
    async def exclude_nested_field() -> Record:
        return Record(
            label="published",
            owner=Owner(name="Bo", credential="opaque-token"),
            internal_note="staff-only",
        )

    @app.get(
        "/exclude-unset",
        response_model=Preferences,
        response_model_exclude_unset=True,
    )
    async def exclude_unset_fields() -> Preferences:
        return Preferences(owner="unset-case", accent=None)

    @app.get(
        "/exclude-defaults",
        response_model=Preferences,
        response_model_exclude_defaults=True,
    )
    async def exclude_default_values() -> Preferences:
        return Preferences(owner="defaults-case", theme="light", accent="blue", retries=3)

    @app.get("/alias-default", response_model=AliasedItem)
    async def serialize_alias_by_default() -> dict[str, str]:
        return {"displayName": "aliased-default"}

    @app.get(
        "/alias-field-name",
        response_model=AliasedItem,
        response_model_by_alias=False,
    )
    async def serialize_field_name() -> dict[str, str]:
        return {"displayName": "python-field-name"}

    @app.get("/invalid-output", response_model=RequiredOutput)
    async def return_invalid_output() -> dict[str, str]:
        return {"name": "missing-total"}

    return app
