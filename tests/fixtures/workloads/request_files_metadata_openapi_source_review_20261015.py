"""Independent OpenAPI workload for documented file descriptions."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, UploadFile


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/files/")
    async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
        return {"file_size": len(file)}

    @app.post("/uploadfile/")
    async def create_upload_file(
        file: Annotated[UploadFile, File(description="A file read as UploadFile")],
    ):
        return {"filename": file.filename}

    @app.post("/multiple-files/")
    async def create_multiple_files(
        files: Annotated[list[bytes], File(description="Multiple files as bytes")],
    ):
        return {"file_sizes": [len(file) for file in files]}

    @app.post("/multiple-uploadfiles/")
    async def create_multiple_upload_files(
        files: Annotated[
            list[UploadFile],
            File(description="Multiple files as UploadFile"),
        ],
    ):
        return {"filenames": [file.filename for file in files]}

    return app
