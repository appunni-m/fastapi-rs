"""Independent default and custom OpenAPI document inputs from the guide."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def create_app(factory_input: dict[str, Any], _event_trace: list[str]) -> FastAPI:
    app = FastAPI(
        title="Atlas Parcel Interface",
        version="8.4",
        summary="A compact parcel index",
        description="An independently assembled interface for parcel lookup.",
    )

    @app.get("/parcels/{parcel_id}")
    async def read_parcel(parcel_id: int) -> dict[str, Any]:
        return {"parcel_id": parcel_id, "label": "North Archive"}

    if factory_input["scenario"] == "custom":

        def custom_openapi() -> dict[str, Any]:
            if app.openapi_schema:
                return app.openapi_schema
            schema = get_openapi(
                title="Custom Parcel Catalog",
                version="9.3",
                summary="An independently reviewed parcel API",
                description="Parcel lookup metadata assembled for a documentation probe.",
                routes=app.routes,
            )
            schema["info"]["x-logo"] = {"url": "https://example.invalid/assets/parcel-mark.svg"}
            app.openapi_schema = schema
            return app.openapi_schema

        app.openapi = custom_openapi

    return app
