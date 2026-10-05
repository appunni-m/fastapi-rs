# Prospective ordinary HTTP worker dispatch

This draft is unapplied, unformatted, uncompiled and unexecuted. It changes only a
prospective copy of `fastapi-rs/src/application_runtime.rs` under `/private/tmp`.
It adds no Python facade code, unsafe code, lint suppressions or unit tests.

## Files and base

- Full copy: `/private/tmp/fastapi-rs-worker-dispatch-application_runtime.rs`.
- Unified patch: `/private/tmp/fastapi-rs-worker-dispatch.patch`.
- Exact base copy: `/private/tmp/fastapi-rs-worker-dispatch-base-application_runtime.rs`.
- Base commit: `cb4231984d692d66846b3820829068f4e34ae43f`.
- Base runtime SHA256: `f81e2d41ee7435befa249335ff5db3fd48b8a06769ded70af0dd438254cd066f`.
- Prospective runtime SHA256: `01ccc8f3fe52bd62c4d2518cddc6ef767349a675110329b81fb9ea01028f97e3`.
- Unified patch SHA256: `4b5de69314924a89af7e8bf6649f78e5068697df4fcc2913029d381650c3f86d`.

Root separately owns the source-equivalent immutable classifier/node-await patch,
ASGI send-field correction, reviewed mappings and fixture integration. This patch
does not change those helper/node/send sections. It calls the existing
`dependency_override_callable` during registration and therefore requires root's
classifier helper integration before claiming source coroutine classification.

Input-only proposal: `docs/atlas/drafts/proposals/worker-dispatch/worker_dispatch.py`,
`worker-dispatch.yaml`, and `review-plan.md`: 18 cases / 54 actions. The proposal's
static recipe/Ruff admission does not establish live behavior. Root owns fresh
normal and instrumented builds, identity checks, parity and benchmark admission.

## Pins and exact source order

FastAPI 0.141.1 oracle: `/Users/lazytrot/work/fastapi`,
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`. Starlette 1.6.0 sole oracle:
`/Users/lazytrot/work/starlette`, `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
Pinned sibling: `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`,
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. CPython 3.12.13, Pydantic 2.13.4 /
core 2.46.4, AnyIO 4.12.1. No sibling changes or original FastAPI runtime imports.

| Source | Preserved boundary |
| --- | --- |
| `fastapi/routing.py:394` | Capture `_is_coroutine_callable(dependant.call)` while building the handler. |
| `fastapi/routing.py:342-354` | Ordinary coroutine endpoint: await original call once; sync endpoint: await `run_in_threadpool(original_call, **values)` once. |
| `fastapi/routing.py:641-708` | Generator streaming branches create the generator directly; do not move that creation into the ordinary endpoint worker path. |
| `fastapi/routing.py:316-338` | Full `field.validate` runs in a worker for the original sync endpoint; async endpoint validation runs on caller loop; serialization runs on loop. |
| `fastapi/_compat/v2.py:174-189` | Validation calls `validate_python(from_attributes=True)`, catches only ValidationError, extracts `errors(include_url=False)` and returns response-prefixed details. |
| `fastapi/_compat/v2.py:486-492` | Copy each whole error mapping and replace `loc` with prefix + `err.get("loc", ())`; preserve other fields. |
| `fastapi/routing.py:711-714` | A returned Response bypasses model validation and receives solved background work only when missing. |
| `fastapi/routing.py:721-748` | Response model plus DefaultPlaceholder uses `serialize_json` / adapter `dump_json`; concrete response classes use `serialize` / adapter `dump_python`. |
| `starlette/concurrency.py:32-34` | Worker uses partial + AnyIO `to_thread.run_sync`, preserving sibling-owned scheduling/context semantics. |
| `fastapi/routing.py:138-159` | Function scope closes before send; request scope surrounds send/background; exceptions unwind before registered handlers. |

## Native flow

1. `FastApiRoute.endpoint_is_coroutine` stores the registration-time classification.
   Included routes retain this captured kind with the same original endpoint.
   Mutable callable classification/cache history remains a separate frontier.
2. `invoke_route` snapshots the selected plan and ordinary HTTP worker choice under
   a short app borrow. Dependency solving, cache policy and endpoint own argument
   preparation remain on the loop. An ordinary sync endpoint uses the existing
   `CallablePlan::call_with_arguments(..., true)` sibling worker boundary; an
   ordinary async endpoint invokes the same original callable directly.
3. Both ordinary branches unconditionally install `PendingAction::Endpoint` and
   await their framework operation once. `MachineResume::Value` calls
   `finish_endpoint` directly on the raw result, including an awaitable returned
   as a value. No result-based recursive await is added. Scalar results from
   coroutine-classified forwarders enter the existing TypeError/cleanup path.
4. Returned Response bypass and generator streaming paths retain their existing
   finishing paths. Frontend/WebSocket invocation is outside this change.
5. Ordinary model finishing clones configuration and route identity under a short
   app borrow, then releases it before TypeAdapter construction and callbacks.
   `ResponseValidationState` owns adapter, original response body, serialization
   flags, selected response class/status and original endpoint identity.
6. Private Rust `ResponseModelValidator` implements the full validation stage.
   It invokes `validate_python(from_attributes=True)` and, on ValidationError,
   invokes `errors(include_url=False)`, copies each detail and prefixes location
   in that same execution context. All detail fields are retained. Tuple addition
   uses the ordinary `operator.add` operation rather than permissive flattening.
   Its Rust-owned result is a `(validated_value, error_list)` tuple, matching the
   source stage's internal result shape; no facade/helper Python function exists.
7. Async endpoint validation invokes this stage on the caller loop. Sync endpoint
   validation calls this native callable through pinned `run_in_threadpool`, with
   boxed `PendingAction::ResponseValidation` retaining state across the await.
8. Successful validation resume consumes its outcome once. Nonempty errors create
   native ResponseValidationError on the loop with the original body and prefixed
   details. Unrelated stage exceptions propagate unchanged. The existing outer
   resume guard and route exception flow retain function/request stack cleanup.
9. Serialization runs only on the caller loop. For the current native absent-class
   default representation, model serialization uses `dump_json` and its bytes
   directly; this also preserves default-path serializer error messages. A
   concrete explicit/inherited response class uses `dump_python(mode="json")`
   and the existing response constructor/merge path. No-model content retains
   jsonable_encoder + JSON rendering.
10. Existing send, function close, background and request close continuations are
    reused. No dependency plan/policy reanalysis, argument revalidation, endpoint
    reinvocation, or validation/serialization repetition is added on resume.

## Separate boundaries and gates

- TypeAdapter construction remains per response in the existing native location;
  source route-level adapter construction/cache/schema warning timing is not
  repaired here. Source endpoint-context extraction/cache timing also remains
  separate; native error context is still computed on validation failure.
- The absent native response class represents the source default-placeholder path.
  Explicit public DefaultPlaceholder objects and mutable response-class/route
  internals require separate reviewed representation and fixtures. Concrete
  explicit/inherited classes keep their existing Python-value path.
- Default model bytes change the producer to source `dump_json`; this is not a
  performance claim. Broader serializer gates still require aliases/exclude flags,
  nan/inf, warnings, custom serializers/errors, explicit/inherited classes and
  custom response observations before broader support/ranking claims.
- Pinned normal Pydantic errors produce ordinary dict details. Custom error-list
  providers using non-ABC duck mappings remain unproven because the safe PyO3
  update path checks PyMapping; the ordinary error hooks/stage all run in the
  source-selected context. No source exception helper is imported at runtime.
- Generator streaming/WS/frontend classification and mutable classifier LRU or
  descriptor history, native bound-method classification, and `types.coroutine`
  generator await-adapter behavior are outside this patch.
- This patch leaves FastAPI `response_body` unchanged. Root's separate wire patch
  must preserve source absence of `more_body` on ordinary messages. The input
  recorder must continue to expose full raw send fields without normalization.
- Cancellation, concurrent request capacity/exhaustion and sync background thread
  semantics are not established by these 18 sequential worker inputs. Worker
  scheduling/context are delegated to the pinned sibling; no custom threadpool,
  thread IDs, blocking Rust wait or fixture-specific control is introduced.

No tests, builds, extension installs, source/target workload execution, benchmarks,
formatter invocation or repository edits were performed by this author. The draft
is ready for independent static review before parent integration.
