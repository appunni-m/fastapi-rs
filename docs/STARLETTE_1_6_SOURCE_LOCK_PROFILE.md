# Starlette 1.6.0 source-lock dependency profile

This profile records the dependency lock shipped with the pinned Starlette
1.6.0 source-oracle checkout. It is separate from FastAPI 0.141.1's own
[`uv.lock` entry for `starlette==1.3.1`](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/uv.lock#L4145-L4152).
That FastAPI lock remains its source dependency record and is not replaced by
this profile. Nothing here
declares a target runtime dependency for FastAPI-RS; the target uses the pinned
Starlette-RS implementation.

## Source identity and lock evidence

| Evidence | Value |
| --- | --- |
| Upstream source | [`Kludex/starlette` tag `1.6.0`](https://github.com/Kludex/starlette/tree/4f250d6b814587e20c5365f0a5f0c4d42bcb929f) |
| Tag commit | `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` |
| Lock file | [`uv.lock` at that commit](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/uv.lock) |
| Lock SHA-256 | `55651218ddc03f4a40eb37173a63e85899cd1b303afa208666ea75754b58c991` |
| Lock format | `version = 1`, `revision = 3`; source project requires Python `>=3.10` |
| Lock package records | 86 total: the editable Starlette root plus 85 registry distributions |

The tag dereferences to the recorded commit, and hashing `git show
1.6.0:uv.lock` produces the recorded lock SHA. The project version is dynamic
in `pyproject.toml`; the source tag supplies the `1.6.0` identity. The lock's
Python resolution markers split at Python 3.15. The tables below describe the
union of packages reachable across lock markers, retaining the narrower
Python conditions called out in the source metadata.

The package name, runtime roots, `full` extra, dependency groups, and default
group selection are declared in the tagged
[`pyproject.toml`](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/pyproject.toml).
Resolved versions and dependency edges come from the tagged `uv.lock`. Package
names in the tables link to exact-version PyPI release metadata. Purpose and
implementation notes combine those release records with the tagged Starlette
source call sites shown in the table.

## Default runtime closure

The direct project requirements are `anyio>=3.6.2,<5` and, when
`python_version < 3.13`, `typing_extensions>=4.10.0`. The lock resolves the
following four third-party distributions across the supported Python marker
range:

| Distribution and locked version | Edge and role | Purpose and language/native component | License |
| --- | --- | --- | --- |
| [anyio 4.14.2](https://pypi.org/project/anyio/4.14.2/) | Direct; runtime. Also reached by the optional HTTP clients. | Async concurrency and thread-offload primitives used throughout Starlette, including its [concurrency helpers](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/concurrency.py). Python implementation; no compiled extension in the locked package. | [MIT](https://pypi.org/pypi/anyio/4.14.2/json) |
| [typing-extensions 4.15.0](https://pypi.org/project/typing-extensions/4.15.0/) | Direct for Python `<3.13`; also a conditional AnyIO/HTTPX2 dependency. Runtime. | Backports typing names used by Starlette on older Python, including `TypeIs`, `TypeVar`, and `Self` ([source](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/_utils.py)). Python implementation; no compiled extension in the locked package. | [PSF-2.0](https://pypi.org/pypi/typing-extensions/4.15.0/json) |
| [exceptiongroup 1.3.0](https://pypi.org/project/exceptiongroup/1.3.0/) | Transitive through AnyIO for Python `<3.11`; runtime only under that marker. | Backport of Python 3.11 exception-group types used by AnyIO on older interpreters. Python-only package; no native component. | [MIT](https://pypi.org/pypi/exceptiongroup/1.3.0/json) |
| [idna 3.18](https://pypi.org/project/idna/3.18/) | Transitive through AnyIO; runtime. Also reached by both optional HTTP clients. | Internationalized domain-name encoding for network destinations. Python implementation; no compiled extension in the locked package. | [BSD-3-Clause](https://pypi.org/pypi/idna/3.18/json) |

`exceptiongroup` is not part of the runtime closure on Python 3.11 and newer;
`typing-extensions` is not part of it on Python 3.13 and newer. The reported
four-package count is the marker union, not a claim that every interpreter
installs all four.

## Optional `full` extra closure

The `full` extra directly selects `httpx`, `httpx2`, `itsdangerous`, `jinja2`,
`python-multipart`, and `pyyaml`. Together with the default runtime closure,
the transitive `full` closure is 16 third-party distributions. The four
runtime rows above are shared; the 12 additional locked packages are:

| Distribution and locked version | Edge and role | Purpose and language/native component | License |
| --- | --- | --- | --- |
| [certifi 2025.8.3](https://pypi.org/project/certifi/2025.8.3/) | Transitive through HTTPX/HTTP Core; optional `full`. | Mozilla CA bundle consumed by the HTTP clients. Python package plus certificate data; no compiled extension. | [MPL-2.0](https://pypi.org/pypi/certifi/2025.8.3/json) |
| [h11 0.16.0](https://pypi.org/project/h11/0.16.0/) | Transitive through HTTP Core and HTTP Core 2; optional `full`. | Pure-Python HTTP/1.1 protocol implementation. | [MIT](https://pypi.org/pypi/h11/0.16.0/json) |
| [httpcore 1.0.9](https://pypi.org/project/httpcore/1.0.9/) | Transitive through HTTPX; optional `full`. | Low-level HTTP transport used by HTTPX. Python implementation; no compiled extension. | [BSD-3-Clause](https://pypi.org/pypi/httpcore/1.0.9/json) |
| [httpcore2 2.9.1](https://pypi.org/project/httpcore2/2.9.1/) | Transitive through HTTPX2; optional `full`. | Low-level HTTP transport used by HTTPX2. Python implementation; no compiled extension. | [BSD-3-Clause](https://pypi.org/pypi/httpcore2/2.9.1/json) |
| [httpx 0.28.1](https://pypi.org/project/httpx/0.28.1/) | Direct `full`; optional. | HTTP client accepted as the deprecated compatibility fallback by Starlette's [TestClient](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/testclient.py). Python implementation; no compiled extension. | [BSD-3-Clause](https://pypi.org/pypi/httpx/0.28.1/json) |
| [httpx2 2.9.1](https://pypi.org/project/httpx2/2.9.1/) | Direct `full`; optional. The dev group separately requests its `zstd` extra. | Preferred HTTP client for Starlette's [TestClient](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/testclient.py). Python implementation; no compiled extension. | [BSD-3-Clause](https://pypi.org/pypi/httpx2/2.9.1/json) |
| [itsdangerous 2.2.0](https://pypi.org/project/itsdangerous/2.2.0/) | Direct `full`; optional. | Timestamp signing used by Starlette's [session middleware](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/middleware/sessions.py). Python implementation; no compiled extension. | [BSD license classifier; exact SPDX variant is not stated in the release metadata.](https://pypi.org/pypi/itsdangerous/2.2.0/json) |
| [jinja2 3.1.6](https://pypi.org/project/jinja2/3.1.6/) | Direct `full`; optional. | Template engine used by Starlette's [Jinja2 templates](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/templating.py). Python implementation; no compiled extension. | [BSD license classifier; exact SPDX variant is not stated in the release metadata.](https://pypi.org/pypi/jinja2/3.1.6/json) |
| [markupsafe 3.0.2](https://pypi.org/project/markupsafe/3.0.2/) | Transitive through Jinja2; optional `full`. | HTML/XML escaping support for Jinja2. Python implementation with an optional C speedup extension. | [BSD-3-Clause](https://pypi.org/pypi/markupsafe/3.0.2/json) |
| [python-multipart 0.0.32](https://pypi.org/project/python-multipart/0.0.32/) | Direct `full`; optional. | Multipart and form parsing used by Starlette's [form parsers](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/formparsers.py). Python implementation; no compiled extension. | [Apache-2.0](https://pypi.org/pypi/python-multipart/0.0.32/json) |
| [pyyaml 6.0.3](https://pypi.org/project/PyYAML/6.0.3/) | Direct `full`; optional. | YAML load/dump support for Starlette's [schema helpers](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/schemas.py). Python implementation with a LibYAML-backed C extension when available. | [MIT](https://pypi.org/pypi/pyyaml/6.0.3/json) |
| [truststore 0.10.4](https://pypi.org/project/truststore/0.10.4/) | Transitive through HTTPX2/HTTP Core 2; optional `full`. | Lets HTTPX2 verify certificates with the operating system's trust store. Python implementation calling platform trust-store APIs; no bundled compiled extension. | [MIT](https://pypi.org/pypi/truststore/0.10.4/json) |

These are upstream optional Starlette capabilities, not a requirement that a
FastAPI-RS target environment install the `full` extra. The exact source call
sites for the optional behavior are linked above; lock reachability by itself
does not establish that FastAPI-RS uses those libraries.

## Development and documentation profiles

The tagged project declares `dev` and `docs` dependency groups and configures
both as `uv` default groups. The direct locked roots and their roles are:

| Group | Direct locked roots | Profile purpose |
| --- | --- | --- |
| `dev` | `coverage==7.15.2`; `httpx2[zstd]==2.9.1`; `importlib-metadata==9.0.0`; `mypy==2.1.0`; `pytest==9.1.1`; `pytest-codspeed==5.0.3`; `ruff==0.16.0`; `starlette[full]` (editable source root); `trio==0.33.0`; `twine==7.0.0`; `types-pyyaml==6.0.12.20250516` | Coverage, tests and benchmarks, alternate Trio backend, type checking, linting, and distribution checks; also activates Starlette's optional `full` extra. These are source-project development tools. |
| `docs` | `black==26.5.1`; `mkdocstrings==1.0.6`; `mkdocstrings-python==2.0.5`; `zensical==0.0.51` | Documentation formatting, API reference integration, and site generation. These are source-project documentation tools. |

Traversing each group from the source lock yields 65 third-party distributions
for `dev` and 33 for `docs`, each count including the base runtime closure.
With both configured default groups enabled, their combined lock union is 85
third-party distributions plus the editable Starlette root. The lock includes
platform- and Python-conditional development packages, so these counts describe
lock reachability, not one universal installation set. None of these group
closures changes FastAPI-RS's target runtime dependency policy.

The dev-only `httpx2[zstd]` root additionally reaches
[`zstandard==0.25.0`](https://pypi.org/project/zstandard/0.25.0/) when
Python is `<3.14`; it is a BSD-3-Clause Python binding with compiled C
extensions. `zstandard` is not part of the `full` extra closure by itself.

## Complete locked development and documentation closure

The `dev` and `docs` rows below enumerate the marker-union lock closures: 65
third-party distributions for `dev` (which includes `starlette[full]` and the
`httpx2[zstd]` development extra), 33 for `docs` (including the required
Starlette runtime closure), and 85 in their union. The 86 lock records are the
editable source root plus those 85 registry distributions; each appears once
in the ledger.

The role column distinguishes runtime, `full`, `dev`, and `docs` reachability,
including direct roots and representative locked parent paths. The distribution
link records the exact release version resolved by the pinned lock; the license
link opens that exact release's PyPI JSON metadata. Purpose is drawn from the
pinned project/source inventory and lock paths. Language labels and available wheel kinds come from the pinned Starlette-RS
[locked-dependencies.csv snapshot for 2026-09-27](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/docs/locked-dependencies.csv),
cross-checked against each exact-release PyPI record. Where native code was not
established, the cell says so instead of inferring it from a platform wheel. This is a metadata inventory, not a review of every archive license file or
selected installed wheel binary. PyPI JSON metadata omits a license for
`mypy-extensions==1.1.0`, but the pinned [Starlette lock](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/uv.lock#L1008-L1014)
selects an sdist with SHA-256
`52e68efc3284861e772bbcd66823fde5ae21fd2fdb51c62a211403730b916558`.
FastAPI 0.141.1's [lock](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/uv.lock#L2393-L2399)
selects the same sdist hash, and its inventory records the exact-version
source archive's `LICENSE` as MIT. The package's
[1.1.0 `LICENSE`](https://github.com/python/mypy_extensions/blob/1.1.0/LICENSE)
confirms that classification. This resolves the package-level license
classification; the lock still does not identify a selected artifact for
every platform.

| Distribution and locked version | Role, profile, and lock path | Feature purpose; language/native component | Reported license metadata |
| --- | --- | --- | --- |
| [starlette 1.6.0 (editable source root)](https://github.com/Kludex/starlette/tree/4f250d6b814587e20c5365f0a5f0c4d42bcb929f) | Editable project root; owns the runtime, `full`, `dev`, and `docs` selections; not a third-party registry record. | Pinned Starlette source/oracle project; Python ASGI framework; package metadata declares no native implementation. | [BSD-3-Clause](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/pyproject.toml) |
| [anyio==4.14.2](https://pypi.org/project/anyio/4.14.2/) | runtime direct; full transitive via `httpx`; dev transitive via `httpx2[zstd]`; docs inherits project runtime | Async task groups, cancellation, thread offload, and backend-neutral concurrency; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/anyio/4.14.2/json) |
| [ast-serialize==0.6.0](https://pypi.org/project/ast-serialize/0.6.0/) | dev transitive via `mypy` | Transitive dependency required by: mypy; implementation/native: the verified [cp39-abi3 macOS arm64 wheel](https://files.pythonhosted.org/packages/c1/f6/ec7ec652c51db77c2f61d8573338e13e4704303265ccc658cb4031d9f354/ast_serialize-0.6.0-cp39-abi3-macosx_11_0_arm64.whl) matches the Starlette lock SHA-256 `e61580a69faf47e3689795367ed211f2a10fd741478cc0f36a0f128793360aad`; it contains `ast_serialize/ast_serialize.abi3.so`, a Mach-O 64-bit arm64 shared library. Its `WHEEL` metadata declares `cp39-abi3-macosx_11_0_arm64` and `Generator: maturin (1.14.1)`; its `METADATA` lists the Rust classifier. This verifies one platform artifact; other platform variants are not reviewed. | MIT, declared by the verified wheel's `METADATA`; the archive includes `licenses/LICENSE`. |
| [attrs==25.3.0](https://pypi.org/project/attrs/25.3.0/) | dev transitive via `trio` | Transitive dependency required by: outcome, trio; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/attrs/25.3.0/json) |
| [backports-tarfile==1.2.0](https://pypi.org/project/backports-tarfile/1.2.0/) | dev transitive via `twine` → `keyring` → `jaraco-context` | Transitive dependency required by: jaraco-context; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/backports-tarfile/1.2.0/json) |
| [black==26.5.1](https://pypi.org/project/black/26.5.1/) | docs direct | Format Python snippets in documentation; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT](https://pypi.org/pypi/black/26.5.1/json) |
| [certifi==2025.8.3](https://pypi.org/project/certifi/2025.8.3/) | full transitive via `httpx`; dev transitive via `starlette[full]` → `httpx` | Transitive dependency required by: httpcore, httpx, requests; implementation/native: Python; universal wheel; native implementation not inferred. | [MPL-2.0](https://pypi.org/pypi/certifi/2025.8.3/json) |
| [cffi==2.0.0](https://pypi.org/project/cffi/2.0.0/) | dev transitive via `trio` | Transitive dependency required by: cryptography, trio; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT](https://pypi.org/pypi/cffi/2.0.0/json) |
| [charset-normalizer==3.4.3](https://pypi.org/project/charset-normalizer/3.4.3/) | dev transitive via `twine` → `requests` | Transitive dependency required by: requests; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT](https://pypi.org/pypi/charset-normalizer/3.4.3/json) |
| [click==8.2.1](https://pypi.org/project/click/8.2.1/) | docs transitive via `black` | Transitive dependency required by: black, mkdocs, zensical; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/click/8.2.1/json) |
| [colorama==0.4.6](https://pypi.org/project/colorama/0.4.6/) | dev transitive via `pytest`; docs transitive via `black` → `click` | Transitive dependency required by: click, mkdocs, pytest; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD license label; exact SPDX variant unknown](https://pypi.org/pypi/colorama/0.4.6/json) |
| [coverage==7.15.2](https://pypi.org/project/coverage/7.15.2/) | dev direct | Coverage collection/reporting; implementation/native: Python; optional C tracer is documented upstream; exact built variant not selected here. | [Apache-2.0](https://pypi.org/pypi/coverage/7.15.2/json) |
| [cryptography==48.0.1](https://pypi.org/project/cryptography/48.0.1/) | dev transitive via `twine` → `keyring` → `secretstorage` | Transitive dependency required by: secretstorage; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [Apache-2.0 OR BSD-3-Clause](https://pypi.org/pypi/cryptography/48.0.1/json) |
| [deepmerge==2.0](https://pypi.org/project/deepmerge/2.0/) | docs transitive via `zensical` | Transitive dependency required by: zensical; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/deepmerge/2.0/json) |
| [docutils==0.22](https://pypi.org/project/docutils/0.22/) | dev transitive via `twine` → `readme-renderer` | Transitive dependency required by: readme-renderer; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD license label; exact SPDX variant unknown](https://pypi.org/pypi/docutils/0.22/json) |
| [exceptiongroup==1.3.0](https://pypi.org/project/exceptiongroup/1.3.0/) | runtime transitive via `anyio`; full transitive via `httpx` → `anyio`; dev transitive via `pytest`; docs inherits project runtime | Transitive dependency required by: anyio, pytest, trio; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/exceptiongroup/1.3.0/json) |
| [ghp-import==2.1.0](https://pypi.org/project/ghp-import/2.1.0/) | docs transitive via `mkdocstrings` → `mkdocs` | Transitive dependency required by: mkdocs; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache Software License label; version/expression unknown](https://pypi.org/pypi/ghp-import/2.1.0/json) |
| [griffelib==2.0.0](https://pypi.org/project/griffelib/2.0.0/) | docs transitive via `mkdocstrings-python` | Transitive dependency required by: mkdocstrings-python; implementation/native: Python; universal wheel; native implementation not inferred. | [ISC](https://pypi.org/pypi/griffelib/2.0.0/json) |
| [h11==0.16.0](https://pypi.org/project/h11/0.16.0/) | full transitive via `httpx` → `httpcore`; dev transitive via `httpx2[zstd]` → `httpcore2` | Transitive dependency required by: httpcore, httpcore2; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/h11/0.16.0/json) |
| [httpcore==1.0.9](https://pypi.org/project/httpcore/1.0.9/) | full transitive via `httpx`; dev transitive via `starlette[full]` → `httpx` | Transitive dependency required by: httpx; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/httpcore/1.0.9/json) |
| [httpcore2==2.9.1](https://pypi.org/project/httpcore2/2.9.1/) | full transitive via `httpx2`; dev transitive via `httpx2[zstd]` | Transitive dependency required by: httpx2; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/httpcore2/2.9.1/json) |
| [httpx==0.28.1](https://pypi.org/project/httpx/0.28.1/) | full direct; dev transitive via `starlette[full]` | Deprecated TestClient transport/backend compatibility; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/httpx/0.28.1/json) |
| [httpx2==2.9.1](https://pypi.org/project/httpx2/2.9.1/) | full direct; dev direct (`httpx2[zstd]`) | Preferred TestClient backend; zstd extra is enabled in dev; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/httpx2/2.9.1/json) |
| [id==1.5.0](https://pypi.org/project/id/1.5.0/) | dev transitive via `twine` | Transitive dependency required by: twine; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache Software License label; version/expression unknown](https://pypi.org/pypi/id/1.5.0/json) |
| [idna==3.18](https://pypi.org/project/idna/3.18/) | runtime transitive via `anyio`; full transitive via `httpx`; dev transitive via `httpx2[zstd]`; docs inherits project runtime | Transitive dependency required by: anyio, httpx, httpx2, requests, trio; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/idna/3.18/json) |
| [importlib-metadata==9.0.0](https://pypi.org/project/importlib-metadata/9.0.0/) | dev direct | Distribution metadata compatibility checks; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/importlib-metadata/9.0.0/json) |
| [iniconfig==2.1.0](https://pypi.org/project/iniconfig/2.1.0/) | dev transitive via `pytest` | Transitive dependency required by: pytest; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/iniconfig/2.1.0/json) |
| [itsdangerous==2.2.0](https://pypi.org/project/itsdangerous/2.2.0/) | full direct; dev transitive via `starlette[full]` | Signing and validating SessionMiddleware cookies; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD license label; exact SPDX variant unknown](https://pypi.org/pypi/itsdangerous/2.2.0/json) |
| [jaraco-classes==3.4.0](https://pypi.org/project/jaraco-classes/3.4.0/) | dev transitive via `twine` → `keyring` | Transitive dependency required by: keyring; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/jaraco-classes/3.4.0/json) |
| [jaraco-context==6.0.1](https://pypi.org/project/jaraco-context/6.0.1/) | dev transitive via `twine` → `keyring` | Transitive dependency required by: keyring; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/jaraco-context/6.0.1/json) |
| [jaraco-functools==4.3.0](https://pypi.org/project/jaraco-functools/4.3.0/) | dev transitive via `twine` → `keyring` | Transitive dependency required by: keyring; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/jaraco-functools/4.3.0/json) |
| [jeepney==0.9.0](https://pypi.org/project/jeepney/0.9.0/) | dev transitive via `twine` → `keyring` | Transitive dependency required by: keyring, secretstorage; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/jeepney/0.9.0/json) |
| [jinja2==3.1.6](https://pypi.org/project/jinja2/3.1.6/) | full direct; dev transitive via `starlette[full]`; docs transitive via `mkdocstrings` | Rendering Jinja2Templates; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD license label; exact SPDX variant unknown](https://pypi.org/pypi/jinja2/3.1.6/json) |
| [keyring==25.6.0](https://pypi.org/project/keyring/25.6.0/) | dev transitive via `twine` | Transitive dependency required by: twine; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/keyring/25.6.0/json) |
| [librt==0.13.0](https://pypi.org/project/librt/0.13.0/) | dev transitive via `mypy` | Transitive dependency required by: mypy; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT](https://pypi.org/pypi/librt/0.13.0/json) |
| [markdown==3.9](https://pypi.org/project/markdown/3.9/) | docs transitive via `mkdocstrings` | Transitive dependency required by: mkdocs, mkdocs-autorefs, mkdocstrings, pymdown-extensions, zensical; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/markdown/3.9/json) |
| [markdown-it-py==4.0.0](https://pypi.org/project/markdown-it-py/4.0.0/) | dev transitive via `pytest-codspeed` → `rich` | Transitive dependency required by: rich; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/markdown-it-py/4.0.0/json) |
| [markupsafe==3.0.2](https://pypi.org/project/markupsafe/3.0.2/) | full transitive via `jinja2`; dev transitive via `starlette[full]` → `jinja2`; docs transitive via `mkdocstrings` | Transitive dependency required by: jinja2, mkdocs, mkdocs-autorefs, mkdocstrings; implementation/native: Python with optional C speedup; wheel/source build variant can differ. | [BSD 3-clause text; SPDX expression not reported](https://pypi.org/pypi/markupsafe/3.0.2/json) |
| [mdurl==0.1.2](https://pypi.org/project/mdurl/0.1.2/) | dev transitive via `pytest-codspeed` → `rich` → `markdown-it-py` | Transitive dependency required by: markdown-it-py; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/mdurl/0.1.2/json) |
| [mergedeep==1.3.4](https://pypi.org/project/mergedeep/1.3.4/) | docs transitive via `mkdocstrings` → `mkdocs` | Transitive dependency required by: mkdocs, mkdocs-get-deps; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/mergedeep/1.3.4/json) |
| [mkdocs==1.6.1](https://pypi.org/project/mkdocs/1.6.1/) | docs transitive via `mkdocstrings` | Transitive dependency required by: mkdocs-autorefs, mkdocstrings; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD license label; exact SPDX variant unknown](https://pypi.org/pypi/mkdocs/1.6.1/json) |
| [mkdocs-autorefs==1.4.3](https://pypi.org/project/mkdocs-autorefs/1.4.3/) | docs transitive via `mkdocstrings` | Transitive dependency required by: mkdocstrings, mkdocstrings-python; implementation/native: Python; universal wheel; native implementation not inferred. | [ISC](https://pypi.org/pypi/mkdocs-autorefs/1.4.3/json) |
| [mkdocs-get-deps==0.2.0](https://pypi.org/project/mkdocs-get-deps/0.2.0/) | docs transitive via `mkdocstrings` → `mkdocs` | Transitive dependency required by: mkdocs; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/mkdocs-get-deps/0.2.0/json) |
| [mkdocstrings==1.0.6](https://pypi.org/project/mkdocstrings/1.0.6/) | docs direct | Render API documentation; implementation/native: Python; universal wheel; native implementation not inferred. | [ISC](https://pypi.org/pypi/mkdocstrings/1.0.6/json) |
| [mkdocstrings-python==2.0.5](https://pypi.org/project/mkdocstrings-python/2.0.5/) | docs direct | Python API documentation handler; implementation/native: Python; universal wheel; native implementation not inferred. | [ISC](https://pypi.org/pypi/mkdocstrings-python/2.0.5/json) |
| [more-itertools==10.8.0](https://pypi.org/project/more-itertools/10.8.0/) | dev transitive via `twine` → `keyring` → `jaraco-classes` | Transitive dependency required by: jaraco-classes, jaraco-functools; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/more-itertools/10.8.0/json) |
| [mypy==2.1.0](https://pypi.org/project/mypy/2.1.0/) | dev direct | Strict type checking; implementation/native: Python; mypyc-compiled distributions are available, but this lock does not select a wheel variant. | [MIT](https://pypi.org/pypi/mypy/2.1.0/json) |
| [mypy-extensions==1.1.0](https://pypi.org/project/mypy-extensions/1.1.0/) | dev transitive via `mypy`; docs transitive via `black` | Transitive dependency required by: black, mypy; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT (same locked sdist reviewed in the FastAPI source-lock inventory)](https://github.com/python/mypy_extensions/blob/1.1.0/LICENSE) |
| [nh3==0.3.0](https://pypi.org/project/nh3/0.3.0/) | dev transitive via `twine` → `readme-renderer` | Transitive dependency required by: readme-renderer; implementation/native: Python/Rust classifiers; platform-specific wheels; exact native/runtime component not audited. | [MIT](https://pypi.org/pypi/nh3/0.3.0/json) |
| [outcome==1.3.0.post0](https://pypi.org/project/outcome/1.3.0.post0/) | dev transitive via `trio` | Transitive dependency required by: trio; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT OR Apache-2.0](https://pypi.org/pypi/outcome/1.3.0.post0/json) |
| [packaging==26.2](https://pypi.org/project/packaging/26.2/) | dev transitive via `pytest`; docs transitive via `black` | Transitive dependency required by: black, mkdocs, pytest, twine; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0 OR BSD-2-Clause](https://pypi.org/pypi/packaging/26.2/json) |
| [pathspec==1.0.4](https://pypi.org/project/pathspec/1.0.4/) | dev transitive via `mypy`; docs transitive via `black` | Transitive dependency required by: black, mkdocs, mypy; implementation/native: Python; universal wheel; native implementation not inferred. | [MPL-2.0](https://pypi.org/pypi/pathspec/1.0.4/json) |
| [platformdirs==4.4.0](https://pypi.org/project/platformdirs/4.4.0/) | docs transitive via `black` | Transitive dependency required by: black, mkdocs-get-deps; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/platformdirs/4.4.0/json) |
| [pluggy==1.6.0](https://pypi.org/project/pluggy/1.6.0/) | dev transitive via `pytest` | Transitive dependency required by: pytest; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/pluggy/1.6.0/json) |
| [pycparser==2.22](https://pypi.org/project/pycparser/2.22/) | dev transitive via `trio` → `cffi` | Transitive dependency required by: cffi; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/pycparser/2.22/json) |
| [pygments==2.20.0](https://pypi.org/project/pygments/2.20.0/) | dev transitive via `pytest`; docs transitive via `zensical` | Transitive dependency required by: pytest, readme-renderer, rich, zensical; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-2-Clause](https://pypi.org/pypi/pygments/2.20.0/json) |
| [pymdown-extensions==11.0.1](https://pypi.org/project/pymdown-extensions/11.0.1/) | docs transitive via `mkdocstrings` | Transitive dependency required by: mkdocstrings, zensical; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/pymdown-extensions/11.0.1/json) |
| [pytest==9.1.1](https://pypi.org/project/pytest/9.1.1/) | dev direct | Upstream test runner; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/pytest/9.1.1/json) |
| [pytest-codspeed==5.0.3](https://pypi.org/project/pytest-codspeed/5.0.3/) | dev direct | CodSpeed benchmark integration; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT license text](https://pypi.org/pypi/pytest-codspeed/5.0.3/json) |
| [python-dateutil==2.9.0.post0](https://pypi.org/project/python-dateutil/2.9.0.post0/) | docs transitive via `mkdocstrings` → `mkdocs` → `ghp-import` | Transitive dependency required by: ghp-import; implementation/native: Python; universal wheel; native implementation not inferred. | [Dual license label; exact expression unknown](https://pypi.org/pypi/python-dateutil/2.9.0.post0/json) |
| [python-multipart==0.0.32](https://pypi.org/project/python-multipart/0.0.32/) | full direct; dev transitive via `starlette[full]` | Parsing multipart forms and uploaded files; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/python-multipart/0.0.32/json) |
| [pytokens==0.4.1](https://pypi.org/project/pytokens/0.4.1/) | docs transitive via `black` | Transitive dependency required by: black; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT license text](https://pypi.org/pypi/pytokens/0.4.1/json) |
| [pywin32-ctypes==0.2.3](https://pypi.org/project/pywin32-ctypes/0.2.3/) | dev transitive via `twine` → `keyring` | Transitive dependency required by: keyring; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/pywin32-ctypes/0.2.3/json) |
| [pyyaml==6.0.3](https://pypi.org/project/PyYAML/6.0.3/) | full direct; dev transitive via `starlette[full]`; docs transitive via `zensical` | YAML schema support; implementation/native: Python/Cython; optional LibYAML C extension; exact linked component is not established here. | [MIT](https://pypi.org/pypi/pyyaml/6.0.3/json) |
| [pyyaml-env-tag==1.1](https://pypi.org/project/pyyaml-env-tag/1.1/) | docs transitive via `mkdocstrings` → `mkdocs` | Transitive dependency required by: mkdocs; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/pyyaml-env-tag/1.1/json) |
| [readme-renderer==44.0](https://pypi.org/project/readme-renderer/44.0/) | dev transitive via `twine` | Transitive dependency required by: twine; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/readme-renderer/44.0/json) |
| [requests==2.33.0](https://pypi.org/project/requests/2.33.0/) | dev transitive via `twine` | Transitive dependency required by: id, requests-toolbelt, twine; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/requests/2.33.0/json) |
| [requests-toolbelt==1.0.0](https://pypi.org/project/requests-toolbelt/1.0.0/) | dev transitive via `twine` | Transitive dependency required by: twine; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/requests-toolbelt/1.0.0/json) |
| [rfc3986==2.0.0](https://pypi.org/project/rfc3986/2.0.0/) | dev transitive via `twine` | Transitive dependency required by: twine; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/rfc3986/2.0.0/json) |
| [rich==15.0.0](https://pypi.org/project/rich/15.0.0/) | dev transitive via `pytest-codspeed` | Transitive dependency required by: pytest-codspeed, twine; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/rich/15.0.0/json) |
| [ruff==0.16.0](https://pypi.org/project/ruff/0.16.0/) | dev direct | Linting and formatting; implementation/native: Rust executable distributed for Python tooling; native executable. | [MIT](https://pypi.org/pypi/ruff/0.16.0/json) |
| [secretstorage==3.3.3](https://pypi.org/project/secretstorage/3.3.3/) | dev transitive via `twine` → `keyring` | Transitive dependency required by: keyring; implementation/native: Python; universal wheel; native implementation not inferred. | [BSD-3-Clause](https://pypi.org/pypi/secretstorage/3.3.3/json) |
| [six==1.17.0](https://pypi.org/project/six/1.17.0/) | docs transitive via `mkdocstrings` → `mkdocs` → `ghp-import` → `python-dateutil` | Transitive dependency required by: python-dateutil; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/six/1.17.0/json) |
| [sniffio==1.3.1](https://pypi.org/project/sniffio/1.3.1/) | dev transitive via `trio` | Transitive dependency required by: trio; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT OR Apache-2.0](https://pypi.org/pypi/sniffio/1.3.1/json) |
| [sortedcontainers==2.4.0](https://pypi.org/project/sortedcontainers/2.4.0/) | dev transitive via `trio` | Transitive dependency required by: trio; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/sortedcontainers/2.4.0/json) |
| [tomli==2.4.1](https://pypi.org/project/tomli/2.4.1/) | dev transitive via `mypy`; docs transitive via `black` | Transitive dependency required by: black, mypy, pytest, zensical; implementation/native: Python; platform-specific wheel(s); native/runtime component not audited. | [MIT](https://pypi.org/pypi/tomli/2.4.1/json) |
| [trio==0.33.0](https://pypi.org/project/trio/0.33.0/) | dev direct | AnyIO alternate-backend test and TestClient parity coverage; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT OR Apache-2.0](https://pypi.org/pypi/trio/0.33.0/json) |
| [truststore==0.10.4](https://pypi.org/project/truststore/0.10.4/) | full transitive via `httpx2`; dev transitive via `httpx2[zstd]` | Transitive dependency required by: httpcore2, httpx2; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/truststore/0.10.4/json) |
| [twine==7.0.0](https://pypi.org/project/twine/7.0.0/) | dev direct | Inspect built Python distributions; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/twine/7.0.0/json) |
| [types-pyyaml==6.0.12.20250516](https://pypi.org/project/types-pyyaml/6.0.12.20250516/) | dev direct | PyYAML typing stubs; implementation/native: Python; universal wheel; native implementation not inferred. | [Apache-2.0](https://pypi.org/pypi/types-pyyaml/6.0.12.20250516/json) |
| [typing-extensions==4.15.0](https://pypi.org/project/typing-extensions/4.15.0/) | runtime direct; full transitive via `httpx2`; dev transitive via `httpx2[zstd]`; docs inherits project runtime | Typing backports on Python versions below 3.13; implementation/native: Python; universal wheel; native implementation not inferred. | [PSF-2.0](https://pypi.org/pypi/typing-extensions/4.15.0/json) |
| [urllib3==2.7.0](https://pypi.org/project/urllib3/2.7.0/) | dev transitive via `twine` | Transitive dependency required by: requests, twine; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/urllib3/2.7.0/json) |
| [watchdog==6.0.0](https://pypi.org/project/watchdog/6.0.0/) | docs transitive via `mkdocstrings` → `mkdocs` | Transitive dependency required by: mkdocs; implementation/native: Python/C classifiers; platform-specific wheels; exact native/runtime component not audited. | [Apache-2.0](https://pypi.org/pypi/watchdog/6.0.0/json) |
| [zensical==0.0.51](https://pypi.org/project/zensical/0.0.51/) | docs direct | Build the upstream documentation site; implementation/native: Python/Rust classifiers; platform-specific wheels; exact native/runtime component not audited. | [MIT](https://pypi.org/pypi/zensical/0.0.51/json) |
| [zipp==3.23.0](https://pypi.org/project/zipp/3.23.0/) | dev transitive via `importlib-metadata` | Transitive dependency required by: importlib-metadata; implementation/native: Python; universal wheel; native implementation not inferred. | [MIT](https://pypi.org/pypi/zipp/3.23.0/json) |
| [zstandard==0.25.0](https://pypi.org/project/zstandard/0.25.0/) | dev transitive via `httpx2[zstd]` | The httpx2[zstd] development/test extra; implementation/native: Python binding with compiled C extension; dev extra only. | [BSD-3-Clause](https://pypi.org/pypi/zstandard/0.25.0/json) |

Conditional edges remain conditional in the source lock. In particular, the
base `exceptiongroup` backport is selected below Python 3.11; `typing-extensions`
is a Starlette runtime requirement below Python 3.13 but also appears through
other tools; `zstandard` is selected by `httpx2[zstd]` below Python 3.14; and
several tool edges are platform-conditional. Counts above describe the union of
reachable locked records, not a single universal install. The lock and package
metadata links above are the evidence for exact markers and versions.

## Build backend: unresolved in this lock

The tagged `pyproject.toml` declares the build requirement as unversioned
`hatchling` and the backend as `hatchling.build`. There is no `hatchling`
package record in this `uv.lock`, so this source lock does not resolve the
backend version or its transitive build closure. Treat the version and closure
as **unknown**, and the backend as a **build-only** input. Do not infer a
version from the runtime, `dev`, or `docs` groups.

The linked FastAPI 0.141.1 source-lock row remains unchanged; its lock is not
an input to this Starlette 1.6.0 profile.

## Starlette-RS Python runtime and optional-extra closure at `4139a72`

This record uses
[`pyproject.toml`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/pyproject.toml)
and
[`uv.lock`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/uv.lock)
from the pinned Starlette-RS checkout. The lock SHA-256 is
`26951717298e46e5c647688df1310f3a4c516d70b75620314dba5e04594ddb6b`; it contains the editable
`starlette-rs-py` root and 17 registry distributions. The project requires Python `>=3.10`;
its root version is dynamic and is not resolved in the editable lock record, so that
distribution version is **not established by this lock**. The source commit is the package
identity used here.

`pyproject.toml` declares `anyio>=3.6.2,<5` and `typing-extensions>=4.12.0` as runtime
roots. Its optional groups are `full = [itsdangerous, jinja2, python-multipart>=0.0.18,
pyyaml, httpx>=0.27.0,<0.29.0, httpx2>=2.0.0]`, `schemas = [pyyaml]`,
`templates = [jinja2]`, and `testclient = [httpx>=0.27.0,<0.29.0, httpx2>=2.0.0]`.
The lock's reachable-record union resolves runtime to four external distributions; runtime
plus `schemas` to five; runtime plus `templates` to six; runtime plus `testclient` to twelve;
and runtime plus `full` to all 17 registry distributions. On ordinary platforms, the `full`
extra installs 16 external distributions; the additional record is the WebAssembly-only
`httpx2-jsfetch` dependency. The `full` extra includes the specialized optional features and
adds `itsdangerous` and `python-multipart`. Group sets overlap through AnyIO, HTTP clients,
and their shared transitive packages.
Versions below come from the pinned lock; per-release metadata links document reported
licenses and available Python/wheel metadata. Source call sites for the optional
integrations are
[`formparsers.py`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/python/starlette/formparsers.py),
[`sessions.py`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/python/starlette/middleware/sessions.py),
[`schemas.py`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/python/starlette/schemas.py),
[`templating.py`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/python/starlette/templating.py),
and
[`testclient.py`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/starlette-rs-py/python/starlette/testclient.py).
The source [`dependency
inventory`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/docs/DEPENDENCIES.md)
documents the intended client backend roles.

| Distribution and locked version | Role in runtime/extra closure | Feature purpose; language/native component | Reported license metadata |
| --- | --- | --- | --- |
| [`starlette-rs-py` (editable; version dynamic)](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/pyproject.toml) | Source project root; not an external extra dependency. | Python package with Rust/PyO3 extension module (`starlette_rs_py._core`); Rust core is outside this Python-distribution closure. | [`BSD-3-Clause`](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/pyproject.toml) |
| [anyio==4.15.1](https://pypi.org/project/anyio/4.15.1/) | runtime direct; testclient transitive via httpx and httpx2 | Async concurrency backend shared by the runtime and client transport; Python; universal wheel, native component not indicated | [MIT](https://pypi.org/pypi/anyio/4.15.1/json) |
| [certifi==2026.7.22](https://pypi.org/project/certifi/2026.7.22/) | testclient/full transitive via httpx | Mozilla CA bundle used by the deprecated HTTPX compatibility backend; Python certificate data; universal wheel, native component not indicated | [MPL-2.0](https://pypi.org/pypi/certifi/2026.7.22/json) |
| [exceptiongroup==1.3.1](https://pypi.org/project/exceptiongroup/1.3.1/) | runtime transitive via anyio; testclient/full share that path (Python <3.11) | Backport used by AnyIO on Python versions without built-in exception groups; Python; universal wheel, no native component indicated | [MIT classifier; SPDX expression not reported](https://pypi.org/pypi/exceptiongroup/1.3.1/json) |
| [h11==0.16.0](https://pypi.org/project/h11/0.16.0/) | testclient/full transitive via httpcore and httpcore2 | HTTP/1.1 protocol implementation for both client backends; Python; universal wheel, native component not indicated | [MIT](https://pypi.org/pypi/h11/0.16.0/json) |
| [httpcore==1.0.9](https://pypi.org/project/httpcore/1.0.9/) | testclient/full transitive via httpx | Low-level transport for the deprecated HTTPX compatibility backend; Python; universal wheel, native component not indicated | [BSD-3-Clause](https://pypi.org/pypi/httpcore/1.0.9/json) |
| [httpcore2==2.13.1](https://pypi.org/project/httpcore2/2.13.1/) | testclient/full transitive via httpx2 | Low-level transport for the preferred HTTPX2 backend; Python; universal wheel, native component not indicated | [BSD-3-Clause](https://pypi.org/pypi/httpcore2/2.13.1/json) |
| [httpx==0.28.1](https://pypi.org/project/httpx/0.28.1/) | testclient and full direct optional dependency | Deprecated TestClient transport/backend compatibility; Python; universal wheel, native component not indicated | [BSD-3-Clause](https://pypi.org/pypi/httpx/0.28.1/json) |
| [httpx2==2.13.1](https://pypi.org/project/httpx2/2.13.1/) | testclient and full direct optional dependency | Preferred TestClient backend; Python; universal wheel, native component not indicated | [BSD-3-Clause](https://pypi.org/pypi/httpx2/2.13.1/json) |
| [httpx2-jsfetch==1.0](https://pypi.org/project/httpx2-jsfetch/1.0/) | testclient/full transitive via httpx2; lock marker Python >=3.12 and sys_platform == emscripten | Browser/Pyodide fetch transport adapter selected only under the lock marker; Python; universal wheel; browser JS API use is not a native component | [BSD-3-Clause](https://pypi.org/pypi/httpx2-jsfetch/1.0/json) |
| [idna==3.20](https://pypi.org/project/idna/3.20/) | runtime transitive via anyio; testclient/full transitive via httpx and httpx2 | Internationalized domain-name encoding for async networking and HTTP clients; Python; universal wheel, native component not indicated | [BSD-3-Clause](https://pypi.org/pypi/idna/3.20/json) |
| [itsdangerous==2.2.0](https://pypi.org/project/itsdangerous/2.2.0/) | full direct optional dependency | Source-compatible signed-session dependency; Starlette-RS performs session signing and verification in Rust; Python, universal wheel, native component not indicated | [BSD License classifier; SPDX expression not reported](https://pypi.org/pypi/itsdangerous/2.2.0/json) |
| [jinja2==3.1.6](https://pypi.org/project/jinja2/3.1.6/) | templates and full direct optional dependency | Jinja template environment and rendering; Python; universal wheel; uses MarkupSafe and may use its optional C speedup | [BSD license classifier; exact SPDX variant unknown](https://pypi.org/pypi/jinja2/3.1.6/json) |
| [markupsafe==3.0.3](https://pypi.org/project/markupsafe/3.0.3/) | templates/full transitive via jinja2 | Escaping and markup-safe string operations for Jinja; Python with optional C speedup; wheel/source build variant can differ | [BSD-3-Clause](https://pypi.org/pypi/markupsafe/3.0.3/json) |
| [python-multipart==0.0.32](https://pypi.org/project/python-multipart/0.0.32/) | full direct optional dependency (`>=0.0.18`) | Multipart form/upload compatibility import; Starlette-RS parses multipart bodies in Rust; Python, universal wheel, native component not indicated | [Apache-2.0](https://pypi.org/pypi/python-multipart/0.0.32/json) |
| [pyyaml==6.0.3](https://pypi.org/project/PyYAML/6.0.3/) | schemas and full direct optional dependency | YAML docstring/schema parsing and OpenAPI schema responses; Python/Cython; optional LibYAML C extension; exact linked component is not established here | [MIT](https://pypi.org/pypi/pyyaml/6.0.3/json) |
| [truststore==0.10.4](https://pypi.org/project/truststore/0.10.4/) | testclient/full transitive via httpx2 | HTTPX2 system certificate trust integration; Python; universal wheel, uses platform trust APIs; no bundled native component indicated | [MIT](https://pypi.org/pypi/truststore/0.10.4/json) |
| [typing-extensions==4.16.0](https://pypi.org/project/typing-extensions/4.16.0/) | runtime direct; also a conditional AnyIO/HTTPX2 dependency (Python <3.15) | Typing backports required by the declared Python package runtime and client stack; Python; universal wheel, native component not indicated | [PSF-2.0](https://pypi.org/pypi/typing-extensions/4.16.0/json) |

The WebAssembly-only `httpx2-jsfetch` edge is marker-conditional and must not be counted as
installed on ordinary platforms. [`maturin==1.14.1` build-system
requirement](https://github.com/appunni-m/starlette-rs/blob/4139a72449bf5751e8902fb1c7175ee7f191d338/pyproject.toml)
is declared separately; it is not in `uv.lock` and is outside this runtime/extra closure.
Its build-time transitive closure is therefore **unknown from this lock**. The upstream
`uv.lock` does not contain license or implementation fields: package license claims above
link to exact-release PyPI JSON metadata; native-component claims are limited to release
wheel/classifier evidence and the pinned package source. This is not an audit of included
license files or a particular platform's installed wheel.
