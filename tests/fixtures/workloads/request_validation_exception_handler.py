"""Independent request-validation exception-handler stimuli."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Form, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Payload(BaseModel):
    count: int


class ValidationMode(Enum):
    STRICT = "strict"


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
            endpoint = {
                "function": exception.endpoint_function,
                "path": exception.endpoint_path,
            }
            if factory_input.get("observe_full_endpoint_context", False):
                endpoint.update(
                    {
                        "file": exception.endpoint_file,
                        "line": exception.endpoint_line,
                        "context": exception.endpoint_ctx,
                    }
                )
            return JSONResponse(
                {
                    "errors": exception.errors(),
                    "body": body,
                    "endpoint": endpoint,
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

    @app.get("/validation-manual-structured")
    def raise_structured_validation_error():
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("body", "payload", "amount"),
                    "msg": "Invalid amount",
                    "input": {
                        "amount": Decimal("12.50"),
                        "observed_at": datetime(2025, 1, 2, 3, 4, 5),
                        "request_id": UUID("12345678-1234-5678-1234-567812345678"),
                        "mode": ValidationMode.STRICT,
                    },
                    "ctx": {"error": ValueError("invalid amount")},
                }
            ]
        )

    if "manual_validation_error" in factory_input:

        @app.get("/validation-manual-context")
        def raise_manual_context_validation_error():
            raise RequestValidationError(**factory_input["manual_validation_error"])

    return app
