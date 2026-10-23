# FastAPI 0.157.0 source-evidence and parity snapshot

- Review date: 2026-10-23
- FastAPI-RS main when this note was refreshed: `1ed1f20c53946bb27a16982d242cc3bf521d8699`
- Earlier FastAPI-RS parity target: `e52fba0708185a312c9dae6b4c6e887fbd39972c`
- Current manifest SHA-256: `9a600d458c39683e04a81f3a68020e0e2a23a0881fc40a2821ccaa4b44b20a2`

## Pinned identities

- FastAPI 0.157.0: `386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`.
- Starlette 1.6.0: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` (sole Starlette oracle).
- Starlette-RS: `4139a72449bf5751e8902fb1c7175ee7f191d338`.
- Pydantic 2.13.5, pydantic-core 2.46.5, and CPython 3.12.13.

The identities are declared by the active metadata and source artifacts. The
retained 13-case receipts below target revision
`e52fba0708185a312c9dae6b4c6e887fbd39972c`, source-tree SHA-256
`fe307044aa2938bb7d4bac8b0458fd4deae0813dca3f1948d82f01c52d06d989`, and
native binary SHA-256
`40676a3159e985e9564b16ff94204476802a511152082aa3851da4ee855bc274`. The
later one-case API-contract receipt records the target source digest and binary
separately.

## Current atlas and target scope

Counts below were read from the generated `tests/fixtures/compatibility-atlas.json`
and current `tests/fixtures/manifest.yaml`. Source API
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
| Target API entries fully supported / unresolved | 29 / 474 of 503 |

No candidate page, test module, or documentation Python example remains pending
behavior review. A reviewed partial mapping is not complete feature coverage.
The current manifest still has 474 unresolved target API entries; this project
does not have full FastAPI parity.

The source inventory records 23 deprecation-bearing symbols. Parameter
annotations and warning calls are assigned to their owning methods; class-level
deprecations include `UJSONResponse` and `ORJSONResponse`. This is source
evidence, not proof of warning-category or runtime-timing parity.

## Retained focused parity evidence

The `first-asgi-request` workflow matched all 15 selected cases at current
`main` (`1ed1f20c53946bb27a16982d242cc3bf521d8699`) against FastAPI 0.157.0
`386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`, Starlette 1.6.0
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338`. The comparison receipt is
`d72e6222-cfff-4b55-aab8-0213bcad479f`, with input SHA-256
`f86389f4c4540db8122d11742d60549adb27082d2adbda7590e37492450edc14`,
manifest SHA-256 `9a600d458c39683e04a81f3a68020e0e2a23a0881fc40a2821ccaa4b44b20a2`,
target source-tree SHA-256
`a063f899a67ad3663b1699252b144daf55f5a851990a22753607ba5e62732bf3`, and
native binary SHA-256
`16f1334ad26e2d2047cf5bd51e64f5ae0311a676f82ece1544a6232453722287`. This
workflow includes the OpenAPI case affected by the intervening OpenAPI changes;
the other 14 cases passed as part of the selected workflow, not as proof of
broader parity.

The `validation-exception-api-contract` workflow ran only
`fastapi.validation-exceptions.direct-api-contract` after the private native
binding change. It matched 1/1 against the current manifest SHA-256
`4142a1b897968c940574f37b6adbaed346da585437419c710c1e04bcd441fa`; comparison
receipt `de67ff79-36bc-4d64-9e49-f16eb0eb35aa`, target revision
`d032baf2f9e660a7fd15cf11a889d37664671c88`, input SHA-256
`e30709e97ac905953a5992c0dd24d9b037ab1d1929ea9d7400a7255aeffc8570`, target
source-tree SHA-256
`0242dc96427a2103c976be7c52dcfa8ce8550c0f00a0967d5e30ead4311e3bee`, and
native binary SHA-256
`624582476d957ead9cdee6f0acf17e460cc9d8f2064e63d92f464c5035972638`. The
workflow used Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338`.

The `validation-error-context-exact-review` workflow passed in two selected
groups against manifest SHA-256
`caefe574340ff873c8fb5ac7d8403235bf21d8a42a48872e546d4656018d18f5` and target
`e52fba0708185a312c9dae6b4c6e887fbd39972c`. Together, these receipts cover 13
selected cases, not the complete FastAPI error contract:

| Selected cases | Result | Comparison receipt | Input SHA-256 |
| ---: | --- | --- | --- |
| 5 | 5 passed, 0 failed | `257553d9-5be3-41e6-a9d5-fd21903818f6` | `d636f535494bdc1b79fd9bb7d54588495554806b765fda3ee5031ab9b49857eb` |
| 8 | 8 passed, 0 failed | `f40b43b8-88bd-4b53-b070-a581f4f84007` | `4a83a7f4ecbdd8a7a7fc7e9e60f5e50f55dd1367a88cda1361c6b2ad0b048a2e` |

Both receipts declare the previous manifest SHA and the pinned source and
target identities above. The subsequent atlas refresh changed only backlog
acceptance wording, generated atlas bytes, and the manifest's atlas digest; it
did not change API operations, recipes, generated inputs, target code, or binary.
The receipts remain valid for their recorded identities but do not match the
current full-manifest hash, so they are retained as prior-identity evidence and
were not rerun for this metadata-only edit. Generated inputs and results remain
ignored local evidence; reviewed recipes and metadata are committed.

## Earlier receipts retained as historical evidence

The previously recorded `model-extra-request-parameters-upstream` (4/4),
`response-204-bodyless-isolated-upstream` (1/1), `uploadfile-pydantic-contract`
(6/6), and `worker-dispatch` (18/18) receipts targeted FastAPI-RS revision
`f84074ce292f62ece155cc3ba6879e54508475ee`. They remain evidence for those
specific inputs at that earlier target, but are not current-target receipts.
They are not repeated here as proof of the current `e52fba0` target.

The `jsonable-encoder.name-email` case passed 1/1 at target revision
`f5bf63670dd4eb6a45250902a0f963da87542f24` with the prior manifest SHA
`caefe574340ff873c8fb5ac7d8403235bf21d8a42a48872e546d4656018d18f5`. The
first-slice benchmark is recorded separately in
[`docs/benchmarks/2026-10-23-f5bf636.md`](../../benchmarks/2026-10-23-f5bf636.md);
it reports slower latency and throughput than FastAPI for its one direct-ASGI
workload and does not establish broad performance.

## Validation boundary

`make compatibility-atlas-update` and `make metadata-check` passed for this
refresh using the pinned Starlette-RS source commit. `python-facade-check`,
Rust formatting, and Clippy also passed for the private binding change. The
single selected API case above ran because that change touched the native
binding; no other parity cases or unit tests were run. The older
`benchmark-contract-check` record belongs to the `f84074ce` snapshot and does
not replace checks required for future relevant changes.
