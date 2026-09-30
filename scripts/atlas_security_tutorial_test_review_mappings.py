"""Source-reviewed case links for FastAPI's security tutorial tests.

This atlas sidecar links the seven pinned tutorial test modules to existing,
independently authored inputs. The links are review evidence only: they do not
assert parity, and the selected observations do not reproduce the tutorials'
complete TestClient assertions or OpenAPI snapshots.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from atlas_security_test_exclusions import (
    TEST_FUNCTION_EXCLUSION_EVIDENCE as _SYNTHETIC_AUTH_EXCLUSION_EVIDENCE,
)
from atlas_security_test_exclusions import (
    TEST_FUNCTION_EXCLUSIONS as _SYNTHETIC_AUTH_EXCLUSIONS,
)

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT.parent / "fastapi"

SOURCE_IDENTITY = {
    "fastapi_version": "0.141.1",
    "fastapi_commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "starlette_version": "1.6.0",
    "starlette_commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}

_TEST_ROOT = "tests/test_tutorial/test_security/"
_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_OPENAPI_ATLAS = ["docs.response.status", "http.status", "openapi.security"]
_OPENAPI_BASIC = [
    "docs.response.headers",
    "docs.response.status",
    "http.headers.ordered",
    "http.status",
    "openapi.security",
]
_OPENAPI_TUTORIAL004 = ["openapi.document", "openapi.paths", "openapi.security"]
_OPENAPI_TUTORIAL005 = ["openapi.document", "openapi.paths", "openapi.security"]

_SECURITY_DEPENDENCIES = "tests/fixtures/input-recipes/parity/security-dependencies.yaml"
_SECURITY_WAVE = "tests/fixtures/input-recipes/parity/security-wave.yaml"
_SECURITY_ATLAS = "tests/fixtures/input-recipes/parity/security-atlas-wave.yaml"
_TUTORIAL004 = "tests/fixtures/input-recipes/parity/security-tutorial004-auth-input-gap-wave.yaml"
_TUTORIAL005 = "tests/fixtures/input-recipes/parity/security-tutorial005-auth-scopes-gap-wave.yaml"
_HTTP_BASIC_RECIPE = "tests/fixtures/input-recipes/parity/http-basic.yaml"
_OAUTH2_INACTIVE_USER_RECIPE = (
    "tests/fixtures/input-recipes/parity/security-oauth2-inactive-user-source-wave.yaml"
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    return _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test stimulus and assertions for {function_name}",
    )


def _docs(tutorial: str, start: int, end: int, role: str) -> dict[str, Any]:
    return _source(f"docs_src/security/{tutorial}_py310.py", start, end, role)


def _case(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str] = _HTTP,
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _http_case(recipe_path: str, case_id: str, action_id: str) -> dict[str, Any]:
    return _case(recipe_path, case_id, [action_id])


def _review(
    test_file: str,
    function_name: str,
    feature_ids: list[str],
    rationale: str,
    gate: str,
    cases: list[dict[str, Any]],
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    case_notes = "; ".join(
        f"{case['recipe_path']}::{case['case_id']} actions {', '.join(case['action_ids'])}"
        for case in cases
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": sorted(
            {selector for case in cases for selector in case["observation_selectors"]}
        ),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "workflow_cases": cases,
        "stimulus_notes": (
            f"Existing independent input-only case(s): {case_notes}. "
            "The workflows contain no expected outputs."
        ),
        "supporting_sources": [
            _test_span(_TEST_ROOT + test_file, function_name),
            *sources,
        ],
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    cases: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for review in functions.values():
        for case in review["workflow_cases"]:
            key = (
                case["recipe_path"],
                case["case_id"],
                tuple(case["action_ids"]),
            )
            cases.setdefault(key, case)
        for source in review["supporting_sources"]:
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources.setdefault(key, source)
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
        "functions": functions,
        "workflow_cases": list(cases.values()),
        "supporting_sources": list(sources.values()),
        "module_observation_selectors": sorted(
            {
                selector
                for review in functions.values()
                for selector in review["observation_selectors"]
            }
        ),
    }


_OAUTH2_REQUIRED = _source(
    "fastapi/security/oauth2.py",
    401,
    430,
    "OAuth2 raises the default unauthenticated error when a required authorization value is absent",
)
_OAUTH2_BEARER = _source(
    "fastapi/security/oauth2.py",
    433,
    544,
    "OAuth2PasswordBearer builds password-flow metadata and extracts only Bearer credentials",
)
_OAUTH2_FORM = _source(
    "fastapi/security/oauth2.py",
    14,
    159,
    "OAuth2PasswordRequestForm declares and collects form-encoded OAuth2 fields",
)
_FORM_REQUEST = _source(
    "fastapi/routing.py",
    425,
    432,
    "FastAPI reads form data for a route with form body fields",
)
_FORM_FIELDS = _source(
    "fastapi/dependencies/utils.py",
    951,
    998,
    "FastAPI extracts and validates the declared form fields before dependency invocation",
)
_DEPENDENCY_SOLVER = _source(
    "fastapi/dependencies/utils.py",
    619,
    730,
    "FastAPI recursively resolves security dependencies and injects endpoint values",
)
_HTTP_BASIC = _source(
    "fastapi/security/http.py",
    69,
    102,
    "HTTPBase reads authorization credentials and applies auto_error",
)
_HTTP_BASIC_PARSER = _source(
    "fastapi/security/http.py",
    105,
    219,
    "HTTPBasic validates the scheme, decodes Base64, splits username/password, and creates credentials",
)
_AUTHORIZATION_SPLIT = _source(
    "fastapi/security/utils.py",
    1,
    7,
    "FastAPI splits the authorization scheme and strips surrounding credential whitespace",
)
_HTTP_EXCEPTION_HANDLER = _source(
    "fastapi/exception_handlers.py",
    11,
    17,
    "FastAPI renders HTTPException status, detail, and headers as a response",
)
_OPENAPI_SECURITY_SCHEME = _source(
    "fastapi/openapi/utils.py",
    99,
    156,
    "FastAPI discovers security dependencies and encodes scheme definitions and operation scopes",
)
_OPENAPI_SECURITY_OPERATION = _source(
    "fastapi/openapi/utils.py",
    331,
    356,
    "FastAPI adds dependency-derived security definitions and requirements to OpenAPI operations",
)
_OPENAPI_FORM_BODY = _source(
    "fastapi/openapi/utils.py",
    231,
    263,
    "FastAPI builds OpenAPI requestBody content and requiredness from the route body field",
)


def _fn(
    test_file: str,
    name: str,
    rationale: str,
    gate: str,
    cases: list[dict[str, Any]],
    sources: tuple[dict[str, Any], ...],
    features: list[str] | None = None,
) -> dict[str, Any]:
    return _review(
        test_file,
        name,
        features or ["dependency-security"],
        rationale,
        gate,
        cases,
        sources,
    )


SECURITY_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    _TEST_ROOT + "test_tutorial001.py": _module(
        "Tutorial 001 tests required OAuth2PasswordBearer extraction, token injection, and a complete OpenAPI snapshot. Existing cases independently sample required bearer behavior and security projection.",
        {
            "test_no_token": _fn(
                "test_tutorial001.py",
                "test_no_token",
                "The source checks required bearer authentication, the default 401 JSON detail, and a Bearer challenge.",
                "The independent route differs from /items/. It selects raw body bytes and the complete ordered header list, which is broader than the source's named challenge lookup; TestClient JSON decoding is outside this selector set.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-missing",
                        "required-bearer-missing",
                    )
                ],
                (
                    _docs(
                        "tutorial001",
                        6,
                        11,
                        "required OAuth2PasswordBearer dependency and token-returning route",
                    ),
                    _OAUTH2_REQUIRED,
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_token": _fn(
                "test_tutorial001.py",
                "test_token",
                "A supplied bearer value is extracted by OAuth2PasswordBearer and injected into the endpoint.",
                "The independent /security/tutorial-token route uses a different token and path. It samples token extraction and dependency injection, not the source path or exact response value.",
                [
                    _http_case(
                        _SECURITY_WAVE,
                        "fastapi.security-wave.oauth2-tutorial-002.test-token",
                        "dispatch",
                    )
                ],
                (
                    _docs(
                        "tutorial001", 6, 11, "required bearer dependency and endpoint token return"
                    ),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
            ),
            "test_incorrect_token": _fn(
                "test_tutorial001.py",
                "test_incorrect_token",
                "A non-Bearer authorization scheme is rejected by OAuth2PasswordBearer before the endpoint runs.",
                "The independent case uses a different wrong scheme and route. It selects raw response bytes and all ordered headers; the source's decoded JSON assertion and named WWW-Authenticate assertion are not separately projected.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-wrong-scheme",
                        "required-bearer-wrong-scheme",
                    )
                ],
                (
                    _docs("tutorial001", 6, 11, "required bearer dependency on the route"),
                    _OAUTH2_BEARER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial001.py",
                "test_openapi_schema",
                "The source compares a full OpenAPI document containing an OAuth2 password-flow scheme and operation security.",
                "The independent case selects only the OAuth2PasswordBearer component and one operation security pointer for a separately named route. The complete snapshot, path spelling, generated operation metadata, and unrelated schema fields remain gated.",
                [
                    _case(
                        _SECURITY_ATLAS,
                        "fastapi.security-atlas-wave.oauth2-password-bearer-optional.default-name-openapi",
                        ["inspect-password-bearer-security-scheme"],
                        _OPENAPI_ATLAS,
                    )
                ],
                (
                    _docs(
                        "tutorial001",
                        6,
                        11,
                        "OAuth2PasswordBearer token URL and documented path operation",
                    ),
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial002.py": _module(
        "Tutorial 002 tests required bearer extraction, fake token decoding in the app, and an OpenAPI snapshot. The linked request cases cover the FastAPI-owned security boundary while preserving the app-owned decode gate.",
        {
            "test_no_token": _fn(
                "test_tutorial002.py",
                "test_no_token",
                "A missing bearer value is rejected before the fake decoder and user endpoint run.",
                "The independent route differs from /users/me. It selects raw body bytes and the ordered header list; source JSON decoding and the named challenge assertion are not separate selectors.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-missing",
                        "required-bearer-missing",
                    )
                ],
                (
                    _docs("tutorial002", 7, 8, "required OAuth2PasswordBearer dependency"),
                    _docs(
                        "tutorial002", 23, 30, "fake decoder dependency and protected user route"
                    ),
                    _OAUTH2_REQUIRED,
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_token": _fn(
                "test_tutorial002.py",
                "test_token",
                "The source first extracts a bearer value, then applies tutorial-owned fake decoding and constructs a Pydantic User.",
                "The independent route echoes a different token instead of running fake_decode_token. This mapping covers bearer extraction and dependency injection only; fake decoding and source User serialization remain gated.",
                [
                    _http_case(
                        _SECURITY_WAVE,
                        "fastapi.security-wave.oauth2-tutorial-002.test-token",
                        "dispatch",
                    )
                ],
                (
                    _docs("tutorial002", 7, 8, "required OAuth2PasswordBearer dependency"),
                    _docs("tutorial002", 17, 30, "app-owned fake decoder and protected endpoint"),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_openapi_schema": _fn(
                "test_tutorial002.py",
                "test_openapi_schema",
                "The source compares the OAuth2 password-flow scheme and operation security in a complete OpenAPI snapshot.",
                "The independent case checks only the scheme and one operation security pointer on another path; full OpenAPI equality and generated route metadata remain gated.",
                [
                    _case(
                        _SECURITY_ATLAS,
                        "fastapi.security-atlas-wave.oauth2-password-bearer-optional.default-name-openapi",
                        ["inspect-password-bearer-security-scheme"],
                        _OPENAPI_ATLAS,
                    )
                ],
                (
                    _docs("tutorial002", 7, 8, "OAuth2PasswordBearer configuration"),
                    _docs(
                        "tutorial002",
                        10,
                        30,
                        "Pydantic User and protected path operation included in OpenAPI",
                    ),
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial003.py": _module(
        "Tutorial 003 combines OAuth2 form parsing and bearer dependencies with a tutorial-owned in-memory user database and fake password/token functions. FastAPI-owned form, bearer, dependency, and OpenAPI paths are mapped; the inactive-user input observes dependency dispatch while keeping its authorization policy app-owned.",
        {
            "test_login": _fn(
                "test_tutorial003.py",
                "test_login",
                "The successful login request submits username and password as OAuth2 form data to a FastAPI route with OAuth2PasswordRequestForm.",
                "The independent synthetic login uses different route data and a non-cryptographic token. It samples form parsing, dependency resolution, and route response emission; the tutorial's fake password check and exact token response are not claimed.",
                [
                    _case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-token",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs(
                        "tutorial003",
                        73,
                        84,
                        "OAuth2PasswordRequestForm login route and fake password check",
                    ),
                    _OAUTH2_FORM,
                    _FORM_REQUEST,
                    _FORM_FIELDS,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "request-validation", "response-serialization"],
            ),
            "test_no_token": _fn(
                "test_tutorial003.py",
                "test_no_token",
                "A missing bearer value is rejected before the app's fake token lookup and active-user dependency run.",
                "The independent required-bearer case uses another path. It selects raw response bytes and all ordered headers; the TestClient JSON object and named challenge lookup are not separately represented.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-missing",
                        "required-bearer-missing",
                    )
                ],
                (
                    _docs("tutorial003", 29, 30, "required OAuth2PasswordBearer dependency"),
                    _docs(
                        "tutorial003", 56, 64, "bearer dependency and app-owned fake token lookup"
                    ),
                    _OAUTH2_REQUIRED,
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_token": _fn(
                "test_tutorial003.py",
                "test_token",
                "FastAPI extracts a supplied bearer string and injects it into the app-owned fake decoder dependency.",
                "The independent endpoint echoes a different token rather than looking up a user. It samples only bearer extraction and dependency injection, not fake user lookup or Pydantic user serialization.",
                [
                    _http_case(
                        _SECURITY_WAVE,
                        "fastapi.security-wave.oauth2-tutorial-002.test-token",
                        "dispatch",
                    )
                ],
                (
                    _docs("tutorial003", 29, 30, "OAuth2PasswordBearer dependency"),
                    _docs(
                        "tutorial003",
                        49,
                        64,
                        "tutorial-owned fake decode and current-user dependency",
                    ),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_inactive_user": _fn(
                "test_tutorial003.py",
                "test_inactive_user",
                "The source supplies a valid bearer token for an inactive user, exercising bearer extraction and nested current-user dependencies before application authorization returns an error.",
                "The independent case sends a different authenticated inactive-user token through the same dependency shape and observes the HTTP response. FastAPI bearer parsing and dependency dispatch are the mapped behavior; the inactive flag policy and its error text are application-owned.",
                [
                    _http_case(
                        _OAUTH2_INACTIVE_USER_RECIPE,
                        "fastapi.security.tutorial-003.oauth2-inactive-user",
                        "authenticated-inactive-user",
                    )
                ],
                (
                    _docs(
                        "tutorial003",
                        56,
                        70,
                        "bearer extraction, current-user lookup, and nested active-user dependency",
                    ),
                    _source(
                        "docs/en/docs/tutorial/security/simple-oauth2.md",
                        187,
                        197,
                        "OAuth2 bearer token and current-user dependency tutorial",
                    ),
                    _source(
                        "docs/en/docs/tutorial/security/simple-oauth2.md",
                        263,
                        279,
                        "inactive-user HTTPException behavior is application-owned",
                    ),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
                ["dependency-security", "public-api-errors"],
            ),
            "test_incorrect_token_type": _fn(
                "test_tutorial003.py",
                "test_incorrect_token_type",
                "A non-Bearer authorization scheme is rejected by FastAPI before fake token lookup.",
                "The independent case uses a different wrong scheme and route. It selects raw body bytes and the full ordered header list, not TestClient's parsed JSON result or just the challenge header.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-wrong-scheme",
                        "required-bearer-wrong-scheme",
                    )
                ],
                (
                    _docs("tutorial003", 29, 30, "OAuth2PasswordBearer dependency"),
                    _docs(
                        "tutorial003",
                        56,
                        64,
                        "app-owned current-user branch behind the bearer dependency",
                    ),
                    _OAUTH2_BEARER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial003.py",
                "test_openapi_schema",
                "The source snapshot includes a password-form request body, OAuth2 scheme, and operation security for two routes.",
                "The tutorial 004 input selects requestBody and security pointers for independently exercised paths. It does not compare the full source snapshot, generated names, route spelling, or every validation schema field.",
                [
                    _case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-openapi-schema",
                        ["inspect-openapi"],
                        _OPENAPI_TUTORIAL004,
                    )
                ],
                (
                    _docs(
                        "tutorial003",
                        73,
                        88,
                        "OAuth2 form login and protected route included in OpenAPI",
                    ),
                    _OAUTH2_FORM,
                    _OPENAPI_FORM_BODY,
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial004.py": _module(
        "Tutorial 004 requests exercise FastAPI's form dependency, required bearer extraction, protected route dependency, and selected OpenAPI fields. The recipes use synthetic auth inputs; pwdlib and JWT outputs remain excluded or gated.",
        {
            "test_login": _fn(
                "test_tutorial004.py",
                "test_login",
                "The source posts form credentials and checks FastAPI's login route response.",
                "The linked synthetic workflow submits different credentials and a synthetic token, then performs an extra protected request. It samples form binding and route response handling; pwdlib, PyJWT, and exact login JSON are not claimed.",
                [
                    _case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-token",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs(
                        "tutorial004",
                        118,
                        134,
                        "login route verifies app credentials and creates a JWT",
                    ),
                    _OAUTH2_FORM,
                    _FORM_REQUEST,
                    _FORM_FIELDS,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "request-validation", "response-serialization"],
            ),
            "test_no_token": _fn(
                "test_tutorial004.py",
                "test_no_token",
                "The protected route rejects a missing OAuth2 bearer value before JWT decoding.",
                "The independent case sends a missing token to a synthetic protected endpoint. It covers FastAPI's required bearer/dependency boundary only; no cryptographic decode or full header/JSON comparison is claimed.",
                [
                    _http_case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-no-token",
                        "protected-request",
                    )
                ],
                (
                    _docs("tutorial004", 52, 52, "required OAuth2PasswordBearer dependency"),
                    _docs("tutorial004", 92, 109, "JWT decoding occurs after bearer extraction"),
                    _OAUTH2_REQUIRED,
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
            ),
            "test_token": _fn(
                "test_tutorial004.py",
                "test_token",
                "The workflow first submits synthetic login input, then supplies a bearer value to the protected route.",
                "The recipe deliberately avoids tutorial pwdlib and PyJWT behavior. It samples FastAPI form, bearer, and dependency integration with independent user/token data; the source's full User JSON and cryptographic token are not compared.",
                [
                    _case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-token",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs("tutorial004", 52, 52, "OAuth2PasswordBearer dependency"),
                    _docs("tutorial004", 92, 109, "app-owned JWT decode and user lookup"),
                    _docs("tutorial004", 112, 138, "active-user dependency and protected route"),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_incorrect_token_type": _fn(
                "test_tutorial004.py",
                "test_incorrect_token_type",
                "A wrong authorization scheme is rejected by OAuth2PasswordBearer before the tutorial's JWT decoder.",
                "The independent required-bearer wrong-scheme case uses another route and header value. It selects raw response bytes and the complete ordered headers; the source checks one named challenge and parsed JSON.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-wrong-scheme",
                        "required-bearer-wrong-scheme",
                    )
                ],
                (
                    _docs("tutorial004", 52, 52, "required OAuth2PasswordBearer dependency"),
                    _docs(
                        "tutorial004",
                        92,
                        109,
                        "app-owned JWT decode behind the security dependency",
                    ),
                    _OAUTH2_BEARER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_read_items": _fn(
                "test_tutorial004.py",
                "test_read_items",
                "The source requests the protected item route after obtaining a tutorial JWT through login.",
                "The independent workflow uses synthetic login and bearer data and a separately authored item. It covers FastAPI route dependency execution; tutorial JWT validation and exact item JSON remain gated.",
                [
                    _case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-read-items",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs("tutorial004", 52, 52, "OAuth2PasswordBearer dependency"),
                    _docs("tutorial004", 92, 109, "app-owned JWT decode and user lookup"),
                    _docs(
                        "tutorial004",
                        112,
                        143,
                        "active-user dependency and protected current-user/item routes",
                    ),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_openapi_schema": _fn(
                "test_tutorial004.py",
                "test_openapi_schema",
                "The source snapshot checks OAuth2 password-flow metadata, form requestBody, and security requirements for current-user and item operations.",
                "The linked case selects the OAuth2 component, token requestBody, and two security pointers. It does not claim complete snapshot equality, operation metadata, or unrelated generated schemas.",
                [
                    _case(
                        _TUTORIAL004,
                        "fastapi.security-tutorial004.test-openapi-schema",
                        ["inspect-openapi"],
                        _OPENAPI_TUTORIAL004,
                    )
                ],
                (
                    _docs("tutorial004", 52, 52, "OAuth2PasswordBearer configuration"),
                    _docs("tutorial004", 118, 143, "login, current-user, and item path operations"),
                    _OAUTH2_FORM,
                    _OPENAPI_FORM_BODY,
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial005.py": _module(
        "Tutorial 005 adds OAuth2 scope propagation and scope-dependent routes to the synthetic login/bearer flow. Existing cases sample token scope input, dependency requests, and selected OpenAPI security pointers; application JWT/password logic remains outside the mapped behavior.",
        {
            "test_login": _fn(
                "test_tutorial005.py",
                "test_login",
                "The source posts form data to a route that turns requested scopes into a JWT claim.",
                "The independent workflow submits synthetic form values and an additional protected request. It samples OAuth2 form binding; app-owned password checking, JWT claims, and exact token JSON are gated.",
                [
                    _case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-token",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs("tutorial005", 64, 67, "OAuth2PasswordBearer scope declarations"),
                    _docs(
                        "tutorial005",
                        150,
                        163,
                        "OAuth2 form login and app-owned JWT scope creation",
                    ),
                    _OAUTH2_FORM,
                    _FORM_REQUEST,
                    _FORM_FIELDS,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "request-validation", "response-serialization"],
            ),
            "test_no_token": _fn(
                "test_tutorial005.py",
                "test_no_token",
                "The source checks that an absent bearer is rejected by the required security dependency.",
                "The independent case sends no authorization to a synthetic protected route. The raw body and full ordered header list are selected; exact source JSON decoding and named-header semantics remain gated.",
                [
                    _http_case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-no-token",
                        "protected-request",
                    )
                ],
                (
                    _docs("tutorial005", 64, 67, "required OAuth2PasswordBearer configuration"),
                    _docs(
                        "tutorial005",
                        107,
                        139,
                        "scope-aware current-user dependency after bearer extraction",
                    ),
                    _OAUTH2_REQUIRED,
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
            ),
            "test_token": _fn(
                "test_tutorial005.py",
                "test_token",
                "The workflow submits synthetic login input and exercises a protected request that receives a bearer value.",
                "The case samples FastAPI form and bearer dependency integration with independent scope/token inputs. It intentionally does not exercise tutorial pwdlib/JWT decoding or assert the complete source User object.",
                [
                    _case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-token",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs("tutorial005", 64, 67, "OAuth2PasswordBearer scopes"),
                    _docs(
                        "tutorial005",
                        107,
                        139,
                        "scope-aware token parsing and dependency resolution",
                    ),
                    _docs(
                        "tutorial005", 150, 167, "app-owned token issuance and protected user route"
                    ),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_incorrect_token_type": _fn(
                "test_tutorial005.py",
                "test_incorrect_token_type",
                "A non-Bearer scheme is rejected by FastAPI before application JWT parsing.",
                "The independent case uses another wrong scheme and route. Its raw response bytes and full ordered headers are selected; the source asserts parsed JSON and a named challenge header.",
                [
                    _http_case(
                        _SECURITY_DEPENDENCIES,
                        "fastapi.docs.security.bearer-required-wrong-scheme",
                        "required-bearer-wrong-scheme",
                    )
                ],
                (
                    _docs("tutorial005", 64, 67, "required OAuth2PasswordBearer dependency"),
                    _docs(
                        "tutorial005",
                        107,
                        128,
                        "application JWT validation behind bearer extraction",
                    ),
                    _OAUTH2_BEARER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_token_no_scope": _fn(
                "test_tutorial005.py",
                "test_token_no_scope",
                "The test reaches a scope-protected operation with a token lacking its required scope.",
                "The independent case submits synthetic login data and sends a bearer to a separately authored scope-protected route. It samples FastAPI's Security dependency graph and scope injection, not JWT claim parsing or the tutorial's exact authorization response.",
                [
                    _case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-token-no-scope",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs(
                        "tutorial005",
                        107,
                        139,
                        "SecurityScopes injection and scope comparison in app code",
                    ),
                    _docs("tutorial005", 170, 174, "items route declares the items scope"),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_read_items": _fn(
                "test_tutorial005.py",
                "test_read_items",
                "The source requests the `/users/me/items/` route whose FastAPI Security dependency requires the items scope.",
                "The independent recipe uses a synthetic token and separately authored item route. It samples scoped dependency resolution and request handling; application JWT checks and exact item JSON remain gated.",
                [
                    _case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-read-items",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs("tutorial005", 107, 139, "scope-aware dependency and authorization path"),
                    _docs("tutorial005", 170, 174, "items route declares the items scope"),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_read_system_status": _fn(
                "test_tutorial005.py",
                "test_read_system_status",
                "The source route uses the current-user dependency without declaring an additional operation scope.",
                "The independent workflow samples a separately authored authenticated route with synthetic token data. It does not assert the tutorial's exact status object or app-owned JWT decoding.",
                [
                    _case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-read-system-status",
                        ["submit-login", "protected-request"],
                        _HTTP,
                    )
                ],
                (
                    _docs(
                        "tutorial005",
                        107,
                        139,
                        "current-user dependency without app-level operation scopes",
                    ),
                    _docs("tutorial005", 177, 179, "authenticated status endpoint"),
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_read_system_status_no_token": _fn(
                "test_tutorial005.py",
                "test_read_system_status_no_token",
                "The source status route still requires the OAuth2PasswordBearer dependency even though it declares no operation scope.",
                "The independent case requests its status route without a token. It samples required bearer rejection on a different route and does not claim app response equivalence.",
                [
                    _http_case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-read-system-status-no-token",
                        "protected-request",
                    )
                ],
                (
                    _docs("tutorial005", 64, 67, "required OAuth2PasswordBearer dependency"),
                    _docs("tutorial005", 177, 179, "status route with get_current_user dependency"),
                    _OAUTH2_REQUIRED,
                    _OAUTH2_BEARER,
                    _DEPENDENCY_SOLVER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial005.py",
                "test_openapi_schema",
                "The source snapshot asserts OAuth2 scope declarations, form requestBody, and operation security for scoped routes.",
                "The independent case selects the password-flow scope map, login requestBody, and two route security pointers. Other snapshot fields and all generated names are not claimed.",
                [
                    _case(
                        _TUTORIAL005,
                        "fastapi.security-tutorial005.test-openapi-schema",
                        ["inspect-openapi"],
                        _OPENAPI_TUTORIAL005,
                    )
                ],
                (
                    _docs("tutorial005", 64, 67, "OAuth2 password-flow scope descriptions"),
                    _docs(
                        "tutorial005",
                        150,
                        179,
                        "login, scoped user/items, and status path operations",
                    ),
                    _OAUTH2_FORM,
                    _OPENAPI_FORM_BODY,
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial006.py": _module(
        "Tutorial 006 tests HTTPBasic credential extraction, missing/malformed authorization handling, and an OpenAPI snapshot. Existing independent cases cover each FastAPI-owned parser branch and the Basic security projection.",
        {
            "test_security_http_basic": _fn(
                "test_tutorial006.py",
                "test_security_http_basic",
                "The source exposes both parsed HTTPBasic username and password fields to the endpoint.",
                "The independent case uses different credentials and route values. It selects response bytes, ordered headers, and status to sample HTTPBasic parsing and dependency injection; source values are not expected outputs here.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.valid",
                        "valid-basic-credentials",
                    )
                ],
                (
                    _docs(
                        "tutorial006",
                        6,
                        11,
                        "HTTPBasic dependency and endpoint returning both parsed credentials",
                    ),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _AUTHORIZATION_SPLIT,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_security_http_basic_no_credentials": _fn(
                "test_tutorial006.py",
                "test_security_http_basic_no_credentials",
                "The test verifies that required HTTPBasic credentials trigger a 401 response with a Basic challenge.",
                "The independent missing-credentials input selects raw body bytes and the complete ordered header list. It samples missing-credential rejection; parsed JSON and the source's named challenge lookup are not separate selectors.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.missing",
                        "missing-basic-credentials",
                    )
                ],
                (
                    _docs("tutorial006", 6, 11, "required HTTPBasic dependency"),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_security_http_basic_invalid_credentials": _fn(
                "test_tutorial006.py",
                "test_security_http_basic_invalid_credentials",
                "A Basic header with malformed Base64 is rejected by FastAPI's HTTPBasic parser.",
                "The independent case uses a different malformed payload and route. It selects raw bytes and ordered headers; the source's parsed JSON and named challenge assertions are not separately represented.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.malformed-base64",
                        "invalid-basic-base64",
                    )
                ],
                (
                    _docs("tutorial006", 6, 11, "HTTPBasic dependency"),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_security_http_basic_non_basic_credentials": _fn(
                "test_tutorial006.py",
                "test_security_http_basic_non_basic_credentials",
                "Despite its name, this test sends a Basic scheme with Base64 content that decodes without a username/password separator; FastAPI rejects the malformed pair.",
                "The independent malformed-pair case uses different decoded text and a different route. It samples HTTPBasic's missing-separator branch, not a non-Basic authorization scheme.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.malformed-pair",
                        "basic-payload-without-separator",
                    )
                ],
                (
                    _docs("tutorial006", 6, 11, "HTTPBasic dependency"),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _AUTHORIZATION_SPLIT,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial006.py",
                "test_openapi_schema",
                "The source snapshot checks an HTTP Basic security scheme and its operation requirement.",
                "The independent case selects the HTTPBasic component and one operation security pointer for another path. It does not claim a complete OpenAPI snapshot or generated operation metadata.",
                [
                    _case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.openapi",
                        ["inspect-basic-security-schema"],
                        _OPENAPI_BASIC,
                    )
                ],
                (
                    _docs("tutorial006", 6, 11, "HTTPBasic model and protected path operation"),
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial007.py": _module(
        "Tutorial 007 keeps HTTPBasic parsing in FastAPI and adds tutorial-owned constant-time credential comparison. Existing cases cover parsed credentials, required and malformed headers, and one rejected-credential route; username/password comparison details remain gated.",
        {
            "test_security_http_basic": _fn(
                "test_tutorial007.py",
                "test_security_http_basic",
                "A valid Basic header reaches the endpoint through HTTPBasic and the tutorial then checks application-owned credential constants.",
                "The independent case uses other valid credentials and returns parsed fields from an unrelated route. It samples FastAPI's parser and injection; `secrets.compare_digest` and the tutorial's exact username response are app-owned and unclaimed.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.valid",
                        "valid-basic-credentials",
                    )
                ],
                (
                    _docs(
                        "tutorial007",
                        8,
                        28,
                        "HTTPBasic dependency followed by app-owned constant-time username/password checks",
                    ),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _AUTHORIZATION_SPLIT,
                    _DEPENDENCY_SOLVER,
                ),
                ["dependency-security", "response-serialization"],
            ),
            "test_security_http_basic_no_credentials": _fn(
                "test_tutorial007.py",
                "test_security_http_basic_no_credentials",
                "Required HTTPBasic rejects a request before the app-owned username/password comparison.",
                "The independent case selects raw bytes and all ordered headers; it does not project the source's exact parsed JSON or named challenge assertion.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.missing",
                        "missing-basic-credentials",
                    )
                ],
                (
                    _docs("tutorial007", 8, 11, "required HTTPBasic dependency"),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_security_http_basic_invalid_credentials": _fn(
                "test_tutorial007.py",
                "test_security_http_basic_invalid_credentials",
                "A malformed Base64 Basic credential is rejected in FastAPI before tutorial credential checks.",
                "The independent case uses a different malformed payload and route. It selects raw response bytes and complete ordered headers, not the source's parsed JSON or named challenge assertion.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.malformed-base64",
                        "invalid-basic-base64",
                    )
                ],
                (
                    _docs("tutorial007", 8, 11, "HTTPBasic dependency"),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
            ),
            "test_security_http_basic_non_basic_credentials": _fn(
                "test_tutorial007.py",
                "test_security_http_basic_non_basic_credentials",
                "The test name says non-Basic, but its header is Basic and its decoded payload lacks the colon separator required by HTTPBasicCredentials.",
                "The independent malformed-pair case samples that no-separator parser branch with different payload text and a different route.",
                [
                    _http_case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.malformed-pair",
                        "basic-payload-without-separator",
                    )
                ],
                (
                    _docs("tutorial007", 8, 11, "HTTPBasic dependency"),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _AUTHORIZATION_SPLIT,
                ),
            ),
            "test_security_http_basic_invalid_username": _fn(
                "test_tutorial007.py",
                "test_security_http_basic_invalid_username",
                "The request supplies parseable Basic credentials, after which the tutorial's application code rejects its username/password pair.",
                "The independent checked-Basic workflow supplies a different rejected credential pair and selects response bytes, headers, and status. It samples FastAPI parsing plus a rejection response, but does not distinguish an invalid username from an invalid password or compare app-specific text.",
                [
                    _http_case(
                        _SECURITY_WAVE,
                        "fastapi.security-wave.http-basic-tutorial-007.test-security-http-basic-invalid-password",
                        "dispatch",
                    )
                ],
                (
                    _docs(
                        "tutorial007",
                        8,
                        28,
                        "HTTPBasic parsing followed by app-owned credential comparison and HTTPException",
                    ),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
                ["dependency-security", "public-api-errors"],
            ),
            "test_security_http_basic_invalid_password": _fn(
                "test_tutorial007.py",
                "test_security_http_basic_invalid_password",
                "The request supplies parseable Basic credentials and the app rejects the password through its own comparison branch.",
                "The independent checked-Basic case uses a different rejected pair and route. It samples FastAPI parsing and HTTPException response emission; app-specific values and exact body equality remain gated.",
                [
                    _http_case(
                        _SECURITY_WAVE,
                        "fastapi.security-wave.http-basic-tutorial-007.test-security-http-basic-invalid-password",
                        "dispatch",
                    )
                ],
                (
                    _docs(
                        "tutorial007",
                        8,
                        28,
                        "HTTPBasic parsing followed by app-owned credential comparison and HTTPException",
                    ),
                    _HTTP_BASIC,
                    _HTTP_BASIC_PARSER,
                    _DEPENDENCY_SOLVER,
                    _HTTP_EXCEPTION_HANDLER,
                ),
                ["dependency-security", "public-api-errors"],
            ),
            "test_openapi_schema": _fn(
                "test_tutorial007.py",
                "test_openapi_schema",
                "The source snapshot checks the HTTP Basic scheme and operation security requirement, not the tutorial credential-comparison helper.",
                "The independent case selects only the security component and requirement pointer for a separately authored path; complete OpenAPI equality and generated metadata remain gated.",
                [
                    _case(
                        _HTTP_BASIC_RECIPE,
                        "fastapi.advanced.security.http-basic.openapi",
                        ["inspect-basic-security-schema"],
                        _OPENAPI_BASIC,
                    )
                ],
                (
                    _docs("tutorial007", 8, 32, "HTTPBasic dependency and protected route"),
                    _OPENAPI_SECURITY_SCHEME,
                    _OPENAPI_SECURITY_OPERATION,
                ),
                ["dependency-security", "openapi-docs"],
            ),
        },
    ),
}


def _exclusion(
    test_path: str,
    function_name: str,
    reason: str,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "mapping_status": "source-backed-exclusion",
        "reason": reason,
        "supporting_sources": [
            _test_span(test_path, function_name),
            *sources,
        ],
    }


SECURITY_TUTORIAL_TEST_FUNCTION_EXCLUSIONS: dict[str, dict[str, dict[str, Any]]] = {}

# Preserve the established pwdlib/PyJWT exclusions exactly, adding each pinned
# test function span so every omitted assertion is still auditable.
for _test_path, _excluded_functions in _SYNTHETIC_AUTH_EXCLUSIONS.items():
    if _test_path not in {
        _TEST_ROOT + "test_tutorial004.py",
        _TEST_ROOT + "test_tutorial005.py",
    }:
        continue
    for _name, _reason in _excluded_functions.items():
        SECURITY_TUTORIAL_TEST_FUNCTION_EXCLUSIONS.setdefault(_test_path, {})[_name] = _exclusion(
            _test_path,
            _name,
            _reason,
            [dict(source) for source in _SYNTHETIC_AUTH_EXCLUSION_EVIDENCE[_test_path][_name]],
        )

# Keep the direct pwdlib/PyJWT helper exclusions already used by the atlas.
_DIRECT_HELPER_EXCLUSIONS = {
    "test_tutorial004.py": {
        "test_verify_password": (
            "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
            _docs("tutorial004", 57, 62, "application password helper"),
        ),
        "test_get_password_hash": (
            "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
            _docs("tutorial004", 57, 62, "application password helper"),
        ),
        "test_create_access_token": (
            "Direct PyJWT token-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
            _docs("tutorial004", 81, 89, "application JWT token helper"),
        ),
    },
    "test_tutorial005.py": {
        "test_verify_password": (
            "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
            _docs("tutorial005", 72, 78, "application password helper"),
        ),
        "test_get_password_hash": (
            "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
            _docs("tutorial005", 72, 78, "application password helper"),
        ),
        "test_create_access_token": (
            "Direct PyJWT token-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
            _docs("tutorial005", 96, 104, "application JWT token helper"),
        ),
    },
}
for _file_name, _functions in _DIRECT_HELPER_EXCLUSIONS.items():
    _test_path = _TEST_ROOT + _file_name
    for _name, (_reason, _source_row) in _functions.items():
        SECURITY_TUTORIAL_TEST_FUNCTION_EXCLUSIONS.setdefault(_test_path, {})[_name] = _exclusion(
            _test_path, _name, _reason, [_source_row]
        )

# These tutorial 003 assertions are entirely about fake in-memory application
# authentication policy. Successful form binding, required bearer behavior,
# wrong-scheme rejection, and generic HTTPException handling have separate
# FastAPI-owned workflow evidence above or in the handling-errors mappings.
_TUTORIAL003_APP_EXCLUSIONS = {
    "test_login_incorrect_password": (
        "The source route compares the submitted password against a tutorial-owned fake hash and raises its app-owned credential error. Successful form binding is mapped separately; this negative credential policy is not FastAPI behavior.",
        _docs(
            "tutorial003",
            73,
            83,
            "app-owned fake user lookup, password comparison, and error branch",
        ),
    ),
    "test_login_incorrect_username": (
        "The source route looks up the username in the tutorial's in-memory fake database and raises its app-owned credential error. This negative user-database policy is outside FastAPI's form/dependency contract.",
        _docs("tutorial003", 73, 78, "app-owned fake user lookup and error branch"),
    ),
    "test_incorrect_token": (
        "OAuth2PasswordBearer accepts the syntactically valid bearer string; the source failure comes from the tutorial's fake token-to-user lookup and custom HTTPException, not a FastAPI token validator.",
        _docs("tutorial003", 49, 64, "app-owned fake token decoding and user lookup"),
    ),
}
_TUTORIAL003_PATH = _TEST_ROOT + "test_tutorial003.py"
for _name, (_reason, _source_row) in _TUTORIAL003_APP_EXCLUSIONS.items():
    SECURITY_TUTORIAL_TEST_FUNCTION_EXCLUSIONS.setdefault(_TUTORIAL003_PATH, {})[_name] = (
        _exclusion(_TUTORIAL003_PATH, _name, _reason, [_source_row])
    )


# The reviewed recipes use independently authored inputs. The tutorial 003
# inactive-user case samples bearer extraction and nested dependency dispatch
# while treating the authorization policy as app-owned.
