"""Reviewed section-to-workflow mappings for FastAPI security API reference."""

_REFERENCE_SECURITY = "reference/security/index.md"
_SECURITY_DEPENDENCIES = "tests/fixtures/input-recipes/parity/security-dependencies.yaml"
_SECURITY_PUBLIC_API = "tests/fixtures/input-recipes/parity/security-oauth-public-api.yaml"
_RUNTIME_SELECTORS = [
    "docs.response.headers",
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.security",
]
_SIGNATURE_SELECTOR = ["python.signature"]


def _workflow(heading, start, end, recipe, cases, selectors, scope_note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "observation_selectors": selectors,
        "scope_note": scope_note,
        "rationale": rationale,
    }


DOC_SECTION_CASE_MAPPINGS_SECURITY_REFERENCE_SECTIONS_20261015 = {
    (_REFERENCE_SECURITY, "@line:1"): _workflow(
        "Security Tools",
        1,
        75,
        _SECURITY_DEPENDENCIES,
        [
            "fastapi.docs.security.api-key-required-missing",
            "fastapi.docs.security.api-key-required-provided",
            "fastapi.docs.security.bearer-required-missing",
            "fastapi.docs.security.bearer-required-valid",
            "fastapi.docs.security.bearer-required-wrong-scheme",
            "fastapi.docs.security.openapi",
        ],
        _RUNTIME_SELECTORS,
        (
            "The H1 span is the full page (lines 1-75); this mapping concerns its overview "
            "prose while the child headings have their own rows. Partial sample across six "
            "page-linked cases: required APIKeyHeader "
            "missing and provided, required OAuth2PasswordBearer missing, valid, and wrong "
            "scheme, plus selected generated security-scheme and operation pointers. The "
            "OpenAPI action also observes its response status and headers; it does not exercise "
            "Swagger or ReDoc HTML rendering. This does not cover every imported utility, "
            "optional credentials, token validation, or external OAuth flows."
        ),
        (
            "The pinned page's overview and import listing are docs/en/docs/reference/security/"
            "index.md#L1-L32. The existing page-backed input cases observe FastAPI's required "
            "header-key and bearer dependency results and the selected OpenAPI security "
            "projection. The selected OpenAPI action requests `/openapi.json`, so its status "
            "and headers are included with the selected document pointers; no interactive docs "
            "page is requested. FastAPI owns those dependency and schema paths in "
            "fastapi/security/api_key.py, fastapi/security/oauth2.py, and "
            "fastapi/openapi/utils.py."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:33"): _workflow(
        "API Key Security Schemes",
        33,
        40,
        _SECURITY_PUBLIC_API,
        [
            "fastapi.security.public-api.api-key-cookie",
            "fastapi.security.public-api.api-key-header",
            "fastapi.security.public-api.api-key-query",
        ],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes root-export, module-export, and constructor "
            "signatures for APIKeyCookie, APIKeyHeader, and APIKeyQuery. It does not claim "
            "credential extraction, missing-key responses, or OpenAPI projection."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L33-L40. "
            "Its three generated API directives name exactly the APIKey classes selected by "
            "the direct API probes. FastAPI defines them in fastapi/security/api_key.py:55-320; "
            "the cases observe only python.signature."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:41"): _workflow(
        "HTTP Authentication Schemes",
        41,
        48,
        _SECURITY_PUBLIC_API,
        [
            "fastapi.security.public-api.http-basic",
            "fastapi.security.public-api.http-bearer",
            "fastapi.security.public-api.http-digest",
        ],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes root-export, module-export, and constructor "
            "signatures for HTTPBasic, HTTPBearer, and HTTPDigest. It does not test "
            "Authorization parsing, authentication challenges, or OpenAPI output."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L41-L48. "
            "Its API directives correspond to the three selected FastAPI security classes in "
            "fastapi/security/http.py:105-417. The selected cases observe only "
            "python.signature."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:49"): _workflow(
        "HTTP Credentials",
        49,
        54,
        _SECURITY_PUBLIC_API,
        [
            "fastapi.security.public-api.http-authorization-credentials",
            "fastapi.security.public-api.http-basic-credentials",
        ],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes the public class signatures for "
            "HTTPAuthorizationCredentials and HTTPBasicCredentials. It does not claim "
            "credential parsing or Pydantic model-validation behavior."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L49-L54. "
            "The generated directives name the two credential classes probed from FastAPI's "
            "root and security.http modules; their definitions are in "
            "fastapi/security/http.py:16-66. "
            "The selected cases observe only python.signature."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:55"): _workflow(
        "OAuth2 Authentication",
        55,
        62,
        _SECURITY_PUBLIC_API,
        [
            "fastapi.security.public-api.oauth2",
            "fastapi.security.public-api.oauth2-authorization-code-bearer",
            "fastapi.security.public-api.oauth2-password-bearer",
        ],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes root-export, module-export, and constructor "
            "signatures for OAuth2, OAuth2AuthorizationCodeBearer, and OAuth2PasswordBearer. "
            "It does not test authorization-code exchange, token validity, or authorization policy."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L55-L62. "
            "Its API directives match the three selected FastAPI classes defined in "
            "fastapi/security/oauth2.py:330-650. The cases observe only python.signature."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:63"): _workflow(
        "OAuth2 Password Form",
        63,
        68,
        _SECURITY_PUBLIC_API,
        [
            "fastapi.security.public-api.oauth2-password-request-form",
            "fastapi.security.public-api.oauth2-password-request-form-strict",
        ],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes class and constructor signatures for the "
            "permissive and strict OAuth2 password-form dependencies. It does not test form "
            "field extraction, grant-type validation, or Pydantic behavior."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L63-L68. "
            "Its directives name OAuth2PasswordRequestForm and OAuth2PasswordRequestFormStrict, "
            "defined in fastapi/security/oauth2.py:14-327. The selected cases observe only "
            "python.signature."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:69"): _workflow(
        "OAuth2 Security Scopes in Dependencies",
        69,
        72,
        _SECURITY_PUBLIC_API,
        ["fastapi.security.public-api.security-scopes"],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes the SecurityScopes class and constructor "
            "signatures. It does not test scope accumulation, injection into a dependency, or "
            "authorization decisions."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L69-L72. "
            "Its generated directive names SecurityScopes, whose FastAPI definition is "
            "fastapi/security/oauth2.py:653-693. The selected case observes only "
            "python.signature."
        ),
    ),
    (_REFERENCE_SECURITY, "@line:73"): _workflow(
        "OpenID Connect",
        73,
        75,
        _SECURITY_PUBLIC_API,
        ["fastapi.security.public-api.open-id-connect"],
        _SIGNATURE_SELECTOR,
        (
            "Partial API-surface sample: observes the OpenIdConnect root-export, module-export, "
            "and constructor signatures. It does not claim provider discovery, token "
            "validation, or the generated OpenAPI security projection."
        ),
        (
            "The pinned reference section is docs/en/docs/reference/security/index.md#L73-L75. "
            "Its generated directive names FastAPI's OpenIdConnect class, defined in "
            "fastapi/security/open_id_connect_url.py:11-94. The selected case observes only "
            "python.signature."
        ),
    ),
}
