"""Independent ASGI workload for tutorial file and form inputs."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel


class LoginFields(BaseModel):
    username: str
    password: str


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/files/bytes")
    async def file_bytes(file: Annotated[bytes, File()]) -> dict[str, int]:
        return {"file_size": len(file)}

    @app.post("/files/upload")
    async def uploaded_file(file: UploadFile) -> dict[str, str | None]:
        return {"filename": file.filename}

    @app.post("/files/multiple-bytes")
    async def multiple_byte_files(
        files: Annotated[list[bytes], File()],
    ) -> dict[str, list[int]]:
        return {"file_sizes": [len(content) for content in files]}

    @app.post("/forms/model")
    async def form_model(data: Annotated[LoginFields, Form()]):
        return data

    @app.post("/forms/fields")
    async def form_fields(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
    ) -> dict[str, str]:
        return {"username": username}

    return app
