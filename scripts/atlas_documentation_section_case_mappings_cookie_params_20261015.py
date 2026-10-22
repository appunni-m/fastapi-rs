"""Reviewed mapping for the annotated Cookie parameter tutorial section."""

DOC_SECTION_CASE_MAPPINGS_COOKIE_PARAMS_20261015 = {
    ("tutorial/cookie-params.md", "declare-cookie-parameters"): {
        "heading": "Declare `Cookie` parameters { #declare-cookie-parameters }",
        "start_line": 11,
        "end_line": 42,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/atlas-pending-tutorials-source-wave.yaml"
        ),
        "case_ids": ["fastapi.pending.tutorials-source-wave.cookie-parameter-cases"],
        "action_ids": ["cookie-annotated-absent", "cookie-annotated-present"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "The selected actions sample only the annotated optional scalar declaration: "
            "cookie-annotated-absent omits the Cookie header, while "
            "cookie-annotated-present sends ads_id=ad-value in that header. Both select "
            "response status and body bytes. They cover the declared None default and one "
            "present cookie value. They do not exercise required cookies, aliases, extra "
            "validation or annotation attributes, OpenAPI output, import/signature identity, "
            "the unannotated form, extra-cookie behavior, or the browser docs UI note."
        ),
        "rationale": (
            "Pinned FastAPI 0.157.0 docs/en/docs/tutorial/cookie-params.md:11-17 explains "
            "declaring Cookie parameters and highlights the annotated example at "
            "docs_src/cookie_params/tutorial001_an_py310.py:8-10; lines 27-31 state that "
            "Cookie is needed to declare a cookie instead of an inferred query parameter. "
            "The existing independently authored workload mirrors that example's optional "
            "annotated declaration ("
            "tests/fixtures/workloads/atlas_pending_tutorials_wave.py:70-73). "
            "Its input-only recipe case "
            "fastapi.pending.tutorials-source-wave.cookie-parameter-cases selects only "
            "cookie-annotated-absent and cookie-annotated-present, each observing exact "
            "HTTP status and body. FastAPI 0.157.0 marks Cookie as ParamTypes.cookie "
            "(fastapi/params.py:410-411), assigns cookie fields to the cookie collection "
            "(fastapi/dependencies/utils.py:621-634), and resolves them from request.cookies "
            "(fastapi/dependencies/utils.py:777-778); its absent-value path uses the field "
            "default during extraction and validation (fastapi/dependencies/utils.py:843-864,"
            "952-989). Starlette 1.6.0 "
            "owns parsing the Cookie header into Request.cookies "
            "(starlette/requests.py:150-159)."
        ),
    }
}
