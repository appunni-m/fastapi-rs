# Release preparation

This guide covers local preparation for the first public release. It does not
authorize or perform a registry upload, tag, GitHub release, or documentation
deployment.

## Release scope and order

- Publish one Cargo crate: `fastapi-rs`. Keep `fastapi-rs-py` internal.
- Publish the `fastapi-rs` Python distribution as a wheel and source archive.
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
export STARLETTE_RS_SOURCE=/absolute/path/to/starlette-rs
git -C "$STARLETTE_RS_SOURCE" rev-parse HEAD
export RELEASE_ID="$(git rev-parse --short HEAD)"
make release-sdist \
  STARLETTE_RS_SOURCE="$STARLETTE_RS_SOURCE" \
  RELEASE_SDIST_DIR="target/release-sdist-$RELEASE_ID" \
  RELEASE_SDIST_WHEEL_DIR="target/release-sdist-wheels-$RELEASE_ID"
```

The target is built from the sdist and places the source archive and validated
wheel in the two selected directories. Record the commit, filenames, platform
tags, and SHA-256 for each artifact:

```sh
shasum -a 256 target/release-sdist-"$RELEASE_ID"/* \
  target/release-sdist-wheels-"$RELEASE_ID"/*
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
the project account. Check and upload the validated source archive and wheel;
Twine prompts for credentials when none are configured:

```sh
uvx --from twine twine check \
  target/release-sdist-"$RELEASE_ID"/fastapi_rs-0.1.0.tar.gz \
  target/release-sdist-wheels-"$RELEASE_ID"/*.whl
uvx --from twine twine upload --repository pypi \
  target/release-sdist-"$RELEASE_ID"/fastapi_rs-0.1.0.tar.gz \
  target/release-sdist-wheels-"$RELEASE_ID"/*.whl
```

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
PYO3_PYTHON=.venv-build-tools/bin/python \
  RUSTC_WRAPPER=/usr/bin/env CARGO_NET_OFFLINE=true \
  cargo doc --locked --package fastapi-rs --no-deps
open target/doc/fastapi_rs/index.html
```

After publication, [docs.rs automatically builds the API reference for
crates.io releases](https://docs.rs/about/builds). Documentation changes are
released with their Git commit; there is no site deployment command until a
separate hosted site is selected and configured.

## Current readiness snapshot

The local 0.1.0 artifact checks were built from clean main `bfbfe69`; the
wheel was macOS arm64 only. The source archive, rebuilt abi3 wheel, Cargo
archive, and license checks passed, and rustdoc built from the extracted
Cargo archive against the exact pinned Starlette-RS source. These artifacts
precede this release-guide change and must be rebuilt from the final release
commit. The checks do not establish cross-platform support or public registry
installability. The required Starlette-RS registry packages were not publicly
resolvable during this preparation, project-name ownership still needs
confirmation, and a release/publishing workflow is not configured. FastAPI-RS
compatibility remains incomplete as described in the README.
