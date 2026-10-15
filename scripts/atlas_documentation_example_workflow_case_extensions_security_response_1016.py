"""Additive reviewed links from selected FastAPI examples to workflow cases."""

DOC_EXAMPLE_WORKFLOW_CASE_EXTENSIONS_SECURITY_RESPONSE_1016 = [
    {
        "source_path": "docs_src/security/tutorial005_an_py310.py",
        "recipe_path": "tests/fixtures/input-recipes/parity/docs-security-scopes-1016.yaml",
        "case_id": "fastapi.docs.security-scopes-1016.oauth2-surface",
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
        "supporting_sources": [
            {
                "path": "docs_src/security/tutorial005_an_py310.py",
                "start_line": 65,
                "end_line": 68,
                "role": "OAuth2PasswordBearer configuration with declared scopes",
            },
            {
                "path": "docs_src/security/tutorial005_an_py310.py",
                "start_line": 108,
                "end_line": 110,
                "role": "SecurityScopes and bearer dependency injection",
            },
            {
                "path": "docs_src/security/tutorial005_an_py310.py",
                "start_line": 143,
                "end_line": 177,
                "role": "scoped current-user and item route declarations",
            },
        ],
    },
    {
        "source_path": "docs_src/security/tutorial004_an_py310.py",
        "recipe_path": "tests/fixtures/input-recipes/parity/docs-security-scopes-1016.yaml",
        "case_id": "fastapi.docs.security-scopes-1016.oauth2-surface",
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.security",
        ],
        "supporting_sources": [
            {
                "path": "docs_src/security/tutorial004_an_py310.py",
                "start_line": 53,
                "end_line": 53,
                "role": "OAuth2PasswordBearer configuration",
            },
            {
                "path": "docs_src/security/tutorial004_an_py310.py",
                "start_line": 93,
                "end_line": 95,
                "role": "Annotated bearer dependency parameter",
            },
            {
                "path": "docs_src/security/tutorial004_an_py310.py",
                "start_line": 139,
                "end_line": 150,
                "role": "protected current-user and item route declarations",
            },
        ],
    },
    {
        "source_path": "docs_src/response_directly/tutorial002_py310.py",
        "recipe_path": "tests/fixtures/input-recipes/parity/response-directly-custom-xml-1016.yaml",
        "case_id": "fastapi.docs.response-directly.custom-xml-response",
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "supporting_sources": [
            {
                "path": "docs_src/response_directly/tutorial002_py310.py",
                "start_line": 6,
                "end_line": 18,
                "role": "GET route returning a Response with XML content and media type",
            }
        ],
    },
    {
        "source_path": "docs_src/response_headers/tutorial001_py310.py",
        "recipe_path": "tests/fixtures/input-recipes/parity/docs-response-headers-1016.yaml",
        "case_id": "fastapi.docs.response-headers-1016.direct-response",
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "supporting_sources": [
            {
                "path": "docs_src/response_headers/tutorial001_py310.py",
                "start_line": 7,
                "end_line": 11,
                "role": "JSONResponse route declaring response headers",
            }
        ],
    },
]
