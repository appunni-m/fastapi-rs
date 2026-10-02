"""Reviewed workflow mapping for the strict Content-Type documentation example."""

STRICT_CONTENT_TYPE_DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS = {
    "docs_src/strict_content_type/tutorial001_py310.py": {
        "rationale": (
            "The FastAPI 0.141.1 example sets strict_content_type=False and documents that a "
            "request without Content-Type is parsed as JSON. The independent request uses the "
            "separately authored /legacy/items/ route, a different model and payload, and only "
            "claims the successful status and response body bytes; it does not claim the "
            "example's /items/ route or literal values."
        ),
        "supporting_sources": [
            {
                "path": "docs_src/strict_content_type/tutorial001_py310.py",
                "start_line": 4,
                "end_line": 4,
                "role": "documented application-level strict_content_type=False setting",
            },
            {
                "path": "docs_src/strict_content_type/tutorial001_py310.py",
                "start_line": 12,
                "end_line": 14,
                "role": "documented POST endpoint and response model on /items/",
            },
            {
                "path": "docs/en/docs/advanced/strict-content-type.md",
                "start_line": 78,
                "end_line": 82,
                "role": "documentation states that no-Content-Type bodies are parsed as JSON when strict checking is disabled",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/strict-content-type-documentation-example-independent.yaml",
                "case_ids": ["fastapi.docs.strict-content-type.independent-legacy-no-content-type"],
                "observation_selectors": ["http.body.bytes", "http.status"],
            }
        ],
    }
}
