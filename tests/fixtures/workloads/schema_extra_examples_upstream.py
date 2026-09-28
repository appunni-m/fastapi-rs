"""Independent APIs for OpenAPI schema and request-body example inputs."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field


class ConfigExampleRecord(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Compass",
                    "description": "A field notebook",
                    "price": 28.5,
                    "tax": 1.4,
                }
            ]
        }
    }


class FieldExamplesRecord(BaseModel):
    name: str = Field(examples=["Compass"])
    description: str | None = Field(default=None, examples=["A field notebook"])
    price: float = Field(examples=[28.5])
    tax: float | None = Field(default=None, examples=[1.4])


class BodyExamplesRecord(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class MultipleBodyExamplesRecord(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class NamedBodyExamplesRecord(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


_ONE_EXAMPLE = [
    {
        "name": "Compass",
        "description": "A field notebook",
        "price": 28.5,
        "tax": 1.4,
    }
]
_SEVERAL_EXAMPLES = [
    {
        "name": "Compass",
        "description": "A field notebook",
        "price": 28.5,
        "tax": 1.4,
    },
    {"name": "Spare part", "price": "28.5"},
    {"name": "Unpriced sample", "price": "not-a-number"},
]
_NAMED_EXAMPLES = {
    "ordinary": {
        "summary": "A complete record",
        "description": "This record satisfies the request model.",
        "value": {
            "name": "Compass",
            "description": "A field notebook",
            "price": 28.5,
            "tax": 1.4,
        },
    },
    "converted": {
        "summary": "A number supplied as text",
        "description": "The request model accepts a numeric string.",
        "value": {"name": "Spare part", "price": "28.5"},
    },
    "invalid": {
        "summary": "A value that cannot be converted",
        "value": {"name": "Unpriced sample", "price": "not-a-number"},
    },
}
_ONE_BODY_DEFAULT = Body(examples=_ONE_EXAMPLE)
_ONE_BODY_ANNOTATED = Body(examples=_ONE_EXAMPLE)
_SEVERAL_BODY_DEFAULT = Body(examples=_SEVERAL_EXAMPLES)
_SEVERAL_BODY_ANNOTATED = Body(examples=_SEVERAL_EXAMPLES)
_NAMED_BODY_DEFAULT = Body(openapi_examples=_NAMED_EXAMPLES)
_NAMED_BODY_ANNOTATED = Body(openapi_examples=_NAMED_EXAMPLES)


def _result(record_id: int, record: BaseModel) -> dict[str, object]:
    return {"record_id": record_id, "record": record}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/examples/model-config/{record_id}")
    async def update_model_config(record_id: int, record: ConfigExampleRecord) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/field-values/{record_id}")
    async def update_field_values(record_id: int, record: FieldExamplesRecord) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/body-default/{record_id}")
    async def update_body_default(
        record_id: int, record: BodyExamplesRecord = _ONE_BODY_DEFAULT
    ) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/body-annotated/{record_id}")
    async def update_body_annotated(
        record_id: int,
        record: Annotated[BodyExamplesRecord, _ONE_BODY_ANNOTATED],
    ) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/body-multiple-default/{record_id}")
    async def update_multiple_default(
        record_id: int,
        record: MultipleBodyExamplesRecord = _SEVERAL_BODY_DEFAULT,
    ) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/body-multiple-annotated/{record_id}")
    async def update_multiple_annotated(
        record_id: int,
        record: Annotated[MultipleBodyExamplesRecord, _SEVERAL_BODY_ANNOTATED],
    ) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/openapi-default/{record_id}")
    async def update_openapi_default(
        record_id: int,
        record: NamedBodyExamplesRecord = _NAMED_BODY_DEFAULT,
    ) -> dict[str, object]:
        return _result(record_id, record)

    @app.put("/examples/openapi-annotated/{record_id}")
    async def update_openapi_annotated(
        record_id: int,
        record: Annotated[NamedBodyExamplesRecord, _NAMED_BODY_ANNOTATED],
    ) -> dict[str, object]:
        return _result(record_id, record)

    return app
