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
PYO3_PYTHON=.venv-build-tools/bin/python \
  RUSTC_WRAPPER=/usr/bin/env CARGO_NET_OFFLINE=true \
  cargo doc --locked --package fastapi-rs --no-deps
open target/doc/fastapi_rs/index.html
```

After publication, [docs.rs automatically builds the API reference for
crates.io releases](https://docs.rs/about/builds). Documentation changes are
released with their Git commit; there is no site deployment command until a
separate hosted site is selected and configured.

## Readiness snapshot (2026-10-20)

This source snapshot is bound to `main` at
`4a89a968b7729cddd1eaec414b6066820772da97`. The shared checkout has uncommitted
work, so it is not a clean release candidate and no artifact check from that
checkout is claimed here.

- The current manifests declare `fastapi-rs` as the one publishable Cargo
  crate, `fastapi-rs-py` as `publish = false`, and `fastapi-rs` as the Python
  distribution name. The release plan is one Python wheel; the sdist and wheel
  rebuilt from it are validation-only outputs.
- Public registry ownership and package availability are **unknown**. The
  registry probes recorded on 2026-10-19 were against the preceding
  `4aa588d` source revision; those results are historical and must be checked
  again by the release maintainer.
- The most recent source-archive and rebuilt-wheel evidence in
  [LICENSING.md](LICENSING.md#source-archive-evidence-fastapi-rs-010-2026-10-18)
  is from `adae40e` on macOS arm64. The Cargo archive evidence there is from
  `0738588`. These records are historical; none verifies artifacts from
  `4a89a96`.
- The source tree contains the FastAPI MIT notice. Inclusion in a candidate
  wheel and Cargo archive remains **unverified** until
  `make license-artifact-check` is run on those exact files.
- The compatibility atlas at `4a89a96` records 490 unresolved target
  dispositions among 497 source-supported public API entries. This inventory
  is not a claim of complete FastAPI compatibility or release readiness.

No package build, current registry query, upload, tag, GitHub release, or
documentation deployment was performed while refreshing this source snapshot.
Project guides remain in repository Markdown; docs.rs can build the Rust API
reference after the crate is published, and no static-site workflow is
configured.
