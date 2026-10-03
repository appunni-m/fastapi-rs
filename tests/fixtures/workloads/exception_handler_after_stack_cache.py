"""Synthetic ASGI stimulus for late FastAPI exception-handler registration."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class LateRegistrationError(Exception):
    pass


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    async def late_registration_handler(_request: Request, exception: Exception) -> JSONResponse:
        event_trace.append("late-handler-called")
        return JSONResponse({"error": str(exception)}, status_code=449)

    @app.get("/arm-handler")
    async def arm_handler() -> dict[str, bool]:
        registered_handler = app.exception_handler(LateRegistrationError)(late_registration_handler)
        event_trace.append(
            "decorator-returned-original"
            if registered_handler is late_registration_handler
            else "decorator-returned-different"
        )
        return {"registered": True}

    @app.get("/raise-probe")
    async def raise_probe() -> None:
        raise LateRegistrationError("late handler registration")

    return app
