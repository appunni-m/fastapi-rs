"""Independent input workload for the custom APIRoute class documentation section."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute


class MarkedRoute(APIRoute):
    def get_route_handler(self) -> Callable[..., Any]:
        original_handler = super().get_route_handler()

        async def add_route_marker(request: Request) -> Response:
            response = await original_handler(request)
            response.headers["X-Route-Class"] = "router-custom"
            return response

        return add_route_marker


def create_app() -> FastAPI:
    app = FastAPI()
    router = APIRouter(route_class=MarkedRoute)

    @router.get("/router-route")
    async def read_router_route() -> dict[str, str]:
        return {"route": "router"}

    app.include_router(router)
    return app
