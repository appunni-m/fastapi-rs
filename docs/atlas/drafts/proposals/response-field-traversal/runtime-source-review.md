# Response-field traversal7: current native/source review

2026-10-05. Detailed read-only review of the immutable included-branch path at
FastAPI-RS commit `ebcdf2d2c6c333bbfb04a19d122ad778eb3cbbd6`, against the independent
inactive traversal7 proposal. Only this temporary review note was written. No
tracked files or proposal files changed; no application imports/execution, parity,
build, install, unit tests or sibling mutations. Parent owns fault61/restoration.

## Verdict and exact reviewed inputs

No concrete mismatch or lifetime/borrow blocker found in the seven selected
sequential, immutable HTTP scenarios. The generic branch/index algorithm fits
their source ordering and fail/retry observations. This is static clearance for
admission and live diagnosis, not a passing source/target result or a claim of
general included-context compatibility.

| Reviewed file | SHA256 |
| --- | --- |
| fastapi-rs/src/application_runtime.rs | 9608a3aacce77d8583617eed6a840dd48910fee3a0f256cb1463cd16b2dfeaad |
| fastapi-rs/src/response_field.rs | aa943aa0caa352ba579b58f9a1b3c0ee4f660c3f9400366d023b954e97aba825 |
| proposal/response_field_traversal.py | 35aa2d46026953a69ac6284f6a0215c62df22e19ddac0018c9d31336224de4d9 |
| proposal/response-field-traversal.yaml | 3dfd1caa6573faa55edaef83e1eb166e4279a97542bda323a4ea8ab2de929c66 |
| proposal/review-plan.md | 8d5164a0825cf7755f3049c905578dd264a2ad29609cc73a882785b9bffd8ad2 |

Proposal directory:
`/private/tmp/fastapi-rs-response-field-traversal-proposal-2026-10-05/`.
The unchanged counts are seven parity cases, 42 HTTP actions (24 state reads,
18 other requests), and seven construction observations. The earlier independent
input/schema review remains at
`/private/tmp/fastapi-rs-response-field-traversal-independent-review-2026-10-05.md`.

Pinned source heads were read: FastAPI0.141.1
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; Starlette1.6.0 sole oracle
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`. The immutable b4c8a65 sibling routing
and exception-middleware source was read through Git objects, without changing
a checkout. Generic behavior and the separate BackgroundTasks crossing blocker
remain sibling-owned.

## Whole-branch failure, retry and ownership

Source `routing.py:1601-1624` reads the recursive version, takes the branch's
`threading.Lock`, checks the version again, builds a local candidate list and
publishes the list/version only after all own direct contexts succeed. A child
include contributes a new child descriptor at this stage; it does not recursively
build child fields. A later own field failure discards the preceding local fields.

Native `materialize_included_response_fields` at1447-1538 snapshots branch visits
and owned field inputs under short app borrows. It builds every own field into
`prepared` at1489-1500 after releasing those borrows. Commit checks both indexes
and the descendant descriptor before replacing any state, replaces the entire
prepared branch, then marks it ready at1530. A build error exits before commit,
so all previously prepared fields and remaining input references are discarded
outside an app borrow. Success moves retired fields into a vector and drops that
vector after releasing the mutable borrow. There is no Python callback in the
replacement/readiness sequence. Borrow guards also leave scope before the outer
prepared vector is destroyed on a failed commit precheck.

Thus the selected two-own-route refusal leaves both destinations Deferred and
the branch unready. The early `/state` match does not retry it. The repeat request
prepares both again, so the first hook's repetition is observable; later requests
reuse the committed fields. Separate earlier branches that already committed are
retained when a later branch fails. Atomicity is per branch, not per whole app.

`ResponseFieldState` at953-969 distinguishes Deferred from Ready(None). The helper
retains the field, its metadata and adapter; `.field(py)` only clones references.
Response validation/serialization takes its owned snapshot after materialization.
The custom user ValueError remains outside the helper's narrow
PydanticSchemaGenerationError translation, as in `utils.py:58-78`. Warning context
restoration is performed on both success and error. These seven hooks have no
finalizers, warning-filter mutations or reentrant callbacks, so no extra drop or
warning-history protocol is being claimed from them.

## Nested A/B/C and matching order

`IncludedFieldBranch::from_router` at1353 excludes immediate child index ranges
from its own direct indexes. `for_new_context` at1376 adds the new ancestor offset
once to each already source-relative index, including descendants. The tree case
has app index0 for state, own A at1, child B at2, own C at3. The parent has own
indexes[1,3] and child[2]. `collect_visits` at1398 is preorder: an unready parent
first, then children in declaration order. A full match prunes a branch only when
its start is later than the selected flat index; it does not prune the rest of a
visited branch's own fields.

On cold A, the parent prepares A/C and the child start2 is later than full index1,
so B remains deferred. On subsequent C, the ready parent needs no rebuild, but
child start2 is before full index3; B builds before C dispatch. Requesting B last
reuses it. Source1609-1617 and1730-1759 produce the same ordering: own A/C
construction, then child visitation when matching reaches that descriptor.

For fixed ordinary API routes, the flat first-full selection used by
`FastApiOperationRouter::matches` (`operation.rs:246-282`) corresponds to the
hierarchical first-full scan. The sibling table retains the first path-only
partial while searching for a later full match (b4c8a65
`route_table.rs:555-583`). All selected paths are static and use ordinary GET/POST;
there are no custom route.matches/converter callbacks whose effects would be
reordered by selecting the flat index before constructing fields.

| Selected case boundary | Current native flow versus pinned source |
| --- | --- |
| Early state/direct full match | Full index before the include start prunes it, matching source2729-2735's immediate full return. |
| Earlier direct POST partial, later included GET full | The table returns the later full index; visited included fields build before dispatch. Source2729-2743 retains the partial and continues. |
| Initial miss/404 | `begin` passes None to materialization at10274, visiting all branches before ordinary default/404 handling. Source completes the normal route loop first. |
| Slash redirect | Initial miss materializes both includes before `redirect_http_slash` at10098. Its search reuses fields already ready; source2744-2761 likewise begins redirect search after its initial scan. |
| Returned JSONResponse | Included construction runs before invocation; `finish_endpoint` at11167 bypasses field lookup/validation for a returned Response, matching source711-714. Its original response ASGI path is retained. |

A terminal 405 also passes None in this native path, but selected7 contains no
terminal-405 action. Its partial case proves reaching a later full route only.
Mounted/frontend/raw routes, docs shadowing, custom converters and URL/OpenAPI
traversal do not acquire coverage from this static table correspondence.

## Matching-time error-handler reachability

The schema refusal happens in `begin`, before the selected endpoint Request or
dependency invocation exists. It leaves no entered yield stack to close. Native
`FastApiCall::resume` propagates that error, and `middleware_stack_for` at3803-3883
places Starlette ExceptionMiddleware outside the core ASGI call with the actual
registered custom class handler.

The pinned sibling middleware creates/retains its Request before awaiting the
core (`application_runtime.rs:715-786` in b4c8a65), then selects the actual error
class's MRO handler before response start at788-844. It therefore does not require
FastApiCall.request to be populated. The sole-oracle Python source follows the
same public handler boundary (`middleware/exceptions.py:46-68`,
`_exception_handler.py:31-65`). The selected handler's request.url.path, full
actual class/message, status/body, and subsequent recovery trace are reachable.
Exact raw message fields are exposed by the ordinary observer's next state body;
no output normalization or fault substitution is needed.

## Concrete unsupported callback/locking boundaries

These are code differences, not failures in the selected seven inputs:

- Source holds a non-reentrant branch lock through own-context construction and
  rechecks its version after acquiring it. Native uses plain readiness plus an
  initially snapshotted visit list, with no in-progress state/lock/recheck. A
  schema hook that releases the GIL and allows another thread to visit the same
  cold branch can permit duplicate native builds. The current inputs have no
  thread handshakes, suspension or concurrent requests; they cannot establish
  source lock semantics.
- Same-branch synchronous reentry during a source build can block on that
  non-reentrant lock. Native's released app borrow avoids a borrow panic but
  permits another unready preparation/recursive build instead. Short borrows
  alone do not establish equivalent reentry. Do not add an invented reentry
  error, silently claim safety, or use this path in bounded traversal7.
- Callbacks that cause another request to finish materializing a branch can leave
  the outer native visit list stale; commit does not recheck readiness. Selected
  hooks only journal/counter/raise and never reenter, so this is not exercised.
- Native field readiness does not replace source's complete effective-context
  version cache. Dynamic declaration/model/default mutation and version refresh
  remain a separate goal. Existing `merge_router_routes` still rebuilds callable
  plans under source/destination borrows during include setup; selected endpoints
  only require ordinary Request injection and introduce no user dependency or
  signature callbacks there. This earlier gap is not solved by field preparation.
- Native destroys prepared fields outside app borrows without a source branch
  lock. The source error traceback can retain construction-frame locals, so this
  review does not establish equivalent destruction timing. Exact finalizer/reentry
  observations need separate public inputs, absent here.

The algorithm contains no label, fixture ID, rejection counter or scenario
dispatch. Its decisions use route insertion indexes, branch structure and ordinary
field construction results. No case-specific repair is indicated by this review.

## Recommended next bounded goal

Admit the unchanged traversal7 inputs with reviewed public mappings, then preserve
identity-checked live source and unchanged-ebcdf2d target diagnostics. Gate exact
construction outcome, actual error/handler bytes, ordered hook history, retry,
matching selection and full recorded ASGI sends across all seven cases. Repair
only an evidenced first divergence if one appears; there is no static reason to
change this native field path before those runs.

Keep the existing191 normal regression and separated fault/cleanup evidence under
their own receipts. The normal user schema refusal is reachable on both sides and
requires no new target-only fault hook. A later distinct backlog may add terminal
405 and child-branch failure after a successful parent commit, before any broader
lock/reentry or dynamic-refresh goal. Streaming, worker scheduling and the sibling
BackgroundTasks blocker remain separate. No benchmark or support claim follows
from this note.
