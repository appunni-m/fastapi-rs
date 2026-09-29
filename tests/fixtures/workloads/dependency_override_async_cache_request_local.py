"""Input-only workload for async dependency override cache reuse."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    replacement_calls = {"count": 0}

    def original_dependency() -> int:
        return -1

    async def replacement_dependency() -> int:
        await asyncio.sleep(0)
        replacement_calls["count"] += 1
        return replacement_calls["count"]

    @app.get("/override-async-cache")
    def read_override_cache(
        first: Annotated[int, Depends(original_dependency)],
        second: Annotated[int, Depends(original_dependency)],
    ) -> dict[str, int]:
        return {
            "first": first,
            "second": second,
            "replacement_calls": replacement_calls["count"],
        }

    app.dependency_overrides[original_dependency] = replacement_dependency
    return app
