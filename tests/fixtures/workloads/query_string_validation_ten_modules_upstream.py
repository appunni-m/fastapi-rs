"""Small independent apps for pinned FastAPI query-validation test modules."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import AfterValidator


def _items(q: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        result["q"] = q
    return result


def _check_id(value: str) -> str:
    if not value.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return value


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/tutorial001/items/")
    async def plain_optional_query(q: str | None = None) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial003/items/")
    async def bounded_query(
        q: str | None = Query(default=None, min_length=3, max_length=50),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial004/items/")
    async def patterned_query(
        q: str | None = Query(
            default=None,
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
        ),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial005/items/")
    async def defaulted_query(
        q: str = Query(default="fixedquery", min_length=3),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial006c/items/")
    async def required_bounded_query(
        q: str | None = Query(min_length=3),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial007/items/")
    async def titled_query(
        q: str | None = Query(default=None, title="Query string", min_length=3),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial008/items/")
    async def described_query(
        q: str | None = Query(
            default=None,
            title="Query string",
            description=(
                "Query string for the items to search in the database that have a good match"
            ),
            min_length=3,
        ),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial009/items/")
    async def aliased_query(
        q: str | None = Query(default=None, alias="item-query"),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial010/items/")
    async def deprecated_aliased_query(
        q: str | None = Query(
            default=None,
            alias="item-query",
            title="Query string",
            description=(
                "Query string for the items to search in the database that have a good match"
            ),
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ) -> dict[str, object]:
        return _items(q)

    @app.get("/tutorial015/items/")
    async def custom_validated_query(
        id: Annotated[str | None, AfterValidator(_check_id)] = None,
    ) -> dict[str, str | None]:
        names = {
            "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
            "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
            "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
        }
        return {"id": id, "name": names.get(id) if id else None}

    return app
