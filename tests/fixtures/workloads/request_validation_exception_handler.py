"""Independent request-validation exception-handler stimuli."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Payload(BaseModel):
    count: int


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()

    @app.exception_handler(Exception)
    async def server_error_handler(_request: Request, _exception: Exception):
        return JSONResponse({"exception": "server-error"}, status_code=500)

    if factory_input.get("custom_validation_handler", False):

        @app.exception_handler(RequestValidationError)
        async def request_validation_handler(_request: Request, exception: RequestValidationError):
            body = exception.body
            if hasattr(body, "multi_items"):
                body = body.multi_items()
            return JSONResponse(
                {
                    "errors": exception.errors(),
                    "body": body,
                    "endpoint": {
                        "function": exception.endpoint_function,
                        "path": exception.endpoint_path,
                    },
                },
                status_code=422,
            )

    @app.get("/validation/{number}")
    def validate_path(number: int):
        return {"number": number}

    @app.post("/validation-body/{number}")
    def validate_body(number: int, payload: Payload):
        return {"number": number, "payload": payload}

    @app.post("/validation-form")
    def validate_form(count: int = Form()):
        return {"count": count}

    return app
