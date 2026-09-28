"""Small independent stimuli for two reviewed OpenAPI source gaps."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class DeliveryAddress(BaseModel):
    """Public delivery location.\fPrivate routing note."""

    street: str
    locality: str


class FacilityRecord(BaseModel):
    id: str
    address: DeliveryAddress


class InvoiceRecord(BaseModel):
    id: str


class InvoiceNotice(BaseModel):
    accepted: bool


class DeliveryNotice(BaseModel):
    invoice_id: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/facilities/{facility_id}", response_model=FacilityRecord)
    async def get_facility(facility_id: str) -> dict[str, object]:
        return {
            "id": facility_id,
            "address": {"street": "8 Cedar Way", "locality": "Riverton"},
        }

    invoice_callbacks = APIRouter()

    @invoice_callbacks.post("{$callback_url}/invoices/{$request.body.id}")
    async def invoice_notice(notice: InvoiceNotice) -> InvoiceNotice:
        return notice

    event_callbacks = APIRouter()

    @event_callbacks.get("{$callback_url}/events/{$request.body.id}")
    async def delivery_notice(notice: DeliveryNotice) -> DeliveryNotice:
        return notice

    invoice_router = APIRouter()

    @invoice_router.post("/invoices/", callbacks=invoice_callbacks.routes)
    async def submit_invoice(
        invoice: InvoiceRecord, callback_url: str | None = None
    ) -> dict[str, str]:
        return {"id": invoice.id}

    app.include_router(invoice_router, callbacks=event_callbacks.routes)
    return app
