"""Reviewed mappings for the FastAPI request-form tutorial sections."""

_DOCS_REQUEST_SCHEMA = "tests/fixtures/input-recipes/parity/docs-request-schema.yaml"
_DOCS_FORM_FILE = "tests/fixtures/input-recipes/parity/docs-example-wave-f-form-file-inputs.yaml"
_REQUEST_MULTIPART = "tests/fixtures/input-recipes/parity/request-multipart.yaml"

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]
_OPENAPI = [
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_FORM_MODEL_DISPATCH_AND_OPENAPI = [
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
]


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


DOC_SECTION_CASE_MAPPINGS_REQUEST_FORMS_20261015 = {
    ("tutorial/request-form-models.md", "form-models"): _workflow(
        "Form Models { #form-models }",
        1,
        80,
        _DOCS_REQUEST_SCHEMA,
        ["fastapi.docs.request-schema.tutorial-request-form-models.form-model"],
        ["dispatch", "openapi"],
        _FORM_MODEL_DISPATCH_AND_OPENAPI,
        (
            "The selected `dispatch` action sends URL-encoded fields to an independent "
            "`Annotated[Preferences, Form()]` route and observes response body bytes, ordered "
            "headers, and status. `openapi` observes the `/preferences` request-body and "
            "component schema plus the `/openapi.json` status. The case cites this exact "
            "tutorial page and its form-model example. It samples an equivalent Pydantic-model "
            "form route and schema, not the tutorial's `username`/`password` values, its exact "
            "`/login/` response, Pydantic internals, parser-installation notes, or docs UI "
            "rendering. Child sections are mapped separately."
        ),
        (
            "FastAPI 0.157.0 defines `Form` as a `Body` subclass with the "
            "`application/x-www-form-urlencoded` media type (fastapi/params.py:614-700), "
            "recognizes Form bodies and calls `request.form()` (fastapi/routing.py:412-475), "
            "then extracts model fields and validates a top-level BaseModel "
            "(fastapi/dependencies/utils.py:1162-1215). The pinned section "
            "docs/en/docs/tutorial/request-form-models.md:1-38 links the model route in "
            "docs_src/request_form_models/tutorial001_an_py310.py:9-16. Recipe "
            "docs-request-schema.yaml case "
            "fastapi.docs.request-schema.tutorial-request-form-models.form-model records "
            "that exact page and example as source evidence; its selected dispatch/openapi "
            "actions project to the listed HTTP and OpenAPI selectors. FastAPI generates "
            "the schema through `FastAPI.openapi()` (fastapi/applications.py:1085-1118). "
            "Starlette 1.6.0 owns generic URL-encoded parsing: `Request._get_form` selects "
            "`FormParser` (starlette/requests.py:296-304), which returns the parsed pairs "
            "as `FormData` (starlette/formparsers.py:105-143)."
        ),
    ),
    ("tutorial/request-form-models.md", "pydantic-models-for-forms"): _workflow(
        "Pydantic Models for Forms { #pydantic-models-for-forms }",
        23,
        32,
        _DOCS_REQUEST_SCHEMA,
        ["fastapi.docs.request-schema.tutorial-request-form-models.form-model"],
        ["dispatch"],
        _HTTP,
        (
            "The selected action posts URL-encoded data to an independent route whose single "
            "body parameter is `Annotated[Preferences, Form()]`, returns that model, and "
            "observes response bytes, headers, and status. Its recipe case cites this exact "
            "page and the linked form-model example. It samples model-valued form extraction; "
            "the workload uses `display_name` and `notifications_enabled`, so it does not "
            "claim the tutorial's login field names, exact response, field-validation rules, "
            "or all Pydantic behavior. The added Boolean omission sentence at line 31 is "
            "explicitly excluded: this action sends `notifications_enabled=true`, and the "
            "separate Boolean Form mapping covers a scalar parameter rather than a model."
        ),
        (
            "The pinned FastAPI 0.157.0 section at "
            "docs/en/docs/tutorial/request-form-models.md:23-32 links "
            "docs_src/request_form_models/tutorial001_an_py310.py:9-16, which declares a "
            "Pydantic model and uses it as an `Annotated[..., Form()]` parameter. The exact "
            "page-evidenced docs-request-schema case "
            "fastapi.docs.request-schema.tutorial-request-form-models.form-model selects its "
            "`dispatch` action, whose HTTP body, ordered headers, and status are the claimed "
            "observations; the recipe sends `display_name=Amira&notifications_enabled=true` "
            "(tests/fixtures/input-recipes/parity/docs-request-schema.yaml:2292-2324). FastAPI "
            "extracts Form model fields in `request_body_to_args` and `_extract_form_items` "
            "(fastapi/dependencies/utils.py:1084-1118, 1162-1213); Pydantic supplies model "
            "validation. The 0.157.0 source explicitly infers `False` for missing boolean "
            "form fields (fastapi/dependencies/utils.py:1104-1117), and its upstream test "
            "covers both scalar and model checkbox inputs (tests/test_request_params/test_form/"
            "test_nullable_and_defaults.py:775-792). The linked recipe has no omitted-boolean "
            "model action, so that newly documented behavior remains excluded from this mapping. "
            "Starlette 1.6.0 supplies generic URL-encoded `FormData` parsing "
            "(starlette/requests.py:296-304; starlette/formparsers.py:105-143)."
        ),
    ),
    ("tutorial/request-form-models.md", "check-the-docs"): _workflow(
        "Check the Docs { #check-the-docs }",
        33,
        40,
        _DOCS_REQUEST_SCHEMA,
        ["fastapi.docs.request-schema.tutorial-request-form-models.form-model"],
        ["openapi"],
        _OPENAPI,
        (
            "The selected `openapi` action observes the `/openapi.json` response status and "
            "the generated `/preferences` request-body and `Preferences` component schema. "
            "This reviews structured schema data that a docs UI can render; it does not "
            "request `/docs`, render HTML or JavaScript, inspect browser output, or validate "
            "the screenshot/UI presentation shown by this section."
        ),
        (
            "The pinned section says to verify the form model in `/docs` and shows a UI "
            "screenshot (docs/en/docs/tutorial/request-form-models.md:31-38). The exact "
            "page-evidenced docs-request-schema case "
            "fastapi.docs.request-schema.tutorial-request-form-models.form-model selects an "
            "`openapi` action that requests `/openapi.json` and observes the request-body "
            "and component schema pointers. FastAPI builds and serves that schema through "
            "`FastAPI.openapi()` and its `/openapi.json` route "
            "(fastapi/applications.py:1070-1114). This is evidence for the underlying "
            "OpenAPI document, not for `/docs` HTML, JavaScript, or visual rendering."
        ),
    ),
    ("tutorial/request-form-models.md", "summary"): _excluded(
        "Summary { #summary }",
        78,
        80,
        (
            "The summary repeats the opening promise that Pydantic models can declare form "
            "fields. The model-form extraction behavior is already sampled in the `form-models` "
            "and `pydantic-models-for-forms` mappings, so this sentence adds no distinct request "
            "shape or observable operation."
        ),
        (
            "The pinned span at docs/en/docs/tutorial/request-form-models.md:76-78 is one "
            "recap sentence duplicating the page's opening and the mapped model-form example; "
            "a separate workflow would repeat the same dispatch observation."
        ),
    ),
    ("tutorial/request-forms-and-files.md", "request-forms-and-files"): _workflow(
        "Request Forms and Files { #request-forms-and-files }",
        1,
        41,
        _REQUEST_MULTIPART,
        ["fastapi.request-multipart.mixed.form-and-file"],
        ["dispatch"],
        _HTTP_BODY_STATUS,
        (
            "The exact-page-evidenced case sends one multipart `caption` field and one file "
            "part to an independent route, then observes response bytes and status. The H1 "
            "span includes the child sections, which are mapped separately. The sample does "
            "not cover the tutorial's two file types, import identity, parser-absent behavior, "
            "or the warning about combining multipart input with a JSON `Body`."
        ),
        (
            "The pinned H1 span docs/en/docs/tutorial/request-forms-and-files.md:1-41 says "
            "that `File` and `Form` can receive files and form fields together. The exact "
            "page-evidenced recipe case "
            "fastapi.request-multipart.mixed.form-and-file selects its `dispatch` action, "
            "which posts a multipart caption and file and projects to HTTP body bytes and "
            "status. The independent workload declares the corresponding `Form()` and "
            "`File()` parameters (tests/fixtures/workloads/request_multipart.py:83-89). "
            "FastAPI classifies and extracts these declared fields "
            "(fastapi/routing.py:395, 425-432; fastapi/dependencies/utils.py:912-948). "
            "Starlette 1.6.0 parses multipart input in `Request._get_form` "
            "(starlette/requests.py:282-295); the request does not exercise a JSON `Body` "
            "conflict or generic parser limits."
        ),
    ),
    ("tutorial/request-forms-and-files.md", "import-file-and-form"): _workflow(
        "Import `File` and `Form` { #import-file-and-form }",
        17,
        20,
        _REQUEST_MULTIPART,
        ["fastapi.request-multipart.mixed.form-and-file"],
        ["dispatch"],
        _HTTP_BODY_STATUS,
        (
            "The selected request succeeds through an independent route that imports and "
            "uses `File` and `Form` from `fastapi`, then observes response bytes and status. "
            "It shows functional use of these names, but does not directly inspect import "
            "paths, aliases, or object identity."
        ),
        (
            "The pinned section at docs/en/docs/tutorial/request-forms-and-files.md:17-19 "
            "links docs_src/request_forms_and_files/tutorial001_an_py310.py:1-3, which "
            "imports `File` and `Form` from `fastapi`. The exact-page-evidenced "
            "fastapi.request-multipart.mixed.form-and-file case uses both names in an "
            "independent mixed multipart route and observes HTTP body bytes and status. "
            "FastAPI's Form/File classification and request extraction are in "
            "fastapi/routing.py:395, 425-432; Starlette 1.6.0 owns multipart decoding "
            "(starlette/requests.py:282-295). This HTTP workflow does not test Python import "
            "identity."
        ),
    ),
    (
        "tutorial/request-forms-and-files.md",
        "define-file-and-form-parameters",
    ): _workflow(
        "Define `File` and `Form` parameters { #define-file-and-form-parameters }",
        21,
        38,
        _REQUEST_MULTIPART,
        ["fastapi.request-multipart.mixed.form-and-file"],
        ["dispatch"],
        _HTTP_BODY_STATUS,
        (
            "The selected multipart action sends a text `caption` and one uploaded file to "
            "an independent endpoint, which returns the caption, filename, and file size. "
            "It samples one form field and one `UploadFile`; it does not exercise the "
            "tutorial's separate `bytes` file parameter, multiple parameters, a JSON `Body` "
            "conflict, or all `File`/`Form` declarations."
        ),
        (
            "The pinned section docs/en/docs/tutorial/request-forms-and-files.md:21-38 "
            "links the `File`/`Form` declarations in "
            "docs_src/request_forms_and_files/tutorial001_an_py310.py:8-18 and explains "
            "their multipart request and the JSON-body protocol constraint. The exact page "
            "evidence on case fastapi.request-multipart.mixed.form-and-file selects a "
            "multipart `dispatch` with HTTP body/status observations. FastAPI identifies "
            "Form bodies and calls `request.form()` (fastapi/routing.py:395, 425-432), then "
            "extracts declared form/file values (fastapi/dependencies/utils.py:912-948). "
            "Starlette 1.6.0 performs generic multipart parsing "
            "(starlette/requests.py:282-295); the selected input does not test the separate "
            "JSON `Body` conflict described by the warning."
        ),
    ),
    ("tutorial/request-forms-and-files.md", "recap"): _excluded(
        "Recap { #recap }",
        39,
        41,
        (
            "The recap restates that `File` and `Form` are used together for files and form "
            "data. That mixed multipart request is already sampled by the H1 and parameter "
            "mappings, so the recap adds no distinct request shape or observable behavior."
        ),
        (
            "The pinned span docs/en/docs/tutorial/request-forms-and-files.md:39-41 contains "
            "one summary sentence duplicating the preceding mapped mixed-form/file request; "
            "a separate case would duplicate that observation."
        ),
    ),
    ("tutorial/request-forms.md", "form-data"): _workflow(
        "Form Data { #form-data }",
        1,
        79,
        _REQUEST_MULTIPART,
        ["fastapi.request-multipart.form.required-present"],
        ["dispatch"],
        _HTTP_BODY_STATUS,
        (
            "The selected URL-encoded request supplies one required form value and observes "
            "the response bytes and status. The recipe uses the standard multipart profile "
            "for parser availability; this action does not test an absent parser, a missing "
            "required field, JSON input, or the installation instructions."
        ),
        (
            "The pinned H1 span docs/en/docs/tutorial/request-forms.md:1-16 introduces "
            "`Form` for receiving form fields instead of JSON. The exact-page-evidenced "
            "case fastapi.request-multipart.form.required-present selects one "
            "`application/x-www-form-urlencoded` `dispatch` and observes HTTP body bytes "
            "and status. FastAPI defines the Form media type "
            "(fastapi/params.py:581-590) and calls `request.form()` for Form bodies "
            "(fastapi/routing.py:395, 425-432); Starlette 1.6.0 parses URL-encoded form "
            "pairs into `FormData` (starlette/requests.py:296-304; "
            "starlette/formparsers.py:105-143)."
        ),
    ),
    ("tutorial/request-forms.md", "import-form"): _workflow(
        "Import `Form` { #import-form }",
        17,
        22,
        _DOCS_FORM_FILE,
        ["fastapi.docs-example-wave-f.request-forms.required-fields"],
        ["form-fields-annotated"],
        _HTTP_BODY_STATUS,
        (
            "The selected action posts two URL-encoded required fields to the annotated "
            "independent route and observes response bytes and status. The case cites this "
            "exact page and its `Form` import example. It demonstrates functional use through "
            "the facade but does not inspect the import path, alias, or object identity."
        ),
        (
            "The pinned section at docs/en/docs/tutorial/request-forms.md:17-22 says to "
            "import `Form` from `fastapi` and links "
            "docs_src/request_forms/tutorial001_an_py310.py:1-3. Case "
            "fastapi.docs-example-wave-f.request-forms.required-fields records this exact "
            "page and example as source evidence; its `form-fields-annotated` action sends "
            "the two URL-encoded required fields and selects HTTP body bytes/status. The "
            "independent workload imports and applies `Form` "
            "(tests/fixtures/workloads/request_form_upload_source_review_independent.py:194-199). "
            "FastAPI's form-body classification is in fastapi/params.py:581-590 and "
            "fastapi/routing.py:395, 425-432; Starlette 1.6.0 owns URL-encoded parsing "
            "(starlette/requests.py:296-304; starlette/formparsers.py:105-143). The HTTP "
            "action does not check import identity."
        ),
    ),
    ("tutorial/request-forms.md", "about-form-fields"): _workflow(
        'About "Form Fields" { #about-form-fields }',
        53,
        76,
        _REQUEST_MULTIPART,
        [
            "fastapi.request-multipart.form.required-present",
            "fastapi.request-multipart.form.list-repeated",
        ],
        ["dispatch"],
        _HTTP_BODY_STATUS,
        (
            "The two exact-page-evidenced actions submit URL-encoded text fields: one required "
            "scalar and one repeated list value. They observe HTTP body bytes and status, "
            "sampling FastAPI's declared-field extraction over Starlette's URL-encoded form "
            "data. They do not exercise multipart file encoding, a JSON `Body` conflict, "
            "browser-generated requests, or parser-installation failures."
        ),
        (
            "The pinned section docs/en/docs/tutorial/request-forms.md:47-70 distinguishes "
            "URL-encoded form fields from JSON and notes that files use `multipart/form-data`. "
            "Cases fastapi.request-multipart.form.required-present and "
            "fastapi.request-multipart.form.list-repeated both record this exact page as "
            "source evidence; their `dispatch` actions exercise one scalar field and repeated "
            "list fields with HTTP body/status observations. FastAPI extracts each declared "
            "form field (fastapi/dependencies/utils.py:912-948, 981-998). Starlette 1.6.0 "
            "selects `FormParser` for URL-encoded input and builds `FormData` "
            "(starlette/requests.py:296-304; starlette/formparsers.py:105-143). Neither "
            "action samples multipart files or the separate JSON-body protocol warning."
        ),
    ),
    ("tutorial/request-forms.md", "recap"): _excluded(
        "Recap { #recap }",
        77,
        79,
        (
            "The recap repeats the instruction to use `Form` for form-data input, already "
            "covered by the H1, import, and form-field mappings. It adds no distinct request "
            "shape or observable behavior."
        ),
        (
            "The pinned span docs/en/docs/tutorial/request-forms.md:71-73 is one summary "
            "sentence restating the mapped Form declaration and URL-encoded field behavior; "
            "a separate workflow would duplicate existing request observations."
        ),
    ),
}
