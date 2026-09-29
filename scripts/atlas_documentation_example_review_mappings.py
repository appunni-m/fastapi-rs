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
    "docs_src/path_operation_advanced_configuration/tutorial003_py310.py": {
        "rationale": (
            "FastAPI 0.141.1 serves the documented GET /items/ route while excluding it from the "
            "selected OpenAPI paths because include_in_schema=False. The linked case observes "
            "that route response and the paths projection only; it does not claim other route "
            "configuration behavior or full application parity."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_advanced_configuration/tutorial003_py310.py",
                "start_line": 1,
                "end_line": 8,
                "role": "documented route response and include_in_schema=False",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial003-upstream.yaml",
                "case_ids": ["fastapi.path-operation-advanced-configurations.tutorial003"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                ],
            }
        ],
    },
    "docs_src/path_operation_configuration/tutorial006_py310.py": {
        "rationale": (
            "The linked input case observes the documented /items/, /users/, and /elements/ "
            "routes as successful responses, plus their selected OpenAPI tags and the "
            "deprecated=True flag for /elements/. The mapping is limited to these non-empty "
            "tags and the deprecation field; it does not cover other path-operation options."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial006_py310.py",
                "start_line": 1,
                "end_line": 18,
                "role": "documented non-empty tags and deprecated=True path operations",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial006-upstream.yaml",
                "case_ids": ["fastapi.path-operation-configurations.tutorial006"],
                "observation_selectors": ["http.status", "openapi.document"],
            }
        ],
    },
    "docs_src/header_params/tutorial002_an_py310.py": {
        "rationale": (
            "The linked cases sample the documented Annotated Header(convert_underscores=False) "
            "parameter when absent, supplied under its underscore name, and supplied under the "
            "hyphenated name. This is a partial sample of that header-name conversion setting, "
            "not a claim about other Header options or header parameter behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/header_params/tutorial002_an_py310.py",
                "start_line": 1,
                "end_line": 12,
                "role": "documented optional Header(convert_underscores=False) route",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/header-convert-underscores-false.yaml",
                "case_ids": [
                    "fastapi.header.convert-underscores-false.missing",
                    "fastapi.header.convert-underscores-false.underscore-name",
                    "fastapi.header.convert-underscores-false.hyphen-name",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/path_operation_configuration/tutorial001_py310.py": {
        "rationale": (
            "The linked case submits the documented POST /items/ body and samples the HTTP "
            "status plus the selected OpenAPI response 201 and Item schema pointers. The mapping "
            "is limited to this route's status_code=201 behavior and those selected document "
            "fields; it does not claim status defaults or broader response-model behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial001_py310.py",
                "start_line": 1,
                "end_line": 17,
                "role": "documented Item request/response and status_code=201 route",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial001-upstream.yaml",
                "case_ids": ["fastapi.path-operation-configurations.tutorial001"],
                "observation_selectors": ["http.status", "openapi.document"],
            }
        ],
    },
    "docs_src/metadata/tutorial001_py310.py": {
        "rationale": (
            "The selected OpenAPI pointers observe the pinned example's exact non-empty "
            "summary, description, terms_of_service, contact, and license_info values. The "
            "mapping is limited to those five /info fields; it does not claim empty or omitted "
            "value handling, openapi_external_docs, route behavior, model serialization, or other "
            "constructor options."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/metadata/tutorial001_py310.py",
                "start_line": 3,
                "end_line": 33,
                "role": "documented description and app-level OpenAPI metadata",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/metadata-tutorial001-upstream.yaml",
                "case_ids": ["fastapi.docs.metadata.tutorial001.openapi-info-fields"],
                "observation_selectors": ["openapi.document"],
            }
        ],
    },
}
