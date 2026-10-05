# Native worker dispatch and immutable callable classification

Measured implementation: `a03de4bb06bce926a92b947430272381b71b8285`.
The implementation checkpoint is pushed. This report and subsequent inactive
proposals are documentation changes after measurement; the receipts below belong
to the measured source tree, not an unspecified later HEAD.

## Scope and pins

FastAPI 0.141.1 (`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`),
Starlette 1.6.0 (`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`),
Starlette-RS `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`, CPython 3.12.13,
Pydantic 2.13.4 / Core 2.46.4, AnyIO 4.12.1, Rust 1.98.1, arm64 macOS.
The selected sibling remains `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`.

The active corpus added 41 input-only cases / 108 actions:

- `dependency-callable-classification`: 23 cases / 54 actions.
- `worker-dispatch`: 18 cases / 54 actions.

The corpus now indexes 549 workflows / 2,256 cases / 1,543 partial source
mappings. Inventory and mappings do not establish support or complete parity.
During admission the classifier inputs gained handling-errors documentation
evidence and ordered response headers. The generated contract rejected direct
operation overlays for internal ResponseValidationError and DependencyScopeError;
generated error outcomes remain mapped through the public route/handler and
dependency operations without promoting those types to a public API claim.

## Integrated native behavior

The Rust classifier removes partials before unwrapping and follows the pinned
routine/class/call-method checks and coroutine predicate. Dependency execution
awaits the selected framework operation once: classified coroutine scalars enter
the real await-error/cleanup path, while a worker's returned awaitable stays raw.

Ordinary HTTP routes capture original endpoint kind. Sync endpoint invocation
and response-model validation use the pinned sibling worker boundary; async
endpoint validation stays on the loop. Full validation includes extracting and
prefixing error details in that same context. A boxed continuation preserves
the body/configuration and resumes once. Serialization stays on the loop;
eligible omitted-default models use Pydantic dump_json, while concrete response
classes retain the Python-value constructor path. App borrows are released before
callbacks. Returned Response and streaming/frontend/WebSocket paths keep their
existing boundaries.

Ordinary FastAPI-produced response-body messages now omit `more_body`, as the
pinned source does. Streaming flags remain unchanged. No fixture normalization
was added. Runtime Python remains native re-exports and literal `__all__`, and
the original FastAPI remains absent from the target runtime.

## Normal live comparisons

**37 workflows / 160 cases passed**, including 137 regression cases and all
23 newly admitted classifier cases with the stronger header observations.
Source, input hashes and both installed native libraries remained fixed between
the initial and final snapshots, and every target receipt matched those hashes.

Receipts:

- `parity-results/worker-classifier-wave/final-normal-without-blocked-worker/normal-runs.json`
- `initial-source-build-snapshot.json` and `final-source-build-snapshot.json`
  in that directory.
- New classifier comparison:
  `parity-results/comparisons/a796c9e6-a72a-4b20-a299-e3bf8f7fbb97.json`.

Measured source trees:

| Identity | SHA-256 |
| --- | --- |
| FastAPI-RS source | `867fcfc41f222759d20628ad9294d7f539d003618590352b22a065c447fbc33a` |
| Starlette-RS source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `bd4bd96759cca83194c57ee150e845ddf296d121c44d891a13db50b891584141` |
| Normal FastAPI native library | `5020552b6fa0a58fdf0eafe36f981dfa0a997eb97bb0d514479e8f0e38ba3b0d` |
| Starlette native library | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Normal native pair | `21b33a522e47d72d5acebc726817176bad96f86a8d4d5362d9ef2c8be9053c4a` |

## Incremental coverage

A separate normal build used `-C instrument-coverage`, `CARGO_INCREMENTAL=0`
and only `pyo3/extension-module`. Four selections passed **45 parity cases**:
first ASGI slice 12, dependency lifecycle 5, callable controls 5, classifier 23.
All 29 source/build/input checks matched. Export and installed FastAPI libraries
matched, and profiles were exported only for FastAPI-owned source prefixes.

Coverage-MCP verified **244 newly covered regions**. The accepted union grew
from 11,873 to **12,117 / 30,085 regions**, an increase of 0.811035 percentage
points. This is a same-source, same-build selected-workflow union. Full-suite
regression status and per-case region attribution remain unmeasured; neither
the previous revision nor fault-enabled maps were mixed into it.

Build ID:
`fastapi-rs-instrumented-sha256:2754d5df6883a6f8dbe907d842efc85ea3a231b36201636d4cee955e196e30df`.
Instrumented native pair:
`31f550ec42917d7d1836a5fe08318cbf71e077998cbc4ca88bdc34daadaf61ae`.

Evidence directory:
`parity-results/coverage/worker-classifier-normal/a03de4b-final/` contains
`runs.json`, `case-ledger.json`, source/build checks, reports/contexts,
`native-build-identity.json` and `coverage-mcp-comparison.json`.
The first attempt in `a03de4b-first/` stopped because its temporary orchestrator
incorrectly required the older @2 result schema to expose the newer fault-build
identity field. The successful rerun independently verified the installed native
identity as normal; the public runner also enforces that lane. No product case
or assertion was changed to repair this orchestration error.

## Fault contracts

A distinct fault-enabled instrumented build passed **55 parity cases plus all
six selected target-only cleanup/recovery fault contracts**. Its 36 source/build
checks matched, and all indexed case/requirement/point bindings were retained.
The oracle fault rows are not applicable; the target executes and asserts them.

Evidence: `parity-results/coverage/worker-classifier-fault/a03de4b-first/`.
Build ID:
`fastapi-rs-instrumented-sha256:8590365b5f93dc27b838f2532ae7447c03ee5c9d96f91d327d86e7f9397690ea`.
Fault native pair:
`68cdc46f93b80af362d111cbec7f6889d2a6cb584dc611635533ac457bcbf445`.
The fault map denominator is 30,285 regions and is separate from normal coverage.

These six faults precede endpoint-worker invocation and response validation.
Five recover through state routes; they do not establish fresh resource re-entry
or failures inside a pending worker. Ordinary callback/validation failures belong
in source/target parity. The separate static scope audit is
`worker-classifier-fault-contract-review-2026-10-05.md`.

## Unpassed worker gate and dependency correction

All 18 worker cases completed against the live oracle:
`parity-results/oracle/57ac9013-acf9-4a1a-b944-7717036735be.json`.
The target workflow crashed at sync endpoint `background_tasks.add_task` because
the pinned native BackgroundTasks collector is `unsendable`. A loop-created
collector is accessed from the source-required worker. Its worker-created
individual task would likewise be accessed later on the loop. The failed
transport/stack is preserved in
`parity-results/worker-dispatch-target-diagnostic.log`. A crashed workflow proves
no passing subset of the 18-case gate.

Committed sibling `d0769b005ce12dce2c8fce5945800a42a3810960` retains the same
background native/wrapper blobs. Taking that revision does not repair this bug.

The reviewed proposal in `sibling-background-cross-thread/` removes the
thread restriction only from the two task data classes, which store owned Python
handles. Strict Clippy accepted the normal PyO3 transfer bounds in an isolated
checkout. Scheduling, classifier timing and thread-bound continuations stay
unchanged. It remains a proposal: the shared sibling checkout, configured pin
and installed dependency were not changed. A corrected, reviewed dependency
revision and live worker parity are required. FileResponse and StreamingResponse
cross-thread stores remain separate gaps outside the current 18 inputs.

## Checks, restored runtime and remaining work

Recipe materialization/index/validation, metadata/API checks, dependency/license
inventories, Pydantic Core inventory, dependency graph, benchmark contract,
Rust policy, formatting, strict Clippy and source/installed runtime boundary
checks passed. No unit tests, pytest, unittest or Cargo test were run.

The normal uninstrumented build was restored and its source and both libraries
exactly matched the measured normal snapshot. Receipt:
`parity-results/worker-classifier-normal-restore-snapshot.json`.
Documentation added after this check changes the full source-tree hash, not the
measured implementation or installed libraries.

The worker gate is incomplete, so no new benchmark suite or performance ranking
is claimed. Adapter construction/reuse, Field metadata and warning timing,
explicit placeholder provenance, classification history, generic await protocols,
audit hooks, cancellation/concurrency and broader response classes remain open.
Reviewed inactive next inputs contain 13 generator-awaitable cases and 16
response-field lifecycle/provenance cases under `proposals/`; they contain no
expected outputs and have not run against either implementation. The generator
adapter patch is also unapplied and uncompiled.
