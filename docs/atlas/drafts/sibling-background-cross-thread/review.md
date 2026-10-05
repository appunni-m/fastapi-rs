# Worker-boundary review and prospective sibling correction

## Parent proposal check

The parent applied the exact two-attribute patch only in the isolated checkout
`/private/tmp/fastapi-rs-starlette-background-review`. Strict workspace Clippy
passed with CPython 3.12.13 and PyO3 0.29.2; the default PyO3 Send/Sync bounds
accepted both task classes. The log is
`parity-results/worker-sibling-background-proposal-clippy.log`.
This check did not change the configured sibling pin, installed runtime, or
shared Starlette-RS checkout, and does not establish live parity. The first
proposal compile selected the system Python 3.9 and failed configuration;
the successful retry explicitly selected the project's pinned interpreter.

Static review only. No sibling or repository edit, build, test, extension install,
or live workload execution by this reviewer. Parent separately observed the actual
BackgroundTasks worker failure in its diagnostic target process; the stderr is
`parity-results/worker-dispatch-target-diagnostic.log`.

## Ordinary FastAPI worker draft review

Reviewed frozen `/private/tmp/fastapi-rs-worker-dispatch.patch` and full runtime
copy, SHA-256 `01ccc8f3fe52bd62c4d2518cddc6ef767349a675110329b81fb9ea01028f97e3`,
against the exact `cb4231984d692d66846b3820829068f4e34ae43f` base.

The following receive bounded static clearance, pending parent build/live parity:

- Captured original endpoint coroutine classification controls both ordinary
  invocation and response validation. Request argument validation stays on loop.
- Both async original calls and sync worker operations are awaited once. Successful
  endpoint resume passes the raw returned value to finishing, including an
  attribute-backed awaitable; it does not recursively await that result.
- The full source ModelField.validate stage runs in the selected context:
  `validate_python(from_attributes=True)`, ValidationError extraction with
  `include_url=False`, whole-detail mapping copy, and response location prefix.
- Boxed validation state retains the original body/configuration across the worker
  await. Public ResponseValidationError construction and serialization run on the
  loop. Eligible absent-class defaults use dump_json bytes; concrete response
  classes use dump_python and the existing response constructor.
- Ordinary app borrows are dropped before user callbacks/awaits. Prepared graph
  dependency values prevent re-invocation or policy rereads. Returned Response
  bypass, generator/frontend/WebSocket paths, cleanup/background/send sequencing
  stay on their existing routes.

Source references: FastAPI 0.141.1 `routing.py:342-354,394,711-750`,
`routing.py:316-338`, `_compat/v2.py:174-189,486-492`, and `routing.py:138-159`.
Adapter construction/cache timing, mutable classification history, unusual error
mapping protocols, and broader stream/serializer/cancellation protocols remain
the author-documented boundaries. This clearance does not erase the external
background state blocker below.

## Exact cross-thread background failure

Pinned sibling: `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`,
commit `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Its Cargo lock and the FastAPI
lock both select PyO3 0.29.2.

FastAPI creates injected BackgroundTasks while preparing arguments on the loop.
Its class is a native-created subclass of the sibling's public BackgroundTasks.
The sibling Python wrapper creates `_core.BackgroundTasks` at construction;
`background.py:70` implements add_task with
`self._inner.append_task(BackgroundTask(func,*args,**kwargs))`.

The native classes at `starlette-rs-py/src/background.rs:22,114` are marked
`unsendable`. A sync endpoint's add_task therefore borrows the loop-created
PyBackgroundTasks through `append_task(&self)` on the worker (`:154-157`).
PyO3 0.29.2 `impl_/pyclass.rs:1081-1093` checks creation thread and panics on
cross-thread access; `pycell/impl_.rs:486-489` invokes that checker during borrow.
The parent diagnostic confirms this exact boundary, rather than only an inferred
failure.

Removing only the collection restriction is insufficient. BackgroundTask is
constructed on that worker and later invoked on the loop after response sending.
Its native continuation borrows the worker-created task in
`background.rs:684-690`. Both task data classes must support that normal source
ownership transfer. The affected active inputs include the sync endpoint with
two yielded scopes/background and the sync returned-JSONResponse/background case.

## Minimal prospective generic sibling patch

Full copy: `/private/tmp/fastapi-rs-starlette-background-cross-thread.rs`.
Base copy: `/private/tmp/fastapi-rs-starlette-background-cross-thread-base.rs`.
Patch: `/private/tmp/fastapi-rs-starlette-background-cross-thread.patch`.

The patch removes `unsendable` from only PyBackgroundTask and PyBackgroundTasks.
It adds no unsafe code, manual Send/Sync implementation, lock, lint suppression,
new threadpool, Python helper, or callback rescheduling. The ordinary PyO3 class
bounds will enforce Send/Sync when the parent compiles the prospective change.

Safety rationale:

| Class | Complete stored state | Transfer rationale |
| --- | --- | --- |
| PyBackgroundTask | `func`, `args`, `kwargs`, `is_async`: all `Py<PyAny>` | Owned Python handles implement Send/Sync; access/mutation occurs with Python attachment and PyO3 borrow guards. |
| PyBackgroundTasks | `tasks`: `Py<PyAny>` | Same handle/borrow guarantee; ordinary task list operations remain under Python attachment. |

Neither changed class stores Rc, RefCell, Cell, Rust references, an active Python
iterator, or a continuation. Although the module has Rc/RefCell/Cell, those fields
belong to separate iterator/runtime classes. Their thread restrictions stay intact.

Task classification remains in the original constructor on the add_task caller's
thread; it is not repeated/deferred on the loop. BackgroundTaskCall snapshots its
fields and drops its PyRef before invoking user callables/worker scheduling.
BackgroundTasksCall drops its collection borrow before constructing/advancing the
task iterator. The existing sibling continuation and run_in_threadpool keep all
generic sequencing, context copying, and scheduling ownership. NativeAwaitable is
still created and driven on the loop; its unsendable state is not transferred.

The sibling's Rust background and awaitable modules are private; there is no
public Rust task factory that takes captured records and bypasses the owning
thread check. Reimplementing generic task execution in FastAPI, or reconstructing
tasks on the loop and rerunning classifier hooks, would broaden ownership or
change source timing. The two-attribute generic sibling correction is the smallest
source-preserving option found. Applying it requires an explicitly reviewed new
sibling revision/pin and its own static/live gates. This draft does not change the
current pin.

## Broader ordinary object inventory

| Public object/route | Static status at the pinned sibling |
| --- | --- |
| Returned ordinary JSONResponse/Response created in a sync worker | Core PyResponse (`lib.rs:688-694`) already lacks unsendable and holds owned native Response plus Py handles. Public body/status/background are Python slots; later loop ASGI use has no analogous task thread guard. This is present in the 18-case suite. |
| Injected Request/HTTPConnection reads in sync callbacks | HTTPConnection (`request_runtime.rs:61-73`) is already transferable; RequestBody uses Arc/Mutex (`:28-45`). No analogous creation-thread guard on those ordinary stores. |
| Injected/returned ordinary Response headers/status | PyResponse is transferable; header state uses sibling-owned Py/Arc/Mutex values. No ordinary unsendable data guard found. |
| UploadFile public data/file operations | PyUploadFile (`datastructure_runtime.rs:799-806`) is already transferable with Arc/Mutex-owned Python field handles. Not a current 18-case input. |
| FileResponse created in a sync worker and later sent on loop | Native PyFileResponse (`file_response_runtime.rs:34-39`) is unsendable, so later public header sync/asgi_call crosses its creation thread. Concrete separate source-reachable gap, outside the 18 current inputs. Requires its own stored-type audit and recipe. |
| StreamingResponse created in a sync worker and later sent on loop | Native PyStreamingResponse (`runtime_calls.rs:160-168`) is unsendable and stores Rc/RefCell sync iterator state. Concrete separate gap; simply removing unsendable is not a safe proposal. Requires state-transfer redesign and separate fixtures. |

Other thread-bound continuation/iterator/middleware classes are not made
transferable by this patch. Concurrent callback mutation, user-created awaitables
driven on another loop/thread, and all arbitrary dynamic Python object protocols
are not established by this static audit or the 18 sequential inputs.
