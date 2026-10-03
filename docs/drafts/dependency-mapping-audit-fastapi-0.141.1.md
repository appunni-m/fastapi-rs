# Draft: recursive dependency mapping audit

**Status:** historical draft, 2026-09-30; superseded for current state by
[`DEPENDENCY_GRAPH.md`](../DEPENDENCY_GRAPH.md),
[`RUST_TARGET_DEPENDENCIES.md`](../RUST_TARGET_DEPENDENCIES.md), and
[`LICENSING.md`](../LICENSING.md). This dated note records the earlier audit
and backlog; its target build-tool gap predates the hash-locked
`requirements/build-tools-cpython-3.12.13.lock` profile.

## Audit result

The existing inventories cover FastAPI 0.141.1's upstream dependency graph at
the requested level. [`DEPENDENCY_GRAPH.md`](../DEPENDENCY_GRAPH.md) records
locked versions, active extras/groups and marker-bearing edges, purpose,
implementation/native notes, release license metadata, and the path back to
each group or extra root. [`DEPENDENCIES.md`](../DEPENDENCIES.md) and
[`dependency-atlas.md`](../dependency-atlas.md) explain the core request path,
optional feature roles, the build backend, and the distinction between source
oracle dependencies and FastAPI-RS target dependencies. The graph contains 204
third-party source-lock distributions across runtime, extras, and contributor
groups; that count is not a runtime count.

The source identities agree with reviewed metadata:

| Evidence | Verified result |
|---|---|
| FastAPI source at `../fastapi` | Clean checkout at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; `pyproject.toml` declares five runtime requirements and Python `>=3.10`. |
| FastAPI source lock | `../fastapi/uv.lock` SHA-256 is `96ae079a121e11b4cc0d260df5b7f77189bb90fa23a2da368f607418c2d98165`; it resolves FastAPI's source graph to Pydantic 2.13.4, pydantic-core 2.46.4, and Starlette 1.3.1. |
| Selected Starlette contract | Clean `../starlette` checkout is tag 1.6.0, commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. This is the sole Starlette compatibility contract. The upstream lock's 1.3.1 row is provenance only. The parity preparation explicitly omits that locked package and installs the selected source checkout. |
| Starlette-RS source | `metadata.yaml` selects commit `bf3ff745536547dff1177a29e1c2fe9b21202f14`. The shared `../starlette-rs` checkout is at that revision and has concurrent uncommitted work; parity uses the clean detached worktree `/private/tmp/starlette-rs-parity-bf3ff745` at the same commit. Pass it with `STARLETTE_RS_SOURCE` for reproducible checks while the shared checkout is dirty. |

### Pydantic and Rust finding

The pinned source verifies a split implementation, not “Pydantic is written in
Rust.” Pydantic 2.13.4's project metadata pins `pydantic-core==2.46.4`;
FastAPI's lock resolves that same pair. The Pydantic architecture document
assigns model definition and core-schema generation to the `pydantic` package,
and validation and serialization to `pydantic-core`. In the pinned source,
`pydantic-core/Cargo.toml` identifies version 2.46.4, declares a Rust `cdylib`
and `rlib`, and uses PyO3; its tagged `Cargo.lock` supplies a separate native
Rust graph. The FastAPI lock's Pydantic wheel is universal `py3-none-any`, while
the pydantic-core wheels are platform/ABI-specific. Therefore the correct
inventory boundary is: Python Pydantic model/schema API plus a Rust-backed
pydantic-core extension. The Rust core is not a separate FastAPI requirement;
it is transitive through Pydantic.

Primary source checks: [FastAPI 0.141.1 metadata](https://github.com/fastapi/fastapi/blob/0.141.1/pyproject.toml), [FastAPI 0.141.1 lock](https://github.com/fastapi/fastapi/blob/0.141.1/uv.lock), [Starlette 1.6.0 metadata](https://github.com/Kludex/starlette/blob/1.6.0/pyproject.toml), [Pydantic 2.13.4 metadata](https://github.com/pydantic/pydantic/blob/v2.13.4/pyproject.toml), [Pydantic architecture](https://github.com/pydantic/pydantic/blob/v2.13.4/docs/internals/architecture.md), [pydantic-core manifest](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/Cargo.toml), and [pydantic-core lock](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/Cargo.lock).

## Dependency-role cross-check

| Scope | Current source-backed record | Audit conclusion |
|---|---|---|
| Upstream default runtime | Five FastAPI requirements plus recursive locked closure in `DEPENDENCY_GRAPH.md`; `DEPENDENCIES.md` names the AnyIO, Pydantic, and Starlette edges and their Python-version conditions. | Covered. For CPython 3.12.13, the reviewed oracle profile contains nine third-party distributions plus FastAPI; the source-lock union adds `exceptiongroup` on Python below 3.11. |
| Upstream optional extras | `extra:standard`, `extra:standard-no-fastapi-cloud-cli`, and `extra:all` surfaces and their recursive edges in the generated graph; purpose/native/license notes in the atlas. | Covered as upstream features, not target defaults. CLI, server, TestClient, templates, forms/uploads, email, settings/types, sessions, and YAML roles remain distinct. |
| Upstream build and development | Locked group surfaces and recursive incoming edges in `DEPENDENCY_GRAPH.md`; build-backend evidence in `DEPENDENCIES.md` and `docs/audit-locks/fastapi-0.141.1-pdm-backend.yaml`. | Covered with an explicit exception: upstream declares unversioned `pdm-backend`, absent from `uv.lock`; 2.4.9 is an audit selection, not a verified historical release-build version. |
| FastAPI-RS target Rust | Root `Cargo.lock` plus generated `RUST_TARGET_DEPENDENCIES.md` record resolved crate versions, Cargo features, roles, license expressions, targets, and immediate edges for the target workspace and pinned Starlette-RS path source. | Covered for the recorded Cargo profile, provided regeneration uses the clean reviewed source revision. This graph does not include Pydantic Core's separately built crate graph. |
| FastAPI-RS target Python runtime | Root `pyproject.toml` pins direct runtime roots `pydantic==2.13.4` and `starlette-rs-py==0.1.0`. `requirements/target-runtime-cpython-3.12.13.lock` hash-pins the recursive parity-runtime closure; `metadata.yaml` records its SHA-256, and `make parity-prepare-target` uses `uv pip sync --require-hashes` and verifies the selected interpreter. | Covered for the pinned CPython 3.12.13 profile. This is the parity profile, not a claim about every supported Python version. |
| FastAPI-RS target build tools | The project pins Maturin 1.14.1 as a direct build requirement. | Partial: there is no separate hash-locked recursive build-tool environment. |

## Prioritized missing-evidence backlog

1. **P1 — target build-tool closure.** Create a separate reproducible,
   hash-locked build environment for Maturin and its recursive requirements.
   Keep it distinct from the target runtime lock and FastAPI source-oracle
   lock. The current target runtime Python lock and CPython 3.12.13 identity
   checks are complete.
2. **P2 — Python dependency graph regeneration.** `DEPENDENCY_GRAPH.md` matches
   all 204 versioned FastAPI source-lock packages. `make dependency-graph-check`
   now verifies the lock digest from metadata, exact package names/versions, and
   the required role, dependency-path, purpose, language/native, and license
   fields. There is no generator for the reviewed semantic notes, so update the
   table and rerun this check whenever the pinned lock changes.
3. **P2 — native Pydantic Core closure, conditional on shipping/rebuilding it.**
   The current target consumes the Pydantic wheel, so its native dependency
   tree belongs to that distribution rather than the target `Cargo.lock`.
   If the project vendors or rebuilds pydantic-core, generate a full recursive
   Cargo SBOM from the tagged Pydantic Core `Cargo.lock`, retaining selected
   features, target conditions, licenses, and build/dev roles. The existing
   Pydantic Core table in `DEPENDENCIES.md` is a direct-dependency summary, not
   that full native SBOM.
4. **P2 — native artifact and notice closure for releases.** The upstream
   inventory's license column is exact-release package metadata, with noted
   legacy/ambiguous values; it is not a scan of every wheel's bundled license
   files. Before shipping copied extras/tools or a native dependency subtree,
   tie selected platform artifacts to included notices. For Starlette-RS's
   zlib path, record the built artifact's selected system or bundled backend
   and the corresponding C zlib notice.
5. **P3 — optional CLI-only native behavior.** FastAPI's optional `standard`
   profile declares `fastar`, and the pinned FastAPI Cloud CLI deploy command
   uses it to create the zstd-compressed upload archive. It remains outside
   FastAPI's ASGI request path; include it only if optional deployment CLI
   behavior is in FastAPI-RS scope.

The draft keeps source-oracle dependencies, FastAPI-RS runtime dependencies,
and build tooling as separate scopes. Release license/notice verification for
the selected native artifacts remains an explicit pre-publish gate.
