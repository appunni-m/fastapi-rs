"""Reviewed section mappings for OpenAPI schema tutorials and guides."""

_SCHEMA_PAGE = "tutorial/schema-extra-example.md"
_SCHEMA_RECIPE = "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml"
_SPLIT_PAGE = "how-to/separate-openapi-schemas.md"
_SPLIT_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-schema-modes-interface-review.yaml"
)
_EXTEND_PAGE = "how-to/extending-openapi.md"
_EXTEND_RECIPE = "tests/fixtures/input-recipes/parity/docs-openapi-extending-openapi-20261015.yaml"


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
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


_SCHEMA_COMPONENT_SELECTORS = [
    "docs.response.status",
    "http.status",
    "openapi.document",
]
_BODY_SCHEMA_SELECTORS = [
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.request_schema",
]
_NAMED_EXAMPLES_SELECTORS = [
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_MODE_DOCUMENT_SELECTORS = ["http.status", "openapi.document"]
_MODE_HTTP_DOCUMENT_SELECTORS = ["http.body.bytes", "http.status", "openapi.document"]
_EXTEND_SELECTORS = [
    "construction.exception_class",
    "construction.exception_message",
    "construction.outcome",
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
]


_SCHEMA_COMPONENT_RATIONALE = (
    "The pinned page embeds the named model example. FastAPI 0.141.1 gathers route fields, "
    "builds model definitions, and returns the assembled OpenAPI document in "
    "fastapi/openapi/utils.py:585-679; Pydantic supplies JSON Schema field generation."
)
_BODY_RATIONALE = (
    "The pinned page embeds this Body example. FastAPI 0.141.1 projects the body field and "
    "its JSON Schema in fastapi/openapi/utils.py:231-263 and :377-385; the selected JSON "
    "pointers are request-body schemas, not parameter-location or browser observations."
)
_MODE_RATIONALE = (
    "The pinned page describes validation-mode input schemas and serialization-mode output "
    "schemas for a model with a default. FastAPI 0.141.1 passes "
    "separate_input_output_schemas through fastapi/applications.py:780-814, :890, and "
    ":1090-1101 into OpenAPI generation at fastapi/openapi/utils.py:585-679. On the pinned "
    "FastAPI 0.141.1/Pydantic 2.13.4 observation, both `/split/openapi.json` and "
    "`/shared/openapi.json` contain one `Record` component with `label` required; neither "
    "shows a `Record-Input`/`Record-Output` pair. These cases observe the configured modes, "
    "requests, responses, and documents, but do not demonstrate distinct input/output schema "
    "components or distinct schemas for this model. The fixture uses `Record.summary` instead "
    "of the source example's `Item.description`; Pydantic owns model-field schema generation "
    "and Starlette 1.6.0 owns generic ASGI/HTTP."
)
_EXTEND_RATIONALE = (
    "The pinned page describes FastAPI's app.openapi() method, its generated-schema cache, "
    "and get_openapi(). FastAPI 0.141.1 implements the default method and /openapi.json "
    "route in fastapi/applications.py:1070-1120 and assembles info, paths, and schemas in "
    "fastapi/openapi/utils.py:585-679. Starlette 1.6.0 owns generic route dispatch and HTTP "
    "transport; ReDoc/Swagger UI rendering is outside these ASGI observations."
)


DOC_SECTION_CASE_MAPPINGS_OPENAPI_SCHEMA_20261015 = {
    (_SCHEMA_PAGE, "declare-request-example-data"): _excluded(
        "Declare Request Example Data { #declare-request-example-data }",
        1,
        202,
        (
            "This page title aggregates model examples, request-body examples, and an "
            "OpenAPI-specific examples option; each concrete behavior has its own child "
            "section mapping."
        ),
        (
            "A page-wide case would combine model components, request-body schemas, and "
            "Media Type examples. The child sections select each observed OpenAPI pointer "
            "separately, while the standards-history and recap sections are scoped below."
        ),
    ),
    (_SCHEMA_PAGE, "extra-json-schema-data-in-pydantic-models"): _workflow(
        "Extra JSON Schema data in Pydantic models { #extra-json-schema-data-in-pydantic-models }",
        7,
        36,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.model-schema-extra"],
        ["model-config-openapi"],
        _SCHEMA_COMPONENT_SELECTORS,
        (
            "The selected OpenAPI action inspects the `ConfigExampleRecord` component that "
            "carries model-level `json_schema_extra`. It does not claim arbitrary extra "
            "metadata or Pydantic configuration behavior beyond this component."
        ),
        _SCHEMA_COMPONENT_RATIONALE,
    ),
    (_SCHEMA_PAGE, "field-additional-arguments"): _workflow(
        "`Field` additional arguments { #field-additional-arguments }",
        37,
        42,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.field-examples"],
        ["field-examples-openapi"],
        _SCHEMA_COMPONENT_SELECTORS,
        (
            "The selected OpenAPI action inspects the `FieldExamplesRecord` component for "
            "the declared field examples. It does not claim validation effects or every "
            "`Field` option."
        ),
        (
            "The pinned section embeds the Pydantic `Field` example. FastAPI 0.141.1 gathers "
            "the route's model definitions for OpenAPI in fastapi/openapi/utils.py:620-679; "
            "Pydantic supplies the field JSON Schema content."
        ),
    ),
    (_SCHEMA_PAGE, "examples-in-json-schema-openapi"): _workflow(
        "`examples` in JSON Schema - OpenAPI { #examples-in-json-schema-openapi }",
        43,
        121,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.body-examples-list"],
        ["body-examples-openapi"],
        _BODY_SCHEMA_SELECTORS,
        (
            "This case samples `Body(examples=...)` and its request-body JSON Schema only. "
            "It does not sample the separately listed Path, Query, Header, Cookie, Form, or "
            "File locations; multiple Body examples and OpenAPI-specific examples are "
            "mapped in child sections."
        ),
        _BODY_RATIONALE,
    ),
    (_SCHEMA_PAGE, "body-with-examples"): _workflow(
        "`Body` with `examples` { #body-with-examples }",
        57,
        62,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.body-examples-list"],
        ["body-examples-openapi"],
        _BODY_SCHEMA_SELECTORS,
        (
            "The selected pointers are the default and annotated Body request schemas. The "
            "input does not run the docs UI or claim non-Body parameter locations."
        ),
        _BODY_RATIONALE,
    ),
    (_SCHEMA_PAGE, "example-in-the-docs-ui"): _workflow(
        "Example in the docs UI { #example-in-the-docs-ui }",
        63,
        68,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.body-examples-list"],
        ["body-examples-openapi"],
        _BODY_SCHEMA_SELECTORS,
        (
            "This selects the generated Body schema used as input to the documentation "
            "interface. It does not render Swagger UI or compare the screenshot."
        ),
        (
            "FastAPI 0.141.1 serves generated schema data through its OpenAPI endpoint "
            "(fastapi/applications.py:1105-1120); the selected request-schema pointers carry "
            "the example field. Starlette 1.6.0 owns HTTP transport and Swagger UI is an "
            "external browser renderer."
        ),
    ),
    (_SCHEMA_PAGE, "body-with-multiple-examples"): _workflow(
        "`Body` with multiple `examples` { #body-with-multiple-examples }",
        69,
        78,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.body-examples-several"],
        ["several-examples-openapi"],
        _BODY_SCHEMA_SELECTORS,
        (
            "The selected pointers inspect the default and annotated routes' Body JSON "
            "Schemas containing multiple examples. Swagger UI display of those JSON Schema "
            "examples is not observed."
        ),
        _BODY_RATIONALE,
    ),
    (_SCHEMA_PAGE, "openapi-specific-examples"): _workflow(
        "OpenAPI-specific `examples` { #openapi-specific-examples }",
        79,
        90,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.openapi-example-objects"],
        ["named-examples-openapi"],
        _NAMED_EXAMPLES_SELECTORS,
        (
            "The selected operation pointers inspect named OpenAPI Media Type `examples` "
            "for `Body`, outside the request JSON Schema. Although the page lists Path, "
            "Query, Header, Cookie, Form, and File too, those locations and the rendered UI "
            "are not covered by this case."
        ),
        (
            "FastAPI 0.141.1 puts `openapi_examples` on the request Media Type at "
            "fastapi/openapi/utils.py:249-263. The selected pointer is the operation's "
            "Media Type examples object, not its JSON Schema."
        ),
    ),
    (_SCHEMA_PAGE, "openapi-examples-in-the-docs-ui"): _workflow(
        "OpenAPI Examples in the Docs UI { #openapi-examples-in-the-docs-ui }",
        116,
        121,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.openapi-example-objects"],
        ["named-examples-openapi"],
        _NAMED_EXAMPLES_SELECTORS,
        (
            "The OpenAPI action selects named Media Type examples configured on `Body`; the "
            "other listed Path, Query, Header, Cookie, Form, and File locations are not "
            "sampled. It does not launch Swagger UI or verify its visual rendering."
        ),
        (
            "FastAPI 0.141.1 emits the OpenAPI-specific examples into the request Media Type "
            "at fastapi/openapi/utils.py:249-263. The docs page describes their UI use, but "
            "the independent action observes only the generated document."
        ),
    ),
    (_SCHEMA_PAGE, "technical-details"): _excluded(
        "Technical Details { #technical-details }",
        122,
        202,
        (
            "This parent is a standards and version-history discussion. Its current concrete "
            "model and request-example behavior is mapped under the anchored child sections; "
            "pre-0.99/0.103 FastAPI behavior and Swagger UI version claims are outside the "
            "pinned 0.141.1 contract."
        ),
        (
            "FastAPI 0.141.1 generates OpenAPI 3.1.0 documents and its current examples are "
            "mapped in the child rows. This exclusion does not exclude those child inputs or "
            "claim historical compatibility."
        ),
    ),
    (_SCHEMA_PAGE, "json-schemas-examples-field"): _workflow(
        "JSON Schema's `examples` field { #json-schemas-examples-field }",
        164,
        181,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.body-examples-several"],
        ["several-examples-openapi"],
        _BODY_SCHEMA_SELECTORS,
        (
            "The selected Body request-schema pointers sample the JSON Schema `examples` "
            "list. They do not inspect OpenAPI Media Type examples or assert standards "
            "history."
        ),
        _BODY_RATIONALE,
    ),
    (_SCHEMA_PAGE, "pydantic-and-fastapi-examples"): _workflow(
        "Pydantic and FastAPI `examples` { #pydantic-and-fastapi-examples }",
        182,
        191,
        _SCHEMA_RECIPE,
        [
            "fastapi.schema-extra-example.model-schema-extra",
            "fastapi.schema-extra-example.field-examples",
        ],
        None,
        _SCHEMA_COMPONENT_SELECTORS,
        (
            "The selected component pointers cover one model-level `json_schema_extra` "
            "component and one Pydantic Field examples component. Body examples and the UI "
            "are covered separately; this does not claim every Pydantic schema option."
        ),
        (
            "The pinned section distinguishes model-config extras from `Field(examples=...)`. "
            "FastAPI 0.141.1 gathers both models into the OpenAPI definitions at "
            "fastapi/openapi/utils.py:620-679; Pydantic generates their field schemas."
        ),
    ),
    (_SCHEMA_PAGE, "swagger-ui-and-openapi-specific-examples"): _workflow(
        "Swagger UI and OpenAPI-specific `examples` { #swagger-ui-and-openapi-specific-examples }",
        192,
        197,
        _SCHEMA_RECIPE,
        ["fastapi.schema-extra-example.openapi-example-objects"],
        ["named-examples-openapi"],
        _NAMED_EXAMPLES_SELECTORS,
        (
            "This action selects named OpenAPI Media Type examples attached to `Body`, which "
            "differ from Body JSON Schema examples. It does not sample Path, Query, Header, "
            "Cookie, Form, or File, render Swagger UI, or claim UI behavior for every frontend "
            "version."
        ),
        (
            "FastAPI 0.141.1 emits `openapi_examples` at the request Media Type in "
            "fastapi/openapi/utils.py:249-263. Swagger UI is a separate browser renderer; "
            "only the generated OpenAPI document is observed."
        ),
    ),
    (_SCHEMA_PAGE, "summary"): _excluded(
        "Summary { #summary }",
        198,
        202,
        (
            "The section is a recap and upgrade recommendation, with no distinct endpoint "
            "input or schema option."
        ),
        (
            "The current FastAPI 0.141.1 model, Body, and OpenAPI-specific examples are "
            "mapped above; this recap adds only historical version advice."
        ),
    ),
    (_SPLIT_PAGE, "separate-openapi-schemas-for-input-and-output-or-not"): _excluded(
        (
            "Separate OpenAPI Schemas for Input and Output or Not { "
            "#separate-openapi-schemas-for-input-and-output-or-not }"
        ),
        1,
        102,
        (
            "The title combines the default separate-schema example and the opt-out example, "
            "which are independently mapped to inputs with each option value below."
        ),
        (
            "FastAPI passes the schema-mode option to its OpenAPI generator; child mappings "
            "select requests, responses, and documents produced with each option value. On "
            "the pinned FastAPI/Pydantic versions, both fixture documents contain one `Record` "
            "component, so this input does not demonstrate distinct split and shared schema "
            "components."
        ),
    ),
    (_SPLIT_PAGE, "pydantic-models-for-input-and-output"): _workflow(
        "Pydantic Models for Input and Output { #pydantic-models-for-input-and-output }",
        9,
        79,
        _SPLIT_RECIPE,
        [
            "fastapi.atlas-openapi-tutorial.split-schema-create",
            "fastapi.atlas-openapi-tutorial.split-schema-list",
            "fastapi.atlas-openapi-tutorial.split-schema-document",
        ],
        None,
        _MODE_HTTP_DOCUMENT_SELECTORS,
        (
            "These cases submit a model input, serialize a model output with a default, and "
            "select the document with separate input/output schemas enabled. In the exact-pin "
            "observation, that document has one `Record` component with only `label` required; "
            "a distinct input/output pair is not demonstrated. The fixture uses `Record.summary` "
            "rather than the page's `Item.description` and does not cover every model/default "
            "combination."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "model-for-input"): _workflow(
        "Model for Input { #model-for-input }",
        15,
        22,
        _SPLIT_RECIPE,
        [
            "fastapi.atlas-openapi-tutorial.split-schema-create",
            "fastapi.atlas-openapi-tutorial.split-schema-document",
        ],
        None,
        _MODE_HTTP_DOCUMENT_SELECTORS,
        (
            "The POST accepts `Record` with its optional `summary` omitted, and the selected "
            "document with separate input/output schemas enabled. That document still has one "
            "`Record` component, so this does not demonstrate a distinct input component. The "
            "fixture uses a different field name from the page and does not enumerate other "
            "accepted inputs."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "input-model-in-docs"): _workflow(
        "Input Model in Docs { #input-model-in-docs }",
        23,
        30,
        _SPLIT_RECIPE,
        ["fastapi.atlas-openapi-tutorial.split-schema-document"],
        ["inspect-split-schema-document"],
        _MODE_DOCUMENT_SELECTORS,
        (
            "The OpenAPI action selects the document generated with separate input/output "
            "schemas enabled; it contains one `Record` component on these pins, not a "
            "demonstrated input/output pair. It does not render Swagger UI or reproduce the "
            "screenshot's red asterisk."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "model-for-output"): _workflow(
        "Model for Output { #model-for-output }",
        31,
        38,
        _SPLIT_RECIPE,
        [
            "fastapi.atlas-openapi-tutorial.split-schema-list",
            "fastapi.atlas-openapi-tutorial.split-schema-document",
        ],
        None,
        _MODE_HTTP_DOCUMENT_SELECTORS,
        (
            "The GET returns two independent `Record` values and selects the OpenAPI document "
            "generated with separate input/output schemas enabled. That document has one "
            "`Record` component, so a distinct output schema is not demonstrated. The fixture's "
            "`summary` field and route differ from the tutorial, and its application response "
            "values are fixture-owned."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "model-for-output-response-data"): _workflow(
        "Model for Output Response Data { #model-for-output-response-data }",
        39,
        57,
        _SPLIT_RECIPE,
        ["fastapi.atlas-openapi-tutorial.split-schema-list"],
        ["read-split-records"],
        ["http.body.bytes", "http.status"],
        (
            "The response contains the fixture's omitted `summary` value as JSON null. "
            "Application-authored field contents and the browser docs interaction are not "
            "FastAPI response-model behavior."
        ),
        (
            "FastAPI 0.141.1 attaches response fields and performs response serialization "
            "before returning the ASGI response; generic HTTP response transport belongs to "
            "Starlette 1.6.0. The selected action is the fixture's GET response."
        ),
    ),
    (_SPLIT_PAGE, "model-for-output-in-docs"): _workflow(
        "Model for Output in Docs { #model-for-output-in-docs }",
        58,
        65,
        _SPLIT_RECIPE,
        ["fastapi.atlas-openapi-tutorial.split-schema-document"],
        ["inspect-split-schema-document"],
        _MODE_DOCUMENT_SELECTORS,
        (
            "The selected full OpenAPI document is generated with separate input/output "
            "schemas enabled, but contains one `Record` component rather than a demonstrated "
            "output component distinct from input. No docs UI is rendered, and screenshot "
            "appearance is not claimed."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "model-for-input-and-output-in-docs"): _workflow(
        "Model for Input and Output in Docs { #model-for-input-and-output-in-docs }",
        66,
        79,
        _SPLIT_RECIPE,
        ["fastapi.atlas-openapi-tutorial.split-schema-document"],
        ["inspect-split-schema-document"],
        _MODE_DOCUMENT_SELECTORS,
        (
            "The full OpenAPI document is generated with separate input/output schemas enabled "
            "but contains one `Record` component; separate input and output components are "
            "not demonstrated for this model. It does not compare docs UI marks or every model "
            "field."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "do-not-separate-schemas"): _workflow(
        "Do not Separate Schemas { #do-not-separate-schemas }",
        80,
        102,
        _SPLIT_RECIPE,
        [
            "fastapi.atlas-openapi-tutorial.shared-schema-create",
            "fastapi.atlas-openapi-tutorial.shared-schema-list",
            "fastapi.atlas-openapi-tutorial.shared-schema-document",
        ],
        None,
        _MODE_HTTP_DOCUMENT_SELECTORS,
        (
            "These cases submit and return the fixture's `Record` model with separate schema "
            "generation disabled, then select its OpenAPI document. That document also has "
            "one `Record` component, as does the enabled-option document, so this fixture does "
            "not demonstrate merging a distinct pair. The independent field is `summary`, not "
            "the tutorial's `description`; no migration of generated client code is tested."
        ),
        _MODE_RATIONALE,
    ),
    (_SPLIT_PAGE, "same-schema-for-input-and-output-models-in-docs"): _workflow(
        (
            "Same Schema for Input and Output Models in Docs { "
            "#same-schema-for-input-and-output-models-in-docs }"
        ),
        96,
        102,
        _SPLIT_RECIPE,
        ["fastapi.atlas-openapi-tutorial.shared-schema-document"],
        ["inspect-shared-schema-document"],
        _MODE_DOCUMENT_SELECTORS,
        (
            "The selected full OpenAPI document is generated with separate schema generation "
            "disabled and contains one `Record` component; the enabled-option document also "
            "contains one, so this fixture does not establish a distinct shared-versus-split "
            "component result. It does not render docs UI or cover client compatibility "
            "choices."
        ),
        _MODE_RATIONALE,
    ),
    (_EXTEND_PAGE, "extending-openapi"): _excluded(
        "Extending OpenAPI { #extending-openapi }",
        1,
        88,
        (
            "This page title aggregates default OpenAPI generation, custom schema extension, "
            "caching, method override, and an external ReDoc view; these behaviors are mapped "
            "individually below or under the existing cache section."
        ),
        (
            "FastAPI 0.141.1 owns OpenAPI generation and the schema endpoint; child rows "
            "separately select the default and custom documents. The ReDoc browser rendering "
            "is external and is not combined with the schema inputs."
        ),
    ),
    (_EXTEND_PAGE, "the-normal-process"): _workflow(
        "The normal process { #the-normal-process }",
        7,
        43,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.normal-schema-route"],
        None,
        _EXTEND_SELECTORS,
        (
            "The default `/openapi.json` case selects the generated info metadata and route "
            "paths and checks the endpoint status. It does not claim every `get_openapi` "
            "parameter, response header/body byte, or docs renderer."
        ),
        _EXTEND_RATIONALE,
    ),
    (_EXTEND_PAGE, "overriding-the-defaults"): _workflow(
        "Overriding the defaults { #overriding-the-defaults }",
        44,
        88,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.custom-logo-schema"],
        None,
        _EXTEND_SELECTORS,
        (
            "The custom case calls `get_openapi`, adds the page's `info.x-logo`, and serves "
            "selected info/path pointers. It samples this one custom field, not arbitrary "
            "schema overrides or ReDoc rendering."
        ),
        _EXTEND_RATIONALE,
    ),
    (_EXTEND_PAGE, "normal-fastapi"): _workflow(
        "Normal **FastAPI** { #normal-fastapi }",
        50,
        55,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.normal-schema-route"],
        None,
        _EXTEND_SELECTORS,
        (
            "The default app registers one GET operation and selects its generated info and "
            "path metadata through `/openapi.json`. Its response data and operation differ "
            "from the tutorial example."
        ),
        _EXTEND_RATIONALE,
    ),
    (_EXTEND_PAGE, "generate-the-openapi-schema"): _workflow(
        "Generate the OpenAPI schema { #generate-the-openapi-schema }",
        56,
        61,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.custom-logo-schema"],
        None,
        _EXTEND_SELECTORS,
        (
            "The custom `get_openapi` call supplies title, version, summary, description, "
            "and `app.routes`; selected `/info` and `/paths` pointers inspect those generated "
            "document portions. This is one call shape, not all optional utility arguments."
        ),
        _EXTEND_RATIONALE,
    ),
    (_EXTEND_PAGE, "modify-the-openapi-schema"): _workflow(
        "Modify the OpenAPI schema { #modify-the-openapi-schema }",
        62,
        67,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.custom-logo-schema"],
        None,
        _EXTEND_SELECTORS,
        (
            "The selected OpenAPI action includes the exact `/info/x-logo` pointer added to "
            "the generated schema. It does not claim other vendor extensions."
        ),
        (
            'The pinned source example mutates `openapi_schema["info"]["x-logo"]`. '
            "FastAPI serves the result of the assigned `app.openapi()` method through its "
            "schema route in fastapi/applications.py:1105-1120."
        ),
    ),
    (_EXTEND_PAGE, "override-the-method"): _workflow(
        "Override the method { #override-the-method }",
        78,
        83,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.custom-logo-schema"],
        None,
        _EXTEND_SELECTORS,
        (
            "The case replaces `app.openapi` with `custom_openapi` and observes the served "
            "info/path document, including `info.x-logo`. It does not exercise repeated-call "
            "cache behavior, which is mapped separately."
        ),
        _EXTEND_RATIONALE,
    ),
    (_EXTEND_PAGE, "check-it"): _workflow(
        "Check it { #check-it }",
        84,
        88,
        _EXTEND_RECIPE,
        ["fastapi.docs.extending-openapi.custom-logo-schema"],
        None,
        _EXTEND_SELECTORS,
        (
            "The selected response confirms that the OpenAPI document served to a client "
            "contains the custom logo URL. It does not visit ReDoc or assert that a browser "
            "renders the image."
        ),
        _EXTEND_RATIONALE,
    ),
}
