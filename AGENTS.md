# Project rules

- Pin FastAPI 0.141.1, Starlette 1.6.0, Starlette-RS, Python, and Pydantic.
  Starlette 1.6 is sole oracle; sibling owns generic behavior.
- `metadata.yaml` owns identities, policy, and reviewed API overlays. Generate
  candidates/inventory from pinned source; keep classifications and fixture
  mappings in reviewed files. Run `make metadata-check` after changes.
- Complete the manifest before implementation/claims: exports, signatures,
  aliases, deprecations, requirements, operations, identities, and isolated
  Python/ASGI runner/comparator. Inventory is discovery, not support evidence.
- Expose `fastapi`; original FastAPI is source-oracle/dev-only, with zero
  target runtime dependency or import. Python runtime files allow only direct
  native re-exports and literal `__all__`; no helpers, functions, `if`/`else`,
  loops, or fallback behavior. Rust owns FastAPI behavior and control flow.
  Put it in `fastapi-rs/`; limit `fastapi-rs-py/` to PyO3 binding and
  value conversion. Enforce with `make python-facade-check`.
- For Rust changes, forbid unsafe and blanket lint suppressions; run
  `make fmt clippy` and static contract checks. Keep zero unit tests; never run
  pytest, unittest, or Cargo test. Verify with live identity-checked parity
  and static contract checks.
- Map recursive dependencies by feature, purpose, version, native/language
  parts, license, and runtime/optional/build/dev role. Author parity recipes as
  YAML under `tests/fixtures/input-recipes/`; include no expected outputs.
  After recipe edits run `make parity-inputs parity-index-update parity-validate`
  and exercise public interfaces in identity-checked isolated processes.
- After atlas or exclusion changes run `make compatibility-atlas-update`.
  Keep drafts outside active inputs; reviewed schemas cover Python/ASGI. Compare
  HTTP, WebSocket, lifecycle, validation, serialization, and OpenAPI; expose
  unsupported cases and normalize only documented differences.
- Bench only equivalent work after parity; declare boundary, gate, warmups,
  samples, environment, and ASGI/server/facade/native costs. Preserve notices;
  map every public API to manifest/index and never weaken the contract.
