# Licensing

## Project license

FastAPI-RS currently declares **MIT** for its independently written code. The
license text is in [`LICENSE.md`](../LICENSE.md), and MIT is declared in the
Cargo workspace and Python package metadata. Both Cargo crates package that
file via `license-file`. Before publication, maintainers must confirm that the
copyright holders can license the code and that contributor terms authorize
the contributions. The declaration does not relicense FastAPI, Starlette,
Pydantic, or third-party material.

## Upstream and dependency material

- FastAPI 0.141.1 is MIT-licensed. FastAPI source is not copied into this
  repository; if any covered material is added later, preserve its notice.
- The selected Starlette compatibility contract is 1.6.0 (BSD-3-Clause).
  Starlette-RS is a separate BSD-3-Clause project and remains a distinct
  dependency with its own notices.
- Pydantic 2.13.4 and `pydantic-core` 2.46.4 are MIT-licensed in the selected
  oracle environment. Pydantic remains an independent runtime dependency.
- The locked Rust workspace dependency graph, its licenses, enabled features,
  and dependency edges are inventoried in
  [`RUST_TARGET_DEPENDENCIES.md`](RUST_TARGET_DEPENDENCIES.md). The FastAPI
  source dependency graph is documented separately in
  [`DEPENDENCY_GRAPH.md`](DEPENDENCY_GRAPH.md).

## Release gate

Before publishing, record whether each component is independently authored,
copied, generated, or bundled; resolve and review the Cargo and Python
distribution dependency graphs; and include the applicable notices and license
texts in source and binary distributions. Starlette-RS is statically linked;
the current notice summary does not include its full BSD-3-Clause text or
identify the selected zlib backend notice. Verify wheel and sdist contents,
and verify licenses for the versions actually shipped, rather than relying on
current branch metadata. Upstream tests, docs, examples, and branding must be
reviewed separately.

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
