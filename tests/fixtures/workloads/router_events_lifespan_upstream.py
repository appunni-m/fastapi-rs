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


def _callback(
    trace: list[str],
    marker: str,
    is_async: bool,
    item_store: dict[str, Any] | None = None,
    populate_items: Mapping[str, Any] | None = None,
) -> Any:
    def record() -> None:
        trace.append(marker)
        if item_store is not None and populate_items is not None:
            item_store.update(populate_items)

    if is_async:

        async def callback() -> None:
            record()

    else:

        def callback() -> None:
            record()

    callback.__name__ = marker.replace("-", "_")
    return callback


def _lifespan_context(spec: Mapping[str, Any] | None, trace: list[str]) -> Any:
    if spec is None:
        return None

    kind = spec["kind"]
    startup_marker = spec.get("startup_marker")
    shutdown_marker = spec.get("shutdown_marker")
    yielded_state = spec.get("state")
    startup_error = spec.get("startup_error")
    suppress_startup_error = spec.get("suppress_startup_error", False)
    suppressed_marker = spec.get("suppressed_marker")

    def record(marker: Any) -> None:
        if marker is not None:
            trace.append(marker)

    if kind == "async-context-manager":

        @asynccontextmanager
        async def context_manager(app: FastAPI | APIRouter) -> Any:
            del app
            record(startup_marker)
            if startup_error is not None:
                raise ValueError(startup_error)
            try:
                yield yielded_state
            except ValueError:
                if not suppress_startup_error:
                    raise
                record(suppressed_marker)
            finally:
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


def _node_options(
    spec: Mapping[str, Any],
    trace: list[str],
    item_store: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[Any]]:
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
            (
                event["stage"],
                _callback(
                    trace,
                    event["marker"],
                    event.get("async", False),
                    item_store,
                    event.get("populate_items"),
                ),
            )
        )
    return options, legacy_callbacks


def _add_legacy_events(target: Any, events: list[tuple[str, Any]]) -> None:
    for stage, callback in events:
        target.on_event(stage)(callback)


def _add_direct_events(target: Any, spec: Mapping[str, Any], trace: list[str]) -> None:
    for event in spec.get("direct_event_handlers", []):
        target.add_event_handler(
            event["stage"],
            _callback(trace, event["marker"], event.get("async", False)),
        )


def _add_state_route(target: Any, route: Mapping[str, Any]) -> None:
    path = route.get("path", "/")
    message = route.get("message", "Hello World")

    async def endpoint(request: Request) -> dict[str, Any]:
        return {
            "message": message,
            "state": dict(request.scope.get("state", {})),
        }

    target.get(path, response_model=None)(endpoint)


def _add_item_lookup_route(
    target: Any,
    route: Mapping[str, Any],
    item_store: dict[str, Any],
) -> None:
    path = route.get("path", "/items/{item_id}")

    async def endpoint(item_id: str) -> Any:
        return item_store[item_id]

    target.get(path, response_model=None)(endpoint)


def _build_router(
    spec: Mapping[str, Any],
    trace: list[str],
    item_store: dict[str, Any],
) -> APIRouter:
    options, legacy_events = _node_options(spec, trace, item_store)
    router = APIRouter(**options)
    _add_legacy_events(router, legacy_events)
    _add_direct_events(router, spec, trace)
    for route in spec.get("routes", []):
        if route.get("item_lookup", False):
            _add_item_lookup_route(router, route, item_store)
        else:
            _add_state_route(router, route)
    for child_spec in spec.get("routers", []):
        router.include_router(_build_router(child_spec, trace, item_store))
    return router


def _build_app(spec: Mapping[str, Any], trace: list[str]) -> FastAPI:
    item_store: dict[str, Any] = {}
    options, legacy_events = _node_options(spec, trace, item_store)
    app = FastAPI(**options)
    _add_legacy_events(app, legacy_events)
    _add_direct_events(app, spec, trace)
    for route in spec.get("routes", []):
        if route.get("item_lookup", False):
            _add_item_lookup_route(app, route, item_store)
        else:
            _add_state_route(app, route)
    for child_spec in spec.get("routers", []):
        app.include_router(_build_router(child_spec, trace, item_store))
    for mount_spec in spec.get("mounts", []):
        app.mount(mount_spec["path"], _build_app(mount_spec["application"], trace))
    return app


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one app/router tree from declarative callback and state inputs."""
    return _build_app(factory_input["application"], event_trace)
