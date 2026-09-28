"""Pydantic computed response field with either FastAPI schema mode."""

from fastapi import FastAPI
from pydantic import BaseModel, computed_field


def _build_app(*, separate_input_output_schemas: bool) -> FastAPI:
    app = FastAPI(separate_input_output_schemas=separate_input_output_schemas)

    class Rectangle(BaseModel):
        width: int
        length: int

        @computed_field
        @property
        def area(self) -> int:
            return self.width * self.length

    @app.get("/")
    def read_root() -> Rectangle:
        return Rectangle(width=3, length=4)

    @app.get("/responses", responses={200: {"model": Rectangle}})
    def read_responses() -> Rectangle:
        return Rectangle(width=3, length=4)

    return app


def create_app_separate_schemas() -> FastAPI:
    return _build_app(separate_input_output_schemas=True)


def create_app_shared_schemas() -> FastAPI:
    return _build_app(separate_input_output_schemas=False)
