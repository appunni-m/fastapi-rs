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
    "docs_src/header_params/tutorial001_py310.py": {
        "rationale": (
            "The documented route declares user_agent with Header(default=None). The linked "
            "input omits the user-agent header and observes the response status and body, "
            "limiting this mapping to the omitted-header default None."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/header_params/tutorial001_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented route declaration with Header(default=None)",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-header-parameter-header-tutorial001-direct.yaml",
                "case_ids": ["fastapi.header.tutorial001.direct.absent-user-agent"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/header_params/tutorial001_an_py310.py": {
        "rationale": (
            "The documented route declares user_agent with Header() and a Python default of "
            "None. The linked input omits the user-agent header and observes the response "
            "status and body, limiting this mapping to the omitted-header default None."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/header_params/tutorial001_an_py310.py",
                "start_line": 8,
                "end_line": 10,
                "role": "documented Annotated route declaration with default None",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-header-parameter-header-tutorial001-annotated.yaml",
                "case_ids": ["fastapi.header.tutorial001.annotated.absent-user-agent"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/header_params/tutorial003_py310.py": {
        "rationale": (
            "The documented route declares optional list[str] x_token values with "
            "Header(default=None). The linked request cases cover an omitted value, one "
            "value, and repeated values in order; this partial mapping does not claim other "
            "Header options or parameter types."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/header_params/tutorial003_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented direct optional list header declaration",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-header-parameter-header-tutorial003-direct.yaml",
                "case_ids": [
                    "fastapi.query-header-review.header003.direct.missing-list-header",
                    "fastapi.query-header-review.header003.direct.single-list-header-value",
                    "fastapi.query-header-review.header003.direct.repeated-list-header-values",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/header_params/tutorial003_an_py310.py": {
        "rationale": (
            "The documented route declares optional list[str] x_token values with Header() "
            "and a Python default of None. The linked request cases cover an omitted value, "
            "one value, and repeated values in order; this partial mapping does not claim "
            "other Header options or parameter types."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/header_params/tutorial003_an_py310.py",
                "start_line": 8,
                "end_line": 10,
                "role": "documented Annotated optional list header declaration",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-header-parameter-header-tutorial003-annotated.yaml",
                "case_ids": [
                    "fastapi.query-header-review.header003.annotated.missing-list-header",
                    "fastapi.query-header-review.header003.annotated.single-list-header-value",
                    "fastapi.query-header-review.header003.annotated.repeated-list-header-values",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
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
    "docs_src/path_operation_configuration/tutorial002_py310.py": {
        "rationale": (
            "The linked case observes the three documented non-empty string tag values for "
            "POST /items/, GET /items/, and GET /users/ through their selected OpenAPI tag "
            "pointers. The mapping is limited to those tag fields; it does not claim the Item "
            "request/response model behavior, HTTP response bodies, enum tags, or tag inheritance."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial002_py310.py",
                "start_line": 15,
                "end_line": 27,
                "role": "documented string-tagged POST and GET operations",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial002-upstream.yaml",
                "case_ids": ["fastapi.path-operation-configurations.tutorial002"],
                "observation_selectors": ["http.status", "openapi.document"],
            }
        ],
    },
    "docs_src/path_operation_configuration/tutorial005_py310.py": {
        "rationale": (
            "The linked case observes the pinned example's explicit non-empty "
            "response_description at the selected POST success-response pointer. The mapping "
            "does not claim summary or docstring extraction, request/response model behavior, "
            "status defaults, or other response descriptions."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial005_py310.py",
                "start_line": 15,
                "end_line": 30,
                "role": "documented POST response_description and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial005-upstream.yaml",
                "case_ids": ["fastapi.path-operation-configurations.tutorial005"],
                "observation_selectors": ["http.status", "openapi.document"],
            }
        ],
    },
    "docs_src/query_params/tutorial002_py310.py": {
        "rationale": (
            "FastAPI 0.141.1 declares GET /items/{item_id} with optional q and returns q only "
            "when it is truthy. The linked cases request the route with q absent and present, "
            "and observe the HTTP response. This partial mapping does not cover other query "
            "types, empty q, or broader routing behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/query_params/tutorial002_py310.py",
                "start_line": 6,
                "end_line": 10,
                "role": "documented optional q route and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-params-tutorial002-upstream.yaml",
                "case_ids": [
                    "fastapi.query-params.tutorial002.item-without-query",
                    "fastapi.query-params.tutorial002.item-with-query",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/query_params/tutorial003_py310.py": {
        "rationale": (
            "The listed requests sample the documented optional q and short parameters: q "
            "absent, q present, and short=true, observing the HTTP responses. This partial "
            "mapping does not claim other values, validation errors, or general query-parameter "
            "behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/query_params/tutorial003_py310.py",
                "start_line": 6,
                "end_line": 15,
                "role": "documented optional q and short parameters with conditional response fields",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-params-tutorial003-upstream.yaml",
                "case_ids": [
                    "fastapi.query-params.tutorial003.item-default-detail",
                    "fastapi.query-params.tutorial003.item-query-detail",
                    "fastapi.query-params.tutorial003.item-short",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/query_params/tutorial004_py310.py": {
        "rationale": (
            "The selected cases exercise GET /users/{user_id}/items/{item_id} with the "
            "documented integer user_id, optional q, and short flag: defaults, q present, and "
            "short=true. This mapping is limited to those inputs and observations."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/query_params/tutorial004_py310.py",
                "start_line": 6,
                "end_line": 17,
                "role": "documented typed user path parameter and optional query parameters",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-params-tutorial004-upstream.yaml",
                "case_ids": [
                    "fastapi.query-params.tutorial004.user-item-default-detail",
                    "fastapi.query-params.tutorial004.user-item-query-detail",
                    "fastapi.query-params.tutorial004.user-item-short",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/query_params/tutorial005_py310.py": {
        "rationale": (
            "The documented route declares needy without a default. The linked cases supply "
            "needy and omit it, then observe the route responses. "
            "This partial mapping covers only this required query parameter and these cases."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/query_params/tutorial005_py310.py",
                "start_line": 6,
                "end_line": 9,
                "role": "documented required needy query parameter and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-params-tutorial005-upstream.yaml",
                "case_ids": [
                    "fastapi.query-params.tutorial005.required-query-present",
                    "fastapi.query-params.tutorial005.required-query-missing",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/query_params/tutorial006_py310.py": {
        "rationale": (
            "The selected successful request supplies the documented required needy value "
            "while omitting skip and limit, exercising their defaults. The mixed "
            "invalid-integers-and-missing-required-query case is not linked because that combined "
            "error scenario is not shown by this example."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/query_params/tutorial006_py310.py",
                "start_line": 6,
                "end_line": 11,
                "role": "documented required needy parameter and optional defaults",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-params-tutorial006-upstream.yaml",
                "case_ids": [
                    "fastapi.query-params.tutorial006.required-query-present",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/path_params/tutorial001_py310.py": {
        "rationale": (
            "The documented untyped item_id route is sampled with numeric-looking and "
            "alphabetic path segments, plus the selected route paths in OpenAPI. This partial "
            "mapping covers only these two values and observations."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_params/tutorial001_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented untyped item_id path parameter and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-params-tutorial001-upstream.yaml",
                "case_ids": [
                    "fastapi.path-params.tutorial001-untyped-item-id",
                    "fastapi.path-params.tutorial001-openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/path_params/tutorial002_py310.py": {
        "rationale": (
            "The documented item_id: int route is sampled with a valid integer and a "
            "non-integer segment, plus the selected route paths in OpenAPI. This mapping is "
            "limited to integer path parsing and the listed response observations."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_params/tutorial002_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented integer item_id path parameter and response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-params-tutorial002-upstream.yaml",
                "case_ids": [
                    "fastapi.path-params.tutorial002-integer-item-id",
                    "fastapi.path-params.tutorial002-openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/path_params/tutorial003_py310.py": {
        "rationale": (
            "The documented app registers the literal /users/me route before the dynamic "
            "/users/{user_id} route. The linked case requests both paths and observes their "
            "responses plus the selected OpenAPI paths. This partial mapping does not claim "
            "other route-order conflicts."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_params/tutorial003_py310.py",
                "start_line": 6,
                "end_line": 13,
                "role": "documented static and dynamic user routes in registration order",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-params-tutorial003-upstream.yaml",
                "case_ids": [
                    "fastapi.path-params.tutorial003-static-route-precedence",
                    "fastapi.path-params.tutorial003-openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/response_model/tutorial002_py310.py": {
        "rationale": (
            "The pinned example deliberately uses UserIn for both the request and response, "
            "so the linked case observes the sensitive password field retained in the response "
            "and the selected OpenAPI paths. The source explicitly warns not to use this in "
            "production; this mapping records that negative example and does not endorse it."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/response_model/tutorial002_py310.py",
                "start_line": 7,
                "end_line": 17,
                "role": "documented shared input/output model with production warning",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
                "case_ids": [
                    "fastapi.response-model.tutorial002-same-model-retains-sensitive-field"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/response_model/tutorial003_py310.py": {
        "rationale": (
            "The documented handler accepts UserIn and declares response_model=UserOut, whose "
            "fields omit password. The linked case observes the filtered response and selected "
            "OpenAPI paths; this mapping is limited to that explicit model pair."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/response_model/tutorial003_py310.py",
                "start_line": 9,
                "end_line": 24,
                "role": "documented input and explicit output response models",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
                "case_ids": [
                    "fastapi.response-model.tutorial003-explicit-output-model-filters-input"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/response_model/tutorial003_01_py310.py": {
        "rationale": (
            "The documented handler returns UserIn while annotating its return as BaseUser, "
            "which omits the subclass password field. The linked case observes that inferred "
            "response filtering and selected OpenAPI paths only; it does not claim other "
            "return-annotation forms."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/response_model/tutorial003_01_py310.py",
                "start_line": 7,
                "end_line": 19,
                "role": "documented base return annotation and derived input model",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
                "case_ids": [
                    "fastapi.response-model.tutorial003-01-return-annotation-filters-derived-input"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/response_model/tutorial004_py310.py": {
        "rationale": (
            "The example sets response_model_exclude_unset=True and provides records with "
            "omitted, explicitly provided, and explicit-null fields. The linked cases observe "
            "the resulting response bodies and selected OpenAPI paths; the mapping does not cover "
            "exclude_defaults or exclude_none."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/response_model/tutorial004_py310.py",
                "start_line": 7,
                "end_line": 24,
                "role": "documented model, contrasting records, and exclude_unset route",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
                "case_ids": [
                    "fastapi.response-model.tutorial004-exclude-unset-preserves-explicit-fields"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/response_model/tutorial006_py310.py": {
        "rationale": (
            "The documented routes exercise response_model_include for name and description "
            "and response_model_exclude for tax. The linked cases observe both response bodies "
            "and selected OpenAPI paths; this mapping covers only these top-level field "
            "selections."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/response_model/tutorial006_py310.py",
                "start_line": 7,
                "end_line": 37,
                "role": "documented top-level response include and exclude routes",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
                "case_ids": [
                    "fastapi.response-model.tutorial006-include-and-exclude-top-level-fields"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/response_model/tutorial003_05_py310.py": {
        "rationale": (
            "The example explicitly sets response_model=None for a handler annotated as "
            "Response | dict and shows JSON and RedirectResponse branches. The linked cases "
            "observe those responses and selected OpenAPI paths; this mapping preserves "
            "that union-return scope."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/response_model/tutorial003_05_py310.py",
                "start_line": 7,
                "end_line": 11,
                "role": "documented response_model=None union return and branches",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
                "case_ids": [
                    "fastapi.response-model.tutorial003-05-explicitly-disabled-response-model"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
            }
        ],
    },
    "docs_src/custom_response/tutorial003_py310.py": {
        "rationale": (
            "The documented GET /items/ handler directly returns HTMLResponse with the "
            "declared HTML content and status code. The linked case observes response status "
            "and body only; it does not claim broader custom-response or OpenAPI behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/custom_response/tutorial003_py310.py",
                "start_line": 7,
                "end_line": 19,
                "role": "documented direct HTMLResponse return",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/custom-response-tutorial003-upstream.yaml",
                "case_ids": ["fastapi.custom-response.tutorial003.items-response"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/body/tutorial003_py310.py": {
        "rationale": (
            "The documented model requires name and price, permits optional description and "
            "tax, and the PUT handler returns the submitted model fields. The linked complete "
            "record case exercises that documented request and response; boundary probes are "
            "not mapped as direct examples."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body/tutorial003_py310.py",
                "start_line": 5,
                "end_line": 17,
                "role": "documented Pydantic body model and PUT handler",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-tutorial003-model-upstream.yaml",
                "case_ids": ["fastapi.body.tutorial003.complete-model"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
}
