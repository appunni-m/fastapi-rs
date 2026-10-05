# Next OpenAPI response fields: independent pre-change evidence audit

2026-10-05. Read-only audit of the closed canonical diagnostic. Only this temporary
note was written. No app/factory/native module was imported, no binary bytes were
read, and no builder, installer, parity command, unit test or comparator rerun
was executed. All descriptions below come from retained actual records; no
expected output was added to the inputs.

## Closed inventory and immutable receipts

The helper retained exit codes **oracle 0 / target 0 / compare 1**. Both products
completed **three independent constructions and 19 HTTP actions**, with all
construction outcomes `ok`, zero construction/product/infrastructure errors and
exact input case/action order. Comparison is completed ordinary parity:
**3 selected / 0 passed / 3 failed / 0 not_run; 0 fault-contract cases**.

| Receipt | Run ID | SHA256 |
| --- | --- | --- |
| Oracle | 8a541cd1-51d9-4010-9c9b-8c10226e6725 | 2ded9223d83829243fae66724c5b9d855f73e1bb5bc8ac4ad5b3c1bd95a823b5 |
| Target | 9ef67d4e-800f-4995-a5da-bf85b3133f66 | a7bea0b02e0de12f634bba0d7431a1a77d102db7a31428622b6d2c20ce3241e3 |
| Comparison | 62d4a34a-70d0-4931-8f5f-a4e6ae8ae413 | 87c03a52cd7f41be03162da40df8cdda24018dea04dc09f8e178ef27f8671df9 |

Files are under `parity-results/oracle/`, `target/` and `comparisons/` using those
UUID filenames. The comparator's source/target artifact references bind both
actual file hashes and run IDs. Its 22 retained differences are exactly the
unequal actual observation values at the recorded action/index paths: **6 / 6 /
10** differences across the three cases. No unretained selected mismatch was
found, and no recorded difference substitutes a prescribed value.

There are **64 action observations per product**: 19 exact HTTP values, 19 ASGI
message-type sequences, 19 application-error observations and seven whole
OpenAPI document observations. All 19 message-type sequences and application
errors match. Fifteen HTTP values and all seven document values differ. The
three construction projections are equal independently of those action totals.

The four workflow/result/comparison documents and the materialized index passed
their five local schema validations, including format checks. Source completion
precedes target start; target completion precedes comparison creation. The three
stage logs parse to the same command results retained in `normal-runs.json`.

| Closed orchestration artifact | SHA256 |
| --- | --- |
| pre-change/normal-runs.json | bfc5e405a4c3cd140079358e0790415268bddb2cd427bdf98f1d665d36c449c8 |
| initial-source-build-snapshot.json | 96b0c0061d369b249c7eaf2c64bb166797f45898ee31976434786cbafcc68cfd |
| final-source-build-snapshot.json | 96b0c0061d369b249c7eaf2c64bb166797f45898ee31976434786cbafcc68cfd |
| next-openapi-response-field-pre-orchestration.log | 584214940e158946eaa0767432275e17c8d139667b1e4086c3c4e9d4f72e09f0 |

The first three entries are under
`parity-results/next-openapi-response-field-wave/pre-change/`; the orchestration
log is directly under `parity-results/`.

## Fixed input, identities and source reconstruction

Input `558a3d9cde89de0fd8342fe9a04deaef08a3caac836f5afd3a1b16d0c6829767`,
recipe `e1243762e877e182bffadeb4eed6668d852bfb4d1bc31f8c98a7cceb9f8ce132`,
and workload `d1c2824c616533127910a459075af4b020e6e97a8d9f260dd838d3b0ef7733bf`
match the indexed files. The parsed recipe equals the materialized input. All
three products/comparison bind the same manifest SHA256
`eba84432c34ad05b8b0613d2d9a285443d100357d189bd7583c935cac9758859`.

The index SHA256 is
`239cc81b7d8fec4b8d5995f6bbbd786dc3bfe4ccf25a8855b0887850922092a6`.
Its ordered contracts have 4 / 4 / 5 requirement references, all resolving to
declared source evidence. These 13 case links equal the five partial source
mappings for this workflow; the handling-errors mapping applies only to retry.
Atlas SHA256 is
`51046e82a98daa711e8fdffa5d4c187e348ed4622abf6c93cc103d386baee767`.
These are input/source coverage bindings, not LLVM region measurements or
accepted coverage gains.

The generated manifest contains exactly 19 new operation fixture links on the
seven previously reviewed operations. Request appears only on retry. The existing
generator nevertheless attaches the full case selector set to each operation
link; the narrower reviewed Request status/body scope remains the claim boundary.
Active metadata SHA256 is `24e916145a0174644a48295b6065d28569325267e1db3fc44495e4fbe1989ef1`.

Both initial/final snapshots are byte-identical, and recombining their component
digests reproduces the target identity:

| Captured quantity | SHA256 |
| --- | --- |
| FastAPI-RS source tree | 1c9b4a24cf64949bc23761e678c3b87ef1d2d7abba3b5f5e3e9477ae1e8e794e |
| Starlette-RS source tree | 37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55 |
| Combined source | 5c403a8d64c087b0935be2e4ffad28ec9aec3e850139f0ddf753ad311056f39a |
| Installed FastAPI-RS core | 5eeae03b977c74fed3808df9194bef0d23527a8208b2c05c92f9415084b7a244 |
| Installed sibling core | fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5 |
| Combined native pair | 8e1888dbe104c3bdf69f63b47bb0e9ded4a3ba9cc70d2c04676890134501f6ed |

Git reconstruction of all 1,404 tracked files at measured revision
`bbac9b5e16aace4a29bfd2521ba623eb4f2b55fe` independently reproduces the captured
FastAPI-RS source-tree digest. Native Rust and facade trees are unchanged from
`827612f`. This reconstruction reads Git source blobs, not installed extensions.
The binary values above are captured receipt facts, not a claim about files after
future installation or source changes.

Oracle identity is FastAPI 0.141.1 commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`,
sole Starlette 1.6.0 commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and
CPython 3.12.13. Target records measured bbac9b5 and sibling
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Shared package versions match the
manifest, including Pydantic 2.13.4 / pydantic-core 2.46.4. Fault identity is
oracle N/A (`null`) and target `false`. The target command explicitly selects the
pinned sibling path. The earlier helper review remains the record of the inherited
environment requirement; the receipts do not independently record every parent
environment variable.

## Earliest divergences and observed control flow

All three first `/state` HTTP projections are byte-equal. They retain equal
attachment-time core hooks, no setup-time JSON hooks and equal setup warnings.
This diagnostic therefore does not show the old premature attachment-phase gap.

### 1. annotated-metadata-outer-titles-retained-hooks

First selected difference: `docs-first-document`, exact HTTP value and whole
OpenAPI document. Both status codes are 200; document lengths are 1,378 versus
1,354 bytes. The source summary is `Independent Probe`, target `Probe`. Source
primary title is `Response Independent Probe Operation`, target
`Response Probe Probe Get`. Those are the two parsed differing document values.
Source primary schema keys are `type,title,x-independent-probe`; target primary
keys are `type,x-independent-probe,title`. Additional field titles/values match
in this case; inner Field variants do not prove explicit outer alias/title policy.

The following state identifies the earlier callback cause: target logs another
primary core hook before its first JSON hook; source starts directly with the
retained primary JSON hook. Source JSON order visits primary then all four extras
for pass 1, then the same five for pass 2. Target completes both passes per field
before advancing to the next. Each field's JSON total is two on both sides, but
the ordered journal differs. Final primary core count is 1 versus 2; warning
counts are 15 versus 16. Cached docs add no hooks/warnings and return each
product's same document bytes. Comparator retains six diffs.

### 2. shared-primitive-definition

First selected difference: `docs-first-document`. Both status codes are 200;
document lengths are 865 versus 661 bytes. Summary differs as above. Source's
200, 409 and 202 schemas contain `$ref` plus the `x-independent-probe` sibling;
target keeps only `$ref`. Both documents retain the same `SharedReading` integer
component, so this is not a missing component or dangling-reference observation.

Source and target both invoke the shared JSON hook **six times**. The same label
is used for all three fields, so that count alone cannot identify per-field batch
ordering or establish one-call deduplication. The journal instead positively
observes target's extra primary core callback: shared core count 3 versus 4;
warning count 9 versus 10. Cached docs invoke no additional callbacks. Comparator
retains six diffs. Batch/ref/title handling is the source-backed diagnosis; the
actual extension loss and core callback are the selected evidence.

### 3. late-json-hook-error-public-retry-cache

The first docs refusal itself matches exactly: status 409, full body bytes and
ordered headers (`x-independent-error: json-schema`, content-length 181,
content-type application/json). Both actual handler bodies record:

- Class: `fastapi_rs_parity_workload_558a3d9cde89de0f.IndependentJsonSchemaError`
- Message: `independent JSON schema refusal: late-extra`
- Path: `/openapi.json`

First selected difference is the next state, `state-after-json-hook-refusal`.
Source attempted JSON hooks once each in primary/first-extra/late-extra order.
Target first rebuilt primary core, then attempted primary twice and first-extra
twice before late-extra's first hook refused. Source counts after refusal are
1/1/1; target 2/2/1. Warnings are 6 versus 9 including setup.

Public `/document` retry succeeds on both sides. Source keeps primary core count
1 and completes two whole-field passes; target rebuilds it again to count 3 and
pairs passes per field. Final JSON totals are source 3/3/3 versus target 4/4/3;
warnings 12 versus 16. Successful document values/body order still differ in
summary/primary title as in case 1 (875 versus 851 bytes).

The public document-result identity relation is `[null,true]` on both sides.
The second public call and final docs request add no core/JSON hooks or warnings
and return each product's same successful bytes. Thus handled error propagation,
ordinary retry and these public cache-hit observations agree; the hook ordering/
reconstruction and generated document observations do not. No private cache or
adapter identity was read. Comparator retains ten diffs.

## Warnings, raw sends and evidence limits

Final journals retain 36 source versus 42 target warnings, all actual
`builtins.UserWarning` category/message records in occurrence order. Totals are
11/25 source core/JSON hooks versus 15/27 target hooks. No warning was filtered
or normalized in this audit; warning filenames/tracebacks are outside the input's
projection.

Each product's final journals contain 16 lossless send messages for eight
non-state requests. Every byte payload and ordered tuple header pair binds back
to the corresponding selected HTTP observation. All starts have exactly
`type,status,headers`; bodies exactly `type,body`, without an invented more_body
field. The refusal's two complete raw send records are equal. State requests
are not recursively journaled but all 11 state HTTP projections remain directly
selected. Every application-error observation is null and neither journal has
an unhandled `request:raised` record.

Parsed OpenAPI observations compare mapping values and do not by themselves
establish object-key byte order. Exact HTTP bodies and the lossless send journal
retain that order separately. The seven successful document mismatches include
actual value differences; a key-order normalization could not repair them and
none was introduced. Cache agreement does not imply document or hook parity.

No receipt integrity blocker was found. These negative pre-change receipts
establish only the three immutable primitive direct-route inputs: generated
outer titles despite inner metadata, scalar ref extension preservation, and one
ordinary user JSON-hook refusal/retry. They do not establish general nested
models, input/output mode combinations, arbitrary alias/title metadata, included
contexts, custom generator history, concurrent/reentrant behavior, full OpenAPI
model validation or LLVM coverage. Fresh post-change execution remains necessary.
