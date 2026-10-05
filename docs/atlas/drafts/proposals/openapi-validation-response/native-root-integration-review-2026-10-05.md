# Response-key and automatic validation-response native integration

2026-10-05. The parent applied independently reviewed v2 patch
`e06e0f074f9e5b98f0538891522cd745f68a3f44e2bab2f6e835bb8b5dcd4afc`
after the complete source-first gate and preserved unchanged-target failure.
Author and independent reviews describe historical prospective snapshots;
this note records their later integration. They establish bounded source-backed
intent; fresh post-repair runtime evidence remains a subsequent gate.

## Exact scope and checks

Only two native files changed. Raw additional-response status ownership and
Python-stage key conversion replace eager integer-only rejection. Declared
responses merge before the actual merged-key automatic 422 decision. The prior
metadata restriction, private OpenAPI model graph, Python facade, dependencies,
pins, inputs, comparison selectors and source classifications are unchanged.
The existing global validation-definition collision behavior remains a gap.

| Applied source | SHA256 |
|---|---|
| application_runtime.rs | `0cd89081d79ca2d59b94e01839eb5e5e30778f18683c86822919a054e03bca11` |
| openapi.rs | `e217e4c26a1fdf0f5ec3f8078b85f6f5a44c1f4bf20439bab709e9c29463742d` |

Independent formatting verification finds these exact active bytes equal to
Rustfmt output of the frozen proposal. Strict checks closed with exit 0:

```sh
env RUSTC_WRAPPER= STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65 \
  make -j1 fmt clippy metadata-check api-contract-check parity-index-check \
  dependency-inventory-check pydantic-core-inventory-check dependency-graph-check \
  python-facade-check benchmark-contract-check parity-validate
```

Saved log: `parity-results/openapi-validation-response-native-static-contracts.log`, SHA256 `0d7d4b63c4d2fdc947ddb00d312d4e2077b8152ec03ff387283298c5f7664053`.
Policy checks cover 22 Rust source files and 616 formatted/linted Python files.
No unit framework was added or run. Manifest remains 555 workflows / 2304
input cases, with 1582 reviewed partial source mappings and 1369 fixture links.
The benchmark policy checker sees seven workload contracts and zero root suite
artifacts; historical suites were preserved before the input admission.

## Preserved baseline and next evidence

Source PRE4 reached four successful constructors and all 24 HTTP actions.
Target PRE4 reached two constructors/12 actions, with two ordinary constructor
errors blocking twelve actions. Comparison selected four cases and failed all
four; zero case-level not_run does not mean those twelve actions executed.
Those receipts remain preserved in the pre-change folder and its independent
audit. They are ordinary parity failures, not fault contracts.

Next execution must prove the rebuilt native import and unchanged input/source/
native snapshots, compare all four fresh cases, and rerun the selected prior
normal/API corpus. Managed normal coverage and existing fault contracts use
separate freshly instrumented builds; benchmark timing follows parity and exact
normal binary restoration. This integration note makes no post-repair pass,
coverage increment, benchmark or full public-surface support claim.

Raw hash/callback/snapshot histories, full response deep merge, fallback metadata,
modeled ranges/includes, empty parameter models, schema-name collisions and the
legacy eleven inline-schema key-order differences retain independent gaps.
