"""Input-only ASGI workload for FastAPI 0.157.0 field metadata behavior."""

from typing import Annotated, Literal

from fastapi import Body, Cookie, FastAPI, File, Form, Header, Path, Query
from pydantic import BaseModel, Field

FieldCount = Annotated[
    int,
    Field(
        alias="source_name",
        title="Source title",
        description="Metadata from Field",
        examples=[17],
        deprecated=True,
        json_schema_extra={"x-origin": "field", "x-retained": True},
    ),
]


class Lynx(BaseModel):
    kind: Literal["lynx"]


class Heron(BaseModel):
    kind: Literal["heron"]


TaggedAnimal = Annotated[Lynx | Heron, Field(discriminator="kind")]


def create_app(factory_input, event_trace):
    """Build the route set exercised by the YAML input recipe."""
    del factory_input, event_trace
    app = FastAPI()

    @app.post("/parameters/path-alias/{wire_key}")
    def path_alias(value: Annotated[int, Field(alias="wire_key"), Path()]):
        return {"value": value}

    @app.post("/parameters/path-validation-alias/{wire_key}")
    def path_validation_alias(
        value: Annotated[
            int,
            Field(alias="ignored_key", validation_alias="wire_key"),
            Path(),
        ],
    ):
        return {"value": value}

    @app.post("/parameters/query-alias")
    def query_alias(value: Annotated[int, Field(alias="wire_key"), Query()]):
        return {"value": value}

    @app.post("/parameters/query-validation-alias")
    def query_validation_alias(
        value: Annotated[
            int,
            Field(alias="ignored_key", validation_alias="wire_key"),
            Query(),
        ],
    ):
        return {"value": value}

    @app.post("/parameters/header-alias")
    def header_alias(
        value: Annotated[int, Field(alias="x-wire-token"), Header()],
    ):
        return {"value": value}

    @app.post("/parameters/header-validation-alias")
    def header_validation_alias(
        value: Annotated[
            int,
            Field(alias="x-ignored-token", validation_alias="x-wire-token"),
            Header(),
        ],
    ):
        return {"value": value}

    @app.post("/parameters/cookie-alias")
    def cookie_alias(value: Annotated[int, Field(alias="wire_key"), Cookie()]):
        return {"value": value}

    @app.post("/parameters/cookie-validation-alias")
    def cookie_validation_alias(
        value: Annotated[
            int,
            Field(alias="ignored_key", validation_alias="wire_key"),
            Cookie(),
        ],
    ):
        return {"value": value}

    @app.post("/parameters/body-alias")
    def body_alias(
        value: Annotated[int, Field(alias="wire_key"), Body(embed=True)],
    ):
        return {"value": value}

    @app.post("/parameters/body-validation-alias")
    def body_validation_alias(
        value: Annotated[
            int,
            Field(alias="ignored_key", validation_alias="wire_key"),
            Body(embed=True),
        ],
    ):
        return {"value": value}

    @app.post("/parameters/form-alias")
    def form_alias(value: Annotated[int, Field(alias="wire_key"), Form()]):
        return {"value": value}

    @app.post("/parameters/form-validation-alias")
    def form_validation_alias(
        value: Annotated[
            int,
            Field(alias="ignored_key", validation_alias="wire_key"),
            Form(),
        ],
    ):
        return {"value": value}

    @app.post("/parameters/file-alias")
    def file_alias(value: Annotated[bytes, Field(alias="wire_key"), File()]):
        return value.decode("utf-8")

    @app.post("/parameters/file-validation-alias")
    def file_validation_alias(
        value: Annotated[
            bytes,
            Field(alias="ignored_key", validation_alias="wire_key"),
            File(),
        ],
    ):
        return value.decode("utf-8")

    @app.post("/body/inferred-aliases")
    def inferred_body_aliases(
        active: Annotated[list[int], Field(alias="active_items")],
        archived: Annotated[
            list[int],
            Field(alias="unused_items", validation_alias="archive_items"),
        ],
    ):
        return {"active": active, "archived": archived}

    @app.post("/body/discriminator")
    def discriminator(animal: Annotated[TaggedAnimal, Body()]):
        return animal

    @app.get("/metadata/query")
    def metadata_query(
        preserved: Annotated[FieldCount, Query()],
        replaced: Annotated[
            FieldCount,
            Query(
                alias="route_choice",
                title="Route title",
                description="Metadata from Query",
                examples=[29],
                deprecated=False,
                json_schema_extra={"x-origin": "query"},
            ),
        ],
        cleared: Annotated[
            FieldCount,
            Query(
                alias=None,
                title=None,
                description=None,
                examples=None,
                deprecated=None,
                json_schema_extra=None,
            ),
        ],
    ):
        return {
            "preserved": preserved,
            "replaced": replaced,
            "cleared": cleared,
        }

    @app.post("/metadata/body")
    def metadata_body(
        preserved: Annotated[FieldCount, Body()],
        replaced: Annotated[
            FieldCount,
            Body(
                alias="route_choice",
                title="Route title",
                description="Metadata from Body",
                examples=[31],
                deprecated=False,
                json_schema_extra={"x-origin": "body"},
            ),
        ],
        cleared: Annotated[
            FieldCount,
            Body(
                alias=None,
                title=None,
                description=None,
                examples=None,
                deprecated=None,
                json_schema_extra=None,
            ),
        ],
    ):
        return {
            "preserved": preserved,
            "replaced": replaced,
            "cleared": cleared,
        }

    @app.get("/inferred")
    @app.get("/inferred/{resource_id}")
    def inferred_query(
        resource_id: Annotated[
            int,
            Field(
                default_factory=lambda: 5,
                title="Resource ID",
                description="The resource to read",
            ),
        ],
        count: Annotated[
            int,
            Field(alias="batch_size", title="Batch size", description="Items to read"),
        ] = 6,
    ):
        return {"resource_id": resource_id, "count": count}

    return app
