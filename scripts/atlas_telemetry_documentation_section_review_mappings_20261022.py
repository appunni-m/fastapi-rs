"""Reviewed OpenTelemetry documentation section mappings for FastAPI 0.157.0."""

_PAGE = "advanced/opentelemetry.md"
_CONSTRUCTOR_RECIPE = "tests/fixtures/input-recipes/parity/telemetry-constructor-contract.yaml"
_SERVER_SPAN_RECIPE = "tests/fixtures/input-recipes/parity/telemetry-server-span.yaml"
_CLI_RECIPE = "tests/fixtures/input-recipes/parity/fastapi-cli-documented-process-v2.yaml"
_CLI_GUIDE_REQUEST = "fastapi.cli.process.opentelemetry-guide-request"

_DEFAULT = "fastapi.telemetry.constructor-default"
_TRACING_DISABLED = "fastapi.telemetry.constructor-tracing-disabled"
_OPERATIONS_DISABLED = "fastapi.telemetry.constructor-operation-spans-disabled"
_SIGNALS_DISABLED = "fastapi.telemetry.constructor-signals-disabled"
_HTTP_SERVER_SPAN_ROOT = "fastapi.telemetry.http-server-span-root"

DOC_SECTION_CASE_MAPPINGS_OPENTELEMETRY_20261022 = {
    (_PAGE, "install-fastapi"): {
        "status": "excluded",
        "heading": "Install FastAPI { #install-fastapi }",
        "start_line": 15,
        "end_line": 27,
        "exclusion_reason": (
            "This section demonstrates adding the standard extra with the uv package manager. "
            "The runtime fixture profile does not install packages or observe extra resolution; "
            "dependency identities and optional-feature roles are tracked in the dependency "
            "graph instead."
        ),
        "rationale": (
            "FastAPI 0.157.0's pinned section at "
            "docs/en/docs/advanced/opentelemetry.md:15-27 gives the uv add command for the "
            "standard extra. This is a package installation and optional-extra resolution step, "
            "not an "
            "in-process request/API stimulus; the current fixture profile has no package-manager "
            "observation."
        ),
    },
    (_PAGE, "fastapi-cloud"): {
        "status": "excluded",
        "heading": "FastAPI Cloud { #fastapi-cloud }",
        "start_line": 36,
        "end_line": 43,
        "exclusion_reason": (
            "The described metrics dashboard and hosted telemetry behavior require the external "
            "FastAPI Cloud service and account; the local parity fixtures cannot create or "
            "observe that service."
        ),
        "rationale": (
            "FastAPI 0.157.0's pinned section at "
            "docs/en/docs/advanced/opentelemetry.md:36-43 describes deployment to FastAPI Cloud "
            "and its hosted metrics dashboard. These service operations are outside the "
            "independently executable FastAPI library contract."
        ),
    },
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
            "plus the FastAPI constructor signature. A separate trace-request-operations "
            "mapping observes one root-path HTTP SERVER span. WebSocket spans, metrics, log "
            "records, context data, provider/exporter effects, and the FastAPI Cloud service "
            "remain outside those selected inputs."
        ),
        "rationale": (
            "FastAPI 0.157.0 introduces the telemetry constructor parameter in "
            "fastapi/applications.py and defines its TypedDict settings in "
            "fastapi/telemetry/_api.py. The pinned OpenTelemetry guide at "
            "docs/en/docs/advanced/opentelemetry.md:1-158 describes many runtime signals "
            "beyond constructor acceptance. These four independent constructor calls map "
            "only the bounded configuration surface. The separate trace-request-operations "
            "input maps one completed root-path HTTP SERVER span; broader emitted telemetry "
            "remains unresolved."
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
            "parity observations do not capture exporter selection or provider lifecycle; "
            "one separate input observes a root-path HTTP SERVER span, "
            "and the fixture profile does not start a collector. Keep these behaviors in "
            "the telemetry observation-contract backlog until a deterministic process and "
            "export observation is available."
        ),
        "rationale": (
            "FastAPI 0.157.0 documents FASTAPI_OTEL_AUTO_CONFIGURE and OTEL_EXPORTER_OTLP_* "
            "configuration at docs/en/docs/advanced/opentelemetry.md:44-59; "
            "fastapi/telemetry/_runtime.py implements endpoint selection and exporter "
            "registration. The selected server-span projection does not report OTLP "
            "exporter selection, metrics, logs, or shutdown effects, so this section is excluded "
            "from the present "
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
            "exporters, logs, metrics, or provider shutdown. A separate trace section maps "
            "one root-path HTTP SERVER span."
        ),
        "rationale": (
            "FastAPI 0.157.0 defines tracing, metrics, logs, operation_spans, provider, and "
            "auto_configure fields in fastapi/telemetry/_api.py; the pinned guide describes "
            "their settings at docs/en/docs/advanced/opentelemetry.md:81-131. The linked "
            "constructor recipe selects only the three disabled-configuration calls and "
            "therefore establishes input acceptance. The separate trace section maps one "
            "root-path HTTP SERVER span, not general telemetry runtime behavior."
        ),
    },
    (_PAGE, "configure-providers-and-exporters"): {
        "status": "excluded",
        "heading": "Configure providers and exporters { #configure-providers-and-exporters }",
        "start_line": 83,
        "end_line": 106,
        "exclusion_reason": (
            "The section documents global and injected provider selection, automatic exporter "
            "registration, and provider shutdown behavior. Current selectors do not observe "
            "provider identity, exporter setup, or lifecycle effects; the separate trace case "
            "observes only a root-path HTTP SERVER span."
        ),
        "rationale": (
            "FastAPI 0.157.0's pinned section at "
            "docs/en/docs/advanced/opentelemetry.md:83-106 describes provider/exporter "
            "configuration and links tutorial002, which injects a TracerProvider configured "
            "with BatchSpanProcessor and ConsoleSpanExporter. The current constructor cases do "
            "not exercise that provider input, and the span selector does not identify provider "
            "or exporter behavior, so the section remains excluded pending a broader deterministic "
            "telemetry profile."
        ),
    },
    (_PAGE, "trace-request-operations"): {
        "heading": "Trace request operations { #trace-request-operations }",
        "start_line": 107,
        "end_line": 117,
        "recipe_path": _SERVER_SPAN_RECIPE,
        "case_ids": [_HTTP_SERVER_SPAN_ROOT],
        "action_ids": ["root-request"],
        "observation_selectors": ["telemetry.server_spans"],
        "scope_note": (
            "One direct ASGI GET / input selects completed HTTP SERVER spans, including their "
            "name, status, attributes, and events. It does not cover the documented /items/1 "
            "route, operation spans, metrics, logs, context, export, or lifespan behavior."
        ),
        "rationale": (
            "The pinned section at docs/en/docs/advanced/opentelemetry.md:107-117 describes "
            "FastAPI request and operation spans. The linked input observes one root-path HTTP "
            "SERVER span through the parity-only SDK profile. Dependency, endpoint, "
            "serialization, and background-task spans remain outside this selected case."
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
