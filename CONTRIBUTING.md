# Contributing

FastAPI-RS is an alpha source-informed implementation of FastAPI 0.157.0.
Keep compatibility claims tied to reviewed evidence and the pinned Starlette
1.6.0 contract. `fastapi-rs/` owns FastAPI behavior; `fastapi-rs-py/` is the
internal PyO3 binding and value-conversion crate, and Python runtime files stay
limited to native re-exports and literal `__all__` declarations. See
[`AGENTS.md`](AGENTS.md) for the full project contract.

## Development setup

Use CPython 3.12.13 for the locked development profiles, `uv`, the Rust
toolchain pinned in `rust-toolchain.toml`, and a clean Starlette-RS checkout at
the exact commit in `metadata.yaml`. Do not use a modified sibling checkout
for identity-checked work.

From the repository root, set `STARLETTE_RS_SOURCE` to that clean checkout and
prepare the needed tools or target environment. On a fresh checkout, create
and activate a local helper environment first:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --requirement requirements-dev.txt
export STARLETTE_RS_SOURCE=/absolute/path/to/clean/starlette-rs
make parity-prepare-target STARLETTE_RS_SOURCE="$STARLETTE_RS_SOURCE"
.venv-target/bin/python -c 'import fastapi'
```

The last command checks that the facade imports in the prepared target
environment; it does not establish the FastAPI behavior contract. Use a
focused, identity-checked parity workflow for behavior changes.

## Change and validation guidance

- Keep implementation and control flow in Rust. Do not add compatibility
  shims for older FastAPI versions or helpers and fallback logic to Python
  runtime modules.
- For Rust changes, run `make fmt clippy` and the static contract checks
  required by the changed surface, using the pinned Starlette-RS checkout.
- For parity recipe changes, edit input-only YAML under
  `tests/fixtures/input-recipes/`, then run
  `make parity-inputs parity-index-update parity-validate`.
- For reviewed API policy or identity changes, update `metadata.yaml` and run
  `make metadata-check`.
- Run focused checks for the changed contract. Do not run `cargo test`,
  `pytest`, or `unittest`; the project keeps zero unit tests and uses the
  isolated parity workflows for behavior evidence.
- Keep generated inventories and reports synchronized only through their
  maintained commands. Do not edit generated parity inputs by hand or include
  ignored run output in a change.
- For FastAPI-derived or other third-party material, record its exact source
  and license and preserve all required notices. The project's original code
  is MIT-licensed; third-party terms remain separate. No separate CLA or DCO
  process is currently documented.

Open an issue or pull request with a focused change description and the exact
checks and evidence run. `make help` lists maintained repository commands.
