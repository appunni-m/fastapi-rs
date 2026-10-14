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
| [anyio 4.14.2](https://pypi.org/project/anyio/4.14.2/) | Direct; runtime. Also reached by the optional HTTP clients. | Async concurrency and thread-offload primitives used throughout Starlette, including its [concurrency helpers](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/concurrency.py). Python implementation; no compiled extension in the locked package. | MIT |
| [typing-extensions 4.15.0](https://pypi.org/project/typing-extensions/4.15.0/) | Direct for Python `<3.13`; also a conditional AnyIO/HTTPX2 dependency. Runtime. | Backports typing names used by Starlette on older Python, including `TypeIs`, `TypeVar`, and `Self` ([source](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/_utils.py)). Python implementation; no compiled extension in the locked package. | PSF-2.0 |
| [exceptiongroup 1.3.0](https://pypi.org/project/exceptiongroup/1.3.0/) | Transitive through AnyIO for Python `<3.11`; runtime only under that marker. | Backport of Python 3.11 exception-group types used by AnyIO on older interpreters. Python-only package; no native component. | MIT |
| [idna 3.18](https://pypi.org/project/idna/3.18/) | Transitive through AnyIO; runtime. Also reached by both optional HTTP clients. | Internationalized domain-name encoding for network destinations. Python implementation; no compiled extension in the locked package. | BSD-3-Clause |

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
| [certifi 2025.8.3](https://pypi.org/project/certifi/2025.8.3/) | Transitive through HTTPX/HTTP Core; optional `full`. | Mozilla CA bundle consumed by the HTTP clients. Python package plus certificate data; no compiled extension. | MPL-2.0 |
| [h11 0.16.0](https://pypi.org/project/h11/0.16.0/) | Transitive through HTTP Core and HTTP Core 2; optional `full`. | Pure-Python HTTP/1.1 protocol implementation. | MIT |
| [httpcore 1.0.9](https://pypi.org/project/httpcore/1.0.9/) | Transitive through HTTPX; optional `full`. | Low-level HTTP transport used by HTTPX. Python implementation; no compiled extension. | BSD-3-Clause |
| [httpcore2 2.9.1](https://pypi.org/project/httpcore2/2.9.1/) | Transitive through HTTPX2; optional `full`. | Low-level HTTP transport used by HTTPX2. Python implementation; no compiled extension. | BSD-3-Clause |
| [httpx 0.28.1](https://pypi.org/project/httpx/0.28.1/) | Direct `full`; optional. | HTTP client accepted as the deprecated compatibility fallback by Starlette's [TestClient](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/testclient.py). Python implementation; no compiled extension. | BSD-3-Clause |
| [httpx2 2.9.1](https://pypi.org/project/httpx2/2.9.1/) | Direct `full`; optional. The dev group separately requests its `zstd` extra. | Preferred HTTP client for Starlette's [TestClient](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/testclient.py). Python implementation; no compiled extension. | BSD-3-Clause |
| [itsdangerous 2.2.0](https://pypi.org/project/itsdangerous/2.2.0/) | Direct `full`; optional. | Timestamp signing used by Starlette's [session middleware](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/middleware/sessions.py). Python implementation; no compiled extension. | BSD license classifier; exact SPDX variant is not stated in the release metadata. |
| [jinja2 3.1.6](https://pypi.org/project/jinja2/3.1.6/) | Direct `full`; optional. | Template engine used by Starlette's [Jinja2 templates](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/templating.py). Python implementation; no compiled extension. | BSD license classifier; exact SPDX variant is not stated in the release metadata. |
| [markupsafe 3.0.2](https://pypi.org/project/markupsafe/3.0.2/) | Transitive through Jinja2; optional `full`. | HTML/XML escaping support for Jinja2. Python implementation with an optional C speedup extension. | BSD-3-Clause |
| [python-multipart 0.0.32](https://pypi.org/project/python-multipart/0.0.32/) | Direct `full`; optional. | Multipart and form parsing used by Starlette's [form parsers](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/formparsers.py). Python implementation; no compiled extension. | Apache-2.0 |
| [pyyaml 6.0.3](https://pypi.org/project/PyYAML/6.0.3/) | Direct `full`; optional. | YAML load/dump support for Starlette's [schema helpers](https://github.com/Kludex/starlette/blob/4f250d6b814587e20c5365f0a5f0c4d42bcb929f/starlette/schemas.py). Python implementation with a LibYAML-backed C extension when available. | MIT |
| [truststore 0.10.4](https://pypi.org/project/truststore/0.10.4/) | Transitive through HTTPX2/HTTP Core 2; optional `full`. | Lets HTTPX2 verify certificates with the operating system's trust store. Python implementation calling platform trust-store APIs; no bundled compiled extension. | MIT |

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

## Build backend: unresolved in this lock

The tagged `pyproject.toml` declares the build requirement as unversioned
`hatchling` and the backend as `hatchling.build`. There is no `hatchling`
package record in this `uv.lock`, so this source lock does not resolve the
backend version or its transitive build closure. Treat the version and closure
as **unknown**, and the backend as a **build-only** input. Do not infer a
version from the runtime, `dev`, or `docs` groups.

The linked FastAPI 0.141.1 source-lock row remains unchanged; its lock is not
an input to this Starlette 1.6.0 profile.
