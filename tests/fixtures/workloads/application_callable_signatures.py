"""Input bundle setup for FastAPI and inherited Starlette signature probes."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


class NoopMiddleware:
    def __init__(self, app: Any) -> None:
        self.app = app


async def endpoint(request: Any) -> dict[str, str]:
    return {"path": request.url.path}


async def exception_handler(request: Any, error: Exception) -> dict[str, str]:
    return {"error": str(error)}


def create_argument_bundles() -> dict[str, dict[str, object]]:
    app = FastAPI()
    app.add_route("/probe", endpoint, name="route")
    app.host("probe.example", app, name="host")
    app.url_path_for("route")
    app.add_middleware(NoopMiddleware)
    app.add_exception_handler(ValueError, exception_handler)
    app.mount("/mounted", FastAPI(), name="mounted")
    return {"unused": {"args": [], "kwargs": {}}}
