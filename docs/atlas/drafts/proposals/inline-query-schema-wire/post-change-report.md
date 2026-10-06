# Inline query default OpenAPI schema parity: post-change report

Date: 2026-10-06. Scope: the two admitted primitive query-default cases in
`inline-query-schema-wire.yaml` (direct endpoint parameters and dependency
parameters). This closes those cases only; it does not claim general FastAPI
parameter or OpenAPI parity.

## Change

`CallableParameter` now retains whether a default arrived outside `Annotated`
or inside its `FieldInfo`. OpenAPI schema generation delivers external defaults
through Pydantic's public `Field` metadata before schema creation, retaining
explicit `None`; defaults already in `FieldInfo` remain in the annotation.
Schema defaults are no longer reinserted after Pydantic has generated the
schema. The parameter-specific normalizer preserves Pydantic's key order while
translating component references and retaining existing FastAPI bytes and
`exclusiveMinimum` conversions. Request-body and response-schema normalization
remain unchanged.

## Evidence

The saved PRE audit (`parity-results/staging/inline-query-pre-audit/review.md`,
SHA-256 `b9edbc05612dad34a7698fbe1c83a8b14c63d6ecd85dd1ca1aadee53e51edd6e`)
records two failures caused by raw `/openapi.json` object-key order: source
encoded each non-null schema as `type, default, title`, while the target encoded
`type, title, default`. Parsed OpenAPI documents were equal. All eight HTTP
actions completed; the saved PRE run used FastAPI 0.141.1 / Starlette 1.6.0 and
target revision `b16f744ed95671ff9488d24840d6003cd114c025`. The failure was kept
as evidence; selectors and normalization rules were not weakened.

After the change, `make parity-first-slice` completed both selected cases:

| Artifact | Run ID | SHA-256 |
|---|---|---|
| Input `tests/fixtures/inputs/parity/inline-query-schema-wire.json` | — | `3526e6b55176663e566ae1495c8b5e3ce9779a98cbfe9aaec10750b2e4dbd9b1` |
| Oracle `parity-results/oracle/a8a4c11f-7ec0-45b5-b550-55b35abac2ab.json` | `a8a4c11f-7ec0-45b5-b550-55b35abac2ab` | `916d7d1308ff53aa6369a091c6852d284db85c556f036ba50dc78a0dd5feba54` |
| Target `parity-results/target/84823e8e-e75b-4aaf-85b1-ef649c0ac096.json` | `84823e8e-e75b-4aaf-85b1-ef649c0ac096` | `56fe5afc4dafac5d63a0fcbb0c4837528d1b01633744ce29590283f6b8828d32` |
| Comparison `parity-results/comparisons/24d642e7-aafc-4536-9e6d-31a845be96f4.json` | `24d642e7-aafc-4536-9e6d-31a845be96f4` | `de7fe57b1c0a2fd784d79f479cb75599d953c2e032987be7d619ff6205839ccc` |

Comparison result: 2 selected, 2 passed, 0 failed, 0 not run; fault-contract
cases selected: 0. Each case exercises four GET actions, including exact HTTP
status, ordered headers, raw body bytes, ASGI message types, exception result,
and the public OpenAPI document. There were no construction or product errors.

Source identity: FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`,
Starlette 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4. Target identity: fastapi-rs 0.1.0,
checkout base revision `a4af9282968952113396330449722bb1c9592bb3`, source tree
SHA-256 `405c66fc969f0ad9921fdf9c6896d2606b8d3f5f1b92c251a34e761116104bc8`,
release binary SHA-256
`0a82927c5f7186d6d15865eb282266b7029b763bc19739cbd7a4ef6b6ef3dbe9`,
Starlette-RS `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`, CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4. The target was the normal release
extension (`fault_injection_compiled=false`); upstream FastAPI was absent from
the target runtime.

The saved regression aggregate
`parity-results/inline-query-schema-wire-wave/post-regression/normal-runs.json`
has SHA-256 `e3e3c6d3948693104d332d41412b15203cb32ec8795bca0604da07972050a9e5`.
It replays the existing 47 workflows and direct API controls: 214 selected,
214 passed, 0 failed, 0 not run. Every source, target, and comparison process
exited successfully. To compare identity across older receipt schemas, the
aggregate ignores only the optional `fault_injection_compiled` field: it is
absent in 39 legacy receipts, null in 8 source receipts, and false in 8 target
receipts. All other identity fields match within each lane; all target runs
used `.venv-target`.

## Gates and limits

Passed:

- `RUSTC_WRAPPER= make fmt clippy python-facade-check metadata-check api-contract-check STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65`
- `make parity-prepare-oracle`
- `make parity-prepare-target STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65`
- `make parity-first-slice PARITY_INPUT=tests/fixtures/inputs/parity/inline-query-schema-wire.json STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65`

No expected outputs or copied upstream tests were added. No unit-test framework
or benchmark was run. The result covers static primitive defaults on direct and
dependency parameters; nullable and required cases, other parameter sources,
complex models, aliases, custom metadata, shared definitions, and broader
schema-order behavior remain separate parity work.
