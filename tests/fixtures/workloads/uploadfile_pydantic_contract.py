"""Exercise UploadFile's Pydantic hooks through public validation and schema APIs."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from io import BytesIO

from fastapi import FastAPI, UploadFile
from pydantic import TypeAdapter, ValidationError
from starlette.datastructures import UploadFile as StarletteUploadFile


class _DisagreeingMeta(type):
    def __str__(cls) -> str:
        return "custom-str-type"

    def __repr__(cls) -> str:
        return "custom-repr-type"


class _FormattingMeta(_DisagreeingMeta):
    def __format__(cls, format_spec: str) -> str:
        return "custom-format-type"


class _UnexpectedValue(metaclass=_DisagreeingMeta):
    pass


class _UnexpectedFormattedValue(metaclass=_FormattingMeta):
    pass


_UNEXPECTED_VALUE = _UnexpectedValue()
_UNEXPECTED_FORMATTED_VALUE = _UnexpectedFormattedValue()
_STANDARD_INVALID_VALUES: dict[str, object] = {
    "none": None,
    "boolean": True,
    "integer": 42,
    "float": 3.5,
    "string": "not an upload",
    "bytes": b"not an upload",
    "bytearray": bytearray(b"not an upload"),
    "list": [],
    "mapping": {},
    "tuple": (),
    "set": set(),
    "frozenset": frozenset(),
    "complex": complex(1, 2),
    "object": object(),
}


def _method_introspection(method: Callable[..., object]) -> dict[str, object]:
    return {
        "annotations": {name: repr(value) for name, value in method.__annotations__.items()},
        "doc": inspect.getdoc(method),
        "is_coroutine_function": inspect.iscoroutinefunction(method),
        "module": method.__module__,
        "qualname": method.__qualname__,
    }


def create_app(_factory_input: dict[str, object], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()

    @app.get("/uploadfile-pydantic-contract/json-schema")
    async def json_schema() -> dict[str, str]:
        return TypeAdapter(UploadFile).json_schema()

    @app.get("/uploadfile-pydantic-contract/serialization-json-schema")
    async def serialization_json_schema() -> dict[str, str]:
        return TypeAdapter(UploadFile).json_schema(mode="serialization")

    @app.get("/uploadfile-pydantic-contract/class-inheritance-identity")
    async def class_inheritance_identity() -> dict[str, bool | str]:
        from fastapi.datastructures import UploadFile as CanonicalUploadFile

        return {
            "root_is_canonical": UploadFile is CanonicalUploadFile,
            "direct_base_is_starlette": CanonicalUploadFile.__base__ is StarletteUploadFile,
            "is_starlette_subclass": issubclass(CanonicalUploadFile, StarletteUploadFile),
            "module": CanonicalUploadFile.__module__,
            "qualname": CanonicalUploadFile.__qualname__,
        }

    @app.get("/uploadfile-pydantic-contract/accept-starlette-base")
    async def accept_starlette_base() -> dict[str, bool]:
        value = StarletteUploadFile(BytesIO(b"upload"), filename="upload.bin", size=6)
        result = TypeAdapter(UploadFile).validate_python(value)
        return {
            "same_object": result is value,
            "is_starlette_upload_file": isinstance(result, StarletteUploadFile),
        }

    @app.get("/uploadfile-pydantic-contract/reject-custom-type")
    async def reject_custom_type() -> dict[str, str]:
        try:
            TypeAdapter(UploadFile).validate_python(_UNEXPECTED_VALUE)
        except ValidationError as error:
            details = error.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            )
            return {"outcome": "rejected", "message": details[0]["msg"]}
        return {"outcome": "accepted"}

    @app.get("/uploadfile-pydantic-contract/reject-custom-format-type")
    async def reject_custom_format_type() -> dict[str, str]:
        try:
            TypeAdapter(UploadFile).validate_python(_UNEXPECTED_FORMATTED_VALUE)
        except ValidationError as error:
            details = error.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            )
            return {"outcome": "rejected", "message": details[0]["msg"]}
        return {"outcome": "accepted"}

    @app.post("/uploadfile-pydantic-contract/reject-standard-invalid-type")
    async def reject_standard_invalid_type(payload: dict[str, object]) -> dict[str, str]:
        value = _STANDARD_INVALID_VALUES[str(payload["kind"])]
        try:
            TypeAdapter(UploadFile).validate_python(value)
        except ValidationError as error:
            details = error.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            )
            return {"outcome": "rejected", "message": details[0]["msg"]}
        return {"outcome": "accepted"}

    @app.get("/uploadfile-pydantic-contract/introspection")
    async def introspection() -> dict[str, object]:
        return {
            "class": {
                "annotations": {
                    name: repr(value) for name, value in UploadFile.__annotations__.items()
                },
                "doc": inspect.getdoc(UploadFile),
            },
            "methods": {
                "write": _method_introspection(UploadFile.write),
                "read": _method_introspection(UploadFile.read),
                "seek": _method_introspection(UploadFile.seek),
                "close": _method_introspection(UploadFile.close),
            },
        }

    return app
