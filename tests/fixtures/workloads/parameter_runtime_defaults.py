"""Minimal request workloads for public Query, Body, Form, and File defaults.

The body, form, and file string fallbacks intentionally do not match their
annotations, showing that a missing default is returned without value validation.
"""

from __future__ import annotations

from itertools import cycle
from typing import Annotated

from fastapi import Body, FastAPI, File, Form, Query


def annotated_default() -> int:
    return 41


def create_app() -> FastAPI:
    app = FastAPI()
    none_factory_calls = [0]
    none_values = cycle((None, None, 7))
    value_factory_calls = [0]
    body_factory_calls = [0]
    form_factory_calls = [0]
    form_values = cycle((None, "form fallback"))
    file_factory_calls = [0]
    file_values = cycle((None, "file fallback"))

    def optional_default() -> int | None:
        none_factory_calls[0] += 1
        return next(none_values)

    def value_default() -> int:
        value_factory_calls[0] += 1
        return value_factory_calls[0]

    def body_default() -> str:
        body_factory_calls[0] += 1
        return "body fallback"

    def form_default() -> str | None:
        form_factory_calls[0] += 1
        return next(form_values)

    def file_default() -> str | None:
        file_factory_calls[0] += 1
        return next(file_values)

    @app.get("/query/default-factory")
    async def read_factory_default(
        q: int | None = Query(default_factory=optional_default),
    ) -> dict[str, int | None]:
        return {"q": q, "calls": none_factory_calls[0]}

    @app.get("/query/default-factory-value")
    async def read_value_default(
        q: int = Query(default_factory=value_default),
    ) -> dict[str, int]:
        return {"q": q, "calls": value_factory_calls[0]}

    @app.get("/annotated-default-factory")
    async def read_annotated_default(
        q: Annotated[int, Query(default_factory=annotated_default)],
    ) -> dict[str, int]:
        return {"q": q}

    @app.post("/body/default-factory", response_model=None)
    async def read_body_default(
        q: int = Body(default_factory=body_default),
    ) -> dict[str, object]:
        return {"value": repr(q), "calls": body_factory_calls[0]}

    @app.post("/form/default-factory", response_model=None)
    async def read_form_default(
        q: int = Form(default_factory=form_default),
    ) -> dict[str, object]:
        return {"value": repr(q), "calls": form_factory_calls[0]}

    @app.post("/file/default-factory", response_model=None)
    async def read_file_default(
        q: bytes = File(default_factory=file_default),
    ) -> dict[str, object]:
        return {"value": repr(q), "calls": file_factory_calls[0]}

    return app
