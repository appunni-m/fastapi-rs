"""Input-only APIKeyHeader constructor and falsey-option workload."""

from typing import Any

from fastapi import FastAPI, Security
from fastapi.security import APIKeyHeader


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    api_key = APIKeyHeader(**factory_input)
    app = FastAPI()

    @app.get("/protected")
    async def read_protected(key: str | None = Security(api_key)) -> dict[str, str | None]:
        return {"key": key}

    return app
