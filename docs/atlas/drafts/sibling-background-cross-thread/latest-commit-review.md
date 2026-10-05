# BackgroundTasks crossing into a sync worker

Read-only comparison of the immutable sibling pin and the latest committed local
sibling. No sibling edits, builds or execution; no new pin was selected here.

## Conclusion

Latest commit **d0769b005ce12dce2c8fce5945800a42a3810960** does **not** repair the
BackgroundTasks loop-to-worker crossing. This comparison uses committed blobs.
Both native task classes retain the unsendable thread checker, and their wrappers
and borrowing flow are unchanged from the pinned commit.

| Evidence | b4c8a65 and d0769b |
| --- | --- |
| `starlette-rs-py/src/background.rs` Git blob | `a2437e8aa89426a434b9ff020b1686effb8efbf3` in both commits |
| `starlette-rs-py/python/starlette/background.py` Git blob | `0600f2a10236a12d1dfb8c6ab41b1e858adcae2b` in both commits |
| Native BackgroundTask declaration | `#[pyclass(name = "BackgroundTask", unsendable)]`, line 22 |
| Native BackgroundTasks declaration | `#[pyclass(name = "BackgroundTasks", unsendable)]`, line 114 |

`git diff b4c8a65c85e1b0d251ca05874412811eaa3ac7b8
d0769b005ce12dce2c8fce5945800a42a3810960 -- starlette-rs-py/src/background.rs`
and the corresponding path history are empty.

The local sibling checkout was clean at the first inspection. A later read-only
status showed concurrent changes in `scripts/parity/adapters/value_lifetime.py`,
`scripts/parity/contract.py` and
`tests/fixtures/sources/parity/public-value-lifetime.yaml`. This conclusion is
about the exact committed `d0769b` blobs above; those working-tree changes were
not edited or reviewed here.

## Public source path and unchanged target path

Pinned FastAPI `dependencies/utils.py:715-718` creates the injected BackgroundTasks
while solving inputs on the request loop. Source sync endpoints then run in the
worker (`routing.py:342-354`). Starlette 1.6.0 `background.py:26-41` uses ordinary
Python object fields/list append, so add_task from that worker and later callback
execution on the loop are source-reachable public behavior.

The prospective FastAPI worker draft creates the target tasks value at
`application_runtime.rs:5977-5987`, then passes it to the prepared sync endpoint
worker. The unchanged sibling Python wrapper's add_task calls
`self._inner.append_task(BackgroundTask(...))`. The collection's native
append_task method at `background.rs:153-157` must borrow the loop-created
unsendable native collection on the worker, triggering its thread restriction.

The new BackgroundTask wrapper/native object is itself created on the worker.
Even if only collection append were bypassed, later loop execution calls the
native task's run and reads its fields in BackgroundTaskCall, crossing that
second unsendable boundary. Both native classes require source-matching thread
ownership, while their continuations can remain tied to the loop that drives
them. This is generic sibling behavior; a FastAPI-only private append bypass or
an inline sync endpoint would not establish the public worker contract.

## Other release-owned changes

The latest interval contains distinct ownership changes, including:

- `f9191561cb84e9d2e270918bb025bccd96dae78c`: streaming thread ownership and
  middleware exception chains in runtime_calls/base_http_runtime.
- `452ad40080a10ca4e95b26dd5bf3e01b4a81b716`: template portal thread parity.
- `bc54da45849ca372121b8318041ffbc81048aec1`: Request cycle collection and
  coroutine finalization; the latest form context uses regular PyO3 classes with
  Python-visible shared state (`request_runtime.rs:1930-1953`).
- `7c02f8540081096a642e7a1528e0919973a8c355` and `d0769b...`: public-value cycles,
  UploadFile callback ownership and backing-file replacement during arithmetic.

Those changes do not modify either background-task blob or class declaration.
They provide no source evidence that the reported BackgroundTasks crossing is
fixed. Selecting latest under the user's existing authorization still requires
fresh identity/pin/contract verification; it cannot be recorded as this repair.

The old six route fault cases contain no BackgroundTasks crossing. Their pass
does not establish worker18's sync background case. Preserve that input and
exact observations while the generic sibling repair is handled by its owner.
