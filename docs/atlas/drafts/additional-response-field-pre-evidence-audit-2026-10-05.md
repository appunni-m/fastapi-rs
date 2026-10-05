# Additional response-field lifecycle: closed pre-change evidence audit

Date: 2026-10-05. Independent, read-only review of retained actual records. This note binds the admission revision `6da823585dbe4605ff1e04204eee287813eb34e8` and the closed pre-change run; it makes no claim about subsequently edited source or installed native modules.

## Result and admission

No receipt, inventory, schema, or identity blocker was found. Both products completed all three constructors and all 15 ordered HTTP actions. The canonical comparison reports **0 passed / 3 failed / 0 not run**, all ordinary parity cases; the fault-contract selection is zero. These are observable product differences, with no infrastructure failure or unhandled application error.

| Case suffix under `fastapi.additional-response-field-lifecycle.` | Actions per product | Exact differing observations |
| --- | ---: | ---: |
| `saved-decorator-attachment` | 3 | 2 |
| `shared-router-two-contexts` | 5 | 3 |
| `second-additional-hook-retry` | 7 | 5 |

All construction observations are `ok`, with null error class/message. Every case/action status is completed; both infrastructure-error inventories are empty. Each product contains the full admitted three-case inventory, in order, and 45 indexed action observations (three per action), plus three construction observations. Public application-error selectors are null for every action; the source refusal described below is handled by the public exception handler.

The stored workflow, source result, target result, and comparison validate against the committed revision's schema-9 JSON schemas, including format validation. The materialized workflow equals the safe-loaded committed recipe. The committed index has one matching workflow row, with exact recipe/workload/input hashes, case order, and three parity contracts; each has nonempty required API references (3, 5, and 5). The oracle identity agrees with the committed manifest's source profile and the target identity with its sibling profile. No expected outputs, selectors, observations, comparator, or receipts were changed during this audit.

The complete comparator difference set was independently recomputed from the stored selected observations: all ten unequal observation values are reported, in action order, with comparison `exact`; there are no omitted or spurious differences. All ten paths are `observations[0].values`, the selected HTTP status/ordered headers/exact body. Application-error and message-type observations agree throughout.

## Receipts and frozen bindings

Receipt directory: `/Users/lazytrot/work/fastapi-rs/parity-results/additional-response-field-wave/pre-change/`.

| Artifact | Run ID / timestamp | SHA-256 |
| --- | --- | --- |
| `normal-runs.json` | One additional-response-field workflow; oracle/target exit 0, comparison exit 1 | `8d0a285d5f29ece8571d92aa0dd571b3569092e6286aa25b4ddfd81ebbcc6c26` |
| Oracle actual record | `97502d42-fdca-49f0-aaaa-0f0578b24a7d`; 11:44:35.308161–11:44:35.507722 UTC | `12e9c028676bf0210380ff140a0092a6b24437d5aa234a7a901f284d1d0fd95a` |
| Target actual record | `66c56b22-fa48-4366-bc89-8d65a24e6700`; 11:44:37.935166–11:44:38.533409 UTC | `6bb0bf170d1120539512bf281f236c8b1daefbeca6baf4cd985e44d56506d7a3` |
| Comparison actual record | `8b2b48eb-5795-4cdc-ac1d-e21f6cd6c3e3`; created 11:44:40.739022 UTC | `cc691e33020a126578cd146d52c1107fc374890d981067eda0fe0f29f07be5d3` |
| Initial and final source/build snapshots | Identical JSON and bytes | `f264f4b5ce9bbe88e6fea90fcd11242fe28db6711fb6d6add299c3dcfaa7b1ef` |

The results are stored under `parity-results/oracle/`, `target/`, and `comparisons/` with the listed IDs. Their referenced manifest, input, workload, result IDs, and byte hashes agree with the receipt and CLI logs. Source execution finished before target execution began; target finished before comparison creation. Log hashes are:

- Oracle: `d8b7e1c7f04f6f19831a0bfae9a226ccd1ddaa705bc758eaf59f090b79925298`.
- Target: `c9b24b5b2f0cc1588db6dbd1afc5d90d0be5178b318af429dad48c64626103fe`.
- Comparison: `bf064b1833dc6a58f72f132d9e536281ab638e2f18db9b329d0a97d27d80ba49`.

### Committed input/contract hashes

- Materialized `tests/fixtures/inputs/parity/additional-response-field-lifecycle.json`: `8ec188213588f06c8a107941f442f8f9bf69020828ae42626238f247c4944190`.
- Recipe: `199ab0b81d4b1e923933a13f076c49bb89229add1e0c90ce441902c0c5db7ae1`.
- Workload: `ef756492903a719a8b3522bc1971794663083bcbb55ed20076b74f988d0e8025`.
- Index: `517719a589e8199d64fdf5f99aabe864f8a0e954e22540bc6f40b2e4581c631f`.
- Manifest: `ae88fc58d1ead1a70cf3b9435c470b16794a03f050f368eb0e68f7c4457cc697`.
- Workflow-v9 schema: `0ebba2ad03340ac494313a0357e855d07867cb6a4c9f6436948a1dbb684c9513`.
- Result-v9 schema: `3e6baca18ce16c5ffd894b8457d40858f44d67e138d418b8ad507fe9ebc60d67`.
- Comparison-v9 schema: `bcbd65c70fc012fb29826d14b53871600a353599d72eae63e82063b955d8ef8d`.

### Source and binary identities captured during execution

The pinned oracle is FastAPI 0.141.1, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, and Starlette 1.6.0, commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. Target sibling is `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`, commit `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Both products report CPython 3.12.13, Pydantic 2.13.4 / pydantic-core 2.46.4, and AnyIO 4.12.1. Target package evidence excludes original FastAPI/Starlette runtime dependencies and reports `fault_injection_compiled=false`.

| Captured component | SHA-256 |
| --- | --- |
| FastAPI-RS source | `ef6955df722dc04fe2747de5fec7631b0c48ca80b45e9610d58fdb142f7f7a6c` |
| Starlette-RS source | `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55` |
| Combined source | `d3080c3ae92691af9a9973f34354c0066d58c07d3326c24d11bec1ed727ed63c` |
| Old normal FastAPI native core | `6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e` |
| Sibling native core | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Combined native pair | `10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73` |

Initial/final snapshots and target result identity agree on these bindings. Independent reconstruction from immutable Git blobs at the stated revisions used the canonical sorted-path/file-kind/content framing: all 1,388 FastAPI-RS and 314 sibling entries reproduce the component source hashes exactly; the combined source and native-pair digest calculations also agree. Native hashes were read from captured records only. No current installed native bytes were read, and this audit does not assert current-tree or current-binary equality after the pre-change gate.

## Exact selected first differences and later evidence

For all three cases, the first unequal selected observation is the initial public state response, at `observations[0].values`. Both initial responses have status 200 and `application/json`; their actual state bodies and content lengths differ. Reversible decoding of retained bodies reveals the following earliest trace entries (zero-based indexes); no decoding was introduced into the comparator.

| Case | First action / trace index | Source entry | Target entry | Initial content length, source / target |
| --- | --- | --- | --- | --- |
| Saved decorator | `read-state-after-attachment` / 7 | `setup:exit`, stage `decorator:direct:create`, request 0 | `schema:core`, same create stage, label `extra`, call 1, annotation `int` | 1569 / 1900 |
| Two contexts | `read-state-before-visiting-contexts` / 9 | `setup:exit`, stage `decorator:shared:create`, request 0 | `schema:core`, same create stage, label `extra`, call 1, annotation `int` | 1892 / 2223 |
| Second extra retry | `read-state-after-arming-hook` / 9 | `setup:exit`, stage `decorator:branch:create`, request 0 | `schema:core`, same create stage, label `first`, call 1, annotation `int` | 2264 / 2930 |

### Saved decorator attachment

Source executes extra then primary core hooks at decorator attachment, with counts `{extra:1, primary:1}`. Target executes the extra core hook during decorator creation, followed by two extra JSON hooks there (`mode=serialization`, `core_type=function-after`), then executes primary core at attachment. Source JSON-hook inventory stays empty. The exact `builtins.UserWarning` message `independent extra core schema warning` is the same but its selected stage is attachment in source and creation in target.

`request-primary-value` agrees exactly: HTTP 200, body bytes `b'19'`, ordered headers `content-length: 2` then `content-type: application/json`. Both log one endpoint call and primary validation/serialization of integer 19. The final state remains unequal because the construction and premature JSON history differs. Both comparator differences are state responses.

### Same router in two contexts

Source extra/primary core counts progress `{1,1}` at direct attachment, `{2,2}` after the left context, and `{3,3}` after the right context. Target progresses `{1,1}`, `{1,2}`, `{1,3}`: primary construction follows the visited contexts, but extra construction is missing in both. Source JSON inventory remains empty; target retains its two premature extra JSON callbacks. Warning inventories are empty on both products.

Both actual endpoint responses agree exactly and bypass primary response validation/serialization because the endpoint returns a Response. They are HTTP 409, with ordered headers `x-lifecycle-stimulus: shared`, `content-length`, and `content-type: application/json`:

- Left length 103, body bytes `b'{"label":"shared","path":"/left/item","value":"29","outside_declared_integer":["independent response"]}'`.
- Right length 104, body bytes `b'{"label":"shared","path":"/right/item","value":"31","outside_declared_integer":["independent response"]}'`.

The three differences are the before/after public state responses, which retain every hook event and both endpoint calls.

### Second additional field refusal and retry

Setup attaches two extras in insertion order **409 then 202**, then primary. Source setup core counts are `{first:1, second:1, primary:1}`, with no JSON callbacks. Target constructs first and second during decorator creation and calls each JSON hook twice there; primary is constructed at attachment. Both products arm one second-extra refusal only after setup.

On the first branch request, source reconstructs first (call 2), then second (call 2), whose ordinary user core hook refuses. Primary remains at call 1 and the endpoint has not run. The public handler returns HTTP 409, ordered `content-length: 187`, `content-type: application/json`, and these exact body bytes:

```text
{"exception_class":"fastapi_rs_parity_workload_8ec188213588f06c.IndependentCoreConstructionError","exception_message":"independent core construction refused second","path":"/branch/item"}
```

The fully qualified class is the actual shared workload-loader module name; it is not normalized. Target does not reconstruct either extra, constructs primary call 2, runs the endpoint, and returns HTTP 200 with `b'41'` and length 2. Its refusal remains armed. Both application-error selectors remain null: source records a handled user error, not a construction/admission failure or unhandled ASGI exception.

On retry, source repeats first and second construction (calls 3/3), then constructs primary call 2 and invokes the endpoint once. A further repeat performs no new core construction and invokes the endpoint a second time. Target extra counts remain 1/1, primary 2, endpoint counts become 2 then 3, and the unused refusal remains 1. Both retry and repeat HTTP responses agree exactly (200, `b'41'`). Source's visible repeated first hook after failure and lack of reconstruction after success establish the selected branch retry/retention behavior; no private cache field was inspected.

Source warnings are six ordered `builtins.UserWarning` entries: first/second at attachment, first/second during the refused request, and first/second during retry. Target has only the two creation warnings. Messages are untouched: `independent first core schema warning` and `independent second core schema warning`. Source JSON inventory stays empty; target remains `{first:2, second:2}`. All four state responses and the first branch response differ (five comparator differences).

## Lossless send/error coverage and limits

All 15 actions on each product select exact HTTP status, ordered binary headers, exact body, application error, and ordered message types. Every action emits `http.response.start` then `http.response.body`. The public state journal also retains all six non-state endpoint requests per product: 12 full send messages, reversibly representing byte and tuple values. The audited start dictionaries contain exactly `type`, `status`, `headers` in that order; body dictionaries exactly `type`, `body`. Header bytes/order and body bytes agree with the selected canonical HTTP observations, including the source refusal versus target success. No `more_body` or other synthetic defaults were inserted for inspection.

State responses intentionally do not recursively journal their own full send dictionaries; their HTTP body/headers/status and message types remain selected. These records establish premature target core/JSON callbacks, absent per-context extra construction, and absent armed refusal/retry. They do not establish positive OpenAPI schema generation, serialization-mode definitions/title/alias handling, additional-field dependency-analysis hook ordering, private adapter-cache contents, model/namespace mutation, concurrency/reentry, or fault-injection cleanup. No yielded resource is entered before the selected construction refusal. The existing two OpenAPI pre-repair controls are separate receipts and are not counted or unioned here.

This audit used only stored JSON/recipe/schema/log data and immutable Git objects. No application or workload import, product execution, parity rerun, build/install, active-file edit, or current-native-byte read occurred.
