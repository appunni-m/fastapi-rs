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

The primary target profile is the **FastAPI-RS Python consumer surface**:
user code builds the app, routes, endpoint callables, and Pydantic models
through FastAPI-RS's public `fastapi` import, whose Python layer mechanically
forwards to PyO3 and Rust. The `fastapi-rs` crate owns FastAPI decisions and
control flow; `fastapi-rs-py` handles PyO3 boundary conversion. Upstream
FastAPI is source-oracle/dev-only and must not be an installed runtime
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
Starlette's entire public denominator. If FastAPI-RS also exposes a native
Rust API, declare it as a distinct target with a documented mapping to
consumer-visible operations. Do not treat native Rust microbenchmarks as
Python-facade or FastAPI parity results.

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
reviewed six-workload set in a fixed order. The contract check rejects missing,
renamed, or additional declarations until the suite denominator is reviewed.
Before building, the runner verifies the FastAPI, Starlette, and Starlette-RS
source revisions against their current manifest pins. FastAPI-RS must have a
clean working tree; its current HEAD is recorded per run because the manifest
does not pin a FastAPI-RS commit. Each workload then runs its own fresh
full-workflow parity gate and release measurement. A completed suite summary is
emitted only if every declaration has a new valid result and all results share
source revisions, native target binary, Python, host, and build identities. A
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

The implemented suite currently measures six direct-ASGI workloads through
the isolated FastAPI Python consumers. Each run gates the full selected
workflow, performs an untimed response check, then records 50 warmups and five
rounds of 200 sequential samples per subject. Per-request latency starts at
`await app(scope, receive, send)`: app construction, interpreter startup, and
per-call ASGI scope/callback setup are outside that timer. The target timing
includes its public `fastapi` facade, PyO3 conversion, native FastAPI-RS code,
Pydantic work, and Starlette-RS dispatch as one combined path. The current
results do not separate those components and do not measure a loopback HTTP
server or a native-only Rust boundary. Those measurements remain separate
future workloads; do not infer them by subtracting the Starlette control or
from the end-to-end target time.

| Tier | Workload | Timing boundary and purpose |
| --- | --- | --- |
| 1. Request path | Preserve sync/async input-model validation; small dict/model output with and without `response_model`; nested dependencies; large request payload; and large dict/model response with and without `response_model`. The upstream large response contains 300 items with 25 integers each plus metadata. Add a plain-route control implemented with Starlette 1.6.0's public `Route` and response APIs. | Match upstream's in-process `TestClient` path. Construct the app and client outside the timed request; exclude the one warmup request. Keep the raw Starlette control to the same simple request/response work; it is not a feature-equivalent FastAPI comparison. This is an integrated Python/ASGI/client measurement, not network-server latency. |
| 2. OpenAPI | Preserve the upstream graph: 20 routes sharing a 101-dependency chain, with query parameters discovered from the graph. | Measure cold generation by clearing the schema cache then calling `app.openapi()`. Keep route/app construction outside the measured function, as upstream does. Add warm cached lookup as a separate workload. |
| 3. Construction and memory | Preserve route dependency graph construction (20 routes) and the graph with 50 endpoint parameters and 100-deep dependencies. Measure application setup, route registration, and retained/peak memory in distinct workloads. | Time construction only when it is the declared workload. Report memory separately from latency and identify whether app creation, OpenAPI generation, or request execution is inside the measurement. |
| 4. ASGI/server | Add direct in-process ASGI requests and loopback HTTP server runs only after the upstream-equivalent tier is stable. Include startup/shutdown, steady-state request latency, throughput, concurrency, and tail latency as separate declared measurements. | Use the same pinned server, client, transport, configuration, payload, machine class, and concurrency for source and target. Keep server start-up out of steady-state request timings; report it separately. |
| 5. Native Rust | For workloads with a measurable Rust boundary, record native Rust time/cost separately from the public Python `fastapi` call; state the instrumentation or native harness boundary. | Keep the public Python-facade result as the primary FastAPI-RS comparison. Report native Rust measurements separately, even when collected through internal instrumentation, and mark them unavailable when the boundary cannot be measured. Do not infer native cost by subtracting from end-to-end time or present it as Python-facade/FastAPI parity. |

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
