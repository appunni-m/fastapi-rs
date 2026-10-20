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

## Readiness snapshot (2026-10-20)

The clean validation build used commit `e483e93` from a detached local clone.
The shared checkout still contains uncommitted parity changes. These artifacts
are validation evidence for that exact source commit, not uploaded or tagged
release files.

- The current manifests declare `fastapi-rs` as the one publishable Cargo
  crate, `fastapi-rs-py` as `publish = false`, and `fastapi-rs` as the Python
  distribution name. The release plan is one Python wheel; the sdist and wheel
  rebuilt from it are validation-only outputs.
- On 2026-10-20, `cargo info starlette-rs@0.1.0 --registry crates-io` could not
  find the required dependency version. PyPI returned 404 for
  [`starlette-rs-py==0.1.0`](https://pypi.org/pypi/starlette-rs-py/0.1.0/json)
  and [`fastapi-rs==0.1.0`](https://pypi.org/pypi/fastapi-rs/0.1.0/json). These
  responses do not establish registry-name ownership or availability. Release
  the exact Starlette-RS dependencies first, then recheck the names and
  versions before publishing FastAPI-RS.
- On 2026-10-20, the direct CPython 3.12.13 macOS arm64 build from clean commit
  `e483e93` produced
  `fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`, SHA-256
  `e0b1c263ed161995ff5973d4bd04787310429a276f57fcb445efc990337bb693`. The
  package checker verified its facade, native extension, metadata, SBOM
  portability, SBOM references, and every `RECORD` hash and size. The notice
  checker verified the wheel against FastAPI `95f8322` and Starlette-RS
  `4139a724` and confirmed the Sebastián Ramírez MIT attribution.
- The same clean commit produced a validation-only source archive with SHA-256
  `01ea625cbe4e373c722ca1a4838be4aafada6f5202ad9cd6bb9143dd452b7b37`, 202
  members, and the pinned Starlette-RS tree digest. Its extracted source rebuilt
  the same macOS arm64 wheel tag with SHA-256
  `4e5f51add803d6f67adcf2c9f7e2978469c533ab8704b0d7125d5213b33b120a`. Both
  wheels passed package and notice checks. This remains one platform only.
- `cargo package --list --locked --package fastapi-rs` listed the intended crate
  files from clean commit `e483e93`, including README, LICENSE, and third-party
  notices. No `.crate` archive or registry-consumer check was produced: the
  required `starlette-rs 0.1.0` is not available from crates.io, and the
  sandbox could not resolve crates.io during the package attempt. Run
  `make license-artifact-check` against the exact crate archive once that
  dependency is published and the archive is built from a clean candidate.
- The registry probes still do not establish release name ownership:
  `cargo info starlette-rs@0.1.0 --registry crates-io` did not find the crate;
  PyPI returned 404 for [`starlette-rs-py==0.1.0`](https://pypi.org/pypi/starlette-rs-py/0.1.0/json)
  and [`fastapi-rs==0.1.0`](https://pypi.org/pypi/fastapi-rs/0.1.0/json). Release
  and verify the exact Starlette-RS packages first, then verify ownership and
  installability before publishing FastAPI-RS.
- `cargo doc --locked --package fastapi-rs --no-deps` succeeded from clean
  commit `e483e93` against the pinned Starlette-RS source. Documentation remains
  repository Markdown with docs.rs as the planned Rust API reference; no
  static-site or package-publish workflow is configured.
- The manifest requires dispositions for 497 source-supported public API
  entries; 7 are supported and 490 remain unresolved. This is not a claim of
  complete FastAPI compatibility or release readiness.

No package was uploaded; no tag, GitHub release, or documentation deployment
was created. Release still requires a clean candidate, the Starlette-RS registry
dependencies, a publishable Cargo archive, platform coverage, and final
maintainer approval.
