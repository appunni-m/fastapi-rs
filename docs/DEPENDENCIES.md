# Dependency and license maps

FastAPI 0.141.1 is the source oracle. Starlette 1.6.0 is the sole Starlette
compatibility oracle; the sibling Starlette-RS checkout is the implementation
contract. FastAPI's lock graph describes its own runtime, extras, and
development tooling. It does not define FastAPI-RS's runtime dependencies.

For the source-backed recursive FastAPI dependency graph, including version,
feature, purpose, language/native components, license, and runtime/optional/
build/dev reachability, see [the dependency graph](DEPENDENCY_GRAPH.md) and
[the per-package dependency atlas](dependency-atlas.md). For FastAPI-RS's
actual Cargo graph and direct Rust use, see [Rust target dependencies](RUST_TARGET_DEPENDENCIES.md).
For the separately installed Pydantic Core wheel's Pydantic-owned native Cargo
closure, see [Pydantic Core dependencies](PYDANTIC_CORE_DEPENDENCIES.md).
For license scope, notices, and remaining legal review, see [licensing](LICENSING.md).

The Python package is a thin PyO3 facade. FastAPI-specific routing,
dependency resolution, validation orchestration, serialization, OpenAPI,
middleware, lifecycle, and protocol control flow belong in Rust. FastAPI's
source package is oracle-only and must not be installed or imported by the
target at runtime. Pydantic remains a separately pinned user-model/schema
dependency; its Python model layer and native `pydantic-core` engine are
distinct parts of that boundary.

Dependency signature resolution also uses the pinned Pydantic 2.13.4 private
`pydantic._internal._typing_extra.try_eval_type` helper through PyO3. It
resolves string annotations from `inspect.signature` in the unwrapped
callable's globals, matching FastAPI's `_compat/v2.py::evaluate_forwardref`
bridge. Rust selects the signature, handles fallback and constructs dependency
plans; Pydantic owns Python typing evaluation. This private interface is tied
to the exact Pydantic pin and needs review before a version change.

Native dependency records expose CPython 3.12.13 dataclass metadata through
stdlib `dataclasses.field`, `_FIELD`, and `_DataclassParams`. Rust constructs
the record classes, performs argument binding, and implements repr, equality,
hashing, initialization, and frozen attribute control. The stdlib provides
metadata values and public `fields`/`asdict`/`replace` consumers; the target does
not call `dataclasses.dataclass` to generate Python methods. The two private
metadata interfaces require review before changing the Python pin.

Generated dependency records are refreshed from pinned source and lockfiles;
do not edit generated tables by hand. Review their evidence in
`docs/audit-locks/fastapi-0.141.1-source-use.yaml` and
`metadata.yaml`.
