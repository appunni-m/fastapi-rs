"""Focused ASGI workload for included-router slash redirect ordering."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    redirect_router = APIRouter()
    exact_router = APIRouter()

    @redirect_router.get("/items/")
    def read_items_with_slash():
        return {"path": "slash"}

    @exact_router.get("/items")
    def read_items_without_slash():
        return {"path": "exact"}

    app = FastAPI()
    app.include_router(redirect_router, prefix="/api")
    app.include_router(exact_router, prefix="/api")
    return app
