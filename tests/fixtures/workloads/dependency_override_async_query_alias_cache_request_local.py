"""Input-only workload for an aliased optional-query async override."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI, Query


def create_app() -> FastAPI:
    app = FastAPI()
    override_calls = {"count": 0}

    def original_dependency() -> str:
        return "original"

    async def query_override(
        q: Annotated[str | None, Query(alias="search")] = None,
    ) -> str | None:
        await asyncio.sleep(0)
        override_calls["count"] += 1
        return q

    @app.get("/override-async-query-alias-cache")
    def read_override(
        first: Annotated[str | None, Depends(original_dependency)],
        second: Annotated[str | None, Depends(original_dependency)],
    ) -> dict[str, object]:
        return {
            "search": first,
            "duplicate_equal": first == second,
            "call_count": override_calls["count"],
        }

    app.dependency_overrides[original_dependency] = query_override
    return app
