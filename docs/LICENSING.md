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

### Target Python runtime profile

The target package declares Pydantic, Pydantic Core, and Starlette-RS-Py as
runtime dependencies in [`pyproject.toml`](../pyproject.toml). The hashed
requirements lock is a **scoped external-wheel lock** for CPython 3.12.13, not
an all-in-one lock for building and installing the target: Starlette-RS-Py is
installed separately from the source revision pinned in
[`metadata.yaml`](../metadata.yaml), with `--no-deps`; its declared AnyIO
requirement is resolved in the external-wheel lock. The lock also contains
`annotated-doc` only to keep the parity environments' package identities
aligned; the target package does not declare or import it. Lock inputs and exact
wheel hashes are in the [profile input](../requirements/target-runtime-cpython-3.12.13.in)
and [lock](../requirements/target-runtime-cpython-3.12.13.lock).

| Package | Pinned version and role | Purpose / dependency path | Implementation and native parts | License evidence |
|---|---|---|---|---|
| `pydantic` | `2.13.4`; direct target runtime dependency | Reused public Python model, field, and schema API. | Python package; the validation engine is the separate `pydantic-core` wheel. | MIT, `License-Expression` in the [2.13.4 wheel metadata](https://pypi.org/pypi/pydantic/2.13.4/json) and [upstream license](https://github.com/pydantic/pydantic/blob/v2.13.4/LICENSE). |
| `pydantic-core` | `2.46.4`; direct target runtime dependency and required by Pydantic | Supplies Pydantic's validation and serialization engine; FastAPI-RS calls its Python wheel API through PyO3. | Python API with a Rust native extension. Its Rust implementation and internal crate graph remain Pydantic-owned, not a FastAPI-RS Cargo dependency. | MIT, `License-Expression` in the [2.46.4 wheel metadata](https://pypi.org/pypi/pydantic-core/2.46.4/json) and [upstream license](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/LICENSE). |
| `starlette-rs-py` | `0.1.0`; direct target runtime dependency, installed from the pinned local source | Provides the selected Starlette-RS Python package and declares `anyio>=3.6.2,<5`; the selected source is commit `3125e6127804528015f13610a0cfb3c3c5f8ba07`. | Python package and PyO3 extension backed by Rust. | BSD-3-Clause declared by its [pinned project metadata](https://github.com/appunni-m/starlette-rs/blob/3125e6127804528015f13610a0cfb3c3c5f8ba07/pyproject.toml); version is in the [pinned Cargo workspace manifest](https://github.com/appunni-m/starlette-rs/blob/3125e6127804528015f13610a0cfb3c3c5f8ba07/Cargo.toml), and its license files are declared in project metadata. |
| `anyio` | `4.12.1`; external runtime dependency of Starlette-RS-Py | AnyIO task groups, streams, cancellation, and thread offload are called from the pinned Rust runtime; see [`runtime_calls.rs`](https://github.com/appunni-m/starlette-rs/blob/3125e6127804528015f13610a0cfb3c3c5f8ba07/starlette-rs-py/src/runtime_calls.rs#L551) and [`request_runtime.rs`](https://github.com/appunni-m/starlette-rs/blob/3125e6127804528015f13610a0cfb3c3c5f8ba07/starlette-rs-py/src/request_runtime.rs#L859). | Python wheel; no native component is identified by the locked wheel metadata. | MIT, `License-Expression` in the [4.12.1 wheel metadata](https://pypi.org/pypi/anyio/4.12.1/json). |
| `annotated-types` | `0.7.0`; Pydantic transitive runtime dependency | Supplies `Annotated` constraint metadata consumed by Pydantic's field/type handling. | Python wheel; no native component is identified by the locked wheel metadata. | The wheel has an MIT license classifier and a `LICENSE` file, but no `License-Expression`; the exact SPDX expression is **unresolved**. See [0.7.0 wheel metadata](https://pypi.org/pypi/annotated-types/0.7.0/json). |
| `idna` | `3.18`; AnyIO transitive runtime dependency | Required by AnyIO's declared dependency metadata. Whether the selected FastAPI-RS request path exercises IDNA handling is **unresolved**. | Python wheel; no native component is identified by the locked wheel metadata. | BSD-3-Clause, `License-Expression` in the [3.18 wheel metadata](https://pypi.org/pypi/idna/3.18/json). |
| `typing-extensions` | `4.16.0`; Pydantic, Pydantic Core, and AnyIO transitive runtime dependency | Typing definitions required by the pinned Python dependency stack. | Python wheel; no native component is identified by the locked wheel metadata. | PSF-2.0, `License-Expression` in the [4.16.0 wheel metadata](https://pypi.org/pypi/typing-extensions/4.16.0/json). |
| `typing-inspection` | `0.4.2`; Pydantic transitive runtime dependency | Typing-object inspection required by Pydantic's type and field handling. | Python wheel; no native component is identified by the locked wheel metadata. | MIT, `License-Expression` in the [0.4.2 wheel metadata](https://pypi.org/pypi/typing-inspection/0.4.2/json). |
| `annotated-doc` | `0.0.4`; parity-profile only, not a target package dependency | Preserves the source/target parity environment's shared package identity; FastAPI-RS does not import it. | Python wheel; no native component is identified by the locked wheel metadata. | MIT, `License-Expression` in the [0.0.4 wheel metadata](https://pypi.org/pypi/annotated-doc/0.0.4/json). |

The target's current `pyproject.toml` declares no optional dependency groups.
The pinned Starlette-RS package separately declares `schemas` (`pyyaml`),
`templates` (`jinja2`), and `testclient` (`httpx>=0.27,<0.29`, `httpx2>=2`)
extras. FastAPI-RS does not currently request those extras, so their resolved
versions, native parts, and license evidence are outside this base profile and
remain **unresolved** for any future target feature that needs them.
`maturin==1.14.1` is pinned as the Python build backend, but its isolated Python
build closure is not in this runtime lock. The recursive build-tool closure and
its license/native-component evidence are **unresolved** here. The profile also
covers CPython 3.12.13 only; it does not establish a lock or wheel audit for
every supported Python version and platform.

License values above come from the exact locked wheel's `License-Expression`
unless the row identifies a classifier/file fallback. They are package metadata,
not a review of bundled files or a substitute for the distribution notice gate
below. The lock pins wheel hashes but does not include the local Starlette-RS
source package or Maturin's build closure.

## Release gate

Before publishing, record whether each component is independently authored,
copied, generated, or bundled; resolve and review the Cargo and Python
distribution dependency graphs; and include the applicable notices and license
texts in source and binary distributions. The Starlette-RS BSD text is now
included, but the selected zlib backend still needs to be recorded for each
release build. The target's external Python runtime wheel closure is now
hash-locked for CPython 3.12.13; the lock does not cover the separate local
Starlette-RS checkout or the package build environment. If a source
distribution contains bundled zlib source, retain its notice and mark altered
source; zlib says product-documentation
acknowledgment is appreciated but not required. Cargo.lock does not identify
whether a platform build uses system or bundled zlib. The inspected local
macOS arm64 development extension links `/usr/lib/libz.1.dylib` version 1.2.12;
this does not establish the backend in other platform builds or release
artifacts. Verify wheel and sdist contents, including their license-file
metadata and notices, against the versions and native components actually
shipped.
Upstream tests, docs, examples, and branding must be reviewed separately.

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
