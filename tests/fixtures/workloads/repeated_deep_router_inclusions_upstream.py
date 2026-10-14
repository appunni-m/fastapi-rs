"""Build the repeated nested-router graph used by the pinned OpenAPI case."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    shared_router = APIRouter()

    @shared_router.get("/items")
    def read_items() -> list[object]:
        return []

    parent_router = APIRouter()
    parent_router.include_router(shared_router, prefix="/a")
    parent_router.include_router(shared_router, prefix="/b")

    app = FastAPI()
    app.include_router(parent_router, prefix="/v1")
    app.include_router(parent_router, prefix="/v2")
    return app
