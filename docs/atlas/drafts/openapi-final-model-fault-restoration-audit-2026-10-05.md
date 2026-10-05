# Final OpenAPI model: closed fault coverage and restoration audit

Independent read-only audit, 2026-10-05, after the parent closed fault measurement, provider comparison, restoration, direct native proofs and runtime boundary checks. Scope: `parity-results/coverage/openapi-final-model-fault/62dacc5-first/` and closed `next-openapi-response-field-wave/measurement-receipts/`. The prepared stdlib audit routine passed; separate raw-export reconstruction and authorized current-file hashing also passed. No application, compiler, builder, parity/LLVM process or native module was executed/imported. Only TMP documentation was written.

## Actual fault-lane results

| Selection | Ordinary cases/actions | Injected cases/actions | Covered regions / 32,702 |
| --- | ---: | ---: | ---: |
| Route-invocation baseline | 0 / 0 | 2 / 4 | 8,726 |
| Sync-parent/nested-async | 7 / 24 | 1 / 2 | 10,729 |
| Record protocol | 17 / 41 | 1 / 2 | 11,314 |
| Dynamic cache policy | 13 / 50 | 1 / 2 | 12,991 |
| Override-policy batch | 18 / 34 | 1 / 2 | 10,580 |
| **Total** | **55 / 149** | **6 / 12** | workflow counts must not be added |

All five ordered source/target/comparator triples are completed and infrastructure-error-free, with verified result hashes/run IDs, input/recipe/workload/index bindings, requirement references, contexts and full case-ledger equality. All 61 selected outcomes pass; comparator failed/not-run counts are zero. Source intentionally marks six target-only fault cases `not_applicable`, with no constructors/actions for them. Its 55 ordinary constructors and 149 actions complete successfully. Target completes all 61 constructors and 161 actions. Ordinary user error/recovery cases remain ordinary parity; their errors are not relabeled as injected faults.

All 36 fixed-state checks are true and exactly ordered: 35 per-workflow checks plus final `all-selections-complete`, spanning 14:38:48.601972–14:39:28.628796 UTC. The early missing-fault-venv preparation stop was resolved before the successful fault pre-build receipt and build; it is not a product case failure or substituted measurement.

Actual injection observations expose `builtins.RuntimeError`, one at `http.route.invoke.before` and five at `http.route.invoke.after_dependencies.before`. All six select the complete start/body message-type pair, HTTP 500, then a completed HTTP 200 recovery. The five dependency-cleanup bodies decode to the recorded dependency-enter/dependency-cleanup journal. Canonical fault assertions enforce those public contracts with source N/A. They do not assert OpenAPI adapter/cache internals, exact injected exception text, complete raw 500 body/headers, or source-equivalent injected behavior. No new fault assertion or expected output was introduced.

## Exact source and isolated build

Root remains `62dacc5283a0cee282258e268f7545765679e974`; sibling remains `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Combined source is `503211630df8f7e2bf624c55c217d08444658252311bff19bf6568b4736a4c0f`. It matches the pre-build/backup/restoration source records, every target identity and coverage context. All 21 Rust hashes and policy/builder hashes agree. Current whole-tree hashes and both Git HEADs were independently checked after restoration and still match those frozen records.

Fault build ID: `fastapi-rs-instrumented-sha256:271a69886baf9045e660d00010052770b7d1971ea6e9704e80aeb9dd749be20b`, recomputed from configuration. Fault installed/export FastAPI hash: `dd0d309e2a01376c95b9e954ba65cdb93a6d73ff2a1af2f9cb4147f7a5810f70`; unchanged sibling: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`; fault native pair: `69a88d70a9ca3bbb506287d91168694dcc3df46ff545d8ac318f4cfe63efd346`.

Configuration/pre-build records declare normal extension plus binding fault feature, with explicit binding-to-core fault forwarding, instrument coverage, incremental off, disabled wrapper, Rust 1.98.1/aarch64 macOS, and pinned CPython 3.12.13. The completed log records successful isolated release compilation (32.96s), installation under `target/fault-injection/python/fastapi_rs`, fault-venv activation, and exact sibling pin. Full shell environment remains parent-receipt attribution rather than independently printed compiler environment. Actual LLVM profiles/export prove instrumentation; every target receipt and the closed isolated direct proof report `fault_injection_compiled=true`. Direct module path is the intended `target/fault-injection/python/fastapi_rs/_core.abi3.so`, with the isolated fault venv command. Current fault installed/export bytes were independently hashed after normal restoration and still equal the recorded fault hash.

The closed `fault-built-native-proof.json` also records that the normal instrumented installed/export copies remained `df2e89029f4d640cd76c09a91dee4358e981245a2cbfd4c76439dff5eab80382` through isolated fault building. Its normal direct identity remained false and its path remained the normal package. This preservation claim precedes the later deliberate restoration to uninstrumented bytes.

## LLVM and separate provider acceptance

Each workflow has one retained target profile with verified checksum. All five raw exports reconstruct exactly to the published canonicalized native-only file/function reports and totals. They contain 21 native files, 1,493 function records and a common 32,702-region denominator; no LLVM mismatch/out-of-date stderr diagnostic appears. Workflow commands select their own profdata and the one fault export; source profiles are excluded.

The actual fault Coverage-MCP request matches its hints: fault baseline plus fresh `[previous, records, dynamic]` and fault batch, all with the same source/build/features/native pair and passing result bindings. Provider `isError=false`, evidence `verified`, status `improved`: own prior union **13,864/32,702**, **8** newly covered regions, combined **13,872/32,702**. `previous_batches=3` and `regression_checked=false` are retained. No normal report appears in the request.

This fault-feature result is separate from normal build `75cf0c99…`, normal denominator 32,502 and its accepted 121-region gain. The mixed fault workflow profiles include ordinary and injected execution; neither case-region attribution nor full-matrix coverage follows. No normal/fault or cross-revision coverage union is made.

## Exact normal restoration

`normal-native-restored.json` records installed, export and sibling restoration at 14:39:58.104347 UTC; the direct normal proof follows at 14:39:59.033635. Independently hashed current originals and saved backup files match all three entries:

- Normal installed and export: `d934ba09884e6c8a657300c4800a92e76577285f2bf5833e73418d21912b6140`, exactly the uninstrumented normal gate/backup bytes.
- Sibling original and backup: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`, unchanged before/after.
- Restored normal pair, computed from these digests: `e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0`.

The closed direct proof reports fault=false and the normal `_core.abi3.so` path, with that exact module hash and `exact_release_restoration=true`. Its source object equals the saved backup source. The retained installed runtime-boundary log confirms target installed, upstream FastAPI absent, native-only facade and no upstream runtime dependency; parent reported exit 0. The proof log's existing Starlette WSGI deprecation warning is retained and is not a boundary failure. These import results are the parent's closed observations; this reviewer performed file hashing only.

## Evidence hashes

| Artifact | SHA-256 |
| --- | --- |
| Fault `runs.json` | `4d920ac633c9de5d8969fb2c207d90d5387c7f8d391249ad624756adf49a9f03` |
| Fault `case-ledger.json` | `407dd330a25c03df100d21cb37159eef470662739ced21b44aa4504e57198c6f` |
| Fault state checks | `d36d42cfe5dcc09242e6cccbbb8d57cf51a7f9fa920b784a8b847be4c7f7c770` |
| Fault build configuration | `f9e3593de2da2b7d4193ea8779406a26df83809851cc9ccb98f63de3a0e182ef` |
| Fault provider args/result | `d8700510711c1b1f7c8e64f07075543f91b654c33654b4331cf991f08a2c5b62` |
| Fault build log | `61c4529e331ad5a769f3c90eece037157055bdc88a96d1d32d70de08a53ccf45` |
| Fault pre-build | `5781188b029146c16077b1f5f87dbd2825410f820a74bad769ca46ce8074ad3e` |
| Fault built native proof | `e2bfd1542669f3e8cbb106acaf03636feaea50df31e69be1f6c8753b099d7b33` |
| Normal restored record | `e8ec90d665be9fb3d5d6b2154b2f43c2c2c38b3fcb672a6cc2903a96f05795fa` |
| Normal restored native proof | `1dc8a6927c1152153653c98b1599534b19667d0f13f60ad7822925f18f820f74` |
| Restored boundary log | `78ea5bb704ab2030594c429e06018859ca38348d340840032afea101dfedf167` |

No concrete fault receipt, provider, source/build isolation, preservation or restoration blocker remains. Heavy parsing/hashing ended before benchmark timing was released; this note makes no benchmark claim.
