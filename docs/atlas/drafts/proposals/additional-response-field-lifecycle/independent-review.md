# Additional response fields: independent source/input review

2026-10-05. Independent review of the frozen inactive additional3 proposal is
complete. No source/input/selector admission blocker was found for the selected
immutable boundary. This note is not live support evidence. Only this temporary
review note is writable in this task. No active
input, metadata, generated file, runtime, tracked source, sibling or measurement
was edited; no application import, native binary read, worker/parity execution,
build, installation or unit test occurred.

## Independently rechecked pinned source

Verified source HEADs:

- FastAPI0.141.1: `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette1.6.0 sole oracle: `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.

The fixed profile additionally declares Python3.12.13, Pydantic2.13.4/core2.46.4
and immutable Starlette-RS b4c8a65. The priority note was read as direction;
the source conclusions below were rederived from the pinned files.

| Pinned source | Contract |
| --- | --- |
| `applications.py:1993-2017`; `routing.py:2973-3033` | Public get/api_route returns a decorator. It calls add_api_route only when that decorator is applied to an endpoint; response-field construction is not decorator creation work. |
| `routing.py:2922-2971` | Router responses precede route responses in the merged dictionary; overrides replace values without moving an existing key's initial position. Route construction completes before append/route-version publication. |
| `routing.py:1038-1054` | Visit responses.items in insertion order, require each response value to be a dict, fetch and truth-test model. A truthy model gets the status-body assertion, then a retained field named Response_status_uniqueid in serialization mode. Falsy models produce no field. |
| `routing.py:1056-1074,1103-1114` | The additional-field loop completes before endpoint callability/dependency/body analysis, generator analysis and primary response-field construction. Ordinary route metadata/path/unique-ID work at995-1037 precedes the additional loop; extras are not universally the first possible user callback. |
| `utils.py:58-78`; `_compat/v2.py:141-166` | FieldInfo/Annotated metadata reconstruction and TypeAdapter construction use the same helper as primary fields, with scoped UnsupportedFieldAttributeWarning suppression. Only PydanticSchemaGenerationError is translated; a separate named user ValueError raised by a schema hook propagates. |
| `routing.py:1430-1478,1601-1624` | Each effective included context reruns population with its merged responses. Own contexts are built in a local vector; branch publication/version assignment occurs only after all own contexts succeed. A later extra refusal leaves that branch uncommitted, and retry reconstructs its earlier extras. Child descriptors are created during the parent loop but child fields remain lazy. |
| `routing.py:1730-1803,2719-2743,3309-3312` | Matching builds a reached branch before candidate iteration; earlier FULL stops traversal. A repeated original router under separate nonempty prefixes supplies independent included contexts. Handling rematches retained successful contexts. |
| `routing.py:1232-1247,705-747` | Ordinary runtime validation receives the primary response_field only. An additional status model is not selected as an alternate runtime validator; a returned Response bypasses primary processing even though its fields have already been constructed. |

Public hook side effects are not rolled back when field construction fails.
The input journal can expose repeated construction without inspecting private
cache/adapter identity. No assertion is made about immediate destruction of
failed local fields: exception tracebacks can retain construction locals.

## Core construction versus OpenAPI JSON-schema phase

`openapi/utils.py:551-580` traverses effective contexts and collects primary
response fields before additional fields in their retained insertion order.
This collection order differs from route-time core construction order.
`get_openapi:620-627` then calls `_compat/v2.py:get_definitions:285-346`, whose
selected inputs use each retained `field._type_adapter.core_schema` at324-336
with that field's mode (subject to the public separate-schema option).
`openapi/utils.py:473-516` subsequently merges each additional response and
its generated field schema, removes the user model key and determines its
description. Public `FastAPI.openapi:1070-1103` retains the completed document
for the router version; the ordinary OpenAPI HTTP endpoint calls it at1108-1118.

Do not claim that OpenAPI universally performs zero new core construction:
`get_definitions:303-318` also constructs fields for flattened models not among
the input annotations. Primitive Annotated int metadata controls avoid adding
that broader nested-model phase. A workload that defines JSON-schema hooks but
never requests OpenAPI positively gates premature JSON-hook invocation; it
does not gate later OpenAPI hook order/counts, serialization/validation schema
mapping, shared definitions, aliases or cached document identity.

## Prospective source-only and unchanged-target orchestration

Read-only review of `/private/tmp/fastapi-additional-response-field-pre-runner.py`
verified SHA256
`9cadec4ae67d0fd5dfe581acce5dedb445365733220f7aef2e001a804f471a53`.
Its imported hashing helper is SHA256
`4caa87ea24021076b96245fb5e005efcf6cd9a70950fd675bf8bea757b52a7f5`;
the helper's executable main is guarded and import performs no run/build/install.

The runner selects the whole prospective additional-response-field-lifecycle
ASGI workflow using canonical CLI commands. Before invoking target it requires
oracle exit0, exact case/action inventories/IDs, each source case/action
completed and construction outcome ok. Public handled schema refusals remain
normal source actions; there are no prescribed statuses/bodies/hook counts.
It uses the fixed source interpreter, restored normal target interpreter and
exact b4c8a65 sibling path. Canonical schema9 target identity requires a normal
fault_injection_compiled=False build for an all-parity workflow.

Initial/final snapshots bind tracked/nonignored source trees, materialized input
and the unchanged native pair; target-reported source/native digests must equal
the initial snapshot. Logs and canonical artifacts are preserved. A parity
mismatch deliberately exits1 without runtime edits/builds. A failed source
reachability gate stops before target and does not produce a completed-stage
final receipt; it is an input/source diagnostic to resolve first. I did not run
this helper or inspect native binary bytes. Frozen input admission must precede
its actual execution by the parent.

## Saved existing OpenAPI output controls

The parent separately executed two unchanged-target legacy controls before
admission. I audited their saved JSON receipts under
`parity-results/additional-response-field-wave/pre-openapi-controls/` without
running their helper or reading current native bytes. Helper SHA256 is
`f1c1c42a0d26e7db4959007a5995125b75250289e859ed1bbd2a7c1e9bea3ea9`.

Both source/target workflows, cases and sole HTTP actions actually completed.
Each comparison reports selected1/passed1/failed0/not_run0. The first selects
status, the tea418 response and TeaError component; the second selects status
and additional descriptions for two statuses across the declared app/router
verbs. Neither selects full raw send fields, construction-hook timing or shared
JSON-schema generation.

Initial/final snapshots are byte-identical, SHA256
`be10a43e105dbcc2730454ee937572b3c59f22d8c8a41710772bd25cc0a5af06`;
the run manifest is
`ba8adf939a01ac8226684de5edeede23fa950edacc0fc4d40cf97f0edcbd3be4`.
Both target artifacts bind the saved combined source
`1b87fd3e25b6307ba2582a50626fc014f16455c7603aeec9bef4cdc67fc2eadb`
and native pair
`10b3932cd4a42cd7b34d69043bfa54992383fb254673507230523a646f079a73`
to those snapshots and exact b4c8a65 sibling revision. These legacy schema2
records omit the fault-compiled flag; the canonical normal target setup still
rejects a compiled fault extension. Do not present a missing receipt flag as an
explicit False observation or reuse this earlier source digest after admission.

| Family/lane | Saved artifact | SHA256 |
| --- | --- | --- |
| model/source | `oracle/c3c23d55-b181-4af2-9b40-096ad5c49091.json` | `7919fc33dff00a8bea0f3e7c1243ffd837772cef615b6c0e9b46eb087e08ed70` |
| model/target | `target/93fd2c8f-f53a-4bc9-bbd8-447991ee25c6.json` | `36116e12ecce0153d12fd3bfe515dcab7e91bd81b697988fec20f6222fbe7521` |
| model/comparison | `comparisons/0229202d-9615-4b5d-bb50-c3d2c93c0ca0.json` | `7ff9daefc3791c9560894ccf3766c7e64fd70295f759464e4ac84226b6c67b79` |
| verbs/source | `oracle/f55996d3-5f6a-4c6b-83c5-abda2cd16574.json` | `f0a25a4af451acc5cdfa7b4e4fad8a97f7bd7b34b65238f60c699d46c5f3dbba` |
| verbs/target | `target/9f2b64ce-55ea-4ec9-b424-7c9c45a56127.json` | `cc6cf064d495e5cb4b0f3e5a9bd9a04df014438088948815b4cbb478b897f696` |
| verbs/comparison | `comparisons/b13b19e8-9623-4784-ac12-ae29b47f2f3e.json` | `f141befa62d7db915a84e17be019d1a53b563a896e440d7027edb77ca7b349bb` |

Artifact paths in the table are relative to `parity-results/`. These are two
existing selected-output regression controls, not positive JSON-hook order,
retained adapter identity or full shared-definition evidence for the new slice.

## Frozen input review

Directory:
`/private/tmp/fastapi-rs-additional-response-field-proposal-2026-10-05/`.

| File | SHA256 |
| --- | --- |
| `additional_response_field_lifecycle.py` | `ef756492903a719a8b3522bc1971794663083bcbb55ed20076b74f988d0e8025` |
| `additional-response-field-lifecycle.yaml` | `199ab0b81d4b1e923933a13f076c49bb89229add1e0c90ce441902c0c5db7ae1` |
| `review-plan.md` | `d9c6ff61722a264924ad2abc16a47d4751021f25ce3053359c608d305143d102` |

Verified text and hashes: **3 ordinary parity cases, 15 HTTP GET actions,
3 construction observations; 9 state reads and 6 endpoint requests**. Each case
begins and ends with state, and each endpoint request has a following state
read. There are no arm requests, OpenAPI requests, target-only fault cases or
empty-prefix includes. The factory has the two ordinary positional arguments.
The YAML uses explicit mappings and whole-value observation/receive aliases;
there are no merge keys. Schema9 selections are exact status/ordered
headers/body, singular ordered ASGI message_types, exact application exception
and exact construction outcome/class/message. All evidence paths exist in the
pinned source. The author reports canonical read_recipe/schema/AST/counts and
repository-configured Ruff checks passed without importing the workload. I
independently inspected source/shape/hashes and did not rerun those tools.

| Exact case ID | HTTP/state/endpoint counts | Public source boundary |
| --- | --- | --- |
| `fastapi.additional-response-field-lifecycle.saved-decorator-attachment` | 3/2/1 | Separate saved-decorator creation/retention/attachment stages; an extra409 and primary field expose core construction at attachment, extra-before-primary order and absence of premature JSON hooks. The unused extra receives no runtime value, while the primary validates/serializes the ordinary endpoint value. A user core warning remains selected with its real phase. |
| `fastapi.additional-response-field-lifecycle.shared-router-two-contexts` | 5/3/2 | One actual original router is included under left/right nonempty prefixes. Original plus separately reached effective context construction and reuse are public callback observations. The right request still traverses the already visited left context. Returned409 JSONResponse contains data outside both declared int models and an ordinary header, independently exposing response bypass while additional and primary fields are still constructed. |
| `fastapi.additional-response-field-lifecycle.second-additional-hook-retry` | 7/4/3 | Extras are inserted409 then202, deliberately unsorted. Only after all setup/includes, a user hook is armed for one refusal at the second label. Matching builds the first extra, reaches the second warning/refusal before the primary, and a public handler returns actual class/message/path. Retry/repeat journals expose whole bundle reconstruction and successful reuse, without a cache or field identity lookup. |

The unsorted statuses are ordinary body-allowed integer inputs. Responses are
built from the declaration list in insertion order; no sorting or copied
oracle output is used. Named router storage is only a user object registry, not
a field/cache substitute. The custom ValueError is separate from the helper's
translated schema error and includes only the user label, avoiding repr or
address dependence. Handler class/message/path are returned unchanged. A
matching-time refusal precedes endpoint/dependency/resource entry. Actual
UserWarning emissions and later successful requests are selected, but the
separate narrow UnsupportedFieldAttributeWarning restoration control is not
repeated here. No yield cleanup occurs in these inputs.

## Exact public API mappings for admission

All cases use these existing public bindings/operations:

- `fastapi.FastAPI` and canonical
  `fastapi.applications.FastAPI.__init__`: actual app construction.
- `fastapi.applications.FastAPI.get`: state declaration and, in the direct case,
  explicit saved decorator creation/endpoint attachment.
- `fastapi.applications.FastAPI.__call__`: the wrapper delegates every HTTP
  request to the same actual app.
- `fastapi.applications.FastAPI.exception_handler`: registration in every
  factory; only the refusal case invokes the handler.
- `fastapi.Request`: actual endpoint/handler injection and public query/URL
  properties. These inherited Request mechanics remain sibling-owned.
- `fastapi.responses.JSONResponse`: actual public state/error responses, and
  an explicit returned response in the two-context case. Generic response/send
  mechanics remain sibling-owned; no new alias identity relation is asserted.

The two router cases additionally use `fastapi.APIRouter`, canonical
`fastapi.routing.APIRouter.__init__`, `fastapi.routing.APIRouter.get` and
`fastapi.applications.FastAPI.include_router`. Neither input calls
`APIRouter.include_router`, FastAPI.post, public api_route/add_api_route,
FastAPI.openapi or get_openapi. Do not map those operations or promote private
ModelField/IncludedRouter helpers merely because they supply source evidence.
The external Pydantic/core-schema hooks are pinned runtime requirement edges,
not new FastAPI import/export claims.

## Complete journals and remaining limits

State retains ordered setup/request/core/JSON/validation/serialization/endpoint
entries, relative request counts, complete handled error records, user refusal
state and actual warning category/message order. The wrapper records every
non-state send field without filling omitted keys; bytes use typed hex and
tuples remain distinct from lists. It forwards the original message. State
does not record its own body into itself, while canonical selectors still
observe all state HTTP responses. Following state reads include the preceding
request's finally/warning records and final send messages. No trace is reduced
to counts alone or normalized. No raw object repr, expected outputs, source
runtime/private lookup, case-ID dispatch, target detection, clock/thread ID,
sleep, GC, concurrency or reentry is present.

The proposal directly observes extra-before-primary, not extra-before-input/
dependency schema construction: endpoints inject Request only. Falsy/custom
model truthiness, body-forbidden statuses, inherited/overridden mapping keys,
string/range/enum/default statuses, missing descriptions, deep metadata merges,
namespace/annotation mutation and alias/title/name semantics remain unselected.
Positive OpenAPI JSON mode/order/shared definitions/cache failure are likewise
unselected; defining the JSON hook only makes premature calls observable.

The frozen native design at
`/private/tmp/fastapi-rs-additional-response-field-native-design-2026-10-05.md`
is SHA256
`830fdc322053a08131bd1b85a2e53eaab49c4de8de588a51bfd93c330b340efb`.
Read-only assessment found no selected-input disagreement in raw capture until
attachment, separate extra/primary owners, direct extra-before-plan-before-
primary preparation, independent prefix bundles, atomic retry or owned
OpenAPI snapshots. It remains an unapplied proposal. Its existing include-time
CallablePlan analysis is still earlier than source's matching-time extra-
before-dependency analysis; the no-dependency-hook cases do not discharge that
source-order gap. Source locks/version refresh and concurrent/reentrant/drop
history remain outside the immutable slice. The design's one-field JSON path
is explicitly different from source shared generation and needs separate
positive public gates before stronger claims.

## Admission recommendation

Admit exact frozen copies only after the parent binds reviewed APIs/requirements
and materializes/validates the index; then use the reviewed source-first helper.
Require all three source constructions and all15 actions to complete before
the unchanged-target diagnostic. Preserve mismatch/error artifacts and all
selectors, with no implementation change or comparison adjustment in that
stage. No static inference is a passed new-case receipt or coverage result.
Public schema refusal needs no new fault hook. Existing generic RuntimeError/
500/later200 fault evidence cannot establish field retention. BackgroundTasks
worker crossing, mutable router/version refresh and generic Starlette behavior
remain separate and no sibling change is proposed.
