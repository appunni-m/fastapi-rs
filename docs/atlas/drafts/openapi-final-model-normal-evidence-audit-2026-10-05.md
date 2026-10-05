# OpenAPI final model: independent closed normal evidence audit

Date: 2026-10-05. Auditor: runtime peer. Scope: saved, parent-acknowledged CLOSED stages only. This audit reads JSON inputs, schemas, index, manifests, ledgers, receipts and saved snapshots. It does not import products, launch applications/parity/builds, read current native binaries, change active files, or read the LIVE coverage folder.

## Declared result and completion

| Closed stage under `parity-results/next-openapi-response-field-wave/` | Workflows | Selected / passed / failed / not_run | Actual completed work per implementation |
| --- | ---: | --- | --- |
| `post-final-model-v2/` | 1 | 3 / 3 / 0 / 0 | 3 successful constructors; 19 HTTP actions; 64 observations |
| `final-normal-v3/` | 44 | 206 / 206 / 0 / 0 | 96 construction observations (89 successful, 7 matching public errors); 523 ASGI actions; 15 API probes; 917 step observations |
| `public-controls-v2/` | 2 | 4 / 4 / 0 / 0 | 4 direct API probes; 5 observations; no declared warning sidecars |

The broader two stages contain **46 workflows / 210 distinct declared passed cases**. The targeted three are already in the 206 and are a separate rerun, not three additional cases. There are 138 distinct-stage receipt artifacts plus 3 targeted rerun artifacts, each bound to its source/target/comparison ledger entry.

All planned case, action/probe and observation-kind/index orders are complete. There are no blocked actions/probes or infrastructure errors. The seven constructor-error controls complete their declared cases; they are neither skipped requests nor successful constructors. Their exact classes/messages and source/target construction records match, including scope/assertion errors and the unsupported response model error.

The audit validates each declared artifact/input/index schema, duplicate-key rejection, artifact/run-ID and comparison source/target path/hash bindings, current manifest hashes, materialized input hashes, recipe/workload hashes, indexed case contracts and requirement references. It checks ordered declared selectors where represented in result records, all requested warning arrays, saved snapshot input bindings, and complete planned lane results. No case/subset/skip command arguments or expected-output replacement are present in these closed ledgers. Actual source and target observations remain unmodified.

## Frozen identities

Every recorded target identity uses revision `62dacc5283a0cee282258e268f7545765679e974`. Parent identified the run checkout as clean at stage launch. Each stage's saved initial/final snapshots is byte-identical, and all three stages share:

- combined source SHA256: `503211630df8f7e2bf624c55c217d08444658252311bff19bf6568b4736a4c0f`;
- FastAPI-RS source tree: `6a38bbe00ed5d9814b7c0e0bf435e0349c042243a4842422d622add1925fbb06`;
- sibling source tree: `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`;
- normal native pair: `e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0`;
- FastAPI native file: `d934ba09884e6c8a657300c4800a92e76577285f2bf5833e73418d21912b6140`;
- sibling native file: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.

Pins in actual receipts are FastAPI 0.141.1 / source `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 / source `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, sibling `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`, CPython 3.12.13, Pydantic 2.13.4/core 2.46.4 and the recorded shared packages. Target package identities do not include original FastAPI.

Newer result schemas explicitly record `fault_injection_compiled: false` (7 full-stage workflows and the targeted rerun). The 37 older full-stage workflows and two direct API workflows omit this field because their declared schemas do not permit it; they bind to the same saved normal pair. No claim equates current instrumentation binaries to these historical normal files.

Stage snapshot SHA256 / ledger SHA256:

- targeted: `fa643d7562d2ece98694cdc22f471ba81ec2cf842430cb8db8481761c70a454c` / `b0e9149adcc823b9a831add03a5505e9747bcd69a862a6bdfec33b95f765a6d2`;
- full206: `1e350d23fefdfc2ad8e2f72ec796f527a83e92adebd74e6e311319343881c0ed` / `623494428d964a8c03bedf01007bccdb48458a896f8c7968610fbcda102cf3f4`;
- direct4: `0d7899c377d01ef9e3a6c31b2ab92bf67599b300ed03ea2e9c729a3b6c31d456` / `511e7ec31a491c8a82f82f94bee67cb0774737e28279e4f27861c96e678ce30e`.

## Historical oracle stability and exact wire repair

The preserved `final-normal/` stage at 1c66469 declares 205 passed / 1 failed / 0 not_run. All 44 workflow/input orders and all **206 complete ordered typed oracle case payloads** equal the fresh full-stage oracle payloads. The failed stage and earlier bootstrap/build failures remain historical evidence; they are not aggregated into the current pass count.

For `fastapi.first-slice.openapi`, `get-openapi`, source/new target status 200, both ordered headers and all **2057 response bytes** are exact:

- preserved and fresh source / corrected target body SHA256: `52e6edbe28c219cf75ddaedb3482c944a41d24b5efd52c3794b18209ff7ecacd`;
- failed 1c target body SHA256: `8e9dbac4fc3184a2d2e5a30da7f70df9c46180cd76a9dd870ac098d2c9060def`;
- fresh source artifact `oracle/9e95bb61-64c0-4fab-891e-7903af62324b.json` SHA256 `d004005a775f2df566ba485e24f205004a4f2015dfa9df55cce3f199f92df9d7`;
- fresh target artifact `target/90d3e288-c2a9-4251-9ab8-2d2e6595cc78.json` SHA256 `8d1e4fb576eab79240a5933ba025338129c7976e2ff3cc7fd08827892335fc9b`;
- fresh comparison `d475fec5-c833-4699-8185-33f8d8cd7bc2`.

These artifact paths are under `parity-results/`. Decode `cases[case_id=fastapi.first-slice.openapi].actions[action_id=get-openapi].observations[kind=http_response].values.body.data` as base64 and hash those bytes to reproduce the wire check. The three `/items/{item_id}` POST parameter maps now retain source `[name,in,required,schema]`; requestBody retains `[required,content]`. This establishes the selected raw wire repair rather than parsed-document equality alone.

## Targeted three and explicit ordering limit

The targeted and full-stage next-three source/target complete ordered typed case payloads all have SHA256 `16dd4a2b95e3cf8f8394f4c50e6f50f75f9587e6b1e00ef0a1b05d2b2bf074ee`, also equal the preserved pre-change oracle. Input SHA256 remains `558a3d9cde89de0fd8342fe9a04deaef08a3caac836f5afd3a1b16d0c6829767`.

Actual selected results preserve raw schema bytes, headers, lossless public ASGI journals, full fixture warning/exception journals, retained core-hook counts and cache observations. Shared JSON-hook count is six in both products; it is not evidence of one-call deduplication. The 409 refusal matches complete class/message/body, retry succeeds without rebuilding retained core fields, and later cached calls preserve journal counts and `[null,true]` cache identity. Full-stage run IDs are source `c3010244-d787-4759-8770-10064641c13b`, target `bb80fa83-7418-4682-a367-21f352abb344`, comparison `f3482b8f-7f4c-4e12-a6de-b4b3f2e5c3e3`. The separate targeted audit supplies exact body and warning/error digests.

Full ordered typed projected receipt equality holds for 43 of 44 full-stage workflows. The exception is the legacy structural selector in `fastapi.dependencies.tutorial-review.openapi-projection`: 11 nested schema maps retain source `[type,default,title]` versus target `[type,title,default]`. There are no other value/type/array differences in that case. All 11 are an exact subset of the preserved old target's 29 map-order differences; 18 Parameter map orders are repaired. The unchanged structural comparator declares this case passed. Thus **210 declared passes do not establish all210 raw wire or ordered typed equality**. Direct4 establish their declared structural API/signature outcomes and capture no warning sidecars.

## Reproduction and bounded summary

Audit helper `/private/tmp/fastapi-rs-openapi-final-model-evidence-audit.py` with config `/private/tmp/fastapi-rs-openapi-final-model-full-audit-config.json` writes the complete hash/run-ID/schema/input/snapshot/detail report. Supplementary helper independently verifies the residual-order subset, constructor errors, observed selector metadata and targeted/full consistency. Both read saved closed files and write only TMP.

Files and SHA256:

- full report `fastapi-rs-openapi-final-model-full-audit.json`: `8d4c6e0a7ad4619872acb279a3c402a0e7deaf99d6aafc01a689f1e34856a004`;
- historical report `fastapi-rs-openapi-final-model-historical-audit.json`: `115e5975ca074e918b50fcc933ad3913b469a0093cd90bd91578ae4536c8b10c`;
- supplementary report `fastapi-rs-openapi-final-model-supplementary-audit.json`: `b035bad13be33ae7f9203537a71121699133e73551bc11c9033341e63811001b`;
- main helper: `d2c12648a313eeeb186d2abc5e7a6065617f457bc7b0ef6c644069a5b5a3e883`;
- config: `905c9ab0b74acbcec2d621876c8eb98ee130062d3fa1a4ac283d848435938c42`;
- supplementary helper: `a976d04cb2f5918dacc90df4546b4d1beb341ae087dff6602085080bbe255aa1`;
- separate targeted note: `879f84d48491f932033173eb87f1548fc6d1c525a2412f32969c3291129d1e0c`.

Bounded measured summary: fixed normal source/pair passed the 210 declared distinct cases plus the separate three-case rerun; the selected first-request exact-wire regression is fixed and all206 oracle payloads remain stable. The legacy nested schema map-order gap remains. These receipts do not establish unexercised OpenAPI assembly/status/default/outer-alias branches, public model API compatibility, warning behavior of direct4, or complete await protocol/mutation/concurrency support. Coverage, fault, restoration and fresh benchmark stages need their own closed evidence and are outside this note.
