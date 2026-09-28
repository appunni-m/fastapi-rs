"""Source-reviewed metadata tutorial mappings for FastAPI 0.141.1.

This is a builder-shaped data sidecar. Its case links point to existing
input-only workflows plus one small input-only route workflow for the two
uncovered ``Foo`` item-response assertions. It does not generate or modify
atlas artifacts and does not claim live parity.
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
        "role": "sole generic ASGI, TestClient, and response contract",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "pinned model and OpenAPI-object validation/encoding dependency",
    },
}


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _workflow(
    recipe_path: str,
    case_id: str,
    selectors: tuple[str, ...],
    action_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_ids": [case_id],
        "observation_selectors": list(selectors),
        "action_ids": list(action_ids),
    }


def _review(
    test_path: str,
    start: int,
    end: int,
    feature_ids: tuple[str, ...],
    selectors: tuple[str, ...],
    rationale: str,
    *,
    supporting_sources: tuple[dict[str, Any], ...],
    workflow_cases: tuple[dict[str, Any], ...],
    stimulus_notes: str,
    contract_gate: str,
) -> dict[str, Any]:
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "supporting_sources": [
            _source(
                test_path,
                start,
                end,
                "upstream FastAPI 0.141.1 test function and asserted observations",
            ),
            *supporting_sources,
        ],
        "workflow_cases": list(workflow_cases),
        "stimulus_notes": stimulus_notes,
        "contract_gate": contract_gate,
    }


_HTTP_ITEM = _workflow(
    "tests/fixtures/input-recipes/parity/metadata-tutorial-items-upstream.yaml",
    "fastapi.test.test-tutorial-test-metadata-shared-items.test-items-foo",
    ("http.status", "http.body.bytes"),
    ("items",),
)
_METADATA001_ITEMS = _workflow(
    "tests/fixtures/input-recipes/parity/metadata-tutorial001-upstream.yaml",
    "fastapi.test.test-tutorial-test-metadata-test-tutorial001.test-items",
    ("http.status", "http.body.bytes"),
    ("items",),
)
_METADATA001_1_OPENAPI = _workflow(
    "tests/fixtures/input-recipes/parity/metadata-tutorial001-1-upstream.yaml",
    "fastapi.test.test-tutorial-test-metadata-test-tutorial001-1.test-openapi-schema",
    ("http.status", "openapi.document"),
    ("openapi",),
)
_METADATA002_OPENAPI = _workflow(
    "tests/fixtures/input-recipes/parity/metadata-tutorial002-upstream.yaml",
    "fastapi.test.test-tutorial-test-metadata-test-tutorial002.test-openapi-schema",
    ("http.status", "openapi.document"),
    ("default-openapi-location", "configured-openapi-location"),
)
_METADATA003_DOCS = _workflow(
    "tests/fixtures/input-recipes/parity/metadata-tutorial003-upstream.yaml",
    "fastapi.test.test-tutorial-test-metadata-test-tutorial003.test-swagger-ui-custom-url",
    ("http.status", "http.body.bytes"),
    ("default-swagger-url", "configured-swagger-url", "disabled-redoc-url"),
)
_METADATA004_OPENAPI = _workflow(
    "tests/fixtures/input-recipes/parity/metadata-tutorial004-upstream.yaml",
    "fastapi.test.test-tutorial-test-metadata-test-tutorial004.test-openapi-schema",
    ("http.status", "openapi.document"),
    ("users", "items", "openapi"),
)
_GUIDE_METADATA_OPENAPI = _workflow(
    "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
    "fastapi.docs.openapi-interface.tutorial-metadata.openapi-metadata",
    ("http.status", "openapi.document"),
    ("openapi",),
)


_HTTP_AND_OPENAPI_SOURCES = (
    _source(
        "fastapi/testclient.py",
        1,
        1,
        "FastAPI TestClient is a direct Starlette TestClient re-export",
    ),
    _source(
        "fastapi/routing.py",
        706,
        750,
        "FastAPI executes the endpoint and prepares non-Response return values for the configured response class",
    ),
    _source(
        "starlette/testclient.py",
        327,
        365,
        "Starlette 1.6.0 TestClient captures ASGI response status, headers, and body",
    ),
    _source(
        "starlette/responses.py",
        163,
        170,
        "Starlette 1.6.0 sends the response-start and response-body ASGI messages",
    ),
    _source(
        "starlette/responses.py",
        181,
        202,
        "Starlette 1.6.0 JSONResponse renders JSON bytes",
    ),
)

_OPENAPI_SOURCES = (
    _source(
        "fastapi/applications.py",
        873,
        890,
        "FastAPI stores API metadata, OpenAPI URL, tag metadata, and documentation URLs on the application",
    ),
    _source(
        "fastapi/applications.py",
        1070,
        1103,
        "FastAPI builds and caches the OpenAPI object from application metadata and routes",
    ),
    _source(
        "fastapi/openapi/utils.py",
        585,
        627,
        "FastAPI assembles OpenAPI info and route/model fields from application metadata",
    ),
    _source(
        "fastapi/openapi/utils.py",
        672,
        679,
        "FastAPI attaches tag metadata and validates/encodes the OpenAPI object through its Pydantic model",
    ),
    _source(
        "fastapi/openapi/models.py",
        57,
        80,
        "FastAPI declares the OpenAPI Info model on Pydantic BaseModelWithConfig",
    ),
    _source(
        "fastapi/openapi/models.py",
        413,
        430,
        "FastAPI declares the OpenAPI Tag and OpenAPI models on Pydantic BaseModelWithConfig",
    ),
)

_URL_AND_DOCS_SOURCES = (
    _source(
        "fastapi/applications.py",
        199,
        221,
        "FastAPI openapi_url configuration and default",
    ),
    _source(
        "fastapi/applications.py",
        398,
        445,
        "FastAPI Swagger UI and ReDoc URL configuration and defaults",
    ),
    _source(
        "fastapi/applications.py",
        1105,
        1158,
        "FastAPI conditionally registers OpenAPI, Swagger UI, and ReDoc routes",
    ),
    _source(
        "fastapi/openapi/docs.py",
        148,
        194,
        "FastAPI generates the Swagger UI HTML and returns Starlette HTMLResponse",
    ),
    _source(
        "fastapi/openapi/docs.py",
        270,
        298,
        "FastAPI generates ReDoc HTML and returns Starlette HTMLResponse",
    ),
)

_TAG_SOURCES = (
    _source(
        "fastapi/applications.py",
        222,
        281,
        "FastAPI documents openapi_tags and their relationship to path-operation tags",
    ),
    _source(
        "fastapi/openapi/utils.py",
        672,
        679,
        "FastAPI appends tag metadata and encodes the OpenAPI Pydantic model",
    ),
)

_COMMON_GATE = (
    "Source-backed candidate only; this atlas review is not executable parity evidence. "
    "FastAPI owns metadata storage, route setup, OpenAPI assembly, and Swagger/ReDoc HTML "
    "generation. Starlette 1.6.0 owns the generic TestClient/ASGI transport and response "
    "message handling through the sibling Starlette-RS contract. Pydantic 2.13.4 owns its "
    "model behavior; these source examples declare no input models. FastAPI's OpenAPI "
    "endpoint does pass its schema through FastAPI-declared Pydantic models, so that "
    "conversion boundary remains separately attributable."
)


METADATA_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    "tests/test_tutorial/test_metadata/__init__.py": {
        "rationale": "The pinned package initializer is empty and declares no test function or runtime behavior to map.",
        "supporting_sources": [],
        "module_observation_selectors": [],
        "functions": {},
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": "Empty test package initializer; it contains no executable behavior or assertions.",
        "contract_gate": "Source exclusion based on the zero-byte FastAPI 0.141.1 initializer; there is no case ID or observable contract in this file.",
    },
    "tests/test_tutorial/test_metadata/test_tutorial001.py": {
        "rationale": "The module checks a metadata-configured item route and the generated OpenAPI document.",
        "supporting_sources": [
            *_HTTP_AND_OPENAPI_SOURCES,
            *_OPENAPI_SOURCES,
            _source(
                "docs_src/metadata/tutorial001_py310.py",
                18,
                38,
                "metadata configuration and unannotated GET /items/ example",
            ),
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "workflow_cases": [_METADATA001_ITEMS, _GUIDE_METADATA_OPENAPI],
        "contract_gate": _COMMON_GATE,
        "functions": {
            "test_items": _review(
                "tests/test_tutorial/test_metadata/test_tutorial001.py",
                9,
                12,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The function requests the app-owned item list and asserts only the HTTP status and decoded JSON value.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial001_py310.py",
                        36,
                        38,
                        "unannotated GET /items/ returns the Katana item list",
                    ),
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA001_ITEMS,),
                stimulus_notes="Reuse metadata-tutorial001-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial001.test-items (items action; http.status and http.body.bytes). Its input is independently authored; it observes the same fixed route data.",
                contract_gate="Partial candidate: the existing workload annotates its route return as list[dict[str, str]], while the pinned docs example has no return annotation. It observes only status/body for this valid fixed value and does not claim Pydantic response validation parity. TestClient/ASGI delivery is Starlette 1.6.0-owned.",
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_metadata/test_tutorial001.py",
                15,
                52,
                ("openapi-docs",),
                ("http.status", "openapi.document"),
                "The function compares the complete OpenAPI response to a snapshot containing API metadata and the unannotated route operation.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial001_py310.py",
                        18,
                        38,
                        "API metadata and the item route reflected in OpenAPI",
                    ),
                    *_OPENAPI_SOURCES,
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_GUIDE_METADATA_OPENAPI,),
                stimulus_notes="Reuse docs-openapi-interface.yaml::fastapi.docs.openapi-interface.tutorial-metadata.openapi-metadata (openapi action; http.status and openapi.document). It observes /info, /tags, and /paths with an independently authored metadata app; the concrete values differ from this snapshot.",
                contract_gate="Partial candidate: the linked independent case checks /info, /tags, and /paths, not every field in this test's full snapshot, and uses different metadata values. FastAPI owns schema assembly; FastAPI's OpenAPI Pydantic model and Pydantic 2.13.4 encode that schema; Starlette 1.6.0 supplies JSONResponse and the generic ASGI transport.",
            ),
        },
    },
    "tests/test_tutorial/test_metadata/test_tutorial001_1.py": {
        "rationale": "The module checks the same item route with the SPDX license-identifier metadata variant and its generated OpenAPI document.",
        "supporting_sources": [
            *_HTTP_AND_OPENAPI_SOURCES,
            *_OPENAPI_SOURCES,
            _source(
                "docs_src/metadata/tutorial001_1_py310.py",
                18,
                38,
                "SPDX license identifier metadata and unannotated GET /items/ example",
            ),
            _source(
                "fastapi/applications.py",
                591,
                624,
                "FastAPI license_info identifier/url input contract",
            ),
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "workflow_cases": [_METADATA001_ITEMS, _METADATA001_1_OPENAPI, _GUIDE_METADATA_OPENAPI],
        "contract_gate": _COMMON_GATE,
        "functions": {
            "test_items": _review(
                "tests/test_tutorial/test_metadata/test_tutorial001_1.py",
                9,
                12,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The test observes the item route; its SPDX license setting does not affect the asserted response.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial001_1_py310.py",
                        29,
                        38,
                        "SPDX license metadata plus the same Katana item route",
                    ),
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA001_ITEMS,),
                stimulus_notes="Reuse metadata-tutorial001-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial001.test-items (items action; http.status and http.body.bytes). The route result is the same Katana list; the linked case uses the URL-license variant, which this function does not observe.",
                contract_gate="Partial candidate: the reused workload has a return annotation and the source example does not. The test does not observe license metadata; the route response sample does not establish Pydantic validation behavior. Starlette 1.6.0 owns TestClient/ASGI delivery.",
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_metadata/test_tutorial001_1.py",
                15,
                52,
                ("openapi-docs",),
                ("http.status", "openapi.document"),
                "The function's snapshot includes the SPDX identifier in /info/license and the rest of the generated OpenAPI document.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial001_1_py310.py",
                        18,
                        33,
                        "license_info identifier is mutually exclusive with url in the app configuration",
                    ),
                    _source(
                        "fastapi/applications.py",
                        591,
                        624,
                        "FastAPI license_info identifier contract",
                    ),
                    *_OPENAPI_SOURCES,
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA001_1_OPENAPI, _GUIDE_METADATA_OPENAPI),
                stimulus_notes="Reuse metadata-tutorial001-1-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial001-1.test-openapi-schema (openapi action; http.status and openapi.document), which observes /info/license for the identifier variant. The guide metadata case additionally observes /info, /tags, and /paths but has different API values.",
                contract_gate="Partial candidate: the identifier workflow observes only /info/license, while the source test snapshots the complete OpenAPI document. The generic metadata workflow covers /info, /tags, and /paths with different values. FastAPI assembles OpenAPI; its OpenAPI model uses Pydantic 2.13.4; Starlette 1.6.0 owns the response transport.",
            ),
        },
    },
    "tests/test_tutorial/test_metadata/test_tutorial002.py": {
        "rationale": "The module covers the item route, the configured OpenAPI URL, and the absence of the default OpenAPI URL.",
        "supporting_sources": [
            *_HTTP_AND_OPENAPI_SOURCES,
            *_OPENAPI_SOURCES,
            *_URL_AND_DOCS_SOURCES[:3],
            _source(
                "docs_src/metadata/tutorial002_py310.py",
                3,
                8,
                "custom OpenAPI URL and unannotated item route",
            ),
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "workflow_cases": [_HTTP_ITEM, _METADATA002_OPENAPI, _GUIDE_METADATA_OPENAPI],
        "contract_gate": _COMMON_GATE,
        "functions": {
            "test_items": _review(
                "tests/test_tutorial/test_metadata/test_tutorial002.py",
                9,
                12,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The function checks the fixed Foo item response independently of the OpenAPI endpoint URL.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial002_py310.py",
                        3,
                        8,
                        "openapi_url setting and unannotated GET /items/ route",
                    ),
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_HTTP_ITEM,),
                stimulus_notes="Use metadata-tutorial-items-upstream.yaml::fastapi.test.test-tutorial-test-metadata-shared-items.test-items-foo (items action; http.status and http.body.bytes). It invokes the same /items/ request and Foo list without adding a Pydantic return annotation.",
                contract_gate="Partial candidate: the upstream function asserts the route response only; the shared independent input omits the separate openapi_url constructor setting because that setting is covered by test_get_openapi_json_default_url. No request model or response model is involved. Starlette 1.6.0 owns generic TestClient/ASGI transport.",
            ),
            "test_get_openapi_json_default_url": _review(
                "tests/test_tutorial/test_metadata/test_tutorial002.py",
                15,
                17,
                ("openapi-docs",),
                ("http.status",),
                "The function asserts that configuring openapi_url removes the default /openapi.json endpoint.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial002_py310.py",
                        3,
                        3,
                        "FastAPI app configured with openapi_url=/api/v1/openapi.json",
                    ),
                    *_URL_AND_DOCS_SOURCES[:3],
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA002_OPENAPI,),
                stimulus_notes="Reuse metadata-tutorial002-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial002.test-openapi-schema, default-openapi-location action; actual selector is http.status.",
                contract_gate="Partial candidate: the workflow also requests the configured URL and observes its /paths, but it does not execute the upstream TestClient wrapper. FastAPI owns route registration from openapi_url; Starlette 1.6.0 owns generic routing/HTTP response delivery.",
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_metadata/test_tutorial002.py",
                20,
                45,
                ("openapi-docs",),
                ("http.status", "openapi.document"),
                "The function compares the generated schema at the custom URL, including the /items/ operation.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial002_py310.py",
                        3,
                        8,
                        "custom OpenAPI route plus the /items/ path included in the schema",
                    ),
                    *_OPENAPI_SOURCES,
                    *_URL_AND_DOCS_SOURCES[:3],
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA002_OPENAPI, _GUIDE_METADATA_OPENAPI),
                stimulus_notes="Reuse metadata-tutorial002-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial002.test-openapi-schema (configured-openapi-location action observes /paths) and docs-openapi-interface.yaml::fastapi.docs.openapi-interface.tutorial-metadata.openapi-metadata (observes /info, /tags, /paths with different API values).",
                contract_gate="Partial candidate: the tutorial workflow observes /paths but not the full schema snapshot; the guide workflow covers /info, /tags, and /paths with a different metadata app. FastAPI owns URL registration and schema assembly; Pydantic 2.13.4 is the OpenAPI model conversion boundary, and Starlette 1.6.0 owns the generic JSON response/ASGI transport.",
            ),
        },
    },
    "tests/test_tutorial/test_metadata/test_tutorial003.py": {
        "rationale": "The module checks ordinary item output, the generated OpenAPI document, and custom/disabled interactive documentation URLs.",
        "supporting_sources": [
            *_HTTP_AND_OPENAPI_SOURCES,
            *_OPENAPI_SOURCES,
            *_URL_AND_DOCS_SOURCES,
            _source(
                "docs_src/metadata/tutorial003_py310.py",
                3,
                8,
                "custom Swagger URL, disabled ReDoc, and unannotated item route",
            ),
        ],
        "module_observation_selectors": ["http.status", "http.body.bytes", "openapi.document"],
        "workflow_cases": [_HTTP_ITEM, _METADATA003_DOCS, _GUIDE_METADATA_OPENAPI],
        "contract_gate": _COMMON_GATE,
        "functions": {
            "test_items": _review(
                "tests/test_tutorial/test_metadata/test_tutorial003.py",
                9,
                12,
                ("response-serialization",),
                ("http.status", "http.body.bytes"),
                "The custom documentation URLs do not affect the tested Foo item route response.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial003_py310.py",
                        3,
                        8,
                        "docs URL settings and unannotated GET /items/ route",
                    ),
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_HTTP_ITEM,),
                stimulus_notes="Use metadata-tutorial-items-upstream.yaml::fastapi.test.test-tutorial-test-metadata-shared-items.test-items-foo (items action; http.status and http.body.bytes). The route returns the same Foo list; docs URL settings are exercised by the module's docs tests.",
                contract_gate="Partial candidate: this function asserts only the item response; the shared input focuses on that request and omits docs_url/redoc_url settings, which are covered by the sibling functions. The unannotated route avoids a Pydantic response-model claim. Starlette 1.6.0 owns generic TestClient/ASGI delivery.",
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_metadata/test_tutorial003.py",
                15,
                40,
                ("openapi-docs",),
                ("http.status", "openapi.document"),
                "The function checks the default OpenAPI endpoint and snapshots its default API metadata and item path.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial003_py310.py",
                        3,
                        8,
                        "custom docs URL setting is independent of the default OpenAPI URL and item route",
                    ),
                    *_OPENAPI_SOURCES,
                    *_URL_AND_DOCS_SOURCES[:3],
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_GUIDE_METADATA_OPENAPI,),
                stimulus_notes="Reuse docs-openapi-interface.yaml::fastapi.docs.openapi-interface.tutorial-metadata.openapi-metadata (openapi action; http.status and openapi.document). Its /info, /tags, and /paths values differ, so this maps generated metadata mechanics only.",
                contract_gate="Partial candidate: the independent case does not combine the source app's custom docs_url/redoc_url with the OpenAPI request and does not match the full snapshot values. FastAPI owns schema generation; its OpenAPI Pydantic model uses pinned Pydantic 2.13.4; Starlette 1.6.0 supplies JSONResponse and ASGI delivery.",
            ),
            "test_swagger_ui_default_url": _review(
                "tests/test_tutorial/test_metadata/test_tutorial003.py",
                43,
                45,
                ("openapi-docs",),
                ("http.status",),
                "The function asserts that the default Swagger URL is absent after the app is configured with docs_url=/documentation.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial003_py310.py",
                        3,
                        3,
                        "custom Swagger URL and disabled ReDoc configuration",
                    ),
                    *_URL_AND_DOCS_SOURCES,
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA003_DOCS,),
                stimulus_notes="Reuse metadata-tutorial003-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial003.test-swagger-ui-custom-url, default-swagger-url action; actual selector is http.status.",
                contract_gate="Partial candidate: this request is one action in the linked custom-URL workflow, whose case also observes the configured Swagger response and disabled ReDoc status. Route existence is FastAPI setup behavior; generic 404 handling and TestClient transport belong to Starlette 1.6.0.",
            ),
            "test_swagger_ui_custom_url": _review(
                "tests/test_tutorial/test_metadata/test_tutorial003.py",
                48,
                51,
                ("openapi-docs",),
                ("http.status", "http.body.bytes"),
                "The function checks that the configured Swagger route returns HTML with the FastAPI Swagger UI title.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial003_py310.py",
                        3,
                        3,
                        "docs_url is configured as /documentation",
                    ),
                    *_URL_AND_DOCS_SOURCES,
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA003_DOCS,),
                stimulus_notes="Reuse metadata-tutorial003-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial003.test-swagger-ui-custom-url, configured-swagger-url action; actual selectors are http.status and http.body.bytes.",
                contract_gate="Partial candidate: the independent workflow compares the entire HTML response body, while the source assertion checks only for its title substring. Swagger HTML construction is FastAPI-owned; Starlette 1.6.0 owns HTMLResponse and ASGI delivery. Browser execution and remote JS/CSS assets are outside this case.",
            ),
            "test_redoc_ui_default_url": _review(
                "tests/test_tutorial/test_metadata/test_tutorial003.py",
                54,
                56,
                ("openapi-docs",),
                ("http.status",),
                "The function asserts that setting redoc_url=None removes the default /redoc endpoint.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial003_py310.py",
                        3,
                        3,
                        "redoc_url=None configuration",
                    ),
                    *_URL_AND_DOCS_SOURCES,
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA003_DOCS,),
                stimulus_notes="Reuse metadata-tutorial003-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial003.test-swagger-ui-custom-url, disabled-redoc-url action; actual selector is http.status.",
                contract_gate="Partial candidate: the linked workflow observes the disabled endpoint's HTTP status only. FastAPI owns whether the ReDoc route is registered; Starlette 1.6.0 owns generic routing, 404 response, and TestClient transport.",
            ),
        },
    },
    "tests/test_tutorial/test_metadata/test_tutorial004.py": {
        "rationale": "The module checks two tagged item routes and the generated OpenAPI tag metadata and path operations.",
        "supporting_sources": [
            *_HTTP_AND_OPENAPI_SOURCES,
            *_OPENAPI_SOURCES,
            *_TAG_SOURCES,
            _source(
                "docs_src/metadata/tutorial004_py310.py",
                3,
                28,
                "OpenAPI tag metadata and tagged GET routes",
            ),
            _source(
                "docs/en/docs/tutorial/metadata.md",
                41,
                75,
                "documented tag metadata and path-operation tag application",
            ),
        ],
        "module_observation_selectors": ["http.status", "openapi.document"],
        "workflow_cases": [_METADATA004_OPENAPI, _GUIDE_METADATA_OPENAPI],
        "contract_gate": _COMMON_GATE,
        "functions": {
            "test_path_operations": _review(
                "tests/test_tutorial/test_metadata/test_tutorial004.py",
                9,
                13,
                ("response-serialization",),
                ("http.status",),
                "The function makes the users and items GET requests and asserts only that both status codes are successful.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial004_py310.py",
                        21,
                        28,
                        "users and items GET routes with their path-operation tags",
                    ),
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA004_OPENAPI,),
                stimulus_notes="Reuse metadata-tutorial004-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial004.test-openapi-schema (users and items actions; actual selector http.status). The same case also requests OpenAPI for the sibling snapshot function.",
                contract_gate="Partial candidate: the source function asserts only 200 status for the two routes; the existing case observes status only for those actions and does not compare their bodies. The workload annotates route returns, unlike the docs snippet, so this does not establish Pydantic response-model parity. Generic ASGI/TestClient behavior is Starlette 1.6.0-owned.",
            ),
            "test_openapi_schema": _review(
                "tests/test_tutorial/test_metadata/test_tutorial004.py",
                16,
                66,
                ("openapi-docs",),
                ("http.status", "openapi.document"),
                "The function snapshots OpenAPI paths and declared tag metadata, including the second tag's externalDocs object.",
                supporting_sources=(
                    _source(
                        "docs_src/metadata/tutorial004_py310.py",
                        3,
                        28,
                        "ordered openapi_tags and route tags used to generate the snapshot",
                    ),
                    _source(
                        "docs/en/docs/tutorial/metadata.md",
                        41,
                        93,
                        "tag descriptions, externalDocs, path-operation use, and order",
                    ),
                    *_TAG_SOURCES,
                    *_OPENAPI_SOURCES,
                    *_HTTP_AND_OPENAPI_SOURCES,
                ),
                workflow_cases=(_METADATA004_OPENAPI, _GUIDE_METADATA_OPENAPI),
                stimulus_notes="Reuse metadata-tutorial004-upstream.yaml::fastapi.test.test-tutorial-test-metadata-test-tutorial004.test-openapi-schema (openapi action observes /tags/1/externalDocs) and docs-openapi-interface.yaml::fastapi.docs.openapi-interface.tutorial-metadata.openapi-metadata (observes /info, /tags, /paths with different API values).",
                contract_gate="Partial candidate: the exact tutorial workflow observes only /tags/1/externalDocs plus HTTP status, not the full snapshot; the broader guide case observes /info, /tags, /paths with a different app. FastAPI orders/builds tag metadata and assembles OpenAPI; its OpenAPI model conversion uses Pydantic 2.13.4. Starlette 1.6.0 owns generic JSON response and test transport.",
            ),
        },
    },
}
