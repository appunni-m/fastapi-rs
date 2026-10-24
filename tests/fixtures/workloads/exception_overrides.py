"""Independently authored override behavior for FastAPI's default handlers."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    app = FastAPI(title="Order Error Overrides", version="1.0.0")

    class DerivedOrderException(StarletteHTTPException):
        pass

    class DerivedFirstOrderException(DerivedOrderException, LookupError):
        pass

    class LookupFirstOrderException(LookupError, DerivedOrderException):
        def __init__(
            self,
            *,
            status_code: int,
            detail: str,
            headers: dict[str, str] | None = None,
        ) -> None:
            DerivedOrderException.__init__(
                self, status_code=status_code, detail=detail, headers=headers
            )

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

    async def handle_derived_http_exception(
        request: Request, exc: DerivedOrderException
    ) -> JSONResponse:
        del request
        return JSONResponse(
            content={"handler": "derived", "detail": exc.detail},
            status_code=exc.status_code,
            headers=exc.headers,
        )

    app.add_exception_handler(DerivedOrderException, handle_derived_http_exception)

    async def handle_lookup_error(request: Request, exc: LookupError) -> JSONResponse:
        del request, exc
        return JSONResponse(
            content={"handler": "lookup", "detail": "LookupError handler selected."},
            status_code=409,
            headers={"X-Failure-Origin": "lookup-order"},
        )

    app.add_exception_handler(LookupError, handle_lookup_error)

    @app.get("/orders/{order_id}")
    async def read_order(order_id: int) -> dict[str, int]:
        if order_id == 3:
            raise HTTPException(status_code=418, detail="Order is temporarily locked.")
        return {"order_id": order_id}

    @app.get("/error-cases/derived")
    async def read_derived_order() -> None:
        raise DerivedOrderException(
            status_code=409,
            detail="Derived order handler must take precedence.",
            headers={"X-Failure-Origin": "derived-order"},
        )

    @app.get("/error-cases/mixed-derived-first")
    async def read_mixed_derived_first() -> None:
        raise DerivedFirstOrderException(
            status_code=409,
            detail="DerivedOrderException appears first in the MRO.",
            headers={"X-Failure-Origin": "derived-first"},
        )

    @app.get("/error-cases/mixed-lookup-first")
    async def read_mixed_lookup_first() -> None:
        raise LookupFirstOrderException(
            status_code=409,
            detail="LookupError appears first in the MRO.",
            headers={"X-Failure-Origin": "lookup-first"},
        )

    return app
