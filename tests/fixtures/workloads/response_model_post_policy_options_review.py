"""POST response-model serialization policy workload for source review."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str
    email: str
    access_token: str


class Record(BaseModel):
    label: str
    owner: Contact
    audit_note: str


class PolicyPayload(BaseModel):
    label: str
    state: str = "draft"
    retries: int = 3
    note: str | None = None
    display_name: str = Field(alias="displayName")


class AttributeInput(BaseModel):
    name: str


class AttributeResponse(BaseModel):
    name: str
    full_name: str


class AttributeRecord:
    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def full_name(self) -> str:
        return f"{self.name} Person"


def create_app() -> FastAPI:
    app = FastAPI(title="POST response-model policy options")

    @app.post(
        "/nested/include",
        response_model=Record,
        response_model_include={"label": ..., "owner": {"name"}},
    )
    def include_nested(payload: Record) -> Record:
        return payload

    @app.post(
        "/nested/exclude",
        response_model=Record,
        response_model_exclude={"owner": {"access_token"}},
    )
    def exclude_nested(payload: Record) -> Record:
        return payload

    @app.post(
        "/exclude-unset",
        response_model=PolicyPayload,
        response_model_exclude_unset=True,
    )
    def exclude_unset(payload: PolicyPayload) -> PolicyPayload:
        return payload

    @app.post(
        "/exclude-defaults",
        response_model=PolicyPayload,
        response_model_exclude_defaults=True,
    )
    def exclude_defaults(payload: PolicyPayload) -> PolicyPayload:
        return payload

    @app.post(
        "/exclude-none",
        response_model=PolicyPayload,
        response_model_exclude_none=True,
    )
    def exclude_none(payload: PolicyPayload) -> PolicyPayload:
        return payload

    @app.post(
        "/field-name",
        response_model=PolicyPayload,
        response_model_by_alias=False,
    )
    def field_name_output(payload: PolicyPayload) -> PolicyPayload:
        return payload

    @app.post("/attributes", response_model=AttributeResponse)
    def attributes(payload: AttributeInput) -> AttributeRecord:
        return AttributeRecord(payload.name)

    return app
