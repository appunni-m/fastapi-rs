"""Runtime argument bundles for direct FastAPI JSON encoder probes."""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel, Field


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


class ModelWithDefaults(BaseModel):
    foo: str
    bar: str = "bar"
    bla: str = "bla"


class ModelWithAlias(BaseModel):
    foo: str = Field(alias="Foo")


class SafeDateTime(datetime):
    """Datetime subtype used to exercise custom-encoder type matching."""


class TimestampPayload(TypedDict):
    timestamp: SafeDateTime


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build non-JSON Python values for calls through the public FastAPI API."""
    item = Item(
        title="Foo",
        timestamp=datetime(2023, 1, 1, 12),
        description="An optional description",
    )
    pet = {"name": "Firulais", "owner": {"name": "Foo"}}
    model = ModelWithDefaults(foo="foo", bar="bar")
    alias_model = ModelWithAlias(Foo="Bar")
    timestamp: TimestampPayload = {"timestamp": SafeDateTime(2019, 1, 1, 8, 9, 10)}

    return {
        "tutorial-item": {"args": [item], "kwargs": {}},
        "mapping-include": {"args": [pet], "kwargs": {"include": {"name"}}},
        "mapping-exclude": {"args": [pet], "kwargs": {"exclude": {"owner"}}},
        "model-alias": {"args": [alias_model], "kwargs": {}},
        "model-defaults": {"args": [model], "kwargs": {}},
        "model-exclude-unset": {"args": [model], "kwargs": {"exclude_unset": True}},
        "model-exclude-defaults": {
            "args": [model],
            "kwargs": {"exclude_defaults": True},
        },
        "custom-encoder-exact": {
            "args": [timestamp],
            "kwargs": {
                "custom_encoder": {
                    SafeDateTime: lambda value: value.strftime("%H:%M:%S"),
                }
            },
        },
        "custom-encoder-base": {
            "args": [timestamp],
            "kwargs": {
                "custom_encoder": {
                    datetime: lambda value: value.strftime("%H:%M:%S"),
                }
            },
        },
    }
