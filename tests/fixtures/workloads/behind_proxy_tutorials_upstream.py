"""Independent ASGI workloads for FastAPI root-path OpenAPI policy."""

from __future__ import annotations

from fastapi import FastAPI, Request


def _register_echo_route(app: FastAPI) -> FastAPI:
    @app.get("/app")
    def read_service(request: Request):
        return {"message": "Service is ready", "root_path": request.scope.get("root_path")}

    return app


def create_root_path_only_app() -> FastAPI:
    return _register_echo_route(FastAPI(root_path="/edge/v2"))


def create_servers_with_root_path_app() -> FastAPI:
    return _register_echo_route(
        FastAPI(
            root_path="/edge/v2",
            servers=[
                {"url": "https://preview.example.net", "description": "Preview"},
                {"url": "https://api.example.net", "description": "Production"},
            ],
        )
    )


def create_servers_without_root_path_app() -> FastAPI:
    return _register_echo_route(
        FastAPI(
            root_path="/edge/v2",
            root_path_in_servers=False,
            servers=[
                {"url": "https://preview.example.net", "description": "Preview"},
                {"url": "https://api.example.net", "description": "Production"},
            ],
        )
    )
