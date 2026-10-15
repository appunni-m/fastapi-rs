"""Exercise strict JSON and raw-body observations on ordinary HTTP responses."""

from typing import Any

from fastapi import FastAPI, Response


def create_app(factory_input: dict[str, Any], event_trace: list[str]) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/json")
    async def json_body() -> dict[str, Any]:
        return {"count": 3, "message": "ok"}

    @app.get("/duplicate-keys")
    async def duplicate_keys() -> Response:
        return Response(
            content=b'{"item": 1, "item": 2}',
            media_type="application/json",
        )

    @app.get("/invalid-utf8")
    async def invalid_utf8() -> Response:
        return Response(
            content=b'{"item": "\xff"}',
            media_type="application/json",
        )

    return app
