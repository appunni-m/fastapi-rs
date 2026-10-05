# Response-field measurement receipt audit — 2026-10-05

## Scope and conclusion

Independent read-only audit of retained actual measurements at FastAPI-RS revision `ebcdf2d2c6c333bbfb04a19d122ad778eb3cbbd6`. No repository, helper, result, report, fixture, metadata or sibling files were modified. This note is the only new artifact. No app/native import, build, install, parity, unit framework or coverage-provider query was executed by this reviewer. Static JSON parsing, hash checks, source reads and recorded-proof inspection were used.

No measurement-integrity blocker was found. Normal76 passed on one normal instrumented build; the separate fault61 lane passed on one isolated fault instrumented build. Normal Coverage-MCP accepted a verified gain of **823 regions** against the fresh baseline plus all four fresh prior batches. The original helper hints omit the awaitable prior report; the actual provider request includes it and the accepted result records four previous batches. The omission is preserved and is not used for attribution.

## Source and build identities

- FastAPI 0.141.1 oracle commit: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0 oracle commit: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Starlette-RS pin: `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.
- Recorded CPython 3.12.13; Pydantic 2.13.4/core2.46.4; shared packages and platform agree in source/target receipts.
- Recorded compiler: `rustc 1.98.1 (48a229cea 2026-09-01)`; target `aarch64-apple-darwin`; declared instrument flag `-C instrument-coverage`.
- Combined source digest for both lanes: `2e07a686038c2b1b5cb37b25fc438d10304d7d72d82364f138bcfb2a2b866bb6`.
- FastAPI source digest: `cce83012a8c17d3544885096afa70498a3970fb8ea5ec3239b76fa4b8ff23330`.
- Sibling source digest: `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`.
- Normal build ID: `fastapi-rs-instrumented-sha256:b2b5959d8135af904b6c9091dc9885f41cc71060e3dc87dd3fd1f12abdb864c7`.
- Normal exported/installed FastAPI native digest: `59fc37f6167ef3e8880f0dd71df35af9bb77e114d2e6a6e64b7b8d52b9f6a899`.
- Normal imported native pair: `0b7f91efd0f46e703c60d9986cee079ce5f2c67007d1f67e90958fa50c6f1691`.
- Fault build ID: `fastapi-rs-instrumented-sha256:f80d754461077076a0e1d3ce0501323a4b67ba2d6934881306ac3694f67ff25a`.
- Fault exported/installed FastAPI native digest: `75d2417d21d28232444e1b23f43ab948b785b6ce50082ad23f80c0a4e0bbced9`.
- Fault imported native pair: `0da22ae04bed6245fe08b5ec0c2bf7ecde07c549db4e949ff94702385149577c`.
- Shared sibling extension digest: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.

The normal native identity records `fault_injection_compiled=false` and the public binding extension under `fastapi-rs-py/python/fastapi_rs`. Every @9 normal worker receipt records false; legacy @2 workers omit the receipt field but canonical worker rejection of fault builds and the recorded direct native false check apply. All fault worker receipts record true and use `target/fault-injection/venv/bin/python`; the after-close native proof identifies the isolated fault extension and matching digest. Export and installed digests are equal within each recorded lane. Build IDs recompute exactly from their configuration JSON and differ between lanes.

Completed build logs identify CPython3.12.13, successful release compilation, the exact sibling checkout, and the normal or isolated fault installation location. Their hashes equal configuration references. The normal pre-build receipt has matching individual/combined source digests. The fault configuration explicitly has no pre-build receipt. Exact flags are recorded configuration rather than a full printed compiler invocation; real profiles and LLVM exports prove usable instrumentation but do not provide complete reproducible-build attestation.

## Actual workflows and receipts

All 33 oracle, target and comparator artifacts have matching retained SHA256 and run IDs. Every artifact is completed with no infrastructure errors. Input, workload and manifest digests match current indexed files as inspected before documentation editing. Case order, cardinality, unique IDs, verification lane, requirement references and ledger bindings agree exactly with the index. Per-selection saved run objects agree with `runs.json`; contexts agree with report digests, common source file hashes, configuration/build IDs and receipt summaries.

Normal lane: **76 parity cases**, **191 completed actions per product**, 76 ledger rows. Fault lane: **55 parity + 6 fault cases**, 61 ledger rows; 149 completed ordinary parity actions per product and12 completed target fault actions. All six fault oracle cases are `not_applicable` and contain no actions. No selected case IDs overlap between lanes. Source fault N/A is not parity execution evidence. Comparator summaries have zero failed/not-run cases; @9 parity/fault subtotals were checked without assuming legacy summary shape.

| Lane | Selection | Cases | Source run | Target run | Comparison run | Covered regions |
| --- | --- | ---: | --- | --- | --- | ---: |
| normal | baseline | 12 | `934be289-f6a1-48d1-8373-08175d434d7b` | `2fd08dbc-261a-410e-8b58-f83faef58501` | `dc6a3a79-2262-418c-ab96-d053cd29bba9` | 11826 |
| normal | previous | 5 | `8b0a98e2-8c7d-4107-b311-a71dd166be2c` | `cc0ad254-6a05-4da3-bc72-f3bf9a7d1a0b` | `12570afb-48e2-4365-91f4-3e16ebff16f6` | 9329 |
| normal | records | 5 | `0ef198f0-2e2e-49d8-8aa2-744fd1204a7a` | `ca76893f-6c8c-4ec7-965b-868face4d41b` | `a24832df-f398-41e9-a847-b97c6811624f` | 10354 |
| normal | classifier | 23 | `83e01390-ecd2-4e1b-8175-0c7423d9b2d7` | `b173c4af-da87-4082-b4f4-3a0b59a93137` | `eb703106-ab3f-4947-b536-f9b908d373ab` | 9799 |
| normal | awaitable | 15 | `4e402803-c551-4297-9be4-dfabce1703b8` | `3e6a9058-0ff2-499c-b19e-0217028ef410` | `d6171056-7af6-4c4a-944b-30181f979842` | 9277 |
| normal | batch | 16 | `cc7f6840-2328-4cfc-94ee-28c6ddc768ee` | `467b2f4e-0aed-4d45-9236-4c91dfc6aa02` | `404ac828-bafb-4fba-b5bc-63a14dd85306` | 8410 |
| fault | baseline | 0 parity + 2 fault | `85b39a0e-16b8-43f6-a6ca-4bbc83520bc7` | `6b15ad3d-c779-4964-a645-5deca9aa436b` | `586d19ed-a54d-45f8-9ac9-a5a845dcc45e` | 7998 |
| fault | previous | 7 parity + 1 fault | `db602114-b062-4bff-91e6-9c6a88660477` | `16369d3f-5676-4553-851e-63e0b5a7421c` | `a5335ca7-3bc5-4ec1-882b-f15c5080fef0` | 10001 |
| fault | records | 17 parity + 1 fault | `2f5ffc24-0fdb-48a2-9333-71125b99b3fa` | `6d539ea4-e93d-495c-9a7f-de0c5dbaad9c` | `c19bf4eb-8529-4948-b966-a46de62553d9` | 10586 |
| fault | dynamic | 13 parity + 1 fault | `f7039ffb-4ea1-48b2-9a14-7522ac444c41` | `345740cf-413c-4fe4-b2c6-86b47286735f` | `1e1869b2-d2f7-4839-96e0-4a000a244f6e` | 12046 |
| fault | batch | 18 parity + 1 fault | `f9c3ab3a-3251-4f46-8b2c-d1af4f5b98a9` | `3b4156ba-12e2-4522-898d-152c88973e44` | `ce254d81-21f1-4608-bb41-8ec5ef981bbf` | 9852 |

Normal selections are first-asgi-request12, dependency-lifecycle5, dependency-wave-callables5, callable-classification23, generator-awaitable15 and response-field16. The last workflow retains61 HTTP actions and16 construction observations, including a zero-action unsupported-model registration error case. Construction outcome/class/message, warning/error detail projections and raw-send state remain the admitted exact observations; no normalization was introduced. This audit checks their retained exact comparison success, not stronger observations absent from selectors.

Fault selections are route-invocation2fault, sync-parent-nested-async7parity+1fault, dependency-record-public-protocol17parity+1fault, dynamic-cache-policy13parity+1fault and override-policy-mutation18parity+1fault. This is a current-revision dependency/fault regression measurement, not an instrumented execution of response16 on the fault binary.

## Freeze and LLVM profile integrity

- Normal: **42 per-workflow checks plus one closing check =43**, all true, in the exact expected stage order; UTC timestamps are monotonic. Bounds: `2026-10-05T10:12:21.712200+00:00` through `2026-10-05T10:13:08.780120+00:00`.
- Fault: **35 per-workflow checks plus one closing check =36**, all true, in the exact expected stage order; UTC timestamps are monotonic. Bounds: `2026-10-05T10:20:01.249115+00:00` through `2026-10-05T10:20:41.556253+00:00`.
- Input/recipe/workload/manifest/index/metadata and all18 Rust source hashes match each initial snapshot. Both lanes retain the same Rust hash inventory.
- Each of11 workflows has exactly one retained `%p-%m` raw profile with matching saved digest. Merge commands consume only that workflow directory; the normal native-identity raw profile is excluded. Export commands use the lane-specific recorded dylib and its own profdata. All export stderr files are empty.
- Every final report exactly equals its raw LLVM export after documented native path canonicalization, FastAPI Rust file/function filtering and recomputation of retained file totals. No counters, regions, segments, function contents or other export values were altered.
- All six normal reports have identical retained file/region inventory:17 files and31,160 regions. All five fault reports have identical inventory and31,360 regions. Feature-dependent denominators and build/native identities remain separate; no normal/fault coverage union is made.

Profiles cover isolated target module initialization, public factory construction, requests and cleanup at workflow granularity. They do not attribute regions to individual cases and exclude sibling/Python coverage from final totals.

## Accepted normal coverage attribution

The recorded provider request selects the fresh normal `baseline.json`, four fresh previous reports (`previous.json`, `records.json`, `classifier.json`, `awaitable.json`) and new `batch.json`, with incremental scope and regions metric. No historical4b report appears. Coverage-MCP result has `isError=false`, status improved, source `matches_receipt`, tests passed and matching normal build IDs; incremental evidence is verified and previous_batches=4.

- Fixed normal region denominator:31,160.
- Prior accepted union:12,833 covered;18,327 missing.
- Batch:8,410 covered, including7,587 already covered and **823 newly covered**.
- Combined:13,656 covered;17,504 missing.
- Gain:2.641206675224647 percentage points;4.49064222185846% reduction of prior remaining gaps.
- Provider explicitly records regression_checked=false; selected-test incremental union cannot establish full-suite regressions.

The original `comparison-hints.json` lists only three prior reports and is preserved unchanged. The actual provider request, result and verified arithmetic establish the accepted four-prior attribution. Fault provider gain is not claimed in this note; only its completed measurement and receipts were audited.

## Recorded normal restoration bounds

The reviewer read the parent-recorded restoration proof and successful restored runtime boundary log; restoration was not reproduced. The proof matches the prior uninstrumented final-normal snapshot: same combined source digest, FastAPI native digest `6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e`, unchanged sibling digest and native pair `10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73`. It records exported/installed equality, exact prior normal restoration, isolated native identity false and the normal module path. The build log records successful restoration; the runtime boundary log reports installed FastAPI-RS, absent upstream FastAPI, direct native facade and no upstream runtime dependency.

This is a recorded point-in-time restoration proof after both measurement lanes closed. Later documentation edits legitimately change the repository source digest; they do not expand these measurement bounds or establish a new-revision build/run. No current binary or imported-module equality claim is made beyond the retained proof.

## Frozen reference digests

| Artifact | SHA256 |
| --- | --- |
| `/private/tmp/fastapi-response-field-normal-coverage-runner.py` | `53e5fff8bd7de0c39b46d64499a2856d2245dbbad5569843029fa529edd8cba6` |
| `/private/tmp/fastapi-lazy-dependency-coverage-runner.py` | `4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/initial-source-build-snapshot.json` | `3722ad18c04c2d859ed42c6a4b423d3391d2531cee0e3fe8e10558f91846021d` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/build-configuration.json` | `d3e3037d3e4a19cb8ca654e8069ddecc150d9a10f6b897c31993d6eb338d6e9f` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/native-build-identity.json` | `fe54cc6c47f02b24c8c241ac34d0e98d36b4fc1bb85a99016667d5c8f43cb5c4` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/runs.json` | `3ced037cc0238e6016be4fe21669262f8229c76aeea99105487d5c527e582b09` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/case-ledger.json` | `c393e2ee5b9219c8e2139e0974b2c235e27d6d97f694460dba8415ec69b47d2c` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/source-build-state-checks.json` | `dd0a34d6ab88e15b14614dc8e7d24ad7da7adf89cb2dafbdd5f83ab3fcce0990` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/provider-request.json` | `ee95357cee242476b02464ff86acd3b7a2f6773fffab72c0c7f36ac2efb0a9c2` |
| `parity-results/coverage/response-field-normal/ebcdf2d-first/coverage-mcp-comparison.json` | `d5727a1cb1e2082b35232e42ec569ae996a64f5c77062187ed2798943ca137b9` |
| `parity-results/coverage/response-field-fault/ebcdf2d-first/initial-source-build-snapshot.json` | `fa6c33fb95da9380776b13f1febe88b4f89ee51e1155a5315db96024c5e63303` |
| `parity-results/coverage/response-field-fault/ebcdf2d-first/build-configuration.json` | `0e0fdba72ca86154e9b328d5fe66c0831e250262236d17ea92c6e07d33da9bf8` |
| `parity-results/coverage/response-field-fault/ebcdf2d-first/runs.json` | `f63d3375231ead8730dab88cd57f8f52206d8ef541526abb51cca9081c3f83e6` |
| `parity-results/coverage/response-field-fault/ebcdf2d-first/case-ledger.json` | `adbf9d365ba04b57532a5e1ea95892baa549fd7cb10ad825bd8d6e49b17210f0` |
| `parity-results/coverage/response-field-fault/ebcdf2d-first/source-build-state-checks.json` | `238c7d275024ede49be006b24289cf0f9c8538d42f0cce73031c6f12be60ff41` |
| `parity-results/coverage/response-field-fault/ebcdf2d-first/native-build-identity-after-close.json` | `f036e00fb86f9d86d462d2c9be43ed0be2206b5418791cadc6acff7aa324ef48` |
| `parity-results/response-field-normal-instrumented-build.log` | `5f085994764900e7b703ff0ee9e8ccf3be61527a1985f40f99ec398c7d2730de` |
| `parity-results/response-field-normal-instrumented-pre-build.json` | `a9b1617b210addff13a6a3ba207c8a5148ae8025742a5ed92998f28f9560bc52` |
| `parity-results/response-field-fault-instrumented-build.log` | `62f23bebff87fb837c412e9985574535492d180a4b20be764077f2a478e46818` |
| `parity-results/response-field-normal-restored-build.log` | `4f69c4bac9ecd49e64c2678a3e51af2d40e6290d769987e0aaab2ce1212ff21b` |
| `parity-results/response-field-normal-restore-snapshot.json` | `c0ec1d1ed8478dd69cb0127f1852f4ff2a9662cc910f38c54d7170dda70bb585` |
| `parity-results/response-field-restored-runtime-boundary.log` | `78ea5bb704ab2030594c429e06018859ca38348d340840032afea101dfedf167` |

Per-workflow report, raw profile, profdata, source/target/comparison receipt hashes and commands remain in the retained run/context artifacts. The audit independently checked all receipt/profile/report references; this note does not replace them.

## Remaining boundaries

Coverage confirms observed control-flow reachability; it does not prove arbitrary FastAPI compatibility, case interchangeability or full regression absence. Mutable model/cache history, reentrancy, concurrent warning-filter mutations and response traversal branches absent from immutable16 remain outside that slice. Build flags beyond recorded configuration are not independently attested. Temporary orchestrators live outside Git source hashing, so their frozen digests above must accompany reproduction. No excluded generic sibling behavior is credited as FastAPI native coverage.
