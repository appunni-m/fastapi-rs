"""Input-only workload for ordered async overrides on two cache keys."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    calls = {"first": 0, "second": 0}
    resolution_order: list[str] = []

    def original_first() -> str:
        return "original-first"

    def original_second() -> str:
        return "original-second"

    async def first_override() -> str:
        await asyncio.sleep(0)
        calls["first"] += 1
        resolution_order.append("first")
        return f"first-{calls['first']}"

    async def second_override() -> str:
        await asyncio.sleep(0)
        calls["second"] += 1
        resolution_order.append("second")
        return f"second-{calls['second']}"

    @app.get("/override-async-two-keys")
    def read_overrides(
        first: Annotated[str, Depends(original_first)],
        first_again: Annotated[str, Depends(original_first)],
        second: Annotated[str, Depends(original_second)],
        second_again: Annotated[str, Depends(original_second)],
    ) -> dict[str, object]:
        return {
            "first": first,
            "first_again": first_again,
            "second": second,
            "second_again": second_again,
            "calls": dict(calls),
            "resolution_order": list(resolution_order),
        }

    app.dependency_overrides[original_first] = first_override
    app.dependency_overrides[original_second] = second_override
    return app
