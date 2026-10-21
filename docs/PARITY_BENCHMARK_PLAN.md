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

## Benchmark evidence freshness

The latest current-main, current-manifest measurement is the one-workload
[large-response-model refresh](benchmarks/2026-10-21-57aec8c.md). It passed
1/1 selected parity observations at FastAPI-RS
`57aec8ce9804f7e2c6284a18c86a5eeac5cf6008` with FastAPI 0.141.1, Starlette
1.6.0, and Starlette-RS `4139a72449bf5751e8902fb1c7175ee7f191d338`. Its
manifest SHA-256 is
`6fcf1c2a57e4a7bcd77a4ae3380b3777ec0932a9c4270644602dbf6d65257549`. This
refresh covers one of seven declared workloads only; the full suite remains
stale to the current manifest.

The latest completed seven-workload direct-ASGI suite is recorded in
[the 2026-10-21 report](benchmarks/2026-10-21-8c7eb97.md). It completed all
seven reviewed workloads and passed all 45 selected parity observations on
FastAPI-RS 8c7eb970cabd5fee871bc0a9fcf1691b9d4014f3, FastAPI 0.141.1 at
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f, Starlette 1.6.0 at
4f250d6b814587e20c5365f0a5f0c4d42bcb929f, and Starlette-RS
4139a72449bf5751e8902fb1c7175ee7f191d338. The fixture manifest SHA-256 is
f67678c11d87b35d56d5d5b04c78b40cf8251faeb9865e8b405cdc7aa296705b. Suite
receipt benchmark-results/suite-20261021T053534Z-3b38e3b4-06a9-4420-853d-2005a79921fa.json
has SHA-256
1a2715291047b44cf19ad9e83b0032693651d9bdf79375b525149b04753e785a.
FastAPI-RS median latency was higher in all seven workloads; p95 was higher in
six, with the distinct-query-alias workload's FastAPI p95 influenced by large
outliers. The report records identities, direct-ASGI boundaries, timing
policy, parity counts, and per-workload result paths. This selected workload
set was valid for its recorded revision but is historical to current main
because it binds the prior target and manifest. It does not establish full
FastAPI parity or a broader performance conclusion. The earlier same-day suite
is historical because it binds the previous target and manifest; its receipt is preserved under
benchmark-results/archive/stale-manifest-20261021-before-8c7eb97/.
The 2026-10-19 report remains historical because it binds an earlier target
and fixture manifest. Its suite receipt is archived at
`benchmark-results/archive/stale-manifest-20261019/suite-20261019T091804Z-650d1f09-bdaf-4cc3-b125-21c3ae0b7f33.json`.

The prior report [`2026-10-19-135805f.md`](benchmarks/2026-10-19-135805f.md)
is historical because it binds the previous manifest and target revision.

The prior suite report [`2026-10-19-8eceda6.md`](benchmarks/2026-10-19-8eceda6.md)
and its suite receipt are historical because they reference the previous
manifest and target revision. Earlier reports under `docs/benchmarks/` are
historical for the same reason. Re-run a workload only after its
identity-checked parity gate passes for the current target.

## Parity suite

The first thirteen-case HTTP request/response slice has a Rust-owned target,
pass-through `fastapi` facade, isolated workers, and an exact comparator. The
`make parity-first-slice` command runs both pinned products and stores the
comparison in ignored `parity-results/`; CI runs this gate. The latest
identity-checked first-slice comparison passed 13/13 at FastAPI-RS
`8c7eb970cabd5fee871bc0a9fcf1691b9d4014f3` with FastAPI 0.141.1, Starlette
1.6.0, and Starlette-RS `4139a72449bf5751e8902fb1c7175ee7f191d338`; comparison
receipt `parity-results/comparisons/ab90820d-cf0d-482c-8135-ffc422232ac3.json`
binds manifest SHA-256
`f67678c11d87b35d56d5d5b04c78b40cf8251faeb9865e8b405cdc7aa296705b`. This
validates only the declared first slice. It does not establish broader API or
feature parity. Broader parity remains incomplete.

Direct Python API workflows use isolated source and target workers, a versioned
result schema, and exact comparison. The 2026-10-14 receipt below contains one
selected case, `fastapi.testclient.public-api.alias-signature`, which failed
(0/1 passed). The source annotations `ASGIApp`, `Literal['asyncio', 'trio']`,
and `httpx._types.CookieTypes | None` appear as `Any`, `str`, and `Any` on the
pinned Starlette-RS target; the parameter names, defaults, and other signature
fields match. This single-case receipt makes no aggregate claim about other
workflows. It is not a complete public API parity result, and FastAPI-RS keeps
the direct alias boundary. The nine-case `encoding.yaml` workflow is one
covered slice, not the entire API surface.

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

Revision-specific observations are recorded in the
[2026-10-05 measurements at 76dedd6](benchmarks/2026-10-05-76dedd6.md), the
[2026-10-18 first-slice refresh at 9c8df51](benchmarks/2026-10-18-9c8df51.md),
and the [2026-10-19 first-slice refresh at 2a6d186](benchmarks/2026-10-19-2a6d186.md).
Each report applies only to the measured revision and workload.

### First executable lane

`benchmarks/workloads/first-slice-valid-asgi.yaml` defines the first runnable
measurement. `make benchmark-first-slice` rebuilds the pinned target extension
with Cargo's release profile, runs the complete thirteen-case identity-checked
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

### TestClient request lane

`benchmarks/workloads/testclient/testclient-sync-validated.yaml` follows the
pinned upstream `test_sync_receiving_validated_pydantic_model` scenario:
POST a JSON Pydantic model through a synchronous endpoint with a nested
dependency and response model. `make benchmark-testclient` gates the selected
schema-v12 TestClient parity case with fresh identity-checked oracle and target
runs, then measures the same `client.post(..., json=payload)` call and extracts
status/body using one reused TestClient context per subject. App construction,
TestClient construction, and lifespan startup/teardown are outside the latency
timer; HTTPX serialization, TestClient, in-process ASGI, FastAPI validation,
dependency execution, response serialization, and status/body extraction are
inside it. The TestClient profile pins HTTPX 0.28.1. This lane has a separate
workload/result contract and stays outside the fixed direct-ASGI suite. A plain
Starlette route cannot execute the FastAPI validation and dependency work in
this scenario, so results compare FastAPI 0.141.1 with FastAPI-RS only.

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

The configured suite contains seven direct-ASGI workloads through
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

#### Recorded seven-workload run (2026-10-14; historical target identity)

The suite completed at `2026-10-14T19:44:20Z` with suite ID
`5897d445-2b20-4c47-af92-7e33e2a90a93` and receipt
`benchmark-results/suite-20261014T194420Z-5897d445-2b20-4c47-af92-7e33e2a90a93.json`
(SHA-256 `42a680377778332505dbd0704effa035816db3d09246dad204a95fd5bf7f576b`).
Every parity comparison references the current manifest SHA-256
`ca8bce7b28f9ae38d134544762de8954154d9f7fbec465618cc5578290a64247`. The
suite binds FastAPI-RS commit `4ae3a354291e44a27c2a9384edf26ae0a4a15aa5`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo 1.98.1, rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed 45/45
selected observations with zero failures or not-run cases. Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `c108faea55f740fac202d2243d9a34042e090025e168557eee2705d43fea0da9`;
the target binary SHA-256 was
`a6a8017d5567b8d6fcd2ad8adef7bba441c9cf0e3c7d182ab40884aa04dfe8d4`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI; values above `1.0x` mean FastAPI-RS took
longer on this host. Each raw receipt is referenced below; the suite receipt
binds every workload receipt by SHA-256.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 485.5 / 497.3 µs | 653.4 / 694.2 µs | 1.346x / 1.396x | 2/2 | `benchmark-results/20261014T193601Z-72b30e90-d53c-434e-b268-c0681db3465f.json` |
| Async nested dependencies, two query parameters | 404.8 / 414.8 µs | 626.0 / 650.1 µs | 1.546x / 1.567x | 2/2 | `benchmark-results/20261014T193724Z-9c5245d0-b9c1-4e12-bb7b-a164ecbe360d.json` |
| Chunked request body | 124.3 / 133.9 µs | 132.8 / 148.7 µs | 1.068x / 1.110x | 13/13 | `benchmark-results/20261014T193847Z-0622ebe2-7242-43b2-9f4a-fa05ccacfbc9.json` |
| Invalid request | 141.2 / 208.0 µs | 301.5 / 328.3 µs | 2.135x / 1.578x | 13/13 | `benchmark-results/20261014T194009Z-82112777-b2bd-4416-982b-88360be068b6.json` |
| Valid request | 131.0 / 144.6 µs | 131.0 / 149.7 µs | 1.000x / 1.035x | 13/13 | `benchmark-results/20261014T194132Z-ad76a649-04c7-42cc-956f-c6a09a160c59.json` |
| Large response model | 358.3 / 383.7 µs | 384.0 / 425.0 µs | 1.072x / 1.108x | 1/1 | `benchmark-results/20261014T194257Z-38b51d8e-5f6c-4d52-9231-e91fc9abcb75.json` |
| Repeated sequence query | 98.1 / 113.0 µs | 107.1 / 125.9 µs | 1.092x / 1.114x | 1/1 | `benchmark-results/20261014T194420Z-66ef3599-f07a-4d51-b2fa-16d4be94d88e.json` |

FastAPI-RS had higher median latency on six workloads and higher p95 latency
on all seven. Invalid requests had the largest median and p95 ratios; the
valid-request median was effectively equal. This is a single-host
direct-ASGI result, not a global performance claim. It does not measure
network/server latency or separate facade, PyO3, Rust, Pydantic, or
Starlette-RS costs; no Starlette control is subtracted. Two incomplete suite
attempts caused by oracle-path and sandboxed-sccache setup failures remain
archived under `benchmark-results/stale/`; neither is parity evidence.

#### Previous completed seven-workload run (2026-10-14; commit faa8fa9; archived stale manifest)

The suite completed at `2026-10-14T18:40:27Z` with suite ID
`f5bf4476-767c-4af5-9dd0-0f8ddc656ccb` and receipt
`benchmark-results/stale/suite-20261014T184027Z-f5bf4476-767c-4af5-9dd0-0f8ddc656ccb.json`
(SHA-256 `e0175bd7c4c3e924c705fced77a9c10d7cce5c9234d981095c95d57909bd5db1`).
Every workload comparison binds that run's manifest SHA-256
`dcd93ae080080c1bd84bcc33d3b01259aedcacec550c74d29599cbc871e4a8b9`. The
suite binds FastAPI-RS commit `faa8fa9784ab760a70782906c403a45c29469b85`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo 1.98.1, rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed 45/45
selected observations with zero failures or not-run cases. Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `c108faea55f740fac202d2243d9a34042e090025e168557eee2705d43fea0da9`;
the target binary SHA-256 was
`a6a8017d5567b8d6fcd2ad8adef7bba441c9cf0e3c7d182ab40884aa04dfe8d4`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI; values above `1.0x` mean FastAPI-RS took
longer on this host. Each raw receipt is referenced below; the suite receipt
binds every workload receipt by SHA-256.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 490.5 / 507.2 µs | 658.4 / 694.1 µs | 1.342x / 1.368x | 2/2 | `benchmark-results/20261014T183210Z-9f82153c-fec8-4f4d-a165-184db8935318.json` |
| Async nested dependencies, two query parameters | 406.2 / 420.0 µs | 631.2 / 657.2 µs | 1.554x / 1.565x | 2/2 | `benchmark-results/20261014T183334Z-4541d734-c87c-4e92-923a-5bac48010530.json` |
| Chunked request body | 134.8 / 166.5 µs | 139.4 / 152.9 µs | 1.034x / 0.918x | 13/13 | `benchmark-results/20261014T183456Z-e130a58d-bff5-45c7-8ab8-e22cb805b8d4.json` |
| Invalid request | 144.7 / 218.3 µs | 327.9 / 344.4 µs | 2.266x / 1.578x | 13/13 | `benchmark-results/20261014T183618Z-72ac9108-2d5c-4291-81bb-207364e15b63.json` |
| Valid request | 132.5 / 137.7 µs | 137.5 / 157.1 µs | 1.038x / 1.141x | 13/13 | `benchmark-results/20261014T183740Z-26c3cf71-06d4-4fdc-bd83-a00a6c2c0290.json` |
| Large response model | 360.0 / 373.5 µs | 382.8 / 409.6 µs | 1.063x / 1.096x | 1/1 | `benchmark-results/20261014T183905Z-575d2d9d-6ddc-435e-8d21-331a476eba7c.json` |
| Repeated sequence query | 96.0 / 104.5 µs | 108.5 / 117.9 µs | 1.130x / 1.128x | 1/1 | `benchmark-results/20261014T184027Z-d3479ac5-61c5-4f59-b0e1-0d620bd3bce1.json` |

FastAPI-RS had higher median latency on all seven workloads. Its p95 latency
was lower only on chunked request bodies; invalid-request handling had the
largest median gap. This is a single-host direct-ASGI result, not a global
performance claim. It does not measure network/server latency or separate
facade, PyO3, Rust, Pydantic, and Starlette-RS costs. Starlette controls remain
contextual and are not subtracted from FastAPI timings. The
`make benchmark-contract-check` gate passed after the prior stale-manifest
suite receipt was archived under `benchmark-results/stale/`.

#### Previous completed seven-workload run (2026-10-14; commit bd54328; archived stale manifest)

The suite completed at `2026-10-14T17:26:09Z` with suite ID
`916f0da6-8fec-420d-9110-84c799d9efad` and receipt
`benchmark-results/stale/suite-20261014T172609Z-916f0da6-8fec-420d-9110-84c799d9efad.json`
(SHA-256 `2235e96064c5bbb28a133840152e0bd23f2dd25bf34fc3d086393b702a3ad397`).
Its workload comparisons bind the run's manifest SHA-256
`6bdf877e33c2d950aebd672a21ddfac7b6cf90757d1465c62b7b4fb3f5a81941`. The
suite binds FastAPI-RS commit `bd543282947f3f0526e344089a9be6cb082f5bd6`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo 1.98.1, rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed 45/45
selected observations with zero failures or not-run cases. Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `c108faea55f740fac202d2243d9a34042e090025e168557eee2705d43fea0da9`;
the target binary SHA-256 was
`a6a8017d5567b8d6fcd2ad8adef7bba441c9cf0e3c7d182ab40884aa04dfe8d4`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI; values above `1.0x` mean FastAPI-RS took
longer on this host. Each raw receipt is referenced below; the suite receipt
binds every workload receipt by SHA-256.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 485.8 / 501.9 µs | 663.8 / 691.5 µs | 1.366x / 1.378x | 2/2 | `benchmark-results/20261014T171748Z-35258def-a160-4c07-a19a-0cb51e65314c.json` |
| Async nested dependencies, two query parameters | 406.7 / 426.2 µs | 634.8 / 691.8 µs | 1.561x / 1.623x | 2/2 | `benchmark-results/20261014T171913Z-6356cdd5-0ff8-4cb9-bbd8-04ef8ed965b1.json` |
| Chunked request body | 130.2 / 138.7 µs | 140.9 / 170.4 µs | 1.082x / 1.229x | 13/13 | `benchmark-results/20261014T172036Z-e368b7f3-47af-4b40-80e3-23e5a637aa37.json` |
| Invalid request | 144.3 / 209.7 µs | 319.0 / 332.5 µs | 2.211x / 1.586x | 13/13 | `benchmark-results/20261014T172200Z-3a5882c2-e932-4647-8a70-727c6499d44a.json` |
| Valid request | 126.1 / 136.3 µs | 136.7 / 148.6 µs | 1.084x / 1.090x | 13/13 | `benchmark-results/20261014T172322Z-9dfb29fb-b3e6-40c2-8f63-ef74cfd8696e.json` |
| Large response model | 361.3 / 380.3 µs | 387.2 / 418.4 µs | 1.072x / 1.100x | 1/1 | `benchmark-results/20261014T172445Z-a8b9df4f-73d3-4d83-8e76-44c234e8b21e.json` |
| Repeated sequence query | 99.0 / 111.4 µs | 113.1 / 133.4 µs | 1.143x / 1.198x | 1/1 | `benchmark-results/20261014T172609Z-7bdee5b4-463d-4a3f-90bb-cc5821e6b7cf.json` |

FastAPI-RS had higher median and p95 latency on all seven workloads; invalid
requests had the largest median gap. This is a single-host direct-ASGI result,
not a global performance claim; it does not measure network/server latency or
separate facade, PyO3, Rust, Pydantic, or Starlette-RS costs. Starlette 1.6.0
controls remain contextual and are not subtracted from FastAPI timings.

#### Historical completed seven-workload run (2026-10-14; commit fbd71dd; stale manifest)

The suite completed at `2026-10-14T13:31:05Z` with suite ID
`ee508354-1cac-42f4-b5ee-3a34c0e09f6a` and receipt
`benchmark-results/stale/suite-20261014T133105Z-ee508354-1cac-42f4-b5ee-3a34c0e09f6a.json`
(SHA-256 `8336e61ffdf369f96f98e3ee3189638cd4607d2c73d1e69445e6d84a583557fe`).
Every workload comparison binds that run's manifest SHA-256
`d3ecf179662e9431af687579ccf5606081e0ce6d75a6b91984136d4a5c0d0ef7`. The
suite binds FastAPI-RS commit `fbd71dd58a83751a09c02b3e676c70f34d0e95c3`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed 45/45
selected observations with zero failures or not-run cases. Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `e2c157ef20cadbe79cd0c69375ec8c0d916498c400d3d902a5a3d297b576fd95`;
the target binary SHA-256 was
`c9e6ea51f61335da030d97335680577fa5914e55316d7a65b9c13885dde5329f`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI; values above `1.0x` mean FastAPI-RS took
longer on this host. Each raw receipt is referenced below; the suite receipt
binds every workload receipt by SHA-256.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 496.1 / 521.0 µs | 666.1 / 720.9 µs | 1.343x / 1.384x | 2/2 | `benchmark-results/20261014T132243Z-4a36ae20-68f9-4a73-87ae-b885f24c3624.json` |
| Async nested dependencies, two query parameters | 407.5 / 420.1 µs | 631.6 / 673.4 µs | 1.550x / 1.603x | 2/2 | `benchmark-results/20261014T132408Z-61d949ba-1b97-4f03-8355-0a091cb4b7e6.json` |
| Chunked request body | 133.2 / 138.5 µs | 140.6 / 152.9 µs | 1.055x / 1.104x | 13/13 | `benchmark-results/20261014T132531Z-71a4336a-29d7-41c1-98b0-070924b09171.json` |
| Invalid request | 144.4 / 212.6 µs | 321.9 / 343.0 µs | 2.229x / 1.613x | 13/13 | `benchmark-results/20261014T132655Z-cad3a259-a590-43c5-9240-5e05a8916b65.json` |
| Valid request | 126.8 / 138.1 µs | 141.6 / 174.6 µs | 1.117x / 1.264x | 13/13 | `benchmark-results/20261014T132818Z-5d369a94-bc71-460b-a2c1-4afe35d2d0ff.json` |
| Large response model | 361.7 / 383.0 µs | 384.5 / 421.3 µs | 1.063x / 1.100x | 1/1 | `benchmark-results/20261014T132942Z-fc5a8fc6-a1e0-4957-bd0f-0afcc825f499.json` |
| Repeated sequence query | 100.6 / 106.9 µs | 110.3 / 126.2 µs | 1.096x / 1.181x | 1/1 | `benchmark-results/20261014T133105Z-27d13fa3-e350-45b1-8ef8-a431b8731d7c.json` |

FastAPI-RS had higher median and p95 latency on all seven workloads; invalid
requests had the largest median gap. This is a single-host direct-ASGI result,
not a global performance claim; it does not measure network/server latency or
separate facade, PyO3, Rust, Pydantic, or Starlette-RS costs. Starlette 1.6.0
controls remain contextual and are not subtracted from FastAPI timings.

#### Previous completed seven-workload run (2026-10-14; commit 9dd48e5; stale manifest)

The suite completed at `2026-10-14T12:48:35Z` with suite ID
`6ca3d22d-72fe-4f15-b997-7f80dbe29af7` and receipt
`benchmark-results/stale/suite-20261014T124835Z-6ca3d22d-72fe-4f15-b997-7f80dbe29af7.json`
(SHA-256 `77834a2a9c4ab77d5287587438832f461bae6c42a26788bd70bdf7c13f4abd79`).
Each workload comparison binds manifest SHA-256
`2f57de585d287bcf8fca27caf098b8788a61124001262df3ab109ab173126cec`. The
suite binds FastAPI-RS commit `9dd48e562960d31d7e73156afd79c1053892447d`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed 45/45
selected observations with zero failures or not-run cases. Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `e2c157ef20cadbe79cd0c69375ec8c0d916498c400d3d902a5a3d297b576fd95`;
the target binary SHA-256 was
`c9e6ea51f61335da030d97335680577fa5914e55316d7a65b9c13885dde5329f`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI; values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced below.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 495.6 / 527.8 µs | 680.2 / 753.8 µs | 1.372x / 1.428x | 2/2 | `benchmark-results/20261014T124010Z-833e6ef5-37d8-4eb8-bf34-f253785ac3c9.json` |
| Async nested dependencies, two query parameters | 412.3 / 435.7 µs | 652.4 / 707.3 µs | 1.582x / 1.623x | 2/2 | `benchmark-results/20261014T124135Z-66227043-c994-48f5-b024-8bafd5c57a9d.json` |
| Chunked request body | 135.8 / 154.0 µs | 142.4 / 165.2 µs | 1.048x / 1.073x | 13/13 | `benchmark-results/20261014T124259Z-cbe8fac3-e4c9-4df2-a92e-82a71f035066.json` |
| Invalid request | 144.6 / 213.8 µs | 319.9 / 332.5 µs | 2.212x / 1.555x | 13/13 | `benchmark-results/20261014T124423Z-f3bc0017-0aaa-4c48-aa28-c2db5fd5b600.json` |
| Valid request | 136.6 / 156.7 µs | 139.9 / 158.7 µs | 1.024x / 1.013x | 13/13 | `benchmark-results/20261014T124546Z-0276cafe-4a43-41c5-99e6-ff23e003d54a.json` |
| Large response model | 359.4 / 369.5 µs | 381.6 / 403.5 µs | 1.062x / 1.092x | 1/1 | `benchmark-results/20261014T124713Z-80ac3dca-94fb-4f42-9d99-55a75d44c5b5.json` |
| Repeated sequence query | 100.4 / 106.0 µs | 111.3 / 126.3 µs | 1.108x / 1.191x | 1/1 | `benchmark-results/20261014T124834Z-e0993952-4a89-48f3-a47c-8c0f1afe9575.json` |

FastAPI-RS had higher median and p95 latency on all seven workloads; invalid
requests had the largest median gap. This is a single-host direct-ASGI result,
not a global performance claim; it does not measure network/server latency or
separate facade, PyO3, Rust, Pydantic, or Starlette-RS costs. Starlette 1.6.0
controls remain contextual and are not subtracted from FastAPI timings.

This suite is retained as historical evidence; its workload comparisons bind
the previous manifest and are not the current benchmark contract.

#### Previous completed seven-workload run (2026-10-14; commit c94b5d4; stale manifest)

The suite completed at `2026-10-14T12:21:04Z` with suite ID
`4638f77b-99e2-427b-8da7-fa2487eee136`; its receipt is retained at
`benchmark-results/stale/suite-20261014T122104Z-4638f77b-99e2-427b-8da7-fa2487eee136.json`
(SHA-256 `03c0d8d98dffd6221605831c08fdb771a7646ad1f7d771fdc73409944e6295ef`).
Its comparisons bind the earlier manifest SHA-256
`c136b9710eacfbc22683dfec2c2bbad717092d386360afde061d4da47c5cd695`. It
passed 45/45 selected observations across the same seven workloads, on the same
CPython 3.12.13 / macOS 15.7.7 arm64 benchmark boundary. Its artifacts are
retained for history; the table above is the current run against the reviewed
nested-router request/response-model manifest.

#### Earlier completed seven-workload run (2026-10-14; commit 2553434; stale manifest)

The suite completed at `2026-10-14T11:13:20Z` with suite ID
`b8d9a7d5-1ad2-4cfd-8ed0-5004857d4d88` and receipt
`benchmark-results/stale/suite-20261014T111320Z-b8d9a7d5-1ad2-4cfd-8ed0-5004857d4d88.json`
(SHA-256 `9d11041054a9e6ade3a57ae4052db393019be56381dfa04ca5d3f3b48a9fc6bb`).
Each workload parity comparison binds the current manifest SHA-256
`b7ceba9309b7da96ccf30a40e910d734b293ad55451d3d006c47c63a8ed55d2c`. The
suite binds FastAPI-RS commit `2553434c596c8af2a73f62a9f687921e8fd695c5`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed 45/45
selected observations with zero failures or not-run cases. Each subject used
50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `cbe98cd6a778cba516ef4391f796b0302595d740bf7a889aea8e622e26636cb6`;
the target binary SHA-256 was
`e596867dc86fc3c07ee768774e0101ea0e2b745cd2319af5aded8ab019aa7670`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced below.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 505.7 / 515.7 µs | 679.0 / 739.8 µs | 1.343x / 1.435x | 2/2 | `benchmark-results/20261014T110459Z-fe1c4fda-152a-452d-8ef6-339a9ad40143.json` |
| Async nested dependencies, two query parameters | 428.3 / 440.9 µs | 658.2 / 699.5 µs | 1.537x / 1.587x | 2/2 | `benchmark-results/20261014T110625Z-1533f4ec-9f74-4a61-b9f6-0083a117afcd.json` |
| Chunked request body | 134.0 / 138.6 µs | 139.5 / 149.5 µs | 1.041x / 1.078x | 13/13 | `benchmark-results/20261014T110748Z-e78aede1-2256-4782-bae9-187c251f23f9.json` |
| Invalid request | 145.0 / 212.8 µs | 327.5 / 366.8 µs | 2.258x / 1.723x | 13/13 | `benchmark-results/20261014T110909Z-1e208705-85bb-4bfa-82f4-444f1d00c9d5.json` |
| Valid request | 130.5 / 138.2 µs | 137.3 / 157.0 µs | 1.052x / 1.136x | 13/13 | `benchmark-results/20261014T111032Z-6cb07edf-bc07-45a3-b49b-9f04f8d9cd54.json` |
| Large response model | 358.1 / 373.2 µs | 385.2 / 408.6 µs | 1.076x / 1.095x | 1/1 | `benchmark-results/20261014T111154Z-f7f59db7-8483-4403-b99e-0b478028e317.json` |
| Repeated sequence query | 95.5 / 106.4 µs | 105.2 / 124.7 µs | 1.101x / 1.172x | 1/1 | `benchmark-results/20261014T111320Z-0a1eb35d-8763-4583-9097-f3f74beb3be9.json` |

FastAPI-RS had higher median and p95 latency on all seven workloads; invalid
requests had the largest median gap. This is a single-host direct-ASGI result,
not a global performance claim; it does not measure network/server latency or
separate facade, PyO3, Rust, Pydantic, or Starlette-RS costs. Starlette 1.6.0
controls remain contextual and are not subtracted from FastAPI timings.

#### Previous completed seven-workload run (2026-10-14; commit c6b5246; stale manifest)

The suite completed at `2026-10-14T10:05:13Z` with suite ID
`923415bf-56b3-499a-9ab2-83402aeca3a1` and receipt
`benchmark-results/stale/suite-20261014T100513Z-923415bf-56b3-499a-9ab2-83402aeca3a1.json`
(SHA-256 `71bf96b4e547abf1c0f2640ceb3a3f92475b99ffa80f355aa294200ec194a381`).
Each workload parity comparison binds manifest SHA-256
`d808858a9fd54ded33b713a8b1fa31db3c9cf17e0fcbfc6d07dd3815e88b8b1c`.
The suite binds FastAPI-RS commit `c6b5246a68a8b9f6e9f562be6c669e69c03f171b`,
FastAPI `0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette
`1.6.0` at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven identity-checked parity gates passed
45/45 selected observations with zero failures or not-run cases. Each subject
used 50 warmups and 1,000 measured calls in five rounds. The target extension
SHA-256 was `cbe98cd6a778cba516ef4391f796b0302595d740bf7a889aea8e622e26636cb6`;
the target binary SHA-256 was
`e596867dc86fc3c07ee768774e0101ea0e2b745cd2319af5aded8ab019aa7670`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced below.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 517.0 / 553.7 µs | 686.4 / 753.7 µs | 1.328x / 1.361x | 2/2 | `benchmark-results/20261014T095651Z-b84ad218-15f9-46b7-92d4-6fbc482e0de4.json` |
| Async nested dependencies, two query parameters | 434.1 / 478.7 µs | 669.0 / 748.6 µs | 1.541x / 1.564x | 2/2 | `benchmark-results/20261014T095817Z-3ca5b793-9701-4938-ab74-0be568a571f3.json` |
| Chunked request body | 134.8 / 147.2 µs | 141.4 / 163.5 µs | 1.049x / 1.111x | 13/13 | `benchmark-results/20261014T095943Z-ea597c4b-602a-4ebc-96f1-ffc2fb6a9c53.json` |
| Invalid request | 145.4 / 212.8 µs | 327.2 / 377.2 µs | 2.250x / 1.772x | 13/13 | `benchmark-results/20261014T100106Z-e84f95e1-af43-4c0f-8acb-f857702d5d11.json` |
| Valid request | 132.8 / 140.3 µs | 139.5 / 158.3 µs | 1.050x / 1.128x | 13/13 | `benchmark-results/20261014T100228Z-1c14c18a-392c-499e-8a8e-41f8e928f73b.json` |
| Large response model | 360.2 / 381.5 µs | 386.0 / 413.2 µs | 1.071x / 1.083x | 1/1 | `benchmark-results/20261014T100352Z-196dee93-8e77-453a-9cbf-1fb86ac83669.json` |
| Repeated sequence query | 93.6 / 105.5 µs | 112.5 / 135.6 µs | 1.202x / 1.286x | 1/1 | `benchmark-results/20261014T100513Z-130cb956-4f73-4bfb-8b96-c205a211d287.json` |

At the time it was generated, `make benchmark-contract-check` passed. The
manifest changed in commit `2553434`, so its suite receipt is retained under
`benchmark-results/stale/` and is not current evidence. FastAPI-RS had higher
median and p95 latency on all seven workloads; invalid requests had the largest
relative median gap. Starlette 1.6.0 controls are contextual and are not
subtracted from FastAPI timings. This single-host direct-ASGI result is not a
global performance claim. The older `b0d64fd` suite receipt remains under
`benchmark-results/archive/stale-manifest-20261014/` because its parity
comparisons used an older manifest.

#### Previous completed seven-workload run (2026-10-14; commit 7d42eee; stale manifest)

The suite completed at `2026-10-14T04:14:26Z` with suite ID
`975d019c-1e79-4184-b6e8-34fd215639c7` and receipt
`benchmark-results/suite-20261014T041426Z-975d019c-1e79-4184-b6e8-34fd215639c7.json`
(SHA-256 `87191a95c6d2c22b99d3903911fed3cc80efd56bb9177209ffdee0f877f3adbf`).
It binds manifest SHA-256
`9f69ed1f419c6900720ee4aa2f65193c970089b5e3df9ae344e95bc8dd4bbf5b`,
FastAPI-RS commit `7d42eee7a2a57aaf5f8649d6caab3b9689f2b9ee`, FastAPI
`0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette `1.6.0`
at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven workloads completed; their fresh,
identity-checked gates passed 45/45 selected observations with zero failures
and zero not-run cases. Each subject used 50 warmups and 1,000 measured calls
in five rounds. The target extension SHA-256 was
`751624869bd37cf499a1e0d22c76521ab308457b78f1dd914f9c8dbee3adb883`; the
target binary SHA-256 was
`cafa9226adcca314acf856cc916dbb5649a7ee2bbc8f130ec609a3c56cfa4914`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced below.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity | Raw receipt |
| --- | ---: | ---: | ---: | ---: | --- |
| Async nested dependencies, distinct query aliases | 487.9 / 533.3 µs | 655.2 / 721.7 µs | 1.343x / 1.353x | 2/2 | `benchmark-results/20261014T040601Z-e6916195-374e-4f35-832f-39aeb55d1684.json` |
| Async nested dependencies, two query parameters | 423.4 / 446.8 µs | 628.9 / 681.5 µs | 1.485x / 1.525x | 2/2 | `benchmark-results/20261014T040724Z-c20b8602-09e4-429a-969c-d3c7e7d0bd3c.json` |
| Chunked request body | 134.9 / 150.4 µs | 141.8 / 168.5 µs | 1.051x / 1.121x | 13/13 | `benchmark-results/20261014T040847Z-292bc3b8-d231-41af-81f5-446d9e3016ad.json` |
| Invalid request | 146.9 / 214.9 µs | 327.0 / 352.7 µs | 2.226x / 1.641x | 13/13 | `benchmark-results/20261014T041011Z-d6c318bf-963e-4bc3-9e42-1a8f18fa3b8c.json` |
| Valid request | 135.5 / 152.0 µs | 143.2 / 163.8 µs | 1.057x / 1.077x | 13/13 | `benchmark-results/20261014T041132Z-1785a8cd-c1ef-47e3-9f07-4500435d0e00.json` |
| Large response model | 368.8 / 403.7 µs | 402.4 / 457.1 µs | 1.091x / 1.132x | 1/1 | `benchmark-results/20261014T041258Z-93c9c7da-a83a-4db5-8a8c-85adfaf1aa1c.json` |
| Repeated sequence query | 98.3 / 114.7 µs | 113.8 / 143.5 µs | 1.157x / 1.251x | 1/1 | `benchmark-results/20261014T041425Z-7b4341a5-328b-43c0-b0b7-c874471f2ea8.json` |

FastAPI-RS had higher median and p95 latency on all seven workloads; invalid
requests had the largest relative median gap. A plain Starlette 1.6.0 control
was also measured for the chunked-body and valid-request lanes (5.3 and
5.0 µs median respectively); it is contextual, not subtracted from FastAPI
timings. This is one host and a narrow direct-ASGI suite, not a global
performance claim. It does not measure network/server latency or separate
facade, PyO3, Rust, Pydantic, or Starlette-RS costs.
At the time, `make benchmark-contract-check` passed for this run. Its manifest
is historical and no longer satisfies the current benchmark evidence gate.

#### Previous completed seven-workload run (2026-10-14; commit acf511f)

The suite completed at `2026-10-14T02:58:36Z` with suite ID
`c64e5f39-821e-46df-b97d-f8a38c8887be` and receipt
`benchmark-results/archive/suite-20261014T025837Z-c64e5f39-821e-46df-b97d-f8a38c8887be.json`
(SHA-256 `c096ac280f82dd56176f151f262dafd99aae6fb4403e943607b47d7c02f597b1`).
It binds manifest SHA-256
`812100b0c2390ebba6a736c834b722b2c828279e7a69a4a6e2feb2a9e498d7e4`,
FastAPI-RS commit `acf511faa4ce385eb59c070b8fed1be03535fb63`, FastAPI
`0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette `1.6.0`
at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven workloads completed; their fresh,
identity-checked gates passed 45/45 selected observations with zero failures
and zero not-run cases. Each subject used 50 warmups and 1,000 measured calls
in five rounds. The target extension SHA-256 was
`a10ac7ba40dadf3e7c2f3af4ad4d226c58cfda96d9eb90788db7b297a7979a3c`; the
target binary SHA-256 was
`bf1b102e48e734a28cc1be77416e953cd3859888f4a2b36f60ee5af86db87d2a`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity |
| --- | ---: | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 495.5 / 525.1 µs | 687.1 / 775.0 µs | 1.387x / 1.476x | 2/2 |
| Async nested dependencies, two query parameters | 412.5 / 438.0 µs | 647.4 / 724.0 µs | 1.569x / 1.653x | 2/2 |
| Chunked request body | 134.1 / 147.5 µs | 141.0 / 159.2 µs | 1.051x / 1.079x | 13/13 |
| Invalid request | 145.6 / 215.1 µs | 327.4 / 381.7 µs | 2.249x / 1.774x | 13/13 |
| Valid request | 133.8 / 155.2 µs | 137.9 / 159.6 µs | 1.031x / 1.028x | 13/13 |
| Large response model | 834.0 / 2064.3 µs | 439.9 / 1035.6 µs | 0.528x / 0.502x | 1/1 |
| Repeated sequence query | 101.3 / 106.0 µs | 111.0 / 120.6 µs | 1.095x / 1.138x | 1/1 |

FastAPI-RS had higher median latency on six workloads and lower median latency
for the large response model; its p95 was higher on six workloads and lower
for the large response model. Invalid requests remain the largest relative
median gap. A plain Starlette 1.6.0 control was also measured for the
chunked-body and valid-request lanes (5.0 and 5.0 µs median respectively); it
is contextual, not subtracted from FastAPI timings. This is one host and a
narrow direct-ASGI suite, not a global performance claim. It does not measure
network/server latency or separate facade, PyO3, Rust, Pydantic, or
Starlette-RS costs. Its suite summary is archived because its seven
comparison artifacts reference manifest SHA-256
`812100b0c2390ebba6a736c834b722b2c828279e7a69a4a6e2feb2a9e498d7e4`, not the
current manifest. Its per-workload result artifacts remain in
`benchmark-results/`.

#### Archived preceding seven-workload run (2026-10-14; stale manifest b317219)

The prior run completed at `2026-10-14T02:04:37Z` with suite ID
`972b59b0-832b-40cf-950d-7ede29e625a8` and receipt
`benchmark-results/stale/suite-20261014T020437Z-972b59b0-832b-40cf-950d-7ede29e625a8.json`
(SHA-256 `bce9701f31d93a634c48f692d1bac15ce42a323f83cbd90f51adae14e0faa68b`).
It bound FastAPI-RS commit `b317219b1f5f2f80db6ebedad80eacad0d0cf2bd` and
manifest SHA-256 `9904b4d55cccadd878c7141ba501c0980b7ad32ad102bf00cc3b3fb292c2f00f`;
its seven identity-checked gates passed 45/45 observations. The receipt stays
archived because those comparisons reference the previous manifest.

#### Archived previous seven-workload run (2026-10-14; stale manifest e1ce3b2)

The suite completed at `2026-10-14T01:23:49Z` with suite ID
`4429413f-af20-4c31-af67-2d904124bd35` and receipt
`benchmark-results/stale/suite-20261014T012349Z-4429413f-af20-4c31-af67-2d904124bd35.json`
(SHA-256 `e02609b93fae57e88cfa4f46bfbcad4cf5ee90ab12dc46023aa46977f58b7b95`).
It binds manifest SHA-256
`36055d0670be99d6cc141c4e96bc65bc5478c716e3ee9584738b5f67191d421b`,
FastAPI-RS commit `e1ce3b2fc6738e2fb2fd2de2bed54ffe0ada8880`, FastAPI
`0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette `1.6.0`
at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven workloads completed, and their fresh
identity-checked gates passed 45/45 selected observations with zero failures
and zero not-run cases. Each subject used 50 warmups and 1,000 measured calls
in five rounds. The target extension SHA-256 was
`a10ac7ba40dadf3e7c2f3af4ad4d226c58cfda96d9eb90788db7b297a7979a3c`; the
target binary SHA-256 was
`bf1b102e48e734a28cc1be77416e953cd3859888f4a2b36f60ee5af86db87d2a`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity |
| --- | ---: | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 483.9 / 519.0 µs | 657.6 / 703.5 µs | 1.359x / 1.356x | 2/2 |
| Async nested dependencies, two query parameters | 409.6 / 437.2 µs | 632.1 / 691.8 µs | 1.543x / 1.582x | 2/2 |
| Chunked request body | 136.2 / 145.1 µs | 144.4 / 164.4 µs | 1.060x / 1.133x | 13/13 |
| Invalid request | 143.8 / 210.5 µs | 316.0 / 334.0 µs | 2.197x / 1.587x | 13/13 |
| Valid request | 135.5 / 144.5 µs | 142.0 / 161.7 µs | 1.048x / 1.119x | 13/13 |
| Large response model | 363.2 / 432.6 µs | 387.3 / 432.4 µs | 1.066x / 1.000x | 1/1 |
| Repeated sequence query | 93.9 / 112.2 µs | 106.6 / 140.0 µs | 1.136x / 1.247x | 1/1 |

FastAPI-RS had higher median latency on all seven workloads in that historical
run. The suite receipt is archived because its comparison artifacts reference
a prior manifest; it is retained for history and is not current evidence.

#### Prior completed seven-workload run (2026-10-13; stale manifest)

The suite completed at `2026-10-13T21:41:21Z` with suite ID
`3daa276b-2a75-425b-82df-ce041294e2fd` and receipt
`benchmark-results/stale/suite-20261013T214121Z-3daa276b-2a75-425b-82df-ce041294e2fd.json`
(SHA-256 `d1f5167992ff7c56e9af529603bfa60bbbf326d3ae7f52f670ef79673d217803`).
It binds manifest SHA-256
`8cc5b54492d24272f79c88ce8f8c16af6f5c88099f2104b52b1bc7e4b4e66b1b`,
FastAPI-RS commit `d7d3f5fec9cf4af1ae192ea9be495a7c0eaa4b55`, FastAPI
`0.141.1` at `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette `1.6.0`
at `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and Starlette-RS
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. It used CPython 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4, macOS 15.7.7 arm64 (12 logical
CPUs), Cargo/rustc 1.98.1, and the optimized release profile with
`pyo3/extension-module`. All seven workloads completed, and their fresh
identity-checked gates passed 42/42 selected observations with zero failures
and zero not-run cases. Each subject used 50 warmups and 1,000 measured calls
in five rounds. The target extension SHA-256 was
`84b8bb08c9726620171da2abf7f550c941fc9c643bb5324e777c9c58070daf24`; the
target binary SHA-256 was
`d185784c161c241679b86890cd02e505dd716cdc2c982cf0a330fb48cf5e3569`.

The table reports median and p95 direct-ASGI latency in microseconds. Ratios
are FastAPI-RS divided by FastAPI, so values above `1.0x` mean FastAPI-RS took
longer on this host. Raw samples and parity identities remain in the ignored
suite and workload receipts referenced above.

| Workload | FastAPI median / p95 | FastAPI-RS median / p95 | Median / p95 ratio | Parity |
| --- | ---: | ---: | ---: | ---: |
| Async nested dependencies, distinct query aliases | 483.6 / 517.9 µs | 660.3 / 726.1 µs | 1.365x / 1.402x | 2/2 |
| Async nested dependencies, two query parameters | 431.4 / 467.6 µs | 657.6 / 758.3 µs | 1.524x / 1.621x | 2/2 |
| Chunked request body | 134.4 / 143.8 µs | 143.3 / 176.0 µs | 1.066x / 1.223x | 12/12 |
| Invalid request | 145.5 / 213.8 µs | 326.3 / 387.7 µs | 2.243x / 1.813x | 12/12 |
| Valid request | 140.1 / 152.3 µs | 140.7 / 176.9 µs | 1.004x / 1.161x | 12/12 |
| Large response model | 365.5 / 455.1 µs | 389.0 / 421.0 µs | 1.064x / 0.925x | 1/1 |
| Repeated sequence query | 103.0 / 130.3 µs | 111.3 / 137.8 µs | 1.081x / 1.058x | 1/1 |

FastAPI-RS had higher median latency on all seven workloads. Large-response
p95 was lower than FastAPI's, while its median and the other p95 ratios were
higher. The invalid-request path remains the largest gap. This is one host and
a narrow direct-ASGI suite, not a global performance claim. It does not
measure network/server latency or separate facade, PyO3, Rust, Pydantic, or
Starlette-RS costs. The Starlette control remains contextual and is not
subtracted from FastAPI timings. `make benchmark-contract-check` passed after
the previous `cb1352a` suite receipt was retained under
`benchmark-results/stale/`.

#### Prior completed seven-workload run (2026-10-13; archived stale manifest)

The suite completed at `2026-10-13T19:30:07Z` with suite ID
`62b84e96-4d6d-4284-9f70-b6bf142a4aa7` and receipt
`benchmark-results/stale/suite-20261013T193007Z-62b84e96-4d6d-4284-9f70-b6bf142a4aa7.json`
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
also slower than the previous revision-specific run. This was one host and a
narrow direct-ASGI suite, not a global performance claim. It did not measure
network/server latency or separate facade, PyO3, Rust, Pydantic, or
Starlette-RS costs. The Starlette control was contextual and was not
subtracted from FastAPI timings. The suite remains historical because it used
manifest `9ecbd9e9…` and target `cb1352a`; its receipt is retained under
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
after each app was constructed. FastAPI-RS calls
`TypeAdapter(annotation)` inside `validate_python_value` for each validated
input (`fastapi-rs/src/application_runtime.rs`), which identifies repeated
adapter setup as an optimization candidate but does not establish causality.
The current report measures a 1.439x median and 2.832x p95 ratio for invalid
requests on this host. After the public operation contract is complete, measure
per-parameter adapter reuse on the full boundary, including dependency
overrides, and retain the invalid error-body parity gate.

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
