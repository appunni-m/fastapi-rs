# Additional response field admission: independent review

Date: 2026-10-05. Reviewer: `override_reanalysis`. Static admission review only; no application import, live worker, parity, native binary read, build, installation, unit test or repository/sibling write was performed. Root reported regeneration closed with exit 0; the final generated-index audit is recorded below.

## Metadata boundary

Compared committed `HEAD:metadata.yaml` (SHA-256 `4d7c3566f1cd282852c158cbe2a374f14e54fac5338a5c584059b61c8fb26cb7`) with `/private/tmp/fastapi-rs-additional-response-field-admitted-metadata.yaml` (SHA-256 `09038fbb5d1778405e94fa482197abe111835e7185ebb5cf98f285a43048781d`). During review, working-tree metadata became byte-identical to the proposal. The structural diff contains exactly 26 new fixture links across 10 existing operation rows. The only other operation change is a bounded `FastAPI.__init__.supported_slice` paragraph. Everything outside `reviewed_api_contract_overlay.operations` is identical. Existing operation evidence, feature IDs, operation selectors, bindings, classifications, normalizers, identities/pins and public/private dispositions are unchanged.

Case abbreviations below are only presentation: saved = `fastapi.additional-response-field-lifecycle.saved-decorator-attachment`; contexts = `fastapi.additional-response-field-lifecycle.shared-router-two-contexts`; retry = `fastapi.additional-response-field-lifecycle.second-additional-hook-retry`.

| Existing operation | Added cases | Links |
| --- | --- | ---: |
| `fastapi.applications.FastAPI.__init__` | saved, contexts, retry | 3 |
| `fastapi.applications.FastAPI.__call__` | saved, contexts, retry | 3 |
| `fastapi.applications.FastAPI.get` | saved, contexts, retry | 3 |
| `fastapi.applications.FastAPI.exception_handler` | saved, contexts, retry | 3 |
| `fastapi.responses.JSONResponse` | saved, contexts, retry | 3 |
| `fastapi.Request` | saved, contexts, retry | 3 |
| `fastapi.APIRouter` | contexts, retry | 2 |
| `fastapi.routing.APIRouter.__init__` | contexts, retry | 2 |
| `fastapi.routing.APIRouter.get` | contexts, retry | 2 |
| `fastapi.applications.FastAPI.include_router` | contexts, retry | 2 |
| **Total** | | **26** |

These calls are ordinarily reachable in the unchanged workload: all cases construct/call FastAPI, register `/state` and the endpoint through `get`, register the public exception-handler decorator, construct JSONResponse in every state action, and inject Request into endpoints. Contexts/retry additionally construct the root APIRouter export, call its canonical constructor/get implementation, and include that original router through FastAPI. No alias-identity assertion is claimed by linking alias and canonical constructor. All cases register the handler; only retry invokes it. State routes do not have a Request parameter; endpoint Request projections include actual query value/path, and the retry handler includes actual path. Generic Request behavior stays sibling-owned.

The three Request fixture declarations select only `http.status` and `http.body.bytes`. The other links use the existing eight case selectors. No new `FastAPI.openapi`, `APIRouter.include_router`, `api_route`, `add_api_route`, private field/cache or DefaultPlaceholder operation is mapped.

## Source documentation requirements

No extra recipe source path is mechanically required for these direct operation links. `scripts/parity/api_contract.py:978` resolves direct `overlay.operations` links against one materialized recipe/case and current file digests; it does not require each linked case to repeat every operation documentation path. The stricter case-documentation-subset rule at `scripts/parity/api_contract.py:812` applies to `inherited_operations`, which these ten rows are not. `scripts/build_materialized_input_index.py:365` constructs source requirement refs from actual recipe evidence/source mappings; direct API probe refs require actual probes. The new ASGI cases already contain reviewed additional-response documentation/test evidence with usable observed selectors.

Unchanged Request overlay evidence includes `docs/en/docs/advanced/using-request-directly.md`; the pinned page lines 18-20/34/52-54 support direct Request injection and sibling ownership. Unchanged exception-handler overlay evidence includes `docs/en/docs/tutorial/handling-errors.md:82-108`, supporting registration, ordinary custom-error handling and Request/JSONResponse convenience exports. The retry recipe directly includes handling-errors; saved/contexts do not claim a positive handler invocation. Adding either page to more recipes is an optional source-coverage expansion, requiring fresh recipe/materialized digests, not a prerequisite for this metadata-only admission. No missing-doc shortcut or new coverage claim is needed.

## Generated-selector caveat

The current direct-operation resolver ignores `fixture_reference.observation_selectors`: at `scripts/parity/api_contract.py:1061` it returns the entire materialized case selector set. Consequently Request's generated `operation_fixture_refs` are expected to carry all eight case selectors despite the two-selector reviewed link declaration. This is full-case provenance, not evidence that Request independently owns header/send/construction observations. The reviewed Request operation-level selectors remain status/body/OpenAPI. The generated Request aggregate selectors also remain unchanged from HEAD; they additionally include existing documentation/identity evidence (`dependency.call_order`, `python.import_path`, `python.object_identity`, `route.match`). Symbol assembly at `scripts/parity/api_contract.py:3043` incorporates operation-level selectors, documentation and direct API probes, but does not union operation fixture refs.

This pre-existing generator behavior is disclosed; do not report that the generated Request fixture-ref selector list itself is restricted to status/body unless it is changed and reviewed separately. It does not change the actual full workflow comparator or its input selectors. Root owns any generator decision. The metadata declarations themselves preserve the intended Request integration boundary.

## Frozen input bindings

Active and archived/historical recipe/workload copies were verified byte-identical to the frozen proposal:

| File | SHA-256 |
| --- | --- |
| `tests/fixtures/input-recipes/parity/additional-response-field-lifecycle.yaml` | `199ab0b81d4b1e923933a13f076c49bb89229add1e0c90ce441902c0c5db7ae1` |
| `tests/fixtures/workloads/additional_response_field_lifecycle.py` | `ef756492903a719a8b3522bc1971794663083bcbb55ed20076b74f988d0e8025` |
| Archived proposal review plan | `d9c6ff61722a264924ad2abc16a47d4751021f25ce3053359c608d305143d102` |
| Prior independent source/input review | `cef8badbe3610bb8e76746362c9f682a58273b5cd810ddbb93e911dd6d472b7c` |
| Archived native design | `830fdc322053a08131bd1b85a2e53eaab49c4de8de588a51bfd93c330b340efb` |

Inputs retain 3 parity cases, 15 GET actions (3/5/7 by case), 9 state and 6 endpoint actions, and 3 construction observations. Exact warning/error and lossless earlier send journals are selected through full state-body bytes. No expected outputs, normalizations, private lookup, implementation detection, new fault hook or OpenAPI request was introduced. Extra-before-dependency timing and positive JSON-hook/shared-definition generation remain source/design distinctions outside these three inputs. The unrelated immutable sibling BackgroundTasks worker-crossing blocker is unchanged.

## Post-regeneration audit

Completed after root's explicit regeneration-ready notification. `parity-results/additional-response-field-admission-static.log` records the closed `make parity-inputs parity-index-update compatibility-atlas-update metadata-check python-facade-check` sequence. Its final metadata and facade checks are successful. Parent's separate `parity-validate`/API-contract checks are outside this note's executed-command claims.

The reviewer loaded only static documents and canonical `read_recipe`, never the workload/factory. Canonical schema-9 recipe output and generated JSON are structurally identical. Actual input digest, recipe/workload paths and digests agree in the index and every one of the 26 generated operation fixture refs. Unique action IDs retain the exact declared order and all actions are ordinary GET requests. There is one indexed workflow for this family, three case contracts marked `parity`, and no fault metadata. Construction selects outcome/class/message. All cases retain the same eight selected selectors listed above.

| Actual case | GET actions | State | Endpoint |
| --- | ---: | ---: | ---: |
| saved | 3 | 2 | 1 |
| contexts | 5 | 3 | 2 |
| retry | 7 | 4 | 3 |
| **Total** | **15** | **9** | **6** |

The source-only requirement refs are exactly derived from the eight family source mapping rows, not inferred from API link names:

| Source mapping | Cases |
| --- | --- |
| `documented-page:advanced/additional-responses.md` | saved, contexts, retry |
| `documented-page:tutorial/response-model.md` | saved |
| `documented-page:tutorial/bigger-applications.md` | contexts |
| `documented-page:tutorial/handling-errors.md` | retry |
| `upstream-test:tests/test_additional_responses_router.py` | saved, contexts, retry |
| `upstream-test:tests/test_additional_responses_response_class.py` | contexts |
| `upstream-test:tests/test_router_include_context.py` | contexts, retry |
| `upstream-test:tests/test_additional_responses_bad.py` | retry |

All eight rows are explicitly partial mappings; no `openapi.document` selector is attributed to the new family. Seven rows map the observed send message types and status/headers/body; the bad-additional model source row has its existing narrower send-message-types/body mapping. Per-case source requirement counts are 3, 5 and 5. There is no new direct-API-probe or inherited-operation requirement.

Actual corpus totals agree with manifest counters: **553 workflows, 2297 cases, 1571 partial source mappings**. The manifest contains **1326 operation fixture refs**, compared with HEAD's 1300, so the delta is exactly 26. The new family maps exactly the ten operations in the table, with no stray OpenAPI/private/inherited operation. All generated API symbol target bindings and aggregate selector lists remain equal to HEAD. The candidate classification map was compared by every candidate ID, not just counts, and is identical: **460 supported, 1102 private/internal, 31 uncertain**. Request's three reviewed link selector lists are exactly status/body; its three generated fixture refs carry the full eight-selector case provenance as disclosed above. Its seven-selector aggregate set is unchanged.

| Finished artifact | SHA-256 |
| --- | --- |
| `metadata.yaml` | `09038fbb5d1778405e94fa482197abe111835e7185ebb5cf98f285a43048781d` |
| `tests/fixtures/manifest.yaml` | `ae88fc58d1ead1a70cf3b9435c470b16794a03f050f368eb0e68f7c4457cc697` |
| `tests/fixtures/materialized-input-index.json` | `517719a589e8199d64fdf5f99aabe864f8a0e954e22540bc6f40b2e4581c631f` |
| `tests/fixtures/inputs/parity/additional-response-field-lifecycle.json` | `8ec188213588f06c8a107941f442f8f9bf69020828ae42626238f247c4944190` |
| `tests/fixtures/compatibility-atlas.json` | `086963d655e1e458c79d6b4744c04e88c3bfb02020b82d430d41addad6339ecc` |
| Closed admission static log | `e7a0a8dde397029d38f914293b86173e47d6f0202180cbfd4afb9973ecc823c6` |

The proposals README states mapping admission and explicitly requires the isolated pinned source gate and unchanged-target diagnosis; it does not claim a new successful product execution. The metadata/materialized/index mapping admission is clear for root's source-first pre-run, subject to root closing its separate static checks and committing/fixing the source identity. This note makes no source/target parity, implementation support, coverage or benchmark claim for the three cases. Root alone owns live execution and any native repair. No active files were changed by this reviewer.
