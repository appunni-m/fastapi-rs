"""Additive review mappings for the 2026-10-15 custom docs UI workflows.

These entries extend existing tutorial001/tutorial002 reviews. The central
registry must merge their workflow cases and supporting source spans into the
existing per-example records instead of replacing those records.
"""

DOC_EXAMPLE_CITATION_UI_CLIENTS_20261015_EXTENSION = {
    "docs_src/custom_docs_ui/tutorial001_py310.py": {
        "rationale": (
            "The custom-CDN case samples the tutorial's configured Swagger and ReDoc HTML, "
            "OAuth redirect helper, enabled OpenAPI path, and matching users route. Its "
            "selectors describe case-level observations, so response-byte/status selectors "
            "also occur on the users action. The automatic-docs-disabled case reuses only "
            "docs_url=None and redoc_url=None, without the tutorial's replacement /docs and "
            "/redoc handlers; its misses therefore sample suppression of automatic routes, "
            "not the complete tutorial app. The OpenAPI endpoint remains enabled. Neither "
            "case fetches or executes CDN assets, renders a browser UI, or exercises an "
            "OAuth provider flow. The pinned tutorial tests separately assert the CDN URL "
            "strings, redirect helper response, ReDoc URL, and users route response."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                "start_line": 8,
                "end_line": 8,
                "role": "disable automatic Swagger UI and ReDoc route registration",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                "start_line": 11,
                "end_line": 19,
                "role": "custom Swagger UI route with the documented CDN asset URLs",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                "start_line": 22,
                "end_line": 24,
                "role": "custom OAuth2 redirect helper route",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                "start_line": 27,
                "end_line": 33,
                "role": "custom ReDoc route with its documented CDN asset URL",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                "start_line": 36,
                "end_line": 38,
                "role": "documented users path operation represented in the OpenAPI sample",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": (
                    "tests/fixtures/input-recipes/parity/docs-ui-clients-sections-20261015.yaml"
                ),
                "case_ids": ["fastapi.docs.ui-clients.custom-cdn"],
                "observation_selectors": [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
            },
            {
                "recipe_path": (
                    "tests/fixtures/input-recipes/parity/docs-ui-clients-sections-20261015.yaml"
                ),
                "case_ids": ["fastapi.docs.ui-clients.automatic-docs-disabled"],
                "observation_selectors": [
                    "docs.response.status",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
            },
        ],
    },
    "docs_src/custom_docs_ui/tutorial002_py310.py": {
        "rationale": (
            "The self-hosted case samples the tutorial's /static mount, generated Swagger "
            "and ReDoc HTML configured with local asset paths, and responses for three "
            "synthetic files. Those file bodies are input markers, not vendor distributions; "
            "the case does not establish real-asset contents, offline browser rendering, or "
            "interaction. Its case-level HTTP selectors also cover the helper, OpenAPI, and "
            "users actions, but this added review relies on the custom-docs and static-file "
            "responses. The pinned tutorial tests assert the local asset URLs in the emitted "
            "HTML and the OAuth redirect helper response."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/custom_docs_ui/tutorial002_py310.py",
                "start_line": 7,
                "end_line": 11,
                "role": "StaticFiles import, disabled automatic docs, and /static mount",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial002_py310.py",
                "start_line": 14,
                "end_line": 22,
                "role": "Swagger UI route configured with locally served JavaScript and CSS",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial002_py310.py",
                "start_line": 30,
                "end_line": 36,
                "role": "ReDoc route configured with its locally served JavaScript asset",
            },
            {
                "path": "docs_src/custom_docs_ui/tutorial002_py310.py",
                "start_line": 39,
                "end_line": 41,
                "role": "documented users path operation represented in the OpenAPI sample",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": (
                    "tests/fixtures/input-recipes/parity/docs-ui-clients-sections-20261015.yaml"
                ),
                "case_ids": ["fastapi.docs.ui-clients.custom-self-hosted"],
                "observation_selectors": [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
            }
        ],
    },
}
