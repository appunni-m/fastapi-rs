"""Independent workload for FastAPI route-construction error observations."""

from __future__ import annotations

import inspect
import operator
import warnings
from collections.abc import Mapping
from functools import reduce
from typing import Any

from fastapi import FastAPI, Query
from pydantic import BaseModel

_BUILTIN_TYPES: dict[str, type[Any]] = {
    "dict": dict,
    "list": list,
    "set": set,
    "str": str,
    "tuple": tuple,
}
_GENERIC_TYPES: dict[str, Any] = {
    "dict": dict,
    "list": list,
    "set": set,
    "tuple": tuple,
}
_FIELD_TYPES: dict[str, type[Any]] = {"int": int, "str": str}


def _make_model_type(
    name: str,
    base_name: str,
    fields: Mapping[str, str],
) -> type[Any]:
    if base_name == "pydantic-v2":
        base = BaseModel
    elif base_name == "pydantic-v1":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            from pydantic.v1 import BaseModel as PydanticV1BaseModel

        base = PydanticV1BaseModel
    else:
        raise ValueError("unsupported model base in workload input")

    annotations: dict[str, type[Any]] = {}
    for field_name, field_type in fields.items():
        annotations[field_name] = _FIELD_TYPES[field_type]
    return type(
        name,
        (base,),
        {"__annotations__": annotations, "__module__": __name__},
    )


def _build_type(specification: Mapping[str, Any]) -> Any:
    kind = specification["kind"]
    if kind == "builtin":
        return _BUILTIN_TYPES[specification["name"]]
    if kind == "class":
        return type(specification["name"], (), {"__module__": __name__})
    if kind == "model":
        return _make_model_type(
            specification["name"],
            specification["base"],
            specification.get("fields", {}),
        )
    if kind == "none":
        return type(None)
    if kind == "generic":
        origin = _GENERIC_TYPES[specification["origin"]]
        arguments = tuple(_build_type(argument) for argument in specification["arguments"])
        return origin[arguments[0] if len(arguments) == 1 else arguments]
    if kind == "union":
        members = [_build_type(member) for member in specification["members"]]
        if not members:
            raise ValueError("a union descriptor must contain at least one member")
        return reduce(operator.or_, members)
    raise ValueError("unsupported annotation descriptor in workload input")


def _make_endpoint(route: Mapping[str, Any]) -> Any:
    parameters = []
    for parameter in route.get("parameters", []):
        default_specification = parameter.get("default", {"kind": "required"})
        if default_specification["kind"] == "required":
            default = inspect.Parameter.empty
        elif default_specification["kind"] == "query-none":
            default = Query(default=None)
        else:
            raise ValueError("unsupported parameter default in workload input")

        parameters.append(
            inspect.Parameter(
                parameter["name"],
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=_build_type(parameter["annotation"]),
            )
        )

    return_annotation = inspect.Signature.empty
    if "return_annotation" in route:
        return_annotation = _build_type(route["return_annotation"])

    def endpoint(*args: Any, **kwargs: Any) -> None:
        del args, kwargs

    endpoint.__name__ = route.get("endpoint_name", "endpoint")
    endpoint.__qualname__ = endpoint.__name__
    endpoint.__module__ = __name__
    endpoint.__signature__ = inspect.Signature(
        parameters=parameters,
        return_annotation=return_annotation,
    )
    return endpoint


def _route_options(route: Mapping[str, Any]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    if "response_model" in route:
        options["response_model"] = _build_type(route["response_model"])
    elif route.get("disable_response_model", False):
        options["response_model"] = None

    if "responses" in route:
        responses: dict[int | str, dict[str, Any]] = {}
        for response in route["responses"]:
            status_code = response["status_code"]
            details = {key: value for key, value in response.items() if key != "status_code"}
            if "model" in details:
                details["model"] = _build_type(details["model"])
            responses[status_code] = details
        options["responses"] = responses
    return options


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    """Build one route from declarative, input-only Python type descriptors."""
    del event_trace
    app = FastAPI()
    route = factory_input["route"]
    endpoint = _make_endpoint(route)
    register = getattr(app, route["method"])
    register(route["path"], **_route_options(route))(endpoint)
    return app
