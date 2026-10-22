"""Input-only request cases for FastAPI 0.157.0 nullable/default parameters."""

from typing import Annotated

from fastapi import Body, Cookie, FastAPI, File, Form, Header, Query
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


def create_app(factory_input, event_trace):
    """Build route declarations shared by the nullable/default recipe cases."""
    del factory_input, event_trace
    app = FastAPI()

    @app.post("/request/query-required")
    def query_required(value: Annotated[int | None, Query()]):
        return value

    @app.post("/request/query-default")
    def query_default(value: Annotated[int | None, Query()] = 10):
        return value

    @app.post("/request/cookie-required")
    def cookie_required(value: Annotated[int | None, Cookie()]):
        return value

    @app.post("/request/header-required")
    def header_required(value: Annotated[int | None, Header()]):
        return value

    @app.post("/request/form-required")
    def form_required(value: Annotated[int | None, Form()]):
        return value

    @app.post("/request/body-required")
    def body_required(value: Annotated[int | None, Body(embed=True)]):
        return value

    @app.post("/request/body-default")
    def body_default(value: Annotated[int | None, Body(embed=True)] = 10):
        return value

    @app.post("/form/empty-default")
    def form_empty_default(value: Annotated[int | None, Form()] = 10):
        return {"value": value}

    class FormModel(BaseModel):
        value: int | None = 10

    @app.post("/form/empty-model")
    def form_empty_model(params: Annotated[FormModel, Form()]):
        return {
            "value": params.value,
            "fields_set": sorted(params.model_fields_set),
        }

    @app.post("/form/required-empty")
    def form_required_empty(value: Annotated[int, Form()]):
        return value

    @app.post("/form/checkbox-default")
    def form_checkbox_default(value: Annotated[bool, Form()] = True):
        return value

    @app.get("/header/nullable")
    def header_nullable(int_val: Annotated[int | None, Header()]):
        return int_val

    class HeaderModel(BaseModel):
        int_val: int | None

    @app.get("/header/model")
    def header_model(params: Annotated[HeaderModel, Header()]):
        return params.int_val

    @app.get("/header/raw-model")
    def header_raw_model(params: Annotated[HeaderModel, Header(convert_underscores=False)]):
        return params.int_val

    class AliasHeaders(BaseModel):
        int_val: int
        count: Annotated[int, Field(alias="x_count")]
        total: Annotated[int, Field(alias="unused", validation_alias="x_total")]

    @app.get("/header/alias-model")
    def header_alias_model(params: Annotated[AliasHeaders, Header()]):
        return params

    class NameLocationHeaders(BaseModel):
        model_config = ConfigDict(loc_by_alias=False)
        int_val: int
        item_count: Annotated[int, Field(alias="x_count")]

    @app.get("/header/name-location-model")
    def header_name_location_model(params: Annotated[NameLocationHeaders, Header()]):
        return params

    class ListHeaders(BaseModel):
        item_ids: list[int]

    @app.get("/header/list-model")
    def header_list_model(params: Annotated[ListHeaders, Header()]):
        return params.item_ids

    @app.post("/file/required")
    def file_required(
        file: Annotated[bytes | None, File()],
        files: Annotated[list[bytes] | None, File()],
    ):
        return {
            "file": len(file) if file is not None else None,
            "files": [len(value) for value in files] if files is not None else None,
        }

    @app.post("/file/optional")
    def file_optional(
        file: Annotated[bytes | None, File()] = None,
        files: Annotated[list[bytes] | None, File()] = None,
    ):
        return {
            "file": len(file) if file is not None else None,
            "files": [len(value) for value in files] if files is not None else None,
        }

    @app.post("/file/defaults")
    def file_defaults(
        *,
        file: Annotated[bytes | None, File()] = b"default",
        files: Annotated[list[bytes] | None, File(default_factory=lambda: [b"default"])],
    ):
        return {
            "file": len(file) if file is not None else None,
            "files": [len(value) for value in files] if files is not None else None,
        }

    @app.post("/file/alias-choice")
    def file_alias_choice(
        file: Annotated[
            bytes,
            File(alias="legacy", validation_alias=AliasChoices("primary", "secondary")),
        ],
    ):
        return file.decode("utf-8")

    return app
