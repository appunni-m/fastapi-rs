"""Reviewed section mapping for FastAPI's direct Request access tutorial."""


DOC_SECTION_CASE_MAPPINGS_REQUEST_OBJECT_DIRECTLY_20261015 = {
    (
        "advanced/using-request-directly.md",
        "use-the-request-object-directly",
    ): {
        "heading": "Use the `Request` object directly { #use-the-request-object-directly }",
        "start_line": 26,
        "end_line": 45,
        "recipe_path": "tests/fixtures/input-recipes/parity/using_request_directly.yaml",
        "case_ids": ["fastapi.docs.using-request-directly.client-host"],
        "action_ids": ["read-client-host", "request-openapi"],
        "observation_selectors": [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "scope_note": (
            "The HTTP action supplies client=(127.0.0.1, 123) to GET /items/chair and the "
            "independent endpoint returns request.client.host with the successful string path "
            "value. The OpenAPI action selects the path operation's parameter projection. This "
            "covers one present client and one successful string path value; it does not sample "
            "a missing client, invalid path input or validation errors, direct body reads, other "
            "Request properties, or FastAPI/Starlette Request identity."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/using-request-directly.md:26-44 "
            "describes reading the client host through a Request-typed path-operation parameter "
            "and retaining a separately declared path parameter; its included "
            "docs_src/using_request_directly/tutorial001_py310.py:1,6-9 shows that route. The "
            "independently authored workload accepts Request and returns its client host and "
            "item_id; its recipe sends the explicit ASGI client tuple and selects HTTP status, "
            "headers, and body bytes, then selects the /items/{item_id} GET parameter projection "
            "from OpenAPI. FastAPI 0.141.1 fastapi/dependencies/utils.py:350-355 classifies a "
            "Request-typed endpoint parameter, :711-712 places the current Request in dependency "
            "values, and fastapi/routing.py:706-710 invokes the endpoint with those values. "
            "Starlette 1.6.0 starlette/requests.py:161-167 derives Request.client from the ASGI "
            "scope client tuple. The selected OpenAPI projection establishes the documented "
            "string path parameter shape only; this successful request does not establish "
            "invalid-input validation behavior."
        ),
    }
}
