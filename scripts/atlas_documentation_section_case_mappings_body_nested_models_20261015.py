"""Reviewed section-to-input mappings for FastAPI's nested-body tutorial."""

_PAGE = "tutorial/body-nested-models.md"
_RECIPE = "tests/fixtures/input-recipes/parity/docs-example-wave-f-nested-bodies.yaml"
_HTTP = ["http.body.bytes", "http.status"]
_BODY_SCHEMA = [
    "http.body.bytes",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.request_schema",
]


def _workflow(heading, start, end, case_id, request_action, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": _RECIPE,
        "case_ids": [case_id],
        "action_ids": [request_action, "openapi"],
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


_BODY_PIPELINE = (
    "FastAPI 0.157.0 selects form versus body handling and decides whether JSON "
    "parsing applies from the request content type in fastapi/routing.py:425-450; "
    "Starlette 1.6.0 Request.body() buffers the ASGI stream and Request.json() "
    "decodes JSON in starlette/requests.py:254-266. FastAPI validates a single "
    "non-embedded body field in "
    "fastapi/dependencies/utils.py:975-980, and projects request-body schemas in "
    "fastapi/openapi/utils.py:377-385. Starlette 1.6.0 owns generic ASGI dispatch and "
    "HTTP response transport; Pydantic supplies the declared model-field conversion "
    "and validation."
)


DOC_SECTION_CASE_MAPPINGS_BODY_NESTED_MODELS_20261015 = {
    (_PAGE, "body-nested-models"): _excluded(
        "Body - Nested Models { #body-nested-models }",
        1,
        221,
        (
            "This page heading summarizes multiple independently observable body shapes. "
            "Its concrete behavior is represented by the anchored list, nested-model, "
            "special-type, pure-list, and dictionary sections below."
        ),
        (
            "A page-wide input would merge unrelated Pydantic schemas and request bodies. "
            "Each child mapping selects its own request and schema observations; the two "
            "existing exclusions cover IDE-only assistance and recap prose."
        ),
    ),
    (_PAGE, "list-fields"): _workflow(
        "List fields { #list-fields }",
        5,
        12,
        "fastapi.docs-example-wave-f.nested-body.bare-list-values-preserved",
        "submit-heterogeneous-bare-list",
        _BODY_SCHEMA,
        (
            "The request sends mixed string, integer, and object values to a bare `list` "
            "field; the response and request-body/component schema are selected. The "
            "independent model uses the same primary field names but omits the tutorial's "
            "other Item fields and uses a different route."
        ),
        (
            "The pinned section embeds tutorial001's bare-list body field "
            "(docs_src/body_nested_models/tutorial001_py310.py:7-18). The fixture isolates "
            "unparameterized list acceptance/preservation and its OpenAPI schema. " + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "list-fields-with-type-parameter"): _workflow(
        "List fields with type parameter { #list-fields-with-type-parameter }",
        13,
        33,
        "fastapi.docs-example-wave-f.nested-body.list-tags-valid",
        "submit-typed-tag-list",
        _BODY_SCHEMA,
        (
            "The request submits string items to a `list[str]` field and selects its "
            "request-body schema. This checks the typed-list shape only; it does not claim "
            "the separate Python syntax examples as executable behavior."
        ),
        (
            "The section's executable example declares `tags: list[str]` "
            "(docs_src/body_nested_models/tutorial002_py310.py:7-18). The fixture observes "
            "accepted JSON values, serialized response, and the declared item schema. "
            + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "declare-a-list-with-a-type-parameter"): _workflow(
        "Declare a `list` with a type parameter { #declare-a-list-with-a-type-parameter }",
        17,
        33,
        "fastapi.docs-example-wave-f.nested-body.list-tags-valid",
        "submit-typed-tag-list",
        _BODY_SCHEMA,
        (
            "The same isolated typed-list request selects both runtime JSON handling and "
            "the `list[str]` request schema. The illustrative standalone annotation is "
            "not executed as an endpoint."
        ),
        (
            "The child section explains standard generic annotation syntax and embeds "
            "tutorial002's `list[str]` model field "
            "(docs_src/body_nested_models/tutorial002_py310.py:7-18). FastAPI's body "
            "binding/schema projection is covered by the selected request and OpenAPI "
            "actions; generic ASGI dispatch is Starlette 1.6.0 behavior."
        ),
    ),
    (_PAGE, "set-types"): _workflow(
        "Set types { #set-types }",
        34,
        49,
        "fastapi.docs-example-wave-f.nested-body.set-tags-deduplicated",
        "submit-unique-tag-set",
        _BODY_SCHEMA,
        (
            "The JSON input contains duplicate strings for a `set[str]` body field. The "
            "selected response checks de-duplication/serialization, and OpenAPI selects "
            "the declared field and request schema."
        ),
        (
            "The pinned tutorial003 example changes `tags` to `set[str]` and documents "
            "duplicate removal (docs_src/body_nested_models/tutorial003_py310.py:7-18). "
            "The independent input includes a duplicate and reads the resulting response "
            "and schema. " + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "nested-models"): _workflow(
        "Nested Models { #nested-models }",
        50,
        94,
        "fastapi.docs-example-wave-f.nested-body.optional-image-present",
        "submit-nested-image",
        _BODY_SCHEMA,
        (
            "The selected action submits one present nested image model and reads its "
            "OpenAPI body/component schema. It demonstrates one nesting level; recursive "
            "list nesting is isolated by the Deeply nested models section. Field names "
            "and tutorial example values differ."
        ),
        (
            "This section describes Pydantic submodels as fields and embeds "
            "tutorial004's Image and Item definitions "
            "(docs_src/body_nested_models/tutorial004_py310.py:7-24). The independent "
            "request samples successful nested-model parsing and schema projection. "
            + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "define-a-submodel"): _workflow(
        "Define a submodel { #define-a-submodel }",
        60,
        65,
        "fastapi.docs-example-wave-f.nested-body.optional-image-present",
        "submit-nested-image",
        _BODY_SCHEMA,
        (
            "The request contains a valid `ReviewImage` value and its OpenAPI component "
            "is selected. This observes a concrete nested model shape, not Python class "
            "editor behavior or the source tutorial's `url`/`name` field spelling."
        ),
        (
            "The section's source defines Image as a Pydantic model "
            "(docs_src/body_nested_models/tutorial004_py310.py:7-9). FastAPI uses the "
            "model as request metadata and projects it through OpenAPI; Pydantic performs "
            "field validation. " + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "use-the-submodel-as-a-type"): _workflow(
        "Use the submodel as a type { #use-the-submodel-as-a-type }",
        66,
        94,
        "fastapi.docs-example-wave-f.nested-body.optional-image-present",
        "submit-nested-image",
        _BODY_SCHEMA,
        (
            "The selected HTTP input carries an image object inside the body model and "
            "the schema selectors inspect the containing field and request schema. The "
            "fixture does not claim the source example's exact fields or every nested "
            "validation branch."
        ),
        (
            "The pinned endpoint annotates `Item.image` with the `Image` submodel "
            "(docs_src/body_nested_models/tutorial004_py310.py:12-24). This independent "
            "action samples binding of a nested object and its request schema. " + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "special-types-and-validation"): _workflow(
        "Special types and validation { #special-types-and-validation }",
        95,
        106,
        "fastapi.docs-example-wave-f.nested-body.http-url-invalid",
        "reject-invalid-image-url",
        _BODY_SCHEMA,
        (
            "The request sends a malformed URL to an `HttpUrl` nested field and selects "
            "the validation response plus its OpenAPI request/component schema. It does "
            "not attempt to cover Pydantic's full set of special types."
        ),
        (
            "Tutorial005 declares its nested `Image.url` as `HttpUrl` and says it is "
            "validated and documented (docs_src/body_nested_models/tutorial005_py310.py:1-24). "
            "The fixture isolates one invalid URL and the field's schema projection. "
            + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "attributes-with-lists-of-submodels"): _workflow(
        "Attributes with lists of submodels { #attributes-with-lists-of-submodels }",
        107,
        144,
        "fastapi.docs-example-wave-f.nested-body.optional-image-list-present",
        "submit-image-list",
        _BODY_SCHEMA,
        (
            "The body contains a non-empty list of nested image objects and selects the "
            "request schema for the containing list field. The tutorial's other model "
            "fields and exact image properties are outside this action."
        ),
        (
            "The section embeds tutorial006's optional list of Image models "
            "(docs_src/body_nested_models/tutorial006_py310.py:7-24). Its input observes "
            "list-of-submodel body validation/serialization and schema projection. "
            + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "deeply-nested-models"): _workflow(
        "Deeply nested models { #deeply-nested-models }",
        145,
        156,
        "fastapi.docs-example-wave-f.nested-body.offer-nested-items",
        "submit-offer-with-nested-line",
        _BODY_SCHEMA,
        (
            "The body contains an offer with nested lines and nested image lists, then "
            "selects the response and request schema. This samples the documented three "
            "model levels, with independent model names and values."
        ),
        (
            "The source example declares Offer, Item, and Image models at nested levels "
            "(docs_src/body_nested_models/tutorial007_py310.py:7-30). The fixture submits "
            "the recursive body shape and inspects its request schema. " + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "bodies-of-pure-lists"): _workflow(
        "Bodies of pure lists { #bodies-of-pure-lists }",
        157,
        168,
        "fastapi.docs-example-wave-f.nested-body.top-level-image-list",
        "submit-image-array",
        _BODY_SCHEMA,
        (
            "The request body is a top-level JSON array of image objects, not an object "
            "with a list field. The selected request-body schema distinguishes this shape."
        ),
        (
            "Tutorial008 annotates the endpoint parameter as `list[Image]` "
            "(docs_src/body_nested_models/tutorial008_py310.py:7-14). The fixture sends an "
            "array and selects FastAPI's request schema and response serialization. "
            + _BODY_PIPELINE
        ),
    ),
    (_PAGE, "bodies-of-arbitrary-dicts"): _workflow(
        "Bodies of arbitrary `dict`s { #bodies-of-arbitrary-dicts }",
        181,
        210,
        "fastapi.docs-example-wave-f.nested-body.integer-float-map-key-types",
        "probe-integer-dictionary-keys",
        _BODY_SCHEMA,
        (
            "The body sends numeric-string keys and decimal values to a `dict[int, float]` "
            "parameter. A diagnostic route checks membership using integer keys so the "
            "conversion is externally visible; OpenAPI selects the request schema. The "
            "probe does not exhaust arbitrary property-name populations."
        ),
        (
            "Tutorial009 annotates the body as `dict[int, float]` and explains conversion "
            "from JSON string keys (docs_src/body_nested_models/tutorial009_py310.py:6-8; "
            "docs/en/docs/tutorial/body-nested-models.md:181-210). The source endpoint's "
            "ordinary JSON dictionary serialization cannot reveal whether its in-process "
            "keys are integers, so the input recipe uses a probe endpoint that evaluates "
            "integer-key membership and returns that boolean. It still uses FastAPI's "
            "annotated body binding and OpenAPI schema projection. " + _BODY_PIPELINE
        ),
    ),
}
