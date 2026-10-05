# Next native compatibility goal

Implement source-matching worker dispatch and immutable dependency callable
classification, with exact public outcomes, before new performance rankings.

These reviewed proposals are inactive. They have no expected outputs and are
outside the generated input tree. Parent checks use the repository recipe schema
loader and Ruff; no source/target execution is claimed. Recipe workload paths
describe future activation destinations.

- `worker-dispatch/`: 18 parity cases and 54 actions cover relative loop/worker
  execution, ContextVar propagation, original endpoint-kind response validation,
  loop serialization, sync/async dependencies, yield cleanup, errors/recovery,
  background work, returned Response and awaitable values, and worker-to-loop
  handoffs. Preserve complete raw sends: the current omitted-versus-false
  `more_body` difference must be exposed and resolved. Cancellation is unproven.
- `dependency-callable-classification/`: 23 parity cases and 54 actions cover
  immutable wrappers/partials around functions, methods, and instances,
  generator scopes/cleanup, endpoint controls, unmarked sync coroutine values,
  and scalar-return errors for wrapped or publicly marked coroutine routines. Classification-cache history and mutable descriptors remain separate.
  `native-classifier.patch` is a reviewed prospective helper/executor change
  based on `db8118a`; it remains unapplied and uncompiled. It routes classified
  coroutine scalars through the existing await error/cleanup adapter and retains
  raw worker return values. Generator-based awaitable adapters remain a gap.

## Completion evidence

1. Activate each independent recipe/workload with reviewed metadata references;
   regenerate atlas, manifest and input index and run static contract checks.
2. Observe the pinned live oracle; resolve input defects without weakening
   observations. Review Rust changes independently and run formatting/Clippy.
3. Run exact isolated source/target comparisons, existing regression selections,
   and cleanup fault contracts on fixed source/builds. Keep failures and gaps.
4. Remeasure accepted coverage on the new revision before any incremental union.
   Keep source, inputs, and extension binaries fixed; match build flags/features.
   Normal and fault-enabled instrumentation are separate verification lanes.
5. Benchmark equivalent direct-ASGI workloads only after dispatch, validation,
   serialization, cleanup, and raw-message behavior meet their declared gates.

This goal is one bounded slice. Full FastAPI compatibility remains unfinished.
