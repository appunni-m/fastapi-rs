# FastAPI 0.157.0 source-evidence and parity snapshot

- Review date: 2026-10-23
- FastAPI-RS main: `e52fba0708185a312c9dae6b4c6e887fbd39972c`
- Manifest SHA-256: `caefe574340ff873c8fb5ac7d8403235bf21d8a42a48872e546d4656018d18f5`

## Pinned identities

- FastAPI 0.157.0: `386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`.
- Starlette 1.6.0: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` (sole Starlette oracle).
- Starlette-RS: `4139a72449bf5751e8902fb1c7175ee7f191d338`.
- Pydantic 2.13.5, pydantic-core 2.46.5, and CPython 3.12.13.

The identities are declared by the active metadata and source artifacts. The
current target identity recorded in the focused parity receipts is revision
`e52fba0708185a312c9dae6b4c6e887fbd39972c`, source-tree SHA-256
`fe307044aa2938bb7d4bac8b0458fd4deae0813dca3f1948d82f01c52d06d989`, and
native binary SHA-256
`40676a3159e985e9564b16ff94204476802a511152082aa3851da4ee855bc274`.

## Current atlas and target scope

Counts below were read from the generated `tests/fixtures/compatibility-atlas.json`
and `tests/fixtures/manifest.yaml` at the revisions above. Source API
classification does not claim FastAPI-RS implementation support.

| Inventory | Current count |
| --- | ---: |
| Source API candidates | 1,831 |
| Source-supported / private-internal / uncertain | 494 / 1,279 / 58 |
| Supported inherited Starlette operations | 9 of 13 reviewed candidates |
| Upstream test modules linked to input workflows | 473 of 527; 54 excluded with reasons |
| Documentation pages linked / excluded | 106 / 50 of 156 |
| Documentation Python examples linked / excluded | 335 / 41; 91 support files excluded |
| Reviewed documentation sections / excluded | 559 / 1,613 of 2,172 |
| Input-only fixture designs / function designs | 914 / 2,363 |
| Exact test-function workflow/case links | 1,041 |
| Target API entries fully supported / unresolved | 29 / 473 of 502 |

No candidate page, test module, or documentation Python example remains pending
behavior review. A reviewed partial mapping is not complete feature coverage.
The current manifest still has 473 unresolved target API entries; this project
does not have full FastAPI parity.

The source inventory records 23 deprecation-bearing symbols. Parameter
annotations and warning calls are assigned to their owning methods; class-level
deprecations include `UJSONResponse` and `ORJSONResponse`. This is source
evidence, not proof of warning-category or runtime-timing parity.

## Current focused parity evidence

The `validation-error-context-exact-review` workflow was run in two selected
groups against the same manifest and target identity. Together, these receipts
cover 13 selected cases, not the complete FastAPI error contract:

| Selected cases | Result | Comparison receipt | Input SHA-256 |
| ---: | --- | --- | --- |
| 5 | 5 passed, 0 failed | `257553d9-5be3-41e6-a9d5-fd21903818f6` | `d636f535494bdc1b79fd9bb7d54588495554806b765fda3ee5031ab9b49857eb` |
| 8 | 8 passed, 0 failed | `f40b43b8-88bd-4b53-b070-a581f4f84007` | `4a83a7f4ecbdd8a7a7fc7e9e60f5e50f55dd1367a88cda1361c6b2ad0b048a2e` |

Both comparison artifacts declare manifest SHA-256
`caefe574340ff873c8fb5ac7d8403235bf21d8a42a48872e546d4656018d18f5`, pinned
FastAPI and Starlette source commits above, and target revision, Starlette-RS,
source-tree, and binary identities above. Generated inputs and results remain
ignored local evidence; reviewed recipes and metadata are committed.

## Earlier receipts retained as historical evidence

The previously recorded `model-extra-request-parameters-upstream` (4/4),
`response-204-bodyless-isolated-upstream` (1/1), `uploadfile-pydantic-contract`
(6/6), and `worker-dispatch` (18/18) receipts targeted FastAPI-RS revision
`f84074ce292f62ece155cc3ba6879e54508475ee`. They remain evidence for those
specific inputs at that earlier target, but are not current-target receipts.
They are not repeated here as proof of the current `e52fba0` target.

The `jsonable-encoder.name-email` case passed 1/1 at target revision
`f5bf63670dd4eb6a45250902a0f963da87542f24` with the active manifest SHA. The
first-slice benchmark is recorded separately in
[`docs/benchmarks/2026-10-23-f5bf636.md`](../../benchmarks/2026-10-23-f5bf636.md);
it reports slower latency and throughput than FastAPI for its one direct-ASGI
workload and does not establish broad performance.

## Validation boundary

The atlas counters and parity details in this snapshot were checked against the
generated atlas, manifest, and comparison artifacts. The documentation edit
does not change recipes, generated inputs, manifest data, or implementation;
no parity workflow or broad test suite was rerun for it.

The earlier validation record (`compatibility-atlas-update`, `metadata-check`,
`api-contract-check`, `benchmark-contract-check`, `clippy`, and Rust formatting)
belongs to the `f84074ce` snapshot. It is historical evidence and does not
replace checks required by future atlas, metadata, or Rust code changes.
