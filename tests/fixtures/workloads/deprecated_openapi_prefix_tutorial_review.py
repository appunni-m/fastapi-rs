"""Independent ASGI observations for FastAPI root-path constructor options."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request


class _RecordHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[dict[str, str]] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(
            {
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
        )


def create_app(factory_input: Mapping[str, Any], _event_trace: list[str]) -> FastAPI:
    """Build an app from input so the oracle and target receive identical stimuli."""
    handler = _RecordHandler()
    logger = logging.getLogger("fastapi")
    logger.addHandler(handler)
    supplied_servers = factory_input.get("servers")
    try:
        app = FastAPI(
            openapi_prefix=factory_input.get("openapi_prefix", ""),
            root_path=factory_input.get("root_path", ""),
            root_path_in_servers=factory_input.get("root_path_in_servers", True),
            servers=supplied_servers,
        )
    finally:
        logger.removeHandler(handler)

    for name, value in factory_input.get("attribute_updates", {}).items():
        setattr(app, name, value)

    @app.middleware("http")
    async def observe_root_path(request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["x-fastapi-root-path"] = str(request.scope.get("root_path", ""))
        return response

    @app.get("/inspect")
    def inspect_root_path(request: Request) -> dict[str, Any]:
        return {
            "root_path": app.root_path,
            "root_path_in_servers": app.root_path_in_servers,
            "scope_root_path": request.scope.get("root_path", ""),
            "deprecation_records": handler.records,
        }

    if supplied_servers is not None:

        @app.get("/configured-servers", include_in_schema=False)
        def configured_servers() -> dict[str, Any]:
            return {"supplied": supplied_servers, "application": app.servers}

    return app
