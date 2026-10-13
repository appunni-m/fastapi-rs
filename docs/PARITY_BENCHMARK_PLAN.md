# FastAPI-RS parity and benchmark plan

This plan defines how to establish behavioral and performance evidence for
FastAPI-RS. It assumes Starlette-RS will be a full Starlette replacement and
does not include implementing or benchmarking Starlette-RS itself.

## Reference and target boundary

Use the released FastAPI **0.141.1** source at commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` with **Starlette 1.6.0 only**, at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. FastAPI declares
`starlette>=0.46.0`, which admits this selected contract. Pin Pydantic 2.13.4,
pydantic-core 2.46.4, AnyIO 4.12.1, the Python patch, and all other
behavior-relevant package versions in each run identity. FastAPI's benchmark
CI uses CPython 3.13; `.python-version` in the source tag is 3.11, so choose
and record the benchmark runtime explicitly rather than inheriting the
developer's interpreter. Keep additional supported-Python profiles separate;
do not add a second Starlette version profile.

Optional-feature workflows record package overlays separately from the core
identity. The multipart lane adds `python-multipart` 0.0.32 from the locked
standard environment; FastAPI, Pydantic, Python, and Starlette remain pinned to
the same versions.

The target profile is the **FastAPI-RS Python consumer surface**: user code
builds the app, routes, endpoint callables, and Pydantic models through
FastAPI-RS's public `fastapi` import. It is one FastAPI implementation:
`fastapi-rs` owns its behavior and control flow, while `fastapi-rs-py` is the
thin PyO3 packaging and boundary-conversion crate. The Python facade forwards
to that implementation; parity and benchmarks have one FastAPI-RS target.
Upstream FastAPI is source-oracle/dev-only and must not be an installed runtime
dependency or imported by the target process. FastAPI-RS uses Starlette-RS for
the generic Starlette contract. Run the target in a separate
process/environment from upstream FastAPI because both use the `fastapi`
import namespace and must not share imported modules or mutable application
state. Verify the target revision, build, Python ABI, feature set,
Pydantic/pydantic-core versions, and exact Starlette-RS revision before running
a case. `make parity-prepare-target` builds the extension with Cargo's release
profile; the target worker verifies that Cargo's resolved Starlette-RS crate
and the editable Python distribution point to the same clean pinned checkout.

The FastAPI contract owns FastAPI exports and behavior: route registration and
dependency interpretation, parameter extraction, validation/serialization
wiring, FastAPI exception mapping, OpenAPI/docs generation, and its
integration of HTTP, WebSocket, and lifespan operations. Starlette-RS's own
contract owns the generic Starlette APIs and primitives. FastAPI workflows
must still exercise these primitives through FastAPI so integration and
cross-layer regressions are visible; the FastAPI manifest should not duplicate
Starlette's entire public denominator. Benchmarks and parity exercise the same
Python consumer surface; Rust-only microbenchmarks are not FastAPI parity or
consumer-surface benchmark results.

## Parity suite

The first twelve-case HTTP request/response slice now has a Rust-owned target,
pass-through `fastapi` facade, isolated workers, and an exact comparator. The
`make parity-first-slice` command runs both pinned products and stores the
comparison in ignored `parity-results/`; CI runs this gate. This only validates
the current first slice. It does not establish broader API or feature parity.

Direct Python callable probes also have isolated source and target workers, a
versioned result schema, and an exact comparison command. The initial
`encoding.yaml` workflow observes JSON-encoder return values and signatures; run it with
`make parity-api-oracle`, `make parity-api-target`, then
`make parity-api-compare SOURCE_RESULT=... TARGET_RESULT=...`. Its nine cases
are a narrow direct-call slice and do not establish the rest of the public API.

Workflow v2 also reads non-callable public attributes through the same
identity-checked workers. A `public_attribute` probe emits a
`python_attribute_value` observation only when the value is strict JSON, so
the source and target values compare exactly. The input-only
`fastapi-version-value.yaml` case exercises `fastapi.__version__` without
embedding the oracle value in the recipe. Its `upstream_api_definition`
evidence binds that public symbol to the digest-pinned definition in
`fastapi/__init__.py`; definition evidence does not claim fixture-matrix
coverage.

Keep the complete FastAPI public inventory in the one project manifest and
make every parity case reference a public operation and semantic requirement.
Use input files as executable stimuli only: app/route setup, ordered public
actions, arguments, deterministic assets, selected observations, and target
profiles. Do not store expected status codes, response bodies, schemas, error
messages, or oracle outputs in fixtures. Each isolated worker executes the
same workflow against its live public implementation and emits the same
structured result interface. A host runner checks source and target identity,
matches case/step IDs, then compares public success/error status and declared
observations. Missing, skipped, partial, or unsupported behavior remains
visible and cannot pass.

Where the public contract permits exact comparison, compare exact values,
including HTTP status, response bytes, headers, cookies, WebSocket messages,
and lifecycle event order. Compare OpenAPI as structured JSON while retaining
observable fields such as paths, operations, schemas, references, security,
responses, and extensions. Error observations should include public error
class, status, structured validation details, and message when stable. Use a
normalization only when it is reusable, justified by the public contract, and
declared once in the comparison policy. Never normalize away a real
compatibility difference or accept an unspecified error as equivalent.

Build requirements and workflows across these feature groups:

| Feature group | Representative parity dimensions |
| --- | --- |
| App and routing | app/router construction, route inclusion, prefixes, tags, dependencies, operation metadata, custom route classes, mounts/sub-applications, route order and conflicts |
| HTTP inputs | path/query/header/cookie parameters; aliases and defaults; required/invalid values; JSON/body fields and nested models; forms/files/uploads; scalar and collection constraints |
| Dependency injection | nested and shared dependencies, overrides, caching, sync/async callables, request/response injection, security scopes, yield cleanup and error propagation |
| Outputs and errors | response models and filtering, aliases/exclusion flags, model/dict returns, direct/custom responses, status/headers/cookies, background task wiring, request and response validation failures, exception handlers |
| OpenAPI and docs | cold and cached schema, operation IDs, models/references, request/response schemas, security, callbacks/webhooks, deprecation, custom schema changes, `/docs`, `/redoc`, and `/openapi.json` configuration |
| WebSocket and lifecycle | endpoint dependencies and validation, accept/receive/send/close/error sequences, lifespan startup/shutdown ordering, and event-handler compatibility |
| Public surface | documented exports, aliases, signatures/defaults, deprecated names, constants, helper functions, and supported Starlette re-exports as defined by the FastAPI inventory |

Fixtures should cover successful and failing inputs, defaults and boundaries,
representative types, sync and async execution, and interactions between
features. Include an observation only when it is part of the behavior being
specified. Arbitrary user Python callables and Pydantic model declarations
must be built through shared, reviewed workload definitions and passed through
the public interface; the runner must not branch on case IDs or call private
target internals to manufacture compatibility.

### Execution and evidence

- Keep oracle and target environments, working directories, temporary files,
  and application state isolated. The orchestration process may compare
  result artifacts but must never load both implementations into one worker.
- Verify the oracle package version, source commit, runtime, and dependency
  identity at startup. Verify target revision/build/profile similarly. A
  startup failure, timeout, crash, malformed result, duplicate/missing case,
  or count mismatch is infrastructure failure, not a FastAPI behavior error.
- Invoke each product through its consumer-facing Python API. Adapters may
  encode values, map public values/errors to the result protocol, and manage
  handles; they must not reimplement FastAPI semantics.
- Store immutable run artifacts outside the input tree with manifest/input/
  asset digests, identity details, command, raw observations (or references),
  comparisons, and infrastructure errors. Inputs describe work; results
  describe what happened.
- Report parity per case and target profile, with explicit pass, fail, or
  not-run. Do not turn unsupported cases or unrun requirements into passes.

## Benchmark plan

Revision-specific observations are recorded in
[the 2026-10-05 measurements at 76dedd6](benchmarks/2026-10-05-76dedd6.md).
These include the slower workloads and apply only to the measured revision.

### First executable lane

`benchmarks/workloads/first-slice-valid-asgi.yaml` defines the first runnable
measurement. `make benchmark-first-slice` rebuilds the pinned target extension
with Cargo's release profile, runs the complete twelve-case identity-checked
parity gate, then measures the valid item request in three
isolated processes: FastAPI 0.141.1 with Starlette 1.6.0, the FastAPI-RS release
extension with the pinned Starlette-RS source, and a plain Starlette 1.6.0
route/response control. The untimed output must match exactly across all three
subjects before timing proceeds.

Per-request latency measures one direct ASGI call, timed only around
`await app(scope, receive, send)`. App construction, scope/event setup,
interpreter startup, HTTP client, and network are outside that latency timer;
the Python facade, PyO3/native dispatch, application, validation, response
serialization, and captured ASGI sends are inside. Sequential request-loop
throughput uses a wider timer that also includes scope copies, callback
construction, response signature extraction and equality checks, and loop
bookkeeping. It is a harness-level rate, not app-only throughput. The runner
uses 50 warmups and 1,000 measured samples in five rounds and retains every
latency sample. The Starlette control is contextual and its time is never
subtracted from FastAPI.
Each artifact stores workload/input digests, fresh parity evidence, source
revisions, Python/host identity, Cargo profile/features, and Rust/Cargo versions
under ignored `benchmark-results/`.

This is a first-slice baseline only. It does not replace the upstream TestClient
benchmark suite or establish performance parity beyond the measured request.

The repeated-sequence-query lane is also executable after its three-action
identity-checked workflow passes. Run
`make benchmark-first-slice BENCHMARK_WORKLOAD=benchmarks/workloads/repeated-sequence-query-asgi.yaml`
to time only the valid `q=5&q=6` request while gating against the complete
multi-query case, including invalid-value aggregation and OpenAPI parity. It
compares FastAPI with FastAPI-RS directly; Starlette is omitted because it does
not own FastAPI's repeated-query list validation behavior.

### Required direct-ASGI workload suite

`make benchmark-suite STARLETTE_RS_SOURCE=/path/to/clean/starlette-rs` runs the
reviewed seven-workload set in a fixed order. The contract check rejects missing,
renamed, or additional declarations until the suite denominator is reviewed.
Before building, the runner verifies the FastAPI, Starlette, and Starlette-RS
source revisions against their current manifest pins. FastAPI-RS must have a
clean working tree; its current HEAD is recorded per run because the manifest
does not pin a FastAPI-RS commit. Each workload then runs its own fresh
full-workflow parity gate and release measurement. A completed suite summary is
emitted only if every declaration has a new valid result and all results share
source revisions, FastAPI-RS target artifact, Python, host, and build identities. A
versioned suite record references each per-workload artifact by path and
SHA-256. `make benchmark-contract-check` validates the suite schema and every
saved suite-to-result reference. If preflight, a workload, or identity
aggregation fails, an incomplete suite record captures completed, failed, and
not-run workload outcomes along with any available identities. Use
`STARLETTE_RS_SOURCE` for a clean detached worktree at its pinned revision if
the sibling development checkout is dirty.

Start with FastAPI's own workloads in `tests/benchmarks/` and
`tests/memory_benchmarks/` at the pinned tag. This preserves comparisons to
FastAPI's established work while the additional workloads isolate costs that
the upstream suite does not measure. Upstream has 20 in-process request
benchmarks, one OpenAPI generation benchmark, and three memory benchmarks.

Measure three subjects where the workload supports them: FastAPI 0.141.1 with
Starlette 1.6.0, FastAPI-RS through its public Python `fastapi` import with
Starlette-RS, and a raw Starlette 1.6.0 control. The FastAPI-RS result measures
the complete pass-through Python/PyO3/Rust call path; never substitute the
upstream FastAPI package inside the target runtime. The control should use
Starlette's public routing and response APIs for a plain route with the same
request and response bytes. Treat it as context for the generic ASGI/HTTP
path; it does not implement FastAPI validation, dependency injection,
response-model filtering, or OpenAPI behavior. Keep its results separate and
do not subtract them from FastAPI timings as a claimed FastAPI-only cost. Only
compare FastAPI to FastAPI-RS for workloads whose behavioral parity gate
passes.

The implemented suite currently measures seven direct-ASGI workloads through
the isolated FastAPI Python consumers. Each run gates the full selected
workflow, performs an untimed response check, then records 50 warmups and five
rounds of 200 sequential samples per subject. Per-request latency starts at
`await app(scope, receive, send)`: app construction, interpreter startup, and
per-call ASGI scope/callback setup are outside that timer. The target timing
includes its public `fastapi` facade, PyO3 conversion, Rust FastAPI-RS code,
Pydantic work, and Starlette-RS dispatch as one combined path. The current
results do not separate those components and do not measure a loopback HTTP
server. Internal Rust timing attribution may be added as a measurement of this
same implementation; it is not a separate target. Do not infer component costs
by subtracting the Starlette control or from the end-to-end target time.

#### Current completed seven-workload run (2026-10-13; current manifest)

The suite completed at `2026-10-13T19:30:07Z` with suite ID
`62b84e96-4d6d-4284-9f70-b6bf142a4aa7` and receipt
`benchmark-results/suite-20261013T193007Z-62b84e96-4d6d-4284-9f70-b6bf142a4aa7.json`
(SHA-256 `77541f828135f89b3fc77baaa2ac8152dcb19bc20952e104927a54d9e4233064`).
It binds manifest SHA-256
`9ecbd9e9ab4ec497a7e9febd4d5b6d3716c0c2660f208a5719c90371ad3f01e9`,
FastAPI-RS commit `cb1352a4cc5a127ee5a9e1236d6c556c3e8027e8`, FastAPI
`0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette `1.6.0`
at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven workloads completed, and their fresh
identity-checked gates passed 42/42 selected observations with zero failures
and zero not-run cases. Each subject used 50 warmups and 1,000 measured calls
in five rounds. The target extension SHA-256 was
`7b8a6d666ffdc724dddcbc17e124642c8e4eb2e3ee8307f2e5e6b8842a953a1e`; the
target binary SHA-256 was
`31c86756a57393c9d4675634f45eda1239311f190cbb9ecb9d4689af8ba926db`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity |
| --- | ---: | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 492.4 / 513.1 µs | 656.1 / 728.9 µs | 1.333x / 1.421x | 2/2 |
| Async nested dependencies, two query parameters | 405.0 / 424.9 µs | 626.1 / 691.4 µs | 1.546x / 1.627x | 2/2 |
| Chunked request body | 133.5 / 139.5 µs | 139.6 / 157.3 µs | 1.046x / 1.128x | 12/12 |
| Invalid request | 144.8 / 210.1 µs | 320.9 / 346.9 µs | 2.216x / 1.651x | 12/12 |
| Valid request | 132.5 / 139.0 µs | 137.9 / 153.1 µs | 1.041x / 1.102x | 12/12 |
| Large response model | 358.5 / 373.6 µs | 386.0 / 431.7 µs | 1.077x / 1.156x | 1/1 |
| Repeated sequence query | 94.1 / 104.1 µs | 104.8 / 123.3 µs | 1.114x / 1.185x | 1/1 |

FastAPI-RS had higher median latency on all seven workloads in this run. The
largest gap was invalid-request handling; the two nested-query workloads were
also slower than the previous revision-specific run. This is one host and a
narrow direct-ASGI suite, not a global performance claim. It does not measure
network/server latency or separate facade, PyO3, Rust, Pydantic, or
Starlette-RS costs. The Starlette control remains contextual and is not
subtracted from FastAPI timings. `make benchmark-contract-check` passed after
older suite receipts tied to earlier manifests were retained under
`benchmark-results/stale/`.

#### Completed seven-workload run (2026-10-13; archived stale manifest)

The suite completed at `2026-10-13T04:09:04Z` with suite ID
`3bc888b0-18e3-439b-8c33-891ef5c8d081` and receipt
`benchmark-results/stale/suite-20261013T040904Z-3bc888b0-18e3-439b-8c33-891ef5c8d081.json`
(SHA-256 `88d734af83a735173a1707df453650f1715476b2c3ee4fec78a738e873d10ce1`).
Its comparison artifacts use manifest SHA-256
`06e3652d0154dd0c6717b2c698d5978a6b3f40669d90f24e396591806104b73c`, while
the current manifest is `f56d38c4d19e7b5440495b81410409b751a3041b3b070bf774502bde341e59dc`.
The suite receipt is archived as historical evidence and is not current-contract
benchmark evidence; its referenced workload artifacts remain in place.
It ran against FastAPI-RS commit `43aee0f2c73087a94696dac8387d275cb9d5b27f`
and manifest SHA-256
`06e3652d0154dd0c6717b2c698d5978a6b3f40669d90f24e396591806104b73c`.
The source identities are FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven workloads completed; all selected parity
gates passed (42/42 comparisons, zero failed, zero not-run). Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was
`7b47d5b218203cf84e73c43a5e979e5a3535c86b6d94ea4caa5db75e936808ac`; the
target binary SHA-256 was
`49669189f42cca7490da2a14be60e5d2efc56f4e2cbfcf3e0fedacb8fe07f442`.

The table reports median and p95 direct-ASGI latency in microseconds; ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and identity details remain in the ignored
suite and workload receipts referenced above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio |
| --- | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 491.4 / 516.0 µs | 307.1 / 338.2 µs | 0.625x / 0.655x |
| Async nested dependencies, two query parameters | 442.7 / 660.4 µs | 303.7 / 572.0 µs | 0.686x / 0.866x |
| Chunked request body | 137.5 / 171.9 µs | 145.2 / 205.4 µs | 1.056x / 1.195x |
| Invalid request | 146.8 / 224.2 µs | 326.7 / 451.0 µs | 2.225x / 2.012x |
| Valid request | 135.5 / 175.3 µs | 143.4 / 202.2 µs | 1.058x / 1.153x |
| Large response model | 367.9 / 461.6 µs | 403.6 / 534.3 µs | 1.097x / 1.158x |
| Repeated sequence query | 102.9 / 129.0 µs | 114.2 / 153.9 µs | 1.109x / 1.193x |

FastAPI-RS had lower median latency on the two nested-query workloads and
higher median latency on the other five, with the largest median gap on
invalid-request handling. This single-host direct-ASGI run does not measure
network/server latency or isolate facade, PyO3, Rust, Pydantic, and Starlette-RS
costs. It is a narrow workload suite, not a full FastAPI performance claim.
The Starlette control remains contextual and is not subtracted from FastAPI
timings.

#### Previous completed seven-workload run (2026-10-13; stale manifest; archived)

The suite completed at `2026-10-13T02:45:45Z` with suite ID
`f601c4c1-b599-43df-a56b-35eaca114cd5` and receipt
`benchmark-results/stale/suite-20261013T024545Z-f601c4c1-b599-43df-a56b-35eaca114cd5.json`
(SHA-256 `6dd11aefc53715d9f5774439077ced8c49193dc3b0b69176c9134fe4e94d5f14`).
It ran against FastAPI-RS commit `7f5145f7c74c1e42dea00db3d4cb77fd9115ec53`
and manifest SHA-256
`3c687cc307e36558fe25044cc8740d2e3a8589fc71b295539e153fb9b243ec24`.
The source identities are FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. The run used CPython 3.12.13,
macOS 15.7.7 arm64 (12 logical CPUs), Cargo/rustc 1.98.1, and the optimized
release profile with `pyo3/extension-module`. All seven workloads completed;
all selected parity gates passed (42/42 comparisons, zero failed, zero
not-run). Each subject used 50 warmups and 1,000 measured calls in five rounds.
The target extension SHA-256 was
`7b47d5b218203cf84e73c43a5e979e5a3535c86b6d94ea4caa5db75e936808ac`; the
target binary SHA-256 was
`49669189f42cca7490da2a14be60e5d2efc56f4e2cbfcf3e0fedacb8fe07f442`.

The table reports median and p95 direct-ASGI latency in microseconds; ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and identity details remain in the ignored
suite and workload receipts referenced above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio |
| --- | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 500.5 / 508.8 µs | 307.9 / 319.0 µs | 0.615x / 0.627x |
| Async nested dependencies, two query parameters | 422.9 / 441.7 µs | 281.0 / 297.7 µs | 0.664x / 0.674x |
| Chunked request body | 134.4 / 140.0 µs | 142.7 / 168.0 µs | 1.062x / 1.200x |
| Invalid request | 144.8 / 210.6 µs | 319.1 / 331.3 µs | 2.204x / 1.573x |
| Valid request | 134.5 / 139.6 µs | 137.3 / 158.0 µs | 1.021x / 1.132x |
| Large response model | 363.0 / 386.8 µs | 385.1 / 409.6 µs | 1.061x / 1.059x |
| Repeated sequence query | 99.2 / 104.9 µs | 110.2 / 126.1 µs | 1.112x / 1.202x |

FastAPI-RS had lower median latency on the two nested-query workloads and
higher median latency on the other five. This single-host direct-ASGI run
does not measure network/server latency or isolate facade, PyO3, Rust, Pydantic,
and Starlette-RS costs. `make benchmark-contract-check` passed after the older
suite receipt, whose comparisons reference a prior manifest, was moved under
`benchmark-results/stale/`. The prior completed run is retained below as
historical evidence only.

#### Previous completed seven-workload run (2026-10-13; stale manifest)

The suite completed at `2026-10-13T01:56:24Z` with suite ID
`dc3222f3-f075-42a0-9648-2f0271c6fe5e` and archived receipt
`benchmark-results/stale/suite-20261013T015624Z-dc3222f3-f075-42a0-9648-2f0271c6fe5e.json`
(SHA-256 `7c44fc0b9bf79cb3da97b52b69b3b6333f45786c793eff5dc6dfd7b2b6e94779`).
It ran against FastAPI-RS commit `adef6a0ffcce0a2b2fd1ca71bc71adaa513555e0`
and manifest SHA-256
`b1db20de747cd2ae4d4f39212ab774f449afd3e50a40ff6779011a74dcac14f0`.
The receipt is archived because its comparison artifacts reference an older
manifest; retain it as historical evidence only.
The source identities are FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. The run used CPython 3.12.13,
macOS 15.7.7 arm64 (12 logical CPUs), Cargo/rustc 1.98.1, and the optimized
release profile with `pyo3/extension-module`. All seven workloads completed;
all selected parity gates passed (42/42 comparisons, zero failed, zero
not-run). Each subject used 50 warmups and 1,000 measured calls in five rounds.
The target extension SHA-256 was
`cfdc64a5343715e02eac44b6c2c88a13aea75a8a2d1fe31893569d442ec1e6ce`; the
target binary SHA-256 was
`ff88fc1417a7edf5f4615d4404e700c8161a45ba60737e5e38994a79bccffbd1`.

The table reports median and p95 direct-ASGI latency in microseconds; ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. The raw samples and identity details remain in the ignored
suite and workload receipts linked above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio |
| --- | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 508.9 / 721.9 µs | 316.4 / 443.5 µs | 0.622x / 0.614x |
| Async nested dependencies, two query parameters | 421.7 / 737.2 µs | 294.2 / 535.9 µs | 0.698x / 0.727x |
| Chunked request body | 137.3 / 176.5 µs | 144.7 / 196.3 µs | 1.054x / 1.112x |
| Invalid request | 149.6 / 251.3 µs | 334.0 / 627.3 µs | 2.233x / 2.496x |
| Valid request | 134.0 / 186.7 µs | 144.6 / 215.2 µs | 1.079x / 1.152x |
| Large response model | 367.8 / 635.8 µs | 430.9 / 1783.5 µs | 1.172x / 2.805x |
| Repeated sequence query | 103.6 / 139.8 µs | 114.9 / 156.1 µs | 1.109x / 1.117x |

FastAPI-RS had lower median latency on the two nested-query workloads and
higher median latency on the other five. The large-response-model p95 is
2.805x the FastAPI p95 on this host; raw samples remain in the workload
receipt for inspection. These single-host direct-ASGI results do not measure
network/server latency or isolate native Rust time. The preceding 14:48Z
suite is retained below as historical evidence.

#### Earlier completed seven-workload run (2026-10-12; suite schema v2)

The prior suite completed at `2026-10-12T14:48:16Z` with suite ID
`a5f2aaff-8460-45ed-b82a-c78517006bf6` and receipt
`benchmark-results/stale/suite-20261012T144816Z-a5f2aaff-8460-45ed-b82a-c78517006bf6.json`.
It ran against FastAPI-RS commit `a68e09a5a39a2d4c20b6d742d8a2be5cd6a8ec46`
and manifest SHA-256
`b0871654e15f2d3a4064b8e2b24bce3660b52b86d4f6d702924d59cc43c92815`.
The receipt is archived because its manifest hash no longer matches the
current benchmark contract; it is retained as historical evidence only.
The source identities were FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
macOS 15.7.7 arm64 (12 logical CPUs), Cargo/rustc 1.98.1, and the optimized
release profile with `pyo3/extension-module`. All seven parity gates passed
(42/42 comparisons); each subject used 50 warmups and 1,000 measured calls in
five rounds. Its results remain below for historical comparison.

#### Historical stale-manifest run (2026-10-12; suite schema v2)

This run completed at `2026-10-12T12:34:22Z` with suite ID
`2a7f56cb-f01b-427b-a9c4-2817954131ce`. Its preserved receipt is archived at
`benchmark-results/archive/stale-manifest-20261012/suite-20261012T123422Z-2a7f56cb-f01b-427b-a9c4-2817954131ce.json`.
It ran against FastAPI-RS commit `979909ffddd8cc47d461980ead1b2fee6dff0a15`
and manifest SHA-256
`c961e13a1ce310b6913f785af0772c54972fe78dbb916558cea2b6c3f6d0c937`.
The suite remains historical evidence; the later optional query-list fixture
changed the manifest, so its comparison does not satisfy the current benchmark
contract. It passed all seven parity gates (42/42), with 50 warmups and 1,000
measured calls in five rounds.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio |
| --- | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 506.6 / 521.8 µs | 317.2 / 332.7 µs | 0.626x / 0.638x |
| Async nested dependencies, two query parameters | 412.6 / 424.8 µs | 268.4 / 285.1 µs | 0.650x / 0.671x |
| Chunked request body | 135.2 / 146.4 µs | 142.8 / 164.7 µs | 1.056x / 1.125x |
| Invalid request | 147.5 / 220.6 µs | 323.9 / 387.3 µs | 2.195x / 1.755x |
| Valid request | 134.3 / 146.4 µs | 142.9 / 168.9 µs | 1.064x / 1.154x |
| Large response model | 369.4 / 407.8 µs | 394.4 / 437.6 µs | 1.068x / 1.073x |
| Repeated sequence query | 102.3 / 120.9 µs | 118.0 / 152.1 µs | 1.154x / 1.258x |

#### Earlier same-day run (2026-10-12; suite schema v2)

This earlier same-day run completed at `2026-10-12T09:20:04Z` with suite ID
`263a98eb-9af5-4c4e-9572-96d86853af9a`. Its archived receipt is
`benchmark-results/archive/stale-manifest-20261012/suite-20261012T092004Z-263a98eb-9af5-4c4e-9572-96d86853af9a.json`.
It used FastAPI-RS commit `98fd2eb6390bf8aededa9d658eed9b7e9365ab45` and
manifest SHA-256
`2f7360d4da3cc3871f49f0b12c92f89f0bffb0bd7f1c590b21dd3e66b6d8d172`, which
is historical and differs from the current manifest. FastAPI 0.141.1,
Starlette 1.6.0, Starlette-RS `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`,
CPython 3.12.13, macOS 15.7.7 arm64, and Cargo/rustc 1.98.1 were unchanged.
The run passed all seven parity gates (42/42); each subject used 50 warmups
and 1,000 measured calls in five rounds.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio |
| --- | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 493.4 / 520.6 µs | 307.2 / 335.4 µs | 0.623x / 0.644x |
| Async nested dependencies, two query parameters | 409.4 / 439.5 µs | 267.0 / 288.2 µs | 0.652x / 0.656x |
| Chunked request body | 136.1 / 156.2 µs | 153.6 / 475.7 µs | 1.129x / 3.044x |
| Invalid request | 143.7 / 208.9 µs | 316.3 / 346.2 µs | 2.202x / 1.658x |
| Valid request | 129.6 / 144.0 µs | 140.2 / 165.8 µs | 1.082x / 1.151x |
| Large response model | 360.8 / 381.0 µs | 385.1 / 418.4 µs | 1.067x / 1.098x |
| Repeated sequence query | 93.8 / 106.0 µs | 108.4 / 125.7 µs | 1.155x / 1.186x |

FastAPI-RS was faster on the two nested-query workloads and slower on the other
five. This single-host direct-ASGI result is historical; it does not measure
network/server latency or isolate native Rust time.

#### Historical seven-workload run (2026-10-05; suite schema v2)

The run completed at `2026-10-05T15:59:05Z` with suite ID
`1835834f-5295-4952-bde3-cfd742f6f608`. Its archived record is
`benchmark-results/archive/d508878-before-inline-query-schema-wire/suite-20261005T155905Z-1835834f-5295-4952-bde3-cfd742f6f608.json`.
It used FastAPI-RS commit `d50887853d382bd9d9e03c7e82a504614ff02aba`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS at
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It ran on CPython 3.12.13,
macOS 15.7.7 ARM64 (12 logical CPUs), with Cargo 1.98.1 release profile and
`pyo3/extension-module`. All seven workload parity gates passed. Each subject
used 50 warmups and 1,000 measured calls in five rounds.

The table reports median and p95 direct-ASGI latency in microseconds; ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio |
| --- | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 517.2 / 584.8 µs | 326.2 / 384.0 µs | 0.631x / 0.657x |
| Async nested dependencies, two query parameters | 437.6 / 486.5 µs | 288.4 / 313.2 µs | 0.659x / 0.644x |
| Chunked request body | 134.6 / 149.4 µs | 142.2 / 169.9 µs | 1.056x / 1.137x |
| Invalid request | 150.1 / 226.2 µs | 338.8 / 396.2 µs | 2.257x / 1.752x |
| Valid request | 135.4 / 157.0 µs | 139.9 / 162.1 µs | 1.033x / 1.033x |
| Large response model | 373.2 / 620.6 µs | 404.1 / 473.7 µs | 1.083x / 0.763x |
| Repeated sequence query | 98.3 / 122.6 µs | 126.3 / 229.7 µs | 1.284x / 1.873x |

These are single-host direct-ASGI results; they do not measure network/server
latency or isolate native Rust time. This is retained historical evidence; its
target revision and manifest identity do not match the current checkout. The
earlier six-workload run (`c98c3402-28d7-4c87-9c66-e4ab1717de2f`) remains
historical too.

An earlier exploratory warm-request call profile of the invalid workload
counted four `TypeAdapter` constructions in FastAPI-RS and none in FastAPI
after each app was constructed. FastAPI-RS currently calls
`TypeAdapter(annotation)` inside
`validate_python_value` for each validated input
(`fastapi-rs/src/application_runtime.rs`); this identifies repeated adapter
setup as an optimization candidate, but does not establish how much of the
`2.195x` median ratio for invalid requests in the latest run it causes. After
the public operation contract is complete, measure per-parameter adapter reuse
on the full boundary, including dependency overrides, and retain the invalid
error-body parity gate.

| Tier | Workload | Timing boundary and purpose |
| --- | --- | --- |
| 1. Request path | Preserve sync/async input-model validation; small dict/model output with and without `response_model`; nested dependencies; large request payload; and large dict/model response with and without `response_model`. The upstream large response contains 300 items with 25 integers each plus metadata. Add a plain-route control implemented with Starlette 1.6.0's public `Route` and response APIs. | Match upstream's in-process `TestClient` path. Construct the app and client outside the timed request; exclude the one warmup request. Keep the raw Starlette control to the same simple request/response work; it is not a feature-equivalent FastAPI comparison. This is an integrated Python/ASGI/client measurement, not network-server latency. |
| 2. OpenAPI | Preserve the upstream graph: 20 routes sharing a 101-dependency chain, with query parameters discovered from the graph. | Measure cold generation by clearing the schema cache then calling `app.openapi()`. Keep route/app construction outside the measured function, as upstream does. Add warm cached lookup as a separate workload. |
| 3. Construction and memory | Preserve route dependency graph construction (20 routes) and the graph with 50 endpoint parameters and 100-deep dependencies. Measure application setup, route registration, and retained/peak memory in distinct workloads. | Time construction only when it is the declared workload. Report memory separately from latency and identify whether app creation, OpenAPI generation, or request execution is inside the measurement. |
| 4. ASGI/server | Add direct in-process ASGI requests and loopback HTTP server runs only after the upstream-equivalent tier is stable. Include startup/shutdown, steady-state request latency, throughput, concurrency, and tail latency as separate declared measurements. | Use the same pinned server, client, transport, configuration, payload, machine class, and concurrency for source and target. Keep server start-up out of steady-state request timings; report it separately. |
| 5. Internal Rust attribution | If useful, instrument Rust-owned work within the same FastAPI-RS target and declare the boundary. | Keep the public Python `fastapi` path as the primary result. Report internal timing only as attribution within that path, never as a separate implementation or parity target. Do not infer it by subtracting from end-to-end time. |

For each workload, the input declares its subjects, exact work, measurement
boundary, measured steps, metrics, warmups, sample/iteration policy,
concurrency, cache state, environment requirements, and correctness gate.
Keep timings, memory samples, baselines, and budget outcomes in immutable
benchmark results, not in benchmark inputs or the manifest. Pin the compiler
and optimization profile for Rust runs and record CPU/OS, Python build, Rust
toolchain, enabled Cargo features, Starlette-RS revision, Pydantic versions,
and benchmark runner. Keep environment identity constant across paired runs;
mark evidence incompatible when it differs.

### Correctness gates and reporting

1. Run the selected live parity workflows for the exact source and target
   identities before timing. A parity failure, missing observation, unsupported
   workload, or infrastructure failure blocks that comparison's benchmark.
2. Perform an untimed correctness invocation using the benchmark workload and
   verify its status and output through the same public consumer surface. Keep
   that output check outside the timed region. Workloads must not silently
   skip validation, dependencies, response serialization, or schema work on
   one side.
3. For timed request workloads, verify the result after the measurement and
   preserve the raw result where practical. Report latency distributions and
   throughput from repeated samples; include warmups and sample counts.
   Collect allocation/peak/resident memory as distinct metrics and do not
   substitute them for latency.
4. Publish comparison results only for matching input digest, workload,
   feature set, boundary, and compatible environment. Store oracle and target
   measurements separately with a derived ratio and complete evidence links.
   No performance claim is valid when its correctness gate did not pass.

## Implementation order

### Essential foundation

1. Pin the FastAPI source revision and a reproducible oracle environment; pin
   each target build/profile independently. Establish the Python facade as the
   initial parity target.
2. Build the complete API inventory and one strict manifest/input index. Add
   structural validation for signatures, parameters, operations, requirements,
   input references, and public-surface-to-case mapping before creating a
   large fixture corpus.
3. Extend the current result protocol, identity handshake, process runner,
   public API adapters, and generic comparator to the reviewed manifest. The
   first HTTP vertical slice is already in place; add request construction,
   WebSocket, lifespan, and the remaining public behaviors as independently
   reviewed workflows.
4. Convert the pinned upstream request and OpenAPI benchmarks into
   input-described workloads, but do not record performance claims until a
   target exists, its relevant parity passes, and the measurement environment
   is controlled.

### Follow-on work

Expand the parity corpus to every manifest requirement and supported profile,
then add cross-version/platform matrices and managed coverage mapping. Add
performance budgets only after repeatable baselines exist. Add server/load,
concurrency, startup, allocation, and memory suites as separate workloads.
Generate specification and evidence-status documentation from the manifest
and compatible result artifacts, and fail CI on inventory drift, stale
evidence, incompatible identities, or hidden unsupported cases.

## Source pointers

- FastAPI release reference: `fastapi/`, `tests/`, `docs/en/docs/`, and
  `docs_src/` at commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Upstream request/OpenAPI workloads:
  `tests/benchmarks/test_general_performance.py`,
  `tests/benchmarks/test_openapi.py`, and `tests/benchmarks/utils.py`.
- Upstream memory workloads: `tests/memory_benchmarks/`.
- Upstream benchmark CI: `.github/workflows/test.yml` (CPython 3.13,
  CodSpeed simulation plus a memory run).
- Repository parity conventions: `AGENTS.md` and the migration-parity
  manifest/evidence contracts used by the project.
