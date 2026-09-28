"""Reviewed function-to-input mappings for core validation/schema tests.

This sidecar is intentionally not imported by the atlas builder yet. It records
function-level fixture/action links and source evidence so the atlas owner can
wire it in without inferring coverage from inventory or generated artifacts.
All workflow recipes are input-only; selector names identify observations and
never encode expected values.
"""

from __future__ import annotations

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "pinned development-time source oracle; not a Python runtime dependency",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI request, response, and test-client replacement contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model validation, serialization, and schema-generation dependency",
    },
}

BEHAVIOR_OWNERSHIP = {
    "fastapi_control_flow": "Rust implementation; upstream FastAPI 0.141.1 is development/oracle source only",
    "python_runtime": "direct native re-exports and literal __all__ only; no helpers or framework control flow",
    "generic_starlette_behavior": "Starlette-RS contract, with Starlette 1.6.0 as the sole replacement contract",
    "model_validation_and_schema": "pinned Pydantic 2.13.4 dependency behavior",
}


def _source(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _workflow(
    recipe: str,
    case_id: str,
    action_ids: str | list[str],
    selectors: list[str],
) -> dict[str, object]:
    actions = [action_ids] if isinstance(action_ids, str) else list(action_ids)
    return {
        "recipe_path": f"tests/fixtures/input-recipes/parity/{recipe}",
        "case_id": case_id,
        "action_ids": actions,
        "observation_selectors": list(selectors),
        "coverage": "source-reviewed candidate; not a parity result",
    }


def _function(
    module: str,
    lines: tuple[int, int],
    feature_ids: list[str],
    selectors: list[str],
    rationale: str,
    workflows: list[dict[str, object]],
    *,
    contract_gate: str | None = None,
) -> dict[str, object]:
    gate = contract_gate or (
        "Source-reviewed fixture link only; no parity run or compatibility claim is included in this review wave."
    )
    if not gate.startswith("Partial:"):
        gate = f"Partial: {gate}"
    mapping: dict[str, object] = {
        "mapping_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "workflow_cases": workflows,
        "contract_gate": gate,
        "supporting_sources": [
            _source(
                module,
                lines[0],
                lines[1],
                "upstream test input and asserted observation",
            )
        ],
    }
    return mapping


def _module(
    test_path: str,
    rationale: str,
    sources: list[dict[str, object]],
    functions: dict[str, dict[str, object]],
) -> dict[str, object]:
    return {
        "rationale": rationale,
        "behavior_ownership": dict(BEHAVIOR_OWNERSHIP),
        "supporting_sources": sources,
        "functions": functions,
    }


_HTTP_REQUEST_EDGES = [
    _source(
        "starlette/testclient.py",
        207,
        375,
        "Starlette 1.6.0 TestClient transport drives the ASGI app and collects response events; direct workflow actions express the input at the ASGI boundary",
    ),
    _source(
        "starlette/testclient.py",
        430,
        505,
        "Starlette 1.6.0 TestClient request and verb helpers own generic client behavior used by the upstream source tests",
    ),
    _source(
        "starlette/requests.py",
        139,
        142,
        "Starlette 1.6.0 decodes the ASGI query string as QueryParams; FastAPI-RS assigns this generic request behavior to the Starlette-RS contract",
    ),
    _source(
        "starlette/requests.py",
        254,
        266,
        "Starlette 1.6.0 collects the ASGI body stream and JSON-decodes it; generic request behavior remains under the Starlette-RS contract",
    ),
    _source(
        "starlette/responses.py",
        163,
        168,
        "Starlette 1.6.0 sends response-start and response-body events; generic response transport remains under the Starlette-RS contract",
    ),
]

_OPENAPI_EDGES = [
    _source(
        "fastapi/openapi/utils.py",
        311,
        376,
        "FastAPI builds operation metadata and query/path parameter schemas from registered routes",
    ),
    _source(
        "fastapi/openapi/utils.py",
        585,
        674,
        "FastAPI gathers route fields, emits path operations, and assembles OpenAPI components",
    ),
    _source(
        "starlette/responses.py",
        181,
        199,
        "Starlette 1.6.0 JSONResponse supplies the JSON media type and JSON encoding beneath the FastAPI OpenAPI endpoint",
    ),
]

_REQUEST_BODY_EDGES = [
    _source(
        "fastapi/routing.py",
        425,
        450,
        "FastAPI reads the request body and chooses JSON parsing from the content type",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        951,
        998,
        "FastAPI validates one body field directly or extracts embedded fields and accumulates request errors",
    ),
    _source(
        "fastapi/exception_handlers.py",
        20,
        26,
        "FastAPI converts request validation errors into its JSON 422 response",
    ),
    *_HTTP_REQUEST_EDGES,
]

_QUERY_VALIDATION_EDGES = [
    _source(
        "fastapi/dependencies/utils.py",
        780,
        875,
        "FastAPI extracts multidict values, validates parameter fields, and preserves per-item list locations",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        381,
        471,
        "FastAPI selects the effective Annotated field/dependency and applies declaration defaults",
    ),
    _source(
        "fastapi/exception_handlers.py",
        20,
        26,
        "FastAPI maps RequestValidationError.errors() to the HTTP 422 body",
    ),
    *_HTTP_REQUEST_EDGES,
]

_RESPONSE_EDGES = [
    _source(
        "fastapi/routing.py",
        301,
        341,
        "FastAPI validates response-model values and serializes them with Pydantic field serializers",
    ),
    _source(
        "fastapi/routing.py",
        710,
        748,
        "FastAPI selects its response-model JSON byte fast path only for the default response class",
    ),
    _source(
        "starlette/responses.py",
        48,
        65,
        "Starlette 1.6.0 renders response bodies and derives generic content headers",
    ),
    _source(
        "starlette/responses.py",
        163,
        168,
        "Starlette 1.6.0 emits ASGI response events beneath FastAPI serialization",
    ),
    _source(
        "starlette/responses.py",
        181,
        199,
        "Starlette 1.6.0 JSONResponse uses json.dumps; its generic response behavior belongs to Starlette-RS",
    ),
]


CORE_VALIDATION_TEST_REVIEW_MAPPINGS = {
    "tests/test_additional_properties.py": _module(
        "tests/test_additional_properties.py",
        "A Pydantic dictionary-valued model is parsed from a JSON body and exposed in OpenAPI. The dedicated independent workload covers the same typed additionalProperties path with different field names and values.",
        [
            _source("tests/test_additional_properties.py", 8, 19, "request model and POST route"),
            *_REQUEST_BODY_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_additional_properties_post": _function(
                "tests/test_additional_properties.py",
                (21, 24),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A valid JSON body supplies a dictionary of integer values and the route returns that dictionary. The independent map case exercises this request/response shape with new keys and values.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.map-values-valid",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_openapi_schema": _function(
                "tests/test_additional_properties.py",
                (27, 114),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The source snapshots the complete OpenAPI document for the typed dictionary request body.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.openapi-components",
                        "dispatch",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The independent workflow observes the MapPayload component pointer and adjacent curated components, not the empty-string OpenAPI document root asserted by the upstream snapshot. Coverage is therefore limited to selected component schema material until a root-pointer recipe is added.",
            ),
        },
    ),
    "tests/test_additional_properties_bool.py": _module(
        "tests/test_additional_properties_bool.py",
        "A model configured with extra='forbid' is accepted when empty and rejects an unexpected body property; OpenAPI exposes additionalProperties false.",
        [
            _source(
                "tests/test_additional_properties_bool.py",
                7,
                23,
                "strict model, optional body parameter, and route",
            ),
            *_REQUEST_BODY_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_call_invalid": _function(
                "tests/test_additional_properties_bool.py",
                (28, 30),
                ["request-validation"],
                ["http.status"],
                "An unexpected JSON property is sent to an extra-forbidden Pydantic model and the source checks for HTTP 422.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.strict-extra-invalid",
                        "dispatch",
                        ["http.status"],
                    )
                ],
            ),
            "test_call_valid": _function(
                "tests/test_additional_properties_bool.py",
                (33, 36),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "An empty JSON object is accepted by an optional extra-forbidden model and returned as an empty object.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.strict-empty-valid",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_openapi_schema": _function(
                "tests/test_additional_properties_bool.py",
                (39, 125),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The source snapshots the full OpenAPI document, including the closed Foo model schema.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.openapi-components",
                        "dispatch",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The workflow selects StrictPayload and other component pointers but not the empty-string document root asserted by the source. It samples additionalProperties=false without full-document coverage.",
            ),
        },
    ),
    "tests/test_allow_inf_nan_in_enforcing.py": _module(
        "tests/test_allow_inf_nan_in_enforcing.py",
        "FastAPI Query and Body field declarations carry allow_inf_nan metadata into Pydantic request validation. The new input matrix keeps every original parameterized string value.",
        [
            _source(
                "tests/test_allow_inf_nan_in_enforcing.py",
                7,
                27,
                "route declarations for three query policies and one body policy",
            ),
            _source(
                "fastapi/params.py",
                221,
                295,
                "Query forwards allow_inf_nan through FastAPI field metadata",
            ),
            _source(
                "fastapi/params.py",
                469,
                545,
                "Body forwards allow_inf_nan through FastAPI field metadata",
            ),
            *_QUERY_VALIDATION_EDGES,
        ],
        {
            "test_allow_inf_nan_param_true": _function(
                "tests/test_allow_inf_nan_in_enforcing.py",
                (34, 36),
                ["request-validation"],
                ["http.status"],
                "The true-policy query route is exercised with all six source values, including positive/negative infinity and NaN.",
                [
                    _workflow(
                        "core-allow-inf-nan-enforcing-upstream.yaml",
                        "fastapi.request.allow-inf-nan.query-true",
                        [f"query-true-{i}" for i in range(1, 7)],
                        ["http.status"],
                    )
                ],
            ),
            "test_allow_inf_nan_param_false": _function(
                "tests/test_allow_inf_nan_in_enforcing.py",
                (50, 52),
                ["request-validation"],
                ["http.status"],
                "The false-policy query route is exercised with all six source values, including all three non-finite spellings.",
                [
                    _workflow(
                        "core-allow-inf-nan-enforcing-upstream.yaml",
                        "fastapi.request.allow-inf-nan.query-false",
                        [f"query-false-{i}" for i in range(1, 7)],
                        ["http.status"],
                    )
                ],
            ),
            "test_allow_inf_nan_param_default": _function(
                "tests/test_allow_inf_nan_in_enforcing.py",
                (66, 68),
                ["request-validation"],
                ["http.status"],
                "The default Query policy is exercised with every finite and non-finite value in the source parameter table.",
                [
                    _workflow(
                        "core-allow-inf-nan-enforcing-upstream.yaml",
                        "fastapi.request.allow-inf-nan.query-default",
                        [f"query-default-{i}" for i in range(1, 7)],
                        ["http.status"],
                    )
                ],
            ),
            "test_allow_inf_nan_body": _function(
                "tests/test_allow_inf_nan_in_enforcing.py",
                (82, 84),
                ["request-validation"],
                ["http.status"],
                "The JSON string body is exercised with the full six-value source table under allow_inf_nan=False.",
                [
                    _workflow(
                        "core-allow-inf-nan-enforcing-upstream.yaml",
                        "fastapi.request.allow-inf-nan.body-false",
                        [f"body-false-{i}" for i in range(1, 7)],
                        ["http.status"],
                    )
                ],
            ),
        },
    ),
    "tests/test_ambiguous_params.py": _module(
        "tests/test_ambiguous_params.py",
        "The source combines registration-time FastAPI annotation conflicts with runtime validation from multiple Query annotations.",
        [
            _source(
                "fastapi/dependencies/utils.py",
                381,
                471,
                "FastAPI resolves Annotated FieldInfo/Depends values, checks defaults, and rejects incompatible declarations",
            ),
            _source(
                "fastapi/dependencies/utils.py",
                271,
                347,
                "FastAPI registers dependant fields and dependencies during route construction",
            ),
            *_QUERY_VALIDATION_EDGES,
        ],
        {
            "test_no_annotated_defaults": _function(
                "tests/test_ambiguous_params.py",
                (11, 30),
                ["public-api-errors"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "Two route declarations place defaults inside Annotated metadata: one forbidden path default and one forbidden Query default.",
                [
                    _workflow(
                        "core-ambiguous-params-construction-upstream.yaml",
                        "fastapi.request.ambiguous-params.path-default-in-annotated",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    ),
                    _workflow(
                        "core-ambiguous-params-construction-upstream.yaml",
                        "fastapi.request.ambiguous-params.query-default-in-annotated",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    ),
                ],
            ),
            "test_multiple_annotations": _function(
                "tests/test_ambiguous_params.py",
                (33, 74),
                ["request-validation", "public-api-errors"],
                [
                    "http.status",
                    "http.body.bytes",
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "Three independent query actions sample the same stacked gt/lt bounds; two construction-only cases cover the Depends/Annotated conflicts also asserted in this function.",
                [
                    _workflow(
                        "ambiguous-query-annotations-wave.yaml",
                        "fastapi.ambiguous-params.query-annotations-inside-bounds",
                        "inside-bounds",
                        ["http.status", "http.body.bytes"],
                    ),
                    _workflow(
                        "ambiguous-query-annotations-wave.yaml",
                        "fastapi.ambiguous-params.query-annotations-lower-bound",
                        "at-lower-bound",
                        ["http.status", "http.body.bytes"],
                    ),
                    _workflow(
                        "ambiguous-query-annotations-wave.yaml",
                        "fastapi.ambiguous-params.query-annotations-upper-bound",
                        "above-upper-bound",
                        ["http.status", "http.body.bytes"],
                    ),
                    _workflow(
                        "core-ambiguous-params-construction-upstream.yaml",
                        "fastapi.request.ambiguous-params.depends-annotation-plus-default",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    ),
                    _workflow(
                        "core-ambiguous-params-construction-upstream.yaml",
                        "fastapi.request.ambiguous-params.field-annotation-plus-depends-default",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    ),
                ],
                contract_gate="The runtime inputs preserve the inside/lower/upper validation branches but use values 7, 2, and 11 in place of the source's 5, 1, and 123. Error response bytes are observed; TestClient-specific behavior is not claimed.",
            ),
        },
    ),
    "tests/test_annotated.py": _module(
        "tests/test_annotated.py",
        "The source covers defaulted/required Query parameters, unrelated Annotated metadata, multiple route paths, nested router inclusion, and OpenAPI parameter declarations.",
        [
            _source(
                "tests/test_annotated.py",
                8,
                20,
                "module-level FastAPI routes for default, required, and unrelated Annotated metadata",
            ),
            _source(
                "fastapi/dependencies/utils.py",
                381,
                471,
                "FastAPI selects Query metadata from Annotated and creates parameter fields",
            ),
            *_QUERY_VALIDATION_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_get": _function(
                "tests/test_annotated.py",
                (71, 74),
                ["request-validation"],
                ["http.status", "http.body.bytes"],
                "The ten source cases for default, required, and unrelated metadata map to independently authored route requests covering omitted, supplied, and empty values.",
                [
                    _workflow(
                        "annotated-parameters-upstream.yaml",
                        "fastapi.request.annotated-query-metadata-upstream",
                        [
                            "default-annotated-query-uses-default",
                            "default-annotated-query-overridden",
                            "required-query-with-unconstrained-metadata",
                            "required-query-missing",
                            "required-query-min-length",
                            "query-metadata-after-unrelated-object",
                            "query-metadata-after-unrelated-object-missing",
                            "query-metadata-after-unrelated-object-min-length",
                            "unrelated-annotated-metadata-remains-query",
                            "unrelated-annotated-metadata-required-query",
                        ],
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_multiple_path": _function(
                "tests/test_annotated.py",
                (77, 100),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "Both registrations of a single Annotated endpoint are observed with the default and supplied query value.",
                [
                    _workflow(
                        "annotated-parameters-upstream.yaml",
                        "fastapi.request.annotated-query-metadata-upstream",
                        [
                            "multi-path-annotated-default-first-route",
                            "multi-path-annotated-value-first-route",
                            "multi-path-annotated-default-second-route",
                            "multi-path-annotated-value-second-route",
                        ],
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_nested_router": _function(
                "tests/test_annotated.py",
                (103, 118),
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A defaulted Annotated query is requested through a prefixed included router.",
                [
                    _workflow(
                        "annotated-parameters-upstream.yaml",
                        "fastapi.request.annotated-query-metadata-upstream",
                        "nested-router-annotated-default",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_openapi_schema": _function(
                "tests/test_annotated.py",
                (121, 298),
                ["openapi-docs"],
                ["openapi.document"],
                "The input workload requests OpenAPI for the same four Annotated route categories.",
                [
                    _workflow(
                        "annotated-parameters-upstream.yaml",
                        "fastapi.request.annotated-query-metadata-upstream",
                        "annotated-query-parameters",
                        ["openapi.document"],
                    )
                ],
                contract_gate="The recipe selects the four paths' parameters, while the source compares the full OpenAPI document. Other document sections are outside this workflow's selected pointers.",
            ),
        },
    ),
    "tests/test_arbitrary_types.py": _module(
        "tests/test_arbitrary_types.py",
        "The supported FastAPI portion uses a Pydantic arbitrary runtime value with an explicit JSON schema and serializer, then observes response and OpenAPI behavior.",
        [
            _source(
                "tests/test_arbitrary_types.py",
                11,
                46,
                "arbitrary runtime class, Pydantic serializer/schema metadata, route, and response assertions",
            ),
            *_RESPONSE_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_get": _function(
                "tests/test_arbitrary_types.py",
                (43, 45),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "An arbitrary runtime object is serialized through an explicit Pydantic PlainSerializer in a FastAPI response model.",
                [
                    _workflow(
                        "arbitrary-types-public-api-upstream.yaml",
                        "fastapi.arbitrary-types.vector-response",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_openapi_schema": _function(
                "tests/test_arbitrary_types.py",
                (92, 135),
                ["openapi-docs"],
                ["openapi.document"],
                "The source schema includes the explicit schema supplied for the arbitrary type field.",
                [
                    _workflow(
                        "arbitrary-types-public-api-upstream.yaml",
                        "fastapi.arbitrary-types.vector-openapi-schema",
                        "openapi",
                        ["openapi.document"],
                    )
                ],
                contract_gate="The workflow selects the response schema and VectorEnvelope component, not the complete OpenAPI document snapshot asserted by the source.",
            ),
        },
    ),
    "tests/test_compat.py": _module(
        "tests/test_compat.py",
        "Only the two tests that exercise a public FastAPI body/response workflow are mapped. Direct tests of FastAPI._compat internals and Pydantic ModelField helpers are explicitly outside the supported facade contract.",
        [
            _source("tests/test_compat.py", 23, 38, "public union body route and HTTP requests"),
            _source(
                "tests/test_compat.py",
                41,
                88,
                "public nested Pydantic v2 model-config route and requests",
            ),
            *_REQUEST_BODY_EDGES,
            *_RESPONSE_EDGES,
        ],
        {
            "test_complex": _function(
                "tests/test_compat.py",
                (23, 38),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A public route accepts either a JSON string or an integer list and returns the selected union value.",
                [
                    _workflow(
                        "compatibility-public-workflows-upstream.yaml",
                        "fastapi.compatibility.flexible-text",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    ),
                    _workflow(
                        "compatibility-public-workflows-upstream.yaml",
                        "fastapi.compatibility.flexible-integer-sequence",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    ),
                ],
                contract_gate="The workload uses different strings and list values than the source; it covers the same union branches and exact transport selectors, not the original literals.",
            ),
            "test_propagates_pydantic2_model_config": _function(
                "tests/test_compat.py",
                (41, 88),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "Nested models configured with arbitrary_types_allowed preserve their missing sentinels for absent and explicitly supplied body values.",
                [
                    _workflow(
                        "compatibility-public-workflows-upstream.yaml",
                        "fastapi.compatibility.nested-model-defaults",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    ),
                    _workflow(
                        "compatibility-public-workflows-upstream.yaml",
                        "fastapi.compatibility.nested-model-explicit-values",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    ),
                ],
                contract_gate="The independent workload uses UnsetMarker and renamed model fields instead of the source's Missing type and value key; it samples equivalent nested default/configuration behavior.",
            ),
        },
    ),
    "tests/test_computed_fields.py": _module(
        "tests/test_computed_fields.py",
        "Both separate and shared input/output schema modes serialize a computed field and expose its response schema through OpenAPI.",
        [
            _source(
                "tests/test_computed_fields.py",
                21,
                41,
                "computed Rectangle field, response routes, and response assertions",
            ),
            *_RESPONSE_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_get": _function(
                "tests/test_computed_fields.py",
                (37, 40),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "The response model and additional-response model return the computed area in both schema modes.",
                [
                    _workflow(
                        "computed-fields-separate-schemas-upstream.yaml",
                        "fastapi.responses.computed-fields.separate-schemas.upstream",
                        [
                            "computed-field-on-response-model",
                            "computed-field-on-additional-response-model",
                        ],
                        ["http.status", "http.body.bytes"],
                    ),
                    _workflow(
                        "computed-fields-shared-schemas-upstream.yaml",
                        "fastapi.responses.computed-fields.shared-schemas.upstream",
                        [
                            "computed-field-on-response-model",
                            "computed-field-on-additional-response-model",
                        ],
                        ["http.status", "http.body.bytes"],
                    ),
                ],
            ),
            "test_openapi_schema": _function(
                "tests/test_computed_fields.py",
                (44, 108),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The separate/shared schema workloads select both operation responses and the Rectangle output component.",
                [
                    _workflow(
                        "core-computed-fields-separate-openapi-status-upstream.yaml",
                        "fastapi.responses.computed-fields.separate.openapi-status-review",
                        "computed-fields-openapi-status",
                        ["http.status", "openapi.document"],
                    ),
                    _workflow(
                        "core-computed-fields-shared-openapi-status-upstream.yaml",
                        "fastapi.responses.computed-fields.shared.openapi-status-review",
                        "computed-fields-openapi-status",
                        ["http.status", "openapi.document"],
                    ),
                ],
                contract_gate="The independent actions compare the HTTP status and selected operation/component pointers; the source snapshots the complete OpenAPI document.",
            ),
        },
    ),
    "tests/test_custom_schema_fields.py": _module(
        "tests/test_custom_schema_fields.py",
        "A Pydantic model supplies field-level WithJsonSchema metadata and model-level json_schema_extra; FastAPI exposes the schema and serializes the response model.",
        [
            _source(
                "tests/test_custom_schema_fields.py",
                8,
                38,
                "model schema metadata, route, and expected component shape",
            ),
            *_RESPONSE_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_custom_response_schema": _function(
                "tests/test_custom_schema_fields.py",
                (52, 55),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The selected Gadget schema has an explicit nullable field schema and model extension, analogous to the source Item component.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.openapi-components",
                        "dispatch",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="Only selected component pointers are observed; the source asserts the complete Item component value and full OpenAPI response. The independent workload renames the model, field, and extension key.",
            ),
            "test_response": _function(
                "tests/test_custom_schema_fields.py",
                (58, 62),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "The route response is filtered and serialized with its default nullable model field.",
                [
                    _workflow(
                        "schema-extensions.yaml",
                        "fastapi.schema.custom-json-schema",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The route/model/field names and returned required value differ from the source. This observes a corresponding custom-schema response-model serialization path, not the original payload literal.",
            ),
        },
    ),
    "tests/test_datetime_custom_encoder.py": _module(
        "tests/test_datetime_custom_encoder.py",
        "A response-model field serializer removes microseconds, assigns UTC, and emits an ISO timestamp through FastAPI response serialization.",
        [
            _source(
                "tests/test_datetime_custom_encoder.py",
                8,
                28,
                "Pydantic field serializer, route, and JSON response assertion",
            ),
            *_RESPONSE_EDGES,
        ],
        {
            "test_pydanticv2": _function(
                "tests/test_datetime_custom_encoder.py",
                (8, 28),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "The dedicated workload uses the same timestamp and field serializer operation and observes the serialized response body.",
                [
                    _workflow(
                        "datetime-custom-encoder-upstream.yaml",
                        "fastapi.responses.pydantic-datetime-field-serializer.upstream",
                        "response-model-custom-datetime",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
        },
    ),
    "tests/test_dependency_models.py": _module(
        "tests/test_dependency_models.py",
        "Every function directly exercises private callable-classification caches, private Dependant fields/helpers, or implementation identity semantics. These do not produce a public FastAPI ASGI observation and are not support claims for the facade.",
        [
            _source(
                "tests/test_dependency_models.py",
                1,
                20,
                "test module imports private FastAPI dependency model internals directly",
            ),
            _source(
                "fastapi/dependencies/models.py",
                18,
                65,
                "private callable unwrapping and identity-key internals",
            ),
            _source(
                "fastapi/dependencies/models.py",
                71,
                120,
                "private Dependant scope/cache derivation helpers",
            ),
            _source(
                "fastapi/dependencies/models.py",
                161,
                234,
                "private callable classifiers and computed-scope helper",
            ),
        ],
        {},
    ),
    "tests/test_dump_json_fast_path.py": _module(
        "tests/test_dump_json_fast_path.py",
        "The two source tests assert visible response output and patch Starlette's private json.dumps binding to distinguish an internal serialization optimization.",
        [
            _source(
                "tests/test_dump_json_fast_path.py",
                14,
                24,
                "Pydantic response routes with inferred and explicit JSONResponse classes",
            ),
            *_RESPONSE_EDGES,
        ],
        {
            "test_default_response_class_skips_json_dumps": _function(
                "tests/test_dump_json_fast_path.py",
                (30, 39),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "The inferred response workflow observes the route status and response bytes for a response-model value.",
                [
                    _workflow(
                        "dump-json-fast-path-observable-upstream.yaml",
                        "fastapi.dump-json-fast-path.inferred-response",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The recipe covers visible response output only. The source's differentiating mock assertion counts calls to starlette.responses.json.dumps, a private implementation/performance detail with no current parity selector; no fast-path call-count claim is made.",
            ),
            "test_explicit_response_class_uses_json_dumps": _function(
                "tests/test_dump_json_fast_path.py",
                (42, 51),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "The explicit JSONResponse workflow observes the same visible status and response bytes.",
                [
                    _workflow(
                        "dump-json-fast-path-observable-upstream.yaml",
                        "fastapi.dump-json-fast-path.explicit-response",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The recipe does not instrument the private Starlette json.dumps call-count asserted by the source. It only samples equivalent visible response behavior.",
            ),
        },
    ),
    "tests/test_filter_pydantic_sub_model_pv2.py": _module(
        "tests/test_filter_pydantic_sub_model_pv2.py",
        "A response model filters inherited submodel fields, applies model validators, and exposes a response schema. FastAPI response-validation exceptions cross Starlette's generic server-error re-raise boundary.",
        [
            _source(
                "tests/test_filter_pydantic_sub_model_pv2.py",
                14,
                43,
                "nested response models, validator, dependency, and route",
            ),
            *_RESPONSE_EDGES,
            *_OPENAPI_EDGES,
            _source(
                "starlette/middleware/errors.py",
                150,
                186,
                "Starlette 1.6.0 emits generic 500 handling and re-raises the application exception for callers that observe it",
            ),
        ],
        {
            "test_filter_sub_model": _function(
                "tests/test_filter_pydantic_sub_model_pv2.py",
                (49, 57),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "An inherited nested response object contains a private field that the declared parent response model removes.",
                [
                    _workflow(
                        "pydantic-response-serialization-wave.yaml",
                        "fastapi.pydantic-response-serialization-wave.nested-submodel-filter.test-filter-sub-model",
                        "dispatch",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The independent model uses a different nested tags mapping/value and does not copy the upstream response snapshot; it exercises the same subclass-field filtering branch.",
            ),
            "test_validator_is_cloned": _function(
                "tests/test_filter_pydantic_sub_model_pv2.py",
                (60, 71),
                ["response-serialization", "public-api-errors"],
                ["asgi.application_error.exception"],
                "The invalid path input makes the response-model validator raise during FastAPI response validation; the direct ASGI workflow observes the re-raised exception.",
                [
                    _workflow(
                        "core-filter-sub-model-validator-upstream.yaml",
                        "fastapi.response.filter-submodel.validator-invalid-source-review",
                        "invalid-response-model-name",
                        ["asgi.application_error.exception"],
                    )
                ],
                contract_gate="The v2 workflow selector exposes only the application exception class. The source inspects ResponseValidationError.errors() including structured ctx/input data, so the exact message and detailed error assertion remain unrepresented.",
            ),
            "test_openapi_schema": _function(
                "tests/test_filter_pydantic_sub_model_pv2.py",
                (74, 182),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The independent OpenAPI action selects the response model schema used by the nested filtering route.",
                [
                    _workflow(
                        "core-filter-sub-model-openapi-status-upstream.yaml",
                        "fastapi.response.filter-submodel.openapi-status-review",
                        "filter-model-openapi-status",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The independent action selects the HTTP status and response schema pointer; the source compares the whole OpenAPI document including validation components and metadata.",
            ),
        },
    ),
    "tests/test_multi_body_errors.py": _module(
        "tests/test_multi_body_errors.py",
        "The source tests array-body model parsing, positive decimal validation, multiple indexed element errors, and OpenAPI request schema generation.",
        [
            _source(
                "tests/test_multi_body_errors.py",
                8,
                23,
                "constrained decimal model and list-body route",
            ),
            *_REQUEST_BODY_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_put_correct_body": _function(
                "tests/test_multi_body_errors.py",
                (25, 37),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A valid one-item JSON array is parsed and returned with a positive decimal field.",
                [
                    _workflow(
                        "core-multi-body-errors-upstream.yaml",
                        "fastapi.request.multi-body-errors.core-upstream",
                        "single-valid-list-row",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_jsonable_encoder_requiring_error": _function(
                "tests/test_multi_body_errors.py",
                (40, 53),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "A negative constrained-decimal field produces a FastAPI request validation response.",
                [
                    _workflow(
                        "core-multi-body-errors-upstream.yaml",
                        "fastapi.request.multi-body-errors.core-upstream",
                        "constrained-decimal-error",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The workload uses a renamed InventoryRow model and quantity field; it samples the same Decimal greater-than constraint and JSON error response branch.",
            ),
            "test_put_incorrect_body_multiple": _function(
                "tests/test_multi_body_errors.py",
                (56, 86),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "A list containing two invalid model objects exercises multiple body-index error locations in one response.",
                [
                    _workflow(
                        "core-multi-body-errors-upstream.yaml",
                        "fastapi.request.multi-body-errors.core-upstream",
                        "multiple-row-errors",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The input uses different field names and invalid strings than the source but retains two array items, missing required fields, and invalid decimal values.",
            ),
            "test_openapi_schema": _function(
                "tests/test_multi_body_errors.py",
                (89, 191),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The independent route generates an OpenAPI array request body with an InventoryRow schema.",
                [
                    _workflow(
                        "core-multi-body-errors-upstream.yaml",
                        "fastapi.request.multi-body-errors.core-upstream",
                        "openapi-list-row-schema",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The route and model names differ from the source Item schema; this full-document workflow compares the independent array-body schema, not the source snapshot's literal identifiers.",
            ),
        },
    ),
    "tests/test_multi_query_errors.py": _module(
        "tests/test_multi_query_errors.py",
        "The source tests repeated integer query values, indexed parse errors, and the OpenAPI array parameter schema.",
        [
            _source(
                "tests/test_multi_query_errors.py", 8, 13, "list[int] Query declaration and route"
            ),
            *_QUERY_VALIDATION_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_multi_query": _function(
                "tests/test_multi_query_errors.py",
                (16, 19),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "Two repeated query values are parsed as one integer list and returned.",
                [
                    _workflow(
                        "core-multi-query-errors-upstream.yaml",
                        "fastapi.request.multi-query-errors.core-upstream",
                        "repeated-valid-integers",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_multi_query_incorrect": _function(
                "tests/test_multi_query_errors.py",
                (22, 40),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "Two repeated non-integer values exercise indexed query validation errors in input order.",
                [
                    _workflow(
                        "core-multi-query-errors-upstream.yaml",
                        "fastapi.request.multi-query-errors.core-upstream",
                        "repeated-invalid-integers",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_openapi_schema": _function(
                "tests/test_multi_query_errors.py",
                (43, 122),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The source schema describes an optional repeated query parameter as an integer array.",
                [
                    _workflow(
                        "core-multi-query-errors-upstream.yaml",
                        "fastapi.request.multi-query-errors.core-upstream",
                        "openapi-query-list-schema",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The independent route uses a new path and operation id, so full OpenAPI equality compares the corresponding schema with different document identifiers.",
            ),
        },
    ),
    "tests/test_nested_annotated_in_sequence.py": _module(
        "tests/test_nested_annotated_in_sequence.py",
        "A nested Annotated set query preserves optionality, repeated-value coercion, maximum length validation, and schema generation.",
        [
            _source(
                "tests/test_nested_annotated_in_sequence.py",
                10,
                18,
                "nested Annotated set type and route",
            ),
            *_QUERY_VALIDATION_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_endpoint_none": _function(
                "tests/test_nested_annotated_in_sequence.py",
                (22, 25),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "An omitted optional repeated-set query is returned as null.",
                [
                    _workflow(
                        "nested-annotated-sequence-upstream.yaml",
                        "fastapi.request.nested-annotated-set-query.upstream",
                        "optional-set-query-omitted",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_endpoint_valid": _function(
                "tests/test_nested_annotated_in_sequence.py",
                (28, 31),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "Repeated query values are collected into a set below the declared size limit.",
                [
                    _workflow(
                        "core-nested-annotated-valid-upstream.yaml",
                        "fastapi.request.nested-annotated-set-query.valid-response-review",
                        "valid-repeated-set-query-response",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The source uses an order-insensitive IsList assertion for a set-valued result; the current byte selector compares serialized array order exactly, so a byte mismatch can reflect set iteration order rather than a value mismatch.",
            ),
            "test_endpoint_too_long": _function(
                "tests/test_nested_annotated_in_sequence.py",
                (34, 53),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "Four repeated set values exceed Field(max_length=3) and exercise the FastAPI validation response.",
                [
                    _workflow(
                        "nested-annotated-sequence-upstream.yaml",
                        "fastapi.request.nested-annotated-set-query.upstream",
                        "set-max-length-validation",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The selector captures exact body bytes from an independently authored input; the upstream dirty_equals predicate treats set-item order as irrelevant and also checks its error ctx details.",
            ),
            "test_openapi": _function(
                "tests/test_nested_annotated_in_sequence.py",
                (56, 143),
                ["openapi-docs"],
                ["openapi.document"],
                "The selected parameter schema includes the nested set maximum length and nullable union.",
                [
                    _workflow(
                        "nested-annotated-sequence-upstream.yaml",
                        "fastapi.request.nested-annotated-set-query.upstream",
                        "nested-annotated-query-schema",
                        ["openapi.document"],
                    )
                ],
                contract_gate="Only the route parameter pointer is compared; the source asserts the whole OpenAPI object and its validation definitions.",
            ),
        },
    ),
    "tests/test_required_noneable.py": _module(
        "tests/test_required_noneable.py",
        "Nullable type annotations remain required when no default is declared for Query or embedded Body parameters.",
        [
            _source(
                "tests/test_required_noneable.py",
                6,
                20,
                "required nullable query and embedded body route declarations",
            ),
            *_QUERY_VALIDATION_EDGES,
            *_REQUEST_BODY_EDGES,
        ],
        {
            "test_required_nonable_query_invalid": _function(
                "tests/test_required_noneable.py",
                (25, 27),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "The required nullable query is omitted and must produce a validation response.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "required-query-missing",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_required_noneable_query_value": _function(
                "tests/test_required_noneable.py",
                (30, 33),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A supplied string value is accepted by the required nullable query.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "required-query-value",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The independent route renames the source parameter q to value and supplies indigo instead of foo; it samples the same required-nullable acceptance path with exact status/body observations.",
            ),
            "test_required_nonable_explicit_query_invalid": _function(
                "tests/test_required_noneable.py",
                (36, 38),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "An explicit Query() without a default remains required when omitted.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "explicit-query-missing",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_required_nonable_explicit_query_value": _function(
                "tests/test_required_noneable.py",
                (41, 44),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A supplied value is accepted by the explicit required nullable Query field.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "explicit-query-value",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The independent route renames the source parameter q to value and supplies indigo instead of foo; it samples the same explicit required-nullable Query path.",
            ),
            "test_required_nonable_body_embed_no_content": _function(
                "tests/test_required_noneable.py",
                (47, 49),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "An empty body omits the required nullable embedded field.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "embedded-body-missing",
                        ["http.status", "http.body.bytes"],
                    )
                ],
            ),
            "test_required_nonable_body_embed_invalid": _function(
                "tests/test_required_noneable.py",
                (52, 54),
                ["request-validation", "public-api-errors"],
                ["http.status", "http.body.bytes"],
                "An object with the wrong embedded key still omits the required nullable Body field.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "embedded-body-wrong-key",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The independent route uses field name value and the wrong key wrong instead of source name b and wrong key invalid; it samples the same missing-embedded-field status/error path.",
            ),
            "test_required_noneable_body_embed_value": _function(
                "tests/test_required_noneable.py",
                (57, 60),
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "The embedded nullable body field accepts a supplied string value.",
                [
                    _workflow(
                        "core-required-noneable-upstream.yaml",
                        "fastapi.request.required-noneable.core-upstream",
                        "embedded-body-value",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The independent route renames the source embedded body field b to value and supplies indigo instead of foo; it samples the same required-nullable embedded-body path.",
            ),
        },
    ),
    "tests/test_pydantic_v1_error.py": _module(
        "tests/test_pydantic_v1_error.py",
        "FastAPI rejects Pydantic v1 model classes at parameter, return, response-model, additional-response, union, and sequence registration boundaries.",
        [
            _source(
                "fastapi/utils.py",
                58,
                77,
                "FastAPI detects a Pydantic v1 annotation and raises PydanticV1NotSupportedError while constructing a model field",
            ),
            _source(
                "fastapi/_compat/shared.py",
                198,
                221,
                "FastAPI recognizes Pydantic v1 classes nested directly, in unions, and in sequences",
            ),
        ],
        {
            "test_raises_pydantic_v1_model_in_endpoint_param": _function(
                "tests/test_pydantic_v1_error.py",
                (19, 29),
                ["public-api-errors", "request-validation"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "A pydantic.v1 BaseModel used as a route body parameter is rejected at route construction.",
                [
                    _workflow(
                        "construction-errors-upstream.yaml",
                        "fastapi.construction.pydantic-v1-endpoint-parameter",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    )
                ],
                contract_gate="Upstream skips this source module on Python 3.14 and newer; keep its Python<3.14 source constraint when wiring this mapping.",
            ),
            "test_raises_pydantic_v1_model_in_return_type": _function(
                "tests/test_pydantic_v1_error.py",
                (32, 42),
                ["public-api-errors", "response-serialization"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "A pydantic.v1 model return annotation is rejected during route construction.",
                [
                    _workflow(
                        "construction-errors-upstream.yaml",
                        "fastapi.construction.pydantic-v1-return-type",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    )
                ],
                contract_gate="Upstream skips this source module on Python 3.14 and newer; keep its Python<3.14 source constraint when wiring this mapping.",
            ),
            "test_raises_pydantic_v1_model_in_response_model": _function(
                "tests/test_pydantic_v1_error.py",
                (45, 55),
                ["public-api-errors", "response-serialization"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "An explicit pydantic.v1 response_model is rejected during route construction.",
                [
                    _workflow(
                        "construction-errors-upstream.yaml",
                        "fastapi.construction.pydantic-v1-response-model",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    )
                ],
                contract_gate="Upstream skips this source module on Python 3.14 and newer; keep its Python<3.14 source constraint when wiring this mapping.",
            ),
            "test_raises_pydantic_v1_model_in_additional_responses_model": _function(
                "tests/test_pydantic_v1_error.py",
                (58, 70),
                ["public-api-errors", "openapi-docs"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "A pydantic.v1 model declared under additional response metadata is rejected while registering the route.",
                [
                    _workflow(
                        "construction-errors-upstream.yaml",
                        "fastapi.construction.pydantic-v1-additional-response",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    )
                ],
                contract_gate="Upstream skips this source module on Python 3.14 and newer; keep its Python<3.14 source constraint when wiring this mapping.",
            ),
            "test_raises_pydantic_v1_model_in_union": _function(
                "tests/test_pydantic_v1_error.py",
                (73, 83),
                ["public-api-errors", "request-validation"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "A Pydantic v1 model nested in a dict-or-model parameter union is rejected during route construction.",
                [
                    _workflow(
                        "construction-errors-upstream.yaml",
                        "fastapi.construction.pydantic-v1-union-parameter",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    )
                ],
                contract_gate="Upstream skips this source module on Python 3.14 and newer; keep its Python<3.14 source constraint when wiring this mapping.",
            ),
            "test_raises_pydantic_v1_model_in_sequence": _function(
                "tests/test_pydantic_v1_error.py",
                (86, 96),
                ["public-api-errors", "request-validation"],
                [
                    "construction.outcome",
                    "construction.exception_class",
                    "construction.exception_message",
                ],
                "A Pydantic v1 model nested in a list parameter is rejected during route construction.",
                [
                    _workflow(
                        "construction-errors-upstream.yaml",
                        "fastapi.construction.pydantic-v1-sequence-parameter",
                        [],
                        [
                            "construction.outcome",
                            "construction.exception_class",
                            "construction.exception_message",
                        ],
                    )
                ],
                contract_gate="Upstream skips this source module on Python 3.14 and newer; keep its Python<3.14 source constraint when wiring this mapping.",
            ),
        },
    ),
    "tests/test_schema_compat_pydantic_v2.py": _module(
        "tests/test_schema_compat_pydantic_v2.py",
        "The Pydantic v2 string-enum union response and generated OpenAPI schema are observed through a dedicated independent app workload.",
        [
            _source(
                "tests/test_schema_compat_pydantic_v2.py",
                21,
                33,
                "enum model and response-model route",
            ),
            *_RESPONSE_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_get": _function(
                "tests/test_schema_compat_pydantic_v2.py",
                (36, 38),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "A route returns a model whose field is a union of a populated enum and an empty enum.",
                [
                    _workflow(
                        "core-schema-response-get-upstream.yaml",
                        "fastapi.openapi.schema-compat-pydantic-v2.response",
                        "get-user-response",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The workload uses independently named enum/model values and samples the response shape rather than the source's exact alice/admin literal.",
            ),
            "test_openapi_schema": _function(
                "tests/test_schema_compat_pydantic_v2.py",
                (42, 121),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The source schema includes an enum union and accounts for Pydantic-version-specific placement of an empty enum schema.",
                [
                    _workflow(
                        "openapi-schemas.yaml",
                        "fastapi.openapi.schema-compat-pydantic-v2.openapi-schema",
                        "openapi",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The independent workload compares selected path and CompatibleUser component pointers; the source snapshots the complete document and uses a separate IsOneOf branch for Pydantic before/after 2.11.",
            ),
        },
    ),
    "tests/test_schema_ref_pydantic_v2.py": _module(
        "tests/test_schema_ref_pydantic_v2.py",
        "A response model accepts and serializes a property whose alias is the OpenAPI-reserved $ref key.",
        [
            _source(
                "tests/test_schema_ref_pydantic_v2.py",
                9,
                24,
                "Pydantic alias/config model and FastAPI response route",
            ),
            *_RESPONSE_EDGES,
            *_OPENAPI_EDGES,
        ],
        {
            "test_get": _function(
                "tests/test_schema_ref_pydantic_v2.py",
                (26, 28),
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "The response serializer emits the aliased $ref property from the model output.",
                [
                    _workflow(
                        "core-schema-response-get-upstream.yaml",
                        "fastapi.openapi.schema-ref-pydantic-v2.response",
                        "get-ref-response",
                        ["http.status", "http.body.bytes"],
                    )
                ],
                contract_gate="The independent route returns the value local-reference under a renamed path; it samples the same reserved-alias response behavior without matching the source literal.",
            ),
            "test_openapi_schema": _function(
                "tests/test_schema_ref_pydantic_v2.py",
                (31, 68),
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The generated response schema keeps $ref as a property name instead of interpreting the alias as a schema reference.",
                [
                    _workflow(
                        "openapi-schemas.yaml",
                        "fastapi.openapi.schema-ref-pydantic-v2.openapi-schema",
                        "openapi",
                        ["http.status", "openapi.document"],
                    )
                ],
                contract_gate="The workflow selects the /refs response and RefNamedRecord component; the source asserts its full OpenAPI document and the source route has a different path/model name.",
            ),
        },
    ),
}


CORE_VALIDATION_TEST_EXCLUSIONS = {
    "tests/test_arbitrary_types.py": {
        "test_typeadapter": "Pydantic-only test: it constructs pydantic.TypeAdapter and calls dump_python/json_schema without invoking FastAPI or its public facade. Pydantic is a pinned dependency/oracle, not a FastAPI behavior target.",
    },
    "tests/test_compat.py": {
        "test_model_field_default_required": "Directly constructs FastAPI._compat.v2.ModelField and compares its private default to Pydantic Undefined; no public FastAPI request/response behavior is involved.",
        "test_is_bytes_sequence_annotation_union": "Directly calls FastAPI._compat.shared.is_bytes_sequence_annotation, a private annotation classifier with no public request workflow in this source test.",
        "test_is_uploadfile_sequence_annotation": "Directly calls FastAPI._compat.is_uploadfile_sequence_annotation, a private annotation classifier with no public request workflow in this source test.",
        "test_serialize_sequence_value_with_optional_list": "Directly constructs the private compatibility ModelField and invokes serialize_sequence_value; the output assertion is an internal helper invariant.",
        "test_serialize_sequence_value_with_optional_list_pipe_union": "Directly constructs the private compatibility ModelField and invokes serialize_sequence_value; the output assertion duplicates an internal helper invariant for the same optional-list type.",
        "test_serialize_sequence_value_with_none_first_in_union": "Directly invokes private serialize_sequence_value on a typing.Union[None, list[str]] ModelField; union argument ordering is an internal compatibility detail, not public HTTP behavior.",
    },
    "tests/test_dependency_models.py": {
        "test_callable_classification_is_shared_by_call": "Asserts private lru_cache hit/miss/maxsize counters after calling internal callable classifiers; this internal optimization state has no public ASGI observation.",
        "test_callable_classification_cache_supports_large_apps": "Asserts private cache counters and capacity across 3,000 callables; this stress/performance invariant does not expose a public API result.",
        "test_unhashable_callable_classification": "Directly calls private callable-classification helpers on unhashable objects without registering or invoking a public FastAPI dependency.",
        "test_equal_callable_instances_are_cached_by_identity": "Asserts private callable-classification behavior for two equal objects and identity-keyed cache internals; it is implementation-specific and not publicly observable.",
        "test_callable_classification": "Directly asserts private sync/generator/coroutine classifiers without using a route or public dependency contract.",
        "test_derived_values_are_not_stored_on_dependant": "Inspects private Dependant derived-scope/cache helpers and __dict__ storage; these object-layout invariants are not part of the public FastAPI facade contract.",
        "test_security_scheme_helpers": "Directly calls private security-scheme and scope helpers over Dependant objects rather than exercising HTTP security extraction or OpenAPI output.",
        "test_derived_values_follow_dependency_state": "Mutates private Dependant implementation fields and asserts cache-key/scope helper internals; no public dependency workflow is exercised.",
        "test_explicit_and_generator_scopes": "Directly asserts the private computed-scope helper on constructed Dependant objects instead of observing dependency lifecycle through ASGI.",
        "test_callable_return_annotations_are_not_used": "Directly calls a private coroutine classifier on an internal callable instance; return annotation handling has no route/request observation in this test.",
    },
}


CORE_VALIDATION_TEST_EXCLUSION_EVIDENCE = {
    "tests/test_arbitrary_types.py": {
        "test_typeadapter": [
            _source(
                "tests/test_arbitrary_types.py",
                48,
                89,
                "source labels this check Pydantic-only and invokes TypeAdapter directly",
            ),
        ],
    },
    "tests/test_compat.py": {
        "test_model_field_default_required": [
            _source(
                "tests/test_compat.py",
                14,
                20,
                "private FastAPI compatibility ModelField and Pydantic Undefined",
            )
        ],
        "test_is_bytes_sequence_annotation_union": [
            _source(
                "tests/test_compat.py", 91, 96, "private shared compatibility classifier assertion"
            )
        ],
        "test_is_uploadfile_sequence_annotation": [
            _source(
                "tests/test_compat.py",
                99,
                104,
                "private UploadFile annotation classifier assertion",
            )
        ],
        "test_serialize_sequence_value_with_optional_list": [
            _source(
                "tests/test_compat.py",
                107,
                115,
                "direct private serializer and compatibility field assertion",
            )
        ],
        "test_serialize_sequence_value_with_optional_list_pipe_union": [
            _source(
                "tests/test_compat.py",
                118,
                126,
                "direct private serializer and compatibility field assertion",
            )
        ],
        "test_serialize_sequence_value_with_none_first_in_union": [
            _source(
                "tests/test_compat.py",
                129,
                140,
                "direct private serializer assertion for typing.Union argument order",
            )
        ],
    },
    "tests/test_dependency_models.py": {
        "test_callable_classification_is_shared_by_call": [
            _source(
                "tests/test_dependency_models.py",
                77,
                95,
                "cache counters for private classifier callables",
            )
        ],
        "test_callable_classification_cache_supports_large_apps": [
            _source(
                "tests/test_dependency_models.py",
                98,
                115,
                "large private classifier-cache capacity probe",
            )
        ],
        "test_unhashable_callable_classification": [
            _source(
                "tests/test_dependency_models.py",
                118,
                121,
                "private classification of unhashable callables",
            )
        ],
        "test_equal_callable_instances_are_cached_by_identity": [
            _source(
                "tests/test_dependency_models.py", 124, 130, "private classifier identity semantics"
            )
        ],
        "test_callable_classification": [
            _source(
                "tests/test_dependency_models.py",
                133,
                138,
                "direct private sync/generator/coroutine assertions",
            )
        ],
        "test_derived_values_are_not_stored_on_dependant": [
            _source(
                "tests/test_dependency_models.py",
                141,
                151,
                "private Dependant state/cache assertions",
            )
        ],
        "test_security_scheme_helpers": [
            _source(
                "tests/test_dependency_models.py",
                154,
                161,
                "direct private security helper assertions",
            )
        ],
        "test_derived_values_follow_dependency_state": [
            _source(
                "tests/test_dependency_models.py",
                164,
                184,
                "mutates private Dependant fields and observes derived values",
            )
        ],
        "test_explicit_and_generator_scopes": [
            _source(
                "tests/test_dependency_models.py",
                187,
                194,
                "private computed dependency scope assertions",
            )
        ],
        "test_callable_return_annotations_are_not_used": [
            _source(
                "tests/test_dependency_models.py",
                197,
                204,
                "private classifier assertion on callable return annotation",
            )
        ],
    },
}
