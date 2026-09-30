"""Independent response-model input for combined unset and null filtering."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class ProjectionRecord(BaseModel):
    deferred_note: str | None = None
    cleared_note: str | None = None
    phase: str = "active"
    retries: int = 0


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        "/projection/state",
        response_model=ProjectionRecord,
        response_model_exclude_unset=True,
        response_model_exclude_none=True,
    )
    def read_projection() -> ProjectionRecord:
        return ProjectionRecord(cleared_note=None, phase="active")

    return app
