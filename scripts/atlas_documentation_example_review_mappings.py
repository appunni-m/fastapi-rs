"""Reviewed, exact workflow links for selected FastAPI documentation examples.

The `upstream_documentation_example` evidence kind binds a case to one exact
`docs_src` file. These links remain partial: they describe only the listed
case IDs and observation selectors, not the entire example or documentation
page.
"""

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS = {
    "docs_src/behind_a_proxy/tutorial002_py310.py": {
        "rationale": (
            "FastAPI 0.141.1 configures this app with root_path=/api/v1. The listed input cases "
            "request /app, read the resulting root_path response, and inspect the selected "
            "OpenAPI server document. They do not cover proxy-header processing or deployment "
            "server behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/behind_a_proxy/tutorial002_py310.py",
                "start_line": 1,
                "end_line": 8,
                "role": "documented root_path app and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/behind-proxy-tutorial002-upstream.yaml",
                "case_ids": ["fastapi.behind-proxy.tutorial002.app-root-path"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-root-path-source-review.yaml",
                "case_ids": ["fastapi.middleware-proxy.proxy-app-root-path"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                ],
            },
        ],
    },
    "docs_src/behind_a_proxy/tutorial003_py310.py": {
        "rationale": (
            "FastAPI 0.141.1 configures root_path plus explicit staging and production servers. "
            "The listed input cases observe the /app root_path response and the generated "
            "OpenAPI server list. They do not cover proxy-header processing or deployment "
            "server behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/behind_a_proxy/tutorial003_py310.py",
                "start_line": 1,
                "end_line": 14,
                "role": "documented configured servers, root_path, and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/behind-proxy-tutorial003-upstream.yaml",
                "case_ids": ["fastapi.behind-proxy.tutorial003.app-root-path"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-root-path-source-review.yaml",
                "case_ids": ["fastapi.middleware-proxy.proxy-root-path-with-servers"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                ],
            },
        ],
    },
    "docs_src/behind_a_proxy/tutorial004_py310.py": {
        "rationale": (
            "FastAPI 0.141.1 configures root_path, explicit servers, and "
            "root_path_in_servers=False. The listed input cases observe the /app root_path "
            "response and selected OpenAPI server paths. They do not cover proxy-header "
            "processing or deployment server behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/behind_a_proxy/tutorial004_py310.py",
                "start_line": 1,
                "end_line": 15,
                "role": "documented configured servers, root_path, and root_path_in_servers",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/behind-proxy-tutorial004-upstream.yaml",
                "case_ids": ["fastapi.behind-proxy.tutorial004.app-root-path"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-root-path-source-review.yaml",
                "case_ids": ["fastapi.middleware-proxy.proxy-root-path-without-auto-server"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                ],
            },
        ],
    },
    "docs_src/settings/app02_an_py310/main.py": {
        "rationale": (
            "The pinned example injects Settings with Annotated and Depends. The input case "
            "observes the dependency-override route response only; Pydantic Settings parsing, "
            "environment loading, caching, and TestClient mechanics are outside this mapping."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/settings/app02_an_py310/main.py",
                "start_line": 1,
                "end_line": 22,
                "role": "documented Annotated dependency and /info response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-settings-injection.yaml",
                "case_ids": ["fastapi.docs.settings.dependency-override"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/settings/app02_an_py310/test_main.py": {
        "rationale": (
            "The pinned test installs a FastAPI dependency override and checks /info. The input "
            "case directly observes that route response; TestClient mechanics and the full "
            "Pydantic Settings contract are not covered."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/settings/app02_an_py310/test_main.py",
                "start_line": 1,
                "end_line": 23,
                "role": "documented dependency override and /info assertion",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-settings-injection.yaml",
                "case_ids": ["fastapi.docs.settings.dependency-override"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/settings/app02_py310/main.py": {
        "rationale": (
            "The pinned non-Annotated example injects Settings with Depends. The input case "
            "observes generic dependency replacement and the response body/status only; it "
            "does not exercise Pydantic Settings parsing, environment loading, or caching."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/settings/app02_py310/main.py",
                "start_line": 1,
                "end_line": 21,
                "role": "documented Settings dependency and /info response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml",
                "case_ids": ["fastapi.middleware-proxy.settings-dependency-override"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/settings/app02_py310/test_main.py": {
        "rationale": (
            "The pinned test installs a FastAPI dependency override and calls /info through "
            "TestClient. The input case observes generic dependency replacement and the route "
            "response only; TestClient mechanics and Pydantic Settings behavior are not covered."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/settings/app02_py310/test_main.py",
                "start_line": 1,
                "end_line": 23,
                "role": "documented dependency override and /info assertion",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml",
                "case_ids": ["fastapi.middleware-proxy.settings-dependency-override"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
}
