"""Exercise response-model alias serialization on a POST route."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field


class PublicRecord(BaseModel):
    record_name: str = Field(alias="publicName")


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/records", response_model=PublicRecord)
    def create_record() -> dict[str, str]:
        return {"publicName": "citrine"}

    return app
