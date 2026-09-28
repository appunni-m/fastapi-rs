"""Source-backed mapping for FastAPI's local documentation helper tests."""

from __future__ import annotations

from typing import Any

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole HTMLResponse and ASGI HTTP transport contract",
    },
}

__all__ = ["LOCAL_DOCS_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]

_RECIPE = "tests/fixtures/input-recipes/parity/local-docs-helpers-upstream.yaml"
_CASE = "fastapi.openapi.docs.local-docs-html-helpers"
_JSON_BODY = ["http.status", "http.body.bytes"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _function(
    name: str,
    start: int,
    end: int,
    action_ids: list[str],
    rationale: str,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "feature_ids": ["openapi-docs"],
        "observation_selectors": _JSON_BODY,
        "rationale": rationale,
        "replace_features": True,
        "supporting_sources": [
            _source(
                "tests/test_local_docs.py",
                start,
                end,
                f"pinned FastAPI 0.141.1 assertion function {name}",
            ),
            *sources,
        ],
        "workflow_cases": [
            {
                "recipe_path": _RECIPE,
                "case_id": _CASE,
                "action_ids": action_ids,
                "observation_selectors": _JSON_BODY,
            }
        ],
        "stimulus_notes": (
            f"The input-only ASGI helper workload reaches {', '.join(action_ids)}. "
            "It compares status and raw body bytes; recipes contain no expected HTML."
        ),
        "contract_gate": (
            "Partial: upstream assertions check selected strings in the helper's "
            "HTMLResponse body. The ASGI workflow compares the full body bytes but "
            "does not directly compare the helper return type or response headers."
        ),
    }


_SWAGGER = [
    _source(
        "fastapi/openapi/docs.py",
        40,
        196,
        "FastAPI generates Swagger UI HTML with the declared asset URLs and parameters",
    )
]
_REDOC = [
    _source(
        "fastapi/openapi/docs.py",
        197,
        299,
        "FastAPI generates ReDoc HTML with configurable asset URLs and Google Fonts",
    )
]

LOCAL_DOCS_TEST_REVIEW_MAPPINGS = {
    "tests/test_local_docs.py": {
        "feature_ids": ["openapi-docs"],
        "module_observation_selectors": _JSON_BODY,
        "rationale": "The tests call FastAPI's public Swagger UI and ReDoc HTML helpers with default and custom asset options.",
        "supporting_sources": [*_SWAGGER, *_REDOC],
        "functions": {
            "test_strings_in_generated_swagger": _function(
                "test_strings_in_generated_swagger",
                6,
                15,
                ["swagger-generated"],
                "Default Swagger JS, CSS, and favicon URLs are inputs from the pinned helper signature and should appear in the returned HTML.",
                _SWAGGER,
            ),
            "test_strings_in_custom_swagger": _function(
                "test_strings_in_custom_swagger",
                18,
                32,
                ["swagger-custom"],
                "Custom Swagger JS, CSS, and favicon URLs are forwarded into generated HTML.",
                _SWAGGER,
            ),
            "test_strings_in_generated_redoc": _function(
                "test_strings_in_generated_redoc",
                35,
                43,
                ["redoc-generated"],
                "Default ReDoc JS and favicon URLs are included in generated HTML.",
                _REDOC,
            ),
            "test_strings_in_custom_redoc": _function(
                "test_strings_in_custom_redoc",
                45,
                57,
                ["redoc-custom"],
                "Custom ReDoc JS and favicon URLs are forwarded into generated HTML.",
                _REDOC,
            ),
            "test_google_fonts_in_generated_redoc": _function(
                "test_google_fonts_in_generated_redoc",
                59,
                66,
                ["redoc-generated", "redoc-no-google-fonts"],
                "Default ReDoc HTML includes Google Fonts, and disabling the option removes that reference.",
                _REDOC,
            ),
        },
    }
}
