"""Input workload for paths composed from router and include prefixes."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    router = APIRouter(prefix="/tenants/{tenant_id}")

    @router.get("/items/{item_id}")
    def read_item(version: int, tenant_id: int, item_id: int):
        return {"version": version, "tenant_id": tenant_id, "item_id": item_id}

    app = FastAPI()
    app.include_router(router, prefix="/api/{version}")
    return app
