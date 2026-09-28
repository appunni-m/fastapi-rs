"""Source-reviewed mappings for nested FastAPI dependency-cache semantics."""

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
        "role": "sole generic ASGI and HTTP response transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "not used to cache dependency values or validate a response model in these scalar-counter cases",
    },
}

_TEST = "tests/test_dependency_cache.py"
_RECIPE = "tests/fixtures/input-recipes/parity/dependency-cache-source-wave.yaml"
_WORKLOAD = "tests/fixtures/workloads/dependency_cache_source_wave.py"
_HTTP = ["http.status", "http.body.bytes"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / _TEST).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {name} in {_TEST}")
    node = matches[0]
    return _source(
        _TEST,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 public HTTP test function {name}",
    )


_CACHE_ROUTE_DEFINITIONS = _source(
    _TEST,
    9,
    35,
    "upstream counter dependency, parent dependency, and both nested-cache route definitions",
)
_CACHE_SOLVER = _source(
    "fastapi/dependencies/utils.py",
    640,
    680,
    "FastAPI recursively solves each dependency, consults the request-local cache only when use_cache is true, and stores a resolved value only when the key is absent",
)
_CACHE_KEY = _source(
    "fastapi/dependencies/models.py",
    82,
    96,
    "FastAPI keys dependency results by callable and applicable security and cleanup scopes",
)
_REQUEST_CACHE_LIFETIME = _source(
    "fastapi/routing.py",
    481,
    488,
    "FastAPI starts dependency solving for each request without passing a previous request's cache",
)
_REQUEST_CACHE_INIT = _source(
    "fastapi/dependencies/utils.py",
    615,
    616,
    "FastAPI allocates a new dependency-cache dictionary when the route does not supply one",
)
_FASTAPI_JSON_ENCODING = _source(
    "fastapi/routing.py",
    340,
    342,
    "FastAPI uses jsonable_encoder when no response model field is selected",
)
_STARLETTE_JSON_RESPONSE = _source(
    "starlette/responses.py",
    181,
    201,
    "Starlette 1.6.0 JSONResponse serializes the already-resolved endpoint dictionary to response bytes",
)


def _workflow(
    case_id: str,
    action_ids: list[str],
    observation_selectors: list[str],
    recipe_path: str = _RECIPE,
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": action_ids,
        "observation_selectors": observation_selectors,
    }


_EXISTING_REUSE = _workflow(
    "fastapi.dependencies.cache-reuse",
    ["first-request", "next-request"],
    ["http.status", "http.body.json"],
    "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
)
_EXISTING_BYPASS = _workflow(
    "fastapi.dependencies.cache-bypass",
    ["first-request", "next-request"],
    ["http.status", "http.body.json"],
    "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml",
)


def _review_function(
    name: str,
    case_id: str,
    rationale: str,
    existing_case: dict[str, Any],
) -> dict[str, Any]:
    return {
        "feature_ids": ["dependency-security"],
        "observation_selectors": _HTTP,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": (
            "Partial: the new independent workload preserves the source dependency-graph shape and two-request counter observations, but uses fresh callable names and paths. The source parses JSON while the ASGI workflow compares response bytes, which also samples FastAPI's jsonable_encoder and Starlette 1.6.0 JSONResponse/transport behavior. Pydantic does not validate dependency results or a response model in these cases."
        ),
        "workflow_cases": [
            existing_case,
            _workflow(
                case_id,
                ["first-request", "next-request"],
                _HTTP,
            ),
        ],
        "stimulus_notes": (
            f"Use {_RECIPE} case {case_id}, with two direct ASGI requests to the same route. "
            f"The independent workload is {_WORKLOAD}; the recipe contains no expected outputs."
        ),
        "supporting_sources": [
            _test_function_span(name),
            _CACHE_ROUTE_DEFINITIONS,
            _CACHE_SOLVER,
            _CACHE_KEY,
            _REQUEST_CACHE_LIFETIME,
            _REQUEST_CACHE_INIT,
            _FASTAPI_JSON_ENCODING,
            _STARLETTE_JSON_RESPONSE,
        ],
    }


DEPENDENCY_CACHE_SOURCE_WAVE_MAPPINGS = {
    _TEST: {
        "functions": {
            "test_sub_counter": _review_function(
                "test_sub_counter",
                "fastapi.dependencies.cache-shared-subdependency-source-wave",
                "A common FastAPI dependency result is reused when reached once through a parent dependency and once as a direct endpoint dependency; a later HTTP request resolves it afresh.",
                _EXISTING_REUSE,
            ),
            "test_sub_counter_no_cache": _review_function(
                "test_sub_counter_no_cache",
                "fastapi.dependencies.cache-bypass-subdependency-source-wave",
                "A direct use_cache=False edge re-evaluates a dependency after the nested parent edge has resolved it, while the cached parent result remains available for the endpoint's other value; the same behavior repeats on the next request.",
                _EXISTING_BYPASS,
            ),
        }
    }
}

__all__ = [
    "DEPENDENCY_CACHE_SOURCE_WAVE_MAPPINGS",
    "SOURCE_IDENTITIES",
]
