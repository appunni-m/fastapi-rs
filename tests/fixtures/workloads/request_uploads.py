"""Independent multipart upload and mixed form/file workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/optional-bytes")
    async def optional_bytes(
        files: Annotated[list[bytes] | None, File()] = None,
    ) -> dict[str, object]:
        if files is None:
            return {"files": None}
        return {"files": [content.decode("utf-8") for content in files]}

    @app.post("/ordered-form-file")
    async def ordered_form_file(
        upload: Annotated[UploadFile, File()], label: Annotated[str, Form()]
    ) -> dict[str, object]:
        content = await upload.read()
        return {"label": label, "filename": upload.filename, "content": content.decode("utf-8")}

    @app.post("/ordered-file-list")
    async def ordered_file_list(
        uploads: Annotated[list[UploadFile], File()], label: Annotated[str, Form()]
    ) -> dict[str, object]:
        names = [upload.filename for upload in uploads]
        return {"label": label, "filenames": names}

    @app.post("/ordered-byte-list-files-first")
    async def ordered_byte_list_files_first(
        files: Annotated[list[bytes], File()], label: Annotated[str, Form()]
    ) -> dict[str, object]:
        return {
            "label": label,
            "files": [content.decode("utf-8") for content in files],
        }

    @app.post("/ordered-byte-list-label-first")
    async def ordered_byte_list_label_first(
        label: Annotated[str, Form()], files: Annotated[list[bytes], File()]
    ) -> dict[str, object]:
        return {
            "label": label,
            "files": [content.decode("utf-8") for content in files],
        }

    @app.post("/preserve-bytes")
    async def preserve_bytes(files: Annotated[list[bytes], File()]) -> list[str]:
        return [content.decode("utf-8") for content in files]

    @app.post("/single-upload")
    async def single_upload(upload: Annotated[UploadFile, File()]) -> dict[str, object]:
        content = await upload.read()
        return {
            "filename": upload.filename,
            "content_type": upload.content_type,
            "size": len(content),
        }

    @app.post("/multiple-uploads")
    async def multiple_uploads(uploads: Annotated[list[UploadFile], File()]) -> list[str | None]:
        return [upload.filename for upload in uploads]

    @app.post("/token-uploads")
    async def token_uploads(
        token: Annotated[str, Form()], uploads: Annotated[list[UploadFile], File()]
    ) -> dict[str, object]:
        return {"token": token, "filenames": [upload.filename for upload in uploads]}

    return app
