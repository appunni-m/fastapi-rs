# FastAPI-RS

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/appunni-m)

A Rust reimplementation of FastAPI that provides the existing `fastapi` import
surface through a pass-through facade. The initial Rust vertical slice
implements a scoped HTTP request-to-response flow; full FastAPI compatibility
remains in progress, so no overall compatibility claim is made.

**Status: alpha.** A public `fastapi-rs` release and consumer installation have
not been verified. Registry ownership and availability remain unknown, so do
not rely on `pip install fastapi-rs` yet. The release plan is one public
`fastapi-rs` Cargo crate and one Python wheel; the source archive is built only
for portability validation, and `fastapi-rs-py` remains an internal binding
crate.

## Availability and first use

There is no verified public install command yet. To check the facade from a
source checkout, use CPython 3.12.13, `uv`, the Rust toolchain in
[`rust-toolchain.toml`](https://github.com/appunni-m/fastapi-rs/blob/main/rust-toolchain.toml),
and a clean Starlette-RS checkout at the commit pinned in `metadata.yaml`:

On a fresh checkout, create and activate a local helper environment, then
prepare the target environment:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --requirement requirements-dev.txt
STARLETTE_RS_SOURCE=/absolute/path/to/clean/starlette-rs make parity-prepare-target
.venv-target/bin/python -c 'import fastapi'
```

The second command is a facade import smoke check; it does not establish route
or API compatibility. The current public implementation scope remains the
scoped HTTP slice described below. See
[release preparation](https://github.com/appunni-m/fastapi-rs/blob/main/docs/RELEASE.md)
for artifact checks and publication prerequisites.

## Compatibility target

- Oracle baseline: FastAPI 0.157.0, pinned to upstream commit
  `386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`.
- Starlette contract: Starlette 1.6.0 at upstream commit
  `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`; this is the sole oracle, and
  Starlette-RS is expected to replace that contract.
- FastAPI 0.157.0's upstream `uv.lock` records Starlette 1.7.0. That version is
  kept only as dependency-audit provenance and is not an oracle or target profile.
- Runtime baseline: CPython 3.10 and later, matching that FastAPI release's
  declared minimum.
- Starlette integration: use the separately developed Starlette-RS as a full
  Starlette replacement. FastAPI-RS work does not implement Starlette.
- Validation: keep Pydantic's public model API compatible. Pydantic v2 uses
  Python for model definition and Rust `pydantic-core` for validation and
  serialization; dependency reuse is the working assumption.
- Planned Python distribution: `fastapi-rs`, exposing `import fastapi`; its
  installability remains unverified until its dependencies are published and
  a consumer install is checked.
- Runtime boundary: upstream FastAPI is source-oracle-only and never a runtime
  dependency or import. Python runtime modules contain only native re-exports
  and literal `__all__`, with no functions, branches, loops, or fallback
  behavior. All FastAPI behavior and control flow lives in `fastapi-rs/`.

## Project rules and research

- [AGENTS.md](https://github.com/appunni-m/fastapi-rs/blob/main/AGENTS.md) keeps the core contract, parity, benchmark, and license
  rules compact.
- [Project scope and depth](https://github.com/appunni-m/fastapi-rs/blob/main/docs/PROJECT_SCOPE.md) records the confirmed scale,
  sequencing, and rough effort ranges.
- [API scope](https://github.com/appunni-m/fastapi-rs/blob/main/docs/API_SCOPE.md) and the generated
  [`api-inventory.json`](https://github.com/appunni-m/fastapi-rs/blob/main/tests/fixtures/api-inventory.json) map source APIs;
  regenerate the JSON with `scripts/inventory_fastapi_api.py`.
- [`metadata.yaml`](https://github.com/appunni-m/fastapi-rs/blob/main/metadata.yaml) is the compact human-maintained API source
  authority. It pins the source identities and names generated inventory/atlas
  pointers; `make metadata-check` reconciles it against those artifacts and the
  sibling Starlette-RS contract without duplicating that catalog.
- The active [`manifest.yaml`](https://github.com/appunni-m/fastapi-rs/blob/main/tests/fixtures/manifest.yaml) contains the
  generated per-symbol source/runtime contract for source-supported APIs. Use
  `make api-contract-update` after refreshing its inputs and
  `make api-contract-check` to verify freshness.
- [`runtime-api-surface-core.json`](https://github.com/appunni-m/fastapi-rs/blob/main/tests/fixtures/runtime-api-surface-core.json)
  and [`runtime-api-surface-standard.json`](https://github.com/appunni-m/fastapi-rs/blob/main/tests/fixtures/runtime-api-surface-standard.json)
  reflect the pinned CPython API namespaces, identity aliases, and Pydantic
  OpenAPI models. Prepare the core and standard environments, then run
  `make parity-api-runtime`.
- [Compatibility atlas](https://github.com/appunni-m/fastapi-rs/blob/main/docs/COMPATIBILITY_ATLAS.md) and the generated
  [`fixture-backlog.json`](https://github.com/appunni-m/fastapi-rs/blob/main/tests/fixtures/fixture-backlog.json) map API evidence,
  upstream test modules, documentation pages/examples, and Starlette-RS ownership.
  [`observation-selectors.json`](https://github.com/appunni-m/fastapi-rs/blob/main/tests/fixtures/observation-selectors.json) defines
  each exact output projection and its current workflow support.
- [Dependency atlas](https://github.com/appunni-m/fastapi-rs/blob/main/docs/dependency-atlas.md) explains the recursive runtime,
  optional-feature, and development closures, including package purpose,
  language/native components, and license evidence. The [dependency summary](https://github.com/appunni-m/fastapi-rs/blob/main/docs/DEPENDENCIES.md)
  and [full lock graph](https://github.com/appunni-m/fastapi-rs/blob/main/docs/DEPENDENCY_GRAPH.md) provide compact and exhaustive
  views.
- [Developer-tool dependency profile](https://github.com/appunni-m/fastapi-rs/blob/main/docs/DEVELOPER_TOOL_DEPENDENCIES.md)
  records the hash-locked Ruff, uv, JSON Schema, and PyYAML closure separately
  from the target runtime. Use `make developer-tools-prepare` to install it,
  `make developer-tools-inventory-check` to check it offline, and
  `make developer-tools-inventory-update` to resolve and refresh it.
- [Parity and benchmark plan](https://github.com/appunni-m/fastapi-rs/blob/main/docs/PARITY_BENCHMARK_PLAN.md) and
  [license analysis](https://github.com/appunni-m/fastapi-rs/blob/main/docs/LICENSING.md) define the next contract and release work.
- [Release preparation](https://github.com/appunni-m/fastapi-rs/blob/main/docs/RELEASE.md)
  records the one-crate/one-wheel plan, sdist validation, and release evidence;
  registry ownership and availability must be rechecked before publication.
- FastAPI-derived signature metadata retains the original MIT attribution
  `Copyright (c) 2018 Sebastián Ramírez`. The complete required notice is in
  [THIRD_PARTY_NOTICES.md](https://github.com/appunni-m/fastapi-rs/blob/main/THIRD_PARTY_NOTICES.md);
  inclusion in a release artifact must be verified on that exact artifact.

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

The `fastapi-rs` crate also exposes an initial Python-free Rust service surface
at `fastapi_rs::native`. It registers typed Rust handlers on Starlette-RS's
server-neutral native service and provides bounded JSON-body, JSON-response,
and streaming-response helpers. The default feature graph excludes PyO3; the
`python` feature enables the implementation used by `fastapi-rs-py`. This
native route slice does not implement Python FastAPI's complete validation,
dependency-injection, Pydantic, or OpenAPI contracts, and it does not claim
parity with the Python API. CI runs
`cargo check --package fastapi-rs --no-default-features --locked` and rejects
PyO3 packages from that resolved normal/build dependency graph.

An earlier OpenAPI response-contract checkpoint passed 214 selected normal
cases and six separate fault contracts; its incremental coverage added 42 Rust
regions. See the
[checkpoint report](https://github.com/appunni-m/fastapi-rs/blob/main/docs/atlas/drafts/openapi-validation-response-native-contract-review-2026-10-05.md)
for that run's identity, scope and remaining schema-order gaps.

The latest recorded complete seven-workload suite on the previous FastAPI
0.141.1 oracle passed 45/45 selected parity observations at FastAPI-RS
`8c7eb97`; it binds an earlier manifest and is historical to the current
0.157.0 baseline. A single workload was subsequently refreshed at main
`57aec8c` against that previous oracle: the large-response-model case passed
1/1 parity observations, with FastAPI-RS median/p95 latency at
1.123×/1.224× FastAPI on this host. That single workload does not replace the
full suite or establish a global performance claim. See the
[single-workload report](https://github.com/appunni-m/fastapi-rs/blob/main/docs/benchmarks/2026-10-21-57aec8c.md),
[previous-baseline suite report](https://github.com/appunni-m/fastapi-rs/blob/main/docs/benchmarks/2026-10-21-8c7eb97.md), and
[benchmark evidence freshness note](https://github.com/appunni-m/fastapi-rs/blob/main/docs/PARITY_BENCHMARK_PLAN.md#benchmark-evidence-freshness).
These measurements do not establish parity or performance for FastAPI 0.157.0.

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
`make parity-first-slice` for the current fourteen-case HTTP parity gate. CI
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
It runs the pinned fourteen-case parity gate, then compares one valid request
through the FastAPI 0.157.0 oracle, release FastAPI-RS facade, and Starlette
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

## Contributing, security, and license

See the [contribution guide](https://github.com/appunni-m/fastapi-rs/blob/main/CONTRIBUTING.md)
for the pinned development environment and focused validation workflow. For
vulnerabilities, follow the [security policy](https://github.com/appunni-m/fastapi-rs/blob/main/SECURITY.md)
and keep unpatched details private. Original FastAPI-RS code
is MIT-licensed under [LICENSE.md](https://github.com/appunni-m/fastapi-rs/blob/main/LICENSE.md),
with third-party attributions in
[THIRD_PARTY_NOTICES.md](https://github.com/appunni-m/fastapi-rs/blob/main/THIRD_PARTY_NOTICES.md).
