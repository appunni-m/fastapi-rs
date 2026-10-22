"""Exact materialized workflow links for the first reviewed documentation-page gap wave.

Keys are paths relative to FastAPI 0.157.0 at
``386a28af2f87af1a32ac26d88f07b7f58ab2dfb1``'s ``docs/en/docs`` tree. Each row
copies one indexed workflow mapping and its partial selector scope.
"""

from typing import Any

DOC_PAGE_CASE_LINK_COMPLETIONS: dict[str, list[dict[str, Any]]] = {
    "advanced/async-tests.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/async_tests.yaml",
            "case_ids": [
                "fastapi.docs.async-tests.async-route",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "advanced/custom-response.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/apirouter-default-response-class.yaml"
            ),
            "case_ids": [
                "fastapi.routing.apirouter.default-response-class.direct-read-write",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, docs.response.status, http.body.bytes, "
                "http.headers.ordered, http.status, openapi.document, openapi.paths. Unlisted "
                "functions, branches, configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/array-items-query-wire.yaml",
            "case_ids": [
                "fastapi.openapi-array-items-query-wire.required-list",
                "fastapi.openapi-array-items-query-wire.required-sequence",
            ],
            "observation_selectors": [
                "asgi.application_error.exception",
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "python.warnings",
                "warnings.category_message",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes "
                "asgi.application_error.exception, asgi.send.message_types, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, docs.response.body.bytes, docs.response.headers, "
                "docs.response.status, http.body.bytes, http.headers.ordered, http.status, "
                "openapi.document, python.warnings, warnings.category_message. Unlisted "
                "functions, branches, configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/inline-query-schema-wire.yaml",
            "case_ids": [
                "fastapi.openapi-inline-query-schema-wire.dependency-defaults",
                "fastapi.openapi-inline-query-schema-wire.direct-defaults",
            ],
            "observation_selectors": [
                "asgi.application_error.exception",
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "python.warnings",
                "warnings.category_message",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes "
                "asgi.application_error.exception, asgi.send.message_types, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, docs.response.body.bytes, docs.response.headers, "
                "docs.response.status, http.body.bytes, http.headers.ordered, http.status, "
                "openapi.document, python.warnings, warnings.category_message. Unlisted "
                "functions, branches, configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/plain-text-openapi-media-type.yaml",
            "case_ids": [
                "fastapi.openapi.plain-text-response-class-media-type",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes docs.response.status, "
                "http.status, openapi.document, openapi.paths. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-field-lifecycle.yaml",
            "case_ids": [
                "fastapi.response-class-provenance.application-explicit-json-default-model-nan",
                "fastapi.response-class-provenance.explicit-custom-class-model",
                "fastapi.response-class-provenance.explicit-jsonresponse-model-nan",
                "fastapi.response-class-provenance.explicit-none-over-default-model",
                "fastapi.response-class-provenance.include-custom-default-model",
                "fastapi.response-class-provenance.inherited-omitted-defaults-model-nan",
                "fastapi.response-class-provenance.omitted-model-nan",
                "fastapi.response-class-provenance.route-explicit-over-inherited-model",
                "fastapi.response-class-provenance.router-custom-default-model",
            ],
            "observation_selectors": [
                "asgi.application_error.exception",
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 9 case(s); observes "
                "asgi.application_error.exception, asgi.send.message_types, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, http.body.bytes, http.headers.ordered, http.status. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/"
                "response-model-return-annotation-focused-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.response-model-return-annotation.explicit-response-model-bypass",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.send.message_types, construction.exception_class, "
                "construction.exception_message, construction.outcome, http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-policy-matrix.yaml",
            "case_ids": [
                "fastapi.response.bodyless-204",
                "fastapi.response.openapi-content-and-models",
                "fastapi.response.response-class-inheritance",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 3 case(s); observes docs.response.status, "
                "http.body.bytes, http.headers.ordered, http.status, openapi.document, "
                "openapi.paths. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": [
                "fastapi.response.direct-json",
                "fastapi.response.direct-plain-text",
                "fastapi.response.openapi-status-and-media",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 3 case(s); observes "
                "asgi.send.message_types, docs.response.body.bytes, docs.response.headers, "
                "docs.response.status, http.body.bytes, http.headers.ordered, http.status, "
                "openapi.document, openapi.paths. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/router-overrides.yaml",
            "case_ids": [
                "fastapi.routing.include-router.default-response-class-openapi-media-type",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes docs.response.status, "
                "http.status, openapi.document, openapi.paths. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/stream-cancellation.yaml",
            "case_ids": [
                "fastapi.stream-cancellation.jsonl-async-generator",
                "fastapi.stream-cancellation.raw-async-generator",
            ],
            "observation_selectors": [
                "asgi.cancellation.cancelled_caught",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes "
                "asgi.cancellation.cancelled_caught, construction.exception_class, "
                "construction.exception_message, construction.outcome, http.headers.ordered, "
                "http.status. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
    ],
    "advanced/events.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.lifecycle.add-event-handler-invalid-string",
                "fastapi.lifecycle.app-lifespan-state",
                "fastapi.lifecycle.async-generator-lifespan",
                "fastapi.lifecycle.async-shutdown-handler",
                "fastapi.lifecycle.empty-merged-lifespan-state",
                "fastapi.lifecycle.mixed-merged-lifespan-state",
                "fastapi.lifecycle.mounted-subapp-lifespan-exclusion",
                "fastapi.lifecycle.nested-lifespan-state",
                "fastapi.lifecycle.parameter-event-handlers",
                "fastapi.lifecycle.parent-lifespan-state-override",
                "fastapi.lifecycle.router-events-legacy",
                "fastapi.lifecycle.sync-generator-lifespan",
            ],
            "observation_selectors": [
                "asgi.lifespan.application_errors",
                "asgi.lifespan.event_order",
                "asgi.lifespan.shutdown",
                "asgi.lifespan.startup",
                "asgi.lifespan.workload_trace",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
                "python.warnings",
                "warnings.category_message",
            ],
            "scope_note": (
                "Partial independent sample across 12 case(s); observes "
                "asgi.lifespan.application_errors, asgi.lifespan.event_order, "
                "asgi.lifespan.shutdown, asgi.lifespan.startup, asgi.lifespan.workload_trace, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, http.body.bytes, http.status, python.warnings, "
                "warnings.category_message. Unlisted functions, branches, configurations, and "
                "edge cases are not claimed."
            ),
        },
    ],
    "advanced/response-change-status-code.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-policy-matrix.yaml",
            "case_ids": [
                "fastapi.response.dependency-status",
                "fastapi.response.status-overwrite",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": [
                "fastapi.response.declared-status",
                "fastapi.response.openapi-status-and-media",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes "
                "asgi.send.message_types, docs.response.body.bytes, docs.response.headers, "
                "docs.response.status, http.body.bytes, http.headers.ordered, http.status, "
                "openapi.document, openapi.paths. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/route-dependency-response-status.yaml"
            ),
            "case_ids": [
                "fastapi.route-dependency.response-status",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "advanced/response-cookies.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": [
                "fastapi.response.cookie-header",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.send.message_types, http.body.bytes, http.headers.ordered, http.status. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
    ],
    "advanced/response-directly.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/response-directly-tutorial001-wave.yaml"
            ),
            "case_ids": [
                "fastapi.response-directly.tutorial001.openapi-document",
                "fastapi.response-directly.tutorial001.path-response",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes docs.response.status, "
                "http.body.bytes, http.headers.ordered, http.status, openapi.document. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-field-lifecycle.yaml",
            "case_ids": [
                "fastapi.response-class-provenance.returned-response-bypasses-model-and-none",
            ],
            "observation_selectors": [
                "asgi.application_error.exception",
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.application_error.exception, asgi.send.message_types, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, http.body.bytes, http.headers.ordered, http.status. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-field-traversal.yaml",
            "case_ids": [
                "fastapi.response-field-traversal.returned-response-still-constructs-included-field",
            ],
            "observation_selectors": [
                "asgi.application_error.exception",
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.application_error.exception, asgi.send.message_types, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, http.body.bytes, http.headers.ordered, http.status. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": [
                "fastapi.response.direct-plain-text",
                "fastapi.response.openapi-status-and-media",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes "
                "asgi.send.message_types, docs.response.body.bytes, docs.response.headers, "
                "docs.response.status, http.body.bytes, http.headers.ordered, http.status, "
                "openapi.document, openapi.paths. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/worker-dispatch.yaml",
            "case_ids": [
                "fastapi.worker-dispatch.returned-response-bypasses-response-validation",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.send.message_types, construction.exception_class, "
                "construction.exception_message, construction.outcome, http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "advanced/response-headers.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": [
                "fastapi.response.injected-headers",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.send.message_types, http.body.bytes, http.headers.ordered, http.status. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
    ],
    "advanced/security/http-basic-auth.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/http-basic.yaml",
            "case_ids": [
                "fastapi.advanced.security.http-basic.malformed-base64",
                "fastapi.advanced.security.http-basic.malformed-pair",
                "fastapi.advanced.security.http-basic.missing",
                "fastapi.advanced.security.http-basic.non-basic-scheme",
                "fastapi.advanced.security.http-basic.openapi",
                "fastapi.advanced.security.http-basic.valid",
            ],
            "observation_selectors": [
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.security",
            ],
            "scope_note": (
                "Partial independent sample across 6 case(s); observes docs.response.headers, "
                "docs.response.status, http.body.bytes, http.headers.ordered, http.status, "
                "openapi.document, openapi.paths, openapi.security. Unlisted functions, "
                "branches, configurations, and edge cases are not claimed."
            ),
        },
    ],
    "advanced/stream-data.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/stream_data.yaml",
            "case_ids": [
                "fastapi.docs.stream-data.binary-stream",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/stream-data-tutorials-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.tutorial.stream-data.tutorial001.generator-forms",
                "fastapi.tutorial.stream-data.tutorial002.binary-generator-forms",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "advanced/testing-events.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/first-steps-application-testing-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.application-testing.lifespan-items",
            ],
            "observation_selectors": [
                "asgi.lifespan.application_errors",
                "asgi.lifespan.event_order",
                "asgi.lifespan.shutdown",
                "asgi.lifespan.startup",
                "asgi.lifespan.workload_trace",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.lifespan.application_errors, asgi.lifespan.event_order, "
                "asgi.lifespan.shutdown, asgi.lifespan.startup, asgi.lifespan.workload_trace, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, http.body.bytes, http.status. Unlisted functions, "
                "branches, configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.lifecycle.app-lifespan-state",
                "fastapi.lifecycle.async-generator-lifespan",
                "fastapi.lifecycle.async-shutdown-handler",
                "fastapi.lifecycle.empty-merged-lifespan-state",
                "fastapi.lifecycle.mixed-merged-lifespan-state",
                "fastapi.lifecycle.nested-lifespan-state",
                "fastapi.lifecycle.parameter-event-handlers",
                "fastapi.lifecycle.parent-lifespan-state-override",
                "fastapi.lifecycle.router-events-legacy",
                "fastapi.lifecycle.sync-generator-lifespan",
            ],
            "observation_selectors": [
                "asgi.lifespan.application_errors",
                "asgi.lifespan.event_order",
                "asgi.lifespan.shutdown",
                "asgi.lifespan.startup",
                "asgi.lifespan.workload_trace",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
                "python.warnings",
                "warnings.category_message",
            ],
            "scope_note": (
                "Partial independent sample across 10 case(s); observes "
                "asgi.lifespan.application_errors, asgi.lifespan.event_order, "
                "asgi.lifespan.shutdown, asgi.lifespan.startup, asgi.lifespan.workload_trace, "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, http.body.bytes, http.status, python.warnings, "
                "warnings.category_message. Unlisted functions, branches, configurations, and "
                "edge cases are not claimed."
            ),
        },
    ],
    "advanced/testing-websockets.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/testing_websockets.yaml",
            "case_ids": [
                "fastapi.docs.testing-websockets.testclient-example",
            ],
            "observation_selectors": [
                "websocket.close_code",
                "websocket.event_order",
                "websocket.messages",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes websocket.close_code, "
                "websocket.event_order, websocket.messages. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "advanced/websockets.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/public-errors-http-websocket-wave.yaml"
            ),
            "case_ids": [
                "fastapi.public-errors.websocket.default-reason-empty",
                "fastapi.public-errors.websocket.pre-accept-code-and-reason",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "websocket.close_code",
                "websocket.close_reason",
                "websocket.event_order",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, websocket.close_code, websocket.close_reason, "
                "websocket.event_order. Unlisted functions, branches, configurations, and "
                "edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/websocket-echo.yaml",
            "case_ids": [
                "fastapi.websocket.echo-text",
            ],
            "observation_selectors": [
                "websocket.event_order",
                "websocket.messages",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes websocket.event_order, "
                "websocket.messages. Unlisted functions, branches, configurations, and edge "
                "cases are not claimed."
            ),
        },
    ],
    "reference/apirouter.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.http.apirouter-prefix",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes docs.response.status, "
                "http.body.bytes, http.headers.ordered, http.status, openapi.document, "
                "openapi.paths. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/root-alias-identity.yaml",
            "case_ids": [
                "fastapi.root-alias-identity.http-reexports",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.status. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/router-dependencies-isolated.yaml",
            "case_ids": [
                "fastapi.routing.include-router.router-and-include-dependencies",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.status, openapi.document, openapi.paths. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "reference/exceptions.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml",
            "case_ids": [
                "fastapi.direct-api-reference-wave.http-exception-signature",
                "fastapi.direct-api-reference-wave.websocket-exception-signature",
            ],
            "observation_selectors": [
                "python.signature",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes python.signature. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.asgi.http-exception-mapping",
                "fastapi.docs.reference-wave.asgi.websocket-exception-close",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "websocket.close_code",
                "websocket.event_order",
                "websocket.messages",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status, websocket.close_code, "
                "websocket.event_order, websocket.messages. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/public-errors-http-websocket-wave.yaml"
            ),
            "case_ids": [
                "fastapi.public-errors.websocket.pre-accept-code-and-reason",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "websocket.close_code",
                "websocket.close_reason",
                "websocket.event_order",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, websocket.close_code, websocket.close_reason, "
                "websocket.event_order. Unlisted functions, branches, configurations, and "
                "edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/root-alias-identity.yaml",
            "case_ids": [
                "fastapi.root-alias-identity.http-reexports",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.status. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
    ],
    "reference/httpconnection.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml",
            "case_ids": [
                "fastapi.test.test-http-connection-injection.test-value-extracting-by-http",
                "fastapi.test.test-http-connection-injection.test-value-extracting-by-ws",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "websocket.close_code",
                "websocket.event_order",
                "websocket.messages",
            ],
            "scope_note": (
                "Partial independent sample across 2 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status, websocket.close_code, "
                "websocket.event_order, websocket.messages. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/http-connection-injection-websocket.yaml"
            ),
            "case_ids": [
                "fastapi.http-connection-injection.http-app-state",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.status. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/request-injection-slice.yaml",
            "case_ids": [
                "fastapi.request-injection-slice.request-app-state",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "reference/openapi/docs.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-openapi.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.openapi.docs-ui-helpers",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
    ],
    "reference/openapi/models.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml",
            "case_ids": [
                "fastapi.direct-api-reference-wave.openapi-info-signature",
                "fastapi.direct-api-reference-wave.openapi-model-signature",
                "fastapi.direct-api-reference-wave.openapi-schema-signature",
            ],
            "observation_selectors": [
                "python.signature",
            ],
            "scope_note": (
                "Partial independent sample across 3 case(s); observes python.signature. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-openapi.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.openapi.openapi-info-model",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes docs.response.status, "
                "http.body.bytes, http.headers.ordered, http.status, openapi.document, "
                "openapi.paths. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/openapi-model-public-api.yaml",
            "case_ids": [
                "fastapi.openapi-models.components.signature",
                "fastapi.openapi-models.discriminator.signature",
                "fastapi.openapi-models.schema.signature",
            ],
            "observation_selectors": [
                "python.signature",
            ],
            "scope_note": (
                "Partial independent sample across 3 case(s); observes python.signature. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/openapi-operation-pathitem-public-api.yaml"
            ),
            "case_ids": [
                "fastapi.openapi-models.operation.signature",
                "fastapi.openapi-models.operation.defaults",
                "fastapi.openapi-models.operation.populated",
                "fastapi.openapi-models.operation.invalid-deprecated",
                "fastapi.openapi-models.path-item.signature",
                "fastapi.openapi-models.path-item.defaults",
                "fastapi.openapi-models.path-item.populated",
                "fastapi.openapi-models.path-item.invalid-summary",
            ],
            "observation_selectors": [
                "python.call_outcome",
                "python.pydantic_model_result",
                "python.signature",
            ],
            "scope_note": (
                "Partial independent sample across 8 cases; observes constructor signatures, "
                "default and populated model dumps, nested OpenAPI fields, reference aliases, "
                "extra extension retention, and invalid values for Operation and PathItem. "
                "Other model classes, Pydantic behavior, and validation boundaries are not claimed."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/openapi-auxiliary-models-public-api.yaml"
            ),
            "case_ids": [
                "fastapi.openapi-models.external-documentation.signature",
                "fastapi.openapi-models.external-documentation.defaults",
                "fastapi.openapi-models.external-documentation.populated",
                "fastapi.openapi-models.external-documentation.invalid-missing-url",
                "fastapi.openapi-models.license.signature",
                "fastapi.openapi-models.license.defaults",
                "fastapi.openapi-models.license.populated",
                "fastapi.openapi-models.license.invalid-missing-name",
                "fastapi.openapi-models.tag.signature",
                "fastapi.openapi-models.tag.defaults",
                "fastapi.openapi-models.tag.populated",
                "fastapi.openapi-models.tag.invalid-name",
                "fastapi.openapi-models.xml.signature",
                "fastapi.openapi-models.xml.defaults",
                "fastapi.openapi-models.xml.populated",
                "fastapi.openapi-models.xml.invalid-wrapped",
            ],
            "observation_selectors": [
                "python.call_outcome",
                "python.pydantic_model_result",
                "python.signature",
            ],
            "scope_note": (
                "Partial independent sample across 16 cases; observes signatures, required and "
                "optional field projections, nested ExternalDocumentation, extension retention, "
                "and representative invalid inputs for ExternalDocumentation, License, Tag, "
                "and XML. Other Pydantic behavior and validation boundaries are not claimed."
            ),
        },
    ],
    "reference/request.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.http.request-injection",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/root-alias-identity.yaml",
            "case_ids": [
                "fastapi.root-alias-identity.http-reexports",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.status. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
    ],
    "reference/response.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.http.response-injection",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.headers.ordered, http.status. Unlisted functions, branches, "
                "configurations, and edge cases are not claimed."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/root-alias-identity.yaml",
            "case_ids": [
                "fastapi.root-alias-identity.http-reexports",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes http.body.bytes, "
                "http.status. Unlisted functions, branches, configurations, and edge cases "
                "are not claimed."
            ),
        },
    ],
    "reference/responses.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": [
                "fastapi.response.direct-plain-text",
            ],
            "observation_selectors": [
                "asgi.send.message_types",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "Partial independent sample across 1 case(s); observes "
                "asgi.send.message_types, http.body.bytes, http.headers.ordered, http.status. "
                "Unlisted functions, branches, configurations, and edge cases are not "
                "claimed."
            ),
        },
    ],
    "reference/security/index.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/security-dependencies.yaml",
            "case_ids": [
                "fastapi.docs.security.api-key-optional-missing",
                "fastapi.docs.security.api-key-optional-provided",
                "fastapi.docs.security.api-key-required-missing",
                "fastapi.docs.security.api-key-required-provided",
                "fastapi.docs.security.bearer-optional-missing",
                "fastapi.docs.security.bearer-optional-valid",
                "fastapi.docs.security.bearer-optional-wrong-scheme",
                "fastapi.docs.security.bearer-required-missing",
                "fastapi.docs.security.bearer-required-valid",
                "fastapi.docs.security.bearer-required-wrong-scheme",
                "fastapi.docs.security.openapi",
            ],
            "observation_selectors": [
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.security",
            ],
            "scope_note": (
                "Partial independent sample across 11 case(s); observes "
                "docs.response.headers, docs.response.status, http.body.bytes, "
                "http.headers.ordered, http.status, openapi.document, openapi.paths, "
                "openapi.security. Unlisted functions, branches, configurations, and edge "
                "cases are not claimed."
            ),
        },
    ],
    "reference/sse.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/sse.yaml",
            "case_ids": [
                "fastapi.test.test-sse.test-async-generator-no-annotation",
                "fastapi.test.test-sse.test-async-generator-with-model",
                "fastapi.test.test-sse.test-data-and-raw-data-mutually-exclusive",
                "fastapi.test.test-sse.test-default-response-class-on-app-openapi-schema",
                "fastapi.test.test-sse.test-default-response-class-on-app-stream",
                "fastapi.test.test-sse.test-default-response-class-on-parent-router-openapi-schema",
                "fastapi.test.test-sse.test-default-response-class-on-parent-router-stream",
                "fastapi.test.test-sse.test-dict-items",
                "fastapi.test.test-sse.test-format-sse-event-splitlines-behavior-in-comment",
                "fastapi.test.test-sse.test-format-sse-event-splitlines-behavior-in-data",
                "fastapi.test.test-sse.test-mixed-plain-and-sse-events",
                "fastapi.test.test-sse.test-no-keepalive-when-fast",
                "fastapi.test.test-sse.test-post-method-sse",
                "fastapi.test.test-sse.test-raw-data-sent-without-json-encoding",
                "fastapi.test.test-sse.test-server-sent-event-float-retry-rejected",
                "fastapi.test.test-sse.test-server-sent-event-negative-retry-rejected",
                "fastapi.test.test-sse.test-server-sent-event-null-id-rejected",
                "fastapi.test.test-sse.test-server-sent-event-single-line-fields-reject-newlines.event-cr",
                "fastapi.test.test-sse.test-server-sent-event-single-line-fields-reject-newlines.event-crlf",
                "fastapi.test.test-sse.test-server-sent-event-single-line-fields-reject-newlines.event-lf",
                "fastapi.test.test-sse.test-server-sent-event-single-line-fields-reject-newlines.id-cr",
                "fastapi.test.test-sse.test-server-sent-event-single-line-fields-reject-newlines.id-crlf",
                "fastapi.test.test-sse.test-server-sent-event-single-line-fields-reject-newlines.id-lf",
                "fastapi.test.test-sse.test-sse-events-with-fields",
                "fastapi.test.test-sse.test-sse-on-router-included-in-app",
                "fastapi.test.test-sse.test-sse-router-typed-openapi-schema",
                "fastapi.test.test-sse.test-sse-router-typed-stream",
                "fastapi.test.test-sse.test-string-data-json-encoded",
                "fastapi.test.test-sse.test-sync-generator-no-annotation",
                "fastapi.test.test-sse.test-sync-generator-with-model",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Partial independent sample across 30 case(s); observes "
                "construction.exception_class, construction.exception_message, "
                "construction.outcome, docs.response.status, http.body.bytes, "
                "http.headers.ordered, http.status, openapi.document, openapi.paths. Unlisted "
                "functions, branches, configurations, and edge cases are not claimed."
            ),
        },
    ],
}

from atlas_documentation_page_case_links_tail import (  # noqa: E402
    DOC_PAGE_CASE_LINK_COMPLETIONS_TAIL,
)

_duplicate_page_paths = set(DOC_PAGE_CASE_LINK_COMPLETIONS) & set(
    DOC_PAGE_CASE_LINK_COMPLETIONS_TAIL
)
if _duplicate_page_paths:
    raise ValueError(
        "documentation case-link sidecars overlap: " + ", ".join(sorted(_duplicate_page_paths))
    )
DOC_PAGE_CASE_LINK_COMPLETIONS.update(DOC_PAGE_CASE_LINK_COMPLETIONS_TAIL)
