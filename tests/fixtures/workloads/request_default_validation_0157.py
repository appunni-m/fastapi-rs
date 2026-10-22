"""Independent ASGI workload for request parameter default validation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Body, Cookie, FastAPI, File, Form, Header, Query
from pydantic import BaseModel, BeforeValidator, Field


def _double(value: Any) -> int:
    return 0 if value is None else int(value) * 2


ValidatedInt = Annotated[int | None, BeforeValidator(_double)]


class DefaultModel(BaseModel):
    value: ValidatedInt = 10


class ValidatedDefaultModel(BaseModel):
    value: Annotated[ValidatedInt, Field(validate_default=True)] = 10


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()
    factory_calls = {"parameter": 0, "pydantic_field": 0}

    @app.get("/query/default")
    def query_default(value: Annotated[ValidatedInt, Query()] = 10):
        return value

    @app.get("/header/default")
    def header_default(value: Annotated[ValidatedInt, Header()] = 10):
        return value

    @app.get("/cookie/default")
    def cookie_default(value: Annotated[ValidatedInt, Cookie()] = 10):
        return value

    @app.post("/form/default")
    def form_default(value: Annotated[ValidatedInt, Form()] = 10):
        return value

    @app.post("/body/default")
    def body_default(value: Annotated[ValidatedInt, Body(embed=True)] = 10):
        return value

    @app.post("/model/default")
    def model_default(value: Annotated[DefaultModel, Body()]):
        return value.value

    @app.get("/query/validate-default")
    def query_validate_default(
        value: Annotated[ValidatedInt, Query(validate_default=True)] = 10,
    ):
        return value

    @app.post("/model/validate-default")
    def model_validate_default(value: Annotated[ValidatedDefaultModel, Body()]):
        return value.value

    @app.post("/body/null-default-none")
    def body_null_default_none(value: Annotated[ValidatedInt, Body()] = None):
        return value

    @app.post("/body/null-default-value")
    def body_null_default_value(value: Annotated[ValidatedInt, Body()] = 10):
        return value

    def parameter_factory() -> str:
        factory_calls["parameter"] += 1
        return "10"

    @app.get("/factory/parameter")
    def parameter_factory_default(
        value: Annotated[
            ValidatedInt,
            Query(default_factory=parameter_factory, validate_default=True),
        ],
    ):
        return {"value": value, "factory_calls": factory_calls["parameter"]}

    def pydantic_field_factory() -> int:
        factory_calls["pydantic_field"] += 1
        return 5

    @app.get("/factory/pydantic-field")
    def pydantic_field_factory_default(
        value: Annotated[int, Field(default_factory=pydantic_field_factory), Query()],
    ):
        return {"value": value, "factory_calls": factory_calls["pydantic_field"]}

    @app.get("/query/invalid-default")
    def invalid_query_default(
        value: Annotated[int, Query(gt=0, validate_default=True)] = -1,
    ):
        return value

    @app.post("/file/unvalidated-default")
    def file_unvalidated_default(
        value: Annotated[bytes, File(min_length=2, validate_default=False)] = b"x",
    ):
        return value

    @app.post("/file/validated-default")
    def file_validated_default(
        value: Annotated[bytes, File(min_length=2, validate_default=True)] = b"x",
    ):
        return value

    return app
