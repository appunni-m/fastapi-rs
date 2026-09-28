"""Source-reviewed mappings for remaining FastAPI documentation pages.

FastAPI 0.141.1 is the source authority. Starlette 1.6.0 is the sole generic
framework authority; Starlette-owned behavior remains assigned to Starlette-RS.
Linked recipes contain stimuli, not parity results.
"""

DOC_PAGE_REVIEW_MAPPINGS = {
    "advanced/json-base64-bytes.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "rationale": "FastAPI integrates Pydantic bytes models with "
        "request fields, response fields, and generated "
        "schemas; Pydantic owns the base64 codecs and "
        "Starlette 1.6.0 owns HTTP transport.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed per "
        "recipe; these are stimuli, not parity "
        "results.",
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
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.document.",
            }
        ],
        "contract_gate": "One linked input observes a base64 model "
        "request/response and schema. Missing: "
        "alternate byte encodings, malformed input "
        "paths, all model placements, signatures and "
        "alias identity. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/json-base64-bytes.md",
                "start_line": 1,
                "end_line": 63,
                "role": "Page-level source evidence for "
                "the documented JSON with Bytes "
                "as Base64 behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas "
                "and merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies "
                "and binds path, query, header, "
                "cookie, body, and connection "
                "inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI validates and "
                "serializes response-model "
                "content and applies filters.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and JSON "
                "behavior; generic "
                "request contract "
                "belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "advanced/middleware.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "middleware-integrations"],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "rationale": "FastAPI provides its HTTP middleware decorator and "
        "inherits middleware registration; generic middleware "
        "stack and built-in middleware dispatch are Starlette "
        "1.6.0 behavior, while third-party middleware belongs to "
        "its package.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case IDs "
        "and selector unions are listed per recipe; these "
        "are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/custom-middleware-upload-limit.yaml",
                "case_ids": [
                    "fastapi.middleware.custom-upload-budget-accepted",
                    "fastapi.middleware.custom-upload-budget-exceeded",
                ],
                "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/middleware.yaml",
                "case_ids": [
                    "fastapi.middleware.https-redirect-http",
                    "fastapi.middleware.trusted-host-wildcard-allowed",
                    "fastapi.middleware.trusted-host-rejected",
                    "fastapi.middleware.custom-asgi-body-accepted",
                    "fastapi.middleware.custom-asgi-body-exceeded",
                ],
                "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status.",
            },
        ],
        "contract_gate": "Linked cases cover selected middleware and redirect "
        "outcomes. Missing: arbitrary middleware "
        "ordering/errors, all middleware classes, third-party "
        "package contracts and Python decorator signature. "
        "The mapping remains partial pending the full FastAPI "
        "manifest and identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and the "
        "separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/middleware.md",
                "start_line": 1,
                "end_line": 97,
                "role": "Page-level source evidence for the "
                "documented Advanced Middleware "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 4683,
                "end_line": 4735,
                "role": "FastAPI middleware decorator registers an HTTP dispatch callable.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body "
                "and JSON behavior; generic "
                "request contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
            {
                "path": "starlette/applications.py",
                "start_line": 63,
                "end_line": 108,
                "role": "Starlette 1.6.0 "
                "middleware-stack construction "
                "and app dispatch; tracked by "
                "Starlette-RS.",
            },
        ],
    },
    "advanced/security/oauth2-scopes.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
        "rationale": "FastAPI builds security dependency graphs, "
        "propagates OAuth2 scopes and projects "
        "requirements into OpenAPI; credential policy "
        "and token creation are application-owned.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. "
        "The case IDs and selector unions are "
        "listed per recipe; these are stimuli, "
        "not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/security-dependencies.yaml",
                "case_ids": [
                    "fastapi.docs.security.bearer-required-valid",
                    "fastapi.docs.security.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                    "openapi.security",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.document, "
                "openapi.paths, "
                "openapi.security.",
            }
        ],
        "contract_gate": "Linked cases cover selected bearer "
        "handling and OpenAPI pointers. Missing: "
        "every nested scope combination, "
        "application password/JWT policy, all "
        "failures and full signature/identity "
        "checks. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 "
        "and the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/security/oauth2-scopes.md",
                "start_line": 1,
                "end_line": 274,
                "role": "Page-level source "
                "evidence for the "
                "documented OAuth2 scopes "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and "
                "Security declarations "
                "expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request "
                "bodies, callbacks, and "
                "security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies "
                "and prepares endpoint "
                "dispatch.",
            },
            {
                "path": "fastapi/security/oauth2.py",
                "start_line": 653,
                "end_line": 693,
                "role": "FastAPI SecurityScopes and OAuth2 scope interface.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs "
                "to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "advanced/testing-dependencies.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "rationale": "FastAPI applies dependency_overrides during "
        "graph resolution and rebuilds the replacement "
        "dependency node; TestClient and test runner "
        "behavior belong to Starlette 1.6.0.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. "
        "The case IDs and selector unions are "
        "listed per recipe; these are stimuli, not "
        "parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                "case_ids": ["fastapi.dependencies.override-resolution"],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            }
        ],
        "contract_gate": "One override case is linked. Missing: "
        "nested overrides, restoration fixtures, "
        "cache/scope combinations, test-client "
        "behavior and callable identity. The "
        "mapping remains partial pending the full "
        "FastAPI manifest and identity/signature "
        "checks. Generic HTTP behavior is assigned "
        "to Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/testing-dependencies.md",
                "start_line": 1,
                "end_line": 53,
                "role": "Page-level source evidence "
                "for the documented Testing "
                "Dependencies with Overrides "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and "
                "Security declarations "
                "expose dependency and scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "async.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "rationale": "FastAPI awaits coroutine endpoints and runs synchronous endpoints "
        "through its endpoint runner; event-loop scheduling and third-party "
        "async behavior are outside FastAPI.",
        "stimulus_notes": "Reuses input-only recipe cases whose source_evidence cites this "
        "exact page. The case IDs and selector unions are listed per "
        "recipe; these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-async-handlers.yaml",
                "case_ids": ["fastapi.docs.async-handlers.mixed-callables"],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            }
        ],
        "contract_gate": "One mixed-callable case is linked. Missing: cancellation, "
        "thread-pool limits, streaming, background work and all endpoint "
        "signature forms. The mapping remains partial pending the full "
        "FastAPI manifest and identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/async.md",
                "start_line": 1,
                "end_line": 444,
                "role": "Page-level source evidence for the documented "
                "Concurrency and async / await behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, response, and "
                "OpenAPI route configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security declarations expose "
                "dependency and scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body and JSON "
                "behavior; generic request contract belongs "
                "to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "python-types.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI interprets endpoint annotations for request fields, "
        "dependencies and OpenAPI; Python typing semantics and Pydantic "
        "validation/schema primitives are separate pinned contracts.",
        "stimulus_notes": "Reuses input-only recipe cases whose source_evidence cites "
        "this exact page. The case IDs and selector unions are "
        "listed per recipe; these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-types-frontend.yaml",
                "case_ids": ["fastapi.docs.reference-wave.types.typed-path-and-query-inputs"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One typed path/query input and selected schema pointers are "
        "linked. Missing: the page's full typing matrix, nested "
        "types, coercion edges and every annotation position. The "
        "mapping remains partial pending the full FastAPI manifest "
        "and identity/signature checks. Generic HTTP behavior is "
        "assigned to Starlette 1.6.0 and the separate Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/python-types.md",
                "start_line": 1,
                "end_line": 348,
                "role": "Page-level source evidence for the "
                "documented Python Types Intro behavior and "
                "examples.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security declarations "
                "expose dependency and scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation parameters, "
                "request bodies, callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and merges "
                "additional response declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses declared "
                "bodies and prepares endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body and "
                "JSON behavior; generic request "
                "contract belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "reference/dependencies.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
        "rationale": "Depends and Security declarations construct FastAPI "
        "dependency nodes and security metadata; callable "
        "signatures and public object identity remain manifest "
        "obligations.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
                "case_ids": ["fastapi.docs.reference-wave.http.security-dependency"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                    "openapi.security",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.document, openapi.paths, "
                "openapi.security.",
            }
        ],
        "contract_gate": "One security dependency case and selected OpenAPI "
        "pointers are linked. Missing: Depends/Security "
        "signature and identity probes, all "
        "graph/cache/scope options and error branches. The "
        "mapping remains partial pending the full FastAPI "
        "manifest and identity/signature checks. Generic "
        "HTTP behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/dependencies.md",
                "start_line": 1,
                "end_line": 29,
                "role": "Page-level source evidence for the "
                "documented Dependencies - "
                "`Depends()` and `Security()` "
                "behavior and examples.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and "
                "merges additional response "
                "declarations.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request contract "
                "belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "reference/encoders.md": {
        "replace_features": True,
        "feature_ids": ["python-data-encoding"],
        "observation_selectors": ["python.attribute_value", "python.signature"],
        "rationale": "jsonable_encoder is a FastAPI public callable that "
        "converts supported values and exposes filtering options; "
        "Pydantic conversion primitives remain separate.",
        "stimulus_notes": "Reuses input-only recipe cases whose source_evidence "
        "cites this exact page. The case IDs and selector "
        "unions are listed per recipe; these are stimuli, not "
        "parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml",
                "case_ids": ["fastapi.direct-api-reference-wave.encoder-reference-dataclass"],
                "observation_selectors": ["python.attribute_value", "python.signature"],
                "coverage": "Selected cases observe python.attribute_value, python.signature.",
            }
        ],
        "contract_gate": "One direct API case checks a dataclass result and "
        "signature. Missing: type matrix, custom encoders, "
        "recursive edge cases, filter combinations and "
        "exception identity. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. This direct callable "
        "case does not cross the HTTP/Starlette boundary.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/encoders.md",
                "start_line": 1,
                "end_line": 3,
                "role": "Page-level source evidence for the "
                "documented Encoders - "
                "`jsonable_encoder` behavior and "
                "examples.",
            },
            {
                "path": "fastapi/encoders.py",
                "start_line": 129,
                "end_line": 190,
                "role": "FastAPI jsonable_encoder public "
                "signature and filtering/conversion "
                "implementation.",
            },
        ],
        "starlette_contract_sources": [],
    },
    "reference/parameters.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI parameter declaration classes describe "
        "endpoint/dependency fields, Pydantic-backed validation "
        "and OpenAPI; generic header/query/cookie extraction "
        "belongs to Starlette 1.6.0.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-http.yaml",
                "case_ids": ["fastapi.docs.reference-wave.http.parameter-source-matrix"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One source matrix and selected OpenAPI pointers are "
        "linked. Missing: all constructor "
        "signatures/defaults/aliases, repeated values, full "
        "validation edges, multipart guards and import "
        "identity. The mapping remains partial pending the "
        "full FastAPI manifest and identity/signature "
        "checks. Generic HTTP behavior is assigned to "
        "Starlette 1.6.0 and the separate Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/parameters.md",
                "start_line": 1,
                "end_line": 35,
                "role": "Page-level source evidence for the "
                "documented Request Parameters "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and "
                "merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 137,
                "end_line": 220,
                "role": "FastAPI Path declaration metadata.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 221,
                "end_line": 302,
                "role": "FastAPI Query declaration metadata.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 303,
                "end_line": 468,
                "role": "FastAPI Header and Cookie declaration metadata.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 469,
                "end_line": 745,
                "role": "FastAPI Body, Form, and File declarations.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body "
                "and JSON behavior; generic "
                "request contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "reference/uploadfile.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI UploadFile adds FastAPI field validation around "
        "the Starlette UploadFile class; Starlette 1.6.0 owns "
        "multipart parsing, file storage and generic file "
        "methods.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml",
                "case_ids": ["fastapi.docs.reference-wave.asgi.uploadfile-multipart"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.paths, "
                "openapi.request_schema.",
            }
        ],
        "contract_gate": "One multipart route and selected OpenAPI paths are "
        "linked. Missing: rollover, async file methods, "
        "parser limits, all form/file shapes, identity and "
        "signatures. The mapping remains partial pending the "
        "full FastAPI manifest and identity/signature "
        "checks. Generic HTTP behavior is assigned to "
        "Starlette 1.6.0 and the separate Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/uploadfile.md",
                "start_line": 1,
                "end_line": 22,
                "role": "Page-level source evidence for the "
                "documented `UploadFile` class "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and "
                "merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint signatures "
                "and builds dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies and "
                "binds path, query, header, cookie, "
                "body, and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/datastructures.py",
                "start_line": 18,
                "end_line": 137,
                "role": "FastAPI UploadFile subclass and "
                "validation against Starlette "
                "UploadFile values.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body "
                "and JSON behavior; generic "
                "request contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 268,
                "end_line": 322,
                "role": "Starlette 1.6.0 form/multipart parsing entry point.",
            },
            {
                "path": "starlette/datastructures.py",
                "start_line": 410,
                "end_line": 490,
                "role": "Starlette 1.6.0 generic UploadFile storage and file operations.",
            },
        ],
    },
    "tutorial/bigger-applications.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI APIRouter and include_router merge "
        "route prefixes, metadata and dependencies; "
        "generic matching/dispatch is Starlette 1.6.0 "
        "behavior.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed "
        "per recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/routing-surface.yaml",
                "case_ids": [
                    "fastapi.routing.include-router-prefix",
                    "fastapi.routing.openapi-paths",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "Linked cases cover one included prefix and "
        "selected OpenAPI paths. Missing: all merge "
        "precedence, nested/repeated inclusion, "
        "warning behavior and complete metadata "
        "combinations. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/bigger-applications.md",
                "start_line": 1,
                "end_line": 547,
                "role": "Page-level source evidence "
                "for the documented Bigger "
                "Applications - Multiple "
                "Files behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose "
                "dependency and scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 2255,
                "end_line": 2318,
                "role": "FastAPI APIRouter initialization and configuration.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 3133,
                "end_line": 3215,
                "role": "FastAPI APIRouter.include_router merges route/router metadata.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/body-multiple-params.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI classifies multiple body fields, "
        "assembles embedded request bodies, validates "
        "them and generates OpenAPI; Pydantic owns "
        "model primitives.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. "
        "The case IDs and selector unions are "
        "listed per recipe; these are stimuli, not "
        "parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-surface.yaml",
                "case_ids": [
                    "fastapi.body.multiple-values-valid",
                    "fastapi.body.multiple-values-invalid",
                    "fastapi.body.optional-model-absent",
                    "fastapi.body.optional-model-present",
                    "fastapi.body.openapi-schemas",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, openapi.paths, "
                "openapi.request_schema.",
            }
        ],
        "contract_gate": "Linked cases sample combined and optional "
        "bodies plus schema pointers. Missing: all "
        "aliases/media types/unions, duplicate "
        "names, malformed bodies and full error "
        "detail. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 "
        "and the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/body-multiple-params.md",
                "start_line": 1,
                "end_line": 169,
                "role": "Page-level source evidence "
                "for the documented Body - "
                "Multiple Parameters "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves "
                "dependencies and binds "
                "path, query, header, "
                "cookie, body, and "
                "connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint "
                "dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/body-nested-models.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI feeds nested body fields into Pydantic "
        "validation and generated request schemas; nested "
        "model semantics are Pydantic behavior.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed per "
        "recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                "case_ids": ["fastapi.docs.request-schema.tutorial-body-nested-models.nested-body"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.document, "
                "openapi.paths, "
                "openapi.request_schema.",
            }
        ],
        "contract_gate": "One nested model case and schema pointer are "
        "linked. Missing: deep/union/list variants, "
        "nested invalid paths and all examples. The "
        "mapping remains partial pending the full "
        "FastAPI manifest and identity/signature "
        "checks. Generic HTTP behavior is assigned to "
        "Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/body-nested-models.md",
                "start_line": 1,
                "end_line": 221,
                "role": "Page-level source evidence "
                "for the documented Body - "
                "Nested Models behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges additional "
                "response declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies "
                "and binds path, query, "
                "header, cookie, body, and "
                "connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and JSON "
                "behavior; generic "
                "request contract "
                "belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/body-updates.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "python-data-encoding",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "rationale": "FastAPI validates update models and serializes "
        "response models; jsonable_encoder supports "
        "application-side JSON conversion, while "
        "persistence/update policy is application code.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/nested-body-corner-wave.yaml",
                "case_ids": [
                    "fastapi.nested-body-corner-wave.patch-model.test-get",
                    "fastapi.nested-body-corner-wave.patch-model.test-patch-all",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                "case_ids": ["fastapi.docs.request-schema.tutorial-body-updates.partial-update"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.document, openapi.paths.",
            },
        ],
        "contract_gate": "Linked cases sample a partial update and selected "
        "model branches. Missing: storage behavior, all "
        "unset/default/null combinations, every update "
        "method and full snapshots. The mapping remains "
        "partial pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP behavior "
        "is assigned to Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/body-updates.md",
                "start_line": 1,
                "end_line": 100,
                "role": "Page-level source evidence for the "
                "documented Body - Updates behavior "
                "and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and "
                "merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/encoders.py",
                "start_line": 129,
                "end_line": 190,
                "role": "FastAPI jsonable_encoder public "
                "signature and filtering/conversion "
                "implementation.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies and "
                "binds path, query, header, cookie, "
                "body, and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI validates and serializes "
                "response-model content and applies "
                "filters.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request contract "
                "belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/body.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI infers body fields, parses declared content, validates "
        "through Pydantic and generates request-body OpenAPI metadata.",
        "stimulus_notes": "Reuses input-only recipe cases whose source_evidence "
        "cites this exact page. The case IDs and selector unions "
        "are listed per recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-surface.yaml",
                "case_ids": [
                    "fastapi.body.embedded-scalar-valid",
                    "fastapi.body.embedded-scalar-missing",
                    "fastapi.body.embedded-list-valid",
                    "fastapi.body.openapi-schemas",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.paths, openapi.request_schema.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
                "case_ids": [
                    "fastapi.first-slice.create-item-invalid",
                    "fastapi.first-slice.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.paths, openapi.request_schema.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-tutorial004-model-upstream.yaml",
                "case_ids": [
                    "fastapi.body.tutorial004.complete-model",
                    "fastapi.body.tutorial004.optional-model-fields-absent",
                    "fastapi.body.tutorial004.required-model-fields-missing",
                    "fastapi.body.tutorial004.openapi-operation-and-model",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.document, openapi.paths.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/body-tutorial003-model-upstream.yaml",
                "case_ids": [
                    "fastapi.body.tutorial003.complete-model",
                    "fastapi.body.tutorial003.optional-model-fields-absent",
                    "fastapi.body.tutorial003.required-model-fields-missing",
                    "fastapi.body.tutorial003.openapi-operation-and-model",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.document, openapi.paths.",
            },
        ],
        "contract_gate": "Linked cases sample embedded, optional and model-body "
        "branches. Missing: all declarations/media types/aliases, "
        "malformed input and full validation details. The mapping "
        "remains partial pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP behavior is "
        "assigned to Starlette 1.6.0 and the separate Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/body.md",
                "start_line": 1,
                "end_line": 166,
                "role": "Page-level source evidence for the "
                "documented Request Body behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation parameters, "
                "request bodies, callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and merges "
                "additional response declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint signatures and "
                "builds dependency/request-field nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies and binds "
                "path, query, header, cookie, body, and "
                "connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses declared "
                "bodies and prepares endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body and "
                "JSON behavior; generic request "
                "contract belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/cookie-param-models.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI recognizes grouped Pydantic models "
        "declared with Cookie and builds "
        "validation/OpenAPI fields; cookie parsing is "
        "generic Starlette request behavior.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed "
        "per recipe; these are stimuli, not parity "
        "results.",
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
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One grouped cookie model and selected "
        "OpenAPI paths are linked. Missing: aliases, "
        "repeated names, invalid combinations and "
        "constructor identity/signatures. The "
        "mapping remains partial pending the full "
        "FastAPI manifest and identity/signature "
        "checks. Generic HTTP behavior is assigned "
        "to Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/cookie-param-models.md",
                "start_line": 1,
                "end_line": 76,
                "role": "Page-level source evidence "
                "for the documented Cookie "
                "Parameter Models behavior "
                "and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves "
                "dependencies and binds path, "
                "query, header, cookie, body, "
                "and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint "
                "dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/dependencies/classes-as-dependencies.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI inspects callable "
        "instances as dependency "
        "providers, builds their "
        "parameter graph, invokes them "
        "and documents their "
        "parameters.",
        "stimulus_notes": "Reuses input-only recipe "
        "cases whose "
        "source_evidence cites "
        "this exact page. The case "
        "IDs and selector unions "
        "are listed per recipe; "
        "these are stimuli, not "
        "parity results.",
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
                "coverage": "Selected "
                "cases "
                "observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One callable-class "
        "dependency and selected "
        "OpenAPI paths are linked. "
        "Missing: constructor "
        "variants, nesting, cache, "
        "overrides, yield cleanup "
        "and signature matrix. The "
        "mapping remains partial "
        "pending the full FastAPI "
        "manifest and "
        "identity/signature checks. "
        "Generic HTTP behavior is "
        "assigned to Starlette "
        "1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/dependencies/classes-as-dependencies.md",
                "start_line": 1,
                "end_line": 288,
                "role": "Page-level "
                "source "
                "evidence "
                "for the "
                "documented "
                "Classes as "
                "Dependencies "
                "behavior "
                "and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI "
                "APIRoute "
                "stores "
                "dependency, "
                "response, "
                "and OpenAPI "
                "route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI "
                "Depends and "
                "Security "
                "declarations "
                "expose "
                "dependency "
                "and scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI "
                "creates "
                "operation "
                "parameters, "
                "request "
                "bodies, "
                "callbacks, "
                "and "
                "security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI "
                "emits "
                "response "
                "schemas and "
                "merges "
                "additional "
                "response "
                "declarations.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette "
                "1.6.0 "
                "request "
                "body "
                "and "
                "JSON "
                "behavior; "
                "generic "
                "request "
                "contract "
                "belongs "
                "to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/dependencies/dependencies-in-path-operation-decorators.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI "
        "resolves "
        "decorator-level "
        "dependencies "
        "even when "
        "endpoint "
        "code does "
        "not receive "
        "the return "
        "value, and "
        "converts "
        "dependency "
        "errors "
        "through "
        "route "
        "handling.",
        "stimulus_notes": "Reuses "
        "input-only "
        "recipe "
        "cases "
        "whose "
        "source_evidence "
        "cites "
        "this "
        "exact "
        "page. "
        "The "
        "case "
        "IDs and "
        "selector "
        "unions "
        "are "
        "listed "
        "per "
        "recipe; "
        "these "
        "are "
        "stimuli, "
        "not "
        "parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                "case_ids": [
                    "fastapi.docs.documentation-wave.dependencies-security.path-operation-dependencies"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected "
                "cases "
                "observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One "
        "decorator-level "
        "dependency "
        "case is "
        "linked. "
        "Missing: "
        "ordering, "
        "subdependency "
        "failures, "
        "security/error "
        "branches, "
        "cleanup "
        "and "
        "cache "
        "behavior. "
        "The "
        "mapping "
        "remains "
        "partial "
        "pending "
        "the full "
        "FastAPI "
        "manifest "
        "and "
        "identity/signature "
        "checks. "
        "Generic "
        "HTTP "
        "behavior "
        "is "
        "assigned "
        "to "
        "Starlette "
        "1.6.0 "
        "and the "
        "separate "
        "Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/dependencies/dependencies-in-path-operation-decorators.md",
                "start_line": 1,
                "end_line": 69,
                "role": "Page-level "
                "source "
                "evidence "
                "for "
                "the "
                "documented "
                "Dependencies "
                "in "
                "path "
                "operation "
                "decorators "
                "behavior "
                "and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI "
                "APIRoute "
                "stores "
                "dependency, "
                "response, "
                "and "
                "OpenAPI "
                "route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI "
                "Depends "
                "and "
                "Security "
                "declarations "
                "expose "
                "dependency "
                "and "
                "scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI "
                "request "
                "handler "
                "parses "
                "declared "
                "bodies "
                "and "
                "prepares "
                "endpoint "
                "dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette "
                "1.6.0 "
                "request "
                "body "
                "and "
                "JSON "
                "behavior; "
                "generic "
                "request "
                "contract "
                "belongs "
                "to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/dependencies/dependencies-with-yield.md": {
        "replace_features": True,
        "feature_ids": ["dependency-security"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "rationale": "FastAPI enters generator "
        "dependencies during graph "
        "resolution and exits them at "
        "the configured scope; generic "
        "streaming/HTTP transport is "
        "Starlette 1.6.0 behavior.",
        "stimulus_notes": "Reuses input-only recipe "
        "cases whose "
        "source_evidence cites "
        "this exact page. The case "
        "IDs and selector unions "
        "are listed per recipe; "
        "these are stimuli, not "
        "parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
                "case_ids": [
                    "fastapi.dependencies.yield-scope-cleanup",
                    "fastapi.dependencies.yield-cleanup-error",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            }
        ],
        "contract_gate": "Linked cases sample "
        "cleanup and cleanup-error "
        "paths. Missing: all "
        "scopes, nested order, "
        "suppression/re-raise, "
        "streaming/background "
        "ordering and WebSocket "
        "cleanup. The mapping "
        "remains partial pending "
        "the full FastAPI manifest "
        "and identity/signature "
        "checks. Generic HTTP "
        "behavior is assigned to "
        "Starlette 1.6.0 and the "
        "separate Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/dependencies/dependencies-with-yield.md",
                "start_line": 1,
                "end_line": 290,
                "role": "Page-level "
                "source "
                "evidence "
                "for the "
                "documented "
                "Dependencies "
                "with yield "
                "behavior "
                "and "
                "examples.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI "
                "Depends and "
                "Security "
                "declarations "
                "expose "
                "dependency "
                "and scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette "
                "1.6.0 "
                "request "
                "body "
                "and "
                "JSON "
                "behavior; "
                "generic "
                "request "
                "contract "
                "belongs "
                "to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/dependencies/global-dependencies.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI applies app-level "
        "dependencies when constructing "
        "route dependency graphs.",
        "stimulus_notes": "Reuses input-only recipe "
        "cases whose source_evidence "
        "cites this exact page. The "
        "case IDs and selector unions "
        "are listed per recipe; these "
        "are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                "case_ids": [
                    "fastapi.docs.documentation-wave.dependencies-security.global-dependencies"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected cases "
                "observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One global dependency case is "
        "linked. Missing: router "
        "precedence, multiple global "
        "dependencies, overrides, "
        "cache/scope and all errors. "
        "The mapping remains partial "
        "pending the full FastAPI "
        "manifest and "
        "identity/signature checks. "
        "Generic HTTP behavior is "
        "assigned to Starlette 1.6.0 "
        "and the separate Starlette-RS "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/dependencies/global-dependencies.md",
                "start_line": 1,
                "end_line": 16,
                "role": "Page-level "
                "source evidence "
                "for the "
                "documented "
                "Global "
                "Dependencies "
                "behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI "
                "APIRoute stores "
                "dependency, "
                "response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends "
                "and Security "
                "declarations "
                "expose "
                "dependency and "
                "scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette "
                "1.6.0 "
                "request "
                "body "
                "and "
                "JSON "
                "behavior; "
                "generic "
                "request "
                "contract "
                "belongs "
                "to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/dependencies/index.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "This page introduces FastAPI's dependency graph; "
        "the linked first-slice route shows a basic "
        "dependency request and generated path.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed per "
        "recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
                "case_ids": [
                    "fastapi.first-slice.create-item-valid",
                    "fastapi.first-slice.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, openapi.paths, "
                "openapi.request_schema.",
            }
        ],
        "contract_gate": "The linked first-slice input is introductory "
        "only. Missing: graph recursion, cache, "
        "callable instances, overrides, scopes, yield "
        "cleanup and dependency signatures. The "
        "mapping remains partial pending the full "
        "FastAPI manifest and identity/signature "
        "checks. Generic HTTP behavior is assigned to "
        "Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/dependencies/index.md",
                "start_line": 1,
                "end_line": 250,
                "role": "Page-level source evidence "
                "for the documented "
                "Dependencies behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose "
                "dependency and scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges additional "
                "response declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and JSON "
                "behavior; generic "
                "request contract "
                "belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/extra-data-types.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "rationale": "FastAPI passes annotated types into "
        "Pydantic-backed request/response fields and uses "
        "those fields in OpenAPI; type conversion "
        "primitives belong to Pydantic.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed per "
        "recipe; these are stimuli, not parity "
        "results.",
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
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, openapi.document, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One extra-type route and selected schema "
        "pointers are linked. Missing: all "
        "Python/Pydantic types, invalid values, "
        "serialization modes and version-specific "
        "behavior. The mapping remains partial pending "
        "the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/extra-data-types.md",
                "start_line": 1,
                "end_line": 62,
                "role": "Page-level source evidence for "
                "the documented Extra Data Types "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas "
                "and merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies "
                "and binds path, query, header, "
                "cookie, body, and connection "
                "inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI validates and "
                "serializes response-model "
                "content and applies filters.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/extra-models.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "rationale": "FastAPI uses declared models for request validation, "
        "response filtering and OpenAPI; security/storage "
        "choices remain application code.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
                "case_ids": ["fastapi.docs.documentation-wave.openapi-schema.extra-models"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.document, openapi.paths.",
            }
        ],
        "contract_gate": "One extra-model case and selected schema "
        "projections are linked. Missing: all input/output "
        "combinations, sensitive-field policy, invalid "
        "output and nested schemas. The mapping remains "
        "partial pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP behavior "
        "is assigned to Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/extra-models.md",
                "start_line": 1,
                "end_line": 211,
                "role": "Page-level source evidence for the "
                "documented Extra Models behavior "
                "and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and "
                "merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI validates and serializes "
                "response-model content and applies "
                "filters.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request contract "
                "belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/header-param-models.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI flattens a Pydantic model declared with "
        "Header into validated request fields and "
        "OpenAPI; header lookup is Starlette 1.6.0 "
        "behavior.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed "
        "per recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                "case_ids": [
                    "fastapi.docs.request-schema.tutorial-header-param-models.header-model"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths.",
            }
        ],
        "contract_gate": "One header model and selected OpenAPI paths "
        "are linked. Missing: underscore conversion, "
        "aliases, repeated headers, extra-field "
        "policy, invalid combinations and "
        "signatures. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/header-param-models.md",
                "start_line": 1,
                "end_line": 72,
                "role": "Page-level source evidence "
                "for the documented Header "
                "Parameter Models behavior "
                "and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves "
                "dependencies and binds path, "
                "query, header, cookie, body, "
                "and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint "
                "dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/path-params.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
        ],
        "rationale": "FastAPI builds path fields from route templates and "
        "endpoint annotations, validates captured values and "
        "documents them; generic matching/converters belong to "
        "Starlette 1.6.0.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-parameters.yaml",
                "case_ids": [
                    "fastapi.request-parameters.path.valid-integer",
                    "fastapi.request-parameters.path.invalid-integer",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/routing-surface.yaml",
                "case_ids": [
                    "fastapi.routing.include-router-prefix",
                    "fastapi.routing.path-converter",
                    "fastapi.routing.path-parameter-invalid",
                    "fastapi.routing.openapi-paths",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, http.status, "
                "openapi.paths.",
            },
        ],
        "contract_gate": "Linked cases sample integer inputs, a path "
        "converter, router inclusion and selected paths. "
        "Missing: every converter/type/constraint, mounted "
        "routes, full errors and signatures. The mapping "
        "remains partial pending the full FastAPI manifest "
        "and identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and the "
        "separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/path-params.md",
                "start_line": 1,
                "end_line": 251,
                "role": "Page-level source evidence for the "
                "documented Path Parameters behavior "
                "and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas and "
                "merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint signatures "
                "and builds dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies and "
                "binds path, query, header, cookie, "
                "body, and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request body "
                "and JSON behavior; generic "
                "request contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/query-param-models.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": ["http.body.bytes", "http.status", "openapi.paths"],
        "rationale": "FastAPI expands a Pydantic model declared with "
        "Query into validated query fields and OpenAPI "
        "parameters.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed per "
        "recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/query-param-models.yaml",
                "case_ids": [
                    "fastapi.query-param-models.grouped-repeated-list",
                    "fastapi.query-param-models.grouped-defaults",
                    "fastapi.query-param-models.grouped-validation-invalid",
                    "fastapi.query-param-models.openapi-query-parameters",
                ],
                "observation_selectors": ["http.body.bytes", "http.status", "openapi.paths"],
                "coverage": "Selected cases observe http.body.bytes, http.status, openapi.paths.",
            }
        ],
        "contract_gate": "Linked cases sample repeated values, "
        "defaults, invalid input and selected "
        "parameters. Missing: extra policy, aliases, "
        "nested models, coercion edges and "
        "constructor signatures. The mapping remains "
        "partial pending the full FastAPI manifest "
        "and identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/query-param-models.md",
                "start_line": 1,
                "end_line": 68,
                "role": "Page-level source evidence "
                "for the documented Query "
                "Parameter Models behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges additional "
                "response declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies "
                "and binds path, query, "
                "header, cookie, body, and "
                "connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and JSON "
                "behavior; generic "
                "request contract "
                "belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/query-params.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "request-validation"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "rationale": "FastAPI infers non-path endpoint values as query "
        "fields, validates them and produces request-validation "
        "responses for invalid/missing inputs.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-parameters.yaml",
                "case_ids": [
                    "fastapi.request-parameters.query.required-missing",
                    "fastapi.request-parameters.query.invalid-integer",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            }
        ],
        "contract_gate": "Linked cases sample missing and invalid required "
        "values only. Missing: defaults, aliases, repeated "
        "values, enums, constraints and OpenAPI. The "
        "mapping remains partial pending the full FastAPI "
        "manifest and identity/signature checks. Generic "
        "HTTP behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/query-params.md",
                "start_line": 1,
                "end_line": 188,
                "role": "Page-level source evidence for the "
                "documented Query Parameters "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores dependency, "
                "response, and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependencies and "
                "binds path, query, header, cookie, "
                "body, and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request contract "
                "belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/request-form-models.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI binds Form-declared fields to a "
        "Pydantic model and documents them; Starlette "
        "1.6.0 performs generic form parsing.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The "
        "case IDs and selector unions are listed "
        "per recipe; these are stimuli, not parity "
        "results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-request-schema.yaml",
                "case_ids": ["fastapi.docs.request-schema.tutorial-request-form-models.form-model"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.document, "
                "openapi.paths, "
                "openapi.request_schema.",
            }
        ],
        "contract_gate": "One form model and selected OpenAPI "
        "pointers are linked. Missing: all "
        "aliases/defaults/errors, repeated values, "
        "multipart/file combinations and parser "
        "limits. The mapping remains partial pending "
        "the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/request-form-models.md",
                "start_line": 1,
                "end_line": 78,
                "role": "Page-level source evidence "
                "for the documented Form "
                "Models behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects endpoint "
                "signatures and builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves "
                "dependencies and binds path, "
                "query, header, cookie, body, "
                "and connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint "
                "dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 268,
                "end_line": 322,
                "role": "Starlette 1.6.0 form/multipart parsing entry point.",
            },
            {
                "path": "starlette/datastructures.py",
                "start_line": 410,
                "end_line": 490,
                "role": "Starlette 1.6.0 generic UploadFile storage and file operations.",
            },
        ],
    },
    "tutorial/request-forms-and-files.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "request-validation"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "rationale": "FastAPI classifies mixed Form/File fields "
        "and validates them; Starlette 1.6.0 owns "
        "multipart parsing and UploadFile resource "
        "operations.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. "
        "The case IDs and selector unions are "
        "listed per recipe; these are stimuli, "
        "not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-multipart.yaml",
                "case_ids": ["fastapi.request-multipart.mixed.form-and-file"],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            }
        ],
        "contract_gate": "One mixed form/file case is linked. "
        "Missing: file sizes, parser limits, "
        "repeated fields, all UploadFile "
        "methods, optionality and errors. The "
        "mapping remains partial pending the "
        "full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 "
        "and the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/request-forms-and-files.md",
                "start_line": 1,
                "end_line": 41,
                "role": "Page-level source "
                "evidence for the "
                "documented Request Forms "
                "and Files behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, "
                "and OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI inspects "
                "endpoint signatures and "
                "builds "
                "dependency/request-field "
                "nodes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves "
                "dependencies and binds "
                "path, query, header, "
                "cookie, body, and "
                "connection inputs.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies "
                "and prepares endpoint "
                "dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs "
                "to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 268,
                "end_line": 322,
                "role": "Starlette 1.6.0 form/multipart parsing entry point.",
            },
            {
                "path": "starlette/datastructures.py",
                "start_line": 410,
                "end_line": 490,
                "role": "Starlette 1.6.0 generic UploadFile storage and file operations.",
            },
        ],
    },
    "tutorial/request-forms.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "request-validation"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "rationale": "FastAPI distinguishes Form fields from JSON body "
        "fields and validates declared values; Starlette 1.6.0 "
        "owns URL-encoded/multipart parsing.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/request-multipart.yaml",
                "case_ids": [
                    "fastapi.request-multipart.form.required-present",
                    "fastapi.request-multipart.form.required-missing",
                    "fastapi.request-multipart.form.optional-missing",
                    "fastapi.request-multipart.form.optional-present",
                    "fastapi.request-multipart.form.list-repeated",
                    "fastapi.request-multipart.form.optional-list-missing",
                    "fastapi.request-multipart.form.optional-list-repeated",
                ],
                "observation_selectors": ["http.body.bytes", "http.status"],
                "coverage": "Selected cases observe http.body.bytes, http.status.",
            }
        ],
        "contract_gate": "Linked cases sample required, optional and "
        "repeated fields. Missing: all constraints, parser "
        "boundaries, model binding, files, content-type "
        "errors and signatures. The mapping remains "
        "partial pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP behavior "
        "is assigned to Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/request-forms.md",
                "start_line": 1,
                "end_line": 73,
                "role": "Page-level source evidence for the "
                "documented Form Data behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and OpenAPI "
                "route configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request contract "
                "belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 268,
                "end_line": 322,
                "role": "Starlette 1.6.0 form/multipart parsing entry point.",
            },
            {
                "path": "starlette/datastructures.py",
                "start_line": 410,
                "end_line": 490,
                "role": "Starlette 1.6.0 generic UploadFile storage and file operations.",
            },
        ],
    },
    "tutorial/response-model.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI validates returned values, applies "
        "response-model filters and generates response "
        "schemas; direct Response rendering is Starlette "
        "1.6.0 behavior.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. The case "
        "IDs and selector unions are listed per recipe; "
        "these are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/first-asgi-request.yaml",
                "case_ids": [
                    "fastapi.first-slice.create-item-valid",
                    "fastapi.first-slice.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, openapi.paths, "
                "openapi.request_schema.",
            },
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/response-model-serialization.yaml",
                "case_ids": [
                    "fastapi.response-model.include.nested",
                    "fastapi.response-model.exclude.nested",
                    "fastapi.response-model.exclude-unset.explicit-null",
                    "fastapi.response-model.exclude-defaults.explicit-defaults",
                    "fastapi.response-model.alias.default-by-alias",
                    "fastapi.response-model.alias.field-name-output",
                    "fastapi.response-model.validation.missing-output-field",
                ],
                "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status.",
            },
        ],
        "contract_gate": "Linked cases sample basic output plus selected "
        "filters, aliases and invalid output. Missing: "
        "all response types/filter combinations, custom "
        "classes and full OpenAPI snapshots. The mapping "
        "remains partial pending the full FastAPI "
        "manifest and identity/signature checks. Generic "
        "HTTP behavior is assigned to Starlette 1.6.0 and "
        "the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/response-model.md",
                "start_line": 1,
                "end_line": 344,
                "role": "Page-level source evidence for "
                "the documented Response Model - "
                "Return Type behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and OpenAPI "
                "route configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and Security "
                "declarations expose dependency "
                "and scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response schemas "
                "and merges additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler parses "
                "declared bodies and prepares "
                "endpoint dispatch.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI validates and serializes "
                "response-model content and "
                "applies filters.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 request "
                "body and JSON behavior; "
                "generic request contract "
                "belongs to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/security/first-steps.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
        "rationale": "FastAPI exposes OAuth2 bearer dependencies, "
        "resolves security inputs and generates OpenAPI "
        "schemes/requirements; token policy is "
        "application-owned.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. "
        "The case IDs and selector unions are "
        "listed per recipe; these are stimuli, not "
        "parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/security-dependencies.yaml",
                "case_ids": [
                    "fastapi.docs.security.bearer-required-missing",
                    "fastapi.docs.security.bearer-required-valid",
                    "fastapi.docs.security.bearer-required-wrong-scheme",
                    "fastapi.docs.security.openapi",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                    "openapi.security",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.document, "
                "openapi.paths, "
                "openapi.security.",
            }
        ],
        "contract_gate": "Linked cases sample "
        "missing/valid/wrong-scheme branches and "
        "selected OpenAPI pointers. Missing: token "
        "issuance, JWT/password policy, all scopes, "
        "browser OAuth and signatures. The mapping "
        "remains partial pending the full FastAPI "
        "manifest and identity/signature checks. "
        "Generic HTTP behavior is assigned to "
        "Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/security/first-steps.md",
                "start_line": 1,
                "end_line": 203,
                "role": "Page-level source evidence "
                "for the documented Security "
                "- First Steps behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and "
                "Security declarations "
                "expose dependency and scope "
                "configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request bodies, "
                "callbacks, and security "
                "metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies and "
                "prepares endpoint "
                "dispatch.",
            },
            {
                "path": "fastapi/security/oauth2.py",
                "start_line": 330,
                "end_line": 510,
                "role": "FastAPI OAuth2 bearer security declarations.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/security/get-current-user.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
        "rationale": "FastAPI resolves nested current-user "
        "dependencies and carries security "
        "metadata into OpenAPI; user lookup and "
        "credential policy are application code.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact "
        "page. The case IDs and selector "
        "unions are listed per recipe; these "
        "are stimuli, not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                "case_ids": ["fastapi.docs.documentation-wave.dependencies-security.current-user"],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                    "openapi.security",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.document, "
                "openapi.paths, "
                "openapi.security.",
            }
        ],
        "contract_gate": "One current-user case and selected "
        "security/path pointers are linked. "
        "Missing: database/JWT behavior, all "
        "dependency failures, scopes, cache "
        "and graph variants. The mapping "
        "remains partial pending the full "
        "FastAPI manifest and "
        "identity/signature checks. Generic "
        "HTTP behavior is assigned to "
        "Starlette 1.6.0 and the separate "
        "Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/security/get-current-user.md",
                "start_line": 1,
                "end_line": 105,
                "role": "Page-level source "
                "evidence for the "
                "documented Get Current "
                "User behavior and "
                "examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute "
                "stores dependency, "
                "response, and OpenAPI "
                "route configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and "
                "Security declarations "
                "expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates "
                "operation parameters, "
                "request bodies, "
                "callbacks, and "
                "security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request "
                "handler parses "
                "declared bodies and "
                "prepares endpoint "
                "dispatch.",
            },
            {
                "path": "fastapi/security/oauth2.py",
                "start_line": 330,
                "end_line": 510,
                "role": "FastAPI OAuth2 bearer security declarations.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette "
                "1.6.0 request "
                "body and JSON "
                "behavior; "
                "generic "
                "request "
                "contract "
                "belongs to "
                "Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
    "tutorial/security/simple-oauth2.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.paths",
            "openapi.request_schema",
        ],
        "rationale": "FastAPI binds OAuth2 form fields and bearer "
        "dependencies and generates their OpenAPI "
        "security contract; password hashing, token "
        "issuance and JWT validation are app-owned.",
        "stimulus_notes": "Reuses input-only recipe cases whose "
        "source_evidence cites this exact page. "
        "The case IDs and selector unions are "
        "listed per recipe; these are stimuli, "
        "not parity results.",
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                "case_ids": [
                    "fastapi.docs.documentation-wave.dependencies-security.simple-oauth2-token-form"
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                    "openapi.request_schema",
                ],
                "coverage": "Selected cases observe "
                "http.body.bytes, "
                "http.headers.ordered, "
                "http.status, "
                "openapi.paths, "
                "openapi.request_schema.",
            }
        ],
        "contract_gate": "One form/token workflow and selected "
        "OpenAPI pointers are linked. Missing: "
        "password/crypto policy, storage, every "
        "invalid token branch and other OAuth "
        "flows. The mapping remains partial "
        "pending the full FastAPI manifest and "
        "identity/signature checks. Generic HTTP "
        "behavior is assigned to Starlette 1.6.0 "
        "and the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/security/simple-oauth2.md",
                "start_line": 1,
                "end_line": 289,
                "role": "Page-level source "
                "evidence for the "
                "documented Simple OAuth2 "
                "with Password and Bearer "
                "behavior and examples.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1161,
                "end_line": 1219,
                "role": "FastAPI APIRoute stores "
                "dependency, response, and "
                "OpenAPI route "
                "configuration.",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 746,
                "end_line": 754,
                "role": "FastAPI Depends and "
                "Security declarations "
                "expose dependency and "
                "scope configuration.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 349,
                "role": "FastAPI builds dependency graph nodes and propagates security scopes.",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI resolves dependency callables, overrides, and injected values.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 400,
                "role": "FastAPI creates operation "
                "parameters, request "
                "bodies, callbacks, and "
                "security metadata.",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 505,
                "role": "FastAPI emits response "
                "schemas and merges "
                "additional response "
                "declarations.",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 375,
                "end_line": 455,
                "role": "FastAPI request handler "
                "parses declared bodies "
                "and prepares endpoint "
                "dispatch.",
            },
            {
                "path": "fastapi/security/oauth2.py",
                "start_line": 14,
                "end_line": 161,
                "role": "FastAPI OAuth2 password form extraction and strict field handling.",
            },
            {
                "path": "fastapi/security/oauth2.py",
                "start_line": 330,
                "end_line": 510,
                "role": "FastAPI OAuth2 bearer security declarations.",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 266,
                "role": "Starlette 1.6.0 "
                "request body and "
                "JSON behavior; "
                "generic request "
                "contract belongs "
                "to Starlette-RS.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 65,
                "role": "Starlette 1.6.0 response construction, body rendering, and header setup.",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 ASGI response emission.",
            },
        ],
    },
}

DOC_PAGE_EXCLUSION_MAPPINGS = {
    "_llm-test.md": {
        "exclusion_reason": "Repository meta-test page, not a user-facing FastAPI feature.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/_llm-test.md",
                "start_line": 1,
                "end_line": 495,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "about/index.md": {
        "exclusion_reason": "Orientation/community/resource content has no independent "
        "FastAPI runtime observation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/about/index.md",
                "start_line": 1,
                "end_line": 3,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "advanced/advanced-python-types.md": {
        "exclusion_reason": "Explains Python Union and Optional "
        "typing without specifying FastAPI "
        "behavior; response_model is mentioned "
        "only as a typing example.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/advanced-python-types.md",
                "start_line": 1,
                "end_line": 61,
                "role": "Page-level evidence "
                "supporting exclusion from "
                "FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "advanced/index.md": {
        "exclusion_reason": "Section landing/navigation page; independently "
        "observable features are mapped to their linked "
        "reference pages and examples.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/index.md",
                "start_line": 1,
                "end_line": 21,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "advanced/security/index.md": {
        "exclusion_reason": "Security section index with no behavior "
        "beyond the focused FastAPI security "
        "tutorials, which carry their own input "
        "workflows.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/security/index.md",
                "start_line": 1,
                "end_line": 19,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "alternatives.md": {
        "exclusion_reason": "Comparative overview without an independently observable "
        "FastAPI runtime contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/alternatives.md",
                "start_line": 1,
                "end_line": 485,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "benchmarks.md": {
        "exclusion_reason": "Performance discussion is not a parity stimulus; benchmark "
        "workloads and correctness gates are specified separately.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/benchmarks.md",
                "start_line": 1,
                "end_line": 34,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "contributing.md": {
        "exclusion_reason": "Contribution guidance links out to project contribution "
        "instructions; no FastAPI runtime behavior is specified.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/contributing.md",
                "start_line": 1,
                "end_line": 7,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "deployment/cloud.md": {
        "exclusion_reason": "Deployment-provider or deployment-process guidance "
        "is outside the FastAPI library API contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/cloud.md",
                "start_line": 1,
                "end_line": 24,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "deployment/concepts.md": {
        "exclusion_reason": "Deployment-provider or deployment-process "
        "guidance is outside the FastAPI library API "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/concepts.md",
                "start_line": 1,
                "end_line": 321,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "deployment/docker.md": {
        "exclusion_reason": "Deployment-provider or deployment-process guidance "
        "is outside the FastAPI library API contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/docker.md",
                "start_line": 1,
                "end_line": 614,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "deployment/fastapicloud.md": {
        "exclusion_reason": "Deployment-provider or deployment-process "
        "guidance is outside the FastAPI library API "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/fastapicloud.md",
                "start_line": 1,
                "end_line": 47,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "deployment/https.md": {
        "exclusion_reason": "Deployment-provider or deployment-process guidance "
        "is outside the FastAPI library API contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/https.md",
                "start_line": 1,
                "end_line": 231,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "deployment/index.md": {
        "exclusion_reason": "Deployment-provider or deployment-process guidance "
        "is outside the FastAPI library API contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/index.md",
                "start_line": 1,
                "end_line": 23,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "deployment/manually.md": {
        "exclusion_reason": "Deployment-provider or deployment-process "
        "guidance is outside the FastAPI library API "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/manually.md",
                "start_line": 1,
                "end_line": 156,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "deployment/server-workers.md": {
        "exclusion_reason": "Server worker startup, process count, and "
        "deployment behavior belong to Uvicorn and "
        "the deployment environment, outside "
        "FastAPI's library contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/server-workers.md",
                "start_line": 1,
                "end_line": 139,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "deployment/versions.md": {
        "exclusion_reason": "Deployment-provider or deployment-process "
        "guidance is outside the FastAPI library API "
        "contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/deployment/versions.md",
                "start_line": 1,
                "end_line": 93,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "editor-support.md": {
        "exclusion_reason": "Editor and language-server integration is tooling "
        "behavior, not FastAPI runtime behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/editor-support.md",
                "start_line": 1,
                "end_line": 23,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "environment-variables.md": {
        "exclusion_reason": "Environment parsing in this guide is supplied "
        "by Pydantic Settings and deployment "
        "configuration, not an independent FastAPI "
        "runtime feature.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/environment-variables.md",
                "start_line": 1,
                "end_line": 11,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "external-links.md": {
        "exclusion_reason": "Community-link generation produces documentation-site "
        "links, not FastAPI runtime behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/external-links.md",
                "start_line": 1,
                "end_line": 30,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "fastapi-cli.md": {
        "exclusion_reason": "The page delegates the `fastapi` console entrypoint to a "
        "separate fastapi-cli package. Treat this as a visible "
        "package-pin and process-workflow boundary; the CLI is "
        "excluded from current executable inputs until its product "
        "identity and argv/stdout/stderr/exit contract are "
        "selected.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/fastapi-cli.md",
                "start_line": 1,
                "end_line": 138,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "fastapi-people.md": {
        "exclusion_reason": "Template-generated maintainer, contributor, reviewer, "
        "and sponsor information has no FastAPI runtime "
        "observation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/fastapi-people.md",
                "start_line": 1,
                "end_line": 193,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "features.md": {
        "exclusion_reason": "Broad feature index with no independent stimulus; the "
        "focused feature pages carry the relevant FastAPI workflows.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/features.md",
                "start_line": 1,
                "end_line": 201,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "help-fastapi.md": {
        "exclusion_reason": "Community and support guidance, including a promotional "
        "deployment mention, does not specify CLI or runtime "
        "behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/help-fastapi.md",
                "start_line": 1,
                "end_line": 79,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "history-design-future.md": {
        "exclusion_reason": "Historical and design narrative, not behavior "
        "in the pinned FastAPI 0.141.1 contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/history-design-future.md",
                "start_line": 1,
                "end_line": 79,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "how-to/general.md": {
        "exclusion_reason": "How-to navigation page with no independently "
        "observable behavior; focused guides are mapped "
        "separately.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/how-to/general.md",
                "start_line": 1,
                "end_line": 43,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "how-to/graphql.md": {
        "exclusion_reason": "GraphQL routing and schema execution are "
        "third-party-owned; the page provides no independent "
        "FastAPI behavior case.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/how-to/graphql.md",
                "start_line": 1,
                "end_line": 60,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "how-to/index.md": {
        "exclusion_reason": "Section landing/navigation page; independently "
        "observable features are mapped to their linked reference "
        "pages and examples.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/how-to/index.md",
                "start_line": 1,
                "end_line": 13,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "how-to/migrate-from-pydantic-v1-to-pydantic-v2.md": {
        "exclusion_reason": "Migration guidance "
        "concerns Pydantic "
        "model APIs; the "
        "selected FastAPI "
        "contract pins Pydantic "
        "2.13.4 and maps its "
        "integration "
        "separately.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/how-to/migrate-from-pydantic-v1-to-pydantic-v2.md",
                "start_line": 1,
                "end_line": 153,
                "role": "Page-level "
                "evidence "
                "supporting "
                "exclusion "
                "from "
                "FastAPI "
                "runtime "
                "feature "
                "coverage.",
            }
        ],
    },
    "how-to/testing-database.md": {
        "exclusion_reason": "The page links to external SQLModel database "
        "tutorials and specifies no FastAPI behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/how-to/testing-database.md",
                "start_line": 1,
                "end_line": 7,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "index.md": {
        "exclusion_reason": "Section landing/navigation page; independently observable "
        "features are mapped to their linked reference pages and "
        "examples.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/index.md",
                "start_line": 1,
                "end_line": 587,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "learn/index.md": {
        "exclusion_reason": "Orientation/community/resource content has no independent "
        "FastAPI runtime observation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/learn/index.md",
                "start_line": 1,
                "end_line": 5,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "management.md": {
        "exclusion_reason": "Repository management and contribution governance are "
        "outside the FastAPI runtime contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/management.md",
                "start_line": 1,
                "end_line": 15,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "newsletter.md": {
        "exclusion_reason": "Newsletter signup and project communication content do not "
        "specify FastAPI runtime behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/newsletter.md",
                "start_line": 1,
                "end_line": 5,
                "role": "Page-level evidence supporting exclusion from "
                "FastAPI runtime feature coverage.",
            }
        ],
    },
    "project-generation.md": {
        "exclusion_reason": "Project scaffolding and generated template "
        "behavior belong to separate tooling, outside the "
        "FastAPI runtime API.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/project-generation.md",
                "start_line": 1,
                "end_line": 28,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "reference/index.md": {
        "exclusion_reason": "Section landing/navigation page; independently "
        "observable features are mapped to their linked "
        "reference pages and examples.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/index.md",
                "start_line": 1,
                "end_line": 7,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "reference/openapi/index.md": {
        "exclusion_reason": "Short OpenAPI section overview with no "
        "independently documented callable or "
        "observable behavior; detailed utilities and "
        "models are mapped on their own pages.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/openapi/index.md",
                "start_line": 1,
                "end_line": 5,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
    "release-notes.md": {
        "exclusion_reason": "Release notes span multiple historical versions and do "
        "not define one behavior of pinned FastAPI 0.141.1.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/release-notes.md",
                "start_line": 1,
                "end_line": 7348,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "resources/index.md": {
        "exclusion_reason": "Orientation/community/resource content has no "
        "independent FastAPI runtime observation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/resources/index.md",
                "start_line": 1,
                "end_line": 3,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "translation-banner.md": {
        "exclusion_reason": "Translation-quality notice and editorial link do "
        "not describe framework behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/translation-banner.md",
                "start_line": 1,
                "end_line": 11,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime feature "
                "coverage.",
            }
        ],
    },
    "translations.md": {
        "exclusion_reason": "Translation content does not define an independently "
        "observable FastAPI runtime behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/translations.md",
                "start_line": 1,
                "end_line": 28,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "tutorial/index.md": {
        "exclusion_reason": "Section landing/navigation page; independently "
        "observable features are mapped to their linked "
        "reference pages and examples.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/index.md",
                "start_line": 1,
                "end_line": 141,
                "role": "Page-level evidence supporting exclusion "
                "from FastAPI runtime feature coverage.",
            }
        ],
    },
    "virtual-environments.md": {
        "exclusion_reason": "Python environment creation and package "
        "installation guidance is contributor/setup "
        "tooling, not FastAPI runtime behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/virtual-environments.md",
                "start_line": 1,
                "end_line": 35,
                "role": "Page-level evidence supporting "
                "exclusion from FastAPI runtime "
                "feature coverage.",
            }
        ],
    },
}
