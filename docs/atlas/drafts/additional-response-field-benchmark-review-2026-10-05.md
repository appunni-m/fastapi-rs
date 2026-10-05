# Additional response field benchmark evidence audit — 2026-10-05

## Bounded conclusion

The closed canonical suite contains all seven reviewed workloads, each with a fresh complete public parity gate before measurement. No admission or receipt-binding blocker was found. Independent arithmetic reproduces every retained latency summary, throughput value and reported ratio. The closing readback, performed before the parent began subsequent documentation edits, matched the recorded normal source and native pair. This note binds the measured historical state; it does not assert that later documentation edits retain the same full source digest.

Only read-only artifact/schema/identity inspection and raw-data arithmetic were performed. No app execution, native import, build, installation, test run, source edit or benchmark rerun occurred. This note is the sole output under `/private/tmp`.

## Closure and identities

- Suite: `benchmark-results/suite-20261005T121923Z-250a48d8-8719-4737-82bb-de7a71841c51.json`, SHA256 `b71c0a5db8ae410ff7a73ae5ff36571428f3ed6a3cd150f247e296cff809cc8e`, status `completed`, failure `null`; exact reviewed order and seven completed artifact references.
- Log closes with status `completed` and workloads `7`. Parent reported process exit 0; the auditor did not rerun the process.
- Log: `benchmark-results/additional-response-field-827612f-suite.log`, SHA256 `d69beda5b7d626b60f40313c0e138dcc1e18eada6be95d515e04d19581ef7b87`.
- Measured clean HEAD: `827612f28226dc5c0d6e008d1a38231c03293389`.
- FastAPI 0.141.1: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; Starlette 1.6.0: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Immutable sibling: `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`, revision `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.
- Closing git readbacks: FastAPI-RS, sibling and FastAPI clean; Starlette has no tracked change and only an untracked `.DS_Store`.
- Recorded and independently rehashed source trees: FastAPI-RS `f7cd6b9ef3d93cd2da3c85a45a4a9eaf4ab1aeb97620d96c7ab2c44e7c1b166c`; sibling `37e8af974396041b2194e256820f4d1e15787beb9f54e6ca1bf7b5937367ab55`; combined `204d9a6aa869e6ec5623f6a93c07fa7973910784c7b63e64efd21f51ea17edf2`.
- Independently rehashed normal extensions: FastAPI `_core.abi3.so` `5eeae03b977c74fed3808df9194bef0d23527a8208b2c05c92f9415084b7a244`; sibling `_core.abi3.so` `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`; combined native pair `8e1888dbe104c3bdf69f63b47bb0e9ded4a3ba9cc70d2c04676890134501f6ed`.
- Source-tree hashing reproduced the runner’s tracked plus nonignored file algorithm, including symlink/missing-file tags; pair hashing reproduced sorted name/NUL/digest/NUL concatenation.
- Restored normal proof: `parity-results/additional-response-field-normal-restore-snapshot.json`, SHA256 `0714a90ccbc9e50cd34979f4c869032ea092be1f64a7d50f22fa5f6247113213`. Its recorded native identity reports `fault_injection_compiled=false`; byte identity was independently tied to the same normal pair without importing it.
- Normal 203-case reference snapshot: `parity-results/additional-response-field-wave/final-normal/initial-source-build-snapshot.json`, SHA256 `3a2922a1a05b366ac3f15faae56fd0d93f8f2c54b792db2898f097baa7da2318`. The recorded source/native fields equal restore, post-suite and the auditor’s closing readback.
- Post-suite proof: `benchmark-results/additional-response-field-827612f-post-suite-snapshot.json`, SHA256 `5fc89e9ebd7b287157503263c98986b53e4b169655338ca8b0346239fe1f424f`; clean recorded HEAD and exact preservation flag agree with the closing readback.
- All seven fresh parity target identities bind source `204d9a6a…` and pair `8e1888db…`; every timed target identity binds this pair and the FastAPI extension hash above. Oracle, target and control runtime/package identities are internally consistent.
- Runtime: CPython 3.12.13; Pydantic 2.13.4/core 2.46.4; AnyIO 4.12.1; annotated-doc 0.0.4, annotated-types 0.7.0, idna 3.18, typing-extensions 4.16.0, typing-inspection 0.4.2. Target receipts contain `fastapi-rs`/`starlette-rs-py` 0.1.0 and no original FastAPI or Starlette distribution.
- All subjects: macOS 15.7.7, arm64/arm, 12 logical CPUs. Recorded release build: Rust 1.98.1, Cargo 1.98.1, aarch64-apple-darwin, LLVM 22.1.8, exactly `pyo3/extension-module` feature.

## Public parity gates and input bindings

- Seven distinct fresh comparison receipts plus fourteen source/target receipts passed schema validation, referenced hash/run-ID/product checks, complete ordered case/action checks, current manifest/input/workload binding and successful completion checks. Every infrastructure-error list is empty. No action, constructor or planned case is skipped; no case-ID subset flags appear in these commands.
- Workflows repeat as planned: two nested gates each execute 2 cases/8 actions; chunked, invalid and valid gates each execute all 12 first-slice cases/12 actions; large response executes 1 case/1 action; sequence query executes 1 case/3 actions. Totals are 42 case executions and 56 ASGI actions per side, not 42 distinct cases.
- Current materialized index case IDs/order and recipe/input/workload hashes match every gate. Input-only workflow schema validation and source references passed; no expected output substitution was introduced.
- Source/target recorded case values compare equal for all seven gates. Their JSON value types, list ordering and dictionary ordering also match except for the unmeasured sequence-gate OpenAPI root object described below.
- Gate completion timestamps precede all corresponding measurement-subject completion timestamps; suite workloads are sequential, with each prior result finished before the next gate is created.
- In three first-slice declarations `action_id` is null: the chosen case has exactly one `post-item` action and every subject records that concrete ID. Other declarations record and match the explicit selected action ID.
- Manifest SHA256: `ae88fc58d1ead1a70cf3b9435c470b16794a03f050f368eb0e68f7c4457cc697`.
- Materialized index SHA256: `517719a589e8199d64fdf5f99aabe864f8a0e954e22540bc6f40b2e4581c631f`.

## Raw measurements and verified ratios

Each of 16 subject measurements retains 1,000 positive integer nanosecond samples: 50 warmups, 5 rounds × 200 samples, concurrency 1. This is 16,000 retained latency samples, 800 warmup calls and 16 extra baseline calls whose elapsed values are discarded. There are 14 FastAPI/target measurements and two contextual Starlette controls.

Every min/max, integer median, P95/P99 and arithmetic mean was independently recomputed from its entire raw array. Percentiles reproduce `ordered[round((n-1)*percent/100)]`; median reproduces `int(statistics.median(samples))`. Every loop throughput reproduces `1000 * 1e9 / request_loop_elapsed_ns`, and loop elapsed exceeds the sum of timed per-request latencies. Both ratios reproduce target/source summary division exactly. No outlier was removed.

Latency columns are nanoseconds. Ratios are target/oracle; values below 1 mean less target latency for this specific workload.

| Workload ID | Gate cases/actions | Oracle median | Target median | Median ratio | Oracle P95 | Target P95 | P95 ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fastapi.async-nested-distinct-query-aliases.asgi` | 2/8 | 499395 | 320771 | 0.642319206240 | 536709 | 376959 | 0.702352671559 |
| `fastapi.async-nested-two-query.asgi` | 2/8 | 421792 | 273479 | 0.648374080115 | 453333 | 295917 | 0.652758568205 |
| `fastapi.first-slice.chunked-body-asgi` | 12/12 | 135708 | 142729 | 1.051736080408 | 155542 | 168041 | 1.080357716887 |
| `fastapi.first-slice.invalid-asgi` | 12/12 | 146666 | 324208 | 2.210519138723 | 212500 | 357833 | 1.683920000000 |
| `fastapi.first-slice.valid-asgi` | 12/12 | 137229 | 147583 | 1.075450524306 | 160417 | 213583 | 1.331423726912 |
| `fastapi.large-response-model.asgi` | 1/1 | 373541 | 402500 | 1.077525626370 | 415042 | 448375 | 1.080312353930 |
| `fastapi.request.repeated-sequence-query.asgi` | 1/3 | 103625 | 114291 | 1.102928829916 | 124334 | 136916 | 1.101195167854 |

The two nested workloads have lower target medians and P95s; the other five have higher target medians and P95s. This is a seven-scenario observation, not an aggregate speedup or evidence that a particular implementation change caused a difference.

| Contextual Starlette control | Median ns | P95 ns |
|---|---:|---:|
| `fastapi.first-slice.chunked-body-asgi` | 5125 | 5625 |
| `fastapi.first-slice.valid-asgi` | 5125 | 6541 |

Controls return a fixed matching 201 JSON response through an async Starlette route. They perform no FastAPI dependency, input/body or response-model validation. They provide framework context only and are not subtracted from the timings or treated as equivalent work. No control is declared for the other five workloads.

## Measurement boundary and limits

- `scripts/benchmarks/worker.py` starts the per-request timer immediately before `await app(scope, receive, send)` and stops immediately afterward. This includes public facade/native conversion/dispatch, request work, dependency and endpoint execution, response validation/serialization and captured ASGI sends for the selected input.
- Interpreter/module startup, app/route construction, large-response payload generation and HTTP server/network/client work are excluded. Scope and receive/send callback construction happen before the per-request timer. Signature extraction and correctness checks happen after it. Sequential request-loop throughput includes those per-call costs and loop bookkeeping, so it is a separate boundary.
- The app is constructed once per isolated subject worker and reused across baseline/warmups/samples. All selected factory inputs are default/empty; no ignored per-case factory configuration changes equivalent work.
- Every measured and warmup request is checked against its subject’s untimed baseline by the worker. Cross-subject retained baseline status, ordered header hex and full concatenated body hex are exactly equal, including the two controls. The selected oracle receipt status/body, where recorded, also matches this baseline.
- Benchmark response signatures concatenate body chunks and omit other ASGI fields; they do not prove complete ASGI message shape. Full raw-send/cleanup/scheduling compatibility is separately bounded by the 203-case normal receipts and their existing inputs.
- The sequence gate selects `/openapi.json` as a third unmeasured action using an OpenAPI root-map selector. Its parameter schema is recorded oracle `{type, items, title}` versus target `{items, type, title}` insertion order. Values/types match and the existing map comparator passes, but this gate does not prove raw OpenAPI JSON byte order. The measured `repeated-valid-integers` response body and ordered headers are exactly equal. No selector or comparator was weakened.
- Nested workloads use async endpoints/dependencies. Valid/chunked first-slice endpoints are async with a sync header dependency. Invalid first-slice rejects validation before its endpoint. Large-response and sequence endpoints are sync; large response uses 300 prebuilt nested dictionaries and a response model.
- Subjects execute in declared oracle→target→optional-control order, without randomized interleaving or declared CPU affinity/frequency controls. Five rounds are retained as a single ordered sample array, without confidence intervals. No network, concurrent throughput, complete API compatibility, native-only cost, cache mutation history or historical-revision causal claim follows. Exact public schema byte/hook timing remains a proposed separate frontier.

## Frozen artifact hashes

Paths below are repository-relative. All were read and hashed; the suite binds the result hashes, which bind comparisons and the two live receipts.

### fastapi.async-nested-distinct-query-aliases.asgi

- benchmark: `benchmark-results/20261005T121208Z-e70f9fe8-1979-4208-a385-cb08bff0932a.json`, SHA256 `8cff856ba520a5394cd3795953a58d9043faf5c14557927ccdd0dbd861cad620`.
- comparison: `parity-results/comparisons/48bcc20e-8903-42a6-8d36-28685756b9bc.json`, SHA256 `eaada9de6ee46879b374d2c400cd00a0a83aec45860c289d389bb2a93805e79e`.
- oracle: `parity-results/oracle/9a42499b-e10c-4d32-8451-32bf1e0c5d78.json`, SHA256 `4b9fdcd6eeaf6cb8009c4d652306e1e2b6dc6f454b19d1e9544d40f323e5bc55`.
- target: `parity-results/target/22cd057e-9e21-4a33-a7a1-44e1e118e9b3.json`, SHA256 `d4a1ce40ab3dd3aedca30ce1f646c87036b4b1c9b6c200ee37dd82c428b8a7fd`.

### fastapi.async-nested-two-query.asgi

- benchmark: `benchmark-results/20261005T121322Z-b7a778c3-a6c0-4810-a526-f73af5347948.json`, SHA256 `6420270e726330e3cf4e66ca68ba0e0615673d21335a44e4eeef8ce0ad912844`.
- comparison: `parity-results/comparisons/85255bf6-c7b6-463a-88a4-45f99d78cb81.json`, SHA256 `cebf3191b91f08283c5bd6128a1536952f417d68896dc4dc05837de971cd4e8b`.
- oracle: `parity-results/oracle/c9e7789f-91ce-4cb4-898b-c7c565745b24.json`, SHA256 `4f7fdbb2c9a88faec4478866769c20a469ab8d1285b9c0db05aab3d13690b7b8`.
- target: `parity-results/target/57145bc3-5a17-4f74-b75f-fcbf5022d3c8.json`, SHA256 `f63320984e60e9f8f09578552d184b422d58e474c66041dd8113a24eeb10c643`.

### fastapi.first-slice.chunked-body-asgi

- benchmark: `benchmark-results/20261005T121434Z-808236c9-7456-4c21-898f-c3d10d2ae050.json`, SHA256 `79df9061312f907e20771d32cf662954a6ff44df243fdefef4262edbdd9b4ce1`.
- comparison: `parity-results/comparisons/7367bc1c-2b72-4fd9-b405-01d6ec0614d0.json`, SHA256 `73cae6984463777b4ddbd74b3c4dca95455b2c499dfd98936d7f0a60a6053064`.
- oracle: `parity-results/oracle/cc1a4b56-2529-48dc-8804-8113272fafcd.json`, SHA256 `bbfe05eb520cfe210df8ce0ac475282f862c8742106c16fdc71f8e9c9257bc2e`.
- target: `parity-results/target/f6c22b24-40c2-4bb4-856c-87208c81b07e.json`, SHA256 `4f876f41d342df23b9f5a2dad32c49854df2ed184b14c17c8e601fb9a284a7f3`.

### fastapi.first-slice.invalid-asgi

- benchmark: `benchmark-results/20261005T121543Z-5245cbe1-6184-482a-9b43-1bc02ecab8e9.json`, SHA256 `84e2dbc07ca530f764a742e7709578c768fa860cacd074456691e4374e454fa1`.
- comparison: `parity-results/comparisons/8ea31188-54ff-4d2d-a96d-ba16c7a43790.json`, SHA256 `42c918a93736ac01057c3b801d149b194c81e6a925751dbb4a34dbf438af0265`.
- oracle: `parity-results/oracle/173bced2-ed41-4a7c-b001-15d7fe170846.json`, SHA256 `d78b9709cc47baa40468d22340c572942c3003e12d7e5f11f5beb47f74b28a2d`.
- target: `parity-results/target/3beda16b-f944-43f5-8524-8372d5878ea1.json`, SHA256 `6b941612a9b27fa990efceac2a2ad42151e54d2746bf0fac261291a65bdba648`.

### fastapi.first-slice.valid-asgi

- benchmark: `benchmark-results/20261005T121656Z-ac3c9d89-c327-400d-9c8e-854dbe4b9a82.json`, SHA256 `6725f7caabc616f4dfed9ade4bfc30f635f578970fd665e4e168c902277b53b6`.
- comparison: `parity-results/comparisons/106260a9-9ec2-47bd-9c97-1501de7a535d.json`, SHA256 `7e6da53e41dd79e6e266500176219389bd075debe9e90c9e6b5d03701cc7d455`.
- oracle: `parity-results/oracle/7e533434-6b57-4a2a-8937-0f32668e69da.json`, SHA256 `add2ceb06439fecf145c12047f4cbd3c427bbd5e4e5e3fc90e7e7f472ed5cb25`.
- target: `parity-results/target/ea5e3a13-3582-4fb1-a887-650b859fdaf9.json`, SHA256 `96aadeae28ad7baad2e4c9ce73cd2d39db28da9bc372253eb2ab9ecfab758c35`.

### fastapi.large-response-model.asgi

- benchmark: `benchmark-results/20261005T121809Z-0fc7a7e0-02f3-4c2b-8b65-e9d13f54a339.json`, SHA256 `144b28f0703822e81045f8cbfe4c43ba95eeb6d92870fb782f1db11907ce9acf`.
- comparison: `parity-results/comparisons/22d711a4-b611-45ca-852b-8b9415fea038.json`, SHA256 `0e3375507e8c6374690cf1e71eb563943c0da94f429efcbf5eefff65f228d586`.
- oracle: `parity-results/oracle/112f94e6-0795-4613-a154-35e2d3181e63.json`, SHA256 `133fd6df3f901df80b7dae1223112f12ad7c65b657a29842acbd728113b545c1`.
- target: `parity-results/target/08f94248-bcec-4aec-a94f-da72fa3bda9e.json`, SHA256 `56c4addccd71670d4688a9d1787c500d557ac1e1cba6d70ef54c237da035ac5b`.

### fastapi.request.repeated-sequence-query.asgi

- benchmark: `benchmark-results/20261005T121923Z-91619a75-98bf-485f-a095-3fa91abcfbff.json`, SHA256 `752cbc5217ef47457d0b7e4adb73b8177e4a7d4fd3f95bd0ac044480092b8e94`.
- comparison: `parity-results/comparisons/0bc99df1-66ae-4c30-925a-7baea1971875.json`, SHA256 `2fd412be1f16ccc0608f812771802ed5fc8daeb1b30af57a05ffecd62f6fd9c5`.
- oracle: `parity-results/oracle/ba961770-88d7-4621-8a54-680aa353e98c.json`, SHA256 `17c055c81c9cdc2e8289e0a782719bc26033e13ee110fa4dce700e5456d0375f`.
- target: `parity-results/target/17d6a835-f566-4506-a021-b2c8d91041ea.json`, SHA256 `cf794873ee462a83b6917777974ac51ac44ee64a337593e5eb4d80befd0a9678`.

## Admission input/declaration hashes

- Benchmark declaration `benchmarks/workloads/async-nested-distinct-query-aliases-asgi.yaml`: `68dc7041a3d02d27af5c6766c93ac33d1595ce1544718ae5e93a103c77e4f49d`.
- `tests/fixtures/inputs/parity/dependency-override-async-nested-two-required-query-wave.json`: `ad4c97b7ca940bba454249f4076faf2860a4f3eb80cdec433c492a1e9b331d11`.
- `tests/fixtures/input-recipes/parity/dependency-override-async-nested-two-required-query-wave.yaml`: `9f8510206fd5397f591f3360b580f32ceb9e1e10a8c36103ba01a93497249016`.
- `tests/fixtures/workloads/dependency_override_async_nested_two_required_query_wave.py`: `b141d4a519a40acd92aab0f195b39f783713256c25678307630c098b0716a5c4`.
- Benchmark declaration `benchmarks/workloads/async-nested-two-query-asgi.yaml`: `c4ee9f39cbde5120a07d676dd3ea6c4834acd1b2f8406bd963849e31e75e5f79`.
- Benchmark declaration `benchmarks/workloads/first-slice-chunked-asgi.yaml`: `48e67cd99062729567a18c45c4b6147061c8cae04c6bd173c3a354029adf7be7`.
- `tests/fixtures/inputs/parity/first-asgi-request.json`: `b22280138b86cee8ab23c71db5cb6048fbe6920de2edc58e19aec1f1a126e2ef`.
- `tests/fixtures/input-recipes/parity/first-asgi-request.yaml`: `54a6e3101eb040f85e535dedbcbb70489684d74cd3bffd09c369a2e7e4fc3386`.
- `tests/fixtures/workloads/first_slice.py`: `da41fd8b054c50c6ffdcdc92a943440c88b4c94f9bdb83a9b510058e9ba7b3ec`.
- Benchmark declaration `benchmarks/workloads/first-slice-invalid-asgi.yaml`: `7ad9677d1938dfb93aaa3d6dd6341177512ceac31b79e2ddea27de76e467b001`.
- Benchmark declaration `benchmarks/workloads/first-slice-valid-asgi.yaml`: `fcc07446d1bc4e60a9375319a048736690647625ce6fb905de6621d11901177a`.
- Benchmark declaration `benchmarks/workloads/large-response-model-asgi.yaml`: `d489474f1e47f200813b1b4a848117e03adab594cd1ffe8c131d37a7646f9693`.
- `tests/fixtures/inputs/parity/large-response-model.json`: `8659166f3530ff2ecc5239a4b01e2d9f6df9ddbb2b5d95437ea7c84da39b6e5c`.
- `tests/fixtures/input-recipes/parity/large-response-model.yaml`: `78b7d09d8c879e09076f9e3e1c716d394b0c3fc6ff9fddaaecdd091041de1ab2`.
- `tests/fixtures/workloads/large_response_model.py`: `1febb0026019df4ef1bb93722fbff4b5614f6b8ff8bd6e811e5aebefb291f802`.
- Benchmark declaration `benchmarks/workloads/repeated-sequence-query-asgi.yaml`: `da006d8bcf4aefaa9ade59e69765653d485b6b74abe32149e228a6114614de4d`.
- `tests/fixtures/inputs/parity/core-multi-query-errors-upstream.json`: `0152083cfc28e3ced57c2ccc1e860cb186b10cfca32a54d327365b9ce0c6433a`.
- `tests/fixtures/input-recipes/parity/core-multi-query-errors-upstream.yaml`: `c5e3412b511549ec69987f4e41df60f5ed5ad4c22711a9cbe6068b0d658e0ae7`.
- `tests/fixtures/workloads/core_multi_query_errors_upstream.py`: `d13b768fc2499dc7717365c7be504c99f13c6ca3e6bfb00e68797eabc2ba3689`.

## Freeze

All admission and measurement records remain unchanged by this audit. The source/native equality statement is tied to the saved post-suite proof and the independent pre-documentation closing readback. Later evidence documentation changes are outside the measured full source digest. The next OpenAPI 3-case/19-action proposal remains private and inactive; it contributes no passing behavior or performance evidence here.
