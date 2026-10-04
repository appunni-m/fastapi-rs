"""Exercise public dependency cleanup ordering after an injected route failure."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

from fastapi import Depends, FastAPI


class _ResponseBoundaryTrace:
    def __init__(self, app: Callable[..., Any], events: list[str]) -> None:
        self._app = app
        self._events = events

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        async def trace_send(message: dict[str, Any]) -> None:
            await send(message)
            if message.get("type") == "http.response.start":
                self._events.append("response-start")
            elif message.get("type") == "http.response.body" and not message.get(
                "more_body", False
            ):
                self._events.append("response-end")

        await self._app(scope, receive, trace_send)


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> Any:
    app = FastAPI()

    async def function_resource() -> AsyncIterator[str]:
        event_trace.append("function-enter")
        try:
            yield "function-ready"
        finally:
            event_trace.append("function-cleanup")

    async def request_resource() -> AsyncIterator[str]:
        event_trace.append("request-enter")
        try:
            yield "request-ready"
        finally:
            event_trace.append("request-cleanup")

    @app.get("/scope-fault")
    async def scope_fault(
        function_value: str = Depends(function_resource, scope="function"),
        request_value: str = Depends(request_resource),
    ) -> dict[str, str]:
        return {"function": function_value, "request": request_value}

    @app.get("/scope-error")
    async def scope_error(
        function_value: str = Depends(function_resource, scope="function"),
        request_value: str = Depends(request_resource),
    ) -> None:
        raise RuntimeError("endpoint failure")

    @app.get("/scope-events")
    async def scope_events() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    return _ResponseBoundaryTrace(app, event_trace)
