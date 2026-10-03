"""Reviewed, exact workflow links for selected FastAPI documentation examples.

The `upstream_documentation_example` evidence kind binds a case to one exact
`docs_src` file. These links remain partial: they describe only the listed
case IDs and observation selectors, not the entire example or documentation
page.
"""

if __package__:
    from scripts.atlas_strict_content_type_documentation_example_review_mappings import (
        STRICT_CONTENT_TYPE_DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS,
    )
else:
    from atlas_strict_content_type_documentation_example_review_mappings import (
        STRICT_CONTENT_TYPE_DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS,
    )

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS = {
    "docs_src/advanced_middleware/tutorial001_py310.py": {
        "rationale": (
            "The pinned example installs HTTPSRedirectMiddleware around a GET route. The "
            "independent workflow sends an HTTP request to a separately named /status route "
            "and observes the redirect response status, ordered headers, and body. This "
            "supports only the redirect behavior; it does not claim the source route or body, "
            "HTTPS dispatch, or middleware composition."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/advanced_middleware/tutorial001_py310.py",
                "start_line": 2,
                "end_line": 2,
                "role": "documented import of HTTPSRedirectMiddleware",
            },
            {
                "path": "docs_src/advanced_middleware/tutorial001_py310.py",
                "start_line": 6,
                "end_line": 6,
                "role": "documented HTTPSRedirectMiddleware installation",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware.yaml",
                "case_ids": ["fastapi.middleware.https-redirect-http"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/authentication_error_status_code/tutorial001_an_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example overrides HTTPBearer's missing-credentials error to "
            "return HTTP 403. The independent requests exercise that unauthenticated branch and "
            "a valid bearer credential on a separately named route with different detail and "
            "token values. They observe status, ordered headers, and body bytes only; they do not "
            "claim the tutorial's literals, route name, or OpenAPI document."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/authentication_error_status_code/tutorial001_an_py310.py",
                "start_line": 9,
                "end_line": 16,
                "role": "documented HTTPBearer missing-credentials override and dependency",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/authentication-error-status-code-tutorial.yaml",
                "case_ids": [
                    "fastapi.docs.auth-error-status.legacy-forbidden",
                    "fastapi.docs.auth-error-status.valid-bearer",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/cors/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example installs credentialed CORSMiddleware with allowed "
            "origins, methods, and headers. The independent cases use different origins, an "
            "explicit method/header allowlist, and a separate records route to sample allowed "
            "and rejected preflights plus simple requests. The mapping claims only status and "
            "ordered response headers, which carry the CORS policy result; it does not claim the "
            "tutorial's origin list, wildcard configuration, or literal route and response."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/cors/tutorial001_py310.py",
                "start_line": 13,
                "end_line": 19,
                "role": "documented CORSMiddleware registration and CORS policy options",
            },
            {
                "path": "docs_src/cors/tutorial001_py310.py",
                "start_line": 22,
                "end_line": 24,
                "role": "documented route behind CORS middleware",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml",
                "case_ids": [
                    "fastapi.docs.cors-tutorial.allowed-preflight",
                    "fastapi.docs.cors-tutorial.disallowed-preflight-method",
                    "fastapi.docs.cors-tutorial.allowed-simple-request",
                    "fastapi.docs.cors-tutorial.unlisted-simple-request",
                ],
                "observation_selectors": [
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/body_updates/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example encodes and stores a complete model for a PUT request. "
            "The independent records workflow sends a partial body to a separate route and "
            "observes the full replacement result, including model defaults; it uses different "
            "field names and values from the tutorial."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body_updates/tutorial001_py310.py",
                "start_line": 28,
                "end_line": 32,
                "role": "documented PUT model encoding and replacement behavior",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-updates-independent.yaml",
                "case_ids": ["fastapi.docs.body-updates.put-replaces-omitted-fields"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/body_updates/tutorial002_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example applies only explicitly supplied fields when handling "
            "PATCH. Independent cases use a separately named records route and model to verify "
            "that omitted fields remain stored while an explicit null is applied; the tutorial's "
            "identifiers, field names, and values are not reused."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body_updates/tutorial002_py310.py",
                "start_line": 28,
                "end_line": 35,
                "role": "documented PATCH exclude-unset merge and JSON encoding behavior",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-updates-independent.yaml",
                "case_ids": [
                    "fastapi.docs.body-updates.patch-preserves-omitted-fields",
                    "fastapi.docs.body-updates.patch-applies-explicit-null",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/first_steps/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example registers an async root route and returns a JSON "
            "object. An independent app exposes `/welcome` and returns different data, then the "
            "workflow requests that route and compares status and body bytes; it does not reuse "
            "the example's route or response literals."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/first_steps/tutorial001_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented async root route and JSON response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/first-steps-application-testing-upstream.yaml",
                "case_ids": ["fastapi.first-steps.async-independent-route"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/first_steps/tutorial003_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example registers a synchronous root route with a JSON return "
            "value. An independent app exposes `/portal` and returns different data, then the "
            "workflow requests that route and compares status and body bytes; it does not reuse "
            "the example's route or response literals."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/first_steps/tutorial003_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented synchronous root route and JSON response",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/first-steps-application-testing-upstream.yaml",
                "case_ids": ["fastapi.first-steps.sync-independent-route"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/additional_status_codes/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example upserts an item: an existing item returns the normal "
            "response, while a new item returns JSONResponse with HTTP 201. The independent "
            "cases exercise those two branches with separate identifiers and payloads, observing "
            "exact status and body bytes only; they do not claim the tutorial's literal values, "
            "state across requests, response headers, or OpenAPI documentation."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/additional_status_codes/tutorial001_py310.py",
                "start_line": 9,
                "end_line": 23,
                "role": "documented existing-item and new-item PUT response branches",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/additional-status-codes-tutorial-upstream.yaml",
                "case_ids": [
                    "fastapi.additional-status-codes.tutorial-update-existing",
                    "fastapi.additional-status-codes.tutorial-create-new",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/additional_status_codes/tutorial001_an_py310.py": {
        "rationale": (
            "The Annotated FastAPI 0.141.1 example upserts an item: an existing item returns the "
            "normal response, while a new item returns JSONResponse with HTTP 201. The independent "
            "cases exercise those two branches with separate identifiers and payloads, observing "
            "exact status and body bytes only; they do not claim the tutorial's literal values, "
            "state across requests, response headers, or OpenAPI documentation."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/additional_status_codes/tutorial001_an_py310.py",
                "start_line": 11,
                "end_line": 25,
                "role": "documented existing-item and new-item PUT response branches",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/additional-status-codes-tutorial-upstream.yaml",
                "case_ids": [
                    "fastapi.additional-status-codes.tutorial-update-existing",
                    "fastapi.additional-status-codes.tutorial-create-new",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/handling_errors/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example returns an existing item and raises HTTPException "
            "for an unknown item. The independent cases sample those success and default-error "
            "response paths on an entries route; they observe status and body only and do not "
            "claim the source route, literal values, or OpenAPI snapshot."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/handling_errors/tutorial001_py310.py",
                "start_line": 8,
                "end_line": 12,
                "role": "documented item route with success and HTTPException branches",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial001-review.yaml",
                "case_ids": [
                    "fastapi.docs-example.handling-errors.tutorial001.success",
                    "fastapi.docs-example.handling-errors.tutorial001.not-found",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/handling_errors/tutorial002_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example supplies custom headers on an HTTPException. The "
            "independent case samples status, response headers, and body on a different archive "
            "route with another header name and value; it does not claim the source literals, "
            "success branch, or OpenAPI snapshot."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/handling_errors/tutorial002_py310.py",
                "start_line": 8,
                "end_line": 16,
                "role": "documented route and HTTPException custom headers",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial002-review.yaml",
                "case_ids": ["fastapi.docs-example.handling-errors.tutorial002.forwarded-header"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/handling_errors/tutorial003_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example registers a handler for an application-defined "
            "exception and returns JSON with a non-default status. The independent case samples "
            "registered exception dispatch and the resulting status/body using a separate "
            "exception type, route, and payload; it does not cover the exact interpolated text "
            "or OpenAPI snapshot."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/handling_errors/tutorial003_py310.py",
                "start_line": 5,
                "end_line": 18,
                "role": "documented custom exception class and JSONResponse handler",
            },
            {
                "path": "docs_src/handling_errors/tutorial003_py310.py",
                "start_line": 21,
                "end_line": 25,
                "role": "documented route branch that raises the custom exception",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial003-review.yaml",
                "case_ids": ["fastapi.docs-example.handling-errors.tutorial003.custom-exception"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/handling_errors/tutorial004_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example registers custom Starlette HTTP and FastAPI request-"
            "validation handlers, then exercises an integer path route with success, HTTP error, "
            "and validation branches. The independent cases exercise analogous handler dispatch "
            "and a successful typed route using different paths and values. They observe response "
            "status, ordered headers, and body bytes; they do not claim the tutorial's exact error "
            "text, validation location, route literals, or OpenAPI snapshot."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/handling_errors/tutorial004_py310.py",
                "start_line": 9,
                "end_line": 19,
                "role": "custom HTTP and request-validation exception handlers",
            },
            {
                "path": "docs_src/handling_errors/tutorial004_py310.py",
                "start_line": 22,
                "end_line": 26,
                "role": "typed item route with success, HTTP exception, and validation branches",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/exception-overrides.yaml",
                "case_ids": [
                    "fastapi.docs.handling-errors.overridden-http-error",
                    "fastapi.docs.handling-errors.overridden-validation-error",
                    "fastapi.docs.handling-errors.override-success",
                    "fastapi.docs.handling-errors.overrides-openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/handling_errors/tutorial005_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example customizes RequestValidationError handling to encode "
            "both validation details and the parsed request body, and returns a Pydantic model "
            "for valid input. The independent cases sample invalid-body handling, valid model "
            "input/output, and the related OpenAPI request/422 schemas with a separately named "
            "model and handler payload. They do not claim the tutorial's exact field names, "
            "validation records, encoded JSON keys, or complete OpenAPI document."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/handling_errors/tutorial005_py310.py",
                "start_line": 10,
                "end_line": 15,
                "role": "custom request-validation response encoding errors and parsed body",
            },
            {
                "path": "docs_src/handling_errors/tutorial005_py310.py",
                "start_line": 18,
                "end_line": 25,
                "role": "Pydantic request model and POST route returning the model",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-body.yaml",
                "case_ids": [
                    "fastapi.docs.handling-errors.body-echo.invalid-input",
                    "fastapi.docs.handling-errors.body-echo.openapi",
                    "fastapi.docs.handling-errors.body-echo.valid-input",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
    "docs_src/handling_errors/tutorial006_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example registers HTTP and request-validation handlers that "
            "delegate to FastAPI's defaults. The original independent cases trigger those two "
            "handler categories and observe response status/body only. A separate probe registers "
            "a distinctive Starlette HTTP exception handler and samples dispatch for an "
            "unregistered path; this makes route-miss handling observable but does not claim the "
            "example's printed messages, default delegation, route, or literal details."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/handling_errors/tutorial006_py310.py",
                "start_line": 12,
                "end_line": 21,
                "role": "documented custom HTTP and validation handlers delegating to defaults",
            },
            {
                "path": "docs_src/handling_errors/tutorial006_py310.py",
                "start_line": 24,
                "end_line": 28,
                "role": "documented typed item route with HTTP and success branches",
            },
            {
                "path": "docs_src/handling_errors/tutorial006_py310.py",
                "start_line": 12,
                "end_line": 17,
                "role": "documented Starlette HTTP exception handler registration",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial006-review.yaml",
                "case_ids": [
                    "fastapi.docs-example.handling-errors.tutorial006.delegated-http-error",
                    "fastapi.docs-example.handling-errors.tutorial006.delegated-validation-error",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/custom-not-found-handler.yaml",
                "case_ids": [
                    "fastapi.docs-example.handling-errors.tutorial006.custom-route-miss-handler"
                ],
                "observation_selectors": [
                    "asgi.send.message_types",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            },
        ],
    },
    "docs_src/security/tutorial003_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example extracts a bearer token, resolves a current user through "
            "nested dependencies, and applies an app-owned inactive-user policy. The independent "
            "case sends an authenticated token through the same dependency shape and observes the "
            "resulting HTTP response. It samples FastAPI bearer parsing and dependency dispatch; "
            "the inactive flag check and error text remain application-owned."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/security/tutorial003_py310.py",
                "start_line": 56,
                "end_line": 70,
                "role": "documented bearer extraction and nested current-active-user dependency",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/security-oauth2-inactive-user-source-wave.yaml",
                "case_ids": ["fastapi.security.tutorial-003.oauth2-inactive-user"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                ],
            }
        ],
    },
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
    "docs_src/cookie_params/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 direct example declares optional ads_id with "
            "Cookie(default=None). The mapped case includes requests to its separately "
            "declared direct route with the cookie omitted and supplied, observing response "
            "status and body bytes. The same case separately exercises the Annotated route "
            "mapped to its own source example; this mapping does not assert equivalence "
            "between the two declaration forms or cover other Cookie behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/cookie_params/tutorial001_py310.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented direct optional Cookie parameter and default",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/atlas-pending-tutorials-source-wave.yaml",
                "case_ids": ["fastapi.pending.tutorials-source-wave.cookie-parameter-cases"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/cookie_params/tutorial001_an_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 Annotated example declares optional ads_id with Cookie() "
            "and a Python default of None. The mapped case includes requests to its separately "
            "declared Annotated route with the cookie omitted and supplied, observing response "
            "status and body bytes. The same case separately exercises the direct route "
            "mapped to its own source example; this mapping does not assert equivalence "
            "between the two declaration forms or cover other Cookie behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/cookie_params/tutorial001_an_py310.py",
                "start_line": 8,
                "end_line": 10,
                "role": "documented Annotated optional Cookie parameter and default",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/atlas-pending-tutorials-source-wave.yaml",
                "case_ids": ["fastapi.pending.tutorials-source-wave.cookie-parameter-cases"],
                "observation_selectors": ["http.body.bytes", "http.status"],
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
    "docs_src/header_params/tutorial002_py310.py": {
        "rationale": (
            "This FastAPI 0.141.1 example declares an optional header with "
            "convert_underscores=False and returns its value. The independent cases sample the "
            "missing, irrelevant, underscore-name, and hyphen-name branches with exact response "
            "status/body observations; they do not claim the OpenAPI parameter schema or other "
            "Header options."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/header_params/tutorial002_py310.py",
                "start_line": 6,
                "end_line": 10,
                "role": "documented optional header with underscore conversion disabled",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-header-parameter-header-tutorial002-direct.yaml",
                "case_ids": [
                    "fastapi.query-header-review.header002.direct.default-underscore-alias",
                    "fastapi.query-header-review.header002.direct.irrelevant-x-header",
                    "fastapi.query-header-review.header002.direct.underscore-alias",
                    "fastapi.query-header-review.header002.direct.hyphen-does-not-match-underscore-alias",
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
    "docs_src/path_operation_configuration/tutorial002b_py310.py": {
        "rationale": (
            "This FastAPI 0.141.1 example assigns Enum members as tags for GET /items/ and "
            "GET /users/. The independent case observes HTTP response status and selects the tag "
            "arrays for those methods, sampling Enum-to-OpenAPI tag serialization. It does not "
            "claim the example's runtime response bodies, other tag forms, or unrelated OpenAPI "
            "fields."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial002b_py310.py",
                "start_line": 8,
                "end_line": 19,
                "role": "documented Enum members used as path-operation tags",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial002b-upstream.yaml",
                "case_ids": ["fastapi.path-operation-configurations.tutorial002b"],
                "observation_selectors": ["http.status", "openapi.document"],
            }
        ],
    },
    "docs_src/path_operation_configuration/tutorial003_py310.py": {
        "rationale": (
            "The example sets explicit summary and description metadata on a POST operation. "
            "The independent case observes the POST response status and selects those two OpenAPI "
            "fields from an analogous Item route; it does not claim the tutorial's full schema, "
            "request validation, or response serialization behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial003_py310.py",
                "start_line": 15,
                "end_line": 20,
                "role": "documented explicit operation summary and description",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial003-upstream.yaml",
                "case_ids": [
                    "fastapi.path-operation-configurations.tutorial003-explicit-description"
                ],
                "observation_selectors": ["http.status", "openapi.document"],
            }
        ],
    },
    "docs_src/path_operation_configuration/tutorial004_py310.py": {
        "rationale": (
            "The example derives an operation summary and description from the endpoint docstring. "
            "The independent case observes the POST response status and selects those two OpenAPI "
            "fields from an analogous Item route; it does not claim the tutorial's full schema, "
            "request validation, or response serialization behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/path_operation_configuration/tutorial004_py310.py",
                "start_line": 15,
                "end_line": 25,
                "role": "documented endpoint docstring used as OpenAPI description",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial004-upstream.yaml",
                "case_ids": [
                    "fastapi.path-operation-configurations.tutorial004-docstring-description"
                ],
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
    "docs_src/query_params/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example declares integer skip and limit query parameters "
            "with defaults and slices the item list. The linked cases exercise the default "
            "request, skip=1, and skip=1 with limit=1, observing only response status and "
            "body bytes. This is a partial mapping of those pagination inputs; it does not "
            "claim invalid-integer behavior, other values, or the OpenAPI document."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/query_params/tutorial001_py310.py",
                "start_line": 8,
                "end_line": 10,
                "role": "documented integer query defaults and list-slice behavior",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-header-parameter-query-tutorial001.yaml",
                "case_ids": [
                    "fastapi.query-header-review.query001.items-default",
                    "fastapi.query-header-review.query001.items-skip",
                    "fastapi.query-header-review.query001.items-skip-limit",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
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
    "docs_src/request_files/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example accepts a bytes file and an UploadFile on two POST "
            "routes. The independent cases sample the resulting file length and filename with "
            "different route paths, observing HTTP status and response bytes only. This mapping "
            "does not claim the source route paths, exact OpenAPI, parser-missing behavior, or "
            "UploadFile lifetime behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/request_files/tutorial001_py310.py",
                "start_line": 6,
                "end_line": 13,
                "role": "documented bytes File and UploadFile route behaviors",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-file-form-tutorials-wave.yaml",
                "case_ids": [
                    "fastapi.request-files-tutorial001.post-file-bytes",
                    "fastapi.request-files-tutorial001-03.post-upload-file",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/request_files/tutorial001_02_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example declares an optional UploadFile parameter. The linked "
            "independent request omits the multipart body and observes the HTTP response only; "
            "its route additionally declares separate File.alias and validation_alias values, "
            "but this documentation mapping claims only the omitted optional-upload branch. "
            "Alias acceptance and OpenAPI projection are mapped separately to the pinned test "
            "functions."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/request_files/tutorial001_02_py310.py",
                "start_line": 14,
                "end_line": 18,
                "role": "documented optional UploadFile endpoint and absent-file response branch",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-optional-upload-alias-validation-alias-review.yaml",
                "case_ids": ["fastapi.request-optional-upload.optional-missing-doc-example"],
                "observation_selectors": ["http.body.bytes", "http.status"],
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
    "docs_src/custom_response/tutorial002_py310.py": {
        "rationale": (
            "The documented GET /items/ route declares response_class=HTMLResponse and returns "
            "HTML text. The linked cases observe response status/body/headers, including the "
            "text/html media type, and the OpenAPI 200 response content with a string schema, "
            "as asserted by the upstream test. They do not claim broader custom-response behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/custom_response/tutorial002_py310.py",
                "start_line": 7,
                "end_line": 18,
                "role": "documented response_class=HTMLResponse route and HTML content",
            },
            {
                "path": "tests/test_tutorial/test_custom_response/test_tutorial002_tutorial003_tutorial004.py",
                "start_line": 38,
                "end_line": 68,
                "role": "upstream response and text/html string-schema OpenAPI assertions",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml",
                "case_ids": [
                    "fastapi.custom-response.tutorial002.items-response",
                    "fastapi.custom-response.tutorial002.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
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
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/custom-response-tutorial003-upstream.yaml",
                "case_ids": ["fastapi.custom-response.tutorial003.items-response"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/custom_response/tutorial004_py310.py": {
        "rationale": (
            "The documented GET /items/ route declares response_class=HTMLResponse and returns an "
            "explicit HTMLResponse with status code 200. The linked cases observe response "
            "status/body/headers, including the text/html media type, and the OpenAPI 200 response "
            "content with a string schema, as asserted by the upstream test. They do not claim "
            "broader custom-response behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/custom_response/tutorial004_py310.py",
                "start_line": 7,
                "end_line": 23,
                "role": "documented HTMLResponse factory and route returning it",
            },
            {
                "path": "tests/test_tutorial/test_custom_response/test_tutorial002_tutorial003_tutorial004.py",
                "start_line": 38,
                "end_line": 68,
                "role": "upstream response and text/html string-schema OpenAPI assertions",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/custom-response-tutorial004-upstream.yaml",
                "case_ids": [
                    "fastapi.custom-response.tutorial004.items-response",
                    "fastapi.custom-response.tutorial004.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
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
    "docs_src/body/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example accepts a typed model body with two required and two "
            "optional fields, then returns that model. The independent catalog cases exercise "
            "a complete body and the required-fields-only form on another route, observing "
            "response status and body only; they do not claim the source field names, exact "
            "values, validation boundaries, or OpenAPI document."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body/tutorial001_py310.py",
                "start_line": 5,
                "end_line": 17,
                "role": "documented Pydantic body model and POST route",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-doc-tutorial001-review.yaml",
                "case_ids": [
                    "fastapi.docs-example.body.tutorial001.complete-entry",
                    "fastapi.docs-example.body.tutorial001.required-fields-only",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/body/tutorial002_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example binds a model body, dumps its fields, and conditionally "
            "adds a computed response field when the optional tax value is supplied. The "
            "independent quote cases sample both optional-value branches with another model "
            "and route, observing status/body only. The arithmetic is application-owned and "
            "is not claimed as FastAPI behavior; source field names, values, and OpenAPI are "
            "also outside this mapping."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body/tutorial002_py310.py",
                "start_line": 5,
                "end_line": 21,
                "role": "documented Pydantic body model and optional-tax response branch",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-doc-tutorial002-review.yaml",
                "case_ids": [
                    "fastapi.docs-example.body.tutorial002.optional-surcharge-present",
                    "fastapi.docs-example.body.tutorial002.optional-surcharge-absent",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/body/tutorial004_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example binds an integer path parameter, a Pydantic request "
            "body, and an optional query value. The independent revision cases exercise those "
            "three request inputs with and without the optional query value, observing response "
            "status/body only. The route's result assembly is application-owned; exact source "
            "names, values, and OpenAPI are outside this mapping."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body/tutorial004_py310.py",
                "start_line": 5,
                "end_line": 20,
                "role": "documented Pydantic model and path/body/query route",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-doc-tutorial004-review.yaml",
                "case_ids": [
                    "fastapi.docs-example.body.tutorial004.path-query-body",
                    "fastapi.docs-example.body.tutorial004.optional-query-absent",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    },
    "docs_src/body_fields/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example embeds a model body under a named property and uses "
            "Pydantic field constraints. The independent supply cases exercise the embedded "
            "JSON envelope, positive-value validation, and the generated request schema on a "
            "different route/model. They observe status/body and a selected OpenAPI path "
            "projection; they do not claim the source field names, limit values, descriptions, "
            "or complete document."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/body_fields/tutorial001_py310.py",
                "start_line": 7,
                "end_line": 19,
                "role": "documented constrained model and Body(embed=True) path operation",
            }
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-fields-doc-tutorial001-review.yaml",
                "case_ids": [
                    "fastapi.docs-example.body-fields.tutorial001.embedded-model-valid",
                    "fastapi.docs-example.body-fields.tutorial001.embedded-model-invalid-amount",
                    "fastapi.docs-example.body-fields.tutorial001.openapi-embedded-schema",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                ],
            }
        ],
    },
}

if __package__:
    from scripts.atlas_documentation_example_review_wave_d import (
        DOC_EXAMPLE_CITATION_WAVE_D,
    )
else:
    from atlas_documentation_example_review_wave_d import DOC_EXAMPLE_CITATION_WAVE_D

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_D)


# Query parameter tutorial examples: exact source-to-input workflow links.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/response_change_status_code/tutorial001_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example returns an existing task at the declared default "
                "status and changes the response status to 201 when it creates a task. The "
                "independent case samples the existing-record and new-record branches and "
                "observes status and body only. Its route path and literal task values differ; "
                "this mapping does not claim those literals, OpenAPI, or other response-status "
                "behavior."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/response_change_status_code/tutorial001_py310.py",
                    "start_line": 8,
                    "end_line": 12,
                    "role": "documented default-status route and conditional Response status mutation",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/response-change-status-tutorial-review.yaml",
                    "case_ids": [
                        "fastapi.response.change-status-code.tutorial-existing-and-created"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial001_py310.py": {
            "rationale": "The exact source "
            "example declares an "
            "optional plain query "
            "string. The "
            "independent echo "
            "route observes "
            "supplied-value "
            "extraction and its "
            "OpenAPI parameter "
            "entry; the source "
            "example’s fixed "
            "catalog response is "
            "application-owned "
            "and not reproduced.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial001_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial001"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial002_py310.py": {
            "rationale": "The exact source "
            "example declares an "
            "optional query with "
            "a 50-character "
            "maximum. The "
            "independent case "
            "submits an "
            "over-limit value to "
            "its direct or "
            "Annotated "
            "declaration and "
            "observes status/body "
            "plus the selected "
            "OpenAPI parameter. "
            "The source catalog "
            "response is not "
            "claimed.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial002_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial002"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial002_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "an optional query "
            "with a "
            "50-character "
            "maximum. The "
            "independent case "
            "submits an "
            "over-limit value "
            "to its direct or "
            "Annotated "
            "declaration and "
            "observes "
            "status/body plus "
            "the selected "
            "OpenAPI "
            "parameter. The "
            "source catalog "
            "response is not "
            "claimed.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial002_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial002"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial003_py310.py": {
            "rationale": "The exact source "
            "example declares an "
            "optional query with "
            "3-to-50-character "
            "bounds. The "
            "independent case "
            "submits a value "
            "below the minimum "
            "through each "
            "declaration and "
            "observes status/body "
            "plus the selected "
            "OpenAPI parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial003_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial003"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial003_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "an optional query "
            "with "
            "3-to-50-character "
            "bounds. The "
            "independent case "
            "submits a value "
            "below the minimum "
            "through each "
            "declaration and "
            "observes "
            "status/body plus "
            "the selected "
            "OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial003_an_py310.py",
                    "start_line": 8,
                    "end_line": 11,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial003"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial004_py310.py": {
            "rationale": "The exact source "
            "example adds the "
            "anchored fixedquery "
            "pattern to its "
            "optional "
            "3-to-50-character "
            "query. The "
            "independent case "
            "submits a "
            "length-valid pattern "
            "mismatch and "
            "observes validation "
            "response plus the "
            "selected OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial004_py310.py",
                    "start_line": 6,
                    "end_line": 11,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-pattern-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial004"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial004_an_py310.py": {
            "rationale": "The exact source "
            "example adds the "
            "anchored "
            "fixedquery "
            "pattern to its "
            "optional "
            "3-to-50-character "
            "query. The "
            "independent case "
            "submits a "
            "length-valid "
            "pattern mismatch "
            "and observes "
            "validation "
            "response plus the "
            "selected OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial004_an_py310.py",
                    "start_line": 8,
                    "end_line": 13,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-pattern-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial004"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial005_py310.py": {
            "rationale": "The exact source "
            "example declares a "
            "query with a literal "
            "default and minimum "
            "length. The "
            "independent case "
            "omits the query to "
            "observe default "
            "selection and the "
            "parameter schema; "
            "the independent "
            "default text differs "
            "from the docs "
            "example.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial005_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial005"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial005_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "a query with a "
            "literal default "
            "and minimum "
            "length. The "
            "independent case "
            "omits the query "
            "to observe "
            "default selection "
            "and the parameter "
            "schema; the "
            "independent "
            "default text "
            "differs from the "
            "docs example.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial005_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial005"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial006_py310.py": {
            "rationale": "The exact source "
            "example declares a "
            "required string "
            "query with a minimum "
            "length. The "
            "independent case "
            "omits it to observe "
            "required-query "
            "validation and the "
            "selected OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial006_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial006"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial006_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "a required string "
            "query with a "
            "minimum length. "
            "The independent "
            "case omits it to "
            "observe "
            "required-query "
            "validation and "
            "the selected "
            "OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial006_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial006"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial006c_py310.py": {
            "rationale": "The exact source "
            "example declares a "
            "nullable-typed "
            "query without a "
            "default, so the "
            "request still "
            "requires it, with a "
            "minimum length. The "
            "independent case "
            "observes that "
            "missing-value "
            "behavior and the "
            "selected OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial006c_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial006c"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial006c_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "a nullable-typed "
            "query without a "
            "default, so the "
            "request still "
            "requires it, "
            "with a minimum "
            "length. The "
            "independent case "
            "observes that "
            "missing-value "
            "behavior and the "
            "selected OpenAPI "
            "parameter.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial006c_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial006c"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial007_py310.py": {
            "rationale": "The exact source "
            "example adds title "
            "metadata and a "
            "minimum length to an "
            "optional query. The "
            "independent case "
            "submits a too-short "
            "value and selects "
            "the generated "
            "parameter schema; "
            "its title text and "
            "response object are "
            "independently "
            "chosen.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial007_py310.py",
                    "start_line": 6,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-title-description-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial007"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial007_an_py310.py": {
            "rationale": "The exact source "
            "example adds "
            "title metadata "
            "and a minimum "
            "length to an "
            "optional query. "
            "The independent "
            "case submits a "
            "too-short value "
            "and selects the "
            "generated "
            "parameter schema; "
            "its title text "
            "and response "
            "object are "
            "independently "
            "chosen.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial007_an_py310.py",
                    "start_line": 8,
                    "end_line": 11,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-title-description-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial007"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial008_py310.py": {
            "rationale": "The exact source "
            "example adds title, "
            "description, and a "
            "minimum length to an "
            "optional query. The "
            "independent case "
            "submits a too-short "
            "value and selects "
            "the generated "
            "parameter schema "
            "using independent "
            "metadata text.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial008_py310.py",
                    "start_line": 6,
                    "end_line": 14,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-title-description-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial008"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial008_an_py310.py": {
            "rationale": "The exact source "
            "example adds "
            "title, "
            "description, and "
            "a minimum length "
            "to an optional "
            "query. The "
            "independent case "
            "submits a "
            "too-short value "
            "and selects the "
            "generated "
            "parameter schema "
            "using independent "
            "metadata text.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial008_an_py310.py",
                    "start_line": 8,
                    "end_line": 18,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-title-description-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial008"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial009_py310.py": {
            "rationale": "The exact source "
            "example binds a "
            "Python argument "
            "through the "
            "item-query alias. "
            "The independent case "
            "supplies that alias "
            "and selects its "
            "generated parameter "
            "schema; its response "
            "object is an "
            "independent echo.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial009_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial009"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial009_an_py310.py": {
            "rationale": "The exact source "
            "example binds a "
            "Python argument "
            "through the "
            "item-query alias. "
            "The independent "
            "case supplies "
            "that alias and "
            "selects its "
            "generated "
            "parameter schema; "
            "its response "
            "object is an "
            "independent echo.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial009_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial009"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial010_py310.py": {
            "rationale": "The exact source "
            "example combines the "
            "item-query alias, "
            "title/description, "
            "bounds, pattern, and "
            "deprecated metadata. "
            "The independent case "
            "submits an aliased "
            "pattern mismatch and "
            "selects the "
            "generated parameter "
            "schema; descriptive "
            "text and response "
            "object are "
            "independent.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial010_py310.py",
                    "start_line": 6,
                    "end_line": 18,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-pattern-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial010"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial010_an_py310.py": {
            "rationale": "The exact source "
            "example combines "
            "the item-query "
            "alias, "
            "title/description, "
            "bounds, pattern, "
            "and deprecated "
            "metadata. The "
            "independent case "
            "submits an "
            "aliased pattern "
            "mismatch and "
            "selects the "
            "generated "
            "parameter schema; "
            "descriptive text "
            "and response "
            "object are "
            "independent.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial010_an_py310.py",
                    "start_line": 8,
                    "end_line": 22,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-pattern-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial010"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial011_py310.py": {
            "rationale": "The exact source "
            "example declares an "
            "optional list-valued "
            "query. The "
            "independent case "
            "sends repeated query "
            "keys to exercise "
            "list extraction and "
            "selects the "
            "generated parameter "
            "schema; response "
            "formatting is an "
            "independent echo.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial011_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial011"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial011_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "an optional "
            "list-valued "
            "query. The "
            "independent case "
            "sends repeated "
            "query keys to "
            "exercise list "
            "extraction and "
            "selects the "
            "generated "
            "parameter schema; "
            "response "
            "formatting is an "
            "independent echo.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial011_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial011"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial012_py310.py": {
            "rationale": "The exact source "
            "example declares a "
            "list-valued query "
            "with a default list. "
            "The independent case "
            "observes both the "
            "omitted-query "
            "default and "
            "repeated-key list "
            "extraction, along "
            "with the generated "
            "parameter schema; "
            "the default values "
            "differ from the docs "
            "example.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial012_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial012"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial012_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "a list-valued "
            "query with a "
            "default list. The "
            "independent case "
            "observes both the "
            "omitted-query "
            "default and "
            "repeated-key list "
            "extraction, along "
            "with the "
            "generated "
            "parameter schema; "
            "the default "
            "values differ "
            "from the docs "
            "example.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial012_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial012"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial013_py310.py": {
            "rationale": "The exact source "
            "example declares a "
            "bare list query with "
            "an empty-list "
            "default. The "
            "independent case "
            "observes the omitted "
            "default and "
            "repeated-key "
            "extraction, plus its "
            "generated parameter "
            "schema.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial013_py310.py",
                    "start_line": 6,
                    "end_line": 7,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial013"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial013_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "a bare list query "
            "with an "
            "empty-list "
            "default. The "
            "independent case "
            "observes the "
            "omitted default "
            "and repeated-key "
            "extraction, plus "
            "its generated "
            "parameter schema.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial013_an_py310.py",
                    "start_line": 8,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial013"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial014_py310.py": {
            "rationale": "The exact source "
            "example declares an "
            "optional query "
            "excluded from "
            "OpenAPI. The "
            "independent case "
            "supplies it and "
            "selects the whole "
            "operation object to "
            "observe that the "
            "parameter is absent "
            "from the schema; the "
            "docs branch’s "
            "fallback text is "
            "application-owned.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial014_py310.py",
                    "start_line": 6,
                    "end_line": 9,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-exclude-schema-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial014"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial014_an_py310.py": {
            "rationale": "The exact source "
            "example declares "
            "an optional query "
            "excluded from "
            "OpenAPI. The "
            "independent case "
            "supplies it and "
            "selects the whole "
            "operation object "
            "to observe that "
            "the parameter is "
            "absent from the "
            "schema; the docs "
            "branch’s fallback "
            "text is "
            "application-owned.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial014_an_py310.py",
                    "start_line": 8,
                    "end_line": 11,
                    "role": "documented query parameter declaration and route signature",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-exclude-schema-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial014"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/query_params_str_validations/tutorial015_an_py310.py": {
            "rationale": "The exact source "
            "example applies "
            "an AfterValidator "
            "requiring an "
            "isbn- or imdb- "
            "prefix. The "
            "independent case "
            "observes valid "
            "and invalid "
            "prefixes plus the "
            "selected OpenAPI "
            "projection. The "
            "source app’s "
            "omitted-ID "
            "random.choice "
            "branch and item "
            "database lookup "
            "are "
            "application-owned "
            "and excluded.",
            "supporting_sources": [
                {
                    "path": "docs_src/query_params_str_validations/tutorial015_an_py310.py",
                    "start_line": 16,
                    "end_line": 19,
                    "role": "documented AfterValidator prefix rule",
                },
                {
                    "path": "docs_src/query_params_str_validations/tutorial015_an_py310.py",
                    "start_line": 22,
                    "end_line": 25,
                    "role": "documented query parameter declaration and route signature",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
                    "case_ids": ["fastapi.docs-example.query-params-str-validations.tutorial015"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
    }
)

if __package__:
    from scripts.atlas_documentation_example_review_wave_e import (
        DOC_EXAMPLE_CITATION_WAVE_E,
    )
else:
    from atlas_documentation_example_review_wave_e import DOC_EXAMPLE_CITATION_WAVE_E

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_E)

if __package__:
    from scripts.atlas_documentation_example_review_wave_f import (
        DOC_EXAMPLE_CITATION_WAVE_F,
    )
    from scripts.atlas_documentation_example_review_wave_g import (
        DOC_EXAMPLE_CITATION_WAVE_G,
    )
    from scripts.atlas_documentation_example_review_wave_h import (
        DOC_EXAMPLE_CITATION_WAVE_H,
    )
    from scripts.atlas_documentation_example_review_wave_i_security import (
        DOC_EXAMPLE_CITATION_WAVE_I,
    )
    from scripts.atlas_documentation_example_review_wave_j_custom_docs import (
        DOC_EXAMPLE_CITATION_WAVE_J,
    )
    from scripts.atlas_documentation_example_review_wave_k_reuse import (
        DOC_EXAMPLE_CITATION_WAVE_K,
    )
else:
    from atlas_documentation_example_review_wave_f import DOC_EXAMPLE_CITATION_WAVE_F
    from atlas_documentation_example_review_wave_g import DOC_EXAMPLE_CITATION_WAVE_G
    from atlas_documentation_example_review_wave_h import DOC_EXAMPLE_CITATION_WAVE_H
    from atlas_documentation_example_review_wave_i_security import (
        DOC_EXAMPLE_CITATION_WAVE_I,
    )
    from atlas_documentation_example_review_wave_j_custom_docs import (
        DOC_EXAMPLE_CITATION_WAVE_J,
    )
    from atlas_documentation_example_review_wave_k_reuse import (
        DOC_EXAMPLE_CITATION_WAVE_K,
    )

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_F)
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_G)
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_H)
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_I)
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_J)
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(DOC_EXAMPLE_CITATION_WAVE_K)

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/cookie_param_models/tutorial001_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example binds a Pydantic cookie model at an item route. "
                "The independent cookie-model case observes response status, headers, body, and "
                "the route parameter schema on a separate session route. This is a partial "
                "binding/schema sample: it does not establish the source field names and literals, "
                "missing required-cookie behavior, duplicate-cookie parsing, or every optional-cookie branch."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/cookie_param_models/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 15,
                    "role": "documented cookie model fields and Cookie-bound endpoint",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.tutorial-cookie-param-models.cookie-model"
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
        "docs_src/custom_docs_ui/tutorial001_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example disables built-in documentation routes and defines "
                "a custom Swagger UI HTML route. The independent case observes a separately named "
                "custom-docs response and an OpenAPI info projection. It does not establish the "
                "source route path or HTML/assets, OAuth redirect route, ReDoc route, or disabled-route misses."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                    "start_line": 8,
                    "end_line": 19,
                    "role": "disabled built-in docs and documented custom Swagger UI route",
                },
                {
                    "path": "docs_src/custom_docs_ui/tutorial001_py310.py",
                    "start_line": 22,
                    "end_line": 33,
                    "role": "additional OAuth redirect and ReDoc routes outside the selected case",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                    "case_ids": [
                        "fastapi.docs.openapi-interface.how-to-custom-docs-ui-assets.custom-docs-assets"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/custom_response/tutorial006c_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example declares a RedirectResponse with status 302. "
                "The selected case retrieves OpenAPI and observes the response-status slot for "
                "the source path plus the retrieval status. It does not send a request to the "
                "redirect route or establish Location, response-body, or redirect-follow behavior."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/custom_response/tutorial006c_py310.py",
                    "start_line": 7,
                    "end_line": 9,
                    "role": "documented redirect response class, status, and endpoint",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/custom-response-tutorial006c-openapi-review.yaml",
                    "case_ids": ["fastapi.custom-response.tutorial006c.openapi-response-status"],
                    "observation_selectors": ["http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/dataclasses_/tutorial003_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example nests dataclass items inside an author dataclass, "
                "uses a default factory, accepts nested request items, and declares response models. "
                "The independent case samples nested request/response projection and the related "
                "OpenAPI schemas. It does not establish all source records, omission/default "
                "combinations, coercion edges, or validation failures."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dataclasses_/tutorial003_py310.py",
                    "start_line": 7,
                    "end_line": 24,
                    "role": "nested dataclass definitions, default factory, and request endpoint",
                },
                {
                    "path": "docs_src/dataclasses_/tutorial003_py310.py",
                    "start_line": 27,
                    "end_line": 54,
                    "role": "documented response-model endpoint and returned author records",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/pydantic-dataclasses-tutorial003-upstream-wave.yaml",
                    "case_ids": [
                        "fastapi.pydantic-dataclasses.tutorial003-nested-request-and-defaults"
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/dependencies/tutorial008b_an_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example catches a yielded-resource OwnerError and translates "
                "it to an HTTP exception in an Annotated dependency route. The independent case "
                "samples this exception-translation behavior through response body and status. "
                "It does not claim cleanup ordering, suppression/re-raise variants, exact source "
                "values, or the unrelated not-found branch."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008b_an_py310.py",
                    "start_line": 18,
                    "end_line": 22,
                    "role": "documented yielded dependency and OwnerError translation",
                },
                {
                    "path": "docs_src/dependencies/tutorial008b_an_py310.py",
                    "start_line": 25,
                    "end_line": 32,
                    "role": "route dependency use and ownership-error branch",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
                    "case_ids": [
                        "fastapi.dependencies.tutorial008b.annotated-parameter-exception-translation"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependencies/tutorial011_an_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example uses a callable FixedContentQueryChecker dependency "
                "whose predicate checks whether configured text occurs in a non-empty query value. "
                "The independent matching and nonmatching cases observe response body, ordered "
                "headers, and status for two query samples. They do not cover an absent/empty query, "
                "other configured text, or other advanced-dependency forms."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial011_an_py310.py",
                    "start_line": 8,
                    "end_line": 23,
                    "role": "documented callable checker, predicate, and route dependency",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/advanced_dependencies.yaml",
                    "case_ids": [
                        "fastapi.docs.advanced-dependencies.matching-query",
                        "fastapi.docs.advanced-dependencies.nonmatching-query",
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/dependencies/tutorial012_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example installs two required header dependencies globally "
                "for its item and user routes. The independent case exercises the global-dependency "
                "wiring on those route shapes and observes response status/body plus selected path "
                "schema. It does not claim the source header literals, every missing/invalid-header "
                "combination, or exact error details."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial012_py310.py",
                    "start_line": 4,
                    "end_line": 25,
                    "role": "documented required header dependencies, global registration, and routes",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-tutorial012-default-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial012.global-headers-default"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/dependency_testing/tutorial001_an_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example replaces a common query-parameter dependency through "
                "dependency_overrides. The independent ASGI case samples override effects on item "
                "and user routes, including plain and Annotated dependency declarations, and "
                "observes response body/status. It does not execute the source TestClient assertions "
                "or claim all source parameter values, dependency call ordering, or override lifecycle."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependency_testing/tutorial001_an_py310.py",
                    "start_line": 9,
                    "end_line": 20,
                    "role": "documented dependency signature and item/user route use",
                },
                {
                    "path": "docs_src/dependency_testing/tutorial001_an_py310.py",
                    "start_line": 23,
                    "end_line": 30,
                    "role": "source TestClient declaration and dependency override registration",
                },
                {
                    "path": "docs_src/dependency_testing/tutorial001_an_py310.py",
                    "start_line": 33,
                    "end_line": 57,
                    "role": "source TestClient assertions outside the ASGI workflow boundary",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/atlas-testing-websocket-dependency-overrides.yaml",
                    "case_ids": ["fastapi.atlas-testing-dependency.overrides"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/generate_clients/tutorial001_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example defines request/response models and item routes used "
                "as an API input for client generation. The independent case samples POST/GET "
                "responses and the related OpenAPI paths/schemas. It does not perform code "
                "generation, compile generated clients, or exercise a client-language runtime."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/generate_clients/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 26,
                    "role": "documented item models and API routes used for client generation",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/generate-clients-tutorial001-upstream.yaml",
                    "case_ids": [
                        "fastapi.test.test-tutorial-test-generate-clients-test-tutorial001.client-requests-and-openapi"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/path_operation_advanced_configuration/tutorial002_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example supplies a custom unique-operation-ID function "
                "that derives the identifier from a route name. The independent case samples "
                "one route response and its OpenAPI operation identifier. It does not establish "
                "collision handling across arbitrary route names, routers, or tags."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial002_py310.py",
                    "start_line": 5,
                    "end_line": 14,
                    "role": "documented unique-operation-ID function, app configuration, and route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial002-upstream.yaml",
                    "case_ids": ["fastapi.path-operation-advanced-configurations.tutorial002"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/path_operation_advanced_configuration/tutorial006_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example reads the raw request body and supplies a manual "
                "OpenAPI requestBody schema for a route that returns parsed data. The independent "
                "case observes one request/response and that requestBody projection. It does not "
                "establish arbitrary extension merging, malformed-body behavior, or every source "
                "field and validation/error path."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial006_py310.py",
                    "start_line": 6,
                    "end_line": 14,
                    "role": "documented raw-body reader and parsed response shape",
                },
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial006_py310.py",
                    "start_line": 17,
                    "end_line": 40,
                    "role": "manual OpenAPI requestBody extension and request handling",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial006-upstream.yaml",
                    "case_ids": ["fastapi.path-operation-advanced-configurations.tutorial006"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/path_params/tutorial004_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example declares a path converter and returns the captured "
                "suffix as data. The independent file-path and root-file-path cases observe route "
                "status/body, while a separate OpenAPI case observes the path parameter projection. "
                "This does not claim general path normalization, filesystem access/security, or "
                "unbounded URL-form behavior beyond the selected requests."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params/tutorial004_py310.py",
                    "start_line": 6,
                    "end_line": 8,
                    "role": "documented path converter and captured path value response",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial004_test_file_path.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial004-test-file-path"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial004_test_root_file_path.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial004-test-root-file-path"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial004_test_openapi_schema.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial004-test-openapi-schema"
                    ],
                    "observation_selectors": ["http.status", "openapi.paths"],
                },
            ],
        },
        "docs_src/schema_extra_example/tutorial002_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example attaches example metadata to Pydantic fields. The "
                "independent case observes the corresponding OpenAPI schema projection and an "
                "HTTP status sample. The schema observation does not establish acceptance or "
                "rejection for each illustrated value, response bodies, or Swagger rendering."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/schema_extra_example/tutorial002_py310.py",
                    "start_line": 7,
                    "end_line": 16,
                    "role": "documented field-level examples and request route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml",
                    "case_ids": ["fastapi.schema-extra-example.field-examples"],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/schema_extra_example/tutorial004_an_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example declares multiple examples on an Annotated Body "
                "parameter. The independent case observes the requestBody schema projection and "
                "HTTP status for selected requests; it does not submit every documented example "
                "or claim their validation outcomes, response bodies, or Swagger rendering."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/schema_extra_example/tutorial004_an_py310.py",
                    "start_line": 16,
                    "end_line": 43,
                    "role": "documented Annotated Body examples and request handler",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml",
                    "case_ids": ["fastapi.schema-extra-example.body-examples-several"],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/schema_extra_example/tutorial005_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example declares named OpenAPI example objects for a body "
                "parameter. The independent case observes the examples projection and HTTP status "
                "for selected requests. It does not establish request acceptance/rejection for "
                "each named value, response bodies, or Swagger rendering."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/schema_extra_example/tutorial005_py310.py",
                    "start_line": 14,
                    "end_line": 49,
                    "role": "documented named OpenAPI body examples and route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml",
                    "case_ids": ["fastapi.schema-extra-example.openapi-example-objects"],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/server_sent_events/tutorial001_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example exposes four sync/async and annotated/unannotated "
                "generator routes returning event-stream responses. The independent stream-routes "
                "case observes aggregate response body bytes, ordered headers, and status for its "
                "selected routes. It does not establish send-chunk boundaries, timing, backpressure, "
                "disconnect/cancellation, or reconnect behavior; the OpenAPI-only case has no "
                "non-empty selector intersection with this source row and is not linked here."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/server_sent_events/tutorial001_py310.py",
                    "start_line": 10,
                    "end_line": 19,
                    "role": "documented stream item model and source records",
                },
                {
                    "path": "docs_src/server_sent_events/tutorial001_py310.py",
                    "start_line": 22,
                    "end_line": 43,
                    "role": "four documented event-stream route declaration forms",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial001-upstream.yaml",
                    "case_ids": ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/server_sent_events/tutorial005_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example maps prompt words to token events and then emits a "
                "terminal event. The independent case observes aggregate response bytes, ordered "
                "headers, and status for a stream request. It does not establish chunk boundaries, "
                "timing, backpressure, disconnect/cancellation, reconnect behavior, or other prompt "
                "and event-field combinations; the OpenAPI-only case has no non-empty selector "
                "intersection and is not linked here."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/server_sent_events/tutorial005_py310.py",
                    "start_line": 10,
                    "end_line": 19,
                    "role": "documented prompt model and token/done event generation",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial005-upstream.yaml",
                    "case_ids": [
                        "fastapi.tutorial.server-sent-events.tutorial005.post-chat-stream"
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/using_request_directly/tutorial001_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example reads the client host from a Request and returns it "
                "with a path parameter. The independent case observes its route response/status and "
                "a selected OpenAPI path projection. It does not establish absent-client behavior "
                "or other Request attributes and scope values."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/using_request_directly/tutorial001_py310.py",
                    "start_line": 6,
                    "end_line": 9,
                    "role": "documented Request client-host access and route response",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/using_request_directly.yaml",
                    "case_ids": ["fastapi.docs.using-request-directly.client-host"],
                    "observation_selectors": [
                        "docs.response.headers",
                        "docs.response.status",
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/websockets_/tutorial002_py310.py": {
            "rationale": (
                "The FastAPI 0.141.1 example serves an HTTP page and a WebSocket route with "
                "cookie-or-query authentication, an optional integer query value, path data, and "
                "a message loop. The independent case observes the page response and selected "
                "WebSocket message/order/close behavior across representative sessions. It does "
                "not run the page's JavaScript in a browser or establish browser networking, live "
                "timing, or every cookie/query combination."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/websockets_/tutorial002_py310.py",
                    "start_line": 14,
                    "end_line": 61,
                    "role": "documented HTML page and root HTTP route",
                },
                {
                    "path": "docs_src/websockets_/tutorial002_py310.py",
                    "start_line": 64,
                    "end_line": 89,
                    "role": "documented WebSocket authentication dependency and message route",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/atlas-testing-websocket-websockets-tutorial002.yaml",
                    "case_ids": ["fastapi.atlas-testing.websocket-tutorial002"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "websocket.close_code",
                        "websocket.event_order",
                        "websocket.messages",
                    ],
                }
            ],
        },
    }
)

# Direct-response and base64-byte examples use independent ASGI workloads with
# distinct route values. These mappings cover only the listed observations.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/response_cookies/tutorial001_py310.py": {
            "rationale": (
                "The pinned example returns a JSONResponse from `/cookie/` and sets a response cookie. "
                "The independent ASGI case keeps the route and method shape but uses a different response "
                "message and cookie name/value, and observes status, ordered response headers, and body "
                "bytes. This samples the direct response-cookie path; it does not claim TestClient parity."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/response_cookies/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 12,
                    "role": "documented JSONResponse route that sets a response cookie",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/response-cookie-direct-wave.yaml",
                    "case_ids": ["fastapi.response.cookies.direct-jsonresponse-set-cookie"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/response_directly/tutorial001_py310.py": {
            "rationale": (
                "The pinned route validates an Item, passes it through jsonable_encoder, and returns a "
                "JSONResponse. The independent inventory route uses a different model, path, field names, "
                "and values; it observes only status, ordered headers, and response-body bytes for that "
                "analogous direct JSON response. A separate case observes the independent app's full "
                "OpenAPI document and status. These are partial samples of the route and generated schema, "
                "not claims of matching the tutorial payload or complete schema."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/response_directly/tutorial001_py310.py",
                    "start_line": 9,
                    "end_line": 12,
                    "role": "documented Pydantic response input model",
                },
                {
                    "path": "docs_src/response_directly/tutorial001_py310.py",
                    "start_line": 18,
                    "end_line": 21,
                    "role": "documented route using jsonable_encoder and JSONResponse",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/response-directly-tutorial001-wave.yaml",
                    "case_ids": [
                        "fastapi.response-directly.tutorial001.openapi-document",
                        "fastapi.response-directly.tutorial001.path-response",
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                    ],
                },
            ],
        },
        "docs_src/json_base64_bytes/tutorial001_py310.py": {
            "rationale": (
                "The pinned example configures base64 validation, serialization, and round-trip models. "
                "The independent workflow sends `independent-input` and `roundtrip-input` as distinct valid "
                "base64 payloads and returns `independent-output` from its GET route, rather than reusing "
                "the source's hardcoded `hello` value or the upstream test payloads. It observes HTTP "
                "status, ordered headers, and body bytes for the decode, encode, round-trip, and OpenAPI "
                "requests, plus one selected DataInput OpenAPI schema pointer. "
                "This is a partial sample of those workflows and that schema field, not all bytes values or "
                "every generated schema."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/json_base64_bytes/tutorial001_py310.py",
                    "start_line": 5,
                    "end_line": 26,
                    "role": "documented base64 input, output, and round-trip model configuration",
                },
                {
                    "path": "docs_src/json_base64_bytes/tutorial001_py310.py",
                    "start_line": 32,
                    "end_line": 46,
                    "role": "documented decode, encode, and round-trip routes",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/json_base64_bytes.yaml",
                    "case_ids": ["fastapi.docs.json-base64-bytes.input-output-and-schema"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
    }
)

DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    STRICT_CONTENT_TYPE_DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS
)

# Focused mappings for the five extra-models response-model examples. Their
# recipes use distinct data and observe response bytes/status plus selected
# OpenAPI paths and documents.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/extra_models/tutorial001_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 accepts the flat UserIn model, creates a UserInDB value with a hashed_password, "
                "and returns it through response_model=UserOut. The independent workflow uses the same model "
                "shape with different user/password values and a separate hash prefix; it observes response "
                "status/body and selected OpenAPI paths and schemas. This maps request/response model filtering "
                "and schema generation only, not the tutorial's hasher, print, values, or TestClient semantics."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/extra_models/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 24,
                    "role": "documented flat input, output, and database user model shapes",
                },
                {
                    "path": "docs_src/extra_models/tutorial001_py310.py",
                    "start_line": 31,
                    "end_line": 41,
                    "role": "documented user conversion and response_model route",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml",
                    "case_ids": ["fastapi.extra-models.tutorial001-flat-user-models"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/extra_models/tutorial002_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 builds UserIn, UserOut, and UserInDB from a shared UserBase model and returns "
                "the database-shaped value through response_model=UserOut. The independent workflow reproduces "
                "that inheritance shape with separate values and hashing; it observes response status/body and "
                "selected OpenAPI paths and schemas. This maps model inheritance, response filtering, and the "
                "selected schema output, not the tutorial's helper implementation, values, or TestClient semantics."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/extra_models/tutorial002_py310.py",
                    "start_line": 7,
                    "end_line": 23,
                    "role": "documented shared base, input, output, and database user model inheritance",
                },
                {
                    "path": "docs_src/extra_models/tutorial002_py310.py",
                    "start_line": 29,
                    "end_line": 39,
                    "role": "documented user conversion and response_model route",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml",
                    "case_ids": ["fastapi.extra-models.tutorial002-inherited-user-models"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/extra_models/tutorial003_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 declares PlaneItem | CarItem as the route response model. The independent "
                "workflow uses the same union model shape and exercises one car-shaped and one plane-shaped "
                "response with different item IDs and data, then inspects the selected OpenAPI paths and model "
                "schemas. It maps the observed union response filtering and schema only, not the tutorial's item "
                "values or TestClient semantics."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/extra_models/tutorial003_py310.py",
                    "start_line": 7,
                    "end_line": 18,
                    "role": "documented base, car, and plane response model definitions",
                },
                {
                    "path": "docs_src/extra_models/tutorial003_py310.py",
                    "start_line": 21,
                    "end_line": 33,
                    "role": "documented variant data and union response_model route",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml",
                    "case_ids": ["fastapi.extra-models.tutorial003-union-response-model"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/extra_models/tutorial004_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 returns a list of dictionaries through response_model=list[Item]. The independent "
                "workflow uses the same Item fields and typed-list route with different catalog values; it observes "
                "the response status/body and selected OpenAPI path and Item schema. This maps list response "
                "validation/filtering and its selected schema, not the tutorial's literal rows or TestClient semantics."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/extra_models/tutorial004_py310.py",
                    "start_line": 7,
                    "end_line": 20,
                    "role": "documented Item response model, list data, and typed-list route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml",
                    "case_ids": ["fastapi.extra-models.tutorial004-typed-list-response"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/extra_models/tutorial005_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 declares dict[str, float] as the response model. The independent workflow uses "
                "the same typed-map route with different keys and values; it observes response status/body and the "
                "OpenAPI paths containing the map response schema. This maps the typed mapping response and its "
                "path-level schema only, not the tutorial's literal values or TestClient semantics."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/extra_models/tutorial005_py310.py",
                    "start_line": 6,
                    "end_line": 8,
                    "role": "documented dict[str, float] response model and route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml",
                    "case_ids": ["fastapi.extra-models.tutorial005-typed-map-response"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
    }
)

# Focused mappings for yield-dependency exception handling, scalar Body
# constraints, nested query/cookie dependencies, and ASGI lifecycle inputs.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/dependencies/tutorial008c_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's direct-parameter example injects an exception into a yield dependency, "
                "catches InternalError without re-raising, and has an endpoint branch that raises it. The "
                "independent workflow exercises the corresponding direct-signature route and observes HTTP "
                "status/body; it separately records an application-exception outcome, which this mapping does "
                "not claim. The case also contains a separate Annotated route. This mapping does not claim "
                "stdout, the tutorial's literals, or behavior outside these inputs."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008c_py310.py",
                    "start_line": 10,
                    "end_line": 26,
                    "role": "documented direct Depends yield cleanup and endpoint exception branch",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial008c.suppressed-yield-exception"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependencies/tutorial008c_an_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's Annotated example injects an exception into a yield dependency, catches "
                "InternalError without re-raising, and has an endpoint branch that raises it. The independent "
                "workflow exercises the corresponding Annotated route and observes HTTP status/body; it separately "
                "records an application-exception outcome, which this mapping does not claim. The case also "
                "contains a separate direct-signature route. This mapping does not claim stdout, the tutorial's "
                "literals, or behavior outside these inputs."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008c_an_py310.py",
                    "start_line": 12,
                    "end_line": 28,
                    "role": "documented Annotated Depends yield cleanup and endpoint exception branch",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial008c.suppressed-yield-exception"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependencies/tutorial008d_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's direct-parameter example injects an exception into a yield dependency, "
                "records it, and re-raises it. The independent workflow exercises the corresponding "
                "direct-signature route and observes HTTP status/body. Although the case also records an "
                "application error class, this mapping does not claim that selector. The case contains a separate "
                "Annotated route; this mapping does not claim stdout, the tutorial's literals, or behavior outside "
                "these inputs."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008d_py310.py",
                    "start_line": 10,
                    "end_line": 26,
                    "role": "documented direct Depends yield cleanup and re-raised endpoint exception",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial008d.reraised-yield-exception"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependencies/tutorial008d_an_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's Annotated example injects an exception into a yield dependency, records it, "
                "and re-raises it. The independent workflow exercises the corresponding Annotated route and "
                "observes HTTP status/body. Although the case also records an application error class, this "
                "mapping does not claim that selector. The case contains a separate direct-signature route; this "
                "mapping does not claim stdout, the tutorial's literals, or behavior outside these inputs."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008d_an_py310.py",
                    "start_line": 12,
                    "end_line": 28,
                    "role": "documented Annotated Depends yield cleanup and re-raised endpoint exception",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial008d.reraised-yield-exception"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/security/tutorial003_an_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's Annotated example wires OAuth2 bearer extraction through nested current-user "
                "and active-user dependencies. The independent case uses the same Annotated dependency shape and "
                "sends a token for a disabled user; it substitutes a small dict-backed user store for the "
                "tutorial's Pydantic models and observes response status, ordered headers, and body bytes. This "
                "mapping covers only that authenticated inactive-user request, not the token route or password flow."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/security/tutorial003_an_py310.py",
                    "start_line": 58,
                    "end_line": 74,
                    "role": "documented Annotated bearer and nested active-user dependency checks",
                },
                {
                    "path": "docs_src/security/tutorial003_an_py310.py",
                    "start_line": 90,
                    "end_line": 94,
                    "role": "documented route depending on the Annotated active-user dependency",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/security-oauth2-inactive-user-source-wave.yaml",
                    "case_ids": ["fastapi.security.tutorial-003.oauth2-inactive-user"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/body_multiple_params/tutorial004_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 declares the importance field as a direct Body(gt=0) scalar inside a request "
                "that also contains Item and User models. The independent workflow isolates that same "
                "positive-integer constraint on a scalar JSON body and observes status/body for a positive value and zero. "
                "It does not claim multi-body embedding, Item/User parsing, the optional q parameter, or the "
                "tutorial's route and response literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/body_multiple_params/tutorial004_py310.py",
                    "start_line": 19,
                    "end_line": 30,
                    "role": "documented direct Body(gt=0) importance field and endpoint result",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/body-gt-zero.yaml",
                    "case_ids": [
                        "fastapi.body.gt-zero.positive-integer",
                        "fastapi.body.gt-zero.zero-rejected",
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/body_multiple_params/tutorial004_an_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 declares the importance field as Annotated[int, Body(gt=0)] inside a request "
                "that also contains Item and User models. The independent workflow isolates that same "
                "positive-integer constraint on a scalar JSON body and observes status/body for a positive value and zero. "
                "It does not claim multi-body embedding, Item/User parsing, the optional q parameter, or the "
                "tutorial's route and response literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/body_multiple_params/tutorial004_an_py310.py",
                    "start_line": 21,
                    "end_line": 32,
                    "role": "documented Annotated Body(gt=0) importance field and endpoint result",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/body-gt-zero.yaml",
                    "case_ids": [
                        "fastapi.body.gt-zero.annotated-positive-integer",
                        "fastapi.body.gt-zero.annotated-zero-rejected",
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependencies/tutorial005_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's direct/default-parameter example nests a query extractor and a cookie fallback. "
                "The independent workload covers query precedence, cookie fallback, absence of both values, and "
                "the query/cookie OpenAPI parameters, but its Python signatures use Annotated declarations. This "
                "is a behavior-level mapping only; it does not establish parity for the direct declaration style."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial005_py310.py",
                    "start_line": 6,
                    "end_line": 20,
                    "role": "documented direct query dependency, cookie fallback, and endpoint",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-tutorial005-query-cookie-fallback.yaml",
                    "case_ids": [
                        "fastapi.dependencies.tutorial005.query-cookie.fallback",
                        "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
                        "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
                        "fastapi.dependencies.tutorial005.query-cookie.openapi-parameters",
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/dependencies/tutorial005_an_py310.py": {
            "rationale": (
                "FastAPI 0.141.1's Annotated example nests the same query extractor and cookie fallback. The "
                "independent workload uses Annotated dependency declarations and covers query precedence, cookie "
                "fallback, absence of both values, and the query/cookie OpenAPI parameters. The mapping is limited "
                "to those inputs and observations; it does not claim unrelated dependency behavior."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial005_an_py310.py",
                    "start_line": 8,
                    "end_line": 25,
                    "role": "documented Annotated query dependency, cookie fallback, and endpoint",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-tutorial005-query-cookie-fallback.yaml",
                    "case_ids": [
                        "fastapi.dependencies.tutorial005.query-cookie.fallback",
                        "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
                        "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
                        "fastapi.dependencies.tutorial005.query-cookie.openapi-parameters",
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/app_testing/tutorial003_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 registers startup work with on_event and the example runs a request inside a "
                "TestClient context. The independent workflow observes startup/shutdown through raw ASGI lifespan "
                "events and also requests the initialized item, but this mapping claims only the lifecycle "
                "selectors. Direct ASGI lifecycle inputs do not establish TestClient context-manager parity or "
                "the example's import-time deprecation warning."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/app_testing/tutorial003_py310.py",
                    "start_line": 9,
                    "end_line": 24,
                    "role": "documented startup callback, item route, and TestClient-scoped request",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/testing-tutorial003-lifecycle-upstream.yaml",
                    "case_ids": [
                        "fastapi.test.test-tutorial-test-testing-test-tutorial003.startup-items-lifecycle"
                    ],
                    "observation_selectors": [
                        "asgi.lifespan.application_errors",
                        "asgi.lifespan.event_order",
                        "asgi.lifespan.shutdown",
                        "asgi.lifespan.startup",
                        "asgi.lifespan.workload_trace",
                    ],
                }
            ],
        },
        "docs_src/app_testing/tutorial004_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 defines a context-manager lifespan that adds items before yield and clears them "
                "afterward; its example asserts those states around a TestClient context. The independent workflow "
                "drives startup/shutdown with raw ASGI lifespan events and requests an item while the app is "
                "started. This mapping claims only lifecycle events and the workload trace; it does not claim the "
                "HTTP response, TestClient context-manager parity, or the tutorial's before/after state assertions."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/app_testing/tutorial004_py310.py",
                    "start_line": 9,
                    "end_line": 23,
                    "role": "documented context-manager lifespan cleanup and dependent route",
                },
                {
                    "path": "docs_src/app_testing/tutorial004_py310.py",
                    "start_line": 30,
                    "end_line": 43,
                    "role": "documented TestClient lifecycle context and before/after state assertions",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/first-steps-application-testing-upstream.yaml",
                    "case_ids": ["fastapi.application-testing.lifespan-items"],
                    "observation_selectors": [
                        "asgi.lifespan.application_errors",
                        "asgi.lifespan.event_order",
                        "asgi.lifespan.shutdown",
                        "asgi.lifespan.startup",
                        "asgi.lifespan.workload_trace",
                    ],
                }
            ],
        },
    }
)

# Numeric path-parameter tutorials: every included default-style and Annotated
# source has its own independently routed input case. The route signatures keep
# the respective declaration form, and cases observe only the documented HTTP
# binding/validation/schema effects for that exact source.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/path_params_numeric_validations/tutorial001_py310.py": {
            "rationale": (
                "This independent route preserves the example's default-style Path declaration, "
                "optional aliased query parameter, and integer path type. Its distinct case sends "
                "requests with the alias absent and present, rejects a non-integer path, and reads "
                "the generated OpenAPI response as raw HTTP bytes. It does not claim the source "
                "route or response literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial001_py310.py",
                    "start_line": 1,
                    "end_line": 14,
                    "role": "default-style Path metadata and optional aliased Query example",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial001-default"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial001_an_py310.py": {
            "rationale": (
                "This independent route preserves the example's Annotated Path declaration, "
                "optional aliased Query parameter, and integer path type. Its distinct case sends "
                "requests with the alias absent and present, rejects a non-integer path, and reads "
                "the generated OpenAPI response as raw HTTP bytes. It does not claim the source "
                "route or response literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial001_an_py310.py",
                    "start_line": 1,
                    "end_line": 16,
                    "role": "Annotated Path metadata and optional aliased Query example",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial001-annotated"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial002_py310.py": {
            "rationale": (
                "This independent route preserves the example's required query-first signature and "
                "default-style Path declaration. Its distinct case sends the required query, omits "
                "it to exercise requiredness, rejects a non-integer path, and reads the generated "
                "OpenAPI response as raw HTTP bytes. It does not claim the source route or literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial002_py310.py",
                    "start_line": 1,
                    "end_line": 11,
                    "role": "required query before default-style Path declaration",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial002-default"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial002_an_py310.py": {
            "rationale": (
                "This independent route preserves the example's Annotated Path declaration with "
                "the required query first. Its distinct case sends the required query, omits it to "
                "exercise requiredness, rejects a non-integer path, and reads the generated OpenAPI "
                "response as raw HTTP bytes. It does not claim source literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial002_an_py310.py",
                    "start_line": 1,
                    "end_line": 15,
                    "role": "required query before Annotated Path declaration",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial002-annotated"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial003_py310.py": {
            "rationale": (
                "This independent route preserves the example's keyword-only marker, placing the "
                "Path-declared item identifier before a required query. Its distinct case sends a "
                "valid request, omits the required query, rejects a non-integer path, and reads the "
                "generated OpenAPI response as raw HTTP bytes. It does not claim source literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial003_py310.py",
                    "start_line": 1,
                    "end_line": 11,
                    "role": "keyword-only parameter ordering with default-style Path",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial003-default"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial003_an_py310.py": {
            "rationale": (
                "This independent route preserves the example's Annotated Path declaration before "
                "a required query without a keyword-only marker. Its distinct case sends a valid "
                "request, omits the required query, rejects a non-integer path, and reads the "
                "generated OpenAPI response as raw HTTP bytes. It does not claim source literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial003_an_py310.py",
                    "start_line": 1,
                    "end_line": 15,
                    "role": "Annotated Path declaration before required query without `*`",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial003-annotated"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial004_py310.py": {
            "rationale": (
                "This independent route preserves the default-style Path declaration with the "
                "inclusive ge=1 bound and a required query. Its distinct case accepts item_id 1, "
                "rejects 0, and reads the generated OpenAPI response as raw HTTP bytes. It does not "
                "claim source route literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial004_py310.py",
                    "start_line": 1,
                    "end_line": 13,
                    "role": "default-style integer Path with the inclusive lower bound",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial004-default"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial004_an_py310.py": {
            "rationale": (
                "This independent route preserves the Annotated Path declaration with the "
                "inclusive ge=1 bound and a required query. Its distinct case accepts item_id 1, "
                "rejects 0, and reads the generated OpenAPI response as raw HTTP bytes. It does not "
                "claim source route literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial004_an_py310.py",
                    "start_line": 1,
                    "end_line": 15,
                    "role": "Annotated integer Path with the inclusive lower bound",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial004-annotated"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial005_py310.py": {
            "rationale": (
                "This independent route preserves the default-style Path declaration with gt=0 and "
                "le=1000 plus a required query. Its distinct case rejects 0 and 1001, accepts the "
                "upper endpoint 1000, and reads the generated OpenAPI response as raw HTTP bytes. "
                "It does not claim source route literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial005_py310.py",
                    "start_line": 1,
                    "end_line": 15,
                    "role": "default-style integer Path with exclusive and inclusive bounds",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial005-default"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial005_an_py310.py": {
            "rationale": (
                "This independent route preserves the Annotated Path declaration with gt=0 and "
                "le=1000 plus a required query. Its distinct case rejects 0 and 1001, accepts the "
                "upper endpoint 1000, and reads the generated OpenAPI response as raw HTTP bytes. "
                "It does not claim source route literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial005_an_py310.py",
                    "start_line": 1,
                    "end_line": 16,
                    "role": "Annotated integer Path with exclusive and inclusive bounds",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial005-annotated"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial006_py310.py": {
            "rationale": (
                "This independent route preserves the default-style Path ge=0/le=1000 bounds and "
                "required float Query gt=0/lt=10.5 constraints. Its distinct case accepts numeric "
                "path endpoints and in-range float values and rejects each exclusive/out-of-range "
                "boundary; it also reads raw OpenAPI response bytes. It does not claim source literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial006_py310.py",
                    "start_line": 1,
                    "end_line": 18,
                    "role": "default-style bounded integer Path and bounded float Query example",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial006-default"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/path_params_numeric_validations/tutorial006_an_py310.py": {
            "rationale": (
                "This independent route preserves the Annotated Path ge=0/le=1000 bounds and "
                "required Annotated float Query gt=0/lt=10.5 constraints. Its distinct case accepts "
                "numeric path endpoints and in-range float values and rejects each exclusive/out-of-range "
                "boundary; it also reads raw OpenAPI response bytes. It does not claim source literals."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/path_params_numeric_validations/tutorial006_an_py310.py",
                    "start_line": 1,
                    "end_line": 20,
                    "role": "Annotated bounded integer Path and bounded float Query example",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.path-params-numeric-validations.tutorial006-annotated"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
    }
)

# Additional-response tutorials: map each exact documented example source to
# independent runtime and/or OpenAPI observations already present in the input
# backlog. These links claim only the named behaviors, not the full examples.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/additional_responses/tutorial001_py310.py": {
            "rationale": (
                "The pinned example declares an Item response model and a modeled 404 response, "
                "then returns either a valid item or a JSONResponse error. The independent "
                "inventory workflow observes analogous success, not-found, and selected OpenAPI "
                "response/schema behavior using separate models, paths, and values. It does not "
                "claim the example's literals, complete OpenAPI document, or every response case."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/additional_responses/tutorial001_py310.py",
                    "start_line": 18,
                    "end_line": 22,
                    "role": "documented response model, modeled 404 response, and success/error branches",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/additional-responses.yaml",
                    "case_ids": [
                        "fastapi.docs.additional-responses.found",
                        "fastapi.docs.additional-responses.not-found",
                        "fastapi.docs.additional-responses.openapi",
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
                }
            ],
        },
        "docs_src/additional_responses/tutorial002_py310.py": {
            "rationale": (
                "The pinned example documents image/png as an alternate 200 content type and "
                "selects FileResponse from a query parameter. The independent inputs exercise a "
                "separate FileResponse route and inspect the analogous OpenAPI media-content "
                "declaration. They use an independent workload and do not claim the tutorial's "
                "file bytes, route values, or complete schema."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/additional_responses/tutorial002_py310.py",
                    "start_line": 14,
                    "end_line": 28,
                    "role": "documented alternate image/png response and query-selected FileResponse",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml",
                    "case_ids": [
                        "fastapi.additional-response-openapi-wave.media-content.test-openapi-schema"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/tutorial-additional-responses-file-response-review.yaml",
                    "case_ids": ["fastapi.tutorial-additional-responses.file-response"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                },
            ],
        },
        "docs_src/additional_responses/tutorial003_py310.py": {
            "rationale": (
                "The pinned example declares a Pydantic model for its 404 response and returns "
                "JSONResponse on the missing-item branch. Independent inputs sample an analogous "
                "not-found response plus selected OpenAPI response-schema pointers with different "
                "models, route names, and values. They do not claim the literal example payload "
                "or full generated schema."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/additional_responses/tutorial003_py310.py",
                    "start_line": 18,
                    "end_line": 37,
                    "role": "documented modeled 404 and 200 response declarations with runtime branches",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/additional-responses.yaml",
                    "case_ids": ["fastapi.docs.additional-responses.not-found"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml",
                    "case_ids": [
                        "fastapi.additional-response-openapi-wave.modeled-not-found.test-openapi-schema"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                },
            ],
        },
        "docs_src/additional_responses/tutorial004_py310.py": {
            "rationale": (
                "The pinned example combines 404, 302, and 403 response descriptions with an "
                "image/png 200 response, and selects FileResponse for an image query. Independent "
                "inputs sample the FileResponse path and selected OpenAPI status/content entries "
                "using separate routes and descriptions. They do not claim the tutorial's redirect "
                "runtime branch or complete schema."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/additional_responses/tutorial004_py310.py",
                    "start_line": 11,
                    "end_line": 30,
                    "role": "documented shared status responses, image content, and FileResponse branch",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml",
                    "case_ids": [
                        "fastapi.additional-response-openapi-wave.multiple-statuses.test-openapi-schema"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/tutorial-additional-responses-file-response-review.yaml",
                    "case_ids": ["fastapi.tutorial-additional-responses.file-response"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                },
            ],
        },
    }
)

# Function-scoped yield dependency examples: direct response input plus a
# separate, documented cleanup-order probe. The tutorial test only asserts the
# response value; neither mapping claims that it captures stdout or print order.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/server_sent_events/tutorial004_py310.py": {
            "rationale": (
                "This independent input exercises the documented SSE route from the beginning and after "
                "Last-Event-ID values 0 and 1. It compares status, ordered headers, and concatenated body "
                "bytes. It does not claim 15-second keepalive timing or ASGI send-chunk boundaries."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/server_sent_events/tutorial004_py310.py",
                    "start_line": 23,
                    "end_line": 31,
                    "role": "documented SSE event stream and Last-Event-ID resume behavior",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
                    "case_ids": ["fastapi.tutorial.server-sent-events.tutorial004.resume-stream"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/dependencies/tutorial008e_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 yields Rick from a function-scoped dependency and prints from its cleanup. "
                "The independent tutorial case sends the same `/users/me` request and has a follow-up "
                "request that exposes a workload cleanup event; only the first response's status and body "
                "match the upstream test assertions. The separate `first-response` action in the lifecycle "
                "case probes documented function-scope cleanup relative to a streamed response using an "
                "independent workload. These are partial inputs: the tutorial test does not assert cleanup, "
                "capture stdout, or assert print order."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008e_py310.py",
                    "start_line": 6,
                    "end_line": 15,
                    "role": "documented yielding dependency, cleanup print, function scope, and user route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-tutorials-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial008e.function-scope-yield-rick"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                    "case_ids": ["fastapi.dependencies.yield-scope-cleanup"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
            ],
        },
        "docs_src/dependencies/tutorial008e_an_py310.py": {
            "rationale": (
                "FastAPI 0.141.1 expresses the same function-scoped yield dependency with Annotated: it "
                "yields Rick and prints from cleanup. The independent tutorial case sends a separate "
                "`/users/me-annotated` request and has a follow-up request that exposes a workload cleanup event; "
                "only the first response's status and body match the upstream test assertions. The separate "
                "`first-response` action in the lifecycle case probes documented function-scope cleanup "
                "relative to a streamed response using an independent workload. These are partial inputs: "
                "the tutorial test does not assert cleanup, capture stdout, or assert print order."
            ),
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008e_an_py310.py",
                    "start_line": 8,
                    "end_line": 17,
                    "role": "documented Annotated yielding dependency, cleanup print, function scope, and user route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-tutorials-upstream.yaml",
                    "case_ids": [
                        "fastapi.dependencies.tutorial008e.annotated-function-scope-yield-rick"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                    "case_ids": ["fastapi.dependencies.yield-scope-cleanup"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
            ],
        },
    }
)

# Shard A: exact, source-backed workflow links for pending examples.
DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.update(
    {
        "docs_src/app_testing/tutorial002_py310.py": {
            "rationale": "The pinned example defines an HTTP route and a WebSocket endpoint tested through TestClient. This independent TestClient case observes only WebSocket messages; it does not establish the source HTTP route response, the TestClient harness/import behavior, or close/event-order semantics for this source.",
            "supporting_sources": [
                {
                    "path": "docs_src/app_testing/tutorial002_py310.py",
                    "start_line": 8,
                    "end_line": 31,
                    "role": "documented HTTP and WebSocket routes with TestClient exercises",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/testing_websockets.yaml",
                    "case_ids": ["fastapi.docs.testing-websockets.testclient-example"],
                    "observation_selectors": ["websocket.messages"],
                }
            ],
        },
        "docs_src/background_tasks/tutorial001_py310.py": {
            "rationale": "The pinned example schedules a post-response notification effect. The independent workflow observes a separate in-memory effect through a follow-up response, limited to body bytes, ordered headers, and status; it does not establish the source filesystem write or notification formatting.",
            "supporting_sources": [
                {
                    "path": "docs_src/background_tasks/tutorial001_py310.py",
                    "start_line": 6,
                    "end_line": 15,
                    "role": "documented background task scheduling and notification effect",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml",
                    "case_ids": [
                        "fastapi.docs.documentation-wave.http-behaviors.background-task-effect"
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/conditional_openapi/tutorial001_py310.py": {
            "rationale": "The pinned example configures the OpenAPI URL conditionally and exposes a normal route. The cited independent case observes the disabled OpenAPI endpoint and its response/document surface, not the Settings or environment decision that selects the URL and not the normal route response.",
            "supporting_sources": [
                {
                    "path": "docs_src/conditional_openapi/tutorial001_py310.py",
                    "start_line": 5,
                    "end_line": 16,
                    "role": "documented conditional OpenAPI URL configuration and ordinary route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                    "case_ids": [
                        "fastapi.docs.openapi-interface.how-to-conditional-openapi.disabled-schema-endpoint"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                    ],
                }
            ],
        },
        "docs_src/custom_response/tutorial001_py310.py": {
            "rationale": "The pinned example selects UJSONResponse for its route. The two cited cases observe the route response envelope and OpenAPI projection only; they do not establish UJSON encoding internals, optional dependency behavior, or response behavior beyond those selected observations.",
            "supporting_sources": [
                {
                    "path": "docs_src/custom_response/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 9,
                    "role": "documented UJSONResponse selection and item route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/custom-response-tutorial001-upstream.yaml",
                    "case_ids": [
                        "fastapi.custom-response.tutorial001.items-response",
                        "fastapi.custom-response.tutorial001.openapi",
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/dependencies/tutorial002_an_py310.py": {
            "rationale": "The pinned example uses a callable class as a dependency. The independent case samples class-based dependency resolution, response fields, and the route schema using different class/parameter names; it does not establish the source CommonQueryParams values or constructor customization.",
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial002_an_py310.py",
                    "start_line": 11,
                    "end_line": 25,
                    "role": "documented callable dependency class and injection into a route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                    "case_ids": [
                        "fastapi.docs.documentation-wave.dependencies-security.classes-as-dependencies"
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
        "docs_src/dependencies/tutorial008b_py310.py": {
            "rationale": "The pinned example catches a yielded-dependency error and translates it through the HTTP response path. The selected case observes one exception-translation response by body and status; it does not cover every not-found or owner-mismatch branch in the source.",
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial008b_py310.py",
                    "start_line": 16,
                    "end_line": 30,
                    "role": "documented yielded-dependency error handling and route branches",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml",
                    "case_ids": [
                        "fastapi.dependencies.tutorial008b.default-parameter-exception-translation"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependencies/tutorial011_py310.py": {
            "rationale": "The pinned example builds a callable query checker used by a route. The selected case observes one default/search request response by body and status; alternative checker configuration and other callable behavior are not claimed.",
            "supporting_sources": [
                {
                    "path": "docs_src/dependencies/tutorial011_py310.py",
                    "start_line": 6,
                    "end_line": 21,
                    "role": "documented callable query checker and dependent route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml",
                    "case_ids": ["fastapi.dependencies.tutorial-review.search-default"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/dependency_testing/tutorial001_py310.py": {
            "rationale": "The pinned example overrides an async dependency used by item and user routes. The selected independent case observes response body and status for the override workload; it does not claim execution of the source TestClient assertions or Python object identity.",
            "supporting_sources": [
                {
                    "path": "docs_src/dependency_testing/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 55,
                    "role": "documented async dependency, override, and affected routes",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/atlas-testing-websocket-dependency-overrides.yaml",
                    "case_ids": ["fastapi.atlas-testing-dependency.overrides"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
        },
        "docs_src/extra_data_types/tutorial001_an_py310.py": {
            "rationale": "The pinned example declares extra data types in request parameters and projects them into the API schema. The cited case observes the route and OpenAPI surface; runtime parsing of all UUID/date/time values and the derived time calculation are not separately established by this schema-focused case.",
            "supporting_sources": [
                {
                    "path": "docs_src/extra_data_types/tutorial001_an_py310.py",
                    "start_line": 10,
                    "end_line": 28,
                    "role": "documented extra-type route parameters and schema-relevant declarations",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
                    "case_ids": ["fastapi.docs.documentation-wave.openapi-schema.extra-data-types"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/frontend/tutorial002_py310.py": {
            "rationale": "The pinned example configures a directory-backed frontend with index fallback. The selected case samples the HTTP fallback response headers, status, and body; browser execution, client-side navigation, and route transitions are not covered.",
            "supporting_sources": [
                {
                    "path": "docs_src/frontend/tutorial002_py310.py",
                    "start_line": 1,
                    "end_line": 5,
                    "role": "documented static frontend mount and index fallback configuration",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-types-frontend.yaml",
                    "case_ids": ["fastapi.docs.reference-wave.frontend.html-client-route-fallback"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/generate_clients/tutorial002_py310.py": {
            "rationale": "The pinned example exposes tagged API routes and an OpenAPI document for client generation. The independent workflow observes tagged route responses and OpenAPI only; generated client source, compilation, and client runtime behavior are not exercised.",
            "supporting_sources": [
                {
                    "path": "docs_src/generate_clients/tutorial002_py310.py",
                    "start_line": 7,
                    "end_line": 36,
                    "role": "documented tagged routes and generated-client API schema",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/generate-clients-tutorial002-upstream.yaml",
                    "case_ids": [
                        "fastapi.test.test-tutorial-test-generate-clients-test-tutorial002.tagged-client-requests-and-openapi"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/metadata/tutorial001_1_py310.py": {
            "rationale": "The pinned example adds license metadata to the FastAPI application. The selected case observes the OpenAPI response status and document projection; other metadata fields, endpoint behavior, and downstream license consumers are outside this mapping.",
            "supporting_sources": [
                {
                    "path": "docs_src/metadata/tutorial001_1_py310.py",
                    "start_line": 18,
                    "end_line": 38,
                    "role": "documented application metadata including its license field",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/metadata-tutorial001-1-upstream.yaml",
                    "case_ids": [
                        "fastapi.test.test-tutorial-test-metadata-test-tutorial001-1.test-openapi-schema"
                    ],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/metadata/tutorial004_py310.py": {
            "rationale": "The pinned example associates tags and external documentation with operations. The selected case observes the OpenAPI response status and document projection for tags; external documentation navigation and downstream consumers are not covered.",
            "supporting_sources": [
                {
                    "path": "docs_src/metadata/tutorial004_py310.py",
                    "start_line": 3,
                    "end_line": 28,
                    "role": "documented tags, externalDocs metadata, and tagged routes",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/metadata-tutorial004-upstream.yaml",
                    "case_ids": [
                        "fastapi.test.test-tutorial-test-metadata-test-tutorial004.test-openapi-schema"
                    ],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/path_operation_advanced_configuration/tutorial004_py310.py": {
            "rationale": "The pinned example declares operation summary and description metadata on a POST route. The selected workflow observes its request response and OpenAPI path/document projection; other path-operation options are not implied.",
            "supporting_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial004_py310.py",
                    "start_line": 7,
                    "end_line": 28,
                    "role": "documented POST route summary, description, and request behavior",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial004-upstream.yaml",
                    "case_ids": ["fastapi.path-operation-advanced-configurations.tutorial004"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/path_operation_advanced_configuration/tutorial007_py310.py": {
            "rationale": "The pinned example parses a YAML request body and declares the request schema. The independent cases observe the route body/status and selected OpenAPI path/document projections, including malformed and invalid inputs; other response/error detail semantics are not claimed.",
            "supporting_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
                    "start_line": 13,
                    "end_line": 32,
                    "role": "documented YAML body parameter, parsing, and route declaration",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial007-upstream.yaml",
                    "case_ids": ["fastapi.path-operation-advanced-configurations.tutorial007"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_openapi_schema.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-openapi-schema"
                    ],
                    "observation_selectors": [
                        "docs.response.status",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_post.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-post"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_post_broken_yaml.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-post-broken-yaml"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_post_invalid.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-post-invalid"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
            ],
        },
        "docs_src/path_params/tutorial005_py310.py": {
            "rationale": "The pinned example declares an enum path parameter. The two cited cases observe one valid member route response and the invalid-enum response by body and status; other valid members and the OpenAPI enum schema are not mapped here.",
            "supporting_sources": [
                {
                    "path": "docs_src/path_params/tutorial005_py310.py",
                    "start_line": 6,
                    "end_line": 23,
                    "role": "documented enum path parameter, selected route, and response",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_get_enums_alexnet.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-get-enums-alexnet"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_get_enums_invalid.yaml",
                    "case_ids": [
                        "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-get-enums-invalid"
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
            ],
        },
        "docs_src/request_form_models/tutorial001_py310.py": {
            "rationale": "The pinned example accepts a Pydantic model through form fields. The selected case observes the valid request/response and OpenAPI route surface; it does not cover every invalid form/model branch or all field coercions.",
            "supporting_sources": [
                {
                    "path": "docs_src/request_form_models/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 14,
                    "role": "documented Pydantic model and form-model route declaration",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                    "case_ids": [
                        "fastapi.docs.request-schema.tutorial-request-form-models.form-model"
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                    ],
                }
            ],
        },
        "docs_src/schema_extra_example/tutorial003_an_py310.py": {
            "rationale": "The pinned example declares a list of request-body examples in OpenAPI. The selected case observes the OpenAPI response status and document only; it does not submit those example bodies for runtime validation.",
            "supporting_sources": [
                {
                    "path": "docs_src/schema_extra_example/tutorial003_an_py310.py",
                    "start_line": 16,
                    "end_line": 34,
                    "role": "documented list of request-body examples",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml",
                    "case_ids": ["fastapi.schema-extra-example.body-examples-list"],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/schema_extra_example/tutorial004_py310.py": {
            "rationale": "The pinned example declares multiple request-body examples. The selected case observes the OpenAPI response status and document only; it does not execute the example payloads as valid or invalid requests.",
            "supporting_sources": [
                {
                    "path": "docs_src/schema_extra_example/tutorial004_py310.py",
                    "start_line": 14,
                    "end_line": 38,
                    "role": "documented multiple request-body examples",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml",
                    "case_ids": ["fastapi.schema-extra-example.body-examples-several"],
                    "observation_selectors": ["docs.response.status", "openapi.document"],
                }
            ],
        },
        "docs_src/security/tutorial001_an_py310.py": {
            "rationale": "The pinned example defines a bearer token dependency and a current-user route. The selected case observes current-user response fields, status, headers, and the OpenAPI security projection; the source token-issuing `/token` response is not exercised.",
            "supporting_sources": [
                {
                    "path": "docs_src/security/tutorial001_an_py310.py",
                    "start_line": 8,
                    "end_line": 13,
                    "role": "documented OAuth2 bearer dependency and current-user route setup",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                    "case_ids": [
                        "fastapi.docs.documentation-wave.dependencies-security.current-user"
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                        "openapi.security",
                    ],
                }
            ],
        },
        "docs_src/separate_openapi_schemas/tutorial001_py310.py": {
            "rationale": "The pinned example uses separate input and output models for a route. The selected case observes the route response and OpenAPI schema/path projection; other validation branches are not covered.",
            "supporting_sources": [
                {
                    "path": "docs_src/separate_openapi_schemas/tutorial001_py310.py",
                    "start_line": 5,
                    "end_line": 20,
                    "role": "documented distinct input/output models and route",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                    "case_ids": [
                        "fastapi.docs.openapi-interface.how-to-separate-openapi-schemas.input-output-models"
                    ],
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
        "docs_src/server_sent_events/tutorial002_py310.py": {
            "rationale": "The pinned example emits server-sent events with structured fields. The selected case observes streamed body bytes, response headers, and status; reconnection/retry policy and long-lived client lifecycle are not covered. The adjacent OpenAPI-only case has no selector intersection for this source row and is intentionally omitted.",
            "supporting_sources": [
                {
                    "path": "docs_src/server_sent_events/tutorial002_py310.py",
                    "start_line": 10,
                    "end_line": 26,
                    "role": "documented event source and event-field response construction",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/server-sent-events-tutorial002-upstream.yaml",
                    "case_ids": ["fastapi.tutorial.server-sent-events.tutorial002.event-fields"],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/static_files/tutorial001_py310.py": {
            "rationale": "The pinned example mounts StaticFiles at a path. The independent case observes the fixture asset/missing-file HTTP responses and OpenAPI mount boundary; arbitrary filesystem contents and filesystem error behavior are outside this recipe.",
            "supporting_sources": [
                {
                    "path": "docs_src/static_files/tutorial001_py310.py",
                    "start_line": 6,
                    "end_line": 6,
                    "role": "documented StaticFiles mount",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml",
                    "case_ids": ["fastapi.middleware-proxy.static-files"],
                    "observation_selectors": ["http.body.bytes", "http.status", "openapi.document"],
                }
            ],
        },
        "docs_src/stream_json_lines/tutorial001_py310.py": {
            "rationale": "The pinned example defines annotated and unannotated sync/async JSON-lines generators. The selected case covers one async typed stream response by body, headers, and status; the other three variants, chunk timing, cancellation, and generator failure are not covered.",
            "supporting_sources": [
                {
                    "path": "docs_src/stream_json_lines/tutorial001_py310.py",
                    "start_line": 9,
                    "end_line": 42,
                    "role": "documented JSON-lines generator variants and route declarations",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml",
                    "case_ids": [
                        "fastapi.docs.documentation-wave.http-behaviors.stream-json-lines"
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "http.headers.ordered",
                        "http.status",
                    ],
                }
            ],
        },
        "docs_src/websockets_/tutorial003_py310.py": {
            "rationale": "The pinned example serves a home page and uses a connection manager for client IDs, personal messages, broadcast, and disconnect cleanup. The selected cases observe the home response and one-client message/order behavior only; multi-client broadcast fan-out and disconnect membership changes remain untested.",
            "supporting_sources": [
                {
                    "path": "docs_src/websockets_/tutorial003_py310.py",
                    "start_line": 44,
                    "end_line": 81,
                    "role": "documented connection manager, personal/broadcast messages, and disconnect cleanup",
                }
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/websockets-tutorial003-upstream-subset.yaml",
                    "case_ids": [
                        "fastapi.websockets.tutorial003.home",
                        "fastapi.websockets.tutorial003.single-client-session",
                    ],
                    "observation_selectors": [
                        "http.body.bytes",
                        "websocket.event_order",
                        "websocket.messages",
                    ],
                }
            ],
        },
    }
)
