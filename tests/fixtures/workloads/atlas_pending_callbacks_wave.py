"""Independent callback routes for selected callback OpenAPI observations."""

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, HttpUrl


class Invoice(BaseModel):
    id: str
    customer: str
    total: float


class InvoiceNotice(BaseModel):
    description: str
    paid: bool


class NoticeAccepted(BaseModel):
    accepted: bool


class Event(BaseModel):
    name: str
    total: float


def create_app() -> FastAPI:
    app = FastAPI()

    invoice_callbacks = APIRouter()

    @invoice_callbacks.post("{$callback_url}/invoices/{$request.body.id}")
    def invoice_notice(notice: InvoiceNotice) -> NoticeAccepted:
        return NoticeAccepted(accepted=True)

    event_callbacks = APIRouter()

    @event_callbacks.get("{$callback_url}/events/{$request.body.name}")
    def event_notice(event: Event):
        return {"accepted": event.name}

    invoice_router = APIRouter()

    @invoice_router.post("/invoices/", callbacks=invoice_callbacks.routes)
    def create_invoice(invoice: Invoice, callback_url: HttpUrl | None = None):
        return {"message": "invoice accepted", "id": invoice.id}

    app.include_router(invoice_router, callbacks=event_callbacks.routes)
    return app
