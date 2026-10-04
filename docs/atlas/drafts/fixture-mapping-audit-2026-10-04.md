# FastAPI 0.141.1 fixture-mapping audit — 2026-10-04

> Read-only compatibility-atlas audit. Snapshot base: FastAPI-RS `c496ca40733c252e427e5e53f848b23ddc5a424a`, pinned FastAPI source `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` (0.141.1), and sole Starlette oracle 1.6.0 at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. Concurrent uncommitted candidate-classification and operation-overlay edits were present in the shared worktree; the coverage-matrix denominator and mapping counts reported here were unchanged. I made no active artifact edits. No tests or live parity were run.

## Finding

The active artifacts satisfy **module/page-level traceability**: every inventoried upstream test module and user-facing documentation page has either an indexed input workflow with selectors or a nonempty exclusion reason. This is not complete behavior coverage. Every materialized source mapping is explicitly partial, and the atlas makes no full-module, full-page, or parity claim.

The current counts differ from the 2026-10-03 draft snapshot. Use the counts in this report for this workspace revision.

## Source denominator and disposition

I enumerated the pinned source tree and compared it with `tests/fixtures/compatibility-atlas.json`. All 1,108 coverage rows point to existing source files with matching SHA-256 digests; inventory differences are zero.

| Source inventory | Denominator | Reviewed input links with selectors | Explicit exclusions with reasons | Other/pending |
| --- | ---: | ---: | ---: | ---: |
| `tests/test_*.py` modules | 492 | 453 (`reviewed_partial`; 410 `partially_mapped` + 43 `candidate`) | 39 | 0 |
| User-facing `docs/en/docs/**/*.md` pages | 155 | 104 (`reviewed_partial`; `mapping_status: candidate`) | 51 | 0 |
| `docs_src/**/*.py` example sources | 370 | 333 (`reviewed_partial`, direct workflow links) | 37 | 0 |
| `docs_src/**/*.py` support files, chiefly `__init__.py` | 91 | 0 | 91 | 0 |
| **All compatibility-atlas rows above** | **1,108** | **890** | **218** | **0** |

For the specific requested denominator—test modules plus documented feature pages—the result is 647 rows: 557 have reviewed partial fixture mappings and 90 have explicit exclusions. No source row is pending. The extra 461 Python source files under `docs_src/` are split into 370 examples and 91 support files; they are not additional documentation pages.

All 39 test exclusions have `review_status: excluded`, a nonempty `exclusion_reason`, and no `fixture_id`. Examples include benchmark modules routed to a correctness-gated benchmark workload, comment-only unsupported parameter variants, optional ORJSON/UJSON profiles, subprocess-based `tests/test_fastapi_cli.py`, and tests that exercise plain Python, Pydantic Settings, or third-party behavior rather than FastAPI. All 51 excluded pages likewise have reasons; examples include navigation/setup pages and pages whose runtime behavior is owned by Starlette 1.6.0 or third parties. All 37 excluded `docs_src` examples and all 91 support files have reasons.

The validator checks that exclusion reasons are present, but does not mechanically verify that the reason is correct or tied to line-specific source evidence. That part remains reviewed policy.

## Materialized workflow index

`tests/fixtures/materialized-input-index.json` currently records **523 workflows, 2,059 cases, and 1,483 source-to-workflow mappings**. Its manifest entry records the same counts and calls the artifact “Partial, independently authored workflow mappings.” The mappings partition as follows:

| Source kind | Linked source rows | Source-to-workflow mapping rows | Case references across those mappings* |
| --- | ---: | ---: | ---: |
| Upstream test modules | 453 | 901 | 1,950 |
| Documentation pages | 104 | 228 | 458 |
| Documentation Python examples | 333 | 354 | 457 |
| **Total** | **890** | **1,483** | **2,865** |

*Case references repeat when a case supports more than one source row; 2,865 is not a count of unique workflow cases. The index contains 2,059 unique case IDs across its workflows.

Each mapped row has a `fixture_id`, `workflow_id`, nonempty case IDs, and observation selectors. The source-to-workflow links are exact references to recipe paths and cases; the index builder also filters out selectors not marked `supported` or `partial` in the selector catalog. The active YAML recipes are input-only workflows with a workload factory, stimuli/actions, observations, and source evidence. They contain no expected results.

Representative links:

- Test module `tests/test_tutorial/test_path_params/test_tutorial001.py` maps to `path-operation-parameter-tutorials-test_path_params_test_tutorial001_test_get_items.yaml` / case `fastapi.path-operation-parameter-tutorials.test-path-params-test-tutorial001-test-get-items` with `http.body.bytes` and `http.status`. A second link maps the OpenAPI case with `docs.response.status`, `http.status`, `openapi.document`, and `openapi.paths`.
- Documentation page `docs/en/docs/tutorial/path-params.md` maps to `request-validation-parameters.yaml` (cases `fastapi.request-parameters.path.invalid-integer` and `.valid-integer`, selectors `http.body.bytes`, `http.status`) and `routing-surface.yaml` (four path/routing cases, including `openapi.paths`).
- Example `docs_src/path_params/tutorial001_py310.py` maps to `path-params-tutorial001-upstream.yaml` (cases `fastapi.path-params.tutorial001-openapi` and `.tutorial001-untyped-item-id`, selectors `http.body.bytes`, `http.status`, and `openapi.paths`). The YAML observation declarations use recipe-level selector names such as `status`/`body`; the materialized index records the normalized observation-selector IDs.
- `docs/en/docs/reference/staticfiles.md` is explicitly excluded because it identifies FastAPI’s Starlette `StaticFiles` re-export; the reason keeps import identity in the API manifest and assigns generic behavior to the separate Starlette-RS contract.

`tests/fixtures/fixture-backlog.json` has 890 source-linked fixture designs and 2,118 per-function test designs. Those design records are not an executable-coverage total. The 2,118 design statuses are 371 `reviewed_source_candidate`, 511 `candidate`, and 1,236 `contract_gated_source_candidate`. The materialized index identifies modules/pages, workflow/case IDs, and selectors; it does not carry upstream test-function names on each case mapping. Therefore the source-function designs cannot be treated as proof that each upstream test function has its own live input case.

## Partial versus complete mapping

The distinction is explicit in active code and schemas:

- `tests/fixtures/schemas/materialized-input-index.schema.json` fixes each mapping’s `coverage_status` to `partial` and says a partial mapping does not claim full source-suite coverage.
- `scripts/build_materialized_input_index.py` writes `coverage_status: partial` for every link and creates a scope sentence saying unlisted functions, branches, configurations, and edge cases are not claimed.
- `scripts/build_fastapi_compatibility_atlas.py` states that `reviewed_partial` means the linked evidence/workflows/cases/selectors were reviewed, not that the source behavior is complete or parity-proven. It also distinguishes `mapping_status` from `review_status`: a `candidate` row can have a reviewed partial mapping and exact workflow links.
- `scripts/parity/coverage.py` requires each non-excluded test/page row to have a fixture and selectors; each reviewed partial row also needs a workflow link. For tests it rejects unmatched functions and checks backlog case-design IDs against the module’s matched-function map. It checks page section feature/selector mappings and requires source evidence for reviewed page mappings.

Consequently, the 43 test rows labelled `candidate` are not missing links: all 453 non-excluded test rows have `review_status: reviewed_partial`, fixture IDs, selectors, and index links. The label is a source-to-feature mapping classification, not a claim of no workflow. Conversely, `reviewed_partial` is not a complete mapping state. No full-coverage status exists in the index schema or current atlas rows.

The validators establish file identity, source hashes, structure, source citations, case/selector linkage, and absence of expected output values in design artifacts. They do not execute the target, establish FastAPI-RS parity, prove semantic independence of every stimulus from upstream test literals, or establish full branch/function coverage. The current materialized index is an input corpus, not a parity result.

## Feature-family association snapshot

Counts are `linked rows / rows tagged to the family`; families overlap, so rows must not be summed. “Linked” here means a non-excluded atlas row with at least one input workflow link.

| Feature family | Test modules | Documentation pages |
| --- | ---: | ---: |
| `app-routing` | 104 / 105 | 69 / 71 |
| `root-path` | 7 / 7 | 1 / 1 |
| `request-validation` | 239 / 256 | 46 / 47 |
| `request-body` | 8 / 10 | 0 / 0 |
| `dependency-security` | 96 / 104 | 39 / 39 |
| `dependency-overrides` | 3 / 3 | 1 / 1 |
| `response-serialization` | 282 / 286 | 32 / 34 |
| `status-codes` | 64 / 73 | 0 / 0 |
| `python-data-encoding` | 2 / 2 | 6 / 6 |
| `openapi-docs` | 324 / 330 | 59 / 59 |
| `websocket-lifecycle` | 13 / 13 | 8 / 8 |
| `asgi-error-propagation` | 4 / 4 | 0 / 0 |
| `middleware-integrations` | 11 / 16 | 8 / 13 |
| `static-files` | 1 / 1 | 0 / 0 |
| `public-api-errors` | 102 / 105 | 29 / 31 |

There are no docs-page tags for `request-body`, `status-codes`, `asgi-error-propagation`, or `static-files`. This is a feature-to-page taxonomy gap, not an unclassified page row: for example, `tutorial/body.md` is tagged `request-validation`; `tutorial/response-status-code.md` is tagged `response-serialization`/`openapi-docs`/`public-api-errors`; the static-files reference page is explicitly excluded as a Starlette re-export; and there is no dedicated ASGI error-propagation guide.

## Selector support and coverage limits

The selector catalog has 50 definitions: 30 `supported`, 16 `planned`, and 4 `partial`. The index uses 33 distinct selector IDs, with **296 partial-selector occurrences** and **zero planned-selector occurrences**:

- `openapi.paths`: 265
- `validation.error_class`: 21
- `error.public_attributes`: 6
- `validation.error_details`: 4

Important planned observations include `http.body.json`, `http.cookies`, `route.match`, `dependency.call_order`, `dependency.cleanup_order`, lifecycle event/cleanup effects, and process stdout/stderr/exit code. Feature-family observation lists include some planned IDs, but the materialized index builder filters them from workflow mappings. Selector names in the atlas therefore do not by themselves prove the runner can observe that projection. `openapi.paths` is partial, so its selected-path observations are narrower than a full OpenAPI document; validation/error selector use is also limited by the partial definitions.

## Authorities, validators, and recipe format reviewed

- `AGENTS.md` requires pinned FastAPI 0.141.1 and sole Starlette 1.6.0 oracle, input-only YAML recipes, an explicit observation/feature map or exclusion, and no parity claims from inventory alone.
- `metadata.yaml` pins FastAPI 0.141.1 / commit `95f8322…`, Starlette 1.6.0 / commit `4f250d6…`, CPython 3.12.13, and Pydantic 2.13.4. It is the canonical identity/policy source.
- `tests/fixtures/manifest.yaml` records the atlas, backlog, selector catalog, and materialized-index digests/counts. It labels the fixture backlog `source-linked input-only fixture design queue; no expected results`, the index partial, and `fixture_backlog_integrity` as `source-linked-designs-validated; incremental-materialization-indexed; full-backlog-pending`.
- `scripts/parity/coverage.py` validates coverage rows against source hashes, fixture IDs, selectors, workflow links, fixture design source evidence, and input-only constraints. Its checks are static contract checks; this audit did not invoke them.
- `scripts/build_materialized_input_index.py` derives the active index from materialized JSON workflows under `tests/fixtures/inputs/parity/`, links each case’s source evidence to atlas source rows, intersects declared source selectors with selectors actually observed by that case, and hard-codes partial status/scope.
- `tests/fixtures/input-recipes/parity/` contains YAML recipes. For example, `path-params-tutorial001-upstream.yaml` declares a workload factory, separate HTTP/OpenAPI requests, exact recipe observations, and source-evidence paths. The workflow schema has no expected-result field; active coverage validation rejects expected-output data in design artifacts.

## Priority actions

1. Preserve the distinction in release/support language: the current gate closes source-row traceability, not complete compatibility coverage or parity.
2. If complete upstream test coverage is a goal, add a durable test-function-to-workflow/case link and report which of the 2,118 function designs are executable, explicitly excluded, or still candidates. Module-path evidence alone cannot prove per-function coverage.
3. Prioritize runner support and use of the 16 planned selectors that block meaningful observations (notably parsed JSON, cookie projection, route matches, dependency order, lifecycle cleanup, and subprocess results); expand the four partial selectors before using them as broad coverage evidence.
4. Reconcile the four feature families with zero page tags, retaining explicit ownership/exclusion rationale where a feature has no FastAPI-owned guide.
5. Keep exclusions reviewed and source-justified. Current validators enforce a reason string, but not a structured source citation or correctness review for each exclusion.

## Audit method and limits

Counts were computed read-only from the current atlas/index/backlog JSON and the pinned `../fastapi` checkout; source inventory path sets and SHA-256s were compared directly. Active validators, schemas, metadata, manifest, and representative YAML recipes were inspected. No pytest, unittest, Cargo test, oracle/target parity run, `make parity-validate`, or metadata update command was executed. No active artifact was edited; this report is a draft only.
