"""Independent request-parameter extraction and validation workload."""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Path, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/path-values/{item_id}")
    async def read_path_value(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @app.get("/bindings/{token}")
    async def read_path_and_query_alias(
        path_value: Annotated[str, Path(alias="token")],
        query_value: Annotated[str, Query(alias="token")],
    ) -> dict[str, str]:
        return {"path": path_value, "query": query_value}

    @app.get("/lookup")
    async def read_lookup(query_value: Annotated[int, Query(alias="term")]) -> dict[str, int]:
        return {"value": query_value}

    @app.get("/tags")
    async def read_tags(tags: Annotated[list[str], Query(alias="tag")]) -> dict[str, list[str]]:
        return {"values": tags}

    @app.get("/quantities")
    async def read_quantities(values: Annotated[list[int], Query()]) -> dict[str, list[int]]:
        return {"values": values}

    @app.get("/headers/trace")
    async def read_trace_header(x_trace_id: Annotated[str, Header()]) -> dict[str, str]:
        return {"value": x_trace_id}

    @app.get("/headers/repeated")
    async def read_repeated_header(
        x_token: Annotated[list[str], Header()],
    ) -> dict[str, list[str]]:
        return {"values": x_token}

    @app.get("/cookies/required")
    async def read_required_cookie(
        session: Annotated[str, Cookie(alias="session-id")],
    ) -> dict[str, str]:
        return {"value": session}

    @app.get("/cookies/optional")
    async def read_optional_cookie(
        session: Annotated[str | None, Cookie(alias="session-id")] = None,
    ) -> dict[str, str | None]:
        return {"value": session}

    return app
