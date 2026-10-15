"""Reviewed section-to-input mappings for body and extra-model tutorials."""

_BODY = "tutorial/body.md"
_BODY_FIELDS = "tutorial/body-fields.md"
_EXTRA_MODELS = "tutorial/extra-models.md"

_BODY_TUTORIAL003 = "tests/fixtures/input-recipes/parity/body-tutorial003-model-upstream.yaml"
_BODY_TUTORIAL004 = "tests/fixtures/input-recipes/parity/body-tutorial004-model-upstream.yaml"
_BODY_SURFACE = "tests/fixtures/input-recipes/parity/body-surface.yaml"
_BODY_FIELDS_TUTORIAL001 = (
    "tests/fixtures/input-recipes/parity/body-fields-doc-tutorial001-review.yaml"
)
_BODY_FIELDS_SCHEMA = (
    "tests/fixtures/input-recipes/parity/body-fields-schema-evidence-20261015.yaml"
)
_EXTRA_MODELS_RECIPE = (
    "tests/fixtures/input-recipes/parity/extra-models-tutorials-upstream-wave.yaml"
)

_HTTP = ["http.body.bytes", "http.status"]
_HTTP_AND_OPENAPI_PATHS = [
    "http.body.bytes",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_OPENAPI_OPERATION = [
    "docs.response.headers",
    "docs.response.status",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_FIELD_SCHEMA = [
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.request_schema",
]


def _workflow(
    heading,
    start,
    end,
    recipe_path,
    case_ids,
    action_ids,
    selectors,
    note,
    rationale,
):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe_path,
        "case_ids": case_ids,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if action_ids is not None:
        mapping["action_ids"] = action_ids
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


_BODY_PIPELINE = (
    "FastAPI 0.141.1 chooses body parsing from the request content type in "
    "fastapi/routing.py:425-450 and binds a non-embedded model body in "
    "fastapi/dependencies/utils.py:951-998. Starlette 1.6.0 owns generic ASGI request "
    "body buffering and JSON decoding in starlette/requests.py:254-266; Pydantic owns "
    "model field conversion and validation."
)


DOC_SECTION_CASE_MAPPINGS_REQUEST_BODY_CORE_20261015 = {
    (_BODY, "request-body"): _excluded(
        "Request Body { #request-body }",
        1,
        166,
        (
            "This heading introduces several independent request-body contracts. Its "
            "runtime examples are reviewed under the anchored child sections below."
        ),
        (
            "The page is not one input shape: child mappings separately select model "
            "binding, required-field validation, OpenAPI, path/query combination, and a "
            "non-Pydantic Body parameter. The intro's HTTP-method guidance is prose rather "
            "than an additional runtime behavior."
        ),
    ),
    (_BODY, "import-pydantics-basemodel"): _excluded(
        "Import Pydantic's `BaseModel` { #import-pydantics-basemodel }",
        21,
        26,
        "This section only shows a Python import of Pydantic's BaseModel.",
        (
            "The import does not exercise FastAPI request handling. Model body behavior "
            "is covered by the following request examples."
        ),
    ),
    (_BODY, "create-your-data-model"): _workflow(
        "Create your data model { #create-your-data-model }",
        27,
        57,
        _BODY_TUTORIAL003,
        ["fastapi.body.tutorial003.optional-model-fields-absent"],
        ["tutorial003-replace-required-fields-only"],
        _HTTP,
        (
            "The body submits the required Record fields while omitting its optional "
            "notes and rebate fields; the HTTP response selects accepted input and the "
            "resulting model data. This samples one model with standard typed fields and "
            "defaults, not every field type or Pydantic model feature."
        ),
        (
            "The section's pinned example declares a BaseModel with required and defaulted "
            "attributes (docs_src/body/tutorial001_py310.py:5-9). The independent model "
            "has the same required/optional distinction and the selected request omits "
            "optional fields. " + _BODY_PIPELINE
        ),
    ),
    (_BODY, "declare-it-as-a-parameter"): _workflow(
        "Declare it as a parameter { #declare-it-as-a-parameter }",
        58,
        65,
        _BODY_TUTORIAL003,
        ["fastapi.body.tutorial003.complete-model"],
        ["tutorial003-replace-complete-record"],
        _HTTP,
        (
            "The endpoint receives a complete Pydantic model from a JSON request body "
            "alongside its path ID, then returns the selected HTTP status and body. The "
            "fixture uses independent field names and values."
        ),
        (
            "The section declares the model as a path-operation parameter "
            "(docs_src/body/tutorial001_py310.py:15-16). The selected tutorial003 action "
            "uses the same model-as-body declaration pattern with a path parameter. "
            + _BODY_PIPELINE
        ),
    ),
    (_BODY, "results"): _workflow(
        "Results { #results }",
        66,
        78,
        _BODY_TUTORIAL003,
        [
            "fastapi.body.tutorial003.complete-model",
            "fastapi.body.tutorial003.required-model-fields-missing",
        ],
        None,
        _HTTP,
        (
            "The selected requests exercise one accepted model body and one body missing "
            "required fields; status and response bytes are observed for each. The "
            "separate OpenAPI section covers schema generation, and this mapping does not "
            "claim Pydantic's full conversion or error-detail contract."
        ),
        (
            "The pinned section lists JSON body reading, conversion, validation, and "
            "delivery to the endpoint (docs/en/docs/tutorial/body.md:68-77). The paired "
            "tutorial003 requests reach FastAPI's request-body binding and required-field "
            "failure path. " + _BODY_PIPELINE
        ),
    ),
    (_BODY, "automatic-docs"): _workflow(
        "Automatic docs { #automatic-docs }",
        79,
        88,
        _BODY_TUTORIAL003,
        ["fastapi.body.tutorial003.openapi-operation-and-model"],
        ["tutorial003-inspect-body-operation"],
        _OPENAPI_OPERATION,
        (
            "The selected GET /openapi.json request observes its status, ordered headers, "
            "document, and path operation for the model-body route. It does not exercise "
            "the Swagger UI browser rendering."
        ),
        (
            "The section says a body model is included in OpenAPI and interactive docs "
            "(docs/en/docs/tutorial/body.md:79-87). FastAPI projects body fields into "
            "request-body schema in fastapi/openapi/utils.py:378-385; this action selects "
            "the generated operation and model components. Starlette 1.6.0 supplies the "
            "generic HTTP response transport."
        ),
    ),
    (_BODY, "editor-support"): _excluded(
        "Editor support { #editor-support }",
        89,
        124,
        "The section concerns IDE completion, static type checking, and editor plugins.",
        (
            "These claims describe editor tooling and Python/Pydantic type information; "
            "they are not FastAPI runtime behavior observable through the HTTP or OpenAPI "
            "workflows."
        ),
    ),
    (_BODY, "use-the-model"): _workflow(
        "Use the model { #use-the-model }",
        125,
        130,
        _BODY_TUTORIAL004,
        ["fastapi.body.tutorial004.complete-model"],
        ["tutorial004-replace-complete-record"],
        _HTTP,
        (
            "The selected request binds an independent JSON model to an endpoint, and "
            "the handler serializes its model fields in a response alongside path and "
            "query values. It samples model delivery and response serialization only; "
            "it does not exercise the section's direct attribute access or price "
            "calculation."
        ),
        (
            "The page includes a handler that accesses model attributes and calculates "
            "a price with tax (docs_src/body/tutorial002_py310.py:15-21), but the selected "
            "action is tutorial004-replace-complete-record. Its independent Record "
            "handler returns record.model_dump() with path/query values "
            "(tests/fixtures/workloads/body_tutorial_model_upstream.py:29-34), so this "
            "case supports model delivery and serialization only. " + _BODY_PIPELINE
        ),
    ),
    (_BODY, "request-body-path-parameters"): _workflow(
        "Request body + path parameters { #request-body-path-parameters }",
        131,
        139,
        _BODY_TUTORIAL003,
        ["fastapi.body.tutorial003.complete-model"],
        ["tutorial003-replace-complete-record"],
        _HTTP,
        (
            "The selected PUT request carries both a record ID in the path and a model "
            "in the JSON body, and observes the response body. It samples this combined "
            "binding shape only."
        ),
        (
            "The section's tutorial003 endpoint declares both `record_id` and a body "
            "model (docs_src/body/tutorial003_py310.py:15-16). The independent workflow "
            "submits both values and observes the resulting response. " + _BODY_PIPELINE
        ),
    ),
    (_BODY, "request-body-path-query-parameters"): _workflow(
        "Request body + path + query parameters { #request-body-path-query-parameters }",
        140,
        163,
        _BODY_TUTORIAL004,
        ["fastapi.body.tutorial004.complete-model"],
        ["tutorial004-replace-complete-record"],
        _HTTP,
        (
            "The PUT request supplies a path ID, query value, and JSON model body; the "
            "selected response body exposes all three values. It samples this endpoint "
            "signature and does not claim every parameter-source inference rule."
        ),
        (
            "The pinned tutorial004 endpoint combines an integer path parameter, a model "
            "body, and an optional query parameter (docs_src/body/tutorial004_py310.py:15-20). "
            "Its input supplies all three and observes their integrated response. " + _BODY_PIPELINE
        ),
    ),
    (_BODY, "without-pydantic"): _workflow(
        "Without Pydantic { #without-pydantic }",
        164,
        166,
        _BODY_SURFACE,
        ["fastapi.body.embedded-scalar-valid"],
        ["dispatch"],
        [
            "asgi.send.message_types",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        (
            "The action posts an embedded scalar Body parameter without a Pydantic model "
            "and selects HTTP status, headers, response bytes, and ASGI send message "
            "types. It does not cover all Body parameter configurations."
        ),
        (
            "The section explicitly points to singular values in Body parameters "
            "(docs/en/docs/tutorial/body.md:164-166). The selected workload declares an "
            "embedded `str` with Body and no BaseModel. FastAPI supplies parameter/body "
            "binding; Starlette 1.6.0 owns generic ASGI dispatch and response emission."
        ),
    ),
    (_BODY_FIELDS, "body-fields"): _excluded(
        "Body - Fields { #body-fields }",
        1,
        61,
        (
            "This heading groups Field import, model constraints, and schema metadata, "
            "which are reviewed separately under its child sections."
        ),
        (
            "One page-level input would conflate model validation and OpenAPI metadata. "
            "The child mappings select their respective request or schema behavior; the "
            "opening summary adds no independent runtime operation."
        ),
    ),
    (_BODY_FIELDS, "import-field"): _excluded(
        "Import `Field` { #import-field }",
        5,
        17,
        "This section shows importing Pydantic's Field and clarifies its module origin.",
        (
            "A Python import and module-origin note do not exercise FastAPI runtime "
            "behavior. The following sections map model validation and schema projection."
        ),
    ),
    (_BODY_FIELDS, "declare-model-attributes"): _workflow(
        "Declare model attributes { #declare-model-attributes }",
        18,
        43,
        _BODY_FIELDS_TUTORIAL001,
        [
            "fastapi.docs-example.body-fields.tutorial001.embedded-model-valid",
            "fastapi.docs-example.body-fields.tutorial001.embedded-model-invalid-amount",
        ],
        None,
        _HTTP,
        (
            "The selected requests submit an embedded model with a positive amount and "
            "then an amount of zero, observing accepted and rejected HTTP responses. "
            "This samples the `gt=0` model-field constraint only; it does not compare the "
            "full Param/FieldInfo class relationship described in the technical note."
        ),
        (
            "The pinned example declares typed model attributes with Field constraints "
            "(docs_src/body_fields/tutorial001_an_py310.py:9-19). The independent "
            "workload has a positive amount field and the selected pair reaches its valid "
            "and invalid values. Pydantic validates the field; FastAPI binds the embedded "
            "model as request data."
        ),
    ),
    (_BODY_FIELDS, "add-extra-information"): _workflow(
        "Add extra information { #add-extra-information }",
        44,
        56,
        _BODY_FIELDS_SCHEMA,
        ["fastapi.body-fields.field-json-schema-metadata"],
        ["inspect-field-json-schema-metadata"],
        _FIELD_SCHEMA,
        (
            "The OpenAPI observation selects the embedded request schema and the `note` "
            "and `amount` component schemas, including their maxLength and greater-than "
            "constraints. It samples these Field-derived JSON Schema entries only, not "
            "arbitrary extra keywords or every Body/Query metadata option."
        ),
        (
            "The section says Field metadata and extra values appear in generated JSON "
            "Schema (docs/en/docs/tutorial/body-fields.md:44-53). The existing independent "
            "SupplyInput workload declares `note` with max_length and `amount` with `gt`; "
            "the uniquely named input recipe selects those exact OpenAPI component "
            "subtrees plus the request-body schema. FastAPI projects request schemas in "
            "fastapi/openapi/utils.py:378-385, while Pydantic emits the model field schema."
        ),
    ),
    (_BODY_FIELDS, "recap"): _workflow(
        "Recap { #recap }",
        57,
        61,
        _BODY_FIELDS_SCHEMA,
        ["fastapi.body-fields.field-json-schema-metadata"],
        ["inspect-field-json-schema-metadata"],
        _FIELD_SCHEMA,
        (
            "The selected field-schema observation demonstrates one positive-value "
            "constraint and one maximum-length constraint projected into OpenAPI. Other "
            "Field options and arbitrary JSON Schema extras are outside this sample."
        ),
        (
            "The recap describes Field-based validation and extra JSON Schema metadata "
            "(docs/en/docs/tutorial/body-fields.md:57-61). The selected component "
            "subtrees are produced from Field declarations in the existing independent "
            "SupplyInput model; FastAPI exposes them through the request OpenAPI schema."
        ),
    ),
    (_EXTRA_MODELS, "extra-models"): _excluded(
        "Extra Models { #extra-models }",
        1,
        211,
        (
            "This page heading covers user-model, union-response, list-response, and "
            "dictionary-response examples mapped under its child sections."
        ),
        (
            "The umbrella page contains distinct request and response model workflows, "
            "along with a password-storage warning. Child sections each select the "
            "relevant existing workflow rather than treating the full page as one case."
        ),
    ),
    (_EXTRA_MODELS, "multiple-models"): _workflow(
        "Multiple models { #multiple-models }",
        19,
        140,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial001-flat-user-models"],
        ["create-user", "openapi-user-models"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "The selected request uses distinct input and output user models; the response "
            "and OpenAPI operation/model schemas are observed. The app's database model "
            "is constructed internally and is not returned or asserted."
        ),
        (
            "The pinned tutorial001 source declares UserIn, UserOut, and UserInDB and "
            "attaches UserOut as response_model "
            "(docs_src/extra_models/tutorial001_py310.py:7-24,31-41). The existing "
            "workload uses the same three-model roles and selects the public response and "
            "schema. FastAPI response-model filtering is implemented in "
            "fastapi/routing.py:301-342."
        ),
    ),
    (_EXTRA_MODELS, "about-user-in-model-dump"): _workflow(
        "About `**user_in.model_dump()` { #about-user-in-model-dump }",
        25,
        140,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial001-flat-user-models"],
        ["create-user"],
        _HTTP,
        (
            "The POST executes the example's model transformation in its endpoint, then "
            "selects the public HTTP response. The internal dictionary and database model "
            "are not separately observed."
        ),
        (
            "The pinned example uses model_dump, adds a hashed password, and constructs "
            "UserInDB before returning (docs_src/extra_models/tutorial001_py310.py:31-35). "
            "The existing input reaches that route and observes only FastAPI's public "
            "request/response integration. " + _BODY_PIPELINE
        ),
    ),
    (_EXTRA_MODELS, "pydantics-model-dump"): _workflow(
        "Pydantic's `.model_dump()` { #pydantics-model-dump }",
        27,
        63,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial001-flat-user-models"],
        ["create-user"],
        _HTTP,
        (
            "The selected POST runs the example path that calls `model_dump` and observes "
            "the FastAPI response. It does not assert the intermediate dict or the full "
            "Pydantic method contract."
        ),
        (
            "The page describes Pydantic's `model_dump` and uses it in the FastAPI "
            "example (docs/en/docs/tutorial/extra-models.md:27-63; "
            "docs_src/extra_models/tutorial001_py310.py:31-35). The case samples that "
            "method in an endpoint's request-to-response path while limiting the claim to "
            "the observable HTTP boundary."
        ),
    ),
    (_EXTRA_MODELS, "unpacking-a-dict"): _excluded(
        "Unpacking a `dict` { #unpacking-a-dict }",
        64,
        95,
        (
            "The section demonstrates Python keyword-argument unpacking into a "
            "Pydantic model constructor."
        ),
        (
            "The code calls `UserInDB(**user_dict)` and writes its equivalent explicit "
            "keyword arguments, without defining or exercising a FastAPI route. Python "
            "unpacking and Pydantic model construction are not FastAPI request/response "
            "contracts. The later anchored section that passes incoming request data "
            "and adds an extra password field is mapped separately."
        ),
    ),
    (
        _EXTRA_MODELS,
        "a-pydantic-model-from-the-contents-of-another",
    ): _workflow(
        (
            "A Pydantic model from the contents of another "
            "{ #a-pydantic-model-from-the-contents-of-another }"
        ),
        96,
        114,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial001-flat-user-models"],
        ["create-user"],
        _HTTP,
        (
            "The endpoint transforms a validated input model into a database-model "
            "instance and returns a response filtered by UserOut. The internal instance "
            "is not selected as an observation."
        ),
        (
            "The pinned section shows UserInDB constructed from `user_in.model_dump()` "
            "(docs/en/docs/tutorial/extra-models.md:96-113); tutorial001 performs that "
            "transformation in the handler (docs_src/extra_models/tutorial001_py310.py:31-35). "
            "The input reaches the workflow and selects its external response only."
        ),
    ),
    (_EXTRA_MODELS, "unpacking-a-dict-and-extra-keywords"): _workflow(
        "Unpacking a `dict` and extra keywords { #unpacking-a-dict-and-extra-keywords }",
        115,
        140,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial001-flat-user-models"],
        ["create-user"],
        _HTTP,
        (
            "The request executes the endpoint's dict unpacking and added hashed-password "
            "argument before FastAPI filters the response. The hidden UserInDB fields and "
            "Python keyword-unpacking details are not independently observed."
        ),
        (
            "The pinned section adds `hashed_password` while constructing UserInDB from "
            "the model data (docs/en/docs/tutorial/extra-models.md:115-133). The matching "
            "route runs the same application transformation and selects only the public "
            "HTTP result; FastAPI's response-model filter omits private fields."
        ),
    ),
    (_EXTRA_MODELS, "reduce-duplication"): _workflow(
        "Reduce duplication { #reduce-duplication }",
        141,
        158,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial002-inherited-user-models"],
        ["create-user", "openapi-user-models"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "The inherited input/output model workflow submits a user and observes its "
            "public response and OpenAPI user schemas. It samples the documented shared "
            "base-model shape, not every inheritance combination."
        ),
        (
            "Tutorial002 declares UserBase and derives input, output, and database models "
            "from it (docs_src/extra_models/tutorial002_py310.py:7-23). The existing "
            "workload uses that inherited shape; FastAPI binds the input, filters the "
            "response model, and emits the route/schema."
        ),
    ),
    (_EXTRA_MODELS, "union-or-anyof"): _workflow(
        "`Union` or `anyOf` { #union-or-anyof }",
        159,
        188,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial003-union-response-model"],
        ["read-car-variant", "read-plane-variant", "openapi-union-model"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "The two GET requests select car and plane response variants, and the OpenAPI "
            "observation selects their response operation and model definitions. The "
            "independent workload uses the pinned executable example's PEP 604 union "
            "expression rather than `typing.Union`."
        ),
        (
            "The pinned section describes a union response and its OpenAPI `anyOf` "
            "representation (docs/en/docs/tutorial/extra-models.md:159-173). The "
            "tutorial003 workload has two variants and observes both responses plus the "
            "generated operation and component schemas. FastAPI response validation and "
            "serialization occur in fastapi/routing.py:301-342."
        ),
    ),
    (_EXTRA_MODELS, "union-in-python-3-10"): _workflow(
        "`Union` in Python 3.10 { #union-in-python-3-10 }",
        175,
        188,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial003-union-response-model"],
        ["openapi-union-model"],
        ["openapi.document", "openapi.paths"],
        (
            "The selected OpenAPI action observes the schema produced by the pinned "
            "tutorial003 executable's `PlaneItem | CarItem` response_model expression. "
            "It does not compare `typing.Union` spelling or exercise the page prose's "
            "claim that the pipe expression raises."
        ),
        (
            "The source documentation is internally inconsistent: tutorial003's pinned "
            "executable uses `response_model=PlaneItem | CarItem` "
            "(docs_src/extra_models/tutorial003_py310.py:31), while this prose says that "
            "expression errors and recommends `Union` "
            "(docs/en/docs/tutorial/extra-models.md:177-188). This mapping deliberately "
            "records only the executable source's resulting OpenAPI behavior."
        ),
    ),
    (_EXTRA_MODELS, "list-of-models"): _workflow(
        "List of models { #list-of-models }",
        189,
        196,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial004-typed-list-response"],
        ["read-item-list", "openapi-list-response-model"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "The selected GET returns a list through a typed `list[Item]` response "
            "model, and the OpenAPI action observes its route and Item schema. This "
            "samples the list response shape only; other collection and model types "
            "are outside the mapping."
        ),
        (
            "The pinned section declares `response_model=list[Item]` for GET /items/ "
            "(docs/en/docs/tutorial/extra-models.md:189-195; "
            "docs_src/extra_models/tutorial004_py310.py:18-20). The existing "
            "tutorial004 case selects HTTP status/body for `read-item-list` and the "
            "`/paths` and Item schema projections for `openapi-list-response-model`."
        ),
    ),
    (_EXTRA_MODELS, "response-with-arbitrary-dict"): _workflow(
        "Response with arbitrary `dict` { #response-with-arbitrary-dict }",
        197,
        206,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial005-typed-map-response"],
        ["read-keyword-weights", "openapi-map-response-model"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "The endpoint returns a typed mapping without a Pydantic model; the selected "
            "response body and OpenAPI path are observed. The fixture samples `dict[str, "
            "float]` only."
        ),
        (
            "The pinned tutorial005 endpoint declares `response_model=dict[str, float]` "
            "(docs_src/extra_models/tutorial005_py310.py:6-8). The existing workload "
            "returns a string-to-float mapping and selects both the response and path "
            "schema projection in OpenAPI."
        ),
    ),
    (_EXTRA_MODELS, "recap"): _workflow(
        "Recap { #recap }",
        207,
        211,
        _EXTRA_MODELS_RECIPE,
        ["fastapi.extra-models.tutorial002-inherited-user-models"],
        ["create-user", "openapi-user-models"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "The selected inherited-user request observes its public response and model "
            "schemas. It samples one shared-base model arrangement and its password-free "
            "output projection."
        ),
        (
            "The recap summarizes multiple models and inheritance for distinct user "
            "states (docs/en/docs/tutorial/extra-models.md:207-211). Tutorial002 "
            "implements that shape and the workflow selects its HTTP and OpenAPI effects."
        ),
    ),
}
