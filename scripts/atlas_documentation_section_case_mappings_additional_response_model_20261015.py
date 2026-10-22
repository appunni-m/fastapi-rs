"""Reviewed mapping for FastAPI's additional-response model section."""

DOC_SECTION_CASE_MAPPINGS_ADDITIONAL_RESPONSE_MODEL_20261015 = {
    ("advanced/additional-responses.md", "additional-response-with-model"): {
        "heading": "Additional Response with `model` { #additional-response-with-model }",
        "start_line": 17,
        "end_line": 171,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/additional-response-model-openapi.yaml"
        ),
        "case_ids": ["fastapi.openapi.additional-response-model"],
        "action_ids": ["inspect-additional-response-schema"],
        "observation_selectors": [
            "docs.response.status",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "The selected action reads `/openapi.json`, observes its exact HTTP status, and "
            "compares only the `/paths/~1tea/get/responses/418` and "
            "`/components/schemas/TeaError` JSON pointers. This samples one generated 418 "
            "response declaration and its model schema; it does not observe a returned 418 "
            "response, runtime response validation or serialization, other status codes or "
            "media types, or all response models."
        ),
        "rationale": (
            "FastAPI 0.157.0 walks each route's additional `responses` entry, removes its "
            "Python-only `model` key, retrieves the route's prepared response field, and "
            "merges that field's generated schema into the declared response content "
            "(fastapi/openapi/utils.py:458-501). `get_schema_from_model_field` reads the "
            "schema prepared for the field and applies its alias/title projection "
            "(fastapi/_compat/v2.py:254-284). The selected OpenAPI action compares the 418 "
            "response and TeaError component pointers; Pydantic supplies the field schema, "
            "and Starlette 1.6.0 owns generic HTTP transport."
        ),
    },
}
