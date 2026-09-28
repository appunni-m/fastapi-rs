"""Source-reviewed mappings for FastAPI's numeric path-parameter tutorials."""


def _link(recipe_path, case_id, action_ids, observation_selectors):
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(observation_selectors),
    }


def _function(feature_ids, observation_selectors, rationale, links, contract_gate):
    link_note = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} (actions: {', '.join(link['action_ids'])})"
        for link in links
    )
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(observation_selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + contract_gate,
        "workflow_cases": list(links),
        "stimulus_notes": (
            "Independent input-only case link(s): "
            + link_note
            + ". These cases use new paths/values and contain no expected output. "
            "Generic ASGI response transport belongs to Starlette-RS."
        ),
    }


_OPTIONAL = "tests/fixtures/input-recipes/parity/numeric-path-query-forms-upstream.yaml"
_REQUIRED = "tests/fixtures/input-recipes/parity/numeric-path-query-forms-upstream.yaml"
_VALIDATION = "tests/fixtures/input-recipes/parity/request-validation-wave.yaml"
_OPENAPI = "tests/fixtures/input-recipes/parity/request-parameter-openapi-wave.yaml"
_TAIL = "tests/fixtures/input-recipes/parity/request-parameter-tail-wave.yaml"

_HTTP = ["http.status", "http.body.bytes"]
_OPENAPI_SELECTORS = ["http.status", "openapi.document"]

_OPTIONAL_LINK = _link(
    _OPTIONAL,
    "fastapi.numeric-path-query-forms.optional-alias",
    [
        "integer-path-without-optional-query",
        "integer-path-with-aliased-query",
        "non-integer-path-value",
        "optional-query-openapi-response",
    ],
    ["docs.response.body.bytes", "docs.response.status", "http.body.bytes", "http.status"],
)
_REQUIRED_LINK = _link(
    _REQUIRED,
    "fastapi.numeric-path-query-forms.required-query",
    [
        "required-query-with-empty-value",
        "required-query-with-value",
        "required-query-with-non-integer-path-value",
        "required-query-omitted",
        "required-query-openapi-response",
    ],
    ["docs.response.body.bytes", "docs.response.status", "http.body.bytes", "http.status"],
)
_LESS_THAN_ONE_LINK = _link(
    _VALIDATION,
    "fastapi.request-validation-wave.numeric-path-validation.test-read-items-item-id-less-than-one",
    ["dispatch"],
    _HTTP,
)
_OPENAPI_READ_LINK = _link(
    _OPENAPI,
    "fastapi.request-parameter-openapi-wave.path-numeric.test-read-items",
    ["dispatch"],
    _HTTP,
)
_OPENAPI_GREATER_LINK = _link(
    _OPENAPI,
    "fastapi.request-parameter-openapi-wave.path-numeric.test-read-items-item-id-greater-than-one-thousand",
    ["dispatch"],
    _HTTP,
)
_OPENAPI_SCHEMA_LINK = _link(
    _OPENAPI,
    "fastapi.request-parameter-openapi-wave.path-numeric.test-openapi-schema",
    ["dispatch"],
    _OPENAPI_SELECTORS,
)
_TAIL_READ_LINK = _link(
    _TAIL,
    "fastapi.request-parameter-tail-wave.numeric-path.test-read-items",
    ["boundary-zero", "boundary-maximum"],
    _HTTP,
)
_TAIL_NEGATIVE_LINK = _link(
    _TAIL,
    "fastapi.request-parameter-tail-wave.numeric-path.test-read-items-item-id-less-than-zero",
    ["dispatch"],
    _HTTP,
)
_TAIL_GREATER_LINK = _link(
    _TAIL,
    "fastapi.request-parameter-tail-wave.numeric-path.test-read-items-item-id-greater-than-one-thousand",
    ["dispatch"],
    _HTTP,
)
_TAIL_SIZE_LOW_LINK = _link(
    _TAIL,
    "fastapi.request-parameter-tail-wave.numeric-path.test-read-items-size-too-small",
    ["dispatch"],
    _HTTP,
)
_TAIL_SIZE_HIGH_LINK = _link(
    _TAIL,
    "fastapi.request-parameter-tail-wave.numeric-path.test-read-items-size-too-large",
    ["dispatch"],
    _HTTP,
)
_TAIL_OPENAPI_LINK = _link(
    _TAIL,
    "fastapi.request-parameter-tail-wave.numeric-path.test-openapi-schema",
    ["dispatch"],
    _OPENAPI_SELECTORS,
)


_RESPONSE_GATE = (
    "The upstream uses response.json() equality; the selected response body is exact bytes and "
    "can be stricter than semantic JSON equality. Existing independent routes also use different "
    "paths and values, so they are sampled compatibility cases rather than reproductions."
)
_VALIDATION_GATE = (
    "The upstream asserts structured response.json() error details. The current recipe selects "
    "status and exact body bytes, which is stricter at the wire level; several linked cases use "
    "different route names or bounds, so only their common validation behavior is sampled."
)
_OPENAPI_GATE = (
    "The source compares a full OpenAPI JSON snapshot. The selected workflow observes either "
    "raw /openapi.json bytes or selected parameter-schema pointers from an independent app with "
    "different paths and metadata; full-document equivalence is not claimed."
)


def _entry(rationale, functions):
    links = {}
    for function in functions.values():
        for link in function["workflow_cases"]:
            key = (link["recipe_path"], link["case_id"])
            links.setdefault(key, link)
    selectors = sorted(
        {
            selector
            for function in functions.values()
            for selector in function["observation_selectors"]
        }
    )
    workflow_note = "; ".join(
        f"{link['recipe_path']}::{link['case_id']}" for link in links.values()
    )
    return {
        "rationale": rationale,
        "module_observation_selectors": selectors,
        "workflow_cases": list(links.values()),
        "stimulus_notes": "Function-level links use the following independent cases: "
        + workflow_note,
        "functions": functions,
    }


NUMERIC_PATH_VALIDATION_TUTORIAL_MAPPINGS = {
    "tests/test_tutorial/test_path_params_numeric_validations/test_tutorial001.py": _entry(
        "Optional query alias, integer path parsing, and the corresponding OpenAPI projection.",
        {
            "test_read_items": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source checks valid integer path values with an optional aliased query parameter.",
                [_OPTIONAL_LINK],
                _RESPONSE_GATE,
            ),
            "test_read_items_invalid_item_id": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the validation error produced by a non-integer path value.",
                [_OPTIONAL_LINK],
                _VALIDATION_GATE,
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _HTTP,
                "The source snapshots OpenAPI for an integer path and optional aliased query parameter.",
                [_OPTIONAL_LINK],
                _OPENAPI_GATE,
            ),
        },
    ),
    "tests/test_tutorial/test_path_params_numeric_validations/test_tutorial002_tutorial003.py": _entry(
        "Required query parameter behavior and its OpenAPI representation with integer path parsing.",
        {
            "test_read_items": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source checks successful requests with present required query values.",
                [_REQUIRED_LINK],
                _RESPONSE_GATE,
            ),
            "test_read_items_invalid_item_id": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks a validation error for a non-integer path value while a query is present.",
                [_REQUIRED_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_missing_q": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks a missing required query parameter.",
                [_REQUIRED_LINK],
                _VALIDATION_GATE,
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _HTTP,
                "The source snapshots OpenAPI with a required string query parameter.",
                [_REQUIRED_LINK],
                _OPENAPI_GATE,
            ),
        },
    ),
    "tests/test_tutorial/test_path_params_numeric_validations/test_tutorial004.py": _entry(
        "Integer path parsing, a greater-than-or-equal bound, a required query, and OpenAPI.",
        {
            "test_read_items": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source checks valid path integers at and above the inclusive lower bound.",
                [_OPENAPI_READ_LINK, _TAIL_READ_LINK],
                _RESPONSE_GATE,
            ),
            "test_read_items_non_int_item_id": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks path integer parsing failure.",
                [_OPTIONAL_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_item_id_less_than_one": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the inclusive lower path bound at zero.",
                [_LESS_THAN_ONE_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_missing_q": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the missing required query parameter.",
                [_REQUIRED_LINK],
                _VALIDATION_GATE,
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source snapshots the lower path bound and required query parameter schema.",
                [_OPENAPI_SCHEMA_LINK],
                _OPENAPI_GATE,
            ),
        },
    ),
    "tests/test_tutorial/test_path_params_numeric_validations/test_tutorial005.py": _entry(
        "Integer path parsing with inclusive/exclusive bounds, a required query, and OpenAPI.",
        {
            "test_read_items": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source checks valid values at both path-boundary endpoints.",
                [_OPENAPI_READ_LINK, _TAIL_READ_LINK],
                _RESPONSE_GATE,
            ),
            "test_read_items_non_int_item_id": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks path integer parsing failure.",
                [_OPTIONAL_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_item_id_less_than_one": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the inclusive minimum path bound.",
                [_LESS_THAN_ONE_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_item_id_greater_than_one_thousand": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the inclusive maximum path bound.",
                [_OPENAPI_GREATER_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_missing_q": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the missing required query parameter.",
                [_REQUIRED_LINK],
                _VALIDATION_GATE,
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source snapshots path bounds and the required query parameter schema.",
                [_OPENAPI_SCHEMA_LINK],
                _OPENAPI_GATE,
            ),
        },
    ),
    "tests/test_tutorial/test_path_params_numeric_validations/test_tutorial006.py": _entry(
        "Combined numeric path/query constraints, request validation, and OpenAPI.",
        {
            "test_read_items": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source checks valid lower and upper path bounds with constrained query values.",
                [_TAIL_READ_LINK],
                _RESPONSE_GATE,
            ),
            "test_read_items_item_id_less_than_zero": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the inclusive lower path bound.",
                [_TAIL_NEGATIVE_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_item_id_greater_than_one_thousand": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the inclusive upper path bound.",
                [_TAIL_GREATER_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_size_too_small": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the exclusive lower query bound.",
                [_TAIL_SIZE_LOW_LINK],
                _VALIDATION_GATE,
            ),
            "test_read_items_size_too_large": _function(
                ["request-validation", "public-api-errors"],
                _HTTP,
                "The source checks the exclusive upper query bound.",
                [_TAIL_SIZE_HIGH_LINK],
                _VALIDATION_GATE,
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI_SELECTORS,
                "The source snapshots the combined numeric path and query schemas.",
                [_TAIL_OPENAPI_LINK],
                _OPENAPI_GATE,
            ),
        },
    ),
}
