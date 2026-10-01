"""Independent ASGI stimulus for FastAPI's inherited exception-handler method."""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class WidgetUnavailable(Exception):
    pass


async def widget_exception_handler(
    _request: Request, _exception: WidgetUnavailable
) -> JSONResponse:
    return JSONResponse({"error": "widget unavailable"}, status_code=418)


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()
    app.add_exception_handler(WidgetUnavailable, widget_exception_handler)

    @app.get("/widget")
    async def read_widget() -> dict[str, str]:
        raise WidgetUnavailable("synthetic missing widget")

    return app
