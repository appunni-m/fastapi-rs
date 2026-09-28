"""Source-reviewed FastAPI Json parameter-location test mappings."""

_SEMANTIC_JSON_GATE = (
    "The upstream assertion parses response.json() and compares a list. The current ASGI recipe "
    "records exact response bytes, which is stricter than semantic JSON equality; retain the "
    "semantic assertion as an explicit contract gate until the workflow supports parsed JSON."
)

_WORKFLOW_NOTES = (
    "The independent cases use new values and direct ASGI requests for form, query, header, and "
    "cookie Json[list[str]] parameters. The query case is in request-coercion.yaml; the other "
    "three cases are in json-parameter-locations-atlas.yaml. Generic request/cookie transport "
    "remains part of the Starlette-RS contract."
)


def _function_mapping(case_id: str, rationale: str) -> dict[str, object]:
    return {
        "feature_ids": ["request-validation"],
        "observation_selectors": ["http.status", "http.body.bytes"],
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": _SEMANTIC_JSON_GATE,
        "stimulus_notes": f"Input case {case_id}; {_WORKFLOW_NOTES}",
    }


JSON_PARAMETER_LOCATIONS_TEST_REVIEW_MAPPINGS = {
    "tests/test_json_type.py": {
        "module_observation_selectors": ["http.status", "http.body.bytes"],
        "functions": {
            "test_form_json_list": _function_mapping(
                "fastapi.json-parameter-locations.test-form-json-list",
                "The source sends a JSON-encoded list as a form field and asserts the decoded "
                "response list. The independent form case exercises Json parameter validation "
                "from a URL-encoded form field.",
            ),
            "test_query_json_list": _function_mapping(
                "fastapi.request-coercion.json-type.test-query-json-list",
                "The source sends a JSON-encoded list in a query parameter and asserts the "
                "decoded response list. The independent request-coercion query case uses a "
                "different list value.",
            ),
            "test_header_json_list": _function_mapping(
                "fastapi.json-parameter-locations.test-header-json-list",
                "The source sends a JSON-encoded list in a header and asserts the decoded "
                "response list. The independent header case uses a different list value.",
            ),
            "test_cookie_json_list": _function_mapping(
                "fastapi.json-parameter-locations.test-cookie-json-list",
                "The source sends a JSON-encoded list in a cookie and asserts the decoded "
                "response list. The independent direct-ASGI case supplies the cookie header "
                "without relying on TestClient's cookie jar.",
            ),
        },
    }
}
