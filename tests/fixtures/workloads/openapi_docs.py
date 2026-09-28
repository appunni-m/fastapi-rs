"""Independent docs routes and mounted applications for documentation inputs."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)


def _custom_docs_app(title: str, *, oauth_client: str) -> FastAPI:
    child = FastAPI(
        title=title,
        version="5.0",
        docs_url="/swagger",
        redoc_url="/reference",
        openapi_url="/schema.json",
        swagger_ui_parameters={"displayRequestDuration": True, "filter": True},
        swagger_ui_init_oauth={"clientId": oauth_client, "usePkceWithAuthorizationCodeGrant": True},
    )

    @child.get("/status")
    async def child_status() -> dict[str, str]:
        return {"status": "active"}

    @child.get("/manual-swagger", include_in_schema=False)
    async def manual_swagger() -> Any:
        return get_swagger_ui_html(
            openapi_url=child.openapi_url or "/schema.json",
            title=f"{title} Manual Explorer",
            oauth2_redirect_url="/auth-redirect",
            swagger_js_url="/assets/swagger-ui-bundle.js",
            swagger_css_url="/assets/swagger-ui.css",
            swagger_ui_parameters={"displayOperationId": True},
        )

    @child.get("/manual-redirect", include_in_schema=False)
    async def manual_redirect() -> Any:
        return get_swagger_ui_oauth2_redirect_html()

    @child.get("/manual-reference", include_in_schema=False)
    async def manual_reference() -> Any:
        return get_redoc_html(
            openapi_url=child.openapi_url or "/schema.json",
            title=f"{title} Manual Reference",
            redoc_js_url="/assets/redoc.standalone.js",
        )

    return child


def create_app() -> FastAPI:
    app = FastAPI(
        title="Documentation Workload",
        version="4.2",
        servers=[{"url": "https://api.example.invalid/v4", "description": "Configured base"}],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"state": "ready"}

    custom_ui = _custom_docs_app("Custom UI One", oauth_client="client-one")
    custom_oauth_ui = _custom_docs_app("Custom UI Two", oauth_client="client-two")
    app.mount("/ui-one", custom_ui)
    app.mount("/ui-two", custom_oauth_ui)

    disabled = FastAPI(openapi_url=None)

    @disabled.get("/")
    async def disabled_root() -> dict[str, str]:
        return {"mode": "disabled"}

    enabled = FastAPI(title="Enabled Subapplication")

    @enabled.get("/")
    async def enabled_root() -> dict[str, str]:
        return {"mode": "enabled"}

    app.mount("/conditional/disabled", disabled)
    app.mount("/conditional/enabled", enabled)

    callback_router = FastAPI()

    @callback_router.get("/notify")
    async def callback_notice() -> dict[str, str]:
        return {"state": "notified"}

    @app.post(
        "/events",
        callbacks=[
            # Callback paths use a runtime-provided URL expression.
            callback_router.routes[0],
        ],
    )
    async def create_event(callback_url: str) -> dict[str, str]:
        return {"state": "created"}

    @app.webhooks.post("record-updated")
    async def record_updated(payload: dict[str, Any]) -> None:
        return None

    original_openapi = app.openapi

    def extended_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = original_openapi()
        schema["info"]["x-workload-group"] = "docs-and-schema"
        schema["x-workload-revision"] = 2
        app.openapi_schema = schema
        return schema

    app.openapi = extended_openapi
    return app
