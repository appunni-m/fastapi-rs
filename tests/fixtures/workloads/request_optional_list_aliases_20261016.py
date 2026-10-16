"""Optional form and file list alias-selection workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel, Field


class FormAliasModel(BaseModel):
    p: list[str] | None = Field(default=None, alias="p_alias")


class FormValidationAliasModel(BaseModel):
    p: list[str] | None = Field(default=None, validation_alias="p_val_alias")


class FormBothAliasesModel(BaseModel):
    p: list[str] | None = Field(
        default=None,
        alias="p_alias",
        validation_alias="p_val_alias",
    )


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/optional-list-alias")
    async def optional_list_alias(
        p: Annotated[list[str] | None, Form(alias="p_alias")] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post("/model-optional-list-alias")
    async def model_optional_list_alias(
        form: Annotated[FormAliasModel, Form()],
    ) -> dict[str, list[str] | None]:
        return {"p": form.p}

    @app.post("/optional-list-validation-alias")
    async def optional_list_validation_alias(
        p: Annotated[list[str] | None, Form(validation_alias="p_val_alias")] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post("/model-optional-list-validation-alias")
    async def model_optional_list_validation_alias(
        form: Annotated[FormValidationAliasModel, Form()],
    ) -> dict[str, list[str] | None]:
        return {"p": form.p}

    @app.post("/optional-list-alias-and-validation-alias")
    async def optional_list_both_aliases(
        p: Annotated[
            list[str] | None,
            Form(alias="p_alias", validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, list[str] | None]:
        return {"p": p}

    @app.post("/model-optional-list-alias-and-validation-alias")
    async def model_optional_list_both_aliases(
        form: Annotated[FormBothAliasesModel, Form()],
    ) -> dict[str, list[str] | None]:
        return {"p": form.p}

    @app.post("/optional-list-bytes-alias")
    async def optional_list_bytes_alias(
        p: Annotated[list[bytes] | None, File(alias="p_alias")] = None,
    ) -> dict[str, list[int] | None]:
        return {"file_size": [len(item) for item in p] if p else None}

    @app.post("/optional-list-uploadfile-alias")
    async def optional_list_uploadfile_alias(
        p: Annotated[list[UploadFile] | None, File(alias="p_alias")] = None,
    ) -> dict[str, list[int] | None]:
        return {"file_size": [item.size for item in p] if p else None}

    @app.post("/optional-list-bytes-validation-alias")
    async def optional_list_bytes_validation_alias(
        p: Annotated[list[bytes] | None, File(validation_alias="p_val_alias")] = None,
    ) -> dict[str, list[int] | None]:
        return {"file_size": [len(item) for item in p] if p else None}

    @app.post("/optional-list-uploadfile-validation-alias")
    async def optional_list_uploadfile_validation_alias(
        p: Annotated[
            list[UploadFile] | None,
            File(validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, list[int] | None]:
        return {"file_size": [item.size for item in p] if p else None}

    @app.post("/optional-list-bytes-alias-and-validation-alias")
    async def optional_list_bytes_both_aliases(
        p: Annotated[
            list[bytes] | None,
            File(alias="p_alias", validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, list[int] | None]:
        return {"file_size": [len(item) for item in p] if p else None}

    @app.post("/optional-list-uploadfile-alias-and-validation-alias")
    async def optional_list_uploadfile_both_aliases(
        p: Annotated[
            list[UploadFile] | None,
            File(alias="p_alias", validation_alias="p_val_alias"),
        ] = None,
    ) -> dict[str, list[int] | None]:
        return {"file_size": [item.size for item in p] if p else None}

    return app
