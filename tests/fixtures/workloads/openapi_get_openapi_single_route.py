"""Independent single-route input for direct FastAPI get_openapi parity."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.routing import APIRoute


def standalone_items():
    return {"items": []}


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Build native route inputs as public arguments; expected output stays in results."""
    router = APIRouter()
    tagged_router = APIRouter()
    webhook_router = APIRouter()
    unusual_name_router = APIRouter()

    @router.get("/items")
    def items():
        return {"items": []}

    @tagged_router.get("/catalog", tags=["catalog"])
    def catalog():
        return {"items": []}

    def stock_updated():
        return {"accepted": True}

    webhook_router.add_api_route("stock-updated", stock_updated, methods=["GET"])

    @unusual_name_router.get("/http2-status")
    def get_HTTP2_v2_status():
        return {"status": "ok"}

    return {
        "single-route": {
            "args": [],
            "kwargs": {
                "title": "Single Route OpenAPI Probe",
                "version": "1.0.0",
                "routes": router.routes,
            },
        },
        "tagged-route": {
            "args": [],
            "kwargs": {
                "title": "Tagged Route OpenAPI Probe",
                "version": "2.0.0",
                "routes": tagged_router.routes,
            },
        },
        "webhook-route": {
            "args": [],
            "kwargs": {
                "title": "Webhook Route OpenAPI Probe",
                "version": "1.0.0",
                "routes": router.routes,
                "webhooks": webhook_router.routes,
            },
        },
        "unusual-endpoint-name": {
            "args": [],
            "kwargs": {
                "title": "Endpoint Summary Case Probe",
                "version": "1.0.0",
                "routes": unusual_name_router.routes,
            },
        },
        "standalone-route": {
            "args": ["/direct-items", standalone_items],
            "kwargs": {},
        },
        "standalone-apiroute": {
            "args": [],
            "kwargs": {
                "title": "Standalone APIRoute OpenAPI Probe",
                "version": "1.0.0",
                "routes": [APIRoute("/direct-items", standalone_items)],
            },
        },
    }
