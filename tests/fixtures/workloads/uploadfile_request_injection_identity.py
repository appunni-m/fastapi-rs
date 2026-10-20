"""Observe the UploadFile object shared by multipart parsing and FastAPI injection."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/uploadfile-request-injection")
    async def upload_file_identity(
        request: Request,
        upload: Annotated[UploadFile, File()],
    ) -> dict[str, object]:
        parsed_upload = (await request.form())["upload"]
        content = await upload.read()
        return {
            "same_object": upload is parsed_upload,
            "is_fastapi_upload_file": isinstance(upload, UploadFile),
            "is_starlette_upload_file": isinstance(upload, StarletteUploadFile),
            "type_module": type(upload).__module__,
            "type_qualname": type(upload).__qualname__,
            "filename": upload.filename,
            "size": upload.size,
            "content_type": upload.content_type,
            "content": content.decode("utf-8"),
        }

    return app
