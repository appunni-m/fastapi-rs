"""Direct FastAPI UploadFile metadata and asynchronous file-operation workload."""

from __future__ import annotations

from io import BytesIO

from fastapi import FastAPI, UploadFile
from fastapi.datastructures import Headers


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/uploadfile-io")
    async def uploadfile_io(payload: dict[str, object]) -> dict[str, object]:
        content = str(payload["content"]).encode("ascii")
        file_object = BytesIO(content)
        headers = Headers(payload["headers"])
        upload = UploadFile(
            file_object,
            size=payload["size"],
            filename=payload["filename"],
            headers=headers,
        )
        size_before_write = upload.size

        file_object_prefix = upload.file.read(2).decode("ascii")
        file_object.seek(0)

        read_prefix = (await upload.read(2)).decode("ascii")
        read_remainder = (await upload.read()).decode("ascii")
        seek_result = await upload.seek(2)
        write_result = await upload.write(b"Z")
        rewind_result = await upload.seek(0)
        rewritten_content = (await upload.read()).decode("ascii")
        size_after_write = upload.size
        close_result = await upload.close()

        return {
            "filename": upload.filename,
            "size": size_before_write,
            "size_after_write": size_after_write,
            "headers": dict(upload.headers),
            "content_type": upload.content_type,
            "file_is_original": upload.file is file_object,
            "file_object_prefix": file_object_prefix,
            "read_prefix": read_prefix,
            "read_remainder": read_remainder,
            "seek_returned_none": seek_result is None and rewind_result is None,
            "write_returned_none": write_result is None,
            "rewritten_content": rewritten_content,
            "close_returned_none": close_result is None,
            "file_closed": upload.file.closed,
        }

    return app
