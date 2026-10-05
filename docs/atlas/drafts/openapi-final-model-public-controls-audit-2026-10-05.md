# Closed direct OpenAPI API controls and historical suite review

Read-only artifact audit, 2026-10-05. No application/native import, build,
installation, parity, coverage or benchmark command was run; no active file
or artifact was changed. The benchmark move below is a proposal only.

## Actual direct-control gate

`parity-results/next-openapi-response-field-wave/public-controls-v2/` contains
**2 whole API workflows, 4 selected / 4 passed / 0 failed / 0 not-run**.
All six oracle/target/comparison commands exit 0. Both product sides have four
completed cases and four completed probes; each side records **5 observations:
4 return documents + 1 public signature**. All cases, probes and artifacts are
completed with empty infrastructure errors; comparisons have no differences.

Artifact input/workload/manifest hashes and all comparison artifact digest/run
ID links match their actual files. Initial/final snapshot bytes are identical.
Both target identities bind revision `62dacc5283a0cee282258e268f7545765679e974`,
Starlette-RS `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`, combined source
`503211630df8f7e2bf624c55c217d08444658252311bff19bf6568b4736a4c0f`, and native pair
`e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0`. Recorded native files are FastAPI
`d934ba09884e6c8a657300c4800a92e76577285f2bf5833e73418d21912b6140` and Starlette
`fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.
These are closed-run receipt bindings, not measurements of binaries after
coverage or other later stages.

Oracle identity remains FastAPI 0.141.1, Starlette 1.6.0, CPython 3.12.13,
Pydantic 2.13.4 / core 2.46.4 and the pinned FastAPI/Starlette revisions.
Current manifest is `eba84432c34ad05b8b0613d2d9a285443d100357d189bd7583c935cac9758859`.
The frozen artifact/projection hashes are retained in the JSON audit below.

## Observation strength and source limits

The empty-route signature preserves all 14 keyword-only parameters, default
and annotation values, ordered parameter array and return annotation. The
other selected results cover empty metadata, explicit info/contact/license/
server/tag/externalDocs data and two ordinary parameter-free static GET routes.
The source and target retain `api@example.invalid` and normalize externalDocs
URL to `https://docs.example.invalid/`.

API worker `_json_safe` (`api_worker.py:135-151`) projects return values to
strict JSON, preserving key insertion order in the saved result. The comparator
(`api_comparator.py:31-42`) is recursive and type-strict, but dictionary keys are
compared as a key view, so dictionary insertion order is not its gate. Ordered
signature/list values are gated. An independent compact serialization of each
saved document matches source/target bytes, including every nested key order:

| Case suffix | Audit projection bytes | Recorded root/operation order |
|---|---:|---|
| empty-routes | 92 | openapi, info, paths |
| document-metadata | 512 | openapi, info, servers, paths, tags, externalDocs |
| single-route | 265 | operation summary, operationId, responses |
| single-route-tags-version | 292 | operation tags, summary, operationId, responses |

Those byte counts are derived audit projections of saved API JSON values;
**they are not HTTP body observations**. These four controls have no ASGI
requests/raw sends or HTTP-byte comparator, no warning/logging sidecars, no
malformed metadata/error input and no public model/type-identity projection.

Pinned source `openapi/models.py:15-54` selects EmailStr by optional import,
falling back only on ImportError; its fallback warns through the logger and
returns a string. `logger.py:1-3` supplies logging.getLogger("fastapi"). These
controls observe the resulting contact email string, not the selected type,
warning emission/count, fallback callback path or optional-installed branch.
Those email branches remain explicitly unmeasured. Source
`openapi/utils.py:679` finalizes OpenAPI then dumps through the encoder;
`models.py:112-114` makes the externalDocs URL normalization a final model
validation property. Success here supports the selected direct subset, with
full HTTP wire regression evidence kept separate in the parent-reviewed 206.
No coverage, fault, restored-binary or equivalent-benchmark claim is added.

## Historical benchmark suite recommendation

The active nonrecursive root contains **one** existing suite:
`benchmark-results/suite-20261005T121923Z-250a48d8-8719-4737-82bb-de7a71841c51.json` (completed, seven workloads), SHA256
`b71c0a5db8ae410ff7a73ae5ff36571428f3ed6a3cd150f247e296cff809cc8e`. Its seven workload result digests and seven comparison
artifact digests still match. Every comparison binds prior manifest
`ae88fc58d1ead1a70cf3b9435c470b16794a03f050f368eb0e68f7c4457cc697`,
not current `eba84432...`; its source revision is 827612f, not 62dacc5.

`run_suite.py:467-482` validates ALL root suite-*.json through a nonrecursive
glob. `contract.py:243-244` requires each referenced parity gate's current
manifest. A fresh suite cannot repair that existing historical mismatch.

Move only the unchanged suite file to
`benchmark-results/archive/827612f-before-openapi-final-model/` using its same
basename. Leave all seven referenced benchmark result and comparison paths
(and their source/target artifacts) in place, because the immutable suite names
those paths. Preserve the old suite log/post-suite snapshot too. Record
original/new suite paths, before/after identical SHA256, run ID, revision,
old/current manifest and all original path/digest bindings in a relocation
receipt in that archive. The plan below contains exact paths/hashes; it is
marked performed=false and has no after digest yet.

The entire benchmark-results tree is already ignored. Archival records
historical evidence under its original context; it does not alter the root
glob, validator, current-manifest requirement or outcomes, and it gives no
current benchmark result. Parent owns the move/receipt, fresh seven-workload
measurement after exact normal restoration, and any later independent audit.

## Frozen TMP audit files

- JSON audit: `/private/tmp/fastapi-rs-public-openapi-controls-v2-audit.json`,
  SHA256 `3499e8740e89a20087d3413f19aa55504ae3677abf5109692f07ad1201bf7e3c`.
- Exact preservation proposal:
  `/private/tmp/fastapi-rs-benchmark-suite-preservation-plan.json`,
  SHA256 `b42741eb3c72964adeecef270bf3a949d22615b474b0989b2d5136adb7b4f5f0`.
- Gate ledger SHA256 `511e7ec31a491c8a82f82f94bee67cb0774737e28279e4f27861c96e678ce30e`;
  both snapshots SHA256
  `0d7899c377d01ef9e3a6c31b2ab92bf67599b300ed03ea2e9c729a3b6c31d456`.
