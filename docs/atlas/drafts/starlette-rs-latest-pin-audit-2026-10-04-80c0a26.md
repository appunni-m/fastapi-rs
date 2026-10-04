# Starlette-RS pin audit: 80c0a26

FastAPI-RS advances its Starlette-RS implementation contract from
`534578339d9c2487abb23fd8ee589fcf03be0778` to the latest verified remote
`main`, `80c0a269b8b10ed427e3f1ebda36320ae375776c`. Starlette remains pinned to
1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` as the sole compatibility
oracle. The existing `../starlette-rs` worktree contains unrelated changes and
was not modified; generation and builds used the clean detached checkout at
`/private/tmp/fastapi-rs-starlette-rs-80c0a269`.

Since `5345783`, commit `08c5539` implements live native Router mutations and
updates Router cache-invalidation parity inputs and adapters. Commit `80c0a26`
refreshes Router parity and benchmark documentation. The pinned metadata,
API-surface catalog, and API review are unchanged; the sibling manifest digest
is updated to `d1f8a36d8579946cc6e3a451405393578419f352e93cf7253110f944659fbd2f`.
The FastAPI import-binding review now records the exact source blobs and hashes
for the selected sibling commit. Generic Router cases remain sibling-owned and
do not establish FastAPI-RS parity by themselves.

The refreshed atlas still inventories 1,593 FastAPI API candidates (460
supported, 1,104 private/internal, 29 uncertain), maps 453 of 492 upstream
test modules, and materializes 526 workflows / 2,069 cases. The first
request-to-response slice passed 12/12 after rebuilding the target against
`80c0a26` (comparison `3d5b6fb2-cc49-465c-ad47-bda506c54684`). This is narrow
parity evidence; 341 public operation scopes remain pending review and full
FastAPI parity remains incomplete.

Formatting, Clippy, Rust policy, Python facade, metadata authority, API
contract, fixture index, dependency inventory, and dependency graph checks
passed. The six-workload benchmark suite still needs a fresh run against this
pin. No unit-test suite was run.
