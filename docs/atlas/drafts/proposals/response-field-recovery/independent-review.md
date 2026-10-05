# Response-field recovery3 independent static review

2026-10-05. Reviewed the frozen inactive proposal under
`/private/tmp/fastapi-rs-response-field-recovery-proposal-2026-10-05/`.
No remaining source/input/selector blocker found within the selected boundary.
This is static review, not live source reachability or target support evidence.
No factory import, app/worker/parity execution, build, installation, active
input or metadata change, tracked edit, sibling edit or measurement occurred.
Only this independent review note was written.

## Frozen inputs and admission correction

| File | SHA256 |
| --- | --- |
| `response_field_recovery.py` | `e898b990066b4a1a65ad1833e992ebc30d6177bca9187c29f18ee0aa3bda514a` |
| `response-field-recovery.yaml` | `aaec3e2ac3455454158a1e961f9d4606b3a42af85efea6dd51c9908f7afcb375` |
| `review-plan.md` | `f8915d3dfee884178e693c060f345ed2c89a60291a6fcc8df280667c3b30b710` |
| `fault-companion-feasibility.md` | `05e0f3b4775dc0f558e749412635f4883858c4e78548a3706b3d412273e55725` |

There are **3 parity cases, 30 HTTP actions, 15 state reads, 3 arm POSTs,
12 other requests and 3 construction observations**. Their action counts are
10/12/8. The factory accepts the canonical positional `(factory_input,
event_trace)` contract (`worker.py:1253`). IDs and action order remain intact.

Independent review found that the original YAML merge mappings were rejected
by the repository's duplicate-key loader (`contract.py:203-223`), which does
not flatten merge nodes. The author expanded only those mappings and refroze
the recipe/plan. No merge mappings remain; whole-value scope, receive and
observation aliases are supported and retain the same declarative sequences.
The author reports canonical `read_recipe`, schema and Ruff admission passed,
and parsed inputs equal the earlier SafeLoader payload. I inspected the
corrected text and independently verified the hashes; I did not rerun loaders.
All declared upstream evidence paths exist in the pinned FastAPI checkout.

## Source and public reachability

Verified source HEADs are FastAPI0.141.1
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` and Starlette1.6.0
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. Pydantic2.13.4/core2.46.4 and
Python3.12.13 are the declared fixed profile; no moving source substitutes.

The workload uses public FastAPI/APIRouter construction, get/post decorators,
include_router, exception_handler, Request query/URL properties, JSONResponse,
Annotated metadata and the public Pydantic core-schema/warning protocols.
No private Default, route/context/cache/ModelField imports or original-FastAPI
helpers exist. Declarations supply ordinary labels, paths, values and include
prefixes; there is no case-ID dispatch, result lookup or prescribed output.

All schema hooks begin unarmed. State and arm routes are registered first with
`response_model=None`. Nonempty prefixes avoid source's empty-prefix validation
traversal (`routing.py:3277-3295`). Original route attachment constructs its
field (`routing.py:1103-1114`); arming changes only a user journal's label and
one-use rejection count after attachment. The callback raises a deterministic
named ValueError subclass; `utils.py:58-78` translates only
PydanticSchemaGenerationError. Starlette's exception middleware creates a
Request before matching and catches the registered error before response start
(`middleware/exceptions.py:46-68`, `_exception_handler.py:31-65`). The async
handler can therefore observe the request path and send its unchanged error
class/message in a public 409 JSONResponse.

| Case ID suffix | Source-ordered boundary reached |
| --- | --- |
| `parent-retained-after-child-error` | A/C own fields and a child descriptor are built and published by the parent before B's child matching/build. B then rejects. An A full match skips failed B; retrying B reconstructs only the child; C later reuses the successful contexts. Public schema stages/counts expose incorrect parent rollback or eager child construction. |
| `shared-router-prefix-error-isolation` | One actual named APIRouter is included under two prefixes, creating distinct source branches. Left warms; right's second own field rejects after its first succeeds but before right publication. An earlier left full match can succeed while right remains failed; right retry rebuilds its own vector. Shared labels plus request stages expose prefix/context isolation without private identity access. |
| `warning-filters-restored-before-handler` | The failed field's warning context exits before the public handler emits UnsupportedFieldAttributeWarning and UserWarning. The outer per-request observer captures category/message and an independent emission trace, distinguishing leaked suppression from omitted handler code. Retry/repeat then expose retained successful response validation and serialization. |

Source branch publication/child ordering is explicit at
`routing.py:1599-1625`; matching and reuse are at `1730-1803`; earlier FULL
selection is at `2719-2743`. Included field reconstruction follows
`_EffectiveRouteContext.from_api_route:1430-1478`. The exact scoped warning
filter is `_compat/v2.py:141-166`. No declaration, annotation, router version,
provider or signature mutation is used by these inputs.

## Observation strength and limits

Every HTTP action selects exact status, ordered headers, body and actual
application exception; ASGI message types use singular `selector` and
`comparison: ordered`, as schema9 requires. Construction selects actual
outcome/full class/message. Each final request is followed by a state read.

The state body retains ordered public callback entries, counts, unchanged
handled class/message/path and warning category/message. Full prior non-state
send messages preserve every original field, bytes as typed hex, tuple/list
shape and header order, without adding omitted keys. Messages are forwarded
unchanged. State excludes recording its own response to prevent recursive
snapshots; the canonical runner still selects each state response. Thus raw
send fields and completed request-finally/warning journals remain observable.
No addresses, absolute thread IDs, timing, warning filename/frame selection,
normalization or target detection appear.

All endpoints/handlers are async, requests are sequential, and no resources,
dependencies, background tasks, yield cleanup, reentry, concurrency, locks or
GC observations are introduced. These cases expose retention through public
callbacks, not private adapter identity. Dynamic router/version refresh,
additional fields, empty prefixes, OpenAPI traversal, streaming and concurrent
or reentrant construction remain outside the selected boundary. The immutable
Starlette-RS BackgroundTasks crossing blocker is not discharged by this review.

## Existing fault companion note

The separate note honestly proposes no new fault recipe or hook. Existing
`http.route.invoke.before` is consumed after included-field materialization
(`application_runtime.rs:10274`, `10915-10935`). A fresh unarmed app can reach
that point with a cold included GET, then recover with the same GET; an earlier
state/arm route would consume the fault first and must be omitted. Only the
fault action should select application_error: even null successful rows count.

Verified comparator scope (`fault_contracts.py:125-210`) is exactly one actual
builtins.RuntimeError observation, completed fault action, two ASGI message
types, status500 and a later completed integer status200. It does not assert
message/body, same path, callback order/counts, warning restoration, adapter
identity/cache readiness, field retention or absence of reconstruction. Full
journals would be diagnostic only under that named contract. Dependency cleanup
contracts require their existing single later events-only200 shape and cannot
be repurposed as adapter-state assertions (`fault_contracts.py:213-260`).
The three public callback errors belong to ordinary parity, not target-only
faults. No fault extension is needed for their source-reachable outcomes.
