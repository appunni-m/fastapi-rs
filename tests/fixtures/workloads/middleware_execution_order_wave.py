"""Independent request/response trace for FastAPI middleware stack order."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


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


def create_app() -> FastAPI:
    app = FastAPI()
    events: list[str] = []
    app.add_middleware(TraceMiddleware, label="first-added", events=events)
    app.add_middleware(TraceMiddleware, label="last-added", events=events)

    @app.get("/probe")
    async def probe() -> dict[str, str]:
        events.append("route")
        return {"message": "probe"}

    @app.get("/observe")
    async def observe() -> dict[str, list[str]]:
        return {"events": list(events)}

    return app
