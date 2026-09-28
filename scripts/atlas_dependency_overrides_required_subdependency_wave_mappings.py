"""Source-reviewed mapping for nested required query parameters in overrides.

The recipe links independent HTTP stimuli to the selected FastAPI 0.141.1
source functions. It records no expected response values and makes no claim
about the unselected route-placement and parameter variants.
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
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI and HTTP transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned required-query-field validation dependency",
    },
}

_TEST_PATH = "tests/test_dependency_overrides.py"
_TEST_FILE = FASTAPI_ROOT / _TEST_PATH
_RECIPE = (
    "tests/fixtures/input-recipes/parity/dependency-overrides-required-subdependency-wave.yaml"
)
_WORKLOAD = "tests/fixtures/workloads/dependency_override_required_subdependency_wave.py"
_CASE = "fastapi.dependency-overrides.required-nested-query-parameter"
_ACTIONS = ["missing-k", "provide-k"]
_FEATURES = ["dependency-security", "request-validation"]
_SELECTORS = ["http.status", "http.body.bytes"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(name: str, role: str) -> dict[str, Any]:
    tree = ast.parse(_TEST_FILE.read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {name} in {_TEST_PATH}")
    node = matches[0]
    return _source(_TEST_PATH, node.lineno, node.end_lineno or node.lineno, role)


def _exclusion_group(names: tuple[str, ...], reason: str) -> dict[str, Any]:
    return {
        "test_functions": {
            name: _test_function_span(
                name,
                f"pinned FastAPI test function excluded from this focused nested-override wave: {name}",
            )
            for name in names
        },
        "reason": reason,
    }


_ROUTE_AND_ORIGINAL_DEPENDENCY = [
    _source(
        _TEST_PATH,
        10,
        16,
        "pinned test's original query-parameter dependency and the /main-depends/ route selected by the two source tests",
    ),
]
_REPLACEMENT_CHAIN = _source(
    _TEST_PATH,
    43,
    48,
    "pinned replacement graph: required query parameter k feeds the subdependency, then its value feeds the override",
)
_OVERRIDE_RESOLUTION = _source(
    "fastapi/dependencies/utils.py",
    623,
    639,
    "FastAPI selects a dependency override and rebuilds the dependant from the replacement callable's signature",
)
_REQUIRED_QUERY_VALIDATION = _source(
    "fastapi/dependencies/utils.py",
    492,
    505,
    "FastAPI infers an ordinary required scalar dependency parameter as a query field",
)
_QUERY_VALUE_VALIDATION = _source(
    "fastapi/dependencies/utils.py",
    852,
    866,
    "FastAPI validates extracted request query fields and collects missing-field errors",
)

_WORKFLOW_LINK = {
    "recipe_path": _RECIPE,
    "case_id": _CASE,
    "action_ids": _ACTIONS,
    "observation_selectors": _SELECTORS,
}

_BASELINE_EXCLUSIONS = _exclusion_group(
    (
        "test_main_depends",
        "test_main_depends_q_foo",
        "test_main_depends_q_foo_skip_100_limit_200",
        "test_decorator_depends",
        "test_decorator_depends_q_foo",
        "test_decorator_depends_q_foo_skip_100_limit_200",
        "test_router_depends",
        "test_router_depends_q_foo",
        "test_router_depends_q_foo_skip_100_limit_200",
        "test_router_decorator_depends",
        "test_router_decorator_depends_q_foo",
        "test_router_decorator_depends_q_foo_skip_100_limit_200",
        "test_override_simple",
    ),
    "These baseline dependency-parameter tests and the simple override do not exercise a replacement that adds a nested required query field; the simple override is linked to the existing dependency-resolution case.",
)
_EXCLUSIONS = [
    _BASELINE_EXCLUSIONS,
    _exclusion_group(
        ("test_override_with_sub__main_depends_q_foo",),
        "This is the related main-route negative case with the original q parameter present; this compact pair uses the no-query negative case and the k=bar success case to isolate the newly required field.",
    ),
    _exclusion_group(
        (
            "test_override_with_sub_decorator_depends",
            "test_override_with_sub_decorator_depends_q_foo",
            "test_override_with_sub_decorator_depends_k_bar",
        ),
        "These functions attach the dependency through route decorator metadata; the selected pair is limited to a parameter dependency whose replacement value is returned in the endpoint body.",
    ),
    _exclusion_group(
        (
            "test_override_with_sub_router_depends",
            "test_override_with_sub_router_depends_q_foo",
            "test_override_with_sub_router_depends_k_bar",
            "test_override_with_sub_router_decorator_depends",
            "test_override_with_sub_router_decorator_depends_q_foo",
            "test_override_with_sub_router_decorator_depends_k_bar",
        ),
        "These functions add APIRouter or router-decorator dependency placement; router composition is a separate configuration axis outside the single main-app route pair.",
    ),
]

DEPENDENCY_OVERRIDES_REQUIRED_SUBDEPENDENCY_WAVE_MAPPINGS = {
    _TEST_PATH: {
        "feature_ids": _FEATURES,
        "module_observation_selectors": _SELECTORS,
        "rationale": "A focused pair samples the nested replacement dependency's newly required query parameter: absent k produces a validation response, while k=bar reaches the original route with the replacement value.",
        "supporting_sources": [
            *_ROUTE_AND_ORIGINAL_DEPENDENCY,
            _REPLACEMENT_CHAIN,
            _OVERRIDE_RESOLUTION,
            _REQUIRED_QUERY_VALIDATION,
            _QUERY_VALUE_VALIDATION,
        ],
        "workflow_cases": [_WORKFLOW_LINK],
        "stimulus_notes": (
            f"Input-only case: {_RECIPE}::{_CASE} actions {', '.join(_ACTIONS)}. "
            f"The independent workload is {_WORKLOAD}; the recipe stores no expected outputs."
        ),
        "source_review_scope_exclusions": _EXCLUSIONS,
        "functions": {
            "test_override_with_sub_main_depends": {
                "feature_ids": _FEATURES,
                "observation_selectors": _SELECTORS,
                "rationale": "With the replacement dependency's nested required k parameter absent, FastAPI returns the request-validation response on /main-depends/.",
                "replace_features": True,
                "contract_gate": "Partial: the source test asserts status and parsed JSON while this workflow also compares raw body bytes; the selected pair covers one app-level route and one value, with query-field semantics supplied by pinned Pydantic and generic ASGI transport supplied by Starlette 1.6.0.",
                "workflow_cases": [_WORKFLOW_LINK],
                "supporting_sources": [
                    _test_function_span(
                        "test_override_with_sub_main_depends",
                        "pinned FastAPI test function and its missing-required-k response assertion",
                    ),
                    *_ROUTE_AND_ORIGINAL_DEPENDENCY,
                    _REPLACEMENT_CHAIN,
                    _OVERRIDE_RESOLUTION,
                    _REQUIRED_QUERY_VALIDATION,
                    _QUERY_VALUE_VALIDATION,
                ],
            },
            "test_override_with_sub_main_depends_k_bar": {
                "feature_ids": _FEATURES,
                "observation_selectors": _SELECTORS,
                "rationale": "Supplying k=bar satisfies the nested replacement dependency and the main route returns the replacement value.",
                "replace_features": True,
                "contract_gate": "Partial: the source test asserts status and parsed JSON while this workflow also compares raw body bytes; the selected pair covers one app-level route and one value, with query-field semantics supplied by pinned Pydantic and generic ASGI transport supplied by Starlette 1.6.0.",
                "workflow_cases": [_WORKFLOW_LINK],
                "supporting_sources": [
                    _test_function_span(
                        "test_override_with_sub_main_depends_k_bar",
                        "pinned FastAPI test function and its k=bar success assertion",
                    ),
                    *_ROUTE_AND_ORIGINAL_DEPENDENCY,
                    _REPLACEMENT_CHAIN,
                    _OVERRIDE_RESOLUTION,
                    _REQUIRED_QUERY_VALIDATION,
                    _QUERY_VALUE_VALIDATION,
                ],
            },
        },
    }
}

__all__ = [
    "DEPENDENCY_OVERRIDES_REQUIRED_SUBDEPENDENCY_WAVE_MAPPINGS",
    "SOURCE_IDENTITIES",
]
