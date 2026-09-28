"""Independent request-parameter routes for query, path, cookie, and header inputs.

FastAPI's Python-only deprecation warning for the legacy ``Query(regex=...)``
parameter is not representable by the ASGI workflow observation schema.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel


class TrackingCookies(BaseModel):
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/catalog/{item_id}")
    async def catalog_item(
        item_id: Annotated[int, Path(gt=0, le=1000)], q: str
    ) -> dict[str, int | str]:
        return {"item_id": item_id, "q": q}

    @app.get("/search")
    async def search_items(q: Annotated[str, Query(min_length=3)]) -> dict[str, object]:
        return {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}], "q": q}

    @app.get("/cookies")
    async def read_cookies(
        cookies: Annotated[TrackingCookies, Cookie()],
    ) -> TrackingCookies:
        return cookies

    @app.get("/headers")
    async def read_headers(
        headers: Annotated[CommonHeaders, Header()],
    ) -> CommonHeaders:
        return headers

    @app.get("/legacy-query")
    async def legacy_query(
        q: Annotated[str | None, Query(regex="^fixedquery$")] = None,
    ) -> str:
        return f"Hello {q}" if q else "Hello World"

    return app
