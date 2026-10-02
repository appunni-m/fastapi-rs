"""Independent app-level and router-level strict content type configuration."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI(strict_content_type=True)

    @app.post("/app-default/items/")
    async def app_default_post(data: dict) -> dict:
        return data

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

    lax_app = FastAPI(strict_content_type=False)

    @lax_app.post("/items/")
    async def lax_app_post(data: dict) -> dict:
        return data

    lax_outer = APIRouter(prefix="/outer")
    lax_app_strict_inner = APIRouter(prefix="/strict", strict_content_type=True)
    lax_app_default_inner = APIRouter(prefix="/default")

    @lax_app_strict_inner.post("/items/")
    async def lax_app_strict_inner_post(data: dict) -> dict:
        return data

    @lax_app_default_inner.post("/items/")
    async def lax_app_default_inner_post(data: dict) -> dict:
        return data

    lax_outer.include_router(lax_app_strict_inner)
    lax_outer.include_router(lax_app_default_inner)
    lax_app.include_router(lax_outer)
    app.mount("/app-lax", lax_app)

    mixed_app = FastAPI(strict_content_type=True)
    mixed_lax_outer = APIRouter(prefix="/outer", strict_content_type=False)
    mixed_strict_inner = APIRouter(prefix="/inner", strict_content_type=True)

    @mixed_lax_outer.post("/items/")
    async def mixed_lax_outer_post(data: dict) -> dict:
        return data

    @mixed_strict_inner.post("/items/")
    async def mixed_strict_inner_post(data: dict) -> dict:
        return data

    mixed_lax_outer.include_router(mixed_strict_inner)
    mixed_app.include_router(mixed_lax_outer)
    app.mount("/mixed-app", mixed_app)
    return app
