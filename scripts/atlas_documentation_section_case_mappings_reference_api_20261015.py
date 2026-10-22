"""Reviewed mappings for pending FastAPI API-reference sections.

Originally reviewed against FastAPI 0.141.1 at
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f; that pin is historical provenance.
Active FastAPI claims below were rechecked against 0.157.0 at
386a28af2f87af1a32ac26d88f07b7f58ab2dfb1. Starlette remains pinned to
1.6.0 at 4f250d6b814587e20c5365f0a5f0c4d42bcb929f, and the
Starlette-RS behavior owner at
/private/tmp/fastapi-rs-starlette-rs-b4c8-validation
(b4c8a65c85e1b0d251ca05874412811eaa3ac7b8).
"""

_DOCS_REFERENCE_HTTP = "tests/fixtures/input-recipes/parity/docs-reference-http.yaml"
_DOCS_REFERENCE_OPENAPI = "tests/fixtures/input-recipes/parity/docs-reference-openapi.yaml"
_DOCS_REFERENCE_ASGI = "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml"
_OPENAPI_SCHEMA_FIELDS = "tests/fixtures/input-recipes/parity/openapi-schema-field-inputs.yaml"
_RESPONSE_CLASS_SOURCE_REVIEW = (
    "tests/fixtures/input-recipes/parity/reference-response-class-source-review-20261015.yaml"
)
_ROOT_ALIAS_IDENTITY = "tests/fixtures/input-recipes/parity/root-alias-identity.yaml"


DOC_SECTION_CASE_MAPPINGS_REFERENCE_API_20261015 = {
    ("reference/apirouter.md", "@line:1"): {
        "heading": "`APIRouter` class",
        "start_line": 1,
        "end_line": 25,
        "recipe_path": _DOCS_REFERENCE_HTTP,
        "case_ids": ["fastapi.docs.reference-wave.http.apirouter-prefix"],
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "The selected case registers one GET operation on an APIRouter with prefix `/v2` "
            "and tag `catalogue`; its request and OpenAPI actions observe that route under "
            "`/v2/items/{item_id}`. It does not cover the other listed decorators, frontend, "
            "lifespan callbacks, router options, or all inclusion behavior."
        ),
        "rationale": (
            "FastAPI 0.157.0's APIRouter registers API routes by combining its prefix with the "
            "operation path and carries tags into the generated operation "
            "(`fastapi/routing.py:2996-3057`; "
            "`fastapi/openapi/utils.py:272-278`). The selected independent "
            "input declares prefix `/v2` and tag `catalogue`, then observes the request and "
            "OpenAPI path. Starlette 1.6.0 owns generic HTTP transport; the pinned "
            "Starlette-RS checkout remains the sibling behavior boundary."
        ),
    },
    ("reference/fastapi.md", "@line:1"): {
        "heading": "`FastAPI` class",
        "start_line": 1,
        "end_line": 32,
        "recipe_path": _DOCS_REFERENCE_OPENAPI,
        "case_ids": ["fastapi.docs.reference-wave.openapi.fastapi-application-settings"],
        "observation_selectors": [
            "docs.response.body.bytes",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "The selected case constructs one FastAPI app with a title, summary, version, tags, "
            "and custom docs URLs, then observes its `/openapi.json` response and generated "
            "schema. This samples application construction and OpenAPI output; it does not "
            "claim the full constructor, attribute, or method contract listed on the page."
        ),
        "rationale": (
            "FastAPI 0.157.0 declares FastAPI as the public application class, stores its "
            "constructor metadata, and passes those values to OpenAPI generation "
            "(`fastapi/applications.py:52,68,855-879,1085-1118`). The selected case observes "
            "the configured application's HTTP OpenAPI "
            "response and selected document fields. Starlette 1.6.0 owns the inherited ASGI "
            "application base; the pinned Starlette-RS checkout is the generic behavior owner."
        ),
    },
    ("reference/httpconnection.md", "@line:1"): {
        "heading": "`HTTPConnection` class",
        "start_line": 1,
        "end_line": 11,
        "recipe_path": _DOCS_REFERENCE_ASGI,
        "case_ids": [
            "fastapi.test.test-http-connection-injection.test-value-extracting-by-http",
            "fastapi.test.test-http-connection-injection.test-value-extracting-by-ws",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "websocket.close_code",
            "websocket.event_order",
            "websocket.messages",
        ],
        "scope_note": (
            "The selected HTTP and WebSocket cases inject HTTPConnection into a dependency "
            "and return the shared application-state value. They sample dependency injection "
            "for both connection types, not the full HTTPConnection properties or methods."
        ),
        "rationale": (
            "FastAPI 0.157.0 directly re-exports Starlette's HTTPConnection "
            "(`fastapi/requests.py:1`) and recognizes and injects that type during dependency "
            "analysis (`fastapi/dependencies/utils.py:392-413,797-812`). The selected cases "
            "are independently "
            "documented on this page and exercise one HTTP request plus one WebSocket session. "
            "Starlette 1.6.0 owns the connection object and generic HTTP/WebSocket transport; "
            "the pinned Starlette-RS checkout is the sibling behavior boundary."
        ),
    },
    ("reference/openapi/docs.md", "@line:1"): {
        "heading": "OpenAPI `docs`",
        "start_line": 1,
        "end_line": 11,
        "recipe_path": _DOCS_REFERENCE_OPENAPI,
        "case_ids": ["fastapi.docs.reference-wave.openapi.docs-ui-helpers"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The selected Swagger UI, ReDoc, and manual-helper actions observe their returned "
            "HTTP status, headers, and HTML bodies. They sample rendered helper responses, "
            "not helper signatures, every option, OAuth2 redirect HTML, or the default "
            "parameter dictionary."
        ),
        "rationale": (
            "FastAPI 0.157.0 implements the documented Swagger UI, ReDoc, and OAuth2 redirect "
            "helpers in `fastapi/openapi/docs.py:40-194,197-298,301-389`; the helpers "
            "return HTMLResponse values. The selected actions exercise the page's Swagger UI "
            "and ReDoc routes plus an explicit helper route and observe the resulting HTTP "
            "responses. Starlette 1.6.0 owns HTMLResponse rendering and emission."
        ),
    },
    ("reference/openapi/models.md", "@line:1"): {
        "heading": "OpenAPI `models`",
        "start_line": 1,
        "end_line": 5,
        "recipe_path": _OPENAPI_SCHEMA_FIELDS,
        "case_ids": [
            "fastapi.openapi-models.schema.aliases-wire-name",
            "fastapi.openapi-models.schema.aliases-python-field-names",
            "fastapi.openapi-models.schema.field-defaults",
            "fastapi.openapi-models.schema.invalid-multiple-of",
            "fastapi.openapi-models.schema.invalid-min-length",
            "fastapi.openapi-models.schema.invalid-max-items",
        ],
        "observation_selectors": [
            "python.call_outcome",
            "python.pydantic_model_result",
        ],
        "scope_note": (
            "The selected direct inputs exercise FastAPI's OpenAPI Schema model's JSON Schema "
            "wire aliases, Python field names, defaults, and three invalid constrained values. "
            "They do not cover the other OpenAPI model classes or generation and validation of "
            "a complete OpenAPI document."
        ),
        "rationale": (
            "FastAPI 0.157.0 defines `Schema` as a Pydantic model and declares JSON Schema "
            "aliases and field constraints (`fastapi/openapi/models.py:123-180`). The "
            "selected input-only API cases cite this exact documentation page and project only "
            "model dumps or call outcomes. They sample the documented public model's input "
            "contract under the pinned Pydantic runtime, not standalone Pydantic behavior."
        ),
    },
    ("reference/parameters.md", "@line:1"): {
        "heading": "Request Parameters",
        "start_line": 1,
        "end_line": 35,
        "recipe_path": _DOCS_REFERENCE_HTTP,
        "case_ids": ["fastapi.docs.reference-wave.http.parameter-source-matrix"],
        "observation_selectors": [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "The selected GET request supplies a path value, query value, and aliased header; "
            "the OpenAPI action observes their declarations for one operation. This samples "
            "Path, Query, and Header usage only; Body, Cookie, Form, File, and other parameter "
            "forms are outside this mapping."
        ),
        "rationale": (
            "FastAPI 0.157.0 exposes Path, Query, and Header constructors through "
            "`fastapi/param_functions.py:14,375,734`; dependency analysis reads the endpoint "
            "signature and converts request parameters into validated fields "
            "(`fastapi/dependencies/utils.py:314-343,423-485,952-989`). The selected case sends "
            "`widget_id`, "
            "`scale`, and `X-Region` values and observes the response plus generated parameter "
            "schema."
        ),
    },
    ("reference/response.md", "@line:1"): {
        "heading": "`Response` class",
        "start_line": 1,
        "end_line": 15,
        "recipe_path": _RESPONSE_CLASS_SOURCE_REVIEW,
        "case_ids": [
            "fastapi.docs.reference-response.injected-header",
            "fastapi.docs.reference-response.returned-instance",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "The selected independent requests exercise both documented forms: mutating an "
            "injected Response's status and header, and returning a Response instance. They "
            "do not cover cookies, other Response methods, or all Starlette response classes."
        ),
        "rationale": (
            "FastAPI 0.157.0 identifies and injects a Response parameter during dependency "
            "solving, then preserves a returned Response in its request handler "
            "(`fastapi/dependencies/utils.py:392-413,797-812`; "
            "`fastapi/routing.py:751-779`). "
            "The selected cases cite this exact reference page and observe only the resulting "
            "HTTP responses. Starlette 1.6.0 owns generic Response rendering and ASGI emission."
        ),
    },
    ("reference/websockets.md", "@line:1"): {
        "heading": "WebSockets",
        "start_line": 1,
        "end_line": 73,
        "recipe_path": _DOCS_REFERENCE_ASGI,
        "case_ids": ["fastapi.docs.reference-wave.asgi.websocket-endpoint-session"],
        "observation_selectors": [
            "websocket.close_code",
            "websocket.event_order",
            "websocket.messages",
        ],
        "scope_note": (
            "The selected session registers one FastAPI WebSocket endpoint, accepts the "
            "connection, receives one text message, sends one text reply, and closes. It does "
            "not cover the full listed WebSocket interface, HTTPConnection tip, or other "
            "message types and state transitions."
        ),
        "rationale": (
            "FastAPI 0.157.0 registers WebSocket operations on its router and builds an "
            "APIWebSocketRoute that solves dependencies before calling the endpoint "
            "(`fastapi/applications.py:1418-1481`; "
            "`fastapi/routing.py:3142-3162,808-892`). The selected "
            "case cites this page and observes one endpoint session. Starlette 1.6.0 supplies "
            "the WebSocket class and protocol state machine; the pinned Starlette-RS checkout "
            "owns that generic behavior boundary."
        ),
    },
    ("reference/websockets.md", "@line:49"): {
        "heading": "WebSockets - additional classes",
        "start_line": 49,
        "end_line": 73,
        "recipe_path": _ROOT_ALIAS_IDENTITY,
        "case_ids": ["fastapi.root-alias-identity.websocket-reexports"],
        "observation_selectors": [
            "websocket.event_order",
            "websocket.messages",
        ],
        "scope_note": (
            "The selected identity action reports whether `WebSocketDisconnect` and "
            "`WebSocketState` resolve to the corresponding Starlette classes through the "
            "documented FastAPI import paths. It does not exercise disconnect exceptions or "
            "WebSocketState values and transitions."
        ),
        "rationale": (
            "FastAPI 0.157.0 directly imports and re-exports `WebSocketDisconnect` and "
            "`WebSocketState` from Starlette (`fastapi/websockets.py:1-3`; "
            "`fastapi/__init__.py:24-25`), while the pinned "
            "Starlette 1.6.0 defines their exception and enum behavior (`starlette/websockets.py:"
            "13-24`). The selected WebSocket action observes identity relations for both names "
            "and cites this exact page; it does not claim generic disconnect or state-machine "
            "semantics."
        ),
    },
}
