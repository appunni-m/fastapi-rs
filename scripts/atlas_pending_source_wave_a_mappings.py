"""Function-level source review for the pending FastAPI test-module wave A.

The recipe and workload are independently authored input-only oracle stimuli.
FastAPI imports inside the workload are source-oracle/dev-only; they must not
become target runtime imports. The target contract remains Rust-owned FastAPI
behavior with a PyO3 value-conversion facade.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
TEST_ROOT = FASTAPI_ROOT / "tests"
RECIPE = "tests/fixtures/input-recipes/parity/pending-source-wave-a.yaml"
WORKLOAD = "tests/fixtures/workloads/pending_source_wave_a.py"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "pinned source oracle and development evidence only",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI, HTTP response, upload data structure, and wire contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model validation, serialization, and JSON Schema dependency",
    },
}

_ARCHITECTURE_BOUNDARY = (
    "The input workload imports FastAPI only in the pinned source-oracle/dev process. "
    "It does not authorize or imply a FastAPI Python runtime import in the target: Rust "
    "owns FastAPI behavior/control flow and fastapi-rs-py remains binding/value conversion."
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(path: str, name: str) -> dict[str, object]:
    source = (TEST_ROOT / Path(path).relative_to("tests")).read_text(encoding="utf-8")
    tree = ast.parse(source)
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {name} in {path}, found {len(matches)}")
    node = matches[0]
    return _source(
        path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 upstream test function {name}",
    )


def _mapped(
    test_path: str,
    function_name: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
    feature_ids: list[str],
    rationale: str,
    contract_gate: str,
    implementation_sources: tuple[dict[str, object], ...],
    *,
    extra_sources: tuple[dict[str, object], ...] = (),
) -> dict[str, Any]:
    return {
        "review_status": "reviewed_source_candidate",
        "mapping_status": "contract_gated_source_candidate",
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + contract_gate,
        "stimulus_notes": (
            f"Use {RECIPE}::{case_id} actions {', '.join(action_ids)}. "
            f"The independent stimulus is implemented by {WORKLOAD}; it contains no expected output."
        ),
        "workflow_cases": [
            {
                "recipe_path": RECIPE,
                "case_id": case_id,
                "action_ids": list(action_ids),
                "observation_selectors": list(selectors),
            }
        ],
        "supporting_sources": [
            _test_span(test_path, function_name),
            *extra_sources,
            *implementation_sources,
        ],
    }


def _excluded(
    test_path: str,
    function_name: str,
    reason: str,
    sources: tuple[dict[str, object], ...],
) -> dict[str, Any]:
    return {
        "review_status": "reviewed_excluded",
        "exclusion_reason": reason,
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


_FILE_CLOSE = (
    _source(
        "fastapi/routing.py",
        134,
        145,
        "FastAPI creates the request-scoped AsyncExitStack and unwinds it after response dispatch",
    ),
    _source(
        "fastapi/routing.py",
        425,
        432,
        "FastAPI parses form data and registers FormData.close on its request cleanup stack",
    ),
    _source(
        "starlette/datastructures.py",
        482,
        498,
        "Starlette 1.6.0 FormData closes each contained Starlette UploadFile",
    ),
)

_SECURITY = (
    _source(
        "fastapi/dependencies/utils.py",
        271,
        347,
        "FastAPI builds dependency graphs and composes parent and Security-declared OAuth scopes",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        710,
        724,
        "FastAPI injects the resolved Response and accumulated SecurityScopes into dependencies",
    ),
    _source(
        "fastapi/security/oauth2.py",
        653,
        693,
        "FastAPI SecurityScopes exposes the scopes accumulated for a dependency chain",
    ),
)

_BODY_VALIDATION = (
    _source(
        "fastapi/routing.py",
        425,
        450,
        "FastAPI reads body/form inputs and gates JSON decoding on strict_content_type and JSON media types",
    ),
    _source(
        "fastapi/dependencies/utils.py",
        951,
        1048,
        "FastAPI extracts request body values and delegates typed fixed-tuple validation through request fields",
    ),
)

_RESPONSE_SERIALIZATION = (
    _source(
        "fastapi/routing.py",
        301,
        338,
        "FastAPI validates response values and delegates field serialization to the pinned Pydantic adapter",
    ),
    _source(
        "fastapi/routing.py",
        706,
        750,
        "FastAPI builds ordinary responses, applies no-body status policy, and merges dependency response headers",
    ),
)

_RESPONSE_STATUS = (
    _source(
        "fastapi/routing.py",
        357,
        372,
        "FastAPI resolves dependency-mutated Response.status_code over the route-declared status",
    ),
    _source(
        "fastapi/routing.py",
        716,
        750,
        "FastAPI serializes route results, empties bodies for disallowed statuses, and merges injected response headers",
    ),
)

_OPENAPI_ROUTE = (
    _source(
        "fastapi/routing.py",
        1034,
        1054,
        "FastAPI normalizes route descriptions and creates response fields for additional response models",
    ),
    _source(
        "fastapi/openapi/utils.py",
        311,
        365,
        "FastAPI assembles OpenAPI operation metadata, parameters, and route response entries",
    ),
    _source(
        "fastapi/openapi/utils.py",
        403,
        465,
        "FastAPI projects response status, response media types, and JSONL/SSE item schemas into OpenAPI",
    ),
    _source(
        "fastapi/openapi/utils.py",
        585,
        647,
        "FastAPI generates its OpenAPI document from route contexts and Pydantic-derived model definitions",
    ),
)

_STRICT_CONTENT_TYPE = (
    _source(
        "fastapi/applications.py",
        840,
        858,
        "FastAPI exposes strict_content_type on the application constructor",
    ),
    _source(
        "fastapi/applications.py",
        986,
        999,
        "FastAPI forwards the application-level strict_content_type setting to its router",
    ),
    _source(
        "fastapi/routing.py",
        389,
        450,
        "FastAPI resolves route strictness and parses JSON only for accepted Content-Type cases",
    ),
    _source(
        "fastapi/routing.py",
        1300,
        1365,
        "FastAPI router inclusion carries and resolves strict_content_type across nested routers",
    ),
)

_STARLETTE_RESPONSE = (
    _source(
        "starlette/responses.py",
        33,
        81,
        "Starlette 1.6.0 renders response bytes and initializes content headers including bodyless-status policy",
    ),
    _source(
        "starlette/responses.py",
        163,
        168,
        "Starlette 1.6.0 emits generic response status, headers, and body ASGI messages",
    ),
)

_STARLETTE_COOKIES = (
    _source(
        "starlette/responses.py",
        89,
        132,
        "Starlette 1.6.0 creates Set-Cookie values and appends them to ordered response headers",
    ),
)


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
    source_path: str,
    setup_sources: tuple[dict[str, object], ...],
) -> dict[str, Any]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for review in functions.values():
        for link in review.get("workflow_cases", []):
            key = (link["recipe_path"], link["case_id"])
            unique.setdefault(
                key,
                {
                    "recipe_path": link["recipe_path"],
                    "case_ids": [link["case_id"]],
                    "observation_selectors": list(link["observation_selectors"]),
                },
            )
    selectors = sorted(
        {
            selector
            for review in functions.values()
            for selector in review.get("observation_selectors", [])
        }
    )
    return {
        "rationale": rationale,
        "module_observation_selectors": selectors,
        "supporting_sources": list(setup_sources),
        "workflow_cases": list(unique.values()),
        "stimulus_notes": (
            f"Function links use {RECIPE}; case inputs are independently authored and reference the "
            f"pinned module {source_path}. The FastAPI workload is source-oracle/dev-only; the target "
            "must use the Rust implementation boundary."
        ),
        "functions": functions,
    }


# Paths in these records are relative to the pinned FastAPI 0.141.1 source checkout.
T = "tests/test_datastructures.py"
D = "tests/test_dependency_paramless.py"
F = "tests/test_get_model_definitions_formfeed_escape.py"
ORM = "tests/test_read_with_orm_mode.py"
C = "tests/test_repeated_cookie_headers.py"
N = "tests/test_response_code_no_body.py"
S = "tests/test_response_model_sub_types.py"
W = "tests/test_response_set_response_code_empty.py"
R = "tests/test_stream_status_code.py"
U = "tests/test_tuples.py"
A = "tests/test_strict_content_type_app_level.py"
NESTED_CONTENT = "tests/test_strict_content_type_nested.py"
Q = "tests/test_tutorial/test_strict_content_type/test_tutorial001.py"

FASTAPI_SOURCE_WAVE_A_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    T: _module(
        "Reviews public upload request lifetime coverage, excludes FastAPI internal sentinels and validator hooks, and separates delegated Starlette UploadFile mechanics.",
        {
            "test_upload_file_invalid_pydantic_v2": _excluded(
                T,
                "test_upload_file_invalid_pydantic_v2",
                "Calls FastAPI's private UploadFile._validate Pydantic hook directly. This is an internal validator adapter, not an independently consumable FastAPI API call.",
                (
                    _source(
                        "fastapi/datastructures.py",
                        132,
                        150,
                        "FastAPI's private UploadFile validator and Pydantic-core schema hook",
                    ),
                ),
            ),
            "test_default_placeholder_equals": _excluded(
                T,
                "test_default_placeholder_equals",
                "Directly compares DefaultPlaceholder values; FastAPI source says this helper class is internal and should not be used directly.",
                (
                    _source(
                        "fastapi/datastructures.py",
                        153,
                        181,
                        "FastAPI documents DefaultPlaceholder and Default as internal helpers",
                    ),
                ),
            ),
            "test_default_placeholder_bool": _excluded(
                T,
                "test_default_placeholder_bool",
                "Directly checks truthiness of the internal DefaultPlaceholder sentinel rather than a consumer-visible route or dependency behavior.",
                (
                    _source(
                        "fastapi/datastructures.py",
                        153,
                        181,
                        "FastAPI documents DefaultPlaceholder and Default as internal helpers",
                    ),
                ),
            ),
            "test_upload_file_is_closed": _mapped(
                T,
                "test_upload_file_is_closed",
                "fastapi.source-wave-a.uploads.file-request",
                ["accept-upload"],
                ["http.status", "http.body.bytes"],
                ["request-validation", "request-body"],
                "A multipart UploadFile is bound to a FastAPI endpoint and the request cleanup stack closes form resources after dispatch.",
                "FastAPI owns form-body registration of FormData.close and its request cleanup stack. The input compares status and raw response bytes, which imply the source's parsed filename response, but it cannot observe the source's captured file.file.closed assertion: python.attribute_value currently covers direct Python-call results, not a route-local object retained by a workload across ASGI dispatch.",
                _FILE_CLOSE,
                extra_sources=(
                    _source(
                        T,
                        30,
                        49,
                        "Source route accepts UploadFile, retains the parsed object, and asserts closure after the request",
                    ),
                ),
            ),
            "test_upload_file": _excluded(
                T,
                "test_upload_file",
                "Directly exercises read/write/seek/close/size on an in-memory UploadFile. FastAPI's overrides delegate to Starlette UploadFile, and the tested file read/write/seek/close and size mechanics are owned by the pinned Starlette 1.6.0 data structure contract.",
                (
                    _source(
                        "fastapi/datastructures.py",
                        73,
                        130,
                        "FastAPI UploadFile convenience methods delegate to the Starlette superclass",
                    ),
                    _source(
                        "starlette/datastructures.py",
                        410,
                        479,
                        "Starlette 1.6.0 owns UploadFile storage, read/write/seek/close, and size behavior",
                    ),
                ),
            ),
        },
        T,
        _FILE_CLOSE,
    ),
    D: _module(
        "Maps the three HTTP-observable OAuth2 SecurityScopes cases and excludes the direct handler call that bypasses FastAPI.",
        {
            "test_get_credentials": _mapped(
                D,
                "test_get_credentials",
                "fastapi.source-wave-a.security.credentials-scopes",
                ["credential-view"],
                ["http.status", "http.body.bytes"],
                ["dependency-security"],
                "A bearer dependency receives the composed OAuth scopes and the endpoint returns credentials plus the requested scope list.",
                "The source compares parsed JSON; this independent direct-ASGI workflow compares exact body bytes and status. That is a stricter wire observation, including JSON serialization and generic Starlette response transport.",
                _SECURITY,
                extra_sources=(
                    _source(
                        D,
                        15,
                        32,
                        "Source dependency reads bearer credentials and returns the scopes attached to the endpoint security edge",
                    ),
                ),
            ),
            "test_parameterless_with_scopes": _mapped(
                D,
                "test_parameterless_with_scopes",
                "fastapi.source-wave-a.security.parameterless-scopes",
                ["scoped-control"],
                ["http.status", "http.body.bytes"],
                ["dependency-security"],
                "A parameterless Security dependency receives scopes declared at the path operation and allows the request.",
                "The source compares parsed JSON; this independent direct-ASGI workflow compares exact response bytes and status, also sampling serialization and Starlette transport.",
                _SECURITY,
                extra_sources=(
                    _source(
                        D,
                        15,
                        48,
                        "Source security dependency and both parameterless route declarations",
                    ),
                ),
            ),
            "test_parameterless_without_scopes": _mapped(
                D,
                "test_parameterless_without_scopes",
                "fastapi.source-wave-a.security.parameterless-no-scopes",
                ["unscoped-control"],
                ["http.status", "http.body.bytes"],
                ["dependency-security"],
                "A parameterless Security dependency with no declared scopes reaches the dependency with an empty scope set and is rejected by its scope check.",
                "The source compares parsed error JSON and status; this workflow compares exact bytes and status, which is stronger and may expose serialization/Starlette differences not asserted upstream.",
                _SECURITY,
                extra_sources=(
                    _source(
                        D,
                        15,
                        48,
                        "Source security dependency accumulates scopes before the parameterless routes are solved",
                    ),
                ),
            ),
            "test_call_get_parameterless_without_scopes_for_coverage": _excluded(
                D,
                "test_call_get_parameterless_without_scopes_for_coverage",
                "Calls the user-defined endpoint function directly and asserts its constant return. The call bypasses route matching, dependency resolution, SecurityScopes injection, validation, response construction, and ASGI dispatch, so it establishes no FastAPI behavior.",
                (
                    _source(
                        D,
                        43,
                        48,
                        "Source handler is an ordinary user function returning a constant and contains no FastAPI control flow",
                    ),
                ),
            ),
        },
        D,
        _SECURITY,
    ),
    F: _module(
        "Maps response serialization and the Pydantic model-description form-feed projection using independent nested models.",
        {
            "test_get": _mapped(
                F,
                "test_get",
                "fastapi.source-wave-a.schema-formfeed.response",
                ["read-manifest"],
                ["http.status", "http.body.bytes"],
                ["response-serialization"],
                "A nested response model is returned through an endpoint and serializes its fields as the response model contract requires.",
                "The source parses response JSON; this workflow compares exact bytes and status, a stricter observation that includes Pydantic serialization details and Starlette transport.",
                _RESPONSE_SERIALIZATION,
                extra_sources=(
                    _source(
                        F,
                        7,
                        37,
                        "Source nested Pydantic models, form-feed docstring, and response-model route setup",
                    ),
                ),
            ),
            "test_openapi_schema": _mapped(
                F,
                "test_openapi_schema",
                "fastapi.source-wave-a.schema-formfeed.description",
                ["openapi"],
                ["openapi.document"],
                ["openapi-docs"],
                "OpenAPI model definitions keep the public model docstring portion preceding the form-feed page break.",
                "The source snapshots the entire document; the independent workflow observes the parsed OpenAPI document from a distinct nested-model app with a distinct schema name and description. It does not reuse or store the upstream snapshot.",
                (
                    _source(
                        "fastapi/_compat/v2.py",
                        330,
                        345,
                        "FastAPI removes Pydantic model-description content after the form-feed marker",
                    ),
                    *_OPENAPI_ROUTE,
                ),
                extra_sources=(
                    _source(
                        F,
                        7,
                        37,
                        "Source model descriptions and route declaration create the OpenAPI model components",
                    ),
                ),
            ),
        },
        F,
        _OPENAPI_ROUTE,
    ),
    ORM: _module(
        "Maps response-model extraction from an attribute-backed object while preserving the Pydantic ownership boundary.",
        {
            "test_read_with_orm_mode": _mapped(
                ORM,
                "test_read_with_orm_mode",
                "fastapi.source-wave-a.response-model.attribute-projection",
                ["create-applicant"],
                ["http.status", "http.body.bytes"],
                ["response-serialization"],
                "FastAPI response validation projects attribute-backed values into the declared response model, including a property-derived field.",
                "The source inspects selected parsed JSON keys; this independent request compares full exact response bytes. FastAPI performs response-field validation and dispatches to Pydantic for from_attributes semantics and Starlette for HTTP serialization/transport.",
                _RESPONSE_SERIALIZATION,
            ),
        },
        ORM,
        _RESPONSE_SERIALIZATION,
    ),
    C: _module(
        "Maps response cookie mutation through direct and nested dependency injection; generic Set-Cookie encoding remains Starlette-owned.",
        {
            "test_cookie_is_set_once": _mapped(
                C,
                "test_cookie_is_set_once",
                "fastapi.source-wave-a.response-cookie.dependency-depth",
                ["direct-ticket", "relayed-ticket"],
                ["http.headers.ordered"],
                ["dependency-security", "response-serialization"],
                "The dependency mutates the injected Response cookie directly or through one nested dependency; the two response header lists are compared independently.",
                "The source compares only the Set-Cookie values, while the workflow compares the complete ordered response header lists. FastAPI owns dependency graph/Response injection and merge; Starlette 1.6.0 owns cookie formatting and raw header append behavior.",
                (
                    *_SECURITY[:2],
                    *_STARLETTE_COOKIES,
                    _source(
                        "fastapi/routing.py",
                        744,
                        750,
                        "FastAPI merges dependency-mutated raw headers into the selected route response",
                    ),
                ),
                extra_sources=(
                    _source(
                        C, 8, 26, "Source direct/nested cookie dependencies and route declarations"
                    ),
                ),
            ),
        },
        C,
        _STARLETTE_COOKIES,
    ),
    N: _module(
        "Maps a bodyless configured response and its OpenAPI route response metadata while stating Starlette wire ownership.",
        {
            "test_get_response": _mapped(
                N,
                "test_get_response",
                "fastapi.source-wave-a.response-bodyless.wire",
                ["read-empty"],
                ["http.status", "http.headers.ordered", "http.body.bytes"],
                ["response-serialization"],
                "A route selects status 204 and a custom JSON response class; FastAPI applies the no-body route policy and Starlette 1.6.0 emits the generic response.",
                "The source asserts absence of Content-Length and empty body. The workflow compares complete ordered headers and body bytes on an independently authored response class, so its header comparison is stronger and does not claim the source's custom media type or exact header-list parity.",
                (*_RESPONSE_STATUS, *_STARLETTE_RESPONSE),
                extra_sources=(
                    _source(
                        N,
                        7,
                        38,
                        "Source declares a status-204 custom response class and typed additional response metadata",
                    ),
                ),
            ),
            "test_openapi_schema": _mapped(
                N,
                "test_openapi_schema",
                "fastapi.source-wave-a.response-bodyless.openapi",
                ["openapi"],
                ["openapi.document"],
                ["openapi-docs"],
                "The OpenAPI response object records the route's bodyless success status and typed additional error model.",
                "The source snapshots two full path operations; this independent app checks its own complete parsed document and does not copy the snapshot or claim identical operation IDs/paths.",
                _OPENAPI_ROUTE,
                extra_sources=(
                    _source(
                        N,
                        7,
                        38,
                        "Source route response class, success status, and additional typed error model",
                    ),
                ),
            ),
        },
        N,
        _OPENAPI_ROUTE,
    ),
    S: _module(
        "Separates ordinary response dispatch from OpenAPI schemas for primitive, collection, model, and model-collection additional responses.",
        {
            "test_path_operations": _mapped(
                S,
                "test_path_operations",
                "fastapi.source-wave-a.response-subtypes.runtime",
                ["check-1", "check-2", "check-3", "check-4"],
                ["http.status"],
                ["response-serialization"],
                "The four route calls return successful responses while declaring additional response models of primitive, list, model, and list-of-model types.",
                "The upstream function checks only status codes; the direct-ASGI workflow also avoids interpreting or claiming additional response model behavior at runtime. Model-type schema consequences are reviewed by the separate OpenAPI function link.",
                _RESPONSE_STATUS,
                extra_sources=(
                    _source(
                        S,
                        7,
                        33,
                        "Source declares four routes with int, list[int], model, and list[model] additional response schemas",
                    ),
                ),
            ),
            "test_openapi_schema": _mapped(
                S,
                "test_openapi_schema",
                "fastapi.source-wave-a.response-subtypes.openapi",
                ["openapi"],
                ["openapi.document"],
                ["openapi-docs"],
                "The OpenAPI document projects response models spanning primitive values, typed lists, Pydantic models, and model lists.",
                "The source snapshots its route/schema document; the independent workflow observes a separately named set of four routes and models without copying any expected schema output.",
                _OPENAPI_ROUTE,
                extra_sources=(
                    _source(
                        S,
                        7,
                        33,
                        "Source route declarations enumerate all four additional response-model types",
                    ),
                ),
            ),
        },
        S,
        _OPENAPI_ROUTE,
    ),
    W: _module(
        "Maps request-time Response status mutation and the declared route-status OpenAPI view.",
        {
            "test_dependency_set_status_code": _mapped(
                W,
                "test_dependency_set_status_code",
                "fastapi.source-wave-a.response-status.override",
                ["archive-record"],
                ["http.status", "http.body.bytes"],
                ["response-serialization"],
                "An endpoint-injected Response changes the effective status from the decorator's configured value while a nonempty JSON result is returned.",
                "The source checks parsed JSON and a nonempty body; this workflow compares the exact response bytes/status. Starlette 1.6.0 owns generic JSON response byte emission, while FastAPI owns status resolution.",
                (*_RESPONSE_STATUS, *_STARLETTE_RESPONSE),
                extra_sources=(
                    _source(
                        W,
                        8,
                        23,
                        "Source route declares no-content status, injects Response, and overwrites the status before returning data",
                    ),
                ),
            ),
            "test_openapi_schema": _mapped(
                W,
                "test_openapi_schema",
                "fastapi.source-wave-a.response-status.openapi",
                ["openapi"],
                ["openapi.document"],
                ["openapi-docs"],
                "The OpenAPI route contract retains the decorator-declared success response code even though a request-time response object may replace the effective status.",
                "The source snapshots the complete path and validation schemas; the workflow observes the independent route's full parsed OpenAPI document and stores no expected outputs.",
                _OPENAPI_ROUTE,
                extra_sources=(
                    _source(
                        W,
                        8,
                        23,
                        "Source route declaration and decorator status used by OpenAPI generation",
                    ),
                ),
            ),
        },
        W,
        _OPENAPI_ROUTE,
    ),
    R: _module(
        "Maps FastAPI-declared and dependency-mutated statuses across SSE, JSONL, and raw streams, plus generated OpenAPI stream response metadata.",
        {
            "test_status_code": _mapped(
                R,
                "test_status_code",
                "fastapi.source-wave-a.stream-status.matrix",
                [f"stream-{i}" for i in range(1, 10)],
                ["http.status"],
                ["response-serialization", "status-codes"],
                "Nine independently authored generator routes cover declared 201 statuses, injected 202 statuses, and 201 values overridden by dependencies for SSE, JSONL, and raw streaming.",
                "The upstream function asserts only status. The workflow observes only status for each stream; Starlette 1.6.0 remains authoritative for generic StreamingResponse chunks, event transport, headers, and client behavior.",
                (
                    *_RESPONSE_STATUS,
                    _source(
                        "fastapi/routing.py",
                        389,
                        400,
                        "FastAPI classifies generator response kinds from route response classes",
                    ),
                    _source(
                        "fastapi/routing.py",
                        610,
                        704,
                        "FastAPI resolves route/dependency status and constructs SSE, JSONL, and raw StreamingResponse branches",
                    ),
                    _source(
                        "starlette/responses.py",
                        248,
                        255,
                        "Starlette 1.6.0 emits generic streaming status and chunks",
                    ),
                ),
                extra_sources=(
                    _source(
                        R,
                        1,
                        132,
                        "Source declares nine generator routes spanning SSE, JSONL, raw streams, and dependency-mutated status",
                    ),
                ),
            ),
            "test_openapi": _mapped(
                R,
                "test_openapi",
                "fastapi.source-wave-a.stream-status.openapi",
                ["openapi"],
                ["openapi.document"],
                ["openapi-docs"],
                "OpenAPI generation describes stream item schemas and status entries for SSE, JSONL, and raw streaming routes.",
                "The source calls app.openapi() and snapshots the whole document. The workflow fetches /openapi.json because the current ASGI runner exposes OpenAPI through HTTP, then compares its parsed full document for independently named routes; it does not claim TestClient or response-byte parity.",
                (
                    *_OPENAPI_ROUTE,
                    _source(
                        "fastapi/routing.py",
                        1071,
                        1114,
                        "FastAPI detects generator item types and derives route stream response fields",
                    ),
                ),
                extra_sources=(
                    _source(
                        R,
                        1,
                        132,
                        "Source declares route generator annotations, response classes, statuses, and additional stream responses",
                    ),
                ),
            ),
        },
        R,
        _OPENAPI_ROUTE,
    ),
    U: _module(
        "Maps fixed tuple validation in nested JSON models, tuple-of-model request bodies, URL-encoded forms, and the corresponding request schemas.",
        {
            "test_model_with_tuple_valid": _mapped(
                U,
                "test_model_with_tuple_valid",
                "fastapi.source-wave-a.tuples.model-valid",
                ["valid-pairs"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "A nested model accepts lists whose entries validate as fixed two-string tuples.",
                "The source checks parsed response JSON; exact output bytes/status are a stricter independent wire observation and include Pydantic serialization plus Starlette transport.",
                _BODY_VALIDATION,
                extra_sources=(
                    _source(U, 7, 33, "Source tuple models and route field declarations"),
                ),
            ),
            "test_model_with_tuple_invalid": _mapped(
                U,
                "test_model_with_tuple_invalid",
                "fastapi.source-wave-a.tuples.model-invalid",
                ["long-pair", "short-pair"],
                ["http.status"],
                ["request-validation"],
                "Nested fixed tuples reject both overlong and undersized tuple-shaped request values.",
                "The source asserts only 422 status for both malformed inputs; the workflow observes status only and makes no claim about validation error detail formatting.",
                _BODY_VALIDATION,
                extra_sources=(
                    _source(U, 7, 33, "Source nested tuple model and route declarations"),
                ),
            ),
            "test_tuple_with_model_valid": _mapped(
                U,
                "test_tuple_with_model_valid",
                "fastapi.source-wave-a.tuples.model-pair-valid",
                ["valid-points"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The endpoint accepts a fixed-length pair of Pydantic point models and returns the two points.",
                "Exact response bytes/status are stricter than the source's parsed JSON equality and include Pydantic serialization plus Starlette response transport.",
                _BODY_VALIDATION,
                extra_sources=(
                    _source(
                        U, 7, 33, "Source tuple-of-model request signature and route declarations"
                    ),
                ),
            ),
            "test_tuple_with_model_invalid": _mapped(
                U,
                "test_tuple_with_model_invalid",
                "fastapi.source-wave-a.tuples.model-pair-invalid",
                ["too-many-points", "too-few-points"],
                ["http.status"],
                ["request-validation"],
                "A fixed pair of model elements rejects both extra and missing tuple elements.",
                "The source asserts only 422 statuses; the workflow compares status only and does not inspect Pydantic error locations/messages.",
                _BODY_VALIDATION,
                extra_sources=(_source(U, 7, 33, "Source fixed tuple-of-model route declaration"),),
            ),
            "test_tuple_form_valid": _mapped(
                U,
                "test_tuple_form_valid",
                "fastapi.source-wave-a.tuples.form-valid",
                ["valid-form-pair"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "An URL-encoded multi-value field is extracted and validated as a pair of integers.",
                "The source checks parsed JSON; this workflow compares exact bytes/status and therefore also exercises serialization and generic Starlette transport.",
                (
                    *_BODY_VALIDATION,
                    _source(
                        "starlette/requests.py",
                        268,
                        311,
                        "Starlette 1.6.0 parses URL-encoded FormData",
                    ),
                ),
                extra_sources=(_source(U, 7, 33, "Source tuple form field and route declaration"),),
            ),
            "test_tuple_form_invalid": _mapped(
                U,
                "test_tuple_form_invalid",
                "fastapi.source-wave-a.tuples.form-invalid",
                ["too-many-form-values", "too-few-form-values"],
                ["http.status"],
                ["request-validation"],
                "The URL-encoded fixed tuple rejects both excess and missing submitted values.",
                "The source checks only 422 status; no unsupported validation details selector is claimed.",
                (
                    *_BODY_VALIDATION,
                    _source(
                        "starlette/requests.py",
                        268,
                        311,
                        "Starlette 1.6.0 parses URL-encoded FormData",
                    ),
                ),
                extra_sources=(_source(U, 7, 33, "Source tuple form field and route declaration"),),
            ),
            "test_openapi_schema": _mapped(
                U,
                "test_openapi_schema",
                "fastapi.source-wave-a.tuples.openapi",
                ["openapi"],
                ["openapi.document"],
                ["openapi-docs"],
                "OpenAPI request schemas describe a model containing tuples, a fixed tuple of models, and URL-encoded tuple form values.",
                "The source snapshots the entire document; the workflow compares a complete parsed document from the independent app with different paths, model names, and values and stores no expected schema.",
                (
                    *_OPENAPI_ROUTE,
                    _source(
                        "fastapi/openapi/utils.py",
                        231,
                        263,
                        "FastAPI places Pydantic-derived request field schemas and media types into OpenAPI",
                    ),
                ),
                extra_sources=(
                    _source(
                        U, 7, 33, "Source Pydantic tuple model definitions and endpoint signatures"
                    ),
                ),
            ),
        },
        U,
        _BODY_VALIDATION,
    ),
    A: _module(
        "Maps strict and lax application-level body parsing with and without an explicit JSON content type.",
        {
            "test_default_strict_rejects_no_content_type": _mapped(
                A,
                "test_default_strict_rejects_no_content_type",
                "fastapi.source-wave-a.content-app.strict-no-header",
                ["strict-no-header"],
                ["http.status"],
                ["request-validation"],
                "The default strict app rejects a JSON-shaped body without Content-Type.",
                "The source checks 422 status only; the workflow observes status only and does not claim validation error details.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        A,
                        1,
                        22,
                        "Source strict and lax app construction and dictionary body route declarations",
                    ),
                ),
            ),
            "test_default_strict_accepts_json_content_type": _mapped(
                A,
                "test_default_strict_accepts_json_content_type",
                "fastapi.source-wave-a.content-app.strict-json",
                ["strict-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The strict app accepts an application/json request and returns the parsed mapping.",
                "The source checks parsed JSON; the workflow compares exact bytes/status, which also samples response serialization and Starlette transport.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(A, 1, 22, "Source default-strict app and body field setup"),
                ),
            ),
            "test_lax_accepts_no_content_type": _mapped(
                A,
                "test_lax_accepts_no_content_type",
                "fastapi.source-wave-a.content-app.lax-no-header",
                ["lax-no-header"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "An app configured with strict_content_type=False parses an otherwise JSON-shaped body without a media type header.",
                "The source checks parsed JSON; this workflow compares exact response bytes/status and adds generic response-format behavior.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(A, 1, 22, "Source strict/lax app configuration and body routes"),
                ),
            ),
            "test_lax_accepts_json_content_type": _mapped(
                A,
                "test_lax_accepts_json_content_type",
                "fastapi.source-wave-a.content-app.lax-json",
                ["lax-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The lax-configured app also parses a request with the explicit JSON media type.",
                "The source checks parsed JSON; exact response bytes/status are a stricter independent observation.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(_source(A, 1, 22, "Source strict and lax body routes"),),
            ),
        },
        A,
        _STRICT_CONTENT_TYPE,
    ),
    NESTED_CONTENT: _module(
        "Maps inherited and explicitly overridden strict_content_type behavior across nested APIRouter inclusion contexts.",
        {
            "test_strict_inner_on_lax_app_rejects_no_content_type": _mapped(
                NESTED_CONTENT,
                "test_strict_inner_on_lax_app_rejects_no_content_type",
                "fastapi.source-wave-a.content-nested.strict-inner-no-header",
                ["nested-strict-no-header"],
                ["http.status"],
                ["request-validation"],
                "A strict inner router overrides its lax FastAPI parent and rejects a JSON-shaped body without Content-Type.",
                "The source checks 422 status only; the workflow observes status only and does not claim validation details.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        1,
                        67,
                        "Source builds lax app with explicit strict inner and inherited-default routers, plus strict app with lax/strict nesting",
                    ),
                ),
            ),
            "test_default_inner_inherits_lax_from_app": _mapped(
                NESTED_CONTENT,
                "test_default_inner_inherits_lax_from_app",
                "fastapi.source-wave-a.content-nested.default-inner-no-header",
                ["nested-default-no-header"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "An inner router using the default strictness inherits the lax setting through its outer router and app.",
                "The source checks parsed JSON; exact bytes/status also observe serialization and Starlette transport.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        1,
                        67,
                        "Source nested router construction and inclusion order",
                    ),
                ),
            ),
            "test_strict_inner_accepts_json_content_type": _mapped(
                NESTED_CONTENT,
                "test_strict_inner_accepts_json_content_type",
                "fastapi.source-wave-a.content-nested.strict-inner-json",
                ["nested-strict-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The strict inner route parses a body when application/json is supplied.",
                "The source checks parsed JSON and status; the workflow compares exact bytes/status.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        1,
                        67,
                        "Source strict inner router included beneath lax app/outer router",
                    ),
                ),
            ),
            "test_default_inner_accepts_json_content_type": _mapped(
                NESTED_CONTENT,
                "test_default_inner_accepts_json_content_type",
                "fastapi.source-wave-a.content-nested.default-inner-json",
                ["nested-default-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "A default inner router inheriting lax parent configuration accepts a JSON media type request.",
                "The source checks JSON and status; the independent workflow checks exact bytes/status.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        1,
                        67,
                        "Source default inner router and its lax parent context",
                    ),
                ),
            ),
            "test_lax_outer_on_strict_app_accepts_no_content_type": _mapped(
                NESTED_CONTENT,
                "test_lax_outer_on_strict_app_accepts_no_content_type",
                "fastapi.source-wave-a.content-nested.lax-outer-no-header",
                ["mixed-outer-no-header"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "An explicitly lax outer router overrides the strict app setting and parses a body without Content-Type.",
                "The source checks parsed JSON and status; exact bytes/status are a stronger independent check.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        49,
                        67,
                        "Source strict app, lax outer router, and nested strict router declarations",
                    ),
                ),
            ),
            "test_strict_inner_on_lax_outer_rejects_no_content_type": _mapped(
                NESTED_CONTENT,
                "test_strict_inner_on_lax_outer_rejects_no_content_type",
                "fastapi.source-wave-a.content-nested.strict-inner-on-lax-outer-no-header",
                ["mixed-inner-no-header"],
                ["http.status"],
                ["request-validation"],
                "An inner strict router overrides an explicitly lax outer router and rejects a request without Content-Type.",
                "The source asserts 422 status only; no validation error detail selector is claimed.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        49,
                        67,
                        "Source strict inner router included beneath a lax outer router and strict app",
                    ),
                ),
            ),
            "test_lax_outer_accepts_json_content_type": _mapped(
                NESTED_CONTENT,
                "test_lax_outer_accepts_json_content_type",
                "fastapi.source-wave-a.content-nested.lax-outer-json",
                ["mixed-outer-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The explicitly lax outer route accepts a request with application/json.",
                "The source checks status only for this case; the workflow also compares exact body bytes.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        49,
                        67,
                        "Source lax outer route and strict app configuration",
                    ),
                ),
            ),
            "test_strict_inner_on_lax_outer_accepts_json_content_type": _mapped(
                NESTED_CONTENT,
                "test_strict_inner_on_lax_outer_accepts_json_content_type",
                "fastapi.source-wave-a.content-nested.strict-inner-json-on-lax-outer",
                ["mixed-inner-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The explicitly strict inner route accepts a properly labeled JSON body despite the lax parent.",
                "The source checks status only; this workflow additionally compares exact output bytes.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        NESTED_CONTENT,
                        49,
                        67,
                        "Source strict inner route nested under an explicitly lax outer router",
                    ),
                ),
            ),
        },
        NESTED_CONTENT,
        _STRICT_CONTENT_TYPE,
    ),
    Q: _module(
        "Maps tutorial app parsing for a lax JSON body without Content-Type, a regular JSON request, and a text/plain rejection.",
        {
            "test_lax_post_without_content_type_is_parsed_as_json": _mapped(
                Q,
                "test_lax_post_without_content_type_is_parsed_as_json",
                "fastapi.source-wave-a.content-tutorial.lax-no-header",
                ["tutorial-no-header"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The tutorial app uses strict_content_type=False and parses the tutorial-style JSON body without Content-Type.",
                "The source checks parsed JSON; this independent workload uses a different model and values and compares exact response bytes/status.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        "docs_src/strict_content_type/tutorial001_py310.py",
                        1,
                        14,
                        "Tutorial app configuration and request model declaration",
                    ),
                ),
            ),
            "test_lax_post_with_json_content_type": _mapped(
                Q,
                "test_lax_post_with_json_content_type",
                "fastapi.source-wave-a.content-tutorial.lax-json",
                ["tutorial-json"],
                ["http.status", "http.body.bytes"],
                ["request-validation"],
                "The lax tutorial app also accepts a request that explicitly declares JSON.",
                "The source checks parsed JSON; exact bytes/status are a stronger independent wire observation.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        "docs_src/strict_content_type/tutorial001_py310.py",
                        1,
                        14,
                        "Tutorial lax app and request model",
                    ),
                ),
            ),
            "test_lax_post_with_text_plain_is_still_rejected": _mapped(
                Q,
                "test_lax_post_with_text_plain_is_still_rejected",
                "fastapi.source-wave-a.content-tutorial.text-plain-rejected",
                ["tutorial-text-plain"],
                ["http.status"],
                ["request-validation"],
                "The tutorial lax setting permits a missing media type but does not parse an explicit text/plain body as JSON.",
                "The source checks 422 status only; the workflow observes status only and does not claim error detail behavior.",
                _STRICT_CONTENT_TYPE,
                extra_sources=(
                    _source(
                        "docs_src/strict_content_type/tutorial001_py310.py",
                        1,
                        14,
                        "Tutorial lax app and request model",
                    ),
                ),
            ),
        },
        Q,
        _STRICT_CONTENT_TYPE,
    ),
}


__all__ = ["FASTAPI_SOURCE_WAVE_A_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]
