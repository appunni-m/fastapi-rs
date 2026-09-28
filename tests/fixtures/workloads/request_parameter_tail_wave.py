"""Independent path, repeated-query, and repeated-header parameter workloads."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Header, Path, Query

_EMPTY_QUERY_VALUES: list = []


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/bounded/{item_id}")
    async def bounded_item(
        item_id: Annotated[int, Path(title="Identifier within the accepted range", ge=0, le=1000)],
        q: str,
        size: Annotated[float, Query(gt=0, lt=10.5)],
    ) -> dict[str, int | str | float]:
        result: dict[str, int | str | float] = {"item_id": item_id}
        if q:
            result["q"] = q
        if size:
            result["size"] = size
        return result

    @app.get("/repeated-query/")
    async def multi_query(q: Annotated[list, Query()] = _EMPTY_QUERY_VALUES) -> dict[str, list]:
        return {"q": q}

    @app.get("/header-list/")
    async def read_header(
        x_token: Annotated[list[str] | None, Header()] = None,
    ) -> dict[str, list[str] | None]:
        return {"X-Token values": x_token}

    return app
