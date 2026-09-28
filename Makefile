# Dialect: GNU Make >= 3.81. Cargo owns the Rust build graph.
PYTHON ?= $(if $(wildcard $(CURDIR)/.venv/bin/python),$(CURDIR)/.venv/bin/python,python3.12)
PYO3_PYTHON ?= $(PYTHON)
export PYO3_PYTHON
CARGO ?= cargo
MATURIN ?= $(PYTHON) -m maturin
UV ?= uv
ORACLE_PYTHON ?= $(CURDIR)/.venv-oracle/bin/python
ORACLE_STANDARD_ENV ?= $(CURDIR)/.venv-oracle-standard
ORACLE_STANDARD_PYTHON ?= $(ORACLE_STANDARD_ENV)/bin/python
FASTAPI_SOURCE ?= $(abspath ../fastapi)
STARLETTE_SOURCE ?= $(abspath ../starlette)
STARLETTE_RS_SOURCE ?= $(abspath ../starlette-rs)
SOURCE_RESULT ?=
TARGET_RESULT ?=
PARITY_INPUT ?= tests/fixtures/inputs/parity/first-asgi-request.json

.DEFAULT_GOAL := help
.PHONY: help fmt format clippy build build-rust build-python compatibility-atlas-update api-contract-update api-contract-check metadata-check parity-inputs parity-prepare-oracle parity-prepare-oracle-standard parity-api-runtime parity-validate parity-index-update parity-index-check parity-oracle parity-oracle-standard parity-compare verify clean

help: ## Show common development commands
	@printf '%s\n' \
	  'FastAPI-RS — Rust-backed FastAPI compatibility project' '' \
	  '  make fmt            Check Rust formatting and Python lint' \
	  '  make format         Apply Rust formatting' \
	  '  make clippy         Run strict workspace Clippy' \
	  '  make build          Build the Rust crates and Python wheel' \
	  '  make build-rust     Build all Rust workspace crates' \
	  '  make build-python   Build the Python wheel under target/wheels' \
	  '  make compatibility-atlas-update Rebuild the source atlas, backlog, index, and API contract' \
	  '  make api-contract-update Refresh per-symbol source/runtime API links in manifest.yaml' \
	  '  make api-contract-check Check per-symbol API links are current' \
	  '  make metadata-check   Check the human-maintained API source authority' \
	  '  make parity-inputs    Materialize ignored JSON workflows from YAML recipes' \
	  '  make parity-prepare-oracle Prepare pinned FastAPI 0.141.1 / Starlette 1.6.0 Python env' \
	  '  make parity-prepare-oracle-standard Prepare the locked optional-feature reflection profile' \
	  '  make parity-api-runtime Reflect and verify the pinned FastAPI Python API surface' \
	  '  make parity-validate Validate workflows, source atlas, and fixture mappings' \
	  '  make parity-index-update Rebuild source mappings for current fixture workflows' \
	  '  make parity-index-check  Check the materialized fixture index is current' \
	  '  make parity-oracle   Run PARITY_INPUT against the isolated FastAPI oracle' \
	  '  make parity-oracle-standard Run PARITY_INPUT with locked standard extras' \
	  '  make parity-compare  Compare live source/target result artifacts exactly' \
	  '  make verify         Run formatting, lint, static contracts, and wheel build' \
	  '  make clean          Remove Cargo outputs under target/' '' \
	  'PYTHON defaults to the pinned 3.12 development baseline; override PYTHON, CARGO, or MATURIN as needed.'

fmt: ## Check Rust formatting and Python lint
	$(CARGO) fmt --package fastapi-rs --package fastapi-rs-py -- --check
	$(PYTHON) -m ruff format --check fastapi-rs-py/python scripts tests/fixtures/workloads
	$(PYTHON) -m ruff check fastapi-rs-py/python scripts tests/fixtures/workloads

format: ## Apply Rust formatting
	$(CARGO) fmt --package fastapi-rs --package fastapi-rs-py
	$(PYTHON) -m ruff format fastapi-rs-py/python scripts tests/fixtures/workloads

clippy: ## Run strict workspace Clippy
	$(CARGO) clippy --workspace --all-targets --all-features --locked -- -D warnings

build-rust: ## Build all Rust workspace crates
	$(CARGO) build --workspace --all-features --locked

build-python: ## Build the Python wheel under target/wheels
	$(MATURIN) build --release --out target/wheels

compatibility-atlas-update: parity-inputs ## Rebuild generated source atlas, fixture backlog, index, and contract
	$(PYTHON) scripts/build_fastapi_compatibility_atlas.py --fastapi-source "$(FASTAPI_SOURCE)" --starlette-source "$(STARLETTE_SOURCE)" --starlette-rs-root "$(STARLETTE_RS_SOURCE)"
	$(PYTHON) -m scripts.build_materialized_input_index
	$(PYTHON) scripts/build_fastapi_compatibility_atlas.py --fastapi-source "$(FASTAPI_SOURCE)" --starlette-source "$(STARLETTE_SOURCE)" --starlette-rs-root "$(STARLETTE_RS_SOURCE)"
	$(PYTHON) -m scripts.build_materialized_input_index
	$(PYTHON) -m scripts.build_api_surface_contract
	$(PYTHON) -m scripts.parity.cli validate

api-contract-update: ## Refresh per-symbol source/runtime API links in the active manifest
	$(PYTHON) -m scripts.build_api_surface_contract

api-contract-check: ## Check per-symbol API links are current
	$(PYTHON) -m scripts.build_api_surface_contract --check

metadata-check: ## Check API-source metadata against generated contract artifacts
	$(PYTHON) scripts/check_metadata_authority.py

parity-prepare-oracle: ## Create the locked source oracle and select local Starlette 1.6.0
	UV_PROJECT_ENVIRONMENT="$(CURDIR)/.venv-oracle" $(UV) sync --project "$(FASTAPI_SOURCE)" --locked --no-dev --no-install-package starlette --python "$(PYTHON)"
	$(UV) pip install --python "$(ORACLE_PYTHON)" --no-deps --editable "$(STARLETTE_SOURCE)"
	$(UV) pip check --python "$(ORACLE_PYTHON)"

parity-prepare-oracle-standard: ## Prepare standard FastAPI extras and TestClient reflection profile
	UV_PROJECT_ENVIRONMENT="$(ORACLE_STANDARD_ENV)" $(UV) sync --project "$(FASTAPI_SOURCE)" --locked --no-dev --extra standard --group docs-tests --no-install-package starlette --python "$(PYTHON)"
	$(UV) pip install --python "$(ORACLE_STANDARD_PYTHON)" --no-deps --editable "$(STARLETTE_SOURCE)"
	$(UV) pip check --python "$(ORACLE_STANDARD_PYTHON)"

parity-api-runtime: parity-inputs ## Regenerate pinned-source runtime reflections for core and standard profiles
	$(ORACLE_PYTHON) scripts/inventory_fastapi_runtime.py --output tests/fixtures/runtime-api-surface-core.json
	$(ORACLE_STANDARD_PYTHON) scripts/inventory_fastapi_runtime.py --output tests/fixtures/runtime-api-surface-standard.json --optional-extras standard,docs-tests
	$(PYTHON) -m scripts.parity.cli validate

parity-inputs: ## Materialize ignored JSON workflows from input-only YAML recipes
	$(PYTHON) scripts/build_parity_inputs.py

parity-validate: parity-inputs ## Validate workflows, source atlas, fixture mappings, and pinned source references
	$(PYTHON) -m scripts.parity.cli validate

parity-index-update: parity-inputs ## Rebuild source mappings for current fixture workflows
	$(PYTHON) -m scripts.build_materialized_input_index

parity-index-check: parity-inputs ## Check the materialized fixture index is current
	$(PYTHON) -m scripts.build_materialized_input_index --check

parity-oracle: parity-inputs ## Execute the input workflow against the isolated FastAPI oracle
	$(PYTHON) -m scripts.parity.cli oracle --input "$(PARITY_INPUT)" --python "$(ORACLE_PYTHON)"

parity-oracle-standard: parity-inputs ## Execute optional-feature inputs with Starlette 1.6.0 and standard extras
	$(PYTHON) -m scripts.parity.cli oracle --input "$(PARITY_INPUT)" --python "$(ORACLE_STANDARD_PYTHON)"

parity-compare: ## Compare live source/target result artifacts exactly
	$(PYTHON) -m scripts.parity.cli compare --source-result "$(SOURCE_RESULT)" --target-result "$(TARGET_RESULT)"

build: build-rust build-python ## Build the Rust crates and Python wheel

verify: fmt clippy parity-index-check api-contract-check metadata-check parity-validate build-python ## Run formatting, lint, static contracts, and package checks

clean: ## Remove Cargo outputs under target/
	$(CARGO) clean
