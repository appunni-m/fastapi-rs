# Response-field traversal and branch-recovery backlog

Inactive independent input-only draft, 2026-10-05. This directory is outside
active inputs. No application was imported or executed, and no Rust, sibling,
active fixture, manifest, metadata, generated file or measurement was changed.
No support or successful-outcome claim follows from these source readings.

## Files and proposed size

- `response_field_traversal.py`: ordinary public app factory and lossless user
  ASGI observer; declarations describe routes, methods, prefixes, labels, values
  and whether an endpoint returns a Response. The factory reads no case ID.
- `response-field-traversal.yaml`: schema @9 prospective recipe referencing the
  future `tests/fixtures/workloads/response_field_traversal.py` path. It remains
  intentionally unavailable to the active input index.
- `review-plan.md`: source requirements, input independence and review limits.

Proposed scope: **7 normal parity cases, 42 HTTP actions and 7 construction
observations**. Actions comprise 24 `/state` reads and 18 ordinary requests.
There are no target-only fault cases, expected outputs or normalization rules.

## Pinned source evidence

- FastAPI 0.141.1, commit
  `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, at
  `/Users/lazytrot/work/fastapi`.
- Starlette 1.6.0, sole source oracle, commit
  `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, at
  `/Users/lazytrot/work/starlette`.
- CPython 3.12.13, Pydantic 2.13.4/core 2.46.4. Actual target/sibling build and
  source identities must be checked if this backlog is later admitted.

The recipe's upstream test/documentation references identify public API
contexts. Detailed behavior below comes from reading pinned implementation
code; no upstream tests or expected outputs were copied or executed.

| Pinned FastAPI source | Requirement motivating the public input |
| --- | --- |
| `routing.py:1103-1114`; `utils.py:58-78`; `_compat/v2.py:141-166` | An original response field is built during route declaration, even if its endpoint will return a Response. A user schema-hook error other than PydanticSchemaGenerationError propagates without that error translation. |
| `routing.py:1599-1625` | A visited included branch constructs a local vector of all its own effective contexts. The successful vector/version is published only after the entire construction loop completes. If a later own field raises, earlier successful local fields do not establish a partial published cache; a retry reconstructs the branch. |
| `routing.py:1609-1617,1730-1763` | A parent branch first builds its own A and C contexts, with a nested B include represented as a child branch. The child is materialized when matching reaches it. Own-field construction order and child traversal order are distinct. |
| `routing.py:2719-2743` | An earlier full direct match returns immediately. An earlier partial match is retained while later candidates may provide a full match. A `/state` route registered first therefore does not advance later includes. |
| `routing.py:2744-2787` | The initial normal scan precedes slash-redirect search and default/404 handling. Its visited includes may construct fields even when no endpoint runs. Redirect search can revisit already materialized branches. |
| `routing.py:1776-1803` | Handling an included match obtains the selected effective route context after matching; successful materialization is reused rather than rebuilt for each handle. |
| `routing.py:3258-3312` | A nonempty public include prefix avoids the empty-prefix validation traversal. Every draft include supplies a nonempty prefix, so setup does not introduce that separate traversal contract. |
| `routing.py:711-748` | Returning an ordinary Response bypasses runtime response-field validation/serialization while retaining the earlier field-construction boundary. |

Starlette source `middleware/exceptions.py:46-68` and
`_exception_handler.py:31-65` wraps router invocation with public exception
handlers. A user-defined ValueError subclass raised during matching can thus be
reported by its public async handler before response start. Starlette's generic
matching, redirect Response and response execution remain sibling-owned; this
backlog does not authorize generic behavior changes.

## Cases and observation boundaries

| Case suffix | HTTP actions | Independent stimulus and observed boundary |
| --- | ---: | --- |
| `branch-second-construction-error-retry` | 7 | A child has two own traced response models. After public declarations and include complete, user code arms the second schema hook to refuse one later construction. Request the first path, read handled exact error plus hook/send journal, repeat it, then request the second path. First-hook repetition observes rollback without reading cache state. |
| `parent-own-fields-before-child-traversal` | 7 | A parent declares own A, nested child B and own C in that order. Request A cold, C next and B last, with state reads between them. The journal separates eager parent own-context construction from later nested child visitation and retained field reuse. |
| `earlier-full-direct-match-skips-later-include` | 7 | A direct GET path precedes an included GET path at the same URL. Request the overlapping path, then an include-only path, then the overlapping path again; different user values and endpoint labels expose selection while hook stages expose skipped versus visited includes. |
| `earlier-partial-direct-match-reaches-later-full-include` | 5 | Direct POST precedes included GET at the same URL. GET reaches a later full include despite the earlier partial direct match; POST exercises the earlier full direct route with the same immutable declarations. |
| `unmatched-request-visits-both-includes` | 6 | A missing path scans two separate includes before ordinary 404 dispatch. Later calls reach each declared path with the same unchanged models; full status/headers/body and hook/send journals are retained. |
| `redirect-search-follows-initial-branch-traversal` | 5 | Request an included slash-terminated path without its slash, then read state, then request the declared path. A later unrelated include records the initial full scan before redirect search; the workflow does not automatically follow a redirect. |
| `returned-response-still-constructs-included-field` | 5 | An included endpoint declares a traced int model but returns JSONResponse containing a dict outside that model, with a user header and status. Original/effective schema hooks and repeated raw sends remain visible; absence or presence of validator/serializer callbacks is an observation, not a stored expectation. |

All construction selectors preserve actual outcome/class/message. Every HTTP
action selects exact status, ordered headers, body and application exception,
plus ordered ASGI message types. The ordinary observer exposes all prior
non-state send messages through `/state`, preserving bytes as typed hex and
tuple/list distinctions, header order, all keys and field presence. It forwards
the original messages unchanged. State sends are excluded only to prevent
recursive snapshots; the canonical runner still observes each state response.

The schema-hook refusal is an ordinary input-driven user exception, not a native
fault injection. It is armed only after setup, with a deterministic one-use user
counter, and leaves annotations, endpoint metadata, route declarations and
router structure unchanged. The public handler projects the actual exception
module/qualname and untouched message, records its path, and returns an ordinary
JSONResponse. The wrapper preserves any unhandled exception and records its
actual class/message before re-raising. Warning observations preserve ordered
category/message, without filename/frame selection.

## Independence and limits

The workload imports only public FastAPI routing/Request/JSONResponse APIs,
standard Python modules and the public Pydantic schema-hook protocol. It never
imports Default, DefaultPlaceholder, ModelField, APIRoute internals, route
contexts or cache objects; it does not inspect routes, versions or implementation
identities. Labels are ordinary user hook/endpoint labels supplied by route
declarations, not fixture identifiers. No result snapshots, source-result
lookups, private source shortcuts, target detection or per-case comparator exist.

All endpoints and the error handler are async. The draft introduces no workers,
dependencies, yield resources, background tasks, clocks, thread IDs, sleeps, GC
observations or concurrency. It does not prove reentrant/concurrent branch
construction, route-version mutation, dynamic models/Defaults, empty-prefix
inclusion, additional response fields, streaming, OpenAPI/URL traversal or
generic sibling matching. The one-use hook behavior expands beyond immutable16's
always-successful field constructors; admission must separately verify source
reachability and error recovery before changing any implementation.

Static draft checks passed without importing the factory: Python AST syntax,
schema @9 validation, unique case/action identifiers, source-evidence path
existence, and the stated 7/42/24/18/7 counts. Repository-configured Ruff lint and
format checks passed after formatting only the temporary workload. These are
draft checks; no active input loader, generation, source/target worker or app ran.

Before activation: independently review inputs and exact selectors; copy only
approved inputs and add reviewed metadata mappings; run canonical
generation/admission; then preserve identity-checked live source and
unchanged-target diagnostics. No benchmark or compatibility evidence can be
inferred from this inactive draft.
