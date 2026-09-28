"""Independent inputs for annotation resolution and response encoding."""

from __future__ import annotations

import functools
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, field_serializer


class DriverUuid:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value

    @property
    def __class__(self) -> type[uuid.UUID]:
        return uuid.UUID

    @property
    def __dict__(self) -> dict[str, object]:
        raise TypeError("vars() is unavailable for this workload value")


class UuidRecord(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    value: DriverUuid

    @field_serializer("value")
    def serialize_value(self, value: DriverUuid) -> str:
        return str(value)


class DummyClient:
    async def get_people(self) -> list[str]:
        return ["Ada", "Grace"]

    async def close(self) -> None:
        return None


async def get_client() -> AsyncGenerator[DummyClient, None]:
    client = DummyClient()
    yield client
    await client.close()


Client = Annotated[DummyClient, Depends(get_client)]


class RequestLabel:
    def __call__(self, request: Request) -> str:
        return request.method.lower() + "-label"


def forwardref_method(input: ForwardRefModel) -> ForwardRefModel:
    return ForwardRefModel(x=input.x + 1)


class ForwardRefModel(BaseModel):
    x: int = 0


def passthrough(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapped


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/encoded/driver")
    def return_driver_value():
        return {"driver": DriverUuid("d1d7c799-ae44-44c6-a6d7-df6d78eb0f21")}

    @app.get("/encoded/model")
    def return_custom_model():
        return UuidRecord(value=DriverUuid("fd62f0e6-e9ec-46e1-a5c5-3b4b85a61233"))

    @app.get("/annotation/no-content", status_code=204)
    def no_content() -> None:
        return None

    @app.get("/annotation/people")
    async def read_people(client: Client) -> list[str]:
        return await client.get_people()

    @app.get("/annotation/request")
    def read_request_label(label: Annotated[str, Depends(RequestLabel())]):
        return {"label": label}

    @app.post("/forward/one")
    def first_forwarded(input: ForwardRefModel) -> ForwardRefModel:
        return passthrough(forwardref_method)(input)

    @app.post("/forward/two")
    def twice_forwarded(input: ForwardRefModel) -> ForwardRefModel:
        return passthrough(passthrough(forwardref_method))(input)

    return app
