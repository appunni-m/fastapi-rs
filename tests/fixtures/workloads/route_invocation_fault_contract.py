"""Small public route workload for target-only route fault contracts."""

from __future__ import annotations

from fastapi import FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[dict[str, object]]) -> FastAPI:
    app = FastAPI()

    @app.get("/fault")
    async def route() -> dict[str, str]:
        return {"status": "ok"}

    return app
