# Third-party notices

FastAPI-RS's original code is licensed under MIT; see [`LICENSE.md`](LICENSE.md).
This repository does not include FastAPI source or wholesale Starlette
modules. Starlette-RS does include separately licensed Starlette-derived
adaptations; its BSD-3-Clause notice is reproduced below. FastAPI 0.141.1 is
the source oracle only; the target runtime must not install or import the
original FastAPI package. The versioned source trees are compatibility
authorities, not included source trees in this distribution.

## Dependencies

- `starlette-rs` 0.1.0 is a separate BSD-3-Clause project and is a Rust
  dependency of FastAPI-RS.
- PyO3 0.29.2 and its Cargo dependency closure declare MIT OR Apache-2.0 or the
  package-specific expressions recorded in
  [`docs/RUST_TARGET_DEPENDENCIES.md`](docs/RUST_TARGET_DEPENDENCIES.md).
- The Python package pins Pydantic `==2.13.4`; Pydantic and
  `pydantic-core==2.46.4` are MIT-licensed. Pydantic's public model API is
  Python, while `pydantic-core` provides its Rust validation/serialization
  engine. `starlette-rs-py==0.1.0` is separately licensed under BSD-3-Clause
  and brings its own Python runtime dependencies.

The locked Cargo inventory includes each resolved crate's license expression,
version, enabled features, purpose, and dependency edges. The Python project
has no target lockfile yet, so its resolved distribution closure must be
recorded from the release environment. Starlette-RS is statically linked into
the extension and carries Starlette-derived BSD-3-Clause material; this
full license notice is reproduced below. The selected zlib backend
uses the pinned `flate2` zlib feature and `libz-sys` 1.1.29. Its build may link
system zlib or compile the bundled stock zlib C 1.3.2 fallback, which carries
a separate zlib license. Cargo.lock does not identify the host zlib version
selected for each platform. Before publishing, record the backend used by
each build, include the applicable full license texts and copyright notices
for every dependency actually included in a source or binary distribution,
and inspect the wheel and sdist. Retain the zlib notice in any source
distribution containing its bundled source and mark altered source; record
the linked backend for every binary build. The project license does not
replace or relicense dependency material; see
[`docs/LICENSING.md`](docs/LICENSING.md).

## Starlette-RS — BSD 3-Clause

Copyright © 2018, Encode OSS Ltd. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
