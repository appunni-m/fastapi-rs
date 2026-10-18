# Licensing

## Project license

FastAPI-RS currently declares **MIT** for its independently written code. The
license text is in [`LICENSE.md`](../LICENSE.md), and MIT is declared in the
Cargo workspace and Python package metadata. The maintainer has confirmed
authority to license all original FastAPI-RS contributions under MIT. The
public artifacts are the Python wheel and the `fastapi-rs` Cargo crate;
`fastapi-rs-py` is an internal binding crate and is marked `publish = false`.
Describe the project as a source-informed independent implementation, not as
clean-room: the compatibility work deliberately inspects pinned upstream
sources. MIT applies only to original project code; it does not relicense
FastAPI, Starlette, Pydantic, or third-party material.

## Upstream and dependency material

- FastAPI 0.141.1 is MIT-licensed. Its upstream notice credits original author
  Sebastián Ramírez with Copyright (c) 2018. Its implementation modules are not
  copied into this repository. The repository does include selected signature
  and annotation metadata from the pinned source; its complete MIT notice,
  including the required copyright and permission notice, is in
  [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).
- The selected Starlette compatibility contract is 1.6.0 (BSD-3-Clause).
  Starlette-RS is a separate BSD-3-Clause project and remains a distinct
  dependency. Its complete BSD-3-Clause notice is reproduced in
  [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md), which the Python
  package declares as a license file.
- Pydantic 2.13.4 and `pydantic-core` 2.46.4 are MIT-licensed Python runtime
  dependencies. Both are explicitly pinned by the target package; Core is a
  separately distributed wheel with a Rust native extension, and FastAPI-RS
  calls its APIs directly. Their wheel license files remain with those
  separately installed distributions; the target package does not relicense
  or bundle them.
- `annotated-doc==0.0.4` is a direct target runtime dependency. Rust imports
  `annotated_doc.Doc` through PyO3 to build Python `Annotated` documentation
  metadata for signatures, parameters, exceptions, and security APIs. The
  package is separately installed and is not bundled in the FastAPI-RS wheel.
- The external target Python runtime closure for CPython 3.12.13 is hash-locked
  in
  [`requirements/target-runtime-cpython-3.12.13.lock`](../requirements/target-runtime-cpython-3.12.13.lock).
  It excludes Starlette-RS, which is installed separately from the selected
  local source revision. This lock covers the external runtime wheels only;
  it does not lock build tools or establish artifact contents for every
  supported Python/platform combination.
- The locked Rust workspace dependency graph, its licenses, enabled features,
  and dependency edges are inventoried in
  [`RUST_TARGET_DEPENDENCIES.md`](RUST_TARGET_DEPENDENCIES.md). The FastAPI
  source dependency graph is documented separately in
  [`DEPENDENCY_GRAPH.md`](DEPENDENCY_GRAPH.md).
- The Pydantic Core 2.46.4 wheel's Pydantic-owned native Cargo closure is
  inventoried separately in
  [`PYDANTIC_CORE_DEPENDENCIES.md`](PYDANTIC_CORE_DEPENDENCIES.md). That graph
  is not part of FastAPI-RS's Cargo workspace or package bundle.

### Target Python runtime profile

The target package declares annotated-doc, Pydantic, Pydantic Core, and Starlette-RS-Py as
runtime dependencies in [`pyproject.toml`](../pyproject.toml). The hashed
requirements lock is a **scoped external-wheel lock** for CPython 3.12.13, not
an all-in-one lock for building and installing the target: Starlette-RS-Py is
installed separately from the source revision pinned in
[`metadata.yaml`](../metadata.yaml), with `--no-deps`; its declared AnyIO
requirement is resolved in the external-wheel lock. The lock includes
`annotated-doc` as a target runtime import and as part of the shared parity
profile. Lock inputs and exact
wheel hashes are in the [profile input](../requirements/target-runtime-cpython-3.12.13.in)
and [lock](../requirements/target-runtime-cpython-3.12.13.lock).

| Package | Pinned version and role | Purpose / dependency path | Implementation and native parts | License evidence |
|---|---|---|---|---|
| `pydantic` | `2.13.4`; direct target runtime dependency | Reused public Python model, field, and schema API. | Python package; the validation engine is the separate `pydantic-core` wheel. | MIT, `License-Expression` in the [2.13.4 wheel metadata](https://pypi.org/pypi/pydantic/2.13.4/json) and [upstream license](https://github.com/pydantic/pydantic/blob/v2.13.4/LICENSE). |
| `pydantic-core` | `2.46.4`; direct target runtime dependency and required by Pydantic | Supplies Pydantic's validation and serialization engine; FastAPI-RS calls its Python wheel API through PyO3. | Python API with a Rust native extension. Its Rust implementation and internal crate graph remain Pydantic-owned, not a FastAPI-RS Cargo dependency. | MIT, `License-Expression` in the [2.46.4 wheel metadata](https://pypi.org/pypi/pydantic-core/2.46.4/json) and [upstream license](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/LICENSE). |
| `starlette-rs-py` | `0.1.0`; direct target runtime dependency, installed from the pinned local source | Provides the selected Starlette-RS Python package and declares `anyio>=3.6.2,<5` and `typing-extensions>=4.12.0`; the selected source is commit `4139a72449bf5751e8902fb1c7175ee7f191d338`. | Python package and PyO3 extension backed by Rust. | BSD-3-Clause declared by its [pinned project metadata](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/pyproject.toml); version is in the [pinned Cargo workspace manifest](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/Cargo.toml), and its license files are declared in project metadata. |
| `anyio` | `4.12.1`; external runtime dependency of Starlette-RS-Py | AnyIO task groups, streams, cancellation, and thread offload are called from the pinned Rust runtime; see [`runtime_calls.rs`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/src/runtime_calls.rs#L690) and [`request_runtime.rs`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/src/runtime_calls.rs#L904). | Python wheel; no native component is identified by the locked wheel metadata. | MIT, `License-Expression` in the [4.12.1 wheel metadata](https://pypi.org/pypi/anyio/4.12.1/json). |
| `annotated-types` | `0.7.0`; Pydantic transitive runtime dependency | Supplies `Annotated` constraint metadata consumed by Pydantic's field/type handling. | Python wheel; no native component is identified by the locked wheel metadata. | The wheel metadata has an MIT license classifier and a `LICENSE` file, but no `License-Expression`; the exact [v0.7.0 tagged `LICENSE`](https://github.com/annotated-types/annotated-types/blob/v0.7.0/LICENSE) is MIT. See [0.7.0 wheel metadata](https://pypi.org/pypi/annotated-types/0.7.0/json). |
| `idna` | `3.18`; AnyIO transitive runtime dependency | Required by AnyIO's declared dependency metadata. Whether the selected FastAPI-RS request path exercises IDNA handling is **unresolved**. | Python wheel; no native component is identified by the locked wheel metadata. | BSD-3-Clause, `License-Expression` in the [3.18 wheel metadata](https://pypi.org/pypi/idna/3.18/json). |
| `typing-extensions` | `4.16.0`; direct Starlette-RS-Py runtime dependency (`>=4.12.0`), also used by Pydantic, Pydantic Core, and AnyIO | Provides `TypeVar` with a default state type for generic `HTTPConnection`, `Request`, and `WebSocket` annotations in Starlette-RS `starlette/requests.py`; other packages use it for compatible typing APIs. | Python wheel; no native component is identified by the locked wheel metadata. | PSF-2.0, `License-Expression` in the [4.16.0 wheel metadata](https://pypi.org/pypi/typing-extensions/4.16.0/json). |
| `typing-inspection` | `0.4.2`; Pydantic transitive runtime dependency | Typing-object inspection required by Pydantic's type and field handling. | Python wheel; no native component is identified by the locked wheel metadata. | MIT, `License-Expression` in the [0.4.2 wheel metadata](https://pypi.org/pypi/typing-inspection/0.4.2/json). |
| `annotated-doc` | `0.0.4`; direct target runtime dependency | Rust imports `annotated_doc.Doc` through PyO3 to construct `Annotated` metadata for public signatures, parameters, exceptions, and security APIs; the lock also keeps the parity profile aligned. | Pure-Python universal wheel; no native component or runtime dependencies are declared in the locked wheel metadata. | MIT, `License-Expression` in the [0.0.4 wheel metadata](https://pypi.org/pypi/annotated-doc/0.0.4/json). |

The package-level Cargo dependency and license inventory inside the separately
installed `pydantic-core` wheel is
[`PYDANTIC_CORE_DEPENDENCIES.md`](PYDANTIC_CORE_DEPENDENCIES.md). Its root
package is MIT-licensed; dependency license expressions are retained per
resolved crate. This inventory does not bundle those crates into FastAPI-RS.

FastAPI-RS declares a `testclient` optional dependency group
(`httpx>=0.27.0,<0.29.0`). Its CPython 3.12.13 TestClient parity profile is
hash-locked in
[`requirements/target-testclient-cpython-3.12.13.lock`](../requirements/target-testclient-cpython-3.12.13.lock)
and adds `certifi==2026.1.4`, `h11==0.16.0`, `httpcore==1.0.9`, and
`httpx==0.28.1` to the target runtime profile. Their purposes, implementation
details, and license evidence are recorded in the
[dependency atlas](dependency-atlas.md#optional-published-extras). This profile
documents optional install and parity evidence only: the FastAPI-RS
`fastapi.testclient.TestClient` binding remains
`full-contract-not-established` in the
[feature crosswalk](EXTRA_FEATURE_CROSSWALK.md#feature-ownership-and-target-mapping), so
the profile does not claim public API support. The pinned Starlette-RS package
also declares separate `schemas`, `templates`, and `testclient` extras; their
use and support status are tracked independently from this FastAPI-RS profile.
Their other optional package closures remain outside the target profiles and
unresolved.

FastAPI-RS also declares a `templates` optional runtime extra with exact
requirements `Jinja2==3.1.6` and `MarkupSafe==3.0.3`. Its paired CPython
3.12.13 profile is hash-locked in
[`requirements/templates-cpython-3.12.13.lock`](../requirements/templates-cpython-3.12.13.lock);
both packages are optional runtime dependencies installed separately from the
FastAPI-RS wheel. Jinja2 is a Python template engine licensed under BSD-3-Clause
([3.1.6 wheel metadata](https://pypi.org/pypi/Jinja2/3.1.6/json)); MarkupSafe
provides escaping with Python code and an optional C speedup, and is BSD-3-Clause
licensed ([3.0.3 wheel metadata](https://pypi.org/pypi/MarkupSafe/3.0.3/json)).
The profile enables the `fastapi.templating.Jinja2Templates` alias. Its input
workflow checks alias identity and signature; generic template rendering
remains owned by Starlette-RS.
`maturin==1.14.1` is pinned as the Python build backend, and its separate
CPython 3.12.13 build-tool closure is hash-locked in
[`requirements/build-tools-cpython-3.12.13.lock`](../requirements/build-tools-cpython-3.12.13.lock).
Its version, purpose, native component, license evidence, and artifact-hash
count are recorded in [`RUST_TARGET_DEPENDENCIES.md`](RUST_TARGET_DEPENDENCIES.md).
Neither lock establishes supported wheel artifacts for every Python version
and platform or verifies the contents of a release wheel or sdist.

License values above come from the exact locked wheel's `License-Expression`
unless the row identifies a classifier/file fallback. They are package metadata,
not a review of bundled files or a substitute for the distribution notice gate
below. The target runtime lock pins wheel hashes but does not include the local
Starlette-RS source package or the separate build-tool environment.

## Notice file and archive checks

`THIRD_PARTY_NOTICES.md` reproduces the FastAPI `LICENSE` and Starlette-RS
`LICENSE.md` bytes from the commits in `metadata.yaml`. It also contains every
license/copyright-named source file from each registry `.crate` in the pinned
`Cargo.lock`, including nested vendored, build-only, and target-specific
packages. The inventory records each crate's lock checksum, license expression,
role, source path, and source-file digest; identical text is included once.
These are the locked dependency-source union. They do not imply that every
listed package is linked into every wheel. The current arm64 wheel's link table
is described separately below. The notice also reproduces the exact bundled
zlib 1.3.2 license from `libz-sys` 1.1.29, explicitly conditional on that
artifact selecting the bundled backend.

The two Cargo package roots carry generated copies of that full notice file;
`LICENSE.md` remains the shared project license. Run
`make license-notices-check` after editing the notice, dependency lock, or pin.
It verifies local cached `.crate` bytes against `Cargo.lock`; if those archives
are absent, run `cargo fetch --locked`. To regenerate the pinned excerpts,
Cargo license sections, zlib notice, and Cargo copies, run
`make license-notices-update` and review the diff.

`scripts/check_release_wheel.py` requires both declared license files in a
wheel, checks `License-File` metadata, compares archived bytes with the
repository, and rejects universal `any` wheel tags and the unverified
`Operating System :: OS Independent` classifier. Since the complete selected
Cargo license-source union is in `THIRD_PARTY_NOTICES.md`, this byte comparison
covers those texts too.
`make license-artifact-check RELEASE_NOTICE_WHEEL=<wheel-path>`
also requires the already-built public `fastapi-rs-<version>.crate` under
`RELEASE_CRATE_DIR` and checks its root-level license and notice bytes. These
checks establish file presence and identity for the supplied artifacts only.
They do not establish the selected zlib backend or host-system license set
for every target, or that the checked artifacts are the intended release
build. The maintainer has separately confirmed authority to distribute all
original project contributions under MIT.

## Release gate

Before publishing, record whether each component is independently authored,
copied, generated, or bundled; resolve and review the Cargo and Python
distribution dependency graphs; and include the applicable notices and license
texts in source and binary distributions. The Starlette-RS BSD text and
checksum-verified Cargo license-source set are included, but the selected zlib
backend still needs to be recorded for each release build. The target's
external Python runtime and Maturin build-tool
distribution closures are hash-locked for CPython 3.12.13; these locks do not
cover the separate local Starlette-RS checkout or establish every release
artifact's contents. If a source distribution contains bundled zlib source,
retain its notice and mark altered source; zlib says product-documentation
acknowledgment is appreciated but not required. Cargo.lock does not identify
whether a platform build uses system or bundled zlib. Verify wheel and sdist
contents, including license-file metadata and notices, against the versions
and native components actually shipped.
Upstream tests, docs, examples, and branding must be reviewed separately.

### Current-head source-archive evidence (2026-10-18)

Built from FastAPI-RS commit `adae40eeb7258b6fca6021370171d1cbd715c7bf`
against pinned Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338` on macOS arm64 with CPython
3.12.13 and Maturin 1.14.1:

- `target/release-sdist-adae40e/fastapi_rs-0.1.0.tar.gz` has SHA-256
  `0b61809e8b951e51f0418571c5c083a78293e0eaf26e83b513fc349affb60336`
  and is 1,096,021 bytes. The sdist validator accepted all 202 members,
  verified the vendored Starlette-RS source digest
  `da4acf9c64ae8df8a9bde0976d1777f5b36d67a6af45c443b0d0f617cad10f48`,
  and found no machine-local paths, build outputs, or profiling files.
- A release-profile wheel rebuilt from the extracted source archive passed the
  release-wheel validator:
  `target/release-sdist-wheel-adae40e/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`,
  SHA-256
  `ceee5feb3838dab4cd7fb9cc37a33662a2e2e099ad8a3366f420b2e331f2abcb`,
  1,479,718 bytes. It contains the `fastapi` facade, one native extension,
  both declared license files, and the SBOM. The focused wheel notice check
  passed.
- `otool -L` shows this wheel links `/usr/lib/libz.1.dylib` version 1.2.12,
  `/usr/lib/libiconv.2.dylib`, and `/usr/lib/libSystem.B.dylib`.
- `make license-notices-check` passed for the pinned FastAPI and Starlette-RS
  sources. The `make release-sdist` wrapper stopped during tool preparation
  because uv could not write its default cache; the direct release-sdist
  builder succeeded with the pre-existing CPython 3.12.13/Maturin 1.14.1
  environment. The build-tools lock was not re-synced during this run.

This is local artifact evidence for macOS arm64 only. Other platform builds,
Cargo crate verification/publication, and a release workflow remain
unresolved. The maintainer has since confirmed MIT licensing authority and
selected the Python wheel plus `fastapi-rs` Cargo crate as public artifacts.
Offline `cargo package` cannot verify `fastapi-rs` until its `starlette-rs`
0.1.0 dependency is available from the registry. The current core build script
also assumes the monorepo's parent `Cargo.toml`, `metadata.yaml`, and pinned
Starlette-RS checkout; it must support the packaged registry source before
the public crate can build for consumers.

### First-publication blockers

The first public release is not ready. `starlette-rs` 0.1.0 must be available
on crates.io before the core crate can resolve its Rust dependency, and
`starlette-rs-py` 0.1.0 must be available on PyPI before consumers can resolve
the wheel's runtime dependency. Make `fastapi-rs/build.rs` work from the
published crate archive without monorepo-only files, then package and build
the core crate from its `.crate` archive. Rebuild and validate the wheel and
source distribution from the final clean release commit, and verify the
declared platform matrix before publishing.

### Current-head release-profile archive evidence (2026-10-17)

Built and inspected a portable source archive from FastAPI-RS target sources
at commit `ccaf89c19c9e4b66b3da692b5ab599806c9a45f7`, against pinned
Starlette-RS `4139a72449bf5751e8902fb1c7175ee7f191d338`, on macOS arm64 with
CPython 3.12.13:

- `target/release-sdist-current-ccaf89c/fastapi_rs-0.1.0.tar.gz` has SHA-256
  `a7d8d648a3cc4df82a1792d106c3357a01eb6235f4341ab87774cb47a5c8cb70`.
  The source-archive validator accepted all 202 members and verified the
  vendored Starlette-RS source tree digest
  `da4acf9c64ae8df8a9bde0976d1777f5b36d67a6af45c443b0d0f617cad10f48`.
- Built from the extracted archive with Cargo `release` profile using locked,
  offline dependencies. The release-wheel validator passed for
  `target/release-sdist-release-wheel-current-ccaf89c/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`,
  SHA-256
  `f4facca840f6a0f16f2fde362805e9044089489e5ca7029da39671edbb66e615`.
  The archive contains the `fastapi` facade, one native extension, both
  declared license files, and its SBOM.

This verifies one local macOS arm64 source-archive release build. It does not
verify other platform artifacts, publishable Cargo archives, a release
workflow, or contributor licensing authority.

### Earlier local artifact evidence (2026-10-17)

The following checks were run from clean FastAPI-RS commit
`b1dae6577e18de4d7010b69d958631d364e0820a` against pinned Starlette-RS
`4139a72449bf5751e8902fb1c7175ee7f191d338` on macOS arm64 with CPython
3.12.13:

- The optimized abi3 wheel at
  `target/release-wheel-license-b1dae65/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`
  has SHA-256
  `503f7feda2d22c0b045b28f26abe0f48fe4268fb563fefefc999ed6cdbe1ff64`.
  The release-wheel validator and focused wheel notice check passed. The
  archive contains the `fastapi` facade, one `fastapi_rs._core` extension,
  `LICENSE.md`, `THIRD_PARTY_NOTICES.md`, and its SBOM. `otool -L` shows this
  artifact links `/usr/lib/libz.1.dylib` version 1.2.12, system iconv, and
  libSystem.
- The source archive at
  `target/release-sdist-license-b1dae65/fastapi_rs-0.1.0.tar.gz` has SHA-256
  `655f2d58940a218238178fc0f0a7ba22687eb601d07ea2fd1afef3d94aad20c9`.
  The focused sdist validator accepted all 201 members and verified the
  vendored Starlette-RS source identity against the pin. It rejected no
  machine-local paths, build outputs, or profiling files. Building from the
  extracted archive produced a development-profile wheel that passed the
  release-wheel validator and included both declared license files.
- `make license-notices-check` and the offline target dependency/license
  inventory check passed. The latter used the pinned clean Starlette-RS
  checkout and `RUSTC_WRAPPER=` because the default sibling checkout is at a
  different revision and the configured `sccache` wrapper is unavailable in
  this sandbox.
- A focused rebuild at `target/wheels/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`
  has SHA-256
  `f596657f53aa987740649b33d9e06d9f9edcbb34c6b01ce2fd1297c6452a869d`.
  `make build-python` passed the release-wheel checker; the archive has
  `Root-Is-Purelib: false`, the platform-specific
  `cp310-abi3-macosx_11_0_arm64` tag, and no OS-independent classifier. This
  confirms one local arm64 artifact only; other platform support remains
  unverified.

This earlier evidence covers one local macOS arm64 build. Its extracted-sdist
wheel used the development profile; the current-head release-profile result is
recorded above. It does not verify other platform artifacts or publishable
Cargo archives. Contributor licensing authority and the release workflow also
remain unresolved.

### Previous artifact audit (2026-10-15)

Built an arm64 CPython 3.12 abi3 wheel from FastAPI-RS commit
`d23bc7eec67b2f447e2c29f2496dcf73e953030c` against the clean pinned
Starlette-RS commit `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. The ignored
validation artifact is
`target/release-wheel-validation-20261015/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`
(SHA-256 `bbd678e2dfb5b6eb46f91c943800a45760eedd777f913bcca34f904529123b7c`).
The release-wheel validator confirmed the configured `fastapi` packages,
`fastapi_rs._core` native extension, declared license metadata, and exact
`LICENSE.md` / `THIRD_PARTY_NOTICES.md` bytes. The release-notice checker also
passed against this wheel and the pinned FastAPI/Starlette-RS sources.
`otool -L` on the wheel's extracted extension showed `/usr/lib/libz.1.dylib` 1.2.12,
`/usr/lib/libiconv.2.dylib`, and `/usr/lib/libSystem.B.dylib` for this artifact.
This validates one local wheel only; it does not establish contributor
licensing authority or readiness for publication.

An exploratory Maturin source archive was emitted at
`target/release-sdist-validation-20261015/fastapi_rs-0.1.0.tar.gz` (SHA-256
`12c95929a249bd786cd3d049ee87a372d0327fa6a7e360529f88f1229941d1fb`). It is
not usable for publication: the archive contains `Users/lazytrot/...` and
`private/tmp/...` machine-local path trees plus two `.profraw` files, and a
wheel build from the archive failed because `metadata.yaml`, which
`fastapi-rs/build.rs` reads, was omitted. `cargo package --list --locked
--offline` enumerated the FastAPI-RS crate sources in the pinned-source overlay,
but no Cargo archives were built or verified. Resolve source-archive contents,
the build-time Starlette-RS source identity contract, and Cargo package
verification before claiming source-distribution readiness.

A replacement archive was built and checked at
`target/release-sdist/fastapi_rs-0.1.0.tar.gz` (SHA-256
`bbdc4fb9882460a7efa0fa234fab5ef83e7e81e3eaef42f76a76abf720eeead6`). The
focused archive validator accepted all 201 members, verified the vendored
Starlette-RS source hash against `metadata.yaml`, and found no machine-local
paths, build outputs, or profiling files. A wheel build from an extracted copy
passed the vendored-source identity check, built a development-profile abi3
wheel at
`target/release-sdist-validation-wheels/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`
(SHA-256
`6fe6a9a19cc6ad4e71ff80a4e19f7b012ce3c726635610ea940e76ef147589a5`), and
passed the wheel content and license validator. The separate release-profile
build stopped during LTO with `No space left on device`. This validates the
source archive and an extracted-source wheel build; a clean release-profile
build and Cargo archive verification remain outstanding before publication.

The inspected arm64 wheel
`target/wheels-x0mz-20261012/fastapi_rs-0.1.0-cp310-abi3-macosx_11_0_arm64.whl`
(SHA-256 `a29839e2c0679ac6fcff483c847e08022037688e07dcd49044662eac2c80bc5b`)
has an extension whose `otool -L` output lists `/usr/lib/libz.1.dylib` version
1.2.12, `/usr/lib/libiconv.2.dylib`, and `/usr/lib/libSystem.B.dylib`.
That observation applies to this archived arm64 wheel only. Backend selection
for other artifacts remains unresolved until each artifact's link table or
build record is inspected. Host-zlib license source/version is likewise not
established by Cargo.lock.

The project should identify itself as an independent implementation and avoid
implying endorsement by FastAPI, Starlette, or Pydantic. This is an engineering
checklist, not legal advice; seek counsel for a definitive derivative-work,
trademark, or distribution determination.

## References

- [FastAPI 0.141.1 license](https://github.com/fastapi/fastapi/blob/0.141.1/LICENSE)
- [Starlette 1.6.0 license](https://github.com/Kludex/starlette/blob/1.6.0/LICENSE.md)
- [Pydantic 2.13.4 license](https://github.com/pydantic/pydantic/blob/v2.13.4/LICENSE)
- [pydantic-core 2.46.4 license](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/LICENSE)
- [Pydantic v2.13.4 architecture](https://github.com/pydantic/pydantic/blob/v2.13.4/docs/internals/architecture.md)
- [zlib 1.3.2 license notice](https://github.com/madler/zlib/blob/v1.3.2/README)
