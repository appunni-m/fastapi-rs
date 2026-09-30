"""Isolated workload for query tutorial title and description examples."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query-example/t007/direct")
    async def tutorial007_direct(
        q: str | None = Query(default=None, title="Search query", min_length=3),
    ):
        return {"q": q}

    @app.get("/query-example/t007/annotated")
    async def tutorial007_annotated(
        q: Annotated[str | None, Query(title="Search query", min_length=3)] = None,
    ):
        return {"q": q}

    @app.get("/query-example/t008/direct")
    async def tutorial008_direct(
        q: str | None = Query(
            default=None,
            title="Search query",
            description="Filter this independent catalog by phrase.",
            min_length=3,
        ),
    ):
        return {"q": q}

    @app.get("/query-example/t008/annotated")
    async def tutorial008_annotated(
        q: Annotated[
            str | None,
            Query(
                title="Search query",
                description="Filter this independent catalog by phrase.",
                min_length=3,
            ),
        ] = None,
    ):
        return {"q": q}

    return app
