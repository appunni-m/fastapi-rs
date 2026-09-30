"""Independent lifecycle workload for FastAPI router and app behavior.

FastAPI 0.141.1 declares Python >=3.10; parity execution uses the pinned CPython
3.12.13 oracle profile. The v4 workflow selects warning sidecars while constructing
the legacy ``on_event`` app and running its lifespan and HTTP actions.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator, Mapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, Request


def _callback(trace: list[str], marker: str, is_async: bool) -> Any:
    if is_async:

        async def callback() -> None:
            trace.append(marker)

    else:

        def callback() -> None:
            trace.append(marker)

    callback.__name__ = marker.replace("-", "_")
    return callback


def _lifespan_context(spec: Mapping[str, Any] | None, trace: list[str]) -> Any:
    if spec is None:
        return None

    kind = spec["kind"]
    startup_marker = spec.get("startup_marker")
    shutdown_marker = spec.get("shutdown_marker")
    yielded_state = spec.get("state")

    def record(marker: Any) -> None:
        if marker is not None:
            trace.append(marker)

    if kind == "async-context-manager":

        @asynccontextmanager
        async def context_manager(app: FastAPI | APIRouter) -> Any:
            del app
            record(startup_marker)
            yield yielded_state
            record(shutdown_marker)

        return context_manager

    if kind == "async-generator":

        async def async_generator(
            app: FastAPI | APIRouter,
        ) -> AsyncGenerator[Any, None]:
            del app
            record(startup_marker)
            yield yielded_state
            record(shutdown_marker)

        return async_generator

    if kind == "sync-generator":

        def sync_generator(app: FastAPI | APIRouter) -> Generator[Any, None, None]:
            del app
            record(startup_marker)
            yield yielded_state
            record(shutdown_marker)

        return sync_generator

    raise ValueError("unsupported lifespan kind in workload input")


def _node_options(spec: Mapping[str, Any], trace: list[str]) -> tuple[dict[str, Any], list[Any]]:
    options: dict[str, Any] = {}
    lifespan = _lifespan_context(spec.get("lifespan"), trace)
    if lifespan is not None:
        options["lifespan"] = lifespan

    parameter_events = spec.get("parameter_events", {})
    for stage in ("startup", "shutdown"):
        marker_names = parameter_events.get(stage, [])
        if marker_names:
            options[f"on_{stage}"] = [_callback(trace, marker, False) for marker in marker_names]

    legacy_callbacks = []
    for event in spec.get("legacy_on_event", []):
        legacy_callbacks.append(
            (event["stage"], _callback(trace, event["marker"], event.get("async", False)))
        )
    return options, legacy_callbacks


def _add_legacy_events(target: Any, events: list[tuple[str, Any]]) -> None:
    for stage, callback in events:
        target.on_event(stage)(callback)


def _add_state_route(target: Any, route: Mapping[str, Any]) -> None:
    path = route.get("path", "/")
    message = route.get("message", "Hello World")

    async def endpoint(request: Request) -> dict[str, Any]:
        return {
            "message": message,
            "state": dict(request.scope.get("state", {})),
        }

    target.get(path, response_model=None)(endpoint)


def _build_router(spec: Mapping[str, Any], trace: list[str]) -> APIRouter:
    options, legacy_events = _node_options(spec, trace)
    router = APIRouter(**options)
    _add_legacy_events(router, legacy_events)
    for route in spec.get("routes", []):
        _add_state_route(router, route)
    for child_spec in spec.get("routers", []):
        router.include_router(_build_router(child_spec, trace))
    return router


def _build_app(spec: Mapping[str, Any], trace: list[str]) -> FastAPI:
    options, legacy_events = _node_options(spec, trace)
    app = FastAPI(**options)
    _add_legacy_events(app, legacy_events)
    for route in spec.get("routes", []):
        _add_state_route(app, route)
    for child_spec in spec.get("routers", []):
        app.include_router(_build_router(child_spec, trace))
    for mount_spec in spec.get("mounts", []):
        app.mount(mount_spec["path"], _build_app(mount_spec["application"], trace))
    return app


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one app/router tree from declarative callback and state inputs."""
    return _build_app(factory_input["application"], event_trace)
