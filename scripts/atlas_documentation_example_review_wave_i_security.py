"""Reviewed partial links for security tutorial examples to input-only cases.

The mappings were checked against FastAPI 0.141.1 source. Their selected
workflows are independent ASGI inputs; each mapping documents only the listed
cases and selectors, not the complete tutorial example or its page.
"""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(recipe: str, case_ids: list[str], selectors: list[str]) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": case_ids,
        "observation_selectors": sorted(selectors),
    }


def _review(
    rationale: str,
    spans: list[dict[str, object]],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {"rationale": rationale, "supporting_sources": spans, "workflow_cases": cases}


_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_OPENAPI = [
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.security",
]

_OAUTH2_TUTORIAL_002_CASE = _case(
    "security-wave.yaml",
    ["fastapi.security-wave.oauth2-tutorial-002.test-token"],
    _HTTP,
)
_HTTP_BASIC_TUTORIAL_006_CASE = _case(
    "security-wave.yaml",
    ["fastapi.security-wave.http-basic-tutorial-006.test-security-http-basic"],
    _HTTP,
)
_HTTP_BASIC_TUTORIAL_007_CASES = _case(
    "security-wave.yaml",
    [
        "fastapi.security-wave.http-basic-tutorial-007.test-security-http-basic-invalid-password",
        "fastapi.security-wave.http-basic-tutorial-007.valid-credentials",
    ],
    _HTTP,
)
_OAUTH2_TUTORIAL_004_CASES = _case(
    "security-tutorial004-auth-input-gap-wave.yaml",
    [
        "fastapi.security-tutorial004.test-no-token",
        "fastapi.security-tutorial004.test-token",
        "fastapi.security-tutorial004.test-read-items",
        "fastapi.security-tutorial004.test-openapi-schema",
    ],
    _HTTP_OPENAPI,
)
_OAUTH2_TUTORIAL_005_CASES = _case(
    "security-tutorial005-auth-scopes-gap-wave.yaml",
    [
        "fastapi.security-tutorial005.test-no-token",
        "fastapi.security-tutorial005.test-token-no-scope",
        "fastapi.security-tutorial005.test-read-items",
        "fastapi.security-tutorial005.test-openapi-schema",
    ],
    _HTTP_OPENAPI,
)


DOC_EXAMPLE_CITATION_WAVE_I = {
    "docs_src/security/tutorial002_py310.py": _review(
        (
            "The example extracts a Bearer token with OAuth2PasswordBearer and passes it "
            "through a dependency to a protected route. The independent case sends a "
            "different token to a separately named route and observes the HTTP response. "
            "It samples Bearer extraction and dependency injection only; the fake decoder, "
            "User model serialization, and tutorial route literals are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial002_py310.py",
                7,
                7,
                "required OAuth2PasswordBearer dependency configuration",
            ),
            _span(
                "docs_src/security/tutorial002_py310.py",
                23,
                30,
                "token dependency and protected route injection",
            ),
        ],
        [_OAUTH2_TUTORIAL_002_CASE],
    ),
    "docs_src/security/tutorial002_an_py310.py": _review(
        (
            "The Annotated example extracts a Bearer token with OAuth2PasswordBearer and "
            "passes it through a dependency to a protected route. The independent case sends "
            "a different token to a separately named route and observes the HTTP response. "
            "It samples Bearer extraction and dependency injection only; the fake decoder, "
            "User model serialization, and tutorial route literals are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial002_an_py310.py",
                9,
                9,
                "required OAuth2PasswordBearer dependency configuration",
            ),
            _span(
                "docs_src/security/tutorial002_an_py310.py",
                25,
                32,
                "Annotated token dependency and protected route injection",
            ),
        ],
        [_OAUTH2_TUTORIAL_002_CASE],
    ),
    "docs_src/security/tutorial004_py310.py": _review(
        (
            "The example uses OAuth2PasswordBearer in a JWT-backed current-user dependency "
            "and exposes protected user and item routes. Independent cases replace the "
            "application's password and JWT logic with synthetic inputs while sampling the "
            "required Bearer dependency, authenticated route flow, and selected OAuth2 "
            "OpenAPI paths. Password verification, hashing, JWT contents, inactive-user "
            "handling, and tutorial response literals are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial004_py310.py",
                52,
                52,
                "OAuth2PasswordBearer configuration",
            ),
            _span(
                "docs_src/security/tutorial004_py310.py",
                92,
                109,
                "required Bearer token dependency and app-owned JWT validation boundary",
            ),
            _span(
                "docs_src/security/tutorial004_py310.py",
                136,
                143,
                "protected current-user route and injected response model",
            ),
        ],
        [_OAUTH2_TUTORIAL_004_CASES],
    ),
    "docs_src/security/tutorial004_an_py310.py": _review(
        (
            "The Annotated example uses OAuth2PasswordBearer in a JWT-backed current-user "
            "dependency and exposes protected user and item routes. Independent cases "
            "replace the application's password and JWT logic with synthetic inputs while "
            "sampling the required Bearer dependency, authenticated route flow, and selected "
            "OAuth2 OpenAPI paths. Password verification, hashing, JWT contents, "
            "inactive-user handling, and tutorial response literals are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial004_an_py310.py",
                53,
                53,
                "OAuth2PasswordBearer configuration",
            ),
            _span(
                "docs_src/security/tutorial004_an_py310.py",
                93,
                110,
                "Annotated Bearer token dependency and app-owned JWT validation boundary",
            ),
            _span(
                "docs_src/security/tutorial004_an_py310.py",
                139,
                150,
                "protected current-user and item routes",
            ),
        ],
        [_OAUTH2_TUTORIAL_004_CASES],
    ),
    "docs_src/security/tutorial005_py310.py": _review(
        (
            "The example declares OAuth2 scopes, collects required scopes through "
            "SecurityScopes, and checks them in a shared current-user dependency. Independent "
            "cases use synthetic tokens to sample missing credentials, missing required "
            "scope, nested item-scope access, and selected OAuth2 OpenAPI scope/security "
            "paths. JWT and password integrations, token issuance, the no-scope status route, "
            "and tutorial response literals are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial005_py310.py",
                64,
                67,
                "OAuth2PasswordBearer scope declarations",
            ),
            _span(
                "docs_src/security/tutorial005_py310.py",
                107,
                139,
                "SecurityScopes aggregation and authorization checks after app-owned "
                "token decoding",
            ),
            _span(
                "docs_src/security/tutorial005_py310.py",
                142,
                174,
                "nested Security scopes and protected current-user/item routes",
            ),
        ],
        [_OAUTH2_TUTORIAL_005_CASES],
    ),
    "docs_src/security/tutorial005_an_py310.py": _review(
        (
            "The Annotated example declares OAuth2 scopes, collects required scopes through "
            "SecurityScopes, and checks them in a shared current-user dependency. Independent "
            "cases use synthetic tokens to sample missing credentials, missing required "
            "scope, nested item-scope access, and selected OAuth2 OpenAPI scope/security "
            "paths. JWT and password integrations, token issuance, the no-scope status route, "
            "and tutorial response literals are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial005_an_py310.py",
                65,
                68,
                "OAuth2PasswordBearer scope declarations",
            ),
            _span(
                "docs_src/security/tutorial005_an_py310.py",
                108,
                140,
                "SecurityScopes aggregation and authorization checks after app-owned "
                "token decoding",
            ),
            _span(
                "docs_src/security/tutorial005_an_py310.py",
                143,
                177,
                "nested Annotated Security scopes and protected current-user/item routes",
            ),
        ],
        [_OAUTH2_TUTORIAL_005_CASES],
    ),
    "docs_src/security/tutorial006_py310.py": _review(
        (
            "The example injects HTTPBasicCredentials through Depends and returns their "
            "fields. The independent route accepts a different valid Basic credential and "
            "observes the response, sampling Basic parsing and dependency injection only. "
            "Missing or malformed credentials, OpenAPI details, and the tutorial's credential "
            "values are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial006_py310.py",
                6,
                10,
                "HTTPBasic dependency and credentials injection",
            )
        ],
        [_HTTP_BASIC_TUTORIAL_006_CASE],
    ),
    "docs_src/security/tutorial006_an_py310.py": _review(
        (
            "The Annotated example injects HTTPBasicCredentials through Depends and returns "
            "their fields. The independent route accepts a different valid Basic credential "
            "and observes the response, sampling Basic parsing and dependency injection only. "
            "Missing or malformed credentials, OpenAPI details, and the tutorial's credential "
            "values are not claimed."
        ),
        [
            _span(
                "docs_src/security/tutorial006_an_py310.py",
                8,
                12,
                "HTTPBasic dependency and Annotated credentials injection",
            )
        ],
        [_HTTP_BASIC_TUTORIAL_006_CASE],
    ),
    "docs_src/security/tutorial007_py310.py": _review(
        (
            "The example injects HTTPBasicCredentials, compares supplied credentials, and "
            "raises an HTTPException with a Basic challenge on failure. Independent cases "
            "use another valid credential and a different invalid password, observing HTTP "
            "response status, headers, and bytes. They sample Basic injection and "
            "HTTPException response behavior only; direct string comparison in the workload "
            "does not support a claim about secrets.compare_digest or constant-time checks."
        ),
        [
            _span(
                "docs_src/security/tutorial007_py310.py",
                8,
                28,
                "HTTPBasic dependency, app-owned credential check, and Basic challenge exception",
            ),
            _span(
                "docs_src/security/tutorial007_py310.py",
                31,
                32,
                "protected route receiving the dependency result",
            ),
        ],
        [_HTTP_BASIC_TUTORIAL_007_CASES],
    ),
    "docs_src/security/tutorial007_an_py310.py": _review(
        (
            "The Annotated example injects HTTPBasicCredentials, compares supplied "
            "credentials, and raises an HTTPException with a Basic challenge on failure. "
            "Independent cases use another valid credential and a different invalid password, "
            "observing HTTP response status, headers, and bytes. They sample Basic injection "
            "and HTTPException response behavior only; direct string comparison in the "
            "workload does not support a claim about secrets.compare_digest or constant-time "
            "checks."
        ),
        [
            _span(
                "docs_src/security/tutorial007_an_py310.py",
                9,
                31,
                "HTTPBasic dependency, app-owned credential check, and Basic challenge exception",
            ),
            _span(
                "docs_src/security/tutorial007_an_py310.py",
                34,
                36,
                "protected route receiving the dependency result",
            ),
        ],
        [_HTTP_BASIC_TUTORIAL_007_CASES],
    ),
}
