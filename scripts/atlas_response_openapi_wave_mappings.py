"""Source-reviewed mappings for response and JSON encoding test cases.

This wave is intentionally a separate, data-only module.  Its inputs are
independently authored recipes; the pinned upstream test functions and
FastAPI implementation spans below justify the behavior labels.
"""


def _source(path, start, end, role):
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(
    test_path,
    start,
    end,
    feature_ids,
    observation_selectors,
    rationale,
    workflow,
    *,
    implementation=None,
    additional_sources=(),
    contract_gate=None,
):
    sources = [_source(test_path, start, end, "upstream test stimulus and asserted behavior")]
    if implementation is not None:
        sources.append(implementation)
    sources.extend(additional_sources)
    row = {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(observation_selectors),
        "rationale": rationale,
        "replace_features": True,
        "supporting_sources": sources,
        "stimulus_notes": workflow,
    }
    if contract_gate:
        row["contract_gate"] = contract_gate
    return row


_SERIALIZE = _source(
    "fastapi/routing.py",
    301,
    330,
    "FastAPI validates response content and delegates response-field serialization",
)
_ENCODER = _source(
    "fastapi/encoders.py",
    129,
    190,
    "FastAPI jsonable_encoder public call shape and output filtering options",
)
_ENCODER_UNSUPPORTED_FALLBACK = _source(
    "fastapi/encoders.py",
    346,
    355,
    "jsonable_encoder retries dict/vars conversion and raises ValueError when both fail",
)
_ENCODER_PYDANTIC_V1_REJECTION = _source(
    "fastapi/encoders.py",
    341,
    345,
    "jsonable_encoder detects a Pydantic v1 model instance before generic conversion",
)
_PYDANTIC_V1_INSTANCE_DETECTION = _source(
    "fastapi/_compat/shared.py",
    186,
    195,
    "FastAPI identifies Pydantic v1 model instances through pydantic.v1.BaseModel",
)
_PYDANTIC_V1_ERROR_TYPE = _source(
    "fastapi/exceptions.py",
    246,
    249,
    "PydanticV1NotSupportedError is a FastAPIError subtype",
)
_OPENAPI_RESPONSES = _source(
    "fastapi/openapi/utils.py",
    473,
    505,
    "FastAPI converts additional response models into OpenAPI response schemas",
)
_OPENAPI_SUCCESS = _source(
    "fastapi/openapi/utils.py",
    456,
    472,
    "FastAPI emits success-response schema content using the selected media type and response field",
)


RESPONSE_OPENAPI_TEST_REVIEW_MAPPINGS = {
    "tests/test_additional_response_extra.py": {
        "functions": {
            "test_path_operation": _case(
                "tests/test_additional_response_extra.py",
                24,
                27,
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "The nested router's GET route returns a JSON object and the source checks its 200 status and parsed body.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.nested-router-response, action read-nested-inventory. Its independently named router and body preserve the nested-prefix and normal JSON response observations.",
                implementation=_SERIALIZE,
            ),
            "test_openapi_schema": _case(
                "tests/test_additional_response_extra.py",
                30,
                52,
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The source compares a complete OpenAPI snapshot for a nested router operation.",
                "Use openapi-operations.yaml case fastapi.openapi.additional-response-extra.openapi-schema; it checks the route response pointer and success status.",
                implementation=_OPENAPI_RESPONSES,
                contract_gate="The workflow compares selected OpenAPI pointers rather than the source's full document snapshot; it is a focused source candidate, not a full-snapshot parity claim. Generic TestClient behavior remains in the Starlette 1.6.0 contract.",
            ),
        },
    },
    "tests/test_additional_responses_custom_model_in_callback.py": {
        "functions": {
            "test_openapi_schema": _case(
                "tests/test_additional_responses_custom_model_in_callback.py",
                32,
                147,
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The OpenAPI snapshot places a modeled callback response and its schema component under the callback operation.",
                "Use openapi-operations.yaml case fastapi.openapi.additional-responses-custom-model-in-callback.openapi-schema; the independent workflow observes the callback and named schema pointers.",
                implementation=_OPENAPI_RESPONSES,
                contract_gate="Only the callback and component pointers are compared, not the full source snapshot or query parameter schema. FastAPI callback/OpenAPI behavior is gated by the completed public manifest; TestClient mechanics are Starlette-owned.",
            ),
        },
    },
    "tests/test_additional_responses_custom_validationerror.py": {
        "functions": {
            "test_openapi_schema": _case(
                "tests/test_additional_responses_custom_validationerror.py",
                35,
                100,
                ["openapi-docs", "response-serialization"],
                ["http.status", "openapi.document"],
                "The snapshot documents an additional validation-error response using its declared custom media type and model schema.",
                "Use openapi-operations.yaml case fastapi.openapi.additional-responses-custom-validationerror.openapi-schema; it inspects the status-specific content schema pointer.",
                implementation=_OPENAPI_RESPONSES,
                contract_gate="The selected JSON pointer does not compare every field of the source OpenAPI snapshot. The additional-response schema is FastAPI behavior; ordinary TestClient behavior belongs to Starlette-RS.",
            ),
        },
    },
    "tests/test_additional_responses_default_validationerror.py": {
        "functions": {
            "test_openapi_schema": _case(
                "tests/test_additional_responses_default_validationerror.py",
                16,
                91,
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The OpenAPI snapshot checks the default validation-error response schema for an ordinary route.",
                "Use additional-response-openapi-wave.yaml case fastapi.additional-response-openapi-wave.default-validation-error-schema.test-openapi-schema; its independent input compares the error response schema pointer.",
                implementation=_OPENAPI_RESPONSES,
                contract_gate="The case checks a response-schema pointer rather than the complete OpenAPI document. The source also asserts TestClient status; generic client behavior is Starlette-owned.",
            ),
        },
    },
    "tests/test_additional_responses_router.py": {
        "functions": {
            "test_a": _case(
                "tests/test_additional_responses_router.py",
                61,
                64,
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "A route declaring an additional numeric response still returns its ordinary JSON success response.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.additional-router-runtime, action serve-alpha.",
                implementation=_SERIALIZE,
            ),
            "test_b": _case(
                "tests/test_additional_responses_router.py",
                67,
                70,
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "A route declaring numeric and 4XX additional responses still returns its ordinary JSON success response.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.additional-router-runtime, action serve-beta.",
                implementation=_SERIALIZE,
            ),
            "test_c": _case(
                "tests/test_additional_responses_router.py",
                73,
                76,
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "A route declaring string, status-range, and default response entries still returns its ordinary JSON success response.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.additional-router-runtime, action serve-gamma.",
                implementation=_SERIALIZE,
            ),
            "test_d": _case(
                "tests/test_additional_responses_router.py",
                79,
                82,
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "A route with modeled 5XX/default additional responses still returns its ordinary JSON success response.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.additional-router-runtime, action serve-delta.",
                implementation=_SERIALIZE,
            ),
            "test_openapi_schema": _case(
                "tests/test_additional_responses_router.py",
                85,
                182,
                ["openapi-docs"],
                ["docs.response.status", "http.status", "openapi.document", "openapi.paths"],
                "The snapshot checks numeric, string, range, default, and modeled additional-response OpenAPI entries on four router operations. Its /c response declaration uses lowercase 5xx and asserts the normalized 5XX key.",
                "Use openapi-operations.yaml case fastapi.openapi.additional-responses-router.openapi-schema for selected response-object pointers, and additional-response-status-keys-review.yaml case fastapi.additional-responses.status-key-normalization.lowercase-range for /c-style lowercase range normalization.",
                implementation=_OPENAPI_RESPONSES,
                additional_sources=(
                    _source(
                        "tests/test_additional_responses_router.py",
                        31,
                        40,
                        "upstream /c route declaration with lowercase 5xx additional response key",
                    ),
                ),
                contract_gate="The recipes compare selected response pointers rather than the full snapshot. Response-model schemas depend on the completed FastAPI manifest; TestClient behavior is Starlette-owned.",
            ),
        },
    },
    "tests/test_additional_responses_union_duplicate_anyof.py": {
        "functions": {
            "test_openapi_schema": _case(
                "tests/test_additional_responses_union_duplicate_anyof.py",
                44,
                124,
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The OpenAPI regression snapshot checks a union additional-response schema where duplicate anyOf branches must not appear.",
                "Use openapi-operations.yaml case fastapi.openapi.additional-responses-union-duplicate-anyof.openapi-schema; its JSON pointer targets the status-specific schema.",
                implementation=_OPENAPI_RESPONSES,
                contract_gate="The pointer case is narrower than the full source snapshot and must preserve the duplicate-branch predicate. It remains gated on the full FastAPI response/OpenAPI manifest.",
            ),
        },
    },
    "tests/test_response_by_alias.py": {
        "functions": {
            "test_openapi_schema": _case(
                "tests/test_response_by_alias.py",
                137,
                330,
                ["openapi-docs", "response-serialization"],
                ["http.status", "openapi.document"],
                "The OpenAPI snapshot checks whether response schemas use aliases by default and respect response_model_by_alias=False.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.response-alias-openapi, action inspect-response-alias-schemas; selected schema pointers cover the default and field-name variants.",
                implementation=_OPENAPI_SUCCESS,
                contract_gate="The independent case compares selected schema/component pointers, not the complete module snapshot. Response serialization and generated alias schema policy require the full FastAPI manifest gate.",
            ),
        },
    },
    "tests/test_response_model_as_return_annotation.py": {
        "functions": {
            "test_response_model_filtering_model_annotation_submodel_return_submodel": _case(
                "tests/test_response_model_as_return_annotation.py",
                428,
                433,
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "An explicit response model takes precedence over the endpoint annotation and filters fields from a returned subclass model.",
                "Use response-model-return-annotation-focused-upstream.yaml case fastapi.response-model-return-annotation.decorator-precedence; it exercises explicit response-model precedence and removal of the private field.",
                implementation=_SERIALIZE,
                contract_gate="The independent input returns a dictionary rather than a Pydantic subclass instance, while preserving the field-filtering and precedence observation. Other annotation/no-annotation matrix combinations in this source module remain uncovered by this row.",
            ),
        },
    },
    "tests/test_response_model_sub_types.py": {
        "functions": {
            "test_path_operations": _case(
                "tests/test_response_model_sub_types.py",
                37,
                45,
                ["app-routing"],
                ["http.status"],
                "The source issues four successful requests to routes whose additional-response models include scalar and list shapes; only 200 statuses are asserted at runtime.",
                "Use response-openapi-atlas-wave.yaml case fastapi.response-openapi-atlas-wave.additional-router-runtime, actions serve-alpha through serve-delta, for the source's status-only success requests.",
                implementation=_OPENAPI_RESPONSES,
                contract_gate="The independent routes are status controls, not the source's four integer/list response-model declarations. The type-specific OpenAPI snapshot is recorded separately as an uncovered source case until a recipe compares those exact schema shapes.",
            ),
        },
    },
    "tests/test_jsonable_encoder.py": {
        "functions": {
            "test_encode_dict": _case(
                "tests/test_jsonable_encoder.py",
                75,
                84,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "jsonable_encoder preserves nested dictionary values and applies set include/exclude and empty-set filters.",
                "Use jsonable-encoder-atlas-wave.yaml case fastapi.jsonable-encoder-atlas-wave.output-matrix probes dict-default, dict-include-set, dict-exclude-set, dict-empty-include, and dict-empty-exclude.",
                implementation=_ENCODER,
            ),
            "test_encode_dict_include_exclude_list": _case(
                "tests/test_jsonable_encoder.py",
                87,
                96,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder accepts list-form include/exclude inputs for a dictionary, including empty include/exclude lists.",
                "Use output-matrix probes dict-include-list, dict-exclude-list, dict-empty-include-list, and dict-empty-exclude-list.",
                implementation=_ENCODER,
            ),
            "test_encode_class": _case(
                "tests/test_jsonable_encoder.py",
                99,
                109,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder converts an ordinary object's instance attributes recursively and supports field filters.",
                "Use output-matrix probes custom-class, custom-class-include, custom-class-exclude, custom-class-empty-include, and custom-class-empty-exclude.",
                implementation=_ENCODER,
            ),
            "test_encode_dictable": _case(
                "tests/test_jsonable_encoder.py",
                112,
                122,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder converts an iterable object with nested iterable objects to dictionaries and supports field filters.",
                "Use output-matrix probes dictable-object, dictable-object-include, dictable-object-exclude, dictable-object-empty-include, and dictable-object-empty-exclude.",
                implementation=_ENCODER,
            ),
            "test_encode_dataclass": _case(
                "tests/test_jsonable_encoder.py",
                125,
                131,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder converts a dataclass instance and applies field filters.",
                "Use output-matrix probes dataclass, dataclass-include, dataclass-exclude, dataclass-empty-include, and dataclass-empty-exclude.",
                implementation=_ENCODER,
            ),
            "test_encode_custom_json_encoders_model_pydanticv2": _case(
                "tests/test_jsonable_encoder.py",
                140,
                156,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "Pydantic v2 field serializers run during jsonable_encoder conversion for both a model and an inherited subclass.",
                "Use output-matrix probes custom-field-serializer and model-subclass-custom-serializer; both observe independently constructed Pydantic models with a serializer and inherited behavior.",
                implementation=_ENCODER,
            ),
            "test_encode_unsupported": _case(
                "tests/test_jsonable_encoder.py",
                134,
                137,
                ["python-data-encoding"],
                ["python.call_outcome"],
                "The source-defined Unserializable value raises while iterating and while reading instance attributes; jsonable_encoder turns the two fallback failures into ValueError.",
                "Use jsonable-encoder-atlas-wave.yaml case fastapi.jsonable-encoder-atlas-wave.unsupported-value-error, probe unsupported-value-error, with a python_call_outcome observation for the public call's raised ValueError.",
                implementation=_ENCODER_UNSUPPORTED_FALLBACK,
                additional_sources=(
                    _source(
                        "tests/test_jsonable_encoder.py",
                        45,
                        51,
                        "Unserializable input raises from both __iter__ and __dict__ access",
                    ),
                ),
            ),
            "test_json_encoder_error_with_pydanticv1": _case(
                "tests/test_jsonable_encoder.py",
                159,
                169,
                ["python-data-encoding"],
                ["python.call_outcome"],
                "The source constructs a pydantic.v1 model and requires jsonable_encoder to reject it with PydanticV1NotSupportedError.",
                "Use jsonable-encoder-atlas-wave.yaml case fastapi.jsonable-encoder-atlas-wave.pydantic-v1-model-rejection, probe pydantic-v1-model-rejection, with a python_call_outcome observation for the FastAPI-specific raised error.",
                implementation=_ENCODER_PYDANTIC_V1_REJECTION,
                additional_sources=(
                    _PYDANTIC_V1_INSTANCE_DETECTION,
                    _PYDANTIC_V1_ERROR_TYPE,
                ),
            ),
            "test_encode_model_with_config": _case(
                "tests/test_jsonable_encoder.py",
                172,
                174,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "A Pydantic model configured with use_enum_values is encoded with its enum value.",
                "Use output-matrix probe model-enum-config.",
                implementation=_ENCODER,
            ),
            "test_encode_model_with_default": _case(
                "tests/test_jsonable_encoder.py",
                187,
                202,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder includes model defaults by default and supports unset/default/include/exclude filters.",
                "Use output-matrix probes model-defaults, model-exclude-unset, model-exclude-defaults, model-combined-filters, model-include-set, model-exclude-set, model-empty-include-set, and model-empty-exclude-set.",
                implementation=_ENCODER,
            ),
            "test_encode_model_with_default_in_dict_and_list": _case(
                "tests/test_jsonable_encoder.py",
                205,
                216,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder recursively applies model default filtering through lists, dictionaries, and a dictionary value containing a list.",
                "Use output-matrix probes nested-model-list, nested-model-dict, nested-model-dict-list, and nested-model-dict-unfiltered.",
                implementation=_ENCODER,
            ),
            "test_custom_encoders": _case(
                "tests/test_jsonable_encoder.py",
                219,
                239,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "Custom encoders match both the exact datetime subtype and its datetime base class; the default path emits ISO text.",
                "Use output-matrix probes custom-encoder-exact, custom-encoder-parent-type, and custom-encoder-default.",
                implementation=_ENCODER,
            ),
            "test_custom_enum_encoders": _case(
                "tests/test_jsonable_encoder.py",
                242,
                254,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "A custom encoder handles a specific Enum type and returns a transformed value.",
                "Use output-matrix probe custom-enum-encoder.",
                implementation=_ENCODER,
            ),
            "test_decimal_encoder_float": _case(
                "tests/test_jsonable_encoder.py",
                294,
                296,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "A finite non-integral Decimal is encoded as a float.",
                "Use output-matrix probe decimal-finite-float.",
                implementation=_ENCODER,
            ),
            "test_decimal_encoder_int": _case(
                "tests/test_jsonable_encoder.py",
                299,
                301,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "An integral Decimal is encoded as an integer.",
                "Use output-matrix probe decimal-integer.",
                implementation=_ENCODER,
            ),
            "test_decimal_encoder_nan": _case(
                "tests/test_jsonable_encoder.py",
                304,
                306,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "A Decimal NaN value is converted to a non-finite float and remains NaN.",
                "Use output-matrix probe decimal-nan; the generic direct API result projection records non-finite floats as structured sidecar observations.",
                implementation=_ENCODER,
            ),
            "test_decimal_encoder_infinity": _case(
                "tests/test_jsonable_encoder.py",
                309,
                313,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "Positive and negative Decimal infinity values are converted to floats with preserved signs.",
                "Use output-matrix probes decimal-positive-infinity and decimal-negative-infinity; the generic direct API result projection records the non-finite float signs.",
                implementation=_ENCODER,
            ),
            "test_encode_deque_encodes_child_models": _case(
                "tests/test_jsonable_encoder.py",
                316,
                322,
                ["python-data-encoding"],
                ["python.attribute_value"],
                "The encoder traverses a deque and recursively encodes its Pydantic child model.",
                "Use output-matrix probe deque-child-model.",
                implementation=_ENCODER,
            ),
        },
    },
    "tests/test_response_model_default_factory.py": {
        "functions": {
            "test_response_model_has_default_factory_return_dict": _case(
                "tests/test_response_model_default_factory.py",
                32,
                38,
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A dict return is validated with a response model whose omitted message is filled by its factory.",
                "Use response-policy-matrix.yaml case fastapi.response.model-default-factory, action factory-from-dict.",
                implementation=_SERIALIZE,
            ),
            "test_response_model_has_default_factory_return_model": _case(
                "tests/test_response_model_default_factory.py",
                41,
                47,
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A model-instance return includes the default-factory message in the serialized response.",
                "Use response-policy-matrix.yaml case fastapi.response.model-default-factory, action factory-from-model.",
                implementation=_SERIALIZE,
            ),
        },
    },
    "tests/test_stream_bare_type.py": {
        "functions": {
            "test_jsonl_router_typed_stream": _case(
                "tests/test_stream_bare_type.py",
                56,
                61,
                ["response-serialization"],
                ["http.status"],
                "A typed JSONL stream serializes each item and omits None values under the configured response model.",
                "Use stream-bare-type-upstream.yaml case fastapi.responses.bare-stream.typed-jsonl, action typed-stream-excluding-none.",
                implementation=_source(
                    "fastapi/routing.py",
                    490,
                    510,
                    "FastAPI validates and serializes each stream item",
                ),
                contract_gate="The source parses JSON lines and checks per-item filtering/content type; the recipe's exact byte body and headers are stronger and the current mapping has no JSONL item/header selectors. Generic streaming send behavior is Starlette-owned.",
            ),
            "test_jsonl_router_typed_openapi_schema": _case(
                "tests/test_stream_bare_type.py",
                64,
                74,
                ["openapi-docs"],
                ["http.status", "openapi.document"],
                "The OpenAPI response documents the JSONL item schema for a typed stream.",
                "Use stream-bare-type-upstream.yaml case fastapi.responses.bare-stream.openapi-item-schema, action typed-jsonl-openapi-response.",
                implementation=_source(
                    "fastapi/openapi/utils.py",
                    456,
                    505,
                    "FastAPI builds success/additional response schemas",
                ),
                contract_gate="The workflow selects the response object pointer; it does not compare the source's complete OpenAPI snapshot.",
            ),
        },
    },
    "tests/test_stream_json_validation_error.py": {
        "supporting_sources": [
            _source(
                "fastapi/routing.py",
                490,
                510,
                "FastAPI validates each typed stream item before serialization",
            ),
        ],
        "functions": {
            "test_stream_json_validation_error_async": _case(
                "tests/test_stream_json_validation_error.py",
                33,
                35,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "An invalid second item from an async typed stream raises FastAPI ResponseValidationError.",
                "Use stream-json-validation-error-wave.yaml case fastapi.response-stream.validation-error.async.",
                implementation=_source(
                    "fastapi/routing.py",
                    490,
                    510,
                    "FastAPI raises ResponseValidationError when typed stream item validation fails",
                ),
                contract_gate="The source asserts only that ResponseValidationError escapes the TestClient call; the recipe records its public validation-error class. TestClient exception propagation is Starlette-owned.",
            ),
            "test_stream_json_validation_error_sync": _case(
                "tests/test_stream_json_validation_error.py",
                38,
                40,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "An invalid second item from a sync typed stream raises FastAPI ResponseValidationError.",
                "Use stream-json-validation-error-wave.yaml case fastapi.response-stream.validation-error.sync.",
                implementation=_source(
                    "fastapi/routing.py",
                    490,
                    510,
                    "FastAPI raises ResponseValidationError when typed stream item validation fails",
                ),
                contract_gate="The source asserts only that ResponseValidationError escapes the TestClient call; the recipe records its public validation-error class. TestClient exception propagation is Starlette-owned.",
            ),
        },
    },
    "tests/test_validate_response.py": {
        "functions": {
            "test_invalid": _case(
                "tests/test_validate_response.py",
                51,
                53,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A response model rejects a returned object with a nonnumeric price.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.pydantic.invalid-field.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only. Generic exception propagation through TestClient belongs to Starlette-RS.",
            ),
            "test_invalid_none": _case(
                "tests/test_validate_response.py",
                56,
                58,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A non-optional response model rejects a None endpoint result.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.pydantic.nonnullable-none.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only. Generic exception propagation through TestClient belongs to Starlette-RS.",
            ),
            "test_double_invalid": _case(
                "tests/test_validate_response.py",
                75,
                77,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A response object with multiple invalid fields fails validation.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.pydantic.multiple-invalid-fields.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only. Generic exception propagation through TestClient belongs to Starlette-RS.",
            ),
            "test_invalid_list": _case(
                "tests/test_validate_response.py",
                80,
                82,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A list response model rejects a list containing invalid response items.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.pydantic.invalid-list.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only. Generic exception propagation through TestClient belongs to Starlette-RS.",
            ),
        },
    },
    "tests/test_validate_response_dataclass.py": {
        "functions": {
            "test_invalid": _case(
                "tests/test_validate_response_dataclass.py",
                39,
                41,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A Pydantic dataclass response model rejects a nonnumeric field value.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.dataclass.invalid-field.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only; TestClient exception propagation is Starlette-owned.",
            ),
            "test_double_invalid": _case(
                "tests/test_validate_response_dataclass.py",
                44,
                46,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A Pydantic dataclass response contains multiple invalid fields and raises response validation failure.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.dataclass.multiple-invalid-fields.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only; TestClient exception propagation is Starlette-owned.",
            ),
            "test_invalid_list": _case(
                "tests/test_validate_response_dataclass.py",
                49,
                51,
                ["public-api-errors", "response-serialization"],
                ["validation.error_class"],
                "A list of Pydantic dataclass responses rejects invalid item fields.",
                "Use response-validation-uncovered-wave.yaml case fastapi.response-validation.dataclass.invalid-list.",
                implementation=_SERIALIZE,
                contract_gate="The source checks the raised public exception type only; TestClient exception propagation is Starlette-owned.",
            ),
        },
    },
    "tests/test_response_change_status_code.py": {
        "functions": {
            "test_dependency_set_status_code": _case(
                "tests/test_response_change_status_code.py",
                23,
                26,
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "A nested dependency assigns the response status before the endpoint returns its ordinary JSON body.",
                "Use response-change-status-code-exact-upstream.yaml case fastapi.response.change-status-code.nested-dependency.",
                implementation=_source(
                    "fastapi/routing.py",
                    697,
                    740,
                    "FastAPI resolves the dependency-mutated response status",
                ),
                contract_gate="The recipe uses an independently authored dependency and body; compare status and parsed JSON only. Dependency solving belongs to FastAPI, while TestClient behavior is Starlette-owned.",
            ),
        },
    },
}


# Keep response status/body review separate from the response and encoder wave.
# This wave links its source functions to existing recipe cases, avoiding a
# second copy of the same response stimuli.
from atlas_response_status_body_wave_mappings import (  # noqa: E402
    RESPONSE_STATUS_BODY_TEST_REVIEW_MAPPINGS,
)

RESPONSE_OPENAPI_TEST_REVIEW_MAPPINGS.update(RESPONSE_STATUS_BODY_TEST_REVIEW_MAPPINGS)


# The builder's existing function exclusions cover test_encode_model_with_alias_raises
# and whole-module optional or cancellation cases.  These additional exclusions
# are data for the integrating wave; they are not wired into the builder here.
RESPONSE_OPENAPI_TEST_EXCLUSIONS = {
    "tests/test_jsonable_encoder.py": {
        "test_decimal_encoder_nan": {
            "reason": "The source asserts math.isnan on a non-finite float. The JSON-safe Python return-value workflow cannot represent that predicate as a stable JSON value.",
            "supporting_sources": [
                _source(
                    "tests/test_jsonable_encoder.py",
                    304,
                    306,
                    "NaN encoder result is checked with math.isnan",
                )
            ],
        },
        "test_decimal_encoder_infinity": {
            "reason": "The source asserts math.isinf for positive and negative non-finite floats. The JSON-safe Python return-value workflow cannot represent that predicate as a stable JSON value.",
            "supporting_sources": [
                _source(
                    "tests/test_jsonable_encoder.py",
                    309,
                    313,
                    "positive and negative infinity results are checked with math.isinf",
                )
            ],
        },
    },
}


# Source-backed gaps deliberately stay candidates instead of being mislabeled
# as covered or permanently excluded.  They need a distinct input case before
# their source assertions can become mappings.
RESPONSE_OPENAPI_REVIEW_GAPS = {
    "tests/test_datetime_custom_encoder.py": {
        "test_pydanticv2": {
            "reason": "This test asserts a field_serializer's output after FastAPI's HTTP response-model serialization. The direct jsonable_encoder recipe does not traverse the ASGI route response path, and the current response workload has no datetime serializer route.",
            "supporting_sources": [
                _source(
                    "tests/test_datetime_custom_encoder.py",
                    8,
                    28,
                    "field serializer, FastAPI response-model route, and parsed JSON assertion",
                )
            ],
        },
    },
    "tests/test_response_model_sub_types.py": {
        "test_openapi_schema": {
            "reason": "The full source snapshot distinguishes integer, integer-list, model, and model-list additional response schemas. No independent recipe compares all four schema branches.",
            "supporting_sources": [
                _source(
                    "tests/test_response_model_sub_types.py",
                    48,
                    161,
                    "four additional response model shapes in a full OpenAPI snapshot",
                )
            ],
        },
    },
    "tests/test_stream_status_code.py": {
        "test_openapi": {
            "reason": "The source compares the complete OpenAPI snapshot for SSE, JSONL, and raw streams with declared and dependency-overridden status codes. Current streaming cases cover selected runtime status and JSONL item-schema behavior, not this complete document.",
            "supporting_sources": [
                _source(
                    "tests/test_stream_status_code.py",
                    157,
                    452,
                    "full streaming OpenAPI response/status snapshot",
                )
            ],
        },
    },
    "tests/test_response_code_no_body.py": {
        "test_openapi_schema": {
            "reason": "The source full-document snapshot combines a 204 route with an explicit response class and a modeled 500 response. The bodyless runtime case does not observe those OpenAPI schema assertions.",
            "supporting_sources": [
                _source(
                    "tests/test_response_code_no_body.py",
                    48,
                    115,
                    "full OpenAPI snapshot for the bodyless and modeled responses",
                )
            ],
        },
    },
    "tests/test_response_set_response_code_empty.py": {
        "test_openapi_schema": {
            "reason": "The status-overwrite runtime input does not compare the source's complete OpenAPI snapshot for its declared 204 response and parameter schema.",
            "supporting_sources": [
                _source(
                    "tests/test_response_set_response_code_empty.py",
                    32,
                    104,
                    "full OpenAPI snapshot for the response-status route",
                )
            ],
        },
    },
}
