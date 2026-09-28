"""User-defined request and route extensions used as isolated parity inputs."""

from __future__ import annotations

import gzip
from collections.abc import Callable

from fastapi import APIRouter, Body, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

_NUMBERS_BODY = Body()


class DecodingRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = gzip.decompress(body)
            self._body = body
        return self._body


class DecodingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original = super().get_route_handler()

        async def handle(request: Request) -> Response:
            request = DecodingRequest(request.scope, request.receive)
            return await original(request)

        return handle


class ValidationContextRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original = super().get_route_handler()

        async def handle(request: Request) -> Response:
            try:
                return await original(request)
            except RequestValidationError as exc:
                body = await request.body()
                raise HTTPException(
                    status_code=422,
                    detail={"errors": exc.errors(), "body": body.decode()},
                ) from exc

        return handle


def create_app() -> FastAPI:
    app = FastAPI()
    decoding = APIRouter(route_class=DecodingRoute)

    @decoding.post("/decode/sum")
    async def sum_numbers(numbers: list[int] = _NUMBERS_BODY):
        return {"sum": sum(numbers)}

    @decoding.get("/decode/request-type")
    async def request_type(request: Request):
        return {"request_class": type(request).__name__}

    validation = APIRouter(route_class=ValidationContextRoute)

    @validation.post("/validation/context")
    async def sum_validated(numbers: list[int] = _NUMBERS_BODY):
        return sum(numbers)

    app.include_router(decoding)
    app.include_router(validation)
    return app
