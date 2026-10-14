"""Reviewed exact selectors for documentation page workflow-case links."""

# Keys use (page path relative to docs/en/docs, recipe path, linked case IDs).
# Selector lists are the exact sorted projection of those materialized cases.
DOC_PAGE_CASE_SELECTOR_OVERRIDES = {
    (
        "advanced/additional-responses.md",
        "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml",
        ("fastapi.additional-response-openapi-wave.media-content.test-openapi-schema",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "advanced/behind-a-proxy.md",
        "tests/fixtures/input-recipes/parity/behind-proxy-tutorial002-upstream.yaml",
        (
            "fastapi.behind-proxy.tutorial002.app-root-path",
            "fastapi.behind-proxy.tutorial002.openapi-servers",
        ),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
    },
    (
        "advanced/behind-a-proxy.md",
        "tests/fixtures/input-recipes/parity/behind-proxy-tutorial003-upstream.yaml",
        (
            "fastapi.behind-proxy.tutorial003.app-root-path",
            "fastapi.behind-proxy.tutorial003.openapi-servers",
        ),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
    },
    (
        "advanced/behind-a-proxy.md",
        "tests/fixtures/input-recipes/parity/behind-proxy-tutorial004-upstream.yaml",
        (
            "fastapi.behind-proxy.tutorial004.app-root-path",
            "fastapi.behind-proxy.tutorial004.openapi-servers",
        ),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
    },
    (
        "advanced/json-base64-bytes.md",
        "tests/fixtures/input-recipes/parity/json_base64_bytes.yaml",
        ("fastapi.docs.json-base64-bytes.input-output-and-schema",),
    ): {
        "observation_selectors": [
            "docs.response.body.bytes",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
    },
    (
        "advanced/path-operation-advanced-configuration.md",
        "tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial003-upstream.yaml",
        ("fastapi.path-operation-advanced-configurations.tutorial003",),
    ): {
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "advanced/security/oauth2-scopes.md",
        "tests/fixtures/input-recipes/parity/security-dependencies.yaml",
        (
            "fastapi.docs.security.bearer-required-valid",
            "fastapi.docs.security.openapi",
        ),
    ): {
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
    },
    (
        "advanced/security/oauth2-scopes.md",
        "tests/fixtures/input-recipes/parity/security-scopes-dont-propagate-openapi-source-review.yaml",
        ("fastapi.security.scopes-dont-propagate.nested-openapi-sibling-scopes",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
    },
    (
        "advanced/sub-applications.md",
        "tests/fixtures/input-recipes/parity/sub_applications.yaml",
        ("fastapi.docs.sub-applications.mount-and-own-openapi",),
    ): {
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
    },
    (
        "advanced/using-request-directly.md",
        "tests/fixtures/input-recipes/parity/using_request_directly.yaml",
        ("fastapi.docs.using-request-directly.client-host",),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "how-to/authentication-error-status-code.md",
        "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
        ("fastapi.docs.documentation-wave.dependencies-security.authentication-error-status",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
    },
    (
        "how-to/conditional-openapi.md",
        "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
        ("fastapi.docs.openapi-interface.how-to-conditional-openapi.disabled-schema-endpoint",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "how-to/extending-openapi.md",
        "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
        ("fastapi.docs.openapi-interface.how-to-extending-openapi.custom-openapi-fields",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "how-to/extending-openapi.md",
        "tests/fixtures/input-recipes/parity/sub_applications.yaml",
        ("fastapi.docs.sub-applications.route-list-after-mount",),
    ): {
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
    },
    (
        "python-types.md",
        "tests/fixtures/input-recipes/parity/docs-types-frontend.yaml",
        ("fastapi.docs.reference-wave.types.typed-path-and-query-inputs",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "reference/dependencies.md",
        "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
        ("fastapi.docs.reference-wave.http.security-dependency",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
    },
    (
        "reference/fastapi.md",
        "tests/fixtures/input-recipes/parity/docs-reference-openapi.yaml",
        ("fastapi.docs.reference-wave.openapi.fastapi-application-settings",),
    ): {
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
        "scope_note": (
            "This link covers the settings-and-route example: it observes the route response and "
            "application OpenAPI endpoint. The schema example is not a complete OpenAPI contract."
        ),
    },
    (
        "reference/fastapi.md",
        "tests/fixtures/input-recipes/parity/frontend-dependency-source-wave.yaml",
        ("fastapi.frontend.dependencies-override",),
    ): {
        "observation_selectors": [
            "construction.exception_class",
            "construction.exception_message",
            "construction.outcome",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "This link covers one frontend mount with a FastAPI dependency override through HTTP. The "
            "linked case also records construction outcomes."
        ),
    },
    (
        "reference/fastapi.md",
        "tests/fixtures/input-recipes/parity/inherited-exception-handler-registration.yaml",
        ("fastapi.applications.exception-handler.decorator",),
    ): {
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
        "scope_note": (
            "This link covers decorator-based registration of one custom exception handler and the "
            "selected HTTP response. The case also records construction and ASGI lifespan outcomes."
        ),
    },
    (
        "reference/fastapi.md",
        "tests/fixtures/input-recipes/parity/instance-openapi-version.yaml",
        ("fastapi.instance-openapi-version.mutated-field",),
    ): {
        "observation_selectors": [
            "construction.exception_class",
            "construction.exception_message",
            "construction.outcome",
            "docs.response.status",
            "http.status",
            "openapi.document",
        ],
        "scope_note": (
            "This link mutates the FastAPI instance OpenAPI version and observes the resulting schema. "
            "The linked case also records construction outcomes."
        ),
    },
    (
        "reference/fastapi.md",
        "tests/fixtures/input-recipes/parity/middleware.yaml",
        (
            "fastapi.middleware.decorator-openapi",
            "fastapi.middleware.decorator-body-replay",
        ),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "reference/fastapi.md",
        "tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml",
        ("fastapi.lifecycle.router-events-legacy",),
    ): {
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
            "This link covers legacy startup and shutdown callbacks, their FastAPI lifecycle and request "
            "effects, and deprecation warnings. The case also records construction outcomes; modern "
            "lifespan configuration is outside this link."
        ),
    },
    (
        "reference/parameters.md",
        "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
        ("fastapi.docs.reference-wave.http.parameter-source-matrix",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "reference/uploadfile.md",
        "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml",
        ("fastapi.docs.reference-wave.asgi.uploadfile-multipart",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
    },
    (
        "tutorial/bigger-applications.md",
        "tests/fixtures/input-recipes/parity/routing-surface.yaml",
        (
            "fastapi.routing.include-router-prefix",
            "fastapi.routing.openapi-paths",
        ),
    ): {
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
    },
    (
        "tutorial/body-fields.md",
        "tests/fixtures/input-recipes/parity/body-fields-doc-tutorial001-review.yaml",
        (
            "fastapi.docs-example.body-fields.tutorial001.embedded-model-valid",
            "fastapi.docs-example.body-fields.tutorial001.embedded-model-invalid-amount",
            "fastapi.docs-example.body-fields.tutorial001.openapi-embedded-schema",
        ),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
    },
    (
        "tutorial/body-fields.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-body-fields.body-fields",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/body-multiple-params.md",
        "tests/fixtures/input-recipes/parity/body-surface.yaml",
        (
            "fastapi.body.multiple-values-valid",
            "fastapi.body.multiple-values-invalid",
            "fastapi.body.optional-model-absent",
            "fastapi.body.optional-model-present",
            "fastapi.body.openapi-schemas",
        ),
    ): {
        "observation_selectors": [
            "asgi.send.message_types",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
    },
    (
        "tutorial/body-nested-models.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-body-nested-models.nested-body",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/body-updates.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-body-updates.partial-update",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/body.md",
        "tests/fixtures/input-recipes/parity/body-surface.yaml",
        (
            "fastapi.body.embedded-scalar-valid",
            "fastapi.body.embedded-scalar-missing",
            "fastapi.body.embedded-list-valid",
            "fastapi.body.openapi-schemas",
        ),
    ): {
        "observation_selectors": [
            "asgi.send.message_types",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
    },
    (
        "tutorial/body.md",
        "tests/fixtures/input-recipes/parity/body-tutorial003-model-upstream.yaml",
        (
            "fastapi.body.tutorial003.complete-model",
            "fastapi.body.tutorial003.optional-model-fields-absent",
            "fastapi.body.tutorial003.required-model-fields-missing",
            "fastapi.body.tutorial003.openapi-operation-and-model",
        ),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/body.md",
        "tests/fixtures/input-recipes/parity/body-tutorial004-model-upstream.yaml",
        (
            "fastapi.body.tutorial004.complete-model",
            "fastapi.body.tutorial004.optional-model-fields-absent",
            "fastapi.body.tutorial004.required-model-fields-missing",
            "fastapi.body.tutorial004.openapi-operation-and-model",
        ),
    ): {
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/body.md",
        "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
        (
            "fastapi.first-slice.create-item-invalid",
            "fastapi.first-slice.openapi",
        ),
    ): {
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
    },
    (
        "tutorial/cookie-param-models.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-cookie-param-models.cookie-model",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/dependencies/classes-as-dependencies.md",
        "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
        ("fastapi.docs.documentation-wave.dependencies-security.classes-as-dependencies",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/dependencies/dependencies-in-path-operation-decorators.md",
        "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
        ("fastapi.docs.documentation-wave.dependencies-security.path-operation-dependencies",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
        (
            "fastapi.dependencies.tutorial008b.default-parameter-exception-translation",
            "fastapi.dependencies.tutorial008b.annotated-parameter-exception-translation",
            "fastapi.dependencies.tutorial008c.suppressed-yield-exception",
            "fastapi.dependencies.tutorial008d.reraised-yield-exception",
        ),
    ): {
        "observation_selectors": [
            "asgi.application_error.exception",
            "construction.exception_class",
            "construction.exception_message",
            "construction.outcome",
            "http.body.bytes",
            "http.status",
            "validation.error_class",
        ],
    },
    (
        "tutorial/dependencies/global-dependencies.md",
        "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
        ("fastapi.docs.documentation-wave.dependencies-security.global-dependencies",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/dependencies/index.md",
        "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
        (
            "fastapi.first-slice.create-item-valid",
            "fastapi.first-slice.openapi",
        ),
    ): {
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
    },
    (
        "tutorial/extra-data-types.md",
        "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
        ("fastapi.docs.documentation-wave.openapi-schema.extra-data-types",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/extra-models.md",
        "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
        ("fastapi.docs.documentation-wave.openapi-schema.extra-models",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/header-param-models.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-header-param-models.header-model",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/path-params-numeric-validations.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        (
            "fastapi.docs.request-schema.tutorial-path-params-numeric-validations.numeric-path-boundary",
            "fastapi.docs.request-schema.path-params-numeric-validations.tutorial005-annotated",
            "fastapi.docs.request-schema.path-params-numeric-validations.tutorial006-annotated",
        ),
    ): {
        "observation_selectors": [
            "docs.response.body.bytes",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/path-params.md",
        "tests/fixtures/input-recipes/parity/routing-surface.yaml",
        (
            "fastapi.routing.include-router-prefix",
            "fastapi.routing.path-converter",
            "fastapi.routing.path-parameter-invalid",
            "fastapi.routing.openapi-paths",
        ),
    ): {
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
    },
    (
        "tutorial/query-param-models.md",
        "tests/fixtures/input-recipes/parity/query-param-models.yaml",
        (
            "fastapi.query-param-models.grouped-repeated-list",
            "fastapi.query-param-models.grouped-defaults",
            "fastapi.query-param-models.grouped-validation-invalid",
            "fastapi.query-param-models.openapi-query-parameters",
        ),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/query-params-str-validations.md",
        "tests/fixtures/input-recipes/parity/array-items-query-wire.yaml",
        (
            "fastapi.openapi-array-items-query-wire.required-list",
            "fastapi.openapi-array-items-query-wire.required-sequence",
        ),
    ): {
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
    },
    (
        "tutorial/query-params-str-validations.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-query-params-str-validations.query-boundary",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/query-params-str-validations.md",
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        (
            "fastapi.docs-example.query-params-str-validations.tutorial002",
            "fastapi.docs-example.query-params-str-validations.tutorial003",
            "fastapi.docs-example.query-params-str-validations.tutorial015",
        ),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/query-params-str-validations.md",
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-exclude-schema-examples.yaml",
        ("fastapi.docs-example.query-params-str-validations.tutorial014",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/query-params-str-validations.md",
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-pattern-examples.yaml",
        (
            "fastapi.docs-example.query-params-str-validations.tutorial004",
            "fastapi.docs-example.query-params-str-validations.tutorial010",
        ),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/request-form-models.md",
        "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
        ("fastapi.docs.request-schema.tutorial-request-form-models.form-model",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
    },
    (
        "tutorial/response-model.md",
        "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
        (
            "fastapi.first-slice.create-item-valid",
            "fastapi.first-slice.openapi",
        ),
    ): {
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
    },
    (
        "tutorial/response-model.md",
        "tests/fixtures/input-recipes/parity/response-model-serialization.yaml",
        (
            "fastapi.response-model.include.nested",
            "fastapi.response-model.exclude.nested",
            "fastapi.response-model.exclude-unset.explicit-null",
            "fastapi.response-model.exclude-defaults.explicit-defaults",
            "fastapi.response-model.alias.default-by-alias",
            "fastapi.response-model.alias.field-name-output",
            "fastapi.response-model.validation.missing-output-field",
        ),
    ): {
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "validation.error_class",
        ],
    },
    (
        "tutorial/security/first-steps.md",
        "tests/fixtures/input-recipes/parity/security-dependencies.yaml",
        (
            "fastapi.docs.security.bearer-required-missing",
            "fastapi.docs.security.bearer-required-valid",
            "fastapi.docs.security.bearer-required-wrong-scheme",
            "fastapi.docs.security.openapi",
        ),
    ): {
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
    },
    (
        "tutorial/security/get-current-user.md",
        "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
        ("fastapi.docs.documentation-wave.dependencies-security.current-user",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
    },
    (
        "tutorial/security/simple-oauth2.md",
        "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
        ("fastapi.docs.documentation-wave.dependencies-security.simple-oauth2-token-form",),
    ): {
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
    },
}
