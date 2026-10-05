# Closed automatic validation-response POST4 audit

2026-10-05, independent read-only audit of
`parity-results/openapi-validation-response-wave/post-change-v2/`. The parent
closed this stage with exit 0 before the audit. Source, target and comparison
CLI commands each returned 0; comparison selected four ordinary cases, all four
passed, with no failed/unrun case or fault case. No application, native module,
builder or unit framework was executed by the reviewer. Active files and the
ongoing broader regression/public-control stages were not changed or audited.

## Exact bindings and completion

| Artifact | Run ID / SHA256 |
|---|---|
| Oracle | `8f12eedc-87fe-400b-8d91-5f08190a59b5` / `06ed312bb850f73ccd840e4095dbd1a47ea9c4e7ad446eb520a611a8a714af16` |
| Target | `014770d3-7655-4509-98a7-760ce646c244` / `d3224e7d97a6ed055f598c31a95b903356e43d1aa2c6208e30b4ccf87274daed` |
| Comparison | `881b8d1c-38f6-405b-9a1c-57e3c5698204` / `9b80c58b0ee11755c0edfb3bed2e1fc2c67d04a34c3e1636767004ecf863327b` |
| Materialized input | `0ef0311b4fc9930eb2faeb442bc28742f0f3d3bd0a0f6bae753dd684ed7b2dc9` |
| Workload | `9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130` |
| Recipe | `4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334` |
| Manifest | `919fa17dfa66c4a32c57fe7230e214f2c05861e4100ff69a768a72747400bfc2` |
| Materialized index | `0490d2e3366bad2ffa941e5994da07f2a0ea4a8f8c7f0d6c919044e0caf20f68` |

Workflow, source/target results, comparison and materialized index pass
independent Draft202012 validation against their schema-9/index-v5 schemas.
The index row binds the same recipe, workload and input hashes. All four case
IDs, six action IDs/order per case, construction selectors and observation
kind/index inventories match. Six partial source mappings and their required
documentation/test references remain unchanged. Comparison result references
match actual result-file bytes/run IDs, and both lane bindings match the input,
workload and manifest files. No infrastructure errors are present.

Both lanes have four successful construction observations, 24 completed GET
actions and all 80 selected action observations. Every declared warning phase
was reached: four constructors plus 24 actions, with all 28 warning lists empty
in each lane. There are no product errors, constructor errors or unrun actions.
Empty warnings establish no warning-filter branch coverage.

Initial/final snapshot bytes agree, SHA256
`1639d6e90f3c802b044557d83b14c668186d4bb46e714c4dcea4455a83f36a58`.
Recorded root tree is `3007be0eb5c51a8bbe60d3328a62095cb1bb9bd0f8bd012d1e1a8567153fa735`,
sibling tree `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`,
combined `d1299254a34d2c31b0a8ed1b676825a85b749421aa27a9e8084e5c6afecbf8f7`.
Target identity matches that combined tree and revision
`d50887853d382bd9d9e03c7e82a504614ff02aba`. Recorded normal core is
`05fd14200682372037e867108b52f6f44993fb39961fdac03ed626f45b26a3e3`,
sibling `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`,
pair `e1b2a3599081a307941e07b2a00f71edf9cf55d2d00f9185f48416843722086e`.
Target identity binds that pair and has fault flag false; oracle flag is N/A.
Oracle CPython 3.12.13/FastAPI 0.141.1/Starlette 1.6.0/Pydantic 2.13.4/core 2.46.4
and source revisions agree with PRE. Oracle finished before target started.
No current native bytes were read; module path checks remain canonical worker
invariants rather than separate module-path fields in these result identities.

## Lossless observed equality and source stability

Source/target entire case observations compare equal recursively with explicit
type checks, dictionary key order and array order. All 24 HTTP status/ordered
header/raw-body selections agree, as do ASGI message types, application-error
observations and full warning sidecars. Both document actions in each case also
have byte-identical complete bodies and ordered, typed parsed documents:

| Case suffix under `fastapi.openapi-validation-response.` | Actual response key order | Document bytes | Actual component schema names |
|---|---|---:|---|
| `automatic-after-declared-responses` | `200,409,202,422` | 1256 | `HTTPValidationError,ValidationError` |
| `declared-422-suppresses-automatic` | `200,409,422,202` | 611 | None; components absent |
| `declared-4xx-suppresses-automatic` | `200,409,4XX,202` | 610 | None; components absent |
| `declared-default-suppresses-automatic` | `200,409,default,202` | 612 | None; components absent |

The two document actions have the same bytes within each lane as well. The
four final state bodies/journals match exactly, including the complete prior
40 lossless raw-send records, setup/attachment stages and public document status,
component and top-level key order. Only the valid required-query request reaches
the endpoint in each case; actual valid/missing/malformed statuses are 200/422/422
in both lanes, with equal raw validation response bytes. Documentation
suppression therefore does not replace the selected default validation behavior.

All ordered/typed case observations from PRE oracle
`e83b394b-ffce-47eb-a0ce-b8c10c2718ac` remain exactly unchanged, together with its
identity/input/workload/manifest bindings. This includes complete raw bodies,
journals and empty warning lists, not just structural document values. Public
repeated document equality observes the cache path without asserting private
cache state or object identity. The PRE target failures remain preserved as
historical evidence; their unrun actions are not retroactively counted.

## Preserved infrastructure attempts

The first POST and public-control folders are separate closed failed bootstrap
attempts. Their initial/final snapshots agree. Retained source result records
validate against schema 9 or API-result schema 4 and match declared case/action
or probe order and input/workload/manifest hashes:

| Failed-attempt source run | Retained source completion | Source artifact SHA256 |
|---|---|---|
| `d0395bb9-66ef-4aa7-9cda-2e75d3233e1e` | Four POST constructors, 24 actions; ordered/typed cases also equal POST v2 and PRE | `6ad98c108e48144c0d8fa41cd7ddce2f53b4508c938e40716f037e90cd8ff3b5` |
| `b544243c-9268-41b2-8676-e8fbd7490fe2` | Two direct public API cases/two probes | `f6c7e9fe140cad7d7009876013fada863a9a100cebe86c7f139e1075828af773` |
| `082fbbeb-5395-4b84-a093-6b69fa50c354` | Two direct single-route API cases/two probes | `2048de6452d706dbbaa33da2a00b559b0b74ac98123a2eab35f9753c4d17e5db` |

All three corresponding target CLI attempts exit 2 with the retained
`cannot resolve target Cargo dependencies`/sccache `Operation not permitted`
message. No target result artifact or comparison artifact exists in their
receipts. Static worker ordering resolves Cargo linkage before importing public
or native target modules (`target_worker.py:343-477`), and before workload loading;
these are infrastructure failures, not product/parity or fault outcomes. The
helpers then report a missing target identity because no target receipt exists;
that secondary message is not evidence of a changed source/native pair. The
corrected POST helper differs from the first helper only in output directory;
parent separately reports clearing inherited `RUSTC_WRAPPER` for the rerun.

## Frozen audit artifacts and scope

The POST v2 helper is
`9abe3598bb7610463f4d20b5fc4dcf4d7c055ab3458092266e371287626a2c98`.
Read-only checker `/private/tmp/fastapi-rs-openapi-validation-response-post-audit.py`
is SHA256 `53fae896b0cbd8e9a6144cf408c1bfdf9dd92f1638beb7a1d5e57315f375b95d`.
Derived JSON `/private/tmp/fastapi-rs-openapi-validation-response-post-audit.json`
is `cba7371163f53bbfdb7745c653813b110b4ff5c05dbddb8a053f54bc5d2d7abe`,
including retained bootstrap references/log hashes. Canonical artifacts remain
the primary evidence; no expected outputs, selectors or normalizers were added.

This closes only the selected four description-only declarations. Model/range
adapters, generic status callback/hash histories, full response metadata/deep
merging, schema-name collisions, body-only/optional flattening and mutable cache
histories remain unproved. Broader regression, corrected public controls,
coverage/fault measurement and benchmarks are separate stages.
