"""Reviewed section mappings for the FastAPI direct-response documentation."""


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


_DIRECTLY = "tests/fixtures/input-recipes/parity/response-directly-tutorial001-wave.yaml"
_SURFACE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_RESPONSE_MODELS = "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml"
_CUSTOM_XML = "tests/fixtures/input-recipes/parity/response-directly-custom-xml-1016.yaml"

DOC_SECTION_CASE_MAPPINGS_RESPONSE_DIRECTLY_1016 = {
    ("advanced/response-directly.md", "return-a-response-directly"): _excluded(
        "Return a Response Directly { #return-a-response-directly }",
        1,
        83,
        (
            "The introduction summarizes direct JSONResponse, jsonable_encoder, and response-model "
            "choices that are mapped in the child sections. Its performance tip is qualitative "
            "and does not define a distinct request/response input."
        ),
        (
            "The H1 is an overview rather than an independently observable FastAPI operation; "
            "parity inputs establish response behavior, while performance requires a separate "
            "equivalent-work benchmark."
        ),
    ),
    ("advanced/response-directly.md", "return-a-response"): _workflow(
        "Return a `Response` { #return-a-response }",
        17,
        34,
        _SURFACE,
        ["fastapi.response.direct-plain-text"],
        ["dispatch"],
        [
            "asgi.send.message_types",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        (
            "The selected request receives a directly returned PlainTextResponse with a "
            "non-default status and observes its body, ordered headers, status, and ASGI send "
            "message types. It samples one response subclass and does not claim every "
            "constructor or subclass."
        ),
        (
            "FastAPI passes an endpoint-returned Response through without response-model "
            "serialization; Starlette 1.6.0 owns PlainTextResponse wire rendering."
        ),
    ),
    (
        "advanced/response-directly.md",
        "using-the-jsonable-encoder-in-a-response",
    ): _workflow(
        "Using the `jsonable_encoder` in a `Response` "
        "{ #using-the-jsonable-encoder-in-a-response }",
        35,
        52,
        _DIRECTLY,
        ["fastapi.response-directly.tutorial001.path-response"],
        ["update-inventory-item"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected PUT sends a typed item containing a datetime through "
            "jsonable_encoder before JSONResponse construction, then observes the returned "
            "HTTP body, headers, and status. The OpenAPI action is outside this section's claim."
        ),
        (
            "FastAPI's jsonable_encoder prepares model data for a directly returned "
            "JSONResponse; Starlette 1.6.0 owns JSONResponse byte encoding and transport."
        ),
    ),
    ("advanced/response-directly.md", "returning-a-custom-response"): _workflow(
        "Returning a custom `Response` { #returning-a-custom-response }",
        53,
        64,
        _CUSTOM_XML,
        ["fastapi.docs.response-directly.custom-xml-response"],
        ["read-xml-feed"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The independent GET returns a base Response with synthetic XML content and an "
            "application/xml media type; it observes the exact response body, headers, and "
            "status. It does not claim generic Response construction outside FastAPI routing."
        ),
        (
            "FastAPI accepts a directly returned Starlette Response through a route; Starlette "
            "1.6.0 owns the generic Response content and media-type behavior."
        ),
    ),
    ("advanced/response-directly.md", "how-a-response-model-works"): _workflow(
        "How a Response Model Works { #how-a-response-model-works }",
        65,
        76,
        _RESPONSE_MODELS,
        ["fastapi.response-model.tutorial003-01-return-annotation-filters-derived-input"],
        [
            "create-user-using-output-return-annotation",
            "return-annotation-openapi-shape",
        ],
        [
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected POST uses a return annotation as its response model, observes the "
            "serialized result, and pairs it with request/response schema pointers. It samples "
            "one model shape and makes no performance claim."
        ),
        (
            "FastAPI derives response filtering and route documentation from the endpoint's "
            "return annotation; Pydantic supplies model validation, serialization, and schema "
            "details."
        ),
    ),
    ("advanced/response-directly.md", "notes"): _excluded(
        "Notes { #notes }",
        77,
        83,
        (
            "This closing note recaps direct-Response validation, conversion, and documentation "
            "cautions, then links to Additional Responses in OpenAPI. It adds no independent "
            "endpoint or input; the concrete direct-response and response-model examples are "
            "mapped above."
        ),
        (
            "The pinned span is a summary and a cross-reference, not a new FastAPI operation. "
            "The linked additional-response OpenAPI behavior must be evaluated from its own "
            "page and fixtures rather than inferred from this link."
        ),
    ),
}
