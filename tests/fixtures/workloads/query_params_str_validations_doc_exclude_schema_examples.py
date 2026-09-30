"""Independent OpenAPI-exclusion workload for FastAPI 0.141.1 docs."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query-example/t014/direct")
    async def tutorial014_direct(
        hidden_query: str | None = Query(default=None, include_in_schema=False),
    ):
        return {"hidden_query": hidden_query}

    @app.get("/query-example/t014/annotated")
    async def tutorial014_annotated(
        hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None,
    ):
        return {"hidden_query": hidden_query}

    return app
