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

## Readiness snapshot (2026-10-21; source candidate 9b66f3c)

This historical 2026-10-21 snapshot used the FastAPI 0.141.1 source pin. The
clean `main` candidate was `9b66f3c5ef5b53a9b846c43059d119fffba9bc75`, built
against FastAPI 0.141.1 at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` and Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338` (source tree SHA-256
`da4acf9c64ae8df8a9bde0976d1777f5b36d67a6af45c443b0d0f617cad10f48`). These
artifacts are local preparation evidence, not uploaded or tagged releases.

- The direct CPython 3.12.13 macOS arm64 wheel is
  `target/release-wheel-9b66f3c/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`,
  SHA-256 `64e65004fe9b6a49a19a94e3c061e4a3ed962cb4451e43cc3c51690e03a1cfff`.
  The release-wheel checker verified the `fastapi` facade, single native
  extension, metadata, portable SBOM references, and `RECORD`.
- The validation-only sdist is
  `target/release-sdist-validation-9b66f3c/fastapi_rs-0.1.0.tar.gz`, SHA-256
  `18484f7c19009eda41484e2b44bca3e9280e706438c19a1e666aa55d75fd7b91`.
  Its validator accepted 203 members and the pinned Starlette-RS source digest.
  The release-profile wheel rebuilt from that archive passed package checks at
  `target/release-sdist-validation-wheels-9b66f3c/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`,
  SHA-256 `e6c6faaff0de9695f9570a14244bcbb0787270d1c4ba52afd5c77a660c3ba725`.
  Neither artifact is planned for publication. Wheel validation covers macOS
  arm64 only.
- The local Cargo archive is
  `target/release-crate-build-9b66f3c/package/fastapi-rs-0.1.0.crate`, SHA-256
  `85ad1a4cabf649f93a32f07888dfd01cea76a55dc795757645629f1832403e7c`. Cargo
  packaged 33 files and its package verification compiled against the exact
  pinned Starlette-RS checkout. The extracted archive also passed
  `cargo +1.85.0 check --offline --locked` against that source. It includes
  `README.md`, `LICENSE.md`, and `THIRD_PARTY_NOTICES.md`. This verifies the
  source archive against the local pinned source, not a crates.io consumer. The
  published dependency path still needs a registry dry run after Starlette-RS
  is available.
- `make license-artifact-check` passed on the direct wheel and Cargo archive.
  It verified the complete FastAPI MIT attribution, including Copyright (c)
  2018 Sebastián Ramírez, and the pinned third-party notices. Rustdoc succeeded
  through the pinned workspace overlay and generated
  `target/doc/fastapi_rs/index.html`.
- The compatibility manifest currently has 29 supported and 473 unresolved
  target dispositions out of 502 source-supported public API entries. This is
  not full FastAPI compatibility or a direct replacement readiness claim. The
  local environment did not have Twine installed, so `twine check` remains
  unverified.
- Project guides remain repository Markdown; docs.rs is the planned Rust API
  reference after crate publication. There is no static-site deployment
  workflow. PyPI returned 404 for
  [starlette-rs-py==0.1.0](https://pypi.org/pypi/starlette-rs-py/0.1.0/json)
  and [fastapi-rs==0.1.0](https://pypi.org/pypi/fastapi-rs/0.1.0/json); those
  responses do not establish name ownership or availability. Confirm registry
  publication and project ownership before publishing.

No package was uploaded; no tag, GitHub release, or documentation deployment
was created. Remaining gates are registry dependency publication and ownership,
broader platform artifacts, a Twine metadata check, and final maintainer
approval.
