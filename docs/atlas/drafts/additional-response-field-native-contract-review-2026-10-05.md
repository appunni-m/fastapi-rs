# Additional response fields: measured implementation boundary

2026-10-05. Native implementation commit `827612f28226dc5c0d6e008d1a38231c03293389`.
FastAPI 0.141.1 / Starlette 1.6.0 / CPython 3.12.13 / Pydantic 2.13.4,
core 2.46.4 and immutable Starlette-RS `b4c8a65` remain pinned.
This is a bounded compatibility result; full public API parity remains incomplete.

## Inputs and manifest

Three independent ordinary parity cases add 15 HTTP GET actions and three
construction observations: saved decorator attachment, two included contexts of
one original router, and refusal on the second additional core-schema hook with
whole-branch retry. Inputs contain no expected outputs or backend detection.
Public state responses retain ordered hook calls, warnings, actual handled errors,
endpoint counters and losslessly encoded raw sends. No selector or comparator was
weakened. These inputs expose premature JSON hooks; positive OpenAPI generation,
shared definitions and primary adapter reuse during OpenAPI remain separate gates.

Active recipe: `tests/fixtures/input-recipes/parity/additional-response-field-lifecycle.yaml`.
Active workload: `tests/fixtures/workloads/additional_response_field_lifecycle.py`.
Recipe SHA256 `199ab0b81d4b1e923933a13f076c49bb89229add1e0c90ce441902c0c5db7ae1`;
workload `ef756492903a719a8b3522bc1971794663083bcbb55ed20076b74f988d0e8025`;
materialized input `8ec188213588f06c8a107941f442f8f9bf69020828ae42626238f247c4944190`.
Metadata adds 26 fixture links to ten existing operations, including Request
injection and registration of the public error handler. Only retry invokes that
handler. Generic Request behavior remains sibling-owned. The index generator
resolves complete case selectors for each fixture link; that provenance does not
promote all those selectors to Request-owned behavior.

Admission keeps 460 required public symbols plus nine inherited operations
(469 public/inherited candidates) and 21 root exports. At this wave's admission, the matrix had 553 workflows / 2,297
cases, 1,571 partial source maps and 1,326 fixture links. Later OpenAPI input
admission is separate from these measured receipts. Reviewed source classifications remain 460 supported,
1,102 private/internal and 31 uncertain; these are source classifications, not
counts of implemented or passing target APIs.

## Native change

Rust retains raw additional-response declarations at saved decorator creation.
Attachment constructs additional serialization fields in insertion order before
primary fields. Each included branch constructs and publishes its own complete
field vector only after its own construction succeeds. Nested child readiness is
independent, so successful parent-own fields remain available after child failure. Request validation and
serialization select only the primary field; additional status fields remain
schema metadata. A returned Response continues to bypass primary validation.

OpenAPI clones owned app/route inputs under short borrows and runs generation
outside those borrows. Additional JSON schemas use retained adapter core schemas;
non-reference field titles use retained FieldInfo metadata. Publication follows
successful generation. The newly changed materialization/generation publication
paths drop retired values outside guards; the preexisting explicit openapi_schema
setter replacement behavior remains separate.
The existing primary/request/body schema regeneration and individual-field JSON
schema algorithm remain gaps against the pinned shared generator contract.

No Python runtime logic, dependency, public export, unsafe block, blanket lint
suppression or fault point was added. The binding layer remains unchanged.
Implementation and independently reviewed prospective/formatted patch evidence
are under `proposals/additional-response-field-lifecycle/`.

## Live source and target evidence

Unchanged-target diagnosis at `6da8235`: all three source constructions succeeded
and all 15 actions completed on each side, but all three comparisons failed.
Source core hooks wait for attachment; the old target performed extra core and
JSON hooks at saved declaration, reused fields across included contexts, and
missed the armed retry refusal. This was ordinary public input, not fault injection.

After repair, 43 whole workflows passed all 203 selected cases with zero failures
or not_run cases. Forty ASGI workflows comprise 199 cases / 504 actions per
implementation; three API workflows comprise four cases / 15 probes. Seven
constructor-error controls match; every planned executable action completed.
All 853 action/probe observation records and 93 selected construction
observations match (946 observation records per implementation). The new three complete ordered case payloads
match target and are unchanged from pre-change source observations, including
state bytes, seven warning records, handled 409 and 12 raw sends.

Measured target revision was `6da823585dbe4605ff1e04204eee287813eb34e8` with the
reviewed native edits and formatted integration note present. Committing those
same files as `827612f` changed revision only. The complete tracked/nonignored
source bytes and native pair remained equal to the measurement; the pre-build
receipt verifies that relation. No claim binds the old measured revision to its
unmodified Git tree.

Initial/final snapshot files are byte-identical. Combined source identity:
`204d9a6aa869e6ec5623f6a93c07fa7973910784c7b63e64efd21f51ea17edf2`.
Normal FastAPI core: `5eeae03b977c74fed3808df9194bef0d23527a8208b2c05c92f9415084b7a244`;
sibling core: `fd5940e3d5ff196e896823a3d62fe650b4122dbd4447f6f490bc8be1255bdef5`;
normal native pair: `8e1888dbe104c3bdf69f63b47bb0e9ded4a3ba9cc70d2c04676890134501f6ed`.

Ignored receipts: `parity-results/additional-response-field-wave/pre-change/`
and `final-normal/`. Independent pre/final audits accompany this report. The two
legacy OpenAPI controls pass selected parsed-pointer/status observations; these
controls do not establish raw schema-byte equality or JSON-hook timing. Six v9
receipts explicitly report fault=false; 37 legacy receipts omit that mode field.
The canonical normal worker guard and identical binary pair apply to all 43.

## Fresh normal incremental coverage

All eight workflows / 86 cases passed on one fresh normal instrumented build.
The baseline and six previous batches were remeasured on the same source/build;
no prior-revision coverage was reused. All 57 fixed-state checks passed.
Coverage-MCP verifies 105 new regions from the new three-case batch, increasing
the union from 14,022 to 14,127 / 31,473 regions. Batch-only coverage is 8,010 /
31,473; union coverage is a distinct quantity. Per-case region attribution,
sibling/Python coverage and full-suite regressions remain unmeasured.

Build ID `790a865fd710376fd0e2bca1f0de1a5c27e3ab3769780714b8c7725f54b2f1ea`;
normal instrumented core `8560d80af37594007d5624706da53decd7fbfef33e28839b615560ad45d22cd3`.
Actual MCP request/result, reports, contexts, ledger and configuration are under
ignored `parity-results/coverage/additional-response-field-normal/827612f-first/`.
The completed build log is `parity-results/additional-response-field-normal-instrumented-build.log`;
its receipt is `parity-results/additional-response-field-normal-instrumented-pre-build-receipt.json`.

## Separate fault lane and normal restoration

The isolated fault-enabled build passed 55 ordinary parity cases and all six
existing target-only fault contracts across five workflows. Source fault rows are
not_applicable; ordinary source rows execute. All 36 fixed-state checks passed.
Its 31,673-region inventory, build ID `78fef6dc1520f1e504cadc83efe0376952e2d781ca9beb7a97188118e80a09ac`
and core `7b925c4c4b812f813402a25aef461104f38440061ee2de83fe999d8930c8c291`
remain separate from normal coverage. Direct native identity confirms fault=true.
These fault contracts cover public error/cleanup/later-success outcomes; they
make no assertion about additional-field identity or arbitrary cache failures.

After both measurement processes closed, the normal release target was rebuilt.
`parity-results/additional-response-field-normal-restore-snapshot.json` proves the
complete source identity and both normal binaries exactly match the 203-case
measurement, with direct native fault=false and the correct installed path.
This proof precedes subsequent documentation updates, whose file bytes change
full source hashes without changing the measured Rust implementation.

## Fresh correctness-gated benchmark suite

All seven existing workloads completed at clean `827612f` with 42 passing
case executions / 56 ASGI actions per implementation across fresh whole-workflow
parity gates.
Every subject passes equal untimed status, ordered headers and body observations.
The suite retains 16,000 per-request latency samples across 16 subjects. Each
subject uses 50 warmups, five rounds of 200 samples and concurrency one.

The boundary is direct await app(scope, receive, send) latency, including native
dispatch, facade/PyO3 conversion, validation and response sends. Interpreter and
application startup, request setup, server/network/client costs and post-call
observation checks are excluded from latency. Sequential-loop throughput includes
request setup/checks/bookkeeping and is a separate recorded metric. Isolated
facade/native component costs and server/network behavior are unmeasured.

Host: arm64 macOS 15.7.7, 12 logical CPUs; CPython 3.12.13, Rust 1.98.1.
These are one local suite's observations, not a prior-commit regression comparison
or a general speed claim. RS/FastAPI ratios divide target latency by oracle latency.

| Workload | FastAPI median µs | RS median µs | RS/FastAPI median | RS/FastAPI p95 | Starlette control median µs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nested distinct query aliases | 499.395 | 320.771 | 0.642 | 0.702 | — |
| Nested two query parameters | 421.792 | 273.479 | 0.648 | 0.653 | — |
| Chunked body | 135.708 | 142.729 | 1.052 | 1.080 | 5.125 |
| Validation error | 146.666 | 324.208 | 2.211 | 1.684 | — |
| Valid request | 137.229 | 147.583 | 1.075 | 1.331 | 5.125 |
| Large response model | 373.541 | 402.500 | 1.078 | 1.080 | — |
| Repeated query sequence | 103.625 | 114.291 | 1.103 | 1.101 | — |

Starlette 1.6.0 controls are contextual baselines for valid/chunked requests.
They do not perform FastAPI validation, so do not subtract or treat those control
timings as equivalent FastAPI work. Validation-error latency remains a concrete
performance priority; no optimization or causal attribution follows from this run.

Ignored suite: `benchmark-results/suite-20261005T121923Z-250a48d8-8719-4737-82bb-de7a71841c51.json`.
Its seven result artifacts retain gates, identities, raw samples and summary
statistics. `benchmark-results/additional-response-field-827612f-post-suite-snapshot.json`
proves the source and normal native pair still match the 203-case measurement
after all seven complete. Documentation updates follow this frozen evidence.

## Static and runtime boundaries

Final `make fmt clippy api-contract-check metadata-check python-facade-check`
passed, followed by all three dependency inventory/graph checks and benchmark
contract/suite-artifact checks. The runtime target boundary also passed on the
restored normal target: no original FastAPI dependency/import, direct native
reexports only. The recursive Python graph has 204 source-backed locked
distributions across ten profiles with zero unresolved purpose records; the
Pydantic Core inventory resolves 104 packages. This is dependency inventory
validation, not implementation or performance support evidence.

Logs: `parity-results/additional-response-field-final-static.log` and
`parity-results/additional-response-field-runtime-boundary.log`. Original failed
format/argument setup logs were preserved; the formatted strict checks and
explicit-target-Python build completed successfully. No pytest, unittest or
Cargo test ran, and no unit tests were added.

## Remaining boundaries

Full API parity is incomplete. Positive OpenAPI hook ordering, retained primary
adapters, shared definitions, flat title/alias behavior and generation retry need
fresh independent gates. Included dependency-plan timing, mutable maps/annotations,
custom statuses, inheritance/signature coverage, stream/request/body fields,
warning-filter mutation, reentry/concurrency and finalizer behavior remain open.
The sibling BackgroundTasks worker-crossing repair remains a separate pending
human decision; neither sibling source nor its pin was changed.
