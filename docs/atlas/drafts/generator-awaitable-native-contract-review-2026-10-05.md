# Generator awaitable native contract and evidence

Measured implementation revision: `4b4a18c13d1f201f8aa4d406c9b3535998ef3dd6`.
This report is a later documentation checkpoint, not the measured source tree.
Full FastAPI compatibility remains unfinished.

## Input and implementation boundary

The active `generator-awaitable-protocol` workflow has **15 parity cases,
47 HTTP actions and 15 construction observations**. The historical proposal has
13 cases/40 actions; admission added two public Future-error controls without
changing its user workload. They cover original coroutine cleanup/recovery and
ordinary returned-generator throw/warning behavior. Fixtures contain no expected
outputs, implementation detection, private FastAPI imports or copied tests.

The retained observations include status, ordered headers, body bytes, actual
errors, ordered message types, warning category/text and 21 public state reads.
The user ASGI observer preserves prior messages' key presence, byte values,
container kinds and ordering. Warning records are not filtered by the workload
or comparator. Admission added 100 fixture links to eight existing public
operations; inventory and reviewed source classifications are not target support
evidence. The generated corpus is 550 workflows/2,271 cases, far larger than the
selected passing regression set below.

| Input binding | SHA256 |
| --- | --- |
| Recipe | `25ec7b17fca058944654ca98e7331601a441bc3c25bff0f97b796d26ee903256` |
| Workload | `41f6ad6e99746620627947d93a71f8390857ccf6b0e5ba8f5f8b151c3daff356` |
| Materialized input | `ba021904c37edbdd0e5561de821813b8cbddb9f3ed5cbc42510a54a3ca0bbe65` |
| Final `awaitable.rs` | `4682e03475874a2eb7066560b92af19af6cc7fe8e4073180b2071648f47ae55d` |

Safe Rust now retains the original iterator for native coroutines and flagged
generator-based coroutines, rejects forbidden coroutine results from `__await__`,
and uses the single-exception throw form for original coroutines and ordinary
generator iterators. The selected non-iterator error text matches the pinned
CPython behavior. The source boundaries were reviewed against
[CPython 3.12.13 genobject.c](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c).
Owned PyO3 references preserve delegation across existing continuations. Resume,
send, close and cleanup stages remain in native code. No Python runtime helper,
new target dependency, unsafe block, unit test or broad lint suppression was added.

## Live diagnostic and normal parity

All runs used FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`,
Starlette 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and the immutable
Starlette-RS checkout `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. CPython was
3.12.13, Pydantic 2.13.4/core 2.46.4, AnyIO 4.12.1, Rust 1.98.1 on arm64
macOS 15.7.7. Original FastAPI/Starlette distributions are absent from the
target runtime. Source and target run in separate identity-checked processes.

- Before the native change: **15 selected, 5 passed, 10 failed, 0 not_run**.
  Comparison `727f1ab3-4d80-4418-80d6-1bfa65900947` retains every diff.
  Failures include direct flagged-generator delegation, invalid await-result
  acceptance, error wording and legacy throw warnings. The earlier sccache
  permission failure had no comparison and is excluded from product results.
- After the change: **38 complete workflows, 175 selected/passed, 0 failed,
  0 not_run**. The new 15-case comparison is
  `3800d1cf-fe62-447e-94a3-91f1ffe355e2`; source
  `962f4def-b840-45ee-9c82-456d25a266ac`, target
  `12b67b98-f71c-4e41-950e-50c8445f4a4e`. Normal regression receipts are under
  `parity-results/generator-awaitable-wave/final-normal/`.
- Independent receipt review checked all 114 normal artifacts and the three
  valid diagnostic artifacts, exact index/recipe/workload/manifest/case-order
  bindings, 384 actions and 15 direct API probes per implementation. Canonical
  source/target case records are identical. Six selected constructor-error
  outcomes were observed and matched; no case filtering or skipped steps occur.

| Frozen normal binding | SHA256 |
| --- | --- |
| FastAPI-RS source | `f66d9e7f264dea6933019e46394be44f9dd223988b04351a638c30246e72300b` |
| Starlette-RS source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `da7d0dc2e2c42b94152a49d373887b3a3f9ae53c3010bcf92569ec906d1b492c` |
| Normal FastAPI extension | `0de3ac9a9c81d9d40ca8c77567a4582acfa768c4b1aef0e427420e040e29a873` |
| Starlette extension | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Normal native pair | `3a119e2a97afe041e7c43f2912c0ee763c77cd20b1054c32aba8f6a57c80c95d` |

Every normal target artifact binds these source/binary digests; initial/final
snapshots agree. Measurement helpers make no builds or installs. Sources,
inputs and binaries were frozen during each measurement lane.

## Incremental coverage, separate from normal results

One fresh normal instrumented build ran **60 passing parity cases** across five
complete workflows: first request, dependency lifecycle, callable records,
classification and the new awaitable input. Thirty-six state checks bind fixed
sources, inputs and binaries. The direct native identity proves
`fault_injection_compiled=false` and the actual installed extension path.

Coverage-MCP accepted the same-source, same-build incremental region comparison:
the accepted union increased from **12,149/30,145 to 12,311/30,145**, adding
**162 regions** (+0.5374 percentage points). Normal build ID:
`fastapi-rs-instrumented-sha256:a2aa522ddae1fad19f7cb1aeb3575d43191f0f7f2e58daff88f806e67b36f27d`.
Instrumented native pair:
`35af64058fe6d2ed95cf2e60eabafaeae8a5a6d22605ddb6aaa677670dbd85de`.
Receipts, context/ledger, profiles and accepted provider result are under
`parity-results/coverage/generator-awaitable-normal/4b4a18c-first/`.

Coverage is native FastAPI code for those selected workflows. Per-case region
attribution, full-matrix regression coverage and generic sibling/Python coverage
are not established. The gain includes shared error paths, not only awaiter
functions. Old revisions and fault-enabled region maps were not unioned.

The normal orchestrator SHA256 is
`62b7753cc7f650bc4438c1959ca54e636dea8649fba83609f456191f5c03f77e`;
the separate fault orchestrator is
`4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5`.
They invoke the canonical CLI and bind current input-index contracts, actual
receipt hashes and build identities. Build claims also retain the completed
frozen build logs/configuration; declarative flags alone are insufficient.

## Fault contracts and runtime restoration

A separate instrumented build in an isolated fault venv passed **55 ordinary
parity cases and six existing target-only fault contracts**. Source fault rows
are explicitly not applicable; the target executes all six. Thirty-six state
checks agree. Fault build ID:
`fastapi-rs-instrumented-sha256:166cbb4e29e96bda755d7fc2f4571cd3f8ccdf447f7a5e2edf7e1114bda7dd17`;
native pair `30c4a09c41a085bb23646d1dc906f6b9dc0d86e9d3457b06505d9d518e9b840a`.
Evidence is under
`parity-results/coverage/generator-awaitable-fault/4b4a18c-first/`.
Its 30,345-region inventory is separate from normal instrumentation.

No new fault hook was introduced. Invalid await values and throw/close failures
are reachable through ordinary public inputs, so they remain live parity cases.
Existing injected contracts cover ordinary native-coroutine/cleanup regressions;
they do not independently establish flagged-generator or Future throw behavior.
Repeated cases across lanes are not counted as new unique regression cases.

After measurements closed, the normal extension was rebuilt and restored.
`parity-results/generator-awaitable-normal-restore-snapshot.json` proves exact
agreement with the original measured source and both normal native hashes,
export/installed equality, native module path and fault compilation=false.
Runtime-boundary checks passed. The identity-only import emits the existing
inherited WSGI deprecation warning; import-warning parity is not measured here.

## Checks, remaining gaps and next slice

Metadata, API/dependency/benchmark contracts, recipe/index/atlas validation,
Python facade, formatting and strict workspace Clippy passed before the build.
There are no unit tests or unsafe/blanket-suppressed runtime additions. Benchmark
contracts were checked; no new benchmark was measured.

Remaining await-protocol gaps include extra gi_code audit events/rejecting hooks,
generic iterator throw arity/coroutine-wrapper provenance, slot lookup,
reuse/cancellation/GeneratorExit/arbitrary protocol calls, mutable history,
introspection and exact traceback/type-name behavior outside selected inputs.

The complete 18-case worker gate still crashes at the pinned sibling's
thread-bound BackgroundTasks collector. Latest sibling commit
`a57e4e892b7e17b58fa76e20000b07935d4a37af` retains the same background module
blob as the pin. A reviewed isolated two-attribute proposal exists; the pending
choice about sibling ownership/pin remains unresolved. No sibling edit or pin
change was made. It prevents a complete worker gate and new equivalent benchmark
claims, while independent FastAPI work can continue.

Next is the separately reviewed **16-case/61-action response-field lifecycle**
input: source-time construction and retained adapters, per-effective-context
lazy construction, exact warning/schema errors and response-class provenance.
Its native design is a proposal, not evidence of implementation parity.
