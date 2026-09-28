"""Independent workload for FastAPI 0.141.1 custom-response tutorial 001.

The upstream test filters ``FastAPIDeprecationWarning``. ASGI workflow v2 has
no warning action or selector, so this input covers the HTTP and OpenAPI
observations only.
"""

from fastapi import FastAPI
from fastapi.responses import UJSONResponse


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/items/", response_class=UJSONResponse)
    async def read_items():
        return [{"item_id": "Foo"}]

    return app
