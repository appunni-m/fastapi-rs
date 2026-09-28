"""Independent workload for inferred response-model construction errors."""

from __future__ import annotations

import operator
from collections.abc import Mapping
from functools import reduce
from typing import Any

from fastapi import FastAPI, Response

_RETURN_TYPES: dict[str, type[Any]] = {
    "response": Response,
    "dict": dict,
}


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    """Construct a route whose return annotation is defined by workflow input."""
    del event_trace
    route = factory_input["route"]
    return_types = [_RETURN_TYPES[name] for name in route["return_annotation_members"]]
    return_annotation = reduce(operator.or_, return_types)

    def endpoint() -> Any:
        return {"message": "portal"}

    endpoint.__name__ = route["endpoint_name"]
    endpoint.__qualname__ = endpoint.__name__
    endpoint.__annotations__["return"] = return_annotation

    app = FastAPI()
    register = getattr(app, route["method"])
    register(route["path"])(endpoint)
    return app
