"""Minimal form route for the target-only form parse fault contract."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Form


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.post("/form")
    async def form(name: Annotated[str, Form()]) -> dict[str, str]:
        return {"name": name}

    return app
