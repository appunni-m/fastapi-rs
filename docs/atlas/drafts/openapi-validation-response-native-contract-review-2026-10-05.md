# Declared response keys and automatic validation responses

Measured native revision: `d50887853d382bd9d9e03c7e82a504614ff02aba`.
FastAPI 0.141.1 / Starlette 1.6.0 remain the source oracle; the sibling remains
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. This is a selected compatibility
checkpoint, not full API parity or release readiness.

## Rust correction

Rust retains original additional-response keys through field construction,
canonicalizes them during OpenAPI generation, merges declared responses first,
and checks actual merged 422/4XX/default keys before inserting automatic 422.
The Python facade, dependency pins, restricted description/model policy and
comparator are unchanged. Metadata and source classifications are not promoted.

## Live gates

| Gate | Declared outcome |
|---|---|
| Four new cases | 4 pass; both lanes 4 constructors, 24 HTTP actions, 80 action observations |
| Whole regression selection | 45 workflows / 210 pass; 547 ASGI actions (542 HTTP, 5 WebSocket), 15 API probes |
| Separate direct OpenAPI API controls | 2 workflows / 4 pass; 4 probes, 5 observations |
| Distinct normal total | 214 cases; targeted four repeat whole cases |
| Separate fault lane | 55 ordinary controls + 6 target-only contracts pass |

All eight new document bodies, ordered typed observations and final lossless
send journals agree. All 28 selected warning phases are empty in both lanes.
The previous oracle observations are unchanged. Whole selection includes 100
construction observations: 93 success and seven matching ordinary public errors.
Its 997 step observations and direct controls are selected evidence only.

The preserved PRE gate failed all four cases; two target constructor errors
blocked twelve actions. Three later sccache bootstrap failures produced source
receipts but no target/comparison artifacts. Corrected runs clear the wrapper;
those attempts remain infrastructure failures, not product or fault outcomes.

A legacy structural selector still permits eleven Schema dictionary key-order
differences in one case. No other selected type/value/list differences were
found. Direct API structural gates do not establish universal HTTP-byte or
warning parity. General response deep merge, callback histories, modeled ranges,
empty parameter models and schema-name collisions remain separate gaps.

## Managed coverage and restoration

Normal: ten fresh workflows, 93 ordinary cases, 291 HTTP actions and 71 matching
fixed-state checks. Coverage MCP verified 42 additional native Rust regions:
15096 to 15138 of 32605, against this build's baseline/eight previous batches.
All ten raw LLVM reports reconstruct exactly to their published native-only
reports. There are 690 step observations per product and 71 construction
observations: 70 successes plus one matching ordinary error. These counts are
independent of the larger behavioral gate.
Fault: five fresh workflows, 55 ordinary controls/149 source actions and six
intentional source-N/A contracts; target 61 cases/161 actions, 36 fixed checks.
Its separately verified increment is eight regions, 13869 to 13877 of 32805.
These are distinct builds and unions; workflow profiles do not attribute regions
to individual cases or establish full-suite coverage regressions.

Measured combined source tree is
`d1299254a34d2c31b0a8ed1b676825a85b749421aa27a9e8084e5c6afecbf8f7`.
Exact release restoration returns core
`05fd14200682372037e867108b52f6f44993fb39961fdac03ed626f45b26a3e3`
and sibling `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`,
pair `e1b2a3599081a307941e07b2a00f71edf9cf55d2d00f9185f48416843722086e`.
Actual isolated native import paths/feature flags and per-file byte restoration
are checked in the measurement receipts. During the private fault build, the
normal instrumented core `f38d0ae4f2f74b81bfb094909f1b02e0aab4899e2bc049cde3bdc52271dbc8fe`
survived unchanged. It was subsequently replaced by the exact saved release
core `05fd1420…` above; those are separate binary identities.

## Benchmark

Fresh suite: `benchmark-results/suite-20261005T155905Z-1835834f-5295-4952-bde3-cfd742f6f608.json`, SHA256 `218fd439c0f30b1043203ff9994779f812aacece51db816d0333936feef4b24f`.
All seven workloads completed after their own fresh live parity gates.
The same release source/native/policy snapshot was saved before and after.
The gates comprise 42 case executions / 16 distinct case IDs, 56 HTTP
actions, 96 action observations and four selected construction observations
per product. The timed response status, ordered headers and body
signatures agree for every workload. One untimed repeated-query OpenAPI
projection still differs only in schema key order: source `[type,items,title]`
versus target `[items,type,title]`. That older action selects structural document
equality without a raw-body observation, so its gate does not guard wire order.

| Workload | Oracle median µs | Rust target median µs | Target / oracle |
|---|---:|---:|---:|
| Nested distinct aliases | 517.209 | 326.208 | 0.630708 |
| Nested two queries | 437.625 | 288.437 | 0.659096 |
| Chunked body | 134.645 | 142.208 | 1.056170 |
| Invalid request | 150.083 | 338.792 | 2.257364 |
| Valid request | 135.395 | 139.917 | 1.033399 |
| Large response model | 373.187 | 404.083 | 1.082790 |
| Repeated sequence query | 98.312 | 126.271 | 1.284391 |

Medians are independently recalculated as int(statistics.median(raw_ns));
stored half-nanosecond medians truncate. The target is faster in two workloads
and slower in five. These measurements do not establish a global speedup.
Two Starlette controls are contextual, not equivalent validation work or a
quantity to subtract. Their chunked/valid medians are 5.125/4.917 µs.

The boundary is warmed direct ASGI, including Python/native facade costs,
with concurrency one. It excludes network serving, startup and OpenAPI timing;
native/FFI costs are not isolated. Sixteen measured subjects each retain 1000
samples and 50 excluded warmups: 16000 raw samples, 800 warmups, five rounds of
200 samples. Independent recomputation matches every stored minimum, truncated
median, p95, p99, maximum, mean, request-loop throughput and both ratio metrics.
Artifact/hash/pin/snapshot review is closed; raw data and configuration are retained.
Older benchmark input schemas do not select warning capture; this suite makes
no warning-equivalence claim. The producer records platform/toolchain/package
identities, but not CPU affinity, host exclusivity, power state or per-subject PID.

## Evidence

The canonical ignored artifacts remain under
`parity-results/openapi-validation-response-wave/`,
`parity-results/coverage/openapi-validation-response-{normal,fault}/d508878-first/`
and `benchmark-results/`. Failed PRE and bootstrap attempts are preserved.
Independent reviewed notes are retained beside this report:

- [New-case POST audit](proposals/openapi-validation-response/post-evidence-audit-2026-10-05.md).
- [Whole/direct behavioral audit](proposals/openapi-validation-response/normal-evidence-audit-2026-10-05.md).
- [Normal coverage audit](proposals/openapi-validation-response/normal-coverage-audit-2026-10-05.md).
- [Fault/restoration audit](proposals/openapi-validation-response/fault-restoration-audit-2026-10-05.md).
- [Seven-workload benchmark audit](proposals/openapi-validation-response/benchmark-evidence-audit-2026-10-05.md).

These notes bind saved artifact digests, actual run IDs, current input/policy
digests, native identities and measured-source snapshots. Generated results are
not committed or treated as expected outputs.

## Checks and next slice

Strict fmt, Clippy, metadata/API/index/dependency/facade/benchmark contracts and
parity validation passed. No unit framework was added or run. Manifest stays
555 workflows / 2304 input cases with 1582 generated index mappings, all
`coverage_status=partial`, from reviewed source overlays.
The pre-build static log is
`parity-results/openapi-validation-response-native-static-contracts.log`;
normal installed-boundary and exact-restoration checks also returned zero.

Next: admit the independently reviewed two-case/eight-action inline query schema
wire gate, require live source completion, and retain unchanged-target differences
before diagnosing the correction. The existing structural selector stays unchanged.
