"""Reviewed response-cookie and status-code documentation mappings."""


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


_COOKIE_PARAMETER = "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml"
_COOKIE_DIRECT = "tests/fixtures/input-recipes/parity/response-cookie-direct-wave.yaml"
_STATUS_CHANGE = "tests/fixtures/input-recipes/parity/response-change-status-tutorial-review.yaml"
_STATUS_POLICY = "tests/fixtures/input-recipes/parity/response-policy-matrix.yaml"
_ADDITIONAL_STATUS = "tests/fixtures/input-recipes/parity/additional-status-codes-tutorial-upstream.yaml"
_STATUS_TUTORIAL = "tests/fixtures/input-recipes/parity/tutorial-response-status-code001-source-review.yaml"
_RESPONSE_SURFACE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_HTTP_RESPONSE = ["http.status", "http.headers.ordered", "http.body.bytes"]
_STATUS_AND_BODY = ["http.status", "http.body.bytes"]


DOC_SECTION_CASE_MAPPINGS_RESPONSE_STATUS_REVIEW_20261016 = {
    ("advanced/response-cookies.md", "response-cookies"): _excluded(
        "Response Cookies { #response-cookies }",
        1,
        51,
        (
            "The page overview describes its temporary-Response and directly returned-Response "
            "paths. Those independent paths are mapped under their child headings; the "
            "nested cookie API details belong to Starlette 1.6.0."
        ),
        (
            "FastAPI 0.141.1 identifies and injects a temporary Response in "
            "fastapi/dependencies/utils.py:350-364,611-614,719-720, and transfers its headers "
            "in fastapi/routing.py:716-750. The child rows map those route workflows; the "
            "overview adds no separate operation."
        ),
    ),
    ("advanced/response-cookies.md", "use-a-response-parameter"): _workflow(
        "Use a `Response` parameter { #use-a-response-parameter }",
        3,
        18,
        _COOKIE_PARAMETER,
        ["fastapi.test.test-tutorial-test-response-cookies-test-tutorial002.test-path-operation"],
        ["response-cookie"],
        _HTTP_RESPONSE,
        (
            "The selected request sets one cookie through the endpoint's injected temporary "
            "Response and returns a dictionary. It observes status, ordered raw headers, and "
            "body bytes. It does not exercise dependency-set cookies, response-model filtering, "
            "or TestClient cookie-jar persistence and reuse."
        ),
        (
            "FastAPI 0.141.1 recognizes Response as a special dependency parameter "
            "(fastapi/dependencies/utils.py:350-364), creates and injects the temporary value "
            "(fastapi/dependencies/utils.py:611-614,719-720), then copies its raw headers to "
            "the serialized response (fastapi/routing.py:716-750). Starlette 1.6.0 owns cookie "
            "formatting and HTTP header emission."
        ),
    ),
    ("advanced/response-cookies.md", "return-a-response-directly"): _workflow(
        "Return a `Response` directly { #return-a-response-directly }",
        19,
        51,
        _COOKIE_DIRECT,
        ["fastapi.response.cookies.direct-jsonresponse-set-cookie"],
        ["create-cookie-response"],
        _HTTP_RESPONSE,
        (
            "The selected request constructs a JSONResponse, calls set_cookie, and returns it. "
            "It observes status, ordered raw headers, and body bytes. It does not exercise "
            "response-model bypass, cookie-jar behavior, or every Response subclass."
        ),
        (
            "FastAPI 0.141.1 returns an endpoint-provided Response through its direct-response "
            "branch (fastapi/routing.py:706-715). Starlette 1.6.0 owns JSONResponse rendering, "
            "set_cookie formatting, and ASGI response emission."
        ),
    ),
    ("advanced/response-cookies.md", "more-info"): _excluded(
        "More info { #more-info }",
        39,
        51,
        (
            "This subsection documents convenience import paths and links to Starlette's "
            "set_cookie reference. The selected route cases do not compare import paths or "
            "object identity, and cookie formatting/options are Starlette 1.6.0 behavior."
        ),
        (
            "FastAPI 0.141.1 re-exports Starlette response classes from fastapi/responses.py:6-12 "
            "and the root Response from fastapi/__init__.py:22. Those public identities belong "
            "to the API manifest; the linked Starlette page owns the generic cookie contract."
        ),
    ),
    ("advanced/response-change-status-code.md", "response-change-status-code"): _excluded(
        "Response - Change Status Code { #response-change-status-code }",
        1,
        31,
        (
            "The title and introduction summarize the default-status and temporary-Response "
            "workflows mapped under the child headings."
        ),
        (
            "FastAPI 0.141.1 applies a changed temporary Response status while building the "
            "ordinary response (fastapi/routing.py:357-372); the child use-case and parameter "
            "rows map the distinct sampled behavior, so this overview adds no operation."
        ),
    ),
    ("advanced/response-change-status-code.md", "use-case"): _workflow(
        "Use case { #use-case }",
        7,
        16,
        _STATUS_CHANGE,
        ["fastapi.response.change-status-code.tutorial-existing-and-created"],
        ["update-existing-record", "create-new-record"],
        _STATUS_AND_BODY,
        (
            "The two selected requests follow the tutorial's existing-record and create-new "
            "branches: the first returns 200 and the second sets 201. They sample one "
            "in-memory route and returned strings, not dependency ordering, response-model "
            "filtering, or all status values."
        ),
        (
            "FastAPI 0.141.1 creates the shared temporary Response during dependency solving "
            "(fastapi/dependencies/utils.py:611-614) and applies its status to the response "
            "built from a returned value (fastapi/routing.py:357-372,716-750). Starlette 1.6.0 "
            "owns final response emission."
        ),
    ),
    ("advanced/response-change-status-code.md", "use-a-response-parameter"): _workflow(
        "Use a `Response` parameter { #use-a-response-parameter }",
        17,
        31,
        _STATUS_POLICY,
        ["fastapi.response.dependency-status", "fastapi.response.status-overwrite"],
        None,
        _HTTP_RESPONSE,
        (
            "The first input samples a dependency setting the injected temporary Response "
            "status to 201; the second samples an endpoint setting status 400 over its "
            "declared 204. Both select exact status, ordered headers, and body bytes. They do "
            "not exercise temporary-response headers or cookies, response-model filtering, or "
            "multiple status-setting dependencies."
        ),
        (
            "FastAPI 0.141.1 classifies Response parameters in "
            "fastapi/dependencies/utils.py:350-364, creates and injects the shared temporary "
            "Response in fastapi/dependencies/utils.py:611-614,719-729, and applies its final "
            "status in fastapi/routing.py:357-372. Starlette 1.6.0 owns generic response "
            "construction and ASGI emission."
        ),
    ),
    ("advanced/additional-status-codes.md", "additional-status-codes"): _excluded(
        "Additional Status Codes { #additional-status-codes }",
        1,
        41,
        (
            "The introduction is a page-level summary. The default status behavior is mapped "
            "under the tutorial status-code page, and the two additional-status branches plus "
            "the OpenAPI statement are mapped under their child headings."
        ),
        (
            "FastAPI 0.141.1 applies declared or temporary Response status while constructing "
            "ordinary return values (fastapi/routing.py:357-372,716-750). The child workflows "
            "map those independent behaviors without treating the page overview as another "
            "operation."
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
        None,
        _STATUS_AND_BODY,
        (
            "The two selected requests observe an updated dictionary returned with status 200 "
            "and a directly returned JSONResponse with status 201. They do not test other "
            "status codes, response classes, response-model bypass, or the OpenAPI statement "
            "in the next section."
        ),
        (
            "FastAPI 0.141.1 serializes ordinary endpoint values and returns a directly "
            "returned Response through separate branches (fastapi/routing.py:706-750). "
            "Starlette 1.6.0 owns JSONResponse rendering and wire behavior."
        ),
    ),
    ("advanced/additional-status-codes.md", "openapi-and-api-docs"): _excluded(
        "OpenAPI and API docs { #openapi-and-api-docs }",
        37,
        41,
        (
            "This section claims that a status chosen inside a directly returned Response is "
            "not inferred into OpenAPI. The linked recipe cases observe HTTP status and body "
            "only, so they cannot establish absence from the generated schema."
        ),
        (
            "FastAPI 0.141.1 generates OpenAPI responses from route.status_code and declared "
            "route.responses metadata (fastapi/openapi/utils.py:403-419,473-490); runtime "
            "endpoint Responses are returned directly (fastapi/routing.py:706-715). No "
            "selected action queries /openapi.json, so this negative OpenAPI claim remains "
            "outside the mapping."
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
        None,
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "Each linked case has one action. The selected cases observe one endpoint's "
            "explicit 201 response and its OpenAPI response entry. They do not exercise every "
            "decorator or IntEnum value, or the "
            "bodyless-status/OpenAPI note for codes such as 204. The separate existing 204 "
            "OpenAPI case lacks this tutorial page as upstream_documentation source evidence "
            "and is not projected here."
        ),
        (
            "FastAPI 0.141.1 normalizes IntEnum route status values "
            "(fastapi/routing.py:1029-1032), uses the route or temporary Response status for "
            "runtime responses (fastapi/routing.py:357-372), and builds OpenAPI response "
            "entries from route metadata (fastapi/openapi/utils.py:403-419). Starlette 1.6.0 "
            "owns emitted HTTP response behavior."
        ),
    ),
    ("tutorial/response-status-code.md", "about-http-status-codes"): _excluded(
        "About HTTP status codes { #about-http-status-codes }",
        42,
        72,
        (
            "This section describes HTTP status-code ranges and general examples, then links "
            "to MDN. Those protocol definitions do not specify a FastAPI route or OpenAPI "
            "behavior."
        ),
        (
            "The selected FastAPI cases cover only status values used by the route examples. "
            "The ranges and HTTP meanings in docs/en/docs/tutorial/response-status-code.md:50-71 "
            "are general protocol guidance."
        ),
    ),
    ("tutorial/response-status-code.md", "shortcut-to-remember-the-names"): _workflow(
        "Shortcut to remember the names { #shortcut-to-remember-the-names }",
        73,
        98,
        _RESPONSE_SURFACE,
        ["fastapi.docs.reference-wave.status-code-from-constant"],
        ["dispatch"],
        ["asgi.send.message_types", "http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected route uses one fastapi.status constant and observes the HTTP "
            "response. It does not compare fastapi.status with starlette.status, check object "
            "identity, or exercise every constant in the re-exported namespace."
        ),
        (
            "FastAPI 0.141.1 re-exports starlette.status as fastapi.status "
            "(fastapi/__init__.py:5); APIRoute normalizes IntEnum status values "
            "(fastapi/routing.py:1029-1032). The namespace itself is a Starlette re-export."
        ),
    ),
    ("tutorial/response-status-code.md", "changing-the-default"): _workflow(
        "Changing the default { #changing-the-default }",
        99,
        101,
        _STATUS_CHANGE,
        ["fastapi.response.change-status-code.tutorial-existing-and-created"],
        ["update-existing-record", "create-new-record"],
        _STATUS_AND_BODY,
        (
            "The linked advanced tutorial's two requests observe the configured 200 default "
            "and an endpoint-set 201 status. Dependency-provided status and endpoint overwrite "
            "behavior are covered by the separate advanced-section mapping."
        ),
        (
            "FastAPI 0.141.1 applies the temporary Response status when building a response "
            "from the returned value (fastapi/routing.py:357-372,716-750). Starlette 1.6.0 "
            "owns HTTP response emission."
        ),
    ),
}
