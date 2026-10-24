"""Capture FastAPI's server span for one WebSocket connection."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, WebSocket
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


class _TelemetryCaptureApp:
    def __init__(self, app: Any, exporter: InMemorySpanExporter) -> None:
        self._app = app
        self._exporter = exporter

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        await self._app(scope, receive, send)

    def get_parity_finished_spans(self) -> list[Any]:
        return self._exporter.get_finished_spans()


def create_websocket_telemetry_app(
    factory_input: dict[str, Any], event_trace: list[str]
) -> _TelemetryCaptureApp:
    """Build an isolated trace recorder and a WebSocket endpoint."""
    if factory_input or event_trace:
        raise ValueError("the WebSocket telemetry workload takes no setup input")
    exporter = InMemorySpanExporter()
    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = FastAPI(
        telemetry={
            "tracer_provider": provider,
            "tracing": True,
            "metrics": False,
            "logs": False,
            "operation_spans": False,
            "auto_configure": False,
        }
    )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.close()

    return _TelemetryCaptureApp(app, exporter)
