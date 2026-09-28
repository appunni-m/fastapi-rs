"""Observe request-scoped UploadFile cleanup through a follow-up HTTP request."""

from __future__ import annotations

from fastapi import FastAPI, UploadFile


def create_app() -> FastAPI:
    app = FastAPI()
    uploads: list[UploadFile] = []

    @app.post("/uploadfile/")
    async def receive_upload(file: UploadFile) -> dict[str, str | None]:
        uploads.append(file)
        return {"filename": file.filename}

    @app.get("/upload-state/")
    async def upload_state() -> dict[str, bool | None]:
        if not uploads:
            return {"closed": None}
        return {"closed": uploads[0].file.closed}

    return app
