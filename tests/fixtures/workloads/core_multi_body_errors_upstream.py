"""Independent request workload for list-model and decimal validation."""

from __future__ import annotations

from decimal import Decimal

from fastapi import FastAPI
from pydantic import BaseModel, condecimal


class InventoryRow(BaseModel):
    label: str
    quantity: condecimal(gt=Decimal("0.0"))


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/inventory/rows")
    def accept_rows(rows: list[InventoryRow]) -> dict[str, list[InventoryRow]]:
        return {"rows": rows}

    return app
