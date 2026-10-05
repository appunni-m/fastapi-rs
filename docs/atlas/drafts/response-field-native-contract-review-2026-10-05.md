# Response-field lifecycle, provenance and measured evidence

Measured implementation: `ebcdf2d2c6c333bbfb04a19d122ad778eb3cbbd6`.
This later documentation checkpoint records that frozen source and build;
it does not establish full FastAPI compatibility.

## Inputs and native ownership

The active `response-field-lifecycle` input contains **16 parity cases,
61 HTTP actions and 16 construction observations**: 32 state reads and 29 probes.
One unsupported-model constructor has no HTTP actions. Async endpoints isolate
these inputs from the unresolved sibling background-task worker boundary.

The independently authored inputs contain no expected outputs, copied tests,
private FastAPI imports, target detection or case-specific implementation paths.
Construction outcome/class/message, actual warnings, exact HTTP observations and
lossless prior raw sends are retained. State records preserve bytes, container
kinds, message keys and ordering. No normalization or new fault hook was added.

| Input or native file | SHA256 |
| --- | --- |
| Recipe | `2213314fc5a3bbc6100ad791e61bbe2c0bfd61deb11ee25358392e12a6b1cd6a` |
| Workload | `a763538464f0e3a8809daa5fb55ba123a78b852d546170165a370e4f30682d68` |
| Generated input | `e38e3111c17c140732368053bcebff60b7fd65538ff98154d65c4562c0e5d92c` |
| `response_field.rs` | `aa943aa0caa352ba579b58f9a1b3c0ee4f660c3f9400366d023b954e97aba825` |
| `application_runtime.rs` | `9608a3aacce77d8583617eed6a840dd48910fee3a0f256cb1463cd16b2dfeaad` |

Safe Rust retains original response fields and adapters at route declaration.
FieldInfo attributes and metadata are reconstructed in source order, undefined
attributes are excluded, and the source warning category is suppressed only
during adapter construction. Only PydanticSchemaGenerationError is translated to
the existing FastAPIError; unrelated user exceptions propagate. Selected public
hooks expose construction, warning behavior, validation and retained reuse.

Included contexts own separate fields. A visited branch prepares all its own
direct fields before matching, descends into child branches when traversal reaches
them, and publishes its local fields only after successful preparation. Short app
borrows retain owned references; field callbacks and retired-record drops occur
outside those borrows. This preserves the existing immutable flattened routing
boundary; it does not implement router-version refresh.

Native response-class choices retain omission/default provenance and every
explicit object, including None. First-explicit selection follows route, router,
include and app precedence. Returned Response objects bypass response validation;
otherwise retained fields select dump_json only for eligible defaults, or
dump_python followed by the actual chosen response constructor. Explicit None
reaches the ordinary call error. Python runtime files remain native re-exports.

Admission adds 82 fixture links to eight existing public operations. The generated
corpus has **551 workflows/2,287 cases**; the manifest has 460 symbols, 469 required
public/inherited candidates and 1,235 fixture links. The 1,593 source candidates
remain classified as 460 supported by source evidence, 1,102 private/internal and
31 uncertain, with 21 root exports. These are source classifications and fixture
mappings, not a claim that the target implements the entire corpus.

## Live diagnostic and normal verification

Both implementations ran in isolated identity-checked processes. Pins are
FastAPI 0.141.1 (`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`), sole Starlette
1.6.0 oracle (`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`) and immutable
Starlette-RS (`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`). Runtime/build versions
are CPython 3.12.13, Pydantic 2.13.4/core 2.46.4, AnyIO 4.12.1 and Rust 1.98.1
on arm64 macOS 15.7.7. Original FastAPI and Starlette distributions are absent
from the target runtime.

- Before integration: **16 selected, 6 passed, 10 failed, 0 not_run cases**.
  Comparison `b80e49cc-64cf-4f7b-85c5-20737b3b84a6` preserves the differences.
  Source completed 61 actions; target completed 49, with 12 actions not run after
  three unexpected include-keyword constructor errors. Case-level zero not_run
  does not imply all old-target actions executed. Other failures exposed missing
  eager fields, repeated adapters/warnings and incorrect explicit-None inheritance.
- After integration: **39 complete workflows, 191 selected/passed, 0 failed,
  0 not_run**. The new 16-case comparison is
  `af485709-4e66-4ed9-bd15-35ce6e790161`; source
  `8de6db0e-4e82-4045-875a-3f43e6c24a26`, target
  `3539ba20-8e6b-4c3a-ae85-54fb9c1d864b`.
- Independent review checked 117 normal receipts and all three diagnostic
  receipts against current input/index/manifest bindings. Each implementation
  completed 445 actions and 15 direct API probes in the normal selection.
  Seven matched constructor-error outcomes have no actions. New source16
  observations match the prior oracle; all new source/target records match even
  without sorting object keys. A legacy OpenAPI pointer observation has eleven
  object-key insertion-order differences accepted by the declared JSON-map
  comparator. Full artifact/raw JSON serialization equality is not claimed.

Normal receipts and equal initial/final snapshots are under
`parity-results/response-field-wave/final-normal/`. The independent audits are
`response-field-normal-evidence-audit-2026-10-05.md` and
`response-field-pre-native-diagnostic-review-2026-10-05.md` in this directory.

| Frozen normal binding | SHA256 |
| --- | --- |
| FastAPI-RS source | `cce83012a8c17d3544885096afa70498a3970fb8ea5ec3239b76fa4b8ff23330` |
| Starlette-RS source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `2e07a686038c2b1b5cb37b25fc438d10304d7d72d82364f138bcfb2a2b866bb6` |
| Normal FastAPI extension | `6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e` |
| Starlette extension | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Normal native pair | `10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73` |

## Fresh incremental coverage

One separate normal instrumented build completed six fresh workflows:
12 first-request + 5 lifecycle + 5 callable-record + 23 classification +
15 awaitable + 16 response-field = **76 passing parity cases**.
Forty-two per-workflow source/build checks plus the final check, **43 total**,
all agree. The actual normal module identity is fault compilation=false;
export and imported binaries match.

Coverage-MCP accepted **823 newly covered regions**, increasing the accepted
union from **12,833/31,160 to 13,656/31,160** (+2.6412 percentage points).
The new batch covers 8,410 regions; 7,587 overlap prior accepted work.
The explicit provider request includes all four previous reports, including
`awaitable.json`. The original orchestrator hints omit awaitable and are retained
unchanged as a diagnostic; the corrected provider request prevents overcredit.

Normal build ID:
`fastapi-rs-instrumented-sha256:b2b5959d8135af904b6c9091dc9885f41cc71060e3dc87dd3fd1f12abdb864c7`.
Instrumented extension:
`59fc37f6167ef3e8880f0dd71df35af9bb77e114d2e6a6e64b7b8d52b9f6a899`;
native pair `0b7f91efd0f46e703c60d9986cee079ce5f2c67007d1f67e90958fa50c6f1691`.
Evidence, profiles, ledger, configuration and provider request/result are under
`parity-results/coverage/response-field-normal/ebcdf2d-first/`.

Coverage describes FastAPI native imports, construction, execution and cleanup
for these workflows. It does not attribute regions to individual cases, cover
sibling/Python code or establish full-suite regressions. The provider reports
regression status unknown. Old revisions and fault region inventories are not
unioned. The normal helper hash is
`53e5fff8bd7de0c39b46d64499a2856d2245dbbad5569843029fa529edd8cba6`;
the fault helper hash is
`4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5`.
Completed build logs complement declared flags/features.
The independent finished-receipt audit is
`response-field-measurement-receipt-review-2026-10-05.md` in this directory.

## Separate fault contracts and restoration

The isolated fault-enabled instrumented build completed **55 ordinary parity
cases plus six existing target-only fault contracts**, with all 36 source/build
checks agreeing. Source fault cases are explicitly not applicable; the target
executes all six. Its 31,360-region inventory is separate from normal coverage.
The compiled fault feature and isolated module path were also checked directly
after the measurement closed, against the measured installed binary hash.

Fault build ID:
`fastapi-rs-instrumented-sha256:f80d754461077076a0e1d3ce0501323a4b67ba2d6934881306ac3694f67ff25a`;
extension `75d2417d21d28232444e1b23f43ab948b785b6ce50082ad23f80c0a4e0bbced9`;
native pair `0da22ae04bed6245fe08b5ec0c2bf7ecde07c549db4e949ff94702385149577c`.
Receipts are under `parity-results/coverage/response-field-fault/ebcdf2d-first/`.
No new injection point was added. Public schema-hook failures remain ordinary
parity stimuli; existing injected cleanup contracts are regression evidence,
not independent proof of every field constructor failure. Repeated cases across
lanes are not counted as additional unique normal cases.

After both instrumented lanes closed, the normal extension was rebuilt.
`parity-results/response-field-normal-restore-snapshot.json` proves agreement
with the original measured source, both normal extensions and combined pair,
export/installed equality, module path and fault compilation=false. Runtime
boundary checks passed. The identity-only import emits the existing inherited
WSGI deprecation warning; import-warning parity is not measured here.

## Checks and remaining work

Formatting, strict workspace Clippy, Rust policy, facade, API/metadata,
recipe/index/atlas and recursive dependency checks passed. Benchmark input and
contract checks passed; no new benchmark was measured. No unit tests, unsafe
blocks, broad lint suppressions, Python runtime logic or target dependencies were
added. Historical proposal/design copies retain their pre-implementation status;
this report supplies the later implementation and live evidence.

Unproven boundaries include dynamic router/version refresh, raw included-route
proxies, OpenAPI/URL/WebSocket field traversal, empty-prefix inclusion, mutable
models/default placeholders/metadata, forward-annotation frame namespaces,
warning-context replacement, concurrency/reentry, additional/streaming field
lifetimes and V1 guard runtime behavior. Constructor cause/context/suppression
flags were implemented and reviewed but are not selected runtime observations.
Existing include/dependency-plan callbacks still need broader app-borrow review.

The complete 18-case worker gate remains unpassed because pinned sibling
BackgroundTasks crosses its thread-bound classes. Latest reviewed sibling
`a57e4e892b7e17b58fa76e20000b07935d4a37af` retained the same background module
blob. The isolated sibling proposal/pin decision remains pending; no sibling
change was made. New equivalent worker benchmark claims remain blocked.

The independently reviewed next backlog has **seven cases/42 actions** for
whole-branch failure/retry, nested parent/child ordering, early full/partial
matches, 404, slash redirects and returned Response setup. Inputs are retained
under `proposals/response-field-traversal/`, outside the active index. Pure terminal
405, refresh, concurrency and workers remain separate. Admission and fresh live
source/unchanged-target observations are the next gate.
