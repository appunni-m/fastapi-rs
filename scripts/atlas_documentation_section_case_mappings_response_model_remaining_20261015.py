"""Reviewed mappings for the remaining response-model tutorial sections."""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        mapping["action_ids"] = actions
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


_TUTORIALS = "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml"
_RETURN_ANNOTATIONS = (
    "tests/fixtures/input-recipes/parity/response-model-return-annotation-focused-upstream.yaml"
)
_CONSTRUCTION = (
    "tests/fixtures/input-recipes/parity/tutorial-response-model003_04-construction-review.yaml"
)
_TUTORIAL_REVIEW = "tests/fixtures/input-recipes/parity/response-model-tutorial-review.yaml"

DOC_SECTION_CASE_MAPPINGS_RESPONSE_MODEL_REMAINING_20261015 = {
    ("tutorial/response-model.md", "response-model-return-type"): _excluded(
        "Response Model - Return Type { #response-model-return-type }",
        1,
        348,
        (
            "This page-level overview combines response validation, OpenAPI schema generation, "
            "serialization, and filtering that its child sections discuss separately. Its speed "
            "claim is qualitative and declares no comparable workload or measurement boundary, "
            "so the span defines no single independently observable case."
        ),
        (
            "The pinned H1 is an overview, not a separate endpoint or API contract. Concrete "
            "response-model actions are mapped in the focused child sections, and the broad "
            "performance statement cannot be established by a behavior selector."
        ),
    ),
    ("tutorial/response-model.md", "response-model-parameter"): _workflow(
        "`response_model` Parameter { #response-model-parameter }",
        23,
        68,
        _TUTORIALS,
        ["fastapi.response-model.tutorial001-defaults-and-list-output"],
        ["list-items-with-model-defaults"],
        ["http.body.bytes", "http.status"],
        (
            "The selected GET returns a list of dictionaries through an explicitly declared "
            "list response model and observes the serialized HTTP result. It samples one list "
            "response-model declaration; it does not claim every path-operation method or "
            "decorator/annotation precedence."
        ),
        (
            "FastAPI uses the path-operation decorator's response_model to create the response "
            "field for a list output; Pydantic validates and serializes the model values."
        ),
    ),
    ("tutorial/response-model.md", "response-model-priority"): _workflow(
        "`response_model` Priority { #response-model-priority }",
        61,
        68,
        _RETURN_ANNOTATIONS,
        ["fastapi.response-model-return-annotation.decorator-precedence"],
        ["decorator-model-over-annotation"],
        ["http.body.bytes", "http.status"],
        (
            "The endpoint declares a response_model different from its return annotation and "
            "returns data with fields incompatible with that annotation. The selected response "
            "body and status sample the explicit decorator model taking precedence; the case "
            "does not claim static type-checker behavior or all response-model options."
        ),
        (
            "FastAPI selects the explicit response_model when a path operation also has a "
            "return annotation, then validates and serializes the returned value against that "
            "response field."
        ),
    ),
    ("tutorial/response-model.md", "fastapi-data-filtering"): _excluded(
        "FastAPI Data Filtering { #fastapi-data-filtering }",
        161,
        168,
        (
            "This nested explanation restates the return-annotation filtering behavior already "
            "covered by the parent `Return Type and Data Filtering` section's selected POST and "
            "OpenAPI actions; it introduces no additional endpoint input or filtering option."
        ),
        (
            "The parent section's existing case returns a derived input model under its base "
            "return annotation and observes the filtered response. Mapping this nested prose "
            "again would duplicate that same behavior and selectors."
        ),
    ),
    ("tutorial/response-model.md", "see-it-in-the-docs"): _excluded(
        "See it in the docs { #see-it-in-the-docs }",
        169,
        178,
        (
            "This section points to static screenshots of the interactive documentation and "
            "repeats that the input and output models have JSON Schemas; it adds no request, "
            "schema option, or docs-route behavior beyond the already mapped return-annotation "
            "OpenAPI action."
        ),
        (
            "The relevant public schema is already selected in the parent `Return Type and Data "
            "Filtering` workflow. The screenshots are not an independent runtime input, and this "
            "section does not specify a separate observable docs UI contract."
        ),
    ),
    ("tutorial/response-model.md", "other-return-type-annotations"): _excluded(
        "Other Return Type Annotations { #other-return-type-annotations }",
        179,
        222,
        (
            "This parent section introduces a group of child cases for direct Response values, "
            "Response subclasses, invalid annotations, and response_model=None. The children "
            "carry those distinct inputs; the umbrella text adds no separate endpoint behavior."
        ),
        (
            "The pinned heading is an introduction to independently reviewed child sections. "
            "Its only distinct construction-error behavior is mapped under `Invalid Return Type "
            "Annotations`; other concrete response cases have existing child mappings."
        ),
    ),
    ("tutorial/response-model.md", "invalid-return-type-annotations"): _workflow(
        "Invalid Return Type Annotations { #invalid-return-type-annotations }",
        201,
        210,
        _CONSTRUCTION,
        ["fastapi.tutorial-response-model003-04.invalid-union-return-annotation"],
        None,
        [
            "construction.exception_class",
            "construction.exception_message",
            "construction.outcome",
        ],
        (
            "The input constructs an app whose endpoint annotation is `Response | dict`; it "
            "observes construction outcome and the exception class/message. This samples that "
            "invalid union only and does not claim every unsupported Pydantic field type."
        ),
        (
            "FastAPI derives a response field from a return annotation when response_model is "
            "not disabled, and rejects this union during route construction because it is not "
            "a valid Pydantic response field."
        ),
    ),
    ("tutorial/response-model.md", "response-model-encoding-parameters"): _excluded(
        "Response Model encoding parameters { #response-model-encoding-parameters }",
        223,
        343,
        (
            "This section is an umbrella for default-field omission, include/exclude options, "
            "and list-based filters. Its concrete behaviors are represented by the nested "
            "response_model_exclude_unset, include/exclude, same-default, and list subsections; "
            "the introductory model/default prose has no separate request input."
        ),
        (
            "The pinned heading groups child options rather than declaring another operation. "
            "Its runtime claims are scoped by the existing and newly reviewed child mappings, "
            "so a parent-level mapping would duplicate and broaden those cases."
        ),
    ),
    (
        "tutorial/response-model.md",
        "data-with-the-same-values-as-the-defaults",
    ): _workflow(
        "Data with the same values as the defaults { #data-with-the-same-values-as-the-defaults }",
        282,
        309,
        _TUTORIAL_REVIEW,
        ["fastapi.response-model-review.tutorial004-explicit-null-defaults"],
        ["read-record-with-explicit-null-and-default-values"],
        ["http.body.bytes", "http.status"],
        (
            "The selected GET returns source fields explicitly set to the model defaults "
            "including null, the numeric default, and an empty list while exclude_unset is "
            "enabled. It samples this input shape only."
        ),
        (
            "FastAPI forwards response_model_exclude_unset to response serialization; Pydantic "
            "retains fields explicitly present in the returned data even when their values equal "
            "the declared defaults."
        ),
    ),
    ("tutorial/response-model.md", "using-lists-instead-of-sets"): _workflow(
        "Using `list`s instead of `set`s { #using-lists-instead-of-sets }",
        338,
        343,
        _TUTORIAL_REVIEW,
        ["fastapi.response-model-review.tutorial006-list-based-filters"],
        ["include-selected-fields-from-list-option"],
        ["http.body.bytes", "http.status"],
        (
            "The selected GET uses a list for response_model_include and observes its filtered "
            "HTTP response. The paired exclude route uses a set, so it is deliberately omitted; "
            "tuple conversion and other list-based parameters are not claimed."
        ),
        (
            "FastAPI normalizes the documented list-valued include option before response "
            "serialization; the selected input exercises one include list and no tuple or "
            "list-valued exclude option."
        ),
    ),
}
