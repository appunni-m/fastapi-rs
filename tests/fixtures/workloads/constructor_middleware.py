"""Independent FastAPI constructor middleware ordering workload."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from fastapi.middleware import Middleware


class TraceMiddleware:
    def __init__(self, app: Any, label: str, events: list[str]) -> None:
        self.app = app
        self.label = label
        self.events = events

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        record = scope.get("path") == "/probe"
        if record:
            self.events.append(f"{self.label}:request")

        async def traced_send(message: dict[str, Any]) -> None:
            if record and message.get("type") == "http.response.start":
                self.events.append(f"{self.label}:response")
            await send(message)

        await self.app(scope, receive, traced_send)


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    middleware = [
        Middleware(TraceMiddleware, label=item["label"], events=event_trace)
        for item in factory_input["middleware"]
    ]
    app = FastAPI(middleware=middleware)

    @app.get("/probe")
    async def probe() -> dict[str, str]:
        event_trace.append("route")
        return {"message": "probe"}

    @app.get("/observe")
    async def observe() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    return app
