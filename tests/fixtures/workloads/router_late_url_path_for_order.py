"""Probe name-based reversal across a late router inclusion slot."""

from fastapi import APIRouter, FastAPI
from starlette.responses import PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI()
    routes = APIRouter()
    app.include_router(routes)

    @app.get("/direct/{item_id}", name="duplicate-lookup")
    def direct_lookup(item_id: str) -> dict[str, str]:
        return {"source": "direct", "item_id": item_id}

    @routes.get("/included/{item_id}", name="duplicate-lookup")
    def included_lookup(item_id: str) -> dict[str, str]:
        return {"source": "included", "item_id": item_id}

    resolved_path = str(app.url_path_for("duplicate-lookup", item_id="record-1"))

    @app.get("/_probe/route-order-url")
    def probe_route_order_url() -> PlainTextResponse:
        return PlainTextResponse(resolved_path)

    return app
