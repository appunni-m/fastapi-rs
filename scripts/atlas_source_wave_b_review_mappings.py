"""Source-backed mapping for the FastAPI 0.141.1 pending test wave B.

This sidecar records function-level source spans, selected workflow observations,
and explicit exclusions. The workflows are independently authored inputs; this
module does not run the oracle, target, or workloads.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "source oracle and development evidence only",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI routing, request, response, and exception oracle",
    },
    "pydantic": {
        "version": "2.13.4",
        "pydantic_core_version": "2.46.4",
        "role": "pinned public model and serialization dependency",
    },
}

ROUTER_RECIPE = "tests/fixtures/input-recipes/parity/source-wave-b-router-config.yaml"
ANNOTATION_RECIPE = "tests/fixtures/input-recipes/parity/source-wave-b-annotations.yaml"
STARLETTE_RECIPE = "tests/fixtures/input-recipes/parity/source-wave-b-starlette-integration.yaml"
CUSTOM_ROUTE_RECIPE = "tests/fixtures/input-recipes/parity/source-wave-b-custom-routes.yaml"
REQUEST_RECIPE = "tests/fixtures/input-recipes/parity/source-wave-b-request-direct.yaml"

_HTTP = ["http.status", "http.body.bytes"]
_HTTP_HEADERS = ["http.status", "http.headers.ordered", "http.body.bytes"]
_OPENAPI = ["http.status", "openapi.document"]


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
        f"pinned FastAPI 0.141.1 test function {function_name}",
    )


def _link(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    observation_selectors: list[str],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(observation_selectors),
    }


def _mapped(
    test_path: str,
    function_name: str,
    feature_ids: list[str],
    rationale: str,
    contract_gate: str,
    links: list[dict[str, Any]],
    supporting_sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    source_span = _test_span(test_path, function_name)
    selectors = sorted(
        {selector for workflow in links for selector in workflow["observation_selectors"]}
    )
    return {
        "review_status": "reviewed_partial",
        "mapping_status": "mapped_partial",
        "source_span": source_span,
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "contract_gate": "Partial: " + contract_gate,
        "workflow_cases": list(links),
        "supporting_sources": [source_span, *supporting_sources],
    }


def _excluded(
    test_path: str,
    function_name: str,
    reason: str,
    supporting_sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    source_span = _test_span(test_path, function_name)
    return {
        "review_status": "reviewed_excluded",
        "mapping_status": "source_backed_exclusion",
        "source_span": source_span,
        "feature_ids": [],
        "observation_selectors": [],
        "rationale": reason,
        "exclusion_reason": reason,
        "workflow_cases": [],
        "supporting_sources": [source_span, *supporting_sources],
    }


def _module(test_path: str, rationale: str, functions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    links: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for function in functions.values():
        for workflow in function["workflow_cases"]:
            key = (
                workflow["recipe_path"],
                workflow["case_id"],
                tuple(workflow["action_ids"]),
            )
            links.setdefault(key, workflow)
        for source in function["supporting_sources"]:
            key = (
                source["path"],
                source["start_line"],
                source["end_line"],
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
                for function in functions.values()
                for selector in function["observation_selectors"]
            }
        ),
    }


_ROUTER_INCLUDE = _source(
    "fastapi/routing.py",
    3133,
    3312,
    "FastAPI APIRouter.include_router records nested path and metadata context",
)
_ROUTER_CONTEXT = _source(
    "fastapi/routing.py",
    1305,
    1370,
    "FastAPI composes nested prefixes, tags, dependencies, response defaults, and overlays",
)
_ROUTE_CONTEXT = _source(
    "fastapi/routing.py",
    1425,
    1478,
    "FastAPI projects effective include context onto each API route",
)
_ROUTE_REGISTRATION = _source(
    "fastapi/routing.py",
    2889,
    2971,
    "FastAPI registers API routes and resolves route-level defaults",
)
_OPENAPI_BUILD = _source(
    "fastapi/openapi/utils.py",
    287,
    366,
    "FastAPI projects API route metadata and response declarations into OpenAPI",
)
_OPENAPI_DOCUMENT = _source(
    "fastapi/openapi/utils.py",
    585,
    679,
    "FastAPI assembles the OpenAPI document from selected API routes",
)
_REQUEST_HANDLER_CONTENT_TYPE = _source(
    "fastapi/routing.py",
    375,
    455,
    "FastAPI request handling parses JSON only when strict content-type policy permits it",
)
_STRICT_CONTENT_TYPE_FLOW = _source(
    "fastapi/routing.py",
    1300,
    1478,
    "FastAPI preserves strict_content_type defaults through nested router includes",
)
_FASTAPI_APP_ROUTER_OPTIONS = _source(
    "fastapi/applications.py",
    960,
    1005,
    "FastAPI forwards router options including redirect_slashes and strict_content_type",
)
_TYPED_SIGNATURE = _source(
    "fastapi/dependencies/utils.py",
    213,
    248,
    "FastAPI unwraps callables and resolves string parameter and return annotations",
)
_DEPENDANT_SIGNATURES = _source(
    "fastapi/dependencies/utils.py",
    271,
    370,
    "FastAPI classifies Request, dependency, and field parameters from resolved signatures",
)
_DEPENDENCY_LIFETIME = _source(
    "fastapi/dependencies/utils.py",
    566,
    574,
    "FastAPI enters generator dependencies through the request exit stack",
)
_RESPONSE_ENCODER = _source(
    "fastapi/encoders.py",
    129,
    366,
    "FastAPI converts response values through its jsonable_encoder boundary",
)
_RESPONSE_SERIALIZATION = _source(
    "fastapi/routing.py",
    686,
    761,
    "FastAPI serializes endpoint results and invokes the selected response class",
)
_NO_BODY_POLICY = _source(
    "fastapi/utils.py",
    26,
    40,
    "FastAPI identifies HTTP status codes that must not carry an entity body",
)
_HTTP_EXCEPTION_HANDLER = _source(
    "fastapi/exception_handlers.py",
    11,
    17,
    "FastAPI maps HTTPException to a bodyless or JSON response and preserves headers",
)
_EXCEPTION_REGISTRATION = _source(
    "fastapi/applications.py",
    986,
    1005,
    "FastAPI registers its HTTP and validation exception handlers",
)
_STARLETTE_ROUTE_MATCH = _source(
    "starlette/routing.py",
    111,
    164,
    "Starlette compiles generic route templates and converter bindings",
)
_STARLETTE_CONVERTOR_MATCH = _source(
    "starlette/routing.py",
    242,
    258,
    "Starlette matches route paths and converts captured path values",
)
_STARLETTE_INTEGER_FLOAT = _source(
    "starlette/convertors.py",
    43,
    66,
    "Starlette owns integer and floating-point path converter parsing and formatting",
)
_STARLETTE_PATH_CONVERTOR = _source(
    "starlette/convertors.py",
    18,
    40,
    "Starlette owns string and path converter matching and formatting",
)
_STARLETTE_URL_PATH = _source(
    "starlette/applications.py",
    89,
    90,
    "Starlette Application delegates url_path_for to its router",
)
_STARLETTE_ROUTE_URL_PATH = _source(
    "starlette/routing.py",
    260,
    269,
    "Starlette Route generates URL paths from names and converter values",
)
_STARLETTE_ROUTER_URL_PATH = _source(
    "starlette/routing.py",
    631,
    637,
    "Starlette Router searches route names for url_path_for",
)
_STARLETTE_REDIRECT_SLASHES = _source(
    "starlette/routing.py",
    573,
    588,
    "Starlette Router stores redirect_slashes as generic routing policy",
)
_STARLETTE_REDIRECT_MATCH = _source(
    "starlette/routing.py",
    704,
    716,
    "Starlette Router probes slash-adjusted paths and constructs the redirect response",
)
_STARLETTE_EXCEPTION_DISPATCH = _source(
    "starlette/middleware/exceptions.py",
    18,
    73,
    "Starlette ExceptionMiddleware dispatches exceptions to registered handlers",
)
_STARLETTE_HTTP_EXCEPTION = _source(
    "starlette/exceptions.py",
    7,
    22,
    "Starlette defines HTTPException status, detail, and response headers",
)
_FASTAPI_REQUEST_ALIAS = _source(
    "fastapi/requests.py",
    1,
    2,
    "FastAPI directly re-exports Starlette Request and HTTPConnection",
)
_STARLETTE_REQUEST_CLIENT = _source(
    "starlette/requests.py",
    161,
    170,
    "Starlette Request exposes the ASGI scope client address",
)
_GZIP_DOC = _source(
    "docs_src/custom_request_and_route/tutorial001_py310.py",
    8,
    35,
    "FastAPI tutorial documents a user-defined Request and APIRoute extension",
)
_VALIDATION_ROUTE_DOC = _source(
    "docs_src/custom_request_and_route/tutorial002_py310.py",
    8,
    29,
    "FastAPI tutorial documents a user-defined APIRoute validation wrapper",
)
_REQUEST_DIRECT_DOC = _source(
    "docs_src/using_request_directly/tutorial001_py310.py",
    1,
    9,
    "FastAPI tutorial injects the Starlette Request and reads its client host",
)


_INCLUDE_TEST = "tests/test_include_router_defaults_overrides.py"
_INCLUDE_MAPPINGS = _module(
    _INCLUDE_TEST,
    "The source wave samples app, include, nested-router, and route-level defaults plus a whole generated OpenAPI document. Its 3-level and 5-level functions contain wider parametrized matrices than the independent cases.",
    {
        "test_level1_override": _mapped(
            _INCLUDE_TEST,
            "test_level1_override",
            ["app-routing", "dependency-security", "response-serialization"],
            "A route-level response class and dependency are observed against an app-level dependency and an include context.",
            "Only an independently authored single included route is selected; it does not cover the upstream metadata values or response-class subclass matrix.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.explicit-response",
                    ["request-explicit"],
                    _HTTP_HEADERS,
                )
            ],
            (_ROUTER_INCLUDE, _ROUTER_CONTEXT, _ROUTE_CONTEXT, _RESPONSE_SERIALIZATION),
        ),
        "test_level1_default": _mapped(
            _INCLUDE_TEST,
            "test_level1_default",
            ["app-routing", "dependency-security", "response-serialization"],
            "An unoverridden path operation inherits the app response default while app-level dependencies remain active.",
            "The workflow uses a separate route and response media type; it selects the response boundary rather than every source assertion.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.inherited-response",
                    ["request-inherited"],
                    _HTTP_HEADERS,
                )
            ],
            (_ROUTER_CONTEXT, _ROUTE_CONTEXT, _RESPONSE_SERIALIZATION),
        ),
        "test_paths_level3": _mapped(
            _INCLUDE_TEST,
            "test_paths_level3",
            ["app-routing", "dependency-security", "response-serialization"],
            "Explicit and inherited response classes are sampled across nested router include contexts, alongside inherited dependencies.",
            "Two independent paths represent selected override/default branches; the upstream 8-combination parameter product is not exhaustive here.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.nested-explicit",
                    ["request-nested-explicit"],
                    _HTTP_HEADERS,
                ),
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.nested-inherited",
                    ["request-nested-inherited"],
                    _HTTP_HEADERS,
                ),
            ],
            (_ROUTER_INCLUDE, _ROUTER_CONTEXT, _ROUTE_CONTEXT, _RESPONSE_SERIALIZATION),
        ),
        "test_paths_level5": _mapped(
            _INCLUDE_TEST,
            "test_paths_level5",
            ["app-routing", "dependency-security", "response-serialization"],
            "A deeper include chain samples a route override and the inherited response default at the leaf.",
            "Two independent paths sample explicit and inherited leaf behavior; the upstream 32-combination matrix, all include permutations, and every dependency/header assertion are not covered.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.five-level-explicit",
                    ["request-five-level-explicit"],
                    _HTTP_HEADERS,
                ),
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.five-level-inherited",
                    ["request-five-level-inherited"],
                    _HTTP_HEADERS,
                ),
            ],
            (_ROUTER_INCLUDE, _ROUTER_CONTEXT, _ROUTE_CONTEXT, _RESPONSE_SERIALIZATION),
        ),
        "test_openapi": _mapped(
            _INCLUDE_TEST,
            "test_openapi",
            ["app-routing", "openapi-docs"],
            "The workflow selects a complete OpenAPI document generated from independent include-level tags and response overlays.",
            "The workflow does not capture Python warnings, duplicate-operation-ID warning text, or the source's exact five-level callback and response snapshot.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-defaults.openapi",
                    ["inspect-router-openapi"],
                    _OPENAPI,
                )
            ],
            (_ROUTER_INCLUDE, _ROUTER_CONTEXT, _ROUTE_CONTEXT, _OPENAPI_BUILD, _OPENAPI_DOCUMENT),
        ),
    },
)

_INHERITED_TEST = "tests/test_inherited_custom_class.py"
_INHERITED_MAPPINGS = _module(
    _INHERITED_TEST,
    "The test serializes a UUID-like custom object and a Pydantic model containing that object through FastAPI responses.",
    {
        "test_pydanticv2": _mapped(
            _INHERITED_TEST,
            "test_pydanticv2",
            ["response-serialization", "public-api-errors"],
            "Two independent GET requests exercise FastAPI response encoding for a custom object with a spoofed class and a Pydantic field serializer.",
            "Only response bytes are selected; the source's isinstance/vars checks, exact UUID values, and Pydantic serializer internals are not claimed. Pydantic model and field serialization remain delegated to pinned Pydantic 2.13.4.",
            [
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.serialization.driver-class",
                    ["encode-driver-object"],
                    _HTTP,
                ),
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.serialization.pydantic-model",
                    ["encode-custom-model"],
                    _HTTP,
                ),
            ],
            (_RESPONSE_ENCODER, _RESPONSE_SERIALIZATION),
        )
    },
)

_NONE_TEST = "tests/test_return_none_stringified_annotations.py"
_NONE_MAPPINGS = _module(
    _NONE_TEST,
    "The test checks a stringified None return annotation on a 204 path operation and verifies an empty response body.",
    {
        "test_no_content": _mapped(
            _NONE_TEST,
            "test_no_content",
            ["app-routing", "response-serialization"],
            "A 204 route with a None return annotation is observed for status and raw body bytes.",
            "The independent workload uses postponed annotations so the resolved annotation is the string None; it does not assert unrelated response headers or source literals.",
            [
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.annotations.stringified-none",
                    ["request-no-content"],
                    _HTTP,
                )
            ],
            (_TYPED_SIGNATURE, _ROUTE_REGISTRATION, _RESPONSE_SERIALIZATION, _NO_BODY_POLICY),
        )
    },
)

_PREFIX_TEST = "tests/test_router_prefix_with_template.py"
_PREFIX_MAPPINGS = _module(
    _PREFIX_TEST,
    "The test combines an APIRouter prefix containing a path parameter with a child route path and observes the injected values.",
    {
        "test_get": _mapped(
            _PREFIX_TEST,
            "test_get",
            ["app-routing", "request-validation", "response-serialization"],
            "The workflow composes a template-bearing include prefix with a parameterized child route and selects the response bytes.",
            "It samples one independent prefix and identifier; generic route regex matching remains Starlette 1.6.0-owned.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-prefix.template-parameters",
                    ["request-prefixed-template"],
                    _HTTP,
                )
            ],
            (_ROUTER_INCLUDE, _ROUTE_CONTEXT, _STARLETTE_ROUTE_MATCH, _STARLETTE_CONVERTOR_MATCH),
        )
    },
)

_REDIRECT_TEST = "tests/test_router_redirect_slashes.py"
_REDIRECT_MAPPINGS = _module(
    _REDIRECT_TEST,
    "These assertions select only Starlette Router's generic redirect_slashes routing policy. FastAPI forwards the constructor option, while Starlette owns slash probing and response generation.",
    {
        "test_redirect_slashes_enabled": _excluded(
            _REDIRECT_TEST,
            "test_redirect_slashes_enabled",
            "Excluded from this FastAPI source wave: FastAPI passes redirect_slashes to APIRouter, but route matching, slash-adjusted probing, and the 307 response are implemented by the pinned Starlette Router. Track this behavior in the Starlette-RS sibling contract.",
            (_FASTAPI_APP_ROUTER_OPTIONS, _STARLETTE_REDIRECT_SLASHES, _STARLETTE_REDIRECT_MATCH),
        ),
        "test_redirect_slashes_disabled": _excluded(
            _REDIRECT_TEST,
            "test_redirect_slashes_disabled",
            "Excluded from this FastAPI source wave: FastAPI exposes and forwards redirect_slashes=False, but whether a missing-slash path redirects or reaches the not-found handler is generic Starlette Router behavior. Track the routing policy in the Starlette-RS sibling contract.",
            (_FASTAPI_APP_ROUTER_OPTIONS, _STARLETTE_REDIRECT_SLASHES, _STARLETTE_REDIRECT_MATCH),
        ),
    },
)

_EXCEPTION_TEST = "tests/test_starlette_exception.py"
_EXCEPTION_MAPPINGS = _module(
    _EXCEPTION_TEST,
    "The selected behaviors are FastAPI's HTTPException-compatible handlers, bodyless status policy, and generated OpenAPI. Generic exception dispatch stays with Starlette.",
    {
        "test_get_item": _mapped(
            _EXCEPTION_TEST,
            "test_get_item",
            ["app-routing", "response-serialization"],
            "A successful FastAPI route response is selected through the public ASGI boundary.",
            "The route and returned record are independently named; this samples the successful path, not the source's exact route data.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.fastapi-success",
                    ["get-existing-fastapi-item"],
                    _HTTP,
                )
            ],
            (_ROUTE_REGISTRATION, _RESPONSE_SERIALIZATION),
        ),
        "test_get_item_not_found": _mapped(
            _EXCEPTION_TEST,
            "test_get_item_not_found",
            ["public-api-errors"],
            "FastAPI's registered HTTPException handler converts a FastAPI HTTPException into status, response headers, and a JSON detail body.",
            "The input uses an independent route, status detail, and header; generic Starlette ExceptionMiddleware dispatch is not attributed to FastAPI.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.fastapi-not-found",
                    ["get-missing-fastapi-item"],
                    _HTTP_HEADERS,
                )
            ],
            (_EXCEPTION_REGISTRATION, _HTTP_EXCEPTION_HANDLER, _STARLETTE_EXCEPTION_DISPATCH),
        ),
        "test_get_starlette_item": _mapped(
            _EXCEPTION_TEST,
            "test_get_starlette_item",
            ["app-routing", "response-serialization"],
            "A successful endpoint using Starlette's HTTPException type is selected through the FastAPI app boundary.",
            "Only the successful response path is selected; generic Starlette request routing is a sibling-owned behavior.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.starlette-success",
                    ["get-existing-starlette-item"],
                    _HTTP,
                )
            ],
            (_ROUTE_REGISTRATION, _RESPONSE_SERIALIZATION, _STARLETTE_HTTP_EXCEPTION),
        ),
        "test_get_starlette_item_not_found": _mapped(
            _EXCEPTION_TEST,
            "test_get_starlette_item_not_found",
            ["public-api-errors"],
            "FastAPI registers a handler for Starlette's HTTPException base type, so an endpoint raising that public type gets FastAPI's error response mapping.",
            "The workflow samples one not-found status/detail and selected headers; generic exception dispatch remains Starlette 1.6.0 behavior.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.starlette-not-found",
                    ["get-missing-starlette-item"],
                    _HTTP_HEADERS,
                )
            ],
            (
                _EXCEPTION_REGISTRATION,
                _HTTP_EXCEPTION_HANDLER,
                _STARLETTE_HTTP_EXCEPTION,
                _STARLETTE_EXCEPTION_DISPATCH,
            ),
        ),
        "test_no_body_status_code_exception_handlers": _mapped(
            _EXCEPTION_TEST,
            "test_no_body_status_code_exception_handlers",
            ["public-api-errors", "response-serialization"],
            "FastAPI's HTTPException handler suppresses the response entity for a status whose policy disallows a body.",
            "One no-body status is selected; the generic Starlette response transport and all prohibited status values are outside this case.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.no-body-status",
                    ["get-no-body-status"],
                    _HTTP,
                )
            ],
            (_HTTP_EXCEPTION_HANDLER, _NO_BODY_POLICY),
        ),
        "test_no_body_status_code_with_detail_exception_handlers": _mapped(
            _EXCEPTION_TEST,
            "test_no_body_status_code_with_detail_exception_handlers",
            ["public-api-errors", "response-serialization"],
            "FastAPI's no-body status path discards an exception detail from the HTTP response body.",
            "The independent route uses new detail text and selects status/raw body; it does not assert the detail object itself.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.no-body-status-with-detail",
                    ["get-no-body-status-with-detail"],
                    _HTTP,
                )
            ],
            (_HTTP_EXCEPTION_HANDLER, _NO_BODY_POLICY),
        ),
        "test_openapi_schema": _mapped(
            _EXCEPTION_TEST,
            "test_openapi_schema",
            ["openapi-docs"],
            "The workflow selects the complete OpenAPI document for an independent app with FastAPI and Starlette exception routes.",
            "The document is generated from new route names and descriptions, not copied from the source snapshot; generic exception route registration remains Starlette-owned.",
            [
                _link(
                    STARLETTE_RECIPE,
                    "fastapi.source-wave-b.exception.openapi",
                    ["inspect-exception-openapi"],
                    _OPENAPI,
                )
            ],
            (_OPENAPI_BUILD, _OPENAPI_DOCUMENT, _STARLETTE_HTTP_EXCEPTION),
        ),
    },
)

_CONVERTOR_TEST = "tests/test_starlette_urlconvertors.py"
_CONVERTOR_MAPPINGS = _module(
    _CONVERTOR_TEST,
    "HTTP converter cases combine Starlette's route matching and conversion with FastAPI's path/query parameter extraction. The direct app.url_path_for test is generic Starlette behavior.",
    {
        "test_route_converters_int": _mapped(
            _CONVERTOR_TEST,
            "test_route_converters_int",
            ["app-routing", "request-validation", "response-serialization"],
            "An integer path-converter request is selected through the FastAPI endpoint and typed path parameter.",
            "The source also calls app.url_path_for; the ASGI workflow cannot observe that direct Python API assertion, which is covered as Starlette-owned behavior in the dedicated exclusion below.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-config.convertors.integer",
                    ["request-integer-convertor"],
                    _HTTP,
                )
            ],
            (
                _STARLETTE_ROUTE_MATCH,
                _STARLETTE_CONVERTOR_MATCH,
                _STARLETTE_INTEGER_FLOAT,
                _DEPENDANT_SIGNATURES,
            ),
        ),
        "test_route_converters_float": _mapped(
            _CONVERTOR_TEST,
            "test_route_converters_float",
            ["app-routing", "request-validation", "response-serialization"],
            "A floating-point path-converter request is selected through the FastAPI endpoint and typed path parameter.",
            "The source also calls app.url_path_for; this Python API operation is not an ASGI observation. Generic float conversion remains a Starlette 1.6.0 contract.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-config.convertors.float",
                    ["request-float-convertor"],
                    _HTTP,
                )
            ],
            (
                _STARLETTE_ROUTE_MATCH,
                _STARLETTE_CONVERTOR_MATCH,
                _STARLETTE_INTEGER_FLOAT,
                _DEPENDANT_SIGNATURES,
            ),
        ),
        "test_route_converters_path": _mapped(
            _CONVERTOR_TEST,
            "test_route_converters_path",
            ["app-routing", "request-validation", "response-serialization"],
            "A slash-containing path-converter value is passed through FastAPI's typed Path parameter into the endpoint response.",
            "The route regex and path capture are Starlette-owned; this case selects only the shared HTTP response boundary.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-config.convertors.path",
                    ["request-path-convertor"],
                    _HTTP,
                )
            ],
            (
                _STARLETTE_ROUTE_MATCH,
                _STARLETTE_CONVERTOR_MATCH,
                _STARLETTE_PATH_CONVERTOR,
                _DEPENDANT_SIGNATURES,
            ),
        ),
        "test_route_converters_query": _mapped(
            _CONVERTOR_TEST,
            "test_route_converters_query",
            ["request-validation", "response-serialization"],
            "The query-valued path operation exercises FastAPI query parameter extraction and response serialization.",
            "The request and response use independent values; generic route matching and TestClient query construction are not claimed.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.router-config.convertors.query",
                    ["request-query-parameter"],
                    _HTTP,
                )
            ],
            (_DEPENDANT_SIGNATURES,),
        ),
        "test_url_path_for_path_convertor": _excluded(
            _CONVERTOR_TEST,
            "test_url_path_for_path_convertor",
            "Excluded from this FastAPI source wave: FastAPI inherits url_path_for from Starlette and delegates it to Router, while Route and the path converter implement URL formatting. Keep this direct Python API behavior in the Starlette-RS sibling contract.",
            (
                _STARLETTE_URL_PATH,
                _STARLETTE_ROUTER_URL_PATH,
                _STARLETTE_ROUTE_URL_PATH,
                _STARLETTE_PATH_CONVERTOR,
            ),
        ),
    },
)

_STRINGIFIED_DEPENDENCY_TEST = "tests/test_stringified_annotation_dependency.py"
_STRINGIFIED_DEPENDENCY_MAPPINGS = _module(
    _STRINGIFIED_DEPENDENCY_TEST,
    "The module tests postponed Annotated dependency metadata, a yielded client dependency, request-time output, and the generated operation schema.",
    {
        "test_get": _mapped(
            _STRINGIFIED_DEPENDENCY_TEST,
            "test_get",
            ["dependency-security", "response-serialization"],
            "A route using a postponed Annotated dependency obtains a value from a yield dependency and returns a JSON list.",
            "The selected body verifies dependency resolution only; the source DummyClient cleanup method has no externally selected lifecycle observation.",
            [
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.annotations.yield-dependency",
                    ["request-yield-dependency"],
                    _HTTP,
                )
            ],
            (_TYPED_SIGNATURE, _DEPENDANT_SIGNATURES, _DEPENDENCY_LIFETIME),
        ),
        "test_openapi_schema": _mapped(
            _STRINGIFIED_DEPENDENCY_TEST,
            "test_openapi_schema",
            ["dependency-security", "openapi-docs"],
            "The independent OpenAPI request selects the operation generated for a route using a postponed Annotated yield dependency.",
            "Only the operation path is selected, not the source's full document snapshot, response metadata, and validation component schema.",
            [
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.annotations.yield-dependency-openapi",
                    ["inspect-yield-dependency-openapi"],
                    _OPENAPI,
                )
            ],
            (_TYPED_SIGNATURE, _DEPENDANT_SIGNATURES, _OPENAPI_BUILD, _OPENAPI_DOCUMENT),
        ),
    },
)

_STRINGIFIED_SIMPLE_TEST = "tests/test_stringified_annotations_simple.py"
_STRINGIFIED_SIMPLE_MAPPINGS = _module(
    _STRINGIFIED_SIMPLE_TEST,
    "The test resolves a postponed Annotated class dependency whose callable receives Request.",
    {
        "test_stringified_annotations": _mapped(
            _STRINGIFIED_SIMPLE_TEST,
            "test_stringified_annotations",
            ["dependency-security", "response-serialization"],
            "The independent request resolves the postponed Annotated dependency and selects the returned response.",
            "The source checks only status; the independent workflow additionally selects raw response bytes, but does not assert the TestClient redirect sequence.",
            [
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.annotations.request-dependency",
                    ["request-class-dependency"],
                    _HTTP,
                )
            ],
            (_TYPED_SIGNATURE, _DEPENDANT_SIGNATURES),
        )
    },
)

_WRAPPED_TEST = "tests/test_wrapped_method_forward_reference.py"
_WRAPPED_MAPPINGS = _module(
    _WRAPPED_TEST,
    "The regression test checks that one and two functools.wraps layers preserve the original callable annotations and resolve the forward reference.",
    {
        "test_wrapped_method_type_inference": _mapped(
            _WRAPPED_TEST,
            "test_wrapped_method_type_inference",
            ["request-validation", "response-serialization"],
            "Two independent POSTs exercise typed request and response models behind one and two transparent wrapper layers.",
            "The workflow checks each response against the live oracle, but does not assert source-to-source equality across the two responses; its payload and paths are independent.",
            [
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.annotations.forward-reference-once",
                    ["post-forward-reference-once"],
                    _HTTP,
                ),
                _link(
                    ANNOTATION_RECIPE,
                    "fastapi.source-wave-b.annotations.forward-reference-twice",
                    ["post-forward-reference-twice"],
                    _HTTP,
                ),
            ],
            (_TYPED_SIGNATURE, _DEPENDANT_SIGNATURES, _RESPONSE_SERIALIZATION),
        )
    },
)

_STRICT_TEST = "tests/test_strict_content_type_router_level.py"
_STRICT_MAPPINGS = _module(
    _STRICT_TEST,
    "The module compares app-level strict JSON content-type policy with lax, strict, and default APIRouter values for requests with and without a content-type header.",
    {
        "test_lax_router_on_strict_app_accepts_no_content_type": _mapped(
            _STRICT_TEST,
            "test_lax_router_on_strict_app_accepts_no_content_type",
            ["request-validation", "app-routing"],
            "A lax router accepts a JSON body when the strict app's route input omits Content-Type.",
            "The independent JSON document and path differ; only status and response bytes are selected.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.strict-content-type.lax-no-header",
                    ["post-lax-without-type"],
                    _HTTP,
                )
            ],
            (_FASTAPI_APP_ROUTER_OPTIONS, _STRICT_CONTENT_TYPE_FLOW, _REQUEST_HANDLER_CONTENT_TYPE),
        ),
        "test_strict_router_on_strict_app_rejects_no_content_type": _mapped(
            _STRICT_TEST,
            "test_strict_router_on_strict_app_rejects_no_content_type",
            ["request-validation", "app-routing", "public-api-errors"],
            "A strict router rejects a JSON-looking body when Content-Type is absent.",
            "The case selects public status and body only; error detail structure is not a separate selector.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.strict-content-type.strict-no-header",
                    ["post-strict-without-type"],
                    _HTTP,
                )
            ],
            (_STRICT_CONTENT_TYPE_FLOW, _REQUEST_HANDLER_CONTENT_TYPE),
        ),
        "test_default_router_inherits_strict_from_app": _mapped(
            _STRICT_TEST,
            "test_default_router_inherits_strict_from_app",
            ["request-validation", "app-routing", "public-api-errors"],
            "A router that leaves strict_content_type at its default inherits the app-level strict setting.",
            "The independent case selects the validation response boundary, not a copied error payload.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.strict-content-type.default-no-header",
                    ["post-default-without-type"],
                    _HTTP,
                )
            ],
            (_FASTAPI_APP_ROUTER_OPTIONS, _STRICT_CONTENT_TYPE_FLOW, _REQUEST_HANDLER_CONTENT_TYPE),
        ),
        "test_lax_router_accepts_json_content_type": _mapped(
            _STRICT_TEST,
            "test_lax_router_accepts_json_content_type",
            ["request-validation", "app-routing"],
            "An explicitly JSON-typed body remains accepted by a lax router.",
            "The independent request uses a new body object and selects status/body bytes.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.strict-content-type.lax-with-json-header",
                    ["post-lax-with-type"],
                    _HTTP,
                )
            ],
            (_STRICT_CONTENT_TYPE_FLOW, _REQUEST_HANDLER_CONTENT_TYPE),
        ),
        "test_strict_router_accepts_json_content_type": _mapped(
            _STRICT_TEST,
            "test_strict_router_accepts_json_content_type",
            ["request-validation", "app-routing"],
            "An explicitly JSON-typed body is accepted by a strict router.",
            "The independent request uses a new body object and selects status/body bytes.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.strict-content-type.strict-with-json-header",
                    ["post-strict-with-type"],
                    _HTTP,
                )
            ],
            (_STRICT_CONTENT_TYPE_FLOW, _REQUEST_HANDLER_CONTENT_TYPE),
        ),
        "test_default_router_accepts_json_content_type": _mapped(
            _STRICT_TEST,
            "test_default_router_accepts_json_content_type",
            ["request-validation", "app-routing"],
            "A default-valued router inherited from a strict app accepts an explicitly JSON-typed body.",
            "Only the selected request case is represented; the source's exact JSON body is not copied.",
            [
                _link(
                    ROUTER_RECIPE,
                    "fastapi.source-wave-b.strict-content-type.default-with-json-header",
                    ["post-default-with-type"],
                    _HTTP,
                )
            ],
            (_STRICT_CONTENT_TYPE_FLOW, _REQUEST_HANDLER_CONTENT_TYPE),
        ),
    },
)

_TUTORIAL001_TEST = "tests/test_tutorial/test_custom_request_and_route/test_tutorial001.py"
_TUTORIAL001_MAPPINGS = _module(
    _TUTORIAL001_TEST,
    "The tutorial wraps an APIRoute with a user Request subclass that optionally decompresses gzip request bodies and exposes the concrete request class.",
    {
        "test_gzip_request": _mapped(
            _TUTORIAL001_TEST,
            "test_gzip_request",
            ["app-routing", "request-validation", "response-serialization"],
            "The selected request uses the uncompressed JSON branch of the custom request route and reaches the typed list endpoint.",
            "Partial: the upstream test also parameterizes a compressed body, but the current ASGI workflow only accepts UTF-8 text body events and cannot provide arbitrary gzip bytes. The compressed branch remains unrepresented. The request/route override logic is user code in the workload, not FastAPI facade behavior.",
            [
                _link(
                    CUSTOM_ROUTE_RECIPE,
                    "fastapi.source-wave-b.custom-request.uncompressed-json",
                    ["post-uncompressed-json"],
                    _HTTP,
                )
            ],
            (_GZIP_DOC, _ROUTE_REGISTRATION, _ROUTE_CONTEXT),
        ),
        "test_request_class": _mapped(
            _TUTORIAL001_TEST,
            "test_request_class",
            ["app-routing", "response-serialization"],
            "The workflow observes the custom Request subclass name returned by an endpoint after FastAPI's route wrapper constructs the request object.",
            "The class is independently named; execution of the request wrapper is consumer-provided Python extension code, outside the native facade itself.",
            [
                _link(
                    CUSTOM_ROUTE_RECIPE,
                    "fastapi.source-wave-b.custom-request.request-subclass",
                    ["inspect-custom-request-class"],
                    _HTTP,
                )
            ],
            (_GZIP_DOC, _ROUTE_REGISTRATION, _ROUTE_CONTEXT),
        ),
    },
)

_TUTORIAL002_TEST = "tests/test_tutorial/test_custom_request_and_route/test_tutorial002.py"
_TUTORIAL002_MAPPINGS = _module(
    _TUTORIAL002_TEST,
    "The tutorial wraps FastAPI's route handler to translate request validation errors into an HTTPException containing error details and the raw request body.",
    {
        "test_endpoint_works": _mapped(
            _TUTORIAL002_TEST,
            "test_endpoint_works",
            ["app-routing", "request-validation", "response-serialization"],
            "A valid list body is accepted by a route with the user's custom APIRoute subclass installed.",
            "The route and list input are independently authored; custom route-class behavior is user code executed around the FastAPI handler.",
            [
                _link(
                    CUSTOM_ROUTE_RECIPE,
                    "fastapi.source-wave-b.custom-route.valid-request",
                    ["post-valid-list"],
                    _HTTP,
                )
            ],
            (_VALIDATION_ROUTE_DOC, _ROUTE_REGISTRATION, _ROUTE_CONTEXT),
        ),
        "test_exception_handler_body_access": _mapped(
            _TUTORIAL002_TEST,
            "test_exception_handler_body_access",
            ["request-validation", "public-api-errors", "response-serialization"],
            "An invalid object is sent to a list-body endpoint; the custom route catches RequestValidationError, reads the body, and raises FastAPI HTTPException.",
            "The workflow selects raw response bytes for an independently encoded request; the source uses parsed JSON equality with two accepted embedded-body strings. The custom wrapper remains user-authored extension logic.",
            [
                _link(
                    CUSTOM_ROUTE_RECIPE,
                    "fastapi.source-wave-b.custom-route.validation-context",
                    ["post-invalid-shape-with-context"],
                    _HTTP,
                )
            ],
            (
                _VALIDATION_ROUTE_DOC,
                _REQUEST_HANDLER_CONTENT_TYPE,
                _HTTP_EXCEPTION_HANDLER,
                _EXCEPTION_REGISTRATION,
            ),
        ),
    },
)

_REQUEST_DIRECT_TEST = "tests/test_tutorial/test_using_request_directly/test_tutorial001.py"
_REQUEST_DIRECT_MAPPINGS = _module(
    _REQUEST_DIRECT_TEST,
    "The tutorial injects FastAPI.Request, directly re-exported from Starlette, reads the ASGI client host, and documents the route in OpenAPI.",
    {
        "test_path_operation": _mapped(
            _REQUEST_DIRECT_TEST,
            "test_path_operation",
            ["app-routing", "request-validation", "response-serialization"],
            "The independent route injects Request and returns its client host and a path parameter from an ASGI request scope.",
            "The client host is an explicit ASGI input and the route path/value are independently authored. Request.client semantics remain Starlette-owned.",
            [
                _link(
                    REQUEST_RECIPE,
                    "fastapi.source-wave-b.request-direct.client-address",
                    ["read-asgi-client-host"],
                    _HTTP,
                )
            ],
            (
                _FASTAPI_REQUEST_ALIAS,
                _DEPENDANT_SIGNATURES,
                _STARLETTE_REQUEST_CLIENT,
                _REQUEST_DIRECT_DOC,
            ),
        ),
        "test_openapi": _mapped(
            _REQUEST_DIRECT_TEST,
            "test_openapi",
            ["openapi-docs"],
            "The input selects a complete OpenAPI document for an independent route that also declares Request injection.",
            "The source compares the full document, but uses a different path, endpoint name, and operation ID; the workflow validates a separate live document without carrying source snapshot values.",
            [
                _link(
                    REQUEST_RECIPE,
                    "fastapi.source-wave-b.request-direct.openapi",
                    ["inspect-request-direct-openapi"],
                    _OPENAPI,
                )
            ],
            (_FASTAPI_REQUEST_ALIAS, _OPENAPI_BUILD, _OPENAPI_DOCUMENT, _REQUEST_DIRECT_DOC),
        ),
    },
)

SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_include_router_defaults_overrides.py": _INCLUDE_MAPPINGS,
    "tests/test_inherited_custom_class.py": _INHERITED_MAPPINGS,
    "tests/test_return_none_stringified_annotations.py": _NONE_MAPPINGS,
    "tests/test_router_prefix_with_template.py": _PREFIX_MAPPINGS,
    "tests/test_router_redirect_slashes.py": _REDIRECT_MAPPINGS,
    "tests/test_starlette_exception.py": _EXCEPTION_MAPPINGS,
    "tests/test_starlette_urlconvertors.py": _CONVERTOR_MAPPINGS,
    "tests/test_stringified_annotation_dependency.py": _STRINGIFIED_DEPENDENCY_MAPPINGS,
    "tests/test_stringified_annotations_simple.py": _STRINGIFIED_SIMPLE_MAPPINGS,
    "tests/test_wrapped_method_forward_reference.py": _WRAPPED_MAPPINGS,
    "tests/test_strict_content_type_router_level.py": _STRICT_MAPPINGS,
    "tests/test_tutorial/test_custom_request_and_route/test_tutorial001.py": _TUTORIAL001_MAPPINGS,
    "tests/test_tutorial/test_custom_request_and_route/test_tutorial002.py": _TUTORIAL002_MAPPINGS,
    "tests/test_tutorial/test_using_request_directly/test_tutorial001.py": _REQUEST_DIRECT_MAPPINGS,
}

SOURCE_WAVE_B_REVIEW = {
    "fastapi_identity": SOURCE_IDENTITIES["fastapi"],
    "starlette_identity": SOURCE_IDENTITIES["starlette"],
    "pydantic_identity": SOURCE_IDENTITIES["pydantic"],
    "mapping_status": "source-reviewed-input-candidate; parity pending",
    "test_modules": SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS,
    "recipe_paths": [
        ROUTER_RECIPE,
        ANNOTATION_RECIPE,
        STARLETTE_RECIPE,
        CUSTOM_ROUTE_RECIPE,
        REQUEST_RECIPE,
    ],
    "workload_paths": [
        "tests/fixtures/workloads/source_wave_b_router_config.py",
        "tests/fixtures/workloads/source_wave_b_annotations.py",
        "tests/fixtures/workloads/source_wave_b_starlette_integration.py",
        "tests/fixtures/workloads/source_wave_b_custom_routes.py",
        "tests/fixtures/workloads/source_wave_b_request_direct.py",
    ],
    "observation_boundary": (
        "The workflows call FastAPI's consumer API through ASGI and select public HTTP/OpenAPI output. "
        "Generic routing, URL generation, Request behavior, and exception dispatch belong to the pinned "
        "Starlette-RS sibling. User-defined APIRoute and Request overrides remain workload code; the "
        "FastAPI-RS facade stays direct native re-exports and Rust owns FastAPI control flow."
    ),
}


def _all_test_functions(test_path: str) -> set[str]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def _validate_span(source: dict[str, Any]) -> None:
    path = source["path"]
    source_root = STARLETTE_ROOT if path.startswith("starlette/") else FASTAPI_ROOT
    lines = (source_root / path).read_text(encoding="utf-8").splitlines()
    if not (1 <= source["start_line"] <= source["end_line"] <= len(lines)):
        raise ValueError(
            f"source span is out of range: {path}:{source['start_line']}-{source['end_line']}"
        )


def validate_source_wave_b_review_mappings() -> dict[str, int]:
    """Statically validate denominator coverage, source spans, schemas, and links."""
    import json

    import jsonschema
    import yaml

    expected_modules = {
        "tests/test_include_router_defaults_overrides.py",
        "tests/test_inherited_custom_class.py",
        "tests/test_return_none_stringified_annotations.py",
        "tests/test_router_prefix_with_template.py",
        "tests/test_router_redirect_slashes.py",
        "tests/test_starlette_exception.py",
        "tests/test_starlette_urlconvertors.py",
        "tests/test_stringified_annotation_dependency.py",
        "tests/test_stringified_annotations_simple.py",
        "tests/test_wrapped_method_forward_reference.py",
        "tests/test_strict_content_type_router_level.py",
        "tests/test_tutorial/test_custom_request_and_route/test_tutorial001.py",
        "tests/test_tutorial/test_custom_request_and_route/test_tutorial002.py",
        "tests/test_tutorial/test_using_request_directly/test_tutorial001.py",
    }
    if set(SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS) != expected_modules:
        raise ValueError("source-wave-b module paths do not match the requested denominator")

    schema = json.loads(
        (PROJECT_ROOT / "tests/fixtures/schemas/python-asgi-workflow-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    recipes: dict[str, dict[str, Any]] = {}
    workloads: set[str] = set()
    all_case_ids: set[str] = set()
    case_count = 0

    for recipe_path in SOURCE_WAVE_B_REVIEW["recipe_paths"]:
        recipe = yaml.safe_load((PROJECT_ROOT / recipe_path).read_text(encoding="utf-8"))
        validator.validate(recipe)
        workload_path = recipe["workload"]["file"]
        if workload_path in workloads:
            raise ValueError(f"workload path is not unique: {workload_path}")
        workloads.add(workload_path)
        workload_tree = ast.parse((PROJECT_ROOT / workload_path).read_text(encoding="utf-8"))
        factories = {
            node.name
            for node in workload_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if recipe["workload"]["factory"] not in factories:
            raise ValueError(f"missing workload factory in {workload_path}")
        case_map: dict[str, dict[str, Any]] = {}
        for case in recipe["cases"]:
            if case["case_id"] in all_case_ids:
                raise ValueError(f"duplicate case ID across recipes: {case['case_id']}")
            all_case_ids.add(case["case_id"])
            case_map[case["case_id"]] = case
            case_count += 1
            for evidence in case["source_evidence"]:
                if not (FASTAPI_ROOT / evidence["path"]).is_file():
                    raise ValueError(f"missing pinned source evidence: {evidence['path']}")
        recipes[recipe_path] = case_map

    if workloads != set(SOURCE_WAVE_B_REVIEW["workload_paths"]):
        raise ValueError("recipe workloads do not match the sidecar workload list")

    test_function_count = 0
    mapped_count = 0
    exclusion_count = 0
    for test_path, module in SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS.items():
        discovered = _all_test_functions(test_path)
        reviewed = set(module["functions"])
        if discovered != reviewed:
            raise ValueError(
                f"test-function mapping mismatch in {test_path}: "
                f"unmapped={sorted(discovered - reviewed)}, stale={sorted(reviewed - discovered)}"
            )
        test_function_count += len(discovered)
        for function_name, function in module["functions"].items():
            span = function["source_span"]
            _validate_span(span)
            if span != _test_span(test_path, function_name):
                raise ValueError(
                    f"source span does not select the function: {test_path}:{function_name}"
                )
            for source in function["supporting_sources"]:
                _validate_span(source)
            if function["review_status"] == "reviewed_excluded":
                exclusion_count += 1
                if function["workflow_cases"] or not function["exclusion_reason"]:
                    raise ValueError(f"invalid exclusion record in {test_path}:{function_name}")
                continue
            if function["review_status"] != "reviewed_partial" or not function["workflow_cases"]:
                raise ValueError(f"mapped function has no workflow in {test_path}:{function_name}")
            mapped_count += 1
            for link in function["workflow_cases"]:
                case = recipes.get(link["recipe_path"], {}).get(link["case_id"])
                if case is None:
                    raise ValueError(f"mapping references unknown case {link['case_id']}")
                actions = {action["action_id"]: action for action in case["actions"]}
                if not set(link["action_ids"]) <= set(actions):
                    raise ValueError(f"mapping references unknown actions in {link['case_id']}")
                available: set[str] = set()
                for action_id in link["action_ids"]:
                    for observation in actions[action_id]["observations"]:
                        if observation["kind"] == "http_response":
                            for selector in observation["selectors"]:
                                if selector == "status":
                                    available.add("http.status")
                                elif selector == "headers":
                                    available.add("http.headers.ordered")
                                elif selector == "body":
                                    available.add("http.body.bytes")
                        elif observation["kind"] == "openapi":
                            available.add("openapi.document")
                if not set(link["observation_selectors"]) <= available:
                    raise ValueError(
                        f"mapping selectors exceed workflow observations in {link['case_id']}"
                    )

    if test_function_count != mapped_count + exclusion_count:
        raise ValueError("each requested test function must be mapped or source-backed-excluded")
    return {
        "modules": len(expected_modules),
        "test_functions": test_function_count,
        "mapped_functions": mapped_count,
        "excluded_functions": exclusion_count,
        "recipes": len(recipes),
        "workloads": len(workloads),
        "cases": case_count,
    }


__all__ = [
    "SOURCE_IDENTITIES",
    "SOURCE_WAVE_B_REVIEW",
    "SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS",
    "validate_source_wave_b_review_mappings",
]
