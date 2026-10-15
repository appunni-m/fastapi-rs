"""Build a small FastAPI app for the public TestClient request workflow."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        event_trace.append("startup")
        try:
            yield
        finally:
            event_trace.append("shutdown")

    application = FastAPI(lifespan=lifespan)

    @application.get("/probe")
    async def probe(request: Request) -> Response:
        event_trace.append("request")
        return Response(content=request.url.query.encode("ascii"), status_code=200)

    return application
