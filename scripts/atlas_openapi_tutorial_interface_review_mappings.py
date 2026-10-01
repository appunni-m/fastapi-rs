"""Reviewed input mappings for selected OpenAPI tutorial test modules.

The recipes are independent ASGI stimuli with selected observations only. This
sidecar does not claim live parity and does not copy upstream snapshot values.
FastAPI owns framework routing integration and OpenAPI assembly; Starlette 1.6.0
is the sole generic ASGI, response, mount, and TestClient contract; Pydantic
2.13.4 owns model schema generation.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "pinned development/source oracle only; no target runtime import or dependency",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI routing, mount, HTTP response, and TestClient contract",
    },
    "starlette_rs": {
        "version": "0.1.0",
        "commit": "c0ca7706d068b00c090fdf3a60123431085be26d",
        "contract_id": "starlette-1.6.0-asgi-http-config-session-slice",
        "role": "generic Starlette contract implementation owned by the sibling project",
    },
    "python": {
        "implementation": "CPython",
        "version": "3.12.13",
        "minimum_for_selected_tutorial_apps": "3.10",
    },
    "pydantic": {
        "version": "2.13.4",
        "pydantic_core_version": "2.46.4",
        "role": "model validation/serialization and model JSON Schema generation",
    },
}

VERSION_CONSTRAINTS = {
    "source_oracle": "FastAPI 0.141.1 at 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "generic_contract": "Starlette 1.6.0 at 4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    "generic_target_contract": "Starlette-RS 0.1.0 at c0ca7706d068b00c090fdf3a60123431085be26d",
    "python": "CPython 3.12.13 oracle; selected _py310 documentation apps require Python >=3.10",
    "pydantic": "Pydantic 2.13.4 with pydantic-core 2.46.4",
    "separate_input_output_schemas": "FastAPI support is documented as added in 0.102.0; this review pins 0.141.1",
}

VERSION_CONSTRAINT_SOURCES = [
    {
        "path": "metadata.yaml",
        "start_line": 7,
        "end_line": 19,
        "role": "Repository source authority pins FastAPI, the CPython oracle, and Pydantic versions",
    },
    {
        "path": "metadata.yaml",
        "start_line": 26,
        "end_line": 33,
        "role": "Repository source authority pins Starlette 1.6.0 and its source commit",
    },
    {
        "path": "metadata.yaml",
        "start_line": 109,
        "end_line": 115,
        "role": "Repository source authority pins the Starlette-RS distribution, contract, and reviewed revision",
    },
    {
        "path": "pyproject.toml",
        "start_line": 6,
        "end_line": 10,
        "role": "Target project declares its supported Python floor",
    },
    {
        "path": "pyproject.toml",
        "start_line": 5,
        "end_line": 12,
        "source_root": "fastapi",
        "role": "Pinned FastAPI source declares its Python minimum",
    },
    {
        "path": "docs/en/docs/how-to/separate-openapi-schemas.md",
        "start_line": 88,
        "end_line": 91,
        "role": "FastAPI docs state separate_input_output_schemas support began in version 0.102.0",
    },
]

API_NAME_REVIEW = {
    "aliases": [
        {
            "public_name": "fastapi.testclient.TestClient",
            "identity_alias_of": "starlette.testclient.TestClient",
            "source": {
                "path": "fastapi/testclient.py",
                "start_line": 1,
                "end_line": 1,
            },
            "ownership": "Direct re-export; client semantics stay with Starlette 1.6.0 / Starlette-RS.",
        }
    ],
    "deprecated_names_exercised": [],
    "nearby_deprecations_outside_scope": [
        {
            "name": "FastAPI(openapi_prefix=...)",
            "reason": "The constructor contains a deprecation warning, but none of the selected tutorial tests or workloads use openapi_prefix.",
            "source": {
                "path": "fastapi/applications.py",
                "start_line": 929,
                "end_line": 936,
            },
        }
    ],
}

OWNERSHIP_NOTES = [
    "Rust owns FastAPI route behavior, automatic docs registration, custom OpenAPI integration, callback/webhook projection, and schema-mode selection.",
    "Python runtime files remain direct native re-exports plus literal __all__; FastAPI behavior and control flow stay in Rust.",
    "Starlette 1.6.0 is the sole generic routing, mount, HTTP response, and TestClient oracle; the target delegates this contract to Starlette-RS.",
    "Pydantic 2.13.4 owns model validation/serialization and JSON Schema generation; FastAPI selects and inserts model schemas into OpenAPI.",
    "The disabled-docs input uses the documented empty openapi_url setting directly. It does not claim to test pydantic-settings environment parsing or module reload behavior.",
]

_CONDITIONAL_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-conditional-interface-review.yaml"
)
_SWAGGER_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-swagger-parameters-interface-review.yaml"
)
_CALLBACK_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-callback-interface-review.yaml"
)
_WEBHOOK_RECIPE = "tests/fixtures/input-recipes/parity/atlas-openapi-webhook-interface-review.yaml"
_SCHEMA_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-schema-modes-interface-review.yaml"
)
_CUSTOM_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-custom-schema-cache-interface-review.yaml"
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_source(test_path: str, function_name: str) -> dict[str, Any]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    starts = [node.lineno, *(item.lineno for item in node.decorator_list)]
    return _source(
        test_path,
        min(starts),
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test function {function_name} and its assertions",
    )


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


def _feature_status(feature_ids: tuple[str, ...], status: str, note: str) -> dict[str, Any]:
    return {feature_id: {"status": status, "scope": note} for feature_id in feature_ids}


def _mapped(
    test_path: str,
    function_name: str,
    *,
    feature_ids: tuple[str, ...],
    link: dict[str, Any],
    rationale: str,
    contract_gate: str,
    supporting_sources: tuple[dict[str, Any], ...],
    openapi_observation_scope: str = "not_applicable",
) -> dict[str, Any]:
    return {
        "mapping_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "feature_status": _feature_status(
            feature_ids,
            "input_mapped_reviewed_partial",
            rationale,
        ),
        "observation_selectors": list(link["observation_selectors"]),
        "openapi_observation_scope": openapi_observation_scope,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": f"Partial: {contract_gate}",
        "workflow_cases": [link],
        "stimulus_notes": (
            "The linked recipe and Python workload are independently authored. The recipe contains request inputs and selectors only, with no expected status, body, or OpenAPI values."
        ),
        "supporting_sources": [
            _test_function_source(test_path, function_name),
            *supporting_sources,
        ],
    }


def _excluded(
    test_path: str,
    function_name: str,
    *,
    feature_ids: tuple[str, ...],
    reason: str,
    owner: str,
    supporting_sources: tuple[dict[str, Any], ...],
    related_workflows: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    return {
        "mapping_status": "reviewed_excluded_from_asgi_input_lane",
        "feature_ids": list(feature_ids),
        "feature_status": _feature_status(
            feature_ids,
            "excluded_from_asgi_input_lane",
            reason,
        ),
        "observation_selectors": [],
        "openapi_observation_scope": "not_applicable",
        "source_span": _test_function_source(test_path, function_name),
        "exclusion": {"reason": reason, "owner": owner},
        "related_workflows": list(related_workflows),
        "supporting_sources": list(supporting_sources),
    }


_FASTAPI_SETUP = _source(
    "fastapi/applications.py",
    1105,
    1158,
    "FastAPI registers the OpenAPI, Swagger UI, OAuth redirect, and ReDoc routes based on configured URLs",
)
_FASTAPI_OPENAPI_CACHE = _source(
    "fastapi/applications.py",
    1070,
    1103,
    "FastAPI generates and caches the schema, passing routes, webhooks, and the separate-schema setting to get_openapi",
)
_FASTAPI_WEBHOOKS = _source(
    "fastapi/applications.py",
    937,
    948,
    "FastAPI exposes its documentation-only webhook APIRouter on app.webhooks",
)
_FASTAPI_GET_OPENAPI = _source(
    "fastapi/openapi/utils.py",
    585,
    679,
    "FastAPI assembles metadata, routes, callback operations, webhook operations, and model definitions into OpenAPI",
)
_FASTAPI_CALLBACKS = _source(
    "fastapi/openapi/utils.py",
    386,
    402,
    "FastAPI projects callback APIRoute definitions under their owning path operation",
)
_FASTAPI_ROUTE_CALLBACKS = _source(
    "fastapi/routing.py",
    1187,
    1223,
    "FastAPI APIRoute accepts callback routes and stores route configuration for OpenAPI projection",
)
_FASTAPI_REQUEST_HANDLER = _source(
    "fastapi/routing.py",
    375,
    455,
    "FastAPI builds request handling, resolves route inputs, and invokes the endpoint",
)
_FASTAPI_SCHEMA_BRIDGE = _source(
    "fastapi/_compat/v2.py",
    285,
    346,
    "FastAPI selects validation and serialization fields and delegates definitions to Pydantic GenerateJsonSchema",
)
_FASTAPI_SCHEMA_NAMES = _source(
    "fastapi/_compat/v2.py",
    425,
    435,
    "FastAPI normalizes Pydantic model names for OpenAPI schema references",
)
_FASTAPI_SWAGGER_HTML = _source(
    "fastapi/openapi/docs.py",
    22,
    194,
    "FastAPI merges Swagger UI defaults with supplied settings and emits the selected JSON settings into HTML",
)
_FASTAPI_REDOC_HTML = _source(
    "fastapi/openapi/docs.py",
    197,
    299,
    "FastAPI generates ReDoc HTML using the configured OpenAPI URL and title",
)
_FASTAPI_TESTCLIENT_ALIAS = _source(
    "fastapi/testclient.py",
    1,
    1,
    "FastAPI re-exports Starlette TestClient by identity",
)
_STARLETTE_TESTCLIENT = _source(
    "starlette/testclient.py",
    277,
    340,
    "Starlette 1.6.0 TestClient owns generic HTTP request and ASGI transport behavior used by upstream tests",
)
_STARLETTE_RESPONSES = _source(
    "starlette/responses.py",
    29,
    75,
    "Starlette 1.6.0 owns generic Response status, headers, body rendering, and ASGI delivery",
)
_STARLETTE_MOUNT = _source(
    "starlette/routing.py",
    370,
    445,
    "Starlette 1.6.0 owns generic Mount prefix matching and child root_path scope construction used by independent mounted workloads",
)
_FASTAPI_DEPRECATED_PREFIX = _source(
    "fastapi/applications.py",
    929,
    936,
    "FastAPI marks openapi_prefix deprecated; the selected tutorials do not use it",
)

_HTTP = ("http.status", "http.body.bytes")
_STATUS = ("http.status",)
_DOCUMENT = ("http.status", "openapi.document")


OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS = {
    "tests/test_tutorial/test_conditional_openapi/test_tutorial001.py": {
        "feature_ids": ["app-routing", "openapi-docs", "response-serialization"],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "response-serialization"),
            "reviewed_partial_input_mapping",
            "Disabled and default docs/schema registration are mapped; settings parsing and module reload are not.",
        ),
        "rationale": "The source toggles the OpenAPI URL through a setting, checks the hidden docs/OpenAPI paths, the ordinary root route, and default Swagger UI/ReDoc/OpenAPI availability.",
        "supporting_sources": [_FASTAPI_SETUP, _FASTAPI_TESTCLIENT_ALIAS, _STARLETTE_TESTCLIENT],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "functions": {
            "test_disable_openapi": _mapped(
                "tests/test_tutorial/test_conditional_openapi/test_tutorial001.py",
                "test_disable_openapi",
                feature_ids=("openapi-docs",),
                link=_link(
                    _CONDITIONAL_RECIPE,
                    "fastapi.atlas-openapi-tutorial.conditional-hidden-docs",
                    ("hidden-openapi", "hidden-swagger-ui", "hidden-redoc"),
                    _STATUS,
                ),
                rationale="Three requests target the disabled OpenAPI, Swagger UI, and ReDoc routes. The workload uses FastAPI(openapi_url='') to take the same registration-off path; it does not cover environment parsing by pydantic-settings or importlib.reload.",
                contract_gate="The source sets OPENAPI_URL to an empty string and checks 404 statuses. The independent workflow checks the same route availability under a mounted application but does not reproduce settings loading, module reload, response text, or the exact root paths.",
                supporting_sources=(
                    _FASTAPI_SETUP,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_MOUNT,
                ),
            ),
            "test_root": _mapped(
                "tests/test_tutorial/test_conditional_openapi/test_tutorial001.py",
                "test_root",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _CONDITIONAL_RECIPE,
                    "fastapi.atlas-openapi-tutorial.independent-root-route",
                    ("landing-response",),
                    _HTTP,
                ),
                rationale="The request reaches an ordinary GET root route while OpenAPI/docs are configured on the same workload app.",
                contract_gate="The source checks status and parsed JSON equality for its tutorial payload. The independent workload uses a distinct message and compares raw bytes, so it maps route/response shape, not the source literal or TestClient JSON decoding.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                ),
            ),
            "test_default_openapi": _mapped(
                "tests/test_tutorial/test_conditional_openapi/test_tutorial001.py",
                "test_default_openapi",
                feature_ids=("openapi-docs",),
                link=_link(
                    _CONDITIONAL_RECIPE,
                    "fastapi.atlas-openapi-tutorial.default-docs-and-schema",
                    ("default-swagger-ui", "default-redoc", "default-openapi-document"),
                    ("http.status", "openapi.document"),
                ),
                rationale="The three actions check the default docs routes and select the complete OpenAPI JSON document at the empty JSON pointer.",
                contract_gate="The source checks docs statuses and a full-document snapshot. The independent full-document observation covers all generated fields for a separately authored route; docs HTML is status-only, matching the source assertions.",
                supporting_sources=(
                    _FASTAPI_SETUP,
                    _FASTAPI_OPENAPI_CACHE,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                ),
                openapi_observation_scope="full_document",
            ),
        },
    },
    "tests/test_tutorial/test_configure_swagger_ui/test_tutorial001.py": {
        "feature_ids": ["app-routing", "openapi-docs", "response-serialization"],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "response-serialization"),
            "reviewed_partial_input_mapping",
            "One configured Swagger UI variant and its member route are selected; browser execution is outside the ASGI HTML contract.",
        ),
        "rationale": "The tutorial checks Swagger UI configuration JSON embedded in generated HTML and an independent user route.",
        "supporting_sources": [
            _FASTAPI_SETUP,
            _FASTAPI_SWAGGER_HTML,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes"],
        "functions": {
            "test_swagger_ui": _mapped(
                "tests/test_tutorial/test_configure_swagger_ui/test_tutorial001.py",
                "test_swagger_ui",
                feature_ids=("openapi-docs",),
                link=_link(
                    _SWAGGER_RECIPE,
                    "fastapi.atlas-openapi-tutorial.syntax-highlighting-disabled",
                    ("syntax-off-swagger-ui",),
                    _HTTP,
                ),
                rationale="The docs HTML action uses syntaxHighlight=False and contains the default Swagger UI parameter set selected by the source assertions.",
                contract_gate="The source searches for selected text fragments. The ASGI recipe selects status and complete HTML bytes, which is stricter and also includes mounted-path URL effects; it does not execute Swagger UI JavaScript in a browser.",
                supporting_sources=(
                    _FASTAPI_SETUP,
                    _FASTAPI_SWAGGER_HTML,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _STARLETTE_MOUNT,
                ),
            ),
            "test_get_users": _mapped(
                "tests/test_tutorial/test_configure_swagger_ui/test_tutorial001.py",
                "test_get_users",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _SWAGGER_RECIPE,
                    "fastapi.atlas-openapi-tutorial.syntax-highlighting-route",
                    ("syntax-off-member-route",),
                    _HTTP,
                ),
                rationale="A distinct member route is called on the app with syntax highlighting disabled.",
                contract_gate="The source checks status and parsed JSON for /users/foo. The workload uses a different route name and path value, and compares exact response bytes instead of TestClient JSON decoding.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _STARLETTE_MOUNT,
                ),
            ),
        },
    },
    "tests/test_tutorial/test_configure_swagger_ui/test_tutorial002.py": {
        "feature_ids": ["app-routing", "openapi-docs", "response-serialization"],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "response-serialization"),
            "reviewed_partial_input_mapping",
            "Nested Swagger UI theme options and the member route are observed; browser rendering is not.",
        ),
        "rationale": "The source configures nested syntaxHighlight.theme data and verifies that FastAPI serializes it into Swagger UI HTML while retaining default parameters.",
        "supporting_sources": [
            _FASTAPI_SETUP,
            _FASTAPI_SWAGGER_HTML,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes"],
        "functions": {
            "test_swagger_ui": _mapped(
                "tests/test_tutorial/test_configure_swagger_ui/test_tutorial002.py",
                "test_swagger_ui",
                feature_ids=("openapi-docs",),
                link=_link(
                    _SWAGGER_RECIPE,
                    "fastapi.atlas-openapi-tutorial.nested-theme-configuration",
                    ("theme-swagger-ui",),
                    _HTTP,
                ),
                rationale="The docs HTML action carries a nested syntaxHighlight object, exercising JSON-compatible nested parameter encoding and default merging.",
                contract_gate="The source asserts selected HTML substrings and absence of the flat false setting. The independent action compares complete HTML bytes for a separately named theme; it does not measure browser color rendering.",
                supporting_sources=(
                    _FASTAPI_SETUP,
                    _FASTAPI_SWAGGER_HTML,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _STARLETTE_MOUNT,
                ),
            ),
            "test_get_users": _mapped(
                "tests/test_tutorial/test_configure_swagger_ui/test_tutorial002.py",
                "test_get_users",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _SWAGGER_RECIPE,
                    "fastapi.atlas-openapi-tutorial.nested-theme-route",
                    ("theme-member-route",),
                    _HTTP,
                ),
                rationale="A member route is called on the separately configured nested-theme app.",
                contract_gate="The source checks a successful /users/foo response and its JSON value. The workload uses an independent route and member value and selects raw bytes, not TestClient JSON decoding.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _STARLETTE_MOUNT,
                ),
            ),
        },
    },
    "tests/test_tutorial/test_configure_swagger_ui/test_tutorial003.py": {
        "feature_ids": ["app-routing", "openapi-docs", "response-serialization"],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "response-serialization"),
            "reviewed_partial_input_mapping",
            "An overridden Swagger UI parameter and member route are observed; browser execution is outside this case.",
        ),
        "rationale": "The source overrides deepLinking, asserts the new value is present and the old value is absent, and checks remaining defaults.",
        "supporting_sources": [
            _FASTAPI_SETUP,
            _FASTAPI_SWAGGER_HTML,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes"],
        "functions": {
            "test_swagger_ui": _mapped(
                "tests/test_tutorial/test_configure_swagger_ui/test_tutorial003.py",
                "test_swagger_ui",
                feature_ids=("openapi-docs",),
                link=_link(
                    _SWAGGER_RECIPE,
                    "fastapi.atlas-openapi-tutorial.default-parameter-override",
                    ("deep-link-off-swagger-ui",),
                    _HTTP,
                ),
                rationale="The docs HTML action selects the complete serialization for an app that overrides deepLinking to false while inheriting other default settings.",
                contract_gate="The source checks presence/absence of selected substrings. The recipe observes all generated HTML bytes but does not separately expose individual toggles or execute the browser UI.",
                supporting_sources=(
                    _FASTAPI_SETUP,
                    _FASTAPI_SWAGGER_HTML,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _STARLETTE_MOUNT,
                ),
            ),
            "test_get_users": _mapped(
                "tests/test_tutorial/test_configure_swagger_ui/test_tutorial003.py",
                "test_get_users",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _SWAGGER_RECIPE,
                    "fastapi.atlas-openapi-tutorial.default-parameter-route",
                    ("deep-link-off-member-route",),
                    _HTTP,
                ),
                rationale="A member route is called on the app whose Swagger UI default deepLinking parameter is overridden.",
                contract_gate="The source checks status and parsed JSON on /users/foo. The independent app uses a different endpoint and response data and observes raw bytes.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _STARLETTE_MOUNT,
                ),
            ),
        },
    },
    "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py": {
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "request-validation", "response-serialization"),
            "reviewed_partial_input_mapping",
            "The valid callback-owning route and complete generated document are mapped; direct callback invocation is excluded from this ASGI input lane.",
        ),
        "rationale": "The source exercises a valid POST on a callback-declaring route, direct callback function coverage, and a complete OpenAPI snapshot with the callback operation and model components.",
        "supporting_sources": [
            _FASTAPI_OPENAPI_CACHE,
            _FASTAPI_GET_OPENAPI,
            _FASTAPI_CALLBACKS,
            _FASTAPI_ROUTE_CALLBACKS,
            _FASTAPI_SCHEMA_BRIDGE,
            _FASTAPI_SCHEMA_NAMES,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "functions": {
            "test_get": _mapped(
                "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py",
                "test_get",
                feature_ids=("app-routing", "request-validation", "response-serialization"),
                link=_link(
                    _CALLBACK_RECIPE,
                    "fastapi.atlas-openapi-tutorial.callback-route-request",
                    ("submit-independent-transfer",),
                    _HTTP,
                ),
                rationale="A valid JSON request reaches the route that owns callback metadata; the callback is documentation metadata and is not invoked as an outbound request.",
                contract_gate="The source posts a valid invoice and checks status plus parsed JSON. The independent workload uses a distinct model and payload, observes raw response bytes, and does not perform callback delivery.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_ROUTE_CALLBACKS,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                ),
            ),
            "test_dummy_callback": _excluded(
                "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py",
                "test_dummy_callback",
                feature_ids=("openapi-docs",),
                reason="The function calls the callback endpoint Python function directly with an empty mapping solely for coverage and asserts no returned value. It does not exercise an ASGI request, callback delivery, or an observable OpenAPI value.",
                owner="FastAPI callback function and route composition; direct Python invocation is not an HTTP consumer contract.",
                supporting_sources=(_FASTAPI_CALLBACKS, _FASTAPI_ROUTE_CALLBACKS),
                related_workflows=(
                    _link(
                        _CALLBACK_RECIPE,
                        "fastapi.atlas-openapi-tutorial.callback-documentation",
                        ("callback-openapi-document",),
                        _DOCUMENT,
                    ),
                ),
            ),
            "test_openapi_schema": _mapped(
                "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py",
                "test_openapi_schema",
                feature_ids=("openapi-docs", "request-validation"),
                link=_link(
                    _CALLBACK_RECIPE,
                    "fastapi.atlas-openapi-tutorial.callback-documentation",
                    ("callback-openapi-document",),
                    _DOCUMENT,
                ),
                rationale="The selected empty JSON pointer observes the complete generated OpenAPI document, including callback operation projection and all generated components.",
                contract_gate="The source uses a complete snapshot. The recipe uses a separately authored callback path/model set and selects its entire document, not the source snapshot values. Pydantic supplies model schema fragments.",
                supporting_sources=(
                    _FASTAPI_OPENAPI_CACHE,
                    _FASTAPI_GET_OPENAPI,
                    _FASTAPI_CALLBACKS,
                    _FASTAPI_SCHEMA_BRIDGE,
                    _FASTAPI_SCHEMA_NAMES,
                ),
                openapi_observation_scope="full_document",
            ),
        },
    },
    "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py": {
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "request-validation", "response-serialization"),
            "reviewed_partial_input_mapping",
            "Webhook schema projection and the adjacent HTTP route are mapped; direct endpoint invocation is excluded from the ASGI input lane.",
        ),
        "rationale": "The source asserts a normal users route, directly invokes a webhook endpoint for coverage, and snapshots OpenAPI containing a documentation-only webhook operation.",
        "supporting_sources": [
            _FASTAPI_WEBHOOKS,
            _FASTAPI_OPENAPI_CACHE,
            _FASTAPI_GET_OPENAPI,
            _FASTAPI_SCHEMA_BRIDGE,
            _FASTAPI_SCHEMA_NAMES,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "functions": {
            "test_get": _mapped(
                "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
                "test_get",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _WEBHOOK_RECIPE,
                    "fastapi.atlas-openapi-tutorial.webhook-adjacent-route",
                    ("read-independent-accounts",),
                    _HTTP,
                ),
                rationale="The action calls the ordinary route adjacent to an OpenAPI webhook declaration.",
                contract_gate="The source checks status and parsed JSON for /users/. The independent workload uses another route and values and selects raw bytes; TestClient request and JSON decoding remain Starlette-RS behavior.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                ),
            ),
            "test_dummy_webhook": _excluded(
                "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
                "test_dummy_webhook",
                feature_ids=("openapi-docs",),
                reason="The function indexes app.webhooks.routes, checks the Python object is APIRoute, and calls route.endpoint({}) directly for coverage. It sends no ASGI request and asserts no endpoint result.",
                owner="FastAPI app.webhooks/APIRoute identity and route composition; direct Python invocation has no ASGI observation.",
                supporting_sources=(_FASTAPI_WEBHOOKS, _FASTAPI_ROUTE_CALLBACKS),
                related_workflows=(
                    _link(
                        _WEBHOOK_RECIPE,
                        "fastapi.atlas-openapi-tutorial.webhook-documentation",
                        ("webhook-openapi-document",),
                        _DOCUMENT,
                    ),
                ),
            ),
            "test_openapi_schema": _mapped(
                "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
                "test_openapi_schema",
                feature_ids=("openapi-docs", "request-validation"),
                link=_link(
                    _WEBHOOK_RECIPE,
                    "fastapi.atlas-openapi-tutorial.webhook-documentation",
                    ("webhook-openapi-document",),
                    _DOCUMENT,
                ),
                rationale="The empty JSON pointer selects the full OpenAPI document, including the webhook event identifier, operation, request body, response declarations, and model components.",
                contract_gate="The source compares its whole snapshot. The independent workload declares another webhook and model, then selects its entire live document without storing expected outputs.",
                supporting_sources=(
                    _FASTAPI_WEBHOOKS,
                    _FASTAPI_OPENAPI_CACHE,
                    _FASTAPI_GET_OPENAPI,
                    _FASTAPI_SCHEMA_BRIDGE,
                    _FASTAPI_SCHEMA_NAMES,
                ),
                openapi_observation_scope="full_document",
            ),
        },
    },
    "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial001.py": {
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "request-validation", "response-serialization"),
            "reviewed_partial_input_mapping",
            "The default split-schema document and runtime model cases are mapped with independently named data.",
        ),
        "rationale": "The module exercises a model with an optional default through POST and GET routes and snapshots the full default separate-input/output OpenAPI document.",
        "supporting_sources": [
            _FASTAPI_OPENAPI_CACHE,
            _FASTAPI_GET_OPENAPI,
            _FASTAPI_SCHEMA_BRIDGE,
            _FASTAPI_SCHEMA_NAMES,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "functions": {
            "test_create_item": _mapped(
                "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial001.py",
                "test_create_item",
                feature_ids=("app-routing", "request-validation", "response-serialization"),
                link=_link(
                    _SCHEMA_RECIPE,
                    "fastapi.atlas-openapi-tutorial.split-schema-create",
                    ("create-split-record",),
                    _HTTP,
                ),
                rationale="A valid request omits the optional model field, and the response includes the model default through the ordinary route.",
                contract_gate="The source checks status and a parsed JSON result with the omitted field represented as null. The independent workload uses a distinct Record model/field and payload and selects response bytes rather than TestClient JSON decoding.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _FASTAPI_SCHEMA_BRIDGE,
                ),
            ),
            "test_read_items": _mapped(
                "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial001.py",
                "test_read_items",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _SCHEMA_RECIPE,
                    "fastapi.atlas-openapi-tutorial.split-schema-list",
                    ("read-split-records",),
                    _HTTP,
                ),
                rationale="A GET route returns multiple instances, including one whose optional default is omitted during construction.",
                contract_gate="The source compares a parsed array with defaulted and explicit optional values. The independent app uses distinct records/field names and observes exact bytes; response serialization remains FastAPI/Pydantic behavior over Starlette transport.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _FASTAPI_SCHEMA_BRIDGE,
                ),
            ),
            "test_openapi_schema": _mapped(
                "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial001.py",
                "test_openapi_schema",
                feature_ids=("openapi-docs", "request-validation", "response-serialization"),
                link=_link(
                    _SCHEMA_RECIPE,
                    "fastapi.atlas-openapi-tutorial.split-schema-document",
                    ("inspect-split-schema-document",),
                    _DOCUMENT,
                ),
                rationale="The complete generated document is selected for an app using the default separate_input_output_schemas=True mode.",
                contract_gate="The source compares a whole-document snapshot. The recipe uses a new Record model and selects the full output document; Pydantic generates model schemas while FastAPI chooses validation and serialization definitions.",
                supporting_sources=(
                    _FASTAPI_OPENAPI_CACHE,
                    _FASTAPI_GET_OPENAPI,
                    _FASTAPI_SCHEMA_BRIDGE,
                    _FASTAPI_SCHEMA_NAMES,
                ),
                openapi_observation_scope="full_document",
            ),
        },
    },
    "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial002.py": {
        "feature_ids": [
            "app-routing",
            "openapi-docs",
            "request-validation",
            "response-serialization",
        ],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "request-validation", "response-serialization"),
            "reviewed_partial_input_mapping",
            "The explicitly shared-schema document and runtime model cases are mapped with independently named data.",
        ),
        "rationale": "This application sets separate_input_output_schemas=False, exercises the same optional-default model shape through POST and GET routes, and snapshots the complete generated document.",
        "supporting_sources": [
            _FASTAPI_OPENAPI_CACHE,
            _FASTAPI_GET_OPENAPI,
            _FASTAPI_SCHEMA_BRIDGE,
            _FASTAPI_SCHEMA_NAMES,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "functions": {
            "test_create_item": _mapped(
                "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial002.py",
                "test_create_item",
                feature_ids=("app-routing", "request-validation", "response-serialization"),
                link=_link(
                    _SCHEMA_RECIPE,
                    "fastapi.atlas-openapi-tutorial.shared-schema-create",
                    ("create-shared-record",),
                    _HTTP,
                ),
                rationale="A valid request omits the optional field on the app whose OpenAPI input/output schema separation is disabled.",
                contract_gate="The source asserts status and parsed JSON containing the default. The workload uses a separate path prefix and renamed model field, then compares raw response bytes; runtime behavior does not depend on the OpenAPI mode setting.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _FASTAPI_SCHEMA_BRIDGE,
                ),
            ),
            "test_read_items": _mapped(
                "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial002.py",
                "test_read_items",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _SCHEMA_RECIPE,
                    "fastapi.atlas-openapi-tutorial.shared-schema-list",
                    ("read-shared-records",),
                    _HTTP,
                ),
                rationale="The GET action reaches the unsplit-schema app's response model and includes both defaulted and explicitly populated optional values.",
                contract_gate="The source checks parsed JSON. The independent app has distinct names and values and observes exact response bytes; the route's schema mode is not a runtime output switch.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                    _FASTAPI_SCHEMA_BRIDGE,
                ),
            ),
            "test_openapi_schema": _mapped(
                "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial002.py",
                "test_openapi_schema",
                feature_ids=("openapi-docs", "request-validation", "response-serialization"),
                link=_link(
                    _SCHEMA_RECIPE,
                    "fastapi.atlas-openapi-tutorial.shared-schema-document",
                    ("inspect-shared-schema-document",),
                    _DOCUMENT,
                ),
                rationale="The complete generated document is selected for an app configured with separate_input_output_schemas=False.",
                contract_gate="The source compares a full snapshot. The independent model names and values differ, while full-document observation captures the mode's generated schema projection. Pydantic generates model schema fragments.",
                supporting_sources=(
                    _FASTAPI_OPENAPI_CACHE,
                    _FASTAPI_GET_OPENAPI,
                    _FASTAPI_SCHEMA_BRIDGE,
                    _FASTAPI_SCHEMA_NAMES,
                ),
                openapi_observation_scope="full_document",
            ),
        },
    },
    "tests/test_tutorial/test_extending_openapi/test_tutorial001.py": {
        "feature_ids": ["app-routing", "openapi-docs", "response-serialization"],
        "feature_status": _feature_status(
            ("app-routing", "openapi-docs", "response-serialization"),
            "reviewed_partial_input_mapping",
            "The normal route, full custom document, metadata extension, and repeated cached request are mapped.",
        ),
        "rationale": "The source checks a normal route, a custom OpenAPI document with summary/description/extension metadata, and a second request that should return the cached document.",
        "supporting_sources": [
            _FASTAPI_OPENAPI_CACHE,
            _FASTAPI_GET_OPENAPI,
            _FASTAPI_TESTCLIENT_ALIAS,
            _STARLETTE_TESTCLIENT,
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "functions": {
            "test": _mapped(
                "tests/test_tutorial/test_extending_openapi/test_tutorial001.py",
                "test",
                feature_ids=("app-routing", "response-serialization"),
                link=_link(
                    _CUSTOM_RECIPE,
                    "fastapi.atlas-openapi-tutorial.custom-document-route",
                    ("read-independent-archives",),
                    _HTTP,
                ),
                rationale="An ordinary GET route is exercised on an app whose OpenAPI callable is customized and cached separately.",
                contract_gate="The source checks status and parsed JSON for /items/. The independent workload uses a distinct route/data shape and raw body bytes; generic ASGI response transport is Starlette-owned.",
                supporting_sources=(
                    _FASTAPI_REQUEST_HANDLER,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                    _STARLETTE_RESPONSES,
                ),
            ),
            "test_openapi_schema": _mapped(
                "tests/test_tutorial/test_extending_openapi/test_tutorial001.py",
                "test_openapi_schema",
                feature_ids=("openapi-docs",),
                link=_link(
                    _CUSTOM_RECIPE,
                    "fastapi.atlas-openapi-tutorial.custom-document-cache",
                    ("custom-openapi-first-request", "custom-openapi-repeat-request"),
                    _DOCUMENT,
                ),
                rationale="Both actions select the complete customized OpenAPI document; the repeated request reaches the same app instance and exercises its cache path.",
                contract_gate="The source compares the entire customized document, then compares the repeated response with the first response. The independent app defines its own metadata and extension and stores no expected values in the recipe; each full document is compared live, but cross-action equality is not a separate selector.",
                supporting_sources=(
                    _FASTAPI_OPENAPI_CACHE,
                    _FASTAPI_GET_OPENAPI,
                    _FASTAPI_TESTCLIENT_ALIAS,
                    _STARLETTE_TESTCLIENT,
                ),
                openapi_observation_scope="full_document",
            ),
        },
    },
}


def _all_test_functions(test_path: str) -> set[str]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test")
    }


def _recipe_observation_selectors(recipe: dict[str, Any], case_id: str) -> set[str]:
    case = next(item for item in recipe["cases"] if item["case_id"] == case_id)
    selectors: set[str] = set()
    for action in case["actions"]:
        for observation in action["observations"]:
            if observation["kind"] == "http_response":
                selectors.update(
                    "http.body.bytes" if selector == "body" else f"http.{selector}"
                    for selector in observation["selectors"]
                )
            elif observation["kind"] == "openapi":
                selectors.add("openapi.document")
    return selectors


def validate_static_links() -> dict[str, int]:
    """Validate source spans, strict recipe schemas, and function-to-case links."""
    schema_path = PROJECT_ROOT / "tests/fixtures/schemas/python-asgi-workflow-v2.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)

    expected_module_paths = {
        "tests/test_tutorial/test_conditional_openapi/test_tutorial001.py",
        "tests/test_tutorial/test_configure_swagger_ui/test_tutorial001.py",
        "tests/test_tutorial/test_configure_swagger_ui/test_tutorial002.py",
        "tests/test_tutorial/test_configure_swagger_ui/test_tutorial003.py",
        "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py",
        "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
        "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial001.py",
        "tests/test_tutorial/test_separate_openapi_schemas/test_tutorial002.py",
        "tests/test_tutorial/test_extending_openapi/test_tutorial001.py",
    }
    if set(OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS) != expected_module_paths:
        raise ValueError("reviewed module paths do not match the requested pinned source slice")

    test_function_count = 0
    mapped_count = 0
    exclusion_count = 0
    recipe_case_count = 0
    recipe_paths: set[str] = set()
    workload_paths: set[str] = set()
    cases_by_recipe: dict[str, dict[str, Any]] = {}

    for recipe_path in {
        link["recipe_path"]
        for module in OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS.values()
        for function in module["functions"].values()
        for link in function.get("workflow_cases", []) + function.get("related_workflows", [])
    }:
        if recipe_path in recipe_paths:
            raise ValueError(f"recipe path is not unique: {recipe_path}")
        recipe_paths.add(recipe_path)
        full_path = PROJECT_ROOT / recipe_path
        recipe = yaml.safe_load(full_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(recipe)
        for case in recipe["cases"]:
            for evidence in case["source_evidence"]:
                if not (FASTAPI_ROOT / evidence["path"]).is_file():
                    raise ValueError(f"missing pinned source evidence: {evidence['path']}")
        workload_path = recipe["workload"]["file"]
        if workload_path in workload_paths:
            raise ValueError(f"workload path is not unique: {workload_path}")
        workload_paths.add(workload_path)
        workload_tree = ast.parse((PROJECT_ROOT / workload_path).read_text(encoding="utf-8"))
        factories = {
            node.name
            for node in workload_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if recipe["workload"]["factory"] not in factories:
            raise ValueError(
                f"missing workload factory {recipe['workload']['factory']} in {workload_path}"
            )
        case_map = {item["case_id"]: item for item in recipe["cases"]}
        if len(case_map) != len(recipe["cases"]):
            raise ValueError(f"duplicate workflow case ID in {recipe_path}")
        recipe_case_count += len(case_map)
        cases_by_recipe[recipe_path] = {"recipe": recipe, "cases": case_map}

    for test_path, module in OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS.items():
        discovered = _all_test_functions(test_path)
        reviewed = set(module["functions"])
        if discovered != reviewed:
            raise ValueError(
                f"test-function mapping mismatch in {test_path}: "
                f"unmapped={sorted(discovered - reviewed)}, stale={sorted(reviewed - discovered)}"
            )
        test_function_count += len(discovered)
        for source in module["supporting_sources"]:
            _validate_source_span(source)
        if set(module["feature_status"]) != set(module["feature_ids"]):
            raise ValueError(f"module feature status rows do not match feature IDs for {test_path}")
        for function_name, entry in module["functions"].items():
            for source in entry.get("supporting_sources", []):
                _validate_source_span(source)
            if set(entry["feature_status"]) != set(entry["feature_ids"]):
                raise ValueError(
                    f"feature status rows do not match feature IDs for {test_path}:{function_name}"
                )
            if entry["mapping_status"] == "reviewed_partial":
                mapped_count += 1
                if entry["openapi_observation_scope"] == "full_document":
                    assert_full_document_link(entry)
                elif entry["openapi_observation_scope"] == "selected":
                    assert_selected_openapi_link(entry)
                elif entry["openapi_observation_scope"] != "not_applicable":
                    raise ValueError(f"unknown OpenAPI scope for {test_path}:{function_name}")
                for link in entry["workflow_cases"]:
                    _validate_link(link, cases_by_recipe)
            elif entry["mapping_status"] == "reviewed_excluded_from_asgi_input_lane":
                exclusion_count += 1
                _validate_source_span(entry["source_span"])
                if not entry.get("exclusion", {}).get("reason"):
                    raise ValueError(
                        f"missing source-backed exclusion for {test_path}:{function_name}"
                    )
                for link in entry.get("related_workflows", []):
                    _validate_link(link, cases_by_recipe)
            else:
                raise ValueError(f"unknown mapping status for {test_path}:{function_name}")

    for source in VERSION_CONSTRAINT_SOURCES:
        _validate_source_span(source)
    for row in API_NAME_REVIEW["aliases"]:
        _validate_source_span({**row["source"], "role": row["ownership"]})
    for row in API_NAME_REVIEW["nearby_deprecations_outside_scope"]:
        _validate_source_span({**row["source"], "role": row["reason"]})

    if test_function_count != mapped_count + exclusion_count:
        raise ValueError(
            "each selected test function must have one mapping or source-backed exclusion"
        )
    if len(recipe_paths) != len(workload_paths):
        raise ValueError("each unique recipe must link one unique workload")
    return {
        "modules": len(expected_module_paths),
        "test_functions": test_function_count,
        "mapped_functions": mapped_count,
        "excluded_functions": exclusion_count,
        "recipes": len(recipe_paths),
        "workloads": len(workload_paths),
        "cases": recipe_case_count,
    }


def _validate_source_span(source: dict[str, Any]) -> None:
    path = source["path"]
    if source.get("source_root") == "fastapi":
        source_path = FASTAPI_ROOT / path
    elif path.startswith("starlette/"):
        source_path = STARLETTE_ROOT / path
    elif path in {"metadata.yaml", "pyproject.toml"}:
        source_path = PROJECT_ROOT / path
    else:
        source_path = FASTAPI_ROOT / path
    lines = source_path.read_text(encoding="utf-8").splitlines()
    if not (1 <= source["start_line"] <= source["end_line"] <= len(lines)):
        raise ValueError(
            f"source span is out of range: {path}:{source['start_line']}-{source['end_line']}"
        )


def _validate_link(
    link: dict[str, Any],
    cases_by_recipe: dict[str, dict[str, Any]],
) -> None:
    recipe_data = cases_by_recipe.get(link["recipe_path"])
    if recipe_data is None:
        raise ValueError(f"mapping references an unlinked recipe: {link['recipe_path']}")
    case = recipe_data["cases"].get(link["case_id"])
    if case is None:
        raise ValueError(f"mapping references an unknown case: {link['case_id']}")
    action_ids = {action["action_id"] for action in case["actions"]}
    if not set(link["action_ids"]) <= action_ids:
        raise ValueError(f"mapping references unknown action IDs for {link['case_id']}")
    selectors = _recipe_observation_selectors(recipe_data["recipe"], link["case_id"])
    if not set(link["observation_selectors"]) <= selectors:
        raise ValueError(f"mapping selectors do not resolve in recipe case {link['case_id']}")


def assert_full_document_link(entry: dict[str, Any]) -> None:
    for link in entry["workflow_cases"]:
        recipe = yaml.safe_load((PROJECT_ROOT / link["recipe_path"]).read_text(encoding="utf-8"))
        case = next(row for row in recipe["cases"] if row["case_id"] == link["case_id"])
        if not any(
            observation.get("kind") == "openapi" and "" in observation.get("json_pointers", [])
            for action in case["actions"]
            for observation in action["observations"]
        ):
            raise ValueError(f"full-document selection is missing for {link['case_id']}")


def assert_selected_openapi_link(entry: dict[str, Any]) -> None:
    for link in entry["workflow_cases"]:
        recipe = yaml.safe_load((PROJECT_ROOT / link["recipe_path"]).read_text(encoding="utf-8"))
        case = next(row for row in recipe["cases"] if row["case_id"] == link["case_id"])
        if not any(
            observation.get("kind") == "openapi"
            and any(pointer for pointer in observation.get("json_pointers", []))
            for action in case["actions"]
            for observation in action["observations"]
        ):
            raise ValueError(f"selected OpenAPI pointer is missing for {link['case_id']}")


__all__ = [
    "API_NAME_REVIEW",
    "OPENAPI_TUTORIAL_INTERFACE_REVIEW_MAPPINGS",
    "OWNERSHIP_NOTES",
    "SOURCE_IDENTITIES",
    "VERSION_CONSTRAINTS",
    "VERSION_CONSTRAINT_SOURCES",
    "validate_static_links",
]


if __name__ == "__main__":
    print(json.dumps(validate_static_links(), sort_keys=True))
