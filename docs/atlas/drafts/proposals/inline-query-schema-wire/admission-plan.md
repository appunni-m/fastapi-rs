# Inline query schema wire: prospective admission plan

2026-10-05. TMP-only review of the unchanged, independently reviewed two-case
proposal. No active edits, materialization, app/native import, source/target
execution, build or unit framework. This plan adds input provenance; it is not
compatibility or coverage evidence. Activation waits for the parent’s closed
measurement checkpoint.

## Frozen inputs and current authority

| File | SHA256 |
| --- | --- |
| `inline_query_schema_wire.py` | `016c09632284d0c845f5c13554ccad9865884560cbf26ddc7a7bc384476159ef` |
| `inline-query-schema-wire.yaml` | `316011379f94c5084c210aa7dc1d8e28af2a620df35f8b13a028c7552e7811bc` |
| `review-plan.md` | `446052fd97849438c3b3bc72676b0dc3f29b66d4fbfdc1134501fc1d5dd0797a` |
| `independent-review.md` | `a6ad8f41097d30dee099be6ca3ecabfb79d520fb9910916cf28fd4d9f01f858d` |
| current `metadata.yaml` | `89e0abe3c85d041d3dde66fdd6c56da6c698fc90f3f5f2031121ad8b6edaef65` |

Current authority schema is `fastapi-rs/api-source-authority@1`; reviewed
operation rows live at `reviewed_api_contract_overlay.operations` under
`fastapi-rs/reviewed-api-contract-overlay@7`. All eight proposed IDs already have
rows. Append refs only: preserve every existing field, binding, source evidence,
identity ref, scope, classification, target status and coverage_status. No new
operation row, signature, supported_slice or known-gap edit is needed. Root
FastAPI’s null binding/full-contract-not-established state remains unchanged.

Active copies, byte-identical to the frozen originals:

- `tests/fixtures/workloads/inline_query_schema_wire.py`
- `tests/fixtures/input-recipes/parity/inline-query-schema-wire.yaml`

Both paths and the future ignored materialized input are currently absent.
Canonical future JSON input SHA from independent static review is
`3526e6b55176663e566ae1495c8b5e3ce9779a98cbfe9aaec10750b2e4dbd9b1`;
verify it again after actual generation rather than treating this prediction as
an admission receipt.

## Exact 14 fixture links

D = `fastapi.openapi-inline-query-schema-wire.direct-defaults`.
P = `fastapi.openapi-inline-query-schema-wire.dependency-defaults`.

| Existing operation ID | Cases | Added links | Actual public use / pinned evidence |
| --- | --- | ---: | --- |
| `fastapi.FastAPI` | D, P | 2 | Root constructor import; `fastapi/__init__.py:7`. |
| `fastapi.applications.FastAPI` | D, P | 2 | Same canonical class invocation, `applications.py:42,58–1018`; no new alias-identity assertion. |
| `fastapi.applications.FastAPI.__call__` | D, P | 2 | Wrapper awaits app on all requests, `applications.py:1160–1164`. |
| `fastapi.applications.FastAPI.get` | D, P | 2 | Saved public decorator registers `/observe`, `applications.py:1646`. |
| `fastapi.applications.FastAPI.openapi` | D, P | 2 | Endpoint calls it; built-in docs also call it, `applications.py:1070–1120`. |
| `fastapi.responses.JSONResponse` | D, P | 2 | Actual returned response construction; public sibling reexport `responses.py:8`. |
| `fastapi.Depends` | P only | 1 | Retained marker around async dependency, root binding `__init__.py:14`. |
| `fastapi.param_functions.Depends` | P only | 1 | Same factory binding `param_functions.py:2283`; no separate reflection probe. |
| Total | Six shared IDs plus two dependency-only IDs | 14 | |

Each new ref has exactly this shape, with the relevant full case ID:

```yaml
recipe_path: tests/fixtures/input-recipes/parity/inline-query-schema-wire.yaml
case_id: fastapi.openapi-inline-query-schema-wire.direct-defaults
workload_path: tests/fixtures/workloads/inline_query_schema_wire.py
```

Direct-operation resolution in `scripts/parity/api_contract.py:978–1078` derives
selected-case selectors and hash-bound input/recipe/workload references. Do not
handwrite reduced observation_selectors. Validate unique (operation, recipe,
case) triples and exactly 14 additions; removing those refs must recover the
entire current parsed metadata. No direct-case Depends link, inferred Query
factory link, duplicate __init__, Request, APIRouter, get_openapi, private
ModelField/adapter or handler link is justified. Case provenance does not make
every observation individual evidence for every linked operation.

## Counts, generation and static gate

Existing index: 555 workflows / 2304 cases; generated manifest: 1369 operation
refs / 154 symbols with refs. Predicted changes: +1 workflow / +2 cases / +14
refs / +0 symbols, hence **556 / 2306 / 1383 / 154**. Required public candidate
and classification counts remain unchanged. Predictions need post-generation
readback; no coverage_status promotion follows from static admission.

New workflow: two parity constructors, eight GET actions, 28 action observations
plus two construction observations, ten full warning-capture phases, no faults.
Four docs requests select full raw status/ordered headers/body and whole
structural documents; four endpoint requests select full raw responses. Every
action also selects ordered send types and exact application error. The public
journal preserves prior full send dictionaries, exact bytes and container
shapes. The final response cannot recursively contain its own send/exit; those
remain directly observed. No expected outputs or normalization.

Regeneration owns ignored `tests/fixtures/inputs/parity/inline-query-schema-wire.json`
and tracked `tests/fixtures/materialized-input-index.json`,
`tests/fixtures/compatibility-atlas.json`, `tests/fixtures/fixture-backlog.json`,
`tests/fixtures/manifest.yaml`, and `docs/COMPATIBILITY_ATLAS.md` as affected.
Inspect all generated diffs; selector catalog, source inventory/classification,
identity records and comparators should require no semantic changes.

After parent activation, run sequentially from the repo (commands are a plan,
not executed in this review):

```sh
export STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65
export RUSTC_WRAPPER=
.venv/bin/python -m ruff check --no-cache tests/fixtures/workloads/inline_query_schema_wire.py
.venv/bin/python -m ruff format --check tests/fixtures/workloads/inline_query_schema_wire.py
make parity-inputs
make parity-index-update
make compatibility-atlas-update
make api-contract-update
make metadata-check
make parity-validate PARITY_INPUT=tests/fixtures/inputs/parity/inline-query-schema-wire.json
make parity-index-check api-contract-check python-facade-check rust-policy-check
make fmt
 git diff --check
```

Also recheck the recipe with canonical `scripts.parity.contract.read_recipe`,
schema9, factory AST contract, source-evidence paths and no YAML merge keys;
existing frozen checks pass but are not new active admission receipts. These
commands do not install/run apps or compile extensions. Any global Clippy/build
or live gate remains parent-owned, separate from input admission.

## Source boundary and PRE requirements

Pinned source hashes in the original review plan were read back unchanged.
`dependencies/utils.py:491–538,550–565` carries primitive ordinary defaults into
inferred Query fields; `169–198` includes direct/dependency-owned parameters.
`_compat/v2.py:141–167,285–336` retains field/default metadata and batches core
schemas; `254–282` applies the inline title after mapped schema lookup.
`openapi/utils.py:160–231,548–583,679` assembles mapped parameter schemas and
finishes actual OpenAPI model/encoding. `openapi/models.py:425–427` declares
PathItem|Any; there is no universal final field-order assumption. Existing
query-params, dependencies/index and custom-response docs remain recipe source
evidence. Generic JSONResponse behavior is sibling-owned.

After frozen admission, require a source-first PRE with two successful
constructors and all eight actions completed. Preserve actual unchanged-target
results, ordered input/action/observation bindings, full warning journals,
raw bytes/sends, identities and pre/post snapshots. A constructor/request error
is an ordinary outcome, with actual unrun steps retained. Do not substitute the
historical legacy 11 structural-order gaps for these new live results.

Positive scope is primitive int/string defaults, nullable None controls, one
async dependency and stable public document identity/reuse. Nonserializable or
custom defaults, alias/title/Annotated metadata, body/header/cookie/path fields,
refs/input-model hook batches, namespace/adapter mutation, route changes,
concurrency, cancellation and broader caches remain separate gates. No runtime
patch or complete OpenAPI/await/dependency claim is part of admission.
