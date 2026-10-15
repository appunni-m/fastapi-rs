"""Reviewed mapping for the old authentication error status how-to section.

Source identities: FastAPI 0.141.1 at
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f, Starlette 1.6.0 at
4f250d6b814587e20c5365f0a5f0c4d42bcb929f, and Starlette-RS at
b4c8a65c85e1b0d251ca05874412811eaa3ac7b8. Starlette is the oracle for generic
exception responses; Starlette-RS owns the corresponding target behavior.
"""

_RECIPE = "tests/fixtures/input-recipes/parity/authentication-error-status-code-tutorial.yaml"


DOC_SECTION_CASE_MAPPINGS_AUTHENTICATION_ERROR_STATUS_20261015 = {
    (
        "how-to/authentication-error-status-code.md",
        "use-old-403-authentication-error-status-codes",
    ): {
        "heading": (
            "Use Old 403 Authentication Error Status Codes "
            "{ #use-old-403-authentication-error-status-codes }"
        ),
        "start_line": 1,
        "end_line": 17,
        "recipe_path": _RECIPE,
        "case_ids": ["fastapi.docs.auth-error-status.legacy-forbidden"],
        "action_ids": ["missing-bearer"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "Partial mapping: the selected missing-bearer request exercises a custom "
            "HTTPBearer.make_not_authenticated_error override that returns a 403 "
            "HTTPException. The fixture uses its own detail text, so it does not claim the "
            "published example's exact body bytes. It does not establish the built-in 401 "
            "response or WWW-Authenticate header, invalid credentials, optional authentication, "
            "or other security utilities."
        ),
        "rationale": (
            "The pinned FastAPI 0.141.1 page is "
            "docs/en/docs/how-to/authentication-error-status-code.md#L1-L17: it describes the "
            "403 override and says the method returns an exception for the dependency to raise. "
            "Its linked example is docs_src/authentication_error_status_code/"
            "tutorial001_an_py310.py#L9-L21. FastAPI 0.141.1 at "
            "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f defines the hook at "
            "fastapi/security/http.py#L87-L92 and invokes it for missing bearer credentials "
            "in HTTPBearer.__call__ at fastapi/security/http.py#L303-L316. Starlette 1.6.0 at "
            "4f250d6b814587e20c5365f0a5f0c4d42bcb929f dispatches HTTPException responses in "
            "starlette/middleware/exceptions.py#L65-L69; this mapping claims only the selected "
            "public response from the documented override path."
        ),
    },
}
