# OpenAPI validation-response fault coverage and restoration audit

Status: closed, clear within the selected fault lane. Bulk checks ran only after
the parent closed benchmark timings. No concrete receipt or restoration issue
was found.

## Closed selection and actual outcomes

Only `parity-results/coverage/openapi-validation-response-fault/d508878-first/`
and closed measurement receipts are in scope. No product import/execution,
installed native read, builder, LLVM tool or parity rerun was performed by this
auditor. TMP-only audit routines consume recorded artifact data.

| Selection | Ordinary cases | Target-only contracts | Source actions | Target actions | Passed comparisons | Covered regions |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 0 | 2 | 0 | 4 | 2 | 8726 |
| previous | 7 | 1 | 24 | 26 | 8 | 10729 |
| records | 17 | 1 | 41 | 43 | 18 | 11314 |
| dynamic | 13 | 1 | 50 | 52 | 14 | 12996 |
| batch | 18 | 1 | 34 | 36 | 19 | 10580 |
| Total | 55 | 6 | 149 | 161 | 61 | workflow coverage, not a sum |

All applicable constructors are `ok`; all actual actions are completed. The six
source contract records are deliberately `not_applicable`, with no actions:
`target-only injected fault; the reference must not execute it`. They are not
source failures or parity skips. All 15 source/target/comparison artifact digests,
run IDs and ordered case inventories match `runs.json`. The baseline uses its
reviewed schema8; the other four workflows use schema9.

Manifest, input and workload hashes agree with the actual source/target headers,
comparison references and frozen index. The complete ordered case ledger and
requirement refs reconstruct from those actual records. All input/recipe/workload
bindings remain byte-matched. This is recorded provenance, not new expected data.

The six target contracts retain exact `builtins.RuntimeError` messages, the
selected response-start/body sequence and status500 followed by recovery200.
Five additionally select the public `dependency-enter`/`dependency-cleanup`
journal. This verifies those declared error/recovery/cleanup observations;
internal adapter/cache state and broader cleanup protocols are not selected.

## Fixed source and isolated build

All 36 distinct ordered checks are true: seven checks for each of five
workflows, followed by `all-selections-complete`. The build log and pre-build
receipt hashes match their configuration references. The configuration build
ID independently recomputes as:

`fastapi-rs-instrumented-sha256:c149ba0974e45ed0b1be8c676f8c0caa704cb231c16bb3660be32235385114d4`.

- Revision: `d50887853d382bd9d9e03c7e82a504614ff02aba`.
- Combined source: `d1299254a34d2c31b0a8ed1b676825a85b749421aa27a9e8084e5c6afecbf8f7`.
- Isolated fault export/module: `1332f8301eb4c8e63382ecaed7f197f7a25c5385d98048f972b836403f1a7100`.
- Fault runtime pair: `572d47c50b3593685900d01a7952c12229b910caf3bd1a726d752e5e9988c92b`.
- Sibling module: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.

The recorded command uses the pinned sibling and fault venv. Features are
`pyo3/extension-module` plus `fastapi-rs-py/fault-injection`, forwarded to the
core; flags are `-C instrument-coverage`, with incremental compilation disabled
and `RUSTC_WRAPPER` cleared. The closed module proof records native flag `true`
at `target/fault-injection/python/fastapi_rs/_core.abi3.so`. Every target result
binds the same revision/source/pair and flag. Oracle identity remains the pinned
FastAPI0.141.1/Starlette1.6.0/CPython3.12.13/Pydantic2.13.4/core2.46.4 profile.

All five raw LLVM exports reconstruct exactly to their retained filtered JSON:
only native-file/function path canonicalization, the declared Rust scope filter
and recomputed file-summary totals are applied. Report/context hashes, complete
profile inventories and profile byte hashes match. Each workflow has its own
nonempty profile and merged profile; all five export stderr files are empty.
The filter retains every other LLVM value. LLVM merge/export commands were
reviewed as receipts and were not re-executed. The fault runner remains
`4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5`.

## Provider request and attribution

The saved actual MCP request uses this lane's baseline, three fresh previous
reports (`previous`, `records`, `dynamic`) and `batch`, metric `regions`, scope
`incremental`. The provider accepts verified eight newly covered regions:
13869→13877 of32805, with four gained function groups. No normal report or
historical revision is included. The provider explicitly reports
`regression_checked=false`.

Coverage is attributed to each selected workflow's profiles. Case-ledger
entries identify input/requirement/result provenance, not individual case region
ownership. This selected union is not full-matrix coverage or regression proof.

## Preservation and exact restoration

All source trees, Rust-source maps and policy hashes agree across the initial
snapshot, fault pre-build, backups, fault-built proof and restoration receipts.
The normal instrumented module `f38d0ae4f2f74b81bfb094909f1b02e0aab4899e2bc049cde3bdc52271dbc8fe`
was retained during the isolated fault build, with flag `false`. That is distinct
from the release backup subsequently restored.

The closed restoration records installed/export hashes equal to the release
backup `05fd14200682372037e867108b52f6f44993fb39961fdac03ed626f45b26a3e3`,
unchanged sibling hash above, `exact_release_restoration=true`, and normal native
flag `false` at the consumer module path. Direct identity was captured by the
parent's completed proof process; this auditor does not repeat it or infer an
instrumentation profile from the feature flag alone.

All three archived backup byte hashes were independently recomputed and agree
with their backup/restoration bindings. The restored installed/export/core paths
and isolated fault path agree with the proof records. The parent restoration log
records restored=true and the unchanged source digest; the restored boundary log
confirms upstream FastAPI absence and the direct native facade. The isolated
identity proof includes the recorded sibling WSGI deprecation warning, with
parent-reported exit0. No current installed/export/sibling native file was read
by this auditor.

## Frozen independent check artifacts

- `/private/tmp/fastapi-rs-validation-response-fault-closed-receipt-audit.json`:
  `6a06524160747e478c4de80631c2ce037623af294e02260bb3378d1f3488cd43`.
- `/private/tmp/fastapi-rs-validation-response-fault-export-restoration-audit.json`:
  `2cf0b2f439f250bdf4712206a8bd78b54ffcf141c46fe38e48ac57501d4e66da`.
- `/private/tmp/fastapi-rs-validation-response-fault-header-audit.json`:
  `029cc290b6f2ad00ba12ef4330263e40557c8c71e22371051df90ec9e760497a`.

The corresponding data-only checker hashes are `82d1c42c46f64ec04f3f15256f755c3382485073745d745dfb1395a9a88bcded`
and `29f18381bd79a8a5432327713479e14d0751409939efd6ca6dad222ac1104d24`.
Parent restoration/boundary exit0 remains recorded proof, not an auditor run.
