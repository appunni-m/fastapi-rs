"""Input workload for per-route strict Content-Type behavior."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


class Payload(BaseModel):
    value: int


async def echo_payload(payload: Payload) -> Payload:
    return payload


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI(strict_content_type=False)

    @app.post("/app/inherited")
    async def app_inherited(payload: Payload) -> Payload:
        return payload

    app.add_api_route(
        "/app/add-inherited",
        echo_payload,
        methods=["POST"],
    )

    router = APIRouter(prefix="/router", strict_content_type=True)

    @router.post("/inherited")
    async def router_inherited(payload: Payload) -> Payload:
        return payload

    router.add_api_route(
        "/add-lax",
        echo_payload,
        methods=["POST"],
        strict_content_type=False,
    )
    router.add_api_route(
        "/add-strict",
        echo_payload,
        methods=["POST"],
        strict_content_type=True,
    )
    app.include_router(router)
    return app
