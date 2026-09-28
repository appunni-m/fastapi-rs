"""Independent request and schema inputs inspired by FastAPI guide topics."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, Cookie, FastAPI, Form, Header, Path, Query
from pydantic import BaseModel, Field


class Envelope(BaseModel):
    label: str = Field(min_length=2, max_length=40, description="Short display label")
    importance: int = Field(ge=1, le=9)


class Branch(BaseModel):
    span: float = Field(gt=0)


class Tree(BaseModel):
    species: str
    branches: list[Branch]


class RecordPatch(BaseModel):
    label: str | None = None
    active: bool | None = None


class SessionCookies(BaseModel):
    session_id: str = Field(alias="session-id")
    theme: str = "light"


class ClientHeaders(BaseModel):
    client_name: str = Field(alias="x-client-name")
    region: str | None = Field(default=None, alias="x-region")


class Preferences(BaseModel):
    display_name: str = Field(min_length=2, max_length=32)
    notifications_enabled: bool = True


class CreateRecord(BaseModel):
    title: str


class RecordView(BaseModel):
    record_id: int
    title: str
    revision: int


def create_app() -> FastAPI:
    app = FastAPI(title="Guide Request Workload", version="1.7")

    @app.post("/envelopes", tags=["input models"])
    async def create_envelope(
        payload: Annotated[
            Envelope,
            Body(description="Envelope details submitted by a client"),
        ],
    ) -> Envelope:
        return payload

    @app.post("/trees")
    async def create_tree(tree: Tree) -> Tree:
        return tree

    @app.patch("/records/{record_id}", response_model=RecordView)
    async def patch_record(record_id: int, patch: RecordPatch) -> dict[str, object]:
        return {
            "record_id": record_id,
            "title": patch.label or "untitled",
            "revision": 2 if patch.active is not None else 1,
        }

    @app.get("/sessions")
    async def read_session(cookies: Annotated[SessionCookies, Cookie()]) -> SessionCookies:
        return cookies

    @app.get("/envelopes/headers")
    async def read_headers(headers: Annotated[ClientHeaders, Header()]) -> ClientHeaders:
        return headers

    @app.get("/numbers/{value}")
    async def read_number(value: Annotated[int, Path(gt=0, le=300)]) -> dict[str, int]:
        return {"value": value}

    @app.get("/lookup")
    async def lookup(
        term: Annotated[str, Query(min_length=3, max_length=18, pattern="^[a-z-]+$")],
        limit: Annotated[int, Query(ge=1, le=40)] = 10,
    ) -> dict[str, object]:
        return {"term": term, "limit": limit}

    @app.post("/preferences")
    async def update_preferences(
        preferences: Annotated[Preferences, Form()],
    ) -> Preferences:
        return preferences

    return app
