"""Reviewed section mappings for FastAPI's async documentation page."""

_PAGE = "async.md"
_ASYNC_HANDLERS = "tests/fixtures/input-recipes/parity/docs-async-handlers.yaml"
_WORKER_DISPATCH = "tests/fixtures/input-recipes/parity/worker-dispatch.yaml"
_NESTED_DEPENDENCIES = (
    "tests/fixtures/input-recipes/parity/dependency-sync-parent-nested-async.yaml"
)
_HTTP = ["http.body.bytes", "http.status"]
_DISPATCH = [
    "asgi.send.message_types",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
]
_NESTED = [
    "http.body.bytes",
    "http.status",
]


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_MIXED_CALLABLES = "fastapi.docs.async-handlers.mixed-callables"
_SYNC_ENDPOINT = "fastapi.worker-dispatch.sync-endpoint-without-response-model"
_ASYNC_ENDPOINT = "fastapi.worker-dispatch.async-endpoint-without-response-model"
_SYNC_ENDPOINT_ASYNC_DEP = (
    "fastapi.worker-dispatch.sync-endpoint-async-dependency-response-validation"
)
_ASYNC_ENDPOINT_SYNC_DEP = (
    "fastapi.worker-dispatch.async-endpoint-sync-dependency-response-validation"
)
_NESTED_ALTERNATION = "fastapi.dependencies.sync-async-deeper-alternation"
_DISPATCH_ACTIONS = [
    "invoke-user-endpoint",
    "read-completed-callback-and-raw-send-traces",
]


DOC_SECTION_CASE_MAPPINGS_ASYNC_20261015 = {
    (_PAGE, "concurrency-and-async-await"): _excluded(
        "Concurrency and async / await { #concurrency-and-async-await }",
        1,
        444,
        (
            "The page heading is an overview, not a separate FastAPI operation. Its concrete "
            "path-operation and dependency dispatch claims are assigned to the narrower "
            "sections below; language-runtime, third-party I/O, concurrency, and performance "
            "claims are not established by these request inputs."
        ),
        (
            "The source introduces the page as details about async syntax and background "
            "context (lines 1-3). The mixed endpoint example is mapped under `in-a-hurry`; "
            "the async endpoint example and dispatch details are mapped under `async-and-await`, "
            "`more-technical-details`, and the child headings of `very-technical-details`. "
            "The conceptual and performance discussion has no distinct request contract."
        ),
    ),
    (_PAGE, "in-a-hurry"): _workflow(
        "In a hurry? { #in-a-hurry }",
        5,
        56,
        _ASYNC_HANDLERS,
        [_MIXED_CALLABLES],
        ["sync-endpoint", "async-endpoint"],
        _HTTP,
        (
            "One sync and one async route return ordinary JSON values; the selected actions "
            "observe only status and body bytes. This samples successful mixed endpoint "
            "declarations, not awaited third-party I/O, blocking libraries, throughput, or "
            "thread-pool limits."
        ),
        (
            "The pinned page recommends `async def` when the called library is awaitable, "
            "`def` for blocking libraries, and says the forms can be mixed (lines 9-55). "
            "FastAPI 0.157.0 classifies path-operation callables and dispatches them in "
            "`../fastapi/fastapi/routing.py:417-423,364-377,746-750`; the independent workflow "
            "samples one successful route of each declaration form."
        ),
    ),
    (_PAGE, "asynchronous-code"): _excluded(
        "Asynchronous Code { #asynchronous-code }",
        67,
        302,
        (
            "This span explains general asynchronous scheduling, I/O-bound work, and a "
            "burger analogy. Its `file` and `query` matches are ordinary prose, and it does "
            "not define a FastAPI operation or a distinct request."
        ),
        (
            "Lines 67-95 define asynchronous waiting in language/runtime terms; lines 96-302 "
            "continue with concurrency and parallelism analogies and broad web-performance "
            "claims. Those claims do not identify a FastAPI API input or a functional "
            "observation, and event-loop scheduling remains outside this FastAPI section "
            "contract."
        ),
    ),
    (_PAGE, "burger-conclusion"): _excluded(
        "Burger Conclusion { #burger-conclusion }",
        236,
        255,
        (
            "The section concludes a concurrency analogy and makes broad framework "
            "performance comparisons; it specifies no independent FastAPI request behavior."
        ),
        (
            "The pinned text describes waiting in web applications and asserts comparative "
            "performance (lines 236-255). Functional status/body observations cannot verify "
            "benchmark claims, and the matched `query` term is part of the prose rather than "
            "a FastAPI parameter declaration."
        ),
    ),
    (_PAGE, "async-and-await"): _workflow(
        "`async` and `await` { #async-and-await }",
        303,
        387,
        _ASYNC_HANDLERS,
        [_MIXED_CALLABLES],
        ["async-endpoint"],
        _HTTP,
        (
            "The async route action observes a successful async path-operation response. It "
            "does not call or await the page's `get_burgers` helper, validate Python's "
            "coroutine protocol, or establish third-party library behavior."
        ),
        (
            "The page's `/burgers` example is an async path operation that awaits a helper "
            "(lines 343-350). FastAPI 0.157.0 awaits coroutine-classified path operations "
            "in `../fastapi/fastapi/routing.py:364-377,746-750`; ordinary Python `await` "
            "semantics and the external helper remain outside this mapped sample."
        ),
    ),
    (_PAGE, "more-technical-details"): _workflow(
        "More technical details { #more-technical-details }",
        352,
        363,
        _ASYNC_HANDLERS,
        [_MIXED_CALLABLES],
        ["async-endpoint"],
        _HTTP,
        (
            "This action samples one successful async path operation. It does not establish "
            "how standalone Python coroutines are started or how an external helper behaves."
        ),
        (
            "The section says FastAPI calls the first async function when it is a path "
            "operation (lines 354-360). FastAPI's coroutine classification and endpoint "
            "dispatch are implemented in `../fastapi/fastapi/routing.py:417-423,364-377,746-750`; "
            "the linked input observes only the response from one async route."
        ),
    ),
    (_PAGE, "other-forms-of-asynchronous-code"): _excluded(
        "Other forms of asynchronous code { #other-forms-of-asynchronous-code }",
        374,
        387,
        (
            "This section compares earlier language and ecosystem approaches such as "
            "threads, Gevent, and callbacks; it defines no FastAPI-specific operation."
        ),
        (
            "The page attributes threads and Gevent to earlier Python usage and describes "
            "JavaScript callbacks (lines 374-387). The lexical `callback` match refers to "
            "that general comparison; no FastAPI callback API is invoked."
        ),
    ),
    (_PAGE, "very-technical-details"): _excluded(
        "Very Technical Details { #very-technical-details }",
        404,
        444,
        (
            "This heading is an umbrella for the specific path-operation, dependency, "
            "sub-dependency, and utility-function claims in its child sections; it adds no "
            "separate input behavior."
        ),
        (
            "Lines 404-414 are a warning and introduction. The runtime claims in the "
            "remainder are reviewed individually under `path-operation-functions`, "
            "`dependencies`, `sub-dependencies`, and `other-utility-functions`, each with "
            "its own narrower input mapping or source-backed exclusion."
        ),
    ),
    (_PAGE, "path-operation-functions"): _workflow(
        "Path operation functions { #path-operation-functions }",
        416,
        423,
        _WORKER_DISPATCH,
        [_SYNC_ENDPOINT, _ASYNC_ENDPOINT],
        _DISPATCH_ACTIONS,
        _DISPATCH,
        (
            "The selected sync and async endpoint cases inspect the route response and the "
            "workload's public callback trace. They sample one no-response-model endpoint "
            "of each kind and the raw ASGI-send selectors. They do not measure scheduling "
            "fairness, throughput, or thread-pool limits."
        ),
        (
            "The page states that a normal `def` path operation runs in an external "
            "threadpool and that trivial compute-only handlers generally should use "
            "`async def` (lines 418-422). FastAPI 0.157.0 awaits a coroutine path operation "
            "or delegates a sync one to Starlette's `run_in_threadpool` from "
            "`../fastapi/fastapi/routing.py:364-377`; thread-pool implementation and generic "
            "ASGI behavior belong to the pinned Starlette 1.6.0 contract."
        ),
    ),
    (_PAGE, "dependencies"): _workflow(
        "Dependencies { #dependencies }",
        424,
        427,
        _WORKER_DISPATCH,
        [_SYNC_ENDPOINT_ASYNC_DEP, _ASYNC_ENDPOINT_SYNC_DEP],
        _DISPATCH_ACTIONS,
        _DISPATCH,
        (
            "Two selected cases pair a sync dependency with an async endpoint and an async "
            "dependency with a sync endpoint. Each observes one probe and the resulting "
            "public trace and raw-send selectors. This does not cover arbitrary dependency "
            "signatures, caching, or nesting."
        ),
        (
            "The page applies the same `def` versus `async def` rule to dependencies "
            "(lines 424-426). FastAPI 0.157.0 recursively solves dependencies and awaits "
            "coroutine dependencies or calls synchronous ones through `run_in_threadpool` "
            "in `../fastapi/fastapi/dependencies/utils.py:657-758`; Starlette owns the "
            "generic worker-pool implementation."
        ),
    ),
    (_PAGE, "sub-dependencies"): _workflow(
        "Sub-dependencies { #sub-dependencies }",
        428,
        431,
        _NESTED_DEPENDENCIES,
        [_NESTED_ALTERNATION],
        ["alternating-parents-use-resolved-values"],
        _NESTED,
        (
            "One successful request traverses an async leaf, sync parent, async parent, "
            "sync root, and async endpoint; its public body exposes resolved values and "
            "ordered user events. This samples one alternating graph, not all graph shapes, "
            "branching, or thread-pool limits."
        ),
        (
            "The source says nested dependencies may mix normal and async functions "
            "(lines 428-430). FastAPI 0.157.0 constructs and recursively solves "
            "dependency nodes in "
            "`../fastapi/fastapi/dependencies/utils.py:314-389,657-758`; the linked input "
            "uses an independent mixed sync/async graph and records only its public response."
        ),
    ),
    (_PAGE, "other-utility-functions"): _excluded(
        "Other utility functions { #other-utility-functions }",
        432,
        444,
        (
            "The page explicitly says FastAPI does not change how user code directly calls "
            "ordinary or async utility functions; their call and await semantics are Python "
            "behavior rather than a FastAPI operation."
        ),
        (
            "Lines 434-438 contrast functions FastAPI calls for users with utility functions "
            "the application calls directly. The path-operation and dependency dispatch "
            "claims are mapped in their child sections; this section contributes no separate "
            "FastAPI API stimulus."
        ),
    ),
}
