# FastAPI dependency map

## Snapshot

Authority is FastAPI **0.141.1**, tag commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`. The package supports Python `>=3.10`; that is a range, not a pinned interpreter. Its tagged [`pyproject.toml`](https://github.com/fastapi/fastapi/blob/0.141.1/pyproject.toml) declares five runtime requirements, while [`uv.lock`](https://github.com/fastapi/fastapi/blob/0.141.1/uv.lock) resolves a 205-package environment spanning runtime, extras, docs, and contributor tools. Do not count all 205 as runtime.

This describes the pinned **source-oracle** environment. FastAPI 0.141.1 itself
must never be installed or imported by the FastAPI-RS target at runtime; its
framework behavior belongs in Rust. Python runtime modules contain only direct
native re-exports and literal `__all__`, with no functions, branches, loops, or
fallback behavior. FastAPI-RS may separately select Pydantic and Starlette-RS
as pinned runtime components; this oracle graph does not make the remaining
upstream packages target dependencies. FastAPI-specific routing, dependency
resolution, validation orchestration, serialization/OpenAPI, middleware,
lifecycle, and protocol control flow stay in Rust.

The lock resolves the following core packages for CPython 3.11. For this interpreter, the normal Python runtime closure is **nine packages**. On Python 3.10, add `exceptiongroup` (ten total). The lock is multi-Python and does not pin the interpreter itself.

This table preserves FastAPI 0.141.1's source lock exactly for dependency
analysis. Every compatibility and parity run uses Starlette 1.6.0 alone, which
satisfies FastAPI's declared `starlette>=0.46.0` requirement.

| Package / edge | Declared by FastAPI | Locked version | Purpose and FastAPI call sites | Implementation and license |
|---|---|---:|---|---|
| `starlette` (direct) | `>=0.46.0` | `1.3.1` source-lock fact; **1.6.0 selected contract** | ASGI application base, routers/routes, requests, responses, WebSockets, middleware, lifespan, exception handling, datastructures, and re-exported public types. `applications.py`, `routing.py`, `dependencies/utils.py`, `requests.py`, `responses.py`, `websockets.py`, and middleware modules import it; routing also imports `starlette._exception_handler` and `starlette._utils`. | Python; BSD-3-Clause. [FastAPI imports](https://github.com/fastapi/fastapi/blob/0.141.1/fastapi/routing.py), [selected Starlette 1.6.0 metadata](https://github.com/Kludex/starlette/blob/1.6.0/pyproject.toml). |
| `pydantic` (direct) | `>=2.9.0` | `2.13.4` | User model and `FieldInfo` introspection; request/dependency parsing, validation errors, response filtering/serialization, dynamic body models, and JSON Schema/OpenAPI generation. Key sites: `_compat/v2.py`, `dependencies/utils.py`, `routing.py`, `encoders.py`, `openapi/models.py`. FastAPI imports Pydantic private internals in `_compat/v2.py`; this is part of the observed compatibility surface. | Python; MIT. `pydantic-core` supplies the native validation/serialization engine. [FastAPI compatibility layer](https://github.com/fastapi/fastapi/blob/0.141.1/fastapi/_compat/v2.py), [Pydantic metadata](https://github.com/pydantic/pydantic/blob/v2.13.4/pyproject.toml). |
| `typing-extensions` (direct; also transitive) | `>=4.8.0` | `4.16.0` | Backports and typing objects used in public annotations and runtime helpers: `ParamSpec`, `TypedDict`, `deprecated`, and related typing constructs. Imported by `applications.py`, `background.py`, `openapi/models.py`, `params.py`, `param_functions.py`, `responses.py`, and `routing.py`. | Python; PSF-2.0 (Python Software Foundation license). [Upstream project](https://github.com/python/typing_extensions/tree/4.16.0). |
| `typing-inspection` (direct) | `>=0.4.2` | `0.4.2` | Runtime typing introspection. FastAPI calls `typing_inspection.typing_objects.is_typealiastype` in `dependencies/utils.py` while interpreting endpoint/dependency annotations and aliases. | Python; MIT. [FastAPI call site](https://github.com/fastapi/fastapi/blob/0.141.1/fastapi/dependencies/utils.py), [upstream](https://github.com/pydantic/typing-inspection/tree/v0.4.2). |
| `annotated-doc` (direct) | `>=0.0.2` | `0.0.4` | `Doc` metadata in `Annotated` signatures documents parameters and public objects for reference tooling. Used throughout parameter helpers, exceptions, security APIs, background tasks, SSE, and OpenAPI docs. | Python; MIT. [FastAPI parameter helpers](https://github.com/fastapi/fastapi/blob/0.141.1/fastapi/param_functions.py), [upstream](https://github.com/fastapi/annotated-doc/tree/0.0.4). |
| `anyio` (via Starlette) | — | `4.12.1` | Async concurrency/networking abstraction over asyncio or Trio. FastAPI imports it directly: `concurrency.py` uses `CapacityLimiter` and `anyio.to_thread.run_sync`; `routing.py` uses AnyIO stream/task primitives. Starlette also relies on it for ASGI behavior. | Python; MIT. Its declared runtime closure is below. [AnyIO 4.12.1 metadata](https://github.com/agronholm/anyio/blob/4.12.1/pyproject.toml), [FastAPI concurrency use](https://github.com/fastapi/fastapi/blob/0.141.1/fastapi/concurrency.py). |
| `idna` (via AnyIO) | — | `3.18` | Internationalized host-name support in AnyIO's networking layer; not imported by FastAPI's own Python modules. | Python; BSD-3-Clause. [AnyIO 4.12.1 requirements](https://github.com/agronholm/anyio/blob/4.12.1/pyproject.toml), [upstream](https://github.com/kjd/idna). |
| `annotated-types` (via Pydantic) | — | `0.7.0` | Shared `Annotated` constraint metadata types consumed by Pydantic's field/schema layer; FastAPI preserves and forwards these field annotations. | Python; MIT. [Upstream](https://github.com/annotated-types/annotated-types). |
| `pydantic-core` (via Pydantic) | — | `2.46.4` | Pydantic's schema-driven validation and serialization engine. FastAPI directly uses its `CoreSchema`, `PydanticUndefined`, `Url`, validator helpers, and undefined type. | Rust `cdylib` exposed to Python through PyO3; MIT. [Pinned Pydantic architecture](https://github.com/pydantic/pydantic/blob/v2.13.4/docs/internals/architecture.md), [tagged native manifest](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/Cargo.toml). |
| `exceptiongroup` (via AnyIO; conditional) | — | `1.3.1` | Compatibility implementation of exception groups when the interpreter lacks the built-in type. Required only when `python_version < '3.11'`. | Python; MIT. [AnyIO 4.12.1 marker](https://github.com/agronholm/anyio/blob/4.12.1/pyproject.toml). |

AnyIO 4.12.1's exact runtime edges are `idna>=2.8`, `typing_extensions>=4.5; python_version<'3.13'`, and `exceptiongroup>=1.0.2; python_version<'3.11'`. There is **no `sniffio` edge** in this pinned AnyIO release's declared runtime graph; the FastAPI lock includes it through the test-only `anyio[trio] -> trio -> sniffio` path and through translation tooling's Pydantic AI/client extras (for example, `pydantic-ai -> pydantic-ai-slim[anthropic] -> anthropic -> sniffio`). The `trio` extra is enabled by FastAPI's test group, not by FastAPI's default runtime. The exact core closure is nine packages on CPython 3.13; CPython 3.10 adds conditional `exceptiongroup` for ten.

### Pydantic's native subtree

Pydantic is **not all Rust**. Its Python package defines user models, inspects annotations, and generates core schemas; `pydantic-core` executes validation and serialization in Rust. FastAPI-RS keeps Pydantic as a separate model/schema dependency for arbitrary user-defined Python model classes. FastAPI-specific orchestration remains in the `fastapi-rs` Rust crate, exposed through direct native re-exports. FastAPI 0.141.1's compatibility helpers explicitly reject Pydantic v1 models.

The separately versioned `pydantic-core 2.46.4` Cargo manifest resolves these direct native dependencies in its own Rust graph. This is **not** an extra Python runtime requirement of FastAPI-RS if it consumes the published Pydantic wheel; it becomes part of the Rust SBOM if the project vendors or rebuilds that engine.

| Pydantic Core Rust dependency group (locked versions) | Role / requested feature | License |
|---|---|---|
| `pyo3 0.28.3` | Python extension binding; requested features `generate-import-lib`, `num-bigint`, `py-clone`, `smallvec`. | MIT OR Apache-2.0 |
| `jiter 0.14.0` | Fast JSON parsing and Python-object input; `python` feature. | MIT |
| `serde 1.0.228`, `serde_json 1.0.149` | Structured serialization; `derive` and `arbitrary_precision` features. | MIT OR Apache-2.0 |
| `regex 1.12.3`, `lru 0.16.3` | String-pattern validators and compiled-regex cache. | MIT OR Apache-2.0; MIT |
| `speedate 0.17.0`, `strum 0.27.2`, `strum_macros 0.27.2` | Date/time parsing and enum-driven validation/error metadata; Strum `derive` feature. | MIT |
| `url 2.5.8`, `idna 1.1.0`, `percent-encoding 2.3.2` | URL parsing, IDN host conversion, URL encoding. | MIT OR Apache-2.0 |
| `base64 0.22.1`, `hex 0.4.3`, `num-bigint 0.4.6`, `num-traits 0.2.19`, `uuid 1.23.0` | Bytes formats, arbitrary-size numeric values, and UUID validation/serialization. | MIT OR Apache-2.0 (UUID: Apache-2.0 OR MIT) |
| `ahash 0.8.12`, `hashbrown 0.16.1`, `smallvec 1.15.1` | Hash tables/sets and compact inline storage in validation/serialization structures; `hashbrown` enables `inline-more` without its defaults. | MIT OR Apache-2.0 |
| `enum_dispatch 0.3.13` | Generate dispatch for validator, serializer, and GC-traversal enums. | MIT OR Apache-2.0 |
| Build only: `pyo3-build-config 0.28.3`, `version_check 0.9.5` | Select Python ABI/build configuration and check compiler/toolchain versions. | MIT OR Apache-2.0; MIT OR Apache-2.0 |

Versions/features above come from the tagged Pydantic source and its `Cargo.lock`; source use is in `pydantic-core/src/{validators,serializers,url.rs,py_gc.rs}`. See [Pydantic Core Cargo manifest](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/Cargo.toml) and [Pydantic Core Cargo lock](https://github.com/pydantic/pydantic/blob/v2.13.4/pydantic-core/Cargo.lock). Transitive Rust crates under these dependencies must be included in a generated native SBOM if this subtree is shipped or copied.

## Optional runtime extras

These are declared extras, not default FastAPI runtime requirements. Versions below are the FastAPI 0.141.1 lock's selected resolutions, not the open-ended declared bounds. Full bounds and extra membership are in its tagged [`pyproject.toml`](https://github.com/fastapi/fastapi/blob/0.141.1/pyproject.toml).

| Extra / package | Locked version | Feature and use | Language/native code; license |
|---|---:|---|---|
| `standard` and `all`: `fastapi-cli[standard]` | `0.0.32` | Installs the `fastapi` console command; `fastapi/cli.py` delegates to `fastapi_cli`. The CLI package also resolves `rich-toolkit`, `typer`, and `uvicorn[standard]` (plus `tomli` on Python `<3.11`); its `standard` sub-extra adds `fastapi-cloud-cli`. | Python; MIT. [Project](https://github.com/fastapi/fastapi-cli) |
| `standard` (direct) and `all` (via cloud CLI): `fastar` | `0.11.0` | Rust-backed tar archive read/write and compression utility; FastAPI's core source has no direct import site, so do not count it as HTTP request-path logic. | Rust/Python extension; MIT. [Project description](https://pypi.org/project/fastar/) |
| via `fastapi-cli[standard]`: `fastapi-cloud-cli` | `0.11.0` | Separate cloud deployment command integration; adds `fastar`, `httpx`, `pydantic[email]`, `rich-toolkit`, `rignore`, `sentry-sdk`, `typer`, and `uvicorn[standard]`. Not part of FastAPI's framework request path. | Python; MIT. [Project](https://github.com/fastapilabs/fastapi-cloud-cli) |
| `standard`, `standard-no-fastapi-cloud-cli`, `all`: `httpx` | `0.28.1` | Required by Starlette's `TestClient`, re-exported by `fastapi.testclient`; test/client capability. | Python; BSD-3-Clause. [Project](https://github.com/encode/httpx) |
| Same: `jinja2` | `3.1.6` | Template rendering through `fastapi.templating.Jinja2Templates`. | Python; BSD-3-Clause (MarkupSafe dependency may use a native extension). [Project](https://github.com/pallets/jinja) |
| Same: `python-multipart` | `0.0.32` | Parses multipart uploads and form fields, including URL-encoded `Form` inputs; required only when `Form`/`File` fields are used. | Python; Apache-2.0. [Project](https://github.com/Kludex/python-multipart) |
| Same: `email-validator` | `2.3.0` | Optional validation for Pydantic `EmailStr` fields. | Python; Unlicense. [Project](https://github.com/JoshData/python-email-validator) |
| Same: `uvicorn[standard]` | `0.40.0` | ASGI server used with the CLI/deployment path; this is outside in-process FastAPI request handling. `standard` may install platform-specific accelerators such as uvloop/httptools. | Python plus optional native extensions; BSD-3-Clause. [Project](https://github.com/encode/uvicorn) |
| Same: `pydantic-settings` | `2.14.2` | Pydantic settings/environment integration used by examples and users; not imported by FastAPI core. | Python; MIT. [Project](https://github.com/pydantic/pydantic-settings) |
| Same: `pydantic-extra-types` | `2.11.0` | Optional Pydantic field types; `fastapi.encoders` conditionally recognizes its `Color` type. | Python; MIT. [Project](https://github.com/pydantic/pydantic-extra-types) |
| `all`: `itsdangerous` | `2.2.0` | Starlette `SessionMiddleware` signed-cookie support; not commonly used by FastAPI itself. | Python; BSD-3-Clause. [Project](https://github.com/pallets/itsdangerous) |
| `all`: `pyyaml` | `6.0.3` | Starlette schema-generation integration, which FastAPI does not normally use. | Python with optional LibYAML C extension; MIT. [Project](https://github.com/yaml/pyyaml) |

`standard-no-fastapi-cloud-cli` uses the CLI's alternate extra and omits the cloud CLI (and its transitive `fastar`); `all` includes the CLI's standard/cloud extra, plus `itsdangerous` and `pyyaml` for Starlette features. `httpx 0.28.1` resolves `anyio`, `certifi`, `httpcore 1.0.9` (then `h11 0.16.0`), and `idna`. `uvicorn[standard] 0.40.0` adds platform-marked `uvloop 0.22.1` (CPython, not Windows/Cygwin), `httptools 0.7.1`, `watchfiles 1.1.1`, `websockets 15.0.1`, `python-dotenv 1.2.2`, `pyyaml 6.0.3`, and Windows `colorama`. The lock also contains `sniffio 1.3.1`, but its paths are through test-only `anyio[trio] -> trio -> sniffio` and translation tooling (`pydantic-ai -> ... -> anthropic -> sniffio`), not default runtime or the locked HTTPX/AnyIO edges. Resolve and license-audit extras only when they are distributed; do not fold them into the default runtime count.

## Build and contributor groups

FastAPI's Python package is built with unpinned isolated build requirement `pdm-backend` (`pdm.backend`, MIT); its version is read dynamically from `fastapi/__init__.py`. This is not in the application runtime graph. FastAPI is not itself built as a Rust extension.

The following are resolved package sets from `uv.lock`; package groups include the nested groups named by `pyproject.toml`:

| Group | Packages / purpose |
|---|---|
| `tests` | `anyio[trio]`, `httpx`, `httpx2`, `pytest`, `coverage`, `pytest-codspeed`, `pytest-cov`, `pytest-xdist[psutil]`, `pytest-sugar`, `pytest-timeout`, `dirty-equals`, `inline-snapshot`, `flask`, `a2wsgi`, `sqlmodel`, `strawberry-graphql`, `pwdlib[argon2]`, `pyjwt`, `mypy`, `ruff`, `ty`, `typer`, `pyyaml`; test fixtures, adapters, type checks, and benchmark/test runners. |
| `docs` / `docs-tests` | `zensical`, `mkdocstrings[python]`, `griffe-typingdoc`, `griffe-warnings-deprecated`, `markdown-include-variants`, `mdx-include`, `jieba`, `pillow`, `cairosvg`, `python-slugify`, `black`, `httpx`, `httpx2`, `pyyaml`, `typer`, `ruff`; documentation build, API rendering, image generation, and executable docs checks. |
| `translations` | `gitpython`, `pydantic-ai`, `pygithub`; translation automation and GitHub integration. |
| `github-actions` | `httpx`, `pydantic`, `pydantic-settings`, `pygithub`, `pyyaml`, `smokeshow`; release/CI scripts. |
| `dev` additions | `playwright`, `prek`, `zizmor`; browser automation, hooks, and workflow security checks; includes the tests/docs/translations groups. |

These groups and their recursive lock closure are development inputs, not dependencies required by FastAPI applications. Their licenses and any test/docs assets copied into FastAPI-RS need a separate selected-tool/asset audit; they should not be inherited wholesale.

## Implications for FastAPI-RS

1. Reproduce FastAPI's observable Pydantic v2 behavior. Pydantic may be a separately pinned FastAPI-RS runtime dependency for model APIs and Rust-backed validation/serialization; FastAPI-level validation orchestration and schema flow remain in Rust, with Python bindings passing through user model objects. This oracle graph does not require Pydantic or any other upstream package in the target manifest.
2. Treat the Starlette boundary as a full replacement: FastAPI subclasses `Starlette` and imports routes, middleware, ASGI types, and private Starlette helpers. The required `starlette` import namespace and user-visible object identity must be satisfied by Starlette-RS as established in its own contract.
3. Keep FastAPI's optional features optional in FastAPI-RS. HTTPX, Uvicorn, Jinja2, multipart parsing, email validation, settings/types, CLI, sessions, and YAML schema support each add independent user-visible behaviors and license obligations.
4. Pin the oracle package versions, Starlette-RS revision, Pydantic version, and Python implementation/version for each parity lane. Separately cover FastAPI's declared lower bounds; the broad `>=` requirements do not mean every future version is an oracle.

## Sources and license scope

Primary source snapshot: [FastAPI 0.141.1 manifest](https://github.com/fastapi/fastapi/blob/0.141.1/pyproject.toml), [lock](https://github.com/fastapi/fastapi/blob/0.141.1/uv.lock), [Pydantic 2.13.4 architecture](https://github.com/pydantic/pydantic/blob/v2.13.4/docs/internals/architecture.md), [AnyIO 4.12.1 manifest](https://github.com/agronholm/anyio/blob/4.12.1/pyproject.toml), [Starlette 1.6.0 selected contract](https://github.com/Kludex/starlette/blob/1.6.0/pyproject.toml), and [Pydantic 2.13.4 / pydantic-core sources](https://github.com/pydantic/pydantic/tree/v2.13.4).

License labels above were read from pinned upstream package metadata, upstream license files, and (for the Pydantic Core Rust graph) `cargo metadata` for the tagged manifest/lock. They are inventory facts, not a legal conclusion. Any copied upstream code, documentation, fixtures, Rust dependency subtree, or optional extra must receive its own source/notice audit before publication.
