# Additional response-field lifecycle: inactive input proposal

2026-10-05. Independent ordinary public inputs only. This directory is outside
active inputs and proposes no implementation, manifest change, injected fault,
comparison rule, expected output or normalization. No application factory or
oracle/target was imported or executed while authoring it.

## Files and boundary

- `additional_response_field_lifecycle.py`: generalized public declarations and
  hook/warning/error/raw-send journals; positional `create_app(factory_input,
  event_trace)` entry point.
- `additional-response-field-lifecycle.yaml`: canonical
  `fastapi-rs/python-asgi-workflow@9`, instantiate once per case. Its workload path
  names the prospective admitted location, not a current active file.
- This plan: source evidence, proposed public mappings, static checks and later
  evidence gates. The independent reviewer owns a separate review note.

The proposal has **3 parity cases, 15 HTTP GET actions and 3 construction
observations**. Case action counts are 3, 5 and 7. Nine actions read public state;
six request declared endpoints. Every case begins and ends with a state read.
There are no OpenAPI requests, fault workflows, arm HTTP endpoints or POSTs.

## Independent declarations and observations

All endpoint paths, prefixes, labels, values, additional response statuses,
descriptions and model metadata come from ordinary factory data. One named user
router object can be included more than once. The workload dispatches declarations
by `kind`, never by case/action ID, runtime version or target identity.

Each model is a public `Annotated[int, SchemaMetadata(...)]` value. The user
metadata implements Pydantic's core and JSON schema hooks. Actual hook calls are
recorded, with label, occurrence, setup/request phase and source annotation; JSON
hook calls additionally retain the public handler's mode and actual core type.
Core hooks return a schema built through the public handler and `pydantic_core`
builders. Validation and serialization callbacks record actual values and
serialization mode without changing them. They do not invoke FastAPI internals
or construct a second adapter themselves.

Saved decorators have distinct creation, retention and endpoint attachment
journal stages. App/router creation, state/handler registration and public include
calls also have explicit stages. A selected user core hook can refuse one call,
but it is armed only after every declaration and include call has finished.
There is no registration-time user refusal or fixture-side repair of a framework
error. The ordinary `ValueError` subclass reaches a public FastAPI exception
handler; that handler reports its actual module/qualname, untouched message and
request path through a `JSONResponse`. Its status and content are user handler
inputs, not an expected framework result.

Each setup operation and observed endpoint request records actual warning
category module/qualname and untouched message in emission order. Selected user
core hooks emit ordinary `UserWarning` stimuli. A warning emitted before the
refusal remains observable. The workload does not replace or globally clear the
framework's warning filters; its scoped `catch_warnings(record=True)` observer
and `simplefilter("always")` are ordinary user instrumentation.

Every HTTP action selects exact status, ordered headers and body, ordered ASGI
message types and the application exception. Construction selects exact
outcome/class/message. Public `/state` responses expose the complete ordered
hook/endpoint/error/request journal, warning list, counters and remaining user
refusal. Observed endpoint requests also retain every actual ASGI send key and
value: bytes are reversibly encoded as hex and tuple/list identity is retained.
Messages are forwarded unchanged; no defaults are filled, fields omitted,
headers sorted or error messages altered. State sends are excluded from their
own journal to avoid recursive self-observation; the canonical runner still
selects each state action's complete HTTP body/headers/status and message types.

## Three proposed cases

| Public control | HTTP actions | Stimulus and selected observations |
| --- | ---: | --- |
| Saved decorator attachment | 3 | One direct route, one extra 409 model and one primary int model. Initial state exposes decorator creation versus attachment hook phases; probe and final state expose primary processing and any callbacks on the unused extra model. |
| Same router in two contexts | 5 | Include one original router at `/left` and `/right`. State, left, state, right, state expose attachment plus each reached effective context's construction and retention. A returned 409 `JSONResponse` contains data outside both declared int models and uses an explicit user header. |
| Second additional hook refusal and retry | 7 | One included route has extras inserted as 409 then 202, plus a primary model. Arm the second label only after setup. State, request, state, retry, state, repeat, state retain the actual error path, warning journal, full bundle rebuild after refusal and later retention. |

The deliberately unsorted additional statuses observe insertion order. The
second case's right request can traverse the already visited left context; the
plan does not assume that routing skips it. Returning a public Response observes
runtime bypass independently from field construction. No expected call count,
event sequence, schema, error, byte string or response is stored in the recipe.

## Pinned source evidence

The review uses FastAPI 0.141.1 at
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` in
`/Users/lazytrot/work/fastapi`, Starlette 1.6.0 at
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f` in
`/Users/lazytrot/work/starlette`, and the repository's Python 3.12.13,
Pydantic 2.13.4 / pydantic-core 2.46.4 pins. Generic Starlette behavior is owned by
the pinned sibling; this proposal does not alter its source or identity.

- FastAPI `routing.py:2973-3038`: `APIRouter.api_route` returns its decorator;
  `add_api_route` is called when the endpoint is attached. The route is published
  only after construction (`2969-2971`). `FastAPI.get` delegates to this public
  declaration path. A saved-decorator stage therefore exposes field work at
  attachment independently from eager decorator creation.
- `routing.py:1038-1054`: additional response mappings are traversed in insertion
  order. Each truthy model is checked for a body-allowed status and receives a
  named field in serialization mode. Route/path/unique ID setup occurs earlier;
  these fields are not asserted to precede every possible user callback.
- `routing.py:1056-1074,1103-1114`: additional fields precede dependency/body
  analysis and primary field construction. The selected hooks directly observe
  extra-before-primary order. They do not add an input/dependency schema hook;
  extra-before-dependency ordering remains source/design evidence here.
- `routing.py:1430-1478`: every reached effective API context reruns population
  using its merged response declarations. `1599-1625` publishes an included
  branch's own effective contexts only after all construction succeeds. A
  refusal in its second extra prevents publication of that newly built context
  for reuse; the public retry journal observes repeated construction without
  inspecting a private cache or adapter.
- `fastapi/utils.py:58-78`: the field helper's special translation catches only
  `PydanticSchemaGenerationError`. This proposal's independent user `ValueError`
  subclass is preserved. `_compat/v2.py:141-166` builds the retained adapter under
  a scoped filter for `UnsupportedFieldAttributeWarning`; ordinary `UserWarning`
  stimuli remain distinguishable and are not a blanket warning-suppression test.
- `routing.py:711-748`: ordinary response processing uses the primary field;
  returning a Response bypasses it. Extra status models describe responses and
  are not alternate runtime validators selected by the returned status.
- `openapi/utils.py:551-575,476-515` and `_compat/v2.py:289-338`: OpenAPI later
  collects retained fields and generates definitions/schemas, then merges the
  additional response. Merely defining JSON hooks without requesting OpenAPI
  gates premature JSON-hook invocation. It does not positively observe the
  source's OpenAPI serialization-mode mapping or generated definitions.
- Starlette `middleware/exceptions.py:46-68` and `_exception_handler.py:31-65`
  provide public exception dispatch before a response has started. The matching
  construction refusal occurs before endpoint work; no yield/resource cleanup or
  internal fault injection is required.

Recipe evidence points to pinned additional-response, response-class,
include-context and invalid-response upstream tests and public documentation.
Those references justify the public surface; no test expected values or source
runtime code were copied into the workload.

## Proposed admission mapping

| Case | Public interfaces actually exercised |
| --- | --- |
| Saved decorator attachment | FastAPI construction, `FastAPI.get` creation and attachment, HTTP `FastAPI.__call__`, injected `Request`, Pydantic metadata protocols, JSONResponse public state |
| Same router in two contexts | Above plus `APIRouter` construction, `APIRouter.get`, `FastAPI.include_router` twice, direct endpoint JSONResponse construction/call |
| Second additional refusal/retry | Router/include/GET/ASGI paths above plus public `FastAPI.exception_handler` and a handled user exception's JSONResponse |

All cases register the public handler and state route. Only the third case
invokes the handler through a refusal. Generic Request/Response/exception/send
mechanics remain sibling-owned; FastAPI-owned evidence concerns declaration,
field construction, included-context lifetime and primary response processing.
Admission must map existing reviewed identities/requirements; this inactive
draft does not create new operation overlays or metadata entries.

## Static and later gates

Permitted authoring checks are AST parsing, canonical `read_recipe` plus schema
validation, case/action/evidence/count audits, and explicit repository-config
Ruff formatting/lint. The recipe uses ordinary mappings and whole-value aliases;
it has no YAML merge keys. None of these checks imports the workload or proves
source reachability, a target outcome, parity or coverage.

Completed authoring checks: the canonical loader/schema accepted all three
cases; exact IDs, 3/5/7 action counts, three construction observations, nine state
and six endpoint actions, final state reads, exact selectors, integer status
entries, explicit descriptions, nonempty prefixes and pinned evidence paths
passed a static audit. The workload's AST parsed and confirmed its two positional
factory arguments, public imports and absence of case/action-ID dispatch,
target-specific imports, dynamic Python code or private response-field access.
Repository-config Ruff lint and format check both passed. These checks loaded
only the recipe/schema and parsed source text; they imported no workload/factory.

Before implementation: independent source/input review; parent-controlled active
admission and generated manifest/index checks; pinned, identity-checked isolated
source execution of all three cases; then unchanged-target diagnostic on the
same frozen inputs/source/binaries. The public state and exact selectors must
remain intact through admission. Native design and implementation are separate
work. Fresh live parity and the existing whole-suite/coverage gates are required
for a later compatibility claim; no benchmark claim follows from this proposal.

## Explicit limits

This is a bounded integer status, explicit description/model, nonempty-prefix
slice. It does not establish literal None/falsy/custom model truthiness,
body-forbidden statuses, default/string/range/enum statuses, malformed mappings,
deep content/header merges, include-level response declarations, callbacks,
alias/name/namespace behavior, mutable route mappings or model history.

No OpenAPI endpoint/schema/shared definitions, private response-field names or
adapter identity are selected. Public callback counts observe construction and
reuse, not private storage identity. No concurrency, reentry, locks, clocks,
worker execution, dependencies, generators, background work or fault hooks are
introduced. Warning filenames/frames/source objects are outside the selectors;
the narrow UnsupportedFieldAttributeWarning restoration control remains in its
separate proposal. No source or target outcome has been executed or recorded.
