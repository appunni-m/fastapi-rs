"""Source-reviewed overrides for FastAPI tutorial-page atlas candidates.

This file is intentionally separate from the atlas generator.  The source
checkout used for the review is FastAPI 0.141.1; Starlette ownership notes are
against the selected Starlette 1.6.0 contract.
"""

DOC_PAGE_REVIEW_MAPPINGS = {
    "reference/websockets.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "public-api-errors",
            "websocket-lifecycle",
        ],
        "observation_selectors": [
            "websocket.close_code",
            "websocket.event_order",
            "websocket.messages",
        ],
        "rationale": (
            "FastAPI 0.141.1 exposes Starlette's WebSocket and WebSocketDisconnect through "
            "fastapi.websockets and re-exports those two names at the fastapi root; "
            "WebSocketState is available from fastapi.websockets, not the root. FastAPI owns "
            "@app.websocket registration, APIWebSocketRoute construction, and typed "
            "WebSocket/HTTPConnection dependency injection. Starlette 1.6.0 owns the "
            "WebSocket class, its state machine and helper methods, WebSocketDisconnect and "
            "WebSocketState, inherited HTTPConnection properties, and generic WebSocket route "
            "dispatch. The page-linked input samples one endpoint session, not the referenced "
            "class API as a whole."
        ),
        "stimulus_notes": (
            "The materialized documented-page mapping links this page to only "
            "fastapi.docs.reference-wave.asgi.websocket-endpoint-session in "
            "tests/fixtures/input-recipes/parity/docs-reference-asgi.yaml. The workload imports "
            "WebSocket from fastapi, routes /echo, accepts without options, receives one text "
            "frame, sends one prefixed text frame, and closes without options. Its selectors "
            "record the final close code, ordered ASGI WebSocket message types, and ordered "
            "text/binary payloads with message types. The recipe's separate HTTPConnection "
            "case is indexed to reference/httpconnection.md and its upstream test instead. "
            "These are input observations selected for future comparison, not parity results."
        ),
        "contract_gate": (
            "Keep the page mapping partial. Importing WebSocket from fastapi to run the "
            "workload does not assert import-path or object identity, and none of these "
            "selectors records Python signatures. The case does not exercise the listed scope, "
            "connection-property, or state members; WebSocketDisconnect raising/catching on a "
            "client disconnect; WebSocketState values or transitions; bytes or JSON helpers; "
            "iterators; raw receive/send; accept subprotocol/headers; close reasons; denial "
            "responses; or invalid state transitions. The client disconnect supplied by the "
            "recipe is not consumed by the endpoint after it closes, so it is not evidence for "
            "WebSocketDisconnect behavior. The documented HTTPConnection tip has a separate "
            "reference-page mapping and is not counted as this page's linked case."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/websockets.md",
                "start_line": 1,
                "end_line": 17,
                "role": "WebSocket parameter/import guidance and shared HTTPConnection dependency tip",
            },
            {
                "path": "docs/en/docs/reference/websockets.md",
                "start_line": 19,
                "end_line": 47,
                "role": "documented WebSocket properties and method names",
            },
            {
                "path": "docs/en/docs/reference/websockets.md",
                "start_line": 49,
                "end_line": 73,
                "role": "documented WebSocketDisconnect and WebSocketState imports and descriptions",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 24,
                "end_line": 25,
                "role": "FastAPI root re-exports WebSocket and WebSocketDisconnect",
            },
            {
                "path": "fastapi/websockets.py",
                "start_line": 1,
                "end_line": 3,
                "role": "identity-preserving Starlette WebSocket, disconnect, and state aliases",
            },
            {
                "path": "fastapi/requests.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving HTTPConnection import path used by the page tip",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1361,
                "end_line": 1439,
                "role": "FastAPI app.websocket decorator forwards registered endpoints to its router",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 764,
                "end_line": 836,
                "role": "FastAPI dependency solving, WebSocket endpoint dispatch, APIWebSocketRoute construction, and Starlette route matching",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 370,
                "role": "FastAPI recognizes WebSocket and HTTPConnection as injected connection parameters",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 709,
                "end_line": 714,
                "role": "FastAPI supplies HTTPConnection or WebSocket values to endpoint parameters",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/websockets.py",
                "start_line": 13,
                "end_line": 187,
                "role": "Starlette 1.6.0 WebSocketState, WebSocketDisconnect, constructor, state transitions, and documented helper methods/signatures",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 80,
                "end_line": 159,
                "role": "Starlette 1.6.0 shared HTTPConnection scope, URL, headers, query, path, cookie, and client properties inherited by WebSocket",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 188,
                "end_line": 203,
                "role": "Starlette 1.6.0 inherited state and url_for properties documented on WebSocket",
            },
            {
                "path": "starlette/routing.py",
                "start_line": 70,
                "end_line": 84,
                "role": "Starlette 1.6.0 generic WebSocket ASGI session adapter",
            },
            {
                "path": "starlette/routing.py",
                "start_line": 297,
                "end_line": 355,
                "role": "Starlette 1.6.0 generic WebSocketRoute construction, matching, and dispatch",
            },
        ],
    },
    "advanced/websockets.md": {
        "heading": "WebSockets { #websockets }",
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "public-api-errors",
            "request-validation",
            "websocket-lifecycle",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "websocket.close_code",
            "websocket.event_order",
            "websocket.messages",
        ],
        "rationale": (
            "The page covers FastAPI WebSocket route registration, Depends/Security and "
            "path/query/cookie inputs, a WebSocketException policy close, and disconnect "
            "handling. FastAPI owns APIWebSocketRoute construction, WebSocket dependency and "
            "parameter binding, and the WebSocket validation-error handler. Starlette 1.6.0 "
            "owns the WebSocket connection state machine, accept/receive/send helpers, "
            "WebSocketDisconnect, generic WebSocketRoute dispatch, and default "
            "WebSocketException close handling. The selectors are limited to the HTTP demo "
            "response and supported WebSocket close/message/event observations. The FastAPI "
            "WebSocket re-export is a static identity contract; the existing ASGI recipes do "
            "not observe Python import or alias identity. Security scopes, OpenAPI, and HTTP "
            "validation projections are not behaviors of the WebSocket examples."
        ),
        "stimulus_notes": (
            "The current documented-page mapping fastapi.docs.advanced-websockets links to "
            "workflow websocket-echo in tests/fixtures/input-recipes/parity/websocket-echo.yaml, "
            "case fastapi.websocket.echo-text (websocket.event_order and "
            "websocket.messages; two text exchanges in one session). Reusable existing input "
            "workflow websockets-upstream in "
            "tests/fixtures/input-recipes/parity/websockets-upstream.yaml has cases "
            "fastapi.test.test-tutorial-test-websockets-test-tutorial001.test-websocket, "
            "fastapi.test.test-tutorial-test-websockets-test-tutorial002.test-websocket-with-cookie, "
            "fastapi.test.test-tutorial-test-websockets-test-tutorial002.test-websocket-with-header-and-query, "
            "fastapi.test.test-tutorial-test-websockets-test-tutorial002.test-websocket-no-credentials, "
            "and fastapi.test.test-tutorial-test-websockets-test-tutorial002.test-websocket-invalid-data "
            "(messages/event order, with close-code and close-reason checks on the latter two). Its case "
            "fastapi.test.test-tutorial-test-websockets-test-tutorial001.test-main observes the "
            "demo HTTP response. "
            "tests/fixtures/input-recipes/parity/websockets-tutorial003-upstream-subset.yaml "
            "has cases fastapi.websockets.tutorial003.home and "
            "fastapi.websockets.tutorial003.single-client-session (HTTP body and one-client "
            "messages only). These are input recipes and partial samples, not parity results."
        ),
        "contract_gate": (
            "Keep the mapping partial. The tutorial003 subset does not exercise two concurrent "
            "clients, broadcast delivery, or the disconnect announcement described by the page. "
            "The page's binary/JSON statement has no corresponding example input here; current "
            "tutorial cases exercise text only. The page's Header and Security entries have no "
            "matching parameter examples here; the upstream case named test-websocket-with-header "
            "supplies its token in the query string. The selected recipes do not cover all "
            "parameter combinations, Security scopes, dependency cleanup, Python import/alias "
            "identity, or WebSocket API signatures. Do not claim those branches from the existing "
            "inputs. The class-based WebSocket handling link is Starlette reference material, "
            "not a FastAPI example in this page."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/websockets.md",
                "start_line": 43,
                "end_line": 63,
                "role": "route creation, direct Starlette WebSocket note, and text/binary/JSON surface",
            },
            {
                "path": "docs/en/docs/advanced/websockets.md",
                "start_line": 99,
                "end_line": 120,
                "role": "documented dependency and parameter classes, plus policy close guidance",
            },
            {
                "path": "docs/en/docs/advanced/websockets.md",
                "start_line": 153,
                "end_line": 177,
                "role": "disconnect handling, multi-client broadcast description, and in-memory limit",
            },
            {
                "path": "docs/en/docs/advanced/websockets.md",
                "start_line": 93,
                "end_line": 97,
                "role": "multiple messages share one WebSocket connection",
            },
            {
                "path": "docs/en/docs/advanced/websockets.md",
                "start_line": 181,
                "end_line": 185,
                "role": "Starlette references, including its class-based WebSocket handling link",
            },
            {
                "path": "docs_src/websockets_/tutorial001_py310.py",
                "start_line": 1,
                "end_line": 4,
                "role": "FastAPI/WebSocket imports and app construction",
            },
            {
                "path": "docs_src/websockets_/tutorial001_py310.py",
                "start_line": 41,
                "end_line": 51,
                "role": "demo HTTP response and accepted text echo WebSocket route",
            },
            {
                "path": "docs_src/websockets_/tutorial002_an_py310.py",
                "start_line": 1,
                "end_line": 13,
                "role": "FastAPI WebSocket dependency/parameter/exception imports",
            },
            {
                "path": "docs_src/websockets_/tutorial002_an_py310.py",
                "start_line": 66,
                "end_line": 92,
                "role": "Cookie and Query dependency inputs, WebSocketException, and endpoint outputs",
            },
            {
                "path": "docs_src/websockets_/tutorial003_py310.py",
                "start_line": 44,
                "end_line": 61,
                "role": "connection manager accept, connection storage, personal send, and broadcast",
            },
            {
                "path": "docs_src/websockets_/tutorial003_py310.py",
                "start_line": 71,
                "end_line": 81,
                "role": "typed path parameter, receive loop, disconnect catch, and leave broadcast",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1361,
                "end_line": 1439,
                "role": "FastAPI.websocket registration and forwarding to APIRouter",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 764,
                "end_line": 837,
                "role": "FastAPI WebSocket dependency execution and APIWebSocketRoute construction/matching",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 163,
                "end_line": 186,
                "role": "FastAPI WebSocket ASGI wrapper adds dependency exit stacks around endpoint dispatch",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 714,
                "role": "FastAPI dependency recursion, path/query/header/cookie binding, and WebSocket injection",
            },
            {
                "path": "fastapi/exception_handlers.py",
                "start_line": 29,
                "end_line": 34,
                "role": "WebSocket parameter validation mapped to a policy-violation close",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1000,
                "end_line": 1012,
                "role": "FastAPI registers its WebSocket request-validation exception handler",
            },
            {
                "path": "fastapi/exceptions.py",
                "start_line": 86,
                "end_line": 155,
                "role": "FastAPI WebSocketException subclass and public constructor",
            },
            {
                "path": "fastapi/websockets.py",
                "start_line": 1,
                "end_line": 3,
                "role": "direct Starlette WebSocket/Disconnect/State re-exports",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/requests.py",
                "start_line": 80,
                "end_line": 159,
                "role": "Starlette 1.6.0 HTTPConnection headers, query, path, and cookie access used by WebSocket",
            },
            {
                "path": "starlette/websockets.py",
                "start_line": 13,
                "end_line": 57,
                "role": "Starlette 1.6.0 WebSocket states, disconnect exception, and receive transitions",
            },
            {
                "path": "starlette/websockets.py",
                "start_line": 59,
                "end_line": 128,
                "role": "Starlette 1.6.0 send/accept transitions and text/bytes receive helpers",
            },
            {
                "path": "starlette/websockets.py",
                "start_line": 130,
                "end_line": 187,
                "role": "Starlette 1.6.0 JSON/iterator/send/close helpers and denial-response behavior",
            },
            {
                "path": "starlette/routing.py",
                "start_line": 70,
                "end_line": 86,
                "role": "Starlette 1.6.0 generic websocket_session ASGI adapter",
            },
            {
                "path": "starlette/routing.py",
                "start_line": 297,
                "end_line": 355,
                "role": "Starlette 1.6.0 generic WebSocketRoute matching and dispatch",
            },
            {
                "path": "starlette/middleware/exceptions.py",
                "start_line": 18,
                "end_line": 33,
                "role": "Starlette 1.6.0 default WebSocketException handler registration",
            },
            {
                "path": "starlette/middleware/exceptions.py",
                "start_line": 47,
                "end_line": 73,
                "role": "Starlette 1.6.0 WebSocket exception dispatch and close response",
            },
            {
                "path": "starlette/exceptions.py",
                "start_line": 23,
                "end_line": 33,
                "role": "Starlette 1.6.0 WebSocketException code/reason attributes",
            },
        ],
    },
    "advanced/response-cookies.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
        ],
        "rationale": (
            "This page documents two distinct paths. FastAPI owns recognizing and injecting "
            "the temporary Response parameter, carrying its status and headers (including "
            "Set-Cookie) into a response serialized from the returned object, and returning an "
            "endpoint-returned Response directly without response-model filtering. Starlette "
            "1.6.0 owns Response/JSONResponse construction, set_cookie formatting, and ASGI "
            "status/header/body emission. FastAPI requires Python >=3.10; Starlette's "
            "partitioned-cookie option is Python >=3.14 and is outside these examples."
        ),
        "stimulus_notes": (
            "The existing input "
            "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml::"
            "fastapi.test.test-tutorial-test-response-cookies-test-tutorial002.test-path-operation "
            "uses the tutorial002 Response-parameter route and observes raw ASGI status, "
            "headers, and body. "
            "tests/fixtures/input-recipes/parity/response-surface.yaml::"
            "fastapi.response.cookie-header is another Response-parameter case with cookie "
            "attributes. The independent "
            "tests/fixtures/input-recipes/parity/response-cookie-direct-wave.yaml::"
            "fastapi.response.cookies.direct-jsonresponse-set-cookie case covers the direct "
            "JSONResponse.set_cookie branch with raw ASGI Set-Cookie headers and body bytes. "
            "The existing response-directly-tutorial001-wave.yaml direct-response case has no "
            "cookie and is only a dispatch baseline. The upstream TestClient assertions read "
            "response.cookies; these direct-ASGI inputs do not exercise that client jar."
        ),
        "contract_gate": (
            "Keep the page mapping partial. The existing and new inputs set cookies "
            "through a path-operation Response parameter or a direct JSONResponse; none sets "
            "one from a dependency, tests response-model filtering on the temporary-response "
            "path, or tests response-model bypass on the direct path. Raw ASGI headers and body "
            "bytes capture emitted cookie text but do not exercise TestClient/HTTPX cookie-jar "
            "extraction, persistence, or later request sending. No selected input has cookie "
            "middleware, so middleware-added or rewritten cookies remain unexercised. The "
            "catalog's http.cookies selector is a planned parsed Set-Cookie projection, not "
            "the upstream response.cookies jar assertion; this mapping selects raw ordered "
            "headers instead. The re-export/import conveniences cited below are source-verified, "
            "but no selected case compares import paths or object identity. The examples are "
            "within FastAPI's Python >=3.10 package floor; "
            "Starlette 1.6.0's partitioned cookie flag is available only on Python >=3.14 and "
            "is not covered here."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/response-cookies.md",
                "start_line": 3,
                "end_line": 17,
                "role": "temporary Response parameter, returned-object serialization, and dependency usage",
            },
            {
                "path": "docs/en/docs/advanced/response-cookies.md",
                "start_line": 19,
                "end_line": 35,
                "role": "direct Response return bypasses ordinary response-model filtering",
            },
            {
                "path": "docs/en/docs/advanced/response-cookies.md",
                "start_line": 41,
                "end_line": 51,
                "role": "FastAPI Response re-exports and Starlette set_cookie ownership boundary",
            },
            {
                "path": "docs_src/response_cookies/tutorial001_py310.py",
                "start_line": 1,
                "end_line": 12,
                "role": "documented direct JSONResponse cookie construction and return",
            },
            {
                "path": "docs_src/response_cookies/tutorial002_py310.py",
                "start_line": 1,
                "end_line": 9,
                "role": "documented temporary Response parameter and ordinary returned object",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI classifies Response as a special injected dependency parameter",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 611,
                "end_line": 614,
                "role": "FastAPI creates the temporary response shared by dependency solving",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 719,
                "end_line": 720,
                "role": "FastAPI passes the temporary response into the endpoint parameter",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 357,
                "end_line": 372,
                "role": "FastAPI takes the temporary response status into account",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 706,
                "end_line": 715,
                "role": "FastAPI returns an endpoint-provided Response directly",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 716,
                "end_line": 750,
                "role": "FastAPI serializes ordinary endpoint values and copies temporary response headers to the final response",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 6,
                "end_line": 12,
                "role": "FastAPI response classes, including Response and JSONResponse, are Starlette re-exports",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 21,
                "end_line": 22,
                "role": "FastAPI root Request and Response exports",
            },
            {
                "path": "fastapi/testclient.py",
                "start_line": 1,
                "end_line": 1,
                "role": "FastAPI TestClient is a Starlette TestClient re-export",
            },
            {
                "path": "pyproject.toml",
                "start_line": 5,
                "end_line": 12,
                "role": "FastAPI package requires Python 3.10 or newer",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 46,
                "role": "Starlette 1.6.0 generic Response construction",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 89,
                "end_line": 132,
                "role": "Starlette 1.6.0 set_cookie options, serialization, and raw Set-Cookie header append",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 168,
                "role": "Starlette 1.6.0 emits status, raw headers, and body as ASGI messages",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 181,
                "end_line": 201,
                "role": "Starlette 1.6.0 JSONResponse rendering over the generic Response contract",
            },
            {
                "path": "docs/responses.md",
                "start_line": 30,
                "end_line": 51,
                "role": "Starlette 1.6.0 documented cookie setter options and Python 3.14 partitioned-cookie floor",
            },
            {
                "path": "starlette/testclient.py",
                "start_line": 327,
                "end_line": 374,
                "role": "Starlette TestClient converts ASGI status, headers, and body into an HTTPX Response",
            },
            {
                "path": "starlette/testclient.py",
                "start_line": 377,
                "end_line": 420,
                "role": "Starlette TestClient subclasses httpx.Client and delegates cookie state to it",
            },
            {
                "path": "starlette/testclient.py",
                "start_line": 430,
                "end_line": 469,
                "role": "Starlette TestClient request delegates to the underlying HTTPX client",
            },
        ],
    },
    "advanced/response-directly.md": {
        "heading": "Return a Response Directly { #return-a-response-directly }",
        "replace_features": True,
        "feature_ids": ["openapi-docs", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "openapi.document",
            "openapi.paths",
        ],
        "rationale": (
            "FastAPI owns the path-operation decision at routing.py:711-750: a returned "
            "Starlette Response instance bypasses serialize_response and the configured "
            "response class; FastAPI adds solved background tasks only when the response has "
            "no background task already. A non-Response value goes through response "
            "serialization and response construction. FastAPI also excludes a Response return "
            "annotation from the inferred response model at routing.py:1081-1114. The classes exposed at "
            "fastapi.responses are Starlette re-exports; generic content rendering, media "
            "types, header defaults, JSON bytes, and ASGI response messages belong to the "
            "Starlette 1.6.0 response contract (and the sibling Starlette-RS contract). "
            "The selected recipe observations cover exact HTTP status, ordered headers, body "
            "bytes, and selected OpenAPI paths. They do not observe Python import identity, "
            "the jsonable_encoder return value, or response-model conversion."
        ),
        "stimulus_notes": (
            "In tests/fixtures/input-recipes/parity/response-surface.yaml, "
            "fastapi.response.direct-json is a direct JSONResponse return with status, "
            "headers, and body-byte observations; it is an independent compatible sample, "
            "not an execution of docs_src/response_directly/tutorial001_py310.py. The page-linked "
            "case fastapi.response.direct-plain-text returns a PlainTextResponse while also "
            "declaring response_class=PlainTextResponse, so it samples a Response subclass "
            "return but cannot isolate the default response-class path. "
            "fastapi.response.openapi-status-and-media observes selected /openapi.json path "
            "pointers, including /raw-json and /documents; it is not the tutorial examples' "
            "OpenAPI document. These recipes contain stimuli, not expected outputs or parity results."
        ),
        "contract_gate": (
            "Keep this page mapping partial. The current response-surface workload does not "
            "execute tutorial001's Pydantic Item/datetime plus jsonable_encoder flow or "
            "tutorial002's XML Response example, and it does not directly call jsonable_encoder. "
            "Its direct-plain-text route declares response_class, so it cannot prove the "
            "unconfigured direct-Response branch alone; the direct-json case is a separate "
            "workload sample. Existing OpenAPI pointers do not establish all automatic "
            "documentation behavior. Import/re-export identity, Python encoder values, "
            "response validation/serialization bypass for arbitrary models, custom media-type "
            "edge cases, and error branches remain unsupported by these observations. The "
            "indexed ASGI message_types observation establishes emitted message-type order only; "
            "it does not cover response chunk bodies, chunk boundaries, or the complete ASGI "
            "state machine."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/response-directly.md",
                "start_line": 3,
                "end_line": 13,
                "role": "default FastAPI response serialization and JSONResponse guidance",
            },
            {
                "path": "docs/en/docs/advanced/response-directly.md",
                "start_line": 17,
                "end_line": 33,
                "role": "direct Response subclass return and FastAPI pass-through claim",
            },
            {
                "path": "docs/en/docs/advanced/response-directly.md",
                "start_line": 35,
                "end_line": 49,
                "role": "jsonable_encoder example context and FastAPI/Starlette response import note",
            },
            {
                "path": "docs/en/docs/advanced/response-directly.md",
                "start_line": 53,
                "end_line": 63,
                "role": "custom Response example and XML content guidance",
            },
            {
                "path": "docs/en/docs/advanced/response-directly.md",
                "start_line": 65,
                "end_line": 81,
                "role": "response-model serialization versus direct-response validation, conversion, and documentation",
            },
            {
                "path": "docs_src/response_directly/tutorial001_py310.py",
                "start_line": 1,
                "end_line": 21,
                "role": "Pydantic model, explicit jsonable_encoder call, and direct JSONResponse return",
            },
            {
                "path": "docs_src/response_directly/tutorial002_py310.py",
                "start_line": 1,
                "end_line": 18,
                "role": "FastAPI Response import and directly returned application/xml body",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 706,
                "end_line": 750,
                "role": "FastAPI reuses returned Response instances; non-Response values go through serialization and response construction",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1081,
                "end_line": 1114,
                "role": "FastAPI does not infer a response model from a Response subclass return annotation",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 1,
                "end_line": 12,
                "role": "FastAPI response-module aliases for Starlette response classes",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 21,
                "end_line": 23,
                "role": "FastAPI root Request/Response/APIRouter exports",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 81,
                "role": "Starlette 1.6.0 Response construction/rendering and default content headers",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 163,
                "end_line": 201,
                "role": "Starlette 1.6.0 ASGI response sending and PlainTextResponse/JSONResponse body behavior",
            },
        ],
    },
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
            "request validation or an error/deprecation surface. Exact Url and AnyUrl "
            "conversion behavior is sourced to the pinned encoder registrations below, "
            "not inferred from the tutorial text."
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
                "start_line": 103,
                "end_line": 111,
                "role": "Url and AnyUrl are registered as string encoders",
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
            "The page specifies HTTP middleware wrapping, response mutation, stack order, "
            "yield-dependency cleanup, and background-task ordering. FastAPI exposes the "
            "decorator and inherits generic add_middleware stack construction from Starlette. "
            "The Request import convenience is a direct Starlette re-export."
        ),
        "stimulus_notes": (
            "tests/fixtures/input-recipes/parity/middleware-execution-order-wave.yaml::"
            "fastapi.docs.middleware.request-and-response-order records an independent trace "
            "from two `add_middleware` wrappers: the last-added wrapper enters first on the "
            "request path, and the first-added wrapper observes the response first. The trace "
            "is returned by a second request and compared through exact HTTP body bytes. "
            "middleware.yaml::fastapi.middleware.decorator-openapi covers the HTTP decorator "
            "and response headers; middleware.yaml's HTTPS redirect, trusted-host, and custom "
            "body-limit cases cover separate middleware behaviors. "
            "dependency-wave-lifecycle.yaml::fastapi.dependencies.contextvars-through-middleware "
            "covers context propagation across HTTP middleware. These are independent samples, "
            "not complete coverage of arbitrary middleware implementations."
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
                "path": "starlette/applications.py",
                "start_line": 63,
                "end_line": 83,
                "role": "Starlette 1.6.0 builds its middleware stack by wrapping the router in reverse order",
            },
            {
                "path": "starlette/applications.py",
                "start_line": 104,
                "end_line": 107,
                "role": "Starlette 1.6.0 prepends each added middleware, making the newest wrapper outermost",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 214,
                "end_line": 226,
                "role": "selected Starlette Request implementation",
            },
        ],
        "contract_gate": (
            "The new order case observes only the documented two-wrapper HTTP nesting and uses "
            "its independently returned event trace as exact body bytes. The separate decorator "
            "workflow observes middleware headers but not decorator-registration ordering. These "
            "cases do not establish ordering for arbitrary middleware or WebSocket/lifespan scopes. The page's yield-"
            "dependency-exit and background-task-after-middleware statements are not compared "
            "against middleware events by these cases. Existing dependency/background fixtures "
            "observe those lifecycles separately, so do not infer their cross-order from this "
            "page mapping."
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
        "feature_ids": ["openapi-docs", "request-validation"],
        "observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "rationale": (
            "The page specifies File/UploadFile request extraction, required and optional file "
            "parameters, byte and UploadFile values, and repeated file fields. FastAPI infers "
            "UploadFile annotations as File and bridges Starlette form parsing into dependency "
            "validation. The fastapi.responses note is an import convenience, not a file-input "
            "behavior."
        ),
        "stimulus_notes": (
            "tests/fixtures/input-recipes/parity/request-multipart.yaml cases "
            "fastapi.request-multipart.file.bytes-present, "
            "fastapi.request-multipart.file.upload-present, "
            "fastapi.request-multipart.file.required-missing, "
            "fastapi.request-multipart.file.optional-missing, and the optional-list cases "
            "exercise independent multipart bodies for bytes/UploadFile, required/optional, "
            "and repeated file inputs. tests/fixtures/input-recipes/parity/request-uploads.yaml "
            "cases fastapi.request-uploads.request-files-001-02.test-post-upload-file and "
            "fastapi.request-uploads.request-files-002.test-post-files exercise the documented "
            "single and multiple UploadFile examples with independent names and values. These "
            "workflows observe HTTP status and exact response bytes. The same request-uploads "
            "recipe's fastapi.request-uploads.request-files.openapi-schema case observes the "
            "complete OpenAPI document for the independent upload routes."
        ),
        "contract_gate": (
            "The page also documents generated multipart OpenAPI schemas, UploadFile's raw "
            "SpooledTemporaryFile interface, spool-to-disk behavior, seek/write/close, async "
            "thread-pool execution, and Pydantic compatibility. The linked request workflows "
            "observe a complete OpenAPI document for independent routes, not the exact documented "
            "example schemas; they also do not observe Python import/object identity, upload-file "
            "lifetime, or spooling behavior. Multipart execution requires the optional "
            "python-multipart profile; the input cases do not test missing-parser behavior. Do "
            "not infer these unobserved behaviors from successful body extraction."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/tutorial/request-files.md",
                "start_line": 1,
                "end_line": 176,
                "role": "FastAPI File/UploadFile request, optional, repeated, and metadata contract",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 12,
                "end_line": 20,
                "role": "FastAPI root exports the File parameter helper",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 663,
                "end_line": 742,
                "role": "File is a Form specialization with multipart/form-data media type",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 498,
                "end_line": 505,
                "role": "FastAPI infers File for UploadFile and UploadFile sequence annotations",
            },
            {
                "path": "fastapi/datastructures.py",
                "start_line": 21,
                "end_line": 150,
                "role": "FastAPI UploadFile subclass, Pydantic validation/schema hooks, and async file methods",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 425,
                "end_line": 431,
                "role": "FastAPI parses form request bodies and schedules parsed file cleanup",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 231,
                "end_line": 263,
                "role": "FastAPI emits request-body media type and schema in OpenAPI operations",
            },
            {
                "path": "docs/en/docs/tutorial/request-files.md",
                "start_line": 150,
                "end_line": 166,
                "role": "FastAPI response import convenience from Starlette",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 9,
                "end_line": 16,
                "role": "FastAPI root exports UploadFile and File",
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
                "path": "starlette/datastructures.py",
                "start_line": 410,
                "end_line": 476,
                "role": "Starlette UploadFile storage, metadata, and async file methods inherited by FastAPI",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 268,
                "end_line": 311,
                "role": "Starlette request.form parses multipart/form-urlencoded bodies and owns parser error handling",
            },
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
