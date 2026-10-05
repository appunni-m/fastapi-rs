"""Input-only public workload for async children beneath sync dependencies."""

import asyncio
from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input
    app = FastAPI()

    async def async_child(seed: Annotated[int, Query(gt=0)]) -> int:
        await asyncio.sleep(0)
        event_trace.append(f"async-child:{seed}")
        return seed * 3

    def sync_parent(value: Annotated[int, Depends(async_child)]) -> int:
        event_trace.append(f"sync-parent:{value}")
        return value + 2

    @app.get("/nested")
    def nested(value: Annotated[int, Depends(sync_parent)]) -> dict[str, object]:
        event_trace.append(f"endpoint:{value}")
        return {"value": value, "events": list(event_trace)}

    async def async_leaf(seed: Annotated[int, Query(gt=0)]) -> int:
        await asyncio.sleep(0)
        event_trace.append(f"async-leaf:{seed}")
        return seed * 5

    def sync_lower(value: Annotated[int, Depends(async_leaf)]) -> int:
        event_trace.append(f"sync-lower:{value}")
        return value + 3

    async def async_middle(value: Annotated[int, Depends(sync_lower)]) -> int:
        await asyncio.sleep(0)
        event_trace.append(f"async-middle:{value}")
        return value * 2

    def sync_root(value: Annotated[int, Depends(async_middle)]) -> int:
        event_trace.append(f"sync-root:{value}")
        return value + 7

    @app.get("/alternating")
    async def alternating(value: Annotated[int, Depends(sync_root)]) -> dict[str, object]:
        event_trace.append(f"endpoint:{value}")
        return {"value": value, "events": list(event_trace)}

    def original_sync_child(seed: Annotated[int, Query(gt=0)]) -> int:
        event_trace.append(f"original-sync-child:{seed}")
        return seed * 2

    async def replacement_async_child(seed: Annotated[int, Query(gt=0)]) -> int:
        await asyncio.sleep(0)
        event_trace.append(f"async-override-child:{seed}")
        return seed * 7

    def sync_override_parent(value: Annotated[int, Depends(original_sync_child)]) -> int:
        event_trace.append(f"sync-override-parent:{value}")
        return value + 13

    @app.get("/override")
    def overridden(value: Annotated[int, Depends(sync_override_parent)]) -> dict[str, object]:
        event_trace.append(f"endpoint:{value}")
        return {"value": value, "events": list(event_trace)}

    app.dependency_overrides[original_sync_child] = replacement_async_child

    uncached_calls = {"count": 0}

    async def uncached_async_child(seed: Annotated[int, Query(gt=0)]) -> int:
        await asyncio.sleep(0)
        uncached_calls["count"] += 1
        event_trace.append(f"uncached-async-child:{uncached_calls['count']}")
        return seed * 100 + uncached_calls["count"]

    def cached_sync_parent(
        value: Annotated[int, Depends(uncached_async_child, use_cache=False)],
    ) -> int:
        event_trace.append(f"cached-sync-parent:{value}")
        return value + 19

    @app.get("/uncached-child")
    def repeated_cached_parent(
        left: Annotated[int, Depends(cached_sync_parent)],
        right: Annotated[int, Depends(cached_sync_parent)],
    ) -> dict[str, object]:
        event_trace.append(f"endpoint:{left}:{right}")
        return {"left": left, "right": right, "events": list(event_trace)}

    async def query_async_child(child_seed: Annotated[int, Query(gt=0)]) -> int:
        await asyncio.sleep(0)
        event_trace.append(f"query-async-child:{child_seed}")
        return child_seed * 2

    def query_sync_parent(
        value: Annotated[int, Depends(query_async_child)],
        parent_seed: Annotated[int, Query(gt=0)],
    ) -> int:
        event_trace.append(f"query-sync-parent:{value}:{parent_seed}")
        return value + parent_seed

    @app.get("/query-aggregation")
    def child_and_parent_query(
        value: Annotated[int, Depends(query_sync_parent)],
        limit: Annotated[int, Query(gt=0)],
    ) -> dict[str, object]:
        event_trace.append(f"endpoint:{value}:{limit}")
        return {"value": value + limit, "events": list(event_trace)}

    async def async_resource(seed: Annotated[int, Query(gt=0)]) -> AsyncIterator[int]:
        await asyncio.sleep(0)
        event_trace.append("dependency-enter")
        try:
            yield seed * 11
        finally:
            await asyncio.sleep(0)
            event_trace.append("dependency-cleanup")

    def sync_resource_parent(value: Annotated[int, Depends(async_resource)]) -> int:
        return value + 17

    @app.get("/resource")
    def resource(value: Annotated[int, Depends(sync_resource_parent)]) -> dict[str, int]:
        event_trace.append(f"endpoint:{value}")
        return {"value": value}

    @app.get("/resource-error")
    def resource_error(value: Annotated[int, Depends(sync_resource_parent)]) -> None:
        event_trace.append(f"endpoint-error:{value}")
        raise RuntimeError("nested-resource-endpoint-error")

    @app.get("/state")
    def observed_state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    return app
