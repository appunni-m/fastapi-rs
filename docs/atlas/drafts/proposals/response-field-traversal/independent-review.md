# Response-field traversal7: independent source/input review

2026-10-05. Read-only review of the inactive proposal at
`/private/tmp/fastapi-rs-response-field-traversal-proposal-2026-10-05/`.
Only this review note was written. No proposal/input, active recipe, metadata,
documentation, Rust or sibling edits; no factory import, application, parity,
build, install or unit test execution. Parent owns current frozen measurements.

## Verdict and frozen inputs

No concrete source reachability, independence, deterministic observation or
schema-selector blocker found by reading the workload, recipe, schema9/worker,
pinned FastAPI 0.141.1 and Starlette 1.6.0 source. This is static clearance for
later admission, not live source/target evidence or a target support claim.

| File | SHA256 |
| --- | --- |
| response_field_traversal.py | 35aa2d46026953a69ac6284f6a0215c62df22e19ddac0018c9d31336224de4d9 |
| response-field-traversal.yaml | 3dfd1caa6573faa55edaef83e1eb166e4279a97542bda323a4ea8ab2de929c66 |
| review-plan.md | 8d5164a0825cf7755f3049c905578dd264a2ad29609cc73a882785b9bffd8ad2 |

Independent manual count, expanding the two shared state-action aliases:

| Case suffix | State reads | Other requests | Actions | Construction observations |
| --- | ---: | ---: | ---: | ---: |
| branch-second-construction-error-retry | 4 | 3 | 7 | 1 |
| parent-own-fields-before-child-traversal | 4 | 3 | 7 | 1 |
| earlier-full-direct-match-skips-later-include | 4 | 3 | 7 | 1 |
| earlier-partial-direct-match-reaches-later-full-include | 3 | 2 | 5 | 1 |
| unmatched-request-visits-both-includes | 3 | 3 | 6 | 1 |
| redirect-search-follows-initial-branch-traversal | 3 | 2 | 5 | 1 |
| returned-response-still-constructs-included-field | 3 | 2 | 5 | 1 |
| Total | 24 | 18 | **42** | **7** |

Seven case IDs and the action IDs within each case are distinct by inspection.
Every source-evidence path exists in the pinned source checkout. Factory binding
is the canonical positional `create_app(factory_input, event_trace)`. The future
workload path is a valid repository-relative .py path; its intentional absence
from the active index is not an inactive proposal defect. No static parser or
canonical admission/generation was run by this reviewer.

## Public source reachability and order

Pinned FastAPI commit: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
Pinned Starlette commit: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
Python3.12.13 and Pydantic2.13.4/core2.46.4 remain the stated proposal boundary.

1. **Cold state access.** `/state` is registered before every declaration/include,
   with response_model=None and an ordinary returned JSONResponse. APIRouter.app
   stops at its full match (`routing.py:2729-2735`). State reads therefore observe
   setup and the preceding request without triggering a later branch or retry.
   This differs deliberately from lifecycle16's later state route.
2. **Successful original setup.** Each original route creates its traced field
   during public get/post registration (`routing.py:1103-1114`). All includes have
   nonempty prefixes, avoiding the separate empty-prefix route-context traversal
   at3282-3295. The rejection flag is armed only after recursive declaration and
   inclusion complete; original model construction can succeed first.
3. **Later second construction failure.** The first branch request reaches
   effective_candidates (`routing.py:1601-1624`). Its first field succeeds, then
   the second user hook rejects before the candidate vector/version is assigned.
   The callback logs its actual build/rejection and consumes one user rejection.
   The next state read is earlier than the branch. Retrying the branch reconstructs
   its own contexts; first-label build repetition is publicly visible, followed by
   normal endpoint validation/serialization. Requesting the second route afterwards
   observes reuse of the successful branch. No partial native cache is inspected.
4. **Handler catches the matching error.** The custom error is an ordinary top-level
   ValueError subclass and is registered through app.exception_handler. ModelField
   only translates PydanticSchemaGenerationError (`utils.py:58-78`), so this custom
   error propagates from the hook. Starlette ExceptionMiddleware wraps the router
   and resolves registered handlers before response start
   (`middleware/exceptions.py:46-68`, `_exception_handler.py:31-65`). The async handler
   returns the actual class/message/path in a JSONResponse. Its annotations do not
   become route fields; this is a handler registration, not an endpoint declaration.
5. **Nested A/C before B.** Original declaration order is A/B/C during setup. The
   parent effective-candidate loop builds own A and C, creating a child branch
   record between them without materializing B (`routing.py:1609-1617`). The first
   A request stops before visiting that child. A later C request reaches the child
   during matching, builds B, finds no child path match, then dispatches C. The last
   B request reuses that child. Request/stage/build counters distinguish setup,
   parent construction and child traversal without a private route-context read.
6. **Earlier full versus partial.** An earlier full direct GET stops before the
   later include. The include-only path subsequently builds its own fields.
   In the separate POST-before-GET declaration, an earlier partial POST match is
   retained while the later included GET supplies a full match
   (`routing.py:2729-2743`). Endpoint labels and different values expose selection;
   build stages expose whether the include was reached. A later POST is a direct
   full-match control over the unchanged declarations.
7. **Miss and slash search.** A missing path traverses both includes before ordinary
   404 handling. The unslashed path similarly performs its first normal scan through
   both branches, then slash-redirection search revisits the successful branch cache
   (`routing.py:2744-2761`). The worker sends one request and does not automatically
   follow the redirect. Later declared-path requests expose field retention.
8. **Returned Response.** The included field is materialized before endpoint
   dispatch even though the endpoint will return JSONResponse. That returned value
   then bypasses response validation/serialization (`routing.py:711-714`). Exact
   non-int content, custom status/header, callbacks and raw sends expose both stages.

These statements are source readings used to assess inputs. No source outcomes
were executed or stored in the recipe or workload.

## Observation strength and determinism

Every HTTP action uses valid existing schema9 selections:

- http_response: selectors status/headers/body, comparison exact.
- asgi_send: singular selector message_types, comparison ordered.
- application_error: singular selector exception, comparison exact.
- Construction: outcome/exception_class/exception_message, comparison exact.

The checked definitions are in
`tests/fixtures/schemas/python-asgi-workflow-v9.schema.json`; worker.py418-447
extracts exact status/ordered headers/body and message types, and461-469 exposes
unhandled full exception class/message. The canonical factory call is at1253.

Schema9's asgi_send selector alone does not compare every message field. The
ordinary user wrapper fills that observation need: it encodes every prior
non-state message recursively, preserving bytes as typed hex, tuple/list shapes,
header order, every key and field presence, then forwards the original message
unchanged. Subsequent `/state` bodies are selected exactly, so message contents,
hook counts/order, validator/serializer calls and handler records are compared.
The state response excludes only its own recording to prevent recursive growth;
its status/headers/body/message types still have canonical runner observations.
Every final non-state request is followed by a selected state response.

A handled schema error has no unhandled application_error, but its actual full
class/message/path is in both the handler response and following state journal.
A missing or wrong handler is visible through exact status/body/application_error
and the wrapper's re-raised full error. A target that publishes an earlier field
and skips reconstructing it on retry changes schema-call counters/stages even if
later endpoint bytes agree. A target that constructs unvisited child fields or
rebuilds successful fields changes the ordered state trace.

The public error class is named independently at module scope and its message
uses an ordinary declaration label, with no object repr or address. Canonical
workload module naming is shared across source/target; the actual class name is
projected without rewriting it. Warning records retain ordered category and
unchanged message, with user stages/request counters but no filenames/frames.
The user hooks emit no intentional warning; internal narrow suppression and any
unexpected warning remain ordinary live observations. State/error/protocol values
are JSON-compatible fixed scalars/containers. No clocks, absolute IDs, GC effects,
concurrency, coroutine allocation or returned awaitables enter these inputs.

## Independence and bounded omissions

The workload imports public FastAPI/APIRouter/Request/JSONResponse, standard
Python modules and public Pydantic schema hooks. Declarative routes/prefixes/
methods/labels/values drive ordinary app construction. There is no case-ID read,
private cache/version/Default/APIRoute access, oracle import or target detection;
no expected output, normalization, copied upstream test or comparator change.

The one-use callback refusal is a normal public input on both implementations.
It is not a target-only fault and does not justify a new injected fault hook.
The retry observations cover branch publication through schema callback history;
they do not prove private adapter identity, finalizer timing, yielded-resource
cleanup or concurrent construction. Existing cleanup fault lanes stay separate.

There is no terminal 405 action: the partial-match case gates continuing to a later
full match. The miss/redirect cases gate their own scans. Dynamic route refresh,
empty-prefix traversal, raw route/context proxies, OpenAPI/URL traversal, warning
filter mutation, reentry/concurrency, streaming and sync worker scheduling are
outside this7 backlog. No absence here should become a broader compatibility claim.

Public mapping candidates for later admission are FastAPI.__init__/get/include_router/
exception_handler/__call__, APIRouter.__init__/get/include_router, Request's
query_params and url.path, and JSONResponse construction/returned response.
The partial-match case additionally exercises FastAPI.post. Pydantic hooks and
user exception classes are input protocols, not private FastAPI candidates.

The saved inputs remain unchanged and inactive. Parent owns future canonical
admission, identity checks, live oracle/unchanged-target diagnosis and any runtime
repair. Source/target exact receipts are required before accepting support.
