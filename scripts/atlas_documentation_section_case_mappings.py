"""Reviewed section-to-workflow links and behavior-based exclusions."""

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
    ("tutorial/static-files.md", "more-info"): {
        "status": "excluded",
        "heading": "More info { #more-info }",
        "start_line": 46,
        "end_line": 48,
        "exclusion_reason": (
            "This section only links to Starlette's StaticFiles documentation and defines no "
            "additional FastAPI runtime or API behavior."
        ),
        "rationale": (
            "The pinned source span is a single link to generic Starlette StaticFiles options. "
            "FastAPI's static-file integration is described in the preceding sections; this "
            "link adds no independently observable FastAPI contract."
        ),
    },
    ("tutorial/path-params.md", "recap"): {
        "status": "excluded",
        "heading": "Recap { #recap }",
        "start_line": 240,
        "end_line": 251,
        "exclusion_reason": (
            "This section summarizes earlier path-parameter claims and adds no independent "
            "FastAPI request or API behavior."
        ),
        "rationale": (
            "The pinned span recaps editor support, parsing, validation, and API documentation; "
            "its unbounded performance comparison defines no separately testable behavior."
        ),
    },
    ("tutorial/query-params-str-validations.md", "understand-that-code"): {
        "status": "excluded",
        "heading": "Understand that Code { #understand-that-code }",
        "start_line": 399,
        "end_line": 428,
        "exclusion_reason": (
            "This optional explanation repeats the preceding AfterValidator behavior and adds "
            "no separate FastAPI contract."
        ),
        "rationale": (
            "The pinned text identifies AfterValidator inside Annotated as the key point, then "
            "introduces optional details whose child sections are reviewed independently."
        ),
    },
    ("tutorial/query-params-str-validations.md", "string-with-value-startswith"): {
        "status": "excluded",
        "heading": "String with `value.startswith()` { #string-with-value-startswith }",
        "start_line": 407,
        "end_line": 412,
        "exclusion_reason": (
            "This section explains standard Python string-prefix behavior inside an application "
            "validator, not an independent FastAPI behavior."
        ),
        "rationale": (
            "The pinned code uses str.startswith(tuple); FastAPI's AfterValidator integration "
            "is covered separately, while the builtin string operation belongs to Python."
        ),
    },
    ("tutorial/query-params-str-validations.md", "recap"): {
        "status": "excluded",
        "heading": "Recap { #recap }",
        "start_line": 429,
        "end_line": 450,
        "exclusion_reason": (
            "This section lists validations and metadata already described in preceding "
            "sections and adds no independent input/output behavior."
        ),
        "rationale": (
            "The pinned span is a recap of alias, metadata, string constraints, and "
            "AfterValidator, followed by a pointer to later chapters."
        ),
    },
    ("tutorial/response-model.md", "response-model-or-return-type"): {
        "status": "excluded",
        "heading": "`response_model` or Return Type { #response-model-or-return-type }",
        "start_line": 125,
        "end_line": 132,
        "exclusion_reason": (
            "This section concerns editor/type-checker diagnostics and repeats the already "
            "shown response_model choice without adding runtime behavior."
        ),
        "rationale": (
            "The pinned span describes tools rejecting different Python model classes; editor "
            "diagnostics are outside the observable FastAPI runtime contract."
        ),
    },
    ("tutorial/response-model.md", "recap"): {
        "status": "excluded",
        "heading": "Recap { #recap }",
        "start_line": 340,
        "end_line": 344,
        "exclusion_reason": (
            "This section restates response filtering and exclude_unset behavior from earlier "
            "sections and introduces no new contract."
        ),
        "rationale": (
            "The pinned span is explicitly a summary of previously described response-model "
            "claims and defines no new request, response, or OpenAPI behavior."
        ),
    },
    ("tutorial/handling-errors.md", "handling-errors"): {
        "status": "excluded",
        "heading": "Handling Errors { #handling-errors }",
        "start_line": 1,
        "end_line": 244,
        "exclusion_reason": (
            "This page-level heading is an umbrella for the independently reviewed child "
            "sections and adds no distinct FastAPI behavior."
        ),
        "rationale": (
            "The pinned heading spans the whole tutorial; its child sections and the page-level "
            "partial workflows carry the concrete exception contracts."
        ),
    },
    ("tutorial/handling-errors.md", "use-httpexception"): {
        "heading": "Use `HTTPException` { #use-httpexception }",
        "start_line": 22,
        "end_line": 71,
        "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors.yaml",
        "case_ids": [
            "fastapi.docs.handling-errors.http-exception-detail",
            "fastapi.docs.handling-errors.http-exception-status",
        ],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "These actions sample one not-found response and one custom status response. They "
            "do not establish every HTTPException detail type or status code."
        ),
        "rationale": (
            "The exact pinned tutorial page is cited by both input cases, which observe the "
            "public HTTP response produced by FastAPI HTTPException routes."
        ),
    },
    ("tutorial/handling-errors.md", "raise-an-httpexception-in-your-code"): {
        "heading": "Raise an `HTTPException` in your code { #raise-an-httpexception-in-your-code }",
        "start_line": 30,
        "end_line": 43,
        "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors.yaml",
        "case_ids": ["fastapi.docs.handling-errors.http-exception-detail"],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "The input samples a route that raises HTTPException for an absent item; it does "
            "not observe arbitrary utility-function control flow."
        ),
        "rationale": (
            "The linked source page and documentation example describe the same public "
            "not-found response action."
        ),
    },
    ("tutorial/handling-errors.md", "the-resulting-response"): {
        "heading": "The resulting response { #the-resulting-response }",
        "start_line": 44,
        "end_line": 71,
        "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors.yaml",
        "case_ids": [
            "fastapi.docs.handling-errors.success",
            "fastapi.docs.handling-errors.http-exception-detail",
            "fastapi.docs.handling-errors.http-exception-status",
        ],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "These inputs compare one successful response and two HTTPException responses, "
            "including the selected status, headers, and body."
        ),
        "rationale": (
            "The pinned documentation page is directly cited by each case; structured detail "
            "and custom-header behavior remain separately scoped."
        ),
    },
    ("tutorial/handling-errors.md", "add-custom-headers"): {
        "heading": "Add custom headers { #add-custom-headers }",
        "start_line": 72,
        "end_line": 81,
        "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial002-review.yaml",
        "case_ids": ["fastapi.docs-example.handling-errors.tutorial002.forwarded-header"],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "The action samples one custom header on an HTTPException response; it does not "
            "cover all security-header policies."
        ),
        "rationale": (
            "The input cites this pinned page and the included tutorial 002 example, and "
            "observes the full selected HTTP response."
        ),
    },
    ("tutorial/handling-errors.md", "install-custom-exception-handlers"): {
        "heading": "Install custom exception handlers { #install-custom-exception-handlers }",
        "start_line": 82,
        "end_line": 111,
        "recipe_path": "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial003-review.yaml",
        "case_ids": ["fastapi.docs-example.handling-errors.tutorial003.custom-exception"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "This action samples one custom exception handler registration and its JSON body; "
            "generic Request and response rendering remain Starlette-owned."
        ),
        "rationale": (
            "The pinned tutorial page and example are cited by the input, and the action "
            "observes the custom handler's public HTTP response."
        ),
    },
    ("tutorial/handling-errors.md", "override-the-default-exception-handlers"): {
        "heading": "Override the default exception handlers { #override-the-default-exception-handlers }",
        "start_line": 112,
        "end_line": 244,
        "recipe_path": "tests/fixtures/input-recipes/parity/exception-overrides.yaml",
        "case_ids": [
            "fastapi.docs.handling-errors.overridden-validation-error",
            "fastapi.docs.handling-errors.overridden-http-error",
            "fastapi.docs.handling-errors.overrides-openapi",
            "fastapi.docs.handling-errors.override-success",
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
        "scope_note": (
            "These inputs cover selected custom HTTP and validation handlers, an unaffected "
            "route, and two OpenAPI pointers; the RequestValidationError body example is "
            "linked separately."
        ),
        "rationale": (
            "Each case cites this pinned tutorial page and observes its declared route or "
            "OpenAPI projection without claiming complete coverage of every child example."
        ),
    },
    ("tutorial/handling-errors.md", "override-request-validation-exceptions"): {
        "heading": "Override request validation exceptions { #override-request-validation-exceptions }",
        "start_line": 120,
        "end_line": 155,
        "recipe_path": "tests/fixtures/input-recipes/parity/exception-overrides.yaml",
        "case_ids": ["fastapi.docs.handling-errors.overridden-validation-error"],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "This case covers a custom replacement response for one invalid integer path "
            "parameter, not every validation error shape."
        ),
        "rationale": (
            "The pinned page, tutorial 004 example, and upstream test are cited by the "
            "input; the selected action observes status, headers, and body."
        ),
    },
    ("tutorial/handling-errors.md", "override-the-httpexception-error-handler"): {
        "heading": "Override the `HTTPException` error handler { #override-the-httpexception-error-handler }",
        "start_line": 156,
        "end_line": 179,
        "recipe_path": "tests/fixtures/input-recipes/parity/exception-overrides.yaml",
        "case_ids": ["fastapi.docs.handling-errors.overridden-http-error"],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "This case registers a Starlette HTTPException-base handler and raises one FastAPI "
            "HTTPException; generic dispatch remains Starlette-owned."
        ),
        "rationale": (
            "The case cites the exact pinned tutorial page and example and compares the "
            "resulting public HTTP response."
        ),
    },
    ("tutorial/handling-errors.md", "use-the-requestvalidationerror-body"): {
        "heading": "Use the `RequestValidationError` body { #use-the-requestvalidationerror-body }",
        "start_line": 180,
        "end_line": 237,
        "recipe_path": "tests/fixtures/input-recipes/parity/request-validation-body.yaml",
        "case_ids": ["fastapi.docs.handling-errors.body-echo.invalid-input"],
        "observation_selectors": ["http.body.bytes", "http.headers.ordered", "http.status"],
        "scope_note": (
            "This action samples one invalid JSON body echoed by a custom handler; its response "
            "keys differ from the exact tutorial example and it does not isolate jsonable_encoder."
        ),
        "rationale": (
            "The input cites this pinned page and tutorial 005 sources, and the selected body "
            "request yields a completed pinned Oracle observation."
        ),
    },
    ("tutorial/handling-errors.md", "fastapis-httpexception-vs-starlettes-httpexception"): {
        "heading": "FastAPI's `HTTPException` vs Starlette's `HTTPException` { #fastapis-httpexception-vs-starlettes-httpexception }",
        "start_line": 218,
        "end_line": 237,
        "recipe_path": "tests/fixtures/input-recipes/parity/public-errors-http-websocket-wave.yaml",
        "case_ids": [
            "fastapi.public-errors.http.fastapi-json-detail-and-header",
            "fastapi.public-errors.http.starlette-base-detail-and-header",
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
            "The cases compare construction and route-level FastAPI versus Starlette exception "
            "handling for JSON detail/header samples; they do not assert Python MRO."
        ),
        "rationale": (
            "Both input cases cite the exact pinned page and their completed Oracle evidence "
            "observes exception construction plus the public HTTP response."
        ),
    },
    ("tutorial/dependencies/index.md", "dependencies"): {
        "status": "excluded",
        "heading": "Dependencies { #dependencies }",
        "start_line": 1,
        "end_line": 250,
        "exclusion_reason": (
            "This page-level heading is an umbrella for independently reviewable dependency "
            "sections and introduces no separate FastAPI behavior."
        ),
        "rationale": (
            "The pinned title spans the full tutorial; the concrete dependency and OpenAPI "
            "claims are handled by its anchored child sections and the page-level partial map."
        ),
    },
    ("tutorial/dependencies/index.md", "what-is-dependency-injection"): {
        "status": "excluded",
        "heading": "What is \"Dependency Injection\" { #what-is-dependency-injection }",
        "start_line": 7,
        "end_line": 21,
        "exclusion_reason": (
            "This section provides a general dependency-injection definition and benefit list "
            "without a FastAPI operation or observable behavior."
        ),
        "rationale": (
            "The pinned span is introductory conceptual prose; dependency declaration and "
            "resolution claims are handled by the following runnable sections."
        ),
    },
    ("tutorial/dependencies/index.md", "first-steps"): {
        "status": "excluded",
        "heading": "First Steps { #first-steps }",
        "start_line": 22,
        "end_line": 116,
        "exclusion_reason": (
            "This parent heading groups the independently reviewed dependency setup and "
            "declaration sections and has no separate contract."
        ),
        "rationale": (
            "The pinned span's runnable claims belong to its anchored child sections; the "
            "page-level mapping remains partial and does not claim this parent is covered."
        ),
    },
    ("tutorial/dependencies/index.md", "fastapi-plug-ins"): {
        "status": "excluded",
        "heading": "**FastAPI** plug-ins { #fastapi-plug-ins }",
        "start_line": 185,
        "end_line": 192,
        "exclusion_reason": (
            "This section is ecosystem extensibility prose without a concrete FastAPI runtime "
            "operation or documented API claim."
        ),
        "rationale": (
            "The pinned text lists generic integration possibilities and provides no route, "
            "dependency, output, error, or schema observation to map."
        ),
    },
    ("tutorial/dependencies/index.md", "fastapi-compatibility"): {
        "status": "excluded",
        "heading": "**FastAPI** compatibility { #fastapi-compatibility }",
        "start_line": 193,
        "end_line": 205,
        "exclusion_reason": (
            "This section lists ecosystem integration categories without specifying a distinct "
            "FastAPI contract."
        ),
        "rationale": (
            "The pinned span is high-level compatibility prose; concrete dependency and "
            "security behavior is mapped independently."
        ),
    },
}
