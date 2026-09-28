from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import Info


def create_app() -> FastAPI:
    app = FastAPI(
        title="Reference Surface API",
        summary="Public app configuration workload",
        version="2.6",
        docs_url="/reference-ui",
        redoc_url="/reference-redoc",
        openapi_tags=[{"name": "system", "description": "System-facing operations"}],
    )

    @app.get("/system/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"state": "ready"}

    @app.get("/metadata", response_model=Info)
    async def metadata() -> dict[str, str]:
        return {"title": "Inventory Contract", "version": "4.1"}

    @app.get("/manual-ui", include_in_schema=False)
    async def manual_ui():
        return get_swagger_ui_html(openapi_url=app.openapi_url, title="Manual API UI")

    return app
