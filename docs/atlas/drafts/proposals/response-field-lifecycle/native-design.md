# Response-field lifetime and response-class provenance: native design

Read-only next-slice design, 2026-10-05. No Rust, metadata, recipes or sibling
files changed; no app, build, install or parity execution. Source contracts below
are established by reading pinned code. Native structures and sequencing are
proposals, with live verification still required.

## Inspected boundary

- FastAPI 0.141.1 `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`;
  Starlette 1.6.0; CPython 3.12.13; Pydantic 2.13.4/core 2.46.4.
- Actual saved directory is
  `docs/atlas/drafts/proposals/response-field-lifecycle/`, containing 16 proposed
  cases / 61 actions. Workload SHA256
  `a763538464f0e3a8809daa5fb55ba123a78b852d546170165a370e4f30682d68`;
  recipe `2213314fc5a3bbc6100ad791e61bbe2c0bfd61deb11ee25358392e12a6b1cd6a`.
- Inspected native HEAD `c4f829cb8ef0c562a9c468f2a4bd64d0afa4af32`;
  `application_runtime.rs` SHA256
  `974b025c982a64a933e58f4e32e6d20f80ef25245517dbf4ca1e304f8d704b34`.
- The recorded sibling BackgroundTasks crossing remains separate. This design
  does not repair, bypass or verify it.

## Source contracts

| Pinned FastAPI source | Established behavior |
| --- | --- |
| `routing.py:961-1119,1193-1223` | Direct APIRoute population constructs the primary field eagerly, after dependency/body analysis, when the resolved response model is truthy. Construction precedes appending the route. Additional-response fields have an earlier stage; streaming fields are distinct. |
| `utils.py:58-78`; `_compat/v2.py:75-112,141-166` | FieldInfo gets the original annotation, Undefined default and alias. The pinned compatibility decomposition omits Undefined attributes, rebuilds a fresh Field, and eagerly creates `TypeAdapter(Annotated[annotation,*metadata,Field(**attributes)], config=config)`. Only UnsupportedFieldAttributeWarning is ignored within this construction context. |
| `utils.py:58-78` | Pydantic-v1 rejection precedes field construction. Only PydanticSchemaGenerationError from ModelField construction is translated to FastAPIError with suppressed context. Unrelated user schema-hook errors propagate unchanged. |
| `_compat/v2.py:174-235`; `routing.py:316-338` | One retained adapter validates with from_attributes=True and performs both serializers. The full validate/errors/location stage runs on the loop for an original async endpoint, or in a worker for an original sync endpoint. Serialization then runs on the caller loop. |
| `routing.py:1285-1359,1430-1478,1586-1623,3282-3312` | Inclusion stores a branch/context. First traversal constructs all effective candidates of that visited branch. Each effective context owns a newly populated field. Successful candidates are cached by the original router version; no successful partial candidate cache is published if construction fails. |
| `routing.py:1225-1248,1262-1279,1750-1814,1844-1855` | Matching, route-context iteration and URL traversal can materialize included contexts. Included handler selection obtains its field from that effective context. Adapter lifetime and request-handler construction are distinct. |
| `utils.py:121-136`; `routing.py:1329-1331,1351-1353,1457-1461,2924-2926` | Response-class merging selects the first non-placeholder, including explicit None; otherwise it retains the first placeholder. Route, router, include and parent provenance survives merging. |
| `routing.py:396-399,711-748` | Actual response class is unwrapped for invocation. Returned Response bypasses validation/serialization. dump_json eligibility requires a field plus retained placeholder provenance. Other paths dump_python then call the selected actual value; None fails at that later call. |

## Proposed native ownership

1. Add an internal Rust `ResponseField` record containing name, FieldInfo,
   annotation/metadata/attribute construction input, retained adapter, mode and
   config. Owned `Py<...>` references suffice: request snapshots clone references
   to the same adapter. No global cache keyed by annotation or endpoint, no
   public ModelField promotion, and no Python facade helper.
   Preserve user metadata/state object identities; snapshots are owned reference
   copies, not deep copies that clone callbacks or their journals.
2. Give each original direct route one field owner. Give every included effective
   route context its own field owner. Represent unmaterialized included state
   separately from a materialized route with no field; Option::None cannot mean
   both. A successful primary field is never rebuilt in finish_endpoint.
3. Replace response-class Option fields with a choice retaining the original
   setting and a `Default`/`Explicit` category. Default keeps its placeholder and
   wrapped value; Explicit retains any original Python value, including PyNone.
   Resolve the actual invocation value at the source handler boundary. Class
   identity, equality, callability or equality to JSONResponse cannot determine
   default eligibility. Recognizing the existing native placeholder preserves
   explicitly passed signature-default objects without a new public factory.
4. Keep ResponseValidationState as an owned request snapshot: retained adapter,
   original content, serialization options, class choice/actual invocation value,
   status and endpoint context. Keep the existing regular private
   ResponseModelValidator and ResponseValidation pending continuation.

## Construction and callback boundaries

Direct registration at `PyOperationDecorator::__call__:4983-5165` should snapshot
app/router configuration under short borrows, release them, complete dependency
analysis and field creation, then commit the prepared route under a short mutable
borrow. Schema hooks may register other routes: do not hold a PyRef/PyRefMut,
RefCell borrow or app/cache mutex through FieldInfo, Field, TypeAdapter, annotation
truth testing, signature or Python metadata operations. Construct the field
before inserting the operation/named route, so a failed constructor leaves no
registered half-route.

Use a Rust helper with explicit enter/exit of Python warnings.catch_warnings.
Apply only the pinned UnsupportedFieldAttributeWarning filter; execute source
decomposition, fresh Field, Annotated and TypeAdapter inside that context; restore
it on success and error with the actual exception triple. Preserve failures of
the warning context itself. Do not use an infallible Drop callback or a broad
warning/error catch. Translate only the documented schema-generation error after
restoration, preserving the exact source message and suppression flag.

Current `pydantic_field_schema_annotation:8156-8188` is useful structure but is not
automatically an exact response-field builder: public FieldInfo.asdict includes
Undefined default whereas the pinned FastAPI compatibility helper omits it.
The pinned attribute sets otherwise match. Implement the source decomposition
explicitly, or prove/filter this difference before factoring a shared helper;
keep existing query-field callers' contract intact. `mode="serialization"` is
field metadata, not a TypeAdapter constructor keyword.

Included registration currently calls `merge_router_routes:4508-4640` under
destination/source borrows and eagerly flattens contexts. Do not add schema hooks
inside that function's present borrowing pattern. Store immutable declaration
snapshots and include choices without building included fields there. Extend
FastApiRouterInclude with branch identity, parent/source router, merged settings,
version and unmaterialized/materialized candidates. Build the whole candidate
vector outside app/source borrows and publish it only after complete success.
Leave the old/unmaterialized cache unchanged on error; retry reconstructs the
branch as source does. Capture the source version once; callback-driven mutation
does not justify a silent retry loop or altered hook counts in this slice.

FastAPI.include_router currently receives `&mut self`: PyO3 keeps that receiver
borrow for the entire call. Use an owned `slf: Py<Self>` receiver and explicit
short borrows for any callback-bearing include work; merely shortening local
borrows inside the existing method cannot release its receiver borrow. Apply
the same ownership pattern to APIRouter include operations before introducing
callback-bearing preparation there.

Materialization must follow ordered traversal, not "first selected endpoint" or
"all includes on the first request". At `FastApiCall::begin:9798-9960`, visit
include branches in source route order before the first matching direct/branch
route, materialize all candidates of each visited branch, then match inside it.
Use the same branch resolver for route-context/URL/OpenAPI traversal where those
operations visit branches. An initial /state located after two includes can
materialize both before any /probe. Native matching tables may remain an index,
but they must not skip these observable traversal steps. Reentrant/concurrent
materialization and mutable router history need separate source-backed review;
do not introduce an invented public "already materializing" error as parity.

Publish/swap Python-owned records under short borrows, then drop replaced
references after releasing them: finalizers can also call user code. No borrow
or cache lock should survive a response validator, serializer, response class,
returned Response or worker await. Source's own included-branch lock semantics
are a separate concurrency boundary, not permission to hold a native app borrow.

## Request integration and scheduling

- `finish_endpoint:10822-11059`: preserve returned-Response bypass first. Snapshot
  field/config/class choices under a short app borrow; remove the per-response
  TypeAdapter build at11015-11021. Route-time truth testing controls field absence.
- Retain ResponseModelValidator.validate:940-973, including ValidationError-only
  handling and error detail/location regeneration. Async original endpoint:
  invoke it directly on the loop. Sync original endpoint: submit the entire stage
  through pinned run_in_threadpool and keep ResponseValidation pending ownership.
- `finish_response_validation:11061-11119`: use that same retained adapter on the
  loop. Default category plus present field selects dump_json; explicit JSONResponse,
  inherited concrete classes and Explicit(PyNone) select dump_python(mode=json).
- `finish_serialized_response:11121-11167`: call the retained actual class for
  explicit choices, including None, after serialization. Keep no-field encoding,
  returned response, injected headers/status/background, raw body fields and
  function/request cleanup/error continuations source-aligned. Do not special-case
  NaN, named fixtures, model types or prior benchmark routes.

Streaming item adapters and additional-response/OpenAPI fields are distinct
owners/stages in source. Sixteen inputs do not justify claiming their lifetime
parity. Isolate ordinary primary-response work; changes to shared class merging
must still preserve prior streaming gates.

## Minimum admission and implementation sequence

1. Admit the immutable16 source inputs before implementing. Public decorators
   already accept their model/flag options; add_api_route expansion is unnecessary
   because the reviewed input uses app.get/router.get. Keep that independent input.
2. Add `default_response_class` to native FastAPI.include_router and
   APIRouter.include_router signatures (`:2700,3980`) with a distinguishable
   omitted default. Update FastAPI/APIRouter constructors, get/decorator options,
   ResponseModelOptions, PyOperationDecorator, RouterIncludePolicy and route
   storage to retain Explicit(None) versus Default. Do not reject explicit None
   early. Reviewed reflection overlays/signatures must describe the new bounded
   slice; internal Default classes remain internal.
3. Build and retain original fields with exact warning/error handling, then add
   lazy per-include effective fields and source-ordered traversal. Field reuse
   alone cannot satisfy included hook timing.
4. Wire retained snapshots into existing validation/serialization continuations,
   then review borrows and constructor rollback independently. Root owns Rust
   formatting, Clippy/static contracts, isolated live identities and parity.
5. Preserve current normal15 and prior worker/classifier/cleanup gates, record
   the actual sibling pin, and run equivalent benchmarks only after these new
   gates pass. No performance or broad compatibility claim follows from this
   design. Dynamic models/Default values, schema descriptors, endpoint-context
   cache timing, additional/streaming fields and reentrant/concurrent caches
   remain separately unproven.
