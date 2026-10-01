"""Independent ASGI stimulus for FastAPI's inherited exception-handler method."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class WidgetUnavailable(Exception):
    pass


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    registration = factory_input.get("registration", "add")
    original_request: list[Request | None] = [None]

    async def widget_exception_handler(request: Request, _exception: Exception) -> JSONResponse:
        return JSONResponse(
            {
                "error": "widget unavailable",
                "request_identity": request is original_request[0],
            },
            status_code=418,
        )

    if registration == "constructor-class":
        app = FastAPI(exception_handlers={WidgetUnavailable: widget_exception_handler})
    elif registration == "constructor-status":
        app = FastAPI(exception_handlers={418: widget_exception_handler})
    else:
        app = FastAPI()

    if registration == "decorator":
        decorated_handler = app.exception_handler(WidgetUnavailable)(widget_exception_handler)
        event_trace.append(
            "decorator-returned-original"
            if decorated_handler is widget_exception_handler
            else "decorator-returned-different"
        )
    elif registration == "status":
        app.add_exception_handler(418, widget_exception_handler)
    elif registration not in {"constructor-class", "constructor-status", "default-http"}:
        app.add_exception_handler(WidgetUnavailable, widget_exception_handler)

    @app.get("/widget")
    async def read_widget(request: Request) -> dict[str, str]:
        original_request[0] = request
        if registration in {"status", "constructor-status", "default-http"}:
            status_code = 404 if registration == "default-http" else 418
            raise HTTPException(status_code=status_code, detail="synthetic missing widget")
        raise WidgetUnavailable("synthetic missing widget")

    return app
