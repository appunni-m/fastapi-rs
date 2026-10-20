"""Input-driven UploadFile constructor, header, and field mutation workload."""

from __future__ import annotations

from io import BytesIO

from fastapi import FastAPI, UploadFile
from fastapi.datastructures import Headers


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.get("/uploadfile-metadata-edges/omitted-headers")
    async def omitted_headers() -> dict[str, object]:
        file_object = BytesIO(b"maple")
        upload = UploadFile(file_object, filename=None, size=None)
        return {
            "file_is_original": upload.file is file_object,
            "filename": upload.filename,
            "size": upload.size,
            "headers_empty": len(upload.headers) == 0,
            "content_type": upload.content_type,
        }

    @app.get("/uploadfile-metadata-edges/duplicate-content-type")
    async def duplicate_content_type() -> dict[str, object]:
        file_object = BytesIO(b"maple")
        headers = Headers(
            raw=[
                (b"Content-Type", b"text/plain"),
                (b"content-type", b"application/json"),
            ]
        )
        upload = UploadFile(file_object, headers=headers)
        return {
            "file_is_original": upload.file is file_object,
            "raw_headers": [
                [key.decode("latin-1"), value.decode("latin-1")]
                for key, value in upload.headers.raw
            ],
            "content_type": upload.content_type,
        }

    @app.get("/uploadfile-metadata-edges/mutated-fields")
    async def mutated_fields() -> dict[str, object]:
        original_file = BytesIO(b"old")
        replacement_file = BytesIO(b"new")
        upload = UploadFile(
            original_file,
            filename="before.txt",
            size=3,
            headers=Headers({"content-type": "text/old"}),
        )
        upload.file = replacement_file
        upload.filename = "after.txt"
        upload.size = 17
        upload.headers = Headers({"x-state": "updated"})

        content = (await upload.read()).decode("ascii")
        close_result = await upload.close()
        return {
            "file_is_replacement": upload.file is replacement_file,
            "original_file_closed": original_file.closed,
            "replacement_file_closed": upload.file.closed,
            "filename": upload.filename,
            "size": upload.size,
            "headers": upload.headers.items(),
            "content_type": upload.content_type,
            "content": content,
            "close_returned_none": close_result is None,
        }

    @app.get("/uploadfile-metadata-edges/content-type-read-only")
    async def content_type_read_only() -> dict[str, object]:
        upload = UploadFile(
            BytesIO(b"maple"),
            headers=Headers({"content-type": "text/plain"}),
        )
        try:
            upload.content_type = "application/json"
        except AttributeError as error:
            return {
                "assignment": "rejected",
                "exception_class": type(error).__name__,
                "exception_message": str(error),
                "content_type": upload.content_type,
            }
        return {"assignment": "accepted", "content_type": upload.content_type}

    return app
