"""Exercise FastAPI response and schema handling for a Pydantic arbitrary type."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, PlainSerializer, TypeAdapter, WithJsonSchema


class DenseVector:
    def __init__(self, values: tuple[float, ...]) -> None:
        self.values = values


VectorValue = Annotated[
    DenseVector,
    WithJsonSchema(TypeAdapter(list[float]).json_schema()),
    PlainSerializer(lambda value: list(value.values)),
]


class VectorEnvelope(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    payload: VectorValue


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/vectors/latest")
    def get_latest_vector() -> VectorEnvelope:
        return VectorEnvelope(payload=DenseVector((0.25, 0.5, 0.75)))

    return app
