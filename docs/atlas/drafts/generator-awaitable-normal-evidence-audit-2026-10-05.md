# Generator awaitable normal evidence audit

Independent read-only audit on 2026-10-05. This note is the only file written by
the reviewer. No app execution, comparator rerun, build, install, repository edit,
or current instrumented-binary comparison was performed.

## Scope and result

**Bounded clearance: 38 complete indexed workflows, 175 selected / 175 passed,
0 failed / 0 not_run.** This is the selected normal regression set, not the whole
project corpus or complete Python await-protocol coverage.

Receipts: `/Users/lazytrot/work/fastapi-rs/parity-results/generator-awaitable-wave/final-normal/normal-runs.json`.
Generator comparison: `parity-results/comparisons/3800d1cf-fe62-447e-94a3-91f1ffe355e2.json`.

- Checked all 114 normal source, target, and comparison artifacts plus the three
  artifacts in the valid pre-adapter diagnostic. Every reference resolves to its
  recorded run ID, product, and byte SHA256; comparisons bind the actual source
  and target result files. All artifacts completed without infrastructure errors.
- Input, workload, recipe, manifest, and materialized-index hashes agree. Case
  order/cardinality matches each complete input in source, target, comparison,
  index, and case-contract rows. Commands contain no case-filter/skip flags;
  all 175 cases use the parity lane. No expected-output or golden-result keys
  occur in these workflows.
- Every normal source/target case record is canonically JSON-identical, including
  scalar types. All planned actions/probes and observation kinds/indices occur in
  order: **384 actions and 15 direct API probes per implementation**. No step was
  skipped or marked not_run. Six construction-error outcomes per implementation
  were explicitly observed and matched; no normal product-error case was hidden.
- Generator input includes all **15 cases / 47 actions / 21 public state
  snapshots**. HTTP status, ordered headers, body bytes, and ordered send types
  are retained. State bodies preserve the complete captured warning journal and
  lossless raw-send projection, including field presence. The workload records
  every captured warning; no warning-category/message output filter was added.
  The exact comparator reads live result observations, not expected outputs;
  canonical raw-record equality also makes normalization unnecessary here.

## Frozen normal identity

Oracle records agree on FastAPI 0.141.1 (`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`),
Starlette 1.6.0 (`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`), CPython 3.12.13,
Pydantic 2.13.4 / core 2.46.4, and AnyIO 4.12.1. Target records contain native
FastAPI-RS and Starlette-RS distributions without original FastAPI/Starlette
runtime distributions, with explicit sibling checkout b4c8a65.

| Binding | Recorded normal value |
| --- | --- |
| FastAPI-RS revision | `4b4a18c13d1f201f8aa4d406c9b3535998ef3dd6` |
| Starlette-RS revision | `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8` |
| Combined source SHA256 | `da7d0dc2e2c42b94152a49d373887b3a3f9ae53c3010bcf92569ec906d1b492c` |
| Combined native SHA256 | `3a119e2a97afe041e7c43f2912c0ee763c77cd20b1054c32aba8f6a57c80c95d` |
| Generator input SHA256 | `ba021904c37edbdd0e5561de821813b8cbddb9f3ed5cbc42510a54a3ca0bbe65` |
| Generator workload SHA256 | `41f6ad6e99746620627947d93a71f8390857ccf6b0e5ba8f5f8b151c3daff356` |
| Manifest SHA256 | `144ee428ae0e52e8799fe9b799d114b82429df67bdc179c31571e97ae68e3d07` |

Initial/final normal snapshots are identical, including every input and native
component hash. Independently recombined component hashes match both combined
digests, and every normal target artifact records those same bindings. The three
newer result contracts explicitly record fault-injection compiled=false; 35
legacy contracts omit that field but bind the same normal native pair. The worker
identity code hashes the compiled extensions actually imported into each target
process. Current instrumented binaries were deliberately not read or equated to
this normal pair.

## Preserved pre-change diagnostic

`pre-adapter-wrapper-cleared/normal-runs.json` binds comparison
`727f1ab3-4d80-4418-80d6-1bfa65900947`: **15 selected / 5 passed / 10 failed /
0 not_run**, comparison exit 1, source and target process exit 0. All ten failures
have retained diffs. It uses the same generator recipe/input/workload/manifest
and complete case/action order; its source case records are identical to the
final source records. Its separate c4f829c target/source/binary snapshots are
stable within that run and were not treated as current-build coverage evidence.
The earlier `pre-adapter` launch has target exit 2 from sccache permission failure
and no comparison; it is preserved and excluded from parity success claims.

No blocker found in this receipt set. Audit hooks/gi_code, generic iterator throw
arity and coroutine-wrapper provenance, type-slot lookup, reuse/cancellation,
mutable history, exact frame/type-name behavior, and other unselected protocols
remain outside this clearance. Instrumented same-source coverage is a separate
pending evidence lane and must retain its own binary/build identity.
