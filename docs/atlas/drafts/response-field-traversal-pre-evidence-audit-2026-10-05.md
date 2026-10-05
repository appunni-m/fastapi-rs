# Traversal7 preliminary normal receipt audit

Independent read-only audit, 2026-10-05. No repository edits, app/factory import,
worker/comparator rerun, build, install, current native-binary read or unit test.
Only temporary auditor/data/note files were written under /private/tmp.

## Bounded clearance

`parity-results/response-field-traversal-wave/pre-change/` is closed:
**7 selected / 7 passed / 0 failed / 0 not_run cases**, with all **42 planned HTTP
 actions completed by both source and target**, no blocked steps, no construction
failures, and seven matching successful construction observations. There are
24 state reads and 18 non-state probes. All 36 prior non-state send messages are
retained in exact state bodies. No broader support or full-suite claim follows.

| Actual artifact | ID | SHA256 |
| --- | --- | --- |
| oracle | a64dc1e8-cf99-4c69-a40e-da1ba396776d | 6b26b9d8ccd4a9e8e304ef3ba009f1fa1c854f1ca6fbb922300db14883f55a14 |
| target | 03fbe455-559f-4067-b51f-b3fcd582e1f2 | 672f2c7ab6041393d51338a5a5d9bc2e5f3b59eeceef63e438a8bd8b898101e5 |
| comparison | b452100a-345c-4aa7-82fa-24e3dc8d9c8c | 577bcf0fe697f8667bbb69ccade87fc2d3065cbd1d4d5e023f71ce41eb770737 |

Product artifacts are under parity-results/oracle and parity-results/target;
comparison is under parity-results/comparisons. normal-runs.json SHA256 is
`ea7b658822507e1571947d7b8b2de2a857b9f6ee9c744a721f9c06ba852933e7`.
Initial/final snapshot bytes agree, SHA256
`c19fac9b26b5f9ea913079f8dccb70d4b752ba6a5af2c565ef0dd55fcf305afd`.

All three receipts pass their existing schema@9, have completed status and no
infrastructure errors, and their run IDs match filenames. Comparison hashes bind
the actual product file bytes. CLI logs exactly agree with normal-runs summaries.
Declared runner family, case, action, observation index/kind and singular
selector order agree with the complete input/index plan. Construction selector
order is unchanged. All 21 source requirement refs resolve to partial index
mappings. Metadata retains 65 links to 11 existing public operations; private
DefaultPlaceholder/ModelField remain source evidence and JSONResponse's sibling
ownership remains unchanged. No expected-output substitution, selection/skip/
replay flags, comparator changes or normalization were introduced.

All seven full source/target case records match with scalar types, array order,
and dictionary insertion order preserved, without sorting keys. Exact base64
HTTP bodies expose all callback/error/warning/send journals. Decoding the lossless
raw send projections agrees with canonical actual status, ordered byte-header
pairs, byte bodies and message order. Header tuples are retained, every original
message key is present, and all 18 ordinary response body messages omit more_body.
State trace/event/error/warning entries retain their earlier prefixes; no state
read advances the later branch. Warning journals are equal and empty in these
inputs, which does not establish arbitrary warning-hook/filter behavior.

## Recorded source and normal native bindings

| Binding | Value |
| --- | --- |
| target revision | 9c29938bb63842421d16869df528a5c72398a0a4 |
| sibling revision | b4c8a65c85e1b0d251ca05874412811eaa3ac7b8 |
| FastAPI-RS source | 6d4b05e3c6c26fa4d7669c1dd127d62b46287e41a7e0aad97043a484c7346bce |
| sibling source | 37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55 |
| combined source | 5d8dffaa7a2ae9ba2c79ecd0d92b5323c33396fa8ddfb702cceac4c7e985d138 |
| normal FastAPI extension | 6ec7521b97ec31d685357485f6a225231f1c078bc3f5e3e89285b5adfb3f006e |
| sibling extension | fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5 |
| normal pair | 10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73 |
| manifest | 73dc8ac2edba66d65829b9b0b09f44b890846643fbf45c4a3a3b912e2bc1ee6f |
| index | c52f827d1a91192a57d523d8a6747d9604b6757c67d3911b25fe3f384785434c |
| input | 2b1c485e4e34b30a9c4d9d524036d3b709d3e8dcf514116a76fdd9b6cbfd6655 |
| recipe | 3dfd1caa6573faa55edaef83e1eb166e4279a97542bda323a4ea8ab2de929c66 |
| workload | 35aa2d46026953a69ac6284f6a0215c62df22e19ddac0018c9d31336224de4d9 |

Component digests were recombined independently. Current tracked/nonignored
source hashes were independently recomputed through read-only Git/file access
and agree with both fixed snapshots; no native module was imported or hashed by
this auditor. The actual target receipt records fault_injection_compiled=false
and the explicit b4c8a65 source. Normal native pair equals the restored prior
normal pair, but the newly admitted source/input/manifest bindings are distinct.
Coverage/build replacements must not be equated with this recorded normal pair.

Source identities and exact package profiles bind FastAPI0.141.1 commit
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f, sole Starlette1.6.0 commit
4f250d6b814587e20c5365f0a5f0c4d42bcb929f, CPython3.12.13,
Pydantic2.13.4/core2.46.4 and AnyIO4.12.1. Target profiles have the shared packages
plus the native distributions and no original FastAPI or Starlette packages.

## Actual journal boundaries

- One-use later-field refusal: both setup counters start1; the first request
  reaches2 for first/second, handles the actual IndependentSchemaConstructionError
  with409 and no endpoint call. Retry reconstructs both to3, succeeds200; the
  second route retains3. Raw handler class/message/path are equal and untouched.
- Nested A/B/C: original fields are1 each; the first A request builds A/C to2
  while B remains1. Later C traversal builds B to2; the final B call retains2.
- Earlier full direct match leaves child/other at their original1; visiting the
  include-only path later builds both to2. Repeating the direct path retains
  those values. Earlier POST partial allows the later GET full match to build
  its included field to2; the POST control retains the original direct field.
- Missing path builds both included contexts to2 before404, with no endpoint
  execution; later concrete paths reuse them. Slash search similarly builds
  both branches before307; the declared path later reuses them and returns200.
- Returned Response fields build1 at setup and2 on first included traversal,
  retain2 on repeat, and return202 through ordinary JSONResponse. Their selected
  journal contains no validation/serialization callback despite field setup.

These are fresh recorded public observations, not prescribed fixture outcomes.
No blocker found within this preliminary seven-case set. Terminal 405,
route-version/live mutation, proxies, URL/OpenAPI/WebSocket traversal,
reentrancy/concurrency, arbitrary schemas/defaults/warnings, workers, streaming,
resource finalizers/cancellation and broader generic sibling protocols remain
outside this gate. Full 40/198 and instrumented lanes require their own closed
receipts; this preliminary note does not establish them.

Detailed independently checked data:
`/private/tmp/fastapi-rs-traversal-pre-evidence-audit-data-2026-10-05.json`,
SHA256 `0ccab87a501b7acab885baf68094fdeb790db57a9590701738b0519c9f3dcd4d`.
