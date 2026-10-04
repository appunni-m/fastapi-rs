# Feature and policy crosswalk audit — 2026-10-04

## Scope and evidence boundary

Read-only audit of the FastAPI 0.141.1 compatibility atlas and its input mappings, using the pinned FastAPI source commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` and Starlette 1.6.0 commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. Starlette 1.6.0 is the only generic Starlette source authority. No parity or test command was run, and this audit does not claim FastAPI-RS parity.

The evidence ladder matters here:

| Artifact field or file | What it establishes | What it does not establish |
|---|---|---|
| `aliases`, `errors`, `deprecations`, `optional_features`, `authorities` in `tests/fixtures/compatibility-atlas.json` | Source-derived identities, declarations, selectors, and policy facts | Target support or matching runtime behavior |
| A row's `observation_selectors` or a feature family's `observations` | Candidate dimensions to observe | That a recipe selects them or a process produced matching values |
| A row's nested `independent_workflow_mappings` and its recipe | A reviewed, input-only case mapping and the selectors requested for that case | Any oracle/target measurement; recipes contain no expected outputs |
| Live source and target result artifacts plus the comparator | Executed observations and their comparison for the selected profile | Coverage outside the cases, profile, and selectors that ran |

This is also the explicit contract in `tests/fixtures/manifest.yaml`: the foundation is marked `foundation-incomplete`, and it says the atlas/inventory are discovery artifacts rather than support or parity evidence (`contract` lines 3–17). Use nested workflow mappings and their `coverage_scope` for case-specific selection; do not read row-level selector unions or counts as observed coverage.

## Findings

### 1. Candidate selector unions can overstate the selectors in any mapped case

The atlas contains 42 error candidates, 69 alias records, and 21 source deprecation records. These are source inventories. For example, the `fastapi.HTTPException` error row declares `error.args`, `error.public_attributes`, and several HTTP selectors, while the `public-api-errors` feature family lists `error.class` and `error.public_attributes` but omits both `error.args` and `websocket.close_reason` (`compatibility-atlas.json` `/errors` and `/feature_families`).

The module-level rows also aggregate selectors more broadly than an individual recipe. `upstream-test:tests/test_openapi_schema_type.py` has `error.args` in its row-level `observation_selectors`, but its linked `public-model-edge-cases-upstream` mapping selects only `http.body.bytes`. That difference is visible in the nested mapping's `observation_selectors` and `coverage_scope`. A corpus search found no recipe selector named `error.args`. Likewise, the direct API reference recipe observes only the signatures of `fastapi.HTTPException` and `fastapi.WebSocketException`; it does not construct those objects and compare their `args` or public fields (`direct-api-reference-wave.yaml`).

There is a useful positive case: `public-errors-http-websocket-wave.yaml` selects HTTP status/headers/body and a pre-accept WebSocket close code, close reason, and event order. Its coverage row is partial and its nested mapping carries those selectors. This proves that the input contract has a focused error slice, not that the selected observations have run.

**Audit disposition:** keep selector inventories, per-case selectors, and executed result fields distinct in reports. If the atlas intends `error.args` as a coverage objective, add explicit input cases and a supported observation path; otherwise label it as an unexercised candidate dimension. Keep `websocket.close_reason` in the canonical feature taxonomy so it agrees with the error inventory and the existing recipe.

### 2. The atlas still has stale statements that warning capture is unsupported

The checked atlas unresolved point `case-construction-input-contract` says warnings are a separate selector “without runner support”; the lifecycle point says `on_event` warnings are not claimed. Those statements no longer match the current input contract. `python-asgi-workflow-v4.schema.json` permits `capture_warnings` on construction and ASGI actions, and `scripts/parity/worker.py` captures warning sidecars. `router-events-lifespan-upstream.yaml` uses workflow v4 and selects `capture_warnings: true` for construction, lifespan, and request actions around deprecated `on_event` registration.

This is only an input-capability correction. The v4 recipe declares warning observations, but no live output was inspected here. Other deprecations still need per-symbol inputs: `deprecations` records are static source evidence without recipe/case links, and the broad `warnings.category_message` feature selector does not mean all 21 source records are exercised. In particular, `tests/test_deprecated_responses.py` is explicitly excluded because its ORJSON/UJSON dependencies are not in the selected profiles (`scripts/build_fastapi_compatibility_atlas.py`, `TEST_EXCLUSIONS`).

**Audit disposition:** update stale unresolved-point evidence to say which warning cases are now expressible and selected, while keeping their runtime status “not established until executed.” Continue to report unlinked deprecations as pending, and distinguish warning-emitting deprecations from deprecated metadata that may not emit a runtime warning.

### 3. Optional-feature records describe declared extras, not matched optional profiles

`optional_features` is a source-derived list of the three FastAPI extras (`standard`, `standard-no-fastapi-cloud-cli`, and `all`). It does not state which package set is installed for every mapped recipe. The manifest's only oracle extension is named `standard-multipart` and lists `python-multipart` as the added package, while its preparation target is `parity-prepare-oracle-standard`; that Make target syncs the full FastAPI `standard` extra plus `docs-tests` (`Makefile` lines 137–140). The source extra includes CLI, HTTPX, Jinja, multipart, email validation, Uvicorn, settings, and extra Pydantic types (`../fastapi/pyproject.toml` lines 59–95), while the docs-tests group adds `httpx2` (lines 147–150). The manifest should make clear whether `standard-multipart` means the complete prepared environment or a minimal package delta.

Three concrete optional boundaries remain open in the atlas:

- `fastapi.testclient.TestClient` is a direct FastAPI alias of `starlette.testclient.TestClient` (`../fastapi/fastapi/testclient.py:1`), but the unresolved point says no target standard-profile lock or direct API workflow establishes its alias identity, signature, or behavior. Starlette 1.6.0's TestClient imports `httpx2` first and only falls back to `httpx` with a deprecation warning (`../starlette/starlette/testclient.py:32–50`).
- The deprecated `ORJSONResponse`/`UJSONResponse` tests are excluded because those packages are absent from the selected profiles; the declared FastAPI extras do not include either package.
- FastAPI's `fastapi` console script is declared in upstream `pyproject.toml`, but the atlas separately marks its subprocess contract unresolved; the current ASGI/API workflows do not observe process output or exit status for that CLI.

These are accurately exposed as pending/excluded cases, but `optional_features` by itself should not be presented as optional-feature coverage.

### 4. Python support declarations exceed the single runtime used for target parity

FastAPI 0.141.1 declares `requires-python = ">=3.10"` and classifiers for Python 3.10–3.14 (`../fastapi/pyproject.toml` lines 12, 35–40). Its CI covers 3.10, 3.12, 3.13, 3.14, and free-threaded 3.14t, but not 3.11 (`../fastapi/.github/workflows/test.yml` lines 53–79). The source repository's `.python-version` is 3.11; the atlas extracts this as `source_python_version_pin`, which is a repository development pin rather than the compatibility floor or the selected oracle interpreter.

FastAPI-RS declares the same `>=3.10` floor and classifiers 3.10–3.14 (`pyproject.toml` lines 10, 19–29), but the manifest, target lock, and Make target pin parity to CPython 3.12.13 (`tests/fixtures/manifest.yaml` lines 35–41, `Makefile` lines 142–149). Workflow inputs do not carry an interpreter matrix. Thus the other advertised versions are package metadata, not parity evidence. The source-only Python metadata parser records declarations and CI matrix values; it does not execute cases (`scripts/build_fastapi_compatibility_atlas.py`, `read_python_support`).

**Audit disposition:** describe current parity as CPython 3.12.13 only. Treat behavior on 3.10, 3.11, 3.13, 3.14, and free-threaded 3.14t as unverified until the corresponding isolated profiles exist and execute. Clarify the two Python pin labels so the upstream repository's 3.11 developer pin is not confused with the 3.12.13 selected oracle/target profile.

## Validation performed

Read source and generated artifacts only: atlas, manifest, target/upstream package metadata, upstream CI configuration, workflow schemas, selected recipes, workloads, validators, and Make targets. No tests, parity executions, or validation commands were run. The repository had unrelated in-progress edits at the start of this audit; no active metadata, atlas, recipe, or validator files were changed. This draft is outside active compatibility inputs.
