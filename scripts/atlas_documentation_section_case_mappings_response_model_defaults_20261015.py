"""Reviewed mapping for the response-model defaults documentation section."""


DOC_SECTION_CASE_MAPPINGS_RESPONSE_MODEL_DEFAULTS_20261015 = {
    ("tutorial/response-model.md", "data-with-values-for-fields-with-defaults"): {
        "heading": (
            "Data with values for fields with defaults "
            "{ #data-with-values-for-fields-with-defaults }"
        ),
        "start_line": 265,
        "end_line": 279,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml"
        ),
        "case_ids": [
            "fastapi.response-model.tutorial004-exclude-unset-preserves-explicit-fields"
        ],
        "action_ids": ["item-with-explicit-default-like-values"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "The selected GET returns the item whose description and tax values are explicitly "
            "supplied even though those fields have model defaults. Only its HTTP response is "
            "mapped; the case's separate OpenAPI action is excluded. The adjacent "
            "response_model_exclude_defaults and response_model_exclude_none options are "
            "mentioned in the preceding note but are not exercised or claimed here."
        ),
        "rationale": (
            "FastAPI 0.141.1 forwards response_model_exclude_unset to response serialization "
            "as a distinct option from response_model_exclude_defaults and "
            "response_model_exclude_none (fastapi/routing.py:510-514). The selected response "
            "covers explicitly supplied values for fields that also have defaults."
        ),
    }
}
