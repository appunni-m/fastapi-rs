"""Independent ASGI stimuli for router prefixes and nested inclusion."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    tenant_router = APIRouter(prefix="/tenants/{tenant_id}")

    @tenant_router.get("/items/{item_id}")
    def read_tenant_item(version: int, tenant_id: int, item_id: int):
        return {"version": version, "tenant_id": tenant_id, "item_id": item_id}

    app.include_router(tenant_router, prefix="/api/{version}")

    shared_router = APIRouter()

    @shared_router.get("/items")
    def read_shared_items():
        return []

    parent_router = APIRouter()
    parent_router.include_router(shared_router, prefix="/a")
    parent_router.include_router(shared_router, prefix="/b")
    app.include_router(parent_router, prefix="/v1")
    app.include_router(parent_router, prefix="/v2")

    return app
