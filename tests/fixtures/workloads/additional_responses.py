"""Independently authored additional-response and OpenAPI workload."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class InventoryItem(BaseModel):
    sku: str
    label: str


class Unavailable(BaseModel):
    code: str
    message: str


class VendorJSONResponse(JSONResponse):
    media_type = "application/vnd.fastapi-rs.inventory+json"


def create_app() -> FastAPI:
    app = FastAPI(title="Warehouse API", version="1.0.0")

    @app.get(
        "/inventory/{sku}",
        response_model=InventoryItem,
        response_class=VendorJSONResponse,
        responses={
            404: {
                "model": Unavailable,
                "description": "The requested stock keeping unit is unavailable.",
            }
        },
    )
    async def read_inventory_item(sku: str) -> dict[str, str] | VendorJSONResponse:
        if sku == "R-404":
            return VendorJSONResponse(
                status_code=404,
                content={"code": "missing", "message": "No inventory record."},
            )
        return {"sku": sku, "label": "Copper kettle", "internal_cost": "18.00"}

    return app
