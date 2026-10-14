"""OpenAPI example placement for a form field."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Form


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/form-example")
    async def submit_form(
        value: Annotated[
            str,
            Form(
                openapi_examples={
                    "short-text": {
                        "summary": "A short form value",
                        "value": "maple",
                    }
                }
            ),
        ],
    ) -> dict[str, str]:
        return {"value": value}

    return app
