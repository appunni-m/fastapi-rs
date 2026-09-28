"""Input workload for a Starlette Host route included without a prefix."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.responses import PlainTextResponse
from starlette.routing import Host, Route, Router


def create_app() -> FastAPI:
    def hosted_endpoint(request):
        return PlainTextResponse("hosted")

    hosted_app = Router(routes=[Route("/items/{item_id}", hosted_endpoint, name="read_item")])
    router = APIRouter(routes=[Host("{subdomain}.example.com", hosted_app, name="hosted")])
    app = FastAPI()
    app.include_router(router)
    return app
