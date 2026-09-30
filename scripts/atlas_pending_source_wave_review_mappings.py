"""Function-level source review for the pending FastAPI 0.141.1 atlas wave.

Every test function below has an independent YAML workflow link. The linked
workloads are oracle-side input applications only; they are not imported by the
``fastapi`` target facade and do not add FastAPI to target dependencies.
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
        "role": (
            "isolated source-oracle and development evidence only; FastAPI is not a target "
            "runtime dependency or import"
        ),
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole authority for generic ASGI transport, routing, responses, and TestClient",
    },
    "python": {
        "version": "CPython 3.12.13",
        "role": "pinned source-oracle and ASGI worker runtime",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model validation, byte handling, and JSON Schema dependency",
    },
}

__all__ = ["PENDING_SOURCE_WAVE_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(path: str, name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {name} in pinned source {path}")
    node = matches[0]
    start = min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)])
    return _source(
        path,
        start,
        node.end_lineno or node.lineno,
        f"FastAPI 0.141.1 test function {name} and its asserted behavior",
    )


def _link(recipe: str, case_id: str, selectors: tuple[str, ...]) -> dict[str, Any]:
    return {
        "recipe_path": recipe,
        "case_ids": [case_id],
        "observation_selectors": list(selectors),
    }


def _function(
    test_path: str,
    name: str,
    *,
    features: tuple[str, ...],
    selectors: tuple[str, ...],
    rationale: str,
    links: tuple[dict[str, Any], ...],
    sources: tuple[dict[str, Any], ...],
    gate: str,
) -> dict[str, Any]:
    source_span = _test_span(test_path, name)
    return {
        "feature_ids": list(features),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + gate,
        "source_span": source_span,
        "supporting_sources": [source_span, *sources],
        "workflow_cases": list(links),
        "stimulus_notes": (
            "The linked YAML workflow selects an independently authored input workload and stores "
            "no expected outputs. Oracle and target workers load that workload in separate "
            "processes: the oracle uses pinned upstream FastAPI, while the target resolves the "
            "public fastapi facade to direct native re-exports. Upstream FastAPI remains outside "
            "the target runtime dependency/import graph; Rust owns FastAPI behavior and control flow."
        ),
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
    *,
    exclusions: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    workflows: dict[tuple[str, str], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for row in functions.values():
        for link in row["workflow_cases"]:
            for case_id in link["case_ids"]:
                key = (link["recipe_path"], case_id)
                current = workflows.setdefault(
                    key,
                    {
                        "recipe_path": link["recipe_path"],
                        "case_ids": [case_id],
                        "observation_selectors": set(),
                    },
                )
                current["observation_selectors"].update(link["observation_selectors"])
        for source in row["supporting_sources"]:
            key = (
                source["path"],
                source["start_line"],
                source["end_line"],
                source["role"],
            )
            sources.setdefault(key, source)

    module_links = [
        {
            **link,
            "observation_selectors": sorted(link["observation_selectors"]),
        }
        for _key, link in sorted(workflows.items())
    ]
    return {
        "rationale": rationale,
        "module_observation_selectors": sorted(
            {selector for row in functions.values() for selector in row["observation_selectors"]}
        ),
        "supporting_sources": list(sources.values()),
        "workflow_cases": module_links,
        "stimulus_notes": (
            "Reviewed module links point to independent YAML workflows and workload modules "
            "loaded separately by oracle and target workers. FastAPI 0.141.1 source is "
            "development/oracle-only: the source worker uses upstream FastAPI, while the target "
            "worker uses the direct-native-re-export fastapi facade. Rust owns FastAPI control "
            "flow and the target must not import or depend on upstream FastAPI."
        ),
        "source_review_scope_exclusions": list(exclusions),
        "functions": functions,
    }


_OPENAPI_RECIPE = "tests/fixtures/input-recipes/parity/atlas-pending-openapi-source-wave.yaml"
_ID_RECIPE = "tests/fixtures/input-recipes/parity/atlas-pending-operation-ids-source-wave.yaml"
_CALLBACK_RECIPE = "tests/fixtures/input-recipes/parity/atlas-pending-callbacks-source-wave.yaml"
_SWAGGER_RECIPE = "tests/fixtures/input-recipes/parity/atlas-pending-swagger-ui-source-wave.yaml"
_TUTORIAL_RECIPE = "tests/fixtures/input-recipes/parity/atlas-pending-tutorials-source-wave.yaml"

_OPENAPI = ("openapi.document",)
_HTTP_JSON = ("http.status", "http.body.json")
_HTTP_STATUS = ("http.status",)
_HTTP_HTML = ("http.body.bytes",)
_HTTP_STREAM = ("http.status", "http.headers.ordered", "http.body.bytes")
_PYTHON_DIRECT_API_WARNING = ("python.call_outcome", "python.warnings")

_ROUTE_ID = _source(
    "fastapi/utils.py",
    95,
    100,
    "FastAPI builds the default operation ID from the route name, path, and first method",
)
_ROUTE_ID_ASSIGNMENT = _source(
    "fastapi/routing.py",
    1011,
    1028,
    "FastAPI stores and invokes the route-specific ID callable while constructing APIRoute",
)
_ROUTER_ID_INHERITANCE = _source(
    "fastapi/routing.py",
    1306,
    1367,
    "FastAPI resolves include and nested-router unique-ID function inheritance",
)
_OPENAPI_ID_WARNING = _source(
    "fastapi/openapi/utils.py",
    287,
    308,
    "FastAPI adds operationId to OpenAPI and emits a Python warning for duplicate IDs",
)
_OPENAPI_PARAMETERS = _source(
    "fastapi/openapi/utils.py",
    159,
    228,
    "FastAPI flattens dependency parameters and projects path/query/header/cookie examples",
)
_OPENAPI_REQUEST_BODY = _source(
    "fastapi/openapi/utils.py",
    231,
    263,
    "FastAPI projects Body example and openapi_examples metadata onto requestBody content",
)
_OPENAPI_MODELS = _source(
    "fastapi/openapi/utils.py",
    565,
    582,
    "FastAPI gathers request, response, dependency, and callback fields before schema generation",
)
_MODEL_DEFINITIONS = _source(
    "fastapi/_compat/v2.py",
    285,
    346,
    "FastAPI asks Pydantic for field definitions and truncates Pydantic model descriptions at form feed",
)
_MODEL_FIELD_SCHEMA = _source(
    "fastapi/_compat/v2.py",
    254,
    282,
    "FastAPI selects the Pydantic validation or serialization schema for an OpenAPI field",
)
_DEPENDENCY_PARAMETER_DEDUP = _source(
    "fastapi/dependencies/utils.py",
    169,
    195,
    "FastAPI traverses dependency fields once and flattens the effective OpenAPI parameters",
)
_CALLBACKS_OPENAPI = _source(
    "fastapi/openapi/utils.py",
    386,
    402,
    "FastAPI recursively generates callback operations and attaches them to the owning operation",
)
_CALLBACK_FIELDS = _source(
    "fastapi/openapi/utils.py",
    565,
    582,
    "FastAPI includes callback route fields while building model schemas",
)
_SWAGGER_ESCAPE = _source(
    "fastapi/openapi/docs.py",
    9,
    19,
    "FastAPI JSON-escapes HTML-sensitive characters in Swagger UI configuration",
)
_SWAGGER_HTML = _source(
    "fastapi/openapi/docs.py",
    148,
    194,
    "FastAPI merges UI parameters and serializes Swagger UI OAuth and HTML configuration",
)
_ROUTE_DESCRIPTION = _source(
    "fastapi/routing.py",
    1034,
    1037,
    "FastAPI extracts endpoint documentation and truncates route descriptions at form feed",
)
_JSONL_SERIALIZATION = _source(
    "fastapi/routing.py",
    647,
    682,
    "FastAPI recognizes sync/async JSONL generators and serializes each item with a newline",
)
_STARLETTE_STREAMING = _source(
    "starlette/responses.py",
    222,
    283,
    "Starlette owns StreamingResponse status/header framing, chunk sends, disconnect handling, and background execution",
)
_STARLETTE_SLASH = _source(
    "starlette/routing.py",
    704,
    718,
    "Starlette Router implements optional slash redirects for unmatched HTTP paths",
)
_STARLETTE_TESTCLIENT = _source(
    "starlette/testclient.py",
    277,
    291,
    "Starlette TestClient constructs the generic HTTP ASGI scope used by upstream tests",
)
_STARLETTE_CLIENT_CONFIG = _source(
    "starlette/testclient.py",
    377,
    420,
    "Starlette TestClient delegates cookie-jar and redirect-follow policy to its HTTP client",
)
_PYDANTIC_OPENAPI = _source(
    "fastapi/_compat/v2.py",
    285,
    346,
    "FastAPI delegates model JSON Schema generation to pinned Pydantic 2.13.4",
)


PENDING_SOURCE_WAVE_REVIEW_MAPPINGS = {
    "tests/test_generate_unique_id_function.py": _module(
        "The tests exercise FastAPI operation-ID generation at app, router, include, nested-router, path-operation, and callback scopes.",
        {
            "test_top_level_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_top_level_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The app-level ID function is inherited by a plain included router and appears in each OpenAPI operation.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTE_ID, _ROUTE_ID_ASSIGNMENT, _ROUTER_ID_INHERITANCE),
                gate="The input selects operation metadata and route paths; it does not reproduce the source test's response-model and additional-response schema matrix.",
            ),
            "test_router_overrides_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_router_overrides_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="A router-level ID function takes precedence over the app-level function for its included route.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTE_ID_ASSIGNMENT, _ROUTER_ID_INHERITANCE),
                gate="One route in each inheritance branch is represented; the original response-model snapshots are not carried into input recipes.",
            ),
            "test_router_include_overrides_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_router_include_overrides_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="An include_router ID override replaces the router default for directly included routes.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTER_ID_INHERITANCE, _ROUTE_ID_ASSIGNMENT),
                gate="The independent router tree samples direct include precedence and leaves the source test's full response-schema snapshots unclaimed.",
            ),
            "test_subrouter_top_level_include_overrides_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_subrouter_top_level_include_overrides_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="Nested include context preserves the child router's explicit ID function while applying an outer override to its direct parent route.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTER_ID_INHERITANCE, _ROUTE_ID_ASSIGNMENT),
                gate="The new nested route tree checks the precedence boundary but does not copy the source's model and response definitions.",
            ),
            "test_router_path_operation_overrides_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_router_path_operation_overrides_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="A path-operation ID function on a router route takes precedence over both the router default and app default.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTE_ID_ASSIGNMENT, _ROUTER_ID_INHERITANCE),
                gate="The OpenAPI path selection proves declared operation IDs; the source's additional response-model schema is outside this compact workflow.",
            ),
            "test_app_path_operation_overrides_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_app_path_operation_overrides_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="An app path-operation ID function takes precedence over the app-level default.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTE_ID_ASSIGNMENT,),
                gate="The input selects route metadata and does not replicate all source response-model details.",
            ),
            "test_callback_override_generate_unique_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_callback_override_generate_unique_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The callback operation and its owning route each use path-operation ID overrides in generated OpenAPI.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTE_ID_ASSIGNMENT, _CALLBACKS_OPENAPI),
                gate="The selected callback metadata is independent; the source test's response-model schema matrix is not asserted by this recipe.",
            ),
            "test_warn_duplicate_operation_id": _function(
                "tests/test_generate_unique_id_function.py",
                "test_warn_duplicate_operation_id",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The input emits duplicate operation IDs in the OpenAPI document using an independent router with a constant ID callable.",
                links=(
                    _link(
                        _ID_RECIPE,
                        "fastapi.pending.operation-ids-source-wave.openapi-identifiers",
                        _OPENAPI,
                    ),
                ),
                sources=(_ROUTE_ID_ASSIGNMENT, _OPENAPI_ID_WARNING),
                gate="The ASGI observation selector can compare duplicate IDs in OpenAPI but cannot capture Python UserWarning records or their message. The source warning assertion is therefore not claimed as parity-covered.",
            ),
        },
        exclusions=(
            {
                "scope": "unrepresented warning observation inside a mapped test function",
                "test_functions": {
                    "test_warn_duplicate_operation_id": _test_span(
                        "tests/test_generate_unique_id_function.py",
                        "test_warn_duplicate_operation_id",
                    )
                },
                "reason": "The current Python/ASGI workflow observation set has no Python warning-capture selector; only duplicate operation IDs in the public OpenAPI document are mapped.",
                "supporting_sources": [_OPENAPI_ID_WARNING],
            },
        ),
    ),
    "tests/test_modules_same_name_body/test_main.py": _module(
        "Same-named endpoint functions and multi-body request validation are exercised through two independently included routers.",
        {
            "test_post": _function(
                "tests/test_modules_same_name_body/test_main.py",
                "test_post",
                features=("app-routing", "request-validation", "response-serialization"),
                selectors=_HTTP_JSON,
                rationale="Valid independently authored requests reach two same-named endpoint functions with two embedded body fields.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.same-named-body-success",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "tests/test_modules_same_name_body/app/a.py",
                        1,
                        8,
                        "First router declares a two-field JSON body endpoint",
                    ),
                    _source(
                        "tests/test_modules_same_name_body/app/b.py",
                        1,
                        8,
                        "Second router declares a same-named endpoint with a distinct route path",
                    ),
                    _source(
                        "fastapi/routing.py",
                        413,
                        432,
                        "FastAPI collects and parses a route body before dependency and endpoint execution",
                    ),
                ),
                gate="The ASGI input selects canonical route paths. Starlette TestClient redirect-follow behavior for the two slash variants is outside the workflow and is not part of this mapping.",
            ),
            "test_post_invalid": _function(
                "tests/test_modules_same_name_body/test_main.py",
                "test_post_invalid",
                features=("request-validation", "public-api-errors"),
                selectors=_HTTP_JSON,
                rationale="An invalid integer field is submitted independently to each same-named multi-body operation.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.same-named-body-invalid",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "tests/test_modules_same_name_body/app/a.py",
                        6,
                        8,
                        "First route's Body declarations and endpoint response",
                    ),
                    _source(
                        "tests/test_modules_same_name_body/app/b.py",
                        6,
                        8,
                        "Second route's same-named Body declarations and endpoint response",
                    ),
                    _source(
                        "fastapi/routing.py",
                        413,
                        432,
                        "FastAPI parses request body values before Pydantic field validation",
                    ),
                ),
                gate="The workflow observes status and body for canonical route paths; Starlette TestClient slash redirects are not selected.",
            ),
            "test_openapi_schema": _function(
                "tests/test_modules_same_name_body/test_main.py",
                "test_openapi_schema",
                features=("openapi-docs", "request-validation"),
                selectors=_OPENAPI,
                rationale="The OpenAPI input selects each route's requestBody and generated per-route embedded-body schema.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.same-named-body-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_OPENAPI_MODELS, _MODEL_DEFINITIONS),
                gate="The independent routes cover same-name operation/body model derivation but omit the Python test package/module-name collision mechanism.",
            ),
        },
        exclusions=(
            {
                "scope": "test-client slash-redirect behavior only",
                "test_functions": {
                    name: _test_span("tests/test_modules_same_name_body/test_main.py", name)
                    for name in ("test_post", "test_post_invalid")
                },
                "reason": "The source tests submit both slash forms and rely on Starlette TestClient's redirect policy. The workflows use canonical route paths; Router slash redirects are separately owned by Starlette 1.6.0.",
                "supporting_sources": [
                    _STARLETTE_SLASH,
                    _STARLETTE_TESTCLIENT,
                    _source(
                        "tests/test_modules_same_name_body/app/a.py",
                        6,
                        8,
                        "Canonical slashless route",
                    ),
                    _source(
                        "tests/test_modules_same_name_body/app/b.py", 6, 8, "Canonical slash route"
                    ),
                ],
            },
            {
                "scope": "Python test package import-name collision behavior",
                "test_functions": {
                    "test_openapi_schema": _test_span(
                        "tests/test_modules_same_name_body/test_main.py",
                        "test_openapi_schema",
                    )
                },
                "reason": "The independent workflows exercise route registration and body schemas; Python's import resolution for test_main.py and app modules is a test layout property, not a FastAPI consumer API.",
                "supporting_sources": [
                    _source(
                        "tests/test_modules_same_name_body/test_main.py",
                        1,
                        6,
                        "Test module imports the app from a nested package",
                    ),
                    _source(
                        "tests/test_modules_same_name_body/app/main.py",
                        1,
                        8,
                        "Application module imports and includes two router modules",
                    ),
                ],
            },
        ),
    ),
    "tests/test_no_schema_split.py": _module(
        "Nested Pydantic models and enum defaults are projected into an OpenAPI document and returned through a model response.",
        {
            "test_create_message": _function(
                "tests/test_no_schema_split.py",
                "test_create_message",
                features=("response-serialization", "request-validation"),
                selectors=_HTTP_JSON,
                rationale="A query value flows into a nested Pydantic response model and is serialized through the route.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.nested-model-request",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "fastapi/routing.py",
                        301,
                        341,
                        "FastAPI validates and serializes endpoint response data",
                    ),
                ),
                gate="The route response is independently modeled; the separate complete snapshot of every nested schema field is linked to the OpenAPI case.",
            ),
            "test_openapi_schema": _function(
                "tests/test_no_schema_split.py",
                "test_openapi_schema",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The selected paths and component definitions cover nested model properties, enum defaults, and response references.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.nested-model-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_OPENAPI_MODELS, _MODEL_DEFINITIONS),
                gate="Pydantic supplies nested model JSON Schema; this workflow samples the selected route and referenced components rather than every source-snapshot field.",
            ),
        },
    ),
    "tests/test_openapi_model_description_trim_on_formfeed.py": _module(
        "A Pydantic model description containing a form-feed separator is projected through FastAPI OpenAPI generation.",
        {
            "test_openapi": _function(
                "tests/test_openapi_model_description_trim_on_formfeed.py",
                "test_openapi",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The OpenAPI pointer selects the named component description produced from a model docstring containing a form feed.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.form-feed-schema-description",
                        _OPENAPI,
                    ),
                ),
                sources=(_MODEL_DEFINITIONS, _MODEL_FIELD_SCHEMA),
                gate="The selected pointer isolates the description projection; other model-schema fields are outside this specific source test.",
            ),
        },
    ),
    "tests/test_repeated_dependency_schema.py": _module(
        "The HTTP route and OpenAPI operation share one header parameter through a repeated dependency graph.",
        {
            "test_response": _function(
                "tests/test_repeated_dependency_schema.py",
                "test_response",
                features=("dependency-security", "response-serialization"),
                selectors=_HTTP_JSON,
                rationale="The independently declared direct and nested dependencies receive one request header and contribute both values to the response.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.repeated-dependency-header",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "fastapi/dependencies/utils.py",
                        586,
                        731,
                        "FastAPI traverses and executes subdependencies for an HTTP request",
                    ),
                ),
                gate="The input exercises one successful header value and dependency graph; it does not claim all cache, override, or failure combinations.",
            ),
            "test_openapi_schema": _function(
                "tests/test_repeated_dependency_schema.py",
                "test_openapi_schema",
                features=("openapi-docs", "dependency-security"),
                selectors=_OPENAPI,
                rationale="The OpenAPI pointer selects the route's flattened header list and represents its deduplicated shared dependency parameter.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.repeated-dependency-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_DEPENDENCY_PARAMETER_DEDUP, _OPENAPI_PARAMETERS),
                gate="The selected parameter list is the source test's primary invariant; the rest of the document is not claimed as a full snapshot.",
            ),
        },
    ),
    "tests/test_schema_extra_examples.py": _module(
        "The module samples model-level JSON Schema examples, request-body examples, and path/query/header/cookie example metadata.",
        {
            "test_call_api": _function(
                "tests/test_schema_extra_examples.py",
                "test_call_api",
                features=("request-validation", "response-serialization"),
                selectors=(*_HTTP_STATUS, *_PYTHON_DIRECT_API_WARNING),
                rationale="Valid requests sample parameter locations with example metadata, and direct public-call probes observe their deprecated-example warnings.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.examples-request-smoke",
                        _HTTP_STATUS,
                    ),
                    *(
                        _link(
                            "tests/fixtures/input-recipes/parity/direct-api-warnings.yaml",
                            case_id,
                            _PYTHON_DIRECT_API_WARNING,
                        )
                        for case_id in (
                            "fastapi.deprecation.body-example-warning",
                            "fastapi.deprecation.path-example-warning",
                            "fastapi.deprecation.query-example-warning",
                            "fastapi.deprecation.header-example-warning",
                            "fastapi.deprecation.cookie-example-warning",
                        )
                    ),
                ),
                sources=(
                    _source(
                        "tests/test_schema_extra_examples.py",
                        9,
                        213,
                        "Source route declarations use Pydantic schema_extra and FastAPI parameter example fields",
                    ),
                ),
                gate="The direct API cases cover one legacy example warning per public parameter factory; example-plus-examples precedence combinations and the complete route matrix remain partial.",
            ),
            "test_openapi_schema": _function(
                "tests/test_schema_extra_examples.py",
                "test_openapi_schema",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="Selected OpenAPI pointers cover model-level examples, Body examples, and parameter examples at five HTTP locations.",
                links=(
                    _link(
                        _OPENAPI_RECIPE,
                        "fastapi.pending.openapi-source-wave.examples-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_OPENAPI_PARAMETERS, _OPENAPI_REQUEST_BODY, _PYDANTIC_OPENAPI),
                gate="The independent recipe selects modern examples and model extra metadata, not every deprecated example-plus-examples precedence combination; representative constructor warnings are linked from the create_app warning assertions.",
            ),
        },
    ),
    "tests/test_sub_callbacks.py": _module(
        "A subrouter route and inherited callbacks are represented in request behavior and OpenAPI callback entries.",
        {
            "test_get": _function(
                "tests/test_sub_callbacks.py",
                "test_get",
                features=("app-routing", "request-validation", "response-serialization"),
                selectors=_HTTP_JSON,
                rationale="A valid invoice request reaches a route included through a subrouter and returns its response body.",
                links=(
                    _link(
                        _CALLBACK_RECIPE,
                        "fastapi.pending.callbacks-source-wave.invoice-request",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "fastapi/routing.py",
                        2915,
                        2963,
                        "FastAPI router route registration appends route-level callbacks",
                    ),
                ),
                gate="The HTTP case observes the route request/response only; callback execution itself is documentation-only in FastAPI.",
            ),
            "test_openapi_schema": _function(
                "tests/test_sub_callbacks.py",
                "test_openapi_schema",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The selected callback subtree includes both a route callback and a callback inherited from the subrouter include.",
                links=(
                    _link(
                        _CALLBACK_RECIPE,
                        "fastapi.pending.callbacks-source-wave.callback-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_CALLBACKS_OPENAPI, _CALLBACK_FIELDS, _ROUTER_ID_INHERITANCE),
                gate="The workflow selects callback metadata under one operation; the source's full OpenAPI snapshot is not copied into the recipe.",
            ),
        },
        exclusions=(
            {
                "scope": "outbound callback delivery",
                "test_functions": {
                    "test_get": _test_span("tests/test_sub_callbacks.py", "test_get"),
                    "test_openapi_schema": _test_span(
                        "tests/test_sub_callbacks.py", "test_openapi_schema"
                    ),
                },
                "reason": "FastAPI callback definitions are OpenAPI documentation for a future client/server interaction; the source tests do not send an outbound callback request and the independent workflow does not invent one.",
                "supporting_sources": [
                    _source(
                        "tests/test_sub_callbacks.py",
                        43,
                        45,
                        "Callback endpoint is a schema declaration and contains no outbound request logic",
                    ),
                    _CALLBACKS_OPENAPI,
                ],
            },
        ),
    ),
    "tests/test_swagger_ui_escape.py": _module(
        "The public Swagger UI HTML helper escapes script-sensitive and markup-sensitive configuration values while preserving regular OAuth configuration.",
        {
            "test_init_oauth_html_chars_are_escaped": _function(
                "tests/test_swagger_ui_escape.py",
                "test_init_oauth_html_chars_are_escaped",
                features=("openapi-docs",),
                selectors=_HTTP_HTML,
                rationale="The selected raw HTML body contains the helper's JSON-escaped OAuth configuration for script-sensitive characters.",
                links=(
                    _link(
                        _SWAGGER_RECIPE,
                        "fastapi.pending.swagger-ui-source-wave.oauth-html-escaping",
                        _HTTP_HTML,
                    ),
                ),
                sources=(_SWAGGER_ESCAPE, _SWAGGER_HTML),
                gate="The source directly invokes get_swagger_ui_html; the independent ASGI workflow wraps that returned HTMLResponse in a route and compares body bytes, so direct-call signature/error behavior is not claimed.",
            ),
            "test_swagger_ui_parameters_html_chars_are_escaped": _function(
                "tests/test_swagger_ui_escape.py",
                "test_swagger_ui_parameters_html_chars_are_escaped",
                features=("openapi-docs",),
                selectors=_HTTP_HTML,
                rationale="The raw response bytes select the HTML-safe JSON encoding of a Swagger UI parameter containing markup characters.",
                links=(
                    _link(
                        _SWAGGER_RECIPE,
                        "fastapi.pending.swagger-ui-source-wave.parameter-html-escaping",
                        _HTTP_HTML,
                    ),
                ),
                sources=(_SWAGGER_ESCAPE, _SWAGGER_HTML),
                gate="The route wrapper compares the helper output bytes; direct Python call signature and exception behavior remain outside the ASGI input lane.",
            ),
            "test_normal_init_oauth_still_works": _function(
                "tests/test_swagger_ui_escape.py",
                "test_normal_init_oauth_still_works",
                features=("openapi-docs",),
                selectors=_HTTP_HTML,
                rationale="The HTML body includes ordinary OAuth initialization values and the ui.initOAuth call.",
                links=(
                    _link(
                        _SWAGGER_RECIPE,
                        "fastapi.pending.swagger-ui-source-wave.normal-oauth-config",
                        _HTTP_HTML,
                    ),
                ),
                sources=(_SWAGGER_HTML,),
                gate="The source assertions are represented by one exact HTML byte observation through a route wrapper; helper call errors are not asserted.",
            ),
        },
    ),
    "tests/test_tutorial/test_cookie_params/test_tutorial001.py": _module(
        "Cookie parameter extraction, optionality, and OpenAPI placement are tested for default-value and Annotated tutorial declarations.",
        {
            "test": _function(
                "tests/test_tutorial/test_cookie_params/test_tutorial001.py",
                "test",
                features=("request-validation", "response-serialization"),
                selectors=_HTTP_JSON,
                rationale="The input sends absent, present, extra, and unrelated cookie values to both independently declared optional cookie routes.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.cookie-parameter-cases",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "docs_src/cookie_params/tutorial001_py310.py",
                        1,
                        8,
                        "Default-value Cookie parameter tutorial route",
                    ),
                    _source(
                        "docs_src/cookie_params/tutorial001_an_py310.py",
                        1,
                        9,
                        "Annotated Cookie parameter tutorial route",
                    ),
                    _OPENAPI_PARAMETERS,
                ),
                gate="The ASGI workflow supplies explicit Cookie headers instead of exercising Starlette TestClient's cookie jar; cookie extraction and optional defaults remain the selected FastAPI behavior.",
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_cookie_params/test_tutorial001.py",
                "test_openapi_schema",
                features=("openapi-docs", "request-validation"),
                selectors=_OPENAPI,
                rationale="The selected parameter pointers identify an optional cookie parameter for both annotation styles.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.cookie-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_OPENAPI_PARAMETERS, _MODEL_FIELD_SCHEMA),
                gate="The selected OpenAPI parameter entries and schema pointers replace the full document snapshot; TestClient construction is not part of the input.",
            ),
        },
        exclusions=(
            {
                "scope": "Starlette TestClient cookie-jar and slash-redirect behavior",
                "test_functions": {
                    "test": _test_span(
                        "tests/test_tutorial/test_cookie_params/test_tutorial001.py",
                        "test",
                    )
                },
                "reason": "The source test uses TestClient(cookies=...) and requests /items while the tutorial routes are declared at /items/. The workflow supplies explicit Cookie headers at canonical route paths and maps FastAPI cookie extraction/optionality; client cookie persistence and optional slash redirects are Starlette-owned.",
                "supporting_sources": [
                    _STARLETTE_CLIENT_CONFIG,
                    _STARLETTE_SLASH,
                    _source(
                        "docs_src/cookie_params/tutorial001_py310.py",
                        6,
                        8,
                        "Default-value tutorial declares the slash-suffixed cookie route",
                    ),
                    _source(
                        "docs_src/cookie_params/tutorial001_an_py310.py",
                        8,
                        10,
                        "Annotated tutorial declares the slash-suffixed cookie route",
                    ),
                ],
            },
        ),
    ),
    "tests/test_tutorial/test_json_base64_bytes/test_tutorial001.py": _module(
        "Pydantic byte fields configured for base64 validation and serialization pass through FastAPI request and response models.",
        {
            "test_post_data": _function(
                "tests/test_tutorial/test_json_base64_bytes/test_tutorial001.py",
                "test_post_data",
                features=("request-validation", "response-serialization"),
                selectors=_HTTP_JSON,
                rationale="A JSON base64 string is accepted as a bytes request field and the route returns a decoded text value.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.base64-byte-exchange",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "docs_src/json_base64_bytes/tutorial001_py310.py",
                        5,
                        10,
                        "Pydantic input bytes model config selects base64 JSON validation",
                    ),
                    _source(
                        "docs_src/json_base64_bytes/tutorial001_py310.py",
                        32,
                        35,
                        "FastAPI route consumes validated byte field",
                    ),
                ),
                gate="Pydantic owns base64 value decoding; this mapping covers FastAPI's request-model path and route response, not arbitrary byte encodings.",
            ),
            "test_get_data": _function(
                "tests/test_tutorial/test_json_base64_bytes/test_tutorial001.py",
                "test_get_data",
                features=("response-serialization",),
                selectors=_HTTP_JSON,
                rationale="The route serializes a bytes response-model field using its Pydantic base64 configuration.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.base64-byte-exchange",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "docs_src/json_base64_bytes/tutorial001_py310.py",
                        12,
                        16,
                        "Pydantic output bytes model config selects base64 JSON serialization",
                    ),
                    _source(
                        "docs_src/json_base64_bytes/tutorial001_py310.py",
                        38,
                        41,
                        "FastAPI route returns the configured output model",
                    ),
                ),
                gate="Byte base64 encoding is Pydantic-owned; FastAPI response-field serialization and JSON response generation are selected.",
            ),
            "test_post_data_in_out": _function(
                "tests/test_tutorial/test_json_base64_bytes/test_tutorial001.py",
                "test_post_data_in_out",
                features=("request-validation", "response-serialization"),
                selectors=_HTTP_JSON,
                rationale="A round-trip model applies Pydantic base64 decoding on input and encoding on output.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.base64-byte-exchange",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "docs_src/json_base64_bytes/tutorial001_py310.py",
                        19,
                        27,
                        "Pydantic round-trip model config combines base64 validation and serialization",
                    ),
                    _source(
                        "docs_src/json_base64_bytes/tutorial001_py310.py",
                        44,
                        46,
                        "FastAPI route returns the typed byte model",
                    ),
                ),
                gate="The one round-trip input samples a single base64 value; Pydantic defines byte conversion semantics.",
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_json_base64_bytes/test_tutorial001.py",
                "test_openapi_schema",
                features=("openapi-docs",),
                selectors=_OPENAPI,
                rationale="The selected route and model pointers describe the three byte-field request/response schemas and operation structure.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.base64-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(_OPENAPI_MODELS, _PYDANTIC_OPENAPI, _MODEL_FIELD_SCHEMA),
                gate="The workflow selects OpenAPI paths and byte models; the byte JSON Schema encoding annotations themselves are generated by Pydantic.",
            ),
        },
    ),
    "tests/test_tutorial/test_sql_databases/test_tutorial002.py": _module(
        "A deterministic in-memory analogue samples FastAPI route validation, response models, status handling, pagination parameters, and OpenAPI projection from the SQL tutorial.",
        {
            "test_crud_app": _function(
                "tests/test_tutorial/test_sql_databases/test_tutorial002.py",
                "test_crud_app",
                features=(
                    "app-routing",
                    "request-validation",
                    "response-serialization",
                    "public-api-errors",
                ),
                selectors=_HTTP_JSON,
                rationale="An input-only route sequence samples create/list/page/update/read/delete and missing-record HTTP behavior with independently authored in-memory data.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.sql-application-requests",
                        _HTTP_JSON,
                    ),
                ),
                sources=(
                    _source(
                        "docs_src/sql_databases/tutorial002_py310.py",
                        45,
                        102,
                        "Source tutorial application and CRUD endpoint declarations",
                    ),
                    _source(
                        "fastapi/routing.py",
                        413,
                        473,
                        "FastAPI request parsing, dependency resolution, and response validation/serialization",
                    ),
                ),
                gate="The independent app uses Pydantic models and deterministic in-memory state. SQLModel metadata, SQLite transactions/generated IDs, SQLAlchemy queries, fixture reload, startup table creation, and TestClient lifespan are explicitly outside this FastAPI behavior slice.",
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_sql_databases/test_tutorial002.py",
                "test_openapi_schema",
                features=("openapi-docs", "request-validation"),
                selectors=_OPENAPI,
                rationale="Selected paths and model components cover the CRUD route declarations, response models, request fields, and query parameter projection.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.sql-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(
                    _OPENAPI_MODELS,
                    _MODEL_FIELD_SCHEMA,
                    _PYDANTIC_OPENAPI,
                    _source(
                        "docs_src/sql_databases/tutorial002_py310.py",
                        5,
                        26,
                        "SQLModel tutorial model declarations adapted as Pydantic workload inputs",
                    ),
                ),
                gate="The input uses Pydantic model equivalents to isolate FastAPI route/OpenAPI assembly; SQLModel's table/field generation and the full source schema snapshot are not claimed.",
            ),
        },
        exclusions=(
            {
                "scope": "database, SQLModel, and fixture lifecycle implementation",
                "test_functions": {
                    "test_crud_app": _test_span(
                        "tests/test_tutorial/test_sql_databases/test_tutorial002.py",
                        "test_crud_app",
                    ),
                    "test_openapi_schema": _test_span(
                        "tests/test_tutorial/test_sql_databases/test_tutorial002.py",
                        "test_openapi_schema",
                    ),
                },
                "reason": "The recipe deliberately maps FastAPI's HTTP request/response and OpenAPI boundaries; database state, SQLModel table metadata, SQLAlchemy/SQLite transaction semantics, reload/cleanup, and TestClient lifespan are external tutorial concerns.",
                "supporting_sources": [
                    _source(
                        "tests/test_tutorial/test_sql_databases/test_tutorial002.py",
                        16,
                        50,
                        "Test fixture clears SQLModel metadata, reloads the tutorial module, installs SQLite StaticPool, and enters TestClient lifespan",
                    ),
                    _source(
                        "docs_src/sql_databases/tutorial002_py310.py",
                        5,
                        43,
                        "SQLModel model classes, SQLite engine, table setup, and yielded Session dependency",
                    ),
                    _source(
                        "docs_src/sql_databases/tutorial002_py310.py",
                        53,
                        102,
                        "SQLModel session CRUD and database transaction implementation",
                    ),
                ],
            },
        ),
    ),
    "tests/test_tutorial/test_stream_json_lines/test_tutorial001.py": _module(
        "Four typed/untyped and sync/async generator routes are reviewed for collected JSONL bytes and generated stream-item OpenAPI schemas.",
        {
            "test_stream_items": _function(
                "tests/test_tutorial/test_stream_json_lines/test_tutorial001.py",
                "test_stream_items",
                features=("response-serialization",),
                selectors=_HTTP_STREAM,
                rationale="Four independent requests compare status, ordered headers, and the collected JSONL response bytes from sync/async typed and untyped generators.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.jsonl-stream-responses",
                        _HTTP_STREAM,
                    ),
                ),
                sources=(
                    _JSONL_SERIALIZATION,
                    _STARLETTE_STREAMING,
                    _source(
                        "docs_src/stream_json_lines/tutorial001_py310.py",
                        9,
                        42,
                        "Tutorial item model and typed/untyped sync/async generators",
                    ),
                ),
                gate="Collected output bytes and media type are represented; ASGI chunk boundaries, backpressure, client disconnect timing, and TestClient response collection are owned by Starlette and not observed here.",
            ),
            "test_openapi_schema": _function(
                "tests/test_tutorial/test_stream_json_lines/test_tutorial001.py",
                "test_openapi_schema",
                features=("openapi-docs", "response-serialization"),
                selectors=_OPENAPI,
                rationale="The selected document pointers cover all four streaming operations and the shared typed stream-item component.",
                links=(
                    _link(
                        _TUTORIAL_RECIPE,
                        "fastapi.pending.tutorials-source-wave.jsonl-openapi",
                        _OPENAPI,
                    ),
                ),
                sources=(
                    _JSONL_SERIALIZATION,
                    _OPENAPI_MODELS,
                    _MODEL_FIELD_SCHEMA,
                    _source(
                        "fastapi/openapi/utils.py",
                        411,
                        435,
                        "FastAPI adds JSONL response media type and itemSchema to OpenAPI",
                    ),
                ),
                gate="The selected paths and component capture the stream-item contract; generic StreamingResponse framing remains Starlette-owned.",
            ),
        },
        exclusions=(
            {
                "scope": "stream transport chunk and disconnect behavior",
                "test_functions": {
                    "test_stream_items": _test_span(
                        "tests/test_tutorial/test_stream_json_lines/test_tutorial001.py",
                        "test_stream_items",
                    ),
                    "test_openapi_schema": _test_span(
                        "tests/test_tutorial/test_stream_json_lines/test_tutorial001.py",
                        "test_openapi_schema",
                    ),
                },
                "reason": "The source test collects a TestClient response and asserts content type and decoded lines. It does not assert ASGI chunk boundaries or disconnect behavior; generic StreamingResponse transport is Starlette 1.6.0 behavior.",
                "supporting_sources": [_JSONL_SERIALIZATION, _STARLETTE_STREAMING],
            },
        ),
    ),
}
