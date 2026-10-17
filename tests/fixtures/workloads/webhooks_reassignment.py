"""Probe replacing the FastAPI webhook router before OpenAPI generation."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    constructor_webhooks = APIRouter()

    @constructor_webhooks.post("constructor-event", operation_id="constructor_event")
    async def constructor_event():
        return {"source": "constructor"}

    replacement_webhooks = APIRouter()

    @replacement_webhooks.post("reassigned-event", operation_id="reassigned_event")
    async def reassigned_event():
        return {"source": "replacement"}

    app = FastAPI(
        title="Webhook Reassignment",
        version="1.0",
        webhooks=constructor_webhooks,
    )
    app.webhooks = replacement_webhooks

    @app.get("/_probe/webhook-identity")
    async def webhook_identity():
        return {"same": app.webhooks is replacement_webhooks}

    return app
