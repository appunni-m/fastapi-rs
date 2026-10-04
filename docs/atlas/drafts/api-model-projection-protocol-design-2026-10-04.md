# Direct API Pydantic model projection protocol

## Audit findings

The direct API lane has three paired input/result/comparison contracts:

| Input workflow | Input features | Product result | Comparison |
| --- | --- | --- | --- |
| `python-api-workflow@1` | Callable return and signature observations | `python-api-workflow-result@2` | `python-api-comparison@1` |
| `python-api-workflow@2` | Adds public attributes, call outcomes, and non-finite return sidecars | `python-api-workflow-result@3` | `python-api-comparison@2` |
| `python-api-workflow@3` | Adds ordered warning capture | `python-api-workflow-result@4` | `python-api-comparison@3` |

The input schemas are closed at each object (`additionalProperties: false`). `load_workflow` in `scripts/parity/contract.py` selects the schema by identity and rejects unknown fields before either worker runs. `api_worker.py` resolves only atlas-supported public symbols, invokes the selected callable using the named workload argument bundle, and emits indexed `{kind, values}` observations. `api_target_worker.py` uses the same observation implementation while importing the target facade. `cli.py` binds each result back to the workflow's case, probe, kind, and index. `api_comparator.py` checks source/target identity, ordering, and type-sensitive exact JSON equality; differences are retained as exact JSON values in generic comparison diffs.

The current identity path already fixes the model runtime: source results identify the pinned FastAPI 0.141.1 and Starlette 1.6.0 checkouts and exact runtime package set, including Pydantic 2.13.4 and pydantic-core 2.46.4. Target results must carry the same Pydantic packages, Python runtime, and platform, while identifying FastAPI-RS and Starlette-RS and excluding upstream FastAPI/Starlette imports. A model observation needs no new identity field if it keeps these existing checks.

## Recommended versioned addition

Add workflow v4, result v5, and comparison v4 as a paired contract. Copy the v3 schemas and change only their identities plus the new observation variant. Keep v1-v3 registrations and behaviors unchanged. The new input observation should be fixed and Pydantic-specific, for example:

```yaml
kind: python_pydantic_model_result
selector: model_dump
comparison: exact
```

Permit it only on a `public_callable` probe with an `argument_bundle`; require it to be the probe's sole observation so invocation and model projection have one unambiguous result. Keep existing v3 `capture_warnings` behavior. The schema must retain closed objects and must not expose a projection path, method name, arbitrary serializer options, callback, or Python expression.

Define the worker projection once for both products: invoke the selected callable once, require its result to be an instance of the pinned `pydantic.BaseModel`, then call `model_dump` with fixed options: `mode="json"`, `by_alias=True`, `exclude_unset=False`, `exclude_defaults=False`, `exclude_none=False`, `round_trip=False`, and `warnings="error"`. Pass the dump through the existing non-finite JSON sidecar projection used by v2/v3 returns. This retains aliases such as `$ref`, defaults, explicit nulls, and allowed extra fields while keeping the artifact JSON-only. A non-model result or dump failure is a normal `product_error` with no observations. The comparison remains exact, including the existing type-sensitive JSON comparison and exact source/target diff values; no expected values enter recipes.

The result v5 schema should add only the new indexed observation shape, with `values.value` as JSON and an optional `nonfinite_floats` sidecar of JSON-pointer paths. The comparison v4 schema can retain the v3 diff structure; its identity and `input.schema` must bind it to workflow v4. Preserve `additionalProperties: false` in all copied and added result/comparison objects.

`model_dump(mode="json")` renders set-valued fields as arrays. Exact cross-process equality is consequently appropriate only when ordering is part of the selected case or the input avoids such fields; do not silently sort arrays as a general normalization. If a selected OpenAPI model case exercises set-valued fields, document and version a deterministic set projection before claiming exact parity for that case.

## Coordinated files

1. Add `tests/fixtures/schemas/python-api-workflow-v4.schema.json`, `tests/fixtures/schemas/python-api-workflow-result-v5.schema.json`, and `tests/fixtures/schemas/python-api-comparison-v4.schema.json`.
2. In `scripts/parity/contract.py`, register the three paths and IDs, extend the workflow/result/comparison maps, and verify a `python_api_workflow_v4` manifest block and all schema digests. Do not replace or broaden v1-v3 mappings.
3. In `scripts/parity/api_worker.py`, register workflow v4 and result v5, add the one fixed Pydantic projection branch, and retain non-finite projection for v4. `scripts/parity/api_target_worker.py` already delegates to this runner; extend its accepted workflow/non-finite version set.
4. In `scripts/parity/api_comparator.py`, register the v4 warning-capable version alongside v3. Its observation loop and identity checker already handle indexed exact JSON observations. `scripts/parity/cli.py` result schema/binding/comparison selection is map-driven; keep its generic binding checks and add a narrow model-kind/probe guard only if schema validation does not enforce the intended sole-observation rule.
5. Add `python_pydantic_model_result` to `API_OBSERVATION_SELECTORS` and `_selected_selectors` in `scripts/parity/materialized.py`. Add a dedicated `python.pydantic_model_result` exact selector to `tests/fixtures/observation-selectors.json`; it must be marked supported only when both workers implement the same projection.
6. Add an input-only YAML recipe under `tests/fixtures/input-recipes/parity/` and its deterministic argument-bundle workload under `tests/fixtures/workloads/`. Use `upstream_api_definition` evidence for each constructor symbol and no stored expected outputs. Add the v4 workflow entry and refreshed digest references to `tests/fixtures/manifest.yaml`.
7. Review/classify the selected `fastapi.openapi.models` symbols in `metadata.yaml` and the generated API/atlas artifacts before treating them as supported. The inventory alone is discovery, not support evidence. Regenerate `tests/fixtures/inputs/parity/*.json`, `tests/fixtures/materialized-input-index.json`, `tests/fixtures/compatibility-atlas.json`, `tests/fixtures/fixture-backlog.json`, and the generated API surface contract through their existing build commands rather than hand-editing generated artifacts.

## Command sequence after implementation

After recipe/schema/selector and reviewed source-classification changes, run:

```sh
make parity-inputs parity-index-update
make api-contract-update
make compatibility-atlas-update
make metadata-check api-contract-check parity-index-check
make parity-validate
```

Then exercise the materialized v4 input in isolated identity-checked processes, preserving the emitted result artifact paths for comparison:

```sh
PARITY_API_INPUT=tests/fixtures/inputs/parity/<model-recipe>.json make parity-api-validate
PARITY_API_INPUT=tests/fixtures/inputs/parity/<model-recipe>.json make parity-api-oracle
PARITY_API_INPUT=tests/fixtures/inputs/parity/<model-recipe>.json make parity-api-target
PARITY_API_INPUT=tests/fixtures/inputs/parity/<model-recipe>.json SOURCE_RESULT=<oracle-result> TARGET_RESULT=<target-result> make parity-api-compare
```

This audit only inspected the protocol and wrote this draft. It did not edit active schemas, workers, recipes, metadata, or generated artifacts, and it did not run tests or parity commands.
