"""Independent models and routes for OpenAPI schema generation inputs."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any

from fastapi import Body, Depends, FastAPI, Header
from pydantic import BaseModel, ConfigDict, Field


class PostalAddress(BaseModel):
    street: str
    locality: str


class SharedRecord(BaseModel):
    name: str
    address: PostalAddress | None = None


class RecordInput(BaseModel):
    label: str


class RecordOutput(BaseModel):
    id: int
    label: str
    revision: int


class ExampleRecord(BaseModel):
    label: str = Field(examples=["field sample"])

    model_config = ConfigDict(json_schema_extra={"examples": [{"label": "model sample"}]})


class RefNamedRecord(BaseModel):
    ref: str = Field(validation_alias="$ref", serialization_alias="$ref")

    model_config = ConfigDict(validate_by_alias=True, serialize_by_alias=True)


class PlatformRole(str, Enum):
    editor = "editor"
    viewer = "viewer"


class ReservedRole(str, Enum):
    pass


class CompatibleUser(BaseModel):
    username: str
    role: PlatformRole | ReservedRole


class MessageResult(BaseModel):
    input: str
    output: dict[str, Any]


class FormFeedRecord(BaseModel):
    """A model with a form feed in its description.\fThe tail is separate."""

    value: str


class HeaderToken(BaseModel):
    token: str


def _configure_routes(app: FastAPI) -> None:
    @app.get("/shared/primary", response_model=SharedRecord)
    async def primary_record() -> dict[str, Any]:
        return {"name": "primary"}

    @app.get("/shared/secondary", response_model=SharedRecord)
    async def secondary_record() -> dict[str, Any]:
        return {"name": "secondary"}

    @app.post("/records", response_model=RecordOutput)
    async def create_record(record: RecordInput) -> dict[str, Any]:
        return {"id": 1, "label": record.label, "revision": 1}

    @app.post("/records/batch", response_model=list[RecordOutput])
    async def create_records(records: list[RecordInput]) -> list[dict[str, Any]]:
        return [
            {"id": index, "label": record.label, "revision": 1}
            for index, record in enumerate(records, start=1)
        ]

    @app.post("/examples", response_model=ExampleRecord)
    async def echo_example(
        record: Annotated[
            ExampleRecord,
            Body(
                openapi_examples={
                    "request sample": {
                        "summary": "A request-level example",
                        "value": {"label": "request sample"},
                    }
                }
            ),
        ],
    ) -> ExampleRecord:
        return record

    @app.get("/refs", response_model=RefNamedRecord)
    async def get_ref() -> dict[str, str]:
        return {"$ref": "local-reference"}

    @app.get("/users", response_model=CompatibleUser)
    async def get_user() -> dict[str, str]:
        return {"username": "sam", "role": "editor"}

    @app.get("/described", response_model=FormFeedRecord)
    async def get_described_record() -> dict[str, str]:
        return {"value": "sample"}

    def shared_token(token: Annotated[str, Header(alias="x-record-token")]) -> str:
        return token

    def decorate_token(token: Annotated[str, Header(alias="x-record-token")]) -> str:
        return token

    @app.get("/dependency-schema")
    async def dependency_schema(
        first: Annotated[str, Depends(shared_token)],
        second: Annotated[str, Depends(decorate_token)],
    ) -> dict[str, str]:
        return {"first": first, "second": second}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"state": "ready"}


def create_app() -> FastAPI:
    app = FastAPI(title="Schema Workload", version="2.4")
    _configure_routes(app)

    unsplit_app = FastAPI(
        title="Schema Workload",
        version="2.4",
        separate_input_output_schemas=False,
    )
    _configure_routes(unsplit_app)

    @app.get("/openapi-unsplit.json", include_in_schema=False)
    async def unsplit_openapi() -> dict[str, Any]:
        return unsplit_app.openapi()

    return app
