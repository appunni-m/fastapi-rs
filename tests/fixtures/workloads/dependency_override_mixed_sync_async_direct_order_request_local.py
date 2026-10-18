"""Input-only workload for ordered sync and overridden async dependencies."""

import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI


def create_app(_factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    app = FastAPI()
    calls = {"sync": 0, "async": 0}

    def unoverridden_sync_dependency() -> str:
        calls["sync"] += 1
        event_trace.append("sync")
        return f"sync-{calls['sync']}"

    def original_second_dependency() -> str:
        return "original-second"

    async def async_override() -> str:
        await asyncio.sleep(0)
        calls["async"] += 1
        event_trace.append("async")
        return f"async-{calls['async']}"

    @app.get("/mixed-sync-async-direct-order")
    def read_dependencies(
        sync_value: Annotated[str, Depends(unoverridden_sync_dependency)],
        async_value: Annotated[str, Depends(original_second_dependency)],
    ) -> dict[str, object]:
        return {
            "sync_value": sync_value,
            "async_value": async_value,
            "calls": dict(calls),
            "resolution_order": list(event_trace),
        }

    app.dependency_overrides[original_second_dependency] = async_override
    return app
