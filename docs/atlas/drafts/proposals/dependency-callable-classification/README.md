# Immutable callable classification input proposal

Inactive reviewed proposal: 23 parity cases and 54 HTTP actions. The parent has
saved and formatted these independent inputs; live source/target behavior remains
unexecuted and requires active metadata/manifest/index bindings.

The source boundary is FastAPI 0.141.1, commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, with CPython 3.12.13 and the
existing pinned Pydantic and Starlette 1.6.0 profiles. The partial/wrapped source
tests were read as evidence of public reachability; no test implementation or
expected output was copied.

## Proposed files

- `dependency_callable_classification.py`: ordinary user callable definitions,
  public Depends/FastAPI registrations, and an ASGI response boundary recorder.
- `dependency-callable-classification.yaml`: input-only workflow schema v9.

The proposed workload path inside the recipe is
`tests/fixtures/workloads/dependency_callable_classification.py`. Copying,
reviewed API mappings, materialization, validation, and live oracle/target runs
remain parent work after the active override slice completes.

## Cases and observations

Every ID below has prefix `fastapi.dependencies.callable-classification.`.

| ID suffix | Public input shape | Main observations | Actions |
| --- | --- | --- | ---: |
| `sync-wrap-coroutine-function` | Sync forwarding decorator with `functools.wraps` over async function | Invalid query suppression, forwarding, awaited data, cache identity, uncached repeat | 4 |
| `sync-wrap-coroutine-instance` | Sync forwarding decorator over async callable instance | Original wrapper invocation, instance inputs and data | 2 |
| `sync-wrap-coroutine-call-method` | Sync decorated async `__call__` | Self binding, method forwarding, data | 2 |
| `partial-coroutine-instance` | Positional partial of async instance | Bound input, shared cache value, uncached invocation | 2 |
| `partial-wrapped-coroutine-nested` | Partial of sync-wrapped async function below a parent | Bound input, parent trace, direct child reuse | 2 |
| `plain-partial-function-method-controls` | Plain async function, partial function, partial bound method | Distinct ordinary binding and completed-call controls | 2 |
| `unmarked-sync-awaitable-control` | Unmarked sync function returning a coroutine | Actual type, awaitability, coroutine state, identity, explicit close, body execution trace | 2 |
| `async-wrapped-scalar-error-cleanup-recovery` | Sync routine with `wraps(async_fn)` metadata returning an integer | Actual full error class/message, original wrapper invocation, yielded cleanup and fresh recovery | 4 |
| `public-marked-scalar-error-cleanup-recovery` | Sync routine marked before registration through public `inspect.markcoroutinefunction`, returning an integer | Actual full error class/message, marked routine invocation, yielded cleanup and fresh recovery | 4 |
| `sync-wrap-sync-generator-function` | Sync wrapper over sync generator, implicit scope | Entered value, original forwarding, cleanup relative to response send | 2 |
| `sync-wrap-async-generator-function` | Sync wrapper over async generator, function scope | Entered value, cleanup relative to response send | 2 |
| `sync-wrap-sync-generator-instance` | Sync wrapper over generator instance, function scope | Cache identity, two resource entries/exits, response boundaries | 2 |
| `sync-wrap-async-generator-instance` | Sync wrapper over async-generator instance, implicit scope | Underlying `__call__`, entered value, cleanup | 2 |
| `sync-wrap-async-generator-call-method` | Sync decorated async-generator `__call__`, function scope | Method forwarding, entered value, cleanup | 2 |
| `partial-sync-generator-instance` | Partial generator instance, function scope | Bound input, resource enter/exit | 2 |
| `partial-async-generator-instance` | Partial async-generator instance, implicit scope | Bound input, resource enter/exit | 2 |
| `async-generator-adapter-over-sync-generator` | Actual async-generator wrapper with sync-generator `__wrapped__` | Original adapter invocation and both layers of cleanup | 2 |
| `partial-wrapped-sync-generator-function` | Partial of sync-wrapped sync generator, function scope | Partial-removal/unwrap composition, original bound invocation, cleanup | 2 |
| `partial-wrapped-async-generator-function` | Partial of sync-wrapped async generator, implicit scope | Partial-removal/unwrap composition, original bound invocation, cleanup | 2 |
| `partial-generator-function-method-controls` | Raw partial sync/async generator functions and bound methods | Distinct bound inputs, four entered values and request exits | 2 |
| `wrapped-partial-yield-scope-construction` | Public registration of wrapped function and partial instance generator parents with a function-scoped child | Actual construction outcome and full exception class/message for request/function parent scopes | 1 |
| `wrapped-yield-error-cleanup-recovery` | Endpoint raises ordinary user error after wrapped async-generator instance entry | Exact public error, resource propagation/cleanup, fresh request recovery | 3 |
| `public-endpoint-role-classification` | Public route registrations of wrapped async function/instance and partial async instance | Actual route data, original forwarding, bound arguments | 4 |

## Source-backed boundaries

`fastapi/dependencies/models.py:18-27` removes nested partial wrappers before
calling `inspect.unwrap`. The generator, async-generator, and coroutine
predicates at `:138-220` inspect the callable and both direct/unwrapped
`__call__` chains. They guard classes; coroutine routine checks apply before
method inspection. Classification does not replace the original invoker.

`fastapi/dependencies/utils.py:300-315` uses generator classification to enforce
scope rules at public route registration. `:655-680` keeps the original edge's
cache key and invokes the selected original wrapper/partial. `_solve_generator`
at `:566-576` checks the async-generator predicate before the sync-generator
predicate. The adapter case makes that priority observable without changing
either callable after registration.

`fastapi/routing.py:140-146` defines yield cleanup around response sending.
`:394` also uses callable classification for endpoint invocation, which the
endpoint-role case exercises through public route registration.

`fastapi/dependencies/utils.py:673-674` awaits a callable already classified as
a coroutine unconditionally. The scalar-wrapper and publicly marked routine
cases preserve that metadata and record their original sync body returning an
integer. A request-scoped guard enters before that edge; the public TypeError
handler returns the actual fully qualified class and unmodified message after
guard cleanup. Follow-up requests invoke a separate ordinary coroutine with a
fresh guard and observe its completed cleanup. These callbacks never allocate
an underlying coroutine merely to return a scalar. The routine marker is set
only by the public decorator before registration; no private marker attributes
are read or written.

The unmarked control uses no coroutine marker or `__wrapped__` chain. Its
endpoint projects the returned object through public `inspect` functions and
closes a received coroutine; it never schedules or awaits that object itself.
No raw object repr, process address, source lookup, expected output, private
FastAPI import, or fixture-ID dispatch appears in the input workload.

## Reviewed API mapping proposal

All cases observe `fastapi.FastAPI` construction and public `FastAPI.get`
registrations. The dependency-role cases additionally observe the root
`fastapi.Depends` factory protocol through injection (also map the public alias
`fastapi.param_functions.Depends`). The error-cleanup cases also observe
`FastAPI.add_exception_handler` and `fastapi.responses.JSONResponse`.
The endpoint-role case maps invocation effects to `FastAPI.get`; its other
unreached dependency declarations are not direct injection observations.
The scope-construction case observes the public `DependencyScopeError` class
and message as a factory/registration effect, without importing any private
dependency class or classifier. Preserve private/internal classification for
the source implementation helpers and `params.Depends` class candidates.

`functools`, `asyncio`, and `inspect` are standard-library user inputs;
`typing.Annotated` carries public Depends declarations. The ASGI wrapper only
records public response events around the application.

## Separate frontier

All wrappers, partial bindings, class methods, code, and marker definitions
stay fixed after registration. The ordinary request dependency cache is
observed, but this proposal establishes nothing about the separate source
classification LRU caches: mutation of `__wrapped__`, `__call__`, `__code__`,
partial internals, descriptor lookup effects, coroutine marker mutation, eviction,
or first-population history. Instance coroutine markers and unusual mutable
classification protocols remain later inputs rather than this common slice.

## Parent static admission checks

The saved inactive recipe passed `scripts.build_parity_inputs.read_recipe`
(schema @9, repository unique-key loader): 23 cases and 54 actions. Its Python
workload passed Ruff format/check after parent integration. The prospective
`native-classifier.patch` has independent read-only helper and executor review;
it remains unapplied, uncompiled, and unexecuted. The source review preserves
classification-history, descriptor, native-method and generator-awaitable gaps.
