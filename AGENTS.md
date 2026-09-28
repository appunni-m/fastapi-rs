# Project rules

- Pin FastAPI 0.141.1, Starlette 1.6.0, Starlette-RS, Python, and Pydantic
  identities. Starlette 1.6.0 is the sole oracle and replacement contract. Do
  not add another Starlette profile or use moving branches as authority.
- Keep `metadata.yaml` as the human-maintained API source authority; verify it
  against generated inventories, the manifest, and the sibling Starlette-RS
  contract with `make metadata-check`.
- Before implementation or compatibility claims, create one full API contract
  at `tests/fixtures/manifest.yaml`, including exports, signatures, aliases,
  deprecations, and requirements. Until then, atlas entries are candidates, not
  executable parity evidence. Track generic Starlette behavior through
  Starlette-RS's separate contract. The current manifest is foundation-only;
  finish operation review, identity checks, and the Python/ASGI runner first.
- The original FastAPI package is source-oracle/dev-only and must never be a
  target runtime dependency or import. Python is a pass-through binding layer:
  expose `fastapi`, forward arguments/results and preserve Python object,
  exception, and awaitable identity. Put routing, dependency resolution,
  validation, serialization, OpenAPI, middleware, lifecycle, and protocol
  control flow in Rust; no Python `if`/`else` or loops may implement FastAPI
  behavior. Keep Python glue mechanical and minimal.
- Put Rust behavior in `fastapi-rs/` and PyO3 conversion in `fastapi-rs-py/`;
  keep the public import namespace `fastapi` free of Python fallback behavior.
- Keep unsafe Rust forbidden and do not add blanket lint suppressions. Run
  `make fmt clippy` and the static contract checks for Rust changes.
- Keep zero unit tests in the repository. Verify compatibility through live
  source/target parity workflows plus static schema, manifest, index, and lint
  checks; do not add or invoke pytest, unittest, or Cargo test suites.
- Generate `tests/fixtures/api-inventory.json` from the pinned source; it is
  inventory input, never support or parity evidence.
- Map recursive dependencies by feature, purpose, version, language/native
  parts, and license; distinguish runtime, optional, build, and dev graphs.
- Author parity/benchmark stimuli as YAML under
  `tests/fixtures/input-recipes/`; JSON under `tests/fixtures/inputs/parity/`
  is generated and ignored. Recipes contain no expected outputs or measurements.
  After recipe edits run `make parity-inputs`, `make parity-index-update`, and
  `make parity-validate`; run live
  identity-checked products through public interfaces in isolated processes.
- After atlas or exclusion-rule changes run `make compatibility-atlas-update`
  to regenerate the atlas/backlog, sync manifest digests, and validate links.
- Keep design drafts outside active input directories; use only a reviewed,
  fixed schema that can represent Python workloads and ASGI observations.
- Compare observable HTTP, WebSocket, lifecycle, validation, serialization,
  and OpenAPI behavior. Keep unsupported/skipped cases visible; normalize only
  reusable, documented differences.
- Bench only equivalent work after its parity gate passes. Declare boundary,
  correctness gate, warmups, samples, and environment; separate in-process
  ASGI/server timings and Python-facade/native-Rust costs.
- Preserve upstream notices. Check that every public API maps to the manifest
  and indexed inputs; never weaken the contract to hide a mismatch.
