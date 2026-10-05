# Response-field next controls and source-gap priority

2026-10-05. Read-only source/design note after traversal7/helper review. No active
or inactive recipe/workload was authored or changed, no tracked/sibling edit,
application import/execution, build or installation. The current traversal7
remains frozen; parent owns its admission and measurements.

## One prospective terminal-405 control

Use the unchanged traversal workload's public declarative factory, with `/state`
still registered first. Declare these immutable ordinary routes:

- Direct POST `/branch/item`, one traced int response model.
- Include `/branch`: GET `/item`, a different traced int response model.
- Later include `/later`: GET `/other`, another traced int response model.

One prospective case has **seven HTTP actions and one construction observation**:
state; PUT `/branch/item`; state; GET `/branch/item`; state; POST `/branch/item`;
state. Values/labels are independent ordinary user inputs. Keep the existing exact
status/ordered headers/body/application-error selectors, ordered message types,
and lossless raw sends and schema/endpoint/validator/serializer journal through
the state responses. No stored status, Allow value, count, error or other expected
output is needed. No dependency/fault injection or new implementation branch is
needed.

### What it adds beyond partial-to-full traversal7

The existing POST-before-included-GET case sends GET, so a later FULL wins and
normal scanning stops at that full match; it then sends an earlier FULL POST.
It never dispatches a retained PARTIAL. PUT over the proposed declarations has
two partial candidates and no full candidate, so source must finish scanning the
later unrelated include, then dispatch the first retained direct POST partial.
The actual terminal405, ordered Allow header/body/raw messages, absent endpoint
invocations and additional later-branch construction are observed independently.
Subsequent full GET/POST requests observe reuse/normal recovery over unchanged
declarations.

Thus this is one additional normal contract: **first-partial retention through a
complete scan followed by terminal405 dispatch**, including visited fields after
the partial. It is not redundant with the existing later-full control. Source
`routing.py:2719-2743` performs the full scan before handling the saved partial;
redirect search at2744 is reached only when no partial exists. The original
Starlette route's method rejection/default exception handling remains generic
and sibling-owned. The additional field-traversal observation belongs to FastAPI.

Current native `begin`10261-10274 maps MethodNotAllowed to full_match=None, visits
all branches, and only afterwards constructs its405 response at10343-10357. The
operation/sibling table retains the first partial while seeking a later full
(`operation.rs:246-282`; b4c8a65 `route_table.rs:555-583`). Static reading predicts
this immutable control fits the current code; it is new evidence to run, not a
reason to change matching code now. It adds **1case/7actions/1construction**, and
does not claim generic matching, custom converters, mount or redirect coverage.

## Higher-return separate gap: retained additional response fields

This is distinct from primary fields, concurrent branch locking, mutable version
refresh and the native reviewer's child-failure-after-parent-publication plan.
The latter should stay a separate small traversal control: the parent own cache
succeeds before a reached child fails, so retry should retain parent hooks but
rebuild the child. Traversal7's own-vector rejection does not establish that.

### Exact source contract

1. Public APIRouter.api_route2973-3038 returns a decorator without constructing
   response fields; the closure calls add_api_route when the endpoint is attached.
   FastAPI.get delegates through this same public route declaration path.
2. In `_populate_api_route_state`, route metadata/path/unique ID is established,
   then `responses.items()` is visited in insertion order at1038-1054. For each
   dict entry, model is fetched and truth-tested. Truthy models first receive the
   body-allowed status assertion, then `create_model_field` with
   `Response_{status}_{unique_id}` and **mode="serialization"**. Falsy models
   produce no field. These additional fields are retained in route.response_fields.
3. This stage precedes endpoint callable/dependency/body analysis at1056-1074 and
   primary response-field construction at1103-1114. It completes before publishing
   the direct route (`add_api_route:2969-2971`). Its field builder has the same
   FieldInfo/metadata/narrow warning/error translation as the primary builder.
4. Each reached effective API route context reruns that population from its
   merged responses (`from_api_route:1430-1478`). The branch publishes only after
   all own effective contexts succeed (`effective_candidates:1601-1624`). A new
   include context therefore owns new additional fields, not copies of a frozen
   JSON-schema result. An unvisited child retains no new effective adapter yet.
5. Ordinary runtime response validation uses the primary response_field;
   additional status fields are not selected as alternate runtime validators.
   Returning a Response still bypasses primary processing. Field construction
   occurs even if that additional status is never returned.
6. OpenAPI later collects retained response_fields atutils.py551-575 and generates
   definitions/schemas from them, then merges the extra response at476-515. Core
   field construction and JSON-schema generation are separate user-hook phases.

### Concrete current target divergence

`operation_decorator`5279 calls `additional_response_descriptions`5185 at decorator
creation. That parser invokes `pydantic_schema`5230 for every model except literal
None. At8119-8178 this creates a fresh raw TypeAdapter and immediately invokes
GenerateJsonSchema.generate_definitions. Thus both core-schema and JSON-schema
user hooks can run before the endpoint is attached. It stores only status,
description, model name and JSON schema in `OpenApiAdditionalResponse`
(`openapi.rs:20-25`), not the annotation/metadata/field/adapter.

`merge_router_routes`4922 clones those OpenAPI descriptions/schemas; the lazy
field input1447 only includes the primary model. Neither direct attachment nor
later include visitation builds retained additional fields. The parser also
tests only None rather than the source's truthiness and does not perform the
source's additional status body assertion. These are concrete source differences;
no live outcome is claimed here.

The existing admitted subset requires integer status keys and explicit nonempty
description/model-only entries. New lifecycle inputs can initially keep that
shape, avoiding unrelated string/range/default statuses, description fallback,
headers/content deep merge, include-level responses signature expansion, aliases,
namespace rebinding or mutable mapping history. Those wider gaps remain explicit.

### Small independent input plan, before implementation

Use ordinary public factories/endpoints and named user metadata implementing core
and JSON-schema hook protocols, with phase labels and JSON journals. No private
FieldInfo/ModelField/cache access, expected outputs, target detection, raw reprs,
clocks, concurrency or normalizations. JSON-schema hooks can be defined without
requesting OpenAPI, making any premature registration-time call visible in state.

Three focused prospective scenarios are sufficient for the first slice:

- **Delayed decorator attachment (3HTTP actions).** Record before/after
  `saved=app.get(..., responses={409:{description:..., model:traced_extra}},
  response_model=traced_primary)` and before/after saved(endpoint). Initial state
  observes actual core/JSON hook phases and extra-before-primary order. Probe plus
  state observes retained primary callbacks while the unused extra model receives
  no runtime value validation/serialization. No OpenAPI request is necessary to
  catch the eager JSON-hook difference.
- **Two include contexts (5HTTP actions).** One original router owns an extra
  traced model and is included twice with nonempty prefixes. Early state; left;
  state; right; state. Observe original attachment, each visited context's own
  additional construction and reuse. An ordinary returned JSONResponse can be
  outside the extra model; this must not introduce runtime status-model validation.
- **Later additional-field failure and retry (7HTTP actions).** One included route
  has two distinct extra models in insertion order plus a primary model. Arm one
  named user core hook to reject the second extra only after registration/includes.
  State; branch request; state; retry; state; retained repeat; state. Actual public
  handler class/message/status/raw-send trace and extra/primary construction order
  expose the field bundle's rollback, retry and successful retention. No yielded
  resource has entered at matching-time failure; no fault hook is justified.

This optional lifecycle plan is **3normal cases/15HTTP actions/3construction
observations**, separate from the terminal405 case. These are proposed input
shapes only, not authored or selected evidence. A source-only reachability gate
and unchanged-target diagnosis should precede any native implementation.

### Minimal native integration direction

Retain raw route responses until decorator invocation, then snapshot ordinary
additional-field inputs/keys in source order and build owned ResponseFields in
serialization mode, outside application borrows, before dependency/body and
primary-field work. Publish the route only after its full construction succeeds.
Additional field names use the route's unique ID; primary and additional fields
remain different owners. Do not add alternate runtime response validation based
on an actual status.

Extend each included route's deferred preparation to a field bundle containing
its additional fields followed by its primary field; prepare all own bundles
before committing that branch. Preserve branch rollback, owned request snapshots
and retired-reference destruction outside app borrows. The existing primary
ResponseField helper can construct the extra serialization-mode fields; it must
not be replaced with eager raw TypeAdapter/JSON-schema snapshots.

OpenAPI generation should use retained adapters' core schemas rather than build
fresh adapters. Exact shared-definition generation, field-mode mapping and the
existing OpenAPI callback-under-borrow boundary require their own read/review and
public gates if that phase is included. Do not represent per-type frozen schema
reuse as source field retention or infer complete OpenAPI/alias/history support
from the first lifecycle inputs. No Rust patch is proposed/applied in this note.
