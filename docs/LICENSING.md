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
