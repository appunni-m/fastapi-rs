"""Input-only request workload for FastAPI 0.157.0 field option behavior."""

import re
from typing import Annotated

from fastapi import Body, Cookie, FastAPI, File, Form, Header, Path, Query, UploadFile
from pydantic import Field


def _endpoint_for_field(annotation, function_name):
    def endpoint(value):
        return value

    endpoint.__name__ = function_name
    endpoint.__annotations__["value"] = annotation
    return endpoint


def _register_field_endpoint(app, route, field_annotation, function_name):
    app.add_api_route(
        route,
        _endpoint_for_field(field_annotation, function_name),
        methods=["POST"],
        name=function_name,
    )


def create_app(factory_input, event_trace):
    """Build independent routes selected by the field-options input recipe."""
    del factory_input, event_trace
    app = FastAPI()

    locations = {
        "path": Path,
        "query": Query,
        "header": Header,
        "cookie": Cookie,
        "body": Body,
        "form": Form,
    }
    union_modes = (("none", None), ("smart", "smart"), ("left-to-right", "left_to_right"))
    for location, parameter in locations.items():
        for mode_name, mode in union_modes:
            route = f"/field-options/union/{location}/{mode_name}"
            if parameter is Path:
                route += "/{value}"
            _register_field_endpoint(
                app,
                route,
                Annotated[int | str, parameter(union_mode=mode)],
                f"union_{location}_{mode_name.replace('-', '_')}",
            )

    for location, parameter in {
        "query": Query,
        "header": Header,
        "body": Body,
        "form": Form,
    }.items():
        for fail_fast in (True, False):
            _register_field_endpoint(
                app,
                f"/field-options/fail-fast/{location}/{'fast' if fail_fast else 'all'}",
                Annotated[list[int], parameter(fail_fast=fail_fast)],
                f"fail_fast_{location}_{'fast' if fail_fast else 'all'}",
            )

    for fail_fast in (True, False):
        route = f"/field-options/file-fail-fast/{'fast' if fail_fast else 'all'}"

        def upload(files: Annotated[list[UploadFile], File(fail_fast=fail_fast)]):
            return [file.filename for file in files]

        upload.__name__ = f"file_fail_fast_{'fast' if fail_fast else 'all'}"
        app.add_api_route(route, upload, methods=["POST"], name=upload.__name__)

    pattern = re.compile("^abc$", re.IGNORECASE)
    for location, parameter in locations.items():
        route = f"/field-options/pattern/{location}"
        if parameter is Path:
            route += "/{value}"
        _register_field_endpoint(
            app,
            route,
            Annotated[str, parameter(pattern=pattern)],
            f"compiled_pattern_{location}",
        )

    @app.post("/field-options/omitted-options")
    def omitted_options(
        number: Annotated[int | str, Field(union_mode="left_to_right"), Query()],
        values: Annotated[list[int], Field(fail_fast=True), Body()],
    ):
        return {"number": number, "values": values}

    @app.post("/field-options/explicit-options")
    def explicit_options(
        number: Annotated[int | str, Field(union_mode="left_to_right"), Query(union_mode="smart")],
        values: Annotated[list[int], Field(fail_fast=True), Body(fail_fast=False)],
    ):
        return {"number": number, "values": values}

    def customize_schema(schema):
        schema["x-custom"] = "preserved"

    @app.get("/query")
    def read_query(
        value: Annotated[int | str, Query(union_mode="left_to_right")],
        items: Annotated[list[int], Query(fail_fast=True)],
        count: Annotated[int, Query(validate_default=True)] = 1,
        label: Annotated[
            str,
            Query(
                pattern=pattern,
                json_schema_extra=customize_schema,
            ),
        ] = "ABC",
    ):
        return {"value": value, "items": items, "count": count, "label": label}

    @app.post("/body")
    def read_body(
        items: Annotated[list[int], Body(fail_fast=True)],
        number: Annotated[int | str, Body(union_mode="left_to_right")],
        count: Annotated[int, Body(validate_default=True, json_schema_extra=customize_schema)] = 1,
    ):
        return {"items": items, "number": number, "count": count}

    return app
