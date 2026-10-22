# FastAPI 0.157.0 dependency atlas

This page is the navigation and ownership crosswalk for the active FastAPI-RS dependency baseline. The detailed source-backed recursive graph is generated from the pinned FastAPI `pyproject.toml`, `uv.lock`, and reviewed dependency-use evidence in [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md). That graph records package versions, feature and group reachability, recursive purpose, implementation language/native components, and license evidence.

## Fixed identities

| Boundary | Identity and role |
|---|---|
| FastAPI source oracle | Tag `0.157.0`, commit `386a28af2f87af1a32ac26d88f07b7f58ab2dfb1`; source package and its lock are development/oracle evidence only. The target must not install or import original FastAPI at runtime. |
| FastAPI source lock | `uv.lock` SHA-256 `62147be0657e1be6cbe592f335f52429e814f1236524c607e1e4cf4b01913678`; resolves 207 third-party distributions across runtime, extras, and groups. |
| Starlette compatibility oracle | `1.6.0`, commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`; sole selected Starlette contract. FastAPI's source lock resolves Starlette `1.7.0` for inventory, not parity. |
| Pydantic source/target pin | `pydantic==2.13.5`, `pydantic-core==2.46.5`; Pydantic owns the Python model API and native Core engine. |
| Starlette-RS implementation contract | Exact source pin is in [`metadata.yaml`](../metadata.yaml); generic ASGI behavior belongs to that sibling project. |

FastAPI 0.157.0 newly declares `opentelemetry-api` in its default runtime closure and has an optional `opentelemetry` extra. Those are upstream source facts, not FastAPI-RS target runtime dependencies. The target dependency surface is separately declared in [`pyproject.toml`](../pyproject.toml), Cargo manifests, and profile locks.

## FastAPI-RS target Pydantic profile

The target directly pins Pydantic `2.13.5` and pydantic-core `2.46.5` because FastAPI-RS calls their Python APIs through PyO3. The Core wheel contains Pydantic-owned Rust code; it is not a FastAPI-RS Cargo dependency or public API. FastAPI's upstream lock reaches pydantic-core transitively through Pydantic, while the target declares it directly for its own binding boundary.

For the target's complete package roles, licenses, and recursive Python/Cargo dependencies, see [Rust target dependencies](RUST_TARGET_DEPENDENCIES.md), [Pydantic Core dependencies](PYDANTIC_CORE_DEPENDENCIES.md), and [DEPENDENCIES.md](DEPENDENCIES.md). For the full FastAPI source graph and evidence links, use [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md).

## Historical baseline

The prior FastAPI `0.141.1` dependency atlas is preserved at [`archive/dependency-atlas-fastapi-0.141.1.md`](archive/dependency-atlas-fastapi-0.141.1.md). Its lock identities and counts are historical and do not describe the active `0.157.0` baseline.
