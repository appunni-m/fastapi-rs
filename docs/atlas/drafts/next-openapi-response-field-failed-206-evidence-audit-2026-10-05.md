# Closed normal regression: one exact-wire failure

Read-only artifact audit, 2026-10-05. No application, import of a native binary,
build, parity command or current-environment measurement was run for this audit.
The inspected run is closed under
`parity-results/next-openapi-response-field-wave/final-normal/`.

## Actual scope and outcome

The ledger contains 44 whole workflows: all oracle and target commands exit0,
and all comparison artifacts are completed without infrastructure errors.
Aggregated comparison scope is 206 selected, 205 passed, 1 failed, 0 not_run.
Every source and target case is completed. Each side records 523 completed ASGI
actions and 15 completed API probes. Construction errors are not reclassified
as action execution by this count; it counts only recorded completed actions.
The new retained-response-field workflow's three cases pass, as a separate
targeted result inside this failed regression run.

The sole failed case is **`fastapi.first-slice.openapi`**, from the
`first-asgi-request` workflow. Its source and target both return HTTP200 and a
2057-byte body with identical response headers. Parsed documents are equal;
raw bytes differ. The comparator preserves that exact HTTP mismatch.

| Recorded dictionary | Source key order | Target key order |
|---|---|---|
| Each of three operation parameters | name, in, required, schema | required, schema, name, in |
| requestBody | required, content | content, required |

Source body SHA256:
`52e6edbe28c219cf75ddaedb3482c944a41d24b5efd52c3794b18209ff7ecacd`.
Target body SHA256:
`8e9dbac4fc3184a2d2e5a30da7f70df9c46180cd76a9dd870ac098d2c9060def`.

## Artifact and identity bindings

| Artifact | SHA256 |
|---|---|
| final-normal/normal-runs.json | 834c162fde660ee788b397c2a44829d9fda914f474d6a699c01fe291e310f948 |
| final-normal/initial-source-build-snapshot.json | 909755e9e8009a4f67d4dd44327468b0e954e525f0d02a2feb79e0e40b81fdea |
| final-normal/final-source-build-snapshot.json | 909755e9e8009a4f67d4dd44327468b0e954e525f0d02a2feb79e0e40b81fdea |
| oracle/9de94eea-4165-42c2-a787-6f2987d92829.json | 04beeddaa7b99a0ae6702acc729a139179c6de8b8475d1ab5106c32ec0774498 |
| target/10b7f4df-3ebf-42fa-9eab-096b1e256536.json | 985c6bb8ddd1819ad210ce3c7fb1152b78108a04d22dd8c3dcd77552310daea7 |
| comparisons/13224e0d-2a94-4699-91d7-a1edac3c2864.json | 4424fd270f80732dd5e3ac6daeeb0689cd3275891369ac5fc15c291ae8d623fd |

Artifact paths in the final three rows are relative to `parity-results/`.
Initial and final snapshots are byte-identical, including all44 input hashes.
Every source/target/comparison artifact binds its input to the appropriate
frozen input hash. Every comparison source/target reference matches the actual
artifact digest and run ID. All44 target receipt identities match these frozen
source/native digests:

- FastAPI-RS source: `39967f7ec6f9e484005751af2a1e6750da00a8edc1f0728ca6e98fa98842bbf3`
- Starlette-RS source: `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`
- Combined source: `f4f1b382bae2cfd4d3cb3b0ef7f9aae8a7520fac33bd6c4f2a95cc1ac40d87b2`
- FastAPI native: `847bc07236baaa461b88ed4f29ddefe730ddf32de4610541d0b1f93d9a145184`
- Starlette native: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`
- Native pair: `a437662135f67157e37d984c9e6b6db42f011fdbe4479fc2bb00c2c835860356`
- Target revision: `1c66469c5b2eae6af709c52d4e7ae2bcf61d8aa8`
- Sibling revision: `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`

The recorded oracle remains FastAPI0.141.1 / Starlette1.6.0 /
CPython3.12.13 / Pydantic2.13.4 / core2.46.4. These are receipt bindings;
they make no claim about binaries after this closed run.

## Source diagnosis and limits

Pinned `fastapi/openapi/models.py:419-425` declares
`paths: dict[str, PathItem | Any] | None`. Parameter's `in` field is an Enum
at221-225,258-260. The source finalizes with `OpenAPI(**output)` before encoder
model_dump at `openapi/utils.py:679` and `encoders.py:243-258`. Pydantic's actual
union selection can therefore keep a path value as Any after lax enum
conversion, preserving its input dictionary order. A parameter-free path may
instead select the model branch. This source-backed explanation requires the
real graph and its engine rather than role-based unconditional ordering.

This is failed regression evidence. It is not a206-pass claim, complete active
matrix evidence, a coverage result, a fault result, a restored-binary proof or
a benchmark gate. Fresh reviewed implementation and live regression closure
remain parent-owned. No selector or comparator change is proposed.
