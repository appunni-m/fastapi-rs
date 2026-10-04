# FastAPI 0.141.1 atlas reason and selector completeness audit

**Draft, 2026-10-04.** Read-only audit of the active compatibility atlas, materialized input index, selector catalog, validator, and pinned source trees. FastAPI source is `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` (0.141.1); Starlette is `4f250d6b814587e20c5365f0a5f0c4d42bcb929f` (1.6.0), as recorded in `metadata.yaml` and `tests/fixtures/compatibility-atlas.json`. No active recipes, metadata, generated artifacts, or tests were changed. No tests, parity runs, or benchmarks were run.

## Finding

The active atlas closes the **source-row disposition** requirement: all 492 upstream test modules and 155 English feature pages are either linked to an input workflow or excluded with a reason, with no pending rows. The 557 linked rows each have a fixture reference, selectors, and exact workflow/case links. The exclusion totals do **not** establish that every test exclusion is source-backed, and module/page links do **not** establish full source behavior coverage.

| Pinned source inventory | Rows | Input-linked rows | Excluded rows | Pending |
| --- | ---: | ---: | ---: | ---: |
| `tests/test_*.py` modules | 492 | 453 | 39 | 0 |
| `docs/en/docs/**/*.md` feature pages | 155 | 104 | 51 | 0 |
| **Combined requested denominator** | **647** | **557** | **90** | **0** |

The active atlas source digests for all 39 excluded test modules and all 51 excluded pages matched the pinned FastAPI files. The counts above are current for this checkout; the materialized index has 527 workflows and 1,484 source-to-workflow mappings.

## What the mapped counts establish

Every linked test-module row (453/453) and page row (104/104) has a fixture id, nonempty selectors, and at least one `independent_workflow_mappings` entry. These entries total 902 test-module links and 228 page links. I matched all **1,130/1,130** atlas links to the materialized input index by source, workflow, case ids, selector ids, and recipe path; none were missing or mismatched. Every link carries a nonempty recipe path, case id list, and observation-selector list.

The exact workflow-link selectors are usable under the selector catalog: test-module links select 2,836 supported and 196 partial selector occurrences; page links select 688 supported and 42 partial occurrences. They use no planned selectors. This is the right field to use when checking a fixture mapping.

Do not treat the coverage row’s top-level `observation_selectors` as that exact per-workflow selector set. Those lists include broad family selectors: **443/453** mapped test rows carry at least one planned selector (1,668 occurrences across 15 ids), as do **37/104** mapped pages (120 occurrences across 12 ids). For example, the row-level lists include `http.body.json`, `dependency.call_order`, `route.match`, `process.stdout`, and `lifecycle.cleanup_effects`, even where no linked workflow observes them. Their presence describes feature-family expectations, not the mapped recipe’s observations. The per-workflow mapping lists above contain only supported or partial selectors.

All 1,130 input-index links are expressly `coverage_status: partial`; the index schema says unlisted functions, branches, configurations, and edge cases are not claimed (`tests/fixtures/schemas/materialized-input-index.schema.json:3-5, 80-110`). Thus “453 modules mapped” is a traceability result, not a claim that all 453 upstream modules’ tests have corresponding inputs.

## Exclusion evidence gap

All 90 excluded rows have a nonempty `exclusion_reason` and no fixture. However, the validator’s exclusion branch checks only excluded status, reason presence, and null fixture (`scripts/parity/coverage.py:1011-1022`). It does not require a source citation or establish that a reason follows from source evidence.

For the 51 excluded documentation pages, all 51 `reviewed_source_mapping` records include source evidence with a source path, line span, and hash. For upstream test modules, only **9/39** excluded rows include `supporting_sources` or function-level `source_evidence`; the other **30/39** carry a reason and the module path/hash, but no reason-linked line citation in the active row. The nine cited modules are `tests/test_dependency_models.py`, the five comment-only unsupported parameter modules under `tests/test_request_params/`, `tests/test_tutorial/test_custom_response/test_tutorial001b.py`, `tests/test_tutorial/test_custom_response/test_tutorial009c.py`, and `tests/test_tutorial/test_dependencies/test_tutorial007.py`. The remaining reasons may be verifiable by opening the hashed source, but the current aggregate and validator do not prove that.

## Function-level and selector limits

The atlas reports 2,118 test-function designs: 371 `reviewed_source_candidate`, 1,236 `contract_gated_source_candidate`, and 511 `candidate`. These are classifications in the design queue, not 2,118 executable inputs. The atlas stores module-level workflow links; the materialized index mapping schema has source, workflow, cases, and selectors but no test-function name. The builder permits a module to become `reviewed_partial` through a module review plus one or more workflows, or through statuses assigned to each function design (`scripts/build_fastapi_compatibility_atlas.py:8941-8947`; `scripts/parity/coverage.py:1052-1089`). It does not require an independent workflow/case link for each upstream test function.

Consequently, the mapped/excluded counts prove useful, exact **row-level traceability**, but do not prove per-function mapping completeness, selector completeness for every upstream assertion, or source-backed evidence for every excluded test module.

## Highest-impact unresolved item: FastAPI CLI

The CLI is a concrete visible feature behind two excluded rows. `tests/test_fastapi_cli.py:10-34` checks a subprocess invocation of `python -m coverage run -m fastapi dev` plus the missing-CLI error path. The feature page documents `fastapi dev`, `fastapi run`, path discovery, and `--entrypoint` (`docs/en/docs/fastapi-cli.md:1-7, 98-124`). The pinned package declares the `fastapi` script as `fastapi.cli:main` and lists `fastapi-cli[standard]` as an optional dependency (`../fastapi/pyproject.toml:97-120`). The active atlas excludes both the module and page; the reason is a runner/package boundary, and `process.stdout`, `process.stderr`, and `process.exit_code` remain planned (`tests/fixtures/observation-selectors.json:201-218`). The unresolved point explicitly asks whether FastAPI-RS replaces that command and which package identity, optional environment, arguments, streams, and exit behavior are in scope (`scripts/build_fastapi_compatibility_atlas.py:9672-9675`).

## Recommended next wave

Run a focused **CLI contract and exclusion-evidence wave**:

1. Record line-span source evidence for the 30 excluded test-module reasons that currently have none, retaining the exclusion only where the pinned source supports it.
2. Resolve the CLI product boundary and version/profile. If the console command is in scope, add an isolated subprocess input workflow and supported stdout/stderr/exit-code selectors, then map the CLI tests and documented command cases. If it is out of scope, record the separate owner and explicit scope decision in the reviewed overlay so the exclusion is auditable.
3. Keep the resulting status partial and report function-level coverage separately until each source function has an explicit case link or source-backed exclusion.

This wave addresses the clearest user-visible exclusion and the current gap between nonempty exclusion reasons and evidence-backed exclusions without inflating the 557 row-level mapping count into a full-coverage claim.
