# Additional response-field wave: prospective helper audit

2026-10-05. Read-only static review before the additional3 pre-gate closes. No
orchestrator, app, factory, native import, build, installer, parity command or
measurement was executed. Only source text, admitted JSON/index bindings and
code-file hashes were read; this note is the sole new output.

## Reviewed immutable helper identities

| Helper | SHA256 |
| --- | --- |
| `/private/tmp/fastapi-additional-response-field-normal-runner.py` | `66a8867f02eb1ebaa83b9d2dc1875925b88f9a616cb7aadf3c2fda08510bf69d` |
| `/private/tmp/fastapi-additional-response-field-normal-coverage-runner.py` | `a716a3d8f18d2b79691db13883599aad129dd71d4b7c18372be3f5f7b6abd30e` |
| Imported utility module `/private/tmp/fastapi-lazy-dependency-coverage-runner.py` | `4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5` |

The normal helper imports the utility module under `lazy_coverage_helpers` and
uses only hashing/extension-path functions. Its `if __name__ == '__main__'` guard
prevents executing the utility module's separate fault lane during that import.
The coverage helper contains those utilities itself.

## Static selection reconciliation

Parsing the helpers' AST and the current admitted workflow/index files gives:

- Normal regression: **43 workflows / 203 unique cases**. This is prior198 plus
  the two existing OpenAPI controls plus new3. Forty workflows contain 199 ASGI
  cases and 504 ASGI actions; three direct Python API workflows contain four
  cases. The ASGI action count does not count direct API projections as requests.
- Normal coverage: **8 workflows / 86 unique cases / 248 ASGI actions per
  product**. No selected input contains a fault-contract case.
- Successful coverage closure should write **57 state checks**: seven stage
  checks for each of eight workflows (56), plus all-selections-complete (one).

| Coverage selection | Cases | ASGI actions |
| --- | ---: | ---: |
| baseline first-asgi-request | 12 | 12 |
| previous dependency-lifecycle | 5 | 9 |
| records dependency-wave-callables | 5 | 8 |
| classifier dependency-callable-classification | 23 | 54 |
| awaitable generator-awaitable-protocol | 15 | 47 |
| response response-field-lifecycle | 16 | 61 |
| traversal response-field-traversal | 7 | 42 |
| batch additional-response-field-lifecycle | 3 | 15 |

The six previous hints include **awaitable and traversal**, as well as previous,
records, classifier and response. Baseline12 + six previous71 = freshly measured
prior83; new3 produces86. There is no omission of the awaitable prior report, no
reuse of an old report path and no union with the separate fault build. The two
existing OpenAPI controls remain normal regression controls; they are not among
these coverage selections. This coverage subset therefore does not measure all
203 regression cases.

All eight prospective selections are uniquely indexed now. Input/recipe/workload
bytes match their indexed hashes; case and case-contract orders/cardinality are
equal; every indexed case has parity mode and nonempty requirement references.
The generic `--batch` parameter must be invoked with the reviewed additional3
materialized input; the helper itself does not hardcode or assert the 86 total.
Likewise the normal helper's expected203 is externally reconciled here, not an
internal literal threshold. Active admission remains parent-owned.

## Canonical execution and receipt guards

Normal regression delegates each whole workflow to canonical oracle/target and
compare commands, selecting the direct API commands only for the three declared
API workflows. It writes a new evidence directory, full logs, structured command
results and immutable canonical artifact references. It compares only after both
product commands exit zero; final success requires every comparison exit zero.
Its three independent workflow worker threads do not rewrite input cases or
observations. Canonical CLI and comparator enforce current input/workload/manifest
digests, schema, result order, identities and selected observations.

Its initial/final snapshots cover both target source trees using target_worker's
tracked/nonignored hashing rule, both installed native files and every selected
materialized input hash. Each target command identity must match the initial
combined source/pair digests. Snapshot hashing includes deleted tracked files and
symlink targets. Manifest, reviewed recipes and workloads are also covered by the
target source-tree digest. Canonical workers independently check workload and
manifest bytes and pinned source identity. The normal helper does not add a
per-stage source check or full per-case ledger; detailed canonical receipts and
an independent post-close audit remain required.

The coverage helper additionally fixes manifest, metadata, index and every
indexed input/recipe/workload file; verifies their case bindings before execution;
checks source, revisions, input files and native binaries around all canonical
stages; and checks all three receipts' exact selected case order. It requires
completed error-free artifacts, every target/source case completed and every
comparison passed. Canonical comparison still handles equality; the helper does
not inject results, normalize observations or weaken selectors.

Each workflow uses its own fresh profile directory. Oracle/compare environments
clear LLVM_PROFILE_FILE; only the target workflow receives that directory's
profile pattern. The isolated native identity probe uses a separate pattern
outside workflow directories and is not merged into any workflow report.
Nonempty profiles are merged; llvm-cov exports the captured binary; mismatch or
out-of-date stderr aborts the run. Raw export/stderr, filtered reports, contexts,
profile hashes and merge/export commands remain available for the later audit.
Filtering is limited to the declared FastAPI native prefixes and recomputes file
totals. Contexts and ledgers label coverage as workflow-level attribution, not
individual-case region ownership.

Report contexts bind configuration/build ID, native source hashes, report hash,
source/target/comparison artifact hashes and run IDs. A new output directory and
exclusive JSON writes prevent replacement of prior closed results. Fixed checks
are written in a finally block; a partial/failed run must never be treated as
completed measurements just because it has some reports.

## Build/lane and launch requirements

The coverage helper **does not build or install**. Exported dylib and installed
FastAPI extension must match; the sibling file participates in the native pair
digest. The exact sibling commit is checked. Isolated native identity must report
`fault_injection_compiled == False` and the selected installed module path.
Schema9 target identities must also explicitly prove a normal build. The
`--fault-python` argument name is inherited, but its default is the ordinary
`.venv-target`; feature checks reject an actual fault binary.

Canonical target/API workers also forbid fault binaries for older normal schemas
and verify imported extension locations, editable distributions, Python/package
pins and Cargo's selected sibling source. Their offline cargo metadata probe is
an identity check, not a build or installer. Its scratch overlay is ignored by
the repository so concurrent CLI identity checks do not enter source digests.

Launch must explicitly retain:

`STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65`

Both helpers inherit this environment instead of assigning it. Canonical direct
API source/compare and manifest API-contract validation resolve sibling artifacts
through this variable; passing target `--starlette-rs-source` alone does not bind
those checks. The parent was notified before any proposed run. The exact pinned
FastAPI/Starlette source checkouts must stay clean and their environments frozen.

For measurement claims, supply and preserve the completed instrumented build log
and pre-build receipt. The helper's feature list, flag string, toolchain/target
and build ID describe the caller-provided build; direct identity proves normal
versus fault, while LLVM profile compatibility proves this binary can consume the
profiles. Those checks do not reconstruct the entire compiler invocation or
detect undeclared unrelated features if no actual build evidence is supplied.
Build-log hashes are recorded when supplied; helper hashes and LLVM/tool versions
must be preserved with the parent command receipt.

## Clearance and later evidence boundaries

No concrete helper-selection, lane-contamination, prior-omission, result-shaping
or build/install blocker was found. Static clearance is conditional on the
explicit sibling environment, reviewed batch input and parent build/source
freezing. These are prospective controls; this note claims no future exit status,
imported binary equality, passing203/86, LLVM gain or accepted provider result.

Coverage-MCP must receive baseline + all six **fresh compatible** previous reports
+ batch, with their exact source/build contexts. Comparison hints alone are not
provider acceptance. Region gains and union counts require retained actual
provider request/result; historical prior83/normal198 receipts or fault reports
cannot replace these new measurements. The separate fault55+6 lane remains a
different feature/build identity and must retain oracle N/A for its six injected
cases. Individual-case coverage, full-matrix coverage, OpenAPI positive mode/
shared definitions and benchmarks remain outside this helper review.

Once additional3 pre-gate closes, the independent receipt audit will check actual
source/old-target/conparison IDs, counts, status/order, current indexed hashes,
initial/final source/native-pair snapshots, constructed/error observations,
lossless state/raw-send projections and first divergence without rerunning apps
or inserting expected data. Author-input provenance and independent receipt
observations will remain separate.
