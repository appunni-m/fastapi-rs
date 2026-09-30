# FastAPI extras and dependency-group crosswalk

Source authority: FastAPI 0.141.1, commit
[`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`](https://github.com/fastapi/fastapi/tree/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f); declarations are in pinned
[`pyproject.toml`](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/pyproject.toml#L44-L187).
Resolved versions, recursive edges, languages/native parts, and license evidence
are in the [dependency atlas](dependency-atlas.md) and
[dependency graph](DEPENDENCY_GRAPH.md).

FastAPI-RS declares `pydantic==2.13.4`, `pydantic-core==2.46.4`, and
`starlette-rs-py==0.1.0` as runtime dependencies
([target metadata](../pyproject.toml#L5-L16)); it has no
project extras, dependency groups, or CLI script. “Absent” below means no target
package/feature mapping is declared, not an explicit exclusion. No explicit
exclusions were found. Presence in a parity/dev environment is not support.

## Published runtime surfaces

| FastAPI surface | Direct packages and purpose | Owner; FastAPI-RS status |
|---|---|---|
| Base | `starlette>=0.46.0`; `pydantic>=2.9.0`; `typing-extensions>=4.8.0`; `typing-inspection>=0.4.2`; `annotated-doc>=0.0.2` | FastAPI orchestration, Pydantic models/schemas, Starlette ASGI behavior. Target directly depends on Pydantic, Pydantic Core, and Starlette-RS; other packages are not direct target requirements. Contract incomplete. |
| `standard` | `fastapi-cli[standard]>=0.0.32`; `fastar>=0.9.0`; `httpx>=0.23.0,<1.0.0`; `jinja2>=3.1.5`; `python-multipart>=0.0.18`; `email-validator>=2.0.0`; `uvicorn[standard]>=0.12.0`; `pydantic-settings>=2.0.0`; `pydantic-extra-types>=2.0.0` | CLI/deployment, TestClient, templates, forms/uploads, email validation, server, settings, extra Pydantic types. No matching target optional extra; Form/File has a Rust-backed implementation slice, while other optional integrations remain unmapped. |
| `standard-no-fastapi-cloud-cli` | `fastapi-cli[standard-no-fastapi-cloud-cli]>=0.0.32`; `httpx>=0.23.0,<1.0.0`; `jinja2>=3.1.5`; `python-multipart>=0.0.18`; `email-validator>=2.0.0`; `uvicorn[standard]>=0.12.0`; `pydantic-settings>=2.0.0`; `pydantic-extra-types>=2.0.0` | Same integration categories as `standard`, without Cloud CLI. No matching target optional extra; Form/File has a Rust-backed implementation slice, while other optional integrations remain unmapped. |
| `all` | `fastapi-cli[standard]>=0.0.32`; `httpx>=0.23.0,<1.0.0`; `jinja2>=3.1.5`; `python-multipart>=0.0.18`; `itsdangerous>=1.1.0`; `pyyaml>=5.3.1`; `email-validator>=2.0.0`; `uvicorn[standard]>=0.12.0`; `pydantic-settings>=2.0.0`; `pydantic-extra-types>=2.0.0` | Adds Starlette session signing and schema support (FastAPI says these are not commonly used with FastAPI). No target extra or mapping; not explicitly excluded. |

## Feature ownership and target mapping

| Package / source-backed feature | Owner | FastAPI-RS target status |
|---|---|---|
| `starlette`: app, routes, requests, responses, middleware, WebSockets, lifespan | Starlette-RS owns generic ASGI behavior | `starlette-rs-py==0.1.0` is direct. Sibling contract is incomplete; see `metadata.yaml`. |
| `pydantic` / `pydantic-core`: Python models, fields, schemas, validation/serialization primitives | Pydantic; FastAPI owns orchestration | Pinned direct dependencies `2.13.4` and `2.46.4`; Rust calls the Pydantic Core wheel API through PyO3. This does not complete FastAPI parity. |
| `typing-extensions`, `typing-inspection`, `annotated-doc`: typing/`Doc` metadata | FastAPI annotation and dependency inspection | Not direct target requirements; pinned in parity setup or present transitively. No optional mapping. |
| `fastapi-cli` / `fastapi-cloud-cli`: command and cloud deployment | Project tooling | No target script, CLI package, or extra. |
| `fastar`: CLI archive creation | Project tooling; resolved Cloud CLI deployment consumer, not FastAPI request handling | No target CLI/deployment extra or package mapping. |
| `httpx`: optional FastAPI test client | Starlette-RS owns TestClient transport | Pinned Starlette-RS `d1ca591` adds context-managed lifespan behavior and parity inputs under its `testclient` extra (`httpx>=0.27,<0.29` and `httpx2>=2`); its Rust-native TestClient binding remains unimplemented. FastAPI-RS does not enable that extra or expose `fastapi.testclient.TestClient`; the FastAPI target binding remains `full-contract-not-established`. |
| `jinja2`: FastAPI re-exports Starlette `Jinja2Templates` | Starlette-RS owns templates | No target extra; pinned sibling source has no `starlette/templating.py`. |
| `python-multipart`: optional upstream form/upload parser for `Form` and `File` | FastAPI owns parameter interpretation; Starlette-RS provides the Rust-backed `Request.form()` boundary | FastAPI-RS has no Python `python-multipart` runtime dependency. Form/File request extraction is implemented in Rust through Starlette-RS; constructor options and full behavior parity remain incomplete. |
| `email-validator`: enables Pydantic `EmailStr`; FastAPI fallback warns and treats values as strings | Pydantic validation with FastAPI fallback | No target optional mapping; target email behavior unresolved. |
| `uvicorn[standard]`: optional ASGI server/accelerators | External server tooling | No target server extra; apps can install an ASGI server separately. |
| `pydantic-settings` | Pydantic ecosystem, not FastAPI core | No target extra or mapping. |
| `pydantic-extra-types`: FastAPI encoder recognizes `Color` | Pydantic with FastAPI encoder integration | No target extra or mapping; Color parity unresolved. |
| `itsdangerous`: signed Starlette `SessionMiddleware` cookies | Starlette-RS owns session behavior | No target `all` mapping; pinned sibling source has no `starlette/middleware/sessions.py`. |
| `pyyaml`: Starlette schema generation | Starlette-RS owns schema feature | Sibling has a separate `schemas` extra, but FastAPI-RS declares no alias or `all` mapping. |

These rows record unresolved packaging/behavior boundaries, not inferred support.
See the [contract manifest](../tests/fixtures/manifest.yaml).

## Build and contributor groups

These groups are project tooling, not runtime feature ownership. `docs` and
`tests` include `docs-tests`; `dev` includes `tests`, `docs`, and `translations`.
Every group below has no matching target dependency group or published optional
extra; exceptions are noted. The [dependency atlas](dependency-atlas.md#build-and-development-dependency-graphs)
records resolved purpose, implementation language, recursive edges, and licenses.

| FastAPI group | Direct packages and source purpose | FastAPI-RS target status |
|---|---|---|
| `docs-tests` | `httpx>=0.23.0,<1.0.0`, `httpx2>=2.0.0` (exercise docs clients); `ruff>=0.14.14` (lint docs/examples) | `ruff` is in `requirements-dev.txt`; no client mapping. |
| `docs` | `black>=25.1.0`, `cairosvg>=2.8.2`, `griffe-typingdoc>=0.3.0`, `griffe-warnings-deprecated>=1.1.0`, `jieba>=0.42.1`, `markdown-include-variants>=0.0.8`, `mdx-include>=1.4.1,<2.0.0`, `mkdocstrings[python]>=1.0.3`, `pillow>=11.3.0`, `python-slugify>=8.0.4`, `pyyaml>=5.3.1,<7.0.0`, `typer>=0.21.1`, `zensical>=0.0.42` (site/API docs, Markdown and asset processing) | `pyyaml` is a repository dev tool, not a published target extra. |
| `tests` | `anyio[trio]>=3.2.1,<5.0.0`, `coverage[toml]>=7.13,<8.0`, `dirty-equals>=0.9.0`, `flask>=3.0.0,<4.0.0`, `inline-snapshot>=0.21.1`, `mypy>=1.14.1`, `pwdlib[argon2]>=0.2.1`, `pyjwt>=2.9.0`, `pytest>=9.0.0`, `pytest-codspeed>=4.3.0`, `pyyaml>=5.3.1,<7.0.0`, `sqlmodel>=0.0.31`, `strawberry-graphql>=0.200.0,<1.0.0`, `ty>=0.0.25`, `typer>=0.24.1`, `a2wsgi>=1.9.0,<=2.0.0`, `pytest-xdist[psutil]>=2.5.0`, `pytest-cov>=4.0.0`, `pytest-sugar>=1.0.0`, `pytest-timeout>=2.4.0` (tests, tutorial integrations, static analysis) | Test runners remain dev-only by project policy. |
| `github-actions` | `httpx>=0.27.0,<1.0.0`, `pydantic>=2.9.0,<3.0.0`, `pydantic-settings>=2.1.0,<3.0.0`, `pygithub>=2.3.0,<3.0.0`, `pyyaml>=5.3.1,<7.0.0`, `smokeshow>=0.5.0` (workflow automation/reporting) | `pydantic` is independently a target runtime dependency; no CI feature mapping. |
| `translations` | `gitpython>=3.1.46`, `pydantic-ai>=0.4.10`, `pygithub>=2.8.1` (translation automation) | No target package mapping. |
| `dev` additions | `playwright>=1.57.0`, `prek>=0.2.22`, `zizmor>=1.23.1` (browser automation, hooks, workflow security) | Target `requirements-dev.txt` separately declares Maturin, Ruff, UV, jsonschema, and PyYAML. |

## Build command and `fastar` evidence

FastAPI uses unversioned `pdm-backend` ([pinned build-system declaration](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/pyproject.toml#L1-L3)) and declares `fastapi = "fastapi.cli:main"`;
FastAPI-RS uses `maturin==1.14.1` and has no script. The pinned FastAPI lock
selects `fastapi-cloud-cli==0.11.0` and `fastar==0.11.0`
([`uv.lock` lines 1170–1193](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/uv.lock#L1170-L1193)).
In the locked [Cloud CLI wheel](https://files.pythonhosted.org/packages/1a/07/60f79270a3320780be7e2ae8a1740cb98a692920b569ba420b97bcc6e175/fastapi_cloud_cli-0.11.0-py3-none-any.whl)
(SHA-256 `76857b0f09d918acfcb50ade34682ba3b2079ca0c43fda10215de301f185a7f8`),
`fastapi_cloud_cli/commands/deploy.py` imports `fastar` at lines 12–13 and uses
`fastar.open(..., "w:zst")` at lines 71–94. FastAPI also directly names `fastar`
in `standard`. Its concrete consumer is CLI archive creation.

## Source anchors

- [FastAPI extras, groups, and script](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/pyproject.toml#L44-L187).
- Feature sources: [multipart guard](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/dependencies/utils.py#L88-L129), [EmailStr fallback](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/openapi/models.py#L16-L55), [TestClient](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/testclient.py#L1), [templates](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/templating.py#L1), [extra Color import](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/encoders.py#L34-L49), [Color encoder registration](https://github.com/fastapi/fastapi/blob/95f8322ee1dcda7ceace7b1c4f6c9915b36d748f/fastapi/encoders.py#L84-L87).
- [Dependency atlas](dependency-atlas.md), [recursive graph](DEPENDENCY_GRAPH.md), [target manifest](../metadata.yaml), and [Starlette-RS package/extra](https://github.com/appunni-m/starlette-rs/blob/8730d0af2616cd3edc874737601726155886c660/pyproject.toml#L30-L34).
