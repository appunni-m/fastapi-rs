"""Input-driven FastAPI UploadFile storage rollover workload."""

from __future__ import annotations

from tempfile import SpooledTemporaryFile

from fastapi import FastAPI, UploadFile
from fastapi.datastructures import Headers


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.post("/uploadfile-spooled-storage")
    async def spooled_storage(payload: dict[str, object]) -> dict[str, object]:
        mode = str(payload["mode"])
        max_size, force_rollover = {
            "threshold-equality": (6, False),
            "threshold-crossing": (5, False),
            "already-rolled": (5, True),
        }[mode]
        file_object = SpooledTemporaryFile(max_size=max_size, mode="w+b")
        file_object.write(b"maple")
        if force_rollover:
            file_object.rollover()
        upload = UploadFile(
            file_object,
            size=5,
            filename="maple.txt",
            headers=Headers({"content-type": "text/plain"}),
        )

        write_result = await upload.write(b"Z")
        rolled_after_write = bool(upload.file._rolled)
        seek_result = await upload.seek(0)
        content = (await upload.read()).decode("ascii")
        close_result = await upload.close()

        return {
            "file_is_original": upload.file is file_object,
            "rolled_after_write": rolled_after_write,
            "content": content,
            "size": upload.size,
            "write_returned_none": write_result is None,
            "seek_returned_none": seek_result is None,
            "close_returned_none": close_result is None,
            "file_closed": upload.file.closed,
        }

    return app
