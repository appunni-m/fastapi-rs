"""Reviewed section mapping for FastAPI CLI pyproject entrypoint configuration."""

DOC_SECTION_CASE_MAPPINGS_FASTAPI_CLI_ENTRYPOINT_20261015 = {
    ("fastapi-cli.md", "configure-the-app-entrypoint-in-pyproject-toml"): {
        "heading": (
            "Configure the app `entrypoint` in `pyproject.toml` "
            "{ #configure-the-app-entrypoint-in-pyproject-toml }"
        ),
        "start_line": 61,
        "end_line": 115,
        "recipe_path": (
            "tests/fixtures/input-recipes/parity/fastapi-cli-documented-process-v2.yaml"
        ),
        "case_ids": ["fastapi.cli.process.dev-pyproject-entrypoint"],
        "observation_selectors": ["http.body.bytes", "http.status", "process.exit_code"],
        "scope_note": (
            "One isolated `fastapi dev` case reads `[tool.fastapi] entrypoint = "
            '"backend.main:app"`, imports that app, and serves one GET `/probe` request. '
            "The selectors cover process completion and that HTTP response. The nested "
            "command-option section, invalid configuration, explicit-entrypoint precedence, "
            "auto-discovery, terminal output, and reload behavior are outside this mapping."
        ),
        "rationale": (
            "FastAPI 0.141.1's optional `standard` extra requires "
            "`fastapi-cli[standard] >=0.0.32` (../fastapi/pyproject.toml:59-61), and its "
            "console script is `fastapi = fastapi.cli:main` "
            "(../fastapi/pyproject.toml:119-120). The standard oracle pins fastapi-cli "
            "0.0.32 (metadata.yaml:100-104). The separately packaged fastapi-cli implements "
            "project entrypoint discovery, so this is the pinned FastAPI optional CLI surface "
            "rather than core ASGI behavior. Starlette 1.6.0 owns generic ASGI and HTTP "
            "transport behavior for the selected probe."
        ),
    },
}
