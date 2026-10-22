"""Reviewed mapping for the FastAPI form-parameter tutorial section."""

_RECIPE = "tests/fixtures/input-recipes/parity/docs-example-wave-f-form-file-inputs.yaml"
_HTTP = ["http.body.bytes", "http.status"]


DOC_SECTION_CASE_MAPPINGS_FORM_PARAMETERS_20261015 = {
    ("tutorial/request-forms.md", "define-form-parameters"): {
        "heading": "Define `Form` parameters { #define-form-parameters }",
        "start_line": 23,
        "end_line": 46,
        "recipe_path": _RECIPE,
        "case_ids": ["fastapi.docs-example-wave-f.request-forms.required-fields"],
        "action_ids": ["form-fields-annotated"],
        "observation_selectors": _HTTP,
        "scope_note": (
            "The selected action sends two required `Annotated[str, Form()]` fields as "
            "`application/x-www-form-urlencoded` and observes the response status and body "
            "bytes; the independent handler returns the submitted username. The recipe uses "
            "the `standard-multipart` profile to provide form-parser dependencies but does "
            "not sample a missing-parser case. It covers this two-field annotated declaration "
            "only, not `Form` inheritance, aliases, validation, examples, alternate "
            "declarations, or a JSON comparison."
        ),
        "rationale": (
            "The pinned FastAPI 0.157.0 heading spans "
            "docs/en/docs/tutorial/request-forms.md#L23-L46; its referenced source example "
            "declares `username` and `password` with `Annotated[str, Form()]` and returns "
            "the username (docs_src/request_forms/tutorial001_an_py310.py#L8-L10). The "
            "input-only recipe selects the matching annotated action and cites both pinned "
            "request-form documentation examples; its independently authored workload has "
            "the same two required fields and returns only the username. FastAPI 0.157.0 "
            "defines `Form` as a `Body` subclass with the URL-encoded media type "
            "(fastapi/params.py#L614-L650), identifies a Form body and asks the request for "
            "form data (fastapi/routing.py#L398-L457), then extracts and validates the "
            "declared fields (fastapi/dependencies/utils.py#L1138-L1234). Starlette "
            "1.6.0 owns generic URL-encoded form decoding: `Request._get_form` selects "
            "`FormParser` from the content type (starlette/requests.py#L268-L311), and "
            "`FormParser` builds the `FormData` items (starlette/formparsers.py#L105-L141). "
            "The recipe records inputs and selected observations, not expected outputs or "
            "a parity result."
        ),
    },
    ("tutorial/request-forms.md", "boolean-form-fields"): {
        "heading": "Boolean Form Fields { #boolean-form-fields }",
        "start_line": 47,
        "end_line": 52,
        "recipe_path": "tests/fixtures/input-recipes/parity/request-nullable-defaults-0157.yaml",
        "case_ids": ["fastapi.request-parameters.nullable-defaults.form"],
        "action_ids": ["form-checkbox-default"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "The selected action omits a standalone `bool` form field declared with a "
            "default of `True` and observes its response, covering the unchecked-checkbox "
            "case. It does not sample a checked checkbox, a nullable `bool | None` field "
            "with a `None` default, browser form construction, or JSON/Pydantic validation."
        ),
        "rationale": (
            "The new section says omitted unchecked-checkbox fields of type `bool` or "
            "`bool | None` become `False` even when the default is `True` or `None`, and "
            "distinguishes JSON/direct Pydantic behavior "
            "(docs/en/docs/tutorial/request-forms.md:47-51). The selected 0.157 recipe "
            "uses the upstream default-True checkbox input shape but does not claim the "
            "nullable-None case or the separate Pydantic/model paragraph "
            "(tests/test_request_params/test_form/test_nullable_and_defaults.py:775-783). "
            "FastAPI's `_extract_form_items` converts an absent `bool` or `bool | None` "
            "form alias to `False` before validation "
            "(fastapi/dependencies/utils.py:1080-1118); request form extraction and "
            "field validation follow in `_extract_form_body` and `request_body_to_args` "
            "(fastapi/dependencies/utils.py:1138-1234). Starlette 1.6.0 provides the "
            "generic form parser, while this recipe supplies the post-parser ASGI input."
        ),
    },
}
