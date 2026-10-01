"""Source-reviewed mappings for SSE and streaming behavior tests.

The test sources are pinned to FastAPI 0.141.1. Recipes contain independent
ASGI requests, not copied pytest bodies or expected results. Generic response
framing and TestClient behavior remain in the Starlette 1.6.0 contract.
"""

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic response, transport, and TestClient contract",
    },
    "pydantic": {"version": "2.13.4", "role": "pinned model validation and encoding dependency"},
}

__all__ = ["SSE_STREAM_TEST_REVIEW_MAPPINGS", "SOURCE_IDENTITIES"]


def _source(path, start, end, role):
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _link(recipe_path, case_id, action_ids, selectors):
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _workflow_recipe(function_rows):
    links = [link for row in function_rows.values() for link in row["workflow_cases"]]
    unique = {}
    for link in links:
        key = (link["recipe_path"], link["case_id"])
        record = unique.setdefault(
            key,
            {
                "recipe_path": link["recipe_path"],
                "case_id": link["case_id"],
                "action_ids": [],
                "observation_selectors": [],
            },
        )
        for field in ("action_ids", "observation_selectors"):
            for value in link[field]:
                if value not in record[field]:
                    record[field].append(value)
    return [unique[key] for key in sorted(unique)]


def _function(feature_ids, selectors, rationale, links, sources, gate):
    link_text = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} "
        f"(actions: {', '.join(link['action_ids'])}; "
        f"selectors: {', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "replace_features": True,
        "workflow_cases": list(links),
        "supporting_sources": list(sources),
        "contract_gate": "Partial: " + gate,
        "stimulus_notes": (
            "Independent input-only workflow reference: "
            + link_text
            + ". The recipe records no expected output. The selected body and headers are "
            "observations from the generated workload, not source snapshots."
        ),
    }


def _module(rationale, docs_source, implementation_sources, functions):
    links = _workflow_recipe(functions)
    selectors = sorted(
        {selector for row in functions.values() for selector in row["observation_selectors"]}
    )
    sources = [docs_source, *implementation_sources]
    note = (
        "Source-reviewed partial mapping to independent recipes: "
        + "; ".join(
            f"{link['recipe_path']}::{link['case_id']} ({', '.join(link['observation_selectors'])})"
            for link in links
        )
        + ". TestClient behavior, response transport, and ASGI streaming mechanics are "
        "covered by Starlette 1.6.0's separate contract."
    )
    return {
        "rationale": rationale,
        "supporting_sources": sources,
        "workflow_cases": links,
        "module_observation_selectors": selectors,
        "stimulus_notes": note,
        "functions": functions,
    }


_HTTP = ["http.status", "http.headers.ordered", "http.body.bytes"]
_OPENAPI = ["openapi.document"]
_STREAM_CANCELLATION = [
    "asgi.cancellation.cancelled_caught",
    "http.status",
    "http.headers.ordered",
]

_SSE_STREAM = _source(
    "fastapi/routing.py",
    492,
    551,
    "FastAPI validates and serializes yielded SSE items, distinguishing raw data from JSON data",
)
_SSE_ITERATION = _source(
    "fastapi/routing.py",
    520,
    557,
    "FastAPI dispatches async and sync SSE generators and formats yielded records",
)
_SSE_OAS = _source(
    "fastapi/openapi/utils.py",
    436,
    455,
    "FastAPI generates the text/event-stream item schema and optional payload schema",
)
_RAW_STREAM = _source(
    "fastapi/routing.py",
    683,
    704,
    "FastAPI forwards raw async or sync generator chunks into the declared response class",
)
_GENERATOR_ROUTE = _source(
    "fastapi/routing.py",
    1071,
    1101,
    "FastAPI detects generator endpoints and infers or suppresses response models from stream item annotations",
)
_STREAM_OAS = _source(
    "fastapi/openapi/utils.py",
    456,
    472,
    "FastAPI documents a response-class media type with its selected schema",
)


SSE_STREAM_TEST_REVIEW_MAPPINGS = {
    "tests/test_tutorial/test_server_sent_events/test_tutorial001.py": _module(
        "The module checks four async/sync and typed/untyped SSE routes plus their generated OpenAPI schemas.",
        _source(
            "docs/en/docs/tutorial/server-sent-events.md",
            36,
            70,
            "SSE generator routes, typed stream items, synchronous generators, and omitted return annotations",
        ),
        [
            _SSE_STREAM,
            _SSE_ITERATION,
            _SSE_OAS,
            _GENERATOR_ROUTE,
        ],
        {
            "test_stream_items": _function(
                ["response-serialization"],
                _HTTP,
                "The source asserts status, event-stream content type, and three data lines for four generator variants.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial001-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial001.stream-routes",
                        [
                            "stream-async-typed",
                            "stream-sync-typed",
                            "stream-async-untyped",
                            "stream-sync-untyped",
                        ],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial001_py310.py",
                        10,
                        43,
                        "Pydantic stream item and four typed/untyped async/sync generator routes",
                    ),
                    _SSE_STREAM,
                    _SSE_ITERATION,
                    _GENERATOR_ROUTE,
                ],
                "The independent workflow compares collected response bytes and ordered headers, which are stricter than the test's selected fields. It does not observe ASGI chunk boundaries, keepalive timing, or TestClient behavior.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI,
                "The source snapshots the OpenAPI document for four typed/untyped SSE routes.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial001-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial001.openapi",
                        ["openapi-routes"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial001_py310.py",
                        10,
                        43,
                        "Four SSE routes with typed and untyped return annotations",
                    ),
                    _SSE_OAS,
                    _GENERATOR_ROUTE,
                ],
                "The workflow selects the four operation pointers and components, rather than comparing the source test's full FastAPI-title document snapshot. It is a behavior sample only.",
            ),
        },
    ),
    "tests/test_tutorial/test_server_sent_events/test_tutorial002.py": _module(
        "The module checks comment, event, JSON data, ID, and retry fields, then snapshots the SSE OpenAPI operation.",
        _source(
            "docs/en/docs/tutorial/server-sent-events.md",
            72,
            80,
            "ServerSentEvent fields and JSON serialization of event data",
        ),
        [_SSE_STREAM, _SSE_ITERATION, _GENERATOR_ROUTE, _SSE_OAS],
        {
            "test_stream_items": _function(
                ["response-serialization"],
                _HTTP,
                "The source observes the initial comment and the count and values of event, data, ID, and retry lines.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial002-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial002.event-fields",
                        ["stream-event-fields"],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial002_py310.py",
                        10,
                        26,
                        "Pydantic item data and comment/event/ID/retry SSE records",
                    ),
                    _SSE_STREAM,
                    _SSE_ITERATION,
                    _GENERATOR_ROUTE,
                    _source(
                        "fastapi/sse.py",
                        165,
                        233,
                        "FastAPI SSE field order, line encoding, and event termination",
                    ),
                ],
                "The workflow compares the entire collected response body and ordered headers, beyond the field-count assertions. It does not claim chunk-boundary or keepalive parity.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI,
                "The source snapshots the response schema for the explicit ServerSentEvent stream.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial002-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial002.openapi",
                        ["openapi-event-item"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial002_py310.py",
                        22,
                        26,
                        "Explicit ServerSentEvent result annotation and event metadata",
                    ),
                    _SSE_OAS,
                    _GENERATOR_ROUTE,
                ],
                "The independent workflow selects the route operation pointer, not the full source snapshot. Generic response status and transport behavior remain Starlette-owned.",
            ),
        },
    ),
    "tests/test_tutorial/test_server_sent_events/test_tutorial003.py": _module(
        "The module checks raw, non-JSON log event data and the generated stream-item OpenAPI operation.",
        _source(
            "docs/en/docs/tutorial/server-sent-events.md",
            82,
            94,
            "Raw SSE data bypasses JSON encoding and is mutually exclusive with data",
        ),
        [_SSE_STREAM, _SSE_ITERATION, _GENERATOR_ROUTE, _SSE_OAS],
        {
            "test_stream_logs": _function(
                ["response-serialization"],
                _HTTP,
                "The source requires three exact data lines without JSON string quotes.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial003-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial003.raw-log-data",
                        ["stream-raw-logs"],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial003_py310.py",
                        9,
                        17,
                        "Raw log strings are yielded using ServerSentEvent.raw_data",
                    ),
                    _SSE_STREAM,
                    _GENERATOR_ROUTE,
                ],
                "The independent workflow compares all response bytes and ordered headers for an independently authored log stream. The test's literal app log values are not treated as FastAPI outputs; ASGI chunking and keepalive behavior are unobserved.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI,
                "The source snapshots the OpenAPI operation for an annotated ServerSentEvent stream.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial003-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial003.openapi",
                        ["openapi-raw-log-item"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial003_py310.py",
                        9,
                        17,
                        "Annotated raw-data stream route",
                    ),
                    _SSE_OAS,
                    _GENERATOR_ROUTE,
                ],
                "The workflow selects the route operation pointer and is not a full document snapshot claim.",
            ),
        },
    ),
    "tests/test_tutorial/test_server_sent_events/test_tutorial004.py": _module(
        "The module checks sequential SSE IDs, resumption from integer Last-Event-ID values, and the OpenAPI header parameter.",
        _source(
            "docs/en/docs/tutorial/server-sent-events.md",
            96,
            102,
            "Last-Event-ID is read as a header parameter to resume an SSE stream",
        ),
        [
            _SSE_STREAM,
            _SSE_ITERATION,
            _GENERATOR_ROUTE,
            _SSE_OAS,
            _source(
                "fastapi/dependencies/utils.py",
                780,
                849,
                "FastAPI extracts and validates request header parameters",
            ),
        ],
        {
            "test_stream_all_items": _function(
                ["response-serialization"],
                _HTTP,
                "The source checks the full event count and ordered IDs when no resume header is sent.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial004.resume-stream",
                        ["stream-from-start"],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial004_py310.py",
                        23,
                        31,
                        "Default stream starting position and sequential item IDs",
                    ),
                    _SSE_STREAM,
                    _GENERATOR_ROUTE,
                ],
                "The independent case observes the full response bytes and headers, beyond the selected ID/count assertions; it does not observe individual ASGI chunks.",
            ),
            "test_resume_from_last_event_id": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source sends Last-Event-ID 0 and checks that the parsed integer resumes at ID 1.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial004.resume-stream",
                        ["resume-after-event-zero"],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial004_py310.py",
                        23,
                        31,
                        "Typed Last-Event-ID header and app-owned resume offset",
                    ),
                    _source(
                        "fastapi/dependencies/utils.py",
                        780,
                        849,
                        "FastAPI header lookup, alias handling, and Pydantic value validation",
                    ),
                    _SSE_STREAM,
                ],
                "The fixture's collected body/headers exceed the test's selected ID/count assertions. The resume offset is application code; FastAPI owns header extraction and integer validation. Generic headers behavior is assigned to Starlette 1.6.0.",
            ),
            "test_resume_from_last_item": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source sends Last-Event-ID 1 and checks the single remaining event with ID 2.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial004.resume-stream",
                        ["resume-after-event-one"],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial004_py310.py",
                        23,
                        31,
                        "Typed Last-Event-ID header and app-owned resume offset",
                    ),
                    _source(
                        "fastapi/dependencies/utils.py",
                        780,
                        849,
                        "FastAPI header lookup, alias handling, and Pydantic value validation",
                    ),
                    _SSE_STREAM,
                ],
                "The fixture compares full response bytes and headers, beyond the test's selected ID/count assertions. No malformed or absent-but-required header cases are claimed.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs", "request-validation"],
                _OPENAPI,
                "The source snapshots the SSE operation including the Last-Event-ID header parameter and generated components.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial004.openapi",
                        ["openapi-resume-header"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial004_py310.py",
                        23,
                        31,
                        "Header-annotated route and generated stream item type",
                    ),
                    _source(
                        "fastapi/openapi/utils.py",
                        357,
                        377,
                        "FastAPI builds operation parameter documentation",
                    ),
                    _SSE_OAS,
                    _GENERATOR_ROUTE,
                ],
                "The workflow selects an operation and components, not every field in the upstream full-document snapshot.",
            ),
        },
    ),
    "tests/test_tutorial/test_server_sent_events/test_tutorial005.py": _module(
        "The module sends a Pydantic request model to an SSE POST endpoint and snapshots its request and response schemas.",
        _source(
            "docs/en/docs/tutorial/server-sent-events.md",
            104,
            110,
            "SSE may stream over POST and a request model supplies the stream input",
        ),
        [
            _SSE_STREAM,
            _SSE_ITERATION,
            _SSE_OAS,
            _source(
                "fastapi/routing.py",
                425,
                489,
                "FastAPI reads and parses a request body before solving endpoint dependencies",
            ),
            _source(
                "fastapi/dependencies/utils.py",
                951,
                998,
                "FastAPI validates a request model from the parsed body",
            ),
        ],
        {
            "test_stream_chat": _function(
                ["request-validation", "response-serialization"],
                _HTTP,
                "The source posts a Prompt model and checks JSON-encoded token data followed by a raw terminal event.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial005-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial005.post-chat-stream",
                        ["post-chat-stream"],
                        _HTTP,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial005_py310.py",
                        10,
                        19,
                        "Prompt model, POST SSE route, JSON data events, and raw terminal event",
                    ),
                    _source(
                        "fastapi/routing.py",
                        425,
                        489,
                        "FastAPI body read and JSON parsing",
                    ),
                    _source(
                        "fastapi/dependencies/utils.py",
                        951,
                        998,
                        "FastAPI request model validation",
                    ),
                    _SSE_STREAM,
                ],
                "The independent input uses the source request shape and compares the collected event stream exactly. It does not claim general body validation errors, stream chunk boundaries, or TestClient behavior.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs", "request-validation"],
                _OPENAPI,
                "The source snapshots the POST requestBody, SSE response item schema, and generated validation components.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial005-upstream.yaml",
                        "fastapi.tutorial.server-sent-events.tutorial005.openapi",
                        ["openapi-post-stream"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/server_sent_events/tutorial005_py310.py",
                        10,
                        19,
                        "Request model and SSE POST operation",
                    ),
                    _source(
                        "fastapi/openapi/utils.py",
                        377,
                        385,
                        "FastAPI emits requestBody OpenAPI metadata",
                    ),
                    _SSE_OAS,
                ],
                "The workflow selects the POST operation and schema components rather than the upstream full OpenAPI snapshot.",
            ),
        },
    ),
    "tests/test_tutorial/test_stream_data/test_tutorial001.py": _module(
        "The module checks text and byte StreamingResponse generator variants and their OpenAPI response descriptions.",
        _source(
            "docs/en/docs/advanced/stream-data.md",
            21,
            49,
            "StreamingResponse passes yielded strings and bytes through without JSON serialization",
        ),
        [
            _RAW_STREAM,
            _GENERATOR_ROUTE,
            _STREAM_OAS,
            _source(
                "fastapi/responses.py",
                5,
                12,
                "FastAPI re-exports StreamingResponse from Starlette",
            ),
        ],
        {
            "test_stream_story": _function(
                ["response-serialization"],
                _HTTP,
                "The source checks identical final text from four typed/untyped async/sync text streams and four corresponding byte streams.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/stream_data.yaml",
                        "fastapi.docs.stream-data.binary-stream",
                        ["read-binary-stream"],
                        _HTTP,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/stream-data-tutorials-upstream.yaml",
                        "fastapi.tutorial.stream-data.tutorial001.generator-forms",
                        [
                            "read-telemetry-story-async-typed",
                            "read-telemetry-story-sync-typed",
                            "read-telemetry-story-async-inferred",
                            "read-telemetry-story-sync-inferred",
                            "read-telemetry-story-bytes-async-typed",
                            "read-telemetry-story-bytes-sync-typed",
                            "read-telemetry-story-bytes-async-inferred",
                            "read-telemetry-story-bytes-sync-inferred",
                        ],
                        _HTTP,
                    ),
                ],
                [
                    _source(
                        "docs_src/stream_data/tutorial001_py310.py",
                        20,
                        65,
                        "Eight text/byte streaming routes covering typed/untyped async/sync generators",
                    ),
                    _RAW_STREAM,
                    _GENERATOR_ROUTE,
                ],
                "The existing binary-stream recipe is only a basic two-chunk sample; the new independent case adds the eight generator forms with different payloads. StreamingResponse framing and TestClient behavior belong to Starlette 1.6.0. No individual chunk boundary is observed.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI,
                "The source snapshots successful-response descriptions for all eight routes with no response content schema.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/stream-data-tutorials-upstream.yaml",
                        "fastapi.tutorial.stream-data.tutorial001.openapi",
                        ["inspect-story-openapi"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/stream_data/tutorial001_py310.py",
                        20,
                        65,
                        "Streaming routes using the default media-type-free StreamingResponse",
                    ),
                    _STREAM_OAS,
                    _GENERATOR_ROUTE,
                ],
                "The new independent case selects all eight operation pointers; it does not claim equality with the full upstream OpenAPI document or generated unique identifiers.",
            ),
        },
    ),
    "tests/test_tutorial/test_stream_data/test_tutorial002.py": _module(
        "The module checks streamed binary bytes, image/png media type, and documented response schemas for five generator forms.",
        _source(
            "docs/en/docs/advanced/stream-data.md",
            51,
            81,
            "A custom StreamingResponse media_type documents and serves a streamed PNG",
        ),
        [
            _RAW_STREAM,
            _GENERATOR_ROUTE,
            _STREAM_OAS,
            _source(
                "fastapi/responses.py",
                5,
                12,
                "FastAPI re-exports StreamingResponse from Starlette",
            ),
        ],
        {
            "test_stream_image": _function(
                ["response-serialization"],
                _HTTP,
                "The source checks status, image/png content type, and exact binary bytes from async/sync, yield/yield-from, and annotated/unannotated variants.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/streaming-runtime-upstream.yaml",
                        "fastapi.streaming-runtime.stream-data-async-typed",
                        ["read-raster-async-typed"],
                        _HTTP,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/streaming-runtime-upstream.yaml",
                        "fastapi.streaming-runtime.stream-data-sync-typed",
                        ["read-raster-sync-typed"],
                        _HTTP,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/streaming-runtime-upstream.yaml",
                        "fastapi.streaming-runtime.stream-data-sync-forward",
                        ["read-raster-sync-forward"],
                        _HTTP,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/streaming-runtime-upstream.yaml",
                        "fastapi.streaming-runtime.stream-data-async-inferred",
                        ["read-raster-async-inferred"],
                        _HTTP,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/streaming-runtime-upstream.yaml",
                        "fastapi.streaming-runtime.stream-data-sync-inferred",
                        ["read-raster-sync-inferred"],
                        _HTTP,
                    ),
                    _link(
                        "tests/fixtures/input-recipes/parity/stream-data-tutorials-upstream.yaml",
                        "fastapi.tutorial.stream-data.tutorial002.binary-generator-forms",
                        [
                            "read-raster-async-typed",
                            "read-raster-sync-typed",
                            "read-raster-sync-forward",
                            "read-raster-async-inferred",
                            "read-raster-sync-inferred",
                        ],
                        _HTTP,
                    ),
                ],
                [
                    _source(
                        "docs_src/stream_data/tutorial002_py310.py",
                        19,
                        54,
                        "Custom PNG response class and five stream generator variants",
                    ),
                    _RAW_STREAM,
                    _GENERATOR_ROUTE,
                ],
                "The existing runtime recipe and new tutorial-specific case use independently generated PNG bytes rather than the source's image asset. They exercise response media type and collection of streamed bytes, not file lifetime, individual ASGI chunks, or generic StreamingResponse semantics owned by Starlette 1.6.0.",
            ),
            "test_openapi_schema": _function(
                ["openapi-docs"],
                _OPENAPI,
                "The source snapshots the image/png response content schema for five routes.",
                [
                    _link(
                        "tests/fixtures/input-recipes/parity/stream-data-tutorials-upstream.yaml",
                        "fastapi.tutorial.stream-data.tutorial002.openapi",
                        ["inspect-raster-openapi"],
                        _OPENAPI,
                    )
                ],
                [
                    _source(
                        "docs_src/stream_data/tutorial002_py310.py",
                        19,
                        54,
                        "The image/png StreamingResponse subclass and all five route declarations",
                    ),
                    _STREAM_OAS,
                    _GENERATOR_ROUTE,
                ],
                "The independent workflow selects the five operation pointers, not the source's complete OpenAPI snapshot or source-specific operation IDs.",
            ),
        },
    ),
    "tests/test_stream_cancellation.py": {
        **_module(
            "The module directly invokes the FastAPI ASGI app with infinite async streams and cancels the call from an outer timeout. It covers raw StreamingResponse and FastAPI JSON Lines generator paths without TestClient.",
            _source(
                "docs/en/docs/advanced/stream-data.md",
                21,
                28,
                "A StreamingResponse route yields chunks that FastAPI passes through without JSON conversion",
            ),
            [
                _source(
                    "docs/en/docs/advanced/custom-response.md",
                    180,
                    194,
                    "The documentation explains cancellation checkpoints for async streams and recommends FastAPI's stream-data and JSON Lines patterns",
                ),
                _source(
                    "fastapi/routing.py",
                    656,
                    662,
                    "FastAPI inserts a cancellation checkpoint after each async JSON Lines item",
                ),
                _source(
                    "fastapi/routing.py",
                    683,
                    704,
                    "FastAPI wraps raw async generator streams with a cancellation checkpoint",
                ),
                _source(
                    "fastapi/responses.py",
                    5,
                    12,
                    "FastAPI publicly re-exports StreamingResponse from Starlette",
                ),
                _source(
                    "starlette/responses.py",
                    242,
                    280,
                    "Starlette iterates streamed chunks and coordinates stream sending with disconnect listening for ASGI 2.0",
                ),
            ],
            {
                "test_raw_stream_cancellation": _function(
                    ["response-serialization"],
                    _STREAM_CANCELLATION,
                    "The source's raw async generator has no internal await and is invoked through a direct ASGI call bounded by an external cancellation scope.",
                    [
                        _link(
                            "tests/fixtures/input-recipes/parity/stream-cancellation.yaml",
                            "fastapi.stream-cancellation.raw-async-generator",
                            ["cancel-raw-stream"],
                            _STREAM_CANCELLATION,
                        ),
                    ],
                    [
                        _source(
                            "tests/test_stream_cancellation.py",
                            24,
                            30,
                            "The raw StreamingResponse route yields indefinitely without an internal await",
                        ),
                        _source(
                            "tests/test_stream_cancellation.py",
                            42,
                            75,
                            "The source directly calls the ASGI app, leaves receive pending, and cancels the call under a timeout",
                        ),
                        _source(
                            "tests/test_stream_cancellation.py",
                            78,
                            83,
                            "The source asserts that cancellation returns instead of hanging",
                        ),
                    ],
                    "The upstream helper reports success when cancellation was caught or at least one body chunk was emitted, then the test asserts that result. The independent recipe uses a finite cancellation deadline and observes response status, ordered headers, and cancellation; it does not compare stream bytes or chunk count, model an http.disconnect event, backpressure, or network-client behavior. Generic StreamingResponse transport belongs to Starlette 1.6.0.",
                )
                | {
                    "stimulus_notes": "Independent direct-ASGI cancellation input: tests/fixtures/input-recipes/parity/stream-cancellation.yaml::fastapi.stream-cancellation.raw-async-generator (action cancel-raw-stream). The recipe records no expected output and observes only response status, headers, and the outer cancellation outcome."
                },
                "test_jsonl_stream_cancellation": _function(
                    ["response-serialization"],
                    _STREAM_CANCELLATION,
                    "The source's async JSON Lines generator has no internal await and is invoked through the same direct ASGI timeout harness.",
                    [
                        _link(
                            "tests/fixtures/input-recipes/parity/stream-cancellation.yaml",
                            "fastapi.stream-cancellation.jsonl-async-generator",
                            ["cancel-jsonl-stream"],
                            _STREAM_CANCELLATION,
                        )
                    ],
                    [
                        _source(
                            "tests/test_stream_cancellation.py",
                            33,
                            39,
                            "The JSON Lines route yields integer items indefinitely without an internal await",
                        ),
                        _source(
                            "tests/test_stream_cancellation.py",
                            42,
                            75,
                            "The source directly calls the ASGI app, leaves receive pending, and cancels the call under a timeout",
                        ),
                        _source(
                            "tests/test_stream_cancellation.py",
                            86,
                            89,
                            "The source asserts that JSON Lines cancellation returns instead of hanging",
                        ),
                        _source(
                            "docs/en/docs/tutorial/stream-json-lines.md",
                            75,
                            85,
                            "The JSON Lines documentation describes async generator routes and streamed serialization",
                        ),
                    ],
                    "The upstream helper reports success when cancellation was caught or at least one body chunk was emitted, then the test asserts that result. The independent recipe uses a finite cancellation deadline and observes response status, ordered headers, and cancellation; it does not compare stream bytes or chunk count, model an http.disconnect event, backpressure, or network-client behavior. Generic StreamingResponse transport belongs to Starlette 1.6.0.",
                )
                | {
                    "stimulus_notes": "Independent direct-ASGI cancellation input: tests/fixtures/input-recipes/parity/stream-cancellation.yaml::fastapi.stream-cancellation.jsonl-async-generator (action cancel-jsonl-stream). The recipe records no expected output and observes only response status, headers, and the outer cancellation outcome."
                },
            },
        ),
        "stimulus_notes": "Two independent direct-ASGI workflows cover the module's raw and JSON Lines cancellation tests. The composed request-scoped yield-dependency cleanup probe is mapped under the separate dependency-after-yield source module. Fixtures record no expected output. Starlette 1.6.0 owns generic StreamingResponse send and disconnect mechanics; recipes do not model TestClient, network transport, streamed body bytes, chunk counts, or backpressure.",
    },
}
