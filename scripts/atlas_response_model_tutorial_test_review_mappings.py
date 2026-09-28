"""Function-level source review for FastAPI response-model tutorial tests.

The mappings point to pinned FastAPI 0.141.1 source and input-only parity
workflows. They are deliberately partial: response JSON assertions use exact
body bytes in current workflows, and existing OpenAPI cases select pointers
instead of storing source snapshot outputs.
"""

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
        "role": "sole generic ASGI, TestClient, response-class, and HTTP transport contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model validation, response-field serialization, and schema generation dependency",
    },
}

__all__ = ["RESPONSE_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


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
    start: int,
    end: int,
    feature_ids: tuple[str, ...],
    selectors: tuple[str, ...],
    rationale: str,
    links: tuple[dict[str, Any], ...],
    gate: str,
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    link_notes = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} "
        f"(actions: {', '.join(link['action_ids'])}; "
        f"selectors: {', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "stimulus_notes": (
            "Independent input-only recipe links: "
            + link_notes
            + ". Recipes hold inputs only, with no expected output or copied upstream test body."
        ),
        "workflow_cases": list(links),
        "supporting_sources": [
            _source(
                test_path,
                start,
                end,
                "pinned FastAPI 0.141.1 test function and asserted observations",
            ),
            *sources,
        ],
    }


def _module(rationale: str, functions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    links_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    sources_by_key: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in functions.values():
        for link in row["workflow_cases"]:
            links_by_key.setdefault((link["recipe_path"], link["case_id"]), link)
        for source in row["supporting_sources"]:
            key = (
                source["path"],
                source["start_line"],
                source["end_line"],
                source["role"],
            )
            sources_by_key.setdefault(key, source)
    links = list(links_by_key.values())
    return {
        "rationale": rationale,
        "supporting_sources": list(sources_by_key.values()),
        "workflow_cases": links,
        "module_observation_selectors": sorted(
            {selector for row in functions.values() for selector in row["observation_selectors"]}
        ),
        "stimulus_notes": (
            "Source-reviewed partial mapping to independent input-only cases: "
            + "; ".join(
                f"{link['recipe_path']}::{link['case_id']} "
                f"(actions: {', '.join(link['action_ids'])}; "
                f"selectors: {', '.join(link['observation_selectors'])})"
                for link in links
            )
            + ". FastAPI owns response-model selection, validation, filtering, and its OpenAPI projection. "
            "Pydantic owns model validation/serialization mechanics; generic TestClient and response "
            "transport behavior belongs to Starlette 1.6.0."
        ),
        "functions": functions,
    }


_RECIPE = "tests/fixtures/input-recipes/parity/response-model-tutorials-upstream.yaml"
_REVIEW_RECIPE = "tests/fixtures/input-recipes/parity/response-model-tutorial-review.yaml"
_PYDANTIC_RECIPE = "tests/fixtures/input-recipes/parity/pydantic-response-serialization-wave.yaml"
_JSON = ("http.status", "http.body.bytes")
_RESPONSE = ("http.status", "http.headers.ordered", "http.body.bytes")
_OPENAPI = ("openapi.document",)

_ROUTING_SERIALIZATION = (
    _source(
        "fastapi/routing.py",
        301,
        338,
        "FastAPI validates a response field and forwards include/exclude/unset options to its Pydantic serializer",
    ),
    _source(
        "fastapi/routing.py",
        727,
        739,
        "FastAPI passes route response-model projection options into response serialization",
    ),
)
_ROUTE_MODEL_SELECTION = (
    _source(
        "fastapi/routing.py",
        961,
        1007,
        "FastAPI accepts and stores response-model include, exclude, and unset configuration on a route",
    ),
    _source(
        "fastapi/routing.py",
        1081,
        1123,
        "FastAPI selects explicit/annotated response models, suppresses Response annotations, and creates response fields",
    ),
)
_OPENAPI_RESPONSE = (
    _source(
        "fastapi/openapi/utils.py",
        357,
        385,
        "FastAPI derives operation parameters and request-body schemas from route dependencies and body fields",
    ),
    _source(
        "fastapi/openapi/utils.py",
        419,
        472,
        "FastAPI projects response fields into generated OpenAPI response schemas",
    ),
)
_TESTCLIENT = (
    _source("fastapi/testclient.py", 1, 1, "FastAPI re-exports Starlette TestClient"),
    _source(
        "starlette/testclient.py",
        377,
        420,
        "Starlette 1.6.0 TestClient wraps the ASGI app and configures the HTTP client",
    ),
)
_STARLETTE_RESPONSES = (
    _source(
        "starlette/responses.py",
        163,
        170,
        "Starlette sends generic HTTP response-start and body ASGI messages",
    ),
    _source(
        "starlette/responses.py",
        181,
        201,
        "Starlette JSONResponse renders JSON bytes",
    ),
    _source(
        "starlette/responses.py",
        204,
        213,
        "Starlette RedirectResponse selects its default status and Location header",
    ),
)
_DIRECT_RESPONSE = (
    _source(
        "fastapi/routing.py",
        706,
        739,
        "FastAPI preserves returned Response instances and serializes other endpoint values through the selected response field",
    ),
    *_STARLETTE_RESPONSES,
)

_RESPONSE_GATE = (
    "The upstream function parses response.json() and compares a JSON value. The supported workflow "
    "selector is exact http.body.bytes, which is stricter about JSON formatting and key order; "
    "http.body.json is planned and cannot yet express the source comparison directly."
)
_OPENAPI_GATE = (
    "The upstream function compares a full OpenAPI document snapshot and asserts HTTP status 200. "
    "The linked recipe selects the listed JSON pointers only and does not observe that HTTP status; "
    "the complete snapshot, unselected components/fields, and status assertion are not claimed."
)
_RESPONSE_AND_HEADERS_GATE = (
    "The upstream function asserts status and the Location header only. The workflow also compares "
    "ordered headers and exact response body bytes, which are stricter generic Starlette response "
    "observations; body and header order are not source assertions."
)


RESPONSE_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS = {
    "tests/test_tutorial/test_response_model/test_tutorial001_tutorial001_01.py": _module(
        "The parametrized module checks explicit response_model and inferred return-annotation response models for list output, full input models, omitted defaults, and OpenAPI snapshots.",
        {
            "test_read_items": _function(
                "tests/test_tutorial/test_response_model/test_tutorial001_tutorial001_01.py",
                24,
                42,
                ("response-serialization",),
                _JSON,
                "Both source app variants return a list whose missing optional/default fields are populated by response-model validation and serialization.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial001-defaults-and-list-output",
                        ("list-items-with-model-defaults",),
                        _JSON,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial001-explicit-and-inferred",
                        ("list-items-with-inferred-model-defaults",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial001_py310.py",
                        9,
                        27,
                        "Item model and explicit list response_model route",
                    ),
                    _source(
                        "docs_src/response_model/tutorial001_01_py310.py",
                        7,
                        25,
                        "Item model and list return-annotation inference",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_create_item": _function(
                "tests/test_tutorial/test_response_model/test_tutorial001_tutorial001_01.py",
                45,
                55,
                ("response-serialization",),
                _JSON,
                "The source sends all optional fields and checks the model returned by both the explicit response_model and inferred return-annotation routes.",
                (
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial001-explicit-and-inferred",
                        (
                            "create-explicit-model-with-all-fields",
                            "create-inferred-model-with-all-fields",
                        ),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial001_py310.py",
                        9,
                        19,
                        "Item body and explicit response_model endpoint",
                    ),
                    _source(
                        "docs_src/response_model/tutorial001_01_py310.py",
                        7,
                        17,
                        "Item body and response type inferred from the return annotation",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_create_item_only_required": _function(
                "tests/test_tutorial/test_response_model/test_tutorial001_tutorial001_01.py",
                58,
                73,
                ("response-serialization",),
                _JSON,
                "The source omits optional input fields and checks that response-model serialization emits their None and empty-list defaults for both app variants.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial001-defaults-and-list-output",
                        ("create-item-with-omitted-optional-fields",),
                        _JSON,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial001-explicit-and-inferred",
                        ("create-inferred-model-with-required-fields",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial001_py310.py",
                        9,
                        19,
                        "Optional Item fields and explicit response_model endpoint",
                    ),
                    _source(
                        "docs_src/response_model/tutorial001_01_py310.py",
                        7,
                        17,
                        "Optional Item fields and annotation-inferred endpoint",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial001_tutorial001_01.py",
                76,
                200,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots request, response, validation-error, component, and route metadata for the two app variants.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial001-defaults-and-list-output",
                        ("item-request-and-response-schema",),
                        _OPENAPI,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial001-explicit-and-inferred",
                        ("explicit-and-inferred-model-openapi-shapes",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial001_py310.py",
                        9,
                        27,
                        "Explicit response-model list and item endpoints",
                    ),
                    _source(
                        "docs_src/response_model/tutorial001_01_py310.py",
                        7,
                        25,
                        "Annotation-inferred list and item endpoints",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial002.py": _module(
        "The module checks a request/response model reused for user creation, including its sensitive field, and a full OpenAPI snapshot.",
        {
            "test_post_user": _function(
                "tests/test_tutorial/test_response_model/test_tutorial002.py",
                23,
                35,
                ("response-serialization",),
                _JSON,
                "The same UserIn model validates the request and shapes the response, so the password field remains present by design.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial002-same-model-retains-sensitive-field",
                        ("create-user-with-shared-input-output-model",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial002_py310.py",
                        7,
                        17,
                        "Shared user input and output model route",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial002.py",
                38,
                137,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the request body, response schema, and shared user model schema.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial002-same-model-retains-sensitive-field",
                        ("shared-model-openapi-shape",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial002_py310.py",
                        7,
                        17,
                        "Shared model request body and response route",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial003.py": _module(
        "The module verifies that an explicit output model filters a password from a richer input model, then snapshots OpenAPI.",
        {
            "test_post_user": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003.py",
                23,
                38,
                ("response-serialization",),
                _JSON,
                "FastAPI validates the richer UserIn request but serializes the returned value through UserOut, which omits password.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-explicit-output-model-filters-input",
                        ("create-user-with-distinct-output-model",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_py310.py",
                        9,
                        24,
                        "Input and output models differ by the password field",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003.py",
                41,
                157,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots separate input and output schemas for a single operation.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-explicit-output-model-filters-input",
                        ("input-and-output-model-openapi-shape",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_py310.py",
                        9,
                        24,
                        "Input/output model declarations and explicit response_model",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial003_01.py": _module(
        "The module verifies output filtering inferred from a BaseUser return annotation instead of an explicit response_model, then snapshots OpenAPI.",
        {
            "test_post_user": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_01.py",
                23,
                38,
                ("response-serialization",),
                _JSON,
                "The request uses UserIn, while the BaseUser return annotation becomes the output model and removes password.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-01-return-annotation-filters-derived-input",
                        ("create-user-using-output-return-annotation",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_01_py310.py",
                        7,
                        19,
                        "Derived request model and base-model return annotation",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_01.py",
                41,
                157,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the input and output schemas inferred from the parameter and return annotation.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-01-return-annotation-filters-derived-input",
                        ("return-annotation-openapi-shape",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_01_py310.py",
                        7,
                        19,
                        "Base/derived models and inferred return-model route",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial003_02.py": _module(
        "The module uses a Response return annotation to permit JSONResponse and RedirectResponse values and snapshots the inferred OpenAPI shape.",
        {
            "test_get_portal": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_02.py",
                9,
                12,
                ("response-serialization",),
                _JSON,
                "The false/default query branch returns a concrete JSONResponse under a Response annotation; FastAPI does not build a response model from that annotation.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-02-response-annotation-allows-response-values",
                        ("portal-json-response",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_02_py310.py",
                        7,
                        11,
                        "Response-annotated endpoint returns JSONResponse or RedirectResponse",
                    ),
                    *_DIRECT_RESPONSE,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_get_redirect": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_02.py",
                15,
                18,
                ("response-serialization",),
                _RESPONSE,
                "The true query branch returns RedirectResponse under the same Response annotation; source checks status and Location with redirects disabled.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-02-response-annotation-allows-response-values",
                        ("portal-redirect-response",),
                        _RESPONSE,
                    ),
                ),
                _RESPONSE_AND_HEADERS_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_02_py310.py",
                        7,
                        11,
                        "Response annotation and conditional redirect return",
                    ),
                    *_DIRECT_RESPONSE,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_02.py",
                21,
                100,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the boolean query parameter and Response-annotated operation schema.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-02-response-annotation-allows-response-values",
                        ("response-annotation-openapi-shape",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_02_py310.py",
                        7,
                        11,
                        "Response return annotation and query parameter",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial003_03.py": _module(
        "The module verifies a RedirectResponse return annotation inferred as a direct Response instead of a response model, then snapshots OpenAPI.",
        {
            "test_get_portal": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_03.py",
                9,
                12,
                ("response-serialization",),
                _RESPONSE,
                "A RedirectResponse return annotation suppresses response-model construction; the source checks status and Location with redirect following disabled.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-03-redirect-response-return-annotation",
                        ("annotated-redirect-endpoint",),
                        _RESPONSE,
                    ),
                ),
                _RESPONSE_AND_HEADERS_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_03_py310.py",
                        7,
                        9,
                        "RedirectResponse endpoint return annotation",
                    ),
                    *_DIRECT_RESPONSE,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_03.py",
                15,
                37,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the schema generated for an endpoint annotated with RedirectResponse.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-03-redirect-response-return-annotation",
                        ("redirect-annotation-openapi-shape",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_03_py310.py",
                        7,
                        9,
                        "RedirectResponse annotation and return",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial003_05.py": _module(
        "The module checks a union response annotation with explicit response_model=None, for both a JSON mapping and RedirectResponse, then snapshots OpenAPI.",
        {
            "test_get_portal": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_05.py",
                23,
                26,
                ("response-serialization",),
                _JSON,
                "Explicit response_model=None suppresses model construction for the Response | dict return annotation while the mapping uses the configured JSON response class.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-05-explicitly-disabled-response-model",
                        ("union-return-json-response",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_05_py310.py",
                        7,
                        11,
                        "Explicitly disabled response model and union return values",
                    ),
                    *_DIRECT_RESPONSE,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_get_redirect": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_05.py",
                29,
                32,
                ("response-serialization",),
                _RESPONSE,
                "Explicit response_model=None allows the Response | dict endpoint to return RedirectResponse; the source checks status and Location.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-05-explicitly-disabled-response-model",
                        ("union-return-redirect-response",),
                        _RESPONSE,
                    ),
                ),
                _RESPONSE_AND_HEADERS_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_05_py310.py",
                        7,
                        11,
                        "Disabled response model on a conditional union return",
                    ),
                    *_DIRECT_RESPONSE,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial003_05.py",
                35,
                114,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the operation and boolean query parameter while response_model is explicitly disabled.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial003-05-explicitly-disabled-response-model",
                        ("disabled-response-model-openapi-shape",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial003_05_py310.py",
                        7,
                        11,
                        "response_model=None and Response | dict return annotation",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial004.py": _module(
        "The parametrized module checks response_model_exclude_unset with omitted fields, explicit fields, explicit null, and explicit model-default values, then snapshots OpenAPI.",
        {
            "test_get": _function(
                "tests/test_tutorial/test_response_model/test_tutorial004.py",
                43,
                46,
                ("response-serialization",),
                _JSON,
                "The source has three URL/data variants. Existing cases cover omitted and explicitly supplied non-default values; the new baz case covers explicit null plus values equal to model defaults.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial004-exclude-unset-preserves-explicit-fields",
                        (
                            "item-with-defaults-omitted-in-return-value",
                            "item-with-explicit-default-like-values",
                        ),
                        _JSON,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial004-explicit-null-defaults",
                        ("read-record-with-explicit-null-and-default-values",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial004_py310.py",
                        7,
                        24,
                        "Item defaults, three source data states, and response_model_exclude_unset",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial004.py",
                49,
                148,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots the route's response model and path parameter schema.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial004-exclude-unset-preserves-explicit-fields",
                        ("exclude-unset-response-schema",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial004_py310.py",
                        7,
                        24,
                        "Response model and exclude_unset route declaration",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial005.py": _module(
        "The module checks set-based response_model_include/exclude filtering for two routes and snapshots their OpenAPI schemas.",
        {
            "test_read_item_name": _function(
                "tests/test_tutorial/test_response_model/test_tutorial005.py",
                23,
                26,
                ("response-serialization",),
                _JSON,
                "The name route selects name and description with response_model_include; its current independent case uses the same include fields and observes exact bytes.",
                (
                    _link(
                        _PYDANTIC_RECIPE,
                        "fastapi.pydantic-response-serialization-wave.response-field-filter.test-read-item-name",
                        ("dispatch",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial005_py310.py",
                        7,
                        32,
                        "Item model data and set-based response_model_include route",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_read_item_public_data": _function(
                "tests/test_tutorial/test_response_model/test_tutorial005.py",
                29,
                36,
                ("response-serialization",),
                _JSON,
                "The public route excludes tax from the response model and observes the remaining fields.",
                (
                    _link(
                        _PYDANTIC_RECIPE,
                        "fastapi.pydantic-response-serialization-wave.response-field-filter.test-read-item-public-data",
                        ("dispatch",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial005_py310.py",
                        7,
                        37,
                        "Item model data and set-based response_model_exclude route",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial005.py",
                39,
                166,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots both include/exclude route operations and the shared model component. The existing pointer case covers the include response only; a new case observes both responses and the component.",
                (
                    _link(
                        _PYDANTIC_RECIPE,
                        "fastapi.pydantic-response-serialization-wave.response-field-filter.test-openapi-schema",
                        ("dispatch",),
                        _OPENAPI,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial005-openapi-filtered-routes",
                        ("filtered-route-openapi-schema",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial005_py310.py",
                        7,
                        37,
                        "Model component and both filtered response routes",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
    "tests/test_tutorial/test_response_model/test_tutorial006.py": _module(
        "The module checks list-based response_model_include/exclude filters and snapshots the generated schemas.",
        {
            "test_read_item_name": _function(
                "tests/test_tutorial/test_response_model/test_tutorial006.py",
                23,
                26,
                ("response-serialization",),
                _JSON,
                "The source passes a list of field names to response_model_include. The pre-existing workflow uses a set; a new distinct case uses the list form with independent values.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial006-include-and-exclude-top-level-fields",
                        ("include-name-and-description",),
                        _JSON,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial006-list-based-filters",
                        ("include-selected-fields-from-list-option",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial006_py310.py",
                        7,
                        32,
                        "Item model data and list-based response_model_include route",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_read_item_public_data": _function(
                "tests/test_tutorial/test_response_model/test_tutorial006.py",
                29,
                36,
                ("response-serialization",),
                _JSON,
                "The source passes a list to response_model_exclude. The existing workflow uses a set; the new case exercises list-valued exclusion directly.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial006-include-and-exclude-top-level-fields",
                        ("exclude-tax",),
                        _JSON,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial006-list-based-filters",
                        ("exclude-selected-fields-from-list-option",),
                        _JSON,
                    ),
                ),
                _RESPONSE_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial006_py310.py",
                        7,
                        37,
                        "Item model data and list-based response_model_exclude route",
                    ),
                    *_ROUTING_SERIALIZATION,
                    *_ROUTE_MODEL_SELECTION,
                    *_TESTCLIENT,
                ),
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_response_model/test_tutorial006.py",
                39,
                166,
                ("openapi-docs",),
                _OPENAPI,
                "The source snapshots both filtered operations and their shared response component.",
                (
                    _link(
                        _RECIPE,
                        "fastapi.response-model.tutorial006-include-and-exclude-top-level-fields",
                        ("include-exclude-model-schema",),
                        _OPENAPI,
                    ),
                    _link(
                        _REVIEW_RECIPE,
                        "fastapi.response-model-review.tutorial006-list-based-filters",
                        ("list-based-filter-openapi-shapes",),
                        _OPENAPI,
                    ),
                ),
                _OPENAPI_GATE,
                (
                    _source(
                        "docs_src/response_model/tutorial006_py310.py",
                        7,
                        37,
                        "List-valued include/exclude route declarations and shared schema",
                    ),
                    *_OPENAPI_RESPONSE,
                    *_TESTCLIENT,
                ),
            ),
        },
    ),
}
