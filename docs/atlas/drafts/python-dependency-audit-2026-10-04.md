# Draft: FastAPI-RS Python dependency audit

**Status:** read-only audit, 2026-10-04. This note checks the target Python
runtime/build profile and source-declared Starlette-RS extras. It does not treat
the FastAPI source-oracle lock as the target dependency lock. No tests were run.

## Scope inspected

Checked the project `pyproject.toml`, `requirements/target-runtime-cpython-3.12.13.{in,lock}`, `requirements/build-tools-cpython-3.12.13.{in,lock}`, `requirements-dev.txt`, `metadata.yaml`, `Makefile`, `Cargo.toml`, both target Cargo manifests, `Cargo.lock`, and `rust-toolchain.toml`. Checked the pinned FastAPI source `../fastapi/pyproject.toml` and selected `uv.lock` identity/dependency rows for oracle-versus-target separation. Reviewed target dependency claims in `docs/LICENSING.md`, `docs/RUST_TARGET_DEPENDENCIES.md`, `docs/DEPENDENCIES.md`, `docs/DEPENDENCY_GRAPH.md`, `docs/dependency-atlas.md`, `docs/EXTRA_FEATURE_CROSSWALK.md`, `THIRD_PARTY_NOTICES.md`, and the earlier dependency-mapping draft.

For source evidence, checked FastAPI-RS imports and extension registration, the
clean Starlette-RS worktree at `a345f8c3f5306dbc00c5fc37f8f16d2e79666065`,
and its `pyproject.toml`, Rust runtime calls, and Python schema/template/
TestClient facades. The shared `../starlette-rs` checkout is dirty and at another commit;
it was not used for the selected-source findings. Read exact-version PyPI
release metadata for pinned runtime/build/dev packages named below, including
`Requires-Dist`, license fields/classifiers, programming-language classifiers,
and wheel tags. Also inspected example JSON Schema closure metadata (`attrs`
25.4.0, `jsonschema-specifications` 2025.9.1, `referencing` 0.37.0,
`rpds-py` 0.27.1) and HTTPX 0.28.1, HTTPX2 2.0.0, and Jinja2 3.1.6 release
metadata; those are not selected target versions.
There is no checked-out Pydantic source tree in the inspected inputs; Pydantic
package behavior below is limited to target call sites and pinned package
metadata.

## Target runtime profile

`metadata.yaml` pins CPython 3.12.13 and the target-runtime lock digest; the
recorded digest matches the file. The target package directly declares Pydantic
2.13.4, pydantic-core 2.46.4, and Starlette-RS-Py 0.1.0. The selected
Starlette-RS source commit is separately fixed in `metadata.yaml`; its Python
package is installed from that checkout with `--no-deps`.

| Distribution | Role and resolved identity | Purpose and recursive path | Language/native parts; license evidence |
|---|---|---|---|
| `starlette-rs-py` | Direct target runtime; 0.1.0 at Starlette-RS commit `a345f8c3f5306dbc00c5fc37f8f16d2e79666065` | Generic ASGI objects and behavior called by FastAPI-RS. Its pinned metadata requires `anyio>=3.6.2,<5` and `typing-extensions>=4.12.0`. | Python package plus PyO3/Rust extension; BSD-3-Clause declared by the pinned `pyproject.toml` and license files. |
| `pydantic` | Direct target runtime; 2.13.4 | Reused model, field, schema, and validation API; target Rust code imports Pydantic modules and calls model/schema interfaces. Requires `pydantic-core==2.46.4`, `annotated-types>=0.6.0`, `typing-extensions>=4.14.1`, and `typing-inspection>=0.4.2`. | Universal Python wheel; MIT `License-Expression` in exact release metadata. |
| `pydantic-core` | Direct target runtime; 2.46.4; also required exactly by Pydantic | Pydantic validation/serialization engine. FastAPI-RS imports its runtime APIs through PyO3, so the direct root declaration is justified in addition to Pydantic's edge. Requires `typing-extensions>=4.14.1`. | Python API with Rust native extension; exact release metadata identifies Rust and publishes platform/ABI wheels. MIT `License-Expression`. Its separately built crate graph is not in this workspace's `Cargo.lock`. |
| `anyio` | Transitive target runtime; 4.12.1 via Starlette-RS-Py | Starlette-RS calls AnyIO task groups, cancellation, streams, and thread offload. AnyIO requires `idna>=2.8`; it also requires `typing_extensions>=4.5` on Python `<3.13`, active in this profile. | Universal Python wheel; MIT `License-Expression`. |
| `idna` | Transitive target runtime; 3.18 via AnyIO | AnyIO's required IDNA/network dependency. Whether this FastAPI-RS request path exercises its IDNA behavior is not established. | Universal Python wheel; BSD-3-Clause `License-Expression`. |
| `typing-extensions` | Transitive target runtime; 4.16.0 via Starlette-RS-Py, Pydantic, pydantic-core, and AnyIO | Provides the generic `TypeVar` default used by Starlette-RS request/connection types and compatible typing APIs used by the other packages. | Universal Python wheel; PSF-2.0 `License-Expression`. |
| `annotated-types` | Transitive target runtime; 0.7.0 via Pydantic | Python `Annotated` constraint metadata consumed by Pydantic. | Universal Python wheel; exact release metadata has an MIT classifier but no `License-Expression`. The exact license text was not checked in this audit. |
| `typing-inspection` | Transitive target runtime; 0.4.2 via Pydantic | Runtime typing-object inspection for Pydantic's type/field handling. | Universal Python wheel; MIT `License-Expression`. |
| `annotated-doc` | **Direct target runtime requirement, 0.0.4; currently undeclared in project metadata** | Supplies `annotated_doc.Doc` values used for FastAPI parameter, error, security, and API-signature annotations. It has no runtime dependencies in exact release metadata. See the discrepancy below. | Universal pure-Python wheel; MIT `License-Expression`. |

For CPython 3.12.13, AnyIO's `exceptiongroup` marker (`python_version <
"3.11"`) is inactive, and its Trio dependency is only selected through the
`trio` extra, which the target does not request. Pydantic's email/timezone
extras are also not selected. The external target lock contains eight wheel
distributions: seven other product runtime packages plus `annotated-doc`, also
used by the target at runtime. `starlette-rs-py` is installed separately from
its pinned source. The package metadata currently omits `annotated-doc`, so the
lock is covering an actual runtime import by accident rather than through the
target package's declared dependency graph.

## Concrete discrepancy: `annotated-doc`

The claim that FastAPI-RS does not import `annotated-doc` is false. The
extension initializer ([`fastapi-rs-py/src/lib.rs`](../../../fastapi-rs-py/src/lib.rs:321)) calls
[`register_python_api`](../../../fastapi-rs/src/lib.rs:31), which calls
[`parameters::register`](../../../fastapi-rs/src/lib.rs:34) and constructs the
`Depends` and `Security` signatures. The signature builders
[`set_depends_signature`](../../../fastapi-rs/src/parameters.rs:899) and
[`set_security_signature`](../../../fastapi-rs/src/parameters.rs:1067) import
`annotated_doc.Doc`. Thus an ordinary `fastapi` import reaches this dependency.
Other direct call sites build documented parameter/error/security annotations
in [`docs.rs`](../../../fastapi-rs/src/docs.rs:508),
[`errors.rs`](../../../fastapi-rs/src/errors.rs:512), and
[`security.rs`](../../../fastapi-rs/src/security.rs:1382).

The following current claims need correction:

- `requirements/target-runtime-cpython-3.12.13.in` calls the package
  comparator-only and says FastAPI-RS does not import it.
- `docs/LICENSING.md` repeats that claim in the profile introduction and the
  `annotated-doc` row.
- `docs/EXTRA_FEATURE_CROSSWALK.md` groups it with packages that are not direct
  target requirements.
- `THIRD_PARTY_NOTICES.md` says the target does not import or declare it.
- Root `pyproject.toml` has no `annotated-doc` project dependency, even though
  the runtime code imports it and the target profile already pins 0.0.4.

Declare `annotated-doc==0.0.4` as a target runtime dependency (or remove the
runtime imports as part of a separately reviewed implementation change), then
correct the lock-input comments and target license/crosswalk/notice text. Keep
the comparator identity check; it is additional evidence, not the runtime
reason for this package. Regenerate/check the relevant dependency metadata and
hash lock after that change.

## Optional and developer profiles

The target project's `pyproject.toml` declares no optional dependency groups.
The pinned Starlette-RS metadata declares these optional extras, none requested
by FastAPI-RS's base dependency declaration:

| Starlette-RS extra | Declared packages and source-backed purpose | Resolved version/license/native status in target profile |
|---|---|---|
| `schemas` | `pyyaml`; schema rendering and YAML docstring parsing in `starlette/schemas.py` | Not resolved for target optional runtime. Target `requirements-dev.txt` separately pins PyYAML 6.0.3 for scripts; that is not the `schemas` extra lock. |
| `templates` | `jinja2`; template integration in `starlette/templating.py` | Not resolved for target optional runtime. Exact version and recursive dependency/native closure are unknown. |
| `testclient` | `httpx>=0.27,<0.29` and `httpx2>=2`; TestClient transport prefers HTTPX2 and falls back to HTTPX with a deprecation warning | Neither client is in the target runtime lock. Resolved versions, transitive/native closure, and license evidence for a target TestClient profile are unknown. |

`requirements-dev.txt` pins Maturin 1.14.1, Ruff 0.14.14, uv 0.11.29,
jsonschema 4.26.0, and PyYAML 6.0.3. Maturin is the build backend and is run
directly by `make build-python`; Ruff formats/lints; uv creates and syncs the
isolated tool environment; jsonschema validates recipes, contracts, and
schemas; PyYAML reads YAML inputs. The build-tools input/lock correctly
isolates Maturin as the CPython 3.12.13 build backend: exact release metadata
has no active `Requires-Dist` dependency for Python 3.12 (the `tomli` marker is
below 3.11; `patchelf` and `ziglang` are unselected extras). The locked Maturin
wheel is Rust-backed/native and MIT OR Apache-2.0; the hash-locked build-tools
closure has one package. Cargo dependencies/build dependencies are separately
recorded in `Cargo.lock` and `docs/RUST_TARGET_DEPENDENCIES.md`.

The remaining developer dependencies have direct version pins but no recursive
hash lock in this repository. Exact release metadata shows Ruff and uv are
Rust-backed/native command-line packages with no declared Python dependencies;
Ruff reports MIT and uv reports MIT OR Apache-2.0. PyYAML 6.0.3 reports legacy
MIT license metadata and publishes CPython platform wheels; which wheel/native
accelerator is selected is not fixed by `requirements-dev.txt`. jsonschema
4.26.0 reports MIT and declares the base recursive closure `attrs`,
`jsonschema-specifications`, `referencing`, and `rpds-py`; their selected
versions and their selected language/native/license details are unresolved
without a target dev lock. The `[format]` extras are not declared by this
project requirement.

`Makefile` prepares the isolated Maturin environment with the external `uv`
command. Although uv 0.11.29 is in `requirements-dev.txt`, it is not in the
hash-locked build-tools environment or lock, so bootstrap tooling itself is not
reproduced by `make build-tools-prepare`. The documented direct build command
uses `maturin build`; do not count the FastAPI source-oracle `uv.lock` as the
target's developer lock.

## Remaining limits and next inventory work

1. Fix the undeclared runtime `annotated-doc` dependency and its false
   parity-only descriptions before making installation/runtime claims.
2. Add a hash-locked developer/bootstrap-tools profile for the pinned
   `requirements-dev.txt` entries and recursive JSON Schema dependencies, or
   keep each unresolved developer closure explicitly out of the supported
   build profile. Record selected artifact hashes so PyYAML/Rust-wheel choices
   and license evidence are reproducible.
3. Keep optional Starlette-RS extras visibly unresolved until each intended
   feature has a dedicated resolved lock and metadata/license/native review.
4. Treat pydantic-core's Rust crate graph as a separate external-wheel native
   artifact inventory. Its package version, Python requirement, direct Python
   dependency, Rust implementation, wheel hashes, and MIT license were
   verified; its recursive Rust crate/build closure was not available in the
   checked-out inputs and is not represented by the FastAPI-RS `Cargo.lock`.

## Resolution verified after the audit

The root task declared `annotated-doc==0.0.4` in `pyproject.toml`, corrected
the target lock-input scope note and dependency/license crosswalks, and
regenerated `docs/RUST_TARGET_DEPENDENCIES.md`. The exact pin was already in
the hash-locked target runtime profile, so the lock contents and recorded lock
digest did not need to change. `make metadata-check`,
`make dependency-inventory-check`, `make dependency-graph-check`, and the
target-runtime boundary checks passed. A release wheel built from a temporary
workspace overlay using the clean pinned Starlette-RS source declares
`Requires-Dist: annotated-doc==0.0.4` along with the three existing direct
requirements, and declares no upstream `fastapi` dependency. Optional
Starlette-RS extras, developer/bootstrap hash closure, and the external
pydantic-core Rust crate graph remain unresolved as listed above.

The FastAPI 0.141.1 `uv.lock` remains source-oracle evidence only. Its optional
extras and development closure are not target runtime/build/dev dependencies.

## Exact release metadata consulted

Runtime: [Pydantic 2.13.4](https://pypi.org/pypi/pydantic/2.13.4/json),
[pydantic-core 2.46.4](https://pypi.org/pypi/pydantic-core/2.46.4/json),
[annotated-types 0.7.0](https://pypi.org/pypi/annotated-types/0.7.0/json),
[typing-inspection 0.4.2](https://pypi.org/pypi/typing-inspection/0.4.2/json),
[typing-extensions 4.16.0](https://pypi.org/pypi/typing-extensions/4.16.0/json),
[AnyIO 4.12.1](https://pypi.org/pypi/anyio/4.12.1/json),
[idna 3.18](https://pypi.org/pypi/idna/3.18/json), and
[annotated-doc 0.0.4](https://pypi.org/pypi/annotated-doc/0.0.4/json).
Build/dev: [Maturin 1.14.1](https://pypi.org/pypi/maturin/1.14.1/json),
[Ruff 0.14.14](https://pypi.org/pypi/ruff/0.14.14/json),
[uv 0.11.29](https://pypi.org/pypi/uv/0.11.29/json),
[jsonschema 4.26.0](https://pypi.org/pypi/jsonschema/4.26.0/json), and
[PyYAML 6.0.3](https://pypi.org/pypi/PyYAML/6.0.3/json). The Starlette-RS
project metadata is pinned at [commit a345f8c](https://github.com/appunni-m/starlette-rs/blob/a345f8c3f5306dbc00c5fc37f8f16d2e79666065/pyproject.toml).
