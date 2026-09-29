"""Input-only workload for async overrides on uncached dependency edges."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    override_calls = {"count": 0}

    def original_dependency() -> int:
        return 0

    async def replacement_dependency() -> int:
        await asyncio.sleep(0)
        override_calls["count"] += 1
        return override_calls["count"]

    @app.get("/override-async-uncached")
    def read_override(
        first: Annotated[int, Depends(original_dependency, use_cache=False)],
        second: Annotated[int, Depends(original_dependency, use_cache=False)],
        cached: Annotated[int, Depends(original_dependency)],
    ) -> dict[str, object]:
        return {
            "first": first,
            "second": second,
            "cached": cached,
            "call_count": override_calls["count"],
        }

    app.dependency_overrides[original_dependency] = replacement_dependency
    return app
