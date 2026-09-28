"""Input-only route for finite and non-finite float validation probes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/")
    async def read_float(
        allow: Annotated[float, Query(allow_inf_nan=True)] = 0,
        reject: Annotated[float, Query(allow_inf_nan=False)] = 0,
        inherited: Annotated[float, Query()] = 0,
        body: Annotated[float, Body(allow_inf_nan=False)] = 0,
    ) -> str:
        return "accepted"

    return app
