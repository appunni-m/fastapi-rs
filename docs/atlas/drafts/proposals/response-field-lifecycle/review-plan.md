# Prospective response-field lifecycle and response-class provenance slice

These independent drafts remain outside active inputs. Their authored copies
are retained here; the app factories have not been imported or executed. Static admission and independent source
review are recorded below. The current worker/classifier wave and
its separate sibling blocker establish no support for this proposal.

Files in this directory:

- `response_field_lifecycle.py`: ordinary public user app, Pydantic metadata,
  callback recorder and lossless ASGI send observer.
- `response-field-lifecycle.yaml`: schema @9 normal parity inputs, with the intended
  future workload path `tests/fixtures/workloads/response_field_lifecycle.py`.
- `review-plan.md`: source contracts, observation boundaries and review gates.

Manual count: **16 independent parity cases, 61 materialized HTTP actions,
16 construction observations**. The actions are 29 `/probe` requests and 32
`/state` requests. There are no fault contracts, stored results, copied upstream
tests, comparator changes or normalization rules. One case has no HTTP actions:
its public route-registration exception is the construction observation.

## Pins and boundaries

- FastAPI 0.141.1: `/Users/lazytrot/work/fastapi`, commit
  `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0: `/Users/lazytrot/work/starlette`, commit
  `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`; sole source oracle.
- Recorded sibling pin: `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`, commit
  `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`. Before any future activation, parent
  must record and identity-check the reviewed actual sibling pin. This proposal
  does not presume resolution of the worker wave's cross-thread BackgroundTasks
  blocker or authorize a sibling change.
- CPython 3.12.13; Pydantic 2.13.4/core 2.46.4; AnyIO 4.12.1.

All probe endpoints are ordinary async functions. This isolates the proposed
field/provenance behavior from worker dispatch and context/thread observations.
Endpoint, schema and metadata objects are fixed after factory construction.
Repeated requests vary ordinary query input, not model definitions, schema hooks,
response-class defaults or cache contents. Public inheritance settings are
declared once. This slice makes no claim about mutable cache or model-rebuild
history, descriptor changes, dynamic DefaultPlaceholder values or cache lifetime
after a later route mutation.

No direct `Default` or `DefaultPlaceholder` import/call is used. Pinned
`fastapi/datastructures.py:153-176` marks them internal. Their immutable provenance
is reached through omitted public options versus concrete public response classes
on FastAPI, APIRouter, include_router and route declarations.

## Exact source contracts

All FastAPI paths below are relative to the pinned source checkout.

| Source | Contract exposed or required by the follow-on implementation |
| --- | --- |
| `fastapi/routing.py:1103-1114` | A truthy response model creates the response field while populating route state, with `mode="serialization"`; no field is created for an absent/false response model. |
| `fastapi/utils.py:58-78` | `create_model_field` constructs FieldInfo/ModelField at analysis. A PydanticSchemaGenerationError becomes FastAPIError, with suppressed exception context; unrelated schema-hook errors propagate. |
| `fastapi/_compat/v2.py:97-112` | FieldInfo is decomposed into annotation, metadata and attributes; these are distinct components of the adapter input. |
| `fastapi/_compat/v2.py:141-166` | ModelField eagerly creates one TypeAdapter from `Annotated[annotation, *metadata, Field(**attributes)]`; its warnings context ignores UnsupportedFieldAttributeWarning on the pinned Pydantic version. Configuration is preserved. |
| `fastapi/_compat/v2.py:174-189` | Validation uses that retained adapter and `from_attributes=True`. Only ValidationError is caught; error detail extraction and response-location regeneration are part of this stage. |
| `fastapi/_compat/v2.py:191-235` | Both dump_python(mode="json") and dump_json use the retained adapter with include/exclude, by_alias and exclusion flags. User serializer callbacks remain observable. |
| `fastapi/routing.py:316-338` | Validation scheduling follows original endpoint coroutine classification; serialization follows validation on the caller loop. This proposal uses async endpoints but must preserve this already separate worker boundary. |
| `fastapi/routing.py:1223-1248` | The handler captures the route/effective-context field and response configuration; request processing is not supposed to rebuild a field for every response. |
| `fastapi/routing.py:1430-1478` | An included route's effective context repopulates route state from its original declaration and include context. Its field belongs to that effective context; a global adapter keyed only by callable or annotation would erase distinct construction hooks. |
| `fastapi/utils.py:121-136` | Response-class merging returns the first non-DefaultPlaceholder, including explicit None, or the first placeholder when all settings retain defaults. |
| `fastapi/routing.py:2924-2926` | Route response_class has priority over the router's concrete default_response_class. Omitted placeholders retain provenance. |
| `fastapi/routing.py:1329-1331,1457-1461` | Include default merging retains parent settings and combines route, included-router and include-context precedence without replacing placeholder provenance with its wrapped class. |
| `fastapi/routing.py:396-399` | The handler separately unwraps actual_response_class for a later concrete construction call. |
| `fastapi/routing.py:711-714` | Returned Response bypasses response-field validation and serialization, even if the declared response_class would fail when called. |
| `fastapi/routing.py:724-748` | Eligibility is exactly `response_field is not None and isinstance(response_class, DefaultPlaceholder)`. Eligible content uses adapter dump_json and base Response with JSON media type. Concrete JSONResponse, inherited concrete classes and explicit None use the dump_python/class-call branch. |

Included route materialization can occur when a first public request resolves
the route tree, including the initial `/state` read. The fixture records hook
ordering and current user stage as they occur; it does not require that a hook
wait specifically for the first `/probe`. The implementation design must follow
the pinned route/effective-context cache lifecycle, not impose a fixture-specific
construction time. Calling the same included endpoint twice and its other prefix
exposes retention per effective context without inspecting private route caches.

## Case inventory and exact counts

| # | Case suffix | HTTP actions | Public observations |
| --- | --- | ---: | --- |
| 1 | direct-annotated-reuse | 4 | Setup-time schema hook; two values validated/serialized through an unchanged Annotated scalar declaration; ordered raw sends. |
| 2 | included-annotated-reuse | 7 | Register once on APIRouter, include twice, call left twice/right once; state reads expose original/effective-context construction and reuse boundaries. |
| 3 | field-metadata-warning-error-recovery | 5 | Annotated Field constraint plus field-specific aliases, ordered setup/request warning category/text, invalid response details/body, then valid response with the same declaration. |
| 4 | model-field-aliases-output-flags | 4 | Coercion, serialization alias, declared defaults, include/exclude, by_alias=False and all three exclusion flags; validator/serializer callback observations. |
| 5 | schema-hook-registration-error | 1 | User code catches a schema-hook ValueError during route registration; `/state` returns exact nested constructor outcome/class/message and setup/hook trace. |
| 6 | unsupported-model-construction-error | 0 | Uncaught public registration error for an unsupported type; exact factory construction result/class/message. |
| 7 | omitted-model-nan | 4 | Unchanged model with NaN plus serializer callbacks and omitted route class. Exact body/raw sends expose default JSON-byte behavior. |
| 8 | explicit-jsonresponse-model-nan | 4 | Same model/value with explicit JSONResponse; exact class-construction error, body and sends remain visible. |
| 9 | explicit-custom-class-model | 4 | Explicit JSONResponse subclass records construction/content type and adds a provenance header. |
| 10 | application-explicit-json-default-model-nan | 4 | Concrete JSONResponse inherited from FastAPI default_response_class; equality to the wrapped default does not grant placeholder eligibility. |
| 11 | router-custom-default-model | 4 | Distinct concrete app/router/include classes; router declaration priority is visible through callbacks/header/raw sends. |
| 12 | include-custom-default-model | 4 | Omitted router/route settings plus distinct app/include classes; include priority is visible. |
| 13 | route-explicit-over-inherited-model | 4 | Explicit route JSONResponse over distinct app/router/include concrete classes; NaN and callbacks expose retained concrete provenance. |
| 14 | inherited-omitted-defaults-model-nan | 4 | App/router/include/route all omit concrete classes; original placeholder provenance survives inclusion. |
| 15 | explicit-none-over-default-model | 4 | Explicit None has priority over a concrete app default; exact public construction/request errors, validation/serialization and sends are retained. |
| 16 | returned-response-bypasses-model-and-none | 4 | Declared traced scalar field plus None class, endpoint returns an ordinary JSONResponse with content outside that model; adapter construction remains visible and runtime bypass is directly observable. |
| | **Total** | **61** | **16 construction observations; 29 probes; 32 state reads.** |

## Observation and input integrity

The schema @9 runner compares exact construction outcomes, status, ordered
headers, bodies, application exceptions and ordered send message types. The
constraint failure additionally selects public `errors()` details and `body`.
No direct FastAPI exception implementation import is used. Generated errors are
observed through public route dispatch and the existing runner interface.

Because schema @9's HTTP asgi_send selector exposes only message types, the
ordinary user observer records every prior `/probe` send and exposes it through
the public `/state` JSONResponse. It recursively preserves bytes as hex, tuple
versus list, header order, every key and field presence. It never adds `more_body`,
decodes protocol bytes or fills missing keys. The `/state` response is excluded
from that recorder to avoid recursive state growth; it still receives the usual
runner HTTP/send/error observations. The original message is forwarded unchanged.

Pinned Starlette `starlette/responses.py:162-169` constructs normal start and body
messages; body `more_body` presence must remain exposed. Native FastAPI default
response construction (`FastApiCall::send_body`/`response_body` in
`fastapi-rs/src/application_runtime.rs`) is FastAPI owned. Concrete/returned
Response invocation uses sibling-owned generic response execution. Parent must
verify any reviewed send correction and actual sibling pin independently. No
normalization or generic sibling implementation is included in these drafts.

Warning records retain actual ordered category and message; no filename/line
projection is selected. User `warnings.catch_warnings` is an ordinary input and
the pinned source's narrower internal suppression remains effective inside it.
Only sequential requests are used. There are no clocks, sleeps, absolute thread
IDs, GC observations, concurrency race outcomes or implementation detection.
No NaN is placed into the recorder JSON: validation/serializer logs report its
value type and serializer configuration while actual response bytes/exceptions
are observed unchanged. The user output itself still contains the NaN.

## Bounded implementation design, separate from inputs

1. Introduce a Rust-owned response-field record at source-equivalent route state
   analysis. Its owned Python adapter and field input retain the canonical
   FieldInfo-derived annotation, metadata, attributes, mode and config. Match the
   source's narrow warning suppression and schema-generation exception mapping at
   construction, including early failures when the route is never requested.
   Python facade files remain direct reexports only; original FastAPI imports,
   Python helper implementations, unsafe and blanket lint suppressions are barred.
2. Retain that field for validation and both serializers. Repeated request errors
   and successes use the same constructed field. Materialize separate fields for
   original/effective included route contexts at the pinned lifecycle boundary;
   do not share adapters globally merely because model/callable objects match.
   Keep current worker scheduling and complete worker error-extraction/location
   stages intact. No app borrow may survive a schema/validator/serializer callback.
3. Preserve response-class provenance separately from its actual Python value.
   An omitted public option must be distinct from explicit None and from an
   explicitly supplied JSONResponse class. Merge public priorities with the
   source first-non-placeholder rule; carry provenance through route/include clones.
   A class identity/equality check or Option<PyAny> that conflates None/omission is
   insufficient. The selected actual class remains the original invocation object.
4. Run dump_json only for a retained field plus retained placeholder provenance;
   otherwise use dump_python(mode="json") then the selected concrete value's
   construction call. Keep user serializers, flags, warnings, errors, status,
   headers, content length and raw bytes exact. Preserve returned-Response bypass
   and function/request cleanup paths on every early or resumed failure.
5. Source endpoint-context introspection/cache timing is a separate requirement;
   do not infer that retaining an adapter fixes it. Mutable annotation/model
   rebuild, changing defaults, callable classification history, warning filters
   changed by callbacks and exotic descriptor/provider hooks remain unproven.

## Required later review and admission

1. Independent read-only review of source reachability, public-only observations,
   warning/error determinism, nested setup capture, alias semantics, raw-send
   losslessness, route/include context timing, schema @9 and manual action counts.
   The bounded review and static admission results are recorded below; they are
   not live source or target evidence.
2. Parent may copy corrected drafts into the repository only after review. Run
   normal formatting/lint and schema checks, then reviewed metadata/requirement
   mappings. Source tests/docs are evidence paths, not copied test bodies. Keep
   unsupported outcomes and compatibility ownership explicit.
3. Materialize with `make parity-inputs parity-index-update parity-validate`; run
   `make metadata-check`, facade/static contracts and atlas update for reviewed
   mappings. No fixture-ID runtime dispatch or adapter suppression for these cases.
4. Execute all inputs unchanged on isolated identity-checked pinned source and
   normal target processes. Compare complete selected public observations; keep
   fresh raw receipts. No fault-only promotion, expected-output addition,
   observation weakening or source/target-specific branch is permitted.
5. Implement only after the bounded plan is authorized, respecting source freeze.
   Parent owns builds, installs and verification; never run unit tests, pytest,
   unittest or Cargo test. No new performance comparison is equivalent merely
   because existing body-only benchmarks passed or this static proposal exists.

Adapter reuse and byte serialization may remove redundant work, but this proposal
contains no measured phase costs or speed claim. Fresh equivalent-work benchmarks
are eligible only after the new field/provenance gates and prior worker/classifier
and cleanup contracts pass with reviewed pins.

## Independent static review and admission

The existing schema @9 `read_recipe` loader accepted 16 parity cases, 61 HTTP
actions and 16 construction observations. Expanded paths are 32 `/state`, 18
`/probe`, 10 `/left/probe` and one `/right/probe`; action IDs are unique within
each case. Factory binding is the runner's positional
`create_app(factory_input, event_trace)`, and every selected observation uses the
existing schema/worker protocol. Static Ruff results are recorded at handoff.
On 2026-10-05, Ruff lint and format checks passed with the repository's explicit
`pyproject.toml` and caching disabled. Every source_evidence path exists in the
pinned source checkout. No factory, ASGI request, source oracle or target was
executed for these static checks.

With root approval, the public registration calls use
`app.get(...)(probe)`, `router.get(...)(probe)` and
`app.get('/state', response_model=None)(read_state)`. All response models, flags,
classes, setup stage labels, actions and observations are retained. Source
APIRouter.get uses the same route creation path. This keeps the proposal focused:
the current target's add_api_route rejects response configuration keywords,
whereas its get decorator accepts them. APIRouter exposes both by delegating to
its inner native FastAPI. Include default_response_class remains a deliberate
public implementation gap in the current target and is still supplied unchanged.

Public API mapping candidates are root FastAPI, FastAPI.__init__, FastAPI.get
and the public FastAPI.__call__ boundary for all cases; root APIRouter,
APIRouter.__init__, APIRouter.get and FastAPI.include_router for the five included
cases; root Request with its pinned Starlette query_params operation; and
fastapi.responses.JSONResponse for state and concrete/returned responses.
Pydantic metadata, schemas and callbacks are ordinary user inputs. Internal
Default/DefaultPlaceholder and ModelField types are neither imported nor
promoted to public candidates. The actual constructor and response error class
and unchanged message are observed, rather than importing or constructing
private FastAPI exceptions.

The review found no source input blocker: schema hooks are immutable, the scalar
constraint recovery uses the same declaration, included contexts are observed
without a requested materialization time, and returned Response bypasses the
declared model/class. Warnings retain actual category/message and all prior
probe sends retain field presence, bytes, container shapes and order. Errors
whose text includes a user class use the runner's deterministic workload module;
response-validation location text uses the identical workload path on both
sides. No raw object repr, clock, process/thread ID, expected output or private
Default import is selected. Eager field construction, effective-context reuse,
warning suppression, response-class provenance and exact serialization remain
live verification requirements, not support claims from this review.
