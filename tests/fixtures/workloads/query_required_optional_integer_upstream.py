"""Independent query workload for FastAPI 0.141.1.

Route behavior follows ``../fastapi/tests/main.py:145-208``; the corresponding
consumer requests and assertions are in ``../fastapi/tests/test_query.py``.

The collection routes are registered with the trailing slash used by the
upstream TestClient inputs. This keeps the query cases focused on extraction;
the TestClient's redirect-following behavior is not part of these ASGI inputs.
"""

from fastapi import FastAPI, Query


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

    @app.get("/query/param")
    async def read_explicit_optional_text(query=Query(default=None)):  # noqa: B008
        if query is None:
            return "foo bar"
        return f"foo bar {query}"

    @app.get("/query/param-required")
    async def read_explicit_required_text(query=Query()):  # noqa: B008
        return f"foo bar {query}"

    @app.get("/query/param-required/int")
    async def read_explicit_required_integer(query: int = Query()):
        return f"foo bar {query}"

    @app.get("/query/frozenset/")
    async def read_integer_frozenset(query: frozenset[int] = Query(...)):  # noqa: B008
        return ",".join(map(str, sorted(query)))

    @app.get("/query/list/")
    async def read_integer_list(device_ids: list[int] = Query()) -> list[int]:  # noqa: B008
        return device_ids

    @app.get("/query/list-default/")
    async def read_integer_list_default(
        device_ids: list[int] = Query(default=[]),  # noqa: B008
    ) -> list[int]:
        return device_ids

    return app
