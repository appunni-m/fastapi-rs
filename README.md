# FastAPI-RS

A Rust reimplementation of FastAPI that provides the existing `fastapi` import
surface through a pass-through facade. The initial native vertical slice
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
  behavior. All FastAPI behavior and control flow lives in Rust.

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

The public `fastapi` package is a thin direct re-export from the native module;
the initial request/response behavior is implemented in Rust. The isolated
target worker and exact comparator are present, but the operation-level
contract and full public API implementation remain incomplete. Author
input-only workflow recipes in `tests/fixtures/input-recipes/parity/`; run
`make parity-inputs` to materialize ignored JSON before validation or execution.
Recipes contain stimuli only, never expected output. Oracle artifacts under
`parity-results/` are per-run evidence; the atlas and manifest record fixture
scope and runner capability, not pass/fail results.

The latest measured native checkpoint retains additional response fields at
attachment and independently in each included context. Its selected regression
passed 203 normal cases and six separate fault contracts. Fresh incremental
coverage added 105 Rust regions; all seven existing benchmark workloads completed
with mixed latency results. See the [measured contract and timings](docs/atlas/drafts/additional-response-field-native-contract-review-2026-10-05.md)
for exact scopes, identities and remaining gaps. These selected results do not
establish full API parity.

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
`make parity-first-slice` for the current twelve-case HTTP parity gate. CI runs
this same identity-checked oracle/target/comparator path. Target preparation
builds the PyO3 extension in Cargo release mode and verifies that the Python
and Rust Starlette-RS dependencies resolve to the same clean pinned checkout.
Per-run results stay under ignored `parity-results/`.

The legacy version 1 direct Python API lane covers nine `jsonable_encoder`
inputs, observing return values and signatures through isolated workers. The
version 2 encoder atlas wave compares 61 return probes and two callable
outcomes, including exact raised exception classes/messages and non-finite
floats retained in a JSON Pointer sidecar. Run
`make parity-api-oracle`, `make parity-api-target`, then
`make parity-api-compare SOURCE_RESULT=... TARGET_RESULT=...`; this narrow lane
does not represent full public API parity.

The first correctness-gated performance lane is `make benchmark-first-slice`.
It runs the pinned twelve-case parity gate, then compares one valid request through
the FastAPI 0.141.1 oracle, release FastAPI-RS facade, and Starlette 1.6.0 plain
route control. It measures direct ASGI dispatch without network/client startup
and stores raw, identity-stamped samples under ignored `benchmark-results/`.
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
and all seven results share source, native binary, Python, host, and build
identities. Completed and incomplete suite records, plus per-workload results,
are stored under ignored `benchmark-results/`.

## Workspace layout

- `fastapi-rs/` owns Rust implementation behavior and integrates the separate
  `starlette-rs` crate.
- `fastapi-rs-py/` owns the private PyO3 extension and thin Python `fastapi`
  facade. Keep Python runtime modules to direct native re-exports; place all
  FastAPI-specific behavior and control flow in `fastapi-rs/`.
- `tests/fixtures/` contains the source inventory, compatibility atlas, and
  input-only workflow definitions. Run `make help` for maintained build and
  quality commands.
