"""Independent exception-handler and failed-dependency ASGI stimuli."""

from __future__ import annotations

from collections.abc import Generator, Mapping
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse


async def server_error_handler(_request: Request, _exception: Exception) -> JSONResponse:
    return JSONResponse({"error": "service-fault"}, status_code=500)


def invalid_dependency_value() -> str:
    raise ValueError("dependency initialization failed")


def failing_yield_dependency() -> Generator[str, None, None]:
    yield invalid_dependency_value()


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI(exception_handlers={Exception: server_error_handler})

    @app.get("/service-fault")
    def service_fault() -> None:
        raise RuntimeError("synthetic service failure")

    @app.get("/dependency-fault", dependencies=[Depends(failing_yield_dependency)])
    def dependency_fault() -> dict[str, Any]:
        return {"ok": True}

    return app
