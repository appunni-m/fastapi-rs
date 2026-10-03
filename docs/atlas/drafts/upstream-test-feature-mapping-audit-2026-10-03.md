# FastAPI 0.141.1 test and feature mapping audit

> Read-only audit of the pinned FastAPI source, active input index, compatibility atlas, and the clean Starlette-RS checkout at `693050dce44a52a54eb319c47ec2ff15e55fa608`. No source tests were copied. No recipe, exclusion, metadata, or generated atlas mapping was changed.
>
> **Snapshot note:** Counts and digests below describe the FastAPI-RS files before concurrent active atlas/metadata updates in this shared checkout; they are not a post-update validation.

## Authorities and denominator

The local FastAPI source checkout is exactly `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, the pinned 0.141.1 revision. The atlas has one coverage row for every source file in each audited category; SHA-256 checks found no missing source files or digest mismatches across all 1,108 rows.

| Source inventory | Pinned-source denominator | Active workflow mapping | Explicit exclusion |
| --- | ---: | ---: | ---: |
| Upstream `tests/test_*.py` modules | 492 | 452 (`reviewed_partial`; 409 `partially_mapped` + 43 `candidate`) | 40 |
| User-facing English docs pages under `docs/en/docs` | 155 | 104 (`reviewed_partial`) | 51 |
| `docs_src/**/*.py` example files | 370 | 333 (`reviewed_partial`) | 37 |
| `docs_src/**/*.py` support files, chiefly package initializers | 91 | 0 | 91 |

The source inventories, not the count of recipes or candidate signals, are the denominators. The 15 atlas feature families overlap; their row counts below must not be added. The input index contains 514 workflows, 2,037 cases, and 1,468 source-to-workflow mappings. These are inputs and reviewed partial links, not parity results or complete source coverage.

## Feature-family links

Counts below are `test modules linked / test modules tagged` and `docs pages linked / docs pages tagged`. Pages and modules may carry multiple family tags. A linked page is still partial evidence.

| Feature family | Test modules | Docs pages |
| --- | ---: | ---: |
| `app-routing` | 104 / 106 | 69 / 71 |
| `root-path` | 7 / 7 | 1 / 1 |
| `request-validation` | 240 / 257 | 46 / 47 |
| `request-body` | 8 / 10 | 0 / 0 |
| `dependency-security` | 96 / 104 | 39 / 39 |
| `dependency-overrides` | 3 / 3 | 1 / 1 |
| `response-serialization` | 282 / 286 | 32 / 34 |
| `status-codes` | 63 / 72 | 0 / 0 |
| `python-data-encoding` | 2 / 2 | 6 / 6 |
| `openapi-docs` | 325 / 331 | 59 / 59 |
| `websocket-lifecycle` | 13 / 13 | 8 / 8 |
| `asgi-error-propagation` | 4 / 4 | 0 / 0 |
| `middleware-integrations` | 11 / 16 | 8 / 13 |
| `static-files` | 1 / 1 | 0 / 0 |
| `public-api-errors` | 101 / 104 | 29 / 31 |

Four families have no dedicated page tag: `request-body`, `status-codes`, `asgi-error-propagation`, and `static-files`. This is a taxonomy association gap, not a missing test-module mapping: respectively, `tutorial/body.md` is tagged as request validation, `tutorial/response-status-code.md` is tagged as response/OpenAPI/API errors, ASGI propagation has no dedicated user guide, and `reference/staticfiles.md` is explicitly excluded as a Starlette re-export. Their associated test modules do have workflow mappings or explicit exclusions.

## Test modules without an active input-workflow link

All 40 rows are explicitly excluded with reasons; none is an unexplained/pending test-module row. The complete row-level evidence and individual function dispositions remain in `tests/fixtures/compatibility-atlas.json`.

| Exclusion group | Modules |
| --- | --- |
| Benchmarks (5) | `tests/benchmarks/test_general_performance.py`, `tests/benchmarks/test_openapi.py`, `tests/memory_benchmarks/test_dependency_graph.py`, `tests/memory_benchmarks/test_openapi.py`, `tests/memory_benchmarks/test_route_dependency_graph.py` |
| Internal, release, or generic Starlette behavior (4) | `tests/test_dependencies_utils.py`, `tests/test_dependency_models.py`, `tests/test_prepare_release.py`, `tests/test_router_redirect_slashes.py` |
| Optional ORJSON/UJSON profiles (4) | `tests/test_deprecated_responses.py`, `tests/test_orjson_response_class.py`, `tests/test_tutorial/test_custom_response/test_tutorial001b.py`, `tests/test_tutorial/test_custom_response/test_tutorial009c.py` |
| Runner/profile boundary (2) | `tests/test_fastapi_cli.py`, `tests/test_stringified_annotation_dependency_py314.py` |
| Comment-only unsupported parameter variants (5) | `tests/test_request_params/test_cookie/test_list.py`, `tests/test_request_params/test_cookie/test_optional_list.py`, `tests/test_request_params/test_path/test_list.py`, `tests/test_request_params/test_path/test_optional_list.py`, `tests/test_request_params/test_path/test_optional_str.py` |
| Tutorial code outside FastAPI's runtime contract (20) | `tests/test_tutorial/test_dependencies/test_tutorial007.py`, `tests/test_tutorial/test_generate_clients/test_tutorial004.py`, `tests/test_tutorial/test_graphql/test_tutorial001.py`; all 12 modules in `tests/test_tutorial/test_python_types/` (`test_tutorial001_tutorial002.py`, `test_tutorial003.py` through `test_tutorial011.py` except `test_tutorial012.py`, plus `test_tutorial013.py`); `tests/test_tutorial/test_settings/test_app03.py`, `tests/test_tutorial/test_settings/test_tutorial001.py`, `tests/test_tutorial/test_sql_databases/test_tutorial001.py`, `tests/test_tutorial/test_templates/test_tutorial001.py`, `tests/test_tutorial/test_wsgi/test_tutorial001.py` |

The final row's `test_tutorial003.py` through `test_tutorial011.py` shorthand is not a literal continuous range: the exact modules are `test_tutorial003.py`, `test_tutorial004.py`, `test_tutorial005.py`, `test_tutorial006.py`, `test_tutorial007.py`, `test_tutorial008.py`, `test_tutorial008b.py`, `test_tutorial009_tutorial009b.py`, `test_tutorial010.py`, and `test_tutorial011.py`.

## Observation-selector gaps

The selector catalog has 50 selectors: 30 `supported`, 16 `planned`, and 4 `partial`. The 16 planned selectors are `dependency.call_order`, `dependency.cleanup_order`, `error.args`, `error.class`, `http.body.json`, `http.cookies`, `http.header.absent:{lowercase_header_name}`, `lifecycle.cleanup_effects`, `lifecycle.event_order`, `process.exit_code`, `process.stderr`, `process.stdout`, `python.import_path`, `python.object_identity`, `response.background_effects`, and `route.match`. The 4 partial selectors are `error.public_attributes`, `openapi.paths`, `validation.error_class`, and `validation.error_details`.

At the materialized mapping level, 284 of 1,468 rows use at least one partial selector (295 selector occurrences: 264 `openapi.paths`, 21 `validation.error_class`, 6 `validation.error_details`, 4 `error.public_attributes`). No materialized mapping row requests a planned selector. The feature-family observation lists still name planned selectors, so their presence in an atlas row must not be read as runner support. Largest gaps are exact body JSON, cookie projections, route matching, dependency call/cleanup order, response background effects, lifecycle ordering/cleanup, process stdout/stderr/exit status, and direct Python import/identity checks. Validation details/class, selected OpenAPI paths, and public exception attributes are only partial.

## Starlette-RS crosswalk, revision-bound

The FastAPI atlas currently records implementation revision `2f9978d4c8e28443a176b83fb9a6f2b9966d0953`, manifest SHA-256 `aa3108780be0d225f0e1e234768417446b945f0f7b16b1f013aa1a221d73ddec`, and coverage-matrix SHA-256 `57ddad6e3a2547bd79ccf1c45344ff59c0cac7005d111588e22b00bf40d49145`. The clean checkout specified for this audit is at `693050dce44a52a54eb319c47ec2ff15e55fa608`; its manifest SHA is `a9d723785c9f76f0d41c14b770d39e55a8140a4091122ec9a7df1efa8ecf4dd9` and coverage-matrix SHA is `f2bd03e4415cc7be46a6a241752f239d84971d57029cfd52f828de1223b858e9`. Its `docs/api-surface.csv` and `docs/atlas/api-review.csv` hashes still match the FastAPI atlas references.

At revision `693050d`, the sibling manifest has 51 surfaces, 94 operations, and 831 unique operation requirement IDs; its API catalog/review has 999 rows (530 supported, 285 private/internal, 184 uncertain), coverage matrix 802 rows, and fixture backlog 184 rows. The FastAPI atlas has 133 direct integration-edge records and 2,895 row-level sibling mapping objects across 924 source rows. Their 3,429 repeated operation references resolve to 12 distinct operation IDs across 6 surfaces in the clean latest manifest; all referenced requirement IDs exist there and the selected target statuses match. The main workstream regenerated the active atlas and manifest against 693 after this snapshot, refreshing the stored implementation, manifest, and coverage hashes.

## Verification and disposition

No active mapping batch was appropriate: every non-linked upstream module/page is explicitly excluded, the four zero-page feature associations are taxonomy/ownership cases, and selector gaps require runner support rather than input-only recipe edits. I added this report only; no recipe or atlas/exclusion update was made.

Commands and checks used:

```sh
git -C /Users/lazytrot/work/fastapi rev-parse HEAD
find /Users/lazytrot/work/fastapi/tests -type f -name 'test_*.py' | wc -l
find /Users/lazytrot/work/fastapi/docs/en/docs -type f -name '*.md' | wc -l
find /Users/lazytrot/work/fastapi/docs_src -type f -name '*.py' | wc -l
find tests/fixtures/input-recipes/parity -maxdepth 1 -type f -name '*.yaml' | wc -l
git -C /tmp/fastapi-rs-starlette-rs-693050d rev-parse HEAD
make parity-validate
```

The source-digest comparison was an inline Python SHA-256 comparison of each atlas `coverage_matrix` row against the same relative path below `/Users/lazytrot/work/fastapi`; result: 0 missing files and 0 mismatches across 1,108 rows. The latest-checkout crosswalk comparison parsed its `tests/fixtures/manifest.yaml` and matched every FastAPI atlas operation reference, requirement ID, and target status. `make parity-validate` initially stopped on the old pin; after the main workstream regenerated against 693, the validation completed successfully with 514 workflows, 2,037 cases, and 1,468 source mappings. No pytest, unittest, or Cargo test command was run.

### Pin follow-up

The counts above are a snapshot of the feature-mapping audit. Starlette-RS `main` later advanced to `4807b3a11efcb96c6ac2bf8537e806b6971aed37`, adding three direct middleware requirements in the sibling manifest. They do not change the FastAPI upstream module or documentation inventory. The active generated crosswalk and source identities have been refreshed to `4807b3a`; the FastAPI feature-to-fixture gaps in this snapshot remain unchanged.


Starlette-RS subsequently advanced to `baea19981ba3119d362be8c3a1b0913e4824313e` for a benchmark-documentation refresh only. The active FastAPI pin now tracks that head; the FastAPI inventory and feature-mapping counts above are unaffected.
