# Additional response field: independent evidence review

Date: 2026-10-05. Reviewer: `override_reanalysis`. Read-only helper/JSON/log review; only this TMP report is authored. No helper, application, worker, parity, build, install, native-binary read or unit test was executed. Root owns fresh measurements. Rust implementation review is outside this report.

## Helper and pre-build requirements

Reviewed `/private/tmp/fastapi-additional-response-field-normal-coverage-runner.py`, SHA-256 `a716a3d8f18d2b79691db13883599aad129dd71d4b7c18372be3f5f7b6abd30e`. It invokes the canonical parity CLI for whole materialized workflows, selects only parity cases, fixes inputs/recipes/workloads plus metadata/manifest/index, and uses one prepared normal instrumented build. It does not build/install. Eight selections use freshly measured same-build reports. The six previous hints are these reports from this run, not historical report reuse:

| Label / hint role | Whole workflow | Cases |
| --- | --- | ---: |
| baseline | `first-asgi-request` | 12 |
| previous / prior 1 | `dependency-lifecycle` | 5 |
| records / prior 2 | `dependency-wave-callables` | 5 |
| classifier / prior 3 | `dependency-callable-classification` | 23 |
| awaitable / prior 4 | `generator-awaitable-protocol` | 15 |
| response / prior 5 | `response-field-lifecycle` | 16 |
| traversal / prior 6 | `response-field-traversal` | 7 |
| batch / new measurement | `additional-response-field-lifecycle` | 3 |
| **Total** | | **86** |

The helper's receipt argument is optional and its checks are permissive: it compares top-level `source_tree_sha256` only when non-null, and compares only entries provided under `source_trees`. An empty receipt would not establish a pre-build source binding. A meaningful receipt must provide both:

- `source_tree_sha256`: exact combined digest using sorted named digest entries.
- `source_trees`: exactly named `fastapi-rs` and `starlette-rs` digests, from the target worker's tracked plus nonignored source hash rule (paths, symlinks, file/missing markers and bytes).

Keep receipt/build log under ignored evidence or TMP so writing them does not itself change the captured source tree. Pre-build provenance should also retain exact `repositories`, Rust `source_hashes`, metadata/manifest/index/input bindings, `environment`, `features`, `profile`, `target`, `rustc`, and exact build `command`. These extra fields are independently auditable evidence; this helper does not validate all of them. Record no fault-injection feature for the normal lane. A prior normal binary pair is only a restoration reference, not the new instrumented pair. Supply `--build-log` and `--build-receipt`; their paths and file digests enter the emitted build configuration/build ID.

The helper checks that export and installed FastAPI hashes agree, asserts the exact b4c sibling revision, and records a direct native-module identity with `fault_injection_compiled is False` and exact installed module path before measuring. Schema-9 target receipts additionally prove False. Legacy receipt omission is not an explicit False observation; the direct identity and canonical target worker guard retain the lane proof.

Note the hash names: initial/target receipt `target_binary_sha256` is the two-module runtime pair; build-configuration `target_binary_sha256` is the single export file. The configuration separately records `runtime_native_pair_sha256`, installed FastAPI and installed Starlette hashes. Compare like fields.

Each selection has six CLI before/after fixed-state checks plus one export-after check; successful eight-selection closure adds one final check, for **57**. All must be true. Report/context/build IDs, report SHA, source hashes, profile digests, exact result paths/hashes/run IDs and ordered case ledgers must agree. Identity-profile files are outside per-workflow profile directories. Coverage selects only `fastapi-rs/src/` and `fastapi-rs-py/src/`; it does not expand generic sibling coverage. Region attribution is workflow-level, not per-case.

## Actual normal build receipt: clear

Root supplied a completed normal build and started fresh coverage. Read:

- `parity-results/additional-response-field-normal-instrumented-pre-build-receipt.json`: SHA-256 `f0caf0b6bc87bb4467f2b94a9a7668dc1eec2a764963e86bbe2de4e4bf12d43b`.
- `parity-results/additional-response-field-normal-instrumented-build.log`: SHA-256 `a6f588f6d6d6b6dee900d6fdfe13d935f4953eeef38aa7ffafc9b5e9cb76d457`, ending in finished release/build installation against the exact sibling. Root reported exit 0.
- Current `parity-results/coverage/additional-response-field-normal/827612f-first/build-configuration.json` and initial snapshot.

The actual receipt supplies both mandatory source keys and all provenance fields above: repositories `827612f28226dc5c0d6e008d1a38231c03293389` / `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`, eighteen Rust source hashes, metadata/manifest/index/new-input bindings, `RUSTFLAGS=-C instrument-coverage`, empty wrapper, incremental disabled, LLVM profile unset during build, extension-module feature only, release profile, aarch64 Apple target/toolchain and exact native builder command. Its old normal restoration reference matches the saved 203-case pair. The new config references the exact receipt/log hashes.

| Recorded binding | Value |
| --- | --- |
| Project source | `f7cd6b9ef3d93cd2da3c85a45a4a9eaf4ab1aeb97620d96c7ab2c44e7c1b166c` |
| Sibling source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `204d9a6aa869e6ec5623f6a93c07fa7973910784c7b63e64efd21f51ea17edf2` |
| Export / installed normal instrumented FastAPI | `8560d80af37594007d5624706da53decd7fbfef33e28839b615560ad45d22cd3` |
| Recorded installed sibling | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| New normal instrumented runtime pair | `d6f31c9483eb9e7c78d9198c0a0ab98c4eb50270abd664573a2dc818bb4e399b` |
| Normal instrumented build ID | `fastapi-rs-instrumented-sha256:790a865fd710376fd0e2bca1f0de1a5c27e3ab3769780714b8c7725f54b2f1ea` |

This is recorded receipt/config evidence, not a reviewer recomputation from native files. Coverage was still in progress when this section was authored; partial baseline/previous output is not closed 86-case evidence. No build-receipt blocker was found.

## Closed normal 203 receipts: independently cross-checked

Read `parity-results/additional-response-field-wave/final-normal/normal-runs.json` (SHA-256 `10e356e1741f51f89000858dc169c1d0f6472ac90ccd2d66d6d697310e333810`) and all referenced source/target/comparison JSON documents. All **43 whole workflows / 203 cases** were selected and passed, with zero failed/not-run cases. Every artifact completed without infrastructure errors, exact declared case order was retained, and all recorded HTTP actions completed. Schema-9 summaries additionally show zero fault selections. Product inputs and saved snapshot input digests agree.

Initial/final snapshot bytes are equal, SHA-256 `3a2922a1a05b366ac3f15faae56fd0d93f8f2c54b792db2898f097baa7da2318`. Every target artifact/result identity binds the saved combined source `204d9a6a...` and normal runtime pair `8e1888dbe104c3bdf69f63b47bb0e9ded4a3ba9cc70d2c04676890134501f6ed`. The measured FastAPI-RS revision was `6da823585dbe4605ff1e04204eee287813eb34e8`; the sibling was exact b4c. The later commit changes Git revision, not the source bytes, as the pre-build receipt records. Source identities consistently pin FastAPI 0.141.1, Starlette 1.6.0, Python 3.12.13, Pydantic 2.13.4/core 2.46.4 and both oracle commits. Six schema-9 target artifacts explicitly prove False; 37 legacy artifacts omit the field. No legacy omission is represented as explicit False.

The uninstrumented saved pair differs from the new instrumented pair by design. This review does not claim current installed-binary equality after lane changes. Normal 203 is behavioral regression evidence, not a coverage receipt for 203 cases.

## Fresh normal coverage and separate fault lane

Normal measurement is now closed; root reported exit 0. The reviewer independently read the eight reports/contexts and all 24 source/target/comparison result artifacts. Report/context SHA-256 values, run IDs, exact case order and completed statuses match. All 86 cases pass, all recorded HTTP actions complete, every ledger row exactly matches its indexed contract/requirement refs and emitted result bindings, and the 57 expected fixed-state stages are present in order and true. Context configurations/build IDs and all eighteen source hashes agree with the captured initial snapshot. Native file bytes were not read by this reviewer. Five schema-9 workflow target artifacts explicitly record False; three legacy workflow artifacts omit the flag, with the common direct False identity retained.

All reports have the same 31,473-region native universe. Covered counts are baseline 11,961; previous 9,359; records 10,490; classifier 9,829; awaitable 9,334; response 8,457; traversal 8,284; batch 8,010. Totals were checked against the sums of retained native file summaries. Each workflow records its own profile and owned context; hints include exactly the six prior paths from this same run, in order. No historical profile or fault report is included.

The saved `coverage-mcp-comparison.json` contains actual invocation args and structured result. Its args match the hints exactly. Result status is `improved`, incremental evidence `verified`: the accepted baseline/six-prior union grows from **14,022 to 14,127 covered regions out of 31,473**, with **105 newly observed regions**. Batch alone covers 8,010, of which 7,905 were already observed. Gained workflow-level groups are additional-field construction 66, additional-description handling 24, response declaration retrieval 14 and included-field materialization 1. These sum to 105. `regression_checked` is explicitly False, and the stored reason says the full suite was not rerun; no full-suite or per-case coverage claim follows.

| Closed normal artifact under `parity-results/coverage/additional-response-field-normal/827612f-first/` | SHA-256 |
| --- | --- |
| `runs.json` | `6709e33f2097a820875d288583862d4d8ac26ddeb3fee5e2c2bfb9d80c36002c` |
| `case-ledger.json` | `98c0ad99b33793101e868617f2f56db02ef41087b8d0a24808ad8efc40f38130` |
| `comparison-hints.json` | `90d9dc740d8d68f8b8b1d525d3d2176c35deaf1b3d86adb5c28d0ab974ac58e3` |
| `source-build-state-checks.json` | `0a1377067abb7587bfa2f4b90e5f8c7380eb7af92dd0b278a7ce4484456e071d` |
| `build-configuration.json` | `e60a9422e9d11d257243798bc182f5cb18751bc4aa341025c6d2eb2dabc07e24` |
| `initial-source-build-snapshot.json` | `ed4362577f55ee1464308f668d676f1fb8dd8f5ee1a27b8df7232d751f3a3f65` |
| `native-build-identity.json` | `a009ec3fa17f1175ebb536d1a34bb5d62136fa16b12c4e70c5fae0133c40e57e` |
| `batch.json` | `3da6c83931c7f7bd14334ff0c40b7025b73ca2a60414c7980a8dfb68a657dead` |
| `batch.json.context.json` | `3c787602a3397e864678fd53e6dc84084ef089820d88b11219243c2cdf28b61e` |
| `coverage-mcp-comparison.json` | `f373bd62aec740118e9a098c89dd162b92a8694280e56bd9059c3ad705391e79` |

Fault build and measurement are now closed with root-reported exit 0. Independently read `parity-results/coverage/additional-response-field-fault/827612f-first/`: five reports/contexts, all fifteen referenced result documents, the complete ledger and all 36 expected fixed-state stages. Every record agrees on build/source/result hashes, run IDs, exact declared case order, contracts and requirement refs. All **55 ordinary parity cases and 6 target-only faults / 61 cases** pass. Every target and ordinary source action completes. All six source fault rows are `not_applicable`, with no source actions; every target artifact explicitly proves `fault_injection_compiled is True`.

| Fault selection | Whole workflow | Ordinary parity | Faults |
| --- | --- | ---: | ---: |
| baseline | `route-invocation-fault-contract` | 0 | 2 |
| previous | `dependency-sync-parent-nested-async` | 7 | 1 |
| records | `dependency-record-public-protocol` | 17 | 1 |
| dynamic | `dependency-dynamic-cache-policy` | 13 | 1 |
| batch | `dependency-override-cache-policy-mutation` | 18 | 1 |
| **Total** | | **55** | **6** |

The pre-build fault receipt matches normal and fault snapshots on both source trees, combined source, all eighteen Rust hashes and repository revisions. It records the explicit `fastapi-rs-py/fault-injection` feature, isolated Cargo target/venv/binding paths and `--fault-injection` build command. Its log/receipt hashes match configuration refs. The separately saved direct native identity records True, the exact isolated fault module path and the installed file digest. Each merge command references only its own workflow profile directory, excluding that direct-identity profile.

Fault build ID is `fastapi-rs-instrumented-sha256:78fef6dc1520f1e504cadc83efe0376952e2d781ca9beb7a97188118e80a09ac`, export/installed hash `7b925c4c4b812f813402a25aef461104f38440061ee2de83fe999d8930c8c291`, runtime pair `378d72dc87c4dd8cd6e36043606b64a894820955102c3e61f7283a41c52b217b`. These differ from the normal instrumented build ID/pair. Fault region universe is 31,673, versus normal 31,473. The five fault reports' covered counts are 8,028 / 10,031 / 10,616 / 12,199 / 9,882; they are deliberately not unioned into normal MCP evidence. Fault's own hints have three prior fault-lane report paths; no normal path is present.

The six actual fault observations retain the established contract strength: the pre-dependency route fault exposes full `builtins.RuntimeError`/unchanged point message, HTTP 500 and then HTTP 200. The five after-dependencies faults expose the exact after-dependencies point message, HTTP 500, then one HTTP 200 events-only body: `{"events":["dependency-enter","dependency-cleanup"]}`. All error sends have the selected start/body message-type pair. The ordinary user refusal/retry of additional3 remains normal parity; it needs no new target fault. No broad hook or comparator change was added.

| Closed fault artifact | SHA-256 |
| --- | --- |
| `runs.json` | `5f3190d07d93a53f1721a2051f0cf7f8717c96c706beadb2cf218e40b4464042` |
| `case-ledger.json` | `ffd42606050998327b38febdbdc8453362134432c81dbabf730d9ee1b5faa40a` |
| `source-build-state-checks.json` | `8a7c331ffcbb2686e322fde98a62846fd6ebb7ddc82efe624e9954ec929d6b65` |
| `build-configuration.json` | `bd5a56b3edfe8ec6c71036d4e875be6eecd18bac6a949b7a8d6d32e7e5574fb0` |
| `initial-source-build-snapshot.json` | `8826e84be7abd420d6f426e3f17391969e32c6f54d929e25aa2271e7e2039254` |
| `comparison-hints.json` | `2bf2304e34f9673e95ac606382730ce20c18d13b39d72d5a6d022f37ab352a81` |
| Pre-build fault receipt | `ff9048df144ccd6e0ad0c614f18c0b7aaf90f5465efefdbef158c51e4ba74b92` |
| Fault build log | `b12d55bc82172e51e5e31535f73bc51003154ede89202bf7115a67b560b99ee7` |
| Separate direct fault native identity | `aeac61941af708c7228fde246987d3c7b0f42b41e30cba6cc28bd00b9b058f1b` | Do not union the fault profiles, regions or receipts into the normal 86 measurement. Source fault cases must be `not_applicable`; ordinary parity cases must complete on source and target, and all six target fault outcomes/recovery selectors must pass the existing exact contracts. No new fault hook is required for the publicly reachable schema refusal in additional3.

The earlier six cleanup fault contracts remain a bounded regression scope: RuntimeError/500 plus later success, and five yielded-cleanup journals before endpoint invocation. They do not establish additional-field cache identity, response-field schema hooks, worker scheduling or per-case regions. The immutable sibling BackgroundTasks worker-crossing blocker remains separate and unchanged.


## Exact normal restore: recorded proof checked

Read `parity-results/additional-response-field-normal-restore-snapshot.json`, SHA-256 `0714a90ccbc9e50cd34979f4c869032ea092be1f64a7d50f22fa5f6247113213`, and `parity-results/additional-response-field-normal-restore-build.log`. The log ends with a successful release build/normal installation against b4c; its actual SHA-256 `cb72abdbf6d0cfc20e35c5f8b52ff78101b67d899772f9b46e12bdd471086425` matches the receipt.

Every recorded restore source-tree and native-pair field equals the closed 203-case initial reference byte-for-byte. The reference artifact digest is the independently checked `3a2922a1a05b366ac3f15faae56fd0d93f8f2c54b792db2898f097baa7da2318`. Recorded source is `204d9a6aa869e6ec5623f6a93c07fa7973910784c7b63e64efd21f51ea17edf2`; normal module digests are `5eeae03b977c74fed3808df9194bef0d23527a8208b2c05c92f9415084b7a244` / `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`; combined pair is `8e1888dbe104c3bdf69f63b47bb0e9ded4a3ba9cc70d2c04676890134501f6ed`. The exact-restored flag is True. Current revision is recorded as `827612f28226dc5c0d6e008d1a38231c03293389`; the source bytes match the older measured commit as explained above. The direct recorded native identity proves False and the exact normal installed module path.

This is an artifact-consistency audit of root's live restore proof. The reviewer did not rehash current native binaries or import current applications while root's frozen benchmark owns the environment. Benchmark execution/results are outside this report; none were run or claimed here. No normal/fault coverage union, full-matrix coverage/regression claim, per-case region ownership, new fault hook, mutable-source contract or resolution of the sibling BackgroundTasks blocker is inferred. Normal203, selected normal86 coverage/MCP, separate fault61 and exact restore receipts are all internally consistent within their stated boundaries; no blocker was found.
