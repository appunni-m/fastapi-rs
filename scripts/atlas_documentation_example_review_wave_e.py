"""Reviewed partial mappings for the next FastAPI documentation-example batch."""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(recipe: str, case_id: str, selectors: list[str]) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": [case_id],
        "observation_selectors": sorted(selectors),
    }


def _review(
    rationale: str,
    spans: list[dict[str, object]],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {"rationale": rationale, "supporting_sources": spans, "workflow_cases": cases}


DOC_EXAMPLE_CITATION_WAVE_E = {
    "docs_src/path_params/tutorial003b_py310.py": _review(
        (
            "The example registers two handlers at the same path. Independent dispatch "
            "and OpenAPI cases exercise first-registration routing and the later "
            "registration's schema projection, with different names and response "
            "literals."
        ),
        [
            _span(
                "docs_src/path_params/tutorial003b_py310.py",
                6,
                12,
                "duplicate path operation declarations",
            )
        ],
        [
            _case(
                "path-operation-parameter-tutorials-test_path_params_test_tutorial003b_test_get_users.yaml",
                "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial003b-test-get-users",
                ["http.body.bytes", "http.status"],
            ),
            _case(
                "path-operation-parameter-tutorials-test_path_params_test_tutorial003b_test_openapi_schema.yaml",
                "fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial003b-test-openapi-schema",
                ["openapi.document"],
            ),
        ],
    ),
    "docs_src/schema_extra_example/tutorial001_py310.py": _review(
        (
            "The example declares model-level json_schema_extra examples. The independent "
            "case observes model-level example metadata in the generated schema; its "
            "model and example values differ, and runtime submission of those values is "
            "not covered."
        ),
        [
            _span(
                "docs_src/schema_extra_example/tutorial001_py310.py",
                7,
                24,
                "model-level JSON Schema examples and route",
            )
        ],
        [
            _case(
                "schema-extra-examples-upstream.yaml",
                "fastapi.schema-extra-example.model-schema-extra",
                ["openapi.document"],
            )
        ],
    ),
    "docs_src/schema_extra_example/tutorial003_py310.py": _review(
        (
            "The example declares Body examples in the generated request-body schema. The "
            "independent case observes request schema placement for default and Annotated "
            "declarations; route and example data differ, and the case submits only a "
            "valid body."
        ),
        [
            _span(
                "docs_src/schema_extra_example/tutorial003_py310.py",
                14,
                26,
                "Body examples and request route declarations",
            )
        ],
        [
            _case(
                "schema-extra-examples-upstream.yaml",
                "fastapi.schema-extra-example.body-examples-list",
                ["openapi.document"],
            )
        ],
    ),
    "docs_src/schema_extra_example/tutorial005_an_py310.py": _review(
        (
            "The example attaches named OpenAPI example objects to a request body. The "
            "independent case observes the request-body examples projection with "
            "different keys, descriptions, and values; it does not submit the converted "
            "and invalid examples."
        ),
        [
            _span(
                "docs_src/schema_extra_example/tutorial005_an_py310.py",
                16,
                50,
                "named request-body OpenAPI examples",
            )
        ],
        [
            _case(
                "schema-extra-examples-upstream.yaml",
                "fastapi.schema-extra-example.openapi-example-objects",
                ["openapi.document"],
            )
        ],
    ),
    "docs_src/security/tutorial001_py310.py": _review(
        (
            "The example uses a required OAuth2PasswordBearer dependency. Independent "
            "requests cover missing credentials, a wrong authentication scheme, and a "
            "valid bearer token; the valid response body differs, so that case claims "
            "status only. The OpenAPI case uses different security declarations and is "
            "omitted."
        ),
        [
            _span(
                "docs_src/security/tutorial001_py310.py",
                6,
                10,
                "required OAuth2 bearer dependency and endpoint",
            )
        ],
        [
            _case(
                "security-dependencies.yaml",
                "fastapi.docs.security.bearer-required-missing",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            ),
            _case(
                "security-dependencies.yaml",
                "fastapi.docs.security.bearer-required-wrong-scheme",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            ),
            _case(
                "security-dependencies.yaml",
                "fastapi.docs.security.bearer-required-valid",
                ["http.status"],
            ),
        ],
    ),
    "docs_src/response_model/tutorial003_04_py310.py": _review(
        (
            "This example's response-model declaration fails during route construction "
            "under pinned FastAPI. The independent construction-error case compares the "
            "failure outcome and exception metadata only; there is no supported endpoint "
            "or response claim."
        ),
        [
            _span(
                "docs_src/response_model/tutorial003_04_py310.py",
                7,
                10,
                "invalid inferred union response-model declaration",
            ),
            _span(
                "tests/test_tutorial/test_response_model/test_tutorial003_04.py",
                9,
                17,
                "upstream assertion for the construction failure",
            ),
        ],
        [
            _case(
                "response-model-union-construction-gap.yaml",
                "fastapi.response-model.union-inferred-construction-error",
                [
                    "construction.exception_class",
                    "construction.exception_message",
                    "construction.outcome",
                ],
            )
        ],
    ),
    "docs_src/separate_openapi_schemas/tutorial002_py310.py": _review(
        (
            "The example uses one model for request and response data while optional "
            "fields differ between the two. Independent create/read requests observe the "
            "returned values and status; the fixture changes the response annotation, so "
            "this mapping omits its OpenAPI projection."
        ),
        [
            _span(
                "docs_src/separate_openapi_schemas/tutorial002_py310.py",
                5,
                25,
                "shared request/response model and routes",
            )
        ],
        [
            _case(
                "separate-openapi-schemas-tutorial002-upstream.yaml",
                "fastapi.test.test-tutorial-test-separate-openapi-schemas-test-tutorial002.shared-model-requests-and-openapi",
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/server_sent_events/tutorial003_py310.py": _review(
        (
            "The example streams raw log data from a named SSE route. The independent "
            "case observes stream response bytes, headers, and status and selects the "
            "corresponding OpenAPI operation; other SSE tutorials and event shapes are "
            "not claimed."
        ),
        [
            _span(
                "docs_src/server_sent_events/tutorial003_py310.py",
                9,
                17,
                "raw-data SSE generator and route",
            )
        ],
        [
            _case(
                "server-sent-events-tutorial003-upstream.yaml",
                "fastapi.tutorial.server-sent-events.tutorial003.raw-log-data",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            ),
            _case(
                "server-sent-events-tutorial003-upstream.yaml",
                "fastapi.tutorial.server-sent-events.tutorial003.openapi",
                ["openapi.document"],
            ),
        ],
    ),
    "docs_src/sql_databases/tutorial002_an_py310.py": _review(
        (
            "The example's FastAPI slice declares Hero request/response behavior and "
            "yields a database session. Independent cases cover required-name validation, "
            "model schema projection, and the response/cleanup path with an in-memory "
            "fake. SQLModel/SQLite operations, startup table creation, and "
            "read/update/delete routes are not covered."
        ),
        [
            _span(
                "docs_src/sql_databases/tutorial002_an_py310.py",
                7,
                28,
                "Hero model and FastAPI route declarations",
            ),
            _span(
                "docs_src/sql_databases/tutorial002_an_py310.py",
                42,
                62,
                "yielded dependency and application route use",
            ),
        ],
        [
            _case(
                "docs-sql-databases-fake-dependency.yaml",
                "fastapi.docs.sql-databases.fake-yield.invalid-request",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            ),
            _case(
                "docs-sql-databases-fake-dependency.yaml",
                "fastapi.docs.sql-databases.fake-yield.openapi-models",
                ["openapi.document"],
            ),
            _case(
                "docs-sql-databases-fake-dependency.yaml",
                "fastapi.docs.sql-databases.fake-yield.create-and-cleanup",
                ["http.body.bytes", "http.status"],
            ),
        ],
    ),
    "docs_src/stream_data/tutorial001_py310.py": _review(
        (
            "The example demonstrates sync and async generator response forms. The "
            "independent case observes response status, headers, and full body bytes for "
            "represented stream forms; chunk boundaries, source content, and the source's "
            "OpenAPI paths are not covered."
        ),
        [
            _span(
                "docs_src/stream_data/tutorial001_py310.py",
                20,
                65,
                "sync and async generator response forms",
            )
        ],
        [
            _case(
                "stream-data-tutorials-upstream.yaml",
                "fastapi.tutorial.stream-data.tutorial001.generator-forms",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/stream_data/tutorial002_py310.py": _review(
        (
            "The example streams PNG data using sync and async generator forms. The "
            "independent cases exercise binary streaming with image/png and compare full "
            "response bytes, headers, and status using different synthesized PNG data; "
            "chunk boundaries and matching OpenAPI paths are not covered."
        ),
        [
            _span(
                "docs_src/stream_data/tutorial002_py310.py",
                19,
                54,
                "binary PNG generator response forms",
            )
        ],
        [
            _case(
                "stream-data-tutorials-upstream.yaml",
                "fastapi.tutorial.stream-data.tutorial002.binary-generator-forms",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/sub_applications/tutorial001_py310.py": _review(
        (
            "The example mounts a FastAPI sub-application and observes the main and "
            "mounted application routes and schemas. The independent workflow reproduces "
            "that composition, default metadata, request dispatch, and OpenAPI boundary; "
            "only its listed endpoints and observations are claimed."
        ),
        [
            _span(
                "docs_src/sub_applications/tutorial001_py310.py",
                1,
                19,
                "main and mounted FastAPI application setup",
            )
        ],
        [
            _case(
                "atlas-testing-websocket-sub-applications.yaml",
                "fastapi.atlas-testing.sub-applications",
                ["http.body.bytes", "http.status", "openapi.document"],
            )
        ],
    ),
}
