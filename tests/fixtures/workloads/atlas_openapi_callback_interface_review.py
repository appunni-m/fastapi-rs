"""Independent callback route and OpenAPI callback inputs."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, HttpUrl


class Transfer(BaseModel):
    reference: str
    recipient: str
    amount: float


class TransferEvent(BaseModel):
    state: str
    settled: bool


class TransferReceipt(BaseModel):
    accepted: bool


def create_app() -> FastAPI:
    app = FastAPI(title="Transfer Interface Probe", version="3.7")
    callback_routes = APIRouter()

    @callback_routes.post(
        "{$notification_url}/transfers/{$request.body.reference}",
        response_model=TransferReceipt,
    )
    def transfer_notification(body: TransferEvent):
        return {"accepted": True}

    @app.post("/transfers/", callbacks=callback_routes.routes)
    def create_transfer(
        transfer: Transfer,
        notification_url: HttpUrl | None = None,
    ):
        return {"state": "received"}

    return app
