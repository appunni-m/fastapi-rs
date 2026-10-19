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

This snapshot was checked on 2026-10-19 at clean `main` commit
`4aa588dafe5b1e1f7bcdf9b2b28192434fe62c4d`:

- `cargo package --list --locked --package fastapi-rs` lists 33 files,
  including `README.md`, `LICENSE.md`, `THIRD_PARTY_NOTICES.md`, and
  `Cargo.lock`. This is a file-list check only; no current `.crate` archive
  was built. The release audit's missing README/license findings are false
  positives for these parent-relative manifest paths; Cargo's package list
  confirms both files are included.
- `cargo info fastapi-rs@0.1.0 --registry crates-io` and
  `cargo info starlette-rs@0.1.0 --registry crates-io` both report that the
  exact crate version is not in the registry. PyPI's JSON endpoints for
  `fastapi-rs` and `starlette-rs-py` returned 404. A missing result does not
  prove that a name is available or that this project controls it; verify
  ownership in the maintainer accounts.
- The configured sibling checkout is Starlette-RS commit
  `2da349cf90bb5b6f47aaf9b3bd61759e0b3d450c`, on a different branch with local
  modifications. It is not the pinned source `4139a72449bf5751e8902fb1c7175ee7f191d338`
  and must not be used to build release artifacts. Keep that checkout intact;
  prepare a separate clean pinned source before the next local build.
- The pinned build-tools environment uses CPython 3.12.13. The default shell
  `python3` is 3.9.6 and is not the release builder.
- Earlier local sdist, wheel, crate archive, notice, and rustdoc evidence was
  produced at `b5987b4`. It is historical and does not verify current HEAD.

No current release artifact was built, no registry upload or tag was created,
and no GitHub release or documentation deployment occurred. The repository
keeps project documentation in Markdown; docs.rs can publish the Rust API
reference after the crate is available, and there is no separate static-site
workflow. FastAPI-RS compatibility remains incomplete: the current
[compatibility atlas](COMPATIBILITY_ATLAS.md) reports 490 unresolved target
dispositions among 497 source-supported public API entries. Do not describe
this candidate as a complete FastAPI replacement or as release-ready until the
compatibility scope and release gates are resolved.
