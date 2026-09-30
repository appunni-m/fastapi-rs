"""Independent file, form, and form-model ASGI workload for source review."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    password: str


class StrictLoginForm(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/review/plain/files/required-bytes")
    async def required_file_bytes_plain(file: bytes = File()) -> dict[str, int]:
        return {"length": len(file)}

    @app.post("/review/annotated/files/required-bytes")
    async def required_file_bytes_annotated(
        file: Annotated[bytes, File()],
    ) -> dict[str, int]:
        return {"length": len(file)}

    @app.post("/review/plain/files/optional-bytes")
    async def optional_file_bytes_plain(
        file: bytes | None = File(default=None),
    ) -> dict[str, int | str]:
        if not file:
            return {"state": "absent"}
        return {"length": len(file)}

    @app.post("/review/annotated/files/optional-bytes")
    async def optional_file_bytes_annotated(
        file: Annotated[bytes | None, File()] = None,
    ) -> dict[str, int | str]:
        if not file:
            return {"state": "absent"}
        return {"length": len(file)}

    @app.post("/review/plain/files/required-upload")
    async def required_upload_plain(file: UploadFile) -> dict[str, str | None]:
        return {"filename": file.filename}

    @app.post("/review/annotated/files/required-upload")
    async def required_upload_annotated(
        file: Annotated[UploadFile, File()],
    ) -> dict[str, str | None]:
        return {"filename": file.filename}

    @app.post("/review/plain/files/upload-read-seek")
    async def upload_read_seek_plain(file: UploadFile) -> dict[str, str]:
        prefix = await file.read(4)
        remainder = await file.read()
        await file.seek(0)
        replay = await file.read()
        return {
            "prefix": prefix.decode("ascii"),
            "remainder": remainder.decode("ascii"),
            "replay": replay.decode("ascii"),
        }

    @app.post("/review/annotated/files/upload-read-seek")
    async def upload_read_seek_annotated(
        file: Annotated[UploadFile, File()],
    ) -> dict[str, str]:
        prefix = await file.read(4)
        remainder = await file.read()
        await file.seek(0)
        replay = await file.read()
        return {
            "prefix": prefix.decode("ascii"),
            "remainder": remainder.decode("ascii"),
            "replay": replay.decode("ascii"),
        }

    @app.post("/review/plain/files/optional-upload")
    async def optional_upload_plain(
        file: UploadFile | None = None,
    ) -> dict[str, str | None]:
        if not file:
            return {"state": "absent"}
        return {"filename": file.filename}

    @app.post("/review/annotated/files/optional-upload")
    async def optional_upload_annotated(
        file: Annotated[UploadFile | None, File()] = None,
    ) -> dict[str, str | None]:
        if not file:
            return {"state": "absent"}
        return {"filename": file.filename}

    @app.post("/review/plain/files/described-bytes")
    async def described_file_bytes_plain(
        file: bytes = File(description="A file read as bytes"),
    ) -> dict[str, int]:
        return {"length": len(file)}

    @app.post("/review/annotated/files/described-bytes")
    async def described_file_bytes_annotated(
        file: Annotated[bytes, File(description="A file read as bytes")],
    ) -> dict[str, int]:
        return {"length": len(file)}

    @app.post("/review/plain/files/described-upload")
    async def described_upload_plain(
        file: UploadFile = File(description="A file read as UploadFile"),  # noqa: B008
    ) -> dict[str, str | None]:
        return {"filename": file.filename}

    @app.post("/review/annotated/files/described-upload")
    async def described_upload_annotated(
        file: Annotated[
            UploadFile,
            File(description="A file read as UploadFile"),
        ],
    ) -> dict[str, str | None]:
        return {"filename": file.filename}

    @app.post("/review/plain/files/multiple-bytes")
    async def multiple_file_bytes_plain(
        files: list[bytes] = File(),  # noqa: B008
    ) -> dict[str, list[int]]:
        return {"lengths": [len(value) for value in files]}

    @app.post("/review/annotated/files/multiple-bytes")
    async def multiple_file_bytes_annotated(
        files: Annotated[list[bytes], File()],
    ) -> dict[str, list[int]]:
        return {"lengths": [len(value) for value in files]}

    @app.post("/review/plain/files/multiple-upload")
    async def multiple_uploads_plain(
        files: list[UploadFile],
    ) -> dict[str, list[str | None]]:
        return {"filenames": [value.filename for value in files]}

    @app.post("/review/annotated/files/multiple-upload")
    async def multiple_uploads_annotated(
        files: Annotated[list[UploadFile], File()],
    ) -> dict[str, list[str | None]]:
        return {"filenames": [value.filename for value in files]}

    @app.post("/review/plain/files/described-multiple-bytes")
    async def described_multiple_bytes_plain(
        files: list[bytes] = File(description="Multiple files as bytes"),  # noqa: B008
    ) -> dict[str, list[int]]:
        return {"lengths": [len(value) for value in files]}

    @app.post("/review/annotated/files/described-multiple-bytes")
    async def described_multiple_bytes_annotated(
        files: Annotated[
            list[bytes],
            File(description="Multiple files as bytes"),
        ],
    ) -> dict[str, list[int]]:
        return {"lengths": [len(value) for value in files]}

    @app.post("/review/plain/files/described-multiple-upload")
    async def described_multiple_uploads_plain(
        files: list[UploadFile] = File(  # noqa: B008
            description="Multiple files as UploadFile",
        ),
    ) -> dict[str, list[str | None]]:
        return {"filenames": [value.filename for value in files]}

    @app.post("/review/annotated/files/described-multiple-upload")
    async def described_multiple_uploads_annotated(
        files: Annotated[
            list[UploadFile],
            File(description="Multiple files as UploadFile"),
        ],
    ) -> dict[str, list[str | None]]:
        return {"filenames": [value.filename for value in files]}

    @app.post("/review/plain/forms/fields")
    async def form_fields_plain(
        username: str = Form(),
        password: str = Form(),
    ) -> dict[str, str]:
        return {"username": username}

    @app.post("/review/annotated/forms/fields")
    async def form_fields_annotated(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
    ) -> dict[str, str]:
        return {"username": username}

    @app.post("/review/plain/forms/model")
    async def form_model_plain(data: LoginForm = Form()) -> LoginForm:  # noqa: B008
        return data

    @app.post("/review/annotated/forms/model")
    async def form_model_annotated(
        data: Annotated[LoginForm, Form()],
    ) -> LoginForm:
        return data

    @app.post("/review/plain/forms/model-extra-forbid")
    async def strict_form_model_plain(
        data: StrictLoginForm = Form(),  # noqa: B008
    ) -> StrictLoginForm:
        return data

    @app.post("/review/annotated/forms/model-extra-forbid")
    async def strict_form_model_annotated(
        data: Annotated[StrictLoginForm, Form()],
    ) -> StrictLoginForm:
        return data

    @app.post("/review/plain/forms-and-files")
    async def mixed_form_and_files_plain(
        file: bytes = File(),
        fileb: UploadFile = File(),  # noqa: B008
        token: str = Form(),
    ) -> dict[str, int | str | None]:
        return {
            "length": len(file),
            "token": token,
            "file_content_type": fileb.content_type,
        }

    @app.post("/review/annotated/forms-and-files")
    async def mixed_form_and_files_annotated(
        file: Annotated[bytes, File()],
        fileb: Annotated[UploadFile, File()],
        token: Annotated[str, Form()],
    ) -> dict[str, int | str | None]:
        return {
            "length": len(file),
            "token": token,
            "file_content_type": fileb.content_type,
        }

    @app.get("/review/files/")
    async def file_upload_index() -> HTMLResponse:
        return HTMLResponse(
            "<body><form action='/review/plain/files/multiple-bytes' "
            "enctype='multipart/form-data' method='post'>"
            "<input name='files' type='file' multiple></form></body>"
        )

    return app
