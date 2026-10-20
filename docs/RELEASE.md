# Release preparation

This guide covers local preparation for the first public release. It does not
authorize or perform a registry upload, tag, GitHub release, or documentation
deployment.

## Release scope and order

- Publish one Cargo crate: `fastapi-rs`. Keep `fastapi-rs-py` internal.
- Publish one Python wheel for the `fastapi-rs` distribution. Build a source
  distribution only as a local portability-validation input; do not publish or
  upload it. The wheel rebuilt from that source archive is validation output,
  not a second release artifact.
- Keep project guides in repository Markdown and publish the Rust API reference
  through docs.rs when the crate is published. There is no separate static site
  build or deployment workflow yet.
- Publish the exact `starlette-rs` 0.1.0 Cargo dependency before `fastapi-rs`;
  publish `starlette-rs-py` 0.1.0 before the Python package can be installed.
  Check registry ownership and availability before claiming either name. A
  registry 404 does not prove that a name is available.

## Build and inspect local artifacts

Start from a clean release candidate and the exact pinned Starlette-RS source.
Set `STARLETTE_RS_SOURCE` to the Starlette-RS repository root:

```sh
git status --short --branch
test -z "$(git status --porcelain)" || exit 1
git rev-parse HEAD
export STARLETTE_RS_SOURCE=/absolute/path/to/clean/starlette-rs
git -C "$STARLETTE_RS_SOURCE" rev-parse HEAD
export RELEASE_ID="$(git rev-parse --short HEAD)"
make build-python STARLETTE_RS_SOURCE="$STARLETTE_RS_SOURCE"
make release-sdist \
  STARLETTE_RS_SOURCE="$STARLETTE_RS_SOURCE" \
  RELEASE_SDIST_DIR="target/release-sdist-validation-$RELEASE_ID" \
  RELEASE_SDIST_WHEEL_DIR="target/release-sdist-validation-wheels-$RELEASE_ID"
```

`make build-python` produces the candidate wheel under `target/wheels/`.
`make release-sdist` then creates a source archive, validates it, and rebuilds a
wheel from the extracted archive in the two validation directories. Only the
directly built wheel is a planned Python release artifact. Record the source
commit, exact candidate wheel filename, platform tag, and SHA-256; record the
sdist and rebuilt wheel separately as validation evidence:

Both build routes keep the generated CycloneDX Rust dependency SBOM. When the
local Starlette-RS overlay adds Cargo path dependencies, the build helper replaces
their machine-local download URLs with stable Cargo package references, updates
the dependency edges, and regenerates wheel `RECORD`. The wheel checker rejects
local build paths, dangling or duplicate SBOM references, and incorrect `RECORD`
hashes or sizes.

```sh
shasum -a 256 target/release-sdist-validation-"$RELEASE_ID"/* \
  target/release-sdist-validation-wheels-"$RELEASE_ID"/* \
  target/wheels/fastapi_rs-0.1.0-*.whl
```

Before publishing, verify the Rust package without a local path patch, using
the registry-published Starlette-RS dependency:

```sh
cargo package --locked --package fastapi-rs
cargo publish --dry-run --locked --package fastapi-rs
```

When Starlette-RS is not yet published, local archive verification can use a
Cargo patch to its pinned crate directory. That only verifies the source
archive; it is not registry-consumer evidence and must not be used for the
publish command.

Run the repository's artifact notice check on the exact files that will ship:

```sh
make license-artifact-check \
  STARLETTE_RS_SOURCE="$STARLETTE_RS_SOURCE" \
  RELEASE_NOTICE_WHEEL=/absolute/path/to/fastapi_rs-0.1.0-....whl \
  RELEASE_CRATE_DIR=/absolute/path/to/directory/containing/fastapi-rs-0.1.0.crate
```

The check requires the complete FastAPI MIT notice, including Copyright (c)
2018 Sebastián Ramírez, and the applicable third-party notices in each
artifact.

## First-time manual publication commands

Use these only after the candidate is approved, the exact dependencies are
available from their registries, package checks pass, and the release commit
is clean. Publish Starlette-RS first in its own repository.

Cargo requires an initial account token. Enter it through Cargo's prompt, then
dry-run and publish the candidate:

```sh
cargo login
cargo publish --dry-run --locked --package fastapi-rs
cargo publish --locked --package fastapi-rs
```

The first crates.io publication is manual; configure [crates.io Trusted
Publishing](https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html)
for later releases after the crate exists. PyPI supports [Trusted
Publishers](https://docs.pypi.org/trusted-publishers/) for workflow-based
publishing, but this repository does not yet contain a publish workflow.

For PyPI, confirm the `fastapi-rs` project name is available or controlled by
the project account. Check and upload only the directly built candidate wheel;
Twine prompts for credentials when none are configured. Select the single
validated platform-tagged wheel from `target/wheels/`:

```sh
set -- target/wheels/fastapi_rs-0.1.0-*.whl
test "$#" -eq 1 && test -f "$1" || exit 1
uvx --from twine twine check "$1"
uvx --from twine twine upload --repository pypi "$1"
```

Do not upload the source archive or the wheel rebuilt from it; those are local
validation outputs.

Do not put registry tokens in shell history, source files, or command-line
arguments. After each upload, install into a fresh environment from the public
registry and record the resolved dependency versions and artifact hashes.

## Documentation preview

Project documentation is maintained as Markdown in this repository. Preview
the public Rust API locally from a workspace with Starlette-RS checked out at
the pinned commit `4139a72449bf5751e8902fb1c7175ee7f191d338`. The docs build
needs a CPython 3.10 or later interpreter; the pinned build-tools environment
provides CPython 3.12.13:

```sh
make build-tools-prepare
RUSTC_WRAPPER=/usr/bin/env CARGO_NET_OFFLINE=true \
  .venv/bin/python scripts/build_target_extension.py \
    --rustdoc \
    --python "$PWD/.venv-build-tools/bin/python" \
    --starlette-rs-source "$STARLETTE_RS_SOURCE"
open target/doc/fastapi_rs/index.html
```

After publication, [docs.rs automatically builds the API reference for
crates.io releases](https://docs.rs/about/builds). Documentation changes are
released with their Git commit; there is no site deployment command until a
separate hosted site is selected and configured.

## Readiness snapshot (2026-10-20; source candidate 674974e)

The clean candidate was `674974e26feffd9764657ca77bd2f5c17d13cd07`, built
against FastAPI `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` and Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338` (source tree SHA-256
`da4acf9c64ae8df8a9bde0976d1777f5b36d67a6af45c443b0d0f617cad10f48`). These
artifacts are local preparation evidence, not uploaded or tagged releases.

- The direct CPython 3.12.13 macOS arm64 wheel is
  `target/release-wheel-674974e/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`,
  SHA-256 `91d956099c39c1a52841481325a8a4e5eb6e155b9cf7546d9ca47de8d16c8dae`.
  The release-wheel checker verified its `fastapi` facade, single native
  extension, metadata, portable SBOM references, and `RECORD`; the notice
  checker verified the FastAPI MIT attribution, including Copyright (c) 2018
  Sebastián Ramírez, and the pinned third-party notices.
- The validation-only sdist is
  `target/release-sdist-validation-674974e/fastapi_rs-0.1.0.tar.gz`, SHA-256
  `3d19e659129c3e1444f8be724c353f9d1138d6c696ff1ee61db8829afbcc889d`.
  Its validator accepted 202 members and the pinned Starlette-RS source digest.
  The release-profile wheel rebuilt from that archive passed package and notice
  checks; SHA-256
  `dda3d30bce7b158643733c84ad274ebe9670f46aebdd605225b149ede3b519af`. Neither
  the sdist nor the rebuilt wheel is a planned publish artifact. This confirms
  macOS arm64 only.
- Cargo listed 33 package entries, including `Cargo.toml`, `README.md`,
  `LICENSE.md`, `THIRD_PARTY_NOTICES.md`, and `build.rs`. A local
  `fastapi-rs-0.1.0.crate` was created with `--no-verify` and a Cargo patch to
  the pinned Starlette-RS checkout:
  `target/release-crate-674974e/fastapi-rs-0.1.0.crate`, SHA-256
  `47479997a4d8b0b4d1b7ee225793ce254b95fce0f5b9b71e4e7343350534008a`. The
  archive contains 33 files and passed `make license-artifact-check` with the
  direct wheel. An extracted copy passed offline `cargo check --locked` and
  warning-denied `cargo doc --locked --no-deps` using the same local Starlette-RS
  patch. This verifies the archive against the pinned local source, not against
  a crates.io consumer.
- Unpatched `cargo package --locked --offline` from the candidate still fails
  because crates.io has no matching `starlette-rs 0.1.0`. PyPI returned 404 for
  [starlette-rs-py==0.1.0](https://pypi.org/pypi/starlette-rs-py/0.1.0/json)
  and [fastapi-rs==0.1.0](https://pypi.org/pypi/fastapi-rs/0.1.0/json); those
  responses do not establish name ownership or availability. Publish the exact
  Starlette-RS dependencies and verify package ownership and installability
  before publishing FastAPI-RS.
- Warning-denied rustdoc succeeded both through the pinned workspace overlay
  and from the extracted `.crate`. Project guides remain repository Markdown;
  docs.rs is the planned Rust API reference after crate publication. There is
  no static-site deployment workflow. The standard `make build-python` wrapper
  could not initialize its uv cache in this environment, so the wheel builders
  ran directly with the already-prepared locked CPython 3.12.13/Maturin tools.
- The compatibility manifest currently has 7 of 497 required public API
  dispositions supported; 490 remain unresolved. This is not a claim of full
  FastAPI compatibility or release readiness.

No package was uploaded; no tag, GitHub release, or documentation deployment
was created. Remaining external gates are registry availability and name
ownership, broader platform artifacts, and final maintainer approval.
