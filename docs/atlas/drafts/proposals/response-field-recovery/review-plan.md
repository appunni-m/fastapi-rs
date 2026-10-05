# Response-field recovery and warning restoration controls

Inactive independent input-only proposal, 2026-10-05. This directory is outside
the active inputs and contains **3 ordinary parity cases, 30 HTTP actions and
3 construction observations**. There are 15 `/state` reads, 3 public POST hook
arming actions and 12 other requests. No target-only fault recipe is included.
No app factory was imported or executed. No tracked file, runtime, sibling,
manifest, active input, generated file or measurement was changed by this
proposal.

## Files

- `response_field_recovery.py`: a generalized public declarative workload.
  Route declarations supply paths, methods, labels, values and nonempty include
  prefixes. A named-router registry lets two public include declarations use
  the same actual APIRouter object. User warning declarations select a public
  warning category and message. No application logic reads a fixture identity.
- `response-field-recovery.yaml`: schema @9 prospective normal parity recipe;
  its repository-relative workload path is a future admission path, not an
  existing active workload.
- `fault-companion-feasibility.md`: a separate static assessment of the
  existing target-only fault point and named contract. It contains no new
  comparator, hook, contract or asserted adapter-cache state.

## Pinned source evidence

FastAPI 0.141.1 is commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` at
`/Users/lazytrot/work/fastapi`. Starlette 1.6.0, the sole oracle, is commit
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f` at
`/Users/lazytrot/work/starlette`. The runtime profile pins CPython 3.12.13,
Pydantic 2.13.4/core 2.46.4 and AnyIO 4.12.1. No moving sibling or later source
version is evidence for these inputs.

Recipe upstream test/documentation references identify public API contexts;
the precise requirements below come from reading the pinned source. No
upstream app, tests or prescribed outputs were copied or run.

| Source | Requirement motivating these ordinary inputs |
| --- | --- |
| FastAPI `routing.py:1103-1114`; `utils.py:58-78` | Primary response fields are constructed for the original route at public endpoint attachment. A user ValueError subclass raised by a core-schema callback propagates; only PydanticSchemaGenerationError is translated by create_model_field. |
| FastAPI `routing.py:1430-1478` | Each effective included route context is populated from its original route and include context, constructing a fresh response field. |
| FastAPI `routing.py:1599-1625` | A branch builds a local vector of its own contexts and publishes it only after that complete construction loop succeeds. Nested includes become child branches without constructing their fields in that loop. Failure in a reached child occurs after the successful parent vector has already been published. |
| FastAPI `routing.py:1730-1763,1776-1803` | Matching materializes a branch before iterating candidates. A nested child is reached in candidate order. A later retry reuses an already successful parent branch while the failed child tries its own construction again. Handling reuses the selected contexts. |
| FastAPI `routing.py:2719-2743` | An earlier full match ends the scan. An early `/state` or `/arm` route skips later include branches; a first prefix full match can also skip a later failed prefix. |
| FastAPI `routing.py:3258-3312` | Each public include appends a distinct included branch around the original router. Nonempty prefixes avoid the separate empty-prefix validation traversal. Including one original router under two nonempty prefixes therefore supplies two independent effective contexts. |
| FastAPI `_compat/v2.py:141-166` | ModelField construction uses a warnings context that ignores only UnsupportedFieldAttributeWarning, then constructs its TypeAdapter inside that context. The context exits when a user schema callback raises, before an outer public handler runs. |
| Starlette `middleware/exceptions.py:46-68`; `_exception_handler.py:31-65` | A public async exception handler can catch the user construction error during router matching before response start and send its own ordinary Response. |

Generic ASGI response execution and exception middleware remain sibling-owned.
These controls exercise FastAPI response-field construction and lifetime through
public callbacks; they authorize no generic Starlette behavior changes.

## Three independent controls

| Case suffix | Actions | Input and selected boundary |
| --- | ---: | --- |
| `parent-retained-after-child-error` | 10 | Declare parent own A, nested child B and own C. Arm B through public POST `/arm`, then request B cold, observe the handled error and journal, request A, retry B and request C, with state reads after each. A/C schema callbacks expose parent construction before B traversal and whether they repeat after the child error; later endpoint, validator and serializer callbacks expose successful retained parent use and child retry. |
| `shared-router-prefix-error-isolation` | 12 | Declare one actual named router with two own fields and include it under `/left` then `/right`. Warm `/left/one`, arm the second hook through `/arm`, then request `/right/one`, revisit `/left/two`, retry `/right/one` and request `/right/two`, with state reads. A right request still scans the earlier left branch. The selected stages/counts expose successful left reuse, right failure after its first local field, left early full selection while right remains failed, and independent right retry/reuse. |
| `warning-filters-restored-before-handler` | 8 | Arm a single included field, request it, and let its public handler call warnings.warn for UnsupportedFieldAttributeWarning and UserWarning. An outer per-request warning observer remains active across construction, handler and sends. Read captured warning categories/messages plus emission trace, retry the same route and repeat it, with state reads. A suppression filter left active after construction failure is observable in this same handler invocation. |

The arming route changes only ordinary user hook state: selected label and one
remaining rejection. It does not inspect or mutate route declarations, models,
annotations, endpoint metadata, include contexts, FastAPI cache/version state
or implementation identities. Both state/arming routes are registered before
the declared includes with `response_model=None`; no traced model is attached
to those observer routes. Public arming occurs after all declarations complete
and, in the shared-router case, after the earlier successful request.

The one-use schema rejection is a normal input error, not a native fault. Its
actual exception module/qualname, untouched message and public request path are
recorded by the handler and returned in its JSONResponse. It is intentionally a
ValueError subclass distinct from PydanticSchemaGenerationError. The same
factory constructs a fresh app and journal for each recipe case.

## Exact observations and independence

All construction observations select actual outcome, exception class and
message. Every HTTP action selects exact status, ordered headers, body and
actual application exception, plus ordered ASGI message types. `/state` bodies
contain actual prior callback journals, counts, handled errors and warning
records. Warning records select ordered category module/qualname and untouched
message; warning filename, line, frame and source-object fields are outside the
selected boundary. Before emitting each warning, the handler records its actual
category/message so suppression is distinguishable from omitted user code.

The ordinary ASGI observer records every field of prior non-state send messages
without filling omitted keys. Typed hex preserves bytes; typed tuples preserve
tuple/list shape, headers and order. Original messages are forwarded unchanged.
State sends are omitted from its own journal to prevent recursive snapshots;
the canonical runner still selects every state response status/headers/body and
message sequence. All final journals are reached by a selected state action.

Workload imports are standard Python, public FastAPI/APIRouter/Request/
JSONResponse, public Pydantic warning classes and its core-schema protocol. No
Default, ModelField, APIRoute, route context/version/cache, private FastAPI
runtime imports, source-result lookup, target detection, expected outputs,
normalization or per-case control flow exists. The named-router registry is a
user-held public object registry required to provide the same original router
to both include calls; it does not cache FastAPI construction results.

All endpoints, the handler and observer are async. No clocks, worker threads,
concurrency, reentry, locks, sleeps, GC observations, dependencies, background
tasks or yield resources are introduced. This proposal does not prove route
mutation, concurrent/reentrant construction, empty-prefix inclusion, additional
response fields, dynamic annotations/namespaces, OpenAPI traversal, streaming,
or actual private adapter identity. Adapter retention/reconstruction is exposed
only through ordinary public schema-callback invocation and later response
validation/serialization observations, to be compared live after admission.

## Static admission boundary

Python AST syntax, schema @9 validation, identifier uniqueness, selected
observation structure, pinned evidence-path existence and the 3/30/15/3/12/3
counts passed static checks. The factory has the required two positional
parameters. Repository-configured Ruff lint and format checks passed; Ruff
formatted only this temporary workload, which was already in the required
format. No factory import occurred during these checks.
Independent review found that YAML merge mappings passed SafeLoader/schema
checks but were unsupported by the repository's duplicate-key loader. The
recipe now expands those mappings into ordinary scope/action mappings while
retaining whole-value aliases; canonical `read_recipe` passed with identical
declarative input semantics and unchanged counts. No loader or comparator was
changed.
No factory import, active input loader, app, source/target worker, parity run,
Rust build/install or benchmark is allowed by this proposal task. These static
checks establish draft shape and cannot establish source reachability or target
support. Source/target frozen identities, exact receipts and canonical admission
remain required if the parent approves future activation.
