"""Independent ASGI workload for a proxy-stripped mount prefix."""

from __future__ import annotations

from fastapi import FastAPI, Request


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI-RS root-path proxy workload")

    @app.get("/app")
    async def read_app(request: Request) -> dict[str, str | None]:
        return {
            "message": "Hello World",
            "root_path": request.scope.get("root_path"),
        }

    return app
