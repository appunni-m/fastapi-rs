"""Observe APIRouter.add_api_route route-class fallback and override behavior."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute


class DefaultRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def default_handler(request):
            response = await original(request)
            response.headers["x-selected-route-class"] = "default"
            return response

        return default_handler


class OverrideRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def override_handler(request):
            response = await original(request)
            response.headers["x-selected-route-class"] = "override"
            return response

        return override_handler


def create_app() -> FastAPI:
    router = APIRouter(route_class=DefaultRoute)

    def default_endpoint() -> dict[str, str]:
        return {"route": "default"}

    def override_endpoint() -> dict[str, str]:
        return {"route": "override"}

    router.add_api_route("/override", override_endpoint, route_class_override=OverrideRoute)
    router.add_api_route("/default", default_endpoint)

    app = FastAPI()
    app.include_router(router)
    return app
