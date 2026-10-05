# Response-field traversal measurement receipt audit — 2026-10-05

## Scope and conclusion

Independent read-only audit of retained actual coverage at FastAPI-RS revision 9c29938bb63842421d16869df528a5c72398a0a4. No repository, measurement helper, result, report, fixture, metadata or sibling file was edited by this audit. No app/native import, parity/comparator rerun, build, install, unit framework, LLVM command or coverage-provider query was executed. The reviewer read actual JSON/logs, independently checked hashes and recorded contracts, reconstructed the documented LLVM report filtering in memory, and read the parent's restoration proof. This temporary note is the audit's only new artifact.

No measurement-integrity blocker was found. The normal coverage lane passed **83 parity cases, 233 completed actions per product and 50 fixed-state checks**. Its fresh baseline plus five fresh previous selections established the accepted normal union before traversal7. The saved Coverage-MCP request/result accepts a verified gain of **213 regions**, from 13,656 to 13,869 of 31,160. The separately built fault lane passed **55 parity plus 6 target-only fault cases**, with 149 parity actions per product, 12 target fault actions and 36 fixed-state checks. Six oracle fault cases are N/A and contain neither actions nor construction observations.

Normal coverage, fault coverage and the earlier uninstrumented normal198 receipts remain separate. No feature-dependent coverage, import/module identity or historical report is unioned. Recovery3 is an inactive follow-on proposal and is not credited by these measurements.

## Fixed source and binary identities

- FastAPI 0.141.1 oracle commit: 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f.
- Starlette 1.6.0 sole oracle commit: 4f250d6b814587e20c5365f0a5f0c4d42bcb929f.
- Starlette-RS exact pin: b4c8a65c85e1b0d251ca05874412811eaa3ac7b8.
- Recorded shared profile: CPython 3.12.13, Pydantic 2.13.4/core 2.46.4, AnyIO 4.12.1; all other pinned shared packages and platform agree in every source/target receipt.
- FastAPI-RS source digest: 6d4b05e3c6c26fa4d7669c1dd127d62b46287e41a7e0aad97043a484c7346bce.
- Sibling source digest: 37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55.
- Combined source digest for both coverage lanes and recorded restoration: 5d8dffaa7a2ae9ba2c79ecd0d92b5323c33396fa8ddfb702cceac4c7e985d138.
- Recorded compiler: rustc 1.98.1 (48a229cea 2026-09-01); aarch64-apple-darwin; instrument configuration -C instrument-coverage.

The reviewer independently reproduced the tracked/nonignored source hashing rule using read-only Git inventories while source was frozen. It matched both individual digests and the combined digest above. Documentation editing was subsequently permitted after measurement/restoration closure. Later repository digests do not expand these bounds.

| Boundary | FastAPI native SHA256 | Native-pair SHA256 | Feature/module proof |
| --- | --- | --- | --- |
| Earlier normal198; restored after coverage | 6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e | 10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73 | Recorded native false; normal binding path |
| Fresh normal83 instrumented | d6869ca4eefc3c035e4369c1a0116598e74397b32e88196b604993cae20b8cbf | 95632381ba9d949a631876b75d38eb8035a371ad81b0b66cca1d0648bc988eba | Native false; fastapi-rs-py/python/fastapi_rs/_core.abi3.so |
| Separate fault61 instrumented | 75d2417d21d28232444e1b23f43ab948b785b6ce50082ad23f80c0a4e0bbced9 | 0da22ae04bed6245fe08b5ec0c2bf7ecde07c549db4e949ff94702385149577c | Native true; target/fault-injection/python/fastapi_rs/_core.abi3.so |

All three recorded pairs use sibling native digest fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5. Export and installed FastAPI hashes match within each recorded coverage lane. Pair hashes recompute from their constituent extensions.

Normal build ID: fastapi-rs-instrumented-sha256:6e30fe13b5d13094eee9bb348f6af9b1ad0722565340ac382cd350462b1a32f1.

Fault build ID: fastapi-rs-instrumented-sha256:84cfa8d073426bb60ea6b94374ed3d659bb413d39ffbcf031a85f02e0a6346ef.

Both IDs recompute exactly from configuration JSON. Normal features are pyo3/extension-module; fault adds fastapi-rs-py/fault-injection. Normal @9 receipts explicitly record false; legacy @2 receipts do not add that field, so their boundary is canonical normal-worker feature rejection plus the direct recorded native false proof. All fault receipts explicitly record true and use the isolated fault interpreter. The after-close fault native proof matches the measured digest and isolated module path.

Completed build logs identify CPython 3.12.13, successful release compilation, the exact sibling checkout and correct normal/isolated fault installation. Log hashes match configuration references. The normal pre-build receipt matches measured source; fault configuration explicitly has no pre-build receipt. Flags are recorded configuration rather than complete printed compiler invocations. Usable profiles/exports support instrumentation but do not provide full reproducible-build attestation.

## Actual receipts, order and contracts

All **36 source/target/comparison receipts** have matching retained SHA256/run IDs, completed status and no infrastructure errors. Per-selection records agree with runs.json. Input/workload/manifest digests match indexed files as inspected; recipe/input/workload digests match the index. Case IDs, order and counts agree with the index and receipts; all indexed cases have nonempty requirement references. The exact ledger matches indexed contracts plus observed statuses, references, report and build ID. Selected IDs are unique within and disjoint between lanes.

Contexts bind report digests, configuration/build IDs, all 18 Rust source hashes, receipt references and actual summaries. @9 parity/fault subtotals are retained without assuming legacy summary shape. Every ordinary source/target action ID matches input order and completed status. Every comparison case passes with empty diffs. The review changed no data, selector, outcome or normalization policy.

| Lane | Selection | Cases | Source run | Target run | Comparison run | Covered regions |
| --- | --- | --- | --- | --- | --- | ---: |
| normal | baseline | 12 | 4539f2ad-5e7e-49d4-ba07-cb043e4fe89c | 798f07eb-a9ba-4190-8283-49b86879d282 | 89d04f56-2425-4139-8d7b-fa9e7b763622 | 11826 |
| normal | previous | 5 | 0c6816f4-9772-4620-82cd-c917dee6e13b | fb334fb9-b9e9-47ae-a545-b9a49d9edca6 | f78c4f74-076b-4f5e-86ad-7ed567376783 | 9329 |
| normal | records | 5 | e5dedb51-4921-49ce-9913-176ec462a729 | 22b6e09a-fcc8-4241-89b2-0f911914aa92 | 11d86526-e81b-452d-8de3-04a73fd6c471 | 10354 |
| normal | classifier | 23 | f3ecbaa6-6144-4eb6-b451-65c6564fb331 | 001728e1-14e9-44d2-8b33-6d3318c04563 | 7061987f-79bf-492d-a185-54190b6b1802 | 9799 |
| normal | awaitable | 15 | 33a22607-efaf-48d4-a52a-905c568fd802 | de431543-bb0b-4b12-bd47-daa46a28ef1c | d90ffa11-18c3-4a1e-8f65-da3917262d08 | 9277 |
| normal | response | 16 | a00ea447-2a6e-49ba-8bf1-5dfce4539b9f | e84f8259-f223-418d-8ef3-364a84670d32 | 8b4ab9d1-1cf4-485e-83c7-ac8b5ef8c84c | 8410 |
| normal | batch | 7 | 55f2abae-a406-4572-a1d0-3e5ce2ef8151 | 0b2da24a-152f-473c-835f-0dbb7ffd4bfa | f2495884-2794-4843-a1e3-49f18b6fa11d | 8237 |
| fault | baseline | 0 parity + 2 fault | 8c03b701-7875-46c1-b472-2a7663803d05 | 6a928219-292a-4e39-b1c4-0f8f170f22d7 | 1e0add2d-4b95-40b3-b1f9-4b8f99766a8b | 7998 |
| fault | previous | 7 parity + 1 fault | 911cc011-bfa2-45e3-9e73-2ad5c556b473 | ed80f299-a647-4be2-9866-e1bd97d6e5e7 | 1357dd87-d90a-4ea1-95c9-77630f1f81dc | 10001 |
| fault | records | 17 parity + 1 fault | 1680a666-6235-4c96-bd89-5b70d608fe6d | d0f167ab-30e7-4930-acfd-e180825a6764 | d4811593-002d-498f-a893-82160675511e | 10586 |
| fault | dynamic | 13 parity + 1 fault | ba3f4bc6-4e45-430d-89a7-70924e21356a | 5578c828-24c7-4b7a-8d9c-9897153bdea6 | d6889eb9-70d9-43e6-8ee8-727af6894156 | 12046 |
| fault | batch | 18 parity + 1 fault | 58c0029b-490f-4fbd-bbb4-c1287af59df5 | 1ca978c1-af6c-4285-9eae-4cc1a2396326 | 0dbc664d-d762-4cef-8d85-1be6db57b4da | 9852 |

Normal selections are first-asgi-request12, dependency-lifecycle5, dependency-wave-callables5, callable-classification23, generator-awaitable15, response-field-lifecycle16 and response-field-traversal7. All five previous selections were freshly remeasured with this normal build. Response16 includes its admitted zero-action registration error: construction outcome/class/message is compared. Traversal7 has 42 completed HTTP actions and 7 construction observations, retaining its admitted exact status/headers/body, callback/warning/handled-error journals and raw sends. No stronger unselected observations are claimed.

Fault selects route-invocation2fault, sync-parent-nested-async7parity+1fault, dependency-record-public-protocol17parity+1fault, dynamic-cache-policy13parity+1fault and override-policy-mutation18parity+1fault. It is a current-source dependency/fault regression measurement, not instrumented traversal7 or response16 on the fault binary. Six actual RuntimeErrors, complete two-message 500 responses and later 200 responses satisfy existing named contracts; five cleanup contracts expose the required dependency-enter/dependency-cleanup public event body. Target-only cases are not oracle parity execution. Their contract passes do not assert response adapter cache state.

## Freeze and LLVM integrity

- Normal: **49 per-workflow checks plus closing check =50**, all true in exact expected stage order; monotonic UTC bounds 2026-10-05T10:47:06.431478+00:00 through 2026-10-05T10:48:00.145590+00:00.
- Fault: **35 per-workflow checks plus closing check =36**, all true in exact expected stage order; monotonic UTC bounds 2026-10-05T10:50:44.360997+00:00 through 2026-10-05T10:51:23.254144+00:00.
- Recipe/input/workload/manifest/index/metadata and all 18 native Rust file hashes match their snapshots at audit time. Lane snapshots retain the same Rust source inventory.
- Each of 12 workflows retains exactly one raw profile with matching recorded digest. Merge commands consume only that workflow directory. Separate normal identity/fault after-close probe profiles are excluded. Exports use the correct lane dylib and workflow profdata. All export stderr files are empty.
- Every report equals its retained raw LLVM export after documented native path canonicalization, native file/function filtering and recomputed file totals. Region/segment/function contents and other values are preserved; counters were not changed. Reconstruction happened only in memory.
- Normal reports share **17 files /31,160 regions**. Fault reports share their separate **18 files /31,360 regions**. Feature-dependent inventories are not merged.

Profiles include isolated target module initialization, public factory construction, requests and cleanup at workflow granularity. Final totals exclude sibling/Python coverage. Individual case ownership of regions is not measured.

## Accepted normal provider attribution

Retained provider request and hints both select fresh baseline.json, all five previous reports (previous.json, records.json, classifier.json, awaitable.json, response.json), and batch.json. Neither old nor fault reports are named. Result has isError=false, status improved, source matches_receipt, passing tests, matching build IDs, verified incremental evidence and previous_batches=5.

- Fixed denominator: 31,160 regions.
- Prior accepted union: 13,656 covered; 17,504 missing.
- Traversal7: 8,237 covered, including 8,024 previously covered and **213 newly covered**.
- Combined: 13,869 covered; 17,291 missing.
- Gain: 0.6835686777920411 percentage points; 1.2168647166361974% reduction of prior remaining gaps.

Count arithmetic agrees with retained reports/provider result. Provider internals were not rerun. regression_checked=false is preserved: selected-test incremental coverage does not establish full-suite coverage regressions. Separate uninstrumented normal198 parity is not a substitute coverage comparison. No fault provider gain is claimed.

## Recorded restoration bounds

The reviewer read parity-results/response-field-traversal-normal-restore-snapshot.json and successful restored build/boundary logs without reproducing commands. Source/native digests and pair exactly match both earlier normal198 initial/final snapshots. Proof records export_matches_installed=true, normal_measurement_restored_exactly=true, native false and the normal public module path. Identity stderr retains actual sibling StarletteDeprecationWarning; the reviewer neither edited nor suppressed it. Boundary log records native facade, absent upstream FastAPI and no upstream runtime dependency.

This is point-in-time recorded restoration after both measured lanes closed. It does not equate restored normal with either instrumented binary, prove a post-documentation build or establish an independent current-process imported-module identity. The audit read normal198 snapshot bounds, not all 198 separate comparison receipts.

## Frozen references

The table binds external orchestrators and principal evidence. Per-workflow receipt/report/context/profile hashes and merge/export commands remain in runs/context artifacts and were independently checked.

| Artifact | SHA256 |
| --- | --- |
| `/private/tmp/fastapi-response-field-traversal-normal-coverage-runner.py` | `ec89980f7a04c7e848c58ae7d72d009875b76d4a38a154ef22e0c64db117b851` |
| `/private/tmp/fastapi-lazy-dependency-coverage-runner.py` | `4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/initial-source-build-snapshot.json` | `2beb48d32d142738d8a9a7c4c0518e9a6750e2b240675331771b9916b26a94e2` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/build-configuration.json` | `53f15597c6ba825e782f8dfc18e20f6a9e2185306dd34a037e7a11add90ec50d` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/native-build-identity.json` | `1d4e454ad5be299d3bb70d285a6c8619fafd6f98dc13e126fb894da2eb721b52` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/runs.json` | `409a12034ac84bcb64697dc67b08d3bd2098a2f2544f43dc546d87eff04bf0f3` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/case-ledger.json` | `cf4031ab858c2cfef1a6630bc3143bec0009ac0b84f1b94681ccc0860f7a5e4c` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/source-build-state-checks.json` | `d3b4739955e9a78e3abf34e074dbd54c58b09c51402ae98d58602ed5677abad0` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/provider-request.json` | `932e414cf09f5eab960c1aeb29d4f25c23a2acb4c46094d10dc96a173cfc6c1c` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/coverage-mcp-comparison.json` | `19fd73ae084b8c657699f7536e48522c3a80833419a30a0a02fe4d00b082039e` |
| `parity-results/coverage/response-field-traversal-normal/9c29938-first/comparison-hints.json` | `4ebed2b1bf1e77c1511da78342c70a3001c1796d032fe525fab1a1cd7d59bedb` |
| `parity-results/coverage/response-field-traversal-fault/9c29938-first/initial-source-build-snapshot.json` | `7eef71a88420c740f8fe87e959b9f22168e462cd7de2de5af605b8d7783f7ddb` |
| `parity-results/coverage/response-field-traversal-fault/9c29938-first/build-configuration.json` | `0e68e6690f7b2ae14c4e283352f3a541f55d382884e7ab73cacfbe46f0a69fe0` |
| `parity-results/coverage/response-field-traversal-fault/9c29938-first/runs.json` | `474643eaf1246862085f127f201fd5e326cabb6dd99d101d267aa171525dfc5f` |
| `parity-results/coverage/response-field-traversal-fault/9c29938-first/case-ledger.json` | `af5f231d13e1f02c1fbd225ed6ba582d1cc0bbf1a9a537660e283bfcfe7ad0e8` |
| `parity-results/coverage/response-field-traversal-fault/9c29938-first/source-build-state-checks.json` | `919d9f22706ef03bcc0e1747066ed2f0eb503b1c9c56026f8bafca543781aeb3` |
| `parity-results/coverage/response-field-traversal-fault/9c29938-first/native-build-identity-after-close.json` | `f036e00fb86f9d86d462d2c9be43ed0be2206b5418791cadc6acff7aa324ef48` |
| `parity-results/response-field-traversal-normal-instrumented-build.log` | `c98f5372d05d748c66b35a8f6a5293fa9b04dc694a8393389f327af503f3d81c` |
| `parity-results/response-field-traversal-normal-instrumented-pre-build.json` | `348c8c11b0135f5df7af05bd112d1cffd8fbea56af4805a2a5adb9bf37b0fa96` |
| `parity-results/response-field-traversal-fault-instrumented-build.log` | `ad159b2b267eccd6246293320ed6e112ebd5f4a7257679d8a3a62be2cf27ec08` |
| `parity-results/response-field-traversal-normal-restored-build.log` | `ec978d64ce504267b4b7c8121f73bde2be48da924da3a2de3cb5a4aac62b8d67` |
| `parity-results/response-field-traversal-normal-restore-snapshot.json` | `9fa398a5e4d93789f1e7a489ae0c12cf8cd78caa27a1f74103d607b4cf6a9273` |
| `parity-results/response-field-traversal-restored-runtime-boundary.log` | `78ea5bb704ab2030594c429e06018859ca38348d340840032afea101dfedf167` |

## Remaining boundaries

Observed reachability and passing selected contracts do not prove arbitrary FastAPI compatibility, private adapter identity, unrestricted mutable model/route histories, additional fields, concurrent/reentrant construction, warning-filter concurrency, streaming or unselected reflection/protocol branches. Generic Starlette behavior remains sibling-owned; no sibling region is credited. Source/build freezes bind only these receipts. Later sources/inputs/binaries require fresh checks. Temporary orchestrators are outside Git source hashing, so preserved helper hashes are required for reproduction. No benchmark claim follows from this audit.
