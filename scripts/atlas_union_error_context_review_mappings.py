"""Function-level request-union and validation-context source review.

Workflow links are input-only cases. They contain request stimuli and public
observation selectors, with no copied assertion values or expected outputs.
This module records candidate mappings; it does not run workloads or parity.
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
        "role": "source oracle and development evidence only",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic routing, request parsing, ASGI transport, and TestClient contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "pydantic_core_version": "2.46.4",
        "role": "pinned BaseModel field, union validation, error-item, and schema authority",
    },
}

__all__ = [
    "SOURCE_IDENTITIES",
    "TOP_LEVEL_TEST_MODULES",
    "FUNCTION_DENOMINATORS",
    "TOTAL_FUNCTION_DENOMINATOR",
    "UNION_ERROR_CONTEXT_TEST_REVIEW_MAPPINGS",
    "validate_union_error_context_review_mappings",
]

TOP_LEVEL_TEST_MODULES = (
    "tests/test_union_body.py",
    "tests/test_union_body_discriminator.py",
    "tests/test_union_body_discriminator_annotated.py",
    "tests/test_union_forms.py",
    "tests/test_union_inherited_body.py",
    "tests/test_validation_error_context.py",
)

_PIN_SOURCE = (
    {
        "path": "tests/fixtures/manifest.yaml",
        "start_line": 47,
        "end_line": 52,
        "role": "reviewed oracle pin for Pydantic 2.13.4 / pydantic-core 2.46.4",
    },
    {
        "path": "tests/fixtures/manifest.yaml",
        "start_line": 60,
        "end_line": 77,
        "role": "reviewed FastAPI 0.141.1, Starlette 1.6.0, and Python package identity pins",
    },
)

_FASTAPI_UNION_SOURCES = (
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 271,
        "end_line": 347,
        "role": "FastAPI 0.141.1 inspects endpoint signatures and derives dependency/body fields",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 951,
        "end_line": 1048,
        "role": "FastAPI extracts URL-encoded fields, validates body parameters, and composes embedded body fields",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 425,
        "end_line": 465,
        "role": "FastAPI reads body bytes and selects JSON decoding/error handling before dependency solving",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 231,
        "end_line": 263,
        "role": "FastAPI places the Pydantic-derived request field schema and required flag in OpenAPI",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 331,
        "end_line": 385,
        "role": "FastAPI assembles OpenAPI operation metadata, request parameters, and requestBody",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 585,
        "end_line": 647,
        "role": "FastAPI generates the OpenAPI document from route contexts and model definitions",
    },
)

_FASTAPI_ERROR_CONTEXT_SOURCES = (
    {
        "path": "fastapi/routing.py",
        "start_line": 278,
        "end_line": 298,
        "role": "FastAPI extracts endpoint source file, line, and callable name for validation context",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 406,
        "end_line": 423,
        "role": "FastAPI attaches the HTTP method/path and mounted root_path to endpoint context",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 301,
        "end_line": 328,
        "role": "FastAPI validates response fields and raises ResponseValidationError with endpoint context",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 751,
        "end_line": 755,
        "role": "FastAPI raises RequestValidationError with endpoint context after request dependency validation",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 764,
        "end_line": 795,
        "role": "FastAPI builds WebSocket endpoint context, validates dependencies, and raises WebSocketRequestValidationError",
    },
    {
        "path": "fastapi/exceptions.py",
        "start_line": 174,
        "end_line": 243,
        "role": "FastAPI validation exception classes retain endpoint context and format it in __str__",
    },
)

_STARLETTE_TRANSPORT_SOURCES = (
    {
        "path": "starlette/requests.py",
        "start_line": 234,
        "end_line": 311,
        "role": "Starlette 1.6.0 streams HTTP request bytes and parses URL-encoded/multipart FormData",
    },
    {
        "path": "starlette/routing.py",
        "start_line": 363,
        "end_line": 424,
        "role": "Starlette 1.6.0 matches mounted HTTP/WebSocket scopes and extends child root_path",
    },
    {
        "path": "starlette/testclient.py",
        "start_line": 225,
        "end_line": 366,
        "role": "Starlette 1.6.0 TestClient encodes requests, drives ASGI, and re-raises server exceptions",
    },
)

_PYDANTIC_BOUNDARY = (
    "Pydantic 2.13.4 owns BaseModel field metadata, union-branch validation and coercion, "
    "Annotated Tag/Discriminator interpretation, validation error items, and model JSON Schema. "
    "FastAPI owns Python endpoint annotation inspection, deciding that these declarations are "
    "request bodies or forms, applying request/error locations and endpoint context, and placing "
    "the generated field schema into an OpenAPI operation. No Pydantic internals are claimed as "
    "FastAPI-RS behavior by this mapping."
)

_STARLETTE_BOUNDARY = (
    "Starlette 1.6.0 is the sole contract for ASGI request/response transport, URL-encoded form "
    "parsing, generic route/mount scope behavior, exception middleware, and TestClient encoding "
    "and re-raising. FastAPI owns body/form parameter binding, validation exception context and "
    "OpenAPI operation composition. The error-context workflows observe the ASGI exception "
    "directly; they do not claim TestClient transport or re-raising parity."
)

_RUST_TARGET_BOUNDARY = (
    "The original FastAPI tree is a development/oracle source only. Every FastAPI behavior "
    "described here belongs in fastapi-rs Rust control flow. The target Python runtime may only "
    "directly re-export native symbols and declare literal __all__; fastapi-rs-py is limited to "
    "PyO3 binding and value conversion. The Starlette 1.6.0 replacement has a separate Rust "
    "contract; Pydantic 2.13.4 remains the pinned model/validation/schema authority."
)

_PARITY_GATE = (
    "Input mapping only. Cases contain independent stimuli and selectors, not expected values, "
    "and no live parity was run. Compare the selectors only after identity-checked isolated "
    "execution; generic ASGI, form parser, mount, and TestClient behavior remains under the "
    "Starlette 1.6.0 contract, while Pydantic 2.13.4 retains model validation and schema ownership."
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
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
        f"pinned FastAPI 0.141.1 test function {function_name} and its assertions",
    )


def _test_function_spans(test_path: str) -> list[dict[str, Any]]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return [
        _source(
            test_path,
            node.lineno,
            node.end_lineno or node.lineno,
            f"pinned FastAPI 0.141.1 test function {node.name}",
        )
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


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
    rationale: str,
    links: tuple[dict[str, Any], ...],
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    selectors = sorted({selector for link in links for selector in link["observation_selectors"]})
    link_notes = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} actions "
        f"{', '.join(link['action_ids'])} observe "
        f"{', '.join(link['observation_selectors'])}"
        for link in links
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "behavior_ownership": {
            "fastapi_target": _RUST_TARGET_BOUNDARY,
            "pydantic": _PYDANTIC_BOUNDARY,
            "starlette": _STARLETTE_BOUNDARY,
        },
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + _PARITY_GATE,
        "workflow_cases": list(links),
        "stimulus_notes": (
            "Input-only links: "
            + link_notes
            + ". No expected response, snapshot value, or copied upstream test body is stored."
        ),
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _module(
    test_path: str,
    rationale: str,
    functions: dict[str, dict[str, Any]],
    module_sources: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    function_spans = _test_function_spans(test_path)
    source_function_names = {
        span["role"].removeprefix("pinned FastAPI 0.141.1 test function ")
        for span in function_spans
    }
    if source_function_names != set(functions):
        raise ValueError(
            f"function mapping denominator mismatch for {test_path}: "
            f"source={sorted(source_function_names)}, mapped={sorted(functions)}"
        )

    links: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in functions.values():
        for link in row["workflow_cases"]:
            key = (link["recipe_path"], link["case_id"], tuple(link["action_ids"]))
            links.setdefault(key, link)
        for source in row["supporting_sources"]:
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources.setdefault(key, source)
    for source in (*module_sources, *_PIN_SOURCE):
        key = (
            source["path"],
            source.get("start_line", 0),
            source.get("end_line", 0),
            source["role"],
        )
        sources.setdefault(key, source)
    selectors = sorted(
        {selector for row in functions.values() for selector in row["observation_selectors"]}
    )
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
        "source_test_spans": function_spans,
        "workflow_cases": list(links.values()),
        "module_observation_selectors": selectors,
        "pydantic_ownership_boundary": _PYDANTIC_BOUNDARY,
        "starlette_ownership_boundary": _STARLETTE_BOUNDARY,
        "rust_target_ownership_boundary": _RUST_TARGET_BOUNDARY,
        "contract_gate": "Partial: " + _PARITY_GATE,
        "supporting_sources": list(sources.values()),
        "functions": functions,
    }


_UNION_HTTP = ("http.status", "http.body.bytes")
_UNION_OPENAPI = ("http.status", "openapi.document")
_APPLICATION_EXCEPTION = ("asgi.application_error.exception",)
_CONSTRUCTION_SELECTORS = (
    "construction.outcome",
    "construction.exception_class",
    "construction.exception_message",
)
_VALIDATION_EXCEPTION_SELECTORS = (*_APPLICATION_EXCEPTION, *_CONSTRUCTION_SELECTORS)

_BODY_RECIPE = "tests/fixtures/input-recipes/parity/union-body-tutorial-review.yaml"
_BODY_WORKFLOW = "tests/fixtures/workloads/union_body_tutorial_review.py"
_TAGGED_RECIPE = "tests/fixtures/input-recipes/parity/union-body-discriminator-upstream.yaml"
_TAGGED_FULL_SCHEMA_RECIPE = (
    "tests/fixtures/input-recipes/parity/union-body-discriminator-full-schema-review.yaml"
)
_ANNOTATED_RECIPE = (
    "tests/fixtures/input-recipes/parity/union-body-discriminator-annotated-review.yaml"
)
_FORMS_RECIPE = "tests/fixtures/input-recipes/parity/union-forms-tutorial-review.yaml"
_INHERITED_RECIPE = "tests/fixtures/input-recipes/parity/union-inherited-body-tutorial-review.yaml"
_ERROR_CONTEXT_RECIPE = (
    "tests/fixtures/input-recipes/parity/validation-error-context-exact-review.yaml"
)
_WEBSOCKET_VALIDATION_HANDLER_RECIPE = (
    "tests/fixtures/input-recipes/parity/websocket-validation-handler-wave.yaml"
)

_UNION_SOURCE_EVIDENCE = (*_FASTAPI_UNION_SOURCES, *_STARLETTE_TRANSPORT_SOURCES)
_ERROR_CONTEXT_SOURCE_EVIDENCE = (
    *_FASTAPI_ERROR_CONTEXT_SOURCES,
    *_STARLETTE_TRANSPORT_SOURCES,
)


UNION_ERROR_CONTEXT_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_union_body.py": _module(
        "tests/test_union_body.py",
        "The two branch requests use the test's exact JSON objects, and the OpenAPI case selects the full document plus HTTP status. Pydantic owns union model validation/schema; FastAPI owns body-field discovery and operation assembly; Starlette owns ASGI byte transport.",
        {
            "test_post_other_item": _function(
                "tests/test_union_body.py",
                "test_post_other_item",
                ("request-validation",),
                "The independent workload posts the exact price-only body to the same OtherItem | Item endpoint and observes status and response bytes.",
                (
                    _link(
                        _BODY_RECIPE,
                        "fastapi.request-union-body.tutorial.other-item",
                        ("post-other-item",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_post_item": _function(
                "tests/test_union_body.py",
                "test_post_item",
                ("request-validation",),
                "The independent workload posts the exact name-only body to the same union endpoint and observes status and response bytes.",
                (
                    _link(
                        _BODY_RECIPE,
                        "fastapi.request-union-body.tutorial.item",
                        ("post-item",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_openapi_schema": _function(
                "tests/test_union_body.py",
                "test_openapi_schema",
                ("openapi-docs", "request-validation"),
                "A GET of /openapi.json observes the full generated document and status for the same two-model union request body.",
                (
                    _link(
                        _BODY_RECIPE,
                        "fastapi.request-union-body.tutorial.openapi",
                        ("union-body-openapi",),
                        _UNION_OPENAPI,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
        },
        _UNION_SOURCE_EVIDENCE,
    ),
    "tests/test_union_body_discriminator.py": _module(
        "tests/test_union_body_discriminator.py",
        "The pinned test is one function containing two tagged JSON branch calls and a full OpenAPI snapshot. Its existing exact request actions are reused; a separate docs action selects the full OpenAPI document because the existing candidate selected only a subset of the snapshot.",
        {
            "test_discriminator_pydantic_v2": _function(
                "tests/test_union_body_discriminator.py",
                "test_discriminator_pydantic_v2",
                ("request-validation", "openapi-docs"),
                "Both query/body pairs are exact matches to the test. The existing recipe's selected schema pointers are supplemented with a full-document observation for the complete source snapshot.",
                (
                    _link(
                        _TAGGED_RECIPE,
                        "fastapi.request.explicit-tagged-union-body-discriminator-upstream",
                        ("first-tagged-union-branch", "other-tagged-union-branch"),
                        _UNION_HTTP,
                    ),
                    _link(
                        _TAGGED_FULL_SCHEMA_RECIPE,
                        "fastapi.request.explicit-tagged-union-body-discriminator.full-schema",
                        ("full-tagged-discriminator-openapi",),
                        _UNION_OPENAPI,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
        },
        _UNION_SOURCE_EVIDENCE,
    ),
    "tests/test_union_body_discriminator_annotated.py": _module(
        "tests/test_union_body_discriminator_annotated.py",
        "The callable Pydantic discriminator is exercised using both Body declaration forms, and the full OpenAPI document records their distinct request-schema projections.",
        {
            "test_union_body_discriminator_assignment": _function(
                "tests/test_union_body_discriminator_annotated.py",
                "test_union_body_discriminator_assignment",
                ("request-validation",),
                "The workload sends the exact cat discriminator object through the pet: Pet = Body() declaration and observes status/body.",
                (
                    _link(
                        _ANNOTATED_RECIPE,
                        "fastapi.request-union-body.callable-discriminator.assignment",
                        ("callable-discriminator-assignment-body",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_union_body_discriminator_annotated": _function(
                "tests/test_union_body_discriminator_annotated.py",
                "test_union_body_discriminator_annotated",
                ("request-validation",),
                "The workload sends the exact dog discriminator object through Annotated[Pet, Body()] and observes status/body.",
                (
                    _link(
                        _ANNOTATED_RECIPE,
                        "fastapi.request-union-body.callable-discriminator.annotated",
                        ("callable-discriminator-annotated-body",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_openapi_schema": _function(
                "tests/test_union_body_discriminator_annotated.py",
                "test_openapi_schema",
                ("openapi-docs", "request-validation"),
                "The docs action selects the full OpenAPI document for both assignment and Annotated body routes, including their anyOf/oneOf schema distinction.",
                (
                    _link(
                        _ANNOTATED_RECIPE,
                        "fastapi.request-union-body.callable-discriminator.openapi",
                        ("callable-discriminator-openapi",),
                        _UNION_OPENAPI,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
        },
        _UNION_SOURCE_EVIDENCE,
    ),
    "tests/test_union_forms.py": _module(
        "tests/test_union_forms.py",
        "URL-encoded inputs reproduce the two valid branches, mixed-field invalid input, missing form, and full OpenAPI snapshot. Starlette owns form parsing; FastAPI owns Form binding/error shaping and OpenAPI operation assembly.",
        {
            "test_post_user_form": _function(
                "tests/test_union_forms.py",
                "test_post_user_form",
                ("request-validation",),
                "The form payload is the source test's exact name/email pair; status and response bytes are selected.",
                (
                    _link(
                        _FORMS_RECIPE,
                        "fastapi.request-union-forms.tutorial.user",
                        ("post-user-form",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_post_company_form": _function(
                "tests/test_union_forms.py",
                "test_post_company_form",
                ("request-validation",),
                "The form payload is the source test's exact company_name/industry pair; status and response bytes are selected.",
                (
                    _link(
                        _FORMS_RECIPE,
                        "fastapi.request-union-forms.tutorial.company",
                        ("post-company-form",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_invalid_form_data": _function(
                "tests/test_union_forms.py",
                "test_invalid_form_data",
                ("request-validation", "public-api-errors"),
                "The workflow sends the exact mixed name/company_name form object; status and complete error response bytes are selected.",
                (
                    _link(
                        _FORMS_RECIPE,
                        "fastapi.request-union-forms.tutorial.invalid-mixed-fields",
                        ("post-invalid-mixed-form",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_empty_form": _function(
                "tests/test_union_forms.py",
                "test_empty_form",
                ("request-validation", "public-api-errors"),
                "The workflow sends an empty POST without a content-type header, matching the source call with no data argument.",
                (
                    _link(
                        _FORMS_RECIPE,
                        "fastapi.request-union-forms.tutorial.empty",
                        ("post-empty-form",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_openapi_schema": _function(
                "tests/test_union_forms.py",
                "test_openapi_schema",
                ("openapi-docs", "request-validation"),
                "The docs action selects the full OpenAPI document for the union form requestBody and its component schemas.",
                (
                    _link(
                        _FORMS_RECIPE,
                        "fastapi.request-union-forms.tutorial.openapi",
                        ("union-forms-openapi",),
                        _UNION_OPENAPI,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
        },
        _UNION_SOURCE_EVIDENCE,
    ),
    "tests/test_union_inherited_body.py": _module(
        "tests/test_union_inherited_body.py",
        "The exact extended and base JSON objects are sent to an inherited-model union, and the OpenAPI action selects the full generated document.",
        {
            "test_post_extended_item": _function(
                "tests/test_union_inherited_body.py",
                "test_post_extended_item",
                ("request-validation",),
                "The workflow sends the exact name/age object accepted as ExtendedItem and observes status/body.",
                (
                    _link(
                        _INHERITED_RECIPE,
                        "fastapi.request-union-body.inherited.extended-item",
                        ("post-extended-item",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_post_item": _function(
                "tests/test_union_inherited_body.py",
                "test_post_item",
                ("request-validation",),
                "The workflow sends the exact name-only base Item object and observes status/body.",
                (
                    _link(
                        _INHERITED_RECIPE,
                        "fastapi.request-union-body.inherited.base-item",
                        ("post-base-item",),
                        _UNION_HTTP,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
            "test_openapi_schema": _function(
                "tests/test_union_inherited_body.py",
                "test_openapi_schema",
                ("openapi-docs", "request-validation"),
                "The docs action selects the full OpenAPI document with both inherited union branch schemas.",
                (
                    _link(
                        _INHERITED_RECIPE,
                        "fastapi.request-union-body.inherited.openapi",
                        ("inherited-union-openapi",),
                        _UNION_OPENAPI,
                    ),
                ),
                _UNION_SOURCE_EVIDENCE,
            ),
        },
        _UNION_SOURCE_EVIDENCE,
    ),
    "tests/test_validation_error_context.py": _module(
        "tests/test_validation_error_context.py",
        "Five workflows reproduce the source route paths, endpoint names, response model failures, websocket invalid path values, and mounted sub-application cases. Two existing cases exercise explicit-path-only and empty endpoint contexts. The function named request-validation for /sub/items/ actually captures a ResponseValidationError, as its source handler and response_model route show.",
        {
            "test_request_validation_error_includes_endpoint_context": _function(
                "tests/test_validation_error_context.py",
                "test_request_validation_error_includes_endpoint_context",
                ("request-validation", "public-api-errors"),
                "The exact /users/invalid request selects the propagated RequestValidationError class and full message, including endpoint function/path context.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.request-endpoint",
                        ("invalid-user-path",),
                        _VALIDATION_EXCEPTION_SELECTORS,
                    ),
                ),
                _ERROR_CONTEXT_SOURCE_EVIDENCE,
            ),
            "test_response_validation_error_includes_endpoint_context": _function(
                "tests/test_validation_error_context.py",
                "test_response_validation_error_includes_endpoint_context",
                ("public-api-errors", "response-serialization"),
                "The exact /items/ route and missing response-model id select the propagated ResponseValidationError class/message and endpoint context.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.response-endpoint",
                        ("invalid-item-response",),
                        _VALIDATION_EXCEPTION_SELECTORS,
                    ),
                ),
                _ERROR_CONTEXT_SOURCE_EVIDENCE,
            ),
            "test_websocket_validation_error_includes_endpoint_context": _function(
                "tests/test_validation_error_context.py",
                "test_websocket_validation_error_includes_endpoint_context",
                ("request-validation", "public-api-errors"),
                "The exact invalid integer WebSocket path selects the propagated WebSocketRequestValidationError class/message and endpoint context. A second independent case registers a handler for that exception and observes only close/event behavior; it is a handler-dispatch variation grounded in the source test's exception type and the upstream custom WebSocket close-handler pattern, not a copy of either test's outputs.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.websocket-endpoint",
                        ("invalid-websocket-path",),
                        _VALIDATION_EXCEPTION_SELECTORS,
                    ),
                    _link(
                        _WEBSOCKET_VALIDATION_HANDLER_RECIPE,
                        "fastapi.websocket-validation.custom-handler-close",
                        ("invalid-path-custom-close",),
                        (
                            "websocket.close_code",
                            "websocket.close_reason",
                            "websocket.event_order",
                            "websocket.messages",
                        ),
                    ),
                ),
                (
                    *_ERROR_CONTEXT_SOURCE_EVIDENCE,
                    _source(
                        "fastapi/applications.py",
                        1000,
                        1012,
                        "FastAPI preserves a user-supplied WebSocketRequestValidationError handler while installing the default with setdefault",
                    ),
                    _source(
                        "fastapi/exception_handlers.py",
                        29,
                        34,
                        "FastAPI's default WebSocket validation handler closes with policy-violation code and encoded errors",
                    ),
                    _source(
                        "tests/test_ws_router.py",
                        257,
                        271,
                        "The pinned upstream test demonstrates a custom WebSocket exception handler closing with a selected code and reason",
                    ),
                ),
            ),
            "test_subapp_request_validation_error_includes_endpoint_context": _function(
                "tests/test_validation_error_context.py",
                "test_subapp_request_validation_error_includes_endpoint_context",
                ("response-serialization", "public-api-errors"),
                "Although named request validation, the source requests /sub/items/ from a response_model route that omits id; its registered handler captures ResponseValidationError. The workflow preserves the mounted path and error class/message.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.mounted-response-endpoint",
                        ("invalid-mounted-item-response",),
                        _VALIDATION_EXCEPTION_SELECTORS,
                    ),
                ),
                _ERROR_CONTEXT_SOURCE_EVIDENCE,
            ),
            "test_subapp_websocket_validation_error_includes_endpoint_context": _function(
                "tests/test_validation_error_context.py",
                "test_subapp_websocket_validation_error_includes_endpoint_context",
                ("request-validation", "public-api-errors"),
                "The exact /sub/ws/invalid WebSocket path selects the propagated validation exception and mounted endpoint path context.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.mounted-websocket-endpoint",
                        ("invalid-mounted-websocket-path",),
                        _VALIDATION_EXCEPTION_SELECTORS,
                    ),
                ),
                _ERROR_CONTEXT_SOURCE_EVIDENCE,
            ),
            "test_validation_error_with_only_path": _function(
                "tests/test_validation_error_context.py",
                "test_validation_error_with_only_path",
                ("public-api-errors",),
                "The route constructs the exact missing body/name error and path-only endpoint_ctx from the source test, then exposes str(error) as text for an ASGI body selector.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.path-only",
                        ("format-path-only-context",),
                        (*_UNION_HTTP, *_CONSTRUCTION_SELECTORS),
                    ),
                ),
                _ERROR_CONTEXT_SOURCE_EVIDENCE,
            ),
            "test_validation_error_with_no_context": _function(
                "tests/test_validation_error_context.py",
                "test_validation_error_with_no_context",
                ("public-api-errors",),
                "The route constructs the exact missing body/name error and empty endpoint_ctx from the source test, then exposes str(error) as text for an ASGI body selector.",
                (
                    _link(
                        _ERROR_CONTEXT_RECIPE,
                        "fastapi.validation-error-context.exact.empty-context",
                        ("format-empty-context",),
                        (*_UNION_HTTP, *_CONSTRUCTION_SELECTORS),
                    ),
                ),
                _ERROR_CONTEXT_SOURCE_EVIDENCE,
            ),
        },
        _ERROR_CONTEXT_SOURCE_EVIDENCE,
    ),
}

FUNCTION_DENOMINATORS = {
    test_path: len(_test_function_spans(test_path)) for test_path in TOP_LEVEL_TEST_MODULES
}
TOTAL_FUNCTION_DENOMINATOR = sum(FUNCTION_DENOMINATORS.values())


def _selectors_for_action(action: dict[str, Any]) -> set[str]:
    selectors: set[str] = set()
    for observation in action.get("observations", []):
        kind = observation.get("kind")
        if kind == "http_response":
            values = set(observation.get("selectors", []))
            if "status" in values:
                selectors.add("http.status")
            if "body" in values:
                selectors.add("http.body.bytes")
        elif kind == "openapi":
            selectors.add("openapi.document")
            if any(pointer.startswith("/paths/") for pointer in observation["json_pointers"]):
                selectors.add("openapi.paths")
        elif kind == "application_error" and observation.get("selector") == "exception":
            selectors.add("asgi.application_error.exception")
    return selectors


def validate_union_error_context_review_mappings() -> list[str]:
    """Statically check module/function denominators and linked workflow actions."""
    import yaml

    errors: list[str] = []
    if set(UNION_ERROR_CONTEXT_TEST_REVIEW_MAPPINGS) != set(TOP_LEVEL_TEST_MODULES):
        errors.append("review mapping keys differ from the declared six-module scope")

    recipe_cache: dict[str, dict[str, Any]] = {}
    for module_path, module in UNION_ERROR_CONTEXT_TEST_REVIEW_MAPPINGS.items():
        source_path = FASTAPI_ROOT / module_path
        if not source_path.is_file():
            errors.append(f"missing pinned FastAPI source module: {module_path}")
            continue
        actual_spans = _test_function_spans(module_path)
        if module.get("source_test_spans") != actual_spans:
            errors.append(f"source test function denominator changed: {module_path}")
        mapped_functions = module.get("functions", {})
        expected_names = {
            span["role"].removeprefix("pinned FastAPI 0.141.1 test function ")
            for span in actual_spans
        }
        if set(mapped_functions) != expected_names:
            errors.append(f"function mappings differ from source AST: {module_path}")

        for function_name, row in mapped_functions.items():
            if row.get("review_status") == "reviewed_excluded":
                if not row.get("exclusion_reason"):
                    errors.append(
                        f"source exclusion lacks rationale: {module_path}:{function_name}"
                    )
                continue
            if not row.get("workflow_cases"):
                errors.append(
                    f"test function has no workflow mapping: {module_path}:{function_name}"
                )
            for link in row.get("workflow_cases", []):
                recipe_path = link["recipe_path"]
                if recipe_path not in recipe_cache:
                    absolute = PROJECT_ROOT / recipe_path
                    if not absolute.is_file():
                        errors.append(f"missing linked input recipe: {recipe_path}")
                        continue
                    recipe_cache[recipe_path] = yaml.safe_load(absolute.read_text(encoding="utf-8"))
                cases = {
                    case.get("case_id"): case for case in recipe_cache[recipe_path].get("cases", [])
                }
                case = cases.get(link["case_id"])
                if case is None:
                    errors.append(f"missing linked input case: {recipe_path}::{link['case_id']}")
                    continue
                actions = {action.get("action_id"): action for action in case.get("actions", [])}
                if not set(link["action_ids"]) <= set(actions):
                    errors.append(
                        f"missing linked action: {recipe_path}::{link['case_id']} "
                        f"{sorted(set(link['action_ids']) - set(actions))}"
                    )
                    continue
                selected = {
                    f"construction.{selector}"
                    for selector in case.get("construction_observation", {}).get("selectors", [])
                }
                selected.update(
                    set().union(
                        *(
                            _selectors_for_action(actions[action_id])
                            for action_id in link["action_ids"]
                        )
                    )
                )
                if set(link["observation_selectors"]) != selected:
                    errors.append(
                        f"selector mapping differs from workflow: {module_path}:{function_name} "
                        f"declared={sorted(set(link['observation_selectors']))} "
                        f"actual={sorted(selected)}"
                    )
    return errors
