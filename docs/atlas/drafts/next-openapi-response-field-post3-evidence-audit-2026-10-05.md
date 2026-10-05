# Closed NEXT OpenAPI post-change three-case audit

Date: 2026-10-05. Independent reviewer: `/root/dependency_records_runtime` (Sol).
Read-only actual JSON/schema/source-contract audit. No application, workload
import, native-byte read, builder, install, parity execution or active edit.

**Result:** the closed post-change slice has three successful constructions,
19 completed HTTP actions and 64 action observations on each side. Comparison
selects/passes three parity cases, with zero failed/not-run/fault cases and no
infrastructure errors. Entire ordered case payloads, container/scalar types and
values are equal across PRE source, POST source and POST target. This certifies
only this slice at the recorded normal build. The unclosed full 206 stage was
not inspected or certified by this audit.

## Actual receipt bindings

All paths below are relative to `/Users/lazytrot/work/fastapi-rs/`.

| Artifact | SHA256 |
| --- | --- |
| POST source `parity-results/oracle/61e9f9d2-6753-422f-891d-a08344c492f6.json` | `93b8efff2404a09e055e1d2bfab0a1f24ac9f44fa86c593b0e51955ae05bc0bc` |
| POST target `parity-results/target/e760c6c3-4b35-46eb-a01e-503be5b89a74.json` | `51c3d3d092c21b212b0839a6e4925d41ef3104e8756435be97cb871ac2ada000` |
| POST comparison `parity-results/comparisons/ae566774-971c-4f2f-884b-bb665f9dad44.json` | `7355680920b134e8215425100a9494321ba48566d5825ccf539e57eedaea5b00` |
| PRE source `parity-results/oracle/8a541cd1-51d9-4010-9c9b-8c10226e6725.json` | `2ded9223d83829243fae66724c5b9d855f73e1bb5bc8ac4ad5b3c1bd95a823b5` |
| PRE target `parity-results/target/9ef67d4e-800f-4995-a5da-bf85b3133f66.json` | `a7bea0b02e0de12f634bba0d7431a1a77d102db7a31428622b6d2c20ce3241e3` |
| PRE comparison `parity-results/comparisons/62d4a34a-70d0-4931-8f5f-a4e6ae8ae413.json` | `87c03a52cd7f41be03162da40df8cdda24018dea04dc09f8e178ef27f8671df9` |

POST comparison references the actual source/target paths, run IDs and SHA256
above; both result schemas and comparison schema@9 validate. All result status
and lane logs are completed/exit0. The PRE comparison preserves its closed
zero-pass/three-fail/zero-not-run diagnosis. Its source is unchanged public
evidence, not a stored expected-output replacement.

`post-change/normal-runs.json`, initial/final snapshots and individual lane logs
are complete under `parity-results/next-openapi-response-field-wave/`.
The three-lane orchestration log is directly under
`parity-results/next-openapi-response-field-post-orchestration.log`.

## Fixed identities

POST initial and final snapshot JSON are byte-identical, SHA256
`8da2b1f1eff7e45b545fd9adae643c24534f0ab23804c3503d700857e86580f4`.
Their recorded child digests recombine to the receipt identities using the
runner's sorted-name/NUL rule:

- Native revision: `1c66469c5b2eae6af709c52d4e7ae2bcf61d8aa8`.
- Combined source: `f4f1b382bae2cfd4d3cb3b0ef7f9aae8a7520fac33bd6c4f2a95cc1ac40d87b2`.
  FastAPI-RS tree `39967f7ec6f9e484005751af2a1e6750da00a8edc1f0728ca6e98fa98842bbf3`;
  sibling tree `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`.
- Combined normal binary: `a437662135f67157e37d984c9e6b6db42f011fdbe4479fc2bb00c2c835860356`.
  Recorded FastAPI SO `847bc07236baaa461b88ed4f29ddefe730ddf32de4610541d0b1f93d9a145184`;
  sibling SO `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.
- Target `fault_injection_compiled` is the JSON boolean `false`, not an
  instrumented build. The release builder log closes at 27.89s and records
  installation against immutable `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`.
- Source commits are FastAPI `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` and
  Starlette `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. Target sibling commit is
  `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.
- Source/target Python is CPython 3.12.13. Oracle packages exactly match the
  recorded profile; shared packages match target, including Pydantic 2.13.4 /
  core 2.46.4 and AnyIO 4.12.1. Target package identity does not report original
  FastAPI or Starlette as runtime distributions.

No current binary was read or assumed equal. These are recorded closed-stage
bindings; a later rebuild/instrumentation needs its own receipts and snapshots.

## Inputs, index and mappings

Recipe `next-openapi-response-fields.yaml` hashes
`e1243762e877e182bffadeb4eed6668d852bfb4d1bc31f8c98a7cceb9f8ce132`;
workload `next_openapi_response_fields.py` hashes
`d1c2824c616533127910a459075af4b020e6e97a8d9f260dd838d3b0ef7733bf`.
Canonical recipe materialization exactly equals active JSON, digest
`558a3d9cde89de0fd8342fe9a04deaef08a3caac836f5afd3a1b16d0c6829767`,
bound by all PRE/POST receipts and both snapshot pairs.

Manifest digest is `eba84432c34ad05b8b0613d2d9a285443d100357d189bd7583c935cac9758859`;
index digest `239cc81b7d8fec4b8d5995f6bbbd786dc3bfe4ccf25a8855b0887850922092a6`;
metadata digest `24e916145a0174644a48295b6065d28569325267e1db3fc44495e4fbe1989ef1`.
Index schema@5 and canonical recipe/workflow@9 validate. Case contracts match
their source-evidence requirement references. Nineteen reviewed fixture links
bind seven existing operations: constructor, exception_handler, Request,
JSONResponse, application invocation, openapi and get. No classification or
private API is promoted by these links or this audit.

The CLI commands contain the whole input with no case/subset/verification skip
or normalization flags. Source and target results contain every planned case,
action and observation in order, matching kinds, indices and selectors. The
post helper SHA256 `01870def07aaa01d381cbd0d565cb93a298471929a6ffb979ad2ddcb261ce2e2`
differs from reviewed PRE helper `86b309b61b3983281b233c0660c2731c43b44cdc7ed3245f5cb8d4ac15e2d048`
only in the output path. It launches live isolated oracle/target workers and
compares their actual artifacts. Nothing dispatches on expected observations.

## Actual selected public behavior

- **Flat Annotated metadata:** construction has four extra core callbacks
  then one primary callback, each once, before any JSON hook. First docs call
  makes the two ordered serialization-mode passes, primary then extras:
  ten JSON calls total. Cached docs adds none. Warning journal counts are
  five initially and fifteen after generation, stable after cache reuse.
  Both document bodies are 1378 bytes and byte-equal. Primary and extra schema
  order is `type,title,x-independent-probe`; source summary and owner titles
  match exactly. These are generated outer-name titles; inner Field inputs
  do not prove nondefault outer alias/title branches.
- **Shared primitive reference:** retained core count is three before/after
  document generation. Actual JSON hook count is six, not one-call dedup.
  Ordered passes, all warnings and reference sibling extensions match. One
  `SharedReading` definition appears; docs/cache bodies are 865 bytes and equal.
  Three initial/nine final warnings remain unchanged on cache hit.
- **Late JSON hook refusal:** ordinary public handler returns actual 409 with
  exact class/message/path, ordered headers and 181-byte body. Failed generation
  reaches primary/first-extra/late-extra once, then records refusal. Successful
  public retry adds two ordered passes (totals three each), returns 875 bytes,
  and reuses retained core counts. Public successful-document identity values
  are `[null,true]`; later docs cache adds no hooks/warnings. Complete warnings
  increase three→six→twelve and stay twelve. Handled error and raw sends remain
  in later state bodies; runner application exceptions are absent as expected
  from the actual handled response, not hidden by observation reduction.

All 19 raw HTTP bodies and ordered headers match, including every state response.
The decoded states retain complete ordered hook/error/warning/send journals,
all raw send fields, bytes and header/container representations. Sixteen final
earlier raw sends across the three state journals are preserved (4+4+8).
Every public whole-document observation is also present. Ordered deep equality
checks dictionaries, list positions and exact scalar types, beyond ordinary
map equality. Compact ordered entire-case payload digest is
`5fd1c66e3b5d4e9810ff13d9b33ebf55a64a5ce623c5ea591ba949b579aae749`
for PRE source, POST source and POST target.

Detailed hashes, action body lengths/digests, case-state summaries and bindings:
`/private/tmp/fastapi-rs-next-openapi-post3-evidence-audit-2026-10-05.json`, SHA256
`17df9d78b9af3fbc05302d2701d6be6def91f7bb1b6a421bcddb95dbd60873c7`.

No missing/case-order/input/identity/schema/evidence blocker was found for this
closed three-case stage. Broader OpenAPI model validation/union/Any fallback,
422 ordering, outer aliases/modes, flattening/mixed schemas and mutable/reentrant
history remain unproved here. The separate full 206 regression gate must close
and be audited before a complete selected-suite claim.
