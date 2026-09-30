"""Source review for selected FastAPI OpenAPI/security test functions.

The mapping rows identify independently authored input workflows, or record
per-function scope exclusions. They do not claim parity results. Starlette
1.6.0 remains the sole generic ASGI/router/response oracle; Pydantic owns model
validation and generated model-schema details. FastAPI 0.141.1 owns the
OpenAPI assembly and FastAPI security integration represented here.
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
        "role": "sole generic ASGI routing, HTTP/WebSocket transport, and Response contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model validation/serialization and JSON Schema generation dependency",
    },
}

_OPENAPI_SCHEMAS = "tests/fixtures/input-recipes/parity/openapi-schemas.yaml"
_OPENAPI_OPERATIONS = "tests/fixtures/input-recipes/parity/openapi-operations.yaml"
_SECURITY_RECIPE = "tests/fixtures/input-recipes/parity/security_oauth_openapi_upstream.yaml"
_WEBHOOKS_RECIPE = "tests/fixtures/input-recipes/parity/webhooks-security.yaml"
_WEBHOOK_ROUTE_SEPARATION_RECIPE = (
    "tests/fixtures/input-recipes/parity/openapi-webhook-route-separation-source-review.yaml"
)
_EXAMPLES_RECIPE = (
    "tests/fixtures/input-recipes/parity/openapi-parameter-examples-source-review.yaml"
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(test_path: str, function_name: str) -> dict[str, Any]:
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
    starts = [node.lineno, *(decorator.lineno for decorator in node.decorator_list)]
    return _source(
        test_path,
        min(starts),
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test function {function_name} and its assertions",
    )


def _workflow(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
    coverage: str,
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
        "coverage": coverage,
    }


def _mapping(
    test_path: str,
    function_name: str,
    *,
    feature_ids: list[str],
    workflows: list[dict[str, Any]],
    rationale: str,
    contract_gate: str,
    supporting_sources: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    selectors = sorted(
        {selector for workflow in workflows for selector in workflow["observation_selectors"]}
    )
    return {
        "mapping_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": f"Partial: {contract_gate}",
        "workflow_cases": list(workflows),
        "stimulus_notes": (
            "The linked YAML recipes contain deterministic inputs and selected observations only; "
            "their workloads embed no expected outputs."
        ),
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            *supporting_sources,
        ],
    }


def _exclusion(
    test_path: str,
    function_name: str,
    reason: str,
    *,
    owner: str,
    supporting_sources: tuple[dict[str, Any], ...] = (),
    related_workflows: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    return {
        "source_span": _test_function_span(test_path, function_name),
        "reason": reason,
        "owner": owner,
        "related_workflows": list(related_workflows),
        "supporting_sources": list(supporting_sources),
    }


_OPENAPI_OPERATION_PARAMETERS = _source(
    "fastapi/openapi/utils.py",
    159,
    228,
    "FastAPI groups path/query/header/cookie fields and emits OpenAPI parameter example values",
)
_OPENAPI_REQUEST_BODY = _source(
    "fastapi/openapi/utils.py",
    231,
    263,
    "FastAPI creates the requestBody object and encodes Body.openapi_examples or Body.example",
)
_OPENAPI_EXTRA_MERGE = _source(
    "fastapi/openapi/utils.py",
    537,
    539,
    "FastAPI deep-merges APIRoute.openapi_extra into the generated operation",
)
_OPENAPI_PATHS_AND_SCHEMAS = _source(
    "fastapi/openapi/utils.py",
    618,
    674,
    "FastAPI gathers route/webhook fields, generates component definitions, and assembles paths/webhooks",
)
_OPENAPI_SECURITY = _source(
    "fastapi/openapi/utils.py",
    132,
    156,
    "FastAPI translates dependency security schemes and scopes into OpenAPI components and requirements",
)
_OPENAPI_SPLIT_SCHEMAS = _source(
    "fastapi/_compat/v2.py",
    254,
    345,
    "FastAPI selects validation/serialization model-field definitions and asks Pydantic GenerateJsonSchema to build them",
)
_OPENAPI_MODEL_NAMES = _source(
    "fastapi/_compat/v2.py",
    425,
    435,
    "FastAPI flattens model references and normalizes component names before OpenAPI generation",
)
_FASTAPI_OPENAPI_ENTRY = _source(
    "fastapi/applications.py",
    1070,
    1103,
    "FastAPI.openapi passes its registered routes, webhook routes, and split-schema option to get_openapi",
)
_FASTAPI_WEBHOOK_REGISTRATION = _source(
    "fastapi/applications.py",
    937,
    948,
    "FastAPI exposes a dedicated APIRouter for OpenAPI-only webhook operations",
)
_FASTAPI_APP_ROUTER = _source(
    "fastapi/applications.py",
    984,
    999,
    "FastAPI constructs the request router separately from its documentation-only webhook router",
)
_FASTAPI_ROUTE_OPENAPI_EXTRA = _source(
    "fastapi/routing.py",
    1188,
    1223,
    "FastAPI APIRoute accepts openapi_extra and passes it into route state",
)
_FASTAPI_HTTP_BEARER = _source(
    "fastapi/security/http.py",
    254,
    316,
    "FastAPI HTTPBearer defines the HTTP bearer security scheme and validates Authorization headers",
)
_FASTAPI_HTTP_BASE = _source(
    "fastapi/security/http.py",
    69,
    102,
    "FastAPI HTTPBase constructs the default 401 exception and parses Authorization credentials",
)
_FASTAPI_HTTP_EXCEPTION_HANDLER = _source(
    "fastapi/exception_handlers.py",
    11,
    17,
    "FastAPI maps HTTPException details into a JSON response body",
)
_FASTAPI_HTTP_EXCEPTION_REGISTRATION = _source(
    "fastapi/applications.py",
    1000,
    1006,
    "FastAPI registers its HTTPException and request-validation handlers",
)
_FASTAPI_RESPONSE_SERIALIZATION = _source(
    "fastapi/routing.py",
    301,
    342,
    "FastAPI validates and serializes response-model values through the field adapter or jsonable_encoder",
)
_FASTAPI_REQUEST_HANDLER = _source(
    "fastapi/routing.py",
    375,
    455,
    "FastAPI builds endpoint request handling and invokes dependency/body processing",
)
_STARLETTE_ROUTE_MATCHING = _source(
    "starlette/routing.py",
    242,
    258,
    "Starlette 1.6.0 performs generic HTTP path and method matching",
)
_STARLETTE_ROUTER_DISPATCH = _source(
    "starlette/routing.py",
    684,
    720,
    "Starlette 1.6.0 dispatches full/partial route matches and uses its default for misses",
)
_STARLETTE_RESPONSE = _source(
    "starlette/responses.py",
    29,
    75,
    "Starlette 1.6.0 owns generic Response status/body/header initialization and rendering",
)
_STARLETTE_JSON_RESPONSE = _source(
    "starlette/responses.py",
    181,
    201,
    "Starlette 1.6.0 JSONResponse renders the supplied content as JSON bytes",
)
_STARLETTE_RESPONSE_DISPATCH = _source(
    "starlette/responses.py",
    163,
    168,
    "Starlette 1.6.0 Response emits status, headers, and body as ASGI messages",
)
_STARLETTE_EXCEPTION_DISPATCH = _source(
    "starlette/middleware/exceptions.py",
    47,
    65,
    "Starlette 1.6.0 dispatches exceptions through the application's registered handlers",
)


_EXAMPLES_REQUEST_SMOKE = _workflow(
    _EXAMPLES_RECIPE,
    "fastapi.openapi.examples-parameter-locations.request-smoke",
    [
        "post-body-example",
        "get-path-example",
        "get-query-example",
        "get-header-example",
        "get-cookie-example",
    ],
    ["http.status"],
    "Valid request smoke probes at the five source parameter locations; only successful status is observed.",
)
_EXAMPLES_PARAMETER_OPENAPI = _workflow(
    _EXAMPLES_RECIPE,
    "fastapi.openapi.examples-parameter-locations.openapi",
    ["inspect-parameter-examples"],
    ["http.status", "openapi.document", "openapi.paths", "openapi.request_schema"],
    "Selected requestBody and parameter pointers for Body, Path, Query, Header, and Cookie examples.",
)
_WEBHOOK_ROUTE_SEPARATION = _workflow(
    _WEBHOOK_ROUTE_SEPARATION_RECIPE,
    "fastapi.openapi.webhooks.event-identifier-is-not-route",
    [
        "request-event-identifier-as-inbound-path",
        "inspect-separate-path-and-webhook-collections",
    ],
    ["http.status", "openapi.document", "openapi.paths"],
    "Probe the named webhook identifier as an inbound URL and inspect its separate OpenAPI webhook entry and path collection.",
)


OPENAPI_EXAMPLES_SECURITY_SOURCE_REVIEW = {
    "fastapi_identity": SOURCE_IDENTITIES["fastapi"],
    "starlette_identity": SOURCE_IDENTITIES["starlette"],
    "pydantic_identity": SOURCE_IDENTITIES["pydantic"],
    "ownership_notes": [
        "FastAPI 0.141.1 owns route/dependency projection into OpenAPI, operation extensions, parameter/body example placement, security requirements, and webhook registration. The FastAPI source checkout is oracle/dev-only; the target runtime must not import or depend on upstream FastAPI.",
        "Starlette 1.6.0 is the sole generic ASGI routing, HTTP transport, TestClient, and Response contract. HTTP request/response smoke checks do not assign generic router or response behavior to FastAPI.",
        "Pydantic 2.13.4 owns model validation/serialization and the model-schema fragments produced through its public schema generator. FastAPI owns when those fragments are selected, named, and inserted into paths/components, including the separate-input/output switch.",
    ],
    "input_only_additions": [
        {
            "recipe_path": _EXAMPLES_RECIPE,
            "workload_path": "tests/fixtures/workloads/openapi_parameter_examples_source_review.py",
            "case_ids": [
                "fastapi.openapi.examples-parameter-locations.openapi",
                "fastapi.openapi.examples-parameter-locations.request-smoke",
            ],
            "reason": "Existing active OpenAPI example inputs select request-body examples only; none observes OpenAPI examples attached to Path, Query, Header, and Cookie parameters.",
        }
    ],
    "modules": {
        "tests/test_openapi_examples.py": {
            "test_mappings": {
                "test_call_api": _mapping(
                    "tests/test_openapi_examples.py",
                    "test_call_api",
                    feature_ids=["app-routing", "request-validation"],
                    workflows=[_EXAMPLES_REQUEST_SMOKE],
                    rationale=(
                        "The source submits one valid request to each Body, Path, Query, Header, and Cookie route and checks each status. The new case uses the same five input locations with independently named routes and deterministic valid values."
                    ),
                    contract_gate=(
                        "This maps only five successful-status probes, not the source's response payloads or invalid-input branches. Generic route dispatch/HTTP response behavior remains Starlette 1.6.0-owned, and Pydantic owns model conversion."
                    ),
                    supporting_sources=(
                        _FASTAPI_REQUEST_HANDLER,
                        _STARLETTE_RESPONSE_DISPATCH,
                    ),
                ),
                "test_openapi_schema": _mapping(
                    "tests/test_openapi_examples.py",
                    "test_openapi_schema",
                    feature_ids=["openapi-docs", "request-validation"],
                    workflows=[_EXAMPLES_PARAMETER_OPENAPI],
                    rationale=(
                        "The new independent case samples two named examples and JSON Schema examples at Body, Path, Query, Header, and Cookie locations, covering the placement behavior highlighted by the snapshot. Existing active recipes sample body examples but do not observe parameter `openapi_examples` across the four parameter locations."
                    ),
                    contract_gate=(
                        "The workflow compares selected requestBody/parameter/model pointers from an independently authored app, not the complete FastAPI snapshot, its exact operation ids, all response/error-schema details, or every schema fragment. Pydantic owns generated model-schema fragments; FastAPI owns placement and encoding of the examples metadata."
                    ),
                    supporting_sources=(_OPENAPI_OPERATION_PARAMETERS, _OPENAPI_REQUEST_BODY),
                ),
            },
            "exclusions": {},
        },
        "tests/test_duplicate_models_openapi.py": {
            "test_mappings": {
                "test_openapi_schema": _mapping(
                    "tests/test_duplicate_models_openapi.py",
                    "test_openapi_schema",
                    feature_ids=["openapi-docs"],
                    workflows=[
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.duplicate-models-openapi.openapi-schema",
                            ["openapi"],
                            ["http.status", "openapi.document", "openapi.paths"],
                            "Repeated model references across path operations and nested component schemas.",
                        )
                    ],
                    rationale=(
                        "The source snapshot checks nested models reused at multiple schema locations. The existing independent schema workflow also selects all paths and component schemas and reuses shared model references across routes."
                    ),
                    contract_gate=(
                        "The selected roots cover paths and components/schemas for the independent workload, not the source's exact model fields, titles, or complete document metadata. FastAPI flattens/names model references; Pydantic supplies the generated schema details."
                    ),
                    supporting_sources=(
                        _OPENAPI_PATHS_AND_SCHEMAS,
                        _OPENAPI_MODEL_NAMES,
                        _OPENAPI_SPLIT_SCHEMAS,
                    ),
                )
            },
            "exclusions": {
                "test_get_api_route": _exclusion(
                    "tests/test_duplicate_models_openapi.py",
                    "test_get_api_route",
                    (
                        "This function only requests `/` and checks the status plus nested JSON response-model output; it does not inspect OpenAPI model reuse. Runtime response validation and serialization belong to the FastAPI response/Pydantic lane, while generic HTTP routing and response transport are Starlette-owned."
                    ),
                    owner="FastAPI response serialization and Pydantic model conversion; generic transport is Starlette-RS",
                    supporting_sources=(
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _STARLETTE_ROUTE_MATCHING,
                        _STARLETTE_RESPONSE,
                    ),
                )
            },
        },
        "tests/test_openapi_query_parameter_extension.py": {
            "test_mappings": {
                "test_openapi": _mapping(
                    "tests/test_openapi_query_parameter_extension.py",
                    "test_openapi",
                    feature_ids=["openapi-docs", "request-validation"],
                    workflows=[
                        _workflow(
                            _OPENAPI_OPERATIONS,
                            "fastapi.openapi.openapi-query-parameter-extension.openapi",
                            ["openapi"],
                            ["http.status", "openapi.document", "openapi.paths"],
                            "Selected generated query parameter list for a route with openapi_extra additions.",
                        )
                    ],
                    rationale=(
                        "The existing workflow observes the generated parameter array for a route combining a normal query parameter with openapi_extra parameters."
                    ),
                    contract_gate=(
                        "The case selects the parameter array, not the source's entire snapshot, operation metadata, validation-error schemas, or runtime query coercion. FastAPI owns the OpenAPI deep merge and parameter projection; Pydantic owns the ordinary typed query schema."
                    ),
                    supporting_sources=(
                        _OPENAPI_EXTRA_MERGE,
                        _FASTAPI_ROUTE_OPENAPI_EXTRA,
                        _OPENAPI_OPERATION_PARAMETERS,
                    ),
                )
            },
            "exclusions": {
                "test_get_route": _exclusion(
                    "tests/test_openapi_query_parameter_extension.py",
                    "test_get_route",
                    (
                        "The function only checks a 200 status and empty JSON body from a GET route; the declared extra query parameters are not sent and the empty response does not reveal the standard query default. The observable assertions are runtime routing/response behavior, not OpenAPI extension behavior."
                    ),
                    owner="Starlette-RS generic routing/Response contract; request parameter coercion is separately Pydantic/FastAPI-owned",
                    supporting_sources=(
                        _STARLETTE_ROUTE_MATCHING,
                        _STARLETTE_RESPONSE,
                        _STARLETTE_JSON_RESPONSE,
                        _STARLETTE_RESPONSE_DISPATCH,
                        _FASTAPI_REQUEST_HANDLER,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                    ),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_OPERATIONS,
                            "fastapi.openapi.openapi-query-parameter-extension.openapi",
                            ["openapi"],
                            ["http.status", "openapi.document", "openapi.paths"],
                            "Related OpenAPI operation case does not represent this runtime response assertion.",
                        ),
                    ),
                )
            },
        },
        "tests/test_openapi_route_extensions.py": {
            "test_mappings": {
                "test_openapi_schema": _mapping(
                    "tests/test_openapi_route_extensions.py",
                    "test_openapi_schema",
                    feature_ids=["openapi-docs"],
                    workflows=[
                        _workflow(
                            _OPENAPI_OPERATIONS,
                            "fastapi.openapi.openapi-route-extensions.openapi-schema",
                            ["openapi"],
                            ["http.status", "openapi.document", "openapi.paths"],
                            "Selected OpenAPI operation including the custom x- extension field.",
                        )
                    ],
                    rationale=(
                        "The existing operation pointer observes the route-specific custom extension in generated OpenAPI."
                    ),
                    contract_gate=(
                        "Only the selected path operation and status are compared; this is not a complete document snapshot or runtime route-response comparison. FastAPI owns storing/merging openapi_extra."
                    ),
                    supporting_sources=(_OPENAPI_EXTRA_MERGE, _FASTAPI_ROUTE_OPENAPI_EXTRA),
                )
            },
            "exclusions": {
                "test_get_route": _exclusion(
                    "tests/test_openapi_route_extensions.py",
                    "test_get_route",
                    (
                        "The function checks only the generic successful GET response status and empty JSON body; it does not observe the OpenAPI extension. The extension is separately mapped by the snapshot function."
                    ),
                    owner="Starlette-RS generic routing and Response behavior",
                    supporting_sources=(
                        _STARLETTE_ROUTE_MATCHING,
                        _STARLETTE_ROUTER_DISPATCH,
                        _STARLETTE_RESPONSE,
                        _STARLETTE_JSON_RESPONSE,
                        _STARLETTE_RESPONSE_DISPATCH,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                    ),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_OPERATIONS,
                            "fastapi.openapi.openapi-route-extensions.openapi-schema",
                            ["openapi"],
                            ["http.status", "openapi.document", "openapi.paths"],
                            "Related OpenAPI extension case; it does not represent this route response assertion.",
                        ),
                    ),
                )
            },
        },
        "tests/test_openapi_separate_input_output_schemas.py": {
            "test_mappings": {
                "test_openapi_schema": _mapping(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_openapi_schema",
                    feature_ids=["openapi-docs", "request-validation", "response-serialization"],
                    workflows=[
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Separate validation/serialization schema case selects paths, components and input/output request/response schema pointers.",
                        )
                    ],
                    rationale=(
                        "The existing case exercises FastAPI's default split-schema mode with nested optional models, a computed field, request bodies, normal responses, and an additional response model."
                    ),
                    contract_gate=(
                        "The independent workload is not the same application/model set and the selected pointers do not include every source snapshot field. FastAPI chooses validation/serialization definitions; Pydantic generates their model-schema content."
                    ),
                    supporting_sources=(
                        _FASTAPI_OPENAPI_ENTRY,
                        _OPENAPI_PATHS_AND_SCHEMAS,
                        _OPENAPI_SPLIT_SCHEMAS,
                    ),
                ),
                "test_openapi_schema_no_separate": _mapping(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_openapi_schema_no_separate",
                    feature_ids=["openapi-docs", "request-validation", "response-serialization"],
                    workflows=[
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema-no-separate",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Unsplit schema case selects the paths and component schema roots.",
                        )
                    ],
                    rationale=(
                        "The existing second-application OpenAPI endpoint is configured with separate_input_output_schemas=False and exposes its generated path/schema roots."
                    ),
                    contract_gate=(
                        "The workflow compares the source-generated schemas from an independently named model set, not every snapshot field. FastAPI selects the unsplit schema mode; Pydantic remains the model-schema generator."
                    ),
                    supporting_sources=(
                        _FASTAPI_OPENAPI_ENTRY,
                        _OPENAPI_PATHS_AND_SCHEMAS,
                        _OPENAPI_SPLIT_SCHEMAS,
                    ),
                ),
            },
            "exclusions": {
                "test_create_item": _exclusion(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_create_item",
                    (
                        "The function sends the same model payload to two apps with separate_input_output_schemas enabled/disabled, then compares their runtime status and serialized model body. That option is consumed by OpenAPI generation; this assertion is runtime validation/serialization, and no active input case compares two app configurations as a paired result."
                    ),
                    owner="FastAPI runtime request/response lane and Pydantic model conversion; OpenAPI split-schema behavior is mapped separately",
                    supporting_sources=(
                        _FASTAPI_REQUEST_HANDLER,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _FASTAPI_OPENAPI_ENTRY,
                    ),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Related schema-mode case; it does not compare runtime responses across two app configurations.",
                        ),
                    ),
                ),
                "test_create_item_with_sub": _exclusion(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_create_item_with_sub",
                    (
                        "This function compares nested default/omitted-field response serialization across split and unsplit app instances; its assertion is runtime Pydantic model output, not generated OpenAPI. No active input performs the cross-configuration response comparison."
                    ),
                    owner="FastAPI runtime response serialization and Pydantic model defaults",
                    supporting_sources=(
                        _FASTAPI_REQUEST_HANDLER,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _FASTAPI_OPENAPI_ENTRY,
                    ),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Related schema-mode case does not assert nested runtime serialization equivalence.",
                        ),
                    ),
                ),
                "test_create_item_list": _exclusion(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_create_item_list",
                    (
                        "The function compares list-body validation and serialized responses across split and unsplit apps. Those are runtime request/response and Pydantic behaviors; the schema recipe does not make a paired runtime assertion."
                    ),
                    owner="FastAPI runtime request/response lane and Pydantic model conversion",
                    supporting_sources=(
                        _FASTAPI_REQUEST_HANDLER,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _FASTAPI_OPENAPI_ENTRY,
                    ),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Related schema-mode case does not compare runtime list payloads.",
                        ),
                    ),
                ),
                "test_read_items": _exclusion(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_read_items",
                    (
                        "The function compares nested model serialization, optional values, and defaults for GET responses across split and unsplit apps. It observes runtime Pydantic output, not OpenAPI, and no active workflow pairs these app configurations."
                    ),
                    owner="FastAPI runtime response serialization and Pydantic model defaults",
                    supporting_sources=(_FASTAPI_RESPONSE_SERIALIZATION, _FASTAPI_OPENAPI_ENTRY),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Related schema-mode case does not inspect runtime GET response bodies.",
                        ),
                    ),
                ),
                "test_with_computed_field": _exclusion(
                    "tests/test_openapi_separate_input_output_schemas.py",
                    "test_with_computed_field",
                    (
                        "The function compares runtime computed-field serialization for a POST response across split and unsplit app configurations. Pydantic computes/serializes the field and the test does not request OpenAPI; the adjacent schema case separately observes computed-field input/output schemas."
                    ),
                    owner="FastAPI runtime response serialization and Pydantic computed-field behavior",
                    supporting_sources=(
                        _FASTAPI_REQUEST_HANDLER,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _FASTAPI_OPENAPI_ENTRY,
                    ),
                    related_workflows=(
                        _workflow(
                            _OPENAPI_SCHEMAS,
                            "fastapi.openapi.openapi-separate-input-output-schemas.openapi-schema",
                            ["openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.request_schema",
                            ],
                            "Related schema-mode case observes computed-field schema references, not computed-field runtime serialization.",
                        ),
                    ),
                ),
            },
        },
        "tests/test_top_level_security_scheme_in_openapi.py": {
            "test_mappings": {
                "test_get_root": _mapping(
                    "tests/test_top_level_security_scheme_in_openapi.py",
                    "test_get_root",
                    feature_ids=["dependency-security", "app-routing"],
                    workflows=[
                        _workflow(
                            _SECURITY_RECIPE,
                            "fastapi.security.test-top-level-security-scheme-in-openapi.test-get-root",
                            ["request"],
                            ["http.status", "http.body.bytes"],
                            "HTTPBearer-protected GET with a deterministic Bearer Authorization header.",
                        )
                    ],
                    rationale=(
                        "The existing case sends a valid Bearer header to the same root operation shape and observes the successful status/body. FastAPI owns HTTPBearer dependency behavior; Starlette owns generic transport and response emission."
                    ),
                    contract_gate=(
                        "This is a source-to-independent-app sample: the case checks raw response bytes rather than the source's parsed JSON convenience. It does not assign TestClient behavior to FastAPI."
                    ),
                    supporting_sources=(
                        _FASTAPI_HTTP_BASE,
                        _FASTAPI_HTTP_BEARER,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _STARLETTE_JSON_RESPONSE,
                        _STARLETTE_RESPONSE_DISPATCH,
                    ),
                ),
                "test_get_root_no_token": _mapping(
                    "tests/test_top_level_security_scheme_in_openapi.py",
                    "test_get_root_no_token",
                    feature_ids=["dependency-security", "app-routing"],
                    workflows=[
                        _workflow(
                            _SECURITY_RECIPE,
                            "fastapi.security.test-top-level-security-scheme-in-openapi.test-get-root-no-token",
                            ["request"],
                            ["http.status", "http.body.bytes"],
                            "HTTPBearer-protected GET without Authorization; observes the denial status/body.",
                        )
                    ],
                    rationale=(
                        "The existing case exercises missing credentials on the matching independent root route. FastAPI HTTPBearer raises the authentication exception and FastAPI's registered handler forms the JSON detail response; Starlette owns exception-handler dispatch and JSONResponse transport."
                    ),
                    contract_gate=(
                        "The recipe compares an independent workflow's raw status/body and does not claim TestClient identity or the entire security subsystem. FastAPI owns the HTTPBearer denial and JSON envelope; Starlette owns generic handler dispatch and response bytes."
                    ),
                    supporting_sources=(
                        _FASTAPI_HTTP_BASE,
                        _FASTAPI_HTTP_BEARER,
                        _FASTAPI_HTTP_EXCEPTION_HANDLER,
                        _FASTAPI_HTTP_EXCEPTION_REGISTRATION,
                        _FASTAPI_RESPONSE_SERIALIZATION,
                        _STARLETTE_EXCEPTION_DISPATCH,
                        _STARLETTE_JSON_RESPONSE,
                        _STARLETTE_RESPONSE_DISPATCH,
                    ),
                ),
                "test_openapi_schema": _mapping(
                    "tests/test_top_level_security_scheme_in_openapi.py",
                    "test_openapi_schema",
                    feature_ids=["openapi-docs", "dependency-security"],
                    workflows=[
                        _workflow(
                            _SECURITY_RECIPE,
                            "fastapi.security.test-top-level-security-scheme-in-openapi.test-openapi-schema",
                            ["request"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.paths",
                                "openapi.security",
                            ],
                            "Selected HTTPBearer component and operation security pointers from OpenAPI.",
                        )
                    ],
                    rationale=(
                        "The existing schema request selects the HTTPBearer security scheme and the root operation's security requirement. FastAPI derives both from the dependency graph and registered security object."
                    ),
                    contract_gate=(
                        "Only selected security pointers plus status are compared, not the source's full OpenAPI snapshot or all route/response fields. Starlette remains the generic HTTP oracle and Pydantic owns model-schema generation."
                    ),
                    supporting_sources=(
                        _OPENAPI_SECURITY,
                        _FASTAPI_HTTP_BEARER,
                        _FASTAPI_OPENAPI_ENTRY,
                    ),
                ),
            },
            "exclusions": {},
        },
        "tests/test_webhooks_security.py": {
            "test_mappings": {
                "test_openapi_schema": _mapping(
                    "tests/test_webhooks_security.py",
                    "test_openapi_schema",
                    feature_ids=["openapi-docs", "dependency-security"],
                    workflows=[
                        _workflow(
                            _WEBHOOKS_RECIPE,
                            "fastapi.webhooks.security.openapi-contract",
                            ["inspect-webhook-openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.request_schema",
                                "openapi.security",
                            ],
                            "Selected webhook requestBody, operation security, and HTTPBearer component pointers.",
                        ),
                        _WEBHOOK_ROUTE_SEPARATION,
                    ],
                    rationale=(
                        "The existing input registers a named webhook with a Pydantic request model and an HTTPBearer dependency, then selects its webhook operation, request body, and security components. A second independent input checks the documented distinction between webhook event identifiers and routable paths."
                    ),
                    contract_gate=(
                        "The security workflow selects requestBody/security pointers rather than the source's full OpenAPI document or Subscription field definitions. The additional workflow samples one event identifier, its absence from OpenAPI paths, and generic HTTP dispatch for that URL; it does not cover webhook delivery or all HTTP methods. FastAPI owns webhook registration and OpenAPI projection, Pydantic owns the referenced model schema, and Starlette 1.6.0 owns generic route misses and HTTP transport."
                    ),
                    supporting_sources=(
                        _FASTAPI_WEBHOOK_REGISTRATION,
                        _FASTAPI_APP_ROUTER,
                        _FASTAPI_OPENAPI_ENTRY,
                        _OPENAPI_PATHS_AND_SCHEMAS,
                        _OPENAPI_SECURITY,
                        _source(
                            "docs/en/docs/advanced/openapi-webhooks.md",
                            33,
                            47,
                            "The documented webhook identifier belongs to OpenAPI; users configure the actual receiving URL separately.",
                        ),
                        _STARLETTE_ROUTE_MATCHING,
                        _STARLETTE_ROUTER_DISPATCH,
                    ),
                )
            },
            "exclusions": {
                "test_dummy_webhook": _exclusion(
                    "tests/test_webhooks_security.py",
                    "test_dummy_webhook",
                    (
                        "The function directly constructs a Pydantic Subscription and calls the endpoint as an ordinary Python function. It makes no assertions, sends no ASGI request, and observes no webhook or OpenAPI behavior."
                    ),
                    owner="Pydantic model construction and non-observable direct-call coverage; no Starlette or FastAPI ASGI contract asserted",
                    supporting_sources=(_FASTAPI_WEBHOOK_REGISTRATION,),
                    related_workflows=(
                        _workflow(
                            _WEBHOOKS_RECIPE,
                            "fastapi.webhooks.security.openapi-contract",
                            ["inspect-webhook-openapi"],
                            [
                                "http.status",
                                "openapi.document",
                                "openapi.request_schema",
                                "openapi.security",
                            ],
                            "Related OpenAPI webhook contract does not represent the direct Python function call.",
                        ),
                    ),
                )
            },
        },
    },
}


__all__ = ["OPENAPI_EXAMPLES_SECURITY_SOURCE_REVIEW", "SOURCE_IDENTITIES"]
