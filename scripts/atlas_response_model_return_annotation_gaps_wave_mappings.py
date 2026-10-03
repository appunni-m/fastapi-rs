"""Source-reviewed response-model return-annotation gap-wave mappings."""

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI, Response-class, and wire-transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned validation and model serialization dependency",
    },
}

_TEST = "tests/test_response_model_as_return_annotation.py"
_RECIPE = "tests/fixtures/input-recipes/parity/response-model-return-annotation-gaps-wave.yaml"
_WORKLOAD = "tests/fixtures/workloads/response_model_return_annotation_gaps_wave.py"
_HTTP = ["http.status", "http.body.bytes"]
_VALIDATION = ["validation.error_class"]
_CONSTRUCTION = [
    "construction.outcome",
    "construction.exception_class",
    "construction.exception_message",
]


def _source(path, start, end, role):
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _workflow(case_id, action_id, selectors, recipe_path):
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": [action_id] if action_id else [],
        "observation_selectors": list(selectors),
    }


def _function(
    name,
    test_start,
    test_end,
    route_start,
    route_end,
    case_id,
    action_id,
    selectors,
    rationale,
    gate,
    *,
    recipe_path=_RECIPE,
    workload_path=_WORKLOAD,
    feature_ids=None,
):
    return {
        "feature_ids": feature_ids or ["response-serialization"],
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "workflow_cases": [_workflow(case_id, action_id, selectors, recipe_path)],
        "stimulus_notes": (
            f"Use {recipe_path} case {case_id}, action {action_id or '(construction only)'}; "
            f"the workload at {workload_path} "
            "uses new paths and values and stores no expected response."
        ),
        "supporting_sources": [
            _source(
                _TEST,
                test_start,
                test_end,
                f"pinned FastAPI 0.141.1 upstream test function {name} and its assertions",
            ),
            _source(
                _TEST,
                route_start,
                route_end,
                "upstream route annotation, response-model declaration, and return value",
            ),
        ],
    }


_MODEL_SELECTION = _source(
    "fastapi/routing.py",
    1081,
    1114,
    "FastAPI resolves the endpoint return annotation, suppresses Response subclasses as response models, and creates the selected response field",
)
_RESPONSE_SERIALIZATION = _source(
    "fastapi/routing.py",
    301,
    338,
    "FastAPI validates response content and raises ResponseValidationError before delegating successful values to the field serializer",
)
_RESPONSE_DISPATCH = _source(
    "fastapi/routing.py",
    711,
    739,
    "FastAPI bypasses response-model serialization for returned Response instances and serializes other endpoint values",
)

RESPONSE_MODEL_RETURN_ANNOTATION_GAP_WAVE_MAPPINGS = {
    _TEST: {
        "feature_ids": ["response-serialization", "public-api-errors"],
        "module_observation_selectors": sorted(set(_HTTP + _VALIDATION + _CONSTRUCTION)),
        "rationale": (
            "This supplemental wave reviews high-value return-annotation gaps: quoted forward references, "
            "submodel and extra-field filtering, explicit response-model precedence, JSONResponse annotation "
            "passthrough, invalid response-model output, and invalid inferred response-field construction. "
            "It claims only the selected behavior."
        ),
        "stimulus_notes": (
            "Use the independently authored cases in "
            f"{_RECIPE}. They intentionally omit the upstream OpenAPI snapshot, basic pass-through controls, "
            "response_model=None matrix, plain Response case, and list/union matrix; some are already sampled "
            "by the existing focused recipe. The construction-only error uses a separate recipe and workload."
        ),
        "supporting_sources": [_MODEL_SELECTION, _RESPONSE_SERIALIZATION, _RESPONSE_DISPATCH],
        "source_review_scope_exclusions": [
            {
                "test_functions": {
                    "test_no_response_model_no_annotation_return_model": [254, 257],
                    "test_no_response_model_no_annotation_return_dict": [260, 263],
                    "test_response_model_no_annotation_return_same_model": [266, 269],
                    "test_response_model_no_annotation_return_exact_dict": [272, 275],
                },
                "reason": "Basic unannotated pass-through and exact-shape controls are outside this missing-gap wave.",
            },
            {
                "test_functions": {
                    "test_response_model_no_annotation_return_invalid_dict": [278, 281],
                },
                "reason": "The existing core review mapping already covers this invalid-dictionary response-validation case; this wave adds the unrepresented invalid Pydantic-model return case.",
            },
            {
                "test_functions": {
                    "test_response_model_no_annotation_return_invalid_model": [284, 287],
                },
                "reason": "The explicit response_model invalid-model variant is outside this wave; its inferred-annotation counterpart is selected to isolate return-annotation response validation.",
            },
            {
                "test_functions": {
                    "test_no_response_model_annotation_return_invalid_dict": [316, 319],
                    "test_no_response_model_annotation_return_dict_with_extra_data": [328, 331],
                },
                "reason": "The inferred invalid-dictionary and inferred extra-dictionary variants are outside this submodel-focused sample; the wave covers inferred submodel output and its invalid-model counterpart.",
            },
            {
                "test_functions": {
                    "test_response_model_none_annotation_return_same_model": [342, 345],
                    "test_response_model_none_annotation_return_exact_dict": [348, 351],
                    "test_response_model_none_annotation_return_invalid_dict": [354, 357],
                    "test_response_model_none_annotation_return_invalid_model": [360, 363],
                    "test_response_model_none_annotation_return_dict_with_extra_data": [366, 373],
                    "test_response_model_none_annotation_return_submodel_with_extra_data": [
                        376,
                        385,
                    ],
                },
                "reason": "The response_model=None matrix is separate from response-field filtering; the existing focused recipe samples its submodel passthrough behavior.",
            },
            {
                "test_functions": {
                    "test_response_model_list_of_model_no_annotation": [436, 442],
                    "test_no_response_model_annotation_list_of_model": [445, 451],
                    "test_response_model_union_no_annotation_return_model1": [463, 466],
                    "test_response_model_union_no_annotation_return_model2": [469, 472],
                    "test_no_response_model_annotation_union_return_model1": [475, 478],
                    "test_no_response_model_annotation_union_return_model2": [481, 484],
                },
                "reason": "Ordinary list and union controls are already included in the focused recipe; only the separately uncovered quoted forward reference is added here.",
            },
            {
                "test_functions": {
                    "test_no_response_model_annotation_return_class": [487, 490],
                    "test_openapi_schema": [511, 1121],
                },
                "reason": "Plain Response behavior and selected OpenAPI pointers are handled by the existing focused recipe; the full OpenAPI snapshot is intentionally not copied into this runtime wave.",
            },
        ],
        "functions": {
            "test_no_response_model_annotation_forward_ref_list_of_model": _function(
                "test_no_response_model_annotation_forward_ref_list_of_model",
                454,
                460,
                207,
                212,
                "fastapi.response-model-return-annotation-gaps.forward-reference-list",
                "serve-forward-reference-list",
                _HTTP,
                "FastAPI resolves a quoted list[User] return annotation and applies the inferred response field to returned subclass instances.",
                "The source compares parsed response JSON; this workflow compares exact body bytes, which also observe JSON byte formatting and order. Pydantic serialization and generic Starlette HTTP transport are dependency-owned details.",
            ),
            "test_response_model_no_annotation_return_dict_with_extra_data": _function(
                "test_response_model_no_annotation_return_dict_with_extra_data",
                290,
                293,
                60,
                64,
                "fastapi.response-model-return-annotation-gaps.explicit-dict-extra",
                "filter-extra-dict-field",
                _HTTP,
                "FastAPI's explicit response_model selects User and filters an extra field from a returned dictionary.",
                "The source compares parsed JSON; this workflow compares exact body bytes. The additional byte-format comparison is outside the source assertion.",
            ),
            "test_response_model_no_annotation_return_submodel_with_extra_data": _function(
                "test_response_model_no_annotation_return_submodel_with_extra_data",
                296,
                301,
                67,
                71,
                "fastapi.response-model-return-annotation-gaps.explicit-submodel-extra",
                "filter-extra-explicit-submodel-field",
                _HTTP,
                "FastAPI's explicit response_model validates and projects a returned Pydantic subclass instance to the declared User fields.",
                "The source compares parsed JSON; this workflow compares exact body bytes. Pydantic owns model validation and serialization mechanics, while generic Starlette transport is separately contracted.",
            ),
            "test_no_response_model_annotation_return_submodel_with_extra_data": _function(
                "test_no_response_model_annotation_return_submodel_with_extra_data",
                334,
                339,
                99,
                102,
                "fastapi.response-model-return-annotation-gaps.inferred-submodel-extra",
                "filter-extra-inferred-submodel-field",
                _HTTP,
                "FastAPI infers User from the endpoint annotation and filters the extra field from a returned DatabaseUser subclass instance.",
                "The source compares parsed JSON; this workflow compares exact body bytes. The byte-format comparison is additional wire detail, and Pydantic provides the model serializer.",
            ),
            "test_response_model_model1_annotation_model2_return_submodel_with_extra_data": _function(
                "test_response_model_model1_annotation_model2_return_submodel_with_extra_data",
                420,
                425,
                175,
                180,
                "fastapi.response-model-return-annotation-gaps.explicit-model-over-annotation",
                "explicit-model-over-annotation",
                _HTTP,
                "FastAPI gives the explicit User response_model precedence over an Item return annotation and projects a returned subclass instance accordingly.",
                "The source compares parsed JSON; this workflow compares exact body bytes. Pydantic serialization and generic Starlette transport are dependency-owned details.",
            ),
            "test_no_response_model_annotation_json_response_class": _function(
                "test_no_response_model_annotation_json_response_class",
                493,
                496,
                246,
                248,
                "fastapi.response-model-return-annotation-gaps.jsonresponse-annotation",
                "return-annotated-jsonresponse",
                _HTTP,
                "FastAPI recognizes JSONResponse as a Response subclass annotation, does not infer a response model from it, and passes through the returned response instance.",
                "The source asserts status and parsed JSON; this workflow compares status and body bytes. FastAPI's annotation and passthrough policy is mapped, while JSON rendering, response headers, and ASGI response messages belong to Starlette 1.6.0.",
            ),
            "test_no_response_model_annotation_return_invalid_model": _function(
                "test_no_response_model_annotation_return_invalid_model",
                322,
                325,
                89,
                91,
                "fastapi.response-model-return-annotation-gaps.invalid-inferred-model-validation",
                "reject-invalid-model-output",
                _VALIDATION,
                "FastAPI infers User from the endpoint return annotation, validates the returned Item value against that response field, and raises ResponseValidationError for its missing required field.",
                "The source uses pytest.raises(ResponseValidationError) and checks that the message contains 'missing'. The declared workflow selector records the exact fully qualified exception class, so subclass acceptance and the message-substring predicate remain gated; Starlette TestClient exception propagation is not claimed.",
            ),
            "test_invalid_response_model_field": _function(
                "test_invalid_response_model_field",
                499,
                508,
                503,
                505,
                "fastapi.response-model.return-annotation.invalid-response-field",
                None,
                _CONSTRUCTION,
                "FastAPI rejects an inferred Response | None return annotation while registering the route because it cannot build a valid Pydantic response field. The failure prevents application construction and includes guidance to set response_model=None.",
                "The target currently accepts this annotation at route registration, so this behavior remains unsupported pending implementation. The upstream test uses pytest.raises(FastAPIError), which accepts subclasses, and checks that the message contains 'valid Pydantic field type' and 'parameter response_model=None'. The workflow compares the exact exception class and complete message, which are stronger input observations than those source predicates; they remain gated and are not a parity result.",
                recipe_path="tests/fixtures/input-recipes/parity/response-model-invalid-return-field.yaml",
                workload_path="tests/fixtures/workloads/response_model_invalid_return_field.py",
                feature_ids=["response-serialization", "public-api-errors"],
            ),
        },
    }
}

# Module-level workflow links drive atlas status independently from the
# function-level source notes above.
RESPONSE_MODEL_RETURN_ANNOTATION_GAP_WAVE_MAPPINGS[_TEST]["workflow_cases"] = [
    workflow
    for function_review in RESPONSE_MODEL_RETURN_ANNOTATION_GAP_WAVE_MAPPINGS[_TEST][
        "functions"
    ].values()
    for workflow in function_review["workflow_cases"]
]

__all__ = [
    "RESPONSE_MODEL_RETURN_ANNOTATION_GAP_WAVE_MAPPINGS",
    "SOURCE_IDENTITIES",
]
