"""Independent HTTP and WebSocket exception stimuli for the public error surface."""

from collections.abc import Mapping
from inspect import signature
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketException
from fastapi import WebSocketDisconnect as FastAPIWebSocketDisconnect
from fastapi.exceptions import HTTPException as FastAPIExceptionsHTTPException
from fastapi.websockets import WebSocketDisconnect as FastAPIWebsocketsWebSocketDisconnect
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)
from starlette.exceptions import (
    WebSocketException as StarletteWebSocketException,
)
from starlette.websockets import WebSocketDisconnect as StarletteWebSocketDisconnect


def _exception_snapshot(exception: Exception) -> dict[str, object]:
    exception_type = type(exception)
    return {
        "class_module": exception_type.__module__,
        "class_qualname": exception_type.__qualname__,
        "mro": [
            f"{class_type.__module__}.{class_type.__qualname__}"
            for class_type in exception_type.__mro__
        ],
        "args": list(exception.args),
        "message": str(exception),
    }


def _websocket_exception_value_snapshot(
    exception: WebSocketException,
) -> dict[str, object]:
    return {
        **_exception_snapshot(exception),
        "representation": repr(exception),
        "code": exception.code,
        "reason": exception.reason,
    }


class _FalseyReason(str):
    def __bool__(self) -> bool:
        return False


class _RaisingReason(str):
    def __bool__(self) -> bool:
        raise ValueError("reason truthiness failed")


class _FalseyDetail(str):
    def __bool__(self) -> bool:
        return False


def _http_exception_arguments(
    call: Mapping[str, Any],
) -> tuple[tuple[object, ...], dict[str, object]]:
    args = tuple(call.get("args", []))
    kwargs = dict(call.get("kwargs", {}))
    if call.get("detail_behavior") == "falsey-str":
        kwargs["detail"] = _FalseyDetail("falsey-detail")
    return args, kwargs


def _http_exception_snapshot(call: Mapping[str, Any]) -> dict[str, object]:
    args, kwargs = _http_exception_arguments(call)
    exception_class: type[HTTPException] = HTTPException
    if call.get("exception_subclass"):
        class DerivedHTTPException(HTTPException):
            pass

        exception_class = DerivedHTTPException
    try:
        exception = exception_class(*args, **kwargs)
    except Exception as error:
        error_type = type(error)
        return {
            "label": call["label"],
            "outcome": "error",
            "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
            "exception_message": str(error),
            "exception_args": list(error.args),
        }

    for name, value in call.get("mutations", {}).items():
        setattr(exception, name, value)

    exception_type = type(exception)
    return {
        "label": call["label"],
        "outcome": "returned",
        "class_module": exception_type.__module__,
        "class_qualname": exception_type.__qualname__,
        "mro": [
            f"{class_type.__module__}.{class_type.__qualname__}"
            for class_type in exception_type.__mro__
        ],
        "args": list(exception.args),
        "args_types": [type(value).__name__ for value in exception.args],
        "attributes": vars(exception),
        "message": str(exception),
        "repr": repr(exception),
        "status_code": exception.status_code,
        "detail": exception.detail,
        "headers": exception.headers,
        "is_starlette_subclass": isinstance(exception, StarletteHTTPException),
    }


def _http_exception_init_method_snapshot(call: Mapping[str, Any]) -> dict[str, object]:
    exception = HTTPException(
        *call.get("initial_args", []),
        **call.get("initial_kwargs", {}),
    )
    args = tuple(call.get("args", []))
    kwargs = dict(call.get("kwargs", {}))
    try:
        FastAPIExceptionsHTTPException.__init__(exception, *args, **kwargs)
    except Exception as error:
        error_type = type(error)
        return {
            "label": call["label"],
            "outcome": "error",
            "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
            "exception_message": str(error),
            "exception_args": list(error.args),
            "status_code": exception.status_code,
            "detail": exception.detail,
            "headers": exception.headers,
        }

    return {
        "label": call["label"],
        "outcome": "returned",
        "args": list(exception.args),
        "status_code": exception.status_code,
        "detail": exception.detail,
        "headers": exception.headers,
        "message": str(exception),
        "repr": repr(exception),
    }


def _websocket_disconnect_arguments(
    call: Mapping[str, Any],
) -> tuple[tuple[object, ...], dict[str, object]]:
    args = tuple(call.get("args", []))
    kwargs = dict(call.get("kwargs", {}))
    reason_behavior = call.get("reason_behavior")
    if reason_behavior == "falsey-str":
        reason: str = _FalseyReason("falsey")
    elif reason_behavior == "raising-str":
        reason = _RaisingReason("raising")
    else:
        return args, kwargs

    if call.get("reason_position") == "positional":
        return (*args, reason), kwargs
    kwargs["reason"] = reason
    return args, kwargs


def _websocket_disconnect_snapshot(call: Mapping[str, Any]) -> dict[str, object]:
    args, kwargs = _websocket_disconnect_arguments(call)
    try:
        exception = FastAPIWebSocketDisconnect(*args, **kwargs)
    except Exception as error:
        error_type = type(error)
        return {
            "label": call["label"],
            "outcome": "error",
            "exception_class": f"{error_type.__module__}.{error_type.__qualname__}",
            "exception_message": str(error),
            "exception_args": list(error.args),
        }

    for name, value in call.get("mutations", {}).items():
        setattr(exception, name, value)

    exception_type = type(exception)
    return {
        "label": call["label"],
        "outcome": "returned",
        "class_module": exception_type.__module__,
        "class_qualname": exception_type.__qualname__,
        "mro": [
            f"{class_type.__module__}.{class_type.__qualname__}"
            for class_type in exception_type.__mro__
        ],
        "args": list(exception.args),
        "args_types": [type(value).__name__ for value in exception.args],
        "attributes": vars(exception),
        "message": str(exception),
        "repr": repr(exception),
        "code": exception.code,
        "reason": exception.reason,
    }


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()

    @app.get("/errors/fastapi")
    async def fastapi_http_error() -> None:
        raise HTTPException(
            status_code=418,
            detail={
                "kind": "invalid_request",
                "field": "display_name",
                "problems": ["empty", "too_short"],
            },
            headers={"X-Failure-Origin": "fastapi"},
        )

    @app.get("/errors/starlette")
    async def starlette_http_error() -> None:
        raise StarletteHTTPException(
            status_code=451,
            detail="This resource is restricted.",
            headers={"X-Failure-Origin": "starlette"},
        )

    @app.get("/errors/starlette-subclass")
    async def starlette_http_exception_subclass() -> None:
        values = factory_input["starlette_http_exception_subclass"]

        class DerivedStarletteHTTPException(StarletteHTTPException):
            pass

        raise DerivedStarletteHTTPException(
            status_code=values["status_code"],
            detail=values["detail"],
            headers=values["headers"],
        )

    @app.get("/errors/bodyless")
    async def bodyless_http_error() -> None:
        raise HTTPException(
            status_code=204,
            detail="This detail should not produce a body.",
            headers={"X-Failure-Origin": "bodyless"},
        )

    @app.get("/errors/informational")
    async def informational_http_error() -> None:
        raise HTTPException(
            status_code=199,
            detail="Informational responses do not carry a body.",
            headers={"X-Failure-Origin": "informational"},
        )

    @app.get("/errors/reset-content")
    async def reset_content_http_error() -> None:
        raise HTTPException(
            status_code=205,
            detail="Reset-content responses do not carry a body.",
            headers={"X-Failure-Origin": "reset-content"},
        )

    @app.get("/errors/not-modified")
    async def not_modified_http_error() -> None:
        raise HTTPException(
            status_code=304,
            detail="Not-modified responses do not carry a body.",
            headers={"X-Failure-Origin": "not-modified"},
        )

    @app.get("/errors/numeric-string-status")
    async def numeric_string_status_error() -> None:
        raise HTTPException(
            status_code="204",
            detail="Status values are not normalized by the exception constructor.",
        )

    @app.get("/errors/http-constructor-state")
    async def http_exception_constructor_state() -> dict[str, object]:
        exception = HTTPException(
            status_code=422,
            detail={"field": "display_name", "problems": ["empty", "too_short"]},
            headers={"X-Exception-Owner": "fastapi"},
        )
        return {
            **_exception_snapshot(exception),
            "is_starlette_http_exception": isinstance(exception, StarletteHTTPException),
            "status_code": exception.status_code,
            "detail": exception.detail,
            "headers": exception.headers,
        }

    @app.get("/errors/http-default-constructor-state")
    async def http_exception_default_constructor_state() -> dict[str, object]:
        exception = HTTPException(status_code=418)
        return {
            **_exception_snapshot(exception),
            "is_starlette_http_exception": isinstance(exception, StarletteHTTPException),
            "status_code": exception.status_code,
            "detail": exception.detail,
            "headers": exception.headers,
        }

    @app.get("/errors/http-exception-constructor-contract")
    async def http_exception_constructor_contract() -> dict[str, object]:
        return {
            "identity": {
                "root_to_module": HTTPException is FastAPIExceptionsHTTPException,
                "subclass_of_starlette": issubclass(HTTPException, StarletteHTTPException),
                "same_as_starlette": HTTPException is StarletteHTTPException,
            },
            "signature": str(signature(HTTPException)),
            "class_metadata": {
                "module": HTTPException.__module__,
                "name": HTTPException.__name__,
                "qualname": HTTPException.__qualname__,
                "doc": HTTPException.__doc__,
            },
            "calls": [
                _http_exception_snapshot(call)
                for call in factory_input.get("http_exception_calls", [])
            ],
            "init_method_calls": [
                _http_exception_init_method_snapshot(call)
                for call in factory_input.get("http_exception_init_calls", [])
            ],
        }

    @app.get("/errors/websocket-constructor-state")
    async def websocket_exception_constructor_state() -> dict[str, object]:
        exception = WebSocketException(code=1008, reason="credentials required")
        return {
            **_exception_snapshot(exception),
            "is_starlette_websocket_exception": isinstance(exception, StarletteWebSocketException),
            "class_metadata": {
                "module": WebSocketException.__module__,
                "name": WebSocketException.__name__,
                "qualname": WebSocketException.__qualname__,
                "doc": WebSocketException.__doc__,
            },
            "code": exception.code,
            "reason": exception.reason,
        }

    @app.get("/errors/websocket-value-formatting")
    async def websocket_exception_value_formatting() -> dict[str, object]:
        values = factory_input["websocket_exception_value_formatting"]
        omitted_reason = WebSocketException(code=values["omitted_code"])
        falsey_reason = WebSocketException(
            code=values["falsey_code"], reason=_FalseyReason(values["falsey_reason"])
        )
        explicit = WebSocketException(
            code=values["explicit_code"], reason=values["explicit_reason"]
        )
        explicit_before = _websocket_exception_value_snapshot(explicit)
        explicit.code = values["mutated_code"]
        explicit.reason = values["mutated_reason"]
        explicit_after = _websocket_exception_value_snapshot(explicit)

        class DerivedWebSocketException(WebSocketException):
            pass

        derived = DerivedWebSocketException(
            code=values["derived_code"], reason=values["derived_reason"]
        )
        derived_before = _websocket_exception_value_snapshot(derived)
        derived.code = values["derived_mutated_code"]
        derived.reason = values["derived_mutated_reason"]
        derived_after = _websocket_exception_value_snapshot(derived)
        return {
            "omitted_reason": _websocket_exception_value_snapshot(omitted_reason),
            "falsey_reason": _websocket_exception_value_snapshot(falsey_reason),
            "explicit_before_mutation": explicit_before,
            "explicit_after_mutation": explicit_after,
            "derived_before_mutation": derived_before,
            "derived_after_mutation": derived_after,
        }

    @app.get("/errors/websocket-disconnect-constructor-state")
    async def websocket_disconnect_constructor_state() -> dict[str, object]:
        return {
            "identity": {
                "root_to_module": (
                    FastAPIWebSocketDisconnect is FastAPIWebsocketsWebSocketDisconnect
                ),
                "root_to_starlette": (FastAPIWebSocketDisconnect is StarletteWebSocketDisconnect),
                "module_to_starlette": (
                    FastAPIWebsocketsWebSocketDisconnect is StarletteWebSocketDisconnect
                ),
            },
            "signature": str(signature(FastAPIWebSocketDisconnect)),
            "calls": [
                _websocket_disconnect_snapshot(call)
                for call in factory_input.get("websocket_disconnect_calls", [])
            ],
        }

    @app.websocket("/errors/websocket")
    async def websocket_policy_error(websocket: WebSocket) -> None:
        del websocket
        raise WebSocketException(code=1008, reason="credentials required")

    @app.websocket("/errors/websocket-default-reason")
    async def websocket_default_reason_error(websocket: WebSocket) -> None:
        del websocket
        raise WebSocketException(code=1008)

    return app
