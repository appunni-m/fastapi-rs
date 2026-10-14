"""Independent workload for FastAPI 0.141.1 custom-response tutorial 001.

The core oracle profile captures the runtime deprecation warning and the
missing-``ujson`` assertion. Successful optional-``ujson`` serialization is a
separate profile and remains outside this input.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.responses import UJSONResponse


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/items/", response_class=UJSONResponse)
    async def read_items():
        return [{"item_id": "Foo"}]

    return app
