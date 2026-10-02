"""Independent optional UploadFile alias and validation-alias workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, UploadFile


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/wire/optional-upload")
    async def optional_upload(
        upload: Annotated[
            UploadFile | None,
            File(alias="public-upload", validation_alias="wire-upload"),
        ] = None,
    ) -> dict[str, int | None]:
        return {"size": upload.size if upload else None}

    return app
