"""Independent workloads for query and header parameter tutorial reviews."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Header


def create_query_tutorial001_app() -> FastAPI:
    app = FastAPI()
    fake_items_db = [
        {"item_name": "Foo"},
        {"item_name": "Bar"},
        {"item_name": "Baz"},
    ]

    @app.get("/items/")
    async def read_item(skip: int = 0, limit: int = 10):
        return fake_items_db[skip : skip + limit]

    return app


def create_query_tutorial002_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: str, q: str | None = None):
        if q:
            return {"item_id": item_id, "q": q}
        return {"item_id": item_id}

    return app


def create_query_tutorial003_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: str, q: str | None = None, short: bool = False):
        item = {"item_id": item_id}
        if q:
            item.update({"q": q})
        if not short:
            item.update({"description": "This is an amazing item that has a long description"})
        return item

    return app


def create_query_tutorial004_app() -> FastAPI:
    app = FastAPI()

    @app.get("/users/{user_id}/items/{item_id}")
    async def read_user_item(user_id: int, item_id: str, q: str | None = None, short: bool = False):
        item = {"item_id": item_id, "owner_id": user_id}
        if q:
            item.update({"q": q})
        if not short:
            item.update({"description": "This is an amazing item that has a long description"})
        return item

    return app


def create_query_tutorial005_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_user_item(item_id: str, needy: str):
        return {"item_id": item_id, "needy": needy}

    return app


def create_query_tutorial006_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_user_item(item_id: str, needy: str, skip: int = 0, limit: int | None = None):
        return {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}

    return app


def create_header_tutorial001_direct_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(user_agent: str | None = Header(default=None)):
        return {"User-Agent": user_agent}

    return app


def create_header_tutorial001_annotated_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(user_agent: Annotated[str | None, Header()] = None):
        return {"User-Agent": user_agent}

    return app


def create_header_tutorial002_direct_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(
        strange_header: str | None = Header(default=None, convert_underscores=False),
    ):
        return {"strange_header": strange_header}

    return app


def create_header_tutorial002_annotated_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(
        strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
    ):
        return {"strange_header": strange_header}

    return app


def create_header_tutorial003_direct_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(x_token: list[str] | None = Header(default=None)):  # noqa: B008
        return {"X-Token values": x_token}

    return app


def create_header_tutorial003_annotated_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/")
    async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
        return {"X-Token values": x_token}

    return app
