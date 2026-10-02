"""Independent form and Pydantic form-model workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel, ConfigDict, Field


class FormModel(BaseModel):
    username: str
    lastname: str
    age: int | None = None
    tags: list[str] = ["foo", "bar"]
    alias_with: str = Field(alias="with", default="nothing")


class FormModelExtraAllow(BaseModel):
    param: str

    model_config = ConfigDict(extra="allow")


class PersonAccount(BaseModel):
    person_name: str


class TeamAccount(BaseModel):
    team_name: str


class Registration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/defaults/urlencoded")
    async def urlencoded_default(topic: Annotated[str, Form()] = "general") -> dict[str, str]:
        return {"topic": topic}

    @app.post("/defaults/multipart")
    async def multipart_default(topic: Annotated[str, Form()] = "general") -> dict[str, str]:
        return {"topic": topic}

    @app.post("/sequences/list")
    async def list_values(values: Annotated[list[str], Form()]) -> dict[str, list[str]]:
        return {"values": values}

    @app.post("/sequences/set")
    async def set_values(values: Annotated[set[str], Form()]) -> dict[str, set[str]]:
        return {"values": values}

    @app.post("/sequences/tuple")
    async def tuple_values(
        values: Annotated[tuple[str, ...], Form()],
    ) -> dict[str, tuple[str, ...]]:
        return {"values": values}

    @app.post("/form/")
    def submit_form(user: Annotated[FormModel, Form()]) -> FormModel:
        return user

    @app.post("/form-extra-allow/")
    def submit_form_extra_allow(
        params: Annotated[FormModelExtraAllow, Form()],
    ) -> FormModelExtraAllow:
        return params

    @app.post("/note")
    async def submit_note(note: Annotated[str, Form()]) -> dict[str, str]:
        return {"note": note}

    @app.post("/accounts")
    async def create_account(
        account: Annotated[PersonAccount | TeamAccount, Form()],
    ) -> PersonAccount | TeamAccount:
        return account

    @app.post("/registration")
    async def register(registration: Annotated[Registration, Form()]) -> Registration:
        return registration

    return app
