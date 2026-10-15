"""Exact reviewed input-workflow links for the remaining documentation pages.

Rows mirror the pinned materialized input index. Selector lists are the exact
projection of the linked recipe cases and their actions; notes bound each link
to the behavior sampled by those inputs.
"""

from typing import Any

DOC_PAGE_CASE_LINK_COMPLETIONS_TAIL: dict[str, list[dict[str, Any]]] = {
    "reference/status.md": [
        {
            "workflow_id": "response-surface",
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": ["fastapi.docs.reference-wave.status-code-from-constant"],
            "observation_selectors": [
                "asgi.send.message_types",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page identifies named HTTP status constants; this "
            "case observes one constant-backed response through its "
            "status, body, headers, and ASGI send types.",
        },
        {
            "workflow_id": "root-alias-identity",
            "recipe_path": "tests/fixtures/input-recipes/parity/root-alias-identity.yaml",
            "case_ids": ["fastapi.root-alias-identity.http-reexports"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": "The page documents importing status helpers through "
            "fastapi; this case samples the HTTP root re-export "
            "through response status and body.",
        },
        {
            "workflow_id": "status-module-identity",
            "recipe_path": "tests/fixtures/input-recipes/parity/status-module-identity.yaml",
            "case_ids": ["fastapi.status-alias.namespace"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": "The page says fastapi.status is provided by Starlette; "
            "this case samples the status namespace through one HTTP "
            "route response.",
        },
    ],
    "reference/websockets.md": [
        {
            "workflow_id": "docs-reference-asgi",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml",
            "case_ids": ["fastapi.docs.reference-wave.asgi.websocket-endpoint-session"],
            "observation_selectors": [
                "websocket.close_code",
                "websocket.event_order",
                "websocket.messages",
            ],
            "scope_note": "The page describes receiving from and sending to a "
            "WebSocket client; this case observes one endpoint "
            "session’s messages, event order, and close code.",
        },
        {
            "workflow_id": "root-alias-identity",
            "recipe_path": "tests/fixtures/input-recipes/parity/root-alias-identity.yaml",
            "case_ids": ["fastapi.root-alias-identity.websocket-reexports"],
            "observation_selectors": ["websocket.event_order", "websocket.messages"],
            "scope_note": "The page documents importing WebSocket through "
            "fastapi; this case samples the root re-export’s "
            "WebSocket messages and event order.",
        },
    ],
    "tutorial/cookie-params.md": [
        {
            "workflow_id": "cookie-parameter-surface-review",
            "recipe_path": "tests/fixtures/input-recipes/parity/cookie-parameter-surface-review.yaml",
            "case_ids": [
                "fastapi.request-parameters.cookie.review-slice.alias-name-missing",
                "fastapi.request-parameters.cookie.review-slice.alias-valid",
                "fastapi.request-parameters.cookie.review-slice.optional-missing",
                "fastapi.request-parameters.cookie.review-slice.required-missing",
            ],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": "The page documents Cookie parameter declarations "
            "and aliases; these cases sample valid, missing, "
            "required, and optional cookie inputs through HTTP "
            "status and body.",
        },
        {
            "workflow_id": "request-validation-parameters",
            "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-parameters.yaml",
            "case_ids": [
                "fastapi.request-parameters.cookie.alias-valid",
                "fastapi.request-parameters.cookie.optional-missing",
                "fastapi.request-parameters.cookie.required-missing",
            ],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": "The page explains that Cookie marks an input as a "
            "cookie parameter; these cases sample valid and "
            "missing cookie values through HTTP status and "
            "body.",
        },
    ],
    "tutorial/cors.md": [
        {
            "workflow_id": "cors-middleware-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/cors-middleware-upstream.yaml",
            "case_ids": [
                "fastapi.test.test-tutorial-test-cors-test-tutorial001.cors-preflight-disallowed-method",
                "fastapi.test.test-tutorial-test-cors-test-tutorial001.cors-preflight-disallowed-origin",
                "fastapi.test.test-tutorial-test-cors-test-tutorial001.cors-simple-disallowed-origin",
                "fastapi.test.test-tutorial-test-cors-test-tutorial001.test-cors",
            ],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page documents CORS origins, preflight, and simple "
            "requests; these cases observe selected preflight and "
            "origin-policy responses through HTTP body, headers, and "
            "status.",
        },
        {
            "workflow_id": "cors-tutorial-independent",
            "recipe_path": "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml",
            "case_ids": [
                "fastapi.docs.cors-tutorial.allowed-preflight",
                "fastapi.docs.cors-tutorial.allowed-simple-request",
                "fastapi.docs.cors-tutorial.disallowed-preflight-method",
                "fastapi.docs.cors-tutorial.unlisted-simple-request",
            ],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page describes browser cross-origin requests and CORS "
            "authorization; these independent cases sample allowed and "
            "rejected preflight/simple requests through HTTP "
            "projections.",
        },
        {
            "workflow_id": "docs-http-behaviors",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml",
            "case_ids": ["fastapi.docs.documentation-wave.http-behaviors.cors-preflight"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page explains the browser’s OPTIONS preflight exchange; "
            "this case observes one CORS preflight response through HTTP "
            "body, headers, and status.",
        },
    ],
    "tutorial/dependencies/sub-dependencies.md": [
        {
            "workflow_id": "dependency-callable-classification",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-callable-classification.yaml",
            "case_ids": [
                "fastapi.dependencies.callable-classification.partial-coroutine-instance",
                "fastapi.dependencies.callable-classification.partial-wrapped-coroutine-nested",
                "fastapi.dependencies.callable-classification.plain-partial-function-method-controls",
                "fastapi.dependencies.callable-classification.public-endpoint-role-classification",
                "fastapi.dependencies.callable-classification.sync-wrap-coroutine-call-method",
                "fastapi.dependencies.callable-classification.sync-wrap-coroutine-function",
                "fastapi.dependencies.callable-classification.sync-wrap-coroutine-instance",
                "fastapi.dependencies.callable-classification.unmarked-sync-awaitable-control",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page introduces nested "
            "dependencies; these cases sample "
            "FastAPI’s dependency callable and "
            "awaitable classification, including "
            "partial and wrapped callables, "
            "through construction and HTTP "
            "outcomes.",
        },
        {
            "workflow_id": "dependency-dynamic-cache-policy",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-dynamic-cache-policy.yaml",
            "case_ids": [
                "fastapi.dependencies.dynamic-cache-policy.failed-edge-later-sibling",
                "fastapi.dependencies.dynamic-cache-policy.flat-async-cache-hit-validation",
                "fastapi.dependencies.dynamic-cache-policy.flat-async-validation",
                "fastapi.dependencies.dynamic-cache-policy.nested-async-parent-sync-child",
                "fastapi.dependencies.dynamic-cache-policy.nested-sync-parent-async-child",
                "fastapi.dependencies.dynamic-cache-policy.parameterless-app-policy-ignored",
                "fastapi.dependencies.dynamic-cache-policy.parameterless-route-policy-ignored",
                "fastapi.dependencies.dynamic-cache-policy.parameterless-router-policy-ignored",
                "fastapi.dependencies.dynamic-cache-policy.raw-capture",
                "fastapi.dependencies.dynamic-cache-policy.sync-false-first-insertion",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.status",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": "The page describes nested "
            "dependencies and per-request "
            "caching; these cases sample nested "
            "sync/async resolution, cache-policy "
            "selection, and validation effects "
            "through the listed construction and "
            "HTTP observations.",
        },
        {
            "workflow_id": "dependency-lifecycle",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
            "case_ids": ["fastapi.dependencies.cache-bypass", "fastapi.dependencies.cache-reuse"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": "The page documents dependency "
            "caching and use_cache=False; these "
            "cases sample cache reuse and bypass "
            "through HTTP status and body.",
        },
        {
            "workflow_id": "dependency-override-cache-policy-mutation",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-override-cache-policy-mutation.yaml",
            "case_ids": [
                "fastapi.dependencies.override-policy-mutation.awaited-provider-removal",
                "fastapi.dependencies.override-policy-mutation.awaited-provider-replacement",
                "fastapi.dependencies.override-policy-mutation.cache-hit-policy-mutation",
                "fastapi.dependencies.override-policy-mutation.cached-later-validation",
                "fastapi.dependencies.override-policy-mutation.captured-child-declarations",
                "fastapi.dependencies.override-policy-mutation.earlier-failure-later-mutator",
                "fastapi.dependencies.override-policy-mutation.failed-mutator-valid-later",
                "fastapi.dependencies.override-policy-mutation.invalid-later-override-repaired",
                "fastapi.dependencies.override-policy-mutation.nested-parent-and-later-child",
                "fastapi.dependencies.override-policy-mutation.signature-clear-retains-registration",
                "fastapi.dependencies.override-policy-mutation.signature-unrelated-reanalysis",
                "fastapi.dependencies.override-policy-mutation.sync-own-selected-call-and-cache",
                "fastapi.dependencies.override-policy-mutation.sync-provider-removal",
                "fastapi.dependencies.override-policy-mutation.sync-provider-replacement",
                "fastapi.dependencies.override-policy-mutation.sync-to-coroutine",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": "The page’s dependency graph and "
            "cache discussion is linked to cases "
            "that mutate selected overrides and "
            "cache policies; only their "
            "construction and HTTP outcomes are "
            "claimed.",
        },
        {
            "workflow_id": "dependency-record-public-protocol",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-record-public-protocol.yaml",
            "case_ids": ["fastapi.dependency-records.public-protocol.cache-use-cache"],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": "The page shows nested dependency "
            "declarations; this case samples the "
            "public dependency-record cache "
            "setting through construction and "
            "one HTTP response.",
        },
        {
            "workflow_id": "dependency-tutorial005-query-cookie-fallback",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-tutorial005-query-cookie-fallback.yaml",
            "case_ids": [
                "fastapi.dependencies.tutorial005.query-cookie.fallback",
                "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
                "fastapi.dependencies.tutorial005.query-cookie.openapi-parameters",
                "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page’s tutorial005 example "
            "combines a query dependency with a "
            "cookie fallback; these cases "
            "observe fallback/precedence "
            "responses and the generated "
            "parameter paths.",
        },
        {
            "workflow_id": "generator-awaitable-protocol",
            "recipe_path": "tests/fixtures/input-recipes/parity/generator-awaitable-protocol.yaml",
            "case_ids": [
                "fastapi.awaitables.generator-protocol.await-method-generator-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.await-method-noniterator-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.caught-future-error",
                "fastapi.awaitables.generator-protocol.direct-generator-declaration-is-a-yield-role",
                "fastapi.awaitables.generator-protocol.genuine-async-bridge-control",
                "fastapi.awaitables.generator-protocol.genuine-async-bridge-future-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.marked-checkpoint",
                "fastapi.awaitables.generator-protocol.marked-endpoint-future",
                "fastapi.awaitables.generator-protocol.marked-future-nested-cache",
                "fastapi.awaitables.generator-protocol.marked-immediate-validation-cache",
                "fastapi.awaitables.generator-protocol.ordinary-await-iterator-caught-future-error",
                "fastapi.awaitables.generator-protocol.ordinary-await-iterator-control",
                "fastapi.awaitables.generator-protocol.propagated-future-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.unflagged-generator-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.unmarked-returned-generator-is-a-value",
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
            "scope_note": "The page’s nested dependency "
            "example is linked to cases sampling "
            "dependency awaitable/yield "
            "protocols, error propagation, and "
            "cleanup through construction and "
            "ASGI/HTTP observations.",
        },
    ],
    "tutorial/encoder.md": [
        {
            "workflow_id": "encoding",
            "recipe_path": "tests/fixtures/input-recipes/parity/encoding.yaml",
            "case_ids": ["fastapi.jsonable-encoder.tutorial.datetime-model"],
            "observation_selectors": ["python.attribute_value", "python.signature"],
            "scope_note": "The page states that jsonable_encoder converts models and "
            "values such as datetime to JSON-compatible Python data; "
            "this case samples a datetime model conversion and "
            "callable signature.",
        },
        {
            "workflow_id": "pydantic-core-encoder-compatibility",
            "recipe_path": "tests/fixtures/input-recipes/parity/pydantic-core-encoder-compatibility.yaml",
            "case_ids": ["fastapi.jsonable-encoder.pydantic-core-urls"],
            "observation_selectors": ["python.attribute_value"],
            "scope_note": "The page presents jsonable_encoder for JSON-compatible "
            "values; this case samples its Pydantic-core URL "
            "conversion result.",
        },
    ],
    "tutorial/first-steps.md": [
        {
            "workflow_id": "first-asgi-request",
            "recipe_path": "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
            "case_ids": [
                "fastapi.first-slice.create-item-chunked-body",
                "fastapi.first-slice.create-item-valid",
                "fastapi.first-slice.openapi",
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
                "openapi.request_schema",
            ],
            "scope_note": "The page starts with a minimal FastAPI route; these "
            "cases sample a valid/chunked request and the "
            "generated OpenAPI endpoint through the listed ASGI, "
            "HTTP, and schema selectors.",
        },
        {
            "workflow_id": "inherited-app-url-path-for",
            "recipe_path": "tests/fixtures/input-recipes/parity/inherited-app-url-path-for.yaml",
            "case_ids": ["fastapi.applications.url-path-for.included-router-context"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page demonstrates a minimal FastAPI application; "
            "this case samples URL generation for an included "
            "router through one HTTP response.",
        },
        {
            "workflow_id": "inherited-fastapi-add-route",
            "recipe_path": "tests/fixtures/input-recipes/parity/inherited-fastapi-add-route.yaml",
            "case_ids": [
                "fastapi.applications.add-route.registration-dispatch",
                "fastapi.applications.add-route.registration-method-miss",
            ],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page introduces registering a route on FastAPI; "
            "these cases sample add_route dispatch and a method "
            "miss through HTTP status, headers, and body.",
        },
        {
            "workflow_id": "inherited-fastapi-host",
            "recipe_path": "tests/fixtures/input-recipes/parity/inherited-fastapi-host.yaml",
            "case_ids": ["fastapi.applications.host.named-subdomain-dispatch"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page introduces the first application route; this "
            "case samples named-subdomain host dispatch through "
            "its HTTP response.",
        },
        {
            "workflow_id": "starlette-url-converters-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/starlette-url-converters-upstream.yaml",
            "case_ids": [
                "fastapi.applications.url-path-for.explicit-route-name",
                "fastapi.test.test-starlette-urlconvertors.test-route-converters-float-url-path-for",
                "fastapi.test.test-starlette-urlconvertors.test-route-converters-int-url-path-for",
                "fastapi.test.test-starlette-urlconvertors.test-url-path-for-path-convertor",
            ],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page demonstrates a minimal routed application; "
            "these cases sample explicit route names and "
            "URL-converter path-for results through HTTP "
            "responses.",
        },
        {
            "workflow_id": "webhooks-constructor",
            "recipe_path": "tests/fixtures/input-recipes/parity/webhooks-constructor.yaml",
            "case_ids": ["fastapi.webhooks.constructor-router.openapi-and-route-separation"],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page introduces a FastAPI application and its "
            "routes; this case samples webhook route/schema "
            "separation through HTTP and OpenAPI projections.",
        },
    ],
    "tutorial/frontend.md": [
        {
            "workflow_id": "docs-types-frontend",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-types-frontend.yaml",
            "case_ids": [
                "fastapi.docs.reference-wave.frontend.api-route-priority",
                "fastapi.docs.reference-wave.frontend.html-client-route-fallback",
                "fastapi.docs.reference-wave.frontend.missing-asset-no-fallback",
                "fastapi.docs.reference-wave.frontend.non-get-fallback",
            ],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page documents API-route precedence, frontend "
            "fallback, and non-GET behavior; these cases sample route "
            "priority and fallback responses through HTTP status, "
            "headers, and body.",
        },
        {
            "workflow_id": "frontend-fallback-routing-source-review",
            "recipe_path": "tests/fixtures/input-recipes/parity/frontend-fallback-routing-source-review.yaml",
            "case_ids": [
                "fastapi.frontend.configuration.auto-check-directory-production",
                "fastapi.frontend.configuration.check-dir-false-defers-check",
                "fastapi.frontend.fallback-routing-surface",
            ],
            "observation_selectors": [
                "asgi.application_error.exception",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": "The page specifies frontend directory checking and "
            "fallback routing; these cases sample directory "
            "configuration outcomes and a missing-path fallback "
            "through construction, ASGI, and HTTP observations.",
        },
    ],
    "tutorial/handling-errors.md": [
        {
            "workflow_id": "additional-response-field-lifecycle",
            "recipe_path": "tests/fixtures/input-recipes/parity/additional-response-field-lifecycle.yaml",
            "case_ids": [
                "fastapi.additional-response-field-lifecycle.second-additional-hook-retry"
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
            "scope_note": "The page explains handling request failures; this "
            "case samples an additional-response retry/error "
            "path through ASGI, construction, and HTTP "
            "outcomes.",
        },
        {
            "workflow_id": "custom-middleware-upload-limit",
            "recipe_path": "tests/fixtures/input-recipes/parity/custom-middleware-upload-limit.yaml",
            "case_ids": [
                "fastapi.middleware.custom-upload-budget-accepted",
                "fastapi.middleware.custom-upload-budget-exceeded",
            ],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page covers reporting client errors; these "
            "cases sample accepted and over-budget upload "
            "responses through HTTP body, headers, and "
            "status.",
        },
        {
            "workflow_id": "dependency-callable-classification",
            "recipe_path": "tests/fixtures/input-recipes/parity/dependency-callable-classification.yaml",
            "case_ids": [
                "fastapi.dependencies.callable-classification.async-wrapped-scalar-error-cleanup-recovery",
                "fastapi.dependencies.callable-classification.public-marked-scalar-error-cleanup-recovery",
                "fastapi.dependencies.callable-classification.wrapped-yield-error-cleanup-recovery",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page discusses surfacing request errors; "
            "these cases sample error cleanup from selected "
            "async/wrapped dependency callables through "
            "construction and HTTP outcomes.",
        },
        {
            "workflow_id": "exception-handler-after-stack-cache",
            "recipe_path": "tests/fixtures/input-recipes/parity/exception-handler-after-stack-cache.yaml",
            "case_ids": ["fastapi.applications.exception-handler.after-stack-cache"],
            "observation_selectors": [
                "asgi.application_error.exception",
                "asgi.lifespan.application_errors",
                "asgi.lifespan.event_order",
                "asgi.lifespan.shutdown",
                "asgi.lifespan.startup",
                "asgi.lifespan.workload_trace",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page documents exception handling; this case "
            "samples a cached exception-handler registration "
            "after stack initialization, including lifespan, "
            "ASGI error, and HTTP outcomes.",
        },
        {
            "workflow_id": "exception-overrides",
            "recipe_path": "tests/fixtures/input-recipes/parity/exception-overrides.yaml",
            "case_ids": [
                "fastapi.docs.handling-errors.overridden-http-error",
                "fastapi.docs.handling-errors.overridden-validation-error",
                "fastapi.docs.handling-errors.override-success",
                "fastapi.docs.handling-errors.overrides-openapi",
            ],
            "observation_selectors": [
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page documents overriding exception handling; "
            "these cases sample HTTP and validation exception "
            "overrides, success, and the corresponding OpenAPI "
            "response.",
        },
        {
            "workflow_id": "generator-awaitable-protocol",
            "recipe_path": "tests/fixtures/input-recipes/parity/generator-awaitable-protocol.yaml",
            "case_ids": [
                "fastapi.awaitables.generator-protocol.await-method-generator-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.await-method-noniterator-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.genuine-async-bridge-future-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.propagated-future-error-cleanup-recovery",
                "fastapi.awaitables.generator-protocol.unflagged-generator-error-cleanup-recovery",
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
            "scope_note": "The page covers handling errors raised during "
            "request processing; these cases sample dependency "
            "awaitable/generator failures and cleanup through "
            "construction, ASGI, and HTTP outputs.",
        },
        {
            "workflow_id": "handling-errors",
            "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors.yaml",
            "case_ids": [
                "fastapi.docs.handling-errors.custom-exception",
                "fastapi.docs.handling-errors.http-exception-detail",
                "fastapi.docs.handling-errors.http-exception-status",
                "fastapi.docs.handling-errors.openapi",
                "fastapi.docs.handling-errors.starlette-exception",
                "fastapi.docs.handling-errors.success",
                "fastapi.docs.handling-errors.validation-error",
            ],
            "observation_selectors": [
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page’s examples use HTTPException and "
            "validation errors; these cases sample "
            "custom/status/detail errors, success, validation, "
            "and the selected OpenAPI response.",
        },
        {
            "workflow_id": "handling-errors-import-http-exception",
            "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-import-http-exception.yaml",
            "case_ids": ["fastapi.docs.handling-errors.import-http-exception"],
            "observation_selectors": ["python.signature"],
            "scope_note": "This direct API case resolves the documented `fastapi.HTTPException` "
            "root import and compares its public signature. Constructor and HTTP behavior are "
            "covered by separate workflow inputs.",
        },
        {
            "workflow_id": "inherited-exception-handler-registration",
            "recipe_path": "tests/fixtures/input-recipes/parity/inherited-exception-handler-registration.yaml",
            "case_ids": [
                "fastapi.applications.add-exception-handler.custom-exception",
                "fastapi.applications.add-exception-handler.status-code",
                "fastapi.applications.exception-handler.decorator",
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
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page describes exception handlers; these "
            "cases sample handler registration by decorator, "
            "custom exception, and status code through "
            "construction, lifespan, and HTTP outputs.",
        },
        {
            "workflow_id": "next-openapi-response-fields",
            "recipe_path": "tests/fixtures/input-recipes/parity/next-openapi-response-fields.yaml",
            "case_ids": [
                "fastapi.next-openapi-response-fields.late-json-hook-error-public-retry-cache"
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
            ],
            "scope_note": "The page describes HTTP error responses; this "
            "case samples a late response-field JSON hook "
            "retry/error path together with the selected HTTP "
            "and OpenAPI observations.",
        },
        {
            "workflow_id": "openapi-validation-response",
            "recipe_path": "tests/fixtures/input-recipes/parity/openapi-validation-response.yaml",
            "case_ids": [
                "fastapi.openapi-validation-response.automatic-after-declared-responses",
                "fastapi.openapi-validation-response.declared-422-suppresses-automatic",
                "fastapi.openapi-validation-response.declared-4xx-suppresses-automatic",
                "fastapi.openapi-validation-response.declared-default-suppresses-automatic",
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
            "scope_note": "The page covers request-validation errors; these "
            "cases sample when automatic validation responses "
            "are suppressed by declared response entries, "
            "including recorded warnings.",
        },
        {
            "workflow_id": "public-errors-http-websocket-wave",
            "recipe_path": "tests/fixtures/input-recipes/parity/public-errors-http-websocket-wave.yaml",
            "case_ids": [
                "fastapi.public-errors.http.bodyless-status-with-detail",
                "fastapi.public-errors.http.fastapi-json-detail-and-header",
                "fastapi.public-errors.http.starlette-base-detail-and-header",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page explains client-error reporting; these "
            "cases sample FastAPI and Starlette HTTP exception "
            "details plus a bodyless status through HTTP "
            "projections.",
        },
        {
            "workflow_id": "request-validation-body",
            "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-body.yaml",
            "case_ids": [
                "fastapi.docs.handling-errors.body-echo.invalid-input",
                "fastapi.docs.handling-errors.body-echo.openapi",
                "fastapi.docs.handling-errors.body-echo.valid-input",
            ],
            "observation_selectors": [
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "scope_note": "The page documents request-validation errors; "
            "these cases sample valid/invalid body input and "
            "its OpenAPI request schema through HTTP and "
            "schema projections.",
        },
        {
            "workflow_id": "security-api-key-exception-boundary",
            "recipe_path": "tests/fixtures/input-recipes/parity/security-api-key-exception-boundary.yaml",
            "case_ids": ["fastapi.security.api-key-header.fastapi-http-exception-handler-boundary"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page discusses HTTP exception handling; this "
            "case samples the FastAPI HTTPException boundary "
            "for one API-key path through HTTP status, "
            "headers, and body.",
        },
        {
            "workflow_id": "websocket-exception-handler",
            "recipe_path": "tests/fixtures/input-recipes/parity/websocket-exception-handler.yaml",
            "case_ids": ["fastapi.websocket-exception.custom-handler-close"],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "websocket.close_code",
                "websocket.close_reason",
                "websocket.event_order",
                "websocket.messages",
                "websocket.workload_trace",
            ],
            "scope_note": "The page documents handling client errors; this "
            "case samples a custom WebSocket exception "
            "handler’s close result and recorded construction "
            "outcome.",
        },
        {
            "workflow_id": "websocket-validation-handler-wave",
            "recipe_path": "tests/fixtures/input-recipes/parity/websocket-validation-handler-wave.yaml",
            "case_ids": ["fastapi.websocket-validation.custom-handler-close"],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "websocket.close_code",
                "websocket.close_reason",
                "websocket.event_order",
                "websocket.messages",
                "websocket.workload_trace",
            ],
            "scope_note": "The page covers request validation failures; this "
            "case samples a custom WebSocket validation "
            "handler’s close result and recorded construction "
            "outcome.",
        },
    ],
    "tutorial/header-params.md": [
        {
            "workflow_id": "first-asgi-request",
            "recipe_path": "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
            "case_ids": [
                "fastapi.first-slice.create-item-missing-header",
                "fastapi.first-slice.create-item-valid",
                "fastapi.first-slice.openapi",
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
                "openapi.request_schema",
            ],
            "scope_note": "The page documents Header parameter declaration and "
            "validation; these cases sample a missing/valid "
            "header request and OpenAPI request schema through "
            "the listed HTTP/ASGI selectors.",
        },
        {
            "workflow_id": "request-validation-parameters",
            "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-parameters.yaml",
            "case_ids": [
                "fastapi.request-parameters.header.repeated-values",
                "fastapi.request-parameters.header.required-missing",
                "fastapi.request-parameters.header.underscore-alias",
            ],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": "The page explains Header aliases and parameter "
            "conversion; these cases sample repeated values, "
            "missing required input, and underscore aliasing "
            "through HTTP status and body.",
        },
    ],
    "tutorial/metadata.md": [
        {
            "workflow_id": "constructor-openapi-tags",
            "recipe_path": "tests/fixtures/input-recipes/parity/constructor-openapi-tags.yaml",
            "case_ids": ["fastapi.applications.constructor.openapi-tags"],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.status",
                "http.body.bytes",
                "http.status",
                "openapi.document",
            ],
            "scope_note": "The page lists API metadata fields used in OpenAPI; this "
            "case samples constructor OpenAPI tags and the resulting "
            "schema/response.",
        },
        {
            "workflow_id": "docs-openapi-interface",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
            "case_ids": ["fastapi.docs.openapi-interface.tutorial-metadata.openapi-metadata"],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page documents API metadata and documentation URLs; "
            "this case samples its metadata endpoint and generated "
            "OpenAPI paths.",
        },
        {
            "workflow_id": "metadata-tutorial001-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/metadata-tutorial001-upstream.yaml",
            "case_ids": ["fastapi.docs.metadata.tutorial001.openapi-info-fields"],
            "observation_selectors": ["openapi.document"],
            "scope_note": "The page demonstrates title/version/contact/license "
            "metadata; this case samples the generated OpenAPI "
            "information fields.",
        },
    ],
    "tutorial/middleware.md": [
        {
            "workflow_id": "middleware",
            "recipe_path": "tests/fixtures/input-recipes/parity/middleware.yaml",
            "case_ids": [
                "fastapi.middleware.decorator-body-replay",
                "fastapi.middleware.decorator-openapi",
            ],
            "observation_selectors": [
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page describes middleware around requests and "
            "responses; these cases sample decorator middleware "
            "body replay and its OpenAPI/HTTP response "
            "projections.",
        },
        {
            "workflow_id": "middleware-execution-order-wave",
            "recipe_path": "tests/fixtures/input-recipes/parity/middleware-execution-order-wave.yaml",
            "case_ids": ["fastapi.docs.middleware.request-and-response-order"],
            "observation_selectors": [
                "asgi.send.message_types",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page explains request/response middleware "
            "ordering; this case records the order through ASGI "
            "sends and the resulting HTTP response.",
        },
        {
            "workflow_id": "middleware-proxy-static-settings-source-review",
            "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml",
            "case_ids": ["fastapi.middleware-proxy.decorator-middleware"],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.headers",
                "docs.response.status",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page documents adding middleware to a FastAPI "
            "application; this case samples decorator middleware "
            "registration through construction, docs, and HTTP "
            "headers/status.",
        },
    ],
    "tutorial/path-operation-configuration.md": [
        {
            "workflow_id": "docs-openapi-schema",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
            "case_ids": [
                "fastapi.docs.documentation-wave.openapi-schema.path-operation-configuration"
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page describes parameters on "
            "path-operation decorators; this case "
            "samples documented configuration "
            "through the response and selected "
            "OpenAPI paths.",
        },
        {
            "workflow_id": "path-operation-other-verbs-deprecated",
            "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-other-verbs-deprecated.yaml",
            "case_ids": ["fastapi.path-operation.other-verbs-deprecated"],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page explains path-operation "
            "decorator options; this case samples "
            "deprecated other-verb registration "
            "in HTTP status and OpenAPI.",
        },
        {
            "workflow_id": "path-operation-other-verbs-response-descriptions",
            "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-other-verbs-response-descriptions.yaml",
            "case_ids": ["fastapi.path-operation.other-verbs-response-descriptions"],
            "observation_selectors": ["openapi.document", "openapi.paths"],
            "scope_note": "The page documents path-operation "
            "response configuration; this case "
            "samples response descriptions for "
            "other HTTP verbs in the generated "
            "OpenAPI paths.",
        },
        {
            "workflow_id": "path-operation-post-deprecated-isolated",
            "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-post-deprecated-isolated.yaml",
            "case_ids": ["fastapi.path-operation.post-deprecated-isolated"],
            "observation_selectors": ["openapi.document", "openapi.paths"],
            "scope_note": "The page covers path-operation "
            "decorator configuration; this case "
            "samples the deprecated POST option "
            "in the generated OpenAPI paths.",
        },
        {
            "workflow_id": "path-operation-post-response-description-isolated",
            "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-post-response-description-isolated.yaml",
            "case_ids": ["fastapi.path-operation.post-response-description-isolated"],
            "observation_selectors": ["openapi.document", "openapi.paths"],
            "scope_note": "The page covers response metadata on "
            "path operations; this case samples "
            "one POST response description in the "
            "generated OpenAPI paths.",
        },
        {
            "workflow_id": "path-operation-post-status-code-isolated",
            "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-post-status-code-isolated.yaml",
            "case_ids": ["fastapi.path-operation.post-status-code-isolated"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "scope_note": "The page says status_code is "
            "configured on the decorator and "
            "appears in OpenAPI; this case "
            "samples the POST status and schema "
            "paths.",
        },
        {
            "workflow_id": "path-operation-status-code-none-isolated",
            "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-status-code-none-isolated.yaml",
            "case_ids": ["fastapi.path-operation.status-code-none"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "scope_note": "The page documents decorator-level "
            "status_code; this case samples "
            "status_code=None through the HTTP "
            "status and OpenAPI paths.",
        },
    ],
    "tutorial/response-status-code.md": [
        {
            "workflow_id": "response-surface",
            "recipe_path": "tests/fixtures/input-recipes/parity/response-surface.yaml",
            "case_ids": ["fastapi.response.openapi-status-and-media"],
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
            "scope_note": "The page says status_code sets both the HTTP "
            "response and its OpenAPI documentation; this "
            "case samples status, media, response "
            "bytes/headers, and the generated schema.",
        }
    ],
    "tutorial/schema-extra-example.md": [
        {
            "workflow_id": "docs-openapi-schema",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
            "case_ids": ["fastapi.docs.documentation-wave.openapi-schema.schema-extra-example"],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page demonstrates extra examples in "
            "generated JSON Schema; this case samples the "
            "route response and selected OpenAPI "
            "schema/path projections.",
        }
    ],
    "tutorial/security/index.md": [
        {
            "workflow_id": "docs-security-schemes",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-security-schemes.yaml",
            "case_ids": [
                "fastapi.docs.security-schemes.cookie-api-key",
                "fastapi.docs.security-schemes.query-api-key",
            ],
            "observation_selectors": [
                "docs.response.body.bytes",
                "docs.response.status",
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.security",
            ],
            "scope_note": "The page introduces FastAPI security tools; these "
            "cases sample cookie and query API-key responses "
            "and their OpenAPI security schemes.",
        }
    ],
    "tutorial/security/oauth2-jwt.md": [
        {
            "workflow_id": "security-tutorial004-auth-input-gap-wave",
            "recipe_path": "tests/fixtures/input-recipes/parity/security-tutorial004-auth-input-gap-wave.yaml",
            "case_ids": [
                "fastapi.security-tutorial004.test-no-token",
                "fastapi.security-tutorial004.test-openapi-schema",
                "fastapi.security-tutorial004.test-token",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.security",
            ],
            "scope_note": "The page documents password authentication "
            "with bearer JWTs; these cases sample "
            "absent/valid-token responses and the "
            "generated OpenAPI security scheme.",
        }
    ],
    "tutorial/server-sent-events.md": [
        {
            "workflow_id": "docs-http-behaviors",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml",
            "case_ids": ["fastapi.docs.documentation-wave.http-behaviors.server-sent-events"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page describes HTTP Server-Sent Events "
            "streaming; this case samples one SSE "
            "response’s body, headers, and status.",
        },
        {
            "workflow_id": "server-sent-events-tutorial001-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial001-upstream.yaml",
            "case_ids": ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page documents streaming SSE routes; this "
            "case samples the tutorial route streams "
            "through HTTP body, headers, and status.",
        },
        {
            "workflow_id": "server-sent-events-tutorial002-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial002-upstream.yaml",
            "case_ids": ["fastapi.tutorial.server-sent-events.tutorial002.event-fields"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page describes SSE event fields; this case "
            "samples event-field encoding in the HTTP "
            "stream body and response metadata.",
        },
        {
            "workflow_id": "server-sent-events-tutorial003-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial003-upstream.yaml",
            "case_ids": ["fastapi.tutorial.server-sent-events.tutorial003.raw-log-data"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page shows raw data in an SSE event; this "
            "case samples the streamed response body and "
            "HTTP metadata.",
        },
        {
            "workflow_id": "server-sent-events-tutorial004-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
            "case_ids": ["fastapi.tutorial.server-sent-events.tutorial004.resume-stream"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page documents resuming an SSE stream; "
            "this case samples the resume response body and "
            "HTTP metadata.",
        },
        {
            "workflow_id": "server-sent-events-tutorial005-upstream",
            "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial005-upstream.yaml",
            "case_ids": ["fastapi.tutorial.server-sent-events.tutorial005.post-chat-stream"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page documents posting chat input and "
            "streaming SSE output; this case samples the "
            "streamed HTTP response body and metadata.",
        },
    ],
    "tutorial/sql-databases.md": [
        {
            "workflow_id": "docs-sql-databases-fake-dependency",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-sql-databases-fake-dependency.yaml",
            "case_ids": [
                "fastapi.docs.sql-databases.fake-yield.create-and-cleanup",
                "fastapi.docs.sql-databases.fake-yield.invalid-request",
                "fastapi.docs.sql-databases.fake-yield.openapi-models",
            ],
            "observation_selectors": [
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "scope_note": "The page uses SQLModel with FastAPI; these "
            "fake-dependency cases sample create/cleanup, "
            "invalid request handling, and OpenAPI models "
            "without claiming database-library behavior.",
        }
    ],
    "tutorial/static-files.md": [
        {
            "workflow_id": "docs-static-files-mount-boundary",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-static-files-mount-boundary.yaml",
            "case_ids": ["fastapi.docs.static-files.mount-parent-openapi-docs-boundary"],
            "observation_selectors": [
                "docs.response.body.bytes",
                "docs.response.headers",
                "docs.response.status",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page documents mounting StaticFiles at a path; "
            "this case samples the parent application’s "
            "route/OpenAPI boundary and selected static "
            "response.",
        },
        {
            "workflow_id": "middleware-proxy-static-settings-source-review",
            "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml",
            "case_ids": ["fastapi.middleware-proxy.static-files"],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.status",
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": "The page describes serving a directory with "
            "StaticFiles; this case samples static-file mounting "
            "through construction, HTTP, and parent OpenAPI "
            "observations.",
        },
    ],
    "tutorial/stream-json-lines.md": [
        {
            "workflow_id": "docs-http-behaviors",
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml",
            "case_ids": ["fastapi.docs.documentation-wave.http-behaviors.stream-json-lines"],
            "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
            "scope_note": "The page introduces JSON Lines as incremental "
            "HTTP streaming; this case samples one streamed "
            "response body, headers, and status.",
        },
        {
            "workflow_id": "stream-cancellation",
            "recipe_path": "tests/fixtures/input-recipes/parity/stream-cancellation.yaml",
            "case_ids": ["fastapi.stream-cancellation.jsonl-async-generator"],
            "observation_selectors": [
                "asgi.cancellation.cancelled_caught",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": "The page describes producing a JSON Lines "
            "stream incrementally; this case samples "
            "async-generator cancellation and the resulting "
            "response headers/status.",
        },
    ],
}
