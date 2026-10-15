"""Independent ASGI workloads for behind-a-proxy documentation sections."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one app for a documented redirect, root_path, or mount scenario."""
    scenario = factory_input["scenario"]

    if scenario == "https-slash-redirect":
        app = FastAPI()

        @app.get("/items/")
        def read_items() -> list[str]:
            return ["plumbus", "portal gun"]

        return app

    if scenario == "root-path-scope":
        app = FastAPI()

        @app.get("/app")
        def read_app(request: Request) -> dict[str, str | None]:
            return {
                "message": "Hello World",
                "root_path": request.scope.get("root_path"),
            }

        return app

    if scenario == "mounted-root-path":
        app = FastAPI()
        subapi = FastAPI()

        @subapi.get("/sub")
        def read_sub(request: Request) -> dict[str, str | None]:
            return {
                "message": "Hello World from sub API",
                "root_path": request.scope.get("root_path"),
            }

        app.mount("/subapi", subapi)
        return app

    raise ValueError(f"unknown behind-a-proxy workload scenario: {scenario!r}")
