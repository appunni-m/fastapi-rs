#!/usr/bin/env python3
"""Build the FastAPI source compatibility atlas and input-only fixture backlog.

The generator reads the pinned FastAPI and Starlette source trees plus the
Starlette-RS contract catalog. It does not import either package or copy
upstream tests, documentation examples, or expected outputs.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml
from public_candidate_review_schema import (
    PublicCandidateReviewSchemaError,
    validate_public_candidate_review_schema,
)
from source_api_review_schema import (
    SourceApiReviewSchemaError,
    validate_source_api_review_schema,
    validate_source_api_selection,
)

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_VERSION = "0.141.1"
FASTAPI_COMMIT = "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"
STARLETTE_VERSION = "1.6.0"
STARLETTE_COMMIT = "4f250d6b814587e20c5365f0a5f0c4d42bcb929f"
STARLETTE_RS_AREAS = {
    "asgi-http-websocket-lifespan",
    "routing-converters-mounts-hosts-and-errors",
    "applications-requests-responses-background-concurrency",
    "middleware-authentication-endpoints-datastructures-status",
    "wsgi-static-files-templates-schemas-configuration-testclient",
    "streaming-headers-cookies-errors-and-cleanup",
}
ASGI_WORKFLOW_SCHEMA_PATH = Path("tests/fixtures/schemas/python-asgi-workflow-v2.schema.json")
ASGI_WORKFLOW_INPUT_PATH = Path("tests/fixtures/inputs/parity/first-asgi-request.json")
ASGI_WORKFLOW_SCHEMA_ID = "fastapi-rs/python-asgi-workflow@2"
CALLABLE_CLASSIFICATION_REVIEW_SCHEMA = "fastapi-callable-classification-review/v1"
IMPORT_BINDING_CLASSIFICATION_REVIEW_SCHEMA = "fastapi-starlette-import-binding-review/v1"
REVIEWED_CALLABLE_KINDS = {
    "classmethod",
    "function",
    "async_function",
    "method",
    "property_getter",
    "protocol_method",
}
# Curated mappings for sources that cannot be classified reliably from names
# alone. These describe source evidence only; they never embed upstream test
# bodies or expected results.
TEST_REVIEW_MAPPINGS = {
    "tests/test_router_events.py": {
        "feature_ids": ["websocket-lifecycle", "public-api-errors"],
        "module_observation_selectors": [
            "asgi.lifespan.event_order",
            "asgi.lifespan.startup",
            "asgi.lifespan.shutdown",
            "asgi.lifespan.application_errors",
            "asgi.lifespan.workload_trace",
            "http.status",
            "http.body.bytes",
            "python.warnings",
            "warnings.category_message",
        ],
        "rationale": "FastAPI app and included-router lifecycle callbacks are driven through the public ASGI lifespan protocol, and the legacy on_event case selects construction and action warning records. TestClient behavior belongs to Starlette-RS.",
        "stimulus_notes": "Construct the app and nested routers from the input recipe, drive ASGI lifespan startup/request/shutdown, record callback order and request-visible lifespan state, and capture selected warnings from legacy on_event registration and actions. This does not claim TestClient.app_state.",
        "supporting_sources": [
            {
                "path": "tests/test_router_events.py",
                "start_line": 27,
                "end_line": 118,
                "role": "deprecated app/router event handlers and application/router lifespan state",
            },
            {
                "path": "tests/test_router_events.py",
                "start_line": 114,
                "end_line": 245,
                "role": "nested router lifespan state merging and precedence",
            },
            {
                "path": "tests/test_router_events.py",
                "start_line": 248,
                "end_line": 348,
                "role": "async shutdown and sync/async generator lifespan variants",
            },
        ],
    },
    "tests/test_invalid_path_param.py": {
        "feature_ids": ["request-validation", "public-api-errors"],
        "module_observation_selectors": [
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
        ],
        "rationale": "Invalid path-parameter declarations raise while the FastAPI route is registered, before ASGI dispatch.",
        "stimulus_notes": "Pass each route declaration through the per-case app factory and observe constructor outcome and exact public exception metadata.",
    },
    "tests/test_invalid_sequence_param.py": {
        "feature_ids": ["request-validation", "public-api-errors"],
        "module_observation_selectors": [
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
        ],
        "rationale": "Invalid sequence and mapping parameter declarations raise during FastAPI route registration.",
        "stimulus_notes": "Pass each route declaration through the per-case app factory and observe constructor outcome and exact public exception metadata.",
    },
    "tests/test_response_model_invalid.py": {
        "feature_ids": ["response-serialization", "public-api-errors"],
        "module_observation_selectors": [
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
        ],
        "rationale": "Invalid response-model annotations raise when FastAPI registers the route, before a request can run.",
        "stimulus_notes": "Pass each invalid return annotation or response model through the per-case app factory and observe exact construction errors.",
    },
    "tests/test_pydantic_v1_error.py": {
        "feature_ids": ["request-validation", "response-serialization", "public-api-errors"],
        "module_observation_selectors": [
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
        ],
        "rationale": "FastAPI rejects Pydantic v1 models at parameter, return, response-model, additional-response, union, and sequence registration boundaries.",
        "stimulus_notes": "Construct each route under the pinned Pydantic v2 profile and compare the exact FastAPI construction exception; upstream skips this module on Python 3.14+.",
    },
    "tests/test_callable_endpoint.py": {
        "feature_ids": ["app-routing", "request-validation"],
        "rationale": "A partial endpoint is registered through the FastAPI route API and invoked with a query input.",
    },
    "tests/test_orjson_response_class.py": {
        "feature_ids": ["response-serialization", "public-api-errors"],
        "rationale": "The test selects the deprecated public ORJSONResponse and observes encoded response behavior and the deprecation warning.",
    },
    "tests/test_serialize_response.py": {
        "feature_ids": ["response-serialization"],
        "rationale": "Response-model declarations are exercised for scalar, coercion, and list serialization.",
    },
    "tests/test_skip_defaults.py": {
        "feature_ids": ["response-serialization"],
        "rationale": "Routes exercise response_model_exclude_unset, response_model_exclude_defaults, and response_model_exclude_none.",
    },
    "tests/test_stream_cancellation.py": {
        "feature_ids": ["response-serialization"],
        "module_observation_selectors": [
            "asgi.cancellation.cancelled_caught",
            "http.status",
            "http.headers.ordered",
        ],
        "rationale": "FastAPI's raw StreamingResponse and JSON Lines async-generator paths must remain cancellable when their generators contain no await.",
        "stimulus_notes": "Build each independent infinite stream through the public route API, keep the ASGI receive channel open, cancel the request inside the declared timeout, and compare the selected cancellation outcome plus response status and headers. This does not claim stream completion or byte-for-byte partial bodies.",
        "supporting_sources": [
            {
                "path": "tests/test_stream_cancellation.py",
                "start_line": 24,
                "end_line": 39,
                "role": "raw and JSONL async generators with no internal await",
            },
            {
                "path": "tests/test_stream_cancellation.py",
                "start_line": 42,
                "end_line": 75,
                "role": "ASGI request harness and bounded cancellation observation",
            },
            {
                "path": "docs/en/docs/advanced/custom-response.md",
                "start_line": 174,
                "end_line": 194,
                "role": "StreamingResponse and cancellation checkpoints for infinite streams",
            },
            {
                "path": "docs/en/docs/tutorial/stream-json-lines.md",
                "start_line": 75,
                "end_line": 85,
                "role": "FastAPI async iterable JSON Lines response behavior",
            },
        ],
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/stream-cancellation.yaml",
                "case_ids": [
                    "fastapi.stream-cancellation.raw-async-generator",
                    "fastapi.stream-cancellation.jsonl-async-generator",
                ],
                "observation_selectors": [
                    "asgi.cancellation.cancelled_caught",
                    "http.headers.ordered",
                    "http.status",
                ],
            },
        ],
    },
    "tests/test_tutorial/test_async_tests/test_main_a.py": {
        "feature_ids": ["app-routing"],
        "rationale": "The tutorial test runs an async FastAPI app and observes an HTTP request to its registered route.",
        "supporting_sources": [
            {
                "path": "docs_src/async_tests/app_a_py310/main.py",
                "start_line": 6,
                "end_line": 8,
                "role": "documented async app route",
            },
            {
                "path": "docs_src/async_tests/app_a_py310/test_main.py",
                "start_line": 9,
                "end_line": 14,
                "role": "documented async HTTP stimulus",
            },
        ],
    },
    "tests/test_tutorial/test_background_tasks/test_tutorial001.py": {
        "feature_ids": ["response-serialization"],
        "rationale": "The tutorial request observes the response and a background file effect.",
        "supporting_sources": [
            {
                "path": "docs_src/background_tasks/tutorial001_py310.py",
                "start_line": 12,
                "end_line": 15,
                "role": "FastAPI endpoint and background task",
            },
        ],
    },
    "tests/test_tutorial/test_background_tasks/test_tutorial002.py": {
        "feature_ids": ["dependency-security", "response-serialization"],
        "rationale": "The tutorial request observes a dependency-injected response and background task effects.",
        "supporting_sources": [
            {
                "path": "docs_src/background_tasks/tutorial002_py310.py",
                "start_line": 11,
                "end_line": 24,
                "role": "dependency and background task",
            },
            {
                "path": "docs_src/background_tasks/tutorial002_an_py310.py",
                "start_line": 13,
                "end_line": 26,
                "role": "Annotated dependency variant",
            },
        ],
    },
    "tests/test_tutorial/test_custom_response/test_tutorial007.py": {
        "feature_ids": ["response-serialization"],
        "rationale": "The tutorial observes bytes emitted by a streaming response.",
        "supporting_sources": [
            {
                "path": "docs_src/custom_response/tutorial007_py310.py",
                "start_line": 8,
                "end_line": 16,
                "role": "streaming response endpoint",
            },
        ],
    },
    "tests/test_tutorial/test_custom_response/test_tutorial009c.py": {
        "feature_ids": ["response-serialization"],
        "rationale": "The tutorial observes a response produced by a custom Response.render implementation.",
        "supporting_sources": [
            {
                "path": "docs_src/custom_response/tutorial009c_py310.py",
                "start_line": 9,
                "end_line": 19,
                "role": "custom response class and route",
            },
        ],
    },
    "tests/test_tutorial/test_testing/test_main_b.py": {
        "feature_ids": ["request-validation"],
        "rationale": "The tutorial test invokes a FastAPI app with Header extraction and a Pydantic request model, including invalid requests.",
        "supporting_sources": [
            {
                "path": "docs_src/app_testing/app_b_py310/main.py",
                "start_line": 14,
                "end_line": 35,
                "role": "header and request model endpoint",
            },
            {
                "path": "docs_src/app_testing/app_b_py310/test_main.py",
                "start_line": 8,
                "end_line": 65,
                "role": "valid and invalid HTTP inputs",
            },
            {
                "path": "docs_src/app_testing/app_b_an_py310/main.py",
                "start_line": 14,
                "end_line": 37,
                "role": "Annotated header and request model variant",
            },
        ],
    },
    "tests/test_tutorial/test_testing/test_tutorial003.py": {
        "feature_ids": ["public-api-errors", "websocket-lifecycle"],
        "module_observation_selectors": [
            "http.status",
            "http.body.bytes",
            "asgi.lifespan.event_order",
            "asgi.lifespan.startup",
            "asgi.lifespan.shutdown",
            "asgi.lifespan.workload_trace",
        ],
        "rationale": "The test checks the deprecated startup-event API warning and exercises the startup lifecycle through the tutorial app.",
        "stimulus_notes": "The direct-ASGI case observes startup-driven request state and cleanup. It does not capture the separate import-time DeprecationWarning because warning observations are not expressible by the current v3 workflow.",
        "contract_gate": "The upstream test also asserts an import-time DeprecationWarning; exact warning category/message capture remains planned and is not claimed by this input workflow.",
        "supporting_sources": [
            {
                "path": "docs_src/app_testing/tutorial003_py310.py",
                "start_line": 9,
                "end_line": 24,
                "role": "startup event and route",
            },
        ],
    },
    "tests/test_tutorial/test_testing/test_tutorial004.py": {
        "feature_ids": ["websocket-lifecycle"],
        "module_observation_selectors": [
            "http.status",
            "http.body.bytes",
            "asgi.lifespan.event_order",
            "asgi.lifespan.startup",
            "asgi.lifespan.shutdown",
            "asgi.lifespan.workload_trace",
        ],
        "rationale": "The tutorial observes lifespan startup, request-time state, and shutdown cleanup.",
        "supporting_sources": [
            {
                "path": "docs_src/app_testing/tutorial004_py310.py",
                "start_line": 9,
                "end_line": 18,
                "role": "lifespan app definition",
            },
            {
                "path": "docs_src/app_testing/tutorial004_py310.py",
                "start_line": 26,
                "end_line": 43,
                "role": "startup, request state, and cleanup observations",
            },
        ],
    },
}


def merge_test_review_mappings(additions: dict[str, dict[str, Any]]) -> None:
    """Merge curated entries without discarding earlier function-level review."""
    for path, addition in additions.items():
        current = TEST_REVIEW_MAPPINGS.setdefault(path, {})
        for key, value in addition.items():
            if key == "functions":
                current_functions = current.setdefault(key, {})
                for function_name, function_value in value.items():
                    current_functions.setdefault(function_name, {}).update(function_value)
            elif key == "supporting_sources":
                current[key] = [*current.get(key, []), *value]
            else:
                current[key] = value


merge_test_review_mappings(
    {
        "tests/test_tutorial/test_custom_request_and_route/test_tutorial003.py": {
            "feature_ids": [],
            "rationale": "The tutorial contrasts a normal app route with a router using a custom APIRoute subclass that adds a response header.",
            "supporting_sources": [
                {
                    "path": "docs_src/custom_request_and_route/tutorial003_py310.py",
                    "start_line": 8,
                    "end_line": 22,
                    "role": "custom TimedRoute response handler",
                },
                {
                    "path": "docs_src/custom_request_and_route/tutorial003_py310.py",
                    "start_line": 25,
                    "end_line": 36,
                    "role": "normal route and custom router registration",
                },
            ],
            "functions": {
                "test_get": {
                    "feature_ids": ["app-routing"],
                    "observation_selectors": [
                        "http.status",
                        "http.headers.ordered",
                        "http.body.json",
                    ],
                    "rationale": "The plain app route returns its JSON body and does not gain the router-specific timing header.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_tutorial/test_custom_request_and_route/test_tutorial003.py",
                            "start_line": 22,
                            "end_line": 26,
                            "role": "request and response observations",
                        }
                    ],
                },
                "test_get_timed": {
                    "feature_ids": ["app-routing", "response-serialization"],
                    "observation_selectors": [
                        "http.status",
                        "http.headers.ordered",
                        "http.body.json",
                    ],
                    "rationale": "The custom APIRoute route returns JSON and adds X-Response-Time.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_tutorial/test_custom_request_and_route/test_tutorial003.py",
                            "start_line": 28,
                            "end_line": 32,
                            "role": "request and response observations",
                        }
                    ],
                },
            },
        },
        "tests/test_response_model_data_filter.py": {
            "feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "rationale": "Each test invokes a separately configured response model; module-level route and model declarations provide context for the test functions.",
            "supporting_sources": [
                {
                    "path": "tests/test_response_model_data_filter.py",
                    "start_line": 30,
                    "end_line": 53,
                    "role": "response models and route setup",
                },
            ],
            "functions": {
                "test_filter_top_level_model": {
                    "rationale": "Top-level response-model field filtering.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_response_model_data_filter.py",
                            "start_line": 59,
                            "end_line": 63,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_filter_second_level_model": {
                    "rationale": "Nested response-model field filtering.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_response_model_data_filter.py",
                            "start_line": 66,
                            "end_line": 71,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_list_of_models": {
                    "rationale": "Filtering each item in a list of nested response models.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_response_model_data_filter.py",
                            "start_line": 74,
                            "end_line": 79,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
            },
        },
        "tests/test_response_model_data_filter_no_inheritance.py": {
            "feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "rationale": "Each test exercises field filtering where returned and declared model classes are unrelated; module-level declarations distinguish this case from inheritance-based filtering.",
            "supporting_sources": [
                {
                    "path": "tests/test_response_model_data_filter_no_inheritance.py",
                    "start_line": 8,
                    "end_line": 55,
                    "role": "unrelated response-model and route setup",
                },
            ],
            "functions": {
                "test_filter_top_level_model": {
                    "rationale": "Top-level field filtering across unrelated model classes.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_response_model_data_filter_no_inheritance.py",
                            "start_line": 61,
                            "end_line": 65,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_filter_second_level_model": {
                    "rationale": "Nested field filtering across unrelated model classes.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_response_model_data_filter_no_inheritance.py",
                            "start_line": 68,
                            "end_line": 74,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_list_of_models": {
                    "rationale": "Filtering a list of nested unrelated response models.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_response_model_data_filter_no_inheritance.py",
                            "start_line": 76,
                            "end_line": 81,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
            },
        },
        "tests/test_serialize_response_model.py": {
            "feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "rationale": "Each function calls a distinct route configured at module scope and observes only its JSON response body.",
            "supporting_sources": [
                {
                    "path": "tests/test_serialize_response_model.py",
                    "start_line": 8,
                    "end_line": 81,
                    "role": "response model declarations and route setup",
                },
            ],
            "functions": {
                "test_valid": {
                    "rationale": "Model output with an alias and default None field.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 87,
                            "end_line": 90,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_coerce": {
                    "rationale": "Model output from an Item instance; the handler constructs Item(price='1.0'), so this case does not isolate FastAPI coercion.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 93,
                            "end_line": 100,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_validlist": {
                    "rationale": "List response-model serialization.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 103,
                            "end_line": 110,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_validdict": {
                    "rationale": "Dictionary response-model serialization.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 113,
                            "end_line": 120,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_valid_exclude_unset": {
                    "rationale": "Response serialization with unset fields excluded.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 123,
                            "end_line": 126,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_coerce_exclude_unset": {
                    "rationale": "Unset-field filtering for an Item instance constructed by the handler; this case does not isolate FastAPI coercion.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 129,
                            "end_line": 132,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_validlist_exclude_unset": {
                    "rationale": "Unset-field filtering for list response-model serialization.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 135,
                            "end_line": 142,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
                "test_validdict_exclude_unset": {
                    "rationale": "Unset-field filtering for dictionary response-model serialization.",
                    "supporting_sources": [
                        {
                            "path": "tests/test_serialize_response_model.py",
                            "start_line": 145,
                            "end_line": 152,
                            "role": "input invocation and JSON observation",
                        }
                    ],
                },
            },
        },
        "tests/test_tutorial/test_testing/test_main_a.py": {
            "functions": {
                "test_main": {
                    "feature_ids": ["app-routing", "response-serialization"],
                    "observation_selectors": ["http.status", "http.body.json"],
                    "rationale": "The wrapper executes the documented separated-app HTTP test through TestClient.",
                    "supporting_sources": [
                        {
                            "path": "docs_src/app_testing/app_a_py310/test_main.py",
                            "start_line": 8,
                            "end_line": 11,
                            "role": "HTTP request and response observation",
                        },
                        {
                            "path": "docs_src/app_testing/app_a_py310/main.py",
                            "start_line": 6,
                            "end_line": 8,
                            "role": "FastAPI route under test",
                        },
                    ],
                },
            },
        },
        "tests/test_tutorial/test_testing/test_tutorial001.py": {
            "functions": {
                "test_main": {
                    "feature_ids": ["app-routing", "response-serialization"],
                    "observation_selectors": ["http.status", "http.body.json"],
                    "rationale": "The wrapper invokes the documented TestClient request for the tutorial route.",
                    "supporting_sources": [
                        {
                            "path": "docs_src/app_testing/tutorial001_py310.py",
                            "start_line": 7,
                            "end_line": 18,
                            "role": "route and HTTP response test",
                        },
                    ],
                },
            },
        },
        "tests/test_tutorial/test_testing/test_tutorial002.py": {
            "functions": {
                "test_main": {
                    "feature_ids": ["app-routing", "response-serialization"],
                    "observation_selectors": ["http.status", "http.body.json"],
                    "rationale": "This wrapper executes only the tutorial HTTP test; its sibling WebSocket test is a separate case.",
                    "supporting_sources": [
                        {
                            "path": "docs_src/app_testing/tutorial002_py310.py",
                            "start_line": 8,
                            "end_line": 24,
                            "role": "route and HTTP response test",
                        },
                    ],
                },
            },
        },
        "tests/test_tutorial/test_testing_dependencies/test_tutorial001.py": {
            "functions": {
                "test_override_in_items_run": {
                    "feature_ids": ["dependency-security", "request-validation"],
                    "observation_selectors": ["http.status", "http.body.json"],
                    "rationale": "The app dependency override changes the response observed by an HTTP request.",
                    "supporting_sources": [
                        {
                            "path": "docs_src/dependency_testing/tutorial001_py310.py",
                            "start_line": 7,
                            "end_line": 55,
                            "role": "route, dependency override, and HTTP test",
                        },
                        {
                            "path": "docs_src/dependency_testing/tutorial001_an_py310.py",
                            "start_line": 9,
                            "end_line": 57,
                            "role": "Annotated dependency override variant",
                        },
                    ],
                },
                "test_override_in_items_with_q_run": {
                    "feature_ids": ["dependency-security", "request-validation"],
                    "observation_selectors": ["http.status", "http.body.json"],
                    "rationale": "The q input is passed through a dependency override and observed in the HTTP response.",
                    "supporting_sources": [
                        {
                            "path": "docs_src/dependency_testing/tutorial001_py310.py",
                            "start_line": 7,
                            "end_line": 55,
                            "role": "route, dependency override, and HTTP test",
                        },
                        {
                            "path": "docs_src/dependency_testing/tutorial001_an_py310.py",
                            "start_line": 9,
                            "end_line": 57,
                            "role": "Annotated dependency override variant",
                        },
                    ],
                },
                "test_override_in_items_with_params_run": {
                    "feature_ids": ["dependency-security", "request-validation"],
                    "observation_selectors": ["http.status", "http.body.json"],
                    "rationale": "Request parameters and dependency overrides determine the JSON observed over HTTP.",
                    "supporting_sources": [
                        {
                            "path": "docs_src/dependency_testing/tutorial001_py310.py",
                            "start_line": 7,
                            "end_line": 55,
                            "role": "route, dependency override, and HTTP test",
                        },
                        {
                            "path": "docs_src/dependency_testing/tutorial001_an_py310.py",
                            "start_line": 9,
                            "end_line": 57,
                            "role": "Annotated dependency override variant",
                        },
                    ],
                },
            },
        },
    }
)

TEST_EXCLUSIONS = {
    "tests/test_fastapi_cli.py": (
        "The CLI contract is subprocess based: test_fastapi_cli invokes `python -m coverage run -m fastapi dev` "
        "and checks process stdout/exit status, while test_fastapi_cli_not_installed monkeypatches "
        "fastapi.cli.cli_main. The fixed direct-ASGI workload has no subprocess runner or module-state "
        "control; process.stdout and process.exit_code remain planned selectors."
    ),
    "tests/test_orjson_response_class.py": (
        'The module calls pytest.importorskip("orjson") before defining its app. No selected locked '
        "oracle profile installs orjson, so this optional response implementation is unavailable in the "
        "pinned test environment."
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial001b.py": (
        'The module imports ORJSONResponse and calls pytest.importorskip("orjson") before running '
        "its response/OpenAPI assertions. No selected locked oracle profile installs orjson, so this "
        "optional response implementation is unavailable in the pinned test environment."
    ),
    "tests/test_tutorial/test_custom_response/test_tutorial009c.py": (
        'The module calls pytest.importorskip("orjson") and asserts the exact indented ORJSON response '
        "bytes. No selected locked oracle profile installs orjson, so this optional response implementation "
        "cannot be executed under the selected profile."
    ),
    "tests/test_deprecated_responses.py": (
        "The module exercises optional ORJSONResponse/UJSONResponse integrations through needs_orjson and "
        "needs_ujson; neither dependency is in a selected locked oracle profile. Warning capture is now "
        "supported, but these optional integrations remain unavailable in the selected profiles."
    ),
    "tests/test_stringified_annotation_dependency_py314.py": (
        "The sole test is guarded by needs_py314 and uses Python 3.14 runtime annotation evaluation. "
        "The pinned oracle profile is CPython 3.12.13 and the workload schema has no runtime matrix; "
        "adapting the annotation to run on 3.12 would change the stimulus."
    ),
    "tests/test_tutorial/test_graphql/test_tutorial001.py": (
        "The example imports Strawberry and strawberry.fastapi.GraphQLRouter, neither of which is in "
        "the selected core/standard-multipart oracle profiles. Its resolver execution and GraphQL "
        "schema are third-party behavior; FastAPI include_router integration is covered separately."
    ),
    "tests/test_tutorial/test_settings/test_app01.py": (
        "The route and OpenAPI are built around pydantic_settings.BaseSettings; pydantic-settings is "
        "not installed by the selected oracle profile. This fixture cannot reproduce the environment "
        "settings construction/assertions without changing the declared dependency profile."
    ),
    "tests/test_tutorial/test_settings/test_app03.py": (
        "The example exercises pydantic_settings.BaseSettings and .env loading, whose pydantic-settings "
        "and dotenv integrations are outside the selected oracle profile."
    ),
    "tests/test_tutorial/test_settings/test_tutorial001.py": (
        "The example exercises pydantic_settings.BaseSettings environment parsing, which is not "
        "installed by the selected oracle profile; its settings and environment assertions cannot be "
        "represented without expanding that profile."
    ),
    "tests/test_tutorial/test_sql_databases/test_tutorial001.py": (
        "The tutorial requires SQLModel, SQLAlchemy, and in-memory SQLite. SQLModel is present only in "
        "FastAPI's test dependency group, not the selected oracle profile; database/ORM behavior is not "
        "a FastAPI contract. The sibling tutorial002 mapping separately samples FastAPI response, "
        "validation, and OpenAPI behavior."
    ),
    "tests/test_tutorial/test_templates/test_tutorial001.py": (
        "The assertions depend on Jinja2 rendering and Starlette StaticFiles, both absent from the "
        "selected core/standard-multipart profile and owned by Jinja2/Starlette-RS. FastAPI's import "
        "aliases remain in the public API inventory."
    ),
    "tests/test_tutorial/test_wsgi/test_tutorial001.py": (
        "The tutorial uses third-party a2wsgi.WSGIMiddleware and Flask rather than Starlette's "
        "WSGIMiddleware; neither a2wsgi nor Flask is in the selected oracle profile. Starlette-RS's "
        "WSGI contract cannot be claimed as coverage of a2wsgi."
    ),
    "tests/test_tutorial/test_generate_clients/test_tutorial004.py": (
        "The test writes an OpenAPI JSON file in tmp_path, patches pathlib.Path during import, and "
        "asserts import-time file rewriting that removes tag prefixes from operationIds. The ASGI "
        "workflow cannot express patched imports or filesystem mutation; an HTTP/OpenAPI request "
        "would not represent this behavior."
    ),
    "tests/test_tutorial/test_python_types/test_tutorial001_tutorial002.py": "Standalone Python type tutorial; it executes plain functions and observes printed values without a FastAPI API or app.",
    "tests/test_tutorial/test_python_types/test_tutorial003.py": "Standalone Python type tutorial; it checks string concatenation and Python TypeError behavior, with no FastAPI API or app.",
    "tests/test_tutorial/test_python_types/test_tutorial004.py": "Standalone Python type tutorial; it calls a plain function and observes its string result without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial005.py": "Standalone Python type tutorial; it calls a plain typed function and observes a tuple without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial006.py": "Standalone Python type tutorial; it observes print calls from a plain function without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial007.py": "Standalone Python type tutorial; it observes a plain function tuple/set result without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial008.py": "Standalone Python type tutorial; it observes printed dictionary entries without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial008b.py": "Standalone Python type tutorial; it dynamically imports a plain function and observes printing without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial009_tutorial009b.py": "Standalone Python type tutorial; it observes a plain function with optional arguments and no FastAPI API or app.",
    "tests/test_tutorial/test_python_types/test_tutorial010.py": "Standalone Python type tutorial; it constructs and reads a plain Person object without FastAPI.",
    "tests/test_tutorial/test_python_types/test_tutorial011.py": "Standalone Pydantic tutorial; its BaseModel use is outside FastAPI's contract because no FastAPI API or app is exercised.",
    "tests/test_tutorial/test_python_types/test_tutorial013.py": "Standalone Python typing tutorial; Annotated metadata is not passed through a FastAPI API or app.",
    "tests/test_dependencies_utils.py": "This test calls the private fastapi.dependencies.utils.get_typed_annotation helper directly; it does not exercise a consumer-facing FastAPI API or app workflow.",
    "tests/test_request_params/test_cookie/test_list.py": "Comments-only unsupported boundary: repeated same-name cookie list parsing has no executable test, input, or observation; generic cookie parsing belongs to the Starlette contract.",
    "tests/test_request_params/test_cookie/test_optional_list.py": "Comments-only unsupported boundary: optional repeated same-name cookie list parsing has no executable test, input, or observation; generic cookie parsing belongs to the Starlette contract.",
    "tests/test_request_params/test_path/test_list.py": "Comments-only unsupported boundary: non-scalar Path parameters have no executable test, input, or observation.",
    "tests/test_request_params/test_path/test_optional_list.py": "Comments-only unsupported boundary: optional non-scalar Path parameters have no executable test, input, or observation.",
    "tests/test_request_params/test_path/test_optional_str.py": "Comments-only unsupported boundary: optional Path parameter behavior has no executable test, input, or observation; the precise failure mode is unresolved.",
}

TEST_FUNCTION_EXCLUSIONS = {
    "tests/test_tutorial/test_settings/test_app02.py": {
        "test_settings": (
            "Reads an environment variable into pydantic_settings.BaseSettings through an un-cached "
            "settings factory. That optional package is absent from the selected oracle profile; "
            "the dependency-override HTTP integration is covered separately."
        ),
    },
    "tests/test_datastructures.py": {
        "test_upload_file_invalid_pydantic_v2": (
            "Calls the private UploadFile._validate helper directly. The consumer-facing "
            "multipart integration is covered through HTTP; the private helper is not a "
            "separate FastAPI API contract."
        ),
        "test_default_placeholder_equals": (
            "Directly exercises DefaultPlaceholder, which FastAPI documents as an internal "
            "sentinel; equality of arbitrary Python objects has no JSON-safe workflow projection."
        ),
        "test_default_placeholder_bool": (
            "Directly exercises DefaultPlaceholder, which FastAPI documents as an internal "
            "sentinel; object truthiness has no JSON-safe workflow projection."
        ),
        "test_upload_file": (
            "Exercises generic UploadFile stream read/write/seek/close behavior directly. "
            "FastAPI-RS delegates this Starlette 1.6.0-owned behavior to Starlette-RS; FastAPI "
            "multipart parsing and route integration remain in HTTP fixtures."
        ),
    },
    "tests/test_tutorial/test_events/test_tutorial001.py": {
        "test_events": (
            "This upstream assertion depends on TestClient driving application lifespan. A "
            "separate v3 direct-ASGI fixture covers FastAPI startup callbacks and route output; "
            "TestClient context and app-state behavior are owned by the Starlette-RS contract."
        ),
    },
    "tests/test_tutorial/test_events/test_tutorial002.py": {
        "test_events": (
            "This upstream assertion depends on TestClient driving application lifespan. A "
            "separate v3 direct-ASGI fixture covers FastAPI shutdown callbacks and cleanup "
            "order; TestClient context behavior is owned by the Starlette-RS contract."
        ),
    },
    "tests/test_tutorial/test_events/test_tutorial003.py": {
        "test_events": (
            "This upstream assertion depends on TestClient driving application lifespan and "
            "exposes TestClient-managed state. A separate v3 direct-ASGI fixture covers yielded "
            "lifespan state through request scope; TestClient app_state remains Starlette-RS-owned."
        ),
    },
    "tests/test_tutorial/test_debugging/test_tutorial001.py": {
        "test_uvicorn_run_is_not_called_on_import": "Checks Python import side effects and uvicorn.run behavior, not a FastAPI consumer contract.",
        "test_uvicorn_run_called_when_run_as_main": "Checks Python __main__ execution and uvicorn.run behavior, not a FastAPI consumer contract.",
    },
    "tests/test_tutorial/test_dependencies/test_tutorial007.py": {
        "test_get_db.test_async_gen": "Exercises a plain contextlib async context manager and its close effect directly; it does not use FastAPI Depends or a request.",
    },
    "tests/test_tutorial/test_path_params/test_tutorial003b.py": {
        "test_read_users2": "Directly calls a handler and bypasses routing; the sibling HTTP test already observes route ordering through FastAPI.",
    },
    "tests/test_tutorial/test_security/test_tutorial004.py": {
        "test_verify_password": "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
        "test_get_password_hash": "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
        "test_create_access_token": "Direct PyJWT token-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
    },
    "tests/test_tutorial/test_security/test_tutorial005.py": {
        "test_verify_password": "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
        "test_get_password_hash": "Direct application password-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
        "test_create_access_token": "Direct PyJWT token-helper behavior is outside FastAPI; the neighboring HTTP auth-flow case covers FastAPI integration.",
    },
    "tests/test_ws_router.py": {
        "test_wrong_uri": (
            "This case observes only Starlette Router.not_found's generic WebSocket close; "
            "the pinned Starlette-RS contract already covers "
            "starlette.routing.WebSocketRoute.route-dispatch.router-miss-close."
        ),
    },
}

TEST_FUNCTION_EXCLUSION_EVIDENCE = {
    "tests/test_tutorial/test_settings/test_app02.py": {
        "test_settings": [
            {
                "path": "docs_src/settings/app02_py310/config.py",
                "start_line": 1,
                "end_line": 7,
                "role": "optional Pydantic Settings model read from environment",
            }
        ],
    },
    "tests/test_datastructures.py": {
        "test_upload_file_invalid_pydantic_v2": [
            {
                "path": "fastapi/datastructures.py",
                "start_line": 132,
                "end_line": 150,
                "role": "private UploadFile validator and Pydantic schema hook",
            },
        ],
        "test_default_placeholder_equals": [
            {
                "path": "fastapi/datastructures.py",
                "start_line": 153,
                "end_line": 181,
                "role": "DefaultPlaceholder and Default are internal sentinel helpers",
            },
        ],
        "test_default_placeholder_bool": [
            {
                "path": "fastapi/datastructures.py",
                "start_line": 153,
                "end_line": 181,
                "role": "DefaultPlaceholder and Default are internal sentinel helpers",
            },
        ],
        "test_upload_file": [
            {
                "path": "fastapi/datastructures.py",
                "start_line": 18,
                "end_line": 130,
                "role": "FastAPI UploadFile subclasses Starlette UploadFile and delegates stream methods",
            },
            {
                "path": "starlette/datastructures.py",
                "start_line": 410,
                "end_line": 476,
                "role": "Starlette 1.6.0 owns generic UploadFile stream operations",
            },
        ],
    },
    "tests/test_tutorial/test_debugging/test_tutorial001.py": {
        "test_uvicorn_run_is_not_called_on_import": [
            {
                "path": "docs_src/debugging/tutorial001_py310.py",
                "start_line": 14,
                "end_line": 15,
                "role": "Python __main__ guard",
            },
            {
                "path": "docs/en/docs/tutorial/debugging.md",
                "start_line": 11,
                "end_line": 28,
                "role": "documented import and server-run behavior",
            },
        ],
        "test_uvicorn_run_called_when_run_as_main": [
            {
                "path": "docs_src/debugging/tutorial001_py310.py",
                "start_line": 14,
                "end_line": 15,
                "role": "Python __main__ guard",
            },
            {
                "path": "docs/en/docs/tutorial/debugging.md",
                "start_line": 43,
                "end_line": 73,
                "role": "documented module-run behavior",
            },
        ],
    },
    "tests/test_tutorial/test_dependencies/test_tutorial007.py": {
        "test_get_db.test_async_gen": [
            {
                "path": "docs_src/dependencies/tutorial007_py310.py",
                "start_line": 1,
                "end_line": 6,
                "role": "plain async context manager example",
            },
            {
                "path": "docs/en/docs/tutorial/dependencies/dependencies-with-yield.md",
                "start_line": 15,
                "end_line": 22,
                "role": "context-manager documentation",
            },
            {
                "path": "docs/en/docs/tutorial/dependencies/dependencies-with-yield.md",
                "start_line": 32,
                "end_line": 40,
                "role": "FastAPI dependency integration context",
            },
        ],
    },
    "tests/test_tutorial/test_path_params/test_tutorial003b.py": {
        "test_read_users2": [
            {
                "path": "docs_src/path_params/tutorial003b_py310.py",
                "start_line": 6,
                "end_line": 13,
                "role": "duplicate route registrations",
            },
            {
                "path": "docs/en/docs/tutorial/path-params.md",
                "start_line": 125,
                "end_line": 129,
                "role": "documented duplicate route behavior",
            },
        ],
    },
    "tests/test_tutorial/test_security/test_tutorial004.py": {
        "test_verify_password": [
            {
                "path": "docs_src/security/tutorial004_py310.py",
                "start_line": 57,
                "end_line": 62,
                "role": "application password helper",
            }
        ],
        "test_get_password_hash": [
            {
                "path": "docs_src/security/tutorial004_py310.py",
                "start_line": 57,
                "end_line": 62,
                "role": "application password helper",
            }
        ],
        "test_create_access_token": [
            {
                "path": "docs_src/security/tutorial004_py310.py",
                "start_line": 81,
                "end_line": 89,
                "role": "application token helper",
            }
        ],
    },
    "tests/test_tutorial/test_security/test_tutorial005.py": {
        "test_verify_password": [
            {
                "path": "docs_src/security/tutorial005_py310.py",
                "start_line": 72,
                "end_line": 78,
                "role": "application password helper",
            }
        ],
        "test_get_password_hash": [
            {
                "path": "docs_src/security/tutorial005_py310.py",
                "start_line": 72,
                "end_line": 78,
                "role": "application password helper",
            }
        ],
        "test_create_access_token": [
            {
                "path": "docs_src/security/tutorial005_py310.py",
                "start_line": 96,
                "end_line": 104,
                "role": "application token helper",
            }
        ],
    },
    "tests/test_ws_router.py": {
        "test_wrong_uri": [
            {
                "path": "tests/test_ws_router.py",
                "start_line": 177,
                "end_line": 185,
                "role": "unmatched WebSocket URI and generic close-code assertion delegated to Starlette-RS",
            },
        ],
    },
}


def reviewed_case(
    feature_ids: Sequence[str],
    selectors: Sequence[str],
    rationale: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        **extra,
    }


TEST_FUNCTION_EXCLUSIONS.update(
    {
        "tests/test_compat.py": {
            "test_model_field_default_required": "Tests fastapi._compat.ModelField internals directly; this is not an app or consumer-facing API workflow.",
            "test_is_bytes_sequence_annotation_union": "Tests an internal fastapi._compat annotation helper directly, not an app workflow.",
            "test_is_uploadfile_sequence_annotation": "Tests an internal fastapi._compat annotation helper directly; the source explicitly questions this as a first-class feature.",
            "test_serialize_sequence_value_with_optional_list": "Tests the internal fastapi._compat sequence serializer directly; it does not exercise FastAPI through a public endpoint.",
            "test_serialize_sequence_value_with_optional_list_pipe_union": "Duplicates the direct internal serializer stimulus in test_serialize_sequence_value_with_optional_list; it is not an independent public workflow.",
            "test_serialize_sequence_value_with_none_first_in_union": "Tests the internal fastapi._compat sequence serializer directly; it does not exercise FastAPI through a public endpoint.",
        },
        "tests/test_datastructures.py": {
            "test_default_placeholder_equals": "Tests Default/DefaultPlaceholder helpers that FastAPI source labels for internal use.",
            "test_default_placeholder_bool": "Tests Default/DefaultPlaceholder helpers that FastAPI source labels for internal use.",
        },
        "tests/test_dependency_models.py": {
            "test_callable_classification_cache_supports_large_apps": "Inspects underscore-private callable-classification cache internals; this is an internal performance invariant, not consumer-visible behavior.",
            "test_unhashable_callable_classification": "Calls an underscore-private callable classifier directly; the public equivalent belongs in a Depends HTTP workflow if required.",
            "test_equal_callable_instances_are_cached_by_identity": "Inspects the private callable-classification cache directly; no FastAPI request or public observation is made.",
            "test_callable_return_annotations_are_not_used": "Tests the underscore-private dependency callable classifier directly; no FastAPI request or public observation is made.",
        },
        "tests/test_dependency_paramless.py": {
            "test_call_get_parameterless_without_scopes_for_coverage": "Calls the route handler directly and checks its constant return; it bypasses FastAPI's dependency/security request pipeline.",
        },
        "tests/test_router_include_context.py": {
            "test_restore_fastapi_scope_key_ignores_non_dict_fastapi_scope": "Calls private fastapi.routing._restore_fastapi_scope_key directly; it is defensive helper coverage, not a public route observation.",
        },
        "tests/test_arbitrary_types.py": {
            "test_typeadapter": "The test explicitly verifies Pydantic TypeAdapter behavior without a FastAPI app; that belongs to Pydantic's separate contract.",
        },
        "tests/test_tutorial/test_debugging/test_tutorial001.py": {
            "get_client.test": "Nested endpoint helper inside a pytest fixture, not a separately collected pytest test function.",
            "test_uvicorn_run_is_not_called_on_import": "Checks the documentation example's Uvicorn entry point with a mocked process runner; this is application launch behavior, not FastAPI's public contract.",
            "test_uvicorn_run_called_when_run_as_main": "Checks the documentation example's Uvicorn entry point with a mocked process runner; this is application launch behavior, not FastAPI's public contract.",
        },
        "tests/test_sse.py": {
            "test_keepalive_ping_async": "Patches FastAPI's explicitly private _PING_INTERVAL constant to force timing; it does not establish the public default keep-alive interval.",
            "test_keepalive_ping_sync": "Patches FastAPI's explicitly private _PING_INTERVAL constant to force timing; it does not establish the public default keep-alive interval.",
        },
    }
)

TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault("tests/test_compat.py", {}).update(
    {
        name: [
            {
                "path": "fastapi/_compat/v2.py",
                "start_line": 114,
                "end_line": 139,
                "role": "internal field compatibility helper",
            },
            {
                "path": "fastapi/_compat/v2.py",
                "start_line": 366,
                "end_line": 376,
                "role": "internal sequence serialization helper",
            },
            {
                "path": "fastapi/_compat/shared.py",
                "start_line": 156,
                "end_line": 168,
                "role": "internal annotation helper",
            },
        ]
        for name in TEST_FUNCTION_EXCLUSIONS["tests/test_compat.py"]
    }
)
TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault("tests/test_datastructures.py", {}).update(
    {
        name: [
            {
                "path": "fastapi/datastructures.py",
                "start_line": 153,
                "end_line": 181,
                "role": "source-marked internal DefaultPlaceholder helpers",
            }
        ]
        for name in TEST_FUNCTION_EXCLUSIONS["tests/test_datastructures.py"]
    }
)
TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault("tests/test_router_include_context.py", {}).update(
    {
        "test_restore_fastapi_scope_key_ignores_non_dict_fastapi_scope": [
            {
                "path": "fastapi/routing.py",
                "start_line": 908,
                "end_line": 915,
                "role": "private scope restoration helper",
            },
        ],
    }
)
TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault("tests/test_sse.py", {}).update(
    {
        name: [
            {
                "path": "fastapi/sse.py",
                "start_line": 236,
                "end_line": 241,
                "role": "private configurable keep-alive implementation constant",
            }
        ]
        for name in TEST_FUNCTION_EXCLUSIONS["tests/test_sse.py"]
    }
)
TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(
    "tests/test_tutorial/test_debugging/test_tutorial001.py", {}
).update(
    {
        "test_uvicorn_run_is_not_called_on_import": [
            {
                "path": "docs_src/debugging/tutorial001_py310.py",
                "start_line": 14,
                "end_line": 15,
                "role": "documentation example process entry point",
            },
        ],
        "test_uvicorn_run_called_when_run_as_main": [
            {
                "path": "docs_src/debugging/tutorial001_py310.py",
                "start_line": 14,
                "end_line": 15,
                "role": "documentation example process entry point",
            },
        ],
    }
)

merge_test_review_mappings(
    {
        "tests/test_compat.py": {
            "functions": {
                "test_complex": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A public endpoint accepts scalar and list union inputs and returns the parsed value.",
                ),
                "test_propagates_pydantic2_model_config": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A public endpoint parses nested models configured for an arbitrary sentinel type and returns their observable values.",
                ),
            },
        },
        "tests/test_custom_swagger_ui_redirect.py": {
            "functions": {
                "test_swagger_ui": reviewed_case(
                    ["openapi-docs"],
                    ["docs.response.status", "docs.response.headers", "docs.response.body.bytes"],
                    "The docs endpoint includes Swagger UI and the configured OAuth2 redirect URL.",
                ),
                "test_swagger_ui_oauth2_redirect": reviewed_case(
                    ["openapi-docs"],
                    ["docs.response.status", "docs.response.headers", "docs.response.body.bytes"],
                    "The configured OAuth2 redirect endpoint returns its HTML payload.",
                ),
                "test_response": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A normal JSON route response is included as a control; it does not exercise Swagger or OAuth2.",
                ),
            },
        },
        "tests/test_no_swagger_ui_redirect.py": {
            "functions": {
                "test_swagger_ui": reviewed_case(
                    ["openapi-docs"],
                    ["docs.response.status", "docs.response.body.bytes"],
                    "The docs endpoint returns Swagger UI without an OAuth2 redirect URL.",
                ),
                "test_swagger_ui_no_oauth2_redirect": reviewed_case(
                    ["openapi-docs"],
                    ["docs.response.status"],
                    "The disabled OAuth2 redirect URL has no docs route; this is a docs configuration observation, not dependency/security behavior.",
                ),
                "test_response": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A normal JSON route response is included as a control; it does not exercise Swagger or OAuth2.",
                ),
            },
        },
        "tests/test_default_response_class.py": {
            "feature_ids": ["response-serialization"],
            "replace_features": True,
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": [
                "http.status",
                "http.headers.ordered",
                "http.body.bytes",
            ],
            "rationale": "The module checks default response-class selection and inherited overrides through nested routers; response representation and content type are the observed contract.",
            "functions": {
                "test_app": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.json"],
                    "An app-level custom JSON response class determines the root route content type and JSON result.",
                    constraints={"optional_dependency": "orjson", "skip_must_remain_visible": True},
                ),
                "test_app_override": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An explicit plain-text route response class overrides the app-level default.",
                ),
            },
        },
        "tests/test_default_response_class_router.py": {
            "feature_ids": ["response-serialization"],
            "replace_features": True,
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": [
                "http.status",
                "http.headers.ordered",
                "http.body.bytes",
            ],
            "rationale": "The module checks inherited default response-class selection and explicit overrides through nested routers.",
            "functions": {
                "test_app": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.json"],
                    "The app's built-in JSON response class determines the root route result and content type.",
                ),
                "test_app_override": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An explicit plain-text route response class overrides the inherited default.",
                ),
            },
        },
        "tests/test_dependency_after_yield_raise.py": {
            "functions": {
                "test_broken_raise": reviewed_case(
                    ["dependency-security"],
                    ["dependency.cleanup_order", "error.class", "error.public_attributes"],
                    "The endpoint returns normally, then its yielding dependency finalizer raises ValueError.",
                ),
            },
        },
        "tests/test_dependency_after_yield_streaming.py": {
            "functions": {
                "test_regular_no_stream": reviewed_case(
                    ["dependency-security", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A normal response consumes and serializes values from a yielding session dependency.",
                ),
                "test_stream_simple": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A static streaming iterator returns bytes without depending on the yielded session.",
                ),
                "test_stream_session": reviewed_case(
                    ["dependency-security", "response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A streaming iterator consumes session values while the dependency remains available.",
                ),
                "test_broken_session_data": reviewed_case(
                    ["dependency-security"],
                    ["error.class", "error.public_attributes"],
                    "A dependency closes its session before the endpoint iterates it, causing a public request failure.",
                ),
            },
        },
        "tests/test_dependency_security_overrides.py": {
            "functions": {
                "test_normal": reviewed_case(
                    ["dependency-security"],
                    ["http.status", "http.body.json"],
                    "The unmodified Security and Depends declarations provide the baseline response before override cases.",
                ),
            },
        },
        "tests/test_exception_handlers.py": {
            "functions": {
                "test_override_server_error_exception_raises": reviewed_case(
                    ["public-api-errors"],
                    ["error.class"],
                    "With the default TestClient server-exception mode, the registered FastAPI handler does not suppress the raised RuntimeError.",
                ),
            },
        },
        "tests/test_include_router_defaults_overrides.py": {
            "functions": {
                "test_level1_override": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.json"],
                    "Nested router defaults and overrides determine the response content type and level headers.",
                ),
                "test_level1_default": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.json"],
                    "Nested router defaults determine the response content type and level headers.",
                ),
                "test_paths_level3": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.json"],
                    "Nested include_router defaults and Boolean overrides determine the response and headers.",
                ),
                "test_paths_level5": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.json"],
                    "A deeper include_router tree applies its Boolean default/override combinations to response content type and headers.",
                ),
            },
        },
        "tests/test_openapi_schema_type.py": {
            "rationale": "These functions construct FastAPI OpenAPI Schema models directly; the model surface remains an uncertain API candidate until the full manifest explicitly includes it.",
            "contract_gate": "Keep as a reviewed candidate; include in executable parity only if fastapi.openapi.models.Schema is listed in the full public manifest.",
            "functions": {
                "test_allowed_schema_type": reviewed_case(
                    ["openapi-docs"],
                    ["python.attribute_value"],
                    "Schema.type accepts the parameterized string/list/None values in the direct OpenAPI model workflow.",
                ),
                "test_invalid_type_value": reviewed_case(
                    ["openapi-docs"],
                    ["error.class", "error.args"],
                    "A direct Schema constructor rejects a Boolean type and raises a Pydantic validation error; this is not HTTP request validation.",
                ),
            },
        },
        "tests/test_serialize_response_dataclass.py": {
            "feature_ids": ["response-serialization"],
            "replace_features": True,
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "rationale": "Each route has a dataclass response model; cases distinguish dict/dataclass instances, coercion, scalar/list returns, and defaults.",
        },
        "tests/test_arbitrary_types.py": {
            "rationale": "The mapped request case exercises FastAPI response serialization; the TypeAdapter helper is Pydantic-only and excluded.",
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "A FastAPI endpoint returns a Pydantic model containing a custom type with PlainSerializer.",
                ),
                "test_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.document"],
                    "The app's generated OpenAPI schema describes the custom serialized model.",
                ),
            },
        },
        "tests/test_schema_compat_pydantic_v2.py": {
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "A response model serializes a union of enum classes through the public endpoint.",
                ),
            },
        },
        "tests/test_schema_ref_pydantic_v2.py": {
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "The response model serializes a field using '$ref' as its validation and serialization alias.",
                ),
            },
        },
        "tests/test_serialize_response.py": {
            "module_observation_selectors": ["http.body.json"],
        },
        "tests/test_skip_defaults.py": {
            "module_observation_selectors": ["http.body.json"],
        },
        "tests/test_response_model_data_filter.py": {
            "stimulus_notes": "Use `/users/` in the independent case input so Starlette's slash redirect does not become an incidental observation.",
        },
        "tests/test_response_model_data_filter_no_inheritance.py": {
            "stimulus_notes": "Use `/users/` in the independent case input so Starlette's slash redirect does not become an incidental observation.",
        },
        "tests/test_params_repr.py": {
            "feature_ids": ["public-api-errors"],
            "replace_features": True,
            "replace_module_features": True,
            "module_feature_ids": ["public-api-errors"],
            "module_observation_selectors": ["http.status", "http.body.bytes"],
            "rationale": "These cases register FastAPI Param instances in a representative route and serialize their repr() strings into the observable HTTP response; the reviewed operation gate is fastapi.params.Param.__repr__.",
            "contract_gate": "Requires an explicit fastapi.params.Param.__repr__ operation in the full public manifest.",
            "supporting_sources": [
                {
                    "path": "tests/test_params_repr.py",
                    "start_line": 1,
                    "end_line": 5,
                    "role": "public Param imports and test values",
                },
                {
                    "path": "fastapi/params.py",
                    "start_line": 133,
                    "end_line": 134,
                    "role": "Param repr implementation",
                },
            ],
        },
    }
)

merge_test_review_mappings(
    {
        "tests/test_dependency_contextmanager.py": {
            "replace_module_features": True,
            "module_feature_ids": ["dependency-security", "response-serialization"],
            "supporting_sources": [
                {
                    "path": "tests/test_dependency_contextmanager.py",
                    "start_line": 73,
                    "end_line": 86,
                    "role": "yield dependency setup and cleanup traces",
                },
                {
                    "path": "tests/test_dependency_contextmanager.py",
                    "start_line": 135,
                    "end_line": 141,
                    "role": "nested yield dependencies",
                },
                {
                    "path": "tests/test_dependency_contextmanager.py",
                    "start_line": 193,
                    "end_line": 203,
                    "role": "background task route using nested yield dependencies",
                },
            ],
            "functions": {
                "test_async_state": reviewed_case(
                    ["dependency-security"],
                    [
                        "http.status",
                        "http.body.json",
                        "dependency.call_order",
                        "dependency.cleanup_order",
                    ],
                    "An async generator dependency surrounds a successful HTTP response and records finalization.",
                ),
                "test_sync_state": reviewed_case(
                    ["dependency-security"],
                    [
                        "http.status",
                        "http.body.json",
                        "dependency.call_order",
                        "dependency.cleanup_order",
                    ],
                    "A sync generator dependency surrounds a successful HTTP response and records finalization.",
                ),
                "test_async_raise_other": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "An async yielding dependency receives and re-raises a different endpoint exception.",
                ),
                "test_sync_raise_other": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "A sync yielding dependency receives and re-raises a different endpoint exception.",
                ),
                "test_async_raise_raises": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "An async yielding dependency receives the endpoint exception and performs its finally cleanup.",
                ),
                "test_async_raise_server_error": reviewed_case(
                    ["dependency-security"],
                    ["http.status", "dependency.call_order", "dependency.cleanup_order"],
                    "A non-raising TestClient profile returns the server-error response after the async dependency handles and finalizes the exception.",
                    constraints={"starlette_testclient": {"raise_server_exceptions": False}},
                ),
                "test_sync_raise_raises": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "A sync yielding dependency receives the endpoint exception and performs its finally cleanup.",
                ),
                "test_sync_raise_server_error": reviewed_case(
                    ["dependency-security"],
                    ["http.status", "dependency.call_order", "dependency.cleanup_order"],
                    "A non-raising TestClient profile returns the server-error response after the sync dependency handles and finalizes the exception.",
                    constraints={"starlette_testclient": {"raise_server_exceptions": False}},
                ),
                "test_sync_async_state": reviewed_case(
                    ["dependency-security"],
                    [
                        "http.status",
                        "http.body.json",
                        "dependency.call_order",
                        "dependency.cleanup_order",
                    ],
                    "A sync dependency wrapper surrounds an async endpoint response and records generator finalization.",
                ),
                "test_sync_sync_state": reviewed_case(
                    ["dependency-security"],
                    [
                        "http.status",
                        "http.body.json",
                        "dependency.call_order",
                        "dependency.cleanup_order",
                    ],
                    "A sync dependency wrapper surrounds a sync endpoint response and records generator finalization.",
                ),
                "test_sync_async_raise_other": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "A sync yielding dependency around an async endpoint re-raises a different exception.",
                ),
                "test_sync_sync_raise_other": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "A sync yielding dependency around a sync endpoint re-raises a different exception.",
                ),
                "test_sync_async_raise_raises": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "A sync yielding dependency around an async endpoint receives the endpoint exception.",
                ),
                "test_sync_sync_raise_raises": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "A sync yielding dependency around a sync endpoint receives the endpoint exception.",
                ),
                "test_context_b": reviewed_case(
                    ["dependency-security"],
                    ["http.body.json", "dependency.call_order", "dependency.cleanup_order"],
                    "Nested async yield dependencies provide both values and expose inner-to-outer cleanup.",
                ),
                "test_context_b_raise": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "Nested async yield dependencies clean up after the endpoint raises.",
                ),
                "test_sync_context_b": reviewed_case(
                    ["dependency-security"],
                    ["http.body.json", "dependency.call_order", "dependency.cleanup_order"],
                    "Nested yield dependencies return shared state and expose cleanup ordering across the sync dependency wrapper.",
                ),
                "test_sync_context_b_raise": reviewed_case(
                    ["dependency-security"],
                    ["dependency.call_order", "dependency.cleanup_order", "error.class"],
                    "Nested yield dependencies clean up after an endpoint exception across the sync dependency wrapper.",
                ),
                "test_background_tasks": reviewed_case(
                    ["dependency-security", "response-serialization"],
                    [
                        "http.body.json",
                        "dependency.call_order",
                        "dependency.cleanup_order",
                        "response.background_effects",
                    ],
                    "The response and post-response task state show nested dependency finalization and background execution; the x-state test middleware is instrumentation, not a FastAPI middleware contract.",
                ),
                "test_sync_async_raise_server_error": reviewed_case(
                    ["dependency-security"],
                    ["http.status", "dependency.call_order", "dependency.cleanup_order"],
                    "A non-raising TestClient profile returns the server-error response after a sync dependency wraps an async exception.",
                    constraints={"starlette_testclient": {"raise_server_exceptions": False}},
                ),
                "test_sync_sync_raise_server_error": reviewed_case(
                    ["dependency-security"],
                    ["http.status", "dependency.call_order", "dependency.cleanup_order"],
                    "A non-raising TestClient profile returns the server-error response after a sync dependency wraps a sync exception.",
                    constraints={"starlette_testclient": {"raise_server_exceptions": False}},
                ),
                "test_sync_background_tasks": reviewed_case(
                    ["dependency-security", "response-serialization"],
                    [
                        "http.body.json",
                        "dependency.call_order",
                        "dependency.cleanup_order",
                        "response.background_effects",
                    ],
                    "A background task and nested yielding dependency expose response, cleanup, and post-response effects; the endpoint itself is async.",
                    constraints={"fresh_app_state_per_case": True},
                ),
            },
        },
        "tests/test_response_model_data_filter.py": {
            "feature_ids": ["response-serialization"],
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "functions": {
                "test_filter_top_level_model": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model filters undeclared top-level fields.",
                ),
                "test_filter_second_level_model": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model filters undeclared fields in a nested model.",
                ),
                "test_list_of_models": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model applies nested field filtering to every returned model in a list.",
                ),
            },
        },
        "tests/test_response_model_data_filter_no_inheritance.py": {
            "feature_ids": ["response-serialization"],
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "functions": {
                "test_filter_top_level_model": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model filters undeclared fields across unrelated returned and declared model classes.",
                ),
                "test_filter_second_level_model": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model filters nested fields across unrelated returned and declared model classes.",
                ),
                "test_list_of_models": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model filters each nested item across unrelated model classes.",
                ),
            },
        },
        "tests/test_serialize_response.py": {
            "feature_ids": ["response-serialization"],
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "functions": {
                "test_valid": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A declared response model serializes an endpoint's dict result.",
                ),
                "test_coerce": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A declared response model coerces a returned dictionary before JSON serialization.",
                ),
                "test_validlist": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A declared list response model serializes each returned item.",
                ),
            },
        },
        "tests/test_skip_defaults.py": {
            "feature_ids": ["response-serialization"],
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.body.json"],
            "functions": {
                "test_return_defaults": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A response model includes default-valued fields under the default configuration.",
                ),
                "test_return_exclude_unset": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "Response serialization excludes fields that were not explicitly set.",
                ),
                "test_return_exclude_defaults": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "Response serialization excludes fields equal to their model defaults.",
                ),
                "test_return_exclude_none": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "Response serialization excludes fields whose values are None.",
                ),
                "test_return_exclude_unset_none": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "Response serialization combines unset and None field filtering.",
                ),
                "test_return_iterable_exclude_unset": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "An inferred iterable response model excludes unset fields in every item.",
                ),
                "test_return_iterable_exclude_defaults": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "An inferred iterable response model excludes default-valued fields in every item.",
                ),
                "test_return_iterable_exclude_none": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "An inferred iterable response model excludes None-valued fields in every item.",
                ),
            },
        },
        "tests/test_sse.py": {
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization", "openapi-docs"],
            "module_observation_selectors": [
                "http.status",
                "http.headers.ordered",
                "http.body.bytes",
            ],
            "supporting_sources": [
                {
                    "path": "tests/test_sse.py",
                    "start_line": 14,
                    "end_line": 113,
                    "role": "SSE routes, app, models, and fixture setup",
                },
            ],
            "functions": {
                "test_async_generator_with_model": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An async typed generator emits serialized model events.",
                ),
                "test_sync_generator_with_model": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "A sync typed generator emits serialized model events.",
                ),
                "test_async_generator_no_annotation": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An untyped async generator emits model-valued server-sent events.",
                ),
                "test_sync_generator_no_annotation": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An untyped sync generator emits model-valued server-sent events.",
                ),
                "test_dict_items": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A route streams dictionary values as server-sent events.",
                ),
                "test_post_method_sse": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "A POST route returns the configured event stream response.",
                ),
                "test_sse_events_with_fields": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A route streams events with event, ID, comment, retry, and JSON data fields.",
                ),
                "test_mixed_plain_and_sse_events": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "An event stream interleaves model values with explicit server-sent events.",
                ),
                "test_string_data_json_encoded": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "String event data is emitted using the event response's JSON encoding.",
                ),
                "test_server_sent_event_null_id_rejected": reviewed_case(
                    ["response-serialization"],
                    [
                        "construction.outcome",
                        "construction.exception_class",
                        "construction.exception_message",
                    ],
                    "Constructing a public ServerSentEvent with a null ID raises a value error with its message.",
                    contract_gate="Requires the ServerSentEvent constructor and its validation behavior in the full API manifest.",
                ),
                "test_server_sent_event_single_line_fields_reject_newlines": reviewed_case(
                    ["response-serialization"],
                    [
                        "construction.outcome",
                        "construction.exception_class",
                        "construction.exception_message",
                    ],
                    "Constructing a ServerSentEvent with newline-containing single-line fields raises a value error.",
                    contract_gate="Requires the ServerSentEvent constructor and its validation behavior in the full API manifest.",
                ),
                "test_server_sent_event_negative_retry_rejected": reviewed_case(
                    ["response-serialization"],
                    ["construction.outcome", "construction.exception_class"],
                    "A negative retry value is rejected by the public ServerSentEvent constructor.",
                    contract_gate="Requires the ServerSentEvent constructor and its validation behavior in the full API manifest.",
                ),
                "test_server_sent_event_float_retry_rejected": reviewed_case(
                    ["response-serialization"],
                    ["construction.outcome", "construction.exception_class"],
                    "A non-integer retry value is rejected by the public ServerSentEvent constructor.",
                    contract_gate="Requires the ServerSentEvent constructor and its validation behavior in the full API manifest.",
                ),
                "test_raw_data_sent_without_json_encoding": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "Explicit raw event data is streamed without JSON encoding.",
                ),
                "test_data_and_raw_data_mutually_exclusive": reviewed_case(
                    ["response-serialization"],
                    [
                        "construction.outcome",
                        "construction.exception_class",
                        "construction.exception_message",
                    ],
                    "A ServerSentEvent rejects simultaneous data and raw_data constructor inputs.",
                    contract_gate="Requires the ServerSentEvent constructor and its validation behavior in the full API manifest.",
                ),
                "test_sse_on_router_included_in_app": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An EventSourceResponse route remains active when its router is included in an app.",
                ),
                "test_sse_router_typed_stream": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "A typed model stream on an included router produces serialized event data.",
                ),
                "test_sse_router_typed_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.paths"],
                    "The OpenAPI document describes a typed event stream route.",
                ),
                "test_no_keepalive_when_fast": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A fast-completing event stream returns without injecting an idle keep-alive ping.",
                ),
                "test_format_sse_event_splitlines_behavior_in_data": reviewed_case(
                    ["response-serialization"],
                    ["http.body.bytes"],
                    "The workload returns the exact bytes from format_sse_event as the ASGI response body, without a JSON or text transformation.",
                    contract_gate="Requires fastapi.sse.format_sse_event to be explicitly included in the full API manifest.",
                ),
                "test_format_sse_event_splitlines_behavior_in_comment": reviewed_case(
                    ["response-serialization"],
                    ["http.body.bytes"],
                    "The workload returns the exact bytes from format_sse_event as the ASGI response body, without a JSON or text transformation.",
                    contract_gate="Requires fastapi.sse.format_sse_event to be explicitly included in the full API manifest.",
                ),
                "test_default_response_class_on_app_stream": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "An app-level default EventSourceResponse class controls a stream route's representation.",
                    supporting_sources=[
                        {
                            "path": "tests/test_sse.py",
                            "start_line": 402,
                            "end_line": 437,
                            "role": "app default-response-class route setup",
                        }
                    ],
                ),
                "test_default_response_class_on_app_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.paths"],
                    "OpenAPI reflects an app-level EventSourceResponse default class.",
                    supporting_sources=[
                        {
                            "path": "tests/test_sse.py",
                            "start_line": 402,
                            "end_line": 437,
                            "role": "app default-response-class route setup",
                        }
                    ],
                ),
                "test_default_response_class_on_parent_router_stream": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.headers.ordered", "http.body.bytes"],
                    "A parent router's default EventSourceResponse class is inherited by the stream route.",
                    supporting_sources=[
                        {
                            "path": "tests/test_sse.py",
                            "start_line": 460,
                            "end_line": 472,
                            "role": "parent-router default-response-class route setup",
                        }
                    ],
                ),
                "test_default_response_class_on_parent_router_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.paths"],
                    "OpenAPI reflects a parent router's inherited EventSourceResponse default class.",
                    supporting_sources=[
                        {
                            "path": "tests/test_sse.py",
                            "start_line": 460,
                            "end_line": 472,
                            "role": "parent-router default-response-class route setup",
                        }
                    ],
                ),
            },
        },
        "tests/test_swagger_ui_init_oauth.py": {
            "replace_module_features": True,
            "module_feature_ids": ["openapi-docs", "response-serialization"],
            "functions": {
                "test_swagger_ui": reviewed_case(
                    ["openapi-docs"],
                    ["docs.response.status", "docs.response.body.bytes"],
                    "The docs response contains the configured Swagger OAuth initialization.",
                ),
                "test_response": reviewed_case(
                    ["response-serialization"],
                    ["http.body.json"],
                    "A normal JSON endpoint provides a control case unrelated to OAuth UI setup.",
                ),
            },
        },
        "tests/test_tutorial/test_body_updates/test_tutorial001.py": {
            "replace_module_features": True,
            "module_feature_ids": ["request-validation", "response-serialization", "openapi-docs"],
            "rationale": "The tutorial app replaces an in-memory item through PUT; the module also observes its seeded GET response and generated OpenAPI document.",
            "stimulus_notes": "The three independent ASGI cases mirror the pinned tutorial app's /items endpoints. Response bytes are a stricter projection than the upstream tests' parsed JSON assertions; inputs contain no expected outputs.",
            "supporting_sources": [
                {
                    "path": "docs_src/body_updates/tutorial001_py310.py",
                    "start_line": 7,
                    "end_line": 29,
                    "role": "Item model, seeded item records, and GET/PUT routes under review",
                },
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/body-updates-tutorial001-upstream.yaml",
                    "case_ids": [
                        "fastapi.body-updates.tutorial001.get-baz",
                        "fastapi.body-updates.tutorial001.put-bar",
                        "fastapi.body-updates.tutorial001.openapi-schema",
                    ],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                },
            ],
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A seeded GET request returns the tutorial's baz item through its Item response model.",
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial001_py310.py",
                            "start_line": 16,
                            "end_line": 25,
                            "role": "seeded baz record and GET route",
                        },
                    ],
                ),
                "test_put": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A PUT request replaces the seeded bar record using the tutorial Item model and returns the updated record.",
                    constraints={"fresh_app_state_per_case": True},
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial001_py310.py",
                            "start_line": 7,
                            "end_line": 13,
                            "role": "Item request/response model",
                        },
                        {
                            "path": "docs_src/body_updates/tutorial001_py310.py",
                            "start_line": 15,
                            "end_line": 29,
                            "role": "seeded bar record and PUT route",
                        },
                    ],
                ),
                "test_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["http.status", "http.body.bytes"],
                    "The generated OpenAPI response describes the tutorial's GET and PUT item operations and Item schema.",
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial001_py310.py",
                            "start_line": 7,
                            "end_line": 29,
                            "role": "model and routes represented by the OpenAPI snapshot",
                        },
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_body_updates/test_tutorial002.py": {
            "replace_module_features": True,
            "module_feature_ids": ["request-validation", "response-serialization", "openapi-docs"],
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A seeded GET request returns the tutorial's baz item through its Item response model.",
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial002_py310.py",
                            "start_line": 16,
                            "end_line": 25,
                            "role": "seeded baz record and GET route",
                        },
                    ],
                ),
                "test_patch_all": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A PATCH workflow applies a fully supplied partial-update model and returns the resulting JSON record.",
                    constraints={"fresh_app_state_per_case": True},
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial002_py310.py",
                            "start_line": 8,
                            "end_line": 35,
                            "role": "Item model and PATCH route",
                        },
                    ],
                ),
                "test_patch_name": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "A PATCH workflow preserves omitted stored fields while changing the supplied name.",
                    constraints={"fresh_app_state_per_case": True},
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial002_py310.py",
                            "start_line": 8,
                            "end_line": 35,
                            "role": "Item model and PATCH route",
                        },
                    ],
                ),
                "test_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.document", "openapi.paths"],
                    "The app's generated OpenAPI document describes the GET and PATCH item operations and Item schema.",
                    contract_gate="The upstream test compares the full OpenAPI JSON snapshot; the linked independent input observes the PATCH request-body schema pointer only, so other document fields remain uncovered.",
                    supporting_sources=[
                        {
                            "path": "docs_src/body_updates/tutorial002_py310.py",
                            "start_line": 8,
                            "end_line": 35,
                            "role": "model and routes represented by the OpenAPI snapshot",
                        },
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_custom_request_and_route/test_tutorial001.py": {
            "replace_module_features": True,
            "module_feature_ids": ["app-routing", "request-validation"],
            "functions": {
                "test_request_class": reviewed_case(
                    ["app-routing"],
                    ["http.body.json"],
                    "A custom APIRoute supplies a custom Request subclass to the endpoint; this function observes class injection, while request decoding is covered separately and generic Request behavior is Starlette-owned.",
                    supporting_sources=[
                        {
                            "path": "docs_src/custom_request_and_route/tutorial001_py310.py",
                            "start_line": 8,
                            "end_line": 30,
                            "role": "custom Request and APIRoute implementation",
                        }
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_custom_request_and_route/test_tutorial002.py": {
            "replace_module_features": True,
            "module_feature_ids": ["request-validation", "response-serialization"],
            "functions": {
                "test_endpoint_works": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.body.json"],
                    "A valid JSON request reaches the endpoint through the custom route and returns its JSON response; the error branch is not exercised.",
                ),
            },
        },
        "tests/test_tutorial/test_dependencies/test_tutorial008d.py": {
            "replace_module_features": True,
            "module_feature_ids": ["dependency-security"],
            "functions": {
                "test_internal_error": reviewed_case(
                    ["dependency-security"],
                    ["error.class", "error.args"],
                    "An exception raised by the endpoint is delivered through a yielding dependency that re-raises it; TestClient re-raising semantics belong to Starlette.",
                    supporting_sources=[
                        {
                            "path": "docs_src/dependencies/tutorial008d_py310.py",
                            "start_line": 6,
                            "end_line": 23,
                            "role": "yield dependency and endpoint exception propagation",
                        }
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_settings/test_app01.py": {
            "replace_module_features": True,
            "module_feature_ids": ["middleware-integrations"],
            "functions": {
                "test_app": reviewed_case(
                    ["middleware-integrations"],
                    ["http.body.json"],
                    "A settings-backed application returns its route's JSON; environment parsing and settings validation belong to Pydantic Settings.",
                    supporting_sources=[
                        {
                            "path": "docs_src/settings/app01_py310/main.py",
                            "start_line": 1,
                            "end_line": 14,
                            "role": "settings-backed FastAPI app",
                        },
                        {
                            "path": "docs_src/settings/app01_py310/config.py",
                            "start_line": 1,
                            "end_line": 10,
                            "role": "Pydantic Settings model",
                        },
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_websockets/test_tutorial003.py": {
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.body.bytes"],
                    "This function asserts the exact HTML body returned by an ordinary HTTP route; it is not a WebSocket exchange.",
                    supporting_sources=[
                        {
                            "path": "docs_src/websockets_/tutorial003_py310.py",
                            "start_line": 6,
                            "end_line": 41,
                            "role": "HTML response body",
                        },
                        {
                            "path": "docs_src/websockets_/tutorial003_py310.py",
                            "start_line": 66,
                            "end_line": 68,
                            "role": "ordinary HTTP route",
                        },
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_debugging/test_tutorial001.py": {
            "replace_module_features": True,
            "module_feature_ids": ["app-routing", "response-serialization", "openapi-docs"],
            "functions": {
                "test_get_root": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "The FastAPI tutorial app returns a JSON value from its root route.",
                ),
                "test_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.document"],
                    "The tutorial app exposes the generated OpenAPI document for its root route.",
                ),
            },
        },
        "tests/test_jsonable_encoder.py": {
            "feature_ids": ["python-data-encoding"],
            "replace_features": True,
            "replace_module_features": True,
            "module_feature_ids": ["python-data-encoding"],
            "module_observation_selectors": ["python.attribute_value"],
            "rationale": "Direct jsonable_encoder workflows exercise FastAPI's documented Python-value conversion API; Pydantic model construction failures are excluded.",
            "functions": {
                "test_encode_unsupported": reviewed_case(
                    ["python-data-encoding"],
                    ["error.class"],
                    "An unsupported Python object raises ValueError when encoded.",
                ),
                "test_json_encoder_error_with_pydanticv1": reviewed_case(
                    ["python-data-encoding"],
                    ["error.class"],
                    "A Pydantic v1 model is rejected by FastAPI's encoder.",
                ),
                "test_encode_custom_json_encoders_model_pydanticv2": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "A Pydantic v2 field serializer determines the encoder's observable model value.",
                ),
                "test_encode_model_with_pure_path": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "A Pydantic model containing PurePath values is converted to JSON-compatible path strings.",
                ),
                "test_encode_model_with_pure_posix_path": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "A Pydantic model containing PurePosixPath values is converted to a JSON-compatible value.",
                ),
                "test_encode_model_with_pure_windows_path": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "A Pydantic model containing PureWindowsPath values is converted to a JSON-compatible value.",
                ),
                "test_encode_pure_path": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "A PurePath value is converted to its public encoded value.",
                ),
                "test_encode_pydantic_undefined": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "Pydantic's undefined sentinel is converted by the public encoder.",
                ),
                "test_encode_color": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "An optional color-package value is converted by the public encoder.",
                    constraints={
                        "optional_dependency": "pydantic-extra-types[color]",
                        "skip_must_remain_visible": True,
                    },
                ),
                "test_encode_model_with_alias": reviewed_case(
                    ["python-data-encoding"],
                    ["python.attribute_value"],
                    "A Pydantic model's alias is retained in the encoded value.",
                ),
            },
        },
        "tests/test_tutorial/test_additional_status_codes/test_tutorial001.py": {
            "replace_module_features": True,
            "module_feature_ids": ["app-routing", "request-validation", "response-serialization"],
            "functions": {
                "test_update": reviewed_case(
                    ["app-routing", "request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A PUT request updates an existing item using body fields and returns the configured route result.",
                    supporting_sources=[
                        {
                            "path": "docs_src/additional_status_codes/tutorial001_py310.py",
                            "start_line": 1,
                            "end_line": 23,
                            "role": "request model, upsert route, and status selection",
                        }
                    ],
                ),
                "test_create": reviewed_case(
                    ["app-routing", "request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A PUT request creates an item and returns a JSONResponse with the route's explicit 201 status.",
                    supporting_sources=[
                        {
                            "path": "docs_src/additional_status_codes/tutorial001_py310.py",
                            "start_line": 1,
                            "end_line": 23,
                            "role": "request model, upsert route, and status selection",
                        }
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_behind_a_proxy/test_tutorial001_01.py": {
            "replace_module_features": True,
            "module_feature_ids": ["app-routing"],
            "functions": {
                "test_redirect": reviewed_case(
                    ["app-routing"],
                    ["http.status", "http.headers.ordered"],
                    "With redirect following disabled, the app redirects a slashless route using the configured external root path; the generic redirect-slash mechanism is Starlette-owned.",
                    supporting_sources=[
                        {
                            "path": "docs_src/behind_a_proxy/tutorial001_01_py310.py",
                            "start_line": 1,
                            "end_line": 8,
                            "role": "proxied app route",
                        }
                    ],
                ),
                "test_no_redirect": reviewed_case(
                    ["app-routing"],
                    ["http.status", "http.body.json"],
                    "The slash-terminated path reaches the route without a redirect and returns its JSON list.",
                    supporting_sources=[
                        {
                            "path": "docs_src/behind_a_proxy/tutorial001_01_py310.py",
                            "start_line": 1,
                            "end_line": 8,
                            "role": "proxied app route",
                        }
                    ],
                ),
            },
        },
        "tests/test_tutorial/test_cors/test_tutorial001.py": {
            "replace_module_features": True,
            "module_feature_ids": ["middleware-integrations"],
            "functions": {
                "test_cors": reviewed_case(
                    ["middleware-integrations"],
                    ["http.status", "http.headers.ordered", "http.body.bytes", "http.body.json"],
                    "The app registers CORSMiddleware and the test observes preflight, CORS-enabled, and ordinary responses; generic middleware behavior is Starlette-owned.",
                    supporting_sources=[
                        {
                            "path": "docs_src/cors/tutorial001_py310.py",
                            "start_line": 1,
                            "end_line": 24,
                            "role": "FastAPI app with registered CORSMiddleware",
                        }
                    ],
                ),
            },
        },
        "tests/test_validate_response_recursive/test_validate_response_recursive.py": {
            "replace_module_features": True,
            "module_feature_ids": ["response-serialization"],
            "module_observation_selectors": ["http.status", "http.body.json"],
            "functions": {
                "test_recursive": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "Recursive and mutually nested Pydantic response models serialize through two public routes.",
                    supporting_sources=[
                        {
                            "path": "tests/test_validate_response_recursive/app.py",
                            "start_line": 1,
                            "end_line": 46,
                            "role": "recursive response models and route handlers",
                        }
                    ],
                ),
            },
        },
        "tests/test_application.py": {
            "functions": {
                "test_enum_status_code_response": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A route uses http.HTTPStatus.CREATED as its configured default status and returns a JSON string.",
                    supporting_sources=[
                        {
                            "path": "tests/main.py",
                            "start_line": 191,
                            "end_line": 193,
                            "role": "route using an HTTPStatus enum",
                        }
                    ],
                ),
            },
        },
        "tests/test_operations_signatures.py": {
            "rationale": "This source compatibility assertion compares public APIRouter and FastAPI HTTP decorator signatures.",
            "contract_gate": "Retain the signatures only for decorator methods included in the full public API manifest.",
            "supporting_sources": [
                {
                    "path": "fastapi/applications.py",
                    "start_line": 1646,
                    "end_line": 1655,
                    "role": "FastAPI HTTP decorator signature",
                },
                {
                    "path": "fastapi/routing.py",
                    "start_line": 3322,
                    "end_line": 3331,
                    "role": "APIRouter HTTP decorator signature",
                },
            ],
            "functions": {
                "test_signatures_consistency": reviewed_case(
                    ["public-api-errors"],
                    ["python.signature"],
                    "Public APIRouter and FastAPI method signatures agree for the supported HTTP decorator set.",
                    contract_gate="Requires each compared decorator signature to appear in the full API manifest.",
                ),
            },
        },
    }
)

merge_test_review_mappings(
    {
        "tests/test_tutorial/test_handling_errors/test_tutorial001.py": {
            "functions": {
                "test_get_item": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "A normal path operation returns its app-owned item value as JSON.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial001_py310.py",
                            "start_line": 8,
                            "end_line": 12,
                            "role": "item route and application lookup",
                        }
                    ],
                ),
                "test_get_item_not_found": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json", "http.header.absent:x-error"],
                    "A FastAPI HTTPException is translated to the tested HTTP error response.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial001_py310.py",
                            "start_line": 8,
                            "end_line": 12,
                            "role": "route raises FastAPI HTTPException for a missing item",
                        },
                        {
                            "path": "fastapi/exception_handlers.py",
                            "start_line": 11,
                            "end_line": 17,
                            "role": "default FastAPI HTTP exception response",
                        },
                        {
                            "path": "fastapi/exceptions.py",
                            "start_line": 17,
                            "end_line": 29,
                            "role": "FastAPI HTTPException subclasses Starlette HTTPException",
                        },
                    ],
                    contract_gate="Requires the observation schema to support a response-header absence predicate; this case checks only that x-error is absent, not the complete ordered header set.",
                    stimulus_notes="The assertion covers the HTTP response and absence of x-error, not the raised exception class as an output.",
                ),
            },
        },
        "tests/test_tutorial/test_handling_errors/test_tutorial003.py": {
            "functions": {
                "test_get": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "The successful route returns its app-owned unicorn value as JSON.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial003_py310.py",
                            "start_line": 21,
                            "end_line": 25,
                            "role": "successful unicorn route branch",
                        }
                    ],
                ),
                "test_get_exception": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "A user-defined exception handler returns the tested HTTP status and JSON response.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial003_py310.py",
                            "start_line": 5,
                            "end_line": 18,
                            "role": "application exception and registered JSON response handler",
                        },
                        {
                            "path": "fastapi/applications.py",
                            "start_line": 4729,
                            "end_line": 4772,
                            "role": "FastAPI exception_handler decorator",
                        },
                        {
                            "path": "starlette/_exception_handler.py",
                            "start_line": 16,
                            "end_line": 20,
                            "role": "Starlette exception handler lookup by exception MRO",
                        },
                    ],
                    stimulus_notes="The exception type and message construction are app-owned; only the HTTP status/body are observed.",
                ),
            },
        },
        "tests/test_tutorial/test_handling_errors/test_tutorial004.py": {
            "functions": {
                "test_get_http_error": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.bytes"],
                    "The custom handler for Starlette HTTP exceptions returns a plain-text response.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial004_py310.py",
                            "start_line": 9,
                            "end_line": 25,
                            "role": "base HTTP exception handler and route branch",
                        }
                    ],
                    stimulus_notes="The registered handler targets StarletteHTTPException, which includes FastAPI's subclass; assert the HTTP response, not the exception object.",
                ),
                "test_get": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A valid integer path parameter reaches the route and returns its JSON value.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial004_py310.py",
                            "start_line": 22,
                            "end_line": 26,
                            "role": "typed path parameter and successful route branch",
                        }
                    ],
                    stimulus_notes="Path conversion is FastAPI/Pydantic integration; the branch and response value are app logic.",
                ),
            },
        },
        "tests/test_tutorial/test_handling_errors/test_tutorial005.py": {
            "functions": {
                "test_post": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A valid Pydantic Item request body is parsed and returned through a public route.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial005_py310.py",
                            "start_line": 18,
                            "end_line": 25,
                            "role": "Pydantic request model and route",
                        }
                    ],
                    stimulus_notes="The Item fields and validation are Pydantic-owned under the pinned Pydantic identity; this function covers only a valid body.",
                ),
            },
        },
        "tests/test_tutorial/test_handling_errors/test_tutorial006.py": {
            "functions": {
                "test_get_http_error": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "A custom handler delegates to FastAPI's default HTTP exception handler.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial006_py310.py",
                            "start_line": 12,
                            "end_line": 15,
                            "role": "delegating HTTP exception handler",
                        },
                        {
                            "path": "fastapi/exception_handlers.py",
                            "start_line": 11,
                            "end_line": 17,
                            "role": "default FastAPI HTTP exception response",
                        },
                    ],
                    stimulus_notes="The app handler prints before delegation, but this test does not capture or assert stdout.",
                ),
                "test_get": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A valid integer path parameter reaches the route and returns its JSON value.",
                    supporting_sources=[
                        {
                            "path": "docs_src/handling_errors/tutorial006_py310.py",
                            "start_line": 24,
                            "end_line": 28,
                            "role": "typed path parameter and successful route branch",
                        }
                    ],
                    stimulus_notes="Path conversion is FastAPI/Pydantic integration; the branch and response value are app logic.",
                ),
            },
        },
        "tests/test_tutorial/test_json_base64_bytes/test_tutorial001.py": {
            "functions": {
                "test_get_data": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "A response model serializes bytes using its configured Base64 JSON representation.",
                    supporting_sources=[
                        {
                            "path": "docs_src/json_base64_bytes/tutorial001_py310.py",
                            "start_line": 12,
                            "end_line": 16,
                            "role": "Pydantic output model byte serialization config",
                        },
                        {
                            "path": "docs_src/json_base64_bytes/tutorial001_py310.py",
                            "start_line": 38,
                            "end_line": 41,
                            "role": "route constructs bytes and returns the output model",
                        },
                    ],
                    stimulus_notes="Pydantic owns ser_json_bytes conversion; the route's description and byte construction are app logic.",
                ),
                "test_post_data_in_out": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A configured Pydantic model parses and returns Base64 JSON bytes through one route.",
                    supporting_sources=[
                        {
                            "path": "docs_src/json_base64_bytes/tutorial001_py310.py",
                            "start_line": 19,
                            "end_line": 26,
                            "role": "Pydantic input/output model byte config",
                        },
                        {
                            "path": "docs_src/json_base64_bytes/tutorial001_py310.py",
                            "start_line": 44,
                            "end_line": 46,
                            "role": "route uses the same model for input and output",
                        },
                    ],
                    stimulus_notes="Base64 parsing and encoding are Pydantic behavior; FastAPI integrates the model into HTTP request/response handling.",
                ),
            },
        },
        "tests/test_tutorial/test_metadata/test_tutorial001.py": {
            "functions": {
                "test_items": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "The metadata example's ordinary GET route returns its app-owned item list.",
                    supporting_sources=[
                        {
                            "path": "docs_src/metadata/tutorial001_py310.py",
                            "start_line": 36,
                            "end_line": 38,
                            "role": "GET item route",
                        }
                    ],
                    stimulus_notes="The function observes the route response, not the app's OpenAPI metadata.",
                ),
            },
        },
        "tests/test_tutorial/test_metadata/test_tutorial001_1.py": {
            "functions": {
                "test_items": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "The metadata variant's ordinary GET route returns its app-owned item list.",
                    supporting_sources=[
                        {
                            "path": "docs_src/metadata/tutorial001_1_py310.py",
                            "start_line": 36,
                            "end_line": 38,
                            "role": "GET item route",
                        }
                    ],
                    stimulus_notes="The license identifier difference is not observed by this route-response test; metadata is covered by the sibling OpenAPI test.",
                ),
            },
        },
        "tests/test_tutorial/test_metadata/test_tutorial002.py": {
            "functions": {
                "test_items": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "The custom OpenAPI URL example's ordinary GET route returns its app-owned item list.",
                    supporting_sources=[
                        {
                            "path": "docs_src/metadata/tutorial002_py310.py",
                            "start_line": 3,
                            "end_line": 8,
                            "role": "custom OpenAPI URL and GET item route",
                        }
                    ],
                    stimulus_notes="The custom OpenAPI URL does not affect this GET; endpoint data is app-owned.",
                ),
            },
        },
        "tests/test_tutorial/test_metadata/test_tutorial003.py": {
            "functions": {
                "test_items": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.json"],
                    "The custom docs URL example's ordinary GET route returns its app-owned item list.",
                    supporting_sources=[
                        {
                            "path": "docs_src/metadata/tutorial003_py310.py",
                            "start_line": 3,
                            "end_line": 8,
                            "role": "docs URL settings and GET item route",
                        }
                    ],
                    stimulus_notes="The custom Swagger/ReDoc settings do not affect this GET; endpoint data is app-owned.",
                ),
            },
        },
        "tests/test_tutorial/test_response_status_code/test_tutorial001_tutorial002.py": {
            "functions": {
                "test_create_item": reviewed_case(
                    ["request-validation", "response-serialization"],
                    ["http.status", "http.body.json"],
                    "A POST route parses its query input and returns the configured created status with JSON.",
                    supporting_sources=[
                        {
                            "path": "docs_src/response_status_code/tutorial001_py310.py",
                            "start_line": 6,
                            "end_line": 8,
                            "role": "literal status-code route variant",
                        },
                        {
                            "path": "docs_src/response_status_code/tutorial002_py310.py",
                            "start_line": 1,
                            "end_line": 8,
                            "role": "Starlette status alias and route variant",
                        },
                    ],
                    stimulus_notes="Preserve both configured spellings, literal 201 and status.HTTP_201_CREATED; the response status is the same. The OpenAPI assertion is a separate matched function.",
                ),
            },
        },
        "tests/test_tutorial/test_settings/test_app01.py": {
            "module_feature_ids": ["middleware-integrations", "openapi-docs"],
            "functions": {
                "test_openapi_schema": reviewed_case(
                    ["openapi-docs"],
                    ["openapi.document", "docs.response.status"],
                    "The settings tutorial exposes the generated OpenAPI document for a no-parameter GET route.",
                    supporting_sources=[
                        {
                            "path": "docs_src/settings/app01_py310/main.py",
                            "start_line": 5,
                            "end_line": 14,
                            "role": "app and info route represented in OpenAPI",
                        },
                        {
                            "path": "fastapi/applications.py",
                            "start_line": 1070,
                            "end_line": 1158,
                            "role": "OpenAPI generation and serving route",
                        },
                        {
                            "path": "fastapi/openapi/utils.py",
                            "start_line": 585,
                            "end_line": 679,
                            "role": "OpenAPI document generation",
                        },
                    ],
                    stimulus_notes="This case observes the schema only; environment-backed Pydantic Settings validation and route response values belong to separate functions.",
                ),
            },
        },
        "tests/test_tutorial/test_sub_applications/test_tutorial001.py": {
            "functions": {
                "test_main": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["route.match", "http.status", "http.body.json"],
                    "The parent FastAPI app routes a request to its ordinary JSON endpoint.",
                    supporting_sources=[
                        {
                            "path": "docs_src/sub_applications/tutorial001_py310.py",
                            "start_line": 3,
                            "end_line": 8,
                            "role": "parent application route",
                        }
                    ],
                    stimulus_notes="The response payload is app-owned; the matched OpenAPI schema assertion is a separate function.",
                ),
                "test_sub": reviewed_case(
                    ["app-routing", "response-serialization"],
                    ["route.match", "http.status", "http.body.json"],
                    "The mounted FastAPI sub-application receives a request through the Starlette mount path.",
                    supporting_sources=[
                        {
                            "path": "docs_src/sub_applications/tutorial001_py310.py",
                            "start_line": 11,
                            "end_line": 19,
                            "role": "sub-application route and mount",
                        },
                        {
                            "path": "starlette/applications.py",
                            "start_line": 98,
                            "end_line": 99,
                            "role": "Starlette application delegates mount to its router",
                        },
                        {
                            "path": "starlette/routing.py",
                            "start_line": 363,
                            "end_line": 425,
                            "role": "generic mount path match and child scope",
                        },
                    ],
                    stimulus_notes="Separate FastAPI route integration from Starlette's generic Mount dispatch; the returned message is app logic.",
                ),
            },
        },
        "tests/test_tutorial/test_websockets/test_tutorial001.py": {
            "functions": {
                "test_main": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.prefix"],
                    "The tutorial's HTTP root route returns an HTML response.",
                    supporting_sources=[
                        {
                            "path": "docs_src/websockets_/tutorial001_py310.py",
                            "start_line": 6,
                            "end_line": 43,
                            "role": "HTML body and ordinary HTTP route",
                        }
                    ],
                    contract_gate="Requires observation-schema support for a response-body prefix projection; this test checks a doctype prefix and does not compare the full HTML bytes.",
                    stimulus_notes="This test is HTTP-only and asserts a doctype prefix; it is not evidence for the app's WebSocket route.",
                ),
            },
        },
        "tests/test_tutorial/test_websockets/test_tutorial002.py": {
            "functions": {
                "test_main": reviewed_case(
                    ["response-serialization"],
                    ["http.status", "http.body.prefix"],
                    "The tutorial's HTTP root route returns an HTML response for each app variant.",
                    supporting_sources=[
                        {
                            "path": "docs_src/websockets_/tutorial002_py310.py",
                            "start_line": 59,
                            "end_line": 61,
                            "role": "ordinary HTTP route",
                        },
                        {
                            "path": "docs_src/websockets_/tutorial002_an_py310.py",
                            "start_line": 61,
                            "end_line": 63,
                            "role": "Annotated variant ordinary HTTP route",
                        },
                    ],
                    contract_gate="Requires observation-schema support for a response-body prefix projection; this test checks a doctype prefix and does not compare the full HTML bytes.",
                    stimulus_notes="This test is HTTP-only and checks a doctype prefix; it is not evidence for WebSocket credential, dependency, or validation behavior.",
                ),
            },
        },
        "tests/test_tutorial/test_websockets/test_tutorial003.py": {
            "module_feature_ids": ["response-serialization", "websocket-lifecycle"],
            "functions": {
                "test_websocket_handle_disconnection": reviewed_case(
                    ["websocket-lifecycle"],
                    ["websocket.messages", "websocket.event_order"],
                    "Two connected clients exchange and broadcast messages; after the second closes, the remaining client receives the departure broadcast. The source observes message behavior, not the connection manager's private list.",
                    contract_gate="The current WebSocket workflow cannot represent two concurrent clients; its materialized one-client session is only a subset and does not observe the second client's disconnect broadcast.",
                    supporting_sources=[
                        {
                            "path": "docs_src/websockets_/tutorial003_py310.py",
                            "start_line": 44,
                            "end_line": 81,
                            "role": "application connection manager, WebSocket endpoint, and disconnect cleanup",
                        },
                        {
                            "path": "starlette/websockets.py",
                            "start_line": 35,
                            "end_line": 58,
                            "role": "generic WebSocket receive state and disconnect handling",
                        },
                        {
                            "path": "starlette/websockets.py",
                            "start_line": 112,
                            "end_line": 121,
                            "role": "receive_text raises WebSocketDisconnect on client disconnect",
                        },
                    ],
                    constraints={"fresh_app_state_per_case": True},
                    stimulus_notes="Connection-list mutation, broadcast order, and departure text are app logic. Preserve observable message order with deterministic sequencing; the source test's sleeps are not timing requirements. No close code or exception class is asserted. The current materialized one-client session does not cover this multi-client function.",
                ),
            },
        },
    }
)

TEST_FUNCTION_EXCLUSIONS.setdefault("tests/test_jsonable_encoder.py", {}).update(
    {
        "test_encode_model_with_alias_raises": "Only constructs an invalid Pydantic model and observes Pydantic's ValidationError; FastAPI's jsonable_encoder is never called.",
    }
)
TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault("tests/test_jsonable_encoder.py", {}).update(
    {
        "test_encode_model_with_alias_raises": [
            {
                "path": "tests/test_jsonable_encoder.py",
                "start_line": 177,
                "end_line": 179,
                "role": "Pydantic model construction failure without encoder invocation",
            },
        ],
    }
)

# Keep the broad, source-reviewed core mapping wave separate from the generator
# so it can be audited and extended without obscuring the classification logic.
from atlas_core_review_mappings import CORE_TEST_REVIEW_MAPPINGS  # noqa: E402

merge_test_review_mappings(CORE_TEST_REVIEW_MAPPINGS)

# Function-level tutorial mapping wave, reviewed separately from core tests.
from atlas_tutorial_test_review_mappings import TUTORIAL_TEST_REVIEW_MAPPINGS  # noqa: E402

merge_test_review_mappings(TUTORIAL_TEST_REVIEW_MAPPINGS)

# Response, encoder, and security waves keep their source review separate from
# the generator's heuristic classification logic.
from atlas_response_openapi_wave_mappings import (  # noqa: E402
    RESPONSE_OPENAPI_TEST_EXCLUSIONS,
    RESPONSE_OPENAPI_TEST_REVIEW_MAPPINGS,
)
from atlas_security_wave_mappings import SECURITY_TEST_REVIEW_MAPPINGS  # noqa: E402

merge_test_review_mappings(RESPONSE_OPENAPI_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(SECURITY_TEST_REVIEW_MAPPINGS)

# Add the OpenAPI scope-projection case to the existing non-propagation test
# mapping. The security wave has module-level evidence but no function row for
# this test, so the supplemental function mapping can coexist without replacing it.
from atlas_security_scopes_dont_propagate_openapi_source_review_mappings import (  # noqa: E402
    SECURITY_SCOPE_NONPROPAGATION_OPENAPI_ATLAS_MAPPINGS,
)

merge_test_review_mappings(SECURITY_SCOPE_NONPROPAGATION_OPENAPI_ATLAS_MAPPINGS)

for test_path, exclusions in RESPONSE_OPENAPI_TEST_EXCLUSIONS.items():
    TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {}).update(
        {function_name: evidence["reason"] for function_name, evidence in exclusions.items()}
    )
    TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {}).update(
        {
            function_name: evidence.get("supporting_sources", [])
            for function_name, evidence in exclusions.items()
        }
    )

TEST_REVIEW_MAPPINGS.setdefault("tests/test_multipart_installation.py", {}).update(
    {
        "feature_ids": ["request-validation", "public-api-errors"],
        "module_observation_selectors": [
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
        ],
        "rationale": (
            "The module mutates multipart package state, then observes FastAPI route "
            "construction success or the exact public installation error for Form and File shapes."
        ),
        "stimulus_notes": (
            "Apply one isolated package-state mutation per case and register the matching "
            "public FastAPI route; compare construction outcome, exception class, and message."
        ),
    }
)

TEST_REVIEW_MAPPINGS.setdefault("tests/test_router_circular_import.py", {}).update(
    {
        "feature_ids": ["app-routing", "public-api-errors"],
        "module_observation_selectors": [
            "construction.outcome",
            "construction.exception_class",
            "construction.exception_message",
        ],
        "rationale": (
            "The upstream test asserts that APIRouter.include_router rejects direct "
            "self-inclusion. The independent workflow adds a source-derived transitive "
            "cycle case from FastAPI's recursive-router guard."
        ),
        "stimulus_notes": (
            "Create routers and observe the upstream direct self-inclusion error plus "
            "the input-only transitive-cycle extension; compare construction outcome, "
            "exception class, and exact message."
        ),
    }
)

TEST_REVIEW_MAPPINGS.setdefault(
    "tests/test_tutorial/test_body_updates/test_tutorial002.py", {}
).update(
    {
        "module_observation_selectors": [
            "http.status",
            "http.body.bytes",
            "openapi.document",
            "openapi.paths",
        ],
        "rationale": (
            "The module observes its documented PATCH workflow and the app's generated "
            "OpenAPI document; the latter needs a document/path selector in addition to "
            "the HTTP response selectors."
        ),
        "supporting_sources": [
            {
                "path": "tests/test_tutorial/test_body_updates/test_tutorial002.py",
                "start_line": 69,
                "end_line": 213,
                "role": "OpenAPI document observation for the body-update tutorial app",
            },
            {
                "path": "docs/en/docs/tutorial/body-updates.md",
                "start_line": 47,
                "end_line": 96,
                "role": "documented partial-update model and PATCH workflow",
            },
        ],
        "stimulus_notes": (
            "The linked independent ASGI workflow covers the seeded GET, both PATCH inputs, and one selected OpenAPI request-body schema pointer. The upstream OpenAPI test compares the full document, so the pointer case is partial. Response bytes are stricter than the source tests' parsed JSON checks; fixtures store inputs only."
        ),
        "workflow_cases": [
            {
                "recipe_path": "tests/fixtures/input-recipes/parity/nested-body-corner-wave.yaml",
                "case_ids": [
                    "fastapi.nested-body-corner-wave.patch-model.test-get",
                    "fastapi.nested-body-corner-wave.patch-model.test-patch-all",
                    "fastapi.nested-body-corner-wave.patch-model.test-patch-name",
                    "fastapi.nested-body-corner-wave.patch-model.test-openapi-schema",
                ],
                "observation_selectors": [
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
            },
        ],
    }
)

# Security tutorial workflows intentionally use synthetic tokens. Keep
# app-owned password/JWT branches out of FastAPI parity with source-backed
# per-function reasons, while retaining FastAPI's bearer/dependency cases.
from atlas_security_test_exclusions import (  # noqa: E402
    TEST_FUNCTION_EXCLUSION_EVIDENCE as SECURITY_TEST_FUNCTION_EXCLUSION_EVIDENCE,
)
from atlas_security_test_exclusions import (  # noqa: E402
    TEST_FUNCTION_EXCLUSIONS as SECURITY_TEST_FUNCTION_EXCLUSIONS,
)

for test_path, exclusions in SECURITY_TEST_FUNCTION_EXCLUSIONS.items():
    TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {}).update(exclusions)
for test_path, evidence in SECURITY_TEST_FUNCTION_EXCLUSION_EVIDENCE.items():
    TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {}).update(evidence)

from atlas_security_tutorial_test_review_mappings import (  # noqa: E402
    SECURITY_TUTORIAL_TEST_FUNCTION_EXCLUSIONS,
    SECURITY_TUTORIAL_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(SECURITY_TUTORIAL_TEST_REVIEW_MAPPINGS)
for test_path, exclusions in SECURITY_TUTORIAL_TEST_FUNCTION_EXCLUSIONS.items():
    TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {}).update(
        {function_name: exclusion["reason"] for function_name, exclusion in exclusions.items()}
    )
    TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {}).update(
        {
            function_name: exclusion.get("supporting_sources", [])
            for function_name, exclusion in exclusions.items()
        }
    )

# App, dependency, lifecycle, routing, exception, and WebSocket review.
from atlas_app_dependency_wave_mappings import (  # noqa: E402
    APP_DEPENDENCY_TEST_FUNCTION_EXCLUSIONS,
    APP_DEPENDENCY_TEST_MODULE_EXCLUSIONS,
    APP_DEPENDENCY_TEST_REVIEW_MAPPINGS,
    APP_DEPENDENCY_WAVE_GAPS,
)

merge_test_review_mappings(APP_DEPENDENCY_TEST_REVIEW_MAPPINGS)
APP_DEPENDENCY_SCOPE_REVIEW_BY_MODULE = {
    test_path: {
        "module": APP_DEPENDENCY_TEST_MODULE_EXCLUSIONS.get(test_path),
        "functions": APP_DEPENDENCY_TEST_FUNCTION_EXCLUSIONS.get(test_path, {}),
    }
    for test_path in set(APP_DEPENDENCY_TEST_MODULE_EXCLUSIONS)
    | set(APP_DEPENDENCY_TEST_FUNCTION_EXCLUSIONS)
}

# The routing/application review keeps its source cases and exclusions in a
# separate file; adapt it into the atlas's function-level review contract here.
from atlas_route_application_test_review_mappings import (  # noqa: E402
    ROUTE_APPLICATION_TEST_SOURCE_REVIEW,
)

for _route_test_path, _route_module_review in ROUTE_APPLICATION_TEST_SOURCE_REVIEW[
    "test_modules"
].items():
    merge_test_review_mappings(
        {
            _route_test_path: {
                "functions": _route_module_review.get("test_mappings", {}),
            }
        }
    )
    for _function_name, _function_exclusion in _route_module_review.get("exclusions", {}).items():
        TEST_FUNCTION_EXCLUSIONS.setdefault(_route_test_path, {})[_function_name] = (
            _function_exclusion["reason"]
        )
        TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(_route_test_path, {})[_function_name] = [
            _function_exclusion["source_span"],
            *_function_exclusion.get("supporting_sources", []),
        ]

from atlas_exception_handlers_test_review_mappings import (  # noqa: E402
    EXCEPTION_HANDLERS_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(EXCEPTION_HANDLERS_TEST_REVIEW_MAPPINGS)

from atlas_openapi_servers_root_path_prefix_test_review_mappings import (  # noqa: E402
    OPENAPI_SERVERS_ROOT_PATH_PREFIX_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(OPENAPI_SERVERS_ROOT_PATH_PREFIX_TEST_REVIEW_MAPPINGS)

from atlas_builtin_generic_type_test_review_mappings import (  # noqa: E402
    BUILTIN_GENERIC_TYPE_TEST_REVIEW_MAPPINGS,
)
from atlas_custom_response_tutorial_test_review_mappings import (  # noqa: E402
    CUSTOM_RESPONSE_TUTORIAL_TEST_REVIEW_MAPPINGS,
)
from atlas_dependency_tutorial_test_review_mappings import (  # noqa: E402
    DEPENDENCY_TUTORIAL_TEST_MODULE_EXCLUSIONS,
    DEPENDENCY_TUTORIAL_TEST_REVIEW_MAPPINGS,
)
from atlas_error_tutorial_test_review_mappings import (  # noqa: E402
    ERROR_TUTORIAL_TEST_REVIEW_MAPPINGS,
)
from atlas_metadata_tutorial_test_review_mappings import (  # noqa: E402
    METADATA_TUTORIAL_TEST_REVIEW_MAPPINGS,
)
from atlas_nested_body_tutorial_test_review_mappings import (  # noqa: E402
    NESTED_BODY_TUTORIAL_TEST_MODULE_EXCLUSIONS,
    NESTED_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS,
)
from atlas_response_headers_status_cookies_tutorial_test_review_mappings import (  # noqa: E402
    RESPONSE_HEADERS_STATUS_COOKIES_TUTORIAL_REVIEW_MAPPINGS,
)
from atlas_response_model_tutorial_test_review_mappings import (  # noqa: E402
    RESPONSE_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS,
)
from atlas_sse_stream_test_review_mappings import (  # noqa: E402
    SSE_STREAM_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(ERROR_TUTORIAL_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(DEPENDENCY_TUTORIAL_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(METADATA_TUTORIAL_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(NESTED_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(RESPONSE_HEADERS_STATUS_COOKIES_TUTORIAL_REVIEW_MAPPINGS)
merge_test_review_mappings(SSE_STREAM_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(RESPONSE_MODEL_TUTORIAL_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(CUSTOM_RESPONSE_TUTORIAL_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(BUILTIN_GENERIC_TYPE_TEST_REVIEW_MAPPINGS)

from atlas_tutorial_response_body_input_review_mappings import (  # noqa: E402
    TUTORIAL_RESPONSE_BODY_INPUT_REVIEW_MAPPINGS,
)

for (
    _tutorial_test_path,
    _tutorial_module_review,
) in TUTORIAL_RESPONSE_BODY_INPUT_REVIEW_MAPPINGS.items():
    _tutorial_functions = {}
    for _tutorial_function_name, _tutorial_function_review in _tutorial_module_review[
        "functions"
    ].items():
        if _tutorial_function_review.get("review_status") == "reviewed_excluded":
            TEST_FUNCTION_EXCLUSIONS.setdefault(_tutorial_test_path, {})[
                _tutorial_function_name
            ] = _tutorial_function_review["exclusion_reason"]
            TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(_tutorial_test_path, {})[
                _tutorial_function_name
            ] = _tutorial_function_review.get("supporting_sources", [])
            continue
        _tutorial_functions[_tutorial_function_name] = {
            key: value for key, value in _tutorial_function_review.items() if key != "review_status"
        }
    _tutorial_module_workflows_by_case = {}
    for _tutorial_link in _tutorial_module_review.get("workflow_cases", []):
        _tutorial_link_key = (_tutorial_link["recipe_path"], _tutorial_link["case_id"])
        _tutorial_module_link = _tutorial_module_workflows_by_case.setdefault(
            _tutorial_link_key,
            {
                "recipe_path": _tutorial_link["recipe_path"],
                "case_ids": [_tutorial_link["case_id"]],
                "observation_selectors": set(),
            },
        )
        _tutorial_module_link["observation_selectors"].update(
            _tutorial_link["observation_selectors"]
        )
    _tutorial_module_workflows = [
        {
            **link,
            "observation_selectors": sorted(link["observation_selectors"]),
        }
        for link in _tutorial_module_workflows_by_case.values()
    ]
    merge_test_review_mappings(
        {
            _tutorial_test_path: {
                "rationale": _tutorial_module_review["rationale"],
                "supporting_sources": _tutorial_module_review.get("supporting_sources", []),
                "module_observation_selectors": _tutorial_module_review.get(
                    "module_observation_selectors", []
                ),
                "stimulus_notes": _tutorial_module_review.get("stimulus_notes", ""),
                "workflow_cases": _tutorial_module_workflows,
                "functions": _tutorial_functions,
            }
        }
    )

from atlas_openapi_examples_security_source_review_mappings import (  # noqa: E402
    OPENAPI_EXAMPLES_SECURITY_SOURCE_REVIEW,
)

for _openapi_test_path, _openapi_module_review in OPENAPI_EXAMPLES_SECURITY_SOURCE_REVIEW[
    "modules"
].items():
    _openapi_functions = {}
    _openapi_module_sources = []
    _openapi_module_selectors = set()
    _openapi_module_workflows_by_case = {}
    for _openapi_function_name, _openapi_function_review in _openapi_module_review[
        "test_mappings"
    ].items():
        _openapi_module_sources.extend(_openapi_function_review.get("supporting_sources", []))
        _openapi_module_selectors.update(_openapi_function_review.get("observation_selectors", []))
        _openapi_function_workflows = []
        for _openapi_link in _openapi_function_review.get("workflow_cases", []):
            _openapi_case_key = (_openapi_link["recipe_path"], _openapi_link["case_id"])
            _openapi_module_link = _openapi_module_workflows_by_case.setdefault(
                _openapi_case_key,
                {
                    "recipe_path": _openapi_link["recipe_path"],
                    "case_ids": [_openapi_link["case_id"]],
                    "observation_selectors": set(),
                },
            )
            _openapi_module_link["observation_selectors"].update(
                _openapi_link["observation_selectors"]
            )
            _openapi_function_workflows.append(
                {key: value for key, value in _openapi_link.items() if key != "coverage"}
            )
        _coverage_notes = [
            f"{link['recipe_path']}::{link['case_id']} covers {link['coverage']}"
            for link in _openapi_function_review.get("workflow_cases", [])
            if link.get("coverage")
        ]
        _openapi_functions[_openapi_function_name] = {
            key: value
            for key, value in _openapi_function_review.items()
            if key not in {"mapping_status", "workflow_cases"}
        }
        _openapi_functions[_openapi_function_name]["workflow_cases"] = _openapi_function_workflows
        if _coverage_notes:
            _openapi_functions[_openapi_function_name]["stimulus_notes"] = "; ".join(
                [
                    _openapi_function_review.get("stimulus_notes", ""),
                    *_coverage_notes,
                ]
            )
    for _openapi_function_name, _openapi_exclusion in _openapi_module_review.get(
        "exclusions", {}
    ).items():
        TEST_FUNCTION_EXCLUSIONS.setdefault(_openapi_test_path, {})[_openapi_function_name] = (
            _openapi_exclusion["reason"]
        )
        TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(_openapi_test_path, {})[
            _openapi_function_name
        ] = [
            _openapi_exclusion["source_span"],
            *_openapi_exclusion.get("supporting_sources", []),
        ]
    merge_test_review_mappings(
        {
            _openapi_test_path: {
                "rationale": (
                    "Source-reviewed OpenAPI/security module; per-function workflow coverage "
                    "and exclusions are linked below."
                ),
                "supporting_sources": _openapi_module_sources,
                "module_observation_selectors": sorted(_openapi_module_selectors),
                "workflow_cases": [
                    {
                        **link,
                        "observation_selectors": sorted(link["observation_selectors"]),
                    }
                    for link in _openapi_module_workflows_by_case.values()
                ],
                "functions": _openapi_functions,
            }
        }
    )

# Supplemental source-reviewed input waves keep their workflows and source
# links in separate review files while feeding the merged atlas map.
from atlas_dependency_cache_source_wave_mappings import (  # noqa: E402
    DEPENDENCY_CACHE_SOURCE_WAVE_MAPPINGS,
)
from atlas_dependency_overrides_required_subdependency_wave_mappings import (  # noqa: E402
    DEPENDENCY_OVERRIDES_REQUIRED_SUBDEPENDENCY_WAVE_MAPPINGS,
)
from atlas_frontend_test_review_mappings import (  # noqa: E402
    FRONTEND_TEST_FUNCTION_EXCLUSION_EVIDENCE,
    FRONTEND_TEST_FUNCTION_EXCLUSIONS,
    FRONTEND_TEST_REVIEW_MAPPINGS,
)
from atlas_response_model_return_annotation_gaps_wave_mappings import (  # noqa: E402
    RESPONSE_MODEL_RETURN_ANNOTATION_GAP_WAVE_MAPPINGS,
)
from atlas_router_live_route_after_include_mappings import (  # noqa: E402
    ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW,
)

merge_test_review_mappings(DEPENDENCY_CACHE_SOURCE_WAVE_MAPPINGS)
merge_test_review_mappings(DEPENDENCY_OVERRIDES_REQUIRED_SUBDEPENDENCY_WAVE_MAPPINGS)
merge_test_review_mappings(FRONTEND_TEST_REVIEW_MAPPINGS)
merge_test_review_mappings(RESPONSE_MODEL_RETURN_ANNOTATION_GAP_WAVE_MAPPINGS)
_router_live_route_test_path = ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW["test_module"]
_router_live_route_test_mappings = ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW["test_mappings"]
_router_live_route_function = next(iter(_router_live_route_test_mappings.values()))
merge_test_review_mappings(
    {
        _router_live_route_test_path: {
            "feature_ids": _router_live_route_function["feature_ids"],
            "module_observation_selectors": _router_live_route_function["observation_selectors"],
            "rationale": _router_live_route_function["rationale"],
            "supporting_sources": _router_live_route_function["supporting_sources"],
            "workflow_cases": _router_live_route_function["workflow_cases"],
            "source_review_scope_exclusions": [
                {
                    "scope": "wave_only",
                    "source_path": _router_live_route_test_path,
                    "source_function": function_name,
                    "source_evidence": [exclusion["source_span"]],
                    "reason": exclusion["reason"],
                }
                for function_name, exclusion in ROUTER_LIVE_ROUTE_AFTER_INCLUDE_SOURCE_REVIEW[
                    "exclusions"
                ].items()
            ],
            "functions": _router_live_route_test_mappings,
        }
    }
)
for test_path, exclusions in FRONTEND_TEST_FUNCTION_EXCLUSIONS.items():
    TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {}).update(exclusions)
for test_path, evidence in FRONTEND_TEST_FUNCTION_EXCLUSION_EVIDENCE.items():
    TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {}).update(evidence)

# Core validation/schema review keeps source links and exclusions in a focused
# sidecar. Normalize its wave annotations into the atlas's stable review shape.
from atlas_core_validation_contract_wave_mappings import (  # noqa: E402
    CORE_VALIDATION_TEST_EXCLUSION_EVIDENCE,
    CORE_VALIDATION_TEST_EXCLUSIONS,
    CORE_VALIDATION_TEST_REVIEW_MAPPINGS,
)

_core_validation_review_mappings = {}
for _core_test_path, _core_module_review in CORE_VALIDATION_TEST_REVIEW_MAPPINGS.items():
    _core_functions = {}
    for _core_function_name, _core_function_review in _core_module_review["functions"].items():
        _core_functions[_core_function_name] = {
            key: value for key, value in _core_function_review.items() if key != "mapping_status"
        }
        _core_functions[_core_function_name]["workflow_cases"] = [
            {key: value for key, value in workflow.items() if key != "coverage"}
            for workflow in _core_function_review.get("workflow_cases", [])
        ]
    _core_validation_review_mappings[_core_test_path] = {
        "rationale": _core_module_review["rationale"],
        "supporting_sources": _core_module_review.get("supporting_sources", []),
        "functions": _core_functions,
    }
merge_test_review_mappings(_core_validation_review_mappings)
for test_path, exclusions in CORE_VALIDATION_TEST_EXCLUSIONS.items():
    TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {}).update(exclusions)
for test_path, evidence in CORE_VALIDATION_TEST_EXCLUSION_EVIDENCE.items():
    TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {}).update(evidence)

# The response/serialization wave replaces broad prior response-scope notes
# with function-level input cases while retaining the older scope evidence.
from atlas_response_serialization_dependency_source_review_mappings import (  # noqa: E402
    RESPONSE_SERIALIZATION_DEPENDENCY_SOURCE_REVIEW_MAPPINGS,
)

_response_serialization_review_mappings = {}
for (
    _response_test_path,
    _response_module_review,
) in RESPONSE_SERIALIZATION_DEPENDENCY_SOURCE_REVIEW_MAPPINGS.items():
    _response_functions = {}
    for _response_function_name, _response_function_review in _response_module_review[
        "functions"
    ].items():
        _response_functions[_response_function_name] = {
            key: value
            for key, value in _response_function_review.items()
            if key != "mapping_status"
        }
        _response_functions[_response_function_name]["workflow_cases"] = [
            {key: value for key, value in workflow.items() if key != "coverage"}
            for workflow in _response_function_review.get("workflow_cases", [])
        ]
    _response_serialization_review_mappings[_response_test_path] = {
        "functions": _response_functions,
    }
merge_test_review_mappings(_response_serialization_review_mappings)

# Request-union and endpoint-context review records function links plus shared
# ownership boundaries; normalize both levels to the merged atlas contract.
from atlas_union_error_context_review_mappings import (  # noqa: E402
    UNION_ERROR_CONTEXT_TEST_REVIEW_MAPPINGS,
)

_union_error_context_review_mappings = {}
for _union_test_path, _union_module_review in UNION_ERROR_CONTEXT_TEST_REVIEW_MAPPINGS.items():
    _union_functions = {}
    _union_workflows = {}
    for _union_function_name, _union_function_review in _union_module_review["functions"].items():
        _union_function = {
            key: value
            for key, value in _union_function_review.items()
            if key not in {"review_status", "behavior_ownership", "workflow_cases"}
        }
        _function_workflows = []
        for _union_link in _union_function_review.get("workflow_cases", []):
            _link = {
                "recipe_path": _union_link["recipe_path"],
                "case_ids": [_union_link["case_id"]],
                "observation_selectors": _union_link["observation_selectors"],
            }
            _function_workflows.append(_link)
            _workflow_key = (_link["recipe_path"], _union_link["case_id"])
            _module_link = _union_workflows.setdefault(
                _workflow_key,
                {
                    "recipe_path": _link["recipe_path"],
                    "case_ids": [_union_link["case_id"]],
                    "observation_selectors": set(),
                },
            )
            _module_link["observation_selectors"].update(_union_link["observation_selectors"])
        _union_function["workflow_cases"] = _function_workflows
        _union_functions[_union_function_name] = _union_function

    _union_module_sources = [
        source
        for source in _union_module_review.get("supporting_sources", [])
        if source.get("path") != "tests/fixtures/manifest.yaml"
    ]
    _union_module_stimulus = " ".join(
        value
        for value in (
            _union_module_review.get("pydantic_ownership_boundary"),
            _union_module_review.get("starlette_ownership_boundary"),
            _union_module_review.get("rust_target_ownership_boundary"),
        )
        if value
    )
    _union_error_context_review_mappings[_union_test_path] = {
        "rationale": _union_module_review["rationale"],
        "supporting_sources": _union_module_sources,
        "module_observation_selectors": _union_module_review.get(
            "module_observation_selectors", []
        ),
        "workflow_cases": [
            {
                **link,
                "observation_selectors": sorted(link["observation_selectors"]),
            }
            for link in _union_workflows.values()
        ],
        "contract_gate": _union_module_review.get("contract_gate"),
        "stimulus_notes": _union_module_stimulus,
        "functions": _union_functions,
    }
merge_test_review_mappings(_union_error_context_review_mappings)

# Middleware/proxy workflows carry explicit owner boundaries and one source
# exclusion for direct Pydantic Settings behavior; flatten them into the atlas.
from atlas_middleware_proxy_source_review_mappings import (  # noqa: E402
    MIDDLEWARE_PROXY_SOURCE_REVIEW_MAPPINGS,
)

_middleware_proxy_review_mappings = {}
for (
    _middleware_test_path,
    _middleware_module_review,
) in MIDDLEWARE_PROXY_SOURCE_REVIEW_MAPPINGS.items():
    _middleware_functions = {}
    _middleware_workflows = {}
    for _middleware_function_name, _middleware_function_review in _middleware_module_review[
        "functions"
    ].items():
        if _middleware_function_review.get("mapping_status") == "source-backed-exclusion":
            TEST_FUNCTION_EXCLUSIONS.setdefault(_middleware_test_path, {})[
                _middleware_function_name
            ] = _middleware_function_review["exclusion_reason"]
            TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(_middleware_test_path, {})[
                _middleware_function_name
            ] = _middleware_function_review.get("supporting_sources", [])
            continue

        _middleware_function = {
            key: value
            for key, value in _middleware_function_review.items()
            if key not in {"mapping_status", "workflow_cases"}
        }
        _function_workflows = []
        for _middleware_link in _middleware_function_review.get("workflow_cases", []):
            _link = {
                "recipe_path": _middleware_link["recipe_path"],
                "case_ids": [_middleware_link["case_id"]],
                "observation_selectors": _middleware_link["observation_selectors"],
            }
            _function_workflows.append(_link)
            _workflow_key = (_link["recipe_path"], _middleware_link["case_id"])
            _module_link = _middleware_workflows.setdefault(
                _workflow_key,
                {
                    "recipe_path": _link["recipe_path"],
                    "case_ids": [_middleware_link["case_id"]],
                    "observation_selectors": set(),
                },
            )
            _module_link["observation_selectors"].update(_middleware_link["observation_selectors"])
        _middleware_function["workflow_cases"] = _function_workflows
        _middleware_functions[_middleware_function_name] = _middleware_function

    _middleware_ownership = _middleware_module_review.get("ownership_boundaries", {})
    _middleware_proxy_review_mappings[_middleware_test_path] = {
        "rationale": _middleware_module_review["rationale"],
        "supporting_sources": _middleware_module_review.get("supporting_sources", []),
        "module_observation_selectors": _middleware_module_review.get(
            "module_observation_selectors", []
        ),
        "workflow_cases": [
            {
                **link,
                "observation_selectors": sorted(link["observation_selectors"]),
            }
            for link in _middleware_workflows.values()
        ],
        "stimulus_notes": " ".join(_middleware_ownership.values()),
        "functions": _middleware_functions,
    }
merge_test_review_mappings(_middleware_proxy_review_mappings)

from atlas_testing_websocket_tutorial_review_mappings import (  # noqa: E402
    TESTING_WEBSOCKET_TUTORIAL_REVIEW_MAPPINGS,
)

_testing_websocket_review_mappings = {}
for (
    _testing_test_path,
    _testing_module_review,
) in TESTING_WEBSOCKET_TUTORIAL_REVIEW_MAPPINGS.items():
    _testing_functions = {}
    for _testing_function_name, _testing_function_review in _testing_module_review[
        "functions"
    ].items():
        _testing_function = {
            key: value
            for key, value in _testing_function_review.items()
            if key not in {"review_status", "workflow_cases"}
        }
        _testing_function["workflow_cases"] = [
            {
                "recipe_path": link["recipe_path"],
                "case_ids": [link["case_id"]],
                "observation_selectors": link["observation_selectors"],
            }
            for link in _testing_function_review.get("workflow_cases", [])
        ]
        _testing_functions[_testing_function_name] = _testing_function
    _testing_websocket_review_mappings[_testing_test_path] = {
        "rationale": _testing_module_review["rationale"],
        "supporting_sources": _testing_module_review.get("supporting_sources", []),
        "module_observation_selectors": _testing_module_review.get(
            "module_observation_selectors", []
        ),
        "workflow_cases": _testing_module_review.get("workflow_cases", []),
        "stimulus_notes": _testing_module_review.get("stimulus_notes", ""),
        "functions": _testing_functions,
    }
merge_test_review_mappings(_testing_websocket_review_mappings)

from atlas_form_upload_source_review_mappings import (  # noqa: E402
    FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS,
)

_form_upload_review_mappings = {}
for _form_test_path, _form_module_review in FORM_UPLOAD_SOURCE_REVIEW_MAPPINGS.items():
    _form_functions = {}
    _form_workflows = {}
    for _form_function_name, _form_function_review in _form_module_review["functions"].items():
        if _form_function_review.get("function_role") != "source_test":
            continue
        _form_function = {
            key: value
            for key, value in _form_function_review.items()
            if key not in {"review_status", "function_role", "workflow_cases"}
        }
        _function_workflows = []
        for _form_link in _form_function_review.get("workflow_cases", []):
            _link = {
                "recipe_path": _form_link["recipe_path"],
                "case_ids": [_form_link["case_id"]],
                "observation_selectors": _form_link["observation_selectors"],
            }
            _function_workflows.append(_link)
            _workflow_key = (_link["recipe_path"], _form_link["case_id"])
            _module_link = _form_workflows.setdefault(
                _workflow_key,
                {
                    "recipe_path": _link["recipe_path"],
                    "case_ids": [_form_link["case_id"]],
                    "observation_selectors": set(),
                },
            )
            _module_link["observation_selectors"].update(_form_link["observation_selectors"])
        _form_function["workflow_cases"] = _function_workflows
        _form_functions[_form_function_name] = _form_function

    _form_module_notes = _form_module_review.get("stimulus_notes", "")
    _form_upload_review_mappings[_form_test_path] = {
        "rationale": _form_module_review["rationale"],
        "supporting_sources": _form_module_review.get("supporting_sources", []),
        "module_observation_selectors": _form_module_review.get("observation_selectors", []),
        "workflow_cases": [
            {
                **link,
                "observation_selectors": sorted(link["observation_selectors"]),
            }
            for link in _form_workflows.values()
        ],
        "constraints": _form_module_review.get("constraints", {}),
        "contract_gate": _form_module_review.get("contract_gate"),
        "stimulus_notes": _form_module_notes,
        "functions": _form_functions,
    }
merge_test_review_mappings(_form_upload_review_mappings)

import atlas_query_header_parameter_tutorial_review_mappings as query_header_review  # noqa: E402

QUERY_HEADER_FASTAPI_ROOT = query_header_review.FASTAPI_ROOT
QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS = (
    query_header_review.QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS
)
QUERY_HEADER_TARGET_OWNERSHIP = query_header_review.TARGET_OWNERSHIP

_query_header_feature_ids = {
    "request.query.parameters": "request-validation",
    "request.header.parameters": "request-validation",
    "openapi.parameters": "openapi-docs",
}
_query_header_review_mappings = {}
for (
    _query_header_test_path,
    _query_header_module_review,
) in QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS.items():
    _query_header_functions = {}
    _query_header_workflows = {}
    _query_header_docs = _query_header_module_review.get("supporting_docs", [])
    if isinstance(_query_header_docs, dict):
        _query_header_docs = list(_query_header_docs.values())
    _query_header_sources = []
    for _query_header_doc in _query_header_docs:
        _query_header_doc_path = QUERY_HEADER_FASTAPI_ROOT / _query_header_doc
        _query_header_doc_lines = _query_header_doc_path.read_text(encoding="utf-8").splitlines()
        _query_header_sources.append(
            {
                "path": _query_header_doc,
                "start_line": 1,
                "end_line": max(1, len(_query_header_doc_lines)),
                "role": "documented query/header parameter example source",
            }
        )
    for _query_header_function_name, _query_header_function_review in _query_header_module_review[
        "functions"
    ].items():
        _query_header_workflow_links = []
        _function_sources = [
            _query_header_function_review["source_span"],
            *_query_header_sources,
        ]
        for _query_header_link in _query_header_function_review.get("workflow_cases", []):
            _link = {
                "recipe_path": _query_header_link["recipe_path"],
                "case_ids": [_query_header_link["case_id"]],
                "observation_selectors": _query_header_function_review["observation_selectors"],
            }
            _query_header_workflow_links.append(_link)
            _workflow_key = (_link["recipe_path"], _query_header_link["case_id"])
            _module_link = _query_header_workflows.setdefault(
                _workflow_key,
                {
                    "recipe_path": _link["recipe_path"],
                    "case_ids": [_query_header_link["case_id"]],
                    "observation_selectors": set(),
                },
            )
            _module_link["observation_selectors"].update(
                _query_header_function_review["observation_selectors"]
            )
        _coverage_notes = _query_header_function_review.get("coverage_notes", [])
        _query_header_functions[_query_header_function_name] = {
            "feature_ids": [
                _query_header_feature_ids[feature_id]
                for feature_id in _query_header_module_review["feature_ids"]
            ],
            "observation_selectors": _query_header_function_review["observation_selectors"],
            "rationale": _query_header_function_review["rationale"],
            "replace_features": True,
            "workflow_cases": _query_header_workflow_links,
            "supporting_sources": _function_sources,
            "stimulus_notes": " ".join(_coverage_notes),
        }
    _parameter_notes = "; ".join(
        "%s %s alias=%s type=%s required=%s"
        % (
            parameter["name"],
            parameter["location"],
            parameter["alias"],
            parameter["type"],
            parameter["required"],
        )
        for parameter in _query_header_module_review.get("parameter_contracts", [])
    )
    _query_header_review_mappings[_query_header_test_path] = {
        "rationale": (
            "Source-reviewed query/header parameter tutorial with direct and Annotated inputs."
        ),
        "supporting_sources": _query_header_sources,
        "module_observation_selectors": sorted(
            {
                selector
                for function in _query_header_module_review["functions"].values()
                for selector in function["observation_selectors"]
            }
        ),
        "workflow_cases": [
            {
                **link,
                "observation_selectors": sorted(link["observation_selectors"]),
            }
            for link in _query_header_workflows.values()
        ],
        "stimulus_notes": " ".join([*QUERY_HEADER_TARGET_OWNERSHIP.values(), _parameter_notes]),
        "functions": _query_header_functions,
    }
merge_test_review_mappings(_query_header_review_mappings)

for test_path, exclusion in DEPENDENCY_TUTORIAL_TEST_MODULE_EXCLUSIONS.items():
    if not test_path.startswith("tests/test_") or not test_path.endswith(".py"):
        continue
    TEST_EXCLUSIONS[test_path] = exclusion["exclusion_reason"]
    merge_test_review_mappings(
        {
            test_path: {
                "rationale": exclusion["exclusion_reason"],
                "supporting_sources": exclusion.get("supporting_sources", []),
            }
        }
    )

for test_path, exclusion in NESTED_BODY_TUTORIAL_TEST_MODULE_EXCLUSIONS.items():
    if not test_path.startswith("tests/test_") or not test_path.endswith(".py"):
        continue
    TEST_EXCLUSIONS[test_path] = exclusion["exclusion_reason"]
    merge_test_review_mappings(
        {
            test_path: {
                "rationale": exclusion["exclusion_reason"],
                "supporting_sources": exclusion.get("supporting_sources", []),
            }
        }
    )

from atlas_json_parameter_locations_review_mappings import (  # noqa: E402
    JSON_PARAMETER_LOCATIONS_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(JSON_PARAMETER_LOCATIONS_TEST_REVIEW_MAPPINGS)

from atlas_local_docs_test_review_mappings import (  # noqa: E402
    LOCAL_DOCS_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(LOCAL_DOCS_TEST_REVIEW_MAPPINGS)

from atlas_numeric_path_validation_tutorial_mappings import (  # noqa: E402
    NUMERIC_PATH_VALIDATION_TUTORIAL_MAPPINGS,
)

merge_test_review_mappings(NUMERIC_PATH_VALIDATION_TUTORIAL_MAPPINGS)

from atlas_query_string_validation_tutorial_mappings import (  # noqa: E402
    QUERY_STRING_VALIDATION_TUTORIAL_BUILDER_REVIEW_MAPPINGS,
    QUERY_STRING_VALIDATION_TUTORIAL_FUNCTION_EXCLUSION_EVIDENCE,
    QUERY_STRING_VALIDATION_TUTORIAL_FUNCTION_EXCLUSIONS,
)

merge_test_review_mappings(QUERY_STRING_VALIDATION_TUTORIAL_BUILDER_REVIEW_MAPPINGS)
for test_path, exclusions in QUERY_STRING_VALIDATION_TUTORIAL_FUNCTION_EXCLUSIONS.items():
    TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {}).update(exclusions)
for test_path, evidence in QUERY_STRING_VALIDATION_TUTORIAL_FUNCTION_EXCLUSION_EVIDENCE.items():
    TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {}).update(evidence)

from atlas_parameter_model_tutorial_mappings import (  # noqa: E402
    PARAMETER_MODEL_TUTORIAL_BUILDER_REVIEW_MAPPINGS,
)

merge_test_review_mappings(PARAMETER_MODEL_TUTORIAL_BUILDER_REVIEW_MAPPINGS)

# Request-parameter module review carries exact source-to-workflow links at
# module scope; the six alias-specific function rows are normalized below to
# the generator's existing per-function review contract.
from atlas_request_parameter_wave_mappings import (  # noqa: E402
    REQUEST_PARAMETER_FUNCTION_MAPPINGS,
    REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS,
)

REQUEST_PARAMETER_SOURCE_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {}


def _append_unique_review_sources(
    existing: Sequence[dict[str, Any]], additions: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = []
    seen = set()
    for row in [*existing, *additions]:
        identity = tuple(row.get(key) for key in ("path", "start_line", "end_line", "role"))
        if identity not in seen:
            seen.add(identity)
            rows.append(row)
    return rows


for test_path, source_review in REQUEST_PARAMETER_TEST_REVIEW_MAPPINGS.items():
    if not test_path.startswith("tests/test_"):
        continue
    reviewed = TEST_REVIEW_MAPPINGS.setdefault(test_path, {})
    if source_review.get("mapping_status") == "source-backed-exclusion":
        reason = source_review["exclusion_reason"]
        TEST_EXCLUSIONS[test_path] = reason
        reviewed["rationale"] = reason
        reviewed["supporting_sources"] = _append_unique_review_sources(
            reviewed.get("supporting_sources", []),
            source_review.get("supporting_sources", []),
        )
        continue

    REQUEST_PARAMETER_SOURCE_REVIEW_MAPPINGS[test_path] = source_review
    workflow_notes = [
        "%s::%s (actions: %s; selectors: %s)"
        % (
            workflow["recipe_path"],
            workflow["case_id"],
            ", ".join(workflow.get("action_ids", [])),
            ", ".join(workflow["observation_selectors"]),
        )
        for workflow in source_review["workflow_cases"]
    ]
    request_note = (
        "Request-parameter source review links these partial input cases: "
        + "; ".join(workflow_notes)
        + ". Inputs contain no expected results."
    )
    reviewed["rationale"] = reviewed.get(
        "rationale",
        "Source-reviewed request-parameter module with explicitly linked partial input cases.",
    )
    prior_notes = reviewed.get("stimulus_notes")
    if request_note not in (prior_notes or ""):
        reviewed["stimulus_notes"] = "; ".join(filter(None, [prior_notes, request_note]))
    prior_gate = reviewed.get("contract_gate")
    request_gate = source_review.get("contract_gate")
    if request_gate and request_gate not in (prior_gate or ""):
        reviewed["contract_gate"] = "; ".join(filter(None, [prior_gate, request_gate]))
    workflow_links = reviewed.setdefault("workflow_cases", [])
    for workflow in source_review["workflow_cases"]:
        link = {
            "recipe_path": workflow["recipe_path"],
            "case_ids": [workflow["case_id"]],
            "observation_selectors": workflow["observation_selectors"],
        }
        if link not in workflow_links:
            workflow_links.append(link)
    reviewed["supporting_sources"] = _append_unique_review_sources(
        reviewed.get("supporting_sources", []),
        [
            *source_review.get("fastapi_implementation_sources", []),
            *source_review.get("starlette_contract_sources", []),
        ],
    )
    reviewed["module_observation_selectors"] = sorted(
        set(reviewed.get("module_observation_selectors", []))
        | set(source_review["observation_selectors"])
    )

for test_path, function_rows in REQUEST_PARAMETER_FUNCTION_MAPPINGS.items():
    module_review = REQUEST_PARAMETER_SOURCE_REVIEW_MAPPINGS[test_path]
    reviewed_functions = TEST_REVIEW_MAPPINGS.setdefault(test_path, {}).setdefault("functions", {})
    for function_name, function_row in function_rows.items():
        workflow = function_row["workflow_case"]
        function_note = "Use %s::%s actions %s; the workflow is input-only and observes %s." % (
            workflow["recipe_path"],
            workflow["case_id"],
            ", ".join(workflow["action_ids"]),
            ", ".join(workflow["observation_selectors"]),
        )
        function_review = {
            "feature_ids": ["request-validation"],
            "observation_selectors": workflow["observation_selectors"],
            "rationale": function_row["rationale"],
            "replace_features": True,
            "supporting_sources": _append_unique_review_sources(
                [],
                [
                    function_row["source_span"],
                    *module_review.get("fastapi_implementation_sources", []),
                    *module_review.get("starlette_contract_sources", []),
                ],
            ),
            "stimulus_notes": function_note,
            "contract_gate": function_row["contract_gate"],
        }
        reviewed_functions.setdefault(function_name, {}).update(function_review)

DOC_EXCLUSION_OVERRIDES = {
    "contributing.md": "Contribution guidance links out to project contribution instructions; no FastAPI runtime behavior is specified.",
    "external-links.md": "Community-link generation produces documentation-site links, not FastAPI runtime behavior.",
    "fastapi-people.md": "Template-generated maintainer, contributor, reviewer, and sponsor information has no FastAPI runtime observation.",
    "help-fastapi.md": "Community and support guidance, including a promotional deployment mention, does not specify CLI or runtime behavior.",
    "how-to/testing-database.md": "The page links to external SQLModel database tutorials and specifies no FastAPI behavior.",
    "management.md": "Repository management and contribution governance are outside the FastAPI runtime contract.",
    "advanced/advanced-python-types.md": "Explains Python Union and Optional typing without specifying FastAPI behavior; response_model is mentioned only as a typing example.",
    "reference/openapi/index.md": "Short OpenAPI section overview with no independently documented callable or observable behavior; detailed utilities and models are mapped on their own pages.",
    "translation-banner.md": "Translation-quality notice and editorial link do not describe framework behavior.",
    "advanced/security/index.md": "Security section index with no behavior beyond the focused FastAPI security tutorials, which carry their own input workflows.",
    "advanced/templates.md": "Template rendering uses Starlette 1.6.0 Jinja2Templates and third-party Jinja2; FastAPI's import surface remains in the API manifest, while rendering is owned by Starlette-RS and Jinja2.",
    "advanced/wsgi.md": "WSGIMiddleware is a Starlette 1.6.0 re-export and a2wsgi is external; generic protocol bridging belongs to Starlette-RS and the third-party adapter.",
    "alternatives.md": "Comparative overview without an independently observable FastAPI runtime contract.",
    "benchmarks.md": "Performance discussion is not a parity stimulus; benchmark workloads and correctness gates are specified separately.",
    "deployment/server-workers.md": "Server worker startup, process count, and deployment behavior belong to Uvicorn and the deployment environment, outside FastAPI's library contract.",
    "editor-support.md": "Editor and language-server integration is tooling behavior, not FastAPI runtime behavior.",
    "environment-variables.md": "Environment parsing in this guide is supplied by Pydantic Settings and deployment configuration, not an independent FastAPI runtime feature.",
    "fastapi-cli.md": "The page delegates the `fastapi` console entrypoint to a separate fastapi-cli package. Treat this as a visible package-pin and process-workflow boundary; the CLI is excluded from current executable inputs until its product identity and argv/stdout/stderr/exit contract are selected.",
    "features.md": "Broad feature index with no independent stimulus; the focused feature pages carry the relevant FastAPI workflows.",
    "history-design-future.md": "Historical and design narrative, not behavior in the pinned FastAPI 0.141.1 contract.",
    "how-to/general.md": "How-to navigation page with no independently observable behavior; focused guides are mapped separately.",
    "how-to/graphql.md": "GraphQL routing and schema execution are third-party-owned; the page provides no independent FastAPI behavior case.",
    "how-to/migrate-from-pydantic-v1-to-pydantic-v2.md": "Migration guidance concerns Pydantic model APIs; the selected FastAPI contract pins Pydantic 2.13.4 and maps its integration separately.",
    "newsletter.md": "Newsletter signup and project communication content do not specify FastAPI runtime behavior.",
    "project-generation.md": "Project scaffolding and generated template behavior belong to separate tooling, outside the FastAPI runtime API.",
    "reference/middleware.md": "The reference exposes Starlette 1.6.0 middleware aliases; import paths remain in the FastAPI API manifest and generic middleware behavior belongs to Starlette-RS.",
    "reference/staticfiles.md": "This page only identifies FastAPI's direct Starlette StaticFiles re-export. Keep its import identity in the FastAPI API manifest and exclude it from an independent FastAPI behavior workflow; the separate Starlette-RS StaticFiles configuration contract is mapped below, but its missing-root and repeated-check requirements are not exercised by this page's workflow.",
    "reference/templating.md": "The reference exposes Starlette 1.6.0 Jinja2Templates; import paths remain in the FastAPI API manifest and rendering behavior belongs to Starlette-RS and Jinja2.",
    "reference/testclient.md": "The reference exposes Starlette 1.6.0 TestClient; import paths remain in the FastAPI API manifest and client/lifespan behavior belongs to Starlette-RS.",
    "release-notes.md": "Release notes span multiple historical versions and do not define one behavior of pinned FastAPI 0.141.1.",
    "translations.md": "Translation content does not define an independently observable FastAPI runtime behavior.",
    "tutorial/testing.md": "The tutorial's TestClient and HTTPX behavior belongs to the Starlette 1.6.0/client contracts; FastAPI route behavior is covered by direct ASGI workflows.",
    "virtual-environments.md": "Python environment creation and package installation guidance is contributor/setup tooling, not FastAPI runtime behavior.",
}

DOC_EXAMPLE_EXCLUSION_OVERRIDES = {
    "docs_src/debugging/tutorial001_py310.py": (
        "The only linked page is excluded debugging guidance; the example demonstrates "
        "editor/debugger and server-launch setup, not an independently observable FastAPI behavior."
    ),
    "docs_src/app_testing/app_a_py310/main.py": (
        "This source is a simple app embedded in a generic TestClient tutorial. Its FastAPI "
        "route behavior is covered by direct-ASGI request workflows; TestClient behavior is "
        "owned by the separate Starlette 1.6.0 contract."
    ),
    "docs_src/app_testing/app_a_py310/test_main.py": (
        "This example tests a FastAPI app through TestClient. The TestClient/HTTPX behavior is "
        "owned by Starlette-RS; FastAPI route behavior is covered through direct-ASGI inputs."
    ),
    "docs_src/app_testing/app_b_an_py310/main.py": (
        "This app is embedded in the TestClient tutorial; its header, validation, exception, "
        "and response-model behavior is covered by independent FastAPI ASGI workflows."
    ),
    "docs_src/app_testing/app_b_an_py310/test_main.py": (
        "The example invokes FastAPI routes through TestClient. Client mechanics belong to the "
        "Starlette-RS contract; FastAPI route behavior is represented by direct-ASGI workflows."
    ),
    "docs_src/app_testing/app_b_py310/main.py": (
        "This app is embedded in the TestClient tutorial; its header, validation, exception, "
        "and response-model behavior is covered by independent FastAPI ASGI workflows."
    ),
    "docs_src/app_testing/app_b_py310/test_main.py": (
        "The example invokes FastAPI routes through TestClient. Client mechanics belong to the "
        "Starlette-RS contract; FastAPI route behavior is represented by direct-ASGI workflows."
    ),
    "docs_src/app_testing/tutorial001_py310.py": (
        "This example tests a FastAPI route through TestClient. Client mechanics belong to the "
        "Starlette-RS contract; FastAPI route behavior is covered through direct-ASGI inputs."
    ),
    "docs_src/graphql_/tutorial001_py310.py": (
        "This example runs a third-party Strawberry GraphQL router and schema. GraphQL "
        "execution is not FastAPI-owned behavior."
    ),
    "docs_src/pydantic_v1_in_v2/tutorial001_an_py310.py": (
        "This example is Pydantic-only; FastAPI 0.141.1 uses Pydantic v2 and does not expose "
        "the historical FastAPI support for pydantic.v1 models."
    ),
    "docs_src/pydantic_v1_in_v2/tutorial002_an_py310.py": (
        "This example documents temporary pydantic.v1 support that FastAPI removed in 0.128.0; "
        "it is not part of the FastAPI 0.141.1 contract."
    ),
    "docs_src/pydantic_v1_in_v2/tutorial003_an_py310.py": (
        "This example documents temporary mixed Pydantic v1/v2 route support that FastAPI "
        "removed in 0.128.0; it is not part of the FastAPI 0.141.1 contract."
    ),
    "docs_src/pydantic_v1_in_v2/tutorial004_an_py310.py": (
        "This example uses fastapi.temp_pydantic_v1_params for temporary Pydantic v1 support "
        "removed in FastAPI 0.128.0; it is not part of the 0.141.1 contract."
    ),
    "docs_src/settings/app02_py310/config.py": (
        "This file only defines a pydantic_settings.BaseSettings subclass. Environment parsing, "
        "defaults, and settings construction are Pydantic Settings behavior; the linked FastAPI "
        "dependency-override input does not exercise this file's behavior."
    ),
    "docs_src/templates/tutorial001_py310.py": (
        "This example exercises Starlette 1.6.0 StaticFiles and Jinja2Templates with Jinja2. "
        "FastAPI's import paths remain in the API manifest; generic static and template "
        "behavior belongs to Starlette-RS and Jinja2."
    ),
    "docs_src/wsgi/tutorial001_py310.py": (
        "This example bridges Flask through third-party a2wsgi and Starlette's WSGIMiddleware. "
        "The adapter and generic protocol bridge are outside FastAPI-owned behavior."
    ),
}

DOC_RELATED_USAGE_SOURCES = {
    "reference/encoders.md": [
        {
            "path": "fastapi/encoders.py",
            "start_line": 119,
            "end_line": 206,
            "role": "documented encoder signature and options",
        },
        {
            "path": "fastapi/encoders.py",
            "start_line": 218,
            "end_line": 352,
            "role": "encoder conversion behavior",
        },
        {
            "path": "docs_src/response_directly/tutorial001_py310.py",
            "start_line": 4,
            "end_line": 21,
            "role": "encoder output used as a JSON response",
        },
        {
            "path": "docs_src/body_updates/tutorial001_py310.py",
            "start_line": 2,
            "end_line": 30,
            "role": "encoder used in update-and-return workflow",
        },
        {
            "path": "docs_src/encoder/tutorial001_py310.py",
            "start_line": 4,
            "end_line": 22,
            "role": "Pydantic model and datetime conversion example",
        },
        {
            "path": "docs_src/handling_errors/tutorial005_py310.py",
            "start_line": 2,
            "end_line": 15,
            "role": "encoded validation-error payload",
        },
    ],
}

DOC_PAGE_REVIEW_MAPPINGS = {
    "reference/exceptions.md": {
        "replace_features": True,
        "feature_ids": ["public-api-errors"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "websocket.close_code",
            "python.import_path",
            "python.object_identity",
            "python.signature",
        ],
        "rationale": (
            "The reference documents FastAPI's HTTPException and WebSocketException imports and "
            "constructors. FastAPI handles HTTPException as a JSON response; WebSocketException "
            "closes through Starlette's ASGI exception middleware. The two ASGI workflows observe "
            "those results, while direct API probes observe the constructor signatures."
        ),
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/exceptions.md",
                "start_line": 1,
                "end_line": 20,
                "role": "documented HTTP and WebSocket exception imports and public names",
            },
            {
                "path": "fastapi/exceptions.py",
                "start_line": 17,
                "end_line": 83,
                "role": "FastAPI HTTPException subclass and public constructor",
            },
            {
                "path": "fastapi/exceptions.py",
                "start_line": 86,
                "end_line": 154,
                "role": "FastAPI WebSocketException subclass and public constructor",
            },
            {
                "path": "fastapi/exception_handlers.py",
                "start_line": 11,
                "end_line": 17,
                "role": "FastAPI HTTP exception response mapping",
            },
        ],
        "starlette_contract_sources": [
            {
                "path": "starlette/exceptions.py",
                "start_line": 7,
                "end_line": 14,
                "role": "Starlette 1.6.0 HTTPException public fields",
            },
            {
                "path": "starlette/exceptions.py",
                "start_line": 23,
                "end_line": 26,
                "role": "Starlette 1.6.0 WebSocketException public fields",
            },
            {
                "path": "starlette/middleware/exceptions.py",
                "start_line": 65,
                "end_line": 73,
                "role": "Starlette 1.6.0 HTTP and WebSocket exception dispatch",
            },
        ],
    },
    "reference/testclient.md": {
        "feature_ids": ["public-api-errors"],
        "observation_selectors": ["python.import_path", "python.object_identity"],
        "rationale": "The reference documents the FastAPI import path, while the pinned source aliases Starlette 1.6.0 TestClient directly; generic client behavior remains Starlette-RS-owned.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/testclient.md",
                "start_line": 7,
                "end_line": 13,
                "role": "documented FastAPI TestClient import path",
            },
            {
                "path": "fastapi/testclient.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette TestClient re-export",
            },
        ],
    },
    "advanced/async-tests.md": {
        "replace_features": True,
        "feature_ids": ["app-routing"],
        "observation_selectors": ["http.status", "http.body.json", "route.match"],
        "rationale": "The page exercises an ordinary FastAPI HTTP route. Async pytest, HTTPX AsyncClient, TestClient, and lifespan-driving behavior belong to their respective harness and Starlette contracts; the LifespanManager note is external test setup, not a FastAPI lifecycle feature.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/async-tests.md",
                "start_line": 13,
                "end_line": 20,
                "role": "HTTPX async request example and TestClient boundary",
            },
            {
                "path": "docs/en/docs/advanced/async-tests.md",
                "start_line": 63,
                "end_line": 87,
                "role": "async test and external lifespan-manager guidance",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 42,
                "end_line": 45,
                "role": "FastAPI application class over Starlette",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1165,
                "end_line": 1190,
                "role": "FastAPI route registration surface",
            },
        ],
    },
    "advanced/behind-a-proxy.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "openapi.document",
            "docs.response.body.bytes",
        ],
        "rationale": "Only FastAPI root-path routing and generated OpenAPI/docs URL effects belong here. Forwarded-header interpretation and proxy configuration are server/proxy behavior; generic middleware, dependency/security, and request-validation selectors are false keyword matches.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/behind-a-proxy.md",
                "start_line": 7,
                "end_line": 27,
                "role": "server and proxy forwarded-header configuration",
            },
            {
                "path": "docs/en/docs/advanced/behind-a-proxy.md",
                "start_line": 98,
                "end_line": 112,
                "role": "FastAPI root_path and stripped-prefix documentation",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1105,
                "end_line": 1137,
                "role": "FastAPI applies ASGI root_path to OpenAPI and docs URLs",
            },
        ],
    },
    "advanced/custom-response.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "public-api-errors",
            "response-serialization",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.bytes",
            "http.body.json",
            "route.match",
            "openapi.document",
            "python.import_path",
            "python.object_identity",
            "warnings.category_message",
        ],
        "rationale": "FastAPI selects response classes, applies response-model serialization, and generates response documentation; direct Response values bypass those FastAPI steps. Remove request-validation and middleware noise. Generic response rendering is Starlette-owned; UJSONResponse and ORJSONResponse are FastAPI deprecated exports.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/custom-response.md",
                "start_line": 5,
                "end_line": 15,
                "role": "direct Response and response_class behavior",
            },
            {
                "path": "docs/en/docs/advanced/custom-response.md",
                "start_line": 23,
                "end_line": 27,
                "role": "FastAPI response-model and encoder distinction",
            },
            {
                "path": "docs/en/docs/advanced/custom-response.md",
                "start_line": 247,
                "end_line": 253,
                "role": "deprecated optimized response discussion",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI response-model serialization",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 39,
                "end_line": 78,
                "role": "FastAPI UJSONResponse and ORJSONResponse deprecation declarations",
            },
        ],
    },
    "advanced/events.md": {
        "replace_features": True,
        "feature_ids": ["public-api-errors", "websocket-lifecycle"],
        "observation_selectors": [
            "asgi.lifespan.event_order",
            "asgi.lifespan.startup",
            "asgi.lifespan.shutdown",
            "asgi.lifespan.application_errors",
            "asgi.lifespan.workload_trace",
            "http.status",
            "http.body.bytes",
            "warnings.category_message",
        ],
        "rationale": "The page covers FastAPI lifespan and deprecated startup/shutdown handlers. The v4 direct-ASGI workflow maps startup, shutdown, request-visible merged state, callback effects, and selected on_event warning records; TestClient lifecycle driving and TestClient.app_state remain Starlette-owned.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/events.md",
                "start_line": 25,
                "end_line": 31,
                "role": "FastAPI lifespan parameter and context manager",
            },
            {
                "path": "docs/en/docs/advanced/events.md",
                "start_line": 87,
                "end_line": 115,
                "role": "deprecated startup and shutdown alternatives",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 6415,
                "end_line": 6445,
                "role": "FastAPI on_event deprecation and handler registration",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 2520,
                "end_line": 2537,
                "role": "FastAPI router lifespan context wiring",
            },
        ],
    },
    "advanced/response-change-status-code.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.json",
            "dependency.call_order",
            "route.match",
        ],
        "rationale": "FastAPI injects a temporary Response into routes and dependencies, then copies its status/header/cookie values onto the final response; the last dependency write wins. Request-validation and OpenAPI security/schema selectors do not describe this page.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/response-change-status-code.md",
                "start_line": 15,
                "end_line": 31,
                "role": "temporary Response injection and last-write-wins behavior",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI special injection for Response parameters",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 357,
                "end_line": 372,
                "role": "FastAPI combines status from route and injected response",
            },
        ],
    },
    "advanced/response-cookies.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.json",
            "dependency.call_order",
            "route.match",
        ],
        "rationale": "The FastAPI-specific behavior is injected Response state from a route/dependency and its transfer to the final response. Drop request-validation and OpenAPI selectors. Direct cookie construction and cookie header semantics belong to Starlette's response contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/response-cookies.md",
                "start_line": 3,
                "end_line": 17,
                "role": "temporary Response cookie injection",
            },
            {
                "path": "docs/en/docs/advanced/response-cookies.md",
                "start_line": 39,
                "end_line": 51,
                "role": "Starlette response ownership and FastAPI import convenience",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI special injection for Response parameters",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 357,
                "end_line": 372,
                "role": "FastAPI response status transfer",
            },
        ],
    },
    "advanced/response-headers.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.json",
            "dependency.call_order",
            "route.match",
        ],
        "rationale": "FastAPI injects a temporary Response into routes and dependencies and transfers header state to the final response. The CORS mention is only a link to Starlette guidance, not middleware behavior under this page; remove middleware, request-validation, and OpenAPI security selectors. Raw header and CORS behavior belongs to Starlette.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/response-headers.md",
                "start_line": 3,
                "end_line": 17,
                "role": "temporary Response header injection",
            },
            {
                "path": "docs/en/docs/advanced/response-headers.md",
                "start_line": 37,
                "end_line": 41,
                "role": "CORS link to Starlette ownership",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI special injection for Response parameters",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 357,
                "end_line": 372,
                "role": "FastAPI response status transfer",
            },
        ],
    },
    "advanced/security/http-basic-auth.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "openapi-docs", "public-api-errors"],
        "observation_selectors": [
            "dependency.call_order",
            "error.class",
            "error.public_attributes",
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "openapi.document",
            "openapi.security",
            "python.import_path",
            "python.object_identity",
        ],
        "rationale": "HTTPBasic is a FastAPI security dependency whose scheme is represented in OpenAPI. Credential extraction is dependency behavior, not ordinary Pydantic request validation; remove request-validation and its error selectors. Error responses are observable only when the security dependency raises them, not when application logic chooses a credential policy.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/security/http-basic-auth.md",
                "start_line": 17,
                "end_line": 25,
                "role": "HTTP Basic dependency and generated security documentation",
            },
            {
                "path": "fastapi/security/http.py",
                "start_line": 105,
                "end_line": 155,
                "role": "FastAPI HTTPBasic public security dependency",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 132,
                "end_line": 156,
                "role": "FastAPI OpenAPI security scheme assembly",
            },
        ],
    },
    "advanced/settings.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security"],
        "observation_selectors": [
            "http.status",
            "http.body.json",
            "dependency.call_order",
            "route.match",
        ],
        "rationale": "The FastAPI contribution is injecting or overriding a settings dependency. Environment lookup, settings construction, and their validation are Pydantic Settings behavior, not FastAPI HTTP request validation; the page's settings keyword also does not make this middleware behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/settings.md",
                "start_line": 25,
                "end_line": 69,
                "role": "Pydantic Settings owns environment parsing and validation",
            },
            {
                "path": "docs/en/docs/advanced/settings.md",
                "start_line": 143,
                "end_line": 155,
                "role": "settings injected through a FastAPI dependency",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI dependency parameter analysis",
            },
        ],
    },
    "advanced/templates.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "middleware-integrations", "response-serialization"],
        "observation_selectors": [
            "python.import_path",
            "python.object_identity",
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
        ],
        "rationale": "The FastAPI-specific parts are app route setup and the FastAPI import convenience. Jinja2Templates, template rendering, Request, StaticFiles, and generic HTML response behavior are provided by Starlette; remove dependency, request-validation, and process selectors.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/templates.md",
                "start_line": 7,
                "end_line": 8,
                "role": "page identifies template utilities as Starlette-provided",
            },
            {
                "path": "docs/en/docs/advanced/templates.md",
                "start_line": 23,
                "end_line": 50,
                "role": "Jinja2Templates use and FastAPI import convenience",
            },
            {
                "path": "fastapi/templating.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette Jinja2Templates re-export",
            },
        ],
    },
    "advanced/wsgi.md": {
        "replace_features": True,
        "feature_ids": ["middleware-integrations"],
        "observation_selectors": ["python.import_path", "python.object_identity"],
        "rationale": "This page recommends a2wsgi and describes the old FastAPI import as deprecated. The pinned FastAPI module is a direct Starlette WSGIMiddleware alias and does not implement WSGI execution or emit a deprecation warning; remove request-validation, process, HTTP, and warning selectors. Mount/bridge behavior belongs to Starlette and a2wsgi.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/wsgi.md",
                "start_line": 7,
                "end_line": 29,
                "role": "a2wsgi recommendation and old import path description",
            },
            {
                "path": "fastapi/middleware/wsgi.py",
                "start_line": 1,
                "end_line": 3,
                "role": "identity-preserving Starlette WSGIMiddleware re-export",
            },
        ],
    },
    "advanced/stream-data.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
        ],
        "rationale": "FastAPI invokes the generator and passes raw chunks to the declared response class without JSON conversion. Remove request-validation and OpenAPI request-schema selectors. StreamingResponse transport/chunk delivery is generic Starlette behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/stream-data.md",
                "start_line": 21,
                "end_line": 43,
                "role": "raw StreamingResponse chunks bypass FastAPI conversion",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 683,
                "end_line": 704,
                "role": "FastAPI invokes raw generator endpoints and constructs the response class",
            },
        ],
    },
    "advanced/testing-events.md": {
        "replace_features": True,
        "feature_ids": ["public-api-errors", "websocket-lifecycle"],
        "observation_selectors": [
            "asgi.lifespan.event_order",
            "asgi.lifespan.startup",
            "asgi.lifespan.shutdown",
            "asgi.lifespan.application_errors",
            "asgi.lifespan.workload_trace",
            "warnings.category_message",
        ],
        "rationale": "The page explains FastAPI lifespan registration through TestClient. The v3 direct-ASGI workflow observes FastAPI lifecycle effects; TestClient context-manager and app-state behavior remain Starlette-RS-owned, and on_event warning capture is still planned.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/testing-events.md",
                "start_line": 3,
                "end_line": 10,
                "role": "TestClient lifespan context and explicit Starlette ownership link",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 6415,
                "end_line": 6445,
                "role": "FastAPI on_event deprecation and registration",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 2520,
                "end_line": 2537,
                "role": "FastAPI lifespan context wiring",
            },
        ],
    },
    "advanced/testing-websockets.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "websocket-lifecycle"],
        "observation_selectors": ["route.match", "websocket.messages"],
        "rationale": "The page's FastAPI behavior is WebSocket route registration and endpoint messages. TestClient websocket_connect/session transport is explicitly delegated to Starlette; this page has no lifespan, HTTP-response, or OpenAPI observation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/advanced/testing-websockets.md",
                "start_line": 3,
                "end_line": 11,
                "role": "TestClient WebSocket example and Starlette ownership link",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1376,
                "end_line": 1398,
                "role": "FastAPI WebSocket route registration surface",
            },
        ],
    },
    "reference/apirouter.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "openapi-docs",
            "request-validation",
            "response-serialization",
            "websocket-lifecycle",
        ],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "route.match",
            "dependency.call_order",
            "validation.error_class",
            "validation.error_details",
            "openapi.paths",
            "openapi.request_schema",
            "openapi.security",
            "websocket.messages",
            "lifecycle.event_order",
        ],
        "rationale": "APIRouter's documented members include route decorators, include_router, websocket, and on_event. Its FastAPI contract spans route composition, dependencies, parameter validation, response configuration, and generated OpenAPI; retain WebSocket/lifespan coverage only for those explicit members.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/apirouter.md",
                "start_line": 1,
                "end_line": 25,
                "role": "APIRouter import and documented member allowlist",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 2889,
                "end_line": 2910,
                "role": "APIRouter route signature includes response, dependency, and operation settings",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 3133,
                "end_line": 3155,
                "role": "FastAPI router composition and dependency configuration",
            },
        ],
    },
    "reference/background.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "dependency.call_order",
            "response.background_effects",
            "route.match",
        ],
        "rationale": "FastAPI injects and merges BackgroundTasks for route/dependency use; the task executes after the response. Remove request-validation. Starlette owns the inherited task collection and post-send execution semantics.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/background.md",
                "start_line": 1,
                "end_line": 11,
                "role": "documented BackgroundTasks injection and FastAPI import",
            },
            {
                "path": "fastapi/background.py",
                "start_line": 5,
                "end_line": 11,
                "role": "FastAPI BackgroundTasks subclasses Starlette's collection",
            },
            {
                "path": "fastapi/background.py",
                "start_line": 40,
                "end_line": 61,
                "role": "FastAPI add_task delegates to Starlette",
            },
        ],
    },
    "reference/fastapi.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "middleware-integrations",
            "openapi-docs",
            "public-api-errors",
            "request-validation",
            "response-serialization",
            "websocket-lifecycle",
        ],
        "observation_selectors": [
            "python.import_path",
            "python.signature",
            "python.attribute_value",
            "warnings.category_message",
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "validation.error_class",
            "validation.error_details",
            "route.match",
            "dependency.call_order",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
            "openapi.security",
            "docs.response.status",
            "docs.response.body.bytes",
            "response.background_effects",
            "websocket.messages",
            "websocket.event_order",
            "lifecycle.event_order",
            "lifecycle.cleanup_effects",
        ],
        "rationale": "This is the full FastAPI class reference. The curated set covers its route methods, dependency overrides, request/response configuration, OpenAPI, WebSocket/lifespan, middleware and public API signatures. Request validation and response serialization were missing from the previous mapping; generic process stdout/stderr are not FastAPI class behavior.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/fastapi.md",
                "start_line": 1,
                "end_line": 32,
                "role": "full FastAPI class reference and member list",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 42,
                "end_line": 45,
                "role": "FastAPI subclasses Starlette",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1165,
                "end_line": 1195,
                "role": "FastAPI route registration signature and response configuration",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 301,
                "end_line": 342,
                "role": "FastAPI response validation and serialization",
            },
            {
                "path": "fastapi/applications.py",
                "start_line": 1105,
                "end_line": 1120,
                "role": "FastAPI OpenAPI route generation and serving",
            },
        ],
    },
    "reference/httpconnection.md": {
        "replace_features": True,
        "feature_ids": ["dependency-security"],
        "observation_selectors": [
            "http.status",
            "http.body.bytes",
            "websocket.messages",
        ],
        "rationale": "FastAPI recognizes the Starlette HTTPConnection alias for dependency injection in both HTTP and WebSocket endpoints. The independent HTTP and WebSocket cases observe the injected app-state value; generic connection scopes and WebSocket transport remain Starlette-owned.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/httpconnection.md",
                "start_line": 1,
                "end_line": 11,
                "role": "HTTPConnection reference and dependency compatibility",
            },
            {
                "path": "fastapi/requests.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette HTTPConnection re-export",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI special injection for HTTPConnection parameters",
            },
        ],
    },
    "reference/openapi/docs.md": {
        "replace_features": True,
        "feature_ids": ["openapi-docs"],
        "observation_selectors": [
            "python.signature",
            "python.attribute_value",
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
        ],
        "rationale": "The page documents FastAPI HTML helper callables and their signatures, not authentication dependencies or mounted docs endpoint behavior. OAuth2 is mentioned only for the Swagger redirect. Returned HTMLResponse rendering remains Starlette-owned.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/openapi/docs.md",
                "start_line": 1,
                "end_line": 11,
                "role": "OpenAPI docs helper reference",
            },
            {
                "path": "fastapi/openapi/docs.py",
                "start_line": 40,
                "end_line": 65,
                "role": "FastAPI Swagger UI HTML helper signature",
            },
            {
                "path": "fastapi/openapi/docs.py",
                "start_line": 197,
                "end_line": 224,
                "role": "FastAPI ReDoc HTML helper signature",
            },
            {
                "path": "fastapi/openapi/docs.py",
                "start_line": 301,
                "end_line": 307,
                "role": "FastAPI OAuth2 redirect HTML helper",
            },
        ],
    },
    "reference/openapi/models.md": {
        "replace_features": True,
        "feature_ids": ["openapi-docs"],
        "observation_selectors": [
            "python.import_path",
            "python.signature",
            "python.attribute_value",
            "openapi.document",
        ],
        "rationale": "The page documents FastAPI's public OpenAPI model types, which are Pydantic models. Direct probes cover public signatures; a reference workflow uses Info as a response model and observes its schema in generated OpenAPI. This checks FastAPI's Pydantic integration under the pinned dependency, not standalone Pydantic construction or validation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/openapi/models.md",
                "start_line": 1,
                "end_line": 5,
                "role": "OpenAPI models explicitly identified as Pydantic models",
            },
            {
                "path": "fastapi/openapi/models.py",
                "start_line": 57,
                "end_line": 104,
                "role": "FastAPI OpenAPI model classes derive from Pydantic models",
            },
        ],
    },
    "reference/request.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "dependency-security", "public-api-errors"],
        "observation_selectors": [
            "python.import_path",
            "python.object_identity",
            "dependency.call_order",
            "route.match",
            "http.status",
            "http.body.bytes",
        ],
        "rationale": "Request is a direct Starlette alias, and FastAPI's DI special-cases it for route injection. The independent request-injection workflow observes the raw request-derived HTTP result. The page's HTTPConnection note is dependency compatibility, not WebSocket lifecycle; request parsing and methods belong to Starlette.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/request.md",
                "start_line": 1,
                "end_line": 15,
                "role": "Request import and raw request guidance",
            },
            {
                "path": "fastapi/requests.py",
                "start_line": 1,
                "end_line": 2,
                "role": "identity-preserving Starlette Request and HTTPConnection re-exports",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI special injection for Request parameters",
            },
        ],
    },
    "reference/response.md": {
        "replace_features": True,
        "feature_ids": [
            "app-routing",
            "dependency-security",
            "public-api-errors",
            "response-serialization",
        ],
        "observation_selectors": [
            "python.import_path",
            "python.object_identity",
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.bytes",
            "http.body.json",
            "dependency.call_order",
            "route.match",
        ],
        "rationale": "FastAPI injects Response into routes/dependencies and copies temporary response metadata; it also re-exports Starlette Response at fastapi.Response. Remove request-validation and OpenAPI selectors. Response construction and wire behavior remain in Starlette's contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/response.md",
                "start_line": 1,
                "end_line": 15,
                "role": "Response injection, direct return, and public import path",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 22,
                "end_line": 22,
                "role": "FastAPI root exports the response alias",
            },
            {
                "path": "fastapi/dependencies/utils.py",
                "start_line": 350,
                "end_line": 365,
                "role": "FastAPI special injection for Response parameters",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 357,
                "end_line": 372,
                "role": "FastAPI merges injected Response status into final response",
            },
        ],
    },
    "reference/responses.md": {
        "replace_features": True,
        "feature_ids": ["public-api-errors", "response-serialization"],
        "observation_selectors": [
            "python.import_path",
            "python.object_identity",
            "warnings.category_message",
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.bytes",
            "http.body.json",
        ],
        "rationale": "FastAPI re-exports the standard response classes from Starlette and defines deprecated UJSONResponse/ORJSONResponse. Remove request-validation and OpenAPI request-schema selectors. Standard response rendering is Starlette-owned; FastAPI-specific contract is alias identity and deprecation.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/responses.md",
                "start_line": 7,
                "end_line": 31,
                "role": "response export list and FastAPI deprecation notice",
            },
            {
                "path": "docs/en/docs/reference/responses.md",
                "start_line": 63,
                "end_line": 75,
                "role": "remaining response classes identified as Starlette-provided",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 6,
                "end_line": 12,
                "role": "identity-preserving Starlette response exports",
            },
            {
                "path": "fastapi/responses.py",
                "start_line": 39,
                "end_line": 78,
                "role": "FastAPI UJSONResponse and ORJSONResponse deprecation declarations",
            },
        ],
    },
    "reference/security/index.md": {
        "replace_features": True,
        "feature_ids": ["dependency-security", "openapi-docs", "request-validation"],
        "observation_selectors": [
            "dependency.call_order",
            "http.status",
            "http.headers.ordered",
            "http.body.json",
            "validation.error_class",
            "validation.error_details",
            "openapi.document",
            "openapi.request_schema",
            "openapi.security",
        ],
        "rationale": "Security dependencies and generated OpenAPI security definitions are FastAPI behavior; OAuth2 password-form fields also pass through FastAPI dependency parameter extraction. Remove docs.response selectors because the page describes generated OpenAPI UI integration, not UI response rendering. Pydantic credential/model internals remain excluded.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/security/index.md",
                "start_line": 1,
                "end_line": 31,
                "role": "security dependency and OpenAPI integration overview",
            },
            {
                "path": "docs/en/docs/reference/security/index.md",
                "start_line": 55,
                "end_line": 73,
                "role": "OAuth2 password form and scope dependencies",
            },
            {
                "path": "fastapi/security/oauth2.py",
                "start_line": 14,
                "end_line": 49,
                "role": "FastAPI OAuth2PasswordRequestForm fields",
            },
            {
                "path": "fastapi/openapi/utils.py",
                "start_line": 132,
                "end_line": 156,
                "role": "FastAPI OpenAPI security scheme assembly",
            },
        ],
    },
    "reference/sse.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "openapi-docs", "response-serialization"],
        "observation_selectors": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "openapi.document",
        ],
        "rationale": "FastAPI provides EventSourceResponse, ServerSentEvent formatting, routing integration, and the SSE response schema. Remove request-validation; ServerSentEvent field validation is Pydantic-owned and generic streaming response delivery is Starlette-owned.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/sse.md",
                "start_line": 1,
                "end_line": 17,
                "role": "SSE response classes and route usage",
            },
            {
                "path": "fastapi/sse.py",
                "start_line": 20,
                "end_line": 34,
                "role": "FastAPI EventSourceResponse over Starlette StreamingResponse",
            },
            {
                "path": "fastapi/sse.py",
                "start_line": 52,
                "end_line": 76,
                "role": "FastAPI ServerSentEvent public model",
            },
            {
                "path": "fastapi/sse.py",
                "start_line": 165,
                "end_line": 190,
                "role": "FastAPI SSE event formatting helper",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 640,
                "end_line": 646,
                "role": "FastAPI response construction for SSE streams",
            },
        ],
    },
    "reference/staticfiles.md": {
        "replace_features": True,
        "feature_ids": ["middleware-integrations"],
        "observation_selectors": ["python.import_path", "python.object_identity"],
        "rationale": "FastAPI exposes StaticFiles through a convenience import, but the pinned source is an exact Starlette alias. Remove HTTP/process selectors from the FastAPI page mapping; static-file serving, mounting, and response behavior belong to the Starlette contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/staticfiles.md",
                "start_line": 1,
                "end_line": 13,
                "role": "StaticFiles public FastAPI import path",
            },
            {
                "path": "fastapi/staticfiles.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette StaticFiles re-export",
            },
        ],
    },
    "reference/templating.md": {
        "replace_features": True,
        "feature_ids": ["middleware-integrations"],
        "observation_selectors": ["python.import_path", "python.object_identity"],
        "rationale": "FastAPI's templating module is an import convenience for Starlette Jinja2Templates. Remove HTTP/process selectors as FastAPI behavior; template construction, rendering, and resulting responses belong to Starlette.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/templating.md",
                "start_line": 1,
                "end_line": 13,
                "role": "Jinja2Templates public FastAPI import path",
            },
            {
                "path": "fastapi/templating.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette Jinja2Templates re-export",
            },
        ],
    },
    "reference/middleware.md": {
        "replace_features": True,
        "feature_ids": ["middleware-integrations"],
        "observation_selectors": ["python.import_path", "python.object_identity"],
        "rationale": "The page explicitly says the listed middleware is provided directly by Starlette, and FastAPI middleware modules are aliases. Track the FastAPI import surface only here; configuration and HTTP effects belong to the Starlette contract.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/middleware.md",
                "start_line": 1,
                "end_line": 37,
                "role": "middleware reference and Starlette ownership statement",
            },
            {
                "path": "fastapi/middleware/cors.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette CORSMiddleware re-export",
            },
            {
                "path": "fastapi/middleware/gzip.py",
                "start_line": 1,
                "end_line": 1,
                "role": "identity-preserving Starlette GZipMiddleware re-export",
            },
        ],
    },
    "reference/status.md": {
        "replace_features": True,
        "feature_ids": ["app-routing", "public-api-errors", "response-serialization"],
        "observation_selectors": [
            "python.import_path",
            "python.object_identity",
            "python.attribute_value",
            "http.status",
            "route.match",
        ],
        "rationale": "FastAPI's status module is directly imported from Starlette; the page separately illustrates FastAPI's status_code route option. Remove WebSocket/lifespan selectors: status constant names do not imply those behaviors. Constant values belong to Starlette; route status configuration belongs to FastAPI.",
        "supporting_sources": [
            {
                "path": "docs/en/docs/reference/status.md",
                "start_line": 1,
                "end_line": 34,
                "role": "Starlette status alias and FastAPI status_code example",
            },
            {
                "path": "fastapi/__init__.py",
                "start_line": 5,
                "end_line": 5,
                "role": "FastAPI root exports Starlette status module directly",
            },
            {
                "path": "fastapi/routing.py",
                "start_line": 357,
                "end_line": 372,
                "role": "FastAPI route and injected response status resolution",
            },
        ],
    },
}


# Normalize source-reviewed test waves that retain action IDs in their sidecars
# to the atlas's stable workflow-case contract.
def _normalize_source_review_workflow_mappings(
    additions: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    normalized_modules = {}
    for test_path, module_review in additions.items():
        normalized_functions = {}
        module_workflows = {}
        scope_exclusions: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
        for exclusion in module_review.get("source_review_scope_exclusions", []):
            note = "Source-backed scope exclusion (%s): %s" % (
                exclusion.get("scope", "partial behavior"),
                exclusion["reason"],
            )
            for function_name in exclusion.get("test_functions", {}):
                scope_exclusions[function_name].append((note, exclusion))

        for function_name, function_review in module_review.get("functions", {}).items():
            if function_review.get("review_status") == "reviewed_excluded":
                TEST_FUNCTION_EXCLUSIONS.setdefault(test_path, {})[function_name] = function_review[
                    "exclusion_reason"
                ]
                TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(test_path, {})[function_name] = (
                    function_review.get("supporting_sources", [])
                )
                continue

            function_mapping = {
                key: value
                for key, value in function_review.items()
                if key not in {"review_status", "workflow_cases"}
            }
            for note, exclusion in scope_exclusions.get(function_name, []):
                gate = function_mapping.get("contract_gate", "")
                if note not in gate:
                    function_mapping["contract_gate"] = "; ".join(filter(None, (gate, note)))
                function_mapping["supporting_sources"] = _append_unique_review_sources(
                    function_mapping.get("supporting_sources", []),
                    exclusion.get("supporting_sources", []),
                )

            function_workflows = []
            for link in function_review.get("workflow_cases", []):
                case_ids = link.get("case_ids", [link.get("case_id")])
                for case_id in case_ids:
                    normalized_link = {
                        "recipe_path": link["recipe_path"],
                        "case_ids": [case_id],
                        "observation_selectors": link["observation_selectors"],
                    }
                    function_workflows.append(normalized_link)

                    workflow_key = (link["recipe_path"], case_id)
                    module_link = module_workflows.setdefault(
                        workflow_key,
                        {
                            "recipe_path": link["recipe_path"],
                            "case_ids": [],
                            "observation_selectors": set(),
                        },
                    )
                    if case_id not in module_link["case_ids"]:
                        module_link["case_ids"].append(case_id)
                    module_link["observation_selectors"].update(link["observation_selectors"])

            function_mapping["workflow_cases"] = function_workflows
            normalized_functions[function_name] = function_mapping

        normalized_module = {
            "rationale": module_review["rationale"],
            "supporting_sources": module_review.get("supporting_sources", []),
            "module_observation_selectors": module_review.get("module_observation_selectors", []),
            "workflow_cases": [
                {
                    **link,
                    "observation_selectors": sorted(link["observation_selectors"]),
                }
                for link in module_workflows.values()
            ],
            "stimulus_notes": module_review.get("stimulus_notes", ""),
            "functions": normalized_functions,
        }
        for key in ("contract_gate", "constraints"):
            if key in module_review:
                normalized_module[key] = module_review[key]
        normalized_modules[test_path] = normalized_module
    return normalized_modules


from atlas_response_model_data_filter_policy_review_mappings import (  # noqa: E402
    RESPONSE_MODEL_DATA_FILTER_POLICY_REVIEW_MAPPINGS,
)

merge_test_review_mappings(
    _normalize_source_review_workflow_mappings(RESPONSE_MODEL_DATA_FILTER_POLICY_REVIEW_MAPPINGS)
)

from atlas_request_body_tutorial_review_mappings import (  # noqa: E402
    REQUEST_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS,
)

merge_test_review_mappings(
    _normalize_source_review_workflow_mappings(REQUEST_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS)
)

from atlas_path_operation_parameter_tutorials_mappings import (  # noqa: E402
    PATH_OPERATION_PARAMETER_TUTORIALS_MAPPINGS,
)

merge_test_review_mappings(
    _normalize_source_review_workflow_mappings(PATH_OPERATION_PARAMETER_TUTORIALS_MAPPINGS)
)

from atlas_openapi_tutorial_interface_review_mappings import (  # noqa: E402
    OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS,
)

_openapi_tutorial_review_mappings = {}
for (
    _openapi_tutorial_path,
    _openapi_tutorial_module,
) in OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS.items():
    _openapi_tutorial_functions = {}
    for _openapi_tutorial_name, _openapi_tutorial_function in _openapi_tutorial_module[
        "functions"
    ].items():
        _openapi_tutorial_status = _openapi_tutorial_function.get("mapping_status")
        if _openapi_tutorial_status == "reviewed_excluded_from_asgi_input_lane":
            _openapi_exclusion = _openapi_tutorial_function["exclusion"]
            TEST_FUNCTION_EXCLUSIONS.setdefault(_openapi_tutorial_path, {})[
                _openapi_tutorial_name
            ] = _openapi_exclusion["reason"]
            TEST_FUNCTION_EXCLUSION_EVIDENCE.setdefault(_openapi_tutorial_path, {})[
                _openapi_tutorial_name
            ] = _append_unique_review_sources(
                _openapi_tutorial_function.get("supporting_sources", []),
                [_openapi_tutorial_function["source_span"]]
                if _openapi_tutorial_function.get("source_span")
                else [],
            )
            continue

        _openapi_function_notes = []
        for _feature_id, _feature_review in _openapi_tutorial_function.get(
            "feature_status", {}
        ).items():
            _openapi_function_notes.append(
                f"{_feature_id}: {_feature_review.get('status')} — {_feature_review.get('scope')}"
            )
        _openapi_scope = _openapi_tutorial_function.get("openapi_observation_scope")
        if _openapi_scope and _openapi_scope != "not_applicable":
            _openapi_function_notes.append(f"OpenAPI observation scope: {_openapi_scope}")

        _openapi_function_sources = _append_unique_review_sources(
            _openapi_tutorial_function.get("supporting_sources", []),
            [_openapi_tutorial_function["source_span"]]
            if _openapi_tutorial_function.get("source_span")
            else [],
        )
        _openapi_function_mapping = {
            key: value
            for key, value in _openapi_tutorial_function.items()
            if key
            not in {
                "mapping_status",
                "feature_status",
                "openapi_observation_scope",
                "source_span",
                "workflow_cases",
            }
        }
        _openapi_function_mapping["review_status"] = "reviewed_partial"
        _openapi_function_mapping["supporting_sources"] = _openapi_function_sources
        _openapi_function_mapping["stimulus_notes"] = "; ".join(
            filter(
                None,
                [
                    _openapi_tutorial_function.get("stimulus_notes", ""),
                    "; ".join(_openapi_function_notes),
                ],
            )
        )
        _openapi_function_mapping["workflow_cases"] = _openapi_tutorial_function.get(
            "workflow_cases", []
        )
        _openapi_tutorial_functions[_openapi_tutorial_name] = _openapi_function_mapping

    _openapi_module_status_notes = [
        f"{feature_id}: {review.get('status')} — {review.get('scope')}"
        for feature_id, review in _openapi_tutorial_module.get("feature_status", {}).items()
    ]
    _openapi_tutorial_review_mappings[_openapi_tutorial_path] = {
        "rationale": _openapi_tutorial_module["rationale"],
        "supporting_sources": _openapi_tutorial_module.get("supporting_sources", []),
        "module_observation_selectors": _openapi_tutorial_module.get(
            "module_observation_selectors", []
        ),
        "stimulus_notes": "; ".join(_openapi_module_status_notes),
        "functions": _openapi_tutorial_functions,
    }

merge_test_review_mappings(
    _normalize_source_review_workflow_mappings(_openapi_tutorial_review_mappings)
)

from atlas_openapi_response_tutorial_source_review_mappings import (  # noqa: E402
    OPENAPI_RESPONSE_TUTORIAL_SOURCE_REVIEW,
)

_openapi_response_tutorial_modules = {}
for (
    _openapi_response_tutorial_path,
    _openapi_response_tutorial_functions,
) in OPENAPI_RESPONSE_TUTORIAL_SOURCE_REVIEW["modules"].items():
    _openapi_response_tutorial_selectors = sorted(
        {
            selector
            for function_review in _openapi_response_tutorial_functions.values()
            for selector in function_review["observation_selectors"]
        }
    )
    _openapi_response_tutorial_modules[_openapi_response_tutorial_path] = {
        "rationale": (
            "Source-reviewed schema-example and direct-response tutorial functions; "
            "the linked inputs select only the recorded response or OpenAPI observations."
        ),
        "module_observation_selectors": _openapi_response_tutorial_selectors,
        "functions": _openapi_response_tutorial_functions,
    }

merge_test_review_mappings(
    _normalize_source_review_workflow_mappings(_openapi_response_tutorial_modules)
)

import atlas_dependency_lifecycle_security_review_mappings as dependency_lifecycle_review  # noqa: E402

_dependency_lifecycle_limits_note = "; ".join(
    [
        "Python source baseline >= "
        + dependency_lifecycle_review.REVIEW_LIMITS["python"]["minimum"],
        "generic TestClient behavior is owned by Starlette 1.6.0; FastAPI's lock resolves Starlette 1.3.1 and does not establish HTTPX pairing for the selected contract",
        "Pydantic behavior is pinned to "
        + dependency_lifecycle_review.REVIEW_LIMITS["pydantic"]["version"],
    ]
)
_dependency_lifecycle_review_mappings = {
    test_path: {
        **module_review,
        "stimulus_notes": "; ".join(
            filter(
                None, [module_review.get("stimulus_notes", ""), _dependency_lifecycle_limits_note]
            )
        ),
    }
    for test_path, module_review in dependency_lifecycle_review.DEPENDENCY_LIFECYCLE_SECURITY_REVIEW_MAPPINGS.items()
}
merge_test_review_mappings(
    _normalize_source_review_workflow_mappings(_dependency_lifecycle_review_mappings)
)

# Tutorial-page curation is reviewed independently from the reference-page
# mappings above. Its Starlette ownership spans are resolved against the pinned
# Starlette 1.6.0 checkout during atlas generation.
from atlas_tutorial_doc_review_mappings import (  # noqa: E402
    DOC_EXCLUSION_OVERRIDES as TUTORIAL_DOC_EXCLUSION_OVERRIDES,
)
from atlas_tutorial_doc_review_mappings import (  # noqa: E402
    DOC_PAGE_REVIEW_MAPPINGS as TUTORIAL_DOC_PAGE_REVIEW_MAPPINGS,
)

DOC_PAGE_REVIEW_MAPPINGS.update(TUTORIAL_DOC_PAGE_REVIEW_MAPPINGS)
DOC_EXCLUSION_OVERRIDES.update(TUTORIAL_DOC_EXCLUSION_OVERRIDES)

# Selected advanced and how-to pages reuse already-indexed workflow cases.
from atlas_advanced_howto_wave_mappings import (  # noqa: E402
    DOC_PAGE_REVIEW_MAPPINGS as ADVANCED_HOWTO_DOC_PAGE_REVIEW_MAPPINGS,
)

DOC_PAGE_REVIEW_MAPPINGS.update(ADVANCED_HOWTO_DOC_PAGE_REVIEW_MAPPINGS)

# Remaining docs pages were reviewed independently. Feature pages link to
# existing input cases; explicit exclusions retain exact page source spans.
import atlas_remaining_docs_wave_mappings as remaining_docs_wave  # noqa: E402

DOC_PAGE_REVIEW_MAPPINGS.update(remaining_docs_wave.DOC_PAGE_REVIEW_MAPPINGS)
for doc_path, exclusion in remaining_docs_wave.DOC_PAGE_EXCLUSION_MAPPINGS.items():
    reason = exclusion["exclusion_reason"]
    DOC_EXCLUSION_OVERRIDES[doc_path] = reason
    DOC_PAGE_REVIEW_MAPPINGS[doc_path] = {
        "rationale": reason,
        "replace_features": True,
        "feature_ids": [],
        "exclusion_reason": reason,
        "supporting_sources": exclusion["supporting_sources"],
    }

from atlas_documentation_example_review_mappings import (  # noqa: E402
    DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS,
)

# The final pending test-source wave is reviewed in independent sidecars. Keep
# each function mapping and its scoped exclusions in the merged fixture atlas.
from atlas_pending_source_wave_a_mappings import (  # noqa: E402
    FASTAPI_SOURCE_WAVE_A_TEST_REVIEW_MAPPINGS,
)
from atlas_pending_source_wave_review_mappings import (  # noqa: E402
    PENDING_SOURCE_WAVE_REVIEW_MAPPINGS,
)
from atlas_source_wave_b_review_mappings import (  # noqa: E402
    SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS,
)

for _pending_test_wave in (
    FASTAPI_SOURCE_WAVE_A_TEST_REVIEW_MAPPINGS,
    SOURCE_WAVE_B_TEST_REVIEW_MAPPINGS,
    PENDING_SOURCE_WAVE_REVIEW_MAPPINGS,
):
    merge_test_review_mappings(_normalize_source_review_workflow_mappings(_pending_test_wave))

FEATURES = [
    {
        "id": "app-routing",
        "terms": (
            "apirouter",
            "router",
            "mount",
            "frontend",
            "path operation",
            "path_operation",
            "url_path_for",
            "redirect_slash",
            "include_router(",
            "api_route(",
            "add_api_route(",
            "@app.get(",
            "@app.post(",
            "route order",
        ),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "openapi.paths",
        ],
        "starlette_areas": [
            "routing-converters-mounts-hosts-and-errors",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Construct an app or router through the public FastAPI API, register the feature's route configuration, and make the documented request or route inspection.",
    },
    {
        "id": "root-path",
        "terms": ("root_path", "root path", "root-path", "behind a proxy"),
        "observations": [
            "http.status",
            "http.body.bytes",
            "route.match",
            "openapi.document",
        ],
        "starlette_areas": [
            "routing-converters-mounts-hosts-and-errors",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Set or send an ASGI root_path, invoke the route, and inspect FastAPI's scope or OpenAPI server projection.",
    },
    {
        "id": "request-validation",
        "terms": (
            "query parameter",
            "path parameter",
            "header parameter",
            "cookie parameter",
            "request body",
            "form field",
            "file upload",
            "validation",
            "annotated",
            "query(",
            "path(",
            "header(",
            "cookie(",
            "body(",
            "form(",
            "file(",
            "uploadfile",
            "strict content type",
            "strict_content_type",
            "request files",
            "request forms",
            "pydantic",
        ),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "http.body.json",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
        ],
        "starlette_areas": [
            "applications-requests-responses-background-concurrency",
            "streaming-headers-cookies-errors-and-cleanup",
            "middleware-authentication-endpoints-datastructures-status",
        ],
        "stimulus": "Build a fresh app and endpoint with the documented parameter/model declarations, then submit representative valid and invalid HTTP inputs.",
    },
    {
        "id": "request-body",
        "terms": ("request-body", "request body", "requestbody", "body field"),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "http.body.json",
            "validation.error_class",
            "validation.error_details",
            "openapi.request_schema",
        ],
        "starlette_areas": [
            "applications-requests-responses-background-concurrency",
            "streaming-headers-cookies-errors-and-cleanup",
        ],
        "stimulus": "Declare body parameters and media types, submit independent request bodies, and inspect validation or OpenAPI projections.",
    },
    {
        "id": "dependency-security",
        "terms": (
            "depends(",
            "security(",
            "dependency",
            "dependencies",
            "oauth2",
            "security scope",
            "dependency override",
            "yield dependency",
            "dependency cache",
            "api key",
        ),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "http.body.json",
            "dependency.call_order",
            "dependency.cleanup_order",
            "openapi.security",
        ],
        "starlette_areas": [
            "middleware-authentication-endpoints-datastructures-status",
            "asgi-http-websocket-lifespan",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Declare the dependency/security graph and credential inputs, invoke the public endpoint, and observe response, call order, cleanup, and schema effects.",
    },
    {
        "id": "dependency-overrides",
        "terms": ("dependency override", "dependency overrides", "dependency_overrides"),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "http.body.json",
            "dependency.call_order",
        ],
        "starlette_areas": [
            "middleware-authentication-endpoints-datastructures-status",
            "asgi-http-websocket-lifespan",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Register a dependency override, call its dependent route with independent inputs, and observe the override's public response effects.",
    },
    {
        "id": "response-serialization",
        "terms": (
            "response_model",
            "response model",
            "response serialization",
            "jsonresponse",
            "streamingresponse",
            "eventsource",
            "background task",
            "set-cookie",
            "responsevalidationerror",
        ),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.cookies",
            "http.body.bytes",
            "http.body.json",
            "response.background_effects",
            "validation.error_class",
        ],
        "starlette_areas": [
            "applications-requests-responses-background-concurrency",
            "streaming-headers-cookies-errors-and-cleanup",
        ],
        "stimulus": "Register an endpoint with the documented response type, status, header/cookie, filtering, or streaming configuration and invoke it with input-only data.",
    },
    {
        "id": "status-codes",
        "terms": ("status_code", "status code", "status codes", "additional status"),
        "observations": ["http.status", "http.body.bytes", "http.body.json", "openapi.paths"],
        "starlette_areas": [
            "applications-requests-responses-background-concurrency",
            "middleware-authentication-endpoints-datastructures-status",
        ],
        "stimulus": "Set a route's configured status and exercise it with an independent request while observing the response and documented operation status.",
    },
    {
        "id": "python-data-encoding",
        "terms": ("jsonable_encoder", "jsonable encoder"),
        "observations": ["python.attribute_value", "python.signature"],
        "starlette_areas": [],
        "stimulus": "Call the documented FastAPI encoder with representative Python/Pydantic values and options, then observe its public return value and callable signature.",
    },
    {
        "id": "openapi-docs",
        "terms": (
            "openapi",
            "swagger",
            "redoc",
            "docs_url",
            "openapi_url",
            "callback",
            "webhook",
            "operation id",
            "operation_id",
        ),
        "observations": [
            "openapi.document",
            "docs.response.status",
            "docs.response.headers",
            "docs.response.body.bytes",
            "http.body.bytes",
        ],
        "starlette_areas": [
            "applications-requests-responses-background-concurrency",
            "wsgi-static-files-templates-schemas-configuration-testclient",
        ],
        "stimulus": "Configure the documented app/route/schema option, then observe the public OpenAPI result or docs endpoint response.",
    },
    {
        "id": "websocket-lifecycle",
        "terms": (
            "websocket",
            "web socket",
            "lifespan",
            "startup event",
            "shutdown event",
            "on_event(",
        ),
        "observations": [
            "websocket.event_order",
            "websocket.messages",
            "websocket.close_code",
            "lifecycle.event_order",
            "lifecycle.cleanup_effects",
            "error.class",
        ],
        "starlette_areas": [
            "asgi-http-websocket-lifespan",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Create a WebSocket or lifespan workflow with ordered public actions and observe messages, close/error state, startup, shutdown, and cleanup.",
    },
    {
        "id": "asgi-error-propagation",
        "terms": ("ASGI application error", "ASGI exception propagation"),
        "observations": ["asgi.application_error.exception"],
        "starlette_areas": [
            "asgi-http-websocket-lifespan",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Trigger an application exception during ASGI dispatch and observe its qualified class, exact message, and protocol events.",
    },
    {
        "id": "middleware-integrations",
        "terms": (
            "middleware",
            "corsmiddleware",
            "gzipmiddleware",
            "trustedhostmiddleware",
            "httpsredirectmiddleware",
            "staticfiles",
            "static files",
            "jinja2templates",
            "wsgi",
            "graphql",
            "sql database",
            "settings",
            "fastapi cli",
        ),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "http.body.json",
            "process.exit_code",
            "process.stdout",
            "process.stderr",
        ],
        "starlette_areas": [
            "middleware-authentication-endpoints-datastructures-status",
            "wsgi-static-files-templates-schemas-configuration-testclient",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Enable the named optional integration or middleware, provide deterministic request/filesystem/configuration inputs, and observe its public effect.",
    },
    {
        "id": "static-files",
        "terms": ("static files", "staticfiles", "mount static"),
        "observations": [
            "http.status",
            "http.headers.ordered",
            "http.body.bytes",
            "route.match",
            "openapi.paths",
        ],
        "starlette_areas": [
            "routing-converters-mounts-hosts-and-errors",
            "applications-requests-responses-background-concurrency",
            "wsgi-static-files-templates-schemas-configuration-testclient",
        ],
        "stimulus": "Mount the documented static-file application with independent filesystem inputs, then inspect its response and parent OpenAPI boundary.",
    },
    {
        "id": "public-api-errors",
        "terms": (
            "exception handler",
            "httpexception",
            "websocketexception",
            "deprecated",
            "deprecation",
            "import path",
            "datastructure",
            "data structure",
            "param class",
        ),
        "observations": [
            "python.import_path",
            "python.object_identity",
            "python.signature",
            "python.attribute_value",
            "warnings.category_message",
            "error.class",
            "error.public_attributes",
        ],
        "starlette_areas": [
            "middleware-authentication-endpoints-datastructures-status",
            "applications-requests-responses-background-concurrency",
        ],
        "stimulus": "Import or call the named public symbol with the documented arguments, including deprecated aliases and public error construction where applicable.",
    },
]

IMPORT_RE = re.compile(
    r"(?m)^\s*from\s+(fastapi(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s+import\s+(\([^)]*\)|[^\n#]+)"
)
IMPORT_NAME_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?")


class AtlasError(RuntimeError):
    pass


def run_git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise AtlasError("git identity check failed for %s: %s" % (repo, detail.strip())) from exc
    return result.stdout.strip()


def verify_checkout(
    repo: Path, tag: str, commit: str, label: str, tracked_paths: Sequence[str]
) -> dict[str, str]:
    repo = repo.resolve()
    observed_commit = run_git(repo, "rev-parse", "HEAD")
    observed_tag = run_git(repo, "describe", "--tags", "--exact-match", "HEAD")
    tag_commit = run_git(repo, "rev-parse", "refs/tags/%s^{commit}" % tag)
    if observed_commit != commit or observed_tag != tag or tag_commit != commit:
        raise AtlasError(
            "%s source mismatch: expected %s/%s, observed %s/%s"
            % (label, tag, commit, observed_tag, observed_commit)
        )
    dirty = run_git(repo, "status", "--porcelain=v1", "--", *tracked_paths)
    if dirty:
        raise AtlasError(
            "%s source paths have local changes; atlas evidence would not match the pinned commit:\n%s"
            % (label, dirty)
        )
    return {"version": tag, "commit": commit, "working_tree": "pinned-source"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_first_asgi_workflow() -> dict[str, Any]:
    schema_path = PROJECT / ASGI_WORKFLOW_SCHEMA_PATH
    input_path = PROJECT / ASGI_WORKFLOW_INPUT_PATH
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        workflow = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read first ASGI workflow contract: %s" % exc) from exc

    schema_const = schema.get("properties", {}).get("schema", {}).get("const")
    if schema_const != ASGI_WORKFLOW_SCHEMA_ID or workflow.get("schema") != ASGI_WORKFLOW_SCHEMA_ID:
        raise AtlasError(
            "first ASGI workflow schema/input do not identify %s" % ASGI_WORKFLOW_SCHEMA_ID
        )
    if schema.get("additionalProperties") is not False or not workflow.get("cases"):
        raise AtlasError("first ASGI workflow requires a strict schema and at least one input case")

    case_ids = [case.get("case_id") for case in workflow["cases"]]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids) or len(
        case_ids
    ) != len(set(case_ids)):
        raise AtlasError("first ASGI workflow case IDs must be non-empty and unique")
    forbidden_keys = {
        "expected",
        "expected_output",
        "expected_outputs",
        "expected_body",
        "expected_error",
        "result",
        "oracle_observation",
    }

    def reject_expected_values(value: Any) -> None:
        if isinstance(value, dict):
            forbidden = forbidden_keys.intersection(value)
            if forbidden:
                raise AtlasError(
                    "first ASGI workflow contains forbidden result field(s): %s"
                    % ", ".join(sorted(forbidden))
                )
            for child in value.values():
                reject_expected_values(child)
        elif isinstance(value, list):
            for child in value:
                reject_expected_values(child)

    reject_expected_values(workflow)
    workload_path = workflow.get("workload", {}).get("file")
    if not isinstance(workload_path, str) or not (PROJECT / workload_path).is_file():
        raise AtlasError("first ASGI workflow workload file is missing")

    return {
        "schema": ASGI_WORKFLOW_SCHEMA_ID,
        "schema_id": schema.get("$id"),
        "schema_path": ASGI_WORKFLOW_SCHEMA_PATH.as_posix(),
        "schema_sha256": sha256(schema_path),
        "input_path": ASGI_WORKFLOW_INPUT_PATH.as_posix(),
        "input_sha256": sha256(input_path),
        "case_ids": case_ids,
        "expected_outputs": "absent",
        "workload": {
            "path": workload_path,
            "factory": workflow["workload"].get("factory"),
            "sha256": sha256(PROJECT / workload_path),
        },
        "state": "input-only ten-case recipe and workload, public pass-through facade, Rust first-slice implementation, identity-checked source/target runners, and exact comparator are present; broader operation-level coverage remains pending",
    }


def norm_id(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "unnamed"


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def markdown_import_evidence(path: Path, root: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    evidence = []
    for match in IMPORT_RE.finditer(text):
        module = match.group(1)
        names = match.group(2).strip().strip("()")
        for item in IMPORT_NAME_RE.finditer(names):
            name = item.group(1)
            alias = item.group(2)
            evidence.append(
                {
                    "candidate_id": module + "." + (alias or name),
                    "kind": "documented_import",
                    "path": relative(path, root),
                    "line": text.count("\n", 0, match.start()) + 1,
                }
            )
    return evidence


def markdown_member_evidence(path: Path, root: Path) -> list[dict[str, Any]]:
    """Read explicit mkdocstrings member allowlists as public API evidence."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    records = []
    for index, line in enumerate(lines):
        directive = re.match(r"^\s*:::\s+(fastapi(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*$", line)
        if not directive:
            continue
        target = directive.group(1)
        member_indent = None
        for member_index in range(index + 1, len(lines)):
            candidate = lines[member_index]
            if candidate.lstrip().startswith(":::"):
                break
            if not candidate.strip():
                continue
            indent = len(candidate) - len(candidate.lstrip())
            if member_indent is not None and indent <= member_indent:
                break
            if re.match(r"^\s*members:\s*$", candidate):
                member_indent = indent
                continue
            if member_indent is not None and candidate.strip().startswith("-"):
                name = candidate.strip()[1:].strip()
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                    records.append(
                        {
                            "target": target,
                            "member": name,
                            "path": relative(path, root),
                            "line": member_index + 1,
                        }
                    )
    return records


def normalized_words(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def feature_match_evidence(path_text: str, content: str) -> list[dict[str, Any]]:
    """Return exact whole-token feature signals; never infer a default family."""
    normalized_path = normalized_words(path_text)
    lines = content.splitlines()
    normalized_lines = [
        (line_number, normalized_words(line)) for line_number, line in enumerate(lines, 1)
    ]
    evidence = []
    for feature in FEATURES:
        signals = []
        for term in feature["terms"]:
            needle = normalized_words(term)
            if not needle:
                continue
            if re.search(r"(?:^| )" + re.escape(needle) + r"(?: |$)", normalized_path):
                signals.append({"term": term, "source": "path"})
                continue
            for line_number, normalized_line in normalized_lines:
                if re.search(r"(?:^| )" + re.escape(needle) + r"(?: |$)", normalized_line):
                    signals.append({"term": term, "source": "content", "line": line_number})
                    break
        if signals:
            evidence.append({"feature_id": feature["id"], "signals": signals})
    return evidence


def feature_matches(path_text: str, content: str) -> list[str]:
    return [item["feature_id"] for item in feature_match_evidence(path_text, content)]


def test_function_evidence(content: str, module_path: str = "") -> list[dict[str, Any]]:
    """Index test function identity/line and feature signals without copying code."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    functions = []
    # A filename may supply a candidate family when the test is terse, but
    # unrelated imports/routes elsewhere in a large module must not be copied
    # onto each function as if that function exercised them.
    module_evidence = feature_match_evidence(module_path, "") if module_path else []

    def visit(body: Sequence[ast.stmt], scope: Sequence[str] = ()) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                visit(node.body, [*scope, node.name])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified_name = ".".join([*scope, node.name])
                if node.name == "test" or node.name.startswith("test_"):
                    snippet = ast.get_source_segment(content, node) or ""
                    matches = feature_match_evidence(qualified_name, snippet)
                    mapping_scope = "test_function_source" if matches else None
                    if not matches and module_evidence:
                        matches = module_evidence
                        mapping_scope = "module_path_candidate"
                    functions.append(
                        {
                            "name": node.name,
                            "qualified_name": qualified_name,
                            "line": node.lineno,
                            "end_line": getattr(node, "end_lineno", node.lineno),
                            "feature_evidence": matches,
                            "feature_ids": [item["feature_id"] for item in matches],
                            "mapping_scope": mapping_scope if matches else None,
                            "mapping_status": "candidate" if matches else "review_required",
                        }
                    )
                # Nested functions inside fixtures/tests are not collected as
                # pytest tests. Visit class bodies, but do not descend through
                # function bodies (which previously treated endpoint helpers
                # and local context-manager checks as independent tests).

    visit(tree.body)
    return sorted(functions, key=lambda item: (item["line"], item["name"]))


def selectors_with_exact_http_body(selectors: Sequence[str]) -> list[str]:
    """Retain raw response bytes whenever a fixture also selects parsed JSON."""
    result = list(dict.fromkeys(selectors))
    if "http.body.json" in result and "http.body.bytes" not in result:
        json_index = result.index("http.body.json")
        result.insert(json_index, "http.body.bytes")
    return result


def selector_evidence(
    features: Sequence[str], selectors: Sequence[str] | None = None
) -> list[dict[str, Any]]:
    by_id = {feature["id"]: feature for feature in FEATURES}
    if selectors is None:
        return [
            {"feature_id": feature_id, "selectors": by_id[feature_id]["observations"]}
            for feature_id in features
        ]

    namespace_owners = {
        "asgi": ("asgi-error-propagation",),
        "dependency": ("dependency-security",),
        "docs": ("openapi-docs",),
        "error": ("public-api-errors", "websocket-lifecycle"),
        "http": (
            "response-serialization",
            "request-validation",
            "app-routing",
            "middleware-integrations",
        ),
        "lifecycle": ("websocket-lifecycle",),
        "middleware": ("middleware-integrations",),
        "openapi": ("openapi-docs", "request-validation", "app-routing"),
        "process": ("middleware-integrations",),
        "python": ("public-api-errors", "python-data-encoding"),
        "response": ("response-serialization",),
        "security": ("dependency-security",),
        "validation": ("request-validation",),
        "websocket": ("websocket-lifecycle",),
    }
    assigned: dict[str, list[str]] = defaultdict(list)
    extension: dict[str, list[str]] = defaultdict(list)
    unassigned: list[str] = []
    for selector in selectors_with_exact_http_body(selectors):
        exact_owners = [
            feature_id for feature_id in features if selector in by_id[feature_id]["observations"]
        ]
        if exact_owners:
            for feature_id in exact_owners:
                assigned[feature_id].append(selector)
            continue
        namespace = selector.split(".", 1)[0]
        owner = next(
            (
                feature_id
                for feature_id in namespace_owners.get(namespace, ())
                if feature_id in features
            ),
            None,
        )
        if owner:
            assigned[owner].append(selector)
            extension[owner].append(selector)
        else:
            unassigned.append(selector)

    result = []
    for feature_id in features:
        if not assigned[feature_id]:
            continue
        record = {"feature_id": feature_id, "selectors": assigned[feature_id]}
        if extension[feature_id]:
            record["schema_extension_required"] = extension[feature_id]
        result.append(record)
    if unassigned:
        result.append(
            {
                "feature_id": None,
                "selectors": unassigned,
                "schema_extension_required": unassigned,
            }
        )
    return result


def merge_selector_evidence(
    evidence_groups: Sequence[Sequence[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Merge page-level feature/selector links without reassigning selectors."""
    selectors_by_feature: dict[str | None, set[str]] = defaultdict(set)
    extensions_by_feature: dict[str | None, set[str]] = defaultdict(set)
    for evidence_group in evidence_groups:
        for evidence in evidence_group:
            feature_id = evidence["feature_id"]
            selectors_by_feature[feature_id].update(evidence["selectors"])
            extensions_by_feature[feature_id].update(evidence.get("schema_extension_required", []))

    merged = []
    for feature_id in sorted(selectors_by_feature, key=lambda value: (value is None, value or "")):
        evidence = {
            "feature_id": feature_id,
            "selectors": sorted(selectors_by_feature[feature_id]),
        }
        if extensions_by_feature[feature_id]:
            evidence["schema_extension_required"] = sorted(extensions_by_feature[feature_id])
        merged.append(evidence)
    return merged


def selectors_for(features: Sequence[str]) -> list[str]:
    by_id = {feature["id"]: feature for feature in FEATURES}
    return selectors_with_exact_http_body(
        sorted(
            {selector for feature_id in features for selector in by_id[feature_id]["observations"]}
        )
    )


def starlette_areas_for(features: Sequence[str]) -> list[str]:
    by_id = {feature["id"]: feature for feature in FEATURES}
    return sorted(
        {area for feature_id in features for area in by_id[feature_id]["starlette_areas"]}
    )


def stimulus_for(features: Sequence[str]) -> list[str]:
    by_id = {feature["id"]: feature for feature in FEATURES}
    return [by_id[feature_id]["stimulus"] for feature_id in features]


def docs_exclusion(path: str) -> str | None:
    lower = path.lower()
    if path in DOC_EXCLUSION_OVERRIDES:
        return DOC_EXCLUSION_OVERRIDES[path]
    if lower.endswith("_llm-test.md"):
        return "Repository meta-test page, not a user-facing FastAPI feature."
    if lower.startswith(("about/", "learn/", "resources/")):
        return (
            "Orientation/community/resource content has no independent FastAPI runtime observation."
        )
    if lower.startswith("deployment/") and not any(
        x in lower for x in ("behind-a-proxy", "server-workers")
    ):
        return "Deployment-provider or deployment-process guidance is outside the FastAPI library API contract."
    if path in {
        "advanced/index.md",
        "tutorial/index.md",
        "reference/index.md",
        "how-to/index.md",
        "index.md",
    }:
        return "Section landing/navigation page; independently observable features are mapped to their linked reference pages and examples."
    return None


def reviewed_source_spans(
    root: Path,
    spans: Sequence[dict[str, Any]],
    starlette_root: Path | None = None,
) -> list[dict[str, Any]]:
    records = []
    for item in spans:
        source_root = root
        source_authority = None
        if item["path"].startswith("starlette/") and starlette_root is not None:
            source_root = starlette_root
            source_authority = "Starlette " + STARLETTE_VERSION
        path = source_root / item["path"]
        if not path.is_file():
            raise AtlasError("reviewed source evidence is missing: " + item["path"])
        line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        start = int(item["start_line"])
        end = int(item["end_line"])
        if start < 1 or end < start or end > line_count:
            raise AtlasError(
                "reviewed source evidence has an invalid line span: %s:%d-%d"
                % (item["path"], start, end)
            )
        record = {
            "path": item["path"],
            "sha256": sha256(path),
            "start_line": start,
            "end_line": end,
            "role": item["role"],
        }
        if source_authority:
            record["source_authority"] = source_authority
        records.append(record)
    return records


def find_doc_pages_for_example(
    example: Path, docs_root: Path, fastapi_root: Path, source_links: dict[str, set[str]]
) -> list[str]:
    relpath = relative(example, fastapi_root)
    if relpath in source_links:
        return sorted(source_links[relpath])
    variants = []
    if "_an_py310.py" in relpath:
        variants.append(relpath.replace("_an_py310.py", "_py310.py"))
    elif "_py310.py" in relpath:
        variants.append(relpath.replace("_py310.py", "_an_py310.py"))
    elif "_an_py310/" in relpath:
        variants.append(relpath.replace("_an_py310/", "_py310/"))
    elif "_py310/" in relpath:
        variants.append(relpath.replace("_py310/", "_an_py310/"))
    for variant in variants:
        if variant in source_links:
            return sorted(source_links[variant])
        # Some tested variants live beside docs-included examples under a
        # second app directory; map by the directory's documentation include.
        variant_path = fastapi_root / variant
        if variant_path.exists():
            parent = variant_path.parent
            matches = set()
            for candidate in parent.rglob("*.py"):
                matches.update(source_links.get(relative(candidate, fastapi_root), set()))
            if matches:
                return sorted(matches)
    # docs_src mirrors most, but not all, documentation section paths.
    rel = example.relative_to(fastapi_root / "docs_src")
    dirs = list(rel.parts[:-1])
    candidates = []
    for depth in range(len(dirs), 0, -1):
        candidates.append("/".join(part.replace("_", "-") for part in dirs[:depth]) + ".md")
    for candidate in candidates:
        if (docs_root / candidate).exists():
            return [candidate]
    leaf = dirs[-1].replace("_", "-") if dirs else ""
    matches = (
        sorted(p.relative_to(docs_root).as_posix() for p in docs_root.rglob(leaf + ".md"))
        if leaf
        else []
    )
    return matches if matches else []


def read_python_support(pyproject: Path, workflow: Path) -> dict[str, Any]:
    text = pyproject.read_text(encoding="utf-8")
    requirement = re.search(r'(?m)^requires-python\s*=\s*"([^"]+)"', text)
    classifiers = sorted(set(re.findall(r'"Programming Language :: Python :: (3\.\d+)"', text)))
    ci_text = workflow.read_text(encoding="utf-8")
    ci_versions = sorted(set(re.findall(r'python-version:\s*["\']?(3\.\d+)(?:t)?["\']?', ci_text)))
    python_pin = workflow.parents[2] / ".python-version"
    return {
        "requires_python": requirement.group(1) if requirement else "unresolved",
        "project_classifiers": classifiers,
        "test_workflow_versions": ci_versions,
        "test_workflow_free_threaded": "3.14t" in ci_text,
        "source_python_version_pin": python_pin.read_text(encoding="utf-8").strip()
        if python_pin.exists()
        else None,
        "source_refs": [
            "pyproject.toml:[project].requires-python",
            ".github/workflows/test.yml:python-version matrix",
        ],
        "legacy_named_test_note": "test_typing_python39.py is a typing compatibility case; it does not override requires-python >=3.10.",
    }


def parse_extras(pyproject: Path) -> list[dict[str, Any]]:
    text = pyproject.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^\[project\.optional-dependencies\]\s*\n(.*?)(?=^\[|\Z)", text)
    if not match:
        return []
    rows = []
    for entry in re.finditer(r"(?ms)^([A-Za-z0-9_-]+)\s*=\s*\[(.*?)^\]", match.group(1)):
        packages = re.findall(r"\"([^\"]+)\"", entry.group(2))
        rows.append(
            {
                "extra": entry.group(1),
                "requirements": packages,
                "source": "pyproject.toml:[project.optional-dependencies]",
            }
        )
    return rows


def source_ref_lookup(starlette_source: Path, symbol: str) -> dict[str, Any]:
    parts = symbol.split(".")
    if not parts or parts[0] != "starlette":
        return {"symbol": symbol, "status": "unresolved-non-starlette"}
    tail = parts[1:]
    if not tail:
        return {"symbol": symbol, "path": "starlette/__init__.py", "status": "package-namespace"}
    name = tail[-1]
    module_parts = tail[:-1]
    if name == "status" and not module_parts:
        module_parts = ["status"]
        name = ""
    if not module_parts or module_parts[-1] != name and len(tail) == 1:
        module_parts = tail
        name = ""
    path = starlette_source / "starlette" / ("/".join(module_parts) + ".py")
    if (
        not path.exists()
        and (starlette_source / "starlette" / "/".join(module_parts) / "__init__.py").exists()
    ):
        path = starlette_source / "starlette" / "/".join(module_parts) / "__init__.py"
    ref: dict[str, Any] = {
        "symbol": symbol,
        "path": path.relative_to(starlette_source).as_posix() if path.exists() else None,
    }
    if not path.exists():
        ref["status"] = "source-path-unresolved"
        return ref
    if not name:
        ref["status"] = "module-surface"
        return ref
    pattern = re.compile(
        r"^\s*(?:async\s+)?(?:def|class)\s+"
        + re.escape(name)
        + r"\b|^\s*"
        + re.escape(name)
        + r"\s*=",
        re.M,
    )
    text = path.read_text(encoding="utf-8", errors="replace")
    match = pattern.search(text)
    if match:
        ref.update(
            {"line": text.count("\n", 0, match.start()) + 1, "status": "source-definition-located"}
        )
    else:
        ref["status"] = "imported-or-runtime-symbol"
    return ref


def starlette_area_for_symbol(
    symbol: str, areas: set[str], source_ref: dict[str, Any] | None = None
) -> list[str]:
    # A module import (for example `import starlette.routing`) has no leaf
    # symbol. Use its full path instead of treating its parent as the module.
    module = (
        symbol
        if source_ref and source_ref.get("status") == "module-surface"
        else symbol.rpartition(".")[0]
    )
    applications = "applications-requests-responses-background-concurrency"
    middleware = "middleware-authentication-endpoints-datastructures-status"
    routing = "routing-converters-mounts-hosts-and-errors"
    streaming = "streaming-headers-cookies-errors-and-cleanup"
    asgi = "asgi-http-websocket-lifespan"
    wsgi = "wsgi-static-files-templates-schemas-configuration-testclient"

    if module == "starlette.middleware.wsgi":
        candidates = [middleware, wsgi]
    elif module.startswith("starlette.middleware") or module in {
        "starlette.authentication",
        "starlette.endpoints",
        "starlette.status",
        "starlette.datastructures",
    }:
        candidates = [middleware]
    elif module in {"starlette.routing", "starlette.convertors", "starlette.schemas"}:
        candidates = [routing]
    elif module in {"starlette.websockets", "starlette.types"}:
        candidates = [asgi]
    elif module in {
        "starlette.staticfiles",
        "starlette.templating",
        "starlette.testclient",
        "starlette.config",
        "starlette.wsgi",
    }:
        candidates = [wsgi]
    elif module == "starlette.exceptions":
        candidates = [middleware, routing, streaming]
    elif module == "starlette._exception_handler":
        candidates = [middleware, applications, streaming]
    elif module == "starlette._utils":
        if symbol.endswith(".get_route_path"):
            candidates = [routing]
        else:
            candidates = [applications]
    elif module == "starlette.formparsers":
        candidates = [applications, streaming]
    elif module in {
        "starlette.requests",
        "starlette.responses",
        "starlette.background",
        "starlette.concurrency",
        "starlette.applications",
    }:
        candidates = [applications]
        if module in {
            "starlette.requests",
            "starlette.responses",
            "starlette.background",
            "starlette.concurrency",
        }:
            candidates.append(streaming)
    else:
        candidates = []
    return [item for item in candidates if item in areas]


def classify_candidate(
    candidate: dict[str, Any], explicit_public: bool, supported_parent: bool
) -> tuple[str, str]:
    if explicit_public or supported_parent:
        return (
            "supported",
            "Explicit root export/import, documented target or module declaration, explicit member allowlist, or field of a documented OpenAPI model.",
        )
    if candidate.get("visibility", "").startswith("private"):
        return (
            "private/internal",
            "Pinned source marks the declaration private or protocol-internal.",
        )
    symbol = candidate.get("id", "")
    if any(
        part.startswith("_") and not (part.startswith("__") and part.endswith("__"))
        for part in symbol.split(".")
    ):
        return "private/internal", "The source module or member is explicitly underscore-private."
    if candidate.get("kind") == "import_binding":
        if (candidate.get("imported_module") or "").startswith("_"):
            return (
                "private/internal",
                "The binding imports an underscore-private dependency module.",
            )
        return "uncertain", "Importability from this module is not by itself public API evidence."
    return (
        "uncertain",
        "Public-looking source declaration lacks explicit root-export or documentation evidence.",
    )


def _review_evidence_path(value: str) -> tuple[str, int | None, int | None]:
    line_match = re.fullmatch(r"(.+):(\d+)(?:-(\d+))?", value)
    if line_match:
        start = int(line_match.group(2))
        return line_match.group(1), start, int(line_match.group(3) or start)
    return value, None, None


def load_callable_classification_review(
    path: Path,
    *,
    fastapi_root: Path,
    fastapi_identity: dict[str, Any],
) -> dict[str, Any]:
    """Load and source-check the manual review of uncertain public callables."""
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read API callable classification review: " + str(exc)) from exc
    if (
        not isinstance(review, dict)
        or review.get("schema") != CALLABLE_CLASSIFICATION_REVIEW_SCHEMA
    ):
        raise AtlasError("API callable classification review has an unsupported schema")
    expected_identity = {
        "package": "FastAPI",
        "version": FASTAPI_VERSION,
        "source_commit": fastapi_identity["commit"],
        "selected_starlette_profile": STARLETTE_VERSION,
    }
    if review.get("source_identity") != expected_identity:
        raise AtlasError("API callable classification review has the wrong source identity")
    rows = review.get("rows")
    if not isinstance(rows, list) or not rows:
        raise AtlasError("API callable classification review has no rows")
    identifiers = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(identifiers) != len(rows) or len(identifiers) != len(set(identifiers)):
        raise AtlasError("API callable classification review IDs must be unique")
    counts = Counter()
    for row in rows:
        identifier = row.get("id")
        recommendation = row.get("recommendation")
        source = row.get("source")
        evidence_basis = row.get("evidence_basis")
        evidence = row.get("evidence")
        reason = row.get("reason")
        if (
            not isinstance(identifier, str)
            or recommendation not in {"supported", "private/internal", "uncertain"}
            or not isinstance(source, dict)
            or not isinstance(source.get("path"), str)
            or not isinstance(source.get("line"), int)
            or not isinstance(evidence_basis, list)
            or not isinstance(evidence, list)
            or not evidence
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise AtlasError(
                "API callable classification review row is malformed: " + str(identifier)
            )
        source_path = (fastapi_root / source["path"]).resolve()
        try:
            source_path.relative_to(fastapi_root.resolve())
        except ValueError as exc:
            raise AtlasError("API callable review source escapes FastAPI: " + identifier) from exc
        if not source_path.is_file():
            raise AtlasError("API callable review source is missing: " + source["path"])
        source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not 1 <= source["line"] <= len(source_lines):
            raise AtlasError("API callable review source line is out of range: " + identifier)
        strong_public_basis = {
            "documented",
            "release-note",
            "explicit-deprecation/source-contract",
            "explicit-source-contract",
        }
        if recommendation == "supported" and not (strong_public_basis & set(evidence_basis)):
            raise AtlasError(
                "supported callable review lacks public-contract evidence: " + identifier
            )
        for reference in evidence:
            if not isinstance(reference, str) or not reference:
                raise AtlasError("API callable review has malformed evidence: " + identifier)
            evidence_path, line_start, line_end = _review_evidence_path(reference)
            evidence_file = (fastapi_root / evidence_path).resolve()
            try:
                evidence_file.relative_to(fastapi_root.resolve())
            except ValueError as exc:
                raise AtlasError(
                    "API callable review evidence escapes FastAPI: " + reference
                ) from exc
            if not evidence_file.is_file():
                raise AtlasError("API callable review evidence is missing: " + reference)
            if line_start is not None:
                line_count = len(
                    evidence_file.read_text(encoding="utf-8", errors="replace").splitlines()
                )
                if not 1 <= line_start <= line_end <= line_count:
                    raise AtlasError(
                        "API callable review evidence line is out of range: " + reference
                    )
        counts[recommendation] += 1
    scope = review.get("scope", {})
    if scope.get("candidate_count") != len(rows) or scope.get("recommendation_counts") != dict(
        counts
    ):
        raise AtlasError("API callable review summary does not match its rows")
    return review


def load_source_api_classification_review(
    path: Path,
    *,
    fastapi_root: Path,
    fastapi_identity: dict[str, Any],
    selection: dict[str, list[str]],
) -> dict[str, Any]:
    """Load a pinned-source review for the selected non-callable/API-name slice."""
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read source API classification review: " + str(exc)) from exc
    expected_identity = {
        "package": "FastAPI",
        "version": FASTAPI_VERSION,
        "source_commit": fastapi_identity["commit"],
    }
    try:
        validate_source_api_review_schema(
            review,
            expected_identity=expected_identity,
            expected_selection=selection,
        )
    except SourceApiReviewSchemaError as exc:
        raise AtlasError(str(exc)) from exc
    scope = review.get("scope")
    rows = review.get("rows")
    identifiers = [row.get("id") for row in rows if isinstance(row, dict)]
    expected_ids_digest = hashlib.sha256(
        ("\n".join(sorted(identifiers)) + "\n").encode()
    ).hexdigest()
    if scope.get("candidate_ids_sha256") != expected_ids_digest:
        raise AtlasError(
            "source API classification review candidate summary does not match its rows"
        )

    counts: Counter[str] = Counter()
    root = fastapi_root.resolve()
    for row in rows:
        identifier = row.get("id")
        recommendation = row.get("recommendation")
        candidate_kind = row.get("candidate_kind")
        source = row.get("source")
        binding = row.get("binding")
        evidence_basis = row.get("evidence_basis")
        evidence = row.get("evidence")
        reason = row.get("reason")
        if (
            not isinstance(identifier, str)
            or recommendation not in {"supported", "private/internal", "uncertain"}
            or not isinstance(candidate_kind, str)
            or not isinstance(source, dict)
            or not isinstance(source.get("path"), str)
            or not isinstance(source.get("line"), int)
            or isinstance(source.get("line"), bool)
            or not isinstance(evidence_basis, list)
            or not evidence_basis
            or any(not isinstance(value, str) or not value for value in evidence_basis)
            or not isinstance(evidence, list)
            or not evidence
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise AtlasError(
                "source API classification review row is malformed: " + str(identifier)
            )
        if candidate_kind == "import_binding":
            if not isinstance(binding, dict) or not all(
                isinstance(binding.get(key), str) for key in ("module", "name", "target")
            ):
                raise AtlasError("source API import review lacks binding identity: " + identifier)
        elif binding is not None:
            raise AtlasError("non-import source API review row has binding identity: " + identifier)

        source_path = (root / source["path"]).resolve()
        try:
            source_path.relative_to(root)
        except ValueError as exc:
            raise AtlasError("source API review source escapes FastAPI: " + identifier) from exc
        if not source_path.is_file():
            raise AtlasError("source API review source is missing: " + source["path"])
        source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not 1 <= source["line"] <= len(source_lines):
            raise AtlasError("source API review source line is out of range: " + identifier)

        evidence_roles: set[str] = set()
        has_public_docs = False
        for reference in evidence:
            if (
                not isinstance(reference, dict)
                or not isinstance(reference.get("path"), str)
                or not isinstance(reference.get("line"), int)
                or isinstance(reference.get("line"), bool)
                or not isinstance(reference.get("role"), str)
                or not reference["role"]
            ):
                raise AtlasError("source API review evidence is malformed: " + identifier)
            end_line = reference.get("end_line", reference["line"])
            if not isinstance(end_line, int) or isinstance(end_line, bool):
                raise AtlasError("source API review evidence range is malformed: " + identifier)
            evidence_path = (root / reference["path"]).resolve()
            try:
                evidence_path.relative_to(root)
            except ValueError as exc:
                raise AtlasError(
                    "source API review evidence escapes FastAPI: " + identifier
                ) from exc
            if not evidence_path.is_file():
                raise AtlasError("source API review evidence is missing: " + reference["path"])
            evidence_lines = evidence_path.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
            if not 1 <= reference["line"] <= end_line <= len(evidence_lines):
                raise AtlasError("source API review evidence line is out of range: " + identifier)
            evidence_roles.add(reference["role"])
            has_public_docs |= reference["path"].startswith("docs/en/docs/")

        if recommendation == "supported" and (
            "documented" not in evidence_basis or not has_public_docs
        ):
            raise AtlasError(
                "supported source API review lacks documentation evidence: " + identifier
            )
        if recommendation == "private/internal" and (
            "implementation-only" not in evidence_basis
            or "fastapi-implementation-use" not in evidence_roles
        ):
            raise AtlasError(
                "internal source API review lacks implementation evidence: " + identifier
            )
        counts[recommendation] += 1

    if scope.get("recommendation_counts") != dict(counts):
        raise AtlasError("source API classification review recommendation counts are stale")
    return review


def load_public_candidate_classification_review(
    path: Path,
    *,
    fastapi_root: Path,
    fastapi_identity: dict[str, Any],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Load the exact source-backed review of public-looking non-callable candidates."""
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read public candidate classification review: " + str(exc)) from exc
    expected_identity = {
        "package": "FastAPI",
        "version": FASTAPI_VERSION,
        "source_commit": fastapi_identity["commit"],
    }
    try:
        validate_public_candidate_review_schema(review, expected_identity=expected_identity)
    except PublicCandidateReviewSchemaError as exc:
        raise AtlasError(str(exc)) from exc
    if metadata.get("schema") != review["schema"]:
        raise AtlasError("metadata.yaml public candidate review schema is stale")
    if metadata.get("artifact") != path.resolve().relative_to(PROJECT).as_posix():
        raise AtlasError("metadata.yaml public candidate review path is stale")
    if metadata.get("source_identity") != expected_identity:
        raise AtlasError("metadata.yaml public candidate review identity is stale")
    if metadata.get("sha256") != sha256(path.resolve()):
        raise AtlasError("metadata.yaml public candidate review digest is stale")
    scope = review["scope"]
    recommendations = Counter(row["recommendation"] for row in review["rows"])
    expected_counts = {
        "candidates": len(review["rows"]),
        "supported": recommendations.get("supported", 0),
        "private_or_internal": recommendations.get("private/internal", 0),
        "uncertain": recommendations.get("uncertain", 0),
    }
    if metadata.get("counts") != expected_counts:
        raise AtlasError("metadata.yaml public candidate review counts are stale")
    if metadata.get("candidate_ids_sha256") != scope["candidate_ids_sha256"]:
        raise AtlasError("metadata.yaml public candidate review ID digest is stale")

    root = fastapi_root.resolve()
    for row in review["rows"]:
        references = [row["source"], *row["evidence"]]
        for reference in references:
            evidence_path = (root / reference["path"]).resolve()
            try:
                evidence_path.relative_to(root)
            except ValueError as exc:
                raise AtlasError(
                    "public candidate review evidence escapes FastAPI: " + row["id"]
                ) from exc
            if not evidence_path.is_file():
                raise AtlasError("public candidate review source is missing: " + reference["path"])
            source_lines = evidence_path.read_text(encoding="utf-8", errors="replace").splitlines()
            end_line = reference.get("end_line", reference["line"])
            if not 1 <= reference["line"] <= end_line <= len(source_lines):
                raise AtlasError(
                    "public candidate review source line is out of range: " + row["id"]
                )
    return review


def apply_public_candidate_classification_review(
    candidates: dict[str, dict[str, Any]], review: dict[str, Any]
) -> None:
    """Apply the exact source review for uncertain, public-looking source candidates."""
    review_kinds = {"class", "field", "import_binding", "value"}
    expected = {
        identifier
        for identifier, candidate in candidates.items()
        if candidate.get("classification") == "uncertain"
        and candidate.get("visibility") in {"public", "public_candidate"}
        and candidate.get("kind") in review_kinds
        and "classification_review" not in candidate
    }
    rows = {row["id"]: row for row in review["rows"]}
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise AtlasError(
            "public candidate review does not match its uncertain source candidate denominator; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    for identifier, row in rows.items():
        candidate = candidates[identifier]
        source = row["source"]
        if row["candidate_kind"] != candidate.get("kind"):
            raise AtlasError("public candidate review kind differs from inventory: " + identifier)
        if not any(
            reference.get("path") == source["path"]
            and reference.get("line", 0)
            <= source["line"]
            <= reference.get("end_line", reference.get("line", 0))
            for reference in candidate.get("source_evidence", [])
        ):
            raise AtlasError("public candidate review source differs from inventory: " + identifier)
        binding = row.get("binding")
        if binding is not None and (
            candidate.get("kind") != "import_binding"
            or binding.get("module") != candidate.get("imported_module")
            or binding.get("name") != candidate.get("imported_name")
            or binding.get("target") != candidate.get("target_path")
        ):
            raise AtlasError(
                "public candidate review binding differs from inventory: " + identifier
            )

        candidate["classification"] = row["recommendation"]
        candidate["classification_evidence_rule"] = (
            "Reviewed pinned FastAPI source/docs evidence; this source classification makes no "
            "FastAPI-RS support or parity claim."
        )
        candidate["classification_review"] = {
            "review_artifact": "api_public_candidate_classification_review",
            "source": source,
            "candidate_kind": row["candidate_kind"],
            "binding": binding,
            "evidence_basis": row["evidence_basis"],
            "evidence": row["evidence"],
            "reason": row["reason"],
        }
        if row["recommendation"] == "supported":
            for reference in row["evidence"]:
                if reference["role"] == "fastapi-public-documentation" and reference[
                    "path"
                ].startswith("docs/en/docs/"):
                    public_ref: dict[str, Any] = {
                        "kind": "reviewed_public_candidate_documentation_contract",
                        "path": reference["path"],
                        "line": reference["line"],
                    }
                    if reference.get("end_line", reference["line"]) != reference["line"]:
                        public_ref["end_line"] = reference["end_line"]
                    candidate["public_evidence"].append(public_ref)


def _pinned_review_source_text(
    source: str,
    path_text: str,
    *,
    fastapi_root: Path,
    starlette_root: Path,
    starlette_rs_root: Path,
    starlette_rs_commit: str,
) -> str:
    if source == "starlette_rs":
        path = Path(path_text)
        if path.is_absolute() or ".." in path.parts:
            raise AtlasError("Starlette-RS review evidence path is not repository-relative")
        try:
            return subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(starlette_rs_root),
                    "show",
                    f"{starlette_rs_commit}:{path.as_posix()}",
                ],
                text=True,
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = (
                exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
            )
            raise AtlasError("cannot read pinned Starlette-RS review evidence: " + detail) from exc
    roots = {"fastapi": fastapi_root, "starlette": starlette_root}
    if source not in roots:
        raise AtlasError("import-binding review evidence names an unknown source: " + source)
    root = roots[source].resolve()
    evidence_path = (root / path_text).resolve()
    try:
        evidence_path.relative_to(root)
    except ValueError as exc:
        raise AtlasError("import-binding review evidence escapes its source checkout") from exc
    if not evidence_path.is_file():
        raise AtlasError("import-binding review evidence is missing: " + path_text)
    return evidence_path.read_text(encoding="utf-8", errors="replace")


def load_import_binding_classification_review(
    path: Path,
    *,
    fastapi_root: Path,
    starlette_root: Path,
    starlette_rs_root: Path,
    fastapi_identity: dict[str, Any],
    starlette_identity: dict[str, Any],
    starlette_rs_commit: str,
) -> dict[str, Any]:
    """Load source evidence for a partial, exact Starlette-origin binding review."""
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError(
            "cannot read API import-binding classification review: " + str(exc)
        ) from exc
    if (
        not isinstance(review, dict)
        or review.get("schema") != IMPORT_BINDING_CLASSIFICATION_REVIEW_SCHEMA
    ):
        raise AtlasError("API import-binding classification review has an unsupported schema")
    expected_identity = {
        "package": "FastAPI",
        "version": FASTAPI_VERSION,
        "source_commit": fastapi_identity["commit"],
        "selected_starlette_profile": STARLETTE_VERSION,
        "starlette_source_commit": starlette_identity["commit"],
        "starlette_rs_contract_commit": starlette_rs_commit,
    }
    if review.get("source_identity") != expected_identity:
        raise AtlasError("API import-binding review has the wrong source identity")
    # Validate that the immutable sibling commit object exists even if the
    # caller's working tree has local changes. The main atlas path separately
    # requires its selected Starlette-RS checkout to match the pinned revision.
    if (
        run_git(starlette_rs_root, "rev-parse", "--verify", f"{starlette_rs_commit}^{{commit}}")
        != starlette_rs_commit
    ):
        raise AtlasError("API import-binding review Starlette-RS commit is unavailable")

    pinned_sources = review.get("pinned_starlette_rs_sources")
    expected_source_paths = {
        "metadata": "metadata.yaml",
        "manifest": "tests/fixtures/manifest.yaml",
        "api_catalog": "docs/api-surface.csv",
        "api_review": "docs/atlas/api-review.csv",
    }
    if not isinstance(pinned_sources, dict) or set(pinned_sources.get("files", {})) != set(
        expected_source_paths
    ):
        raise AtlasError("API import-binding review lacks its pinned Starlette-RS source set")
    pinned_text: dict[str, str] = {}
    for role, expected_path in expected_source_paths.items():
        reference = pinned_sources["files"].get(role)
        if (
            not isinstance(reference, dict)
            or reference.get("path") != expected_path
            or not isinstance(reference.get("git_blob"), str)
            or not isinstance(reference.get("sha256"), str)
        ):
            raise AtlasError("API import-binding review has malformed Starlette-RS source identity")
        actual_blob = run_git(
            starlette_rs_root, "rev-parse", f"{starlette_rs_commit}:{expected_path}"
        )
        try:
            source_bytes = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(starlette_rs_root),
                    "show",
                    f"{starlette_rs_commit}:{expected_path}",
                ],
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = (
                exc.stderr.decode("utf-8", errors="replace").strip()
                if isinstance(exc, subprocess.CalledProcessError)
                else str(exc)
            )
            raise AtlasError("cannot read pinned Starlette-RS source identity: " + detail) from exc
        if (
            reference["git_blob"] != actual_blob
            or reference["sha256"] != hashlib.sha256(source_bytes).hexdigest()
        ):
            raise AtlasError("pinned Starlette-RS source digest differs from the review: " + role)
        pinned_text[role] = source_bytes.decode("utf-8", errors="replace")
    try:
        pinned_metadata = yaml.safe_load(pinned_text["metadata"])
        pinned_manifest = json.loads(pinned_text["manifest"])
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise AtlasError("pinned Starlette-RS identity artifacts are malformed") from exc
    if (
        pinned_metadata.get("authority", {}).get("revision") != STARLETTE_COMMIT
        or pinned_manifest.get("scope", {}).get("inventory", {}).get("revision") != STARLETTE_COMMIT
        or not any(
            oracle.get("id") == "starlette-python" and oracle.get("version") == STARLETTE_VERSION
            for oracle in pinned_manifest.get("oracles", [])
        )
    ):
        raise AtlasError("pinned Starlette-RS sources select the wrong Starlette profile")
    sibling_contract_id = pinned_manifest.get("scope", {}).get("id")
    if pinned_sources.get("contract_id") != sibling_contract_id:
        raise AtlasError("API import-binding review has the wrong Starlette-RS contract id")

    evidence_text_cache: dict[tuple[str, str], str] = {}
    sibling_review_text = pinned_text["api_review"]
    sibling_review_rows_by_line: dict[int, dict[str, str]] = {}
    sibling_review_reader = csv.DictReader(io.StringIO(sibling_review_text, newline=""))
    for sibling_row in sibling_review_reader:
        sibling_review_rows_by_line[sibling_review_reader.line_num] = sibling_row

    rows = review.get("rows")
    if not isinstance(rows, list) or not rows:
        raise AtlasError("API import-binding review has no rows")
    identifiers = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(identifiers) != len(rows) or len(identifiers) != len(set(identifiers)):
        raise AtlasError("API import-binding review IDs must be unique")
    counts: Counter[str] = Counter()
    for row in rows:
        identifier = row.get("id")
        recommendation = row.get("recommendation")
        source = row.get("source")
        evidence_basis = row.get("evidence_basis")
        evidence = row.get("evidence")
        reason = row.get("reason")
        binding = row.get("binding")
        sibling_review = row.get("starlette_rs_review")
        if (
            not isinstance(identifier, str)
            or recommendation not in {"supported", "private/internal", "uncertain"}
            or not isinstance(source, dict)
            or not isinstance(source.get("path"), str)
            or not isinstance(source.get("line"), int)
            or isinstance(source.get("line"), bool)
            or not isinstance(binding, dict)
            or not all(isinstance(binding.get(key), str) for key in ("module", "name", "target"))
            or not isinstance(evidence_basis, list)
            or not evidence_basis
            or any(not isinstance(value, str) or not value for value in evidence_basis)
            or not isinstance(evidence, list)
            or not evidence
            or not isinstance(reason, str)
            or not reason.strip()
            or not isinstance(sibling_review, dict)
            or sibling_review.get("state") not in {"reviewed", "no_exact_row"}
        ):
            raise AtlasError("API import-binding review row is malformed: " + str(identifier))

        fastapi_source = (fastapi_root / source["path"]).resolve()
        try:
            fastapi_source.relative_to(fastapi_root.resolve())
        except ValueError as exc:
            raise AtlasError(
                "API import-binding review source escapes FastAPI: " + identifier
            ) from exc
        if not fastapi_source.is_file():
            raise AtlasError("API import-binding review source is missing: " + source["path"])
        fastapi_lines = fastapi_source.read_text(encoding="utf-8", errors="replace").splitlines()
        if not 1 <= source["line"] <= len(fastapi_lines):
            raise AtlasError("API import-binding review source line is out of range: " + identifier)

        evidence_roles: set[str] = set()
        has_public_doc_evidence = False
        exact_starlette_review: dict[str, str] | None = None
        for reference in evidence:
            if (
                not isinstance(reference, dict)
                or reference.get("source") not in {"fastapi", "starlette", "starlette_rs"}
                or not isinstance(reference.get("path"), str)
                or not isinstance(reference.get("line"), int)
                or isinstance(reference.get("line"), bool)
                or not isinstance(reference.get("role"), str)
                or not reference["role"]
            ):
                raise AtlasError("API import-binding review has malformed evidence: " + identifier)
            end_line = reference.get("end_line", reference["line"])
            if not isinstance(end_line, int) or isinstance(end_line, bool):
                raise AtlasError(
                    "API import-binding review has malformed evidence range: " + identifier
                )
            evidence_key = (reference["source"], reference["path"])
            if evidence_key not in evidence_text_cache:
                evidence_text_cache[evidence_key] = _pinned_review_source_text(
                    reference["source"],
                    reference["path"],
                    fastapi_root=fastapi_root,
                    starlette_root=starlette_root,
                    starlette_rs_root=starlette_rs_root,
                    starlette_rs_commit=starlette_rs_commit,
                )
            evidence_text = evidence_text_cache[evidence_key]
            evidence_lines = evidence_text.splitlines()
            if not 1 <= reference["line"] <= end_line <= len(evidence_lines):
                raise AtlasError(
                    "API import-binding review evidence line is out of range: " + identifier
                )
            evidence_roles.add(reference["role"])
            if reference["source"] == "fastapi" and reference["path"].startswith("docs/"):
                has_public_doc_evidence = True
            if (
                reference["source"] == "starlette_rs"
                and reference["path"] == "docs/atlas/api-review.csv"
            ):
                csv_row = sibling_review_rows_by_line.get(reference["line"])
                if csv_row is None:
                    raise AtlasError("pinned Starlette-RS API review line is not a data row")
                if csv_row.get("qualified_name") != binding["target"]:
                    raise AtlasError(
                        "Starlette-RS evidence target differs from FastAPI binding: " + identifier
                    )
                exact_starlette_review = csv_row
        if "fastapi-binding" not in evidence_roles or "starlette-target" not in evidence_roles:
            raise AtlasError(
                "API import-binding review lacks both binding and target evidence: " + identifier
            )
        strong_public_basis = {"release-note", "documented", "explicit-deprecation/source-contract"}
        if recommendation == "supported" and (
            not (strong_public_basis & set(evidence_basis)) or not has_public_doc_evidence
        ):
            raise AtlasError(
                "supported import-binding review lacks FastAPI public-contract evidence: "
                + identifier
            )
        if (
            recommendation == "private/internal"
            and "fastapi-implementation-use" not in evidence_roles
        ):
            raise AtlasError(
                "internal import-binding review lacks FastAPI implementation-use evidence: "
                + identifier
            )

        if sibling_review["state"] == "reviewed":
            if (
                exact_starlette_review is None
                or sibling_review.get("qualified_name") != binding["target"]
                or sibling_review.get("disposition")
                != exact_starlette_review.get("api_disposition")
                or sibling_review.get("catalog_row") != exact_starlette_review.get("catalog_row")
            ):
                raise AtlasError(
                    "Starlette-RS review record differs from pinned source: " + identifier
                )
        elif exact_starlette_review is not None or sibling_review.get("disposition") is not None:
            raise AtlasError(
                "Starlette-RS no-row limitation conflicts with pinned source: " + identifier
            )

        counts[recommendation] += 1
    scope = review.get("scope", {})
    reviewed_candidate_count = sum(
        row.get("starlette_rs_review", {}).get("state") == "reviewed" for row in rows
    )
    unreviewed_targets = {
        row.get("binding", {}).get("target")
        for row in rows
        if row.get("starlette_rs_review", {}).get("state") == "no_exact_row"
    }
    if (
        scope.get("candidate_count") != len(rows)
        or scope.get("recommendation_counts") != dict(counts)
        or scope.get("starlette_rs_reviewed_candidate_count") != reviewed_candidate_count
        or scope.get("starlette_rs_unreviewed_unique_target_count") != len(unreviewed_targets)
    ):
        raise AtlasError("API import-binding review summary does not match its rows")
    return review


def apply_callable_classification_review(
    candidates: dict[str, dict[str, Any]], review: dict[str, Any]
) -> None:
    """Apply reviewed classifications to the exact uncertain callable subset."""
    expected = {
        identifier
        for identifier, candidate in candidates.items()
        if candidate.get("classification") == "uncertain"
        and candidate.get("visibility") in {"public", "public_protocol"}
        and candidate.get("kind") in REVIEWED_CALLABLE_KINDS
    }
    rows = {row["id"]: row for row in review["rows"]}
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise AtlasError(
            "API callable review does not match the uncertain callable denominator; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    for identifier, row in rows.items():
        candidate = candidates[identifier]
        source = row["source"]
        if not any(
            reference.get("path") == source["path"] and reference.get("line") == source["line"]
            for reference in candidate.get("source_evidence", [])
        ):
            raise AtlasError(
                "API callable review source location differs from inventory: " + identifier
            )
        candidate["classification"] = row["recommendation"]
        candidate["classification_evidence_rule"] = (
            "Reviewed pinned-source/docs/test evidence; tests establish exercised behavior, "
            "while public documentation, release notes, or explicit deprecation evidence "
            "establish lifecycle and exposure."
        )
        candidate["classification_review"] = {
            "source": source,
            "evidence_basis": row["evidence_basis"],
            "evidence": row["evidence"],
            "reason": row["reason"],
        }
        if row["recommendation"] == "supported":
            for reference in row["evidence"]:
                evidence_path, line, end_line = _review_evidence_path(reference)
                if evidence_path.startswith("docs/en/docs/"):
                    public_ref: dict[str, Any] = {
                        "kind": "reviewed_documentation_contract",
                        "path": evidence_path,
                    }
                    if line is not None:
                        public_ref["line"] = line
                        if end_line != line:
                            public_ref["end_line"] = end_line
                    candidate["public_evidence"].append(public_ref)
            if "explicit-deprecation/source-contract" in row["evidence_basis"]:
                candidate["public_evidence"].append(
                    {
                        "kind": "reviewed_source_deprecation_contract",
                        "path": source["path"],
                        "line": source["line"],
                    }
                )
            if "explicit-source-contract" in row["evidence_basis"]:
                candidate["public_evidence"].append(
                    {
                        "kind": "reviewed_source_contract",
                        "path": source["path"],
                        "line": source["line"],
                    }
                )


def apply_import_binding_classification_review(
    candidates: dict[str, dict[str, Any]], review: dict[str, Any]
) -> None:
    """Apply review rows to exactly the uncertain Starlette-origin bindings."""
    expected = {
        identifier
        for identifier, candidate in candidates.items()
        if candidate.get("classification") == "uncertain"
        and candidate.get("kind") == "import_binding"
        and (candidate.get("imported_module") or "").startswith("starlette")
    }
    rows = {row["id"]: row for row in review["rows"]}
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise AtlasError(
            "API import-binding review does not match the uncertain Starlette-origin denominator; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    for identifier, row in rows.items():
        candidate = candidates[identifier]
        source = row["source"]
        binding = row["binding"]
        if (
            binding.get("module") != candidate.get("imported_module")
            or binding.get("name") != candidate.get("imported_name")
            or binding.get("target") != candidate.get("target_path")
        ):
            raise AtlasError(
                "API import-binding review target differs from inventory: " + identifier
            )
        if not any(
            reference.get("path") == source["path"] and reference.get("line") == source["line"]
            for reference in candidate.get("source_evidence", [])
        ):
            raise AtlasError(
                "API import-binding review source location differs from inventory: " + identifier
            )
        candidate["classification"] = row["recommendation"]
        candidate["classification_evidence_rule"] = (
            "Reviewed FastAPI import-site/use evidence, pinned Starlette target source, and the "
            "pinned Starlette-RS target review where present. The sibling disposition applies to "
            "the canonical Starlette target, not automatically to this FastAPI import path."
        )
        candidate["classification_review"] = {
            "source": source,
            "binding": binding,
            "evidence_basis": row["evidence_basis"],
            "evidence": row["evidence"],
            "starlette_rs_review": row["starlette_rs_review"],
            "reason": row["reason"],
        }
        if row["recommendation"] == "supported":
            for reference in row["evidence"]:
                if reference["source"] == "fastapi" and reference["path"].startswith("docs/"):
                    public_ref: dict[str, Any] = {
                        "kind": "reviewed_import_binding_documentation_contract",
                        "path": reference["path"],
                        "line": reference["line"],
                    }
                    if reference.get("end_line", reference["line"]) != reference["line"]:
                        public_ref["end_line"] = reference["end_line"]
                    candidate["public_evidence"].append(public_ref)
            if "explicit-deprecation/source-contract" in row["evidence_basis"]:
                candidate["public_evidence"].append(
                    {
                        "kind": "reviewed_import_binding_deprecation_contract",
                        "path": source["path"],
                        "line": source["line"],
                    }
                )


def apply_source_api_classification_review(
    candidates: dict[str, dict[str, Any]],
    review: dict[str, Any],
    *,
    selection: dict[str, list[str]],
) -> None:
    """Apply reviewed source-only dispositions to the exact selected candidate slice."""
    imported_modules = set(selection["uncertain_imported_modules"])
    candidate_prefixes = tuple(selection["uncertain_candidate_id_prefixes"])
    expected = {
        identifier
        for identifier, candidate in candidates.items()
        if candidate.get("classification") == "uncertain"
        and (
            (
                candidate.get("kind") == "import_binding"
                and candidate.get("imported_module") in imported_modules
            )
            or identifier.startswith(candidate_prefixes)
        )
    }
    rows = {row["id"]: row for row in review["rows"]}
    if set(rows) != expected:
        missing = sorted(expected - set(rows))
        extra = sorted(set(rows) - expected)
        raise AtlasError(
            "source API classification review does not match its uncertain candidate denominator; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )
    for identifier, row in rows.items():
        candidate = candidates[identifier]
        source = row["source"]
        if row["candidate_kind"] != candidate.get("kind"):
            raise AtlasError(
                "source API review candidate kind differs from inventory: " + identifier
            )
        if not any(
            reference.get("path") == source["path"]
            and reference.get("line", 0)
            <= source["line"]
            <= reference.get("end_line", reference.get("line", 0))
            for reference in candidate.get("source_evidence", [])
        ):
            raise AtlasError(
                "source API review source location differs from inventory: " + identifier
            )
        binding = row.get("binding")
        if binding is not None and (
            candidate.get("kind") != "import_binding"
            or binding.get("module") != candidate.get("imported_module")
            or binding.get("name") != candidate.get("imported_name")
            or binding.get("target") != candidate.get("target_path")
        ):
            raise AtlasError("source API review binding differs from inventory: " + identifier)

        candidate["classification"] = row["recommendation"]
        candidate["classification_evidence_rule"] = (
            "Reviewed pinned FastAPI source/docs evidence; this source classification makes no "
            "FastAPI-RS support or parity claim."
        )
        candidate["classification_review"] = {
            "source": source,
            "candidate_kind": row["candidate_kind"],
            "binding": binding,
            "evidence_basis": row["evidence_basis"],
            "evidence": row["evidence"],
            "reason": row["reason"],
        }
        if row["recommendation"] == "supported":
            for reference in row["evidence"]:
                if reference["role"] == "fastapi-public-documentation" and reference[
                    "path"
                ].startswith("docs/en/docs/"):
                    public_ref: dict[str, Any] = {
                        "kind": "reviewed_source_api_documentation_contract",
                        "path": reference["path"],
                        "line": reference["line"],
                    }
                    if reference.get("end_line", reference["line"]) != reference["line"]:
                        public_ref["end_line"] = reference["end_line"]
                    candidate["public_evidence"].append(public_ref)


def generate(args: argparse.Namespace) -> dict[str, Any]:
    first_slice_workflow = read_first_asgi_workflow()
    fastapi_root = args.fastapi_source.resolve()
    starlette_root = args.starlette_source.resolve()
    starlette_rs_root = args.starlette_rs_root.resolve()
    project_metadata = yaml.safe_load((PROJECT / "metadata.yaml").read_text(encoding="utf-8"))
    starlette_rs_revision = project_metadata["starlette_rs"]["commit"]
    source_api_meta = project_metadata["source_api_classification_review"]
    public_candidate_meta = project_metadata["api_public_candidate_classification_review"]
    try:
        source_api_selection = validate_source_api_selection(source_api_meta["selection"])
    except (KeyError, SourceApiReviewSchemaError) as exc:
        raise AtlasError(f"metadata.yaml source API selection is invalid: {exc}") from exc
    try:
        actual_starlette_rs_revision = subprocess.check_output(
            ["git", "-C", str(starlette_rs_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
        starlette_rs_worktree_changes = subprocess.check_output(
            ["git", "-C", str(starlette_rs_root), "status", "--porcelain"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise AtlasError(f"cannot identify the pinned Starlette-RS checkout: {detail}") from exc
    if actual_starlette_rs_revision != starlette_rs_revision:
        raise AtlasError(
            "Starlette-RS checkout does not match metadata.yaml commit "
            f"{starlette_rs_revision}: {actual_starlette_rs_revision}"
        )
    starlette_rs_revision_state = (
        "pinned, clean Starlette-RS checkout"
        if not starlette_rs_worktree_changes
        else "pinned Starlette-RS checkout with local changes; artifact digests identify inspected contract files"
    )
    fastapi_identity = verify_checkout(
        fastapi_root,
        FASTAPI_VERSION,
        FASTAPI_COMMIT,
        "FastAPI",
        ["fastapi", "docs", "docs_src", "tests", "pyproject.toml", "uv.lock"],
    )
    starlette_identity = verify_checkout(
        starlette_root,
        STARLETTE_VERSION,
        STARLETTE_COMMIT,
        "Starlette",
        ["starlette", "docs", "tests", "pyproject.toml", "uv.lock"],
    )
    callable_review = load_callable_classification_review(
        args.callable_review,
        fastapi_root=fastapi_root,
        fastapi_identity=fastapi_identity,
    )
    starlette_rs_metadata = project_metadata["starlette_rs"]
    import_binding_review = load_import_binding_classification_review(
        args.import_binding_review,
        fastapi_root=fastapi_root,
        starlette_root=starlette_root,
        starlette_rs_root=starlette_rs_root,
        fastapi_identity=fastapi_identity,
        starlette_identity=starlette_identity,
        starlette_rs_commit=starlette_rs_revision,
    )
    source_api_review = load_source_api_classification_review(
        args.source_api_review,
        fastapi_root=fastapi_root,
        fastapi_identity=fastapi_identity,
        selection=source_api_selection,
    )
    public_candidate_review = load_public_candidate_classification_review(
        args.public_candidate_review,
        fastapi_root=fastapi_root,
        fastapi_identity=fastapi_identity,
        metadata=public_candidate_meta,
    )

    def starlette_rs_artifact_path(path_text: str) -> Path:
        owner_path = Path(starlette_rs_metadata["owner"])
        artifact_path = Path(path_text)
        try:
            relative_path = artifact_path.relative_to(owner_path)
        except ValueError:
            return (PROJECT / artifact_path).resolve()
        return (starlette_rs_root / relative_path).resolve()

    starlette_rs_manifest_path = starlette_rs_artifact_path(starlette_rs_metadata["manifest"])
    if not starlette_rs_manifest_path.is_file():
        raise AtlasError("Starlette-RS manifest not found: " + starlette_rs_metadata["manifest"])
    starlette_rs_manifest_text = starlette_rs_manifest_path.read_text(encoding="utf-8")
    try:
        starlette_rs_manifest = json.loads(starlette_rs_manifest_text)
    except json.JSONDecodeError:
        starlette_rs_manifest = None
    if starlette_rs_manifest is not None:
        manifest_revision = (
            starlette_rs_manifest.get("scope", {}).get("inventory", {}).get("revision")
        )
        oracle_pins = [
            oracle
            for oracle in starlette_rs_manifest.get("oracles", [])
            if oracle.get("id") == "starlette-python"
            or oracle.get("name", "").lower() == "starlette"
        ]
        if manifest_revision != STARLETTE_COMMIT or not any(
            oracle.get("version") == STARLETTE_VERSION for oracle in oracle_pins
        ):
            raise AtlasError(
                "Starlette-RS manifest does not identify the selected Starlette 1.6.0 source pin"
            )
        starlette_rs_contract_id = starlette_rs_manifest.get("scope", {}).get("id")
        starlette_rs_target_statuses = sorted(
            {
                support["support"].get("status")
                for surface in starlette_rs_manifest.get("surfaces", [])
                for operation in surface.get("operations", [])
                for support in operation.get("targets", [])
                if isinstance(support.get("support"), dict) and support["support"].get("status")
            }
        )
    else:
        # Older Starlette-RS manifests used YAML. Keep a narrow fallback for
        # the same version and source-revision evidence, without relying on its
        # former coverage_areas layout.
        has_version = re.search(
            r'(?m)^\s*(?:version|"version"):\s*"?1\.6\.0"?\s*,?\s*$', starlette_rs_manifest_text
        )
        if not has_version or STARLETTE_COMMIT not in starlette_rs_manifest_text:
            raise AtlasError(
                "Starlette-RS manifest does not identify the selected Starlette 1.6.0 source pin"
            )
        starlette_rs_contract_id = None
        starlette_rs_target_statuses = []
    # These stable names group FastAPI's Starlette dependency edges. They are
    # FastAPI-RS crosswalk categories, not implementation coverage claimed by
    # the current Starlette-RS slice manifest.
    starlette_areas = set(STARLETTE_RS_AREAS)
    starlette_rs_operations = {
        (surface.get("id"), operation.get("id")): (surface, operation)
        for surface in (starlette_rs_manifest or {}).get("surfaces", [])
        for operation in surface.get("operations", [])
    }
    starlette_surface_catalog_path = starlette_rs_artifact_path(
        starlette_rs_metadata["api_catalog"]
    )
    starlette_review_path = starlette_rs_artifact_path(starlette_rs_metadata["api_review"])
    starlette_coverage_matrix_path = starlette_rs_artifact_path(
        starlette_rs_metadata["coverage_matrix"]
    )
    if not starlette_surface_catalog_path.exists() or not starlette_review_path.exists():
        raise AtlasError("Starlette-RS merged API catalog or review is missing")
    starlette_review_records: dict[str, list[dict[str, str]]] = defaultdict(list)
    with starlette_review_path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            starlette_review_records[row.get("qualified_name", "")].append(row)

    inventory_path = args.inventory.resolve()
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if (
        inventory["source_identity"].get("commit") != FASTAPI_COMMIT
        or inventory["source_identity"].get("tag") != FASTAPI_VERSION
    ):
        raise AtlasError("API inventory does not match the pinned FastAPI source")
    inventory_sha = sha256(inventory_path)
    module_hashes = {module["id"]: module["sha256"] for module in inventory["modules"]}
    module_doc_path = {
        module["id"]: module["source_ref"]["path"] for module in inventory["modules"]
    }
    doc_import_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    doc_member_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    docs_root = fastapi_root / "docs/en/docs"
    docs_src = fastapi_root / "docs_src"
    doc_source_links: dict[str, set[str]] = defaultdict(set)
    for source_root in (docs_root, docs_src):
        for path in sorted(source_root.rglob("*.md" if source_root == docs_root else "*.py")):
            if path.name == "__init__.py":
                continue
            for record in markdown_import_evidence(path, fastapi_root):
                doc_import_evidence[record["candidate_id"]].append(record)
            if source_root == docs_root:
                for record in markdown_member_evidence(path, fastapi_root):
                    doc_member_evidence[record["target"]].append(record)
    for page in sorted(docs_root.rglob("*.md")):
        page_rel = relative(page, docs_root)
        page_text = page.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"docs_src/([A-Za-z0-9_./-]+\.py)", page_text):
            doc_source_links["docs_src/" + match.group(1)].add(page_rel)
    for item in inventory["documented_targets"]:
        for ref in item.get("references", []):
            doc_import_evidence[item["id"]].append(
                {"kind": "reference_autodoc", "path": ref["path"], "line": ref["line"]}
            )

    candidates: dict[str, dict[str, Any]] = {}

    def add_candidate(record: dict[str, Any], candidate_kind: str) -> None:
        candidate_id = record["id"]
        existing = candidates.get(candidate_id)
        if existing is None:
            existing = {
                "id": candidate_id,
                "candidate_kinds": [],
                "source_evidence": [],
                "public_evidence": [],
                "visibility": record.get("visibility", "unknown"),
                "kind": record.get("kind", candidate_kind),
            }
            candidates[candidate_id] = existing
        if candidate_kind not in existing["candidate_kinds"]:
            existing["candidate_kinds"].append(candidate_kind)
        source_ref = record.get("source_ref")
        if source_ref:
            module_id = next(
                (
                    name
                    for name, source_path in module_doc_path.items()
                    if source_path == source_ref["path"]
                ),
                None,
            )
            source_record = {
                "path": source_ref["path"],
                "line": source_ref["line"],
                "end_line": source_ref.get("end_line"),
            }
            if module_id in module_hashes:
                source_record["module_sha256"] = module_hashes[module_id]
            if source_record not in existing["source_evidence"]:
                existing["source_evidence"].append(source_record)
        if candidate_kind == "import_binding":
            for key in (
                "module",
                "local_name",
                "imported_name",
                "imported_module",
                "target_path",
                "alias_spelling",
                "identity_alias",
                "root_export",
                "starlette_delegation",
            ):
                if key in record:
                    existing[key] = record[key]

    for module in inventory["modules"]:
        for definition in module["definitions"]:
            add_candidate(definition, "source_declaration")

            def descend(owner: dict[str, Any]) -> None:
                for member in owner.get("members", []):
                    add_candidate(member, "class_member")
                    descend(member)

            descend(definition)
    for binding in inventory["import_bindings"]:
        record = dict(binding)
        record["kind"] = "import_binding"
        record["visibility"] = (
            "public_candidate" if binding.get("reexport_candidate") else "imported_name"
        )
        add_candidate(record, "import_binding")
    for item in inventory["root_exports"]:
        if item["id"] in candidates:
            candidates[item["id"]]["public_evidence"].append(
                {
                    "kind": "root_export",
                    "path": item["source_ref"]["path"],
                    "line": item["source_ref"]["line"],
                }
            )
    for candidate_id, evidence in doc_import_evidence.items():
        if candidate_id in candidates:
            for record in evidence:
                if record not in candidates[candidate_id]["public_evidence"]:
                    candidates[candidate_id]["public_evidence"].append(record)
    for item in inventory["documented_targets"]:
        candidate_id = item["id"]
        if candidate_id in candidates:
            candidates[candidate_id]["public_evidence"].append(
                {
                    "kind": "documented_target",
                    "resolved_source_path": item.get("resolved_source_path"),
                    "references": item.get("references", []),
                }
            )
        source_id = item.get("resolved_source_path")
        if source_id in candidates:
            candidates[source_id]["public_evidence"].append(
                {
                    "kind": "documented_target_alias",
                    "documented_name": candidate_id,
                    "references": item.get("references", []),
                }
            )

    # Only explicitly allowlisted class members are public because a documented
    # parent class exists. A documented OpenAPI-model module also exposes its
    # declared types and Pydantic field names as part of their schema contract.
    documented_target_by_name = {item["id"]: item for item in inventory["documented_targets"]}
    for target_name, members in doc_member_evidence.items():
        target = documented_target_by_name.get(target_name)
        parent_id = target.get("resolved_source_path") if target else None
        if not parent_id:
            continue
        for member in members:
            candidate = candidates.get(parent_id + "." + member["member"])
            if candidate is not None and not candidate["visibility"].startswith("private"):
                candidate["public_evidence"].append(
                    {
                        "kind": "documented_member_allowlist",
                        "path": member["path"],
                        "line": member["line"],
                        "container": parent_id,
                    }
                )

    openapi_model_target = documented_target_by_name.get("fastapi.openapi.models")
    openapi_model_refs = openapi_model_target.get("references", []) if openapi_model_target else []
    openapi_model_names = set()
    for candidate in candidates.values():
        if "fastapi.openapi.models." not in candidate["id"]:
            continue
        parent, _, member_name = candidate["id"].rpartition(".")
        if (
            parent == "fastapi.openapi.models"
            and "source_declaration" in candidate["candidate_kinds"]
            and not candidate["visibility"].startswith("private")
        ):
            openapi_model_names.add(candidate["id"])
            for reference in openapi_model_refs:
                candidate["public_evidence"].append(
                    {
                        "kind": "documented_module_declaration",
                        "path": reference["path"],
                        "line": reference["line"],
                        "container": "fastapi.openapi.models",
                    }
                )
    for candidate in candidates.values():
        parent, _, member_name = candidate["id"].rpartition(".")
        if (
            parent in openapi_model_names
            and candidate["kind"] == "field"
            and member_name != "model_config"
            and not candidate["visibility"].startswith("private")
        ):
            candidate["public_evidence"].extend(
                {
                    "kind": "documented_pydantic_model_field",
                    "path": reference["path"],
                    "line": reference["line"],
                    "container": parent,
                }
                for reference in openapi_model_refs
            )

    for record in candidates.values():
        explicitly_public = bool(record["public_evidence"])
        status, evidence_rule = classify_candidate(record, explicitly_public, False)
        record["classification"] = status
        record["classification_evidence_rule"] = evidence_rule
    apply_callable_classification_review(candidates, callable_review)
    apply_import_binding_classification_review(candidates, import_binding_review)
    apply_source_api_classification_review(
        candidates, source_api_review, selection=source_api_selection
    )
    apply_public_candidate_classification_review(candidates, public_candidate_review)
    for record in candidates.values():
        record["candidate_kinds"].sort()
        record["source_evidence"].sort(key=lambda x: (x["path"], x["line"]))
        record["public_evidence"].sort(
            key=lambda x: (x.get("kind", ""), x.get("path", ""), x.get("line", 0))
        )

    starlette_catalog_path = starlette_surface_catalog_path
    catalog_records: dict[str, list[dict[str, str]]] = defaultdict(list)
    if starlette_catalog_path.exists():
        with starlette_catalog_path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                catalog_records[row.get("qualified_name", "")].append(row)

    def starlette_crosswalk_evidence(
        symbol: str,
        source_ref: dict[str, Any] | None,
        fastapi_ref: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        exact_catalog = catalog_records.get(symbol, [])
        exact_review = starlette_review_records.get(symbol, [])
        if exact_catalog or exact_review:
            return exact_catalog, [
                {
                    "review_origin": "Starlette-RS merged API review",
                    "qualified_name": item.get("qualified_name"),
                    "catalog_row": item.get("catalog_row"),
                    "api_disposition": item.get("api_disposition"),
                    "evidence_refs": item.get("evidence_refs"),
                    "rationale": item.get("rationale"),
                }
                for item in exact_review
            ]

        if source_ref and source_ref.get("status") == "module-surface":
            return [
                {
                    "record_type": "external_module_namespace_reference",
                    "module": symbol,
                    "contract_id": starlette_rs_contract_id,
                    "catalog_path": "docs/api-surface.csv",
                    "catalog_sha256": sha256(starlette_surface_catalog_path),
                    "review_path": "docs/atlas/api-review.csv",
                    "review_sha256": sha256(starlette_review_path),
                    "note": "The complete namespace inventory remains owned by Starlette-RS and is referenced by digest rather than copied into the FastAPI atlas.",
                }
            ], [
                {
                    "review_origin": "Starlette-RS merged API review",
                    "scope": "external module namespace reference",
                    "qualified_name": symbol,
                    "rationale": "FastAPI imports this Starlette module namespace. Keep its complete member inventory and dispositions in the sibling Starlette-RS contract; FastAPI-RS maps only individually consumed names as direct edges.",
                }
            ]

        module = symbol.rpartition(".")[0]
        if module.startswith("starlette._"):
            return [], [
                {
                    "review_origin": "FastAPI-RS source crosswalk classification",
                    "scope": "FastAPI dependency on a private Starlette helper",
                    "qualified_name": symbol,
                    "api_disposition": "private/internal",
                    "evidence_refs": [
                        "FastAPI " + str((fastapi_ref or {}).get("path", "source")),
                        "Starlette 1.6.0 " + str((source_ref or {}).get("path", "source")),
                    ],
                    "rationale": "FastAPI imports this helper from an underscore-private Starlette module. Preserve any observable FastAPI integration behavior through its owning public contract; do not promise this helper as Starlette-RS public API.",
                }
            ]
        return exact_catalog, []

    def starlette_contract_operation_ref(
        surface_id: str,
        operation_id: str,
        requirement_ids: Sequence[str],
        relationship: str,
    ) -> dict[str, Any]:
        operation_entry = starlette_rs_operations.get((surface_id, operation_id))
        if operation_entry is None:
            raise AtlasError(
                "FastAPI crosswalk references missing Starlette-RS operation %s::%s"
                % (surface_id, operation_id)
            )
        surface, operation = operation_entry
        available_requirements = {
            requirement.get("id") for requirement in operation.get("requirements", [])
        }
        missing = set(requirement_ids) - available_requirements
        if missing:
            raise AtlasError(
                "FastAPI crosswalk references missing Starlette-RS requirements %s::%s: %s"
                % (surface_id, operation_id, sorted(missing))
            )
        target_support = {}
        for target in operation.get("targets", []):
            support = target.get("support", {})
            if isinstance(support, dict):
                target_support[target.get("target_id", "unknown")] = {
                    "status": support.get("status", "unknown"),
                    "reason": support.get("reason"),
                    "missing_requirements": support.get("missing_requirements", []),
                }
        return {
            "contract_id": starlette_rs_contract_id,
            "surface_id": surface.get("id"),
            "operation_id": operation.get("id"),
            "source_path": operation.get("source", {}).get("path"),
            "requirement_ids": list(requirement_ids),
            "target_support": target_support,
            "relationship": relationship,
        }

    def has_middleware_registration_source(coverage_item: dict[str, Any]) -> bool:
        source_path = coverage_item.get("source_path")
        if not isinstance(source_path, str):
            return False
        relative_path = Path(source_path)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            return False
        source = (fastapi_root / relative_path).resolve()
        try:
            source.relative_to(fastapi_root.resolve())
        except ValueError:
            return False
        if not source.is_file():
            return False
        source_text = source.read_text(encoding="utf-8", errors="replace")
        return bool(
            re.search(r"\badd_middleware\s*\(", source_text)
            or re.search(r"\.\s*middleware\s*\(", source_text)
        )

    def starlette_contract_mappings_for(coverage_item: dict[str, Any]) -> list[dict[str, Any]]:
        source_path = str(coverage_item.get("source_path", "")).lower()
        mappings = []
        specifications = {
            "app-routing": (
                "shared FastAPI/Starlette dispatch boundary",
                "FastAPI owns its decorators, dependency graph, and route registration; this reference is only to the generic Starlette application/router boundary.",
                [
                    (
                        "starlette.applications.Starlette",
                        "__init__",
                        ["starlette.asgi.get-hello.application-construction"],
                    ),
                    (
                        "starlette.applications.Starlette",
                        "__call__",
                        [
                            "starlette.asgi.get-hello.dispatch",
                            "starlette.asgi.get-hello.route-miss-404",
                            "starlette.asgi.get-hello.wrong-method-405",
                        ],
                    ),
                    (
                        "starlette.applications.Starlette",
                        "request-dispatch",
                        [
                            "starlette.routing.request-scope-values",
                            "starlette.routing.items-route-miss-404",
                            "starlette.routing.items-wrong-method-405",
                        ],
                    ),
                ],
            ),
            "request-validation": (
                "composed request boundary",
                "Starlette-RS covers only generic ASGI Request/scope extraction in this slice; FastAPI parameter classification and Pydantic validation remain FastAPI-RS behavior.",
                [
                    (
                        "starlette.applications.Starlette",
                        "request-dispatch",
                        [
                            "starlette.request.path-param-int",
                            "starlette.request.query-params-getlist-scalar",
                            "starlette.request.headers-case-insensitive",
                        ],
                    ),
                ],
            ),
            "response-serialization": (
                "shared response dispatch boundary",
                "The linked operation covers generic Starlette ASGI dispatch; response-model filtering, validation, and serialization remain FastAPI-RS behavior.",
                [
                    (
                        "starlette.applications.Starlette",
                        "__call__",
                        ["starlette.asgi.get-hello.dispatch"],
                    ),
                ],
            ),
            "openapi-docs": (
                "FastAPI-owned with a generic ASGI outer boundary",
                "OpenAPI generation, schema projection, and FastAPI docs endpoints are outside the current Starlette-RS slice; only the generic Starlette ASGI dispatch envelope is referenced.",
                [
                    (
                        "starlette.applications.Starlette",
                        "__call__",
                        ["starlette.asgi.get-hello.dispatch"],
                    ),
                ],
            ),
            "public-api-errors": (
                "composed error boundary",
                "This sibling requirement covers Starlette's generic default server-error response only; FastAPI HTTP/validation exceptions and handler integration need their own FastAPI contract cases.",
                [
                    (
                        "starlette.applications.Starlette",
                        "__call__",
                        ["starlette.asgi.server-error.default-response"],
                    ),
                ],
            ),
        }
        for feature_id in coverage_item.get("feature_ids", []):
            if feature_id == "websocket-lifecycle":
                if "websocket" in source_path:
                    relation = "shared FastAPI/Starlette WebSocket dispatch boundary"
                    note = "These links cover only the sibling's declared WebSocket protocol/state/route slice; FastAPI websocket dependency and route semantics remain FastAPI-RS behavior."
                    operation_specs = [
                        (
                            "starlette.websockets.WebSocket",
                            "protocol-sequence",
                            [
                                "starlette.websocket.protocol.handshake-text-close",
                                "starlette.websocket.protocol.disconnect",
                                "starlette.websocket.protocol.invalid-transition",
                            ],
                        ),
                        (
                            "starlette.websockets.WebSocket",
                            "state-sequence",
                            [
                                "starlette.websocket.state.handshake-text-close",
                                "starlette.websocket.state.disconnect",
                                "starlette.websocket.state.invalid-transition",
                            ],
                        ),
                        (
                            "starlette.routing.WebSocketRoute",
                            "route-dispatch",
                            [
                                "starlette.routing.WebSocketRoute.route-dispatch.matched-root-path",
                                "starlette.routing.WebSocketRoute.route-dispatch.router-miss-close",
                                "starlette.routing.WebSocketRoute.route-dispatch.http-scope-404",
                            ],
                        ),
                    ]
                else:
                    relation = "shared ASGI lifespan boundary"
                    note = "These links cover generic Starlette lifespan startup/shutdown and yielded state; FastAPI registration/deprecation behavior remains FastAPI-RS behavior."
                    operation_specs = [
                        (
                            "starlette.applications.Starlette",
                            "__call__",
                            ["starlette.asgi.get-hello.lifespan"],
                        ),
                    ]
                specs = (relation, note, operation_specs)
            elif feature_id == "middleware-integrations":
                if "staticfiles" in source_path or "static-files" in source_path:
                    specs = (
                        "shared FastAPI/Starlette StaticFiles boundary",
                        "FastAPI re-exports Starlette StaticFiles and owns mount integration; Starlette-RS owns generic configuration checks. The sibling Python-package lane supports this operation while its Rust-native lane is out of scope. The linked FastAPI workflows do not exercise the missing-root, file-root, or repeated-configuration requirements, so this is an ownership and backlog link rather than parity evidence.",
                        [
                            (
                                "starlette.staticfiles.StaticFiles",
                                "configuration-check",
                                [
                                    "starlette.staticfiles.StaticFiles.configuration-check.constructor-missing-directory",
                                    "starlette.staticfiles.StaticFiles.configuration-check.lazy-missing-directory",
                                    "starlette.staticfiles.StaticFiles.configuration-check.lazy-not-directory",
                                    "starlette.staticfiles.StaticFiles.configuration-check.repeated-call-state-and-asgi-events",
                                ],
                            ),
                        ],
                    )
                elif "gzip" in source_path:
                    specs = (
                        "shared GZipMiddleware boundary",
                        "Only the separately inventoried GZipMiddleware contract is in the current sibling slice; other middleware, integrations, and CLI behavior remain outside it.",
                        [
                            (
                                "starlette.middleware.gzip.GZipMiddleware",
                                "__init__",
                                ["starlette.middleware.gzip.GZipMiddleware.construct"],
                            ),
                            (
                                "starlette.middleware.gzip.GZipMiddleware",
                                "__call__",
                                [
                                    "starlette.middleware.gzip.GZipMiddleware.gzip-final-response",
                                    "starlette.middleware.gzip.GZipMiddleware.identity-client",
                                    "starlette.middleware.gzip.GZipMiddleware.small-body-bypass",
                                    "starlette.middleware.gzip.GZipMiddleware.excluded-content-type",
                                    "starlette.middleware.gzip.GZipMiddleware.streaming-chunks",
                                    "starlette.middleware.gzip.GZipMiddleware.pathsend",
                                    "starlette.middleware.gzip.GZipMiddleware.existing-encoding-stream-bypass",
                                    "starlette.middleware.gzip.GZipMiddleware.partial-response-stream-bypass",
                                ],
                            ),
                        ],
                    )
                elif has_middleware_registration_source(coverage_item):
                    specs = (
                        "shared Starlette middleware registration boundary",
                        "The FastAPI source directly calls or documents middleware registration. Starlette-RS owns generic argument forwarding, insertion order, per-application stack caching, and the post-start error; FastAPI owns its middleware decorator, stack composition, and exception integration. The Rust-native sibling binding is currently unimplemented, so this link records ownership and a parity contract rather than support.",
                        [
                            (
                                "starlette.applications.Starlette",
                                "add_middleware",
                                [
                                    "starlette.applications.Starlette.add_middleware.positional-order-and-cache",
                                    "starlette.applications.Starlette.add_middleware.factory-keyword-arguments",
                                    "starlette.applications.Starlette.add_middleware.after-start-error",
                                    "starlette.applications.Starlette.add_middleware.per-application-stack-cache",
                                ],
                            ),
                        ],
                    )
                else:
                    specs = (
                        "Starlette-RS integration outside the current slice",
                        "The sibling manifest currently declares only GZipMiddleware from this broad integration family; this behavior has no matching current operation or requirement.",
                        [],
                    )
            elif feature_id in specifications:
                specs = specifications[feature_id]
            elif feature_id == "dependency-security":
                specs = (
                    "FastAPI-owned behavior",
                    "Dependency graph execution, security scopes, overrides, and FastAPI OpenAPI security projection are not declared by the current Starlette-RS slice.",
                    [],
                )
            elif feature_id == "python-data-encoding":
                specs = (
                    "FastAPI/Pydantic-owned behavior",
                    "FastAPI jsonable_encoder and Pydantic value conversion have no corresponding Starlette-RS operation in the current contract.",
                    [],
                )
            else:
                specs = (
                    "owner review required",
                    "No exact sibling Starlette-RS operation has been selected for this FastAPI behavior family.",
                    [],
                )
            relation, note, operation_specs = specs
            mappings.append(
                {
                    "feature_id": feature_id,
                    "ownership_boundary": relation,
                    "status": "linked-to-current-contract-slice"
                    if operation_specs
                    else "out-of-current-contract-slice",
                    "contract_id": starlette_rs_contract_id,
                    "manifest_path": "tests/fixtures/manifest.yaml",
                    "manifest_sha256": sha256(starlette_rs_manifest_path),
                    "operation_refs": [
                        starlette_contract_operation_ref(*operation_spec, relation)
                        for operation_spec in operation_specs
                    ],
                    "scope_note": note,
                }
            )
        return mappings

    starlette = inventory["delegated_scope"]["starlette"]
    starlette_edges = []
    for binding in inventory["import_bindings"]:
        if binding.get("starlette_delegation"):
            relation = binding["starlette_delegation"]
            target_symbol = binding.get("target_path") or (
                binding.get("imported_module", "") + "." + binding.get("imported_name", "")
            )
            source_ref = source_ref_lookup(starlette_root, target_symbol)
            target_catalog_evidence, target_review_evidence = starlette_crosswalk_evidence(
                target_symbol, source_ref, binding.get("source_ref")
            )
            starlette_edges.append(
                {
                    "id": "fastapi-starlette:%s:%s" % (relation, norm_id(binding["id"])),
                    "fastapi_binding": binding["id"],
                    "fastapi_source": binding["source_ref"],
                    "relation": relation,
                    "starlette_symbol": target_symbol,
                    "starlette_source": source_ref,
                    "starlette_rs_planning_areas": starlette_area_for_symbol(
                        target_symbol, starlette_areas, source_ref
                    ),
                    "starlette_rs_catalog_evidence": target_catalog_evidence,
                    "starlette_rs_review_evidence": target_review_evidence,
                    "status": "source-mapped; Starlette-RS behavior proof pending its atlas/parity run",
                }
            )
    for edge in starlette.get("base_edges", []):
        symbol = edge["base"]
        source_ref = source_ref_lookup(starlette_root, symbol)
        target_catalog_evidence, target_review_evidence = starlette_crosswalk_evidence(
            symbol, source_ref, edge.get("source_ref")
        )
        starlette_edges.append(
            {
                "id": "fastapi-starlette:subclass:%s" % norm_id(edge["class_id"]),
                "fastapi_binding": edge["class_id"],
                "fastapi_source": edge["source_ref"],
                "relation": "subclass_edge",
                "starlette_symbol": symbol,
                "starlette_source": source_ref,
                "starlette_rs_planning_areas": starlette_area_for_symbol(
                    symbol, starlette_areas, source_ref
                ),
                "starlette_rs_catalog_evidence": target_catalog_evidence,
                "starlette_rs_review_evidence": target_review_evidence,
                "status": "source-mapped; inheritance contract must be verified through FastAPI",
            }
        )
    starlette_edges.sort(key=lambda x: x["id"])

    materialized_index_path = PROJECT / "tests/fixtures/materialized-input-index.json"
    if not materialized_index_path.is_file():
        raise AtlasError("materialized input index is required to review source-to-workflow links")
    materialized_index = json.loads(materialized_index_path.read_text(encoding="utf-8"))
    indexed_workflows = {row["id"]: row for row in materialized_index["workflows"]}
    indexed_workflow_mappings_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for mapping in materialized_index["mappings"]:
        workflow = indexed_workflows.get(mapping["workflow_id"])
        if workflow is None:
            raise AtlasError(
                "materialized input mapping references unknown workflow " + mapping["workflow_id"]
            )
        indexed_workflow_mappings_by_source[mapping["source_item_id"]].append(
            {
                "workflow_id": mapping["workflow_id"],
                "recipe_path": workflow["recipe_path"],
                "case_ids": mapping["case_ids"],
                "observation_selectors": mapping["observation_selectors"],
                "coverage_status": mapping["coverage_status"],
                "coverage_scope": mapping["coverage_scope"],
            }
        )
    for workflow_mappings in indexed_workflow_mappings_by_source.values():
        workflow_mappings.sort(key=lambda row: row["workflow_id"])

    coverage_items = []
    fixture_backlog = []
    tests_root = fastapi_root / "tests"
    for path in sorted(tests_root.rglob("test_*.py")):
        rel = relative(path, fastapi_root)
        content = path.read_text(encoding="utf-8", errors="replace")
        is_benchmark = rel.startswith("tests/benchmarks/") or rel.startswith(
            "tests/memory_benchmarks/"
        )
        is_maintenance = path.stem == "test_prepare_release"
        test_functions = test_function_evidence(content, rel)
        reviewed_mapping = TEST_REVIEW_MAPPINGS.get(rel, {})
        reviewed_function_mappings = reviewed_mapping.get("functions", {})
        for test in test_functions:
            function_exclusion = TEST_FUNCTION_EXCLUSIONS.get(rel, {}).get(test["qualified_name"])
            if function_exclusion:
                exclusion_spans = reviewed_source_spans(
                    fastapi_root,
                    [
                        {
                            "path": rel,
                            "start_line": test["line"],
                            "end_line": test["end_line"],
                            "role": "upstream test function",
                        },
                        *TEST_FUNCTION_EXCLUSION_EVIDENCE.get(rel, {}).get(
                            test["qualified_name"], []
                        ),
                    ],
                    starlette_root,
                )
                test["feature_ids"] = []
                test["feature_evidence"] = []
                test["mapping_status"] = "excluded"
                test["exclusion_reason"] = function_exclusion
                test["reviewed_mapping"] = {
                    "rationale": function_exclusion,
                    "source_evidence": exclusion_spans,
                }
                continue
            function_mapping = reviewed_function_mappings.get(test["name"], {})
            mapped_features = function_mapping.get(
                "feature_ids", reviewed_mapping.get("feature_ids", [])
            )
            if not mapped_features:
                continue
            supporting = list(reviewed_mapping.get("supporting_sources", []))
            supporting.extend(function_mapping.get("supporting_sources", []))
            evidence_spans = reviewed_source_spans(
                fastapi_root,
                [
                    {
                        "path": rel,
                        "start_line": test["line"],
                        "end_line": test["end_line"],
                        "role": "upstream test function",
                    },
                    *supporting,
                ],
                starlette_root,
            )
            rationale = function_mapping.get(
                "rationale",
                reviewed_mapping.get("rationale", "Reviewed against the pinned source."),
            )
            replace_features = function_mapping.get(
                "replace_features", reviewed_mapping.get("replace_features", False)
            )
            if replace_features:
                test["feature_ids"] = sorted(set(mapped_features))
                test["feature_evidence"] = [
                    item
                    for item in test["feature_evidence"]
                    if item["feature_id"] in test["feature_ids"]
                ]
            else:
                test["feature_ids"] = sorted(set(test["feature_ids"]) | set(mapped_features))
            for feature_id in mapped_features:
                if not any(item["feature_id"] == feature_id for item in test["feature_evidence"]):
                    test["feature_evidence"].append(
                        {
                            "feature_id": feature_id,
                            "signals": [
                                {
                                    "term": "curated source review",
                                    "source": "reviewed-source-span",
                                    "path": span["path"],
                                    "line": span["start_line"],
                                    "end_line": span["end_line"],
                                }
                                for span in evidence_spans
                            ],
                        }
                    )
            test["feature_evidence"].sort(key=lambda item: item["feature_id"])
            test["mapping_status"] = (
                "contract_gated_source_candidate"
                if function_mapping.get("contract_gate", reviewed_mapping.get("contract_gate"))
                else "reviewed_source_candidate"
            )
            test["mapping_scope"] = "reviewed_source_mapping"
            reviewed_record = {"rationale": rationale, "source_evidence": evidence_spans}
            for metadata_key in ("constraints", "contract_gate", "stimulus_notes"):
                metadata = function_mapping.get(metadata_key, reviewed_mapping.get(metadata_key))
                if metadata is not None:
                    reviewed_record[metadata_key] = metadata
            test["reviewed_mapping"] = reviewed_record
            test["reviewed_observation_selectors"] = function_mapping.get("observation_selectors")
            test["reviewed_stimulus_notes"] = function_mapping.get(
                "stimulus_notes", reviewed_mapping.get("stimulus_notes")
            )
        if reviewed_mapping.get("replace_module_features"):
            allowed_features = set(reviewed_mapping.get("module_feature_ids", []))
            for test in test_functions:
                if test["mapping_status"] == "excluded":
                    continue
                impossible = set(test["feature_ids"]) - allowed_features
                if test.get("mapping_status") == "reviewed_source_candidate" and impossible:
                    raise AtlasError(
                        "reviewed function features %s are outside the curated module feature set for %s::%s"
                        % (sorted(impossible), rel, test["qualified_name"])
                    )
                test["feature_ids"] = sorted(set(test["feature_ids"]) & allowed_features)
                test["feature_evidence"] = [
                    item
                    for item in test["feature_evidence"]
                    if item["feature_id"] in test["feature_ids"]
                ]
                if not test["feature_ids"]:
                    test["mapping_status"] = "review_required"
        feature_evidence_by_id: dict[str, dict[str, Any]] = {}
        for record in feature_match_evidence(rel, "") + [
            evidence for test in test_functions for evidence in test["feature_evidence"]
        ]:
            feature_evidence_by_id.setdefault(record["feature_id"], record)
        if reviewed_mapping.get("replace_module_features"):
            module_evidence = {}
            for feature_id in reviewed_mapping.get("module_feature_ids", []):
                evidence = feature_evidence_by_id.get(feature_id)
                if evidence is None:
                    test_evidence = next(
                        (
                            item
                            for test in test_functions
                            for item in test["feature_evidence"]
                            if item["feature_id"] == feature_id
                        ),
                        None,
                    )
                    if test_evidence is not None:
                        evidence = test_evidence
                    else:
                        source_test = next(
                            (item for item in test_functions if item.get("reviewed_mapping")), None
                        )
                        evidence = {
                            "feature_id": feature_id,
                            "signals": [
                                {
                                    "term": "curated module source review",
                                    "source": "reviewed-source-span",
                                    "path": rel,
                                    "line": source_test["line"] if source_test else 1,
                                    "end_line": source_test["end_line"] if source_test else 1,
                                }
                            ],
                        }
                module_evidence[feature_id] = evidence
            feature_evidence_by_id = module_evidence
        features = sorted(feature_evidence_by_id)
        selectors = selectors_for(features)
        item_id = "upstream-test:" + rel
        fixture_id = "fastapi.test." + norm_id(rel[len("tests/") :].removesuffix(".py"))
        exclusion = None
        if is_benchmark:
            exclusion = "Performance harness module: exclude from behavioral parity inputs and map to a separate correctness-gated benchmark workload."
        elif is_maintenance:
            exclusion = "Release automation test does not observe FastAPI's consumer-facing runtime contract."
        elif rel in TEST_EXCLUSIONS:
            exclusion = TEST_EXCLUSIONS[rel]
        elif test_functions and all(
            test["mapping_status"] == "excluded" for test in test_functions
        ):
            exclusion = (
                "All %d executable test functions have individual source-backed exclusion "
                "reasons recorded below; this module contributes no independent FastAPI "
                "behavioral parity input." % len(test_functions)
            )
        case_designs = []
        used_case_ids: set[str] = set()
        if not exclusion:
            for test in test_functions:
                if not test["feature_ids"]:
                    continue
                case_features = test["feature_ids"]
                case_id = fixture_id + "." + norm_id(test["qualified_name"])
                if case_id in used_case_ids:
                    identity = "%s:%s" % (test["qualified_name"], test["line"])
                    suffix = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:8]
                    case_id = case_id + "-" + suffix
                if case_id in used_case_ids:
                    raise AtlasError(
                        "duplicate test fixture ID for %s::%s" % (rel, test["qualified_name"])
                    )
                used_case_ids.add(case_id)
                exact_selectors = test.get(
                    "reviewed_observation_selectors",
                    reviewed_mapping.get("module_observation_selectors"),
                )
                if exact_selectors is not None:
                    exact_selectors = selectors_with_exact_http_body(exact_selectors)
                case_designs.append(
                    {
                        "id": case_id,
                        "source_function": test["qualified_name"],
                        "source_line": test["line"],
                        "source_end_line": test["end_line"],
                        "feature_ids": case_features,
                        "feature_evidence": test["feature_evidence"],
                        "stimulus_design": stimulus_for(case_features),
                        "observation_selectors": list(exact_selectors)
                        if exact_selectors is not None
                        else selectors_for(case_features),
                        "selector_evidence": selector_evidence(case_features, exact_selectors),
                        "mapping_status": test["mapping_status"],
                        "mapping_scope": test.get("mapping_scope"),
                        "reviewed_mapping": test.get("reviewed_mapping"),
                        "stimulus_design_notes": test.get("reviewed_stimulus_notes")
                        or reviewed_mapping.get("stimulus_notes"),
                    }
                )
        unmatched_test_functions = [
            {"name": item["qualified_name"], "line": item["line"], "end_line": item["end_line"]}
            for item in test_functions
            if not item["feature_ids"] and item["mapping_status"] != "excluded"
        ]
        excluded_test_functions = [
            {
                "name": item["qualified_name"],
                "line": item["line"],
                "end_line": item["end_line"],
                "reason": item["exclusion_reason"],
                "source_evidence": item["reviewed_mapping"]["source_evidence"],
            }
            for item in test_functions
            if item["mapping_status"] == "excluded"
        ]
        app_scope_review = APP_DEPENDENCY_SCOPE_REVIEW_BY_MODULE.get(rel)
        app_scope_review_record = None
        if app_scope_review:
            module_review = app_scope_review.get("module")
            app_scope_review_record = {
                "scope": "app/dependency wave disposition; does not exclude behavior from the merged FastAPI contract",
                "module": (
                    {
                        "reason": module_review["reason"],
                        "source_evidence": reviewed_source_spans(
                            fastapi_root,
                            module_review.get("supporting_sources", []),
                            starlette_root,
                        ),
                    }
                    if module_review
                    else None
                ),
                "functions": [
                    {
                        "name": function_name,
                        "reason": function_review["reason"],
                        "source_evidence": reviewed_source_spans(
                            fastapi_root,
                            function_review.get("supporting_sources", []),
                            starlette_root,
                        ),
                    }
                    for function_name, function_review in sorted(
                        app_scope_review.get("functions", {}).items()
                    )
                ],
            }
        independent_workflow_mappings = indexed_workflow_mappings_by_source.get(item_id, [])
        reviewed_module_sources = reviewed_source_spans(
            fastapi_root, reviewed_mapping.get("supporting_sources", []), starlette_root
        )
        reviewed_module_note = reviewed_mapping.get("stimulus_notes", "")
        has_explicit_module_workflow_review = bool(
            reviewed_mapping.get("rationale")
            and reviewed_module_sources
            and (
                reviewed_mapping.get("workflow_cases")
                or (
                    "tests/fixtures/input-recipes/" in reviewed_module_note
                    and "::" in reviewed_module_note
                )
            )
        )
        all_test_functions_reviewed = (
            bool(test_functions)
            and not unmatched_test_functions
            and all(
                test["mapping_status"]
                in {"reviewed_source_candidate", "contract_gated_source_candidate", "excluded"}
                for test in test_functions
            )
        )
        review_status = (
            "excluded"
            if exclusion
            else "reviewed_partial"
            if independent_workflow_mappings
            and (has_explicit_module_workflow_review or all_test_functions_reviewed)
            else "pending"
        )
        if exclusion:
            mapping_status = "excluded"
        elif case_designs and (
            unmatched_test_functions
            or bool(reviewed_mapping.get("contract_gate"))
            or any(
                case["mapping_status"] == "contract_gated_source_candidate" for case in case_designs
            )
        ):
            mapping_status = "partially_mapped"
        elif case_designs:
            mapping_status = "candidate"
        else:
            mapping_status = "review_required"
        module_selector_set = set(selectors)
        module_selector_set.update(reviewed_mapping.get("module_observation_selectors", []))
        module_selector_set.update(
            selector
            for function_mapping in reviewed_function_mappings.values()
            for selector in function_mapping.get("observation_selectors", [])
        )
        module_selectors = selectors_with_exact_http_body(sorted(module_selector_set))
        coverage_items.append(
            {
                "id": item_id,
                "kind": "upstream_test_module",
                "source_path": rel,
                "source_sha256": sha256(path),
                "feature_ids": features,
                "fixture_id": fixture_id if not exclusion and case_designs else None,
                "benchmark_workload_id": fixture_id if is_benchmark else None,
                "observation_selectors": [] if exclusion else module_selectors,
                "selector_evidence": []
                if exclusion
                else selector_evidence(
                    features,
                    module_selectors
                    if "module_observation_selectors" in reviewed_mapping
                    else None,
                ),
                "starlette_rs_planning_areas": [] if exclusion else starlette_areas_for(features),
                "exclusion_reason": exclusion,
                "mapping_status": mapping_status,
                "review_status": review_status,
                "review_reason": (
                    "Some executable test functions still need an independent behavior mapping."
                    if not exclusion and unmatched_test_functions
                    else "At least one behavior mapping is contract-gated and is not represented by a complete independent workflow."
                    if not exclusion
                    and (
                        bool(reviewed_mapping.get("contract_gate"))
                        or any(
                            case["mapping_status"] == "contract_gated_source_candidate"
                            for case in case_designs
                        )
                    )
                    else "No executable test function has a behavior mapping; manual mapping required."
                    if not exclusion and not case_designs
                    else None
                ),
                "mapping_evidence": {
                    "source_module_path": rel,
                    "module_feature_evidence": feature_match_evidence(rel, ""),
                    "test_function_count": len(test_functions),
                    "matched_test_functions": [
                        {
                            "name": case["source_function"],
                            "line": case["source_line"],
                            "end_line": case["source_end_line"],
                            "case_id": case["id"],
                            "mapping_status": case["mapping_status"],
                            "mapping_scope": case.get("mapping_scope"),
                        }
                        for case in case_designs
                    ],
                    "unmatched_test_functions": unmatched_test_functions,
                    "excluded_test_functions": excluded_test_functions,
                    "independent_workflow_mappings": independent_workflow_mappings,
                    **(
                        {"app_dependency_wave_scope_review": app_scope_review_record}
                        if app_scope_review_record
                        else {}
                    ),
                    "reviewed_module_mapping": {
                        "rationale": reviewed_mapping.get("rationale"),
                        "supporting_sources": reviewed_module_sources,
                        **(
                            {"contract_gate": reviewed_mapping["contract_gate"]}
                            if "contract_gate" in reviewed_mapping
                            else {}
                        ),
                        **(
                            {"stimulus_notes": reviewed_mapping["stimulus_notes"]}
                            if "stimulus_notes" in reviewed_mapping
                            else {}
                        ),
                        **(
                            {"workflow_cases": reviewed_mapping["workflow_cases"]}
                            if "workflow_cases" in reviewed_mapping
                            else {}
                        ),
                        **(
                            {
                                "wave_scope_review_exclusions": [
                                    {"scope": "wave_only", **exclusion}
                                    for exclusion in reviewed_mapping[
                                        "source_review_scope_exclusions"
                                    ]
                                ]
                            }
                            if "source_review_scope_exclusions" in reviewed_mapping
                            else {}
                        ),
                    }
                    if reviewed_mapping
                    else None,
                    "mapping_rule": "whole-token source signals plus explicitly reviewed function-to-feature mappings; candidate only",
                },
            }
        )
        if not exclusion and case_designs:
            fixture_backlog.append(
                {
                    "id": fixture_id,
                    "source_item_id": item_id,
                    "stage": "reviewed partial source-to-input mapping; remaining source behavior is not claimed"
                    if review_status == "reviewed_partial"
                    else "partially mapped; remaining functions need review"
                    if unmatched_test_functions
                    else "partially mapped; one or more behaviors remain contract-gated"
                    if any(
                        case["mapping_status"] == "contract_gated_source_candidate"
                        for case in case_designs
                    )
                    else "candidate; independent stimuli require review/materialization",
                    "input_only": True,
                    "stimulus_design": stimulus_for(features),
                    "stimulus_design_notes": reviewed_mapping.get("stimulus_notes"),
                    "observation_selectors": module_selectors,
                    "selector_evidence": selector_evidence(
                        features,
                        module_selectors
                        if "module_observation_selectors" in reviewed_mapping
                        else None,
                    ),
                    "feature_ids": features,
                    "case_designs": case_designs,
                    "independent_workflow_mappings": independent_workflow_mappings,
                    "starlette_rs_planning_areas": starlette_areas_for(features),
                    "source_evidence": {"path": rel, "sha256": sha256(path)},
                }
            )

    docs_root = fastapi_root / "docs/en/docs"
    examples_root = fastapi_root / "docs_src"
    unmatched_examples = []
    examples_by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    example_records = []
    for path in sorted(examples_root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        rel = relative(path, fastapi_root)
        content = path.read_text(encoding="utf-8", errors="replace")
        pages = find_doc_pages_for_example(path, docs_root, fastapi_root, doc_source_links)
        if not pages:
            unmatched_examples.append(rel)
        feature_evidence = feature_match_evidence(rel, content)
        record = {
            "path": rel,
            "sha256": sha256(path),
            "pages": pages,
            "feature_evidence": feature_evidence,
            "feature_ids": [item["feature_id"] for item in feature_evidence],
        }
        example_records.append(record)
        for page in pages:
            examples_by_page[page].append(record)

    page_by_rel = {relative(path, docs_root): path for path in docs_root.rglob("*.md")}
    for rel, path in sorted(page_by_rel.items()):
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        headings = [
            {"line": index, "level": len(match.group(1)), "text": match.group(2).strip()}
            for index, line in enumerate(lines, 1)
            if (match := re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line))
        ]
        page_feature_evidence = feature_match_evidence(rel, "")
        documented_sections = []
        section_feature_evidence = []
        for position, heading in enumerate(headings):
            next_positions = [
                candidate["line"]
                for candidate in headings[position + 1 :]
                if candidate["level"] <= heading["level"]
            ]
            end_line = min(next_positions) - 1 if next_positions else len(lines)
            section_text = "\n".join(lines[heading["line"] : end_line])
            section_evidence = feature_match_evidence(heading["text"], section_text)
            if not section_evidence:
                continue
            section_feature_evidence.extend(section_evidence)
            section_features = [item["feature_id"] for item in section_evidence]
            documented_sections.append(
                {
                    "heading": heading["text"],
                    "start_line": heading["line"],
                    "end_line": end_line,
                    "feature_ids": section_features,
                    "feature_evidence": section_evidence,
                    "observation_selectors": selectors_for(section_features),
                    "selector_evidence": selector_evidence(section_features),
                }
            )
        linked_examples = sorted(examples_by_page.get(rel, []), key=lambda item: item["path"])
        related_usage_evidence = reviewed_source_spans(
            fastapi_root, DOC_RELATED_USAGE_SOURCES.get(rel, []), starlette_root
        )
        evidence_by_feature: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for evidence in page_feature_evidence + section_feature_evidence:
            evidence_by_feature[evidence["feature_id"]].append(
                {"source_path": "docs/en/docs/" + rel, "signals": evidence["signals"]}
            )
        for example in linked_examples:
            for evidence in example["feature_evidence"]:
                evidence_by_feature[evidence["feature_id"]].append(
                    {"source_path": example["path"], "signals": evidence["signals"]}
                )
        reviewed_page_mapping = DOC_PAGE_REVIEW_MAPPINGS.get(rel, {})
        reviewed_page_spans = reviewed_source_spans(
            fastapi_root, reviewed_page_mapping.get("supporting_sources", []), starlette_root
        )
        reviewed_starlette_spans = reviewed_source_spans(
            starlette_root,
            reviewed_page_mapping.get("starlette_contract_sources", []),
            starlette_root,
        )
        for span in reviewed_starlette_spans:
            span["source_authority"] = "Starlette " + STARLETTE_VERSION
        for feature_id in reviewed_page_mapping.get("feature_ids", []):
            evidence_by_feature[feature_id].append(
                {
                    "source_path": "docs/en/docs/" + rel,
                    "signals": [
                        {
                            "term": "curated public-reference review",
                            "source": "reviewed-source-span",
                            "path": span["path"],
                            "line": span["start_line"],
                            "end_line": span["end_line"],
                        }
                        for span in reviewed_page_spans
                    ],
                }
            )
        if reviewed_page_mapping.get("replace_features"):
            allowed_features = set(reviewed_page_mapping.get("feature_ids", []))
            evidence_by_feature = {
                feature_id: evidence
                for feature_id, evidence in evidence_by_feature.items()
                if feature_id in allowed_features
            }
        features = sorted(evidence_by_feature)
        feature_evidence = [
            {"feature_id": feature_id, "evidence": evidence_by_feature[feature_id]}
            for feature_id in features
        ]
        page_id = "documented-page:" + rel
        fixture_id = "fastapi.docs." + norm_id(rel.removesuffix(".md"))
        exclusion = docs_exclusion(rel)
        independent_workflow_mappings = indexed_workflow_mappings_by_source.get(page_id, [])
        review_status = (
            "excluded"
            if exclusion
            else "reviewed_partial"
            if independent_workflow_mappings
            and reviewed_page_mapping.get("rationale")
            and reviewed_page_spans
            else "pending"
        )
        mapping_status = "excluded" if exclusion else "candidate" if features else "review_required"
        page_selectors = selectors_with_exact_http_body(
            reviewed_page_mapping.get("observation_selectors", selectors_for(features))
        )
        reviewed_page_record = None
        if reviewed_page_mapping:
            reviewed_page_record = {
                "rationale": reviewed_page_mapping.get("rationale"),
                "source_evidence": reviewed_page_spans,
            }
            if reviewed_starlette_spans:
                reviewed_page_record["starlette_source_evidence"] = reviewed_starlette_spans
                reviewed_page_record["starlette_contract_authority"] = STARLETTE_VERSION
            for metadata_key in ("contract_gate", "stimulus_notes", "exclusion_reason"):
                if reviewed_page_mapping.get(metadata_key) is not None:
                    reviewed_page_record[metadata_key] = reviewed_page_mapping[metadata_key]
            if reviewed_page_mapping.get("workflow_cases"):
                reviewed_page_record["workflow_cases"] = reviewed_page_mapping["workflow_cases"]
        source_evidence = (
            [{"path": "docs/en/docs/" + rel, "sha256": sha256(path)}]
            + [{"path": item["path"], "sha256": item["sha256"]} for item in linked_examples]
            + related_usage_evidence
            + reviewed_page_spans
            + reviewed_starlette_spans
        )
        coverage_items.append(
            {
                "id": page_id,
                "kind": "documented_feature_page",
                "source_path": "docs/en/docs/" + rel,
                "source_sha256": sha256(path),
                "title": headings[0]["text"] if headings else path.stem,
                "headings": headings,
                "feature_ids": features,
                "fixture_id": fixture_id if not exclusion and features else None,
                "observation_selectors": [] if exclusion else page_selectors,
                "selector_evidence": []
                if exclusion
                else selector_evidence(
                    features,
                    page_selectors if "observation_selectors" in reviewed_page_mapping else None,
                ),
                "starlette_rs_planning_areas": [] if exclusion else starlette_areas_for(features),
                "exclusion_reason": exclusion,
                "mapping_status": mapping_status,
                "review_status": review_status,
                "review_reason": "No whole-token feature signal in page or linked example sources; manual mapping required."
                if not exclusion and not features
                else None,
                "mapping_evidence": {
                    "source_page": "docs/en/docs/" + rel,
                    "headings_indexed": len(headings),
                    "page_feature_evidence": page_feature_evidence,
                    "documented_sections": documented_sections,
                    "linked_example_sources": linked_examples,
                    "related_usage_sources": related_usage_evidence,
                    "reviewed_source_mapping": reviewed_page_record,
                    "independent_workflow_mappings": independent_workflow_mappings,
                    "feature_evidence": feature_evidence,
                    "mapping_rule": "whole-token signals from page and explicitly included docs_src files; candidate only",
                },
            }
        )
        if not exclusion and features:
            fixture_backlog.append(
                {
                    "id": fixture_id,
                    "source_item_id": page_id,
                    "stage": "reviewed partial source-to-input mapping; remaining documented behavior is not claimed"
                    if review_status == "reviewed_partial"
                    else "candidate; independent stimulus requires review/materialization",
                    "input_only": True,
                    "stimulus_design": stimulus_for(features),
                    "observation_selectors": page_selectors,
                    "selector_evidence": selector_evidence(
                        features,
                        page_selectors
                        if "observation_selectors" in reviewed_page_mapping
                        else None,
                    ),
                    "feature_ids": features,
                    "starlette_rs_planning_areas": starlette_areas_for(features),
                    "documented_sections": documented_sections,
                    "source_evidence": source_evidence,
                    "independent_workflow_mappings": independent_workflow_mappings,
                    "related_usage_sources": related_usage_evidence,
                    "reviewed_source_mapping": reviewed_page_record,
                }
            )

    for path in sorted(examples_root.rglob("*.py")):
        rel = relative(path, fastapi_root)
        item_id = "documented-example:" + rel
        if path.name == "__init__.py":
            coverage_items.append(
                {
                    "id": item_id,
                    "kind": "documentation_support_file",
                    "source_path": rel,
                    "source_sha256": sha256(path),
                    "feature_ids": [],
                    "fixture_id": None,
                    "observation_selectors": [],
                    "starlette_rs_planning_areas": [],
                    "exclusion_reason": "Package initializer for documentation examples; not an independently documented behavior.",
                    "mapping_status": "excluded",
                    "mapping_evidence": {"source_path": rel},
                }
            )
            continue
        record = next((item for item in example_records if item["path"] == rel), None)
        if record is None:
            continue
        mapped_page_items = [
            item
            for page in record["pages"]
            for item in coverage_items
            if item["kind"] == "documented_feature_page"
            and item["source_path"] == "docs/en/docs/" + page
            and item["fixture_id"]
        ]
        mapped_pages = sorted({item["fixture_id"] for item in mapped_page_items})
        inherited_page_selectors = sorted(
            {selector for item in mapped_page_items for selector in item["observation_selectors"]}
        )
        example_exclusion = DOC_EXAMPLE_EXCLUSION_OVERRIDES.get(rel)
        reviewed_example_mapping = DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.get(rel)
        if example_exclusion and reviewed_example_mapping:
            raise AtlasError(f"documentation example is both mapped and excluded: {rel}")
        features = (
            []
            if example_exclusion
            else sorted(
                {
                    feature_id
                    for feature_id in record["feature_ids"]
                    + [
                        feature_id
                        for page_item in mapped_page_items
                        for feature_id in page_item["feature_ids"]
                    ]
                }
            )
        )
        example_selectors = (
            []
            if example_exclusion
            else inherited_page_selectors
            if mapped_pages
            else selectors_for(features)
        )
        example_selector_evidence = (
            []
            if example_exclusion
            else merge_selector_evidence([item["selector_evidence"] for item in mapped_page_items])
            if mapped_pages
            else selector_evidence(features, example_selectors)
        )
        independent_workflow_mappings = indexed_workflow_mappings_by_source.get(item_id, [])
        example_fixture_id = (
            "fastapi.docs-example." + norm_id(rel.removeprefix("docs_src/").removesuffix(".py"))
            if reviewed_example_mapping and not example_exclusion
            else None
        )
        direct_example_selectors = sorted(
            {
                selector
                for mapping in (reviewed_example_mapping or {}).get("workflow_cases", [])
                for selector in mapping["observation_selectors"]
            }
        )
        direct_example_selector_evidence = (
            selector_evidence(features, direct_example_selectors)
            if reviewed_example_mapping and not example_exclusion
            else []
        )
        reviewed_example_sources = (
            reviewed_source_spans(
                fastapi_root,
                reviewed_example_mapping.get("supporting_sources", []),
                starlette_root,
            )
            if reviewed_example_mapping and not example_exclusion
            else []
        )
        if reviewed_example_mapping and independent_workflow_mappings:
            expected_mappings = sorted(
                (
                    mapping["recipe_path"],
                    tuple(sorted(mapping["case_ids"])),
                    tuple(sorted(mapping["observation_selectors"])),
                )
                for mapping in reviewed_example_mapping["workflow_cases"]
            )
            actual_mappings = sorted(
                (
                    mapping["recipe_path"],
                    tuple(mapping["case_ids"]),
                    tuple(mapping["observation_selectors"]),
                )
                for mapping in independent_workflow_mappings
            )
            if actual_mappings != expected_mappings:
                raise AtlasError(
                    "indexed documentation-example cases/selectors differ from reviewed mapping: "
                    f"{rel}; expected {expected_mappings!r}, found {actual_mappings!r}"
                )
        example_review_status = (
            "excluded"
            if example_exclusion
            else "reviewed_partial"
            if reviewed_example_mapping and independent_workflow_mappings
            else "pending"
        )
        reviewed_example_record = (
            {
                "rationale": reviewed_example_mapping["rationale"],
                "source_evidence": reviewed_example_sources,
                "workflow_cases": reviewed_example_mapping["workflow_cases"],
            }
            if reviewed_example_mapping and not example_exclusion
            else None
        )
        mapping_rule = (
            "distinct upstream_documentation_example evidence maps this exact docs_src file to "
            "the listed independent cases and selectors; inherited page selectors remain "
            "separate and do not widen this example-level scope"
            if reviewed_example_mapping and independent_workflow_mappings and not example_exclusion
            else "reviewed exact docs_src mapping awaits materialization in the independent input index; inherited selectors remain page-level"
            if reviewed_example_mapping and not example_exclusion
            else "supporting source inherits selectors from its mapped page fixture; this links the source to page-level observations and does not claim independent per-example behavior coverage"
            if mapped_pages and not example_exclusion
            else "source is excluded by the recorded exclusion reason"
            if example_exclusion
            else "source has no active page fixture mapping and requires review"
        )
        example_item = {
            "id": item_id,
            "kind": "documented_python_example_source",
            "source_path": rel,
            "source_sha256": record["sha256"],
            "document_pages": ["docs/en/docs/" + page for page in record["pages"]],
            "feature_ids": features,
            "fixture_id": example_fixture_id,
            "mapped_fixture_ids": mapped_pages,
            "observation_selectors": example_selectors,
            "selector_evidence": example_selector_evidence,
            "starlette_rs_planning_areas": starlette_areas_for(features),
            "exclusion_reason": example_exclusion,
            "mapping_status": "excluded"
            if example_exclusion
            else "supporting_source"
            if mapped_pages
            else "review_required",
            "review_status": example_review_status,
            "review_reason": None
            if example_exclusion or example_review_status == "reviewed_partial"
            else "Exact example-level case/selectors or a source-backed exclusion reason remain to be reviewed.",
            "mapping_evidence": {
                "example_source_path": rel,
                "page_match": "matched" if record["pages"] else "unresolved",
                "page_paths": record["pages"],
                "feature_evidence": record["feature_evidence"],
                "mapped_documented_pages": [
                    {
                        "source_path": item["source_path"],
                        "fixture_id": item["fixture_id"],
                        "feature_ids": item["feature_ids"],
                        "observation_selectors": item["observation_selectors"],
                        "selector_evidence": item["selector_evidence"],
                    }
                    for item in mapped_page_items
                ],
                "independent_workflow_mappings": independent_workflow_mappings,
                "example_observation_selectors": direct_example_selectors,
                "example_selector_evidence": direct_example_selector_evidence,
                "reviewed_example_mapping": reviewed_example_record,
                "mapping_rule": mapping_rule,
            },
        }
        coverage_items.append(example_item)
        if reviewed_example_mapping and not example_exclusion:
            fixture_backlog.append(
                {
                    "id": example_fixture_id,
                    "source_item_id": item_id,
                    "stage": "reviewed partial example-to-input mapping; only the listed cases and selectors are claimed",
                    "input_only": True,
                    "stimulus_design": stimulus_for(features),
                    "stimulus_design_notes": reviewed_example_mapping["rationale"],
                    "observation_selectors": direct_example_selectors,
                    "selector_evidence": direct_example_selector_evidence,
                    "feature_ids": features,
                    "starlette_rs_planning_areas": starlette_areas_for(features),
                    "source_evidence": reviewed_example_sources,
                    "independent_workflow_mappings": independent_workflow_mappings,
                }
            )
    coverage_items.sort(key=lambda x: x["id"])
    fixture_backlog.sort(key=lambda x: x["id"])

    aliases = []
    for binding in inventory["import_bindings"]:
        if (
            binding.get("local_name") != binding.get("imported_name")
            or binding.get("root_export")
            or binding.get("starlette_delegation") == "direct_reexport"
        ):
            aliases.append(
                {
                    "id": binding["id"],
                    "local_name": binding.get("local_name"),
                    "source_name": binding.get("imported_name"),
                    "source_module": binding.get("imported_module"),
                    "target_path": binding.get("target_path"),
                    "identity_alias": binding.get("identity_alias"),
                    "root_export": binding.get("root_export"),
                    "evidence": binding.get("source_ref"),
                }
            )
    deprecations = inventory.get("deprecations", [])
    error_candidates = []
    api_contract_overlay = project_metadata.get("reviewed_api_contract_overlay", {})
    selector_rules = api_contract_overlay.get("error_selector_rules", [])
    matched_selector_rules: set[str] = set()
    warning_reviews = api_contract_overlay.get("warning_classification_reviews", {})
    generic_error_selectors = [
        "error.class",
        "error.args",
        "error.public_attributes",
    ]
    for record in candidates.values():
        candidate_name = record["id"].split(".")[-1]
        if re.search(r"(?:Exception|Error|Disconnect|Warning)$", candidate_name):
            is_warning = candidate_name.endswith("Warning")
            matching_rules = [
                rule
                for rule in selector_rules
                if record["id"] in rule.get("candidate_ids", [])
                or record.get("target_path") in rule.get("target_paths", [])
            ]
            if len(matching_rules) > 1:
                raise ValueError(
                    f"error candidate matches multiple protocol selector rules: {record['id']}"
                )
            if matching_rules:
                matched_selector_rules.add(matching_rules[0]["id"])
                observation_selectors = matching_rules[0]["observation_selectors"]
            elif is_warning:
                observation_selectors = ["warnings.category_message"]
            else:
                observation_selectors = generic_error_selectors

            error_candidate = {
                "id": record["id"],
                "classification": record["classification"],
                "candidate_kind": "warning" if is_warning else "error",
                "source_evidence": record["source_evidence"],
                "public_evidence": record["public_evidence"],
                "observation_selectors": observation_selectors,
            }
            warning_review = warning_reviews.get(record["id"])
            if (
                warning_review is None
                and record.get("target_path")
                and record.get("classification") == "uncertain"
            ):
                target_review = warning_reviews.get(record["target_path"])
                if (
                    target_review is not None
                    and target_review.get("classification") == record["classification"]
                ):
                    warning_review = target_review
            if warning_review is not None:
                if (
                    not is_warning
                    or warning_review.get("classification") != record["classification"]
                ):
                    raise ValueError(
                        f"warning review must preserve the source classification: {record['id']}"
                    )
                error_candidate["classification_review"] = warning_review
            error_candidates.append(error_candidate)

    missing_selector_rules = {
        rule["id"] for rule in selector_rules if rule["id"] not in matched_selector_rules
    }
    if missing_selector_rules:
        raise ValueError(
            "reviewed error selector rules do not match pinned source candidates: "
            + ", ".join(sorted(missing_selector_rules))
        )

    for coverage_item in coverage_items:
        coverage_item["starlette_rs_contract_mappings"] = starlette_contract_mappings_for(
            coverage_item
        )

    unresolved = [
        {
            "id": "starlette-rs-surface-review",
            "status": "crosswalk-generated; support-and-revision-review-pending",
            "question": "For each FastAPI behavior that delegates to Starlette, does the sibling Starlette-RS contract provide the required surface and exact target support, without importing or duplicating unrelated Starlette APIs?",
            "evidence": f"The merged FastAPI coverage matrix assigns Starlette-RS ownership areas, and direct re-export/subclass/helper edges reference the sibling catalog and reviewed dispositions. FastAPI-RS metadata and CI pin the local sibling at {starlette_rs_revision[:12]}; the initial FastAPI-RS slice consumes it, while full cross-project behavior review remains open.",
        },
        {
            "id": "pydantic-runtime-generated-api",
            "status": "pending",
            "question": "Which inherited/runtime-generated Pydantic model methods and schemas are externally observable through FastAPI's OpenAPI models and facade?",
            "evidence": "FastAPI AST inventory explicitly excludes Pydantic-generated BaseModel surfaces.",
        },
        {
            "id": "fastapi-dynamic-runtime-surface",
            "status": "pending",
            "question": "What package attributes, wrappers, signatures, and warnings are added or modified at import/runtime?",
            "evidence": "Source inventory records AST declarations; it does not import FastAPI for reflection.",
        },
        {
            "id": "case-construction-input-contract",
            "status": "workflow-v3-present; dependency-module-state-and-warning-controls-pending",
            "question": "Which controlled dependency-module states and warning observations are still required for setup-time errors beyond the v3 per-case factory input and construction-exception selectors?",
            "evidence": "The v3 workflow expresses per-case factory input and exact construction outcome/class/message, and construction-error cases now map invalid path/sequence parameters, response models, and Pydantic v1 models. tests/test_multipart_installation.py still mutates multipart module state before route setup, and warnings remain a separate selector without runner support.",
        },
        {
            "id": "lifespan-input-and-observation-contract",
            "status": "workflow-v3-expressible; fixture-and-warning-coverage-pending",
            "question": "Which FastAPI and APIRouter lifespan combinations still need independent input cases and exact deprecation-warning observations under the v3 lifecycle workflow?",
            "evidence": "The v3 contract now drives lifespan startup before requests and shutdown after them, carries yielded state into request scopes, and selects protocol order, stage outcomes, errors, and workload side effects. The source-backed fixture wave is being mapped; TestClient-specific effects and on_event warnings are not claimed by these direct-ASGI inputs.",
        },
        {
            "id": "fastapi-cli-compatibility-boundary",
            "status": "package-pin-and-process-workflow-required",
            "question": "Does FastAPI-RS replace FastAPI's `fastapi` console script, and if so which fastapi-cli package identity, optional environment, arguments, output streams, and exit behavior are in the compatibility contract?",
            "evidence": "FastAPI 0.141.1 declares the `fastapi` entrypoint and delegates its implementation to the separate fastapi-cli package; the current workflow schemas cannot execute or observe subprocesses, and no CLI package pin is selected.",
        },
        {
            "id": "fixture-recipe-execution-contract",
            "status": "first-slice-defined; broader-api-coverage-pending",
            "question": "Which additional independently authored workflows should extend the first request/response slice to cover the public FastAPI contract?",
            "evidence": "The strict first-slice input recipe and workload, public pass-through facade, Rust-owned target implementation, oracle and target workers, and exact comparator are present. The first slice is narrow; full operation-level coverage and fresh results for broader cases remain pending.",
        },
        {
            "id": "starlette-rs-target-revision",
            "status": starlette_rs_revision_state,
            "question": "Do the local path dependency, metadata, and CI continue to resolve to the same committed Starlette-RS target profile?",
            "evidence": f"FastAPI-RS directly reuses ../starlette-rs/starlette-rs; metadata.yaml and CI pin {starlette_rs_revision}. The atlas reads the sibling manifest/catalog/review and records the checkout state. Keep the local checkout clean at the pin for reproducible builds and parity runs.",
        },
    ]
    unresolved.append(
        {
            "id": "app-dependency-wave-residual-gaps",
            "status": "source-reviewed; partial-input-gates-remain",
            "question": "Which app, dependency, lifecycle, exception, and WebSocket cases still need independent inputs or target observations?",
            "evidence": " ".join(APP_DEPENDENCY_WAVE_GAPS.values()),
        }
    )

    priority_backlog = [
        {
            "priority": 0,
            "id": "first-end-to-end-request-response-slice",
            "status": "implementation-present; broader-contract-pending",
            "schema_path": first_slice_workflow["schema_path"],
            "fixture_path": first_slice_workflow["input_path"],
            "workload_path": first_slice_workflow["workload"]["path"],
            "feature_ids": [
                "app-routing",
                "request-validation",
                "dependency-security",
                "response-serialization",
                "openapi-docs",
            ],
            "fixture_ids": first_slice_workflow["case_ids"],
            "acceptance": "POST /items/{item_id} through FastAPI public API; path/query/header dependency; Pydantic request validation; response-model field filtering; observe exact HTTP response and ordered ASGI send message types; observe generated OpenAPI; execute the same input against identity-checked oracle and target workers.",
            "starlette_rs_planning_areas": [
                "asgi-http-websocket-lifespan",
                "applications-requests-responses-background-concurrency",
                "streaming-headers-cookies-errors-and-cleanup",
            ],
        },
        {
            "priority": 1,
            "id": "complete-public-operation-contract",
            "status": "incomplete",
            "acceptance": "Complete the FastAPI public operation contract: signatures, runtime availability, target bindings, observable requirements, and an explicit supported, unsupported, or unresolved target disposition for every public API; keep the 1.6.0 Starlette-RS ownership boundary explicit.",
        },
        {
            "priority": 2,
            "id": "complete-starlette-consumption-crosswalk",
            "status": "partial",
            "acceptance": "Review all 133 direct re-export, subclass, helper, and internal-import edges against the pinned Starlette 1.6.0 and Starlette-RS contracts; resolve the four target paths without exact sibling review rows; never duplicate Starlette-owned behavior.",
        },
        {
            "priority": 3,
            "id": "review-runtime-and-generated-public-surfaces",
            "status": "backlog",
            "acceptance": "Reflect supported Python profiles and review runtime-added FastAPI attributes, inherited Pydantic model methods, generated OpenAPI models, and object identity; retain explicit uncertainty where source inspection cannot establish behavior.",
        },
        {
            "priority": 4,
            "id": "deepen-independent-input-and-observation-coverage",
            "status": "partial",
            "acceptance": "Extend the 486 materialized workflows with independent cases and supported selectors for high-impact partial behavior, starting with yield-dependency cleanup/cancellation and request validation; directly map documentation examples when page-level selectors are insufficient; never copy upstream tests or expected outputs.",
        },
        {
            "priority": 5,
            "id": "complete-alias-deprecation-error-and-extra-matrix",
            "status": "backlog",
            "acceptance": "Review alias identity and behavior, exercise source deprecations and warnings, materialize the 42 HTTP/WebSocket/validation error candidates, and verify all three optional-extra profiles across supported Python versions 3.10-3.14.",
        },
        {
            "priority": 6,
            "id": "complete-recursive-dependency-purpose-and-license-records",
            "status": "incomplete",
            "acceptance": "Add source-backed feature/purpose evidence for Python transitive dependencies, reconcile target-runtime and recursive build-time closures, resolve ambiguous license families, bundle required notices, and record the zlib backend in each release artifact.",
        },
        {
            "priority": 7,
            "id": "build-upstream-equivalent-benchmark-tiers",
            "status": "narrow-direct-asgi-lanes-only",
            "acceptance": "After each corresponding parity gate passes, reproduce FastAPI's TestClient request, OpenAPI, construction, and memory benchmark workloads with matched timing boundaries; report direct-ASGI measurements separately and never generalize the current first-slice result.",
        },
    ]

    source_api_candidates = sorted(candidates.values(), key=lambda row: row["id"])
    source_api_candidate_indexes = {
        row["id"]: index for index, row in enumerate(source_api_candidates)
    }
    reviewed_api_overlay = project_metadata.get("reviewed_api_contract_overlay", {})
    if reviewed_api_overlay.get("schema") != "fastapi-rs/reviewed-api-contract-overlay@2":
        raise AtlasError("metadata.yaml reviewed API contract overlay schema is unsupported")
    inherited_api_overlay = reviewed_api_overlay.get("inherited_operations", {})
    if not isinstance(inherited_api_overlay, dict):
        raise AtlasError("metadata.yaml inherited API operation overlay must be a mapping")
    reviewed_inherited_api_candidates = []
    for operation_id, operation in sorted(inherited_api_overlay.items()):
        if not isinstance(operation, dict):
            raise AtlasError(
                f"metadata.yaml inherited API candidate must be a mapping: {operation_id}"
            )
        if operation_id in candidates:
            raise AtlasError(
                "inherited API candidates must remain separate from source declarations: "
                + operation_id
            )
        exposure_candidate_id = operation.get("fastapi_exposure_candidate_id")
        exposure_candidate = candidates.get(exposure_candidate_id)
        if (
            not isinstance(exposure_candidate_id, str)
            or exposure_candidate is None
            or exposure_candidate.get("kind") != "class"
            or exposure_candidate.get("classification") != "supported"
        ):
            raise AtlasError(
                "inherited API candidate must reference a supported FastAPI class: " + operation_id
            )
        inherited_candidate = {
            "id": operation_id,
            "kind": "inherited_method",
            "classification": "supported",
            "classification_evidence_rule": (
                "FastAPI class inheritance and reviewed user documentation expose the "
                "Starlette-owned method on FastAPI"
            ),
            "exposure_candidate_id": exposure_candidate_id,
            "exposure_candidate_ref": (
                "/api_candidates/" + str(source_api_candidate_indexes[exposure_candidate_id])
            ),
            "source_evidence": operation.get("source_evidence", []),
            "documentation_contract_refs": operation.get("documentation_contract_refs", []),
            "fixture_refs": operation.get("fixture_refs", []),
            "feature_ids": operation.get("feature_ids", []),
            "observation_selectors": operation.get("observation_selectors", []),
            "reviewed_overlay_ref": (
                "/reviewed_api_contract_overlay/inherited_operations/"
                + operation_id.replace("~", "~0").replace("/", "~1")
            ),
        }
        sibling_gap = operation.get("sibling_contract_gap")
        if sibling_gap is not None:
            if (
                not isinstance(sibling_gap, dict)
                or "canonical_operation_id" in operation
                or not isinstance(operation.get("signature_source"), dict)
                or not isinstance(operation.get("target_binding"), dict)
            ):
                raise AtlasError(
                    "inherited sibling-gap candidates require signature source and target "
                    "binding and must omit a canonical operation: " + operation_id
                )
            inherited_candidate.update(
                {
                    "signature_source": operation["signature_source"],
                    "sibling_contract_gap": sibling_gap,
                    "target_binding": operation["target_binding"],
                }
            )
        else:
            canonical_operation_id = operation.get("canonical_operation_id")
            if not isinstance(canonical_operation_id, str) or not canonical_operation_id:
                raise AtlasError(
                    "inherited API candidate has no canonical sibling operation: " + operation_id
                )
            inherited_candidate["canonical_operation_id"] = canonical_operation_id
            target_binding = operation.get("target_binding")
            if target_binding is not None:
                if not isinstance(target_binding, dict):
                    raise AtlasError(
                        "inherited API target binding must be a mapping: " + operation_id
                    )
                inherited_candidate["target_binding"] = target_binding
        reviewed_inherited_api_candidates.append(inherited_candidate)

    atlas = {
        "schema": "fastapi-rs/compatibility-atlas@3",
        "purpose": "Source-backed FastAPI API classification and merged upstream test/documentation fixture backlog; not parity evidence.",
        "authorities": {
            "fastapi": {
                "repository": "https://github.com/fastapi/fastapi",
                **fastapi_identity,
                "inventory_path": "tests/fixtures/api-inventory.json",
                "inventory_sha256": inventory_sha,
                "declared_starlette_requirement": ">=0.46.0",
                "declared_pydantic_requirement": ">=2.9.0",
            },
            "starlette": {
                "repository": "https://github.com/Kludex/starlette",
                **starlette_identity,
                "use": "sole selected Starlette compatibility/oracle contract",
            },
            "starlette_rs": {
                "project": "starlette-rs",
                "manifest_path": "tests/fixtures/manifest.yaml",
                "manifest_sha256": sha256(starlette_rs_manifest_path),
                "current_contract_id": starlette_rs_contract_id,
                "source_version": STARLETTE_VERSION,
                "source_commit": STARLETTE_COMMIT,
                "current_target_statuses": starlette_rs_target_statuses,
                "api_surface_catalog_path": "docs/api-surface.csv",
                "api_surface_catalog_sha256": sha256(starlette_surface_catalog_path),
                "api_review_path": "docs/atlas/api-review.csv",
                "api_review_sha256": sha256(starlette_review_path),
                "api_review_dispositions": dict(
                    Counter(
                        row.get("api_disposition")
                        for records in starlette_review_records.values()
                        for row in records
                    )
                ),
                "coverage_matrix_path": "docs/atlas/coverage-matrix.csv"
                if starlette_coverage_matrix_path.exists()
                else None,
                "coverage_matrix_sha256": sha256(starlette_coverage_matrix_path)
                if starlette_coverage_matrix_path.exists()
                else None,
                "fastapi_rs_planning_area_ids": sorted(starlette_areas),
                "planning_area_owner": "FastAPI-RS taxonomy; not sibling contract operations or implementation coverage",
                "implementation_revision": starlette_rs_revision,
                "implementation_revision_state": starlette_rs_revision_state,
                "state": "bounded Starlette-RS source contract and implementations exist; FastAPI-RS consumes the pinned sibling, while full cross-project consumption review remains open",
            },
            "python": read_python_support(
                fastapi_root / "pyproject.toml", fastapi_root / ".github/workflows/test.yml"
            ),
            "pydantic": {
                "selected_version": "2.13.4",
                "source_lock_version": inventory["source_identity"]
                .get("locked_components", {})
                .get("pydantic"),
                "ownership": "reuse public Pydantic v2 models; Rust pydantic-core is an implementation detail of Pydantic",
            },
        },
        "classification_policy": {
            "supported": "FastAPI root re-export, documented target/import/module declaration, explicitly allowlisted documented class member, field of a documented OpenAPI model, or an exact reviewed source/docs contract; this describes source API evidence and does not claim FastAPI-RS support.",
            "private/internal": "Pinned source marks the name private/protocol-internal, it lives in an underscore-private module/member, or source review finds only implementation use without consumer-facing contract evidence.",
            "uncertain": "Importable or public-looking source name without sufficient user-facing API evidence; keep visible until reviewed.",
            "source_inventory_is_not_runtime_reflection": True,
        },
        "api_classification_review": {
            "path": args.callable_review.resolve().relative_to(PROJECT).as_posix(),
            "schema": callable_review["schema"],
            "sha256": sha256(args.callable_review.resolve()),
            "scope": callable_review["scope"],
        },
        "api_import_binding_classification_review": {
            "path": args.import_binding_review.resolve().relative_to(PROJECT).as_posix(),
            "schema": import_binding_review["schema"],
            "sha256": sha256(args.import_binding_review.resolve()),
            "source_identity": import_binding_review["source_identity"],
            "scope": import_binding_review["scope"],
            "pinned_starlette_rs_sources": import_binding_review["pinned_starlette_rs_sources"],
        },
        "api_source_classification_review": {
            "path": args.source_api_review.resolve().relative_to(PROJECT).as_posix(),
            "schema": source_api_review["schema"],
            "sha256": sha256(args.source_api_review.resolve()),
            "source_identity": source_api_review["source_identity"],
            "scope": source_api_review["scope"],
        },
        "api_public_candidate_classification_review": {
            "path": args.public_candidate_review.resolve().relative_to(PROJECT).as_posix(),
            "schema": public_candidate_review["schema"],
            "sha256": sha256(args.public_candidate_review.resolve()),
            "source_identity": public_candidate_review["source_identity"],
            "scope": public_candidate_review["scope"],
        },
        "api_candidates": source_api_candidates,
        "reviewed_inherited_api_candidates": reviewed_inherited_api_candidates,
        "aliases": aliases,
        "deprecations": deprecations,
        "errors": sorted(error_candidates, key=lambda x: x["id"]),
        "optional_features": parse_extras(fastapi_root / "pyproject.toml"),
        "feature_families": FEATURES,
        "starlette_integration_edges": starlette_edges,
        "coverage_matrix": coverage_items,
        "first_end_to_end_request_response_slice": first_slice_workflow,
        "fixture_backlog_ref": {
            "path": "tests/fixtures/fixture-backlog.json",
            "schema": "fastapi-rs/fixture-backlog@1",
            "item_count": len(fixture_backlog),
        },
        "_fixture_backlog_designs": fixture_backlog,
        "unresolved_compatibility_points": unresolved,
        "prioritized_backlog": priority_backlog,
        "counts": {
            "api_candidates": len(candidates),
            "reviewed_inherited_api_candidates": len(reviewed_inherited_api_candidates),
            "inherited_api_classifications": dict(
                Counter(row["classification"] for row in reviewed_inherited_api_candidates)
            ),
            "reviewed_callable_candidates": len(callable_review["rows"]),
            "reviewed_import_binding_candidates": len(import_binding_review["rows"]),
            "reviewed_source_api_candidates": len(source_api_review["rows"]),
            "reviewed_public_candidate_candidates": len(public_candidate_review["rows"]),
            "api_classifications": dict(
                Counter(record["classification"] for record in candidates.values())
            ),
            "starlette_integration_edges": len(starlette_edges),
            "test_modules": sum(
                1 for item in coverage_items if item["kind"] == "upstream_test_module"
            ),
            "test_modules_mapped_to_parity_backlog": sum(
                1
                for item in coverage_items
                if item["kind"] == "upstream_test_module" and item["fixture_id"]
            ),
            "test_modules_with_independent_input_workflow_link": sum(
                1
                for item in coverage_items
                if item["kind"] == "upstream_test_module"
                and item["mapping_evidence"]["independent_workflow_mappings"]
            ),
            "test_modules_candidate_links_pending_behavior_review": sum(
                1
                for item in coverage_items
                if item["kind"] == "upstream_test_module"
                and item["fixture_id"]
                and item["review_status"] == "pending"
            ),
            "test_modules_with_reviewed_partial_mapping": sum(
                1
                for item in coverage_items
                if item["kind"] == "upstream_test_module"
                and item["review_status"] == "reviewed_partial"
            ),
            "test_modules_excluded_from_parity": sum(
                1
                for item in coverage_items
                if item["kind"] == "upstream_test_module" and item["exclusion_reason"]
            ),
            "documentation_pages": sum(
                1 for item in coverage_items if item["kind"] == "documented_feature_page"
            ),
            "documentation_pages_with_independent_input_workflow_link": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_feature_page"
                and item["mapping_evidence"]["independent_workflow_mappings"]
            ),
            "documentation_pages_candidate_links_pending_behavior_review": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_feature_page"
                and item["fixture_id"]
                and item["review_status"] == "pending"
            ),
            "documentation_pages_with_reviewed_partial_mapping": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_feature_page"
                and item["review_status"] == "reviewed_partial"
            ),
            "documentation_pages_excluded": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_feature_page" and item["exclusion_reason"]
            ),
            "documentation_python_examples": sum(
                1 for item in coverage_items if item["kind"] == "documented_python_example_source"
            ),
            "documentation_python_source_files": sum(
                1
                for item in coverage_items
                if item["kind"]
                in {"documented_python_example_source", "documentation_support_file"}
            ),
            "documentation_python_examples_grouped_with_page": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_python_example_source"
                and item["mapping_status"] == "supporting_source"
            ),
            "documentation_python_examples_with_independent_input_workflow_link": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_python_example_source"
                and item["mapping_evidence"]["independent_workflow_mappings"]
            ),
            "documentation_python_examples_with_reviewed_partial_mapping": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_python_example_source"
                and item["review_status"] == "reviewed_partial"
            ),
            "documentation_python_examples_pending_behavior_review": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_python_example_source"
                and item["review_status"] == "pending"
            ),
            "documentation_python_examples_excluded": sum(
                1
                for item in coverage_items
                if item["kind"] == "documented_python_example_source"
                and item["mapping_status"] == "excluded"
            ),
            "documentation_support_files_excluded": sum(
                1 for item in coverage_items if item["kind"] == "documentation_support_file"
            ),
            "fixture_backlog_items": len(fixture_backlog),
            "test_function_designs": sum(
                len(item.get("case_designs", [])) for item in fixture_backlog
            ),
            "first_slice_input_cases": len(first_slice_workflow["case_ids"]),
            "unmatched_documentation_examples": len(unmatched_examples),
            "source_deprecations": len(deprecations),
            "alias_records": len(aliases),
            "error_candidates": len(error_candidates),
        },
        "unmatched_documentation_examples": unmatched_examples,
    }
    return atlas


def render_markdown(atlas: dict[str, Any]) -> str:
    counts = atlas["counts"]
    manifest = yaml.safe_load(
        (PROJECT / "tests/fixtures/manifest.yaml").read_text(encoding="utf-8")
    )
    api_contract = manifest.get("api_surface_contract", {})
    api_contract_counts = api_contract.get("counts", {})
    if api_contract.get("schema") not in {
        "fastapi-rs/public-api-contract@1",
        "fastapi-rs/public-api-contract@2",
        "fastapi-rs/public-api-contract@3",
    }:
        raise AtlasError("manifest has no generated per-symbol source API contract")
    required_public_symbols = api_contract_counts.get("required_public_symbols", 0)
    required_inherited_operations = counts.get("reviewed_inherited_api_candidates", 0)
    required_public_api_candidates = required_public_symbols + required_inherited_operations
    facade_tree = ast.parse(
        (PROJECT / "fastapi-rs-py/python/fastapi/__init__.py").read_text(encoding="utf-8")
    )
    native_facade_exports = sum(
        len(node.names)
        for node in facade_tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "fastapi_rs._core"
    )
    symbols_with_documented_refs = api_contract_counts.get(
        "symbols_with_documented_feature_refs", 0
    )
    symbols_with_api_workflow_refs = api_contract_counts.get(
        "symbols_with_direct_api_input_workflow_refs", 0
    )
    materialized_index = json.loads(
        (PROJECT / "tests/fixtures/materialized-input-index.json").read_text(encoding="utf-8")
    )
    materialized_workflows = len(materialized_index["workflows"])
    materialized_cases = sum(len(row["case_ids"]) for row in materialized_index["workflows"])
    materialized_mappings = len(materialized_index["mappings"])
    materialized_partial_mappings = sum(
        mapping["coverage_status"] == "partial" for mapping in materialized_index["mappings"]
    )
    materialized_test_sources = {
        mapping["source_item_id"]
        for mapping in materialized_index["mappings"]
        if mapping["source_item_id"].startswith("upstream-test:")
    }
    materialized_documentation_sources = {
        mapping["source_item_id"]
        for mapping in materialized_index["mappings"]
        if mapping["source_item_id"].startswith("documented-page:")
    }
    materialized_documentation_example_sources = {
        mapping["source_item_id"]
        for mapping in materialized_index["mappings"]
        if mapping["source_item_id"].startswith("documented-example:")
    }
    selector_catalog = json.loads(
        (PROJECT / "tests/fixtures/observation-selectors.json").read_text(encoding="utf-8")
    )
    selector_count = len(selector_catalog["selectors"])
    starlette_contract_mappings = [
        mapping
        for row in atlas["coverage_matrix"]
        for mapping in row.get("starlette_rs_contract_mappings", [])
    ]
    linked_contract_mappings = [
        mapping
        for mapping in starlette_contract_mappings
        if mapping["status"] == "linked-to-current-contract-slice"
    ]
    out_of_contract_mappings = [
        mapping
        for mapping in starlette_contract_mappings
        if mapping["status"] == "out-of-current-contract-slice"
    ]
    unique_starlette_operations = {
        (operation["surface_id"], operation["operation_id"])
        for mapping in linked_contract_mappings
        for operation in mapping["operation_refs"]
    }
    mappings_by_workflow = {}
    for mapping in materialized_index["mappings"]:
        mappings_by_workflow[mapping["workflow_id"]] = (
            mappings_by_workflow.get(mapping["workflow_id"], 0) + 1
        )
    lines = [
        "# FastAPI compatibility atlas",
        "",
        "This source-backed compatibility atlas indexes the API denominator and candidate fixture mappings. Automated family assignments are evidence leads, not manually reviewed coverage, parity results, or complete FastAPI-RS support claims.",
        "",
        "## Pinned authorities",
        "",
        "- FastAPI: 0.141.1 at `" + atlas["authorities"]["fastapi"]["commit"] + "`.",
        "- Starlette oracle contract: 1.6.0 at `"
        + atlas["authorities"]["starlette"]["commit"]
        + "` (the sole selected Starlette version).",
        "- Starlette-RS implementation contract: at `"
        + atlas["authorities"]["starlette_rs"]["implementation_revision"]
        + "`.",
        "- FastAPI declares `starlette>=0.46.0`, which admits the selected contract. Its upstream lock graph is dependency-inventory evidence, not another compatibility profile.",
        "- Pydantic: 2.13.4 source-lock baseline; Python support is `"
        + atlas["authorities"]["python"]["requires_python"]
        + "`.",
        "",
        "## Source candidate classification",
        "",
        "| Candidates | Supported by source evidence | Private/internal | Uncertain |",
        "|---:|---:|---:|---:|",
        "| %d | %d | %d | %d |"
        % (
            counts["api_candidates"],
            atlas["counts"]["api_classifications"].get("supported", 0),
            atlas["counts"]["api_classifications"].get("private/internal", 0),
            atlas["counts"]["api_classifications"].get("uncertain", 0),
        ),
        "",
        "`api_candidates` in the machine-readable atlas carries a FastAPI source path/line for every row plus public evidence or an explicit uncertainty/private rule. `supported` classifies the upstream API surface only; it does not claim target implementation support.",
        "",
        "## Per-symbol API contract in the active manifest",
        "",
        "The single `tests/fixtures/manifest.yaml` indexes %d source-supported symbols and %d separately reviewed inherited API candidates (%d public API candidates total). Direct symbols link to the pinned AST inventory and both runtime-reflection profiles; inherited candidates either delegate to a canonical Starlette-RS operation or record a pinned source signature and explicit sibling-contract gap, without treating registration as ASGI dispatch. The contract links alias, deprecation, error, documented-feature, direct API workflow, selector, and planned Python import-path evidence; %d direct symbols link to a documented-page fixture design and %d to a direct API input workflow. The current Python facade directly re-exports %d native names; this source contract does not measure behavioral completeness, and broader operation-level review remains pending."
        % (
            required_public_symbols,
            required_inherited_operations,
            required_public_api_candidates,
            symbols_with_documented_refs,
            symbols_with_api_workflow_refs,
            native_facade_exports,
        ),
        "",
        "| Signature/shape evidence | Symbols |",
        "|---|---:|",
    ]
    for signature_state, symbol_count in sorted(
        api_contract_counts.get("signature_contract_states", {}).items()
    ):
        lines.append(f"| `{signature_state}` | {symbol_count} |")
    lines.extend(
        [
            "",
            "## Merged coverage matrix and fixture backlog",
            "",
            "| Source denominator | Total | Input workflow links | Reviewed partial | Pending behavior review | Explicitly excluded |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(
        [
            "| Upstream `test_*.py` modules | %d | %d | %d | %d | %d |"
            % (
                counts["test_modules"],
                counts["test_modules_with_independent_input_workflow_link"],
                counts["test_modules_with_reviewed_partial_mapping"],
                counts["test_modules_candidate_links_pending_behavior_review"],
                counts["test_modules_excluded_from_parity"],
            ),
            "| User-facing documentation pages | %d | %d | %d | %d | %d |"
            % (
                counts["documentation_pages"],
                counts["documentation_pages_with_independent_input_workflow_link"],
                counts["documentation_pages_with_reviewed_partial_mapping"],
                counts["documentation_pages_candidate_links_pending_behavior_review"],
                counts["documentation_pages_excluded"],
            ),
            "| Documentation Python files (examples + support initializers) | %d | %d | %d | %d | %d |"
            % (
                counts["documentation_python_source_files"],
                counts["documentation_python_examples_with_independent_input_workflow_link"],
                counts["documentation_python_examples_with_reviewed_partial_mapping"],
                counts["documentation_python_examples_pending_behavior_review"],
                counts["documentation_python_examples_excluded"]
                + counts["documentation_support_files_excluded"],
            ),
            "",
            "Python-source exclusions include the documented Pydantic Settings configuration file, one debugging/setup example, and %d package initializers. Of the remaining examples, %d have a reviewed direct input-workflow link; examples grouped with a documentation page inherit only page-level selectors, which do not claim that each example's behavior was exercised."
            % (
                counts["documentation_support_files_excluded"],
                counts["documentation_python_examples_with_reviewed_partial_mapping"],
            ),
            "",
            "Review state is separate from coverage completeness. `reviewed_partial` means pinned source evidence and exact indexed workflows, cases, and selectors were reviewed for the linked behavior; it does not claim complete source behavior or parity. Pending counts identify examples without that direct review. The materialized index has %d distinct upstream test modules, %d documentation pages, and %d exact documentation Python examples linked to workflows; all %d mapping rows are partial. No source module, documentation page, or Python example is fully covered by an input workflow."
            % (
                len(materialized_test_sources),
                len(materialized_documentation_sources),
                len(materialized_documentation_example_sources),
                materialized_partial_mappings,
            ),
            "",
            "`mapping_status` labels source-to-feature mapping, while `review_status` and independent workflow links record whether a partial input mapping was reviewed. A row may therefore retain `candidate` while already having `review_status: reviewed_partial` and exact fixture cases/selectors. The documentation denominator is feature pages; `documented_sections` are discovery leads, not separately reviewed workflow units.",
            "",
            "Candidate function and section records carry source path/SHA evidence, exact whole-token signals, family IDs, and family-level selectors. Per-function mapping scope distinguishes reviewed source mappings, function-body signals, and filename candidates. Test modules index function names/lines without copying bodies. These records are backlog leads, not independent executable parity cases; linked workflows cover only their declared partial behavior, and additional behavior needs tailored stimuli and selector review. Rows without a signal remain `review_required`; exclusions include a reason. Benchmark modules are routed to correctness-gated benchmark work.",
            "",
            "`make parity-validate` checks %d API classifications against pinned FastAPI source evidence, every source digest in the coverage matrix, fixture links or exclusion reasons for all %d test modules and %d documentation pages, direct Starlette 1.6.0 dependency edges, and all %d declared observation selectors. It also validates %d input-only design records, including %d per-function test designs, selector evidence, source digests, and the absence of expected result fields. The current materialized-input index contains %d input-only workflows, %d cases, and %d partial source mappings. These are oracle inputs, not target parity results; the remaining design candidates still need review and materialization. Selectors marked `planned` in `observation-selectors.json` still need runner support."
            % (
                counts["api_candidates"],
                counts["test_modules"],
                counts["documentation_pages"],
                selector_count,
                counts["fixture_backlog_items"],
                counts["test_function_designs"],
                materialized_workflows,
                materialized_cases,
                materialized_mappings,
            ),
            "",
            "## Independently authored input workflows",
            "",
            "Reviewed workflow recipes live in `tests/fixtures/input-recipes/parity/*.yaml`. Run `make parity-inputs` to generate ignored JSON under `tests/fixtures/inputs/parity/` before running a workflow. The materialized index binds each recipe, generated input, and workload digest to source modules or documentation pages, exact observed selectors, and a deliberately partial scope. These rows are source-oracle inputs; they do not imply full upstream-suite coverage or FastAPI-RS parity. Each merged source-coverage row also carries explicit ownership links to relevant Starlette-RS operations and requirement IDs, or records that the behavior is outside its current slice.",
            "",
            "| Workflow | Cases | Partial source mappings | Recipe | Workload |",
            "|---|---:|---:|---|---|",
        ]
    )
    for workflow in materialized_index["workflows"]:
        lines.append(
            "| `%s` | %d | %d | [`%s`](../%s) | [`%s`](../%s) |"
            % (
                workflow["id"],
                len(workflow["case_ids"]),
                mappings_by_workflow.get(workflow["id"], 0),
                workflow["recipe_path"],
                workflow["recipe_path"],
                workflow["workload_path"],
                workflow["workload_path"],
            )
        )
    lines.extend(
        [
            "",
            "## FastAPI to Starlette-RS ownership crosswalk",
            "",
            "The merged coverage matrix links each FastAPI test, documented feature, or example to relevant operation and requirement IDs from the sibling Starlette-RS manifest, including its per-target support states. Rows without a matching operation say why they are outside the sibling's current slice. Direct re-export, subclass, and helper edges retain FastAPI and Starlette source locations plus exact sibling review/catalog references. Module namespaces point to the sibling catalog and digest rather than copying every member. FastAPI-RS planning labels are separate from Starlette-RS contract IDs, and no source mapping claims implementation support.",
            "",
            "| FastAPI source rows with feature links | Feature links to sibling operations | Feature links outside current sibling slice | Distinct sibling operations referenced |",
            "|---:|---:|---:|---:|",
            "| %d | %d | %d | %d |"
            % (
                sum(
                    bool(row.get("starlette_rs_contract_mappings"))
                    for row in atlas["coverage_matrix"]
                ),
                len(linked_contract_mappings),
                len(out_of_contract_mappings),
                len(unique_starlette_operations),
            ),
            "",
            "The sibling Starlette-RS manifest, API review, and coverage matrix remain the sole Starlette API inventory. FastAPI's atlas stores only relevant requirement references plus manifest/catalog/review/matrix SHA-256 digests. The inspected Starlette-RS implementation revision is "
            + atlas["authorities"]["starlette_rs"]["implementation_revision"]
            + " ("
            + atlas["authorities"]["starlette_rs"]["implementation_revision_state"]
            + ").",
            "",
            "## Errors, aliases, optional features, and deprecations",
            "",
            "- Error and warning-type candidates: %d, each with source evidence and relevant observation selectors."
            % counts["error_candidates"],
            "- Alias/re-export records: %d." % counts["alias_records"],
            "- Source deprecation records: %d." % counts["source_deprecations"],
            "- Optional FastAPI extras: %s."
            % ", ".join(item["extra"] for item in atlas["optional_features"]),
            "- Python contract: %s; project classifiers: %s; upstream test workflow versions: %s."
            % (
                atlas["authorities"]["python"]["requires_python"],
                ", ".join(atlas["authorities"]["python"]["project_classifiers"]),
                ", ".join(atlas["authorities"]["python"]["test_workflow_versions"]),
            ),
            "",
            "## First end-to-end request/response slice and next backlog",
            "",
            "The implemented first slice is a scoped end-to-end POST `/items/{item_id}` path: Rust-owned app/route construction, path and query parsing, a header-backed dependency, Pydantic request validation, response-model filtering, exact HTTP observations, ordered ASGI send-message types, and selected generated OpenAPI fields. Ten input-only cases are in `tests/fixtures/input-recipes/parity/first-asgi-request.yaml` under the strict schema `tests/fixtures/schemas/python-asgi-workflow-v2.schema.json`; `make parity-inputs` materializes the ignored JSON input, and the independently authored workload is `tests/fixtures/workloads/first_slice.py`. The isolated oracle and target workers and exact comparator are present. This atlas records fixture scope and runner capability; fresh run outcomes belong in ignored `parity-results/` artifacts.",
            "",
            "The ten cases define a narrow first vertical slice. Full FastAPI 0.141.1 API and behavior parity remains incomplete; do not read fixture links or runner availability as broader support evidence.",
            "",
            "## Prioritized project backlog",
            "",
            "Priority 0 records the narrow end-to-end slice already present. The remaining priorities close its contract, source ownership, independent coverage, dependency, licensing, and benchmark gaps before broader support claims.",
            "",
            "| Priority | Workstream | Status | Acceptance condition |",
            "|---:|---|---|---|",
        ]
    )
    for item in atlas["prioritized_backlog"]:
        acceptance = item["acceptance"].replace("|", "\\|")
        lines.append(
            "| %s | `%s` | %s | %s |"
            % (item["priority"], item["id"], item["status"], acceptance)
        )
    lines.extend(["", "## Unresolved points", ""])
    for item in atlas["unresolved_compatibility_points"]:
        lines.append("- **%s** (%s): %s" % (item["id"], item["status"], item["question"]))
    lines.extend(
        [
            "",
            "## Machine-readable authority",
            "",
            "- [`compatibility-atlas.json`](../tests/fixtures/compatibility-atlas.json) is generated by [`build_fastapi_compatibility_atlas.py`](../scripts/build_fastapi_compatibility_atlas.py).",
            "- [`api-inventory.json`](../tests/fixtures/api-inventory.json) remains source inventory input, not support/parity evidence.",
            "- [`fixture-backlog.json`](../tests/fixtures/fixture-backlog.json) is the merged input-only design queue. Its source links, selectors, and no-output invariant are checked by `make parity-validate`; the remaining candidates still need concrete independent workloads before they can execute as parity cases.",
            "- [`observation-selectors.json`](../tests/fixtures/observation-selectors.json) defines exact projection semantics for every selector used by the atlas and backlog; selectors marked `planned` still need runner support.",
            "",
        ]
    )
    return "\n".join(lines)


def _replace_manifest_artifact_block(text: str, artifact_name: str, updates: dict[str, Any]) -> str:
    """Update generated metadata without reformatting the hand-maintained YAML."""
    header = f"  {artifact_name}:\n"
    start = text.find(header)
    if start < 0:
        raise AtlasError(f"manifest source_artifacts has no {artifact_name} block")
    block_start = start + len(header)
    remainder = text[block_start:]
    next_block = re.search(r"^  [A-Za-z0-9_-]+:\n", remainder, re.MULTILINE)
    end = block_start + next_block.start() if next_block else len(text)
    block = text[start:end]
    for key, value in updates.items():
        field = re.compile(rf"^(\s+{re.escape(key)}: ).*$", re.MULTILINE)
        block, replacements = field.subn(rf"\g<1>{value}", block, count=1)
        if replacements != 1:
            raise AtlasError(f"manifest {artifact_name} block is missing generated field {key}")
    return text[:start] + block + text[end:]


def _sync_manifest_artifact_metadata(
    atlas: dict[str, Any], fixture_designs: list[dict[str, Any]]
) -> None:
    """Keep atlas/backlog hashes and counts tied to generated JSON outputs."""
    manifest_path = PROJECT / "tests/fixtures/manifest.yaml"
    atlas_path = PROJECT / "tests/fixtures/compatibility-atlas.json"
    backlog_path = PROJECT / "tests/fixtures/fixture-backlog.json"
    counts = atlas["counts"]
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "compatibility_atlas",
        {
            "schema": atlas["schema"],
            "sha256": sha256(atlas_path),
            "api_candidates": counts["api_candidates"],
            "reviewed_inherited_api_candidates": counts["reviewed_inherited_api_candidates"],
            "reviewed_import_binding_candidates": counts["reviewed_import_binding_candidates"],
            "reviewed_source_api_candidates": counts["reviewed_source_api_candidates"],
            "supported": counts["api_classifications"]["supported"],
            "private_or_internal": counts["api_classifications"]["private/internal"],
            "uncertain": counts["api_classifications"]["uncertain"],
            "alias_records": counts["alias_records"],
            "source_deprecations": counts["source_deprecations"],
            "error_candidates": counts["error_candidates"],
            "optional_features": len(atlas["optional_features"]),
            "starlette_integration_edges": counts["starlette_integration_edges"],
            "documentation_python_examples": counts["documentation_python_examples"],
            "documentation_python_examples_grouped_with_page": counts[
                "documentation_python_examples_grouped_with_page"
            ],
            "documentation_python_examples_excluded": counts[
                "documentation_python_examples_excluded"
            ],
        },
    )
    source_api_review = atlas["api_source_classification_review"]
    source_api_scope = source_api_review["scope"]
    source_api_counts = source_api_scope["recommendation_counts"]
    source_api_selection = source_api_scope["selection"]
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "api_source_classification_review",
        {
            "sha256": source_api_review["sha256"],
            "candidates": source_api_scope["candidate_count"],
            "supported": source_api_counts["supported"],
            "private_or_internal": source_api_counts["private/internal"],
            "uncertain": source_api_counts["uncertain"],
            "candidate_ids_sha256": source_api_scope["candidate_ids_sha256"],
            "uncertain_imported_modules": json.dumps(
                source_api_selection["uncertain_imported_modules"]
            ),
            "uncertain_candidate_id_prefixes": json.dumps(
                source_api_selection["uncertain_candidate_id_prefixes"]
            ),
        },
    )
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "fixture_backlog",
        {
            "sha256": sha256(backlog_path),
            "designs": len(fixture_designs),
            "test_case_designs": sum(len(row.get("case_designs", [])) for row in fixture_designs),
        },
    )
    selector_catalog_path = PROJECT / "tests/fixtures/observation-selectors.json"
    selector_catalog = json.loads(selector_catalog_path.read_text(encoding="utf-8"))
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "observation_selector_catalog",
        {
            "sha256": sha256(selector_catalog_path),
            "selectors": len(selector_catalog["selectors"]),
            "parameterized_selectors": sum(
                "id" not in row for row in selector_catalog["selectors"]
            ),
        },
    )
    inventory_path = PROJECT / "tests/fixtures/api-inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory_counts = inventory["counts"]
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "api_inventory",
        {
            "sha256": sha256(inventory_path),
            "root_exports": inventory_counts["root_exports"],
            "documented_targets": inventory_counts["documented_target_names"],
            "python_source_modules": inventory_counts["python_source_modules"],
            "source_defined_callables": inventory_counts["source_defined_callables"],
            "import_bindings": inventory_counts["import_bindings"],
            "source_deprecations": inventory_counts["symbols_with_source_deprecation_evidence"],
        },
    )
    contract_metadata_start = manifest_text.find("contract_metadata:\n")
    deprecations_start = manifest_text.find("  deprecations:\n", contract_metadata_start)
    if contract_metadata_start < 0 or deprecations_start < 0:
        raise AtlasError("manifest contract_metadata is missing its deprecations record")
    deprecations_header_end = deprecations_start + len("  deprecations:\n")
    deprecations_remainder = manifest_text[deprecations_header_end:]
    next_contract_record = re.search(r"^  [A-Za-z0-9_-]+:\n", deprecations_remainder, re.MULTILINE)
    deprecations_end = (
        deprecations_header_end + next_contract_record.start()
        if next_contract_record
        else len(manifest_text)
    )
    deprecations_block = manifest_text[deprecations_start:deprecations_end]
    deprecations_block, count_replacements = re.subn(
        r"(?m)^(    count: )\d+$",
        rf"\g<1>{len(atlas['deprecations'])}",
        deprecations_block,
        count=1,
    )
    if count_replacements != 1:
        raise AtlasError("manifest contract_metadata deprecations record has no count")
    manifest_text = (
        manifest_text[:deprecations_start]
        + deprecations_block
        + manifest_text[deprecations_end:]
    )
    runtime_core_path = PROJECT / "tests/fixtures/runtime-api-surface-core.json"
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "runtime_api_surface_core",
        {"sha256": sha256(runtime_core_path)},
    )
    runtime_standard_path = PROJECT / "tests/fixtures/runtime-api-surface-standard.json"
    manifest_text = _replace_manifest_artifact_block(
        manifest_text,
        "runtime_api_surface_standard",
        {"sha256": sha256(runtime_standard_path)},
    )
    manifest_path.write_text(manifest_text, encoding="utf-8")


def write_outputs(atlas: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fixture_designs = atlas.pop("_fixture_backlog_designs")
    output.write_text(
        json.dumps(atlas, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    backlog = {
        "schema": "fastapi-rs/fixture-backlog@1",
        "purpose": "Input-only candidate fixture designs derived from the pinned source coverage matrix; not an executable parity input index.",
        "authority": {
            key: atlas["authorities"][key] for key in ("fastapi", "starlette", "python", "pydantic")
        },
        "forbidden_fixture_content": [
            "expected outputs",
            "expected errors",
            "oracle observations",
            "pass/fail claims",
            "timings",
        ],
        "fixture_designs": fixture_designs,
        "first_end_to_end_request_response_slice": {
            **atlas["first_end_to_end_request_response_slice"],
        },
    }
    (PROJECT / "tests/fixtures/fixture-backlog.json").write_text(
        json.dumps(backlog, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if output.resolve() == (PROJECT / "tests/fixtures/compatibility-atlas.json").resolve():
        _sync_manifest_artifact_metadata(atlas, fixture_designs)
    (PROJECT / "docs/COMPATIBILITY_ATLAS.md").write_text(render_markdown(atlas), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fastapi-source", type=Path, default=PROJECT.parent / "fastapi")
    parser.add_argument("--starlette-source", type=Path, default=PROJECT.parent / "starlette")
    parser.add_argument("--starlette-rs-root", type=Path, default=PROJECT.parent / "starlette-rs")
    parser.add_argument(
        "--inventory", type=Path, default=PROJECT / "tests/fixtures/api-inventory.json"
    )
    parser.add_argument(
        "--callable-review",
        type=Path,
        default=PROJECT / "tests/fixtures/api-classification-review.json",
    )
    parser.add_argument(
        "--import-binding-review",
        type=Path,
        default=PROJECT / "tests/fixtures/api-import-binding-classification-review.json",
    )
    parser.add_argument(
        "--source-api-review",
        type=Path,
        default=PROJECT / "tests/fixtures/api-source-classification-review.json",
    )
    parser.add_argument(
        "--public-candidate-review",
        type=Path,
        default=PROJECT / "tests/fixtures/api-public-candidate-classification-review.json",
    )
    parser.add_argument(
        "--output", type=Path, default=PROJECT / "tests/fixtures/compatibility-atlas.json"
    )
    args = parser.parse_args(argv)
    try:
        atlas = generate(args)
        write_outputs(atlas, args.output)
    except (AtlasError, OSError, KeyError, ValueError) as exc:
        print("atlas generation failed: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(atlas["counts"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
