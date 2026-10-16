"""Reviewed section mappings for the query and header parameter tutorials.

All workflow links reuse existing input-only recipes with exact pinned-page
source evidence. No expected outputs or upstream test bodies are added here.
FastAPI source citations refer to 0.141.1 at 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f.
"""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    row = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": list(selectors),
        "scope_note": note,
        "rationale": rationale,
    }
    return row


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_P = "tests/fixtures/input-recipes/parity/"
_FIRST = _P + "first-asgi-request.yaml"
_REQUEST_PARAMETERS = _P + "request-validation-parameters.yaml"
_QUERY_MODELS = _P + "query-param-models.yaml"
_REQUEST_SCHEMA = _P + "docs-request-schema.yaml"
_HTTP = ["http.body.bytes", "http.status"]
_HTTP_HEADERS = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_HEADERS_ASGI = [*_HTTP_HEADERS, "asgi.send.message_types"]


DOC_SECTION_CASE_MAPPINGS_QUERY_HEADER_PARAMETERS_20261015 = {
    ("tutorial/query-params.md", "query-parameters"): _excluded(
        "Query Parameters { #query-parameters }",
        1,
        188,
        (
            "The H1 is a page-level container whose Markdown span includes all nested query "
            "sections. Concrete query behaviors are reviewed under their own headings."
        ),
        (
            "The pinned H1 names a page containing defaults, optional values, conversion, "
            "mixed path/query, and required-parameter sections. A single case cannot "
            "represent that combined scope; child headings carry the reviewed mappings."
        ),
    ),
    ("tutorial/query-params.md", "defaults"): _workflow(
        "Defaults { #defaults }",
        31,
        59,
        _FIRST,
        ["fastapi.first-slice.create-item-optional-query-default"],
        ["post-item"],
        _HTTP_HEADERS_ASGI,
        (
            "The action samples an omitted optional query field alongside a path value and "
            "observes the response. It does not reproduce the tutorial's numeric skip/limit "
            "defaults or test explicit overrides. The recipe also observes generic ASGI "
            "send message types; that harness selector is not an additional query claim."
        ),
        (
            "The pinned section explains that a missing query value receives the endpoint "
            "default (docs/en/docs/tutorial/query-params.md:31-59). Its linked page-backed "
            "input omits an optional query value; FastAPI's multidict extraction returns the "
            "field default when the input is absent "
            "(fastapi/dependencies/utils.py:749-777)."
        ),
    ),
    ("tutorial/query-params.md", "optional-parameters"): _workflow(
        "Optional parameters { #optional-parameters }",
        60,
        73,
        _FIRST,
        ["fastapi.first-slice.create-item-optional-query-default"],
        ["post-item"],
        _HTTP_HEADERS_ASGI,
        (
            "The existing page-backed action omits one optional query value and observes "
            "the resulting response. It does not test a supplied value or reproduce the "
            "tutorial002 q parameter. The recipe also observes generic ASGI send message "
            "types; that harness selector is not an additional query claim."
        ),
        (
            "The pinned section declares q optional with a None default "
            "(docs/en/docs/tutorial/query-params.md:60-73). FastAPI binds the query value "
            "and applies its declared default when absent "
            "(fastapi/dependencies/utils.py:749-777); the recipe covers only omission."
        ),
    ),
    ("tutorial/query-params.md", "query-parameter-type-conversion"): _excluded(
        "Query parameter type conversion { #query-parameter-type-conversion }",
        74,
        112,
        (
            "The section's bool spellings describe Pydantic field coercion; this mapping set "
            "does not include a page-cited bool input case."
        ),
        (
            "The pinned section's concrete claim is that short: bool accepts several true "
            "spellings (docs/en/docs/tutorial/query-params.md:74-112; "
            "docs_src/query_params/tutorial003_py310.py:8-10). FastAPI passes typed query "
            "values through its field-validation path, while Pydantic 2.13.4 owns primitive "
            "field coercion. Existing page-backed query cases sample required/missing and "
            "integer validation, not this boolean lexical contract "
            "(fastapi/dependencies/utils.py:734-743, 780-861)."
        ),
    ),
    ("tutorial/query-params.md", "multiple-path-and-query-parameters"): _workflow(
        "Multiple path and query parameters { #multiple-path-and-query-parameters }",
        113,
        122,
        _FIRST,
        ["fastapi.first-slice.create-item-optional-query-default"],
        ["post-item"],
        _HTTP_HEADERS_ASGI,
        (
            "The linked operation combines one path value with an omitted optional query "
            "value and a JSON body. It does not vary the Python declaration order or "
            "supply the tutorial004 query values. The recipe also observes generic ASGI "
            "send message types; that harness selector is not an additional query claim."
        ),
        (
            "The pinned section states that path and query parameters can coexist in one "
            "operation (docs/en/docs/tutorial/query-params.md:113-122). The selected "
            "page-backed request includes the route path value and a query field. FastAPI "
            "classifies path fields separately from inferred query fields "
            "(fastapi/dependencies/utils.py:490-520, 550-563)."
        ),
    ),
    ("tutorial/query-params.md", "required-query-parameters"): _workflow(
        "Required query parameters { #required-query-parameters }",
        123,
        188,
        _REQUEST_PARAMETERS,
        ["fastapi.request-parameters.query.required-missing"],
        ["get-required-query-missing"],
        _HTTP,
        (
            "The action samples the validation response for one omitted required query "
            "value. It does not sample the present value, the tutorial006 mixed signature, "
            "or OpenAPI required status."
        ),
        (
            "The pinned section says that a query parameter with no default is required "
            "and shows its missing-input error (docs/en/docs/tutorial/query-params.md:123-188). "
            "FastAPI treats a parameter without a default as required and produces a missing "
            "field error during request validation (fastapi/dependencies/utils.py:490-506, "
            "734-743, 749-777)."
        ),
    ),
    ("tutorial/header-params.md", "header-parameters"): _excluded(
        "Header Parameters { #header-parameters }",
        1,
        91,
        (
            "The H1 is a page-level container whose Markdown span includes all nested Header "
            "sections. Concrete Header behaviors are reviewed under their own headings."
        ),
        (
            "The pinned H1 names a page and its span includes import, declaration, alias "
            "conversion, duplicate-header, and recap sections. Those child headings carry "
            "the distinct evidence and input mappings."
        ),
    ),
    ("tutorial/header-params.md", "import-header"): _excluded(
        "Import `Header` { #import-header }",
        5,
        10,
        "This section gives import syntax and a code listing, not request or schema behavior.",
        (
            "The pinned lines show `from fastapi import Header` and the example import "
            "(docs/en/docs/tutorial/header-params.md:5-10). Export identity is recorded by "
            "the API manifest; the import-only text has no separate HTTP observation."
        ),
    ),
    ("tutorial/header-params.md", "declare-header-parameters"): _workflow(
        "Declare `Header` parameters { #declare-header-parameters }",
        11,
        32,
        _FIRST,
        ["fastapi.first-slice.create-item-valid"],
        ["post-item"],
        _HTTP_HEADERS_ASGI,
        (
            "The linked operation samples one required aliased Header dependency and "
            "observes its HTTP response. It does not cover missing-header validation, "
            "OpenAPI projection, optional defaults, or additional Header constraints."
        ),
        (
            "The pinned section explains that Header marks values as header parameters "
            "(docs/en/docs/tutorial/header-params.md:11-32). The page-backed workload uses "
            "a required x_actor Header alias; FastAPI classifies it into the header field "
            "collection and resolves it from request headers "
            "(fastapi/params.py:303-316; fastapi/dependencies/utils.py:399-442, 550-563, "
            "681-697). The recipe also records ASGI send message types as a generic "
            "harness observation, which is not a separate Header claim."
        ),
    ),
    ("tutorial/header-params.md", "automatic-conversion"): _workflow(
        "Automatic conversion { #automatic-conversion }",
        33,
        56,
        _P + "header-convert-underscores-documentation-20261017.yaml",
        [
            "fastapi.header.automatic-conversion.default-hyphen-wire-name-review-20261017",
            "fastapi.header.automatic-conversion.preserved-underscore-wire-name-review-20261017",
        ],
        ["send-header"],
        _HTTP,
        (
            "The two page-backed actions send a hyphenated header for default conversion "
            "and an underscore-named header with convert_underscores=False, then observe "
            "the resolved values. The proxy and server restrictions in the warning are "
            "not exercised."
        ),
        (
            "The pinned section documents default underscore-to-hyphen conversion and the "
            "explicit Header(convert_underscores=False) opt-out "
            "(docs/en/docs/tutorial/header-params.md:41-49). FastAPI 0.141.1 declares "
            "the flag on Header and stores it on the field info "
            "(fastapi/params.py:303-316, 352-353), then selects a hyphenated alias only "
            "when conversion is enabled (fastapi/dependencies/utils.py:524-528). The two "
            "independent requests send request-label for Header() and request_label for "
            "Header(convert_underscores=False). Starlette 1.6.0 performs case-insensitive "
            "lookup for the already selected header name (starlette/datastructures.py:537-539)."
        ),
    ),
    ("tutorial/header-params.md", "duplicate-headers"): _workflow(
        "Duplicate headers { #duplicate-headers }",
        57,
        86,
        _REQUEST_PARAMETERS,
        ["fastapi.request-parameters.header.repeated-values"],
        ["get-repeated-header-values"],
        _HTTP,
        (
            "The page-backed action sends two x-token header fields to a list-valued "
            "Header parameter and observes the response. It does not claim ordering or "
            "other client/server wire conventions."
        ),
        (
            "The pinned section declares a list-valued header and shows two X-Token values "
            "(docs/en/docs/tutorial/header-params.md:57-86). FastAPI retrieves all values "
            "for a sequence field through the Starlette 1.6.0 Headers interface before "
            "field validation (fastapi/dependencies/utils.py:749-777, 780-821); Starlette "
            "owns generic header collection behavior."
        ),
    ),
    ("tutorial/header-params.md", "recap"): _excluded(
        "Recap { #recap }",
        87,
        91,
        "This recap repeats Header declaration and underscore conversion already covered above.",
        (
            "The pinned recap adds no new parameter declaration or input example "
            "(docs/en/docs/tutorial/header-params.md:87-91). Its claims are linked to the "
            "declaration and conversion sections."
        ),
    ),
    ("tutorial/query-param-models.md", "query-parameter-models"): _excluded(
        "Query Parameter Models { #query-parameter-models }",
        1,
        68,
        (
            "The H1 is a page-level container whose Markdown span includes model, docs, "
            "extra-policy, and summary sections."
        ),
        (
            "The pinned H1 names a page containing multiple query-model claims; child "
            "headings carry their own evidence and reviewed input scope."
        ),
    ),
    ("tutorial/query-param-models.md", "query-parameters-with-a-pydantic-model"): _workflow(
        "Query Parameters with a Pydantic Model { #query-parameters-with-a-pydantic-model }",
        13,
        20,
        _QUERY_MODELS,
        ["fastapi.query-param-models.grouped-repeated-list"],
        ["get-items-with-repeated-tags"],
        _HTTP,
        (
            "The existing FilterParams-shaped workflow samples repeated tag values and "
            "observes the constructed model response. Its independent route does not claim "
            "field-for-field equality with the tutorial's literal response or its OpenAPI schema."
        ),
        (
            "The pinned example places a Pydantic FilterParams model in Query and returns "
            "the constructed model (docs/en/docs/tutorial/query-param-models.md:13-20; "
            "docs_src/query_param_models/tutorial001_an_py310.py:9-18). FastAPI recognizes "
            "BaseModel query parameters and extracts model fields during request resolution "
            "(fastapi/dependencies/utils.py:540-545, 780-850). Pydantic owns field validation."
        ),
    ),
    ("tutorial/query-param-models.md", "check-the-docs"): _excluded(
        "Check the Docs { #check-the-docs }",
        21,
        28,
        (
            "This section points to a static screenshot; the linked model workflow observes "
            "OpenAPI, not rendered /docs UI."
        ),
        (
            "The pinned section links to /docs and embeds a static screenshot "
            "(docs/en/docs/tutorial/query-param-models.md:21-28). The selected page-backed "
            "model action observes the endpoint response; it does not request or render "
            "the docs UI."
        ),
    ),
    ("tutorial/query-param-models.md", "forbid-extra-query-parameters"): _excluded(
        "Forbid Extra Query Parameters { #forbid-extra-query-parameters }",
        29,
        59,
        (
            "The section's extra='forbid' rule is Pydantic model policy; no page-cited "
            "workflow links that exact tutorial002 policy."
        ),
        (
            "The pinned example explicitly sets model_config extra='forbid' and describes "
            "Pydantic rejecting the undeclared tool field "
            "(docs/en/docs/tutorial/query-param-models.md:29-59; "
            "docs_src/query_param_models/tutorial002_an_py310.py:9-19). Pydantic owns that "
            "model policy. FastAPI's query-model extraction is mapped in the preceding "
            "section; this mapping does not claim the extra-policy response without a "
            "page-cited input workflow."
        ),
    ),
    ("tutorial/query-param-models.md", "summary"): _excluded(
        "Summary { #summary }",
        60,
        68,
        (
            "The section restates query-model use and points forward to cookie/header models; "
            "it adds no request example."
        ),
        (
            "The pinned summary and spoiler contain no new endpoint or parameter configuration "
            "(docs/en/docs/tutorial/query-param-models.md:60-68). Query extraction is mapped "
            "above, and header-model extraction is mapped on its own page."
        ),
    ),
    ("tutorial/header-param-models.md", "header-parameter-models"): _excluded(
        "Header Parameter Models { #header-parameter-models }",
        1,
        72,
        (
            "The H1 is a page-level container whose Markdown span includes model, docs, "
            "extra-policy, underscore, and summary sections."
        ),
        (
            "The pinned H1 names a page containing multiple header-model claims; child "
            "headings carry their own evidence and reviewed input scope."
        ),
    ),
    ("tutorial/header-param-models.md", "header-parameters-with-a-pydantic-model"): _workflow(
        "Header Parameters with a Pydantic Model { #header-parameters-with-a-pydantic-model }",
        13,
        20,
        _REQUEST_SCHEMA,
        ["fastapi.docs.request-schema.tutorial-header-param-models.header-model"],
        ["dispatch"],
        _HTTP_HEADERS,
        (
            "The selected workflow uses a two-field header model analogue and dispatches one "
            "request. It does not claim the literal CommonHeaders field set, OpenAPI "
            "projection, or the other sections' extra/underscore policies."
        ),
        (
            "The pinned example declares a Pydantic CommonHeaders model through Header and "
            "returns it (docs/en/docs/tutorial/header-param-models.md:13-20; "
            "docs_src/header_param_models/tutorial001_an_py310.py:9-18). FastAPI detects a "
            "single model-valued header parameter, extracts its fields from request headers, "
            "and validates the assembled model (fastapi/dependencies/utils.py:780-850); "
            "Starlette 1.6.0 owns generic Headers access."
        ),
    ),
    ("tutorial/header-param-models.md", "check-the-docs"): _excluded(
        "Check the Docs { #check-the-docs }",
        21,
        28,
        (
            "This section points to a static screenshot; the linked header-model workflow "
            "observes OpenAPI, not rendered /docs UI."
        ),
        (
            "The pinned section links to /docs and embeds a static screenshot "
            "(docs/en/docs/tutorial/header-param-models.md:21-28). The page-backed model "
            "workflow selects its HTTP response action, not OpenAPI or the docs UI."
        ),
    ),
    ("tutorial/header-param-models.md", "forbid-extra-headers"): _excluded(
        "Forbid Extra Headers { #forbid-extra-headers }",
        29,
        53,
        (
            "The section's extra='forbid' rule is Pydantic model policy; no page-cited "
            "workflow links that exact tutorial002 policy."
        ),
        (
            "The pinned example configures CommonHeaders with extra='forbid' and describes "
            "Pydantic rejecting an undeclared tool header "
            "(docs/en/docs/tutorial/header-param-models.md:29-53; "
            "docs_src/header_param_models/tutorial002_an_py310.py:9-20). Pydantic owns that "
            "model policy. FastAPI's header-model extraction is mapped in the preceding "
            "section; this mapping does not claim the extra-policy response without a "
            "page-cited input workflow."
        ),
    ),
    ("tutorial/header-param-models.md", "disable-convert-underscores"): _workflow(
        "Disable Convert Underscores { #disable-convert-underscores }",
        54,
        69,
        _P + "header-convert-underscores-documentation-20261017.yaml",
        ["fastapi.header.models.convert-underscores-false.field-name-review-20261017"],
        ["get-model-underscore-header"],
        _HTTP,
        (
            "The page-backed request supplies the underscore-named header matching one "
            "required model field and observes the response value. It does not sample "
            "default model conversion, extra-header policy, OpenAPI, or the proxy/server "
            "warning. Pydantic's string validation and response serialization are not "
            "separate claims in this row."
        ),
        (
            "The pinned section applies Header(convert_underscores=False) to a Pydantic "
            "header model, after explaining the default `save_data`-to-`save-data` alias "
            "conversion (docs/en/docs/tutorial/header-param-models.md:56-62). The "
            "independent request sends request_label using the model field's exact "
            "underscore name. FastAPI 0.141.1 expands the single model into header fields, "
            "reads convert_underscores from the top-level Header, and only rewrites field "
            "names when the flag is true (fastapi/dependencies/utils.py:793-803, 809-824). "
            "Starlette 1.6.0 retrieves the selected key without underscore conversion "
            "(starlette/datastructures.py:537-539); Pydantic owns validation of the "
            "resulting string model field, not FastAPI's header-name selection."
        ),
    ),
    ("tutorial/header-param-models.md", "summary"): _excluded(
        "Summary { #summary }",
        70,
        72,
        (
            "This is a one-sentence recap of the Header model behavior mapped in the "
            "preceding section."
        ),
        (
            "The pinned summary has no new model declaration or request example "
            "(docs/en/docs/tutorial/header-param-models.md:70-72). Model extraction is linked "
            "to the preceding section's selected workflow."
        ),
    ),
}
