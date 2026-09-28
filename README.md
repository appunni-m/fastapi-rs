# FastAPI-RS

A Rust and Python reimplementation of FastAPI, intended to provide the existing
`fastapi` Python import surface as a drop-in replacement. The Rust workspace
and private PyO3 binding now build, but the public `fastapi` package and its
behavior are not implemented. No compatibility or parity claim is made.

## Compatibility target

- Oracle baseline: FastAPI 0.141.1, pinned to upstream commit
  `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette contract: Starlette 1.6.0 at upstream commit
  `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`; this is the sole oracle, and
  Starlette-RS is expected to replace that contract.
- FastAPI's upstream `uv.lock` records Starlette 1.3.1; that version is kept
  only as dependency-audit provenance and is not an oracle or target profile.
- Runtime baseline: CPython 3.10 and later, matching that FastAPI release's
  declared minimum.
- Starlette integration: use the separately developed Starlette-RS as a full
  Starlette replacement. FastAPI-RS work does not implement Starlette.
- Validation: keep Pydantic's public model API compatible. Pydantic v2 uses
  Python for model definition and Rust `pydantic-core` for validation and
  serialization; dependency reuse is the working assumption.
- Public package: install as `fastapi-rs`, expose `import fastapi`, and keep
  implementation bindings private. The package/distribution naming will be
  checked before release.

## Project rules and research

- [AGENTS.md](AGENTS.md) keeps the core contract, parity, benchmark, and license
  rules compact.
- [Project scope and depth](docs/PROJECT_SCOPE.md) records the confirmed scale,
  sequencing, and rough effort ranges.
- [API scope](docs/API_SCOPE.md) and the generated
  [`api-inventory.json`](tests/fixtures/api-inventory.json) map source APIs;
  regenerate the JSON with `scripts/inventory_fastapi_api.py`.
- [`metadata.yaml`](metadata.yaml) is the compact human-maintained API source
  authority. It pins the source identities and names generated inventory/atlas
  pointers; `make metadata-check` reconciles it against those artifacts and the
  sibling Starlette-RS contract without duplicating that catalog.
- The active [`manifest.yaml`](tests/fixtures/manifest.yaml) contains the
  generated per-symbol source/runtime contract for source-supported APIs. Use
  `make api-contract-update` after refreshing its inputs and
  `make api-contract-check` to verify freshness.
- [`runtime-api-surface-core.json`](tests/fixtures/runtime-api-surface-core.json)
  and [`runtime-api-surface-standard.json`](tests/fixtures/runtime-api-surface-standard.json)
  reflect the pinned CPython API namespaces, identity aliases, and Pydantic
  OpenAPI models. Prepare the core and standard environments, then run
  `make parity-api-runtime`.
- [Compatibility atlas](docs/COMPATIBILITY_ATLAS.md) and the generated
  [`fixture-backlog.json`](tests/fixtures/fixture-backlog.json) map API evidence,
  upstream test modules, documentation pages/examples, and Starlette-RS ownership.
  [`observation-selectors.json`](tests/fixtures/observation-selectors.json) defines
  each exact output projection and its current workflow support.
- [Dependency atlas](docs/dependency-atlas.md) explains the recursive runtime,
  optional-feature, and development closures, including package purpose,
  language/native components, and license evidence. The [dependency summary](docs/DEPENDENCIES.md)
  and [full lock graph](docs/DEPENDENCY_GRAPH.md) provide compact and exhaustive
  views.
- [Parity and benchmark plan](docs/PARITY_BENCHMARK_PLAN.md) and
  [license analysis](docs/LICENSING.md) define the next contract and release work.

The public `fastapi` implementation and complete operation-level contract are
not implemented. The isolated target worker and exact comparator are present,
but target execution stops until the public facade exists; no source/target
comparison has run against two live products. Author input-only workflow
recipes in `tests/fixtures/input-recipes/parity/`; run
`make parity-inputs` to materialize ignored JSON before validation or execution.
Recipes contain stimuli only, never expected output. Oracle artifacts under
`parity-results/` are source observations rather than parity evidence.

Use `make parity-prepare-oracle` for the core environment and
`make parity-validate` to check source evidence and workflow links. The
`request-multipart` workflow requires the standard environment, which pins
`python-multipart` 0.0.32 while retaining the sole Starlette 1.6.0 contract;
run it with `make parity-prepare-oracle-standard` followed by
`make parity-oracle-standard PARITY_INPUT=tests/fixtures/inputs/parity/request-multipart.json`.
Use `make parity-oracle PARITY_INPUT=...` for core-profile workflows. Do not
interpret the source atlas or foundation manifest as a full support declaration
or parity result.

## Workspace layout

- `fastapi-rs/` owns Rust implementation behavior and integrates the separate
  `starlette-rs` crate.
- `fastapi-rs-py/` owns the private PyO3 extension and will expose the thin
  Python `fastapi` facade after its operation contract is complete.
- `tests/fixtures/` contains the source inventory, compatibility atlas, and
  input-only workflow definitions. Run `make help` for maintained build and
  quality commands.
