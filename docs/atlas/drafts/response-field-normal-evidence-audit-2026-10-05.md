# Response-field normal evidence audit

Independent read-only audit, 2026-10-05. This note is the reviewer's only written
file for this audit. No apps, workers, comparator reruns, builds, installs,
repository edits, or current native-binary reads were performed.

## Bounded result and receipt integrity

**39 complete indexed workflows; 191 selected / 191 passed / 0 failed /
0 not_run cases.** This is the selected normal regression set, not the complete
project corpus or full response-field/serialization support.

Root: `/Users/lazytrot/work/fastapi-rs/parity-results/response-field-wave/final-normal/`.
`normal-runs.json` SHA256:
`5319d53d9bb1a6e3ece7d1d9644f462f255ab979d3ffd722e077aa9a37bed067`.

- All 117 source, target, and comparison artifacts resolve to their recorded
  run IDs/products. Comparison references bind the actual product-file byte
  hashes. Each artifact is completed, has no infrastructure errors, and passes
  its existing JSON schema. The separate pre-field three artifacts also pass.
- Runner family order matches its complete declared plan. Input, recipe,
  workload, manifest, index, case-contract IDs/order and requirement links agree:
  380 source references resolve to partial index mappings and five API references
  to manifest public operations. Supplied source-evidence hashes agree.
- Every normal planned step completed: **445 actions and 15 direct API probes
  per implementation**, with exact IDs, cardinality, observation indices/kinds
  and selector order. Seven matched construction-error outcomes have zero planned
  actions. No normal constructor failure hid an HTTP step. Commands contain no
  case/subset/skip/replay flags; all cases use parity. Inputs/recipes contain no
  expected/golden output keys. Comparator code reads the two live artifacts.
- All 191 full case records match canonically, including scalar types and ordered
  arrays. One legacy `dependency-tutorial-review-upstream` OpenAPI pointer
  observation contains eleven JSON-object key-order differences: source
  `type/default/title`, target `type/title/default`. Values/types agree under the
  existing unordered JSON-map contract; no normalization was added. Raw JSON
  serialization identity for every legacy case is therefore not claimed.
  The new sixteen cases match without sorting object keys.

## Fixed normal identity

Initial/final snapshot bytes are identical, SHA256
`342ee61f90ec44f55be10ed276e6e94532196a50606e09f01327b5a02279dff6`.
Every selected input agrees with their input-hash table. Component digests were
independently recombined; current tracked/nonignored source digests also agree.

| Binding | Recorded normal value |
| --- | --- |
| FastAPI-RS revision | `ebcdf2d2c6c333bbfb04a19d122ad778eb3cbbd6` |
| Starlette-RS revision | `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8` |
| Combined source SHA256 | `2e07a686038c2b1b5cb37b25fc438d10304d7d72d82364f138bcfb2a2b866bb6` |
| Combined native SHA256 | `10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73` |
| FastAPI native SHA256 | `6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e` |
| Starlette native SHA256 | `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5` |
| Manifest SHA256 | `d54cb021dd571b12256324409faf7cd2a21fa7fdcd865431bb44b337f7c7ca88` |
| Materialized index SHA256 | `29bca17097d92cfba9266b8c4ad35c8e12fd6c787efe6b256aa336be95f507b1` |

All 39 target receipts bind this normal source/native pair. Four newer result
contracts record `fault_injection_compiled=false`; 35 legacy contracts omit the
field but bind the same pair. Worker identity code hashes the compiled modules
actually imported. Instrumented/current binaries are not equated to these hashes.

All source identities/package maps match FastAPI 0.141.1 commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 commit
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, CPython 3.12.13,
Pydantic 2.13.4/core 2.46.4, AnyIO 4.12.1 and the full pinned profile.
Target maps contain the exact shared profile plus native distributions, with no
original FastAPI/Starlette runtime distributions and the explicit b4c8a65 sibling.

## New response-field observations

| Artifact | Run ID | SHA256 |
| --- | --- | --- |
| Oracle | `8de6db0e-4e82-4045-875a-3f43e6c24a26` | `0123f8dbb511bfb9c78038adede997701d6801efeacccfc28d14fc55a8ce9af9` |
| Target | `3539ba20-8e6b-4c3a-ae85-54fb9c1d864b` | `b0694ef8d47dbe9e4d1bdd6730a00520adf43fa4a5ebdf66788bd290262af682` |
| Comparison | `af485709-4e66-4ed9-bd15-35ce6e790161` | `82bc808c558da824525431fd0c9cfce86d56e8e0a05f3accb1c216d134130759` |

Artifacts are under `parity-results/oracle/`, `target/`, and `comparisons/`.
Input SHA256 is `e38e3111c17c140732368053bcebff60b7fd65538ff98154d65c4562c0e5d92c`;
recipe is `2213314fc5a3bbc6100ad791e61bbe2c0bfd61deb11ee25358392e12a6b1cd6a`;
workload is `a763538464f0e3a8809daa5fb55ba123a78b852d546170165a370e4f30682d68`.
Recipe/workload remain byte-identical to the reviewed historical proposal.
Eight existing public operations retain 82 links; internal DefaultPlaceholder
and ModelField were not promoted.

The sixteen cases retain all 61 actions: 29 probes and 32 state snapshots.
State trace/warning journals retain their prefixes across reads. The final
journals contain all 58 probe send messages. Decoding their lossless projections
agrees with actual status, ordered byte-header tuples, body bytes and send order;
every ordinary body omits `more_body`. Recorded request errors agree with runner
exception observations. Warning journals match and remain empty in this selected
corpus, including suppression of the unused field-alias warning; this does not
establish unrelated warning hooks/categories.

Observed source/target boundaries agree: one direct setup schema build retained
across requests; original-router plus two effective-context builds at registration
and `ready`, request 0, retained across three probes; captured setup ValueError;
uncaught unsupported-model FastAPIError with no actions; constrained response
error details and raw body followed by recovery; aliases/exclusion callbacks;
omitted/inherited-placeholder NaN bytes versus concrete-class errors; explicit
None TypeError after response processing; and returned-Response bypass with its
setup field still built and no validation/serialization callbacks. All callback
and send/error observations are unchanged selected receipt values.

## Preserved pre-field diagnostic

`pre-field/normal-runs.json` binds comparison
`b80e49cc-64cf-4f7b-85c5-20737b3b84a6`: **16 selected / 6 passed / 10 failed /
0 not_run cases**, source/target exits 0 and comparison exit 1. All ten failures
retain diffs. Source completed 61 actions; old target completed 49 and explicitly
recorded **12 not_run actions** after three include-keyword constructor failures.
Case-level zero not_run must not be presented as all old-target steps executed.

Pre-field snapshots are stable within their separate run. The final source's
full sixteen case records, identity, input/workload and manifest bindings exactly
match the pre-field source. The old target/source/native identities remain
separate from final-build evidence and instrumented coverage.

No blocker found within this normal receipt set. Mutable model/cache history,
flattened snapshot route mutation/version refresh, raw included-route proxies,
URL/OpenAPI/WebSocket materialization traversal, concurrency/reentrancy and
unselected serializer/warning/provider protocols remain outside the immutable
sixteen-case clearance. Same-source instrumented coverage/fault evidence is a
separate lane and was not compared to this recorded normal binary pair.
