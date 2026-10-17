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

    after_cache_webhooks = APIRouter()

    @after_cache_webhooks.post("after-cache-event", operation_id="after_cache_event")
    async def after_cache_event():
        return {"source": "after-cache"}

    app = FastAPI(
        title="Webhook Reassignment",
        version="1.0",
        webhooks=constructor_webhooks,
    )
    app.webhooks = replacement_webhooks

    @app.get("/_probe/webhook-identity")
    async def webhook_identity():
        return {"same": app.webhooks is replacement_webhooks}

    @app.post("/_probe/replace-webhooks-after-cache")
    async def replace_webhooks_after_cache():
        app.webhooks = after_cache_webhooks
        return {"same": app.webhooks is after_cache_webhooks}

    return app
