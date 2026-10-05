# Included response-field traversal: measured contract

Measured checkpoint: `9c29938bb63842421d16869df528a5c72398a0a4`.
This later documentation checkpoint records that frozen source and build.
Full FastAPI compatibility remains unfinished.

## Admitted inputs and implementation boundary

`response-field-traversal` adds **seven normal parity cases, 42 HTTP actions
and seven construction observations**: 24 state reads and 18 ordinary probes.
The independent public workload covers whole-branch field failure/retry,
parent-own fields before child traversal, earlier full/partial matches, misses,
slash redirects and returned-Response field setup. A one-use user schema-hook
refusal is an ordinary public input; it is not a native injected fault.

Inputs contain no expected outputs, copied tests, private cache inspection,
target detection or implementation-specific dispatch. Exact selected state
bodies retain callback order, actual handler errors, warnings and all prior
non-state raw sends, including bytes, tuple/list distinctions, key presence and
header order. An early state route observes the preceding request without
advancing a later included branch.
Authoring-time draft comments are retained in the byte-identical active copies;
the reviewed metadata/index and this report identify their admitted status.

| Frozen input binding | SHA256 |
| --- | --- |
| Recipe | `3dfd1caa6573faa55edaef83e1eb166e4279a97542bda323a4ea8ab2de929c66` |
| Workload | `35aa2d46026953a69ac6284f6a0215c62df22e19ddac0018c9d31336224de4d9` |
| Generated input | `2b1c485e4e34b30a9c4d9d524036d3b709d3e8dcf514116a76fdd9b6cbfd6655` |
| Metadata | `4d7c3566f1cd282852c158cbe2a374f14e54fac5338a5c584059b61c8fb26cb7` |
| Manifest | `73dc8ac2edba66d65829b9b0b09f44b890846643fbf45c4a3a3b912e2bc1ee6f` |
| Materialized index | `c52f827d1a91192a57d523d8a6747d9604b6757c67d3911b25fe3f384785434c` |

Admission adds **65 links to 11 existing public operations**. Nested
APIRouter.include_router maps only the nested-tree case; FastAPI.post maps only
the earlier POST/later included GET case. All seven register exception_handler;
only the refusal/retry case invokes it. JSONResponse remains sibling-owned.
The corpus is 552 workflows/2,294 cases and 1,300 fixture links. The 460 manifest
symbols, 469 public/inherited candidates, 21 root exports and source
classifications are unchanged. These mappings do not establish target-wide
support or promote internal DefaultPlaceholder/ModelField APIs.

No runtime change was needed. The Rust implementation, Python facade and native
normal extension remain identical to the lifecycle implementation at `ebcdf2d`.
Its whole-branch preparation/publication and separate effective-context owners
already satisfy the selected new behaviors. The prior implementation report is
`response-field-native-contract-review-2026-10-05.md`.

## Live normal comparisons

Both sides use isolated identity-checked processes: FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, sole Starlette 1.6.0 oracle at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and immutable Starlette-RS at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Versions remain CPython 3.12.13,
Pydantic 2.13.4/core 2.46.4, AnyIO 4.12.1 and Rust 1.98.1 on arm64 macOS 15.7.7.

- First unchanged-target comparison: **7 selected/passed, 0 failed/not_run**;
  comparison `b452100a-345c-4aa7-82fa-24e3dc8d9c8c`, source
  `a64dc1e8-cf99-4c69-a40e-da1ba396776d`, target
  `03fbe455-559f-4067-b51f-b3fcd582e1f2`. All seven constructors and all
  42 actions completed on both sides.
- Full selected regression: **40 complete workflows, 198 selected/passed,
  0 failed/not_run**. Each implementation completed 487 actions
  (482 HTTP + five WebSocket) and 15 direct API probes. Seven matched
  constructor-error cases have zero planned actions; no normal step was blocked.
  New seven-case comparison: `6cf888fb-3df4-4075-8b40-719ea3b2f1f8`.
- Independent review checked all 120 full-run receipts and three first-run
  receipts against current schemas, index/contracts, commands and actual result
  hashes. The fresh seven-case records match the first run on both sides and
  match each other without sorting object keys. All 36 prior probe sends are
  retained; the 18 body messages omit more_body. Eleven legacy OpenAPI object-key
  insertion-order differences remain accepted by the declared JSON-map interface;
  full legacy raw JSON serialization equality is not claimed.

Receipts and equal initial/final snapshots are under
`parity-results/response-field-traversal-wave/pre-change/` and `final-normal/`.
Independent notes are `response-field-traversal-pre-evidence-audit-2026-10-05.md`
and `response-field-traversal-normal-evidence-audit-2026-10-05.md` in this directory.

| Frozen normal binding | SHA256 |
| --- | --- |
| FastAPI-RS source | `6d4b05e3c6c26fa4d7669c1dd127d62b46287e41a7e0aad97043a484c7346bce` |
| Starlette-RS source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `5d8dffaa7a2ae9ba2c79ecd0d92b5323c33396fa8ddfb702cceac4c7e985d138` |
| Normal FastAPI extension | `6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e` |
| Starlette extension | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Normal native pair | `10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73` |

## Fresh incremental coverage and fault regression

A fresh normal instrumented build ran **83 passing parity cases** across seven
complete workflows: 12 first-request, five lifecycle, five callable records,
23 classification, 15 awaitable, 16 lifecycle/provenance and seven traversal.
All 50 source/input/build checks agree. Coverage-MCP accepted the fresh baseline
plus all five fresh previous batches and the new seven-case batch:
**213 newly covered regions**, increasing the union from **13,656/31,160 to
13,869/31,160** (+0.6836 percentage points). The batch covers 8,237 regions,
including 8,024 already covered. Request and helper hints agree on all five priors.

Normal build ID:
`fastapi-rs-instrumented-sha256:6e30fe13b5d13094eee9bb348f6af9b1ad0722565340ac382cd350462b1a32f1`;
extension `d6869ca4eefc3c035e4369c1a0116598e74397b32e88196b604993cae20b8cbf`;
native pair `95632381ba9d949a631876b75d38eb8035a371ad81b0b66cca1d0648bc988eba`.
Evidence is under
`parity-results/coverage/response-field-traversal-normal/9c29938-first/`.
This is native workflow-level region coverage. No individual-case attribution,
sibling/Python coverage or full-suite regression is established; the provider
records regression status unknown. Earlier revisions were not unioned.
The finished normal/fault receipt and profile audit is
`response-field-traversal-measurement-receipt-review-2026-10-05.md` in this directory.

The separate isolated fault instrumented build passed **55 ordinary parity cases
and six existing target-only fault contracts**, with all 36 fixed checks agreeing.
Source fault rows are explicitly not applicable; target executes all six.
Its 31,360-region inventory remains separate. No new injection point or fault
case was added for the ordinary schema-hook refusal.

Fault build ID:
`fastapi-rs-instrumented-sha256:84cfa8d073426bb60ea6b94374ed3d659bb413d39ffbcf031a85f02e0a6346ef`;
extension `75d2417d21d28232444e1b23f43ab948b785b6ce50082ad23f80c0a4e0bbced9`;
native pair `0da22ae04bed6245fe08b5ec0c2bf7ecde07c549db4e949ff94702385149577c`.
Receipts are under
`parity-results/coverage/response-field-traversal-fault/9c29938-first/`.
Repeated cases across lanes are not additional unique normal results. Existing
fault contracts check their declared public error/recovery/cleanup outcomes;
they do not establish arbitrary response-field cache behavior.

After both lanes closed, the normal extension was rebuilt.
`parity-results/response-field-traversal-normal-restore-snapshot.json` proves
exact restoration of measured source, both extensions and normal native pair,
export/installed equality, module path and fault compilation=false. The isolated
fault module was separately checked as compiled=true against its measured hash.
Runtime boundary checks pass with original FastAPI absent and direct native
Python re-exports. The identity-only inherited WSGI warning remains outside
these import-warning observations.

## Checks, limits and next work

Canonical recipe loading, Ruff, generation/index/atlas, metadata/API, Rust
policy/facade, formatting, strict Clippy and dependency/benchmark contract checks
passed. No unit tests or benchmark workloads ran. No Rust runtime changes,
dependencies, unsafe code, broad lint suppressions or Python runtime helpers
were introduced in this slice. Historical input/source/helper reviews remain
under `proposals/response-field-traversal/`; temporary orchestrator hashes are
recorded in its runner review and actual receipt audits.

Dynamic route/version refresh, raw proxies, URL/OpenAPI/WebSocket field
traversal, empty-prefix validation traversal, source-equivalent locking,
reentry/concurrency, finalizers, additional/streaming fields and mutable
model/default/metadata history remain separate boundaries. Terminal 405 is not
selected by the earlier partial-to-later-full control. The complete 18-case
worker gate remains unpassed at pinned sibling BackgroundTasks; its
ownership/pin decision is still pending. No sibling change was made.

The independently reviewed inactive `proposals/response-field-recovery/`
backlog adds three cases/30 HTTP actions for retained parent fields after a
child fails, isolation between two contexts of one original router, and warning
filter restoration observed inside the public error handler. Unsupported YAML
merge syntax was expanded before canonical loader admission; the active loader
and contract were not changed. The optional fault feasibility note limits the
existing basic contract to RuntimeError, complete 500 and later 200, without
adapter/cache assertions.

The next implementation gap is **additional response-field construction and
OpenAPI timing**. Source fields are constructed at endpoint attachment and per
visited include context; current native code eagerly builds core/JSON schemas
when creating the decorator and clones frozen schema descriptions. A separate
source-backed note outlines three bounded lifecycle controls and owned field
storage; fresh independent inputs and live diagnostics are required before a
native repair. Its findings and a terminal405 control are retained in
`response-field-next-control-priority-review-2026-10-05.md`.
