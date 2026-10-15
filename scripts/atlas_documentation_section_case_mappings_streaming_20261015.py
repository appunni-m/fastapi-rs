"""Reviewed section mappings for the FastAPI streaming documentation pages.

The mapped recipes are existing input-only workflows. Scope notes identify the
exact documentation examples they sample and keep aggregate-body observations
separate from chunk-boundary, timing, and cancellation claims.
"""


def _workflow(heading, start, end, recipe, case_ids, actions, selectors, note, rationale):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": case_ids,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        mapping["action_ids"] = actions
    return mapping


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_STREAM_DATA = "tests/fixtures/input-recipes/parity/stream-data-tutorials-upstream.yaml"
_SSE_TUTORIAL001 = (
    "tests/fixtures/input-recipes/parity/server-sent-events-tutorial001-upstream.yaml"
)
_JSONL_DOCS = "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml"

DOC_SECTION_CASE_MAPPINGS_STREAMING_20261015 = {
    ("advanced/stream-data.md", "stream-data"): _workflow(
        "Stream Data { #stream-data }",
        1,
        117,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial001.generator-forms"],
        None,
        _HTTP,
        (
            "This whole-page sample covers the documented text and byte generator forms in "
            "docs_src/stream_data/tutorial001_py310.py:20-65. It observes completed response "
            "bodies and metadata; it does not observe individual ASGI chunks, delivery "
            "timing, or client disconnect behavior."
        ),
        (
            "FastAPI's raw generator path forwards chunks to the declared response class "
            "(fastapi/routing.py:683-704); Starlette 1.6.0 owns generic StreamingResponse "
            "iteration and ASGI emission (starlette/responses.py:222-281)."
        ),
    ),
    ("advanced/stream-data.md", "use-cases"): _excluded(
        "Use Cases { #use-cases }",
        13,
        20,
        (
            "The section names possible LLM, large-file, video, and audio uses but defines "
            "no endpoint or distinct FastAPI behavior. The following generator sections "
            "cover the concrete response integration."
        ),
        (
            "These are workload examples rather than a separate public contract; the atlas "
            "does not infer behavior from a use-case description."
        ),
    ),
    ("advanced/stream-data.md", "a-streamingresponse-with-yield"): _workflow(
        "A `StreamingResponse` with `yield` { #a-streamingresponse-with-yield }",
        21,
        50,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial001.generator-forms"],
        ["read-telemetry-story-async-typed"],
        _HTTP,
        (
            "The selected action corresponds to the async typed string generator in "
            "docs_src/stream_data/tutorial001_py310.py:20-24. The recipe observes the "
            "completed body, headers, and status, not chunk boundaries or incremental arrival."
        ),
        (
            "FastAPI recognizes the generator path and passes its yielded strings to the "
            "selected StreamingResponse (fastapi/routing.py:683-704); generic response "
            "transport is Starlette-owned."
        ),
    ),
    ("advanced/stream-data.md", "non-async-path-operation-functions"): _workflow(
        "Non-async *path operation functions* { #non-async-path-operation-functions }",
        29,
        34,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial001.generator-forms"],
        ["read-telemetry-story-sync-typed"],
        _HTTP,
        (
            "The action corresponds to the synchronous typed string generator in "
            "docs_src/stream_data/tutorial001_py310.py:26-29. Only its completed HTTP body "
            "and response metadata are selected; scheduler timing is not observed."
        ),
        (
            "The route accepts a synchronous generator as the StreamingResponse content; "
            "Starlette owns generic iteration and transport. This mapping makes no separate "
            "threadpool-performance claim."
        ),
    ),
    ("advanced/stream-data.md", "no-annotation"): _workflow(
        "No Annotation { #no-annotation }",
        35,
        44,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial001.generator-forms"],
        ["read-telemetry-story-async-inferred"],
        _HTTP,
        (
            "The action corresponds to the unannotated async string generator in "
            "docs_src/stream_data/tutorial001_py310.py:32-35. It samples response output "
            "only; it does not infer or compare type-annotation handling beyond that route."
        ),
        (
            "The documented raw StreamingResponse path does not run FastAPI's stream-item "
            "JSON serializer (fastapi/routing.py:686-704)."
        ),
    ),
    ("advanced/stream-data.md", "stream-bytes"): _workflow(
        "Stream Bytes { #stream-bytes }",
        45,
        50,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial001.generator-forms"],
        ["read-telemetry-story-bytes-async-typed"],
        _HTTP,
        (
            "The selected action corresponds to the async typed byte generator in "
            "docs_src/stream_data/tutorial001_py310.py:44-47. The recipe compares the "
            "completed byte body and response metadata, not byte-chunk boundaries."
        ),
        (
            "FastAPI forwards each raw yielded byte value to the response class without "
            "JSON conversion (fastapi/routing.py:683-704); Starlette owns stream emission."
        ),
    ),
    ("advanced/stream-data.md", "a-custom-pngstreamingresponse"): _workflow(
        "A Custom `PNGStreamingResponse` { #a-custom-pngstreamingresponse }",
        51,
        117,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial002.binary-generator-forms"],
        ["read-raster-async-typed"],
        _HTTP,
        (
            "The action corresponds to the custom response class and async typed route in "
            "docs_src/stream_data/tutorial002_py310.py:19-27. It samples the final binary "
            "body and response headers, including the declared media type; it does not "
            "inspect chunk boundaries."
        ),
        (
            "FastAPI accepts the user response class for the route and forwards the yielded "
            "bytes (fastapi/routing.py:683-704); media-type response construction and "
            "streaming transport are Starlette response behavior."
        ),
    ),
    ("advanced/stream-data.md", "simulate-a-file"): _workflow(
        "Simulate a File { #simulate-a-file }",
        65,
        84,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial002.binary-generator-forms"],
        ["read-raster-async-typed"],
        _HTTP,
        (
            "The action corresponds to the BytesIO-backed generator in "
            "docs_src/stream_data/tutorial002_py310.py:12-14,23-27. It samples the final "
            "image body and headers but does not observe file closure or per-chunk delivery."
        ),
        (
            "The route integration passes the generator to StreamingResponse; the fixture "
            "uses in-memory BytesIO and therefore does not claim filesystem or real-file "
            "lifecycle behavior."
        ),
    ),
    ("advanced/stream-data.md", "files-and-async"): _excluded(
        "Files and Async { #files-and-async }",
        85,
        110,
        (
            "The section's main FastAPI claim is that a synchronous path operation avoids "
            "blocking the event loop by running on a worker thread. The closest existing "
            "recipe selects only a completed in-memory BytesIO response and has no event-loop "
            "responsiveness or scheduling observation; it cannot substantiate that claim."
        ),
        (
            "The documented route is docs_src/stream_data/tutorial002_py310.py:30-34. "
            "Its behavior needs a page-linked input with an observable concurrent request "
            "or scheduling effect before it can be claimed here."
        ),
    ),
    ("advanced/stream-data.md", "yield-from"): _workflow(
        "`yield from` { #yield-from }",
        111,
        117,
        _STREAM_DATA,
        ["fastapi.tutorial.stream-data.tutorial002.binary-generator-forms"],
        ["read-raster-sync-forward"],
        _HTTP,
        (
            "The selected action corresponds to the synchronous `yield from` route in "
            "docs_src/stream_data/tutorial002_py310.py:37-40. It observes the completed "
            "response only; Python's generator delegation semantics are not attributed to FastAPI."
        ),
        (
            "The documentation explicitly identifies `yield from` as Python syntax. The "
            "mapping selects only FastAPI's use of that generator as response content."
        ),
    ),
    ("tutorial/server-sent-events.md", "server-sent-events-sse"): _workflow(
        "Server-Sent Events (SSE) { #server-sent-events-sse }",
        1,
        120,
        _SSE_TUTORIAL001,
        ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
        None,
        _HTTP,
        (
            "The whole-page sample covers the four documented async/sync and typed/untyped "
            "route forms from docs_src/server_sent_events/tutorial001_py310.py:22-43. It "
            "observes aggregated bodies and response metadata, not event chunk boundaries, "
            "reconnection, or delivery timing."
        ),
        (
            "FastAPI encodes yielded values into SSE fields in fastapi/routing.py:520-556; "
            "EventSourceResponse supplies the response marker and media type in "
            "fastapi/sse.py:20-34, while Starlette owns generic streaming transport."
        ),
    ),
    ("tutorial/server-sent-events.md", "what-are-server-sent-events"): _excluded(
        "What are Server-Sent Events? { #what-are-server-sent-events }",
        13,
        35,
        (
            "This section explains the SSE protocol and links to the binary streaming guide; "
            "it does not define a FastAPI-specific endpoint or observable library behavior."
        ),
        (
            "The SSE wire format is covered by the FastAPI response examples in the following "
            "sections; protocol background alone is not support evidence."
        ),
    ),
    ("tutorial/server-sent-events.md", "stream-sse-with-fastapi"): _workflow(
        "Stream SSE with FastAPI { #stream-sse-with-fastapi }",
        36,
        71,
        _SSE_TUTORIAL001,
        ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
        ["stream-async-typed"],
        _HTTP,
        (
            "The selected action corresponds to the async typed `Item` generator in "
            "docs_src/server_sent_events/tutorial001_py310.py:10-25. It samples the completed "
            "SSE response and metadata; it does not measure individual event arrival or the "
            "performance advice in the tip."
        ),
        (
            "FastAPI validates/serializes typed stream items and wraps them in SSE data fields "
            "(fastapi/routing.py:492-518,520-551); Starlette 1.6.0 supplies generic "
            "StreamingResponse transport."
        ),
    ),
    ("tutorial/server-sent-events.md", "non-async-path-operation-functions"): _workflow(
        "Non-async *path operation functions* { #non-async-path-operation-functions }",
        56,
        65,
        _SSE_TUTORIAL001,
        ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
        ["stream-sync-typed"],
        _HTTP,
        (
            "The action corresponds to the synchronous typed generator in "
            "docs_src/server_sent_events/tutorial001_py310.py:28-31. It samples the complete "
            "response body and metadata, not worker scheduling or event-loop responsiveness."
        ),
        (
            "FastAPI accepts the synchronous generator for this SSE route; stream iteration uses "
            "the pinned Starlette integration. The mapping makes no timing or performance claim."
        ),
    ),
    ("tutorial/server-sent-events.md", "no-return-type"): _workflow(
        "No Return Type { #no-return-type }",
        66,
        71,
        _SSE_TUTORIAL001,
        ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
        ["stream-async-untyped"],
        _HTTP,
        (
            "The action corresponds to the unannotated async route in "
            "docs_src/server_sent_events/tutorial001_py310.py:34-37. It samples one completed "
            "SSE body and metadata, not alternate item values or per-event timing."
        ),
        (
            "FastAPI applies its untyped stream-item encoder before writing SSE data fields "
            "(fastapi/routing.py:516-518,546-551)."
        ),
    ),
    ("tutorial/server-sent-events.md", "serversentevent"): _workflow(
        "`ServerSentEvent` { #serversentevent }",
        72,
        81,
        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial002-upstream.yaml",
        ["fastapi.tutorial.server-sent-events.tutorial002.event-fields"],
        ["stream-event-fields"],
        _HTTP,
        (
            "The action corresponds to docs_src/server_sent_events/tutorial002_py310.py:10-26 "
            "and samples data, event, id, retry, and comment encoding in the aggregate response "
            "body. It does not observe event chunk boundaries or reconnect behavior."
        ),
        (
            "FastAPI maps ServerSentEvent fields to SSE wire-format bytes in "
            "fastapi/routing.py:524-545, backed by the public model in fastapi/sse.py:52-156."
        ),
    ),
    ("tutorial/server-sent-events.md", "raw-data"): _workflow(
        "Raw Data { #raw-data }",
        82,
        95,
        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial003-upstream.yaml",
        ["fastapi.tutorial.server-sent-events.tutorial003.raw-log-data"],
        ["stream-raw-logs"],
        _HTTP,
        (
            "The action corresponds to the `raw_data` log generator in "
            "docs_src/server_sent_events/tutorial003_py310.py:9-17. It samples the final event "
            "body and response metadata; invalid mutually exclusive field construction is not "
            "covered."
        ),
        (
            "FastAPI routes `ServerSentEvent.raw_data` directly to the event formatter "
            "(fastapi/routing.py:530-545); the model's mutual-exclusion rule is defined in "
            "fastapi/sse.py:148-156."
        ),
    ),
    ("tutorial/server-sent-events.md", "resuming-with-last-event-id"): _workflow(
        "Resuming with `Last-Event-ID` { #resuming-with-last-event-id }",
        96,
        103,
        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial004-upstream.yaml",
        ["fastapi.tutorial.server-sent-events.tutorial004.resume-stream"],
        None,
        _HTTP,
        (
            "The selected case's three requests cover the route in "
            "docs_src/server_sent_events/tutorial004_py310.py:23-31 with no header and two "
            "Last-Event-ID values. It samples response bodies and metadata, not browser reconnects."
        ),
        (
            "FastAPI binds the Last-Event-ID header as an input parameter and passes the "
            "selected stream items to SSE encoding; client reconnection itself is browser behavior."
        ),
    ),
    ("tutorial/server-sent-events.md", "sse-with-post"): _workflow(
        "SSE with POST { #sse-with-post }",
        104,
        111,
        "tests/fixtures/input-recipes/parity/server-sent-events-tutorial005-upstream.yaml",
        ["fastapi.tutorial.server-sent-events.tutorial005.post-chat-stream"],
        ["post-chat-stream"],
        _HTTP,
        (
            "The action corresponds to the POST chat generator in "
            "docs_src/server_sent_events/tutorial005_py310.py:10-19. It samples request-to-stream "
            "HTTP behavior and the aggregate output; it does not model an MCP client."
        ),
        (
            "FastAPI's EventSourceResponse marker is documented for any HTTP method "
            "(fastapi/sse.py:20-30), and the recipe exercises the POST route's streamed items."
        ),
    ),
    ("tutorial/server-sent-events.md", "technical-details"): _workflow(
        "Technical Details { #technical-details }",
        112,
        120,
        _SSE_TUTORIAL001,
        ["fastapi.tutorial.server-sent-events.tutorial001.stream-routes"],
        ["stream-async-typed"],
        _HTTP,
        (
            "The selected response captures ordinary stream headers and body for the "
            "documented route. It can compare cache/buffering headers but does not wait through "
            "a 15-second idle period, so the timed keepalive ping remains unverified."
        ),
        (
            "FastAPI adds Cache-Control and X-Accel-Buffering headers and inserts keepalive "
            "comments on timeout (fastapi/routing.py:585-646); the current finite recipe only "
            "supports the response metadata portion of this section."
        ),
    ),
    ("tutorial/stream-json-lines.md", "stream-json-lines"): _workflow(
        "Stream JSON Lines { #stream-json-lines }",
        1,
        111,
        _JSONL_DOCS,
        ["fastapi.docs.documentation-wave.http-behaviors.stream-json-lines"],
        ["dispatch"],
        _HTTP,
        (
            "This whole-page sample is the typed async JSON Lines response from "
            "docs_src/stream_json_lines/tutorial001_py310.py:9-24, adapted as an independent "
            "two-item workload. It observes aggregate body bytes and response metadata, not "
            "incremental item arrival."
        ),
        (
            "FastAPI serializes each JSON stream item and appends a line terminator before "
            "constructing StreamingResponse (fastapi/routing.py:495-518,647-682); Starlette "
            "owns generic stream transport."
        ),
    ),
    ("tutorial/stream-json-lines.md", "what-is-a-stream"): _excluded(
        "What is a Stream? { #what-is-a-stream }",
        11,
        36,
        (
            "Conceptual explanation and sequence diagram only; it does not declare a FastAPI "
            "endpoint or distinct FastAPI behavior."
        ),
        (
            "The section describes timing between an application, network, and consumer. "
            "Existing cancellation inputs do not prove incremental delivery or client "
            "processing order, so those claims remain outside this mapping."
        ),
    ),
    ("tutorial/stream-json-lines.md", "json-lines"): _workflow(
        "JSON Lines { #json-lines }",
        37,
        64,
        _JSONL_DOCS,
        ["fastapi.docs.documentation-wave.http-behaviors.stream-json-lines"],
        ["dispatch"],
        _HTTP,
        (
            "The action samples a typed async route's completed JSON Lines body and content "
            "metadata, corresponding to docs_src/stream_json_lines/tutorial001_py310.py:9-24. "
            "The flattened body does not prove separate ASGI chunk delivery."
        ),
        (
            "FastAPI serializes each yielded item and appends a newline "
            "(fastapi/routing.py:651-682); the recipe selects only the aggregate HTTP response."
        ),
    ),
    ("tutorial/stream-json-lines.md", "use-cases"): _excluded(
        "Use Cases { #use-cases }",
        65,
        74,
        (
            "This section lists possible JSON telemetry/LLM uses and links to the separate "
            "binary-stream guide; it contains no distinct route or FastAPI contract."
        ),
        (
            "Use-case descriptions are not independent input/output behavior. Concrete JSONL "
            "response behavior is mapped in the adjacent implementation section."
        ),
    ),
    ("tutorial/stream-json-lines.md", "stream-json-lines-with-fastapi"): _workflow(
        "Stream JSON Lines with FastAPI { #stream-json-lines-with-fastapi }",
        75,
        108,
        _JSONL_DOCS,
        ["fastapi.docs.documentation-wave.http-behaviors.stream-json-lines"],
        ["dispatch"],
        _HTTP,
        (
            "The action corresponds to the successful typed async example in "
            "docs_src/stream_json_lines/tutorial001_py310.py:9-24 and observes its aggregate "
            "HTTP body and metadata. It does not exercise an invalid response item, filtering, "
            "or the generated OpenAPI schema."
        ),
        (
            "FastAPI's stream-item validation and JSON encoding path is in "
            "fastapi/routing.py:492-518,647-682. The page-linked recipe confirms successful "
            "serialization only; schema and error claims remain outside this mapping."
        ),
    ),
    ("tutorial/stream-json-lines.md", "non-async-path-operation-functions"): _excluded(
        "Non-async *path operation functions* { #non-async-path-operation-functions }",
        93,
        102,
        (
            "No existing recipe linked to this documentation page selects the documented "
            "synchronous JSONL variant. The nearby streaming-runtime sync case lacks the "
            "required page-source evidence, and the current page-linked recipe observes only "
            "the async typed route."
        ),
        (
            "The documented source is docs_src/stream_json_lines/tutorial001_py310.py:27-30. "
            "The body-only async sample cannot substantiate sync-generator or threadpool behavior."
        ),
    ),
    ("tutorial/stream-json-lines.md", "no-return-type"): _excluded(
        "No Return Type { #no-return-type }",
        103,
        108,
        (
            "No existing page-linked recipe observes the unannotated route's JSON encoder "
            "output. The page-linked HTTP workflow uses a typed async route, while the "
            "cancellation workflow records no response body."
        ),
        (
            "The documented source is docs_src/stream_json_lines/tutorial001_py310.py:33-36. "
            "The encoder fallback claim needs an input that selects this untyped path."
        ),
    ),
    ("tutorial/stream-json-lines.md", "server-sent-events-sse"): _excluded(
        "Server-Sent Events (SSE) { #server-sent-events-sse }",
        109,
        111,
        (
            "This section only links to the separate Server-Sent Events chapter and adds no "
            "independent JSON Lines behavior."
        ),
        (
            "SSE behavior is mapped to its own tutorial and input recipes; it is not part of "
            "the JSON Lines section contract."
        ),
    ),
}
