"""Independent ASGI stimulus for FastAPI slash-policy forwarding."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI


def create_app(factory_input: Mapping[str, Any], _event_trace: list[str]) -> FastAPI:
    app = FastAPI(**factory_input)

    @app.get("/catalog/")
    async def catalog() -> str:
        return "catalog ready"

    return app
