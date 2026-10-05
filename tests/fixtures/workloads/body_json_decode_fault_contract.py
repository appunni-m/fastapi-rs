"""Minimal route workload for the target-only JSON body decode fault contract."""

from __future__ import annotations

from fastapi import FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.post("/body")
    async def body(payload: dict[str, object]) -> dict[str, str]:
        return {"status": "ok"}

    return app
