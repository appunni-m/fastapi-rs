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
For the separately pinned Starlette 1.6.0 source-oracle lock profile, see
[Starlette source-lock dependencies](STARLETTE_1_6_SOURCE_LOCK_PROFILE.md).
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

## Target optional runtime profile: templates

The `templates` extra adds an optional runtime dependency closure for the
`fastapi.templating.Jinja2Templates` alias. The base runtime lock remains free
of Jinja2. The paired CPython 3.12.13 oracle and target profile uses the
hash-locked requirements in
[`requirements/templates-cpython-3.12.13.lock`](../requirements/templates-cpython-3.12.13.lock).

| Package | Version and profile role | Purpose | Language and native components | License evidence |
|---|---|---|---|---|
| Jinja2 | `3.1.6`; direct optional runtime dependency in the `templates` extra | Required by Starlette's `Jinja2Templates` integration; FastAPI directly re-exports that class. | Python template engine; the locked distribution is a Python wheel. | BSD-3-Clause ([3.1.6 wheel metadata](https://pypi.org/pypi/Jinja2/3.1.6/json)). |
| MarkupSafe | `3.0.3`; direct optional runtime dependency in the `templates` extra and part of Jinja2's runtime closure | Escapes template text and supplies the `Markup` type. | Python implementation with an optional CPython C speedup; selected wheel depends on platform. | BSD-3-Clause ([3.0.3 wheel metadata](https://pypi.org/pypi/MarkupSafe/3.0.3/json)). |

The profile records the facade's import path, alias identity, and callable
signature. Starlette-RS owns generic rendering behavior; this optional package
closure does not implement it in FastAPI-RS.

## Target optional runtime profile: testclient

The `testclient` extra adds the optional runtime dependency for the direct
`fastapi.testclient.TestClient` facade. The paired CPython 3.12.13 target lock
resolves 12 external distributions: the eight packages in the base target
runtime profile plus HTTPX and its three additional locked dependencies below.
The base packages and their purposes are documented in the
[target Python dependency inventory](RUST_TARGET_DEPENDENCIES.md#python-package-dependencies).
The complete hash-locked profile is
[`requirements/target-testclient-cpython-3.12.13.lock`](../requirements/target-testclient-cpython-3.12.13.lock).

| Package | Version and profile role | Purpose | Language and native components | License evidence |
|---|---|---|---|---|
| HTTPX | `0.28.1`; direct optional runtime dependency in the `testclient` extra (`httpx>=0.27.0,<0.29.0`) | Provides the HTTP client used by Starlette-RS TestClient for in-process requests. FastAPI exposes the TestClient alias. | Python HTTP client; no native component in the locked wheel. | BSD-3-Clause ([0.28.1 wheel metadata](https://pypi.org/pypi/httpx/0.28.1/json)). |
| HTTPcore | `1.0.9`; transitive optional runtime dependency of HTTPX | Supplies HTTPX's low-level connection pools and transport implementation. | Python implementation; no native component in the locked wheel. | BSD-3-Clause ([1.0.9 wheel metadata](https://pypi.org/pypi/httpcore/1.0.9/json)). |
| h11 | `0.16.0`; transitive optional runtime dependency of HTTPcore | Implements the HTTP/1.1 protocol used by HTTPcore. | Pure-Python HTTP/1.1 state machine. | MIT ([0.16.0 wheel metadata](https://pypi.org/pypi/h11/0.16.0/json)). |
| certifi | `2026.1.4`; transitive optional runtime dependency of HTTPX and included in the profile lock | Supplies the CA certificate bundle used by HTTPX's default TLS verification. | Python package containing CA certificate data; no native component. | MPL-2.0 ([2026.1.4 wheel metadata](https://pypi.org/pypi/certifi/2026.1.4/json)). |

Starlette-RS owns TestClient behavior; the extra supplies its HTTPX client
dependency. This package closure does not implement the FastAPI application or
server-side HTTP stack.

## Hash-locked parity profiles: multipart and email validation

These profiles add packages for selected parity workflows. They are not
published FastAPI-RS extras: `pyproject.toml` currently declares only
`testclient` and `templates`. The target locks are
[`target-standard-multipart`](../requirements/target-standard-multipart-cpython-3.12.13.lock)
and [`email-validation`](../requirements/email-validation-cpython-3.12.13.lock);
the latter is shared by the source oracle and target. The FastAPI source oracle
uses its own `standard` extra for multipart workflows, while the target profile
installs only the multipart package needed by those cases.

| Package | Version and profile role | Purpose | Language and native components | License evidence |
|---|---|---|---|---|
| python-multipart | `0.0.32`; direct dependency in the `standard-multipart` target parity profile | Provides optional form-support availability and `parse_options_header` compatibility at the Python request boundary; the pinned Starlette-RS Rust implementation parses multipart request bodies with `multer`. | Python package; no native component in the locked wheel. | Apache-2.0 ([0.0.32 wheel metadata](https://pypi.org/pypi/python-multipart/0.0.32/json)). |
| email-validator | `2.3.0`; direct dependency in the `email-validation` parity profiles | Enables Pydantic `EmailStr` validation used by FastAPI models. | Python validation library; no native component in the locked wheel. | Unlicense ([2.3.0 wheel metadata](https://pypi.org/pypi/email-validator/2.3.0/json)). |
| dnspython | `2.8.0`; transitive dependency of `email-validator` in the `email-validation` profiles | Supports optional DNS deliverability checks; the selected syntax acceptance/rejection cases do not exercise DNS queries. | Python DNS toolkit; no native component in the locked wheel. | ISC ([2.8.0 wheel metadata](https://pypi.org/pypi/dnspython/2.8.0/json)). |

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
