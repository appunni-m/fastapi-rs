# Additional response fields: bounded native ownership design

2026-10-05. Read-only design for the next slice. No tracked edit, prospective Rust
patch, build, installation, application/factory execution, native import,
comparison rerun or unit test. Only this temporary document was written.
Implementation is not authorized by this note and no new target support is claimed.

## Recommended bounded option

Implement the three independently authored lifecycle cases first, while retaining
the existing OpenAPI outputs through additional fields' owned adapters. This is
three normal cases / 15 HTTP actions / three construction observations: delayed
decorator attachment (3 actions), one original router in two nonempty include
prefixes (5), and second-extra refusal/retry (7). None requests OpenAPI. They expose
premature JSON hooks through public state, but do not establish positive JSON-hook
mode/order, shared definitions, OpenAPI cache recovery or arbitrary mutable history.

Root reports the unchanged-current pre-controls closed at
`parity-results/additional-response-field-wave/pre-openapi-controls/`: the existing
`additional-response-model-openapi` pointer case and
`path-operation-other-verbs-responses` description matrix case each pass with all
planned actions completed and equal initial/final snapshots. Their exact selected
public outputs are required regression gates. They do not establish hook timing or
complete schema equality beyond their declared selectors. Their runner is
`/private/tmp/fastapi-additional-response-field-openapi-pre-runner.py`, SHA256
`f1c1c42a0d26e7db4959007a5995125b75250289e859ed1bbd2a7c1e9bea3ea9`.

Keep primary and additional ResponseField owners distinct. Additional status fields
are documentation fields, never alternate runtime validators selected by an actual
response status. Returned Response bypass and primary response validation remain
unchanged. No Python facade helpers or original FastAPI runtime imports are needed.
The existing Rust ResponseField constructor already supplies the serialization-mode
FieldInfo/Annotated/TypeAdapter decomposition required for extra fields.

## Pinned source contract

Paths below are relative to `/Users/lazytrot/work/fastapi/fastapi` at FastAPI 0.141.1
commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`. Starlette 1.6.0 remains the sole
oracle; immutable sibling pin is `b4c8a65c85e1b0d251ca05874412811eaa3ac7b8`.

| Stage | Source and ordering |
| --- | --- |
| Saved declaration | `routing.py:2973-3038` returns a closure; fields and responses are processed when the endpoint is attached. The closure retains the supplied responses object. |
| Direct merge/publication | `routing.py:2923-2971` evaluates responses-or-empty, shallow-merges router defaults followed by route responses, constructs the route, then appends and marks routes changed. Nested response dictionaries are not deep-copied. |
| Names and metadata | `routing.py:1000-1037` sets metadata, endpoint-derived/provided name, compiled path, uppercase method set and unique ID before additional fields. `unique_id = operation_id or current_generate_unique_id(route)`. |
| Additional fields | `routing.py:1038-1054` visits response dictionaries in insertion order, asserts dict, gets model, and truth-tests it. Only truthy models receive the body-status assertion and fresh serialization ModelField named `Response_{status}_{unique_id}`. Falsy models retain response metadata without a field. |
| Remaining route construction | `routing.py:1056-1074` asserts callable and builds dependency/body state; generator and inferred return-model work follows. Primary response field is constructed at `1103-1114`, after its own truthiness/body-status check. |
| Included context | `routing.py:1426-1478` populates a new effective context from `{**include_context.responses, **original_route.responses}`, including newly owned extra and primary fields. It uses the effective prefixed path and original route name/operation ID. |
| Include composition | `routing.py:1327-1364` combines parent/include response mappings in source insertion/override order. At `1601-1624`, all own effective contexts are prepared before the branch vector/version is published; child branches remain independently lazy. |
| Field builder | `utils.py:58-80`, `_compat/v2.py:121-168`: same serialization field constructor, narrow schema-error translation and UnsupportedFieldAttributeWarning filter as primary fields. Arbitrary user-hook exceptions propagate unchanged. |
| Status assertion | `utils.py:26-39`: None and exact supported range/default strings permit a body; otherwise int(status) must be at least 200 and not 204, 205 or 304. Assertion text is `Status code {status} must not have a response body`. It is applied only when model is truthy. |
| OpenAPI field collection | `openapi/utils.py:551-580`: collects retained primary before extra fields, unlike core construction order. Traversing contexts can itself materialize includes. |
| JSON generation | `_compat/v2.py:285-345`: GenerateJsonSchema uses retained field adapters' core_schema with field/mode identities and shared generation; flattened model fields may additionally be constructed. Universal zero core construction during OpenAPI is not a source contract. |
| Extra schema attachment | `openapi/utils.py:476-516`: deepcopy extra response metadata, remove model, normalize status key, find retained field, merge its schema, derive description, and deep-merge response. `_compat/v2.py:256-282` applies field title or alias/name when schema has no $ref. |
| Application cache | `applications.py:1084-1104`: read route version, generate only for false/obsolete cache, publish complete schema on success and retain the version captured before generation. Failed generation leaves prior cache unchanged. |

## Current native integration points and actual gaps

The source read was at HEAD `90556f4d714f24e2c389675e48f038b98a2becad`.

- `application_runtime.rs:5185-5249` parses responses and builds raw TypeAdapters
  plus JSON schemas. `operation_decorator:5270-5308` calls it while creating the
  saved decorator, before the endpoint is supplied.
- `PyOperationDecorator::__call__:5313-5484` builds CallablePlan before the primary
  field. It currently stores only OpenApiAdditionalResponse schema descriptions.
  `FastApiRoute:967-1008` has no extra-field owner.
- `merge_router_routes:4838-4951` clones frozen extra schemas while marking only
  the primary field deferred. It already reanalyzes CallablePlan and route metadata
  at include time under app/source borrows; that existing timing/borrow gap is not
  solved by a field-only lifecycle slice.
- `ResponseFieldInput/materialize_included_response_fields:1438-1543` snapshots
  primary inputs under a short borrow, builds a full own branch outside it,
  atomically replaces states, marks ready and drops retired states afterward.
  Extend this mechanism to a primary-plus-extra field bundle.
- `response_field.rs:44-185` owns annotation, FieldInfo decomposition, adapter and
  name. New extra fields can call ResponseField::new directly. clone_ref copies
  references without rebuilding an adapter and is suitable for owned snapshots.
- `openapi:3085-3106`, `openapi_document:3888-3911` and the ASGI OpenAPI entry
  `begin:10172-10176` currently hold the app borrow through schema generation.
  `openapi_operation:3913-4172` does not use its &self argument; its route inputs
  can be cloned into an owned snapshot without redesigning schema assembly.
- `openapi.rs:21-25` is a presentation value containing status/description/schema,
  not a route field owner. Keep it a transient OpenAPI output. Existing one-field
  schema generation/normalization may be reused for additional retained adapters.
  The existing primary, request/body, stream and shared-definition generation
  gaps remain explicit.

## Minimal retained state

Names below are proposed private Rust names, not public API additions.

1. PyOperationDecorator stores `responses: Option<Py<PyAny>>` directly. Declaration
   performs no response cast, key traversal, description/model extraction,
   truthiness, adapter creation or JSON generation. Defer current subset validation
   to endpoint attachment. Capture the object, not an eager copied vector.
2. Original FastApiRoute stores an owned, freshly shallow-merged outer PyDict of
   response records. Preserve insertion order and owned references to each nested
   record and annotation. Do not freeze raw descriptions/models at declaration.
   With current native signatures, inherited responses are empty; do not pretend
   unsupported constructor/include responses keywords are supported.
3. A ready route field bundle contains an independent `primary: Option<ResponseField>`
   and an ordered vector of extra entries. Each extra entry owns status key/label,
   its response metadata reference and `field: Option<ResponseField>`; description
   and model remain recoverable from the raw record. Description-only/falsy entries
   still exist but have no field. Each truthy entry calls ResponseField::new even if
   another entry uses the same annotation. No per-model adapter cache is introduced.
4. Replace the primary-only deferred/ready state with a deferred/ready bundle, or
   keep two states published in one nonfallible branch commit. A single bundle is
   simpler to prevent ready-primary/deferred-extra combinations. Request response
   handling clones only its primary owner. OpenAPI snapshots may clone extra owners.
5. Included routes retain owned raw declaration records separately from deferred
   field owners. Preparing each context creates its own effective outer mapping
   and new fields; it never clones the original route's field owners into an include.
   A repeated request reuses that context's bundle; a distinct prefix owns another.

Keeping Py<PyAny>/Py<PyDict> values owned avoids lifetime references to borrowed
application storage. No unsafe, Rc/RefCell cross-thread bridge, Python helper or
public ModelField/Default promotion is required.

## Endpoint attachment ordering

Prepare the whole native route outside an app borrow:

1. Clone app/router defaults and prefix under a short borrow. Release it before
   endpoint attributes, formatting, response dict work, truthiness or callbacks.
2. Establish route name, path format/converters, effective scope path and unique ID.
   Source name/path metadata precedes extra hooks. Use the already selected route
   operation ID or the generated ID from that effective name/path/method; an empty
   operation_id uses the generated ID, as source `or` does. Reuse that one ID for
   all fields of this context. Do not derive names from a later endpoint.__name__
   lookup during OpenAPI.
3. Normalize/merge responses at attachment, then walk entries in source order.
   For each: check dict, get model, truth-test once, enforce body status for truthy
   models, and construct its owned field before proceeding to the next entry.
   Do not first truth-test all models or preconstruct later entries. Keep exact
   source assertion text and ordinary schema warnings/errors. Existing restricted
   description/key policy can be checked here; it remains an explicit unsupported
   subset, not a source-equivalent general response parser.
4. Only after extra fields succeed, assert callable, build/prepend the existing
   CallablePlan/dependency/body state, detect streaming/inferred response model,
   and construct the primary field with its existing contract. Extra fields are
   needed even when primary is None or endpoint returns an ordinary Response.
5. Finish route views/registration inputs, then take a brief mutable app borrow to
   publish the fully prepared route. No Python callback is introduced at commit.
   A field/dependency failure publishes no route or field bundle. Do not overwrite
   Python owners by assignment while holding a borrow; use replacement plus an
   outside-borrow retired drop. Existing operation-table failure atomicity remains
   its own boundary and must not be silently claimed fixed by field preparation.

For plain integer status keys, use the source predicate without narrowing to a
new u16 conversion: the existing parser accepts Python ints of arbitrary width.
False models must skip status assertion. Source accepts more key/status forms
than the native integer-only policy; do not broaden or silently normalize those
forms in this slice. Model truthiness and formatting may invoke user code and must
be outside borrows. The primary u16 status signature is an existing separate bound.

## Included context preparation and branch commit

Extend ResponseFieldInput with owned raw additional response records plus that
context's name, effective path, method and operation ID. Add all extra fields first
and primary afterward to each locally prepared bundle. Context merge priority is
parent → include → child include → original route; overwriting a key preserves the
first insertion position. Current supported empty inherited mapping simplifies
this to fresh context construction from original records; raw input storage should
not make a later full merge implementation impossible.

Use the existing branch visit schedule unchanged. For each reached branch:

- Snapshot all direct context inputs while borrowed, including raw records and
  primary annotations. Release the borrow before model truthiness, ResponseField
  construction, errors/warnings, field-name formatting or reference destruction.
- Prepare every direct context's entire bundle in a local vector. If the second
  extra or a later own route fails, publish none of that branch's bundles. Drop
  all successfully prepared fields outside any borrow, then propagate the actual
  exception. Retry reconstructs that branch's own fields from its retained inputs.
- Validate every destination and branch marker before moving prepared values.
  Commit with nonfallible replacements, then mark ready. Collect old bundles and
  release the borrow before dropping them. No callback can observe a partially
  published own branch.
- Child branches retain independent readiness and failure behavior. An already
  published parent's fields survive a later child failure; do not turn traversal
  into one global transaction or roll a parent back on a child exception.

This preserves the source field bundle publication discipline for immutable
selected declarations. It does not move the current include-time CallablePlan
work to traversal, establish source lock/version/reentrant behavior, or prove
mutable route/metadata history. New schema callbacks and retired drops are outside
borrows; the preexisting include-time callback-under-borrow gap remains stated.

## Bounded OpenAPI integration, both entry points

The purpose of this step is to keep existing schema outputs and generate *extra*
JSON schemas from retained extra adapters. It does not reimplement source shared
schema generation or change the existing primary/request/stream schema pipeline.

### Owned cache-miss service

Change public openapi() to receive an owned `slf: Py<Self>` and call a Rust-owned
service. The ASGI /openapi.json branch calls that same service with self.app,
removing its surrounding app.borrow(). Root-path document adjustment, encoding
and sending also occur after borrows are released. Public return/ASGI contract and
Python facade exports remain unchanged.

1. Under a short app borrow/cache lock, clone version and cached schema references.
   Release both before evaluating cache truthiness. A valid nonempty cache returns
   directly; do not reconstruct fields or schemas on a hit.
2. On a miss, call materialize_included_response_fields(app, None) to prepare all
   reached included bundles before JSON generation, outside the app borrow. The
   immutable branch walker already enumerates own contexts before children.
3. Snapshot the full existing OpenAPI metadata and eligible routes into owned
   OpenApiAppSnapshot/OpenApiRouteSnapshot values under a short borrow: Rust
   strings/flags, Py reference clones, response class choice, CallablePlan::clone_ref,
   response model/stream inputs, raw extra records and ready extra-field owners.
   Snapshot references only; no endpoint attribute read, dict traversal/extraction,
   adapter/core_schema access, model-name lookup or schema generation in this block.
   These snapshots retain inputs needed for the complete existing document, not
   selected pointers or a reduced hardcoded schema.
4. Run the existing per-operation body/parameter/primary/stream generation and
   document assembly against owned snapshots outside app borrows. Drop the unused
   &self parameter on openapi_operation. Keep its existing algorithm and order;
   do not replace primary/request adapters or normalize additional outputs to hide
   a difference. Generate extra schemas in the additional phase from its retained
   adapter.core_schema through the current one-field GenerateJsonSchema path.
5. Publish only a fully generated schema. Use mem::replace to move the old schema
   out of the cache lock, record the version captured before generation, release
   lock/borrow and drop the retired schema. On error, leave the previous cache and
   version unchanged. Do not hold the cache lock across Python calls. A callback
   changing route version must not cause an old document to be marked with a newer
   version. Correct concurrent/reentrant publication still needs separate gates.

The explicit openapi_schema setter currently replaces a Python value while its
mutex is held. If this cache service touches that path, use the same outside-lock
retired-drop pattern without changing the setter's public cache semantics. General
setter/finalizer reentrancy is not proved by the selected cases.

### Retained-extra adapter schema helper

Factor the existing pydantic_schema_with_config generation half so it can accept
an existing adapter/core schema; do not call TypeAdapter(annotation) for extras.
Use the native FastApiGenerateJsonSchema class already exported internally by Rust,
ref_template `#/components/schemas/{model}` and serialization mode. Generate the
schema plus definitions and retain the full result in transient
OpenApiAdditionalResponse values. Keep existing normalization/component assembly.
If batching is later introduced, use distinct internal field keys rather than
annotation or name keys, since same-model and same-name owners can be distinct.

For every non-$ref field schema, source overwrites the generated title with
field.field_info.title or the serialization alias/alias/name transformed through
Python str.title().replace("_", " "); do not apply a setdefault-only rule. Preserve
that retained metadata and field name, and leave $ref schemas untouched. These
attribute reads and string calls occur outside application borrows. The existing
TeaError extra-model control covers a $ref, not this flat-schema title branch.
A separate small positive Annotated/Field OpenAPI gate is required for that branch.
For the present plain integer/explicit-description
subset, schema/model-name extraction and description handling can retain the
existing public output format. Names are `Response_{status}_{context_unique_id}`.
Do not let the assembler overwrite explicit Field title/alias with a freshly
computed endpoint operation name. Existing richer alias/title/collision behavior
needs dedicated inputs before broad claims.

The current one-field generator is intentionally not the source's one shared
field_mapping/definitions pass. Primary/body/parameter/stream fields still build
raw adapters through the old paths; source flattened-model discovery may build
additional fields at OpenAPI time. Shared validation/serialization model modes,
computed fields, collisions, callbacks/webhooks, duplicate IDs and full JSON hook
ordering remain separate gaps. Primitive metadata lifecycle inputs avoid those
additional source phases. Public get_openapi(routes=...) has its existing simple
native-route limitation; do not expand that API in this slice.

## Existing public subset and mutation risks

- Supported declarations for this slice are app/router get/post/put/delete/patch/
  head/options/trace with route-level responses. Router decorators delegate to
  native inner FastAPI. The current api_route/add_api_route signatures omit these
  response keywords; APIRouter constructor and include_router omit responses.
  Use existing verb APIs, not signature expansion.
- Native response policy is integer keys excluding bool, dict entries containing
  only description/model, explicit nonempty string description. Source accepts
  wider dict metadata, string/range/default statuses, missing descriptions and
  response dictionaries/subclasses; those remain unsupported. Model-free entries
  still affect OpenAPI. Do not treat the policy checks as source parity.
- Preserve the raw supplied outer object until saved decorator invocation, so
  reassignment/mutation before attachment is not missed. Attachment creates the
  source-style fresh shallow outer mapping; nested dictionaries/models are shared
  references. Deep-copying or eagerly freezing annotations loses source behavior.
- Original fields remain owned after attachment; reassigning a response record's
  model does not rebuild an original field. A not-yet-materialized include reads
  its appropriate original response records when building its new field. Freezing
  nested model/description values at include time would introduce a further gap.
- Current flattened inclusion captures route lists/options and does not follow
  replaced public route.responses, outer-key additions after inclusion, route
  version refresh or arbitrary mutation. If selected fields are immutable, keep
  these limitations explicit; preserving owned records is not a mutable-history
  proof. Custom dict/status truthiness/hash/format hooks, namespace rebinding and
  annotation mutation likewise need separate source-backed inputs.
- Source default ID uses one member of the method set. Bound this implementation
  to existing single-method verb decorators and immutable effective names/paths;
  custom generate_unique_id_function, multi-method grouping and Unicode/name/ID
  history remain separate. Empty string operation_id must follow source fallback.

## Implementation review and evidence gates

1. Freeze independent input-only lifecycle3 before any native edit. Confirm factory,
   schema@9, exact constructor/status/ordered headers/body/warnings/errors/raw-send
   records, no expected outputs or native branch detection. Proposal author and
   reviewer retain independent provenance. No new native fault injection is needed.
2. Run pinned source and unchanged target against those same bytes, preserving
   hashes, all planned actions and failures. Root owns execution/authorization.
   Pre-control pointer/description receipts remain separate regression evidence.
3. Review direct extra-before-plan-before-primary ordering, raw object capture,
   one truth-test per entry, false-model behavior and exact assertion/schema-error/
   warning semantics. Review two same-model extra owners and distinct prefixes.
4. Audit every borrow/drop edge: successful construction, partial preparation
   failure, lost destination, cache hit/miss, GenerateJsonSchema error and cache
   replacement. No Python call/attribute/format/truthiness/serialization or last
   reference drop may be added inside app/cache borrow or lock regions.
5. Once authorized, run formatting/strict Clippy and static policy/metadata/facade
   checks; no unit tests, unsafe or suppressions. Then live lifecycle3, prior full
   regression, exact existing OpenAPI pointer/description controls, same fixed-build
   coverage/fault receipts and normal restoration as root selects.
6. Positive OpenAPI hook/order/cache failure, body-forbidden extra status, falsy
   model, scalar/Annotated Field alias/title, schema-generation translation and
   generator/stream contexts are important next public gates if support claims
   expand. The selected lifecycle3 and old pointer/description controls alone
   must not be presented as complete additional-response/OpenAPI compatibility.

No prospective patch was authored. This plan supports a bounded owned-field repair
and full existing OpenAPI output preservation; its known gaps remain distinct from
future shared-schema or dynamic-route work.

## Frozen read bindings

| File | SHA256 |
| --- | --- |
| `fastapi-rs/src/application_runtime.rs` | `9608a3aacce77d8583617eed6a840dd48910fee3a0f256cb1463cd16b2dfeaad` |
| `fastapi-rs/src/response_field.rs` | `aa943aa0caa352ba579b58f9a1b3c0ee4f660c3f9400366d023b954e97aba825` |
| `fastapi-rs/src/openapi.rs` | `7b5f2109c53620a9ae7ed8c02e7ac6df31db5c1f944bd9a794568e036ec893dc` |
| `../fastapi/fastapi/routing.py` | `7b1ef65fb6b209445dc43be070a23324b7879aef9c6b9f63e6968234b7723b55` |
| `../fastapi/fastapi/openapi/utils.py` | `81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527` |
| `../fastapi/fastapi/_compat/v2.py` | `b031b28b588a4855bd2ee27b9f807ad7ed72ad0235347452c2c15144bb8527c9` |
| `../fastapi/fastapi/utils.py` | `0d7d15ae73307d5b19c51cfc222b50e36736fbef9f0f398566479131947650ca` |

These are design read bindings only, not live build or coverage identities.
