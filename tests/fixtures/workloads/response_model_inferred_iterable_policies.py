"""Independent inputs for inferred iterable response-model policy probes."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import FastAPI
from pydantic import BaseModel


class PolicyItem(BaseModel):
    omitted_null: str | None = None
    explicit_null: str | None = None
    preferred: str = "preferred"
    fallback: str = "fallback"


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/iterable/exclude-unset", response_model_exclude_unset=True)
    def exclude_unset() -> Iterable[PolicyItem]:
        return [PolicyItem(explicit_null=None, preferred="preferred")]

    @app.get("/iterable/exclude-defaults", response_model_exclude_defaults=True)
    def exclude_defaults() -> Iterable[PolicyItem]:
        return [PolicyItem(explicit_null=None, preferred="preferred")]

    @app.get("/iterable/exclude-none", response_model_exclude_none=True)
    def exclude_none() -> Iterable[PolicyItem]:
        return [PolicyItem(explicit_null=None, preferred="preferred")]

    return app
