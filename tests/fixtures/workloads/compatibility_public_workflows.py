"""Exercise public FastAPI body validation with Pydantic v2 model settings."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict


class UnsetMarker:
    def __bool__(self) -> bool:
        return False


class NestedOptions(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    label: str | UnsetMarker = UnsetMarker()


class Options(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    label: str | UnsetMarker = UnsetMarker()
    nested: NestedOptions = NestedOptions()


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/flexible-value")
    def accept_flexible_value(value: str | list[int]) -> str | list[int]:
        return value

    @app.post("/options")
    def resolve_options(options: Options) -> dict[str, str | None]:
        label = None if isinstance(options.label, UnsetMarker) else options.label
        nested_label = (
            None if isinstance(options.nested.label, UnsetMarker) else options.nested.label
        )
        return {"label": label, "nested_label": nested_label}

    return app
