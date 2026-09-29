"""Independent direct-call inputs for the JSON encoder source review."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import TypedDict

from pydantic import BaseModel, Field, field_serializer
from pydantic.v1 import BaseModel as PydanticV1BaseModel
from pydantic_core import PydanticUndefined as Undefined


class Person:
    def __init__(self, handle: str):
        self.handle = handle


class Pet:
    def __init__(self, keeper: Person, label: str):
        self.keeper = keeper
        self.label = label


class DictablePerson(Person):
    def __iter__(self):
        return iter(self.__dict__.items())


class DictablePet(Pet):
    def __iter__(self):
        return iter(self.__dict__.items())


class Unserializable:
    def __iter__(self):
        raise NotImplementedError("iteration is unavailable")

    @property
    def __dict__(self):
        raise NotImplementedError("attributes are unavailable")


class ItemsOverrideDict(dict[str, object]):
    def items(self):
        return [("label", "reported")]


@dataclass
class InventoryRecord:
    label: str
    count: int


class AccessLevel(Enum):
    steward = "STEWARD"
    visitor = "VISITOR"


class ConfiguredModel(BaseModel):
    access: AccessLevel | None = None
    model_config = {"use_enum_values": True}


class AliasedModel(BaseModel):
    call_sign: str = Field(alias="CallSign")


class ModelWithDefaults(BaseModel):
    required: str
    preferred: str = "preferred"
    fallback: str = "fallback"


class CustomDateModel(BaseModel):
    moment: datetime

    @field_serializer("moment")
    def serialize_moment(self, value: datetime) -> str:
        return value.replace(microsecond=0).isoformat()


class CustomDateModelChild(CustomDateModel):
    """Subtype with inherited custom serialization for regression input."""


class SafeDateTime(datetime):
    """Datetime subtype for custom-encoder matching inputs."""


class DatePayload(TypedDict):
    moment: SafeDateTime


class PathModel(BaseModel):
    path: PurePath

    model_config = {"arbitrary_types_allowed": True}


class PosixPathModel(BaseModel):
    path: PurePosixPath

    model_config = {"arbitrary_types_allowed": True}


class WindowsPathModel(BaseModel):
    path: PureWindowsPath

    model_config = {"arbitrary_types_allowed": True}


class ChildModel(BaseModel):
    tag: str


class PydanticV1Model(PydanticV1BaseModel):
    name: str


class ObservingModelDump(BaseModel):
    label: str

    def model_dump(self, **kwargs: object) -> dict[str, object]:
        return {"keyword_names": sorted(kwargs)}


def create_argument_bundles() -> dict[str, dict[str, object]]:
    """Construct independent Python values for direct public-API probes."""
    nested = {"label": "Juniper", "keeper": {"handle": "Ari"}}
    defaults = ModelWithDefaults(required="fixed", preferred="fixed")
    custom_date: DatePayload = {"moment": SafeDateTime(2024, 2, 3, 4, 5, 6)}
    pet = Pet(keeper=Person(handle="Bela"), label="Saffron")
    dictable_pet = DictablePet(keeper=DictablePerson(handle="Cato"), label="Indigo")
    record = InventoryRecord(label="Fennel", count=23)

    class CustomStatus(Enum):
        OPEN = "OPEN"

    from pydantic.color import Color

    return {
        "dict.default": {"args": [nested], "kwargs": {}},
        "dict.include-set": {"args": [nested], "kwargs": {"include": {"label"}}},
        "dict.exclude-set": {"args": [nested], "kwargs": {"exclude": {"keeper"}}},
        "dict.empty-include": {"args": [nested], "kwargs": {"include": set()}},
        "dict.empty-exclude": {"args": [nested], "kwargs": {"exclude": set()}},
        "dict.include-list": {"args": [nested], "kwargs": {"include": ["label"]}},
        "dict.exclude-list": {"args": [nested], "kwargs": {"exclude": ["keeper"]}},
        "dict.empty-include-list": {"args": [nested], "kwargs": {"include": []}},
        "dict.empty-exclude-list": {"args": [nested], "kwargs": {"exclude": []}},
        "list.include-generator": {
            "args": [[nested]],
            "kwargs": {"include": (key for key in ("label",))},
        },
        "list.exclude-generator": {
            "args": [[nested]],
            "kwargs": {"exclude": (key for key in ("keeper",))},
        },
        "dict.sqlalchemy-safe-falsy": {
            "args": [{"_sa_state": "stored", "label": "Juniper"}],
            "kwargs": {"sqlalchemy_safe": 0},
        },
        "object.custom-class": {"args": [pet], "kwargs": {}},
        "object.custom-class-include": {"args": [pet], "kwargs": {"include": {"label"}}},
        "object.custom-class-exclude": {"args": [pet], "kwargs": {"exclude": {"keeper"}}},
        "object.custom-class-empty-include": {"args": [pet], "kwargs": {"include": set()}},
        "object.custom-class-empty-exclude": {"args": [pet], "kwargs": {"exclude": set()}},
        "object.dictable": {"args": [dictable_pet], "kwargs": {}},
        "object.dictable-include": {"args": [dictable_pet], "kwargs": {"include": {"label"}}},
        "object.dictable-exclude": {"args": [dictable_pet], "kwargs": {"exclude": {"keeper"}}},
        "object.dictable-empty-include": {"args": [dictable_pet], "kwargs": {"include": set()}},
        "object.dictable-empty-exclude": {"args": [dictable_pet], "kwargs": {"exclude": set()}},
        "dict.items-override": {
            "args": [ItemsOverrideDict(label="stored")],
            "kwargs": {},
        },
        "object.dataclass": {"args": [record], "kwargs": {}},
        "object.dataclass-include": {"args": [record], "kwargs": {"include": {"label"}}},
        "object.dataclass-exclude": {"args": [record], "kwargs": {"exclude": {"count"}}},
        "object.dataclass-empty-include": {"args": [record], "kwargs": {"include": set()}},
        "object.dataclass-empty-exclude": {"args": [record], "kwargs": {"exclude": set()}},
        "object.unsupported": {"args": [Unserializable()], "kwargs": {}},
        "model.pydantic-v1": {
            "args": [PydanticV1Model(name="Juniper")],
            "kwargs": {},
        },
        "model.dump-keyword-presence": {
            "args": [ObservingModelDump(label="Juniper")],
            "kwargs": {},
        },
        "model.custom-serializer": {
            "args": [CustomDateModel(moment=datetime(2024, 3, 4, 5, 6, 7, 123456))],
            "kwargs": {},
        },
        "model.custom-serializer-subclass": {
            "args": [CustomDateModelChild(moment=datetime(2024, 3, 4, 5, 6, 7, 123456))],
            "kwargs": {},
        },
        "model.enum-config": {"args": [ConfiguredModel(access=AccessLevel.steward)], "kwargs": {}},
        "model.alias": {"args": [AliasedModel(CallSign="North")], "kwargs": {}},
        "model.defaults": {"args": [defaults], "kwargs": {}},
        "model.include-set": {"args": [defaults], "kwargs": {"include": {"preferred"}}},
        "model.exclude-set": {"args": [defaults], "kwargs": {"exclude": {"fallback"}}},
        "model.empty-include-set": {"args": [defaults], "kwargs": {"include": set()}},
        "model.empty-exclude-set": {"args": [defaults], "kwargs": {"exclude": set()}},
        "model.exclude-unset": {"args": [defaults], "kwargs": {"exclude_unset": True}},
        "model.exclude-defaults": {"args": [defaults], "kwargs": {"exclude_defaults": True}},
        "model.combined-filter": {
            "args": [defaults],
            "kwargs": {"exclude_unset": True, "exclude_defaults": True},
        },
        "nested.model-list": {"args": [[defaults]], "kwargs": {"exclude_defaults": True}},
        "nested.model-dict": {"args": [{"entry": defaults}], "kwargs": {"exclude_defaults": True}},
        "nested.model-dict-unfiltered": {"args": [{"entry": defaults}], "kwargs": {}},
        "nested.model-dict-list": {
            "args": [{"entry": [defaults]}],
            "kwargs": {"exclude_defaults": True},
        },
        "custom-encoder.exact": {
            "args": [custom_date],
            "kwargs": {"custom_encoder": {SafeDateTime: lambda value: value.strftime("%H:%M:%S")}},
        },
        "custom-encoder.base": {
            "args": [custom_date],
            "kwargs": {"custom_encoder": {datetime: lambda value: value.strftime("%H:%M:%S")}},
        },
        "custom-encoder.default": {"args": [custom_date], "kwargs": {}},
        "enum.custom-encoder": {
            "args": [CustomStatus.OPEN],
            "kwargs": {"custom_encoder": {CustomStatus: lambda value: value.value.lower()}},
        },
        "path.model-pure": {"args": [PathModel(path=PurePath("/orchid", "seed"))], "kwargs": {}},
        "path.model-posix": {
            "args": [PosixPathModel(path=PurePosixPath("/orchid", "seed"))],
            "kwargs": {},
        },
        "path.model-windows": {
            "args": [WindowsPathModel(path=PureWindowsPath("/orchid", "seed"))],
            "kwargs": {},
        },
        "path.value": {"args": [{"location": PurePath("/orchid", "seed")}], "kwargs": {}},
        "decimal.float": {"args": [{"amount": Decimal("3.75")}], "kwargs": {}},
        "decimal.integer": {"args": [{"amount": Decimal("8")}], "kwargs": {}},
        "decimal.nan": {"args": [{"amount": Decimal("NaN")}], "kwargs": {}},
        "decimal.positive-infinity": {
            "args": [{"amount": Decimal("Infinity")}],
            "kwargs": {},
        },
        "decimal.negative-infinity": {
            "args": [{"amount": Decimal("-Infinity")}],
            "kwargs": {},
        },
        "nested.deque-models": {"args": [deque([ChildModel(tag="larch")])], "kwargs": {}},
        "undefined.value": {"args": [{"amount": Undefined}], "kwargs": {}},
        "color.core": {"args": [{"shade": Color("blue")}], "kwargs": {}},
    }
