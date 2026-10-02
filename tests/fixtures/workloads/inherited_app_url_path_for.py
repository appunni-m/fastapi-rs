"""Independent route-reversal input for FastAPI's inherited application API."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from starlette.responses import PlainTextResponse


def create_app() -> FastAPI:
    app = FastAPI()
    catalog = APIRouter()
    app.include_router(catalog, prefix="/v2")

    @catalog.get("/items/{item_id}", name="catalog-item")
    def read_catalog_item(item_id: str):
        return {"item_id": item_id}

    @app.get("/_probe/app-path")
    def app_path():
        return PlainTextResponse(str(app.url_path_for("catalog-item", item_id="sku-901")))

    return app
