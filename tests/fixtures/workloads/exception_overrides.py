"""Independently authored override behavior for FastAPI's default handlers."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    app = FastAPI(title="Order Error Overrides", version="1.0.0")

    @app.exception_handler(RequestValidationError)
    async def handle_invalid_request(
        request: Request, exc: RequestValidationError
    ) -> PlainTextResponse:
        return PlainTextResponse(
            status_code=400,
            content=f"Request rejected with {len(exc.errors())} invalid field(s).",
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> PlainTextResponse:
        return PlainTextResponse(
            status_code=exc.status_code,
            content=f"Order error: {exc.detail}",
        )

    @app.get("/orders/{order_id}")
    async def read_order(order_id: int) -> dict[str, int]:
        if order_id == 3:
            raise HTTPException(status_code=418, detail="Order is temporarily locked.")
        return {"order_id": order_id}

    return app
