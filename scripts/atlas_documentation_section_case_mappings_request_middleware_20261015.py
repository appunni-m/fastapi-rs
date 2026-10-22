"""Reviewed partial mappings for pending request, middleware, and type docs.

This sidecar records input coverage and source evidence only. It contains no
expected outputs or parity-result claims. Generic ASGI behavior belongs to
Starlette 1.6.0 / Starlette-RS; FastAPI 0.157.0 owns framework integration.
"""

FASTAPI_PIN = {
    "version": "0.157.0",
    "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
}
STARLETTE_PIN = {
    "version": "1.6.0",
    "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}
STARLETTE_RS_PIN = {
    "commit": "b4c8a65c85e1b0d251ca05874412811eaa3ac7b8",
    "role": "sole generic Starlette behavior owner",
}

_HTTP = ["http.status", "http.headers.ordered", "http.body.bytes"]


def _workflow(
    heading,
    start,
    end,
    recipe,
    cases,
    actions,
    selectors,
    note,
    rationale,
):
    row = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        row["action_ids"] = actions
    return row


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_CORS = "tests/fixtures/input-recipes/parity/cors-tutorial-independent.yaml"
_MIDDLEWARE = "tests/fixtures/input-recipes/parity/middleware.yaml"
_MIDDLEWARE_ORDER = "tests/fixtures/input-recipes/parity/middleware-execution-order-wave.yaml"
_STATIC = "tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml"
_STATIC_BOUNDARY = "tests/fixtures/input-recipes/parity/docs-static-files-mount-boundary.yaml"
_OPENAPI_SCHEMA = "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml"
_TYPES_FRONTEND = "tests/fixtures/input-recipes/parity/docs-types-frontend.yaml"
_REFERENCE_HTTP = "tests/fixtures/input-recipes/parity/docs-reference-http.yaml"
_REFERENCE_ASGI = "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml"
DOC_SECTION_CASE_MAPPINGS_REQUEST_MIDDLEWARE_20261015 = {
    # CORS tutorial: concrete explicit-origin requests only.
    ("tutorial/cors.md", "cors-cross-origin-resource-sharing"): _excluded(
        "CORS (Cross-Origin Resource Sharing) { #cors-cross-origin-resource-sharing }",
        1,
        89,
        (
            "The page-level H1 spans the tutorial's child sections. Its broad browser and CORS "
            "summary is reviewed through the narrower child sections below, which sample direct "
            "ASGI responses without exercising browser policy enforcement."
        ),
        (
            "The pinned page-level section is "
            "`../fastapi/docs/en/docs/tutorial/cors.md:1-89`. The CORS recipe "
            "records HTTP responses for literal Origin headers; it has no browser runtime or "
            "JavaScript frontend."
        ),
    ),
    ("tutorial/cors.md", "origin"): _excluded(
        "Origin { #origin }",
        5,
        16,
        (
            "The section defines origin as a protocol/domain/port tuple and lists examples, "
            "while the available requests exercise only their literal Origin header values. "
            "They do not vary each tuple component independently or establish browser origin "
            "comparison rules."
        ),
        (
            "The pinned prose is at "
            "`../fastapi/docs/en/docs/tutorial/cors.md:5-16`. The independent "
            "CORS workload sends literal origins in "
            "`tests/fixtures/workloads/cors_tutorial_independent.py:7-13`; its "
            "selected responses are mapped in the CORS middleware and request subsections below."
        ),
    ),
    ("tutorial/cors.md", "wildcards"): _excluded(
        "Wildcards { #wildcards }",
        27,
        34,
        (
            "The independent CORS workload configures two explicit origins and does not send a "
            "wildcard-origin configuration. It therefore cannot support wildcard or wildcard "
            "with-credentials claims."
        ),
        (
            "FastAPI 0.157.0 `fastapi/middleware/cors.py:1` directly re-exports Starlette's "
            "middleware. The pinned generic source contains separate wildcard and credential "
            "branches at `starlette/middleware/cors.py:35-63,166-174`; none of the selected "
            "input actions configures a wildcard."
        ),
    ),
    ("tutorial/cors.md", "steps"): _excluded(
        "Steps { #steps }",
        17,
        26,
        (
            "This explanation describes browser-generated OPTIONS traffic and browser permission "
            "to send a later cross-origin request. The inputs directly provide ASGI requests and "
            "do not exercise browser scheduling or enforcement."
        ),
        (
            "The pinned browser sequence is `../fastapi/docs/en/docs/tutorial/cors.md:17-26`. The "
            "input workflow directly constructs preflight requests; it does not contain browser "
            "automation. The FastAPI export is a direct Starlette alias "
            "(`fastapi/middleware/cors.py:1`)."
        ),
    ),
    ("tutorial/cors.md", "use-corsmiddleware"): _workflow(
        "Use `CORSMiddleware` { #use-corsmiddleware }",
        35,
        78,
        _CORS,
        [
            "fastapi.docs.cors-tutorial.allowed-preflight",
            "fastapi.docs.cors-tutorial.disallowed-preflight-method",
            "fastapi.docs.cors-tutorial.allowed-simple-request",
            "fastapi.docs.cors-tutorial.unlisted-simple-request",
        ],
        None,
        _HTTP,
        (
            "The four actions configure explicit origins, `allow_credentials=True`, GET/PATCH "
            "methods, and two allowed request headers, then select the HTTP status, ordered "
            "headers, and body for two preflights and two simple GET requests. This samples the "
            "configured cases only; it does not cover wildcard modes, regex origins, exposed "
            "headers, max-age variation, browser enforcement, or credential-bearing cookie or "
            "authorization requests."
        ),
        (
            "The pinned tutorial configures `CORSMiddleware` and lists its options at "
            "`../fastapi/docs/en/docs/tutorial/cors.md:35-78`, with the example at "
            "`../fastapi/docs_src/cors/tutorial001_py310.py:1-24`. FastAPI directly re-exports the "
            "class (`fastapi/middleware/cors.py:1`); Starlette 1.6.0 owns CORS "
            "configuration and generic dispatch (`starlette/middleware/cors.py:15-76`)."
        ),
    ),
    ("tutorial/cors.md", "more-info"): _excluded(
        "More info { #more-info }",
        79,
        89,
        (
            "This section links to Mozilla and Starlette CORS documentation and adds no separate "
            "FastAPI route or input behavior."
        ),
        (
            "The pinned source span is `../fastapi/docs/en/docs/tutorial/cors.md:79-89`. Its only "
            "behavioral statement is that FastAPI provides Starlette middleware as a convenience "
            "(:85-87), already source-backed in the middleware row above; the external standards "
            "and documentation links are not FastAPI runtime behavior."
        ),
    ),
    # Middleware tutorial: the input workflow probes decorator wiring and stacking.
    ("tutorial/middleware.md", "middleware"): _excluded(
        "Middleware { #middleware }",
        1,
        95,
        (
            "The page-level H1 spans the tutorial's child sections, whose sampled decorator and "
            "two-layer trace behavior is reviewed separately. The H1 adds no distinct workflow."
        ),
        (
            "Pinned FastAPI 0.157.0 `../fastapi/docs/en/docs/tutorial/middleware.md:1-95` is the "
            "page-level section. The decorator and execution-order child headings have their own "
            "reviewed mappings below."
        ),
    ),
    ("tutorial/middleware.md", "create-a-middleware"): _workflow(
        "Create a middleware { #create-a-middleware }",
        22,
        67,
        _MIDDLEWARE,
        [
            "fastapi.middleware.decorator-openapi",
            "fastapi.middleware.decorator-body-replay",
        ],
        None,
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "docs.response.headers",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The GET action selects response status/headers and two OpenAPI subtrees while the "
            "decorator middleware is installed. The POST action selects status/body after the "
            "middleware reads the request body before `call_next`. These actions do not observe "
            "middleware-added headers on the POST, yield-dependency teardown, background-task "
            "timing, or every `Request` property."
        ),
        (
            "The pinned tutorial is "
            "`../fastapi/docs/en/docs/tutorial/middleware.md:22-50`. FastAPI "
            "registers the decorator through `BaseHTTPMiddleware` at "
            "`fastapi/applications.py:4725-4769`; Starlette 1.6.0 supplies the generic "
            "HTTP middleware wrapper at `starlette/middleware/base.py:96-120`."
        ),
    ),
    ("tutorial/middleware.md", "before-and-after-the-response"): _workflow(
        "Before and after the `response` { #before-and-after-the-response }",
        52,
        67,
        _MIDDLEWARE,
        [
            "fastapi.middleware.decorator-openapi",
            "fastapi.middleware.decorator-body-replay",
        ],
        None,
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "docs.response.headers",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected GET observes the response headers after decorator middleware adds its "
            "marker, plus selected OpenAPI paths. The POST observes the response after the "
            "middleware consumes the request body and the endpoint reads it again. It does not "
            "claim elapsed-time measurement or the exact tutorial header value."
        ),
        (
            "The pinned behavior description and example are at "
            "`../fastapi/docs/en/docs/tutorial/middleware.md:52-66` and "
            "`../fastapi/docs_src/middleware/tutorial001_py310.py:8-14`. FastAPI's decorator "
            "registration is `fastapi/applications.py:4725-4769`; generic middleware "
            "dispatch is Starlette-owned (`starlette/middleware/base.py:96-120`)."
        ),
    ),
    ("tutorial/middleware.md", "multiple-middleware-execution-order"): _workflow(
        "Multiple middleware execution order { #multiple-middleware-execution-order }",
        68,
        90,
        _MIDDLEWARE_ORDER,
        ["fastapi.docs.middleware.request-and-response-order"],
        ["enter-stacked-middleware", "read-middleware-event-trace"],
        [*_HTTP, "asgi.send.message_types"],
        (
            "The first action traverses two independently written middleware wrappers and "
            "selects ASGI send message types plus the HTTP response. The second action returns "
            "the route's request/response event trace in the HTTP body. This covers the sampled "
            "two-middleware stack only; it does not measure arbitrary middleware combinations "
            "or dependency/background-task timing."
        ),
        (
            "The pinned order explanation is "
            "`../fastapi/docs/en/docs/tutorial/middleware.md:68-90`. "
            "Starlette inserts added middleware at the start of its user list and reverses the "
            "list while wrapping (`starlette/applications.py:63-83,104-108`); FastAPI "
            "middleware registration uses that generic stack through "
            "`fastapi/applications.py:4725-4769`."
        ),
    ),
    ("tutorial/middleware.md", "other-middlewares"): _excluded(
        "Other middlewares { #other-middlewares }",
        91,
        95,
        (
            "This section points to the advanced middleware and CORS pages without adding an "
            "independent behavior claim."
        ),
        (
            "The pinned link-only span is `../fastapi/docs/en/docs/tutorial/middleware.md:91-95`. "
            "CORS behavior is mapped to its own input cases above; a navigation link does not "
            "warrant another workflow."
        ),
    ),
    # Static files and frontend mounting.
    ("tutorial/static-files.md", "static-files"): _workflow(
        "Static Files { #static-files }",
        1,
        48,
        _STATIC,
        ["fastapi.middleware-proxy.static-files"],
        ["request-mounted-file", "request-missing-mounted-file"],
        ["http.status", "http.body.bytes"],
        (
            "A directory-backed StaticFiles mount serves one created file and selects the "
            "status/body for that file and a missing path. This samples one mount and does not "
            "cover the full StaticFiles configuration surface or the page's `app.frontend()` "
            "route and fallback behavior."
        ),
        (
            "The pinned page-level section is "
            "`../fastapi/docs/en/docs/tutorial/static-files.md:1-48`. FastAPI "
            "re-exports Starlette StaticFiles (`fastapi/staticfiles.py:1`); Starlette 1.6.0 "
            "owns directory lookup and static response construction "
            "(`starlette/staticfiles.py:39-56,87-152`)."
        ),
    ),
    ("tutorial/static-files.md", "use-staticfiles"): _workflow(
        "Use `StaticFiles` { #use-staticfiles }",
        13,
        35,
        _STATIC,
        ["fastapi.middleware-proxy.static-files"],
        ["request-mounted-file", "request-missing-mounted-file", "request-static-openapi"],
        [
            "http.status",
            "http.body.bytes",
            "docs.response.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The workload constructs `StaticFiles(directory=<temporary directory>)`, mounts it "
            "at `/assets` with name `assets`, then selects a present-file response, a missing "
            "file status, construction outcome, and the parent's OpenAPI projection. It does not "
            "exercise package directories, HTML mode, symlinks, response headers, range requests, "
            "or URL reversal by mount name."
        ),
        (
            "The pinned tutorial and import note are "
            "`../fastapi/docs/en/docs/tutorial/static-files.md:13-35`. "
            "FastAPI directly re-exports `StaticFiles` (`fastapi/staticfiles.py:1`); "
            "Starlette 1.6.0 owns its constructor and dispatch "
            "(`starlette/staticfiles.py:39-56,87-152`)."
        ),
    ),
    ("tutorial/static-files.md", "what-is-mounting"): _workflow(
        'What is "Mounting" { #what-is-mounting }',
        28,
        35,
        _STATIC_BOUNDARY,
        ["fastapi.docs.static-files.mount-parent-openapi-docs-boundary"],
        ["parent-openapi", "parent-docs-ui"],
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The workload mounts a minimal independent ASGI child at `/static`, then selects the "
            "parent `/openapi.json` path projection and parent `/docs` response. It does not "
            "send a request to the child, compare a child's own OpenAPI/docs, or establish all "
            "mounted-app isolation properties."
        ),
        (
            "The pinned description is `../fastapi/docs/en/docs/tutorial/static-files.md:28-35`. "
            "The input mounts a child using Starlette's inherited application method "
            "(`starlette/applications.py:98-100`); FastAPI's router/OpenAPI generation "
            "remains the parent application boundary."
        ),
    ),
    ("tutorial/static-files.md", "details"): _workflow(
        "Details { #details }",
        36,
        45,
        _STATIC,
        ["fastapi.middleware-proxy.static-files"],
        ["request-mounted-file", "request-missing-mounted-file"],
        ["http.status", "http.body.bytes"],
        (
            "The two selected file actions exercise a directory-backed mount at `/assets` for "
            "one existing and one missing child path. The response selectors are status and "
            "body bytes. The mount name is configured but no URL reversal is observed."
        ),
        (
            "The pinned parameter explanation is "
            "`../fastapi/docs/en/docs/tutorial/static-files.md:36-45`. "
            "The independent workload uses a temporary directory and mounts `StaticFiles` at "
            "`/assets` in `tests/fixtures/workloads/middleware_proxy_source_review.py:87-101`; "
            "generic file resolution and status behavior is Starlette-owned "
            "(`starlette/staticfiles.py:97-152`)."
        ),
    ),
    # Extra data types: one request/response and schema projection, with Pydantic as owner.
    ("tutorial/extra-data-types.md", "extra-data-types"): _excluded(
        "Extra Data Types { #extra-data-types }",
        1,
        62,
        (
            "The page-level H1 spans several data-type examples and makes broad claims about "
            "conversion, validation, editor support, and annotation behavior. The independent "
            "typed request samples only the narrower `Other data types` and `Example` sections."
        ),
        (
            "The pinned page-level section is "
            "`../fastapi/docs/en/docs/tutorial/extra-data-types.md:1-62`; the "
            "specific UUID/datetime/timedelta/time example is mapped below. FastAPI's request and "
            "response validation pipeline delegates type conversion and serialization to its "
            "Pydantic field (`fastapi/utils.py:58-77`, `fastapi/routing.py:321-361`)."
        ),
    ),
    ("tutorial/extra-data-types.md", "other-data-types"): _workflow(
        "Other data types { #other-data-types }",
        20,
        53,
        _OPENAPI_SCHEMA,
        ["fastapi.docs.documentation-wave.openapi-schema.extra-data-types"],
        ["dispatch", "openapi"],
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The request and OpenAPI actions sample `UUID`, `datetime`, `timedelta`, and `time` "
            "in one path/body example. The OpenAPI action selects the path-parameter and "
            "`TimeWindow` schema projections; the request action selects status, headers, and "
            "response body. It does not sample `date`, `frozenset`, `bytes`, `Decimal`, alternate "
            "encodings, invalid input, or every Pydantic type."
        ),
        (
            "The pinned list is `../fastapi/docs/en/docs/tutorial/extra-data-types.md:20-53`; its "
            "example declarations are "
            "`../fastapi/docs_src/extra_data_types/tutorial001_an_py310.py:1-28`. "
            "FastAPI analyzes endpoint fields and forms request-body arguments "
            "(`fastapi/dependencies/utils.py:423-606,1162-1234`) and validates/serializes "
            "through Pydantic-backed fields (`fastapi/routing.py:321-361`)."
        ),
    ),
    ("tutorial/extra-data-types.md", "example"): _workflow(
        "Example { #example }",
        54,
        62,
        _OPENAPI_SCHEMA,
        ["fastapi.docs.documentation-wave.openapi-schema.extra-data-types"],
        ["dispatch", "openapi"],
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The workload sends one valid UUID path and a JSON body with datetime, timedelta, "
            "and time-shaped fields, then selects response and OpenAPI projections. It does not "
            "perform the date arithmetic described immediately after the example or claim invalid "
            "input behavior."
        ),
        (
            "The pinned example and source include are at "
            "`../fastapi/docs/en/docs/tutorial/extra-data-types.md:54-62`; source code is "
            "`../fastapi/docs_src/extra_data_types/tutorial001_an_py310.py:1-28`. The independent "
            "workload declares these types in "
            "`tests/fixtures/workloads/docs_openapi_schema.py:1-13,51-56`."
        ),
    ),
    # Python typing reference: only a successful, typed FastAPI path/query route is sampled.
    ("python-types.md", "python-types-intro"): _excluded(
        "Python Types Intro { #python-types-intro }",
        1,
        348,
        (
            "The introduction describes Python annotations and their editor/tooling benefits. "
            "The available FastAPI input workflow does not measure editor tooling or general "
            "Python typing behavior."
        ),
        (
            "The pinned page-level section is `../fastapi/docs/en/docs/python-types.md:1-348`. The "
            "independent route and its successful request are source-backed by the narrower "
            "FastAPI sections below and `tests/fixtures/workloads/docs_types_frontend.py:12-18`."
        ),
    ),
    ("python-types.md", "motivation"): _excluded(
        "Motivation { #motivation }",
        21,
        104,
        (
            "This standalone Python function and editor-support explanation is not an HTTP or "
            "FastAPI behavior sampled by the selected route."
        ),
        (
            "The pinned example is `../fastapi/docs/en/docs/python-types.md:21-104` and "
            "`../fastapi/docs_src/python_types/tutorial001_py310.py:1-2`; the existing independent "
            "workload does not call that function or inspect editor completion."
        ),
    ),
    ("python-types.md", "edit-it"): _excluded(
        "Edit it { #edit-it }",
        41,
        60,
        (
            "This section is about interactive editor autocomplete. No parity input can observe "
            "that editor behavior."
        ),
        (
            "The pinned editor instructions and screenshots are at "
            "`../fastapi/docs/en/docs/python-types.md:41-60`; the selected HTTP/OpenAPI actions do "
            "not start an editor or inspect its suggestions."
        ),
    ),
    ("python-types.md", "add-types"): _excluded(
        "Add types { #add-types }",
        61,
        104,
        (
            "The section contrasts Python annotations with defaults and illustrates editor "
            "completion, but has no independent FastAPI request behavior."
        ),
        (
            "The pinned source is `../fastapi/docs/en/docs/python-types.md:61-104`, including "
            "standalone examples and editor images; the independent route only observes FastAPI "
            "request parameter handling, mapped in the child sections below."
        ),
    ),
    ("python-types.md", "more-motivation"): _excluded(
        "More motivation { #more-motivation }",
        105,
        118,
        (
            "The examples teach editor-side type checking in standalone Python; the selected "
            "workflow does not exercise a Python editor or type checker."
        ),
        (
            "The pinned examples are `../fastapi/docs/en/docs/python-types.md:105-118` and "
            "`../fastapi/docs_src/python_types/tutorial003_py310.py:1` / "
            "`../fastapi/docs_src/python_types/tutorial004_py310.py:1-2`; "
            "no matching editor input exists."
        ),
    ),
    ("python-types.md", "declaring-types"): _excluded(
        "Declaring types { #declaring-types }",
        119,
        269,
        (
            "This parent section contains several distinct Python-type topics. The sampled FastAPI "
            "parameter behavior is reviewed only in the child headings with "
            "matching feature evidence."
        ),
        (
            "The pinned parent span is "
            "`../fastapi/docs/en/docs/python-types.md:119-269`, including "
            "Simple types through Classes as types. Pydantic models begin at the next sibling "
            "heading. The concrete parameter workflow is attached to "
            "its narrower Type Hints child sections."
        ),
    ),
    ("python-types.md", "typing-module"): _excluded(
        "`typing` module { #typing-module }",
        138,
        149,
        (
            "The section is a standalone Python `Any` annotation example and has no matching "
            "FastAPI input behavior."
        ),
        (
            "The pinned example is `../fastapi/docs/en/docs/python-types.md:138-149`; no selected "
            "workload uses `Any` as a request field or observes its annotation semantics."
        ),
    ),
    ("python-types.md", "generic-types"): _excluded(
        "Generic types { #generic-types }",
        150,
        249,
        (
            "The list/tuple/set/dict/union/optional tutorial covers generic Python shapes not "
            "established by the selected scalar path/query request."
        ),
        (
            "The pinned section is `../fastapi/docs/en/docs/python-types.md:150-249`. The existing "
            "scalar route workload does not declare these shapes."
        ),
    ),
    ("python-types.md", "classes-as-types"): _excluded(
        "Classes as types { #classes-as-types }",
        250,
        269,
        (
            "The section teaches class-instance typing and editor support; no input workflow "
            "uses the documented `Person` class."
        ),
        (
            "The pinned example is `../fastapi/docs/en/docs/python-types.md:250-269` and "
            "`../fastapi/docs_src/python_types/tutorial010_py310.py:1-6`; the mapped workload has "
            "no such class value."
        ),
    ),
    ("python-types.md", "pydantic-models"): _excluded(
        "Pydantic models { #pydantic-models }",
        270,
        295,
        (
            "The page explains Pydantic model validation and editor support, but no route from "
            "the selected input workflow uses the examples in this section."
        ),
        (
            "The pinned section is "
            "`../fastapi/docs/en/docs/python-types.md:270-295`. Pydantic owns "
            "model validation/serialization; no model behavior is claimed by the scalar route "
            "recipe linked in this sidecar."
        ),
    ),
    ("python-types.md", "type-hints-with-metadata-annotations"): _workflow(
        "Type Hints with Metadata Annotations { #type-hints-with-metadata-annotations }",
        296,
        321,
        _TYPES_FRONTEND,
        ["fastapi.docs.reference-wave.types.typed-path-and-query-inputs"],
        ["dispatch", "openapi"],
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The independent route uses `Annotated[int, Path(gt=0)]` and "
            "`Annotated[float, Query(gt=0)]`; the actions select one successful request and the "
            "route's parameter projection. The workload does not test general Python "
            "`Annotated` behavior, editor support, or invalid values."
        ),
        (
            "The pinned metadata section is `../fastapi/docs/en/docs/python-types.md:296-321`. "
            "FastAPI extracts FastAPI `FieldInfo` metadata from `Annotated` in "
            "`fastapi/dependencies/utils.py:441-485` and creates the analyzed parameter "
            "field at `:507-535`."
        ),
    ),
    ("python-types.md", "type-hints-in-fastapi"): _workflow(
        "Type hints in **FastAPI** { #type-hints-in-fastapi }",
        322,
        348,
        _TYPES_FRONTEND,
        ["fastapi.docs.reference-wave.types.typed-path-and-query-inputs"],
        ["dispatch", "openapi"],
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected workflow samples successful conversion of one integer path value, one "
            "float query value, and one bool query/default, plus their OpenAPI parameter "
            "projection. It does not cover invalid-input errors, bodies, dependencies, headers, "
            "editor/type-checker support, or every parameter source."
        ),
        (
            "The pinned overview is `../fastapi/docs/en/docs/python-types.md:322-348`. FastAPI "
            "analyzes parameter annotations and constructs request fields in "
            "`fastapi/dependencies/utils.py:423-606`, then validates request values "
            "through those fields at `fastapi/dependencies/utils.py:822-831`; OpenAPI "
            "generation consumes the analyzed route fields."
        ),
    ),
    # Request/Response/UploadFile reference pages.
    ("reference/request.md", "@line:1"): _workflow(
        "`Request` class",
        1,
        19,
        _REFERENCE_HTTP,
        ["fastapi.docs.reference-wave.http.request-injection"],
        ["dispatch"],
        _HTTP,
        (
            "The POST action injects `Request`, reads JSON directly, and selects a response "
            "whose body includes the method, URL path, one query value, and parsed payload. It "
            "does not validate that body through a FastAPI model or exercise other Request "
            "members. The workload imports the public name but does not compare class identity."
        ),
        (
            "The pinned page is `../fastapi/docs/en/docs/reference/request.md:1-19`. "
            "FastAPI exposes Request as a direct Starlette re-export "
            "(`fastapi/requests.py:1-2`, `fastapi/__init__.py:21`), recognizes "
            "and injects it through dependency analysis "
            "(`fastapi/dependencies/utils.py:392-397,797-800`). "
            "The workload reads and returns request data at "
            "`tests/fixtures/workloads/docs_reference_request.py:70-78`; generic Request "
            "semantics belong to Starlette 1.6.0."
        ),
    ),
    ("reference/uploadfile.md", "@line:1"): _workflow(
        "`UploadFile` class",
        1,
        22,
        _REFERENCE_ASGI,
        ["fastapi.docs.reference-wave.asgi.uploadfile-multipart"],
        ["dispatch", "openapi"],
        [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "docs.response.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
        (
            "The multipart request injects `UploadFile`, reads its content, and returns selected "
            "filename/content-type/size/text fields; the OpenAPI action selects the multipart "
            "request schema. The imports in the independently authored workload prove the public "
            "name is usable but do not compare its class identity or exercise every member."
        ),
        (
            "The pinned page is `../fastapi/docs/en/docs/reference/uploadfile.md:1-22`. FastAPI "
            "exports its UploadFile subclass from the root (`fastapi/__init__.py:9`) and "
            "declares its fields at `fastapi/datastructures.py:21-65`; FastAPI recognizes "
            "UploadFile annotations as file fields at "
            "`fastapi/dependencies/utils.py:541-545,1162-1234`. "
            "The workload reads and returns upload metadata at "
            "`tests/fixtures/workloads/docs_reference_asgi.py:49-57`; multipart parsing and "
            "generic upload behavior belong to Starlette 1.6.0."
        ),
    ),
}
