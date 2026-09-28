"""Independent request-model workloads for body tutorial fixtures."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


class Record(BaseModel):
    label: str
    cost: float
    notes: str | None = None
    rebate: float | None = None


def create_body_model_only_app() -> FastAPI:
    app = FastAPI()

    @app.put("/records/{record_id}")
    async def replace_record(record_id: int, record: Record):
        return {"record_id": record_id, **record.model_dump()}

    return app


def create_body_model_with_query_app() -> FastAPI:
    app = FastAPI()

    @app.put("/records/{record_id}")
    async def replace_record(record_id: int, record: Record, q: str | None = None):
        result = {"record_id": record_id, **record.model_dump()}
        if q:
            result["q"] = q
        return result

    return app
