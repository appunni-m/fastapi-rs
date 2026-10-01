"""Source-reviewed mappings for FastAPI's dependency tutorial tests.

The mappings are static atlas inputs. Workflow cases use independently authored
stimuli and contain no expected results or parity claims.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT.parent / "fastapi"

SOURCE_IDENTITY = {
    "fastapi_version": "0.141.1",
    "fastapi_commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "starlette_version": "1.6.0",
    "starlette_commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}

_HTTP = ["http.body.bytes", "http.status"]
_OPENAPI = ["docs.response.status", "http.status", "openapi.document", "openapi.paths"]
_ERROR_CLASS = ["validation.error_class"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
    path = FASTAPI_ROOT / test_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
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
        f"pinned FastAPI 0.141.1 test function {function_name}",
    )


def _link(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _review(
    test_path: str,
    function_name: str,
    feature_ids: list[str],
    rationale: str,
    contract_gate: str,
    links: list[dict[str, Any]],
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    selectors = sorted({selector for link in links for selector in link["observation_selectors"]})
    links_note = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} actions "
        f"{', '.join(link['action_ids'])} ({', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + contract_gate,
        "workflow_cases": links,
        "stimulus_notes": (
            "Input-only case links: "
            + links_note
            + ". The workflow inputs contain no expected outputs."
        ),
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _module(rationale: str, functions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    links: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for review in functions.values():
        for link in review["workflow_cases"]:
            key = (link["recipe_path"], link["case_id"], tuple(link["action_ids"]))
            links.setdefault(key, link)
        for source in review["supporting_sources"]:
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources.setdefault(key, source)
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
        "functions": functions,
        "workflow_cases": list(links.values()),
        "supporting_sources": list(sources.values()),
        "module_observation_selectors": sorted(
            {
                selector
                for review in functions.values()
                for selector in review["observation_selectors"]
            }
        ),
    }


_SOLVER = _source(
    "fastapi/dependencies/utils.py",
    619,
    705,
    "FastAPI recursively resolves dependency callables and extracts request parameters",
)
_REQUEST_PARAMS = _source(
    "fastapi/dependencies/utils.py",
    780,
    849,
    "FastAPI extracts and validates path, query, header, and cookie parameters",
)
_YIELD_DEPENDENCY = _source(
    "fastapi/dependencies/utils.py",
    566,
    574,
    "FastAPI enters generator dependencies as context managers on an exit stack",
)
_ROUTE_STACKS = _source(
    "fastapi/routing.py",
    134,
    158,
    "FastAPI owns request/function exit-stack lifetime and reports swallowed dependency exceptions",
)
_ROUTE_SOLVE = _source(
    "fastapi/routing.py",
    475,
    490,
    "FastAPI invokes dependency solving before calling the endpoint",
)
_VALIDATION_RAISE = _source(
    "fastapi/routing.py",
    751,
    755,
    "FastAPI raises RequestValidationError when dependency and field resolution yields errors",
)
_OPENAPI_PARAMS = _source(
    "fastapi/openapi/utils.py",
    331,
    385,
    "FastAPI emits flattened dependency parameters and request-body metadata in OpenAPI",
)
_OPENAPI_RESPONSES = _source(
    "fastapi/openapi/utils.py",
    403,
    472,
    "FastAPI emits operation response and validation-error schema references",
)
_FASTAPI_SWALLOWED_YIELD = _source(
    "fastapi/routing.py",
    140,
    158,
    "FastAPI detects a response suppressed by a yield dependency that does not re-raise",
)
_STARLETTE_CLIENT_ERROR = _source(
    "starlette/testclient.py",
    207,
    220,
    "Starlette 1.6.0 TestClient stores its raise_server_exceptions policy",
)
_STARLETTE_CLIENT_RAISE = _source(
    "starlette/testclient.py",
    348,
    362,
    "Starlette 1.6.0 TestClient re-raises app exceptions or materializes a 500 response",
)

_DEPENDENCY_WAVE = "tests/fixtures/input-recipes/parity/dependency-wave.yaml"
_TUTORIAL_REVIEW = "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml"
_QUERY_COOKIE = (
    "tests/fixtures/input-recipes/parity/dependency-tutorial005-query-cookie-fallback.yaml"
)
_ADVANCED = "tests/fixtures/input-recipes/parity/advanced_dependencies.yaml"
_YIELD_ERRORS = (
    "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml"
)
_YIELD_TUTORIALS = "tests/fixtures/input-recipes/parity/dependency-yield-tutorials-upstream.yaml"
_GLOBAL_DEFAULT = "tests/fixtures/input-recipes/parity/dependency-tutorial012-default-upstream.yaml"
_GLOBAL_ANNOTATED = (
    "tests/fixtures/input-recipes/parity/dependency-tutorial012-annotated-upstream.yaml"
)


DEPENDENCY_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_tutorial/test_dependencies/test_tutorial001_tutorial001_02.py": _module(
        "The parametrized test exercises a reusable query dependency through two routes and three annotation examples; its separate OpenAPI test asserts a complete snapshot.",
        {
            "test_get": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial001_tutorial001_02.py",
                "test_get",
                ["dependency-security", "response-serialization"],
                "A shared function dependency resolves optional query data and integer pagination values into two route results.",
                "The source runs five request shapes against three documentation examples. The links sample default and query conversion plus one full override on independently named routes; exact route paths, values, annotation variants, all combinations, and TestClient JSON decoding are not claimed.",
                [
                    _link(
                        _DEPENDENCY_WAVE,
                        "fastapi.dependency-wave.dependency-basics.test-get",
                        ["dispatch"],
                        _HTTP,
                    ),
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.basic-defaults",
                        ["omit-query-values"],
                        _HTTP,
                    ),
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.basic-partial-query",
                        ["set-query-and-use-numeric-defaults"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial001_py310.py",
                        6,
                        17,
                        "shared query dependency and its two route uses",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial001_tutorial001_02.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The source compares path operations, optional query parameter schemas/defaults, and the shared validation response schema.",
                "The case observes selected parameter and 422-schema pointers on separate /library and /members routes, not the entire source snapshot or the three source app variants.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.openapi-projection",
                        ["inspect-dependency-parameter-schema"],
                        _OPENAPI,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial001_py310.py",
                        1,
                        17,
                        "documented routes represented by the source OpenAPI snapshot",
                    ),
                    _OPENAPI_PARAMS,
                    _OPENAPI_RESPONSES,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial002_tutorial003_tutorial004.py": _module(
        "The parametrized function covers class dependencies declared explicitly, untyped, and by inferred Depends(), with query echo and pagination; the separate function asserts a full OpenAPI snapshot.",
        {
            "test_get": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial002_tutorial003_tutorial004.py",
                "test_get",
                ["dependency-security", "response-serialization"],
                "A callable class dependency exposes query parameters that feed a paginated route result.",
                "The source runs six query combinations across three annotation examples. Existing and new cases sample the dependency declaration forms, defaults, and one combined query window; exact source item data, every query order/composition, routes, and parsed JSON assertions remain gated.",
                [
                    _link(
                        _DEPENDENCY_WAVE,
                        "fastapi.dependency-wave.dependency-filter-chain.test-get",
                        ["dispatch"],
                        _HTTP,
                    ),
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.catalog-default-window",
                        [
                            "explicit-class-dependency",
                            "untyped-class-dependency",
                            "inferred-class-dependency",
                        ],
                        _HTTP,
                    ),
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.catalog-custom-window",
                        [
                            "explicit-class-query-window",
                            "untyped-class-query-window",
                            "inferred-class-query-window",
                        ],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial002_py310.py",
                        9,
                        23,
                        "explicit class-based query dependency and paginated response",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial003_py310.py",
                        9,
                        23,
                        "untyped class dependency and paginated response",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial004_py310.py",
                        9,
                        23,
                        "inferred class dependency and paginated response",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial002_tutorial003_tutorial004.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The source compares query parameters, operation responses, and the validation schema for the dependency route.",
                "Only selected parameter and validation-schema pointers for independent catalog routes are observed; the complete /items/ snapshot and all three source app variants are not covered.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.openapi-projection",
                        ["inspect-dependency-parameter-schema"],
                        _OPENAPI,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial002_py310.py",
                        1,
                        23,
                        "documented class dependency route represented by OpenAPI",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial003_py310.py",
                        1,
                        23,
                        "documented untyped dependency route represented by OpenAPI",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial004_py310.py",
                        1,
                        23,
                        "documented inferred dependency route represented by OpenAPI",
                    ),
                    _OPENAPI_PARAMS,
                    _OPENAPI_RESPONSES,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial005.py": _module(
        "The module checks query-over-cookie fallback for three input combinations and snapshots the query/cookie OpenAPI parameter declarations.",
        {
            "test_get": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial005.py",
                "test_get",
                ["dependency-security", "request-validation", "response-serialization"],
                "Nested query and cookie dependencies select the query value when supplied and otherwise use the cookie or optional default.",
                "All three source input combinations have corresponding independent cases. The cases preserve the same parameter names and precedence but use an independently authored dependency graph and values; exact application objects and TestClient JSON parsing are not asserted.",
                [
                    _link(
                        _QUERY_COOKIE,
                        "fastapi.dependencies.tutorial005.query-cookie.fallback",
                        ["use-cookie-when-query-is-absent"],
                        _HTTP,
                    ),
                    _link(
                        _QUERY_COOKIE,
                        "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
                        ["prefer-query-over-cookie"],
                        _HTTP,
                    ),
                    _link(
                        _QUERY_COOKIE,
                        "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
                        ["use-null-when-query-and-cookie-are-absent"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial005_py310.py",
                        6,
                        20,
                        "query extraction, cookie fallback, and route dependency graph",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial005.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The source snapshot includes the query and cookie parameter declarations plus generated validation schemas.",
                "The workflow selects two parameter objects for an independently authored route. It does not compare the full /items/ document, all components, or the exact operation metadata.",
                [
                    _link(
                        _QUERY_COOKIE,
                        "fastapi.dependencies.tutorial005.query-cookie.openapi-parameters",
                        ["inspect-query-and-cookie-parameter-definitions"],
                        _OPENAPI,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial005_py310.py",
                        1,
                        20,
                        "documented query/cookie dependency route in the snapshot",
                    ),
                    _OPENAPI_PARAMS,
                    _OPENAPI_RESPONSES,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial006.py": _module(
        "The module checks missing, invalid-first, invalid-second, and valid required-header dependency behavior in default and Annotated example forms, then snapshots OpenAPI.",
        {
            "test_get_no_headers": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial006.py",
                "test_get_no_headers",
                ["dependency-security", "request-validation"],
                "Missing required headers through endpoint dependencies produce a validation response.",
                "The new input omits both independent vault headers and records status/body; its aliases and error representation differ from the source's exact X-Token/X-Key Pydantic error list.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.headers-missing",
                        ["omit-both-required-headers"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial006_py310.py",
                        6,
                        19,
                        "required header dependencies and protected route",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                    _VALIDATION_RAISE,
                ),
            ),
            "test_get_invalid_one_header": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial006.py",
                "test_get_invalid_one_header",
                ["dependency-security", "public-api-errors"],
                "The first header dependency raises an HTTP error when its supplied value is invalid.",
                "The independent vault route supplies only an invalid access token; header alias, detail text, and exact JSON body differ from the source, while the 400 response path is sampled.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.headers-invalid-token",
                        ["reject-first-header"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial006_py310.py",
                        6,
                        9,
                        "first header verifier and its invalid-value branch",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_get_invalid_second_header": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial006.py",
                "test_get_invalid_second_header",
                ["dependency-security", "public-api-errors"],
                "After the first header passes, the second header dependency rejects its invalid value.",
                "The new case sends a valid independent first header and an invalid second header. Aliases, values, detail text, and exact JSON body differ from the tutorial assertion.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.headers-invalid-key",
                        ["reject-second-header"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial006_py310.py",
                        11,
                        14,
                        "second header verifier and invalid-value branch",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_get_valid_headers": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial006.py",
                "test_get_valid_headers",
                ["dependency-security", "response-serialization"],
                "Both required header dependencies resolve before the route returns its item list.",
                "The existing case exercises the route-level dependency list with different header values and response records. It samples successful dependency sequencing; exact source JSON content and the two module annotation variants are not claimed.",
                [
                    _link(
                        _DEPENDENCY_WAVE,
                        "fastapi.dependency-wave.dependency-header-guards.test-get-valid-headers",
                        ["dispatch"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial006_py310.py",
                        6,
                        19,
                        "header guards and successful route output",
                    ),
                    _SOLVER,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial006.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The source snapshot records required header parameters and the default validation response schema.",
                "Selected header-parameter and validation-schema pointers are observed for an independent vault route, not the exact /items/ document or default/Annotated examples.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.openapi-projection",
                        ["inspect-dependency-parameter-schema"],
                        _OPENAPI,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial006_py310.py",
                        1,
                        19,
                        "documented header dependencies and route represented by OpenAPI",
                    ),
                    _OPENAPI_PARAMS,
                    _OPENAPI_RESPONSES,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008.py": _module(
        "A dynamically imported chain of three yield dependencies feeds one endpoint; mocks verify the leaf result, while the source contains an additional Python-version-specific Annotated variant.",
        {
            "test_get_db": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008.py",
                "test_get_db",
                ["dependency-security"],
                "A route resolves a three-level generator-dependency chain and returns its leaf value.",
                "The existing case exercises a separate nested yield chain and a post-request cleanup observation. It does not use the source's patched mocks or compare their object identity/string representation, and its Annotated example is marked xfail on Python versions before 3.14.",
                [
                    _link(
                        _YIELD_TUTORIALS,
                        "fastapi.dependencies.tutorial008.async-yield-chain-default",
                        ["chain-result"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008_py310.py",
                        4,
                        25,
                        "nested generator dependencies and reverse cleanup",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                    _SOLVER,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008b.py": _module(
        "The module tests a yield dependency that translates ownership failures, missing-item errors, and successful lookup through a route dependency.",
        {
            "test_get_no_item": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008b.py",
                "test_get_no_item",
                ["dependency-security", "public-api-errors"],
                "A missing dependent item raises an HTTP 404 response.",
                "The added independent asset case uses another route and detail value; it samples the route-through-yield-dependency error path but not the exact item identifier or parsed JSON body.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.ownership-not-found",
                        ["request-unknown-asset"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008b_py310.py",
                        16,
                        30,
                        "yielding user dependency, item lookup, and not-found branch",
                    ),
                    _YIELD_DEPENDENCY,
                    _SOLVER,
                ),
            ),
            "test_owner_error": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008b.py",
                "test_owner_error",
                ["dependency-security", "public-api-errors"],
                "An endpoint ownership exception is thrown into the yield dependency and translated to an HTTP error.",
                "The new case samples a different owner exception and resource. It uses status 400 and dependency translation but does not assert the source OwnerError name, owner value, detail string, or decoded body.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.ownership-denied",
                        ["request-other-owners-asset"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008b_py310.py",
                        12,
                        30,
                        "OwnerError handling in a yielding dependency and endpoint",
                    ),
                    _YIELD_DEPENDENCY,
                    _SOLVER,
                    _ROUTE_STACKS,
                ),
            ),
            "test_get_item": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008b.py",
                "test_get_item",
                ["dependency-security", "response-serialization"],
                "A valid ownership check returns the item resolved through the dependency graph.",
                "The existing case returns an independently authored record for a different ID and values; it samples successful dependent lookup but not the exact response object or TestClient JSON decoding.",
                [
                    _link(
                        _DEPENDENCY_WAVE,
                        "fastapi.dependency-wave.dependency-item-chain.test-get-item",
                        ["dispatch"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008b_py310.py",
                        16,
                        30,
                        "yield dependency and successful item lookup branch",
                    ),
                    _YIELD_DEPENDENCY,
                    _SOLVER,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008c.py": _module(
        "The module covers ordinary yield-dependency responses, swallowed endpoint exceptions, FastAPI's swallowed-response error, and TestClient's non-raising 500 mode.",
        {
            "test_get_no_item": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008c.py",
                "test_get_no_item",
                ["dependency-security", "public-api-errors"],
                "The route returns its HTTPException response while a yield dependency is active.",
                "The existing case uses a corresponding missing-item action with a separate route. Status/body bytes are observed; TestClient JSON decoding and the exact source path are not.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008c.suppressed-yield-exception",
                        ["not-found"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008c_py310.py",
                        10,
                        27,
                        "yield dependency and item route error branches",
                    ),
                    _YIELD_DEPENDENCY,
                    _SOLVER,
                ),
            ),
            "test_get": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008c.py",
                "test_get",
                ["dependency-security", "response-serialization"],
                "The successful route returns a string value after dependency setup.",
                "The existing action returns the same result shape on an independently named route; it does not cover stdout emitted during dependency cleanup.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008c.suppressed-yield-exception",
                        ["ordinary-result"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008c_py310.py",
                        10,
                        27,
                        "yield dependency and successful endpoint branch",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                ),
            ),
            "test_fastapi_error": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008c.py",
                "test_fastapi_error",
                ["dependency-security", "asgi-error-propagation"],
                "A yield dependency that suppresses an endpoint exception causes FastAPIError.",
                "The two existing actions observe the escaping exception class but not the source's required message substring or TestClient.raises boundary. The default and Annotated source modules are separate pytest fixture variants.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008c.suppressed-yield-exception",
                        ["suppressed-default", "suppressed-annotated"],
                        _ERROR_CLASS,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008c_py310.py",
                        10,
                        15,
                        "yield dependency catches without re-raising",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial008c_an_py310.py",
                        10,
                        15,
                        "Annotated yield dependency catches without re-raising",
                    ),
                    _FASTAPI_SWALLOWED_YIELD,
                    _STARLETTE_CLIENT_ERROR,
                    _STARLETTE_CLIENT_RAISE,
                ),
            ),
            "test_internal_server_error": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008c.py",
                "test_internal_server_error",
                ["dependency-security", "asgi-error-propagation"],
                "With TestClient re-raising disabled, a suppressed dependency exception is surfaced as an HTTP 500 response.",
                "The existing actions observe the ASGI status/body for independent default and Annotated routes. The workflow does not instantiate Starlette TestClient or select raise_server_exceptions=False; its client-specific conversion policy remains gated.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008c.suppressed-yield-exception",
                        ["suppressed-default", "suppressed-annotated"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008c_py310.py",
                        10,
                        15,
                        "yield dependency suppression branch",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial008c_an_py310.py",
                        10,
                        15,
                        "Annotated yield dependency suppression branch",
                    ),
                    _FASTAPI_SWALLOWED_YIELD,
                    _STARLETTE_CLIENT_ERROR,
                    _STARLETTE_CLIENT_RAISE,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008d.py": _module(
        "The module covers ordinary yield-dependency responses, exception re-raising, exception class/arguments, and TestClient's non-raising 500 mode.",
        {
            "test_get_no_item": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008d.py",
                "test_get_no_item",
                ["dependency-security", "public-api-errors"],
                "The route returns its HTTPException response while the dependency later handles another exception type.",
                "The workflow samples a separate missing-item route and output. Exact source route and parsed JSON value remain gated.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008d.reraised-yield-exception",
                        ["not-found"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008d_py310.py",
                        10,
                        28,
                        "re-raising yield dependency and item route error branches",
                    ),
                    _YIELD_DEPENDENCY,
                    _SOLVER,
                ),
            ),
            "test_get": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008d.py",
                "test_get",
                ["dependency-security", "response-serialization"],
                "The successful route returns a string result after dependency setup.",
                "The independent ordinary-result action samples the response path but not the source's printed cleanup message.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008d.reraised-yield-exception",
                        ["ordinary-result"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008d_py310.py",
                        10,
                        28,
                        "re-raising dependency and successful route branch",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                ),
            ),
            "test_internal_error": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008d.py",
                "test_internal_error",
                ["dependency-security", "asgi-error-propagation"],
                "A dependency that re-raises preserves the endpoint's InternalError for the caller.",
                "The actions observe the escaping error class but not the source's exception args or the TestClient.raises boundary. Starlette owns client-side exception re-raising.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008d.reraised-yield-exception",
                        ["reraised-default", "reraised-annotated"],
                        _ERROR_CLASS,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008d_py310.py",
                        6,
                        23,
                        "yield dependency catches then re-raises endpoint exception",
                    ),
                    _source(
                        "docs_src/dependencies/tutorial008d_an_py310.py",
                        6,
                        23,
                        "Annotated yield dependency catches then re-raises",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                    _STARLETTE_CLIENT_ERROR,
                    _STARLETTE_CLIENT_RAISE,
                ),
            ),
            "test_internal_server_error": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008d.py",
                "test_internal_server_error",
                ["dependency-security", "asgi-error-propagation"],
                "With TestClient re-raising disabled, the uncaught dependency exception is represented as an HTTP 500 response.",
                "The workflow observes an independent ASGI 500 response but does not exercise TestClient's raise_server_exceptions=False policy or its generic server-error body behavior.",
                [
                    _link(
                        _YIELD_ERRORS,
                        "fastapi.dependencies.tutorial008d.reraised-yield-exception",
                        ["reraised-default", "reraised-annotated"],
                        _HTTP,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008d_py310.py",
                        10,
                        28,
                        "re-raising dependency and endpoint exception",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                    _STARLETTE_CLIENT_RAISE,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008e.py": _module(
        "The module parametrizes the two documented function-scoped yield-dependency signatures and asserts only the current-user response.",
        {
            "test_get_users_me": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial008e.py",
                "test_get_users_me",
                ["dependency-security", "response-serialization"],
                "Both parameterized source apps yield the literal current-user value Rick from a dependency declared with function scope, and the test asserts HTTP 200 plus the JSON value Rick.",
                "The independent workflow gives each syntax variant its own status/body response case and adds a separate follow-up request to observe cleanup; the upstream test does not assert cleanup timing, stdout, or print order.",
                [
                    _link(
                        _YIELD_TUTORIALS,
                        "fastapi.dependencies.tutorial008e.function-scope-yield-rick",
                        ["rick-response"],
                        _HTTP,
                    ),
                    _link(
                        _YIELD_TUTORIALS,
                        "fastapi.dependencies.tutorial008e.annotated-function-scope-yield-rick",
                        ["rick-response"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial008e_py310.py",
                        6,
                        15,
                        "yield dependency declared with function lifetime and user route",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                    _SOLVER,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial010.py": _module(
        "The test creates an app around the documented context-manager yield dependency and patches its DBSession constructor.",
        {
            "test_get_db": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial010.py",
                "test_get_db",
                ["dependency-security"],
                "A context manager entered by a generator dependency supplies a value to an HTTP route.",
                "The independent workflows sample a yielding resource response and context-manager entry/cleanup on separate requests. They do not patch a module-global DBSession or observe the Mock identity/string value asserted by the source.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/dependency-wave.yaml",
                        "fastapi.dependency-wave.dependency-yield-resource.test-get-db",
                        ["dispatch"],
                        ["http.status", "http.body.bytes"],
                    ),
                    _link(
                        _YIELD_TUTORIALS,
                        "fastapi.dependencies.tutorial010.context-manager-in-yield-dependency",
                        ["database-result"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial010_py310.py",
                        1,
                        14,
                        "context manager wrapped by a yield dependency",
                    ),
                    _YIELD_DEPENDENCY,
                    _ROUTE_STACKS,
                    _SOLVER,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial011.py": _module(
        "The module tests a callable dependency object with absent, nonmatching, and matching query values, followed by a complete OpenAPI snapshot.",
        {
            "test_get": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial011.py",
                "test_get",
                ["dependency-security", "response-serialization"],
                "A callable instance inspects a query parameter and returns a boolean result through a route.",
                "Existing cases cover matching and nonmatching values and the new case covers the absent-query default. Routes, search term, and response property names differ; source response JSON parsing remains a client assertion.",
                [
                    _link(
                        _ADVANCED,
                        "fastapi.docs.advanced-dependencies.matching-query",
                        ["matching-query"],
                        _HTTP,
                    ),
                    _link(
                        _ADVANCED,
                        "fastapi.docs.advanced-dependencies.nonmatching-query",
                        ["nonmatching-query"],
                        _HTTP,
                    ),
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.search-default",
                        ["use-empty-search-phrase"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial011_py310.py",
                        6,
                        21,
                        "parameterized checker instance and query route",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial011.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The snapshot includes the callable dependency's query parameter, default value, route response, and validation schema.",
                "Selected parameter and validation-schema pointers are observed for an independently named search route; the full /query-checker/ snapshot and exact operation metadata are not compared.",
                [
                    _link(
                        _TUTORIAL_REVIEW,
                        "fastapi.dependencies.tutorial-review.openapi-projection",
                        ["inspect-dependency-parameter-schema"],
                        _OPENAPI,
                    )
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial011_py310.py",
                        1,
                        21,
                        "documented callable dependency route represented by OpenAPI",
                    ),
                    _OPENAPI_PARAMS,
                    _OPENAPI_RESPONSES,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial012.py": _module(
        "The module applies two global header dependencies to two routes in both default and Annotated declaration forms; test functions check missing, invalid-first, invalid-second, and valid header cases plus OpenAPI snapshots.",
        {
            "test_get_no_headers_items": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_no_headers_items",
                ["dependency-security", "request-validation"],
                "Global required-header dependencies reject a request to the items route when both headers are absent.",
                "Both existing default and Annotated workflows exercise the items route. The source checks decoded Pydantic error objects; workflows compare response bytes and use independent value/profile identity.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["missing-items-headers"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["missing-items-headers"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        4,
                        20,
                        "default-form global dependencies and items route",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                    _VALIDATION_RAISE,
                ),
            ),
            "test_get_no_headers_users": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_no_headers_users",
                ["dependency-security", "request-validation"],
                "The shared required-header dependencies also reject requests to the users route when both headers are absent.",
                "Default and Annotated workflows include the users route with both headers absent. Exact body error decoding is Pydantic-owned and the source snapshot's error values are not independently claimed.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["missing-users-headers"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["missing-users-headers"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        4,
                        25,
                        "global header dependencies shared by users route",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                    _VALIDATION_RAISE,
                ),
            ),
            "test_get_invalid_one_header_items": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_invalid_one_header_items",
                ["dependency-security", "public-api-errors"],
                "The first global dependency rejects an invalid token on the items route.",
                "Both default and Annotated workflows sample this route and branch with a different invalid token value and compare raw bytes rather than source JSON parsing.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["invalid-token"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["invalid-token"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        4,
                        7,
                        "first global header dependency and invalid-token branch",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_get_invalid_one_users": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_invalid_one_users",
                ["dependency-security", "public-api-errors"],
                "The first global dependency rejects an invalid token on the users route.",
                "The linked actions trigger this dependency on the items route rather than the source users route; the second route's repeated branch and its decoded error body remain gated.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["invalid-token"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["invalid-token"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        4,
                        7,
                        "first global header dependency shared by both routes",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_get_invalid_second_header_items": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_invalid_second_header_items",
                ["dependency-security", "public-api-errors"],
                "After the token dependency succeeds, the second global dependency rejects an invalid key on the items route.",
                "Both default and Annotated workflows sample this branch using independent credentials and error content; the source's exact HTTPException JSON detail is not claimed.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["invalid-key"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["invalid-key"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        9,
                        12,
                        "second global header dependency and invalid-key branch",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_get_invalid_second_header_users": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_invalid_second_header_users",
                ["dependency-security", "public-api-errors"],
                "The second global dependency rejects an invalid key on the users route after the token check passes.",
                "The workflows exercise the same shared dependency branch on /items/ instead of the source /users/ route; the repeated route behavior and decoded message remain gated.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["invalid-key"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["invalid-key"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        9,
                        12,
                        "second global header dependency shared by both routes",
                    ),
                    _SOLVER,
                    _REQUEST_PARAMS,
                ),
            ),
            "test_get_valid_headers_items": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_valid_headers_items",
                ["dependency-security", "response-serialization"],
                "Both global header dependencies pass and the items route returns its collection.",
                "Default and Annotated workflows exercise the source route with independent accepted values/data; only status and raw body bytes are compared.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["valid-items"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["valid-items"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        4,
                        20,
                        "global header checks and items route",
                    ),
                    _SOLVER,
                ),
            ),
            "test_get_valid_headers_users": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_get_valid_headers_users",
                ["dependency-security", "response-serialization"],
                "Both global header dependencies pass and the users route returns its collection.",
                "Default and Annotated workflows exercise the source users route with independent accepted values/data; only status and raw body bytes are compared.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["valid-users"],
                        _HTTP,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["valid-users"],
                        _HTTP,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        4,
                        25,
                        "global header checks and both protected routes",
                    ),
                    _SOLVER,
                ),
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_dependencies/test_tutorial012.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The source compares both routes' flattened required header parameters and the generated validation schemas.",
                "The default and Annotated workflows observe selected parameter/schema pointers for both routes; neither checks the exact complete OpenAPI snapshot, operation names, or all component fields.",
                [
                    _link(
                        _GLOBAL_DEFAULT,
                        "fastapi.dependencies.tutorial012.global-headers-default",
                        ["openapi-parameters"],
                        _OPENAPI,
                    ),
                    _link(
                        _GLOBAL_ANNOTATED,
                        "fastapi.dependencies.tutorial012.global-headers-annotated",
                        ["openapi-parameters"],
                        _OPENAPI,
                    ),
                ],
                (
                    _source(
                        "docs_src/dependencies/tutorial012_py310.py",
                        1,
                        25,
                        "global header dependencies and protected routes represented by OpenAPI",
                    ),
                    _OPENAPI_PARAMS,
                    _OPENAPI_RESPONSES,
                ),
            ),
        },
    ),
}


# The upstream fixtures run the same assertions against these additional
# default/Annotated examples. Cite each pinned source variant at the module and
# function levels without duplicating test code or treating the variants as
# separate parity results.
_ANNOTATION_VARIANT_SOURCES = {
    "tests/test_tutorial/test_dependencies/test_tutorial001_tutorial001_02.py": (
        _source(
            "docs_src/dependencies/tutorial001_an_py310.py",
            1,
            19,
            "Annotated shared query dependency example",
        ),
        _source(
            "docs_src/dependencies/tutorial001_02_an_py310.py",
            1,
            22,
            "second Annotated query dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial002_tutorial003_tutorial004.py": (
        _source(
            "docs_src/dependencies/tutorial002_an_py310.py",
            1,
            25,
            "Annotated explicit class dependency example",
        ),
        _source(
            "docs_src/dependencies/tutorial003_an_py310.py",
            1,
            25,
            "Annotated untyped class dependency example",
        ),
        _source(
            "docs_src/dependencies/tutorial004_an_py310.py",
            1,
            25,
            "Annotated inferred class dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial005.py": (
        _source(
            "docs_src/dependencies/tutorial005_an_py310.py",
            1,
            25,
            "Annotated query/cookie dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial006.py": (
        _source(
            "docs_src/dependencies/tutorial006_an_py310.py",
            1,
            21,
            "Annotated required-header dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008.py": (
        _source(
            "docs_src/dependencies/tutorial008_an_py310.py",
            1,
            27,
            "Annotated nested yield dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008b.py": (
        _source(
            "docs_src/dependencies/tutorial008b_an_py310.py",
            1,
            32,
            "Annotated ownership-check yield dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008c.py": (
        _source(
            "docs_src/dependencies/tutorial008c_an_py310.py",
            1,
            29,
            "Annotated suppressing yield dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008d.py": (
        _source(
            "docs_src/dependencies/tutorial008d_an_py310.py",
            1,
            30,
            "Annotated re-raising yield dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial008e.py": (
        _source(
            "docs_src/dependencies/tutorial008e_an_py310.py",
            1,
            17,
            "Annotated function-scoped yield dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial011.py": (
        _source(
            "docs_src/dependencies/tutorial011_an_py310.py",
            1,
            23,
            "Annotated callable dependency example",
        ),
    ),
    "tests/test_tutorial/test_dependencies/test_tutorial012.py": (
        _source(
            "docs_src/dependencies/tutorial012_an_py310.py",
            1,
            27,
            "Annotated global-header dependency example",
        ),
    ),
}

for _test_path, _variant_sources in _ANNOTATION_VARIANT_SOURCES.items():
    _module_mapping = DEPENDENCY_TUTORIAL_TEST_REVIEW_MAPPINGS[_test_path]
    for _function_mapping in _module_mapping["functions"].values():
        _function_mapping["supporting_sources"].extend(_variant_sources)
    _module_mapping["supporting_sources"].extend(_variant_sources)


DEPENDENCY_TUTORIAL_TEST_MODULE_EXCLUSIONS = {
    "tests/test_tutorial/test_dependencies/test_tutorial007.py": {
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": "The test manually wraps the documented generator with contextlib.asynccontextmanager, patches DBSession, and asserts object identity/close calls. It does not instantiate FastAPI, use Depends, or send an HTTP/ASGI request; this is app-owned generator code rather than FastAPI behavior.",
        "supporting_sources": [
            _source(
                "tests/test_tutorial/test_dependencies/test_tutorial007.py",
                8,
                24,
                "direct generator invocation and Mock assertions without a FastAPI app",
            ),
            _source(
                "docs_src/dependencies/tutorial007_py310.py",
                1,
                6,
                "app-owned get_db generator under test",
            ),
        ],
    },
    "tests/test_tutorial/test_dependencies/__init__.py": {
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": "The package marker has no executable test functions and is outside the tests/test_*.py module denominator.",
        "supporting_sources": [
            {
                "path": "tests/test_tutorial/test_dependencies/__init__.py",
                "role": "pinned FastAPI package marker without test functions",
            }
        ],
    },
}
