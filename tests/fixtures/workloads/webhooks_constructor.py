"""Independent FastAPI webhook-router constructor workload."""

from fastapi import APIRouter, FastAPI, Security
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse


def create_app() -> FastAPI:
    webhooks = APIRouter(
        tags=["events"],
        dependencies=[Security(HTTPBearer())],
        deprecated=True,
    )

    @webhooks.post("stock-updated")
    def stock_updated():
        return {"accepted": True}

    relative_routes = APIRouter()

    @relative_routes.get("items/{item_id}", name="relative-item")
    def read_relative_item(item_id: str):
        return {"item_id": item_id}

    prefixed_relative_routes = APIRouter(prefix="/v1")

    @prefixed_relative_routes.get("items/{item_id}", name="prefixed-relative-item")
    def read_prefixed_relative_item(item_id: str):
        return {"item_id": item_id}

    hidden_webhooks = APIRouter(include_in_schema=False)

    @hidden_webhooks.post("hidden-event")
    def hidden_event():
        return {"accepted": True}

    hidden_app = FastAPI(webhooks=hidden_webhooks)
    default_webhooks_app = FastAPI(webhooks=None)

    app = FastAPI(title="Stock Events", version="1.0", webhooks=webhooks)
    app.include_router(relative_routes, prefix="/v2")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/_probe/webhook-url")
    async def webhook_url():
        url = webhooks.url_path_for("stock_updated")
        return JSONResponse({"path": str(url), "protocol": url.protocol, "host": url.host})

    @app.get("/_probe/none-webhook-default")
    async def none_webhook_default():
        return {
            "is_router": isinstance(default_webhooks_app.webhooks, APIRouter),
            "is_none": default_webhooks_app.webhooks is None,
        }

    @app.get("/_probe/relative-router-url")
    async def relative_router_url():
        url = app.url_path_for("relative-item", item_id="sku-17")
        return JSONResponse({"path": str(url), "protocol": url.protocol, "host": url.host})

    @app.get("/_probe/prefixed-relative-router-url")
    async def prefixed_relative_router_url():
        url = prefixed_relative_routes.url_path_for("prefixed-relative-item", item_id="sku-17")
        return JSONResponse({"path": str(url), "protocol": url.protocol, "host": url.host})

    @app.get("/_probe/webhook-field")
    async def webhook_field():
        return {"same": app.webhooks is webhooks}

    @app.get("/_probe/hidden-webhook-schema")
    async def hidden_webhook_schema():
        return {"has_webhooks": "webhooks" in hidden_app.openapi()}

    return app
