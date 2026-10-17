# Parity workload source check

`make parity-workload-check` screens every Python module under
`tests/fixtures/workloads/` and validates all active recipes in
`tests/fixtures/input-recipes/parity/`. It also parses every pinned FastAPI
`tests/test*.py` source module with Python's AST. The check reads source only:
it does not import or execute workload or upstream test modules.

The gate rejects test framework and upstream test-module imports, `TestClient`
usage, test-named functions, conventionally named assertion-helper calls and
imported aliases, every Python `assert` statement, conventional expected-output
names or mapping keys, and workload function bodies whose AST exactly matches
a source-evidence `test_*` function after literal values are normalized. It
also verifies that every upstream test evidence path used for that comparison
resolves inside the selected pinned FastAPI source tree. Workload and upstream
test symlinks that resolve outside their declared roots are rejected.

Application code may return literal response data: that is part of the
independent workload run by both implementations, not a stored oracle result.
The naming checks target common expected-output storage patterns. AST matching
catches copied test-function bodies with changed literal inputs, while partial
copies, custom assertion helpers renamed to ordinary identifiers, and arbitrary
semantic encodings are not provable from static source analysis.
Workflow schemas independently reject output fields in parity recipes.

`make parity-validate` runs this gate before validating the selected
materialized workflow. Set `FASTAPI_SOURCE` to the pinned FastAPI checkout when
it is not at the repository's default sibling path.
