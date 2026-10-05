# Prospective worker dispatch parity slice

These independent input drafts are saved outside active inputs. Parent integration
has formatted the Python workload and validated the recipe through the repository
schema loader; source/target behavior remains unexecuted. The recipe uses its
intended future workload path, which requires reviewed manifest/index mappings
before activation.

Files in this directory:

- `worker_dispatch.py`: ordinary user app and public ASGI observer.
- `worker-dispatch.yaml`: 18 parity cases, no expected output or fault injection.
- `review-plan.md`: source evidence, admission gates and implementation design.

Independent read-only review by `override_reanalysis` found one recipe issue:
the repo's unique-key YAML loader does not support merge keys. Both recovery
actions now use explicit mappings and ordinary aliases. Final manual review
count is 18 cases / 54 actions, with no remaining actionable input issue.
The narrow marker-default correction was independently reviewed: two distinct
local Depends markers preserve selected route signatures and cache observations.
Schema validation is recorded below; live behavior still requires parity.

## Pins and source evidence

- FastAPI 0.141.1, checkout `/Users/lazytrot/work/fastapi`, commit
  `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0, `/Users/lazytrot/work/starlette`, commit
  `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`; sole source oracle.
- Starlette-RS sibling `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`, commit
  `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`; generic behavior stays sibling owned.
- CPython 3.12.13; Pydantic 2.13.4/core 2.46.4; AnyIO 4.12.1.

Exact source execution boundaries (FastAPI paths are checkout-relative):

| Source | Contract |
| --- | --- |
| `fastapi/routing.py:394` | Capture `_is_coroutine_callable(dependant.call)` while building the request handler. |
| `fastapi/routing.py:342-354` | After inputs/dependencies solve, await async endpoints on the loop; sync endpoints use `run_in_threadpool`. |
| `fastapi/routing.py:316-338` | Response model validation uses the original endpoint coroutine classification: sync endpoint validation in a worker; async endpoint validation on the loop. Serialize on the loop after validation in both branches. |
| `fastapi/routing.py:711-751` | Returned Response bypasses response-model validation; ordinary content validates/serializes, then uses eligible direct JSON bytes or selected response class. |
| `fastapi/dependencies/utils.py:640-680` | Child solving/own validation precede policy/cache decision; uncached sync dependency executes in a worker, async dependency is awaited. |
| `fastapi/dependencies/utils.py:681-745` | Own request input validation runs on the caller loop, not in the callable's later worker. |
| `fastapi/dependencies/utils.py:566-579` | Enter async generators directly; wrap sync generators with contextmanager + contextmanager_in_threadpool. |
| `fastapi/concurrency.py:19-38` | Sync contextmanager enter and exit are separate worker calls. Exit gets its own capacity limiter. |
| `fastapi/routing.py:138-159` | Function scope closes before response send; request scope surrounds sending/background work. Exceptions unwind yielded scopes before registered exception handling. |
| `starlette/concurrency.py:32-34` | Worker call is functools.partial plus `anyio.to_thread.run_sync`. |
| pinned AnyIO `_backends/_asyncio.py:2444-2505` | Copy context into worker; default abandonment is false and its cancel scope shields worker waiting. |

Response validation uses `from_attributes=True` (`fastapi/_compat/v2.py:182`). A
user awaitable returned *as a value* is therefore a legitimate attribute-backed
response-model input. Await the endpoint's own coroutine or the framework worker
awaitable exactly once; do not recursively await the endpoint result based on its
runtime type. The two AwaitablePayload controls create no coroutine until their
user `__await__` is actually invoked, avoiding unawaited-coroutine warning/GC races.

The recipe cites public upstream documents/tests supported by schema @9. Exact
code references above provide additional review evidence, not case inputs or
runtime dispatch keys. Cases require reviewed mappings to existing app-routing,
dependency, request validation, response validation/serialization and lifecycle
requirements before active integration. No support classifications are proposed
from static reading alone.

## Observations and determinism

The outer observer is ordinary user ASGI code. It records the request event-loop
thread privately, seeds a ContextVar, then invokes the public app unchanged.
Callbacks report only `on_loop` relationships and context values, never absolute
thread IDs/names, worker reuse, wall-clock times or thread-pool sizes. It restores
observer tokens after app completion so each sequential request starts from its
declared seed. Its request-exit trace captures the framework context before reset.

Pydantic input validators, sync/async dependencies, endpoint bodies, response
validators/serializers, typed public handlers, sync/async yielded scope enter/exit,
and one async background callback write deterministic markers. Sync resource
callbacks deliberately do not reset a ContextVar token captured during generator
enter: source exit receives another context copy and potentially another worker.
Two bound dependency edges share the same callable/default cache policy; traces
also expose input revalidation versus one cached dependency value.

The cases compare response status, ordered headers, body and ordered ASGI message
types. `/state` then exposes complete prior callback/send traces through an ordinary
JSONResponse. HTTP schema @9 has no generic workload_trace selector. The recorder
keeps every send field, ordered headers, byte values as hex, list/tuple shape and
field presence; it performs no source/target normalization. Recording happens
before invoking the user's send callable, so later mutation cannot rewrite history.

Worker handoffs are explicit protocols: an off-loop synchronous user callback
submits a coroutine to its captured request loop and waits for that future. The
coroutine records completion before the worker resumes. There is no timer, sleep
or ordering inference from elapsed time. A callback already on the loop records
that fact and returns without self-deadlock; that branch remains fully observed,
not treated as a skip or success. The spawned coroutine's ContextVar changes stay
in its task; callback context after resumption is also recorded. A product that
blocks the event loop while waiting for a worker may still hang this valid public
protocol; the runner's existing infrastructure timeout must report that failure,
not turn it into a fixture assertion.

## Proposed case groups

| Cases | Distinct observed behavior |
| --- | --- |
| 1-2 | Plain sync vs async endpoint dispatch with explicitly no response model; request input validation remains on loop. |
| 3-4 | Sync endpoint + async dependencies and async endpoint + sync dependencies; response validator placement follows endpoint kind, not last dependency/resume. Serializer stays on loop; worker ContextVar writes do not leak into the caller. |
| 5-6 | Both yielded scopes, opposite sync/async resource kinds and async background work; thread/context and success cleanup/send order. |
| 7-8 | Endpoint/dependency user error, typed handler, both cleanup scopes and successful follow-up after clearing the ordinary user failure switch. |
| 9-10 | Sync-route and async-route response-validation failure, public ResponseValidationError handler/body/locations, cleanup and recovery. |
| 11 | Endpoint input rejection after yielded/dependency solving; endpoint does not execute and validation remains on loop. |
| 12 | Serializer error is a PydanticSerializationError on loop, not ResponseValidationError; cleanup and recovery. |
| 13 | Returned JSONResponse bypasses declared response model; background/cleanup/send remain observable. |
| 14-16 | Deterministic worker-to-loop handoffs in sync endpoint, sync dependency and sync-route response validator. |
| 17-18 | Custom awaitable is the returned value from sync/async endpoint; source model validation reads attributes without another await. |

All outputs are obtained from the live selected product. Fixture helpers neither
import original FastAPI implementation helpers nor inspect target identity,
private runtime state, build mode, fixture IDs or internal dispatch.

## Adjacent raw ASGI gap must remain visible

Pinned Starlette `responses.py:162-169` emits a normal body message containing
`type` and `body`, with no `more_body` key. Native FastAPI
`fastapi-rs/src/application_runtime.rs` helper `response_body` currently adds
`more_body=False`; its `FastApiCall::send_body` constructs normal FastAPI default
JSON/422 responses through that helper. This is FastAPI-owned send construction.
The public raw-send recorder intentionally preserves the difference. Existing
message-type/status/body observations alone do not establish full send-field parity.
No fixture-side default insertion, normalization or observation omission is allowed.

Generic returned/custom responses use `start_returned_response` and sibling-owned
ASGI flow. In the pinned sibling, `starlette-rs-py/src/runtime_calls.rs:1034-1059`
`response_event_to_py` emits normal body `type`/`body` without `more_body`, and the
public Response wrapper supplies its body override. Streaming, middleware and
other generic sibling behaviors require separate ownership/evidence; do not edit
the sibling to mask a FastAPI helper mismatch. Parent should verify these exact
paths against the current source before a bounded send correction.

## Minimal native implementation design (separate from fixtures)

1. Retain source-equivalent original endpoint coroutine classification per HTTP
   route/handler at analysis, alongside existing streaming classification. The
   immutable classifier draft is a separate prerequisite; descriptor/LRU history
   effects and mutable callable internals must remain explicit limitations.
2. Keep dependency graph solving, policy timing, cache identity and endpoint own
   argument validation on the loop. After successful preparation, invoke ordinary
   sync HTTP endpoints through the pinned Starlette `run_in_threadpool` boundary;
   await ordinary async endpoints according to captured classification.
3. Distinguish the worker awaitable from the endpoint's returned Python value in
   pending state. Resume into response finishing once; do not recursively await a
   value merely because `is_awaitable(result)` is true. Do not move request input
   validation into the endpoint worker or rerun prepared inputs after resumption.
4. For a non-Response result with a response model, schedule only
   `adapter.validate_python(result, from_attributes=True)` in a worker when the
   original endpoint classification is sync. Retain an explicit response-validation
   pending state with owned adapter, original body and serialization configuration.
   Clone these under a short app borrow and release it before callbacks/awaits.
5. After validation resume, serialize once on the caller loop with existing flags
   and source-equivalent eligible dump_json/custom-response rules. Preserve original
   body and location-prefix conversion for Pydantic validation failures. Convert
   a validation failure to ResponseValidationError before existing exception/stack
   cleanup handling; propagate unrelated errors and serializer errors unchanged.
6. Preserve function/request exit stacks, request cache and completed graph cursor
   across both endpoint and validation awaits. Reuse current error cleanup guards
   for exceptions while awaiting/resuming. No re-selection of completed dependencies,
   re-reading cache policies, revalidation or repeated endpoint invocation on resume.
   Preserve source function close, response send, background and request close order.
7. Match FastAPI-owned normal body message fields and independently verify generic
   sibling response flow. Do not change the facade, introduce Python runtime helpers,
   unsafe code or broad lint suppressions.

Response adapter/context caches are separate optimizations, not substitutes for
worker semantics. In particular, schema generation/warnings/registration behavior
must be reviewed before moving adapter construction. These fixtures intentionally
exercise ordinary callback scheduling; they do not establish all response-model
or classifier contracts.

## Admission and unproven boundaries

After independent review, parent can integrate the two draft files, reviewed
requirement/fixture maps, and public API descriptor evidence. Run repo-mandated
materialization, index/metadata/static checks and fresh isolated identity-checked
source/target parity. Preserve every mismatch, including raw sends and callback
contexts. No unit tests, pytest, unittest or Cargo test. Equivalent benchmarks
require passing dispatch/context/error/cleanup/raw-send parity first; retain the
historical064 evidence as selected output-equivalent results with scheduler limits.

Cancellation is not executed by this proposal. Existing HTTP cancellation actions
use a duration, which cannot prove the deterministic event boundary requested here.
A future generic event-driven cancellation schedule must observe worker completion,
single cleanup and recovery against live source without race-based expectations.
Arbitrary concurrent request scheduling, capacity-limiter exhaustion, synchronous
background callbacks, custom response classes, streaming/WebSocket dispatch,
wrapped/partial/callable-instance mutable classification history and arbitrary
ContextVar payload aliasing remain separate frontiers. No full compatibility or
numerical performance claim follows from these unrun drafts.

## Parent static admission checks

The saved inactive copy passed `scripts.build_parity_inputs.read_recipe` using
the repository unique-key loader and schema @9: 18 cases and 54 actions. Ruff
formatting/checks also passed after the reviewed distinct-marker correction.
These checks do not bind active manifest/index requirements or establish live
source/target agreement; those remain required on activation.
