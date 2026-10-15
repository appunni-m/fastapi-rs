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
            "The pinned FastAPI 0.141.1 heading spans "
            "docs/en/docs/tutorial/request-forms.md#L23-L46; its referenced source example "
            "declares `username` and `password` with `Annotated[str, Form()]` and returns "
            "the username (docs_src/request_forms/tutorial001_an_py310.py#L8-L10). The "
            "input-only recipe selects the matching annotated action and cites both pinned "
            "request-form documentation examples; its independently authored workload has "
            "the same two required fields and returns only the username. FastAPI 0.141.1 "
            "defines `Form` as a `Body` subclass with the URL-encoded media type "
            "(fastapi/params.py#L581-L589), identifies a Form body and asks the request for "
            "form data (fastapi/routing.py#L395, #L425-L431), then extracts and validates "
            "the declared fields (fastapi/dependencies/utils.py#L972-L998). Starlette "
            "1.6.0 owns generic URL-encoded form decoding: `Request._get_form` selects "
            "`FormParser` from the content type (starlette/requests.py#L268-L311), and "
            "`FormParser` builds the `FormData` items (starlette/formparsers.py#L105-L141). "
            "The recipe records inputs and selected observations, not expected outputs or "
            "a parity result."
        ),
    },
}
