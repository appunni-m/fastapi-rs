"""Independent ASGI apps exercising installed optional JSON response serializers."""

from typing import Any

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, UJSONResponse


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/orjson", response_class=ORJSONResponse)
    async def orjson_response():
        return {1: "one", "message": "snow 雪"}

    @app.get("/ujson", response_class=UJSONResponse)
    async def ujson_response():
        return {"message": "snow 雪"}

    return app
