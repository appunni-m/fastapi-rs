"""Source-reviewed overrides for FastAPI tutorial-page atlas candidates.

This file is intentionally separate from the atlas generator.  The source
checkout used for the review is FastAPI 0.141.1; Starlette ownership notes are
against the selected Starlette 1.6.0 contract.
"""

DOC_PAGE_REVIEW_MAPPINGS = {
    "tutorial/body-fields.md": {
        "heading": "Body - Fields { #body-fields }",
        "replace_features": True,
        "feature_ids": ["openapi-docs", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "openapi.document",
            "python.import_path",
            "python.signature",
        ],
        "rationale": (
            "The page covers Pydantic Field metadata and FastAPI Body/Query/Path parameter "
            "classes in request schemas. Its path-operation mentions are context, not routing "
            "behavior; public Param imports/signatures are relevant, while generic exception "
            "and warning selectors are not."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/body-fields.md",
                "start_line": 1,
                "end_line": 40,
                "role": "Body/Query/Path metadata and public Param class explanation",
            }
        ],
    },
    "tutorial/cookie-params.md": {
        "heading": "Cookie Parameters { #cookie-parameters }",
        "replace_features": True,
        "feature_ids": ["app-routing", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "python.import_path",
            "python.signature",
        ],
        "rationale": (
            "Cookie extraction/validation and FastAPI's Cookie parameter import/signature are "
            "documented. The public-api-errors feature is selected for that parameter API, not "
            "for exception or warning behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/cookie-params.md",
                "start_line": 1,
                "end_line": 29,
                "role": "Cookie parameter import, validation options, and FastAPI Param class note",
            }
        ],
    },
    "tutorial/header-params.md": {
        "heading": "Header Parameters { #header-parameters }",
        "replace_features": True,
        "feature_ids": ["app-routing", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "python.import_path",
            "python.signature",
        ],
        "rationale": (
            "Header extraction and validation are core; public-api-errors is relevant only for "
            "the FastAPI Header parameter import/signature. The generated family-wide error and "
            "warning selectors do not follow from the page's 'Param class' terminology."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/header-params.md",
                "start_line": 1,
                "end_line": 35,
                "role": "Header parameter import, validation options, and public Param class note",
            }
        ],
    },
    "tutorial/dependencies/sub-dependencies.md": {
        "heading": "Sub-dependencies { #sub-dependencies }",
        "replace_features": True,
        "feature_ids": ["dependency-security"],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "openapi.paths",
        ],
        "rationale": (
            "The page documents nested dependency resolution, query/cookie fallback, and "
            "per-request dependency caching. The independent fixture mappings cover query/cookie "
            "responses and selected OpenAPI paths, plus cache reuse and use_cache=False through "
            "HTTP responses; they do not observe dependency call/cleanup order, security scopes, "
            "validation failures, route matching, or request-object internals. FastAPI owns the "
            "dependency graph, parameter binding, and cache decision. Generic Request "
            "query/cookie access remains Starlette 1.6.0-owned; the fixture's route dispatch is "
            "only the entry point for these dependency observations."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/dependencies/sub-dependencies.md",
                "start_line": 9,
                "end_line": 54,
                "role": "nested dependency graph and query/cookie fallback example",
            },
            {
                "path": "docs/en/docs/tutorial/dependencies/sub-dependencies.md",
                "start_line": 57,
                "end_line": 85,
                "role": "per-request dependency cache and use_cache=False contract",
            },
            {
                "path": "docs_src/dependencies/tutorial005_py310.py",
                "start_line": 1,
                "end_line": 20,
                "role": "pinned query/cookie dependency example used by the page",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 697,
                "role": "FastAPI recursive solve/cache and query/cookie parameter binding",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 138,
                "end_line": 159,
                "role": "generic Starlette 1.6.0 Request query-parameter and cookie access",
            }
        ],
    },
    "tutorial/path-params-numeric-validations.md": {
        "heading": "Path Parameters and Numeric Validations { #path-parameters-and-numeric-validations }",
        "replace_features": True,
        "feature_ids": ["app-routing", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "python.import_path",
            "python.signature",
        ],
        "rationale": (
            "This is a real path/query validation and FastAPI Path/Query API page. The public "
            "API selectors apply to those imports/signatures; no Python warnings or escaping "
            "error-class observations are documented."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/path-params-numeric-validations.md",
                "start_line": 1,
                "end_line": 17,
                "role": "Path and Query imports and numeric validation tutorial scope",
            },
            {
                "path": "docs/en/docs/tutorial/path-params-numeric-validations.md",
                "start_line": 94,
                "end_line": 127,
                "role": "numeric boundary validation and recap",
            },
        ],
    },
    "tutorial/schema-extra-example.md": {
        "heading": "Declare Request Example Data { #declare-request-example-data }",
        "replace_features": True,
        "feature_ids": ["openapi-docs", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "openapi.document",
            "openapi.request_schema",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
            "python.import_path",
            "python.signature",
        ],
        "rationale": (
            "This page specifies JSON Schema/OpenAPI examples for request declarations, including "
            "the deprecated `example` option. The generic path-operation context does not make "
            "routing or HTTP request execution part of this feature. Deprecation appears in the "
            "schema/docs, not as a Python warning."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/schema-extra-example.md",
                "start_line": 1,
                "end_line": 65,
                "role": "request examples, deprecated schema field, and docs UI output",
            },
            {
                "path": "docs/en/docs/tutorial/schema-extra-example.md",
                "start_line": 91,
                "end_line": 118,
                "role": "OpenAPI-specific example parameter and interactive docs rendering",
            },
        ],
    },
    "tutorial/handling-errors.md": {
        "heading": "Handling Errors { #handling-errors }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "public-api-errors",
            "python-data-encoding",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "python.attribute_value",
            "python.import_path",
            "python.object_identity",
            "python.signature",
            "error.class",
            "error.public_attributes",
        ],
        "rationale": (
            "The page covers HTTPException construction/handling, request-validation errors, "
            "custom handlers, and a jsonable_encoder error payload. The security mention is an "
            "example context, not dependency/security behavior. Direct Starlette Request/response "
            "imports are facade identity checks; their generic implementations stay Starlette-owned."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/handling-errors.md",
                "start_line": 22,
                "end_line": 108,
                "role": "HTTPException behavior, exception handler setup, and Starlette imports",
            },
            {
                "path": "docs/en/docs/tutorial/handling-errors.md",
                "start_line": 112,
                "end_line": 188,
                "role": "FastAPI request-validation error handlers and error body",
            },
            {
                "path": "docs/en/docs/tutorial/handling-errors.md",
                "start_line": 218,
                "end_line": 240,
                "role": "FastAPI HTTPException subclass versus Starlette exception handling",
            },
            {
                "path": "fastapi/exceptions.py",
                "start_line": 17,
                "end_line": 83,
                "role": "FastAPI HTTPException class and JSON-capable detail contract",
            },
            {
                "path": "fastapi/requests.py",
                "start_line": 1,
                "end_line": 2,
                "role": "direct Starlette Request and HTTPConnection re-exports",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/exceptions.py",
                "start_line": 7,
                "end_line": 18,
                "role": "selected Starlette HTTPException base contract",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 173,
                "end_line": 190,
                "role": "generic Starlette HTML/JSON response classes",
            },
        ],
    },
    "tutorial/background-tasks.md": {
        "heading": "Background Tasks { #background-tasks }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "public-api-errors",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "dependency.call_order",
            "response.background_effects",
            "python.import_path",
            "python.signature",
        ],
        "rationale": (
            "The tutorial covers FastAPI injection of BackgroundTasks, merging tasks "
            "from dependencies, and request values used by those tasks. File/path "
            "tokens are incidental and do not justify request error/schema selectors. "
            "FastAPI's BackgroundTasks is a subclass with an add_task wrapper; task "
            "execution remains Starlette-owned."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/background-tasks.md",
                "start_line": 14,
                "end_line": 74,
                "role": "injection, merged dependency tasks, response timing, and Starlette boundary",
            },
            {
                "path": "fastapi/background.py",
                "start_line": 5,
                "end_line": 61,
                "role": "FastAPI BackgroundTasks subclass and documented add_task wrapper",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/background.py",
                "start_line": 12,
                "end_line": 36,
                "role": "generic task invocation and sequential BackgroundTasks execution",
            }
        ],
    },
    "tutorial/cors.md": {
        "heading": "CORS (Cross-Origin Resource Sharing) { #cors-cross-origin-resource-sharing }",
        "replace_features": True,
        "feature_ids": ["middleware-integrations", "public-api-errors"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "This page documents CORS middleware configuration and its response headers; "
            "the example route and CORS header names are not FastAPI route validation. "
            "The FastAPI middleware module directly re-exports Starlette's class, so "
            "only the FastAPI import identity is FastAPI-owned here."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/cors.md",
                "start_line": 35,
                "end_line": 87,
                "role": "CORS configuration, preflight/simple responses, and direct-Starlette note",
            },
            {
                "path": "fastapi/middleware/cors.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette CORSMiddleware re-export",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/middleware/cors.py",
                "start_line": 15,
                "end_line": 27,
                "role": "selected Starlette 1.6.0 CORSMiddleware implementation and options",
            }
        ],
    },
    "tutorial/encoder.md": {
        "heading": "JSON Compatible Encoder { #json-compatible-encoder }",
        "replace_features": True,
        "feature_ids": ["python-data-encoding"],
        "observation_selectors": ["python.attribute_value", "python.signature"],
        "rationale": (
            "This is a direct jsonable_encoder call and conversion tutorial. Its generic "
            "'data structure' wording and Pydantic input examples do not document FastAPI "
            "request validation or an error/deprecation surface."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/encoder.md",
                "start_line": 1,
                "end_line": 35,
                "role": "jsonable_encoder conversion behavior and public call example",
            },
            {
                "path": "fastapi/encoders.py",
                "start_line": 119,
                "end_line": 206,
                "role": "pinned encoder signature and options",
            },
        ],
    },
    "tutorial/debugging.md": {
        "heading": "Debugging { #debugging }",
        "replace_features": True,
        "feature_ids": [],
        "observation_selectors": [],
        "rationale": (
            "The page is Python debugger and Uvicorn launch guidance. Its linked FastAPI "
            "example is only a trivial root route; the page specifies no independent "
            "FastAPI runtime behavior."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/debugging.md",
                "start_line": 1,
                "end_line": 113,
                "role": "debugger and direct-Uvicorn usage guidance",
            },
            {
                "path": "docs_src/debugging/tutorial001_py310.py",
                "start_line": 1,
                "end_line": 15,
                "role": "incidental root route and uvicorn.run example",
            },
        ],
    },
    "tutorial/first-steps.md": {
        "heading": "First Steps { #first-steps }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "middleware-integrations",
            "openapi-docs",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "openapi.document",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
            "process.stdout",
        ],
        "rationale": (
            "The page demonstrates a root route returning JSON, generated OpenAPI and "
            "docs endpoints, and the fastapi dev command. Its request-validation match "
            "comes from URL/file vocabulary and Pydantic response prose; the GraphQL "
            "analogy is not a middleware integration. The CLI family is retained only "
            "for the documented command/output."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/first-steps.md",
                "start_line": 57,
                "end_line": 150,
                "role": "JSON response, docs endpoints, and generated OpenAPI",
            },
            {
                "path": "docs/en/docs/tutorial/first-steps.md",
                "start_line": 390,
                "end_line": 427,
                "role": "return-value conversion and documented fastapi dev command",
            },
        ],
    },
    "tutorial/frontend.md": {
        "heading": "Frontend { #frontend }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "middleware-integrations",
            "public-api-errors",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "dependency.call_order",
            "response.background_effects",
            "python.signature",
            "warnings.category_message",
            "error.class",
        ],
        "rationale": (
            "The page specifies FastAPI frontend fallback precedence, router integration, "
            "dependency/middleware application, and app-creation missing-directory "
            "warning/error behavior. Path/file terms do not describe request validation; "
            "the filesystem response body is still an observable shared with Starlette."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/frontend.md",
                "start_line": 1,
                "end_line": 18,
                "role": "FastAPI frontend and API-route precedence",
            },
            {
                "path": "docs/en/docs/tutorial/frontend.md",
                "start_line": 107,
                "end_line": 145,
                "role": "directory warnings/errors, router precedence, dependencies, and middleware",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1222,
                "end_line": 1299,
                "role": "FastAPI app.frontend public signature and router delegation",
            },
        ],
    },
    "tutorial/metadata.md": {
        "heading": "Metadata and Docs URLs { #metadata-and-docs-urls }",
        "replace_features": True,
        "feature_ids": ["openapi-docs"],
        "observation_selectors": [
            "openapi.document",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
        ],
        "rationale": (
            "This page configures API/tag metadata and OpenAPI/docs URLs. Its request-validation "
            "match is from path-operation/path vocabulary; it has no request parameter or body case."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/metadata.md",
                "start_line": 1,
                "end_line": 120,
                "role": "API/tag metadata, OpenAPI URL, and docs URL configuration",
            }
        ],
    },
    "tutorial/middleware.md": {
        "heading": "Middleware { #middleware }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "middleware-integrations",
            "public-api-errors",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "dependency.call_order",
            "dependency.cleanup_order",
            "response.background_effects",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "The request-validation match is only path/header wording. The page explicitly "
            "covers middleware nesting plus yield-dependency cleanup and background-task "
            "ordering, so response-serialization is missing from the lexical map. Request "
            "and response middleware execution order has no dedicated selector in FEATURES. "
            "The Request import is a direct Starlette re-export."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/middleware.md",
                "start_line": 1,
                "end_line": 89,
                "role": "middleware lifecycle, dependency/task order, and nested execution order",
            },
            {
                "path": "docs/en/docs/tutorial/middleware.md",
                "start_line": 44,
                "end_line": 49,
                "role": "FastAPI Request import convenience and Starlette ownership",
            },
            {
                "path": "fastapi/requests.py",
                "start_line": 1,
                "end_line": 2,
                "role": "direct Starlette Request and HTTPConnection re-exports",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 226,
                "role": "selected Starlette Request implementation",
            }
        ],
        "contract_gate": (
            "The ordered request/response middleware trace is not representable by current "
            "FEATURES selectors; add a reviewed middleware.execution_order observation before "
            "treating nesting order as an executable schema case."
        ),
    },
    "tutorial/path-operation-configuration.md": {
        "heading": "Path Operation Configuration { #path-operation-configuration }",
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "public-api-errors"],
        "observation_selectors": [
            "http.status",
            "openapi.document",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "The page documents route status/metadata/deprecation in generated docs and the "
            "fastapi.status convenience alias. It has no request-input validation case; a "
            "deprecated operation marker is an OpenAPI observation, not a Python warning."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/path-operation-configuration.md",
                "start_line": 11,
                "end_line": 39,
                "role": "response status, FastAPI status alias, and OpenAPI metadata",
            },
            {
                "path": "docs/en/docs/tutorial/path-operation-configuration.md",
                "start_line": 91,
                "end_line": 103,
                "role": "deprecated path-operation marker in interactive docs",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 5,
                "end_line": 5,
                "role": "FastAPI root status re-export",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/status.py",
                "start_line": 100,
                "end_line": 123,
                "role": "generic status constants re-exported by FastAPI",
            }
        ],
    },
    "tutorial/query-params-str-validations.md": {
        "heading": "Query Parameters and String Validations { #query-parameters-and-string-validations }",
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "openapi.document",
            "python.signature",
        ],
        "rationale": (
            "The page is query parsing/validation, OpenAPI metadata, and the deprecated Query "
            "parameter option. Dependency-security was selected only by a sentence recommending "
            "dependencies for validations requiring external services; no dependency is declared here."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/query-params-str-validations.md",
                "start_line": 64,
                "end_line": 124,
                "role": "query validation and generated OpenAPI behavior",
            },
            {
                "path": "docs/en/docs/tutorial/query-params-str-validations.md",
                "start_line": 347,
                "end_line": 383,
                "role": "deprecated parameter option and custom validation example",
            },
            {
                "path": "docs/en/docs/tutorial/query-params-str-validations.md",
                "start_line": 393,
                "end_line": 393,
                "role": "incidental recommendation to use dependencies, not a dependency example",
            },
        ],
    },
    "tutorial/request-files.md": {
        "heading": "Request Files { #request-files }",
        "replace_features": True,
        "feature_ids": ["app-routing", "public-api-errors", "request-validation"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "The request-file mapping is valid, and the page also documents the FastAPI "
            "responses import as a direct Starlette convenience. File-upload handling itself "
            "is an input contract; generic response classes remain Starlette-owned."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/request-files.md",
                "start_line": 1,
                "end_line": 40,
                "role": "file and upload request parameters",
            },
            {
                "path": "docs/en/docs/tutorial/request-files.md",
                "start_line": 150,
                "end_line": 166,
                "role": "FastAPI response import convenience from Starlette",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 6,
                "end_line": 12,
                "role": "direct Starlette response-class re-exports",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/responses.py",
                "start_line": 173,
                "end_line": 181,
                "role": "selected Starlette HTMLResponse implementation",
            }
        ],
    },
    "tutorial/response-status-code.md": {
        "heading": "Response Status Code { #response-status-code }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "public-api-errors",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "openapi.document",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "The page explicitly distinguishes decorator status_code from function/request "
            "parameters and documents response/OpenAPI status behavior. The request-validation "
            "match is a false positive. It also explicitly documents FastAPI's direct Starlette "
            "status re-export."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/response-status-code.md",
                "start_line": 1,
                "end_line": 38,
                "role": "status_code response and OpenAPI semantics; excludes request validation",
            },
            {
                "path": "docs/en/docs/tutorial/response-status-code.md",
                "start_line": 83,
                "end_line": 95,
                "role": "FastAPI status import convenience and Starlette ownership",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 5,
                "end_line": 5,
                "role": "FastAPI root status re-export",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/status.py",
                "start_line": 100,
                "end_line": 123,
                "role": "generic status constants re-exported by FastAPI",
            }
        ],
    },
    "tutorial/security/index.md": {
        "heading": "Security { #security }",
        "replace_features": True,
        "feature_ids": ["dependency-security", "openapi-docs"],
        "observation_selectors": ["openapi.document", "openapi.security"],
        "rationale": (
            "The query/header/cookie terms describe locations for OpenAPI apiKey schemes, not "
            "FastAPI request parameter parsing or validation. This overview documents security "
            "schemes and their generated OpenAPI representation, with no HTTP validation case."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/security/index.md",
                "start_line": 59,
                "end_line": 106,
                "role": "OpenAPI security schemes and FastAPI security utilities",
            }
        ],
    },
    "tutorial/security/oauth2-jwt.md": {
        "heading": "OAuth2 with Password (and hashing), Bearer with JWT tokens { #oauth2-with-password-and-hashing-bearer-with-jwt-tokens }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "openapi-docs",
            "public-api-errors",
            "request-validation",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "openapi.document",
            "openapi.security",
            "error.class",
            "error.public_attributes",
        ],
        "rationale": (
            "The `settings` match refers to pwdlib algorithm settings, not FastAPI settings or "
            "middleware. This page extends the OAuth2/JWT flow, uses FastAPI HTTP errors, and "
            "shows the authorized docs UI; the dependency/security and OpenAPI contracts remain."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/security/oauth2-jwt.md",
                "start_line": 97,
                "end_line": 123,
                "role": "pwdlib settings and password verification example",
            },
            {
                "path": "docs/en/docs/tutorial/security/oauth2-jwt.md",
                "start_line": 131,
                "end_line": 177,
                "role": "JWT token and FastAPI dependency/error flow",
            },
            {
                "path": "docs/en/docs/tutorial/security/oauth2-jwt.md",
                "start_line": 201,
                "end_line": 230,
                "role": "generated docs authorization workflow and response",
            },
        ],
    },
    "tutorial/server-sent-events.md": {
        "heading": "Server-Sent Events (SSE) { #server-sent-events-sse }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "python-data-encoding",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "validation.error_class",
        ],
        "rationale": (
            "The page covers FastAPI SSE encoding/response behavior and explicitly reads the "
            "Last-Event-ID header. Validation here is per-stream response-item validation, not "
            "request-body/schema validation; response cookies/background-task selectors do not "
            "apply. FastAPI performs item encoding while Starlette supplies StreamingResponse."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/server-sent-events.md",
                "start_line": 36,
                "end_line": 118,
                "role": "SSE response, encoding, header input, and periodic ping contract",
            },
            {
                "path": "fastapi/sse.py",
                "start_line": 20,
                "end_line": 35,
                "role": "FastAPI EventSourceResponse marker over StreamingResponse",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 492,
                "end_line": 530,
                "role": "FastAPI stream-item validation and SSE item encoding",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/responses.py",
                "start_line": 212,
                "end_line": 229,
                "role": "selected Starlette StreamingResponse transport",
            }
        ],
        "contract_gate": (
            "Current FEATURES has http.body.bytes but no ordered, timestamped stream-event "
            "selector. Add a reviewed http.body.events observation to distinguish SSE event "
            "chunks and FastAPI's periodic keepalive timing before claiming streaming parity."
        ),
    },
    "tutorial/sql-databases.md": {
        "heading": "SQL (Relational) Databases { #sql-relational-databases }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "middleware-integrations",
            "openapi-docs",
            "public-api-errors",
            "request-validation",
            "response-serialization",
            "websocket-lifecycle",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "dependency.call_order",
            "dependency.cleanup_order",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
            "openapi.document",
            "openapi.paths",
            "response.background_effects",
            "lifecycle.event_order",
            "process.stdout",
            "error.class",
            "error.public_attributes",
        ],
        "rationale": (
            "The page demonstrates SQLModel through FastAPI dependencies, request/response "
            "models, a startup event, and the fastapi dev console command. The lifecycle family "
            "is selected only for startup ordering: this tutorial has no WebSocket, shutdown, or "
            "cleanup case. Remove WebSocket selectors, lifecycle.cleanup_effects, cookies, and "
            "process stderr/exit selectors. SQLModel/DB internals remain outside FastAPI ownership."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/sql-databases.md",
                "start_line": 92,
                "end_line": 162,
                "role": "session dependency, startup, request/response models, docs, and CLI output",
            },
            {
                "path": "docs/en/docs/tutorial/sql-databases.md",
                "start_line": 281,
                "end_line": 309,
                "role": "FastAPI response-model validation and serialization",
            },
        ],
    },
    "tutorial/static-files.md": {
        "heading": "Static Files { #static-files }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "middleware-integrations",
            "openapi-docs",
            "public-api-errors",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "openapi.document",
            "openapi.paths",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "Mounting and exclusion from the parent OpenAPI/docs are documented, and the page "
            "explicitly says FastAPI's StaticFiles is Starlette's direct re-export. The path() "
            "match is a filesystem/path word, not request validation. Static file serving and "
            "conditional response details stay Starlette-owned."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/static-files.md",
                "start_line": 13,
                "end_line": 48,
                "role": "mounting, OpenAPI boundary, and direct-Starlette StaticFiles note",
            },
            {
                "path": "fastapi/staticfiles.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette StaticFiles re-export",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/staticfiles.py",
                "start_line": 39,
                "end_line": 50,
                "role": "selected Starlette 1.6.0 StaticFiles implementation",
            }
        ],
    },
    "tutorial/stream-json-lines.md": {
        "heading": "Stream JSON Lines { #stream-json-lines }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "python-data-encoding",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "openapi.document",
            "openapi.paths",
            "validation.error_class",
        ],
        "rationale": (
            "The tutorial validates, documents, filters, and serializes streamed return items, "
            "so response-serialization is required. request-validation is a false positive: the "
            "validation at lines 81–89 is on response items, not incoming requests."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/stream-json-lines.md",
                "start_line": 75,
                "end_line": 107,
                "role": "yielded JSONL items, response validation/documentation/serialization, and encoder fallback",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 492,
                "end_line": 518,
                "role": "shared stream-item response validation and serialization",
            },
        ],
        "contract_gate": (
            "Current FEATURES has http.body.bytes but no selector for ordered stream chunks. "
            "Add a reviewed http.body.events observation before claiming JSONL item-boundary or "
            "streaming parity."
        ),
    },
    "tutorial/testing.md": {
        "heading": "Testing { #testing }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "public-api-errors",
            "request-validation",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "validation.error_class",
            "validation.error_details",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": (
            "The tutorial's FastAPI-specific surface is its TestClient import convenience plus "
            "the FastAPI app/routes being exercised. TestClient request mechanics are explicitly "
            "Starlette/HTTPX-owned; jsonable_encoder is a cross-reference rather than an encoder "
            "case."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/testing.md",
                "start_line": 1,
                "end_line": 49,
                "role": "TestClient usage and explicit Starlette import identity note",
            },
            {
                "path": "docs/en/docs/tutorial/testing.md",
                "start_line": 100,
                "end_line": 151,
                "role": "FastAPI route/error tests and generic HTTPX request-input guidance",
            },
            {
                "path": "fastapi/testclient.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette TestClient re-export",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/testclient.py",
                "start_line": 377,
                "end_line": 398,
                "role": "selected Starlette 1.6.0 TestClient implementation",
            }
        ],
    },
}

DOC_EXCLUSION_OVERRIDES = {
    "tutorial/debugging.md": (
        "Editor/Python debugger and Uvicorn launch guidance; the linked FastAPI root-route "
        "example is incidental and the page specifies no independent FastAPI runtime behavior."
    ),
}
