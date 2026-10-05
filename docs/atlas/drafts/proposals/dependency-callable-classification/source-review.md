# Immutable dependency classification review proposal

Source: FastAPI 0.141.1 (`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`),
CPython 3.12.13. Read-only source/runtime review; no execution or fresh parity
claim. This is a proposed next slice, separate from lazy override verification.

## Source algorithm and timing

`fastapi/dependencies/models.py:17-27` removes every `functools.partial` before
`inspect.unwrap`. The three predicates at `:138`, `:168`, and `:198` inspect:

1. The callable after partial removal, then after unwrapping.
2. An unwrapped-class guard.
3. The partial-removed callable's `__call__`, with partial removal/unwrapping.
4. The unwrapped callable's `__call__`, with partial removal/unwrapping.

The coroutine predicate additionally requires `inspect.isroutine` in step 1.
On CPython 3.12 it uses `asyncio.iscoroutinefunction`, which includes the inspect
predicate plus the legacy asyncio marker. Native bindings need an equivalent
classification bridge for their native async methods; checking Python flags
alone does not classify those native method descriptors.

In `utils.py:271-331`, source signature construction can classify generator
parents to enforce request/function scope rules. `models.py:229` computes an
unspecified generator scope as `request`; `:82` also uses classification when
forming the original edge's cache key. Thus classification affects construction,
scope errors, and cache identity as well as invocation.

In `utils.py:625-680`, effective signature/children/input solving precedes the
original raw policy/cache lookup. A hit bypasses execution classification. On a
miss, generator predicates are consulted before coroutine classification.
`utils.py:566` (`_solve_generator`) chooses async-generator context management
before sync-generator context management when both predicates are true. This
can occur with an async-generator wrapper around a sync-generator function.
Classification must retain the original wrapper/partial for invocation and
argument binding; the unwrapped function is only classification evidence.

## Concrete immutable gaps

Native `application_runtime.rs:6206` checks only direct
`inspect.iscoroutinefunction(value)`/`value.__call__`, plus native security
identity. `:6243` similarly checks direct generator flags and direct `__call__`.
Neither predicate follows the source's partial/unwrap chains.

| Public shape | Source classification | Native consequence inferred from code |
| --- | --- | --- |
| Sync `functools.wraps` forwarding wrapper around an async function | Coroutine via unwrapped routine | Sync worker returns a coroutine object, retained as the dependency value |
| Sync wrapper around an async callable instance, or sync-decorated async `__call__` | Coroutine via unwrapped callable/method | Same missed await |
| `partial(async_callable_instance, bound_argument)` | Coroutine via underlying instance `__call__` | Partial's own method descriptor hides the async method; same missed await |
| Sync wrappers around sync/async generator functions or generator instances/methods | Generator via unwrapped routine/`__call__` | Raw generator value rather than entered context; cleanup and source scope checks are missed |
| Partials around sync/async generator instances | Generator via underlying instance `__call__` | Raw generator value, missed context entry/cleanup/scope analysis |

These are public source-reachable forms explicitly exercised by
`tests/test_dependency_partial.py:115-147` and
`tests/test_dependency_wrapped.py:13-21,67-111,122-179,186-220,232-307`.
No source test was executed or copied into target fixtures.

Direct plain async/generator functions and bound methods, their partials, and
direct async/generator instances are distinct controls. CPython's
`inspect.py:391-437` already removes partial wrappers when inspecting function
flags; direct partials of functions/methods therefore do not demonstrate the
instance gap. The existing `dependency_wave_callables.py` covers those ordinary
forms and a sync wrapped function, but omits wrapped async/yield forms and
partials of instances.

The missing routine guard also merits a later protocol input: a callable
instance marked directly with public `inspect.markcoroutinefunction` can be
accepted by the native direct predicate while source ignores that instance-level
marker and classifies its actual `__call__`. This is separate from the common
wrapper/partial gaps; no full marker-protocol claim is proposed here.

## Minimal independent fixture backlog

Use independently authored callables, public Depends/routes, scalar query inputs,
user forwarding/binding traces, yielded enter/exit traces, object relationships,
and live HTTP/error observations; store no expected outputs.

1. Sync `wraps` forwarders around an async function, an async instance, and an
   async instance's decorated `__call__`; observe actual awaited values and
   forwarding traces. Include an undecorated async control.
2. Partial async instance with a bound argument, plus partial async function and
   bound-method controls. One partial of a wrapped callable checks composition.
3. Wrapped sync/async generator functions and generator instances/methods;
   partial sync/async generator instances. Observe both returned values and
   cleanup after response, then an ordinary public endpoint exception. Include
   function/request scopes where already supported.
4. Wrapped/partial generator parent with a function-scoped child: observe
   construction outcome/class/message to catch missed source scope rejection.
   An async-generator wrapper over a sync-generator function exercises source's
   async-first execution selection when both predicates identify a generator.
5. Negative control: an intentionally unmarked sync callable returns a coroutine.
   Source runs it in the worker and injects the coroutine itself. A user endpoint
   can project `inspect.isawaitable`/type, explicitly close it, and return JSON.
   Never blanket-await worker return values to repair misclassification.

## Classification-cache history is a separate frontier

Source has three independent `lru_cache(maxsize=4096)` values keyed by
`_CallIdentity`: identity hash/equality with a strong reference to the callable.
Construction, original-key scope analysis, and miss execution populate them at
different times, with Python short-circuit ordering. Correctness for immutable
shapes does not establish behavior after changing `__wrapped__`, `__call__`,
`__code__`, partial structure, descriptors, or markers on the same identity, nor
eviction/repopulation timing. Keep those mutable-history and descriptor-side
effect protocols explicitly unproven; do not eagerly populate every predicate
and claim source history parity.

No repository files, native implementation, recipes, builds, or benchmarks were
changed by this review.

## Frozen proposals after independent review

Inputs are under
`/private/tmp/fastapi-rs-dependency-callable-classification-proposal-2026-10-05/`:
`dependency_callable_classification.py`,
`dependency-callable-classification.yaml`, and `README.md`.
The final backlog has 23 parity cases and 54 actions. Review corrected unsupported
`body_json` selectors to exact `body` selectors, corrected source-evidence enums,
and added partial/wrapped generator composition plus raw generator function/method
controls. Two additional immutable scalar-return cases observe unconditional-await
errors, original invocation, yielded cleanup, and normal request recovery. Source
reachability, scope/error/cleanup timing, and the unmarked raw coroutine projection
were reviewed without execution.

Prospective Rust copy:
`/private/tmp/fastapi-rs-immutable-callable-classification-application_runtime.rs`.
Unified patch:
`/private/tmp/fastapi-rs-immutable-callable-classification.patch`.
Base HEAD is `db8118a4552a4eb3f44977db912162f10dcac25b`; the repository runtime
SHA-256 at drafting was
`f81e2d41ee7435befa249335ff5db3fd48b8a06769ded70af0dd438254cd066f`.
Classifier helpers change: partial removal before unwrapping, source ordered
call/method checks and routine/class guards, pinned asyncio coroutine predicate,
sync-before-async generator detection followed by async-first context selection,
and the existing native async-instance bridge after method flag checks.
The node also sends every non-generator invocation through the existing Await
path: classified coroutine results are awaited even when scalar; synchronous
invocation returns the worker awaitable, which is awaited once. Original invocation,
cache policy/result storage, and endpoint execution remain unchanged. The worker's
returned coroutine remains a raw stored value; no second await is introduced.

The patch is not applied, compiled, formatted, or exercised. Besides the separate
LRU/mutable descriptor/history boundaries above, direct native async bound-method
objects still need their own binding evidence: the existing native bridge checks
the receiver instance's class implementation, not a standalone method object's
code flags. Endpoint-role probes do not establish endpoint classification timing
after mutable metadata changes.

## Unconditional-await execution gap and prospective delta

Source `dependencies/utils.py:673-676` unconditionally awaits the original
callable's return value on the classified-coroutine branch. By contrast, current
native `DependencyExecutionNode::advance` at `application_runtime.rs:586-590`
awaits only an `inspect.isawaitable` return value, otherwise accepting and storing
the value. A fixed sync wrapper with `functools.wraps(async_function)` that
returns an integer, or a sync integer-returning routine decorated before
registration with public `inspect.markcoroutinefunction`, reaches this difference:
source raises an actual Python TypeError; native currently accepts the integer.
This is an immutable error/control gap, separate from classification LRU history.

The initial classifier-only draft did not repair this branch. The revised unapplied
draft removes the node's awaitability gate and direct scalar storage path. It sends
either the classified call result or the synchronous worker awaitable through the
existing await/error machinery. `awaitable.rs:305-317` rejects the integer with
the same TypeError wording used by CPython's await expression; `:209-215` feeds
that rejection back as `MachineResume::Error`, retaining existing dependency stack
cleanup and public exception handling. A successful graph resume stores the
returned value once, so an unmarked sync callable's worker-returned coroutine
is still injected as a raw value. This delta is not compiled or executed.

The two frozen public controls use a fixed sync `wraps(async_function)` routine
and a sync routine marked before registration through public
`inspect.markcoroutinefunction` (`inspect.py:408-437`). Each returns an integer
without allocating a coroutine. A request-scoped async guard enters first; the
handler projects the actual full error class and untouched message. Follow-up
state and normal-coroutine requests expose guard error/cleanup and recovery.
Exact body selectors retain original callable counters and traces; no expected
outputs or normalization are present. The unmarked-sync-returning-coroutine
negative control remains separate.

Existing await-adapter protocols beyond these controls remain unproven. In
particular, `types.coroutine` generator-based awaitables can satisfy
`inspect.isawaitable` without defining `__await__`; `awaitable.rs:319` currently
calls `__await__` directly. This is a separate adapter gap, not repaired by the
classifier/forced-await draft. Mutable classification-cache history, standalone
native async method objects, and descriptor-side effects remain separate too.

Independent runtime review cleared the revised execution delta by source reading:
pending graph state is installed before await rejection; a scalar error reaches
the existing stack cleanup without cache insertion; successful resume stores the
worker's raw return once. Input/policy/cache-hit ordering, generator context entry,
and completion cursors are unchanged. The frozen full copy SHA-256 is
`3be77984dfa96ae2623998ecd3b4f0d5f4af66bc90d1ce5566749c19444a49f1`;
the patch SHA-256 is
`f68b1d12f716dec86b2bdc42a8f1c19278efa49af265a8776be537e93a45757a`.
Static clearance does not establish compilation or live parity.
