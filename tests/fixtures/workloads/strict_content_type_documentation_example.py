"""Independent request workload for the strict Content-Type documentation example."""

from fastapi import FastAPI
from pydantic import BaseModel


class LegacyRecord(BaseModel):
    label: str
    quantity: int


def create_app() -> FastAPI:
    app = FastAPI(strict_content_type=False)

    @app.post("/legacy/items/")
    async def create_legacy_item(record: LegacyRecord) -> LegacyRecord:
        return record

    return app
