"""Reviewed mappings for response cookies and status-code documentation sections."""


def _workflow(heading, start, end, recipe, cases, selectors, note, rationale, actions=None):
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


_COOKIE_PARAMETER = "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml"
_COOKIE_DIRECT = "tests/fixtures/input-recipes/parity/response-cookie-direct-wave.yaml"
_STATUS_CHANGE = "tests/fixtures/input-recipes/parity/response-change-status-tutorial-review.yaml"
_ADDITIONAL_STATUS = (
    "tests/fixtures/input-recipes/parity/additional-status-codes-tutorial-upstream.yaml"
)
_STATUS_TUTORIAL = (
    "tests/fixtures/input-recipes/parity/tutorial-response-status-code001-source-review.yaml"
)
_RESPONSE_SURFACE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_HTTP_RESPONSE = ["http.status", "http.headers.ordered", "http.body.bytes"]
_STATUS_AND_BODY = ["http.status", "http.body.bytes"]


DOC_SECTION_CASE_MAPPINGS_RESPONSE_COOKIES_STATUS_20261015 = {
    ("advanced/response-cookies.md", "response-cookies"): _excluded(
        "Response Cookies { #response-cookies }",
        1,
        51,
        (
            "This page combines two independently observable paths: an injected temporary "
            "Response and a directly returned Response. Those paths are mapped under their "
            "own headings; the nested technical details identify Starlette response behavior."
        ),
        (
            "The page heading is an overview of its child sections rather than a third cookie "
            "operation. The selected child inputs cover the documented FastAPI integration "
            "paths without claiming generic Starlette cookie behavior."
        ),
    ),
    ("advanced/response-cookies.md", "use-a-response-parameter"): _workflow(
        "Use a `Response` parameter { #use-a-response-parameter }",
        3,
        18,
        _COOKIE_PARAMETER,
        ["fastapi.test.test-tutorial-test-response-cookies-test-tutorial002.test-path-operation"],
        _HTTP_RESPONSE,
        (
            "The selected tutorial002 request sets one cookie on the injected temporary "
            "Response and returns a dictionary. It observes the final status, ordered headers, "
            "and body; dependency-set cookies, response-model filtering, middleware, and a "
            "client cookie jar are outside this input."
        ),
        (
            "FastAPI injects the temporary Response and carries its headers to the response "
            "built from the returned object. Starlette 1.6.0 owns cookie formatting and HTTP "
            "header emission."
        ),
        ["response-cookie"],
    ),
    ("advanced/response-cookies.md", "return-a-response-directly"): _workflow(
        "Return a `Response` directly { #return-a-response-directly }",
        19,
        51,
        _COOKIE_DIRECT,
        ["fastapi.response.cookies.direct-jsonresponse-set-cookie"],
        _HTTP_RESPONSE,
        (
            "The selected request constructs a JSONResponse, calls set_cookie, and returns "
            "that response. It observes the resulting status, ordered Set-Cookie header, and "
            "body. It does not test response-model bypass, cookie-jar behavior, or every "
            "Response subclass."
        ),
        (
            "FastAPI passes a directly returned Response through the route. Starlette 1.6.0 "
            "owns JSONResponse rendering, set_cookie formatting, and ASGI emission."
        ),
        ["create-cookie-response"],
    ),
    ("advanced/response-cookies.md", "more-info"): _excluded(
        "More info { #more-info }",
        39,
        51,
        (
            "This subsection gives FastAPI import conveniences and links to Starlette's "
            "generic set_cookie reference. The selected HTTP cases do not compare import paths "
            "or object identity, and cookie formatting/options belong to Starlette 1.6.0."
        ),
        (
            "The FastAPI re-exports are covered by the public API manifest and source "
            "authority; the link points readers to Starlette for the cookie API contract. "
            "Neither is a separate route behavior in these inputs."
        ),
    ),
    ("advanced/response-change-status-code.md", "response-change-status-code"): _excluded(
        "Response - Change Status Code { #response-change-status-code }",
        1,
        31,
        (
            "The title and introduction summarize the use case and temporary Response "
            "mechanism mapped under their child headings."
        ),
        (
            "The child use-case input observes the documented 200/201 outcomes, while the "
            "existing child mapping covers dependency status mutation and endpoint overwrite. "
            "The page heading adds no independent operation."
        ),
    ),
    ("advanced/response-change-status-code.md", "use-case"): _workflow(
        "Use case { #use-case }",
        7,
        16,
        _STATUS_CHANGE,
        ["fastapi.response.change-status-code.tutorial-existing-and-created"],
        _STATUS_AND_BODY,
        (
            "The two selected requests follow the tutorial's existing-record and create-new "
            "branches: the first returns the default 200 and the second sets 201. They sample "
            "one in-memory route and returned strings, not dependency ordering or all status "
            "values."
        ),
        (
            "FastAPI applies the endpoint's temporary Response status to the response built "
            "from the returned object; Starlette owns the final response wire representation."
        ),
        ["update-existing-record", "create-new-record"],
    ),
    ("advanced/additional-status-codes.md", "additional-status-codes"): _excluded(
        "Additional Status Codes { #additional-status-codes }",
        1,
        41,
        (
            "The introduction is a page-level summary. Its default status behavior is "
            "covered by the tutorial status-code section, and the two additional-status "
            "branches are mapped below."
        ),
        (
            "Treating the overview as a separate workflow would duplicate the child route "
            "inputs and overstate their coverage of response classes and OpenAPI."
        ),
    ),
    ("advanced/additional-status-codes.md", "additional-status-codes_1"): _workflow(
        "Additional status codes { #additional-status-codes_1 }",
        7,
        36,
        _ADDITIONAL_STATUS,
        [
            "fastapi.additional-status-codes.tutorial-update-existing",
            "fastapi.additional-status-codes.tutorial-create-new",
        ],
        _STATUS_AND_BODY,
        (
            "The two existing cases observe an updated dictionary returned with status 200 "
            "and a directly returned JSONResponse with status 201. The inputs do not test "
            "other status codes, response classes, declared response models, or the OpenAPI "
            "claim in the next section."
        ),
        (
            "FastAPI supports returning either a normal endpoint value or a directly returned "
            "Response from a path operation. Starlette 1.6.0 owns JSONResponse rendering and "
            "wire behavior."
        ),
    ),
    ("advanced/additional-status-codes.md", "openapi-and-api-docs"): _excluded(
        "OpenAPI and API docs { #openapi-and-api-docs }",
        37,
        41,
        (
            "This section makes a negative OpenAPI claim about status codes chosen by a "
            "directly returned Response. The linked recipe records only HTTP status and body, "
            "so it cannot establish what is absent from the generated OpenAPI document."
        ),
        (
            "No selected action observes /openapi.json or its status-code entries. The "
            "OpenAPI behavior is therefore not claimed by this documentation mapping."
        ),
    ),
    ("tutorial/response-status-code.md", "response-status-code"): _workflow(
        "Response Status Code { #response-status-code }",
        1,
        101,
        _STATUS_TUTORIAL,
        [
            "fastapi.tutorial-response-status-code001.created-item",
            "fastapi.tutorial-response-status-code001.openapi",
        ],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected cases observe one endpoint's explicit 201 response and its OpenAPI "
            "response entry. They do not exercise every decorator or IntEnum value, and the "
            "OpenAPI case does not cover the bodyless-status note for codes such as 204."
        ),
        (
            "FastAPI uses the path-operation status_code for the runtime response and the "
            "generated OpenAPI response entry. Starlette owns the emitted HTTP response."
        ),
    ),
    ("tutorial/response-status-code.md", "about-http-status-codes"): _excluded(
        "About HTTP status codes { #about-http-status-codes }",
        42,
        72,
        (
            "This section explains general HTTP status-code ranges and examples, then links "
            "to MDN. Those protocol definitions do not specify an independent FastAPI route "
            "or OpenAPI behavior."
        ),
        (
            "The selected FastAPI cases cover only status values used by the documented "
            "routes. The range descriptions are general HTTP semantics."
        ),
    ),
    ("tutorial/response-status-code.md", "shortcut-to-remember-the-names"): _workflow(
        "Shortcut to remember the names { #shortcut-to-remember-the-names }",
        73,
        98,
        _RESPONSE_SURFACE,
        ["fastapi.docs.reference-wave.status-code-from-constant"],
        [
            "asgi.send.message_types",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        (
            "The selected route uses one fastapi.status constant to set its status and "
            "observes the HTTP response. It does not compare fastapi.status with "
            "starlette.status, check object identity, or exercise every constant listed by "
            "the imported enum-like namespace."
        ),
        (
            "FastAPI accepts a Starlette status constant as the path-operation status_code; "
            "this request samples one such route value. The constant namespace itself is a "
            "Starlette re-export."
        ),
        ["dispatch"],
    ),
    ("tutorial/response-status-code.md", "changing-the-default"): _workflow(
        "Changing the default { #changing-the-default }",
        99,
        101,
        _STATUS_CHANGE,
        ["fastapi.response.change-status-code.tutorial-existing-and-created"],
        _STATUS_AND_BODY,
        (
            "The linked advanced tutorial's two requests observe the configured 200 default "
            "and an endpoint-set 201 status. Dependency-provided status and endpoint "
            "overwrite behavior are covered by a separate advanced-section mapping."
        ),
        (
            "FastAPI applies the temporary Response status when constructing the response "
            "from the path operation's returned value. Starlette owns HTTP response emission."
        ),
        ["update-existing-record", "create-new-record"],
    ),
}
