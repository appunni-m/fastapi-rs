"""Independent ASGI inputs for body null, absence, defaults, and validation."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class RequiredValue(BaseModel):
    value: int | None


_REQUIRED_VALUE_DEFAULT = RequiredValue(value=10)


class NullableDefaultValue(BaseModel):
    value: int | None = None


class NullableConcreteDefaultValue(BaseModel):
    value: int | None = 10


class NonNullableDefaultValue(BaseModel):
    value: int = 10


def create_app() -> FastAPI:
    app = FastAPI()
    factory_calls = {"count": 0}

    @app.post("/embedded/required")
    def embedded_required(value: Annotated[int | None, Body(embed=True)]):
        return {"value": value}

    @app.post("/model/required")
    def model_required(value: Annotated[RequiredValue, Body()]):
        return {"value": value.value, "fields_set": sorted(value.model_fields_set)}

    @app.post("/embedded/nullable-default")
    def embedded_nullable_default(
        value: Annotated[int | None, Body(embed=True)] = None,
    ):
        return {"value": value}

    @app.post("/model/nullable-default")
    def model_nullable_default(value: Annotated[NullableDefaultValue, Body()]):
        return {
            "value": value.value,
            "fields_set": sorted(value.model_fields_set),
        }

    @app.post("/embedded/concrete-default")
    def embedded_concrete_default(
        value: Annotated[int | None, Body(embed=True)] = 10,
    ):
        return {"value": value}

    @app.post("/model/concrete-default")
    def model_concrete_default(value: Annotated[NullableConcreteDefaultValue, Body()]):
        return {
            "value": value.value,
            "fields_set": sorted(value.model_fields_set),
        }

    @app.post("/embedded/nonnullable-default")
    def embedded_nonnullable_default(value: Annotated[int, Body(embed=True)] = 10):
        return {"value": value}

    @app.post("/model/nonnullable-default")
    def model_nonnullable_default(value: Annotated[NonNullableDefaultValue, Body()]):
        return {
            "value": value.value,
            "fields_set": sorted(value.model_fields_set),
        }

    @app.post("/bare/required")
    def bare_required(value: Annotated[int | None, Body()]):
        return value

    @app.post("/bare/nullable-default")
    def bare_nullable_default(value: Annotated[int | None, Body()] = None):
        return value

    @app.post("/bare/concrete-default")
    def bare_concrete_default(value: Annotated[int | None, Body()] = 10):
        return value

    @app.post("/bare/nonnullable-default")
    def bare_nonnullable_default(value: Annotated[int, Body()] = 10):
        return value

    @app.post("/bare/string-default")
    def bare_string_default(value: Annotated[str | None, Body()] = "default"):
        return value

    @app.post("/bare/list-factory")
    def bare_list_factory(
        value: Annotated[list[int] | None, Body(default_factory=lambda: [10])],
    ):
        return value

    def default_factory() -> str:
        factory_calls["count"] += 1
        return "10"

    @app.post("/factory/nullable")
    def factory_nullable(
        value: Annotated[
            int | None,
            Body(default_factory=default_factory, validate_default=True),
        ],
    ):
        return {"value": value, "factory_calls": factory_calls["count"]}

    @app.post("/body/multiple")
    def multiple_body_values(
        value: Annotated[int | None, Body()] = 10,
        other: Annotated[int | None, Body()] = 20,
    ):
        return {"value": value, "other": other}

    def body_dependency(value: Annotated[int | None, Body(alias="input")] = 10):
        return value

    @app.post("/body/dependency-alias")
    def dependency_body_value(
        value: Annotated[int | None, Depends(body_dependency)],
        other: Annotated[int, Body()] = 20,
    ):
        return {"value": value, "other": other}

    @app.post("/model/nullable-raw")
    def nullable_model_raw(
        value: Annotated[RequiredValue | None, Body(embed=False)] = _REQUIRED_VALUE_DEFAULT,
    ):
        return value

    @app.post("/model/nullable-embedded")
    def nullable_model_embedded(
        value: Annotated[RequiredValue | None, Body(embed=True)] = _REQUIRED_VALUE_DEFAULT,
    ):
        return value

    @app.exception_handler(RequestValidationError)
    def validation_details(request: Request, error: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"body": error.body, "detail": error.errors()},
        )

    @app.post("/validation/required-integer")
    def required_integer(value: Annotated[int, Body()]):
        return value

    return app
