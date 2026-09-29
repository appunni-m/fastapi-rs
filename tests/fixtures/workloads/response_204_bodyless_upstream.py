"""FastAPI-managed 204 response workload with no unrelated optional APIs."""

from typing import Any

from fastapi import FastAPI


def create_app(
    factory_input: dict[str, Any] | None = None,
    event_trace: list[str] | None = None,
) -> FastAPI:
    del factory_input, event_trace
    app = FastAPI()

    @app.get("/empty", status_code=204)
    async def empty_response() -> None:
        return None

    return app
