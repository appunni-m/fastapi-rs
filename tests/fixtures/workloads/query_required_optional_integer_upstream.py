"""Independent query workload for FastAPI 0.141.1.

Route behavior follows ``../fastapi/tests/main.py:145-171``; the corresponding
consumer requests and assertions are in ``../fastapi/tests/test_query.py``.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query")
    async def read_required_text(query):
        return f"foo bar {query}"

    @app.get("/query/optional")
    async def read_optional_text(query=None):
        if query is None:
            return "foo bar"
        return f"foo bar {query}"

    @app.get("/query/int")
    async def read_required_integer(query: int):
        return f"foo bar {query}"

    @app.get("/query/int/optional")
    async def read_optional_integer(query: int | None = None):
        if query is None:
            return "foo bar"
        return f"foo bar {query}"

    @app.get("/query/int/default")
    async def read_integer_with_default(query: int = 10):
        return f"foo bar {query}"

    return app
