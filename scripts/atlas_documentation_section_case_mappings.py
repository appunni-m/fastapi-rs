"""Reviewed section-level links from FastAPI documentation to input cases."""

DOC_SECTION_CASE_MAPPINGS = {
    ("tutorial/cors.md", "cors-preflight-requests"): {
        "heading": "CORS preflight requests { #cors-preflight-requests }",
        "start_line": 69,
        "end_line": 74,
        "recipe_path": "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml",
        "case_ids": [
            "fastapi.docs.cors-tutorial.allowed-preflight",
            "fastapi.docs.cors-tutorial.disallowed-preflight-method",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The section defines preflight requests as OPTIONS with Origin and "
            "Access-Control-Request-Method; these independent allowed and rejected "
            "inputs observe the response body, headers, and status."
        ),
        "rationale": (
            "This section's request shape and allowed/rejected outcomes are isolated from "
            "the neighboring simple-request section. FastAPI re-exports CORSMiddleware; "
            "Starlette owns the middleware behavior."
        ),
    },
    ("tutorial/cors.md", "simple-requests"): {
        "heading": "Simple requests { #simple-requests }",
        "start_line": 75,
        "end_line": 78,
        "recipe_path": "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml",
        "case_ids": [
            "fastapi.docs.cors-tutorial.allowed-simple-request",
            "fastapi.docs.cors-tutorial.unlisted-simple-request",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The section describes passing requests with Origin through the application "
            "while adding CORS headers; these independent allowed and unlisted origins "
            "observe response body, headers, and status."
        ),
        "rationale": (
            "This section's normal-request behavior is sampled separately from preflight. "
            "FastAPI re-exports CORSMiddleware; Starlette owns the middleware behavior."
        ),
    },
    (
        "tutorial/response-model.md",
        "use-the-response-model-exclude-unset-parameter",
    ): {
        "heading": (
            "Use the `response_model_exclude_unset` parameter "
            "{ #use-the-response-model-exclude-unset-parameter }"
        ),
        "start_line": 237,
        "end_line": 305,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/response-model-post-policy-options-review.yaml"
        ),
        "case_ids": ["fastapi.response-model.post-policy.exclude-unset"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "This POST input samples response_model_exclude_unset=True with an explicitly "
            "set nullable field and alias. It does not claim every exclude policy or model "
            "serialization behavior."
        ),
        "rationale": (
            "FastAPI routes the decorator's exclude_unset option into response-model "
            "serialization; Pydantic performs the value serialization."
        ),
    },
    (
        "tutorial/response-model.md",
        "response-model-include-and-response-model-exclude",
    ): {
        "heading": (
            "`response_model_include` and `response_model_exclude` "
            "{ #response-model-include-and-response-model-exclude }"
        ),
        "start_line": 306,
        "end_line": 339,
        "recipe_path": "tests/fixtures/input-recipes/parity/response-model-serialization.yaml",
        "case_ids": [
            "fastapi.response-model.include.nested",
            "fastapi.response-model.exclude.nested",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The two GET inputs sample nested include and exclude field selection. They do "
            "not claim changes to the complete Pydantic model schema in OpenAPI."
        ),
        "rationale": (
            "FastAPI passes the decorator's include and exclude selections to response "
            "serialization; Pydantic performs the value serialization."
        ),
    },
    ("advanced/response-change-status-code.md", "use-a-response-parameter"): {
        "heading": "Use a `Response` parameter { #use-a-response-parameter }",
        "start_line": 17,
        "end_line": 31,
        "recipe_path": "tests/fixtures/input-recipes/parity/response-policy-matrix.yaml",
        "case_ids": [
            "fastapi.response.dependency-status",
            "fastapi.response.status-overwrite",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "These inputs sample dependency-set status and endpoint status overwrite through "
            "the injected temporary Response. The Response class and wire semantics belong "
            "to Starlette."
        ),
        "rationale": (
            "FastAPI injects the temporary response and merges its status and headers into "
            "the returned response; Starlette owns the Response implementation."
        ),
    },
    ("tutorial/schema-extra-example.md", "using-the-openapi-examples-parameter"): {
        "heading": "Using the `openapi_examples` Parameter { #using-the-openapi-examples-parameter }",
        "start_line": 91,
        "end_line": 115,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/openapi-examples-named-body-external.yaml"
        ),
        "case_ids": ["fastapi.schema-extra-example.openapi-examples.named-body-external-value"],
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
        ],
        "scope_note": (
            "This input samples one named external body example in generated OpenAPI and the "
            "documented response status. It does not claim other parameter locations."
        ),
        "rationale": (
            "FastAPI retains openapi_examples on parameter metadata and emits it into the "
            "OpenAPI operation."
        ),
    },
    ("advanced/path-operation-advanced-configuration.md", "openapi-operationid"): {
        "heading": "OpenAPI operationId { #openapi-operationid }",
        "start_line": 3,
        "end_line": 32,
        "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-post-operation-id-isolated.yaml",
        "case_ids": ["fastapi.path-operation.post-operation-id-isolated"],
        "observation_selectors": ["openapi.document", "openapi.paths"],
        "scope_note": (
            "This input observes the selected path operation ID. It does not claim ID "
            "uniqueness or every schema-generation path."
        ),
        "rationale": (
            "FastAPI selects the route operation ID and writes it into the generated OpenAPI "
            "operation."
        ),
    },
    ("advanced/path-operation-advanced-configuration.md", "openapi-extensions"): {
        "heading": "OpenAPI Extensions { #openapi-extensions }",
        "start_line": 85,
        "end_line": 125,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/"
            "path-operation-advanced-configurations-tutorial005-upstream.yaml"
        ),
        "case_ids": ["fastapi.path-operation-advanced-configurations.tutorial005"],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "The OpenAPI observation targets the tutorial's route extension. The endpoint "
            "response body is authored by the example and is included only as a separate "
            "observed output."
        ),
        "rationale": (
            "FastAPI merges the route's openapi_extra value into the generated operation; "
            "the selected OpenAPI pointer scopes this claim to the documented extension."
        ),
    },
    ("advanced/additional-responses.md", "additional-media-types-for-the-main-response"): {
        "heading": "Additional media types for the main response { #additional-media-types-for-the-main-response }",
        "start_line": 172,
        "end_line": 193,
        "recipe_path": "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml",
        "case_ids": ["fastapi.additional-response-openapi-wave.media-content.test-openapi-schema"],
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "This case observes the documented image/png response declaration in the selected "
            "OpenAPI operation. It does not claim file-response transport behavior."
        ),
        "rationale": (
            "FastAPI combines route response declarations and response-field schemas in "
            "OpenAPI; file and response-class behavior belongs to Starlette."
        ),
    },
    ("how-to/conditional-openapi.md", "conditional-openapi-from-settings-and-env-vars"): {
        "heading": "Conditional OpenAPI from settings and env vars { #conditional-openapi-from-settings-and-env-vars }",
        "start_line": 26,
        "end_line": 56,
        "recipe_path": "tests/fixtures/input-recipes/parity/atlas-openapi-conditional-interface-review.yaml",
        "case_ids": [
            "fastapi.atlas-openapi-tutorial.conditional-hidden-docs",
            "fastapi.atlas-openapi-tutorial.default-docs-and-schema",
        ],
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
        ],
        "scope_note": (
            "These inputs sample hidden docs and default docs/schema routes through FastAPI's "
            "URL options. External settings construction is outside the case."
        ),
        "rationale": (
            "FastAPI registers its schema and documentation routes according to openapi_url, "
            "docs_url, and redoc_url configuration."
        ),
    },
    ("how-to/extending-openapi.md", "cache-the-openapi-schema"): {
        "heading": "Cache the OpenAPI schema { #cache-the-openapi-schema }",
        "start_line": 68,
        "end_line": 77,
        "recipe_path": "tests/fixtures/input-recipes/parity/openapi-cache-direct-add-api-route.yaml",
        "case_ids": ["fastapi.applications.openapi.cache-direct-add-api-route"],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "This input samples the direct-add-route cache invalidation scenario only. It does "
            "not claim every OpenAPI cache lifecycle."
        ),
        "rationale": (
            "FastAPI caches the generated schema and tracks route-list version changes for "
            "direct route additions."
        ),
    },
    ("advanced/behind-a-proxy.md", "setting-the-root-path-in-the-fastapi-app"): {
        "heading": "Setting the `root_path` in the FastAPI app { #setting-the-root-path-in-the-fastapi-app }",
        "start_line": 219,
        "end_line": 226,
        "recipe_path": "tests/fixtures/input-recipes/parity/behind-proxy-tutorial002-upstream.yaml",
        "case_ids": ["fastapi.behind-proxy.tutorial002.app-root-path"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "The example returns the app root_path from the scope. Generic path matching and "
            "proxy-server behavior remain Starlette/server-owned."
        ),
        "rationale": ("FastAPI stores the app root_path and places it in the ASGI scope."),
    },
    ("advanced/behind-a-proxy.md", "additional-servers"): {
        "heading": "Additional servers { #additional-servers }",
        "start_line": 387,
        "end_line": 461,
        "recipe_path": "tests/fixtures/input-recipes/parity/behind-proxy-tutorial004-upstream.yaml",
        "case_ids": ["fastapi.behind-proxy.tutorial004.openapi-servers"],
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "scope_note": (
            "This case selects the OpenAPI servers array after a root_path request. It does "
            "not assert generic proxy-header interpretation."
        ),
        "rationale": (
            "FastAPI can prepend the request root_path as an OpenAPI server when configured; "
            "proxy handling itself remains outside this claim."
        ),
    },
    ("advanced/custom-response.md", "default-response-class"): {
        "heading": "Default response class { #default-response-class }",
        "start_line": 255,
        "end_line": 270,
        "recipe_path": "tests/fixtures/input-recipes/parity/router-overrides.yaml",
        "case_ids": ["fastapi.routing.include-router.default-response-class-openapi-media-type"],
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "This input samples the router default response class's OpenAPI media type only. "
            "Response-class construction and wire behavior belong to Starlette."
        ),
        "rationale": (
            "FastAPI resolves the router's default response class when constructing a route "
            "and reads its media type for OpenAPI."
        ),
    },
}
