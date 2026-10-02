"""Independent request inputs for full replacement and partial update behavior."""

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class StockRecord(BaseModel):
    label: str | None = None
    note: str | None = None
    quantity: int | None = None
    unit_cost: float = 7.25
    flags: list[str] = []


def create_app() -> FastAPI:
    app = FastAPI()
    records = {
        "part-17": {
            "label": "before-update",
            "note": "retain this note",
            "quantity": 6,
            "unit_cost": 3.75,
            "flags": ["seeded"],
        }
    }

    @app.put("/records/{record_id}", response_model=StockRecord)
    async def replace_record(record_id: str, record: StockRecord):
        encoded_record = jsonable_encoder(record)
        records[record_id] = encoded_record
        return encoded_record

    @app.patch("/records/{record_id}")
    async def patch_record(record_id: str, record: StockRecord) -> StockRecord:
        stored_record = StockRecord(**records[record_id])
        update_data = record.model_dump(exclude_unset=True)
        updated_record = stored_record.model_copy(update=update_data)
        records[record_id] = jsonable_encoder(updated_record)
        return updated_record

    return app
