# FastAPI-RS

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/appunni-m)

A Rust reimplementation of FastAPI that provides the existing `fastapi` import
surface through a pass-through facade. The initial Rust vertical slice
implements a scoped HTTP request-to-response flow; full FastAPI compatibility
remains in progress, so no overall compatibility claim is made.

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
- Runtime boundary: upstream FastAPI is source-oracle-only and never a runtime
  dependency or import. Python runtime modules contain only native re-exports
  and literal `__all__`, with no functions, branches, loops, or fallback
  behavior. All FastAPI behavior and control flow lives in `fastapi-rs/`.

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
- [Developer-tool dependency profile](docs/DEVELOPER_TOOL_DEPENDENCIES.md)
  records the hash-locked Ruff, uv, JSON Schema, and PyYAML closure separately
  from the target runtime. Use `make developer-tools-prepare` to install it,
  `make developer-tools-inventory-check` to check it offline, and
  `make developer-tools-inventory-update` to resolve and refresh it.
- [Parity and benchmark plan](docs/PARITY_BENCHMARK_PLAN.md) and
  [license analysis](docs/LICENSING.md) define the next contract and release work.
- [Release preparation](docs/RELEASE.md) records local artifact checks, the first
  publication sequence, and current registry blockers.
- FastAPI-derived signature metadata is attributed to original author and MIT
  copyright holder Sebastián Ramírez; the complete required MIT notice is in
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and ships with distributions.

The `fastapi-rs/` crate is the sole FastAPI implementation. `fastapi-rs-py/`
builds its private PyO3 extension and ships the thin `fastapi` facade; it is
binding and packaging glue, not a second implementation. The initial
request/response behavior is implemented in Rust. The isolated target worker
and exact comparator are present, but the operation-level
contract and full public API implementation remain incomplete. Author
input-only workflow recipes in `tests/fixtures/input-recipes/parity/`; run
`make parity-inputs` to materialize ignored JSON before validation or execution.
Recipes contain stimuli only, never expected output. Oracle artifacts under
`parity-results/` are per-run evidence; the atlas and manifest record fixture
scope and runner capability, not pass/fail results.

An earlier OpenAPI response-contract checkpoint passed 214 selected normal
cases and six separate fault contracts; its incremental coverage added 42 Rust
regions. See the
[checkpoint report](docs/atlas/drafts/openapi-validation-response-native-contract-review-2026-10-05.md)
for that run's identity, scope and remaining schema-order gaps.

The current seven-workload suite passes 45/45 selected parity observations
at FastAPI-RS `8eceda6` against FastAPI 0.141.1, Starlette 1.6.0, and pinned
Starlette-RS `4139a724`. FastAPI-RS median and p95 latency were higher in all
seven measured workloads. See the
[current benchmark report](docs/benchmarks/2026-10-19-8eceda6.md) and
[benchmark evidence freshness note](docs/PARITY_BENCHMARK_PLAN.md#benchmark-evidence-freshness).
These selected cases do not establish full API parity or a global performance
claim.

Use `make parity-prepare-oracle` for the core environment and
`make parity-validate` to check source evidence and workflow links. The
`request-multipart` workflow requires the standard environment, which pins
`python-multipart` 0.0.32 while retaining the sole Starlette 1.6.0 contract;
run it with `make parity-prepare-oracle-standard` followed by
`make parity-oracle-standard PARITY_INPUT=tests/fixtures/inputs/parity/request-multipart.json`.
Use `make parity-oracle PARITY_INPUT=...` for core-profile workflows. Do not
interpret the source atlas or foundation manifest as a full support declaration
or parity result.

After `make parity-prepare-oracle` and `make parity-prepare-target`, run
`make parity-first-slice` for the current thirteen-case HTTP parity gate. CI
runs this same identity-checked oracle/target/comparator path. Target
preparation builds the PyO3 extension in Cargo release mode and verifies that
the Python and Rust Starlette-RS dependencies resolve to the same clean pinned
checkout. Per-run results stay under ignored `parity-results/`.

The active version 5 direct Python API lane covers nine `jsonable_encoder`
inputs, observing return values and structural callable signatures, including
reviewed Pydantic field metadata, through isolated workers. Its encoder atlas
compares 61 return probes and two callable outcomes, including exact raised
exception classes/messages and non-finite floats retained in a JSON Pointer
sidecar. Run
`make parity-api-oracle`, `make parity-api-target`, then
`make parity-api-compare SOURCE_RESULT=... TARGET_RESULT=...`; this narrow lane
does not represent full public API parity.

The first correctness-gated performance lane is `make benchmark-first-slice`.
It runs the pinned thirteen-case parity gate, then compares one valid request
through the FastAPI 0.141.1 oracle, release FastAPI-RS facade, and Starlette
1.6.0 plain route control. It measures direct ASGI dispatch without
network/client startup and stores raw, identity-stamped samples under ignored
`benchmark-results/`.
This narrow baseline is not a full FastAPI performance claim.
Choose the neighboring validation-error or chunked-body profile by setting
`BENCHMARK_WORKLOAD=benchmarks/workloads/first-slice-invalid-asgi.yaml` or
`BENCHMARK_WORKLOAD=benchmarks/workloads/first-slice-chunked-asgi.yaml`.

`make benchmark-suite STARLETTE_RS_SOURCE=/path/to/clean/starlette-rs` runs all
seven reviewed workloads sequentially. The selected Starlette-RS checkout must be
clean and match the commit pinned in `metadata.yaml`, so a detached clean
worktree can be used while the sibling development checkout has changes. The
FastAPI-RS checkout must have a clean working tree; its current HEAD is recorded
in each result because its revision is not pinned by the manifest. The suite
summary is written only after every workload has a fresh passing parity gate
and all seven results share source, extension hashes, Python, host, and build
identities. Completed and incomplete suite records, plus per-workload results,
are stored under ignored `benchmark-results/`.

## Workspace layout

- `fastapi-rs/` is the sole FastAPI implementation and integrates the separate
  `starlette-rs` crate.
- `fastapi-rs-py/` builds the private PyO3 extension and thin Python `fastapi`
  facade. Keep Python runtime modules to direct extension re-exports; all
  FastAPI-specific behavior and control flow belongs in `fastapi-rs/`.
- `tests/fixtures/` contains the source inventory, compatibility atlas, and
  input-only workflow definitions. Run `make help` for maintained build and
  quality commands.
