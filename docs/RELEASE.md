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

Local 0.1.0 artifacts were rebuilt from clean main `b5987b4` on 2026-10-19
against Starlette-RS `4139a72449bf5751e8902fb1c7175ee7f191d338`:

- The sdist validator accepted 202 files; SHA-256:
  `02cc2f2918aad87672ea5e120a881db7024013e9e9ba2309483d6380105168da`.
- The extracted sdist rebuilt and passed the wheel validator for the
  `cp310-abi3-macosx_11_0_arm64` wheel; SHA-256:
  `00fd5b43216a767a397b4d370b1f22526358f21a621a46c970670aeefc9af64b`.
- Cargo packaged and verified 32 files (259.1 KiB compressed) in an isolated
  copy with a local patch to the exact pinned Starlette-RS source; SHA-256:
  `aa6caf1c9cdfb0d9e52688f7a417165d09c3f19cf7d18374ce67e8e9c8f2a62c`.
- Twine metadata checks, `make license-artifact-check`, and rustdoc with
  warnings denied from the extracted Cargo archive passed.

These checks prove local artifact construction only. The wheel evidence covers
macOS arm64; other wheel platforms remain unverified. Current registry queries
found no published `fastapi-rs` or `starlette-rs` 0.1.0 crate, and PyPI returned
404 for `fastapi-rs` and `starlette-rs-py`. Those responses do not establish
project-name ownership or availability. Verify ownership in the maintainer
accounts and publish the Starlette-RS dependencies before attempting the
FastAPI-RS artifacts. No registry upload, tag, GitHub release, or documentation
deployment has occurred. Project docs remain repository Markdown, with the
Rust API reference built by docs.rs after crate publication; there is no
separate static-site workflow. FastAPI-RS compatibility remains incomplete:
497 public API target dispositions are unresolved, as described in the README
and compatibility atlas.
