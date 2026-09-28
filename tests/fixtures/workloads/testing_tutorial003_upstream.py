"""ASGI lifecycle workload for the deprecated startup-event tutorial.

The upstream example registers startup only. The workflow observes the ASGI
shutdown handshake after its request, without adding an application shutdown
callback. The source test also asserts an import-time DeprecationWarning; the
v3 workflow has no warning selector, so that assertion remains unmaterialized.
"""

from __future__ import annotations

from fastapi import FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    """Build the tutorial app and record its startup callback invocation."""
    del factory_input
    app = FastAPI()
    items: dict[str, dict[str, str]] = {}

    @app.on_event("startup")
    async def startup_event() -> None:
        items.update({"foo": {"name": "Fighters"}, "bar": {"name": "Tenders"}})
        event_trace.append("items-loaded")

    @app.get("/items/{item_id}")
    async def read_items(item_id: str) -> dict[str, str]:
        return items[item_id]

    return app
