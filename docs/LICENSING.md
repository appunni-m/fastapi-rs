# Licensing

## Project license

FastAPI-RS currently declares **MIT** for its independently written code. The
license text is in [`LICENSE.md`](../LICENSE.md), and MIT is declared in the
Cargo workspace and Python package metadata. Both Cargo crates package that
file via `license-file`. Before publication, maintainers must confirm that the
copyright holders can license the code and that contributor terms authorize
the contributions. Describe the project as a source-informed independent
implementation, not as clean-room: the compatibility work deliberately
inspects pinned upstream sources. MIT applies only to original project code;
it does not relicense FastAPI, Starlette, Pydantic, or third-party material.

## Upstream and dependency material

- FastAPI 0.141.1 is MIT-licensed. FastAPI source is not copied into this
  repository; if any covered material is added later, preserve its notice.
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
wheel, checks `License-File` metadata, and compares archived bytes with the
repository. Since the complete selected Cargo license-source union is in
`THIRD_PARTY_NOTICES.md`, this byte comparison covers those texts too.
`make license-artifact-check RELEASE_NOTICE_WHEEL=<wheel-path>`
also requires the already-built `fastapi-rs-<version>.crate` and
`fastapi-rs-py-<version>.crate` under `RELEASE_CRATE_DIR` and checks their
root-level license and notice bytes. These checks establish file presence and
identity for the supplied artifacts only. They do not establish the selected
zlib backend or host-system license set for every target, that the checked
artifacts are the intended release build, or that any contributor/rightsholder
has granted rights to distribute the project.

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

### Latest validated local wheel (2026-10-15)

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
