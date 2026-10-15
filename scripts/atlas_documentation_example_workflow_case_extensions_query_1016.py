"""Additive reviewed workflow links for the query validation section cases."""

DOC_EXAMPLE_WORKFLOW_CASE_EXTENSIONS_QUERY_1016 = {
    "docs_src/query_params_str_validations/tutorial001_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/"
                "query-params-str-validations-section-cases-1016.yaml"
            ),
            "case_ids": ["fastapi.docs-section.query-params-str-validations.optional-query"],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
            ],
        }
    ],
    "docs_src/query_params_str_validations/tutorial013_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/"
                "query-params-str-validations-section-cases-1016.yaml"
            ),
            "case_ids": ["fastapi.docs-section.query-params-str-validations.untyped-list-items"],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
            ],
        }
    ],
}
