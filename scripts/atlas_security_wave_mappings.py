"""Source-reviewed top-level FastAPI security test mappings.

The cases below point to independently authored workflows. Generic request
parsing, TestClient transport, and ASGI behavior remain in the Starlette-RS
contract; these mappings cover FastAPI security objects, dependency resolution,
scope propagation, errors, strict form validation, and OpenAPI projection.
"""

from __future__ import annotations

import ast
from pathlib import Path

_FASTAPI_ROOT = Path(__file__).resolve().parents[2] / "fastapi"
_TEST_ROOT = _FASTAPI_ROOT / "tests"


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(test_path: str, function_name: str) -> dict[str, object]:
    path = _TEST_ROOT / test_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    return _span(
        f"tests/{test_path}",
        node.lineno,
        node.end_lineno or node.lineno,
        "upstream stimulus and asserted observations for this exact test function",
    )


def _case(
    test_path: str,
    function_name: str,
    case_ids: list[str],
    feature_ids: list[str],
    observation_selectors: list[str],
    rationale: str,
    *,
    contract_gate: str | None = None,
    stimulus_detail: str = "",
) -> dict[str, object]:
    ids = ", ".join(f"`{case_id}`" for case_id in case_ids)
    stimulus_notes = (
        f"Independent input case(s): {ids}. "
        "The referenced case is input-only and executes its declared workload "
        "through the FastAPI public ASGI interface; it contains no expected output. "
        "The upstream test span is retained separately as the source authority. " + stimulus_detail
    )
    result: dict[str, object] = {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(observation_selectors),
        "rationale": rationale,
        "replace_features": True,
        "stimulus_notes": stimulus_notes,
        "supporting_sources": [_test_function_span(test_path, function_name)],
    }
    if contract_gate:
        result["contract_gate"] = contract_gate
    return result


def _module(
    test_path: str,
    functions: dict[str, dict[str, object]],
    production_sources: list[dict[str, object]],
    rationale: str,
    *,
    module_observation_selectors: list[str] | None = None,
) -> dict[str, object]:
    path = _TEST_ROOT / test_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tests = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]
    setup_end = min((node.lineno for node in tests), default=1) - 1
    sources = [
        _span(
            f"tests/{test_path}",
            1,
            max(setup_end, 1),
            "upstream app, security dependency, and route declarations under review",
        ),
        *production_sources,
    ]
    return {
        "rationale": rationale,
        "supporting_sources": sources,
        "module_observation_selectors": module_observation_selectors
        or ["http.status", "http.body.json", "openapi.security"],
        "functions": functions,
    }


def _openapi_gate() -> str:
    return (
        "The upstream function compares a complete OpenAPI JSON snapshot. The "
        "independent workflow selects the cited security-scheme, operation-security, "
        "or request-schema JSON pointers only; unrelated OpenAPI fields are not claimed."
    )


def _challenge_gate() -> str:
    return (
        "The upstream function asserts the value of WWW-Authenticate by header name. "
        "The fixed workflow can select the complete ordered header list but cannot "
        "project one named header; this mapping covers status and JSON body, while "
        "the challenge assertion remains a visible observation-schema gap."
    )


_API_KEY_SOURCES = [
    _span(
        "fastapi/security/api_key.py",
        11,
        52,
        "APIKeyBase builds the scheme, handles missing credentials, and applies auto_error",
    ),
    _span(
        "fastapi/security/api_key.py",
        132,
        145,
        "APIKeyQuery construction and query-parameter extraction",
    ),
    _span(
        "fastapi/security/api_key.py", 179, 233, "APIKeyHeader construction and header extraction"
    ),
    _span(
        "fastapi/security/api_key.py", 235, 320, "APIKeyCookie construction and cookie extraction"
    ),
    _span(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI recursively builds dependency nodes from endpoint declarations",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        656,
        697,
        "FastAPI resolves dependencies and extracts declared request parameters",
    ),
    _span(
        "fastapi/openapi/utils.py",
        99,
        156,
        "FastAPI discovers security dependencies and encodes named schemes",
    ),
    _span(
        "fastapi/openapi/utils.py",
        311,
        356,
        "FastAPI attaches dependency-derived security to OpenAPI operations",
    ),
    _span(
        "fastapi/exception_handlers.py",
        11,
        17,
        "FastAPI serializes HTTPException status, detail, and headers",
    ),
]

_HTTP_BASE_SOURCES = [
    _span(
        "fastapi/security/http.py",
        69,
        102,
        "HTTPBase constructs its OpenAPI model, parses authorization, and handles auto_error",
    ),
    _span(
        "fastapi/security/utils.py",
        1,
        7,
        "FastAPI splits the authorization scheme and strips surrounding credential whitespace",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI builds the security dependency node from the endpoint signature",
    ),
    _span("fastapi/openapi/utils.py", 99, 156, "FastAPI encodes the HTTP security scheme"),
    _span(
        "fastapi/openapi/utils.py",
        311,
        356,
        "FastAPI attaches the security requirement to an OpenAPI operation",
    ),
    _span(
        "fastapi/exception_handlers.py",
        11,
        17,
        "FastAPI renders the authentication HTTPException as JSON",
    ),
]

_HTTP_BASIC_SOURCES = [
    _span(
        "fastapi/security/http.py",
        105,
        219,
        "HTTPBasic handles realm challenges, Base64 credentials, separators, and auto_error",
    ),
    *_HTTP_BASE_SOURCES[1:],
]

_HTTP_BEARER_SOURCES = [
    _span(
        "fastapi/security/http.py",
        222,
        316,
        "HTTPBearer parses and validates the Bearer scheme and applies auto_error",
    ),
    *_HTTP_BASE_SOURCES[1:],
]

_HTTP_DIGEST_SOURCES = [
    _span(
        "fastapi/security/http.py",
        319,
        417,
        "HTTPDigest validates Digest scheme presence and applies auto_error; it is a documented stub, not a Digest protocol implementation",
    ),
    *_HTTP_BASE_SOURCES[1:],
]

_OAUTH2_SOURCES = [
    _span(
        "fastapi/security/oauth2.py",
        14,
        160,
        "OAuth2PasswordRequestForm extracts OAuth2 password-flow form fields",
    ),
    _span(
        "fastapi/security/oauth2.py",
        162,
        224,
        "OAuth2PasswordRequestFormStrict requires grant_type=password",
    ),
    _span(
        "fastapi/security/oauth2.py",
        330,
        431,
        "OAuth2 constructs flow metadata, scheme name, auto_error behavior, and generic authorization extraction",
    ),
    _span(
        "fastapi/security/oauth2.py",
        433,
        546,
        "OAuth2PasswordBearer constructs its password flow and validates Bearer authorization",
    ),
    _span(
        "fastapi/security/oauth2.py",
        547,
        652,
        "OAuth2AuthorizationCodeBearer constructs its flow and validates Bearer authorization",
    ),
    _span(
        "fastapi/security/utils.py",
        1,
        7,
        "FastAPI splits the authorization scheme and strips credential whitespace",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI expands Security and Depends into recursive dependency nodes",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        656,
        730,
        "FastAPI resolves dependencies, request fields, and injected security scopes",
    ),
    _span(
        "fastapi/openapi/utils.py",
        99,
        156,
        "FastAPI aggregates OAuth2 security definitions and operation scopes",
    ),
    _span(
        "fastapi/openapi/utils.py",
        311,
        356,
        "FastAPI places dependency-derived OAuth2 requirements on operations",
    ),
    _span(
        "fastapi/exception_handlers.py",
        11,
        17,
        "FastAPI serializes security HTTPException responses",
    ),
]

_OPENID_SOURCES = [
    _span(
        "fastapi/security/open_id_connect_url.py",
        11,
        94,
        "OpenIdConnect constructs the scheme model and returns or rejects the authorization header",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI builds the OpenIdConnect security dependency node",
    ),
    _span(
        "fastapi/openapi/utils.py",
        99,
        156,
        "FastAPI emits the OpenID Connect scheme name and model",
    ),
    _span(
        "fastapi/openapi/utils.py",
        311,
        356,
        "FastAPI attaches the OpenID Connect security requirement to an operation",
    ),
    _span(
        "fastapi/exception_handlers.py",
        11,
        17,
        "FastAPI renders missing required authorization as JSON",
    ),
]

_SCOPES_SOURCES = [
    _span(
        "fastapi/security/oauth2.py",
        653,
        693,
        "SecurityScopes stores scope lists and exposes their joined scope string",
    ),
    _span(
        "fastapi/dependencies/models.py",
        64,
        89,
        "FastAPI accumulates OAuth scopes and includes scope-sensitive cache keys",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI propagates parent and local Security scopes through dependency construction",
    ),
    _span(
        "fastapi/dependencies/utils.py",
        656,
        730,
        "FastAPI resolves and caches dependencies and injects SecurityScopes",
    ),
    _span(
        "fastapi/openapi/utils.py",
        99,
        156,
        "FastAPI collects security scopes and merges them into operation requirements",
    ),
    _span(
        "fastapi/openapi/utils.py",
        311,
        356,
        "FastAPI attaches OAuth2 scopes to generated OpenAPI operations",
    ),
]

_FORM_FEATURES = ["dependency-security", "request-validation", "response-serialization"]
_SECURITY_SUCCESS = ["dependency-security", "response-serialization"]
_SECURITY_ERROR = ["dependency-security", "public-api-errors"]
_SECURITY_OPENAPI = ["dependency-security", "openapi-docs"]


def _api_key_module(
    test_path: str,
    case_prefix: str,
    *,
    optional: bool = False,
    success_case: str | None = None,
    missing_case: str | None = None,
    openapi_case: str | None = None,
    rationale: str,
) -> dict[str, object]:
    success = success_case or f"{case_prefix}.test-security-api-key"
    missing = missing_case or f"{case_prefix}.test-security-api-key-no-key"
    missing_feature = _SECURITY_SUCCESS if optional else _SECURITY_ERROR
    missing_reason = (
        "auto_error=False yields None and the route returns its optional-authentication JSON."
        if optional
        else "A missing API key is rejected by FastAPI's APIKeyBase check before the route executes."
    )
    funcs = {
        "test_security_api_key": _case(
            test_path,
            "test_security_api_key",
            [success],
            _SECURITY_SUCCESS,
            ["http.status", "http.body.json"],
            "A supplied API key is extracted from the declared request location and passed to the route.",
        ),
        "test_security_api_key_no_key": _case(
            test_path,
            "test_security_api_key_no_key",
            [missing],
            missing_feature,
            ["http.status", "http.body.json"] if optional else ["http.status", "http.body.json"],
            missing_reason,
            contract_gate=None if optional else _challenge_gate(),
        ),
        "test_openapi_schema": _case(
            test_path,
            "test_openapi_schema",
            [openapi_case or f"{case_prefix}.test-openapi-schema"],
            _SECURITY_OPENAPI,
            ["http.status", "openapi.security"],
            "FastAPI serializes the security model and attaches the scheme requirement to the operation.",
            contract_gate=_openapi_gate(),
            stimulus_detail=(
                "The selected workflow covers scheme metadata and the operation requirement. "
                "For optional security, auto_error changes request handling, not the OpenAPI model; "
                "the selected OpenAPI case can therefore use the corresponding required scheme."
                if optional
                else "The workflow selects the security scheme and operation requirement."
            ),
        ),
    }
    return _module(
        test_path,
        funcs,
        _API_KEY_SOURCES,
        rationale,
        module_observation_selectors=[
            "http.status",
            "http.body.json",
            "openapi.security",
        ],
    )


def _module_level(
    test_path: str,
    feature_ids: list[str],
    selectors: list[str],
    rationale: str,
    case_notes: str,
    production_sources: list[dict[str, object]],
    *,
    contract_gate: str | None = None,
) -> dict[str, object]:
    result = _module(
        test_path,
        {},
        production_sources,
        rationale,
        module_observation_selectors=selectors,
    )
    result.update(
        {
            "feature_ids": list(feature_ids),
            "observation_selectors": list(selectors),
            "replace_features": True,
            "stimulus_notes": (
                "Module-level case mapping (source test-function spans are generated "
                "individually from the pinned upstream AST): "
                + case_notes
                + " Inputs are independent recipe/workload cases with no expected values. "
                "Request header/form parsing and TestClient transport remain generic "
                "Starlette-RS responsibilities; the mapped features are FastAPI's "
                "security dependency, scope, validation, or OpenAPI behavior."
            ),
        }
    )
    if contract_gate:
        result["contract_gate"] = contract_gate
    return result


SECURITY_TEST_REVIEW_MAPPINGS: dict[str, dict[str, object]] = {
    "tests/test_security_api_key_cookie.py": _api_key_module(
        "test_security_api_key_cookie.py",
        "fastapi.security.api-key-cookie",
        rationale="Required APIKeyCookie extraction, FastAPI's missing-key response, and default-name OpenAPI security projection.",
    ),
    "tests/test_security_api_key_cookie_description.py": _api_key_module(
        "test_security_api_key_cookie_description.py",
        "fastapi.security.api-key-cookie-description",
        openapi_case="fastapi.security-atlas-wave.api-key-cookie-description.default-name-openapi",
        rationale="Described APIKeyCookie request extraction plus default scheme-name and description projection in OpenAPI.",
    ),
    "tests/test_security_api_key_cookie_optional.py": _api_key_module(
        "test_security_api_key_cookie_optional.py",
        "fastapi.security.api-key-cookie-optional",
        optional=True,
        openapi_case="fastapi.security.api-key-cookie.test-openapi-schema",
        rationale="Optional APIKeyCookie extraction, None propagation for an absent cookie, and the scheme's auto_error-independent OpenAPI representation.",
    ),
    "tests/test_security_api_key_header_description.py": _api_key_module(
        "test_security_api_key_header_description.py",
        "fastapi.security.api-key-header-description",
        rationale="Described APIKeyHeader request extraction, missing-key rejection, and default-name OpenAPI projection.",
    ),
    "tests/test_security_api_key_header_optional.py": _api_key_module(
        "test_security_api_key_header_optional.py",
        "fastapi.docs.security",
        optional=True,
        success_case="fastapi.docs.security.api-key-optional-provided",
        missing_case="fastapi.docs.security.api-key-optional-missing",
        openapi_case="fastapi.test.security-api-key-header.default-name-openapi",
        rationale="Optional APIKeyHeader extraction and None propagation; OpenAPI uses the default APIKeyHeader scheme name, independent of auto_error.",
    ),
    "tests/test_security_api_key_query.py": _api_key_module(
        "test_security_api_key_query.py",
        "fastapi.security.api-key-query",
        rationale="Required APIKeyQuery extraction, missing-key rejection, and default-name OpenAPI security projection.",
    ),
    "tests/test_security_api_key_query_description.py": _api_key_module(
        "test_security_api_key_query_description.py",
        "fastapi.security.api-key-query-description",
        openapi_case="fastapi.security-atlas-wave.api-key-query-description.default-name-openapi",
        rationale="Described APIKeyQuery extraction and FastAPI's default scheme-name/description projection.",
    ),
    "tests/test_security_api_key_query_optional.py": _api_key_module(
        "test_security_api_key_query_optional.py",
        "fastapi.security.api-key-query-optional",
        optional=True,
        openapi_case="fastapi.security.api-key-query.test-openapi-schema",
        rationale="Optional APIKeyQuery extraction and None propagation; auto_error does not alter the scheme's OpenAPI model.",
    ),
    "tests/test_security_http_base.py": _module(
        "test_security_http_base.py",
        {
            "test_security_http_base": _case(
                "test_security_http_base.py",
                "test_security_http_base",
                ["fastapi.security-wave.http-base-scheme.test-security-http-base"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "HTTPBase returns the parsed authorization scheme and credential string to the route.",
            ),
            "test_security_http_base_with_whitespaces": _case(
                "test_security_http_base.py",
                "test_security_http_base_with_whitespaces",
                ["fastapi.security-gap.http-base.test-security-http-base-with-whitespaces"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "FastAPI's authorization parser splits once and strips whitespace from the credential parameter.",
            ),
            "test_security_http_base_no_credentials": _case(
                "test_security_http_base.py",
                "test_security_http_base_no_credentials",
                ["fastapi.security-gap.http-base.test-security-http-base-no-credentials"],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Required HTTPBase raises its FastAPI authentication exception when authorization or credentials are absent.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_base.py",
                "test_openapi_schema",
                ["fastapi.security-gap.http-base.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "HTTPBase's scheme model and dependency requirement are emitted in OpenAPI.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BASE_SOURCES,
        "HTTPBase security parsing and challenge construction are FastAPI-owned; raw header access and TestClient behavior are generic Starlette boundaries.",
    ),
    "tests/test_security_http_base_description.py": _module(
        "test_security_http_base_description.py",
        {
            "test_security_http_base": _case(
                "test_security_http_base_description.py",
                "test_security_http_base",
                ["fastapi.security-gap.http-base-description.test-security-http-base"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "A described HTTPBase still returns the split scheme and stripped credential value.",
            ),
            "test_security_http_base_no_credentials": _case(
                "test_security_http_base_description.py",
                "test_security_http_base_no_credentials",
                [
                    "fastapi.security-gap.http-base-description.test-security-http-base-no-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "A missing credential is rejected even when the HTTPBase OpenAPI model has a description.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_base_description.py",
                "test_openapi_schema",
                ["fastapi.security-gap.http-base-description.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "The described HTTPBase model and operation security requirement are projected into OpenAPI.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BASE_SOURCES,
        "The module distinguishes HTTPBase description metadata from authorization-header parsing; Starlette owns header access and client transport.",
    ),
    "tests/test_security_http_base_optional.py": _module(
        "test_security_http_base_optional.py",
        {
            "test_security_http_base": _case(
                "test_security_http_base_optional.py",
                "test_security_http_base",
                ["fastapi.security.http-base-optional.test-security-http-base"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "Optional HTTPBase returns authorization credentials when the configured generic scheme is present.",
            ),
            "test_security_http_base_no_credentials": _case(
                "test_security_http_base_optional.py",
                "test_security_http_base_no_credentials",
                ["fastapi.security.http-base-optional.test-security-http-base-no-credentials"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "With auto_error=False, absent authorization becomes None and the route returns its optional-authentication response.",
            ),
            "test_openapi_schema": _case(
                "test_security_http_base_optional.py",
                "test_openapi_schema",
                ["fastapi.security-gap.http-base.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "auto_error does not change HTTPBase's OpenAPI scheme model; the independent required HTTPBase case has the same default scheme definition.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BASE_SOURCES,
        "Optional HTTPBase shares FastAPI's header parsing with the required form but returns None instead of raising when auto_error is false.",
    ),
    "tests/test_security_http_basic_optional.py": _module(
        "test_security_http_basic_optional.py",
        {
            "test_security_http_basic": _case(
                "test_security_http_basic_optional.py",
                "test_security_http_basic",
                ["fastapi.security.http-basic-optional.test-security-http-basic"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "Optional HTTPBasic decodes a valid Basic credential and passes username/password to the route.",
            ),
            "test_security_http_basic_no_credentials": _case(
                "test_security_http_basic_optional.py",
                "test_security_http_basic_no_credentials",
                ["fastapi.security.http-basic-optional.test-security-http-basic-no-credentials"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "With auto_error=False, no Basic authorization yields None and the route returns its optional response.",
            ),
            "test_security_http_basic_invalid_credentials": _case(
                "test_security_http_basic_optional.py",
                "test_security_http_basic_invalid_credentials",
                [
                    "fastapi.security.http-basic-optional.test-security-http-basic-invalid-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Malformed Base64 remains an authentication failure even with auto_error=False after a Basic scheme is present.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_basic_non_basic_credentials": _case(
                "test_security_http_basic_optional.py",
                "test_security_http_basic_non_basic_credentials",
                [
                    "fastapi.security.http-basic-optional.test-security-http-basic-non-basic-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "A decoded Basic value without the username/password separator raises the FastAPI authentication exception.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_basic_optional.py",
                "test_openapi_schema",
                ["fastapi.security-atlas-wave.http-basic-realm.no-description-openapi"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "auto_error is not part of HTTPBasic's OpenAPI scheme; the independent default-name HTTPBasic case checks the same HTTP basic model.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BASIC_SOURCES,
        "HTTPBasic's Base64 decoding, separator validation, realm challenge, and optional missing-credential branch are FastAPI-owned; generic request headers and transport remain Starlette-RS behavior.",
    ),
    "tests/test_security_http_basic_realm.py": _module(
        "test_security_http_basic_realm.py",
        {
            "test_security_http_basic": _case(
                "test_security_http_basic_realm.py",
                "test_security_http_basic",
                ["fastapi.security-gap.http-basic-realm-description.test-security-http-basic"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "A valid Basic credential is decoded independently of the configured challenge realm.",
            ),
            "test_security_http_basic_no_credentials": _case(
                "test_security_http_basic_realm.py",
                "test_security_http_basic_no_credentials",
                [
                    "fastapi.security.http-basic-realm-description.test-security-http-basic-no-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "The configured realm is included in HTTPBasic's required-credential challenge.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_basic_invalid_credentials": _case(
                "test_security_http_basic_realm.py",
                "test_security_http_basic_invalid_credentials",
                [
                    "fastapi.security-gap.http-basic-realm-description.test-security-http-basic-invalid-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Invalid Base64 raises the HTTPBasic authentication error with the configured realm challenge.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_basic_non_basic_credentials": _case(
                "test_security_http_basic_realm.py",
                "test_security_http_basic_non_basic_credentials",
                [
                    "fastapi.security-gap.http-basic-realm-description.test-security-http-basic-non-basic-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "A Basic payload without a colon is rejected with the configured realm challenge.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_basic_realm.py",
                "test_openapi_schema",
                ["fastapi.security-atlas-wave.http-basic-realm.no-description-openapi"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "The HTTPBasic realm affects challenge headers, while the OpenAPI basic scheme contains type and scheme fields; the independent case selects those fields.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BASIC_SOURCES,
        "This module makes the realm observable in the WWW-Authenticate challenge; realm and description are distinct from HTTPBasic's OpenAPI scheme model.",
    ),
    "tests/test_security_http_basic_realm_description.py": _module(
        "test_security_http_basic_realm_description.py",
        {
            "test_security_http_basic": _case(
                "test_security_http_basic_realm_description.py",
                "test_security_http_basic",
                ["fastapi.security-gap.http-basic-realm-description.test-security-http-basic"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "A valid Basic credential is decoded by the described HTTPBasic security dependency.",
            ),
            "test_security_http_basic_no_credentials": _case(
                "test_security_http_basic_realm_description.py",
                "test_security_http_basic_no_credentials",
                [
                    "fastapi.security.http-basic-realm-description.test-security-http-basic-no-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Missing credentials return the FastAPI authentication error with the configured realm challenge.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_basic_invalid_credentials": _case(
                "test_security_http_basic_realm_description.py",
                "test_security_http_basic_invalid_credentials",
                [
                    "fastapi.security-gap.http-basic-realm-description.test-security-http-basic-invalid-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Invalid Base64 credentials are rejected; the description does not change runtime decoding.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_basic_non_basic_credentials": _case(
                "test_security_http_basic_realm_description.py",
                "test_security_http_basic_non_basic_credentials",
                [
                    "fastapi.security-gap.http-basic-realm-description.test-security-http-basic-non-basic-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "A decoded Basic payload without a separator is rejected; the description does not change runtime validation.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_basic_realm_description.py",
                "test_openapi_schema",
                ["fastapi.security.http-basic-realm-description.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "FastAPI includes the HTTPBasic description in its OpenAPI security-scheme definition.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BASIC_SOURCES,
        "The described realm module separately exposes FastAPI's HTTPBasic description in OpenAPI and realm-specific HTTP authentication errors.",
    ),
    "tests/test_security_http_bearer.py": _module(
        "test_security_http_bearer.py",
        {
            "test_security_http_bearer": _case(
                "test_security_http_bearer.py",
                "test_security_http_bearer",
                ["fastapi.security.http-bearer.test-security-http-bearer"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "HTTPBearer accepts a Bearer authorization value and returns its parsed scheme and token.",
            ),
            "test_security_http_bearer_no_credentials": _case(
                "test_security_http_bearer.py",
                "test_security_http_bearer_no_credentials",
                ["fastapi.security.http-bearer.test-security-http-bearer-no-credentials"],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "A required HTTPBearer dependency rejects an absent authorization header.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_bearer_incorrect_scheme_credentials": _case(
                "test_security_http_bearer.py",
                "test_security_http_bearer_incorrect_scheme_credentials",
                [
                    "fastapi.security.http-bearer.test-security-http-bearer-incorrect-scheme-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "HTTPBearer rejects a present authorization value whose scheme is not Bearer.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_bearer.py",
                "test_openapi_schema",
                ["fastapi.security.http-bearer.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "FastAPI encodes the default HTTPBearer security model and operation requirement.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BEARER_SOURCES,
        "HTTPBearer scheme validation and FastAPI's error challenge are distinct from generic Starlette authorization-header access.",
    ),
    "tests/test_security_http_bearer_description.py": _module(
        "test_security_http_bearer_description.py",
        {
            "test_security_http_bearer": _case(
                "test_security_http_bearer_description.py",
                "test_security_http_bearer",
                ["fastapi.security.http-bearer-description.test-security-http-bearer"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "A valid Bearer token is parsed and returned by the described HTTPBearer scheme.",
            ),
            "test_security_http_bearer_no_credentials": _case(
                "test_security_http_bearer_description.py",
                "test_security_http_bearer_no_credentials",
                [
                    "fastapi.security.http-bearer-description.test-security-http-bearer-no-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "The described HTTPBearer dependency rejects a missing authorization header.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_bearer_incorrect_scheme_credentials": _case(
                "test_security_http_bearer_description.py",
                "test_security_http_bearer_incorrect_scheme_credentials",
                [
                    "fastapi.security.http-bearer-description.test-security-http-bearer-incorrect-scheme-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "The described HTTPBearer dependency rejects a non-Bearer authorization scheme.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_bearer_description.py",
                "test_openapi_schema",
                ["fastapi.security-atlas-wave.http-bearer-description.default-name-openapi"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "FastAPI applies the default HTTPBearer scheme name and includes the supplied description in OpenAPI.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BEARER_SOURCES,
        "HTTPBearer runtime behavior is unchanged by description metadata; the independent default-name OpenAPI case isolates the scheme description and security requirement.",
    ),
    "tests/test_security_http_bearer_optional.py": _module(
        "test_security_http_bearer_optional.py",
        {
            "test_security_http_bearer": _case(
                "test_security_http_bearer_optional.py",
                "test_security_http_bearer",
                ["fastapi.security.http-bearer-optional.test-security-http-bearer"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "Optional HTTPBearer returns parsed credentials when a Bearer header is present.",
            ),
            "test_security_http_bearer_no_credentials": _case(
                "test_security_http_bearer_optional.py",
                "test_security_http_bearer_no_credentials",
                ["fastapi.security.http-bearer-optional.test-security-http-bearer-no-credentials"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "With auto_error=False, absent authorization becomes None and the route produces its optional response.",
            ),
            "test_security_http_bearer_incorrect_scheme_credentials": _case(
                "test_security_http_bearer_optional.py",
                "test_security_http_bearer_incorrect_scheme_credentials",
                [
                    "fastapi.security.http-bearer-optional.test-security-http-bearer-incorrect-scheme-credentials"
                ],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "With auto_error=False, a non-Bearer scheme returns None rather than raising.",
            ),
            "test_openapi_schema": _case(
                "test_security_http_bearer_optional.py",
                "test_openapi_schema",
                ["fastapi.security.http-bearer.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "auto_error does not change the HTTPBearer OpenAPI model; the default-name required case exercises the same scheme representation.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_BEARER_SOURCES,
        "Optional HTTPBearer differs at the missing/wrong-scheme branches; generic header extraction is delegated to the pinned Starlette-RS contract.",
    ),
    "tests/test_security_http_digest.py": _module(
        "test_security_http_digest.py",
        {
            "test_security_http_digest": _case(
                "test_security_http_digest.py",
                "test_security_http_digest",
                ["fastapi.security-wave.http-digest.test-security-http-digest"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "HTTPDigest accepts a Digest-scheme header and returns the parsed credentials; this is a scheme stub, not a full digest challenge-response protocol.",
            ),
            "test_security_http_digest_no_credentials": _case(
                "test_security_http_digest.py",
                "test_security_http_digest_no_credentials",
                ["fastapi.security-gap.http-digest.test-security-http-digest-no-credentials"],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Required HTTPDigest rejects missing credentials and constructs the FastAPI challenge response.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_digest_incorrect_scheme_credentials": _case(
                "test_security_http_digest.py",
                "test_security_http_digest_incorrect_scheme_credentials",
                [
                    "fastapi.security-gap.http-digest.test-security-http-digest-incorrect-scheme-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "Required HTTPDigest rejects an authorization header using another scheme.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_digest.py",
                "test_openapi_schema",
                ["fastapi.security-gap.http-digest.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "FastAPI projects the HTTP Digest scheme model and operation requirement into OpenAPI.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_DIGEST_SOURCES,
        "HTTPDigest only validates the Digest authorization scheme and returns credentials; the upstream source documents that full Digest protocol behavior is not implemented.",
    ),
    "tests/test_security_http_digest_description.py": _module(
        "test_security_http_digest_description.py",
        {
            "test_security_http_digest": _case(
                "test_security_http_digest_description.py",
                "test_security_http_digest",
                ["fastapi.security-wave.http-digest.test-security-http-digest"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "Description metadata does not change HTTPDigest's accepted authorization scheme or returned credentials.",
            ),
            "test_security_http_digest_no_credentials": _case(
                "test_security_http_digest_description.py",
                "test_security_http_digest_no_credentials",
                ["fastapi.security-gap.http-digest.test-security-http-digest-no-credentials"],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "The described HTTPDigest dependency still rejects missing credentials.",
                contract_gate=_challenge_gate(),
            ),
            "test_security_http_digest_incorrect_scheme_credentials": _case(
                "test_security_http_digest_description.py",
                "test_security_http_digest_incorrect_scheme_credentials",
                [
                    "fastapi.security-gap.http-digest.test-security-http-digest-incorrect-scheme-credentials"
                ],
                _SECURITY_ERROR,
                ["http.status", "http.body.json"],
                "The described HTTPDigest dependency still rejects non-Digest schemes.",
                contract_gate=_challenge_gate(),
            ),
            "test_openapi_schema": _case(
                "test_security_http_digest_description.py",
                "test_openapi_schema",
                ["fastapi.security-gap.http-digest-description.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "FastAPI includes the HTTPDigest description in its OpenAPI security scheme.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_DIGEST_SOURCES,
        "This module tests HTTPDigest description metadata in OpenAPI and leaves runtime scheme validation unchanged.",
    ),
    "tests/test_security_http_digest_optional.py": _module(
        "test_security_http_digest_optional.py",
        {
            "test_security_http_digest": _case(
                "test_security_http_digest_optional.py",
                "test_security_http_digest",
                ["fastapi.security-gap.http-digest-optional.test-security-http-digest"],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "Optional HTTPDigest accepts and returns Digest authorization credentials.",
            ),
            "test_security_http_digest_no_credentials": _case(
                "test_security_http_digest_optional.py",
                "test_security_http_digest_no_credentials",
                [
                    "fastapi.security-wave.http-digest-optional.test-security-http-digest-no-credentials"
                ],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "With auto_error=False, missing Digest credentials yield None and the optional route response.",
            ),
            "test_security_http_digest_incorrect_scheme_credentials": _case(
                "test_security_http_digest_optional.py",
                "test_security_http_digest_incorrect_scheme_credentials",
                [
                    "fastapi.security-gap.http-digest-optional.test-security-http-digest-incorrect-scheme-credentials"
                ],
                _SECURITY_SUCCESS,
                ["http.status", "http.body.json"],
                "With auto_error=False, a non-Digest scheme yields None rather than an authentication exception.",
            ),
            "test_openapi_schema": _case(
                "test_security_http_digest_optional.py",
                "test_openapi_schema",
                ["fastapi.security-gap.http-digest-optional.test-openapi-schema"],
                _SECURITY_OPENAPI,
                ["http.status", "openapi.security"],
                "auto_error does not change the HTTPDigest OpenAPI model; the independent case selects the optional default-name scheme.",
                contract_gate=_openapi_gate(),
            ),
        },
        _HTTP_DIGEST_SOURCES,
        "Optional HTTPDigest returns None for missing or wrong-scheme authorization; the request-header interface remains Starlette-owned.",
    ),
}

_MODULE_LEVEL_SECURITY_REVIEWS = {
    "test_security_oauth2.py": _module_level(
        "test_security_oauth2.py",
        [
            "dependency-security",
            "request-validation",
            "public-api-errors",
            "response-serialization",
            "openapi-docs",
        ],
        ["http.status", "http.body.json", "openapi.security"],
        "Required generic OAuth2 extraction, strict password-form validation, and security/form OpenAPI projection.",
        "test_security_oauth2 -> `fastapi.security-wave.oauth2-base.test-security-oauth2`; test_security_oauth2_password_other_header -> `fastapi.security-gap.oauth2-required.test-security-oauth2-password-other-header`; test_security_oauth2_password_bearer_no_header -> `fastapi.security-gap.oauth2-required.test-security-oauth2-password-bearer-no-header`; strict form missing/no-grant/incorrect(grant_type=incorrect,passwordblah,blahpassword)/correct -> `fastapi.security-gap.oauth2-strict-required.test-strict-login-no-data`, `fastapi.security-gap.oauth2-strict-required.test-strict-login-no-grant-type`, `fastapi.security-gap.oauth2-strict-required.test-strict-login-incorrect-grant-type-incorrect`, `fastapi.security-gap.oauth2-strict-required.test-strict-login-incorrect-grant-type-passwordblah`, `fastapi.security-gap.oauth2-strict-required.test-strict-login-incorrect-grant-type-blahpassword`, `fastapi.security-gap.oauth2-strict-required.test-strict-login-correct-grant-type`; openapi -> `fastapi.security-gap.oauth2-strict-required.test-openapi-schema`.",
        _OAUTH2_SOURCES,
        contract_gate="Inputs select HTTP status/JSON and relevant OpenAPI pointers; the full source snapshot and generic URL-encoded form decoding are not claimed.",
    ),
    "test_security_oauth2_optional.py": _module_level(
        "test_security_oauth2_optional.py",
        [
            "dependency-security",
            "request-validation",
            "public-api-errors",
            "response-serialization",
            "openapi-docs",
        ],
        ["http.status", "http.body.json", "openapi.security"],
        "Optional generic OAuth2 extraction and strict password-form validation with auto_error=False.",
        "test_security_oauth2 -> `fastapi.security-gap.oauth2-optional.test-security-oauth2`; test_security_oauth2_password_other_header -> `fastapi.security-gap.oauth2-optional.test-security-oauth2-password-other-header`; test_security_oauth2_password_bearer_no_header -> `fastapi.security-wave.oauth2-optional.test-security-oauth2-password-bearer-no-header`; strict form missing/no-grant/incorrect(grant_type=incorrect,passwordblah,blahpassword)/correct -> `fastapi.security-gap.oauth2-strict-optional.test-strict-login-no-data`, `fastapi.security-gap.oauth2-strict-optional.test-strict-login-no-grant-type`, `fastapi.security-gap.oauth2-strict-optional.test-strict-login-incorrect-grant-type-incorrect`, `fastapi.security-gap.oauth2-strict-optional.test-strict-login-incorrect-grant-type-passwordblah`, `fastapi.security-gap.oauth2-strict-optional.test-strict-login-incorrect-grant-type-blahpassword`, `fastapi.security-gap.oauth2-strict-optional.test-strict-login-correct-data`; openapi -> `fastapi.security-gap.oauth2-strict-optional.test-openapi-schema`.",
        _OAUTH2_SOURCES,
        contract_gate="The strict-form inputs select HTTP JSON and selected OpenAPI pointers; generic form decoding and the full OpenAPI snapshot are not claimed.",
    ),
    "test_security_oauth2_optional_description.py": _module_level(
        "test_security_oauth2_optional_description.py",
        [
            "dependency-security",
            "request-validation",
            "public-api-errors",
            "response-serialization",
            "openapi-docs",
        ],
        ["http.status", "http.body.json", "openapi.security"],
        "Described optional OAuth2 extraction, strict form validation, and security-scheme/request-schema projection.",
        "test_security_oauth2 -> `fastapi.security.oauth2-optional-description.test-security-oauth2`; test_security_oauth2_password_other_header -> `fastapi.security.oauth2-optional-description.test-security-oauth2-password-other-header`; test_security_oauth2_password_bearer_no_header -> `fastapi.security.oauth2-optional-description.test-security-oauth2-password-bearer-no-header`; strict login none/no-grant/incorrect(incorrect,passwordblah,blahpassword)/correct -> `fastapi.security-gap.oauth2-optional-description.test-strict-login-none`, `fastapi.security-gap.oauth2-optional-description.test-strict-login-no-grant-type`, `fastapi.security-gap.oauth2-optional-description.test-strict-login-incorrect-grant-type-incorrect`, `fastapi.security-gap.oauth2-optional-description.test-strict-login-incorrect-grant-type-passwordblah`, `fastapi.security-gap.oauth2-optional-description.test-strict-login-incorrect-grant-type-blahpassword`, `fastapi.security-gap.oauth2-optional-description.test-strict-login-correct-correct-grant-type`; openapi -> `fastapi.security-atlas-wave.oauth2-optional-description.strict-form-openapi`.",
        _OAUTH2_SOURCES,
        contract_gate="OpenAPI selects the described scheme, strict-form schema, and request body only; generic form decoding and unrelated snapshot fields are not claimed.",
    ),
    "test_security_oauth2_authorization_code_bearer.py": _module_level(
        "test_security_oauth2_authorization_code_bearer.py",
        ["dependency-security", "public-api-errors", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Required OAuth2 authorization-code bearer extraction, errors, whitespace handling, and flow metadata.",
        "test_no_token/test_incorrect_token/test_token/test_token_with_whitespaces -> `fastapi.security.oauth2-authorization-code-bearer.test-no-token`, `fastapi.security.oauth2-authorization-code-bearer.test-incorrect-token`, `fastapi.security.oauth2-authorization-code-bearer.test-token`, `fastapi.security.oauth2-authorization-code-bearer.test-token-with-whitespaces`; test_openapi_schema -> `fastapi.security.oauth2-authorization-code-bearer.test-openapi-schema`. A separate target-only fault contract injects after the authorization-code dependency resolves and asserts request-dependency cleanup plus a successful follow-up request.",
        _OAUTH2_SOURCES,
        contract_gate="The independent request workload declares scopes while the source has an empty scope map; selected OpenAPI pointers cover flow URLs/type and operation security, not the scope map or full snapshot.",
    ),
    "test_security_oauth2_authorization_code_bearer_description.py": _module_level(
        "test_security_oauth2_authorization_code_bearer_description.py",
        ["dependency-security", "public-api-errors", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Described authorization-code bearer request behavior and default class-name/description OpenAPI projection.",
        "test_no_token/test_incorrect_token/test_token -> `fastapi.security.oauth2-authorization-code-bearer-description.test-no-token`, `fastapi.security.oauth2-authorization-code-bearer-description.test-incorrect-token`, `fastapi.security.oauth2-authorization-code-bearer-description.test-token`; test_openapi_schema -> `fastapi.security-atlas-wave.oauth2-authorization-code-bearer-description.default-name-openapi`.",
        _OAUTH2_SOURCES,
        contract_gate="The existing request route has a custom scheme name; the separate OpenAPI case checks the default class name and description but only selected pointers.",
    ),
    "test_security_oauth2_authorization_code_bearer_scopes_openapi.py": _module_level(
        "test_security_oauth2_authorization_code_bearer_scopes_openapi.py",
        ["dependency-security", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "OAuth2 scope composition across app, route, helper, and router dependencies with OpenAPI operation security.",
        "test_root -> `fastapi.security-oauth2-authorization-code-scopes.test-root`; test_read_with_oauth2_scheme -> `fastapi.security.oauth2-authorization-code-bearer-scopes-openapi.test-read-with-oauth2-scheme`; test_read_with_get_token -> `fastapi.security.oauth2-authorization-code-bearer-scopes-openapi.test-read-with-get-token`; test_read_token -> `fastapi.security.oauth2-authorization-code-bearer-scopes-openapi.test-read-token`; test_create_token -> `fastapi.security.oauth2-authorization-code-bearer-scopes-openapi.test-create-token`; test_openapi_schema -> `fastapi.security.oauth2-authorization-code-bearer-scopes-openapi.test-openapi-schema`.",
        _SCOPES_SOURCES + _OAUTH2_SOURCES,
        contract_gate="OpenAPI selects relevant OAuth2 scopes and operation requirements, not the whole snapshot; the independent app route graph is not a byte-for-byte copy.",
    ),
    "test_security_oauth2_authorization_code_bearer_scopes_openapi_simple.py": _module_level(
        "test_security_oauth2_authorization_code_bearer_scopes_openapi_simple.py",
        ["dependency-security", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Simple Security(get_token, scopes=...) dependency composition and its operation-security requirement.",
        "read-admin -> `fastapi.security-atlas-wave.oauth2-authorization-code-scopes.simple-dependencies-request`; openapi -> `fastapi.security-atlas-wave.oauth2-authorization-code-scopes.simple-dependencies-openapi`.",
        _SCOPES_SOURCES + _OAUTH2_SOURCES,
        contract_gate="The independent route uses route-level Depends/Security rather than source app-wide Depends(get_token) and names the scheme AtlasScopedOAuth2; scope propagation is covered, but the default name/full snapshot are not.",
    ),
    "test_security_oauth2_password_bearer_optional.py": _module_level(
        "test_security_oauth2_password_bearer_optional.py",
        ["dependency-security", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Optional OAuth2PasswordBearer behavior for absent, valid, and wrong-scheme headers plus default-name flow metadata.",
        "test_no_token/test_token/test_incorrect_token -> `fastapi.security.oauth2-password-bearer-optional-description.test-no-token`, `fastapi.security.oauth2-password-bearer-optional-description.test-token`, `fastapi.security.oauth2-password-bearer-optional-description.test-incorrect-token`; test_openapi_schema -> `fastapi.security-atlas-wave.oauth2-password-bearer-optional.default-name-openapi`.",
        _OAUTH2_SOURCES,
        contract_gate="Runtime requests use a described variant because description does not affect extraction; a separate no-description case covers default scheme naming and selected OpenAPI pointers.",
    ),
    "test_security_oauth2_password_bearer_optional_description.py": _module_level(
        "test_security_oauth2_password_bearer_optional_description.py",
        ["dependency-security", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Described optional OAuth2PasswordBearer extraction and OpenAPI representation.",
        "test_no_token/test_token/test_incorrect_token/test_openapi_schema -> `fastapi.security.oauth2-password-bearer-optional-description.test-no-token`, `fastapi.security.oauth2-password-bearer-optional-description.test-token`, `fastapi.security.oauth2-password-bearer-optional-description.test-incorrect-token`, `fastapi.security.oauth2-password-bearer-optional-description.test-openapi-schema`.",
        _OAUTH2_SOURCES,
        contract_gate="The OpenAPI case selects the described flow scheme and operation requirement, not the complete source snapshot.",
    ),
    "test_security_openid_connect.py": _module_level(
        "test_security_openid_connect.py",
        ["dependency-security", "public-api-errors", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Required OpenIdConnect returns the Authorization header unchanged, rejects absence, and emits its security model.",
        "test_security_oauth2 -> `fastapi.security.openid-connect.test-security-oauth2`; test_security_oauth2_password_other_header -> `fastapi.security.openid-connect.test-security-oauth2-password-other-header`; test_security_oauth2_password_bearer_no_header -> `fastapi.security.openid-connect.test-security-oauth2-password-bearer-no-header`; test_openapi_schema -> `fastapi.security.openid-connect.test-openapi-schema`.",
        _OPENID_SOURCES,
        contract_gate="The workflow selects scheme and operation pointers rather than the complete source snapshot; generic header access belongs to Starlette-RS.",
    ),
    "test_security_openid_connect_description.py": _module_level(
        "test_security_openid_connect_description.py",
        ["dependency-security", "public-api-errors", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Described OpenIdConnect request behavior and default class-name/description projection.",
        "test_security_oauth2/test_security_oauth2_password_other_header/test_security_oauth2_password_bearer_no_header -> `fastapi.security.openid-connect-description.test-security-oauth2`, `fastapi.security.openid-connect-description.test-security-oauth2-password-other-header`, `fastapi.security.openid-connect-description.test-security-oauth2-password-bearer-no-header`; test_openapi_schema -> `fastapi.security-atlas-wave.openid-connect-description.default-name-openapi`.",
        _OPENID_SOURCES,
        contract_gate="The request input uses a custom scheme name; the OpenAPI case checks default naming and description but only selected pointers.",
    ),
    "test_security_openid_connect_optional.py": _module_level(
        "test_security_openid_connect_optional.py",
        ["dependency-security", "response-serialization", "openapi-docs"],
        ["http.status", "http.body.json", "openapi.security"],
        "Optional OpenIdConnect returns a present authorization value and maps absence to None.",
        "test_security_oauth2/test_security_oauth2_password_other_header/test_security_oauth2_password_bearer_no_header -> `fastapi.security.openid-connect-optional.test-security-oauth2`, `fastapi.security.openid-connect-optional.test-security-oauth2-password-other-header`, `fastapi.security.openid-connect-optional.test-security-oauth2-password-bearer-no-header`; test_openapi_schema -> `fastapi.security.openid-connect.test-openapi-schema` because auto_error does not change the model.",
        _OPENID_SOURCES,
        contract_gate="The optional request input uses a custom scheme name; the required default-name case covers the same model, but not the optional operation path/full snapshot.",
    ),
    "test_security_scopes.py": _module_level(
        "test_security_scopes.py",
        ["dependency-security", "response-serialization"],
        ["http.status", "http.body.json"],
        "Scope-sensitive FastAPI dependency caching reuses a database dependency under nested Security scopes.",
        "test_security_scopes_dependency_called_once -> `fastapi.security.scopes.test-security-scopes-dependency-called-once`.",
        _SCOPES_SOURCES,
        contract_gate="The source directly asserts a Python fixture call counter; the independent response exposes cached data but has no dedicated call-count selector.",
    ),
    "test_security_scopes_dont_propagate.py": _module_level(
        "test_security_scopes_dont_propagate.py",
        ["dependency-security", "response-serialization"],
        ["http.status", "http.body.json"],
        "FastAPI passes nested SecurityScopes their parent-plus-local scopes without sibling-scope leakage.",
        "test_security_scopes_dont_propagate -> `fastapi.security.scopes-dont-propagate.test-security-scopes-dont-propagate`.",
        _SCOPES_SOURCES,
    ),
    "test_security_scopes_sub_dependency.py": _module_level(
        "test_security_scopes_sub_dependency.py",
        ["dependency-security", "response-serialization"],
        ["http.status", "http.body.json"],
        "FastAPI caches ordinary dependencies while resolving Security dependencies under distinct accumulated scopes.",
        "test_security_scopes_sub_dependency_caching -> `fastapi.security.scopes-sub-dependency.test-security-scopes-sub-dependency-caching`.",
        _SCOPES_SOURCES,
        contract_gate="The source asserts four fixture counters plus JSON output; independent output exposes scope-sensitive values but has no direct call-count selectors.",
    ),
}

SECURITY_TEST_REVIEW_MAPPINGS.update(
    {f"tests/{path}": mapping for path, mapping in _MODULE_LEVEL_SECURITY_REVIEWS.items()}
)
