"""Independent app-level and router-level strict content type configuration."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI(strict_content_type=True)

    router_lax = APIRouter(prefix="/lax", strict_content_type=False)
    router_strict = APIRouter(prefix="/strict", strict_content_type=True)
    router_default = APIRouter(prefix="/default")

    @router_lax.post("/items/")
    async def router_lax_post(data: dict) -> dict:
        return data

    @router_strict.post("/items/")
    async def router_strict_post(data: dict) -> dict:
        return data

    @router_default.post("/items/")
    async def router_default_post(data: dict) -> dict:
        return data

    app.include_router(router_lax)
    app.include_router(router_strict)
    app.include_router(router_default)
    return app
