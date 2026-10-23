"""Workload for W3C traceparent extraction on one HTTP request."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


class _FalseyProvider:
    def __bool__(self) -> bool:
        return False


class _TelemetryCaptureApp:
    def __init__(self, app: Any, exporter: InMemorySpanExporter) -> None:
        self._app = app
        self._exporter = exporter

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        await self._app(scope, receive, send)

    def get_parity_finished_spans(self) -> list[Any]:
        return self._exporter.get_finished_spans()


def create_traceparent_telemetry_app(
    factory_input: dict[str, Any], event_trace: list[str]
) -> _TelemetryCaptureApp:
    """Build a late-bound global provider and a root route."""
    if factory_input or event_trace:
        raise ValueError("the traceparent workload takes no factory input or setup events")
    exporter = InMemorySpanExporter()
    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = FastAPI(
        telemetry={
            "tracer_provider": _FalseyProvider(),
            "metrics": False,
            "logs": False,
            "auto_configure": False,
        }
    )
    trace.set_tracer_provider(provider)

    @app.get("/")
    async def root() -> str:
        return "ok"

    return _TelemetryCaptureApp(app, exporter)
