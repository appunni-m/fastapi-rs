"""Build a route that validates an UploadFile request parameter."""

from __future__ import annotations

from fastapi import FastAPI, UploadFile


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/uploadfile-pydantic-validation")
    async def inspect_upload(upload: UploadFile) -> dict[str, str | None]:
        return {"filename": upload.filename}

    return app
