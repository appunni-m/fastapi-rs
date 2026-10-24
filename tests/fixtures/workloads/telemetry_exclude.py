"""Workload for FastAPI's request-scope telemetry exclusion callback."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
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


def create_excluded_telemetry_app(
    factory_input: dict[str, Any], event_trace: list[str]
) -> _TelemetryCaptureApp:
    """Build an isolated recorder with the excluded path supplied as input."""
    if set(factory_input) != {"excluded_path"} or event_trace:
        raise ValueError("the telemetry exclusion workload needs one path and no setup events")
    excluded_path = factory_input["excluded_path"]
    if not isinstance(excluded_path, str):
        raise TypeError("excluded_path must be a string")

    exporter = InMemorySpanExporter()
    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = FastAPI(
        telemetry={
            "tracer_provider": provider,
            "metrics": False,
            "logs": False,
            "auto_configure": False,
            "exclude": lambda scope: scope["path"] == excluded_path,
        }
    )

    @app.get(excluded_path)
    async def excluded() -> str:
        return "ok"

    return _TelemetryCaptureApp(app, exporter)
