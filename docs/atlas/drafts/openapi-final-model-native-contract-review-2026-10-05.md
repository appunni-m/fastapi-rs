# Retained response fields and private OpenAPI graph: bounded measured contract

Date: 2026-10-05. Measured normal revision: `62dacc5283a0cee282258e268f7545765679e974`.

The normal, coverage, fault/restoration and benchmark stages are closed and independently reviewed. Counts below describe the declared selected contracts and actual completed work. They do not establish full FastAPI compatibility.

## Implementation boundary

Rust retains primary and additional response-field adapters, with separate ownership for each included context. Document generation batches retained response cores through one Pydantic schema generator and consumes each owner's schema without rebuilding the primary adapter. The selected inputs expose core/JSON hook ordering, shared-definition references with sibling extensions, public refusal/retry behavior and cached reuse.

Rust also constructs a private OpenAPI model graph through pinned Pydantic/typing/enum APIs and applies that graph before the existing Rust encoder. This replaces a manual final key-order policy with Pydantic's actual model validation, union selection and serialization. The graph's classes and validator handle remain internal; its use does not establish public OpenAPI model API compatibility. In the selected first-request case, source `PathItem | Any` exactness preserves raw nested parameter/request-body maps, which the earlier ordering finalizer changed.

The first graph module import at 51fa96a failed during target bootstrap because the main `Annotated` subscription used the wrong public call shape. The narrow 2135bee correction uses `__class_getitem__`; the failed bootstrap artifacts remain preserved and count as no parity evidence. The subsequent builder failure occurred before target execution because the editable metadata/wheel stage still reached the moving sibling checkout. The all-stage builder at 62dacc5 uses physical overlay member manifests and pinned sources throughout metadata, wheel and final native compilation. Normal editable provenance remains the repository, and its Python path survives temporary overlay removal. Fault artifacts use their own persistent package path and do not overwrite the normal native files. These fixes precede the successful gates below; failed attempts are not folded into the pass count.

Runtime behavior remains in the Rust core. The Python facade remains direct native passthrough. The target uses Pydantic and the pinned sibling, with zero original FastAPI runtime dependency/import under the static contracts; the source oracle runs separately. Normal receipts also report no original FastAPI target package. Source inventory and private graph reconstruction are implementation evidence, not blanket support claims.

## Closed normal gate

The fixed normal build completed **46 distinct workflows / 210 declared selected and passed cases / 0 failed / 0 not_run**:

- full regression gate: 44 workflows / 206 cases, with 523 completed ASGI actions, 15 completed API probes and 917 step observations per implementation;
- direct public OpenAPI controls: 2 workflows / 4 cases, with 4 completed API probes and 5 observations per implementation;
- a separate targeted rerun: 3 cases / 19 HTTP actions / 64 observations per implementation, already included in the 206 and not added to 210.

The full gate contains 96 construction observations: 89 successful constructions and seven matching public constructor errors. All planned actions/probes complete; no constructor-error case conceals a blocked planned request. Input/index/recipe/workload/manifest hashes, ordered case/action/probe contracts, run IDs and comparison receipt hashes bind the actual results. All 206 complete ordered typed oracle case payloads remain equal to the preserved 1c66469 oracle payloads.

The selected first-request OpenAPI response is exact: status 200, ordered headers and 2057 body bytes match source SHA256 `52e6edbe28c219cf75ddaedb3482c944a41d24b5efd52c3794b18209ff7ecacd`. The preserved failed target digest is `8e9dbac4fc3184a2d2e5a30da7f70df9c46180cd76a9dd870ac098d2c9060def`. This is raw wire evidence, not parsed-object equality alone.

The three new retained-field cases preserve exact selected schema bytes and public send, warning, callback and exception journals. Shared JSON hooks run six times in both products, so the result does not prove one-call deduplication. The matching 409 refusal, successful retry and subsequent cache identity/journal state are observed through public endpoints. Their source/target payloads remain equal to the preserved pre-change oracle, as well as the separate rerun.

### Declared pass is bounded

One legacy structural OpenAPI projection still has 11 schema maps ordered source `[type,default,title]` versus target `[type,title,default]`. These are an exact subset of the preserved old target's 29 map-order differences; 18 Parameter orders are repaired. The unchanged structural comparator declares that case passed. Consequently, the 210 declared passes do not establish all 210 raw wire or ordered typed equality. The direct four establish the declared structural API/signature outcomes and capture no warning sidecars.

## Closed managed coverage and fault stages

The closed nine-workflow normal coverage gate passed 89 cases with 267 actual HTTP actions per implementation. The 64 fixed-state checks are seven source/input/native checks per workflow plus the final all-selections check (9×7+1); they are not receipt/schema counts. Coverage-MCP verified 121 newly observed regions, extending the measured union `14902 → 15023 / 32502` for that normal instrumented build. This does not establish support for every source branch.

The separate closed five-workflow fault gate contains 55 ordinary cases, with 149 HTTP actions per implementation, plus six target-only fault contracts, with 12 HTTP actions executed by the target. The source six injected cases are contract N/A under the declared target-only contracts; these are not source requests or ordinary `not_run` parity cases. Source completes the 55 ordinary cases / 149 actions; target completes 61 constructors / 161 actions (149+12), and all 61 declared outcomes pass. The 36 fixed-state checks are 5×7+1. Coverage-MCP verified eight newly observed fault regions and the separate cumulative fault union `13864 → 13872 / 32702`. The six injected cases exercise their declared public cleanup/error/recovery contracts. They are not source-reachable parity cases, are not added to the normal 210 and do not prove every newly introduced worker/model/schema error boundary has fault coverage. The normal instrumented report covers 20 native files / 32502 regions; the fault report covers 21 native files / 32702 regions. Normal and fault denominators/builds remain separate; repeated run case counts and coverage regions are not concatenated into one compatibility total.

Both coverage lanes include only FastAPI-RS native files; sibling, Python and
external runtime coverage is excluded. Reports are workflow aggregates, with no
per-case or per-injected-case region attribution. The eight fault-lane regions
extend only that fault-feature build's measured union. All prior report hints
were freshly measured on the respective build. Neither union establishes
full-matrix coverage or regression status.

## Exact normal restoration

Exact release restoration was verified before benchmarking:

- combined source: `503211630df8f7e2bf624c55c217d08444658252311bff19bf6568b4736a4c0f`;
- normal pair: `e09f01666f13211eafc047cfd9626f20338796f688734cf39d3c8e86e145c4e0`;
- release FastAPI native: `d934ba09884e6c8a657300c4800a92e76577285f2bf5833e73418d21912b6140`;
- sibling native: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`.

The normal identity is `fault_injection_compiled: false`; the isolated fault identity is true. The fault build preserved the installed/exported normal instrumented binary (`df2e8902…`). After the two coverage lanes closed, the saved installed/exported release files (`d934ba…`) and sibling (`fd594…`) were restored exactly. Direct isolated import paths and feature flags, backup/restoration digests and the installed runtime boundary check passed. These saved proofs remain bound to the measured revision.

## Fresh seven-workload benchmark

The canonical suite completed all seven workloads. Its seven fresh whole-workflow
parity gates passed 42 case executions and 56 actions per implementation; these
are repeated evidence, not additional distinct cases in the normal210 total.
Sixteen isolated subject measurements retain 16,000 raw latency samples. Each
subject has 50 warmups and five rounds of 200 samples, with concurrency one.
Stored median nanoseconds use `int(statistics.median(raw_latency_ns))`, matching
the declared worker; raw samples and all summary statistics remain preserved.

| Workload | FastAPI median µs | FastAPI-RS median µs | Target/source ratio |
| --- | ---: | ---: | ---: |
| Nested distinct query aliases | 511.771 | 321.875 | 0.629 |
| Nested two-query dependencies | 420.458 | 281.521 | 0.670 |
| Chunked body | 136.917 | 146.292 | 1.068 |
| Invalid request | 147.771 | 325.833 | 2.205 |
| Valid request | 134.625 | 139.834 | 1.039 |
| Large response model, 300 records | 370.895 | 396.875 | 1.070 |
| Repeated sequence query | 103.042 | 116.208 | 1.128 |

Ratios below one have a lower measured target median; results are mixed. The two
Starlette controls, chunked-body 5.083µs and valid-request 5.125µs, omit FastAPI
validation/dependency work. They are contextual controls, not equivalent-work
subtraction baselines. No overall speed claim is made.

Boundary: warmed direct ASGI application invocation and declared request/response
work. No network/server/startup cost, OpenAPI generation timing, pure native
timing or separately isolated facade/FFI cost is measured. Environment: arm64
macOS15.7.7, 12 recorded CPUs, CPython3.12.13, Rust1.98.1 release extension,
Pydantic2.13.4/core2.46.4 and the exact pins above. Warmups, samples, observed
responses, interpreter/package/toolchain identities and per-subject hosts remain
in the declared workloads and results. The source/native pre/post suite snapshots
are byte-identical and match the restored normal pair.
Timed worker PIDs and the complete OS environment are not serialized. Process
evidence is bounded to runner isolation, saved parity commands and recorded
interpreter/package/native/host identities; CPU affinity and power-state controls
are not asserted.

Fresh suite: `benchmark-results/suite-20261005T145041Z-7ec4051b-63b7-499d-b175-5203358c2aa4.json`,
SHA256 `b6a16a67ecec978780eebd662251ad27b00c8e407ed3a702f71f50dd006f399d`.
Before the next fixture admission, that suite was preserved byte-for-byte at
`benchmark-results/archive/62dacc5-before-validation-response/` with its original
basename. Its relocation receipt retains the original result/comparison paths
and old manifest. It remains evidence for this measured checkpoint.
The previous827612f suite used the older `ae88fc58…` manifest. Its bytes were moved
unchanged into `benchmark-results/archive/827612f-before-openapi-final-model/`;
all original result/comparison paths and digests remain intact. A relocation
receipt records both manifests and the before/after suite digest. The current
root suite remains separate under manifest `eba84432…`; no checker was weakened.

## Static checks and evidence

`make -j1 fmt clippy metadata-check api-contract-check parity-index-check
dependency-inventory-check pydantic-core-inventory-check dependency-graph-check
python-facade-check benchmark-contract-check parity-validate` passed after all
measurement stages closed. Log: `parity-results/openapi-final-model-final-static-contracts.log`.
No unit test framework, unsafe code, blanket suppression, runtime facade helper,
new runtime dependency or fixture expected output was introduced.

Independent saved reviews:

- [Normal210 and oracle stability](openapi-final-model-normal-evidence-audit-2026-10-05.md)
- [Separate targeted3](openapi-final-model-targeted-evidence-audit-2026-10-05.md)
- [Direct4 public controls](openapi-final-model-public-controls-audit-2026-10-05.md)
- [Normal coverage89](openapi-final-model-normal-coverage-audit-2026-10-05.md)
- [Fault61 and exact restoration](openapi-final-model-fault-restoration-audit-2026-10-05.md)
- [Benchmark7 review](openapi-final-model-benchmark-audit-2026-10-05.md)
- [Residual schema-order diagnosis](legacy-inline-schema-order-diagnosis-2026-10-05.md)

Raw inputs and result JSON remain generated/ignored. Initial failures remain
preserved: three pre-change mismatches; the1c66469 full gate with205pass/1fail;
graph bootstrap failures before the2135bee correction; and editable-stage
compilation against the moving sibling before the62dacc5 builder correction.
No failed/partial attempt is included in the current closed pass denominator.

## Limits retained

The measured inputs establish selected immutable HTTP/ASGI and API behavior. They do not establish complete OpenAPI assembly/status/default/automatic 422/wildcard response branches; direct-field outer alias/title modes; arbitrary shared-definition/model-flattening custom maps; all external-document URL/error paths; public model exports; route mutation/version refresh; callback reentrancy/concurrency; or complete generic await reuse/cancellation/audit/throw semantics. Source classification does not become target support solely through the private graph or successful selected outcomes. Existing exclusions and unexercised sibling-owned behavior remain separate.


Next slice: admit the reviewed four-case/24-request automatic validation-response
inputs, then require live source completion and preserve unchanged-target
construction/wire mismatches before implementation. The remaining legacy inline
schema order needs a separate public HTTP gate.
