"""Input-driven error propagation workload for FastAPI UploadFile methods."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from io import BytesIO
from typing import Any

from fastapi import FastAPI, UploadFile
from fastapi.datastructures import Headers


class _OperationFailingBytesIO(BytesIO):
    def __init__(self, failing_operation: str) -> None:
        super().__init__(b"maple")
        self.failing_operation = failing_operation

    def _raise_if_failing(self, operation: str) -> None:
        if self.failing_operation == operation:
            raise OSError(f"injected {operation} failure")

    def read(self, size: int = -1) -> bytes:
        self._raise_if_failing("read")
        return super().read(size)

    def write(self, data: bytes) -> int:
        self._raise_if_failing("write")
        return super().write(data)

    def seek(self, offset: int, whence: int = 0) -> int:
        self._raise_if_failing("seek")
        return super().seek(offset, whence)

    def close(self) -> None:
        self._raise_if_failing("close")
        super().close()


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.post("/uploadfile-io/error")
    async def uploadfile_io_error(payload: dict[str, object]) -> dict[str, object]:
        operation = str(payload["operation"])
        file_object = _OperationFailingBytesIO(operation)
        upload = UploadFile(
            file_object,
            size=5,
            filename="maple.txt",
            headers=Headers({"content-type": "text/plain"}),
        )
        operation_call: Callable[[], Coroutine[Any, Any, object]] = {
            "read": lambda: upload.read(1),
            "write": lambda: upload.write(b"Z"),
            "seek": lambda: upload.seek(1),
            "close": upload.close,
        }[operation]
        try:
            result = await operation_call()
        except OSError as error:
            return {
                "outcome": "raised",
                "exception_class": type(error).__name__,
                "exception_message": str(error),
                "size": upload.size,
                "file_closed": upload.file.closed,
            }
        return {
            "outcome": "returned",
            "result": result.decode("ascii") if isinstance(result, bytes) else result,
            "size": upload.size,
            "file_closed": upload.file.closed,
        }

    return app
