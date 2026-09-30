"""Independent workload for blank optional form values with File declared."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/review/form-file/defaults")
    async def post_form_file_defaults(
        age: Annotated[int | None, Form()] = None,
        file: Annotated[bytes | None, File()] = None,
    ):
        return {"file": file, "age": age}

    return app
