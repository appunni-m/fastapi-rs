"""Public input workload for dependency signatures changed after registration."""

import asyncio
import inspect
from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query


def _query_parameter(name: str, alias: str, default: Any = ...) -> inspect.Parameter:
    return inspect.Parameter(
        name,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=int,
        default=Query(default, alias=alias, gt=0),
    )


def _dependency_parameter(name: str, dependency: Any) -> inspect.Parameter:
    return inspect.Parameter(
        name,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=dict[str, Any],
        default=Depends(dependency),
    )


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    def unrelated_original() -> str:
        return "unused-original"

    def unrelated_replacement() -> str:
        return "unused-replacement"

    def sync_direct(**values: int) -> dict[str, Any]:
        event_trace.append("sync-direct")
        return {"values": values, "events": list(event_trace)}

    sync_direct.__signature__ = inspect.Signature(
        [_query_parameter("registered", "registered-value", 4)]
    )

    @app.get("/direct")
    def direct(value: Annotated[dict[str, Any], Depends(sync_direct)]) -> dict[str, Any]:
        return value

    async def async_leaf(**values: int) -> dict[str, Any]:
        await asyncio.sleep(0)
        event_trace.append("async-leaf")
        return {"values": values}

    async_leaf.__signature__ = inspect.Signature(
        [_query_parameter("registered_async", "registered-async", 3)]
    )

    def sync_parent(**values: Any) -> dict[str, Any]:
        event_trace.append("sync-parent")
        return values

    sync_parent.__signature__ = inspect.Signature(
        [
            _dependency_parameter("child", async_leaf),
            _query_parameter("registered_parent", "registered-sync-parent", 5),
        ]
    )

    @app.get("/sync-parent-async-child")
    def sync_parent_async_child(
        value: Annotated[dict[str, Any], Depends(sync_parent)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace)}

    def sync_leaf(**values: int) -> dict[str, Any]:
        event_trace.append("sync-leaf")
        return {"values": values}

    sync_leaf.__signature__ = inspect.Signature(
        [_query_parameter("registered_sync", "registered-sync", 2)]
    )

    async def async_parent(**values: Any) -> dict[str, Any]:
        await asyncio.sleep(0)
        event_trace.append("async-parent")
        return values

    async_parent.__signature__ = inspect.Signature(
        [
            _dependency_parameter("child", sync_leaf),
            _query_parameter("registered_parent", "registered-async-parent", 7),
        ]
    )

    @app.get("/async-parent-sync-child")
    async def async_parent_sync_child(
        value: Annotated[dict[str, Any], Depends(async_parent)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace)}

    def replacement_original(**values: int) -> dict[str, Any]:
        event_trace.append("replacement-original")
        return values

    replacement_original.__signature__ = inspect.Signature(
        [_query_parameter("registered_source", "registered-source", 11)]
    )

    def sync_replacement(**values: int) -> dict[str, Any]:
        event_trace.append("sync-replacement")
        return values

    sync_replacement.__signature__ = inspect.Signature(
        [_query_parameter("sync_value", "sync-replacement")]
    )

    async def async_replacement(**values: int) -> dict[str, Any]:
        await asyncio.sleep(0)
        event_trace.append("async-replacement")
        return values

    async_replacement.__signature__ = inspect.Signature(
        [_query_parameter("async_value", "async-replacement")]
    )

    @app.get("/replacement")
    def replacement(
        value: Annotated[dict[str, Any], Depends(replacement_original)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace)}

    def resource_parent(**values: Any) -> dict[str, Any]:
        return values

    resource_parent.__signature__ = inspect.Signature(
        [_query_parameter("registered_resource", "registered-resource", 6)]
    )

    async def request_resource(
        seed: Annotated[int, Query(alias="resource-seed", gt=0)],
    ) -> AsyncIterator[int]:
        event_trace.append("dependency-enter")
        try:
            yield seed
        finally:
            event_trace.append("dependency-cleanup")

    @app.get("/resource")
    def resource(
        value: Annotated[dict[str, Any], Depends(resource_parent)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace)}

    def annotation_dependency(
        value: int = Query(..., alias="typed-value"),  # noqa: B008
    ) -> dict[str, Any]:
        return {"value": value, "value_type": type(value).__name__}

    @app.get("/annotation")
    def annotation(
        value: Annotated[dict[str, Any], Depends(annotation_dependency)],
    ) -> dict[str, Any]:
        return value

    @app.get("/state", include_in_schema=False)
    def state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    def configure_overrides(mode: str) -> dict[str, str]:
        choices = {
            "empty": {},
            "unrelated": {unrelated_original: unrelated_replacement},
            "self": {sync_direct: sync_direct},
            "first": {replacement_original: sync_replacement},
            "second": {replacement_original: async_replacement},
        }
        app.dependency_overrides.clear()
        app.dependency_overrides.update(choices[mode])
        return {"map_mode": mode}

    @app.post("/map/{mode}", include_in_schema=False)
    def change_override_map(mode: str) -> dict[str, str]:
        return configure_overrides(mode)

    @app.post("/annotation-string", include_in_schema=False)
    def change_annotation_to_string() -> dict[str, str]:
        parameter = annotation_dependency.__signature__.parameters["value"]
        annotation_dependency.__signature__ = inspect.Signature(
            [parameter.replace(annotation="str")]
        )
        return {"annotation": "str"}

    # These public signature changes occur only after the routes have captured
    # their original dependency declarations.
    sync_direct.__signature__ = inspect.Signature([_query_parameter("live", "live-value")])
    async_leaf.__signature__ = inspect.Signature([_query_parameter("live_async", "live-async")])
    sync_parent.__signature__ = inspect.Signature(
        [
            _dependency_parameter("child", async_leaf),
            _query_parameter("live_parent", "live-sync-parent"),
        ]
    )
    sync_leaf.__signature__ = inspect.Signature([_query_parameter("live_sync", "live-sync")])
    async_parent.__signature__ = inspect.Signature(
        [
            _dependency_parameter("child", sync_leaf),
            _query_parameter("live_parent", "live-async-parent"),
        ]
    )
    resource_parent.__signature__ = inspect.Signature(
        [_dependency_parameter("resource", request_resource)]
    )
    annotation_dependency.__signature__ = inspect.Signature(
        [
            inspect.Parameter(
                "value",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str,
                default=Query(..., alias="typed-value"),
            )
        ]
    )
    configure_overrides(str(factory_input["map_mode"]))
    return app
