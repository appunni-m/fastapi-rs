# Additional response-field final normal receipt audit

Date: 2026-10-05. Independent read-only audit of the closed receipt directory `/Users/lazytrot/work/fastapi-rs/parity-results/additional-response-field-wave/final-normal/`. No receipt/admission/identity blocker was found.

## Complete aggregate

All **43 workflows / 203 cases** pass ordinary parity: 203 passed, zero failed, zero not run, zero fault-contract cases. Every oracle, target, and comparison CLI exits 0. The full case inventories, their ordering, and every declared action/probe are present in both products and comparisons.

| Lane | Workflows | Cases | Completed operations per product | Indexed observations per product |
| --- | ---: | ---: | ---: | ---: |
| ASGI | 40 | 199 | 504 actions (499 HTTP, 5 WebSocket) | 838 |
| Direct Python API | 3 | 4 | 15 probes | 15 |
| Total | 43 | 203 | 519 | 853 |

There are 93 explicit constructor observations: 86 successful constructions and seven matching ordinary error controls. Another 106 legacy ASGI cases complete construction implicitly; their schema does not expose a separate constructor observation. The seven error controls declare zero actions, so they are completed comparisons, not skipped actions. They are the two invalid dependency-scope cases (`fastapi.exceptions.DependencyScopeError`), four ambiguous-parameter cases (`builtins.AssertionError`), and unsupported response-model construction (`fastapi.exceptions.FastAPIError`). Their full selected class/message observations match; no error projection was weakened.

Every result and comparison reports completed status and no infrastructure errors; all reported product-error inventories are empty. This does **not** mean that no application exception was observed: 121 selected application-error observations include 111 nulls, one RuntimeError, one ResponseValidationError, six ValueErrors, and two TypeErrors, all matching source and target. The direct-call lane also retains its declared raised/returned outcomes.

The indexed observation totals are: 495 HTTP responses, 177 ASGI message-type sequences, 121 application errors, 33 OpenAPI observations, 12 WebSocket observations, 10 Python call outcomes, two Python return values, and three Python signatures. All actual selected values were independently compared and match, and all comparator cases contain empty difference lists.

## Contracts, artifact integrity, and execution scope

All 43 materialized inputs match their captured initial/final input hashes and the committed admission index at `6da823585dbe4605ff1e04204eee287813eb34e8`. Each matching index row binds the exact committed recipe and workload hashes, case inventory, and nonempty required API references; all 203 case contracts are ordinary parity. The snapshot uses input filename stems: the receipt family `security-full` correctly binds `security_oauth_openapi_upstream.json`.

All **172 stored documents** (43 inputs, 86 product results, 43 comparisons) pass JSON-schema and format validation against the exact committed contract schemas. These are 27 ASGI-v2 workflows, seven ASGI-v3, six ASGI-v9, and three Python API workflows (versions 1, 3, and 4); the version-specific result/comparison schemas were selected separately. No product or workload was imported for validation.

The 129 CLI logs parse to the exact corresponding summaries stored in `normal-runs.json`. Every comparison's result ID, path, and byte hash binds its actual source and target record. Source and target manifest/input references agree with each comparison. Per workflow, source finishes before target starts and target finishes before comparison creation. The helper runs independent workflows in batches with three workers; receipt-list order is an inventory order and is not a global chronological sequence. The complete captured interval is 11:52:20.765004–11:54:37.392268 UTC on 2026-10-05.

Commands are canonical `scripts.parity.cli`: 40 each of oracle/target/compare and three each of api-oracle/api-target/api-compare. All 43 target commands explicitly select `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`.

| Receipt or contract | SHA-256 |
| --- | --- |
| `normal-runs.json` | `10e356e1741f51f89000858dc169c1d0f6472ac90ccd2d66d6d697310e333810` |
| Both initial/final source-build snapshots (identical JSON and bytes) | `3a2922a1a05b366ac3f15faae56fd0d93f8f2c54b792db2898f097baa7da2318` |
| Committed manifest | `ae88fc58d1ead1a70cf3b9435c470b16794a03f050f368eb0e68f7c4457cc697` |
| Committed materialized-input index | `517719a589e8199d64fdf5f99aabe864f8a0e954e22540bc6f40b2e4581c631f` |
| Audit-derived ordered artifact hash ledger | `7ed078a0d897519e709f96749b8bbbce8e3be9ca3d5b855d7c5bd6d1eae1781f` |
| Audit-derived sorted 129-log hash ledger | `758d73f2446525641542d0001686abc17aee6dc75c5d158f9076a813df6575b5` |

The artifact-ledger digest is over the receipt-ordered array of each family's name, input hash, and source/target/comparison artifact path+SHA-256, serialized with sorted keys and compact separators. The log-ledger digest uses the same serialization over filename-sorted path+SHA-256 entries. These derived digests describe inspected actual records; they do not add expected outputs or modify receipts.

## Fixed source and binary bindings

Initial and final snapshots are identical, including all 43 input hashes. All 43 target record identities and CLI summaries bind the same captured source and native pair. Source/target identities, after excluding the schema-dependent fault-mode field, each have one consistent value across all workflows. Source package/Python/commit identities match the committed oracle profile; target Python/platform/shared versions match source and the sibling identity matches the manifest. Target package inventories and repository fields exclude the original FastAPI/Starlette runtime.

- Oracle: FastAPI 0.141.1 / `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; sole Starlette 1.6.0 / `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Target reported Git revision: `6da823585dbe4605ff1e04204eee287813eb34e8`; sibling `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.
- Runtime: CPython 3.12.13, Pydantic 2.13.4 / pydantic-core 2.46.4, AnyIO 4.12.1, Darwin arm64.

| Captured measured component | SHA-256 |
| --- | --- |
| FastAPI-RS source | `f7cd6b9ef3d93cd2da3c85a45a4a9eaf4ab1aeb97620d96c7ab2c44e7c1b166c` |
| Sibling source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `204d9a6aa869e6ec5623f6a93c07fa7973910784c7b63e64efd21f51ea17edf2` |
| FastAPI native core | `5eeae03b977c74fed3808df9194bef0d23527a8208b2c05c92f9415084b7a244` |
| Sibling native core | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Combined native pair | `8e1888dbe104c3bdf69f63b47bb0e9ded4a3ba9cc70d2c04676890134501f6ed` |

Combined digests were independently recomputed from the captured component hashes using the canonical sorted-name/NUL framing. The Git revision alone does not identify the applied uncommitted Rust delta; the captured source digest supplies that binding. This repaired measurement is distinct from pre-change source `d3080c…` / native pair `10b393…`.

The six schema-9 target workflows explicitly report `fault_injection_compiled=false`; their source field is null. The other 37 legacy result schemas omit that field. All share the same captured target binary pair, and every selected case is parity; this audit does not invent per-record mode fields absent from legacy schemas. No current native binary bytes were read. These captured bindings do not assert equality with an upcoming instrumented build, coverage run, later commit, or current installed module.

## New three cases: source preservation and exact repaired target

The final new source record is `17746fb5-e1ed-4b47-97f3-0263d3674848`, target `b23651d3-5968-4705-b417-a23618384e24`, comparison `e0d69765-e7f5-4d1d-a570-1d9dd2e8227c`. It selects three constructors and 15 actions (3/5/7), all completed, all passing. Their artifact hashes are respectively:

- Source: `6b25e324fb45a89de710d0c971404ce456be6442f1aa54fe074eb3b16a1b9d59`.
- Target: `fc19542502b888d1554d5fe734e12ec5ae44a8ce56d90de1a384b46ade1ad694`.
- Comparison: `8911dd84b09c0fe14aad98fc72f0713b44f6f3e124a5c8f4734ae0d20090d56b`.

Input `8ec188213588f06c8a107941f442f8f9bf69020828ae42626238f247c4944190`, workload `ef756492903a719a8b3522bc1971794663083bcbb55ed20076b74f988d0e8025`, and manifest references are identical to pre-change source record `97502d42-fdca-49f0-aaaa-0f0578b24a7d` (file SHA `12e9c028676bf0210380ff140a0092a6b24437d5aa234a7a901f284d1d0fd95a`). The **entire ordered case payload** from pre-change source, final source, and final target is equal, including constructor observations and all action observations. Its compact UTF-8 JSON SHA-256, preserving dictionary insertion order rather than sorting keys, is `eed3dd9b5a063eb943bc75fe7ef0022ba25273ba15f955cbb7b2e15e90a60c2c`. Run-envelope IDs/timestamps differ normally and were not treated as unchanged source observations.

| Case suffix | Preserved final public state on source and target | Warning entries | Full journaled sends |
| --- | --- | ---: | ---: |
| `saved-decorator-attachment` | Extra then primary core at attachment, 1/1; JSON hooks empty; direct endpoint 1 | 1 | 2 |
| `shared-router-two-contexts` | Extra/primary 1/1 → 2/2 → 3/3 for direct/left/right; JSON hooks empty; shared endpoint 2 | 0 | 4 |
| `second-additional-hook-retry` | First/second 1/1 → refused 2/2 → retry 3/3; primary ends 2 and endpoint 2; successful repeat performs no new construction; refusal remaining 0 | 6 | 6 |

All 15 selected HTTP bodies are exact base64-encoded bytes, so state journals retain ordered hooks, all actual warning category/message/stage entries, and handled errors without JSON-map-order elision. The seven warning entries are identical. The post-setup armed refusal returns identical HTTP 409, ordered `content-length:187` then `content-type:application/json`, with these exact body bytes:

```text
{"exception_class":"fastapi_rs_parity_workload_8ec188213588f06c.IndependentCoreConstructionError","exception_message":"independent core construction refused second","path":"/branch/item"}
```

Retry/repeat return 200 with `b'41'`; ordinary direct value returns 200 with `b'19'`. Both context endpoints return the identical declared-independent Response bodies and HTTP 409. Every new application-error selector is null (the refusal is publicly handled), and each action has the identical ordered start/body message types.

Reversible inspection of the final state journals verifies all 12 non-state raw send messages: each start has exactly `type,status,headers`, each body exactly `type,body`; original binary header tuples/order and body bytes match the canonical HTTP observations. No synthetic `more_body`, dropped warning/error, coercion, or normalization was added. State responses avoid recursively journaling their own send dictionaries; their exact status/headers/body and message types are selected independently.

## Legacy comparison limits and measurement boundaries

Across the full run, 475 selected HTTP body observations use exact base64 encoding and match byte-for-byte. Other observations have their declared scope. In particular, the two reissued OpenAPI controls select HTTP status plus parsed JSON pointers, without selecting HTTP headers/body. Their selected nested dictionary key order also happens to agree in these retained records, but the canonical comparison uses dictionary equality, which does not gate JSON-map key order, whitespace, unselected document sections, or full OpenAPI wire bytes. Passing those controls cannot supply the new lifecycle journal's byte-order guarantees or broader shared-schema/alias/title evidence.

These receipts establish the admitted 203-case selection and the repaired three-case lifecycle behavior. They do not establish full manifest support, positive hook-aware OpenAPI phase/shared-definition parity for the new metadata, mutable models/namespaces/status policies, private adapter-cache contents, concurrency/reentry, or coverage/performance gains. No old coverage reports or instrumented binaries were unioned into this normal audit. No application/factory import, product execution, build/install, parity rerun, active-file edit, or native-byte read occurred during the audit.

## Workflow inventory

Counts below are actual per-product completed inventories, not aggregate expectations.

| Workflow | Cases | ASGI actions | API probes | Explicit construction / errors |
| --- | ---: | ---: | ---: | ---: |
| dependency-cache-source-wave | 2 | 4 | 0 | 0 / 0 |
| dependency-context-manager-endpoint-modes | 2 | 4 | 0 | 0 / 0 |
| dependency-scope-websocket | 2 | 4 | 0 | 0 / 0 |
| dependency-scope-construction-errors | 2 | 0 | 0 | 2 / 2 |
| dependency-yield-lifo-endpoint-error-upstream | 1 | 2 | 0 | 1 / 0 |
| dependency-yield-tutorials-upstream | 4 | 8 | 0 | 0 / 0 |
| first-asgi-request | 12 | 12 | 0 | 0 / 0 |
| security-explicit-reinitialization | 16 | 128 | 0 | 16 / 0 |
| security-explicit-initializer-api | 2 | 0 | 11 | 0 / 0 |
| dependency-override-async-cache-request-local | 1 | 2 | 0 | 0 / 0 |
| dependency-override-async-endpoint-request-local | 2 | 2 | 0 | 0 / 0 |
| dependency-override-async-nested-query-wave | 1 | 2 | 0 | 1 / 0 |
| dependency-override-async-nested-two-required-query-wave | 2 | 8 | 0 | 2 / 0 |
| dependency-override-async-query-alias-cache-request-local | 1 | 2 | 0 | 0 / 0 |
| dependency-override-async-query-cache-request-local | 1 | 2 | 0 | 0 / 0 |
| dependency-override-async-query-validation-aggregation | 1 | 4 | 0 | 0 / 0 |
| dependency-override-async-two-keys-request-local | 1 | 2 | 0 | 0 / 0 |
| dependency-override-async-uncached-edges-request-local | 2 | 4 | 0 | 0 / 0 |
| dependency-override-cache-request-local | 1 | 2 | 0 | 0 / 0 |
| dependency-override-mixed-sync-async-direct-order-request-local | 1 | 2 | 0 | 0 / 0 |
| dependency-override-sync-defaults-upstream | 1 | 2 | 0 | 0 / 0 |
| dependency-overrides-required-subdependency-wave | 1 | 2 | 0 | 1 / 0 |
| security-full | 39 | 39 | 0 | 0 / 0 |
| depends-signature | 1 | 0 | 1 | 0 / 0 |
| security-declaration-api | 1 | 0 | 3 | 0 / 0 |
| security-declaration-asgi | 1 | 1 | 0 | 0 / 0 |
| root-alias-identity | 2 | 2 | 0 | 0 / 0 |
| core-ambiguous-params-construction-upstream | 4 | 0 | 0 | 4 / 4 |
| advanced_dependencies | 2 | 2 | 0 | 0 / 0 |
| dependency-tutorial-review-upstream | 11 | 15 | 0 | 0 / 0 |
| dependency-lifecycle | 5 | 9 | 0 | 0 / 0 |
| dependency-wave-callables | 5 | 8 | 0 | 0 / 0 |
| dependency-required-parameter-once-upstream | 3 | 3 | 0 | 0 / 0 |
| stringified-annotations-dependency-upstream | 1 | 1 | 0 | 0 / 0 |
| router-dependencies-isolated | 1 | 3 | 0 | 0 / 0 |
| websocket-router-dependency-slice | 2 | 2 | 0 | 2 / 0 |
| dependency-callable-classification | 23 | 54 | 0 | 23 / 0 |
| generator-awaitable-protocol | 15 | 47 | 0 | 15 / 0 |
| response-field-lifecycle | 16 | 61 | 0 | 16 / 1 |
| response-field-traversal | 7 | 42 | 0 | 7 / 0 |
| additional-response-model-openapi | 1 | 1 | 0 | 0 / 0 |
| path-operation-other-verbs-responses | 1 | 1 | 0 | 0 / 0 |
| additional-response-field-lifecycle | 3 | 15 | 0 | 3 / 0 |
