"""Independent response-model inputs for default and exclusion policies."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class NestedProjection(BaseModel):
    note: str | None = "uninitialized"


class BaseProjection(BaseModel):
    identifier: int | None = None
    nested: NestedProjection


class ExtendedProjection(BaseProjection):
    internal_label: str
    weight: int = 0
    optional_tag: str | None = None


class FilterProjection(BaseModel):
    omitted_note: str | None = None
    visible_note: str | None = None
    phase: str = "draft"
    attempts: int = 0


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/subclass-projection",
        response_model=BaseProjection,
        response_model_exclude_unset=True,
    )
    def subclass_projection() -> ExtendedProjection:
        return ExtendedProjection(nested={}, internal_label="internal", weight=0)

    @app.get(
        "/exclude-unset",
        response_model=FilterProjection,
        response_model_exclude_unset=True,
    )
    def exclude_unset() -> FilterProjection:
        return FilterProjection(visible_note=None, phase="draft")

    @app.get(
        "/exclude-defaults",
        response_model=FilterProjection,
        response_model_exclude_defaults=True,
    )
    def exclude_defaults() -> FilterProjection:
        return FilterProjection(visible_note=None, phase="draft")

    @app.get(
        "/exclude-none",
        response_model=FilterProjection,
        response_model_exclude_none=True,
    )
    def exclude_none() -> FilterProjection:
        return FilterProjection(visible_note=None, phase="draft")

    return app
