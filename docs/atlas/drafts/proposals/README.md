# Worker dispatch and callable classification

The independent proposals now have active copies under
`tests/fixtures/input-recipes/parity/` and `tests/fixtures/workloads/`:

- `dependency-callable-classification`: 23 parity cases / 54 actions.
- `worker-dispatch`: 18 parity cases / 54 actions.

The authored copies here preserve proposal history. During admission, the active
classifier recipe added handling-errors source evidence and ordered HTTP headers
so its inherited handler links satisfy the reviewed contract. Neither copy has
expected outputs or copied upstream tests.

The native classifier, once-await behavior, ordinary endpoint worker dispatch,
response validation context, loop serialization, and ordinary ASGI body field
shape are integrated. Formatting, strict Clippy, and the Python facade check pass.
Fresh fixed-source comparisons are required before claiming this slice complete.
Classification history, mutable descriptors, generator-based await adapters,
response adapter construction/reuse, and explicit placeholder provenance remain
separate boundaries.

## Confirmed sibling blocker

The worker workflow's target process panics when a sync endpoint adds a background
task to the loop-created pinned Starlette-RS collector. The latest committed
sibling also retains the same thread-bound task classes. The entire 18-case worker
gate remains unpassed; a crashed process is not partial passing evidence.

A minimal sibling patch and safety review are in
`../sibling-background-cross-thread/`. Strict Clippy accepted the proposal in an
isolated checkout. The configured pin and installed sibling remain unchanged;
live parity and an approved new dependency revision are still required.

## Completion gates

1. Regenerate atlas, manifest and index; run metadata, fixture and static checks.
2. Observe the pinned oracle and compare every declared observation in isolated
   identity-checked processes, retaining failures and unsupported cases.
3. Run existing regression selections and the separate target-only cleanup fault
   contracts on fixed inputs, source and binaries. Ordinary input-triggered worker
   errors are parity evidence, not injected-fault coverage.
4. Remeasure accepted coverage on this revision with matching flags/features.
   Normal and fault-enabled instrumentation remain separate lanes; do not union
   old revisions or infer per-case region attribution.
5. Benchmark equivalent workloads after their callback, validation, serialization,
   cleanup and raw-message gates pass. Keep adapter/lifecycle and sibling gaps
   explicit when interpreting results.

Full FastAPI compatibility remains unfinished.

## Reviewed next inputs

- `generator-awaitable/`: 13 cases / 40 actions cover direct generator-based
  awaitables, invalid await results, future errors/warnings, cleanup and recovery.
  Its native adapter patch has bounded independent static review, but remains
  unapplied and uncompiled. Generic throw arity and audit hooks remain gaps.
- `response-field-lifecycle/`: 16 cases / 61 actions cover registration-time
  adapters, reuse, metadata, schema errors/warnings and immutable public response
  class precedence. Included response class defaults remain a deliberate target
  gap. No runtime execution or native implementation is claimed.

Both proposals passed recipe-loader/Ruff admission and independent static review.
They are outside active inputs and have no expected outputs. Activate and map
them before implementation or coverage claims.
