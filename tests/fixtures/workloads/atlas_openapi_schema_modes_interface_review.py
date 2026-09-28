"""Independent inputs for separate and shared OpenAPI model schemas."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Record(BaseModel):
    label: str
    summary: str | None = None


def _records_app(*, separate: bool) -> FastAPI:
    app = FastAPI(
        title="Schema Mode Probe",
        version="3.7",
        separate_input_output_schemas=separate,
    )

    @app.post("/records/")
    def create_record(record: Record):
        return record

    @app.get("/records/")
    def read_records() -> list[Record]:
        return [
            Record(
                label="Nebula",
                summary="First stored record",
            ),
            Record(label="Orbit"),
        ]

    return app


def create_app() -> FastAPI:
    root = FastAPI(openapi_url=None)
    root.mount("/split", _records_app(separate=True))
    root.mount("/shared", _records_app(separate=False))
    return root
