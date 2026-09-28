"""Independent OpenAPI and documentation routes for guide-derived inputs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, HttpUrl


class CallbackMessage(BaseModel):
    event_id: str
    state: str


class SubscriptionRequest(BaseModel):
    callback_url: HttpUrl
    event_id: str


class NewRecord(BaseModel):
    title: str


class RecordResult(BaseModel):
    record_id: int
    title: str
    audit_marker: str


def create_app() -> FastAPI:
    app = FastAPI(
        title="Guide OpenAPI Workload",
        version="3.6",
        openapi_tags=[
            {"name": "records", "description": "Record operations for the sample API"},
            {"name": "events", "description": "Event delivery callbacks"},
        ],
        contact={"name": "API Support", "url": "https://example.invalid/support"},
        swagger_ui_parameters={"displayRequestDuration": True, "filter": True},
    )

    @app.get("/records/{record_id}", response_model=RecordResult, tags=["records"])
    async def read_record(record_id: int) -> dict[str, Any]:
        return {"record_id": record_id, "title": "Field notes", "audit_marker": "visible"}

    @app.post("/records", response_model=RecordResult, tags=["records"])
    async def create_record(record: NewRecord) -> dict[str, Any]:
        return {"record_id": 28, "title": record.title, "audit_marker": "created"}

    @app.get("/custom-docs", include_in_schema=False)
    async def custom_docs() -> Any:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title="Guide API Explorer",
            swagger_js_url="/assets/swagger-ui-bundle.js",
            swagger_css_url="/assets/swagger-ui.css",
            swagger_ui_parameters={"displayOperationId": True},
        )

    callback_routes = APIRouter()

    @callback_routes.post("{$request.body#/callback_url}", response_model=CallbackMessage)
    async def receive_callback(message: CallbackMessage) -> CallbackMessage:
        return message

    @app.post("/subscriptions", callbacks=callback_routes.routes, tags=["events"])
    async def subscribe(subscription: SubscriptionRequest) -> dict[str, str]:
        return {"state": "registered"}

    disabled_schema = FastAPI(
        title="Hidden Schema Workload",
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    @disabled_schema.get("/status")
    async def hidden_schema_status() -> dict[str, str]:
        return {"status": "private"}

    app.mount("/without-schema", disabled_schema)

    original_openapi = app.openapi

    def extended_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = original_openapi()
        schema["info"]["x-guide-section"] = "openapi-extension"
        schema["x-guide-revision"] = 3
        app.openapi_schema = schema
        return schema

    app.openapi = extended_openapi
    return app
