# Independent closed benchmark7 evidence audit

Date: 2026-10-05. Reviewer: `override_reanalysis` (Sol).
Scope: read-only saved JSON/YAML/log/runner-source inspection and pure-data
recomputation. No product import, app execution, parity replay, native file read,
build/install, unit framework, tracked-file edit or archive move was performed.
Parent reported the suite process CLOSED with exit0. The saved completion log
contains completed/7 and the exact suite path below. Current final static-check
logs were not read while live.

## Closed denominator and fresh gates

Suite: `benchmark-results/suite-20261005T145041Z-7ec4051b-63b7-499d-b175-5203358c2aa4.json`.
Run ID: `7ec4051b-63b7-499d-b175-5203358c2aa4`.
SHA256: `b6a16a67ecec978780eebd662251ad27b00c8e407ed3a702f71f50dd006f399d`.
Schema: benchmark-suite-result@2, completed, failure=None.
Completion log SHA256: `4385e4168b2e016c8bdcf3d7c2bc3de64962d04abb63cc2459fa17e99237462f`.

The declared seven workload IDs and order exactly match the suite, current
seven workload YAML filenames, saved workload/input hashes and current schema.
Each result digest/run ID/identity/gate agrees with its suite entry. All seven
fresh comparison hashes and their source/target result hashes/run IDs resolve.
Every comparison has completed status, no infrastructure errors, no failed or
not_run case, and the frozen manifest digest
`eba84432c34ad05b8b0613d2d9a285443d100357d189bd7583c935cac9758859`. All source/target case/action IDs and ordering match
the full selected input. Actual constructions are ok wherever schema3 selects
construction; older schema2 results have no constructor observation to claim.
Every selected action is completed.

Fresh gates are **42 passing case comparisons and 56 completed actions per
product across seven runs**. The two async benchmarks each rerun both cases/eight
actions; three first-slice benchmarks each rerun all 12 cases/actions; large
response reruns one case/action; repeated query reruns one case/three actions.
These are 16 unique case IDs/24 unique case-action pairs across four workflow
inputs. They are neither seven single-case comparisons nor a full corpus gate.
There are seven saved oracle/target pairs, with 14 isolated parity worker commands.
For each measured action, saved untimed status/body and selected ordered headers
match its completed parity action; untimed signatures also agree between all
subjects. Async query parity inputs select status/body only; their measured
untimed signatures additionally include equal headers. Header equality from
those signatures is not reattributed to a missing parity selector.

| Workload | Source median ns | Target median ns | Target/source median | Target/source p95 | Gate passed/selected | Actions per product |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fastapi.async-nested-distinct-query-aliases.asgi | 511771 | 321875 | 0.628943414 | 0.647695839 | 2 / 2 | 8 |
| fastapi.async-nested-two-query.asgi | 420458 | 281521 | 0.669557958 | 0.688815375 | 2 / 2 | 8 |
| fastapi.first-slice.chunked-body-asgi | 136917 | 146292 | 1.068472140 | 1.116503956 | 12 / 12 | 12 |
| fastapi.first-slice.invalid-asgi | 147771 | 325833 | 2.204986093 | 1.664371986 | 12 / 12 | 12 |
| fastapi.first-slice.valid-asgi | 134625 | 139834 | 1.038692665 | 1.073281554 | 12 / 12 | 12 |
| fastapi.large-response-model.asgi | 370895 | 396875 | 1.070046779 | 1.084854444 | 1 / 1 | 1 |
| fastapi.request.repeated-sequence-query.asgi | 103042 | 116208 | 1.127773141 | 1.191663430 | 1 / 1 | 3 |

The target has lower medians for the two async dependency cases and higher
medians for the other five cases in this run. Invalid-input median is about
2.205 times the source. These ratios are saved target/source per-request ratios,
not inverse speedups, aggregate gains or network throughput claims.

## Every raw sample recomputed

Exactly 16 subject measurements retain 1,000 positive integer nanosecond samples
each: **16,000 saved samples**. Fourteen FastAPI/source-target measurements
account for 14,000 samples; two contextual Starlette controls account for 2,000.
Every subject records 50 excluded warmups and 5 contiguous rounds of 200 samples,
concurrency 1. Total excluded warmups are 800; source code also makes one untimed
correctness baseline per subject (16 calls), whose timings are discarded.
There is no saved warmup latency series to reconstruct or include in the median.

For all 16 subjects, independent pure-data recomputation exactly matches min,
integer-truncated statistics.median, mean, p95 and p99 using the worker's rounded
order-statistic index, plus max. Throughput exactly equals
`1000 * 1e9 / request_loop_elapsed_ns`; the loop elapsed is at least the sum of
per-request latency. Median/p95 ratios exactly equal recomputed target/source
statistics. No raw value is filtered or normalized; per-subject raw-array digests,
full recomputed values and throughput are retained in `audit.json`.
Round grouping is inferred from the saved concatenated sequence/declared count;
no per-request timestamp or separate round timing is serialized.

| Workload | Subject | Min ns | Median ns | p95 ns | p99 ns | Max ns | Mean ns |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fastapi.async-nested-distinct-query-aliases.asgi | fastapi | 501875 | 511771 | 522750 | 531250 | 598375 | 513402.034 |
| fastapi.async-nested-distinct-query-aliases.asgi | fastapi-rs | 311167 | 321875 | 338583 | 378125 | 640583 | 325130.536 |
| fastapi.async-nested-two-query.asgi | fastapi | 404541 | 420458 | 437708 | 451167 | 496292 | 422661.449 |
| fastapi.async-nested-two-query.asgi | fastapi-rs | 267291 | 281521 | 301500 | 319708 | 614167 | 284612.887 |
| fastapi.first-slice.chunked-body-asgi | fastapi | 132333 | 136917 | 151291 | 172667 | 237625 | 139218.610 |
| fastapi.first-slice.chunked-body-asgi | fastapi-rs | 136875 | 146292 | 168917 | 192666 | 448583 | 149721.988 |
| fastapi.first-slice.chunked-body-asgi | starlette-control | 4917 | 5083 | 5333 | 6458 | 6916 | 5135.380 |
| fastapi.first-slice.invalid-asgi | fastapi | 140708 | 147771 | 217750 | 235250 | 5900458 | 162141.585 |
| fastapi.first-slice.invalid-asgi | fastapi-rs | 309208 | 325833 | 362417 | 396792 | 433584 | 330476.635 |
| fastapi.first-slice.valid-asgi | fastapi | 125542 | 134625 | 152958 | 172000 | 221375 | 136984.201 |
| fastapi.first-slice.valid-asgi | fastapi-rs | 128875 | 139834 | 164167 | 193167 | 491792 | 143740.424 |
| fastapi.first-slice.valid-asgi | starlette-control | 4875 | 5125 | 5250 | 6292 | 6917 | 5138.872 |
| fastapi.large-response-model.asgi | fastapi | 351459 | 370895 | 399708 | 430417 | 539125 | 374582.508 |
| fastapi.large-response-model.asgi | fastapi-rs | 378208 | 396875 | 433625 | 477500 | 6329375 | 407927.829 |
| fastapi.request.repeated-sequence-query.asgi | fastapi | 95250 | 103042 | 115875 | 137959 | 175917 | 104801.203 |
| fastapi.request.repeated-sequence-query.asgi | fastapi-rs | 107250 | 116208 | 138084 | 148667 | 473958 | 119247.656 |

## Process, environment and boundary

All saved subjects identify CPython 3.12.13 on macOS 15.7.7/arm64, arm processor,
12 CPUs. Hosts, shared package/version maps and FastAPI/Starlette source pins
are equal across every result and the suite identity. Pydantic 2.13.4,
pydantic-core 2.46.4 and the other shared packages match the manifest. FastAPI
is 0.141.1; Starlette is 1.6.0. Target release records Cargo/rustc 1.98.1 and
pyo3/extension-module, equal across results. These are recorded build fields,
not an independently reconstructed compiler invocation.

Static runner evidence: `scripts/benchmarks/run_first_slice.py:170-213` launches
one subprocess per subject, selecting `.venv-oracle/bin/python` for source and
controls, `.venv-target/bin/python` for target. Saved parity argv likewise use
those separate environments and the immutable sibling path. Worker identity
checks native-extension existence/provenance, source pins, Python/shared package
versions and absence of the original FastAPI distribution in target. The saved
timed measurements retain identities/host but no PID, argv, full OS environment,
CPU affinity/frequency/load or scheduler telemetry; those are not proven by the
JSON alone. Saved subject timestamps follow parity completion, consistent with
the source-ordered gate-before-measurement pipeline.

At `worker.py:270-317`, per-request timing starts immediately before
`await app(scope, receive, send)` and stops on return. It includes FastAPI ASGI
behavior and target facade/PyO3/native conversion; send capture runs within that
call. Scope and receive/send construction, response-signature extraction,
correctness checks and loop bookkeeping are outside per-request latency but
inside the separate request-loop throughput. Startup/import, app registration,
HTTP server/client and network are excluded. No standalone Rust-only cost,
facade/FFI subtraction, cancellation/server concurrency or OpenAPI generation
performance is measured by these seven request actions. Samples from one
process per subject are not independent process-level replications or reported
confidence intervals; there is no cross-machine result here.

The two Starlette controls occur only in chunked/valid item workloads. At
`worker.py:118-136`, the control returns a fixed JSONResponse without FastAPI
input/dependency validation or body consumption. Its median values 5,083 and
5,125 ns are context, despite equal output signatures. They are not equivalent
replacement implementations, part of target/source ratios, or subtractable
FastAPI overhead. Declarations explicitly retain contextual/no-subtraction
reporting. No control is inserted into the invalid or dependency workloads.

## Frozen source and normal native identity

Pre/post snapshot files are **byte-identical**, including all source/policy hash
maps, repository revisions and both native-file digest entries. They equal the
restored normal proof's source map; no fresh native import/hash was performed by
this reviewer. All seven target parity identities and timed target identities
match the same frozen pair and target revision. The restored proof identifies
the installed native path, equal installed/export release bytes and
fault_injection_compiled=False before the suite.

| Boundary | Value |
| --- | --- |
| FastAPI-RS revision | 62dacc5283a0cee282258e268f7545765679e974 |
| Combined source digest | 503211630df8f7e2bf624c55c217d08444658252311bff19bf6568b4736a4c0f |
| FastAPI native digest | d934ba09884e6c8a657300c4800a92e76577285f2bf5833e73418d21912b6140 |
| Starlette-RS native digest | fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5 |
| Combined native digest | e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0 |
| Starlette-RS source revision | b4c8a65c85e1b0d251ca05874412811eaa3ac7b8 |

| Closed proof artifact | SHA256 |
| --- | --- |
| benchmark-results/openapi-final-model-62dacc5-pre-suite-snapshot.json | 21a4a9969d5f323f918f03f6c7c3437f92ff449574a767a1105c63d9564fcdc0 |
| benchmark-results/openapi-final-model-62dacc5-post-suite-snapshot.json | 21a4a9969d5f323f918f03f6c7c3437f92ff449574a767a1105c63d9564fcdc0 |
| parity-results/next-openapi-response-field-wave/measurement-receipts/normal-restored-native-proof.json | 1dc8a6927c1152153653c98b1599534b19667d0f13f60ad7822925f18f820f74 |

This is normal-release measurement evidence. Instrumented normal coverage and
the separate fault lane are different native binaries and denominators; they
are not unioned with benchmarks. The unmodified b4c8a65 BackgroundTasks worker
crossing gap remains outside these selected actions.

## Historical suite preservation

Actual relocation receipt:
`benchmark-results/archive/827612f-before-openapi-final-model/relocation-receipt.json`,
SHA256 `e9e8422e0a1a21599a9fcac56bb624204748570043b1ebd5b05563c3ca0dcf14`.
The archived suite at `benchmark-results/archive/827612f-before-openapi-final-model/suite-20261005T121923Z-250a48d8-8719-4737-82bb-de7a71841c51.json` has unchanged SHA256
`b71c0a5db8ae410ff7a73ae5ff36571428f3ed6a3cd150f247e296cff809cc8e` before/after. Its prior root path is
absent; the sole current root suite is the fresh suite above. It remains a
completed 827612f historical result bound to manifest ae88fc58, with its original
identities and ordered seven entries unchanged. It is not current 62dacc5 evidence.

The preservation plan digest b42741eb matches the receipt. All seven original
benchmark artifact paths/digests, seven comparison paths/digests and 14 transitive
source/target result paths/digests still resolve unchanged. Prior suite log and
post-suite snapshot hashes also match the relocation receipt. No references
were rewritten, parser/schema/comparator/global current-manifest guard changed,
or archived output removed. The ledger preserves the old/current manifest
relationship rather than relabeling old measurements under a new manifest.
The fresh suite independently has current-manifest gates at every workload.

## Result binding

Full JSON audit: `audit.json`, SHA256
`d870db8d7f65884f519e199b9cdc46cd8400c22a95d5003f8dbb48dc23ba814d`.
All bounded checks passed; no measurement/admission blocker found. Parent owns
final static closure, archival of this note and future 422 admission. The four
prospective automatic-validation-response cases have not been measured by this
suite and remain a separate source-first gate. Historical failed final-model
runs, normal 206/public 4 receipts and coverage/fault evidence are not overwritten
or broadened by this audit.

| Workload result | Actual path | SHA256 |
| --- | --- | --- |
| fastapi.async-nested-distinct-query-aliases.asgi | benchmark-results/20261005T144339Z-b911f8fe-0c0e-4b7c-aed3-a1ec3dbfb01b.json | 13700c3f0b33ba10d4e5b86bfa9881b8db047a9eaf4d85dc278322221cbddee9 |
| fastapi.async-nested-two-query.asgi | benchmark-results/20261005T144450Z-7c6f63ed-9d5c-4bd6-ba7e-cbbf662be4bf.json | b6adf99c663f0a51cf7da900fa52a96a7f6b26ebf6176621b017243ea58b3ce7 |
| fastapi.first-slice.chunked-body-asgi | benchmark-results/20261005T144600Z-dc0f6c81-b245-42de-9fdf-3a323dbf7a18.json | b206db86c835d8654cf41048bd3ee56b3ab30b3119a13fbd9a955d11363f7dae |
| fastapi.first-slice.invalid-asgi | benchmark-results/20261005T144709Z-674350ac-95b0-4660-b3e4-0de3426792cb.json | 2cbec988eaa29ac773a9617c4dbe4372addb30b70a1687d63d8657316955b629 |
| fastapi.first-slice.valid-asgi | benchmark-results/20261005T144821Z-a6cfe9c6-f92e-456f-8c69-0f6a996cbc91.json | 21fbe727b40c029c10d0b21bf434ec7b1031fa1e239461adb1e79eb9a82f6460 |
| fastapi.large-response-model.asgi | benchmark-results/20261005T144932Z-52a70096-dca1-4d7a-ba3c-f8c8b35fab4d.json | 4857cf52cd2fa883ba7e031e5348a59364a6ae516239a025a84afc796dc50c79 |
| fastapi.request.repeated-sequence-query.asgi | benchmark-results/20261005T145041Z-c7284136-c055-4ba2-9d19-aa2b0a788a8e.json | d68abe4ba335d67dfa8719cc1c574fc2ac3ef131bce5b3aa9d31729c7b7bbe3e |
