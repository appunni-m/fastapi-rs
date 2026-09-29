"""Observe the public RequestValidationError object through a plain response."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ValidationException

ERRORS = [{"type": "missing", "loc": ("body", "name"), "msg": "Field required"}]


def _error_observation(
    endpoint_ctx: dict[str, object] | None,
    *,
    omit_endpoint_ctx: bool = False,
    omit_body: bool = False,
) -> dict[str, object]:
    body = {"name": None}
    kwargs: dict[str, object] = {}
    if not omit_body:
        kwargs["body"] = body
    if not omit_endpoint_ctx:
        kwargs["endpoint_ctx"] = endpoint_ctx
    error = RequestValidationError(ERRORS, **kwargs)
    return {
        "class_module": type(error).__module__,
        "class_qualname": type(error).__qualname__,
        "mro": [
            f"{class_type.__module__}.{class_type.__qualname__}"
            for class_type in type(error).__mro__
        ],
        "is_request_validation_error": isinstance(error, RequestValidationError),
        "is_validation_exception": isinstance(error, ValidationException),
        "is_exception": isinstance(error, Exception),
        "args": list(error.args),
        "errors": error.errors(),
        "errors_identity": error.errors() is ERRORS,
        "body": error.body,
        "body_is_none": error.body is None,
        "body_identity": error.body is body if not omit_body else None,
        "endpoint_ctx": error.endpoint_ctx,
        "endpoint_ctx_is_none": error.endpoint_ctx is None,
        "endpoint_ctx_identity": error.endpoint_ctx is endpoint_ctx,
        "endpoint_function": error.endpoint_function,
        "endpoint_path": error.endpoint_path,
        "endpoint_file": error.endpoint_file,
        "endpoint_line": error.endpoint_line,
        "message": str(error),
    }


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/path-context")
    def path_context() -> dict[str, object]:
        return _error_observation({"path": "GET /api/test"})

    @app.get("/empty-context")
    def empty_context() -> dict[str, object]:
        return _error_observation({})

    @app.get("/omitted-defaults")
    def omitted_defaults() -> dict[str, object]:
        return _error_observation(None, omit_endpoint_ctx=True, omit_body=True)

    return app
