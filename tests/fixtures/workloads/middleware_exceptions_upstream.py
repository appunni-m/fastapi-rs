"""Independent ASGI stimuli for middleware and exception responses."""

from __future__ import annotations

import json

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException


class HandledHTTPException(HTTPException):
    pass


class CaptureRawBodyRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def capture_raw_body(request: Request):
            raw_body = await request.body()
            request.scope.setdefault("state", {})["captured_body"] = raw_body.decode("utf-8")
            return await original(request)

        return capture_raw_body


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(GZipMiddleware, minimum_size=100)
    items = {"foo": "The Foo Wrestlers"}

    @app.exception_handler(HandledHTTPException)
    async def handled_http_exception(request: Request, exception: HandledHTTPException):
        return JSONResponse({"exception": "http-exception"})

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception(request: Request, exception: RequestValidationError):
        if request.url.path == "/custom-request":
            captured = request.scope.get("state", {}).get("captured_body")
            return JSONResponse(
                {"errors": exception.errors(), "body": json.loads(captured or "null")},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return JSONResponse({"exception": "request-validation"})

    @app.get("/handled-http")
    def handled_http():
        raise HandledHTTPException(status_code=400)

    @app.get("/request-validation/{number}")
    def request_validation(number: int):
        return {"number": number}

    @app.get("/items/{item_id}")
    async def read_item(item_id: str):
        if item_id not in items:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
                headers={"X-Error": "Item missing"},
            )
        return {"item": items[item_id]}

    @app.get("/starlette-items/{item_id}")
    async def read_starlette_item(item_id: str):
        if item_id not in items:
            raise StarletteHTTPException(status_code=404, detail="Item not found")
        return {"item": items[item_id]}

    @app.get("/no-body")
    async def no_body_exception():
        raise HTTPException(status_code=204)

    @app.get("/no-body-detail")
    async def no_body_detail_exception():
        raise HTTPException(status_code=204, detail="discarded for this status")

    @app.get("/large")
    async def large_response():
        return PlainTextResponse("z" * 4000)

    request_router = APIRouter(route_class=CaptureRawBodyRoute)

    @request_router.post("/custom-request")
    def sum_values(numbers: list[int]):
        return sum(numbers)

    app.include_router(request_router)
    return app
