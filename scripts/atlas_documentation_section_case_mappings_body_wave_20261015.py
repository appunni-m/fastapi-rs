"""Reviewed documentation section mappings for request bodies and binary data."""

_BODY_MULTI_PAGE = "tutorial/body-multiple-params.md"
_BODY_UPDATES_PAGE = "tutorial/body-updates.md"
_DATACLASSES_PAGE = "advanced/dataclasses.md"
_JSON_BYTES_PAGE = "advanced/json-base64-bytes.md"

_BODY_MULTI_RECIPE = (
    "tests/fixtures/input-recipes/parity/body-multiple-params-section-review-20261015.yaml"
)
_BODY_UPDATES_RECIPE = "tests/fixtures/input-recipes/parity/body-updates-page-review-20261015.yaml"
_BODY_SURFACE_RECIPE = "tests/fixtures/input-recipes/parity/body-surface.yaml"
_DATACLASSES_RECIPE = "tests/fixtures/input-recipes/parity/dataclasses.yaml"
_DATACLASS_REQUEST_RECIPE = (
    "tests/fixtures/input-recipes/parity/docs-example-dataclass-request-wave-g.yaml"
)
_JSON_BYTES_RECIPE = "tests/fixtures/input-recipes/parity/json_base64_bytes.yaml"

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_ASGI = [
    "asgi.send.message_types",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
]
_HTTP_OPENAPI_BODY = [
    "http.body.bytes",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.request_schema",
]
_DATACLASS_RESPONSE_OPENAPI = [
    "docs.response.body.bytes",
    "docs.response.headers",
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
]
_DATACLASS_REQUEST_RESPONSE_SCHEMA = [
    "http.body.bytes",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_JSON_BYTES_BASE64_INPUT_SCHEMA = [
    "docs.response.body.bytes",
    "docs.response.headers",
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
]
_JSON_BYTES_ALL = _JSON_BYTES_BASE64_INPUT_SCHEMA


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
    mapping = {
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
        mapping["action_ids"] = actions
    return mapping


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_BODY_BINDING_RATIONALE = (
    "FastAPI 0.141.1 classifies path parameters, non-scalar body parameters, and scalar query "
    "parameters in fastapi/dependencies/utils.py:491-505. It embeds body fields when more "
    "than one body parameter is declared or when Body(embed=True) is explicit at :888-909; "
    "request_body_to_args extracts keyed fields and validates them at :951-998. OpenAPI "
    "requestBody generation is in fastapi/openapi/utils.py:377-385. The independent recipes "
    "use changed paths and values. Pydantic supplies model validation; Starlette 1.6.0 owns "
    "generic ASGI dispatch and Request body/JSON handling (starlette/requests.py:254-266)."
)

_BODY_UPDATES_RATIONALE = (
    "The pinned docs examples are docs_src/body_updates/tutorial001_py310.py:28-32 and "
    "tutorial002_py310.py:28-35. The independent StockRecord workload uses different field "
    "names, values, and a different route. FastAPI 0.141.1 reads JSON request bodies and "
    "passes parsed values into request validation (fastapi/routing.py:425-450; "
    "fastapi/dependencies/utils.py:951-998), then validates/serializes an annotated response "
    "field (fastapi/routing.py:301-342). The exclude_unset/model_copy update policy is the "
    "Pydantic and endpoint-authored behavior shown by the tutorial, not a FastAPI update "
    "operation. Starlette 1.6.0 owns Request.body()/json() and generic ASGI transport "
    "(starlette/requests.py:254-266)."
)

_DATACLASSES_RATIONALE = (
    "FastAPI 0.141.1 creates a Pydantic-backed ModelField from the declared response type "
    "in fastapi/utils.py:58-77. APIRoute creates the response field for the declared type "
    "in fastapi/routing.py:1081-1112 and validates/serializes response content through that "
    "field in fastapi/routing.py:301-342. The recipe uses a standard-library dataclass as "
    "response_model and inspects its emitted OpenAPI component; Pydantic supplies dataclass "
    "validation and serialization. Starlette 1.6.0 owns generic response transport."
)

_DATACLASS_REQUEST_RATIONALE = (
    "The pinned tutorial example declares a standard-library Item dataclass as a path "
    "operation parameter and returns it (docs_src/dataclasses_/tutorial001_py310.py:1-19). "
    "FastAPI 0.141.1 constructs APIRoute dependency and body-field state in "
    "fastapi/routing.py:1081-1112, parses request JSON at fastapi/routing.py:425-450, and "
    "classifies/validates body fields in fastapi/dependencies/utils.py:491-505,951-998. "
    "The independent Entry workload changes the route and values while preserving the "
    "standard-dataclass request shape; it observes the exact response and selected operation "
    "OpenAPI path. Pydantic supplies dataclass validation. Starlette 1.6.0 owns generic ASGI "
    "routing and response transport."
)

_JSON_BYTES_RATIONALE = (
    "The pinned documentation's example is docs_src/json_base64_bytes/tutorial001_py310.py. "
    "Its val_json_bytes and ser_json_bytes configuration is Pydantic behavior. FastAPI "
    "0.141.1 reads JSON request bodies and supplies parsed input to model validation "
    "(fastapi/routing.py:425-450), returns model data through response serialization "
    "(fastapi/routing.py:301-342), and emits request/response schemas in OpenAPI "
    "(fastapi/openapi/utils.py:377-385). Starlette 1.6.0 owns the Request body/JSON "
    "methods and generic HTTP transport (starlette/requests.py:254-266). The independent "
    "workload uses different payloads and endpoint paths."
)


DOC_SECTION_CASE_MAPPINGS_BODY_WAVE_20261015 = {
    (_BODY_MULTI_PAGE, "body-multiple-parameters"): _excluded(
        "Body - Multiple Parameters { #body-multiple-parameters }",
        1,
        169,
        (
            "The page-level title and recap span several distinct request-body shapes; each "
            "executable child is mapped independently."
        ),
        (
            "Pinned source docs/en/docs/tutorial/body-multiple-params.md:1-169. The page "
            "contains separate Path/Query/body, multiple-body, scalar-Body, query-plus-body, "
            "and embed sections. The child mappings below select those inputs separately."
        ),
    ),
    (_BODY_MULTI_PAGE, "mix-path-query-and-body-parameters"): _workflow(
        "Mix `Path`, `Query` and body parameters { #mix-path-query-and-body-parameters }",
        5,
        18,
        _BODY_SURFACE_RECIPE,
        ["fastapi.body.optional-model-absent", "fastapi.body.optional-model-present"],
        ["dispatch"],
        _HTTP_ASGI,
        (
            "The two requests combine a path identifier and query value with an optional "
            "single-model body, once absent and once present. This samples that combination "
            "only; it does not establish multiple body fields or every parameter source."
        ),
        _BODY_BINDING_RATIONALE,
    ),
    (_BODY_MULTI_PAGE, "multiple-body-parameters"): _workflow(
        "Multiple body parameters { #multiple-body-parameters }",
        19,
        65,
        _BODY_MULTI_RECIPE,
        ["fastapi.docs.body-multiple-params-section-review.two-models"],
        ["submit-two-model-body", "inspect-two-model-request-schema"],
        _HTTP_OPENAPI_BODY,
        (
            "The independent PUT submits two required Pydantic models under separate body "
            "keys and inspects the request schema. It samples keyed extraction, model results, "
            "and schema shape with different route names and values; it does not cover all "
            "validation branches or the tutorial's exact example literals."
        ),
        _BODY_BINDING_RATIONALE,
    ),
    (_BODY_MULTI_PAGE, "singular-values-in-body"): _workflow(
        "Singular values in body { #singular-values-in-body }",
        66,
        98,
        _BODY_SURFACE_RECIPE,
        ["fastapi.body.multiple-values-valid", "fastapi.body.multiple-values-invalid"],
        ["dispatch"],
        _HTTP_ASGI,
        (
            "The requests pair one Pydantic model body with a scalar `priority` field "
            "explicitly declared with Body(gt=0), sampling a valid and a rejected value. "
            "They do not combine two models or exercise query parameter extraction."
        ),
        _BODY_BINDING_RATIONALE,
    ),
    (_BODY_MULTI_PAGE, "multiple-body-params-and-query"): _workflow(
        "Multiple body params and query { #multiple-body-params-and-query }",
        99,
        119,
        _BODY_MULTI_RECIPE,
        ["fastapi.docs.body-multiple-params-section-review.body-and-query"],
        ["submit-body-with-query", "inspect-body-with-query-openapi"],
        _HTTP_OPENAPI_BODY,
        (
            "The independent PUT combines a path identifier, two model body keys, a scalar "
            "Body value, and an optional query parameter; its OpenAPI action inspects request "
            "body schema and parameter metadata. It samples one valid request and does not "
            "cover missing/invalid query or body branches."
        ),
        _BODY_BINDING_RATIONALE,
    ),
    (_BODY_MULTI_PAGE, "embed-a-single-body-parameter"): _workflow(
        "Embed a single body parameter { #embed-a-single-body-parameter }",
        120,
        160,
        _BODY_MULTI_RECIPE,
        ["fastapi.docs.body-multiple-params-section-review.embedded-model"],
        ["submit-embedded-model", "inspect-embedded-model-request-schema"],
        _HTTP_OPENAPI_BODY,
        (
            "The independent PUT submits one model under its explicitly embedded `item` key "
            "and inspects the resulting request schema. Its path and values differ from the "
            "tutorial and it does not compare the unembedded alternative in the same action."
        ),
        _BODY_BINDING_RATIONALE,
    ),
    (_BODY_MULTI_PAGE, "recap"): _excluded(
        "Recap { #recap }",
        161,
        169,
        (
            "The recap summarizes the previously mapped parameter and embedding behaviors "
            "without introducing another executable example."
        ),
        (
            "Pinned source docs/en/docs/tutorial/body-multiple-params.md:161-169 restates "
            "multiple body fields, scalar Body, and embedding. Those concrete claims are "
            "linked to their individual child section inputs above."
        ),
    ),
    (_BODY_UPDATES_PAGE, "body-updates"): _excluded(
        "Body - Updates { #body-updates }",
        1,
        100,
        (
            "The title and page recap combine full replacement with several endpoint-authored "
            "partial-update steps; child sections are reviewed separately."
        ),
        (
            "Pinned source docs/en/docs/tutorial/body-updates.md:1-100 presents PUT replacement, "
            "PATCH, Pydantic's exclude_unset/model_copy methods, and persistence guidance as "
            "separate topics. The child section mappings select the runtime requests."
        ),
    ),
    (_BODY_UPDATES_PAGE, "update-replacing-with-put"): _workflow(
        "Update replacing with `PUT` { #update-replacing-with-put }",
        3,
        28,
        _BODY_UPDATES_RECIPE,
        ["fastapi.docs.body-updates-page-review.put-replaces-omitted-fields"],
        ["replace-independent-record"],
        ["http.body.bytes", "http.status"],
        (
            "A PUT with a partial independent record payload returns the replaced record, "
            "including model defaults for omitted fields. The in-memory route and record "
            "fields differ from the tutorial and do not model a database."
        ),
        _BODY_UPDATES_RATIONALE,
    ),
    (_BODY_UPDATES_PAGE, "warning-about-replacing"): _workflow(
        "Warning about replacing { #warning-about-replacing }",
        13,
        28,
        _BODY_UPDATES_RECIPE,
        ["fastapi.docs.body-updates-page-review.put-replaces-omitted-fields"],
        ["replace-independent-record"],
        ["http.body.bytes", "http.status"],
        (
            "The seeded stored record has values different from the StockRecord defaults. "
            "The PUT request omits those fields and its response exposes replacement with "
            "defaults; it samples this consequence for one independent record only."
        ),
        _BODY_UPDATES_RATIONALE,
    ),
    (_BODY_UPDATES_PAGE, "partial-updates-with-patch"): _workflow(
        "Partial updates with `PATCH` { #partial-updates-with-patch }",
        29,
        100,
        _BODY_UPDATES_RECIPE,
        [
            "fastapi.docs.body-updates-page-review.patch-preserves-omitted-fields",
            "fastapi.docs.body-updates-page-review.patch-applies-explicit-null",
        ],
        None,
        ["http.body.bytes", "http.status"],
        (
            "The independent PATCH requests sample preserving stored values omitted from an "
            "input and applying an explicit null. The workload uses an in-memory record, not "
            "external persistence, and only these two update shapes."
        ),
        _BODY_UPDATES_RATIONALE,
    ),
    (_BODY_UPDATES_PAGE, "using-pydantics-exclude-unset-parameter"): _workflow(
        "Using Pydantic's `exclude_unset` parameter { #using-pydantics-exclude-unset-parameter }",
        47,
        58,
        _BODY_UPDATES_RECIPE,
        [
            "fastapi.docs.body-updates-page-review.patch-preserves-omitted-fields",
            "fastapi.docs.body-updates-page-review.patch-applies-explicit-null",
        ],
        None,
        ["http.body.bytes", "http.status"],
        (
            "The endpoint applies model_dump(exclude_unset=True) to distinguish omitted fields "
            "from an explicitly supplied null. The two responses expose one preserved and one "
            "explicit-null outcome; this is Pydantic/endpoint logic."
        ),
        _BODY_UPDATES_RATIONALE,
    ),
    (_BODY_UPDATES_PAGE, "using-pydantics-update-parameter"): _workflow(
        "Using Pydantic's `update` parameter { #using-pydantics-update-parameter }",
        59,
        66,
        _BODY_UPDATES_RECIPE,
        [
            "fastapi.docs.body-updates-page-review.patch-preserves-omitted-fields",
            "fastapi.docs.body-updates-page-review.patch-applies-explicit-null",
        ],
        None,
        ["http.body.bytes", "http.status"],
        (
            "The workload passes explicitly supplied values into model_copy(update=...). The "
            "responses sample a field replacement and explicit null; they do not establish "
            "all Pydantic copy semantics."
        ),
        _BODY_UPDATES_RATIONALE,
    ),
    (_BODY_UPDATES_PAGE, "partial-updates-recap"): _workflow(
        "Partial updates recap { #partial-updates-recap }",
        67,
        100,
        _BODY_UPDATES_RECIPE,
        [
            "fastapi.docs.body-updates-page-review.patch-preserves-omitted-fields",
            "fastapi.docs.body-updates-page-review.patch-applies-explicit-null",
        ],
        None,
        ["http.body.bytes", "http.status"],
        (
            "The two PATCH actions cover a preserved omitted field and an explicit null in "
            "the endpoint's in-memory read/merge/return path. They do not cover external "
            "storage, database conversion, or every optional-model shape listed in the recap."
        ),
        _BODY_UPDATES_RATIONALE,
    ),
    (_DATACLASSES_PAGE, "using-dataclasses"): _workflow(
        "Using Dataclasses { #using-dataclasses }",
        1,
        95,
        _DATACLASS_REQUEST_RECIPE,
        ["fastapi.docs-wave-g.dataclasses.stdlib-request-and-return"],
        ["parse-and-return-independent-dataclass", "inspect-independent-dataclass-openapi"],
        _DATACLASS_REQUEST_RESPONSE_SCHEMA,
        (
            "The workflow maps the standard-library Item request/return example embedded at "
            "lines 5-13: its independent Entry route observes exact response bytes and the "
            "POST operation object through a JSON Pointer in the OpenAPI document. The separate "
            "response_model child remains separately "
            "mapped; nested dataclass structures and external Pydantic guidance remain "
            "excluded below."
        ),
        _DATACLASS_REQUEST_RATIONALE,
    ),
    (_DATACLASSES_PAGE, "dataclasses-in-response-model"): _workflow(
        "Dataclasses in `response_model` { #dataclasses-in-response-model }",
        31,
        42,
        _DATACLASSES_RECIPE,
        ["fastapi.docs.dataclasses.response-model-and-openapi"],
        ["dataclass-response", "dataclass-openapi"],
        _DATACLASS_RESPONSE_OPENAPI,
        (
            "The response action returns a standard-library Item dataclass through "
            "response_model, and the OpenAPI action selects that component schema. The "
            "fixture does not test browser rendering of the UI screenshot."
        ),
        _DATACLASSES_RATIONALE,
    ),
    (_DATACLASSES_PAGE, "dataclasses-in-nested-data-structures"): _excluded(
        "Dataclasses in Nested Data Structures { #dataclasses-in-nested-data-structures }",
        43,
        86,
        (
            "No exact page-evidence workflow in this bounded wave samples the nested "
            "request/response and schema combinations described here."
        ),
        (
            "The pinned tutorial003 example at docs_src/dataclasses_/tutorial003_py310.py "
            "uses Pydantic dataclasses for nested Author/Item structures, a list request body, "
            "and multiple response annotations. The page-mapped dataclasses recipe covers "
            "only the simple tutorial002 response_model case; a separate page-evidence input "
            "is needed to map the nested shapes."
        ),
    ),
    (_DATACLASSES_PAGE, "learn-more"): _excluded(
        "Learn More { #learn-more }",
        87,
        92,
        (
            "The section points to Pydantic's external dataclass documentation and makes no "
            "separate FastAPI request or response claim."
        ),
        (
            "Pinned docs/en/docs/advanced/dataclasses.md:87-92 links to Pydantic documentation "
            "for additional dataclass combinations. External Pydantic guidance is outside this "
            "page's FastAPI input workflow."
        ),
    ),
    (_DATACLASSES_PAGE, "version"): _excluded(
        "Version { #version }",
        93,
        95,
        (
            "The section states a historical introduction version and does not select current "
            "runtime behavior."
        ),
        (
            "Pinned docs/en/docs/advanced/dataclasses.md:93-95 states availability since "
            "FastAPI 0.67.0. This is release-history prose rather than a request, response, or "
            "OpenAPI input for the pinned 0.141.1 contract."
        ),
    ),
    (_JSON_BYTES_PAGE, "json-with-bytes-as-base64"): _excluded(
        "JSON with Bytes as Base64 { #json-with-bytes-as-base64 }",
        1,
        63,
        (
            "This H1 page container spans base64/file guidance and separate input/output "
            "cases; each executable bytes behavior is mapped on its child section."
        ),
        (
            "Pinned docs/en/docs/advanced/json-base64-bytes.md:1-63 includes the base64 overview, "
            "file-versus-base64 advice, input validation, output serialization, and a combined "
            "input/output model. The child sections map the request and response workflows "
            "independently, while the file tradeoff is excluded below."
        ),
    ),
    (_JSON_BYTES_PAGE, "base64-vs-files"): _excluded(
        "Base64 vs Files { #base64-vs-files }",
        5,
        14,
        (
            "This section compares transport choices and gives efficiency guidance; it does "
            "not define an executable FastAPI behavior."
        ),
        (
            "Pinned docs/en/docs/advanced/json-base64-bytes.md:5-14 recommends considering "
            "Request Files and FileResponse and describes JSON/base64 size tradeoffs. File "
            "transport is a separate feature, and the text selects no request or response "
            "input for the base64 workflow."
        ),
    ),
    (_JSON_BYTES_PAGE, "pydantic-bytes"): _workflow(
        "Pydantic `bytes` { #pydantic-bytes }",
        15,
        52,
        _JSON_BYTES_RECIPE,
        ["fastapi.docs.json-base64-bytes.input-output-and-schema"],
        ["decode-base64-input", "base64-openapi"],
        _JSON_BYTES_BASE64_INPUT_SCHEMA,
        (
            "The POST decodes one base64 JSON input into bytes and returns decoded text; the "
            "OpenAPI action selects the DataInput bytes field schema. It does not exercise "
            "Swagger UI rendering or every malformed-base64 input."
        ),
        _JSON_BYTES_RATIONALE,
    ),
    (_JSON_BYTES_PAGE, "pydantic-bytes-for-output-data"): _workflow(
        "Pydantic `bytes` for Output Data { #pydantic-bytes-for-output-data }",
        53,
        58,
        _JSON_BYTES_RECIPE,
        ["fastapi.docs.json-base64-bytes.input-output-and-schema"],
        ["encode-base64-output"],
        _HTTP,
        (
            "The GET returns one bytes field configured for base64 JSON serialization. It "
            "samples response encoding only, with independent values; request validation and "
            "other serializer configurations are outside this action."
        ),
        _JSON_BYTES_RATIONALE,
    ),
    (_JSON_BYTES_PAGE, "pydantic-bytes-for-input-and-output-data"): _workflow(
        "Pydantic `bytes` for Input and Output Data { #pydantic-bytes-for-input-and-output-data }",
        59,
        63,
        _JSON_BYTES_RECIPE,
        ["fastapi.docs.json-base64-bytes.input-output-and-schema"],
        ["roundtrip-base64"],
        _HTTP,
        (
            "The POST accepts one base64-encoded bytes field and returns the same model using "
            "base64 serialization. It samples one valid round trip and not separate validation "
            "and serializer edge cases."
        ),
        _JSON_BYTES_RATIONALE,
    ),
}
