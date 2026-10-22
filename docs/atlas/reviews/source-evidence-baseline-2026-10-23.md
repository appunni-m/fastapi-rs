# FastAPI 0.157.0 source-evidence revalidation

Review date: 2026-10-23

## Active identities

The active contract is FastAPI 0.157.0 at `386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`, Starlette 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at `4139a72449bf5751e8902fb1c7175ee7f191d338`. The source authority also pins Pydantic 2.13.5 and pydantic-core 2.46.5, with CPython 3.12.13 as the oracle runtime. `make metadata-check STARLETTE_RS_SOURCE=/private/tmp/starlette-rs-4139` confirmed these identities.

## Atlas and fixture review

The current generated atlas records 1,831 API candidates: 493 supported, 1,279 private/internal, and 59 uncertain. It maps all 472 in-scope upstream test modules to independent workflows and records 55 module exclusions. Of 156 documentation pages, 106 have reviewed workflow links and 50 are excluded; no candidate page, test module, or Python documentation example remains pending behavior review. The atlas also records 558 reviewed documentation section mappings, 335 linked documentation examples, and 913 fixture designs. The remaining uncertain APIs and unimplemented operation targets are explicit work, not support claims.

Active source mappings and recipes were checked against the 0.157.0 checkout. Any retained 0.141.1 references are labeled as historical provenance. The documented-page mapping for the bodyless 204 workflow now flows through the same reviewed wave-L map used by both the atlas and materialized index, including its construction selectors. Generated inputs, parity results, and their historical receipts remain local evidence; the recipes, mappings, manifest, and atlas sources are the reviewed artifacts.

The inventory's deprecation scan now assigns parameter annotations and warning calls to their owning methods instead of duplicating them under the parent class. The refreshed atlas records 23 deprecation-bearing symbols, including `FastAPI.on_event`, `APIRouter.on_event`, and the parameter constructors. Class-level deprecations remain on `UJSONResponse` and `ORJSONResponse`. Warning categories and runtime timing remain behavior questions; the source ledger is evidence, not a claim that those warning cases have passed parity.

The new `model-extra-request-parameters-upstream` input exercises FastAPI's default header underscore conversion using a raw `x_user_id` header. It caught a target mismatch: the request correctly failed validation, but FastAPI-RS reported the Python field name `x_user_id` in the error location while FastAPI reports the normalized header alias `x-user-id`. FastAPI-RS now applies that alias translation to Pydantic header-model error locations when `loc_by_alias` and underscore conversion are enabled. The four-case workflow then matched exactly.

## Focused parity evidence

The current identity-checked workflows matched against FastAPI 0.157.0:

- `model-extra-request-parameters-upstream`: 4/4 cases, including the new header alias case.
- `response-204-bodyless-isolated-upstream`: 1/1 case.
- `uploadfile-pydantic-contract`: 6/6 cases, including the `__format__` case.
- `worker-dispatch`: 18/18 cases.

The target result identity for these runs records Starlette-RS `4139a72449bf5751e8902fb1c7175ee7f191d338`, source-tree SHA-256 `507328420006b3ddf254875388486809b2acb325559f77ad87ec79574850818b`, and native binary SHA-256 `77755183189547b31b00e0944d1dd85bacfb68fa30d02b785e729e04095b2032`. The target revision was `f84074ce292f62ece155cc3ba6879e54508475ee` with this reviewed working-tree change.

`request-forms` remains mapped to the separate `standard-multipart` profile. Its recipe edits update provenance notes without changing requests or observations. That target profile is not provisioned in this checkout, and network access prevented installing it, so no new parity receipt is claimed for that workflow.

## Validation

- `make compatibility-atlas-update STARLETTE_RS_SOURCE=/private/tmp/starlette-rs-4139` completed, regenerated the atlas, fixture index, API contract, and passed parity validation.
- `make metadata-check STARLETTE_RS_SOURCE=/private/tmp/starlette-rs-4139` passed.
- `make api-contract-check STARLETTE_RS_SOURCE=/private/tmp/starlette-rs-4139` passed.
- `make benchmark-contract-check STARLETTE_RS_SOURCE=/private/tmp/starlette-rs-4139` passed for all seven declarations. It structurally checked and retained one 0.141.1 suite as historical; no timing benchmark was run for 0.157.0.
- `RUSTC_WRAPPER=/usr/bin/env make clippy STARLETTE_RS_SOURCE=/private/tmp/starlette-rs-4139` passed, including the Rust policy check; `cargo fmt --package fastapi-rs --package fastapi-rs-py` passed.
- The `make fmt` wrapper could not prepare its hash-locked developer-tool environment because the package index was unreachable. Rust formatting was run directly. Target profile preparation had the same network limitation; the checked-in Cargo overlay and offline release build were used to rebuild the native extension before parity runs.

No pytest, unittest, Cargo test, or broad parity campaign was run.
