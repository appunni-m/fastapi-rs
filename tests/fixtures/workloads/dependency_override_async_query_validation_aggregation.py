"""Input-only workload for repeated-edge async override validation."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    override_calls = {"count": 0}

    def original_dependency() -> int:
        return 0

    async def query_override(q: int | None = None) -> int | None:
        await asyncio.sleep(0)
        override_calls["count"] += 1
        return q

    @app.get("/override-async-query-validation")
    def read_override(
        first: Annotated[int | None, Depends(original_dependency)],
        second: Annotated[int | None, Depends(original_dependency)],
    ) -> dict[str, object]:
        return {
            "first": first,
            "second": second,
            "duplicate_equal": first == second,
            "call_count": override_calls["count"],
        }

    app.dependency_overrides[original_dependency] = query_override
    return app
