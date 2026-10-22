"""Reviewed mappings for FastAPI custom-response documentation sections."""


def _workflow(heading, start, end, recipe, case, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": [case],
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


_SURFACE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_SURFACE_SELECTORS = [
    "asgi.send.message_types",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
]
_TUTORIAL002 = "tests/fixtures/input-recipes/parity/custom-response-tutorial002-upstream.yaml"
_TUTORIAL003 = "tests/fixtures/input-recipes/parity/custom-response-tutorial003-upstream.yaml"
_TUTORIAL004 = "tests/fixtures/input-recipes/parity/custom-response-tutorial004-upstream.yaml"
_HTML_SELECTORS = [
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_HTML_DIRECT_SELECTORS = [
    "docs.response.status",
    "http.body.bytes",
    "http.status",
    "openapi.document",
    "openapi.paths",
]

DOC_SECTION_CASE_MAPPINGS_CUSTOM_RESPONSE_WAVE_M = {
    ("advanced/custom-response.md", "custom-response-html-stream-file-others"): _workflow(
        "Custom Response - HTML, Stream, File, others { #custom-response-html-stream-file-others }",
        1,
        273,
        _TUTORIAL004,
        "fastapi.custom-response.tutorial004.items-response",
        ["items", "openapi"],
        _HTML_SELECTORS,
        (
            "The documented HTML route returns an HTMLResponse while declaring its response "
            "class; paired OpenAPI and HTTP observations cover this representative route, not "
            "every response class listed on the page."
        ),
        (
            "FastAPI selects the response class for route documentation and returns the "
            "endpoint's Response object; generic response construction and transport belong to "
            "Starlette."
        ),
    ),
    ("advanced/custom-response.md", "json-responses"): _workflow(
        "JSON Responses { #json-responses }",
        19,
        34,
        _SURFACE,
        "fastapi.response.direct-json",
        ["dispatch"],
        _SURFACE_SELECTORS,
        (
            "The selected request returns one JSONResponse directly and observes its exact "
            "status, headers, body, and ASGI message types; model and jsonable-encoder paths "
            "are outside this sample."
        ),
        (
            "FastAPI permits a path operation to return a Starlette Response directly; "
            "Starlette owns JSONResponse byte serialization."
        ),
    ),
    ("advanced/custom-response.md", "json-performance"): _excluded(
        "JSON Performance { #json-performance }",
        29,
        34,
        (
            "This subsection gives qualitative performance advice rather than a distinct "
            "request/response behavior. Its performance comparison belongs to the separately "
            "gated equivalent-work benchmark plan."
        ),
        (
            "A parity input can observe response behavior but cannot substantiate the "
            "performance recommendation; no numeric claim is made by this atlas mapping."
        ),
    ),
    ("advanced/custom-response.md", "html-response"): _workflow(
        "HTML Response { #html-response }",
        35,
        93,
        _TUTORIAL002,
        "fastapi.custom-response.tutorial002.items-response",
        ["items"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The tutorial route declares HTMLResponse and observes its returned body and "
            "headers, including the HTML content type; OpenAPI shape is not claimed here."
        ),
        (
            "FastAPI resolves the path operation's response_class and constructs the response "
            "from its returned value; Starlette owns HTML response encoding."
        ),
    ),
    ("advanced/custom-response.md", "return-a-response"): _workflow(
        "Return a `Response` { #return-a-response }",
        54,
        73,
        _TUTORIAL003,
        "fastapi.custom-response.tutorial003.items-response",
        ["items", "openapi"],
        _HTML_DIRECT_SELECTORS,
        (
            "The direct HTMLResponse action is paired with the generated OpenAPI paths to "
            "observe the direct-response route and its documentation. Other Response types "
            "are not claimed."
        ),
        (
            "FastAPI passes a directly returned Response through instead of serializing its "
            "content as a response model; Starlette owns its wire representation."
        ),
    ),
    ("advanced/custom-response.md", "document-in-openapi-and-override-response"): _workflow(
        (
            "Document in OpenAPI and override `Response` "
            "{ #document-in-openapi-and-override-response }"
        ),
        74,
        93,
        _TUTORIAL004,
        "fastapi.custom-response.tutorial004.items-response",
        ["items", "openapi"],
        _HTML_SELECTORS,
        (
            "The route declares HTMLResponse for OpenAPI and returns an HTMLResponse object; "
            "the selected HTTP and OpenAPI actions observe the declared media type and actual "
            "response."
        ),
        (
            "FastAPI uses response_class for route documentation while retaining the "
            "endpoint-returned Response object; generic response behavior belongs to Starlette."
        ),
    ),
    ("advanced/custom-response.md", "return-an-htmlresponse-directly"): _workflow(
        "Return an `HTMLResponse` directly { #return-an-htmlresponse-directly }",
        80,
        93,
        _TUTORIAL004,
        "fastapi.custom-response.tutorial004.items-response",
        ["items", "openapi"],
        _HTML_SELECTORS,
        (
            "The documented endpoint returns an HTMLResponse directly while also declaring "
            "that class for OpenAPI; the input observes one route and its generated paths."
        ),
        (
            "FastAPI's response_class declaration controls OpenAPI documentation even when "
            "the endpoint supplies the concrete Response object."
        ),
    ),
    ("advanced/custom-response.md", "available-responses"): _excluded(
        "Available responses { #available-responses }",
        94,
        218,
        (
            "This section inventories generic Response subclasses, their constructor "
            "arguments, and transport behavior owned by the pinned Starlette contract. "
            "FastAPI-specific response-class selection and direct-return integration are "
            "sampled in adjacent sections."
        ),
        (
            "FastAPI re-exports or accepts Starlette response classes; duplicating their "
            "generic API surface here would misattribute Starlette behavior to FastAPI."
        ),
    ),
    ("advanced/custom-response.md", "response"): _excluded(
        "`Response` { #response }",
        108,
        124,
        (
            "Constructor arguments, content length, content type, and base response behavior "
            "are Starlette 1.6.0 contracts, not FastAPI-specific behavior."
        ),
        (
            "FastAPI-RS consumes the Starlette-RS Response contract; the FastAPI route "
            "integration is exercised in the direct-response section."
        ),
    ),
    ("advanced/custom-response.md", "jsonresponse"): _workflow(
        "`JSONResponse` { #jsonresponse }",
        135,
        148,
        _SURFACE,
        "fastapi.response.direct-json",
        ["dispatch"],
        _SURFACE_SELECTORS,
        (
            "This sample returns one JSONResponse directly and observes its HTTP output; it "
            "does not claim generic JSONResponse constructor or renderer behavior."
        ),
        (
            "FastAPI supports a directly returned Starlette Response; JSON rendering remains "
            "owned by Starlette."
        ),
    ),
    ("advanced/custom-response.md", "redirectresponse"): _workflow(
        "`RedirectResponse` { #redirectresponse }",
        149,
        173,
        "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml",
        "fastapi.response-model.tutorial003-02-response-annotation-allows-response-values",
        ["portal-redirect-response"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected endpoint action returns one RedirectResponse directly and observes "
            "the resulting status, Location header, and body; response_class parameter "
            "variants are outside this sample."
        ),
        (
            "FastAPI allows Response subclasses as endpoint return values; redirect status and "
            "Location header behavior belong to Starlette."
        ),
    ),
    ("advanced/custom-response.md", "streamingresponse"): _workflow(
        "`StreamingResponse` { #streamingresponse }",
        174,
        197,
        "tests/fixtures/input-recipes/parity/stream-cancellation.yaml",
        "fastapi.stream-cancellation.raw-async-generator",
        ["cancel-raw-stream"],
        ["asgi.cancellation.cancelled_caught", "http.headers.ordered", "http.status"],
        (
            "The input samples cancellation propagation for one streamed response and records "
            "status and headers. It does not claim chunk boundaries or all generator forms."
        ),
        (
            "FastAPI routes the endpoint's streaming response through the ASGI application; "
            "generic stream iteration and transport belong to Starlette."
        ),
    ),
    ("advanced/custom-response.md", "fileresponse"): _workflow(
        "`FileResponse` { #fileresponse }",
        198,
        218,
        "tests/fixtures/input-recipes/parity/tutorial-additional-responses-file-response-review.yaml",
        "fastapi.tutorial-additional-responses.file-response",
        ["return-file-response"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The route returns one FileResponse and observes the selected file body's bytes, "
            "headers, and status; ranges, path variation, and generic file transport are not "
            "claimed."
        ),
        (
            "FastAPI accepts the returned Starlette FileResponse through its route; file "
            "metadata and transfer behavior are Starlette-owned."
        ),
    ),
    ("advanced/custom-response.md", "custom-response-class"): _excluded(
        "Custom response class { #custom-response-class }",
        219,
        254,
        (
            "The section's CustomORJSONResponse.render implementation and orjson settings are "
            "user-authored code and optional third-party behavior. FastAPI's route response "
            "class selection is sampled in the HTML response sections."
        ),
        (
            "FastAPI invokes a configured response class but does not own the custom class's "
            "implementation or JSON rendering contract."
        ),
    ),
    ("advanced/custom-response.md", "orjson-or-response-model"): _excluded(
        "`orjson` or Response Model { #orjson-or-response-model }",
        247,
        254,
        (
            "This subsection compares qualitative serialization performance and Pydantic/orjson "
            "implementation details rather than a distinct input/output feature. Performance "
            "claims require the separately gated equivalent-work benchmark."
        ),
        (
            "Pydantic serialization ownership and FastAPI response-model behavior are tracked "
            "elsewhere; this atlas mapping makes no speed or implementation claim."
        ),
    ),
    ("advanced/custom-response.md", "additional-documentation"): _excluded(
        "Additional documentation { #additional-documentation }",
        271,
        273,
        (
            "This section only links to the separate Additional Responses in OpenAPI page and "
            "adds no independent behavior."
        ),
        (
            "The linked OpenAPI response behavior is reviewed under the dedicated "
            "additional-responses documentation and fixtures."
        ),
    ),
}
