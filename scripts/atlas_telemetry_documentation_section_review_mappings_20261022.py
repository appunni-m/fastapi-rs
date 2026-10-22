"""Reviewed OpenTelemetry documentation section mappings for FastAPI 0.157.0."""

_PAGE = "advanced/opentelemetry.md"
_CONSTRUCTOR_RECIPE = (
    "tests/fixtures/input-recipes/parity/telemetry-constructor-contract.yaml"
)
_CLI_RECIPE = "tests/fixtures/input-recipes/parity/fastapi-cli-documented-process-v2.yaml"
_CLI_GUIDE_REQUEST = "fastapi.cli.process.opentelemetry-guide-request"

_DEFAULT = "fastapi.telemetry.constructor-default"
_TRACING_DISABLED = "fastapi.telemetry.constructor-tracing-disabled"
_OPERATIONS_DISABLED = "fastapi.telemetry.constructor-operation-spans-disabled"
_SIGNALS_DISABLED = "fastapi.telemetry.constructor-signals-disabled"

DOC_SECTION_CASE_MAPPINGS_OPENTELEMETRY_20261022 = {
    (_PAGE, "opentelemetry"): {
        "heading": "OpenTelemetry { #opentelemetry }",
        "start_line": 1,
        "end_line": 158,
        "recipe_path": _CONSTRUCTOR_RECIPE,
        "case_ids": [_DEFAULT, _TRACING_DISABLED, _OPERATIONS_DISABLED, _SIGNALS_DISABLED],
        "observation_selectors": ["python.call_outcome", "python.signature"],
        "scope_note": (
            "Partial constructor contract only: the independent inputs observe default app "
            "construction and acceptance of selected telemetry configuration dictionaries, "
            "plus the FastAPI constructor signature. They do not observe HTTP or WebSocket "
            "spans, metrics, log records, context data, provider/exporter effects, or the "
            "FastAPI Cloud service."
        ),
        "rationale": (
            "FastAPI 0.157.0 introduces the telemetry constructor parameter in "
            "fastapi/applications.py and defines its TypedDict settings in "
            "fastapi/telemetry/_api.py. The pinned OpenTelemetry guide at "
            "docs/en/docs/advanced/opentelemetry.md:1-158 describes many runtime signals "
            "beyond constructor acceptance. These four independent constructor calls map "
            "only the bounded configuration surface; emitted telemetry remains an explicit "
            "unresolved contract."
        ),
    },
    (_PAGE, "create-the-app"): {
        "heading": "Create the app { #create-the-app }",
        "start_line": 28,
        "end_line": 35,
        "recipe_path": _CONSTRUCTOR_RECIPE,
        "case_ids": [_DEFAULT],
        "observation_selectors": ["python.call_outcome"],
        "scope_note": (
            "The selected case constructs a default FastAPI application. It does not send the "
            "documented request or observe the default trace, metric, or log signals."
        ),
        "rationale": (
            "The pinned page's Create the app section at "
            "docs/en/docs/advanced/opentelemetry.md:28-35 imports FastAPI and calls "
            "FastAPI() with no custom settings. The independent constructor input mirrors "
            "that call shape and observes only successful public construction."
        ),
    },
    (_PAGE, "other-monitoring-services"): {
        "status": "excluded",
        "heading": "Other monitoring services { #other-monitoring-services }",
        "start_line": 44,
        "end_line": 59,
        "exclusion_reason": (
            "This section describes environment-driven OTLP exporter configuration. Current "
            "parity observations do not capture exported telemetry or provider lifecycle, "
            "and the fixture profile does not start a collector. Keep these behaviors in "
            "the telemetry observation-contract backlog until a deterministic process and "
            "export observation is available."
        ),
        "rationale": (
            "FastAPI 0.157.0 documents FASTAPI_OTEL_AUTO_CONFIGURE and OTEL_EXPORTER_OTLP_* "
            "configuration at docs/en/docs/advanced/opentelemetry.md:44-59; "
            "fastapi/telemetry/_runtime.py implements endpoint selection and exporter "
            "registration. No current selector reports OTLP spans, metrics, logs, or "
            "shutdown effects, so this section is explicitly excluded from the present "
            "fixture denominator and remains an implementation backlog item."
        ),
    },
    (_PAGE, "run-the-app"): {
        "heading": "Run the app { #run-the-app }",
        "start_line": 60,
        "end_line": 80,
        "recipe_path": _CLI_RECIPE,
        "case_ids": [_CLI_GUIDE_REQUEST],
        "observation_selectors": [
            "process.exit_code",
            "http.status",
            "http.body.bytes",
        ],
        "scope_note": (
            "Partial CLI and HTTP mapping only: the selected process starts an app with "
            "fastapi run and observes process completion plus one HTTP response. It does "
            "not observe the trace, metrics, or exports described in the monitoring-service "
            "instructions. The current FastAPI-RS process profile has no fastapi console "
            "entrypoint, so target execution remains unresolved."
        ),
        "rationale": (
            "The pinned OpenTelemetry guide at "
            "docs/en/docs/advanced/opentelemetry.md:60-80 documents fastapi run and a GET "
            "request. The existing input-only FastAPI CLI workflow independently starts "
            "FastAPI with fastapi run and sends one request; its process and HTTP selectors "
            "do not claim telemetry-export parity."
        ),
    },
    (_PAGE, "customize-telemetry"): {
        "heading": "Customize telemetry { #customize-telemetry }",
        "start_line": 81,
        "end_line": 131,
        "recipe_path": _CONSTRUCTOR_RECIPE,
        "case_ids": [_TRACING_DISABLED, _OPERATIONS_DISABLED, _SIGNALS_DISABLED],
        "observation_selectors": ["python.call_outcome", "python.signature"],
        "scope_note": (
            "Partial constructor mapping: inputs cover tracing=False, operation_spans=False, "
            "and all signal flags disabled. They do not inspect supplied providers, custom "
            "exporters, spans, logs, metrics, or provider shutdown."
        ),
        "rationale": (
            "FastAPI 0.157.0 defines tracing, metrics, logs, operation_spans, provider, and "
            "auto_configure fields in fastapi/telemetry/_api.py; the pinned guide describes "
            "their settings at docs/en/docs/advanced/opentelemetry.md:81-131. The linked "
            "constructor recipe selects only the three disabled-configuration calls and "
            "therefore establishes input acceptance, not telemetry runtime behavior."
        ),
    },
    (_PAGE, "trace-request-operations"): {
        "heading": "Trace request operations { #trace-request-operations }",
        "start_line": 107,
        "end_line": 117,
        "recipe_path": _CONSTRUCTOR_RECIPE,
        "case_ids": [_OPERATIONS_DISABLED],
        "observation_selectors": ["python.call_outcome"],
        "scope_note": (
            "The selected case observes acceptance of operation_spans=False only. It does "
            "not observe dependency, endpoint, serialization, or background-task spans."
        ),
        "rationale": (
            "The pinned section at docs/en/docs/advanced/opentelemetry.md:107-117 describes "
            "FastAPI operation spans and the operation_spans setting. The input selects that "
            "setting through the public FastAPI constructor; no span selector is currently "
            "available, so span emission remains unresolved."
        ),
    },
    (_PAGE, "trace-websocket-connections"): {
        "status": "excluded",
        "heading": "Trace WebSocket connections { #trace-websocket-connections }",
        "start_line": 118,
        "end_line": 123,
        "exclusion_reason": (
            "The documented WebSocket traces and disconnect logs have no telemetry-specific "
            "observation selector. Existing WebSocket selectors cover protocol messages, "
            "close codes, and lifecycle effects, not OpenTelemetry spans or log records."
        ),
        "rationale": (
            "FastAPI 0.157.0 documents WebSocket span and normal-disconnect behavior at "
            "docs/en/docs/advanced/opentelemetry.md:118-123 and implements it in "
            "fastapi/telemetry/_asgi.py. Mapping generic WebSocket protocol outcomes as "
            "telemetry evidence would conflate distinct contracts, so this section is "
            "excluded pending a telemetry-specific observation profile."
        ),
    },
    (_PAGE, "inspect-errors"): {
        "status": "excluded",
        "heading": "Inspect errors { #inspect-errors }",
        "start_line": 124,
        "end_line": 131,
        "exclusion_reason": (
            "Current selectors capture HTTP errors and validation details but not OpenTelemetry "
            "log records, severity, attributes, trace association, or redaction behavior."
        ),
        "rationale": (
            "FastAPI 0.157.0 documents exception and validation log behavior at "
            "docs/en/docs/advanced/opentelemetry.md:124-131; implementation is in "
            "fastapi/telemetry/_api.py and fastapi/telemetry/_asgi.py. HTTP error and "
            "validation responses do not establish equivalence of these separate log "
            "signals, so the section remains excluded pending an exact log observation."
        ),
    },
    (_PAGE, "choose-what-to-record"): {
        "heading": "Choose what to record { #choose-what-to-record }",
        "start_line": 132,
        "end_line": 158,
        "recipe_path": _CONSTRUCTOR_RECIPE,
        "case_ids": [_TRACING_DISABLED, _OPERATIONS_DISABLED, _SIGNALS_DISABLED],
        "observation_selectors": ["python.call_outcome", "python.signature"],
        "scope_note": (
            "Partial input mapping: selected cases accept tracing=False, operation_spans=False, "
            "and tracing/metrics/logs plus auto_configure disabled. The exclude callback and "
            "per-signal emission behavior are not observed."
        ),
        "rationale": (
            "The pinned table at docs/en/docs/advanced/opentelemetry.md:132-158 names "
            "tracing, metrics, logs, operation_spans, exclude, and auto_configure. The "
            "constructor recipe covers selected configuration inputs only; it does not "
            "establish the effect of any setting on emitted signals or excluded requests."
        ),
    },
}

__all__ = ["DOC_SECTION_CASE_MAPPINGS_OPENTELEMETRY_20261022"]
