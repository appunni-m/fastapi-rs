"""Independent inputs for query-parameter documentation section mappings."""

from typing import Annotated

from fastapi import FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query-section/optional")
    async def optional_query(q: str | None = None):
        return {"q": q}

    @app.get("/query-section/list/bare")
    async def bare_list(q: Annotated[list, Query()] = []):  # noqa: B006
        return {"q": q}

    @app.get("/query-section/list/typed")
    async def typed_integer_list(q: Annotated[list[int], Query()] = []):  # noqa: B006
        return {"q": q}

    return app
