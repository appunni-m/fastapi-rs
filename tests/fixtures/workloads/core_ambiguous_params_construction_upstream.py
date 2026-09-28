"""Input-only route construction cases for conflicting Annotated defaults."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, Path, Query


async def _dependency() -> int:
    return 1


def create_app(factory_input: dict[str, str], event_trace: list[str]) -> FastAPI:
    del event_trace
    app = FastAPI()
    scenario = factory_input["scenario"]

    if scenario == "annotated-path-default":

        @app.get("/items/{item_id}")
        async def read_item(item_id: Annotated[int, Path(default=1)]) -> int:
            return item_id
    elif scenario == "annotated-query-default":

        @app.get("/")
        async def read_query(item_id: Annotated[int, Query(default=1)]) -> int:
            return item_id
    elif scenario == "depends-annotated-and-default":

        @app.get("/")
        async def read_dependency(
            value: Annotated[int, Depends(_dependency)] = Depends(_dependency),
        ) -> int:
            return value
    elif scenario == "field-annotated-and-depends-default":

        @app.get("/")
        async def read_field(
            value: Annotated[int, Query(min_length=1)] = Depends(_dependency),
        ) -> int:
            return value
    else:
        raise ValueError("unknown route-construction input")

    return app
