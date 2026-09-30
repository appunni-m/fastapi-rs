"""Isolated workload for query tutorial examples that declare a pattern."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query-example/t004/direct")
    async def tutorial004_direct(
        q: str | None = Query(default=None, min_length=3, max_length=50, pattern="^fixedquery$"),
    ):
        return {"q": q}

    @app.get("/query-example/t004/annotated")
    async def tutorial004_annotated(
        q: Annotated[str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")] = None,
    ):
        return {"q": q}

    @app.get("/query-example/t010/direct")
    async def tutorial010_direct(
        q: str | None = Query(
            default=None,
            alias="item-query",
            title="Search query",
            description="Filter this independent catalog by phrase.",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ):
        return {"q": q}

    @app.get("/query-example/t010/annotated")
    async def tutorial010_annotated(
        q: Annotated[
            str | None,
            Query(
                alias="item-query",
                title="Search query",
                description="Filter this independent catalog by phrase.",
                min_length=3,
                max_length=50,
                pattern="^fixedquery$",
                deprecated=True,
            ),
        ] = None,
    ):
        return {"q": q}

    return app
