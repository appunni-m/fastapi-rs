# Independent audit: declared-response-key benchmark seven

## Conclusion

The closed suite is internally coherent within the declared direct-ASGI scope.
The offline checker completed 1,382 checks without a failed check and binds
91 saved artifacts/source-text files. No application, installed extension or
native binary was loaded or rehashed; no parity or benchmark was rerun.

Suite: `benchmark-results/suite-20261005T155905Z-1835834f-5295-4952-bde3-cfd742f6f608.json`.
SHA256: `218fd439c0f30b1043203ff9994779f812aacece51db816d0333936feef4b24f`.
All seven required workload IDs occur exactly once and completed. The saved
suite log records completion; its preflight records clean source checkouts.
The machine receipt retains all seven result/comparison references, fourteen
isolated product results, input/declaration/recipe/workload hashes and run IDs.

## Fresh gate scope

The seven fresh full-input comparisons pass 42 case executions per product,
covering 16 distinct case IDs in four unique workflows. Each product completes
56 HTTP actions, 24 distinct case/action pairs, 96 action observations and four
selected successful construction observations. There are no case/action
filters or injected fault cases. The observations comprise 56 HTTP projections,
36 ordered ASGI message-type projections and four structural OpenAPI projections.
HTTP selectors cover 56 status, 55 body and 37 ordered-header observations.

Warning capture is unselected at every construction/action/timing phase.
Absent warning fields do not prove that no warnings were emitted. Older @2
workflows do not select construction observations; successful completed actions
are their available evidence. The two @3 nested workflows select the four
construction observations across their two repeated gates.

All selected typed values and list order match. One untimed repeated-query
OpenAPI projection has inline schema key order `type, items, title` in the
source and `items, type, title` in the target. That action selects status and a
structural whole-document projection; its raw document bytes are unselected.
This is a bounded gate limitation, not a timed-response mismatch. All seven
timed response signatures agree across source/target and the two applicable
controls, including exact status, ordered header bytes and body bytes. Each
signature also matches the selectors available in its saved parity action.

## Raw statistics

All 16 subjects retain 1,000 positive integer samples, 50 warmups and one
untimed baseline call: 16,000 raw samples, 800 warmups and 16 baselines. Each
subject declares five rounds of 200 requests at concurrency one. Six even-size
raw medians have a half-nanosecond fraction; stored medians correctly truncate
with `int(statistics.median(samples))`.

Every stored min, truncated median, p95, p99, max and arithmetic mean was
recomputed exactly. Percentile indexes follow the producer:
`round((n - 1) * percentile / 100)`. Each request-loop throughput equals
`n * 1e9 / request_loop_elapsed_ns`; all fourteen median/p95 ratios match the
recomputed target/source values exactly. Full statistics are in `audit.json`.

| Workload | Source median ns | Target median ns | Target/source median | Target/source p95 | Starlette control median ns |
|---|---:|---:|---:|---:|---:|
| Nested distinct aliases | 517,209 | 326,208 | 0.630708 | 0.656716 | — |
| Nested two queries | 437,625 | 288,437 | 0.659096 | 0.643856 | — |
| Chunked body | 134,645 | 142,208 | 1.056170 | 1.136926 | 5125 |
| Invalid request | 150,083 | 338,792 | 2.257364 | 1.751846 | — |
| Valid request | 135,395 | 139,917 | 1.033399 | 1.032920 | 4917 |
| Large response model | 373,187 | 404,083 | 1.082790 | 0.763327 | — |
| Repeated sequence query | 98,312 | 126,271 | 1.284391 | 1.872922 | — |

The target is faster in two selected workloads and slower in five. These
single-machine measurements establish no general speedup. The two Starlette
controls return fixed valid JSON without equivalent request parsing,
validation, dependency or response-model work; they are contextual and must
not be subtracted from either subject.

## Identity and boundary

The seven results, timed subjects, saved parity results and suite embeddings
bind the same commits and pinned packages: FastAPI 0.141.1, Starlette 1.6.0,
CPython 3.12.13, Pydantic 2.13.4/core 2.46.4 and sibling commit
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Shared packages match the manifest.
All subjects report macOS 15.7.7 / arm64 / 12 CPUs; the target metadata reports
release with `pyo3/extension-module`, Rust/Cargo 1.98.1. Saved oracle/target
commands use the separate `.venv-oracle`/`.venv-target` workers and exact input,
workload, manifest and source-root arguments. Gate timestamps precede timing;
workloads and subjects are sequential. Timed worker PIDs, complete argv and
complete inherited OS environment are not retained in the timing JSON; their
process/configuration boundary is supported by producer source and saved
identity/count records, not an extra process trace.

Native revision: `d50887853d382bd9d9e03c7e82a504614ff02aba`.
Combined source: `d1299254a34d2c31b0a8ed1b676825a85b749421aa27a9e8084e5c6afecbf8f7`.
Core: `05fd14200682372037e867108b52f6f44993fb39961fdac03ed626f45b26a3e3`.
Sibling: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.
Pair: `e1b2a3599081a307941e07b2a00f71edf9cf55d2d00f9185f48416843722086e`.

Pre/post snapshots are byte-identical, SHA256
`af5dd3202384411be03cadff1cffd5d7e15c983db7df532958cc856a03839bbd`,
including source text, policy, per-extension and pair hashes. The earlier saved
isolated restoration proof reports `fault_injection_compiled=false`, the exact
installed core path and these release bytes; it agrees with both snapshots.
Manifest/index/metadata hashes agree with every linked saved gate and the
current frozen text. This audit does not reopen separate coverage/fault lanes.

The producer times only `await app(scope, receive, send)` after app construction
and warmup. Scope/callback preparation and response signature/check bookkeeping
are excluded from per-request latency but included in sequential-loop
throughput. Public Python facade, PyO3 conversion, Rust/Pydantic and ASGI response
work are included as exercised. There is no network/server/startup/OpenAPI
latency measurement or isolated native/FFI cost; the OpenAPI actions occur only
in correctness gates. No replicated-process or full-suite performance claim is
supported.

## Frozen local evidence

- `audit.json`: full bindings, counts, per-subject recomputations and limits.
- `audit_saved_suite.py`: offline saved-file checker; imports only parser/schema
  dependencies, never products or user workloads.

Machine receipt SHA256: `29479fd028cd2e197a48b7cc0475a059b6cd1f4bae07eb4626e82e144775d163`.
