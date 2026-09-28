"""Source-reviewed function mappings for the FastAPI core-test wave.

Values intentionally contain input/observation designs only. Unsupported
observation projections are gated until the parity schema can express them.
"""


def _case(feature_ids, observation_selectors, rationale, **extra):
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(observation_selectors),
        "rationale": rationale,
        "replace_features": True,
        **extra,
    }


CORE_TEST_REVIEW_MAPPINGS = {
    "tests/test_response_class_no_mediatype.py": {
        "feature_ids": ["openapi-docs", "response-serialization"],
        "module_observation_selectors": ["http.status", "openapi.document"],
        "rationale": "The source checks a successful OpenAPI request and exact parsed document output for an explicit Starlette Response with no media type and a default JSON response class.",
        "stimulus_notes": "The dedicated input uses the same two route declarations and observes the entire parsed OpenAPI document with the root JSON pointer. The declared JsonApiResponse subclass is unused by either route and is not treated as exercised. The source uses TestClient; direct ASGI input observes FastAPI's response while generic TestClient behavior remains in the Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "tests/test_response_class_no_mediatype.py",
                "start_line": 7,
                "end_line": 34,
                "role": "FastAPI app, unused custom JSON response subclass, response models, and the two route declarations",
            },
            {
                "path": "tests/test_response_class_no_mediatype.py",
                "start_line": 40,
                "end_line": 114,
                "role": "OpenAPI request, asserted success status, and exact parsed-document snapshot",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1176,
                "end_line": 1217,
                "role": "FastAPI path-operation decorator defaults to JSONResponse and forwards the selected response class",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 6,
                "end_line": 11,
                "role": "FastAPI re-exports Starlette response classes, including Response and JSONResponse",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 325,
                "end_line": 330,
                "role": "OpenAPI generation resolves the current response class and its media_type",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 472,
                "role": "The ordinary success response content is emitted only when the class has a media type",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 473,
                "end_line": 505,
                "role": "Additional response models use the response class media type or application/json when it is absent",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 29,
                "end_line": 43,
                "role": "Pinned Starlette Response has no default media_type unless a caller supplies one",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 181,
                "end_line": 192,
                "role": "Pinned Starlette JSONResponse declares application/json",
            },
        ],
        "functions": {
            "test_openapi_schema": _case(
                ["openapi-docs", "response-serialization"],
                ["http.status", "openapi.document"],
                "The dedicated app preserves both source routes; the HTTP status selector and root OpenAPI JSON pointer independently cover the asserted 200 status and complete parsed JSON snapshot.",
            ),
        },
    },
    "tests/test_dependency_after_yield_websockets.py": {
        "supporting_sources": [
            {
                "path": "tests/test_dependency_after_yield_websockets.py",
                "start_line": 37,
                "end_line": 40,
                "role": "yield dependency raises ValueError during cleanup-backed iteration",
            },
            {
                "path": "tests/test_dependency_after_yield_websockets.py",
                "start_line": 56,
                "end_line": 60,
                "role": "broken WebSocket route accepts and iterates the yielded session",
            },
            {
                "path": "tests/test_dependency_after_yield_websockets.py",
                "start_line": 76,
                "end_line": 79,
                "role": "source test asserts propagated exception type and message substring",
            },
        ],
        "functions": {
            "test_websocket_dependency_after_yield_broken": _case(
                ["asgi-error-propagation", "websocket-lifecycle"],
                ["asgi.application_error.exception"],
                "The broken yielded dependency raises during WebSocket dispatch; the workflow observes the fully qualified exception class and exact message while retaining the source test's exception boundary.",
            ),
        },
    },
    "tests/test_response_model_as_return_annotation.py": {
        "supporting_sources": [
            {
                "path": "tests/test_response_model_as_return_annotation.py",
                "start_line": 50,
                "end_line": 53,
                "role": "response-model route returns a dictionary missing a required field",
            },
            {
                "path": "tests/test_response_model_as_return_annotation.py",
                "start_line": 278,
                "end_line": 281,
                "role": "source test asserts ResponseValidationError and a missing-field message",
            },
        ],
        "functions": {
            "test_response_model_no_annotation_return_invalid_dict": _case(
                ["asgi-error-propagation", "response-serialization"],
                ["asgi.application_error.exception", "validation.error_class"],
                "An invalid response value raises FastAPI ResponseValidationError; the workflow observes its exact qualified exception and message alongside the source-backed validation class.",
            ),
        },
    },
    "tests/test_response_model_invalid.py": {
        "feature_ids": ["response-serialization", "public-api-errors"],
        "module_observation_selectors": ["construction.outcome"],
        "rationale": "Each function registers a route with an invalid direct or generic response model and asserts that registration raises FastAPIError.",
        "stimulus_notes": "The four existing construction-errors-upstream cases independently cover direct and list response_model declarations plus direct and list models in responses. Each fails during FastAPI route construction, before an ASGI request or Starlette dispatch; no Starlette behavior is delegated. The recipe also records exception class and message, but only the error outcome is selected for this source mapping.",
        "contract_gate": "The source uses pytest.raises(FastAPIError), which accepts subclasses. The available construction.exception_class selector compares exact fully qualified class names and cannot express this superclass predicate, so the asserted exception type is gated. The source does not assert exception text; construction.exception_message is diagnostic input evidence only.",
        "supporting_sources": [
            {
                "path": "tests/test_response_model_invalid.py",
                "start_line": 1,
                "end_line": 4,
                "role": "the source imports pytest and FastAPIError for its raises assertions",
            },
            {
                "path": "tests/test_response_model_invalid.py",
                "start_line": 6,
                "end_line": 7,
                "role": "non-Pydantic model class used by all four cases",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1993,
                "end_line": 2017,
                "role": "FastAPI GET decorator forwards response_model and responses to its router",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 2889,
                "end_line": 2965,
                "role": "FastAPI router constructs the API route with the declared response model and responses",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1038,
                "end_line": 1054,
                "role": "FastAPI creates fields for additional response models during route construction",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1101,
                "end_line": 1113,
                "role": "FastAPI creates the primary response field during route construction",
            },
            {
                "path": "fastapi/utils.py",
                "start_line": 47,
                "end_line": 77,
                "role": "FastAPI converts invalid Pydantic response-field schema construction into FastAPIError",
            },
            {
                "path": "fastapi/exceptions.py",
                "start_line": 161,
                "end_line": 162,
                "role": "FastAPIError is the public RuntimeError subclass caught by the upstream assertions",
            },
        ],
        "functions": {
            "test_invalid_response_model_raises": _case(
                ["response-serialization", "public-api-errors"],
                ["construction.outcome"],
                "The direct response_model case is represented by the existing direct-invalid-response-model construction input; the source asserts that route registration raises.",
            ),
            "test_invalid_response_model_sub_type_raises": _case(
                ["response-serialization", "public-api-errors"],
                ["construction.outcome"],
                "The list[NonPydanticModel] response_model case is represented by the existing sequence-invalid-response-model construction input; the source asserts that route registration raises.",
            ),
            "test_invalid_response_model_in_responses_raises": _case(
                ["response-serialization", "public-api-errors"],
                ["construction.outcome"],
                "The additional response with a direct NonPydanticModel is represented by the existing direct-invalid-additional-response construction input; the source asserts that route registration raises.",
            ),
            "test_invalid_response_model_sub_type_in_responses_raises": _case(
                ["response-serialization", "public-api-errors"],
                ["construction.outcome"],
                "The additional response with list[NonPydanticModel] is represented by the existing sequence-invalid-additional-response construction input; the source asserts that route registration raises.",
            ),
        },
    },
    "tests/test_response_model_include_exclude.py": {
        "feature_ids": ["response-serialization"],
        "module_observation_selectors": ["http.status", "http.body.bytes"],
        "contract_gate": "Each source function asserts response.json() equality as well as status 200. The six independent cases observe supported `http.status` and exact `http.body.bytes`; exact wire bytes and key order can be stricter than the source's parsed-JSON equality. Keep the function mappings partial until a semantic JSON-value selector can represent that source assertion. The source does not assert headers.",
        "stimulus_notes": "response-model-include-exclude-source-review.yaml adds one independently authored ASGI case for each of the six source route variants: nested include and nested exclude with model-instance and dict returns, plus combined include/exclude with both return forms. The workload uses new class/field names and input values while preserving the source-backed nesting and filter shapes; it embeds no expected outputs. The older response-model-serialization.yaml and schema-extensions.yaml cases remain related inputs, not substitutes for these per-function cases. The source uses FastAPI's TestClient re-export, which delegates its HTTP-to-ASGI client mechanics to Starlette 1.6.0; these workflows drive FastAPI directly through ASGI.",
        "supporting_sources": [
            {
                "path": "tests/test_response_model_include_exclude.py",
                "start_line": 6,
                "end_line": 19,
                "role": "nested response model declarations used by the six test routes",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1812,
                "end_line": 1835,
                "role": "FastAPI GET decorator declares include and exclude as response-serialization options passed to Pydantic",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1993,
                "end_line": 2017,
                "role": "FastAPI forwards response-model include and exclude options to its router",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 978,
                "end_line": 1007,
                "role": "FastAPI stores the route's response-model include and exclude configuration",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 727,
                "end_line": 739,
                "role": "FastAPI passes route include and exclude configuration to response serialization",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 338,
                "role": "FastAPI validates the response and delegates the include/exclude projection to the response field serializer",
            },
            {
                "path": "fastapi/testclient.py",
                "start_line": 1,
                "end_line": 1,
                "role": "FastAPI re-exports Starlette TestClient used by the source tests",
            },
            {
                "path": "starlette/testclient.py",
                "start_line": 377,
                "end_line": 420,
                "role": "Starlette 1.6.0 TestClient installs its ASGI transport and client defaults; this client boundary is delegated behavior",
            },
            {
                "path": "starlette/testclient.py",
                "start_line": 277,
                "end_line": 291,
                "role": "Starlette 1.6.0 TestClient constructs the HTTP ASGI scope for each client request",
            },
        ],
        "functions": {
            "test_nested_include_simple": _case(
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "response-model-include-exclude-source-review.yaml case fastapi.response-model.include.nested.model independently exercises the nested include shape with a model-instance return and observes status plus raw response bytes.",
                contract_gate="The exact body-byte comparison is stricter than this source function's parsed response.json() equality; retain partial source coverage until a semantic JSON-value selector is available.",
                stimulus_notes="The case uses independent model and field names and fresh values; its route configuration and model-instance return form match this source variant.",
                supporting_sources=[
                    {
                        "path": "tests/test_response_model_include_exclude.py",
                        "start_line": 25,
                        "end_line": 34,
                        "role": "nested-include route declaration and model-instance endpoint",
                    }
                ],
            ),
            "test_nested_include_simple_dict": _case(
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "response-model-include-exclude-source-review.yaml case fastapi.response-model.include.nested.dict independently exercises the nested include shape with a dict return and observes status plus raw response bytes.",
                contract_gate="The exact body-byte comparison is stricter than this source function's parsed response.json() equality; retain partial source coverage until a semantic JSON-value selector is available.",
                stimulus_notes="The case uses independent model and field names and fresh values; its route configuration and dict return form match this source variant.",
                supporting_sources=[
                    {
                        "path": "tests/test_response_model_include_exclude.py",
                        "start_line": 37,
                        "end_line": 49,
                        "role": "nested-include route declaration and dict-returning endpoint",
                    }
                ],
            ),
            "test_nested_exclude_simple": _case(
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "response-model-include-exclude-source-review.yaml case fastapi.response-model.exclude.nested.model independently exercises the nested exclude shape with a model-instance return and observes status plus raw response bytes.",
                contract_gate="The exact body-byte comparison is stricter than this source function's parsed response.json() equality; retain partial source coverage until a semantic JSON-value selector is available.",
                stimulus_notes="The case uses independent model and field names and fresh values; its route configuration and model-instance return form match this source variant.",
                supporting_sources=[
                    {
                        "path": "tests/test_response_model_include_exclude.py",
                        "start_line": 52,
                        "end_line": 61,
                        "role": "nested-exclude route declaration and model-instance endpoint",
                    }
                ],
            ),
            "test_nested_exclude_simple_dict": _case(
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "response-model-include-exclude-source-review.yaml case fastapi.response-model.exclude.nested.dict independently exercises the nested exclude shape with a dict return and observes status plus raw response bytes.",
                contract_gate="The exact body-byte comparison is stricter than this source function's parsed response.json() equality; retain partial source coverage until a semantic JSON-value selector is available.",
                stimulus_notes="The case uses independent model and field names and fresh values; its route configuration and dict return form match this source variant.",
                supporting_sources=[
                    {
                        "path": "tests/test_response_model_include_exclude.py",
                        "start_line": 64,
                        "end_line": 76,
                        "role": "nested-exclude route declaration and dict-returning endpoint",
                    }
                ],
            ),
            "test_nested_include_mixed": _case(
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "response-model-include-exclude-source-review.yaml case fastapi.response-model.mixed-include-exclude.model independently exercises root-level include plus nested exclude with a model-instance return and observes status plus raw response bytes.",
                contract_gate="The exact body-byte comparison is stricter than this source function's parsed response.json() equality; retain partial source coverage until a semantic JSON-value selector is available.",
                stimulus_notes="The case independently authors the nested response model and values while preserving the source route's simultaneous include/exclude shape and model-instance return form.",
                supporting_sources=[
                    {
                        "path": "tests/test_response_model_include_exclude.py",
                        "start_line": 79,
                        "end_line": 93,
                        "role": "route declaration combines root-level include and nested exclude for a model-instance endpoint",
                    }
                ],
            ),
            "test_nested_include_mixed_dict": _case(
                ["response-serialization"],
                ["http.status", "http.body.bytes"],
                "response-model-include-exclude-source-review.yaml case fastapi.response-model.mixed-include-exclude.dict independently exercises root-level include plus nested exclude with a dict return and observes status plus raw response bytes.",
                contract_gate="The exact body-byte comparison is stricter than this source function's parsed response.json() equality; retain partial source coverage until a semantic JSON-value selector is available.",
                stimulus_notes="The case independently authors the nested response model and values while preserving the source route's simultaneous include/exclude shape and dict return form.",
                supporting_sources=[
                    {
                        "path": "tests/test_response_model_include_exclude.py",
                        "start_line": 96,
                        "end_line": 110,
                        "role": "route declaration combines root-level include and nested exclude for a dict-returning endpoint",
                    }
                ],
            ),
        },
    },
    "tests/test_request_param_model_by_alias.py": {
        "supporting_sources": [
            {
                "path": "tests/test_request_param_model_by_alias.py",
                "start_line": 9,
                "end_line": 25,
                "role": "Pydantic alias model and Query/Header/Cookie route setup",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 790,
                "end_line": 835,
                "role": "FastAPI extracts request-parameter model members by validation alias",
            },
        ],
        "functions": {
            "test_query_model_with_alias": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A query model accepts the declared field alias and returns the endpoint value; the workflow also records the exact HTTP body bytes.",
            ),
            "test_header_model_with_alias": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A header model accepts the declared field alias and returns the endpoint value; the workflow also records the exact HTTP body bytes.",
            ),
            "test_cookie_model_with_alias": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.bytes"],
                "A cookie model accepts the declared field alias and returns the endpoint value; the workflow also records the exact HTTP body bytes.",
            ),
            "test_query_model_with_alias_by_name": _case(
                ["request-validation"],
                ["http.status", "http.body.bytes"],
                "The field name is rejected when the model declares a distinct validation alias; the workflow records the full validation response.",
            ),
            "test_header_model_with_alias_by_name": _case(
                ["request-validation"],
                ["http.status", "http.body.bytes"],
                "The field name is rejected when the header model declares a distinct validation alias; the workflow records the full validation response.",
            ),
            "test_cookie_model_with_alias_by_name": _case(
                ["request-validation"],
                ["http.status", "http.body.bytes"],
                "The field name is rejected when the cookie model declares a distinct validation alias; the workflow records the full validation response.",
            ),
        },
    },
    "tests/test_ws_router.py": {
        "module_observation_selectors": [
            "websocket.close_code",
            "websocket.close_reason",
            "websocket.event_order",
            "websocket.messages",
            "websocket.workload_trace",
        ],
        "supporting_sources": [
            {
                "path": "tests/test_ws_router.py",
                "start_line": 16,
                "end_line": 55,
                "role": "root and router WebSocket route definitions, prefixes, and path parameters",
            },
            {
                "path": "tests/test_ws_router.py",
                "start_line": 107,
                "end_line": 115,
                "role": "APIRouter inclusion with included and native prefixes",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 801,
                "end_line": 831,
                "role": "FastAPI builds APIWebSocketRoute endpoints and dependencies",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1324,
                "end_line": 1370,
                "role": "FastAPI composes included APIRouter routes and prefixes",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1000,
                "end_line": 1012,
                "role": "FastAPI installs default and user-supplied WebSocket exception handlers",
            },
            {
                "path": "fastapi/exception_handlers.py",
                "start_line": 29,
                "end_line": 34,
                "role": "FastAPI closes invalid WebSocket requests with policy-violation status",
            },
            {
                "path": "tests/test_ws_router.py",
                "start_line": 58,
                "end_line": 69,
                "role": "router WebSocket dependency and endpoint behavior",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 764,
                "end_line": 831,
                "role": "FastAPI resolves dependencies for APIWebSocketRoute",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 619,
                "end_line": 647,
                "role": "FastAPI applies app-level dependency overrides during resolution",
            },
        ],
        "functions": {
            "test_app": _case(
                ["app-routing"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "The FastAPI root WebSocket route accepts and emits its message; the fixture records the complete ASGI WebSocket event and close projections.",
            ),
            "test_router": _case(
                ["app-routing"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "An APIRouter WebSocket route is included and dispatched by FastAPI; generic handshake behavior remains Starlette-RS-owned.",
            ),
            "test_prefix_router": _case(
                ["app-routing"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "FastAPI applies an include_router prefix to a root WebSocket route while preserving its endpoint message.",
            ),
            "test_native_prefix_router": _case(
                ["app-routing"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "FastAPI includes an APIRouter with its configured native prefix and dispatches the prefixed WebSocket route.",
            ),
            "test_router2": _case(
                ["app-routing"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "The APIRouter.websocket decorator registers and dispatches the same route behavior as websocket_route.",
            ),
            "test_router_ws_depends": _case(
                ["app-routing", "dependency-security"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "An APIRouter WebSocket endpoint receives a FastAPI-resolved dependency; the workflow records its message and the full handshake/event sequence.",
            ),
            "test_router_ws_depends_with_override": _case(
                ["app-routing", "dependency-security"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "FastAPI's app-level dependency override changes the APIRouter WebSocket dependency result; the workflow records the full handshake/event sequence.",
            ),
            "test_router_with_params": _case(
                ["app-routing", "request-validation"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "FastAPI binds a path-converter parameter containing slashes and a query parameter before invoking the WebSocket endpoint.",
            ),
            "test_depend_validation": _case(
                ["app-routing", "request-validation", "public-api-errors"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                    "websocket.workload_trace",
                ],
                "A missing dependency header is converted by FastAPI's WebSocket validation handler into a policy-violation close; the workload trace confirms the custom middleware catches no error.",
            ),
            "test_depend_err_middleware": _case(
                ["app-routing", "middleware-integrations"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "A user WebSocket middleware catches an application dependency exception and sends an abnormal-close event with its reason.",
            ),
            "test_depend_err_handler": _case(
                ["app-routing", "public-api-errors"],
                [
                    "websocket.close_code",
                    "websocket.close_reason",
                    "websocket.event_order",
                    "websocket.messages",
                ],
                "A FastAPI exception handler maps an application WebSocket exception to the configured close code and reason.",
            ),
        },
    },
    "tests/test_additional_responses_bad.py": {
        "supporting_sources": [
            {
                "path": "tests/test_additional_responses_bad.py",
                "start_line": 38,
                "end_line": 40,
                "role": "invalid additional-response status key and expected exception",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 504,
                "end_line": 509,
                "role": "OpenAPI response-status key is converted to an integer",
            },
        ],
        "functions": {
            "test_openapi_schema": _case(
                ["openapi-docs", "public-api-errors"],
                ["validation.error_class"],
                (
                    "The invalid additional-response status raises ValueError during OpenAPI "
                    "generation; the workflow captures the fully qualified dispatch exception class."
                ),
            ),
        },
        "module_observation_selectors": ["validation.error_class"],
    },
    "tests/test_additional_responses_response_class.py": {
        "feature_ids": ["openapi-docs", "response-serialization"],
        "module_observation_selectors": ["http.status", "openapi.document"],
        "rationale": "The source checks a successful OpenAPI request and an exact parsed-document snapshot for additional response models under a custom JSON media type and the default JSON response class.",
        "stimulus_notes": "The dedicated input-only recipe additional-responses-response-class.yaml independently reproduces the source's paired /a and /b route/model declarations, custom/default response classes, and observes the complete live OpenAPI document. The source uses TestClient while the recipe invokes FastAPI through direct ASGI; generic TestClient behavior remains Starlette-RS-owned.",
        "contract_gate": "This recipe covers the FastAPI route construction and generated OpenAPI assertions. It does not claim behavior of the TestClient/HTTPX client API itself, which is delegated to the separate Starlette-RS contract.",
        "supporting_sources": [
            {
                "path": "tests/test_additional_responses_response_class.py",
                "start_line": 7,
                "end_line": 37,
                "role": "FastAPI app, custom JSONResponse subclass, additional-response models, both route declarations, and TestClient setup",
            },
            {
                "path": "tests/test_additional_responses_response_class.py",
                "start_line": 40,
                "end_line": 117,
                "role": "OpenAPI request, asserted 200 status, and exact parsed-document snapshot",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1188,
                "end_line": 1217,
                "role": "FastAPI path-operation decorator defaults to JSONResponse and forwards the selected response class and additional responses",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 8,
                "end_line": 8,
                "role": "FastAPI re-exports Starlette JSONResponse for the test's custom response subclass",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1038,
                "end_line": 1054,
                "role": "FastAPI creates response fields for declared additional-response models during route setup",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 325,
                "end_line": 330,
                "role": "OpenAPI generation resolves the route response class and reads its media_type",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 403,
                "end_line": 418,
                "role": "FastAPI determines the success status from the response-class signature and adds its response description",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 456,
                "end_line": 472,
                "role": "FastAPI emits the success response content under the selected media type and uses an empty schema for JSONResponse without a response model",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 473,
                "end_line": 516,
                "role": "FastAPI combines additional response models with the selected response media type and emits their OpenAPI response entries",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 551,
                "end_line": 582,
                "role": "FastAPI collects primary and additional response fields for the document's component schemas",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 613,
                "end_line": 672,
                "role": "FastAPI assembles route paths and component schemas in the generated OpenAPI document",
            },
            {
                "path": "starlette/responses.py",
                "start_line": 181,
                "end_line": 192,
                "role": "Pinned Starlette JSONResponse class identity, default application/json media type, and constructor inheritance boundary",
            },
        ],
        "functions": {
            "test_openapi_schema": _case(
                ["openapi-docs", "response-serialization"],
                ["http.status", "openapi.document"],
                "The source asserts status 200 and compares the complete parsed OpenAPI JSON document, including both routes, their success and additional responses, media types, operation metadata, and model schemas.",
                contract_gate="The dedicated input observes the source route/model configuration and complete OpenAPI output through direct ASGI; it does not assert the generic TestClient/HTTPX client API.",
                stimulus_notes="Use tests/fixtures/input-recipes/parity/additional-responses-response-class.yaml case fastapi.additional-responses-response-class.openapi. It observes the full parsed document as live source/target output and embeds no expected snapshot.",
            ),
        },
    },
    "tests/test_additional_properties.py": {
        "supporting_sources": [
            {
                "path": "tests/test_additional_properties.py",
                "start_line": 6,
                "end_line": 18,
                "role": "request/response models and route setup",
            },
        ],
        "functions": {
            "test_additional_properties_post": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A POST accepts and returns a model containing a string-to-integer dictionary; this function does not observe the additionalProperties schema.",
            ),
        },
    },
    "tests/test_additional_properties_bool.py": {
        "supporting_sources": [
            {
                "path": "tests/test_additional_properties_bool.py",
                "start_line": 7,
                "end_line": 25,
                "role": "Pydantic extra-forbid model, route, and request setup",
            },
        ],
        "functions": {
            "test_call_invalid": _case(
                ["request-validation"],
                ["http.status"],
                "An unknown nested model property is rejected with 422; the assertion does not inspect validation details.",
                stimulus_notes="Pydantic owns extra=forbid model semantics under the pinned identity.",
            ),
            "test_call_valid": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "An empty valid model is accepted and the endpoint returns an empty JSON object.",
                stimulus_notes="Pydantic owns the model behavior; the function observes the public HTTP result.",
            ),
        },
    },
    "tests/test_allow_inf_nan_in_enforcing.py": {
        "supporting_sources": [
            {
                "path": "tests/test_allow_inf_nan_in_enforcing.py",
                "start_line": 7,
                "end_line": 68,
                "role": "parameter configuration and finite/non-finite query stimuli",
            },
            {
                "path": "fastapi/params.py",
                "start_line": 600,
                "end_line": 660,
                "role": "Query allow_inf_nan option",
            },
        ],
        "functions": {
            "test_allow_inf_nan_param_true": _case(
                ["request-validation"],
                ["http.status"],
                "The query accepts or rejects finite/non-finite numeric values according to allow_inf_nan=True; the assertion compares status only.",
                stimulus_notes="Numeric acceptance is Pydantic-owned and pinned-version-sensitive.",
            ),
            "test_allow_inf_nan_param_false": _case(
                ["request-validation"],
                ["http.status"],
                "The query accepts or rejects finite/non-finite numeric values according to allow_inf_nan=False; the assertion compares status only.",
                stimulus_notes="Numeric acceptance is Pydantic-owned and pinned-version-sensitive.",
            ),
            "test_allow_inf_nan_param_default": _case(
                ["request-validation"],
                ["http.status"],
                "The query accepts or rejects finite/non-finite numeric values under the option default; the assertion compares status only.",
                stimulus_notes="Numeric acceptance is Pydantic-owned and pinned-version-sensitive.",
            ),
        },
    },
    "tests/test_custom_schema_fields.py": {
        "supporting_sources": [
            {
                "path": "tests/test_custom_schema_fields.py",
                "start_line": 10,
                "end_line": 30,
                "role": "Pydantic models and endpoint setup",
            },
        ],
        "functions": {
            "test_response": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "The route returns its Item response model, including a null description; this function does not inspect custom JSON Schema metadata.",
                stimulus_notes="Pydantic supplies the model behavior.",
            ),
        },
    },
    "tests/test_enforce_once_required_parameter.py": {
        "supporting_sources": [
            {
                "path": "tests/test_enforce_once_required_parameter.py",
                "start_line": 8,
                "end_line": 26,
                "role": "shared required/optional dependency declarations and route",
            },
        ],
        "functions": {
            "test_get_invalid": _case(
                ["request-validation", "dependency-security"],
                ["http.status"],
                "Omitting required client_id produces 422; the test does not inspect error details.",
            ),
            "test_get_valid": _case(
                ["request-validation", "dependency-security"],
                ["http.status", "http.body.json"],
                "One query value satisfies the required/optional dependency parameters and produces the tested keys and tags.",
                stimulus_notes="Pydantic query validation is a pinned contract dependency; response values are endpoint logic.",
            ),
        },
    },
    "tests/test_exception_handlers.py": {
        "supporting_sources": [
            {
                "path": "tests/test_exception_handlers.py",
                "start_line": 8,
                "end_line": 28,
                "role": "application handlers and routes",
            },
            {
                "path": "fastapi/exception_handlers.py",
                "start_line": 11,
                "end_line": 25,
                "role": "FastAPI exception response handlers",
            },
        ],
        "functions": {
            "test_override_http_exception": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A custom handler catches a FastAPI HTTPException and returns its own status-200 JSON response; only the HTTP result is observed.",
            ),
            "test_override_server_error_exception_response": _case(
                ["response-serialization", "middleware-integrations"],
                ["http.status", "http.body.json"],
                "A registered 500 handler produces the tested JSON response when server exceptions are not re-raised.",
                constraints={"starlette_testclient": {"raise_server_exceptions": False}},
                stimulus_notes="Starlette ServerErrorMiddleware and TestClient exception policy are part of this observed path.",
                supporting_sources=[
                    {
                        "path": "tests/test_exception_handlers.py",
                        "start_line": 53,
                        "end_line": 79,
                        "role": "500 handler registration and response assertion",
                    },
                ],
            ),
        },
    },
    "tests/test_extra_routes.py": {
        "supporting_sources": [
            {
                "path": "tests/test_extra_routes.py",
                "start_line": 10,
                "end_line": 49,
                "role": "typed request-body and response route setup",
            },
        ],
        "functions": {
            "test_delete": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A DELETE route parses a typed body and returns the tested JSON, including the Pydantic default price.",
            ),
            "test_patch": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A PATCH route parses a typed body and returns the tested JSON, including the Pydantic default price.",
            ),
            "test_head": _case(
                ["app-routing", "response-serialization"],
                ["http.status"],
                "The HEAD route matches and exposes the asserted custom response header.",
                contract_gate="The custom-header assertion needs a single-header projection; the current ordered-header selector would over-assert unrelated headers.",
                stimulus_notes="HEAD body suppression and TestClient behavior are Starlette-owned.",
            ),
            "test_options": _case(
                ["app-routing", "response-serialization"],
                ["http.status"],
                "The OPTIONS route matches and exposes the asserted custom response header.",
                contract_gate="The custom-header assertion needs a single-header projection; the current ordered-header selector would over-assert unrelated headers.",
            ),
            "test_trace": _case(
                ["app-routing", "response-serialization"],
                ["http.status"],
                "The TRACE route is registered and returns a JSONResponse with the asserted content type.",
                contract_gate="The content-type assertion needs a dedicated header projection; the current ordered-header selector would over-assert unrelated headers.",
                stimulus_notes="Generic route dispatch and JSONResponse framing remain in the Starlette-RS contract.",
            ),
        },
    },
    "tests/test_get_model_definitions_formfeed_escape.py": {
        "supporting_sources": [
            {
                "path": "tests/test_get_model_definitions_formfeed_escape.py",
                "start_line": 7,
                "end_line": 36,
                "role": "nested Pydantic models and route setup",
            },
        ],
        "functions": {
            "test_get": _case(
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "The endpoint returns a nested Facility response for the supplied path input; the Address docstring is not observed in this function.",
            ),
        },
    },
    "tests/test_http_connection_injection.py": {
        "supporting_sources": [
            {
                "path": "tests/test_http_connection_injection.py",
                "start_line": 6,
                "end_line": 16,
                "role": "HTTPConnection dependency, app-state read, and HTTP route setup",
            },
            {
                "path": "tests/test_http_connection_injection.py",
                "start_line": 19,
                "end_line": 25,
                "role": "WebSocket route injects the same HTTPConnection dependency and sends its value",
            },
            {
                "path": "tests/test_http_connection_injection.py",
                "start_line": 31,
                "end_line": 39,
                "role": "TestClient assertions for the HTTP response and WebSocket JSON message",
            },
            {
                "path": "fastapi/requests.py",
                "start_line": 1,
                "end_line": 1,
                "role": "Starlette HTTPConnection re-export",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 371,
                "role": "FastAPI classifies HTTPConnection as a special dependency parameter",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 709,
                "end_line": 714,
                "role": "FastAPI supplies the HTTP request or WebSocket object to the HTTPConnection dependency",
            },
            {
                "path": "starlette/requests.py",
                "start_line": 80,
                "end_line": 107,
                "role": "Starlette HTTPConnection accepts HTTP and WebSocket scopes and exposes the owning app",
            },
            {
                "path": "starlette/applications.py",
                "start_line": 54,
                "end_line": 57,
                "role": "Starlette creates the application state object",
            },
            {
                "path": "starlette/datastructures.py",
                "start_line": 664,
                "end_line": 686,
                "role": "Starlette app.state attribute storage and lookup",
            },
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "websocket.messages"],
        "functions": {
            "test_value_extracting_by_http": _case(
                ["dependency-security", "response-serialization"],
                ["http.status"],
                "The dependency-wave ASGI case injects HTTPConnection, reads app.state.marker, and returns that value; the supported status selector covers the asserted successful response.",
                contract_gate="The source also asserts response.json() == 42. The workflow exposes raw body bytes but no semantic JSON-value selector, so body equality is gated rather than treating wire-byte equality as the source assertion.",
                stimulus_notes="Use fastapi.dependency-wave.http-connection-injection.test-value-extracting-by-http in tests/fixtures/input-recipes/parity/dependency-wave.yaml. The docs-reference-asgi candidate uses /http, but its associated workload registers /connection, so it does not exercise this function. The source's TestClient.get call is only a transport harness; direct ASGI input covers FastAPI behavior, while generic TestClient behavior remains in the Starlette-RS contract. HTTPConnection.app and app.state are Starlette-owned; special dependency classification and binding are FastAPI integration.",
            ),
            "test_value_extracting_by_ws": _case(
                ["dependency-security"],
                ["websocket.messages"],
                "A dedicated WebSocket ASGI case injects HTTPConnection into a dependency, reads app.state.marker, and observes the route's outgoing text message.",
                contract_gate="The source asserts receive_json() == 42, while the workflow selector exposes WebSocket text frames without decoding JSON. The decoded value assertion remains gated; TestClient websocket_connect/receive_json and context-manager behavior belong to the separate Starlette-RS contract.",
                stimulus_notes="Use fastapi.http-connection-injection.websocket-app-state in tests/fixtures/input-recipes/parity/http-connection-injection-websocket.yaml. The docs-reference-asgi candidate requests /ws, but its associated workload registers /connection/ws, so it does not exercise this function. The dedicated case observes only application messages, not TestClient handshake or close behavior. HTTPConnection.app and app.state are Starlette-owned; special dependency classification and binding are FastAPI integration.",
            ),
        },
    },
    "tests/test_infer_param_optionality.py": {
        "supporting_sources": [
            {
                "path": "tests/test_infer_param_optionality.py",
                "start_line": 12,
                "end_line": 44,
                "role": "route declarations, path inference, and optional query parameters",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 291,
                "end_line": 301,
                "role": "path parameter detection",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 491,
                "end_line": 505,
                "role": "parameter field construction",
            },
        ],
        "functions": {
            "test_get_users": _case(
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "Requesting /users reaches a registered /users/ route after the test client follows Starlette's slash redirect.",
                constraints={"starlette_testclient": {"follow_redirects": True}},
                stimulus_notes="The function asserts the final response only, not redirect status or Location.",
            ),
            "test_get_user": _case(
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "A required path value is inferred from the endpoint signature and returned by the route.",
            ),
            "test_get_items_1": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "The optional query parameter is omitted and the endpoint returns the default-backed response after the slashless /items request follows Starlette's redirect.",
                constraints={"starlette_testclient": {"follow_redirects": True}},
                stimulus_notes="The function asserts the final response only, not redirect status or Location.",
            ),
            "test_get_items_2": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "The optional query parameter is supplied and appears in the endpoint response after the slashless /items request follows Starlette's redirect.",
                constraints={"starlette_testclient": {"follow_redirects": True}},
                stimulus_notes="The function asserts the final response only, not redirect status or Location.",
            ),
            "test_get_item_1": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A path parameter is supplied while the optional query parameter is omitted.",
            ),
            "test_get_item_2": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A path parameter and the optional query parameter are both supplied.",
            ),
            "test_get_users_items": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A required path value inferred through nested router prefixes reaches the endpoint; the slashless request follows Starlette's redirect.",
                constraints={"starlette_testclient": {"follow_redirects": True}},
                stimulus_notes="The final response is observed; redirect mechanics are Starlette-owned.",
            ),
            "test_get_users_item": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A required path value and optional query parameter inferred through nested router prefixes reach the full item endpoint.",
            ),
        },
    },
    "tests/test_pydanticv2_dataclasses_uuid_stringified_annotations.py": {
        "supporting_sources": [
            {
                "path": "tests/test_pydanticv2_dataclasses_uuid_stringified_annotations.py",
                "start_line": 12,
                "end_line": 36,
                "role": "dataclass response model and route setup",
            },
        ],
        "functions": {
            "test_annotations": _case(
                ["response-serialization"],
                ["http.status"],
                "A dataclass response contains a generated UUID that is checked by a UUID predicate, not compared to a fixed value.",
                contract_gate="The JSON assertion needs a predicate selector for the generated UUID field; a literal body comparison would be unstable, so the body is not represented by the current selectors.",
                stimulus_notes="The UUID format/conversion is Pydantic behavior under its pinned public contract.",
            ),
        },
    },
    "tests/test_response_by_alias.py": {
        "supporting_sources": [
            {
                "path": "tests/test_response_by_alias.py",
                "start_line": 9,
                "end_line": 71,
                "role": "model aliases, endpoint variants, and response configuration",
            },
        ],
        "functions": {
            "test_read_dict": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned dict is serialized using field names when by-alias is disabled.",
            ),
            "test_read_model": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned model is serialized using field names when by-alias is disabled.",
            ),
            "test_read_list": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned model list is serialized using field names when by-alias is disabled.",
            ),
            "test_read_dict_by_alias": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned dict is serialized using aliases under the response-model by-alias default.",
            ),
            "test_read_model_by_alias": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned model is serialized using aliases under the response-model by-alias default.",
            ),
            "test_read_list_by_alias": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned model list is serialized using aliases under the response-model by-alias default.",
            ),
            "test_read_dict_no_alias": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned dict without an alias remains serialized with its field name.",
            ),
            "test_read_model_no_alias": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned model without an alias remains serialized with its field name.",
            ),
            "test_read_list_no_alias": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A returned model list without aliases remains serialized with field names.",
            ),
        },
    },
    "tests/test_route_scope.py": {
        "supporting_sources": [
            {
                "path": "tests/test_route_scope.py",
                "start_line": 9,
                "end_line": 22,
                "role": "GET route and unsupported-method request setup",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1126,
                "end_line": 1260,
                "role": "FastAPI route integration with inherited Starlette routing",
            },
        ],
        "functions": {
            "test_invalid_method_doesnt_match": _case(
                ["app-routing"],
                ["http.status"],
                "POST does not match the path's GET route and the router returns 405; this observes no FastAPI error object or exception handler.",
                stimulus_notes="Generic 405 method matching is Starlette-owned and tracked by the Starlette 1.6.0 source crosswalk.",
            ),
        },
    },
    "tests/test_security_api_key_header.py": {
        "module_observation_selectors": ["http.status", "openapi.document"],
        "supporting_sources": [
            {
                "path": "tests/test_security_api_key_header.py",
                "start_line": 7,
                "end_line": 26,
                "role": "APIKeyHeader security dependency, nested current-user dependency, User model, and route setup",
            },
            {
                "path": "fastapi/security/api_key.py",
                "start_line": 11,
                "end_line": 52,
                "role": "required API-key behavior, including the 401 challenge and missing-key branch",
            },
            {
                "path": "fastapi/security/api_key.py",
                "start_line": 179,
                "end_line": 233,
                "role": "APIKeyHeader construction, default scheme name, and request-header extraction",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 271,
                "end_line": 347,
                "role": "FastAPI constructs recursive dependency nodes from endpoint signatures",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 656,
                "end_line": 680,
                "role": "FastAPI invokes and caches resolved sub-dependencies",
            },
            {
                "path": "fastapi/exception_handlers.py",
                "start_line": 11,
                "end_line": 17,
                "role": "FastAPI renders Starlette HTTPException status, detail, and explicit headers as JSON",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 341,
                "role": "FastAPI serializes endpoint values and response-model values",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 99,
                "end_line": 156,
                "role": "FastAPI discovers security dependencies and emits their named OpenAPI schemes and requirements",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 311,
                "end_line": 356,
                "role": "FastAPI attaches dependency-derived security metadata to each OpenAPI operation",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1070,
                "end_line": 1120,
                "role": "FastAPI generates and serves the complete OpenAPI document at its configured endpoint",
            },
        ],
        "functions": {
            "test_security_api_key": _case(
                ["dependency-security", "response-serialization"],
                ["http.status"],
                "The required-key workflow case exercises a supplied APIKeyHeader through FastAPI dependency resolution; only the asserted success status is safely selected because parsed-JSON equality is not workflow-supported.",
                contract_gate="The test also asserts the parsed JSON value. The `http.body.json` selector is not workflow-supported, and selecting raw body bytes would require wire-format equality beyond response.json() equality.",
                stimulus_notes="The existing independent case exercises required-header extraction but uses a separate route and direct Security parameter; it does not reproduce this module's nested Depends(get_current_user) and User response value.",
                supporting_sources=[
                    {
                        "path": "tests/test_security_api_key_header.py",
                        "start_line": 29,
                        "end_line": 32,
                        "role": "successful required-key assertion checks status and parsed JSON value",
                    },
                ],
            ),
            "test_security_api_key_no_key": _case(
                ["dependency-security", "response-serialization"],
                ["http.status"],
                "The required-key missing case exercises APIKeyHeader rejection; only the asserted 401 status is selected because the body JSON and individual challenge-header selectors are unavailable.",
                contract_gate="The test also asserts the parsed JSON detail and exact WWW-Authenticate value. The parsed-JSON selector is not workflow-supported, while the available ordered-header selector would assert unrelated headers too.",
                stimulus_notes="The independent required-key missing case exercises the same FastAPI APIKeyHeader failure branch; response detail and challenge value remain outside the selected observation contract.",
                supporting_sources=[
                    {
                        "path": "tests/test_security_api_key_header.py",
                        "start_line": 35,
                        "end_line": 39,
                        "role": "missing-key assertions check 401, parsed detail, and WWW-Authenticate challenge",
                    },
                ],
            ),
            "test_openapi_schema": _case(
                ["dependency-security", "openapi-docs"],
                ["http.status", "openapi.document"],
                "The source asserts a successful OpenAPI response and its complete parsed JSON snapshot; the dedicated independent case selects the whole parsed document with the root JSON pointer and exercises APIKeyHeader's default scheme name.",
                supporting_sources=[
                    {
                        "path": "tests/test_security_api_key_header.py",
                        "start_line": 42,
                        "end_line": 70,
                        "role": "OpenAPI test asserts status and the complete security scheme and operation snapshot",
                    },
                ],
            ),
        },
    },
    "tests/test_starlette_exception.py": {
        "supporting_sources": [
            {
                "path": "tests/test_starlette_exception.py",
                "start_line": 4,
                "end_line": 39,
                "role": "Starlette exception import and app setup",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1000,
                "end_line": 1005,
                "role": "FastAPI registers the Starlette HTTPException handler",
            },
            {
                "path": "fastapi/exception_handlers.py",
                "start_line": 11,
                "end_line": 17,
                "role": "HTTPException JSON response handler",
            },
        ],
        "functions": {
            "test_get_item": _case(
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "The existing-item request succeeds and does not enter either exception branch.",
            ),
            "test_get_starlette_item": _case(
                ["app-routing", "response-serialization"],
                ["http.status", "http.body.json"],
                "The existing-item request succeeds and does not enter the Starlette HTTPException branch.",
            ),
            "test_get_starlette_item_not_found": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A Starlette HTTPException raised by the route is handled by FastAPI and returned as JSON.",
                contract_gate="The x-error absence assertion needs a response-header absence predicate; the test does not assert the complete ordered header set.",
                stimulus_notes="The function observes HTTP status/body and header absence, not the exception object.",
            ),
        },
    },
    "tests/test_stream_bare_type.py": {
        "supporting_sources": [
            {
                "path": "tests/test_stream_bare_type.py",
                "start_line": 17,
                "end_line": 25,
                "role": "sync/async generator route setup",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 647,
                "end_line": 681,
                "role": "JSONL generator response execution",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 1071,
                "end_line": 1101,
                "role": "JSONL response detection and emission",
            },
        ],
        "functions": {
            "test_stream_bare_async_iterable": _case(
                ["app-routing", "response-serialization"],
                ["http.status"],
                "The async bare iterable is emitted as JSON Lines and the test compares parsed line items after stripping whitespace.",
                contract_gate="The asserted content type needs a dedicated header selector, and parsed JSONL items need a line-oriented selector; exact bytes overstate the assertion and JSON-body parsing does not model multiple lines.",
                stimulus_notes="The buffered test does not observe chunk boundaries, cancellation, or backpressure.",
            ),
            "test_stream_bare_sync_iterable": _case(
                ["app-routing", "response-serialization"],
                ["http.status"],
                "The sync bare iterable is emitted as JSON Lines and the test compares parsed line items after stripping whitespace.",
                contract_gate="The asserted content type needs a dedicated header selector, and parsed JSONL items need a line-oriented selector; exact bytes overstate the assertion and JSON-body parsing does not model multiple lines.",
                stimulus_notes="The buffered test does not observe chunk boundaries, cancellation, or backpressure.",
            ),
        },
    },
    "tests/test_sub_callbacks.py": {
        "supporting_sources": [
            {
                "path": "tests/test_sub_callbacks.py",
                "start_line": 25,
                "end_line": 74,
                "role": "callback configuration and ordinary route setup",
            },
        ],
        "functions": {
            "test_get": _case(
                ["app-routing", "request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A valid Invoice is posted to the ordinary route; this function neither invokes callback routes nor observes their OpenAPI metadata.",
                stimulus_notes="Pydantic handles the invoice body model; callback behavior is covered only by separate OpenAPI observations.",
            ),
        },
    },
    "tests/test_tuples.py": {
        "supporting_sources": [
            {
                "path": "tests/test_tuples.py",
                "start_line": 9,
                "end_line": 25,
                "role": "nested/fixed tuple Pydantic model definitions and route setup",
            },
        ],
        "functions": {
            "test_model_with_tuple_valid": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A request with valid nested tuple data is parsed and returned.",
            ),
            "test_model_with_tuple_invalid": _case(
                ["request-validation"],
                ["http.status"],
                "A request with a tuple of invalid length is rejected; the test checks status only.",
                stimulus_notes="Tuple length and nested-model validation are Pydantic-owned.",
            ),
            "test_tuple_with_model_valid": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A fixed-length tuple containing Coordinate models is accepted and returned.",
            ),
            "test_tuple_with_model_invalid": _case(
                ["request-validation"],
                ["http.status"],
                "A fixed-length tuple with a length mismatch is rejected; the test checks status only.",
                stimulus_notes="Tuple length and nested-model validation are Pydantic-owned.",
            ),
        },
    },
    "tests/test_validate_response.py": {
        "supporting_sources": [
            {
                "path": "tests/test_validate_response.py",
                "start_line": 10,
                "end_line": 31,
                "role": "optional response model and route setup",
            },
        ],
        "functions": {
            "test_valid_none_data": _case(
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "An optional response model fills the omitted owner_ids field with null.",
            ),
            "test_valid_none_none": _case(
                ["request-validation", "response-serialization"],
                ["http.status", "http.body.json"],
                "A query boolean selects a None response accepted by an optional response model.",
                stimulus_notes="Optional model parsing/serialization is Pydantic-owned under the pinned identity.",
            ),
        },
    },
}
