"""Input-only workload for a prefixed APIRouter constructor route."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route


async def read_items(_request: Request) -> PlainTextResponse:
    return PlainTextResponse("items from constructor route")


def create_app() -> FastAPI:
    router = APIRouter(routes=[Route("/items", read_items, methods=["GET"])])
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app
