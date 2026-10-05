# Generator-based awaitable adapter proposal

Inactive independent inputs: **13 parity cases / 40 HTTP actions**. These files
are separate from the frozen 23 classification and 18 worker-dispatch cases.
Static admission checks are recorded below. No source/target execution, build or
repository edit is claimed.

- `generator_awaitable_protocol.py`: ordinary public user app and ASGI recorder.
- `generator-awaitable-protocol.yaml`: schema @9 inputs with no expected outputs.
- `review-plan.md`: bounded source evidence, mappings and native design.

The intended future workload path is
`tests/fixtures/workloads/generator_awaitable_protocol.py`. Root owns activation,
reviewed metadata and requirement maps, materialization and live verification.

## Source boundary

FastAPI 0.141.1 commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`,
Starlette 1.6.0 commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`,
CPython 3.12.13 and the repository's pinned Pydantic profile. Generic Starlette
behavior remains owned by the exact sibling
`/private/tmp/fastapi-rs-starlette-rs-b4c8a65` at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.

Pinned Python `types.py:275-297` makes a generator function decorated with public
`types.coroutine` produce an iterable coroutine without adding `__await__`.
`inspect.py:468-474` accepts that generator as awaitable. The input only calls
public decorators and protocol inspection; it neither reads nor changes code
flags or private coroutine markers.

[CPython v3.12.13 genobject.c:940-996](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c#L940-L996)
returns a direct iterable-coroutine generator itself as the await iterator.
The result of an object's `__await__` has different rules: a native coroutine or
an iterable-coroutine generator is rejected before the ordinary iterator check.
The noniterator error message also has no article before `non-iterator`.
[Its throw method:537-562](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c#L537-L562)
emits a DeprecationWarning for the legacy multiargument throw signature.

FastAPI `dependencies/models.py:138-220` classifies generator callables before
the solver coroutine branch. Consequently, direct `Depends(types.coroutine_fn)`
is a yield dependency; it is not evidence of direct await conversion. The
positive input instead defines a nongenerator sync routine, marks it through
public `inspect.markcoroutinefunction` before registration, and returns the
decorated generator. It has no `__wrapped__` link to the generator function.
`dependencies/utils.py:673-674` then awaits that returned object unconditionally.
`routing.py:342-354` provides the corresponding endpoint boundary. Classification
and worker fixes are prerequisites; these inputs do not alter classifier history.

## Proposed cases

Every suffix below has prefix `fastapi.awaitables.generator-protocol.`.

| Suffix | Input and distinct observation | Actions |
| --- | --- | ---: |
| `marked-immediate-validation-cache` | Invalid query before generator allocation; immediate StopIteration value; cache hit and uncached repeat | 4 |
| `marked-checkpoint` | Direct generator yields None, resumes and completes | 2 |
| `marked-future-nested-cache` | Real Future callback, generator continuation, nested async parent and later same-key reuse | 2 |
| `caught-future-error` | Future exception enters the same generator, is caught, and produces ordinary cached/uncached values | 2 |
| `propagated-future-error-cleanup-recovery` | Full error class/message, both entered guard exits, public clear operation and fresh successful callbacks | 5 |
| `marked-endpoint-future` | Publicly marked nongenerator endpoint returns the same iterable-coroutine protocol | 2 |
| `genuine-async-bridge-control` | Ordinary async body awaits the generator through CPython inside its native coroutine | 2 |
| `unmarked-returned-generator-is-a-value` | Sync dependency's raw generator identity/state/awaitability; explicit close without entering its body | 2 |
| `unflagged-generator-error-cleanup-recovery` | Marked routine returns ordinary generator; full await error, unstarted state, explicit close and recovery | 5 |
| `ordinary-await-iterator-control` | User __await__ returns an ordinary generator iterator which forwards to the iterable coroutine | 2 |
| `direct-generator-declaration-is-a-yield-role` | Direct decorated generator callable yields a resource value and exits in request scope | 2 |
| `await-method-generator-error-cleanup-recovery` | User __await__ returns an iterable-coroutine generator; actual rejection before body entry, cleanup and recovery | 5 |
| `await-method-noniterator-error-cleanup-recovery` | User __await__ returns integer; full actual TypeError string, cleanup and recovery | 5 |

All requests compare exact HTTP status, ordered headers, body bytes and ASGI
message types. `/state` additionally exposes every recorded prior send field,
byte value, container shape and insertion order. It omits no message fields and
adds no protocol defaults. Public warning capture records every runtime
DeprecationWarning category and unchanged message; filenames and line numbers
are not selected observations. This reveals legacy generator.throw warnings
without message filters or source/target normalization.

User callback traces retain original marked/unmarked invocation, generator
allocation and public state, Future completion, result/error, generator finally,
cache identity booleans, and function/request guard boundaries. Error handlers
return the actual fully qualified class and unchanged message. Rejected and raw
generators are retained and explicitly closed by ordinary public input actions;
no unawaited native coroutine is allocated. The async bridge control does not
disguise positive direct-generator cases; each uses its own public route.

The Future is completed with `loop.call_soon` on the active request loop. No
sleep, timer, worker identity, process address, deadline assertion, target
detection or private FastAPI import appears. Factory options describe ordinary
user suspension, failure and returned-value shapes, not case IDs. The workload
accepts the schema @9 positional `factory(factory_input, event_trace)` contract,
reading those options from the input mapping. The detailed callback journal is
observed through `/state`; the passed event_trace list is not a selected output.

## Native adapter design

Current `fastapi-rs/src/awaitable.rs:305-328` calls `inspect.isawaitable`, then
always calls the object's `__await__`. A direct real iterable-coroutine generator
passes the first check and fails the second with AttributeError. The same helper
currently accepts an illegal iterable-coroutine __await__ result and differs
from CPython's noniterator TypeError text.

1. Add a small safe Rust helper for an exact `types.GeneratorType` object whose
   `gi_code.co_flags` contains `inspect.CO_ITERABLE_COROUTINE`. Use safe PyO3
   type identity/value conversion; no raw FFI, unsafe code or Python runtime
   helper. Check the original object before calling __await__. Return the same
   owned generator directly. Do not call iter(), construct a coroutine wrapper,
   allocate a task, run another loop, or require a nonexistent __await__.
2. For existing ordinary __await__ calls, reject a returned native coroutine or
   exact iterable-coroutine generator before checking iterator status. Do not
   apply the direct-generator acceptance branch to __await__ results. Match the
   source noniterator TypeError string exactly for the bounded integer control.
3. Reuse the native delegated iterator state in `drive` and
   `resume_delegated_iterator`: preserve yielded Future identity, initial None,
   sent values, StopIteration.value, pending continuation and error cleanup.
   Dispatch still chooses whether to await based on source callable role; do
   not recursively await unmarked worker return values.
4. `throw_into_iterator` currently invokes .throw(type, value, traceback).
   For real native generators/coroutines, the single-exception form avoids the
   pinned deprecation warning and preserves the original exception/traceback.
   Preserve the original awaited-object role when a native coroutine becomes a
   coroutine_wrapper through __await__; checking only the returned iterator's
   GeneratorType/CoroutineType would miss that native-coroutine provenance.
   Review PyErr conversion before that change. CPython `_gen_throw:440-473`
   delegates directly to native generators/coroutines. Generic forwarding
   stops at the first NULL: Task.throw(exc) can forward one argument, while
   explicit three-argument callers can forward three. The existing Rust generic
   three-argument path remains an unproven gap, including user-returned
   coroutine_wrapper objects; these 13 inputs do not establish its full arity.
   Do not globally rewrite such wrapper throw calls. Forward close/GeneratorExit
   through the same current iterator and
   cleanup guards; cancellation remains separately unproven. These 13 inputs
   do not gate a failure passing through the genuine async bridge control.
5. Review the resulting Rust independently, then root runs repository formatting,
   Clippy/static contracts and isolated live parity. Keep the facade export-only,
   the sibling unchanged, and all input observations intact.

The exact type/flags helper is bounded to immutable standard-library bindings.
The existing inspect.isawaitable gate and instance method lookup are not a full
implementation of CPython's type-level am_await lookup. ABC registration without
__await__, mutable/special descriptor lookup, native-coroutine reuse, warning
filters, arbitrary send/throw protocols, cancellation, concurrent callbacks and
classification-cache mutation are separate boundaries. A source-matching helper
must not claim those from these inputs.

## Public metadata mapping proposal

All cases observe root `fastapi.FastAPI`, `fastapi.applications.FastAPI.__init__`,
`FastAPI.get` registration/invocation and the public ASGI `FastAPI.__call__`
boundary. Dependency-role cases map root `fastapi.Depends` and the public alias
`fastapi.param_functions.Depends` through live injection, cache/scopes and errors.
The endpoint case directly exercises the original endpoint await boundary.

Error/recovery cases additionally observe inherited
`fastapi.applications.FastAPI.add_exception_handler` (canonical pinned Starlette
operation), `FastAPI.post` for the clear route, and `fastapi.responses.JSONResponse`.
State requests return public JSONResponse in all cases. The default invalid-query
case reaches ordinary FastAPI validation handling; no private dependency class,
classifier, native awaitable type or exception implementation is imported or
promoted into a public API classification. Standard types/inspect/asyncio/warnings
objects are user inputs and observations, not new FastAPI candidates.

## Admission

On 2026-10-05, the existing `scripts.build_parity_inputs.read_recipe` loader
accepted the corrected schema @9 YAML and counted 13 parity cases / 40 actions.
The workload passed Ruff lint and format checks using the repository's explicit
`pyproject.toml` configuration with caching disabled. Those checks parsed data
and source only: no app factory, ASGI request, source oracle or target was run.
The shared ASGI observation now uses the schema's singular
`selector: message_types` and `comparison: ordered`, preserving every action's
message-type observation and the lossless `/state` send projection.

These are read-only-source design claims, not passing parity evidence. Independent
review should check ordinary source reachability, exact error/warning projection,
resource cleanup and count/mapping consistency. Root may then copy the reviewed
files, bind metadata/manifest/index, run mandated input/static checks and record
fresh source/target results. All failures remain visible. No unit tests, pytest,
unittest, Cargo test or benchmark claim is part of this proposal.

The prospective safe type/flag helper reads gi_code, which can emit extra audit
events or trigger audit-hook errors unlike the source C fast path. Audit hooks
and their side effects remain outside these 13 fixtures and require a separate
source-correct solution before broader await-protocol claims.
