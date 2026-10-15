"""FastAPI page workflow links requiring independent source selectors."""

DOC_PAGE_CASE_LINK_COMPLETIONS_WAVE_L = {
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
