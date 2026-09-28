"""Independent custom request and APIRoute workloads."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute


class InspectRequest(Request):
    """Request subtype used by the app's route wrapper."""


class InspectRoute(APIRoute):
    def get_route_handler(self) -> Callable[..., Any]:
        original_handler = super().get_route_handler()

        async def handle_with_inspect_request(request: Request) -> Response:
            replacement = InspectRequest(request.scope, request.receive)
            return await original_handler(replacement)

        return handle_with_inspect_request


class DurationRoute(APIRoute):
    def get_route_handler(self) -> Callable[..., Any]:
        original_handler = super().get_route_handler()

        async def add_duration_header(request: Request) -> Response:
            started = perf_counter()
            response = await original_handler(request)
            response.headers["X-Response-Time"] = str(perf_counter() - started)
            return response

        return add_duration_header


def create_app() -> FastAPI:
    app = FastAPI()
    app.router.route_class = InspectRoute

    @app.post("/summarize")
    async def summarize_numbers(request: Request, values: list[int]) -> dict[str, object]:
        return {"request_type": type(request).__name__, "total": sum(values)}

    @app.get("/")
    async def standard_response() -> dict[str, str]:
        return {"message": "A plain response"}

    timed_router = APIRouter(route_class=DurationRoute)

    @timed_router.get("/measured")
    async def measured_response() -> dict[str, str]:
        return {"message": "A measured response"}

    app.include_router(timed_router)
    return app
