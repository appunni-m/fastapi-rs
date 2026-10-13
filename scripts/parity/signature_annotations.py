"""Lossless observations of the pinned public signature annotation domain.

Observe type structure and known metadata fields directly. Object repr strings
are unsuitable evidence: their addresses vary and FieldInfo repr omits state.
Unknown annotation metadata is an infrastructure error, never an ignored value.
"""

from __future__ import annotations

import importlib
import inspect
import typing
from collections.abc import Callable
from typing import Any


class SignatureAnnotationError(ValueError):
    """An annotation cannot be represented by the reviewed fixed interface."""


FIELD_INFO_ATTRIBUTES = (
    "annotation",
    "default",
    "default_factory",
    "alias",
    "alias_priority",
    "validation_alias",
    "serialization_alias",
    "title",
    "field_title_generator",
    "description",
    "examples",
    "exclude",
    "exclude_if",
    "discriminator",
    "deprecated",
    "json_schema_extra",
    "frozen",
    "validate_default",
    "repr",
    "init",
    "init_var",
    "kw_only",
)
FASTAPI_FIELD_ATTRIBUTES = (
    "embed",
    "media_type",
    "example",
    "include_in_schema",
    "openapi_examples",
    "in_",
    "convert_underscores",
)
CONSTRAINT_FIELDS = {
    "annotated_types.Gt": ("gt",),
    "annotated_types.Ge": ("ge",),
    "pydantic._internal._fields._general_metadata_cls.<locals>._PydanticGeneralMetadata": (
        "pattern",
    ),
}
TYPING_FORMS = (
    "Any",
    "Union",
    "Literal",
    "Annotated",
    "Optional",
    "ClassVar",
    "Final",
    "NoReturn",
    "Never",
    "Self",
    "LiteralString",
    "TypeGuard",
    "Unpack",
    "Concatenate",
    "Required",
    "NotRequired",
)
FASTAPI_FIELD_INFO_TYPES = frozenset(
    {
        "fastapi.params.Param",
        "fastapi.params.Path",
        "fastapi.params.Query",
        "fastapi.params.Header",
        "fastapi.params.Cookie",
        "fastapi.params.Body",
        "fastapi.params.Form",
        "fastapi.params.File",
    }
)


def _typing_form(value: Any) -> str | None:
    for name in TYPING_FORMS:
        if value is getattr(typing, name, None):
            return f"typing.{name}"
    return None


def _type_name(value: Any) -> str:
    cls = type(value)
    return f"{cls.__module__}.{cls.__qualname__}"


def _alias_name(value: Any) -> str | None:
    name = getattr(value, "_name", None)
    if name is not None and type(name) is not str:
        raise SignatureAnnotationError("generic alias has an unreviewed alias name")
    return name


def _symbol(value: Any) -> str:
    form = _typing_form(value)
    if form is not None:
        return form
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None)
    if inspect.isclass(value) and isinstance(module, str) and isinstance(name, str):
        return f"{module}.{name}"
    raise SignatureAnnotationError(f"unsupported annotation type symbol: {_type_name(value)}")


def project_annotation(value: Any, project_value: Callable[[Any], Any]) -> dict[str, Any]:
    """Preserve ordered type arguments, literal types, and reviewed metadata."""
    return _annotation(value, project_value, depth=0)


def _annotation(value: Any, project_value: Callable[[Any], Any], *, depth: int) -> dict[str, Any]:
    if depth > 64:
        raise SignatureAnnotationError("signature annotation exceeded its nesting limit")
    if value is inspect.Signature.empty:
        return {"kind": "empty"}
    if value is Ellipsis:
        return {"kind": "ellipsis"}
    if type(value) is typing.ForwardRef:
        return {
            "kind": "forward_ref",
            "python_type": _type_name(value),
            "argument": value.__forward_arg__,
            "module": value.__forward_module__,
            "is_argument": value.__forward_is_argument__,
            "is_class": value.__forward_is_class__,
        }
    if type(value) is typing.TypeVar:
        return {
            "kind": "type_variable",
            "python_type": _type_name(value),
            "name": value.__name__,
            "module": value.__module__,
            "bound": _annotation(value.__bound__, project_value, depth=depth + 1),
            "constraints": [
                _annotation(item, project_value, depth=depth + 1) for item in value.__constraints__
            ],
            "covariant": value.__covariant__,
            "contravariant": value.__contravariant__,
            "infer_variance": getattr(value, "__infer_variance__", None),
        }
    origin = typing.get_origin(value)
    if origin is typing.Annotated:
        base, *metadata = typing.get_args(value)
        return {
            "kind": "annotated",
            "python_type": _type_name(value),
            "alias_name": _alias_name(value),
            "base": _annotation(base, project_value, depth=depth + 1),
            "metadata": [_metadata(item, project_value, depth=depth + 1) for item in metadata],
        }
    if origin is not None:
        return {
            "kind": "generic",
            "python_type": _type_name(value),
            "alias_name": _alias_name(value),
            "origin": _symbol(origin),
            "arguments": [
                _annotation(item, project_value, depth=depth + 1) for item in typing.get_args(value)
            ],
        }
    if type(value) in {list, tuple}:
        return {
            "kind": "annotation_sequence",
            "python_type": _type_name(value),
            "items": [_annotation(item, project_value, depth=depth + 1) for item in value],
        }
    if value is None or type(value) in {bool, int, float, str}:
        return {"kind": "literal", "python_type": _type_name(value), "value": project_value(value)}
    form = _typing_form(value)
    if form is not None:
        return {"kind": "typing_form", "python_type": _type_name(value), "qualified_name": form}
    if inspect.isclass(value):
        return {"kind": "type", "python_type": _type_name(value), "qualified_name": _symbol(value)}
    return {"kind": "type", "qualified_name": _symbol(value)}


def _metadata(value: Any, project_value: Callable[[Any], Any], *, depth: int) -> dict[str, Any]:
    if depth > 64:
        raise SignatureAnnotationError("signature metadata exceeded its nesting limit")
    doc_type = getattr(importlib.import_module("annotated_doc"), "Doc", None)
    if doc_type is not None and type(value) is doc_type:
        name = _type_name(value)
        if set(vars(value)) != {"documentation"} or type(value.documentation) is not str:
            raise SignatureAnnotationError("Doc annotation has unreviewed fields or values")
        return {"kind": "doc", "qualified_name": name, "documentation": value.documentation}
    deprecated_type = getattr(importlib.import_module("typing_extensions"), "deprecated", None)
    if deprecated_type is not None and type(value) is deprecated_type:
        name = _type_name(value)
        if (
            set(vars(value)) != {"message", "category", "stacklevel"}
            or type(value.message) is not str
            or type(value.stacklevel) is not int
        ):
            raise SignatureAnnotationError("deprecated annotation has unreviewed fields or values")
        return {
            "kind": "deprecated",
            "qualified_name": name,
            "message": value.message,
            "category": _annotation(value.category, project_value, depth=depth + 1),
            "stacklevel": value.stacklevel,
        }
    name = _type_name(value)
    fields = CONSTRAINT_FIELDS.get(name)
    if fields is not None:
        _require_reviewed_constraint_type(value, name)
        if hasattr(value, "__dict__") and set(vars(value)) != set(fields):
            raise SignatureAnnotationError(f"constraint annotation has unreviewed fields: {name}")
        slots = type(value).__dict__.get("__slots__")
        if slots is not None:
            if isinstance(slots, str):
                slots = (slots,)
            if set(slots) != set(fields):
                raise SignatureAnnotationError(
                    f"constraint annotation has unreviewed slots: {name}"
                )
        return {
            "kind": "constraint",
            "qualified_name": name,
            "fields": {
                field: _field_value(getattr(value, field), project_value) for field in fields
            },
        }
    # Pydantic's public FieldInfo config and the FastAPI subclass attributes
    # affect validation and OpenAPI even when absent from the object's repr.
    from pydantic.fields import FieldInfo

    if isinstance(value, FieldInfo):
        _require_reviewed_field_info_type(value, FieldInfo)
        extra = vars(value) if hasattr(value, "__dict__") else {}
        unknown = set(extra) - set(FASTAPI_FIELD_ATTRIBUTES)
        if unknown:
            raise SignatureAnnotationError(
                f"FieldInfo annotation has unreviewed attributes: {name}"
            )
        observed_fields = {
            field: (
                _annotation(value.annotation, project_value, depth=depth + 1)
                if field == "annotation"
                else _field_value(getattr(value, field), project_value)
            )
            for field in FIELD_INFO_ATTRIBUTES
        }
        observed_fields.update(
            {
                field: _field_value(extra[field], project_value)
                for field in FASTAPI_FIELD_ATTRIBUTES
                if field in extra
            }
        )
        attributes_set = value._attributes_set
        if type(attributes_set) is not dict or any(
            type(field) is not str or field not in FIELD_INFO_ATTRIBUTES for field in attributes_set
        ):
            raise SignatureAnnotationError("FieldInfo has unreviewed explicitly set attributes")
        return {
            "kind": "field_info",
            "qualified_name": name,
            "attributes": observed_fields,
            "attributes_set": {
                field: _field_value(attributes_set[field], project_value)
                for field in sorted(attributes_set)
            },
            "metadata": [
                _metadata(item, project_value, depth=depth + 1) for item in value.metadata
            ],
        }
    if value is None or type(value) in {bool, int, float, str}:
        return _field_value(value, project_value)
    raise SignatureAnnotationError(f"unsupported signature annotation metadata: {name}")


def _require_reviewed_constraint_type(value: Any, name: str) -> None:
    """Reject similarly named user classes and subclasses with extra state."""
    if name in {"annotated_types.Gt", "annotated_types.Ge"}:
        module = importlib.import_module("annotated_types")
        expected = getattr(module, name.rsplit(".", maxsplit=1)[1], None)
    else:
        from pydantic import Field

        metadata = Field(pattern="x").metadata
        expected = next((type(item) for item in metadata if _type_name(item) == name), None)
    if type(value) is not expected:
        raise SignatureAnnotationError(f"unreviewed constraint annotation type: {name}")


def _require_reviewed_field_info_type(value: Any, field_info_type: type[Any]) -> None:
    """Allow only the pinned FieldInfo classes whose public slots are mapped."""
    name = _type_name(value)
    value_type = type(value)
    if value_type is field_info_type:
        return
    if name not in FASTAPI_FIELD_INFO_TYPES:
        raise SignatureAnnotationError(f"unreviewed FieldInfo annotation type: {name}")
    module = importlib.import_module("fastapi.params")
    expected = getattr(module, name.rsplit(".", maxsplit=1)[1], None)
    if value_type is not expected:
        raise SignatureAnnotationError(f"unreviewed FieldInfo annotation type: {name}")

    allowed_slots = set(FIELD_INFO_ATTRIBUTES) | set(FASTAPI_FIELD_ATTRIBUTES) | {"metadata"}
    for cls in value_type.__mro__:
        slots = cls.__dict__.get("__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        unknown = {slot for slot in slots if not slot.startswith("_")} - allowed_slots
        if unknown:
            raise SignatureAnnotationError(
                f"FieldInfo annotation has unreviewed public slots: {name}"
            )


def _field_value(value: Any, project_value: Callable[[Any], Any]) -> dict[str, Any]:
    return {"kind": "value", "python_type": _type_name(value), "value": project_value(value)}
