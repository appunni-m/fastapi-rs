"""Input-only workload for constructor-supplied Starlette route dispatch."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route


async def constructor_route(_request: Request) -> PlainTextResponse:
    return PlainTextResponse("constructor route served")


async def fastapi_get_route() -> PlainTextResponse:
    return PlainTextResponse("FastAPI route served")


def create_app() -> FastAPI:
    post_route = Route("/constructor-route", constructor_route, methods=["POST"])
    app = FastAPI(routes=[post_route])
    app.get("/constructor-route", response_class=PlainTextResponse)(fastapi_get_route)
    return app
