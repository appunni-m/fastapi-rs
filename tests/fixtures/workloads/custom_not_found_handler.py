"""Independent HTTP workflow for configured handlers on a missing route."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    app = FastAPI()

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            {"handled": True, "path": request.url.path},
            status_code=exc.status_code,
            headers={"x-route-miss-handler": "fastapi-starlette-exception"},
        )

    @app.get("/registered")
    async def registered_route() -> dict[str, bool]:
        return {"registered": True}

    return app
