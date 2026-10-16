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
    app_defaults = APIRouter()

    @app_defaults.get("{$callback_url}/app-default/{$request.body.name}")
    def app_default_notice(event: Event):
        return {"accepted": event.name}

    app = FastAPI(callbacks=app_defaults.routes)

    invoice_callbacks = APIRouter()

    @invoice_callbacks.post("{$callback_url}/invoices/{$request.body.id}")
    def invoice_notice(notice: InvoiceNotice) -> NoticeAccepted:
        return NoticeAccepted(accepted=True)

    event_callbacks = APIRouter()

    @event_callbacks.get("{$callback_url}/events/{$request.body.name}")
    def event_notice(event: Event):
        return {"accepted": event.name}

    router_defaults = APIRouter()

    @router_defaults.get("{$callback_url}/router-default/{$request.body.name}")
    def router_default_notice(event: Event):
        return {"accepted": event.name}

    include_callbacks = APIRouter()

    @include_callbacks.get("{$callback_url}/include/{$request.body.name}")
    def include_notice(event: Event):
        return {"accepted": event.name}

    parent_defaults = APIRouter()

    @parent_defaults.get("{$callback_url}/parent-default/{$request.body.name}")
    def parent_default_notice(event: Event):
        return {"accepted": event.name}

    invoice_router = APIRouter(callbacks=router_defaults.routes)

    @invoice_router.post("/invoices/", callbacks=invoice_callbacks.routes)
    def create_invoice(invoice: Invoice, callback_url: HttpUrl | None = None):
        return {"message": "invoice accepted", "id": invoice.id}

    parent_router = APIRouter(callbacks=parent_defaults.routes)
    parent_router.include_router(invoice_router, callbacks=include_callbacks.routes)
    app.include_router(parent_router, callbacks=event_callbacks.routes)
    return app
