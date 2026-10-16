"""Reviewed mapping for the FastAPI form-model extra-field tutorial section."""

DOC_SECTION_CASE_MAPPINGS_EXTRA_FORM_FIELDS_20261015 = {
    ("tutorial/request-form-models.md", "forbid-extra-form-fields"): {
        "heading": "Forbid Extra Form Fields { #forbid-extra-form-fields }",
        "start_line": 39,
        "end_line": 75,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/docs-example-wave-f-form-file-inputs.yaml"
        ),
        "case_ids": ["fastapi.docs-example-wave-f.request-form-models.extra-forbidden"],
        "action_ids": ["strict-form-model-annotated"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "The selected action posts URL-encoded username and password fields plus one "
            "undeclared scalar field to the independently authored Annotated Form-model "
            "route. Its observations select response status and body bytes, so they capture "
            "the validation-error response for this extra field. It directly samples the "
            "documented `extra=forbid` failure path, but does not establish that the error "
            "body matches the documentation's literal field name or values, the plain "
            "parameter declaration, other extra-field shapes, missing-field behavior, "
            "multipart parsing, or OpenAPI output."
        ),
        "rationale": (
            "The pinned FastAPI 0.141.1 section at "
            "docs/en/docs/tutorial/request-form-models.md:39-74 explains forbidding "
            "undeclared form fields and shows the extra-field error; its included snippet "
            "is docs_src/request_form_models/tutorial002_an_py310.py:9-16, whose model "
            "sets `extra` to `forbid` and whose route uses `Annotated[FormData, Form()]`. "
            "The existing input-only case "
            "fastapi.docs-example-wave-f.request-form-models.extra-forbidden selects "
            "strict-form-model-annotated, which sends declared username/password fields "
            "and an independent `unexpected` field to the workload's matching "
            "StrictLoginForm configuration and Annotated route "
            "(tests/fixtures/workloads/request_form_upload_source_review_independent.py:17-20,"
            "217-221). "
            "That action observes recipe selectors `status` and `body`, projected here to "
            "`http.status` and `http.body.bytes`; the recipe contains no expected output. "
            "FastAPI 0.141.1 calls `request.form()` for Form bodies "
            "(fastapi/routing.py:425-432), collects model fields and preserves remaining "
            "form keys before model validation "
            "(fastapi/dependencies/utils.py:912-948,965-979); Pydantic owns rejection "
            "under the model's `extra=forbid` configuration. Starlette 1.6.0 is the sole "
            "generic form-parsing oracle: `Request._get_form` selects `FormParser` for "
            "URL-encoded input (starlette/requests.py:296-310), and the parser returns "
            "the received name/value pairs as `FormData` "
            "(starlette/formparsers.py:105-143). The repository pins FastAPI 0.141.1 "
            "and Starlette 1.6.0 in metadata.yaml:9-12,41-46; the checked source "
            "checkout commits are 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f and "
            "4f250d6b814587e20c5365f0a5f0c4d42bcb929f, respectively."
        ),
    },
}
