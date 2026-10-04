# Dialect: GNU Make >= 3.81. Cargo owns the Rust build graph.
PYTHON ?= $(if $(wildcard $(CURDIR)/.venv/bin/python),$(CURDIR)/.venv/bin/python,python3.12)
PYO3_PYTHON ?= $(PYTHON)
export PYO3_PYTHON
CARGO ?= cargo
MATURIN ?= $(BUILD_TOOLS_PYTHON) -m maturin
UV ?= uv
ORACLE_PYTHON ?= $(CURDIR)/.venv-oracle/bin/python
ORACLE_STANDARD_ENV ?= $(CURDIR)/.venv-oracle-standard
ORACLE_STANDARD_PYTHON ?= $(ORACLE_STANDARD_ENV)/bin/python
TARGET_ENV ?= $(CURDIR)/.venv-target
TARGET_PYTHON ?= $(TARGET_ENV)/bin/python
TARGET_RUNTIME_LOCK ?= $(CURDIR)/requirements/target-runtime-cpython-3.12.13.lock
BUILD_TOOLS_ENV ?= $(CURDIR)/.venv-build-tools
BUILD_TOOLS_PYTHON ?= $(BUILD_TOOLS_ENV)/bin/python
BUILD_TOOLS_LOCK ?= $(CURDIR)/requirements/build-tools-cpython-3.12.13.lock
FASTAPI_SOURCE ?= $(abspath ../fastapi)
STARLETTE_SOURCE ?= $(abspath ../starlette)
STARLETTE_RS_SOURCE ?= $(abspath ../starlette-rs)
export STARLETTE_RS_SOURCE
SOURCE_RESULT ?=
TARGET_RESULT ?=
PARITY_INPUT ?= tests/fixtures/inputs/parity/first-asgi-request.json
PARITY_API_INPUT ?= tests/fixtures/inputs/parity/encoding.json
BENCHMARK_WORKLOAD ?= benchmarks/workloads/first-slice-valid-asgi.yaml

.DEFAULT_GOAL := help
.PHONY: help fmt format clippy build build-rust build-python build-tools-prepare python-facade-check rust-policy-check compatibility-atlas-update api-contract-update api-contract-check metadata-check dependency-inventory-update dependency-inventory-check dependency-graph-update dependency-graph-check parity-inputs parity-prepare-oracle parity-prepare-oracle-standard parity-prepare-target parity-api-runtime parity-validate parity-index-update parity-index-check parity-oracle parity-oracle-standard parity-target parity-compare parity-api-validate parity-api-oracle parity-api-target parity-api-compare parity-first-slice benchmark-input-check benchmark-contract-check benchmark-first-slice benchmark-suite verify clean

help: ## Show common development commands
	@printf '%s\n' \
	  'FastAPI-RS — Rust-backed FastAPI compatibility project' '' \
	  '  make fmt            Check Rust formatting and Python lint' \
	  '  make python-facade-check Enforce import/re-export-only Python runtime modules' \
	  '  make rust-policy-check Enforce no-unsafe, no-unit-test, and lint-suppression policy' \
	  '  make format         Apply Rust formatting' \
	  '  make clippy         Run strict workspace Clippy' \
	  '  make build          Build the Rust crates and Python wheel' \
	  '  make build-rust     Build all Rust workspace crates' \
	  '  make build-python   Build the Python wheel under target/wheels' \
	  '  make build-tools-prepare Prepare hash-locked CPython 3.12.13 Maturin environment' \
	  '  make compatibility-atlas-update Rebuild the source atlas, backlog, index, and API contract' \
	  '  make api-contract-update Refresh per-symbol source/runtime API links in manifest.yaml' \
	  '  make api-contract-check Check per-symbol API links are current' \
	  '  make metadata-check   Check the human-maintained API source authority' \
	  '  make dependency-inventory-update Regenerate the pinned target dependency/license report' \
	  '  make dependency-inventory-check Check the pinned target dependency/license report' \
	  '  make dependency-graph-update Regenerate FastAPI lock-derived dependency edges and surfaces' \
	  '  make dependency-graph-check Check Python dependency rows against FastAPI 0.141.1 uv.lock' \
	  '  make parity-inputs    Materialize ignored JSON workflows from YAML recipes' \
	  '  make parity-prepare-oracle Prepare pinned FastAPI 0.141.1 / Starlette 1.6.0 Python env' \
	  '  make parity-prepare-oracle-standard Prepare the locked optional-feature reflection profile' \
	  '  make parity-prepare-target Prepare .venv-target with pinned shared deps and release FastAPI-RS / ../starlette-rs' \
	  '  make parity-api-runtime Reflect and verify the pinned FastAPI Python API surface' \
	  '  make parity-validate Validate workflows, source atlas, and fixture mappings' \
	  '  make parity-index-update Rebuild source mappings for current fixture workflows' \
	  '  make parity-index-check  Check the materialized fixture index is current' \
	  '  make parity-oracle   Run PARITY_INPUT against the isolated FastAPI oracle' \
	  '  make parity-oracle-standard Run PARITY_INPUT with locked standard extras' \
	  '  make parity-target   Run PARITY_INPUT against the isolated FastAPI-RS target' \
	  '  make parity-compare  Compare live source/target result artifacts exactly' \
	  '  make parity-api-*    Validate, run, and compare direct Python API probes' \
	  '  make parity-first-slice Run and compare the pinned first HTTP slice end to end' \
	  '  make benchmark-input-check Validate workload declarations and their parity inputs' \
	  '  make benchmark-contract-check Validate benchmark workloads against parity inputs and runner policy' \
	  '  make benchmark-first-slice Gate and measure the selected direct-ASGI workload' \
	  '  make benchmark-suite  Gate and measure all six reviewed direct-ASGI workloads' \
	  '  make verify         Run formatting, lint, static contracts, and wheel build' \
	  '  make clean          Remove Cargo outputs under target/' '' \
	  'Builds use the separate hash-locked CPython 3.12.13 Maturin environment; override BUILD_TOOLS_ENV, CARGO, or MATURIN as needed.'

fmt: rust-policy-check ## Check Rust formatting and Python lint
	$(CARGO) fmt --package fastapi-rs --package fastapi-rs-py -- --check
	$(PYTHON) -m ruff format --check fastapi-rs-py/python scripts tests/fixtures/workloads
	$(PYTHON) -m ruff check fastapi-rs-py/python scripts tests/fixtures/workloads
	$(MAKE) python-facade-check

python-facade-check: ## Require imports/re-exports only in the Python runtime package
	$(PYTHON) scripts/check_target_runtime_boundary.py --source-only

rust-policy-check: ## Enforce no-unsafe, no-unit-test, and lint-suppression policy
	$(PYTHON) scripts/check_rust_policy.py

format: ## Apply Rust formatting
	$(CARGO) fmt --package fastapi-rs --package fastapi-rs-py
	$(PYTHON) -m ruff format fastapi-rs-py/python scripts tests/fixtures/workloads

clippy: rust-policy-check ## Run strict workspace Clippy
	$(PYTHON) scripts/build_target_extension.py --clippy --cargo "$(CARGO)" --starlette-rs-source "$(STARLETTE_RS_SOURCE)"

build-rust: ## Build all Rust workspace crates
	$(CARGO) build --workspace --all-features --locked

build-tools-prepare: ## Prepare isolated hash-locked CPython 3.12.13 build tools
	test -x "$(BUILD_TOOLS_PYTHON)" || $(UV) venv --python 3.12.13 "$(BUILD_TOOLS_ENV)"
	$(BUILD_TOOLS_PYTHON) -c 'import platform, sys; (platform.python_implementation() == "CPython" and sys.version_info[:3] == (3, 12, 13)) or sys.exit("build-tool lock requires CPython 3.12.13")'
	$(UV) pip sync --python "$(BUILD_TOOLS_PYTHON)" --require-hashes "$(BUILD_TOOLS_LOCK)"
	$(BUILD_TOOLS_PYTHON) -m maturin --version

build-python: build-tools-prepare ## Build the Python wheel under target/wheels
	PYO3_PYTHON="$(BUILD_TOOLS_PYTHON)" $(MATURIN) build --release --out target/wheels

compatibility-atlas-update: parity-inputs ## Rebuild generated source atlas, fixture backlog, index, and contract
	$(PYTHON) scripts/build_fastapi_compatibility_atlas.py --fastapi-source "$(FASTAPI_SOURCE)" --starlette-source "$(STARLETTE_SOURCE)" --starlette-rs-root "$(STARLETTE_RS_SOURCE)"
	$(PYTHON) -m scripts.build_materialized_input_index
	$(PYTHON) scripts/build_fastapi_compatibility_atlas.py --fastapi-source "$(FASTAPI_SOURCE)" --starlette-source "$(STARLETTE_SOURCE)" --starlette-rs-root "$(STARLETTE_RS_SOURCE)"
	$(PYTHON) -m scripts.build_materialized_input_index
	$(PYTHON) -m scripts.build_api_surface_contract
	$(PYTHON) scripts/build_fastapi_compatibility_atlas.py --fastapi-source "$(FASTAPI_SOURCE)" --starlette-source "$(STARLETTE_SOURCE)" --starlette-rs-root "$(STARLETTE_RS_SOURCE)"
	$(PYTHON) -m scripts.parity.cli validate

api-contract-update: ## Refresh per-symbol source/runtime API links in the active manifest
	$(PYTHON) -m scripts.build_api_surface_contract

api-contract-check: ## Check per-symbol API links are current
	$(PYTHON) -m scripts.build_api_surface_contract --check

metadata-check: ## Check API-source metadata against generated contract artifacts
	$(PYTHON) scripts/check_metadata_authority.py --starlette-rs-source "$(STARLETTE_RS_SOURCE)"

dependency-inventory-update: ## Regenerate the pinned Cargo/Python target dependency inventory
	$(PYTHON) scripts/render_rust_target_dependency_inventory.py --offline --starlette-rs-source "$(STARLETTE_RS_SOURCE)"

dependency-inventory-check: ## Check the pinned Cargo/Python target dependency inventory
	$(PYTHON) scripts/render_rust_target_dependency_inventory.py --offline --check --starlette-rs-source "$(STARLETTE_RS_SOURCE)"

dependency-graph-check: ## Check Python dependency graph rows against the pinned FastAPI lock
	$(PYTHON) scripts/check_fastapi_dependency_graph.py

dependency-graph-update: ## Regenerate lock-derived FastAPI Python dependency edges and surfaces
	$(PYTHON) scripts/check_fastapi_dependency_graph.py --update

parity-prepare-oracle: ## Create the locked source oracle and select local Starlette 1.6.0
	UV_PROJECT_ENVIRONMENT="$(CURDIR)/.venv-oracle" $(UV) sync --project "$(FASTAPI_SOURCE)" --locked --no-dev --no-install-package starlette --python "$(PYTHON)"
	$(UV) pip install --python "$(ORACLE_PYTHON)" --no-deps --editable "$(STARLETTE_SOURCE)"
	$(UV) pip check --python "$(ORACLE_PYTHON)"

parity-prepare-oracle-standard: ## Prepare standard FastAPI extras and TestClient reflection profile
	UV_PROJECT_ENVIRONMENT="$(ORACLE_STANDARD_ENV)" $(UV) sync --project "$(FASTAPI_SOURCE)" --locked --no-dev --extra standard --group docs-tests --no-install-package starlette --python "$(PYTHON)"
	$(UV) pip install --python "$(ORACLE_STANDARD_PYTHON)" --no-deps --editable "$(STARLETTE_SOURCE)"
	$(UV) pip check --python "$(ORACLE_STANDARD_PYTHON)"

parity-prepare-target: ## Prepare hash-locked CPython 3.12.13 target and sibling Starlette-RS
	test -x "$(TARGET_PYTHON)" || $(UV) venv --python 3.12.13 "$(TARGET_ENV)"
	$(TARGET_PYTHON) -c 'import platform, sys; (platform.python_implementation() == "CPython" and sys.version_info[:3] == (3, 12, 13)) or sys.exit("target runtime lock requires CPython 3.12.13")'
	$(UV) pip sync --python "$(TARGET_PYTHON)" --require-hashes "$(TARGET_RUNTIME_LOCK)"
	PYO3_PYTHON="$(TARGET_PYTHON)" $(UV) pip install --python "$(TARGET_PYTHON)" --no-deps --editable "$(STARLETTE_RS_SOURCE)"
	$(PYTHON) scripts/build_target_extension.py --python "$(TARGET_PYTHON)" --uv "$(UV)" --starlette-rs-source "$(STARLETTE_RS_SOURCE)"
	$(UV) pip check --python "$(TARGET_PYTHON)"
	$(TARGET_PYTHON) scripts/check_target_runtime_boundary.py

parity-api-runtime: parity-inputs ## Regenerate pinned-source runtime reflections for core and standard profiles
	$(ORACLE_PYTHON) scripts/inventory_fastapi_runtime.py --output tests/fixtures/runtime-api-surface-core.json
	$(ORACLE_STANDARD_PYTHON) scripts/inventory_fastapi_runtime.py --output tests/fixtures/runtime-api-surface-standard.json --optional-extras standard,docs-tests
	$(PYTHON) -m scripts.parity.cli validate

parity-inputs: ## Materialize ignored JSON workflows from input-only YAML recipes
	$(PYTHON) scripts/build_parity_inputs.py

parity-validate: parity-inputs ## Validate workflows, source atlas, fixture mappings, and pinned source references
	$(PYTHON) -m scripts.parity.cli validate --input "$(PARITY_INPUT)"

parity-index-update: parity-inputs ## Rebuild source mappings for current fixture workflows
	$(PYTHON) -m scripts.build_materialized_input_index

parity-index-check: parity-inputs ## Check the materialized fixture index is current
	$(PYTHON) -m scripts.build_materialized_input_index --check

parity-oracle: parity-inputs ## Execute the input workflow against the isolated FastAPI oracle
	$(PYTHON) -m scripts.parity.cli oracle --input "$(PARITY_INPUT)" --python "$(ORACLE_PYTHON)"

parity-oracle-standard: parity-inputs ## Execute optional-feature inputs with Starlette 1.6.0 and standard extras
	$(PYTHON) -m scripts.parity.cli oracle --input "$(PARITY_INPUT)" --python "$(ORACLE_STANDARD_PYTHON)"

parity-target: parity-inputs ## Execute PARITY_INPUT against the isolated FastAPI-RS target
	$(TARGET_PYTHON) scripts/check_target_runtime_boundary.py
	$(PYTHON) -m scripts.parity.cli target --input "$(PARITY_INPUT)" --python "$(TARGET_PYTHON)" --starlette-rs-source "$(STARLETTE_RS_SOURCE)"

parity-compare: ## Compare live source/target result artifacts exactly
	$(PYTHON) -m scripts.parity.cli compare --input "$(PARITY_INPUT)" --source-result "$(SOURCE_RESULT)" --target-result "$(TARGET_RESULT)"

parity-api-validate: parity-inputs ## Validate a direct public Python API workflow
	$(PYTHON) -m scripts.parity.cli api-validate --input "$(PARITY_API_INPUT)"

parity-api-oracle: parity-inputs ## Execute a direct public API workflow against FastAPI 0.141.1
	$(PYTHON) -m scripts.parity.cli api-oracle --input "$(PARITY_API_INPUT)"

parity-api-target: parity-inputs ## Execute a direct public API workflow against FastAPI-RS
	$(TARGET_PYTHON) scripts/check_target_runtime_boundary.py
	$(PYTHON) -m scripts.parity.cli api-target \
	  --input "$(PARITY_API_INPUT)" \
	  --python "$(TARGET_PYTHON)" \
	  --fastapi-source "$(FASTAPI_SOURCE)" \
	  --starlette-source "$(STARLETTE_SOURCE)" \
	  --target-source "$(CURDIR)" \
	  --starlette-rs-source "$(STARLETTE_RS_SOURCE)"

parity-api-compare: ## Compare direct public API source and target result artifacts exactly
	$(PYTHON) -m scripts.parity.cli api-compare --input "$(PARITY_API_INPUT)" --source-result "$(SOURCE_RESULT)" --target-result "$(TARGET_RESULT)"

parity-first-slice: parity-validate ## Run and exactly compare the pinned first HTTP slice
	$(PYTHON) scripts/parity/run_first_slice.py \
	  --input "$(PARITY_INPUT)" \
	  --fastapi-source "$(FASTAPI_SOURCE)" \
	  --starlette-source "$(STARLETTE_SOURCE)" \
	  --starlette-rs-source "$(STARLETTE_RS_SOURCE)" \
	  --oracle-python "$(ORACLE_PYTHON)" \
	  --target-python "$(TARGET_PYTHON)"

benchmark-input-check: parity-inputs ## Validate benchmark workload declarations and parity-input references
	$(PYTHON) -m scripts.benchmarks.contract --check

benchmark-contract-check: parity-inputs ## Validate workload declarations and current saved suite/parity references
	$(PYTHON) -m scripts.benchmarks.contract --check
	$(PYTHON) -m scripts.benchmarks.run_suite --check

benchmark-first-slice: benchmark-input-check parity-prepare-oracle parity-prepare-target ## Prepare isolated runtimes, gate parity, and measure the selected direct-ASGI workload
	$(PYTHON) scripts/benchmarks/run_first_slice.py \
	  --workload "$(BENCHMARK_WORKLOAD)" \
	  --fastapi-source "$(FASTAPI_SOURCE)" \
	  --starlette-source "$(STARLETTE_SOURCE)" \
	  --starlette-rs-source "$(STARLETTE_RS_SOURCE)" \
	  --oracle-python "$(ORACLE_PYTHON)" \
	  --target-python "$(TARGET_PYTHON)"

benchmark-suite: benchmark-input-check parity-prepare-oracle ## Prepare the oracle, then gate and measure the complete reviewed benchmark set
	$(PYTHON) -m scripts.benchmarks.run_suite \
	  --preflight-only \
	  --fastapi-source "$(FASTAPI_SOURCE)" \
	  --starlette-source "$(STARLETTE_SOURCE)" \
	  --starlette-rs-source "$(STARLETTE_RS_SOURCE)"
	$(MAKE) parity-prepare-target STARLETTE_RS_SOURCE="$(STARLETTE_RS_SOURCE)"
	$(PYTHON) -m scripts.benchmarks.run_suite \
	  --fastapi-source "$(FASTAPI_SOURCE)" \
	  --starlette-source "$(STARLETTE_SOURCE)" \
	  --starlette-rs-source "$(STARLETTE_RS_SOURCE)" \
	  --oracle-python "$(ORACLE_PYTHON)" \
	  --target-python "$(TARGET_PYTHON)"

build: build-rust build-python ## Build the Rust crates and Python wheel

verify: fmt clippy parity-index-check api-contract-check metadata-check dependency-inventory-check dependency-graph-check benchmark-contract-check parity-validate build-python ## Run formatting, lint, static contracts, and package checks

clean: ## Remove Cargo outputs under target/
	$(CARGO) clean
