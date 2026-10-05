# Prospective source-first automatic-validation-response runner

Date: 2026-10-05. TMP-only source/static inspection and constant-only copy.
No helper import/run, app/native execution, build, parity stage, source/sibling
edit or active input/metadata/generated change was performed.

| File | SHA256 |
| --- | --- |
| Reviewed base `/private/tmp/fastapi-openapi-final-model-post-v2-runner.py` | ad28b5a53d598c93f89f7c52a0074c4829315bc43d8371c5f09d9511ebc42fc5 |
| Prospective `/private/tmp/fastapi-openapi-validation-response-pre-runner.py` | 60fa02332e94224d35de2b013493c0eb945d6a42545b005cfff5dddba7e3c39a |
| Narrow `/private/tmp/fastapi-openapi-validation-response-pre-runner.patch` | f70358dcf41abcb0a78df12a4a37fd78dd8293b8e0c757c49eca2228a8be26b4 |
| Unchanged snapshot helper `/private/tmp/fastapi-lazy-dependency-coverage-runner.py` | 4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5 |

Only two assignment values change: OUT now names
`parity-results/openapi-validation-response-wave/pre-change`, and FAMILIES is
one ordinary ASGI family (`openapi-validation-response`, same input basename,
False). Reverse substitution recovers the exact base bytes. AST comparison
with only those assignments restored matches the base. No formatter or body
change is introduced. Metadata/input admission and a new frozen source revision
are root prerequisites; the source/read files are not present actively yet.

## Preserved gate and evidence behavior

- The canonical CLI first runs the entire declared source workflow in the
  pinned oracle environment. It preserves the CLI stdout/stderr log and native
  artifact references. A nonzero source CLI exit stops this family before target.
- Its saved source receipt must have the exact declared case inventory/order.
  Every constructor must select outcome=ok; every planned action must have the
  exact ID and completed status, with no missing/extra action. For the reviewed
  unchanged schema9 inputs this requires four constructors and 24 actual actions.
  The target call appears strictly after all these checks; there is only one
  family, so all selected source work completes before any selected target work.
- The target uses `.venv-target/bin/python` and the exact immutable sibling
  `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`. Product/construction failures are
  retained as actual target artifacts; no code substitutes values, skips cases
  or relabels ordinary 4XX/default declaration failures as faults. Existing CLI
  product-error reporting (`scripts/parity/cli.py:473-482`) remains unchanged.
- If both transport CLI runs exit 0, compare is invoked on their exact artifact
  paths. Comparison exit 1 remains in normal-runs.json and the helper finally
  exits1. No mismatch is swallowed or turned into a successful comparison.
- `OUT.mkdir(exist_ok=False)` protects an existing run. Each command writes its
  own log. Successful family execution writes source/target/comparison command,
  exit/status/result refs to normal-runs.json, plus initial/final snapshots.
  Early raised source/transport errors may leave logs/artifacts without a final
  aggregate snapshot; that is retained incomplete evidence, not a completed run.
- Initial/final snapshots use the existing tracked/nonignored target and pinned
  sibling hash algorithm, direct extension file hashes and materialized input
  hashes. Both snapshots must match. Each target CLI identity's combined source
  and binary digest must equal the initial snapshot. The helper does not build,
  install, import target binaries for snapshots or change the selected native.
  Parent's existing normal/fault identity proof is separate.

The imported snapshot helper's work is under a `__main__` guard; this author
inspected it without loading it. No comparator/schema/fixture selector or
snapshot recipe changed. No explicit constants prescribe expected HTTP/docs/
warning/error values. Source gate completion still means completed selected
observations, not a broad source-support claim or a comparison pass. Root alone
owns later execution after admission/regeneration/commit and stage closure.
