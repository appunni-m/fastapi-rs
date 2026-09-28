"""Independent form and upload workload for FastAPI's multipart feature."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/forms/required")
    async def required_form(value: Annotated[str, Form()]) -> dict[str, str]:
        return {"value": value}

    @app.post("/forms/optional")
    async def optional_form(
        value: Annotated[str | None, Form()] = None,
    ) -> dict[str, str | None]:
        return {"value": value}

    @app.post("/forms/list")
    async def form_list(values: Annotated[list[str], Form()]) -> dict[str, list[str]]:
        return {"values": values}

    @app.post("/forms/optional-list")
    async def optional_form_list(
        values: Annotated[list[str] | None, Form()] = None,
    ) -> dict[str, list[str] | None]:
        return {"values": values}

    @app.post("/files/required-bytes")
    async def required_file_bytes(p: Annotated[bytes, File()]) -> dict[str, int]:
        return {"size": len(p)}

    @app.post("/files/required-upload")
    async def required_file_upload(p: Annotated[UploadFile, File()]) -> dict[str, object]:
        contents = await p.read()
        return {"filename": p.filename, "content_type": p.content_type, "size": len(contents)}

    @app.post("/files/optional-upload")
    async def optional_file_upload(
        p: Annotated[UploadFile | None, File()] = None,
    ) -> dict[str, object | None]:
        if p is None:
            return {"file": None}
        contents = await p.read()
        return {"filename": p.filename, "content_type": p.content_type, "size": len(contents)}

    @app.post("/files/list")
    async def file_list(p: Annotated[list[UploadFile], File()]) -> dict[str, list[int]]:
        sizes = [len(await item.read()) for item in p]
        return {"sizes": sizes}

    @app.post("/files/optional-list")
    async def optional_file_list(
        p: Annotated[list[UploadFile] | None, File()] = None,
    ) -> dict[str, list[int] | None]:
        if p is None:
            return {"sizes": None}
        return {"sizes": [len(await item.read()) for item in p]}

    @app.post("/mixed")
    async def mixed_form_and_file(
        caption: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
    ) -> dict[str, object]:
        contents = await file.read()
        return {"caption": caption, "filename": file.filename, "size": len(contents)}

    return app
