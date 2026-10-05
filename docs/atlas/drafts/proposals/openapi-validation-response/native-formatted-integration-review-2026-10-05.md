# Formatted automatic-422 integration review

2026-10-05, independent source-only check after parent applied frozen v2 patch
`e06e0f074f9e5b98f0538891522cd745f68a3f44e2bab2f6e835bb8b5dcd4afc`.

The repository Rustfmt configuration was applied to each frozen proposal through
stdin with `--emit stdout`, edition 2024 and repository `rustfmt.toml`. Neither
the proposal nor active file was modified by this reviewer. Both formatter calls
returned 0 with empty stderr, and their complete output bytes equal the active
files. Runtime differs only by formatter wrapping; OpenAPI is already identical.

| File | Active / independently formatted proposal SHA256 |
|---|---|
| `fastapi-rs/src/application_runtime.rs` | `0cd89081d79ca2d59b94e01839eb5e5e30778f18683c86822919a054e03bca11` |
| `fastapi-rs/src/openapi.rs` | `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d` |

The frozen runtime proposal remains
`8847050134c52f21cadd77d911e68cc63311deba7ea4be58a05e9a7bed3d436f`;
the OpenAPI proposal hash equals the table. `git diff --name-only` versus
admission revision `a34714f47749b6f96d5d7829dc16b0d444efaa5e` contains exactly
these two files. Other tracked Rust, facade, metadata/input-source and dependency
files therefore have no delta against admission at this check. This tracked-tree
check is not a new assertion about ignored materialized inputs or native bytes.

Machine receipt:
`/private/tmp/fastapi-rs-openapi-validation-response-formatted-integration.json`,
SHA256 `965c19726d701b3a0e850efafa55cf425e75ade23814e4471c8929bcd9909606`.
The prior PRE/author/independent source-review artifacts retain their historical
bytes and bounds. This check establishes formatting and source delta ownership;
it does not establish the still-running full static stage, native build/import
or POST4 parity. No compiler, application, native module or unit framework was
run or read by this reviewer.
