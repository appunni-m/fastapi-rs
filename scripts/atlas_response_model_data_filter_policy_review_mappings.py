"""Source review for combined response-model null and unset filtering.

The workflow is an independently authored input-only case linked to a pinned
FastAPI test. It does not store the asserted response value or claim parity.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "source oracle and development-time source only; never a target runtime dependency",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole owner of generic HTTP response rendering and ASGI transport",
    },
    "starlette-rs": {
        "commit": "d54271705ec898a1160b0bc37036c1c8d1646cc5",
        "role": "target under review",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "model validation and response serialization called by FastAPI",
    },
}

RECIPE_PATH = (
    "tests/fixtures/input-recipes/parity/response-model-data-filter-exclude-unset-none-review.yaml"
)
CASE_ID = "fastapi.response-model-data-filter.exclude-unset-none"
ACTION_ID = "apply-combined-unset-and-null-filter"
SELECTORS = ("http.status", "http.body.bytes")

__all__ = ["RESPONSE_MODEL_DATA_FILTER_POLICY_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(test_path: str, function_name: str) -> dict[str, Any]:
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
        f"pinned FastAPI 0.141.1 test function {function_name} and its response assertion",
    )


def _workflow_link() -> dict[str, Any]:
    return {
        "recipe_path": RECIPE_PATH,
        "case_id": CASE_ID,
        "action_ids": [ACTION_ID],
        "observation_selectors": list(SELECTORS),
    }


_FUNCTION = {
    "review_status": "reviewed_partial",
    "feature_ids": ["response-serialization"],
    "observation_selectors": list(SELECTORS),
    "rationale": (
        "The pinned case combines omission-by-unset and omission-by-None while retaining an "
        "explicitly set value equal to its model default. This extends the current subclass-field "
        "filter sample with response serialization policy behavior."
    ),
    "replace_features": True,
    "contract_gate": (
        "Partial: the source compares parsed JSON for one model response. The workflow observes "
        "status and exact body bytes, and does not claim iterable or other exclusion policies."
    ),
    "stimulus_notes": (
        "The recipe and workload provide one independent HTTP input and selected observations; "
        "they contain no expected response values or copied upstream test body."
    ),
    "workflow_cases": [_workflow_link()],
    "supporting_sources": [
        _test_function_span("tests/test_skip_defaults.py", "test_return_exclude_unset_none"),
        _source(
            "tests/test_skip_defaults.py",
            25,
            29,
            "The source model declares nullable and non-null defaulted response fields",
        ),
        _source(
            "tests/test_skip_defaults.py",
            60,
            67,
            "The source route enables both response exclusion flags and returns a set-null field plus a set default",
        ),
        _source(
            "fastapi/routing.py",
            301,
            338,
            "FastAPI validates response content and forwards include, exclude, unset, default, and null flags to serialization",
        ),
        _source(
            "fastapi/routing.py",
            961,
            1007,
            "FastAPI stores the response-model serialization policies on route state",
        ),
        _source(
            "fastapi/_compat/v2.py",
            190,
            213,
            "FastAPI's Pydantic adapter forwards unset and null flags to TypeAdapter serialization",
        ),
        _source(
            "starlette/responses.py",
            181,
            201,
            "Starlette 1.6.0 owns JSONResponse byte rendering after FastAPI serialization",
        ),
    ],
}

_MODULE_REVIEW = {
    "rationale": (
        "Function-level review for the combined unset and null response-model policy test, "
        "linked to one independently authored input-only ASGI workflow."
    ),
    "functions": {"test_return_exclude_unset_none": _FUNCTION},
    "workflow_cases": [_workflow_link()],
    "module_observation_selectors": list(SELECTORS),
    "supporting_sources": [
        _source(
            "fastapi/routing.py",
            301,
            338,
            "FastAPI response serialization applies the selected filter flags",
        ),
        _source(
            "starlette/responses.py",
            181,
            201,
            "Starlette 1.6.0 renders the final JSON response bytes",
        ),
    ],
    "stimulus_notes": (
        "Input-only workflow: "
        f"{RECIPE_PATH}::{CASE_ID}. FastAPI owns response-model filtering; "
        "Starlette 1.6.0 owns generic JSON response rendering and ASGI transport."
    ),
}

RESPONSE_MODEL_DATA_FILTER_POLICY_REVIEW_MAPPINGS = {
    "tests/test_skip_defaults.py": _MODULE_REVIEW,
}
