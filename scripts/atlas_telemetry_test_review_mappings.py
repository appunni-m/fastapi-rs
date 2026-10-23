"""Source-backed review of FastAPI's 0.157.0 OpenTelemetry tests.

The pinned tests inspect SDK spans, metrics, logs, context state, or exporter
effects. A narrow HTTP server-span workflow maps one completed root-path request;
the remaining output and lifecycle behaviors retain explicit per-function scope
exclusions. The constructor recipe remains a separate input-only probe.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.157.0",
        "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI and TestClient oracle",
    },
    "pydantic": {"version": "2.13.5", "role": "pinned dependency identity"},
}

_GLOBAL_PROVIDER_RECIPE = (
    "tests/fixtures/input-recipes/parity/telemetry-global-provider.yaml"
)
_TRACEPARENT_RECIPE = "tests/fixtures/input-recipes/parity/telemetry-traceparent.yaml"

__all__ = [
    "SOURCE_IDENTITIES",
    "TELEMETRY_TEST_FUNCTION_COUNT",
    "TELEMETRY_TEST_MODULE_EXCLUSIONS",
    "TELEMETRY_TEST_REVIEW_MAPPINGS",
]


def _source(path: str, start_line: int, end_line: int, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "start_line": start_line,
        "end_line": end_line,
        "role": role,
    }


def _whole_source(path: str, role: str) -> dict[str, Any]:
    line_count = len((FASTAPI_ROOT / path).read_text(encoding="utf-8").splitlines())
    if line_count < 1:
        raise ValueError(f"cannot create a line citation for empty source: {path}")
    return _source(path, 1, line_count, role)


def _top_level_functions(path: str) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = ast.parse((FASTAPI_ROOT / path).read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def _signal_families(
    test_path: str, node: ast.FunctionDef | ast.AsyncFunctionDef
) -> tuple[str, ...]:
    names = {child.id.lower() for child in ast.walk(node) if isinstance(child, ast.Name)}
    names.update(child.attr.lower() for child in ast.walk(node) if isinstance(child, ast.Attribute))
    strings = {
        child.value.lower()
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }
    names.update(strings)
    families: list[str] = []

    if names & {"span", "spans", "tracer", "tracing", "trace", "propagator", "baggage"}:
        families.append("trace spans or trace context")
    if names & {"metric", "metrics", "meter", "metering", "reader", "metric_points"}:
        families.append("metric measurements")
    if names & {"log", "logs", "logger", "logging", "record", "records", "caplog"}:
        families.append("OpenTelemetry log records")
    if names & {"get_telemetry_data", "telemetrydata", "saved_contexts", "request_refs"}:
        families.append("request-local TelemetryData and context lifetime")
    if names & {"otlp", "exporter", "export", "endpoint", "_runtime", "_owned"}:
        families.append("OTLP exporter setup or lifecycle")
    if names & {"_export_endpoint", "export_endpoint", "runtime"}:
        families.append("private OTLP environment-endpoint helper")
    if names & {"_registration_provider", "registration_provider"}:
        families.append("private provider adapter selection helper")
    if node.name == "test_otlp_collector_does_not_resolve_hostname":
        families.append("private test-only OTLP collector helper")
    if test_path.endswith(("test_integrations.py", "test_native_integrations.py")) or names & {
        "sentry_sdk",
        "logfire",
        "instrumentor",
        "opentelemetry.instrumentation",
    }:
        families.append("optional third-party instrumentation integration")
    if "test_websockets.py" in test_path:
        families.append("WebSocket telemetry and connection lifecycle")
    if "test_operations.py" in test_path or "operation_spans" in names:
        families.append("FastAPI dependency, endpoint, serialization, or task spans")
    if "environment" in test_path or "environment" in names:
        families.append("environment-driven provider or exporter configuration")
    if node.name == "test_application_lifespan_errors_still_propagate":
        families.append(
            "application lifespan exception propagation with invalid exporter configuration"
        )

    return tuple(dict.fromkeys(families))


def _source_refs(families: tuple[str, ...]) -> list[dict[str, Any]]:
    refs = [
        _source(
            "fastapi/applications.py",
            71,
            83,
            "FastAPI constructor declares the telemetry configuration parameter",
        ),
        _source(
            "fastapi/applications.py",
            1175,
            1205,
            "FastAPI ASGI entrypoint enters native telemetry and delegates other paths",
        ),
        _source(
            "docs/en/docs/advanced/opentelemetry.md",
            13,
            17,
            "User guide describes native HTTP and WebSocket telemetry and standard-extra setup",
        ),
    ]
    family_set = set(families)
    if any("trace" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_asgi.py",
                    157,
                    217,
                    "NativeTelemetry selects providers and creates HTTP telemetry instruments",
                ),
                _source(
                    "fastapi/telemetry/_asgi.py",
                    228,
                    387,
                    "NativeTelemetry extracts trace context, creates spans, and finalizes signals",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    107,
                    122,
                    "User guide specifies operation-span and WebSocket trace behavior",
                ),
            ]
        )
    if any("metric" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_asgi.py",
                    157,
                    217,
                    "NativeTelemetry creates the request-duration and active-request instruments",
                ),
                _source(
                    "fastapi/telemetry/_asgi.py",
                    251,
                    288,
                    "NativeTelemetry independently enables HTTP metrics and creates measurements",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    136,
                    143,
                    "User guide documents telemetry enablement settings and defaults",
                ),
            ]
        )
    if any("log" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_asgi.py",
                    87,
                    114,
                    "Native exception middleware emits exception log records",
                ),
                _source(
                    "fastapi/telemetry/_api.py",
                    151,
                    174,
                    "Validation failures update TelemetryData and emit warning records",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    124,
                    130,
                    "User guide describes exception and validation log behavior",
                ),
            ]
        )
    if any(
        "telemetrydata" in family.lower() or "context lifetime" in family.lower()
        for family in family_set
    ):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_api.py",
                    89,
                    148,
                    "TelemetryData fields and the public context lookup API",
                ),
                _source(
                    "fastapi/telemetry/_asgi.py",
                    328,
                    348,
                    "NativeTelemetry publishes request-local telemetry in context",
                ),
                _source(
                    "fastapi/telemetry/_asgi.py",
                    451,
                    457,
                    "NativeTelemetry clears data and detaches request context on completion",
                ),
            ]
        )
    if any(
        "exporter" in family.lower() or "environment" in family.lower() for family in family_set
    ):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_runtime.py",
                    42,
                    70,
                    "Runtime resolves OTLP endpoint, exporter, and protocol environment settings",
                ),
                _source(
                    "fastapi/telemetry/_runtime.py",
                    85,
                    207,
                    "Runtime conditionally configures and owns OTLP export components",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    46,
                    58,
                    "User guide describes environment-based OTLP export configuration",
                ),
            ]
        )
    if any("private otlp environment-endpoint" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_runtime.py",
                    42,
                    70,
                    "Private runtime helper resolves endpoints and validates OTLP protocol settings",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    46,
                    58,
                    "User guide describes environment-based OTLP endpoint configuration",
                ),
            ]
        )
    if any("private provider adapter" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_runtime.py",
                    73,
                    82,
                    "Private runtime helper adapts an optional Logfire meter-provider wrapper",
                ),
                _source(
                    "pyproject.toml",
                    174,
                    179,
                    "Logfire and OpenTelemetry SDK are test dependencies",
                ),
            ]
        )
    if any("test-only otlp collector" in family.lower() for family in family_set):
        refs.append(
            _source(
                "tests/test_telemetry/_otlp.py",
                1,
                36,
                "Test-only loopback OTLP collector helper whose hostname lookup is asserted",
            )
        )
    if any("application lifespan exception propagation" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_runtime.py",
                    210,
                    238,
                    "Telemetry exporter setup is attempted around ASGI lifespan messages and warning failures are caught",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    89,
                    99,
                    "User guide documents provider setup and exporter ownership",
                ),
            ]
        )
    if any("integration" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_asgi.py",
                    72,
                    84,
                    "Native telemetry detects an already installed contrib middleware",
                ),
                _source(
                    "pyproject.toml",
                    174,
                    179,
                    "Contrib, Logfire, Sentry, SDK, and exporter packages are upstream test dependencies",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    85,
                    99,
                    "User guide assigns provider and exporter ownership to integrations or applications",
                ),
            ]
        )
    if any("operation" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_api.py",
                    190,
                    244,
                    "FastAPI's private operation context creates endpoint and background-task spans",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    107,
                    115,
                    "User guide lists request operation spans and the operation_spans switch",
                ),
            ]
        )
    if any("websocket" in family.lower() for family in family_set):
        refs.extend(
            [
                _source(
                    "fastapi/telemetry/_asgi.py",
                    228,
                    260,
                    "NativeTelemetry selects WebSocket signal behavior and options",
                ),
                _source(
                    "fastapi/telemetry/_asgi.py",
                    416,
                    457,
                    "NativeTelemetry finalizes connection signals and clears request context",
                ),
                _source(
                    "docs/en/docs/advanced/opentelemetry.md",
                    118,
                    122,
                    "User guide describes connection spans, cleanup, and HTTP-only metrics",
                ),
            ]
        )

    unique: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for ref in refs:
        key = (ref["path"], ref["start_line"], ref["end_line"], ref["role"])
        unique.setdefault(key, ref)
    return list(unique.values())


def _reviewed_partial_function(
    *,
    test_path: str,
    name: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    recipe_path: str,
    case_id: str,
    selectors: tuple[str, ...],
    rationale: str,
    gate: str,
    families: tuple[str, ...],
) -> dict[str, Any]:
    span = _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"Pinned FastAPI 0.157.0 test function {name}",
    )
    return {
        "review_status": "reviewed_partial",
        "source_span": span,
        "feature_ids": ["telemetry"],
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "contract_gate": gate,
        "workflow_cases": [
            {
                "recipe_path": recipe_path,
                "case_id": case_id,
                "action_ids": ["root-request"],
                "observation_selectors": list(selectors),
            }
        ],
        "supporting_sources": [span, *_source_refs(families)],
    }


def _review_function(test_path: str, name: str, node: ast.AST) -> dict[str, Any]:
    assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    span = _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"Pinned FastAPI 0.157.0 test function {name}",
    )
    families = _signal_families(test_path, node)
    if (
        test_path == "tests/test_telemetry/test_http.py"
        and name == "test_late_global_providers_enable_existing_app"
    ):
        return _reviewed_partial_function(
            test_path=test_path,
            name=name,
            node=node,
            recipe_path=_GLOBAL_PROVIDER_RECIPE,
            case_id="fastapi.telemetry.global-tracer-provider-late-binding",
            selectors=("telemetry.server_spans",),
            rationale=(
                "Partial mapping: the independent GET / input constructs FastAPI before "
                "installing the global TracerProvider and observes the resulting HTTP SERVER "
                "span. It covers late-bound trace-provider selection only; the upstream test's "
                "initial request before provider installation, metric-provider fallback, explicit "
                "ProxyTracerProvider variant, and provider/exporter lifecycle are not covered."
            ),
            gate=(
                "Only the completed HTTP SERVER span is compared. Initial unconfigured request "
                "behavior, metrics, explicit proxy-provider configuration, and exporter lifecycle "
                "remain outside this input."
            ),
            families=families,
        )
    if test_path == "tests/test_telemetry/test_http.py" and name == "test_propagation_headers":
        return _reviewed_partial_function(
            test_path=test_path,
            name=name,
            node=node,
            recipe_path=_TRACEPARENT_RECIPE,
            case_id="fastapi.telemetry.traceparent-parent-context-root",
            selectors=("telemetry.server_span_parent_context",),
            rationale=(
                "Partial mapping: the independent root GET / input checks the parent trace and "
                "span IDs from one well-formed traceparent header. It does not observe baggage "
                "or tracestate values, duplicate tracestate/baggage joining, or the upstream "
                "parameterized split-header cases."
            ),
            gate=(
                "Only parent trace/span IDs from one traceparent value are compared. Duplicate "
                "baggage and tracestate semantics and baggage context remain unresolved."
            ),
            families=families,
        )
    if (
        test_path == "tests/test_tutorial/test_opentelemetry/test_tutorial001.py"
        and node.name == "test_default_example"
    ):
        reason = (
            f"At {test_path}:{span['start_line']}-{span['end_line']}, `{name}` sends GET "
            "`/items/1` to the documented `item_id: int` route and checks the JSON response; "
            "it does not assert an OpenTelemetry signal. The same typed route and request are "
            "represented by the independent input case "
            "`fastapi.path-params.tutorial002-integer-item-id` in "
            "tests/fixtures/input-recipes/parity/path-params-tutorial002-upstream.yaml, with "
            "exact HTTP status and body selectors. Exclude this function only from the "
            "telemetry-specific denominator; that HTTP case does not establish trace, metric, "
            "or log parity."
        )
    elif node.name == "test_otlp_collector_does_not_resolve_hostname":
        reason = (
            f"At {test_path}:{span['start_line']}-{span['end_line']}, `{name}` calls the "
            "private loopback collector from tests/test_telemetry/_otlp.py and asserts its "
            "hostname-lookup side effect. It does not invoke a FastAPI API or observe emitted "
            "telemetry, so it is excluded from the public telemetry behavior denominator."
        )
    elif "private provider adapter selection helper" in families:
        reason = (
            f"At {test_path}:{span['start_line']}-{span['end_line']}, `{name}` directly calls "
            "the private fastapi.telemetry._runtime._registration_provider helper with an "
            "optional Logfire wrapper. The helper is implementation-specific and the test "
            "observes provider object selection rather than FastAPI's documented API or an "
            "exported telemetry signal; exclude it from the public telemetry behavior denominator."
        )
    elif families:
        family_text = ", ".join(families)
        reason = (
            f"At {test_path}:{span['start_line']}-{span['end_line']}, `{name}` asserts "
            f"{family_text}. FastAPI's pinned implementation and guide identify those as "
            "OpenTelemetry outputs or context state. The current Python/ASGI observation "
            "vocabulary records neither those telemetry values nor exporter/provider effects; "
            "an HTTP status or body from the same function cannot stand in for them. Exclude "
            "this function from telemetry comparison until a telemetry-specific observation "
            "contract exists. This is a scope exclusion, not an unsupported-behavior or parity claim."
        )
    else:
        reason = (
            f"At {test_path}:{span['start_line']}-{span['end_line']}, `{name}` checks generic "
            "FastAPI request, response, or background-task behavior without asserting an "
            "OpenTelemetry signal or request-context value. Exclude this function from the "
            "telemetry denominator; its generic FastAPI behavior belongs to the corresponding "
            "request, response, or task contract and is not evidence of telemetry parity."
        )
    sources = [span, *_source_refs(families)]
    return {
        "review_status": "reviewed_excluded",
        "mapping_status": "source_backed_exclusion",
        "source_span": span,
        "feature_ids": [],
        "observation_selectors": [],
        "rationale": reason,
        "exclusion_reason": reason,
        "workflow_cases": [],
        "supporting_sources": sources,
    }


_TELEMETRY_TEST_ROOTS = (
    "tests/test_telemetry",
    "tests/test_tutorial/test_opentelemetry",
)
_module_reviews: dict[str, dict[str, Any]] = {}
TELEMETRY_TEST_FUNCTION_COUNT = 0
for _test_root in _TELEMETRY_TEST_ROOTS:
    for _path in sorted((FASTAPI_ROOT / _test_root).glob("test_*.py")):
        _test_path = _path.relative_to(FASTAPI_ROOT).as_posix()
        _functions = _top_level_functions(_test_path)
        if not _functions:
            continue
        _reviews = {
            name: _review_function(_test_path, name, node)
            for name, node in sorted(_functions.items())
        }
        TELEMETRY_TEST_FUNCTION_COUNT += len(_reviews)
        has_http_server_span_sources = _test_path in {
            "tests/test_telemetry/test_http.py",
            "tests/test_telemetry/test_semantic_conventions.py",
        }
        _module_reviews[_test_path] = {
            "rationale": (
                (
                    "Each telemetry test function is reviewed individually below. Input-only "
                    "cases partially map late-bound global TracerProvider selection and one "
                    "traceparent parent-context projection; all other assertions retain their "
                    "explicit exclusions or gaps."
                )
                if has_http_server_span_sources
                else (
                    "Each test function is classified individually below. No telemetry "
                    "workflow selects any upstream test function from this module."
                )
            ),
            "functions": _reviews,
            "supporting_sources": [
                _whole_source(
                    _test_path,
                    "Pinned FastAPI 0.157.0 source evidence only; function-level test exclusions follow",
                ),
                *(
                    _source_refs(("trace spans or trace context",))
                    if has_http_server_span_sources
                    else []
                ),
            ],
        }

TELEMETRY_TEST_REVIEW_MAPPINGS = _module_reviews


def _module_exclusion(reason: str, supporting_sources: list[dict[str, Any]]) -> dict[str, Any]:
    return {"exclusion_reason": reason, "supporting_sources": supporting_sources}


TELEMETRY_TEST_MODULE_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "tests/test_telemetry/__init__.py": _module_exclusion(
        "This package marker is an empty file with no test functions or executable behavior; it contributes no telemetry test case.",
        [],
    ),
    "tests/test_telemetry/conftest.py": _module_exclusion(
        "This conftest only clears exporter environment variables and constructs/shuts down SDK in-memory providers for other tests. It defines no test function and is not a FastAPI consumer API or target runtime dependency. The pinned project puts the SDK and OTLP exporter in optional extras and its SDK/integration use in the test dependency group.",
        [
            _whole_source(
                "tests/test_telemetry/conftest.py",
                "Test-only fixture setup creates OpenTelemetry SDK providers and exporters",
            ),
            _source(
                "pyproject.toml",
                60,
                67,
                "OpenTelemetry SDK and OTLP exporter are optional opentelemetry/standard extras",
            ),
            _source(
                "pyproject.toml",
                174,
                179,
                "SDK, exporter, and external integrations are test dependencies",
            ),
        ],
    ),
    "tests/test_telemetry/_otlp.py": _module_exclusion(
        "This private test helper starts a loopback HTTP collector and records incoming OTLP request bytes. It supports tests of exporter wire effects, has no test function of its own, and its collector is not part of the FastAPI public contract.",
        [
            _whole_source(
                "tests/test_telemetry/_otlp.py",
                "Private test-only loopback OTLP collector helper",
            ),
            _source(
                "fastapi/telemetry/_runtime.py",
                85,
                148,
                "FastAPI runtime conditionally creates OTLP exporters from optional dependencies",
            ),
        ],
    ),
    "tests/test_telemetry/_subprocess.py": _module_exclusion(
        "This private test helper strips telemetry environment variables, launches a fresh Python interpreter, and re-runs a decorated test to isolate SDK globals. It defines test infrastructure rather than a FastAPI API or telemetry observation contract.",
        [
            _whole_source(
                "tests/test_telemetry/_subprocess.py",
                "Private subprocess isolation decorator and command-line test helper",
            ),
        ],
    ),
    "tests/test_tutorial/test_opentelemetry/__init__.py": _module_exclusion(
        "This package marker is an empty file with no test functions or executable behavior; it contributes no telemetry test case.",
        [],
    ),
    "tests/test_tutorial/test_opentelemetry/conftest.py": _module_exclusion(
        "This conftest only reuses the telemetry test environment-cleanup fixture. It defines no test function and creates no independent FastAPI behavior or observation.",
        [
            _whole_source(
                "tests/test_tutorial/test_opentelemetry/conftest.py",
                "Tutorial test fixture only removes telemetry environment variables",
            ),
            _source(
                "tests/test_telemetry/conftest.py",
                15,
                21,
                "Shared test-only fixture removes telemetry environment variables",
            ),
        ],
    ),
}
