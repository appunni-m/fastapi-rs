"""Independent default-value probes for FastAPI query parameters.

The required and default list behaviors are covered by FastAPI 0.141.1's
``tests/test_query.py``. These independent cases also expose undefined
sentinel handling, default validation, and per-request mutable-default copies.
"""

from fastapi import FastAPI, Query
from pydantic_core import PydanticUndefined


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/undefined")
    async def explicit_undefined(query: int = Query(default=PydanticUndefined)):
        return query

    @app.get("/invalid-default")
    async def invalid_default(items: list[int] = Query(default=["invalid"])):  # noqa: B008
        return items

    @app.get("/mutable-default")
    async def mutable_default(items: list[int] = Query(default=[])):  # noqa: B008
        items.append(7)
        return items

    return app
