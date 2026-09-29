"""Input-only workload for optional-query async override cache reuse."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    override_calls = {"count": 0}

    def original_dependency() -> str:
        return "original"

    async def query_override(q: str | None = None) -> str | None:
        await asyncio.sleep(0)
        override_calls["count"] += 1
        return q

    @app.get("/override-async-query-cache")
    def read_override(
        first: Annotated[str | None, Depends(original_dependency)],
        second: Annotated[str | None, Depends(original_dependency)],
    ) -> dict[str, object]:
        return {
            "q": first,
            "duplicate_equal": first == second,
            "call_count": override_calls["count"],
        }

    app.dependency_overrides[original_dependency] = query_override
    return app
