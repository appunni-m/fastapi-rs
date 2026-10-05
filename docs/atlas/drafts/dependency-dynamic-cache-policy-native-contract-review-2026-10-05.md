# Dynamic dependency cache policies — reviewed contract

FastAPI 0.141.1 captures the raw `use_cache` object during dependency analysis
(`fastapi/dependencies/utils.py:271-347`). Solving resolves children, validates
the edge's inputs, skips failed edges, then evaluates truthiness once before
cache membership (`:640-680`). Even a false policy can populate an empty cache;
later results do not replace its first value. Cached parents still resolve
children and validate their own inputs. Endpoint input validation follows
dependency solving. Parameterless declarations omit the supplied policy and
use literal True (`:130-145`).

Native plans must retain the captured object identity without coercion.
Mutating that object affects later decisions; replacing a declaration's field
does not replace the original outer edge policy. Overrides retain that outer
policy and cache identity while rebuilt children capture their own policies.
Truthiness errors propagate through the existing yielded-resource cleanup,
and an await/resume must not evaluate the same successful edge twice.

The independent `dependency-dynamic-cache-policy.yaml` inputs project policy,
validation, invocation, identity, and cleanup traces through public HTTP
interfaces. They cover synchronous and asynchronous edges, nested child
mutation, overrides between requests, failed edges and successful siblings,
`__bool__`/`__len__` failures and recovery, and app/router/route parameterless
declarations. Its existing post-resolution injection is target-only fault
evidence and cannot count as an oracle parity pass. Recipes contain no expected
outputs; execution claims require fresh identity-checked results.

Eager override analysis remains a separate gap: a policy on an earlier edge
can mutate `dependency_overrides` and affect a later edge during the same
source request, while native graph construction currently rebuilds the later
edge early. Same-request override-map mutation, signature/property access
counts, mutable callable-classification caches, custom callable hash/equality,
and arbitrary OAuth-scope execution are outside this bounded slice.

## Execution at 064c74f

Fresh normal-build regression at `064c74f96c7e47535a954624eaea6aac4b86c974`
passed 137 parity cases across 36 workflows. A separately instrumented build
remeasured the baseline, prior nested-dependency cases, native-record cases,
and new cache-policy cases on one fixed source/build: 37 parity cases and five
target-only cleanup faults passed. This includes all 13 new parity cases and
their cleanup fault. The mixed v9 workflows require a fault-enabled target;
a later normal-target attempt was rejected by that identity gate before product
execution and adds no parity evidence.

Coverage MCP verified 1,935 new Rust regions beyond the remeasured accepted
selections: 10,004/29,863 became 11,939/29,863, a 6.479590 percentage-point
gain. This is selected-workload region coverage; full-suite coverage regression
is unknown. Reports from changed source/build snapshots are not combined.

The full source digest is
`ea55bd8993b74c9ca6273406a115a3f0e804635065682551f395628af712c1d8`.
The normal binary aggregate is
`7ce612eac3867093b5f5dc91c8292e6f4e0c451c786715295f16fd1f4510e4da`.
Normal receipts are under `parity-results/dynamic-cache-policy-wave/final-normal/`;
instrumented input/source/build snapshots, comparison receipts, fault ledger,
and `coverage-mcp-comparison.json` are under
`parity-results/coverage/dynamic-cache-policy-incremental/064c74f-first/`.
Generated artifacts remain ignored and local. Formatting, strict Clippy,
Python facade/runtime boundaries, metadata, atlas, dependency inventories,
and benchmark contracts passed. No unit tests were used.

The restored normal release build completed all seven benchmark gates;
see [the measurements](../../benchmarks/2026-10-05-064c74f.md).
