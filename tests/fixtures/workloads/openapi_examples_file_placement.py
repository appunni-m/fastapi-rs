"""OpenAPI example placement for an uploaded file."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/file-example")
    async def upload_file(
        content: Annotated[
            bytes,
            File(
                openapi_examples={
                    "plain-text": {
                        "summary": "A small text file",
                        "value": "maple leaf",
                    }
                }
            ),
        ],
    ) -> dict[str, int]:
        return {"size": len(content)}

    return app
