"""Source-backed mapping for built-in generic request and response types."""

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
        "role": "sole generic ASGI request and response transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "request and response validation/serialization for Python generic annotations",
    },
}

__all__ = ["BUILTIN_GENERIC_TYPE_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]

_RECIPE = "tests/fixtures/input-recipes/parity/typing-python39-upstream.yaml"
_CASE = "fastapi.test.test-typing-python39.builtin-generic-request-response-types"
_ACTIONS = ["list-type", "mapping-of-lists-type", "set-type", "variadic-tuple-type"]
_SELECTORS = ["http.status", "http.body.bytes"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


_TEST_SOURCE = _source(
    "tests/test_typing_python39.py",
    7,
    24,
    "pinned FastAPI test for list, mapping-of-lists, set, and variadic tuple annotations",
)
_FASTAPI_SOURCES = [
    _source(
        "fastapi/dependencies/utils.py",
        271,
        301,
        "FastAPI inspects typed endpoint signatures and builds request dependency fields",
    ),
    _source(
        "fastapi/routing.py",
        301,
        341,
        "FastAPI validates and serializes response fields before emitting JSON responses",
    ),
]

BUILTIN_GENERIC_TYPE_TEST_REVIEW_MAPPINGS = {
    "tests/test_typing_python39.py": {
        "feature_ids": ["request-validation", "response-serialization"],
        "module_observation_selectors": _SELECTORS,
        "rationale": "The test exercises built-in generic request annotations and response-model serialization on Python 3.10 and later.",
        "supporting_sources": [_TEST_SOURCE, *_FASTAPI_SOURCES],
        "functions": {
            "test_typing": {
                "feature_ids": ["request-validation", "response-serialization"],
                "observation_selectors": _SELECTORS,
                "rationale": "Four independent requests cover list[int], dict[str, list[int]], set[int], and tuple[int, ...] request and response annotations.",
                "replace_features": True,
                "supporting_sources": [
                    _TEST_SOURCE,
                    *_FASTAPI_SOURCES,
                    _source(
                        "tests/utils.py",
                        6,
                        8,
                        "FastAPI marks this source test as requiring Python 3.10 or later",
                    ),
                ],
                "workflow_cases": [
                    {
                        "recipe_path": _RECIPE,
                        "case_id": _CASE,
                        "action_ids": _ACTIONS,
                        "observation_selectors": _SELECTORS,
                    }
                ],
                "stimulus_notes": (
                    "The input-only recipe sends one JSON body for each built-in generic type. "
                    "The recipe compares status and response bytes and contains no expected outputs."
                ),
                "contract_gate": (
                    "Partial: the source test is guarded by needs_py310 and is skipped before "
                    "Python 3.10; the project baseline starts at 3.10. Runtime annotation "
                    "inspection and Pydantic 2.13.4 serialization details remain dependency-level contracts."
                ),
            }
        },
    }
}
