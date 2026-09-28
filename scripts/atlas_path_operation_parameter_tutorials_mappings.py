"""Source-reviewed mappings for the FastAPI path-operation and path-parameter tutorial tests.

Every mapped function points to a unique input-only ASGI workflow and workload.
The sole exclusion is source-backed and remains visible in the function denominator.
FastAPI owns route integration and control flow in Rust; the Python package remains
limited to direct native re-exports and literal __all__. Starlette 1.6.0 is the sole
generic request/response/TestClient contract, provided by Starlette-RS on the target.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"

SOURCE_IDENTITIES = {
    "fastapi": {"version": "0.141.1", "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f"},
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic request, response, route matching, and TestClient contract via Starlette-RS",
    },
    "starlette_rs": {
        "version": "0.1.0",
        "role": "target implementation of the separately owned Starlette 1.6.0 generic contract",
    },
    "python": {
        "implementation": "CPython",
        "version": "3.12.13",
        "role": "pinned isolated oracle runner profile",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "owns BaseModel validation/coercion, Enum validation, field serialization, and model JSON schema generation where exercised",
    },
}

SOURCE_OWNERSHIP = {
    "fastapi": "FastAPI owns decorator/path-operation setup, endpoint parameter analysis, validation orchestration and error mapping, response-model integration, and OpenAPI assembly. FastAPI behavior/control flow belongs in Rust. Python runtime files permit only direct native re-exports and literal __all__.",
    "starlette": "Pinned Starlette 1.6.0 is the sole generic ASGI Request/Response, HTTP route matching/path converter, and TestClient contract. The target supplies this through Starlette-RS 0.1.0; these generic semantics are not assigned to FastAPI.",
    "pydantic": "Pinned Pydantic 2.13.4 owns model parsing/coercion, enum validation, field serialization, and model schema mechanics. FastAPI chooses the parameter/body fields, invokes the pinned Pydantic contract, maps errors, and assembles OpenAPI.",
}

FASTAPI_TEST_MODULES = (
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial001.py",
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial002.py",
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial003.py",
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial004.py",
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial005.py",
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial006.py",
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial007.py",
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial001.py",
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial002.py",
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial002b.py",
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial003_tutorial004.py",
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial005.py",
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial006.py",
    "tests/test_tutorial/test_path_params/test_tutorial001.py",
    "tests/test_tutorial/test_path_params/test_tutorial002.py",
    "tests/test_tutorial/test_path_params/test_tutorial003.py",
    "tests/test_tutorial/test_path_params/test_tutorial003b.py",
    "tests/test_tutorial/test_path_params/test_tutorial004.py",
    "tests/test_tutorial/test_path_params/test_tutorial005.py",
)

SOURCE_GROUPS = {
    "route_registration": [
        (
            "fastapi/routing.py",
            1161,
            1281,
            "FastAPI APIRoute stores endpoint, response, and path-operation configuration.",
        ),
        (
            "fastapi/routing.py",
            2889,
            2971,
            "FastAPI APIRouter.add_api_route forwards route configuration and registers the API "
            "route.",
        ),
    ],
    "openapi_generation": [
        (
            "fastapi/openapi/utils.py",
            287,
            308,
            "FastAPI creates operation metadata including tags, summary, description, operation "
            "ID, and deprecation.",
        ),
        (
            "fastapi/openapi/utils.py",
            159,
            228,
            "FastAPI projects analyzed endpoint parameter fields into OpenAPI parameters.",
        ),
        (
            "fastapi/openapi/utils.py",
            231,
            263,
            "FastAPI projects request-body field schemas and media types into OpenAPI.",
        ),
        (
            "fastapi/openapi/utils.py",
            311,
            540,
            "FastAPI assembles each operation, response, validation response, and openapi_extra "
            "merge.",
        ),
        (
            "fastapi/openapi/utils.py",
            585,
            679,
            "FastAPI combines included API routes into the OpenAPI document.",
        ),
    ],
    "request_dispatch": [
        (
            "fastapi/routing.py",
            375,
            761,
            "FastAPI parses request bodies, solves dependency/path parameters, and builds "
            "endpoint responses.",
        ),
        (
            "fastapi/exception_handlers.py",
            11,
            26,
            "FastAPI maps HTTPException and request validation exceptions to JSON responses.",
        ),
    ],
    "parameter_analysis": [
        (
            "fastapi/dependencies/utils.py",
            271,
            347,
            "FastAPI matches endpoint signature parameters to path names and builds dependant "
            "fields.",
        ),
        (
            "fastapi/dependencies/utils.py",
            381,
            547,
            "FastAPI analyzes endpoint annotations/defaults and constructs path parameter "
            "validation fields.",
        ),
        (
            "fastapi/dependencies/utils.py",
            586,
            731,
            "FastAPI extracts request values, invokes Pydantic field validation, and "
            "accumulates errors.",
        ),
    ],
    "pydantic_bridge": [
        (
            "fastapi/_compat/v2.py",
            114,
            244,
            "FastAPI wraps pinned Pydantic TypeAdapter validation and serialization through "
            "ModelField.",
        ),
        (
            "fastapi/_compat/v2.py",
            254,
            282,
            "FastAPI uses Pydantic-generated JSON schema for OpenAPI field projections.",
        ),
    ],
    "response_dispatch": [
        (
            "fastapi/routing.py",
            375,
            761,
            "FastAPI dispatches endpoint values through response-model validation/serialization "
            "and response construction.",
        )
    ],
    "starlette_http": [
        (
            "starlette/routing.py",
            197,
            258,
            "Starlette 1.6.0 matches the ASGI path, converts route parameters, and dispatches the "
            "selected route.",
        ),
        (
            "starlette/testclient.py",
            327,
            374,
            "Starlette 1.6.0 TestClient captures response status, headers, and body from ASGI "
            "sends.",
        ),
    ],
    "starlette_path": [
        (
            "starlette/routing.py",
            197,
            258,
            "Starlette 1.6.0 compiles route paths and matches/converts path parameters.",
        ),
        (
            "starlette/convertors.py",
            20,
            40,
            "Starlette 1.6.0 string and catch-all path converters preserve path segments.",
        ),
    ],
}

REVIEW_PLANS = {
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial001.py": {
        "test_get": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A "
            "request "
            "to "
            "the "
            "documented "
            "route "
            "exercises "
            "its "
            "path-operation "
            "declaration "
            "and "
            "returned "
            "response.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial001_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial001_test_get.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial001-test-get",
                    "action_ids": ["request-main"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The route has an explicit operationId.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial001_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial001_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial001-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial002.py": {
        "test_get": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A "
            "request "
            "to "
            "the "
            "documented "
            "route "
            "exercises "
            "its "
            "path-operation "
            "declaration "
            "and "
            "returned "
            "response.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial002_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": ["app"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial002_test_get.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial002-test-get",
                    "action_ids": ["request-main"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "FastAPI uses a caller-provided unique-ID callback.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial002_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": ["app"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial002_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial002-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial003.py": {
        "test_get": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A "
            "request "
            "to "
            "the "
            "documented "
            "route "
            "exercises "
            "its "
            "path-operation "
            "declaration "
            "and "
            "returned "
            "response.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial003_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial003_test_get.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial003-test-get",
                    "action_ids": ["request-main"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "A live route is omitted from generated OpenAPI.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial003_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial003_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial003-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial004.py": {
        "test_query_params_str_validations": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The "
            "source "
            "posts "
            "a "
            "valid "
            "Item "
            "with "
            "optional "
            "fields "
            "omitted "
            "and "
            "observes "
            "the "
            "serialized "
            "model "
            "defaults.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial004_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                    "assignments": [],
                }
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "request_dispatch",
                "pydantic_bridge",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial004_test_query_params_str_validations.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial004-test-query-params-str-validations",
                    "action_ids": ["valid-record"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "A "
            "Pydantic "
            "request/response "
            "model "
            "and "
            "operation "
            "summary/description "
            "are "
            "exposed "
            "in "
            "OpenAPI.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial004_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "pydantic_bridge"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial004_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial004-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial005.py": {
        "test_get": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.status"],
            "rationale": "A "
            "request "
            "to "
            "the "
            "documented "
            "route "
            "exercises "
            "its "
            "path-operation "
            "declaration "
            "and "
            "returned "
            "response.",
            "contract_gate": "The "
            "upstream "
            "function "
            "asserts "
            "only "
            "the "
            "HTTP "
            "status. "
            "The "
            "independent "
            "workflow "
            "observes "
            "the "
            "status "
            "and "
            "does "
            "not "
            "claim "
            "the "
            "source "
            "response "
            "payload.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial005_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial005_test_get.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial005-test-get",
                    "action_ids": ["request-main"],
                    "observation_selectors": ["http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "openapi_extra merges a vendor extension into one operation.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial005_py310.py",
                    "functions": ["read_items"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial005_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial005-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial006.py": {
        "test_post": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-body", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The "
            "route "
            "accepts "
            "a "
            "non-JSON "
            "body "
            "as "
            "raw "
            "bytes "
            "and "
            "returns "
            "a "
            "deterministic "
            "summary "
            "without "
            "FastAPI "
            "body-model "
            "validation.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial006_py310.py",
                    "functions": ["create_item"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "request_dispatch",
                "response_dispatch",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial006_test_post.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial006-test-post",
                    "action_ids": ["raw-body"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "An "
            "endpoint "
            "reads "
            "raw "
            "request "
            "bytes "
            "while "
            "openapi_extra "
            "declares "
            "a "
            "custom "
            "request-body "
            "schema.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial006_py310.py",
                    "functions": ["create_item"],
                    "classes": [],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial006_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial006-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial007.py": {
        "test_post": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-body", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "Valid "
            "YAML "
            "is "
            "parsed, "
            "converted "
            "to "
            "the "
            "declared "
            "Pydantic "
            "model, "
            "and "
            "returned "
            "as "
            "JSON.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                    "assignments": [],
                }
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "request_dispatch",
                "pydantic_bridge",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_post.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-post",
                    "action_ids": ["valid-yaml"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_post_broken_yaml": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-body", "public-api-errors"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "Malformed "
            "YAML "
            "is "
            "handled "
            "by "
            "the "
            "documented "
            "exception "
            "mapping "
            "and "
            "returned "
            "with "
            "status "
            "422.",
            "contract_gate": "The "
            "workflow "
            "uses "
            "a "
            "different "
            "path "
            "and "
            "value "
            "and "
            "observes "
            "status "
            "plus "
            "exact "
            "response "
            "bytes. "
            "The "
            "upstream "
            "structured "
            "error "
            "details, "
            "wording, "
            "and "
            "full "
            "validation "
            "matrix "
            "are "
            "not "
            "claimed; "
            "Pydantic "
            "2.13.4 "
            "owns "
            "validation "
            "detail "
            "semantics "
            "where "
            "used.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "request_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_post_broken_yaml.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-post-broken-yaml",
                    "action_ids": ["malformed-yaml"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_post_invalid": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-body", "public-api-errors"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "Well-formed "
            "YAML "
            "that "
            "violates "
            "the "
            "Pydantic "
            "list[str] "
            "field "
            "is "
            "returned "
            "as "
            "a "
            "422 "
            "HTTP "
            "error.",
            "contract_gate": "The "
            "workflow "
            "uses "
            "a "
            "different "
            "path "
            "and "
            "value "
            "and "
            "observes "
            "status "
            "plus "
            "exact "
            "response "
            "bytes. "
            "The "
            "upstream "
            "structured "
            "error "
            "details, "
            "wording, "
            "and "
            "full "
            "validation "
            "matrix "
            "are "
            "not "
            "claimed; "
            "Pydantic "
            "2.13.4 "
            "owns "
            "validation "
            "detail "
            "semantics "
            "where "
            "used.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "request_dispatch", "pydantic_bridge"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_post_invalid.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-post-invalid",
                    "action_ids": ["invalid-model-yaml"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "A "
            "custom "
            "YAML "
            "request "
            "parser "
            "converts "
            "parse/model "
            "errors "
            "into "
            "HTTP "
            "responses "
            "and "
            "declares "
            "its "
            "media "
            "type "
            "in "
            "OpenAPI.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                    "assignments": [],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "pydantic_bridge"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial007_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial007-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial001.py": {
        "test_post_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["response-serialization", "status-codes"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A "
            "valid "
            "model "
            "request "
            "exercises "
            "the "
            "explicit "
            "201 "
            "response "
            "status "
            "and "
            "response-model "
            "serialization.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial001_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": [
                "route_registration",
                "request_dispatch",
                "pydantic_bridge",
                "response_dispatch",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial001_test_post_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial001-test-post-items",
                    "action_ids": ["create-record"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "The "
            "operation "
            "schema "
            "includes "
            "the "
            "configured "
            "201 "
            "response "
            "and "
            "model "
            "schema.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial001_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "pydantic_bridge"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial001_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial001-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial002.py": {
        "test_post_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A "
            "model-backed "
            "POST "
            "route "
            "returns "
            "the "
            "accepted "
            "record "
            "while "
            "using "
            "its "
            "operation "
            "tag.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002_py310.py",
                    "functions": ["create_item", "read_items", "read_users"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": [
                "route_registration",
                "request_dispatch",
                "pydantic_bridge",
                "response_dispatch",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002_test_post_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002-test-post-items",
                    "action_ids": ["create-record"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_get_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The tagged collection route returns its independent record list.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002_py310.py",
                    "functions": ["create_item", "read_items", "read_users"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002_test_get_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002-test-get-items",
                    "action_ids": ["read-items"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_get_users": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A second route with a different tag returns a user-shaped collection.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002_py310.py",
                    "functions": ["create_item", "read_items", "read_users"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002_test_get_users.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002-test-get-users",
                    "action_ids": ["read-users"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The "
            "operation "
            "tag "
            "assignments "
            "for "
            "all "
            "three "
            "route "
            "forms "
            "are "
            "represented "
            "in "
            "OpenAPI.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002_py310.py",
                    "functions": ["create_item", "read_items", "read_users"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial002b.py": {
        "test_get_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The "
            "first "
            "route "
            "responds "
            "with "
            "its "
            "independent "
            "item "
            "list "
            "and "
            "uses "
            "an "
            "Enum-valued "
            "tag.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002b_py310.py",
                    "functions": ["get_items", "read_users"],
                    "classes": ["Tags"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002b_test_get_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002b-test-get-items",
                    "action_ids": ["read-items"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_get_users": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The "
            "second "
            "route "
            "responds "
            "with "
            "its "
            "independent "
            "user "
            "list "
            "and "
            "uses "
            "an "
            "Enum-valued "
            "tag.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002b_py310.py",
                    "functions": ["get_items", "read_users"],
                    "classes": ["Tags"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002b_test_get_users.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002b-test-get-users",
                    "action_ids": ["read-users"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The generated operations expose Enum-valued tags as their string values.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial002b_py310.py",
                    "functions": ["get_items", "read_users"],
                    "classes": ["Tags"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial002b_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial002b-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial003_tutorial004.py": {
        "test_post_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The "
            "request "
            "body "
            "is "
            "parsed "
            "by "
            "the "
            "Pydantic "
            "model "
            "and "
            "returned "
            "through "
            "the "
            "model-backed "
            "endpoint.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial003_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                },
                {
                    "path": "docs_src/path_operation_configuration/tutorial004_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                },
            ],
            "source_groups": [
                "route_registration",
                "request_dispatch",
                "pydantic_bridge",
                "response_dispatch",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial003_tutorial004_test_post_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial003-tutorial004-test-post-items",
                    "action_ids": ["create-record"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The "
            "two "
            "OpenAPI "
            "projections "
            "exercise "
            "an "
            "explicit "
            "description "
            "and "
            "a "
            "multiline "
            "endpoint "
            "docstring "
            "description.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial003_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                },
                {
                    "path": "docs_src/path_operation_configuration/tutorial004_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                },
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial003_tutorial004_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial003-tutorial004-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial005.py": {
        "test_query_params_str_validations": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "Omitting "
            "optional "
            "model "
            "fields "
            "yields "
            "the "
            "declared "
            "default "
            "values "
            "in "
            "the "
            "JSON "
            "response.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial005_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": [
                "route_registration",
                "request_dispatch",
                "pydantic_bridge",
                "response_dispatch",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial005_test_query_params_str_validations.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial005-test-query-params-str-validations",
                    "action_ids": ["create-record"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "The operation contains its explicit summary and response description.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial005_py310.py",
                    "functions": ["create_item"],
                    "classes": ["Item"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "pydantic_bridge"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial005_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial005-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_operation_configurations/test_tutorial006.py": {
        "test_query_params_str_validations": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "Independent "
            "requests "
            "cover "
            "all "
            "three "
            "operation "
            "routes "
            "and "
            "their "
            "returned "
            "bodies.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status "
            "and "
            "exact "
            "body "
            "bytes, "
            "which "
            "can "
            "be "
            "stricter "
            "about "
            "JSON "
            "encoding "
            "and "
            "array "
            "order; "
            "the "
            "source "
            "fixture "
            "values "
            "and "
            "route "
            "path "
            "are "
            "not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial006_py310.py",
                    "functions": ["read_items", "read_users", "read_elements"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial006_test_query_params_str_validations.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial006-test-query-params-str-validations",
                    "action_ids": ["read-items", "read-users", "read-elements"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "OpenAPI "
            "records "
            "route "
            "tags "
            "and "
            "the "
            "deprecated "
            "flag "
            "on "
            "the "
            "elements "
            "operation.",
            "contract_gate": "The "
            "upstream "
            "function "
            "compares "
            "a "
            "full "
            "OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes "
            "only "
            "the "
            "listed "
            "JSON "
            "Pointer "
            "projections "
            "from "
            "an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields "
            "and "
            "exact "
            "snapshot "
            "identity "
            "are "
            "not "
            "claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_operation_configuration/tutorial006_py310.py",
                    "functions": ["read_items", "read_users", "read_elements"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_operation_configurations_test_tutorial006_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-operation-configurations-test-tutorial006-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from "
            "a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 "
            "/ "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_params/test_tutorial001.py": {
        "test_get_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "Requests with "
            "numeric-looking and "
            "alphabetic path "
            "segments reach the same "
            "string path parameter.",
            "contract_gate": "The upstream "
            "assertion compares "
            "JSON-decoded "
            "response values. "
            "This independent "
            "workflow observes "
            "status and exact "
            "body bytes, which "
            "can be stricter "
            "about JSON encoding "
            "and array order; "
            "the source fixture "
            "values and route "
            "path are not "
            "reproduced.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial001_py310.py", "functions": ["read_item"]}
            ],
            "source_groups": ["route_registration", "response_dispatch", "starlette_path"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial001_test_get_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial001-test-get-items",
                    "action_ids": ["numeric-string", "text-string"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow generated "
            "from a new "
            "workload file. The "
            "recipe contains "
            "request inputs and "
            "observation "
            "selectors only; it "
            "stores no expected "
            "output. Generic "
            "request/response "
            "transport belongs "
            "to Starlette 1.6.0 "
            "/ Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The string path parameter appears in the operation projection.",
            "contract_gate": "The upstream "
            "function "
            "compares a "
            "full OpenAPI "
            "document "
            "snapshot. This "
            "independent "
            "workflow "
            "observes only "
            "the listed "
            "JSON Pointer "
            "projections "
            "from an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields and "
            "exact snapshot "
            "identity are "
            "not claimed.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial001_py310.py", "functions": ["read_item"]}
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "parameter_analysis",
                "pydantic_bridge",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial001_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial001-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_params/test_tutorial002.py": {
        "test_get_items": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A numeric segment is converted to the endpoint integer parameter.",
            "contract_gate": "The upstream "
            "assertion compares "
            "JSON-decoded "
            "response values. "
            "This independent "
            "workflow observes "
            "status and exact "
            "body bytes, which "
            "can be stricter "
            "about JSON encoding "
            "and array order; "
            "the source fixture "
            "values and route "
            "path are not "
            "reproduced.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial002_py310.py", "functions": ["read_item"]}
            ],
            "source_groups": [
                "route_registration",
                "parameter_analysis",
                "pydantic_bridge",
                "response_dispatch",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial002_test_get_items.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial002-test-get-items",
                    "action_ids": ["valid-integer"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow generated "
            "from a new "
            "workload file. The "
            "recipe contains "
            "request inputs and "
            "observation "
            "selectors only; it "
            "stores no expected "
            "output. Generic "
            "request/response "
            "transport belongs "
            "to Starlette 1.6.0 "
            "/ Starlette-RS.",
        },
        "test_get_items_invalid_id": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "public-api-errors"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A "
            "non-integer "
            "segment "
            "reaches "
            "FastAPI "
            "request "
            "validation "
            "and returns "
            "status 422.",
            "contract_gate": "The "
            "workflow "
            "uses a "
            "different "
            "path and "
            "value "
            "and "
            "observes "
            "status "
            "plus "
            "exact "
            "response "
            "bytes. "
            "The "
            "upstream "
            "structured "
            "error "
            "details, "
            "wording, "
            "and full "
            "validation "
            "matrix "
            "are not "
            "claimed; "
            "Pydantic "
            "2.13.4 "
            "owns "
            "validation "
            "detail "
            "semantics "
            "where "
            "used.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial002_py310.py", "functions": ["read_item"]}
            ],
            "source_groups": [
                "route_registration",
                "parameter_analysis",
                "pydantic_bridge",
                "request_dispatch",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial002_test_get_items_invalid_id.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial002-test-get-items-invalid-id",
                    "action_ids": ["invalid-integer"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a "
            "new "
            "workload "
            "file. "
            "The "
            "recipe "
            "contains "
            "request "
            "inputs "
            "and "
            "observation "
            "selectors "
            "only; "
            "it "
            "stores "
            "no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs "
            "to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "The path parameter schema reports an integer type.",
            "contract_gate": "The upstream "
            "function "
            "compares a "
            "full OpenAPI "
            "document "
            "snapshot. This "
            "independent "
            "workflow "
            "observes only "
            "the listed "
            "JSON Pointer "
            "projections "
            "from an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields and "
            "exact snapshot "
            "identity are "
            "not claimed.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial002_py310.py", "functions": ["read_item"]}
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "parameter_analysis",
                "pydantic_bridge",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial002_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial002-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_params/test_tutorial003.py": {
        "test_get_users": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The workflow requests "
            "both the reserved "
            "static segment and an "
            "ordinary dynamic "
            "segment.",
            "contract_gate": "The upstream "
            "assertion compares "
            "JSON-decoded "
            "response values. "
            "This independent "
            "workflow observes "
            "status and exact "
            "body bytes, which "
            "can be stricter "
            "about JSON encoding "
            "and array order; "
            "the source fixture "
            "values and route "
            "path are not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial003_py310.py",
                    "functions": ["read_user_me", "read_user"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch", "starlette_path"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial003_test_get_users.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial003-test-get-users",
                    "action_ids": ["reserved-user", "dynamic-user"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow generated "
            "from a new "
            "workload file. The "
            "recipe contains "
            "request inputs and "
            "observation "
            "selectors only; it "
            "stores no expected "
            "output. Generic "
            "request/response "
            "transport belongs "
            "to Starlette 1.6.0 "
            "/ Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The static and "
            "parameterized path "
            "operations are "
            "independently "
            "selected from "
            "OpenAPI.",
            "contract_gate": "The upstream "
            "function "
            "compares a "
            "full OpenAPI "
            "document "
            "snapshot. This "
            "independent "
            "workflow "
            "observes only "
            "the listed "
            "JSON Pointer "
            "projections "
            "from an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields and "
            "exact snapshot "
            "identity are "
            "not claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial003_py310.py",
                    "functions": ["read_user_me", "read_user"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation", "parameter_analysis"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial003_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial003-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_params/test_tutorial003b.py": {
        "test_get_users": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "The request observes "
            "the response from the "
            "first of two duplicate "
            "path registrations.",
            "contract_gate": "The upstream "
            "assertion compares "
            "JSON-decoded "
            "response values. "
            "This independent "
            "workflow observes "
            "status and exact "
            "body bytes, which "
            "can be stricter "
            "about JSON "
            "encoding and array "
            "order; the source "
            "fixture values and "
            "route path are not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial003b_py310.py",
                    "functions": ["read_users", "read_users2"],
                }
            ],
            "source_groups": ["route_registration", "response_dispatch", "starlette_path"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial003b_test_get_users.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial003b-test-get-users",
                    "action_ids": ["duplicate-path"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated from a "
            "new workload "
            "file. The recipe "
            "contains request "
            "inputs and "
            "observation "
            "selectors only; "
            "it stores no "
            "expected output. "
            "Generic "
            "request/response "
            "transport belongs "
            "to Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_read_users2": {
            "review_status": "reviewed_excluded",
            "feature_ids": [],
            "observation_selectors": [],
            "exclusion_reason": "The upstream "
            "test directly "
            "calls the "
            "docs-only "
            "async helper "
            "`read_users2()` "
            "with "
            "`asyncio.run` "
            "and checks "
            "its Python "
            "list return. "
            "It sends no "
            "HTTP/ASGI "
            "request and "
            "does not call "
            "a FastAPI "
            "public API. "
            "Reproducing "
            "it would make "
            "a docs "
            "example "
            "helper into a "
            "public target "
            "endpoint, so "
            "it is "
            "excluded from "
            "the "
            "compatibility "
            "input "
            "denominator.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial003b_py310.py",
                    "functions": ["read_users", "read_users2"],
                }
            ],
            "source_groups": [],
            "workflow_cases": [],
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "The generated "
            "path item for the "
            "duplicate GET "
            "route is selected "
            "as an OpenAPI "
            "projection.",
            "contract_gate": "The upstream "
            "function "
            "compares a "
            "full OpenAPI "
            "document "
            "snapshot. "
            "This "
            "independent "
            "workflow "
            "observes only "
            "the listed "
            "JSON Pointer "
            "projections "
            "from an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields and "
            "exact "
            "snapshot "
            "identity are "
            "not claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial003b_py310.py",
                    "functions": ["read_users", "read_users2"],
                }
            ],
            "source_groups": ["route_registration", "openapi_generation"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial003b_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial003b-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_params/test_tutorial004.py": {
        "test_file_path": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A slash-separated path "
            "value is captured by "
            "the catch-all path "
            "converter.",
            "contract_gate": "The upstream "
            "assertion compares "
            "JSON-decoded "
            "response values. "
            "This independent "
            "workflow observes "
            "status and exact "
            "body bytes, which "
            "can be stricter "
            "about JSON encoding "
            "and array order; "
            "the source fixture "
            "values and route "
            "path are not "
            "reproduced.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial004_py310.py", "functions": ["read_file"]}
            ],
            "source_groups": ["route_registration", "response_dispatch", "starlette_path"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial004_test_file_path.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial004-test-file-path",
                    "action_ids": ["nested-path"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow generated "
            "from a new "
            "workload file. The "
            "recipe contains "
            "request inputs and "
            "observation "
            "selectors only; it "
            "stores no expected "
            "output. Generic "
            "request/response "
            "transport belongs "
            "to Starlette 1.6.0 "
            "/ Starlette-RS.",
        },
        "test_root_file_path": {
            "review_status": "reviewed_partial",
            "feature_ids": ["app-routing", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A leading slash "
            "after the files "
            "prefix remains "
            "part of the "
            "captured path "
            "value.",
            "contract_gate": "The upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. This "
            "independent "
            "workflow "
            "observes "
            "status and "
            "exact body "
            "bytes, which "
            "can be "
            "stricter about "
            "JSON encoding "
            "and array "
            "order; the "
            "source fixture "
            "values and "
            "route path are "
            "not "
            "reproduced.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial004_py310.py", "functions": ["read_file"]}
            ],
            "source_groups": ["route_registration", "response_dispatch", "starlette_path"],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial004_test_root_file_path.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial004-test-root-file-path",
                    "action_ids": ["leading-slash-path"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
            "rationale": "OpenAPI includes "
            "the catch-all "
            "parameter as a "
            "required string "
            "path parameter.",
            "contract_gate": "The upstream "
            "function "
            "compares a "
            "full OpenAPI "
            "document "
            "snapshot. This "
            "independent "
            "workflow "
            "observes only "
            "the listed "
            "JSON Pointer "
            "projections "
            "from an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields and "
            "exact snapshot "
            "identity are "
            "not claimed.",
            "doc_sources": [
                {"path": "docs_src/path_params/tutorial004_py310.py", "functions": ["read_file"]}
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "parameter_analysis",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial004_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial004-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": ["http.status", "openapi.document", "openapi.paths"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
    },
    "tests/test_tutorial/test_path_params/test_tutorial005.py": {
        "test_get_enums_alexnet": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A declared enum path value is accepted and reaches the endpoint.",
            "contract_gate": "The "
            "upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. "
            "This "
            "independent "
            "workflow "
            "observes "
            "status and "
            "exact body "
            "bytes, "
            "which can "
            "be stricter "
            "about JSON "
            "encoding "
            "and array "
            "order; the "
            "source "
            "fixture "
            "values and "
            "route path "
            "are not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial005_py310.py",
                    "functions": ["get_model"],
                    "classes": ["ModelName"],
                }
            ],
            "source_groups": [
                "route_registration",
                "parameter_analysis",
                "pydantic_bridge",
                "response_dispatch",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_get_enums_alexnet.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-get-enums-alexnet",
                    "action_ids": ["valid-choice-a"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_get_enums_lenet": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A second declared enum value is accepted by the same path parameter.",
            "contract_gate": "The upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. This "
            "independent "
            "workflow "
            "observes "
            "status and "
            "exact body "
            "bytes, which "
            "can be "
            "stricter "
            "about JSON "
            "encoding and "
            "array order; "
            "the source "
            "fixture "
            "values and "
            "route path "
            "are not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial005_py310.py",
                    "functions": ["get_model"],
                    "classes": ["ModelName"],
                }
            ],
            "source_groups": [
                "route_registration",
                "parameter_analysis",
                "pydantic_bridge",
                "response_dispatch",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_get_enums_lenet.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-get-enums-lenet",
                    "action_ids": ["valid-choice-b"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_get_enums_resnet": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "response-serialization"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "A third declared enum value is accepted by the same path parameter.",
            "contract_gate": "The upstream "
            "assertion "
            "compares "
            "JSON-decoded "
            "response "
            "values. This "
            "independent "
            "workflow "
            "observes "
            "status and "
            "exact body "
            "bytes, which "
            "can be "
            "stricter "
            "about JSON "
            "encoding and "
            "array order; "
            "the source "
            "fixture "
            "values and "
            "route path "
            "are not "
            "reproduced.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial005_py310.py",
                    "functions": ["get_model"],
                    "classes": ["ModelName"],
                }
            ],
            "source_groups": [
                "route_registration",
                "parameter_analysis",
                "pydantic_bridge",
                "response_dispatch",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_get_enums_resnet.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-get-enums-resnet",
                    "action_ids": ["valid-choice-c"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_get_enums_invalid": {
            "review_status": "reviewed_partial",
            "feature_ids": ["request-validation", "public-api-errors"],
            "observation_selectors": ["http.body.bytes", "http.status"],
            "rationale": "An undeclared enum path value is rejected with status 422.",
            "contract_gate": "The "
            "workflow "
            "uses a "
            "different "
            "path and "
            "value and "
            "observes "
            "status plus "
            "exact "
            "response "
            "bytes. The "
            "upstream "
            "structured "
            "error "
            "details, "
            "wording, "
            "and full "
            "validation "
            "matrix are "
            "not "
            "claimed; "
            "Pydantic "
            "2.13.4 owns "
            "validation "
            "detail "
            "semantics "
            "where used.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial005_py310.py",
                    "functions": ["get_model"],
                    "classes": ["ModelName"],
                }
            ],
            "source_groups": [
                "route_registration",
                "parameter_analysis",
                "pydantic_bridge",
                "request_dispatch",
                "starlette_path",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_get_enums_invalid.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-get-enums-invalid",
                    "action_ids": ["invalid-choice"],
                    "observation_selectors": ["http.body.bytes", "http.status"],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
        "test_openapi_schema": {
            "review_status": "reviewed_partial",
            "feature_ids": ["openapi-docs"],
            "observation_selectors": [
                "http.status",
                "openapi.document",
                "openapi.paths",
                "openapi.request_schema",
            ],
            "rationale": "The path parameter and referenced enum schema are selected from OpenAPI.",
            "contract_gate": "The upstream "
            "function "
            "compares a "
            "full OpenAPI "
            "document "
            "snapshot. This "
            "independent "
            "workflow "
            "observes only "
            "the listed "
            "JSON Pointer "
            "projections "
            "from an "
            "independently "
            "configured "
            "app; "
            "unselected "
            "document "
            "fields and "
            "exact snapshot "
            "identity are "
            "not claimed.",
            "doc_sources": [
                {
                    "path": "docs_src/path_params/tutorial005_py310.py",
                    "functions": ["get_model"],
                    "classes": ["ModelName"],
                }
            ],
            "source_groups": [
                "route_registration",
                "openapi_generation",
                "parameter_analysis",
                "pydantic_bridge",
            ],
            "workflow_cases": [
                {
                    "recipe_path": "tests/fixtures/input-recipes/parity/path-operation-parameter-tutorials-test_path_params_test_tutorial005_test_openapi_schema.yaml",
                    "case_id": "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial005-test-openapi-schema",
                    "action_ids": ["inspect-openapi"],
                    "observation_selectors": [
                        "http.status",
                        "openapi.document",
                        "openapi.paths",
                        "openapi.request_schema",
                    ],
                }
            ],
            "stimulus_notes": "Independent "
            "input-only "
            "workflow "
            "generated "
            "from a new "
            "workload "
            "file. The "
            "recipe "
            "contains "
            "request "
            "inputs and "
            "observation "
            "selectors "
            "only; it "
            "stores no "
            "expected "
            "output. "
            "Generic "
            "request/response "
            "transport "
            "belongs to "
            "Starlette "
            "1.6.0 / "
            "Starlette-RS.",
        },
    },
}


def _source_root(path: str) -> Path:
    return STARLETTE_ROOT if path.startswith("starlette/") else FASTAPI_ROOT


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    source = _source_root(path) / path
    if not source.is_file():
        raise FileNotFoundError(f"missing pinned source evidence: {path}")
    lines = source.read_text(encoding="utf-8").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise ValueError(f"invalid source span {path}:{start}-{end}")
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _definition_span(path: str, name: str, node_type: type) -> dict[str, Any]:
    tree = ast.parse((_source_root(path) / path).read_text(encoding="utf-8"))
    matches = [node for node in tree.body if isinstance(node, node_type) and node.name == name]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {name} in {path}; found {len(matches)}")
    node = matches[0]
    start = min(
        [node.lineno, *(decorator.lineno for decorator in getattr(node, "decorator_list", []))]
    )
    return _source(
        path,
        start,
        node.end_lineno or node.lineno,
        f"Pinned FastAPI 0.141.1 documentation source for {name}",
    )


def _assignment_span(path: str, name: str) -> dict[str, Any]:
    tree = ast.parse((_source_root(path) / path).read_text(encoding="utf-8"))
    matches = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                matches.append(node)
    if len(matches) != 1:
        raise ValueError(f"expected one {name} assignment in {path}; found {len(matches)}")
    node = matches[0]
    return _source(
        path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"Pinned FastAPI 0.141.1 docs configuration of {name}",
    )


def _test_span(path: str, function_name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {path}; found {len(matches)}")
    node = matches[0]
    return _source(
        path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"FastAPI 0.141.1 upstream test function {function_name}",
    )


def _docs_sources(plan: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for doc in plan.get("doc_sources", []):
        for name in doc.get("functions", []):
            result.append(
                _definition_span(doc["path"], name, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
        for name in doc.get("classes", []):
            result.append(_definition_span(doc["path"], name, ast.ClassDef))
        for name in doc.get("assignments", []):
            result.append(_assignment_span(doc["path"], name))
    return result


def _function_review(path: str, name: str, plan: dict[str, Any]) -> dict[str, Any]:
    supporting = [_test_span(path, name), *_docs_sources(plan)]
    for group in plan.get("source_groups", []):
        for source_path, start, end, role in SOURCE_GROUPS[group]:
            supporting.append(_source(source_path, start, end, role))
    result = {
        key: value for key, value in plan.items() if key not in {"doc_sources", "source_groups"}
    }
    result["supporting_sources"] = supporting
    if result.get("review_status") == "reviewed_partial":
        result["contract_gate"] = "Partial: " + result.pop("contract_gate")
        result["replace_features"] = True
        links_note = "; ".join(
            f"{link['recipe_path']}::{link['case_id']} actions {', '.join(link['action_ids'])}"
            for link in result["workflow_cases"]
        )
        result["stimulus_notes"] += " Linked workflow: " + links_note + "."
    return result


def _module_entry(path: str, module_plan: dict[str, dict[str, Any]]) -> dict[str, Any]:
    functions = {name: _function_review(path, name, plan) for name, plan in module_plan.items()}
    links = {}
    sources = {}
    for row in functions.values():
        for link in row.get("workflow_cases", []):
            links.setdefault((link["recipe_path"], link["case_id"]), link)
        for source in row.get("supporting_sources", []):
            key = (source["path"], source["start_line"], source["end_line"], source["role"])
            sources.setdefault(key, source)
    selectors = sorted(
        {
            selector
            for row in functions.values()
            for selector in row.get("observation_selectors", [])
        }
    )
    return {
        "rationale": "Source-reviewed FastAPI tutorial test module mapped to independent request/OpenAPI inputs; source-specific limits are recorded per function.",
        "supporting_sources": list(sources.values()),
        "module_observation_selectors": selectors,
        "workflow_cases": list(links.values()),
        "stimulus_notes": "Each included function has a separate recipe, workload file, and case ID. Inputs declare requests and observations only; they store no expected outputs.",
        "functions": functions,
    }


PATH_OPERATION_PARAMETER_TUTORIALS_MAPPINGS = {
    path: _module_entry(path, plan) for path, plan in REVIEW_PLANS.items()
}


def validate_review_mappings() -> dict[str, int]:
    """Validate pinned source spans and recipe/workload links without running them."""
    fastapi_commit = subprocess.check_output(
        ["git", "-C", str(FASTAPI_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    starlette_commit = subprocess.check_output(
        ["git", "-C", str(STARLETTE_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    if fastapi_commit != SOURCE_IDENTITIES["fastapi"]["commit"]:
        raise ValueError(f"FastAPI source identity changed: {fastapi_commit}")
    if starlette_commit != SOURCE_IDENTITIES["starlette"]["commit"]:
        raise ValueError(f"Starlette source identity changed: {starlette_commit}")
    discovered = set()
    for module_dir in (
        "tests/test_tutorial/test_path_operation_advanced_configurations",
        "tests/test_tutorial/test_path_operation_configurations",
        "tests/test_tutorial/test_path_params",
    ):
        discovered.update(
            str(path.relative_to(FASTAPI_ROOT))
            for path in (FASTAPI_ROOT / module_dir).glob("test_*.py")
        )
    if discovered != set(FASTAPI_TEST_MODULES):
        raise ValueError(
            f"source test module denominator changed: missing={sorted(discovered - set(FASTAPI_TEST_MODULES))} extra={sorted(set(FASTAPI_TEST_MODULES) - discovered)}"
        )
    if set(PATH_OPERATION_PARAMETER_TUTORIALS_MAPPINGS) != set(FASTAPI_TEST_MODULES):
        raise ValueError("review mapping does not cover the exact source module set")
    seen_recipes, seen_workloads, seen_cases = set(), set(), set()
    mapped_functions = excluded_functions = 0
    for test_path, module in PATH_OPERATION_PARAMETER_TUTORIALS_MAPPINGS.items():
        tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
        source_functions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        }
        rows = module["functions"]
        if source_functions != set(rows):
            raise ValueError(
                f"function denominator mismatch for {test_path}: missing={sorted(source_functions - set(rows))} extra={sorted(set(rows) - source_functions)}"
            )
        for name, row in rows.items():
            for source in row.get("supporting_sources", []):
                _source(source["path"], source["start_line"], source["end_line"], source["role"])
            if row["review_status"] == "reviewed_excluded":
                if row.get("workflow_cases") or not row.get("exclusion_reason"):
                    raise ValueError(f"invalid exclusion record: {test_path}::{name}")
                excluded_functions += 1
                continue
            links = row.get("workflow_cases", [])
            if len(links) != 1:
                raise ValueError(
                    f"expected exactly one independent workflow for {test_path}::{name}"
                )
            link = links[0]
            recipe_path, case_id = link["recipe_path"], link["case_id"]
            workload_path = None
            if recipe_path in seen_recipes or case_id in seen_cases:
                raise ValueError(f"duplicate input identity: {recipe_path} {case_id}")
            seen_recipes.add(recipe_path)
            seen_cases.add(case_id)
            recipe_file = PROJECT_ROOT / recipe_path
            recipe = yaml.safe_load(recipe_file.read_text(encoding="utf-8"))
            if recipe.get("schema") != "fastapi-rs/python-asgi-workflow@2" or set(recipe) != {
                "schema",
                "workload",
                "cases",
            }:
                raise ValueError(f"recipe schema/key mismatch: {recipe_path}")
            workload_path = recipe["workload"]["file"]
            if workload_path in seen_workloads:
                raise ValueError(f"workload file is reused: {workload_path}")
            seen_workloads.add(workload_path)
            workload_file = PROJECT_ROOT / workload_path
            ast.parse(workload_file.read_text(encoding="utf-8"))
            recipe_cases = recipe["cases"]
            if len(recipe_cases) != 1 or recipe_cases[0].get("case_id") != case_id:
                raise ValueError(f"case identity mismatch: {recipe_path}")
            case = recipe_cases[0]
            actions = {action["action_id"]: action for action in case["actions"]}
            if set(actions) != set(link["action_ids"]):
                raise ValueError(f"action link mismatch: {recipe_path}")
            evidence_paths = {entry["path"] for entry in case.get("source_evidence", [])}
            if test_path not in evidence_paths:
                raise ValueError(f"missing upstream test link: {recipe_path}")
            action_selectors = set()
            for action in actions.values():
                for observation in action.get("observations", []):
                    if observation["kind"] == "http_response":
                        selector_names = {
                            "status": "http.status",
                            "body": "http.body.bytes",
                            "headers": "http.headers.ordered",
                        }
                        action_selectors.update(
                            selector_names[selector] for selector in observation["selectors"]
                        )
                    elif observation["kind"] == "openapi":
                        action_selectors.update(("openapi.document", "openapi.paths"))
                        if any(
                            "/components/schemas" in pointer or "/requestBody" in pointer
                            for pointer in observation["json_pointers"]
                        ):
                            action_selectors.add("openapi.request_schema")
            if set(link["observation_selectors"]) != action_selectors:
                raise ValueError(
                    f"selector link mismatch for {recipe_path}: {link['observation_selectors']} != {sorted(action_selectors)}"
                )
            # Inputs may describe requests and selected observations only.
            serialized = recipe_file.read_text(encoding="utf-8").lower()
            if (
                "expected_output" in serialized
                or "expected_response" in serialized
                or "expected_status" in serialized
            ):
                raise ValueError(f"expected result data found in input recipe: {recipe_path}")
            mapped_functions += 1
    return {
        "modules": len(FASTAPI_TEST_MODULES),
        "functions": mapped_functions + excluded_functions,
        "mapped_functions": mapped_functions,
        "excluded_functions": excluded_functions,
        "recipes": len(seen_recipes),
        "workloads": len(seen_workloads),
    }
