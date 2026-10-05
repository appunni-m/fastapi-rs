# Existing six fault cases across the worker/classifier change

Read-only static review. No repository edits, builds, tests, formatting or live
execution. The separate generator-awaitable proposal remains inactive.

## Frozen code reviewed

- Worker copy: `/private/tmp/fastapi-rs-worker-dispatch-application_runtime.rs`,
  author SHA256 `01ccc8f3fe52bd62c4d2518cddc6ef767349a675110329b81fb9ea01028f97e3`.
- Patch/design: `/private/tmp/fastapi-rs-worker-dispatch.patch` and
  `/private/tmp/fastapi-rs-worker-dispatch-design-2026-10-05.md`.
- Base `cb4231984d692d66846b3820829068f4e34ae43f`, runtime SHA256
  `f81e2d41ee7435befa249335ff5db3fd48b8a06769ded70af0dd438254cd066f`.
- Separate classifier copy/patch:
  `/private/tmp/fastapi-rs-immutable-callable-classification-application_runtime.rs`
  and `/private/tmp/fastapi-rs-immutable-callable-classification.patch`.

FastAPI 0.141.1 / CPython 3.12.13 / Starlette 1.6.0 remain the source authority.
This review is not a receipt for root's eventual combined code or binary.

## Exact historical scope and mapping

The ledger at
`parity-results/coverage/lazy-dependency-incremental/db8118a-first/case-ledger.json`
records 55 parity cases and these six fault cases across five workflow selections:

| Full case ID | Named contract / requirement binding | Recovery action |
| --- | --- | --- |
| `fastapi.fault-contract.route-invocation.recovery` | `http-route-invocation-error-and-recovery`; `tests/test_exception_handlers.py` | Same `/fault` endpoint succeeds after the one-shot pre-dependency fault |
| `fastapi.fault-contract.route-invocation.dependency-cleanup` | `http-route-invocation-error-cleans-dependencies`; `tests/test_dependency_contextmanager.py` | `/dependency-state` |
| `fastapi.fault-contract.sync-parent-async-yield-dependency-cleanup` | Same cleanup contract; contextmanager source requirement | `/state` |
| `fastapi.fault-contract.dependency-records.public-protocol.scoped-yield-cleanup` | Same cleanup contract; reference/dependencies and contextmanager source requirements | `/state` |
| `fastapi.fault-contract.dependencies.dynamic-cache-policy.yield-cleanup` | Same cleanup contract; reference/dependencies and dependencies-with-yield requirements | `/cleanup-state` |
| `fastapi.fault-contract.dependencies.override-policy-mutation.yield-cleanup` | Same cleanup contract; testing-dependencies and dependencies-with-yield requirements | `/cleanup-state` |

All six current recipes and materialized-index rows retain their named point,
contract, verification lane and requirement refs. No obvious broken binding was
found. The global registry has nine contract records and 15 recipe fault cases;
the historical six are a selected subset, not the whole fault surface. Signature
reanalysis, OAuth2, mixed function/request cleanup, body and frontend faults are
outside this six-case audit scope.

## Static control-flow result

The worker draft leaves `http.route.invoke.before` at `invoke_route:10505-10516`
after installing RouteInvocation pending state and before preparing dependencies.
The cleanup hook at `:10590-10603` remains only in DependencyPreparation::Ready,
before endpoint argument preparation and before submitting/invoking the endpoint.
Graph completion at `dependency_graph_resumed:10696-10744` returns through the
same invoke_route boundary. The atomic take functions still consume each armed
point once; the patch does not change fault identity or arming.

Ordinary endpoint operations now install Endpoint pending state and await once.
The new ResponseValidation pending state owns the original response/config across
its worker await. `resume_inner:11431-11457` routes Endpoint, ResponseValidation
and DependencyGraph errors into route_exception. Synchronous validation rejection
or serializer failure after a successful resume is also caught by the outer
`AwaitableStateMachine::resume:11474-11519` while exit stacks are open.

`route_exception:11192-11228` marks and exits the function stack first, then the
request stack, retaining the same error. Close flags guard repeated cleanup.
`resume_inner` consumes the corresponding cleanup continuations before handing
the error to the outer HTTP middleware. On success,
`close_function_dependency_stack_before_response:9260-9283` keeps function cleanup
before send, while request cleanup remains after response/background completion.
This matches the pinned source's nested stacks at `fastapi/routing.py:138-159`.

The separate classifier patch awaits the selected coroutine operation or sync
worker once and stores the raw resumed worker value. A scalar from a coroutine-
classified sync routine reaches the existing await error and cleanup path. The
six old inputs use ordinary fixed callables; they do not establish the new
wrapper/partial/scalar classification branches.

No static fault-hook displacement or missing ResponseValidation error-cleanup
branch was found in the frozen draft. Integration, compiler checks and fresh
instrumented execution remain required.

## Omissions and claim boundaries

1. The five cleanup faults stop before endpoint worker invocation and response
   validation. They do not inject an error into a pending worker or validator.
   Public callback and validation failures belong in ordinary live parity:
   worker18's sync-endpoint error, sync-dependency error, sync/async response
   validation error and serializer error cases already select those boundaries
   with fresh `/probe` recovery. Classifier23's two scalar-error cases and wrapped
   yield-error case cover their ordinary failures. Do not add target-only faults
   for behavior both products can reach through these normal inputs.
2. Five cleanup cases prove cleanup once and a successful state response, not
   re-entry of the resource-owning endpoint after failure. Four state endpoints
   are sync, so the new code incidentally exercises successful endpoint-worker
   and response-validation-worker completion there; no thread/context callback
   observation makes that scheduling a fault-contract claim.
3. The six include request-scope resources only. The separate existing
   `fastapi.fault-contract.route-invocation.function-request-cleanup-order` case
   asserts both scope exits before error-response sends; it is not part of the
   historical six. Worker18's normal errors/successes observe both scopes. Keep
   these evidence lanes distinct in completion and coverage summaries.
4. Fault response observations select status and message types, with an events-
   only later body. They cannot establish full send fields, raw body-error
   messages, response-model callbacks, original invoker execution or worker
   ContextVar placement. Worker18's lossless send/callback state and exact live
   source comparison must establish the broader slice.
5. The cleanup assertion in `scripts/parity/fault_contracts.py:207-231` requires
   exactly one later completed HTTP 200 response with the existing events body.
   Appending another HTTP 200 recovery action would violate that named contract.
   Do not silently reinterpret it as a full fresh-resource recovery contract or
   weaken it to admit new observation shapes.

Runner separation remains intact: oracle fault rows are not_applicable, target
must prove the fault-enabled build, and mixed workflows require that build for
the whole selection (`comparator.py:545-556`, `worker.py:1388-1399`). Passing old
receipts at db8118a cannot establish combined-code behavior or new-region union.

## Background worker blocker

The old six do not inject or mutate BackgroundTasks. Passing them would not repair
the valid sync-worker add_task path exposed by worker18. Latest sibling evidence
is recorded separately in
`/private/tmp/fastapi-rs-background-task-worker-crossing-review-2026-10-05.md`.
Do not drop that public case or substitute inline endpoint invocation to make the
fault lane appear sufficient for benchmark admission.
