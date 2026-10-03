"""Reviewed partial links for reusable FastAPI documentation-example inputs."""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(
    recipe: str,
    *case_ids: str,
    selectors: list[str],
) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": list(case_ids),
        "observation_selectors": sorted(selectors),
    }


def _review(
    rationale: str,
    spans: list[dict[str, object]],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "rationale": rationale,
        "supporting_sources": spans,
        "workflow_cases": cases,
    }


HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]
HTTP_STREAM = ["http.body.bytes", "http.headers.ordered", "http.status"]


DOC_EXAMPLE_CITATION_WAVE_K = {
    "docs_src/body_fields/tutorial001_an_py310.py": _review(
        (
            "The route embeds an Item body and applies its model validation. Independent valid and "
            "invalid requests sample embedded-body parsing and validation; "
            "the OpenAPI case selects "
            "the embedded request schema. The tutorial's field values and full model metadata are "
            "not claimed."
        ),
        [
            _span(
                "docs_src/body_fields/tutorial001_an_py310.py",
                9,
                15,
                "Item model fields and validation",
            ),
            _span(
                "docs_src/body_fields/tutorial001_an_py310.py",
                18,
                20,
                "PUT route with an embedded Annotated body",
            ),
        ],
        [
            _case(
                "body-fields-doc-tutorial001-review.yaml",
                "fastapi.docs-example.body-fields.tutorial001.embedded-model-valid",
                "fastapi.docs-example.body-fields.tutorial001.embedded-model-invalid-amount",
                selectors=HTTP_BODY_STATUS,
            ),
            _case(
                "body-fields-doc-tutorial001-review.yaml",
                "fastapi.docs-example.body-fields.tutorial001.openapi-embedded-schema",
                selectors=["http.status", "openapi.paths"],
            ),
        ],
    ),
    "docs_src/custom_request_and_route/tutorial001_an_py310.py": _review(
        (
            "The annotated example installs a custom APIRoute handler that wraps the incoming "
            "request before delegating. An independent uncompressed JSON request through a "
            "separate custom route/request wrapper observes status and body; gzip decompression "
            "and Annotated spelling are not claimed."
        ),
        [
            _span(
                "docs_src/custom_request_and_route/tutorial001_an_py310.py",
                19,
                27,
                "GzipRoute handler wrapper and delegated dispatch",
            ),
            _span(
                "docs_src/custom_request_and_route/tutorial001_an_py310.py",
                30,
                36,
                "custom route registration and typed POST route",
            ),
        ],
        [
            _case(
                "source-wave-b-custom-routes.yaml",
                "fastapi.source-wave-b.custom-request.uncompressed-json",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/custom_request_and_route/tutorial001_py310.py": _review(
        (
            "This variant installs the same custom APIRoute wrapper with a non-Annotated body "
            "parameter. An independent uncompressed JSON request through a separate request/route "
            "wrapper observes status and body; compressed-body handling and annotation behavior "
            "are not claimed."
        ),
        [
            _span(
                "docs_src/custom_request_and_route/tutorial001_py310.py",
                8,
                15,
                "GzipRequest body override",
            ),
            _span(
                "docs_src/custom_request_and_route/tutorial001_py310.py",
                18,
                26,
                "GzipRoute handler wrapper and delegated dispatch",
            ),
            _span(
                "docs_src/custom_request_and_route/tutorial001_py310.py",
                29,
                34,
                "custom route registration and POST body parameter",
            ),
        ],
        [
            _case(
                "source-wave-b-custom-routes.yaml",
                "fastapi.source-wave-b.custom-request.uncompressed-json",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/custom_request_and_route/tutorial002_an_py310.py": _review(
        (
            "The custom route catches RequestValidationError, reads the submitted body, and raises "
            "HTTPException with both values. An independent invalid-shape request exercises that "
            "conversion path and observes status and body; the annotation spelling and tutorial "
            "literals are not claimed."
        ),
        [
            _span(
                "docs_src/custom_request_and_route/tutorial002_an_py310.py",
                9,
                21,
                "validation-error route wrapper and HTTPException conversion",
            ),
            _span(
                "docs_src/custom_request_and_route/tutorial002_an_py310.py",
                24,
                30,
                "route-class installation and typed request body",
            ),
        ],
        [
            _case(
                "source-wave-b-custom-routes.yaml",
                "fastapi.source-wave-b.custom-route.validation-context",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/dependencies/tutorial001_02_an_py310.py": _review(
        (
            "The example aliases a query-parameter helper through Annotated and Depends. An "
            "independent request supplies explicit query values to an equivalent helper and "
            "observes status and body; the second route, defaults, and alias spelling are not "
            "claimed."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial001_02_an_py310.py",
                8,
                16,
                "common query dependency, Annotated alias, and route",
            )
        ],
        [
            _case(
                "atlas-testing-websocket-dependency-defaults.yaml",
                "fastapi.atlas-testing-dependency.defaults",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/dependencies/tutorial001_an_py310.py": _review(
        (
            "Both routes depend on the same query-parameter helper. An independent request invokes "
            "an equivalent helper with explicit query values and observes status and body; the "
            "second source route and default values are not claimed."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial001_an_py310.py",
                8,
                14,
                "common query dependency and first route",
            )
        ],
        [
            _case(
                "atlas-testing-websocket-dependency-defaults.yaml",
                "fastapi.atlas-testing-dependency.defaults",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/dependencies/tutorial007_py310.py": _review(
        (
            "The snippet yields a database session and closes it in a finally block. Independent "
            "requests to a context-manager yield dependency observe its result and cleanup state "
            "through status and body; database construction and persistence are not claimed."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial007_py310.py",
                1,
                6,
                "yield dependency and finally cleanup",
            )
        ],
        [
            _case(
                "dependency-yield-tutorials-upstream.yaml",
                "fastapi.dependencies.tutorial010.context-manager-in-yield-dependency",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/dependencies/tutorial008_an_py310.py": _review(
        (
            "The snippet nests three async generator dependencies, each with cleanup in finally. "
            "Independent requests sample a nested async dependency chain, its cleanup order, and "
            "the response status/body; its resource factories and concrete types are not claimed."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial008_an_py310.py",
                6,
                27,
                "nested async yield dependencies and cleanup",
            )
        ],
        [
            _case(
                "dependency-yield-tutorials-upstream.yaml",
                "fastapi.dependencies.tutorial008.async-yield-chain-default",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/dependencies/tutorial013_an_py310.py": _review(
        (
            "The example injects a yielded session into an authorization dependency and returns a "
            "synchronous generator through StreamingResponse. Independent requests observe the "
            "streaming resource during iteration and after cleanup through status and body; "
            "SQLModel, database queries, authorization, and delay values are not claimed."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial013_an_py310.py",
                19,
                27,
                "session yield dependency and authorization lookup",
            ),
            _span(
                "docs_src/dependencies/tutorial013_an_py310.py",
                30,
                38,
                "synchronous generator and StreamingResponse route",
            ),
        ],
        [
            _case(
                "dependency-wave-lifecycle.yaml",
                "fastapi.dependencies.streaming-resource-lifetime",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/dependencies/tutorial014_an_py310.py": _review(
        (
            "The route returns a synchronous string generator through StreamingResponse. "
            "Independent sync-generator responses sample status, ordered headers, and body bytes; "
            "the early session close, SQLModel behavior, and tutorial payload are not claimed."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial014_an_py310.py",
                31,
                39,
                "synchronous generator and StreamingResponse route",
            )
        ],
        [
            _case(
                "stream-data-tutorials-upstream.yaml",
                "fastapi.tutorial.stream-data.tutorial002.binary-generator-forms",
                selectors=HTTP_STREAM,
            )
        ],
    ),
    "docs_src/events/tutorial001_py310.py": _review(
        (
            "The app registers an async startup event. An independent legacy-event lifecycle "
            "workflow observes event order and startup dispatch; module-level item population, "
            "route behavior, and event data are not claimed."
        ),
        [
            _span(
                "docs_src/events/tutorial001_py310.py",
                8,
                12,
                "startup handler registration and state initialization",
            )
        ],
        [
            _case(
                "router-events-lifespan-upstream.yaml",
                "fastapi.lifecycle.router-events-legacy",
                selectors=["asgi.lifespan.event_order", "asgi.lifespan.startup"],
            )
        ],
    ),
    "docs_src/events/tutorial002_py310.py": _review(
        (
            "The app registers a synchronous shutdown event. An independent legacy-event lifecycle "
            "workflow observes shutdown dispatch and event order; the sampled callback form, "
            "filesystem logging, and log contents are not claimed."
        ),
        [
            _span(
                "docs_src/events/tutorial002_py310.py",
                6,
                9,
                "shutdown handler registration and file operation",
            )
        ],
        [
            _case(
                "router-events-lifespan-upstream.yaml",
                "fastapi.lifecycle.async-shutdown-handler",
                selectors=["asgi.lifespan.event_order", "asgi.lifespan.shutdown"],
            )
        ],
    ),
    "docs_src/events/tutorial003_py310.py": _review(
        (
            "The app supplies an async-context-manager lifespan that initializes state before "
            "yielding and clears it afterward. An independent async-generator lifespan workflow "
            "observes event order and startup/shutdown; ML work and prediction values are not "
            "claimed."
        ),
        [
            _span(
                "docs_src/events/tutorial003_py310.py",
                13,
                19,
                "lifespan context manager and cleanup",
            ),
            _span(
                "docs_src/events/tutorial003_py310.py",
                22,
                22,
                "lifespan registered on the FastAPI application",
            ),
        ],
        [
            _case(
                "router-events-lifespan-upstream.yaml",
                "fastapi.lifecycle.async-generator-lifespan",
                selectors=[
                    "asgi.lifespan.event_order",
                    "asgi.lifespan.startup",
                    "asgi.lifespan.shutdown",
                ],
            )
        ],
    ),
    "docs_src/openapi_webhooks/tutorial001_py310.py": _review(
        (
            "The app declares a webhook POST operation with a Pydantic request model. The "
            "independent OpenAPI request selects the webhook projection and status only; callback "
            "delivery, model field values, and the ordinary users route are not claimed."
        ),
        [
            _span(
                "docs_src/openapi_webhooks/tutorial001_py310.py",
                9,
                16,
                "webhook request model and operation declaration",
            )
        ],
        [
            _case(
                "openapi-docs.yaml",
                "fastapi.openapi.tutorial-openapi-webhooks-tutorial001.openapi-schema",
                selectors=["http.status", "openapi.document"],
            )
        ],
    ),
    "docs_src/sql_databases/tutorial001_an_py310.py": _review(
        (
            "The example provides a Session through a yield dependency and an Annotated alias. An "
            "independent fake-session workflow observes dependency-driven request handling and "
            "cleanup through status and body; database setup and CRUD behavior are not claimed."
        ),
        [
            _span(
                "docs_src/sql_databases/tutorial001_an_py310.py",
                25,
                30,
                "session yield dependency and Annotated alias",
            )
        ],
        [
            _case(
                "docs-sql-databases-fake-dependency.yaml",
                "fastapi.docs.sql-databases.fake-yield.create-and-cleanup",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/sql_databases/tutorial001_py310.py": _review(
        (
            "The example provides a Session through a yield dependency. An independent "
            "fake-session "
            "workflow observes dependency-driven request handling and cleanup through status and "
            "body; database setup and CRUD behavior are not claimed."
        ),
        [
            _span(
                "docs_src/sql_databases/tutorial001_py310.py",
                23,
                25,
                "session yield dependency",
            )
        ],
        [
            _case(
                "docs-sql-databases-fake-dependency.yaml",
                "fastapi.docs.sql-databases.fake-yield.create-and-cleanup",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/sql_databases/tutorial002_py310.py": _review(
        (
            "The tutorial reuses a Session yield dependency in CRUD routes. An independent fake-"
            "session workflow samples dependency-driven request handling and cleanup "
            "through status "
            "and body; SQLModel CRUD and persistence are not claimed."
        ),
        [
            _span(
                "docs_src/sql_databases/tutorial002_py310.py",
                40,
                45,
                "session yield dependency and app setup",
            )
        ],
        [
            _case(
                "docs-sql-databases-fake-dependency.yaml",
                "fastapi.docs.sql-databases.fake-yield.create-and-cleanup",
                selectors=HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/websockets_/tutorial002_an_py310.py": _review(
        (
            "The annotated WebSocket example extracts cookie/query credentials, validates them in "
            "a dependency, then accepts and exchanges messages. Independent socket actions sample "
            "message/event order and close codes; the HTML client and exact tutorial messages are "
            "not claimed."
        ),
        [
            _span(
                "docs_src/websockets_/tutorial002_an_py310.py",
                66,
                74,
                "cookie/query credential dependency",
            ),
            _span(
                "docs_src/websockets_/tutorial002_an_py310.py",
                76,
                92,
                "annotated WebSocket parameters and accept/message loop",
            ),
        ],
        [
            _case(
                "atlas-testing-websocket-websockets-tutorial002.yaml",
                "fastapi.atlas-testing.websocket-tutorial002",
                selectors=[
                    "websocket.close_code",
                    "websocket.event_order",
                    "websocket.messages",
                ],
            )
        ],
    ),
}
