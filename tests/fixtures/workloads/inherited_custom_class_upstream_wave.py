"""Input workload for UUID-like values exposed by application routes."""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, field_serializer


class DriverUuid:
    """Represent a database UUID without inheriting from :class:`uuid.UUID`."""

    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value

    @property
    def __class__(self) -> type[uuid.UUID]:
        return uuid.UUID

    @property
    def __dict__(self) -> dict[str, object]:
        raise TypeError("vars() is unavailable for this driver value")


class UuidRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    key: DriverUuid

    @field_serializer("key")
    def serialize_key(self, value: DriverUuid) -> str:
        return str(value)


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/fast_uuid")
    def return_driver_uuid() -> dict[str, DriverUuid]:
        return {"fast_uuid": DriverUuid("a10ff360-3b1e-4984-a26f-d3ab460bdb51")}

    @app.get("/get_custom_class")
    def return_uuid_record() -> UuidRecord:
        return UuidRecord(key=DriverUuid("b8799909-f914-42de-91bc-95c819218d01"))

    return app
