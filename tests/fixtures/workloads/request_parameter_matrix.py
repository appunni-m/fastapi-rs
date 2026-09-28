"""Independent optional request-parameter workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Body, FastAPI, Header, Path, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query/optional")
    async def optional_query(value: str | None = None) -> dict[str, str | None]:
        return {"value": value}

    @app.get("/query/optional-list")
    async def optional_query_list(
        values: Annotated[list[str] | None, Query()] = None,
    ) -> dict[str, list[str] | None]:
        return {"values": values}

    @app.get("/headers/optional")
    async def optional_header(
        x_trace_id: Annotated[str | None, Header()] = None,
    ) -> dict[str, str | None]:
        return {"value": x_trace_id}

    @app.get("/headers/optional-list")
    async def optional_header_list(
        x_tags: Annotated[list[str] | None, Header()] = None,
    ) -> dict[str, list[str] | None]:
        return {"values": x_tags}

    @app.get("/path/ordinary/{value}")
    async def ordinary_path(value: Annotated[str, Path()]) -> dict[str, str]:
        return {"value": value}

    @app.get("/path/alias/{path_value}")
    async def aliased_path(
        value: Annotated[str, Path(alias="path_value")],
    ) -> dict[str, str]:
        return {"value": value}

    @app.get("/path/validation-alias/{path_value}")
    async def validation_aliased_path(
        value: Annotated[str, Path(validation_alias="path_value")],
    ) -> dict[str, str]:
        return {"value": value}

    @app.get("/path/both-aliases/{path_value}")
    async def path_with_both_aliases(
        value: Annotated[str, Path(alias="public_path", validation_alias="path_value")],
    ) -> dict[str, str]:
        return {"value": value}

    @app.post("/body/optional-string")
    async def optional_body_string(
        value: Annotated[str | None, Body(embed=True)] = None,
    ) -> dict[str, str | None]:
        return {"value": value}

    @app.post("/body/optional-list")
    async def optional_body_list(
        values: Annotated[list[str] | None, Body(embed=True)] = None,
    ) -> dict[str, list[str] | None]:
        return {"values": values}

    return app
