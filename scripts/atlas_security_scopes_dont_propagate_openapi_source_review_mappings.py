"""Pinned-source review sidecar for nested SecurityScopes/OpenAPI inputs.

This is source and input review metadata only. It does not run FastAPI, invoke
the target, assert expected output, or update generated atlas artifacts.
"""

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "pinned FastAPI source oracle and development evidence only",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI and response contract; not the scope/OpenAPI owner",
    },
    "starlette-rs": {
        "distribution": "starlette-rs-py==0.1.0",
        "commit": "7293140ebe9d8e27dc879710a0d7426cbd8f392c",
        "role": "target implementation of the pinned Starlette generic contract",
    },
    "python": {
        "implementation": "CPython",
        "version": "3.12.13",
    },
    "pydantic": {
        "version": "2.13.4",
        "pydantic-core": "2.46.4",
        "role": "pinned public model/schema dependency",
    },
}

RECIPE_PATH = (
    "tests/fixtures/input-recipes/parity/security-scopes-dont-propagate-openapi-source-review.yaml"
)
CASE_ID = "fastapi.security.scopes-dont-propagate.nested-openapi-sibling-scopes"
ACTION_ID = "inspect-nested-oauth-scope-projection"

_SELECTORS = ["http.status", "openapi.security"]
_WORKFLOW = {
    "recipe_path": RECIPE_PATH,
    "case_ids": [CASE_ID],
    "observation_selectors": list(_SELECTORS),
}

SECURITY_SCOPE_NONPROPAGATION_OPENAPI_ATLAS_MAPPINGS = {
    "tests/test_security_scopes_dont_propagate.py": {
        "feature_ids": ["dependency-security", "openapi-docs", "response-serialization"],
        "observation_selectors": ["http.status", "http.body.json", "openapi.security"],
        "replace_features": True,
        "rationale": (
            "The existing runtime workflow observes parent-plus-local scope accumulation "
            "for two sibling dependencies. This supplemental OpenAPI case independently "
            "projects the same nested shape through a shared OAuth2 scheme."
        ),
        "stimulus_notes": (
            f"Use {RECIPE_PATH}::{CASE_ID} action {ACTION_ID}; it selects the scheme scope "
            "catalog and operation security requirements without expected values."
        ),
        "module_observation_selectors": list(_SELECTORS),
        "workflow_cases": [_WORKFLOW],
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/security/oauth2-scopes.md",
                "start_line": 103,
                "end_line": 123,
                "role": "Pinned docs describe scoped Security dependencies and OpenAPI integration",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 99,
                "end_line": 152,
                "role": "FastAPI carries parent OAuth scopes to security dependencies and merges same-scheme requirements",
            },
        ],
        "functions": {
            "test_security_scopes_dont_propagate": {
                "feature_ids": [
                    "dependency-security",
                    "openapi-docs",
                    "response-serialization",
                ],
                "observation_selectors": list(_SELECTORS),
                "replace_features": True,
                "rationale": (
                    "The test's runtime sibling-scope assertion is now paired with a separate "
                    "OpenAPI observation for nested OAuth2 scope projection."
                ),
                "contract_gate": (
                    "Partial: the upstream test asserts runtime SecurityScopes values, not OpenAPI. "
                    "The OAuth2 docs and OpenAPI implementation support the complementary case; "
                    "only the selected scope-map and operation-security pointers are claimed."
                ),
                "stimulus_notes": (
                    f"The added input-only case is {RECIPE_PATH}::{CASE_ID}; the earlier "
                    "security-scopes recipe retains the runtime response observation."
                ),
                "supporting_sources": [
                    {
                        "path": "tests/test_security_scopes_dont_propagate.py",
                        "start_line": 38,
                        "end_line": 44,
                        "role": "Pinned source test asserts parent scope accumulation without sibling-scope leakage",
                    },
                    {
                        "path": "docs/en/docs/advanced/security/oauth2-scopes.md",
                        "start_line": 193,
                        "end_line": 216,
                        "role": "Pinned docs describe dependency-tree scope accumulation",
                    },
                    {
                        "path": "fastapi/openapi/utils.py",
                        "start_line": 99,
                        "end_line": 152,
                        "role": "FastAPI OpenAPI traversal accumulates and merges OAuth2 requirements",
                    },
                ],
            }
        },
    }
}

REVIEW = {
    "status": "source-reviewed-input-only",
    "recipe": "tests/fixtures/input-recipes/parity/security-scopes-dont-propagate-openapi-source-review.yaml",
    "workload": "tests/fixtures/workloads/security_scopes_dont_propagate_openapi_source_review.py",
    "case_id": "fastapi.security.scopes-dont-propagate.nested-openapi-sibling-scopes",
    "action_id": "inspect-nested-oauth-scope-projection",
    "selected_json_pointers": [
        "/components/securitySchemes/OAuth2PasswordBearer/flows/password/scopes",
        "/paths/~1catalog~1items/get/security",
    ],
    "claim": (
        "The new graph independently adds an OpenAPI observation to the existing "
        "runtime sibling-scope contract: one parent scope feeds two sibling "
        "Security dependencies, and their OAuth2 scheme requirements are projected "
        "onto the generated operation. The YAML records only request input and "
        "selected output pointers."
    ),
    "limits": [
        "The upstream non-propagation test asserts runtime SecurityScopes values, not OpenAPI.",
        "The pinned OAuth2 scopes documentation and OpenAPI source support the complementary OpenAPI observation.",
        "No target parity, expected-value assertion, or generic Starlette behavior is claimed.",
    ],
    "sources": [
        {
            "path": "tests/test_security_scopes_dont_propagate.py",
            "line_span": [38, 44],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/tests/test_security_scopes_dont_propagate.py#L38-L44",
            "sha256": "cde24ff0cd8515c672aedd9f63b3c8e5cad1c4029e98846da108b1498f897818",
            "role": "pinned test asserts each nested sibling receives the parent scope and its own local scope",
        },
        {
            "path": "docs/en/docs/advanced/security/oauth2-scopes.md",
            "line_span": [103, 123],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/docs/en/docs/advanced/security/oauth2-scopes.md#L103-L123",
            "sha256": "c8e866d22d766b9473958b91c0231c2547ded1f323207ca1c64609df2b36bb5e",
            "role": "pinned documentation describes Security scopes at path-operation and nested-dependency levels",
        },
        {
            "path": "docs/en/docs/advanced/security/oauth2-scopes.md",
            "line_span": [193, 216],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/docs/en/docs/advanced/security/oauth2-scopes.md#L193-L216",
            "sha256": "c8e866d22d766b9473958b91c0231c2547ded1f323207ca1c64609df2b36bb5e",
            "role": "pinned documentation spells out parent-to-child SecurityScopes accumulation",
        },
        {
            "path": "docs_src/security/tutorial005_an_py310.py",
            "line_span": [65, 68],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/docs_src/security/tutorial005_an_py310.py#L65-L68",
            "sha256": "c92250c94e43ed6925be98f1cbe61c8207e67cf11ffefb78fb845c5280272396",
            "role": "pinned documentation example declares OAuth2 scope descriptions",
        },
        {
            "path": "docs_src/security/tutorial005_an_py310.py",
            "line_span": [108, 110],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/docs_src/security/tutorial005_an_py310.py#L108-L110",
            "sha256": "c92250c94e43ed6925be98f1cbe61c8207e67cf11ffefb78fb845c5280272396",
            "role": "pinned documentation example injects SecurityScopes beside the OAuth2 scheme dependency",
        },
        {
            "path": "docs_src/security/tutorial005_an_py310.py",
            "line_span": [143, 145],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/docs_src/security/tutorial005_an_py310.py#L143-L145",
            "sha256": "c92250c94e43ed6925be98f1cbe61c8207e67cf11ffefb78fb845c5280272396",
            "role": "pinned documentation example declares one scoped Security subdependency",
        },
        {
            "path": "docs_src/security/tutorial005_an_py310.py",
            "line_span": [173, 175],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/docs_src/security/tutorial005_an_py310.py#L173-L175",
            "sha256": "c92250c94e43ed6925be98f1cbe61c8207e67cf11ffefb78fb845c5280272396",
            "role": "pinned documentation example adds a parent path-operation Security scope",
        },
        {
            "path": "fastapi/openapi/utils.py",
            "line_span": [99, 152],
            "citation": "https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/openapi/utils.py#L99-L152",
            "sha256": "81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527",
            "role": "pinned OpenAPI implementation carries parent OAuth scopes to security dependencies and merges same-scheme requirements",
        },
    ],
}
