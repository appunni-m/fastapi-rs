"""Input-driven form validation using FastAPI's deprecated regex keyword."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Form


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/reference/")
    async def read_reference(
        reference: Annotated[str | None, Form(regex=r"^ref-[0-9]{2}$")] = None,
    ) -> str:
        if reference:
            return f"Accepted {reference}"
        return "No reference"

    return app
