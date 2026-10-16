"""Observe the public FastAPI title field and its generated OpenAPI use."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

_MISSING = object()


def create_app(factory_input: dict[str, Any], _workload_trace: list[str]) -> FastAPI:
    options = dict(factory_input)
    mutated_title = options.pop("_mutated_title", _MISSING)
    prime_openapi_cache = options.pop("_prime_openapi_cache", False)
    app = FastAPI(**options)

    @app.get("/_observe/title")
    def observe_title() -> dict[str, str]:
        return {"title": app.title, "openapi_title": app.openapi()["info"]["title"]}

    if prime_openapi_cache:
        app.openapi()
    if mutated_title is not _MISSING:
        app.title = mutated_title

    return app
