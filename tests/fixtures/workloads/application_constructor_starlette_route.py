"""Input-only workload for a Starlette Route passed to FastAPI's constructor."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route


async def constructor_route(_request: Request) -> PlainTextResponse:
    return PlainTextResponse("constructor route served")


def create_app() -> FastAPI:
    route = Route("/constructor-route", constructor_route, methods=["GET"])
    return FastAPI(routes=[route])
