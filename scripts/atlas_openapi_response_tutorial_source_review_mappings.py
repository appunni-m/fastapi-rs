"""Function-level review for OpenAPI and response tutorial test inputs.

The mappings refer to independently authored ASGI inputs. Existing cases are
reused where they already cover the source function; this module adds no copied
test code, documentation sample, or expected response. FastAPI owns route and
OpenAPI integration, Pydantic owns model validation/schema generation, and
Starlette 1.6.0 owns generic response and TestClient/HTTPX behavior.
"""

from __future__ import annotations

import ast
import hashlib
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
        "role": "sole generic ASGI, response-class, FileResponse, and TestClient transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned request-model validation and generated model-schema dependency",
    },
}

__all__ = [
    "OPENAPI_RESPONSE_TUTORIAL_SOURCE_REVIEW",
    "SOURCE_IDENTITIES",
    "SOURCE_SCOPE",
    "TEST_HARNESS_EXCLUSIONS",
]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _top_level_functions(test_path: str) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def _span(test_path: str, function_name: str) -> dict[str, Any]:
    functions = _top_level_functions(test_path)
    if function_name not in functions:
        raise ValueError(f"missing top-level test function {function_name} in {test_path}")
    node = functions[function_name]
    decorated_start = min([node.lineno, *(item.lineno for item in node.decorator_list)])
    return _source(
        test_path,
        decorated_start,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test function {function_name} and its assertions",
    )


def _span_named_definition(test_path: str, definition_name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == definition_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {definition_name} in {test_path}")
    node = matches[0]
    decorated_start = min([node.lineno, *(item.lineno for item in node.decorator_list)])
    return _source(
        test_path,
        decorated_start,
        node.end_lineno or node.lineno,
        f"test-harness helper {definition_name}; not a compatibility test function",
    )


def _span_assignment(test_path: str, target_name: str, role: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == target_name for target in node.targets
        ):
            matches.append(node)
    if len(matches) != 1:
        raise ValueError(f"expected one top-level assignment to {target_name} in {test_path}")
    node = matches[0]
    return _source(test_path, node.lineno, node.end_lineno or node.lineno, role)


_SCOPE_PATHS = (
    "tests/test_tutorial/test_schema_extra_example/test_tutorial001.py",
    "tests/test_tutorial/test_schema_extra_example/test_tutorial002.py",
    "tests/test_tutorial/test_schema_extra_example/test_tutorial003.py",
    "tests/test_tutorial/test_schema_extra_example/test_tutorial004.py",
    "tests/test_tutorial/test_schema_extra_example/test_tutorial005.py",
    "tests/test_tutorial/test_additional_responses/test_tutorial001.py",
    "tests/test_tutorial/test_additional_responses/test_tutorial002.py",
    "tests/test_tutorial/test_additional_responses/test_tutorial003.py",
    "tests/test_tutorial/test_additional_responses/test_tutorial004.py",
    "tests/test_tutorial/test_response_directly/test_tutorial002.py",
)

_PREEXISTING_MODULES = {path for path in _SCOPE_PATHS if "/test_additional_responses/" in path}


def _scope_row(test_path: str) -> dict[str, Any]:
    source_path = FASTAPI_ROOT / test_path
    test_functions = _top_level_functions(test_path)
    is_preexisting = test_path in _PREEXISTING_MODULES
    return {
        "source_module_path": test_path,
        "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "test_function_count": len(test_functions),
        "test_functions": {name: _span(test_path, name) for name in sorted(test_functions)},
        "mapping_disposition": (
            "preexisting_function_mappings_reused"
            if is_preexisting
            else "function_mappings_added_by_this_sidecar"
        ),
        "mapping_reference": (
            "scripts/atlas_tutorial_response_body_input_review_mappings.py"
            if is_preexisting
            else "scripts/atlas_openapi_response_tutorial_source_review_mappings.py"
        ),
    }


SOURCE_SCOPE = {test_path: _scope_row(test_path) for test_path in _SCOPE_PATHS}


def _link(
    recipe_path: str,
    case_id: str,
    action_ids: tuple[str, ...],
    selectors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _function(
    test_path: str,
    function_name: str,
    feature_ids: tuple[str, ...],
    source_assertion_selectors: tuple[str, ...],
    rationale: str,
    links: tuple[dict[str, Any], ...],
    gate: str,
    supporting_sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    workflow_selectors = sorted(
        {selector for link in links for selector in link["observation_selectors"]}
    )
    link_note = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} actions "
        f"{', '.join(link['action_ids'])} ({', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": workflow_selectors,
        "source_assertion_selectors": list(source_assertion_selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "workflow_cases": list(links),
        "stimulus_notes": (
            "Independent input-only workflow links: "
            + link_note
            + ". Linked recipes select inputs and observations only; they contain no expected outputs or copied upstream bodies."
        ),
        "supporting_sources": [_span(test_path, function_name), *supporting_sources],
    }


_SCHEMA_RECIPE = "tests/fixtures/input-recipes/parity/schema-extra-examples-upstream.yaml"
_SCHEMA_FASTAPI_BODY = _source(
    "fastapi/routing.py",
    425,
    475,
    "FastAPI reads/parses a declared request body and proceeds to dependency and endpoint handling",
)
_OPENAPI_ENTRY = _source(
    "fastapi/applications.py",
    1070,
    1103,
    "FastAPI.openapi caches or regenerates the document using its registered routes",
)
_OPENAPI_REQUEST_BODY = _source(
    "fastapi/openapi/utils.py",
    231,
    263,
    "FastAPI encodes request-body schema, Body.example, and Body.openapi_examples into the operation",
)
_OPENAPI_MODEL_SCHEMA = _source(
    "fastapi/_compat/v2.py",
    254,
    345,
    "FastAPI selects generated model fields and delegates JSON Schema generation to the Pydantic v2 adapter",
)
_OPENAPI_OPERATION = _source(
    "fastapi/openapi/utils.py",
    311,
    418,
    "FastAPI assembles the route operation, summary/id, parameters, request body, and initial response description",
)
_DIRECT_RESPONSE = _source(
    "fastapi/routing.py",
    706,
    714,
    "FastAPI preserves a returned Starlette Response instance and attaches pending background work when needed",
)
_STARLETTE_TESTCLIENT = (
    _source("fastapi/testclient.py", 1, 1, "FastAPI directly re-exports Starlette TestClient"),
    _source(
        "starlette/testclient.py",
        377,
        420,
        "Starlette 1.6.0 implements TestClient over its ASGI transport and HTTPX client base",
    ),
)
_STARLETTE_HTTPX_IMPORT = _source(
    "starlette/testclient.py",
    32,
    51,
    "Starlette 1.6.0 prefers httpx2 and emits a deprecation warning for the legacy httpx fallback",
)
_STARLETTE_FILE_RESPONSE = _source(
    "starlette/responses.py",
    296,
    400,
    "Starlette 1.6.0 chooses FileResponse media/header metadata and transfers the file body over ASGI",
)


def _one(
    case_id: str,
    action_id: str,
    selectors: tuple[str, ...] = ("http.status",),
) -> dict[str, Any]:
    return _link(_SCHEMA_RECIPE, case_id, (action_id,), selectors)


_SCHEMA_FUNCTIONS: dict[str, dict[str, Any]] = {
    "tests/test_tutorial/test_schema_extra_example/test_tutorial001.py": {
        "test_post_body_example": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial001.py",
            "test_post_body_example",
            ("request-validation",),
            ("http.status",),
            "A valid model body is submitted to an independently named PUT route; the source asserts successful status only.",
            (_one("fastapi.schema-extra-example.model-schema-extra", "submit-config-extra"),),
            "The workflow checks only status for a different route, payload, and schema model. Pydantic owns model parsing/validation; Starlette's TestClient/HTTPX transport is outside the FastAPI behavior claim.",
            (_SCHEMA_FASTAPI_BODY, *_STARLETTE_TESTCLIENT, _STARLETTE_HTTPX_IMPORT),
        ),
        "test_openapi_schema": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial001.py",
            "test_openapi_schema",
            ("openapi-docs", "request-validation"),
            ("http.status", "openapi.document"),
            "The snapshot includes a model-config JSON Schema example on the component referenced by the request body.",
            (
                _one(
                    "fastapi.schema-extra-example.model-schema-extra",
                    "model-config-openapi",
                    ("http.status", "openapi.document"),
                ),
            ),
            "The independent case selects one component schema and does not compare the source's complete OpenAPI document, path metadata, or exact model names. FastAPI controls placement; Pydantic 2.13.4 owns model JSON Schema mechanics.",
            (_OPENAPI_ENTRY, _OPENAPI_REQUEST_BODY, _OPENAPI_MODEL_SCHEMA),
        ),
    },
    "tests/test_tutorial/test_schema_extra_example/test_tutorial002.py": {
        "test_post_body_example": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial002.py",
            "test_post_body_example",
            ("request-validation",),
            ("http.status",),
            "A valid model body with field examples is submitted; the source checks only successful status.",
            (_one("fastapi.schema-extra-example.field-examples", "submit-field-examples"),),
            "The independently authored route and body exercise one valid request only; model parsing remains Pydantic-owned and generic TestClient transport remains Starlette-owned.",
            (_SCHEMA_FASTAPI_BODY, *_STARLETTE_TESTCLIENT, _STARLETTE_HTTPX_IMPORT),
        ),
        "test_openapi_schema": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial002.py",
            "test_openapi_schema",
            ("openapi-docs", "request-validation"),
            ("http.status", "openapi.document"),
            "The snapshot checks field-level examples in the referenced model component schema.",
            (
                _one(
                    "fastapi.schema-extra-example.field-examples",
                    "field-examples-openapi",
                    ("http.status", "openapi.document"),
                ),
            ),
            "Only the independent component-schema pointer is compared, not the whole source snapshot, operation metadata, or source model names. Pydantic generates field schemas; FastAPI inserts them into the document.",
            (_OPENAPI_ENTRY, _OPENAPI_REQUEST_BODY, _OPENAPI_MODEL_SCHEMA),
        ),
    },
    "tests/test_tutorial/test_schema_extra_example/test_tutorial003.py": {
        "test_post_body_example": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial003.py",
            "test_post_body_example",
            ("request-validation",),
            ("http.status",),
            "The source's valid PUT request is represented by default and Annotated body routes with independently authored values.",
            (
                _one(
                    "fastapi.schema-extra-example.body-examples-list",
                    "submit-body-examples-default",
                ),
                _one(
                    "fastapi.schema-extra-example.body-examples-list",
                    "submit-body-examples-annotated",
                ),
            ),
            "Both parameterized app forms receive successful-status probes, but their response values, exact source request, and full runtime validation surface are not selected. Pydantic owns body-model mechanics.",
            (_SCHEMA_FASTAPI_BODY, *_STARLETTE_TESTCLIENT, _STARLETTE_HTTPX_IMPORT),
        ),
        "test_openapi_schema": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial003.py",
            "test_openapi_schema",
            ("openapi-docs", "request-validation"),
            ("http.status", "openapi.document", "openapi.request_schema"),
            "The snapshot checks the single request-body example attached to the body schema in default and Annotated route forms.",
            (
                _one(
                    "fastapi.schema-extra-example.body-examples-list",
                    "body-examples-openapi",
                    ("http.status", "openapi.document", "openapi.request_schema"),
                ),
            ),
            "The workflow selects only the two request-body schema pointers; it does not compare the complete OpenAPI snapshot, generated components, or route naming. FastAPI encodes Body examples and Pydantic supplies model schema details.",
            (_OPENAPI_ENTRY, _OPENAPI_REQUEST_BODY, _OPENAPI_MODEL_SCHEMA),
        ),
    },
    "tests/test_tutorial/test_schema_extra_example/test_tutorial004.py": {
        "test_post_body_example": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial004.py",
            "test_post_body_example",
            ("request-validation",),
            ("http.status",),
            "The source's valid request is sampled against default and Annotated routes configured with multiple body examples.",
            (
                _one(
                    "fastapi.schema-extra-example.body-examples-several",
                    "submit-body-examples-default",
                ),
                _one(
                    "fastapi.schema-extra-example.body-examples-several",
                    "submit-body-examples-annotated",
                ),
            ),
            "The independent probes select successful status only; they do not claim the source response body or all accepted model inputs. Pydantic owns model validation.",
            (_SCHEMA_FASTAPI_BODY, *_STARLETTE_TESTCLIENT, _STARLETTE_HTTPX_IMPORT),
        ),
        "test_openapi_schema": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial004.py",
            "test_openapi_schema",
            ("openapi-docs", "request-validation"),
            ("http.status", "openapi.document", "openapi.request_schema"),
            "The snapshot checks multiple examples for both default and Annotated request-body routes.",
            (
                _one(
                    "fastapi.schema-extra-example.body-examples-several",
                    "several-examples-openapi",
                    ("http.status", "openapi.document", "openapi.request_schema"),
                ),
            ),
            "The workflow compares selected request-body schema pointers, not the complete source document or exact example/model names. FastAPI places body examples in OpenAPI; Pydantic provides model schema details.",
            (_OPENAPI_ENTRY, _OPENAPI_REQUEST_BODY, _OPENAPI_MODEL_SCHEMA),
        ),
    },
    "tests/test_tutorial/test_schema_extra_example/test_tutorial005.py": {
        "test_post_body_example": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial005.py",
            "test_post_body_example",
            ("request-validation",),
            ("http.status",),
            "The valid source body is submitted to independently authored routes with named OpenAPI examples.",
            (
                _one(
                    "fastapi.schema-extra-example.openapi-example-objects",
                    "submit-openapi-examples-default",
                ),
                _one(
                    "fastapi.schema-extra-example.openapi-example-objects",
                    "submit-openapi-examples-annotated",
                ),
            ),
            "The independent requests select status only and do not compare request or response payload values. Model parsing remains Pydantic-owned.",
            (_SCHEMA_FASTAPI_BODY, *_STARLETTE_TESTCLIENT, _STARLETTE_HTTPX_IMPORT),
        ),
        "test_openapi_schema": _function(
            "tests/test_tutorial/test_schema_extra_example/test_tutorial005.py",
            "test_openapi_schema",
            ("openapi-docs", "request-validation"),
            ("http.status", "openapi.document"),
            "The snapshot checks named OpenAPI example objects on default and Annotated request bodies.",
            (
                _one(
                    "fastapi.schema-extra-example.openapi-example-objects",
                    "named-examples-openapi",
                    ("http.status", "openapi.document"),
                ),
            ),
            "The workflow selects example objects for two independent operations, not their whole path objects, source component schemas, or the full OpenAPI document. It does not claim the examples as model validation fixtures.",
            (_OPENAPI_ENTRY, _OPENAPI_REQUEST_BODY, _OPENAPI_MODEL_SCHEMA),
        ),
    },
}


_DIRECT_RECIPE = "tests/fixtures/input-recipes/parity/responses-background-upstream.yaml"
_DIRECT_TEST_PATH = "tests/test_tutorial/test_response_directly/test_tutorial002.py"
_DIRECT_FUNCTIONS = {
    "test_path_operation": _function(
        _DIRECT_TEST_PATH,
        "test_path_operation",
        ("response-serialization",),
        ("http.status", "http.headers.ordered", "http.body.bytes"),
        "The source returns an XML Response instance and checks status, media type, and decoded text.",
        (
            _link(
                _DIRECT_RECIPE,
                "fastapi.test.test-tutorial-test-response-directly-test-tutorial002.test-path-operation",
                ("direct-response",),
                ("http.status", "http.headers.ordered", "http.body.bytes"),
            ),
        ),
        "The independent XML route returns different content and selects exact raw body bytes plus all headers; it does not compare the source's decoded text value. FastAPI's returned-Response passthrough is the FastAPI claim; XML media/body rendering and TestClient/HTTPX transport are Starlette-owned.",
        (_DIRECT_RESPONSE, *_STARLETTE_TESTCLIENT, _STARLETTE_HTTPX_IMPORT),
    ),
    "test_openapi_schema": _function(
        _DIRECT_TEST_PATH,
        "test_openapi_schema",
        ("openapi-docs",),
        ("http.status", "openapi.document"),
        "The source snapshot checks the OpenAPI operation for a path returning a direct Response without a response model.",
        (
            _link(
                _DIRECT_RECIPE,
                "fastapi.test.test-tutorial-test-response-directly-test-tutorial002.test-openapi-schema",
                ("schema",),
                ("http.status", "openapi.document", "openapi.paths"),
            ),
        ),
        "The independent case selects one path operation and successful status, not the full document or exact source operation id. The recipe records the HTTP status separately from the selected OpenAPI path pointer.",
        (_OPENAPI_ENTRY, _OPENAPI_OPERATION),
    ),
}


OPENAPI_RESPONSE_TUTORIAL_SOURCE_REVIEW = {
    "fastapi_identity": SOURCE_IDENTITIES["fastapi"],
    "starlette_identity": SOURCE_IDENTITIES["starlette"],
    "pydantic_identity": SOURCE_IDENTITIES["pydantic"],
    "ownership_notes": [
        "FastAPI 0.141.1 owns request-body integration into route handling, direct returned-Response passthrough, and assembly/placement of route and request-body data in OpenAPI. The original FastAPI checkout is source-oracle/dev-only.",
        "Pydantic 2.13.4 owns model validation and generated JSON Schema details. FastAPI selects fields and places Pydantic schema results into the OpenAPI document.",
        "Starlette 1.6.0 owns generic FileResponse metadata/body transfer and TestClient HTTP transport. FastAPI directly re-exports TestClient. The tests do not inspect HTTPX request construction or backend-specific transport behavior.",
        "No FastAPI alias or deprecation behavior is asserted by these source functions. Starlette 1.6.0's legacy `httpx` fallback warning is documented as a harness boundary, not mapped behavior; the default TestClient contract prefers `httpx2`.",
    ],
    "scope_counts": {
        "source_modules": len(SOURCE_SCOPE),
        "test_functions": sum(row["test_function_count"] for row in SOURCE_SCOPE.values()),
        "new_function_mappings": sum(len(row) for row in _SCHEMA_FUNCTIONS.values())
        + len(_DIRECT_FUNCTIONS),
        "preexisting_function_mappings_reused": sum(
            SOURCE_SCOPE[path]["test_function_count"] for path in _PREEXISTING_MODULES
        ),
        "excluded_test_functions": 0,
    },
    "modules": {
        **_SCHEMA_FUNCTIONS,
        _DIRECT_TEST_PATH: _DIRECT_FUNCTIONS,
    },
    "preexisting_module_mapping_reference": (
        "scripts/atlas_tutorial_response_body_input_review_mappings.py"
    ),
}


TEST_HARNESS_EXCLUSIONS = {
    "excluded_test_function_count": 0,
    "excluded_non_test_helpers": [
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_schema_extra_example/test_tutorial001.py",
                "get_client",
            ),
            "reason": "The pytest fixture imports a documentation app and creates a TestClient; it prepares each test but makes no product assertion and is outside the test-function denominator.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_schema_extra_example/test_tutorial002.py",
                "get_client",
            ),
            "reason": "The pytest fixture imports a documentation app and creates a TestClient; it prepares the mapped request and makes no product assertion.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_schema_extra_example/test_tutorial003.py",
                "get_client",
            ),
            "reason": "The parameterized pytest fixture imports documentation apps and creates TestClient instances; fixture setup is not a FastAPI test assertion.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_schema_extra_example/test_tutorial004.py",
                "get_client",
            ),
            "reason": "The parameterized pytest fixture imports documentation apps and creates TestClient instances; fixture setup is not a FastAPI test assertion.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_schema_extra_example/test_tutorial005.py",
                "get_client",
            ),
            "reason": "The parameterized pytest fixture imports documentation apps and creates TestClient instances; fixture setup is not a FastAPI test assertion.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_assignment(
                "tests/test_tutorial/test_additional_responses/test_tutorial001.py",
                "client",
                "module-level TestClient construction; it prepares requests but is not a test-function assertion",
            ),
            "reason": "The module-level client is test setup only; assertions are accounted for by the three mapped test functions.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_additional_responses/test_tutorial002.py",
                "get_client",
            ),
            "reason": "The fixture creates a TestClient and clears its default headers before requests; setup is not a FastAPI assertion. The image copy/delete operations in test_path_operation_img only provision and clean the test file.",
            "owner": "Starlette TestClient/HTTPX harness and upstream test filesystem setup",
            "supporting_sources": [
                _span(
                    "tests/test_tutorial/test_additional_responses/test_tutorial002.py",
                    "test_path_operation_img",
                ),
                _span_assignment(
                    "tests/utils.py",
                    "workdir_lock",
                    "pytest xdist group marker serializes tests that create image.png in the working directory",
                ),
            ],
        },
        {
            "source": _span_assignment(
                "tests/test_tutorial/test_additional_responses/test_tutorial003.py",
                "client",
                "module-level TestClient construction; it prepares requests but is not a test-function assertion",
            ),
            "reason": "The module-level client is test setup only; assertions are accounted for by the three preexisting function mappings.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
        {
            "source": _span_named_definition(
                "tests/test_tutorial/test_additional_responses/test_tutorial004.py",
                "get_client",
            ),
            "reason": "The fixture creates a TestClient and clears its default headers before requests; setup is not a FastAPI assertion. The image copy/delete operations in test_path_operation_img only provision and clean the test file.",
            "owner": "Starlette TestClient/HTTPX harness and upstream test filesystem setup",
            "supporting_sources": [
                _span(
                    "tests/test_tutorial/test_additional_responses/test_tutorial004.py",
                    "test_path_operation_img",
                ),
                _span_assignment(
                    "tests/utils.py",
                    "workdir_lock",
                    "pytest xdist group marker serializes tests that create image.png in the working directory",
                ),
            ],
        },
        {
            "source": _span_named_definition(_DIRECT_TEST_PATH, "get_client"),
            "reason": "The pytest fixture imports a documentation app and creates a TestClient; it only prepares the two mapped HTTP requests.",
            "owner": "Starlette TestClient harness; documentation app fixture setup",
        },
    ],
}
