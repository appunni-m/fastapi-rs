# Third-party notices

FastAPI-RS's original code is licensed under MIT; see [`LICENSE.md`](LICENSE.md).
This repository does not copy or vendor the upstream FastAPI or Starlette
source. Their versioned source trees are compatibility authorities, not code
included in this distribution.

## Dependencies

- `starlette-rs` 0.1.0 is a separate BSD-3-Clause project and is a Rust
  dependency of FastAPI-RS.
- PyO3 0.29.2 and its Cargo dependency closure declare MIT OR Apache-2.0 or the
  package-specific expressions recorded in
  [`docs/RUST_TARGET_DEPENDENCIES.md`](docs/RUST_TARGET_DEPENDENCIES.md).
- The Python package declares Pydantic `>=2.9,<3`; the selected oracle uses
  Pydantic 2.13.4. Pydantic and `pydantic-core` are MIT-licensed in that pinned
  source. `starlette-rs-py==0.1.0` is separately licensed under BSD-3-Clause
  and brings its own Python runtime dependencies.

The locked Cargo inventory includes each resolved crate's license expression,
version, enabled features, purpose, and dependency edges. The Python project
has no target lockfile yet, so its resolved distribution closure must be
recorded from the release environment. Preserve the applicable upstream
license texts and copyright notices for every dependency actually included in
a source or binary distribution. The project license does not replace or
relicense dependency material; see [`docs/LICENSING.md`](docs/LICENSING.md).
