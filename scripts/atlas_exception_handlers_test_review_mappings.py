"""Function-level source and workflow review for FastAPI exception handlers."""

from __future__ import annotations

from typing import Any

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.157.0",
        "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI exception dispatch, server-error middleware, and TestClient contract",
    },
    "pydantic": {
        "version": "2.13.5",
        "role": "pinned parameter-validation dependency for the invalid path input",
    },
}

__all__ = ["EXCEPTION_HANDLERS_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _link(
    recipe_path: str,
    case_id: str,
    action_id: str,
    selectors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": [action_id],
        "observation_selectors": list(selectors),
    }


def _direct_link(
    workflow_id: str,
    recipe_path: str,
    case_id: str,
    action_id: str,
    selectors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        **_link(recipe_path, case_id, action_id, selectors),
    }


def _function(
    name: str,
    start: int,
    end: int,
    selectors: tuple[str, ...],
    rationale: str,
    workflow: dict[str, Any],
    gate: str,
    sources: tuple[dict[str, Any], ...],
    direct_workflow_case: dict[str, Any],
) -> dict[str, Any]:
    link_text = (
        f"{workflow['recipe_path']}::{workflow['case_id']} "
        f"(action: {workflow['action_ids'][0]}; "
        f"selectors: {', '.join(workflow['observation_selectors'])})"
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": ["public-api-errors"],
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "workflow_case": direct_workflow_case,
        "workflow_cases": [workflow],
        "stimulus_notes": (
            "Independent input-only workflow reference: "
            + link_text
            + ". The recipe has no expected outputs or copied upstream test body."
        ),
        "supporting_sources": [
            _source(
                "tests/test_exception_handlers.py",
                start,
                end,
                f"pinned FastAPI 0.157.0 test function {name} and its assertions",
            ),
            *sources,
        ],
    }


def _module(functions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_rows: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in functions.values():
        for source in row["supporting_sources"]:
            key = (source["path"], source["start_line"], source["end_line"], source["role"])
            source_rows.setdefault(key, source)
    links_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in functions.values():
        for link in row["workflow_cases"]:
            links_by_key.setdefault((link["recipe_path"], link["case_id"]), link)
    return {
        "review_status": "reviewed_partial",
        "rationale": (
            "All five test functions have an input-only case link. FastAPI owns handler-map "
            "registration, validation-error creation, and dependency solving; generic exception "
            "dispatch, server-error response mechanics, and TestClient re-raising belong to the "
            "pinned Starlette 1.6.0 contract."
        ),
        "supporting_sources": list(source_rows.values()),
        "workflow_cases": list(links_by_key.values()),
        "module_observation_selectors": sorted(
            {selector for row in functions.values() for selector in row["observation_selectors"]}
        ),
        "functions": functions,
    }


_EXISTING_RECIPE = "tests/fixtures/input-recipes/parity/middleware-exceptions-upstream.yaml"
_NEW_RECIPE = "tests/fixtures/input-recipes/parity/exception-handlers-test-review.yaml"
_HTTP_STATUS = ("http.status",)
_ERROR_CLASS = ("validation.error_class",)
_HTTP_ACTION_SELECTORS = ("http.body.bytes", "http.headers.ordered", "http.status")
_ERROR_ACTION_SELECTORS = (
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "validation.error_class",
)

_TEST_HANDLER_SETUP = _source(
    "tests/test_exception_handlers.py",
    8,
    26,
    "The source declares three handlers and registers HTTP, request-validation, and generic exception mappings",
)
_HTTP_HANDLER_SOURCES = (
    _TEST_HANDLER_SETUP,
    _source(
        "tests/test_exception_handlers.py",
        43,
        45,
        "The source route raises FastAPI HTTPException for the tested request",
    ),
    _source(
        "fastapi/applications.py",
        997,
        1056,
        "FastAPI retains supplied exception handlers and places non-server handlers in ExceptionMiddleware",
    ),
    _source(
        "fastapi/exceptions.py",
        17,
        45,
        "FastAPI HTTPException subclasses Starlette HTTPException",
    ),
    _source(
        "starlette/_exception_handler.py",
        41,
        63,
        "Starlette 1.6.0 dispatches a raised HTTP exception to its selected handler",
    ),
)

_VALIDATION_HANDLER_SOURCES = (
    _TEST_HANDLER_SETUP,
    _source(
        "tests/test_exception_handlers.py",
        48,
        50,
        "The source route declares an integer path parameter for invalid-input validation",
    ),
    _source(
        "fastapi/applications.py",
        997,
        1056,
        "FastAPI retains the custom RequestValidationError handler in ExceptionMiddleware",
    ),
    _source(
        "fastapi/routing.py",
        792,
        799,
        "FastAPI raises RequestValidationError when parsed path or dependency validation fails",
    ),
    _source(
        "starlette/_exception_handler.py",
        41,
        63,
        "Starlette 1.6.0 dispatches the raised validation exception to its selected handler",
    ),
    _source(
        "starlette/routing.py",
        704,
        718,
        "Starlette 1.6.0 redirects to a matching route when the slash form differs",
    ),
    _source(
        "starlette/testclient.py",
        385,
        418,
        "Starlette 1.6.0 TestClient follows redirects by default",
    ),
)

_SERVER_ERROR_SOURCES = (
    _TEST_HANDLER_SETUP,
    _source(
        "tests/test_exception_handlers.py",
        53,
        55,
        "The source route raises RuntimeError to enter the server-error handler path",
    ),
    _source(
        "fastapi/applications.py",
        1032,
        1056,
        "FastAPI assigns an Exception handler to its outer ServerErrorMiddleware",
    ),
    _source(
        "starlette/middleware/errors.py",
        163,
        186,
        "Starlette 1.6.0 invokes the generic server-error handler, sends its response, then re-raises",
    ),
    _source(
        "starlette/testclient.py",
        348,
        365,
        "Starlette 1.6.0 TestClient re-raises by default and suppresses the exception when configured false",
    ),
)

_DEPENDENCY_ERROR_SOURCES = (
    _source(
        "fastapi/dependencies/utils.py",
        637,
        645,
        "FastAPI enters generator dependencies through an async exit stack",
    ),
    _source(
        "tests/test_exception_handlers.py",
        31,
        40,
        "Source dependency raises before yielding and is attached to the tested route",
    ),
    _source(
        "starlette/testclient.py",
        348,
        365,
        "Starlette 1.6.0 TestClient propagates the application exception",
    ),
)

EXCEPTION_HANDLERS_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_exception_handlers.py": _module(
        {
            "test_override_http_exception": _function(
                "test_override_http_exception",
                58,
                61,
                _HTTP_STATUS,
                "A FastAPI HTTPException handler replaces the default error representation with a status-200 JSON response.",
                _link(
                    _EXISTING_RECIPE,
                    "fastapi.test.test-exception-handlers.test-override-http-exception",
                    "dispatch",
                    _HTTP_ACTION_SELECTORS,
                ),
                "The direct link claims only the status selector. The independent action uses a subclass exception and decorator registration, and selects raw body bytes rather than the source's parsed JSON assertion; generic exception dispatch remains Starlette-owned.",
                _HTTP_HANDLER_SOURCES,
                _direct_link(
                    "middleware-exceptions-upstream",
                    _EXISTING_RECIPE,
                    "fastapi.test.test-exception-handlers.test-override-http-exception",
                    "dispatch",
                    _HTTP_ACTION_SELECTORS,
                ),
            ),
            "test_override_request_validation_exception": _function(
                "test_override_request_validation_exception",
                64,
                67,
                _HTTP_STATUS,
                "A FastAPI RequestValidationError handler replaces the default validation response after invalid path input.",
                _link(
                    _EXISTING_RECIPE,
                    "fastapi.test.test-exception-handlers.test-override-request-validation-exception",
                    "dispatch",
                    _HTTP_ACTION_SELECTORS,
                ),
                "The direct link claims only the status selector. The independent workflow uses a different slashless integer route and invalid value and selects raw body bytes rather than the source's parsed JSON assertion. The source request omits its route's terminal slash and relies on Starlette's default redirect-following behavior, which this ASGI input does not replay.",
                _VALIDATION_HANDLER_SOURCES,
                _direct_link(
                    "middleware-exceptions-upstream",
                    _EXISTING_RECIPE,
                    "fastapi.test.test-exception-handlers.test-override-request-validation-exception",
                    "dispatch",
                    _HTTP_ACTION_SELECTORS,
                ),
            ),
            "test_override_server_error_exception_raises": _function(
                "test_override_server_error_exception_raises",
                70,
                72,
                _ERROR_CLASS,
                "The source expects the application RuntimeError to escape through TestClient even though an Exception handler is installed.",
                _link(
                    _NEW_RECIPE,
                    "fastapi.test.exception-handlers.server-error-handler-response",
                    "server-error",
                    _ERROR_ACTION_SELECTORS,
                ),
                "The selected ASGI action observes the application error class, which supports the RuntimeError propagation assertion. TestClient's default re-raise option is Starlette-owned and is not a recipe input.",
                _SERVER_ERROR_SOURCES,
                _direct_link(
                    "exception-handlers-test-review",
                    _NEW_RECIPE,
                    "fastapi.test.exception-handlers.server-error-handler-response",
                    "server-error",
                    _ERROR_ACTION_SELECTORS,
                ),
            ),
            "test_override_server_error_exception_response": _function(
                "test_override_server_error_exception_response",
                75,
                79,
                _HTTP_STATUS,
                "A FastAPI Exception handler is assigned to the server-error path and emits the tested 500 JSON response.",
                _link(
                    _NEW_RECIPE,
                    "fastapi.test.exception-handlers.server-error-handler-response",
                    "server-error",
                    _ERROR_ACTION_SELECTORS,
                ),
                "The direct link claims only the 500 status selector. The independent workload uses another RuntimeError, route, and handler body; its selected response observation is raw bytes rather than parsed JSON. ServerErrorMiddleware and TestClient suppression are Starlette-owned.",
                _SERVER_ERROR_SOURCES,
                _direct_link(
                    "exception-handlers-test-review",
                    _NEW_RECIPE,
                    "fastapi.test.exception-handlers.server-error-handler-response",
                    "server-error",
                    _ERROR_ACTION_SELECTORS,
                ),
            ),
            "test_traceback_for_dependency_with_yield": _function(
                "test_traceback_for_dependency_with_yield",
                82,
                88,
                _ERROR_CLASS,
                "A ValueError raised while resolving a yield dependency propagates out of the FastAPI request path.",
                _link(
                    _NEW_RECIPE,
                    "fastapi.test.exception-handlers.yield-dependency-error",
                    "dependency-error",
                    _ERROR_ACTION_SELECTORS,
                ),
                "The selected ASGI action observes the ValueError class raised while resolving a yield dependency. The source traceback-frame path and line have no workflow selector, and TestClient propagation is Starlette-owned.",
                _DEPENDENCY_ERROR_SOURCES,
                _direct_link(
                    "exception-handlers-test-review",
                    _NEW_RECIPE,
                    "fastapi.test.exception-handlers.yield-dependency-error",
                    "dependency-error",
                    _ERROR_ACTION_SELECTORS,
                ),
            ),
        }
    )
}
