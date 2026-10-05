# Response-field immutable16: pre-native diagnostic audit

Read-only independent evidence audit, 2026-10-05. No apps, workers, builds,
installs or parity commands were executed during this audit. No repository,
metadata, recipe, expected-output or Rust file was changed. This note describes
retained actual observations from the completed diagnostic, not fixture results
to be replayed or a claim about a subsequently modified implementation.

## Receipt and identity checks

The canonical normal-run record is
`parity-results/response-field-wave/pre-field/normal-runs.json`. Its oracle,
target and comparison commands completed with exit codes 0, 0 and 1 respectively;
the comparison's exit 1 corresponds to ten parity failures.

| Artifact | Run ID | SHA256 |
| --- | --- | --- |
| Oracle | `c89a528f-0985-4963-856e-b48ce28a27d5` | `5ccbeedd7d899afdec9450f24192ba989ea7dc2770ab0ebd162338b3bd139c8f` |
| Target | `670d89a9-da85-4706-99fa-3cf49d950725` | `8dab389ccaeb6d013959da913f257e7bb677a7287a27734a263ed424853a9a37` |
| Comparison | `b80e49cc-64cf-4f7b-85c5-20737b3b84a6` | `639800f1e57245864b7666bc1449767b963c35fe2e00b4ca025441a7952a48e1` |

Artifacts are under `parity-results/oracle/`, `target/` and `comparisons/`, with
their run IDs as filenames. Both product results and the comparison validate
against their existing schema @9, report `completed`, and have empty
infrastructure-error lists. The normal-run product-error case lists are empty.
Oracle finish (10:00:43.801435 UTC), target start/finish
(10:00:45.976416/10:00:47.053547 UTC) and comparison creation
(10:00:49.392580 UTC) preserve source → target → compare ordering.

- Both products and the comparison bind manifest SHA256
  `d54cb021dd571b12256324409faf7cd2a21fa7fdcd865431bb44b337f7c7ca88`.
- Input SHA256 is
  `e38e3111c17c140732368053bcebff60b7fd65538ff98154d65c4562c0e5d92c`;
  workload is
  `a763538464f0e3a8809daa5fb55ba123a78b852d546170165a370e4f30682d68`;
  recipe is
  `2213314fc5a3bbc6100ad791e61bbe2c0bfd61deb11ee25358392e12a6b1cd6a`.
  Each matches the materialized index and current file bytes at audit time.
- Materialized index SHA256 at audit time is
  `29bca17097d92cfba9266b8c4ad35c8e12fd6c787efe6b256aa336be95f507b1`.
  Its 16 case IDs and case contracts match input/product/comparison order;
  every contract is parity, has nonempty requirement refs, and resolves to the
  corresponding index source mapping. Every product action order matches input.
- Initial and final source/build snapshots are byte-identical, SHA256
  `11f75bf623b0f6a225b02ce831a0a73ba436be1fe1b1aba2f8e25568777086e9`.
  Their input digest matches the receipt/index. Their combined source digest
  `ab7f0a7048d0bb438295cfc69daa74bd22b9751737e5ccdbc75b2f1ba56b6053`
  and combined native digest
  `3a119e2a97afe041e7c43f2912c0ee763c77cd20b1054c32aba8f6a57c80c95d`
  match the target identity. Per-module native hashes are FastAPI-RS
  `0de3ac9a9c81d9d40ca8c77567a4582acfa768c4b1aef0e427420e040e29a873`
  and Starlette-RS
  `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.
- Oracle reports FastAPI 0.141.1 commit
  `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 commit
  `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, CPython 3.12.13,
  Pydantic 2.13.4/core 2.46.4. Target reports FastAPI-RS HEAD
  `8014a5e45afd5b3f5197e52400b8490b5eb24c53`, pinned Starlette-RS
  `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`, matching shared runtime
  packages, and `fault_injection_compiled=false`. The source digest records
  working-tree/admitted-file state in addition to HEAD; HEAD alone is not the
  complete build identity.

## Counts and constructor observations

Comparison: **16 selected, 6 passed, 10 failed, 0 not-run cases**; all are normal
parity and there are no fault contracts. All 16 constructors/cases were observed.
The oracle completed all 61 HTTP actions. The target completed 49 actions and
recorded 12 `not_run` actions after three unexpected constructor errors, four
actions per affected case. Case-level zero not-run must not be reported as all
target HTTP actions executed.

The oracle's unsupported-type factory deliberately records a construction error
with no HTTP actions. The captured user schema-hook registration error is
different: user code catches ValueError and returns an app, so both outer
construction observations are `ok`; its nested user `setup_result` differs.
Neither is an infrastructure/product error. The target's three include keyword
binding errors are ordinary parity failures with actual constructor observations.

## First observed divergence for every failing case

`L` below abbreviates `fastapi.response-field-lifecycle.`; `P` abbreviates
`fastapi.response-class-provenance.`. JSON state was decoded only for this
explanation. The retained comparator still compares exact bytes/headers and
unchanged observations; no normalization was added.

| Failing case | First selected divergence | Retained actual source / old-target observation |
| --- | --- | --- |
| `Ldirect-annotated-reuse` | `read-state-before`, HTTP values | Source trace index 5 is `schema:build`, stage `app:register`, request 0; target index 5 is `setup:exit` for that stage. Source retains one setup build. Target later builds separately on requests 1 and 2. |
| `Lincluded-annotated-reuse` | `read-state-before`, HTTP values | Source trace index 7 builds at `router:register`; target exits that stage without building. Source's first state already records original-router plus two effective-context builds, the latter at `ready`, request 0. Target records none then, and later builds on each of three probe requests. |
| `Lfield-metadata-warning-error-recovery` | `read-state-before`, HTTP values | Source index 5 builds during `app:register`; target exits without building. Target later constructs on both probe requests and retains two `pydantic.warnings.UnsupportedFieldAttributeWarning` records about alias `unused_input`; source warning records stay empty. |
| `Lschema-hook-registration-error` | `read-state-after`, HTTP values | Source invokes the hook at setup and user capture retains `builtins.ValueError`, message `independent response schema rejected`, nested outcome `exception`. Target invokes no hook and nested setup outcome is `return` with null error fields. |
| `Lunsupported-model-construction-error` | Construction observation | Source outer outcome is `error`, class `fastapi.exceptions.FastAPIError`, full invalid-response-field hint shown below. Target outer outcome is `ok` with null error fields. |
| `Prouter-custom-default-model` | Construction observation | Source constructs successfully. Target raises `builtins.TypeError`: `FastAPI.include_router() got an unexpected keyword argument 'default_response_class'`. Its four HTTP actions are not run. |
| `Pinclude-custom-default-model` | Construction observation | Source constructs successfully. Target records the same exact include keyword TypeError; its four HTTP actions are not run. |
| `Proute-explicit-over-inherited-model` | Construction observation | Source constructs successfully. Target records the same exact include keyword TypeError; its four HTTP actions are not run. |
| `Pexplicit-none-over-default-model` | `invoke-first`, HTTP values | Source sends status 500, body `Internal Server Error`, and exposes `builtins.TypeError`, message `'NoneType' object is not callable`. Target sends status 200 with `x-response-provenance: app`, body `{"metric":7.0,"label":"naïve"}`, and no application error. |
| `Preturned-response-bypasses-model-and-none` | `read-state-before`, HTTP values | Source builds the declared field at setup; target exits registration without building. Both probe responses match, including returned-Response bypass. Source retains one schema build; target never constructs this bypassed field. |

Source unsupported-type construction message, copied from the actual receipt:

> Invalid args for response field! Hint: check that <class 'fastapi_rs_parity_workload_e38e3111c17c1407.UnsupportedReply'> is a valid Pydantic field type. If you are using a return type annotation that is not a valid Pydantic field (e.g. Union[Response, dict, None]) you can disable generating the response model from the type annotation with the path operation decorator parameter response_model=None. Read more: https://fastapi.tiangolo.com/tutorial/response-model/

The six passing cases are model-field aliases/output flags; omitted model NaN;
explicit JSONResponse model NaN; explicit custom class; application concrete
JSONResponse default model NaN; and inherited omitted defaults model NaN.
Passing observations do not independently prove adapter identity/lifetime for
those model-class cases.

## Boundaries

This is a completed old-target diagnostic. It establishes neither the new
helper's compile status nor post-change parity, full normal regression, coverage
or performance. Subsequent source changes need fresh receipts/build identities.
Constructor selectors observe outcome/class/message, not suppression flags,
traceback/frame fidelity or user introspection of `sys.exception`. Snapshot
digests and the worker's clean/pinned source checks bind the recorded run; the
audit did not re-import extensions, reproduce builds or rerun clean-tree checks.
Mutable metadata/model/warning state, concurrent traversal, V1 guard behavior,
streaming/additional fields and the seven inactive traversal drafts remain
outside this immutable16 evidence.
