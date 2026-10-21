"""FastAPI page workflow links requiring independent source selectors."""

DOC_PAGE_CASE_LINK_COMPLETIONS_WAVE_L = {
    "how-to/configure-swagger-ui.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/application-attributes.yaml",
            "case_ids": [
                "fastapi.application.attributes.swagger-ui-parameters-reassignment-after-construction"
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.headers.ordered",
                "http.status",
            ],
            "scope_note": (
                "The application reassigns Swagger UI parameters after construction, then "
                "compares the exact `/docs` response status, ordered headers, and body bytes."
            ),
        },
    ],
    "advanced/openapi-webhooks.md": [
        {
            "recipe_path": ("tests/fixtures/input-recipes/parity/webhooks-truthy-non-router.yaml"),
            "case_ids": ["fastapi.webhooks.truthy-non-router.openapi-error"],
            "observation_selectors": [
                "asgi.application_error.exception",
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
            ],
            "scope_note": (
                "The OpenAPI request uses the documented webhook application surface. The "
                "selected plain-object failure is established by the pinned FastAPI source; "
                "the documentation page itself does not specify arbitrary webhook values."
            ),
        },
    ],
    "how-to/extending-openapi.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-openapi-extending-openapi-20261015.yaml"
            ),
            "case_ids": [
                "fastapi.docs.extending-openapi.normal-schema-route",
                "fastapi.docs.extending-openapi.custom-logo-schema",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "The independent default and customized schema cases observe construction, "
                "the schema endpoint status, info metadata, route paths, and the custom logo "
                "extension. Browser rendering and unselected get_openapi "
                "options remain outside scope."
            ),
        },
    ],
    "tutorial/body-fields.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/body-fields-schema-evidence-20261015.yaml"
            ),
            "case_ids": ["fastapi.body-fields.field-json-schema-metadata"],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "scope_note": (
                "The selected pointers observe the embedded request-body reference, its component "
                "property, and the model's maximum-length and positive-value field schemas. "
                "Other Pydantic field metadata is unexercised."
            ),
        },
    ],
    "tutorial/dependencies/index.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.dependencies.tutorial-review.basic-defaults",
                "fastapi.dependencies.tutorial-review.basic-partial-query",
                "fastapi.dependencies.tutorial-review.openapi-projection",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "Independent requests sample default and supplied query values passed through "
                "a callable dependency; the OpenAPI action selects its declared parameter schema. "
                "Other dependency signatures are unexercised."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/dependency-tutorial005-query-cookie-fallback.yaml"
            ),
            "case_ids": [
                "fastapi.dependencies.tutorial005.query-cookie.fallback",
                "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
                "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
                "fastapi.dependencies.tutorial005.query-cookie.openapi-parameters",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "The nested dependency graph is observed through query "
                "precedence, cookie fallback, "
                "absent values, and selected generated parameters. Application fallback logic "
                "supplies the workload stimulus; it is not a FastAPI API claim."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/dependency-dynamic-cache-policy.yaml"
            ),
            "case_ids": [
                "fastapi.dependencies.dynamic-cache-policy.nested-sync-parent-async-child"
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "The independent nested synchronous-parent/asynchronous-child case observes "
                "construction and HTTP responses across two requests. The narrower section "
                "mapping selects the request actions; timing and other dependency graphs remain "
                "unexercised."
            ),
        },
    ],
    "tutorial/dependencies/classes-as-dependencies.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.dependencies.tutorial-review.catalog-default-window",
                "fastapi.dependencies.tutorial-review.catalog-custom-window",
            ],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": (
                "Default and explicit query windows exercise class dependency construction and "
                "delivery to the endpoint. Other constructor signatures and "
                "annotations are unexercised."
            ),
        },
    ],
    "tutorial/dependencies/dependencies-in-path-operation-decorators.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/dependency-declarations-section-review-20261015.yaml"
            ),
            "case_ids": [
                ""
                "fastapi.docs.dependency-declarations.section-review.decorator-return-value-not-injected"
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
            ],
            "scope_note": (
                "A successful request plus public trace readback observes "
                "both declared dependencies "
                "and a non-null discarded return value. The case also observes app construction."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.dependencies.tutorial-review.headers-missing",
                "fastapi.dependencies.tutorial-review.headers-invalid-token",
                "fastapi.dependencies.tutorial-review.headers-invalid-key",
            ],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "scope_note": (
                "Three HTTP requests sample missing required headers and the two independent "
                "dependency error branches. Successful dependency return "
                "behavior has a separate case."
            ),
        },
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/bigger-applications-sections-20261015.yaml"
            ),
            "case_ids": ["fastapi.docs.bigger-applications.main-router-composition"],
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
            "scope_note": (
                "The independently authored router-composition workflow observes construction, "
                "HTTP responses, and dependency parameter schemas. Its narrower group-dependency "
                "section mapping selects three items-route actions for accepted, missing, and "
                "rejected headers; other router configurations remain unexercised."
            ),
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
            "case_ids": [
                "fastapi.docs.documentation-wave.dependencies-security.global-dependencies"
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
                "The request and OpenAPI projection sample one application-wide dependency "
                "through one route. Other routes and dependency types remain unexercised."
            ),
        },
    ],
    "advanced/websockets.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/websockets-cli-startup.yaml",
            "case_ids": ["fastapi.cli.process.websockets-startup-readiness"],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "process.exit_code",
            ],
            "scope_note": (
                "Partial independent process sample; observes FastAPI CLI startup and HTTP "
                "readiness for an app that declares a WebSocket route. It does not connect "
                "a WebSocket client or claim browser behavior."
            ),
        },
    ],
    "tutorial/body-nested-models.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-example-wave-f-nested-bodies.yaml"
            ),
            "case_ids": [
                "fastapi.docs-example-wave-f.nested-body.list-tags-valid",
                "fastapi.docs-example-wave-f.nested-body.integer-float-map-key-types",
                "fastapi.docs-example-wave-f.nested-body.set-tags-deduplicated",
                "fastapi.docs-example-wave-f.nested-body.optional-image-present",
                "fastapi.docs-example-wave-f.nested-body.http-url-invalid",
                "fastapi.docs-example-wave-f.nested-body.optional-image-list-present",
                "fastapi.docs-example-wave-f.nested-body.offer-nested-items",
                "fastapi.docs-example-wave-f.nested-body.top-level-image-list",
                "fastapi.docs-example-wave-f.nested-body.integer-float-map",
                "fastapi.docs-example-wave-f.nested-body.bare-list-values-preserved",
            ],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "scope_note": (
                "All ten listed cases cite this exact page and each sends one HTTP body plus "
                "one /openapi.json request. Their action union selects the response and "
                "request-body schema pointers, including openapi.request_schema. No other "
                "tutorial behavior is claimed."
            ),
        },
    ],
    "tutorial/extra-models.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml"
            ),
            "case_ids": [
                "fastapi.extra-models.tutorial001-flat-user-models",
                "fastapi.extra-models.tutorial002-inherited-user-models",
                "fastapi.extra-models.tutorial003-union-response-model",
                "fastapi.extra-models.tutorial004-typed-list-response",
                "fastapi.extra-models.tutorial005-typed-map-response",
            ],
            "observation_selectors": [
                "construction.exception_class",
                "construction.exception_message",
                "construction.outcome",
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "The five independently authored cases exercise flat and inherited input/output "
                "models, a response union, a typed response list, and a typed response mapping. "
                "They observe construction, returned HTTP values, and selected response-schema "
                "projections. Other Pydantic shapes and external database behavior are outside "
                "these inputs."
            ),
        },
    ],
    "tutorial/schema-extra-example.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml"
            ),
            "case_ids": [
                "fastapi.schema-extra-example.model-schema-extra",
                "fastapi.schema-extra-example.field-examples",
                "fastapi.schema-extra-example.body-examples-list",
                "fastapi.schema-extra-example.body-examples-several",
                "fastapi.schema-extra-example.openapi-example-objects",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "scope_note": (
                "The five cases observe request acceptance and selected OpenAPI model, field, "
                "body-example, and named media-example projections. Request response bodies "
                "and browser rendering are not selected by this workflow."
            ),
        },
    ],
    "tutorial/sql-databases.md": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/sql-databases-sections-20261015.yaml"
            ),
            "case_ids": [
                "fastapi.docs.sql-databases.multiple-models.create-public",
                "fastapi.docs.sql-databases.multiple-models.invalid-create",
                "fastapi.docs.sql-databases.multiple-models.openapi",
                "fastapi.docs.sql-databases.multiple-models.read-public-list",
                "fastapi.docs.sql-databases.multiple-models.update-sparse",
                "fastapi.docs.sql-databases.single-model.create-hero",
                "fastapi.docs.sql-databases.single-model.invalid-hero",
                "fastapi.docs.sql-databases.single-model.openapi",
            ],
            "observation_selectors": [
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
                "openapi.paths",
                "openapi.request_schema",
                "validation.error_class",
                "validation.error_details",
            ],
            "scope_note": (
                "The eight listed cases sample the single-model and multiple-model request, "
                "validation, response-model, and OpenAPI behavior described on this page. "
                "They observe app construction, selected HTTP responses and validation "
                "details, and the selected OpenAPI projections; they do not claim SQLModel, "
                "SQLAlchemy, SQLite, database persistence, or CLI behavior."
            ),
        },
    ],
}
