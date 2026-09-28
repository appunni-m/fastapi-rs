"""Independent dependency cache, override, and yield-cleanup workload."""

import json
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse


def create_app() -> FastAPI:
    app = FastAPI(title="Dependency Lifecycle", version="1.0.0")
    state: dict[str, Any] = {"calls": 0, "events": []}

    async def cached_value() -> str:
        state["calls"] += 1
        return f"value-{state['calls']}"

    @app.get("/cache/reuse")
    async def cache_reuse(
        first: str = Depends(cached_value),
        second: str = Depends(cached_value),
    ) -> dict[str, Any]:
        return {"values": [first, second], "calls": state["calls"]}

    @app.get("/cache/fresh")
    async def cache_fresh(
        cached_before: str = Depends(cached_value),
        fresh: str = Depends(cached_value, use_cache=False),
        cached_after: str = Depends(cached_value),
    ) -> dict[str, Any]:
        return {
            "values": [cached_before, fresh, cached_after],
            "calls": state["calls"],
        }

    async def original_parameters(q: str) -> dict[str, str]:
        return {"source": "original", "q": q}

    async def replacement_region(region: str) -> dict[str, str]:
        return {"source": "replacement", "region": region}

    app.dependency_overrides[original_parameters] = replacement_region

    @app.get("/override/profile")
    async def overridden_profile(
        profile: Annotated[dict[str, str], Depends(original_parameters)],
    ) -> dict[str, str]:
        return profile

    async def function_resource() -> dict[str, bool]:
        state["events"].append("function-enter")
        resource = {"open": True}
        try:
            yield resource
        finally:
            resource["open"] = False
            state["events"].append("function-exit")

    async def request_resource() -> dict[str, bool]:
        state["events"].append("request-enter")
        resource = {"open": True}
        try:
            yield resource
        finally:
            resource["open"] = False
            state["events"].append("request-exit")

    @app.get("/yield/scopes")
    async def yield_scopes(
        function_value: Annotated[dict[str, bool], Depends(function_resource, scope="function")],
        request_value: Annotated[dict[str, bool], Depends(request_resource, scope="request")],
    ) -> StreamingResponse:
        async def stream():
            yield json.dumps(
                {
                    "function_open": function_value["open"],
                    "request_open": request_value["open"],
                    "events": list(state["events"]),
                }
            ).encode("utf-8")

        return StreamingResponse(stream(), media_type="application/json")

    async def exception_aware_resource():
        state["events"].append("error-enter")
        try:
            yield
        except HTTPException as exc:
            state["events"].append("error-caught")
            raise HTTPException(
                status_code=exc.status_code,
                detail={"original": exc.detail, "events": state["events"]},
            ) from exc
        finally:
            state["events"].append("error-exit")

    @app.get("/yield/error")
    async def yield_error(
        _resource: Annotated[None, Depends(exception_aware_resource, scope="function")],
    ) -> None:
        raise HTTPException(status_code=409, detail="operation failed")

    return app
