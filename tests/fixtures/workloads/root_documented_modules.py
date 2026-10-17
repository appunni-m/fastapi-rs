"""Expose documented FastAPI modules and handler identities for parity."""

import importlib
import inspect

import fastapi
from fastapi import FastAPI
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_app() -> FastAPI:
    app = FastAPI()
    imported_exception_handlers = importlib.import_module("fastapi.exception_handlers")
    imported_exceptions = importlib.import_module("fastapi.exceptions")

    @app.get("/root-modules")
    def root_modules() -> dict[str, object]:
        names = (
            "datastructures",
            "encoders",
            "exception_handlers",
            "exceptions",
            "middleware",
            "openapi",
            "requests",
            "responses",
            "routing",
            "security",
            "sse",
            "websockets",
        )
        return {
            **{name: hasattr(fastapi, name) for name in names},
            "exceptions_module_identity": fastapi.exceptions is imported_exceptions,
            "exception_handlers_module_identity": (
                fastapi.exception_handlers is imported_exception_handlers
            ),
            "http_handler_default_identity": (
                app.exception_handlers[StarletteHTTPException] is http_exception_handler
            ),
            "request_validation_handler_default_identity": (
                app.exception_handlers[RequestValidationError]
                is request_validation_exception_handler
            ),
            "http_handler_async": inspect.iscoroutinefunction(http_exception_handler),
            "request_validation_handler_async": inspect.iscoroutinefunction(
                request_validation_exception_handler
            ),
            "http_handler_signature": str(inspect.signature(http_exception_handler)),
            "request_validation_handler_signature": str(
                inspect.signature(request_validation_exception_handler)
            ),
        }

    return app
