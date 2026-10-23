"""Reviewed mappings for pending response-reference documentation sections.

Original review provenance: FastAPI 0.141.1 at
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f. Active FastAPI source claims below
were rechecked against 0.157.0 at 386a28af2f87af1a32ac26d88f07b7f58ab2dfb1.
Starlette remains pinned to 1.6.0 at 4f250d6b814587e20c5365f0a5f0c4d42bcb929f,
and the assigned
Starlette-RS behavior owner at b4c8a65c85e1b0d251ca05874412811eaa3ac7b8.

Existing additional-response model/media-type and tutorial/status-code sections
are intentionally left to their already reviewed sidecars.
"""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_ADDITIONAL_OPENAPI = "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml"
_STATUS_IDENTITY = "tests/fixtures/input-recipes/parity/status-module-identity.yaml"
_RESPONSE_SURFACE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_ROOT_ALIAS_IDENTITY = "tests/fixtures/input-recipes/parity/root-alias-identity.yaml"
_SSE_TUTORIAL002 = (
    "tests/fixtures/input-recipes/parity/server-sent-events-tutorial002-upstream.yaml"
)


DOC_SECTION_CASE_MAPPINGS_RESPONSE_REFERENCE_20261015 = {
    ("advanced/additional-responses.md", "additional-responses-in-openapi"): _excluded(
        "Additional Responses in OpenAPI { #additional-responses-in-openapi }",
        1,
        247,
        (
            "The page introduction is a high-level summary of additional statuses, media types, "
            "direct Response returns, and OpenAPI output. Its broad claims are handled in the "
            "specific child sections; the root heading does not define a separate operation."
        ),
        (
            "The already reviewed additional-response model and media-type sections have their "
            "own inputs. The two remaining OpenAPI examples are mapped below, while the final "
            "section is standards-link prose. Treating this whole-page summary as another "
            "workflow would duplicate those narrower cases and overstate their scope."
        ),
    ),
    ("advanced/additional-responses.md", "combining-information"): _workflow(
        "Combining information { #combining-information }",
        194,
        211,
        _ADDITIONAL_OPENAPI,
        ["fastapi.additional-response-openapi-wave.modeled-not-found.test-openapi-schema"],
        ["dispatch"],
        ["docs.response.status", "http.status", "openapi.document", "openapi.paths"],
        (
            "The selected OpenAPI action reads the `/documented/{item_id}` response subtree, "
            "which combines a response model with additional 200 response content and a "
            "modeled 404 response. It does not observe the endpoint's returned HTTP body, "
            "runtime response validation, other merge forms, or every response declaration."
        ),
        (
            "FastAPI 0.157.0 processes `route.responses`, removes the Python-only `model` key, "
            "and merges any prepared model schema into the declared content "
            "(fastapi/openapi/utils.py:458-501). The selected case observes only the generated "
            "response subtree for its independent `/documented/{item_id}` route."
        ),
    ),
    ("advanced/additional-responses.md", "combine-predefined-responses-and-custom-ones"): _workflow(
        (
            "Combine predefined responses and custom ones "
            "{ #combine-predefined-responses-and-custom-ones }"
        ),
        212,
        241,
        _ADDITIONAL_OPENAPI,
        ["fastapi.additional-response-openapi-wave.multiple-statuses.test-openapi-schema"],
        ["dispatch"],
        ["docs.response.status", "http.status", "openapi.document", "openapi.paths"],
        (
            "The selected action observes the generated response map for one route with 404, "
            "302, 403, and 200 declarations, including the added image/png media type. The "
            "workload authors that resulting mapping directly; it does not test Python `**` "
            "unpacking, override order, FileResponse delivery, or reusable application-wide "
            "response policy."
        ),
        (
            "FastAPI consumes the route's resulting `responses` mapping and merges its entries "
            "into the OpenAPI operation (fastapi/openapi/utils.py:458-501). Python dictionary "
            "unpacking in the source example "
            "(docs_src/additional_responses/tutorial004_py310.py:11-24) "
            "is language behavior and is not claimed by this FastAPI route input."
        ),
    ),
    ("advanced/additional-responses.md", "more-information-about-openapi-responses"): _excluded(
        "More information about OpenAPI responses { #more-information-about-openapi-responses }",
        242,
        247,
        (
            "This section links to the OpenAPI 3.1 Responses Object and Response Object "
            "specification text. It does not define a separate FastAPI route or behavior."
        ),
        (
            "The source at docs/en/docs/advanced/additional-responses.md:242-247 names external "
            "protocol objects and their fields; those standard definitions are not FastAPI "
            "runtime behavior, so no workflow is attached here."
        ),
    ),
    ("reference/responses.md", "@line:1"): _workflow(
        "Custom Response Classes - File, HTML, Redirect, Streaming, etc.",
        1,
        172,
        _RESPONSE_SURFACE,
        ["fastapi.response.direct-plain-text"],
        ["dispatch"],
        [
            "asgi.send.message_types",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        (
            "The introductory section is sampled through one directly returned "
            "PlainTextResponse from a FastAPI route. The observed response does not cover the "
            "other response classes listed on the page or their inherited methods."
        ),
        (
            "FastAPI passes a returned Response instance through in its request handler "
            "(fastapi/routing.py:751-755); Starlette 1.6.0 owns PlainTextResponse rendering "
            "and generic ASGI emission. The selected independent action is PUT "
            "/documents/alpha-7, whose handler returns a PlainTextResponse with status 202."
        ),
    ),
    ("reference/responses.md", "@line:23"): _excluded(
        "FastAPI Responses",
        23,
        62,
        (
            "This section documents the UJSONResponse and ORJSONResponse deprecation and a "
            "comparative serialization-performance recommendation. These class/API and "
            "performance claims are not established by an HTTP result selector in the reviewed "
            "input set."
        ),
        (
            "FastAPI 0.157.0 marks both classes deprecated in fastapi/responses.py:39-98; the "
            "generated API/deprecation inventory is the source of their public contract. The "
            "available UJSON tutorial case does not project a warning selector or successful "
            "serialization result, and no equivalent performance benchmark is part of parity. "
            "No route-behavior claim is made for this section."
        ),
    ),
    ("reference/responses.md", "@line:63"): _workflow(
        "Starlette Responses",
        63,
        172,
        _ROOT_ALIAS_IDENTITY,
        ["fastapi.root-alias-identity.http-reexports"],
        ["read-http-identity-relations"],
        ["http.body.bytes", "http.status"],
        (
            "The selected identity response checks that FastAPI's `responses` module exposes "
            "the same FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, "
            "RedirectResponse, Response, and StreamingResponse classes as Starlette. It does "
            "not test those classes' inherited rendering, file, redirect, cookie, or streaming "
            "methods."
        ),
        (
            "FastAPI 0.157.0 imports the documented classes directly from "
            "starlette.responses (fastapi/responses.py:5-12). The selected independent case "
            "returns class-identity relations in its HTTP body; generic response behavior is "
            "owned by the pinned Starlette 1.6.0 contract."
        ),
    ),
    ("reference/status.md", "@line:1"): _workflow(
        "Status Codes",
        1,
        36,
        _STATUS_IDENTITY,
        ["fastapi.status-alias.namespace"],
        ["read-status-namespace"],
        ["http.body.bytes", "http.status"],
        (
            "The selected route serializes FastAPI's `status` module identity, exported names, "
            "and integer values. This samples the documented Starlette re-export and its "
            "constant namespace; it does not render this reference page or exercise a route "
            "status choice, which is mapped under the Example heading."
        ),
        (
            "FastAPI 0.157.0 re-exports `starlette.status` directly "
            "(fastapi/__init__.py:5). The identity workload compares those module objects and "
            "enumerates the exported constants; Starlette 1.6.0 owns the constants themselves."
        ),
    ),
    ("reference/status.md", "@line:23"): _workflow(
        "Example",
        23,
        36,
        _RESPONSE_SURFACE,
        ["fastapi.docs.reference-wave.status-code-from-constant"],
        ["dispatch"],
        [
            "asgi.send.message_types",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        (
            "The selected GET route uses `status.HTTP_418_IM_A_TEAPOT` as its decorator status "
            "and observes the final status, headers, body, and ASGI send message types. It "
            "samples one named constant and does not claim every status value or the generated "
            "reference documentation."
        ),
        (
            "FastAPI 0.157.0 normalizes IntEnum status values while constructing an APIRoute "
            "(fastapi/routing.py:1083-1088) and uses the configured route status in response "
            "construction (fastapi/routing.py:380-395). The page's example selects one such "
            "constant-backed response."
        ),
    ),
    ("reference/sse.md", "@line:1"): _workflow(
        "Server-Sent Events - `EventSourceResponse` and `ServerSentEvent`",
        1,
        17,
        _SSE_TUTORIAL002,
        ["fastapi.tutorial.server-sent-events.tutorial002.event-fields"],
        ["stream-event-fields"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected GET action yields one comment event and three ServerSentEvent items "
            "with data, event, id, and retry values through EventSourceResponse. It observes "
            "the collected status, headers, and body; it does not assert ASGI chunk boundaries, "
            "keepalive timing, reconnection behavior, field validation, raw_data, or every API "
            "member."
        ),
        (
            "FastAPI 0.157.0 provides EventSourceResponse and the ServerSentEvent field model "
            "in fastapi/sse.py:20-34 and :52-156; its routing layer serializes yielded SSE "
            "items at fastapi/routing.py:560-591,620-623. The selected workflow "
            "action observes one "
            "completed event stream while generic response streaming belongs to Starlette 1.6.0."
        ),
    ),
}
